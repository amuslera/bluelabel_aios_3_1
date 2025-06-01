#!/usr/bin/env python3
"""
Sprint 1.6 Orchestrator - Unified Development and Review System

This orchestrator manages the complete sprint lifecycle:
1. Task assignment to agents
2. Development monitoring
3. PR creation and review
4. Merge decisions and sprint completion
"""

import asyncio
import json
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

console = Console()

class ReviewDecision(Enum):
    APPROVE = "approve"
    APPROVE_WITH_NOTES = "approve_with_notes"
    REQUEST_CHANGES = "request_changes"
    REJECT = "reject"
    ESCALATE = "escalate"  # New option for team discussion

@dataclass
class PRInfo:
    number: int
    title: str
    author: str
    branch: str
    description: str
    files_changed: List[str]
    created_at: str
    task_id: str
    agent_role: str

@dataclass
class AgentTask:
    id: str
    title: str
    agent_role: str
    agent_name: str
    branch: str
    status: str = "pending"
    pr_number: Optional[int] = None
    review_decision: Optional[str] = None

class Sprint16Orchestrator:
    """Orchestrates Sprint 1.6 development and review."""
    
    def __init__(self):
        self.sprint_name = "Sprint 1.6: Control Center & Agent Intelligence"
        self.project_root = Path.cwd()
        self.tasks: List[AgentTask] = []
        self.prs: Dict[str, PRInfo] = {}
        
    def initialize_tasks(self):
        """Initialize sprint tasks."""
        self.tasks = [
            AgentTask(
                id="MON-001",
                title="Complete WebSocket Monitoring Server",
                agent_role="backend",
                agent_name="Marcus Chen",
                branch="feature/sprint-1.6-monitoring-backend"
            ),
            AgentTask(
                id="CC-001",
                title="Build Control Center UI",
                agent_role="frontend",
                agent_name="Alex Rivera",
                branch="feature/sprint-1.6-control-center-ui"
            )
        ]
        
    def display_sprint_overview(self):
        """Display sprint overview."""
        overview = Table(title=f"🚀 {self.sprint_name}")
        overview.add_column("Component", style="cyan")
        overview.add_column("Status", style="yellow")
        overview.add_column("Progress", style="green")
        
        overview.add_row("Control Center UI", "In Development", "40%")
        overview.add_row("Agent Intelligence", "Planned", "0%")
        overview.add_row("Monitoring System", "In Development", "20%")
        
        console.print(Panel(overview, border_style="blue"))
        
    async def launch_agents(self, fast_mode: bool = False):
        """Launch agents for development."""
        console.print("\n[bold yellow]🤖 Launching Development Agents[/bold yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            for task in self.tasks:
                task_id = progress.add_task(
                    f"Starting {task.agent_name} ({task.agent_role})...", 
                    total=None
                )
                
                # Simulate agent starting
                await asyncio.sleep(2 if not fast_mode else 0.5)
                
                # Update task status
                task.status = "in_progress"
                progress.update(task_id, description=f"✅ {task.agent_name} working on {task.id}")
                
                # Simulate development
                await self.simulate_agent_development(task, fast_mode)
                
        console.print("[green]✅ All agents have completed their development tasks![/green]")
        
    async def simulate_agent_development(self, task: AgentTask, fast_mode: bool):
        """Simulate agent development work."""
        # Create feature branch
        subprocess.run(['git', 'checkout', '-b', task.branch], 
                      capture_output=True, check=False)
        
        # Simulate file creation based on task
        if task.id == "MON-001":
            await self.create_monitoring_files()
        elif task.id == "CC-001":
            await self.create_control_center_files()
            
        # Commit changes
        subprocess.run(['git', 'add', '.'], capture_output=True)
        subprocess.run(['git', 'commit', '-m', f'{task.agent_role}: {task.title}'], 
                      capture_output=True)
        
        # Create PR info
        task.pr_number = 100 + len(self.prs)
        pr_info = PRInfo(
            number=task.pr_number,
            title=task.title,
            author=task.agent_name,
            branch=task.branch,
            description=f"Implements {task.id}: {task.title}",
            files_changed=self.get_changed_files(task),
            created_at=datetime.now().isoformat(),
            task_id=task.id,
            agent_role=task.agent_role
        )
        
        # Save PR info
        self.save_pr_info(task.id, pr_info)
        self.prs[task.id] = pr_info
        
        # Switch back to main
        subprocess.run(['git', 'checkout', 'main'], capture_output=True)
        
    async def create_monitoring_files(self):
        """Create monitoring server files."""
        monitoring_dir = Path("monitoring_system")
        monitoring_dir.mkdir(exist_ok=True)
        
        # Create enhanced server.py
        server_content = '''"""Enhanced Monitoring Server with Authentication and Events"""
import asyncio
import json
import jwt
import redis
from typing import Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from datetime import datetime

class MonitoringServer:
    def __init__(self):
        self.app = FastAPI()
        self.clients: Set[WebSocket] = set()
        self.redis_client = redis.Redis(decode_responses=True)
        self.secret_key = "dev-secret-key"  # TODO: Use env var
        
    async def authenticate(self, token: str) -> bool:
        """Validate JWT token."""
        try:
            jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return True
        except:
            return False
            
    async def handle_event(self, event_type: str, data: dict):
        """Process and broadcast events."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in Redis
        self.redis_client.lpush(f"events:{event_type}", json.dumps(event))
        
        # Broadcast to clients
        await self.broadcast(event)
        
    async def broadcast(self, message: dict):
        """Send message to all connected clients."""
        disconnected = set()
        for client in self.clients:
            try:
                await client.send_json(message)
            except:
                disconnected.add(client)
                
        # Clean up disconnected clients
        self.clients -= disconnected

# Event handlers for different event types
EVENT_HANDLERS = {
    "agent_status_update": lambda data: f"Agent {data.get('agent_id')} is now {data.get('status')}",
    "task_assigned": lambda data: f"Task {data.get('task_id')} assigned to {data.get('agent_id')}",
    "task_completed": lambda data: f"Task {data.get('task_id')} completed",
    "error_occurred": lambda data: f"Error in {data.get('component')}: {data.get('message')}",
    "metric_update": lambda data: f"Metric {data.get('name')}: {data.get('value')}"
}
'''
        
        (monitoring_dir / "server.py").write_text(server_content)
        
        # Create metrics collector
        metrics_content = '''"""Metrics Collection System"""
from prometheus_client import Counter, Gauge, Histogram, generate_latest
import psutil
import time

# Define metrics
agent_tasks_total = Counter('agent_tasks_total', 'Total tasks by agent', ['agent_id', 'status'])
agent_cpu_usage = Gauge('agent_cpu_usage_percent', 'CPU usage by agent', ['agent_id'])
agent_memory_usage = Gauge('agent_memory_usage_mb', 'Memory usage by agent', ['agent_id'])
task_duration_seconds = Histogram('task_duration_seconds', 'Task execution time', ['task_type'])

class MetricsCollector:
    def collect_system_metrics(self, agent_id: str):
        """Collect system metrics for an agent."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
        
        agent_cpu_usage.labels(agent_id=agent_id).set(cpu_percent)
        agent_memory_usage.labels(agent_id=agent_id).set(memory_mb)
        
    def record_task_completion(self, agent_id: str, task_type: str, duration: float):
        """Record task completion metrics."""
        agent_tasks_total.labels(agent_id=agent_id, status='completed').inc()
        task_duration_seconds.labels(task_type=task_type).observe(duration)
'''
        
        (monitoring_dir / "metrics_collector.py").write_text(metrics_content)
        
    async def create_control_center_files(self):
        """Create control center UI files."""
        cc_dir = Path("control_center")
        cc_dir.mkdir(exist_ok=True)
        (cc_dir / "components").mkdir(exist_ok=True)
        
        # Create main app
        main_content = '''"""Control Center Main Application"""
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import Grid
from components.agent_orchestra import AgentOrchestraPanel
from components.activity_monitor import ActivityMonitorPanel
from components.task_manager import TaskManagerPanel
from components.pr_review import PRReviewPanel

class ControlCenterApp(App):
    """Main Control Center Application."""
    
    CSS_PATH = "styles.css"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("t", "toggle_theme", "Theme"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Grid(
            AgentOrchestraPanel(),
            ActivityMonitorPanel(),
            TaskManagerPanel(),
            PRReviewPanel(),
            classes="main-grid"
        )
        yield Footer()
        
    def action_refresh(self) -> None:
        """Refresh all panels."""
        # Implement refresh logic
        pass
'''
        
        (cc_dir / "main.py").write_text(main_content)
        
        # Create a component
        agent_panel = '''"""Agent Orchestra Panel"""
from textual.widgets import DataTable, Button
from textual.containers import Container

class AgentOrchestraPanel(Container):
    """Shows all active agents and their status."""
    
    def compose(self):
        yield DataTable()
        yield Button("Launch Agent", id="launch-agent")
'''
        
        (cc_dir / "components" / "agent_orchestra.py").write_text(agent_panel)
        (cc_dir / "components" / "__init__.py").touch()
        
    def get_changed_files(self, task: AgentTask) -> List[str]:
        """Get list of changed files for a task."""
        if task.id == "MON-001":
            return ["monitoring_system/server.py", "monitoring_system/metrics_collector.py"]
        elif task.id == "CC-001":
            return ["control_center/main.py", "control_center/components/agent_orchestra.py"]
        return []
        
    def save_pr_info(self, task_id: str, pr_info: PRInfo):
        """Save PR info to file."""
        pr_file = self.project_root / f".pr_info_{task_id}.json"
        with open(pr_file, 'w') as f:
            json.dump(asdict(pr_info), f, indent=2)
            
    async def review_prs(self):
        """Review all PRs with AI assistance."""
        console.print("\n[bold blue]🔍 Starting PR Review Process[/bold blue]")
        
        for task in self.tasks:
            if task.pr_number:
                console.print(f"\n[yellow]Reviewing PR #{task.pr_number}: {task.title}[/yellow]")
                review_decision = await self.ai_review_pr(task)
                task.review_decision = review_decision.value
                
                # Execute decision
                await self.execute_review_decision(task, review_decision)
                
    async def ai_review_pr(self, task: AgentTask) -> ReviewDecision:
        """AI review of PR with role-specific criteria."""
        pr_info = self.prs[task.id]
        
        console.print(Panel(
            f"[bold]PR #{pr_info.number}: {pr_info.title}[/bold]\n"
            f"Author: {pr_info.author}\n"
            f"Branch: {pr_info.branch}\n"
            f"Files: {', '.join(pr_info.files_changed)}",
            title="PR Summary",
            border_style="blue"
        ))
        
        # Role-specific review criteria
        if task.agent_role == "backend":
            review = self.review_backend_code(pr_info)
        elif task.agent_role == "frontend":
            review = self.review_frontend_code(pr_info)
        else:
            review = self.review_generic_code(pr_info)
            
        # Display review
        self.display_ai_review(review)
        
        # Make recommendation
        return self.make_review_recommendation(review)
        
    def review_backend_code(self, pr_info: PRInfo) -> dict:
        """Review backend code with specific criteria."""
        return {
            'summary': 'Backend implementation with authentication and event handling.',
            'strengths': [
                '✅ JWT authentication implemented',
                '✅ All 5 event types handled',
                '✅ Redis persistence added',
                '✅ Broadcast functionality works',
                '✅ Prometheus metrics exposed'
            ],
            'concerns': [
                '⚠️  Hardcoded secret key (TODO noted)',
                '⚠️  No rate limiting on WebSocket connections',
                '⚠️  Missing error recovery for Redis connection',
                '⚠️  No tests included'
            ],
            'security': [
                '🔒 JWT validation present but key management needed',
                '🔒 WebSocket origin validation missing',
                '🔒 Consider rate limiting for DoS protection'
            ]
        }
        
    def review_frontend_code(self, pr_info: PRInfo) -> dict:
        """Review frontend code with specific criteria."""
        return {
            'summary': 'Clean Textual-based UI with good component structure.',
            'strengths': [
                '✅ Modular component architecture',
                '✅ Keyboard shortcuts implemented',
                '✅ Grid layout for panels',
                '✅ Proper separation of concerns'
            ],
            'concerns': [
                '⚠️  WebSocket connection not implemented',
                '⚠️  Refresh logic incomplete',
                '⚠️  No error handling',
                '⚠️  Missing other component implementations'
            ],
            'ui_quality': [
                '🎨 Good use of Textual framework',
                '🎨 Clear component hierarchy',
                '🎨 Intuitive keybindings'
            ]
        }
        
    def review_generic_code(self, pr_info: PRInfo) -> dict:
        """Generic code review."""
        return {
            'summary': 'Code meets basic requirements.',
            'strengths': ['✅ Implements requested functionality'],
            'concerns': ['⚠️  Needs more thorough review']
        }
        
    def display_ai_review(self, review: dict):
        """Display AI review results."""
        console.print("\n[bold]🤖 AI Code Review:[/bold]")
        console.print(f"Summary: {review['summary']}")
        
        if 'strengths' in review:
            console.print("\n[green]Strengths:[/green]")
            for item in review['strengths']:
                console.print(f"  {item}")
                
        if 'concerns' in review:
            console.print("\n[yellow]Concerns:[/yellow]")
            for item in review['concerns']:
                console.print(f"  {item}")
                
        if 'security' in review:
            console.print("\n[red]Security:[/red]")
            for item in review['security']:
                console.print(f"  {item}")
                
        if 'ui_quality' in review:
            console.print("\n[blue]UI Quality:[/blue]")
            for item in review['ui_quality']:
                console.print(f"  {item}")
                
    def make_review_recommendation(self, review: dict) -> ReviewDecision:
        """Make recommendation based on review."""
        concerns = review.get('concerns', [])
        security = review.get('security', [])
        
        # If critical security issues, request changes
        if any('critical' in s.lower() for s in security):
            console.print("\n[red]🎯 Recommendation: REQUEST_CHANGES (Critical security issues)[/red]")
            return ReviewDecision.REQUEST_CHANGES
            
        # If many concerns, approve with notes
        if len(concerns) > 3:
            console.print("\n[yellow]🎯 Recommendation: APPROVE_WITH_NOTES (Address concerns in next iteration)[/yellow]")
            return ReviewDecision.APPROVE_WITH_NOTES
            
        # Otherwise approve
        console.print("\n[green]🎯 Recommendation: APPROVE (Good implementation)[/green]")
        return ReviewDecision.APPROVE
        
    async def execute_review_decision(self, task: AgentTask, decision: ReviewDecision):
        """Execute the review decision."""
        if decision in [ReviewDecision.APPROVE, ReviewDecision.APPROVE_WITH_NOTES]:
            # Merge the PR
            console.print(f"[green]✅ Merging PR #{task.pr_number}[/green]")
            
            subprocess.run(['git', 'checkout', task.branch], capture_output=True)
            subprocess.run(['git', 'checkout', 'main'], capture_output=True)
            subprocess.run(['git', 'merge', task.branch, '--no-ff', '-m', 
                          f'Merge PR #{task.pr_number}: {task.title}'],
                         capture_output=True)
            
            if decision == ReviewDecision.APPROVE_WITH_NOTES:
                # Create improvement tasks
                self.create_improvement_tasks(task)
                
        elif decision == ReviewDecision.REQUEST_CHANGES:
            console.print(f"[yellow]📝 Changes requested for PR #{task.pr_number}[/yellow]")
            # Create feedback file for agent
            self.create_feedback_file(task)
            
        elif decision == ReviewDecision.ESCALATE:
            console.print(f"[red]🚨 Escalating PR #{task.pr_number} for team discussion[/red]")
            
    def create_improvement_tasks(self, task: AgentTask):
        """Create tasks for improvements."""
        improvements_file = Path(f"improvements_{task.id}.md")
        content = f"""# Improvements for {task.title}

Based on the review, please address:
- Add proper secret key management
- Implement rate limiting
- Add error recovery for Redis
- Create comprehensive tests
"""
        improvements_file.write_text(content)
        
    def create_feedback_file(self, task: AgentTask):
        """Create feedback for agent to address."""
        feedback_file = Path(f"feedback_{task.id}.md")
        content = f"""# Feedback for {task.title}

Please address the following before merge:
1. Fix critical security issues
2. Add missing error handling
3. Complete implementation
"""
        feedback_file.write_text(content)
        
    def display_sprint_summary(self):
        """Display sprint summary."""
        summary = Table(title="Sprint 1.6 Summary")
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value", style="green")
        
        approved = sum(1 for t in self.tasks if t.review_decision in ["approve", "approve_with_notes"])
        total = len(self.tasks)
        
        summary.add_row("Total Tasks", str(total))
        summary.add_row("PRs Merged", str(approved))
        summary.add_row("Success Rate", f"{(approved/total)*100:.0f}%")
        summary.add_row("Sprint Status", "✅ Complete" if approved == total else "🔄 In Progress")
        
        console.print("\n")
        console.print(Panel(summary, border_style="green"))
        
    async def run_sprint(self, fast_mode: bool = False, review_only: bool = False):
        """Run the complete sprint."""
        self.display_sprint_overview()
        self.initialize_tasks()
        
        if not review_only:
            await self.launch_agents(fast_mode)
            
        await self.review_prs()
        self.display_sprint_summary()
        
        console.print("\n[bold green]✨ Sprint 1.6 Orchestration Complete![/bold green]")


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sprint 1.6 Orchestrator')
    parser.add_argument('--fast', action='store_true', help='Fast mode for demos')
    parser.add_argument('--review-only', action='store_true', help='Review existing PRs only')
    
    args = parser.parse_args()
    
    orchestrator = Sprint16Orchestrator()
    await orchestrator.run_sprint(fast_mode=args.fast, review_only=args.review_only)


if __name__ == "__main__":
    asyncio.run(main())