"""
Agent-specific exception classes for AIOSv3 platform.

Provides structured error handling for agent operations, task execution,
and system integration failures.
"""

from typing import Any, Optional


class AgentError(Exception):
    """Base exception for all agent-related errors."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        super().__init__(message)
        self.agent_id = agent_id
        self.error_code = error_code
        self.message = message

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "agent_id": self.agent_id,
            "error_code": self.error_code,
        }


class AgentInitializationError(AgentError):
    """Raised when an agent fails to initialize properly."""

    pass


class AgentRegistrationError(AgentError):
    """Raised when agent registration with the registry fails."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        registry_response: Optional[dict] = None,
    ):
        super().__init__(message, agent_id, "REGISTRATION_FAILED")
        self.registry_response = registry_response


class AgentStateError(AgentError):
    """Raised when an agent is in an invalid state for the requested operation."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        current_state: Optional[str] = None,
        expected_state: Optional[str] = None,
    ):
        super().__init__(message, agent_id, "INVALID_STATE")
        self.current_state = current_state
        self.expected_state = expected_state


class TaskExecutionError(AgentError):
    """Raised when task execution fails."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        task_type: Optional[str] = None,
    ):
        super().__init__(message, agent_id, "TASK_EXECUTION_FAILED")
        self.task_id = task_id
        self.task_type = task_type


class TaskValidationError(AgentError):
    """Raised when task validation fails."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        validation_errors: Optional[list[str]] = None,
    ):
        super().__init__(message, agent_id, "TASK_VALIDATION_FAILED")
        self.task_id = task_id
        self.validation_errors = validation_errors or []


class TaskTimeoutError(AgentError):
    """Raised when task execution times out."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ):
        super().__init__(message, agent_id, "TASK_TIMEOUT")
        self.task_id = task_id
        self.timeout_seconds = timeout_seconds


class AgentCapabilityError(AgentError):
    """Raised when an agent lacks the capability to handle a task."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        required_capability: Optional[str] = None,
        available_capabilities: Optional[list[str]] = None,
    ):
        super().__init__(message, agent_id, "INSUFFICIENT_CAPABILITY")
        self.required_capability = required_capability
        self.available_capabilities = available_capabilities or []


class AgentCommunicationError(AgentError):
    """Raised when agent-to-agent communication fails."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        target_agent_id: Optional[str] = None,
        communication_type: Optional[str] = None,
    ):
        super().__init__(message, agent_id, "COMMUNICATION_FAILED")
        self.target_agent_id = target_agent_id
        self.communication_type = communication_type


class AgentMemoryError(AgentError):
    """Raised when agent memory operations fail."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        memory_operation: Optional[str] = None,
    ):
        super().__init__(message, agent_id, "MEMORY_ERROR")
        self.memory_operation = memory_operation


class AgentHealthError(AgentError):
    """Raised when agent health checks fail."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        health_check_type: Optional[str] = None,
        health_score: Optional[float] = None,
    ):
        super().__init__(message, agent_id, "HEALTH_CHECK_FAILED")
        self.health_check_type = health_check_type
        self.health_score = health_score


class LLMRoutingError(AgentError):
    """Raised when LLM routing fails."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        requested_model: Optional[str] = None,
        available_models: Optional[list[str]] = None,
    ):
        super().__init__(message, agent_id, "LLM_ROUTING_FAILED")
        self.requested_model = requested_model
        self.available_models = available_models or []


class ModelExecutionError(AgentError):
    """Raised when LLM model execution fails."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        model_id: Optional[str] = None,
        provider: Optional[str] = None,
    ):
        super().__init__(message, agent_id, "MODEL_EXECUTION_FAILED")
        self.model_id = model_id
        self.provider = provider


class ResourceLimitError(AgentError):
    """Raised when agent hits resource limits."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        limit_value: Optional[float] = None,
    ):
        super().__init__(message, agent_id, "RESOURCE_LIMIT_EXCEEDED")
        self.resource_type = resource_type
        self.limit_value = limit_value


class ConfigurationError(AgentError):
    """Raised when agent configuration is invalid."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        config_key: Optional[str] = None,
    ):
        super().__init__(message, agent_id, "INVALID_CONFIGURATION")
        self.config_key = config_key


class DependencyError(AgentError):
    """Raised when agent dependencies are unavailable."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        dependency_name: Optional[str] = None,
        dependency_type: Optional[str] = None,
    ):
        super().__init__(message, agent_id, "DEPENDENCY_UNAVAILABLE")
        self.dependency_name = dependency_name
        self.dependency_type = dependency_type


# Exception mappings for error classification
ERROR_SEVERITY_MAP = {
    AgentError: "medium",
    AgentInitializationError: "high",
    AgentRegistrationError: "high",
    AgentStateError: "medium",
    TaskExecutionError: "medium",
    TaskValidationError: "low",
    TaskTimeoutError: "medium",
    AgentCapabilityError: "low",
    AgentCommunicationError: "medium",
    AgentMemoryError: "high",
    AgentHealthError: "high",
    LLMRoutingError: "medium",
    ModelExecutionError: "medium",
    ResourceLimitError: "high",
    ConfigurationError: "high",
    DependencyError: "high",
}

RETRYABLE_ERRORS = {
    TaskTimeoutError,
    AgentCommunicationError,
    ModelExecutionError,
    DependencyError,
}

NON_RETRYABLE_ERRORS = {
    AgentInitializationError,
    TaskValidationError,
    AgentCapabilityError,
    ConfigurationError,
}


def get_error_severity(error: Exception) -> str:
    """Get the severity level of an error."""
    error_type = type(error)
    return ERROR_SEVERITY_MAP.get(error_type, "medium")


def is_retryable_error(error: Exception) -> bool:
    """Check if an error is retryable."""
    error_type = type(error)
    if error_type in NON_RETRYABLE_ERRORS:
        return False
    if error_type in RETRYABLE_ERRORS:
        return True
    # Default to retryable for unknown errors
    return True


def create_error_context(
    error: Exception, agent_id: Optional[str] = None, task_id: Optional[str] = None
) -> dict[str, Any]:
    """Create error context for logging and monitoring."""
    context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "severity": get_error_severity(error),
        "retryable": is_retryable_error(error),
        "timestamp": "utcnow",  # Would be replaced with actual timestamp
    }

    if agent_id:
        context["agent_id"] = agent_id
    if task_id:
        context["task_id"] = task_id

    # Add specific error attributes if available
    if hasattr(error, "to_dict"):
        context.update(error.to_dict())

    return context
