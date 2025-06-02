"""
Base agent framework for AIOSv3 platform.

Provides foundational classes and utilities for building specialized agents
including lifecycle management, health monitoring, and recovery mechanisms.
"""

from .health import (
    AgentHealthReport,
    ComponentHealth,
    HealthCheck,
    HealthMetric,
    HealthMonitor,
    HealthStatus,
)
from .lifecycle import (
    AgentLifecycleManager,
    AgentState,
    LifecycleEvent,
    LifecycleHooks,
    StateTransition,
)
from .recovery import (
    RecoveryAction,
    RecoveryCheckpoint,
    RecoveryManager,
    RecoveryPolicy,
    RecoveryStrategy,
)

__all__ = [
    # Health monitoring
    "HealthStatus",
    "HealthMetric",
    "HealthCheck",
    "ComponentHealth",
    "AgentHealthReport",
    "HealthMonitor",
    # Lifecycle management
    "AgentState",
    "StateTransition",
    "LifecycleEvent",
    "LifecycleHooks",
    "AgentLifecycleManager",
    # Recovery mechanisms
    "RecoveryStrategy",
    "RecoveryAction",
    "RecoveryPolicy",
    "RecoveryCheckpoint",
    "RecoveryManager",
]
