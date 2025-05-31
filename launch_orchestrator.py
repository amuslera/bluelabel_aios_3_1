#!/usr/bin/env python3
"""
Task Orchestrator Launcher

Launch the complete Task Orchestration system that acts as the Technical Lead
coordinating between human Product Owner and specialized AI agents.
"""

import asyncio
import argparse
import logging
import os
import sys
from pathlib import Path

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from orchestration.task_orchestrator import TaskOrchestrator
from orchestration.assignment_engine import AssignmentEngine
from orchestration.progress_monitor import create_progress_monitor
from orchestration.sprint_planner import create_sprint_planner

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OrchestratorTerminal:
    """Interactive terminal for the Task Orchestrator."""
    
    def __init__(self, orchestrator: TaskOrchestrator):
        self.orchestrator = orchestrator
        self.running = True
    
    def print_banner(self):
        """Print orchestrator banner."""
        print("=" * 80)
        print("🎯 AIOSv3 TASK ORCHESTRATOR - AI TECHNICAL LEAD")
        print("=" * 80)
        print(f"Orchestrator ID: {self.orchestrator.orchestrator_id}")
        print(f"Repository: {Path.cwd()}")
        print(f"Collaboration Server: {self.orchestrator.collaboration_server}")
        print("=" * 80)
        print()
        print("🤖 I am your AI Technical Lead and will coordinate our development team.")
        print("💡 I'll help you plan sprints, assign tasks, monitor progress, and resolve blockers.")
        print()
    
    def show_help(self):
        """Show available commands."""
        print("💡 Task Orchestrator Commands:")
        print("   status               - Show current sprint and team status")
        print("   plan sprint          - Start collaborative sprint planning")
        print("   agents               - Show active agents and their status")
        print("   tasks                - Show all tasks and their status")
        print("   blockers             - Show active blockers and resolutions")
        print("   assign <task> <agent> - Manually assign task to agent")
        print("   capacity             - Show team capacity analysis")
        print("   metrics              - Show sprint progress metrics")
        print("   help                 - Show this help")
        print("   quit                 - Shutdown orchestrator")
        print()
        print("🎯 Automatic Functions:")
        print("   • Intelligent task assignment based on agent expertise")
        print("   • Real-time progress monitoring and blocker detection")
        print("   • Automatic blocker resolution or escalation")
        print("   • Sprint goal tracking and team coordination")
        print()
    
    async def run_terminal(self):
        """Run the interactive terminal."""
        self.print_banner()
        
        # Wait for orchestrator to initialize
        await asyncio.sleep(2)
        
        if not self.orchestrator.connected:
            print("❌ Failed to connect to collaboration server")
            print("💡 Make sure the collaboration server is running:")
            print("   python3 collaboration_server.py")
            return
        
        print("✅ Task Orchestrator is online and ready!")
        self.show_help()
        
        try:
            while self.running and self.orchestrator.connected:
                try:
                    # Get user input
                    user_input = await asyncio.get_event_loop().run_in_executor(
                        None, input, "\norchestrator> "
                    )
                    
                    if not user_input.strip():
                        continue
                    
                    await self.handle_command(user_input.strip())
                
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
                except Exception as e:
                    logger.error(f"Error in terminal: {e}")
        
        finally:
            print("\n👋 Task Orchestrator shutting down...")
            if self.orchestrator.websocket:
                await self.orchestrator.websocket.close()
    
    async def handle_command(self, command_line: str):
        """Handle user commands."""
        parts = command_line.split(" ", 2)
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command == "quit":
            self.running = False
            
        elif command == "help":
            self.show_help()
            
        elif command == "status":
            await self.show_status()
            
        elif command == "plan" and len(args) > 0 and args[0] == "sprint":
            await self.start_sprint_planning()
            
        elif command == "agents":
            await self.show_agents()
            
        elif command == "tasks":
            await self.show_tasks()
            
        elif command == "blockers":
            await self.show_blockers()
            
        elif command == "capacity":
            await self.show_capacity()
            
        elif command == "metrics":
            await self.show_metrics()
            
        elif command == "assign" and len(args) >= 2:
            await self.manual_assign(args[0], args[1])
            
        else:
            print(f"Unknown command: {command}. Type 'help' for available commands.")
    
    async def show_status(self):
        """Show current orchestrator status."""
        print("\n📊 ORCHESTRATOR STATUS")
        print("=" * 50)
        
        # Current sprint
        if self.orchestrator.current_sprint:
            print(f"🎯 Active Sprint: {self.orchestrator.current_sprint}")
        else:
            print("🎯 No active sprint")
        
        # Team status
        print(f"\n👥 Team: {len(self.orchestrator.agents)} active agents")
        for agent_id, agent in self.orchestrator.agents.items():
            status_icon = "🟢" if agent.availability else "🔴"
            workload = f"{agent.current_workload}/{agent.max_workload}"
            print(f"   {status_icon} {agent.name} ({agent.role}) - {workload} tasks")
        
        # Task summary
        total_tasks = len(self.orchestrator.tasks)
        if total_tasks > 0:
            completed = len([t for t in self.orchestrator.tasks.values() if t.status.name == "COMPLETED"])
            in_progress = len([t for t in self.orchestrator.tasks.values() if t.status.name == "IN_PROGRESS"])
            blocked = len([t for t in self.orchestrator.tasks.values() if t.status.name == "BLOCKED"])
            
            print(f"\n📋 Tasks: {completed}/{total_tasks} completed")
            print(f"   🔄 In Progress: {in_progress}")
            print(f"   🚫 Blocked: {blocked}")
        else:
            print("\n📋 No tasks assigned yet")
        
        # Human connection
        if self.orchestrator.human_id:
            print(f"\n👤 Product Owner: Connected")
        else:
            print(f"\n👤 Product Owner: Waiting for connection...")
        
        print()
    
    async def start_sprint_planning(self):
        """Start sprint planning session."""
        if not self.orchestrator.human_id:
            print("❌ Cannot start sprint planning - no Product Owner connected")
            print("💡 Wait for human to join the collaboration")
            return
        
        # Import here to avoid circular imports
        sprint_planner = await create_sprint_planner(self.orchestrator)
        
        session_id = await sprint_planner.initiate_sprint_planning(
            self.orchestrator.human_id
        )
        
        print(f"🎯 Sprint planning session started: {session_id}")
        print("💡 Collaborate with the Product Owner in the team chat to plan your sprint!")
    
    async def show_agents(self):
        """Show detailed agent information."""
        print("\n👥 AGENT TEAM")
        print("=" * 50)
        
        if not self.orchestrator.agents:
            print("No agents connected yet")
            return
        
        for agent_id, agent in self.orchestrator.agents.items():
            print(f"\n🤖 {agent.name}")
            print(f"   Role: {agent.role}")
            print(f"   Status: {'🟢 Available' if agent.availability else '🔴 Unavailable'}")
            print(f"   Workload: {agent.current_workload}/{agent.max_workload} tasks")
            print(f"   Capabilities: {', '.join(cap.value for cap in agent.capabilities)}")
            
            # Show current tasks
            agent_tasks = [
                task for task in self.orchestrator.tasks.values()
                if task.assigned_to == agent_id and task.status.name in ["ASSIGNED", "IN_PROGRESS"]
            ]
            if agent_tasks:
                print(f"   Current Tasks:")
                for task in agent_tasks:
                    print(f"     • {task.title} ({task.status.name})")
        
        print()
    
    async def show_tasks(self):
        """Show detailed task information."""
        print("\n📋 TASK STATUS")
        print("=" * 50)
        
        if not self.orchestrator.tasks:
            print("No tasks created yet")
            return
        
        # Group tasks by status
        from orchestration.task_orchestrator import TaskStatus
        
        for status in TaskStatus:
            tasks_in_status = [
                task for task in self.orchestrator.tasks.values()
                if task.status == status
            ]
            
            if tasks_in_status:
                print(f"\n{status.value.upper().replace('_', ' ')} ({len(tasks_in_status)}):")
                for task in tasks_in_status:
                    agent_name = "Unassigned"
                    if task.assigned_to and task.assigned_to in self.orchestrator.agents:
                        agent_name = self.orchestrator.agents[task.assigned_to].name
                    
                    print(f"   • {task.title}")
                    print(f"     Assigned to: {agent_name}")
                    print(f"     Effort: {task.estimated_effort}h, Priority: {task.priority.value}")
        
        print()
    
    async def show_blockers(self):
        """Show active blockers and resolutions."""
        print("\n🚫 ACTIVE BLOCKERS")
        print("=" * 50)
        
        if not self.orchestrator.blockers:
            print("No active blockers - great job team! 🎉")
            return
        
        for blocker_id, blocker in self.orchestrator.blockers.items():
            task = self.orchestrator.tasks.get(blocker.task_id)
            task_title = task.title if task else "Unknown Task"
            
            print(f"\n🚫 {blocker.title}")
            print(f"   Task: {task_title}")
            print(f"   Type: {blocker.blocker_type.value}")
            print(f"   Impact: {blocker.impact}")
            print(f"   Description: {blocker.description}")
            
            if blocker.escalated_to_human:
                print(f"   Status: 🚨 Escalated to Product Owner")
            elif blocker.resolution_strategy:
                print(f"   Resolution: {blocker.resolution_strategy}")
            else:
                print(f"   Status: 🔄 Working on resolution")
        
        print()
    
    async def show_capacity(self):
        """Show team capacity analysis."""
        print("\n📊 TEAM CAPACITY ANALYSIS")
        print("=" * 50)
        
        from orchestration.assignment_engine import analyze_team_capacity
        
        analysis = analyze_team_capacity(
            self.orchestrator.agents,
            self.orchestrator.tasks
        )
        
        print(f"Team Size: {analysis['team_size']} agents")
        print(f"Total Capacity: {analysis['total_capacity']} task slots")
        print(f"Current Utilization: {analysis['utilization_rate']:.1f}%")
        print(f"Active Tasks: {analysis['active_tasks']}")
        
        print(f"\nAgent Breakdown:")
        for agent_id, agent_data in analysis['agents'].items():
            utilization_icon = "🟢" if agent_data['utilization'] < 70 else "🟡" if agent_data['utilization'] < 90 else "🔴"
            print(f"   {utilization_icon} {agent_data['name']} ({agent_data['role']})")
            print(f"      Utilization: {agent_data['utilization']:.1f}% ({agent_data['current_tasks']}/{agent_data['capacity']})")
        
        print()
    
    async def show_metrics(self):
        """Show sprint progress metrics."""
        print("\n📈 SPRINT METRICS")
        print("=" * 50)
        
        if not self.orchestrator.current_sprint:
            print("No active sprint to show metrics for")
            return
        
        # Calculate basic metrics
        total_tasks = len(self.orchestrator.tasks)
        if total_tasks == 0:
            print("No tasks in current sprint")
            return
        
        completed_tasks = len([
            t for t in self.orchestrator.tasks.values()
            if t.status.name == "COMPLETED"
        ])
        
        in_progress_tasks = len([
            t for t in self.orchestrator.tasks.values()
            if t.status.name == "IN_PROGRESS"
        ])
        
        blocked_tasks = len([
            t for t in self.orchestrator.tasks.values()
            if t.status.name == "BLOCKED"
        ])
        
        progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        print(f"Sprint: {self.orchestrator.current_sprint}")
        print(f"Progress: {completed_tasks}/{total_tasks} tasks ({progress_percentage:.1f}%)")
        print(f"Active: {in_progress_tasks} tasks in progress")
        print(f"Blocked: {blocked_tasks} tasks blocked")
        
        # Show progress bar
        bar_length = 30
        filled_length = int(bar_length * progress_percentage / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        print(f"Progress: [{bar}] {progress_percentage:.1f}%")
        
        print()
    
    async def manual_assign(self, task_identifier: str, agent_identifier: str):
        """Manually assign task to agent."""
        # Find task by ID or partial title match
        task = None
        for task_id, t in self.orchestrator.tasks.items():
            if (task_id == task_identifier or 
                task_identifier.lower() in t.title.lower()):
                task = t
                break
        
        if not task:
            print(f"❌ Task not found: {task_identifier}")
            return
        
        # Find agent by ID or name
        agent = None
        for agent_id, a in self.orchestrator.agents.items():
            if (agent_id == agent_identifier or
                agent_identifier.lower() in a.name.lower() or
                agent_identifier.lower() == a.role.lower()):
                agent = a
                break
        
        if not agent:
            print(f"❌ Agent not found: {agent_identifier}")
            return
        
        # Assign task
        await self.orchestrator.assign_task_to_agent(task.id, agent.agent_id)
        print(f"✅ Assigned '{task.title}' to {agent.name}")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Launch AIOSv3 Task Orchestrator")
    parser.add_argument("--server", default="ws://localhost:8765",
                       help="Collaboration server URL")
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("🎯 Starting AIOSv3 Task Orchestrator...")
    print(f"📡 Connecting to: {args.server}")
    print(f"📁 Repository: {Path.cwd()}")
    
    try:
        # Create and initialize orchestrator
        orchestrator = TaskOrchestrator(collaboration_server=args.server)
        await orchestrator.initialize()
        
        # Create progress monitor
        progress_monitor = await create_progress_monitor(orchestrator)
        
        print("✅ Task Orchestrator initialized successfully!")
        print("💡 Waiting for team members to join...")
        print("💡 Use 'help' to see available commands")
        
        # Create and run terminal
        terminal = OrchestratorTerminal(orchestrator)
        await terminal.run_terminal()
        
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        logger.error(f"Failed to start orchestrator: {e}")
        print(f"❌ Failed to start orchestrator: {e}")
        
        if "Connection refused" in str(e):
            print("\n💡 Make sure the collaboration server is running:")
            print("   python3 collaboration_server.py")


if __name__ == "__main__":
    asyncio.run(main())