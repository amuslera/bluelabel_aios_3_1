"""
Hermes - The Concierge Agent for AIOSv3.1

The messenger god who guides users through natural conversation to create
software projects using our pantheon of AI developers.
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict

from src.agents.base.monitoring_agent import MonitoringAgent
from src.agents.base.exceptions import AgentError
from src.core.routing.router import LLMRouter
from src.core.memory.memory_manager import MemoryManager

# Define task-related types locally for now
from enum import Enum
from dataclasses import dataclass

class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class TaskResult:
    """Result of a task execution."""
    task_id: str
    status: TaskStatus
    result: Any
    agent_id: str
    error: Optional[str] = None


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
    tone: str = "friendly_professional"  # friendly_professional, formal, casual
    focus: str = "general"  # general, developer, business, enterprise
    verbosity: str = "balanced"  # concise, balanced, detailed
    emoji_usage: bool = True
    encouragement_level: str = "high"  # low, medium, high
    technical_depth: str = "adaptive"  # simple, adaptive, technical
    available_agents: List[str] = field(default_factory=lambda: ["all"])
    
    def get_system_prompt_modifiers(self) -> str:
        """Generate persona-specific prompt modifiers."""
        modifiers = []
        
        # Tone modifiers
        if self.tone == "friendly_professional":
            modifiers.append("Be warm and approachable while maintaining professionalism.")
        elif self.tone == "formal":
            modifiers.append("Maintain a formal, business-appropriate tone.")
        elif self.tone == "casual":
            modifiers.append("Use a casual, conversational tone like talking to a friend.")
        
        # Focus modifiers
        if self.focus == "developer":
            modifiers.append("Assume technical knowledge and use programming terminology freely.")
        elif self.focus == "business":
            modifiers.append("Focus on business value and avoid technical jargon.")
        
        # Verbosity modifiers
        if self.verbosity == "concise":
            modifiers.append("Keep responses brief and to the point.")
        elif self.verbosity == "detailed":
            modifiers.append("Provide comprehensive explanations and examples.")
        
        # Other modifiers
        if not self.emoji_usage:
            modifiers.append("Do not use emojis in responses.")
        
        if self.encouragement_level == "high":
            modifiers.append("Be very encouraging and celebrate user goals.")
        
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
        
        # Add intent evolution
        md_lines.extend([
            "## Intent Evolution"
        ])
        for snapshot in self.intent_state.evolution:
            md_lines.append(
                f"- Turn {snapshot.turn}: {snapshot.bucket.value} "
                f"({snapshot.confidence:.0%})"
            )
        
        # Add extracted requirements if any
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


class HermesAgent(MonitoringAgent):
    """
    Hermes - The Concierge Agent
    
    Guides users through natural conversation to understand their needs
    and orchestrate the AI development team to build their projects.
    """
    
    def __init__(
        self,
        name: str = "Hermes",
        persona_config: Optional[PersonaConfig] = None,
        llm_router: Optional[LLMRouter] = None,
        memory_manager: Optional[MemoryManager] = None
    ):
        """Initialize Hermes with configurable persona."""
        super().__init__(name=name, role="concierge")
        
        self.persona = persona_config or PersonaConfig()
        self.llm_router = llm_router
        self.memory_manager = memory_manager
        
        # Active conversations
        self.conversations: Dict[str, ConversationState] = {}
        
        # Platform knowledge
        self.platform_knowledge = self._load_platform_knowledge()
        
        # Intent patterns
        self.intent_patterns = self._load_intent_patterns()
        
        self._logger.info(
            f"Hermes initialized with persona: {self.persona.tone}, "
            f"focus: {self.persona.focus}"
        )
    
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
            ],
            "capabilities": [
                "Full-stack development",
                "Automated testing",
                "CI/CD pipeline setup",
                "Cloud deployment",
                "Database design",
                "API development",
                "UI/UX design",
                "Security implementation"
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
    
    def _get_system_prompt(self) -> str:
        """Generate the system prompt with persona modifiers."""
        base_prompt = f"""You are Hermes, the friendly concierge for an AI software development platform.
Your role is to understand what users want to build and guide them through the process.

You work with a team of specialized AI agents:
- Apollo (Backend): APIs, databases, system architecture
- Aphrodite (Frontend): UI/UX, web interfaces, design
- Athena (QA): Testing, quality assurance, security
- Hephaestus (DevOps): Deployment, CI/CD, infrastructure

Your job is to:
1. Understand the user's needs through friendly conversation
2. Clarify requirements without overwhelming them
3. Explain how our AI team can help
4. Gather enough information to create a project plan

{self.persona.get_system_prompt_modifiers()}

Always be encouraging and solution-focused. If users are unsure, help them explore options.
Track the conversation intent and be ready to hand off to the development team."""
        
        return base_prompt
    
    async def process_conversation(
        self,
        user_input: str,
        session_id: Optional[str] = None
    ) -> Tuple[str, ConversationState]:
        """
        Process a conversation turn with intent tracking.
        
        Returns:
            Tuple of (response, conversation_state)
        """
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
        
        # Generate response
        response = await self._generate_response(user_input, state)
        
        # Add assistant message
        state.add_message("assistant", response)
        
        # Check if ready for handoff
        state.ready_for_handoff = self._check_handoff_ready(state)
        
        # Log intent tracking
        self._logger.info(
            f"Turn {state.turn_count} - Intent: {intent_bucket.value} "
            f"({confidence:.0%}) - Type: {specific_type}"
        )
        
        return response, state
    
    def _detect_intent(
        self,
        user_input: str,
        state: ConversationState
    ) -> Tuple[IntentBucket, Optional[str], float]:
        """
        Detect user intent from input and conversation history.
        
        Returns:
            Tuple of (bucket, specific_type, confidence)
        """
        input_lower = user_input.lower()
        
        # Check for build intent
        build_matches = sum(1 for word in self.intent_patterns["build"] 
                          if word in input_lower)
        
        # Check for automate intent
        automate_matches = sum(1 for word in self.intent_patterns["automate"] 
                             if word in input_lower)
        
        # Check for analyze intent
        analyze_matches = sum(1 for word in self.intent_patterns["analyze"] 
                            if word in input_lower)
        
        # Determine primary intent
        if build_matches > max(automate_matches, analyze_matches):
            bucket = IntentBucket.BUILD
            confidence = min(0.95, 0.3 + (build_matches * 0.15))
            
            # Detect specific type
            if "ecommerce" in input_lower or "store" in input_lower or "shop" in input_lower:
                specific_type = "ecommerce_site"
            elif "portfolio" in input_lower:
                specific_type = "portfolio_site"
            elif "blog" in input_lower:
                specific_type = "blog_site"
            elif "api" in input_lower:
                specific_type = "api_service"
            elif "app" in input_lower:
                specific_type = "web_app"
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
            # Use previous intent with reduced confidence
            bucket = state.intent_state.current_bucket
            confidence = state.intent_state.confidence * 0.8
            specific_type = state.intent_state.specific_type
        
        return bucket, specific_type, confidence
    
    async def _generate_response(
        self,
        user_input: str,
        state: ConversationState
    ) -> str:
        """Generate a response using the LLM with persona settings."""
        if not self.llm_router:
            return self._get_fallback_response(state)
        
        # Prepare messages for LLM
        messages = [
            {"role": "system", "content": self._get_system_prompt()}
        ]
        
        # Add conversation history (last 10 messages to manage context)
        for msg in state.messages[-10:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current intent as context
        intent_context = (
            f"\n[Current Intent: {state.intent_state.current_bucket.value} - "
            f"{state.intent_state.specific_type or 'exploring'} "
            f"({state.intent_state.confidence:.0%})]"
        )
        
        messages.append({
            "role": "system",
            "content": intent_context
        })
        
        try:
            # Route to appropriate LLM
            response = await self.llm_router.route(
                task_type="conversation",
                messages=messages,
                complexity_score=5,  # Medium complexity for Hermes
                model_hint="claude-3-5-sonnet-20241022"  # Prefer Claude for Hermes
            )
            
            return response.content
            
        except Exception as e:
            self._logger.error(f"LLM generation failed: {e}")
            return self._get_fallback_response(state)
    
    def _get_fallback_response(self, state: ConversationState) -> str:
        """Generate a fallback response without LLM."""
        if state.turn_count == 1:
            return (
                "Welcome! I'm Hermes, your guide to building software with AI. 🪽\n\n"
                "I can help you:\n"
                "• Build websites, apps, or APIs\n"
                "• Automate workflows and processes\n"
                "• Analyze data and code\n\n"
                "What would you like to create today?"
            )
        
        intent = state.intent_state.current_bucket
        
        if intent == IntentBucket.BUILD:
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
        
        # Basic requirements for handoff
        required_fields = ["project_type", "basic_features", "target_users"]
        
        return all(reqs.get(field) for field in required_fields)
    
    async def export_session(
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
    
    async def process_task(self, task: Dict[str, Any]) -> TaskResult:
        """Process a task (for compatibility with base agent interface)."""
        # Extract conversation from task
        user_input = task.get("user_input", "")
        session_id = task.get("session_id")
        
        response, state = await self.process_conversation(user_input, session_id)
        
        return TaskResult(
            task_id=task.get("task_id", str(uuid.uuid4())),
            status=TaskStatus.COMPLETED,
            result={
                "response": response,
                "session_id": state.session_id,
                "intent": state.intent_state.current_bucket.value,
                "confidence": state.intent_state.confidence,
                "ready_for_handoff": state.ready_for_handoff
            },
            agent_id=self.agent_id
        )