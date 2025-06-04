#!/usr/bin/env python3
"""
Task Decomposer - Breaks down project briefs into assignable tasks.
Maps requirements to specific development tasks for each agent.
"""

import logging
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

from src.agents.specialists.hermes.project_brief import (
    ProjectBrief, ProjectType, Priority, UserRequirement
)
from src.agents.specialists.hermes.requirements_extractor import RequirementType

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of development tasks."""
    # Backend tasks (Apollo)
    API_ENDPOINT = "api_endpoint"
    DATABASE_SCHEMA = "database_schema"
    BUSINESS_LOGIC = "business_logic"
    INTEGRATION = "integration"
    AUTHENTICATION = "authentication"
    
    # Frontend tasks (Aphrodite)
    UI_COMPONENT = "ui_component"
    USER_FLOW = "user_flow"
    RESPONSIVE_DESIGN = "responsive_design"
    STATE_MANAGEMENT = "state_management"
    
    # QA tasks (Athena)
    UNIT_TEST = "unit_test"
    INTEGRATION_TEST = "integration_test"
    E2E_TEST = "e2e_test"
    SECURITY_AUDIT = "security_audit"
    PERFORMANCE_TEST = "performance_test"
    
    # DevOps tasks (Hephaestus)
    INFRASTRUCTURE = "infrastructure"
    CI_CD_PIPELINE = "ci_cd_pipeline"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    SCALING = "scaling"


class AgentType(Enum):
    """AI agent types (Greek gods)."""
    APOLLO = "apollo"  # Backend
    APHRODITE = "aphrodite"  # Frontend
    ATHENA = "athena"  # QA
    HEPHAESTUS = "hephaestus"  # DevOps


@dataclass
class DevelopmentTask:
    """A single development task to be assigned to an agent."""
    id: str = field(default_factory=lambda: str(uuid4())[:8])
    name: str = ""
    description: str = ""
    type: TaskType = TaskType.API_ENDPOINT
    assigned_to: Optional[AgentType] = None
    priority: Priority = Priority.MEDIUM
    estimated_hours: int = 4
    dependencies: List[str] = field(default_factory=list)  # Task IDs
    requirements: List[str] = field(default_factory=list)  # Requirement IDs
    acceptance_criteria: List[str] = field(default_factory=list)
    technical_details: Dict[str, any] = field(default_factory=dict)


class TaskDecomposer:
    """Decomposes project briefs into development tasks."""
    
    def __init__(self):
        """Initialize the task decomposer."""
        # Task templates for common patterns
        self.task_templates = {
            ProjectType.AUTOMATION: [
                # Backend tasks
                ("Create job scheduler", TaskType.BUSINESS_LOGIC, AgentType.APOLLO, 8),
                ("Build data extraction service", TaskType.INTEGRATION, AgentType.APOLLO, 12),
                ("Implement processing pipeline", TaskType.BUSINESS_LOGIC, AgentType.APOLLO, 16),
                ("Create notification service", TaskType.API_ENDPOINT, AgentType.APOLLO, 8),
                # Frontend tasks (minimal for automation)
                ("Build configuration UI", TaskType.UI_COMPONENT, AgentType.APHRODITE, 8),
                ("Create status dashboard", TaskType.UI_COMPONENT, AgentType.APHRODITE, 12),
                # QA tasks
                ("Write unit tests for services", TaskType.UNIT_TEST, AgentType.ATHENA, 8),
                ("Test integration flows", TaskType.INTEGRATION_TEST, AgentType.ATHENA, 12),
                # DevOps tasks
                ("Set up job queue infrastructure", TaskType.INFRASTRUCTURE, AgentType.HEPHAESTUS, 8),
                ("Configure scheduled jobs", TaskType.DEPLOYMENT, AgentType.HEPHAESTUS, 4),
            ],
            ProjectType.WEB_APP: [
                # Backend tasks
                ("Design database schema", TaskType.DATABASE_SCHEMA, AgentType.APOLLO, 8),
                ("Implement REST API", TaskType.API_ENDPOINT, AgentType.APOLLO, 24),
                ("Build authentication system", TaskType.AUTHENTICATION, AgentType.APOLLO, 12),
                # Frontend tasks
                ("Design UI components", TaskType.UI_COMPONENT, AgentType.APHRODITE, 16),
                ("Implement user flows", TaskType.USER_FLOW, AgentType.APHRODITE, 20),
                ("Make responsive design", TaskType.RESPONSIVE_DESIGN, AgentType.APHRODITE, 12),
                # QA tasks
                ("Write comprehensive tests", TaskType.UNIT_TEST, AgentType.ATHENA, 16),
                ("Perform security audit", TaskType.SECURITY_AUDIT, AgentType.ATHENA, 8),
                # DevOps tasks
                ("Set up CI/CD pipeline", TaskType.CI_CD_PIPELINE, AgentType.HEPHAESTUS, 12),
                ("Configure production deployment", TaskType.DEPLOYMENT, AgentType.HEPHAESTUS, 8),
            ],
        }
        
        # Agent capabilities for matching
        self.agent_capabilities = {
            AgentType.APOLLO: {
                TaskType.API_ENDPOINT, TaskType.DATABASE_SCHEMA,
                TaskType.BUSINESS_LOGIC, TaskType.INTEGRATION,
                TaskType.AUTHENTICATION
            },
            AgentType.APHRODITE: {
                TaskType.UI_COMPONENT, TaskType.USER_FLOW,
                TaskType.RESPONSIVE_DESIGN, TaskType.STATE_MANAGEMENT
            },
            AgentType.ATHENA: {
                TaskType.UNIT_TEST, TaskType.INTEGRATION_TEST,
                TaskType.E2E_TEST, TaskType.SECURITY_AUDIT,
                TaskType.PERFORMANCE_TEST
            },
            AgentType.HEPHAESTUS: {
                TaskType.INFRASTRUCTURE, TaskType.CI_CD_PIPELINE,
                TaskType.DEPLOYMENT, TaskType.MONITORING,
                TaskType.SCALING
            }
        }
    
    def decompose_project(self, brief: ProjectBrief) -> List[DevelopmentTask]:
        """Decompose a project brief into development tasks."""
        tasks = []
        
        # Get base tasks from template
        base_tasks = self._get_template_tasks(brief.project_type)
        
        # Enhance tasks with specific requirements
        for template_name, task_type, agent, hours in base_tasks:
            task = self._create_task_from_template(
                template_name, task_type, agent, hours, brief
            )
            tasks.append(task)
        
        # Add custom tasks based on specific requirements
        custom_tasks = self._generate_custom_tasks(brief)
        tasks.extend(custom_tasks)
        
        # Set dependencies
        self._set_task_dependencies(tasks)
        
        # Adjust priorities based on brief
        self._adjust_priorities(tasks, brief)
        
        return tasks
    
    def _get_template_tasks(self, project_type: ProjectType) -> List[Tuple]:
        """Get template tasks for project type."""
        return self.task_templates.get(project_type, self.task_templates[ProjectType.WEB_APP])
    
    def _create_task_from_template(
        self,
        template_name: str,
        task_type: TaskType,
        agent: AgentType,
        hours: int,
        brief: ProjectBrief
    ) -> DevelopmentTask:
        """Create a task from template with project-specific details."""
        task = DevelopmentTask(
            name=template_name,
            type=task_type,
            assigned_to=agent,
            estimated_hours=hours,
            priority=brief.priority
        )
        
        # Add specific description based on project
        task.description = self._generate_task_description(task, brief)
        
        # Add acceptance criteria
        task.acceptance_criteria = self._generate_acceptance_criteria(task, brief)
        
        # Link to requirements
        task.requirements = self._link_requirements(task, brief)
        
        # Add technical details
        task.technical_details = self._extract_technical_details(task, brief)
        
        return task
    
    def _generate_task_description(self, task: DevelopmentTask, brief: ProjectBrief) -> str:
        """Generate detailed task description."""
        descriptions = {
            TaskType.API_ENDPOINT: f"Create REST API endpoints for {brief.name}. "
                                 f"Implement CRUD operations and business logic endpoints.",
            TaskType.DATABASE_SCHEMA: f"Design and implement database schema for {brief.name}. "
                                    f"Create models, relationships, and indexes.",
            TaskType.INTEGRATION: f"Integrate with external services for {brief.name}. "
                                f"Handle API authentication, rate limiting, and error recovery.",
            TaskType.UI_COMPONENT: f"Build user interface components for {brief.name}. "
                                 f"Create reusable, accessible, and responsive components.",
            TaskType.UNIT_TEST: f"Write comprehensive unit tests for {brief.name}. "
                              f"Achieve minimum 80% code coverage.",
            TaskType.INFRASTRUCTURE: f"Set up infrastructure for {brief.name}. "
                                   f"Configure servers, databases, and supporting services.",
        }
        
        base_desc = descriptions.get(task.type, f"Complete {task.name} for {brief.name}.")
        
        # Add specific details from requirements
        if task.type == TaskType.INTEGRATION and brief.technical_spec.integrations:
            integrations = ", ".join(brief.technical_spec.integrations[:3])
            base_desc += f" Specifically integrate with: {integrations}."
        
        return base_desc
    
    def _generate_acceptance_criteria(self, task: DevelopmentTask, brief: ProjectBrief) -> List[str]:
        """Generate acceptance criteria for task."""
        criteria = []
        
        # Common criteria by task type
        if task.type == TaskType.API_ENDPOINT:
            criteria.extend([
                "All endpoints return appropriate HTTP status codes",
                "API responses follow consistent JSON structure",
                "Endpoints are documented with OpenAPI/Swagger",
                "Rate limiting is implemented",
                "Error handling returns meaningful messages"
            ])
        elif task.type == TaskType.DATABASE_SCHEMA:
            criteria.extend([
                "Schema supports all required data relationships",
                "Indexes are created for performance",
                "Migrations are reversible",
                "Data integrity constraints are enforced"
            ])
        elif task.type == TaskType.UI_COMPONENT:
            criteria.extend([
                "Components are responsive across devices",
                "Accessibility standards (WCAG 2.1) are met",
                "Components follow design system guidelines",
                "Loading and error states are handled"
            ])
        elif task.type == TaskType.UNIT_TEST:
            criteria.extend([
                "Test coverage exceeds 80%",
                "All edge cases are tested",
                "Tests are isolated and repeatable",
                "Tests run in under 5 minutes"
            ])
        
        return criteria
    
    def _link_requirements(self, task: DevelopmentTask, brief: ProjectBrief) -> List[str]:
        """Link task to relevant requirements."""
        linked_reqs = []
        
        for req in brief.requirements:
            # Simple keyword matching for now
            if task.type == TaskType.API_ENDPOINT and "api" in req.description.lower():
                linked_reqs.append(req.id)
            elif task.type == TaskType.DATABASE_SCHEMA and any(
                word in req.description.lower() for word in ["store", "data", "save"]
            ):
                linked_reqs.append(req.id)
            elif task.type == TaskType.INTEGRATION and any(
                word in req.description.lower() for word in ["integrate", "connect", "external"]
            ):
                linked_reqs.append(req.id)
        
        return linked_reqs
    
    def _extract_technical_details(self, task: DevelopmentTask, brief: ProjectBrief) -> Dict:
        """Extract technical details relevant to task."""
        details = {}
        
        if task.type == TaskType.API_ENDPOINT:
            details["endpoints"] = brief.technical_spec.api_endpoints
            details["authentication"] = any("auth" in req for req in brief.technical_spec.security_requirements)
        elif task.type == TaskType.DATABASE_SCHEMA:
            details["models"] = brief.technical_spec.database_needs
            details["relationships"] = []  # Would be extracted from requirements
        elif task.type == TaskType.INTEGRATION:
            details["services"] = brief.technical_spec.integrations
            details["apis"] = [api for api in brief.technical_spec.api_endpoints if "external" in api.lower()]
        
        return details
    
    def _generate_custom_tasks(self, brief: ProjectBrief) -> List[DevelopmentTask]:
        """Generate custom tasks based on specific project requirements."""
        custom_tasks = []
        
        # Check for specific technical requirements
        if brief.technical_spec.security_requirements:
            custom_tasks.append(DevelopmentTask(
                name="Implement security requirements",
                description="Implement all security measures including " + 
                          ", ".join(brief.technical_spec.security_requirements[:3]),
                type=TaskType.AUTHENTICATION,
                assigned_to=AgentType.APOLLO,
                priority=Priority.HIGH,
                estimated_hours=16
            ))
        
        # Add monitoring if performance requirements exist
        if brief.technical_spec.performance_requirements:
            custom_tasks.append(DevelopmentTask(
                name="Set up performance monitoring",
                description="Configure monitoring for performance metrics",
                type=TaskType.MONITORING,
                assigned_to=AgentType.HEPHAESTUS,
                priority=Priority.MEDIUM,
                estimated_hours=8
            ))
        
        # Add extra testing for high-priority projects
        if brief.priority == Priority.CRITICAL:
            custom_tasks.append(DevelopmentTask(
                name="Comprehensive E2E testing",
                description="Full end-to-end testing of all user flows",
                type=TaskType.E2E_TEST,
                assigned_to=AgentType.ATHENA,
                priority=Priority.HIGH,
                estimated_hours=20
            ))
        
        return custom_tasks
    
    def _set_task_dependencies(self, tasks: List[DevelopmentTask]):
        """Set dependencies between tasks."""
        # Create task lookup
        task_by_type = {}
        for task in tasks:
            if task.type not in task_by_type:
                task_by_type[task.type] = []
            task_by_type[task.type].append(task)
        
        # Set common dependencies
        for task in tasks:
            if task.type == TaskType.API_ENDPOINT:
                # API depends on database schema
                if TaskType.DATABASE_SCHEMA in task_by_type:
                    task.dependencies.extend([t.id for t in task_by_type[TaskType.DATABASE_SCHEMA]])
            
            elif task.type in [TaskType.UNIT_TEST, TaskType.INTEGRATION_TEST]:
                # Tests depend on implementation
                if TaskType.API_ENDPOINT in task_by_type:
                    task.dependencies.extend([t.id for t in task_by_type[TaskType.API_ENDPOINT][:1]])
            
            elif task.type == TaskType.DEPLOYMENT:
                # Deployment depends on tests passing
                if TaskType.INTEGRATION_TEST in task_by_type:
                    task.dependencies.extend([t.id for t in task_by_type[TaskType.INTEGRATION_TEST]])
    
    def _adjust_priorities(self, tasks: List[DevelopmentTask], brief: ProjectBrief):
        """Adjust task priorities based on project context."""
        # If project is urgent, increase infrastructure priorities
        if brief.timeline.is_urgent:
            for task in tasks:
                if task.type in [TaskType.INFRASTRUCTURE, TaskType.CI_CD_PIPELINE]:
                    task.priority = Priority.HIGH
        
        # If security is mentioned, increase security task priorities  
        if brief.technical_spec.security_requirements:
            for task in tasks:
                if task.type in [TaskType.AUTHENTICATION, TaskType.SECURITY_AUDIT]:
                    task.priority = Priority.CRITICAL
    
    def assign_agents(self, tasks: List[DevelopmentTask]) -> Dict[AgentType, List[DevelopmentTask]]:
        """Group tasks by assigned agent."""
        assignments = {agent: [] for agent in AgentType}
        
        for task in tasks:
            if task.assigned_to:
                assignments[task.assigned_to].append(task)
        
        return assignments
    
    def estimate_timeline(self, tasks: List[DevelopmentTask]) -> Dict[str, any]:
        """Estimate project timeline based on tasks."""
        total_hours = sum(task.estimated_hours for task in tasks)
        
        # Calculate parallel execution potential
        assignments = self.assign_agents(tasks)
        max_agent_hours = max(
            sum(task.estimated_hours for task in agent_tasks)
            for agent_tasks in assignments.values()
        )
        
        # Assume 6 productive hours per day per agent
        days_needed = max_agent_hours / 6
        
        return {
            "total_hours": total_hours,
            "parallel_days": round(days_needed),
            "agents_needed": len([a for a, tasks in assignments.items() if tasks]),
            "critical_path_hours": max_agent_hours
        }


def test_task_decomposer():
    """Test the task decomposer."""
    from src.agents.specialists.hermes.project_brief import create_sample_brief
    
    # Create sample brief
    brief = create_sample_brief()
    
    # Decompose into tasks
    decomposer = TaskDecomposer()
    tasks = decomposer.decompose_project(brief)
    
    print(f"Generated {len(tasks)} tasks for: {brief.name}")
    print("=" * 60)
    
    # Show tasks by agent
    assignments = decomposer.assign_agents(tasks)
    for agent, agent_tasks in assignments.items():
        if agent_tasks:
            print(f"\n{agent.value.upper()} Tasks ({len(agent_tasks)}):")
            for task in agent_tasks:
                deps = f" [depends on: {', '.join(task.dependencies)}]" if task.dependencies else ""
                print(f"  - {task.name} ({task.estimated_hours}h) - {task.priority.value}{deps}")
    
    # Show timeline estimate
    timeline = decomposer.estimate_timeline(tasks)
    print(f"\nTimeline Estimate:")
    print(f"  Total work: {timeline['total_hours']} hours")
    print(f"  Parallel execution: {timeline['parallel_days']} days")
    print(f"  Agents needed: {timeline['agents_needed']}")


if __name__ == "__main__":
    test_task_decomposer()