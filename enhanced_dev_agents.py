#!/usr/bin/env python3
"""
Enhanced Development Agents with Real-Time Visibility

Building on lessons from Sprint 1.3, these agents provide full visibility
into their operations and follow complete git workflows.
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
from pathlib import Path

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Ports
VISIBILITY_SERVER_PORT = 6793
DEV_SERVER_PORT = 6794

class VisibilityServer:
    """Server that provides real-time visibility into agent operations."""
    
    def __init__(self, port=VISIBILITY_SERVER_PORT):
        self.port = port
        self.activities = []
        self.agent_status = {}
        self.lock = threading.Lock()
        self.clients = []
        self.running = True
    
    def start(self):
        """Start the visibility server."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('localhost', self.port))
        server_socket.listen(10)
        
        print(f"👁️  Visibility server started on port {self.port}")
        
        # Start activity printer thread
        printer_thread = threading.Thread(target=self.print_activities)
        printer_thread.daemon = True
        printer_thread.start()
        
        while self.running:
            try:
                client_socket, address = server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
            except:
                break
    
    def handle_client(self, client_socket):
        """Handle visibility client."""
        self.clients.append(client_socket)
        try:
            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                activity = json.loads(data.decode())
                self.process_activity(activity)
                
                # Acknowledge
                client_socket.send(b'{"status": "ok"}\n')
        except:
            pass
        finally:
            self.clients.remove(client_socket)
            client_socket.close()
    
    def process_activity(self, activity):
        """Process an activity from an agent."""
        with self.lock:
            # Add to activities
            activity['timestamp'] = time.time()
            self.activities.append(activity)
            
            # Update agent status
            agent_id = activity.get('agent_id')
            if agent_id:
                if agent_id not in self.agent_status:
                    self.agent_status[agent_id] = {
                        'name': activity.get('agent_name', 'Unknown'),
                        'role': activity.get('agent_role', 'unknown')
                    }
                
                self.agent_status[agent_id].update({
                    'last_activity': activity['activity_type'],
                    'last_update': time.time(),
                    'status': activity.get('status', 'active'),
                    'current_task': activity.get('current_task'),
                    'progress': activity.get('progress', 0)
                })
    
    def print_activities(self):
        """Print activities in real-time."""
        last_print = 0
        
        while self.running:
            with self.lock:
                new_activities = [a for a in self.activities if a['timestamp'] > last_print]
            
            for activity in new_activities:
                self.format_activity(activity)
                last_print = activity['timestamp']
            
            time.sleep(0.1)
    
    def format_activity(self, activity):
        """Format and print an activity."""
        timestamp = datetime.fromtimestamp(activity['timestamp']).strftime('%H:%M:%S')
        agent_name = activity.get('agent_name', 'Unknown')
        activity_type = activity['activity_type']
        details = activity.get('details', {})
        
        # Color coding based on activity type
        if activity_type == 'error':
            prefix = "❌"
            color = "\033[91m"  # Red
        elif activity_type == 'success':
            prefix = "✅"
            color = "\033[92m"  # Green
        elif activity_type == 'git_operation':
            prefix = "🔀"
            color = "\033[94m"  # Blue
        elif activity_type == 'file_operation':
            prefix = "📄"
            color = "\033[93m"  # Yellow
        elif activity_type == 'decision':
            prefix = "💭"
            color = "\033[95m"  # Purple
        elif activity_type == 'progress':
            prefix = "📊"
            color = "\033[96m"  # Cyan
        else:
            prefix = "ℹ️"
            color = "\033[0m"   # Default
        
        reset = "\033[0m"
        
        # Format message
        message = f"{color}[{timestamp}] {prefix} {agent_name}: "
        
        if activity_type == 'git_operation':
            message += f"Git: {details.get('command', 'unknown')}"
            if 'result' in details:
                message += f" → {details['result']}"
        elif activity_type == 'file_operation':
            message += f"File: {details.get('operation', 'unknown')} {details.get('path', '')}"
        elif activity_type == 'decision':
            message += f"Decision: {details.get('decision', '')} - {details.get('reasoning', '')}"
        elif activity_type == 'progress':
            message += f"Progress: {details.get('task', '')} [{details.get('progress', 0)}%]"
        elif activity_type == 'error':
            message += f"Error: {details.get('error', 'Unknown error')}"
        else:
            message += details.get('message', str(details))
        
        print(message + reset)

class VisibleAgent:
    """Base class for agents with comprehensive visibility."""
    
    def __init__(self, name, role, agent_id):
        self.name = name
        self.role = role
        self.agent_id = agent_id
        self.visibility_client = None
        self.current_task = None
        self.task_progress = 0
        
    async def connect_visibility(self):
        """Connect to visibility server."""
        for attempt in range(3):
            try:
                self.visibility_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.visibility_client.connect(('localhost', VISIBILITY_SERVER_PORT))
                self.visibility_client.settimeout(5.0)  # Add timeout
                await self.log_activity('agent_started', {
                    'message': f'{self.name} connected to visibility server'
                })
                return True
            except Exception as e:
                print(f"⚠️  {self.name} couldn't connect to visibility server (attempt {attempt + 1}/3): {e}")
                if attempt < 2:
                    await asyncio.sleep(1)  # Wait before retry
                else:
                    print(f"❌ {self.name} failed to connect after 3 attempts")
        return False
    
    async def log_activity(self, activity_type: str, details: dict):
        """Log an activity to the visibility server."""
        activity = {
            'agent_id': self.agent_id,
            'agent_name': self.name,
            'agent_role': self.role,
            'activity_type': activity_type,
            'details': details,
            'current_task': self.current_task,
            'progress': self.task_progress
        }
        
        if self.visibility_client:
            try:
                self.visibility_client.send(json.dumps(activity).encode() + b'\n')
                # Wait for acknowledgment
                self.visibility_client.recv(1024)
            except:
                pass
        
        # Also print locally for debugging
        if activity_type == 'error':
            print(f"❌ {self.name}: {details.get('error', 'Unknown error')}")
    
    async def run_command(self, cmd: list, description: str) -> subprocess.CompletedProcess:
        """Run a command with full visibility."""
        await self.log_activity('command_start', {
            'command': ' '.join(cmd),
            'description': description
        })
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                await self.log_activity('command_success', {
                    'command': ' '.join(cmd),
                    'output': result.stdout[:200] if result.stdout else 'No output'
                })
            else:
                await self.log_activity('error', {
                    'command': ' '.join(cmd),
                    'error': result.stderr or 'Command failed',
                    'return_code': result.returncode
                })
            
            return result
        except Exception as e:
            await self.log_activity('error', {
                'command': ' '.join(cmd),
                'error': str(e)
            })
            raise
    
    async def write_file(self, path: str, content: str):
        """Write a file with visibility."""
        await self.log_activity('file_operation', {
            'operation': 'write',
            'path': path
        })
        
        try:
            full_path = Path(path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            
            await self.log_activity('file_operation', {
                'operation': 'write_complete',
                'path': path,
                'size': len(content)
            })
        except Exception as e:
            await self.log_activity('error', {
                'operation': 'file_write',
                'path': path,
                'error': str(e)
            })
            raise
    
    async def make_decision(self, decision: str, reasoning: str):
        """Log a decision with reasoning."""
        await self.log_activity('decision', {
            'decision': decision,
            'reasoning': reasoning
        })
    
    async def update_progress(self, progress: int, message: str = ""):
        """Update task progress."""
        self.task_progress = progress
        await self.log_activity('progress', {
            'task': self.current_task or 'Unknown task',
            'progress': progress,
            'message': message
        })
    
    async def git_operation(self, operation: str, details: dict = None):
        """Log a git operation."""
        await self.log_activity('git_operation', {
            'command': operation,
            **({'result': 'success', **(details or {})})
        })

class EnhancedDevelopmentAgent(VisibleAgent):
    """Development agent with full visibility and proper workflows."""
    
    def __init__(self, name, role):
        agent_id = f"{role}_{uuid.uuid4().hex[:8]}"
        super().__init__(name, role, agent_id)
        self.project_path = "visibility_project"
        self.branch = f"feature/{role}-visibility"
        
    async def start(self):
        """Start the agent with visibility."""
        print(f"🚀 Starting {self.name} with enhanced visibility")
        
        # Connect to visibility server
        print(f"📡 Connecting to visibility server on port {VISIBILITY_SERVER_PORT}...")
        if not await self.connect_visibility():
            print("⚠️  Running without visibility server")
            # Still continue even without visibility
        else:
            print("✅ Connected to visibility server")
        
        # Initialize git repository
        print(f"🔧 Setting up git repository...")
        await self.setup_git_repo()
        
        # Start working
        print(f"💼 Starting work on tasks...")
        await self.work_on_tasks()
    
    async def setup_git_repo(self):
        """Set up git repository with visibility."""
        await self.log_activity('setup', {'message': 'Initializing git repository'})
        
        # Create project directory
        os.makedirs(self.project_path, exist_ok=True)
        
        # Initialize git if needed
        if not os.path.exists(os.path.join(self.project_path, '.git')):
            await self.run_command(
                ['git', 'init'],
                'Initialize git repository',
                cwd=self.project_path
            )
            
            # Set git config
            await self.run_command(
                ['git', 'config', 'user.email', f'{self.role}@aiosv3.ai'],
                'Configure git email',
                cwd=self.project_path
            )
            await self.run_command(
                ['git', 'config', 'user.name', self.name],
                'Configure git name',
                cwd=self.project_path
            )
            
            # Create initial commit if needed
            readme_path = os.path.join(self.project_path, 'README.md')
            if not os.path.exists(readme_path):
                with open(readme_path, 'w') as f:
                    f.write(f"# Visibility Project\n\nBuilt by {self.name}")
                await self.run_command(
                    ['git', 'add', 'README.md'],
                    'Add README',
                    cwd=self.project_path
                )
                await self.run_command(
                    ['git', 'commit', '-m', 'Initial commit'],
                    'Create initial commit',
                    cwd=self.project_path
                )
        
        # Check if we're already on the branch
        current_branch_result = await self.run_command(
            ['git', 'branch', '--show-current'],
            'Check current branch',
            cwd=self.project_path
        )
        
        current_branch = current_branch_result.stdout.strip()
        
        if current_branch == self.branch:
            await self.log_activity('info', {
                'message': f'Already on branch {self.branch}'
            })
        else:
            # Try to checkout existing branch first
            result = await self.run_command(
                ['git', 'checkout', self.branch],
                f'Switch to existing branch {self.branch}',
                cwd=self.project_path
            )
            
            if result.returncode != 0:
                # Branch doesn't exist, create it
                await self.git_operation('checkout -b', {'branch': self.branch})
                result = await self.run_command(
                    ['git', 'checkout', '-b', self.branch],
                    f'Create new branch {self.branch}',
                    cwd=self.project_path
                )
                
                if result.returncode != 0:
                    # Last resort: use unique branch
                    import time
                    self.branch = f"{self.branch}-{int(time.time())}"
                    await self.log_activity('info', {
                        'message': f'Using unique branch: {self.branch}'
                    })
                    await self.run_command(
                        ['git', 'checkout', '-b', self.branch],
                        f'Create unique branch {self.branch}',
                        cwd=self.project_path
                    )
    
    async def work_on_tasks(self):
        """Work on assigned tasks with full visibility."""
        if self.role == 'monitor':
            await self.build_monitoring_dashboard()
        elif self.role == 'logger':
            await self.implement_activity_logger()
        elif self.role == 'tester':
            await self.write_visibility_tests()
    
    async def implement_activity_logger(self):
        """Implement the activity logging system."""
        self.current_task = "Implement activity logging system"
        await self.update_progress(0, "Starting logger implementation")
        
        await self.make_decision(
            "Use async logging with queues",
            "Async logging prevents blocking agent operations"
        )
        
        await self.update_progress(30, "Creating logger class")
        
        # Create logger code
        logger_code = '''"""Activity logger for agent visibility."""
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import aiofiles

class ActivityLogger:
    """Logs agent activities for visibility."""
    
    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.log_queue = asyncio.Queue()
        self.log_file = Path(f"logs/{agent_id}.jsonl")
        self.log_file.parent.mkdir(exist_ok=True)
        
    async def log(self, activity_type: str, details: Dict[str, Any]):
        """Queue an activity for logging."""
        activity = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "activity_type": activity_type,
            "details": details
        }
        await self.log_queue.put(activity)
    
    async def process_logs(self):
        """Process queued logs."""
        while True:
            activity = await self.log_queue.get()
            async with aiofiles.open(self.log_file, 'a') as f:
                await f.write(json.dumps(activity) + '\\n')
'''
        
        await self.write_file(
            os.path.join(self.project_path, 'src/activity_logger.py'),
            logger_code
        )
        
        await self.update_progress(70, "Logger implementation complete")
        
        # Commit the work
        await self.git_operation('add', {'files': 'src/activity_logger.py'})
        add_result = await self.run_command(
            ['git', 'add', '.'],
            'Stage logger files',
            cwd=self.project_path
        )
        
        if add_result.returncode == 0:
            await self.git_operation('commit', {'message': 'Implement activity logger'})
            commit_result = await self.run_command(
                ['git', 'commit', '-m', 'feat: Implement async activity logger'],
                'Commit logger implementation',
                cwd=self.project_path
            )
            
            if commit_result.returncode != 0:
                # Maybe nothing to commit?
                await self.log_activity('warning', {
                    'message': 'Nothing to commit or commit failed',
                    'stderr': commit_result.stderr
                })
        else:
            await self.log_activity('error', {
                'message': 'Failed to stage files',
                'stderr': add_result.stderr
            })
        
        await self.update_progress(100, "Logger implementation complete")
        await self.log_activity('success', {
            'message': 'Successfully implemented activity logger'
        })
    
    async def write_visibility_tests(self):
        """Write tests for the visibility system."""
        self.current_task = "Write visibility system tests"
        await self.update_progress(0, "Starting test implementation")
        
        await self.make_decision(
            "Use pytest with async support",
            "Pytest-asyncio provides good async testing capabilities"
        )
        
        await self.update_progress(40, "Writing test cases")
        
        # Create test code
        test_code = '''"""Tests for visibility system."""
import pytest
import asyncio
from src.activity_logger import ActivityLogger
from pathlib import Path
import json

@pytest.mark.asyncio
async def test_activity_logger():
    """Test activity logger functionality."""
    # Create logger
    logger = ActivityLogger("test_agent", "Test Agent")
    
    # Log some activities
    await logger.log("test_start", {"test": "visibility"})
    await logger.log("test_progress", {"progress": 50})
    await logger.log("test_complete", {"status": "success"})
    
    # Process logs
    process_task = asyncio.create_task(logger.process_logs())
    await asyncio.sleep(0.1)  # Let it process
    process_task.cancel()
    
    # Verify log file exists
    assert logger.log_file.exists()
    
    # Read and verify logs
    with open(logger.log_file) as f:
        lines = f.readlines()
    
    assert len(lines) == 3
    
    # Verify first log entry
    first_log = json.loads(lines[0])
    assert first_log["agent_id"] == "test_agent"
    assert first_log["activity_type"] == "test_start"
    assert first_log["details"]["test"] == "visibility"

@pytest.mark.asyncio
async def test_concurrent_logging():
    """Test concurrent logging from multiple agents."""
    loggers = [
        ActivityLogger(f"agent_{i}", f"Agent {i}")
        for i in range(3)
    ]
    
    # Log concurrently
    tasks = []
    for i, logger in enumerate(loggers):
        for j in range(5):
            tasks.append(
                logger.log("action", {"agent": i, "action": j})
            )
    
    await asyncio.gather(*tasks)
    
    # Verify all logs were queued
    for i, logger in enumerate(loggers):
        assert logger.log_queue.qsize() == 5
'''
        
        await self.write_file(
            os.path.join(self.project_path, 'tests/test_visibility.py'),
            test_code
        )
        
        await self.update_progress(80, "Tests complete")
        
        # Commit the work
        await self.git_operation('add', {'files': 'tests/test_visibility.py'})
        await self.run_command(
            ['git', 'add', '.'],
            'Stage test files',
            cwd=self.project_path
        )
        
        await self.git_operation('commit', {'message': 'Add visibility tests'})
        await self.run_command(
            ['git', 'commit', '-m', 'test: Add visibility system tests'],
            'Commit test implementation',
            cwd=self.project_path
        )
        
        await self.update_progress(100, "Test implementation complete")
        await self.log_activity('success', {
            'message': 'Successfully implemented visibility tests'
        })
    
    async def build_monitoring_dashboard(self):
        """Build the monitoring dashboard."""
        self.current_task = "Build real-time monitoring dashboard"
        await self.update_progress(0, "Starting dashboard development")
        
        await self.make_decision(
            "Use Rich for terminal UI",
            "Rich provides modern terminal UI capabilities with live updates"
        )
        
        await self.update_progress(25, "Creating dashboard structure")
        
        # Create dashboard code
        dashboard_code = '''"""Real-time monitoring dashboard for AIOSv3 agents."""
import asyncio
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.panel import Panel

class AgentMonitorDashboard:
    """Real-time dashboard showing agent activities."""
    
    def __init__(self):
        self.console = Console()
        self.agents = {}
        self.activities = []
        
    def create_layout(self):
        """Create dashboard layout."""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="agents", size=10),
            Layout(name="activities", size=15),
            Layout(name="footer", size=1)
        )
        return layout
    
    def update_header(self, layout):
        """Update header panel."""
        layout["header"].update(Panel(
            f"[bold blue]AIOSv3 Agent Monitor[/bold blue] - {datetime.now().strftime('%H:%M:%S')}",
            style="white on blue"
        ))
    
    def update_agents_panel(self, layout):
        """Update agents status panel."""
        table = Table(title="Active Agents")
        table.add_column("Agent", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Current Task")
        table.add_column("Progress")
        
        for agent_id, info in self.agents.items():
            table.add_row(
                info['name'],
                info.get('status', 'active'),
                info.get('current_task', 'idle')[:50],
                f"{info.get('progress', 0)}%"
            )
        
        layout["agents"].update(Panel(table, title="👥 Agent Status"))
    
    async def run(self):
        """Run the dashboard."""
        layout = self.create_layout()
        
        with Live(layout, refresh_per_second=2) as live:
            while True:
                self.update_header(layout)
                self.update_agents_panel(layout)
                await asyncio.sleep(0.5)
'''
        
        await self.write_file(
            os.path.join(self.project_path, 'src/dashboard.py'),
            dashboard_code
        )
        
        await self.update_progress(75, "Dashboard code complete")
        
        # Commit the work
        await self.git_operation('add', {'files': 'src/dashboard.py'})
        await self.run_command(
            ['git', 'add', '.'],
            'Stage dashboard files',
            cwd=self.project_path
        )
        
        await self.git_operation('commit', {'message': 'Implement monitoring dashboard'})
        await self.run_command(
            ['git', 'commit', '-m', 'feat: Implement real-time monitoring dashboard'],
            'Commit dashboard implementation',
            cwd=self.project_path
        )
        
        await self.update_progress(100, "Dashboard implementation complete")
        await self.log_activity('success', {
            'message': 'Successfully implemented monitoring dashboard'
        })
    
    async def run_command(self, cmd: list, description: str, cwd=None) -> subprocess.CompletedProcess:
        """Run command with working directory support."""
        await self.log_activity('command_start', {
            'command': ' '.join(cmd),
            'description': description,
            'cwd': cwd or os.getcwd()
        })
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
            
            if result.returncode == 0:
                await self.log_activity('command_success', {
                    'command': ' '.join(cmd),
                    'output': result.stdout[:200] if result.stdout else 'No output'
                })
            else:
                # Log the full error for debugging
                error_msg = result.stderr or 'Command failed'
                await self.log_activity('error', {
                    'command': ' '.join(cmd),
                    'error': error_msg,
                    'return_code': result.returncode,
                    'stdout': result.stdout[:200] if result.stdout else 'No stdout'
                })
                print(f"❌ Full error: {error_msg}")  # Print locally for debugging
            
            return result
        except Exception as e:
            await self.log_activity('error', {
                'command': ' '.join(cmd),
                'error': str(e),
                'type': type(e).__name__
            })
            print(f"❌ Exception: {e}")  # Print locally for debugging
            raise

async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("🚀 Enhanced Development Agents with Real-Time Visibility")
        print("\nUsage:")
        print("  Terminal 1: python3 enhanced_dev_agents.py visibility")
        print("  Terminal 2: python3 enhanced_dev_agents.py monitor")
        print("  Terminal 3: python3 enhanced_dev_agents.py logger")
        print("  Terminal 4: python3 enhanced_dev_agents.py tester")
        return
    
    role = sys.argv[1].lower()
    
    if role == 'visibility':
        # Start visibility server
        server = VisibilityServer()
        try:
            server.start()
        except KeyboardInterrupt:
            print("\n👋 Visibility server shutting down")
    else:
        # Start agent
        names = {
            'monitor': 'Dashboard Developer',
            'logger': 'Logger Developer',
            'tester': 'Test Engineer'
        }
        
        if role in names:
            agent = EnhancedDevelopmentAgent(names[role], role)
            await agent.start()
        else:
            print(f"Unknown role: {role}")

if __name__ == "__main__":
    asyncio.run(main())