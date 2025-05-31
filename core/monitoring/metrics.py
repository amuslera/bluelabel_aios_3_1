"""
Metrics collection and Prometheus integration for AIOSv3.

Provides comprehensive metrics for agent operations, message queue,
object storage, and system performance.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum

from fastapi import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics we collect."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    INFO = "info"


class AIOSv3Metrics:
    """
    Centralized metrics collection for AIOSv3 platform.

    Provides metrics for:
    - Agent operations and performance
    - Message queue throughput and latency
    - Object storage operations
    - Workspace management
    - System health and resources
    """

    def __init__(self):
        """Initialize metrics collectors."""
        self._setup_metrics()
        self.start_time = time.time()

    def _setup_metrics(self):
        """Set up all Prometheus metrics."""

        # System metrics
        self.system_info = Info("aiosv3_system_info", "System information")

        self.uptime_seconds = Gauge("aiosv3_uptime_seconds", "System uptime in seconds")

        # Agent metrics
        self.agents_active = Gauge(
            "aiosv3_agents_active_total", "Number of active agents"
        )

        self.agent_operations_total = Counter(
            "aiosv3_agent_operations_total",
            "Total agent operations",
            ["agent_id", "operation_type", "status"],
        )

        self.agent_operation_duration = Histogram(
            "aiosv3_agent_operation_duration_seconds",
            "Agent operation duration",
            ["agent_id", "operation_type"],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
        )

        # Message queue metrics
        self.messages_published_total = Counter(
            "aiosv3_messages_published_total",
            "Total messages published",
            ["queue", "sender_agent", "message_type"],
        )

        self.messages_consumed_total = Counter(
            "aiosv3_messages_consumed_total",
            "Total messages consumed",
            ["queue", "receiver_agent", "message_type", "status"],
        )

        self.message_processing_duration = Histogram(
            "aiosv3_message_processing_duration_seconds",
            "Message processing duration",
            ["queue", "message_type"],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0],
        )

        self.queue_depth = Gauge(
            "aiosv3_queue_depth", "Number of messages in queue", ["queue"]
        )

        # Dead letter queue metrics
        self.dlq_messages_total = Counter(
            "aiosv3_dlq_messages_total",
            "Total messages sent to DLQ",
            ["queue", "error_type"],
        )

        self.dlq_retries_total = Counter(
            "aiosv3_dlq_retries_total",
            "Total DLQ message retries",
            ["queue", "retry_result"],
        )

        # Object storage metrics
        self.storage_operations_total = Counter(
            "aiosv3_storage_operations_total",
            "Total storage operations",
            ["bucket", "operation", "status"],
        )

        self.storage_operation_duration = Histogram(
            "aiosv3_storage_operation_duration_seconds",
            "Storage operation duration",
            ["bucket", "operation"],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
        )

        self.storage_bytes_transferred = Counter(
            "aiosv3_storage_bytes_transferred_total",
            "Total bytes transferred",
            ["bucket", "operation"],
        )

        self.storage_objects_total = Gauge(
            "aiosv3_storage_objects_total", "Total objects in storage", ["bucket"]
        )

        self.storage_size_bytes = Gauge(
            "aiosv3_storage_size_bytes", "Total storage size in bytes", ["bucket"]
        )

        # Workspace metrics
        self.workspaces_active = Gauge(
            "aiosv3_workspaces_active_total", "Number of active workspaces"
        )

        self.workspace_operations_total = Counter(
            "aiosv3_workspace_operations_total",
            "Total workspace operations",
            ["workspace_id", "operation", "agent_id", "status"],
        )

        self.workspace_files_total = Gauge(
            "aiosv3_workspace_files_total", "Total files in workspace", ["workspace_id"]
        )

        self.workspace_conflicts_total = Counter(
            "aiosv3_workspace_conflicts_total",
            "Total workspace file conflicts",
            ["workspace_id", "resolution_strategy"],
        )

        # Version management metrics
        self.versions_created_total = Counter(
            "aiosv3_versions_created_total",
            "Total versions created",
            ["bucket", "object_prefix"],
        )

        self.versions_cleaned_total = Counter(
            "aiosv3_versions_cleaned_total",
            "Total versions cleaned up",
            ["bucket", "cleanup_policy"],
        )

        self.backup_operations_total = Counter(
            "aiosv3_backup_operations_total",
            "Total backup operations",
            ["bucket", "backup_type", "status"],
        )

        # Error metrics
        self.errors_total = Counter(
            "aiosv3_errors_total",
            "Total errors by component",
            ["component", "error_type"],
        )

        # Health check metrics
        self.health_check_duration = Histogram(
            "aiosv3_health_check_duration_seconds",
            "Health check duration",
            ["component"],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0],
        )

        self.component_health = Gauge(
            "aiosv3_component_health",
            "Component health status (1=healthy, 0=unhealthy)",
            ["component"],
        )

        logger.info("Metrics collectors initialized")

    def set_system_info(self, **info: str):
        """Set system information."""
        self.system_info.info(info)

    def update_uptime(self):
        """Update system uptime."""
        uptime = time.time() - self.start_time
        self.uptime_seconds.set(uptime)

    def track_agent_operation(
        self,
        agent_id: str,
        operation_type: str,
        status: str = "success",
        duration: float | None = None,
    ):
        """Track an agent operation."""
        self.agent_operations_total.labels(
            agent_id=agent_id, operation_type=operation_type, status=status
        ).inc()

        if duration is not None:
            self.agent_operation_duration.labels(
                agent_id=agent_id, operation_type=operation_type
            ).observe(duration)

    def set_active_agents(self, count: int):
        """Set the number of active agents."""
        self.agents_active.set(count)

    def track_message_published(self, queue: str, sender_agent: str, message_type: str):
        """Track a published message."""
        self.messages_published_total.labels(
            queue=queue, sender_agent=sender_agent, message_type=message_type
        ).inc()

    def track_message_consumed(
        self,
        queue: str,
        receiver_agent: str,
        message_type: str,
        status: str = "success",
        processing_duration: float | None = None,
    ):
        """Track a consumed message."""
        self.messages_consumed_total.labels(
            queue=queue,
            receiver_agent=receiver_agent,
            message_type=message_type,
            status=status,
        ).inc()

        if processing_duration is not None:
            self.message_processing_duration.labels(
                queue=queue, message_type=message_type
            ).observe(processing_duration)

    def set_queue_depth(self, queue: str, depth: int):
        """Set queue depth."""
        self.queue_depth.labels(queue=queue).set(depth)

    def track_dlq_message(self, queue: str, error_type: str):
        """Track a message sent to DLQ."""
        self.dlq_messages_total.labels(queue=queue, error_type=error_type).inc()

    def track_dlq_retry(self, queue: str, result: str):
        """Track a DLQ retry attempt."""
        self.dlq_retries_total.labels(queue=queue, retry_result=result).inc()

    def track_storage_operation(
        self,
        bucket: str,
        operation: str,
        status: str = "success",
        duration: float | None = None,
        bytes_transferred: int | None = None,
    ):
        """Track a storage operation."""
        self.storage_operations_total.labels(
            bucket=bucket, operation=operation, status=status
        ).inc()

        if duration is not None:
            self.storage_operation_duration.labels(
                bucket=bucket, operation=operation
            ).observe(duration)

        if bytes_transferred is not None:
            self.storage_bytes_transferred.labels(
                bucket=bucket, operation=operation
            ).inc(bytes_transferred)

    def set_storage_stats(self, bucket: str, object_count: int, size_bytes: int):
        """Set storage statistics."""
        self.storage_objects_total.labels(bucket=bucket).set(object_count)
        self.storage_size_bytes.labels(bucket=bucket).set(size_bytes)

    def set_active_workspaces(self, count: int):
        """Set the number of active workspaces."""
        self.workspaces_active.set(count)

    def track_workspace_operation(
        self, workspace_id: str, operation: str, agent_id: str, status: str = "success"
    ):
        """Track a workspace operation."""
        self.workspace_operations_total.labels(
            workspace_id=workspace_id,
            operation=operation,
            agent_id=agent_id,
            status=status,
        ).inc()

    def set_workspace_files(self, workspace_id: str, file_count: int):
        """Set workspace file count."""
        self.workspace_files_total.labels(workspace_id=workspace_id).set(file_count)

    def track_workspace_conflict(self, workspace_id: str, resolution_strategy: str):
        """Track a workspace conflict."""
        self.workspace_conflicts_total.labels(
            workspace_id=workspace_id, resolution_strategy=resolution_strategy
        ).inc()

    def track_version_created(self, bucket: str, object_prefix: str):
        """Track version creation."""
        self.versions_created_total.labels(
            bucket=bucket, object_prefix=object_prefix
        ).inc()

    def track_version_cleanup(self, bucket: str, cleanup_policy: str, count: int = 1):
        """Track version cleanup."""
        self.versions_cleaned_total.labels(
            bucket=bucket, cleanup_policy=cleanup_policy
        ).inc(count)

    def track_backup_operation(self, bucket: str, backup_type: str, status: str):
        """Track backup operation."""
        self.backup_operations_total.labels(
            bucket=bucket, backup_type=backup_type, status=status
        ).inc()

    def track_error(self, component: str, error_type: str):
        """Track an error."""
        self.errors_total.labels(component=component, error_type=error_type).inc()

    def track_health_check(self, component: str, duration: float, healthy: bool):
        """Track a health check."""
        self.health_check_duration.labels(component=component).observe(duration)
        self.component_health.labels(component=component).set(1 if healthy else 0)

    @asynccontextmanager
    async def track_operation(
        self,
        operation_type: str,
        agent_id: str | None = None,
        component: str | None = None,
    ):
        """Context manager to track operation duration."""
        start_time = time.time()
        try:
            yield
            duration = time.time() - start_time

            if agent_id:
                self.track_agent_operation(
                    agent_id, operation_type, "success", duration
                )
            elif component:
                # Could add component-specific tracking here
                pass

        except Exception as e:
            duration = time.time() - start_time

            if agent_id:
                self.track_agent_operation(agent_id, operation_type, "error", duration)

            if component:
                self.track_error(component, type(e).__name__)

            raise

    def get_metrics(self) -> str:
        """Get metrics in Prometheus format."""
        self.update_uptime()
        return generate_latest().decode("utf-8")


# Global metrics instance
metrics: AIOSv3Metrics | None = None


def get_metrics() -> AIOSv3Metrics:
    """Get the global metrics instance."""
    global metrics
    if metrics is None:
        metrics = AIOSv3Metrics()
    return metrics


def initialize_metrics(**system_info: str) -> AIOSv3Metrics:
    """Initialize global metrics instance."""
    global metrics
    metrics = AIOSv3Metrics()

    # Set system information
    default_info = {
        "version": "0.1.0",
        "component": "aiosv3",
        "started_at": datetime.utcnow().isoformat(),
    }
    default_info.update(system_info)
    metrics.set_system_info(**default_info)

    return metrics


# FastAPI metrics endpoint
async def metrics_endpoint() -> Response:
    """Metrics endpoint for Prometheus scraping."""
    metrics_data = get_metrics().get_metrics()
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)


# Health check integration
async def collect_system_metrics():
    """Collect system-wide metrics."""
    metrics_instance = get_metrics()

    try:
        # Update system metrics
        metrics_instance.update_uptime()

        # This would collect actual system metrics
        # For now, we'll set some example values
        metrics_instance.set_active_agents(0)  # Would get from agent registry
        metrics_instance.set_active_workspaces(0)  # Would get from workspace manager

        logger.debug("System metrics collected")

    except Exception as e:
        logger.error(f"Failed to collect system metrics: {e}")
        metrics_instance.track_error("metrics_collector", type(e).__name__)


# Metrics collection scheduler
async def start_metrics_collection(interval: float = 30.0):
    """Start periodic metrics collection."""
    while True:
        try:
            await collect_system_metrics()
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Metrics collection error: {e}")
            await asyncio.sleep(interval)
