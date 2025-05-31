"""
Health monitoring system for AIOSv3 agents.

Provides comprehensive health checks, metrics collection, and monitoring
integration for agent lifecycle management.
"""

import asyncio
import logging
import psutil
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class HealthMetric(BaseModel):
    """Individual health metric."""

    name: str
    value: Any
    status: HealthStatus
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    unit: Optional[str] = None
    message: Optional[str] = None


class HealthCheck(BaseModel):
    """Health check definition."""

    name: str
    check_func: str  # Name of the function (stored as string for serialization)
    interval_seconds: int = 30
    timeout_seconds: int = 10
    critical: bool = False  # If True, failure affects overall health
    enabled: bool = True
    retry_count: int = 3
    last_run: Optional[datetime] = None
    last_result: Optional[HealthStatus] = None


class ComponentHealth(BaseModel):
    """Health status of a component."""

    component_name: str
    status: HealthStatus
    checks: Dict[str, HealthMetric]
    last_update: datetime = Field(default_factory=datetime.utcnow)
    message: Optional[str] = None


class AgentHealthReport(BaseModel):
    """Complete health report for an agent."""

    agent_id: str
    overall_status: HealthStatus
    components: Dict[str, ComponentHealth]
    metrics: Dict[str, HealthMetric]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    uptime_seconds: float
    error_count: int = 0
    warning_count: int = 0


class HealthMonitor:
    """
    Monitors agent health and collects metrics.

    Provides configurable health checks, metric collection,
    and integration with monitoring systems.
    """

    def __init__(self, agent_id: str):
        """Initialize health monitor."""
        self.agent_id = agent_id
        self._health_checks: Dict[str, HealthCheck] = {}
        self._check_functions: Dict[str, Callable] = {}
        self._metrics: Dict[str, HealthMetric] = {}
        self._component_status: Dict[str, ComponentHealth] = {}

        # Monitoring state
        self._monitoring_active = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._start_time = datetime.utcnow()

        # Error tracking
        self._error_count = 0
        self._warning_count = 0
        self._consecutive_failures: Dict[str, int] = {}

        # Resource monitoring
        self._process = psutil.Process()
        self._cpu_percent_history: List[float] = []
        self._memory_history: List[float] = []

        # Register default health checks
        self._register_default_checks()

    def _register_default_checks(self) -> None:
        """Register default health checks."""
        # CPU usage check
        self.register_check(
            "cpu_usage", self._check_cpu_usage, interval_seconds=10, critical=True
        )

        # Memory usage check
        self.register_check(
            "memory_usage", self._check_memory_usage, interval_seconds=10, critical=True
        )

        # Response time check
        self.register_check(
            "response_time",
            self._check_response_time,
            interval_seconds=30,
            critical=False,
        )

    def register_check(
        self,
        name: str,
        check_func: Callable,
        interval_seconds: int = 30,
        timeout_seconds: int = 10,
        critical: bool = False,
        enabled: bool = True,
    ) -> None:
        """Register a health check."""
        self._health_checks[name] = HealthCheck(
            name=name,
            check_func=name,  # Store function name
            interval_seconds=interval_seconds,
            timeout_seconds=timeout_seconds,
            critical=critical,
            enabled=enabled,
        )
        self._check_functions[name] = check_func

    def register_component(self, component_name: str) -> None:
        """Register a component for health tracking."""
        self._component_status[component_name] = ComponentHealth(
            component_name=component_name, status=HealthStatus.UNKNOWN, checks={}
        )

    async def start_monitoring(self) -> None:
        """Start health monitoring."""
        if self._monitoring_active:
            return

        self._monitoring_active = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info(f"Started health monitoring for agent {self.agent_id}")

    async def stop_monitoring(self) -> None:
        """Stop health monitoring."""
        self._monitoring_active = False

        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

        logger.info(f"Stopped health monitoring for agent {self.agent_id}")

    async def get_health_report(self) -> AgentHealthReport:
        """Get current health report."""
        # Calculate overall status
        overall_status = self._calculate_overall_status()

        # Calculate uptime
        uptime = (datetime.utcnow() - self._start_time).total_seconds()

        return AgentHealthReport(
            agent_id=self.agent_id,
            overall_status=overall_status,
            components=self._component_status.copy(),
            metrics=self._metrics.copy(),
            uptime_seconds=uptime,
            error_count=self._error_count,
            warning_count=self._warning_count,
        )

    async def check_health(
        self, check_name: Optional[str] = None
    ) -> Dict[str, HealthMetric]:
        """Run health checks and return results."""
        if check_name:
            # Run specific check
            if (
                check_name in self._health_checks
                and check_name in self._check_functions
            ):
                check = self._health_checks[check_name]
                if check.enabled:
                    result = await self._run_check(check_name)
                    return {check_name: result} if result else {}
            return {}

        # Run all enabled checks
        results = {}
        for name, check in self._health_checks.items():
            if check.enabled:
                result = await self._run_check(name)
                if result:
                    results[name] = result

        return results

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        try:
            while self._monitoring_active:
                # Group checks by interval
                checks_to_run = []
                current_time = datetime.utcnow()

                for name, check in self._health_checks.items():
                    if not check.enabled:
                        continue

                    # Check if it's time to run this check
                    if (
                        check.last_run is None
                        or (current_time - check.last_run).total_seconds()
                        >= check.interval_seconds
                    ):
                        checks_to_run.append(name)

                # Run checks concurrently
                if checks_to_run:
                    await asyncio.gather(
                        *[self._run_check(name) for name in checks_to_run],
                        return_exceptions=True,
                    )

                # Update component status
                self._update_component_status()

                # Sleep briefly before next iteration
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info(f"Monitoring loop cancelled for agent {self.agent_id}")
            raise
        except Exception as e:
            logger.error(f"Error in monitoring loop for agent {self.agent_id}: {e}")
            self._error_count += 1

    async def _run_check(self, check_name: str) -> Optional[HealthMetric]:
        """Run a single health check."""
        check = self._health_checks.get(check_name)
        check_func = self._check_functions.get(check_name)

        if not check or not check_func:
            return None

        try:
            # Run check with timeout
            if asyncio.iscoroutinefunction(check_func):
                result = await asyncio.wait_for(
                    check_func(), timeout=check.timeout_seconds
                )
            else:
                result = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, check_func),
                    timeout=check.timeout_seconds,
                )

            # Update check info
            check.last_run = datetime.utcnow()
            check.last_result = (
                result.status
                if isinstance(result, HealthMetric)
                else HealthStatus.HEALTHY
            )

            # Reset consecutive failures on success
            if check.last_result in {HealthStatus.HEALTHY, HealthStatus.DEGRADED}:
                self._consecutive_failures[check_name] = 0

            # Store metric
            if isinstance(result, HealthMetric):
                self._metrics[check_name] = result
                return result

            # Create default metric if check returned boolean
            status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
            metric = HealthMetric(name=check_name, value=result, status=status)
            self._metrics[check_name] = metric
            return metric

        except asyncio.TimeoutError:
            logger.warning(f"Health check {check_name} timed out")
            self._handle_check_failure(check_name, "Timeout")
            return None

        except Exception as e:
            logger.error(f"Health check {check_name} failed: {e}")
            self._handle_check_failure(check_name, str(e))
            return None

    def _handle_check_failure(self, check_name: str, error: str) -> None:
        """Handle health check failure."""
        # Increment consecutive failures
        self._consecutive_failures[check_name] = (
            self._consecutive_failures.get(check_name, 0) + 1
        )

        # Create failure metric
        self._metrics[check_name] = HealthMetric(
            name=check_name,
            value=None,
            status=HealthStatus.CRITICAL,
            message=f"Check failed: {error}",
        )

        # Update check status
        if check_name in self._health_checks:
            self._health_checks[check_name].last_result = HealthStatus.CRITICAL

        # Increment error count
        self._error_count += 1

    async def _check_cpu_usage(self) -> HealthMetric:
        """Check CPU usage."""
        cpu_percent = self._process.cpu_percent(interval=0.1)

        # Track history
        self._cpu_percent_history.append(cpu_percent)
        if len(self._cpu_percent_history) > 60:  # Keep last 60 samples
            self._cpu_percent_history.pop(0)

        # Determine status
        if cpu_percent > 90:
            status = HealthStatus.CRITICAL
        elif cpu_percent > 75:
            status = HealthStatus.UNHEALTHY
        elif cpu_percent > 60:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.HEALTHY

        return HealthMetric(
            name="cpu_usage",
            value=cpu_percent,
            status=status,
            threshold_max=75.0,
            unit="percent",
            message=f"CPU usage: {cpu_percent:.1f}%",
        )

    async def _check_memory_usage(self) -> HealthMetric:
        """Check memory usage."""
        memory_info = self._process.memory_info()
        memory_percent = self._process.memory_percent()
        memory_mb = memory_info.rss / 1024 / 1024

        # Track history
        self._memory_history.append(memory_mb)
        if len(self._memory_history) > 60:
            self._memory_history.pop(0)

        # Determine status
        if memory_percent > 90:
            status = HealthStatus.CRITICAL
        elif memory_percent > 75:
            status = HealthStatus.UNHEALTHY
        elif memory_percent > 60:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.HEALTHY

        return HealthMetric(
            name="memory_usage",
            value=memory_mb,
            status=status,
            threshold_max=1024.0,  # 1GB default threshold
            unit="MB",
            message=f"Memory usage: {memory_mb:.1f}MB ({memory_percent:.1f}%)",
        )

    async def _check_response_time(self) -> HealthMetric:
        """Check agent response time."""
        # This would be implemented based on actual agent operations
        # For now, return a mock healthy status
        return HealthMetric(
            name="response_time",
            value=50.0,
            status=HealthStatus.HEALTHY,
            threshold_max=1000.0,
            unit="ms",
            message="Response time within normal range",
        )

    def _calculate_overall_status(self) -> HealthStatus:
        """Calculate overall health status."""
        if not self._metrics:
            return HealthStatus.UNKNOWN

        # Check critical checks first
        critical_statuses = []
        non_critical_statuses = []

        for check_name, metric in self._metrics.items():
            check = self._health_checks.get(check_name)
            if check and check.critical:
                critical_statuses.append(metric.status)
            else:
                non_critical_statuses.append(metric.status)

        # If any critical check is CRITICAL, overall is CRITICAL
        if HealthStatus.CRITICAL in critical_statuses:
            return HealthStatus.CRITICAL

        # If any critical check is UNHEALTHY, overall is UNHEALTHY
        if HealthStatus.UNHEALTHY in critical_statuses:
            return HealthStatus.UNHEALTHY

        # If multiple non-critical are unhealthy, overall is DEGRADED
        unhealthy_count = sum(
            1 for s in non_critical_statuses if s == HealthStatus.UNHEALTHY
        )
        if unhealthy_count >= 2:
            return HealthStatus.DEGRADED

        # If any check is DEGRADED, overall is DEGRADED
        if HealthStatus.DEGRADED in (critical_statuses + non_critical_statuses):
            return HealthStatus.DEGRADED

        return HealthStatus.HEALTHY

    def _update_component_status(self) -> None:
        """Update component health status."""
        for component_name, component in self._component_status.items():
            # Get checks related to this component
            component_checks = {
                name: metric
                for name, metric in self._metrics.items()
                if name.startswith(f"{component_name}_")
            }

            if component_checks:
                # Calculate component status
                statuses = [check.status for check in component_checks.values()]

                if HealthStatus.CRITICAL in statuses:
                    component.status = HealthStatus.CRITICAL
                elif HealthStatus.UNHEALTHY in statuses:
                    component.status = HealthStatus.UNHEALTHY
                elif HealthStatus.DEGRADED in statuses:
                    component.status = HealthStatus.DEGRADED
                else:
                    component.status = HealthStatus.HEALTHY

                component.checks = component_checks
                component.last_update = datetime.utcnow()

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics."""
        return {
            "agent_id": self.agent_id,
            "uptime_seconds": (datetime.utcnow() - self._start_time).total_seconds(),
            "error_count": self._error_count,
            "warning_count": self._warning_count,
            "cpu_avg": (
                sum(self._cpu_percent_history) / len(self._cpu_percent_history)
                if self._cpu_percent_history
                else 0
            ),
            "memory_avg_mb": (
                sum(self._memory_history) / len(self._memory_history)
                if self._memory_history
                else 0
            ),
            "health_checks": len(self._health_checks),
            "failed_checks": sum(
                1 for m in self._metrics.values() if m.status == HealthStatus.CRITICAL
            ),
            "last_update": datetime.utcnow().isoformat(),
        }

    async def export_metrics(self, format: str = "prometheus") -> str:
        """Export metrics in specified format."""
        if format == "prometheus":
            return self._export_prometheus()
        elif format == "json":
            import json

            report = await self.get_health_report()
            return json.dumps(report.model_dump(), default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []

        # Add metric headers and values
        for name, metric in self._metrics.items():
            safe_name = name.replace("-", "_")

            # Add metric value
            if isinstance(metric.value, (int, float)):
                lines.append(f"agent_health_{safe_name} {metric.value}")

            # Add status as gauge (0=healthy, 1=degraded, 2=unhealthy, 3=critical)
            status_value = {
                HealthStatus.HEALTHY: 0,
                HealthStatus.DEGRADED: 1,
                HealthStatus.UNHEALTHY: 2,
                HealthStatus.CRITICAL: 3,
                HealthStatus.UNKNOWN: -1,
            }.get(metric.status, -1)

            lines.append(f"agent_health_{safe_name}_status {status_value}")

        # Add summary metrics
        summary = self.get_metrics_summary()
        lines.append(f"agent_uptime_seconds {summary['uptime_seconds']}")
        lines.append(f"agent_error_total {summary['error_count']}")
        lines.append(f"agent_cpu_usage_percent {summary['cpu_avg']:.2f}")
        lines.append(f"agent_memory_usage_mb {summary['memory_avg_mb']:.2f}")

        return "\n".join(lines)
