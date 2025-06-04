#!/usr/bin/env python3
"""
Communication Bridge - Enables ongoing communication between Hermes and specialist agents.
Translates technical updates into user-friendly language and vice versa.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages in the bridge."""
    PROGRESS_UPDATE = "progress_update"
    BLOCKER_ALERT = "blocker_alert"
    CLARIFICATION_REQUEST = "clarification_request"
    DECISION_NEEDED = "decision_needed"
    MILESTONE_REACHED = "milestone_reached"
    DELIVERABLE_READY = "deliverable_ready"
    CLIENT_FEEDBACK = "client_feedback"
    REQUIREMENT_CHANGE = "requirement_change"


class UpdateSeverity(Enum):
    """Severity levels for updates."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class CommunicationBridge:
    """
    Bridges communication between Hermes (user-facing) and specialist agents.
    Handles translation, filtering, and routing of messages.
    """
    
    def __init__(self):
        """Initialize the communication bridge."""
        self.message_queue: List[Dict[str, Any]] = []
        self.conversation_context: Dict[str, Any] = {}
        self.technical_to_plain: Dict[str, str] = self._load_translation_mappings()
        self.update_filters = {
            "show_progress": True,
            "show_blockers": True,
            "show_milestones": True,
            "batch_minor_updates": True
        }
    
    def _load_translation_mappings(self) -> Dict[str, str]:
        """Load technical term to plain language mappings."""
        return {
            # Technical terms to user-friendly terms
            "api endpoint": "connection point",
            "database schema": "data structure",
            "unit test": "quality check",
            "deployment": "making it live",
            "ci/cd pipeline": "automated publishing system",
            "authentication": "login system",
            "integration": "connecting services",
            "migration": "data transfer",
            "refactoring": "code improvement",
            "pull request": "code review",
            "merge conflict": "code overlap issue",
            "dependency": "required component",
            "framework": "foundation tools",
            "backend": "server-side",
            "frontend": "user interface",
            "infrastructure": "technical foundation",
            "scalability": "ability to grow",
            "performance optimization": "speed improvement",
            "security audit": "safety check",
            "api rate limiting": "usage controls",
            "caching": "temporary storage for speed",
            "load balancer": "traffic distributor",
            "microservice": "specialized component",
            "containerization": "packaging for deployment",
            "orchestration": "coordination system"
        }
    
    async def process_agent_update(self, update: Dict[str, Any]) -> Optional[str]:
        """
        Process an update from specialist agents into user-friendly format.
        Returns formatted message or None if filtered.
        """
        message_type = MessageType(update.get("type", MessageType.PROGRESS_UPDATE))
        severity = UpdateSeverity(update.get("severity", UpdateSeverity.INFO))
        
        # Filter based on user preferences
        if not self._should_show_update(message_type, severity):
            self.message_queue.append(update)  # Queue for batching
            return None
        
        # Format based on message type
        if message_type == MessageType.PROGRESS_UPDATE:
            return self._format_progress_update(update)
        elif message_type == MessageType.BLOCKER_ALERT:
            return self._format_blocker_alert(update)
        elif message_type == MessageType.CLARIFICATION_REQUEST:
            return self._format_clarification_request(update)
        elif message_type == MessageType.DECISION_NEEDED:
            return self._format_decision_request(update)
        elif message_type == MessageType.MILESTONE_REACHED:
            return self._format_milestone_update(update)
        elif message_type == MessageType.DELIVERABLE_READY:
            return self._format_deliverable_update(update)
        
        return None
    
    def _should_show_update(self, message_type: MessageType, severity: UpdateSeverity) -> bool:
        """Determine if update should be shown immediately."""
        # Always show high-priority items
        if severity in [UpdateSeverity.ERROR, UpdateSeverity.WARNING]:
            return True
        
        # Check filters
        if message_type == MessageType.PROGRESS_UPDATE and not self.update_filters["show_progress"]:
            return False
        if message_type == MessageType.BLOCKER_ALERT and not self.update_filters["show_blockers"]:
            return False
        if message_type == MessageType.MILESTONE_REACHED and not self.update_filters["show_milestones"]:
            return False
        
        # Batch minor updates if enabled
        if self.update_filters["batch_minor_updates"] and severity == UpdateSeverity.INFO:
            return False
        
        return True
    
    def _translate_technical_terms(self, text: str) -> str:
        """Translate technical terms to user-friendly language."""
        result = text
        for technical, plain in self.technical_to_plain.items():
            result = result.replace(technical, plain)
        return result
    
    def _format_progress_update(self, update: Dict[str, Any]) -> str:
        """Format a progress update for the user."""
        agent_name = update.get("agent_name", "Team")
        task_name = update.get("task_name", "current task")
        progress = update.get("progress", 0)
        details = update.get("details", "")
        
        # Translate technical details
        details = self._translate_technical_terms(details)
        
        if progress == 100:
            return f"✅ **{agent_name} completed**: {task_name}\n{details}"
        elif progress == 0:
            return f"🚀 **{agent_name} started**: {task_name}"
        else:
            return f"⚡ **{agent_name} progress**: {task_name} ({progress}% complete)"
    
    def _format_blocker_alert(self, update: Dict[str, Any]) -> str:
        """Format a blocker alert for the user."""
        blocker_type = update.get("blocker_type", "issue")
        description = self._translate_technical_terms(update.get("description", ""))
        impact = update.get("impact", "")
        resolution = update.get("resolution_eta", "")
        
        message = f"⚠️ **Development Update**: We've encountered a {blocker_type}.\n\n"
        message += f"**What happened**: {description}\n"
        
        if impact:
            message += f"**Impact**: {impact}\n"
        
        if resolution:
            message += f"**Expected resolution**: {resolution}\n"
        else:
            message += "Our team is working on a solution."
        
        return message
    
    def _format_clarification_request(self, update: Dict[str, Any]) -> str:
        """Format a clarification request for the user."""
        agent_name = update.get("agent_name", "The team")
        question = self._translate_technical_terms(update.get("question", ""))
        context = self._translate_technical_terms(update.get("context", ""))
        options = update.get("options", [])
        
        message = f"❓ **{agent_name} needs clarification**:\n\n"
        
        if context:
            message += f"**Context**: {context}\n\n"
        
        message += f"**Question**: {question}\n"
        
        if options:
            message += "\n**Options**:\n"
            for i, option in enumerate(options, 1):
                message += f"{i}. {self._translate_technical_terms(option)}\n"
        
        return message
    
    def _format_decision_request(self, update: Dict[str, Any]) -> str:
        """Format a decision request for the user."""
        decision_type = update.get("decision_type", "technical choice")
        description = self._translate_technical_terms(update.get("description", ""))
        options = update.get("options", [])
        recommendation = update.get("recommendation", "")
        
        message = f"🤔 **Decision needed**: {decision_type}\n\n"
        message += f"{description}\n"
        
        if options:
            message += "\n**Your options**:\n"
            for option in options:
                pros = self._translate_technical_terms(option.get("pros", ""))
                cons = self._translate_technical_terms(option.get("cons", ""))
                message += f"\n**{option['name']}**:\n"
                if pros:
                    message += f"  ✅ Pros: {pros}\n"
                if cons:
                    message += f"  ❌ Cons: {cons}\n"
        
        if recommendation:
            message += f"\n💡 **Team recommendation**: {self._translate_technical_terms(recommendation)}"
        
        return message
    
    def _format_milestone_update(self, update: Dict[str, Any]) -> str:
        """Format a milestone achievement for the user."""
        milestone = update.get("milestone", "project milestone")
        description = self._translate_technical_terms(update.get("description", ""))
        next_steps = update.get("next_steps", "")
        
        message = f"🎉 **Milestone reached**: {milestone}!\n\n"
        
        if description:
            message += f"{description}\n"
        
        if next_steps:
            message += f"\n**Next steps**: {self._translate_technical_terms(next_steps)}"
        
        return message
    
    def _format_deliverable_update(self, update: Dict[str, Any]) -> str:
        """Format a deliverable ready notification."""
        deliverable = update.get("deliverable", "component")
        description = self._translate_technical_terms(update.get("description", ""))
        access_info = update.get("access_info", "")
        
        message = f"📦 **Ready for review**: {deliverable}\n\n"
        
        if description:
            message += f"{description}\n"
        
        if access_info:
            message += f"\n**How to access**: {access_info}"
        
        return message
    
    async def process_user_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a user message that needs to be sent to the development team.
        Returns routing information and translated message.
        """
        # Detect message intent
        intent = self._detect_user_intent(message)
        
        # Determine routing
        routing = self._determine_routing(intent, context)
        
        # Translate to technical language if needed
        technical_message = self._translate_to_technical(message, intent)
        
        return {
            "original_message": message,
            "technical_message": technical_message,
            "intent": intent,
            "routing": routing,
            "priority": self._determine_priority(message, intent),
            "requires_response": self._requires_response(intent)
        }
    
    def _detect_user_intent(self, message: str) -> str:
        """Detect the intent of a user message."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["change", "modify", "update", "different"]):
            return "requirement_change"
        elif any(word in message_lower for word in ["status", "progress", "how's", "update"]):
            return "status_request"
        elif any(word in message_lower for word in ["problem", "issue", "wrong", "error", "bug"]):
            return "issue_report"
        elif any(word in message_lower for word in ["looks good", "great", "perfect", "approved"]):
            return "approval"
        elif any(word in message_lower for word in ["when", "timeline", "deadline", "eta"]):
            return "timeline_query"
        elif "?" in message:
            return "question"
        else:
            return "feedback"
    
    def _determine_routing(self, intent: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Determine where to route the message."""
        routing = {
            "primary": "orchestrator",  # Default to orchestrator
            "cc": []
        }
        
        # Route based on intent and context
        if intent == "requirement_change":
            routing["cc"] = ["all_agents"]  # Notify all agents
        elif intent == "issue_report":
            # Route to relevant agent based on context
            if "current_task" in context:
                task_type = context["current_task"].get("type", "")
                if "frontend" in task_type:
                    routing["cc"].append("aphrodite")
                elif "backend" in task_type:
                    routing["cc"].append("apollo")
                elif "test" in task_type:
                    routing["cc"].append("athena")
        
        return routing
    
    def _translate_to_technical(self, message: str, intent: str) -> str:
        """Translate user message to technical language if needed."""
        if intent in ["requirement_change", "issue_report"]:
            # Add technical context
            technical_additions = []
            
            if "button" in message.lower():
                technical_additions.append("(UI component)")
            if "slow" in message.lower():
                technical_additions.append("(performance issue)")
            if "login" in message.lower():
                technical_additions.append("(authentication flow)")
            if "data" in message.lower() and "save" in message.lower():
                technical_additions.append("(persistence layer)")
            
            if technical_additions:
                return f"{message} {' '.join(technical_additions)}"
        
        return message
    
    def _determine_priority(self, message: str, intent: str) -> str:
        """Determine message priority."""
        high_priority_words = ["urgent", "asap", "critical", "broken", "emergency"]
        
        if any(word in message.lower() for word in high_priority_words):
            return "high"
        elif intent in ["requirement_change", "issue_report"]:
            return "medium"
        else:
            return "low"
    
    def _requires_response(self, intent: str) -> bool:
        """Determine if the message requires a response."""
        return intent in ["question", "status_request", "timeline_query", "issue_report"]
    
    def get_batched_updates(self) -> Optional[str]:
        """Get batched minor updates if any are queued."""
        if not self.message_queue:
            return None
        
        # Group updates by type
        progress_updates = []
        other_updates = []
        
        for update in self.message_queue:
            if update.get("type") == MessageType.PROGRESS_UPDATE.value:
                progress_updates.append(update)
            else:
                other_updates.append(update)
        
        # Clear queue
        self.message_queue.clear()
        
        # Format batched message
        if not progress_updates and not other_updates:
            return None
        
        message = "📊 **Team Update Summary**:\n\n"
        
        if progress_updates:
            message += "**Progress on tasks**:\n"
            for update in progress_updates[:5]:  # Limit to 5
                agent = update.get("agent_name", "Team")
                task = update.get("task_name", "task")
                progress = update.get("progress", 0)
                message += f"  • {agent}: {task} ({progress}% complete)\n"
            
            if len(progress_updates) > 5:
                message += f"  • ...and {len(progress_updates) - 5} more tasks\n"
        
        return message
    
    def create_status_summary(self, project_status: Dict[str, Any]) -> str:
        """Create a user-friendly status summary."""
        tasks_total = project_status.get("total_tasks", 0)
        tasks_completed = project_status.get("completed_tasks", 0)
        tasks_in_progress = project_status.get("in_progress_tasks", 0)
        blockers = project_status.get("active_blockers", 0)
        
        progress_percentage = (tasks_completed / tasks_total * 100) if tasks_total > 0 else 0
        
        summary = f"""📈 **Project Status Update**

**Overall Progress**: {progress_percentage:.0f}% complete

**Tasks**:
  ✅ Completed: {tasks_completed}
  ⚡ In Progress: {tasks_in_progress}
  📋 Remaining: {tasks_total - tasks_completed - tasks_in_progress}
"""
        
        if blockers > 0:
            summary += f"\n⚠️ **Active Issues**: {blockers} (team is addressing these)"
        
        # Add timeline status
        if "estimated_completion" in project_status:
            completion_date = project_status["estimated_completion"]
            summary += f"\n\n📅 **Estimated Completion**: {completion_date}"
        
        # Add recent achievements
        if "recent_milestones" in project_status:
            milestones = project_status["recent_milestones"]
            if milestones:
                summary += "\n\n**Recent Achievements**:"
                for milestone in milestones[:3]:
                    summary += f"\n  🎯 {milestone}"
        
        return summary


def test_communication_bridge():
    """Test the communication bridge."""
    bridge = CommunicationBridge()
    
    # Test agent update processing
    print("Testing Agent Updates:")
    print("=" * 60)
    
    updates = [
        {
            "type": MessageType.PROGRESS_UPDATE.value,
            "severity": UpdateSeverity.INFO.value,
            "agent_name": "Apollo",
            "task_name": "API endpoint creation",
            "progress": 50,
            "details": "Implementing REST API for user authentication"
        },
        {
            "type": MessageType.BLOCKER_ALERT.value,
            "severity": UpdateSeverity.WARNING.value,
            "blocker_type": "technical challenge",
            "description": "The API rate limiting is causing issues with third-party integration",
            "impact": "May delay the integration by a few hours",
            "resolution_eta": "Within 2-3 hours"
        },
        {
            "type": MessageType.MILESTONE_REACHED.value,
            "severity": UpdateSeverity.SUCCESS.value,
            "milestone": "Backend API Complete",
            "description": "All backend API endpoints are now functional and tested",
            "next_steps": "Frontend integration can now begin"
        }
    ]
    
    for update in updates:
        result = asyncio.run(bridge.process_agent_update(update))
        if result:
            print(f"\n{result}")
            print("-" * 40)
    
    # Test user message processing
    print("\n\nTesting User Messages:")
    print("=" * 60)
    
    user_messages = [
        "How's the progress going?",
        "Can we change the button color to blue instead?",
        "This is urgent - the login isn't working!",
        "When will the project be ready?"
    ]
    
    for message in user_messages:
        result = asyncio.run(bridge.process_user_message(message, {"current_task": {"type": "frontend"}}))
        print(f"\nUser: {message}")
        print(f"Intent: {result['intent']}")
        print(f"Priority: {result['priority']}")
        print(f"Routing: {result['routing']}")
        print("-" * 40)


if __name__ == "__main__":
    test_communication_bridge()