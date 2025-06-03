#!/usr/bin/env python3
"""
Fixed Enhanced Demo - Clean design with chat and working controls
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
import keyboard
import os

# Add project root to path
sys.path.append(str(Path(__file__).parent))

console = Console()

class FixedEnhancedDemo:
    """Fixed demo with chat and proper controls"""
    
    def __init__(self):
        self.console = console
        self.running = True
        self.started = False
        self.paused = False
        self.start_time = None
        self.event_log = []
        self.chat_messages = deque(maxlen=10)  # Last 10 messages
        self.current_phase = 0
        
        # Metrics
        self.total_tasks = 16
        self.completed_tasks = 0
        self.total_cost = 0.0
        self.lines_of_code = 0
        self.tests_written = 0
        self.files_created = 0
        
        # Agent info
        self.agents = {
            "marcus": {"name": "Marcus Chen", "color": "yellow", "emoji": "🔧"},
            "emily": {"name": "Emily Rodriguez", "color": "cyan", "emoji": "🎨"},
            "alex": {"name": "Alex Thompson", "color": "green", "emoji": "🧪"},
            "jordan": {"name": "Jordan Kim", "color": "magenta", "emoji": "🚀"}
        }
        
        # Activities and chat messages
        self.phases = [
            {
                "activities": {
                    "marcus": "Analyzing requirements...",
                    "emily": "Setting up React project...",
                    "alex": "Setting up test framework...",
                    "jordan": "Creating Docker containers..."
                },
                "chats": [
                    ("marcus", "I'll start with the database schema and API design"),
                    ("emily", "Great! I'll begin setting up the React components"),
                    ("alex", "I'll prepare our testing infrastructure"),
                    ("jordan", "Docker environment coming up!")
                ]
            },
            {
                "activities": {
                    "marcus": "Designing database schema...",
                    "emily": "Creating UI components...",
                    "alex": "Writing unit tests...",
                    "jordan": "Setting up CI/CD pipeline..."
                },
                "chats": [
                    ("marcus", "Database models for User and Task are ready"),
                    ("emily", "TaskList component is looking good!"),
                    ("marcus", "@emily I've exposed the API endpoints you'll need"),
                    ("emily", "Perfect! Integrating now")
                ]
            },
            {
                "activities": {
                    "marcus": "Creating API endpoints...",
                    "emily": "Implementing state management...",
                    "alex": "Creating integration tests...",
                    "jordan": "Configuring monitoring..."
                },
                "chats": [
                    ("alex", "Found a potential security issue in auth"),
                    ("marcus", "On it! Thanks Alex"),
                    ("jordan", "CI pipeline is green ✅"),
                    ("alex", "All tests passing!")
                ]
            },
            {
                "activities": {
                    "marcus": "Implementing authentication...",
                    "emily": "Adding responsive design...",
                    "alex": "Running security scans...",
                    "jordan": "Preparing deployment scripts..."
                },
                "chats": [
                    ("emily", "UI is fully responsive now"),
                    ("jordan", "Kubernetes configs ready for deployment"),
                    ("marcus", "JWT auth implemented with refresh tokens"),
                    ("alex", "Security scan passed, looking good!")
                ]
            },
            {
                "activities": {
                    "marcus": "Writing API documentation...",
                    "emily": "Polishing user interface...",
                    "alex": "Generating coverage report...",
                    "jordan": "Finalizing production config..."
                },
                "chats": [
                    ("alex", "95% test coverage achieved! 🎉"),
                    ("emily", "Dark mode is working beautifully"),
                    ("jordan", "Ready to deploy to production"),
                    ("marcus", "API docs complete with OpenAPI spec")
                ]
            }
        ]
        
    def add_chat_message(self, agent_id: str, message: str):
        """Add a chat message"""
        agent = self.agents[agent_id]
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_messages.append(f"[{agent['color']}]{agent['emoji']} {agent_id}[/]: {message}")
        self.log_event(agent['name'], f"Chat: {message}")
        
    def log_event(self, agent: str, activity: str):
        """Log an event"""
        self.event_log.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "activity": activity
        })
        
    def export_log(self):
        """Export event log"""
        if not self.event_log:
            return
            
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
        # Add to chat
        self.chat_messages.append(f"[green]✓ Log exported to {filename}[/]")
        
    def reset_demo(self):
        """Reset demo state"""
        self.completed_tasks = 0
        self.total_cost = 0.0
        self.lines_of_code = 0
        self.tests_written = 0
        self.files_created = 0
        self.start_time = None
        self.started = False
        self.paused = False
        self.current_phase = 0
        self.chat_messages.clear()
        self.event_log = []
        
    def create_layout(self):
        """Create the demo layout"""
        layout = Layout()
        
        # Main structure
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="main", size=15),
            Layout(name="bottom", size=11)
        )
        
        # Header with project info
        project_info = """[bold cyan]Task Management System[/]
Full-stack web application with authentication, real-time updates, and team collaboration
Tech: FastAPI + PostgreSQL | React + TypeScript | Docker + Kubernetes"""
        
        layout["header"].update(Panel(
            Align.center(project_info),
            title="🚀 Project Overview",
            border_style="cyan",
            box=box.DOUBLE
        ))
        
        # Main area: agents + chat
        layout["main"].split_row(
            Layout(name="agents", ratio=3),
            Layout(name="chat", ratio=1)
        )
        
        # Agent panels
        layout["agents"].split_row(
            Layout(name="marcus"),
            Layout(name="emily"),
            Layout(name="alex"),
            Layout(name="jordan")
        )
        
        # Bottom area: progress + stats + controls
        layout["bottom"].split_column(
            Layout(name="metrics", size=8),
            Layout(name="footer", size=3)
        )
        
        # Metrics area
        layout["metrics"].split_row(
            Layout(name="progress", ratio=2),
            Layout(name="stats", ratio=1)
        )
        
        return layout
        
    def update_display(self, layout):
        """Update all display elements"""
        # Update agent panels
        if not self.started:
            status = "[dim]Ready to start...[/]"
        elif self.current_phase < len(self.phases):
            phase = self.phases[self.current_phase]
            activities = phase["activities"]
        else:
            status = "[green]✅ Complete![/]"
            activities = {agent: status for agent in self.agents}
            
        if self.started and self.current_phase < len(self.phases):
            for agent_id, agent_info in self.agents.items():
                activity = self.phases[self.current_phase]["activities"][agent_id]
                progress_text = f"Phase {self.current_phase + 1}/{len(self.phases)}"
                
                layout[agent_id].update(Panel(
                    f"[{agent_info['color']}]{activity}[/]\n\n[dim]{progress_text}[/]",
                    title=f"{agent_info['emoji']} {agent_info['name']}",
                    border_style=agent_info['color']
                ))
        else:
            # Initial or complete state
            for agent_id, agent_info in self.agents.items():
                text = status if not self.started else "[green]✅ Complete![/]\n\n[dim]All tasks finished[/]"
                layout[agent_id].update(Panel(
                    text,
                    title=f"{agent_info['emoji']} {agent_info['name']}",
                    border_style=agent_info['color']
                ))
        
        # Update chat
        chat_content = "\n".join(self.chat_messages) if self.chat_messages else "[dim]No messages yet...[/]"
        layout["chat"].update(Panel(
            chat_content,
            title="💬 Team Chat",
            border_style="blue"
        ))
        
        # Update progress
        progress = Progress(
            TextColumn("[bold blue]Progress"),
            BarColumn(bar_width=None),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn(f"{self.completed_tasks}/{self.total_tasks}")
        )
        progress_task = progress.add_task("", total=self.total_tasks, completed=self.completed_tasks)
        
        # Calculate time and cost
        if self.start_time:
            elapsed = time.time() - self.start_time
            time_str = str(timedelta(seconds=int(elapsed)))
        else:
            time_str = "00:00:00"
            
        progress_panel = Panel(
            progress,
            title=f"⏱️  {time_str} | 💰 ${self.total_cost:.4f}",
            box=box.ROUNDED
        )
        layout["progress"].update(progress_panel)
        
        # Update stats
        stats = Table(box=box.SIMPLE, show_header=False)
        stats.add_column("Metric", style="cyan", width=8)
        stats.add_column("Value", style="green", width=6)
        stats.add_row("Agents", "4")
        stats.add_row("Files", str(self.files_created))
        stats.add_row("LOC", f"{self.lines_of_code:,}")
        stats.add_row("Tests", str(self.tests_written))
        
        layout["stats"].update(Panel(stats, title="📊 Metrics", box=box.ROUNDED))
        
        # Update footer
        if not self.started:
            controls = "[s] Start  [q] Quit"
        elif self.paused:
            controls = "[s] Resume  [r] Reset  [e] Export  [q] Quit"
        else:
            controls = "[p] Pause  [r] Reset  [e] Export  [q] Quit"
            
        layout["footer"].update(Panel(
            Align.center(f"[bold]{controls}[/]"),
            style="dim white on grey23",
            box=box.ROUNDED
        ))
        
    def run_phase(self):
        """Run a single phase of the demo"""
        if self.current_phase >= len(self.phases):
            return False
            
        phase = self.phases[self.current_phase]
        
        # Add chat messages for this phase
        for agent_id, message in phase["chats"]:
            self.add_chat_message(agent_id, message)
            time.sleep(0.5)  # Stagger messages
            
        # Update metrics
        self.completed_tasks = min((self.current_phase + 1) * 3, self.total_tasks)
        self.files_created = 5 + self.current_phase * 4
        self.lines_of_code = 200 + self.current_phase * 550
        self.tests_written = 10 + self.current_phase * 8
        self.total_cost = 0.001 + self.current_phase * 0.002
        
        self.current_phase += 1
        return True
        
    def run_demo(self):
        """Run the fixed demo"""
        self.console.clear()
        
        # Create layout
        layout = self.create_layout()
        
        # Main demo loop
        with Live(layout, refresh_per_second=2, console=self.console) as live:
            while self.running:
                # Check for keyboard input (non-blocking)
                if os.name == 'nt':  # Windows
                    import msvcrt
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8').lower()
                else:  # Unix/Linux/Mac
                    import select, termios, tty
                    old_settings = termios.tcgetattr(sys.stdin)
                    try:
                        tty.setraw(sys.stdin.fileno())
                        if select.select([sys.stdin], [], [], 0)[0]:
                            key = sys.stdin.read(1).lower()
                        else:
                            key = None
                    finally:
                        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                
                # Handle keyboard input
                if key:
                    if key == 'q':
                        self.running = False
                        break
                    elif key == 's' and not self.started:
                        self.started = True
                        self.start_time = time.time()
                        self.chat_messages.append("[green]🚀 Project started![/]")
                    elif key == 's' and self.paused:
                        self.paused = False
                    elif key == 'p' and self.started and not self.paused:
                        self.paused = True
                        self.chat_messages.append("[yellow]⏸️  Demo paused[/]")
                    elif key == 'r':
                        self.reset_demo()
                        self.chat_messages.append("[yellow]🔄 Demo reset[/]")
                    elif key == 'e' and self.event_log:
                        self.export_log()
                
                # Update display
                self.update_display(layout)
                
                # Run simulation if started and not paused
                if self.started and not self.paused and self.current_phase < len(self.phases):
                    if not self.run_phase():
                        # Demo complete
                        self.chat_messages.append("[green]🎉 Project complete![/]")
                    time.sleep(2)  # Wait between phases
                else:
                    time.sleep(0.1)  # Small delay when idle
            
        # Show final summary if completed
        if self.completed_tasks == self.total_tasks:
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
        # Simple keyboard input approach
        import sys, tty, termios
        
        demo = FixedEnhancedDemo()
        demo.run_demo()
    except KeyboardInterrupt:
        console.print("\n[red]Demo interrupted[/]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/]")

if __name__ == "__main__":
    main()