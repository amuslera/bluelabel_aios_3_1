"""
Agent type definitions and enums for AIOSv3 platform.

Defines agent lifecycle states, types, capabilities, and metadata schemas.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class AgentState(Enum):
    """Lifecycle states for agents."""

    INITIALIZING = "initializing"  # Agent is starting up
    IDLE = "idle"  # Agent is running but not processing tasks
    BUSY = "busy"  # Agent is actively processing a task
    WAITING = "waiting"  # Agent is waiting for external response
    ERROR = "error"  # Agent encountered an error
    STOPPING = "stopping"  # Agent is shutting down gracefully
    STOPPED = "stopped"  # Agent has been stopped
    UNHEALTHY = "unhealthy"  # Agent health check failed


class AgentType(Enum):
    """Types of agents in the platform."""

    CTO = "cto"  # Chief Technology Officer - architecture, decisions
    BACKEND_DEV = "backend_developer"  # Backend development specialist
    FRONTEND_DEV = "frontend_developer"  # Frontend development specialist
    QA_ENGINEER = "qa_engineer"  # Quality assurance specialist
    DEVOPS = "devops"  # DevOps and infrastructure specialist
    PRODUCT_MANAGER = "product_manager"  # Product management specialist
    DESIGNER = "designer"  # UI/UX design specialist
    DATA_ENGINEER = "data_engineer"  # Data engineering specialist
    SECURITY = "security"  # Security specialist
    GENERALIST = "generalist"  # General purpose agent


class TaskType(Enum):
    """Types of tasks that agents can handle."""

    # Development tasks
    CODE_REVIEW = "code_review"
    CODE_GENERATION = "code_generation"
    BUG_FIX = "bug_fix"
    REFACTORING = "refactoring"
    TESTING = "testing"
    DOCUMENTATION = "documentation"

    # Architecture tasks
    SYSTEM_DESIGN = "system_design"
    TECH_DECISION = "tech_decision"
    ARCHITECTURE_REVIEW = "architecture_review"
    PERFORMANCE_ANALYSIS = "performance_analysis"

    # DevOps tasks
    DEPLOYMENT = "deployment"
    MONITORING_SETUP = "monitoring_setup"
    INFRASTRUCTURE = "infrastructure"
    CI_CD = "ci_cd"

    # Analysis tasks
    REQUIREMENTS_ANALYSIS = "requirements_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    FEASIBILITY_STUDY = "feasibility_study"

    # Communication tasks
    AGENT_COLLABORATION = "agent_collaboration"
    STATUS_REPORT = "status_report"
    KNOWLEDGE_SHARING = "knowledge_sharing"

    # General tasks
    GENERAL = "general"
    RESEARCH = "research"
    PLANNING = "planning"


class Priority(Enum):
    """Task priority levels."""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 5
    LOW = 8
    BACKGROUND = 10


class AgentCapability(BaseModel):
    """Represents a capability that an agent has."""

    name: str
    description: str
    task_types: list[TaskType]
    complexity_range: tuple[int, int] = (
        1,
        10,
    )  # Min and max complexity this capability can handle
    requires_tools: list[str] = Field(default_factory=list)
    confidence_level: float = Field(default=1.0, ge=0.0, le=1.0)


class AgentMetadata(BaseModel):
    """Metadata about an agent instance."""

    id: str
    type: AgentType
    name: str
    description: str
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    owner: str = "system"
    tags: list[str] = Field(default_factory=list)
    capabilities: list[AgentCapability] = Field(default_factory=list)


class AgentHealth(BaseModel):
    """Health status of an agent."""

    agent_id: str
    state: AgentState
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    last_task_completed: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    response_time_ms: float = 0.0
    uptime_seconds: float = 0.0
    is_healthy: bool = True
    health_score: float = Field(default=1.0, ge=0.0, le=1.0)


class AgentStats(BaseModel):
    """Statistics for an agent."""

    agent_id: str
    tasks_completed: int = 0
    tasks_failed: int = 0
    average_execution_time: float = 0.0
    total_cost: float = 0.0
    models_used: dict[str, int] = Field(default_factory=dict)
    success_rate: float = 1.0
    last_active: datetime = Field(default_factory=datetime.utcnow)


class RegistrationRequest(BaseModel):
    """Request to register an agent with the registry."""

    metadata: AgentMetadata
    initial_state: AgentState = AgentState.INITIALIZING
    endpoint: Optional[str] = None  # For remote agents
    config: dict[str, Any] = Field(default_factory=dict)


class RegistrationResponse(BaseModel):
    """Response from agent registration."""

    success: bool
    agent_id: str
    message: str
    assigned_queues: list[str] = Field(default_factory=list)
    registry_endpoint: Optional[str] = None


# Default capabilities for each agent type
DEFAULT_CAPABILITIES = {
    AgentType.CTO: [
        AgentCapability(
            name="Architecture Design",
            description="Design system architecture and make technical decisions",
            task_types=[
                TaskType.SYSTEM_DESIGN,
                TaskType.TECH_DECISION,
                TaskType.ARCHITECTURE_REVIEW,
            ],
            complexity_range=(5, 10),
        ),
        AgentCapability(
            name="Code Review",
            description="Review code for architecture compliance and best practices",
            task_types=[TaskType.CODE_REVIEW],
            complexity_range=(3, 10),
        ),
        AgentCapability(
            name="Strategic Planning",
            description="Plan technical strategy and roadmap",
            task_types=[TaskType.PLANNING, TaskType.FEASIBILITY_STUDY],
            complexity_range=(6, 10),
        ),
    ],
    AgentType.BACKEND_DEV: [
        AgentCapability(
            name="Backend Development",
            description="Develop server-side applications and APIs",
            task_types=[
                TaskType.CODE_GENERATION,
                TaskType.BUG_FIX,
                TaskType.REFACTORING,
            ],
            complexity_range=(2, 9),
        ),
        AgentCapability(
            name="API Design",
            description="Design and implement RESTful APIs",
            task_types=[TaskType.CODE_GENERATION, TaskType.SYSTEM_DESIGN],
            complexity_range=(3, 8),
        ),
        AgentCapability(
            name="Database Design",
            description="Design and optimize database schemas",
            task_types=[TaskType.SYSTEM_DESIGN, TaskType.PERFORMANCE_ANALYSIS],
            complexity_range=(4, 9),
        ),
    ],
    AgentType.FRONTEND_DEV: [
        AgentCapability(
            name="Frontend Development",
            description="Develop user interfaces and web applications",
            task_types=[
                TaskType.CODE_GENERATION,
                TaskType.BUG_FIX,
                TaskType.REFACTORING,
            ],
            complexity_range=(2, 8),
        ),
        AgentCapability(
            name="UI/UX Implementation",
            description="Implement user interface designs",
            task_types=[TaskType.CODE_GENERATION],
            complexity_range=(2, 7),
        ),
    ],
    AgentType.QA_ENGINEER: [
        AgentCapability(
            name="Test Development",
            description="Create and maintain automated tests",
            task_types=[TaskType.TESTING, TaskType.CODE_GENERATION],
            complexity_range=(2, 8),
        ),
        AgentCapability(
            name="Quality Assurance",
            description="Ensure code quality and find bugs",
            task_types=[TaskType.CODE_REVIEW, TaskType.BUG_FIX],
            complexity_range=(3, 9),
        ),
    ],
    AgentType.DEVOPS: [
        AgentCapability(
            name="Infrastructure Management",
            description="Manage cloud infrastructure and deployments",
            task_types=[
                TaskType.INFRASTRUCTURE,
                TaskType.DEPLOYMENT,
                TaskType.MONITORING_SETUP,
            ],
            complexity_range=(4, 10),
        ),
        AgentCapability(
            name="CI/CD Pipeline",
            description="Design and maintain CI/CD pipelines",
            task_types=[TaskType.CI_CD, TaskType.DEPLOYMENT],
            complexity_range=(5, 9),
        ),
    ],
    AgentType.GENERALIST: [
        AgentCapability(
            name="General Problem Solving",
            description="Handle various types of tasks",
            task_types=[TaskType.GENERAL, TaskType.RESEARCH, TaskType.DOCUMENTATION],
            complexity_range=(1, 6),
        ),
    ],
}


def get_default_capabilities(agent_type: AgentType) -> list[AgentCapability]:
    """Get the default capabilities for an agent type."""
    return DEFAULT_CAPABILITIES.get(
        agent_type, DEFAULT_CAPABILITIES[AgentType.GENERALIST]
    )


def validate_agent_capability(agent_type: AgentType, task_type: TaskType) -> bool:
    """Check if an agent type can handle a specific task type."""
    capabilities = get_default_capabilities(agent_type)
    for capability in capabilities:
        if task_type in capability.task_types:
            return True
    return False
