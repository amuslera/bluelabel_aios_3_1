"""
Terminal UI for AIOSv3 Monitoring Dashboard

Built with Rich library for modern terminal interfaces.
Following junior developer practices with clear documentation.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, List, Any
import json
from pathlib import Path

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn


class MonitoringDashboard:
    """
    Real-time monitoring dashboard for AI agents.
    
    Shows agent status, tasks, and activity feed in terminal.
    """
    
    def __init__(self):
        """Initialize the dashboard."""
        self.console = Console()
        self.agents = {}
        self.tasks = {}
        self.activities = []
        self.running = True
        self.logger = self.setup_logging()
        
        # Layout setup
        self.layout = Layout()
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=1)
        )
        
        # Split body into panels
        self.layout["body"].split_row(
            Layout(name="agents", ratio=1),
            Layout(name="tasks", ratio=1)
        )
        
        self.logger.info("Dashboard initialized")
    
    def setup_logging(self) -> logging.Logger:
        """Setup logging to prevent stdout interference."""
        logger = logging.getLogger('monitoring_dashboard')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            log_file = os.getenv('DASHBOARD_LOG_FILE', 'logs/dashboard.log')
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            
            # NO console handler to prevent stdout pollution
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def create_header(self) -> Panel:
        """Create header panel."""
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_row(
            "[bold blue]AIOSv3 Monitoring Dashboard[/bold blue]"
        )
        grid.add_row(
            f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]"
        )
        return Panel(grid, style="white on blue")
    
    def create_agents_panel(self) -> Panel:
        """Create agents status panel."""
        table = Table(title="Agent Status", expand=True)
        table.add_column("Agent", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Current Task")
        table.add_column("Progress")
        
        # Add agent rows
        for agent_id, info in self.agents.items():
            status = info.get('status', 'idle')
            task = info.get('current_task', 'None')
            progress = info.get('progress', 0)
            
            # Color code status
            if status == 'working':
                status_text = "[green]● Working[/green]"
            elif status == 'blocked':
                status_text = "[red]● Blocked[/red]"
            else:
                status_text = "[yellow]● Idle[/yellow]"
            
            table.add_row(
                info['name'],
                status_text,
                task[:40] + "..." if len(task) > 40 else task,
                f"{progress}%"
            )
        
        return Panel(table, title="👥 Agents", border_style="blue")
    
    def create_tasks_panel(self) -> Panel:
        """Create tasks panel."""
        table = Table(title="Active Tasks", expand=True)
        table.add_column("ID", style="dim")
        table.add_column("Description")
        table.add_column("Assigned To")
        table.add_column("Status")
        
        # Add task rows
        for task_id, task in self.tasks.items():
            status = task.get('status', 'pending')
            
            # Color code status
            if status == 'completed':
                status_text = "[green]✓ Done[/green]"
            elif status == 'in_progress':
                status_text = "[yellow]⚡ Active[/yellow]"
            else:
                status_text = "[dim]○ Pending[/dim]"
            
            table.add_row(
                task_id[:8],
                task['description'][:35] + "...",
                task.get('assigned_to', 'Unassigned'),
                status_text
            )
        
        return Panel(table, title="📋 Tasks", border_style="green")
    
    def create_footer(self) -> Panel:
        """Create footer with commands."""
        return Panel(
            "[bold]Commands:[/bold] [q]uit | [r]efresh | [a]gents | [t]asks",
            style="dim"
        )
    
    async def update_display(self):
        """Update the dashboard display."""
        self.layout["header"].update(self.create_header())
        self.layout["agents"].update(self.create_agents_panel())
        self.layout["tasks"].update(self.create_tasks_panel())
        self.layout["footer"].update(self.create_footer())
    
    async def load_data(self):
        """Load data from log files."""
        # In real implementation, would connect to WebSocket
        # For now, read from log files
        log_dir = Path("logs")
        if log_dir.exists():
            for log_file in log_dir.glob("*.jsonl"):
                try:
                    with open(log_file) as f:
                        for line in f:
                            activity = json.loads(line)
                            self.process_activity(activity)
                except:
                    pass
    
    def process_activity(self, activity: Dict[str, Any]):
        """Process an activity update."""
        agent_id = activity.get('agent_id')
        
        # Update agent info
        if agent_id:
            if agent_id not in self.agents:
                self.agents[agent_id] = {
                    'name': activity.get('agent_name', 'Unknown'),
                    'status': 'idle'
                }
            
            # Update based on activity type
            if activity['activity_type'] == 'task_started':
                self.agents[agent_id]['status'] = 'working'
                self.agents[agent_id]['current_task'] = activity['details'].get('description', '')
            elif activity['activity_type'] == 'task_completed':
                self.agents[agent_id]['status'] = 'idle'
                self.agents[agent_id]['current_task'] = 'None'
            elif activity['activity_type'] == 'progress_update':
                self.agents[agent_id]['progress'] = activity['details'].get('progress', 0)
    
    async def run(self):
        """Run the dashboard."""
        # Suppress Rich's internal debugging and coordinate output
        try:
            with Live(
                self.layout, 
                refresh_per_second=2, 
                screen=True,
                console=Console(stderr=True)  # Route to stderr to avoid stdout pollution
            ):
                while self.running:
                    await self.load_data()
                    await self.update_display()
                    await asyncio.sleep(1)
        except Exception as e:
            self.logger.error(f"Dashboard error: {e}")
            # Don't print to stdout


async def main():
    """Run the monitoring dashboard."""
    dashboard = MonitoringDashboard()
    
    try:
        print("🚀 Starting monitoring dashboard...")
        print("📊 Dashboard logs: logs/dashboard.log")
        print("Press Ctrl+C to stop")
        await dashboard.run()
    except KeyboardInterrupt:
        dashboard.logger.info("Dashboard stopped by user")
        print("\n✅ Dashboard stopped")


if __name__ == "__main__":
    asyncio.run(main())
