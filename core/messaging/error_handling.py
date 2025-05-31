"""
Error handling and dead letter queue management for AIOSv3 message queue.

Provides comprehensive error handling, retry logic, and dead letter queue
processing for failed messages.
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from core.messaging.queue import AgentMessage, MessageHandler, MessageQueue

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Types of errors that can occur in message processing."""

    VALIDATION_ERROR = "validation_error"
    TIMEOUT_ERROR = "timeout_error"
    PROCESSING_ERROR = "processing_error"
    NETWORK_ERROR = "network_error"
    AUTHENTICATION_ERROR = "authentication_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    RESOURCE_ERROR = "resource_error"
    UNKNOWN_ERROR = "unknown_error"


class RetryStrategy(Enum):
    """Retry strategies for failed messages."""

    NONE = "none"  # No retry
    IMMEDIATE = "immediate"  # Retry immediately
    LINEAR = "linear"  # Linear backoff
    EXPONENTIAL = "exponential"  # Exponential backoff
    CUSTOM = "custom"  # Custom retry logic


@dataclass
class ErrorInfo:
    """Information about an error that occurred during message processing."""

    error_type: ErrorType
    error_message: str
    timestamp: datetime
    agent_id: str
    original_message: AgentMessage
    retry_count: int = 0
    max_retries: int = 3
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    stack_trace: str | None = None


@dataclass
class RetryPolicy:
    """Configuration for retry behavior."""

    max_retries: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    initial_delay: float = 1.0  # seconds
    max_delay: float = 300.0  # 5 minutes
    backoff_factor: float = 2.0
    jitter: bool = True
    retry_on: list[ErrorType] | None = None  # None means retry on all errors
    no_retry_on: list[ErrorType] | None = None


class ErrorHandler:
    """
    Handles errors and implements retry logic for message processing.
    """

    def __init__(
        self,
        message_queue: MessageQueue,
        default_retry_policy: RetryPolicy | None = None,
    ):
        """Initialize error handler."""
        self.message_queue = message_queue
        self.default_retry_policy = default_retry_policy or RetryPolicy()
        self.error_callbacks: dict[ErrorType, list[Callable]] = {}
        self.custom_retry_handlers: dict[str, Callable] = {}

    async def handle_error(
        self,
        error: Exception,
        message: AgentMessage,
        agent_id: str,
        retry_policy: RetryPolicy | None = None,
    ) -> bool:
        """
        Handle an error that occurred during message processing.

        Args:
            error: The exception that occurred
            message: The message being processed when error occurred
            agent_id: ID of the agent that encountered the error
            retry_policy: Custom retry policy (uses default if None)

        Returns:
            bool: True if message should be retried, False if sent to DLQ
        """
        policy = retry_policy or self.default_retry_policy
        error_type = self._classify_error(error)

        # Create error info
        error_info = ErrorInfo(
            error_type=error_type,
            error_message=str(error),
            timestamp=datetime.utcnow(),
            agent_id=agent_id,
            original_message=message,
            retry_count=self._get_retry_count(message),
            max_retries=policy.max_retries,
            retry_strategy=policy.strategy,
            stack_trace=self._get_stack_trace(error),
        )

        logger.error(
            f"Error processing message {message.envelope.get('id', 'unknown')}: "
            f"{error_type.value} - {error}"
        )

        # Check if we should retry
        should_retry = self._should_retry(error_info, policy)

        if should_retry:
            await self._schedule_retry(error_info, policy)
            return True
        else:
            await self._send_to_dlq(error_info)
            return False

    def _classify_error(self, error: Exception) -> ErrorType:
        """Classify an error based on its type and message."""
        error_str = str(error).lower()

        if isinstance(error, asyncio.TimeoutError):
            return ErrorType.TIMEOUT_ERROR
        elif isinstance(error, ValueError) or "validation" in error_str:
            return ErrorType.VALIDATION_ERROR
        elif "network" in error_str or "connection" in error_str:
            return ErrorType.NETWORK_ERROR
        elif "auth" in error_str or "permission" in error_str:
            return ErrorType.AUTHENTICATION_ERROR
        elif "rate limit" in error_str or "throttl" in error_str:
            return ErrorType.RATE_LIMIT_ERROR
        elif "memory" in error_str or "resource" in error_str:
            return ErrorType.RESOURCE_ERROR
        else:
            return ErrorType.UNKNOWN_ERROR

    def _get_retry_count(self, message: AgentMessage) -> int:
        """Get the current retry count from message metadata."""
        return message.metadata.get("retry_count", 0)

    def _get_stack_trace(self, error: Exception) -> str:
        """Get stack trace from exception."""
        import traceback

        return traceback.format_exc()

    def _should_retry(self, error_info: ErrorInfo, policy: RetryPolicy) -> bool:
        """Determine if a message should be retried."""
        # Check if we've exceeded max retries
        if error_info.retry_count >= policy.max_retries:
            return False

        # Check if error type is in no-retry list
        if policy.no_retry_on and error_info.error_type in policy.no_retry_on:
            return False

        # Check if error type is in retry list (if specified)
        if policy.retry_on and error_info.error_type not in policy.retry_on:
            return False

        # Some errors should never be retried
        never_retry = [ErrorType.VALIDATION_ERROR, ErrorType.AUTHENTICATION_ERROR]

        if error_info.error_type in never_retry:
            return False

        return True

    async def _schedule_retry(self, error_info: ErrorInfo, policy: RetryPolicy) -> None:
        """Schedule a message for retry."""
        delay = self._calculate_retry_delay(error_info, policy)

        logger.info(
            f"Scheduling retry {error_info.retry_count + 1}/{policy.max_retries} "
            f"for message {error_info.original_message.envelope.get('id', 'unknown')} "
            f"in {delay:.2f} seconds"
        )

        # Update message metadata
        retry_message = error_info.original_message.model_copy(deep=True)
        retry_message.metadata["retry_count"] = error_info.retry_count + 1
        retry_message.metadata["retry_delay"] = delay
        retry_message.metadata["error_history"] = retry_message.metadata.get(
            "error_history", []
        )
        retry_message.metadata["error_history"].append(
            {
                "error_type": error_info.error_type.value,
                "error_message": error_info.error_message,
                "timestamp": error_info.timestamp.isoformat(),
                "retry_count": error_info.retry_count,
            }
        )

        # Schedule retry
        asyncio.create_task(self._delayed_retry(retry_message, delay))

    def _calculate_retry_delay(
        self, error_info: ErrorInfo, policy: RetryPolicy
    ) -> float:
        """Calculate delay before retry based on strategy."""
        if policy.strategy == RetryStrategy.NONE:
            return 0.0
        elif policy.strategy == RetryStrategy.IMMEDIATE:
            return 0.0
        elif policy.strategy == RetryStrategy.LINEAR:
            delay = policy.initial_delay * (error_info.retry_count + 1)
        elif policy.strategy == RetryStrategy.EXPONENTIAL:
            delay = policy.initial_delay * (
                policy.backoff_factor**error_info.retry_count
            )
        elif policy.strategy == RetryStrategy.CUSTOM:
            # Use custom handler if available
            handler_name = f"{error_info.agent_id}_{error_info.error_type.value}"
            if handler_name in self.custom_retry_handlers:
                return self.custom_retry_handlers[handler_name](error_info, policy)
            else:
                # Fallback to exponential
                delay = policy.initial_delay * (
                    policy.backoff_factor**error_info.retry_count
                )
        else:
            delay = policy.initial_delay

        # Apply jitter if enabled
        if policy.jitter:
            import random

            jitter_factor = random.uniform(0.8, 1.2)
            delay *= jitter_factor

        # Ensure delay is within bounds
        return min(max(delay, 0.0), policy.max_delay)

    async def _delayed_retry(self, message: AgentMessage, delay: float) -> None:
        """Execute a delayed retry of a message."""
        if delay > 0:
            await asyncio.sleep(delay)

        # Republish the message
        envelope = message.envelope
        await self.message_queue.publish(
            routing_key=message.metadata.get("routing_key", "retry.default"),
            payload=message.payload,
            sender_id=envelope.get("sender_id", "error_handler"),
            recipient_id=envelope.get("recipient_id", "*"),
            message_type=envelope.get("message_type", "retry"),
            priority=envelope.get("priority", 5),
        )

    async def _send_to_dlq(self, error_info: ErrorInfo) -> None:
        """Send a failed message to the dead letter queue."""
        dlq_message = {
            "original_message": error_info.original_message.model_dump(),
            "error_info": {
                "error_type": error_info.error_type.value,
                "error_message": error_info.error_message,
                "timestamp": error_info.timestamp.isoformat(),
                "agent_id": error_info.agent_id,
                "retry_count": error_info.retry_count,
                "max_retries": error_info.max_retries,
                "stack_trace": error_info.stack_trace,
            },
            "dlq_timestamp": datetime.utcnow().isoformat(),
        }

        await self.message_queue.publish(
            routing_key=f"failed.{error_info.agent_id}",
            payload=dlq_message,
            sender_id="error_handler",
            recipient_id="dlq_processor",
            message_type="dlq_entry",
            priority=1,
        )

        logger.warning(
            f"Sent message {error_info.original_message.envelope.get('id', 'unknown')} "
            f"to DLQ after {error_info.retry_count} retries"
        )

    def register_error_callback(
        self, error_type: ErrorType, callback: Callable[[ErrorInfo], None]
    ) -> None:
        """Register a callback for specific error types."""
        if error_type not in self.error_callbacks:
            self.error_callbacks[error_type] = []
        self.error_callbacks[error_type].append(callback)

    def register_custom_retry_handler(
        self, handler_name: str, handler: Callable[[ErrorInfo, RetryPolicy], float]
    ) -> None:
        """Register a custom retry delay calculation handler."""
        self.custom_retry_handlers[handler_name] = handler


class DeadLetterQueueProcessor:
    """
    Processes messages from the dead letter queue.

    Provides functionality to:
    - Monitor DLQ for failed messages
    - Analyze failure patterns
    - Retry messages manually
    - Generate error reports
    """

    def __init__(self, message_queue: MessageQueue):
        """Initialize DLQ processor."""
        self.message_queue = message_queue
        self.dlq_messages: list[dict[str, Any]] = []
        self.processing_stats = {
            "total_processed": 0,
            "retry_attempts": 0,
            "permanent_failures": 0,
            "error_types": {},
        }

    async def start_monitoring(self, agent_id: str = "dlq_processor") -> None:
        """Start monitoring the dead letter queue."""
        logger.info("Starting DLQ monitoring")

        dlq_handler = DLQMessageHandler(self)

        await self.message_queue.register_handler(
            agent_id=agent_id,
            handler=dlq_handler,
            routing_keys=["failed.*", "dlx.*"],
            queue_name="dlq.processor",
        )

    async def process_dlq_message(self, dlq_entry: dict[str, Any]) -> None:
        """Process a message from the DLQ."""
        self.dlq_messages.append(dlq_entry)
        self.processing_stats["total_processed"] += 1

        error_info = dlq_entry.get("error_info", {})
        error_type = error_info.get("error_type", "unknown")

        # Update error type statistics
        if error_type not in self.processing_stats["error_types"]:
            self.processing_stats["error_types"][error_type] = 0
        self.processing_stats["error_types"][error_type] += 1

        logger.info(f"Processed DLQ message with error type: {error_type}")

    async def retry_dlq_message(self, message_index: int) -> bool:
        """Manually retry a message from the DLQ."""
        if message_index >= len(self.dlq_messages):
            logger.error(f"Invalid message index: {message_index}")
            return False

        dlq_entry = self.dlq_messages[message_index]
        original_message = dlq_entry["original_message"]

        try:
            # Recreate the original message
            message = AgentMessage.model_validate(original_message)

            # Clear retry metadata
            message.metadata["retry_count"] = 0
            message.metadata.pop("error_history", None)

            # Republish the message
            envelope = message.envelope
            await self.message_queue.publish(
                routing_key=message.metadata.get("routing_key", "retry.manual"),
                payload=message.payload,
                sender_id=envelope.get("sender_id", "dlq_processor"),
                recipient_id=envelope.get("recipient_id", "*"),
                message_type=envelope.get("message_type", "retry"),
                priority=envelope.get("priority", 5),
            )

            self.processing_stats["retry_attempts"] += 1
            logger.info(f"Successfully retried DLQ message {message_index}")
            return True

        except Exception as e:
            logger.error(f"Failed to retry DLQ message {message_index}: {e}")
            return False

    def get_error_report(self) -> dict[str, Any]:
        """Generate an error report from DLQ analysis."""
        recent_messages = [
            msg
            for msg in self.dlq_messages
            if datetime.fromisoformat(msg["dlq_timestamp"])
            > datetime.utcnow() - timedelta(hours=24)
        ]

        return {
            "total_dlq_messages": len(self.dlq_messages),
            "recent_24h": len(recent_messages),
            "processing_stats": self.processing_stats,
            "top_errors": sorted(
                self.processing_stats["error_types"].items(),
                key=lambda x: x[1],
                reverse=True,
            )[:5],
            "report_timestamp": datetime.utcnow().isoformat(),
        }

    def clear_old_messages(self, days: int = 7) -> int:
        """Clear DLQ messages older than specified days."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        initial_count = len(self.dlq_messages)
        self.dlq_messages = [
            msg
            for msg in self.dlq_messages
            if datetime.fromisoformat(msg["dlq_timestamp"]) > cutoff
        ]

        removed = initial_count - len(self.dlq_messages)
        logger.info(f"Cleared {removed} old DLQ messages")
        return removed


class DLQMessageHandler(MessageHandler):
    """Message handler for DLQ processor."""

    def __init__(self, dlq_processor: DeadLetterQueueProcessor):
        self.dlq_processor = dlq_processor

    async def handle_message(self, message: AgentMessage) -> AgentMessage | None:
        """Handle messages sent to the DLQ."""
        if message.envelope.get("message_type") == "dlq_entry":
            await self.dlq_processor.process_dlq_message(message.payload)

        # DLQ handler doesn't send responses
        return None


# Global error handler instance
error_handler: ErrorHandler | None = None
dlq_processor: DeadLetterQueueProcessor | None = None


def initialize_error_handling(message_queue: MessageQueue) -> None:
    """Initialize global error handling components."""
    global error_handler, dlq_processor

    error_handler = ErrorHandler(message_queue)
    dlq_processor = DeadLetterQueueProcessor(message_queue)

    logger.info("Error handling system initialized")
