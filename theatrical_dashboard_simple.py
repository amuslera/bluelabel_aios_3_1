#!/usr/bin/env python3
"""
Simplified Theatrical Dashboard for v3.1
Follows v3.0's design but without complex agent dependencies
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List
import random

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
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


class AgentPanel(Static):
    """Agent status panel with activity log"""
    
    def __init__(self, agent_id: str, agent_name: str, agent_role: str, agent_icon: str, **kwargs):
        super().__init__(**kwargs)
        self._agent_id = agent_id
        self._agent_name = agent_name
        self._agent_role = agent_role
        self._agent_icon = agent_icon
        self.activities = []
        
    def compose(self) -> ComposeResult:
        with Vertical(classes="agent-box"):
            yield Label(f"{self._agent_icon} {self._agent_name}", classes="agent-name")
            yield Label(self._agent_role, classes="agent-role")
            yield Label("Status: Idle", id=f"status-{self._agent_id}")
            yield ProgressBar(total=100, id=f"progress-{self._agent_id}")
            yield Label("", id=f"task-{self._agent_id}", classes="current-task")
            with ScrollableContainer(classes="activity-log"):
                yield Log(id=f"log-{self._agent_id}", max_lines=10)


class V31TheatricalDashboard(App):
    """Theatrical Dashboard following v3.0's design"""
    
    CSS = """
    .agent-box {
        border: solid $primary;
        padding: 1;
        margin: 0 1;
        height: 100%;
    }
    
    .agent-name {
        text-style: bold;
        color: $primary;
    }
    
    .agent-role {
        color: $secondary;
        margin-bottom: 1;
    }
    
    .current-task {
        color: $warning;
        text-style: italic;
    }
    
    .activity-log {
        height: 8;
        border: dashed $surface-lighten-2;
        margin-top: 1;
    }
    
    #team-chat-container {
        border: solid $accent;
        padding: 1;
        height: 100%;
    }
    
    #metrics {
        border: solid $success;
        padding: 1;
    }
    
    .metric-value {
        color: $success;
        text-style: bold;
    }
    """
    
    TITLE = "🎭 AIOSv3.1 Theatrical Dashboard"
    
    def __init__(self):
        super().__init__()
        self.agents = {
            "cto": {"name": "Sarah Chen", "role": "CTO", "icon": "🏛️"},
            "backend": {"name": "Marcus Chen", "role": "Backend Engineer", "icon": "⚙️"},
            "frontend": {"name": "Emily Rodriguez", "role": "Frontend Engineer", "icon": "🎨"},
            "qa": {"name": "Alex Thompson", "role": "QA Engineer", "icon": "🧪"},
            "devops": {"name": "Jordan Kim", "role": "DevOps Engineer", "icon": "🚀"}
        }
        self.metrics = {
            "lines": 0,
            "tests": 0,
            "bugs": 0,
            "deploys": 0
        }
        self.start_time = None
        
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with TabbedContent():
            # Tab 1: Agents View
            with TabPane("Agents", id="agents-tab"):
                with Vertical():
                    # Top row: 3 agents
                    with Horizontal(classes="agent-row"):
                        yield AgentPanel("cto", self.agents["cto"]["name"], self.agents["cto"]["role"], self.agents["cto"]["icon"])
                        yield AgentPanel("backend", self.agents["backend"]["name"], self.agents["backend"]["role"], self.agents["backend"]["icon"])
                        yield AgentPanel("frontend", self.agents["frontend"]["name"], self.agents["frontend"]["role"], self.agents["frontend"]["icon"])
                    
                    # Bottom row: 2 agents + metrics
                    with Horizontal(classes="agent-row"):
                        yield AgentPanel("qa", self.agents["qa"]["name"], self.agents["qa"]["role"], self.agents["qa"]["icon"])
                        yield AgentPanel("devops", self.agents["devops"]["name"], self.agents["devops"]["role"], self.agents["devops"]["icon"])
                        
                        # Metrics panel
                        with Container(id="metrics"):
                            yield Label("📊 Project Metrics", classes="agent-name")
                            yield Label("Lines: 0", id="metric-lines", classes="metric-value")
                            yield Label("Tests: 0", id="metric-tests", classes="metric-value")
                            yield Label("Bugs: 0", id="metric-bugs", classes="metric-value")
                            yield Label("Deploys: 0", id="metric-deploys", classes="metric-value")
                    
                    # Team chat
                    with Container(id="team-chat-container"):
                        yield Label("💬 Team Chat", classes="agent-name")
                        yield Log(id="team-chat", max_lines=20)
            
            # Tab 2: Full Log
            with TabPane("Full Log", id="full-log-tab"):
                yield Log(id="full-log")
                
            # Tab 3: Performance
            with TabPane("Performance", id="performance-tab"):
                yield DataTable(id="performance-table")
                
        yield Footer()
        
    def on_mount(self):
        """Initialize dashboard"""
        # Set up performance table
        table = self.query_one("#performance-table", DataTable)
        table.add_columns("Agent", "Name", "Tasks", "Time (s)", "Cost ($)", "Tokens", "Avg/Task")
        
        # Start the demo
        self.run_worker(self.run_demo())
        
    async def run_demo(self):
        """Run the theatrical demo"""
        self.start_time = time.time()
        
        # Initialize agents
        await self.init_phase()
        
        # Run project phases
        await self.architecture_phase()
        await self.backend_phase()
        await self.frontend_phase()
        await self.qa_phase()
        await self.devops_phase()
        
        # Complete
        await self.complete_phase()
        
    async def init_phase(self):
        """Initialize all agents"""
        self.log_full("🎬 Initializing AI Development Team...")
        
        for agent_id in self.agents:
            self.update_agent_status(agent_id, "initializing", "Setting up...")
            await asyncio.sleep(0.3)
            self.update_agent_status(agent_id, "ready", "")
            self.log_agent_activity(agent_id, "Agent initialized and ready")
            
    async def architecture_phase(self):
        """CTO architecture phase"""
        agent_id = "cto"
        self.log_full("🏛️ Phase 1: Architecture & Planning")
        
        tasks = [
            "Analyzing project requirements",
            "Creating technical specification", 
            "Defining system architecture"
        ]
        
        for i, task in enumerate(tasks):
            progress = int((i + 1) / len(tasks) * 100)
            self.update_agent_status(agent_id, "working", task, progress)
            self.log_agent_activity(agent_id, task)
            self.log_team_chat(agent_id, f"Working on: {task}")
            await asyncio.sleep(1.5)
            
        self.update_agent_status(agent_id, "complete", "Architecture ready", 100)
        self.add_performance_row(agent_id, 1, 4.5, 0.0000, 0)
        
    async def backend_phase(self):
        """Backend development phase"""
        agent_id = "backend"
        self.log_full("⚙️ Phase 2: Backend Development")
        
        tasks = [
            "Setting up FastAPI project",
            "Implementing WebSocket handlers",
            "Creating authentication system",
            "Building database models"
        ]
        
        for i, task in enumerate(tasks):
            progress = int((i + 1) / len(tasks) * 100)
            self.update_agent_status(agent_id, "working", task, progress)
            self.log_agent_activity(agent_id, task)
            self.log_team_chat(agent_id, f"Implementing: {task}")
            await asyncio.sleep(1.2)
            
        lines = 278
        self.update_agent_status(agent_id, "complete", f"Generated {lines} lines", 100)
        self.log_agent_activity(agent_id, f"✅ Backend complete: {lines} lines of code")
        self.update_metrics(lines=lines)
        self.add_performance_row(agent_id, 1, 4.8, 0.0000, 0)
        
    async def frontend_phase(self):
        """Frontend development phase"""
        agent_id = "frontend"
        self.log_full("🎨 Phase 3: Frontend Development")
        
        tasks = [
            "Designing user interface",
            "Creating React components",
            "Building chat interface",
            "Implementing real-time updates"
        ]
        
        for i, task in enumerate(tasks):
            progress = int((i + 1) / len(tasks) * 100)
            self.update_agent_status(agent_id, "working", task, progress)
            self.log_agent_activity(agent_id, task)
            self.log_team_chat(agent_id, f"Building: {task}")
            await asyncio.sleep(1.0)
            
        lines = 283
        total_lines = self.metrics["lines"] + lines
        self.update_agent_status(agent_id, "complete", f"Generated {lines} lines", 100)
        self.log_agent_activity(agent_id, f"✅ Frontend complete: {lines} lines of React")
        self.update_metrics(lines=total_lines)
        self.add_performance_row(agent_id, 1, 4.0, 0.0000, 0)
        
    async def qa_phase(self):
        """QA testing phase"""
        agent_id = "qa"
        self.log_full("🧪 Phase 4: Quality Assurance")
        
        tasks = [
            "Analyzing code for bugs",
            "Writing unit tests",
            "Creating integration tests",
            "Running test suite"
        ]
        
        for i, task in enumerate(tasks):
            progress = int((i + 1) / len(tasks) * 100)
            self.update_agent_status(agent_id, "working", task, progress)
            self.log_agent_activity(agent_id, task)
            self.log_team_chat(agent_id, f"Testing: {task}")
            await asyncio.sleep(1.0)
            
        tests = 289
        self.update_agent_status(agent_id, "complete", f"{tests} tests passed", 100)
        self.log_agent_activity(agent_id, f"✅ All {tests} tests passing!")
        self.update_metrics(tests=tests)
        self.add_performance_row(agent_id, 1, 4.0, 0.0000, 0)
        
    async def devops_phase(self):
        """DevOps deployment phase"""
        agent_id = "devops"
        self.log_full("🚀 Phase 5: Deployment & Infrastructure")
        
        tasks = [
            "Creating Docker containers",
            "Setting up CI/CD pipeline",
            "Configuring cloud infrastructure",
            "Deploying to production"
        ]
        
        for i, task in enumerate(tasks):
            progress = int((i + 1) / len(tasks) * 100)
            self.update_agent_status(agent_id, "working", task, progress)
            self.log_agent_activity(agent_id, task)
            self.log_team_chat(agent_id, f"Deploying: {task}")
            await asyncio.sleep(1.2)
            
        self.update_agent_status(agent_id, "complete", "Deployed!", 100)
        self.log_agent_activity(agent_id, "✅ Application deployed to production!")
        self.update_metrics(deploys=1)
        self.add_performance_row(agent_id, 1, 4.8, 0.0000, 0)
        
    async def complete_phase(self):
        """Project completion"""
        total_time = time.time() - self.start_time
        self.log_full(f"🎉 Project Complete! Total time: {total_time:.1f}s")
        self.log_full(f"📊 Final Metrics: {self.metrics['lines']} lines, {self.metrics['tests']} tests, {self.metrics['deploys']} deploys")
        
        # Add totals row
        table = self.query_one("#performance-table", DataTable)
        table.add_row("📊 TOTAL", "All Agents", "5", f"{total_time:.1f}", "$0.0000", "0", "10.7s")
        
    def update_agent_status(self, agent_id: str, status: str, task: str = "", progress: int = 0):
        """Update agent panel status"""
        status_label = self.query_one(f"#status-{agent_id}", Label)
        task_label = self.query_one(f"#task-{agent_id}", Label)
        progress_bar = self.query_one(f"#progress-{agent_id}", ProgressBar)
        
        status_text = f"Status: {status.capitalize()}"
        if status == "working":
            status_label.update(f"[yellow]{status_text}[/yellow]")
        elif status == "complete":
            status_label.update(f"[green]{status_text}[/green]")
        else:
            status_label.update(status_text)
            
        task_label.update(task)
        progress_bar.progress = progress
        
    def log_agent_activity(self, agent_id: str, activity: str):
        """Log activity to agent panel"""
        log_widget = self.query_one(f"#log-{agent_id}", Log)
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_widget.write_line(f"{timestamp} {activity}")
        
    def log_team_chat(self, agent_id: str, message: str):
        """Log message to team chat"""
        chat = self.query_one("#team-chat", Log)
        timestamp = datetime.now().strftime("%H:%M:%S")
        agent = self.agents[agent_id]
        chat.write_line(f"{timestamp} [{agent['name']}] {message}")
        
    def log_full(self, message: str):
        """Log to full log tab"""
        full_log = self.query_one("#full-log", Log)
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_log.write_line(f"{timestamp} {message}")
        
    def update_metrics(self, **kwargs):
        """Update metrics panel"""
        for key, value in kwargs.items():
            if key in self.metrics:
                self.metrics[key] = value
                label = self.query_one(f"#metric-{key}", Label)
                label.update(f"{key.capitalize()}: {value}")
                
    def add_performance_row(self, agent_id: str, tasks: int, time_s: float, cost: float, tokens: int):
        """Add row to performance table"""
        table = self.query_one("#performance-table", DataTable)
        agent = self.agents[agent_id]
        avg_time = f"{time_s:.1f}s" if tasks > 0 else "0.0s"
        table.add_row(
            agent["icon"],
            agent["name"],
            str(tasks),
            f"{time_s:.1f}",
            f"${cost:.4f}",
            str(tokens),
            avg_time
        )


if __name__ == "__main__":
    print("🎭 AIOSv3.1 Theatrical Dashboard (Simplified)")
    print("=" * 50)
    print("This demonstrates v3.0's beautiful design in v3.1")
    print("Features:")
    print("  • 3-tab interface (Agents/Full Log/Performance)")
    print("  • Real-time agent activity")
    print("  • Team chat and metrics")
    print("=" * 50)
    
    app = V31TheatricalDashboard()
    app.run()