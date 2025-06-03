"""
Theatrical Monitoring Dashboard - SIMPLE VERSION THAT WORKS
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional

# NO CONSOLE LOGGING
logging.basicConfig(
    level=logging.ERROR,
    handlers=[logging.FileHandler('theatrical_debug.log', mode='w')]
)

# Suppress all module logging
for logger_name in ['agents.base', 'core.routing', 'httpx', 'theatrical_orchestrator', 'urllib3', 'httpcore']:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Static, Header, Footer, TabbedContent, TabPane, Label, ProgressBar

from theatrical_orchestrator import TheatricalOrchestrator, TheatricalEvent


class SimpleEventLog(Static):
    """Simple event log widget using text updates."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.events = []
        self.log_display = None
    
    def compose(self) -> ComposeResult:
        """Create the event log display."""
        with ScrollableContainer(classes="event-log-scroll"):
            self.log_display = Static("Events will appear here...", classes="event-display")
            yield self.log_display
    
    def add_event(self, event: TheatricalEvent):
        """Add an event to the log safely."""
        try:
            timestamp = event.timestamp.strftime("%H:%M:%S")
            agent_name = event.agent_role or event.agent_id
            message = f"{timestamp} [{agent_name}] {event.message}"
            
            self.events.append(message)
            
            # Keep only last 50 events to prevent performance issues
            if len(self.events) > 50:
                self.events = self.events[-50:]
            
            # Update display with all events
            if self.log_display:
                try:
                    self.log_display.update("\n".join(self.events))
                except Exception as e:
                    # If update fails, just continue
                    pass
        except Exception as e:
            # Silently handle any errors to prevent crashes
            pass


class SimpleAgentPanel(Static):
    """Enhanced agent status panel with progress and metrics."""
    
    def __init__(self, agent_id: str, agent_name: str, **kwargs):
        super().__init__(**kwargs)
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.activities = []
        # Performance metrics
        self.tasks_assigned = 0
        self.tasks_completed = 0
        self.total_time = 0.0
        self.total_cost = 0.0
        self.total_tokens = 0
        self.progress = 0
    
    def compose(self) -> ComposeResult:
        """Create enhanced agent panel with metrics."""
        with Horizontal(classes="agent-content"):
            # Left side: Activity log (70% width)
            with Vertical(classes="agent-activity"):
                yield Static(f"{self.agent_name}", classes="agent-title")
                yield Static("Activities will appear here...", id=f"activities-{self.agent_id}")
            
            # Right side: Metrics and progress (30% width)
            with Vertical(classes="agent-metrics"):
                yield Static("Status: idle", id=f"status-{self.agent_id}")
                yield ProgressBar(total=100, show_eta=False, id=f"progress-{self.agent_id}")
                yield Static("Tasks: 0/0", id=f"tasks-{self.agent_id}")
                yield Static("Time: 0.0s", id=f"time-{self.agent_id}")
                yield Static("Cost: $0.0000", id=f"cost-{self.agent_id}")
                yield Static("Tokens: 0", id=f"tokens-{self.agent_id}")
    
    def update_status(self, status: str, activity: str = "", progress: int = None):
        """Update agent status with optional progress."""
        # Update status
        try:
            status_widget = self.query_one(f"#status-{self.agent_id}")
            status_widget.update(f"Status: {status}")
        except:
            pass
        
        # Update progress
        if progress is not None:
            self.progress = progress
            try:
                progress_bar = self.query_one(f"#progress-{self.agent_id}")
                progress_bar.progress = progress
            except:
                pass
        
        # Track task progression
        if status == "thinking" and self.tasks_assigned == self.tasks_completed:
            self.tasks_assigned += 1
            self.progress = 25
        elif status == "working":
            self.progress = 50
        elif status == "success":
            self.tasks_completed += 1
            self.progress = 100
        elif status == "error":
            self.progress = 0
        
        # Update progress bar
        try:
            progress_bar = self.query_one(f"#progress-{self.agent_id}")
            progress_bar.progress = self.progress
        except:
            pass
        
        # Update task counter
        try:
            tasks_widget = self.query_one(f"#tasks-{self.agent_id}")
            tasks_widget.update(f"Tasks: {self.tasks_completed}/{self.tasks_assigned}")
        except:
            pass
        
        # Add activity
        if activity:
            self.activities.append(f"{datetime.now().strftime('%H:%M:%S')}: {activity}")
            # Keep only last 3 activities
            if len(self.activities) > 3:
                self.activities = self.activities[-3:]
            
            try:
                activities_widget = self.query_one(f"#activities-{self.agent_id}")
                activities_widget.update("\n".join(self.activities))
            except:
                pass
    
    def update_metrics(self, cost: float = None, tokens: int = None, time_elapsed: float = None):
        """Update performance metrics."""
        if cost is not None:
            self.total_cost += cost
            try:
                cost_widget = self.query_one(f"#cost-{self.agent_id}")
                cost_widget.update(f"Cost: ${self.total_cost:.4f}")
            except:
                pass
        
        if tokens is not None:
            self.total_tokens += tokens
            try:
                tokens_widget = self.query_one(f"#tokens-{self.agent_id}")
                tokens_widget.update(f"Tokens: {self.total_tokens:,}")
            except:
                pass
        
        if time_elapsed is not None:
            self.total_time = time_elapsed
            try:
                time_widget = self.query_one(f"#time-{self.agent_id}")
                time_widget.update(f"Time: {self.total_time:.1f}s")
            except:
                pass


class SimpleTheatricalApp(App):
    """Simple theatrical monitoring app."""
    
    CSS = """
    Static#project-info {
        height: 3;
        border: solid yellow;
        text-align: center;
        color: yellow;
        content-align: center middle;
    }
    
    .agent-panel {
        height: 15;
        border: solid blue;
        margin: 1;
        padding: 1;
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
    
    .agent-title {
        color: white;
        text-style: bold;
        text-align: center;
        height: 1;
        margin-bottom: 1;
    }
    
    .log-placeholder {
        height: 1fr;
        border: solid gray;
        margin: 1;
        padding: 2;
        content-align: center middle;
        color: gray;
    }
    
    .perf-placeholder {
        height: 1fr;
        border: solid gray;
        margin: 1;
        padding: 2;
        content-align: center middle;
        color: gray;
    }
    
    .full-event-log {
        height: 1fr;
        border: solid green;
        margin: 1;
    }
    
    .event-log-scroll {
        height: 1fr;
        scrollbar-size: 1 1;
    }
    
    .event-item {
        height: auto;
        width: 100%;
        color: $text;
        margin: 0;
    }
    
    .event-display {
        height: auto;
        width: 100%;
        color: $text;
        margin: 0;
        padding: 1;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "start_demo", "Start Demo"),
        ("r", "stop_demo", "Stop Demo"),
    ]
    
    def __init__(self):
        super().__init__()
        self.agents = {}
        self.orchestrator = None
        self.demo_running = False
        self.event_log = None
    
    def compose(self) -> ComposeResult:
        """Create the app layout."""
        yield Header(show_clock=True)
        
        with Container():
            # PROJECT DESCRIPTION - SIMPLE STATIC TEXT
            yield Static(
                "🎯 Project: Real-time Chat Application with WebSocket support", 
                id="project-info"
            )
            
            # TABBED INTERFACE
            with TabbedContent():
                with TabPane("Agent Orchestra", id="agents-tab"):
                    # AGENT PANELS (our working dashboard)
                    with Vertical():
                        self.agents["cto"] = SimpleAgentPanel("cto", "🏛️ CTO Agent", classes="agent-panel")
                        yield self.agents["cto"]
                        
                        self.agents["backend"] = SimpleAgentPanel("backend", "⚙️ Backend Dev", classes="agent-panel")
                        yield self.agents["backend"]
                        
                        self.agents["frontend"] = SimpleAgentPanel("frontend", "🎨 Frontend Dev", classes="agent-panel")
                        yield self.agents["frontend"]
                
                with TabPane("Full Log", id="log-tab"):
                    # Real event log with safety wrapper
                    yield Label("📜 Complete Agent Timeline")
                    try:
                        self.event_log = SimpleEventLog(classes="full-event-log")
                        yield self.event_log
                    except Exception as e:
                        # Fallback if event log creation fails
                        yield Static("Event log initialization failed - events will appear after restart", classes="log-placeholder")
                
                with TabPane("Performance", id="performance-tab"):
                    # Placeholder for performance metrics
                    yield Label("📊 Agent Performance Comparison")
                    yield Static("Performance metrics will appear here...", classes="perf-placeholder")
        
        yield Footer()
    
    def action_start_demo(self):
        """Start the demo (non-blocking)."""
        if self.demo_running:
            return
        
        self.demo_running = True
        self.notify("🎭 Starting demo...")
        
        # Update agents
        for agent in self.agents.values():
            agent.update_status("initializing", "Setting up...")
        
        # Start orchestration task in background - IMMEDIATELY RETURN
        asyncio.create_task(self._run_orchestration())
        
        self.notify("🎭 Theatrical orchestration started!", severity="success")
    
    async def _run_orchestration(self):
        """Run the orchestration with live monitoring."""
        try:
            # Initialize orchestrator
            self.orchestrator = TheatricalOrchestrator(theatrical_delay=1.5, show_details=True)
            await self.orchestrator.initialize()
            
            # Start monitoring BEFORE orchestration begins
            monitor_task = asyncio.create_task(self._monitor_orchestrator_events())
            
            # Small delay to ensure monitoring is active
            await asyncio.sleep(0.1)
            
            # Run the project orchestration
            project = "Real-time Chat Application with WebSocket support, user authentication, and message history"
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
    
    async def _monitor_orchestrator_events(self):
        """Monitor orchestrator events and update dashboard."""
        if not self.orchestrator:
            return
        
        last_event_count = 0
        
        while self.demo_running:
            try:
                # Check for new events
                current_event_count = len(self.orchestrator.events)
                
                if current_event_count > last_event_count:
                    # Process new events
                    new_events = self.orchestrator.events[last_event_count:]
                    
                    for event in new_events:
                        # Add to event log safely
                        try:
                            if self.event_log:
                                self.event_log.add_event(event)
                        except Exception as e:
                            # Don't let event log errors break the whole monitoring
                            pass
                        
                        # Update agent status based on event
                        try:
                            await self._update_agent_from_event(event)
                        except Exception as e:
                            # Don't let agent update errors break monitoring
                            pass
                    
                    last_event_count = current_event_count
                
                await asyncio.sleep(0.5)  # Check twice per second
                
            except Exception as e:
                self.notify(f"Monitoring error: {e}")
                break
    
    async def _update_agent_from_event(self, event: TheatricalEvent):
        """Update agent panel based on orchestrator event."""
        # Map agent IDs to our dashboard agents
        agent_mapping = {
            "cto-001": "cto",
            "backend-001": "backend", 
            "frontend-001": "frontend"
        }
        
        dashboard_agent_id = agent_mapping.get(event.agent_id)
        if not dashboard_agent_id or dashboard_agent_id not in self.agents:
            return
        
        agent_panel = self.agents[dashboard_agent_id]
        
        # Map event types to statuses and extract metrics
        if event.event_type == "THINKING":
            agent_panel.update_status("thinking", event.message)
        elif event.event_type == "TASK":
            agent_panel.update_status("working", event.message)
        elif event.event_type == "SUCCESS":
            agent_panel.update_status("success", event.message)
        elif event.event_type == "ERROR":
            agent_panel.update_status("error", event.message)
        elif event.event_type == "PHASE":
            agent_panel.update_status("active", event.message)
        elif event.event_type == "INIT":
            agent_panel.update_status("initializing", event.message)
        elif event.event_type == "DETAILS":
            # Extract cost and tokens from details
            if event.details:
                cost = event.details.get("cost", 0)
                tokens = event.details.get("tokens", 0)
                if cost > 0 or tokens > 0:
                    agent_panel.update_metrics(cost=cost, tokens=tokens)
    
    def action_stop_demo(self):
        """Stop the running demo."""
        if not self.demo_running:
            self.notify("No demo running")
            return
        
        self.demo_running = False
        
        # Reset agent states
        for agent in self.agents.values():
            agent.update_status("idle", "Ready")
        
        self.notify("🛑 Demo stopped")


async def main():
    """Run the app."""
    app = SimpleTheatricalApp()
    await app.run_async()


if __name__ == "__main__":
    asyncio.run(main())