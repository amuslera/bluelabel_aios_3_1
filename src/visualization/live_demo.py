#!/usr/bin/env python3
"""
Live Agent Visualization Demo

Shows agents working in real-time with visible progress and updates.
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


async def animate_progress(visualizer, agent_name, activity_type, description, 
                         start_progress=0, end_progress=100, duration=10,
                         code_snippet=None):
    """Animate progress for an agent over time"""
    steps = 20  # Number of updates
    progress_step = (end_progress - start_progress) / steps
    time_step = duration / steps
    
    for i in range(steps + 1):
        current_progress = start_progress + (i * progress_step)
        await visualizer.update_agent_activity(
            agent_name,
            activity_type,
            f"{description} ({int(current_progress)}%)",
            progress=current_progress,
            code_snippet=code_snippet
        )
        await asyncio.sleep(time_step)


async def live_demo():
    """Run a live demo with visible action"""
    console = Console()
    visualizer = CleanVisualizer(console=console)
    
    # Welcome screen
    console.clear()
    console.print(Panel(
        Align.center(
            Text.from_markup(
                "[bold cyan]Live AI Agent Demonstration[/bold cyan]\n\n"
                "[yellow]Watch agents work in real-time![/yellow]\n\n"
                "[green]• You'll see live progress updates[/green]\n"
                "[green]• Agents will communicate as they work[/green]\n"
                "[green]• Code will appear as it's written[/green]\n"
                "[green]• Metrics will update in real-time[/green]\n\n"
                "[dim]Press Ctrl+C to exit anytime[/dim]",
                justify="center"
            )
        ),
        title="Live Demo",
        border_style="blue",
        height=12
    ))
    await asyncio.sleep(4)
    
    # Create layout and start live display
    layout = visualizer.create_layout()
    
    with Live(
        layout,
        console=console,
        refresh_per_second=8,  # Higher refresh rate
        screen=True
    ) as live:
        try:
            # Initial state - all idle
            for agent_name in ["Marcus Chen", "Emily Rodriguez", "Alex Thompson", "Jordan Kim"]:
                await visualizer.update_agent_activity(
                    agent_name,
                    ActivityType.IDLE,
                    "Waiting for sprint to begin...",
                    progress=0
                )
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(3)
            
            # === PHASE 1: SPRINT KICKOFF ===
            await visualizer.send_message(
                "System", "Team",
                "🎯 Sprint Kickoff: Building Authentication System",
                "announcement"
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # Set initial workflow
            visualizer.update_workflow("Authentication Sprint", [
                {"name": "Architecture Planning", "completed": False},
                {"name": "Backend Development", "completed": False},
                {"name": "Frontend Development", "completed": False},
                {"name": "Testing & QA", "completed": False},
                {"name": "Deployment", "completed": False}
            ])
            
            # === PHASE 2: PLANNING ===
            console.print("\n[bold yellow]👀 Watch Marcus plan the architecture...[/bold yellow]")
            
            # Marcus starts planning - animate his progress
            await animate_progress(
                visualizer, "Marcus Chen", ActivityType.THINKING,
                "Designing JWT authentication architecture",
                0, 100, 8
            )
            
            # Update metrics and workflow
            visualizer.update_workflow("Authentication Sprint", [
                {"name": "Architecture Planning", "completed": True},
                {"name": "Backend Development", "completed": False},
                {"name": "Frontend Development", "completed": False},
                {"name": "Testing & QA", "completed": False},
                {"name": "Deployment", "completed": False}
            ])
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            await visualizer.send_message(
                "Marcus Chen", "Team",
                "✅ Architecture complete! JWT with refresh tokens, OAuth2 for social login",
                "status"
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(3)
            
            # === PHASE 3: BACKEND DEVELOPMENT ===
            console.print("\n[bold yellow]👀 Watch Marcus code the backend API...[/bold yellow]")
            
            # Marcus codes with live code updates
            code_snippets = [
                "from fastapi import FastAPI, HTTPException\nfrom jose import JWTError, jwt\nimport bcrypt",
                "class AuthService:\n    def __init__(self, secret_key: str):\n        self.secret = secret_key",
                "async def login(self, email: str, password: str):\n    user = await User.find_by_email(email)\n    if not user or not bcrypt.checkpw(password, user.password):\n        raise HTTPException(401, 'Invalid credentials')",
                "def create_token(self, user_id: str) -> str:\n    payload = {'user_id': user_id, 'exp': datetime.utcnow() + timedelta(hours=1)}\n    return jwt.encode(payload, self.secret, algorithm='HS256')"
            ]
            
            # Animate coding with different code snippets
            for i, code in enumerate(code_snippets):
                progress = 20 + (i * 20)
                await visualizer.update_agent_activity(
                    "Marcus Chen",
                    ActivityType.CODING,
                    f"Implementing authentication service",
                    progress=progress,
                    code_snippet=code
                )
                visualizer.metrics["lines_written"] += 15
                await visualizer.render_frame(layout)
                live.update(layout)
                await asyncio.sleep(4)  # Slower so you can see code appear
                
            await visualizer.send_message(
                "Marcus Chen", "Emily Rodriguez",
                "🔗 Backend API ready! Endpoints: POST /auth/login, /auth/refresh",
                "handoff"
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # === PHASE 4: FRONTEND DEVELOPMENT ===
            console.print("\n[bold yellow]👀 Watch Emily build the frontend...[/bold yellow]")
            
            await visualizer.send_message(
                "Emily Rodriguez", "Marcus Chen",
                "Perfect! Starting on the login UI now 🎨",
                "response"
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # Emily codes frontend with live updates
            frontend_code = [
                "import React, { useState } from 'react';\nimport { useAuth } from '../hooks/useAuth';",
                "export function LoginForm() {\n  const [email, setEmail] = useState('');\n  const [password, setPassword] = useState('');\n  const { login, loading } = useAuth();",
                "const handleSubmit = async (e: React.FormEvent) => {\n  e.preventDefault();\n  try {\n    await login(email, password);\n    navigate('/dashboard');\n  } catch (error) {\n    showError(error.message);\n  }\n};",
                "return (\n  <form onSubmit={handleSubmit} className='login-form'>\n    <input type='email' value={email} onChange={(e) => setEmail(e.target.value)} />\n    <input type='password' value={password} onChange={(e) => setPassword(e.target.value)} />\n    <button type='submit' disabled={loading}>Login</button>\n  </form>\n);"
            ]
            
            for i, code in enumerate(frontend_code):
                progress = 15 + (i * 20)
                await visualizer.update_agent_activity(
                    "Emily Rodriguez",
                    ActivityType.CODING,
                    f"Building React login components",
                    progress=progress,
                    code_snippet=code
                )
                visualizer.metrics["lines_written"] += 12
                await visualizer.render_frame(layout)
                live.update(layout)
                await asyncio.sleep(4)
                
            # Update workflow
            visualizer.update_workflow("Authentication Sprint", [
                {"name": "Architecture Planning", "completed": True},
                {"name": "Backend Development", "completed": True},
                {"name": "Frontend Development", "completed": True},
                {"name": "Testing & QA", "completed": False},
                {"name": "Deployment", "completed": False}
            ])
            
            # === PHASE 5: TESTING ===
            console.print("\n[bold yellow]👀 Watch Alex test the system...[/bold yellow]")
            
            await visualizer.send_message(
                "Alex Thompson", "Team",
                "🧪 Starting comprehensive test suite for auth system",
                "status"
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # Alex runs tests with live progress
            test_phases = [
                ("Setting up test environment", 10),
                ("Testing user registration flow", 25),
                ("Testing login with valid credentials", 40),
                ("Testing invalid login attempts", 55),
                ("Testing JWT token validation", 70),
                ("Running security vulnerability scans", 85),
                ("Generating test report", 100)
            ]
            
            for phase, progress in test_phases:
                await visualizer.update_agent_activity(
                    "Alex Thompson",
                    ActivityType.TESTING,
                    phase,
                    progress=progress
                )
                
                # Add some test results
                if progress > 20:
                    visualizer.metrics["tests_passed"] += 3
                if progress == 55:  # Found some issues
                    visualizer.metrics["bugs_found"] += 2
                    await visualizer.send_message(
                        "Alex Thompson", "Team",
                        "🐛 Found 2 edge cases: empty password handling & rate limiting",
                        "alert"
                    )
                    
                await visualizer.render_frame(layout)
                live.update(layout)
                await asyncio.sleep(2)
                
            await visualizer.send_message(
                "Alex Thompson", "Team",
                f"✅ Testing complete! {visualizer.metrics['tests_passed']} tests passed, {visualizer.metrics['bugs_found']} issues documented",
                "success"
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(3)
            
            # === PHASE 6: DEPLOYMENT ===
            console.print("\n[bold yellow]👀 Watch Jordan deploy to production...[/bold yellow]")
            
            await visualizer.send_message(
                "Jordan Kim", "Team",
                "🚀 Starting production deployment pipeline",
                "status"
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # Jordan deploys with live progress
            deploy_steps = [
                ("Building Docker containers", 15),
                ("Running security scans", 30),
                ("Deploying to staging environment", 45),
                ("Running automated smoke tests", 60),
                ("Blue-green deployment to production", 80),
                ("Verifying health checks", 95),
                ("Deployment successful!", 100)
            ]
            
            for step, progress in deploy_steps:
                await visualizer.update_agent_activity(
                    "Jordan Kim",
                    ActivityType.DEPLOYING,
                    step,
                    progress=progress
                )
                await visualizer.render_frame(layout)
                live.update(layout)
                await asyncio.sleep(3)  # Slower for deployment steps
                
            visualizer.metrics["deployments"] += 1
            
            # Final workflow update
            visualizer.update_workflow("Authentication Sprint", [
                {"name": "Architecture Planning", "completed": True},
                {"name": "Backend Development", "completed": True},
                {"name": "Frontend Development", "completed": True},
                {"name": "Testing & QA", "completed": True},
                {"name": "Deployment", "completed": True}
            ])
            
            await visualizer.send_message(
                "System", "Team",
                "🎉 SPRINT COMPLETE! Authentication system is live in production!",
                "announcement"
            )
            
            # === PHASE 7: CELEBRATION ===
            console.print("\n[bold green]🎉 Sprint completed successfully![/bold green]")
            
            # Set all agents to accomplished
            for agent_name in ["Marcus Chen", "Emily Rodriguez", "Alex Thompson", "Jordan Kim"]:
                await visualizer.update_agent_activity(
                    agent_name,
                    ActivityType.IDLE,
                    "Sprint completed! 🎉",
                    progress=100
                )
                
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(8)  # Let user see final state
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Demo interrupted by user[/yellow]")
            
    # Final summary
    console.clear()
    console.print(Panel(
        Align.center(
            Text.from_markup(
                "[bold green]🎉 Live Demo Complete![/bold green]\n\n"
                "[cyan]What you just witnessed:[/cyan]\n"
                "• Real-time agent collaboration\n"
                "• Live progress tracking and updates\n"
                "• Inter-agent communication\n"
                "• Code generation visualization\n"
                "• Sprint workflow management\n\n"
                "[yellow]Final Sprint Results:[/yellow]\n"
                f"📝 {visualizer.metrics['lines_written']} lines of code written\n"
                f"✅ {visualizer.metrics['tests_passed']} tests passed\n"
                f"🐛 {visualizer.metrics['bugs_found']} bugs found and documented\n"
                f"🚀 {visualizer.metrics['deployments']} successful deployment\n\n"
                "[bold cyan]The AI agents successfully delivered[/bold cyan]\n"
                "[bold cyan]a production-ready authentication system![/bold cyan]",
                justify="center"
            )
        ),
        height=18,
        border_style="green"
    ))


if __name__ == "__main__":
    try:
        asyncio.run(live_demo())
    except KeyboardInterrupt:
        print("\n\nDemo ended by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()