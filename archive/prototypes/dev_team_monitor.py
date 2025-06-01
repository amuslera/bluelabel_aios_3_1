#!/usr/bin/env python3
"""
Development Team for Building Monitoring System

This coordinates our AI agents to build their own monitoring dashboard.
Includes strict code review and branch protection.
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
import subprocess
from typing import Dict, List, Any

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Dev server port for monitoring project
MONITOR_DEV_PORT = 6792

class MonitoringProjectServer:
    """Server coordinating monitoring system development."""
    
    def __init__(self, port=MONITOR_DEV_PORT):
        self.port = port
        self.agents = {}
        self.messages = []
        self.tasks = {}
        self.code_reviews = {}
        self.branches = {
            'main': {'protected': True, 'commits': []},
            'feature/cto-monitoring-architecture': {'owner': 'cto', 'commits': []},
            'feature/backend-logging-system': {'owner': 'backend', 'commits': []},
            'feature/frontend-terminal-ui': {'owner': 'frontend', 'commits': []},
            'feature/qa-test-suite': {'owner': 'qa', 'commits': []}
        }
        self.project = {
            'name': 'AIOSv3 Monitoring System',
            'path': 'monitoring_project',
            'description': 'Real-time agent monitoring dashboard',
            'status': 'planning'
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
        
        print(f"🚀 Monitoring Project Development Server started on port {self.port}")
        print(f"📦 Project: {self.project['name']}")
        print(f"🔒 Branch protection enabled - all code must be reviewed!")
        
        # Initialize git repo
        self.init_git_repo()
        
        while self.running:
            try:
                client_socket, address = server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
            except:
                break
    
    def init_git_repo(self):
        """Initialize git repository with branch protection."""
        repo_path = os.path.join(os.getcwd(), self.project['path'])
        if not os.path.exists(repo_path):
            os.makedirs(repo_path)
            subprocess.run(['git', 'init'], cwd=repo_path)
            
            # Create initial structure
            os.makedirs(os.path.join(repo_path, 'src'), exist_ok=True)
            os.makedirs(os.path.join(repo_path, 'tests'), exist_ok=True)
            os.makedirs(os.path.join(repo_path, 'docs'), exist_ok=True)
            
            # Create README
            with open(os.path.join(repo_path, 'README.md'), 'w') as f:
                f.write("# AIOSv3 Monitoring System\n\nBuilt by AI agents for AI agents!")
            
            subprocess.run(['git', 'add', '.'], cwd=repo_path)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=repo_path)
    
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
                    'branch': f"feature/{request['role']}-monitoring-system",
                    'last_seen': time.time()
                }
                print(f"✅ {request['name']} ({request['role']}) joined the team!")
                
                # Create tasks for each agent
                if request['role'] == 'cto':
                    self.create_agent_tasks('cto', [
                        "Design monitoring system architecture",
                        "Define message formats and protocols",
                        "Create API specifications"
                    ])
                elif request['role'] == 'backend':
                    self.create_agent_tasks('backend', [
                        "Implement agent activity logging",
                        "Create message streaming system",
                        "Build data persistence layer"
                    ])
                elif request['role'] == 'frontend':
                    self.create_agent_tasks('frontend', [
                        "Build terminal UI framework",
                        "Implement real-time display",
                        "Add interactive commands"
                    ])
                elif request['role'] == 'qa':
                    self.create_agent_tasks('qa', [
                        "Write unit tests",
                        "Create integration tests",
                        "Build test data generators"
                    ])
                
                return {'status': 'ok', 'agent_id': agent_id}
        
        elif cmd == 'submit_code':
            # Agent submitting code for review
            with self.lock:
                review_id = f"review_{uuid.uuid4().hex[:8]}"
                self.code_reviews[review_id] = {
                    'id': review_id,
                    'agent': request['agent'],
                    'branch': request['branch'],
                    'files': request['files'],
                    'description': request['description'],
                    'status': 'pending_review',
                    'submitted_at': time.time()
                }
                print(f"📝 Code review requested: {request['description']}")
                return {'status': 'ok', 'review_id': review_id}
        
        elif cmd == 'get_review_status':
            with self.lock:
                review_id = request['review_id']
                if review_id in self.code_reviews:
                    return {'status': 'ok', 'review': self.code_reviews[review_id]}
                return {'status': 'error', 'message': 'Review not found'}
        
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
        
        return {'status': 'error', 'message': 'Unknown command'}
    
    def create_agent_tasks(self, role, task_descriptions):
        """Create tasks for an agent."""
        for desc in task_descriptions:
            task_id = f"task_{uuid.uuid4().hex[:8]}"
            self.tasks[task_id] = {
                'id': task_id,
                'description': desc,
                'assigned_to': role,
                'status': 'pending',
                'created_at': time.time()
            }

class MonitoringDevelopmentAgent:
    """Agent that develops the monitoring system."""
    
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.agent_id = f"{role}_{uuid.uuid4().hex[:8]}"
        self.client = MonitoringDevClient()
        self.last_msg_time = time.time()
        self.running = True
        self.current_task = None
        self.project_path = "monitoring_project"
        self.branch = f"feature/{role}-monitoring-system"
    
    async def start(self):
        """Start the agent."""
        print(f"🚀 Starting {self.name} ({self.role})")
        print(f"🌿 Working on branch: {self.branch}")
        
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
    
    async def run_developer(self):
        """Run developer agent with strict practices."""
        print(f"🤖 {self.name} ready to develop monitoring system!")
        print(f"📋 Following junior developer practices: clear code, lots of comments, ask for help")
        
        # Switch to feature branch
        self.switch_to_branch()
        
        while self.running:
            try:
                # Check for tasks
                await self.check_for_tasks()
                
                # If working on a task, show progress
                if self.current_task:
                    await self.work_on_task()
                
                await asyncio.sleep(3)
            except KeyboardInterrupt:
                break
        
        print(f"👋 {self.name} signing off...")
    
    async def check_for_tasks(self):
        """Check for available tasks."""
        if self.current_task:
            return  # Already working on something
        
        # Get tasks from server
        tasks = self.client.get_tasks()
        if not tasks:
            return
            
        # Find tasks assigned to this role
        for task_id, task in tasks.items():
            if task.get('assigned_to') == self.role and task.get('status') == 'pending':
                self.current_task = task
                print(f"\n📋 {self.name}: Claimed task: {task['description']}")
                
                # Update task status
                self.client.update_task(task_id, {'status': 'in_progress'})
                break
    
    def switch_to_branch(self):
        """Switch to feature branch."""
        repo_path = os.path.join(os.getcwd(), self.project_path)
        
        try:
            # Check if branch exists
            result = subprocess.run(['git', 'branch', '--list', self.branch], 
                                  cwd=repo_path, capture_output=True, text=True)
            
            if self.branch in result.stdout:
                # Branch exists, switch to it
                result = subprocess.run(['git', 'checkout', self.branch], 
                                      cwd=repo_path, capture_output=True, text=True)
            else:
                # Create new branch
                result = subprocess.run(['git', 'checkout', '-b', self.branch], 
                                      cwd=repo_path, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"⚠️ Git error: {result.stderr}")
            else:
                print(f"🌿 Switched to branch: {self.branch}")
                
        except Exception as e:
            print(f"❌ Error switching branch: {e}")
    
    async def work_on_task(self):
        """Work on current task with verbose output."""
        task_desc = self.current_task['description']
        
        print(f"\n{'='*60}")
        print(f"🔨 {self.name} working on: {task_desc}")
        print(f"{'='*60}")
        
        if self.role == 'cto' and 'architecture' in task_desc.lower():
            await self.design_architecture()
        elif self.role == 'backend' and 'logging' in task_desc.lower():
            await self.implement_logging()
        elif self.role == 'frontend' and 'terminal ui' in task_desc.lower():
            await self.build_terminal_ui()
        elif self.role == 'qa' and 'test' in task_desc.lower():
            await self.write_tests()
        
        # Mark task complete
        self.current_task = None
    
    async def build_terminal_ui(self):
        """Frontend builds the terminal UI."""
        print(f"🎨 {self.name}: Starting terminal UI implementation...")
        await asyncio.sleep(2)
        
        print(f"💭 {self.name}: Researching terminal UI libraries...")
        print(f"   - Option 1: Rich (modern, feature-rich)")
        print(f"   - Option 2: Blessed (classic, stable)")
        print(f"   - Option 3: Curses (built-in, low-level)")
        await asyncio.sleep(3)
        
        print(f"📐 {self.name}: Decided on Rich for modern UI capabilities")
        
        # Create terminal UI code
        ui_code = '''"""
Terminal UI for AIOSv3 Monitoring Dashboard

Built with Rich library for modern terminal interfaces.
Following junior developer practices with clear documentation.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any
import json
from pathlib import Path

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn


class MonitoringDashboard:
    """
    Real-time monitoring dashboard for AI agents.
    
    Shows agent status, tasks, and activity feed in terminal.
    """
    
    def __init__(self):
        """Initialize the dashboard."""
        self.console = Console()
        self.agents = {}
        self.tasks = {}
        self.activities = []
        self.running = True
        
        # Layout setup
        self.layout = Layout()
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=1)
        )
        
        # Split body into panels
        self.layout["body"].split_row(
            Layout(name="agents", ratio=1),
            Layout(name="tasks", ratio=1)
        )
        
        print("Dashboard initialized")
    
    def create_header(self) -> Panel:
        """Create header panel."""
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_row(
            "[bold blue]AIOSv3 Monitoring Dashboard[/bold blue]"
        )
        grid.add_row(
            f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]"
        )
        return Panel(grid, style="white on blue")
    
    def create_agents_panel(self) -> Panel:
        """Create agents status panel."""
        table = Table(title="Agent Status", expand=True)
        table.add_column("Agent", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Current Task")
        table.add_column("Progress")
        
        # Add agent rows
        for agent_id, info in self.agents.items():
            status = info.get('status', 'idle')
            task = info.get('current_task', 'None')
            progress = info.get('progress', 0)
            
            # Color code status
            if status == 'working':
                status_text = "[green]● Working[/green]"
            elif status == 'blocked':
                status_text = "[red]● Blocked[/red]"
            else:
                status_text = "[yellow]● Idle[/yellow]"
            
            table.add_row(
                info['name'],
                status_text,
                task[:40] + "..." if len(task) > 40 else task,
                f"{progress}%"
            )
        
        return Panel(table, title="👥 Agents", border_style="blue")
    
    def create_tasks_panel(self) -> Panel:
        """Create tasks panel."""
        table = Table(title="Active Tasks", expand=True)
        table.add_column("ID", style="dim")
        table.add_column("Description")
        table.add_column("Assigned To")
        table.add_column("Status")
        
        # Add task rows
        for task_id, task in self.tasks.items():
            status = task.get('status', 'pending')
            
            # Color code status
            if status == 'completed':
                status_text = "[green]✓ Done[/green]"
            elif status == 'in_progress':
                status_text = "[yellow]⚡ Active[/yellow]"
            else:
                status_text = "[dim]○ Pending[/dim]"
            
            table.add_row(
                task_id[:8],
                task['description'][:35] + "...",
                task.get('assigned_to', 'Unassigned'),
                status_text
            )
        
        return Panel(table, title="📋 Tasks", border_style="green")
    
    def create_footer(self) -> Panel:
        """Create footer with commands."""
        return Panel(
            "[bold]Commands:[/bold] [q]uit | [r]efresh | [a]gents | [t]asks",
            style="dim"
        )
    
    async def update_display(self):
        """Update the dashboard display."""
        self.layout["header"].update(self.create_header())
        self.layout["agents"].update(self.create_agents_panel())
        self.layout["tasks"].update(self.create_tasks_panel())
        self.layout["footer"].update(self.create_footer())
    
    async def load_data(self):
        """Load data from log files."""
        # In real implementation, would connect to WebSocket
        # For now, read from log files
        log_dir = Path("logs")
        if log_dir.exists():
            for log_file in log_dir.glob("*.jsonl"):
                try:
                    with open(log_file) as f:
                        for line in f:
                            activity = json.loads(line)
                            self.process_activity(activity)
                except:
                    pass
    
    def process_activity(self, activity: Dict[str, Any]):
        """Process an activity update."""
        agent_id = activity.get('agent_id')
        
        # Update agent info
        if agent_id:
            if agent_id not in self.agents:
                self.agents[agent_id] = {
                    'name': activity.get('agent_name', 'Unknown'),
                    'status': 'idle'
                }
            
            # Update based on activity type
            if activity['activity_type'] == 'task_started':
                self.agents[agent_id]['status'] = 'working'
                self.agents[agent_id]['current_task'] = activity['details'].get('description', '')
            elif activity['activity_type'] == 'task_completed':
                self.agents[agent_id]['status'] = 'idle'
                self.agents[agent_id]['current_task'] = 'None'
            elif activity['activity_type'] == 'progress_update':
                self.agents[agent_id]['progress'] = activity['details'].get('progress', 0)
    
    async def run(self):
        """Run the dashboard."""
        with Live(self.layout, refresh_per_second=2, screen=True):
            while self.running:
                await self.load_data()
                await self.update_display()
                await asyncio.sleep(1)


async def main():
    """Run the monitoring dashboard."""
    dashboard = MonitoringDashboard()
    
    try:
        await dashboard.run()
    except KeyboardInterrupt:
        print("\\nDashboard stopped")


if __name__ == "__main__":
    asyncio.run(main())
'''
        
        file_path = os.path.join(self.project_path, 'src', 'dashboard', 'terminal_ui.py')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.write_file(file_path, ui_code)
        
        print(f"✅ {self.name}: Created terminal UI implementation")
        
        # Submit for review
        self.submit_code_for_review(
            [file_path],
            "Implement terminal monitoring dashboard with Rich"
        )
    
    async def write_tests(self):
        """QA writes tests for the monitoring system."""
        print(f"🧪 {self.name}: Planning test strategy...")
        await asyncio.sleep(2)
        
        print(f"📝 {self.name}: Writing integration tests...")
        
        # Create test code
        test_code = '''"""
Integration tests for monitoring system.

Tests the logger and dashboard working together.
"""

import pytest
import asyncio
import json
from pathlib import Path
import tempfile

from src.logging.agent_logger import AgentActivityLogger
from src.dashboard.terminal_ui import MonitoringDashboard


class TestMonitoringIntegration:
    """Test monitoring components work together."""
    
    @pytest.mark.asyncio
    async def test_logger_creates_readable_logs(self):
        """Test logger output can be read by dashboard."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Override log directory
            logger = AgentActivityLogger("test_agent", "Test Agent", "test")
            logger.log_file = Path(tmpdir) / "test_agent.jsonl"
            logger.log_file.parent.mkdir(exist_ok=True)
            
            # Log some activities
            await logger.start_task("TASK-001", "Test task")
            await logger.update_progress(50, "Halfway done")
            await logger.complete_task("Task completed")
            
            # Verify log file exists and is valid JSON
            assert logger.log_file.exists()
            
            with open(logger.log_file) as f:
                lines = f.readlines()
                assert len(lines) == 3
                
                # Each line should be valid JSON
                for line in lines:
                    data = json.loads(line)
                    assert 'timestamp' in data
                    assert 'agent_id' in data
                    assert 'activity_type' in data
    
    @pytest.mark.asyncio
    async def test_dashboard_processes_activities(self):
        """Test dashboard correctly processes activity logs."""
        dashboard = MonitoringDashboard()
        
        # Process a task started activity
        activity = {
            'agent_id': 'test_123',
            'agent_name': 'Test Agent',
            'activity_type': 'task_started',
            'details': {'description': 'Test task'}
        }
        dashboard.process_activity(activity)
        
        # Verify agent status updated
        assert 'test_123' in dashboard.agents
        assert dashboard.agents['test_123']['status'] == 'working'
        assert dashboard.agents['test_123']['current_task'] == 'Test task'
        
        # Process progress update
        progress_activity = {
            'agent_id': 'test_123',
            'activity_type': 'progress_update',
            'details': {'progress': 75}
        }
        dashboard.process_activity(progress_activity)
        
        assert dashboard.agents['test_123']['progress'] == 75
    
    def test_end_to_end_monitoring(self):
        """Test complete monitoring flow."""
        # This would test the full system
        # For now, just verify imports work
        assert AgentActivityLogger is not None
        assert MonitoringDashboard is not None
'''
        
        file_path = os.path.join(self.project_path, 'tests', 'test_integration.py')
        self.write_file(file_path, test_code)
        
        print(f"✅ {self.name}: Created integration tests")
        
        # Submit for review
        self.submit_code_for_review(
            [file_path],
            "Write integration tests for monitoring system"
        )
    
    async def design_architecture(self):
        """CTO designs the monitoring architecture."""
        print(f"🧠 {self.name}: Analyzing requirements for monitoring system...")
        await asyncio.sleep(2)
        
        print(f"💭 {self.name}: Considering different architectural patterns...")
        print(f"   - Option 1: Direct WebSocket connection")
        print(f"   - Option 2: Message queue with Redis")
        print(f"   - Option 3: File-based with inotify")
        await asyncio.sleep(3)
        
        print(f"📐 {self.name}: Decided on WebSocket + fallback to file monitoring")
        
        # Create architecture document
        arch_content = '''# Monitoring System Architecture

## Overview
Real-time monitoring system for AIOSv3 agents with <1s latency goal.

## Architecture Decision
After analyzing requirements, I've chosen a **hybrid approach**:
1. Primary: WebSocket for real-time updates
2. Fallback: File-based monitoring for reliability

## Components

### 1. Agent Logger
```python
# Each agent includes this logger
class AgentActivityLogger:
    """Logs all agent activities with structured data."""
    
    def log_activity(self, activity_type: str, details: dict):
        # Send via WebSocket if connected
        # Write to file as backup
        pass
```

### 2. Message Format
```json
{
    "timestamp": "2025-05-31T14:23:41.123Z",
    "agent_id": "backend_12345",
    "agent_name": "Backend Developer",
    "activity_type": "file_operation",
    "details": {
        "operation": "create",
        "file_path": "/src/models/user.py",
        "lines_added": 145
    },
    "task_id": "TASK-176",
    "progress": 82
}
```

### 3. Data Flow
```
Agent Activity → Logger → WebSocket/File → Monitor Service → Terminal UI
```

## Implementation Plan
1. Backend team: Implement logger and streaming
2. Frontend team: Build terminal UI
3. QA team: Test with high message volumes
'''
        
        file_path = os.path.join(self.project_path, 'docs', 'monitoring_architecture.md')
        self.write_file(file_path, arch_content)
        
        print(f"✅ {self.name}: Created architecture document")
        print(f"📄 {self.name}: Ready for code review before merging")
        
        # Submit for review
        self.submit_code_for_review(
            [file_path],
            "Architecture design for monitoring system"
        )
    
    async def implement_logging(self):
        """Backend implements the logging system."""
        print(f"💻 {self.name}: Starting logging system implementation...")
        await asyncio.sleep(2)
        
        print(f"📝 {self.name}: Creating agent activity logger class...")
        
        logger_code = '''"""
Agent Activity Logger for AIOSv3 Monitoring System

This module provides logging functionality for all agent activities.
Following junior developer practices: clear code, extensive comments.
"""

import json
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
import websockets
from pathlib import Path


class AgentActivityLogger:
    """
    Logs all agent activities for real-time monitoring.
    
    This logger sends activities via WebSocket when available,
    with file-based fallback for reliability.
    """
    
    def __init__(self, agent_id: str, agent_name: str, agent_role: str):
        """
        Initialize the logger for a specific agent.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_name: Human-readable name (e.g., "Backend Developer")
            agent_role: Agent role (e.g., "backend", "frontend")
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.agent_role = agent_role
        self.websocket = None
        self.connected = False
        self.log_file = Path(f"logs/{agent_id}.jsonl")
        
        # Create logs directory if it doesn't exist
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Current task tracking
        self.current_task_id = None
        self.task_start_time = None
        self.task_progress = 0
        
        print(f"Logger initialized for {agent_name}")
    
    async def connect(self, monitor_url: str = "ws://localhost:6793"):
        """
        Connect to the monitoring service via WebSocket.
        
        Args:
            monitor_url: WebSocket URL of monitoring service
        """
        try:
            self.websocket = await websockets.connect(monitor_url)
            self.connected = True
            print(f"✅ Connected to monitoring service")
            
            # Send initial registration
            await self._send_activity("agent_connected", {
                "agent_role": self.agent_role,
                "status": "ready"
            })
        except Exception as e:
            print(f"⚠️  Could not connect to monitor: {e}")
            print(f"   Falling back to file-based logging")
            self.connected = False
    
    async def log_activity(self, activity_type: str, details: Dict[str, Any]):
        """
        Log an agent activity.
        
        Args:
            activity_type: Type of activity (e.g., "file_created", "task_started")
            details: Dictionary with activity-specific details
        """
        # Create activity record
        activity = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "activity_type": activity_type,
            "details": details,
            "task_id": self.current_task_id,
            "progress": self.task_progress
        }
        
        # Try to send via WebSocket
        if self.connected:
            try:
                await self._send_activity(activity_type, details)
            except:
                self.connected = False
                print("⚠️  Lost connection to monitor")
        
        # Always write to file as backup
        self._write_to_file(activity)
    
    async def _send_activity(self, activity_type: str, details: Dict[str, Any]):
        """Send activity via WebSocket."""
        if self.websocket:
            message = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "activity_type": activity_type,
                "details": details,
                "task_id": self.current_task_id,
                "progress": self.task_progress
            }
            await self.websocket.send(json.dumps(message))
    
    def _write_to_file(self, activity: Dict[str, Any]):
        """Write activity to log file."""
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(activity) + '\\n')
    
    async def start_task(self, task_id: str, description: str):
        """Log task start."""
        self.current_task_id = task_id
        self.task_start_time = time.time()
        self.task_progress = 0
        
        await self.log_activity("task_started", {
            "task_id": task_id,
            "description": description
        })
    
    async def update_progress(self, progress: int, message: str = ""):
        """Update task progress."""
        self.task_progress = progress
        
        await self.log_activity("progress_update", {
            "progress": progress,
            "message": message
        })
    
    async def complete_task(self, summary: str):
        """Log task completion."""
        duration = time.time() - self.task_start_time if self.task_start_time else 0
        
        await self.log_activity("task_completed", {
            "task_id": self.current_task_id,
            "duration_seconds": duration,
            "summary": summary
        })
        
        self.current_task_id = None
        self.task_progress = 100


# Example usage
async def example_usage():
    """Show how to use the logger."""
    logger = AgentActivityLogger(
        agent_id="backend_12345",
        agent_name="Backend Developer",
        agent_role="backend"
    )
    
    # Connect to monitor
    await logger.connect()
    
    # Log various activities
    await logger.start_task("TASK-101", "Implement user authentication")
    
    await logger.log_activity("decision_made", {
        "decision": "Use JWT for authentication",
        "reasoning": "Stateless and scalable"
    })
    
    await logger.update_progress(25, "Created user model")
    
    await logger.log_activity("file_created", {
        "file_path": "/src/models/user.py",
        "lines": 89
    })
    
    await logger.update_progress(50, "Implemented auth endpoints")
    
    await logger.complete_task("Authentication system implemented")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
'''
        
        file_path = os.path.join(self.project_path, 'src', 'logging', 'agent_logger.py')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.write_file(file_path, logger_code)
        
        print(f"✅ {self.name}: Created agent logger implementation")
        
        # Create a simple test
        test_code = '''"""Tests for agent activity logger."""

import pytest
import asyncio
import json
from pathlib import Path
from src.logging.agent_logger import AgentActivityLogger


@pytest.mark.asyncio
async def test_logger_initialization():
    """Test logger initializes correctly."""
    logger = AgentActivityLogger(
        agent_id="test_123",
        agent_name="Test Agent",
        agent_role="test"
    )
    
    assert logger.agent_id == "test_123"
    assert logger.agent_name == "Test Agent"
    assert logger.agent_role == "test"
    assert logger.current_task_id is None


@pytest.mark.asyncio
async def test_file_logging():
    """Test logging to file works."""
    logger = AgentActivityLogger(
        agent_id="test_file",
        agent_name="Test Agent",
        agent_role="test"
    )
    
    # Log an activity
    await logger.log_activity("test_activity", {
        "test_data": "hello world"
    })
    
    # Check file was created
    log_file = Path(f"logs/test_file.jsonl")
    assert log_file.exists()
    
    # Read and verify content
    with open(log_file, 'r') as f:
        line = f.readline()
        data = json.loads(line)
        
    assert data['agent_id'] == "test_file"
    assert data['activity_type'] == "test_activity"
    assert data['details']['test_data'] == "hello world"
    
    # Cleanup
    log_file.unlink()


@pytest.mark.asyncio  
async def test_task_tracking():
    """Test task start and completion tracking."""
    logger = AgentActivityLogger(
        agent_id="test_task",
        agent_name="Test Agent",
        agent_role="test"
    )
    
    # Start a task
    await logger.start_task("TASK-001", "Test task")
    assert logger.current_task_id == "TASK-001"
    assert logger.task_progress == 0
    
    # Update progress
    await logger.update_progress(50, "Halfway done")
    assert logger.task_progress == 50
    
    # Complete task
    await logger.complete_task("Task finished")
    assert logger.current_task_id is None
    assert logger.task_progress == 100
    
    # Cleanup
    Path(f"logs/test_task.jsonl").unlink(missing_ok=True)
'''
        
        test_path = os.path.join(self.project_path, 'tests', 'test_agent_logger.py')
        os.makedirs(os.path.dirname(test_path), exist_ok=True)
        self.write_file(test_path, test_code)
        
        print(f"✅ {self.name}: Created test suite for logger")
        
        # Submit for review
        self.submit_code_for_review(
            [file_path, test_path],
            "Implement agent activity logger with tests"
        )
    
    def write_file(self, path, content):
        """Write a file and log the action."""
        full_path = os.path.join(os.getcwd(), path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w') as f:
            f.write(content)
        
        print(f"📄 {self.name}: Created {path}")
        
        # Stage the file in git
        repo_path = os.path.join(os.getcwd(), self.project_path)
        subprocess.run(['git', 'add', path], cwd=repo_path)
    
    def submit_code_for_review(self, files, description):
        """Submit code for review."""
        print(f"\n{'='*60}")
        print(f"📝 {self.name}: Submitting code for review")
        print(f"   Description: {description}")
        print(f"   Files: {', '.join(files)}")
        
        # Commit the changes
        repo_path = os.path.join(os.getcwd(), self.project_path)
        
        # Add and commit
        subprocess.run(['git', 'add', '.'], cwd=repo_path)
        result = subprocess.run(['git', 'commit', '-m', f'{self.role}: {description}'], 
                              cwd=repo_path, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"   ✅ Committed changes to branch: {self.branch}")
        else:
            print(f"   ❌ Commit failed: {result.stderr}")
        
        print(f"{'='*60}\n")
        
        self.client.submit_code(
            self.agent_id,
            self.branch,
            files,
            description
        )
    
    async def run_human(self):
        """Human interface to monitor and review."""
        print(f"\n💡 Welcome {self.name}!")
        print("Commands:")
        print("  'status' - Check team status")
        print("  'reviews' - See pending code reviews")
        print("  'approve <review_id>' - Approve a code review")
        print("  'reject <review_id> <reason>' - Reject with feedback")
        print("  'quit' - Exit")
        print()
        
        while self.running:
            user_input = await asyncio.get_event_loop().run_in_executor(
                None, input, f"{self.role}> "
            )
            
            if user_input.strip().lower() == 'quit':
                break
            elif user_input.strip().lower() == 'status':
                self.show_status()
            elif user_input.strip().lower() == 'reviews':
                self.show_reviews()
            elif user_input.strip().lower().startswith('approve'):
                parts = user_input.split()
                if len(parts) > 1:
                    self.approve_review(parts[1])
            elif user_input.strip().lower().startswith('reject'):
                parts = user_input.split(maxsplit=2)
                if len(parts) > 2:
                    self.reject_review(parts[1], parts[2])
    
    def show_status(self):
        """Show project status."""
        print("\n📊 Project Status")
        print("=" * 60)
        
        agents = self.client.get_agents()
        print(f"👥 Team Members: {len(agents)}")
        for agent_id, info in agents.items():
            print(f"   - {info['name']} ({info['role']})")
        
        tasks = self.client.get_tasks()
        pending = sum(1 for t in tasks.values() if t['status'] == 'pending')
        in_progress = sum(1 for t in tasks.values() if t['status'] == 'in_progress')
        completed = sum(1 for t in tasks.values() if t['status'] == 'completed')
        
        print(f"\n📋 Tasks: {len(tasks)} total")
        print(f"   - Pending: {pending}")
        print(f"   - In Progress: {in_progress}")
        print(f"   - Completed: {completed}")
        print("=" * 60)
    
    def show_reviews(self):
        """Show pending code reviews."""
        print("\n📝 Pending Code Reviews")
        print("=" * 60)
        
        # Quick implementation - check git branches
        import subprocess
        repo_path = os.path.join(os.getcwd(), self.project_path)
        
        # Debug: print the repo path
        print(f"Checking branches in: {repo_path}")
        
        # Get all branches
        result = subprocess.run(['git', 'branch', '-a'], 
                              cwd=repo_path, capture_output=True, text=True)
        
        branches = [b.strip() for b in result.stdout.split('\n') if 'feature/' in b and '*' not in b]
        
        if branches:
            print("Agents have submitted code on these branches:")
            for i, branch in enumerate(branches, 1):
                agent = branch.split('/')[-1].split('-')[0]
                print(f"  {i}. {agent.upper()} - Branch: {branch}")
            print("\nTo review: git checkout <branch> && git diff main")
            print("To approve: approve <agent> (e.g., 'approve cto')")
        else:
            print("No feature branches found.")
        print("=" * 60)
    
    def approve_review(self, review_id):
        """Approve a code review."""
        import subprocess
        repo_path = os.path.join(os.getcwd(), self.project_path)
        
        # Map agent names to branches
        branch_map = {
            'cto': 'feature/cto-monitoring-system',
            'backend': 'feature/backend-monitoring-system',
            'frontend': 'feature/frontend-monitoring-system',
            'qa': 'feature/qa-monitoring-system'
        }
        
        agent = review_id.lower()
        if agent in branch_map:
            branch = branch_map[agent]
            print(f"✅ Approving {agent.upper()}'s code...")
            
            # Checkout main
            subprocess.run(['git', 'checkout', 'main'], cwd=repo_path, capture_output=True)
            
            # Merge the feature branch
            result = subprocess.run(['git', 'merge', branch, '--no-ff', '-m', f'Merge {agent} implementation'], 
                                  cwd=repo_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Successfully merged {agent}'s code into main!")
                # Delete the feature branch
                subprocess.run(['git', 'branch', '-d', branch], cwd=repo_path, capture_output=True)
            else:
                print(f"❌ Merge failed: {result.stderr}")
        else:
            print(f"❌ Unknown agent: {review_id}")
            print("Use: approve cto | approve backend | approve frontend | approve qa")
    
    def reject_review(self, review_id, reason):
        """Reject a code review."""
        print(f"❌ Rejecting review: {review_id}")
        print(f"   Reason: {reason}")
        # Would send rejection to server

class MonitoringDevClient:
    """Client for monitoring development server."""
    
    def __init__(self):
        self.socket = None
        self.connected = False
    
    def connect(self, host='localhost', port=MONITOR_DEV_PORT):
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
    
    def submit_code(self, agent, branch, files, description):
        """Submit code for review."""
        return self.send_request({
            'cmd': 'submit_code',
            'agent': agent,
            'branch': branch,
            'files': files,
            'description': description
        })
    
    def get_tasks(self):
        """Get all tasks."""
        response = self.send_request({'cmd': 'get_tasks'})
        if response and response['status'] == 'ok':
            return response.get('tasks', {})
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
            return response.get('agents', {})
        return {}
    
    def add_message(self, from_name, role, content):
        """Add a message."""
        return self.send_request({
            'cmd': 'add_message',
            'from_name': from_name,
            'role': role,
            'content': content
        })


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("🚀 Monitoring System Development Project")
        print("\nGoal: Build our own monitoring dashboard using AI agents!")
        print("\nFirst, start the server:")
        print("  python3 dev_team_monitor.py server")
        print("\nThen launch agents in separate terminals:")
        print("  Terminal 1: python3 dev_team_monitor.py cto")
        print("  Terminal 2: python3 dev_team_monitor.py backend")
        print("  Terminal 3: python3 dev_team_monitor.py frontend")
        print("  Terminal 4: python3 dev_team_monitor.py qa")
        print("  Terminal 5: python3 dev_team_monitor.py human")
        print("\n🔒 All code must be reviewed before merging!")
        sys.exit(1)
    
    role = sys.argv[1].lower()
    
    if role == "server":
        # Start the development server
        server = MonitoringProjectServer()
        try:
            server.start()
        except KeyboardInterrupt:
            print("\n👋 Server shutting down...")
    else:
        names = {
            'human': 'Tech Lead (You)',
            'cto': 'CTO Agent',
            'backend': 'Backend Developer',
            'frontend': 'Frontend Developer',
            'qa': 'QA Engineer'
        }
        
        if role not in names:
            print(f"Unknown role: {role}")
            sys.exit(1)
        
        # Run the agent
        agent = MonitoringDevelopmentAgent(names[role], role)
        asyncio.run(agent.start())