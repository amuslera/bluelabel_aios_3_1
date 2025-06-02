"""
Agent lifecycle management for AIOSv3 platform.

Provides comprehensive lifecycle management including state transitions,
health monitoring, graceful shutdown, and recovery mechanisms.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent lifecycle states."""

    INITIALIZING = "initializing"  # Agent is starting up
    IDLE = "idle"  # Agent is ready but not processing
    BUSY = "busy"  # Agent is actively processing tasks
    PAUSED = "paused"  # Agent is temporarily suspended
    STOPPING = "stopping"  # Agent is shutting down gracefully
    STOPPED = "stopped"  # Agent has shut down
    ERROR = "error"  # Agent encountered an error
    RECOVERING = "recovering"  # Agent is recovering from error


class StateTransition(BaseModel):
    """Represents a state transition."""

    from_state: AgentState
    to_state: AgentState
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reason: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LifecycleEvent(BaseModel):
    """Lifecycle event for logging and monitoring."""

    event_type: str
    state: AgentState
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str
    details: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class LifecycleHooks:
    """Manages lifecycle hooks for customization."""

    def __init__(self):
        self._hooks: Dict[str, List[Callable]] = {
            "pre_init": [],
            "post_init": [],
            "pre_start": [],
            "post_start": [],
            "pre_stop": [],
            "post_stop": [],
            "pre_pause": [],
            "post_pause": [],
            "pre_resume": [],
            "post_resume": [],
            "on_error": [],
            "on_recovery": [],
        }

    def register(self, hook_name: str, callback: Callable) -> None:
        """Register a lifecycle hook callback."""
        if hook_name not in self._hooks:
            raise ValueError(f"Unknown hook: {hook_name}")
        self._hooks[hook_name].append(callback)

    async def execute(self, hook_name: str, **kwargs) -> None:
        """Execute all callbacks for a hook."""
        if hook_name not in self._hooks:
            return

        for callback in self._hooks[hook_name]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(**kwargs)
                else:
                    callback(**kwargs)
            except Exception as e:
                logger.error(f"Error in lifecycle hook {hook_name}: {e}")


class AgentLifecycleManager:
    """
    Manages agent lifecycle states and transitions.

    Provides a state machine implementation with hooks, monitoring,
    and recovery capabilities.
    """

    # Valid state transitions
    VALID_TRANSITIONS = {
        AgentState.INITIALIZING: {
            AgentState.IDLE,
            AgentState.ERROR,
            AgentState.STOPPED,
        },
        AgentState.IDLE: {
            AgentState.BUSY,
            AgentState.PAUSED,
            AgentState.STOPPING,
            AgentState.ERROR,
        },
        AgentState.BUSY: {
            AgentState.IDLE,
            AgentState.PAUSED,
            AgentState.STOPPING,
            AgentState.ERROR,
        },
        AgentState.PAUSED: {AgentState.IDLE, AgentState.STOPPING, AgentState.ERROR},
        AgentState.STOPPING: {AgentState.STOPPED, AgentState.ERROR},
        AgentState.STOPPED: set(),  # Terminal state
        AgentState.ERROR: {
            AgentState.RECOVERING,
            AgentState.STOPPING,
            AgentState.STOPPED,
        },
        AgentState.RECOVERING: {AgentState.IDLE, AgentState.ERROR, AgentState.STOPPED},
    }

    def __init__(
        self, agent_id: str, initial_state: AgentState = AgentState.INITIALIZING
    ):
        """Initialize lifecycle manager."""
        self.agent_id = agent_id
        self._current_state = initial_state
        self._state_history: List[StateTransition] = []
        self._hooks = LifecycleHooks()
        self._state_lock = asyncio.Lock()
        self._event_handlers: Dict[str, List[Callable]] = {}

        # State persistence
        self._last_checkpoint: Optional[datetime] = None
        self._checkpoint_interval = timedelta(minutes=5)

        # Health monitoring
        self._health_checks: Dict[str, Callable] = {}
        self._last_health_check: Optional[datetime] = None
        self._health_check_interval = timedelta(seconds=30)

        # Recovery tracking
        self._error_count = 0
        self._recovery_attempts = 0
        self._max_recovery_attempts = 3

    @property
    def current_state(self) -> AgentState:
        """Get current agent state."""
        return self._current_state

    @property
    def state_history(self) -> List[StateTransition]:
        """Get state transition history."""
        return self._state_history.copy()

    def is_operational(self) -> bool:
        """Check if agent is in an operational state."""
        return self._current_state in {
            AgentState.IDLE,
            AgentState.BUSY,
            AgentState.PAUSED,
        }

    def can_transition_to(self, target_state: AgentState) -> bool:
        """Check if transition to target state is valid."""
        return target_state in self.VALID_TRANSITIONS.get(self._current_state, set())

    async def transition_to(
        self,
        target_state: AgentState,
        reason: Optional[str] = None,
        force: bool = False,
    ) -> bool:
        """
        Transition to a new state.

        Args:
            target_state: The target state to transition to
            reason: Optional reason for the transition
            force: Force transition even if not normally valid

        Returns:
            True if transition was successful
        """
        async with self._state_lock:
            # Check if transition is valid
            if not force and not self.can_transition_to(target_state):
                logger.warning(
                    f"Invalid state transition: {self._current_state} -> {target_state}"
                )
                return False

            # Create transition record
            transition = StateTransition(
                from_state=self._current_state, to_state=target_state, reason=reason
            )

            # Execute pre-transition hooks
            await self._execute_transition_hooks(transition, pre=True)

            # Update state
            old_state = self._current_state
            self._current_state = target_state
            self._state_history.append(transition)

            # Log transition
            logger.info(
                f"Agent {self.agent_id} transitioned: {old_state} -> {target_state}"
                f"{f' (reason: {reason})' if reason else ''}"
            )

            # Emit lifecycle event
            await self._emit_event(
                LifecycleEvent(
                    event_type="state_transition",
                    state=target_state,
                    agent_id=self.agent_id,
                    details={
                        "from_state": old_state.value,
                        "to_state": target_state.value,
                        "reason": reason,
                    },
                )
            )

            # Execute post-transition hooks
            await self._execute_transition_hooks(transition, pre=False)

            # Handle special state actions
            await self._handle_state_actions(target_state)

            return True

    async def initialize(self) -> bool:
        """Initialize the agent."""
        if self._current_state != AgentState.INITIALIZING:
            logger.warning(f"Cannot initialize from state: {self._current_state}")
            return False

        try:
            # Execute pre-init hooks
            await self._hooks.execute("pre_init", agent_id=self.agent_id)

            # Transition to idle
            success = await self.transition_to(
                AgentState.IDLE, reason="Initialization complete"
            )

            if success:
                # Execute post-init hooks
                await self._hooks.execute("post_init", agent_id=self.agent_id)

            return success

        except Exception as e:
            logger.error(f"Failed to initialize agent {self.agent_id}: {e}")
            await self.transition_to(AgentState.ERROR, reason=str(e), force=True)
            return False

    async def start(self) -> bool:
        """Start the agent (transition to busy)."""
        if self._current_state != AgentState.IDLE:
            logger.warning(f"Cannot start from state: {self._current_state}")
            return False

        try:
            # Execute pre-start hooks
            await self._hooks.execute("pre_start", agent_id=self.agent_id)

            # Transition to busy
            success = await self.transition_to(AgentState.BUSY, reason="Agent started")

            if success:
                # Execute post-start hooks
                await self._hooks.execute("post_start", agent_id=self.agent_id)

            return success

        except Exception as e:
            logger.error(f"Failed to start agent {self.agent_id}: {e}")
            await self.transition_to(AgentState.ERROR, reason=str(e), force=True)
            return False

    async def pause(self, reason: Optional[str] = None) -> bool:
        """Pause the agent."""
        if self._current_state not in {AgentState.IDLE, AgentState.BUSY}:
            logger.warning(f"Cannot pause from state: {self._current_state}")
            return False

        try:
            # Execute pre-pause hooks
            await self._hooks.execute("pre_pause", agent_id=self.agent_id)

            # Transition to paused
            success = await self.transition_to(
                AgentState.PAUSED, reason=reason or "Agent paused"
            )

            if success:
                # Execute post-pause hooks
                await self._hooks.execute("post_pause", agent_id=self.agent_id)

            return success

        except Exception as e:
            logger.error(f"Failed to pause agent {self.agent_id}: {e}")
            return False

    async def resume(self) -> bool:
        """Resume the agent from paused state."""
        if self._current_state != AgentState.PAUSED:
            logger.warning(f"Cannot resume from state: {self._current_state}")
            return False

        try:
            # Execute pre-resume hooks
            await self._hooks.execute("pre_resume", agent_id=self.agent_id)

            # Transition to idle
            success = await self.transition_to(AgentState.IDLE, reason="Agent resumed")

            if success:
                # Execute post-resume hooks
                await self._hooks.execute("post_resume", agent_id=self.agent_id)

            return success

        except Exception as e:
            logger.error(f"Failed to resume agent {self.agent_id}: {e}")
            return False

    async def stop(self, graceful: bool = True) -> bool:
        """Stop the agent."""
        if self._current_state == AgentState.STOPPED:
            return True

        if self._current_state not in {
            AgentState.IDLE,
            AgentState.BUSY,
            AgentState.PAUSED,
            AgentState.ERROR,
            AgentState.STOPPING,
        }:
            logger.warning(f"Cannot stop from state: {self._current_state}")
            if not graceful:
                # Force stop
                return await self.transition_to(AgentState.STOPPED, force=True)
            return False

        try:
            # Execute pre-stop hooks
            await self._hooks.execute("pre_stop", agent_id=self.agent_id)

            # Transition to stopping
            if self._current_state != AgentState.STOPPING:
                await self.transition_to(
                    AgentState.STOPPING, reason="Shutdown initiated"
                )

            # Perform graceful shutdown if requested
            if graceful:
                await self._graceful_shutdown()

            # Transition to stopped
            success = await self.transition_to(
                AgentState.STOPPED, reason="Agent stopped"
            )

            if success:
                # Execute post-stop hooks
                await self._hooks.execute("post_stop", agent_id=self.agent_id)

            return success

        except Exception as e:
            logger.error(f"Failed to stop agent {self.agent_id}: {e}")
            # Force stop on error
            return await self.transition_to(AgentState.STOPPED, force=True)

    async def handle_error(self, error: Exception, auto_recover: bool = True) -> bool:
        """Handle an error condition."""
        self._error_count += 1

        # Transition to error state
        await self.transition_to(
            AgentState.ERROR, reason=f"Error: {str(error)}", force=True
        )

        # Execute error hooks
        await self._hooks.execute("on_error", agent_id=self.agent_id, error=error)

        # Emit error event
        await self._emit_event(
            LifecycleEvent(
                event_type="error",
                state=self._current_state,
                agent_id=self.agent_id,
                error=str(error),
                details={"error_count": self._error_count},
            )
        )

        # Attempt recovery if enabled
        if auto_recover and self._recovery_attempts < self._max_recovery_attempts:
            return await self.attempt_recovery()

        return False

    async def attempt_recovery(self) -> bool:
        """Attempt to recover from error state."""
        if self._current_state != AgentState.ERROR:
            return False

        self._recovery_attempts += 1

        try:
            # Transition to recovering
            await self.transition_to(
                AgentState.RECOVERING,
                reason=f"Recovery attempt {self._recovery_attempts}",
            )

            # Execute recovery hooks
            await self._hooks.execute("on_recovery", agent_id=self.agent_id)

            # Perform recovery actions
            await self._perform_recovery()

            # Transition back to idle
            success = await self.transition_to(
                AgentState.IDLE, reason="Recovery successful"
            )

            if success:
                self._error_count = 0
                self._recovery_attempts = 0

            return success

        except Exception as e:
            logger.error(f"Recovery failed for agent {self.agent_id}: {e}")
            await self.transition_to(AgentState.ERROR, reason=str(e), force=True)
            return False

    def register_health_check(self, name: str, check_func: Callable) -> None:
        """Register a health check function."""
        self._health_checks[name] = check_func

    async def check_health(self) -> Dict[str, Any]:
        """Perform health checks."""
        health_status = {
            "agent_id": self.agent_id,
            "state": self._current_state.value,
            "operational": self.is_operational(),
            "checks": {},
            "timestamp": datetime.utcnow(),
        }

        # Run registered health checks
        for name, check_func in self._health_checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()

                health_status["checks"][name] = {
                    "status": "healthy" if result else "unhealthy",
                    "result": result,
                }
            except Exception as e:
                health_status["checks"][name] = {"status": "error", "error": str(e)}

        # Update last health check time
        self._last_health_check = datetime.utcnow()

        return health_status

    async def save_state(self, storage_backend: Any) -> bool:
        """Save current state to persistent storage."""
        try:
            state_data = {
                "agent_id": self.agent_id,
                "current_state": self._current_state.value,
                "state_history": [
                    {
                        "from_state": t.from_state.value,
                        "to_state": t.to_state.value,
                        "timestamp": t.timestamp.isoformat(),
                        "reason": t.reason,
                        "metadata": t.metadata,
                    }
                    for t in self._state_history[-100:]  # Keep last 100 transitions
                ],
                "error_count": self._error_count,
                "recovery_attempts": self._recovery_attempts,
                "last_checkpoint": datetime.utcnow().isoformat(),
            }

            # Save to storage backend
            await storage_backend.save_agent_state(self.agent_id, state_data)

            self._last_checkpoint = datetime.utcnow()
            return True

        except Exception as e:
            logger.error(f"Failed to save state for agent {self.agent_id}: {e}")
            return False

    async def restore_state(self, storage_backend: Any) -> bool:
        """Restore state from persistent storage."""
        try:
            state_data = await storage_backend.get_agent_state(self.agent_id)

            if not state_data:
                return False

            # Restore state
            self._current_state = AgentState(state_data["current_state"])
            self._error_count = state_data.get("error_count", 0)
            self._recovery_attempts = state_data.get("recovery_attempts", 0)

            # Restore history
            self._state_history = []
            for transition_data in state_data.get("state_history", []):
                self._state_history.append(
                    StateTransition(
                        from_state=AgentState(transition_data["from_state"]),
                        to_state=AgentState(transition_data["to_state"]),
                        timestamp=datetime.fromisoformat(transition_data["timestamp"]),
                        reason=transition_data.get("reason"),
                        metadata=transition_data.get("metadata", {}),
                    )
                )

            logger.info(
                f"Restored state for agent {self.agent_id}: {self._current_state}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to restore state for agent {self.agent_id}: {e}")
            return False

    def add_event_handler(self, event_type: str, handler: Callable) -> None:
        """Add an event handler."""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    async def _emit_event(self, event: LifecycleEvent) -> None:
        """Emit a lifecycle event."""
        handlers = self._event_handlers.get(event.event_type, [])

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Error in event handler for {event.event_type}: {e}")

    async def _execute_transition_hooks(
        self, transition: StateTransition, pre: bool = True
    ) -> None:
        """Execute hooks for state transitions."""
        # Map transitions to hook names
        hook_mapping = {
            (AgentState.INITIALIZING, AgentState.IDLE): ("pre_init", "post_init"),
            (AgentState.IDLE, AgentState.BUSY): ("pre_start", "post_start"),
            (AgentState.BUSY, AgentState.IDLE): ("pre_stop", "post_stop"),
            (AgentState.IDLE, AgentState.PAUSED): ("pre_pause", "post_pause"),
            (AgentState.BUSY, AgentState.PAUSED): ("pre_pause", "post_pause"),
            (AgentState.PAUSED, AgentState.IDLE): ("pre_resume", "post_resume"),
        }

        transition_key = (transition.from_state, transition.to_state)
        if transition_key in hook_mapping:
            hook_name = hook_mapping[transition_key][0 if pre else 1]
            await self._hooks.execute(
                hook_name, agent_id=self.agent_id, transition=transition
            )

    async def _handle_state_actions(self, state: AgentState) -> None:
        """Handle special actions for specific states."""
        if state == AgentState.ERROR:
            # Log error state
            logger.error(f"Agent {self.agent_id} entered ERROR state")

        elif state == AgentState.STOPPED:
            # Clean up resources
            logger.info(f"Agent {self.agent_id} stopped, cleaning up resources")

        elif state == AgentState.RECOVERING:
            # Start recovery timer
            logger.info(f"Agent {self.agent_id} starting recovery")

    async def _graceful_shutdown(self, timeout: float = 30.0) -> None:
        """Perform graceful shutdown."""
        logger.info(f"Starting graceful shutdown for agent {self.agent_id}")

        try:
            # Wait for current operations to complete (with timeout)
            await asyncio.wait_for(self._wait_for_idle(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Graceful shutdown timeout for agent {self.agent_id}")

    async def _wait_for_idle(self) -> None:
        """Wait for agent to become idle."""
        while self._current_state == AgentState.BUSY:
            await asyncio.sleep(0.1)

    async def _perform_recovery(self) -> None:
        """Perform recovery actions."""
        # This would be customized based on agent type
        # For now, just wait a bit
        await asyncio.sleep(1.0)

    def get_state_duration(self, state: Optional[AgentState] = None) -> timedelta:
        """Get duration in current or specified state."""
        target_state = state or self._current_state

        # Find last transition to this state
        for transition in reversed(self._state_history):
            if transition.to_state == target_state:
                return datetime.utcnow() - transition.timestamp

        return timedelta(0)

    def get_uptime(self) -> timedelta:
        """Get total agent uptime (time not in STOPPED state)."""
        if not self._state_history:
            return timedelta(0)

        # Calculate from first transition
        first_transition = self._state_history[0]
        return datetime.utcnow() - first_transition.timestamp
