#!/usr/bin/env python3
"""
Demo showcasing different conversation scenarios with Hermes.
Shows how Hermes adapts to different project types and user personas.
"""

import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.specialists.hermes.hermes_agent_simple import (
    SimpleHermesAgent, PersonaConfig
)
from src.agents.specialists.hermes.persona_system import PersonaLibrary

console = Console()


async def demo_scenario(title, persona_template, conversations):
    """Run a demo scenario with given persona and conversations."""
    
    console.print(f"\n{'='*60}")
    console.print(Panel.fit(
        f"[bold cyan]{title}[/bold cyan]",
        border_style="cyan"
    ))
    
    # Create Hermes with specified persona
    config = PersonaConfig(**persona_template.to_config())
    hermes = SimpleHermesAgent(persona_config=config)
    
    console.print(f"[dim]Persona: {persona_template.name}[/dim]\n")
    
    # Process conversations
    state = None
    for user_input in conversations:
        console.print(f"[blue]User:[/blue] {user_input}")
        
        response, state = hermes.process_conversation(
            user_input,
            session_id=state.session_id if state else None
        )
        
        # Show response (truncated for readability)
        if len(response) > 150:
            response_display = response[:150] + "..."
        else:
            response_display = response
            
        console.print(f"[green]Hermes:[/green] {response_display}")
        console.print(
            f"[dim]Intent: {state.intent_state.current_bucket.value} "
            f"({state.intent_state.confidence:.0%})[/dim]\n"
        )
    
    # Show final analysis
    console.print("[bold]Final Analysis:[/bold]")
    analysis = Table(show_header=False, box=None)
    analysis.add_column("Metric", style="cyan")
    analysis.add_column("Value", style="white")
    
    analysis.add_row("Project Type", state.intent_state.specific_type or "Unknown")
    analysis.add_row("Confidence", f"{state.intent_state.confidence:.0%}")
    analysis.add_row("Ready for Handoff", "Yes ✅" if state.ready_for_handoff else "No ❌")
    
    if state.project_requirements:
        analysis.add_row("Requirements", str(len(state.project_requirements)) + " extracted")
    
    console.print(analysis)


async def run_all_scenarios():
    """Run all demo scenarios."""
    
    console.print(Panel.fit(
        "[bold cyan]🪽 Hermes Conversation Scenarios Demo[/bold cyan]\n"
        "Demonstrating how Hermes handles different project types",
        border_style="cyan"
    ))
    
    # Scenario 1: E-commerce Project (Business Persona)
    await demo_scenario(
        "Scenario 1: E-commerce Website",
        PersonaLibrary.get_business_persona(),
        [
            "I want to create an online store",
            "We sell handmade jewelry",
            "Need shopping cart and payment processing",
            "Around 100 products initially"
        ]
    )
    
    # Scenario 2: SaaS Platform (Developer Persona)
    await demo_scenario(
        "Scenario 2: SaaS Platform",
        PersonaLibrary.get_developer_persona(),
        [
            "Building a project management SaaS",
            "Need multi-tenant architecture with PostgreSQL",
            "REST API with JWT auth",
            "React frontend with TypeScript"
        ]
    )
    
    # Scenario 3: Startup MVP (Startup Persona)
    await demo_scenario(
        "Scenario 3: Startup MVP",
        PersonaLibrary.get_startup_persona(),
        [
            "I have an idea for a fitness tracking app",
            "Users log workouts and track progress",
            "Need social features for accountability",
            "Want to launch in 6 weeks"
        ]
    )
    
    # Scenario 4: Data Analysis (Technical Persona)
    await demo_scenario(
        "Scenario 4: Data Analysis Pipeline",
        PersonaLibrary.get_developer_persona(),
        [
            "Need to analyze sales data",
            "CSV files updated daily via FTP",
            "Generate automated reports",
            "Dashboard for executives"
        ]
    )
    
    # Scenario 5: Portfolio Website (Student Persona)
    await demo_scenario(
        "Scenario 5: Portfolio Website",
        PersonaLibrary.get_student_persona(),
        [
            "I'm a graphic design student",
            "Need a portfolio to showcase my work",
            "Want it to look modern and creative",
            "Maybe a blog section too"
        ]
    )
    
    # Summary
    console.print(f"\n{'='*60}")
    console.print(Panel.fit(
        "[bold green]✅ All Scenarios Complete![/bold green]\n\n"
        "Hermes successfully handled:\n"
        "• E-commerce websites\n"
        "• SaaS platforms\n"
        "• Startup MVPs\n"
        "• Data analysis pipelines\n"
        "• Portfolio websites\n\n"
        "Each with appropriate persona adaptation!",
        border_style="green"
    ))


async def main():
    """Run the scenarios demo."""
    try:
        await run_all_scenarios()
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())