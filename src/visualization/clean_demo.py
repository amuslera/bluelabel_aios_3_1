#!/usr/bin/env python3
"""
Clean Agent Visualization Demo

A cleaner, more organized demonstration of agent collaboration.
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

from src.visualization.clean_visualizer import CleanVisualizer, ActivityType


async def run_clean_demo():
    """Run a clean, organized demo"""
    console = Console()
    visualizer = CleanVisualizer(console=console)
    
    # Welcome
    console.clear()
    console.print(Panel(
        Align.center(
            Text.from_markup(
                "[bold cyan]AI Development Team Visualization[/bold cyan]\n\n"
                "[yellow]Clean, organized view of agent collaboration[/yellow]\n\n"
                "[dim]Starting demo...[/dim]",
                justify="center"
            )
        ),
        title="Welcome",
        border_style="blue",
        height=8
    ))
    await asyncio.sleep(3)
    
    # Create layout
    layout = visualizer.create_layout()
    
    with Live(
        layout,
        console=console,
        refresh_per_second=4,
        screen=True
    ) as live:
        try:
            # Phase 1: Initial Setup
            await visualizer.send_message(
                "System", "Team",
                "Sprint Started: E-Commerce Authentication",
                "announcement"
            )
            
            # Set initial activities
            await visualizer.update_agent_activity(
                "Marcus Chen",
                ActivityType.THINKING,
                "Planning authentication architecture",
                progress=10
            )
            
            await visualizer.update_agent_activity(
                "Emily Rodriguez", 
                ActivityType.DESIGNING,
                "Sketching login UI mockups",
                progress=15
            )
            
            await visualizer.update_agent_activity(
                "Alex Thompson",
                ActivityType.THINKING,
                "Planning security test strategy",
                progress=5
            )
            
            await visualizer.update_agent_activity(
                "Jordan Kim",
                ActivityType.THINKING,
                "Reviewing deployment requirements",
                progress=8
            )
            
            visualizer.update_workflow("Authentication System", [
                {"name": "Planning", "completed": False},
                {"name": "Backend API", "completed": False},
                {"name": "Frontend UI", "completed": False},
                {"name": "Testing", "completed": False},
                {"name": "Deployment", "completed": False}
            ])
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(3)
            
            # Phase 2: Development Begins
            await visualizer.send_message(
                "Marcus Chen", "Team",
                "Starting JWT authentication implementation",
                "status"
            )
            
            await visualizer.update_agent_activity(
                "Marcus Chen",
                ActivityType.CODING,
                "Implementing JWT authentication service",
                progress=35,
                code_snippet="class AuthService:\n    def __init__(self, secret_key):\n        self.secret = secret_key\n        self.algorithm = 'HS256'"
            )
            
            visualizer.metrics["lines_written"] = 87
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(4)
            
            # Phase 3: Frontend Development
            await visualizer.send_message(
                "Emily Rodriguez", "Marcus Chen",
                "Need API endpoints for login form",
                "question"
            )
            
            await visualizer.send_message(
                "Marcus Chen", "Emily Rodriguez", 
                "POST /api/auth/login - ready for testing",
                "response"
            )
            
            await visualizer.update_agent_activity(
                "Emily Rodriguez",
                ActivityType.CODING,
                "Building React login components",
                progress=45,
                code_snippet="export function LoginForm() {\n  const [email, setEmail] = useState('');\n  const [password, setPassword] = useState('');"
            )
            
            visualizer.metrics["lines_written"] = 156
            
            visualizer.update_workflow("Authentication System", [
                {"name": "Planning", "completed": True},
                {"name": "Backend API", "completed": True},
                {"name": "Frontend UI", "completed": False},
                {"name": "Testing", "completed": False},
                {"name": "Deployment", "completed": False}
            ])
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(4)
            
            # Phase 4: Testing
            await visualizer.send_message(
                "Alex Thompson", "Team",
                "Starting comprehensive test suite",
                "status"
            )
            
            await visualizer.update_agent_activity(
                "Alex Thompson",
                ActivityType.TESTING,
                "Running security and integration tests",
                progress=65
            )
            
            visualizer.metrics["tests_passed"] = 23
            visualizer.metrics["bugs_found"] = 2
            
            await visualizer.send_message(
                "Alex Thompson", "Team",
                "Found 2 edge cases - creating bug reports",
                "alert"
            )
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(4)
            
            # Phase 5: Deployment
            await visualizer.update_agent_activity(
                "Jordan Kim",
                ActivityType.DEPLOYING,
                "Deploying to staging environment",
                progress=80
            )
            
            visualizer.metrics["deployments"] = 1
            
            await visualizer.send_message(
                "Jordan Kim", "Team",
                "Deployed to staging - all health checks passing",
                "success"
            )
            
            visualizer.update_workflow("Authentication System", [
                {"name": "Planning", "completed": True},
                {"name": "Backend API", "completed": True},
                {"name": "Frontend UI", "completed": True},
                {"name": "Testing", "completed": True},
                {"name": "Deployment", "completed": True}
            ])
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(4)
            
            # Phase 6: Completion
            await visualizer.send_message(
                "System", "Team",
                "Sprint Complete! All objectives achieved!",
                "announcement"
            )
            
            # Set all agents to idle/accomplished
            for agent_name in ["Marcus Chen", "Emily Rodriguez", "Alex Thompson", "Jordan Kim"]:
                await visualizer.update_agent_activity(
                    agent_name,
                    ActivityType.IDLE,
                    "Sprint completed successfully!",
                    progress=100
                )
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(8)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Demo interrupted[/yellow]")
            
    # Final summary
    console.clear()
    console.print(Panel(
        Align.center(
            Text.from_markup(
                "[bold green]Demo Complete![/bold green]\n\n"
                "[cyan]Sprint Summary:[/cyan]\n"
                f"📝 {visualizer.metrics['lines_written']} lines of code written\n"
                f"✅ {visualizer.metrics['tests_passed']} tests passed\n"
                f"🐛 {visualizer.metrics['bugs_found']} bugs found and fixed\n"
                f"🚀 {visualizer.metrics['deployments']} successful deployment\n\n"
                "[yellow]The AI agents successfully collaborated to build[/yellow]\n"
                "[yellow]a complete authentication system![/yellow]",
                justify="center"
            )
        ),
        height=12,
        border_style="green"
    ))


if __name__ == "__main__":
    try:
        asyncio.run(run_clean_demo())
    except KeyboardInterrupt:
        print("\n\nDemo ended.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()