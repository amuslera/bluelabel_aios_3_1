#!/usr/bin/env python3
"""
Agent Activity Visualization Demo

An interactive visualization showing all four agents working together
on a project, with theatrical pacing for human comprehension.

Controls:
- 1-5: Adjust speed (1=slowest, 5=realtime)
- Space: Pause/Resume
- Q: Quit
"""

import asyncio
import sys
import os
from rich.console import Console
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.visualization.agent_visualizer import AgentVisualizer
from src.visualization.activity_simulator import ActivitySimulator
from src.visualization.visualization_config import VisualizationPresets


async def main():
    """Run the visualization demo"""
    console = Console()
    
    # Welcome message
    console.clear()
    console.print("[bold cyan]🤖 AI Development Team Visualization Demo[/bold cyan]\n")
    console.print("Watch as Marcus, Emily, Alex, and Jordan collaborate on a project!\n")
    console.print("[yellow]Controls:[/yellow]")
    console.print("  • 1-5: Adjust speed (1=slowest, 5=realtime)")
    console.print("  • Space: Pause/Resume")
    console.print("  • Q: Quit\n")
    
    # Select visualization preset
    console.print("[cyan]Select visualization mode:[/cyan]")
    console.print("  1. Demo Mode (recommended) - Smooth animations, auto-slowdown")
    console.print("  2. Monitoring Mode - Fast updates, minimal effects")
    console.print("  3. Presentation Mode - Large text, theatrical pacing")
    console.print("  4. Accessibility Mode - High contrast, no animations\n")
    
    choice = console.input("Enter choice (1-4) [1]: ").strip() or "1"
    
    # Apply configuration preset
    if choice == "1":
        config = VisualizationPresets.demo_mode()
        console.print("\n[green]✓ Demo mode selected - Enjoy the show![/green]")
    elif choice == "2":
        config = VisualizationPresets.monitoring_mode()
        console.print("\n[green]✓ Monitoring mode selected - Real-time updates![/green]")
    elif choice == "3":
        config = VisualizationPresets.presentation_mode()
        console.print("\n[green]✓ Presentation mode selected - Perfect for audiences![/green]")
    elif choice == "4":
        config = VisualizationPresets.accessibility_mode()
        console.print("\n[green]✓ Accessibility mode selected - Clear and readable![/green]")
    else:
        config = VisualizationPresets.demo_mode()
        console.print("\n[yellow]Invalid choice. Using demo mode.[/yellow]")
    
    console.print("\n[dim]Starting visualization in 3 seconds...[/dim]")
    await asyncio.sleep(3)
    
    # Create visualizer with selected configuration
    visualizer = AgentVisualizer(console)
    
    # Apply configuration settings
    visualizer.pacing.set_speed(config.default_speed_preset)
    
    # Create activity simulator
    simulator = ActivitySimulator(visualizer)
    
    # Run visualization and simulation concurrently
    try:
        visualization_task = asyncio.create_task(visualizer.run())
        simulation_task = asyncio.create_task(simulator.run_simulation())
        
        # Wait for either to complete
        done, pending = await asyncio.wait(
            [visualization_task, simulation_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel remaining tasks
        for task in pending:
            task.cancel()
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Visualization interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise
    finally:
        # Summary
        console.print("\n[bold cyan]Visualization Summary[/bold cyan]")
        console.print(f"Total messages exchanged: {len(visualizer.messages)}")
        console.print(f"Lines of code written: {visualizer.metrics['lines_written']}")
        console.print(f"Tests passed: {visualizer.metrics['tests_passed']}")
        console.print(f"Bugs found and fixed: {visualizer.metrics['bugs_found']}")
        console.print(f"Successful deployments: {visualizer.metrics['deployments']}")
        
        console.print("\n[green]Thanks for watching! The AI team is ready for the next project.[/green]")


if __name__ == "__main__":
    # Note: In a real implementation, we'd integrate with a proper keyboard
    # input system. For now, this demonstrates the visualization concept.
    asyncio.run(main())