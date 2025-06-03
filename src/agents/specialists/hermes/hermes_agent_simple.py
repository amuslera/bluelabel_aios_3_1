"""
Simplified Hermes Agent for testing without full infrastructure dependencies.
"""

import json
import uuid
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


class IntentBucket(Enum):
    """High-level intent categories for conversation routing."""
    BUILD = "build_something"
    AUTOMATE = "automate_task"
    ANALYZE = "analyze_data"
    EXPLORE = "explore_platform"
    SUPPORT = "get_support"
    UNKNOWN = "unknown"


@dataclass
class IntentSnapshot:
    """Captures intent state at a specific conversation turn."""
    turn: int
    bucket: IntentBucket
    specific_type: Optional[str]
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    user_input: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "turn": self.turn,
            "bucket": self.bucket.value,
            "specific_type": self.specific_type,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "user_input": self.user_input
        }


@dataclass
class IntentState:
    """Tracks the evolution of user intent throughout conversation."""
    current_bucket: IntentBucket = IntentBucket.UNKNOWN
    specific_type: Optional[str] = None
    confidence: float = 0.0
    evolution: List[IntentSnapshot] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update(self, turn: int, bucket: IntentBucket, 
               specific_type: Optional[str] = None, 
               confidence: float = 0.0,
               user_input: str = "") -> None:
        """Update intent state and track evolution."""
        self.current_bucket = bucket
        self.specific_type = specific_type
        self.confidence = confidence
        
        snapshot = IntentSnapshot(
            turn=turn,
            bucket=bucket,
            specific_type=specific_type,
            confidence=confidence,
            user_input=user_input
        )
        self.evolution.append(snapshot)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for export."""
        return {
            "current_bucket": self.current_bucket.value,
            "specific_type": self.specific_type,
            "confidence": self.confidence,
            "evolution": [s.to_dict() for s in self.evolution],
            "metadata": self.metadata
        }


@dataclass
class PersonaConfig:
    """Configuration for Hermes' dynamic personality."""
    tone: str = "friendly_professional"
    focus: str = "general"
    verbosity: str = "balanced"
    emoji_usage: bool = True
    encouragement_level: str = "high"
    technical_depth: str = "adaptive"
    
    def get_system_prompt_modifiers(self) -> str:
        """Generate persona-specific prompt modifiers."""
        modifiers = []
        
        if self.tone == "friendly_professional":
            modifiers.append("Be warm and approachable while maintaining professionalism.")
        elif self.tone == "formal":
            modifiers.append("Maintain a formal, business-appropriate tone.")
        elif self.tone == "casual":
            modifiers.append("Use a casual, conversational tone.")
        
        if self.focus == "developer":
            modifiers.append("Use technical terminology freely.")
        elif self.focus == "business":
            modifiers.append("Focus on business value and avoid jargon.")
        
        if self.verbosity == "concise":
            modifiers.append("Keep responses brief.")
        elif self.verbosity == "detailed":
            modifiers.append("Provide comprehensive explanations.")
        
        return " ".join(modifiers)


@dataclass
class ConversationState:
    """Maintains the full state of a Hermes conversation."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    turn_count: int = 0
    messages: List[Dict[str, str]] = field(default_factory=list)
    intent_state: IntentState = field(default_factory=IntentState)
    user_context: Dict[str, Any] = field(default_factory=dict)
    project_requirements: Dict[str, Any] = field(default_factory=dict)
    ready_for_handoff: bool = False
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "turn": self.turn_count
        })
        if role == "user":
            self.turn_count += 1
    
    def export_markdown(self) -> str:
        """Export conversation as markdown."""
        md_lines = [
            f"# Hermes Conversation - Session {self.session_id}",
            f"Date: {self.created_at.strftime('%Y-%m-%d %I:%M %p')}",
            f"Duration: {self.turn_count} turns",
            f"Intent: {self.intent_state.current_bucket.value}",
            f"Confidence: {self.intent_state.confidence:.0%}",
            "",
            "## Conversation",
            ""
        ]
        
        for msg in self.messages:
            role = "Hermes" if msg["role"] == "assistant" else "User"
            md_lines.append(f"**{role}**: {msg['content']}")
            md_lines.append("")
        
        md_lines.extend([
            "## Intent Evolution"
        ])
        for snapshot in self.intent_state.evolution:
            md_lines.append(
                f"- Turn {snapshot.turn}: {snapshot.bucket.value} "
                f"({snapshot.confidence:.0%})"
            )
        
        if self.project_requirements:
            md_lines.extend([
                "",
                "## Extracted Requirements"
            ])
            for key, value in self.project_requirements.items():
                md_lines.append(f"- {key}: {value}")
        
        return "\n".join(md_lines)
    
    def export_json(self) -> str:
        """Export conversation as JSON."""
        export_data = {
            "session_id": self.session_id,
            "timestamp": self.created_at.isoformat(),
            "turn_count": self.turn_count,
            "intent_final": self.intent_state.to_dict(),
            "conversation": self.messages,
            "user_context": self.user_context,
            "project_requirements": self.project_requirements,
            "metadata": {
                "ready_for_prd": self.ready_for_handoff,
                "clarifications_needed": self._get_clarifications_needed()
            }
        }
        return json.dumps(export_data, indent=2)
    
    def _get_clarifications_needed(self) -> List[str]:
        """Determine what clarifications are still needed."""
        needed = []
        reqs = self.project_requirements
        
        if not reqs.get("project_type"):
            needed.append("project_type")
        if not reqs.get("timeline"):
            needed.append("timeline")
        if not reqs.get("features"):
            needed.append("features")
        
        return needed


class SimpleHermesAgent:
    """Simplified Hermes agent for testing."""
    
    def __init__(self, persona_config: Optional[PersonaConfig] = None):
        """Initialize Hermes with configurable persona."""
        self.name = "Hermes"
        self.persona = persona_config or PersonaConfig()
        self.conversations: Dict[str, ConversationState] = {}
        self.platform_knowledge = self._load_platform_knowledge()
        self.intent_patterns = self._load_intent_patterns()
        self.logger = logging.getLogger("hermes")
    
    def _load_platform_knowledge(self) -> Dict[str, Any]:
        """Load knowledge about platform capabilities."""
        return {
            "agents": {
                "Apollo": "Backend development - APIs, databases, system architecture",
                "Aphrodite": "Frontend development - UI/UX, React, accessibility",
                "Athena": "Quality assurance - Testing, bug detection, security",
                "Hephaestus": "DevOps - CI/CD, deployment, infrastructure"
            },
            "project_types": [
                "website", "web_app", "mobile_app", "api", "database",
                "ecommerce", "saas", "portfolio", "blog", "dashboard"
            ]
        }
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for intent detection."""
        return {
            "build": [
                "build", "create", "make", "develop", "need",
                "website", "app", "application", "api", "database",
                "store", "shop", "ecommerce", "portfolio", "blog"
            ],
            "automate": [
                "automate", "workflow", "pipeline", "process",
                "schedule", "trigger", "integration", "connect"
            ],
            "analyze": [
                "analyze", "analyse", "review", "audit", "check",
                "performance", "security", "quality", "metrics"
            ]
        }
    
    def process_conversation(
        self,
        user_input: str,
        session_id: Optional[str] = None
    ) -> Tuple[str, ConversationState]:
        """Process a conversation turn with intent tracking."""
        # Get or create conversation state
        if session_id and session_id in self.conversations:
            state = self.conversations[session_id]
        else:
            state = ConversationState()
            self.conversations[state.session_id] = state
        
        # Add user message
        state.add_message("user", user_input)
        
        # Detect intent
        intent_bucket, specific_type, confidence = self._detect_intent(
            user_input, state
        )
        state.intent_state.update(
            turn=state.turn_count,
            bucket=intent_bucket,
            specific_type=specific_type,
            confidence=confidence,
            user_input=user_input
        )
        
        # Generate response (fallback without LLM)
        response = self._get_fallback_response(state)
        
        # Add assistant message
        state.add_message("assistant", response)
        
        # Extract any requirements
        if intent_bucket == IntentBucket.BUILD:
            self._extract_requirements(user_input, state)
        
        # Check if ready for handoff
        state.ready_for_handoff = self._check_handoff_ready(state)
        
        self.logger.info(
            f"Turn {state.turn_count} - Intent: {intent_bucket.value} "
            f"({confidence:.0%}) - Type: {specific_type}"
        )
        
        return response, state
    
    def _detect_intent(
        self,
        user_input: str,
        state: ConversationState
    ) -> Tuple[IntentBucket, Optional[str], float]:
        """Detect user intent from input."""
        input_lower = user_input.lower()
        
        # Count matches for each intent
        build_matches = sum(1 for word in self.intent_patterns["build"] 
                          if word in input_lower)
        automate_matches = sum(1 for word in self.intent_patterns["automate"] 
                             if word in input_lower)
        analyze_matches = sum(1 for word in self.intent_patterns["analyze"] 
                            if word in input_lower)
        
        # Determine primary intent
        if build_matches > max(automate_matches, analyze_matches):
            bucket = IntentBucket.BUILD
            confidence = min(0.95, 0.3 + (build_matches * 0.15))
            
            # Detect specific type
            if any(word in input_lower for word in ["ecommerce", "store", "shop"]):
                specific_type = "ecommerce_site"
            elif "portfolio" in input_lower:
                specific_type = "portfolio_site"
            elif "blog" in input_lower:
                specific_type = "blog_site"
            elif "api" in input_lower:
                specific_type = "api_service"
            else:
                specific_type = "website"
                
        elif automate_matches > analyze_matches:
            bucket = IntentBucket.AUTOMATE
            confidence = min(0.95, 0.3 + (automate_matches * 0.2))
            specific_type = "workflow_automation"
            
        elif analyze_matches > 0:
            bucket = IntentBucket.ANALYZE
            confidence = min(0.95, 0.3 + (analyze_matches * 0.2))
            specific_type = "code_analysis"
            
        elif state.turn_count == 1:
            bucket = IntentBucket.EXPLORE
            confidence = 0.5
            specific_type = None
            
        else:
            bucket = state.intent_state.current_bucket
            confidence = state.intent_state.confidence * 0.8
            specific_type = state.intent_state.specific_type
        
        return bucket, specific_type, confidence
    
    def _extract_requirements(self, user_input: str, state: ConversationState):
        """Extract project requirements from user input."""
        input_lower = user_input.lower()
        
        # Extract business type
        business_types = ["bakery", "restaurant", "shop", "store", "agency", 
                         "clinic", "salon", "studio"]
        for btype in business_types:
            if btype in input_lower:
                state.project_requirements["business_type"] = btype
                break
        
        # Extract product count
        import re
        product_match = re.search(r'(\d+)\s*products?', input_lower)
        if product_match:
            state.project_requirements["product_count"] = int(product_match.group(1))
        
        # Extract features
        if "online" in input_lower and "order" in input_lower:
            if "features" not in state.project_requirements:
                state.project_requirements["features"] = []
            state.project_requirements["features"].append("online_ordering")
    
    def _get_fallback_response(self, state: ConversationState) -> str:
        """Generate a fallback response without LLM."""
        if state.turn_count == 1:
            emoji = "🪽" if self.persona.emoji_usage else ""
            return (
                f"Welcome! I'm Hermes, your guide to building software with AI. {emoji}\n\n"
                "I can help you:\n"
                "• Build websites, apps, or APIs\n"
                "• Automate workflows and processes\n"
                "• Analyze data and code\n\n"
                "What would you like to create today?"
            )
        
        intent = state.intent_state.current_bucket
        
        if intent == IntentBucket.BUILD:
            if state.intent_state.specific_type == "ecommerce_site":
                return (
                    "Great! An online store it is. To help our AI team build "
                    "exactly what you need, could you tell me:\n"
                    "• What products will you sell?\n"
                    "• Do you have product photos ready?\n"
                    "• Any special features needed? (delivery, subscriptions, etc.)"
                )
            return (
                "I understand you want to build something! To help our AI team "
                "create exactly what you need, could you tell me more about:\n"
                "• What type of project (website, app, API)?\n"
                "• Who will use it?\n"
                "• Any specific features you have in mind?"
            )
        
        return (
            "I'm here to help! Could you tell me more about what you'd "
            "like to accomplish? Our AI team can handle various projects "
            "from websites to automation workflows."
        )
    
    def _check_handoff_ready(self, state: ConversationState) -> bool:
        """Check if we have enough information for project handoff."""
        reqs = state.project_requirements
        
        # For MVP, just check if we have basic project understanding
        if state.intent_state.current_bucket == IntentBucket.BUILD:
            return bool(reqs.get("business_type") or reqs.get("project_type"))
        
        return False
    
    def export_session(
        self,
        session_id: str,
        format: str = "markdown"
    ) -> Optional[str]:
        """Export a conversation session."""
        if session_id not in self.conversations:
            return None
        
        state = self.conversations[session_id]
        
        if format == "markdown":
            return state.export_markdown()
        elif format == "json":
            return state.export_json()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get summary of active conversation sessions."""
        sessions = []
        
        for session_id, state in self.conversations.items():
            sessions.append({
                "session_id": session_id,
                "created_at": state.created_at.isoformat(),
                "turn_count": state.turn_count,
                "intent": state.intent_state.current_bucket.value,
                "confidence": state.intent_state.confidence,
                "ready_for_handoff": state.ready_for_handoff
            })
        
        return sessions