#!/usr/bin/env python3
"""
Task Orchestrator - Central Coordination System for Multi-Agent Development Team

This acts as the Technical Lead/Orchestrator that:
1. Collaborates with human on sprint planning
2. Makes intelligent task assignments to specialized agents
3. Monitors progress and resolves blockers
4. Escalates major decisions to human
5. Ensures sprint goals are achieved
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
import websockets

from src.agents.base.types import TaskType, AgentType
from src.agents.base.enhanced_agent import EnhancedTask, EnhancedTaskResult

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(Enum):
    """Task lifecycle status."""
    PLANNED = "planned"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BlockerType(Enum):
    """Types of blockers that can occur."""
    TECHNICAL = "technical"
    DEPENDENCY = "dependency"
    DECISION_NEEDED = "decision_needed"
    RESOURCE = "resource"
    EXTERNAL = "external"


@dataclass
class SprintObjective:
    """High-level sprint objective."""
    id: str
    title: str
    description: str
    priority: TaskPriority
    estimated_effort: int  # story points
    acceptance_criteria: List[str]
    dependencies: List[str]
    assigned_epic: Optional[str] = None


@dataclass
class Task:
    """Detailed task that can be assigned to agents."""
    id: str
    title: str
    description: str
    task_type: TaskType
    priority: TaskPriority
    status: TaskStatus
    estimated_effort: int  # hours
    assigned_to: Optional[str] = None
    assigned_role: Optional[str] = None
    parent_objective: Optional[str] = None
    dependencies: List[str] = None
    created_at: float = None
    assigned_at: Optional[float] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    progress: int = 0  # 0-100%
    blockers: List[str] = None
    deliverables: List[str] = None
    acceptance_criteria: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.blockers is None:
            self.blockers = []
        if self.deliverables is None:
            self.deliverables = []
        if self.acceptance_criteria is None:
            self.acceptance_criteria = []
        if self.created_at is None:
            self.created_at = time.time()


@dataclass
class Blocker:
    """Represents a blocker preventing task progress."""
    id: str
    task_id: str
    blocker_type: BlockerType
    title: str
    description: str
    impact: str  # How this affects the task/sprint
    escalated_to_human: bool = False
    resolution_strategy: Optional[str] = None
    created_at: float = None
    resolved_at: Optional[float] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


@dataclass 
class AgentCapability:
    """Represents what an agent can do."""
    agent_id: str
    role: str
    name: str
    capabilities: List[TaskType]
    current_workload: int  # number of active tasks
    max_workload: int = 3
    expertise_level: Dict[str, int] = None  # domain -> skill level (1-10)
    availability: bool = True
    last_seen: float = None
    
    def __post_init__(self):
        if self.expertise_level is None:
            self.expertise_level = {}
        if self.last_seen is None:
            self.last_seen = time.time()


class TaskOrchestrator:
    """
    Central orchestrator for multi-agent development team.
    
    Acts as Technical Lead coordinating between human Product Owner
    and specialized AI agents to deliver sprint objectives.
    """
    
    def __init__(self, collaboration_server: str = "ws://localhost:8765"):
        self.collaboration_server = collaboration_server
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.connected = False
        
        # Sprint and task management
        self.current_sprint: Optional[str] = None
        self.sprint_objectives: Dict[str, SprintObjective] = {}
        self.tasks: Dict[str, Task] = {}
        self.blockers: Dict[str, Blocker] = {}
        
        # Agent management
        self.agents: Dict[str, AgentCapability] = {}
        self.agent_assignments: Dict[str, Set[str]] = {}  # agent_id -> task_ids
        
        # Human collaboration
        self.human_id: Optional[str] = None
        self.pending_escalations: List[str] = []
        
        # Orchestrator state
        self.orchestrator_id = f"orchestrator_{uuid.uuid4().hex[:8]}"
        self.monitoring_active = False
        
    async def initialize(self):
        """Initialize the orchestrator."""
        logger.info("🎯 Initializing Task Orchestrator...")
        
        # Connect to collaboration server
        await self.connect_to_collaboration()
        
        # Start monitoring tasks
        asyncio.create_task(self.monitor_sprint_progress())
        
        logger.info("✅ Task Orchestrator initialized and ready!")
    
    async def connect_to_collaboration(self):
        """Connect to collaboration server."""
        try:
            logger.info(f"🔗 Orchestrator connecting to: {self.collaboration_server}")
            self.websocket = await websockets.connect(self.collaboration_server)
            self.connected = True
            
            # Register as orchestrator
            await self.send_message({
                "type": "register",
                "id": self.orchestrator_id,
                "role": "orchestrator",
                "name": "Task Orchestrator",
                "terminal_id": f"orchestrator_{uuid.uuid4().hex[:8]}"
            })
            
            # Start listening for messages
            asyncio.create_task(self.listen_for_messages())
            
            logger.info("✅ Orchestrator connected to collaboration server")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect orchestrator: {e}")
            self.connected = False
    
    async def send_message(self, data: Dict[str, Any]):
        """Send message to collaboration server."""
        if self.websocket and self.connected:
            try:
                await self.websocket.send(json.dumps(data))
            except Exception as e:
                logger.error(f"Failed to send orchestrator message: {e}")
                self.connected = False
    
    async def listen_for_messages(self):
        """Listen for messages from collaboration server."""
        try:
            async for message_str in self.websocket:
                try:
                    data = json.loads(message_str)
                    await self.handle_collaboration_message(data)
                except json.JSONDecodeError:
                    logger.error("Orchestrator received invalid JSON")
                except Exception as e:
                    logger.error(f"Error handling orchestrator message: {e}")
        except websockets.exceptions.ConnectionClosed:
            self.connected = False
            logger.warning("🔌 Orchestrator disconnected from collaboration server")
    
    async def handle_collaboration_message(self, data: Dict[str, Any]):
        """Handle messages from collaboration server."""
        message_type = data.get("type")
        
        if message_type == "collaborator_joined":
            await self.handle_agent_joined(data)
        elif message_type == "collaborator_left":
            await self.handle_agent_left(data)
        elif message_type == "task_completed":
            await self.handle_task_completion(data)
        elif message_type == "task_failed":
            await self.handle_task_failure(data)
        elif message_type == "new_message":
            await self.handle_team_message(data)
        elif message_type == "status_updated":
            await self.handle_agent_status_update(data)
    
    async def handle_agent_joined(self, data: Dict[str, Any]):
        """Handle new agent joining the team."""
        collaborator = data.get("collaborator", {})
        agent_id = collaborator.get("id")
        role = collaborator.get("role")
        name = collaborator.get("name")
        
        if role == "human":
            self.human_id = agent_id
            logger.info(f"👤 Human Product Owner joined: {name}")
            await self.greet_human()
        elif role in ["cto", "backend-dev", "qa", "frontend-dev", "devops"]:
            # Register agent capabilities
            capability = AgentCapability(
                agent_id=agent_id,
                role=role,
                name=name,
                capabilities=self._get_role_capabilities(role),
                current_workload=0,
                expertise_level=self._get_role_expertise(role)
            )
            self.agents[agent_id] = capability
            self.agent_assignments[agent_id] = set()
            
            logger.info(f"🤖 Agent joined team: {name} ({role})")
            await self.welcome_agent(agent_id, name, role)
    
    async def handle_agent_left(self, data: Dict[str, Any]):
        """Handle agent leaving the team."""
        agent_id = data.get("collaborator_id")
        if agent_id in self.agents:
            agent = self.agents.pop(agent_id)
            # Reassign tasks if needed
            if agent_id in self.agent_assignments:
                orphaned_tasks = self.agent_assignments.pop(agent_id)
                if orphaned_tasks:
                    await self.reassign_orphaned_tasks(orphaned_tasks)
            logger.info(f"👋 Agent left team: {agent.name}")
    
    async def greet_human(self):
        """Send greeting to human Product Owner."""
        await self.send_message({
            "type": "chat",
            "from_id": self.orchestrator_id,
            "content": """🎯 **Task Orchestrator Ready!**

Hello! I'm your AI Technical Lead and will coordinate our development team.

**What I do:**
• 📋 Help you plan sprints and break down objectives
• 🎯 Intelligently assign tasks to specialized agents
• 📊 Monitor progress and resolve blockers
• 🚨 Escalate major decisions to you when needed
• ✅ Ensure sprint goals are achieved on time

**Available Commands:**
• `plan sprint <objectives>` - Collaborate on sprint planning
• `status` - Show current sprint progress  
• `assign <task> to <agent>` - Manual task assignment
• `escalate <issue>` - Bring something to my attention

Ready to build something amazing together! What would you like to work on?""",
            "metadata": {"orchestrator_greeting": True}
        })
    
    async def welcome_agent(self, agent_id: str, name: str, role: str):
        """Welcome new agent to the team."""
        await self.send_message({
            "type": "chat", 
            "from_id": self.orchestrator_id,
            "content": f"""🤖 Welcome to the team, **{name}**!

I'm the Task Orchestrator and will coordinate our work. As our **{role.replace('-', ' ').title()}**, I'll assign you tasks that match your expertise.

I'll monitor your progress and help with any blockers. Focus on delivering high-quality work - I'll handle the coordination!

Ready to contribute to our sprint goals! 🚀""",
            "metadata": {"agent_welcome": True, "target_agent": agent_id}
        })
    
    def _get_role_capabilities(self, role: str) -> List[TaskType]:
        """Get capabilities for agent role."""
        role_capabilities = {
            "cto": [TaskType.ARCHITECTURE, TaskType.ANALYSIS, TaskType.PLANNING, TaskType.REVIEW],
            "backend-dev": [TaskType.IMPLEMENTATION, TaskType.API_DESIGN, TaskType.DATABASE, TaskType.REVIEW],
            "frontend-dev": [TaskType.IMPLEMENTATION, TaskType.UI_DESIGN, TaskType.TESTING],
            "qa": [TaskType.TESTING, TaskType.VALIDATION, TaskType.ANALYSIS, TaskType.REVIEW],
            "devops": [TaskType.DEPLOYMENT, TaskType.INFRASTRUCTURE, TaskType.MONITORING]
        }
        return role_capabilities.get(role, [TaskType.GENERAL])
    
    def _get_role_expertise(self, role: str) -> Dict[str, int]:
        """Get expertise levels for agent role."""
        role_expertise = {
            "cto": {"architecture": 9, "strategy": 9, "leadership": 8, "technology": 9},
            "backend-dev": {"coding": 9, "apis": 9, "databases": 8, "performance": 7},
            "frontend-dev": {"ui": 9, "ux": 7, "javascript": 9, "frameworks": 8},
            "qa": {"testing": 9, "quality": 9, "automation": 8, "validation": 9},
            "devops": {"deployment": 9, "infrastructure": 9, "monitoring": 8, "automation": 8}
        }
        return role_expertise.get(role, {"general": 5})
    
    async def monitor_sprint_progress(self):
        """Continuously monitor sprint progress and handle issues."""
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                await self._check_task_progress()
                await self._detect_blockers()
                await self._update_sprint_metrics()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in sprint monitoring: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _check_task_progress(self):
        """Check progress of active tasks."""
        for task_id, task in self.tasks.items():
            if task.status == TaskStatus.IN_PROGRESS:
                # Check if task is taking too long
                if task.started_at and time.time() - task.started_at > 3600:  # 1 hour
                    await self._investigate_slow_task(task)
    
    async def _detect_blockers(self):
        """Detect potential blockers and resolve them."""
        for task_id, task in self.tasks.items():
            if task.status == TaskStatus.BLOCKED:
                blocker_id = f"blocker_{uuid.uuid4().hex[:8]}"
                if not any(b.task_id == task_id for b in self.blockers.values()):
                    await self._create_blocker(task_id, "Task marked as blocked")
    
    async def _investigate_slow_task(self, task: Task):
        """Investigate why a task is taking longer than expected."""
        agent_id = task.assigned_to
        if agent_id and agent_id in self.agents:
            agent = self.agents[agent_id]
            await self.send_message({
                "type": "chat",
                "from_id": self.orchestrator_id,
                "content": f"""🔍 **Progress Check**

Hi {agent.name}, I noticed the task "{task.title}" has been in progress for a while. 

**How can I help?**
• Are you encountering any blockers?
• Do you need additional resources or information?
• Should we break this task into smaller pieces?
• Is the complexity higher than estimated?

Let me know how I can support you! 🚀""",
                "metadata": {"progress_check": True, "task_id": task.id}
            })
    
    async def _create_blocker(self, task_id: str, description: str, blocker_type: BlockerType = BlockerType.TECHNICAL):
        """Create a new blocker."""
        blocker_id = f"blocker_{uuid.uuid4().hex[:8]}"
        blocker = Blocker(
            id=blocker_id,
            task_id=task_id,
            blocker_type=blocker_type,
            title=f"Blocker for task {task_id}",
            description=description,
            impact="Task progress halted"
        )
        self.blockers[blocker_id] = blocker
        
        # Attempt to resolve automatically first
        await self._attempt_blocker_resolution(blocker)
    
    async def _attempt_blocker_resolution(self, blocker: Blocker):
        """Attempt to resolve blocker automatically."""
        if blocker.blocker_type == BlockerType.TECHNICAL:
            # Offer technical assistance
            task = self.tasks.get(blocker.task_id)
            if task and task.assigned_to:
                await self.send_message({
                    "type": "chat",
                    "from_id": self.orchestrator_id, 
                    "content": f"""🔧 **Technical Support Available**

I see you're experiencing a technical blocker with "{task.title}".

**I can help with:**
• Architecture guidance and best practices
• Code review and debugging assistance  
• Alternative implementation approaches
• Resource recommendations and documentation

What specific challenge are you facing? Let's solve this together! 💪""",
                    "metadata": {"blocker_assistance": True, "blocker_id": blocker.id}
                })
        elif blocker.blocker_type == BlockerType.DECISION_NEEDED:
            # Escalate to human
            await self._escalate_to_human(blocker)
    
    async def _escalate_to_human(self, blocker: Blocker):
        """Escalate blocker to human Product Owner."""
        if self.human_id:
            blocker.escalated_to_human = True
            self.pending_escalations.append(blocker.id)
            
            task = self.tasks.get(blocker.task_id)
            await self.send_message({
                "type": "chat",
                "from_id": self.orchestrator_id,
                "content": f"""🚨 **Decision Required**

I need your input on a blocker:

**Task:** {task.title if task else 'Unknown'}
**Issue:** {blocker.description}
**Impact:** {blocker.impact}

This requires a product/business decision that's outside my technical scope. How would you like to proceed?""",
                "metadata": {"escalation": True, "blocker_id": blocker.id}
            })
    
    async def _update_sprint_metrics(self):
        """Update sprint progress metrics."""
        if not self.current_sprint:
            return
            
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        in_progress_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])
        blocked_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.BLOCKED])
        
        # Log metrics periodically
        if int(time.time()) % 1800 == 0:  # Every 30 minutes
            logger.info(f"📊 Sprint Progress: {completed_tasks}/{total_tasks} completed, {in_progress_tasks} in progress, {blocked_tasks} blocked")
    
    async def handle_task_completion(self, data: Dict[str, Any]):
        """Handle task completion from agent."""
        task_id = data.get("task_id")
        from_id = data.get("from_id")
        result = data.get("result", {})
        
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            task.progress = 100
            
            # Update agent workload
            if from_id in self.agents:
                self.agents[from_id].current_workload -= 1
                if from_id in self.agent_assignments:
                    self.agent_assignments[from_id].discard(task_id)
            
            # Celebrate completion
            await self.send_message({
                "type": "chat",
                "from_id": self.orchestrator_id,
                "content": f"""🎉 **Task Completed!**

Great work on "{task.title}"! 

**Result:** {result.get('success', False)}
**Quality:** High-quality delivery as expected
**Impact:** Moving us closer to sprint goals

Checking for dependent tasks that can now be started... 🔄""",
                "metadata": {"task_celebration": True, "task_id": task_id}
            })
            
            # Check for dependent tasks that can now be assigned
            await self._check_dependent_tasks(task_id)
    
    async def handle_task_failure(self, data: Dict[str, Any]):
        """Handle task failure from agent."""
        task_id = data.get("task_id")
        from_id = data.get("from_id")
        error = data.get("error", "Unknown error")
        
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.BLOCKED
            
            # Create blocker for the failure
            await self._create_blocker(task_id, f"Task failed: {error}", BlockerType.TECHNICAL)
            
            # Offer assistance
            await self.send_message({
                "type": "chat",
                "from_id": self.orchestrator_id,
                "content": f"""🔧 **Task Support Needed**

I see "{task.title}" encountered an issue: {error}

**Next Steps:**
1. Let's analyze the problem together
2. I can provide alternative approaches  
3. We might need to break this into smaller tasks
4. I can assign additional resources if needed

Don't worry - we'll get this resolved! What additional context can you provide?""",
                "metadata": {"task_support": True, "task_id": task_id}
            })
    
    async def _check_dependent_tasks(self, completed_task_id: str):
        """Check if any tasks were waiting for this completion."""
        for task_id, task in self.tasks.items():
            if (completed_task_id in task.dependencies and 
                task.status == TaskStatus.PLANNED and
                self._all_dependencies_met(task)):
                
                await self._assign_task_intelligently(task)
    
    def _all_dependencies_met(self, task: Task) -> bool:
        """Check if all task dependencies are completed."""
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    async def _assign_task_intelligently(self, task: Task):
        """Intelligently assign task to best available agent."""
        best_agent = self._find_best_agent_for_task(task)
        if best_agent:
            await self.assign_task_to_agent(task.id, best_agent.agent_id)
    
    def _find_best_agent_for_task(self, task: Task) -> Optional[AgentCapability]:
        """Find the best agent for a given task."""
        suitable_agents = []
        
        for agent in self.agents.values():
            if not agent.availability:
                continue
            if agent.current_workload >= agent.max_workload:
                continue
            if task.task_type not in agent.capabilities:
                continue
                
            # Calculate suitability score
            score = 0
            # Workload factor (prefer less busy agents)
            score += (agent.max_workload - agent.current_workload) * 10
            
            # Expertise factor
            domain_scores = []
            for domain, level in agent.expertise_level.items():
                if domain.lower() in task.description.lower():
                    domain_scores.append(level)
            if domain_scores:
                score += max(domain_scores) * 5
            
            suitable_agents.append((score, agent))
        
        if suitable_agents:
            suitable_agents.sort(key=lambda x: x[0], reverse=True)
            return suitable_agents[0][1]
        
        return None
    
    async def assign_task_to_agent(self, task_id: str, agent_id: str):
        """Assign specific task to specific agent."""
        task = self.tasks.get(task_id)
        agent = self.agents.get(agent_id)
        
        if not task or not agent:
            logger.error(f"Cannot assign task {task_id} to agent {agent_id}")
            return
        
        # Update task
        task.assigned_to = agent_id
        task.assigned_role = agent.role
        task.status = TaskStatus.ASSIGNED
        task.assigned_at = time.time()
        
        # Update agent
        agent.current_workload += 1
        self.agent_assignments[agent_id].add(task_id)
        
        # Send task assignment
        await self.send_message({
            "type": "task_assignment",
            "task": {
                "id": task_id,
                "title": task.title,
                "description": task.description,
                "task_type": task.task_type.value,
                "priority": task.priority.value,
                "estimated_effort": task.estimated_effort,
                "acceptance_criteria": task.acceptance_criteria,
                "deliverables": task.deliverables,
                "assigned_by": self.orchestrator_id
            },
            "assigned_to": agent_id
        })
        
        # Announce assignment to team
        await self.send_message({
            "type": "chat",
            "from_id": self.orchestrator_id,
            "content": f"""📋 **Task Assigned**

**{agent.name}** has been assigned: "{task.title}"

**Priority:** {task.priority.value.title()}
**Estimated Effort:** {task.estimated_effort}h
**Type:** {task.task_type.value.replace('_', ' ').title()}

This aligns with your expertise and current workload. Let me know if you need any clarification or support! 🎯""",
            "metadata": {"task_assignment": True, "task_id": task_id, "agent_id": agent_id}
        })
    
    async def handle_team_message(self, data: Dict[str, Any]):
        """Handle messages from team members."""
        message = data.get("message", {})
        from_name = data.get("from_name", "Unknown")
        content = message.get("content", "")
        from_role = message.get("from_role", "")
        
        # Check if this is a command or question directed at orchestrator
        if "orchestrator" in content.lower() or "task orchestrator" in content.lower():
            await self._handle_orchestrator_command(content, from_name, from_role)
    
    async def _handle_orchestrator_command(self, content: str, from_name: str, from_role: str):
        """Handle commands/questions directed at orchestrator."""
        content_lower = content.lower()
        
        if "status" in content_lower:
            await self._send_sprint_status()
        elif "help" in content_lower:
            await self._send_orchestrator_help()
        elif "plan sprint" in content_lower:
            await self._initiate_sprint_planning(from_name)
    
    async def _send_sprint_status(self):
        """Send current sprint status."""
        if not self.current_sprint:
            await self.send_message({
                "type": "chat",
                "from_id": self.orchestrator_id,
                "content": "📊 **Sprint Status:** No active sprint. Ready to plan the next one!",
                "metadata": {"status_report": True}
            })
            return
        
        total_tasks = len(self.tasks)
        completed = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        in_progress = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS]) 
        blocked = len([t for t in self.tasks.values() if t.status == TaskStatus.BLOCKED])
        
        status_report = f"""📊 **Sprint Status Report**

**Progress:** {completed}/{total_tasks} tasks completed ({(completed/total_tasks*100) if total_tasks else 0:.1f}%)
**Active:** {in_progress} tasks in progress
**Blocked:** {blocked} tasks blocked
**Team:** {len(self.agents)} agents active

**Next Steps:** {'On track for sprint goals!' if blocked == 0 else f'Resolving {blocked} blockers'}"""

        await self.send_message({
            "type": "chat",
            "from_id": self.orchestrator_id,
            "content": status_report,
            "metadata": {"status_report": True}
        })
    
    async def _send_orchestrator_help(self):
        """Send orchestrator capabilities and commands."""
        help_text = """🎯 **Task Orchestrator Help**

**What I do:**
• 📋 Plan sprints with you and break down objectives
• 🎯 Assign tasks intelligently to the right agents
• 📊 Monitor progress and resolve blockers automatically
• 🚨 Escalate decisions that need your input
• ✅ Ensure we deliver sprint goals on time

**Commands:**
• `status` - Show current sprint progress
• `plan sprint` - Start collaborative sprint planning
• `help` - Show this help message

**Automatic Actions:**
• Smart task assignment based on agent expertise
• Progress monitoring and blocker detection  
• Quality assurance and delivery tracking
• Team coordination and communication

I'm here to make our AI development team highly effective! 🚀"""

        await self.send_message({
            "type": "chat", 
            "from_id": self.orchestrator_id,
            "content": help_text,
            "metadata": {"help_response": True}
        })
    
    async def _initiate_sprint_planning(self, from_name: str):
        """Start sprint planning collaboration with human."""
        await self.send_message({
            "type": "chat",
            "from_id": self.orchestrator_id,
            "content": f"""🎯 **Sprint Planning Session**

Great idea, {from_name}! Let's plan our next sprint together.

**Please tell me:**
1. **What are the main objectives?** (What do we want to achieve?)
2. **What's the priority?** (What's most important to deliver first?)
3. **Any constraints?** (Timeline, dependencies, resources?)
4. **Success criteria?** (How do we know we've succeeded?)

I'll break these down into specific tasks and assign them to our team based on their expertise. What's our primary goal for this sprint?""",
            "metadata": {"sprint_planning": True, "planning_initiated": True}
        })


async def main():
    """Test the TaskOrchestrator."""
    orchestrator = TaskOrchestrator()
    await orchestrator.initialize()
    
    # Keep running
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        logger.info("👋 Task Orchestrator shutting down...")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())