#!/usr/bin/env python3
"""
Single Agent PR Workflow Test - Phase 1

Tests one agent (Backend) building monitoring server with PR workflow.
Includes human review terminal and faster theatrical pacing.
"""

import asyncio
import subprocess
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Import our theatrical base agent with adjusted speed
from theatrical_base_agent import TheatricalBaseAgent, create_theatrical_agent

# Configuration
PROJECT_PATH = "monitoring_system"
GITHUB_REPO = None  # Will use local git for now

class SingleAgentOrchestrator:
    """Orchestrates single agent with PR workflow."""
    
    def __init__(self):
        self.project_path = PROJECT_PATH
        self.agent = None
        self.current_branch = "main"
        self.pr_created = False
        
    async def setup_project(self):
        """Set up project with proper git structure."""
        print("🔧 Setting up project structure...")
        
        # Create project directory
        os.makedirs(self.project_path, exist_ok=True)
        
        # Initialize git if needed
        git_path = os.path.join(self.project_path, '.git')
        if not os.path.exists(git_path):
            subprocess.run(['git', 'init'], cwd=self.project_path, capture_output=True)
            
            # Configure git
            subprocess.run(['git', 'config', 'user.email', 'orchestrator@aiosv3.ai'], 
                         cwd=self.project_path, capture_output=True)
            subprocess.run(['git', 'config', 'user.name', 'AIOSv3 Orchestrator'], 
                         cwd=self.project_path, capture_output=True)
            
            # Create initial structure
            readme = """# Monitoring System

Real-time monitoring for AIOSv3 agents.

## Architecture
- WebSocket server for real-time streaming
- Activity storage with querying
- REST API for historical data
- Agent client library

## Development Process
All changes must be:
1. Developed on feature branches
2. Submitted via PR
3. Reviewed by human + AI
4. Approved before merge
"""
            
            with open(os.path.join(self.project_path, 'README.md'), 'w') as f:
                f.write(readme)
            
            # Create empty directories
            for dir_name in ['src', 'tests', 'docs']:
                os.makedirs(os.path.join(self.project_path, dir_name), exist_ok=True)
            
            # Initial commit
            subprocess.run(['git', 'add', '.'], cwd=self.project_path)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], 
                         cwd=self.project_path, capture_output=True)
        
        print("✅ Project structure ready\n")
        
    async def create_backend_agent(self):
        """Create backend agent with adjusted theatrical speed."""
        print("🤖 Creating Backend Agent...")
        
        # Create agent
        self.agent = create_theatrical_agent(
            'backend',
            ['coding', 'api_design', 'testing'],
            {'model': 'gpt-4', 'temperature': 0.7}
        )
        
        # Adjust speed - 50% faster than demo
        self.agent.set_theatrical_mode(True, pacing_multiplier=0.5)
        
        # Introduce agent
        await self.agent.narrate_action(
            f"Hello! I'm {self.agent.theatrical_name}, Backend Developer",
            "I'll implement the monitoring server with WebSocket support"
        )
        
        print("✅ Agent ready\n")
        
    async def assign_task(self):
        """Assign monitoring server task to agent."""
        task = {
            'id': 'MON-001',
            'title': 'Implement WebSocket monitoring server',
            'description': 'Build a WebSocket server for real-time agent activity streaming with persistence',
            'requirements': [
                'WebSocket server on port 6795',
                'Handle multiple client connections',
                'Store activities in memory with overflow to disk',
                'REST API for querying historical data',
                'Graceful error handling and reconnection',
                'Basic authentication for connections'
            ],
            'deliverables': [
                'src/monitoring_server.py',
                'src/activity_store.py',
                'tests/test_monitoring.py'
            ]
        }
        
        print("📋 Assigning task to agent...\n")
        await self.agent.narrate_action(
            f"Received task: {task['title']}",
            "Let me analyze the requirements..."
        )
        
        # Create feature branch
        branch_name = 'feature/monitoring-server'
        
        # Clean up any existing branch
        subprocess.run(['git', 'branch', '-D', branch_name], 
                     cwd=self.project_path, capture_output=True)
        
        result = subprocess.run(['git', 'checkout', '-b', branch_name],
                              cwd=self.project_path, capture_output=True, text=True)
        
        if result.returncode == 0:
            await self.agent.narrate_action(
                f"Created feature branch: {branch_name}",
                "I'll work on this branch and create a PR when done"
            )
        else:
            print(f"⚠️  Error creating branch: {result.stderr}")
        
        # Execute task
        await self.implement_monitoring_server()
        
    async def implement_monitoring_server(self):
        """Agent implements the monitoring server."""
        
        # Think about approach
        await self.agent.think_aloud("the best architecture for this server")
        
        # Make architectural decisions
        await self.agent.show_decision_making(
            "Server implementation approach",
            [
                {
                    'name': 'aiohttp with WebSockets',
                    'pros': 'Battle-tested, good documentation',
                    'cons': 'Additional dependency'
                },
                {
                    'name': 'websockets library',
                    'pros': 'Lightweight, focused',
                    'cons': 'Need separate HTTP server'
                }
            ],
            "aiohttp with WebSockets",
            "We need both WebSocket and REST endpoints, aiohttp handles both"
        )
        
        # Show progress
        await self.agent.show_progress(
            "Implementing monitoring server",
            [
                "Setting up server structure",
                "Implementing WebSocket handler",
                "Adding activity storage",
                "Creating REST endpoints",
                "Writing tests",
                "Adding documentation"
            ]
        )
        
        # Write monitoring server code
        server_code = '''"""
WebSocket monitoring server for AIOSv3 agents.

Provides real-time activity streaming and historical queries.
"""

import asyncio
import json
import time
import weakref
from typing import Set, Dict, Any, Optional
from datetime import datetime
from aiohttp import web
import aiohttp_cors

class MonitoringServer:
    """Real-time monitoring server with WebSocket support."""
    
    def __init__(self, port: int = 6795):
        self.port = port
        self.app = web.Application()
        self.websockets: Set[weakref.ref] = set()
        self.activity_store = ActivityStore()
        self.setup_routes()
        self.setup_cors()
        
    def setup_routes(self):
        """Configure server routes."""
        # WebSocket endpoint
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # REST endpoints
        self.app.router.add_get('/api/health', self.health_check)
        self.app.router.add_post('/api/activities', self.post_activity)
        self.app.router.add_get('/api/activities', self.get_activities)
        self.app.router.add_get('/api/agents', self.get_agents)
        
    def setup_cors(self):
        """Configure CORS for dashboard access."""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })
        
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def websocket_handler(self, request):
        """Handle WebSocket connections."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # Store weak reference
        ws_ref = weakref.ref(ws)
        self.websockets.add(ws_ref)
        
        try:
            # Send initial state
            await ws.send_json({
                'type': 'connection',
                'status': 'connected',
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Handle messages
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self.handle_ws_message(data, ws)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print(f'WebSocket error: {ws.exception()}')
                    
        except Exception as e:
            print(f"WebSocket handler error: {e}")
        finally:
            self.websockets.discard(ws_ref)
            
        return ws
    
    async def handle_ws_message(self, data: Dict[str, Any], ws):
        """Process WebSocket messages."""
        msg_type = data.get('type')
        
        if msg_type == 'activity':
            # Store and broadcast activity
            activity = await self.activity_store.add(data['activity'])
            await self.broadcast_activity(activity)
        elif msg_type == 'ping':
            await ws.send_json({'type': 'pong'})
            
    async def broadcast_activity(self, activity: Dict[str, Any]):
        """Broadcast activity to all connected clients."""
        message = {
            'type': 'activity',
            'activity': activity
        }
        
        # Send to all connected clients
        for ws_ref in list(self.websockets):
            ws = ws_ref()
            if ws is not None:
                try:
                    await ws.send_json(message)
                except ConnectionResetError:
                    self.websockets.discard(ws_ref)
                    
    async def health_check(self, request):
        """Health check endpoint."""
        return web.json_response({
            'status': 'healthy',
            'connections': len(self.websockets),
            'activities': self.activity_store.count()
        })
    
    def run(self):
        """Start the server."""
        web.run_app(self.app, host='0.0.0.0', port=self.port)


class ActivityStore:
    """Storage for agent activities."""
    
    def __init__(self, max_memory: int = 10000):
        self.activities = []
        self.max_memory = max_memory
        self.agents = {}
        
    async def add(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Add activity to store."""
        # Add timestamp
        activity['stored_at'] = datetime.utcnow().isoformat()
        
        # Update agent info
        agent_id = activity.get('agent_id')
        if agent_id:
            self.agents[agent_id] = {
                'id': agent_id,
                'name': activity.get('agent_name', 'Unknown'),
                'last_seen': activity['stored_at']
            }
        
        # Store activity
        self.activities.append(activity)
        
        # Manage memory
        if len(self.activities) > self.max_memory:
            # TODO: Overflow to disk
            self.activities = self.activities[-self.max_memory:]
            
        return activity
    
    def count(self) -> int:
        """Get activity count."""
        return len(self.activities)


if __name__ == '__main__':
    server = MonitoringServer()
    print(f"Starting monitoring server on port {server.port}...")
    server.run()
'''
        
        await self.agent.show_code_writing(
            "src/monitoring_server.py",
            server_code,
            "Implementing the WebSocket monitoring server"
        )
        
        # Write to file
        server_path = os.path.join(self.project_path, 'src', 'monitoring_server.py')
        with open(server_path, 'w') as f:
            f.write(server_code)
        
        # Write activity store
        store_code = '''"""
Activity storage with overflow to disk.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import deque


class PersistentActivityStore:
    """Activity store with disk persistence."""
    
    def __init__(self, memory_size: int = 1000, disk_path: str = "activities.jsonl"):
        self.memory_store = deque(maxlen=memory_size)
        self.disk_path = disk_path
        self.total_count = 0
        self._load_from_disk()
        
    def _load_from_disk(self):
        """Load recent activities from disk."""
        if os.path.exists(self.disk_path):
            with open(self.disk_path, 'r') as f:
                for line in f:
                    try:
                        activity = json.loads(line)
                        self.memory_store.append(activity)
                        self.total_count += 1
                    except json.JSONDecodeError:
                        pass
                        
    def add(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Add activity to store."""
        activity['id'] = self.total_count
        activity['timestamp'] = datetime.utcnow().isoformat()
        
        # Add to memory
        self.memory_store.append(activity)
        self.total_count += 1
        
        # Persist to disk
        with open(self.disk_path, 'a') as f:
            f.write(json.dumps(activity) + '\\n')
            
        return activity
    
    def query(self, agent_id: Optional[str] = None, 
              limit: int = 100, 
              offset: int = 0) -> List[Dict[str, Any]]:
        """Query activities with filters."""
        activities = list(self.memory_store)
        
        if agent_id:
            activities = [a for a in activities if a.get('agent_id') == agent_id]
            
        return activities[offset:offset + limit]
'''
        
        await self.agent.show_code_writing(
            "src/activity_store.py",
            store_code,
            "Creating persistent activity storage"
        )
        
        store_path = os.path.join(self.project_path, 'src', 'activity_store.py')
        with open(store_path, 'w') as f:
            f.write(store_code)
        
        # Write basic tests
        test_code = '''"""
Tests for monitoring server.
"""

import pytest
import asyncio
import aiohttp
from src.monitoring_server import MonitoringServer
from src.activity_store import PersistentActivityStore


@pytest.mark.asyncio
async def test_server_health():
    """Test health check endpoint."""
    server = MonitoringServer(port=7777)
    
    async with aiohttp.ClientSession() as session:
        # Start server in background
        runner = aiohttp.web.AppRunner(server.app)
        await runner.setup()
        site = aiohttp.web.TCPSite(runner, 'localhost', 7777)
        await site.start()
        
        # Test health
        async with session.get('http://localhost:7777/api/health') as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data['status'] == 'healthy'
            
        await runner.cleanup()


def test_activity_store():
    """Test activity storage."""
    store = PersistentActivityStore()
    
    activity = {
        'agent_id': 'test_agent',
        'type': 'task_completed',
        'details': {'task': 'test'}
    }
    
    stored = store.add(activity)
    assert stored['id'] == 0
    assert 'timestamp' in stored
    
    # Query
    results = store.query(agent_id='test_agent')
    assert len(results) == 1
'''
        
        await self.agent.show_code_writing(
            "tests/test_monitoring.py",
            test_code,
            "Writing tests for the monitoring system"
        )
        
        test_path = os.path.join(self.project_path, 'tests', 'test_monitoring.py')
        with open(test_path, 'w') as f:
            f.write(test_code)
        
        # Commit work
        await self.agent.narrate_action(
            "Committing completed work",
            "I'll create a commit with all changes"
        )
        
        # Git operations
        subprocess.run(['git', 'add', '.'], cwd=self.project_path)
        
        commit_msg = """feat: Implement WebSocket monitoring server

- WebSocket server with multiple client support
- Activity storage with memory/disk overflow
- REST API for health check and queries
- CORS support for dashboard access
- Basic test coverage

Implements MON-001"""
        
        result = subprocess.run(['git', 'commit', '-m', commit_msg],
                              cwd=self.project_path, capture_output=True, text=True)
        
        if result.returncode == 0:
            await self.agent.narrate_action(
                "✅ Changes committed successfully",
                "Ready to create pull request for review"
            )
        else:
            print(f"⚠️  Commit error: {result.stderr}")
        
        # Create PR (simulated locally)
        await self.create_pull_request()
        
    async def create_pull_request(self):
        """Create a pull request for review."""
        self.pr_created = True
        
        pr_info = {
            'number': 1,
            'title': 'feat: Implement WebSocket monitoring server',
            'branch': 'feature/monitoring-server',
            'author': self.agent.theatrical_name,
            'created_at': datetime.now().isoformat(),
            'files_changed': [
                'src/monitoring_server.py',
                'src/activity_store.py',
                'tests/test_monitoring.py'
            ]
        }
        
        # Save PR info
        pr_path = os.path.join(self.project_path, '.pr_info.json')
        with open(pr_path, 'w') as f:
            json.dump(pr_info, f, indent=2)
        
        await self.agent.narrate_action(
            "📤 Pull Request created",
            f"PR #{pr_info['number']}: {pr_info['title']}"
        )
        
        await self.agent.collaborate(
            "Pull request is ready for review. I've implemented the WebSocket server with all requested features.",
            "reviewer"
        )
        
        print("\n" + "="*70)
        print("📋 PULL REQUEST READY FOR REVIEW")
        print("="*70)
        print(f"PR #{pr_info['number']}: {pr_info['title']}")
        print(f"Author: {pr_info['author']}")
        print(f"Branch: {pr_info['branch']}")
        print(f"Files: {', '.join(pr_info['files_changed'])}")
        print("="*70)
        print("\n✋ Agent work complete. Ready for review process.\n")


async def main():
    """Run single agent test."""
    print("\n" + "="*70)
    print("🚀 SINGLE AGENT PR WORKFLOW TEST - PHASE 1")
    print("="*70)
    print("Testing: Backend agent with PR workflow")
    print("Speed: 50% faster than theatrical demo")
    print("="*70 + "\n")
    
    orchestrator = SingleAgentOrchestrator()
    
    try:
        # Set up project
        await orchestrator.setup_project()
        
        # Create agent
        await orchestrator.create_backend_agent()
        
        # Assign task
        await orchestrator.assign_task()
        
        if orchestrator.pr_created:
            print("✅ Phase 1 complete!")
            print("\nNext: Run 'review_pr.py' to review and approve the PR")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())