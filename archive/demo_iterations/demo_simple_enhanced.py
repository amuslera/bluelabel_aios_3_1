#!/usr/bin/env python3
"""
Simple Enhanced Demo - Clean design with requested UX improvements
Based on the working simple demo with added features
"""

import sys
import time
import json
import threading
from pathlib import Path
from datetime import datetime, timedelta
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

class SimpleEnhancedDemo:
    """Simple demo with enhanced UX features"""
    
    def __init__(self):
        self.console = console
        self.running = True
        self.paused = False
        self.start_time = None
        self.event_log = []
        
        # Metrics
        self.total_tasks = 16
        self.completed_tasks = 0
        self.total_cost = 0.0
        self.lines_of_code = 0
        self.tests_written = 0
        self.files_created = 0
        
        # Agent activities
        self.activities = {
            "marcus": [
                "Analyzing requirements...",
                "Designing database schema...",
                "Creating API endpoints...",
                "Implementing authentication...",
                "Writing API documentation..."
            ],
            "emily": [
                "Setting up React project...",
                "Creating UI components...",
                "Implementing state management...",
                "Adding responsive design...",
                "Polishing user interface..."
            ],
            "alex": [
                "Setting up test framework...",
                "Writing unit tests...",
                "Creating integration tests...",
                "Running security scans...",
                "Generating coverage report..."
            ],
            "jordan": [
                "Creating Docker containers...",
                "Setting up CI/CD pipeline...",
                "Configuring monitoring...",
                "Preparing deployment scripts...",
                "Finalizing production config..."
            ]
        }
        
    def handle_keyboard(self):
        """Handle keyboard input in background"""
        while self.running:
            try:
                key = console.input()
                if key.lower() == 'q':
                    self.running = False
                elif key.lower() == 'p':
                    self.paused = not self.paused
                elif key.lower() == 'r':
                    self.reset_demo()
                elif key.lower() == 'e':
                    self.export_log()
                elif key.lower() == 's' and not self.start_time:
                    self.start_time = time.time()
                    self.paused = False
            except:
                pass
                
    def reset_demo(self):
        """Reset demo state"""
        self.completed_tasks = 0
        self.total_cost = 0.0
        self.lines_of_code = 0
        self.tests_written = 0
        self.files_created = 0
        self.start_time = time.time()
        self.event_log = []
        self.paused = False
        
    def export_log(self):
        """Export event log"""
        filename = f"demo_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump({
                "events": self.event_log,
                "metrics": {
                    "tasks_completed": self.completed_tasks,
                    "total_cost": self.total_cost,
                    "lines_of_code": self.lines_of_code,
                    "duration": time.time() - self.start_time if self.start_time else 0
                }
            }, f, indent=2)
        console.print(f"\n[green]✓ Log exported to {filename}[/]")
        
    def log_event(self, agent: str, activity: str):
        """Log an event"""
        self.event_log.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "activity": activity
        })
        
    def run_demo(self):
        """Run the enhanced demo"""
        self.console.clear()
        
        # Start keyboard handler
        keyboard_thread = threading.Thread(target=self.handle_keyboard, daemon=True)
        keyboard_thread.start()
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="body", size=15),
            Layout(name="metrics", size=8),
            Layout(name="footer", size=3)
        )
        
        # Project header
        project_info = """[bold cyan]Task Management System[/]
Full-stack web application with authentication, real-time updates, and team collaboration
Tech: FastAPI + PostgreSQL | React + TypeScript | Docker + Kubernetes"""
        
        layout["header"].update(Panel(
            Align.center(project_info),
            title="🚀 Project Overview",
            border_style="cyan",
            box=box.DOUBLE
        ))
        
        # Agent panels
        layout["body"].split_row(
            Layout(name="marcus"),
            Layout(name="emily"),
            Layout(name="alex"),
            Layout(name="jordan")
        )
        
        # Metrics area
        layout["metrics"].split_row(
            Layout(name="progress", ratio=2),
            Layout(name="stats", ratio=1)
        )
        
        # Controls footer
        controls = "[bold][s][/] Start  [bold][p][/] Pause/Resume  [bold][r][/] Reset  [bold][e][/] Export  [bold][q][/] Quit"
        layout["footer"].update(Panel(
            Align.center(controls),
            style="dim",
            box=box.ROUNDED
        ))
        
        # Initial agent panels
        for agent, color in [("marcus", "yellow"), ("emily", "cyan"), 
                            ("alex", "green"), ("jordan", "magenta")]:
            layout[agent].update(Panel(
                "[dim]Ready to start...[/]",
                title=f"{agent.title()} ({agent.title()[0]})",
                border_style=color
            ))
        
        with Live(layout, refresh_per_second=2, console=self.console) as live:
            # Wait for start
            while not self.start_time and self.running:
                time.sleep(0.1)
                
            if not self.running:
                return
                
            # Run simulation
            for i in range(len(self.activities["marcus"])):
                if not self.running:
                    break
                    
                while self.paused and self.running:
                    time.sleep(0.1)
                    
                # Update agent activities
                for agent, color in [("marcus", "yellow"), ("emily", "cyan"), 
                                    ("alex", "green"), ("jordan", "magenta")]:
                    activity = self.activities[agent][i]
                    layout[agent].update(Panel(
                        f"[{color}]{activity}[/]\n\n[dim]Progress: {i+1}/{len(self.activities[agent])}[/]",
                        title=f"{agent.title()} ({agent.title()[0]})",
                        border_style=color
                    ))
                    self.log_event(agent, activity)
                
                # Update metrics
                self.completed_tasks = (i + 1) * 4
                self.files_created = 5 + i * 4
                self.lines_of_code = 200 + i * 550
                self.tests_written = 10 + i * 8
                self.total_cost = 0.001 + i * 0.0015
                
                # Progress bar
                progress = Progress(
                    TextColumn("[bold blue]Progress"),
                    BarColumn(bar_width=40),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TextColumn(f"{self.completed_tasks}/{self.total_tasks} tasks")
                )
                task_id = progress.add_task("", total=self.total_tasks, completed=self.completed_tasks)
                
                # Time and cost display
                elapsed = time.time() - self.start_time
                time_str = str(timedelta(seconds=int(elapsed)))
                
                progress_panel = Panel(
                    progress,
                    title=f"⏱️  {time_str} | 💰 ${self.total_cost:.4f}",
                    box=box.ROUNDED
                )
                layout["progress"].update(progress_panel)
                
                # Stats table
                stats = Table(box=box.SIMPLE)
                stats.add_column("Metric", style="cyan")
                stats.add_column("Value", style="green")
                stats.add_row("Agents", "4")
                stats.add_row("Files", str(self.files_created))
                stats.add_row("LOC", f"{self.lines_of_code:,}")
                stats.add_row("Tests", str(self.tests_written))
                
                layout["stats"].update(Panel(stats, title="📊 Metrics", box=box.ROUNDED))
                
                # Simulate work
                time.sleep(3)
            
            # Completion
            if self.running and not self.paused:
                for agent, color in [("marcus", "yellow"), ("emily", "cyan"), 
                                    ("alex", "green"), ("jordan", "magenta")]:
                    layout[agent].update(Panel(
                        f"[{color}]✅ Complete![/]\n\n[dim]All tasks finished[/]",
                        title=f"{agent.title()} ({agent.title()[0]})",
                        border_style=color
                    ))
                
                # Final summary
                self.console.print()
                self.console.print(Panel(
                    f"✅ Task Management System Complete!\n\n"
                    f"Duration: {timedelta(seconds=int(time.time() - self.start_time))}\n"
                    f"Total Cost: ${self.total_cost:.4f}\n"
                    f"Code Written: {self.lines_of_code:,} lines\n"
                    f"Tests: {self.tests_written} ({self.tests_written/self.lines_of_code*100:.1f}% coverage)",
                    style="bold green",
                    box=box.DOUBLE
                ))

def main():
    try:
        demo = SimpleEnhancedDemo()
        demo.run_demo()
    except KeyboardInterrupt:
        console.print("\n[red]Demo interrupted[/]")

if __name__ == "__main__":
    main()