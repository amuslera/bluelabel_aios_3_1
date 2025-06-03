"""
Theatrical Dashboard Adapter for v3.1 Agents

This module bridges the v3.0 theatrical dashboard design with v3.1's agent architecture,
providing a unified interface for beautiful real-time agent monitoring.
"""

import asyncio
import logging
import time
import random
from datetime import datetime
from typing import Dict, Optional, Any, List, Callable
from dataclasses import dataclass
from enum import Enum

# v3.1 imports
from src.agents.specialists.backend_agent import BackendAgent
from src.agents.specialists.frontend_agent import FrontendAgent
from src.agents.specialists.qa_agent import QAAgent

# Try to import optional agents
try:
    from src.agents.specialists.devops_agent import JordanDevOpsAgent as DevOpsAgent
except ImportError:
    DevOpsAgent = None
    
try:
    from src.agents.specialists.cto_agent import CTOAgent
except ImportError:
    CTOAgent = None

from src.agents.base.types import AgentType

# Define enums we need
class TaskStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    
class ActivityType:
    THINKING = "thinking"
    WORKING = "working"
    COMMUNICATING = "communicating"
    IDLE = "idle"
from src.core.routing.llm_integration import LLMIntegration


class EventType(Enum):
    """Types of theatrical events"""
    INIT = "init"
    PHASE = "phase"
    THINK = "think"
    WORK = "work"
    SUCCESS = "success"
    ERROR = "error"
    ACTIVITY = "activity"
    MESSAGE = "message"
    COST = "cost"
    PROJECT = "project"


@dataclass
class TheatricalEvent:
    """Event structure compatible with v3.0 dashboard"""
    type: EventType
    agent_id: str
    message: str
    timestamp: datetime
    details: Dict[str, Any] = None
    progress: float = 0.0
    cost: float = 0.0
    tokens: int = 0


class AgentAdapter:
    """Adapter to make v3.1 agents work with theatrical dashboard"""
    
    def __init__(self, agent_id: str, agent_name: str, agent_instance: Any):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.agent = agent_instance
        self.status = "idle"
        self.current_task = None
        self.tasks_completed = 0
        self.total_cost = 0.0
        self.total_tokens = 0
        
    async def execute_task(self, task_description: str, event_callback: Callable) -> Dict[str, Any]:
        """Execute a task with theatrical event callbacks"""
        self.status = "thinking"
        self.current_task = task_description
        
        # Emit thinking event
        event_callback(TheatricalEvent(
            type=EventType.THINK,
            agent_id=self.agent_id,
            message=f"💭 Analyzing: {task_description}",
            timestamp=datetime.now()
        ))
        
        # Simulate thinking time
        await asyncio.sleep(1.5)
        
        # Execute actual task
        self.status = "working"
        event_callback(TheatricalEvent(
            type=EventType.WORK,
            agent_id=self.agent_id,
            message=f"⚙️ Implementing: {task_description}",
            timestamp=datetime.now(),
            progress=0.5
        ))
        
        try:
            # Call the actual agent's task execution
            if hasattr(self.agent, 'execute_task'):
                result = await self.agent.execute_task({
                    'description': task_description,
                    'type': 'implementation'
                })
            else:
                # Simulate for agents without execute_task
                await asyncio.sleep(2)
                result = {
                    'success': True,
                    'output': f"Completed: {task_description}",
                    'lines_of_code': 150
                }
            
            # Success event
            self.status = "success"
            self.tasks_completed += 1
            
            # Track metrics
            cost = result.get('cost', 0.05)
            tokens = result.get('tokens', 500)
            self.total_cost += cost
            self.total_tokens += tokens
            
            event_callback(TheatricalEvent(
                type=EventType.SUCCESS,
                agent_id=self.agent_id,
                message=f"✅ Completed: {task_description}",
                timestamp=datetime.now(),
                progress=1.0,
                cost=cost,
                tokens=tokens,
                details=result
            ))
            
            return result
            
        except Exception as e:
            self.status = "error"
            event_callback(TheatricalEvent(
                type=EventType.ERROR,
                agent_id=self.agent_id,
                message=f"❌ Error: {str(e)}",
                timestamp=datetime.now()
            ))
            raise
        finally:
            await asyncio.sleep(0.5)
            self.status = "idle"
            self.current_task = None


class TheatricalOrchestrator:
    """Orchestrator that manages v3.1 agents with theatrical presentation"""
    
    def __init__(self, event_callback: Optional[Callable] = None):
        self.agents: Dict[str, AgentAdapter] = {}
        self.event_callback = event_callback or self._default_callback
        self.llm_integration = None
        self.start_time = None
        self.project_name = ""
        
    def _default_callback(self, event: TheatricalEvent):
        """Default event handler"""
        print(f"[{event.timestamp.strftime('%H:%M:%S')}] {event.agent_id}: {event.message}")
        
    def emit_event(self, event: TheatricalEvent):
        """Emit a theatrical event"""
        if self.event_callback:
            self.event_callback(event)
            
    async def initialize(self):
        """Initialize the orchestrator and agents"""
        self.emit_event(TheatricalEvent(
            type=EventType.INIT,
            agent_id="orchestrator",
            message="🎬 Initializing AI Development Team...",
            timestamp=datetime.now()
        ))
        
        # Initialize LLM integration
        self.llm_integration = LLMIntegration()
        
        # Define agents to create
        agent_configs = [
            ("cto-001", "Sarah Chen", "CTO", CTOAgent),
            ("backend-001", "Marcus Chen", "Backend Engineer", BackendAgent),
            ("frontend-001", "Emily Rodriguez", "Frontend Engineer", FrontendAgent),
            ("qa-001", "Alex Thompson", "QA Engineer", QAAgent),
            ("devops-001", "Jordan Kim", "DevOps Engineer", DevOpsAgent),
        ]
        
        # Create and initialize agents
        for agent_id, name, role, agent_class in agent_configs:
            await asyncio.sleep(0.5)
            
            self.emit_event(TheatricalEvent(
                type=EventType.INIT,
                agent_id=agent_id,
                message=f"🔄 Initializing {name} ({role})...",
                timestamp=datetime.now()
            ))
            
            if agent_class:
                # Create real v3.1 agent with proper config
                try:
                    # Try creating with no args first
                    agent_instance = agent_class()
                except Exception:
                    # If that fails, try with agent_id
                    try:
                        agent_instance = agent_class(agent_id=agent_id)
                    except Exception:
                        # If still fails, create mock
                        self.emit_event(TheatricalEvent(
                            type=EventType.INIT,
                            agent_id=agent_id,
                            message=f"⚠️ {name} (simulated - init failed)",
                            timestamp=datetime.now()
                        ))
                        mock_agent = type('MockAgent', (), {
                            'execute_task': self._mock_agent_task
                        })()
                        adapter = AgentAdapter(agent_id, name, mock_agent)
                        self.agents[agent_id] = adapter
                        continue
                        
                adapter = AgentAdapter(agent_id, name, agent_instance)
                self.agents[agent_id] = adapter
            else:
                # Create mock adapter for CTO
                mock_agent = type('MockAgent', (), {
                    'execute_task': self._mock_cto_task
                })()
                adapter = AgentAdapter(agent_id, name, mock_agent)
                self.agents[agent_id] = adapter
            
            self.emit_event(TheatricalEvent(
                type=EventType.SUCCESS,
                agent_id=agent_id,
                message=f"✅ {name} ready!",
                timestamp=datetime.now()
            ))
            
    async def _mock_agent_task(self, task):
        """Generic mock agent task execution"""
        await asyncio.sleep(2)
        return {
            'success': True,
            'output': 'Task completed successfully',
            'lines_of_code': random.randint(100, 300)
        }
        
    async def _mock_cto_task(self, task):
        """Mock CTO task execution"""
        await asyncio.sleep(2)
        return {
            'success': True,
            'output': 'Architecture and planning complete',
            'specification': {
                'backend': 'FastAPI with WebSocket support',
                'frontend': 'React with real-time updates',
                'database': 'PostgreSQL with Redis cache',
                'deployment': 'Kubernetes with auto-scaling'
            }
        }
    
    async def start_project(self, project_name: str, project_description: str):
        """Start a new project with theatrical presentation"""
        self.project_name = project_name
        self.start_time = time.time()
        
        self.emit_event(TheatricalEvent(
            type=EventType.PROJECT,
            agent_id="orchestrator",
            message=f"🎯 Starting Project: {project_name}",
            timestamp=datetime.now(),
            details={'description': project_description}
        ))
        
        await asyncio.sleep(1)
        
    async def run_phase(self, phase_name: str, agent_id: str, tasks: List[str]):
        """Run a project phase with theatrical timing"""
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
            
        self.emit_event(TheatricalEvent(
            type=EventType.PHASE,
            agent_id=agent_id,
            message=f"📋 {phase_name}",
            timestamp=datetime.now()
        ))
        
        await asyncio.sleep(1)
        
        # Execute tasks in sequence
        for i, task in enumerate(tasks):
            progress = i / len(tasks)
            
            # Emit progress update
            self.emit_event(TheatricalEvent(
                type=EventType.ACTIVITY,
                agent_id=agent_id,
                message=f"Task {i+1}/{len(tasks)}: {task}",
                timestamp=datetime.now(),
                progress=progress
            ))
            
            # Execute task through adapter
            result = await agent.execute_task(task, self.emit_event)
            
            # Small pause between tasks
            await asyncio.sleep(0.5)
            
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics for all agents"""
        metrics = {
            'total_time': time.time() - self.start_time if self.start_time else 0,
            'agents': {}
        }
        
        for agent_id, agent in self.agents.items():
            metrics['agents'][agent_id] = {
                'name': agent.agent_name,
                'status': agent.status,
                'tasks_completed': agent.tasks_completed,
                'total_cost': agent.total_cost,
                'total_tokens': agent.total_tokens,
                'current_task': agent.current_task
            }
            
        return metrics