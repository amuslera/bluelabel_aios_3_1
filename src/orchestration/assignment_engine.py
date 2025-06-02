#!/usr/bin/env python3
"""
Intelligent Task Assignment Engine

This module provides sophisticated algorithms for assigning tasks to agents
based on their capabilities, workload, expertise, and historical performance.
"""

import logging
import time
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass
from enum import Enum

from orchestration.task_orchestrator import Task, AgentCapability, TaskPriority, TaskStatus
from src.agents.base.types import TaskType

logger = logging.getLogger(__name__)


class AssignmentStrategy(Enum):
    """Different strategies for task assignment."""
    LOAD_BALANCED = "load_balanced"
    EXPERTISE_OPTIMIZED = "expertise_optimized"
    DEADLINE_DRIVEN = "deadline_driven"
    DEPENDENCY_AWARE = "dependency_aware"
    HYBRID = "hybrid"


@dataclass
class AssignmentScore:
    """Score calculation for task assignment."""
    agent_id: str
    total_score: float
    expertise_score: float
    workload_score: float
    availability_score: float
    dependency_score: float
    historical_score: float
    reasoning: str


@dataclass
class WorkloadMetrics:
    """Agent workload analysis."""
    current_tasks: int
    estimated_hours: float
    utilization_percentage: float
    capacity_remaining: int
    projected_completion: Optional[float]


class AssignmentEngine:
    """
    Intelligent engine for assigning tasks to agents.
    
    Uses multiple factors including:
    - Agent expertise and capabilities
    - Current workload and availability
    - Task dependencies and deadlines
    - Historical performance
    - Team dynamics and collaboration patterns
    """
    
    def __init__(self):
        self.assignment_history: Dict[str, List[str]] = {}  # agent_id -> task_ids
        self.performance_metrics: Dict[str, Dict[str, float]] = {}  # agent_id -> metrics
        self.collaboration_patterns: Dict[str, Set[str]] = {}  # agent_id -> collaborator_ids
        
    def find_best_assignment(
        self,
        task: Task,
        available_agents: Dict[str, AgentCapability],
        current_tasks: Dict[str, Task],
        strategy: AssignmentStrategy = AssignmentStrategy.HYBRID
    ) -> Optional[AssignmentScore]:
        """
        Find the best agent assignment for a given task.
        
        Args:
            task: Task to be assigned
            available_agents: Available agents with their capabilities
            current_tasks: Currently active tasks
            strategy: Assignment strategy to use
            
        Returns:
            AssignmentScore with best agent and reasoning, or None if no suitable agent
        """
        if not available_agents:
            logger.warning(f"No available agents for task {task.id}")
            return None
        
        # Filter agents by basic capabilities
        capable_agents = self._filter_capable_agents(task, available_agents)
        if not capable_agents:
            logger.warning(f"No capable agents found for task {task.id} (type: {task.task_type})")
            return None
        
        # Calculate scores for each capable agent
        scores = []
        for agent_id, agent in capable_agents.items():
            score = self._calculate_assignment_score(
                task, agent, current_tasks, strategy
            )
            scores.append(score)
        
        # Sort by total score and return best
        scores.sort(key=lambda x: x.total_score, reverse=True)
        best_assignment = scores[0]
        
        logger.info(f"Best assignment for '{task.title}': {best_assignment.agent_id} "
                   f"(score: {best_assignment.total_score:.2f})")
        
        return best_assignment
    
    def _filter_capable_agents(
        self,
        task: Task,
        available_agents: Dict[str, AgentCapability]
    ) -> Dict[str, AgentCapability]:
        """Filter agents that can handle the task type."""
        capable = {}
        
        for agent_id, agent in available_agents.items():
            # Check basic availability
            if not agent.availability:
                continue
            
            # Check if agent can handle this task type
            if task.task_type in agent.capabilities:
                capable[agent_id] = agent
                continue
            
            # Special cases for flexible assignment
            if task.task_type == TaskType.GENERAL and agent.capabilities:
                capable[agent_id] = agent
                continue
        
        return capable
    
    def _calculate_assignment_score(
        self,
        task: Task,
        agent: AgentCapability,
        current_tasks: Dict[str, Task],
        strategy: AssignmentStrategy
    ) -> AssignmentScore:
        """Calculate comprehensive assignment score for agent."""
        
        # Calculate individual score components
        expertise_score = self._calculate_expertise_score(task, agent)
        workload_score = self._calculate_workload_score(agent, current_tasks)
        availability_score = self._calculate_availability_score(agent)
        dependency_score = self._calculate_dependency_score(task, agent, current_tasks)
        historical_score = self._calculate_historical_score(task, agent)
        
        # Combine scores based on strategy
        total_score = self._combine_scores(
            strategy,
            expertise_score,
            workload_score,
            availability_score,
            dependency_score,
            historical_score
        )
        
        # Generate reasoning
        reasoning = self._generate_assignment_reasoning(
            agent, expertise_score, workload_score, availability_score
        )
        
        return AssignmentScore(
            agent_id=agent.agent_id,
            total_score=total_score,
            expertise_score=expertise_score,
            workload_score=workload_score,
            availability_score=availability_score,
            dependency_score=dependency_score,
            historical_score=historical_score,
            reasoning=reasoning
        )
    
    def _calculate_expertise_score(self, task: Task, agent: AgentCapability) -> float:
        """Calculate how well agent's expertise matches the task."""
        base_score = 0.0
        
        # Primary capability match
        if task.task_type in agent.capabilities:
            base_score += 50.0
        
        # Expertise level matching
        task_desc_lower = task.description.lower()
        expertise_bonuses = 0.0
        
        for domain, level in agent.expertise_level.items():
            if domain.lower() in task_desc_lower:
                expertise_bonuses += level * 5.0  # Max 50 points for level 10
        
        # Role-specific bonuses
        role_bonus = self._get_role_task_bonus(agent.role, task.task_type)
        
        final_score = min(100.0, base_score + expertise_bonuses + role_bonus)
        return final_score
    
    def _get_role_task_bonus(self, role: str, task_type: TaskType) -> float:
        """Get bonus points for role-task type alignment."""
        role_task_alignment = {
            "cto": {
                TaskType.SYSTEM_DESIGN: 20.0,
                TaskType.PLANNING: 15.0,
                TaskType.REQUIREMENTS_ANALYSIS: 15.0,
                TaskType.ARCHITECTURE_REVIEW: 20.0,
                TaskType.TECH_DECISION: 15.0
            },
            "backend-dev": {
                TaskType.CODE_GENERATION: 20.0,
                TaskType.CODE_REVIEW: 15.0,
                TaskType.BUG_FIX: 15.0,
                TaskType.TESTING: 10.0,
                TaskType.REFACTORING: 10.0
            },
            "frontend-dev": {
                TaskType.CODE_GENERATION: 20.0,
                TaskType.CODE_REVIEW: 15.0,
                TaskType.TESTING: 10.0
            },
            "qa": {
                TaskType.TESTING: 20.0,
                TaskType.CODE_REVIEW: 15.0,
                TaskType.PERFORMANCE_ANALYSIS: 10.0,
                TaskType.REQUIREMENTS_ANALYSIS: 5.0
            },
            "devops": {
                TaskType.DEPLOYMENT: 20.0,
                TaskType.INFRASTRUCTURE: 15.0,
                TaskType.MONITORING_SETUP: 10.0,
                TaskType.CI_CD: 15.0
            }
        }
        
        return role_task_alignment.get(role, {}).get(task_type, 0.0)
    
    def _calculate_workload_score(
        self,
        agent: AgentCapability,
        current_tasks: Dict[str, Task]
    ) -> float:
        """Calculate score based on agent's current workload."""
        
        # Get workload metrics
        metrics = self._calculate_workload_metrics(agent, current_tasks)
        
        # Score inversely related to utilization
        # 0% utilization = 100 points, 100% utilization = 0 points
        utilization_score = max(0.0, 100.0 - metrics.utilization_percentage)
        
        # Bonus for agents with some capacity remaining
        if metrics.capacity_remaining > 0:
            capacity_bonus = min(20.0, metrics.capacity_remaining * 10.0)
        else:
            capacity_bonus = -50.0  # Penalty for overloaded agents
        
        final_score = max(0.0, utilization_score + capacity_bonus)
        return final_score
    
    def _calculate_workload_metrics(
        self,
        agent: AgentCapability,
        current_tasks: Dict[str, Task]
    ) -> WorkloadMetrics:
        """Calculate detailed workload metrics for agent."""
        
        # Count current tasks assigned to agent
        agent_tasks = [
            task for task in current_tasks.values()
            if (task.assigned_to == agent.agent_id and 
                task.status in [TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS])
        ]
        
        current_task_count = len(agent_tasks)
        estimated_hours = sum(task.estimated_effort for task in agent_tasks)
        
        # Calculate utilization percentage
        max_concurrent_hours = agent.max_workload * 8  # Assume 8 hours per task slot
        utilization = (estimated_hours / max_concurrent_hours * 100) if max_concurrent_hours > 0 else 0
        
        # Calculate remaining capacity
        capacity_remaining = max(0, agent.max_workload - current_task_count)
        
        # Estimate completion time for current workload
        projected_completion = None
        if agent_tasks:
            # Simple estimation: assume tasks complete in estimated time
            completion_times = [
                task.assigned_at + (task.estimated_effort * 3600)  # Convert hours to seconds
                for task in agent_tasks
                if task.assigned_at
            ]
            if completion_times:
                projected_completion = max(completion_times)
        
        return WorkloadMetrics(
            current_tasks=current_task_count,
            estimated_hours=estimated_hours,
            utilization_percentage=utilization,
            capacity_remaining=capacity_remaining,
            projected_completion=projected_completion
        )
    
    def _calculate_availability_score(self, agent: AgentCapability) -> float:
        """Calculate availability score based on agent status."""
        if not agent.availability:
            return 0.0
        
        # Check how recently agent was seen
        time_since_seen = time.time() - agent.last_seen
        
        if time_since_seen < 300:  # 5 minutes
            return 100.0
        elif time_since_seen < 900:  # 15 minutes
            return 80.0
        elif time_since_seen < 1800:  # 30 minutes
            return 60.0
        else:
            return 30.0  # Agent may be inactive
    
    def _calculate_dependency_score(
        self,
        task: Task,
        agent: AgentCapability,
        current_tasks: Dict[str, Task]
    ) -> float:
        """Calculate score based on task dependencies and agent relationships."""
        score = 50.0  # Base score
        
        # Check if agent is already working on related tasks
        agent_current_tasks = [
            t for t in current_tasks.values()
            if t.assigned_to == agent.agent_id and t.status == TaskStatus.IN_PROGRESS
        ]
        
        # Bonus for working on related/dependent tasks
        for current_task in agent_current_tasks:
            if (task.id in current_task.dependencies or
                current_task.id in task.dependencies):
                score += 25.0  # Continuity bonus
            
            # Check for same parent objective
            if (task.parent_objective and
                current_task.parent_objective == task.parent_objective):
                score += 15.0  # Same epic bonus
        
        # Check collaboration patterns
        if agent.agent_id in self.collaboration_patterns:
            collaborators = self.collaboration_patterns[agent.agent_id]
            
            # See if any collaborators are working on dependencies
            for dep_id in task.dependencies:
                dep_task = current_tasks.get(dep_id)
                if dep_task and dep_task.assigned_to in collaborators:
                    score += 10.0  # Collaboration bonus
        
        return min(100.0, score)
    
    def _calculate_historical_score(self, task: Task, agent: AgentCapability) -> float:
        """Calculate score based on agent's historical performance."""
        agent_id = agent.agent_id
        
        if agent_id not in self.performance_metrics:
            return 50.0  # Neutral score for new agents
        
        metrics = self.performance_metrics[agent_id]
        
        # Factors to consider
        completion_rate = metrics.get("completion_rate", 0.5)  # 0.0 to 1.0
        quality_score = metrics.get("quality_score", 0.5)      # 0.0 to 1.0
        time_accuracy = metrics.get("time_accuracy", 0.5)      # 0.0 to 1.0
        
        # Calculate weighted score
        historical_score = (
            completion_rate * 40.0 +  # 40% weight on completion
            quality_score * 35.0 +    # 35% weight on quality
            time_accuracy * 25.0      # 25% weight on timing
        )
        
        return historical_score
    
    def _combine_scores(
        self,
        strategy: AssignmentStrategy,
        expertise: float,
        workload: float,
        availability: float,
        dependency: float,
        historical: float
    ) -> float:
        """Combine individual scores based on assignment strategy."""
        
        if strategy == AssignmentStrategy.EXPERTISE_OPTIMIZED:
            return (
                expertise * 0.5 +
                availability * 0.2 +
                historical * 0.15 +
                workload * 0.1 +
                dependency * 0.05
            )
        
        elif strategy == AssignmentStrategy.LOAD_BALANCED:
            return (
                workload * 0.4 +
                availability * 0.3 +
                expertise * 0.2 +
                historical * 0.05 +
                dependency * 0.05
            )
        
        elif strategy == AssignmentStrategy.DEADLINE_DRIVEN:
            return (
                availability * 0.4 +
                workload * 0.3 +
                expertise * 0.2 +
                historical * 0.05 +
                dependency * 0.05
            )
        
        elif strategy == AssignmentStrategy.DEPENDENCY_AWARE:
            return (
                dependency * 0.4 +
                expertise * 0.25 +
                availability * 0.2 +
                workload * 0.1 +
                historical * 0.05
            )
        
        else:  # HYBRID (default)
            return (
                expertise * 0.3 +
                workload * 0.25 +
                availability * 0.2 +
                dependency * 0.15 +
                historical * 0.1
            )
    
    def _generate_assignment_reasoning(
        self,
        agent: AgentCapability,
        expertise_score: float,
        workload_score: float,
        availability_score: float
    ) -> str:
        """Generate human-readable reasoning for assignment decision."""
        
        reasons = []
        
        # Expertise reasoning
        if expertise_score >= 80:
            reasons.append(f"{agent.name} has excellent expertise for this task type")
        elif expertise_score >= 60:
            reasons.append(f"{agent.name} has good expertise for this task")
        else:
            reasons.append(f"{agent.name} can handle this task with moderate expertise")
        
        # Workload reasoning
        if workload_score >= 80:
            reasons.append("has light current workload")
        elif workload_score >= 60:
            reasons.append("has manageable current workload")
        elif workload_score >= 40:
            reasons.append("has moderate current workload")
        else:
            reasons.append("is currently heavily loaded but available")
        
        # Availability reasoning
        if availability_score >= 90:
            reasons.append("is actively available")
        elif availability_score >= 70:
            reasons.append("is recently active")
        else:
            reasons.append("was last seen recently")
        
        return " and ".join(reasons)
    
    def update_assignment_history(self, agent_id: str, task_id: str):
        """Update assignment history when task is assigned."""
        if agent_id not in self.assignment_history:
            self.assignment_history[agent_id] = []
        self.assignment_history[agent_id].append(task_id)
    
    def update_performance_metrics(
        self,
        agent_id: str,
        completion_rate: float,
        quality_score: float,
        time_accuracy: float
    ):
        """Update performance metrics for an agent."""
        if agent_id not in self.performance_metrics:
            self.performance_metrics[agent_id] = {}
        
        metrics = self.performance_metrics[agent_id]
        metrics["completion_rate"] = completion_rate
        metrics["quality_score"] = quality_score
        metrics["time_accuracy"] = time_accuracy
        metrics["last_updated"] = time.time()
    
    def track_collaboration(self, agent1_id: str, agent2_id: str):
        """Track collaboration patterns between agents."""
        if agent1_id not in self.collaboration_patterns:
            self.collaboration_patterns[agent1_id] = set()
        if agent2_id not in self.collaboration_patterns:
            self.collaboration_patterns[agent2_id] = set()
        
        self.collaboration_patterns[agent1_id].add(agent2_id)
        self.collaboration_patterns[agent2_id].add(agent1_id)
    
    def get_assignment_recommendations(
        self,
        tasks: List[Task],
        available_agents: Dict[str, AgentCapability],
        current_tasks: Dict[str, Task]
    ) -> List[Tuple[Task, AssignmentScore]]:
        """Get assignment recommendations for multiple tasks."""
        
        recommendations = []
        
        # Sort tasks by priority and dependencies
        sorted_tasks = self._sort_tasks_for_assignment(tasks)
        
        for task in sorted_tasks:
            best_assignment = self.find_best_assignment(
                task, available_agents, current_tasks
            )
            if best_assignment:
                recommendations.append((task, best_assignment))
        
        return recommendations
    
    def _sort_tasks_for_assignment(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks for optimal assignment order."""
        # Priority order: CRITICAL > HIGH > MEDIUM > LOW
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3
        }
        
        # Sort by priority first, then by dependency order
        return sorted(tasks, key=lambda t: (
            priority_order.get(t.priority, 4),
            len(t.dependencies),  # Tasks with fewer dependencies first
            t.created_at or 0     # Earlier tasks first
        ))


# Utility functions for task assignment analysis
def analyze_team_capacity(
    agents: Dict[str, AgentCapability],
    current_tasks: Dict[str, Task]
) -> Dict[str, Any]:
    """Analyze overall team capacity and utilization."""
    
    total_agents = len(agents)
    total_capacity = sum(agent.max_workload for agent in agents.values())
    
    # Calculate current utilization
    active_tasks_count = len([
        task for task in current_tasks.values()
        if task.status in [TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]
    ])
    
    utilization_rate = (active_tasks_count / total_capacity * 100) if total_capacity > 0 else 0
    
    # Agent-specific analysis
    agent_analysis = {}
    for agent_id, agent in agents.items():
        agent_tasks = [
            task for task in current_tasks.values()
            if task.assigned_to == agent_id and task.status in [TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]
        ]
        
        agent_analysis[agent_id] = {
            "name": agent.name,
            "role": agent.role,
            "current_tasks": len(agent_tasks),
            "capacity": agent.max_workload,
            "utilization": (len(agent_tasks) / agent.max_workload * 100) if agent.max_workload > 0 else 0,
            "available": agent.availability
        }
    
    return {
        "team_size": total_agents,
        "total_capacity": total_capacity,
        "active_tasks": active_tasks_count,
        "utilization_rate": utilization_rate,
        "agents": agent_analysis
    }