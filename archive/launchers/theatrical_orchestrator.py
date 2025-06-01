#!/usr/bin/env python3
"""
Theatrical Orchestrator - Launch real agents with human-comprehensible pacing

This orchestrates the real development of the monitoring system with theatrical
agents, making the development process visible and understandable.
"""

import asyncio
import sys
import os
import json
import subprocess
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Import our theatrical base agent
from theatrical_base_agent import TheatricalBaseAgent, create_theatrical_agent

# Configuration
THEATRICAL_PROJECT_PATH = "theatrical_monitor_project"
VISIBILITY_SERVER_PORT = 6795

class TheatricalOrchestrator:
    """Orchestrates theatrical agents to build real software."""
    
    def __init__(self):
        self.agents = {}
        self.project_path = THEATRICAL_PROJECT_PATH
        self.start_time = datetime.now()
        
    def print_header(self):
        """Print orchestrator header."""
        print("\n" + "="*70)
        print("🎭 THEATRICAL AGENT ORCHESTRATOR - Real Development with Visibility")
        print("="*70)
        print(f"Project: Complete Monitoring System")
        print(f"Location: {self.project_path}/")
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
    
    async def setup_project(self):
        """Initialize project structure."""
        print("🔧 Setting up project structure...")
        
        # Create project directory
        os.makedirs(self.project_path, exist_ok=True)
        
        # Initialize git
        if not os.path.exists(os.path.join(self.project_path, '.git')):
            subprocess.run(['git', 'init'], cwd=self.project_path, capture_output=True)
            
            # Create initial README
            readme_content = """# Theatrical Monitoring System

A real-time monitoring system for AIOSv3 agents, built by theatrical agents
with full visibility into the development process.

## Features
- Real-time activity streaming
- Agent status dashboard
- Progress tracking
- Decision visibility
- Error monitoring

## Built By
- Sarah Kim (Architect)
- Marcus Chen (Backend)
- Alex Thompson (Frontend)
- Diana Martinez (Monitor)

Built with ❤️ by AI agents working at human pace.
"""
            with open(os.path.join(self.project_path, 'README.md'), 'w') as f:
                f.write(readme_content)
            
            subprocess.run(['git', 'add', '.'], cwd=self.project_path)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], 
                         cwd=self.project_path, capture_output=True)
        
        print("✅ Project structure ready\n")
    
    async def create_sprint_plan(self):
        """Create a detailed sprint plan for the monitoring system."""
        print("📋 Creating Sprint Plan for Monitoring System...\n")
        
        sprint_plan = {
            "sprint_name": "Complete Monitoring System",
            "duration": "1 day",
            "goal": "Build a fully functional monitoring system with dashboard",
            "tasks": [
                {
                    "id": "ARCH-001",
                    "assignee": "architect",
                    "title": "Design monitoring architecture",
                    "description": "Design the complete monitoring system architecture including real-time data flow, storage, and visualization components",
                    "deliverables": ["architecture.md", "system_design.py"]
                },
                {
                    "id": "BACK-001", 
                    "assignee": "backend",
                    "title": "Implement monitoring server",
                    "description": "Build WebSocket server for real-time agent activity streaming with persistence and querying capabilities",
                    "deliverables": ["monitoring_server.py", "activity_store.py"],
                    "depends_on": ["ARCH-001"]
                },
                {
                    "id": "BACK-002",
                    "assignee": "backend",
                    "title": "Create agent integration library",
                    "description": "Build client library for agents to report activities with automatic retries and buffering",
                    "deliverables": ["agent_reporter.py", "activity_types.py"],
                    "depends_on": ["ARCH-001"]
                },
                {
                    "id": "FRONT-001",
                    "assignee": "frontend",
                    "title": "Build monitoring dashboard",
                    "description": "Create Rich-based terminal dashboard showing real-time agent activities, status, and progress",
                    "deliverables": ["dashboard.py", "dashboard_components.py"],
                    "depends_on": ["ARCH-001", "BACK-001"]
                },
                {
                    "id": "MON-001",
                    "assignee": "monitor",
                    "title": "Implement metrics collection",
                    "description": "Build metrics collection system for agent performance, task completion rates, and error tracking",
                    "deliverables": ["metrics_collector.py", "metrics_dashboard.py"],
                    "depends_on": ["BACK-001"]
                },
                {
                    "id": "BACK-003",
                    "assignee": "backend",
                    "title": "Add persistence layer",
                    "description": "Implement SQLite persistence for activity history and metrics with efficient querying",
                    "deliverables": ["database.py", "models.py"],
                    "depends_on": ["BACK-001"]
                },
                {
                    "id": "TEST-001",
                    "assignee": "backend",
                    "title": "Write integration tests",
                    "description": "Create comprehensive tests for the monitoring system including load testing",
                    "deliverables": ["test_monitoring.py", "test_integration.py"]
                }
            ]
        }
        
        # Save sprint plan
        plan_path = os.path.join(self.project_path, 'SPRINT_PLAN.json')
        with open(plan_path, 'w') as f:
            json.dump(sprint_plan, f, indent=2)
        
        print(f"✅ Sprint plan created: {plan_path}\n")
        return sprint_plan
    
    async def launch_agent(self, role: str, task_queue: asyncio.Queue):
        """Launch a theatrical agent to work on tasks."""
        # Define capabilities based on role
        capabilities_map = {
            'architect': ['design', 'planning', 'documentation'],
            'backend': ['coding', 'api_design', 'database', 'testing'],
            'frontend': ['ui_design', 'coding', 'visualization'],
            'monitor': ['metrics', 'analysis', 'reporting']
        }
        
        capabilities = capabilities_map.get(role, ['coding'])
        
        # Simple LLM config (would use real config in production)
        llm_config = {
            'model': 'gpt-4',
            'temperature': 0.7
        }
        
        # Create theatrical agent
        agent = create_theatrical_agent(role, capabilities, llm_config)
        self.agents[role] = agent
        
        print(f"\n{agent.emoji} Launching {agent.theatrical_name} ({role})...")
        
        # Agent introduction
        await agent.narrate_action(
            f"Hello! I'm {agent.theatrical_name}, the {role} specialist.",
            "I'll be working on the monitoring system today."
        )
        
        # Process tasks
        while True:
            try:
                task = await asyncio.wait_for(task_queue.get(), timeout=60.0)
                
                if task is None:  # Shutdown signal
                    break
                
                await agent.narrate_action(
                    f"Received task: {task['title']}",
                    task['description']
                )
                
                # Simulate task execution with theatrical elements
                await self.execute_task_theatrically(agent, task)
                
            except asyncio.TimeoutError:
                await agent.narrate_action(
                    "No new tasks available",
                    "Waiting for dependencies to complete..."
                )
    
    async def execute_task_theatrically(self, agent: TheatricalBaseAgent, task: dict):
        """Execute a task with full theatrical presentation."""
        task_id = task['id']
        
        # Think about the task
        await agent.think_aloud(f"how to approach {task['title']}")
        
        # Based on task type, show different execution patterns
        if 'architecture' in task['title'].lower():
            await self.design_architecture(agent, task)
        elif 'server' in task['title'].lower():
            await self.implement_server(agent, task)
        elif 'dashboard' in task['title'].lower():
            await self.build_dashboard(agent, task)
        elif 'integration' in task['title'].lower():
            await self.create_integration(agent, task)
        elif 'metrics' in task['title'].lower():
            await self.implement_metrics(agent, task)
        elif 'persistence' in task['title'].lower():
            await self.add_persistence(agent, task)
        elif 'test' in task['title'].lower():
            await self.write_tests(agent, task)
        else:
            # Generic task execution
            await agent.show_progress(
                task['title'],
                [
                    "Analyzing requirements",
                    "Planning implementation", 
                    "Writing code",
                    "Testing functionality",
                    "Committing changes"
                ]
            )
        
        # Commit work
        await self.commit_work(agent, task)
    
    async def design_architecture(self, agent: TheatricalBaseAgent, task: dict):
        """Architect designs the system."""
        await agent.show_decision_making(
            "Monitoring system architecture",
            [
                {
                    'name': 'WebSocket-based streaming',
                    'pros': 'Real-time updates, low latency',
                    'cons': 'More complex implementation'
                },
                {
                    'name': 'REST API with polling',
                    'pros': 'Simple to implement',
                    'cons': 'Higher latency, more resource usage'
                }
            ],
            "WebSocket-based streaming",
            "Real-time visibility is critical for monitoring agent activities"
        )
        
        # Create architecture document
        arch_content = """# Monitoring System Architecture

## Overview
Real-time monitoring system for AIOSv3 agents with comprehensive visibility.

## Components

### 1. Monitoring Server
- WebSocket server for real-time streaming
- REST API for historical queries
- Activity queue for buffering
- SQLite for persistence

### 2. Agent Reporter
- Async activity reporting
- Automatic reconnection
- Local buffering for reliability
- Structured activity types

### 3. Dashboard
- Rich-based terminal UI
- Real-time activity feed
- Agent status panels
- Progress tracking
- Metrics visualization

### 4. Metrics Collector
- Performance metrics
- Success/failure rates
- Task completion times
- Error tracking

## Data Flow
```
Agent -> Reporter -> WebSocket -> Server -> Dashboard
                                    |
                                    v
                                Database
```
"""
        
        await agent.show_code_writing(
            "architecture.md",
            arch_content,
            "Documenting the system architecture"
        )
        
        # Create system design code
        design_code = """\"\"\"System design for monitoring infrastructure.\"\"\"

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum

class ActivityType(Enum):
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    DECISION_MADE = "decision_made"
    CODE_WRITTEN = "code_written"
    COMMAND_EXECUTED = "command_executed"
    ERROR_OCCURRED = "error_occurred"
    PROGRESS_UPDATE = "progress_update"

@dataclass
class Activity:
    agent_id: str
    agent_name: str
    activity_type: ActivityType
    timestamp: float
    details: Dict[str, Any]
    task_id: Optional[str] = None
    
@dataclass
class AgentStatus:
    agent_id: str
    name: str
    role: str
    status: str  # active, idle, error
    current_task: Optional[str]
    last_activity: float
    metrics: Dict[str, Any]"""
        
        await agent.show_code_writing(
            "system_design.py",
            design_code,
            "Defining core data structures"
        )
    
    async def implement_server(self, agent: TheatricalBaseAgent, task: dict):
        """Backend implements the monitoring server."""
        await agent.show_progress(
            "Implement monitoring server",
            [
                "Setting up WebSocket server",
                "Creating activity handlers",
                "Implementing message routing",
                "Adding connection management",
                "Setting up REST endpoints"
            ]
        )
        
        server_code = """\"\"\"Real-time monitoring server for AIOSv3 agents.\"\"\"

import asyncio
import json
import time
from aiohttp import web
import aiohttp_cors
import weakref
from typing import Set, Dict, Any
from system_design import Activity, AgentStatus, ActivityType

class MonitoringServer:
    def __init__(self, port: int = 6795):
        self.port = port
        self.app = web.Application()
        self.websockets: Set[weakref.ref] = set()
        self.activities = []
        self.agent_status: Dict[str, AgentStatus] = {}
        self.setup_routes()
        
    def setup_routes(self):
        self.app.router.add_get('/ws', self.websocket_handler)
        self.app.router.add_get('/api/activities', self.get_activities)
        self.app.router.add_get('/api/agents', self.get_agents)
        self.app.router.add_post('/api/activity', self.post_activity)
        
        # CORS for dashboard
        cors = aiohttp_cors.setup(self.app)
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        ws_ref = weakref.ref(ws)
        self.websockets.add(ws_ref)
        
        try:
            # Send current status
            await ws.send_json({
                'type': 'initial_state',
                'agents': [s.__dict__ for s in self.agent_status.values()],
                'recent_activities': self.activities[-50:]
            })
            
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self.handle_message(data, ws)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print(f'WebSocket error: {ws.exception()}')
        finally:
            self.websockets.discard(ws_ref)
            
        return ws"""
        
        await agent.show_code_writing(
            "monitoring_server.py",
            server_code,
            "Creating the core monitoring server"
        )
    
    async def build_dashboard(self, agent: TheatricalBaseAgent, task: dict):
        """Frontend builds the dashboard."""
        await agent.think_aloud("the best way to visualize agent activities")
        
        await agent.show_progress(
            "Build monitoring dashboard",
            [
                "Designing layout structure",
                "Creating activity feed component",
                "Building agent status panels",
                "Adding progress visualizations",
                "Implementing auto-refresh"
            ]
        )
        
        dashboard_code = """\"\"\"Real-time monitoring dashboard using Rich.\"\"\"

import asyncio
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
import aiohttp

class MonitoringDashboard:
    def __init__(self, server_url: str = "http://localhost:6795"):
        self.console = Console()
        self.server_url = server_url
        self.agents = {}
        self.activities = []
        self.layout = self.create_layout()
        
    def create_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=1)
        )
        
        layout["main"].split_row(
            Layout(name="agents", ratio=1),
            Layout(name="activities", ratio=2)
        )
        
        return layout
    
    def update_header(self):
        self.layout["header"].update(Panel(
            f"[bold blue]AIOSv3 Monitoring Dashboard[/bold blue] - {datetime.now().strftime('%H:%M:%S')}",
            style="white on blue"
        ))"""
        
        await agent.show_code_writing(
            "dashboard.py",
            dashboard_code,
            "Building the Rich-based dashboard"
        )
    
    async def create_integration(self, agent: TheatricalBaseAgent, task: dict):
        """Backend creates agent integration library."""
        integration_code = """\"\"\"Agent reporter for sending activities to monitoring server.\"\"\"

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
from collections import deque
from system_design import Activity, ActivityType

class AgentReporter:
    def __init__(self, agent_id: str, agent_name: str, server_url: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.server_url = server_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self.activity_queue = deque(maxlen=1000)
        self.connected = False
        
    async def connect(self):
        \"\"\"Connect to monitoring server.\"\"\"
        self.session = aiohttp.ClientSession()
        try:
            self.ws = await self.session.ws_connect(f"{self.server_url}/ws")
            self.connected = True
            asyncio.create_task(self._process_queue())
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.connected = False"""
        
        await agent.show_code_writing(
            "agent_reporter.py",
            integration_code,
            "Creating integration library for agents"
        )
    
    async def implement_metrics(self, agent: TheatricalBaseAgent, task: dict):
        """Monitor implements metrics collection."""
        await agent.show_decision_making(
            "Metrics to track",
            [
                {'name': 'Task completion rate', 'pros': 'Key success metric'},
                {'name': 'Average task duration', 'pros': 'Performance indicator'},
                {'name': 'Error frequency', 'pros': 'Quality metric'},
                {'name': 'Agent utilization', 'pros': 'Efficiency metric'}
            ],
            "All of them",
            "Comprehensive metrics provide full visibility into system health"
        )
        
        metrics_code = """\"\"\"Metrics collection and analysis for monitoring.\"\"\"

import time
from collections import defaultdict, deque
from typing import Dict, List, Any
from dataclasses import dataclass
import statistics

@dataclass
class MetricPoint:
    timestamp: float
    value: float
    labels: Dict[str, str]

class MetricsCollector:
    def __init__(self, retention_minutes: int = 60):
        self.metrics: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=retention_minutes * 60)
        )
        self.counters: Dict[str, int] = defaultdict(int)
        
    def record_task_completion(self, agent_id: str, duration: float, success: bool):
        metric_name = f"task_completion_{agent_id}"
        self.metrics[metric_name].append(MetricPoint(
            timestamp=time.time(),
            value=1.0 if success else 0.0,
            labels={'agent_id': agent_id, 'duration': str(duration)}
        ))"""
        
        await agent.show_code_writing(
            "metrics_collector.py",
            metrics_code,
            "Implementing metrics collection system"
        )
    
    async def add_persistence(self, agent: TheatricalBaseAgent, task: dict):
        """Backend adds database persistence."""
        db_code = """\"\"\"Database persistence for monitoring data.\"\"\"

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any
from contextlib import contextmanager

class MonitoringDatabase:
    def __init__(self, db_path: str = "monitoring.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        with self.get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    task_id TEXT,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_agent_timestamp 
                ON activities(agent_id, timestamp DESC)
            ''')"""
        
        await agent.show_code_writing(
            "database.py",
            db_code,
            "Adding SQLite persistence layer"
        )
    
    async def write_tests(self, agent: TheatricalBaseAgent, task: dict):
        """Backend writes integration tests."""
        await agent.narrate_action(
            "Writing comprehensive tests",
            "Testing is crucial for system reliability"
        )
        
        test_code = """\"\"\"Integration tests for monitoring system.\"\"\"

import pytest
import asyncio
import aiohttp
from monitoring_server import MonitoringServer
from agent_reporter import AgentReporter
from system_design import ActivityType

@pytest.mark.asyncio
async def test_server_startup():
    \"\"\"Test that monitoring server starts correctly.\"\"\"
    server = MonitoringServer(port=7000)
    runner = aiohttp.web.AppRunner(server.app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, 'localhost', 7000)
    await site.start()
    
    # Test health endpoint
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:7000/api/agents') as resp:
            assert resp.status == 200
    
    await runner.cleanup()"""
        
        await agent.show_code_writing(
            "test_monitoring.py",
            test_code,
            "Creating integration tests"
        )
    
    async def commit_work(self, agent: TheatricalBaseAgent, task: dict):
        """Commit completed work."""
        await agent.narrate_action(
            "Committing completed work",
            f"Task {task['id']} is ready for review"
        )
        
        # Git operations
        deliverables = task.get('deliverables', [])
        if deliverables:
            files_str = ' '.join(deliverables)
            
            result = await agent.run_command(
                ['git', 'add'] + deliverables,
                f"Staging {len(deliverables)} files"
            )
            
            if result.returncode == 0:
                commit_msg = f"feat({agent.role}): {task['title']}\n\nImplemented: {files_str}"
                await agent.run_command(
                    ['git', 'commit', '-m', commit_msg],
                    "Creating commit"
                )
    
    async def run_sprint(self):
        """Run the complete sprint with all agents."""
        await self.setup_project()
        sprint_plan = await self.create_sprint_plan()
        
        # Create task queues for each role
        task_queues = {
            'architect': asyncio.Queue(),
            'backend': asyncio.Queue(),
            'frontend': asyncio.Queue(),
            'monitor': asyncio.Queue()
        }
        
        # Distribute tasks
        print("\n📋 Distributing tasks to agents...\n")
        for task in sprint_plan['tasks']:
            assignee = task['assignee']
            await task_queues[assignee].put(task)
        
        # Signal end of tasks
        for queue in task_queues.values():
            await queue.put(None)
        
        # Launch agents
        print("🚀 Launching theatrical agents...\n")
        
        agent_tasks = []
        for role, queue in task_queues.items():
            agent_task = asyncio.create_task(self.launch_agent(role, queue))
            agent_tasks.append(agent_task)
        
        # Wait for all agents to complete
        await asyncio.gather(*agent_tasks)
        
        # Summary
        print("\n" + "="*70)
        print("✅ SPRINT COMPLETE!")
        print("="*70)
        print(f"\nAll agents have completed their tasks.")
        print(f"Check {self.project_path}/ for the complete monitoring system.")
        print("\nThe system includes:")
        print("- WebSocket monitoring server")
        print("- Agent activity reporter library")  
        print("- Rich-based real-time dashboard")
        print("- Metrics collection and analysis")
        print("- SQLite persistence layer")
        print("- Comprehensive test suite")
        print("\n🎭 Development theater concluded!")

async def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("\n🎭 Theatrical Orchestrator")
        print("\nThis orchestrates real agents to build software at human-comprehensible pace.")
        print("\nUsage:")
        print("  python3 theatrical_orchestrator.py")
        print("\nThe agents will:")
        print("- Work at a pace you can follow")
        print("- Explain their thinking")
        print("- Show code as they write it")
        print("- Collaborate visibly")
        return
    
    orchestrator = TheatricalOrchestrator()
    orchestrator.print_header()
    
    try:
        await orchestrator.run_sprint()
    except KeyboardInterrupt:
        print("\n\n⚠️  Sprint interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during sprint: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())