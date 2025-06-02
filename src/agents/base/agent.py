"""
Base agent implementation for AIOSv3 platform.

Provides the foundational agent framework with lifecycle management,
state tracking, and integration with the AIOSv3 infrastructure.
"""

import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from .exceptions import (
    AgentError,
    AgentInitializationError,
    AgentStateError,
    TaskExecutionError,
    TaskValidationError,
)
from .types import (
    AgentHealth,
    AgentMetadata,
    AgentState,
    AgentStats,
    AgentType,
    Priority,
    TaskType,
)

logger = logging.getLogger(__name__)


class Task(BaseModel):
    """Represents a task to be executed by an agent."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: TaskType
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    priority: Priority = Priority.MEDIUM
    complexity: int = Field(default=5, ge=1, le=10)
    requires_privacy: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None
    context: dict[str, Any] = Field(default_factory=dict)
    assigned_agent_id: Optional[str] = None
    parent_task_id: Optional[str] = None


class TaskResult(BaseModel):
    """Represents the result of a task execution."""

    task_id: str
    agent_id: str
    status: str  # "success", "error", "partial", "timeout"
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float
    model_used: str
    cost_estimate: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentConfig(BaseModel):
    """Configuration for an agent."""

    name: str
    description: str
    agent_type: AgentType
    capabilities: list[str]
    model_preferences: dict[str, str]
    routing_rules: list[dict[str, Any]] = Field(default_factory=list)
    personality: dict[str, str] = Field(default_factory=dict)
    max_concurrent_tasks: int = Field(default=3, ge=1)
    task_timeout_seconds: float = Field(default=300.0, gt=0)
    health_check_interval: float = Field(default=30.0, gt=0)
    memory_retention_hours: int = Field(default=24, ge=1)
    auto_restart: bool = True


class BaseAgent(ABC):
    """
    Base class for all agents in the AIOSv3 platform.

    Provides common functionality for:
    - Task execution with lifecycle management
    - State tracking and health monitoring
    - Model routing and LLM integration
    - Memory management and persistence
    - Communication with other agents
    - Error handling and recovery
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        config: Optional[AgentConfig] = None,
        llm_router=None,
        message_queue=None,
        memory_store=None,
        agent_registry=None,
        agent_discovery=None,
    ):
        # Core identity and configuration
        self.id = agent_id or str(uuid.uuid4())
        self.config = config

        # External dependencies
        self.llm_router = llm_router
        self.message_queue = message_queue
        self.memory_store = memory_store
        self.agent_registry = agent_registry
        self.agent_discovery = agent_discovery

        # Communication interface (initialized during startup)
        self.communication: Any = None  # Will be AgentCommunicationInterface

        # State management
        self.state = AgentState.INITIALIZING
        self.start_time = time.time()
        self.last_heartbeat = datetime.utcnow()

        # Task management
        self.current_tasks: dict[str, Task] = {}
        self.task_history: list[TaskResult] = []
        self.task_queue: asyncio.Queue = asyncio.Queue()

        # Memory and statistics
        self.memory: dict[str, Any] = {}
        self.stats = AgentStats(agent_id=self.id)
        self.error_count = 0
        self.last_error: Optional[str] = None

        # Background tasks
        self._background_tasks: set[asyncio.Task] = set()
        self._shutdown_event = asyncio.Event()

        # Initialize logging for this agent
        self.logger = logging.getLogger(f"agent.{self.id}")

        # Create agent metadata
        self.metadata = self._create_metadata()

    def _create_metadata(self) -> AgentMetadata:
        """Create agent metadata from configuration."""
        if not self.config:
            return AgentMetadata(
                id=self.id,
                type=AgentType.GENERALIST,
                name=f"Agent-{self.id[:8]}",
                description="Generic agent with basic capabilities",
            )

        return AgentMetadata(
            id=self.id,
            type=self.config.agent_type,
            name=self.config.name,
            description=self.config.description,
        )

    @property
    def name(self) -> str:
        """Get the agent's name."""
        return self.metadata.name

    @property
    def agent_type(self) -> AgentType:
        """Get the agent's type."""
        return self.metadata.type

    @property
    def capabilities(self) -> list[str]:
        """Get the agent's capabilities."""
        return self.config.capabilities if self.config else []

    @property
    def is_busy(self) -> bool:
        """Check if the agent is currently busy with tasks."""
        return len(self.current_tasks) > 0

    @property
    def can_accept_tasks(self) -> bool:
        """Check if the agent can accept new tasks."""
        if self.state not in [AgentState.IDLE, AgentState.BUSY]:
            return False

        max_tasks = self.config.max_concurrent_tasks if self.config else 1
        return len(self.current_tasks) < max_tasks

    @property
    def uptime_seconds(self) -> float:
        """Get the agent's uptime in seconds."""
        return time.time() - self.start_time

    async def start(self) -> None:
        """Start the agent and begin background processes."""
        try:
            self.logger.info(
                f"Starting agent {self.name} (type: {self.agent_type.value})"
            )
            self.state = AgentState.INITIALIZING

            # Initialize external dependencies
            await self._initialize_dependencies()

            # Load persistent memory
            await self._load_memory()

            # Call subclass initialization
            await self.on_start()

            # Start background tasks
            await self._start_background_tasks()

            # Mark as idle and ready for tasks
            self.state = AgentState.IDLE
            self.last_heartbeat = datetime.utcnow()

            self.logger.info(f"Agent {self.name} started successfully")

        except Exception as e:
            self.state = AgentState.ERROR
            self.error_count += 1
            self.last_error = str(e)
            self.logger.error(f"Failed to start agent {self.name}: {e}")
            raise AgentInitializationError(f"Agent startup failed: {e}", self.id)

    async def stop(self, graceful: bool = True) -> None:
        """Stop the agent gracefully or forcefully."""
        try:
            self.logger.info(f"Stopping agent {self.name} (graceful: {graceful})")
            self.state = AgentState.STOPPING

            # Signal shutdown to background tasks
            self._shutdown_event.set()

            if graceful:
                # Wait for current tasks to complete
                await self._wait_for_tasks_completion()

                # Save memory state
                await self._save_memory()

            # Stop background tasks
            await self._stop_background_tasks()

            # Call subclass cleanup
            await self.on_stop()

            self.state = AgentState.STOPPED
            self.logger.info(f"Agent {self.name} stopped successfully")

        except Exception as e:
            self.state = AgentState.ERROR
            self.logger.error(f"Error stopping agent {self.name}: {e}")
            raise

    async def restart(self) -> None:
        """Restart the agent."""
        self.logger.info(f"Restarting agent {self.name}")
        await self.stop(graceful=True)
        await asyncio.sleep(1)  # Brief pause
        await self.start()

    async def on_start(self) -> None:
        """Called during agent startup. Override in subclasses."""
        pass

    async def on_stop(self) -> None:
        """Called during agent shutdown. Override in subclasses."""
        pass

    async def execute_task(self, task: Task) -> TaskResult:
        """
        Execute a task and return the result.

        Args:
            task: The task to execute

        Returns:
            TaskResult: The result of the task execution
        """
        start_time = asyncio.get_event_loop().time()

        try:
            self.logger.info(f"Executing task {task.id}: {task.description}")

            # Check if agent can handle this task
            if not self.can_handle_task(task):
                raise ValueError(
                    f"Agent {self.name} cannot handle task type: {task.type}"
                )

            # Route to appropriate model
            model_id = await self._route_to_model(task)

            # Execute the task
            result = await self._execute_task_internal(task, model_id)

            execution_time = asyncio.get_event_loop().time() - start_time

            task_result = TaskResult(
                task_id=task.id,
                agent_id=self.id,
                status="success",
                result=result,
                execution_time=execution_time,
                model_used=model_id,
            )

            # Store in history
            self.task_history.append(task_result)

            self.logger.info(
                f"Task {task.id} completed successfully in {execution_time:.2f}s"
            )
            return task_result

        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time

            task_result = TaskResult(
                task_id=task.id,
                agent_id=self.id,
                status="error",
                error=str(e),
                execution_time=execution_time,
                model_used="unknown",
            )

            self.task_history.append(task_result)
            self.logger.error(f"Task {task.id} failed: {e}")
            return task_result

    def can_handle_task(self, task: Task) -> bool:
        """
        Check if this agent can handle the given task.

        Args:
            task: The task to check

        Returns:
            bool: True if the agent can handle the task
        """
        # Basic implementation - check if task type matches capabilities
        return task.type in self.capabilities or "general" in self.capabilities

    async def _route_to_model(self, task: Task) -> str:
        """
        Route the task to the appropriate model.

        Args:
            task: The task to route

        Returns:
            str: The model ID to use
        """
        if self.llm_router:
            routing_decision = await self.llm_router.route_request(
                agent_id=self.id,
                task=task.dict(),
                context={"agent_config": self.config.dict() if self.config else {}},
            )
            return routing_decision.model_id

        # Fallback to primary model
        if self.config and self.config.model_preferences:
            return self.config.model_preferences.get("primary", "claude-3-sonnet")

        return "claude-3-sonnet"  # Default fallback

    @abstractmethod
    async def _execute_task_internal(self, task: Task, model_id: str) -> dict[str, Any]:
        """
        Internal task execution logic. Must be implemented by subclasses.

        Args:
            task: The task to execute
            model_id: The model to use for execution

        Returns:
            Dict[str, Any]: The task result data
        """
        pass

    async def communicate_with_agent(
        self, target_agent_id: str, message: str, message_type: str = "general"
    ) -> Optional[str]:
        """
        Send a message to another agent.

        Args:
            target_agent_id: ID of the target agent
            message: Message content
            message_type: Type of message

        Returns:
            Optional[str]: Response from the target agent, if any
        """
        if not self.communication:
            self.logger.warning("Communication interface not initialized")
            return None

        try:
            from .communication import MessageType

            # Convert string message type to enum
            msg_type = MessageType.NOTIFICATION
            if message_type == "request":
                msg_type = MessageType.REQUEST
            elif message_type == "response":
                msg_type = MessageType.RESPONSE

            if msg_type == MessageType.REQUEST:
                # Send request and wait for response
                response = await self.communication.send_request(
                    recipient_id=target_agent_id,
                    subject=message,
                    content={"message": message},
                    message_type=msg_type,
                )
                return response.get("data", {}).get("message", "")
            else:
                # Send notification
                await self.communication.send_notification(
                    recipient_id=target_agent_id,
                    subject=message,
                    content={"message": message},
                )
                return None

        except Exception as e:
            self.logger.error(f"Failed to communicate with {target_agent_id}: {e}")
            return None

    def get_memory(self, key: str) -> Any:
        """Get a value from agent memory."""
        return self.memory.get(key)

    def set_memory(self, key: str, value: Any) -> None:
        """Set a value in agent memory."""
        self.memory[key] = value

    def get_status(self) -> dict[str, Any]:
        """Get the current status of the agent."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.agent_type.value,
            "state": self.state.value,
            "is_busy": self.is_busy,
            "can_accept_tasks": self.can_accept_tasks,
            "capabilities": self.capabilities,
            "current_tasks": len(self.current_tasks),
            "tasks_completed": len(self.task_history),
            "memory_size": len(self.memory),
            "uptime_seconds": self.uptime_seconds,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "last_heartbeat": self.last_heartbeat.isoformat(),
        }

    def get_health(self) -> AgentHealth:
        """Get detailed health information for the agent."""
        return AgentHealth(
            agent_id=self.id,
            state=self.state,
            last_heartbeat=self.last_heartbeat,
            last_task_completed=self.stats.last_active,
            error_count=self.error_count,
            last_error=self.last_error,
            uptime_seconds=self.uptime_seconds,
            is_healthy=self._is_healthy(),
            health_score=self._calculate_health_score(),
        )

    def _is_healthy(self) -> bool:
        """Check if the agent is in a healthy state."""
        if self.state in [AgentState.ERROR, AgentState.UNHEALTHY, AgentState.STOPPED]:
            return False

        # Check if heartbeat is recent
        time_since_heartbeat = (datetime.utcnow() - self.last_heartbeat).total_seconds()
        heartbeat_threshold = (
            (self.config.health_check_interval * 2) if self.config else 60
        )

        return time_since_heartbeat < heartbeat_threshold

    def _calculate_health_score(self) -> float:
        """Calculate a health score between 0.0 and 1.0."""
        if not self._is_healthy():
            return 0.0

        # Base score
        score = 1.0

        # Reduce score based on recent errors
        if self.error_count > 0:
            # Reduce by 10% for each error in recent history, min 0.5
            error_penalty = min(0.5, self.error_count * 0.1)
            score -= error_penalty

        # Consider task success rate if we have history
        if len(self.task_history) > 0:
            success_rate = self.stats.success_rate
            score = (score + success_rate) / 2

        return max(0.0, min(1.0, score))

    # Placeholder methods for lifecycle helpers
    async def _initialize_dependencies(self) -> None:
        """Initialize external dependencies."""
        # Initialize communication interface if message queue is available
        if self.message_queue:
            from .communication import AgentCommunicationInterface

            self.communication = AgentCommunicationInterface(
                agent_id=self.id,
                message_queue=self.message_queue,
                discovery=self.agent_discovery,
            )
            await self.communication.initialize()

            # Register default message handlers
            await self._setup_default_message_handlers()

        # Register with agent registry if available
        if self.agent_registry:
            from ..types import RegistrationRequest

            registration_request = RegistrationRequest(
                metadata=self.metadata,
                initial_state=self.state,
                config=self.config.model_dump() if self.config else {},
            )
            await self.agent_registry.register_agent(registration_request)

    async def _load_memory(self) -> None:
        """Load persistent memory from storage."""
        if self.memory_store:
            try:
                # Implementation would depend on memory store interface
                pass
            except Exception as e:
                self.logger.warning(f"Failed to load memory: {e}")

    async def _save_memory(self) -> None:
        """Save current memory to persistent storage."""
        if self.memory_store:
            try:
                # Implementation would depend on memory store interface
                pass
            except Exception as e:
                self.logger.warning(f"Failed to save memory: {e}")

    async def _start_background_tasks(self) -> None:
        """Start background monitoring and maintenance tasks."""
        if self.config:
            # Health check task
            health_task = asyncio.create_task(self._health_check_loop())
            self._background_tasks.add(health_task)
            health_task.add_done_callback(self._background_tasks.discard)

    async def _stop_background_tasks(self) -> None:
        """Stop all background tasks."""
        for task in self._background_tasks:
            task.cancel()

        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)

        self._background_tasks.clear()

    async def _wait_for_tasks_completion(self, timeout: float = 30.0) -> None:
        """Wait for current tasks to complete."""
        if not self.current_tasks:
            return

        self.logger.info(f"Waiting for {len(self.current_tasks)} tasks to complete")

        try:
            await asyncio.wait_for(self._wait_for_all_tasks(), timeout=timeout)
        except asyncio.TimeoutError:
            self.logger.warning(
                f"Timeout waiting for tasks to complete, proceeding with shutdown"
            )

    async def _wait_for_all_tasks(self) -> None:
        """Wait until all current tasks are completed."""
        while self.current_tasks:
            await asyncio.sleep(0.1)

    async def _health_check_loop(self) -> None:
        """Background health check loop."""
        if not self.config:
            return

        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_check()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health check error: {e}")

    async def _perform_health_check(self) -> None:
        """Perform a health check and update status."""
        self.last_heartbeat = datetime.utcnow()

        # Update health status
        if not self._is_healthy():
            if self.state != AgentState.ERROR:
                self.state = AgentState.UNHEALTHY
                self.logger.warning(f"Agent {self.name} marked as unhealthy")
        elif self.state == AgentState.UNHEALTHY:
            self.state = AgentState.IDLE if not self.is_busy else AgentState.BUSY
            self.logger.info(f"Agent {self.name} recovered to healthy state")

    async def _setup_default_message_handlers(self) -> None:
        """Set up default message handlers for common message types."""
        if not self.communication:
            return

        from .communication import MessageType

        # Register handlers for different message types
        self.communication.register_handler(
            MessageType.HEALTH_CHECK, self._handle_health_check_message
        )

        self.communication.register_handler(
            MessageType.STATUS_UPDATE, self._handle_status_update_message
        )

        self.communication.register_handler(
            MessageType.TASK_ASSIGNMENT, self._handle_task_assignment_message
        )

        self.communication.register_handler(
            MessageType.TASK_DELEGATION, self._handle_task_delegation_message
        )

    async def _handle_health_check_message(self, message: Any) -> None:
        """Handle health check messages."""
        from .communication import MessageType

        try:
            # Update heartbeat
            self.last_heartbeat = datetime.utcnow()

            # Send health status response if requested
            if message.requires_response:
                health_data = {
                    "agent_id": self.id,
                    "health_score": self._calculate_health_score(),
                    "state": self.state.value,
                    "uptime_seconds": self.uptime_seconds,
                    "is_healthy": self._is_healthy(),
                }

                await self.communication.send_response(
                    request_message=message,
                    content=health_data,
                    success=True,
                )

        except Exception as e:
            self.logger.error(f"Error handling health check message: {e}")

    async def _handle_status_update_message(self, message: Any) -> None:
        """Handle status update messages."""
        try:
            # Log status update request
            self.logger.info(f"Status update requested by {message.sender_id}")

            # Send current status if response is required
            if message.requires_response:
                status_data = self.get_status()

                await self.communication.send_response(
                    request_message=message,
                    content=status_data,
                    success=True,
                )

        except Exception as e:
            self.logger.error(f"Error handling status update message: {e}")

    async def _handle_task_assignment_message(self, message: Any) -> None:
        """Handle task assignment messages."""
        try:
            # Extract task information from message
            content = message.content
            task_type_str = content.get("task_type")
            description = content.get("description", "")
            parameters = content.get("parameters", {})

            if not task_type_str:
                if message.requires_response:
                    await self.communication.send_response(
                        request_message=message,
                        content={"error": "Missing task_type in assignment"},
                        success=False,
                    )
                return

            # Create task from assignment
            from .agent import Task
            from .types import TaskType

            task = Task(
                type=TaskType(task_type_str),
                description=description,
                parameters=parameters,
                assigned_agent_id=self.id,
                context={"assigned_by": message.sender_id},
            )

            # Check if we can handle this task
            if not self.can_handle_task(task):
                if message.requires_response:
                    await self.communication.send_response(
                        request_message=message,
                        content={"error": f"Cannot handle task type {task_type_str}"},
                        success=False,
                    )
                return

            # Execute the task
            result = await self.execute_task(task)

            # Send result if response is required
            if message.requires_response:
                await self.communication.send_response(
                    request_message=message,
                    content={
                        "task_result": result.model_dump(),
                        "execution_successful": result.status == "success",
                    },
                    success=True,
                )

        except Exception as e:
            self.logger.error(f"Error handling task assignment: {e}")
            if message.requires_response:
                try:
                    await self.communication.send_response(
                        request_message=message,
                        content={"error": str(e)},
                        success=False,
                    )
                except Exception:
                    pass  # Avoid cascading errors

    async def _handle_task_delegation_message(self, message: Any) -> None:
        """Handle task delegation messages."""
        # For now, treat delegation the same as assignment
        # Subclasses can override for more sophisticated delegation handling
        await self._handle_task_assignment_message(message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"
