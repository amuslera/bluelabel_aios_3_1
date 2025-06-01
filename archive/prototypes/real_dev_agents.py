#!/usr/bin/env python3
"""
Real Development Agents

Multi-agent system that builds actual applications using file operations.
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

# Development server port
DEV_SERVER_PORT = 6791

class DevelopmentServer:
    """Server that coordinates real development work."""
    
    def __init__(self, port=DEV_SERVER_PORT):
        self.port = port
        self.agents = {}
        self.messages = []
        self.tasks = {}
        self.project = {
            'name': 'TodoApp',
            'path': 'todo_app',
            'description': 'A collaborative task management system',
            'tech_stack': None,
            'architecture': None
        }
        self.lock = threading.Lock()
        self.running = True
        self.clients = []
    
    def start(self):
        """Start the server."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('localhost', self.port))
        server_socket.listen(10)
        
        print(f"🚀 Development server started on port {self.port}")
        print(f"📦 Project: {self.project['name']} - {self.project['description']}")
        
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
                data = client_socket.recv(16384)
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
                print(f"✅ {request['name']} ({request['role']}) joined the development team!")
                return {'status': 'ok', 'agent_id': agent_id}
        
        elif cmd == 'get_project':
            with self.lock:
                return {'status': 'ok', 'project': self.project}
        
        elif cmd == 'update_project':
            with self.lock:
                self.project.update(request['updates'])
                print(f"📝 Project updated: {request['updates']}")
                return {'status': 'ok'}
        
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
                    'type': request.get('type', 'development'),
                    'assigned_to': request.get('assigned_to'),
                    'status': 'pending',
                    'created_by': request['created_by'],
                    'created_at': time.time(),
                    'file_path': request.get('file_path')
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

class DevelopmentAgent:
    """Agent that does real development work."""
    
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.agent_id = f"{role}_{uuid.uuid4().hex[:8]}"
        self.client = DevelopmentClient()
        self.last_msg_time = time.time()
        self.running = True
        self.current_task = None
        self.project_path = "todo_app"
    
    async def start(self):
        """Start the agent."""
        print(f"🚀 Starting {self.name} ({self.role})")
        
        # Connect to server
        if not self.client.connect():
            print("❌ Cannot connect to development server!")
            return
        
        # Register with team
        self.client.register_agent(self.agent_id, self.name, self.role)
        
        if self.role == "human":
            await self.run_human()
        else:
            await self.run_developer()
    
    async def run_human(self):
        """Run human interface."""
        print(f"\n💡 Welcome {self.name}!")
        print("Commands:")
        print("  'start project' - Begin the TodoApp development")
        print("  'status' - Check project status")
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
                elif user_input.strip().lower() == 'status':
                    self.show_project_status()
                elif user_input.strip().lower() == 'start project':
                    await self.start_project()
                elif user_input.strip():
                    self.client.add_message(self.name, self.role, user_input.strip())
        finally:
            monitor.cancel()
            print(f"👋 {self.name} signing off...")
    
    async def start_project(self):
        """Initiate the TodoApp project."""
        print("\n🚀 Starting TodoApp Development!")
        
        # Create project directory
        os.makedirs(self.project_path, exist_ok=True)
        
        # Send message to team
        self.client.add_message(
            self.name, self.role,
            "Let's build a TodoApp! CTO, please design the architecture. We need a REST API with user authentication and task management."
        )
        
        # Create initial tasks
        self.client.create_task(
            "Design TodoApp architecture and technology stack",
            self.name,
            task_type="architecture"
        )
    
    def show_project_status(self):
        """Show current project status."""
        project = self.client.get_project()
        print(f"\n📊 Project Status: {project['name']}")
        print(f"Description: {project['description']}")
        print(f"Tech Stack: {project.get('tech_stack', 'Not decided')}")
        print(f"Architecture: {project.get('architecture', 'Not designed')}")
        
        # Check what files exist
        if os.path.exists(self.project_path):
            print(f"\n📁 Project files:")
            for root, dirs, files in os.walk(self.project_path):
                level = root.replace(self.project_path, '').count(os.sep)
                indent = ' ' * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    print(f"{subindent}{file}")
    
    def show_tasks(self):
        """Show all tasks."""
        tasks = self.client.get_tasks()
        if not tasks:
            print("\n📋 No tasks yet!")
            return
            
        print(f"\n📋 Current Tasks ({len(tasks)}):")
        for task_id, task in tasks.items():
            status = task['status']
            assigned = task.get('assigned_to', 'unassigned')
            task_type = task.get('type', 'general')
            print(f"  [{status}] ({task_type}) {task['description']}")
            print(f"      Assigned to: {assigned}")
        print()
    
    def show_team(self):
        """Show current team."""
        agents = self.client.get_agents()
        print(f"\n👥 Development Team ({len(agents)} members):")
        for agent_id, info in agents.items():
            print(f"   🤖 {info['name']} ({info['role']})")
        print()
    
    async def run_developer(self):
        """Run developer agent."""
        print(f"🤖 {self.name} ready to develop!")
        
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
        content_lower = msg['content'].lower()
        
        # CTO responds to architecture requests
        if self.role == 'cto' and 'architecture' in content_lower:
            await asyncio.sleep(2)
            await self.design_architecture()
        
        # All devs respond to "let's implement" type messages
        elif 'implement' in content_lower or 'build' in content_lower:
            if self.role == 'backend':
                # Create backend implementation tasks
                self.client.create_task(
                    "Set up FastAPI project structure",
                    self.name,
                    task_type="setup"
                )
                self.client.create_task(
                    "Implement User model and authentication",
                    self.name,
                    task_type="backend",
                    file_path="todo_app/models/user.py"
                )
                self.client.create_task(
                    "Implement Todo model and CRUD operations",
                    self.name,
                    task_type="backend",
                    file_path="todo_app/models/todo.py"
                )
                self.client.create_task(
                    "Create API endpoints for todos",
                    self.name,
                    task_type="backend",
                    file_path="todo_app/api/todos.py"
                )
    
    async def design_architecture(self):
        """CTO designs the architecture."""
        self.client.add_message(
            self.name, self.role,
            "I'll design a clean, scalable architecture for our TodoApp."
        )
        
        await asyncio.sleep(3)
        
        # Create architecture design
        architecture = {
            'backend': 'FastAPI with async support',
            'database': 'PostgreSQL for data persistence',
            'auth': 'JWT-based authentication',
            'structure': 'Clean architecture with separation of concerns'
        }
        
        # Update project
        self.client.update_project({
            'tech_stack': 'FastAPI + PostgreSQL + JWT',
            'architecture': json.dumps(architecture, indent=2)
        })
        
        # Create architecture document
        arch_content = self.generate_architecture_doc(architecture)
        self.write_file('todo_app/ARCHITECTURE.md', arch_content)
        
        self.client.add_message(
            self.name, self.role,
            "Architecture designed! I've created ARCHITECTURE.md with our tech stack: FastAPI + PostgreSQL + JWT. Backend team, please implement the API structure."
        )
        
        # Create tasks for implementation
        self.client.create_task(
            "Review and approve architecture design",
            self.name,
            task_type="review"
        )
    
    async def check_for_tasks(self):
        """Check for tasks to work on."""
        if self.current_task:
            return  # Already working
        
        tasks = self.client.get_tasks()
        for task_id, task in tasks.items():
            if task['status'] == 'pending' and self.should_take_task(task):
                # Claim the task
                self.client.update_task(task_id, {
                    'status': 'in_progress',
                    'assigned_to': self.name
                })
                self.current_task = task
                
                self.client.add_message(
                    self.name, self.role,
                    f"Working on: {task['description']}"
                )
                
                # Do the work
                await self.do_task_work(task)
                break
    
    def should_take_task(self, task):
        """Check if agent should take this task."""
        task_type = task.get('type', 'general')
        desc_lower = task['description'].lower()
        
        if self.role == 'cto':
            return task_type in ['architecture', 'review', 'design']
        elif self.role == 'backend':
            return task_type in ['backend', 'api', 'setup'] or 'implement' in desc_lower
        elif self.role == 'qa':
            return task_type in ['test', 'quality'] or 'test' in desc_lower
        elif self.role == 'frontend':
            return task_type in ['frontend', 'ui'] or 'ui' in desc_lower
        
        return False
    
    async def do_task_work(self, task):
        """Actually do the work for a task."""
        desc = task['description']
        task_type = task.get('type', 'general')
        
        print(f"🔨 {self.name} working on: {desc}")
        await asyncio.sleep(3)
        
        # Based on task, create actual files
        if 'fastapi project structure' in desc.lower() and self.role == 'backend':
            await self.setup_fastapi_project()
            
        elif 'user model' in desc.lower() and self.role == 'backend':
            code = self.generate_user_model()
            self.write_file('todo_app/models/user.py', code)
            self.client.add_message(
                self.name, self.role,
                "Implemented User model with secure password hashing in models/user.py"
            )
            
        elif 'todo model' in desc.lower() and self.role == 'backend':
            code = self.generate_todo_model()
            self.write_file('todo_app/models/todo.py', code)
            self.client.add_message(
                self.name, self.role,
                "Implemented Todo model with CRUD operations in models/todo.py"
            )
            
        elif 'api endpoints' in desc.lower() and self.role == 'backend':
            code = self.generate_api_endpoints()
            self.write_file('todo_app/api/todos.py', code)
            self.client.add_message(
                self.name, self.role,
                "Created REST API endpoints for todos in api/todos.py"
            )
            
            # QA should write tests
            self.client.create_task(
                "Write tests for todo API endpoints",
                self.name,
                task_type="test",
                file_path="todo_app/tests/test_todos.py"
            )
        
        # Mark task complete
        self.client.update_task(task['id'], {'status': 'completed'})
        self.current_task = None
        
        self.client.add_message(
            self.name, self.role,
            f"✅ Completed: {desc}"
        )
    
    async def setup_fastapi_project(self):
        """Set up FastAPI project structure."""
        # Create directories
        dirs = [
            'todo_app/api',
            'todo_app/models',
            'todo_app/core',
            'todo_app/tests',
            'todo_app/utils'
        ]
        for dir in dirs:
            os.makedirs(dir, exist_ok=True)
            # Create __init__.py files
            self.write_file(f"{dir}/__init__.py", "")
        
        # Create main.py
        main_content = '''"""TodoApp API - Main application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import todos, auth

app = FastAPI(
    title="TodoApp API",
    description="A collaborative task management system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(todos.router, prefix="/api/todos", tags=["todos"])

@app.get("/")
async def root():
    return {"message": "Welcome to TodoApp API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
'''
        self.write_file('todo_app/main.py', main_content)
        
        # Create requirements.txt
        requirements = '''fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
pytest==7.4.3
httpx==0.25.2
'''
        self.write_file('todo_app/requirements.txt', requirements)
        
        # Create config
        config_content = '''"""Application configuration."""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TodoApp"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost/todoapp"
    )
    
    class Config:
        case_sensitive = True

settings = Settings()
'''
        self.write_file('todo_app/core/config.py', config_content)
        
        self.client.add_message(
            self.name, self.role,
            "FastAPI project structure created! Added main.py, requirements.txt, and configuration."
        )
    
    def write_file(self, path, content):
        """Write a file."""
        full_path = os.path.join(os.getcwd(), path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w') as f:
            f.write(content)
        
        print(f"📄 Created: {path}")
    
    def read_file(self, path):
        """Read a file."""
        full_path = os.path.join(os.getcwd(), path)
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                return f.read()
        return None
    
    def generate_architecture_doc(self, architecture):
        """Generate architecture documentation."""
        return f'''# TodoApp Architecture

## Overview
TodoApp is a collaborative task management system built with modern web technologies.

## Technology Stack
- **Backend**: {architecture['backend']}
- **Database**: {architecture['database']}
- **Authentication**: {architecture['auth']}
- **Architecture Pattern**: {architecture['structure']}

## System Architecture

### Backend Structure
```
todo_app/
├── main.py              # FastAPI application entry point
├── api/                 # API endpoints
│   ├── auth.py         # Authentication endpoints
│   └── todos.py        # Todo CRUD endpoints
├── models/             # Data models
│   ├── user.py         # User model
│   └── todo.py         # Todo model
├── core/               # Core functionality
│   ├── config.py       # Application configuration
│   ├── security.py     # Security utilities
│   └── database.py     # Database setup
├── utils/              # Utility functions
└── tests/              # Test suite
```

### API Design
RESTful API with the following endpoints:

#### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

#### Todos
- `GET /api/todos` - List todos (with pagination)
- `POST /api/todos` - Create new todo
- `GET /api/todos/{{id}}` - Get todo details
- `PUT /api/todos/{{id}}` - Update todo
- `DELETE /api/todos/{{id}}` - Delete todo

### Database Schema

#### Users Table
- id (UUID, primary key)
- email (string, unique)
- hashed_password (string)
- is_active (boolean)
- created_at (timestamp)

#### Todos Table
- id (UUID, primary key)
- title (string)
- description (text)
- is_completed (boolean)
- user_id (UUID, foreign key)
- created_at (timestamp)
- updated_at (timestamp)

### Security
- JWT-based authentication
- Password hashing with bcrypt
- Protected endpoints require valid tokens
- CORS configuration for frontend integration

### Development Workflow
1. Backend team implements models and API
2. QA team writes comprehensive tests
3. Frontend team builds UI (future sprint)
4. DevOps team handles deployment (future sprint)
'''
    
    def generate_user_model(self):
        """Generate user model code."""
        return '''"""User model for authentication."""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from passlib.context import CryptContext
import uuid

from core.database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def verify_password(self, plain_password: str) -> bool:
        """Verify a plain password against the hash."""
        return pwd_context.verify(plain_password, self.hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

# Pydantic models for API
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class User(UserInDB):
    pass
'''
    
    def generate_todo_model(self):
        """Generate todo model code."""
        return '''"""Todo model for task management."""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from core.database import Base

class Todo(Base):
    __tablename__ = "todos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="todos")

# Add todos relationship to User model
from models.user import User
User.todos = relationship("Todo", back_populates="owner", cascade="all, delete-orphan")

# Pydantic models for API
from pydantic import BaseModel

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None

class TodoInDB(TodoBase):
    id: uuid.UUID
    is_completed: bool
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Todo(TodoInDB):
    pass
'''
    
    def generate_api_endpoints(self):
        """Generate API endpoints for todos."""
        return '''"""Todo API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
import uuid

from core.database import get_db
from core.security import get_current_user
from models.todo import Todo as TodoModel, TodoCreate, TodoUpdate, Todo
from models.user import User

router = APIRouter()

@router.get("/", response_model=List[Todo])
async def get_todos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    completed: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all todos for the current user with optional filtering."""
    query = db.query(TodoModel).filter(TodoModel.user_id == current_user.id)
    
    if completed is not None:
        query = query.filter(TodoModel.is_completed == completed)
    
    todos = query.offset(skip).limit(limit).all()
    return todos

@router.post("/", response_model=Todo, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new todo."""
    db_todo = TodoModel(
        **todo.dict(),
        user_id=current_user.id
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@router.get("/{todo_id}", response_model=Todo)
async def get_todo(
    todo_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific todo by ID."""
    todo = db.query(TodoModel).filter(
        and_(
            TodoModel.id == todo_id,
            TodoModel.user_id == current_user.id
        )
    ).first()
    
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    return todo

@router.put("/{todo_id}", response_model=Todo)
async def update_todo(
    todo_id: uuid.UUID,
    todo_update: TodoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a todo."""
    todo = db.query(TodoModel).filter(
        and_(
            TodoModel.id == todo_id,
            TodoModel.user_id == current_user.id
        )
    ).first()
    
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    update_data = todo_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(todo, key, value)
    
    db.commit()
    db.refresh(todo)
    return todo

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a todo."""
    todo = db.query(TodoModel).filter(
        and_(
            TodoModel.id == todo_id,
            TodoModel.user_id == current_user.id
        )
    ).first()
    
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    db.delete(todo)
    db.commit()
    return None
'''

class DevelopmentClient:
    """Client for development server."""
    
    def __init__(self):
        self.socket = None
        self.connected = False
    
    def connect(self, host='localhost', port=DEV_SERVER_PORT):
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
            data = self.socket.recv(16384)
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
    
    def get_project(self):
        """Get project info."""
        response = self.send_request({'cmd': 'get_project'})
        if response and response['status'] == 'ok':
            return response['project']
        return {}
    
    def update_project(self, updates):
        """Update project info."""
        return self.send_request({
            'cmd': 'update_project',
            'updates': updates
        })
    
    def add_message(self, from_name, role, content):
        """Add a message."""
        return self.send_request({
            'cmd': 'add_message',
            'from_name': from_name,
            'role': role,
            'content': content
        })
    
    def create_task(self, description, created_by, task_type="development", file_path=None):
        """Create a task."""
        return self.send_request({
            'cmd': 'create_task',
            'description': description,
            'created_by': created_by,
            'type': task_type,
            'file_path': file_path
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
        print("🚀 Real Development Multi-Agent System")
        print("\nFirst, start the server:")
        print("  python3 real_dev_agents.py server")
        print("\nThen open separate terminals for agents:")
        print("  Terminal 1: python3 real_dev_agents.py cto")
        print("  Terminal 2: python3 real_dev_agents.py backend")
        print("  Terminal 3: python3 real_dev_agents.py qa") 
        print("  Terminal 4: python3 real_dev_agents.py human")
        print("\nAs human, type 'start project' to begin TodoApp development!")
        sys.exit(1)
    
    role = sys.argv[1].lower()
    
    if role == "server":
        # Start the development server
        server = DevelopmentServer()
        try:
            server.start()
        except KeyboardInterrupt:
            print("\n👋 Server shutting down...")
    else:
        names = {
            'human': 'Product Owner',
            'cto': 'CTO Agent',
            'backend': 'Backend Developer',
            'qa': 'QA Engineer',
            'frontend': 'Frontend Developer'
        }
        
        if role not in names:
            print(f"Unknown role: {role}")
            sys.exit(1)
        
        # Run the agent
        agent = DevelopmentAgent(names[role], role)
        asyncio.run(agent.start())