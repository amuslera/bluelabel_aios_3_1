"""
Theatrical Dashboard for v3.1 - Rich-based real-time agent monitoring

This dashboard provides a beautiful, real-time view of agent orchestration
with live updates, progress tracking, and detailed communication logs.
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.box import ROUNDED
from collections import deque

from src.visualization.theatrical_adapter import TheatricalOrchestrator, TheatricalEvent, EventType


class TheatricalDashboard:
    """Rich-based theatrical dashboard for agent monitoring"""
    
    def __init__(self, max_events: int = 50, max_agent_logs: int = 10):
        self.console = Console()
        self.orchestrator = None
        self.agents_data = {}
        self.event_log = deque(maxlen=max_events)
        self.agent_logs = {}  # Per-agent activity logs
        self.max_agent_logs = max_agent_logs
        self.start_time = None
        self.project_info = {}
        self.layout = None
        self.live = None
        
        # Agent icons and colors
        self.agent_styles = {
            "cto-001": {"icon": "🏛️", "color": "magenta", "name": "Sarah Chen"},
            "backend-001": {"icon": "⚙️", "color": "cyan", "name": "Marcus Chen"},
            "frontend-001": {"icon": "🎨", "color": "yellow", "name": "Emily Rodriguez"},
            "qa-001": {"icon": "🧪", "color": "green", "name": "Alex Thompson"},
            "devops-001": {"icon": "🚀", "color": "blue", "name": "Jordan Kim"},
            "orchestrator": {"icon": "🎬", "color": "white", "name": "System"}
        }
        
    def _event_callback(self, event: TheatricalEvent):
        """Handle theatrical events from orchestrator"""
        # Add to main event log
        self.event_log.append(event)
        
        # Add to agent-specific log
        agent_id = event.agent_id
        if agent_id not in self.agent_logs:
            self.agent_logs[agent_id] = deque(maxlen=self.max_agent_logs)
        self.agent_logs[agent_id].append(event)
        
        # Update agent status
        if agent_id in self.agents_data:
            agent = self.agents_data[agent_id]
            
            if event.type == EventType.THINK:
                agent['status'] = '🤔 Thinking'
            elif event.type == EventType.WORK:
                agent['status'] = '⚙️ Working'
                agent['progress'] = event.progress
            elif event.type == EventType.SUCCESS:
                agent['status'] = '✅ Ready'
                agent['tasks_completed'] += 1
                agent['total_cost'] += event.cost
                agent['total_tokens'] += event.tokens
            elif event.type == EventType.ERROR:
                agent['status'] = '❌ Error'
            else:
                agent['status'] = '⚪ Idle'
                
        # Refresh display
        if self.layout:
            self._update_layout()
            
    def _create_layout(self):
        """Create the dashboard layout"""
        layout = Layout()
        
        # Main structure
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Body split into agents and logs
        layout["body"].split_row(
            Layout(name="agents", ratio=2),
            Layout(name="logs", ratio=1)
        )
        
        # Agents area split into individual panels
        layout["agents"].split_column(
            Layout(name="agents_grid")
        )
        
        # Logs area split into timeline and metrics
        layout["logs"].split_column(
            Layout(name="timeline", ratio=3),
            Layout(name="metrics", ratio=1)
        )
        
        return layout
        
    def _create_header(self) -> Panel:
        """Create header panel"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        header_text = Text()
        header_text.append("🎭 AIOSv3.1 Theatrical Dashboard\n", style="bold magenta")
        header_text.append(f"Project: {self.project_info.get('name', 'N/A')} | ", style="yellow")
        header_text.append(f"Elapsed: {elapsed:.1f}s", style="cyan")
        
        return Panel(header_text, box=ROUNDED, style="bright_white")
        
    def _create_agent_panel(self, agent_id: str) -> Panel:
        """Create panel for individual agent"""
        agent = self.agents_data.get(agent_id, {})
        style_info = self.agent_styles.get(agent_id, {})
        
        # Agent header
        header = Text()
        header.append(f"{style_info.get('icon', '❓')} ", style="bold")
        header.append(f"{agent.get('name', 'Unknown')}\n", style=f"bold {style_info.get('color', 'white')}")
        header.append(f"Status: {agent.get('status', '⚪ Idle')}", style="dim")
        
        # Activity log
        content = [header, ""]
        
        if agent_id in self.agent_logs:
            content.append("Recent Activity:")
            for event in list(self.agent_logs[agent_id])[-5:]:  # Last 5 activities
                timestamp = event.timestamp.strftime("%H:%M:%S")
                content.append(f"[dim]{timestamp}[/dim] {event.message}")
        
        # Metrics
        content.extend([
            "",
            f"Tasks: {agent.get('tasks_completed', 0)} | " +
            f"Cost: ${agent.get('total_cost', 0):.4f} | " +
            f"Tokens: {agent.get('total_tokens', 0):,}"
        ])
        
        panel_content = "\n".join(str(c) for c in content)
        return Panel(
            panel_content,
            title=f"[bold {style_info.get('color', 'white')}]{agent.get('role', 'Agent')}[/]",
            box=ROUNDED,
            style=style_info.get('color', 'white')
        )
        
    def _create_agents_grid(self) -> Layout:
        """Create grid of agent panels"""
        grid = Layout()
        
        # Create 2x3 grid for agents
        grid.split_column(
            Layout(name="row1"),
            Layout(name="row2")
        )
        
        # First row: CTO, Backend, Frontend
        grid["row1"].split_row(
            Layout(self._create_agent_panel("cto-001")),
            Layout(self._create_agent_panel("backend-001")),
            Layout(self._create_agent_panel("frontend-001"))
        )
        
        # Second row: QA, DevOps, Metrics
        grid["row2"].split_row(
            Layout(self._create_agent_panel("qa-001")),
            Layout(self._create_agent_panel("devops-001")),
            Layout(self._create_system_metrics())
        )
        
        return grid
        
    def _create_timeline(self) -> Panel:
        """Create event timeline panel"""
        timeline_text = Text()
        timeline_text.append("📜 Event Timeline\n\n", style="bold yellow")
        
        # Show last N events
        for event in list(self.event_log)[-20:]:
            style_info = self.agent_styles.get(event.agent_id, {})
            timestamp = event.timestamp.strftime("%H:%M:%S")
            
            line = Text()
            line.append(f"{timestamp} ", style="dim")
            line.append(f"{style_info.get('icon', '❓')} ", style="bold")
            line.append(f"{event.message}\n", style=style_info.get('color', 'white'))
            
            timeline_text.append(line)
            
        return Panel(timeline_text, title="Event Log", box=ROUNDED, style="cyan")
        
    def _create_system_metrics(self) -> Panel:
        """Create system metrics panel"""
        metrics = Table(show_header=False, box=None)
        metrics.add_column("Metric", style="cyan")
        metrics.add_column("Value", style="yellow")
        
        # Calculate totals
        total_tasks = sum(a.get('tasks_completed', 0) for a in self.agents_data.values())
        total_cost = sum(a.get('total_cost', 0) for a in self.agents_data.values())
        total_tokens = sum(a.get('total_tokens', 0) for a in self.agents_data.values())
        
        metrics.add_row("Total Tasks", str(total_tasks))
        metrics.add_row("Total Cost", f"${total_cost:.4f}")
        metrics.add_row("Total Tokens", f"{total_tokens:,}")
        metrics.add_row("Agents Active", str(len(self.agents_data)))
        
        return Panel(metrics, title="System Metrics", box=ROUNDED, style="green")
        
    def _create_footer(self) -> Panel:
        """Create footer panel"""
        footer_text = Text()
        footer_text.append("Controls: ", style="bold")
        footer_text.append("Q", style="bold red")
        footer_text.append(" = Quit | ", style="dim")
        footer_text.append("R", style="bold green")
        footer_text.append(" = Refresh | ", style="dim")
        footer_text.append("C", style="bold yellow")
        footer_text.append(" = Clear Logs", style="dim")
        
        return Panel(footer_text, box=ROUNDED, style="dim")
        
    def _update_layout(self):
        """Update the entire layout"""
        if not self.layout:
            return
            
        self.layout["header"].update(self._create_header())
        self.layout["agents_grid"].update(self._create_agents_grid())
        self.layout["timeline"].update(self._create_timeline())
        self.layout["footer"].update(self._create_footer())
        
    async def initialize(self):
        """Initialize the dashboard and orchestrator"""
        self.console.print("[bold magenta]🎭 Initializing Theatrical Dashboard...[/]")
        
        # Create orchestrator with our event callback
        self.orchestrator = TheatricalOrchestrator(event_callback=self._event_callback)
        
        # Initialize agents
        await self.orchestrator.initialize()
        
        # Initialize agent data
        for agent_id, adapter in self.orchestrator.agents.items():
            style_info = self.agent_styles.get(agent_id, {})
            self.agents_data[agent_id] = {
                'name': adapter.agent_name,
                'role': style_info.get('name', 'Agent'),
                'status': '⚪ Idle',
                'tasks_completed': 0,
                'total_cost': 0.0,
                'total_tokens': 0,
                'progress': 0.0
            }
            
    async def run_demo_project(self):
        """Run a demo project showing all agents in action"""
        self.start_time = time.time()
        
        # Start project
        project_name = "Real-time Chat Application"
        project_desc = "WebSocket support, user authentication, and message history"
        self.project_info = {'name': project_name, 'description': project_desc}
        
        await self.orchestrator.start_project(project_name, project_desc)
        
        # Phase 1: Architecture
        await self.orchestrator.run_phase(
            "Phase 1: Architecture & Planning",
            "cto-001",
            [
                "Analyze project requirements",
                "Create technical specification",
                "Define system architecture"
            ]
        )
        
        # Phase 2: Backend
        await self.orchestrator.run_phase(
            "Phase 2: Backend Development",
            "backend-001",
            [
                "Set up FastAPI project structure",
                "Implement WebSocket handlers",
                "Create authentication system",
                "Design database schema"
            ]
        )
        
        # Phase 3: Frontend
        await self.orchestrator.run_phase(
            "Phase 3: Frontend Development",
            "frontend-001",
            [
                "Create React project structure",
                "Build chat UI components",
                "Implement WebSocket client",
                "Add authentication flow"
            ]
        )
        
        # Phase 4: QA
        await self.orchestrator.run_phase(
            "Phase 4: Quality Assurance",
            "qa-001",
            [
                "Write unit tests for backend",
                "Create integration tests",
                "Test WebSocket connections",
                "Perform security audit"
            ]
        )
        
        # Phase 5: DevOps
        await self.orchestrator.run_phase(
            "Phase 5: Deployment",
            "devops-001",
            [
                "Create Docker containers",
                "Set up CI/CD pipeline",
                "Configure Kubernetes",
                "Deploy to cloud"
            ]
        )
        
        # Project complete
        elapsed = time.time() - self.start_time
        self._event_callback(TheatricalEvent(
            type=EventType.SUCCESS,
            agent_id="orchestrator",
            message=f"🎉 Project Complete! Total time: {elapsed:.1f}s",
            timestamp=datetime.now()
        ))
        
    async def run(self):
        """Run the dashboard"""
        # Initialize
        await self.initialize()
        
        # Create layout
        self.layout = self._create_layout()
        self._update_layout()
        
        # Run with Live display
        with Live(self.layout, console=self.console, refresh_per_second=4) as live:
            self.live = live
            
            # Run demo project
            await self.run_demo_project()
            
            # Keep running until interrupted
            self.console.print("\n[bold green]Demo complete! Press Ctrl+C to exit.[/]")
            try:
                await asyncio.Event().wait()
            except KeyboardInterrupt:
                pass
                
        self.console.print("\n[bold magenta]Thank you for using the Theatrical Dashboard![/]")