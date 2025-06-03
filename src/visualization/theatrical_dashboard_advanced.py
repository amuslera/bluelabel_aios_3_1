"""
Advanced Theatrical Dashboard with Real LLM Integration

This version supports real LLM API calls and actual agent task execution,
providing a production-ready monitoring interface.
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.box import ROUNDED, DOUBLE
from collections import deque
import json

from src.visualization.theatrical_adapter import TheatricalOrchestrator, TheatricalEvent, EventType
from src.core.routing.llm_integration import LLMIntegration


class AdvancedTheatricalDashboard:
    """Advanced theatrical dashboard with real LLM integration and enhanced features"""
    
    def __init__(self, max_events: int = 100, max_agent_logs: int = 20):
        self.console = Console()
        self.orchestrator = None
        self.agents_data = {}
        self.event_log = deque(maxlen=max_events)
        self.agent_logs = {}
        self.max_agent_logs = max_agent_logs
        self.start_time = None
        self.project_info = {}
        self.layout = None
        self.live = None
        self.session_data = []  # For export
        
        # Configuration
        self.config = {
            'theatrical_delay': 0.5,  # Delay between events for human comprehension
            'show_raw_llm': False,    # Show raw LLM responses
            'enable_export': True,    # Enable session export
            'theme': 'default'        # Color theme
        }
        
        # Enhanced agent styles with more details
        self.agent_styles = {
            "cto-001": {
                "icon": "🏛️", 
                "color": "magenta", 
                "name": "Sarah Chen",
                "title": "Chief Technology Officer",
                "skills": ["Architecture", "Planning", "Leadership"]
            },
            "backend-001": {
                "icon": "⚙️", 
                "color": "cyan", 
                "name": "Marcus Chen",
                "title": "Senior Backend Engineer",
                "skills": ["FastAPI", "Databases", "Microservices"]
            },
            "frontend-001": {
                "icon": "🎨", 
                "color": "yellow", 
                "name": "Emily Rodriguez",
                "title": "Senior Frontend Engineer",
                "skills": ["React", "UI/UX", "Accessibility"]
            },
            "qa-001": {
                "icon": "🧪", 
                "color": "green", 
                "name": "Alex Thompson",
                "title": "QA Engineering Lead",
                "skills": ["Testing", "Security", "Automation"]
            },
            "devops-001": {
                "icon": "🚀", 
                "color": "blue", 
                "name": "Jordan Kim",
                "title": "DevOps Engineer",
                "skills": ["Kubernetes", "CI/CD", "Cloud"]
            },
            "orchestrator": {
                "icon": "🎬", 
                "color": "white", 
                "name": "System",
                "title": "Orchestration System",
                "skills": ["Coordination", "Monitoring", "Reporting"]
            }
        }
        
    def _event_callback(self, event: TheatricalEvent):
        """Enhanced event callback with session recording"""
        # Record for export
        if self.config['enable_export']:
            self.session_data.append({
                'timestamp': event.timestamp.isoformat(),
                'type': event.type.value,
                'agent_id': event.agent_id,
                'message': event.message,
                'details': event.details,
                'cost': event.cost,
                'tokens': event.tokens
            })
        
        # Add to logs
        self.event_log.append(event)
        
        agent_id = event.agent_id
        if agent_id not in self.agent_logs:
            self.agent_logs[agent_id] = deque(maxlen=self.max_agent_logs)
        self.agent_logs[agent_id].append(event)
        
        # Update agent status with more details
        if agent_id in self.agents_data:
            agent = self.agents_data[agent_id]
            
            if event.type == EventType.THINK:
                agent['status'] = '🤔 Thinking'
                agent['current_task'] = event.message.replace('💭 Analyzing: ', '')
            elif event.type == EventType.WORK:
                agent['status'] = '⚙️ Working'
                agent['progress'] = event.progress
            elif event.type == EventType.SUCCESS:
                agent['status'] = '✅ Ready'
                agent['tasks_completed'] += 1
                agent['total_cost'] += event.cost
                agent['total_tokens'] += event.tokens
                agent['last_task'] = agent.get('current_task', 'Unknown')
                agent['current_task'] = None
            elif event.type == EventType.ERROR:
                agent['status'] = '❌ Error'
                agent['errors'] += 1
            elif event.type == EventType.COST:
                agent['total_cost'] += event.cost
                agent['total_tokens'] += event.tokens
            else:
                agent['status'] = '⚪ Idle'
                
        # Refresh display
        if self.layout:
            self._update_layout()
            
    def _create_layout(self):
        """Create enhanced dashboard layout"""
        layout = Layout()
        
        # Main structure with more sections
        layout.split_column(
            Layout(name="header", size=4),
            Layout(name="body"),
            Layout(name="footer", size=4)
        )
        
        # Body with three columns
        layout["body"].split_row(
            Layout(name="agents", ratio=3),
            Layout(name="sidebar", ratio=1)
        )
        
        # Sidebar with timeline and controls
        layout["sidebar"].split_column(
            Layout(name="timeline", ratio=3),
            Layout(name="controls", ratio=1)
        )
        
        return layout
        
    def _create_header(self) -> Panel:
        """Create enhanced header panel"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        # Create header table
        header_table = Table(show_header=False, box=None, expand=True)
        header_table.add_column("", style="bold magenta")
        header_table.add_column("", justify="right")
        
        # Title row
        header_table.add_row(
            "🎭 AIOSv3.1 Theatrical Dashboard - Advanced Mode",
            f"[cyan]Elapsed: {elapsed:.1f}s[/]"
        )
        
        # Project row
        if self.project_info:
            header_table.add_row(
                f"[yellow]Project: {self.project_info.get('name', 'N/A')}[/]",
                f"[dim]{self.project_info.get('description', '')}[/]"
            )
            
        return Panel(header_table, box=DOUBLE, style="bright_white")
        
    def _create_agent_panel(self, agent_id: str) -> Panel:
        """Create enhanced agent panel with more details"""
        agent = self.agents_data.get(agent_id, {})
        style_info = self.agent_styles.get(agent_id, {})
        
        # Create content sections
        content = []
        
        # Header with name and title
        header = Text()
        header.append(f"{style_info.get('icon', '❓')} {agent.get('name', 'Unknown')}\n", 
                     style=f"bold {style_info.get('color', 'white')}")
        header.append(f"{style_info.get('title', 'Agent')}\n", style="italic dim")
        header.append(f"Status: {agent.get('status', '⚪ Idle')}", style="dim")
        content.append(header)
        
        # Current task
        if agent.get('current_task'):
            content.append(f"\n[bold]Current Task:[/]\n{agent['current_task']}")
            
        # Skills
        if style_info.get('skills'):
            skills_text = " • ".join(style_info['skills'])
            content.append(f"\n[dim]Skills: {skills_text}[/]")
        
        # Activity log
        if agent_id in self.agent_logs:
            content.append("\n[bold]Recent Activity:[/]")
            for event in list(self.agent_logs[agent_id])[-5:]:
                timestamp = event.timestamp.strftime("%H:%M:%S")
                # Clean up message for display
                msg = event.message
                for prefix in ['💭 Analyzing: ', '⚙️ Implementing: ', '✅ Completed: ']:
                    msg = msg.replace(prefix, '')
                content.append(f"[dim]{timestamp}[/] {msg[:50]}...")
        
        # Metrics with better formatting
        metrics_table = Table(show_header=False, box=None, padding=(0, 1))
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="yellow", justify="right")
        
        metrics_table.add_row("Tasks", str(agent.get('tasks_completed', 0)))
        metrics_table.add_row("Cost", f"${agent.get('total_cost', 0):.4f}")
        metrics_table.add_row("Tokens", f"{agent.get('total_tokens', 0):,}")
        if agent.get('errors', 0) > 0:
            metrics_table.add_row("Errors", str(agent['errors']))
            
        content.append("")
        content.append(metrics_table)
        
        # Combine all content
        panel_content = "\n".join(str(c) for c in content)
        
        # Determine border style based on status
        border_style = style_info.get('color', 'white')
        if '⚙️ Working' in agent.get('status', ''):
            border_style = f"bold {border_style}"
        elif '❌ Error' in agent.get('status', ''):
            border_style = "bold red"
            
        return Panel(
            panel_content,
            title=f"[{style_info.get('color', 'white')}]{agent.get('role', 'Agent')}[/]",
            box=ROUNDED,
            style=border_style,
            height=15
        )
        
    def _create_agents_grid(self) -> Layout:
        """Create responsive grid of agent panels"""
        grid = Layout()
        
        # Create 2x3 grid
        grid.split_column(
            Layout(name="row1"),
            Layout(name="row2")
        )
        
        # Arrange agents logically
        grid["row1"].split_row(
            Layout(self._create_agent_panel("cto-001")),
            Layout(self._create_agent_panel("backend-001")),
            Layout(self._create_agent_panel("frontend-001"))
        )
        
        grid["row2"].split_row(
            Layout(self._create_agent_panel("qa-001")),
            Layout(self._create_agent_panel("devops-001")),
            Layout(self._create_system_panel())
        )
        
        return grid
        
    def _create_timeline(self) -> Panel:
        """Create enhanced timeline with filtering"""
        timeline_text = Text()
        timeline_text.append("📜 Event Timeline\n", style="bold yellow")
        
        # Group events by type
        event_groups = {
            'system': [],
            'thinking': [],
            'working': [],
            'success': [],
            'error': []
        }
        
        for event in list(self.event_log)[-30:]:
            if event.type in [EventType.INIT, EventType.PROJECT, EventType.PHASE]:
                event_groups['system'].append(event)
            elif event.type == EventType.THINK:
                event_groups['thinking'].append(event)
            elif event.type == EventType.WORK:
                event_groups['working'].append(event)
            elif event.type == EventType.SUCCESS:
                event_groups['success'].append(event)
            elif event.type == EventType.ERROR:
                event_groups['error'].append(event)
                
        # Display recent events
        for event in list(self.event_log)[-15:]:
            style_info = self.agent_styles.get(event.agent_id, {})
            timestamp = event.timestamp.strftime("%H:%M:%S")
            
            # Format based on event type
            if event.type == EventType.SUCCESS:
                timeline_text.append(f"{timestamp} ✅ ", style="dim")
            elif event.type == EventType.ERROR:
                timeline_text.append(f"{timestamp} ❌ ", style="dim")
            else:
                timeline_text.append(f"{timestamp} {style_info.get('icon', '❓')} ", style="dim")
                
            # Add message with appropriate styling
            msg_style = style_info.get('color', 'white')
            if event.type == EventType.ERROR:
                msg_style = "red"
            elif event.type == EventType.SUCCESS:
                msg_style = "green"
                
            timeline_text.append(f"{event.message[:60]}...\n", style=msg_style)
            
        return Panel(timeline_text, title="Event Log", box=ROUNDED, style="cyan")
        
    def _create_system_panel(self) -> Panel:
        """Create system overview panel"""
        content = []
        
        # System header
        header = Text()
        header.append("🎮 System Overview\n", style="bold white")
        header.append("Real-time Orchestration Status", style="italic dim")
        content.append(header)
        content.append("")
        
        # Active agents
        active_count = sum(1 for a in self.agents_data.values() 
                          if a.get('status') not in ['⚪ Idle', None])
        content.append(f"[cyan]Active Agents:[/] {active_count}/{len(self.agents_data)}")
        
        # System metrics
        total_tasks = sum(a.get('tasks_completed', 0) for a in self.agents_data.values())
        total_cost = sum(a.get('total_cost', 0) for a in self.agents_data.values())
        total_tokens = sum(a.get('total_tokens', 0) for a in self.agents_data.values())
        total_errors = sum(a.get('errors', 0) for a in self.agents_data.values())
        
        metrics = Table(show_header=False, box=None, padding=(0, 1))
        metrics.add_column("Metric", style="cyan")
        metrics.add_column("Value", style="yellow", justify="right")
        
        metrics.add_row("Total Tasks", str(total_tasks))
        metrics.add_row("Total Cost", f"${total_cost:.4f}")
        metrics.add_row("Total Tokens", f"{total_tokens:,}")
        if total_errors > 0:
            metrics.add_row("Total Errors", str(total_errors))
        
        content.append("")
        content.append(metrics)
        
        # LLM routing info
        if self.orchestrator and hasattr(self.orchestrator, 'llm_integration'):
            content.append("\n[bold]LLM Routing:[/]")
            content.append("[dim]Primary: Claude 3.5 Sonnet[/]")
            content.append("[dim]Fallback: GPT-4[/]")
            content.append("[dim]Cost Mode: Optimized[/]")
        
        # Session info
        if self.config['enable_export']:
            content.append(f"\n[dim]Session recording: {len(self.session_data)} events[/]")
        
        panel_content = "\n".join(str(c) for c in content)
        
        return Panel(
            panel_content,
            title="[white]System Control[/]",
            box=ROUNDED,
            style="white",
            height=15
        )
        
    def _create_controls(self) -> Panel:
        """Create control panel"""
        controls = Table(show_header=False, box=None)
        controls.add_column("Key", style="bold yellow")
        controls.add_column("Action", style="dim")
        
        controls.add_row("Q", "Quit")
        controls.add_row("E", "Export Session")
        controls.add_row("C", "Clear Logs")
        controls.add_row("T", "Toggle Theme")
        controls.add_row("P", "Pause/Resume")
        
        return Panel(controls, title="Controls", box=ROUNDED, style="dim")
        
    def _create_footer(self) -> Panel:
        """Create footer with status and tips"""
        footer_table = Table(show_header=False, box=None, expand=True)
        footer_table.add_column("", style="dim")
        footer_table.add_column("", justify="right", style="dim")
        
        # Status row
        status = "🟢 Live" if self.live else "⚪ Ready"
        mode = "Advanced Mode" if self.config.get('show_raw_llm') else "Standard Mode"
        footer_table.add_row(
            f"Status: {status} | Mode: {mode}",
            "Press 'Q' to quit"
        )
        
        # Tip row
        tips = [
            "Agents work collaboratively to deliver projects",
            "Each agent has specialized skills and personality",
            "Real LLM calls are made for authentic responses",
            "Sessions can be exported for analysis"
        ]
        import random
        tip = random.choice(tips)
        footer_table.add_row(f"💡 Tip: {tip}", "v3.1 Advanced")
        
        return Panel(footer_table, box=ROUNDED, style="dim")
        
    def _update_layout(self):
        """Update the entire layout"""
        if not self.layout:
            return
            
        self.layout["header"].update(self._create_header())
        self.layout["agents"].update(self._create_agents_grid())
        self.layout["timeline"].update(self._create_timeline())
        self.layout["controls"].update(self._create_controls())
        self.layout["footer"].update(self._create_footer())
        
    async def export_session(self, filename: Optional[str] = None):
        """Export session data to JSON"""
        if not self.config['enable_export'] or not self.session_data:
            return
            
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/sessions/theatrical_session_{timestamp}.json"
            
        # Create directory if needed
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Prepare export data
        export_data = {
            'session_info': {
                'start_time': self.start_time,
                'project': self.project_info,
                'config': self.config,
                'duration': time.time() - self.start_time if self.start_time else 0
            },
            'agents': {
                agent_id: {
                    'name': data.get('name'),
                    'role': data.get('role'),
                    'tasks_completed': data.get('tasks_completed', 0),
                    'total_cost': data.get('total_cost', 0),
                    'total_tokens': data.get('total_tokens', 0),
                    'errors': data.get('errors', 0)
                }
                for agent_id, data in self.agents_data.items()
            },
            'events': self.session_data
        }
        
        # Write to file
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        self.console.print(f"\n[green]✅ Session exported to: {filename}[/]")
        
    async def initialize(self):
        """Initialize the dashboard and orchestrator"""
        self.console.print("[bold magenta]🎭 Initializing Advanced Theatrical Dashboard...[/]")
        
        # Create orchestrator
        self.orchestrator = TheatricalOrchestrator(event_callback=self._event_callback)
        
        # Initialize agents
        await self.orchestrator.initialize()
        
        # Initialize agent data with more fields
        for agent_id, adapter in self.orchestrator.agents.items():
            style_info = self.agent_styles.get(agent_id, {})
            self.agents_data[agent_id] = {
                'name': adapter.agent_name,
                'role': style_info.get('name', 'Agent'),
                'status': '⚪ Idle',
                'tasks_completed': 0,
                'total_cost': 0.0,
                'total_tokens': 0,
                'progress': 0.0,
                'errors': 0,
                'current_task': None,
                'last_task': None
            }
            
    async def run_custom_project(self, project_name: str, phases: List[Dict[str, Any]]):
        """Run a custom project with defined phases"""
        self.start_time = time.time()
        self.project_info = {'name': project_name}
        
        await self.orchestrator.start_project(project_name, "")
        
        for phase in phases:
            await self.orchestrator.run_phase(
                phase['name'],
                phase['agent_id'],
                phase['tasks']
            )
            
            # Theatrical delay
            await asyncio.sleep(self.config['theatrical_delay'])
            
    async def run_demo_project(self):
        """Run the standard demo project"""
        phases = [
            {
                'name': 'Phase 1: Architecture & Planning',
                'agent_id': 'cto-001',
                'tasks': [
                    'Analyze project requirements',
                    'Create technical specification',
                    'Define system architecture',
                    'Plan development phases'
                ]
            },
            {
                'name': 'Phase 2: Backend Development',
                'agent_id': 'backend-001',
                'tasks': [
                    'Set up FastAPI project structure',
                    'Implement WebSocket handlers',
                    'Create authentication system',
                    'Design database schema',
                    'Build API endpoints'
                ]
            },
            {
                'name': 'Phase 3: Frontend Development',
                'agent_id': 'frontend-001',
                'tasks': [
                    'Create React project structure',
                    'Build chat UI components',
                    'Implement WebSocket client',
                    'Add authentication flow',
                    'Ensure accessibility compliance'
                ]
            },
            {
                'name': 'Phase 4: Quality Assurance',
                'agent_id': 'qa-001',
                'tasks': [
                    'Write unit tests for backend',
                    'Create integration tests',
                    'Test WebSocket connections',
                    'Perform security audit',
                    'Load testing and optimization'
                ]
            },
            {
                'name': 'Phase 5: Deployment & Infrastructure',
                'agent_id': 'devops-001',
                'tasks': [
                    'Create Docker containers',
                    'Set up CI/CD pipeline',
                    'Configure Kubernetes',
                    'Set up monitoring',
                    'Deploy to cloud'
                ]
            }
        ]
        
        await self.run_custom_project('Real-time Chat Application', phases)
        
        # Project complete
        elapsed = time.time() - self.start_time
        self._event_callback(TheatricalEvent(
            type=EventType.SUCCESS,
            agent_id="orchestrator",
            message=f"🎉 Project Complete! Total time: {elapsed:.1f}s",
            timestamp=datetime.now()
        ))
        
    async def run(self, demo_mode: bool = True):
        """Run the advanced dashboard"""
        # Initialize
        await self.initialize()
        
        # Create layout
        self.layout = self._create_layout()
        self._update_layout()
        
        # Run with Live display
        with Live(self.layout, console=self.console, refresh_per_second=4) as live:
            self.live = live
            
            # Run project
            if demo_mode:
                await self.run_demo_project()
            else:
                # Wait for custom project commands
                self.console.print("\n[yellow]Dashboard ready. Configure and start your project.[/]")
                
            # Export session automatically
            if self.config['enable_export']:
                await self.export_session()
                
            # Keep running
            self.console.print("\n[bold green]Session complete! Press Ctrl+C to exit.[/]")
            try:
                await asyncio.Event().wait()
            except KeyboardInterrupt:
                pass
                
        self.console.print("\n[bold magenta]Thank you for using the Advanced Theatrical Dashboard![/]")