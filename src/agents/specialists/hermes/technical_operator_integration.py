#!/usr/bin/env python3
"""
Technical Operator Integration - Manages human-in-the-loop checkpoints.
Handles the communication between AI agents and the Technical Operator.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
import uuid

logger = logging.getLogger(__name__)


class CheckpointType(Enum):
    """Types of TO checkpoints."""
    PROJECT_APPROVAL = "project_approval"
    INFRASTRUCTURE_SETUP = "infrastructure_setup"
    API_CREDENTIALS = "api_credentials"
    INFRASTRUCTURE_CREATION = "infrastructure_creation"
    SECURITY_REVIEW = "security_review"
    STAGING_DEPLOYMENT = "staging_deployment"
    PRODUCTION_DEPLOYMENT = "production_deployment"
    DOMAIN_SETUP = "domain_setup"
    MONITORING_SETUP = "monitoring_setup"
    COST_APPROVAL = "cost_approval"


class CheckpointPriority(Enum):
    """Priority levels for checkpoints."""
    CRITICAL = "critical"  # Blocking production
    HIGH = "high"         # Blocking development
    MEDIUM = "medium"     # Can wait few hours
    LOW = "low"          # Optimization/improvement


class CheckpointStatus(Enum):
    """Status of a checkpoint."""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class TOCheckpoint:
    """A checkpoint requiring Technical Operator action."""
    id: str = field(default_factory=lambda: f"chk_{uuid.uuid4().hex[:8]}")
    type: CheckpointType = CheckpointType.PROJECT_APPROVAL
    project_id: str = ""
    project_name: str = ""
    agent_id: str = ""
    agent_name: str = ""
    priority: CheckpointPriority = CheckpointPriority.MEDIUM
    status: CheckpointStatus = CheckpointStatus.PENDING
    
    # Content
    title: str = ""
    description: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    options: List[Dict[str, str]] = field(default_factory=list)
    required_inputs: List[str] = field(default_factory=list)
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    
    # Response
    decision: Optional[str] = None
    response_data: Dict[str, Any] = field(default_factory=dict)
    to_operator_id: Optional[str] = None
    
    def to_message(self) -> str:
        """Format checkpoint as message for TO."""
        deadline_str = f"\nDeadline: {self.deadline.strftime('%Y-%m-%d %H:%M')}" if self.deadline else ""
        options_str = ""
        if self.options:
            options_str = "\n\nOptions:\n" + "\n".join(
                f"{i+1}. {opt.get('label', 'Option ' + str(i+1))}: {opt.get('description', '')}"
                for i, opt in enumerate(self.options)
            )
        
        inputs_str = ""
        if self.required_inputs:
            inputs_str = "\n\nRequired inputs:\n" + "\n".join(
                f"- {input_name}" for input_name in self.required_inputs
            )
        
        return f"""[CHECKPOINT {self.id}] Action Required: {self.title}
Project: {self.project_name}
Agent: {self.agent_name}
Priority: {self.priority.value.upper()}{deadline_str}

Details:
{self.description}
{options_str}
{inputs_str}

Respond with: to_respond <checkpoint_id> <decision> <data>"""


class TechnicalOperatorInterface:
    """Interface for Technical Operator interactions."""
    
    def __init__(self):
        """Initialize the TO interface."""
        self.checkpoints: Dict[str, TOCheckpoint] = {}
        self.active_projects: Dict[str, Dict[str, Any]] = {}
        self.response_callbacks: Dict[str, Callable] = {}
        self.checkpoint_history: List[TOCheckpoint] = []
        
        # SLA configuration (in minutes)
        self.sla_times = {
            CheckpointPriority.CRITICAL: 15,
            CheckpointPriority.HIGH: 120,
            CheckpointPriority.MEDIUM: 240,
            CheckpointPriority.LOW: 1440
        }
    
    async def create_checkpoint(
        self,
        type: CheckpointType,
        project_id: str,
        project_name: str,
        agent_id: str,
        agent_name: str,
        title: str,
        description: str,
        priority: CheckpointPriority = CheckpointPriority.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        options: Optional[List[Dict[str, str]]] = None,
        required_inputs: Optional[List[str]] = None,
        callback: Optional[Callable] = None
    ) -> TOCheckpoint:
        """Create a new checkpoint for TO review."""
        
        checkpoint = TOCheckpoint(
            type=type,
            project_id=project_id,
            project_name=project_name,
            agent_id=agent_id,
            agent_name=agent_name,
            priority=priority,
            title=title,
            description=description,
            details=details or {},
            options=options or [],
            required_inputs=required_inputs or [],
            deadline=datetime.now() + timedelta(minutes=self.sla_times[priority])
        )
        
        self.checkpoints[checkpoint.id] = checkpoint
        
        if callback:
            self.response_callbacks[checkpoint.id] = callback
        
        # Send notification to TO
        await self._notify_to(checkpoint)
        
        logger.info(f"Created checkpoint {checkpoint.id}: {title}")
        return checkpoint
    
    async def _notify_to(self, checkpoint: TOCheckpoint):
        """Notify TO about new checkpoint."""
        # In real implementation, this would:
        # - Send Slack/Discord message
        # - Create dashboard notification
        # - Send email for critical items
        # - Update monitoring systems
        
        message = checkpoint.to_message()
        logger.info(f"TO Notification:\n{message}")
        
        # Simulate TO dashboard update
        if checkpoint.project_id not in self.active_projects:
            self.active_projects[checkpoint.project_id] = {
                "name": checkpoint.project_name,
                "checkpoints": []
            }
        self.active_projects[checkpoint.project_id]["checkpoints"].append(checkpoint.id)
    
    async def respond_to_checkpoint(
        self,
        checkpoint_id: str,
        decision: str,
        response_data: Optional[Dict[str, Any]] = None,
        operator_id: str = "to_default"
    ) -> bool:
        """TO responds to a checkpoint."""
        
        if checkpoint_id not in self.checkpoints:
            logger.error(f"Checkpoint {checkpoint_id} not found")
            return False
        
        checkpoint = self.checkpoints[checkpoint_id]
        
        if checkpoint.status != CheckpointStatus.PENDING:
            logger.warning(f"Checkpoint {checkpoint_id} already processed: {checkpoint.status}")
            return False
        
        # Update checkpoint
        checkpoint.status = CheckpointStatus.APPROVED if decision.lower() in ["yes", "y", "approved", "approve"] else CheckpointStatus.REJECTED
        checkpoint.decision = decision
        checkpoint.response_data = response_data or {}
        checkpoint.to_operator_id = operator_id
        checkpoint.responded_at = datetime.now()
        
        # Move to history
        self.checkpoint_history.append(checkpoint)
        
        # Execute callback if registered
        if checkpoint_id in self.response_callbacks:
            callback = self.response_callbacks[checkpoint_id]
            try:
                await callback(checkpoint)
            except Exception as e:
                logger.error(f"Callback failed for checkpoint {checkpoint_id}: {e}")
        
        logger.info(f"TO responded to checkpoint {checkpoint_id}: {decision}")
        return True
    
    def get_pending_checkpoints(self, project_id: Optional[str] = None) -> List[TOCheckpoint]:
        """Get all pending checkpoints, optionally filtered by project."""
        pending = [
            cp for cp in self.checkpoints.values()
            if cp.status == CheckpointStatus.PENDING
        ]
        
        if project_id:
            pending = [cp for cp in pending if cp.project_id == project_id]
        
        # Sort by priority and deadline
        priority_order = {
            CheckpointPriority.CRITICAL: 0,
            CheckpointPriority.HIGH: 1,
            CheckpointPriority.MEDIUM: 2,
            CheckpointPriority.LOW: 3
        }
        
        return sorted(pending, key=lambda x: (priority_order[x.priority], x.deadline))
    
    async def check_sla_violations(self):
        """Check for checkpoints exceeding SLA."""
        now = datetime.now()
        violations = []
        
        for checkpoint in self.get_pending_checkpoints():
            if checkpoint.deadline and now > checkpoint.deadline:
                violations.append(checkpoint)
                logger.warning(f"SLA violation: Checkpoint {checkpoint.id} exceeded deadline")
        
        return violations
    
    def get_checkpoint_summary(self) -> Dict[str, Any]:
        """Get summary of checkpoint status."""
        pending = self.get_pending_checkpoints()
        
        by_priority = {}
        for priority in CheckpointPriority:
            by_priority[priority.value] = len([
                cp for cp in pending if cp.priority == priority
            ])
        
        by_type = {}
        for cp_type in CheckpointType:
            by_type[cp_type.value] = len([
                cp for cp in pending if cp.type == cp_type
            ])
        
        return {
            "total_pending": len(pending),
            "by_priority": by_priority,
            "by_type": by_type,
            "oldest_pending": min(pending, key=lambda x: x.created_at).created_at if pending else None,
            "sla_violations": len([cp for cp in pending if cp.deadline and datetime.now() > cp.deadline])
        }


class CheckpointFactory:
    """Factory for creating common checkpoints."""
    
    @staticmethod
    def create_project_approval(
        project_id: str,
        project_name: str,
        project_type: str,
        estimated_cost: float,
        required_services: List[str],
        timeline_days: int
    ) -> Dict[str, Any]:
        """Create project approval checkpoint."""
        return {
            "type": CheckpointType.PROJECT_APPROVAL,
            "title": f"New Project Approval: {project_name}",
            "description": f"""New {project_type} project requires approval.

Project: {project_name}
Type: {project_type}
Timeline: {timeline_days} days
Estimated monthly cost: ${estimated_cost:.2f}

Required services:
{chr(10).join('- ' + service for service in required_services)}

This project will be built by our AI agent team. Please review the scope and approve to proceed.""",
            "options": [
                {"label": "Approve", "description": "Proceed with project setup"},
                {"label": "Reject", "description": "Cancel project"},
                {"label": "Modify", "description": "Request scope changes"}
            ],
            "priority": CheckpointPriority.HIGH,
            "details": {
                "project_type": project_type,
                "estimated_cost": estimated_cost,
                "timeline_days": timeline_days,
                "required_services": required_services
            }
        }
    
    @staticmethod
    def create_api_credential_request(
        service_name: str,
        credential_type: str,
        instructions: List[str],
        required_permissions: List[str]
    ) -> Dict[str, Any]:
        """Create API credential request checkpoint."""
        return {
            "type": CheckpointType.API_CREDENTIALS,
            "title": f"{service_name} API Credentials Needed",
            "description": f"""Please provide {credential_type} for {service_name}.

Instructions:
{chr(10).join(f'{i+1}. {inst}' for i, inst in enumerate(instructions))}

Required permissions:
{chr(10).join('- ' + perm for perm in required_permissions)}""",
            "required_inputs": [
                f"{service_name.lower()}_api_key",
                f"{service_name.lower()}_api_secret"
            ],
            "priority": CheckpointPriority.HIGH,
            "details": {
                "service": service_name,
                "credential_type": credential_type,
                "permissions": required_permissions
            }
        }
    
    @staticmethod
    def create_infrastructure_approval(
        resources: List[Dict[str, str]],
        total_cost: float,
        terraform_plan: str
    ) -> Dict[str, Any]:
        """Create infrastructure approval checkpoint."""
        return {
            "type": CheckpointType.INFRASTRUCTURE_CREATION,
            "title": "Infrastructure Approval Required",
            "description": f"""Terraform plan ready for execution.

Resources to create:
{chr(10).join(f"+ {r['type']}.{r['name']}" for r in resources)}

Estimated monthly cost: ${total_cost:.2f}

Review the full plan and approve to create infrastructure.""",
            "options": [
                {"label": "Apply", "description": "Create infrastructure"},
                {"label": "Reject", "description": "Cancel infrastructure creation"},
                {"label": "Modify", "description": "Request changes to plan"}
            ],
            "priority": CheckpointPriority.HIGH,
            "details": {
                "resources": resources,
                "total_cost": total_cost,
                "terraform_plan": terraform_plan
            }
        }
    
    @staticmethod
    def create_deployment_approval(
        environment: str,
        version: str,
        changes: List[str],
        rollback_plan: str
    ) -> Dict[str, Any]:
        """Create deployment approval checkpoint."""
        priority = CheckpointPriority.CRITICAL if environment == "production" else CheckpointPriority.HIGH
        
        return {
            "type": CheckpointType.PRODUCTION_DEPLOYMENT if environment == "production" else CheckpointType.STAGING_DEPLOYMENT,
            "title": f"{environment.title()} Deployment Approval",
            "description": f"""Ready to deploy version {version} to {environment}.

Changes in this release:
{chr(10).join('- ' + change for change in changes)}

Rollback plan: {rollback_plan}

All tests passing. Approve deployment?""",
            "options": [
                {"label": "Deploy", "description": f"Deploy to {environment}"},
                {"label": "Cancel", "description": "Cancel deployment"},
                {"label": "Schedule", "description": "Schedule for later"}
            ],
            "priority": priority,
            "details": {
                "environment": environment,
                "version": version,
                "changes": changes,
                "rollback_plan": rollback_plan
            }
        }


# Example integration with existing handoff system
class TOAwareHandoffConnector:
    """Enhanced handoff connector with TO checkpoints."""
    
    def __init__(self, to_interface: TechnicalOperatorInterface):
        self.to_interface = to_interface
        self.pending_handoffs: Dict[str, Dict[str, Any]] = {}
    
    async def handoff_with_approval(self, brief, session_id: str) -> Dict[str, Any]:
        """Execute handoff with TO approval checkpoint."""
        
        # Create project approval checkpoint
        checkpoint_data = CheckpointFactory.create_project_approval(
            project_id=brief.id,
            project_name=brief.name,
            project_type=brief.project_type.value,
            estimated_cost=self._estimate_monthly_cost(brief),
            required_services=self._identify_required_services(brief),
            timeline_days=brief.timeline.estimated_duration_days
        )
        
        # Create checkpoint with callback
        checkpoint = await self.to_interface.create_checkpoint(
            project_id=brief.id,
            project_name=brief.name,
            agent_id="orchestrator",
            agent_name="Task Orchestrator",
            callback=lambda cp: self._handle_project_approval(cp, brief, session_id),
            **checkpoint_data
        )
        
        # Store pending handoff
        self.pending_handoffs[checkpoint.id] = {
            "brief": brief,
            "session_id": session_id,
            "checkpoint_id": checkpoint.id
        }
        
        return {
            "status": "pending_approval",
            "checkpoint_id": checkpoint.id,
            "message": "Project is pending Technical Operator approval"
        }
    
    async def _handle_project_approval(self, checkpoint: TOCheckpoint, brief, session_id: str):
        """Handle TO response to project approval."""
        if checkpoint.status == CheckpointStatus.APPROVED:
            # Continue with handoff
            logger.info(f"Project {brief.name} approved by TO")
            # ... continue normal handoff process
        else:
            # Project rejected
            logger.info(f"Project {brief.name} rejected by TO: {checkpoint.decision}")
            # ... notify client of rejection
    
    def _estimate_monthly_cost(self, brief) -> float:
        """Estimate infrastructure cost based on project type."""
        # Simplified cost estimation
        base_costs = {
            "web_app": 50,
            "api_service": 40,
            "automation_workflow": 30,
            "data_pipeline": 80,
            "mobile_app": 60
        }
        return base_costs.get(brief.project_type.value, 50)
    
    def _identify_required_services(self, brief) -> List[str]:
        """Identify cloud services needed."""
        services = ["AWS/GCP Core"]
        
        if brief.technical_spec.database_needs:
            services.append("Managed Database")
        if brief.technical_spec.api_endpoints:
            services.append("API Gateway / Load Balancer")
        if any("queue" in req.lower() for req in brief.technical_spec.backend_requirements):
            services.append("Message Queue (SQS/PubSub)")
        
        return services


def test_to_interface():
    """Test the Technical Operator interface."""
    import asyncio
    
    async def run_test():
        # Create TO interface
        to_interface = TechnicalOperatorInterface()
        
        # Create test checkpoint
        checkpoint = await to_interface.create_checkpoint(
            type=CheckpointType.PROJECT_APPROVAL,
            project_id="proj_123",
            project_name="Read Later Digest",
            agent_id="orch_456",
            agent_name="Task Orchestrator",
            title="New Project Approval",
            description="Approve new automation project for article summarization",
            priority=CheckpointPriority.HIGH,
            options=[
                {"label": "Approve", "description": "Start project"},
                {"label": "Reject", "description": "Cancel project"}
            ]
        )
        
        print("Created checkpoint:")
        print(checkpoint.to_message())
        
        # Simulate TO response
        await asyncio.sleep(1)
        await to_interface.respond_to_checkpoint(
            checkpoint.id,
            "Approve",
            {"notes": "Looks good, proceed with standard infrastructure"}
        )
        
        # Check summary
        summary = to_interface.get_checkpoint_summary()
        print(f"\nCheckpoint Summary: {summary}")
    
    asyncio.run(run_test())


if __name__ == "__main__":
    test_to_interface()