#!/usr/bin/env python3
"""
Interactive Demo - Hermes Multi-Agent Handoff System

This demo showcases the complete flow from natural conversation
to AI development team task assignment.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.layout import Layout
from rich.live import Live
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.specialists.hermes.hermes_with_llm import create_hermes_with_llm, PersonaConfig
from src.agents.specialists.hermes.persona_system import PersonaLibrary
from src.agents.specialists.hermes.brief_generator import BriefGenerator
from src.agents.specialists.hermes.task_decomposer import TaskDecomposer
from src.agents.specialists.hermes.handoff_connector import HermesHandoffBridge

console = Console()


class HandoffDemo:
    """Interactive demonstration of the handoff system."""
    
    def __init__(self):
        self.hermes = None
        self.state = None
        self.brief = None
        self.tasks = []
        
    async def initialize(self):
        """Initialize the demo."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Initializing Hermes with LLM support...", total=None)
            
            # Initialize Hermes
            persona = PersonaLibrary.get_business_persona()
            config = PersonaConfig(**persona.to_config())
            self.hermes = await create_hermes_with_llm(persona_config=config)
            
            progress.update(task, completed=True)
    
    def display_welcome(self):
        """Display welcome screen."""
        console.clear()
        
        welcome_text = """
# 🎭 Hermes Multi-Agent Handoff Demo

Welcome to the AI Software Development Platform!

This demo shows how natural conversations with Hermes are transformed into:
- 📄 Structured project briefs
- 📋 Decomposed development tasks
- 🤖 Intelligent agent assignments
- 🚀 Full project execution

**Available Demo Scenarios:**
1. **Read Later Digest** - Automate article summarization
2. **E-commerce Platform** - Build online store
3. **Data Dashboard** - Analytics visualization
4. **Custom Project** - Describe your own idea
        """
        
        console.print(Panel(Markdown(welcome_text), title="Welcome", border_style="blue"))
    
    async def run_conversation_demo(self, scenario: int):
        """Run a demo conversation based on selected scenario."""
        scenarios = {
            1: {
                "name": "Read Later Digest",
                "messages": [
                    "I need help building something to manage my reading list",
                    "I save articles to Pocket but never have time to read them all",
                    "I'd like daily email summaries of my saved articles, maybe AI-generated",
                    "Budget is around $5k, need it in 2-3 weeks",
                    "Oh, and let me filter by topics I'm interested in"
                ]
            },
            2: {
                "name": "E-commerce Platform", 
                "messages": [
                    "I want to build an online store for handmade crafts",
                    "Need product catalog, shopping cart, and payment processing",
                    "Should work on mobile and desktop",
                    "Integration with Stripe for payments and inventory tracking",
                    "Budget $10k, timeline 1 month"
                ]
            },
            3: {
                "name": "Data Dashboard",
                "messages": [
                    "We need a dashboard to visualize our sales data",
                    "Pull data from our PostgreSQL database and Google Analytics",
                    "Real-time updates, interactive charts, export to PDF",
                    "Role-based access for different team members",
                    "Need it deployed on AWS, budget $8k"
                ]
            }
        }
        
        scenario_data = scenarios.get(scenario, scenarios[1])
        
        console.print(f"\n[bold cyan]Starting Demo: {scenario_data['name']}[/bold cyan]\n")
        
        # Run conversation
        for i, message in enumerate(scenario_data['messages'], 1):
            # Display user message
            console.print(Panel(
                message,
                title=f"You ({i}/{len(scenario_data['messages'])})",
                border_style="green"
            ))
            
            # Process with Hermes
            with console.status("Hermes is thinking..."):
                response, self.state = await self.hermes.process_conversation(
                    message,
                    session_id=self.state.session_id if self.state else None
                )
            
            # Display Hermes response
            console.print(Panel(
                response,
                title="Hermes",
                subtitle=f"Intent: {self.state.intent_state.current_bucket.value} ({self.state.intent_state.confidence:.0%})",
                border_style="blue"
            ))
            
            # Pause between messages
            await asyncio.sleep(1)
        
        # Check if ready for handoff
        if self.state.ready_for_handoff:
            console.print("\n[bold green]✅ Project requirements gathered - Ready for handoff![/bold green]\n")
        else:
            console.print("\n[bold yellow]⚠️  More information needed for handoff[/bold yellow]\n")
    
    async def generate_project_brief(self):
        """Generate and display project brief."""
        console.print("\n[bold cyan]Generating Project Brief...[/bold cyan]\n")
        
        with console.status("Analyzing conversation and extracting requirements..."):
            generator = BriefGenerator()
            self.brief = generator.generate_brief(self.state)
            await asyncio.sleep(1)  # Dramatic pause
        
        # Display brief summary
        brief_table = Table(title="Project Brief Summary", show_header=True)
        brief_table.add_column("Field", style="cyan")
        brief_table.add_column("Value", style="white")
        
        brief_table.add_row("Project Name", self.brief.name)
        brief_table.add_row("Type", self.brief.project_type.value.replace('_', ' ').title())
        brief_table.add_row("Priority", self.brief.priority.value.upper())
        brief_table.add_row("Complexity", f"{self.brief.estimate_complexity()}/10")
        brief_table.add_row("Timeline", f"{self.brief.timeline.estimated_duration_days} days")
        brief_table.add_row("Budget", self.brief.budget_range or "Flexible")
        
        console.print(brief_table)
        
        # Display requirements
        if self.brief.requirements:
            console.print("\n[bold]Key Requirements:[/bold]")
            for req in self.brief.requirements[:5]:
                console.print(f"  • {req.description} [{req.priority.value}]")
        
        # Display technical specs
        console.print("\n[bold]Technical Components:[/bold]")
        console.print(f"  • Backend: {len(self.brief.technical_spec.backend_requirements)} components")
        console.print(f"  • APIs: {len(self.brief.technical_spec.api_endpoints)} endpoints")
        console.print(f"  • Database: {len(self.brief.technical_spec.database_needs)} requirements")
        console.print(f"  • Security: {len(self.brief.technical_spec.security_requirements)} measures")
    
    async def decompose_into_tasks(self):
        """Decompose project into tasks."""
        console.print("\n[bold cyan]Decomposing into Development Tasks...[/bold cyan]\n")
        
        with console.status("Creating task breakdown..."):
            decomposer = TaskDecomposer()
            self.tasks = decomposer.decompose_project(self.brief)
            await asyncio.sleep(1)
        
        # Display tasks by agent
        assignments = decomposer.assign_agents(self.tasks)
        
        task_table = Table(title="Task Assignments", show_header=True)
        task_table.add_column("Agent", style="cyan")
        task_table.add_column("Tasks", style="yellow") 
        task_table.add_column("Total Hours", style="green")
        task_table.add_column("Key Responsibilities", style="white")
        
        agent_details = {
            "apollo": ("Apollo 🏛️", "Backend APIs, Database, Business Logic"),
            "aphrodite": ("Aphrodite 🎨", "UI/UX, Frontend Components, Design"),
            "athena": ("Athena 🛡️", "Testing, Security, Quality Assurance"),
            "hephaestus": ("Hephaestus 🔨", "DevOps, Deployment, Infrastructure")
        }
        
        for agent, agent_tasks in assignments.items():
            if agent_tasks:
                agent_name, responsibilities = agent_details.get(agent.value, (agent.value, ""))
                total_hours = sum(task.estimated_hours for task in agent_tasks)
                task_table.add_row(
                    agent_name,
                    str(len(agent_tasks)),
                    f"{total_hours}h",
                    responsibilities
                )
        
        console.print(task_table)
        
        # Show timeline
        timeline = decomposer.estimate_timeline(self.tasks)
        console.print(f"\n[bold]Timeline Estimate:[/bold]")
        console.print(f"  • Total Work: {timeline['total_hours']} hours")
        console.print(f"  • Parallel Execution: {timeline['parallel_days']} days")
        console.print(f"  • Team Size: {timeline['agents_needed']} agents")
    
    async def simulate_handoff(self):
        """Simulate the handoff process."""
        console.print("\n[bold cyan]Initiating Handoff to Development Team...[/bold cyan]\n")
        
        # Create dramatic progress animation
        handoff_steps = [
            "Connecting to Task Orchestrator...",
            "Transmitting project brief...",
            "Assigning tasks to agents...",
            "Setting up development environment...",
            "Initializing team collaboration..."
        ]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            for step in handoff_steps:
                task = progress.add_task(step, total=None)
                await asyncio.sleep(1)
                progress.update(task, completed=True)
        
        # Display handoff result
        handoff_panel = f"""
🎉 **Handoff Successful!**

Your project has been assigned to our AI development team:

**Project**: {self.brief.name}
**Handoff ID**: handoff_{datetime.now().strftime('%Y%m%d_%H%M%S')}

**Team Assigned**:
• Apollo (Backend): 4 tasks
• Aphrodite (Frontend): 2 tasks  
• Athena (QA): 2 tasks
• Hephaestus (DevOps): 2 tasks

**What Happens Next**:
1. Team reviews requirements and creates technical architecture
2. Development begins in parallel across all agents
3. Regular progress updates via Hermes
4. Testing and quality assurance throughout
5. Deployment to production environment

**Estimated Delivery**: {self.brief.timeline.estimated_duration_days} days

The team is now setting up the project. You'll receive the first update shortly!
        """
        
        console.print(Panel(handoff_panel, title="Handoff Complete", border_style="green"))
    
    async def run_custom_project(self):
        """Allow user to describe their own project."""
        console.print("\n[bold cyan]Custom Project Mode[/bold cyan]\n")
        console.print("Describe your project to Hermes. Type 'done' when finished.\n")
        
        while True:
            user_input = console.input("[green]You:[/green] ")
            
            if user_input.lower() == 'done':
                break
            
            # Process with Hermes
            with console.status("Hermes is thinking..."):
                response, self.state = await self.hermes.process_conversation(
                    user_input,
                    session_id=self.state.session_id if self.state else None
                )
            
            console.print(f"\n[blue]Hermes:[/blue] {response}")
            console.print(f"[dim]Intent: {self.state.intent_state.current_bucket.value} ({self.state.intent_state.confidence:.0%})[/dim]\n")
            
            if self.state.ready_for_handoff:
                console.print("[bold green]✅ Ready for handoff![/bold green]")
                break
    
    async def run(self):
        """Run the interactive demo."""
        await self.initialize()
        
        while True:
            self.display_welcome()
            
            # Get scenario choice
            choice = console.input("\nSelect scenario (1-4) or 'q' to quit: ")
            
            if choice.lower() == 'q':
                console.print("\n[bold]Thank you for using Hermes! 👋[/bold]\n")
                break
            
            try:
                scenario = int(choice)
                if scenario not in [1, 2, 3, 4]:
                    console.print("[red]Please select 1-4[/red]")
                    continue
            except ValueError:
                console.print("[red]Please enter a number 1-4[/red]")
                continue
            
            # Run selected scenario
            if scenario == 4:
                await self.run_custom_project()
            else:
                await self.run_conversation_demo(scenario)
            
            if self.state and self.state.ready_for_handoff:
                # Continue with handoff flow
                await self.generate_project_brief()
                
                if console.input("\n[bold]Continue to task decomposition? (y/n):[/bold] ").lower() == 'y':
                    await self.decompose_into_tasks()
                    
                    if console.input("\n[bold]Execute handoff to development team? (y/n):[/bold] ").lower() == 'y':
                        await self.simulate_handoff()
            
            console.input("\n[dim]Press Enter to continue...[/dim]")
            
            # Reset for next demo
            self.state = None
            self.brief = None
            self.tasks = []


async def main():
    """Run the demo."""
    try:
        demo = HandoffDemo()
        await demo.run()
    except KeyboardInterrupt:
        console.print("\n\n[bold red]Demo interrupted by user[/bold red]\n")
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]\n")
        raise


if __name__ == "__main__":
    console.print("""
╔══════════════════════════════════════════════════════════════╗
║      🎭 Hermes Multi-Agent Handoff Interactive Demo 🎭      ║
║                                                              ║
║  Natural Conversation → AI Development Team Assignment       ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())