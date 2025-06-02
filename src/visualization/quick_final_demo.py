#!/usr/bin/env python3
"""
Quick Final Demo

Quick version to demonstrate the persistent console with summary panel.
"""

import asyncio
import sys
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from rich.text import Text

# Add src to path
sys.path.insert(0, '/Users/arielmuslera/Development/Projects/bluelabel-AIOSv3.1')

from src.visualization.improved_visualizer import ImprovedVisualizer, ActivityType


async def quick_demo():
    """Quick demo showing persistent console with summary"""
    console = Console()
    visualizer = ImprovedVisualizer(console=console)
    
    console.clear()
    console.print(Panel(
        Align.center(
            Text.from_markup(
                "[bold cyan]Quick Final Demo[/bold cyan]\n\n"
                "[yellow]Demonstrates:[/yellow]\n"
                "• Persistent console after completion\n"
                "• Summary panel at bottom\n"
                "• All improvements working together\n\n"
                "[green]Running quick sprint...[/green]",
                justify="center"
            )
        ),
        title="Quick Demo",
        border_style="blue",
        height=10
    ))
    await asyncio.sleep(3)
    
    console_messages = []
    
    # Create initial layout
    layout = visualizer.create_layout(show_summary=False)
    
    with Live(
        layout,
        console=console,
        refresh_per_second=4,
        screen=True
    ) as live:
        try:
            # Quick sprint simulation
            console_messages.append("🎯 Sprint Started")
            
            # Set agents working
            await visualizer.update_agent_activity(
                "Marcus Chen", ActivityType.THINKING,
                "Analyzing authentication requirements", 25
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            console_messages.append("📋 Planning Phase")
            await visualizer.update_agent_activity(
                "Marcus Chen", ActivityType.DESIGNING,
                "Creating system architecture", 50
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            console_messages.append("⚙️ Development Phase")
            await visualizer.update_agent_activity(
                "Marcus Chen", ActivityType.CODING,
                "Building authentication API", 75
            )
            await visualizer.update_agent_activity(
                "Emily Rodriguez", ActivityType.CODING,
                "Creating login components", 60
            )
            
            await visualizer.send_message("Marcus Chen", "Emily Rodriguez", "API endpoints ready!", "handoff")
            
            visualizer.metrics["lines_written"] = 156
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(3)
            
            console_messages.append("🔍 Testing Phase")
            await visualizer.update_agent_activity(
                "Alex Thompson", ActivityType.TESTING,
                "Running security tests", 80
            )
            visualizer.metrics["tests_passed"] = 24
            visualizer.metrics["bugs_found"] = 2
            
            await visualizer.send_message("Alex Thompson", "Team", "Found 2 security issues to fix", "alert")
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(3)
            
            console_messages.append("🚀 Deployment Phase")
            await visualizer.update_agent_activity(
                "Jordan Kim", ActivityType.DEPLOYING,
                "Deploying to production", 100
            )
            visualizer.metrics["deployments"] = 1
            
            visualizer.update_workflow("Quick Sprint", [
                {"name": "Planning", "completed": True},
                {"name": "Development", "completed": True},
                {"name": "Testing", "completed": True},
                {"name": "Deployment", "completed": True}
            ])
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            console_messages.append("🎉 Sprint Completed")
            await visualizer.send_message("System", "Team", "🎉 Sprint complete! System deployed!", "announcement")
            
            # Set all agents to completed
            for agent_name in ["Marcus Chen", "Emily Rodriguez", "Alex Thompson", "Jordan Kim"]:
                await visualizer.update_agent_activity(
                    agent_name, ActivityType.IDLE,
                    "Sprint completed successfully! 🎉", 100
                )
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(3)
            
            # Export session
            console_messages.append("💾 Exporting session data")
            exported_file = visualizer.export_session_log()
            console_messages.append("✅ Session exported successfully")
            
            # Switch to summary layout
            summary_layout = visualizer.create_layout(show_summary=True)
            await visualizer.render_frame(summary_layout, console_messages, exported_file)
            live.update(summary_layout)
            
            console.print(f"\n[bold green]✨ Demo complete! Console stays active with summary below.[/bold green]")
            console.print(f"[dim]The agents are still visible above with their final states.[/dim]")
            console.print(f"[dim]Press Ctrl+C to exit when ready.[/dim]")
            
            # Keep running with summary panel
            for i in range(60):  # Run for 60 cycles (5 minutes at 5s each)
                await visualizer.render_frame(summary_layout, console_messages, exported_file)
                live.update(summary_layout)
                await asyncio.sleep(5)
                
        except KeyboardInterrupt:
            console.print(f"\n[yellow]Demo ended by user. All data preserved![/yellow]")


if __name__ == "__main__":
    try:
        asyncio.run(quick_demo())
    except KeyboardInterrupt:
        print("\n\nDemo ended.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()