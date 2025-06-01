#!/usr/bin/env python3
"""
Simple Agent Client

A working agent client for multi-terminal collaboration demo.
"""

import asyncio
import json
import logging
import sys
import time
import os
import argparse
from datetime import datetime
import websockets

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Import Claude API
from core.routing.router import LLMRouter, RoutingPolicy, RoutingStrategy
from core.routing.providers.claude import ClaudeProvider, ClaudeConfig

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class SimpleAgent:
    """Simple agent for real collaboration demo."""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.websocket = None
        self.connected = False
        self.llm_router = None
        
    async def setup_claude(self):
        """Setup Claude API integration."""
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print(f"⚠️ No ANTHROPIC_API_KEY - {self.name} will use simple responses")
                return False
                
            policy = RoutingPolicy(
                strategy=RoutingStrategy.COST_OPTIMIZED,
                max_cost_per_request=0.25
            )
            
            self.llm_router = LLMRouter(default_policy=policy)
            
            claude_config = ClaudeConfig(
                provider_name="claude",
                api_key=api_key,
                timeout=30.0,
                max_retries=2
            )
            
            claude_provider = ClaudeProvider(claude_config)
            self.llm_router.register_provider("claude", claude_provider)
            await self.llm_router.initialize()
            
            print(f"✅ {self.name} connected to Claude API")
            return True
            
        except Exception as e:
            print(f"❌ {self.name} Claude setup failed: {e}")
            return False
    
    async def connect(self):
        """Connect to collaboration server."""
        try:
            print(f"🔗 {self.name} connecting to server...")
            self.websocket = await websockets.connect("ws://localhost:8765")
            self.connected = True
            
            # Wait for welcome message
            welcome_msg = await self.websocket.recv()
            welcome_data = json.loads(welcome_msg)
            print(f"📡 {welcome_data.get('message', 'Connected')}")
            
            # Register with server
            await self.websocket.send(json.dumps({
                "type": "register",
                "id": f"{self.role}_{int(time.time())}",
                "name": self.name,
                "role": self.role
            }))
            
            print(f"✅ {self.name} connected!")
            return True
            
        except Exception as e:
            print(f"❌ {self.name} connection failed: {e}")
            self.connected = False
            return False
    
    async def send_chat(self, message: str):
        """Send chat message."""
        if self.websocket and self.connected:
            await self.websocket.send(json.dumps({
                "type": "chat",
                "content": message
            }))
    
    async def send_task(self, title: str, description: str = ""):
        """Send task creation."""
        if self.websocket and self.connected:
            await self.websocket.send(json.dumps({
                "type": "task",
                "title": title,
                "description": description
            }))
    
    async def generate_response(self, prompt: str) -> str:
        """Generate AI response using Claude."""
        if not self.llm_router:
            # Fallback responses for demo
            return self._get_fallback_response(prompt)
        
        try:
            from core.routing.providers.base import LLMRequest
            
            request = LLMRequest(
                messages=[{"role": "user", "content": self._create_role_prompt(prompt)}],
                max_tokens=500,
                temperature=0.7
            )
            
            response = await self.llm_router.route_request(request)
            return response.content
            
        except Exception as e:
            print(f"❌ {self.name} AI response failed: {e}")
            return self._get_fallback_response(prompt)
    
    def _create_role_prompt(self, user_message: str) -> str:
        """Create role-specific prompt."""
        role_context = {
            "cto": f"You are a CTO (Chief Technology Officer) for a software development team. Provide technical leadership, architecture guidance, and strategic technology decisions. User message: {user_message}",
            "backend-dev": f"You are a Senior Backend Developer. Provide practical implementation guidance, code suggestions, and technical solutions for server-side development. User message: {user_message}",
            "qa": f"You are a QA Engineer. Focus on testing strategies, quality assurance, validation approaches, and quality metrics. User message: {user_message}",
            "human": f"You are a Product Owner. Focus on requirements, priorities, and business decisions. User message: {user_message}"
        }
        
        return role_context.get(self.role, f"You are a {self.role}. Respond helpfully to: {user_message}")
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Get fallback response when Claude API unavailable."""
        fallback_responses = {
            "cto": [
                "I recommend we focus on scalable architecture. Let me design a solution that handles our current needs and future growth.",
                "From a technical leadership perspective, we should consider security, performance, and maintainability in our approach.",
                "Let's break this down into manageable technical components and ensure we're following best practices."
            ],
            "backend-dev": [
                "I can implement that! Let me suggest a robust server-side solution with proper error handling and testing.",
                "For the backend implementation, I'd recommend using proven patterns and ensuring good API design.",
                "I'll handle the implementation details. Should take about 4-6 hours depending on complexity."
            ],
            "qa": [
                "I'll create comprehensive test cases for this feature, including edge cases and error scenarios.",
                "From a quality perspective, we need to ensure proper validation, error handling, and user experience testing.",
                "Let me design a testing strategy that covers functionality, performance, and security aspects."
            ]
        }
        
        import random
        responses = fallback_responses.get(self.role, ["I understand. Let me help with that."])
        return random.choice(responses)
    
    async def listen_for_messages(self):
        """Listen for messages from other agents."""
        try:
            while self.connected and self.websocket:
                try:
                    message_str = await self.websocket.recv()
                    data = json.loads(message_str)
                    await self.handle_server_message(data)
                except json.JSONDecodeError as e:
                    print(f"❌ {self.name} received invalid JSON: {e}")
                except websockets.exceptions.ConnectionClosed:
                    self.connected = False
                    print(f"🔌 {self.name} disconnected")
                    break
        except Exception as e:
            self.connected = False
            print(f"❌ {self.name} listen error: {e}")
    
    async def handle_server_message(self, data):
        """Handle messages from server."""
        msg_type = data.get("type")
        
        if msg_type == "welcome":
            print(f"📡 {data.get('message')}")
            
        elif msg_type == "agent_joined":
            agent_name = data.get("agent")
            role = data.get("role")
            if agent_name != self.name:  # Don't announce self
                print(f"👋 {agent_name} ({role}) joined the team!")
        
        elif msg_type == "chat_message":
            from_agent = data.get("from")
            role = data.get("role") 
            content = data.get("content")
            timestamp = datetime.fromtimestamp(data.get("timestamp", 0))
            
            if from_agent != self.name:  # Don't echo own messages
                print(f"💬 [{timestamp.strftime('%H:%M:%S')}] {from_agent}: {content}")
                
                # Auto-respond if this is relevant to our role
                if await self._should_respond(content, role):
                    await asyncio.sleep(2)  # Think time
                    response = await self.generate_response(content)
                    print(f"🤖 {self.name} responding...")
                    await self.send_chat(response)
        
        elif msg_type == "task_created":
            from_agent = data.get("from")
            title = data.get("title")
            timestamp = datetime.fromtimestamp(data.get("timestamp", 0))
            
            if from_agent != self.name:
                print(f"📋 [{timestamp.strftime('%H:%M:%S')}] Task created by {from_agent}: {title}")
    
    async def _should_respond(self, message: str, from_role: str) -> bool:
        """Determine if agent should respond to a message."""
        message_lower = message.lower()
        
        # Don't respond to other AI agents immediately to avoid loops
        if from_role in ["cto", "backend-dev", "qa"] and self.role in ["cto", "backend-dev", "qa"]:
            return False
        
        # Respond to human messages
        if from_role == "human":
            # CTO responds to architecture/technical questions
            if self.role == "cto" and any(word in message_lower for word in ["architecture", "technical", "design", "approach", "how", "what", "recommend"]):
                return True
            # Backend dev responds to implementation questions  
            elif self.role == "backend-dev" and any(word in message_lower for word in ["implement", "code", "build", "api", "backend", "server"]):
                return True
            # QA responds to testing/quality questions
            elif self.role == "qa" and any(word in message_lower for word in ["test", "quality", "validation", "bug", "error"]):
                return True
        
        return False
    
    async def run_interactive_mode(self):
        """Run interactive mode for human users."""
        print(f"\n💡 Interactive mode for {self.name}")
        print("Commands:")
        print("  chat <message>  - Send message to team") 
        print("  task <title>    - Create task")
        print("  quit           - Exit")
        print()
        
        try:
            while self.connected:
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, f"{self.role}> "
                )
                
                if not user_input.strip():
                    continue
                
                parts = user_input.strip().split(" ", 1)
                command = parts[0].lower()
                
                if command == "quit":
                    break
                elif command == "chat" and len(parts) > 1:
                    await self.send_chat(parts[1])
                elif command == "task" and len(parts) > 1:
                    await self.send_task(parts[1])
                else:
                    print("Use: chat <message> or task <title>")
        
        except KeyboardInterrupt:
            pass
        
        print(f"\n👋 {self.name} signing off...")
        if self.websocket:
            await self.websocket.close()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Simple Agent for Collaboration Demo")
    parser.add_argument("--role", required=True, 
                       choices=["human", "cto", "backend-dev", "qa"],
                       help="Agent role")
    parser.add_argument("--name", help="Agent name")
    
    args = parser.parse_args()
    
    # Default names
    if not args.name:
        names = {
            "human": "Product Owner",
            "cto": "CTO Agent", 
            "backend-dev": "Backend Developer",
            "qa": "QA Engineer"
        }
        args.name = names[args.role]
    
    print(f"🚀 Starting {args.name} ({args.role})")
    
    agent = SimpleAgent(args.name, args.role)
    
    try:
        # Setup Claude API for AI agents
        if args.role != "human":
            await agent.setup_claude()
        
        # Connect to server
        if await agent.connect():
            # Start listening for messages
            listen_task = asyncio.create_task(agent.listen_for_messages())
            
            # Run interactive mode for humans, auto mode for AI
            if args.role == "human":
                await agent.run_interactive_mode()
            else:
                print(f"🤖 {args.name} listening for collaboration...")
                await listen_task
        
    except KeyboardInterrupt:
        print(f"\n👋 {args.name} interrupted")
    except Exception as e:
        print(f"❌ {args.name} error: {e}")


if __name__ == "__main__":
    asyncio.run(main())