"""
Theatrical Dashboard v3.0 Style - Using Textual Framework

This version recreates the v3.0 dashboard design approach using Textual,
providing a rich terminal UI with tabs, scrollable logs, and real-time updates.
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import deque
from dataclasses import dataclass
from enum import Enum

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.reactive import reactive, var
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    Log,
    ProgressBar,
    Static,
    TabbedContent,
    TabPane,
)


# Agent name mapping (v3.0 style)
AGENT_NAMES = {
    "orchestrator": "System",
    "cto-001": "Sarah Chen", 
    "backend-001": "Marcus Chen",
    "frontend-001": "Emily Rodriguez",
    "qa-001": "Alex Thompson",
    "devops-001": "Jordan Kim"
}


class EventType(Enum):
    """Event types for the dashboard"""
    INIT = "init"
    PHASE = "phase"
    THINK = "think"
    WORK = "work"
    SUCCESS = "success"
    ERROR = "error"
    ACTIVITY = "activity"
    MESSAGE = "message"
    COST = "cost"
    PROJECT = "project"


@dataclass
class TheatricalEvent:
    """Event structure for theatrical monitoring"""
    type: EventType
    agent_id: str
    message: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None
    progress: float = 0.0
    cost: float = 0.0
    tokens: int = 0


class AgentStatusWidget(Static):
    """Widget displaying individual agent status with activity log and metrics."""

    def __init__(self, agent_id: str, agent_name: str, **kwargs):
        super().__init__(**kwargs)
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.last_update = time.time()
        self.status = "idle"
        self.progress = 0
        self.current_task = "None"
        # Performance metrics
        self.tasks_assigned = 0
        self.tasks_completed = 0
        self.total_time = 0.0
        self.total_cost = 0.0
        self.total_tokens = 0
        self.task_start_time = None
        # Activity history
        self.activity_history = []
        self.activity_scroll = None
        self.activity_labels = []

    def compose(self) -> ComposeResult:
        """Create agent status display with scrollable activity log."""
        # Main content area with horizontal split
        with Horizontal(classes="agent-content"):
            # Left side: Scrollable activity log (70% width)
            with Vertical(classes="agent-activity"):
                # Compact agent header
                yield Label(f"{self.get_agent_icon()} {self.agent_name}", 
                           id=f"name-{self.agent_id}", 
                           classes="agent-name")
                yield Label(f"Status: {self.get_status_icon()} {self.status.title()}", 
                           id=f"status-{self.agent_id}", 
                           classes="agent-status")
                
                # Scrollable activity log
                self.activity_scroll = ScrollableContainer(
                    id=f"activity-{self.agent_id}",
                    classes="activity-log"
                )
                yield self.activity_scroll
            
            # Right side: Metrics and details (30% width)
            with Vertical(classes="agent-metrics"):
                yield Label("📊 Metrics", classes="metrics-header")
                yield Label(f"Tasks: {self.tasks_completed}/{self.tasks_assigned}", 
                           id=f"tasks-{self.agent_id}")
                yield Label(f"Avg Time: 0.0s", id=f"avgtime-{self.agent_id}")
                yield Label(f"Cost: $0.0000", id=f"cost-{self.agent_id}")
                yield Label(f"Tokens: 0", id=f"tokens-{self.agent_id}")
                
                # Progress bar
                yield Label("Progress:", classes="progress-label")
                yield ProgressBar(total=100, show_eta=False, 
                                id=f"progress-{self.agent_id}",
                                classes="agent-progress")

    def get_agent_icon(self) -> str:
        """Get agent icon based on ID."""
        icons = {
            "cto-001": "🏛️",
            "backend-001": "⚙️",
            "frontend-001": "🎨",
            "qa-001": "🧪",
            "devops-001": "🚀",
            "orchestrator": "🎬"
        }
        return icons.get(self.agent_id, "🤖")

    def get_status_icon(self) -> str:
        """Get status icon."""
        icons = {
            "idle": "⚪",
            "thinking": "🤔",
            "working": "⚙️",
            "success": "✅",
            "error": "❌",
            "active": "🟢"
        }
        return icons.get(self.status, "❓")

    def update_status(self, status: str, task: Optional[str] = None):
        """Update agent status and current task."""
        self.status = status
        if task:
            self.current_task = task
            
        # Update UI elements
        status_label = self.query_one(f"#status-{self.agent_id}", Label)
        status_label.update(f"Status: {self.get_status_icon()} {status.title()}")
        
        # Track task timing
        if status == "working" and self.task_start_time is None:
            self.task_start_time = time.time()
            self.tasks_assigned += 1
        elif status in ["success", "error", "idle"] and self.task_start_time:
            elapsed = time.time() - self.task_start_time
            self.total_time += elapsed
            self.task_start_time = None
            if status == "success":
                self.tasks_completed += 1
            
            # Update metrics
            self.update_task_metrics()

    def update_task_metrics(self):
        """Update task-related metrics in the UI."""
        tasks_label = self.query_one(f"#tasks-{self.agent_id}", Label)
        tasks_label.update(f"Tasks: {self.tasks_completed}/{self.tasks_assigned}")
        
        if self.tasks_completed > 0:
            avg_time = self.total_time / self.tasks_completed
            avgtime_label = self.query_one(f"#avgtime-{self.agent_id}", Label)
            avgtime_label.update(f"Avg Time: {avg_time:.1f}s")

    def add_activity(self, activity_text: str):
        """Add an activity to the log."""
        self.activity_history.append(activity_text)
        if self.activity_scroll:
            try:
                activity_label = Label(activity_text, classes="activity-item")
                self.activity_labels.append(activity_label)
                self.activity_scroll.mount(activity_label)
                self.activity_scroll.scroll_end()
            except:
                pass

    def update_metrics(self, cost: Optional[float] = None, tokens: Optional[int] = None):
        """Update cost and token metrics."""
        if cost is not None:
            self.total_cost += cost
            cost_label = self.query_one(f"#cost-{self.agent_id}", Label)
            cost_label.update(f"Cost: ${self.total_cost:.4f}")
            
        if tokens is not None:
            self.total_tokens += tokens
            tokens_label = self.query_one(f"#tokens-{self.agent_id}", Label)
            tokens_label.update(f"Tokens: {self.total_tokens:,}")

    def update_progress(self, progress: float):
        """Update progress bar."""
        progress_bar = self.query_one(f"#progress-{self.agent_id}", ProgressBar)
        progress_bar.update(progress=int(progress * 100))


class EventLogWidget(Static):
    """Enhanced log widget for full timeline with agent initials and colors."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.event_count = 0
        self.log_container = None
        self.log_labels = []

    def compose(self) -> ComposeResult:
        """Create the scrollable log container."""
        self.log_container = ScrollableContainer(classes="event-log-scroll")
        yield self.log_container

    def log_event(self, event: TheatricalEvent):
        """Log a theatrical event with agent initials and color coding."""
        self.event_count += 1

        # Map agent IDs to initials
        agent_info = {
            "orchestrator": "SYS",
            "cto-001": "CTO",
            "backend-001": "BE",
            "frontend-001": "FE",
            "qa-001": "QA",
            "devops-001": "DO"
        }

        # Get agent initial
        initial = agent_info.get(event.agent_id, "???")
        timestamp = event.timestamp.strftime("%H:%M:%S")

        # Format the message
        if event.type == EventType.PHASE:
            message = f"[bold magenta]═══ {event.message} ═══[/]"
        else:
            message = f"[{timestamp}] [{initial}] {event.message}"

        # Add to log
        log_label = Label(message, markup=True, classes=f"log-{event.type.value}")
        self.log_labels.append(log_label)
        self.log_container.mount(log_label)
        self.log_container.scroll_end()


class TheatricalDashboard(App):
    """A Textual app for theatrical agent monitoring in v3.0 style."""

    # Try to use external CSS, fallback to embedded
    CSS_PATH = "theatrical_dashboard.css"
    TITLE = "🎭 AIOSv3.1 Theatrical Dashboard (v3.0 Style)"
    SUB_TITLE = "Real-time AI Agent Orchestration Monitor"
    
    # Embedded CSS as fallback
    CSS = """
    /* Agent widgets */
    .agent-widget {
        border: round cyan;
        height: 22;
        margin: 1;
        padding: 1;
    }
    
    .agent-content {
        height: 100%;
        layout: horizontal;
    }
    
    .agent-activity {
        width: 65%;
        padding-right: 1;
    }
    
    .agent-metrics {
        width: 35%;
        padding-left: 1;
        border-left: solid white 20%;
    }
    
    .agent-name {
        text-style: bold;
        color: cyan;
    }
    
    .activity-log {
        height: 13;
        border: round white 20%;
        padding: 1;
        margin-top: 1;
    }
    
    .activity-item {
        height: 1;
    }
    
    .metrics-header {
        text-style: bold;
        color: yellow;
    }
    
    /* Event log */
    .event-log-scroll {
        height: 100%;
        border: round white 20%;
        padding: 1;
    }
    
    .log-phase {
        text-style: bold;
        color: magenta;
        text-align: center;
    }
    
    .log-think {
        color: yellow;
    }
    
    .log-work {
        color: cyan;
    }
    
    .log-success {
        color: green;
    }
    
    .log-error {
        color: red;
    }
    
    /* System panel */
    .system-panel {
        border: round yellow;
    }
    
    .system-header {
        text-style: bold;
        color: yellow;
        text-align: center;
    }
    
    /* Layout */
    .agent-row {
        height: 50%;
        layout: horizontal;
    }
    
    #agents-container {
        height: 100%;
        padding: 1;
    }
    
    #config-container {
        padding: 2;
        align: center middle;
    }
    
    .config-header {
        text-style: bold;
        color: magenta;
    }
    
    Button {
        margin: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.agent_widgets = {}
        self.event_log = None
        self.orchestrator = None
        self.start_time = time.time()
        self.mock_agents = {}
        
    def compose(self) -> ComposeResult:
        """Create dashboard layout."""
        yield Header()
        
        # Main container with tabs
        with TabbedContent(initial="agents"):
            # Agents tab
            with TabPane("🤖 Agents", id="agents"):
                with Container(id="agents-container"):
                    # Create 2x3 grid for agents
                    with Horizontal(classes="agent-row"):
                        yield AgentStatusWidget("cto-001", "Sarah Chen", 
                                              classes="agent-widget", id="widget-cto-001")
                        yield AgentStatusWidget("backend-001", "Marcus Chen", 
                                              classes="agent-widget", id="widget-backend-001")
                        yield AgentStatusWidget("frontend-001", "Emily Rodriguez", 
                                              classes="agent-widget", id="widget-frontend-001")
                    
                    with Horizontal(classes="agent-row"):
                        yield AgentStatusWidget("qa-001", "Alex Thompson", 
                                              classes="agent-widget", id="widget-qa-001")
                        yield AgentStatusWidget("devops-001", "Jordan Kim", 
                                              classes="agent-widget", id="widget-devops-001")
                        # System metrics panel
                        with Container(classes="agent-widget system-panel"):
                            yield Label("📊 System Metrics", classes="system-header")
                            yield Label(f"Uptime: 0s", id="uptime")
                            yield Label(f"Total Tasks: 0", id="total-tasks")
                            yield Label(f"Total Cost: $0.0000", id="total-cost")
                            yield Label(f"Active Agents: 0/5", id="active-agents")
            
            # Event Timeline tab
            with TabPane("📜 Timeline", id="timeline"):
                yield EventLogWidget(id="event-log")
            
            # Configuration tab
            with TabPane("⚙️ Config", id="config"):
                with Container(id="config-container"):
                    yield Label("🎯 Theatrical Configuration", classes="config-header")
                    yield Label("Delay between events: 0.5s", id="event-delay")
                    yield Label("Show raw LLM responses: No", id="show-llm")
                    yield Label("Export session data: Yes", id="export-data")
                    yield Button("Start Demo Project", id="start-demo", variant="primary")
                    yield Button("Clear All Logs", id="clear-logs", variant="warning")
        
        yield Footer()

    def on_mount(self) -> None:
        """Initialize dashboard on mount."""
        # Store widget references
        self.agent_widgets = {
            "cto-001": self.query_one("#widget-cto-001", AgentStatusWidget),
            "backend-001": self.query_one("#widget-backend-001", AgentStatusWidget),
            "frontend-001": self.query_one("#widget-frontend-001", AgentStatusWidget),
            "qa-001": self.query_one("#widget-qa-001", AgentStatusWidget),
            "devops-001": self.query_one("#widget-devops-001", AgentStatusWidget),
        }
        
        self.event_log = self.query_one("#event-log", EventLogWidget)
        
        # Initialize mock agents
        self._initialize_mock_agents()
        
        # Start background updates
        self.set_interval(1.0, self.update_system_metrics)

    def _initialize_mock_agents(self):
        """Initialize mock agents for the demo."""
        for agent_id, widget in self.agent_widgets.items():
            self.mock_agents[agent_id] = {
                "name": widget.agent_name,
                "status": "idle",
                "current_task": None
            }
            widget.add_activity("✅ Agent initialized and ready")
            
            # Log initialization
            self.event_log.log_event(TheatricalEvent(
                type=EventType.INIT,
                agent_id=agent_id,
                message=f"{widget.agent_name} initialized",
                timestamp=datetime.now()
            ))

    def update_system_metrics(self):
        """Update system-wide metrics."""
        uptime = int(time.time() - self.start_time)
        self.query_one("#uptime", Label).update(f"Uptime: {uptime}s")
        
        # Calculate totals
        total_tasks = sum(w.tasks_completed for w in self.agent_widgets.values())
        total_cost = sum(w.total_cost for w in self.agent_widgets.values())
        active = sum(1 for w in self.agent_widgets.values() if w.status != "idle")
        
        self.query_one("#total-tasks", Label).update(f"Total Tasks: {total_tasks}")
        self.query_one("#total-cost", Label).update(f"Total Cost: ${total_cost:.4f}")
        self.query_one("#active-agents", Label).update(f"Active Agents: {active}/5")

    @on(Button.Pressed, "#start-demo")
    async def start_demo_project(self):
        """Start the demo project."""
        # Disable button
        button = self.query_one("#start-demo", Button)
        button.disabled = True
        button.label = "Demo Running..."
        
        # Log project start
        self.event_log.log_event(TheatricalEvent(
            type=EventType.PROJECT,
            agent_id="orchestrator",
            message="Starting Demo Project: Real-time Chat Application",
            timestamp=datetime.now()
        ))
        
        # Run demo in background
        asyncio.create_task(self._run_demo_project())

    async def _run_demo_project(self):
        """Run the demo project with theatrical timing."""
        # Phase 1: CTO Planning
        await self._run_agent_phase(
            "cto-001",
            "Phase 1: Architecture & Planning",
            [
                "Analyzing project requirements",
                "Creating technical specification",
                "Defining system architecture"
            ]
        )
        
        # Phase 2: Backend Development
        await self._run_agent_phase(
            "backend-001",
            "Phase 2: Backend Development",
            [
                "Setting up FastAPI project",
                "Implementing WebSocket handlers",
                "Creating authentication system",
                "Designing database schema"
            ]
        )
        
        # Phase 3: Frontend Development
        await self._run_agent_phase(
            "frontend-001",
            "Phase 3: Frontend Development",
            [
                "Creating React components",
                "Building chat interface",
                "Implementing real-time updates",
                "Adding authentication flow"
            ]
        )
        
        # Phase 4: QA Testing
        await self._run_agent_phase(
            "qa-001",
            "Phase 4: Quality Assurance",
            [
                "Writing unit tests",
                "Creating integration tests",
                "Running security audit",
                "Performance testing"
            ]
        )
        
        # Phase 5: DevOps Deployment
        await self._run_agent_phase(
            "devops-001",
            "Phase 5: Deployment",
            [
                "Creating Docker containers",
                "Setting up CI/CD pipeline",
                "Configuring Kubernetes",
                "Deploying to cloud"
            ]
        )
        
        # Project complete
        self.event_log.log_event(TheatricalEvent(
            type=EventType.SUCCESS,
            agent_id="orchestrator",
            message="🎉 Project Complete! All phases successfully executed.",
            timestamp=datetime.now()
        ))
        
        # Re-enable button
        button = self.query_one("#start-demo", Button)
        button.disabled = False
        button.label = "Start Demo Project"

    async def _run_agent_phase(self, agent_id: str, phase_name: str, tasks: List[str]):
        """Run a phase of work for an agent."""
        widget = self.agent_widgets[agent_id]
        
        # Log phase start
        self.event_log.log_event(TheatricalEvent(
            type=EventType.PHASE,
            agent_id=agent_id,
            message=phase_name,
            timestamp=datetime.now()
        ))
        
        for i, task in enumerate(tasks):
            # Update status to thinking
            widget.update_status("thinking", task)
            widget.add_activity(f"💭 Thinking: {task}")
            
            self.event_log.log_event(TheatricalEvent(
                type=EventType.THINK,
                agent_id=agent_id,
                message=f"Analyzing: {task}",
                timestamp=datetime.now()
            ))
            
            await asyncio.sleep(1.5)  # Thinking delay
            
            # Update status to working
            widget.update_status("working", task)
            widget.add_activity(f"⚙️ Working: {task}")
            widget.update_progress((i + 0.5) / len(tasks))
            
            self.event_log.log_event(TheatricalEvent(
                type=EventType.WORK,
                agent_id=agent_id,
                message=f"Implementing: {task}",
                timestamp=datetime.now()
            ))
            
            await asyncio.sleep(2.0)  # Working delay
            
            # Complete task
            widget.update_status("success")
            widget.add_activity(f"✅ Completed: {task}")
            widget.update_progress((i + 1) / len(tasks))
            
            # Simulate cost/tokens
            import random
            cost = round(random.uniform(0.01, 0.05), 4)
            tokens = random.randint(200, 800)
            widget.update_metrics(cost, tokens)
            
            self.event_log.log_event(TheatricalEvent(
                type=EventType.SUCCESS,
                agent_id=agent_id,
                message=f"Completed: {task}",
                timestamp=datetime.now(),
                cost=cost,
                tokens=tokens
            ))
            
            await asyncio.sleep(0.5)  # Brief pause
        
        # Phase complete
        widget.update_status("idle")
        widget.update_progress(0)

    @on(Button.Pressed, "#clear-logs")
    def clear_all_logs(self):
        """Clear all activity logs."""
        # Clear agent logs
        for widget in self.agent_widgets.values():
            widget.activity_history.clear()
            if widget.activity_scroll:
                for label in widget.activity_labels:
                    label.remove()
                widget.activity_labels.clear()
        
        # Clear event log
        if self.event_log.log_container:
            for label in self.event_log.log_labels:
                label.remove()
            self.event_log.log_labels.clear()
        
        self.notify("All logs cleared", severity="information")


# CSS for the dashboard (would normally be in theatrical_dashboard.css)
DEFAULT_CSS = """
/* Agent widgets */
.agent-widget {
    border: solid $primary;
    height: 20;
    width: 1fr;
    margin: 1;
    padding: 1;
}

.agent-content {
    height: 100%;
}

.agent-activity {
    width: 70%;
    padding-right: 1;
}

.agent-metrics {
    width: 30%;
    border-left: solid $surface;
    padding-left: 1;
}

.agent-name {
    text-style: bold;
    color: $primary;
}

.agent-status {
    color: $text-muted;
}

.activity-log {
    height: 12;
    border: solid $surface;
    padding: 1;
    margin-top: 1;
}

.activity-item {
    color: $text;
}

/* Event log */
.event-log-scroll {
    height: 100%;
    border: solid $surface;
    padding: 1;
}

.log-phase {
    text-style: bold;
    color: $primary;
}

.log-think {
    color: $warning;
}

.log-work {
    color: $info;
}

.log-success {
    color: $success;
}

.log-error {
    color: $error;
}

/* System panel */
.system-panel {
    background: $surface;
}

.system-header {
    text-style: bold;
    margin-bottom: 1;
}

/* Config */
#config-container {
    padding: 2;
}

.config-header {
    text-style: bold;
    font-size: 18;
    margin-bottom: 2;
}

/* Layout */
.agent-row {
    height: 50%;
}

#agents-container {
    height: 100%;
}
"""