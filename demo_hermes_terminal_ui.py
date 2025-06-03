#!/usr/bin/env python3
"""
Interactive Terminal UI for Hermes Concierge Agent.
Provides a rich terminal interface for conversing with Hermes.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.specialists.hermes.hermes_agent_simple import (
    SimpleHermesAgent, PersonaConfig, IntentBucket
)
from src.agents.specialists.hermes.persona_system import PersonaLibrary

console = Console()


class HermesTerminalUI:
    """Terminal UI for interacting with Hermes."""
    
    def __init__(self):
        self.hermes = None
        self.session = None
        self.history = InMemoryHistory()
        self.layout = self._create_layout()
        
    def _create_layout(self):
        """Create the terminal UI layout."""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        # Split main area
        layout["main"].split_row(
            Layout(name="conversation", ratio=2),
            Layout(name="sidebar", ratio=1)
        )
        
        return layout
    
    def _update_header(self):
        """Update the header panel."""
        header = Panel(
            Align.center(
                Text("🪽 Hermes Concierge - AI Project Assistant", style="bold cyan"),
                vertical="middle"
            ),
            style="blue"
        )
        self.layout["header"].update(header)
    
    def _update_footer(self):
        """Update the footer panel."""
        footer_text = "Commands: /help | /persona | /export | /reset | /quit"
        footer = Panel(
            Align.center(Text(footer_text, style="dim"), vertical="middle"),
            style="dim"
        )
        self.layout["footer"].update(footer)
    
    def _update_conversation(self, messages):
        """Update the conversation panel."""
        conv_text = Text()
        
        for msg in messages[-10:]:  # Show last 10 messages
            role = msg["role"]
            content = msg["content"]
            
            if role == "user":
                conv_text.append("You: ", style="bold blue")
                conv_text.append(content + "\n", style="white")
            else:
                conv_text.append("Hermes: ", style="bold green") 
                conv_text.append(content + "\n", style="white")
            
            conv_text.append("\n")
        
        conv_panel = Panel(
            conv_text,
            title="[bold]Conversation[/bold]",
            border_style="green"
        )
        self.layout["conversation"].update(conv_panel)
    
    def _update_sidebar(self):
        """Update the sidebar with session info."""
        if not self.session:
            sidebar = Panel(
                "No active session",
                title="[bold]Session Info[/bold]",
                border_style="yellow"
            )
            self.layout["sidebar"].update(sidebar)
            return
        
        # Create info table
        info_table = Table(show_header=False, box=None)
        info_table.add_column("Field", style="cyan")
        info_table.add_column("Value", style="white")
        
        info_table.add_row("Session ID", self.session.session_id[:8] + "...")
        info_table.add_row("Started", self.session.created_at.strftime("%I:%M %p"))
        info_table.add_row("Turns", str(self.session.turn_count))
        info_table.add_row("", "")  # Spacer
        
        # Intent info
        intent = self.session.intent_state
        info_table.add_row("Intent", intent.current_bucket.value)
        info_table.add_row("Type", intent.specific_type or "exploring")
        info_table.add_row("Confidence", f"{intent.confidence:.0%}")
        info_table.add_row("", "")  # Spacer
        
        # Requirements
        reqs = self.session.project_requirements
        if reqs:
            info_table.add_row("[bold]Requirements[/bold]", "")
            for key, value in list(reqs.items())[:3]:  # Show first 3
                info_table.add_row(f"  {key}", str(value)[:20])
        
        # Ready status
        info_table.add_row("", "")  # Spacer
        ready_text = "[green]Ready ✅[/green]" if self.session.ready_for_handoff else "[yellow]Gathering info...[/yellow]"
        info_table.add_row("Handoff Status", ready_text)
        
        sidebar = Panel(
            info_table,
            title="[bold]Session Info[/bold]",
            border_style="yellow"
        )
        self.layout["sidebar"].update(sidebar)
    
    def _show_help(self):
        """Show help information."""
        help_text = """
[bold cyan]Hermes Commands:[/bold cyan]

[yellow]/help[/yellow]     - Show this help message
[yellow]/persona[/yellow]  - Change Hermes' personality
[yellow]/export[/yellow]   - Export conversation (MD/JSON)
[yellow]/reset[/yellow]    - Start a new conversation
[yellow]/quit[/yellow]     - Exit the application

[bold cyan]Tips:[/bold cyan]
• Tell Hermes about your project idea
• Be specific about features you need
• Mention your target users
• Describe any technical requirements
        """
        console.print(Panel(help_text, title="Help", border_style="blue"))
        input("\nPress Enter to continue...")
    
    def _change_persona(self):
        """Change Hermes' persona."""
        console.print("\n[bold]Available Personas:[/bold]")
        console.print("1. Business Professional")
        console.print("2. Technical Developer") 
        console.print("3. Startup Enthusiast")
        console.print("4. Enterprise Focused")
        
        choice = input("\nSelect persona (1-4): ")
        
        personas = {
            "1": PersonaLibrary.get_business_persona(),
            "2": PersonaLibrary.get_developer_persona(),
            "3": PersonaLibrary.get_startup_persona(),
            "4": PersonaLibrary.get_enterprise_persona()
        }
        
        if choice in personas:
            template = personas[choice]
            config = PersonaConfig(**template.to_config())
            self.hermes = SimpleHermesAgent(persona_config=config)
            console.print(f"[green]✓ Switched to {template.name} persona[/green]")
        else:
            console.print("[red]Invalid choice[/red]")
        
        input("\nPress Enter to continue...")
    
    def _export_session(self):
        """Export the current session."""
        if not self.session:
            console.print("[yellow]No active session to export[/yellow]")
            input("\nPress Enter to continue...")
            return
        
        console.print("\n[bold]Export Format:[/bold]")
        console.print("1. Markdown")
        console.print("2. JSON")
        
        choice = input("\nSelect format (1-2): ")
        
        format_map = {"1": "markdown", "2": "json"}
        if choice not in format_map:
            console.print("[red]Invalid choice[/red]")
            input("\nPress Enter to continue...")
            return
        
        format_type = format_map[choice]
        export_data = self.hermes.export_session(self.session.session_id, format=format_type)
        
        # Save to file
        import os
        os.makedirs("hermes_exports", exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = "md" if format_type == "markdown" else "json"
        filename = f"hermes_exports/session_{timestamp}.{ext}"
        
        with open(filename, "w") as f:
            f.write(export_data)
        
        console.print(f"[green]✓ Exported to {filename}[/green]")
        input("\nPress Enter to continue...")
    
    async def run(self):
        """Run the terminal UI."""
        # Initialize Hermes with default persona
        persona = PersonaLibrary.get_business_persona()
        config = PersonaConfig(**persona.to_config())
        self.hermes = SimpleHermesAgent(persona_config=config)
        
        # Welcome message
        console.clear()
        console.print(Panel.fit(
            "[bold cyan]Welcome to Hermes Concierge![/bold cyan]\n\n"
            "I'm here to help you build software with our AI development team.\n"
            "Tell me about your project idea, and I'll guide you through the process.\n\n"
            "Type [yellow]/help[/yellow] for commands or just start chatting!",
            border_style="cyan"
        ))
        input("\nPress Enter to begin...")
        
        # Main conversation loop
        while True:
            try:
                # Update display
                console.clear()
                self._update_header()
                self._update_footer()
                
                if self.session:
                    self._update_conversation(self.session.messages)
                    self._update_sidebar()
                else:
                    self.layout["conversation"].update(
                        Panel("Start a conversation...", border_style="dim")
                    )
                    self.layout["sidebar"].update(
                        Panel("No session", border_style="dim")
                    )
                
                console.print(self.layout)
                
                # Get user input
                user_input = prompt("\n> ", history=self.history).strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith("/"):
                    command = user_input.lower()
                    
                    if command == "/quit":
                        break
                    elif command == "/help":
                        self._show_help()
                        continue
                    elif command == "/persona":
                        self._change_persona()
                        continue
                    elif command == "/export":
                        self._export_session()
                        continue
                    elif command == "/reset":
                        self.session = None
                        console.print("[green]✓ Started new conversation[/green]")
                        await asyncio.sleep(1)
                        continue
                    else:
                        console.print(f"[red]Unknown command: {command}[/red]")
                        await asyncio.sleep(1)
                        continue
                
                # Process conversation
                with console.status("[cyan]Hermes is thinking...[/cyan]"):
                    response, self.session = self.hermes.process_conversation(
                        user_input,
                        session_id=self.session.session_id if self.session else None
                    )
                
                # Show notification if ready for handoff
                if self.session.ready_for_handoff and self.session.turn_count == len(self.session.messages) // 2:
                    console.print("\n[bold green]✅ I have enough information to start your project![/bold green]")
                    console.print("The AI team is ready to begin development.")
                    await asyncio.sleep(2)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]")
                await asyncio.sleep(2)
        
        # Goodbye
        console.clear()
        console.print(Panel.fit(
            "[bold cyan]Thank you for using Hermes Concierge![/bold cyan]\n\n"
            "Your conversation has been saved.\n"
            "Come back anytime to continue building amazing software! 🪽",
            border_style="cyan"
        ))


async def main():
    """Run the Hermes Terminal UI."""
    ui = HermesTerminalUI()
    await ui.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")