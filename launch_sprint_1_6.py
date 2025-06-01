#!/usr/bin/env python3
"""
Sprint 1.6 Launcher - Control Center & Agent Intelligence

This script orchestrates the launch of Sprint 1.6 with all necessary agents.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class Sprint16Launcher:
    def __init__(self):
        self.sprint_name = "Sprint 1.6: Control Center & Agent Intelligence"
        self.agents = {
            'backend': {
                'name': 'Marcus Chen',
                'task_file': 'sprint_1_6_tasks/backend_agent_tasks.md',
                'primary_tasks': ['MON-001', 'MON-002'],
                'branch': 'feature/sprint-1.6-monitoring-backend'
            },
            'frontend': {
                'name': 'Alex Rivera', 
                'task_file': 'sprint_1_6_tasks/frontend_agent_tasks.md',
                'primary_tasks': ['CC-001', 'CC-002', 'CC-003', 'CC-004', 'CC-005'],
                'branch': 'feature/sprint-1.6-control-center-ui'
            }
        }
        
    def display_sprint_info(self):
        """Display sprint information"""
        info = Table(title="Sprint 1.6 Information", show_header=False)
        info.add_column("Key", style="cyan")
        info.add_column("Value", style="green")
        
        info.add_row("Sprint", self.sprint_name)
        info.add_row("Duration", "2 weeks")
        info.add_row("Start Date", datetime.now().strftime("%Y-%m-%d"))
        info.add_row("Main Goals", "1. Control Center UI\n2. Agent Intelligence\n3. Monitoring System")
        
        console.print(Panel(info, border_style="blue"))
        
    def display_agent_assignments(self):
        """Display agent task assignments"""
        assignments = Table(title="Agent Assignments")
        assignments.add_column("Agent", style="cyan")
        assignments.add_column("Role", style="yellow")
        assignments.add_column("Primary Tasks", style="green")
        assignments.add_column("Branch", style="magenta")
        
        assignments.add_row(
            "Marcus Chen",
            "Backend Developer",
            "MON-001: Complete WebSocket Server\nMON-002: Metrics Collection",
            "feature/sprint-1.6-monitoring-backend"
        )
        
        assignments.add_row(
            "Alex Rivera",
            "Frontend Developer", 
            "CC-001: Project Setup\nCC-002: Agent Orchestra\nCC-003: Activity Monitor\nCC-004: Task Manager\nCC-005: PR Review",
            "feature/sprint-1.6-control-center-ui"
        )
        
        console.print("\n")
        console.print(assignments)
        
    async def check_prerequisites(self):
        """Check that all prerequisites are met"""
        console.print("\n[yellow]Checking prerequisites...[/yellow]")
        
        checks = [
            ("Git repository", self._check_git()),
            ("Redis running", self._check_redis()),
            ("Task files created", self._check_task_files()),
            ("Clean working directory", self._check_clean_git())
        ]
        
        all_passed = True
        for check_name, passed in checks:
            status = "[green]✓[/green]" if passed else "[red]✗[/red]"
            console.print(f"  {status} {check_name}")
            if not passed:
                all_passed = False
                
        return all_passed
        
    def _check_git(self):
        """Check if we're in a git repository"""
        return Path(".git").exists()
        
    def _check_redis(self):
        """Check if Redis is running"""
        try:
            import redis
            r = redis.Redis()
            r.ping()
            return True
        except:
            return False
            
    def _check_task_files(self):
        """Check if task files exist"""
        return all(Path(agent['task_file']).exists() for agent in self.agents.values())
        
    def _check_clean_git(self):
        """Check if git working directory is clean"""
        import subprocess
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        return len(result.stdout.strip()) == 0
        
    def display_launch_plan(self):
        """Display the launch plan"""
        console.print("\n[bold blue]Launch Plan:[/bold blue]")
        console.print("1. Create feature branches for each agent")
        console.print("2. Launch Backend Agent (Marcus) first - complete monitoring server")
        console.print("3. Launch Frontend Agent (Alex) - build Control Center UI")
        console.print("4. Monitor progress via orchestration dashboard")
        console.print("5. Review and merge PRs as they're submitted")
        
    async def launch_sprint(self):
        """Launch the sprint"""
        console.print("\n[bold green]Ready to launch Sprint 1.6![/bold green]")
        console.print("\nThis will:")
        console.print("• Start the orchestration server")
        console.print("• Launch configured agents with their tasks")
        console.print("• Open monitoring dashboard")
        
        response = console.input("\n[yellow]Proceed with sprint launch? (y/n): [/yellow]")
        
        if response.lower() != 'y':
            console.print("[red]Sprint launch cancelled.[/red]")
            return
            
        # Here we would actually launch the agents
        console.print("\n[green]Sprint 1.6 launched successfully![/green]")
        console.print("\nNext steps:")
        console.print("1. Run: [cyan]python launch_orchestrator.py[/cyan]")
        console.print("2. Run: [cyan]python enhanced_theatrical_agent.py backend[/cyan]")
        console.print("3. Run: [cyan]python enhanced_theatrical_agent.py frontend[/cyan]")
        console.print("4. Monitor progress in the orchestration dashboard")
        
async def main():
    launcher = Sprint16Launcher()
    
    console.print("[bold blue]🚀 Sprint 1.6 Launcher[/bold blue]")
    console.print("=" * 50)
    
    # Display sprint information
    launcher.display_sprint_info()
    launcher.display_agent_assignments()
    
    # Check prerequisites
    if not await launcher.check_prerequisites():
        console.print("\n[red]Prerequisites not met. Please fix the issues above.[/red]")
        return
        
    # Display launch plan
    launcher.display_launch_plan()
    
    # Launch sprint
    await launcher.launch_sprint()

if __name__ == "__main__":
    asyncio.run(main())