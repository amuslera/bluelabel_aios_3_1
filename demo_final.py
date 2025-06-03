#!/usr/bin/env python3
"""
Final Demo - Professional layout with all requested fixes
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import deque
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn
from rich.layout import Layout
from rich.live import Live
from rich import box
from rich.text import Text
from rich.align import Align

# Add project root to path
sys.path.append(str(Path(__file__).parent))

console = Console()

class FinalDemo:
    """Final demo with professional layout"""
    
    def __init__(self):
        self.console = console
        self.start_time = None
        self.event_log = []
        self.chat_messages = deque(maxlen=50)  # Keep more history
        self.current_phase = 0
        
        # Metrics
        self.total_tasks = 20
        self.completed_tasks = 0
        self.total_cost = 0.0
        self.lines_of_code = 0
        self.tests_written = 0
        self.files_created = 0
        
        # Agent info with roles
        self.agents = {
            "marcus": {
                "name": "Marcus Chen",
                "role": "Backend Engineer", 
                "color": "yellow",
                "initials": "MC"
            },
            "emily": {
                "name": "Emily Rodriguez",
                "role": "Frontend Developer",
                "color": "cyan",
                "initials": "ER"
            },
            "alex": {
                "name": "Alex Thompson",
                "role": "QA Engineer",
                "color": "green",
                "initials": "AT"
            },
            "jordan": {
                "name": "Jordan Kim",
                "role": "DevOps Engineer",
                "color": "magenta",
                "initials": "JK"
            }
        }
        
        # Phases with activities and chats
        self.phases = [
            {
                "name": "Project Setup",
                "activities": {
                    "marcus": "Analyzing requirements and designing API structure",
                    "emily": "Setting up React project with TypeScript",
                    "alex": "Configuring Jest and Playwright frameworks",
                    "jordan": "Creating Docker containers and compose setup"
                },
                "chats": [
                    ("marcus", "I'll start with the database schema and API design"),
                    ("emily", "React + TypeScript initialized with routing"),
                    ("alex", "Test frameworks configured and ready"),
                    ("jordan", "Docker environment is up and running!")
                ],
                "metrics": {"tasks": 4, "files": 8, "loc": 250, "tests": 5, "cost": 0.002}
            },
            {
                "name": "Core Development",
                "activities": {
                    "marcus": "Building REST API endpoints with FastAPI",
                    "emily": "Creating reusable UI components",
                    "alex": "Writing unit tests for models and utils",
                    "jordan": "Setting up GitHub Actions CI/CD pipeline"
                },
                "chats": [
                    ("marcus", "User and Task models implemented with SQLAlchemy"),
                    ("emily", "TaskList and TaskForm components ready"),
                    ("marcus", "@emily API endpoints are live at /api/v1/*"),
                    ("emily", "Perfect! Integrating with the API now"),
                    ("jordan", "CI pipeline configured with automated tests")
                ],
                "metrics": {"tasks": 4, "files": 12, "loc": 850, "tests": 12, "cost": 0.004}
            },
            {
                "name": "Integration & Auth",
                "activities": {
                    "marcus": "Implementing JWT authentication system",
                    "emily": "Adding Redux for state management",
                    "alex": "Creating integration test suite",
                    "jordan": "Configuring Kubernetes manifests"
                },
                "chats": [
                    ("alex", "Found security issue in auth flow - token expiry"),
                    ("marcus", "Good catch! Implementing refresh tokens now"),
                    ("emily", "Redux store connected with auth state"),
                    ("jordan", "K8s deployments and services ready"),
                    ("alex", "All integration tests passing ✅")
                ],
                "metrics": {"tasks": 4, "files": 8, "loc": 650, "tests": 15, "cost": 0.003}
            },
            {
                "name": "Polish & Performance",
                "activities": {
                    "marcus": "Optimizing database queries and caching",
                    "emily": "Implementing dark mode and animations",
                    "alex": "Running performance and load tests",
                    "jordan": "Setting up Prometheus monitoring"
                },
                "chats": [
                    ("emily", "Dark mode toggle working beautifully"),
                    ("alex", "Load tests show <100ms response times"),
                    ("jordan", "Monitoring dashboards configured"),
                    ("marcus", "Added Redis caching for frequent queries"),
                    ("alex", "Performance benchmarks all green!")
                ],
                "metrics": {"tasks": 4, "files": 6, "loc": 400, "tests": 10, "cost": 0.002}
            },
            {
                "name": "Final Review & Deploy",
                "activities": {
                    "marcus": "Writing OpenAPI documentation",
                    "emily": "Final UI/UX polish and accessibility",
                    "alex": "Generating test coverage reports",
                    "jordan": "Deploying to production cluster"
                },
                "chats": [
                    ("alex", "96% test coverage achieved! 🎉"),
                    ("emily", "Accessibility audit passed - WCAG 2.1 AA"),
                    ("jordan", "Deployed to production successfully! 🚀"),
                    ("marcus", "API docs available at /docs"),
                    ("alex", "All systems operational and monitored"),
                    ("marcus", "Great teamwork everyone! 🙌")
                ],
                "metrics": {"tasks": 4, "files": 4, "loc": 200, "tests": 8, "cost": 0.001}
            }
        ]
        
    def add_chat_message(self, agent_id: str, message: str):
        """Add a chat message with initials"""
        agent = self.agents[agent_id]
        self.chat_messages.append(
            f"[{agent['color']}]{agent['initials']}[/]: {message}"
        )
        
    def create_layout(self):
        """Create the demo layout with dynamic sizing"""
        layout = Layout()
        
        # Get console height for dynamic sizing
        console_height = self.console.height
        
        # Calculate sizes dynamically
        header_size = 4
        footer_size = 0  # No footer during demo
        main_size = console_height - header_size - footer_size - 3  # Leave some margin
        
        # Main structure
        layout.split_column(
            Layout(name="header", size=header_size),
            Layout(name="main", size=main_size)
        )
        
        # Header
        project_info = """[bold cyan]Task Management System[/] - Enterprise-grade task tracking with real-time collaboration
[dim]FastAPI + PostgreSQL | React + TypeScript | Docker + Kubernetes[/]"""
        
        layout["header"].update(Panel(
            Align.center(project_info),
            title="🚀 Project Overview",
            border_style="cyan",
            box=box.ROUNDED
        ))
        
        # Main area split: 3/4 for agents+metrics, 1/4 for chat
        layout["main"].split_row(
            Layout(name="left_area", ratio=3),
            Layout(name="chat", ratio=1)
        )
        
        # Left area: agents on top, metrics on bottom
        agents_height = int(main_size * 0.7)  # 70% for agents
        metrics_height = main_size - agents_height  # Rest for metrics
        
        layout["left_area"].split_column(
            Layout(name="agents_area", size=agents_height),
            Layout(name="bottom_area", size=metrics_height)
        )
        
        # Agents in 2x2 grid
        layout["agents_area"].split_column(
            Layout(name="top_row"),
            Layout(name="bottom_row")
        )
        
        layout["top_row"].split_row(
            Layout(name="marcus"),
            Layout(name="emily")
        )
        
        layout["bottom_row"].split_row(
            Layout(name="alex"),
            Layout(name="jordan")
        )
        
        # Bottom area: metrics and progress
        layout["bottom_area"].split_row(
            Layout(name="metrics", ratio=1),
            Layout(name="progress", ratio=2)
        )
        
        return layout
        
    def create_progress_bar(self):
        """Create a clean progress bar"""
        progress = Progress(
            TextColumn("[bold blue]Overall Progress", justify="left"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            TextColumn("• {task.fields[info]}", justify="left"),
            expand=False
        )
        
        task_id = progress.add_task(
            "progress",
            total=self.total_tasks,
            completed=self.completed_tasks,
            info=f"{self.completed_tasks}/{self.total_tasks} tasks"
        )
        
        return progress
        
    def update_display(self, layout, phase_name="Initializing"):
        """Update all display elements"""
        # Update agent panels
        if self.current_phase < len(self.phases):
            phase = self.phases[self.current_phase]
            activities = phase["activities"]
            phase_name = phase["name"]
        else:
            activities = {agent: "✅ All tasks complete!" for agent in self.agents}
            phase_name = "Completed"
            
        for agent_id, agent_info in self.agents.items():
            if self.current_phase < len(self.phases):
                activity = activities.get(agent_id, "Waiting...")
                status = f"[{agent_info['color']}]{activity}[/]"
            else:
                status = "[green]✅ All tasks complete![/]"
                
            content = f"{status}\n\n[dim]Phase: {phase_name}[/]"
            
            # Agent panel with name and role
            layout[agent_id].update(Panel(
                Align.left(content, vertical="top"),
                title=f"[{agent_info['color']}]{agent_info['name']}[/] • {agent_info['role']}",
                border_style=agent_info['color'],
                box=box.ROUNDED,
                padding=(1, 1)
            ))
        
        # Update chat with all messages
        chat_lines = list(self.chat_messages)[-30:]  # Show last 30 messages
        chat_content = "\n".join(chat_lines) if chat_lines else "[dim]Team chat starting...[/]"
        
        layout["chat"].update(Panel(
            Align.left(chat_content, vertical="top"),
            title="💬 Team Chat",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1)
        ))
        
        # Update metrics
        metrics_table = Table(box=None, show_header=False, padding=(0, 1))
        metrics_table.add_column("Metric", style="cyan", no_wrap=True)
        metrics_table.add_column("Value", style="green")
        
        metrics_table.add_row("Agents", "4 active")
        metrics_table.add_row("Files", str(self.files_created))
        metrics_table.add_row("Code", f"{self.lines_of_code:,} LOC")
        metrics_table.add_row("Tests", f"{self.tests_written}")
        metrics_table.add_row("Coverage", f"{min(96, self.tests_written * 2)}%")
        
        layout["metrics"].update(Panel(
            Align.center(metrics_table, vertical="middle"),
            title="📈 Metrics",
            box=box.ROUNDED
        ))
        
        # Update progress
        # Time and phase info
        if self.start_time:
            elapsed = time.time() - self.start_time
            time_str = str(timedelta(seconds=int(elapsed)))
        else:
            time_str = "00:00:00"
        
        # Create progress bar
        progress_bar = Progress(
            TextColumn("[bold blue]Overall Progress", justify="left"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            expand=False
        )
        
        progress_bar.add_task(
            "progress",
            total=self.total_tasks,
            completed=self.completed_tasks
        )
        
        # Build progress content
        phase_info = f"Phase {self.current_phase + 1}/5: {phase_name}" if self.current_phase < len(self.phases) else "All phases complete"
        time_info = f"Time: {time_str} | Cost: ${self.total_cost:.4f}"
        
        # Check if demo is complete
        if self.current_phase >= len(self.phases) and self.completed_tasks == self.total_tasks:
            # Show final summary in progress box
            duration = timedelta(seconds=int(time.time() - self.start_time))
            summary_text = Text()
            summary_text.append("✅ Task Management System Complete!\n\n", style="bold green")
            summary_text.append(f"Duration: {duration}\n", style="cyan")
            summary_text.append(f"Total Cost: ${self.total_cost:.4f}\n", style="cyan")
            summary_text.append(f"Code Written: {self.lines_of_code:,} lines\n", style="cyan")
            summary_text.append(f"Test Coverage: {min(96, self.tests_written * 2)}%\n", style="cyan")
            summary_text.append(f"Files Created: {self.files_created}\n\n", style="cyan")
            summary_text.append("Ready for deployment!", style="dim")
            
            layout["progress"].update(Panel(
                summary_text,
                title="📊 Final Summary",
                box=box.ROUNDED
            ))
        else:
            # Regular progress display
            progress_content = Group(
                progress_bar,
                Text(f"\n{phase_info}", style="cyan"),
                Text(f"{time_info}", style="dim")
            )
            
            layout["progress"].update(Panel(
                progress_content,
                title="📊 Progress",
                box=box.ROUNDED
            ))
        
    def run_demo(self):
        """Run the final demo"""
        self.console.clear()
        
        # Welcome
        welcome = Panel(
            Align.center(
                "[bold cyan]AIOSv3.1 Demo - AI Development Team[/]\n\n"
                "[white]Watch our AI agents collaborate to build a complete application[/]\n"
                "[dim]Demo will start automatically in 3 seconds...[/]"
            ),
            box=box.DOUBLE,
            style="cyan"
        )
        self.console.print(welcome)
        time.sleep(3)
        
        self.console.clear()
        self.start_time = time.time()
        
        # Create layout
        layout = self.create_layout()
        
        # Initial messages
        self.chat_messages.append("[bold green]🚀 Project kickoff![/]")
        self.chat_messages.append("[dim]━━━━━━━━━━━━━━━━━━━━[/]")
        
        try:
            with Live(layout, refresh_per_second=2, console=self.console) as live:
                # Initial display
                self.update_display(layout)
                time.sleep(2)
                
                # Run phases
                for phase_idx, phase in enumerate(self.phases):
                    self.current_phase = phase_idx
                    
                    # Phase announcement
                    self.chat_messages.append(f"\n[bold yellow]>>> {phase['name']} <<<[/]")
                    self.update_display(layout, phase["name"])
                    time.sleep(1)
                    
                    # Process chats
                    for i, (agent_id, message) in enumerate(phase["chats"]):
                        self.add_chat_message(agent_id, message)
                        
                        # Update metrics gradually
                        if i % 2 == 0:
                            metrics = phase["metrics"]
                            self.completed_tasks = min(self.total_tasks, 
                                self.completed_tasks + metrics["tasks"] // 2)
                            self.files_created += metrics["files"] // 2
                            self.lines_of_code += metrics["loc"] // 2
                            self.tests_written += metrics["tests"] // 2
                            self.total_cost += metrics["cost"] / 2
                            
                        self.update_display(layout, phase["name"])
                        time.sleep(1.5)
                    
                    # Complete phase
                    metrics = phase["metrics"]
                    self.completed_tasks = min(self.total_tasks, 
                        self.completed_tasks + metrics["tasks"] // 2)
                    self.files_created += metrics["files"] // 2
                    self.lines_of_code += metrics["loc"] // 2
                    self.tests_written += metrics["tests"] // 2
                    self.total_cost += metrics["cost"] / 2
                    
                    self.update_display(layout, phase["name"])
                    time.sleep(2)
                
                # Complete
                self.current_phase = len(self.phases)
                self.completed_tasks = self.total_tasks
                self.chat_messages.append("\n[bold green]🎉 Project complete![/]")
                self.update_display(layout, "Completed")
                
                # Keep showing for a bit longer to see the summary
                time.sleep(5)
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Demo stopped by user[/]")

def main():
    try:
        demo = FinalDemo()
        demo.run_demo()
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/]")

if __name__ == "__main__":
    main()