#!/usr/bin/env python3
"""
Fixed Agent Visualization Demo

Working demonstration of the AI agent visualization system.
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

from src.visualization.agent_visualizer import AgentVisualizer, ActivityType
from src.visualization.activity_simulator import ActivitySimulator


async def run_fixed_demo():
    """Run a properly working demo"""
    console = Console()
    
    # Create visualizer
    visualizer = AgentVisualizer(console=console)
    simulator = ActivitySimulator(visualizer)
    
    # Set slower speed for better visibility
    visualizer.pacing.speed_multiplier = 0.5
    visualizer.pacing.current_preset = "slow"
    
    # Clear screen
    console.clear()
    
    # Create and render layout
    layout = visualizer.create_layout()
    
    # Initialize some activities for each agent
    await visualizer.update_agent_activity(
        "Marcus Chen",
        ActivityType.THINKING,
        "Analyzing requirements",
        progress=0,
        metadata={"mood": "focused"}
    )
    
    await visualizer.update_agent_activity(
        "Emily Rodriguez",
        ActivityType.IDLE,
        "Waiting for backend API specs",
        progress=0,
        metadata={"mood": "neutral"}
    )
    
    await visualizer.update_agent_activity(
        "Alex Thompson",
        ActivityType.IDLE,
        "Preparing test framework",
        progress=0,
        metadata={"mood": "excited"}
    )
    
    await visualizer.update_agent_activity(
        "Jordan Kim",
        ActivityType.IDLE,
        "Setting up CI/CD pipeline",
        progress=0,
        metadata={"mood": "happy"}
    )
    
    # Run with live display
    with Live(
        layout,
        console=console,
        refresh_per_second=10,
        screen=True
    ) as live:
        try:
            # Initial render
            await visualizer.render_frame(layout)
            live.update(layout)
            
            # Wait a moment for user to see initial state
            await asyncio.sleep(2)
            
            # Send initial message
            await visualizer.send_message(
                "System",
                "Team",
                "🎬 Starting AI Development Team Demo - Watch as our agents collaborate!",
                "announcement"
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # Planning Phase
            await visualizer.send_message(
                "Marcus Chen",
                "Team",
                "Let's start planning the sprint. I'll design the backend architecture.",
                "planning"
            )
            await visualizer.update_agent_activity(
                "Marcus Chen",
                ActivityType.DESIGNING,
                "Creating API architecture",
                progress=20,
                metadata={"mood": "focused"}
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # More planning
            await visualizer.send_message(
                "Emily Rodriguez",
                "Marcus Chen",
                "I'll need the API endpoints for the frontend. What's the timeline?",
                "question"
            )
            await visualizer.update_agent_activity(
                "Emily Rodriguez",
                ActivityType.THINKING,
                "Planning UI components",
                progress=10,
                metadata={"mood": "curious"}
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # Start coding
            await visualizer.update_agent_activity(
                "Marcus Chen",
                ActivityType.CODING,
                "Implementing user authentication API",
                progress=30,
                code_snippet="@app.post('/auth/login')\nasync def login(credentials: UserCredentials):\n    # Validate user credentials",
                metadata={"mood": "focused"}
            )
            visualizer.metrics["lines_written"] += 10
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(3)
            
            # Emily starts coding
            await visualizer.update_agent_activity(
                "Emily Rodriguez",
                ActivityType.CODING,
                "Building login component",
                progress=25,
                code_snippet="const LoginForm = () => {\n  const [email, setEmail] = useState('');\n  return <form>...",
                metadata={"mood": "creative"}
            )
            visualizer.metrics["lines_written"] += 15
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(3)
            
            # Alex starts testing
            await visualizer.send_message(
                "Alex Thompson",
                "Team",
                "I'm setting up the test suite for the authentication flow.",
                "status"
            )
            await visualizer.update_agent_activity(
                "Alex Thompson",
                ActivityType.TESTING,
                "Writing authentication tests",
                progress=40,
                metadata={"mood": "methodical"}
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # Jordan monitoring
            await visualizer.update_agent_activity(
                "Jordan Kim",
                ActivityType.MONITORING,
                "Monitoring build pipeline",
                progress=50,
                metadata={"mood": "vigilant"}
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # Update workflow
            visualizer.update_workflow(
                "Sprint 1: Authentication System",
                [
                    {"name": "API Design", "completed": True},
                    {"name": "Backend Implementation", "completed": False},
                    {"name": "Frontend Components", "completed": False},
                    {"name": "Testing", "completed": False},
                    {"name": "Deployment", "completed": False}
                ]
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(3)
            
            # More interactions
            await visualizer.send_message(
                "Marcus Chen",
                "Emily Rodriguez",
                "API endpoints are ready at /api/v1/auth/*. Here's the documentation.",
                "handoff"
            )
            await visualizer.update_agent_activity(
                "Marcus Chen",
                ActivityType.CODING,
                "Adding JWT token validation",
                progress=60,
                metadata={"mood": "productive"}
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # Testing phase
            await visualizer.send_message(
                "Alex Thompson",
                "Team",
                "Running integration tests... Found 2 edge cases we need to handle.",
                "alert"
            )
            visualizer.metrics["tests_passed"] += 8
            visualizer.metrics["bugs_found"] += 2
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # Final deployment
            await visualizer.update_agent_activity(
                "Jordan Kim",
                ActivityType.DEPLOYING,
                "Deploying to staging environment",
                progress=80,
                metadata={"mood": "focused"}
            )
            visualizer.metrics["deployments"] += 1
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(3)
            
            # Completion
            await visualizer.send_message(
                "System",
                "Team",
                "🎉 Demo Complete! Great teamwork on the authentication system!",
                "announcement"
            )
            
            # Update workflow to complete
            visualizer.update_workflow(
                "Sprint 1: Authentication System",
                [
                    {"name": "API Design", "completed": True},
                    {"name": "Backend Implementation", "completed": True},
                    {"name": "Frontend Components", "completed": True},
                    {"name": "Testing", "completed": True},
                    {"name": "Deployment", "completed": True}
                ]
            )
            
            # Set all agents to idle
            for agent_name in ["Marcus Chen", "Emily Rodriguez", "Alex Thompson", "Jordan Kim"]:
                await visualizer.update_agent_activity(
                    agent_name,
                    ActivityType.IDLE,
                    "Sprint completed successfully!",
                    progress=100,
                    metadata={"mood": "accomplished"}
                )
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(5)
            
        except KeyboardInterrupt:
            console.print("\n[red]Demo interrupted by user[/red]")
            
    # Clear screen and show completion
    console.clear()
    console.print(Panel(
        Align.center(
            Text("Demo Complete!\n\nThe AI agents successfully collaborated on the authentication system.", 
                 style="bold green"),
            vertical="middle"
        ),
        height=5,
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
                "[dim]Starting demo...[/dim]",
                justify="center"
            ),
            vertical="middle"
        ),
        title="Welcome",
        border_style="blue",
        height=8
    ))
    
    await asyncio.sleep(2)
    
    # Run the demo
    await run_fixed_demo()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()