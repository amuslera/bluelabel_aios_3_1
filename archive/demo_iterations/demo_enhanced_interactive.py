#!/usr/bin/env python3
"""
Enhanced Interactive Demo - Professional AIOSv3.1 showcase with full UX
"""

import sys
import time
import json
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.layout import Layout
from rich.live import Live
from rich import box
from rich.text import Text
from rich.align import Align

# Add project root to path
sys.path.append(str(Path(__file__).parent))

console = Console()

class DemoState(Enum):
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"

@dataclass
class DemoMetrics:
    """Track demo metrics"""
    total_tasks: int = 16
    assigned_tasks: int = 0
    completed_tasks: int = 0
    total_cost: float = 0.0
    elapsed_time: float = 0.0
    agents_used: int = 4
    files_created: int = 0
    lines_of_code: int = 0
    tests_written: int = 0
    
@dataclass
class AgentActivity:
    """Track individual agent activities"""
    name: str
    color: str
    current_task: str = "Idle"
    tasks_completed: int = 0
    
class InteractiveDemoController:
    """Controls the interactive demo experience"""
    
    def __init__(self):
        self.state = DemoState.READY
        self.metrics = DemoMetrics()
        self.event_log = []
        self.start_time = None
        self.layout = None
        self.live = None
        self.keyboard_thread = None
        self.running = True
        
        # Agent definitions
        self.agents = {
            "marcus": AgentActivity("Marcus Chen", "yellow"),
            "emily": AgentActivity("Emily Rodriguez", "cyan"),
            "alex": AgentActivity("Alex Thompson", "green"),
            "jordan": AgentActivity("Jordan Kim", "magenta")
        }
        
        # Task sequences for each agent
        self.task_sequences = {
            "marcus": [
                "Analyzing requirements",
                "Designing database schema",
                "Creating User and Task models",
                "Building authentication system",
                "Implementing CRUD endpoints",
                "Adding JWT middleware",
                "Writing API documentation"
            ],
            "emily": [
                "Setting up React project",
                "Creating component architecture", 
                "Building TaskList component",
                "Implementing TaskForm",
                "Adding state management",
                "Styling with Tailwind CSS",
                "Making responsive layouts"
            ],
            "alex": [
                "Setting up test framework",
                "Writing model unit tests",
                "Testing API endpoints",
                "Creating integration tests",
                "Building E2E test suite",
                "Running security scans",
                "Generating coverage report"
            ],
            "jordan": [
                "Creating Dockerfile",
                "Setting up docker-compose",
                "Configuring nginx proxy",
                "Building CI/CD pipeline",
                "Setting up monitoring",
                "Creating deployment scripts",
                "Preparing production config"
            ]
        }
        
    def create_layout(self):
        """Create the demo layout"""
        self.layout = Layout()
        
        # Main structure
        self.layout.split_column(
            Layout(name="header", size=6),
            Layout(name="agents", size=12),
            Layout(name="metrics", size=10),
            Layout(name="footer", size=3)
        )
        
        # Header with project info
        project_info = Panel(
            Align.center(
                Text.from_markup(
                    "[bold cyan]Task Management System[/]\n"
                    "[white]Building a complete web application with authentication, "
                    "RESTful API, React frontend, and Docker deployment[/]\n"
                    "[dim]4 AI agents collaborating to deliver production-ready code[/]"
                ),
                vertical="middle"
            ),
            title="🚀 Project Overview",
            border_style="cyan",
            box=box.DOUBLE
        )
        self.layout["header"].update(project_info)
        
        # Agent panels
        self.layout["agents"].split_row(
            Layout(name="marcus_panel"),
            Layout(name="emily_panel"),
            Layout(name="alex_panel"),
            Layout(name="jordan_panel")
        )
        
        # Metrics section
        self.layout["metrics"].split_row(
            Layout(name="progress", ratio=2),
            Layout(name="stats", ratio=1)
        )
        
        # Footer with controls
        self.update_footer()
        
    def update_footer(self):
        """Update footer with current controls"""
        if self.state == DemoState.READY:
            controls = "[s] Start Demo  [q] Quit"
        elif self.state == DemoState.RUNNING:
            controls = "[p] Pause  [r] Reset  [e] Export Log  [q] Quit"
        elif self.state == DemoState.PAUSED:
            controls = "[s] Resume  [r] Reset  [e] Export Log  [q] Quit"
        else:  # COMPLETED
            controls = "[r] Reset  [e] Export Log  [v] View Summary  [q] Quit"
            
        footer = Panel(
            Align.center(f"[bold]{controls}[/]"),
            style="dim",
            box=box.ROUNDED
        )
        self.layout["footer"].update(footer)
        
    def update_agent_panel(self, agent_id: str):
        """Update an individual agent panel"""
        agent = self.agents[agent_id]
        
        content = f"[{agent.color}]{agent.current_task}[/]\n\n"
        content += f"[dim]Tasks completed: {agent.tasks_completed}[/]"
        
        panel = Panel(
            content,
            title=f"[bold {agent.color}]{agent.name}[/]",
            border_style=agent.color,
            height=8
        )
        
        self.layout[f"{agent_id}_panel"].update(panel)
        
    def update_metrics(self):
        """Update the metrics display"""
        # Progress section
        progress_layout = Layout()
        progress_layout.split_column(
            Layout(name="task_progress", size=4),
            Layout(name="time_cost", size=4)
        )
        
        # Task progress bar
        task_progress = Progress(
            TextColumn("[bold blue]Task Progress"),
            BarColumn(bar_width=None),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn(f"{self.metrics.completed_tasks}/{self.metrics.total_tasks} tasks")
        )
        task_id = task_progress.add_task("Tasks", total=self.metrics.total_tasks, completed=self.metrics.completed_tasks)
        
        progress_panel = Panel(task_progress, box=box.ROUNDED)
        progress_layout["task_progress"].update(progress_panel)
        
        # Time and cost info
        if self.start_time:
            elapsed = time.time() - self.start_time
            time_str = str(timedelta(seconds=int(elapsed)))
        else:
            time_str = "00:00:00"
            
        time_cost_info = Table(box=None, show_header=False, padding=0)
        time_cost_info.add_column(style="cyan", width=20)
        time_cost_info.add_column(style="white")
        time_cost_info.add_row("Elapsed Time:", time_str)
        time_cost_info.add_row("Estimated Cost:", f"${self.metrics.total_cost:.4f}")
        
        progress_layout["time_cost"].update(Panel(time_cost_info, box=box.ROUNDED))
        
        self.layout["progress"].update(progress_layout)
        
        # Stats section
        stats_table = Table(title="System Metrics", box=box.ROUNDED)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Active Agents", str(self.metrics.agents_used))
        stats_table.add_row("Files Created", str(self.metrics.files_created))
        stats_table.add_row("Lines of Code", f"{self.metrics.lines_of_code:,}")
        stats_table.add_row("Tests Written", str(self.metrics.tests_written))
        
        self.layout["stats"].update(stats_table)
        
    def log_event(self, event_type: str, agent: str, message: str):
        """Log an event"""
        self.event_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "agent": agent,
            "message": message
        })
        
    def export_log(self):
        """Export event log to file"""
        filename = f"demo_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump({
                "demo_type": "task_management_system",
                "duration": time.time() - self.start_time if self.start_time else 0,
                "metrics": self.metrics.__dict__,
                "events": self.event_log
            }, f, indent=2)
        console.print(f"\n[green]Log exported to {filename}[/]")
        
    def handle_keyboard(self):
        """Handle keyboard input in a separate thread"""
        while self.running:
            try:
                key = console.input()
                
                if key.lower() == 'q':
                    self.running = False
                    break
                elif key.lower() == 's' and self.state in [DemoState.READY, DemoState.PAUSED]:
                    self.state = DemoState.RUNNING
                elif key.lower() == 'p' and self.state == DemoState.RUNNING:
                    self.state = DemoState.PAUSED
                elif key.lower() == 'r':
                    self.reset_demo()
                elif key.lower() == 'e':
                    self.export_log()
                elif key.lower() == 'v' and self.state == DemoState.COMPLETED:
                    self.show_summary()
                    
                self.update_footer()
            except:
                pass
                
    def reset_demo(self):
        """Reset the demo to initial state"""
        self.state = DemoState.READY
        self.metrics = DemoMetrics()
        self.event_log = []
        self.start_time = None
        
        for agent in self.agents.values():
            agent.current_task = "Idle"
            agent.tasks_completed = 0
            
        self.update_footer()
        
    def show_summary(self):
        """Show demo summary"""
        console.print("\n" + "="*80)
        console.print(Panel("📊 Demo Summary", style="bold green"))
        console.print(f"Total Duration: {timedelta(seconds=int(time.time() - self.start_time))}")
        console.print(f"Tasks Completed: {self.metrics.completed_tasks}/{self.metrics.total_tasks}")
        console.print(f"Total Cost: ${self.metrics.total_cost:.4f}")
        console.print(f"Lines of Code: {self.metrics.lines_of_code:,}")
        console.print("="*80 + "\n")
        
    def simulate_agent_work(self):
        """Simulate agents working on tasks"""
        task_index = 0
        
        while task_index < 7 and self.running:
            if self.state == DemoState.RUNNING:
                # Update each agent with their current task
                for agent_id, tasks in self.task_sequences.items():
                    if task_index < len(tasks):
                        agent = self.agents[agent_id]
                        agent.current_task = tasks[task_index]
                        self.update_agent_panel(agent_id)
                        self.log_event("task_start", agent.name, tasks[task_index])
                
                # Simulate work being done
                time.sleep(2)
                
                # Complete tasks and update metrics
                if self.state == DemoState.RUNNING:  # Check again after sleep
                    for agent_id in self.agents:
                        agent = self.agents[agent_id]
                        agent.tasks_completed += 1
                        
                    self.metrics.completed_tasks = min(task_index * 4 + 4, self.metrics.total_tasks)
                    self.metrics.assigned_tasks = self.metrics.completed_tasks
                    self.metrics.files_created = 5 + task_index * 3
                    self.metrics.lines_of_code = 150 + task_index * 400
                    self.metrics.tests_written = 8 + task_index * 6
                    self.metrics.total_cost = 0.002 * (task_index + 1)
                    
                    self.update_metrics()
                    task_index += 1
            else:
                # Paused or stopped
                time.sleep(0.1)
                
        if self.running and self.state == DemoState.RUNNING:
            self.state = DemoState.COMPLETED
            self.update_footer()
            
            # Final update
            for agent_id in self.agents:
                agent = self.agents[agent_id]
                agent.current_task = "✅ Complete"
                self.update_agent_panel(agent_id)
                
    def run(self):
        """Run the interactive demo"""
        try:
            # Create layout
            self.create_layout()
            
            # Start keyboard handler in background
            self.keyboard_thread = threading.Thread(target=self.handle_keyboard, daemon=True)
            self.keyboard_thread.start()
            
            # Main demo loop
            with Live(self.layout, refresh_per_second=2, console=console) as live:
                self.live = live
                
                # Initial display
                for agent_id in self.agents:
                    self.update_agent_panel(agent_id)
                self.update_metrics()
                
                # Wait for start
                while self.state == DemoState.READY and self.running:
                    time.sleep(0.1)
                    
                if self.running:
                    self.start_time = time.time()
                    self.simulate_agent_work()
                    
                # Keep running until quit
                while self.running:
                    if self.start_time:
                        self.metrics.elapsed_time = time.time() - self.start_time
                    self.update_metrics()
                    time.sleep(0.5)
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            console.print("\n[yellow]Demo ended[/]")

def main():
    """Run the enhanced interactive demo"""
    console.clear()
    
    # Welcome screen
    welcome = Panel(
        Align.center(
            Text.from_markup(
                "[bold magenta]🎭 AIOSv3.1 Enhanced Interactive Demo[/]\n\n"
                "[white]Experience our AI development team building a complete application[/]\n"
                "[dim]With real-time metrics, progress tracking, and interactive controls[/]"
            ),
            vertical="middle"
        ),
        box=box.DOUBLE,
        style="magenta"
    )
    
    console.print(welcome)
    console.print("\n[bold cyan]Press Enter to continue...[/]")
    console.input()
    
    # Clear and run demo
    console.clear()
    controller = InteractiveDemoController()
    controller.run()

if __name__ == "__main__":
    main()