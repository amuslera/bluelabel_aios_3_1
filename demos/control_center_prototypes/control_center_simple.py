#!/usr/bin/env python3
"""
Simple Control Center - A working version of the control center UI
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Header, Footer, Static, DataTable, Button, RichLog, Label
from textual.binding import Binding
from datetime import datetime

class ControlCenter(App):
    """Simplified control center that works with current Textual."""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 2;
        grid-gutter: 1;
    }
    
    .panel {
        height: 100%;
        border: solid $accent;
        padding: 1;
    }
    
    #agents { border: solid green; }
    #monitor { border: solid blue; }
    #tasks { border: solid yellow; }
    #pr { border: solid magenta; }
    
    .title {
        text-align: center;
        text-style: bold;
        color: $text;
        margin-bottom: 1;
    }
    
    DataTable {
        height: 10;
        margin-bottom: 1;
    }
    
    RichLog {
        height: 100%;
        border: solid $panel-lighten-1;
        padding: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("a", "add_activity", "Add Activity"),
        Binding("r", "refresh", "Refresh"),
        Binding("t", "toggle_theme", "Theme"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create the UI."""
        yield Header()
        
        # Agent panel
        with Container(id="agents", classes="panel"):
            yield Label("🎭 Agent Orchestra", classes="title")
            agents_table = DataTable(id="agents_table")
            agents_table.add_columns("Status", "Agent", "Role", "Progress")
            agents_table.add_row("🟢", "Marcus Chen", "backend", "35%")
            agents_table.add_row("🟡", "Alex Rivera", "frontend", "0%")
            agents_table.add_row("🟢", "Diana Martinez", "monitor", "80%")
            yield agents_table
            yield Button("Launch Agent", id="launch")
        
        # Monitor panel
        with Container(id="monitor", classes="panel"):
            yield Label("📊 Activity Monitor", classes="title")
            yield RichLog(id="activity_log", highlight=True, markup=True)
        
        # Tasks panel  
        with Container(id="tasks", classes="panel"):
            yield Label("📋 Task Manager", classes="title")
            tasks_table = DataTable(id="tasks_table")
            tasks_table.add_columns("ID", "Title", "Status")
            tasks_table.add_row("MON-002", "Add WebSocket", "🔵 Pending")
            tasks_table.add_row("MON-003", "Error handling", "⚪ Backlog")
            yield tasks_table
            yield Button("Assign Task", id="assign")
        
        # PR panel
        with Container(id="pr", classes="panel"):
            yield Label("🔍 PR Review", classes="title")
            yield Static("""PR #2: Control Center UI
Author: Alex Rivera
Branch: feature/control-center
Files: 4 changed""", id="pr_info")
            with Horizontal():
                yield Button("Approve", variant="success")
                yield Button("Changes", variant="warning")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize when app starts."""
        self.title = "AIOSv3 Control Center"
        self.sub_title = "Agent Management System"
        
        # Add initial activities
        log = self.query_one("#activity_log", RichLog)
        log.write("[green]System started[/green]")
        log.write(f"[blue]{datetime.now().strftime('%H:%M:%S')} Marcus: Connected to server[/blue]")
        log.write(f"[yellow]{datetime.now().strftime('%H:%M:%S')} Diana: Monitoring active[/yellow]")
    
    def action_quit(self) -> None:
        """Quit the app."""
        self.exit()
    
    def action_add_activity(self) -> None:
        """Add a sample activity."""
        log = self.query_one("#activity_log", RichLog)
        activities = [
            "[green]✅ Backend: API endpoint created[/green]",
            "[blue]🔄 Frontend: Component updated[/blue]",
            "[yellow]📊 Monitor: Metrics collected[/yellow]",
            "[red]❌ Error: Connection timeout[/red]",
            "[cyan]🔀 Git: Changes committed[/cyan]"
        ]
        import random
        activity = random.choice(activities)
        timestamp = datetime.now().strftime('%H:%M:%S')
        log.write(f"{timestamp} {activity}")
    
    def action_refresh(self) -> None:
        """Refresh action."""
        log = self.query_one("#activity_log", RichLog)
        log.write("[green]🔄 Refreshed all panels[/green]")
    
    def action_toggle_theme(self) -> None:
        """Toggle dark/light theme."""
        self.dark = not self.dark

def main():
    """Run the control center."""
    print("\n🚀 Starting AIOSv3 Control Center...")
    print("\nThis is the UI that the agent built!")
    print("It provides a unified interface for:")
    print("  • Monitoring agents in real-time")
    print("  • Managing tasks and assignments")
    print("  • Reviewing PRs without leaving terminal")
    print("  • Launching and controlling agents\n")
    
    app = ControlCenter()
    app.run()

if __name__ == "__main__":
    main()