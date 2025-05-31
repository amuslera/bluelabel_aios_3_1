"""
Recovery mechanisms for AIOSv3 agents.

Provides automatic recovery strategies, state restoration, and
resilience patterns for agent failures.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field

from .lifecycle import AgentState

logger = logging.getLogger(__name__)


class RecoveryStrategy(Enum):
    """Available recovery strategies."""

    RESTART = "restart"  # Full agent restart
    RESET = "reset"  # Reset to initial state
    RESUME = "resume"  # Resume from last checkpoint
    RETRY = "retry"  # Retry failed operation
    FAILOVER = "failover"  # Switch to backup agent
    DEGRADED = "degraded"  # Continue with reduced functionality


class RecoveryAction(BaseModel):
    """Recovery action to be taken."""

    strategy: RecoveryStrategy
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reason: str
    error_context: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 3
    success: Optional[bool] = None


class RecoveryPolicy(BaseModel):
    """Policy for recovery decisions."""

    enabled: bool = True
    strategies: List[RecoveryStrategy] = Field(
        default_factory=lambda: [RecoveryStrategy.RETRY, RecoveryStrategy.RESTART]
    )
    max_recovery_attempts: int = 3
    recovery_timeout_seconds: int = 300
    backoff_multiplier: float = 2.0
    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    error_threshold: int = 5  # Errors before recovery
    time_window_minutes: int = 5  # Time window for error counting


class RecoveryCheckpoint(BaseModel):
    """State checkpoint for recovery."""

    checkpoint_id: str
    agent_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    state: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    valid_until: Optional[datetime] = None


class RecoveryManager:
    """
    Manages agent recovery operations.

    Implements various recovery strategies and coordinates
    the recovery process for failed agents.
    """

    def __init__(self, agent_id: str, policy: Optional[RecoveryPolicy] = None):
        """Initialize recovery manager."""
        self.agent_id = agent_id
        self.policy = policy or RecoveryPolicy()

        # Recovery state
        self._recovery_history: List[RecoveryAction] = []
        self._error_timestamps: List[datetime] = []
        self._recovery_in_progress = False
        self._last_checkpoint: Optional[RecoveryCheckpoint] = None

        # Recovery callbacks
        self._recovery_callbacks: Dict[RecoveryStrategy, List[Callable]] = {
            strategy: [] for strategy in RecoveryStrategy
        }

        # Circuit breaker
        self._circuit_open = False
        self._circuit_open_until: Optional[datetime] = None

    def register_recovery_handler(
        self, strategy: RecoveryStrategy, handler: Callable
    ) -> None:
        """Register a recovery handler for a strategy."""
        self._recovery_callbacks[strategy].append(handler)

    async def handle_failure(
        self, error: Exception, context: Optional[Dict[str, Any]] = None
    ) -> Optional[RecoveryAction]:
        """Handle an agent failure and determine recovery action."""
        # Record error timestamp
        self._error_timestamps.append(datetime.utcnow())
        self._cleanup_old_errors()

        # Check if circuit breaker is open
        if self._is_circuit_open():
            logger.warning(f"Circuit breaker open for agent {self.agent_id}")
            return None

        # Check if recovery is already in progress
        if self._recovery_in_progress:
            logger.warning(f"Recovery already in progress for agent {self.agent_id}")
            return None

        # Check error threshold
        if not self._should_attempt_recovery():
            logger.warning(
                f"Error threshold not reached for agent {self.agent_id}: "
                f"{len(self._error_timestamps)} errors in window"
            )
            return None

        # Determine recovery strategy
        strategy = self._select_recovery_strategy(error, context)

        if not strategy:
            logger.error(f"No suitable recovery strategy for agent {self.agent_id}")
            self._open_circuit_breaker()
            return None

        # Create recovery action
        action = RecoveryAction(
            strategy=strategy,
            reason=str(error),
            error_context=context or {},
            retry_count=self._get_retry_count(strategy),
        )

        # Execute recovery
        try:
            self._recovery_in_progress = True
            success = await self._execute_recovery(action)
            action.success = success

            if not success:
                self._handle_recovery_failure(action)
            else:
                self._handle_recovery_success(action)

        finally:
            self._recovery_in_progress = False
            self._recovery_history.append(action)

        return action

    async def create_checkpoint(
        self, state: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None
    ) -> RecoveryCheckpoint:
        """Create a recovery checkpoint."""
        checkpoint = RecoveryCheckpoint(
            checkpoint_id=f"{self.agent_id}_{datetime.utcnow().timestamp()}",
            agent_id=self.agent_id,
            state=state,
            metadata=metadata or {},
            valid_until=datetime.utcnow() + timedelta(hours=24),
        )

        self._last_checkpoint = checkpoint
        logger.info(
            f"Created checkpoint {checkpoint.checkpoint_id} for agent {self.agent_id}"
        )

        return checkpoint

    async def restore_from_checkpoint(
        self, checkpoint: Optional[RecoveryCheckpoint] = None
    ) -> Optional[Dict[str, Any]]:
        """Restore agent state from checkpoint."""
        target_checkpoint = checkpoint or self._last_checkpoint

        if not target_checkpoint:
            logger.warning(f"No checkpoint available for agent {self.agent_id}")
            return None

        # Check if checkpoint is still valid
        if (
            target_checkpoint.valid_until
            and datetime.utcnow() > target_checkpoint.valid_until
        ):
            logger.warning(f"Checkpoint {target_checkpoint.checkpoint_id} has expired")
            return None

        logger.info(
            f"Restoring agent {self.agent_id} from checkpoint {target_checkpoint.checkpoint_id}"
        )
        return target_checkpoint.state

    def _should_attempt_recovery(self) -> bool:
        """Check if recovery should be attempted."""
        if not self.policy.enabled:
            return False

        # Check recovery attempt limit
        recent_recoveries = [
            action
            for action in self._recovery_history
            if (datetime.utcnow() - action.timestamp).total_seconds()
            < 3600  # Last hour
        ]

        if len(recent_recoveries) >= self.policy.max_recovery_attempts:
            logger.warning(
                f"Max recovery attempts ({self.policy.max_recovery_attempts}) "
                f"reached for agent {self.agent_id}"
            )
            return False

        # Check error threshold
        return len(self._error_timestamps) >= self.policy.error_threshold

    def _select_recovery_strategy(
        self, error: Exception, context: Optional[Dict[str, Any]]
    ) -> Optional[RecoveryStrategy]:
        """Select appropriate recovery strategy."""
        # Check available strategies
        available_strategies = self.policy.strategies.copy()

        # Remove strategies that have failed recently
        for action in self._recovery_history[-3:]:  # Last 3 attempts
            if not action.success and action.strategy in available_strategies:
                available_strategies.remove(action.strategy)

        if not available_strategies:
            return None

        # Select strategy based on error type and context
        error_type = type(error).__name__

        # Memory errors -> restart
        if error_type in ["MemoryError", "ResourceExhausted"]:
            if RecoveryStrategy.RESTART in available_strategies:
                return RecoveryStrategy.RESTART

        # Temporary errors -> retry
        if error_type in ["TimeoutError", "ConnectionError", "TemporaryError"]:
            if RecoveryStrategy.RETRY in available_strategies:
                return RecoveryStrategy.RETRY

        # State errors -> reset or resume
        if error_type in ["StateError", "CorruptedState"]:
            if (
                RecoveryStrategy.RESUME in available_strategies
                and self._last_checkpoint
            ):
                return RecoveryStrategy.RESUME
            elif RecoveryStrategy.RESET in available_strategies:
                return RecoveryStrategy.RESET

        # Default to first available strategy
        return available_strategies[0]

    async def _execute_recovery(self, action: RecoveryAction) -> bool:
        """Execute recovery action."""
        logger.info(
            f"Executing {action.strategy.value} recovery for agent {self.agent_id}"
        )

        try:
            # Apply backoff delay
            delay = self._calculate_backoff_delay(action.retry_count)
            if delay > 0:
                await asyncio.sleep(delay)

            # Execute strategy-specific recovery
            handlers = self._recovery_callbacks.get(action.strategy, [])

            if not handlers:
                # Use default recovery implementation
                return await self._default_recovery(action)

            # Execute custom handlers
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        result = await handler(action)
                    else:
                        result = handler(action)

                    if not result:
                        return False

                except Exception as e:
                    logger.error(f"Recovery handler failed: {e}")
                    return False

            return True

        except asyncio.TimeoutError:
            logger.error(f"Recovery timeout for agent {self.agent_id}")
            return False
        except Exception as e:
            logger.error(f"Recovery failed for agent {self.agent_id}: {e}")
            return False

    async def _default_recovery(self, action: RecoveryAction) -> bool:
        """Default recovery implementation."""
        if action.strategy == RecoveryStrategy.RETRY:
            # Simple retry with backoff
            logger.info(f"Retrying operation for agent {self.agent_id}")
            await asyncio.sleep(1)  # Brief pause
            return True

        elif action.strategy == RecoveryStrategy.RESET:
            # Reset to initial state
            logger.info(f"Resetting agent {self.agent_id} to initial state")
            # This would be implemented by the agent
            return True

        elif action.strategy == RecoveryStrategy.RESUME:
            # Resume from checkpoint
            state = await self.restore_from_checkpoint()
            return state is not None

        elif action.strategy == RecoveryStrategy.RESTART:
            # Full restart
            logger.info(f"Restarting agent {self.agent_id}")
            # This would trigger a full agent restart
            return True

        elif action.strategy == RecoveryStrategy.DEGRADED:
            # Continue with reduced functionality
            logger.info(f"Agent {self.agent_id} continuing in degraded mode")
            return True

        elif action.strategy == RecoveryStrategy.FAILOVER:
            # Failover to backup
            logger.info(f"Failing over agent {self.agent_id} to backup")
            # This would be handled by the orchestration layer
            return True

        return False

    def _calculate_backoff_delay(self, retry_count: int) -> float:
        """Calculate exponential backoff delay."""
        if retry_count == 0:
            return 0

        delay = self.policy.initial_delay_seconds * (
            self.policy.backoff_multiplier ** (retry_count - 1)
        )

        return min(delay, self.policy.max_delay_seconds)

    def _get_retry_count(self, strategy: RecoveryStrategy) -> int:
        """Get retry count for strategy."""
        count = 0

        for action in reversed(self._recovery_history):
            if action.strategy == strategy:
                if action.success:
                    break
                count = action.retry_count + 1
                break

        return count

    def _cleanup_old_errors(self) -> None:
        """Remove old error timestamps outside the time window."""
        cutoff = datetime.utcnow() - timedelta(minutes=self.policy.time_window_minutes)
        self._error_timestamps = [ts for ts in self._error_timestamps if ts > cutoff]

    def _handle_recovery_success(self, action: RecoveryAction) -> None:
        """Handle successful recovery."""
        logger.info(
            f"Recovery successful for agent {self.agent_id} using {action.strategy.value}"
        )

        # Reset error count
        self._error_timestamps.clear()

        # Close circuit breaker
        self._circuit_open = False
        self._circuit_open_until = None

    def _handle_recovery_failure(self, action: RecoveryAction) -> None:
        """Handle failed recovery."""
        logger.error(
            f"Recovery failed for agent {self.agent_id} using {action.strategy.value}"
        )

        # Check if we should open circuit breaker
        recent_failures = sum(1 for a in self._recovery_history[-5:] if not a.success)

        if recent_failures >= 3:
            self._open_circuit_breaker()

    def _open_circuit_breaker(self) -> None:
        """Open circuit breaker to prevent recovery attempts."""
        self._circuit_open = True
        self._circuit_open_until = datetime.utcnow() + timedelta(
            seconds=self.policy.recovery_timeout_seconds
        )

        logger.warning(
            f"Circuit breaker opened for agent {self.agent_id} until "
            f"{self._circuit_open_until}"
        )

    def _is_circuit_open(self) -> bool:
        """Check if circuit breaker is open."""
        if not self._circuit_open:
            return False

        if self._circuit_open_until and datetime.utcnow() > self._circuit_open_until:
            # Circuit breaker timeout expired
            self._circuit_open = False
            self._circuit_open_until = None
            logger.info(f"Circuit breaker closed for agent {self.agent_id}")
            return False

        return True

    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get recovery statistics."""
        total_recoveries = len(self._recovery_history)
        successful_recoveries = sum(1 for a in self._recovery_history if a.success)

        strategy_stats = {}
        for strategy in RecoveryStrategy:
            strategy_actions = [
                a for a in self._recovery_history if a.strategy == strategy
            ]
            if strategy_actions:
                strategy_stats[strategy.value] = {
                    "attempts": len(strategy_actions),
                    "successes": sum(1 for a in strategy_actions if a.success),
                    "success_rate": sum(1 for a in strategy_actions if a.success)
                    / len(strategy_actions),
                }

        return {
            "agent_id": self.agent_id,
            "total_recoveries": total_recoveries,
            "successful_recoveries": successful_recoveries,
            "success_rate": (
                successful_recoveries / total_recoveries if total_recoveries > 0 else 0
            ),
            "circuit_breaker_open": self._circuit_open,
            "error_count": len(self._error_timestamps),
            "strategy_stats": strategy_stats,
            "last_checkpoint": (
                self._last_checkpoint.checkpoint_id if self._last_checkpoint else None
            ),
        }
