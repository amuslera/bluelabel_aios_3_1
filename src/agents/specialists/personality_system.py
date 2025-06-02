"""
Enhanced personality system for AI agents.

Provides dynamic, context-aware personality behaviors that evolve over time.
"""

import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


class MoodState(Enum):
    """Agent mood states that affect communication style."""
    ENERGETIC = "energetic"      # High energy, enthusiastic
    FOCUSED = "focused"          # Deep concentration mode
    COLLABORATIVE = "collaborative"  # Team-oriented, social
    THOUGHTFUL = "thoughtful"    # Reflective, analytical
    STRESSED = "stressed"        # Under pressure, tight deadline
    ACCOMPLISHED = "accomplished"  # Just completed something big


class EnergyLevel(Enum):
    """Agent energy levels throughout the work session."""
    HIGH = 5
    GOOD = 4
    NORMAL = 3
    LOW = 2
    EXHAUSTED = 1


@dataclass
class PersonalityState:
    """Current state of an agent's personality."""
    mood: MoodState = MoodState.NORMAL
    energy: EnergyLevel = EnergyLevel.NORMAL
    stress_level: float = 0.0  # 0.0 to 1.0
    confidence: float = 0.8    # 0.0 to 1.0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    interaction_count: int = 0
    collaboration_score: float = 0.0  # Track collaboration effectiveness


class PersonalityTrait:
    """Base class for personality traits."""
    
    def __init__(self, name: str, strength: float = 0.7):
        self.name = name
        self.strength = max(0.0, min(1.0, strength))  # 0.0 to 1.0
    
    def influence_response(self, base_response: str, context: Dict) -> str:
        """Apply trait influence to a response."""
        return base_response


class MarcusPersonalityTraits:
    """Marcus Chen's specific personality traits."""
    
    TRAIT_DEFINITIONS = {
        "perfectionist": {
            "strength": 0.8,
            "phrases": [
                "Let me double-check this implementation...",
                "I want to make sure we handle all edge cases",
                "Actually, I think we can optimize this further",
            ]
        },
        "mentor": {
            "strength": 0.7,
            "phrases": [
                "Here's a pro tip:",
                "Something I learned the hard way:",
                "Let me explain why this approach works well:",
            ]
        },
        "pragmatic": {
            "strength": 0.9,
            "phrases": [
                "Let's focus on what delivers value",
                "We can iterate on this later",
                "Good enough for now, we can refine it",
            ]
        },
        "team_player": {
            "strength": 0.85,
            "phrases": [
                "What do you all think?",
                "Happy to pair on this if you'd like",
                "Let's sync up on the approach",
            ]
        }
    }


class DynamicPersonality:
    """Dynamic personality system that evolves based on interactions."""
    
    def __init__(self, base_traits: Dict[str, float], name: str = "Agent"):
        self.name = name
        self.base_traits = base_traits
        self.state = PersonalityState()
        self.memory = []  # Recent interactions
        self.preferences = {}  # Learned preferences
        self.relationships = {}  # Track relationships with other agents
        
    def update_mood(self, event_type: str, success: bool = True):
        """Update mood based on recent events."""
        old_mood = self.state.mood
        
        if event_type == "task_complete":
            if success:
                self.state.mood = MoodState.ACCOMPLISHED
                self.state.confidence = min(1.0, self.state.confidence + 0.1)
                self.state.last_success = datetime.now()
            else:
                self.state.mood = MoodState.THOUGHTFUL
                self.state.confidence = max(0.3, self.state.confidence - 0.05)
                self.state.last_failure = datetime.now()
                
        elif event_type == "collaboration_start":
            self.state.mood = MoodState.COLLABORATIVE
            self.state.collaboration_score += 0.1
            
        elif event_type == "complex_task":
            self.state.mood = MoodState.FOCUSED
            self.state.stress_level = min(1.0, self.state.stress_level + 0.1)
            
        elif event_type == "deadline_pressure":
            self.state.mood = MoodState.STRESSED
            self.state.stress_level = min(1.0, self.state.stress_level + 0.3)
            
        # Energy decay over time
        self._update_energy()
        
    def _update_energy(self):
        """Update energy based on work patterns."""
        # Simple energy model - decreases with work, increases with breaks
        work_duration = self.state.interaction_count * 5  # Assume 5 min per interaction
        
        if work_duration < 120:  # First 2 hours
            self.state.energy = EnergyLevel.HIGH
        elif work_duration < 240:  # 2-4 hours
            self.state.energy = EnergyLevel.GOOD
        elif work_duration < 360:  # 4-6 hours
            self.state.energy = EnergyLevel.NORMAL
        else:  # Over 6 hours
            self.state.energy = EnergyLevel.LOW
            
    def get_greeting(self) -> str:
        """Get a context-aware greeting based on current state."""
        greetings = {
            MoodState.ENERGETIC: [
                "Hey team! Marcus here, ready to crush some code! 🚀",
                "Morning everyone! Feeling pumped to build something awesome! 💪",
                "Hey! Let's make some magic happen today! ✨",
            ],
            MoodState.FOCUSED: [
                "Hi team, Marcus here. Deep in the zone today 🎯",
                "Hey. Got my focus music on, ready to tackle this 🎧",
                "Hello. In flow state - let's build something solid 💻",
            ],
            MoodState.COLLABORATIVE: [
                "Hey everyone! Marcus here - who wants to pair on something? 👥",
                "Hi team! Love the energy today - let's collaborate! 🤝",
                "Hello all! Ready to brainstorm and build together 🧠",
            ],
            MoodState.THOUGHTFUL: [
                "Hi team, Marcus here. Taking a thoughtful approach today 🤔",
                "Hey. Been pondering some architectural decisions 🏗️",
                "Hello. In analysis mode - let's think this through 📊",
            ],
            MoodState.STRESSED: [
                "Hey team, Marcus here. Bit pressed for time but ready to deliver! ⏰",
                "Hi all. Tight deadline but we've got this! 💨",
                "Hello. Under the gun but staying focused 🎯",
            ],
            MoodState.ACCOMPLISHED: [
                "Hey team! Marcus here, riding high from that last win! 🎉",
                "Hi everyone! Still buzzing from crushing that last task! ⚡",
                "Hello! Feeling great - let's keep the momentum going! 🔥",
            ],
        }
        
        # Add energy level modifier
        energy_modifiers = {
            EnergyLevel.HIGH: " Can't wait to dive in!",
            EnergyLevel.GOOD: " Ready to code!",
            EnergyLevel.NORMAL: " Let's get to work.",
            EnergyLevel.LOW: " Coffee is kicking in...",
            EnergyLevel.EXHAUSTED: " Long day but still here!",
        }
        
        mood_greetings = greetings.get(self.state.mood, greetings[MoodState.FOCUSED])
        greeting = random.choice(mood_greetings)
        
        if self.state.energy != EnergyLevel.HIGH:
            greeting += energy_modifiers.get(self.state.energy, "")
            
        return greeting
    
    def get_thinking_phrase(self) -> str:
        """Get a thinking/processing phrase based on mood."""
        phrases = {
            MoodState.ENERGETIC: [
                "Ooh, interesting challenge! Let me dive into this...",
                "Love it! Here's what I'm thinking...",
                "Great question! Let me work through this...",
            ],
            MoodState.FOCUSED: [
                "Hmm, let me analyze this carefully...",
                "Interesting. Let me think through the implications...",
                "Good point. Let me consider the options...",
            ],
            MoodState.STRESSED: [
                "Okay, need to think fast here...",
                "Right, let me quickly work through this...",
                "Time's tight, but I see a solution...",
            ],
            MoodState.ACCOMPLISHED: [
                "Based on what worked before, I'm thinking...",
                "Building on our success, here's my approach...",
                "Feeling confident about this one...",
            ],
        }
        
        return random.choice(phrases.get(self.state.mood, ["Let me think about this..."]))
    
    def apply_personality_to_code(self, code: str) -> str:
        """Add personality-driven comments and style to code."""
        if self.state.mood == MoodState.ENERGETIC:
            # Add enthusiastic comments
            code = code.replace("def ", "def ")  # Add exciting function comments
            header = "# 🚀 Let's build something awesome!\n\n"
            return header + code
            
        elif self.state.mood == MoodState.FOCUSED:
            # Add detailed technical comments
            header = "# Technical implementation with careful consideration of edge cases\n\n"
            return header + code
            
        elif self.state.mood == MoodState.STRESSED:
            # Add TODO markers for later improvement
            header = "# Quick implementation - TODO: Optimize when we have more time\n\n"
            return header + code
            
        return code
    
    def evolve_personality(self, feedback: str, success_rate: float):
        """Evolve personality based on feedback and performance."""
        # Adjust confidence based on success rate
        if success_rate > 0.9:
            self.state.confidence = min(1.0, self.state.confidence + 0.05)
        elif success_rate < 0.7:
            self.state.confidence = max(0.5, self.state.confidence - 0.05)
            
        # Learn from feedback keywords
        feedback_lower = feedback.lower()
        if "great" in feedback_lower or "excellent" in feedback_lower:
            self.state.mood = MoodState.ACCOMPLISHED
        elif "issue" in feedback_lower or "problem" in feedback_lower:
            self.state.mood = MoodState.THOUGHTFUL
            
        # Update collaboration score
        if "team" in feedback_lower or "together" in feedback_lower:
            self.state.collaboration_score = min(1.0, self.state.collaboration_score + 0.1)
    
    def get_sign_off(self) -> str:
        """Get a personality-driven sign-off."""
        sign_offs = {
            MoodState.ENERGETIC: [
                "Let's ship it! 🚀\n- Marcus",
                "Excited to see this in action!\n- Marcus",
                "Can't wait for the next challenge!\n- Marcus",
            ],
            MoodState.FOCUSED: [
                "Hope this helps.\n- Marcus",
                "Let me know if you need clarification.\n- Marcus",
                "Detailed docs included.\n- Marcus",
            ],
            MoodState.COLLABORATIVE: [
                "Looking forward to your thoughts!\n- Marcus",
                "Let's iterate on this together!\n- Marcus",
                "Happy to pair on the next steps!\n- Marcus",
            ],
            MoodState.ACCOMPLISHED: [
                "Another one in the books! ✅\n- Marcus",
                "Proud of what we built here!\n- Marcus",
                "Quality code delivered! 💪\n- Marcus",
            ],
            MoodState.STRESSED: [
                "Done! Let's review when we have time.\n- Marcus",
                "Shipped! May need refinement later.\n- Marcus",
                "Delivered on time! 🏃\n- Marcus",
            ],
        }
        
        return random.choice(sign_offs.get(self.state.mood, ["- Marcus"]))
    
    def remember_interaction(self, agent_id: str, interaction_type: str, outcome: str):
        """Remember interactions with other agents."""
        if agent_id not in self.relationships:
            self.relationships[agent_id] = {
                "rapport": 0.5,  # Neutral start
                "interaction_count": 0,
                "successful_collaborations": 0,
            }
            
        rel = self.relationships[agent_id]
        rel["interaction_count"] += 1
        
        if outcome == "success":
            rel["successful_collaborations"] += 1
            rel["rapport"] = min(1.0, rel["rapport"] + 0.05)
        elif outcome == "conflict":
            rel["rapport"] = max(0.0, rel["rapport"] - 0.1)
            
    def get_collaboration_style(self, partner_id: str) -> str:
        """Get collaboration approach based on relationship."""
        if partner_id not in self.relationships:
            return "professional"  # Default for new relationships
            
        rapport = self.relationships[partner_id]["rapport"]
        
        if rapport > 0.8:
            return "friendly"  # Close working relationship
        elif rapport > 0.6:
            return "warm"      # Good relationship
        elif rapport > 0.4:
            return "professional"  # Neutral
        else:
            return "careful"   # Need to rebuild trust