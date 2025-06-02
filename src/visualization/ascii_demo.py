#!/usr/bin/env python3
"""
ASCII Demo - For terminals with Unicode box drawing issues
"""

import asyncio
import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box

# Add src to path
sys.path.insert(0, '/Users/arielmuslera/Development/Projects/bluelabel-AIOSv3.1')

from src.visualization.ascii_visualizer import ASCIIVisualizer
from src.visualization.enhanced_visualizer import ActivityType


async def ascii_demo():
    """Quick ASCII demonstration"""
    console = Console()
    visualizer = ASCIIVisualizer(console=console)
    
    # Clear screen and show welcome
    console.clear()
    console.print(Panel(
        Align.center(
            Text.from_markup(
                "[bold cyan]ASCII Visualization Demo[/bold cyan]\n\n"
                "[yellow]Solid Border Solution:[/yellow]\n"
                "• Uses ASCII characters (+, -, |)\n"
                "• Compatible with all terminals\n"
                "• No Unicode box drawing issues\n\n"
                "[green]Starting ASCII demo...[/green]",
                justify="center"
            )
        ),
        title="ASCII Visualizer",
        border_style="blue",
        box=box.ASCII
    ))
    await asyncio.sleep(3)
    
    # Add sample data
    console.print("\n[cyan]📝 Adding sample messages and activities...[/cyan]")
    
    # Add messages
    messages = [
        ("Marcus Chen", "Team", "🚀 Starting backend development with FastAPI"),
        ("Emily Rodriguez", "Team", "🎨 Creating React components with TypeScript"),
        ("Alex Thompson", "Team", "🔍 Setting up comprehensive test suite"),
        ("Jordan Kim", "Team", "⚙️ Configuring CI/CD pipeline"),
        ("Marcus Chen", "Emily Rodriguez", "API endpoints ready - check Swagger docs"),
        ("Emily Rodriguez", "Marcus Chen", "Perfect! Frontend consuming APIs now"),
        ("Alex Thompson", "Team", "Found 2 security issues - creating tickets"),
        ("Jordan Kim", "Team", "Production deployment successful! 🎉")
    ]
    
    for from_agent, to_agent, content in messages:
        await visualizer.send_message(from_agent, to_agent, content)
    
    # Add agent activities
    activities = [
        ("Marcus Chen", ActivityType.CODING, "Implementing JWT authentication service", 85),
        ("Emily Rodriguez", ActivityType.DESIGNING, "Creating responsive login forms", 70),
        ("Alex Thompson", ActivityType.TESTING, "Running security vulnerability scans", 60),
        ("Jordan Kim", ActivityType.DEPLOYING, "Blue-green production deployment", 95)
    ]
    
    for agent, activity, desc, progress in activities:
        await visualizer.update_agent_activity(agent, activity, desc, progress)
    
    # Add workflow
    visualizer.update_workflow("Sprint Demo", [
        {"name": "Planning", "completed": True},
        {"name": "Development", "completed": True},
        {"name": "Testing", "completed": False},
        {"name": "Deployment", "completed": False}
    ])
    
    # Set metrics
    visualizer.metrics["lines_written"] = 180
    visualizer.metrics["tests_passed"] = 32
    visualizer.metrics["bugs_found"] = 2
    
    console.print(f"✅ Added {len(messages)} messages and {len(activities)} activities")
    
    # Create and render layout
    console.print("\n[cyan]🎨 Rendering ASCII visualization...[/cyan]")
    
    layout = visualizer.create_layout(show_summary=False)
    await visualizer.render_frame(layout)
    
    # Display the layout components individually for clear viewing
    console.print("\n" + "="*80)
    console.print("[bold green]📊 ASCII Visualization Components[/bold green]")
    console.print("="*80)
    
    # Header
    header = visualizer.render_header()
    console.print(header)
    console.print()
    
    # Agent panels in a row
    console.print("[bold cyan]👥 Agent Status[/bold cyan]")
    
    from rich.columns import Columns
    agent_panels = [
        visualizer.render_agent_panel("Marcus Chen"),
        visualizer.render_agent_panel("Emily Rodriguez")
    ]
    console.print(Columns(agent_panels, equal=True))
    console.print()
    
    agent_panels_2 = [
        visualizer.render_agent_panel("Alex Thompson"),
        visualizer.render_agent_panel("Jordan Kim")
    ]
    console.print(Columns(agent_panels_2, equal=True))
    console.print()
    
    # Communication panels
    console.print("[bold cyan]💬 Communication & Progress[/bold cyan]")
    
    comm_panels = [
        visualizer.render_scrollable_messages_panel(),
        visualizer.render_workflow_panel(),
        visualizer.render_metrics_panel()
    ]
    console.print(Columns(comm_panels, equal=True))
    console.print()
    
    # Footer
    footer = visualizer.render_footer()
    console.print(footer)
    
    # Export session
    console.print(f"\n[cyan]💾 Exporting session...[/cyan]")
    export_file = visualizer.export_session_log()
    file_size = os.path.getsize(export_file)
    
    # Final summary
    console.print("\n" + "="*80)
    console.print("[bold green]🎉 ASCII Demo Complete![/bold green]")
    console.print("="*80)
    
    console.print(f"\n[yellow]📊 Demo Statistics:[/yellow]")
    console.print(f"   📨 Messages: {len(visualizer.chat_manager.messages)}")
    console.print(f"   ⚙️ Agent Actions: {sum(len(actions) for actions in visualizer.agent_actions.values())}")
    console.print(f"   📋 Events Logged: {len(visualizer.session_log)}")
    console.print(f"   💾 Export File: {os.path.basename(export_file)} ({file_size:,} bytes)")
    
    console.print(f"\n[bold cyan]✨ ASCII Visualization System Ready![/bold cyan]")
    console.print(f"\n[yellow]Key Features:[/yellow]")
    console.print(f"  ✅ Solid ASCII borders (+, -, |) - No Unicode issues")
    console.print(f"  ✅ Agent action history tracking")
    console.print(f"  ✅ Team communication display")
    console.print(f"  ✅ Live metrics and workflow progress")
    console.print(f"  ✅ Complete session export capability")
    console.print(f"  ✅ Terminal compatibility across all systems")
    
    console.print(f"\n[dim]Session exported to: {export_file}[/dim]")


if __name__ == "__main__":
    try:
        asyncio.run(ascii_demo())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()