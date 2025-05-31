#!/usr/bin/env python3
"""
Join Collaboration - Connect to Multi-Terminal Collaboration

This script allows a Claude Code instance to join a collaborative session
with other Claude Code instances working on the same repository.

Usage:
Terminal 1 (Human): python3 join_collaboration.py --role=human --name="Product Owner"
Terminal 2 (CTO): python3 join_collaboration.py --role=cto --name="CTO Agent"  
Terminal 3 (Backend): python3 join_collaboration.py --role=backend-dev --name="Backend Developer"
"""

import asyncio
import json
import logging
import sys
import argparse
import time
import uuid
from datetime import datetime
import websockets
import threading
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CollaborationClient:
    """Client for connecting to the collaboration server."""
    
    def __init__(self, role: str, name: str, server_url: str = "ws://localhost:8765"):
        self.role = role
        self.name = name
        self.server_url = server_url
        self.client_id = str(uuid.uuid4())
        self.terminal_id = str(uuid.uuid4())
        self.websocket = None
        self.connected = False
        self.collaborators = {}
        self.active_tasks = {}
        
    async def connect(self):
        """Connect to the collaboration server."""
        try:
            print(f"🔗 Connecting to collaboration server: {self.server_url}")
            self.websocket = await websockets.connect(self.server_url)
            self.connected = True
            
            # Register with server
            await self.send_message({
                "type": "register",
                "id": self.client_id,
                "role": self.role,
                "name": self.name,
                "terminal_id": self.terminal_id
            })
            
            print(f"✅ Connected as: {self.name} ({self.role})")
            
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
        
        return True
    
    async def send_message(self, data: dict):
        """Send message to server."""
        if self.websocket and self.connected:
            await self.websocket.send(json.dumps(data))
    
    async def send_chat(self, message: str):
        """Send chat message."""
        await self.send_message({
            "type": "chat",
            "from_id": self.client_id,
            "content": message,
            "metadata": {
                "timestamp": time.time()
            }
        })
    
    async def update_status(self, status: str, current_task: str = None):
        """Update status."""
        await self.send_message({
            "type": "status_update",
            "from_id": self.client_id,
            "status": status,
            "current_task": current_task
        })
    
    async def notify_file_change(self, file_path: str, change_type: str):
        """Notify about file changes."""
        await self.send_message({
            "type": "file_change",
            "from_id": self.client_id,
            "file_path": file_path,
            "change_type": change_type
        })
    
    async def create_task(self, title: str, files_involved: list = None):
        """Create a new task."""
        task_id = str(uuid.uuid4())
        await self.send_message({
            "type": "task_update",
            "task": {
                "id": task_id,
                "title": title,
                "assigned_to": self.client_id,
                "status": "planned",
                "files_involved": files_involved or []
            }
        })
        return task_id
    
    async def listen_for_messages(self):
        """Listen for messages from the server."""
        try:
            async for message_str in self.websocket:
                try:
                    data = json.loads(message_str)
                    await self.handle_server_message(data)
                except json.JSONDecodeError:
                    logger.error("Received invalid JSON from server")
        except websockets.exceptions.ConnectionClosed:
            self.connected = False
            print("🔌 Disconnected from collaboration server")
    
    async def handle_server_message(self, data: dict):
        """Handle messages from the server."""
        message_type = data.get("type")
        
        if message_type == "welcome":
            print(f"📡 {data.get('message')}")
        
        elif message_type == "sync_state":
            self.collaborators = data.get("collaborators", {})
            recent_messages = data.get("recent_messages", [])
            self.active_tasks = data.get("active_tasks", {})
            
            print(f"\n🔄 Synced with collaboration state:")
            print(f"   👥 Active collaborators: {len(self.collaborators)}")
            print(f"   💬 Recent messages: {len(recent_messages)}")
            print(f"   📋 Active tasks: {len(self.active_tasks)}")
            
            # Show current team
            self.show_team_status()
        
        elif message_type == "new_message":
            message = data.get("message", {})
            from_name = data.get("from_name", "Unknown")
            content = message.get("content", "")
            timestamp = datetime.fromtimestamp(message.get("timestamp", 0))
            
            print(f"\n💬 [{timestamp.strftime('%H:%M:%S')}] {from_name}: {content}")
        
        elif message_type == "collaborator_joined":
            collaborator = data.get("collaborator", {})
            print(f"\n✅ {collaborator.get('name')} ({collaborator.get('role')}) joined the team!")
            self.collaborators[collaborator.get('id')] = collaborator
        
        elif message_type == "collaborator_left":
            collab_id = data.get("collaborator_id")
            message = data.get("message", "Someone left")
            print(f"\n👋 {message}")
            if collab_id in self.collaborators:
                del self.collaborators[collab_id]
        
        elif message_type == "task_updated":
            task = data.get("task", {})
            task_id = task.get("id")
            self.active_tasks[task_id] = task
            print(f"\n📋 Task updated: {task.get('title')} [{task.get('status')}]")
        
        elif message_type == "file_changed":
            file_path = data.get("file_path")
            change_type = data.get("change_type")
            changed_by = data.get("changed_by")
            print(f"\n📄 File {change_type}: {file_path} (by {changed_by})")
        
        elif message_type == "status_updated":
            name = data.get("name")
            status = data.get("status")
            current_task = data.get("current_task")
            if current_task:
                print(f"\n🔄 {name} is now {status} - working on: {current_task}")
            else:
                print(f"\n🔄 {name} is now {status}")
    
    def show_team_status(self):
        """Show current team status."""
        print(f"\n👥 Current Team:")
        for collab_id, collab in self.collaborators.items():
            status_icon = "🟢" if collab.get("status") == "active" else "🟡"
            task_info = f" - {collab.get('current_task')}" if collab.get('current_task') else ""
            print(f"   {status_icon} {collab.get('name')} ({collab.get('role')}){task_info}")
    
    def show_help(self):
        """Show available commands."""
        print(f"\n💡 Available commands for {self.role}:")
        print(f"   chat <message>    - Send message to team")
        print(f"   status <status>   - Update your status (active/busy/idle)")
        print(f"   task <title>      - Create new task")
        print(f"   team              - Show team status") 
        print(f"   tasks             - Show active tasks")
        print(f"   help              - Show this help")
        print(f"   quit              - Leave collaboration")
        
        if self.role == "human":
            print(f"\n🎯 As Product Owner, you can:")
            print(f"   - Define requirements and priorities")
            print(f"   - Ask questions about implementation")
            print(f"   - Approve/reject technical decisions")
        
        elif self.role == "cto":
            print(f"\n🎯 As CTO, you can:")
            print(f"   - Provide technical architecture guidance")
            print(f"   - Make technology decisions")
            print(f"   - Review and approve designs")
        
        elif self.role == "backend-dev":
            print(f"\n🎯 As Backend Developer, you can:")
            print(f"   - Implement features and APIs")
            print(f"   - Write tests and documentation")
            print(f"   - Review code changes")
    
    async def run_interactive_session(self):
        """Run interactive collaboration session."""
        print(f"\n🎉 Welcome to AIOSv3 Multi-Terminal Collaboration!")
        print(f"You are: {self.name} ({self.role})")
        print(f"Repository: {Path.cwd()}")
        
        self.show_help()
        
        # Start heartbeat
        heartbeat_task = asyncio.create_task(self.send_heartbeat())
        
        # Start listening for server messages
        listen_task = asyncio.create_task(self.listen_for_messages())
        
        # Interactive command loop
        try:
            while self.connected:
                try:
                    # Get user input
                    user_input = await asyncio.get_event_loop().run_in_executor(
                        None, input, f"\n{self.role}> "
                    )
                    
                    if not user_input.strip():
                        continue
                    
                    # Parse command
                    parts = user_input.strip().split(" ", 1)
                    command = parts[0].lower()
                    args = parts[1] if len(parts) > 1 else ""
                    
                    if command == "quit":
                        break
                    elif command == "help":
                        self.show_help()
                    elif command == "team":
                        self.show_team_status()
                    elif command == "tasks":
                        self.show_active_tasks()
                    elif command == "chat":
                        if args:
                            await self.send_chat(args)
                        else:
                            print("Usage: chat <message>")
                    elif command == "status":
                        if args:
                            await self.update_status(args)
                            print(f"Status updated to: {args}")
                        else:
                            print("Usage: status <active/busy/idle>")
                    elif command == "task":
                        if args:
                            task_id = await self.create_task(args)
                            print(f"Created task: {args} ({task_id})")
                        else:
                            print("Usage: task <title>")
                    else:
                        print(f"Unknown command: {command}. Type 'help' for available commands.")
                
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"Error in interactive session: {e}")
        
        finally:
            heartbeat_task.cancel()
            listen_task.cancel()
            if self.websocket:
                await self.websocket.close()
            print(f"\n👋 {self.name} left the collaboration")
    
    def show_active_tasks(self):
        """Show active tasks."""
        if not self.active_tasks:
            print("📋 No active tasks")
            return
        
        print(f"📋 Active Tasks:")
        for task_id, task in self.active_tasks.items():
            status_icon = {"planned": "📋", "in_progress": "🔄", "completed": "✅", "blocked": "🚫"}.get(task.get("status"), "❓")
            print(f"   {status_icon} {task.get('title')} [{task.get('status')}]")
    
    async def send_heartbeat(self):
        """Send periodic heartbeat."""
        while self.connected:
            try:
                await self.send_message({
                    "type": "heartbeat",
                    "from_id": self.client_id
                })
                await asyncio.sleep(30)  # Every 30 seconds
            except Exception:
                break


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Join AIOSv3 Multi-Terminal Collaboration")
    parser.add_argument("--role", required=True, 
                       choices=["human", "cto", "backend-dev", "frontend-dev", "qa", "devops"],
                       help="Your role in the collaboration")
    parser.add_argument("--name", required=True, help="Your name/identifier")
    parser.add_argument("--server", default="ws://localhost:8765", help="Collaboration server URL")
    
    args = parser.parse_args()
    
    client = CollaborationClient(args.role, args.name, args.server)
    
    if await client.connect():
        await client.run_interactive_session()
    else:
        print("❌ Failed to connect to collaboration server")
        print("💡 Make sure the collaboration server is running:")
        print("   python3 collaboration_server.py")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())