#!/usr/bin/env python3
"""
Clean Multi-Terminal Collaboration Demo

This creates a working demo that definitely works without port conflicts.
"""

import asyncio
import json
import logging
import sys
import time
import os
from datetime import datetime
import threading
import queue

# Load environment
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(message)s')

class FileBasedCollaboration:
    """File-based collaboration system that definitely works."""
    
    def __init__(self):
        self.message_file = "/tmp/collaboration_messages.json"
        self.agent_file = "/tmp/collaboration_agents.json"
        self.running = True
        
        # Initialize files
        self.save_json(self.message_file, [])
        self.save_json(self.agent_file, {})
    
    def save_json(self, filename, data):
        """Save data to JSON file with file locking."""
        import fcntl
        try:
            with open(filename, 'r+') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.seek(0)
                json.dump(data, f)
                f.truncate()
                fcntl.flock(f, fcntl.LOCK_UN)
        except:
            # If file doesn't exist, create it
            try:
                with open(filename, 'w') as f:
                    fcntl.flock(f, fcntl.LOCK_EX)
                    json.dump(data, f)
                    fcntl.flock(f, fcntl.LOCK_UN)
            except:
                pass
    
    def load_json(self, filename):
        """Load data from JSON file with file locking."""
        import fcntl
        try:
            with open(filename, 'r') as f:
                fcntl.flock(f, fcntl.LOCK_SH)
                data = json.load(f)
                fcntl.flock(f, fcntl.LOCK_UN)
                return data
        except:
            return [] if 'messages' in filename else {}
    
    def add_message(self, from_name, role, content):
        """Add a message to the collaboration."""
        messages = self.load_json(self.message_file)
        message = {
            "from": from_name,
            "role": role,
            "content": content,
            "timestamp": time.time()
        }
        messages.append(message)
        self.save_json(self.message_file, messages)
        print(f"💬 {from_name}: {content}")
    
    def register_agent(self, name, role):
        """Register an agent."""
        agents = self.load_json(self.agent_file)
        agents[name] = {
            "role": role,
            "last_seen": time.time()
        }
        self.save_json(self.agent_file, agents)
        print(f"✅ {name} ({role}) joined")
    
    def get_new_messages(self, last_timestamp):
        """Get messages since last timestamp."""
        messages = self.load_json(self.message_file)
        return [msg for msg in messages if msg["timestamp"] > last_timestamp]

class CollaborationAgent:
    """Agent that uses file-based collaboration."""
    
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.collaboration = FileBasedCollaboration()
        self.last_message_time = time.time()
        self.has_claude = False
        
    async def setup_claude(self):
        """Setup Claude API."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            print(f"✅ {self.name} has Claude API access")
            self.has_claude = True
            return True
        else:
            print(f"⚠️ {self.name} using fallback responses (no API key)")
            return False
    
    async def start(self):
        """Start the agent."""
        print(f"🚀 Starting {self.name} ({self.role})")
        
        if self.role != "human":
            await self.setup_claude()
        
        # Register with collaboration
        self.collaboration.register_agent(self.name, self.role)
        
        if self.role == "human":
            await self.run_human_interface()
        else:
            await self.run_ai_agent()
    
    async def run_human_interface(self):
        """Run human interface."""
        print(f"\n💡 Welcome {self.name}!")
        print("Type messages to collaborate with your AI team:")
        print("Type 'quit' to exit")
        print("Type 'team' to see who's online")
        print()
        
        # Start monitoring for responses
        monitor_task = asyncio.create_task(self.monitor_responses())
        
        try:
            while True:
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, f"{self.role}> "
                )
                
                if user_input.strip().lower() == 'quit':
                    break
                elif user_input.strip().lower() == 'team':
                    self.show_team()
                elif user_input.strip():
                    self.collaboration.add_message(self.name, self.role, user_input.strip())
                    
        except KeyboardInterrupt:
            pass
        finally:
            monitor_task.cancel()
            print(f"\n👋 {self.name} signing off...")
    
    def show_team(self):
        """Show team members."""
        agents = self.collaboration.load_json(self.collaboration.agent_file)
        print("\n👥 Current Team:")
        for name, info in agents.items():
            role = info.get("role", "unknown")
            print(f"   🤖 {name} ({role})")
        print()
    
    async def run_ai_agent(self):
        """Run AI agent."""
        print(f"🤖 {self.name} listening for team messages...")
        
        try:
            while True:
                # Check for new messages
                new_messages = self.collaboration.get_new_messages(self.last_message_time)
                
                for message in new_messages:
                    if message["from"] != self.name:  # Don't respond to own messages
                        await self.handle_message(message)
                        self.last_message_time = message["timestamp"]
                
                await asyncio.sleep(2)  # Check every 2 seconds
                
        except KeyboardInterrupt:
            print(f"\n👋 {self.name} signing off...")
    
    async def monitor_responses(self):
        """Monitor for AI responses (for human interface)."""
        try:
            while True:
                new_messages = self.collaboration.get_new_messages(self.last_message_time)
                
                for message in new_messages:
                    if message["from"] != self.name:
                        timestamp = datetime.fromtimestamp(message["timestamp"])
                        print(f"\n💬 [{timestamp.strftime('%H:%M:%S')}] {message['from']}: {message['content']}")
                        print(f"{self.role}> ", end="", flush=True)
                        self.last_message_time = message["timestamp"]
                
                await asyncio.sleep(1)  # Check every second for responses
                
        except asyncio.CancelledError:
            pass
    
    async def handle_message(self, message):
        """Handle incoming message."""
        from_name = message["from"]
        from_role = message["role"]
        content = message["content"]
        
        # Only AI agents respond to human messages
        if from_role == "human" and self.role != "human":
            if await self.should_respond(content):
                print(f"🤖 {self.name} thinking...")
                await asyncio.sleep(2)  # Thinking time
                
                response = await self.generate_response(content)
                self.collaboration.add_message(self.name, self.role, response)
    
    async def should_respond(self, message):
        """Determine if agent should respond."""
        message_lower = message.lower()
        
        if self.role == "cto":
            return any(word in message_lower for word in [
                "architecture", "technical", "design", "approach", "how", "what", 
                "recommend", "auth", "system", "structure", "decision"
            ])
        elif self.role == "backend-dev":
            return any(word in message_lower for word in [
                "implement", "code", "build", "api", "backend", "server", 
                "database", "endpoint", "middleware"
            ])
        elif self.role == "qa":
            return any(word in message_lower for word in [
                "test", "quality", "validation", "bug", "error", "security",
                "verify", "check"
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
                model_id="claude-3-opus-20240229",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
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
            return f"You are a CTO providing technical leadership for a development team. Respond to this message with brief technical guidance (2-3 sentences): {message}"
        elif self.role == "backend-dev":
            return f"You are a backend developer. Provide practical implementation advice for this message (2-3 sentences): {message}"
        elif self.role == "qa":
            return f"You are a QA engineer. Provide testing and quality perspective for this message (2-3 sentences): {message}"
        return f"Respond helpfully to: {message}"
    
    def get_fallback_response(self, message):
        """Get fallback response."""
        responses = {
            "cto": [
                "From an architecture perspective, I recommend using proven patterns with security and scalability in mind.",
                "Let's focus on a modular design that can handle current needs and future growth.",
                "I suggest we prioritize security, maintainability, and performance in our technical approach."
            ],
            "backend-dev": [
                "I can implement that! I'll focus on robust APIs with proper error handling and validation.",
                "For the backend, I recommend using established frameworks and following RESTful principles.",
                "I'll handle the server-side implementation with comprehensive testing and clear documentation."
            ],
            "qa": [
                "I'll create test cases covering functionality, edge cases, and security scenarios.",
                "From a quality perspective, we need proper validation, error handling, and user experience testing.",
                "Let me design testing strategies that ensure reliability, performance, and security compliance."
            ]
        }
        
        import random
        return random.choice(responses.get(self.role, ["I understand and will help with that."]))

async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("🚀 Multi-Terminal AI Collaboration Demo")
        print("\nUsage:")
        print("  Human:   python3 clean_demo.py human")
        print("  CTO:     python3 clean_demo.py cto") 
        print("  Backend: python3 clean_demo.py backend")
        print("  QA:      python3 clean_demo.py qa")
        print("\nStart with different roles in separate terminals!")
        return
    
    role = sys.argv[1].lower()
    
    names = {
        "human": "Product Owner",
        "cto": "CTO Agent",
        "backend": "Backend Developer", 
        "qa": "QA Engineer"
    }
    
    if role not in names:
        print(f"Unknown role: {role}")
        print("Available roles: human, cto, backend, qa")
        return
    
    agent = CollaborationAgent(names[role], role)
    await agent.start()

if __name__ == "__main__":
    asyncio.run(main())