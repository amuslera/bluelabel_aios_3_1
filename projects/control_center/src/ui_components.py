"""
UI components for the control center.
"""

from textual.widgets import Static, DataTable, Button, TextLog
from textual.containers import Container, ScrollableContainer
from textual.reactive import reactive
from typing import Dict, List, Any
import asyncio

class AgentOrchestra(Container):
    """Display and control active agents."""
    
    def compose(self):
        yield Static("🎭 Agent Orchestra", classes="title")
        self.table = DataTable()
        self.table.add_columns("Status", "Agent", "Role", "Task", "Progress")
        yield self.table
        yield Button("Launch Agent", id="launch-agent")
    
    async def update_agents(self, agents: List[Dict[str, Any]]):
        """Update agent display."""
        self.table.clear()
        for agent in agents:
            status_icon = {
                'active': '🟢',
                'idle': '🟡',
                'error': '🔴'
            }.get(agent['status'], '⚪')
            
            self.table.add_row(
                status_icon,
                agent['name'],
                agent['role'],
                agent.get('current_task', 'None')[:30],
                f"{agent.get('progress', 0)}%"
            )

class MonitoringDashboard(Container):
    """Real-time activity monitoring."""
    
    def compose(self):
        yield Static("📊 Activity Monitor", classes="title")
        self.log = TextLog(highlight=True, markup=True)
        yield ScrollableContainer(self.log)
    
    async def add_activity(self, activity: Dict[str, Any]):
        """Add activity to log."""
        timestamp = activity.get('timestamp', '')
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