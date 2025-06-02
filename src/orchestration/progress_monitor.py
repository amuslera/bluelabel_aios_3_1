#!/usr/bin/env python3
"""
Progress Monitor and Blocker Resolution System

This module provides comprehensive monitoring of task progress and intelligent
resolution of blockers that prevent sprint goals from being achieved.
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass

from orchestration.task_orchestrator import Task, Blocker, TaskStatus, TaskPriority, BlockerType

logger = logging.getLogger(__name__)


class ProgressAlert(Enum):
    """Types of progress alerts."""
    SLOW_PROGRESS = "slow_progress"
    MISSED_DEADLINE = "missed_deadline"
    BLOCKER_DETECTED = "blocker_detected"
    QUALITY_CONCERN = "quality_concern"
    RESOURCE_BOTTLENECK = "resource_bottleneck"
    DEPENDENCY_VIOLATION = "dependency_violation"


class ResolutionStrategy(Enum):
    """Strategies for resolving blockers."""
    PROVIDE_GUIDANCE = "provide_guidance"
    REASSIGN_TASK = "reassign_task"
    BREAK_DOWN_TASK = "break_down_task"
    ADD_RESOURCES = "add_resources"
    ESCALATE_TO_HUMAN = "escalate_to_human"
    MODIFY_REQUIREMENTS = "modify_requirements"


@dataclass
class ProgressMetrics:
    """Metrics for tracking task/sprint progress."""
    task_id: str
    progress_percentage: float
    time_elapsed: float
    estimated_remaining: float
    velocity: float  # progress per hour
    on_track: bool
    risk_level: str  # low, medium, high, critical
    blockers_count: int
    last_update: float


@dataclass
class Alert:
    """Progress alert or warning."""
    id: str
    alert_type: ProgressAlert
    severity: str  # info, warning, error, critical
    title: str
    description: str
    affected_tasks: List[str]
    suggested_actions: List[str]
    created_at: float
    escalated: bool = False
    resolved: bool = False


@dataclass
class BlockerResolution:
    """Resolution approach for a blocker."""
    blocker_id: str
    strategy: ResolutionStrategy
    description: str
    estimated_time: float
    confidence: float  # 0.0 to 1.0
    requires_human: bool
    implementation_steps: List[str]


class ProgressMonitor:
    """
    Intelligent progress monitoring and blocker resolution system.
    
    Continuously monitors task progress, detects issues early, and
    automatically resolves blockers or escalates to humans when needed.
    """
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.progress_metrics: Dict[str, ProgressMetrics] = {}
        self.alerts: Dict[str, Alert] = {}
        self.active_resolutions: Dict[str, BlockerResolution] = {}
        
        # Monitoring configuration
        self.monitoring_interval = 30  # seconds
        self.progress_check_interval = 300  # 5 minutes
        self.blocker_detection_threshold = 0.1  # 10% velocity drop
        self.slow_progress_threshold = 2.0  # hours without meaningful progress
        
        # Resolution capabilities
        self.guidance_templates = self._load_guidance_templates()
        self.resolution_history: Dict[str, List[str]] = {}
        
        self.monitoring_active = False
    
    async def start_monitoring(self):
        """Start the progress monitoring system."""
        self.monitoring_active = True
        logger.info("🔍 Progress monitoring started")
        
        # Start monitoring loops
        asyncio.create_task(self._progress_monitoring_loop())
        asyncio.create_task(self._blocker_detection_loop())
        asyncio.create_task(self._alert_processing_loop())
    
    async def stop_monitoring(self):
        """Stop the progress monitoring system."""
        self.monitoring_active = False
        logger.info("🔍 Progress monitoring stopped")
    
    async def _progress_monitoring_loop(self):
        """Main progress monitoring loop."""
        while self.monitoring_active:
            try:
                await self._update_progress_metrics()
                await self._check_deadlines()
                await self._detect_velocity_changes()
                await asyncio.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in progress monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _blocker_detection_loop(self):
        """Detect and analyze blockers."""
        while self.monitoring_active:
            try:
                await self._detect_new_blockers()
                await self._analyze_existing_blockers()
                await self._attempt_automatic_resolution()
                await asyncio.sleep(self.progress_check_interval)
            except Exception as e:
                logger.error(f"Error in blocker detection: {e}")
                await asyncio.sleep(120)
    
    async def _alert_processing_loop(self):
        """Process and act on alerts."""
        while self.monitoring_active:
            try:
                await self._process_pending_alerts()
                await self._escalate_critical_alerts()
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Error in alert processing: {e}")
                await asyncio.sleep(120)
    
    async def _update_progress_metrics(self):
        """Update progress metrics for all active tasks."""
        current_time = time.time()
        
        for task_id, task in self.orchestrator.tasks.items():
            if task.status not in [TaskStatus.IN_PROGRESS, TaskStatus.ASSIGNED]:
                continue
            
            # Calculate progress metrics
            metrics = self._calculate_task_progress(task, current_time)
            self.progress_metrics[task_id] = metrics
            
            # Check for concerning trends
            if metrics.risk_level in ["high", "critical"]:
                await self._create_alert(
                    ProgressAlert.SLOW_PROGRESS,
                    f"Task '{task.title}' showing concerning progress",
                    [task_id],
                    "error" if metrics.risk_level == "critical" else "warning"
                )
    
    def _calculate_task_progress(self, task: Task, current_time: float) -> ProgressMetrics:
        """Calculate detailed progress metrics for a task."""
        
        # Time calculations
        start_time = task.started_at or task.assigned_at or task.created_at
        time_elapsed = current_time - start_time if start_time else 0
        
        # Progress estimation
        progress_percentage = task.progress
        if progress_percentage == 0 and time_elapsed > 1800:  # 30 minutes
            # Assume some progress if task has been active
            progress_percentage = min(10.0, time_elapsed / 3600 * 5)  # 5% per hour baseline
        
        # Velocity calculation
        velocity = progress_percentage / (time_elapsed / 3600) if time_elapsed > 0 else 0
        
        # Estimated remaining time
        remaining_percentage = 100 - progress_percentage
        estimated_remaining = (remaining_percentage / velocity) if velocity > 0 else float('inf')
        
        # Risk assessment
        expected_progress = (time_elapsed / (task.estimated_effort * 3600)) * 100
        progress_ratio = progress_percentage / expected_progress if expected_progress > 0 else 1.0
        
        if progress_ratio >= 0.8:
            risk_level = "low"
        elif progress_ratio >= 0.6:
            risk_level = "medium"
        elif progress_ratio >= 0.3:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        # On track assessment
        on_track = (
            risk_level in ["low", "medium"] and
            velocity > 0 and
            estimated_remaining < task.estimated_effort * 1.5
        )
        
        # Count blockers
        blockers_count = len(task.blockers)
        
        return ProgressMetrics(
            task_id=task.id,
            progress_percentage=progress_percentage,
            time_elapsed=time_elapsed,
            estimated_remaining=estimated_remaining,
            velocity=velocity,
            on_track=on_track,
            risk_level=risk_level,
            blockers_count=blockers_count,
            last_update=current_time
        )
    
    async def _check_deadlines(self):
        """Check for missed or at-risk deadlines."""
        current_time = time.time()
        
        for task_id, task in self.orchestrator.tasks.items():
            if task.status not in [TaskStatus.IN_PROGRESS, TaskStatus.ASSIGNED]:
                continue
            
            # Check if task has an explicit deadline
            deadline = getattr(task, 'deadline', None)
            if not deadline:
                # Estimate deadline based on estimated effort
                start_time = task.assigned_at or task.created_at
                deadline = start_time + (task.estimated_effort * 3600 * 1.5)  # 50% buffer
            
            time_to_deadline = deadline - current_time
            
            if time_to_deadline < 0:
                # Missed deadline
                await self._create_alert(
                    ProgressAlert.MISSED_DEADLINE,
                    f"Task '{task.title}' has missed its deadline",
                    [task_id],
                    "critical"
                )
            elif time_to_deadline < 3600:  # 1 hour warning
                # At risk of missing deadline
                await self._create_alert(
                    ProgressAlert.SLOW_PROGRESS,
                    f"Task '{task.title}' at risk of missing deadline",
                    [task_id],
                    "warning"
                )
    
    async def _detect_velocity_changes(self):
        """Detect significant changes in task velocity."""
        for task_id, metrics in self.progress_metrics.items():
            # Get historical velocity if available
            historical_velocity = self._get_historical_velocity(task_id)
            
            if historical_velocity and metrics.velocity > 0:
                velocity_change = (metrics.velocity - historical_velocity) / historical_velocity
                
                if velocity_change < -self.blocker_detection_threshold:
                    # Significant velocity drop
                    await self._investigate_velocity_drop(task_id, velocity_change)
    
    def _get_historical_velocity(self, task_id: str) -> Optional[float]:
        """Get historical velocity for comparison."""
        # This would ideally look at historical data
        # For now, return None to indicate no historical data
        return None
    
    async def _investigate_velocity_drop(self, task_id: str, velocity_change: float):
        """Investigate significant velocity drops."""
        task = self.orchestrator.tasks.get(task_id)
        if not task:
            return
        
        # Create investigation alert
        await self._create_alert(
            ProgressAlert.SLOW_PROGRESS,
            f"Velocity drop detected for '{task.title}' ({velocity_change:.1%})",
            [task_id],
            "warning"
        )
        
        # Offer proactive assistance
        if task.assigned_to:
            await self.orchestrator.send_message({
                "type": "chat",
                "from_id": self.orchestrator.orchestrator_id,
                "content": f"""🔍 **Proactive Check-in**

I noticed the velocity on "{task.title}" has decreased. This often indicates:

**Possible Causes:**
• Technical complexity higher than expected
• Missing information or requirements
• Dependencies or blockers
• Need for different approach

**How I can help:**
• Provide technical guidance or resources
• Break the task into smaller pieces
• Assign additional team members
• Clarify requirements or acceptance criteria

What's the current challenge? Let's resolve this together! 🚀""",
                "metadata": {"velocity_check": True, "task_id": task_id}
            })
    
    async def _detect_new_blockers(self):
        """Detect new blockers across the sprint."""
        
        # Pattern-based blocker detection
        for task_id, task in self.orchestrator.tasks.items():
            if task.status == TaskStatus.IN_PROGRESS:
                
                # Check for common blocker patterns
                await self._check_dependency_blockers(task)
                await self._check_resource_blockers(task)
                await self._check_technical_blockers(task)
    
    async def _check_dependency_blockers(self, task: Task):
        """Check for dependency-related blockers."""
        for dep_id in task.dependencies:
            dep_task = self.orchestrator.tasks.get(dep_id)
            if dep_task and dep_task.status not in [TaskStatus.COMPLETED]:
                # Dependency not satisfied
                await self._create_blocker(
                    task.id,
                    BlockerType.DEPENDENCY,
                    f"Waiting for dependency: {dep_task.title}",
                    f"Task depends on '{dep_task.title}' which is not yet completed"
                )
    
    async def _check_resource_blockers(self, task: Task):
        """Check for resource-related blockers."""
        # Check if assigned agent is available
        if task.assigned_to:
            agent = self.orchestrator.agents.get(task.assigned_to)
            if agent and not agent.availability:
                await self._create_blocker(
                    task.id,
                    BlockerType.RESOURCE,
                    f"Assigned agent unavailable",
                    f"Agent {agent.name} is currently unavailable"
                )
    
    async def _check_technical_blockers(self, task: Task):
        """Check for technical blockers."""
        metrics = self.progress_metrics.get(task.id)
        if metrics and metrics.velocity == 0 and metrics.time_elapsed > self.slow_progress_threshold * 3600:
            # No progress for extended period
            await self._create_blocker(
                task.id,
                BlockerType.TECHNICAL,
                "No progress detected",
                f"Task has shown no progress for {self.slow_progress_threshold} hours"
            )
    
    async def _create_blocker(self, task_id: str, blocker_type: BlockerType, title: str, description: str):
        """Create a new blocker."""
        blocker_id = f"blocker_{uuid.uuid4().hex[:8]}"
        
        # Check if similar blocker already exists
        existing_blockers = [
            b for b in self.orchestrator.blockers.values()
            if b.task_id == task_id and b.blocker_type == blocker_type
        ]
        
        if existing_blockers:
            return  # Don't create duplicate blockers
        
        blocker = Blocker(
            id=blocker_id,
            task_id=task_id,
            blocker_type=blocker_type,
            title=title,
            description=description,
            impact=self._assess_blocker_impact(task_id, blocker_type)
        )
        
        self.orchestrator.blockers[blocker_id] = blocker
        
        # Add to task's blocker list
        task = self.orchestrator.tasks.get(task_id)
        if task:
            task.blockers.append(blocker_id)
            task.status = TaskStatus.BLOCKED
        
        # Create alert
        await self._create_alert(
            ProgressAlert.BLOCKER_DETECTED,
            f"Blocker detected: {title}",
            [task_id],
            "error"
        )
        
        # Attempt immediate resolution
        await self._attempt_blocker_resolution(blocker)
    
    def _assess_blocker_impact(self, task_id: str, blocker_type: BlockerType) -> str:
        """Assess the impact of a blocker."""
        task = self.orchestrator.tasks.get(task_id)
        if not task:
            return "Unknown impact"
        
        if task.priority == TaskPriority.CRITICAL:
            return "Critical - blocks sprint goal"
        elif task.priority == TaskPriority.HIGH:
            return "High - significant sprint impact"
        elif blocker_type == BlockerType.DEPENDENCY:
            return "Medium - may delay dependent tasks"
        else:
            return "Low - isolated task impact"
    
    async def _attempt_blocker_resolution(self, blocker: Blocker):
        """Attempt to automatically resolve a blocker."""
        
        # Determine resolution strategy
        strategy = self._determine_resolution_strategy(blocker)
        
        resolution = BlockerResolution(
            blocker_id=blocker.id,
            strategy=strategy,
            description=f"Automatic resolution attempt for {blocker.title}",
            estimated_time=self._estimate_resolution_time(strategy),
            confidence=self._estimate_resolution_confidence(blocker, strategy),
            requires_human=strategy == ResolutionStrategy.ESCALATE_TO_HUMAN,
            implementation_steps=self._get_resolution_steps(strategy, blocker)
        )
        
        self.active_resolutions[blocker.id] = resolution
        
        # Execute resolution
        await self._execute_resolution(resolution, blocker)
    
    def _determine_resolution_strategy(self, blocker: Blocker) -> ResolutionStrategy:
        """Determine the best strategy for resolving a blocker."""
        
        if blocker.blocker_type == BlockerType.DEPENDENCY:
            # Check if we can accelerate the dependency
            return ResolutionStrategy.ADD_RESOURCES
        
        elif blocker.blocker_type == BlockerType.TECHNICAL:
            # Provide technical guidance first
            return ResolutionStrategy.PROVIDE_GUIDANCE
        
        elif blocker.blocker_type == BlockerType.RESOURCE:
            # Try reassigning or adding resources
            return ResolutionStrategy.REASSIGN_TASK
        
        elif blocker.blocker_type == BlockerType.DECISION_NEEDED:
            # Escalate to human for decisions
            return ResolutionStrategy.ESCALATE_TO_HUMAN
        
        else:
            # Default to providing guidance
            return ResolutionStrategy.PROVIDE_GUIDANCE
    
    def _estimate_resolution_time(self, strategy: ResolutionStrategy) -> float:
        """Estimate time to resolve using this strategy."""
        time_estimates = {
            ResolutionStrategy.PROVIDE_GUIDANCE: 0.5,  # 30 minutes
            ResolutionStrategy.REASSIGN_TASK: 1.0,     # 1 hour
            ResolutionStrategy.BREAK_DOWN_TASK: 2.0,   # 2 hours
            ResolutionStrategy.ADD_RESOURCES: 4.0,     # 4 hours
            ResolutionStrategy.ESCALATE_TO_HUMAN: 24.0, # 1 day
            ResolutionStrategy.MODIFY_REQUIREMENTS: 8.0 # 8 hours
        }
        return time_estimates.get(strategy, 2.0)
    
    def _estimate_resolution_confidence(self, blocker: Blocker, strategy: ResolutionStrategy) -> float:
        """Estimate confidence in resolution strategy."""
        
        # Base confidence by strategy type
        base_confidence = {
            ResolutionStrategy.PROVIDE_GUIDANCE: 0.7,
            ResolutionStrategy.REASSIGN_TASK: 0.8,
            ResolutionStrategy.BREAK_DOWN_TASK: 0.6,
            ResolutionStrategy.ADD_RESOURCES: 0.9,
            ResolutionStrategy.ESCALATE_TO_HUMAN: 0.95,
            ResolutionStrategy.MODIFY_REQUIREMENTS: 0.5
        }.get(strategy, 0.5)
        
        # Adjust based on blocker type
        if blocker.blocker_type == BlockerType.DEPENDENCY and strategy == ResolutionStrategy.ADD_RESOURCES:
            base_confidence += 0.1
        elif blocker.blocker_type == BlockerType.TECHNICAL and strategy == ResolutionStrategy.PROVIDE_GUIDANCE:
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def _get_resolution_steps(self, strategy: ResolutionStrategy, blocker: Blocker) -> List[str]:
        """Get implementation steps for resolution strategy."""
        
        if strategy == ResolutionStrategy.PROVIDE_GUIDANCE:
            return [
                "Analyze the specific technical challenge",
                "Provide targeted guidance and resources",
                "Offer alternative approaches",
                "Monitor progress after guidance"
            ]
        
        elif strategy == ResolutionStrategy.REASSIGN_TASK:
            return [
                "Identify available agents with required expertise",
                "Assess current workloads",
                "Reassign to best available agent",
                "Transfer context and requirements"
            ]
        
        elif strategy == ResolutionStrategy.ADD_RESOURCES:
            return [
                "Identify task that needs acceleration",
                "Find available team members",
                "Assign additional resources",
                "Coordinate parallel work"
            ]
        
        elif strategy == ResolutionStrategy.BREAK_DOWN_TASK:
            return [
                "Analyze task complexity",
                "Break into smaller, manageable pieces",
                "Redistribute subtasks to team",
                "Update dependencies and priorities"
            ]
        
        else:
            return ["Execute resolution strategy", "Monitor results"]
    
    async def _execute_resolution(self, resolution: BlockerResolution, blocker: Blocker):
        """Execute the resolution strategy."""
        
        if resolution.strategy == ResolutionStrategy.PROVIDE_GUIDANCE:
            await self._provide_technical_guidance(blocker)
        
        elif resolution.strategy == ResolutionStrategy.REASSIGN_TASK:
            await self._attempt_task_reassignment(blocker)
        
        elif resolution.strategy == ResolutionStrategy.ESCALATE_TO_HUMAN:
            await self._escalate_blocker_to_human(blocker)
        
        # Log resolution attempt
        logger.info(f"Attempting resolution for blocker {blocker.id} using {resolution.strategy.value}")
    
    async def _provide_technical_guidance(self, blocker: Blocker):
        """Provide technical guidance to resolve blocker."""
        task = self.orchestrator.tasks.get(blocker.task_id)
        if not task or not task.assigned_to:
            return
        
        # Generate contextual guidance based on blocker and task
        guidance = self._generate_technical_guidance(task, blocker)
        
        await self.orchestrator.send_message({
            "type": "chat",
            "from_id": self.orchestrator.orchestrator_id,
            "content": f"""🔧 **Technical Guidance - Blocker Resolution**

I've detected a blocker with "{task.title}" and I'm here to help resolve it.

**Issue:** {blocker.description}

**Suggested Approach:**
{guidance}

**Additional Support:**
• I can break this task into smaller pieces if helpful
• I can assign additional team members if needed
• I can provide more specific guidance on any aspect

What specific part would you like me to help with first? 🚀""",
            "metadata": {"blocker_guidance": True, "blocker_id": blocker.id}
        })
    
    def _generate_technical_guidance(self, task: Task, blocker: Blocker) -> str:
        """Generate contextual technical guidance."""
        
        # Use templates based on task type and blocker type
        guidance_key = f"{task.task_type.value}_{blocker.blocker_type.value}"
        template = self.guidance_templates.get(guidance_key, self.guidance_templates.get("default"))
        
        return template.format(
            task_title=task.title,
            task_type=task.task_type.value.replace('_', ' '),
            blocker_description=blocker.description
        )
    
    async def _attempt_task_reassignment(self, blocker: Blocker):
        """Attempt to reassign task to resolve blocker."""
        task = self.orchestrator.tasks.get(blocker.task_id)
        if not task:
            return
        
        # Find alternative agents
        from orchestration.assignment_engine import AssignmentEngine
        assignment_engine = AssignmentEngine()
        
        # Remove current assignment
        if task.assigned_to:
            current_agent = self.orchestrator.agents.get(task.assigned_to)
            if current_agent:
                current_agent.current_workload -= 1
                self.orchestrator.agent_assignments[task.assigned_to].discard(task.id)
        
        # Find new assignment
        best_assignment = assignment_engine.find_best_assignment(
            task, self.orchestrator.agents, self.orchestrator.tasks
        )
        
        if best_assignment:
            await self.orchestrator.assign_task_to_agent(task.id, best_assignment.agent_id)
            
            # Update blocker status
            blocker.resolution_strategy = f"Reassigned to {best_assignment.agent_id}"
            
            await self.orchestrator.send_message({
                "type": "chat",
                "from_id": self.orchestrator.orchestrator_id,
                "content": f"""🔄 **Task Reassigned - Blocker Resolution**

I've reassigned "{task.title}" to help resolve the blocker.

**Previous Assignment:** Had challenges with {blocker.description}
**New Assignment:** Better match for this task type and current availability
**Expected Outcome:** Faster resolution with fresh perspective

Monitoring progress and ready to provide additional support! 📊""",
                "metadata": {"task_reassignment": True, "blocker_id": blocker.id}
            })
    
    async def _escalate_blocker_to_human(self, blocker: Blocker):
        """Escalate blocker to human Product Owner."""
        blocker.escalated_to_human = True
        
        task = self.orchestrator.tasks.get(blocker.task_id)
        
        await self.orchestrator.send_message({
            "type": "chat",
            "from_id": self.orchestrator.orchestrator_id,
            "content": f"""🚨 **Escalation Required - Blocker Resolution**

I need your decision on a blocker that's impacting our sprint:

**Task:** {task.title if task else 'Unknown'}
**Blocker:** {blocker.title}
**Issue:** {blocker.description}
**Impact:** {blocker.impact}

**Why I'm escalating:**
This requires a business/product decision that's outside my technical scope.

**Options I see:**
1. Modify requirements to work around the blocker
2. Accept delay and find alternative approach
3. Deprioritize this task for now
4. Assign additional resources

How would you like to proceed? Your guidance will help me resolve this and keep the sprint on track! 🎯""",
            "metadata": {"escalation": True, "blocker_id": blocker.id}
        })
    
    async def _create_alert(
        self,
        alert_type: ProgressAlert,
        description: str,
        affected_tasks: List[str],
        severity: str
    ):
        """Create a new progress alert."""
        alert_id = f"alert_{uuid.uuid4().hex[:8]}"
        
        # Generate suggested actions
        suggested_actions = self._get_suggested_actions(alert_type, affected_tasks)
        
        alert = Alert(
            id=alert_id,
            alert_type=alert_type,
            severity=severity,
            title=f"{alert_type.value.replace('_', ' ').title()} Alert",
            description=description,
            affected_tasks=affected_tasks,
            suggested_actions=suggested_actions,
            created_at=time.time()
        )
        
        self.alerts[alert_id] = alert
        
        # Log alert
        logger.warning(f"Alert created: {alert.title} - {description}")
    
    def _get_suggested_actions(self, alert_type: ProgressAlert, affected_tasks: List[str]) -> List[str]:
        """Get suggested actions for an alert type."""
        
        action_map = {
            ProgressAlert.SLOW_PROGRESS: [
                "Provide additional guidance to assigned agent",
                "Check for blockers or dependencies",
                "Consider breaking task into smaller pieces",
                "Assign additional resources if available"
            ],
            ProgressAlert.MISSED_DEADLINE: [
                "Reassess task priority and requirements",
                "Reallocate resources from lower priority tasks",
                "Negotiate deadline extension if possible",
                "Fast-track task with additional resources"
            ],
            ProgressAlert.BLOCKER_DETECTED: [
                "Analyze root cause of blocker",
                "Provide technical guidance or resources",
                "Consider alternative implementation approach",
                "Escalate to human if decision required"
            ],
            ProgressAlert.RESOURCE_BOTTLENECK: [
                "Redistribute workload across team",
                "Identify and resolve resource constraints",
                "Prioritize critical path tasks",
                "Consider adding temporary resources"
            ]
        }
        
        return action_map.get(alert_type, ["Investigate and resolve"])
    
    async def _process_pending_alerts(self):
        """Process pending alerts and take action."""
        unresolved_alerts = [a for a in self.alerts.values() if not a.resolved]
        
        for alert in unresolved_alerts:
            if alert.severity == "critical" and not alert.escalated:
                await self._escalate_critical_alerts()
    
    async def _escalate_critical_alerts(self):
        """Escalate critical alerts to human."""
        critical_alerts = [
            a for a in self.alerts.values()
            if a.severity == "critical" and not a.escalated
        ]
        
        for alert in critical_alerts:
            alert.escalated = True
            
            await self.orchestrator.send_message({
                "type": "chat",
                "from_id": self.orchestrator.orchestrator_id,
                "content": f"""🚨 **Critical Alert - Immediate Attention Required**

**Alert:** {alert.title}
**Issue:** {alert.description}
**Affected Tasks:** {len(alert.affected_tasks)}

**Suggested Actions:**
{chr(10).join(f'• {action}' for action in alert.suggested_actions)}

This is impacting our sprint goals and requires your immediate attention! 🎯""",
                "metadata": {"critical_alert": True, "alert_id": alert.id}
            })
    
    def _load_guidance_templates(self) -> Dict[str, str]:
        """Load technical guidance templates."""
        return {
            "implementation_technical": """
**For Implementation Tasks:**
1. Break the problem into smaller, testable pieces
2. Start with the simplest working version
3. Use established patterns and frameworks
4. Write tests as you go to validate progress

**Common Solutions:**
• Check documentation and examples for similar implementations
• Consider using existing libraries or frameworks
• Validate assumptions with small proof-of-concepts
• Ask for specific technical guidance on the challenging part
            """,
            
            "testing_technical": """
**For Testing Tasks:**
1. Start with happy path test cases
2. Identify edge cases and error conditions
3. Use appropriate testing frameworks and tools
4. Automate tests for repeatability

**Common Approaches:**
• Unit tests for individual components
• Integration tests for system interactions
• End-to-end tests for user workflows
• Performance tests for critical paths
            """,
            
            "default": """
**General Guidance:**
1. Break the task into smaller, manageable pieces
2. Identify the specific challenge or unknown
3. Research existing solutions and best practices
4. Start with a simple approach and iterate

**Getting Unstuck:**
• Define exactly what's blocking progress
• Try a different approach or perspective
• Ask for specific help on the challenging aspect
• Consider if requirements need clarification
            """
        }


async def create_progress_monitor(orchestrator) -> ProgressMonitor:
    """Create and initialize a progress monitor."""
    monitor = ProgressMonitor(orchestrator)
    await monitor.start_monitoring()
    return monitor