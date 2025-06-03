#!/usr/bin/env python3
"""
Simple Demo Orchestrator - Focused Theatrical Dashboard Demo

A streamlined version that demonstrates:
1. Quick project setup
2. Theatrical dashboard with real agents
3. Live task coordination
4. Summary metrics

Run with: python scripts/demo_orchestrator_simple.py
"""

import asyncio
import sys
import time
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.agents.specialists.backend_agent import BackendAgent
from src.agents.specialists.frontend_agent import FrontendAgent
from src.agents.specialists.qa_agent import QAAgent
from src.agents.specialists.devops_agent import JordanDevOpsAgent as DevOpsAgent
from src.agents.base.types import TaskType
from src.agents.base.enhanced_agent import EnhancedTask
from src.visualization.theatrical_adapter import TheatricalOrchestrator, TheatricalEvent, EventType

console = Console()


class SimpleTheatricalDemo:
    """Simplified theatrical demo with real agents"""
    
    def __init__(self):
        self.console = console
        self.orchestrator = None
        self.agents = {}
        self.start_time = None
        self.metrics = {
            "tasks_completed": 0,
            "total_cost": 0.0,
            "total_tokens": 0
        }
        
    async def run(self):
        """Run the theatrical demo"""
        try:
            # Welcome
            self._show_welcome()
            
            # Initialize
            await self._initialize()
            
            # Run demo
            await self._run_demo()
            
            # Show summary
            self._show_summary()
            
        except KeyboardInterrupt:
            self.console.print("\n[bold red]Demo interrupted[/]")
        finally:
            await self._cleanup()
    
    def _show_welcome(self):
        """Show welcome screen"""
        welcome = Text()
        welcome.append("🎭 AIOSv3.1 Theatrical Dashboard Demo\n\n", style="bold magenta")
        welcome.append("Watch our AI development team collaborate in real-time!\n", style="yellow")
        welcome.append("• Real LLM-powered agents\n", style="white")
        welcome.append("• Live task coordination\n", style="white")
        welcome.append("• Progress visualization\n", style="white")
        
        self.console.print(Panel(welcome, title="Welcome", border_style="magenta"))
    
    async def _initialize(self):
        """Initialize orchestrator and agents"""
        self.console.print("\n[bold cyan]Initializing AI Development Team...[/]")
        self.start_time = time.time()
        
        # Create orchestrator with event callback
        self.orchestrator = TheatricalOrchestrator(event_callback=self._event_handler)
        
        # Initialize real agents
        self.console.print("Creating specialist agents...")
        self.agents = {
            "backend-001": BackendAgent(agent_id="backend-001"),
            "frontend-001": FrontendAgent(agent_id="frontend-001"),
            "qa-001": QAAgent(agent_id="qa-001"),
            "devops-001": DevOpsAgent(agent_id="devops-001")
        }
        
        # Register agents with orchestrator
        for agent_id, agent in self.agents.items():
            self.orchestrator.agents[agent_id] = agent
        
        self.console.print("[bold green]✅ Team ready![/]")
    
    def _event_handler(self, event: TheatricalEvent):
        """Handle events from orchestrator"""
        # Update metrics
        if event.type == EventType.SUCCESS:
            self.metrics["tasks_completed"] += 1
            if event.cost:
                self.metrics["total_cost"] += event.cost
            if event.tokens:
                self.metrics["total_tokens"] += event.tokens
        
        # Display event
        agent_styles = {
            "backend-001": ("⚙️", "cyan"),
            "frontend-001": ("🎨", "yellow"),
            "qa-001": ("🧪", "green"),
            "devops-001": ("🚀", "blue"),
            "orchestrator": ("🎬", "magenta")
        }
        
        icon, color = agent_styles.get(event.agent_id, ("❓", "white"))
        timestamp = event.timestamp.strftime("%H:%M:%S")
        
        self.console.print(f"[dim]{timestamp}[/] {icon} [{color}]{event.message}[/]")
    
    async def _run_demo(self):
        """Run the demonstration"""
        self.console.print("\n[bold cyan]Starting Task Management API Project...[/]\n")
        
        # Project phases
        phases = [
            {
                "name": "Backend Development",
                "agent": "backend-001",
                "tasks": [
                    ("Design API Schema", TaskType.API_DESIGN, "Create RESTful API schema for task management"),
                    ("Implement Authentication", TaskType.IMPLEMENTATION, "Add JWT authentication system"),
                    ("Create Database Models", TaskType.DATABASE, "Design PostgreSQL schema with SQLAlchemy")
                ]
            },
            {
                "name": "Frontend Development",
                "agent": "frontend-001",
                "tasks": [
                    ("Design UI Components", TaskType.UI_DESIGN, "Create React component library"),
                    ("Build Dashboard", TaskType.IMPLEMENTATION, "Implement task management dashboard"),
                    ("Add Responsive Design", TaskType.UI_DESIGN, "Make UI mobile-friendly")
                ]
            },
            {
                "name": "Quality Assurance",
                "agent": "qa-001",
                "tasks": [
                    ("Write API Tests", TaskType.TESTING, "Create comprehensive API test suite"),
                    ("Test Authentication", TaskType.VALIDATION, "Validate security implementation"),
                    ("Performance Testing", TaskType.TESTING, "Load test API endpoints")
                ]
            },
            {
                "name": "Deployment",
                "agent": "devops-001",
                "tasks": [
                    ("Create Docker Setup", TaskType.DEPLOYMENT, "Containerize application"),
                    ("Setup CI/CD", TaskType.INFRASTRUCTURE, "Configure GitHub Actions"),
                    ("Deploy to Cloud", TaskType.DEPLOYMENT, "Deploy to AWS ECS")
                ]
            }
        ]
        
        # Execute phases
        for phase in phases:
            self.console.print(f"\n[bold magenta]Phase: {phase['name']}[/]")
            agent = self.agents[phase["agent"]]
            
            for task_name, task_type, description in phase["tasks"]:
                # Create task
                task = EnhancedTask(
                    task_type=task_type,
                    prompt=description,
                    complexity=5,
                    metadata={"task_name": task_name}
                )
                
                # Emit start event
                self._event_handler(TheatricalEvent(
                    type=EventType.WORK,
                    agent_id=phase["agent"],
                    message=f"Starting: {task_name}",
                    timestamp=datetime.now()
                ))
                
                # Process task
                result = await agent.process_task(task)
                
                # Emit completion event
                if result.success:
                    self._event_handler(TheatricalEvent(
                        type=EventType.SUCCESS,
                        agent_id=phase["agent"],
                        message=f"Completed: {task_name}",
                        timestamp=datetime.now(),
                        cost=result.cost,
                        tokens=result.tokens
                    ))
                else:
                    self._event_handler(TheatricalEvent(
                        type=EventType.ERROR,
                        agent_id=phase["agent"],
                        message=f"Failed: {task_name} - {result.error}",
                        timestamp=datetime.now()
                    ))
                
                # Small delay for visibility
                await asyncio.sleep(2)
        
        # Project complete
        elapsed = time.time() - self.start_time
        self._event_handler(TheatricalEvent(
            type=EventType.SUCCESS,
            agent_id="orchestrator",
            message=f"🎉 Project Complete! Total time: {elapsed:.1f}s",
            timestamp=datetime.now()
        ))
    
    def _show_summary(self):
        """Show final summary"""
        elapsed = time.time() - self.start_time
        
        # Create summary table
        table = Table(title="Demo Summary", show_header=False)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")
        
        table.add_row("Duration", f"{elapsed:.1f} seconds")
        table.add_row("Tasks Completed", str(self.metrics["tasks_completed"]))
        table.add_row("Total Cost", f"${self.metrics['total_cost']:.4f}")
        table.add_row("Total Tokens", f"{self.metrics['total_tokens']:,}")
        table.add_row("Avg Cost/Task", f"${self.metrics['total_cost']/max(self.metrics['tasks_completed'], 1):.4f}")
        
        self.console.print("\n")
        self.console.print(table)
        self.console.print("\n[bold magenta]🎉 Demo Complete![/]")
    
    async def _cleanup(self):
        """Clean up resources"""
        for agent in self.agents.values():
            try:
                await agent.stop()
            except:
                pass


async def main():
    """Main entry point"""
    demo = SimpleTheatricalDemo()
    await demo.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold red]Demo interrupted[/]")