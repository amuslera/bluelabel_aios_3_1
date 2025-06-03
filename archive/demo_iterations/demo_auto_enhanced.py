#!/usr/bin/env python3
"""
Auto-Enhanced Demo - Starts automatically with chat feature
Press Ctrl+C to stop at any time
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import deque
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich import box
from rich.text import Text
from rich.align import Align

# Add project root to path
sys.path.append(str(Path(__file__).parent))

console = Console()

class AutoEnhancedDemo:
    """Auto-running demo with chat"""
    
    def __init__(self):
        self.console = console
        self.start_time = None
        self.event_log = []
        self.chat_messages = deque(maxlen=12)  # Last 12 messages
        self.current_phase = 0
        
        # Metrics
        self.total_tasks = 20
        self.completed_tasks = 0
        self.total_cost = 0.0
        self.lines_of_code = 0
        self.tests_written = 0
        self.files_created = 0
        
        # Agent info
        self.agents = {
            "marcus": {"name": "Marcus Chen", "color": "yellow", "emoji": "🔧", "short": "M"},
            "emily": {"name": "Emily Rodriguez", "color": "cyan", "emoji": "🎨", "short": "E"},
            "alex": {"name": "Alex Thompson", "color": "green", "emoji": "🧪", "short": "A"},
            "jordan": {"name": "Jordan Kim", "color": "magenta", "emoji": "🚀", "short": "J"}
        }
        
        # Activities and chat messages
        self.phases = [
            {
                "name": "Project Setup",
                "activities": {
                    "marcus": "Analyzing requirements...",
                    "emily": "Setting up React project...",
                    "alex": "Configuring test framework...",
                    "jordan": "Creating Docker setup..."
                },
                "chats": [
                    ("marcus", "I'll start with the database schema"),
                    ("emily", "React + TypeScript initialized"),
                    ("alex", "Jest and Playwright ready"),
                    ("jordan", "Docker environment ready!")
                ],
                "metrics": {"tasks": 4, "files": 8, "loc": 250, "tests": 5, "cost": 0.002}
            },
            {
                "name": "Core Development",
                "activities": {
                    "marcus": "Building API endpoints...",
                    "emily": "Creating components...",
                    "alex": "Writing unit tests...",
                    "jordan": "Setting up CI/CD..."
                },
                "chats": [
                    ("marcus", "User and Task models done"),
                    ("emily", "TaskList component ready"),
                    ("marcus", "@emily API endpoints live!"),
                    ("emily", "Perfect! Connecting now")
                ],
                "metrics": {"tasks": 4, "files": 6, "loc": 850, "tests": 12, "cost": 0.004}
            },
            {
                "name": "Integration",
                "activities": {
                    "marcus": "Adding authentication...",
                    "emily": "Implementing state mgmt...",
                    "alex": "Integration testing...",
                    "jordan": "Configuring k8s..."
                },
                "chats": [
                    ("alex", "Security issue in auth flow"),
                    ("marcus", "Thanks! Fixing now..."),
                    ("jordan", "K8s manifests ready"),
                    ("alex", "All tests green ✅")
                ],
                "metrics": {"tasks": 4, "files": 5, "loc": 650, "tests": 8, "cost": 0.003}
            },
            {
                "name": "Polish & Optimization",
                "activities": {
                    "marcus": "Optimizing queries...",
                    "emily": "Adding dark mode...",
                    "alex": "Performance testing...",
                    "jordan": "Setting up monitoring..."
                },
                "chats": [
                    ("emily", "Dark mode looks great!"),
                    ("alex", "Load tests passing"),
                    ("jordan", "Prometheus configured"),
                    ("marcus", "API response < 100ms")
                ],
                "metrics": {"tasks": 4, "files": 4, "loc": 400, "tests": 6, "cost": 0.002}
            },
            {
                "name": "Final Review",
                "activities": {
                    "marcus": "Writing API docs...",
                    "emily": "Final UI polish...",
                    "alex": "Coverage report...",
                    "jordan": "Production deploy..."
                },
                "chats": [
                    ("alex", "96% test coverage! 🎉"),
                    ("emily", "UI/UX review complete"),
                    ("jordan", "Deployed to prod! 🚀"),
                    ("marcus", "Great work team! 🙌")
                ],
                "metrics": {"tasks": 4, "files": 3, "loc": 200, "tests": 5, "cost": 0.001}
            }
        ]
        
    def add_chat_message(self, agent_id: str, message: str):
        """Add a chat message"""
        agent = self.agents[agent_id]
        self.chat_messages.append(
            f"[{agent['color']}]{agent['emoji']} {agent['short']}[/]: {message}"
        )
        
    def create_layout(self):
        """Create the demo layout"""
        layout = Layout()
        
        # Main structure
        layout.split_column(
            Layout(name="header", size=4),
            Layout(name="main", size=14),
            Layout(name="bottom", size=10)
        )
        
        # Header with project info
        project_info = """[bold cyan]Task Management System[/] - Enterprise-grade task tracking with real-time collaboration
[dim]FastAPI + PostgreSQL | React + TypeScript | Docker + Kubernetes[/]"""
        
        layout["header"].update(Panel(
            Align.center(project_info),
            title="🚀 Project Overview",
            border_style="cyan",
            box=box.ROUNDED
        ))
        
        # Main area: agents + chat
        layout["main"].split_row(
            Layout(name="agents", ratio=3),
            Layout(name="chat", ratio=1)
        )
        
        # Agent panels in 2x2 grid
        layout["agents"].split_column(
            Layout(name="top_agents"),
            Layout(name="bot_agents")
        )
        layout["top_agents"].split_row(
            Layout(name="marcus"),
            Layout(name="emily")
        )
        layout["bot_agents"].split_row(
            Layout(name="alex"),
            Layout(name="jordan")
        )
        
        # Bottom area: progress + stats
        layout["bottom"].split_row(
            Layout(name="progress", ratio=2),
            Layout(name="stats", ratio=1)
        )
        
        return layout
        
    def update_display(self, layout, phase_name="Initializing"):
        """Update all display elements"""
        # Update agent panels
        if self.current_phase < len(self.phases):
            phase = self.phases[self.current_phase]
            activities = phase["activities"]
            phase_name = phase["name"]
        else:
            activities = {agent: "✅ Complete!" for agent in self.agents}
            phase_name = "Completed"
            
        for agent_id, agent_info in self.agents.items():
            if self.current_phase < len(self.phases):
                activity = activities.get(agent_id, "Waiting...")
                status = f"[{agent_info['color']}]{activity}[/]"
            else:
                status = "[green]✅ All tasks complete![/]"
                
            content = f"{status}\n[dim]Phase: {phase_name}[/]"
            
            layout[agent_id].update(Panel(
                content,
                title=f"{agent_info['emoji']} {agent_info['name']}",
                border_style=agent_info['color'],
                height=6
            ))
        
        # Update chat
        chat_content = "\n".join(self.chat_messages) if self.chat_messages else "[dim]Team chat...[/]"
        layout["chat"].update(Panel(
            chat_content,
            title="💬 Team Chat",
            border_style="blue",
            height=12
        ))
        
        # Update progress
        progress = Progress(
            TextColumn("[bold blue]Overall Progress"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn(f"({self.completed_tasks}/{self.total_tasks} tasks)")
        )
        task_id = progress.add_task("", total=self.total_tasks, completed=self.completed_tasks)
        
        # Time display
        if self.start_time:
            elapsed = time.time() - self.start_time
            time_str = str(timedelta(seconds=int(elapsed)))
        else:
            time_str = "00:00:00"
        
        # Current phase info
        phase_info = f"Phase {self.current_phase + 1}/5: {phase_name}" if self.current_phase < len(self.phases) else "All phases complete"
        
        progress_content = f"{progress.make_tasks_table(progress.tasks)}\n\n[cyan]{phase_info}[/]\n[dim]Time: {time_str} | Cost: ${self.total_cost:.4f}[/]"
        
        layout["progress"].update(Panel(
            progress_content,
            title="📊 Progress",
            box=box.ROUNDED,
            height=8
        ))
        
        # Update stats
        stats = Table(box=box.SIMPLE, show_header=False, pad_edge=False)
        stats.add_column("Metric", style="cyan", width=10)
        stats.add_column("Value", style="green", width=8)
        
        stats.add_row("Agents", "4 active")
        stats.add_row("Files", str(self.files_created))
        stats.add_row("Code", f"{self.lines_of_code:,} LOC")
        stats.add_row("Tests", f"{self.tests_written}")
        stats.add_row("Coverage", f"{min(96, self.tests_written * 2)}%")
        
        layout["stats"].update(Panel(
            stats, 
            title="📈 Metrics",
            box=box.ROUNDED,
            height=8
        ))
        
    def run_demo(self):
        """Run the auto demo"""
        self.console.clear()
        
        # Welcome message
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
        
        # Initial chat message
        self.chat_messages.append("[bold green]🚀 Project kickoff![/]")
        self.chat_messages.append("[dim]Team assembled and ready[/]")
        
        # Main demo loop
        try:
            with Live(layout, refresh_per_second=2, console=self.console) as live:
                # Initial display
                self.update_display(layout)
                time.sleep(2)
                
                # Run through phases
                for phase_idx, phase in enumerate(self.phases):
                    self.current_phase = phase_idx
                    
                    # Update display for new phase
                    self.update_display(layout, phase["name"])
                    
                    # Add phase announcement
                    self.chat_messages.append(f"\n[yellow]📋 {phase['name']}[/]")
                    time.sleep(1)
                    
                    # Process chat messages with delays
                    for i, (agent_id, message) in enumerate(phase["chats"]):
                        self.add_chat_message(agent_id, message)
                        self.update_display(layout, phase["name"])
                        time.sleep(1.5)
                        
                        # Update metrics gradually
                        if i % 2 == 0:
                            metrics = phase["metrics"]
                            self.completed_tasks += metrics["tasks"] // 2
                            self.files_created += metrics["files"] // 2
                            self.lines_of_code += metrics["loc"] // 2
                            self.tests_written += metrics["tests"] // 2
                            self.total_cost += metrics["cost"] / 2
                            self.update_display(layout, phase["name"])
                    
                    # Complete phase metrics
                    metrics = phase["metrics"]
                    self.completed_tasks = min(self.total_tasks, self.completed_tasks + metrics["tasks"] // 2)
                    self.files_created += metrics["files"] // 2
                    self.lines_of_code += metrics["loc"] // 2
                    self.tests_written += metrics["tests"] // 2
                    self.total_cost += metrics["cost"] / 2
                    
                    self.update_display(layout, phase["name"])
                    time.sleep(2)
                
                # Mark as complete
                self.current_phase = len(self.phases)
                self.completed_tasks = self.total_tasks
                self.chat_messages.append("\n[bold green]🎉 Project complete![/]")
                self.update_display(layout, "Completed")
                
                # Keep displaying for a bit
                time.sleep(5)
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Demo stopped by user[/]")
            
        # Show summary
        self.console.print()
        duration = timedelta(seconds=int(time.time() - self.start_time))
        
        summary = Panel(
            f"[bold green]✅ Task Management System Complete![/]\n\n"
            f"[cyan]Duration:[/] {duration}\n"
            f"[cyan]Total Cost:[/] ${self.total_cost:.4f}\n"
            f"[cyan]Code Written:[/] {self.lines_of_code:,} lines\n"
            f"[cyan]Test Coverage:[/] {min(96, self.tests_written * 2)}%\n"
            f"[cyan]Files Created:[/] {self.files_created}\n\n"
            f"[dim]The application is ready for deployment![/]",
            title="📊 Final Summary",
            box=box.DOUBLE,
            style="green"
        )
        self.console.print(summary)
        
        # Export log
        filename = f"demo_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump({
                "duration": str(duration),
                "metrics": {
                    "tasks_completed": self.completed_tasks,
                    "total_cost": self.total_cost,
                    "lines_of_code": self.lines_of_code,
                    "test_coverage": min(96, self.tests_written * 2),
                    "files_created": self.files_created
                },
                "events": self.event_log
            }, f, indent=2)
        
        self.console.print(f"\n[dim]Session log saved to: {filename}[/]\n")

def main():
    try:
        demo = AutoEnhancedDemo()
        demo.run_demo()
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/]")

if __name__ == "__main__":
    main()