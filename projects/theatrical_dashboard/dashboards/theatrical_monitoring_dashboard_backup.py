"""
Theatrical Monitoring Dashboard - Real-time visualization of agent interactions

This dashboard provides a rich, real-time view of agent orchestration with
live updates, progress tracking, and detailed communication logs.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Optional
import sys

# Set up file logging for debugging - NO CONSOLE OUTPUT
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('theatrical_debug.log', mode='w')
        # Removed StreamHandler to prevent console bleeding
    ]
)
logger = logging.getLogger('theatrical_dashboard')

# Suppress console logging for other modules 
for logger_name in ['agents.base', 'core.routing', 'httpx', 'theatrical_orchestrator', 'urllib3', 'httpcore']:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

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

from theatrical_orchestrator import TheatricalEvent, TheatricalOrchestrator


class AgentStatusWidget(Static):
    """Widget displaying individual agent status with activity log and metrics."""

    def __init__(self, agent_id: str, agent_name: str, **kwargs):
        super().__init__(**kwargs)
        # Store all attributes as regular attributes
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
        # Activity history - now unlimited, stored as list
        self.activity_history = []
        # Will store reference to scrollable activity container and labels
        self.activity_scroll = None
        self.activity_labels = []

    def compose(self) -> ComposeResult:
        """Create agent status display with scrollable activity log."""
        # Main content area with horizontal split
        with Horizontal(classes="agent-content"):
            # Left side: Scrollable activity log with compact header (70% width)
            with Vertical(classes="agent-activity"):
                # Compact agent header
                yield Label(f"{self.agent_name}", classes="agent-header")
                # Create vertically scrollable container
                self.activity_scroll = ScrollableContainer(
                    id=f"activity-scroll-{self.agent_id}",
                    classes="activity-scroll"
                )
                yield self.activity_scroll
            
            # Right side: Metrics and progress (30% width)
            with Vertical(classes="agent-metrics"):
                yield Label(f"Status: {self.status}", id=f"status-{self.agent_id}")
                yield ProgressBar(total=100, show_eta=False, id=f"progress-{self.agent_id}")
                yield Label(f"Tasks: 0/0", id=f"tasks-{self.agent_id}")
                yield Label(f"Time: 0.0s", id=f"time-{self.agent_id}")
                yield Label(f"Cost: $0.0000", id=f"cost-{self.agent_id}")
                yield Label(f"Tokens: 0", id=f"tokens-{self.agent_id}")

    def update_status(self, status: str, progress: Optional[int] = None, task: Optional[str] = None):
        """Update agent status display and log history."""
        self.status = status
        if progress is not None:
            self.progress = progress
        if task is not None:
            self.current_task = task

        self.last_update = time.time()

        # Track task assignment and completion
        if status == "thinking" and self.task_start_time is None:
            self.tasks_assigned += 1
            self.task_start_time = time.time()
        elif status == "success" and self.task_start_time is not None:
            self.tasks_completed += 1
            self.total_time += time.time() - self.task_start_time
            self.task_start_time = None

        # Update UI elements
        try:
            status_label = self.query_one(f"#status-{self.agent_id}", Label)
            status_label.update(f"Status: {status}")
        except:
            pass

        if progress is not None:
            try:
                progress_bar = self.query_one(f"#progress-{self.agent_id}", ProgressBar)
                progress_bar.progress = progress
            except:
                pass

        # Update task counter
        try:
            tasks_label = self.query_one(f"#tasks-{self.agent_id}", Label)
            tasks_label.update(f"Tasks: {self.tasks_completed}/{self.tasks_assigned}")
        except:
            pass

        # Update time
        try:
            time_label = self.query_one(f"#time-{self.agent_id}", Label)
            time_label.update(f"Time: {self.total_time:.1f}s")
        except:
            pass

        # Add new activity to unlimited history
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if task:
            # Keep task descriptions reasonable length to prevent horizontal scrolling
            display_task = task if len(task) <= 60 else task[:57] + "..."
            activity_text = f"{timestamp} {status}: {display_task}"
        else:
            activity_text = f"{timestamp} Status: {status}"
        
        # Add to unlimited activity history
        self.activity_history.append(activity_text)
        
        # Update scrollable container with new label
        if self.activity_scroll:
            try:
                # Create a new label for this activity
                activity_label = Label(activity_text, classes="activity-item")
                self.activity_labels.append(activity_label)
                
                # Mount the new label to the scrollable container
                self.activity_scroll.mount(activity_label)
                
                # Keep only last 100 activities to prevent memory issues
                if len(self.activity_labels) > 100:
                    old_label = self.activity_labels.pop(0)
                    old_label.remove()
                    self.activity_history.pop(0)
                
                # Auto-scroll to bottom to show latest activity
                self.activity_scroll.scroll_end()
                    
            except Exception as e:
                pass  # If mounting fails, just ignore

    def add_activity(self, activity_text: str):
        """Add an activity directly to the log (for manual additions)."""
        self.activity_history.append(activity_text)
        if self.activity_scroll:
            try:
                activity_label = Label(activity_text, classes="activity-item")
                self.activity_labels.append(activity_label)
                self.activity_scroll.mount(activity_label)
                self.activity_scroll.scroll_end()
            except:
                pass

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
    
    def clear_log(self):
        """Clear the agent's activity log and reset metrics."""
        # Clear activity history
        self.activity_history = []
        
        # Clear all activity labels
        if self.activity_scroll:
            try:
                for label in self.activity_labels:
                    label.remove()
                self.activity_labels = []
            except:
                pass
            
        # Reset metrics
        self.tasks_assigned = 0
        self.tasks_completed = 0
        self.total_time = 0.0
        self.total_cost = 0.0
        self.total_tokens = 0
        self.task_start_time = None


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

        # Format message
        formatted_message = f"{timestamp} [{initial}] {event.message}"
        
        # Create and mount the label
        if self.log_container:
            try:
                # Determine CSS class based on agent
                css_class = "event-log-item"
                if event.agent_id == "orchestrator":
                    css_class += " event-sys"
                elif event.agent_id == "cto-001":
                    css_class += " event-cto"
                elif event.agent_id == "backend-001":
                    css_class += " event-backend"
                elif event.agent_id == "frontend-001":
                    css_class += " event-frontend"
                elif event.agent_id == "qa-001":
                    css_class += " event-qa"
                elif event.agent_id == "devops-001":
                    css_class += " event-devops"
                
                label = Label(formatted_message, classes=css_class)
                self.log_labels.append(label)
                self.log_container.mount(label)
                
                # Keep only last 500 events
                if len(self.log_labels) > 500:
                    old_label = self.log_labels.pop(0)
                    old_label.remove()
                
                # Auto-scroll to bottom
                self.log_container.scroll_end()
            except Exception as e:
                pass
    
    def clear(self):
        """Clear all log entries."""
        if self.log_container:
            try:
                for label in self.log_labels:
                    label.remove()
                self.log_labels = []
            except:
                pass


class ProjectMetricsWidget(Static):
    """Widget showing project-wide metrics."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize as regular attributes
        self.total_cost = 0.0
        self.total_time = 0.0
        self.total_tokens = 0
        self.phases_complete = 0

    def compose(self) -> ComposeResult:
        """Create metrics display."""
        with Vertical():
            yield Label("📊 Project Metrics", classes="section-title")
            yield Label(f"💰 Cost: ${self.total_cost:.4f}", id="cost-metric")
            yield Label(f"⏱️ Time: {self.total_time:.1f}s", id="time-metric")
            yield Label(f"🔤 Tokens: {self.total_tokens:,}", id="tokens-metric")
            yield Label(f"📋 Phases: {self.phases_complete}/5", id="phases-metric")

    def update_metrics(self, cost: Optional[float] = None, time_elapsed: Optional[float] = None,
                      tokens: Optional[int] = None, phases: Optional[int] = None):
        """Update metric display."""
        if cost is not None:
            self.total_cost = cost
            cost_label = self.query_one("#cost-metric", Label)
            cost_label.update(f"💰 Cost: ${cost:.4f}")

        if time_elapsed is not None:
            self.total_time = time_elapsed
            time_label = self.query_one("#time-metric", Label)
            time_label.update(f"⏱️ Time: {time_elapsed:.1f}s")

        if tokens is not None:
            self.total_tokens = tokens
            tokens_label = self.query_one("#tokens-metric", Label)
            tokens_label.update(f"🔤 Tokens: {tokens:,}")

        if phases is not None:
            self.phases_complete = phases
            phases_label = self.query_one("#phases-metric", Label)
            phases_label.update(f"📋 Phases: {phases}/5")


class ProjectDescriptionWidget(Static):
    """Custom widget for project description that properly updates."""
    
    project_text = reactive("🎯 Project: Real-time Chat Application with WebSocket support, user authentication, and message history")
    
    def render(self) -> str:
        """Render the project text."""
        return self.project_text


class TheatricalMonitoringApp(App):
    """
    Main monitoring application for theatrical agent orchestration.
    """

    CSS = """
    Static#project-info {
        height: 3;
        border: solid yellow;
        text-align: center;
        color: yellow;
        content-align: center middle;
    }
    
    DataTable {
        scrollbar-size: 1 1;
    }
    
    DataTable > .datatable--cursor {
        display: none;
    }
    
    DataTable:focus .datatable--cursor {
        display: none;
    }

    .agent-panel {
        width: 100%;
        height: 18%;
        border: solid $primary;
        margin: 1;
        padding: 1;
    }

    .agent-header {
        background: $surface;
        color: $text;
        text-align: center;
        height: 1;
        margin-bottom: 1;
    }

    .agent-content {
        height: 100%;
    }
    
    .agent-activity {
        width: 70%;
        padding-right: 1;
        border-right: solid $surface;
    }
    
    .agent-metrics {
        width: 30%;
        padding-left: 1;
    }
    
    .activity-scroll {
        height: 1fr;
        border: solid $surface;
        margin: 0 1;
        scrollbar-size: 1 1;
        scrollbar-background: $background;
        scrollbar-color: $primary;
        scrollbar-corner-color: $background;
    }
    
    .activity-item {
        height: auto;
        width: 100%;
        padding: 0 1;
        margin: 0;
    }

    .section-title {
        text-align: center;
        background: $secondary;
        color: $text;
        margin-bottom: 1;
    }


    .metrics-panel {
        width: 25%;
        border: solid $success;
        margin: 1;
    }

    .log-panel {
        border: solid $warning;
        margin: 1;
        height: 1fr;
    }
    
    .event-log-scroll {
        height: 1fr;
        border: solid $surface;
        margin: 1;
        scrollbar-size: 1 1;
        scrollbar-background: $background;
        scrollbar-color: $primary;
        scrollbar-corner-color: $background;
        overflow-y: auto;
    }
    
    .event-log-item {
        height: auto;
        width: 100%;
        padding: 0 1;
        margin: 0;
    }
    
    .event-sys { color: $primary; }
    .event-cto { color: $accent; }
    .event-backend { color: $success; }
    .event-frontend { color: $secondary; }
    .event-qa { color: $warning; }
    .event-devops { color: $error; }
    .event-default { color: $text; }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "start_demo", "Start Demo"),
        ("r", "reset", "Reset"),
        ("e", "export_log", "Export Full Log"),
        ("p", "export_performance", "Export Performance"),
    ]

    def __init__(self):
        super().__init__()
        self.orchestrator: Optional[TheatricalOrchestrator] = None
        self.agent_widgets: Dict[str, AgentStatusWidget] = {}
        self.event_log: Optional[EventLogWidget] = None
        self.project_widget: Optional[ProjectDescriptionWidget] = None
        self.demo_running = False  # Use a different name to avoid conflict
        self.start_time: Optional[float] = None
        self.total_elapsed: float = 0.0
        self.current_project: str = "Unknown Project"

    def on_mount(self) -> None:
        """Initialize after mounting."""
        pass
    
    def compose(self) -> ComposeResult:
        """Create the monitoring dashboard layout."""
        logger.info("\n=== COMPOSE STARTED ===")
        yield Header(show_clock=True)

        with Container():
            # PROJECT DESCRIPTION - EXACTLY LIKE WORKING VERSION
            self.project_widget = Static("🎯 Project: INITIAL TEXT", id="project-info")
            yield self.project_widget
            
            with TabbedContent():
                with TabPane("Agent Orchestra", id="agents-tab"):
                    # Changed from Horizontal to Vertical for stacked layout
                    with Vertical():
                        
                        # Agent status panels - now stacked vertically
                        self.agent_widgets["cto-001"] = AgentStatusWidget(
                            "cto-001", "🏛️ CTO Agent"
                        )
                        self.agent_widgets["cto-001"].classes = "agent-panel"
                        yield self.agent_widgets["cto-001"]

                        self.agent_widgets["backend-001"] = AgentStatusWidget(
                            "backend-001", "⚙️ Backend Dev"
                        )
                        self.agent_widgets["backend-001"].classes = "agent-panel"
                        yield self.agent_widgets["backend-001"]

                        self.agent_widgets["frontend-001"] = AgentStatusWidget(
                            "frontend-001", "🎨 Frontend Dev"
                        )
                        self.agent_widgets["frontend-001"].classes = "agent-panel"
                        yield self.agent_widgets["frontend-001"]

                        self.agent_widgets["qa-001"] = AgentStatusWidget(
                            "qa-001", "🧪 QA Engineer"
                        )
                        self.agent_widgets["qa-001"].classes = "agent-panel"
                        yield self.agent_widgets["qa-001"]

                        self.agent_widgets["devops-001"] = AgentStatusWidget(
                            "devops-001", "🚀 DevOps"
                        )
                        self.agent_widgets["devops-001"].classes = "agent-panel"
                        yield self.agent_widgets["devops-001"]

                with TabPane("Full Log", id="log-tab"):
                    # Full-width event log
                    yield Label("📜 Complete Agent Timeline", classes="section-title")
                    self.event_log = EventLogWidget(classes="log-panel")
                    yield self.event_log

                with TabPane("Performance", id="performance-tab"):
                    with Vertical():
                        yield Label("📊 Agent Performance Comparison", classes="section-title")
                        # Agent performance comparison table (non-selectable)
                        self.performance_table = DataTable(id="performance-table", cursor_type="none")
                        self.performance_table.add_columns("Agent", "Tasks", "Time (s)", "Cost ($)", "Tokens", "Avg/Task")
                        # Initialize with agent rows
                        agents = [
                            ("🏛️ CTO", "0", "0.0", "0.0000", "0", "0.0"),
                            ("⚙️ Backend", "0", "0.0", "0.0000", "0", "0.0"),
                            ("🎨 Frontend", "0", "0.0", "0.0000", "0", "0.0"),
                            ("🧪 QA", "0", "0.0", "0.0000", "0", "0.0"),
                            ("🚀 DevOps", "0", "0.0", "0.0000", "0", "0.0"),
                            ("🔧 Setup/Other", "0", "0.0", "0.0000", "0", "0.0"),
                        ]
                        for agent_data in agents:
                            self.performance_table.add_row(*agent_data)
                        # Add totalization row
                        self.performance_table.add_row("📊 TOTAL", "0", "0.0", "0.0000", "0", "0.0")
                        yield self.performance_table

            # No control panel - using keybindings instead for minimalist approach

        yield Footer()

    async def start_demo(self):
        """Start the theatrical demo."""
        if self.demo_running:
            self.notify("Demo already running!", severity="warning")
            return

        self.demo_running = True
        self.start_time = time.time()

        # Update project description using the reactive property
        project = "Real-time Chat Application with WebSocket support, user authentication, and message history"
        self.current_project = project
        
        logger.info("\n=== START_DEMO UPDATE ATTEMPT ===")
        logger.info(f"Trying to update to: '🎯 Project: {project}'")
        
        # COPY EXACT WORKING VERSION APPROACH
        try:
            project_static = self.query_one("#project-info", Static)
            project_static.update(f"🎯 Project: {project}")
            logger.info("EXACT COPY: Updated project static like working version")
            self.notify("✅ EXACT COPY UPDATE!", severity="success")
        except Exception as e:
            logger.error(f"Failed exact copy update: {e}")
            self.notify("❌ Exact copy failed!", severity="error")

        # Reset displays and start with real activities
        for widget in self.agent_widgets.values():
            # Add a welcome message to the scrollable log
            widget.add_activity("🎭 Scrollable activity log ready - you can now scroll through full history!")
            widget.update_status("idle", 0, "Demo starting - waiting for initialization...")

        if self.event_log:
            self.event_log.clear()

        # Initialize orchestrator
        self.orchestrator = TheatricalOrchestrator(
            theatrical_delay=1.5,  # Faster for dashboard
            show_details=True
        )

        # Start monitoring task
        asyncio.create_task(self._run_orchestration())

        self.notify("🎭 Theatrical orchestration started!", severity="success")

    def reset_demo(self):
        """Reset the demo."""
        self.demo_running = False
        self.total_elapsed = 0.0

        for widget in self.agent_widgets.values():
            widget.clear_log()  # Clear the history log
            widget.update_status("idle", 0, "Ready")

        if self.event_log:
            self.event_log.clear()

        # Reset performance table including setup row
        if hasattr(self, 'performance_table'):
            try:
                # Reset Setup/Other row
                self.performance_table.update_cell_at((5, 1), "-")
                self.performance_table.update_cell_at((5, 2), "0.0")
                self.performance_table.update_cell_at((5, 3), "0.0000")
                self.performance_table.update_cell_at((5, 4), "0")
                self.performance_table.update_cell_at((5, 5), "-")
                # Reset TOTAL row
                self.performance_table.update_cell_at((6, 1), "0")
                self.performance_table.update_cell_at((6, 2), "0.0")
                self.performance_table.update_cell_at((6, 3), "0.0000")
                self.performance_table.update_cell_at((6, 4), "0")
                self.performance_table.update_cell_at((6, 5), "0.0s")
            except:
                pass

        self.notify("🔄 Demo reset", severity="information")

    def export_conversation(self):
        """Export the full conversation to JSON."""
        import json
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aiosv3_conversation_{timestamp}.json"
        
        try:
            # Collect all conversation data
            export_data = {
                "export_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "project": getattr(self, 'current_project', 'Unknown Project'),
                    "session_duration": time.time() - (self.start_time or time.time()),
                    "total_agents": len(self.agent_widgets)
                },
                "project_description": getattr(self, 'current_project', 'No project description available'),
                "agent_activities": {},
                "orchestrator_events": [],
                "performance_summary": {}
            }
            
            # Export each agent's activity history
            for agent_id, widget in self.agent_widgets.items():
                agent_name = widget.agent_name
                export_data["agent_activities"][agent_id] = {
                    "name": agent_name,
                    "activity_history": widget.activity_history,
                    "performance": {
                        "tasks_completed": widget.tasks_completed,
                        "total_time": widget.total_time,
                        "total_cost": widget.total_cost,
                        "total_tokens": widget.total_tokens
                    }
                }
            
            # Export orchestrator events if available
            if self.orchestrator and hasattr(self.orchestrator, 'events'):
                export_data["orchestrator_events"] = [
                    {
                        "timestamp": event.timestamp.isoformat(),
                        "event_type": event.event_type,
                        "agent_id": event.agent_id,
                        "agent_role": event.agent_role,
                        "message": event.message,
                        "details": event.details
                    }
                    for event in self.orchestrator.events
                ]
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.notify(f"📤 Conversation exported to {filename}", severity="success")
            
        except Exception as e:
            self.notify(f"❌ Export failed: {e}", severity="error")

    def save_log(self):
        """Save the event log to text file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"theatrical_log_{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                # Write header
                f.write(f"AIOSv3 Theatrical Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Project: {getattr(self, 'current_project', 'Unknown')}\n")
                f.write("=" * 80 + "\n\n")
                
                # Write all log entries
                if self.event_log and hasattr(self.event_log, 'log_labels'):
                    for label in self.event_log.log_labels:
                        f.write(label.renderable + "\n")
                
            self.notify(f"💾 Log saved as {filename}", severity="success")
            
        except Exception as e:
            self.notify(f"❌ Save failed: {e}", severity="error")

    async def _run_orchestration(self):
        """Run the orchestration with live monitoring."""
        try:
            if not self.orchestrator:
                return

            await self.orchestrator.initialize()

            # Update agent statuses as initialization happens
            for agent_id in self.agent_widgets.keys():
                self.agent_widgets[agent_id].update_status("initializing", 10, "Setting up...")
                await asyncio.sleep(0.5)

            # Start the project
            project = "Real-time Chat Application with WebSocket support, user authentication, and message history"
            self.current_project = project
            
            # Update project description using correct ID
            try:
                project_static = self.query_one("#project-info", Static)
                project_static.update(f"🎯 Project: {project}")
                logger.info("Updated project STATIC for orchestration using correct ID")
            except Exception as e:
                logger.error(f"Failed to update project widget in orchestration: {e}")

            # Start monitoring BEFORE orchestration begins
            monitor_task = asyncio.create_task(self._monitor_events())
            
            # Small delay to ensure monitoring is active
            await asyncio.sleep(0.1)

            await self.orchestrator.orchestrate_project(project)
            
            # Cancel monitoring task when done
            monitor_task.cancel()

            self.notify("🎉 Orchestration completed successfully!", severity="success")

        except Exception as e:
            self.notify(f"❌ Orchestration failed: {e}", severity="error")
        finally:
            self.demo_running = False
            if self.orchestrator:
                await self.orchestrator.shutdown()

    async def _monitor_events(self):
        """Monitor orchestrator events and update dashboard."""
        if not self.orchestrator:
            return

        last_event_count = 0
        phase_progress = {
            "architecture": 0,
            "backend": 1,
            "frontend": 2,
            "testing": 3,
            "deployment": 4
        }

        while self.demo_running:
            try:
                # Check for new events
                current_event_count = len(self.orchestrator.events)

                if current_event_count > last_event_count:
                    # Process new events
                    new_events = self.orchestrator.events[last_event_count:]

                    for event in new_events:
                        # Log event
                        if self.event_log:
                            self.event_log.log_event(event)

                        # Update agent status based on event
                        await self._update_agent_from_event(event)

                        # Update performance table
                        self._update_performance_table()
                        
                        # Also update total elapsed time if we have start_time
                        if self.start_time:
                            self.total_elapsed = time.time() - self.start_time

                    last_event_count = current_event_count

                await asyncio.sleep(0.5)  # Check for updates twice per second

            except Exception as e:
                self.notify(f"Monitoring error: {e}", severity="error")
                break

    async def _update_agent_from_event(self, event: TheatricalEvent):
        """Update agent widget based on event."""
        agent_id = event.agent_id

        if agent_id not in self.agent_widgets:
            return

        widget = self.agent_widgets[agent_id]

        # Map event types to status updates - always update with event message for debugging
        if event.event_type == "THINKING":
            widget.update_status("thinking", progress=25, task=event.message)
        elif event.event_type == "TASK":
            widget.update_status("working", progress=50, task=event.message)
        elif event.event_type == "SUCCESS":
            widget.update_status("success", progress=100, task=event.message)  # Show actual message
        elif event.event_type == "ERROR":
            widget.update_status("error", progress=0, task=event.message)  # Show actual message
        elif event.event_type == "PHASE":
            widget.update_status("active", progress=10, task=event.message)
        elif event.event_type == "INIT":
            widget.update_status("initializing", progress=15, task=event.message)
        elif event.event_type == "SYSTEM":
            # Show system messages for orchestrator
            if agent_id == "orchestrator":
                # Update all agents to show system status
                for w in self.agent_widgets.values():
                    w.update_status("ready", progress=5, task=f"System: {event.message}")
        elif event.event_type == "DETAILS":
            # Extract cost and time from details event
            if "Cost:" in event.message and "$" in event.message:
                try:
                    cost_str = event.message.split("$")[1].split()[0]
                    cost = float(cost_str)
                    widget.update_metrics(cost=cost)
                except:
                    pass
            # Extract tokens if available
            if event.details and "tokens" in event.details:
                widget.update_metrics(tokens=event.details["tokens"])
        

    def action_start_demo(self) -> None:
        """Action for start demo keybind."""
        asyncio.create_task(self.start_demo())

    def action_reset(self) -> None:
        """Action for reset keybind."""
        self.reset_demo()
    
    def action_export_log(self) -> None:
        """Export full conversation log."""
        self.export_conversation()
    
    def action_export_performance(self) -> None:
        """Export performance metrics to CSV."""
        import csv
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aiosv3_performance_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Agent', 'Tasks', 'Time (s)', 'Cost ($)', 'Tokens', 'Avg/Task'])
                
                # Write agent data
                agent_names = {
                    "cto-001": "CTO",
                    "backend-001": "Backend",
                    "frontend-001": "Frontend",
                    "qa-001": "QA",
                    "devops-001": "DevOps"
                }
                
                total_tasks = 0
                total_time = 0.0
                total_cost = 0.0
                total_tokens = 0
                
                for agent_id, widget in self.agent_widgets.items():
                    name = agent_names.get(agent_id, agent_id)
                    avg_time = widget.total_time / widget.tasks_completed if widget.tasks_completed > 0 else 0.0
                    
                    writer.writerow([
                        name,
                        widget.tasks_completed,
                        f"{widget.total_time:.1f}",
                        f"{widget.total_cost:.4f}",
                        widget.total_tokens,
                        f"{avg_time:.1f}"
                    ])
                    
                    total_tasks += widget.tasks_completed
                    total_time += widget.total_time
                    total_cost += widget.total_cost
                    total_tokens += widget.total_tokens
                
                # Write Setup/Other row
                display_time = self.total_elapsed if hasattr(self, 'total_elapsed') and self.total_elapsed > 0 else total_time
                setup_time = max(0, display_time - total_time)
                
                writer.writerow([
                    'Setup/Other',
                    '-',
                    f"{setup_time:.1f}",
                    '0.0000',
                    '0',
                    '-'
                ])
                
                # Write totals
                avg_total = display_time / total_tasks if total_tasks > 0 else 0.0
                
                writer.writerow([
                    'TOTAL',
                    total_tasks,
                    f"{display_time:.1f}",
                    f"{total_cost:.4f}",
                    total_tokens,
                    f"{avg_total:.1f}"
                ])
                
            self.notify(f"📤 Performance exported to {filename}", severity="success")
            
        except Exception as e:
            self.notify(f"❌ Export failed: {e}", severity="error")
    
    def _update_performance_table(self):
        """Update the performance table with current agent data."""
        if not hasattr(self, 'performance_table'):
            return
            
        try:
            # Agent mapping for table rows
            agent_row_map = {
                "cto-001": 0,
                "backend-001": 1,
                "frontend-001": 2,
                "qa-001": 3,
                "devops-001": 4
            }
            
            # Track totals for summary row
            total_tasks = 0
            total_time = 0.0
            total_cost = 0.0
            total_tokens = 0
            
            for agent_id, widget in self.agent_widgets.items():
                if agent_id in agent_row_map:
                    row_index = agent_row_map[agent_id]
                    
                    # Calculate average time per task
                    avg_time = widget.total_time / widget.tasks_completed if widget.tasks_completed > 0 else 0.0
                    
                    # Update table row
                    self.performance_table.update_cell_at(
                        (row_index, 1), str(widget.tasks_completed)  # Tasks
                    )
                    self.performance_table.update_cell_at(
                        (row_index, 2), f"{widget.total_time:.1f}"  # Time
                    )
                    self.performance_table.update_cell_at(
                        (row_index, 3), f"{widget.total_cost:.4f}"  # Cost
                    )
                    self.performance_table.update_cell_at(
                        (row_index, 4), str(widget.total_tokens)  # Tokens
                    )
                    self.performance_table.update_cell_at(
                        (row_index, 5), f"{avg_time:.1f}s"  # Avg per task
                    )
                    
                    # Add to totals
                    total_tasks += widget.tasks_completed
                    total_time += widget.total_time
                    total_cost += widget.total_cost
                    total_tokens += widget.total_tokens
            
            # Calculate setup/other time (difference between elapsed and agent time)
            display_time = self.total_elapsed if hasattr(self, 'total_elapsed') and self.total_elapsed > 0 else total_time
            setup_time = max(0, display_time - total_time)
            
            # Update Setup/Other row (row 5)
            self.performance_table.update_cell_at((5, 1), "-")  # No tasks for setup
            self.performance_table.update_cell_at((5, 2), f"{setup_time:.1f}")
            self.performance_table.update_cell_at((5, 3), "0.0000")  # No cost for setup
            self.performance_table.update_cell_at((5, 4), "0")  # No tokens for setup
            self.performance_table.update_cell_at((5, 5), "-")  # No avg for setup
            
            # Update totalization row (row 6)
            avg_total_time = display_time / total_tasks if total_tasks > 0 else 0.0
            
            self.performance_table.update_cell_at((6, 1), str(total_tasks))
            self.performance_table.update_cell_at((6, 2), f"{display_time:.1f}")
            self.performance_table.update_cell_at((6, 3), f"{total_cost:.4f}")
            self.performance_table.update_cell_at((6, 4), str(total_tokens))
            self.performance_table.update_cell_at((6, 5), f"{avg_total_time:.1f}s")
            
        except Exception as e:
            # Silently handle any table update errors
            pass


# Standalone dashboard launcher
async def main():
    """Launch the theatrical monitoring dashboard."""
    app = TheatricalMonitoringApp()
    await app.run_async()


if __name__ == "__main__":
    asyncio.run(main())
