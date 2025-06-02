#!/usr/bin/env python3
"""
Visualized Agent Task Demo - Watch agents work on a real task

This combines the real task assignment with our visualization system
to show agents collaborating on creating a string formatter utility.
"""

import asyncio
import sys
import os
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from rich.text import Text

# Add src to path
sys.path.insert(0, '/Users/arielmuslera/Development/Projects/bluelabel-AIOSv3.1')

from src.visualization.improved_visualizer import ImprovedVisualizer, ActivityType


async def simulate_real_task(visualizer, layout, live):
    """Simulate agents working on a real development task"""
    
    # Initialize agents
    for agent_name in ["Marcus Chen", "Emily Rodriguez", "Alex Thompson", "Jordan Kim"]:
        await visualizer.update_agent_activity(
            agent_name, ActivityType.IDLE, "Ready for task assignment", 0
        )
    
    await visualizer.render_frame(layout)
    live.update(layout)
    await asyncio.sleep(2)
    
    # Task announcement
    await visualizer.send_message(
        "System", "Team", 
        "📋 New Task: Create string formatting utility module with tests", 
        "announcement"
    )
    
    visualizer.update_workflow("String Formatter Utility", [
        {"name": "Requirements Analysis", "completed": False},
        {"name": "Implementation", "completed": False},
        {"name": "Test Development", "completed": False},
        {"name": "Code Review", "completed": False},
        {"name": "Documentation", "completed": False}
    ])
    
    await visualizer.render_frame(layout)
    live.update(layout)
    await asyncio.sleep(2)
    
    # Marcus analyzes requirements
    await visualizer.update_agent_activity(
        "Marcus Chen", ActivityType.THINKING, 
        "Analyzing requirements for string formatter", 25
    )
    await visualizer.render_frame(layout)
    live.update(layout)
    await asyncio.sleep(2)
    
    await visualizer.send_message(
        "Marcus Chen", "Team",
        "I'll implement 5 utility functions: truncate, snake_to_camel, camel_to_snake, format_file_size, and pluralize",
        "status"
    )
    
    visualizer.update_workflow("String Formatter Utility", [
        {"name": "Requirements Analysis", "completed": True},
        {"name": "Implementation", "completed": False},
        {"name": "Test Development", "completed": False},
        {"name": "Code Review", "completed": False},
        {"name": "Documentation", "completed": False}
    ])
    
    # Marcus implements the utility
    implementation_steps = [
        ("Implementing truncate_string function", 20),
        ("Implementing case conversion functions", 40),
        ("Implementing format_file_size function", 60),
        ("Implementing pluralize function", 80),
        ("Adding docstrings and type hints", 100)
    ]
    
    for step, progress in implementation_steps:
        await visualizer.update_agent_activity(
            "Marcus Chen", ActivityType.CODING, step, progress
        )
        visualizer.metrics["lines_written"] += 30
        await visualizer.render_frame(layout)
        live.update(layout)
        await asyncio.sleep(1.5)
    
    await visualizer.send_message(
        "Marcus Chen", "Alex Thompson",
        "String formatter module complete! Ready for testing",
        "handoff"
    )
    
    visualizer.update_workflow("String Formatter Utility", [
        {"name": "Requirements Analysis", "completed": True},
        {"name": "Implementation", "completed": True},
        {"name": "Test Development", "completed": False},
        {"name": "Code Review", "completed": False},
        {"name": "Documentation", "completed": False}
    ])
    
    # Alex writes tests
    await visualizer.send_message(
        "Alex Thompson", "Marcus Chen",
        "Great work! I'll write comprehensive tests for all functions",
        "response"
    )
    
    test_steps = [
        ("Writing tests for truncate_string", 20),
        ("Writing tests for case conversions", 40),
        ("Writing tests for format_file_size", 60),
        ("Writing tests for pluralize", 80),
        ("Adding edge case tests", 100)
    ]
    
    for step, progress in test_steps:
        await visualizer.update_agent_activity(
            "Alex Thompson", ActivityType.TESTING, step, progress
        )
        visualizer.metrics["tests_passed"] += 4
        await visualizer.render_frame(layout)
        live.update(layout)
        await asyncio.sleep(1.5)
    
    await visualizer.send_message(
        "Alex Thompson", "Team",
        "✅ All tests passing! 20 test cases with 100% coverage",
        "success"
    )
    
    visualizer.update_workflow("String Formatter Utility", [
        {"name": "Requirements Analysis", "completed": True},
        {"name": "Implementation", "completed": True},
        {"name": "Test Development", "completed": True},
        {"name": "Code Review", "completed": False},
        {"name": "Documentation", "completed": False}
    ])
    
    # Emily reviews the code
    await visualizer.update_agent_activity(
        "Emily Rodriguez", ActivityType.REVIEWING,
        "Reviewing code quality and API design", 100
    )
    await visualizer.render_frame(layout)
    live.update(layout)
    await asyncio.sleep(2)
    
    await visualizer.send_message(
        "Emily Rodriguez", "Team",
        "Code looks clean! API is intuitive and well-documented",
        "approval"
    )
    
    visualizer.update_workflow("String Formatter Utility", [
        {"name": "Requirements Analysis", "completed": True},
        {"name": "Implementation", "completed": True},
        {"name": "Test Development", "completed": True},
        {"name": "Code Review", "completed": True},
        {"name": "Documentation", "completed": False}
    ])
    
    # Jordan prepares for deployment
    await visualizer.update_agent_activity(
        "Jordan Kim", ActivityType.MONITORING,
        "Checking CI/CD pipeline and dependencies", 100
    )
    await visualizer.render_frame(layout)
    live.update(layout)
    await asyncio.sleep(2)
    
    await visualizer.send_message(
        "Jordan Kim", "Team",
        "Module ready for integration! No dependency conflicts found",
        "status"
    )
    
    # Task complete
    await visualizer.send_message(
        "System", "Team",
        "🎉 TASK COMPLETE! String formatter utility successfully implemented",
        "announcement"
    )
    
    visualizer.update_workflow("String Formatter Utility", [
        {"name": "Requirements Analysis", "completed": True},
        {"name": "Implementation", "completed": True},
        {"name": "Test Development", "completed": True},
        {"name": "Code Review", "completed": True},
        {"name": "Documentation", "completed": True}
    ])
    
    # Set all agents to completed state
    for agent_name in ["Marcus Chen", "Emily Rodriguez", "Alex Thompson", "Jordan Kim"]:
        await visualizer.update_agent_activity(
            agent_name, ActivityType.IDLE, "Task completed successfully! 🎉", 100
        )
    
    await visualizer.render_frame(layout)
    live.update(layout)
    
    # Final metrics
    visualizer.metrics["lines_written"] = 150  # Utility + tests
    visualizer.metrics["tests_passed"] = 20
    visualizer.metrics["bugs_found"] = 0
    visualizer.metrics["deployments"] = 0
    
    # Export session
    exported_file = visualizer.export_session_log()
    
    return exported_file


async def visualized_agent_task():
    """Run the visualized agent task demo"""
    console = Console()
    visualizer = ImprovedVisualizer(console=console)
    
    # Welcome screen
    console.clear()
    console.print(Panel(
        Align.center(
            Text.from_markup(
                "[bold cyan]Visualized Agent Task Demo[/bold cyan]\n\n"
                "[yellow]Real Task: String Formatter Utility[/yellow]\n\n"
                "Watch as the AI agents collaborate to:\n"
                "• Analyze requirements\n"
                "• Implement utility functions\n"
                "• Write comprehensive tests\n"
                "• Review and approve code\n\n"
                "[green]Starting demonstration...[/green]",
                justify="center"
            )
        ),
        title="Agent Task Demo",
        border_style="blue",
        height=14
    ))
    await asyncio.sleep(3)
    
    # Run the demo
    console.clear()
    layout = visualizer.create_layout(show_summary=False)
    
    with Live(layout, console=console, refresh_per_second=6) as live:
        try:
            exported_file = await simulate_real_task(visualizer, layout, live)
            
            # Show final state for a moment
            await asyncio.sleep(3)
            
        except KeyboardInterrupt:
            console.print(f"\n🚀 Demo interrupted.")
            return
    
    # Post-demo summary
    console.print("\n" + "="*60)
    console.print("[bold green]✨ Task Demonstration Complete![/bold green]")
    console.print("="*60)
    console.print("\n[bold]What we demonstrated:[/bold]")
    console.print("• Marcus analyzed requirements and implemented the utility")
    console.print("• Alex wrote comprehensive tests with full coverage")
    console.print("• Emily reviewed the code for quality")
    console.print("• Jordan checked deployment readiness")
    console.print("\n[bold]Results:[/bold]")
    console.print(f"• 📝 Lines of code: {visualizer.metrics['lines_written']}")
    console.print(f"• ✅ Tests written: {visualizer.metrics['tests_passed']}")
    console.print(f"• 🐛 Bugs found: {visualizer.metrics['bugs_found']}")
    console.print(f"• 📄 Session exported: {os.path.basename(exported_file)}")
    
    console.print("\n[dim]Note: This was a simulation. In a real scenario,")
    console.print("the agents would generate actual code files.[/dim]")


if __name__ == "__main__":
    try:
        asyncio.run(visualized_agent_task())
    except KeyboardInterrupt:
        print("\nDemo ended by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()