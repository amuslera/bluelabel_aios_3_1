#!/usr/bin/env python3
"""
Launch Control Center Sprint - Sprint 1.6

This launcher coordinates the complete development and review cycle for the
control center project, integrating:
1. Task orchestration with specialized agents
2. PR workflow with feature branches
3. Unified review process
4. Human approval gates
5. Continuous integration

Usage:
    python launch_control_center_sprint.py [--fast] [--review-only]
"""

import asyncio
import subprocess
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import our components
from theatrical_base_agent import TheatricalBaseAgent, create_theatrical_agent
from unified_review_process import UnifiedReviewProcess, PRInfo

# Configuration
PROJECT_PATH = "control_center_project"
SPRINT_NAME = "Sprint 1.6 - Unified Control Center"
COLLABORATION_SERVER = "ws://localhost:8765"


class ControlCenterSprintOrchestrator:
    """Orchestrates Sprint 1.6 for the control center project."""
    
    def __init__(self, fast_mode: bool = False, review_only: bool = False):
        self.project_path = PROJECT_PATH
        self.fast_mode = fast_mode
        self.review_only = review_only
        self.agents = {}
        self.tasks_completed = []
        self.prs_created = []
        
        # Pacing for visibility
        self.pacing_multiplier = 0.3 if fast_mode else 1.0
        
    def print_sprint_header(self):
        """Print sprint header."""
        print("\n" + "="*80)
        print("🚀 CONTROL CENTER SPRINT 1.6 - UNIFIED DEVELOPMENT & REVIEW")
        print("="*80)
        print(f"Sprint: {SPRINT_NAME}")
        print(f"Project: {self.project_path}/")
        print(f"Mode: {'Fast' if self.fast_mode else 'Normal'} {'(Review Only)' if self.review_only else ''}")
        print("="*80)
        
        if not self.review_only:
            print("\nWhat will happen:")
            print("1. 🏗️  Initialize project structure")
            print("2. 🤖 Launch specialized agents (Frontend, Backend, Integration)")
            print("3. 📋 Assign tasks based on expertise")
            print("4. 💻 Agents develop features on feature branches")
            print("5. 🔄 Create PRs when work is complete")
            print("6. 🔍 AI reviews code quality")
            print("7. 👤 Human approves/requests changes")
            print("8. ✅ Merge approved PRs to main")
            print("9. 📊 Show sprint summary")
        else:
            print("\nReview Mode: Will only review existing PRs")
        
        print("="*80 + "\n")
    
    async def setup_project(self):
        """Initialize project structure with git."""
        if self.review_only:
            return
            
        print("🔧 Setting up project structure...")
        
        # Create project directory
        os.makedirs(self.project_path, exist_ok=True)
        
        # Initialize git if needed
        if not os.path.exists(os.path.join(self.project_path, '.git')):
            subprocess.run(['git', 'init'], cwd=self.project_path, capture_output=True)
            
            # Configure git
            subprocess.run(['git', 'config', 'user.email', 'sprint@aiosv3.ai'], 
                         cwd=self.project_path, capture_output=True)
            subprocess.run(['git', 'config', 'user.name', 'Sprint 1.6 Orchestrator'], 
                         cwd=self.project_path, capture_output=True)
            
            # Create initial structure
            self._create_initial_structure()
            
            # Initial commit
            subprocess.run(['git', 'add', '.'], cwd=self.project_path)
            subprocess.run(['git', 'commit', '-m', 'Initial project structure for Sprint 1.6'], 
                         cwd=self.project_path, capture_output=True)
        
        print("✅ Project structure ready\n")
    
    def _create_initial_structure(self):
        """Create initial project structure."""
        # README
        readme = f"""# Control Center - Sprint 1.6

Unified control center for AIOSv3 agent orchestration.

## Features
- Real-time agent monitoring
- Task assignment and tracking
- PR review interface
- System metrics dashboard

## Architecture
- Frontend: Textual-based TUI
- Backend: FastAPI + WebSockets
- Integration: Unified launcher

## Development Process
All changes go through PR review process with AI + Human approval.
"""
        with open(os.path.join(self.project_path, 'README.md'), 'w') as f:
            f.write(readme)
        
        # Create directories
        for dir_name in ['src', 'tests', 'ui', 'api', 'config']:
            os.makedirs(os.path.join(self.project_path, dir_name), exist_ok=True)
        
        # Basic config
        config = {
            "sprint_version": "1.6",
            "api_port": 8000,
            "websocket_port": 8765,
            "monitoring_port": 6795
        }
        with open(os.path.join(self.project_path, 'config', 'settings.json'), 'w') as f:
            json.dump(config, f, indent=2)
    
    async def create_agents(self):
        """Create specialized agents for the sprint."""
        if self.review_only:
            return
            
        print("🤖 Creating specialized agents...\n")
        
        # Frontend Agent - Emma
        frontend_agent = create_theatrical_agent(
            'frontend',
            ['ui_design', 'user_experience', 'textual_framework'],
            {'model': 'gpt-4', 'temperature': 0.7}
        )
        frontend_agent.set_theatrical_mode(True, pacing_multiplier=self.pacing_multiplier)
        self.agents['frontend'] = frontend_agent
        
        await frontend_agent.narrate_action(
            "Emma here, Frontend Developer!",
            "I'll build the Textual-based control center UI with intuitive interactions"
        )
        
        # Backend Agent - Marcus
        backend_agent = create_theatrical_agent(
            'backend',
            ['api_design', 'websockets', 'data_management'],
            {'model': 'gpt-4', 'temperature': 0.7}
        )
        backend_agent.set_theatrical_mode(True, pacing_multiplier=self.pacing_multiplier)
        self.agents['backend'] = backend_agent
        
        await backend_agent.narrate_action(
            "Marcus here, Backend Developer!",
            "I'll implement the API and WebSocket server for real-time communication"
        )
        
        # Integration Agent - Alex
        integration_agent = create_theatrical_agent(
            'integration',
            ['system_integration', 'configuration', 'deployment'],
            {'model': 'gpt-4', 'temperature': 0.7}
        )
        integration_agent.set_theatrical_mode(True, pacing_multiplier=self.pacing_multiplier)
        self.agents['integration'] = integration_agent
        
        await integration_agent.narrate_action(
            "Alex here, Integration Engineer!",
            "I'll wire everything together and ensure smooth deployment"
        )
        
        print("\n✅ All agents ready for Sprint 1.6!\n")
    
    async def define_sprint_tasks(self) -> List[Dict[str, Any]]:
        """Define tasks for the sprint."""
        tasks = [
            {
                'id': 'UI-001',
                'title': 'Build control center TUI with Textual',
                'assignee': 'frontend',
                'description': 'Create the main control center interface with grid layout for monitoring, tasks, and PR reviews',
                'branch': 'feature/control-center-ui',
                'deliverables': ['ui/control_center.py', 'ui/ui_components.py', 'ui/styles.css']
            },
            {
                'id': 'API-001',
                'title': 'Implement WebSocket server and REST API',
                'assignee': 'backend',
                'description': 'Build WebSocket server for real-time updates and REST API for data operations',
                'branch': 'feature/backend-api',
                'deliverables': ['api/websocket_handler.py', 'api/api_endpoints.py', 'api/models.py']
            },
            {
                'id': 'INT-001',
                'title': 'Integrate components and create launcher',
                'assignee': 'integration',
                'description': 'Wire frontend and backend together, create main entry point and configuration',
                'branch': 'feature/integration',
                'deliverables': ['src/main.py', 'config/config.py', 'requirements.txt'],
                'dependencies': ['UI-001', 'API-001']
            }
        ]
        
        return tasks
    
    async def execute_task(self, task: Dict[str, Any]):
        """Execute a single task with an agent."""
        agent = self.agents[task['assignee']]
        
        print(f"\n{'='*60}")
        print(f"📋 TASK: {task['title']}")
        print(f"Assigned to: {agent.theatrical_name}")
        print(f"{'='*60}\n")
        
        # Create feature branch
        branch_name = task['branch']
        
        # Clean up any existing branch
        subprocess.run(['git', 'branch', '-D', branch_name], 
                     cwd=self.project_path, capture_output=True)
        
        subprocess.run(['git', 'checkout', '-b', branch_name],
                      cwd=self.project_path, capture_output=True)
        
        await agent.narrate_action(
            f"Starting work on: {task['title']}",
            f"Creating feature branch: {branch_name}"
        )
        
        # Simulate development work based on role
        if task['assignee'] == 'frontend':
            await self._develop_frontend(agent, task)
        elif task['assignee'] == 'backend':
            await self._develop_backend(agent, task)
        elif task['assignee'] == 'integration':
            await self._develop_integration(agent, task)
        
        # Commit work
        await agent.narrate_action(
            "Committing completed work",
            "All deliverables ready for review"
        )
        
        subprocess.run(['git', 'add', '.'], cwd=self.project_path)
        
        commit_msg = f"feat: {task['title']}\n\nImplemented by {agent.theatrical_name}\nTask ID: {task['id']}"
        subprocess.run(['git', 'commit', '-m', commit_msg],
                      cwd=self.project_path, capture_output=True)
        
        # Create PR
        pr_number = len(self.prs_created) + 1
        pr_info = PRInfo(
            number=pr_number,
            title=task['title'],
            branch=branch_name,
            author=agent.theatrical_name,
            agent_role=task['assignee'],
            description=task['description'],
            created_at=datetime.now().isoformat(),
            files_changed=task['deliverables'],
            task_id=task['id'],
            dependencies=task.get('dependencies', [])
        )
        
        # Save PR info
        pr_file = os.path.join(self.project_path, f'.pr_info_{pr_number}.json')
        with open(pr_file, 'w') as f:
            json.dump({
                'number': pr_info.number,
                'title': pr_info.title,
                'branch': pr_info.branch,
                'author': pr_info.author,
                'agent_role': pr_info.agent_role,
                'description': pr_info.description,
                'created_at': pr_info.created_at,
                'files_changed': pr_info.files_changed,
                'task_id': pr_info.task_id,
                'dependencies': pr_info.dependencies
            }, f, indent=2)
        
        self.prs_created.append(pr_info)
        
        await agent.narrate_action(
            f"📤 Pull Request #{pr_number} created",
            "Ready for AI and human review"
        )
        
        # Return to main branch
        subprocess.run(['git', 'checkout', 'main'],
                      cwd=self.project_path, capture_output=True)
        
        self.tasks_completed.append(task['id'])
    
    async def _develop_frontend(self, agent: TheatricalBaseAgent, task: Dict[str, Any]):
        """Frontend development simulation."""
        await agent.think_aloud("the best UI layout for the control center")
        
        await agent.show_progress(
            "Building control center UI",
            [
                "Setting up Textual app structure",
                "Creating grid layout components",
                "Implementing agent monitoring widget",
                "Adding task management interface",
                "Building PR review panel",
                "Styling with CSS"
            ]
        )
        
        # Create UI files
        control_center_code = '''"""
Control Center TUI - Main Application
"""

from textual.app import App, ComposeResult
from textual.containers import Grid, Vertical, Horizontal
from textual.widgets import Header, Footer, Button, DataTable, Static
from textual.binding import Binding

from ui_components import AgentMonitor, TaskManager, PRReviewer, MetricsDashboard


class ControlCenter(App):
    """Main control center application."""
    
    CSS_PATH = "styles.css"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("t", "focus_tasks", "Tasks"),
        Binding("a", "focus_agents", "Agents"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create application layout."""
        yield Header()
        
        with Grid(id="main-grid"):
            yield AgentMonitor(id="agent-monitor")
            yield MetricsDashboard(id="metrics")
            yield TaskManager(id="task-manager")
            yield PRReviewer(id="pr-reviewer")
            
        yield Footer()
    
    def action_refresh(self) -> None:
        """Refresh all components."""
        self.query_one("#agent-monitor").refresh()
        self.query_one("#metrics").refresh()
        self.query_one("#task-manager").refresh()
        self.query_one("#pr-reviewer").refresh()


if __name__ == "__main__":
    app = ControlCenter()
    app.run()
'''
        
        ui_components_code = '''"""
UI Components for Control Center
"""

from textual.widgets import Static, DataTable, Button
from textual.containers import Vertical, Horizontal
import asyncio


class AgentMonitor(Vertical):
    """Monitor active agents and their status."""
    
    def compose(self):
        yield Static("🤖 Agent Orchestra", classes="section-title")
        
        self.table = DataTable()
        self.table.add_columns("Status", "Agent", "Role", "Current Task", "Progress")
        yield self.table
        
        # Sample data
        self.table.add_row("🟢", "Emma", "Frontend", "Building UI", "75%")
        self.table.add_row("🟢", "Marcus", "Backend", "API endpoints", "60%")
        self.table.add_row("🟡", "Alex", "Integration", "Waiting", "0%")
    
    def refresh(self):
        """Refresh agent data."""
        # In real implementation, fetch from WebSocket
        pass


class TaskManager(Vertical):
    """Manage and assign tasks."""
    
    def compose(self):
        yield Static("📋 Task Queue", classes="section-title")
        
        self.task_list = DataTable()
        self.task_list.add_columns("ID", "Task", "Assigned", "Status")
        yield self.task_list
        
        with Horizontal():
            yield Button("Assign Task", id="assign-btn")
            yield Button("View Details", id="details-btn")


class PRReviewer(Vertical):
    """Review pull requests."""
    
    def compose(self):
        yield Static("🔍 PR Review", classes="section-title")
        
        self.pr_list = DataTable()
        self.pr_list.add_columns("PR", "Author", "Title", "Status")
        yield self.pr_list
        
        with Horizontal():
            yield Button("Review", variant="primary", id="review-btn")
            yield Button("Approve", variant="success", id="approve-btn")
            yield Button("Request Changes", variant="warning", id="changes-btn")


class MetricsDashboard(Vertical):
    """Display system metrics."""
    
    def compose(self):
        yield Static("📊 Sprint Metrics", classes="section-title")
        yield Static("Tasks: 3/10 completed")
        yield Static("PRs: 2 pending review")
        yield Static("Agents: 3 active")
        yield Static("Sprint Progress: 30%")
'''
        
        styles_css = '''
/* Control Center Styles */

#main-grid {
    grid-size: 2 2;
    grid-gutter: 1;
    margin: 1;
}

.section-title {
    text-style: bold;
    color: cyan;
    margin-bottom: 1;
}

AgentMonitor {
    border: solid cyan;
    padding: 1;
}

TaskManager {
    border: solid green;
    padding: 1;
}

PRReviewer {
    border: solid yellow;
    padding: 1;
}

MetricsDashboard {
    border: solid magenta;
    padding: 1;
}

DataTable {
    height: 10;
}
'''
        
        # Write files
        os.makedirs(os.path.join(self.project_path, 'ui'), exist_ok=True)
        
        with open(os.path.join(self.project_path, 'ui', 'control_center.py'), 'w') as f:
            f.write(control_center_code)
            
        with open(os.path.join(self.project_path, 'ui', 'ui_components.py'), 'w') as f:
            f.write(ui_components_code)
            
        with open(os.path.join(self.project_path, 'ui', 'styles.css'), 'w') as f:
            f.write(styles_css)
        
        await agent.show_code_writing(
            "ui/control_center.py",
            control_center_code[:500] + "...",  # Show snippet
            "Creating main control center application"
        )
    
    async def _develop_backend(self, agent: TheatricalBaseAgent, task: Dict[str, Any]):
        """Backend development simulation."""
        await agent.think_aloud("the API structure for real-time updates")
        
        await agent.show_progress(
            "Building backend services",
            [
                "Setting up FastAPI application",
                "Implementing WebSocket handler",
                "Creating data models",
                "Adding API endpoints",
                "Implementing authentication",
                "Setting up CORS"
            ]
        )
        
        # Create API files
        websocket_code = '''"""
WebSocket handler for real-time communication
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio


class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        
    async def broadcast(self, message: dict):
        """Send message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections."""
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Process different message types
            if data["type"] == "agent_update":
                await manager.broadcast({
                    "type": "agent_status",
                    "data": data["payload"]
                })
            elif data["type"] == "task_complete":
                await manager.broadcast({
                    "type": "task_update",
                    "data": data["payload"]
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
'''
        
        api_endpoints_code = '''"""
REST API endpoints for control center
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Control Center API")


class Agent(BaseModel):
    id: str
    name: str
    role: str
    status: str
    current_task: Optional[str]
    
    
class Task(BaseModel):
    id: str
    title: str
    description: str
    assigned_to: Optional[str]
    status: str
    created_at: datetime
    

@app.get("/agents")
async def get_agents() -> List[Agent]:
    """Get all active agents."""
    # In real implementation, fetch from database
    return [
        Agent(id="1", name="Emma", role="frontend", status="active", current_task="UI-001"),
        Agent(id="2", name="Marcus", role="backend", status="active", current_task="API-001"),
        Agent(id="3", name="Alex", role="integration", status="idle", current_task=None)
    ]


@app.get("/tasks")
async def get_tasks() -> List[Task]:
    """Get all tasks."""
    return []


@app.post("/tasks/{task_id}/assign")
async def assign_task(task_id: str, agent_id: str):
    """Assign task to agent."""
    return {"status": "assigned", "task_id": task_id, "agent_id": agent_id}


@app.get("/metrics")
async def get_metrics():
    """Get system metrics."""
    return {
        "agents_active": 3,
        "tasks_completed": 5,
        "tasks_pending": 10,
        "sprint_progress": 33.3
    }
'''
        
        # Write files
        os.makedirs(os.path.join(self.project_path, 'api'), exist_ok=True)
        
        with open(os.path.join(self.project_path, 'api', 'websocket_handler.py'), 'w') as f:
            f.write(websocket_code)
            
        with open(os.path.join(self.project_path, 'api', 'api_endpoints.py'), 'w') as f:
            f.write(api_endpoints_code)
            
        with open(os.path.join(self.project_path, 'api', 'models.py'), 'w') as f:
            f.write('# Data models will go here\n')
        
        await agent.show_code_writing(
            "api/websocket_handler.py",
            websocket_code[:400] + "...",
            "Implementing WebSocket for real-time updates"
        )
    
    async def _develop_integration(self, agent: TheatricalBaseAgent, task: Dict[str, Any]):
        """Integration development simulation."""
        await agent.think_aloud("how to wire all components together")
        
        await agent.show_progress(
            "Integrating components",
            [
                "Creating main entry point",
                "Configuring services",
                "Setting up requirements",
                "Adding startup scripts",
                "Testing integration"
            ]
        )
        
        # Create integration files
        main_code = '''"""
Control Center - Main Entry Point
"""

import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading

# Import our components
from api.api_endpoints import app as api_app
from api.websocket_handler import websocket_endpoint


# Configure CORS
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add WebSocket route
api_app.add_websocket_route("/ws", websocket_endpoint)


def run_api():
    """Run the API server."""
    uvicorn.run(api_app, host="0.0.0.0", port=8000)


def run_tui():
    """Run the TUI."""
    from ui.control_center import ControlCenter
    app = ControlCenter()
    app.run()


def main():
    """Main entry point."""
    print("🚀 Starting Control Center...")
    
    # Run API in background thread
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    print("✅ API running on http://localhost:8000")
    print("✅ WebSocket available on ws://localhost:8000/ws")
    
    # Run TUI in main thread
    print("🖥️  Launching TUI...")
    run_tui()


if __name__ == "__main__":
    main()
'''
        
        config_code = '''"""
Configuration for Control Center
"""

import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    websocket_url: str = "ws://localhost:8000/ws"
    monitoring_server: str = "http://localhost:6795"
    
    class Config:
        env_file = ".env"


settings = Settings()
'''
        
        requirements_txt = '''fastapi==0.104.1
uvicorn==0.24.0
websockets==12.0
textual==0.41.0
pydantic==2.4.2
python-dotenv==1.0.0
aiohttp==3.8.6
rich==13.6.0
pytest==7.4.3
pytest-asyncio==0.21.1
'''
        
        # Write files
        os.makedirs(os.path.join(self.project_path, 'src'), exist_ok=True)
        os.makedirs(os.path.join(self.project_path, 'config'), exist_ok=True)
        
        with open(os.path.join(self.project_path, 'src', 'main.py'), 'w') as f:
            f.write(main_code)
            
        with open(os.path.join(self.project_path, 'config', 'config.py'), 'w') as f:
            f.write(config_code)
            
        with open(os.path.join(self.project_path, 'requirements.txt'), 'w') as f:
            f.write(requirements_txt)
        
        await agent.show_code_writing(
            "src/main.py",
            main_code[:400] + "...",
            "Creating unified launcher"
        )
    
    async def run_sprint(self):
        """Run the complete sprint."""
        self.print_sprint_header()
        
        if not self.review_only:
            # Setup
            await self.setup_project()
            await self.create_agents()
            
            # Define and execute tasks
            tasks = await self.define_sprint_tasks()
            
            print(f"\n📋 Sprint has {len(tasks)} tasks to complete\n")
            
            for task in tasks:
                # Check dependencies
                if task.get('dependencies'):
                    pending = [d for d in task['dependencies'] if d not in self.tasks_completed]
                    if pending:
                        print(f"⏸️  Skipping {task['id']} - waiting for: {pending}")
                        continue
                
                await self.execute_task(task)
                
                # Brief pause between tasks
                if self.fast_mode:
                    await asyncio.sleep(1)
                else:
                    await asyncio.sleep(3)
            
            print("\n✅ All development tasks completed!")
            print(f"📤 Created {len(self.prs_created)} pull requests\n")
        
        # Review phase
        print("\n" + "="*80)
        print("🔍 ENTERING REVIEW PHASE")
        print("="*80 + "\n")
        
        input("Press Enter to start the review process...")
        
        # Launch unified review process
        reviewer = UnifiedReviewProcess(self.project_path)
        await reviewer.run_review_session()
        
        # Sprint summary
        self.show_sprint_summary()
    
    def show_sprint_summary(self):
        """Show sprint summary."""
        print("\n" + "="*80)
        print("📊 SPRINT 1.6 SUMMARY")
        print("="*80)
        
        print(f"\nTasks Completed: {len(self.tasks_completed)}")
        print(f"PRs Created: {len(self.prs_created)}")
        
        # Check merged PRs
        result = subprocess.run(
            ['git', 'log', '--oneline', '-n', '10'],
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            commits = result.stdout.strip().split('\n')
            merge_commits = [c for c in commits if 'Merge PR' in c]
            print(f"PRs Merged: {len(merge_commits)}")
        
        print("\n✅ Sprint 1.6 Complete!")
        print("\nNext Steps:")
        print("1. Run the control center: python src/main.py")
        print("2. Access API docs: http://localhost:8000/docs")
        print("3. Monitor WebSocket: ws://localhost:8000/ws")
        print("="*80)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Launch Control Center Sprint 1.6')
    parser.add_argument('--fast', action='store_true', help='Run in fast mode')
    parser.add_argument('--review-only', action='store_true', help='Only run review process')
    
    args = parser.parse_args()
    
    try:
        orchestrator = ControlCenterSprintOrchestrator(
            fast_mode=args.fast,
            review_only=args.review_only
        )
        await orchestrator.run_sprint()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Sprint interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())