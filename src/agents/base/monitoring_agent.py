"""
Enhanced base agent with automatic monitoring server registration.

This module provides a base agent class that automatically registers with
the monitoring server and sends heartbeats.
"""

import asyncio
import logging
from typing import Optional, Dict, Any

from .agent import BaseAgent, AgentConfig

# Import the mixin from the projects directory
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'projects', 'monitoring', 'src'))
from agent_registry import AgentRegistrationMixin


class MonitoringAgent(AgentRegistrationMixin, BaseAgent):
    """
    Enhanced base agent with automatic monitoring server registration.
    
    This agent automatically:
    - Registers with the monitoring server on startup
    - Sends periodic heartbeats with status updates
    - Unregisters when stopping
    - Reports activities to the monitoring server
    """
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        config: Optional[AgentConfig] = None,
        monitoring_url: str = 'http://localhost:6795',
        api_key: str = 'aios_default_key',
        **kwargs
    ):
        # Initialize both parent classes
        super().__init__(
            agent_id=agent_id,
            config=config,
            monitoring_url=monitoring_url,
            api_key=api_key,
            **kwargs
        )
        
        self.monitoring_enabled = True
        self.logger = logging.getLogger(f"monitoring_agent.{self.id}")
    
    async def on_start(self) -> None:
        """Enhanced startup with monitoring registration."""
        await super().on_start()
        
        if self.monitoring_enabled:
            success = await self.register_with_monitoring()
            if success:
                self.logger.info("Successfully registered with monitoring server")
                await self._report_activity("startup", "info", "Agent started and registered")
            else:
                self.logger.warning("Failed to register with monitoring server")
    
    async def on_stop(self) -> None:
        """Enhanced shutdown with monitoring cleanup."""
        if self.monitoring_enabled:
            await self._report_activity("shutdown", "info", "Agent shutting down")
            await self.unregister_from_monitoring()
            self.logger.info("Unregistered from monitoring server")
        
        await super().on_stop()
    
    async def execute_task(self, task) -> Any:
        """Enhanced task execution with monitoring integration."""
        # Report task start
        if self.monitoring_enabled:
            await self._report_activity(
                "task_start", 
                "info", 
                f"Starting task: {task.description}",
                {
                    "task_id": task.id,
                    "task_type": task.type.value if hasattr(task.type, 'value') else str(task.type),
                    "task_description": task.description,
                    "priority": task.priority.value if hasattr(task.priority, 'value') else str(task.priority)
                }
            )
        
        try:
            # Execute the task using parent implementation
            result = await super().execute_task(task)
            
            # Report task completion
            if self.monitoring_enabled:
                await self._report_activity(
                    "task_complete",
                    "success" if result.status == "success" else "error",
                    f"Task {result.status}: {task.description}",
                    {
                        "task_id": task.id,
                        "result_status": result.status,
                        "execution_time": result.execution_time,
                        "model_used": result.model_used
                    }
                )
            
            return result
            
        except Exception as e:
            # Report task error
            if self.monitoring_enabled:
                await self._report_activity(
                    "task_error",
                    "error",
                    f"Task failed: {str(e)}",
                    {
                        "task_id": task.id,
                        "error": str(e),
                        "task_description": task.description
                    }
                )
            raise
    
    async def _report_activity(
        self, 
        activity_type: str, 
        status: str, 
        message: str, 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Report activity to monitoring server."""
        if not self.monitoring_enabled:
            return
        
        try:
            import aiohttp
            from datetime import datetime
            import uuid
            
            activity = {
                'id': str(uuid.uuid4()),
                'agent_id': self.id,
                'agent_name': self.name,
                'type': activity_type,
                'status': status,
                'message': message,
                'metadata': metadata or {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'{self.monitoring_url}/api/activities',
                    json=activity,
                    headers={'X-API-Key': self.api_key}
                ) as response:
                    if response.status != 200:
                        self.logger.warning(f"Failed to report activity: {response.status}")
                        
        except Exception as e:
            self.logger.warning(f"Error reporting activity: {e}")
    
    async def _send_heartbeat(self):
        """Enhanced heartbeat with additional agent metrics."""
        try:
            # Get enhanced status data
            status_data = {
                'status': self.state.value if hasattr(self.state, 'value') else str(self.state),
                'metadata': {
                    'current_tasks': len(self.current_tasks),
                    'tasks_completed': len(self.task_history),
                    'success_rate': self._calculate_success_rate(),
                    'uptime_seconds': self.uptime_seconds,
                    'memory_usage': len(self.memory),
                    'error_count': self.error_count,
                    'last_error': self.last_error,
                    'health_score': self._calculate_health_score(),
                    'capabilities': self.capabilities,
                    'agent_type': self.agent_type.value if hasattr(self.agent_type, 'value') else str(self.agent_type),
                    'is_busy': self.is_busy,
                    'can_accept_tasks': self.can_accept_tasks
                }
            }
            
            # Call parent heartbeat with enhanced data
            await super()._send_heartbeat()
            
        except Exception as e:
            self.logger.warning(f"Enhanced heartbeat error: {e}")
            # Fallback to basic heartbeat
            await super()._send_heartbeat()
    
    def _calculate_success_rate(self) -> float:
        """Calculate task success rate."""
        if not self.task_history:
            return 1.0
        
        successful_tasks = sum(1 for result in self.task_history if result.status == "success")
        return successful_tasks / len(self.task_history)
    
    def enable_monitoring(self):
        """Enable monitoring integration."""
        self.monitoring_enabled = True
        self.logger.info("Monitoring enabled")
    
    def disable_monitoring(self):
        """Disable monitoring integration."""
        self.monitoring_enabled = False
        self.logger.info("Monitoring disabled")
    
    async def send_custom_metric(self, metric_name: str, value: Any, metadata: Optional[Dict[str, Any]] = None):
        """Send custom metric to monitoring server."""
        await self._report_activity(
            "custom_metric",
            "info",
            f"Metric: {metric_name} = {value}",
            {
                'metric_name': metric_name,
                'metric_value': value,
                'custom_metadata': metadata or {}
            }
        )
    
    async def report_milestone(self, milestone: str, details: Optional[Dict[str, Any]] = None):
        """Report a significant milestone or achievement."""
        await self._report_activity(
            "milestone",
            "success",
            f"Milestone reached: {milestone}",
            {
                'milestone': milestone,
                'details': details or {}
            }
        )
    
    async def report_issue(self, issue: str, severity: str = "warning", details: Optional[Dict[str, Any]] = None):
        """Report an issue or concern."""
        await self._report_activity(
            "issue",
            severity,
            f"Issue reported: {issue}",
            {
                'issue': issue,
                'severity': severity,
                'details': details or {}
            }
        )