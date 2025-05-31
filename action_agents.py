#!/usr/bin/env python3
"""
Action-Oriented Multi-Agent Collaboration

Agents that can actually take coding actions, not just chat.
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
import subprocess

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Collaboration server port
ACTION_SERVER_PORT = 6790

class ActionServer:
    """Server that coordinates agent actions."""
    
    def __init__(self, port=ACTION_SERVER_PORT):
        self.port = port
        self.agents = {}
        self.messages = []
        self.tasks = {}  # task_id -> task_info
        self.lock = threading.Lock()
        self.running = True
        self.clients = []
    
    def start(self):
        """Start the server."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('localhost', self.port))
        server_socket.listen(10)
        
        print(f"🚀 Action server started on port {self.port}")
        
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
                data = client_socket.recv(8192)
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
        
        elif cmd == 'create_task':
            with self.lock:
                task_id = f"task_{uuid.uuid4().hex[:8]}"
                self.tasks[task_id] = {
                    'id': task_id,
                    'description': request['description'],
                    'assigned_to': request.get('assigned_to'),
                    'status': 'pending',
                    'created_by': request['created_by'],
                    'created_at': time.time()
                }
                print(f"📋 New task: {request['description']}")
                return {'status': 'ok', 'task_id': task_id}
        
        elif cmd == 'get_tasks':
            with self.lock:
                return {'status': 'ok', 'tasks': self.tasks}
        
        elif cmd == 'update_task':
            with self.lock:
                task_id = request['task_id']
                if task_id in self.tasks:
                    self.tasks[task_id].update(request['updates'])
                    return {'status': 'ok'}
                return {'status': 'error', 'message': 'Task not found'}
        
        elif cmd == 'get_agents':
            with self.lock:
                return {'status': 'ok', 'agents': self.agents}
        
        elif cmd == 'get_messages':
            with self.lock:
                since = request.get('since', 0)
                messages = [m for m in self.messages if m['timestamp'] > since]
                return {'status': 'ok', 'messages': messages}
        
        return {'status': 'error', 'message': 'Unknown command'}

class ActionAgent:
    """Agent that can take actual coding actions."""
    
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.agent_id = f"{role}_{uuid.uuid4().hex[:8]}"
        self.client = ActionClient()
        self.last_msg_time = time.time()
        self.running = True
        self.current_task = None
    
    async def start(self):
        """Start the agent."""
        print(f"🚀 Starting {self.name} ({self.role})")
        
        # Connect to server
        if not self.client.connect():
            print("❌ Cannot connect to action server!")
            print("Make sure server is running: python3 action_agents.py server")
            return
        
        # Register with collaboration
        self.client.register_agent(self.agent_id, self.name, self.role)
        
        if self.role == "human":
            await self.run_human()
        else:
            await self.run_ai_agent()
    
    async def run_human(self):
        """Run human interface."""
        print(f"\n💡 Welcome {self.name}!")
        print("Commands:")
        print("  <message> - Send a message")
        print("  'task: <description>' - Create a task")
        print("  'tasks' - Show all tasks")
        print("  'team' - Show team members")
        print("  'quit' - Exit")
        print()
        
        # Start message monitor
        monitor = asyncio.create_task(self.monitor_updates())
        
        try:
            while self.running:
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, f"{self.role}> "
                )
                
                if user_input.strip().lower() == 'quit':
                    break
                elif user_input.strip().lower() == 'team':
                    self.show_team()
                elif user_input.strip().lower() == 'tasks':
                    self.show_tasks()
                elif user_input.strip().lower().startswith('task:'):
                    task_desc = user_input[5:].strip()
                    self.create_task(task_desc)
                elif user_input.strip():
                    self.client.add_message(self.name, self.role, user_input.strip())
        finally:
            monitor.cancel()
            print(f"👋 {self.name} signing off...")
    
    def create_task(self, description):
        """Create a new task."""
        response = self.client.create_task(description, self.name)
        if response and response['status'] == 'ok':
            print(f"✅ Task created: {response['task_id']}")
    
    def show_tasks(self):
        """Show all tasks."""
        tasks = self.client.get_tasks()
        print(f"\n📋 Current Tasks ({len(tasks)}):")
        for task_id, task in tasks.items():
            status = task['status']
            assigned = task.get('assigned_to', 'unassigned')
            print(f"  [{status}] {task['description']} (assigned to: {assigned})")
        print()
    
    def show_team(self):
        """Show current team."""
        agents = self.client.get_agents()
        print(f"\n👥 Current Team ({len(agents)} members):")
        for agent_id, info in agents.items():
            print(f"   🤖 {info['name']} ({info['role']})")
        print()
    
    async def run_ai_agent(self):
        """Run AI agent."""
        print(f"🤖 {self.name} ready to work on tasks...")
        
        while self.running:
            try:
                # Check for new messages
                new_messages = self.client.get_messages_since(self.last_msg_time)
                
                for msg in new_messages:
                    if msg['from'] != self.name:
                        await self.handle_message(msg)
                    self.last_msg_time = msg['timestamp']
                
                # Check for tasks to work on
                await self.check_for_tasks()
                
                await asyncio.sleep(2)
            except KeyboardInterrupt:
                break
        
        print(f"👋 {self.name} signing off...")
    
    async def monitor_updates(self):
        """Monitor for updates (human interface)."""
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
        # Check if message creates a task
        if msg['role'] == 'human' and 'implement' in msg['content'].lower():
            if self.role == 'cto':
                # CTO breaks down the task
                await asyncio.sleep(1)
                self.client.add_message(
                    self.name, self.role, 
                    "I'll break this down into subtasks for the team."
                )
                
                # Create implementation tasks
                if 'authentication' in msg['content'].lower():
                    self.client.create_task("Design authentication architecture", self.name)
                    self.client.create_task("Implement JWT token system", self.name)
                    self.client.create_task("Create user model and database schema", self.name)
                    self.client.create_task("Write authentication tests", self.name)
    
    async def check_for_tasks(self):
        """Check for tasks to work on."""
        if self.current_task:
            return  # Already working on something
        
        tasks = self.client.get_tasks()
        for task_id, task in tasks.items():
            if task['status'] == 'pending' and self.should_take_task(task):
                # Claim the task
                self.client.update_task(task_id, {
                    'status': 'in_progress',
                    'assigned_to': self.name
                })
                self.current_task = task
                
                # Announce working on it
                self.client.add_message(
                    self.name, self.role,
                    f"I'm starting work on: {task['description']}"
                )
                
                # Simulate doing the work
                await self.do_task_work(task)
                break
    
    def should_take_task(self, task):
        """Check if agent should take this task."""
        desc_lower = task['description'].lower()
        
        if self.role == 'backend':
            return any(word in desc_lower for word in ['implement', 'api', 'database', 'model', 'jwt'])
        elif self.role == 'qa':
            return any(word in desc_lower for word in ['test', 'validate', 'verify'])
        elif self.role == 'cto':
            return any(word in desc_lower for word in ['design', 'architecture'])
        
        return False
    
    async def do_task_work(self, task):
        """Actually do the work for a task."""
        desc = task['description']
        
        print(f"🔨 {self.name} working on: {desc}")
        await asyncio.sleep(3)  # Simulate work
        
        # Based on task, create actual files
        if 'user model' in desc.lower() and self.role == 'backend':
            # Create a user model file
            code = self.generate_user_model()
            self.write_file('models/user.py', code)
            self.client.add_message(
                self.name, self.role,
                "Created user model in models/user.py with fields: id, email, password_hash, created_at"
            )
        
        elif 'jwt token' in desc.lower() and self.role == 'backend':
            # Create JWT implementation
            code = self.generate_jwt_auth()
            self.write_file('auth/jwt_handler.py', code)
            self.client.add_message(
                self.name, self.role,
                "Implemented JWT token system in auth/jwt_handler.py with create_token and verify_token functions"
            )
        
        elif 'test' in desc.lower() and self.role == 'qa':
            # Create test file
            code = self.generate_auth_tests()
            self.write_file('tests/test_authentication.py', code)
            self.client.add_message(
                self.name, self.role,
                "Created authentication tests in tests/test_authentication.py covering login, token validation, and edge cases"
            )
        
        # Mark task complete
        self.client.update_task(task['id'], {'status': 'completed'})
        self.current_task = None
        
        self.client.add_message(
            self.name, self.role,
            f"✅ Completed: {desc}"
        )
    
    def write_file(self, path, content):
        """Write a file."""
        full_path = os.path.join(os.getcwd(), path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w') as f:
            f.write(content)
        
        print(f"📄 Created: {path}")
    
    def generate_user_model(self):
        """Generate user model code."""
        return '''"""User model for authentication system."""
from datetime import datetime
from typing import Optional
import hashlib
import secrets

class User:
    """User model with secure password handling."""
    
    def __init__(self, email: str, password: Optional[str] = None):
        self.id = self._generate_id()
        self.email = email
        self.password_hash = self._hash_password(password) if password else None
        self.created_at = datetime.utcnow()
        self.is_active = True
    
    def _generate_id(self) -> str:
        """Generate unique user ID."""
        return secrets.token_urlsafe(16)
    
    def _hash_password(self, password: str) -> str:
        """Hash password with salt."""
        salt = secrets.token_bytes(32)
        pwdhash = hashlib.pbkdf2_hmac('sha256', 
                                       password.encode('utf-8'), 
                                       salt, 100000)
        return salt.hex() + pwdhash.hex()
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash."""
        if not self.password_hash:
            return False
        
        salt = bytes.fromhex(self.password_hash[:64])
        stored_hash = self.password_hash[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha256',
                                       password.encode('utf-8'),
                                       salt, 100000)
        return pwdhash.hex() == stored_hash
'''
    
    def generate_jwt_auth(self):
        """Generate JWT authentication code."""
        return '''"""JWT token handling for authentication."""
import jwt
import datetime
from typing import Optional, Dict, Any

SECRET_KEY = "your-secret-key-here"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_token(user_id: str, email: str) -> str:
    """Create JWT access token."""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.datetime.utcnow()
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user(token: str) -> Optional[Dict[str, Any]]:
    """Get current user from token."""
    payload = verify_token(token)
    if payload:
        return {
            "user_id": payload.get("user_id"),
            "email": payload.get("email")
        }
    return None
'''
    
    def generate_auth_tests(self):
        """Generate authentication tests."""
        return '''"""Tests for authentication system."""
import pytest
from models.user import User
from auth.jwt_handler import create_token, verify_token, get_current_user

class TestUserModel:
    """Test user model functionality."""
    
    def test_user_creation(self):
        """Test creating a new user."""
        user = User("test@example.com", "password123")
        assert user.email == "test@example.com"
        assert user.password_hash is not None
        assert user.is_active is True
    
    def test_password_verification(self):
        """Test password verification."""
        user = User("test@example.com", "password123")
        assert user.verify_password("password123") is True
        assert user.verify_password("wrongpassword") is False
    
    def test_unique_user_ids(self):
        """Test that user IDs are unique."""
        user1 = User("user1@example.com", "pass1")
        user2 = User("user2@example.com", "pass2")
        assert user1.id != user2.id

class TestJWTAuth:
    """Test JWT authentication functionality."""
    
    def test_create_token(self):
        """Test token creation."""
        token = create_token("user123", "test@example.com")
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_valid_token(self):
        """Test verifying a valid token."""
        token = create_token("user123", "test@example.com")
        payload = verify_token(token)
        assert payload is not None
        assert payload["user_id"] == "user123"
        assert payload["email"] == "test@example.com"
    
    def test_verify_invalid_token(self):
        """Test verifying an invalid token."""
        payload = verify_token("invalid.token.here")
        assert payload is None
    
    def test_get_current_user(self):
        """Test getting current user from token."""
        token = create_token("user123", "test@example.com")
        user = get_current_user(token)
        assert user is not None
        assert user["user_id"] == "user123"
        assert user["email"] == "test@example.com"
'''

class ActionClient:
    """Client for action server."""
    
    def __init__(self):
        self.socket = None
        self.connected = False
    
    def connect(self, host='localhost', port=ACTION_SERVER_PORT):
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
            data = self.socket.recv(8192)
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
    
    def create_task(self, description, created_by):
        """Create a task."""
        return self.send_request({
            'cmd': 'create_task',
            'description': description,
            'created_by': created_by
        })
    
    def get_tasks(self):
        """Get all tasks."""
        response = self.send_request({'cmd': 'get_tasks'})
        if response and response['status'] == 'ok':
            return response['tasks']
        return {}
    
    def update_task(self, task_id, updates):
        """Update a task."""
        return self.send_request({
            'cmd': 'update_task',
            'task_id': task_id,
            'updates': updates
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("🚀 Action-Oriented Multi-Agent System")
        print("\nFirst, start the server:")
        print("  python3 action_agents.py server")
        print("\nThen open separate terminals and run:")
        print("  Terminal 1: python3 action_agents.py cto")
        print("  Terminal 2: python3 action_agents.py backend")
        print("  Terminal 3: python3 action_agents.py qa")
        print("  Terminal 4: python3 action_agents.py human")
        print("\nAs human, create tasks like:")
        print("  task: Implement user authentication system")
        sys.exit(1)
    
    role = sys.argv[1].lower()
    
    if role == "server":
        # Start the action server
        server = ActionServer()
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
        agent = ActionAgent(names[role], role)
        asyncio.run(agent.start())