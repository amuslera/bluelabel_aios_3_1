"""
AIOSv3 Control Center - Unified agent management interface
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, DataTable, Button
from textual.reactive import reactive
from datetime import datetime
import asyncio
import aiohttp

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
    }
    
    #monitor {
        column-span: 1;
        row-span: 1;
        border: solid blue;
    }
    
    #tasks {
        column-span: 1;
        row-span: 1;
        border: solid yellow;
    }
    
    #pr-review {
        column-span: 1;
        row-span: 1;
        border: solid magenta;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("p", "review_pr", "Review PR"),
        ("t", "assign_task", "Assign Task"),
        ("a", "launch_agent", "Launch Agent"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            AgentOrchestra(id="agents"),
            MonitoringDashboard(id="monitor"),
            TaskManager(id="tasks"),
            PRReviewer(id="pr-review"),
        )
        yield Footer()

# ... continued implementation