"""
Unit tests for the base agent framework.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from typing import Any

from agents.base.agent import BaseAgent, Task, TaskResult, AgentConfig
from agents.base.types import AgentType, TaskType, Priority, AgentState
from agents.base.exceptions import AgentInitializationError, TaskExecutionError


class TestAgent(BaseAgent):
    """Test implementation of BaseAgent for testing purposes."""
    
    async def _execute_task_internal(self, task: Task, model_id: str) -> dict[str, Any]:
        """Simple test task execution."""
        return {"result": f"Completed task {task.id} with model {model_id}"}


@pytest.fixture
def agent_config():
    """Create a test agent configuration."""
    return AgentConfig(
        name="Test Agent",
        description="A test agent for unit testing",
        agent_type=AgentType.GENERALIST,
        capabilities=["general", "testing"],
        model_preferences={"primary": "claude-3-sonnet"},
        max_concurrent_tasks=2,
        task_timeout_seconds=60.0,
        health_check_interval=10.0,
    )


@pytest.fixture
def test_agent(agent_config):
    """Create a test agent instance."""
    return TestAgent(
        agent_id="test-agent-123",
        config=agent_config,
        llm_router=MagicMock(),
        message_queue=MagicMock(),
        memory_store=MagicMock(),
    )


@pytest.fixture
def sample_task():
    """Create a sample task for testing."""
    return Task(
        type=TaskType.GENERAL,
        description="Test task for unit testing",
        priority=Priority.MEDIUM,
        complexity=5,
    )


class TestBaseAgent:
    """Test cases for BaseAgent class."""

    def test_agent_initialization(self, agent_config):
        """Test agent initialization with configuration."""
        agent = TestAgent(config=agent_config)
        
        assert agent.name == "Test Agent"
        assert agent.agent_type == AgentType.GENERALIST
        assert agent.capabilities == ["general", "testing"]
        assert agent.state == AgentState.INITIALIZING
        assert not agent.is_busy
        assert agent.can_accept_tasks is False  # Not started yet

    def test_agent_initialization_without_config():
        """Test agent initialization without configuration."""
        agent = TestAgent()
        
        assert agent.name.startswith("Agent-")
        assert agent.agent_type == AgentType.GENERALIST
        assert agent.capabilities == []
        assert agent.state == AgentState.INITIALIZING

    def test_agent_properties(self, test_agent):
        """Test agent property methods."""
        assert test_agent.id == "test-agent-123"
        assert test_agent.name == "Test Agent"
        assert test_agent.agent_type == AgentType.GENERALIST
        assert not test_agent.is_busy
        assert test_agent.uptime_seconds >= 0

    def test_agent_status(self, test_agent):
        """Test agent status reporting."""
        status = test_agent.get_status()
        
        assert status["id"] == "test-agent-123"
        assert status["name"] == "Test Agent"
        assert status["type"] == "generalist"
        assert status["state"] == "initializing"
        assert status["current_tasks"] == 0
        assert status["tasks_completed"] == 0
        assert isinstance(status["uptime_seconds"], float)

    def test_agent_health(self, test_agent):
        """Test agent health reporting."""
        health = test_agent.get_health()
        
        assert health.agent_id == "test-agent-123"
        assert health.state == AgentState.INITIALIZING
        assert isinstance(health.health_score, float)
        assert 0.0 <= health.health_score <= 1.0

    def test_health_score_calculation(self, test_agent):
        """Test health score calculation logic."""
        # Healthy agent should have high score
        test_agent.state = AgentState.IDLE
        test_agent.error_count = 0
        score = test_agent._calculate_health_score()
        assert score == 1.0

        # Agent with errors should have reduced score
        test_agent.error_count = 2
        score = test_agent._calculate_health_score()
        assert score < 1.0

        # Unhealthy agent should have zero score
        test_agent.state = AgentState.ERROR
        score = test_agent._calculate_health_score()
        assert score == 0.0

    def test_task_capability_check(self, test_agent, sample_task):
        """Test task capability validation."""
        # Agent should be able to handle general tasks
        assert test_agent.can_handle_task(sample_task)

        # Agent should not handle unsupported task types
        specific_task = Task(
            type=TaskType.CODE_REVIEW,
            description="Review this code",
            priority=Priority.HIGH,
        )
        assert not test_agent.can_handle_task(specific_task)

    def test_memory_operations(self, test_agent):
        """Test agent memory get/set operations."""
        # Test setting and getting memory
        test_agent.set_memory("test_key", "test_value")
        assert test_agent.get_memory("test_key") == "test_value"

        # Test getting non-existent key
        assert test_agent.get_memory("non_existent") is None

        # Test complex data structures
        complex_data = {"nested": {"data": [1, 2, 3]}}
        test_agent.set_memory("complex", complex_data)
        assert test_agent.get_memory("complex") == complex_data

    @pytest.mark.asyncio
    async def test_agent_start_stop(self, test_agent):
        """Test agent start and stop lifecycle."""
        # Mock the background task methods to avoid actual task creation
        test_agent._start_background_tasks = AsyncMock()
        test_agent._stop_background_tasks = AsyncMock()
        test_agent._load_memory = AsyncMock()
        test_agent._save_memory = AsyncMock()
        test_agent._wait_for_tasks_completion = AsyncMock()

        # Test starting the agent
        await test_agent.start()
        assert test_agent.state == AgentState.IDLE

        # Test stopping the agent
        await test_agent.stop()
        assert test_agent.state == AgentState.STOPPED

    @pytest.mark.asyncio
    async def test_agent_restart(self, test_agent):
        """Test agent restart functionality."""
        # Mock lifecycle methods
        test_agent.start = AsyncMock()
        test_agent.stop = AsyncMock()

        await test_agent.restart()

        test_agent.stop.assert_called_once_with(graceful=True)
        test_agent.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_task_execution_success(self, test_agent, sample_task):
        """Test successful task execution."""
        # Mock the LLM router
        test_agent.llm_router.route_request = AsyncMock(
            return_value=MagicMock(model_id="claude-3-sonnet")
        )

        result = await test_agent.execute_task(sample_task)

        assert isinstance(result, TaskResult)
        assert result.status == "success"
        assert result.agent_id == test_agent.id
        assert result.task_id == sample_task.id
        assert result.model_used == "claude-3-sonnet"
        assert "result" in result.result

    @pytest.mark.asyncio
    async def test_task_execution_failure(self, test_agent):
        """Test task execution with capability error."""
        # Create a task the agent can't handle
        unsupported_task = Task(
            type=TaskType.CODE_REVIEW,
            description="Review this code",
        )

        result = await test_agent.execute_task(unsupported_task)

        assert result.status == "error"
        assert "cannot handle task type" in result.error

    @pytest.mark.asyncio
    async def test_task_execution_with_router_failure(self, test_agent, sample_task):
        """Test task execution when LLM router fails."""
        # Mock router to raise an exception
        test_agent.llm_router.route_request = AsyncMock(side_effect=Exception("Router error"))

        result = await test_agent.execute_task(sample_task)

        assert result.status == "error"
        assert "Router error" in result.error

    def test_can_accept_tasks_logic(self, test_agent):
        """Test the logic for determining if agent can accept new tasks."""
        # Agent in initializing state should not accept tasks
        test_agent.state = AgentState.INITIALIZING
        assert not test_agent.can_accept_tasks

        # Idle agent should accept tasks
        test_agent.state = AgentState.IDLE
        assert test_agent.can_accept_tasks

        # Busy agent should accept tasks if under limit
        test_agent.state = AgentState.BUSY
        test_agent.current_tasks = {"task1": MagicMock()}
        assert test_agent.can_accept_tasks  # Under limit of 2

        # Agent at max capacity should not accept tasks
        test_agent.current_tasks = {"task1": MagicMock(), "task2": MagicMock()}
        assert not test_agent.can_accept_tasks

        # Stopped agent should not accept tasks
        test_agent.state = AgentState.STOPPED
        test_agent.current_tasks = {}
        assert not test_agent.can_accept_tasks

    def test_agent_repr(self, test_agent):
        """Test agent string representation."""
        repr_str = repr(test_agent)
        assert "TestAgent" in repr_str
        assert test_agent.id in repr_str
        assert test_agent.name in repr_str


class TestAgentTypes:
    """Test cases for agent type definitions."""

    def test_agent_state_enum(self):
        """Test AgentState enum values."""
        assert AgentState.INITIALIZING.value == "initializing"
        assert AgentState.IDLE.value == "idle"
        assert AgentState.BUSY.value == "busy"
        assert AgentState.ERROR.value == "error"
        assert AgentState.STOPPED.value == "stopped"

    def test_task_type_enum(self):
        """Test TaskType enum values."""
        assert TaskType.GENERAL.value == "general"
        assert TaskType.CODE_REVIEW.value == "code_review"
        assert TaskType.SYSTEM_DESIGN.value == "system_design"

    def test_priority_enum(self):
        """Test Priority enum values."""
        assert Priority.CRITICAL.value == 1
        assert Priority.HIGH.value == 2
        assert Priority.MEDIUM.value == 5
        assert Priority.LOW.value == 8


class TestAgentExceptions:
    """Test cases for agent exception handling."""

    def test_agent_error_creation(self):
        """Test basic AgentError creation."""
        from agents.base.exceptions import AgentError
        
        error = AgentError("Test error", agent_id="test-123", error_code="TEST_ERROR")
        
        assert str(error) == "Test error"
        assert error.agent_id == "test-123"
        assert error.error_code == "TEST_ERROR"

    def test_agent_error_to_dict(self):
        """Test AgentError serialization."""
        from agents.base.exceptions import AgentError
        
        error = AgentError("Test error", agent_id="test-123")
        error_dict = error.to_dict()
        
        assert error_dict["error_type"] == "AgentError"
        assert error_dict["message"] == "Test error"
        assert error_dict["agent_id"] == "test-123"

    def test_error_classification(self):
        """Test error severity and retry classification."""
        from agents.base.exceptions import (
            get_error_severity,
            is_retryable_error,
            TaskValidationError,
            TaskTimeoutError,
        )
        
        # Test severity classification
        validation_error = TaskValidationError("Invalid task")
        assert get_error_severity(validation_error) == "low"
        
        # Test retry classification
        assert not is_retryable_error(validation_error)  # Non-retryable
        
        timeout_error = TaskTimeoutError("Task timed out")
        assert is_retryable_error(timeout_error)  # Retryable