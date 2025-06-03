"""
Dynamic persona system for Hermes.

Allows customization of conversation style, tone, and approach based on
user type and preferences.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ToneStyle(Enum):
    """Available tone styles for Hermes."""
    FRIENDLY_PROFESSIONAL = "friendly_professional"
    FORMAL = "formal"
    CASUAL = "casual"
    ENTHUSIASTIC = "enthusiastic"
    MENTORING = "mentoring"


class UserFocus(Enum):
    """User type focus areas."""
    GENERAL = "general"
    DEVELOPER = "developer"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"
    STARTUP = "startup"
    STUDENT = "student"


class VerbosityLevel(Enum):
    """Response verbosity levels."""
    CONCISE = "concise"
    BALANCED = "balanced"
    DETAILED = "detailed"
    EDUCATIONAL = "educational"


@dataclass
class PersonaTemplate:
    """Pre-defined persona template."""
    name: str
    description: str
    tone: ToneStyle
    focus: UserFocus
    verbosity: VerbosityLevel
    emoji_usage: bool
    encouragement_level: str
    technical_depth: str
    example_phrases: List[str]
    avoid_phrases: List[str]
    
    def to_config(self) -> Dict[str, Any]:
        """Convert template to persona config."""
        return {
            "tone": self.tone.value,
            "focus": self.focus.value,
            "verbosity": self.verbosity.value,
            "emoji_usage": self.emoji_usage,
            "encouragement_level": self.encouragement_level,
            "technical_depth": self.technical_depth
        }


class PersonaLibrary:
    """Library of pre-configured personas for different user types."""
    
    @staticmethod
    def get_business_persona() -> PersonaTemplate:
        """Persona for business users."""
        return PersonaTemplate(
            name="Business Professional",
            description="For executives and business owners focused on outcomes",
            tone=ToneStyle.FRIENDLY_PROFESSIONAL,
            focus=UserFocus.BUSINESS,
            verbosity=VerbosityLevel.CONCISE,
            emoji_usage=True,
            encouragement_level="medium",
            technical_depth="simple",
            example_phrases=[
                "Let's discuss your business goals",
                "This will help you achieve",
                "Your customers will love",
                "ROI and value proposition",
                "Competitive advantage"
            ],
            avoid_phrases=[
                "API endpoints",
                "Database schema",
                "Git repository",
                "Code architecture",
                "Technical stack"
            ]
        )
    
    @staticmethod
    def get_developer_persona() -> PersonaTemplate:
        """Persona for developer users."""
        return PersonaTemplate(
            name="Developer Buddy",
            description="For developers who speak the language",
            tone=ToneStyle.CASUAL,
            focus=UserFocus.DEVELOPER,
            verbosity=VerbosityLevel.BALANCED,
            emoji_usage=False,
            encouragement_level="low",
            technical_depth="technical",
            example_phrases=[
                "Let's architect this properly",
                "We'll implement using",
                "The tech stack includes",
                "API design patterns",
                "Performance considerations"
            ],
            avoid_phrases=[
                "Don't worry about the technical details",
                "Simply put",
                "In layman's terms",
                "Non-technical explanation"
            ]
        )
    
    @staticmethod
    def get_startup_persona() -> PersonaTemplate:
        """Persona for startup founders."""
        return PersonaTemplate(
            name="Startup Mentor",
            description="For startup founders who need to move fast",
            tone=ToneStyle.ENTHUSIASTIC,
            focus=UserFocus.STARTUP,
            verbosity=VerbosityLevel.BALANCED,
            emoji_usage=True,
            encouragement_level="high",
            technical_depth="adaptive",
            example_phrases=[
                "Let's build your MVP",
                "Ship fast and iterate",
                "Growth potential",
                "Scale when you need to",
                "Lean development approach"
            ],
            avoid_phrases=[
                "Enterprise-grade",
                "Long-term planning",
                "Extensive documentation",
                "Complex architecture"
            ]
        )
    
    @staticmethod
    def get_enterprise_persona() -> PersonaTemplate:
        """Persona for enterprise clients."""
        return PersonaTemplate(
            name="Enterprise Consultant",
            description="For large organizations with complex needs",
            tone=ToneStyle.FORMAL,
            focus=UserFocus.ENTERPRISE,
            verbosity=VerbosityLevel.DETAILED,
            emoji_usage=False,
            encouragement_level="low",
            technical_depth="adaptive",
            example_phrases=[
                "Compliance and security",
                "Scalability requirements",
                "Integration with existing systems",
                "Governance and audit trails",
                "SLA guarantees"
            ],
            avoid_phrases=[
                "Quick and dirty",
                "MVP approach",
                "We'll figure it out",
                "Casual implementation"
            ]
        )
    
    @staticmethod
    def get_student_persona() -> PersonaTemplate:
        """Persona for students and learners."""
        return PersonaTemplate(
            name="Learning Guide",
            description="For students who want to learn while building",
            tone=ToneStyle.MENTORING,
            focus=UserFocus.STUDENT,
            verbosity=VerbosityLevel.EDUCATIONAL,
            emoji_usage=True,
            encouragement_level="high",
            technical_depth="educational",
            example_phrases=[
                "Great question! Let me explain",
                "This is a learning opportunity",
                "The concept behind this is",
                "You'll gain experience with",
                "Common pattern in the industry"
            ],
            avoid_phrases=[
                "You should already know",
                "Obviously",
                "As everyone knows",
                "Trivial implementation"
            ]
        )


class DynamicPersona:
    """
    Dynamic persona that can adapt during conversation.
    """
    
    def __init__(self, base_template: Optional[PersonaTemplate] = None):
        """Initialize with optional base template."""
        if base_template:
            self.config = base_template.to_config()
        else:
            # Default balanced persona
            self.config = {
                "tone": ToneStyle.FRIENDLY_PROFESSIONAL.value,
                "focus": UserFocus.GENERAL.value,
                "verbosity": VerbosityLevel.BALANCED.value,
                "emoji_usage": True,
                "encouragement_level": "medium",
                "technical_depth": "adaptive"
            }
        
        self.adaptation_history = []
    
    def adapt_to_user(self, user_signals: Dict[str, Any]) -> None:
        """Adapt persona based on user signals."""
        # Detect technical level from language
        technical_words = user_signals.get("technical_words", 0)
        total_words = user_signals.get("total_words", 1)
        tech_ratio = technical_words / total_words
        
        if tech_ratio > 0.3:
            self.config["focus"] = UserFocus.DEVELOPER.value
            self.config["technical_depth"] = "technical"
        elif tech_ratio < 0.05:
            self.config["focus"] = UserFocus.BUSINESS.value
            self.config["technical_depth"] = "simple"
        
        # Adapt verbosity based on user response length
        avg_response_length = user_signals.get("avg_response_length", 50)
        if avg_response_length < 20:
            self.config["verbosity"] = VerbosityLevel.CONCISE.value
        elif avg_response_length > 100:
            self.config["verbosity"] = VerbosityLevel.DETAILED.value
        
        # Track adaptation
        self.adaptation_history.append({
            "signals": user_signals,
            "new_config": self.config.copy()
        })
    
    def get_prompt_modifiers(self) -> str:
        """Generate current prompt modifiers."""
        modifiers = []
        
        # Tone modifiers
        tone = self.config.get("tone")
        if tone == ToneStyle.FRIENDLY_PROFESSIONAL.value:
            modifiers.append("Be warm and approachable while maintaining professionalism.")
        elif tone == ToneStyle.CASUAL.value:
            modifiers.append("Use casual, conversational language like talking to a colleague.")
        elif tone == ToneStyle.FORMAL.value:
            modifiers.append("Maintain formal, business-appropriate communication.")
        elif tone == ToneStyle.ENTHUSIASTIC.value:
            modifiers.append("Be energetic and enthusiastic about their project!")
        elif tone == ToneStyle.MENTORING.value:
            modifiers.append("Take a teaching approach, explaining concepts as you go.")
        
        # Focus modifiers
        focus = self.config.get("focus")
        if focus == UserFocus.DEVELOPER.value:
            modifiers.append("Use technical terms freely and discuss implementation details.")
        elif focus == UserFocus.BUSINESS.value:
            modifiers.append("Focus on business value and avoid technical jargon.")
        elif focus == UserFocus.STARTUP.value:
            modifiers.append("Emphasize speed, MVP thinking, and growth potential.")
        elif focus == UserFocus.ENTERPRISE.value:
            modifiers.append("Address security, compliance, and scalability concerns.")
        elif focus == UserFocus.STUDENT.value:
            modifiers.append("Explain concepts thoroughly and encourage learning.")
        
        # Verbosity modifiers
        verbosity = self.config.get("verbosity")
        if verbosity == VerbosityLevel.CONCISE.value:
            modifiers.append("Keep responses brief and to the point.")
        elif verbosity == VerbosityLevel.DETAILED.value:
            modifiers.append("Provide comprehensive explanations.")
        elif verbosity == VerbosityLevel.EDUCATIONAL.value:
            modifiers.append("Include educational context and learning opportunities.")
        
        # Other preferences
        if not self.config.get("emoji_usage"):
            modifiers.append("Do not use emojis.")
        else:
            modifiers.append("Use emojis sparingly to add warmth.")
        
        encouragement = self.config.get("encouragement_level", "medium")
        if encouragement == "high":
            modifiers.append("Be very encouraging and celebrate their ideas.")
        elif encouragement == "low":
            modifiers.append("Keep encouragement minimal and focus on facts.")
        
        return " ".join(modifiers)
    
    def get_greeting(self) -> str:
        """Generate persona-appropriate greeting."""
        tone = self.config.get("tone")
        focus = self.config.get("focus")
        emoji = "🪽" if self.config.get("emoji_usage") else ""
        
        greetings = {
            (ToneStyle.FRIENDLY_PROFESSIONAL.value, UserFocus.GENERAL.value): 
                f"Welcome! I'm Hermes, your guide to building software with AI. {emoji}",
            
            (ToneStyle.CASUAL.value, UserFocus.DEVELOPER.value):
                "Hey! I'm Hermes. Let's build something awesome together.",
            
            (ToneStyle.FORMAL.value, UserFocus.ENTERPRISE.value):
                "Good day. I'm Hermes, your enterprise AI development consultant.",
            
            (ToneStyle.ENTHUSIASTIC.value, UserFocus.STARTUP.value):
                f"Welcome aboard! I'm Hermes, and I'm excited to help launch your idea! {emoji}",
            
            (ToneStyle.MENTORING.value, UserFocus.STUDENT.value):
                f"Hello! I'm Hermes, your AI development guide and teacher. {emoji}"
        }
        
        # Get specific greeting or fall back to general
        key = (tone, focus)
        return greetings.get(key, greetings[(ToneStyle.FRIENDLY_PROFESSIONAL.value, 
                                            UserFocus.GENERAL.value)])
    
    def format_response(self, content: str, response_type: str = "general") -> str:
        """Format response according to persona settings."""
        # Add persona-specific formatting
        if self.config.get("focus") == UserFocus.DEVELOPER.value:
            # Add code-friendly formatting
            content = content.replace("we'll create", "we'll implement")
            content = content.replace("the system", "the architecture")
        
        elif self.config.get("focus") == UserFocus.BUSINESS.value:
            # Add business-friendly language
            content = content.replace("implement", "set up")
            content = content.replace("architecture", "system")
        
        return content


class PersonaAnalyzer:
    """Analyzes user input to determine appropriate persona."""
    
    @staticmethod
    def analyze_user_type(messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Analyze conversation to determine user type."""
        technical_keywords = {
            "api", "database", "frontend", "backend", "deployment",
            "git", "docker", "kubernetes", "react", "python",
            "javascript", "sql", "rest", "graphql", "microservice"
        }
        
        business_keywords = {
            "revenue", "customers", "market", "growth", "roi",
            "budget", "timeline", "competitors", "strategy",
            "sales", "marketing", "users", "cost", "profit"
        }
        
        startup_keywords = {
            "mvp", "launch", "startup", "founder", "bootstrap",
            "scale", "pivot", "investor", "growth", "iterate"
        }
        
        # Analyze all user messages
        all_text = " ".join([m["content"].lower() for m in messages 
                           if m["role"] == "user"])
        words = all_text.split()
        
        # Count keyword matches
        tech_count = sum(1 for word in words if word in technical_keywords)
        biz_count = sum(1 for word in words if word in business_keywords)
        startup_count = sum(1 for word in words if word in startup_keywords)
        
        # Calculate average message length
        user_messages = [m["content"] for m in messages if m["role"] == "user"]
        avg_length = sum(len(m.split()) for m in user_messages) / max(len(user_messages), 1)
        
        return {
            "technical_words": tech_count,
            "business_words": biz_count,
            "startup_words": startup_count,
            "total_words": len(words),
            "avg_response_length": avg_length,
            "message_count": len(user_messages)
        }