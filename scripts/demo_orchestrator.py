#!/usr/bin/env python3
"""
Demo Orchestrator Script - Interactive AI Development Team Demo

This script provides a cohesive demonstration of:
1. CTO consultation phase with interactive prompts
2. Theatrical dashboard with real agent integration
3. Task management API demo showing coordination
4. Progress tracking and team collaboration
5. Final summary with comprehensive metrics

Run with: python scripts/demo_orchestrator.py
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.agents.specialists.cto_agent import CTOAgent, create_cto_agent
from src.agents.specialists.backend_agent import BackendAgent, create_marcus_agent
from src.agents.specialists.frontend_agent import FrontendAgent, create_emily_agent
from src.agents.specialists.qa_agent import QAAgent
from src.agents.specialists.devops_agent import JordanDevOpsAgent
from src.agents.base.types import TaskType
from src.agents.base.enhanced_agent import EnhancedTask
from src.visualization.theatrical_dashboard import TheatricalDashboard
from src.orchestration.task_orchestrator import TaskOrchestrator, Task, TaskStatus, TaskPriority

console = Console()


class DemoOrchestrator:
    """Interactive demo orchestrator for AI development team"""
    
    def __init__(self):
        self.console = console
        self.agents = {}
        self.project_info = {}
        self.task_results = []
        self.metrics = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "total_cost": 0.0,
            "total_tokens": 0,
            "start_time": None,
            "end_time": None
        }
        
    async def run(self):
        """Run the complete demo flow"""
        try:
            # Welcome screen
            self._show_welcome()
            
            # Phase 1: CTO Consultation
            await self._cto_consultation_phase()
            
            # Phase 2: Initialize Agents
            await self._initialize_agents()
            
            # Phase 3: Run Theatrical Dashboard Demo
            if Confirm.ask("\n[bold cyan]Launch theatrical dashboard?[/]", default=True):
                await self._run_theatrical_demo()
            
            # Phase 4: Task Management Demo
            if Confirm.ask("\n[bold cyan]Run task management demo?[/]", default=True):
                await self._run_task_management_demo()
            
            # Phase 5: Final Summary
            self._show_final_summary()
            
        except KeyboardInterrupt:
            self.console.print("\n[bold red]Demo interrupted by user[/]")
        except Exception as e:
            self.console.print(f"\n[bold red]Error during demo: {e}[/]")
        finally:
            # Cleanup
            await self._cleanup()
    
    def _show_welcome(self):
        """Display welcome screen"""
        welcome_text = Text()
        welcome_text.append("🎭 AIOSv3.1 - AI Development Team Demo\n\n", style="bold magenta")
        welcome_text.append("This interactive demo showcases:\n", style="yellow")
        welcome_text.append("• CTO consultation for project planning\n", style="white")
        welcome_text.append("• Real-time agent collaboration\n", style="white")
        welcome_text.append("• Task orchestration and management\n", style="white")
        welcome_text.append("• Progress tracking and metrics\n", style="white")
        welcome_text.append("• Theatrical visualization dashboard\n", style="white")
        
        panel = Panel(welcome_text, title="Welcome", border_style="magenta")
        self.console.print(panel)
    
    async def _cto_consultation_phase(self):
        """Interactive CTO consultation phase"""
        self.console.print("\n[bold cyan]Phase 1: CTO Consultation[/]")
        self.console.print("Let's plan your project with our AI CTO...\n")
        
        # Get project details
        project_name = Prompt.ask("[bold]Project name", default="Task Management API")
        project_desc = Prompt.ask("[bold]Project description", 
                                   default="RESTful API with authentication, real-time updates, and analytics")
        
        # Project complexity
        complexity_choices = {
            "1": "Simple (1-2 days)",
            "2": "Medium (3-5 days)", 
            "3": "Complex (1-2 weeks)"
        }
        self.console.print("\n[bold]Project complexity:[/]")
        for key, value in complexity_choices.items():
            self.console.print(f"  {key}. {value}")
        complexity = Prompt.ask("Choose complexity", choices=["1", "2", "3"], default="2")
        
        # Technology preferences
        tech_stack = Prompt.ask("\n[bold]Preferred tech stack", 
                                 default="FastAPI, PostgreSQL, Redis, Docker")
        
        self.project_info = {
            "name": project_name,
            "description": project_desc,
            "complexity": complexity_choices[complexity],
            "tech_stack": tech_stack,
            "requested_at": datetime.now().isoformat()
        }
        
        # CTO Analysis
        self.console.print("\n[bold magenta]🏛️ Consulting with CTO Sarah Chen...[/]")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Analyzing project requirements...", total=None)
            
            # Create CTO agent
            cto = await create_cto_agent()
            
            # Get CTO analysis
            cto_task = EnhancedTask(
                task_type=TaskType.SYSTEM_DESIGN,
                prompt=f"""Analyze this project request and provide:
1. Technical architecture recommendation
2. Team resource allocation (which agents needed)
3. Major milestones and phases
4. Risk assessment
5. Estimated timeline

Project: {project_name}
Description: {project_desc}
Complexity: {complexity_choices[complexity]}
Tech Stack: {tech_stack}""",
                complexity=8,
                metadata=self.project_info
            )
            
            result = await cto.process_task(cto_task)
            progress.update(task, completed=True)
        
        if result.success:
            self.console.print("\n[bold green]✅ CTO Analysis Complete[/]\n")
            self.console.print(Panel(result.output, title="CTO Recommendations", border_style="cyan"))
            self.metrics["total_cost"] += result.cost
            self.metrics["total_tokens"] += result.tokens
        
        # Store CTO recommendations
        self.project_info["cto_analysis"] = result.output if result.success else "Analysis failed"
        
        await cto.stop()
    
    async def _initialize_agents(self):
        """Initialize all specialist agents"""
        self.console.print("\n[bold cyan]Phase 2: Initializing AI Development Team[/]")
        
        agents_to_create = [
            ("backend", "Marcus Chen", create_marcus_agent),
            ("frontend", "Emily Rodriguez", create_emily_agent),
            ("qa", "Alex Thompson", lambda: QAAgent()),
            ("devops", "Jordan Kim", lambda: JordanDevOpsAgent())
        ]
        
        # Convert sync constructors to async
        async def create_qa(): return QAAgent()
        async def create_devops(): return JordanDevOpsAgent()
        
        agents_to_create = [
            ("backend", "Marcus Chen", create_marcus_agent),
            ("frontend", "Emily Rodriguez", create_emily_agent),
            ("qa", "Alex Thompson", create_qa),
            ("devops", "Jordan Kim", create_devops)
        ]
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            for agent_type, name, create_func in agents_to_create:
                task = progress.add_task(f"Initializing {name}...", total=None)
                agent = await create_func()
                self.agents[agent_type] = agent
                progress.update(task, completed=True)
        
        self.console.print("[bold green]✅ All agents initialized and ready![/]")
    
    async def _run_theatrical_demo(self):
        """Run the theatrical dashboard demo"""
        self.console.print("\n[bold cyan]Phase 3: Theatrical Dashboard Demo[/]")
        self.console.print("Launching real-time visualization of agent collaboration...\n")
        
        # Create and run theatrical dashboard
        dashboard = TheatricalDashboard()
        
        # Override the demo project with our custom project
        dashboard.run_demo_project = self._create_custom_demo(dashboard)
        
        # Run dashboard in background
        dashboard_task = asyncio.create_task(dashboard.run())
        
        # Let it run for a bit
        await asyncio.sleep(30)
        
        # Cancel dashboard
        dashboard_task.cancel()
        try:
            await dashboard_task
        except asyncio.CancelledError:
            pass
        
        self.console.print("\n[bold green]✅ Theatrical demo completed![/]")
    
    def _create_custom_demo(self, dashboard):
        """Create custom demo based on user's project"""
        async def custom_demo():
            dashboard.start_time = time.time()
            dashboard.project_info = self.project_info
            
            await dashboard.orchestrator.start_project(
                self.project_info["name"],
                self.project_info["description"]
            )
            
            # Run phases based on project
            phases = [
                ("Architecture & Planning", "cto-001", [
                    "Analyze requirements",
                    "Design system architecture",
                    "Create technical specifications"
                ]),
                ("Backend Development", "backend-001", [
                    "Set up project structure",
                    "Implement API endpoints",
                    "Create database schema",
                    "Add authentication"
                ]),
                ("Frontend Development", "frontend-001", [
                    "Create UI components",
                    "Implement API integration",
                    "Add user authentication",
                    "Design responsive layout"
                ]),
                ("Quality Assurance", "qa-001", [
                    "Write unit tests",
                    "Create integration tests",
                    "Perform security audit",
                    "Test edge cases"
                ]),
                ("Deployment", "devops-001", [
                    "Create Docker containers",
                    "Set up CI/CD pipeline",
                    "Configure monitoring",
                    "Deploy to cloud"
                ])
            ]
            
            for phase_name, agent_id, tasks in phases:
                await dashboard.orchestrator.run_phase(
                    f"Phase: {phase_name}",
                    agent_id,
                    tasks
                )
            
            # Complete
            elapsed = time.time() - dashboard.start_time
            dashboard._event_callback({
                "type": "SUCCESS",
                "agent_id": "orchestrator",
                "message": f"🎉 Project Complete! Time: {elapsed:.1f}s",
                "timestamp": datetime.now()
            })
        
        return custom_demo
    
    async def _run_task_management_demo(self):
        """Demonstrate task orchestration and management"""
        self.console.print("\n[bold cyan]Phase 4: Task Management Demo[/]")
        self.console.print("Demonstrating intelligent task assignment and coordination...\n")
        
        # Create task orchestrator
        orchestrator = TaskOrchestrator()
        
        # Define demo tasks
        demo_tasks = [
            {
                "title": "Design API Schema",
                "type": TaskType.API_DESIGN,
                "agent": "backend",
                "priority": TaskPriority.HIGH,
                "effort": 2
            },
            {
                "title": "Implement User Authentication",
                "type": TaskType.IMPLEMENTATION,
                "agent": "backend",
                "priority": TaskPriority.HIGH,
                "effort": 4
            },
            {
                "title": "Create Dashboard UI",
                "type": TaskType.UI_DESIGN,
                "agent": "frontend",
                "priority": TaskPriority.MEDIUM,
                "effort": 3
            },
            {
                "title": "Write API Tests",
                "type": TaskType.TESTING,
                "agent": "qa",
                "priority": TaskPriority.MEDIUM,
                "effort": 2
            },
            {
                "title": "Setup CI/CD Pipeline",
                "type": TaskType.DEPLOYMENT,
                "agent": "devops",
                "priority": TaskPriority.LOW,
                "effort": 3
            }
        ]
        
        self.metrics["start_time"] = time.time()
        self.metrics["total_tasks"] = len(demo_tasks)
        
        # Process tasks
        with Progress() as progress:
            task_progress = progress.add_task("[cyan]Processing tasks...", total=len(demo_tasks))
            
            for task_def in demo_tasks:
                agent = self.agents.get(task_def["agent"])
                if not agent:
                    continue
                
                # Create task
                task = EnhancedTask(
                    task_type=task_def["type"],
                    prompt=f"{task_def['title']} for {self.project_info['name']}",
                    complexity=5,
                    metadata={"project": self.project_info["name"]}
                )
                
                # Process task
                self.console.print(f"\n[bold]{agent.agent_name}[/] working on: {task_def['title']}")
                result = await agent.process_task(task)
                
                if result.success:
                    self.metrics["completed_tasks"] += 1
                    self.metrics["total_cost"] += result.cost
                    self.metrics["total_tokens"] += result.tokens
                    self.task_results.append({
                        "task": task_def["title"],
                        "agent": agent.agent_name,
                        "success": True,
                        "cost": result.cost,
                        "time": result.execution_time
                    })
                    self.console.print(f"[green]✅ Completed in {result.execution_time:.1f}s[/]")
                else:
                    self.console.print(f"[red]❌ Failed: {result.error}[/]")
                
                progress.update(task_progress, advance=1)
        
        self.metrics["end_time"] = time.time()
        self.console.print("\n[bold green]✅ Task management demo completed![/]")
    
    def _show_final_summary(self):
        """Display final summary with metrics"""
        self.console.print("\n[bold cyan]Phase 5: Final Summary[/]")
        
        # Project Summary
        project_panel = Panel(
            f"""[bold]Project:[/] {self.project_info['name']}
[bold]Description:[/] {self.project_info['description']}
[bold]Complexity:[/] {self.project_info['complexity']}
[bold]Tech Stack:[/] {self.project_info['tech_stack']}""",
            title="Project Summary",
            border_style="cyan"
        )
        self.console.print(project_panel)
        
        # Task Results
        if self.task_results:
            task_table = Table(title="Task Results", show_header=True)
            task_table.add_column("Task", style="cyan")
            task_table.add_column("Agent", style="yellow")
            task_table.add_column("Status", style="green")
            task_table.add_column("Time", style="magenta")
            task_table.add_column("Cost", style="blue")
            
            for result in self.task_results:
                task_table.add_row(
                    result["task"],
                    result["agent"],
                    "✅ Success" if result["success"] else "❌ Failed",
                    f"{result['time']:.1f}s",
                    f"${result['cost']:.4f}"
                )
            
            self.console.print("\n")
            self.console.print(task_table)
        
        # Metrics Summary
        if self.metrics["start_time"] and self.metrics["end_time"]:
            duration = self.metrics["end_time"] - self.metrics["start_time"]
        else:
            duration = 0
        
        metrics_text = f"""
[bold]Total Tasks:[/] {self.metrics['total_tasks']}
[bold]Completed:[/] {self.metrics['completed_tasks']} ({self.metrics['completed_tasks']/max(self.metrics['total_tasks'], 1)*100:.0f}%)
[bold]Total Cost:[/] ${self.metrics['total_cost']:.4f}
[bold]Total Tokens:[/] {self.metrics['total_tokens']:,}
[bold]Duration:[/] {duration:.1f}s
[bold]Avg Cost/Task:[/] ${self.metrics['total_cost']/max(self.metrics['completed_tasks'], 1):.4f}
"""
        
        metrics_panel = Panel(
            metrics_text.strip(),
            title="Performance Metrics",
            border_style="green"
        )
        self.console.print("\n")
        self.console.print(metrics_panel)
        
        # Final message
        self.console.print("\n[bold magenta]🎉 Demo Complete![/]")
        self.console.print("Thank you for exploring the AIOSv3.1 AI Development Team!")
    
    async def _cleanup(self):
        """Clean up resources"""
        self.console.print("\n[dim]Cleaning up resources...[/]")
        
        # Stop all agents
        for agent in self.agents.values():
            try:
                await agent.stop()
            except:
                pass
        
        self.console.print("[dim]Cleanup complete.[/]")


async def main():
    """Main entry point"""
    demo = DemoOrchestrator()
    await demo.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold red]Demo interrupted by user[/]")
    except Exception as e:
        console.print(f"\n[bold red]Demo error: {e}[/]")