#!/usr/bin/env python3
"""
Run the Control Center UI - Fixed for Textual 3.x

This launches the control center with compatibility fixes.
"""

import sys
import os
from datetime import datetime

# Add the project path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'control_center_project'))

try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import Header, Footer, Static, DataTable, Button, RichLog, Label
    from textual.binding import Binding
    
except ImportError as e:
    print("❌ Missing dependencies!")
    print(f"Error: {e}")
    sys.exit(1)

class AgentOrchestra(Container):
    """Display and control active agents."""
    
    def compose(self) -> ComposeResult:
        yield Label("🎭 Agent Orchestra", classes="title")
        self.table = DataTable()
        yield self.table
        yield Button("Launch Agent", id="launch-agent")
    
    def on_mount(self) -> None:
        """Set up the table when mounted."""
        table = self.query_one(DataTable)
        table.add_columns("Status", "Agent", "Role", "Task", "Progress")
        
    async def update_agents(self, agents):
        """Update agent display."""
        table = self.query_one(DataTable)
        table.clear()
        for agent in agents:
            status_icon = {
                'active': '🟢',
                'idle': '🟡', 
                'error': '🔴'
            }.get(agent['status'], '⚪')
            
            table.add_row(
                status_icon,
                agent['name'],
                agent['role'],
                agent.get('current_task', 'None')[:30],
                f"{agent.get('progress', 0)}%"
            )

class MonitoringDashboard(Container):
    """Real-time activity monitoring."""
    
    def compose(self) -> ComposeResult:
        yield Label("📊 Activity Monitor", classes="title")
        self.log = RichLog(highlight=True, markup=True)
        yield self.log
    
    async def add_activity(self, activity):
        """Add activity to log."""
        timestamp = activity.get('timestamp', datetime.now().strftime('%H:%M:%S'))
        agent = activity.get('agent_name', 'Unknown')
        action = activity.get('activity_type', '')
        
        # Color based on type
        color = {
            'success': 'green',
            'error': 'red',
            'git_operation': 'blue',
            'file_operation': 'yellow'
        }.get(action, 'white')
        
        self.log.write(f"[{color}]{timestamp} {agent}: {action}[/{color}]")

class TaskManager(Container):
    """Task management interface."""
    
    def compose(self) -> ComposeResult:
        yield Label("📋 Task Manager", classes="title")
        self.task_table = DataTable()
        yield self.task_table
        yield Horizontal(
            Button("Assign Task", id="assign-task"),
            Button("Create Task", id="create-task"),
            classes="task-actions"
        )
    
    def on_mount(self) -> None:
        """Set up the task table."""
        table = self.query_one(DataTable)
        table.add_columns("ID", "Title", "Assignee", "Status", "Priority")
        
        # Add example tasks
        table.add_row(
            "MON-002", 
            "Add WebSocket integration",
            "Backend Agent",
            "🔵 Pending",
            "High"
        )
        table.add_row(
            "MON-003",
            "Implement error handling", 
            "Unassigned",
            "⚪ Backlog",
            "Medium"
        )

class PRReviewer(Container):
    """Interactive PR review interface."""
    
    def compose(self) -> ComposeResult:
        yield Label("🔍 PR Review", classes="title")
        
        # PR info display
        self.pr_info = Static("""PR #2: Control Center UI
Author: Alex Rivera
Branch: feature/control-center-ui
Files: 4 changed

Ready for review""")
        yield self.pr_info
        
        # Diff display
        self.diff_log = RichLog(highlight=True, markup=True)
        yield self.diff_log
        
        yield Horizontal(
            Button("Approve", id="approve", variant="success"),
            Button("Request Changes", id="request-changes", variant="warning"),
            Button("View Code", id="view-code"),
            classes="pr-actions"
        )
    
    def show_sample_diff(self):
        """Show a sample diff."""
        self.diff_log.write("[blue]@@ -0,0 +1,42 @@[/blue]")
        self.diff_log.write("[green]+ class ControlCenter(App):[/green]")
        self.diff_log.write("[green]+     '''Main control center application.'''[/green]")

class ControlCenter(App):
    """Main control center application."""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 2;
        grid-gutter: 1;
    }
    
    #agents {
        border: solid $success;
        height: 100%;
    }
    
    #monitor {
        border: solid $primary;
        height: 100%;
    }
    
    #tasks {
        border: solid $warning;
        height: 100%;
    }
    
    #pr-review {
        border: solid $error;
        height: 100%;
    }
    
    .title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    
    Button {
        margin: 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("a", "launch_agent", "Launch Agent"),
        Binding("p", "review_pr", "Review PR"),
        Binding("t", "assign_task", "Assign Task"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create the UI."""
        yield Header()
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
            },
            {
                'name': 'Sarah Kim',
                'role': 'architect',
                'status': 'idle',
                'current_task': 'None',
                'progress': 0
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
            },
            {
                'timestamp': '10:45:32',
                'agent_name': 'Backend',
                'activity_type': 'Connected to monitoring server'
            }
        ]
        
        for activity in activities:
            await monitor.add_activity(activity)
        
        # Show sample diff
        pr_reviewer = self.query_one("#pr-review", PRReviewer)
        pr_reviewer.show_sample_diff()
        
        # Set window title
        self.title = "AIOSv3 Control Center"
        self.sub_title = "Agent Management Interface"
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
    
    def action_launch_agent(self) -> None:
        """Launch agent action."""
        monitor = self.query_one("#monitor", MonitoringDashboard)
        monitor.log.write("[green]🚀 Launching agent selector...[/green]")
        monitor.log.write("[yellow]Available agents: backend, frontend, monitor, architect[/yellow]")
    
    def action_review_pr(self) -> None:
        """Review PR action."""
        monitor = self.query_one("#monitor", MonitoringDashboard)
        monitor.log.write("[blue]📋 Opening PR review for PR #2...[/blue]")
        monitor.log.write("[cyan]Use arrow keys to navigate diff[/cyan]")
    
    def action_assign_task(self) -> None:
        """Assign task action."""
        monitor = self.query_one("#monitor", MonitoringDashboard)
        monitor.log.write("[yellow]📌 Opening task assignment...[/yellow]")
        monitor.log.write("[white]Select task and agent to assign[/white]")
    
    def action_refresh(self) -> None:
        """Refresh the display."""
        monitor = self.query_one("#monitor", MonitoringDashboard)
        monitor.log.write("[green]🔄 Refreshing all panels...[/green]")


def main():
    """Run the control center."""
    print("🚀 Launching AIOSv3 Control Center...")
    print("\nKeyboard shortcuts:")
    print("  q - Quit")
    print("  a - Launch Agent") 
    print("  p - Review PR")
    print("  t - Assign Task")
    print("  r - Refresh")
    print("\nPress any key to continue...")
    
    try:
        app = ControlCenter()
        app.run()
    except Exception as e:
        print(f"\n❌ Error running control center: {e}")
        print("\nTry running the demo instead:")
        print("  ./control_center_demo.py")


if __name__ == "__main__":
    main()