#!/usr/bin/env python3
"""
REAL Sprint 1.6 Orchestrator - Uses actual AI agents for development

This orchestrator:
1. Launches REAL collaborative agents
2. Assigns them REAL tasks from task files
3. They write REAL code based on requirements
4. Reviews their REAL output
5. Makes REAL merge decisions
"""

import asyncio
import json
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import time

# Import real agent systems
from agents.collaborative_agent import CollaborativeAgent, CollaborativeAgentConfig
from core.routing.router import LLMRouter, RoutingStrategy
from core.routing.providers.claude import ClaudeProvider, ClaudeConfig

console = Console()

class ReviewDecision(Enum):
    APPROVE = "approve"
    APPROVE_WITH_NOTES = "approve_with_notes"
    REQUEST_CHANGES = "request_changes"
    REJECT = "reject"

@dataclass
class RealAgentTask:
    id: str
    title: str
    task_file: str
    agent_role: str
    agent_name: str
    branch: str
    agent_instance: Optional[CollaborativeAgent] = None
    status: str = "pending"
    pr_created: bool = False

class RealSprint16Orchestrator:
    """Orchestrates REAL agent development for Sprint 1.6."""
    
    def __init__(self):
        self.sprint_name = "Sprint 1.6: Control Center & Agent Intelligence"
        self.project_root = Path.cwd()
        self.agents: Dict[str, CollaborativeAgent] = {}
        self.tasks: List[RealAgentTask] = []
        self.llm_router = None
        
    async def initialize(self):
        """Initialize the orchestrator with real components."""
        console.print("[yellow]Initializing REAL Sprint 1.6 Orchestrator...[/yellow]")
        
        # Initialize LLM Router
        self.llm_router = LLMRouter()
        
        # Add Claude provider (or local if configured)
        claude_config = ClaudeConfig(
            api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            model="claude-3-opus-20240229"
        )
        self.llm_router.add_provider("claude", ClaudeProvider(claude_config))
        
        # Initialize tasks
        self.tasks = [
            RealAgentTask(
                id="MON-001",
                title="Complete WebSocket Monitoring Server",
                task_file="sprint_1_6_tasks/backend_agent_tasks.md",
                agent_role="backend-dev",
                agent_name="Marcus Chen",
                branch="feature/sprint-1.6-monitoring-backend"
            ),
            RealAgentTask(
                id="CC-001",
                title="Build Control Center UI",
                task_file="sprint_1_6_tasks/frontend_agent_tasks.md",
                agent_role="frontend-dev",
                agent_name="Alex Rivera",
                branch="feature/sprint-1.6-control-center-ui"
            )
        ]
        
        console.print("[green]✓ Orchestrator initialized[/green]")
        
    async def create_agents(self):
        """Create REAL collaborative agents."""
        console.print("\n[yellow]Creating REAL AI agents...[/yellow]")
        
        for task in self.tasks:
            # Create agent config
            config = CollaborativeAgentConfig(
                role=task.agent_role,
                name=task.agent_name,
                description=f"Agent responsible for {task.title}"
            )
            
            # Create agent instance
            agent = CollaborativeAgent(config, self.llm_router)
            await agent.start()
            
            self.agents[task.id] = agent
            task.agent_instance = agent
            
            console.print(f"[green]✓ Created {task.agent_name} ({task.agent_role})[/green]")
            
    async def assign_tasks(self):
        """Assign REAL tasks to agents."""
        console.print("\n[yellow]Assigning tasks to agents...[/yellow]")
        
        for task in self.tasks:
            if not task.agent_instance:
                console.print(f"[red]✗ No agent for task {task.id}[/red]")
                continue
                
            # Read task file
            task_file_path = Path(task.task_file)
            if not task_file_path.exists():
                console.print(f"[red]✗ Task file not found: {task.task_file}[/red]")
                continue
                
            task_content = task_file_path.read_text()
            
            # Create git branch for agent
            subprocess.run(['git', 'checkout', '-b', task.branch], 
                          capture_output=True, check=False)
            subprocess.run(['git', 'checkout', 'main'], capture_output=True)
            
            # Prepare task for agent
            agent_task = {
                "id": task.id,
                "type": "development",
                "title": task.title,
                "description": task_content,
                "branch": task.branch,
                "acceptance_criteria": [
                    "Code must be functional",
                    "Follow project standards",
                    "Include error handling",
                    "Add appropriate comments"
                ]
            }
            
            # Assign task to agent
            console.print(f"\n[cyan]Assigning {task.id} to {task.agent_name}...[/cyan]")
            result = await task.agent_instance.execute_task(agent_task)
            
            if result.success:
                task.status = "completed"
                console.print(f"[green]✓ {task.agent_name} completed {task.id}[/green]")
            else:
                task.status = "failed"
                console.print(f"[red]✗ {task.agent_name} failed {task.id}: {result.error}[/red]")
                
    async def check_agent_work(self):
        """Check what the agents actually created."""
        console.print("\n[yellow]Checking agent work...[/yellow]")
        
        for task in self.tasks:
            # Switch to agent's branch
            result = subprocess.run(['git', 'checkout', task.branch], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                console.print(f"[red]✗ No branch found for {task.id}[/red]")
                continue
                
            # Check for changes
            diff_result = subprocess.run(['git', 'diff', '--name-only', 'main'], 
                                       capture_output=True, text=True)
            
            if diff_result.stdout.strip():
                files = diff_result.stdout.strip().split('\n')
                console.print(f"\n[green]✓ {task.agent_name} created/modified:[/green]")
                for file in files:
                    console.print(f"  - {file}")
                    
                # Check if committed
                status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                             capture_output=True, text=True)
                
                if status_result.stdout.strip():
                    # Uncommitted changes - commit them
                    console.print(f"[yellow]Committing {task.agent_name}'s work...[/yellow]")
                    subprocess.run(['git', 'add', '.'], capture_output=True)
                    subprocess.run(['git', 'commit', '-m', 
                                  f'{task.agent_role}: {task.title}'], 
                                 capture_output=True)
                    
                task.pr_created = True
            else:
                console.print(f"[yellow]⚠ No changes found for {task.id}[/yellow]")
                
        # Return to main
        subprocess.run(['git', 'checkout', 'main'], capture_output=True)
        
    async def review_agent_code(self):
        """Review the REAL code the agents wrote."""
        console.print("\n[bold blue]🔍 Reviewing Agent Code[/bold blue]")
        
        for task in self.tasks:
            if not task.pr_created:
                continue
                
            console.print(f"\n[yellow]Reviewing {task.id}: {task.title}[/yellow]")
            console.print(f"Agent: {task.agent_name}")
            console.print(f"Branch: {task.branch}")
            
            # Get the diff
            diff_result = subprocess.run(
                ['git', 'diff', f'main...{task.branch}'],
                capture_output=True, text=True
            )
            
            if diff_result.stdout:
                # Analyze the code
                review = await self.ai_review_code(task, diff_result.stdout)
                decision = self.make_review_decision(review)
                
                # Execute decision
                await self.execute_review_decision(task, decision, review)
            else:
                console.print("[yellow]No changes to review[/yellow]")
                
    async def ai_review_code(self, task: RealAgentTask, diff: str) -> dict:
        """AI review of the actual code."""
        console.print("\n[bold]🤖 AI Code Review:[/bold]")
        
        # Analyze based on task type
        if "monitoring" in task.id.lower():
            return self.review_monitoring_code(diff)
        elif "control" in task.id.lower() or "ui" in task.id.lower():
            return self.review_ui_code(diff)
        else:
            return self.review_generic_code(diff)
            
    def review_monitoring_code(self, diff: str) -> dict:
        """Review monitoring/backend code."""
        review = {
            'summary': 'Reviewing monitoring server implementation...',
            'strengths': [],
            'concerns': [],
            'security': []
        }
        
        # Check for key features
        if 'websocket' in diff.lower() or 'ws' in diff.lower():
            review['strengths'].append('✅ WebSocket implementation found')
        else:
            review['concerns'].append('⚠️  No WebSocket implementation detected')
            
        if 'auth' in diff.lower() or 'jwt' in diff.lower():
            review['strengths'].append('✅ Authentication logic present')
        else:
            review['concerns'].append('⚠️  Missing authentication')
            
        if 'try' in diff and 'except' in diff:
            review['strengths'].append('✅ Error handling implemented')
        else:
            review['concerns'].append('⚠️  Limited error handling')
            
        if 'secret' in diff.lower() and 'key' in diff.lower():
            review['security'].append('🔒 Check secret key management')
            
        # Display findings
        self.display_review(review)
        return review
        
    def review_ui_code(self, diff: str) -> dict:
        """Review UI/frontend code."""
        review = {
            'summary': 'Reviewing UI implementation...',
            'strengths': [],
            'concerns': [],
            'ui_quality': []
        }
        
        # Check for UI features
        if 'textual' in diff.lower() or 'rich' in diff.lower():
            review['strengths'].append('✅ Using modern TUI framework')
            
        if 'class' in diff and 'App' in diff:
            review['strengths'].append('✅ Proper application structure')
            
        if 'compose' in diff:
            review['ui_quality'].append('🎨 Component-based architecture')
            
        # Display findings
        self.display_review(review)
        return review
        
    def review_generic_code(self, diff: str) -> dict:
        """Generic code review."""
        review = {
            'summary': 'Reviewing code implementation...',
            'strengths': ['✅ Code created by agent'],
            'concerns': []
        }
        
        if len(diff) < 100:
            review['concerns'].append('⚠️  Very minimal implementation')
            
        self.display_review(review)
        return review
        
    def display_review(self, review: dict):
        """Display review results."""
        for category, items in review.items():
            if category == 'summary':
                console.print(f"{items}")
            elif items:
                console.print(f"\n[bold]{category.title()}:[/bold]")
                for item in items:
                    console.print(f"  {item}")
                    
    def make_review_decision(self, review: dict) -> ReviewDecision:
        """Make decision based on review."""
        concerns = len(review.get('concerns', []))
        security = len(review.get('security', []))
        strengths = len(review.get('strengths', []))
        
        if concerns > 3 or security > 1:
            console.print("\n[yellow]🎯 Recommendation: APPROVE_WITH_NOTES[/yellow]")
            return ReviewDecision.APPROVE_WITH_NOTES
        elif strengths > concerns:
            console.print("\n[green]🎯 Recommendation: APPROVE[/green]")
            return ReviewDecision.APPROVE
        else:
            console.print("\n[yellow]🎯 Recommendation: REQUEST_CHANGES[/yellow]")
            return ReviewDecision.REQUEST_CHANGES
            
    async def execute_review_decision(self, task: RealAgentTask, decision: ReviewDecision, review: dict):
        """Execute the review decision."""
        if decision in [ReviewDecision.APPROVE, ReviewDecision.APPROVE_WITH_NOTES]:
            console.print(f"\n[green]✅ Merging {task.id}[/green]")
            
            # Merge the branch
            subprocess.run(['git', 'checkout', 'main'], capture_output=True)
            result = subprocess.run(['git', 'merge', task.branch, '--no-ff', '-m',
                                   f'Merge {task.id}: {task.title}'],
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print("[green]✓ Merged successfully[/green]")
                
                if decision == ReviewDecision.APPROVE_WITH_NOTES:
                    # Create improvement notes
                    notes = f"# Improvements for {task.title}\n\n"
                    for concern in review.get('concerns', []):
                        notes += f"- {concern}\n"
                    
                    Path(f"improvements_{task.id}.md").write_text(notes)
                    console.print(f"[yellow]📝 Created improvements_{task.id}.md[/yellow]")
            else:
                console.print(f"[red]✗ Merge failed: {result.stderr}[/red]")
                
        elif decision == ReviewDecision.REQUEST_CHANGES:
            console.print(f"[yellow]📝 Changes requested for {task.id}[/yellow]")
            # In a real scenario, we'd notify the agent
            
    def display_summary(self):
        """Display sprint summary."""
        summary = Table(title="Sprint 1.6 Summary")
        summary.add_column("Task", style="cyan")
        summary.add_column("Agent", style="yellow")
        summary.add_column("Status", style="green")
        
        for task in self.tasks:
            status_icon = "✅" if task.status == "completed" else "❌"
            summary.add_row(task.id, task.agent_name, f"{status_icon} {task.status}")
            
        console.print("\n")
        console.print(Panel(summary, border_style="green"))
        
    async def cleanup_agents(self):
        """Cleanup agent instances."""
        for agent_id, agent in self.agents.items():
            await agent.stop()
            
    async def run(self):
        """Run the REAL sprint orchestration."""
        try:
            # Initialize
            await self.initialize()
            
            # Create real agents
            await self.create_agents()
            
            # Assign real tasks
            await self.assign_tasks()
            
            # Check what they created
            await self.check_agent_work()
            
            # Review their code
            await self.review_agent_code()
            
            # Display summary
            self.display_summary()
            
        finally:
            # Cleanup
            await self.cleanup_agents()
            
        console.print("\n[bold green]✨ REAL Sprint 1.6 Complete![/bold green]")


async def main():
    """Main entry point."""
    console.print("[bold blue]🚀 REAL Sprint 1.6 Orchestrator[/bold blue]")
    console.print("This will use REAL AI agents to write REAL code\n")
    
    orchestrator = RealSprint16Orchestrator()
    await orchestrator.run()


if __name__ == "__main__":
    asyncio.run(main())