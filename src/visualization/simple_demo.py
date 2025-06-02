#!/usr/bin/env python3
"""
Simple Agent Visualization Demo

Non-interactive demonstration of the AI agent visualization system.
"""

import asyncio
import sys
from datetime import datetime
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align
from rich.text import Text

# Add src to path for imports
sys.path.insert(0, '/Users/arielmuslera/Development/Projects/bluelabel-AIOSv3.1')

from src.visualization.agent_visualizer import AgentVisualizer
from src.visualization.activity_simulator import ActivitySimulator


async def run_simple_demo():
    """Run a simple non-interactive demo"""
    console = Console()
    
    # Configure visualization
    visualizer = AgentVisualizer()
    simulator = ActivitySimulator(visualizer)
    
    # Set slower speed for better visibility
    visualizer.pacing.speed_multiplier = 0.7
    
    # Agents are already initialized in the visualizer
    # Just update the initial activities
    
    # Clear screen and show title
    console.clear()
    console.print(Panel(
        Align.center(
            Text("AI Agent Visualization Demo", style="bold cyan"),
            vertical="middle"
        ),
        height=3,
        border_style="blue"
    ))
    
    # Run simulation with live display
    with Live(
        visualizer.create_layout(),
        console=console,
        refresh_per_second=10
    ) as live:
        try:
            # Announce start
            await visualizer.send_message(
                "System",
                "Team",
                "🎬 Starting AI Development Team Demo",
                "announcement"
            )
            await asyncio.sleep(2)
            
            # Planning Phase
            console.print("\n[bold yellow]Phase 1: Planning[/bold yellow]")
            await simulator.simulate_planning_phase()
            live.update(visualizer.create_layout())
            await asyncio.sleep(3)
            
            # Development Phase
            console.print("[bold yellow]Phase 2: Development[/bold yellow]")
            await simulator.simulate_development_phase()
            live.update(visualizer.create_layout())
            await asyncio.sleep(3)
            
            # Testing Phase
            console.print("[bold yellow]Phase 3: Testing[/bold yellow]")
            await simulator.simulate_testing_phase()
            live.update(visualizer.create_layout())
            await asyncio.sleep(3)
            
            # Deployment Phase
            console.print("[bold yellow]Phase 4: Deployment[/bold yellow]")
            await simulator.simulate_deployment_phase()
            live.update(visualizer.create_layout())
            await asyncio.sleep(3)
            
            # Final message
            await visualizer.send_message(
                "System",
                "Team",
                "🎉 Demo Complete! Great teamwork everyone!",
                "announcement"
            )
            live.update(visualizer.create_layout())
            await asyncio.sleep(5)
            
        except KeyboardInterrupt:
            console.print("\n[red]Demo interrupted by user[/red]")
            
    # Show completion message
    console.print(Panel(
        Align.center(
            Text("Demo Complete! The AI agents successfully collaborated on the project.", 
                 style="bold green"),
            vertical="middle"
        ),
        height=3,
        border_style="green"
    ))


async def main():
    """Main entry point"""
    console = Console()
    
    # Show welcome
    console.print(Panel(
        Align.center(
            Text.from_markup(
                "[bold cyan]AI Agent Visualization Demo[/bold cyan]\n\n"
                "[yellow]Watch our AI development team in action![/yellow]\n\n"
                "[dim]Starting in 3 seconds...[/dim]",
                justify="center"
            ),
            vertical="middle"
        ),
        title="Welcome",
        border_style="blue",
        height=8
    ))
    
    await asyncio.sleep(3)
    
    # Run the demo
    await run_simple_demo()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()