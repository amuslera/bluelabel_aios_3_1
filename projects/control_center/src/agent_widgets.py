"""
Enhanced agent widgets for detailed status monitoring and management.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, DataTable, Button, ProgressBar, Label
from textual.reactive import reactive
from textual.message import Message

@dataclass
class DetailedAgentStatus:
    """Comprehensive agent status with performance metrics."""
    id: str
    name: str
    role: str
    status: str
    current_task: str = ""
    task_progress: float = 0.0
    last_seen: str = ""
    first_seen: str = ""
    total_activities: int = 0
    success_rate: float = 0.0
    avg_response_time: float = 0.0
    capabilities: List[str] = field(default_factory=list)
    health_score: float = 1.0
    error_count: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0

class AgentDetailCard(Container):
    """Detailed card view for individual agent."""
    
    def __init__(self, agent: DetailedAgentStatus, **kwargs):
        super().__init__(**kwargs)
        self.agent = agent
        
    def compose(self):
        # Status indicator and basic info
        status_color = {
            "active": "green",
            "idle": "yellow", 
            "busy": "blue",
            "error": "red",
            "offline": "dim"
        }.get(self.agent.status, "white")
        
        yield Static(
            f"[{status_color}]●[/{status_color}] {self.agent.name} ({self.agent.role})",
            classes="agent-header"
        )
        
        # Current task with progress
        if self.agent.current_task:
            yield Static(f"Task: {self.agent.current_task}")
            if self.agent.task_progress > 0:
                yield ProgressBar(
                    total=100, 
                    progress=self.agent.task_progress * 100,
                    show_percentage=True
                )
        else:
            yield Static("Task: [dim]None[/dim]")
            
        # Performance metrics
        yield Horizontal(
            Static(f"✅ {self.agent.tasks_completed}", classes="metric"),
            Static(f"❌ {self.agent.tasks_failed}", classes="metric"),
            Static(f"📊 {self.agent.success_rate:.1%}", classes="metric"),
        )
        
        # Health and timing
        health_color = "green" if self.agent.health_score > 0.8 else "yellow" if self.agent.health_score > 0.5 else "red"
        yield Horizontal(
            Static(f"[{health_color}]♥ {self.agent.health_score:.2f}[/{health_color}]"),
            Static(f"⏱️ {self.agent.avg_response_time:.1f}s"),
            Static(f"👁️ {self.agent.last_seen[-8:] if self.agent.last_seen else 'Never'}")
        )
        
        # Capabilities
        if self.agent.capabilities:
            caps_str = ", ".join(self.agent.capabilities[:3])
            if len(self.agent.capabilities) > 3:
                caps_str += f" +{len(self.agent.capabilities) - 3} more"
            yield Static(f"Skills: {caps_str}", classes="capabilities")

class EnhancedAgentOrchestra(Container):
    """Enhanced agent monitoring with detailed status and performance metrics."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.agents: Dict[str, DetailedAgentStatus] = {}
        self.view_mode = "cards"  # "cards" or "table"
        
    def compose(self):
        yield Horizontal(
            Static("🤖 Agent Orchestra", classes="panel-title"),
            Button("Cards", id="view-cards", variant="primary" if self.view_mode == "cards" else "default"),
            Button("Table", id="view-table", variant="primary" if self.view_mode == "table" else "default"),
            classes="header-row"
        )
        
        yield Container(id="agent-view")
        
        yield Horizontal(
            Button("Launch Agent", id="launch-btn", variant="success"),
            Button("Stop Agent", id="stop-btn", variant="error"),
            Button("Restart Agent", id="restart-btn", variant="warning"),
            Button("Agent Details", id="details-btn"),
            classes="action-buttons"
        )
        
    def on_mount(self):
        """Initialize the view."""
        self.refresh_view()
        
    def on_button_pressed(self, event):
        """Handle button presses."""
        if event.button.id == "view-cards":
            self.view_mode = "cards"
            self.refresh_view()
        elif event.button.id == "view-table":
            self.view_mode = "table"
            self.refresh_view()
            
    def update_agent(self, agent: DetailedAgentStatus):
        """Update agent information."""
        self.agents[agent.id] = agent
        self.refresh_view()
        
    def refresh_view(self):
        """Refresh the agent view based on current mode."""
        view_container = self.query_one("#agent-view")
        view_container.remove_children()
        
        if self.view_mode == "cards":
            self.show_cards_view(view_container)
        else:
            self.show_table_view(view_container)
            
    def show_cards_view(self, container):
        """Show agents in card layout."""
        if not self.agents:
            container.mount(Static("No agents connected", classes="empty-state"))
            return
            
        # Create grid of agent cards
        for agent in self.agents.values():
            container.mount(AgentDetailCard(agent, classes="agent-card"))
            
    def show_table_view(self, container):
        """Show agents in table layout."""
        table = DataTable(id="agents-table")
        table.add_columns(
            "Status", "Agent", "Role", "Current Task", 
            "Progress", "Success Rate", "Health", "Last Seen"
        )
        
        for agent in self.agents.values():
            status_icon = {
                "active": "🟢",
                "idle": "🟡", 
                "busy": "🔵",
                "error": "🔴",
                "offline": "⚫"
            }.get(agent.status, "❓")
            
            progress_bar = "▓" * int(agent.task_progress * 10) + "░" * (10 - int(agent.task_progress * 10))
            
            table.add_row(
                f"{status_icon} {agent.status}",
                agent.name,
                agent.role,
                agent.current_task[:30] + "..." if len(agent.current_task) > 30 else agent.current_task,
                f"{progress_bar} {agent.task_progress:.0%}",
                f"{agent.success_rate:.1%}",
                f"{agent.health_score:.2f}",
                agent.last_seen[-8:] if agent.last_seen else "Never"
            )
            
        container.mount(table)

class SystemHealthDashboard(Container):
    """System-wide health and performance dashboard."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.metrics = {}
        
    def compose(self):
        yield Static("📈 System Health Dashboard", classes="panel-title")
        
        # Key metrics row
        yield Horizontal(
            Container(
                Static("0", id="active-agents-count", classes="big-number"),
                Static("Active Agents", classes="metric-label"),
                classes="metric-box"
            ),
            Container(
                Static("0", id="total-tasks-count", classes="big-number"),
                Static("Tasks Today", classes="metric-label"),
                classes="metric-box"
            ),
            Container(
                Static("0%", id="success-rate", classes="big-number"),
                Static("Success Rate", classes="metric-label"),
                classes="metric-box"
            ),
            Container(
                Static("0.0s", id="avg-response", classes="big-number"),
                Static("Avg Response", classes="metric-label"),
                classes="metric-box"
            ),
            classes="metrics-row"
        )
        
        # System status indicators
        yield Horizontal(
            Static("🟢 All Systems Operational", id="system-status"),
            Static("⚡ Load: Normal", id="system-load"),
            Static("💾 Storage: 85% free", id="storage-status"),
            classes="status-indicators"
        )
        
        # Recent alerts/issues
        yield Static("🚨 Recent Alerts", classes="section-title")
        yield Container(
            Static("No recent alerts", id="alerts-list", classes="alerts"),
            id="alerts-container"
        )
        
    def update_metrics(self, metrics: Dict[str, Any]):
        """Update dashboard metrics."""
        self.metrics.update(metrics)
        
        # Update metric displays
        self.query_one("#active-agents-count").update(str(metrics.get('active_agents', 0)))
        self.query_one("#total-tasks-count").update(str(metrics.get('tasks_today', 0)))
        self.query_one("#success-rate").update(f"{metrics.get('success_rate', 0):.1%}")
        self.query_one("#avg-response").update(f"{metrics.get('avg_response_time', 0):.1f}s")
        
        # Update system status based on metrics
        self.update_system_status(metrics)
        
    def update_system_status(self, metrics: Dict[str, Any]):
        """Update system status indicators."""
        # Determine overall system health
        active_agents = metrics.get('active_agents', 0)
        error_rate = metrics.get('error_rate', 0)
        avg_response = metrics.get('avg_response_time', 0)
        
        if error_rate > 0.1 or avg_response > 5.0:
            status = "🔴 System Issues Detected"
            status_class = "error"
        elif error_rate > 0.05 or avg_response > 2.0:
            status = "🟡 Performance Degraded" 
            status_class = "warning"
        else:
            status = "🟢 All Systems Operational"
            status_class = "success"
            
        self.query_one("#system-status").update(status)
        
        # Update load indicator
        if active_agents > 10:
            load = "⚡ Load: High"
        elif active_agents > 5:
            load = "⚡ Load: Medium"
        else:
            load = "⚡ Load: Normal"
            
        self.query_one("#system-load").update(load)
        
    def add_alert(self, alert: str, severity: str = "info"):
        """Add a new alert to the dashboard."""
        alerts_list = self.query_one("#alerts-list")
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        severity_icon = {
            "error": "🔴",
            "warning": "🟡", 
            "info": "🔵",
            "success": "🟢"
        }.get(severity, "ℹ️")
        
        alert_text = f"[{timestamp}] {severity_icon} {alert}"
        
        # Update alerts display (keep last 5)
        current_text = alerts_list.renderable
        if current_text == "No recent alerts":
            alerts_list.update(alert_text)
        else:
            lines = str(current_text).split('\n')
            lines.append(alert_text)
            alerts_list.update('\n'.join(lines[-5:]))  # Keep last 5 alerts

class PerformanceTrends(Container):
    """Performance trends and analytics."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history = []
        
    def compose(self):
        yield Static("📊 Performance Trends", classes="panel-title")
        
        # Simple ASCII chart placeholder
        yield Container(
            Static("Task Completion Rate (Last Hour)", classes="chart-title"),
            Static(self.generate_ascii_chart(), id="completion-chart"),
            classes="chart-container"
        )
        
        yield Container(
            Static("Response Time Trend", classes="chart-title"),
            Static(self.generate_response_chart(), id="response-chart"),
            classes="chart-container"
        )
        
    def generate_ascii_chart(self) -> str:
        """Generate simple ASCII chart for task completion."""
        # Placeholder ASCII chart
        return """
    100% ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
     75% ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░
     50% ▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░
     25% ▓▓▓▓▓░░░░░░░░░░░░░░░░
      0% ░░░░░░░░░░░░░░░░░░░░░░
          00:00  00:15  00:30  00:45
        """
        
    def generate_response_chart(self) -> str:
        """Generate ASCII chart for response times."""
        return """
      5s ░░░░░░░░░░░░░░░░░░░░░░
      4s ░░▓░░░░░░░░░░░░░░░░░░░
      3s ░░▓▓░░░░░░░░░░░░░░░░░░
      2s ▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░
      1s ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
          00:00  00:15  00:30  00:45
        """
        
    def update_trends(self, metrics: Dict[str, Any]):
        """Update performance trends with new data."""
        self.history.append({
            'timestamp': datetime.now(),
            'metrics': metrics.copy()
        })
        
        # Keep only last hour of data
        cutoff = datetime.now().timestamp() - 3600
        self.history = [
            h for h in self.history 
            if h['timestamp'].timestamp() > cutoff
        ]