"""Enhanced base agent that integrates all infrastructure components."""
import asyncio
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from pydantic import BaseModel, Field, validator

# Import new infrastructure components
from src.agents.base.lifecycle import AgentLifecycleManager, AgentState
from src.agents.base.health import HealthMonitor, HealthStatus
from src.agents.base.recovery import RecoveryManager
from src.agents.base.exceptions import AgentError
from src.core.memory.base import MemoryType, MemoryPriority, MemoryScope
from src.core.routing.router import LLMRouter
from src.core.routing.router import RoutingContext, RoutingStrategy, RoutingDecision
from src.core.routing.providers.base import LLMRequest, LLMResponse

# Import existing types
from .types import AgentType, TaskType, Priority, AgentHealth, AgentStats, AgentMetadata


class MockMemoryManager:
    """Simplified memory manager for testing and development."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._conversations = {}
        self._knowledge = {}
    
    async def initialize(self):
        """Initialize memory manager."""
        pass
    
    async def cleanup(self):
        """Cleanup memory manager."""
        pass
    
    async def store_conversation(self, conversation_id: str, role: str, content: str, metadata: Dict[str, Any] = None):
        """Store conversation message."""
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []
        self._conversations[conversation_id].append({
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow()
        })
    
    async def get_conversation_history(self, conversation_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self._conversations.get(conversation_id, [])[-limit:]
    
    async def store_knowledge(self, content: str, category: str, keywords: List[str], 
                            metadata: Optional[Dict[str, Any]] = None, scope: MemoryScope = MemoryScope.AGENT_INSTANCE) -> str:
        """Store knowledge."""
        knowledge_id = str(uuid.uuid4())
        self._knowledge[knowledge_id] = {
            "content": content,
            "category": category,
            "keywords": keywords,
            "metadata": metadata or {},
            "scope": scope,
            "created_at": datetime.utcnow()
        }
        return knowledge_id
    
    async def search_knowledge(self, query: str, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search knowledge base."""
        results = []
        for knowledge_id, knowledge in self._knowledge.items():
            if category and knowledge["category"] != category:
                continue
            # Simple keyword matching
            if any(keyword in query.lower() for keyword in knowledge["keywords"]):
                results.append({
                    "id": knowledge_id,
                    "content": knowledge["content"],
                    "category": knowledge["category"],
                    "relevance": 1.0
                })
        return results[:limit]


class AgentCapability(str, Enum):
    """Capabilities that agents can advertise."""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    ARCHITECTURE_DESIGN = "architecture_design"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    DATA_ANALYSIS = "data_analysis"
    UI_DESIGN = "ui_design"
    API_DESIGN = "api_design"
    SECURITY_AUDIT = "security_audit"
    DOCUMENTATION = "documentation"
    PROJECT_MANAGEMENT = "project_management"


class EnhancedAgentConfig(BaseModel):
    """Enhanced configuration for an agent with infrastructure settings."""
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_type: AgentType
    name: str
    description: str
    capabilities: List[AgentCapability]
    
    # Routing preferences
    default_routing_strategy: RoutingStrategy = RoutingStrategy.BALANCED
    preferred_models: Optional[List[str]] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    
    # Resource limits
    max_memory_mb: int = 512
    max_cpu_percent: float = 80.0
    health_check_interval: int = 30
    
    # Recovery settings
    max_recovery_attempts: int = 3
    recovery_timeout: int = 300
    enable_circuit_breaker: bool = True
    
    # Memory settings
    memory_backend: str = "redis"
    memory_ttl_seconds: Optional[int] = None
    enable_memory_compression: bool = True
    
    @validator('agent_id')
    def validate_agent_id(cls, v):
        """Ensure agent_id is a valid UUID string."""
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("agent_id must be a valid UUID")
        return v


class EnhancedTask(BaseModel):
    """Enhanced task model with routing information."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: TaskType
    prompt: str
    context: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    privacy_sensitive: bool = False
    complexity: int = Field(default=5, ge=1, le=10)
    priority: Priority = Priority.MEDIUM
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None


class EnhancedTaskResult(BaseModel):
    """Enhanced result of a task execution."""
    task_id: str
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tokens_used: int = 0
    cost: float = 0.0
    execution_time: float = 0.0
    model_used: str = "unknown"
    provider_used: str = "unknown"
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class EnhancedBaseAgent(ABC):
    """Enhanced base class for all agents with full infrastructure integration."""
    
    def __init__(self, config: EnhancedAgentConfig):
        """Initialize the enhanced agent with all infrastructure components."""
        self.config = config
        self.agent_id = config.agent_id
        self.agent_type = config.agent_type
        
        # Initialize lifecycle manager
        self.lifecycle = AgentLifecycleManager(self.agent_id)
        
        # Initialize health monitor
        self.health = HealthMonitor(agent_id=self.agent_id)
        
        # Initialize recovery manager
        self.recovery = RecoveryManager(agent_id=self.agent_id)
        
        # Initialize memory manager (simplified for now)
        # TODO: Integrate with actual AIOSMemoryManager
        self.memory = MockMemoryManager(self.agent_id)
        
        # Initialize LLM router
        self.router = LLMRouter()
        
        # Task tracking
        self._current_task: Optional[EnhancedTask] = None
        self._task_history: List[EnhancedTaskResult] = []
        
        # Internal state
        self._initialized = False
        self._shutdown_event = asyncio.Event()
        
        # Create metadata
        self.metadata = AgentMetadata(
            id=self.agent_id,
            type=self.agent_type,
            name=self.config.name,
            description=self.config.description
        )
    
    async def initialize(self) -> None:
        """Initialize the agent and all its components."""
        try:
            # Transition to initializing state
            await self.lifecycle.transition_to(AgentState.INITIALIZING)
            
            # Initialize memory manager
            await self.memory.initialize()
            
            # Initialize router (if it has initialize method)
            if hasattr(self.router, 'initialize'):
                await self.router.initialize()
            
            # Start health monitoring (if it has this method)
            if hasattr(self.health, 'start_monitoring'):
                await self.health.start_monitoring()
            
            # Recovery manager doesn't need initialization
            
            # Custom initialization
            await self._on_initialize()
            
            # Mark as initialized
            self._initialized = True
            
            # Transition to idle state
            await self.lifecycle.transition_to(AgentState.IDLE)
            
        except Exception as e:
            await self.lifecycle.transition_to(AgentState.ERROR)
            raise Exception(f"Failed to initialize agent: {str(e)}")
    
    async def start(self) -> None:
        """Start the agent's main loop."""
        if not self._initialized:
            await self.initialize()
        
        # Run the main agent loop
        await self._run_loop()
    
    async def stop(self) -> None:
        """Stop the agent gracefully."""
        try:
            await self.lifecycle.transition_to(AgentState.STOPPING)
            
            # Set shutdown event
            self._shutdown_event.set()
            
            # Stop health monitoring (if it has this method)
            if hasattr(self.health, 'stop_monitoring'):
                await self.health.stop_monitoring()
            
            # Custom shutdown
            await self._on_shutdown()
            
            # Cleanup memory
            await self.memory.cleanup()
            
            # Cleanup router (if it has cleanup method)
            if hasattr(self.router, 'cleanup'):
                await self.router.cleanup()
            
            # Transition to stopped
            await self.lifecycle.transition_to(AgentState.STOPPED)
            
        except Exception as e:
            await self.lifecycle.transition_to(AgentState.ERROR)
            raise Exception(f"Failed to stop agent: {str(e)}")
    
    async def process_task(self, task: EnhancedTask) -> EnhancedTaskResult:
        """Process a task with full error handling and recovery."""
        start_time = datetime.utcnow()
        
        try:
            # Transition to busy state
            await self.lifecycle.transition_to(AgentState.BUSY)
            self._current_task = task
            
            # Store task in conversation history
            await self.memory.store_conversation(
                conversation_id=task.task_id,
                role="user",
                content=task.prompt,
                metadata=task.metadata
            )
            
            # Execute with recovery (if available)
            if hasattr(self.recovery, 'execute_with_recovery'):
                result = await self.recovery.execute_with_recovery(
                    self._execute_task,
                    task
                )
            else:
                # Execute directly without recovery for now
                result = await self._execute_task(task)
            
            # Store result in conversation history
            await self.memory.store_conversation(
                conversation_id=task.task_id,
                role="assistant",
                content=result.output or "",
                metadata=result.metadata
            )
            
            # Track task history
            self._task_history.append(result)
            
            return result
            
        except AgentError as e:
            # All recovery attempts failed
            error_result = EnhancedTaskResult(
                task_id=task.task_id,
                success=False,
                error=f"Task failed after recovery attempts: {str(e)}",
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
            self._task_history.append(error_result)
            return error_result
            
        finally:
            self._current_task = None
            if self.lifecycle.current_state == AgentState.BUSY:
                await self.lifecycle.transition_to(AgentState.IDLE)
    
    async def _execute_task(self, task: EnhancedTask) -> EnhancedTaskResult:
        """Execute a task using the LLM router."""
        start_time = datetime.utcnow()
        
        try:
            # Get relevant context from memory
            context = await self._get_task_context(task)
            
            # Build prompt with context
            full_prompt = await self._build_prompt(task, context)
            
            # Map task type to routing task type
            routing_task_type = self._map_task_type(task.task_type)
            
            # Create routing context
            routing_context = RoutingContext(
                task_type=routing_task_type,
                agent_id=self.agent_id,
                privacy_sensitive=task.privacy_sensitive,
                complexity=task.complexity,
                required_capabilities=self._get_required_capabilities(routing_task_type)
            )
            
            # Route and execute request
            llm_request = LLMRequest(
                messages=[{"role": "user", "content": full_prompt}],
                model_id="mock-cto-model",  # Will be overridden by routing decision
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                stream=False
            )
            
            # Create routing policy from strategy
            from src.core.routing.router import RoutingPolicy
            policy = RoutingPolicy(strategy=self.config.default_routing_strategy)
            
            decision = await self.router.route_request(
                llm_request,
                routing_context,
                policy=policy
            )
            
            # Generate response
            response = await self.router.execute_request(llm_request, decision)
            
            # Process the response
            result_output = await self._process_response(response, task)
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return EnhancedTaskResult(
                task_id=task.task_id,
                success=True,
                output=result_output,
                tokens_used=response.total_tokens,
                cost=decision.estimated_cost,
                execution_time=execution_time,
                model_used=decision.model_id,
                provider_used=decision.provider_name,
                metadata={
                    "routing_strategy": policy.strategy.value,
                    "complexity": task.complexity,
                    "privacy_sensitive": task.privacy_sensitive
                }
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return EnhancedTaskResult(
                task_id=task.task_id,
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming messages from other agents or systems."""
        message_type = message.get("type", "unknown")
        
        if message_type == "task":
            # Convert to task and process
            task_data = message.get("payload", {})
            task = EnhancedTask(**task_data)
            result = await self.process_task(task)
            return result.dict()
        
        elif message_type == "health_check":
            # Return current health status
            health_status = await self.health.check_health()
            return {
                "agent_id": self.agent_id,
                "health": health_status.dict(),
                "lifecycle_state": self.lifecycle.current_state.value
            }
        
        elif message_type == "capability_query":
            # Return agent capabilities
            return {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "capabilities": [cap.value for cap in self.config.capabilities],
                "metadata": self.metadata.dict()
            }
        
        else:
            return {"error": f"Unknown message type: {message_type}"}
    
    async def llm_generate(
        self,
        prompt: str,
        routing_context: Optional[RoutingContext] = None,
        **kwargs
    ) -> LLMResponse:
        """Convenience method for LLM generation with routing."""
        if routing_context is None:
            routing_context = RoutingContext(
                task_type=TaskType.GENERAL,
                agent_id=self.agent_id
            )
        
        request = LLMRequest(
            messages=[{"role": "user", "content": prompt}],
            model_id=kwargs.get("model_id", "mock-cto-model"),  # Will be overridden by routing
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            temperature=kwargs.get("temperature", self.config.temperature),
            stream=kwargs.get("stream", False)
        )
        
        # Create routing policy from strategy
        from src.core.routing.router import RoutingPolicy
        policy = RoutingPolicy(strategy=self.config.default_routing_strategy)
        
        decision = await self.router.route_request(
            request,
            routing_context,
            policy=policy
        )
        
        return await self.router.execute_request(request, decision)
    
    async def store_knowledge(
        self,
        content: str,
        category: str,
        keywords: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store knowledge in agent's memory."""
        return await self.memory.store_knowledge(
            content=content,
            category=category,
            keywords=keywords,
            metadata=metadata,
            scope=MemoryScope.AGENT_INSTANCE
        )
    
    async def search_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search agent's knowledge base."""
        return await self.memory.search_knowledge(
            query=query,
            category=category,
            limit=limit
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status."""
        return {
            "agent_id": self.agent_id,
            "name": self.config.name,
            "type": self.agent_type.value,
            "lifecycle_state": self.lifecycle.current_state.value,
            "capabilities": [cap.value for cap in self.config.capabilities],
            "current_task": self._current_task.task_id if self._current_task else None,
            "tasks_completed": len(self._task_history),
            "total_cost": sum(t.cost for t in self._task_history),
            "average_execution_time": (
                sum(t.execution_time for t in self._task_history) / len(self._task_history)
                if self._task_history else 0
            ),
            "success_rate": (
                len([t for t in self._task_history if t.success]) / len(self._task_history)
                if self._task_history else 1.0
            ),
            "metadata": self.metadata.dict()
        }
    
    # Private helper methods
    
    async def _run_loop(self) -> None:
        """Main agent loop - can be overridden by subclasses."""
        while not self._shutdown_event.is_set():
            try:
                # Default implementation just waits
                await asyncio.sleep(1)
                
                # Check health periodically
                if self.lifecycle.current_state == AgentState.IDLE:
                    health_status = await self.health.check_health()
                    if health_status.status == HealthStatus.UNHEALTHY:
                        await self.lifecycle.transition_to(AgentState.ERROR)
                        # Trigger recovery
                        await self.recovery.handle_error(
                            Exception("Agent unhealthy"),
                            context={"health_status": health_status.dict()}
                        )
                        
            except Exception as e:
                await self._handle_loop_error(e)
    
    async def _handle_loop_error(self, error: Exception) -> None:
        """Handle errors in the main loop."""
        try:
            await self.lifecycle.transition_to(AgentState.ERROR)
            await self.recovery.handle_error(error)
            
            # If recovery succeeded, go back to idle
            if self.lifecycle.current_state == AgentState.RECOVERING:
                await self.lifecycle.transition_to(AgentState.IDLE)
                
        except Exception:
            # Fatal error - stop the agent
            await self.stop()
    
    async def _get_task_context(self, task: EnhancedTask) -> str:
        """Get relevant context for a task from memory."""
        contexts = []
        
        # Get conversation history if this is part of an ongoing conversation
        if task.context and "conversation_id" in task.context:
            history = await self.memory.get_conversation_history(
                task.context["conversation_id"],
                limit=10
            )
            if history:
                contexts.append("Previous conversation:\\n" + 
                              "\\n".join([f"{h['role']}: {h['content']}" for h in history]))
        
        # Search for relevant knowledge
        if task.prompt:
            knowledge = await self.search_knowledge(task.prompt, limit=5)
            if knowledge:
                contexts.append("Relevant knowledge:\\n" +
                              "\\n".join([k['content'] for k in knowledge]))
        
        return "\\n\\n".join(contexts) if contexts else ""
    
    async def _build_prompt(self, task: EnhancedTask, context: str) -> str:
        """Build the full prompt including context."""
        parts = []
        
        # Add agent identity
        parts.append(f"You are a {self.config.name} agent with the following capabilities: " +
                    ", ".join([cap.value for cap in self.config.capabilities]))
        
        # Add context if available
        if context:
            parts.append(f"Context:\\n{context}")
        
        # Add the actual task
        parts.append(f"Task: {task.prompt}")
        
        # Add metadata if any
        if task.metadata:
            parts.append(f"Additional information: {task.metadata}")
        
        # Custom prompt building
        custom_prompt = await self._customize_prompt(task, context)
        if custom_prompt:
            parts.append(custom_prompt)
        
        return "\\n\\n".join(parts)
    
    def _map_task_type(self, task_type: TaskType) -> TaskType:
        """Map agent task type (just pass through for now)."""
        # Since routing uses the same TaskType, we can pass through directly
        return task_type
    
    def _get_required_capabilities(self, task_type: TaskType) -> List[str]:
        """Get required model capabilities for a task type."""
        capability_map = {
            TaskType.CODE_GENERATION: ["code_generation", "reasoning"],
            TaskType.CODE_REVIEW: ["code_analysis", "reasoning"],
            TaskType.BUG_FIX: ["code_analysis", "reasoning"],
            TaskType.DOCUMENTATION: ["text_generation"],
            TaskType.TESTING: ["code_generation", "reasoning"],
            TaskType.SYSTEM_DESIGN: ["reasoning", "text_generation"],
            TaskType.TECH_DECISION: ["reasoning", "text_generation"],
            TaskType.GENERAL: ["text_generation"]
        }
        return capability_map.get(task_type, ["text_generation"])
    
    # Abstract methods to be implemented by subclasses
    
    @abstractmethod
    async def _on_initialize(self) -> None:
        """Custom initialization logic for specific agent types."""
        pass
    
    @abstractmethod
    async def _on_shutdown(self) -> None:
        """Custom shutdown logic for specific agent types."""
        pass
    
    @abstractmethod
    async def _process_response(self, response: LLMResponse, task: EnhancedTask) -> str:
        """Process the LLM response for the specific agent type."""
        pass
    
    @abstractmethod
    async def _customize_prompt(self, task: EnhancedTask, context: str) -> str:
        """Customize the prompt for the specific agent type."""
        pass