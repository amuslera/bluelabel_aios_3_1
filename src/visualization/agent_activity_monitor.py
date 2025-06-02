"""
Agent Activity Monitor

Bridges the gap between actual agent activities and the visualization system,
providing real-time monitoring and theatrical presentation of agent work.
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.visualization.agent_visualizer import AgentVisualizer, ActivityType
from src.visualization.code_visualization import CodeVisualizer
# For demo purposes, we'll create a simple TaskResult class
from dataclasses import dataclass as task_dataclass
from typing import Optional as task_optional

@task_dataclass
class TaskResult:
    """Simple task result for visualization"""
    task_id: str
    agent_id: str
    status: str
    result: dict
    error: task_optional[str]
    execution_time: float
    model_used: str
    cost_estimate: float


class EventType(Enum):
    """Types of events that can be monitored"""
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    CODE_GENERATED = "code_generated"
    MESSAGE_SENT = "message_sent"
    TEST_RUN = "test_run"
    DEPLOYMENT_STARTED = "deployment_started"
    DEPLOYMENT_COMPLETED = "deployment_completed"
    ERROR_DETECTED = "error_detected"
    REVIEW_COMMENT = "review_comment"


@dataclass
class MonitorEvent:
    """Represents a monitorable event"""
    event_type: EventType
    agent_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5  # 0.0 to 1.0 for auto-slowdown


class AgentActivityMonitor:
    """Monitors and visualizes agent activities in real-time"""
    
    def __init__(
        self, 
        visualizer: AgentVisualizer,
        code_visualizer: Optional[CodeVisualizer] = None
    ):
        self.visualizer = visualizer
        self.code_visualizer = code_visualizer or CodeVisualizer()
        self.event_queue: asyncio.Queue[MonitorEvent] = asyncio.Queue()
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self.agent_states: Dict[str, Dict[str, Any]] = {}
        self.monitoring = False
        
        # Register default event handlers
        self._register_default_handlers()
        
    def _register_default_handlers(self):
        """Register default event handlers"""
        self.register_handler(EventType.TASK_STARTED, self._handle_task_started)
        self.register_handler(EventType.TASK_COMPLETED, self._handle_task_completed)
        self.register_handler(EventType.CODE_GENERATED, self._handle_code_generated)
        self.register_handler(EventType.MESSAGE_SENT, self._handle_message_sent)
        self.register_handler(EventType.TEST_RUN, self._handle_test_run)
        self.register_handler(EventType.DEPLOYMENT_STARTED, self._handle_deployment_started)
        self.register_handler(EventType.ERROR_DETECTED, self._handle_error_detected)
        
    def register_handler(self, event_type: EventType, handler: Callable):
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        
    async def emit_event(self, event: MonitorEvent):
        """Emit an event to be processed"""
        await self.event_queue.put(event)
        
    async def monitor_task(self, agent_name: str, task: str) -> TaskResult:
        """Monitor a task execution"""
        # Emit task started event
        await self.emit_event(MonitorEvent(
            event_type=EventType.TASK_STARTED,
            agent_name=agent_name,
            data={"task": task}
        ))
        
        # Update agent state
        self.agent_states[agent_name] = {
            "current_task": task,
            "start_time": datetime.now(),
            "status": "working"
        }
        
        # Simulate task execution (in real implementation, this would
        # be replaced with actual task monitoring)
        await asyncio.sleep(2)
        
        # Create mock result
        result = TaskResult(
            task_id=f"task_{datetime.now().timestamp()}",
            agent_id=agent_name,
            status="success",  # TaskResult expects a string status
            result={"output": f"Completed: {task}"},
            error=None,
            execution_time=2.0,
            model_used="mock",
            cost_estimate=0.0
        )
        
        # Emit task completed event
        await self.emit_event(MonitorEvent(
            event_type=EventType.TASK_COMPLETED,
            agent_name=agent_name,
            data={"task": task, "result": result}
        ))
        
        return result
        
    async def monitor_code_generation(
        self, 
        agent_name: str, 
        file_path: str,
        code: str,
        language: str = "python"
    ):
        """Monitor code generation activity"""
        # Create file if it doesn't exist
        if file_path not in self.code_visualizer.files:
            self.code_visualizer.create_file(file_path, language)
            
        # Emit code generation event with theatrical pacing
        chunks = self._chunk_code_for_effect(code)
        
        for i, chunk in enumerate(chunks):
            await self.emit_event(MonitorEvent(
                event_type=EventType.CODE_GENERATED,
                agent_name=agent_name,
                data={
                    "file_path": file_path,
                    "code_chunk": chunk,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                },
                importance=0.3 if i < len(chunks) - 1 else 0.7
            ))
            
            # Theatrical delay between chunks
            await asyncio.sleep(self.visualizer.pacing.get_delay(0.5))
            
    def _chunk_code_for_effect(self, code: str, chunk_size: int = 50) -> List[str]:
        """Split code into chunks for theatrical effect"""
        lines = code.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in lines:
            current_chunk.append(line)
            current_size += len(line)
            
            if current_size >= chunk_size or line.strip().endswith(':'):
                # End chunk at natural boundaries
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
                
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
            
        return chunks
        
    async def monitor_message(
        self,
        from_agent: str,
        to_agent: str,
        message: str,
        message_type: str = "chat"
    ):
        """Monitor inter-agent communication"""
        await self.emit_event(MonitorEvent(
            event_type=EventType.MESSAGE_SENT,
            agent_name=from_agent,
            data={
                "to_agent": to_agent,
                "message": message,
                "message_type": message_type
            },
            importance=0.6
        ))
        
    async def monitor_test_execution(
        self,
        agent_name: str,
        test_name: str,
        total_tests: int
    ):
        """Monitor test execution progress"""
        # Simulate test progress
        for i in range(0, total_tests + 1):
            progress = (i / total_tests) * 100
            
            await self.emit_event(MonitorEvent(
                event_type=EventType.TEST_RUN,
                agent_name=agent_name,
                data={
                    "test_name": test_name,
                    "current_test": i,
                    "total_tests": total_tests,
                    "progress": progress
                },
                importance=0.2 if i < total_tests else 0.8
            ))
            
            await asyncio.sleep(self.visualizer.pacing.get_delay(0.2))
            
    async def monitor_deployment(
        self,
        agent_name: str,
        environment: str,
        version: str
    ):
        """Monitor deployment process"""
        stages = [
            ("Building Docker image", 20),
            ("Running security scans", 40),
            ("Pushing to registry", 60),
            ("Updating Kubernetes", 80),
            ("Health checks passing", 100)
        ]
        
        await self.emit_event(MonitorEvent(
            event_type=EventType.DEPLOYMENT_STARTED,
            agent_name=agent_name,
            data={
                "environment": environment,
                "version": version
            },
            importance=0.9
        ))
        
        for stage, progress in stages:
            await self.visualizer.update_agent_activity(
                agent_name,
                ActivityType.DEPLOYING,
                stage,
                progress=progress,
                metadata={"mood": "focused"}
            )
            
            await asyncio.sleep(self.visualizer.pacing.get_delay(1.5))
            
        await self.emit_event(MonitorEvent(
            event_type=EventType.DEPLOYMENT_COMPLETED,
            agent_name=agent_name,
            data={
                "environment": environment,
                "version": version,
                "success": True
            },
            importance=1.0
        ))
        
    async def _handle_task_started(self, event: MonitorEvent):
        """Handle task started event"""
        task = event.data.get("task", "Unknown task")
        
        # Determine activity type based on task
        activity_type = self._determine_activity_type(task)
        
        await self.visualizer.update_agent_activity(
            event.agent_name,
            activity_type,
            task,
            progress=0,
            metadata={"mood": "focused"}
        )
        
    async def _handle_task_completed(self, event: MonitorEvent):
        """Handle task completed event"""
        task = event.data.get("task", "Unknown task")
        
        await self.visualizer.update_agent_activity(
            event.agent_name,
            ActivityType.IDLE,
            f"Completed: {task}",
            progress=100,
            metadata={"mood": "accomplished"}
        )
        
    async def _handle_code_generated(self, event: MonitorEvent):
        """Handle code generation event"""
        file_path = event.data.get("file_path")
        code_chunk = event.data.get("code_chunk", "")
        chunk_index = event.data.get("chunk_index", 0)
        total_chunks = event.data.get("total_chunks", 1)
        
        # Update typing visualization
        if chunk_index == 0:
            self.code_visualizer.simulate_typing(
                event.agent_name,
                code_chunk,
                file_path
            )
        else:
            current = self.code_visualizer.typing_buffers.get(event.agent_name, "")
            self.code_visualizer.simulate_typing(
                event.agent_name,
                current + "\n" + code_chunk,
                file_path
            )
            
        # Update progress
        progress = ((chunk_index + 1) / total_chunks) * 100
        
        await self.visualizer.update_agent_activity(
            event.agent_name,
            ActivityType.CODING,
            f"Writing {file_path}",
            progress=progress,
            code_snippet=code_chunk,
            metadata={"mood": "focused"}
        )
        
        # Commit when done
        if chunk_index == total_chunks - 1:
            await asyncio.sleep(self.visualizer.pacing.get_delay(0.5))
            self.code_visualizer.commit_typing(event.agent_name, file_path)
            
    async def _handle_message_sent(self, event: MonitorEvent):
        """Handle message sent event"""
        to_agent = event.data.get("to_agent", "Team")
        message = event.data.get("message", "")
        message_type = event.data.get("message_type", "chat")
        
        await self.visualizer.send_message(
            event.agent_name,
            to_agent,
            message,
            message_type
        )
        
        # Brief communication activity
        await self.visualizer.update_agent_activity(
            event.agent_name,
            ActivityType.COMMUNICATING,
            f"Messaging {to_agent}",
            progress=100,
            metadata={"mood": "collaborative"}
        )
        
    async def _handle_test_run(self, event: MonitorEvent):
        """Handle test execution event"""
        test_name = event.data.get("test_name", "tests")
        progress = event.data.get("progress", 0)
        current = event.data.get("current_test", 0)
        total = event.data.get("total_tests", 0)
        
        await self.visualizer.update_agent_activity(
            event.agent_name,
            ActivityType.TESTING,
            f"Running {test_name}: {current}/{total}",
            progress=progress,
            metadata={"mood": "methodical"}
        )
        
        # Update metrics when tests complete
        if progress >= 100:
            self.visualizer.metrics["tests_passed"] += total
            
    async def _handle_deployment_started(self, event: MonitorEvent):
        """Handle deployment started event"""
        environment = event.data.get("environment", "production")
        version = event.data.get("version", "latest")
        
        await self.visualizer.update_agent_activity(
            event.agent_name,
            ActivityType.DEPLOYING,
            f"Deploying {version} to {environment}",
            progress=0,
            metadata={"mood": "focused"}
        )
        
        # Update workflow
        self.visualizer.update_workflow(
            f"Deployment to {environment}",
            [
                {"name": "Build image", "completed": False},
                {"name": "Security scan", "completed": False},
                {"name": "Deploy", "completed": False},
                {"name": "Health check", "completed": False}
            ]
        )
        
    async def _handle_error_detected(self, event: MonitorEvent):
        """Handle error detection event"""
        error_type = event.data.get("error_type", "Unknown error")
        
        await self.visualizer.update_agent_activity(
            event.agent_name,
            ActivityType.DEBUGGING,
            f"Investigating: {error_type}",
            progress=50,
            metadata={"mood": "stressed"}
        )
        
        self.visualizer.metrics["bugs_found"] += 1
        
    def _determine_activity_type(self, task: str) -> ActivityType:
        """Determine activity type from task description"""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["code", "implement", "write"]):
            return ActivityType.CODING
        elif any(word in task_lower for word in ["test", "verify", "check"]):
            return ActivityType.TESTING
        elif any(word in task_lower for word in ["debug", "fix", "investigate"]):
            return ActivityType.DEBUGGING
        elif any(word in task_lower for word in ["deploy", "release"]):
            return ActivityType.DEPLOYING
        elif any(word in task_lower for word in ["design", "plan", "architect"]):
            return ActivityType.DESIGNING
        elif any(word in task_lower for word in ["review", "analyze"]):
            return ActivityType.REVIEWING
        elif any(word in task_lower for word in ["monitor", "observe"]):
            return ActivityType.MONITORING
        else:
            return ActivityType.THINKING
            
    async def start_monitoring(self):
        """Start the monitoring loop"""
        self.monitoring = True
        
        while self.monitoring:
            try:
                # Wait for events with timeout
                event = await asyncio.wait_for(
                    self.event_queue.get(),
                    timeout=0.1
                )
                
                # Apply auto-slowdown for important events
                if self.visualizer.pacing.speed_multiplier > 0:
                    importance = event.importance
                    if importance > 0.7:
                        # Temporarily slow down for important events
                        original_speed = self.visualizer.pacing.speed_multiplier
                        self.visualizer.pacing.speed_multiplier *= (1 - importance * 0.5)
                        
                        # Process event
                        await self._process_event(event)
                        
                        # Restore speed
                        self.visualizer.pacing.speed_multiplier = original_speed
                    else:
                        await self._process_event(event)
                else:
                    await self._process_event(event)
                    
            except asyncio.TimeoutError:
                # No events, continue
                continue
                
    async def _process_event(self, event: MonitorEvent):
        """Process a single event"""
        handlers = self.event_handlers.get(event.event_type, [])
        for handler in handlers:
            await handler(event)
            
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.monitoring = False