#!/usr/bin/env python3
"""
Working Collaboration Demo

This creates a fully working multi-terminal collaboration demo
using a simple but reliable approach.
"""

import asyncio
import json
import logging
import sys
import time
import os
from datetime import datetime
import websockets
from typing import Dict, Set

# Load environment
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(message)s')

class WorkingServer:
    """Ultra-simple but working collaboration server."""
    
    def __init__(self):
        self.connections = {}  # websocket -> agent_info
        
    async def handle_connection(self, websocket, path):
        """Handle a client connection."""
        agent_info = None
        try:
            print(f"🔗 New connection from {websocket.remote_address}")
            
            # Wait for registration
            async for message in websocket:
                data = json.loads(message)
                
                if data.get("type") == "register":
                    agent_info = {
                        "name": data.get("name", "Unknown"),
                        "role": data.get("role", "unknown"),
                        "websocket": websocket
                    }
                    self.connections[websocket] = agent_info
                    
                    print(f"✅ {agent_info['name']} ({agent_info['role']}) joined")
                    
                    # Notify others
                    await self.broadcast({
                        "type": "agent_joined",
                        "name": agent_info['name'],
                        "role": agent_info['role']
                    }, exclude=websocket)
                    
                elif data.get("type") == "chat":
                    if websocket in self.connections:
                        sender = self.connections[websocket]
                        print(f"💬 {sender['name']}: {data.get('content', '')}")
                        
                        await self.broadcast({
                            "type": "message",
                            "from": sender['name'],
                            "role": sender['role'],
                            "content": data.get('content', ''),
                            "timestamp": time.time()
                        })
                        
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            print(f"❌ Connection error: {e}")
        finally:
            if websocket in self.connections:
                agent = self.connections.pop(websocket)
                print(f"👋 {agent['name']} left")
    
    async def broadcast(self, message, exclude=None):
        """Broadcast to all connections."""
        message_str = json.dumps(message)
        for ws, agent in list(self.connections.items()):
            if ws == exclude:
                continue
            try:
                await ws.send(message_str)
            except:
                # Remove dead connections
                if ws in self.connections:
                    self.connections.pop(ws)

class WorkingAgent:
    """Simple but working agent."""
    
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.websocket = None
        self.connected = False
        self.has_claude = False
        
    async def setup_claude(self):
        """Setup Claude API."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            print(f"✅ {self.name} has Claude API access")
            self.has_claude = True
        else:
            print(f"⚠️ {self.name} using fallback responses (no API key)")
            
    async def connect_and_run(self):
        """Connect to server and run."""
        try:
            print(f"🔗 {self.name} connecting...")
            self.websocket = await websockets.connect("ws://localhost:8766")
            self.connected = True
            
            # Register
            await self.websocket.send(json.dumps({
                "type": "register",
                "name": self.name,
                "role": self.role
            }))
            
            print(f"✅ {self.name} connected and registered")
            
            if self.role == "human":
                await self.run_human_interface()
            else:
                await self.run_ai_agent()
                
        except Exception as e:
            print(f"❌ {self.name} failed: {e}")
    
    async def run_human_interface(self):
        """Run human interface."""
        print(f"\n💡 {self.name} - Type messages to your AI team:")
        print("Format: <message> (then press Enter)")
        print("Type 'quit' to exit\n")
        
        # Start listening for responses
        listen_task = asyncio.create_task(self.listen_for_responses())
        
        try:
            while self.connected:
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, f"{self.role}> "
                )
                
                if user_input.strip().lower() == 'quit':
                    break
                    
                if user_input.strip():
                    await self.websocket.send(json.dumps({
                        "type": "chat",
                        "content": user_input.strip()
                    }))
                    
        except KeyboardInterrupt:
            pass
        finally:
            listen_task.cancel()
            
    async def run_ai_agent(self):
        """Run AI agent - listen and respond."""
        print(f"🤖 {self.name} listening for team messages...")
        await self.listen_for_responses()
    
    async def listen_for_responses(self):
        """Listen for messages from team."""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                if data.get("type") == "agent_joined":
                    name = data.get("name")
                    role = data.get("role")
                    if name != self.name:
                        print(f"👋 {name} ({role}) joined the team!")
                
                elif data.get("type") == "message":
                    from_name = data.get("from")
                    from_role = data.get("role")
                    content = data.get("content")
                    timestamp = datetime.fromtimestamp(data.get("timestamp", 0))
                    
                    if from_name != self.name:
                        print(f"💬 [{timestamp.strftime('%H:%M:%S')}] {from_name}: {content}")
                        
                        # AI agents respond to human messages
                        if from_role == "human" and self.role != "human":
                            if await self.should_respond(content):
                                await asyncio.sleep(2)  # Think time
                                response = await self.generate_response(content)
                                print(f"🤖 {self.name} responding...")
                                
                                await self.websocket.send(json.dumps({
                                    "type": "chat",
                                    "content": response
                                }))
                                
        except websockets.exceptions.ConnectionClosed:
            self.connected = False
        except Exception as e:
            print(f"❌ {self.name} listen error: {e}")
    
    async def should_respond(self, message):
        """Determine if agent should respond."""
        message_lower = message.lower()
        
        if self.role == "cto":
            return any(word in message_lower for word in [
                "architecture", "technical", "design", "approach", "how", "what", "recommend", "auth"
            ])
        elif self.role == "backend-dev":
            return any(word in message_lower for word in [
                "implement", "code", "build", "api", "backend", "server", "database"
            ])
        elif self.role == "qa":
            return any(word in message_lower for word in [
                "test", "quality", "validation", "bug", "error", "security"
            ])
        
        return False
    
    async def generate_response(self, message):
        """Generate response to message."""
        if self.has_claude:
            return await self.get_claude_response(message)
        else:
            return self.get_fallback_response(message)
    
    async def get_claude_response(self, message):
        """Get real Claude API response."""
        try:
            # Import here to avoid startup issues
            from core.routing.router import LLMRouter, RoutingPolicy, RoutingStrategy
            from core.routing.providers.claude import ClaudeProvider, ClaudeConfig
            from core.routing.providers.base import LLMRequest
            
            # Create router
            policy = RoutingPolicy(strategy=RoutingStrategy.COST_OPTIMIZED)
            router = LLMRouter(default_policy=policy)
            
            # Setup Claude
            claude_config = ClaudeConfig(
                provider_name="claude",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                timeout=30.0
            )
            claude_provider = ClaudeProvider(claude_config)
            router.register_provider("claude", claude_provider)
            await router.initialize()
            
            # Create role-specific prompt
            prompt = self.create_role_prompt(message)
            
            request = LLMRequest(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            response = await router.route_request(request)
            return response.content
            
        except Exception as e:
            print(f"❌ Claude API error: {e}")
            return self.get_fallback_response(message)
    
    def create_role_prompt(self, message):
        """Create role-specific prompt."""
        if self.role == "cto":
            return f"You are a CTO providing technical leadership. The team is discussing: {message}. Provide brief technical guidance (2-3 sentences max)."
        elif self.role == "backend-dev":
            return f"You are a backend developer. The team is discussing: {message}. Provide practical implementation advice (2-3 sentences max)."
        elif self.role == "qa":
            return f"You are a QA engineer. The team is discussing: {message}. Provide testing and quality perspective (2-3 sentences max)."
        return f"Respond to: {message}"
    
    def get_fallback_response(self, message):
        """Get fallback response."""
        responses = {
            "cto": [
                "From an architecture perspective, I recommend we use proven patterns and ensure scalability.",
                "Let's focus on security and maintainability in our technical approach.",
                "I suggest we break this down into manageable components with clear interfaces."
            ],
            "backend-dev": [
                "I can implement that! I'll focus on robust error handling and clean APIs.",
                "For the backend, I recommend using established libraries and following RESTful principles.", 
                "I'll handle the server-side implementation with proper testing and documentation."
            ],
            "qa": [
                "I'll create comprehensive test cases including edge cases and error scenarios.",
                "From a quality perspective, we need to ensure proper validation and user experience testing.",
                "Let me design testing strategies that cover functionality, performance, and security."
            ]
        }
        
        import random
        return random.choice(responses.get(self.role, ["I understand and will help with that."]))

async def run_server():
    """Run the collaboration server."""
    server = WorkingServer()
    print("🚀 Starting collaboration server on port 8766...")
    
    websocket_server = await websockets.serve(server.handle_connection, "localhost", 8766)
    print("✅ Server running! Connect agents now...")
    
    await websocket_server.wait_closed()

async def run_agent(role, name):
    """Run an agent."""
    agent = WorkingAgent(name, role)
    
    if role != "human":
        await agent.setup_claude()
    
    await agent.connect_and_run()

async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Server:  python3 working_demo.py server")
        print("  Human:   python3 working_demo.py human")
        print("  CTO:     python3 working_demo.py cto")
        print("  Backend: python3 working_demo.py backend")
        print("  QA:      python3 working_demo.py qa")
        return
    
    mode = sys.argv[1].lower()
    
    if mode == "server":
        await run_server()
    elif mode == "human":
        await run_agent("human", "Product Owner")
    elif mode == "cto":
        await run_agent("cto", "CTO Agent")
    elif mode in ["backend", "backend-dev"]:
        await run_agent("backend-dev", "Backend Developer")
    elif mode == "qa":
        await run_agent("qa", "QA Engineer")
    else:
        print(f"Unknown mode: {mode}")

if __name__ == "__main__":
    asyncio.run(main())