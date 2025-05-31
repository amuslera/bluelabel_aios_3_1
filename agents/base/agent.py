"""
Base agent implementation for AIOSv3 platform.
"""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Task(BaseModel):
    """Represents a task to be executed by an agent."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=5, ge=1, le=10)
    complexity: int = Field(default=5, ge=1, le=10)
    requires_privacy: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deadline: datetime | None = None
    context: dict[str, Any] = Field(default_factory=dict)


class TaskResult(BaseModel):
    """Represents the result of a task execution."""

    task_id: str
    agent_id: str
    status: str  # "success", "error", "partial", "timeout"
    result: dict[str, Any] | None = None
    error: str | None = None
    execution_time: float
    model_used: str
    cost_estimate: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentConfig(BaseModel):
    """Configuration for an agent."""

    name: str
    description: str
    role: str
    capabilities: list[str]
    model_preferences: dict[str, str]
    routing_rules: list[dict[str, Any]] = Field(default_factory=list)
    personality: dict[str, str] = Field(default_factory=dict)


class BaseAgent(ABC):
    """
    Base class for all agents in the AIOSv3 platform.

    Provides common functionality for:
    - Task execution
    - Model routing
    - Memory management
    - Communication with other agents
    """

    def __init__(
        self,
        agent_id: str | None = None,
        config: AgentConfig | None = None,
        llm_router=None,
    ):
        self.id = agent_id or str(uuid.uuid4())
        self.config = config
        self.llm_router = llm_router
        self.memory: dict[str, Any] = {}
        self.task_history: list[TaskResult] = []
        self.is_active = False

        # Initialize logging for this agent
        self.logger = logging.getLogger(f"agent.{self.id}")

    @property
    def name(self) -> str:
        """Get the agent's name."""
        return self.config.name if self.config else f"Agent-{self.id[:8]}"

    @property
    def capabilities(self) -> list[str]:
        """Get the agent's capabilities."""
        return self.config.capabilities if self.config else []

    async def start(self) -> None:
        """Start the agent."""
        self.is_active = True
        self.logger.info(f"Agent {self.name} started")
        await self.on_start()

    async def stop(self) -> None:
        """Stop the agent."""
        self.is_active = False
        self.logger.info(f"Agent {self.name} stopped")
        await self.on_stop()

    async def on_start(self) -> None:
        """Called when the agent starts. Override in subclasses."""
        pass

    async def on_stop(self) -> None:
        """Called when the agent stops. Override in subclasses."""
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
    ) -> str | None:
        """
        Send a message to another agent.

        Args:
            target_agent_id: ID of the target agent
            message: Message content
            message_type: Type of message

        Returns:
            Optional[str]: Response from the target agent, if any
        """
        # TODO: Implement inter-agent communication
        self.logger.info(f"Sending message to {target_agent_id}: {message}")
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
            "is_active": self.is_active,
            "capabilities": self.capabilities,
            "tasks_completed": len(self.task_history),
            "memory_size": len(self.memory),
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"
