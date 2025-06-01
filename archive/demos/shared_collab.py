#!/usr/bin/env python3
"""
Shared Memory Multi-Agent Collaboration

This uses a proper shared memory server that all agents connect to.
"""

import asyncio
import json
import time
import sys
import os
from datetime import datetime
import multiprocessing
from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager
import threading
import uuid
import socket

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Shared memory server port
SHARED_MEMORY_PORT = 5555

class CollaborationManager:
    """Manages shared collaboration data."""
    
    def __init__(self):
        self.agents = {}
        self.messages = []
        self.lock = threading.Lock()
    
    def register_agent(self, agent_id, name, role):
        """Register an agent."""
        with self.lock:
            self.agents[agent_id] = {
                'name': name,
                'role': role,
                'last_seen': time.time()
            }
            print(f"✅ {name} ({role}) joined the team!")
            return agent_id
    
    def add_message(self, from_name, role, content):
        """Add a message."""
        with self.lock:
            message = {
                'from': from_name,
                'role': role,
                'content': content,
                'timestamp': time.time()
            }
            self.messages.append(message)
        print(f"💬 {from_name}: {content}")
    
    def get_agents(self):
        """Get all agents."""
        with self.lock:
            return dict(self.agents)
    
    def get_messages_since(self, timestamp):
        """Get messages since timestamp."""
        with self.lock:
            return [m for m in self.messages if m['timestamp'] > timestamp]

def start_shared_memory_server():
    """Start the shared memory server."""
    # Register the CollaborationManager
    BaseManager.register('CollaborationManager', CollaborationManager)
    
    # Create manager
    manager = BaseManager(address=('localhost', SHARED_MEMORY_PORT), authkey=b'aios_collab')
    
    # Get server
    server = manager.get_server()
    
    print(f"🚀 Shared memory server starting on port {SHARED_MEMORY_PORT}...")
    server.serve_forever()

class CollaborationAgent:
    """Agent that uses shared memory collaboration."""
    
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.agent_id = f"{role}_{uuid.uuid4().hex[:8]}"
        self.collab = None
        self.last_msg_time = time.time()
        self.has_claude = False
        self.running = True
    
    def connect_to_shared_memory(self):
        """Connect to shared memory server."""
        try:
            # Register the CollaborationManager
            BaseManager.register('CollaborationManager')
            
            # Connect to server
            manager = BaseManager(address=('localhost', SHARED_MEMORY_PORT), authkey=b'aios_collab')
            manager.connect()
            
            # Get the shared collaboration manager
            self.collab = manager.CollaborationManager()
            print(f"✅ Connected to shared memory server")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to shared memory: {e}")
            return False
    
    async def start(self):
        """Start the agent."""
        print(f"🚀 Starting {self.name} ({self.role})")
        
        # Connect to shared memory
        if not self.connect_to_shared_memory():
            print("❌ Cannot start without shared memory connection")
            return
        
        # Setup Claude for AI agents
        if self.role != "human":
            await self.setup_claude()
        
        # Register with collaboration
        self.collab.register_agent(self.agent_id, self.name, self.role)
        
        if self.role == "human":
            await self.run_human()
        else:
            await self.run_ai_agent()
    
    async def setup_claude(self):
        """Setup Claude API."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            print(f"✅ {self.name} has Claude API access")
            self.has_claude = True
        else:
            print(f"⚠️ {self.name} using fallback responses")
    
    async def run_human(self):
        """Run human interface."""
        print(f"\n💡 Welcome {self.name}!")
        print("Commands: <message>, 'team', 'quit'")
        print()
        
        # Start message monitor
        monitor = asyncio.create_task(self.monitor_messages())
        
        try:
            while self.running:
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, f"{self.role}> "
                )
                
                if user_input.strip().lower() == 'quit':
                    break
                elif user_input.strip().lower() == 'team':
                    self.show_team()
                elif user_input.strip():
                    self.collab.add_message(self.name, self.role, user_input.strip())
        finally:
            monitor.cancel()
            print(f"👋 {self.name} signing off...")
    
    def show_team(self):
        """Show current team."""
        agents = self.collab.get_agents()
        print(f"\n👥 Current Team ({len(agents)} members):")
        for agent_id, info in agents.items():
            print(f"   🤖 {info['name']} ({info['role']})")
        print()
    
    async def run_ai_agent(self):
        """Run AI agent."""
        print(f"🤖 {self.name} listening for messages...")
        
        while self.running:
            try:
                # Check for new messages
                new_messages = self.collab.get_messages_since(self.last_msg_time)
                
                for msg in new_messages:
                    if msg['from'] != self.name:
                        await self.handle_message(msg)
                    self.last_msg_time = msg['timestamp']
                
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                break
        
        print(f"👋 {self.name} signing off...")
    
    async def monitor_messages(self):
        """Monitor messages for human."""
        while self.running:
            try:
                new_messages = self.collab.get_messages_since(self.last_msg_time)
                
                for msg in new_messages:
                    if msg['from'] != self.name:
                        timestamp = datetime.fromtimestamp(msg['timestamp'])
                        print(f"\n💬 [{timestamp.strftime('%H:%M:%S')}] {msg['from']}: {msg['content']}")
                        print(f"{self.role}> ", end="", flush=True)
                    self.last_msg_time = msg['timestamp']
                
                await asyncio.sleep(0.5)
            except:
                pass
    
    async def handle_message(self, msg):
        """Handle incoming message."""
        if msg['role'] == 'human' and await self.should_respond(msg['content']):
            print(f"🤖 {self.name} thinking...")
            await asyncio.sleep(2)
            
            response = await self.generate_response(msg['content'])
            self.collab.add_message(self.name, self.role, response)
    
    async def should_respond(self, message):
        """Check if should respond."""
        msg_lower = message.lower()
        
        keywords = {
            'cto': ['architecture', 'technical', 'design', 'system', 'approach', 'structure'],
            'backend': ['implement', 'code', 'api', 'backend', 'endpoint', 'database'],
            'qa': ['test', 'quality', 'validation', 'verify', 'security', 'bug']
        }
        
        return any(word in msg_lower for word in keywords.get(self.role, []))
    
    async def generate_response(self, message):
        """Generate response."""
        if self.has_claude:
            try:
                from core.routing.router import LLMRouter, RoutingPolicy, RoutingStrategy
                from core.routing.providers.claude import ClaudeProvider, ClaudeConfig
                from core.routing.providers.base import LLMRequest
                
                policy = RoutingPolicy(strategy=RoutingStrategy.COST_OPTIMIZED)
                router = LLMRouter(default_policy=policy)
                
                claude_config = ClaudeConfig(
                    provider_name="claude",
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )
                claude_provider = ClaudeProvider(claude_config)
                router.register_provider("claude", claude_provider)
                await router.initialize()
                
                role_prompts = {
                    'cto': f"As CTO, provide brief technical guidance for: {message}",
                    'backend': f"As backend developer, provide implementation advice for: {message}",
                    'qa': f"As QA engineer, provide testing perspective for: {message}"
                }
                
                request = LLMRequest(
                    model_id="claude-3-opus-20240229",
                    messages=[{"role": "user", "content": role_prompts.get(self.role, message)}],
                    max_tokens=150
                )
                
                response = await router.route_request(request)
                return response.content
            except:
                pass
        
        # Fallback responses
        fallbacks = {
            'cto': "From an architecture perspective, I recommend a modular, secure approach that scales well.",
            'backend': "I'll implement that with clean APIs, proper error handling, and comprehensive tests.",
            'qa': "I'll create test cases covering functionality, edge cases, and security scenarios."
        }
        return fallbacks.get(self.role, "I'll help with that.")

def run_agent_process(name, role):
    """Run agent in process."""
    agent = CollaborationAgent(name, role)
    asyncio.run(agent.start())

def is_server_running():
    """Check if shared memory server is running."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', SHARED_MEMORY_PORT))
    sock.close()
    return result == 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("🚀 Shared Memory Multi-Agent Collaboration")
        print("\nFirst, start the server:")
        print("  python3 shared_collab.py server")
        print("\nThen open separate terminals and run:")
        print("  Terminal 1: python3 shared_collab.py cto")
        print("  Terminal 2: python3 shared_collab.py backend")
        print("  Terminal 3: python3 shared_collab.py qa")
        print("  Terminal 4: python3 shared_collab.py human")
        sys.exit(1)
    
    role = sys.argv[1].lower()
    
    if role == "server":
        # Start the shared memory server
        start_shared_memory_server()
    else:
        # Check if server is running
        if not is_server_running():
            print("❌ Shared memory server is not running!")
            print("Start it first with: python3 shared_collab.py server")
            sys.exit(1)
        
        names = {
            'human': 'Product Owner',
            'cto': 'CTO Agent',
            'backend': 'Backend Developer',
            'qa': 'QA Engineer'
        }
        
        if role not in names:
            print(f"Unknown role: {role}")
            sys.exit(1)
        
        # Run the agent
        run_agent_process(names[role], role)