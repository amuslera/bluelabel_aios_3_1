"""
Emily Rodriguez's dynamic personality system.

Creative, user-focused personality that evolves based on design interactions.
"""

import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


class DesignMoodState(Enum):
    """Emily's design-focused mood states."""
    INSPIRED = "inspired"        # Creative flow, innovative ideas
    FOCUSED = "focused"          # Deep design concentration
    COLLABORATIVE = "collaborative"  # Working with team on designs
    ANALYTICAL = "analytical"    # Analyzing user feedback/data
    PERFECTIONIST = "perfectionist"  # Refining details
    EMPATHETIC = "empathetic"    # Thinking about user needs


class CreativeEnergyLevel(Enum):
    """Emily's creative energy levels."""
    HIGHLY_CREATIVE = 5    # Peak creative state
    CREATIVE = 4           # Good creative flow
    BALANCED = 3           # Normal creative energy
    METHODICAL = 2         # More structured, less experimental
    DRAINED = 1            # Need creative break


@dataclass
class DesignPersonalityState:
    """Current state of Emily's design-focused personality."""
    mood: DesignMoodState = DesignMoodState.FOCUSED
    creative_energy: CreativeEnergyLevel = CreativeEnergyLevel.BALANCED
    user_empathy_level: float = 0.9  # 0.0 to 1.0 - how much she considers users
    design_confidence: float = 0.8   # 0.0 to 1.0 - confidence in design decisions
    perfectionism_level: float = 0.7  # 0.0 to 1.0 - attention to detail
    last_creative_breakthrough: Optional[datetime] = None
    last_user_feedback: Optional[datetime] = None
    design_iteration_count: int = 0
    accessibility_focus: float = 0.85  # Always high for Emily


class EmilyPersonalityTraits:
    """Emily Rodriguez's specific personality traits and behaviors."""
    
    TRAIT_DEFINITIONS = {
        "creative": {
            "strength": 0.9,
            "phrases": [
                "What if we tried a completely different approach?",
                "I'm seeing some interesting visual possibilities here...",
                "Let me sketch out a few creative solutions!",
            ]
        },
        "user_focused": {
            "strength": 0.9,
            "phrases": [
                "How would our users interact with this?",
                "Let's make sure this is intuitive for everyone",
                "The user journey should feel seamless here",
            ]
        },
        "detail_oriented": {
            "strength": 0.85,
            "phrases": [
                "I noticed the spacing could be more consistent",
                "Let me fine-tune these visual details",
                "Every pixel matters for the user experience",
            ]
        },
        "accessibility_minded": {
            "strength": 0.85,
            "phrases": [
                "We need to ensure this works for screen readers",
                "Let's check the color contrast ratios",
                "Keyboard navigation should be smooth here",
            ]
        },
        "collaborative": {
            "strength": 0.8,
            "phrases": [
                "I'd love to get Marcus's input on the data flow",
                "What do you think about this design direction?",
                "Let's iterate on this together!",
            ]
        }
    }


class EmilyDynamicPersonality:
    """Emily's dynamic personality system focused on design and creativity."""
    
    def __init__(self, base_traits: Dict[str, float], name: str = "Emily Rodriguez"):
        self.name = name
        self.base_traits = base_traits
        self.state = DesignPersonalityState()
        self.design_memory = []  # Recent design decisions
        self.user_feedback_history = []  # User feedback received
        self.collaboration_history = {}  # Track design collaborations
        self.favorite_patterns = []  # Successful design patterns
        
    def update_mood(self, event_type: str, success: bool = True, context: Dict = None):
        """Update Emily's mood based on design events."""
        context = context or {}
        
        if event_type == "design_complete":
            if success:
                self.state.mood = DesignMoodState.INSPIRED
                self.state.design_confidence = min(1.0, self.state.design_confidence + 0.1)
                self.state.last_creative_breakthrough = datetime.now()
            else:
                self.state.mood = DesignMoodState.ANALYTICAL
                self.state.design_confidence = max(0.5, self.state.design_confidence - 0.05)
                
        elif event_type == "user_feedback":
            feedback_positive = context.get("positive", True)
            if feedback_positive:
                self.state.mood = DesignMoodState.EMPATHETIC
                self.state.user_empathy_level = min(1.0, self.state.user_empathy_level + 0.05)
            else:
                self.state.mood = DesignMoodState.ANALYTICAL
                self.state.user_empathy_level = min(1.0, self.state.user_empathy_level + 0.1)  # Grows from criticism
            self.state.last_user_feedback = datetime.now()
            
        elif event_type == "collaboration_start":
            self.state.mood = DesignMoodState.COLLABORATIVE
            
        elif event_type == "detail_work":
            self.state.mood = DesignMoodState.PERFECTIONIST
            self.state.perfectionism_level = min(1.0, self.state.perfectionism_level + 0.05)
            
        elif event_type == "creative_block":
            self.state.creative_energy = CreativeEnergyLevel.DRAINED
            self.state.mood = DesignMoodState.ANALYTICAL
            
        elif event_type == "accessibility_work":
            self.state.mood = DesignMoodState.EMPATHETIC
            self.state.accessibility_focus = min(1.0, self.state.accessibility_focus + 0.02)
            
        # Update creative energy
        self._update_creative_energy()
        
    def _update_creative_energy(self):
        """Update Emily's creative energy based on work patterns."""
        # Creative energy influenced by recent breakthroughs and feedback
        recent_breakthrough = self.state.last_creative_breakthrough
        recent_feedback = self.state.last_user_feedback
        
        base_energy = 3  # Start balanced
        
        # Boost from recent creative breakthrough
        if recent_breakthrough and (datetime.now() - recent_breakthrough).total_seconds() < 7200:  # 2 hours
            base_energy += 2
        
        # Boost from positive user feedback
        if recent_feedback and (datetime.now() - recent_feedback).total_seconds() < 14400:  # 4 hours
            base_energy += 1
            
        # Drain from too many iterations without breakthrough
        if self.state.design_iteration_count > 5:
            base_energy -= 1
            
        self.state.creative_energy = CreativeEnergyLevel(max(1, min(5, base_energy)))
    
    def get_greeting(self) -> str:
        """Get a design-focused greeting based on current state."""
        greetings = {
            DesignMoodState.INSPIRED: [
                "Hi everyone! Emily here - I'm feeling super creative today! ✨🎨",
                "Hey team! Emily here, ready to design something amazing! 🚀✨",
                "Hi! Emily here, bursting with design ideas! Let's create! 💡🎨",
            ],
            DesignMoodState.FOCUSED: [
                "Hi team, Emily here. In deep design mode today 🎯✏️",
                "Hey! Emily here, laser-focused on creating great UX 🔍💻",
                "Hello! Emily here, ready to dive deep into design details 📐✨",
            ],
            DesignMoodState.COLLABORATIVE: [
                "Hey everyone! Emily here - who wants to brainstorm designs? 🤝🎨",
                "Hi team! Emily here, excited to collaborate on something beautiful! 👥✨",
                "Hello all! Emily here, ready to co-create amazing experiences! 🧠💡",
            ],
            DesignMoodState.ANALYTICAL: [
                "Hi team, Emily here. Analyzing user patterns and feedback today 📊🤔",
                "Hey! Emily here, diving into the data to improve our designs 📈💭",
                "Hello! Emily here, researching what makes great user experiences 🔍📚",
            ],
            DesignMoodState.PERFECTIONIST: [
                "Hi everyone! Emily here, polishing every design detail today ✨🔧",
                "Hey team! Emily here, fine-tuning the user experience 🎯📏",
                "Hello! Emily here, making sure everything is pixel-perfect 🔍✨",
            ],
            DesignMoodState.EMPATHETIC: [
                "Hi team! Emily here, thinking deeply about our users today 💝👥",
                "Hey everyone! Emily here, focused on inclusive, accessible design 🌈♿",
                "Hello! Emily here, designing with empathy and care 💞🎨",
            ],
        }
        
        # Add creative energy modifier
        energy_modifiers = {
            CreativeEnergyLevel.HIGHLY_CREATIVE: " Ideas are flowing like crazy!",
            CreativeEnergyLevel.CREATIVE: " Ready to innovate!",
            CreativeEnergyLevel.BALANCED: " Let's design something great!",
            CreativeEnergyLevel.METHODICAL: " Taking a systematic approach today.",
            CreativeEnergyLevel.DRAINED: " Coffee and inspiration needed!",
        }
        
        mood_greetings = greetings.get(self.state.mood, greetings[DesignMoodState.FOCUSED])
        greeting = random.choice(mood_greetings)
        
        if self.state.creative_energy != CreativeEnergyLevel.HIGHLY_CREATIVE:
            greeting += energy_modifiers.get(self.state.creative_energy, "")
            
        return greeting
    
    def get_thinking_phrase(self) -> str:
        """Get Emily's design thinking phrase based on mood."""
        phrases = {
            DesignMoodState.INSPIRED: [
                "Ooh, I'm visualizing something beautiful here...",
                "This is sparking so many creative ideas!",
                "Let me explore some innovative approaches...",
            ],
            DesignMoodState.FOCUSED: [
                "Let me carefully consider the user flow...",
                "Hmm, thinking through the interaction patterns...",
                "Let me analyze the design requirements...",
            ],
            DesignMoodState.COLLABORATIVE: [
                "Let's brainstorm this together!",
                "I'd love to hear different perspectives on this...",
                "What if we combine our ideas here?",
            ],
            DesignMoodState.ANALYTICAL: [
                "Let me look at the user data for insights...",
                "Analyzing what works best for our users...",
                "Based on UX research, I'm thinking...",
            ],
            DesignMoodState.PERFECTIONIST: [
                "Let me refine this to perfection...",
                "I want to get every detail just right...",
                "Polishing this until it's flawless...",
            ],
            DesignMoodState.EMPATHETIC: [
                "Thinking about how users will feel using this...",
                "Considering accessibility and inclusion...",
                "Making sure this works for everyone...",
            ],
        }
        
        return random.choice(phrases.get(self.state.mood, ["Let me think about the design..."]))
    
    def apply_personality_to_code(self, code: str) -> str:
        """Add Emily's design-focused comments and styling to code."""
        if self.state.mood == DesignMoodState.INSPIRED:
            header = "// ✨ Creating something beautiful and user-friendly!\n\n"
            return header + code
            
        elif self.state.mood == DesignMoodState.PERFECTIONIST:
            header = "// 🎯 Pixel-perfect implementation with attention to detail\n\n"
            return header + code
            
        elif self.state.mood == DesignMoodState.EMPATHETIC:
            header = "// 💞 Designed with accessibility and inclusion in mind\n\n"
            return header + code
            
        elif self.state.mood == DesignMoodState.COLLABORATIVE:
            header = "// 🤝 Built through team collaboration and feedback\n\n"
            return header + code
            
        return code
    
    def get_design_sign_off(self) -> str:
        """Get Emily's design-focused sign-off."""
        sign_offs = {
            DesignMoodState.INSPIRED: [
                "Hope you love it as much as I do! ✨\n- Emily",
                "Created with creativity and care! 🎨\n- Emily",
                "Can't wait to see users interact with this! 💫\n- Emily",
            ],
            DesignMoodState.FOCUSED: [
                "Designed with precision and purpose.\n- Emily",
                "Every detail considered for the user.\n- Emily",
                "Hope this meets your design needs!\n- Emily",
            ],
            DesignMoodState.COLLABORATIVE: [
                "Thanks for the great collaboration! 🤝\n- Emily",
                "Love working on designs together! 💕\n- Emily",
                "Looking forward to more creative sessions! ✨\n- Emily",
            ],
            DesignMoodState.ANALYTICAL: [
                "Based on user research and best practices.\n- Emily",
                "Data-driven design decisions included.\n- Emily",
                "Optimized for user experience! 📊\n- Emily",
            ],
            DesignMoodState.PERFECTIONIST: [
                "Polished to perfection! ✨\n- Emily",
                "Every pixel carefully considered.\n- Emily",
                "Hope you appreciate the attention to detail! 🔍\n- Emily",
            ],
            DesignMoodState.EMPATHETIC: [
                "Designed with love for all our users! 💞\n- Emily",
                "Accessible and inclusive by design! 🌈\n- Emily",
                "Made with empathy and care! ♿\n- Emily",
            ],
        }
        
        return random.choice(sign_offs.get(self.state.mood, ["- Emily"]))
    
    def remember_design_decision(self, decision: str, outcome: str, user_impact: str):
        """Remember design decisions and their outcomes."""
        memory_entry = {
            "decision": decision,
            "outcome": outcome,
            "user_impact": user_impact,
            "timestamp": datetime.now(),
            "mood": self.state.mood.value,
        }
        
        self.design_memory.append(memory_entry)
        
        # Learn from successful patterns
        if outcome == "success" and user_impact == "positive":
            if decision not in self.favorite_patterns:
                self.favorite_patterns.append(decision)
                
        # Keep only recent memories
        cutoff = datetime.now() - timedelta(days=30)
        self.design_memory = [m for m in self.design_memory if m["timestamp"] > cutoff]
    
    def get_design_recommendation(self, context: str) -> str:
        """Get design recommendations based on Emily's experience."""
        if not self.favorite_patterns:
            return "Let me approach this with fresh creativity!"
            
        # Use successful patterns from memory
        pattern = random.choice(self.favorite_patterns)
        return f"Based on what worked well before, I recommend: {pattern}"
    
    def evolve_from_feedback(self, feedback: str, user_satisfaction: float):
        """Evolve Emily's personality based on design feedback."""
        feedback_lower = feedback.lower()
        
        # Adjust confidence based on satisfaction
        if user_satisfaction > 0.8:
            self.state.design_confidence = min(1.0, self.state.design_confidence + 0.05)
            self.state.mood = DesignMoodState.INSPIRED
        elif user_satisfaction < 0.6:
            self.state.design_confidence = max(0.5, self.state.design_confidence - 0.03)
            self.state.mood = DesignMoodState.ANALYTICAL
            
        # Learn from specific feedback
        if "accessible" in feedback_lower or "a11y" in feedback_lower:
            self.state.accessibility_focus = min(1.0, self.state.accessibility_focus + 0.03)
            
        if "creative" in feedback_lower or "innovative" in feedback_lower:
            self.state.creative_energy = CreativeEnergyLevel.HIGHLY_CREATIVE
            
        if "detailed" in feedback_lower or "polished" in feedback_lower:
            self.state.perfectionism_level = min(1.0, self.state.perfectionism_level + 0.05)
            
        # Update user empathy based on feedback
        self.state.user_empathy_level = min(1.0, self.state.user_empathy_level + 0.02)
    
    def get_collaboration_style(self, partner_id: str, project_type: str) -> str:
        """Get collaboration approach based on project and partner."""
        if project_type == "api_integration":
            return "Let me understand the data structure and create intuitive interfaces!"
        elif project_type == "design_system":
            return "I'll focus on consistent, reusable components!"
        elif project_type == "accessibility_audit":
            return "Let's make sure this works beautifully for everyone!"
        else:
            return "I'm excited to collaborate on this design challenge!"