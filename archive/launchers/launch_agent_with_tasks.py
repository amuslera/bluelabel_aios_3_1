#!/usr/bin/env python3
"""
Launch an agent with specific task file for Sprint 1.6
"""

import asyncio
import sys
import argparse
from pathlib import Path
from rich.console import Console
from enhanced_theatrical_agent import TheatricalAgent, ENHANCED_PERSONAS

console = Console()

class TaskFileAgent(TheatricalAgent):
    """Agent that reads tasks from a file"""
    
    def __init__(self, role: str, task_file: str):
        super().__init__(role)
        self.task_file = Path(task_file)
        self.tasks = []
        
    async def load_tasks(self):
        """Load tasks from markdown file"""
        if not self.task_file.exists():
            console.print(f"[red]Task file not found: {self.task_file}[/red]")
            return False
            
        content = self.task_file.read_text()
        self.show_status("📋 Loading tasks from file")
        await self.think("Reading task assignments")
        
        # Simple task extraction (looks for ### Task headers)
        lines = content.split('\n')
        current_task = None
        
        for line in lines:
            if line.startswith('### Task'):
                if current_task:
                    self.tasks.append(current_task)
                current_task = {'title': line, 'content': []}
            elif current_task and line.strip():
                current_task['content'].append(line)
                
        if current_task:
            self.tasks.append(current_task)
            
        console.print(f"[green]✓ Loaded {len(self.tasks)} tasks[/green]")
        return True
        
    async def execute_tasks(self):
        """Execute all tasks"""
        for i, task in enumerate(self.tasks, 1):
            console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
            console.print(f"[bold yellow]{task['title']}[/bold yellow]")
            console.print(f"[bold cyan]{'='*60}[/bold cyan]")
            
            # Show task details
            await self.type_message("Let me work on this task...")
            
            # Simulate task execution
            if 'MON-001' in task['title']:
                await self.complete_monitoring_server()
            elif 'CC-001' in task['title']:
                await self.setup_control_center()
            else:
                await self.generic_task_execution(task)
                
    async def complete_monitoring_server(self):
        """Simulate completing the monitoring server"""
        await self.show_progress("Completing WebSocket server", [
            "Adding JWT authentication",
            "Implementing event handlers",
            "Setting up Redis persistence",
            "Adding broadcast functionality",
            "Creating connection manager"
        ])
        
        await self.type_message("Creating enhanced monitoring server...")
        
        # Show code being written
        code = '''from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Set
import jwt
import redis
import json

class MonitoringServer:
    def __init__(self):
        self.clients: Set[WebSocket] = set()
        self.redis_client = redis.Redis(decode_responses=True)
        
    async def authenticate(self, token: str) -> bool:
        try:
            jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return True
        except:
            return False'''
            
        console.print(f"\n[green]```python\n{code}\n```[/green]")
        
        await self.type_message("✅ Monitoring server enhanced with all required features!")
        
    async def setup_control_center(self):
        """Simulate setting up control center"""
        await self.show_progress("Setting up Control Center", [
            "Creating project structure",
            "Installing Textual framework",
            "Creating base layout",
            "Setting up 4 panels",
            "Adding keyboard shortcuts"
        ])
        
        await self.type_message("Building Control Center UI...")
        console.print("[green]✅ Control Center structure created![/green]")
        
    async def generic_task_execution(self, task):
        """Generic task execution"""
        await self.type_message(f"Working on: {task['title']}")
        await asyncio.sleep(2)  # Simulate work
        console.print("[green]✅ Task completed![/green]")

async def main():
    parser = argparse.ArgumentParser(description='Launch agent with task file')
    parser.add_argument('role', choices=['backend', 'frontend', 'qa', 'devops'],
                        help='Agent role')
    parser.add_argument('--task-file', required=True,
                        help='Path to task file')
    
    args = parser.parse_args()
    
    # Create and run agent
    agent = TaskFileAgent(args.role, args.task_file)
    
    console.print(f"[bold blue]🎭 Launching {agent.persona['name']} ({args.role})[/bold blue]")
    console.print(f"[blue]Task file: {args.task_file}[/blue]")
    console.print("="*60)
    
    if await agent.load_tasks():
        await agent.execute_tasks()
        console.print(f"\n[bold green]✅ All tasks completed![/bold green]")
    else:
        console.print("[red]Failed to load tasks[/red]")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())