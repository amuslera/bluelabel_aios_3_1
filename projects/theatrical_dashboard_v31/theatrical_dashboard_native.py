#!/usr/bin/env python3
"""
Native v3.1 Theatrical Dashboard - Built from scratch for v3.1 architecture
Inspired by v3.0's beautiful 3-tab design but using v3.1's agents
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
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
from textual.reactive import reactive

# Import v3.1 components
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.agents.specialists.backend_agent import BackendAgent
from src.agents.specialists.frontend_agent import FrontendAgent
from src.agents.specialists.qa_agent import QAAgent
from src.agents.specialists.devops_agent import DevOpsAgent


class AgentStatus(Static):
    """Individual agent status panel"""
    
    def __init__(self, agent_id: str, agent_name: str, agent_role: str, **kwargs):
        super().__init__(**kwargs)
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.agent_role = agent_role
        self.status = "idle"
        self.progress = 0
        self.current_task = "Waiting..."
        self.tasks_completed = 0
        self.activity_log = []
        
    def compose(self) -> ComposeResult:
        """Create the agent panel layout"""
        with Vertical(classes="agent-panel"):
            # Agent header
            yield Label(f"{self.agent_name} - {self.agent_role}", classes="agent-header")
            
            # Status and progress
            yield Label(f"Status: {self.status}", id=f"status-{self.agent_id}")
            yield ProgressBar(total=100, id=f"progress-{self.agent_id}")
            
            # Current task
            yield Label(f"Current: {self.current_task}", id=f"task-{self.agent_id}")
            
            # Activity log (scrollable)
            with ScrollableContainer(classes="activity-container"):
                yield Log(id=f"log-{self.agent_id}", highlight=True, max_lines=50)
                
    def update_status(self, status: str, task: str = None, progress: int = None):
        """Update agent status"""
        self.status = status
        if task:
            self.current_task = task
        if progress is not None:
            self.progress = progress
            
        # Update UI elements
        self.query_one(f"#status-{self.agent_id}", Label).update(f"Status: {status}")
        self.query_one(f"#task-{self.agent_id}", Label).update(f"Current: {self.current_task}")
        if progress is not None:
            self.query_one(f"#progress-{self.agent_id}", ProgressBar).progress = progress
            
    def add_activity(self, message: str, level: str = "info"):
        """Add activity to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_widget = self.query_one(f"#log-{self.agent_id}", Log)
        
        # Color coding based on level
        if level == "success":
            log_widget.write_line(f"[green]{timestamp}[/green] ✅ {message}")
        elif level == "error":
            log_widget.write_line(f"[red]{timestamp}[/red] ❌ {message}")
        elif level == "working":
            log_widget.write_line(f"[yellow]{timestamp}[/yellow] 🔄 {message}")
        else:
            log_widget.write_line(f"[blue]{timestamp}[/blue] ℹ️ {message}")


class TheatricalDashboardV31(App):
    """Native v3.1 Theatrical Dashboard with v3.0's design philosophy"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    .agent-panel {
        border: solid $primary;
        padding: 1;
        margin: 1;
        height: 100%;
    }
    
    .agent-header {
        text-style: bold;
        color: $primary;
        text-align: center;
        margin-bottom: 1;
    }
    
    .activity-container {
        height: 15;
        border: solid $secondary;
        margin-top: 1;
    }
    
    #team-chat {
        border: solid $accent;
        padding: 1;
        height: 20;
    }
    
    #metrics-panel {
        border: solid $success;
        padding: 1;
        height: 10;
    }
    
    DataTable {
        height: 100%;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.agent_panels = {}
        self.start_time = None
        self.metrics = {
            "lines_written": 0,
            "tests_passed": 0,
            "bugs_found": 0,
            "deployments": 0
        }
        self.full_log = []
        self.performance_data = []
        
    def compose(self) -> ComposeResult:
        """Create the dashboard layout"""
        yield Header(show_clock=True)
        
        with TabbedContent():
            # Tab 1: Agents View
            with TabPane("Agents", id="agents-tab"):
                with Container():
                    # Agent panels in a 2x3 grid
                    with Horizontal():
                        with Vertical():
                            yield AgentStatus("cto", "Sarah Chen", "CTO", id="agent-cto")
                            yield AgentStatus("backend", "Marcus Chen", "Backend Engineer", id="agent-backend")
                        with Vertical():
                            yield AgentStatus("frontend", "Emily Rodriguez", "Frontend Engineer", id="agent-frontend")
                            yield AgentStatus("qa", "Alex Thompson", "QA Engineer", id="agent-qa")
                        with Vertical():
                            yield AgentStatus("devops", "Jordan Kim", "DevOps Engineer", id="agent-devops")
                            # Metrics panel
                            with Container(id="metrics-panel"):
                                yield Label("📊 Project Metrics", classes="agent-header")
                                yield Label("Lines Written: 0", id="metric-lines")
                                yield Label("Tests Passed: 0", id="metric-tests")
                                yield Label("Bugs Found: 0", id="metric-bugs")
                                yield Label("Deployments: 0", id="metric-deploys")
                    
                    # Team chat
                    with Container(id="team-chat"):
                        yield Label("💬 Team Chat", classes="agent-header")
                        yield Log(id="chat-log", highlight=True, max_lines=100)
            
            # Tab 2: Full Log
            with TabPane("Full Log", id="log-tab"):
                yield Log(id="full-log", highlight=True, wrap=True)
                
            # Tab 3: Performance
            with TabPane("Performance", id="performance-tab"):
                yield DataTable(id="performance-table")
                
        yield Footer()
        
    def on_mount(self):
        """Initialize the dashboard"""
        # Store references to agent panels
        self.agent_panels = {
            "cto": self.query_one("#agent-cto", AgentStatus),
            "backend": self.query_one("#agent-backend", AgentStatus),
            "frontend": self.query_one("#agent-frontend", AgentStatus),
            "qa": self.query_one("#agent-qa", AgentStatus),
            "devops": self.query_one("#agent-devops", AgentStatus),
        }
        
        # Initialize performance table
        table = self.query_one("#performance-table", DataTable)
        table.add_columns("Agent", "Tasks", "Time (s)", "Cost ($)", "Tokens", "Status")
        
        # Start background orchestration
        self.run_worker(self.orchestrate_demo())
        
    async def orchestrate_demo(self):
        """Run a demo project with v3.1 agents"""
        self.start_time = time.time()
        
        # Log start
        self.log_event("system", "🎬 Starting project: Real-time Chat Application")
        
        # Phase 1: Initialize
        await self.init_agents()
        
        # Phase 2: Architecture (simulated since no CTO agent yet)
        await self.simulate_cto_phase()
        
        # Phase 3: Backend Development
        await self.run_backend_phase()
        
        # Phase 4: Frontend Development  
        await self.run_frontend_phase()
        
        # Phase 5: QA Testing
        await self.run_qa_phase()
        
        # Phase 6: DevOps Deployment
        await self.run_devops_phase()
        
        # Complete
        total_time = time.time() - self.start_time
        self.log_event("system", f"🎉 Project complete! Total time: {total_time:.1f}s")
        
    async def init_agents(self):
        """Initialize v3.1 agents"""
        self.log_event("system", "Initializing AI Development Team...")
        
        for agent_id, panel in self.agent_panels.items():
            panel.update_status("initializing", "Setting up...")
            panel.add_activity("Agent initializing...", "info")
            await asyncio.sleep(0.5)
            panel.update_status("ready", "Waiting for tasks", 100)
            panel.add_activity("Agent ready!", "success")
            
    async def simulate_cto_phase(self):
        """Simulate CTO phase (since CTO agent not implemented in v3.1)"""
        panel = self.agent_panels["cto"]
        panel.update_status("working", "Analyzing requirements", 0)
        panel.add_activity("Starting architecture phase", "working")
        
        tasks = [
            ("Analyzing project requirements", 30),
            ("Creating technical specification", 60),
            ("Finalizing architecture", 100)
        ]
        
        for task, progress in tasks:
            panel.update_status("working", task, progress)
            panel.add_activity(task, "working")
            await asyncio.sleep(1.5)
            
        panel.update_status("complete", "Architecture ready", 100)
        panel.add_activity("Architecture complete!", "success")
        self.update_performance("cto", 1, 4.5, 0.0, 0, "success")
        
    async def run_backend_phase(self):
        """Run backend development with real v3.1 agent"""
        panel = self.agent_panels["backend"]
        panel.update_status("working", "Starting backend development", 0)
        
        # Create real backend agent
        marcus = BackendAgent()
        panel.add_activity(f"Marcus ready: {marcus.personality.name}", "success")
        
        # Simulate backend tasks
        tasks = [
            ("Setting up FastAPI project", 20),
            ("Creating WebSocket handlers", 50),
            ("Implementing authentication", 80),
            ("Finalizing backend API", 100)
        ]
        
        for task, progress in tasks:
            panel.update_status("working", task, progress)
            panel.add_activity(task, "working")
            self.log_team_chat("backend", f"Working on: {task}")
            await asyncio.sleep(1.2)
            
        panel.update_status("complete", "Backend complete", 100)
        panel.add_activity("Generated 278 lines of code", "success")
        self.update_metrics(lines_written=278)
        self.update_performance("backend", 1, 4.8, 0.0, 0, "success")
        
    async def run_frontend_phase(self):
        """Run frontend development with real v3.1 agent"""
        panel = self.agent_panels["frontend"]
        panel.update_status("working", "Starting frontend development", 0)
        
        # Create real frontend agent
        emily = FrontendAgent()
        panel.add_activity(f"Emily ready: {emily.personality.name}", "success")
        
        # Simulate frontend tasks
        tasks = [
            ("Creating React components", 25),
            ("Building chat interface", 50),
            ("Implementing real-time updates", 75),
            ("Polishing UI/UX", 100)
        ]
        
        for task, progress in tasks:
            panel.update_status("working", task, progress)
            panel.add_activity(task, "working")
            self.log_team_chat("frontend", f"Designing: {task}")
            await asyncio.sleep(1.0)
            
        panel.update_status("complete", "Frontend complete", 100)
        panel.add_activity("Generated 283 lines of React code", "success")
        self.update_metrics(lines_written=561)  # Total
        self.update_performance("frontend", 1, 4.0, 0.0, 0, "success")
        
    async def run_qa_phase(self):
        """Run QA testing with real v3.1 agent"""
        panel = self.agent_panels["qa"]
        panel.update_status("working", "Starting quality assurance", 0)
        
        # Create real QA agent
        alex = QAAgent()
        panel.add_activity(f"Alex ready: {alex.name}", "success")
        
        # Simulate QA tasks
        tasks = [
            ("Writing unit tests", 33),
            ("Creating integration tests", 66),
            ("Running full test suite", 100)
        ]
        
        for task, progress in tasks:
            panel.update_status("working", task, progress)
            panel.add_activity(task, "working")
            self.log_team_chat("qa", f"Testing: {task}")
            await asyncio.sleep(1.0)
            
        panel.update_status("complete", "All tests passing", 100)
        panel.add_activity("289 tests passed, 0 failed", "success")
        self.update_metrics(tests_passed=289)
        self.update_performance("qa", 1, 3.0, 0.0, 0, "success")
        
    async def run_devops_phase(self):
        """Run DevOps deployment with real v3.1 agent"""
        panel = self.agent_panels["devops"]
        panel.update_status("working", "Starting deployment", 0)
        
        # Create real DevOps agent
        jordan = DevOpsAgent()
        panel.add_activity(f"Jordan ready: {jordan.personality.name}", "success")
        
        # Simulate DevOps tasks
        tasks = [
            ("Creating Docker containers", 25),
            ("Setting up CI/CD pipeline", 50),
            ("Configuring cloud infrastructure", 75),
            ("Deploying to production", 100)
        ]
        
        for task, progress in tasks:
            panel.update_status("working", task, progress)
            panel.add_activity(task, "working")
            self.log_team_chat("devops", f"Deploying: {task}")
            await asyncio.sleep(1.2)
            
        panel.update_status("complete", "Deployed successfully", 100)
        panel.add_activity("Application live in production!", "success")
        self.update_metrics(deployments=1)
        self.update_performance("devops", 1, 4.8, 0.0, 0, "success")
        
    def log_event(self, agent: str, message: str):
        """Log event to full log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{agent.upper()}] {message}"
        self.full_log.append(log_entry)
        
        full_log_widget = self.query_one("#full-log", Log)
        full_log_widget.write_line(log_entry)
        
    def log_team_chat(self, agent: str, message: str):
        """Log team chat message"""
        chat_log = self.query_one("#chat-log", Log)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        agent_colors = {
            "backend": "green",
            "frontend": "magenta", 
            "qa": "yellow",
            "devops": "red",
            "cto": "blue"
        }
        
        color = agent_colors.get(agent, "white")
        chat_log.write_line(f"[{color}]{timestamp} [{agent.upper()}][/{color}] {message}")
        
    def update_metrics(self, **kwargs):
        """Update project metrics"""
        for key, value in kwargs.items():
            if key in self.metrics:
                self.metrics[key] = value
                
        # Update UI
        self.query_one("#metric-lines", Label).update(f"Lines Written: {self.metrics['lines_written']}")
        self.query_one("#metric-tests", Label).update(f"Tests Passed: {self.metrics['tests_passed']}")
        self.query_one("#metric-bugs", Label).update(f"Bugs Found: {self.metrics['bugs_found']}")
        self.query_one("#metric-deploys", Label).update(f"Deployments: {self.metrics['deployments']}")
        
    def update_performance(self, agent: str, tasks: int, time_s: float, cost: float, tokens: int, status: str):
        """Update performance table"""
        table = self.query_one("#performance-table", DataTable)
        
        # Agent name mapping
        names = {
            "cto": "Sarah Chen",
            "backend": "Marcus Chen",
            "frontend": "Emily R.",
            "qa": "Alex T.",
            "devops": "Jordan Kim"
        }
        
        table.add_row(names.get(agent, agent), str(tasks), f"{time_s:.1f}", f"${cost:.4f}", str(tokens), status)


def main():
    """Launch the native v3.1 theatrical dashboard"""
    print("🎭 Launching AIOSv3.1 Native Theatrical Dashboard")
    print("This is built specifically for v3.1's architecture")
    print("-" * 50)
    
    app = TheatricalDashboardV31()
    app.run()


if __name__ == "__main__":
    main()