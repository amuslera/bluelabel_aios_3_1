#!/usr/bin/env python3
"""
Enhanced Agent Visualization Demo

Improved demo with action history, better text handling, console preservation, and log export.
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


async def animate_progress(visualizer, agent_name, activity_type, description, 
                         start_progress=0, end_progress=100, duration=8, steps=4):
    """Animate progress with multiple action updates"""
    progress_step = (end_progress - start_progress) / steps
    time_step = duration / steps
    
    for i in range(steps + 1):
        current_progress = start_progress + (i * progress_step)
        step_description = f"{description} - Step {i+1}/{steps+1}" if i < steps else f"{description} - Complete!"
        
        await visualizer.update_agent_activity(
            agent_name,
            activity_type,
            step_description,
            progress=current_progress
        )
        await asyncio.sleep(time_step)


async def enhanced_demo():
    """Run enhanced demo with all improvements"""
    console = Console()
    visualizer = ImprovedVisualizer(console=console)
    
    # Welcome screen
    console.clear()
    console.print(Panel(
        Align.center(
            Text.from_markup(
                "[bold cyan]Enhanced AI Agent Demonstration[/bold cyan]\n\n"
                "[yellow]New Features:[/yellow]\n"
                "• Action history (last 3-4 actions per agent)\n"
                "• Better text wrapping (2-line max)\n"
                "• Agent initials in chat (MC, ER, AT, JK)\n"
                "• Console preservation after completion\n"
                "• Session log export option\n\n"
                "[green]Watch the agents collaborate![/green]\n\n"
                "[dim]Press Ctrl+C to exit anytime[/dim]",
                justify="center"
            )
        ),
        title="Enhanced Demo",
        border_style="blue",
        height=14
    ))
    await asyncio.sleep(5)
    
    # Create layout and start live display
    layout = visualizer.create_layout()
    
    # Store console content for preservation
    console_messages = []
    
    with Live(
        layout,
        console=console,
        refresh_per_second=6,
        screen=True
    ) as live:
        try:
            # === PHASE 1: INITIALIZATION ===
            console_messages.append("🎯 Initializing AI Development Team...")
            
            # Set all agents to idle initially
            for agent_name in ["Marcus Chen", "Emily Rodriguez", "Alex Thompson", "Jordan Kim"]:
                await visualizer.update_agent_activity(
                    agent_name,
                    ActivityType.IDLE,
                    "Waiting for sprint assignment",
                    progress=0
                )
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # === PHASE 2: SPRINT KICKOFF ===
            console_messages.append("📋 Sprint Planning Phase...")
            
            await visualizer.send_message(
                "System", "Team",
                "🎯 Sprint Kickoff: E-Commerce Authentication System",
                "announcement"
            )
            
            # Set initial workflow
            visualizer.update_workflow("Authentication Sprint", [
                {"name": "Requirements Analysis", "completed": False},
                {"name": "Architecture Design", "completed": False},
                {"name": "Backend Implementation", "completed": False},
                {"name": "Frontend Development", "completed": False},
                {"name": "Quality Assurance", "completed": False},
                {"name": "Production Deployment", "completed": False}
            ])
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # === PHASE 3: REQUIREMENTS & PLANNING ===
            console_messages.append("📊 Requirements Analysis...")
            
            # Marcus analyzes requirements
            await visualizer.update_agent_activity(
                "Marcus Chen", ActivityType.THINKING,
                "Analyzing authentication requirements", 10
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(3)
            
            await visualizer.update_agent_activity(
                "Marcus Chen", ActivityType.DESIGNING,
                "Designing JWT token architecture", 25
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(3)
            
            await visualizer.update_agent_activity(
                "Marcus Chen", ActivityType.THINKING,
                "Planning OAuth2 social login integration", 40
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            await visualizer.send_message(
                "Marcus Chen", "Team",
                "Requirements complete: JWT auth + OAuth2 social login + refresh tokens",
                "status"
            )
            
            # Update workflow
            visualizer.update_workflow("Authentication Sprint", [
                {"name": "Requirements Analysis", "completed": True},
                {"name": "Architecture Design", "completed": False},
                {"name": "Backend Implementation", "completed": False},
                {"name": "Frontend Development", "completed": False},
                {"name": "Quality Assurance", "completed": False},
                {"name": "Production Deployment", "completed": False}
            ])
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # === PHASE 4: ARCHITECTURE DESIGN ===
            console_messages.append("🏗️ Architecture Design Phase...")
            
            await visualizer.update_agent_activity(
                "Marcus Chen", ActivityType.DESIGNING,
                "Creating database schema for users", 60
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(3)
            
            await visualizer.update_agent_activity(
                "Marcus Chen", ActivityType.DESIGNING,
                "Defining API endpoint specifications", 80
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(3)
            
            await visualizer.update_agent_activity(
                "Marcus Chen", ActivityType.REVIEWING,
                "Validating security architecture design", 100
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # Emily starts planning UI
            await visualizer.update_agent_activity(
                "Emily Rodriguez", ActivityType.DESIGNING,
                "Sketching login form wireframes", 20
            )
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            await visualizer.send_message(
                "Emily Rodriguez", "Marcus Chen",
                "Do we need password strength indicators and forgot password flow?",
                "question"
            )
            
            await visualizer.send_message(
                "Marcus Chen", "Emily Rodriguez",
                "Yes - include strength meter and reset email workflow",
                "response"
            )
            
            # Update workflow
            visualizer.update_workflow("Authentication Sprint", [
                {"name": "Requirements Analysis", "completed": True},
                {"name": "Architecture Design", "completed": True},
                {"name": "Backend Implementation", "completed": False},
                {"name": "Frontend Development", "completed": False},
                {"name": "Quality Assurance", "completed": False},
                {"name": "Production Deployment", "completed": False}
            ])
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # === PHASE 5: BACKEND DEVELOPMENT ===
            console_messages.append("⚙️ Backend Development Phase...")
            
            # Marcus implements backend with multiple actions
            backend_tasks = [
                ("Setting up FastAPI project structure", 10),
                ("Implementing user model with SQLAlchemy", 25),
                ("Creating JWT token service", 40),
                ("Building login and registration endpoints", 60),
                ("Adding OAuth2 provider integration", 75),
                ("Implementing password reset functionality", 90),
                ("Adding input validation and error handling", 100)
            ]
            
            for task, progress in backend_tasks:
                await visualizer.update_agent_activity(
                    "Marcus Chen", ActivityType.CODING,
                    task, progress
                )
                visualizer.metrics["lines_written"] += 15
                await visualizer.render_frame(layout)
                live.update(layout)
                await asyncio.sleep(2.5)
            
            await visualizer.send_message(
                "Marcus Chen", "Emily Rodriguez",
                "Backend API ready! Docs at localhost:8000/docs",
                "handoff"
            )
            
            # Update workflow
            visualizer.update_workflow("Authentication Sprint", [
                {"name": "Requirements Analysis", "completed": True},
                {"name": "Architecture Design", "completed": True},
                {"name": "Backend Implementation", "completed": True},
                {"name": "Frontend Development", "completed": False},
                {"name": "Quality Assurance", "completed": False},
                {"name": "Production Deployment", "completed": False}
            ])
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # === PHASE 6: FRONTEND DEVELOPMENT ===
            console_messages.append("🎨 Frontend Development Phase...")
            
            await visualizer.send_message(
                "Emily Rodriguez", "Marcus Chen",
                "Perfect timing! Starting React components now",
                "response"
            )
            
            # Emily builds frontend with action history
            frontend_tasks = [
                ("Setting up React project with TypeScript", 15),
                ("Creating reusable form components", 30),
                ("Building login page with validation", 45),
                ("Implementing registration form", 60),
                ("Adding password strength indicator", 75),
                ("Creating forgot password flow", 90),
                ("Adding OAuth2 social login buttons", 100)
            ]
            
            for task, progress in frontend_tasks:
                await visualizer.update_agent_activity(
                    "Emily Rodriguez", ActivityType.CODING,
                    task, progress
                )
                visualizer.metrics["lines_written"] += 12
                await visualizer.render_frame(layout)
                live.update(layout)
                await asyncio.sleep(2.5)
            
            # Update workflow
            visualizer.update_workflow("Authentication Sprint", [
                {"name": "Requirements Analysis", "completed": True},
                {"name": "Architecture Design", "completed": True},
                {"name": "Backend Implementation", "completed": True},
                {"name": "Frontend Development", "completed": True},
                {"name": "Quality Assurance", "completed": False},
                {"name": "Production Deployment", "completed": False}
            ])
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # === PHASE 7: QUALITY ASSURANCE ===
            console_messages.append("🔍 Quality Assurance Phase...")
            
            await visualizer.send_message(
                "Alex Thompson", "Team",
                "Starting comprehensive testing suite",
                "status"
            )
            
            # Alex tests with detailed actions
            qa_tasks = [
                ("Setting up automated test environment", 10),
                ("Writing unit tests for authentication logic", 25),
                ("Creating integration tests for API endpoints", 40),
                ("Testing password validation edge cases", 55),
                ("Running security vulnerability scans", 70),
                ("Performing cross-browser compatibility tests", 85),
                ("Generating test coverage report", 100)
            ]
            
            for task, progress in qa_tasks:
                await visualizer.update_agent_activity(
                    "Alex Thompson", ActivityType.TESTING,
                    task, progress
                )
                visualizer.metrics["tests_passed"] += 4
                if progress == 55:  # Found some issues
                    visualizer.metrics["bugs_found"] += 3
                    await visualizer.send_message(
                        "Alex Thompson", "Team",
                        "Found 3 edge cases: empty email validation, special chars in passwords, rate limiting",
                        "alert"
                    )
                await visualizer.render_frame(layout)
                live.update(layout)
                await asyncio.sleep(2.5)
            
            await visualizer.send_message(
                "Alex Thompson", "Team",
                f"QA Complete! {visualizer.metrics['tests_passed']} tests passed, {visualizer.metrics['bugs_found']} issues documented",
                "success"
            )
            
            # Update workflow
            visualizer.update_workflow("Authentication Sprint", [
                {"name": "Requirements Analysis", "completed": True},
                {"name": "Architecture Design", "completed": True},
                {"name": "Backend Implementation", "completed": True},
                {"name": "Frontend Development", "completed": True},
                {"name": "Quality Assurance", "completed": True},
                {"name": "Production Deployment", "completed": False}
            ])
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # === PHASE 8: DEPLOYMENT ===
            console_messages.append("🚀 Production Deployment Phase...")
            
            await visualizer.send_message(
                "Jordan Kim", "Team",
                "Initiating production deployment pipeline",
                "status"
            )
            
            # Jordan deploys with detailed steps
            deploy_tasks = [
                ("Building optimized Docker containers", 15),
                ("Running automated security scans", 30),
                ("Deploying to staging environment", 45),
                ("Executing smoke tests on staging", 60),
                ("Configuring load balancer and SSL", 75),
                ("Blue-green deployment to production", 90),
                ("Monitoring health checks and metrics", 100)
            ]
            
            for task, progress in deploy_tasks:
                await visualizer.update_agent_activity(
                    "Jordan Kim", ActivityType.DEPLOYING,
                    task, progress
                )
                await visualizer.render_frame(layout)
                live.update(layout)
                await asyncio.sleep(3)  # Slower for deployment
            
            visualizer.metrics["deployments"] += 1
            
            # Final workflow update
            visualizer.update_workflow("Authentication Sprint", [
                {"name": "Requirements Analysis", "completed": True},
                {"name": "Architecture Design", "completed": True},
                {"name": "Backend Implementation", "completed": True},
                {"name": "Frontend Development", "completed": True},
                {"name": "Quality Assurance", "completed": True},
                {"name": "Production Deployment", "completed": True}
            ])
            
            # === PHASE 9: COMPLETION ===
            console_messages.append("🎉 Sprint Completed Successfully!")
            
            await visualizer.send_message(
                "System", "Team",
                "🎉 SPRINT COMPLETE! Authentication system deployed to production!",
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
                
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(5)
            
        except KeyboardInterrupt:
            console_messages.append("Demo interrupted by user")
            
    # === PRESERVE CONSOLE AND SHOW RESULTS ===
    # Don't clear screen - preserve the visualization
    console.print("\n" + "="*80)
    console.print("[bold green]🎉 Enhanced Demo Complete![/bold green]")
    console.print("="*80)
    
    # Show console log
    console.print("\n[bold cyan]📝 Session Summary:[/bold cyan]")
    for i, msg in enumerate(console_messages[-8:], 1):  # Last 8 messages
        console.print(f"{i:2d}. {msg}")
    
    # Show final metrics
    console.print(f"\n[bold yellow]📊 Final Sprint Results:[/bold yellow]")
    console.print(f"📝 Lines of Code: [cyan]{visualizer.metrics['lines_written']}[/cyan]")
    console.print(f"✅ Tests Passed: [green]{visualizer.metrics['tests_passed']}[/green]")
    console.print(f"🐛 Issues Found: [red]{visualizer.metrics['bugs_found']}[/red]")
    console.print(f"🚀 Deployments: [blue]{visualizer.metrics['deployments']}[/blue]")
    
    # Auto-export log
    console.print(f"\n[bold magenta]💾 Session Export:[/bold magenta]")
    try:
        filename = visualizer.export_session_log()
        console.print(f"✅ Session log automatically exported to: [green]{filename}[/green]")
        console.print(f"📁 File location: [dim]{os.path.abspath(filename)}[/dim]")
        console.print("📄 Log includes: agent actions, messages, metrics, and timeline")
    except Exception as e:
        console.print(f"❌ Export failed: [red]{e}[/red]")
    
    console.print("\n[bold cyan]Thanks for watching the AI team collaboration![/bold cyan]")
    console.print("[dim]The agents successfully delivered a production-ready authentication system.[/dim]")


if __name__ == "__main__":
    try:
        asyncio.run(enhanced_demo())
    except KeyboardInterrupt:
        print("\n\nDemo ended by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()