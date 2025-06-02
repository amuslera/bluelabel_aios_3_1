#!/usr/bin/env python3
"""
Sprint Planning Collaboration Interface

This module provides an intelligent interface for collaborative sprint planning
between the human Product Owner and the AI Task Orchestrator.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

from orchestration.task_orchestrator import SprintObjective, Task, TaskPriority, TaskStatus
from src.agents.base.types import TaskType

logger = logging.getLogger(__name__)


class PlanningPhase(Enum):
    """Phases of sprint planning."""
    OBJECTIVE_SETTING = "objective_setting"
    TASK_BREAKDOWN = "task_breakdown"
    ESTIMATION = "estimation"
    ASSIGNMENT_PLANNING = "assignment_planning"
    CAPACITY_VALIDATION = "capacity_validation"
    FINALIZATION = "finalization"


class PlanningState(Enum):
    """State of the planning session."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress" 
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class PlanningSession:
    """Sprint planning session."""
    session_id: str
    sprint_name: str
    duration_days: int
    start_date: str
    objectives: List[SprintObjective]
    tasks: List[Task]
    current_phase: PlanningPhase
    state: PlanningState
    created_at: float
    human_id: str
    team_capacity: Dict[str, int]
    planning_notes: List[str]
    decisions: List[str]


@dataclass
class TaskEstimate:
    """Task estimation with confidence."""
    task_id: str
    estimated_hours: int
    confidence: float  # 0.0 to 1.0
    complexity: int   # 1-10 scale
    risk_factors: List[str]
    dependencies: List[str]
    suggested_agent_type: str


@dataclass
class CapacityAnalysis:
    """Team capacity analysis for sprint."""
    total_capacity_hours: int
    available_capacity_hours: int
    utilization_percentage: float
    agent_breakdown: Dict[str, Dict[str, Any]]
    overallocation_risk: str
    recommendations: List[str]


class SprintPlanner:
    """
    Intelligent sprint planning interface.
    
    Facilitates collaborative planning between human Product Owner and
    AI Task Orchestrator to create effective, achievable sprint plans.
    """
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.current_session: Optional[PlanningSession] = None
        self.planning_history: List[PlanningSession] = []
        
        # Planning templates and suggestions
        self.objective_templates = self._load_objective_templates()
        self.estimation_models = self._initialize_estimation_models()
        
        # Planning configuration
        self.default_sprint_days = 14
        self.planning_buffer_percentage = 20  # 20% capacity buffer
        self.complexity_multipliers = {1: 0.5, 2: 0.7, 3: 1.0, 4: 1.3, 5: 1.6, 
                                     6: 2.0, 7: 2.5, 8: 3.2, 9: 4.0, 10: 5.0}
    
    async def initiate_sprint_planning(self, human_id: str, sprint_name: str = None) -> str:
        """Initiate a new sprint planning session."""
        
        session_id = f"sprint_planning_{uuid.uuid4().hex[:8]}"
        
        if not sprint_name:
            sprint_name = f"Sprint {datetime.now().strftime('%Y-%m-%d')}"
        
        # Analyze current team capacity
        capacity = await self._analyze_team_capacity()
        
        session = PlanningSession(
            session_id=session_id,
            sprint_name=sprint_name,
            duration_days=self.default_sprint_days,
            start_date=datetime.now().strftime('%Y-%m-%d'),
            objectives=[],
            tasks=[],
            current_phase=PlanningPhase.OBJECTIVE_SETTING,
            state=PlanningState.IN_PROGRESS,
            created_at=time.time(),
            human_id=human_id,
            team_capacity=capacity.agent_breakdown,
            planning_notes=[],
            decisions=[]
        )
        
        self.current_session = session
        
        # Send planning initiation message
        await self._send_planning_message(
            "🎯 **Sprint Planning Session Started**",
            self._generate_planning_welcome_message(session, capacity)
        )
        
        logger.info(f"Sprint planning session initiated: {session_id}")
        return session_id
    
    async def _analyze_team_capacity(self) -> CapacityAnalysis:
        """Analyze current team capacity for sprint planning."""
        
        total_hours = 0
        available_hours = 0
        agent_breakdown = {}
        
        # Calculate capacity for each agent
        for agent_id, agent in self.orchestrator.agents.items():
            if not agent.availability:
                continue
            
            # Assume 8 hours per day, accounting for meetings/overhead
            daily_productive_hours = 6
            sprint_hours = daily_productive_hours * self.default_sprint_days
            
            current_workload_hours = agent.current_workload * 8  # Rough estimate
            available_agent_hours = max(0, sprint_hours - current_workload_hours)
            
            agent_breakdown[agent_id] = {
                "name": agent.name,
                "role": agent.role,
                "total_capacity": sprint_hours,
                "current_workload": current_workload_hours,
                "available_capacity": available_agent_hours,
                "utilization": (current_workload_hours / sprint_hours * 100) if sprint_hours > 0 else 0
            }
            
            total_hours += sprint_hours
            available_hours += available_agent_hours
        
        utilization = ((total_hours - available_hours) / total_hours * 100) if total_hours > 0 else 0
        
        # Generate recommendations
        recommendations = []
        if utilization > 80:
            recommendations.append("Team is highly utilized - consider reducing scope or extending timeline")
        elif utilization < 50:
            recommendations.append("Team has good capacity - opportunity for ambitious sprint goals")
        
        if available_hours < 40:
            recommendations.append("Limited available capacity - focus on high-priority items only")
        
        return CapacityAnalysis(
            total_capacity_hours=total_hours,
            available_capacity_hours=available_hours,
            utilization_percentage=utilization,
            agent_breakdown=agent_breakdown,
            overallocation_risk="high" if utilization > 90 else "medium" if utilization > 70 else "low",
            recommendations=recommendations
        )
    
    def _generate_planning_welcome_message(self, session: PlanningSession, capacity: CapacityAnalysis) -> str:
        """Generate welcome message for sprint planning."""
        
        return f"""Welcome to sprint planning for **{session.sprint_name}**!

**Sprint Details:**
• Duration: {session.duration_days} days
• Start Date: {session.start_date}
• Team Size: {len(capacity.agent_breakdown)} agents

**Team Capacity Analysis:**
• Total Capacity: {capacity.total_capacity_hours} hours
• Available: {capacity.available_capacity_hours} hours ({capacity.utilization_percentage:.1f}% utilized)
• Risk Level: {capacity.overallocation_risk.title()}

**Team Breakdown:**
{self._format_team_capacity(capacity.agent_breakdown)}

**Recommendations:**
{chr(10).join(f'• {rec}' for rec in capacity.recommendations)}

**Next Steps:**
1. Define sprint objectives and priorities
2. Break down objectives into specific tasks
3. Estimate effort and assign to team members
4. Validate capacity and finalize plan

**Let's start with your main objectives!** What are the 2-3 key things you want to achieve this sprint?"""
    
    def _format_team_capacity(self, agent_breakdown: Dict[str, Dict[str, Any]]) -> str:
        """Format team capacity for display."""
        lines = []
        for agent_data in agent_breakdown.values():
            utilization = agent_data['utilization']
            status = "🟢" if utilization < 70 else "🟡" if utilization < 90 else "🔴"
            lines.append(f"{status} {agent_data['name']} ({agent_data['role']}): {agent_data['available_capacity']}h available")
        return chr(10).join(lines)
    
    async def process_objectives_input(self, human_input: str):
        """Process human input for sprint objectives."""
        if not self.current_session:
            return
        
        session = self.current_session
        
        # Parse objectives from human input
        objectives = await self._parse_objectives_from_input(human_input)
        
        # Add to session
        session.objectives.extend(objectives)
        session.planning_notes.append(f"Objectives defined: {human_input}")
        
        # Send analysis and move to next phase
        await self._send_planning_message(
            "📋 **Objectives Analysis**",
            await self._analyze_objectives(objectives)
        )
        
        # Move to task breakdown phase
        session.current_phase = PlanningPhase.TASK_BREAKDOWN
        await self._initiate_task_breakdown_phase()
    
    async def _parse_objectives_from_input(self, human_input: str) -> List[SprintObjective]:
        """Parse sprint objectives from human input."""
        objectives = []
        
        # Simple parsing - split by lines/bullets and create objectives
        lines = human_input.strip().split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Clean up bullet points
            line = line.lstrip('•-*123456789. ')
            
            if len(line) > 10:  # Reasonable objective length
                objective_id = f"obj_{uuid.uuid4().hex[:8]}"
                
                # Determine priority based on order (first = high, etc.)
                priority = TaskPriority.HIGH if i == 0 else TaskPriority.MEDIUM if i < 3 else TaskPriority.LOW
                
                # Estimate effort based on complexity keywords
                effort = self._estimate_objective_effort(line)
                
                # Generate acceptance criteria suggestions
                acceptance_criteria = self._suggest_acceptance_criteria(line)
                
                objective = SprintObjective(
                    id=objective_id,
                    title=line,
                    description=f"Sprint objective: {line}",
                    priority=priority,
                    estimated_effort=effort,
                    acceptance_criteria=acceptance_criteria,
                    dependencies=[]
                )
                
                objectives.append(objective)
        
        return objectives
    
    def _estimate_objective_effort(self, objective_text: str) -> int:
        """Estimate effort for an objective based on text analysis."""
        text_lower = objective_text.lower()
        
        # Complexity indicators
        complexity_indicators = {
            'implement': 5, 'build': 5, 'create': 4, 'develop': 5,
            'design': 3, 'plan': 2, 'research': 3, 'analyze': 3,
            'refactor': 4, 'optimize': 4, 'fix': 2, 'update': 2,
            'integrate': 6, 'migrate': 7, 'deploy': 3, 'test': 3,
            'authentication': 6, 'database': 5, 'api': 4, 'ui': 4,
            'security': 6, 'performance': 5, 'monitoring': 4
        }
        
        base_effort = 3  # Default medium effort
        
        for keyword, effort_boost in complexity_indicators.items():
            if keyword in text_lower:
                base_effort = max(base_effort, effort_boost)
        
        # Scale modifiers
        if 'simple' in text_lower or 'basic' in text_lower:
            base_effort = max(1, base_effort - 2)
        elif 'complex' in text_lower or 'advanced' in text_lower:
            base_effort = min(10, base_effort + 2)
        elif 'comprehensive' in text_lower or 'complete' in text_lower:
            base_effort = min(10, base_effort + 3)
        
        return base_effort
    
    def _suggest_acceptance_criteria(self, objective_text: str) -> List[str]:
        """Suggest acceptance criteria for an objective."""
        text_lower = objective_text.lower()
        criteria = []
        
        # Standard criteria based on objective type
        if 'implement' in text_lower or 'build' in text_lower:
            criteria.extend([
                "Feature is implemented and functional",
                "Code is tested and reviewed",
                "Documentation is updated"
            ])
        
        if 'api' in text_lower:
            criteria.extend([
                "API endpoints are created and tested",
                "API documentation is complete",
                "Error handling is implemented"
            ])
        
        if 'ui' in text_lower or 'interface' in text_lower:
            criteria.extend([
                "UI components are implemented",
                "User interactions work as expected",
                "Design is responsive and accessible"
            ])
        
        if 'test' in text_lower:
            criteria.extend([
                "Test cases are written and passing",
                "Code coverage meets standards",
                "Edge cases are covered"
            ])
        
        # Generic criteria if no specific ones apply
        if not criteria:
            criteria = [
                "Objective requirements are met",
                "Implementation is complete and tested",
                "Quality standards are satisfied"
            ]
        
        return criteria
    
    async def _analyze_objectives(self, objectives: List[SprintObjective]) -> str:
        """Analyze sprint objectives and provide feedback."""
        
        total_effort = sum(obj.estimated_effort for obj in objectives)
        high_priority_count = len([obj for obj in objectives if obj.priority == TaskPriority.HIGH])
        
        analysis = f"""Great! I've analyzed your sprint objectives:

**Objectives Summary:**
{chr(10).join(f'• {obj.title} (Priority: {obj.priority.value.title()}, Effort: {obj.estimated_effort})' for obj in objectives)}

**Analysis:**
• Total Objectives: {len(objectives)}
• High Priority Items: {high_priority_count}
• Estimated Total Effort: {total_effort} story points
• Balance: {'Good mix of priorities' if len(set(obj.priority for obj in objectives)) > 1 else 'Consider varying priorities'}

**Capacity Check:**
"""
        
        # Add capacity analysis
        capacity = await self._analyze_team_capacity()
        estimated_hours = total_effort * 8  # Rough conversion
        
        if estimated_hours <= capacity.available_capacity_hours:
            analysis += f"✅ Fits within team capacity ({capacity.available_capacity_hours}h available)\n"
        else:
            analysis += f"⚠️ May exceed capacity ({estimated_hours}h estimated vs {capacity.available_capacity_hours}h available)\n"
        
        analysis += "\n**Next:** Let's break these down into specific, actionable tasks."
        
        return analysis
    
    async def _initiate_task_breakdown_phase(self):
        """Initiate the task breakdown phase."""
        if not self.current_session:
            return
        
        session = self.current_session
        
        # Generate initial task suggestions
        suggested_tasks = await self._generate_task_suggestions(session.objectives)
        
        message = f"""📋 **Task Breakdown Phase**

Now let's break down your objectives into specific tasks. I've generated some initial suggestions:

**Suggested Tasks:**
{chr(10).join(f'• {task["title"]} ({task["type"]}, {task["effort"]}h)' for task in suggested_tasks)}

**Options:**
1. **Accept suggestions** - I'll create these tasks and we can refine them
2. **Modify suggestions** - Tell me what to change or add
3. **Manual breakdown** - You specify the exact tasks you want

**Task Guidelines:**
• Each task should be completable by one person in 1-8 hours
• Tasks should have clear deliverables and acceptance criteria
• Consider dependencies between tasks

What would you like to do? Accept my suggestions, modify them, or create your own breakdown?"""
        
        await self._send_planning_message("📋 **Task Breakdown**", message)
    
    async def _generate_task_suggestions(self, objectives: List[SprintObjective]) -> List[Dict[str, Any]]:
        """Generate task suggestions based on objectives."""
        suggested_tasks = []
        
        for objective in objectives:
            obj_tasks = self._break_down_objective_to_tasks(objective)
            suggested_tasks.extend(obj_tasks)
        
        return suggested_tasks
    
    def _break_down_objective_to_tasks(self, objective: SprintObjective) -> List[Dict[str, Any]]:
        """Break down an objective into specific tasks."""
        tasks = []
        obj_text = objective.title.lower()
        
        # Common task patterns based on objective content
        if 'implement' in obj_text or 'build' in obj_text:
            tasks.extend([
                {"title": f"Design architecture for {objective.title}", "type": "Architecture", "effort": 2},
                {"title": f"Implement core functionality for {objective.title}", "type": "Implementation", "effort": 4},
                {"title": f"Write tests for {objective.title}", "type": "Testing", "effort": 2},
                {"title": f"Document {objective.title}", "type": "Documentation", "effort": 1}
            ])
        
        elif 'api' in obj_text:
            tasks.extend([
                {"title": f"Design API endpoints for {objective.title}", "type": "API Design", "effort": 2},
                {"title": f"Implement API routes for {objective.title}", "type": "Implementation", "effort": 3},
                {"title": f"Add API validation and error handling", "type": "Implementation", "effort": 2},
                {"title": f"Write API tests", "type": "Testing", "effort": 2},
                {"title": f"Create API documentation", "type": "Documentation", "effort": 1}
            ])
        
        elif 'ui' in obj_text or 'interface' in obj_text:
            tasks.extend([
                {"title": f"Design UI mockups for {objective.title}", "type": "UI Design", "effort": 2},
                {"title": f"Implement UI components for {objective.title}", "type": "Implementation", "effort": 4},
                {"title": f"Add responsive styling", "type": "Implementation", "effort": 2},
                {"title": f"Test UI interactions", "type": "Testing", "effort": 2}
            ])
        
        elif 'test' in obj_text:
            tasks.extend([
                {"title": f"Design test strategy for {objective.title}", "type": "Planning", "effort": 1},
                {"title": f"Write unit tests", "type": "Testing", "effort": 3},
                {"title": f"Write integration tests", "type": "Testing", "effort": 3},
                {"title": f"Set up automated testing", "type": "Infrastructure", "effort": 2}
            ])
        
        else:
            # Generic breakdown
            tasks.extend([
                {"title": f"Plan approach for {objective.title}", "type": "Planning", "effort": 1},
                {"title": f"Implement {objective.title}", "type": "Implementation", "effort": 4},
                {"title": f"Test {objective.title}", "type": "Testing", "effort": 2},
                {"title": f"Review and document {objective.title}", "type": "Review", "effort": 1}
            ])
        
        return tasks
    
    async def process_task_breakdown_response(self, human_input: str):
        """Process human response to task breakdown suggestions."""
        if not self.current_session:
            return
        
        session = self.current_session
        input_lower = human_input.lower()
        
        if 'accept' in input_lower:
            # Accept suggested tasks
            await self._create_tasks_from_suggestions()
            session.decisions.append("Accepted task breakdown suggestions")
            
        elif 'modify' in input_lower or 'change' in input_lower:
            # Request modifications
            await self._request_task_modifications()
            return
            
        elif 'manual' in input_lower or 'own' in input_lower:
            # Manual task specification
            await self._request_manual_task_breakdown()
            return
        
        else:
            # Try to parse as custom task list
            custom_tasks = await self._parse_custom_tasks(human_input)
            if custom_tasks:
                await self._create_custom_tasks(custom_tasks)
                session.decisions.append("Created custom task breakdown")
            else:
                await self._clarify_task_breakdown_response()
                return
        
        # Move to estimation phase
        session.current_phase = PlanningPhase.ESTIMATION
        await self._initiate_estimation_phase()
    
    async def _create_tasks_from_suggestions(self):
        """Create tasks from the generated suggestions."""
        if not self.current_session:
            return
        
        session = self.current_session
        suggested_tasks = await self._generate_task_suggestions(session.objectives)
        
        for i, task_data in enumerate(suggested_tasks):
            task_id = f"task_{uuid.uuid4().hex[:8]}"
            
            # Map task type string to TaskType enum
            task_type = self._map_task_type(task_data["type"])
            
            # Determine parent objective
            parent_obj = session.objectives[i // 4] if session.objectives else None
            
            task = Task(
                id=task_id,
                title=task_data["title"],
                description=f"Task for sprint: {task_data['title']}",
                task_type=task_type,
                priority=parent_obj.priority if parent_obj else TaskPriority.MEDIUM,
                status=TaskStatus.PLANNED,
                estimated_effort=task_data["effort"],
                parent_objective=parent_obj.id if parent_obj else None,
                acceptance_criteria=[
                    "Task is completed according to requirements",
                    "Code is tested and reviewed",
                    "Documentation is updated as needed"
                ]
            )
            
            session.tasks.append(task)
            self.orchestrator.tasks[task_id] = task
        
        logger.info(f"Created {len(suggested_tasks)} tasks from suggestions")
    
    def _map_task_type(self, type_string: str) -> TaskType:
        """Map task type string to TaskType enum."""
        type_mapping = {
            "Architecture": TaskType.ARCHITECTURE,
            "Implementation": TaskType.IMPLEMENTATION,
            "Testing": TaskType.TESTING,
            "Documentation": TaskType.DOCUMENTATION,
            "API Design": TaskType.API_DESIGN,
            "UI Design": TaskType.UI_DESIGN,
            "Planning": TaskType.PLANNING,
            "Review": TaskType.REVIEW,
            "Infrastructure": TaskType.INFRASTRUCTURE
        }
        return type_mapping.get(type_string, TaskType.GENERAL)
    
    async def _initiate_estimation_phase(self):
        """Initiate the effort estimation phase."""
        if not self.current_session:
            return
        
        session = self.current_session
        
        # Analyze tasks and provide estimation review
        task_analysis = self._analyze_task_estimates(session.tasks)
        
        message = f"""📊 **Effort Estimation Review**

I've analyzed the effort estimates for our {len(session.tasks)} tasks:

**Estimation Summary:**
{task_analysis}

**Estimation Questions:**
• Do these estimates seem reasonable for your team?
• Are there any tasks that seem under/over-estimated?
• Should we break down any large tasks further?
• Are there any missing dependencies?

**Options:**
1. **Estimates look good** - Proceed to assignment planning
2. **Adjust estimates** - Tell me which tasks need revision
3. **Review in detail** - Go through each task individually

What would you like to do?"""
        
        await self._send_planning_message("📊 **Estimation Review**", message)
    
    def _analyze_task_estimates(self, tasks: List[Task]) -> str:
        """Analyze task effort estimates."""
        if not tasks:
            return "No tasks to analyze"
        
        total_hours = sum(task.estimated_effort for task in tasks)
        avg_hours = total_hours / len(tasks)
        
        # Categorize tasks by size
        small_tasks = [t for t in tasks if t.estimated_effort <= 2]
        medium_tasks = [t for t in tasks if 3 <= t.estimated_effort <= 5]
        large_tasks = [t for t in tasks if t.estimated_effort >= 6]
        
        # Group by type
        type_breakdown = {}
        for task in tasks:
            task_type = task.task_type.value
            if task_type not in type_breakdown:
                type_breakdown[task_type] = []
            type_breakdown[task_type].append(task.estimated_effort)
        
        analysis = f"""• Total Estimated Hours: {total_hours}h
• Average Task Size: {avg_hours:.1f}h
• Task Distribution: {len(small_tasks)} small (≤2h), {len(medium_tasks)} medium (3-5h), {len(large_tasks)} large (≥6h)

**By Task Type:**
{chr(10).join(f'• {task_type.replace("_", " ").title()}: {len(hours)}x tasks, {sum(hours)}h total' for task_type, hours in type_breakdown.items())}

**Risk Assessment:**
"""
        
        # Risk factors
        if len(large_tasks) > len(tasks) * 0.3:
            analysis += "⚠️ Many large tasks - consider breaking down further\n"
        if total_hours > 100:
            analysis += "⚠️ High total effort - may need to reduce scope\n"
        if len(set(task.task_type for task in tasks)) < 3:
            analysis += "ℹ️ Limited task variety - good for focused sprint\n"
        
        return analysis
    
    async def process_estimation_response(self, human_input: str):
        """Process human response to estimation review."""
        if not self.current_session:
            return
        
        session = self.current_session
        input_lower = human_input.lower()
        
        if 'good' in input_lower or 'proceed' in input_lower:
            # Estimates approved
            session.decisions.append("Approved effort estimates")
            session.current_phase = PlanningPhase.ASSIGNMENT_PLANNING
            await self._initiate_assignment_planning()
            
        elif 'adjust' in input_lower or 'revise' in input_lower:
            # Request estimate adjustments
            await self._request_estimate_adjustments()
            
        elif 'review' in input_lower or 'detail' in input_lower:
            # Detailed review
            await self._initiate_detailed_estimation_review()
            
        else:
            # Try to parse specific estimate adjustments
            adjustments = self._parse_estimate_adjustments(human_input)
            if adjustments:
                await self._apply_estimate_adjustments(adjustments)
                session.current_phase = PlanningPhase.ASSIGNMENT_PLANNING
                await self._initiate_assignment_planning()
            else:
                await self._clarify_estimation_response()
    
    async def _initiate_assignment_planning(self):
        """Initiate the task assignment planning phase."""
        if not self.current_session:
            return
        
        session = self.current_session
        
        # Generate assignment recommendations
        assignments = await self._generate_assignment_recommendations(session.tasks)
        
        # Capacity validation
        capacity_check = await self._validate_sprint_capacity(session.tasks, assignments)
        
        message = f"""🎯 **Task Assignment Planning**

Based on team expertise and current workload, here are my assignment recommendations:

**Recommended Assignments:**
{chr(10).join(f'• {assignment["task_title"]} → {assignment["agent_name"]} ({assignment["reasoning"]})' for assignment in assignments)}

**Capacity Validation:**
{capacity_check}

**Options:**
1. **Accept assignments** - I'll assign tasks and we're ready to start!
2. **Modify assignments** - Tell me what to change
3. **Review capacity** - Look at detailed capacity analysis

Ready to finalize the sprint plan?"""
        
        await self._send_planning_message("🎯 **Assignment Planning**", message)
    
    async def _generate_assignment_recommendations(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """Generate task assignment recommendations."""
        from orchestration.assignment_engine import AssignmentEngine
        
        assignment_engine = AssignmentEngine()
        assignments = []
        
        for task in tasks:
            best_assignment = assignment_engine.find_best_assignment(
                task, self.orchestrator.agents, self.orchestrator.tasks
            )
            
            if best_assignment:
                agent = self.orchestrator.agents[best_assignment.agent_id]
                assignments.append({
                    "task_id": task.id,
                    "task_title": task.title,
                    "agent_id": best_assignment.agent_id,
                    "agent_name": agent.name,
                    "reasoning": best_assignment.reasoning,
                    "confidence": best_assignment.total_score
                })
        
        return assignments
    
    async def _validate_sprint_capacity(self, tasks: List[Task], assignments: List[Dict[str, Any]]) -> str:
        """Validate that sprint fits within team capacity."""
        
        # Calculate workload by agent
        agent_workload = {}
        total_hours = 0
        
        for assignment in assignments:
            agent_id = assignment["agent_id"]
            task = next(t for t in tasks if t.id == assignment["task_id"])
            
            if agent_id not in agent_workload:
                agent_workload[agent_id] = {"name": assignment["agent_name"], "hours": 0}
            
            agent_workload[agent_id]["hours"] += task.estimated_effort
            total_hours += task.estimated_effort
        
        # Compare with capacity
        capacity = await self._analyze_team_capacity()
        
        validation = f"""**Workload Distribution:**
{chr(10).join(f'• {data["name"]}: {data["hours"]}h' for data in agent_workload.values())}

**Overall Capacity:**
• Total Sprint Work: {total_hours}h
• Available Capacity: {capacity.available_capacity_hours}h
• Utilization: {(total_hours / capacity.available_capacity_hours * 100) if capacity.available_capacity_hours > 0 else 0:.1f}%
"""
        
        if total_hours <= capacity.available_capacity_hours:
            validation += "\n✅ Sprint fits comfortably within team capacity"
        elif total_hours <= capacity.available_capacity_hours * 1.1:
            validation += "\n⚠️ Sprint at capacity limit - manageable but tight"
        else:
            validation += "\n🚨 Sprint exceeds capacity - recommend reducing scope"
        
        return validation
    
    async def finalize_sprint_plan(self):
        """Finalize the sprint plan and begin execution."""
        if not self.current_session:
            return
        
        session = self.current_session
        session.state = PlanningState.COMPLETED
        session.current_phase = PlanningPhase.FINALIZATION
        
        # Save to history
        self.planning_history.append(session)
        
        # Create sprint in orchestrator
        sprint_id = f"sprint_{uuid.uuid4().hex[:8]}"
        self.orchestrator.current_sprint = sprint_id
        
        # Assign tasks as planned
        assignments = await self._generate_assignment_recommendations(session.tasks)
        for assignment in assignments:
            await self.orchestrator.assign_task_to_agent(
                assignment["task_id"], 
                assignment["agent_id"]
            )
        
        # Send completion message
        summary = await self._generate_sprint_summary(session)
        
        await self._send_planning_message(
            "🎉 **Sprint Plan Finalized!**",
            f"""{summary}

**Sprint is now ACTIVE!** 🚀

I'll monitor progress, help resolve blockers, and keep you updated on our progress toward the sprint goals.

The team is ready to start working. Let's build something amazing together!"""
        )
        
        # Clear current session
        self.current_session = None
        
        logger.info(f"Sprint plan finalized: {session.sprint_name}")
    
    async def _generate_sprint_summary(self, session: PlanningSession) -> str:
        """Generate a comprehensive sprint summary."""
        
        total_tasks = len(session.tasks)
        total_hours = sum(task.estimated_effort for task in session.tasks)
        
        # Group tasks by priority and type
        priority_breakdown = {}
        type_breakdown = {}
        
        for task in session.tasks:
            # Priority
            priority = task.priority.value
            if priority not in priority_breakdown:
                priority_breakdown[priority] = 0
            priority_breakdown[priority] += 1
            
            # Type
            task_type = task.task_type.value
            if task_type not in type_breakdown:
                type_breakdown[task_type] = 0
            type_breakdown[task_type] += 1
        
        summary = f"""**{session.sprint_name} - Sprint Plan Summary**

**Objectives:** {len(session.objectives)} main goals
**Tasks:** {total_tasks} tasks, {total_hours}h estimated effort
**Duration:** {session.duration_days} days
**Team:** {len(self.orchestrator.agents)} agents

**Priority Breakdown:**
{chr(10).join(f'• {priority.title()}: {count} tasks' for priority, count in priority_breakdown.items())}

**Task Type Breakdown:**
{chr(10).join(f'• {task_type.replace("_", " ").title()}: {count}' for task_type, count in type_breakdown.items())}

**Key Decisions Made:**
{chr(10).join(f'• {decision}' for decision in session.decisions)}"""
        
        return summary
    
    async def _send_planning_message(self, title: str, content: str):
        """Send planning message to the team."""
        await self.orchestrator.send_message({
            "type": "chat",
            "from_id": self.orchestrator.orchestrator_id,
            "content": f"{title}\n\n{content}",
            "metadata": {
                "planning_message": True,
                "session_id": self.current_session.session_id if self.current_session else None
            }
        })
    
    def _load_objective_templates(self) -> Dict[str, Any]:
        """Load common objective templates."""
        return {
            "feature_development": {
                "template": "Implement {feature_name} with {key_capabilities}",
                "tasks": ["Design", "Implement", "Test", "Document"],
                "effort_range": (5, 15)
            },
            "infrastructure": {
                "template": "Set up {infrastructure_component} for {purpose}",
                "tasks": ["Plan", "Configure", "Deploy", "Monitor"],
                "effort_range": (3, 10)
            },
            "improvement": {
                "template": "Improve {area} by {improvement_type}",
                "tasks": ["Analyze", "Design", "Implement", "Validate"],
                "effort_range": (2, 8)
            }
        }
    
    def _initialize_estimation_models(self) -> Dict[str, Any]:
        """Initialize effort estimation models."""
        return {
            "complexity_factors": {
                "integration": 1.5,
                "new_technology": 1.8,
                "security": 1.3,
                "performance": 1.4,
                "user_interface": 1.2
            },
            "team_velocity": 1.0  # Will be updated based on historical data
        }


# Utility functions
async def create_sprint_planner(orchestrator) -> SprintPlanner:
    """Create and initialize a sprint planner."""
    return SprintPlanner(orchestrator)