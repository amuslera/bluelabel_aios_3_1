#!/usr/bin/env python3
"""
Collaboration Server for Multi-Terminal Claude Code Collaboration

This creates a shared context server that multiple Claude Code instances
can connect to for real-time collaboration in the same repository.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import websockets
import threading
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CollaboratorInfo:
    """Information about a collaborator."""
    id: str
    role: str  # "human", "cto", "backend-dev", "qa", etc.
    name: str
    terminal_id: str
    last_seen: float
    current_task: Optional[str] = None
    status: str = "active"  # active, busy, idle

@dataclass
class Message:
    """Collaboration message."""
    id: str
    from_id: str
    from_role: str
    timestamp: float
    message_type: str  # "chat", "task_update", "file_change", "question"
    content: str
    metadata: Dict[str, Any]

@dataclass
class TaskInfo:
    """Information about a task being worked on."""
    id: str
    title: str
    assigned_to: str
    status: str  # "planned", "in_progress", "completed", "blocked"
    created_at: float
    updated_at: float
    files_involved: List[str]
    dependencies: List[str]

class CollaborationServer:
    """WebSocket server for real-time collaboration between Claude Code instances."""
    
    def __init__(self, port: int = 8765):
        self.port = port
        self.collaborators: Dict[str, CollaboratorInfo] = {}
        self.messages: List[Message] = []
        self.tasks: Dict[str, TaskInfo] = {}
        self.connected_clients: Set[websockets.WebSocketServerProtocol] = set()
        self.repo_path = Path.cwd()
        
    async def register_collaborator(self, websocket, data: Dict[str, Any]):
        """Register a new collaborator."""
        collaborator_id = data.get("id", str(uuid.uuid4()))
        role = data.get("role", "unknown")
        name = data.get("name", f"{role}_{collaborator_id[:8]}")
        terminal_id = data.get("terminal_id", str(uuid.uuid4()))
        
        collaborator = CollaboratorInfo(
            id=collaborator_id,
            role=role,
            name=name,
            terminal_id=terminal_id,
            last_seen=time.time()
        )
        
        self.collaborators[collaborator_id] = collaborator
        self.connected_clients.add(websocket)
        
        # Broadcast new collaborator
        await self.broadcast({
            "type": "collaborator_joined",
            "collaborator": asdict(collaborator),
            "message": f"{name} ({role}) joined the collaboration"
        }, exclude=websocket)
        
        # Send current state to new collaborator
        await websocket.send(json.dumps({
            "type": "sync_state",
            "collaborators": {k: asdict(v) for k, v in self.collaborators.items()},
            "recent_messages": [asdict(m) for m in self.messages[-50:]],
            "active_tasks": {k: asdict(v) for k, v in self.tasks.items()},
            "repo_path": str(self.repo_path)
        }))
        
        logger.info(f"Registered collaborator: {name} ({role})")
        return collaborator_id
    
    async def handle_message(self, websocket, data: Dict[str, Any]):
        """Handle incoming message from collaborator."""
        message_type = data.get("type")
        
        if message_type == "register":
            return await self.register_collaborator(websocket, data)
            
        elif message_type == "chat":
            await self.handle_chat_message(websocket, data)
            
        elif message_type == "task_update":
            await self.handle_task_update(websocket, data)
            
        elif message_type == "file_change":
            await self.handle_file_change(websocket, data)
            
        elif message_type == "heartbeat":
            await self.handle_heartbeat(websocket, data)
            
        elif message_type == "status_update":
            await self.handle_status_update(websocket, data)
    
    async def handle_chat_message(self, websocket, data: Dict[str, Any]):
        """Handle chat message between collaborators."""
        from_id = data.get("from_id")
        content = data.get("content", "")
        
        if from_id not in self.collaborators:
            return
        
        collaborator = self.collaborators[from_id]
        
        message = Message(
            id=str(uuid.uuid4()),
            from_id=from_id,
            from_role=collaborator.role,
            timestamp=time.time(),
            message_type="chat",
            content=content,
            metadata=data.get("metadata", {})
        )
        
        self.messages.append(message)
        
        # Broadcast to all collaborators
        await self.broadcast({
            "type": "new_message",
            "message": asdict(message),
            "from_name": collaborator.name
        })
    
    async def handle_task_update(self, websocket, data: Dict[str, Any]):
        """Handle task status updates."""
        task_data = data.get("task", {})
        task_id = task_data.get("id")
        
        if not task_id:
            task_id = str(uuid.uuid4())
            task_data["id"] = task_id
        
        task = TaskInfo(
            id=task_id,
            title=task_data.get("title", "Untitled Task"),
            assigned_to=task_data.get("assigned_to", ""),
            status=task_data.get("status", "planned"),
            created_at=task_data.get("created_at", time.time()),
            updated_at=time.time(),
            files_involved=task_data.get("files_involved", []),
            dependencies=task_data.get("dependencies", [])
        )
        
        self.tasks[task_id] = task
        
        # Broadcast task update
        await self.broadcast({
            "type": "task_updated",
            "task": asdict(task)
        })
    
    async def handle_file_change(self, websocket, data: Dict[str, Any]):
        """Handle file change notifications."""
        from_id = data.get("from_id")
        file_path = data.get("file_path")
        change_type = data.get("change_type")  # "created", "modified", "deleted"
        
        if from_id not in self.collaborators:
            return
        
        collaborator = self.collaborators[from_id]
        
        # Broadcast file change
        await self.broadcast({
            "type": "file_changed",
            "file_path": file_path,
            "change_type": change_type,
            "changed_by": collaborator.name,
            "changed_by_role": collaborator.role,
            "timestamp": time.time()
        }, exclude=websocket)
    
    async def handle_heartbeat(self, websocket, data: Dict[str, Any]):
        """Handle heartbeat to keep collaborator alive."""
        from_id = data.get("from_id")
        
        if from_id in self.collaborators:
            self.collaborators[from_id].last_seen = time.time()
    
    async def handle_status_update(self, websocket, data: Dict[str, Any]):
        """Handle collaborator status updates."""
        from_id = data.get("from_id")
        status = data.get("status")
        current_task = data.get("current_task")
        
        if from_id in self.collaborators:
            collaborator = self.collaborators[from_id]
            collaborator.status = status
            collaborator.current_task = current_task
            collaborator.last_seen = time.time()
            
            # Broadcast status update
            await self.broadcast({
                "type": "status_updated",
                "collaborator_id": from_id,
                "status": status,
                "current_task": current_task,
                "name": collaborator.name
            })
    
    async def broadcast(self, message: Dict[str, Any], exclude: Optional[websockets.WebSocketServerProtocol] = None):
        """Broadcast message to all connected clients."""
        if not self.connected_clients:
            return
        
        message_str = json.dumps(message)
        disconnected = set()
        
        for client in self.connected_clients:
            if client == exclude:
                continue
                
            try:
                await client.send(message_str)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
        
        # Clean up disconnected clients
        self.connected_clients -= disconnected
    
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connection."""
        collaborator_id = None
        try:
            # Send welcome message
            await websocket.send(json.dumps({
                "type": "welcome",
                "message": "Connected to AIOSv3 Collaboration Server",
                "server_time": time.time()
            }))
            
            # Process incoming messages
            async for message_str in websocket:
                try:
                    data = json.loads(message_str)
                    
                    # Track collaborator ID for cleanup
                    if data.get("type") == "register" and not collaborator_id:
                        collaborator_id = await self.handle_message(websocket, data)
                    else:
                        await self.handle_message(websocket, data)
                        
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "type": "error", 
                        "message": "Invalid JSON"
                    }))
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": f"Message processing error: {str(e)}"
                    }))
        
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Unexpected error in handle_client: {e}")
        finally:
            # Clean up when client disconnects
            self.connected_clients.discard(websocket)
            
            # Remove collaborator if they were registered
            if collaborator_id and collaborator_id in self.collaborators:
                collab = self.collaborators.pop(collaborator_id)
                await self.broadcast({
                    "type": "collaborator_left",
                    "collaborator_id": collaborator_id,
                    "message": f"{collab.name} ({collab.role}) left the collaboration"
                })
                logger.info(f"Cleaned up collaborator: {collab.name}")
    
    async def cleanup_stale_collaborators(self):
        """Remove collaborators that haven't been seen recently."""
        while True:
            await asyncio.sleep(30)  # Check every 30 seconds
            
            current_time = time.time()
            stale_threshold = 120  # 2 minutes
            
            to_remove = []
            for collab_id, collab in self.collaborators.items():
                if current_time - collab.last_seen > stale_threshold:
                    to_remove.append(collab_id)
            
            for collab_id in to_remove:
                collab = self.collaborators.pop(collab_id)
                await self.broadcast({
                    "type": "collaborator_left",
                    "collaborator_id": collab_id,
                    "message": f"{collab.name} ({collab.role}) left the collaboration"
                })
                logger.info(f"Removed stale collaborator: {collab.name}")
    
    async def start_server(self):
        """Start the collaboration server."""
        logger.info(f"Starting collaboration server on port {self.port}")
        
        # Start cleanup task
        cleanup_task = asyncio.create_task(self.cleanup_stale_collaborators())
        
        # Start WebSocket server
        server = await websockets.serve(
            lambda websocket, path: self.handle_client(websocket, path),
            "localhost", 
            self.port
        )
        
        logger.info(f"Collaboration server running at ws://localhost:{self.port}")
        logger.info("Multiple Claude Code instances can now connect and collaborate!")
        
        await server.wait_closed()


async def main():
    """Run the collaboration server."""
    server = CollaborationServer()
    await server.start_server()


if __name__ == "__main__":
    asyncio.run(main())