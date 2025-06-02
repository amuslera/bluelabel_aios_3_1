#!/usr/bin/env python3
"""
AI Agent Visualization Showcase

A complete demonstration of the AI development team visualization.
"""

import asyncio
import sys
from datetime import datetime
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
import random

# Add src to path
sys.path.insert(0, '/Users/arielmuslera/Development/Projects/bluelabel-AIOSv3.1')

from src.visualization.agent_visualizer import AgentVisualizer, ActivityType


class ShowcaseDemo:
    """Showcase demonstration of agent visualization"""
    
    def __init__(self):
        self.console = Console()
        self.visualizer = AgentVisualizer(console=self.console)
        self.visualizer.pacing.speed_multiplier = 0.5  # Slower for visibility
        
    async def phase_planning(self):
        """Planning phase"""
        await self.visualizer.send_message(
            "System", "Team", 
            "🎯 Sprint Planning: E-Commerce Authentication System", 
            "announcement"
        )
        await asyncio.sleep(2)
        
        await self.visualizer.update_agent_activity(
            "Marcus Chen", ActivityType.THINKING,
            "Analyzing authentication requirements",
            progress=10, metadata={"mood": "focused"}
        )
        
        await self.visualizer.send_message(
            "Marcus Chen", "Team",
            "I'll design a JWT-based auth system with refresh tokens",
            "planning"
        )
        await asyncio.sleep(2)
        
        await self.visualizer.update_agent_activity(
            "Emily Rodriguez", ActivityType.DESIGNING,
            "Sketching login/signup UI flows",
            progress=15, metadata={"mood": "creative"}
        )
        
        await self.visualizer.send_message(
            "Emily Rodriguez", "Marcus Chen",
            "Will we support social login (Google, GitHub)?",
            "question"
        )
        await asyncio.sleep(2)
        
        await self.visualizer.send_message(
            "Marcus Chen", "Emily Rodriguez",
            "Yes, I'll implement OAuth2 flow for social providers",
            "response"
        )
        
        await self.visualizer.update_agent_activity(
            "Alex Thompson", ActivityType.PLANNING,
            "Creating test plan for auth flows",
            progress=20, metadata={"mood": "methodical"}
        )
        
        await self.visualizer.send_message(
            "Alex Thompson", "Team",
            "I'll focus on security tests - SQL injection, XSS, CSRF",
            "planning"
        )
        await asyncio.sleep(2)
        
        await self.visualizer.update_agent_activity(
            "Jordan Kim", ActivityType.THINKING,
            "Planning deployment strategy",
            progress=10, metadata={"mood": "strategic"}
        )
        
        self.visualizer.update_workflow(
            "Sprint: Authentication System",
            [
                {"name": "Requirements", "completed": True},
                {"name": "Design", "completed": False},
                {"name": "Backend", "completed": False},
                {"name": "Frontend", "completed": False},
                {"name": "Testing", "completed": False},
                {"name": "Deployment", "completed": False}
            ]
        )
        
    async def phase_development(self):
        """Development phase"""
        await self.visualizer.send_message(
            "System", "Team",
            "💻 Development Phase Started",
            "announcement"
        )
        await asyncio.sleep(1)
        
        # Marcus starts coding
        code_snippets = [
            "from fastapi import FastAPI, HTTPException\nfrom jose import JWTError, jwt\nimport bcrypt",
            "class AuthService:\n    def __init__(self, secret_key: str):\n        self.secret = secret_key\n        self.algorithm = 'HS256'",
            "async def create_user(self, email: str, password: str):\n    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())\n    user = await User.create(email=email, password=hashed)",
            "def create_access_token(self, data: dict):\n    to_encode = data.copy()\n    expire = datetime.utcnow() + timedelta(minutes=15)\n    to_encode.update({'exp': expire})\n    return jwt.encode(to_encode, self.secret, algorithm=self.algorithm)"
        ]
        
        for i, snippet in enumerate(code_snippets):
            await self.visualizer.update_agent_activity(
                "Marcus Chen", ActivityType.CODING,
                f"Implementing authentication service",
                progress=30 + (i * 10),
                code_snippet=snippet,
                metadata={"mood": "focused"}
            )
            self.visualizer.metrics["lines_written"] += random.randint(10, 25)
            await asyncio.sleep(3)
        
        # Emily starts frontend
        await self.visualizer.send_message(
            "Emily Rodriguez", "Marcus Chen",
            "What's the login endpoint URL?",
            "question"
        )
        await asyncio.sleep(1)
        
        await self.visualizer.send_message(
            "Marcus Chen", "Emily Rodriguez",
            "POST /api/v1/auth/login - accepts {email, password}",
            "response"
        )
        
        frontend_code = [
            "import { useState } from 'react';\nimport { useAuth } from './hooks/useAuth';",
            "export function LoginForm() {\n  const [email, setEmail] = useState('');\n  const [password, setPassword] = useState('');\n  const { login, loading, error } = useAuth();",
            "const handleSubmit = async (e) => {\n  e.preventDefault();\n  try {\n    await login(email, password);\n    navigate('/dashboard');\n  } catch (err) {\n    setError(err.message);\n  }\n};"
        ]
        
        for i, snippet in enumerate(frontend_code):
            await self.visualizer.update_agent_activity(
                "Emily Rodriguez", ActivityType.CODING,
                "Building login components",
                progress=25 + (i * 15),
                code_snippet=snippet,
                metadata={"mood": "creative"}
            )
            self.visualizer.metrics["lines_written"] += random.randint(15, 30)
            await asyncio.sleep(2)
            
        # Workflow update
        self.visualizer.update_workflow(
            "Sprint: Authentication System",
            [
                {"name": "Requirements", "completed": True},
                {"name": "Design", "completed": True},
                {"name": "Backend", "completed": True},
                {"name": "Frontend", "completed": False},
                {"name": "Testing", "completed": False},
                {"name": "Deployment", "completed": False}
            ]
        )
        
    async def phase_testing(self):
        """Testing phase"""
        await self.visualizer.send_message(
            "Alex Thompson", "Team",
            "Starting comprehensive test suite",
            "status"
        )
        
        test_activities = [
            ("Unit tests for auth service", 20),
            ("Integration tests for API endpoints", 35),
            ("Security vulnerability scanning", 50),
            ("Frontend component tests", 65),
            ("End-to-end user flow tests", 80)
        ]
        
        for activity, progress in test_activities:
            await self.visualizer.update_agent_activity(
                "Alex Thompson", ActivityType.TESTING,
                activity,
                progress=progress,
                metadata={"mood": "methodical"}
            )
            
            # Simulate test results
            passed = random.randint(5, 15)
            self.visualizer.metrics["tests_passed"] += passed
            
            if random.random() < 0.3:  # 30% chance of finding bugs
                bugs = random.randint(1, 3)
                self.visualizer.metrics["bugs_found"] += bugs
                await self.visualizer.send_message(
                    "Alex Thompson", "Team",
                    f"Found {bugs} issue(s) in {activity}",
                    "alert"
                )
                
            await asyncio.sleep(2)
            
        await self.visualizer.send_message(
            "Alex Thompson", "Team",
            f"✅ Test suite complete: {self.visualizer.metrics['tests_passed']} passed, {self.visualizer.metrics['bugs_found']} issues found",
            "success"
        )
        
    async def phase_deployment(self):
        """Deployment phase"""
        await self.visualizer.send_message(
            "Jordan Kim", "Team",
            "Preparing production deployment",
            "status"
        )
        
        deployment_steps = [
            ("Building Docker images", 15),
            ("Running security scans", 30),
            ("Deploying to staging", 45),
            ("Running smoke tests", 60),
            ("Blue-green deployment to production", 80),
            ("Monitoring metrics", 95)
        ]
        
        for step, progress in deployment_steps:
            await self.visualizer.update_agent_activity(
                "Jordan Kim", ActivityType.DEPLOYING,
                step,
                progress=progress,
                metadata={"mood": "focused"}
            )
            await asyncio.sleep(2)
            
        self.visualizer.metrics["deployments"] += 1
        
        await self.visualizer.send_message(
            "Jordan Kim", "Team",
            "🚀 Successfully deployed to production! All systems green.",
            "success"
        )
        
        # Final workflow update
        self.visualizer.update_workflow(
            "Sprint: Authentication System",
            [
                {"name": "Requirements", "completed": True},
                {"name": "Design", "completed": True},
                {"name": "Backend", "completed": True},
                {"name": "Frontend", "completed": True},
                {"name": "Testing", "completed": True},
                {"name": "Deployment", "completed": True}
            ]
        )
        
    async def run(self):
        """Run the complete showcase"""
        # Welcome message
        self.console.clear()
        self.console.print(Panel(
            Align.center(
                Text.from_markup(
                    "[bold cyan]AI Agent Team Visualization[/bold cyan]\n\n"
                    "[yellow]Watch our AI development team build an authentication system[/yellow]\n\n"
                    "Features demonstrated:\n"
                    "• Real-time agent activities with progress tracking\n"
                    "• Inter-agent communication and collaboration\n"
                    "• Live code generation visualization\n"
                    "• Workflow and metrics tracking\n"
                    "• Theatrical pacing for human comprehension\n\n"
                    "[dim]Press Ctrl+C to exit at any time[/dim]",
                    justify="center"
                ),
                vertical="middle"
            ),
            title="Welcome",
            border_style="blue",
            height=15
        ))
        
        await asyncio.sleep(5)
        
        # Create layout
        layout = self.visualizer.create_layout()
        
        # Run with live display
        with Live(
            layout,
            console=self.console,
            refresh_per_second=4,
            screen=True
        ) as live:
            try:
                # Initial state
                await self.visualizer.render_frame(layout)
                live.update(layout)
                
                # Run phases
                self.console.print("\n[bold cyan]Phase 1: Planning[/bold cyan]")
                await self.phase_planning()
                await self.visualizer.render_frame(layout)
                live.update(layout)
                await asyncio.sleep(2)
                
                self.console.print("\n[bold cyan]Phase 2: Development[/bold cyan]")
                await self.phase_development()
                await self.visualizer.render_frame(layout)
                live.update(layout)
                await asyncio.sleep(2)
                
                self.console.print("\n[bold cyan]Phase 3: Testing[/bold cyan]")
                await self.phase_testing()
                await self.visualizer.render_frame(layout)
                live.update(layout)
                await asyncio.sleep(2)
                
                self.console.print("\n[bold cyan]Phase 4: Deployment[/bold cyan]")
                await self.phase_deployment()
                await self.visualizer.render_frame(layout)
                live.update(layout)
                await asyncio.sleep(2)
                
                # Celebration
                await self.visualizer.send_message(
                    "System", "Team",
                    "🎉 Sprint Complete! Authentication system successfully delivered!",
                    "announcement"
                )
                
                # Set all to idle/accomplished
                for agent_name in ["Marcus Chen", "Emily Rodriguez", "Alex Thompson", "Jordan Kim"]:
                    await self.visualizer.update_agent_activity(
                        agent_name,
                        ActivityType.IDLE,
                        "Celebrating successful sprint! 🎉",
                        progress=100,
                        metadata={"mood": "accomplished"}
                    )
                
                await self.visualizer.render_frame(layout)
                live.update(layout)
                
                # Keep displaying for a while
                await asyncio.sleep(10)
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Demo interrupted by user[/yellow]")
                
        # Completion message
        self.console.clear()
        self.console.print(Panel(
            Align.center(
                Text.from_markup(
                    "[bold green]Demo Complete![/bold green]\n\n"
                    f"[cyan]Final Statistics:[/cyan]\n"
                    f"📝 Lines Written: {self.visualizer.metrics['lines_written']}\n"
                    f"✅ Tests Passed: {self.visualizer.metrics['tests_passed']}\n"
                    f"🐛 Bugs Found: {self.visualizer.metrics['bugs_found']}\n"
                    f"🚀 Deployments: {self.visualizer.metrics['deployments']}\n\n"
                    "[yellow]The AI agents successfully collaborated to deliver[/yellow]\n"
                    "[yellow]a complete authentication system![/yellow]",
                    justify="center"
                ),
                vertical="middle"
            ),
            height=12,
            border_style="green"
        ))


async def main():
    """Main entry point"""
    demo = ShowcaseDemo()
    await demo.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo ended.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()