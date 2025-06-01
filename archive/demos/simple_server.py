#!/usr/bin/env python3
"""
Simple Collaboration Server

A working WebSocket server for multi-terminal collaboration.
"""

import asyncio
import json
import logging
import time
import websockets
from typing import Dict, Set

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleCollaborationServer:
    """Simple WebSocket server for agent collaboration."""
    
    def __init__(self):
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.agents: Dict[str, Dict] = {}
        
    async def register_client(self, websocket, data):
        """Register a new client/agent."""
        agent_id = data.get("id", f"agent_{len(self.agents)}")
        agent_info = {
            "id": agent_id,
            "name": data.get("name", "Unknown"),
            "role": data.get("role", "unknown"),
            "websocket": websocket
        }
        
        self.agents[agent_id] = agent_info
        self.clients.add(websocket)
        
        logger.info(f"✅ {agent_info['name']} ({agent_info['role']}) joined")
        
        # Send welcome
        await websocket.send(json.dumps({
            "type": "welcome",
            "message": f"Welcome {agent_info['name']}! Team size: {len(self.agents)}"
        }))
        
        # Notify others
        await self.broadcast({
            "type": "agent_joined",
            "agent": agent_info['name'],
            "role": agent_info['role'],
            "team_size": len(self.agents)
        }, exclude=websocket)
        
        return agent_id
    
    async def handle_message(self, websocket, data):
        """Handle incoming message."""
        msg_type = data.get("type")
        
        if msg_type == "register":
            return await self.register_client(websocket, data)
            
        elif msg_type == "chat":
            await self.handle_chat(websocket, data)
            
        elif msg_type == "task":
            await self.handle_task(websocket, data)
    
    async def handle_chat(self, websocket, data):
        """Handle chat message."""
        # Find sender
        sender = None
        for agent in self.agents.values():
            if agent["websocket"] == websocket:
                sender = agent
                break
        
        if sender:
            logger.info(f"💬 {sender['name']}: {data.get('content', '')}")
            
            # Broadcast to all
            await self.broadcast({
                "type": "chat_message",
                "from": sender['name'],
                "role": sender['role'],
                "content": data.get('content', ''),
                "timestamp": time.time()
            })
    
    async def handle_task(self, websocket, data):
        """Handle task creation."""
        # Find sender
        sender = None
        for agent in self.agents.values():
            if agent["websocket"] == websocket:
                sender = agent
                break
        
        if sender:
            task_title = data.get('title', 'Untitled Task')
            logger.info(f"📋 {sender['name']} created: {task_title}")
            
            # Broadcast task
            await self.broadcast({
                "type": "task_created",
                "from": sender['name'],
                "title": task_title,
                "description": data.get('description', ''),
                "timestamp": time.time()
            })
    
    async def broadcast(self, message, exclude=None):
        """Broadcast message to all clients."""
        if not self.clients:
            return
        
        message_str = json.dumps(message)
        disconnected = set()
        
        for client in self.clients:
            if client == exclude:
                continue
            try:
                await client.send(message_str)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
        
        # Clean up disconnected clients
        for client in disconnected:
            self.clients.discard(client)
            # Remove from agents
            to_remove = []
            for agent_id, agent in self.agents.items():
                if agent["websocket"] == client:
                    to_remove.append(agent_id)
            for agent_id in to_remove:
                agent = self.agents.pop(agent_id)
                logger.info(f"👋 {agent['name']} left")
    
    async def handle_client(self, websocket, path):
        """Handle client connection."""
        try:
            # Send initial welcome
            await websocket.send(json.dumps({
                "type": "welcome",
                "message": "Connected to collaboration server"
            }))
            
            async for message_str in websocket:
                try:
                    data = json.loads(message_str)
                    await self.handle_message(websocket, data)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    try:
                        await websocket.send(json.dumps({"type": "error", "message": "Invalid JSON"}))
                    except:
                        pass
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    try:
                        await websocket.send(json.dumps({"type": "error", "message": str(e)}))
                    except:
                        pass
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self.clients.discard(websocket)
            # Clean up agent if registered
            to_remove = []
            for agent_id, agent in self.agents.items():
                if agent.get("websocket") == websocket:
                    to_remove.append(agent_id)
            for agent_id in to_remove:
                agent = self.agents.pop(agent_id)
                logger.info(f"👋 {agent['name']} left (cleanup)")

async def main():
    """Run the server."""
    server = SimpleCollaborationServer()
    
    print("🚀 Starting Simple Collaboration Server on port 8765...")
    
    websocket_server = await websockets.serve(server.handle_client, "localhost", 8765)
    
    print("✅ Server running at ws://localhost:8765")
    print("💡 Multiple terminals can now connect!")
    
    await websocket_server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())