"""
Minimal Theatrical Dashboard - Works without full agent initialization

This version uses mock agents to demonstrate the UI without requiring
the full v3.1 agent infrastructure to be running.
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.box import ROUNDED
from collections import deque
from dataclasses import dataclass
from enum import Enum
import random


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
    PROJECT = "project"


@dataclass
class TheatricalEvent:
    """Event structure for dashboard"""
    type: EventType
    agent_id: str
    message: str
    timestamp: datetime
    details: Dict[str, Any] = None
    progress: float = 0.0
    cost: float = 0.0
    tokens: int = 0


class MockAgent:
    """Simplified mock agent for demonstrations"""
    
    def __init__(self, agent_id: str, name: str, role: str):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.status = "idle"
        self.tasks_completed = 0
        self.total_cost = 0.0
        self.total_tokens = 0
        
    async def execute_task(self, task: str, callback: Callable) -> Dict[str, Any]:
        """Simulate task execution"""
        # Thinking phase
        callback(TheatricalEvent(
            type=EventType.THINK,
            agent_id=self.agent_id,
            message=f"💭 Analyzing: {task}",
            timestamp=datetime.now()
        ))
        await asyncio.sleep(1.5)
        
        # Working phase
        callback(TheatricalEvent(
            type=EventType.WORK,
            agent_id=self.agent_id,
            message=f"⚙️ Implementing: {task}",
            timestamp=datetime.now(),
            progress=0.5
        ))
        await asyncio.sleep(2)
        
        # Success
        cost = round(random.uniform(0.01, 0.05), 4)
        tokens = random.randint(200, 800)
        self.tasks_completed += 1
        self.total_cost += cost
        self.total_tokens += tokens
        
        callback(TheatricalEvent(
            type=EventType.SUCCESS,
            agent_id=self.agent_id,
            message=f"✅ Completed: {task}",
            timestamp=datetime.now(),
            progress=1.0,
            cost=cost,
            tokens=tokens
        ))
        
        return {
            'success': True,
            'output': f"Completed {task}",
            'cost': cost,
            'tokens': tokens
        }


class MinimalTheatricalDashboard:
    """Minimal theatrical dashboard that works without full infrastructure"""
    
    def __init__(self):
        self.console = Console()
        self.agents: Dict[str, MockAgent] = {}
        self.agents_data = {}
        self.event_log = deque(maxlen=50)
        self.agent_logs = {}
        self.start_time = None
        self.project_info = {}
        
        # Agent configuration
        self.agent_configs = [
            ("cto-001", "Sarah Chen", "CTO", "🏛️", "magenta"),
            ("backend-001", "Marcus Chen", "Backend Engineer", "⚙️", "cyan"),
            ("frontend-001", "Emily Rodriguez", "Frontend Engineer", "🎨", "yellow"),
            ("qa-001", "Alex Thompson", "QA Engineer", "🧪", "green"),
            ("devops-001", "Jordan Kim", "DevOps Engineer", "🚀", "blue"),
        ]
        
        self.agent_styles = {
            agent_id: {
                "icon": icon,
                "color": color,
                "name": name,
                "role": role
            }
            for agent_id, name, role, icon, color in self.agent_configs
        }
        
    def _event_callback(self, event: TheatricalEvent):
        """Handle events from agents"""
        self.event_log.append(event)
        
        agent_id = event.agent_id
        if agent_id not in self.agent_logs:
            self.agent_logs[agent_id] = deque(maxlen=10)
        self.agent_logs[agent_id].append(event)
        
        # Update agent data
        if agent_id in self.agents_data:
            agent = self.agents_data[agent_id]
            if event.type == EventType.THINK:
                agent['status'] = '🤔 Thinking'
            elif event.type == EventType.WORK:
                agent['status'] = '⚙️ Working'
            elif event.type == EventType.SUCCESS:
                agent['status'] = '✅ Ready'
                agent['tasks_completed'] += 1
                agent['total_cost'] += event.cost
                agent['total_tokens'] += event.tokens
        
        # Update display
        if hasattr(self, 'layout'):
            self._update_layout()
            
    def _create_layout(self):
        """Create dashboard layout"""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        layout["body"].split_row(
            Layout(name="agents", ratio=2),
            Layout(name="timeline", ratio=1)
        )
        
        # Create agent grid
        layout["agents"].split_column(
            Layout(name="row1"),
            Layout(name="row2")
        )
        
        return layout
        
    def _create_header(self) -> Panel:
        """Create header"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        text = Text()
        text.append("🎭 AIOSv3.1 Theatrical Dashboard (Minimal)\n", style="bold magenta")
        text.append(f"Project: {self.project_info.get('name', 'Demo')} | ", style="yellow")
        text.append(f"Elapsed: {elapsed:.1f}s", style="cyan")
        return Panel(text, box=ROUNDED)
        
    def _create_agent_panel(self, agent_id: str) -> Panel:
        """Create agent panel"""
        agent = self.agents_data.get(agent_id, {})
        style = self.agent_styles.get(agent_id, {})
        
        content = []
        content.append(f"{style['icon']} {style['name']}")
        content.append(f"Status: {agent.get('status', '⚪ Idle')}")
        content.append("")
        
        # Recent activity
        if agent_id in self.agent_logs:
            content.append("Recent Activity:")
            for event in list(self.agent_logs[agent_id])[-3:]:
                content.append(f"  {event.message[:40]}...")
                
        content.append("")
        content.append(f"Tasks: {agent.get('tasks_completed', 0)} | "
                      f"Cost: ${agent.get('total_cost', 0):.4f}")
        
        return Panel(
            "\n".join(content),
            title=style['role'],
            box=ROUNDED,
            style=style['color']
        )
        
    def _create_timeline(self) -> Panel:
        """Create timeline panel"""
        content = []
        content.append("📜 Event Timeline\n")
        
        for event in list(self.event_log)[-10:]:
            style = self.agent_styles.get(event.agent_id, {})
            timestamp = event.timestamp.strftime("%H:%M:%S")
            content.append(f"{timestamp} {style.get('icon', '❓')} {event.message[:40]}...")
            
        return Panel("\n".join(content), title="Events", box=ROUNDED)
        
    def _create_footer(self) -> Panel:
        """Create footer"""
        return Panel(
            "Press Ctrl+C to exit | Minimal Demo Mode",
            box=ROUNDED,
            style="dim"
        )
        
    def _update_layout(self):
        """Update the layout"""
        if not hasattr(self, 'layout'):
            return
            
        self.layout["header"].update(self._create_header())
        
        # Update agent panels
        self.layout["row1"].split_row(
            Layout(self._create_agent_panel("cto-001")),
            Layout(self._create_agent_panel("backend-001")),
            Layout(self._create_agent_panel("frontend-001"))
        )
        
        self.layout["row2"].split_row(
            Layout(self._create_agent_panel("qa-001")),
            Layout(self._create_agent_panel("devops-001")),
            Layout(Panel("System Metrics\n\nTotal Tasks: " + 
                        str(sum(a.get('tasks_completed', 0) for a in self.agents_data.values())),
                        box=ROUNDED))
        )
        
        self.layout["timeline"].update(self._create_timeline())
        self.layout["footer"].update(self._create_footer())
        
    async def initialize(self):
        """Initialize mock agents"""
        self.console.print("[bold magenta]🎭 Initializing Minimal Dashboard...[/]")
        
        # Create mock agents
        for agent_id, name, role, _, _ in self.agent_configs:
            self.agents[agent_id] = MockAgent(agent_id, name, role)
            self.agents_data[agent_id] = {
                'name': name,
                'role': role,
                'status': '⚪ Idle',
                'tasks_completed': 0,
                'total_cost': 0.0,
                'total_tokens': 0
            }
            
            self._event_callback(TheatricalEvent(
                type=EventType.INIT,
                agent_id=agent_id,
                message=f"✅ {name} ready!",
                timestamp=datetime.now()
            ))
            await asyncio.sleep(0.3)
            
    async def run_demo_project(self):
        """Run demo project"""
        self.start_time = time.time()
        self.project_info = {'name': 'Chat Application Demo'}
        
        # Phase 1: CTO Planning
        agent = self.agents["cto-001"]
        for task in ["Analyze requirements", "Design architecture"]:
            await agent.execute_task(task, self._event_callback)
            
        # Phase 2: Backend
        agent = self.agents["backend-001"]
        for task in ["Create API structure", "Implement WebSocket"]:
            await agent.execute_task(task, self._event_callback)
            
        # Phase 3: Frontend
        agent = self.agents["frontend-001"]
        for task in ["Build UI components", "Add real-time chat"]:
            await agent.execute_task(task, self._event_callback)
            
        # Phase 4: QA
        agent = self.agents["qa-001"]
        for task in ["Write tests", "Security audit"]:
            await agent.execute_task(task, self._event_callback)
            
        # Phase 5: DevOps
        agent = self.agents["devops-001"]
        for task in ["Create Docker setup", "Deploy to cloud"]:
            await agent.execute_task(task, self._event_callback)
            
        self._event_callback(TheatricalEvent(
            type=EventType.SUCCESS,
            agent_id="system",
            message="🎉 Project Complete!",
            timestamp=datetime.now()
        ))
        
    async def run(self):
        """Run the dashboard"""
        await self.initialize()
        
        self.layout = self._create_layout()
        self._update_layout()
        
        with Live(self.layout, console=self.console, refresh_per_second=4) as live:
            await self.run_demo_project()
            
            self.console.print("\n[bold green]Demo complete! Press Ctrl+C to exit.[/]")
            try:
                await asyncio.Event().wait()
            except KeyboardInterrupt:
                pass
                
        self.console.print("\n[bold magenta]Thank you for watching![/]")