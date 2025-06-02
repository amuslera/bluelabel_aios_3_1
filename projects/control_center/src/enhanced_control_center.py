"""
Enhanced Control Center with WebSocket integration for real-time monitoring.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

import aiohttp
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, DataTable, Button, Input, Log
from textual.reactive import reactive
from textual.message import Message
from textual.timer import Timer

@dataclass
class AgentStatus:
    """Agent status information."""
    id: str
    name: str
    status: str
    current_task: str = ""
    last_seen: str = ""
    activities_count: int = 0

class WebSocketManager:
    """Manages WebSocket connection to monitoring server."""
    
    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key
        self.session = None
        self.ws = None
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
    async def connect(self):
        """Connect to WebSocket server."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            ws_url = f"{self.url}?api_key={self.api_key}"
            self.ws = await self.session.ws_connect(ws_url)
            self.connected = True
            self.reconnect_attempts = 0
            return True
            
        except Exception as e:
            print(f"WebSocket connection failed: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from WebSocket server."""
        self.connected = False
        if self.ws:
            await self.ws.close()
            self.ws = None
        if self.session:
            await self.session.close()
            self.session = None
    
    async def send_message(self, message: Dict[str, Any]):
        """Send message to WebSocket server."""
        if self.connected and self.ws:
            try:
                await self.ws.send_json(message)
                return True
            except Exception as e:
                print(f"Failed to send WebSocket message: {e}")
                self.connected = False
                return False
        return False
    
    async def receive_message(self) -> Optional[Dict[str, Any]]:
        """Receive message from WebSocket server."""
        if not self.connected or not self.ws:
            return None
            
        try:
            msg = await self.ws.receive()
            
            if msg.type == aiohttp.WSMsgType.TEXT:
                return json.loads(msg.data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f"WebSocket error: {self.ws.exception()}")
                self.connected = False
                return None
            elif msg.type == aiohttp.WSMsgType.CLOSE:
                print("WebSocket connection closed by server")
                self.connected = False
                return None
                
        except Exception as e:
            print(f"Failed to receive WebSocket message: {e}")
            self.connected = False
            return None
    
    async def reconnect(self):
        """Attempt to reconnect to WebSocket server."""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            return False
            
        self.reconnect_attempts += 1
        await asyncio.sleep(2 ** self.reconnect_attempts)  # Exponential backoff
        return await self.connect()

class ConnectionStatus(Static):
    """Display connection status to monitoring server."""
    
    def __init__(self, **kwargs):
        super().__init__("🔴 Disconnected", **kwargs)
        self.status = "disconnected"
    
    def update_status(self, connected: bool, message: str = ""):
        """Update connection status display."""
        if connected:
            self.status = "connected"
            self.update("🟢 Connected" + (f" - {message}" if message else ""))
        else:
            self.status = "disconnected"
            self.update("🔴 Disconnected" + (f" - {message}" if message else ""))

class AgentOrchestra(Container):
    """Agent monitoring and management panel."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.agents: Dict[str, AgentStatus] = {}
        
    def compose(self) -> ComposeResult:
        yield Static("🤖 Agent Orchestra", classes="panel-title")
        yield DataTable(id="agents-table")
        yield Horizontal(
            Button("Launch Agent", id="launch-btn", variant="primary"),
            Button("Stop Agent", id="stop-btn", variant="warning"),
            Button("Refresh", id="refresh-btn"),
        )
    
    def on_mount(self):
        """Initialize the agents table."""
        table = self.query_one("#agents-table", DataTable)
        table.add_columns("Status", "Agent", "Task", "Last Seen", "Activities")
        
    def update_agent(self, agent: AgentStatus):
        """Update agent information in the table."""
        self.agents[agent.id] = agent
        self.refresh_table()
        
    def refresh_table(self):
        """Refresh the agents table with current data."""
        table = self.query_one("#agents-table", DataTable)
        table.clear()
        
        for agent in self.agents.values():
            status_icon = {
                "active": "🟢",
                "idle": "🟡", 
                "busy": "🔵",
                "error": "🔴",
                "offline": "⚫"
            }.get(agent.status, "❓")
            
            table.add_row(
                f"{status_icon} {agent.status}",
                agent.name,
                agent.current_task or "None",
                agent.last_seen,
                str(agent.activities_count)
            )

class ActivityMonitor(ScrollableContainer):
    """Real-time activity monitoring panel."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_activities = 100
        
    def compose(self) -> ComposeResult:
        yield Static("📊 Activity Monitor", classes="panel-title")
        yield Log(id="activity-log")
        
    def add_activity(self, activity: Dict[str, Any]):
        """Add new activity to the monitor."""
        log = self.query_one("#activity-log", Log)
        
        timestamp = activity.get('stored_at', datetime.now().isoformat())
        agent_name = activity.get('agent_name', 'Unknown')
        message = activity.get('message', 'Activity')
        status = activity.get('status', 'info')
        
        # Format activity entry
        entry = f"[{timestamp[:19]}] {agent_name}: {message}"
        
        # Add with appropriate styling based on status
        if status == 'error':
            log.write(f"[red]{entry}[/red]")
        elif status == 'success':
            log.write(f"[green]{entry}[/green]")
        elif status == 'warning':
            log.write(f"[yellow]{entry}[/yellow]")
        else:
            log.write(entry)

class TaskManager(Container):
    """Task assignment and management panel."""
    
    def compose(self) -> ComposeResult:
        yield Static("📋 Task Manager", classes="panel-title")
        yield DataTable(id="tasks-table")
        yield Horizontal(
            Input(placeholder="Task description...", id="task-input"),
            Button("Assign", id="assign-task-btn", variant="primary"),
        )
        
    def on_mount(self):
        """Initialize the tasks table."""
        table = self.query_one("#tasks-table", DataTable)
        table.add_columns("ID", "Task", "Assigned To", "Status", "Progress")

class SystemMetrics(Container):
    """System health and metrics panel."""
    
    def compose(self) -> ComposeResult:
        yield Static("📈 System Metrics", classes="panel-title")
        yield Static("Active Agents: 0", id="metric-agents")
        yield Static("Total Activities: 0", id="metric-activities")
        yield Static("Activities (24h): 0", id="metric-activities-24h")
        yield Static("Uptime: 0s", id="metric-uptime")
        
    def update_metrics(self, stats: Dict[str, Any]):
        """Update system metrics display."""
        self.query_one("#metric-agents").update(f"Active Agents: {stats.get('active_agents', 0)}")
        self.query_one("#metric-activities").update(f"Total Activities: {stats.get('total_activities', 0)}")
        self.query_one("#metric-activities-24h").update(f"Activities (24h): {stats.get('activities_24h', 0)}")

class EnhancedControlCenter(App):
    """Enhanced Control Center with real-time WebSocket integration."""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 2;
        grid-gutter: 1;
        padding: 1;
    }
    
    .panel-title {
        text-style: bold;
        color: cyan;
        margin-bottom: 1;
    }
    
    #agents {
        border: solid green;
        padding: 1;
    }
    
    #monitor {
        border: solid blue;  
        padding: 1;
    }
    
    #tasks {
        border: solid yellow;
        padding: 1;
    }
    
    #metrics {
        border: solid magenta;
        padding: 1;
    }
    
    #connection-status {
        dock: top;
        height: 1;
        background: $surface;
        color: $text;
        padding: 0 1;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("c", "connect", "Connect/Reconnect"),
        ("t", "assign_task", "Assign Task"),
        ("ctrl+l", "clear_log", "Clear Log"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Configuration
        self.monitoring_url = os.getenv('MONITORING_WS_URL', 'ws://localhost:6795/ws')
        self.api_key = os.getenv('MONITORING_API_KEY', 'aios_default_key')
        
        # WebSocket manager
        self.ws_manager = WebSocketManager(self.monitoring_url, self.api_key)
        
        # Update timer
        self.update_timer = None
        self.start_time = datetime.now()
        
    def compose(self) -> ComposeResult:
        yield ConnectionStatus(id="connection-status")
        yield Header(show_clock=True)
        yield Container(
            AgentOrchestra(id="agents"),
            ActivityMonitor(id="monitor"),
            TaskManager(id="tasks"),
            SystemMetrics(id="metrics"),
        )
        yield Footer()
    
    async def on_mount(self):
        """Initialize the application."""
        # Start WebSocket connection
        await self.action_connect()
        
        # Start update timer (every 5 seconds)
        self.update_timer = self.set_interval(5.0, self.periodic_update)
        
        # Start WebSocket message handler
        asyncio.create_task(self.websocket_handler())
    
    async def action_connect(self):
        """Connect to monitoring server."""
        connection_status = self.query_one("#connection-status", ConnectionStatus)
        connection_status.update_status(False, "Connecting...")
        
        success = await self.ws_manager.connect()
        if success:
            connection_status.update_status(True, "Connected to monitoring server")
            # Subscribe to all activities
            await self.ws_manager.send_message({
                'type': 'subscribe',
                'filters': {}
            })
        else:
            connection_status.update_status(False, "Failed to connect")
    
    async def websocket_handler(self):
        """Handle incoming WebSocket messages."""
        while True:
            if not self.ws_manager.connected:
                # Try to reconnect
                if await self.ws_manager.reconnect():
                    connection_status = self.query_one("#connection-status", ConnectionStatus)
                    connection_status.update_status(True, "Reconnected")
                else:
                    await asyncio.sleep(5)  # Wait before next attempt
                    continue
            
            message = await self.ws_manager.receive_message()
            if message:
                await self.handle_message(message)
            else:
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
    
    async def handle_message(self, message: Dict[str, Any]):
        """Handle incoming WebSocket message."""
        msg_type = message.get('type')
        
        if msg_type == 'activity':
            # New activity received
            activity = message.get('activity', {})
            
            # Update activity monitor
            activity_monitor = self.query_one("#monitor", ActivityMonitor)
            activity_monitor.add_activity(activity)
            
            # Update agent status if activity is from an agent
            agent_id = activity.get('agent_id')
            if agent_id:
                agent_orchestra = self.query_one("#agents", AgentOrchestra)
                agent_status = AgentStatus(
                    id=agent_id,
                    name=activity.get('agent_name', 'Unknown'),
                    status=activity.get('status', 'active'),
                    current_task=activity.get('current_task', ''),
                    last_seen=activity.get('stored_at', ''),
                    activities_count=activity.get('activities_count', 0)
                )
                agent_orchestra.update_agent(agent_status)
        
        elif msg_type == 'connection':
            # Connection status update
            pass
            
        elif msg_type == 'error':
            # Handle error
            error_msg = message.get('message', 'Unknown error')
            activity_monitor = self.query_one("#monitor", ActivityMonitor)
            activity_monitor.add_activity({
                'stored_at': datetime.now().isoformat(),
                'agent_name': 'System',
                'message': f"Error: {error_msg}",
                'status': 'error'
            })
    
    async def periodic_update(self):
        """Periodic update of metrics and data."""
        # Update uptime
        uptime = datetime.now() - self.start_time
        uptime_str = f"{int(uptime.total_seconds())}s"
        
        metrics = self.query_one("#metrics", SystemMetrics)
        metrics.query_one("#metric-uptime").update(f"Uptime: {uptime_str}")
        
        # TODO: Fetch latest statistics from monitoring server
        # For now, we'll use placeholder data
        
    async def action_refresh(self):
        """Refresh all data from monitoring server."""
        # Clear current data and re-fetch from server
        # This would typically make HTTP requests to the monitoring API
        pass
    
    async def action_assign_task(self):
        """Assign a new task to an agent."""
        # Focus on task input
        task_input = self.query_one("#task-input", Input)
        task_input.focus()
    
    async def action_clear_log(self):
        """Clear the activity log."""
        log = self.query_one("#activity-log", Log)
        log.clear()
    
    async def on_unmount(self):
        """Cleanup when app is closing."""
        if self.update_timer:
            self.update_timer.stop()
        await self.ws_manager.disconnect()

def main():
    """Run the enhanced control center."""
    app = EnhancedControlCenter()
    app.run()

if __name__ == "__main__":
    main()