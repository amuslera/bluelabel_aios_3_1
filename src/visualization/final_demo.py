#!/usr/bin/env python3
"""
Final Agent Visualization Demo

Complete demo that keeps the console running with summary panel at the bottom.
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


async def final_demo():
    """Run the final demo with persistent console and summary panel"""
    console = Console()
    visualizer = ImprovedVisualizer(console=console)
    
    # Welcome screen
    console.clear()
    console.print(Panel(
        Align.center(
            Text.from_markup(
                "[bold cyan]Final AI Agent Visualization[/bold cyan]\n\n"
                "[yellow]Complete Experience:[/yellow]\n"
                "• Action history for each agent\n"
                "• Two-line text wrapping\n"
                "• Agent initials in chat\n"
                "• Persistent console after completion\n"
                "• Summary panel at bottom\n"
                "• Automatic session export\n\n"
                "[green]Watch the complete sprint![/green]\n\n"
                "[dim]Press Ctrl+C to exit after completion[/dim]",
                justify="center"
            )
        ),
        title="Final Demo",
        border_style="blue",
        height=15
    ))
    await asyncio.sleep(4)
    
    # Track console messages
    console_messages = []
    exported_file = None
    
    # Create initial layout (no summary panel yet)
    layout = visualizer.create_layout(show_summary=False)
    
    with Live(
        layout,
        console=console,
        refresh_per_second=6,
        screen=True
    ) as live:
        try:
            # === INITIALIZATION ===
            console_messages.append("🎯 Sprint Initialization")
            
            for agent_name in ["Marcus Chen", "Emily Rodriguez", "Alex Thompson", "Jordan Kim"]:
                await visualizer.update_agent_activity(
                    agent_name,
                    ActivityType.IDLE,
                    "Ready for sprint assignment",
                    progress=0
                )
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # === SPRINT SETUP ===
            console_messages.append("📋 Sprint Planning Started")
            
            await visualizer.send_message(
                "System", "Team",
                "🎯 Sprint Goal: Build E-Commerce Authentication System",
                "announcement"
            )
            
            visualizer.update_workflow("Authentication Sprint", [
                {"name": "Requirements & Analysis", "completed": False},
                {"name": "Architecture Design", "completed": False},
                {"name": "Backend Development", "completed": False},
                {"name": "Frontend Development", "completed": False},
                {"name": "Testing & Quality Assurance", "completed": False},
                {"name": "Production Deployment", "completed": False}
            ])
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # === REQUIREMENTS PHASE ===
            console_messages.append("📊 Requirements Analysis")
            
            requirements_tasks = [
                ("Gathering authentication requirements", 20),
                ("Analyzing security compliance needs", 40),
                ("Defining user story acceptance criteria", 60),
                ("Documenting API specification", 80),
                ("Requirements review and approval", 100)
            ]
            
            for task, progress in requirements_tasks:
                await visualizer.update_agent_activity(
                    "Marcus Chen", ActivityType.THINKING,
                    task, progress
                )
                await visualizer.render_frame(layout)
                live.update(layout)
                await asyncio.sleep(2)
            
            await visualizer.send_message(
                "Marcus Chen", "Team",
                "Requirements complete: JWT auth, OAuth2 social login, MFA support",
                "status"
            )
            
            visualizer.update_workflow("Authentication Sprint", [
                {"name": "Requirements & Analysis", "completed": True},
                {"name": "Architecture Design", "completed": False},
                {"name": "Backend Development", "completed": False},
                {"name": "Frontend Development", "completed": False},
                {"name": "Testing & Quality Assurance", "completed": False},
                {"name": "Production Deployment", "completed": False}
            ])
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # === ARCHITECTURE PHASE ===
            console_messages.append("🏗️ Architecture Design")
            
            architecture_tasks = [
                ("Designing database schema", 25),
                ("Planning API endpoint structure", 50),
                ("Defining security architecture", 75),
                ("Creating system architecture diagram", 100)
            ]
            
            for task, progress in architecture_tasks:
                await visualizer.update_agent_activity(
                    "Marcus Chen", ActivityType.DESIGNING,
                    task, progress
                )
                await visualizer.render_frame(layout)
                live.update(layout)
                await asyncio.sleep(2.5)
            
            # Emily starts UI planning
            await visualizer.update_agent_activity(
                "Emily Rodriguez", ActivityType.DESIGNING,
                "Creating login/signup UI mockups", 40
            )
            
            await visualizer.send_message(
                "Emily Rodriguez", "Marcus Chen",
                "Should we include biometric login option?",
                "question"
            )
            
            await visualizer.send_message(
                "Marcus Chen", "Emily Rodriguez",
                "Phase 2 feature - focus on core auth first",
                "response"
            )
            
            visualizer.update_workflow("Authentication Sprint", [
                {"name": "Requirements & Analysis", "completed": True},
                {"name": "Architecture Design", "completed": True},
                {"name": "Backend Development", "completed": False},
                {"name": "Frontend Development", "completed": False},
                {"name": "Testing & Quality Assurance", "completed": False},
                {"name": "Production Deployment", "completed": False}
            ])
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # === BACKEND DEVELOPMENT ===
            console_messages.append("⚙️ Backend Implementation")
            
            backend_tasks = [
                ("Setting up FastAPI project", 10),
                ("Implementing user model", 25),
                ("Creating JWT service", 40),
                ("Building auth endpoints", 55),
                ("Adding OAuth2 integration", 70),
                ("Implementing rate limiting", 85),
                ("Adding comprehensive logging", 100)
            ]
            
            for task, progress in backend_tasks:
                await visualizer.update_agent_activity(
                    "Marcus Chen", ActivityType.CODING,
                    task, progress
                )
                visualizer.metrics["lines_written"] += 18
                await visualizer.render_frame(layout)
                live.update(layout)
                await asyncio.sleep(2.5)
            
            await visualizer.send_message(
                "Marcus Chen", "Emily Rodriguez",
                "Backend API complete! Swagger docs available at /docs",
                "handoff"
            )
            
            visualizer.update_workflow("Authentication Sprint", [
                {"name": "Requirements & Analysis", "completed": True},
                {"name": "Architecture Design", "completed": True},
                {"name": "Backend Development", "completed": True},
                {"name": "Frontend Development", "completed": False},
                {"name": "Testing & Quality Assurance", "completed": False},
                {"name": "Production Deployment", "completed": False}
            ])
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # === FRONTEND DEVELOPMENT ===
            console_messages.append("🎨 Frontend Development")
            
            await visualizer.send_message(
                "Emily Rodriguez", "Marcus Chen",
                "Excellent! Starting React components now",
                "response"
            )
            
            frontend_tasks = [
                ("Setting up React TypeScript project", 15),
                ("Creating authentication context", 30),
                ("Building login form component", 45),
                ("Implementing signup workflow", 60),
                ("Adding form validation", 75),
                ("Creating password reset flow", 90),
                ("Styling with responsive design", 100)
            ]
            
            for task, progress in frontend_tasks:
                await visualizer.update_agent_activity(
                    "Emily Rodriguez", ActivityType.CODING,
                    task, progress
                )
                visualizer.metrics["lines_written"] += 14
                await visualizer.render_frame(layout)
                live.update(layout)
                await asyncio.sleep(2.5)
            
            visualizer.update_workflow("Authentication Sprint", [
                {"name": "Requirements & Analysis", "completed": True},
                {"name": "Architecture Design", "completed": True},
                {"name": "Backend Development", "completed": True},
                {"name": "Frontend Development", "completed": True},
                {"name": "Testing & Quality Assurance", "completed": False},
                {"name": "Production Deployment", "completed": False}
            ])
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # === TESTING PHASE ===
            console_messages.append("🔍 Quality Assurance")
            
            await visualizer.send_message(
                "Alex Thompson", "Team",
                "Beginning comprehensive test suite execution",
                "status"
            )
            
            testing_tasks = [
                ("Setting up test environment", 12),
                ("Writing unit tests for auth logic", 25),
                ("Creating API integration tests", 40),
                ("Testing security vulnerabilities", 55),
                ("Running cross-browser tests", 70),
                ("Performance and load testing", 85),
                ("Generating test reports", 100)
            ]
            
            for task, progress in testing_tasks:
                await visualizer.update_agent_activity(
                    "Alex Thompson", ActivityType.TESTING,
                    task, progress
                )
                visualizer.metrics["tests_passed"] += 5
                
                if progress == 55:  # Security testing finds issues
                    visualizer.metrics["bugs_found"] += 4
                    await visualizer.send_message(
                        "Alex Thompson", "Team",
                        "Security scan found 4 issues: password policy, session timeout, CSRF tokens, input sanitization",
                        "alert"
                    )
                    
                await visualizer.render_frame(layout)
                live.update(layout)
                await asyncio.sleep(2.5)
            
            await visualizer.send_message(
                "Alex Thompson", "Team",
                f"Testing complete! {visualizer.metrics['tests_passed']} tests passed, {visualizer.metrics['bugs_found']} security issues documented",
                "success"
            )
            
            visualizer.update_workflow("Authentication Sprint", [
                {"name": "Requirements & Analysis", "completed": True},
                {"name": "Architecture Design", "completed": True},
                {"name": "Backend Development", "completed": True},
                {"name": "Frontend Development", "completed": True},
                {"name": "Testing & Quality Assurance", "completed": True},
                {"name": "Production Deployment", "completed": False}
            ])
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # === DEPLOYMENT PHASE ===
            console_messages.append("🚀 Production Deployment")
            
            await visualizer.send_message(
                "Jordan Kim", "Team",
                "Initiating production deployment sequence",
                "status"
            )
            
            deployment_tasks = [
                ("Building production Docker images", 15),
                ("Running security compliance scans", 30),
                ("Deploying to staging environment", 45),
                ("Executing automated smoke tests", 60),
                ("Configuring CDN and load balancer", 75),
                ("Blue-green production deployment", 90),
                ("Monitoring deployment health", 100)
            ]
            
            for task, progress in deployment_tasks:
                await visualizer.update_agent_activity(
                    "Jordan Kim", ActivityType.DEPLOYING,
                    task, progress
                )
                await visualizer.render_frame(layout)
                live.update(layout)
                await asyncio.sleep(3)  # Slower for deployment steps
            
            visualizer.metrics["deployments"] += 1
            
            # === SPRINT COMPLETION ===
            console_messages.append("🎉 Sprint Successfully Completed")
            
            await visualizer.send_message(
                "System", "Team",
                "🎉 SPRINT COMPLETE! Authentication system live in production!",
                "announcement"
            )
            
            # Set all agents to accomplished
            for agent_name in ["Marcus Chen", "Emily Rodriguez", "Alex Thompson", "Jordan Kim"]:
                await visualizer.update_agent_activity(
                    agent_name,
                    ActivityType.IDLE,
                    "Sprint completed successfully! 🎉",
                    progress=100
                )
            
            visualizer.update_workflow("Authentication Sprint", [
                {"name": "Requirements & Analysis", "completed": True},
                {"name": "Architecture Design", "completed": True},
                {"name": "Backend Development", "completed": True},
                {"name": "Frontend Development", "completed": True},
                {"name": "Testing & Quality Assurance", "completed": True},
                {"name": "Production Deployment", "completed": True}
            ])
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(3)
            
            # === EXPORT SESSION ===
            console_messages.append("💾 Exporting session data")
            exported_file = visualizer.export_session_log()
            console_messages.append(f"✅ Session exported: {os.path.basename(exported_file)}")
            
            # === SWITCH TO SUMMARY LAYOUT ===
            # Create new layout with summary panel
            summary_layout = visualizer.create_layout(show_summary=True)
            
            # Render with summary panel
            await visualizer.render_frame(summary_layout, console_messages, exported_file)
            live.update(summary_layout)
            
            # === KEEP CONSOLE RUNNING ===
            console.print(f"\n[bold green]✨ Demo complete! Console will stay active.[/bold green]")
            console.print(f"[dim]You can review the agent activities above. Press Ctrl+C to exit.[/dim]")
            
            # Keep running until user interrupts
            while True:
                # Update time in footer and refresh
                await visualizer.render_frame(summary_layout, console_messages, exported_file)
                live.update(summary_layout)
                await asyncio.sleep(5)  # Refresh every 5 seconds
                
        except KeyboardInterrupt:
            console.print(f"\n[yellow]Demo ended by user. Session data preserved.[/yellow]")


if __name__ == "__main__":
    try:
        asyncio.run(final_demo())
    except KeyboardInterrupt:
        print("\n\nDemo ended by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()