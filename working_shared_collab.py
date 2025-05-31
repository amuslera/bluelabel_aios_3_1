#!/usr/bin/env python3
"""
Working Shared Memory Multi-Agent Collaboration

This properly shares state between all agents using a socket-based approach.
"""

import asyncio
import json
import time
import sys
import os
from datetime import datetime
import socket
import threading
import uuid
from typing import Dict, List, Any

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Collaboration server port
COLLAB_SERVER_PORT = 6789

class CollaborationServer:
    """Simple TCP server for agent collaboration."""
    
    def __init__(self, port=COLLAB_SERVER_PORT):
        self.port = port
        self.agents = {}
        self.messages = []
        self.lock = threading.Lock()
        self.running = True
        self.clients = []
    
    def start(self):
        """Start the server."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('localhost', self.port))
        server_socket.listen(10)
        
        print(f"🚀 Collaboration server started on port {self.port}")
        
        while self.running:
            try:
                client_socket, address = server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
            except:
                break
    
    def handle_client(self, client_socket):
        """Handle a client connection."""
        self.clients.append(client_socket)
        try:
            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                request = json.loads(data.decode())
                response = self.process_request(request)
                
                client_socket.send(json.dumps(response).encode() + b'\n')
        except:
            pass
        finally:
            self.clients.remove(client_socket)
            client_socket.close()
    
    def process_request(self, request):
        """Process a client request."""
        cmd = request.get('cmd')
        
        if cmd == 'register':
            with self.lock:
                agent_id = request['agent_id']
                self.agents[agent_id] = {
                    'name': request['name'],
                    'role': request['role'],
                    'last_seen': time.time()
                }
                print(f"✅ {request['name']} ({request['role']}) joined!")
                return {'status': 'ok', 'agent_id': agent_id}
        
        elif cmd == 'add_message':
            with self.lock:
                message = {
                    'from': request['from_name'],
                    'role': request['role'],
                    'content': request['content'],
                    'timestamp': time.time()
                }
                self.messages.append(message)
                print(f"💬 {request['from_name']}: {request['content']}")
                return {'status': 'ok'}
        
        elif cmd == 'get_agents':
            with self.lock:
                return {'status': 'ok', 'agents': self.agents}
        
        elif cmd == 'get_messages':
            with self.lock:
                since = request.get('since', 0)
                messages = [m for m in self.messages if m['timestamp'] > since]
                return {'status': 'ok', 'messages': messages}
        
        return {'status': 'error', 'message': 'Unknown command'}

class CollaborationClient:
    """Client for connecting to collaboration server."""
    
    def __init__(self):
        self.socket = None
        self.connected = False
    
    def connect(self, host='localhost', port=COLLAB_SERVER_PORT):
        """Connect to server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
    
    def send_request(self, request):
        """Send request and get response."""
        if not self.connected:
            return None
        
        try:
            self.socket.send(json.dumps(request).encode() + b'\n')
            data = self.socket.recv(4096)
            return json.loads(data.decode())
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def register_agent(self, agent_id, name, role):
        """Register an agent."""
        return self.send_request({
            'cmd': 'register',
            'agent_id': agent_id,
            'name': name,
            'role': role
        })
    
    def add_message(self, from_name, role, content):
        """Add a message."""
        return self.send_request({
            'cmd': 'add_message',
            'from_name': from_name,
            'role': role,
            'content': content
        })
    
    def get_agents(self):
        """Get all agents."""
        response = self.send_request({'cmd': 'get_agents'})
        if response and response['status'] == 'ok':
            return response['agents']
        return {}
    
    def get_messages_since(self, timestamp):
        """Get messages since timestamp."""
        response = self.send_request({
            'cmd': 'get_messages',
            'since': timestamp
        })
        if response and response['status'] == 'ok':
            return response['messages']
        return []

class CollaborationAgent:
    """Agent that uses TCP collaboration."""
    
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.agent_id = f"{role}_{uuid.uuid4().hex[:8]}"
        self.client = CollaborationClient()
        self.last_msg_time = time.time()
        self.has_claude = False
        self.running = True
    
    async def start(self):
        """Start the agent."""
        print(f"🚀 Starting {self.name} ({self.role})")
        
        # Connect to server
        if not self.client.connect():
            print("❌ Cannot connect to collaboration server!")
            print("Make sure server is running: python3 working_shared_collab.py server")
            return
        
        # Setup Claude for AI agents
        if self.role != "human":
            await self.setup_claude()
        
        # Register with collaboration
        self.client.register_agent(self.agent_id, self.name, self.role)
        
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
                    self.client.add_message(self.name, self.role, user_input.strip())
        finally:
            monitor.cancel()
            print(f"👋 {self.name} signing off...")
    
    def show_team(self):
        """Show current team."""
        agents = self.client.get_agents()
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
                new_messages = self.client.get_messages_since(self.last_msg_time)
                
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
                new_messages = self.client.get_messages_since(self.last_msg_time)
                
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
            self.client.add_message(self.name, self.role, response)
    
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("🚀 Working Multi-Agent Collaboration")
        print("\nFirst, start the server:")
        print("  python3 working_shared_collab.py server")
        print("\nThen open separate terminals and run:")
        print("  Terminal 1: python3 working_shared_collab.py cto")
        print("  Terminal 2: python3 working_shared_collab.py backend")
        print("  Terminal 3: python3 working_shared_collab.py qa")
        print("  Terminal 4: python3 working_shared_collab.py human")
        sys.exit(1)
    
    role = sys.argv[1].lower()
    
    if role == "server":
        # Start the collaboration server
        server = CollaborationServer()
        try:
            server.start()
        except KeyboardInterrupt:
            print("\n👋 Server shutting down...")
    else:
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
        agent = CollaborationAgent(names[role], role)
        asyncio.run(agent.start())