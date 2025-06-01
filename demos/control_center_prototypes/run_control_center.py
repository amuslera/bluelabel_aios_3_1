#!/usr/bin/env python3
"""
Run the Control Center UI

This launches the actual control center that the agent built.
Note: Requires textual to be installed: pip install textual
"""

import sys
import os
import subprocess

# Add the project path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'control_center_project'))

try:
    from src.control_center import ControlCenter
    from src.ui_components import AgentOrchestra, MonitoringDashboard, TaskManager, PRReviewer
    from src.pr_reviewer import DiffViewer, PRInfo
    
    # Import required Textual components
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import Header, Footer, Static, DataTable, Button, TextLog
    from textual.reactive import reactive
    
except ImportError as e:
    print("❌ Missing dependencies!")
    print(f"Error: {e}")
    print("\nTo run the control center, you need to install:")
    print("  pip install textual rich aiohttp")
    print("\nOr create a virtual environment first:")
    print("  python3 -m venv venv")
    print("  source venv/bin/activate")
    print("  pip install textual rich aiohttp")
    sys.exit(1)

# Complete the implementation that agent started
class TaskManager(Container):
    """Task management interface."""
    
    def compose(self):
        yield Static("📋 Task Manager", classes="title")
        self.task_table = DataTable()
        self.task_table.add_columns("ID", "Title", "Assignee", "Status", "Priority")
        
        # Add some example tasks
        self.task_table.add_row(
            "MON-002", 
            "Add WebSocket integration",
            "Backend Agent",
            "🔵 Pending",
            "High"
        )
        self.task_table.add_row(
            "MON-003",
            "Implement error handling", 
            "Unassigned",
            "⚪ Backlog",
            "Medium"
        )
        
        yield self.task_table
        yield Horizontal(
            Button("Assign Task", id="assign-task"),
            Button("Create Task", id="create-task"),
            classes="task-actions"
        )

class PRInfo(Static):
    """Display PR information."""
    
    def update(self, pr_info: dict):
        """Update PR display."""
        self.update(f"""
PR #{pr_info.get('number', 'N/A')}: {pr_info.get('title', 'No PR')}
Author: {pr_info.get('author', 'Unknown')}
Branch: {pr_info.get('branch', 'N/A')}
Files: {len(pr_info.get('files_changed', []))} changed
        """)

# Create complete app with all components
class ControlCenter(App):
    """Main control center application."""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 2;
        grid-gutter: 1;
    }
    
    #agents {
        column-span: 1;
        row-span: 1;
        border: solid green;
        height: 100%;
    }
    
    #monitor {
        column-span: 1;
        row-span: 1;
        border: solid blue;
        height: 100%;
        overflow-y: auto;
    }
    
    #tasks {
        column-span: 1;
        row-span: 1;
        border: solid yellow;
        height: 100%;
    }
    
    #pr-review {
        column-span: 1;
        row-span: 1;
        border: solid magenta;
        height: 100%;
    }
    
    .title {
        text-align: center;
        text-style: bold;
        padding: 1;
    }
    
    Button {
        margin: 1;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("p", "review_pr", "Review PR"),
        ("t", "assign_task", "Assign Task"),
        ("a", "launch_agent", "Launch Agent"),
        ("m", "toggle_monitor", "Toggle Monitor"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create the UI."""
        yield Header(show_clock=True)
        yield Container(
            AgentOrchestra(id="agents"),
            MonitoringDashboard(id="monitor"),
            TaskManager(id="tasks"),
            PRReviewer(id="pr-review"),
        )
        yield Footer()
    
    async def on_mount(self) -> None:
        """Initialize the app with sample data."""
        # Add sample agents
        agents = [
            {
                'name': 'Marcus Chen',
                'role': 'backend',
                'status': 'active',
                'current_task': 'Implementing WebSocket client',
                'progress': 35
            },
            {
                'name': 'Alex Rivera',
                'role': 'frontend',
                'status': 'idle',
                'current_task': 'None',
                'progress': 0
            },
            {
                'name': 'Diana Martinez',
                'role': 'monitor',
                'status': 'active',
                'current_task': 'Collecting metrics',
                'progress': 80
            }
        ]
        
        orchestra = self.query_one("#agents", AgentOrchestra)
        await orchestra.update_agents(agents)
        
        # Add sample activities
        monitor = self.query_one("#monitor", MonitoringDashboard)
        activities = [
            {
                'timestamp': '10:45:23',
                'agent_name': 'Marcus',
                'activity_type': 'file_operation'
            },
            {
                'timestamp': '10:45:25',
                'agent_name': 'Marcus',
                'activity_type': 'success'
            },
            {
                'timestamp': '10:45:30',
                'agent_name': 'Diana',
                'activity_type': 'git_operation'
            }
        ]
        
        for activity in activities:
            await monitor.add_activity(activity)
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
    
    def action_launch_agent(self) -> None:
        """Launch agent action."""
        # In real implementation, would launch agent selector
        monitor = self.query_one("#monitor", MonitoringDashboard)
        monitor.log.write("[green]Launching agent selector...[/green]")
    
    def action_review_pr(self) -> None:
        """Review PR action."""
        monitor = self.query_one("#monitor", MonitoringDashboard)
        monitor.log.write("[blue]Opening PR review interface...[/blue]")
    
    def action_assign_task(self) -> None:
        """Assign task action."""
        monitor = self.query_one("#monitor", MonitoringDashboard)
        monitor.log.write("[yellow]Opening task assignment...[/yellow]")


def main():
    """Run the control center."""
    print("🚀 Launching AIOSv3 Control Center...")
    print("\nKeyboard shortcuts:")
    print("  q - Quit")
    print("  a - Launch Agent")
    print("  p - Review PR")
    print("  t - Assign Task")
    print("  r - Refresh\n")
    
    app = ControlCenter()
    app.run()


if __name__ == "__main__":
    main()