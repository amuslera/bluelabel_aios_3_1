#!/usr/bin/env python3
"""
Demo script showing Hermes in action with a simulated conversation.
Shows how Hermes guides users from vague ideas to concrete project requirements.
"""

import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import print as rprint
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.specialists.hermes.hermes_agent_simple import (
    SimpleHermesAgent, PersonaConfig, IntentBucket
)
from src.agents.specialists.hermes.persona_system import PersonaLibrary

console = Console()


async def simulate_conversation():
    """Simulate a realistic conversation with Hermes."""
    
    # Create Hermes with business-focused persona
    persona = PersonaLibrary.get_business_persona()
    config = PersonaConfig(**persona.to_config())
    hermes = SimpleHermesAgent(persona_config=config)
    
    # Simulated conversation
    conversation_script = [
        ("Hi, I need help with my business", 1.5),
        ("I run a small bakery and want to expand online", 2.0),
        ("I'd like customers to order custom cakes through the website", 2.5),
        ("We make about 20-30 custom orders per week currently", 2.0),
        ("Yes, we need to show photos of our previous work", 1.8),
        ("And handle deposits for large orders", 1.5),
    ]
    
    console.print(Panel.fit(
        "[bold cyan]🪽 Hermes Concierge Demo[/bold cyan]\n"
        "Watch how Hermes guides a bakery owner to define their project",
        border_style="cyan"
    ))
    
    # Process conversation
    state = None
    for i, (user_input, delay) in enumerate(conversation_script):
        # User typing effect
        console.print(f"\n[blue]User:[/blue] ", end="")
        for char in user_input:
            console.print(char, end="")
            await asyncio.sleep(0.03)
        console.print()
        
        # Hermes thinking
        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]Hermes is thinking..."),
            transient=True
        ) as progress:
            progress.add_task("thinking", total=None)
            await asyncio.sleep(0.5)
        
        # Process conversation
        response, state = hermes.process_conversation(
            user_input, 
            session_id=state.session_id if state else None
        )
        
        # Hermes response with typing effect
        console.print(f"[green]Hermes:[/green] ", end="")
        words = response.split()
        for j, word in enumerate(words):
            console.print(word, end=" ")
            if j % 10 == 9:  # Add newline every 10 words for readability
                console.print()
                console.print("       ", end="")  # Indent continuation
            await asyncio.sleep(0.05)
        console.print()
        
        # Show intent tracking
        console.print(
            f"[dim]📊 Intent: {state.intent_state.current_bucket.value} "
            f"({state.intent_state.confidence:.0%}) - "
            f"Type: {state.intent_state.specific_type or 'exploring'}[/dim]"
        )
        
        # Pause between turns
        await asyncio.sleep(delay)
    
    # Show final analysis
    console.print("\n" + "="*60 + "\n")
    console.print(Panel.fit(
        "[bold green]✅ Conversation Analysis Complete[/bold green]",
        border_style="green"
    ))
    
    # Intent Evolution Table
    console.print("\n[bold]Intent Evolution:[/bold]")
    evolution_table = Table(show_header=True, header_style="bold magenta")
    evolution_table.add_column("Turn", style="cyan", width=6)
    evolution_table.add_column("User Input", style="white", width=40)
    evolution_table.add_column("Intent", style="green", width=15)
    evolution_table.add_column("Confidence", style="yellow", width=10)
    
    for snapshot in state.intent_state.evolution:
        evolution_table.add_row(
            str(snapshot.turn),
            snapshot.user_input[:40] + "..." if len(snapshot.user_input) > 40 else snapshot.user_input,
            snapshot.bucket.value,
            f"{snapshot.confidence:.0%}"
        )
    
    console.print(evolution_table)
    
    # Extracted Requirements
    console.print("\n[bold]Extracted Requirements:[/bold]")
    if state.project_requirements:
        req_table = Table(show_header=False)
        req_table.add_column("Field", style="cyan")
        req_table.add_column("Value", style="white")
        
        for key, value in state.project_requirements.items():
            req_table.add_row(key.replace("_", " ").title(), str(value))
        
        console.print(req_table)
    else:
        console.print("[dim]No requirements extracted yet[/dim]")
    
    # Ready for handoff?
    console.print(f"\n[bold]Ready for Project Handoff:[/bold] ", end="")
    if state.ready_for_handoff:
        console.print("[green]Yes ✅[/green]")
        console.print("\n[bold cyan]Next Step:[/bold cyan] Hand off to AI development team:")
        console.print("  • Apollo (Backend) - API and database design")
        console.print("  • Aphrodite (Frontend) - Beautiful cake gallery UI")
        console.print("  • Athena (QA) - Payment security testing")
        console.print("  • Hephaestus (DevOps) - Deploy to cloud")
    else:
        console.print("[yellow]Not yet - need more information[/yellow]")
        clarifications = state._get_clarifications_needed()
        if clarifications:
            console.print("\n[bold]Still need to clarify:[/bold]")
            for item in clarifications:
                console.print(f"  • {item.replace('_', ' ').title()}")
    
    # Export options
    console.print("\n[bold]Session Export:[/bold]")
    console.print(f"  • Session ID: {state.session_id}")
    console.print(f"  • Total turns: {state.turn_count}")
    console.print("  • Export formats: Markdown, JSON")
    
    # Save exports
    import os
    os.makedirs("hermes_sessions", exist_ok=True)
    
    # Export as markdown
    md_export = hermes.export_session(state.session_id, format="markdown")
    md_path = f"hermes_sessions/bakery_session_{state.session_id[:8]}.md"
    with open(md_path, "w") as f:
        f.write(md_export)
    console.print(f"  • Saved: {md_path}")
    
    # Export as JSON
    json_export = hermes.export_session(state.session_id, format="json")
    json_path = f"hermes_sessions/bakery_session_{state.session_id[:8]}.json"
    with open(json_path, "w") as f:
        f.write(json_export)
    console.print(f"  • Saved: {json_path}")


async def main():
    """Run the demo."""
    try:
        await simulate_conversation()
        console.print("\n[bold green]Demo complete! 🎉[/bold green]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())