#!/usr/bin/env python3
"""
Handoff Connector - Bridges Hermes to Task Orchestrator.
Transforms project briefs into sprint planning and task assignments.
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.agents.specialists.hermes.project_brief import ProjectBrief, ProjectType, Priority
from src.agents.specialists.hermes.task_decomposer import TaskDecomposer, DevelopmentTask, AgentType
from src.agents.specialists.hermes.hermes_with_llm import HermesWithLLM
from src.agents.base.types import TaskType as OrchestratorTaskType
from src.orchestration.task_orchestrator import TaskOrchestrator, SprintObjective, Task, TaskPriority, TaskStatus

logger = logging.getLogger(__name__)


class HandoffConnector:
    """Connects Hermes conversations to Task Orchestrator for project execution."""
    
    def __init__(self, hermes: Optional[HermesWithLLM] = None):
        """Initialize the handoff connector."""
        self.hermes = hermes
        self.orchestrator: Optional[TaskOrchestrator] = None
        self.task_decomposer = TaskDecomposer()
        self.active_handoffs: Dict[str, Dict[str, Any]] = {}  # session_id -> handoff info
    
    async def initialize(self, collaboration_server: str = "ws://localhost:8765"):
        """Initialize connection to orchestrator."""
        logger.info("🔗 Initializing Handoff Connector...")
        
        # Create and initialize orchestrator
        self.orchestrator = TaskOrchestrator(collaboration_server)
        await self.orchestrator.initialize()
        
        logger.info("✅ Handoff Connector ready for project handoffs!")
    
    async def handoff_project(self, brief: ProjectBrief, session_id: str) -> Dict[str, Any]:
        """
        Hand off a project brief to the Task Orchestrator.
        This triggers sprint planning and task assignment.
        """
        logger.info(f"🚀 Initiating handoff for project: {brief.name}")
        
        # Decompose project into tasks
        tasks = self.task_decomposer.decompose_project(brief)
        
        # Create sprint objectives from brief
        sprint_objectives = self._create_sprint_objectives(brief)
        
        # Create handoff record
        handoff_id = f"handoff_{uuid.uuid4().hex[:8]}"
        handoff_info = {
            "id": handoff_id,
            "session_id": session_id,
            "project_name": brief.name,
            "created_at": datetime.now(),
            "brief": brief,
            "tasks": tasks,
            "objectives": sprint_objectives,
            "status": "initiating"
        }
        self.active_handoffs[session_id] = handoff_info
        
        # Send project information to orchestrator
        await self._send_project_to_orchestrator(brief, tasks, sprint_objectives)
        
        # Track handoff
        handoff_info["status"] = "handed_off"
        
        return {
            "handoff_id": handoff_id,
            "project_name": brief.name,
            "tasks_created": len(tasks),
            "objectives": len(sprint_objectives),
            "estimated_timeline": self.task_decomposer.estimate_timeline(tasks),
            "assigned_agents": self._get_assigned_agents(tasks),
            "message": f"Successfully handed off '{brief.name}' to the development team!"
        }
    
    def _create_sprint_objectives(self, brief: ProjectBrief) -> List[SprintObjective]:
        """Create sprint objectives from project brief."""
        objectives = []
        
        # Main project objective
        main_objective = SprintObjective(
            id=f"obj_{uuid.uuid4().hex[:8]}",
            title=f"Deliver {brief.name}",
            description=brief.description,
            priority=self._map_priority(brief.priority),
            estimated_effort=brief.estimate_complexity() * 8,  # Convert complexity to story points
            acceptance_criteria=[
                f"All {len(brief.requirements)} requirements implemented",
                "All tests passing with >80% coverage",
                "Documentation complete",
                "Deployment successful"
            ],
            dependencies=[]
        )
        objectives.append(main_objective)
        
        # Create objectives for major features
        for i, feature in enumerate(brief.key_features[:3]):  # Top 3 features
            feature_obj = SprintObjective(
                id=f"obj_{uuid.uuid4().hex[:8]}",
                title=f"Feature: {feature[:50]}",
                description=f"Implement and test: {feature}",
                priority=TaskPriority.HIGH if i == 0 else TaskPriority.MEDIUM,
                estimated_effort=13,  # Standard feature effort
                acceptance_criteria=[
                    "Feature fully implemented",
                    "Unit tests complete", 
                    "Integration tests passing",
                    "User acceptance criteria met"
                ],
                dependencies=[main_objective.id] if i > 0 else []
            )
            objectives.append(feature_obj)
        
        return objectives
    
    def _map_priority(self, brief_priority: Priority) -> TaskPriority:
        """Map ProjectBrief priority to TaskOrchestrator priority."""
        mapping = {
            Priority.CRITICAL: TaskPriority.CRITICAL,
            Priority.HIGH: TaskPriority.HIGH,
            Priority.MEDIUM: TaskPriority.MEDIUM,
            Priority.LOW: TaskPriority.LOW
        }
        return mapping.get(brief_priority, TaskPriority.MEDIUM)
    
    def _map_task_type(self, decomposer_task_type) -> OrchestratorTaskType:
        """Map TaskDecomposer task types to Orchestrator task types."""
        # Import at function level to avoid circular imports
        from src.agents.specialists.hermes.task_decomposer import TaskType as DecomposerTaskType
        
        mapping = {
            DecomposerTaskType.API_ENDPOINT: OrchestratorTaskType.API_DESIGN,
            DecomposerTaskType.DATABASE_SCHEMA: OrchestratorTaskType.DATABASE,
            DecomposerTaskType.BUSINESS_LOGIC: OrchestratorTaskType.IMPLEMENTATION,
            DecomposerTaskType.INTEGRATION: OrchestratorTaskType.IMPLEMENTATION,
            DecomposerTaskType.AUTHENTICATION: OrchestratorTaskType.IMPLEMENTATION,
            DecomposerTaskType.UI_COMPONENT: OrchestratorTaskType.UI_DESIGN,
            DecomposerTaskType.USER_FLOW: OrchestratorTaskType.UI_DESIGN,
            DecomposerTaskType.RESPONSIVE_DESIGN: OrchestratorTaskType.UI_DESIGN,
            DecomposerTaskType.STATE_MANAGEMENT: OrchestratorTaskType.IMPLEMENTATION,
            DecomposerTaskType.UNIT_TEST: OrchestratorTaskType.TESTING,
            DecomposerTaskType.INTEGRATION_TEST: OrchestratorTaskType.TESTING,
            DecomposerTaskType.E2E_TEST: OrchestratorTaskType.TESTING,
            DecomposerTaskType.SECURITY_AUDIT: OrchestratorTaskType.VALIDATION,
            DecomposerTaskType.PERFORMANCE_TEST: OrchestratorTaskType.TESTING,
            DecomposerTaskType.INFRASTRUCTURE: OrchestratorTaskType.INFRASTRUCTURE,
            DecomposerTaskType.CI_CD_PIPELINE: OrchestratorTaskType.DEPLOYMENT,
            DecomposerTaskType.DEPLOYMENT: OrchestratorTaskType.DEPLOYMENT,
            DecomposerTaskType.MONITORING: OrchestratorTaskType.MONITORING,
            DecomposerTaskType.SCALING: OrchestratorTaskType.INFRASTRUCTURE,
        }
        return mapping.get(decomposer_task_type, OrchestratorTaskType.GENERAL)
    
    async def _send_project_to_orchestrator(
        self, 
        brief: ProjectBrief, 
        tasks: List[DevelopmentTask],
        objectives: List[SprintObjective]
    ):
        """Send project information to the Task Orchestrator."""
        # First, announce the new project
        await self.orchestrator.send_message({
            "type": "chat",
            "from_id": "hermes_handoff",
            "content": f"""🎉 **New Project from Hermes!**

**Project:** {brief.name}
**Type:** {brief.project_type.value.replace('_', ' ').title()}
**Priority:** {brief.priority.value.upper()}
**Complexity:** {brief.estimate_complexity()}/10

**Description:** {brief.description}

**Key Requirements:**
{chr(10).join(f'• {req.description}' for req in brief.requirements[:5])}

**Timeline:** {brief.timeline.estimated_duration_days} days
**Budget:** {brief.budget_range or 'Flexible'}

I've decomposed this into {len(tasks)} development tasks. Ready to start sprint planning!""",
            "metadata": {
                "hermes_handoff": True,
                "project_id": brief.id,
                "session_id": brief.session_id
            }
        })
        
        # Create sprint in orchestrator
        sprint_id = f"sprint_{brief.id[:8]}"
        self.orchestrator.current_sprint = sprint_id
        
        # Add objectives to orchestrator
        for obj in objectives:
            self.orchestrator.sprint_objectives[obj.id] = obj
        
        # Convert and add tasks to orchestrator
        for task in tasks:
            orchestrator_task = Task(
                id=task.id,
                title=task.name,
                description=task.description,
                task_type=self._map_task_type(task.type),
                priority=self._map_priority(task.priority),
                status=TaskStatus.PLANNED,
                estimated_effort=task.estimated_hours,
                assigned_to=None,  # Let orchestrator assign
                assigned_role=None,
                parent_objective=objectives[0].id if objectives else None,
                dependencies=task.dependencies,
                acceptance_criteria=task.acceptance_criteria,
                deliverables=[f"Implementation of {task.name}", "Tests", "Documentation"]
            )
            self.orchestrator.tasks[task.id] = orchestrator_task
        
        # Request orchestrator to start assigning tasks
        await self.orchestrator.send_message({
            "type": "chat",
            "from_id": "hermes_handoff",
            "content": """🎯 **Sprint Planning Request**

All project details have been loaded. Please:
1. Review the objectives and tasks
2. Start assigning tasks to available agents
3. Set up the sprint timeline
4. Monitor progress and handle any blockers

The client is eager to see progress! Let's build something amazing! 🚀""",
            "metadata": {"start_sprint": True, "sprint_id": sprint_id}
        })
    
    def _get_assigned_agents(self, tasks: List[DevelopmentTask]) -> Dict[str, int]:
        """Get count of tasks per agent type."""
        assignments = self.task_decomposer.assign_agents(tasks)
        return {
            agent.value: len(agent_tasks)
            for agent, agent_tasks in assignments.items()
            if agent_tasks
        }
    
    async def get_handoff_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a handoff by session ID."""
        handoff = self.active_handoffs.get(session_id)
        if not handoff:
            return None
        
        # Get current task status from orchestrator
        task_statuses = {}
        for task in handoff["tasks"]:
            if task.id in self.orchestrator.tasks:
                orch_task = self.orchestrator.tasks[task.id]
                task_statuses[task.id] = {
                    "name": orch_task.title,
                    "status": orch_task.status.value,
                    "assigned_to": orch_task.assigned_to,
                    "progress": orch_task.progress
                }
        
        return {
            "handoff_id": handoff["id"],
            "project_name": handoff["project_name"],
            "status": handoff["status"],
            "created_at": handoff["created_at"].isoformat(),
            "total_tasks": len(handoff["tasks"]),
            "task_statuses": task_statuses,
            "objectives": [obj.title for obj in handoff["objectives"]]
        }
    
    async def send_client_update(self, session_id: str, message: str):
        """Send an update from the client to the development team."""
        handoff = self.active_handoffs.get(session_id)
        if not handoff:
            logger.warning(f"No handoff found for session {session_id}")
            return
        
        await self.orchestrator.send_message({
            "type": "chat",
            "from_id": "hermes_client",
            "content": f"""💬 **Client Update**

**Project:** {handoff['project_name']}

{message}

Please acknowledge and let me know if this impacts our current sprint.""",
            "metadata": {
                "client_update": True,
                "session_id": session_id,
                "handoff_id": handoff["id"]
            }
        })


class HermesHandoffBridge:
    """Bridge between Hermes agent and handoff system."""
    
    def __init__(self, hermes: HermesWithLLM):
        """Initialize the bridge."""
        self.hermes = hermes
        self.connector = HandoffConnector(hermes)
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(self, collaboration_server: str = "ws://localhost:8765"):
        """Initialize the handoff bridge."""
        await self.connector.initialize(collaboration_server)
    
    async def check_and_handoff(self, state) -> Optional[Dict[str, Any]]:
        """
        Check if conversation is ready for handoff and execute if ready.
        Returns handoff result or None if not ready.
        """
        if not state.ready_for_handoff:
            return None
        
        # Generate project brief
        from src.agents.specialists.hermes.brief_generator import BriefGenerator
        generator = BriefGenerator()
        brief = generator.generate_brief(state)
        
        # Perform handoff
        result = await self.connector.handoff_project(brief, state.session_id)
        
        # Track session
        self.active_sessions[state.session_id] = {
            "handoff_result": result,
            "brief": brief,
            "handoff_time": datetime.now()
        }
        
        return result
    
    def format_handoff_message(self, result: Dict[str, Any]) -> str:
        """Format handoff result for user display."""
        timeline = result["estimated_timeline"]
        agents = result["assigned_agents"]
        
        agent_list = []
        agent_names = {
            "apollo": "Apollo (Backend)",
            "aphrodite": "Aphrodite (Frontend)", 
            "athena": "Athena (QA)",
            "hephaestus": "Hephaestus (DevOps)"
        }
        
        for agent, count in agents.items():
            if agent in agent_names:
                agent_list.append(f"  • {agent_names[agent]}: {count} tasks")
        
        return f"""
🎉 **Project Successfully Handed Off!**

I've transferred your project to our AI development team:

**Project:** {result['project_name']}
**Tasks Created:** {result['tasks_created']}
**Timeline:** ~{timeline['parallel_days']} days with {timeline['agents_needed']} agents

**Team Assignment:**
{chr(10).join(agent_list)}

The team is now:
1. Setting up the development environment
2. Creating the technical architecture
3. Beginning implementation

You'll receive updates as work progresses. The team may reach out if they need clarification on any requirements.

Would you like to add any additional context or requirements before they begin?"""


async def test_handoff_connector():
    """Test the handoff connector with a sample project."""
    from src.agents.specialists.hermes.project_brief import create_sample_brief
    
    # Create connector
    connector = HandoffConnector()
    await connector.initialize()
    
    # Create sample brief
    brief = create_sample_brief()
    
    # Perform handoff
    result = await connector.handoff_project(brief, "test_session_123")
    
    print("Handoff Result:")
    print(json.dumps(result, indent=2))
    
    # Wait a bit for orchestrator to process
    await asyncio.sleep(2)
    
    # Check status
    status = await connector.get_handoff_status("test_session_123")
    print("\nHandoff Status:")
    print(json.dumps(status, indent=2, default=str))
    
    # Keep running to see orchestrator actions
    await asyncio.sleep(10)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_handoff_connector())