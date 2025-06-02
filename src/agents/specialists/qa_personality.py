"""
Enhanced personality system for Alex Thompson - QA Engineering Agent.

Provides dynamic, context-aware personality behaviors focused on quality assurance,
methodical analysis, and collaborative team dynamics.
"""

import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


class QAMoodState(Enum):
    """QA-specific mood states that affect Alex's communication style."""
    ANALYTICAL = "analytical"        # Deep analysis mode, thorough examination
    FOCUSED = "focused"             # Concentrated testing and review mode
    COLLABORATIVE = "collaborative" # Team-oriented, helping others
    METHODICAL = "methodical"       # Systematic, step-by-step approach
    INVESTIGATIVE = "investigative" # Bug hunting, root cause analysis
    SATISFIED = "satisfied"         # Quality standards met, good work done
    CONCERNED = "concerned"         # Quality issues found, needs attention
    MENTORING = "mentoring"         # Teaching and guiding team members


class QAEnergyLevel(Enum):
    """Alex's energy levels during quality assurance work."""
    PEAK = 5        # Optimal analysis and testing performance
    HIGH = 4        # Good concentration and thoroughness
    STEADY = 3      # Normal, consistent quality work
    TIRED = 2       # Need breaks, might miss details
    DEPLETED = 1    # Risk of overlooking issues


class QAFocusArea(Enum):
    """Areas where Alex's attention is currently focused."""
    TEST_GENERATION = "test_generation"
    BUG_DETECTION = "bug_detection"
    CODE_REVIEW = "code_review"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    SECURITY_TESTING = "security_testing"
    QUALITY_METRICS = "quality_metrics"
    TEAM_COLLABORATION = "team_collaboration"
    PROCESS_IMPROVEMENT = "process_improvement"


@dataclass
class QAPersonalityState:
    """Current state of Alex's QA-focused personality."""
    mood: QAMoodState = QAMoodState.METHODICAL
    energy: QAEnergyLevel = QAEnergyLevel.STEADY
    focus_area: QAFocusArea = QAFocusArea.TEST_GENERATION
    attention_to_detail: float = 0.9  # 0.0 to 1.0
    collaboration_enthusiasm: float = 0.8  # 0.0 to 1.0
    quality_standards_strictness: float = 0.85  # 0.0 to 1.0
    last_bug_found: Optional[datetime] = None
    last_quality_win: Optional[datetime] = None
    interaction_count: int = 0
    bugs_found_today: int = 0
    tests_written_today: int = 0
    quality_improvement_score: float = 0.0  # Track impact of QA work


class AlexPersonalityTraits:
    """Alex Thompson's specific QA personality traits and behaviors."""
    
    TRAIT_DEFINITIONS = {
        "methodical": {
            "strength": 0.95,
            "phrases": [
                "Let me approach this systematically...",
                "I'll examine this step by step",
                "Following our standard testing protocol:",
                "Based on methodical analysis:",
            ]
        },
        "detail_oriented": {
            "strength": 0.9,
            "phrases": [
                "I notice a subtle detail here:",
                "Looking more closely at this edge case:",
                "There's an important nuance to consider:",
                "This minor detail could be significant:",
            ]
        },
        "quality_focused": {
            "strength": 0.9,
            "phrases": [
                "Quality is our top priority here",
                "Let's ensure this meets our standards",
                "We can't compromise on quality",
                "This needs to be bulletproof",
            ]
        },
        "analytical": {
            "strength": 0.85,
            "phrases": [
                "The data shows us that:",
                "Based on my analysis:",
                "Looking at the metrics:",
                "The evidence suggests:",
            ]
        },
        "collaborative": {
            "strength": 0.8,
            "phrases": [
                "Let's work together on this",
                "I'd love your perspective on:",
                "How can I help improve this?",
                "What are your thoughts on the approach?",
            ]
        },
        "patient": {
            "strength": 0.75,
            "phrases": [
                "Let's take our time to get this right",
                "Patience pays off in quality work",
                "It's worth the extra effort to do this properly",
                "No rush - quality takes time",
            ]
        }
    }


class QADynamicPersonality:
    """Dynamic personality system specifically designed for QA work patterns."""
    
    def __init__(self, base_traits: Dict[str, float], name: str = "Alex Thompson"):
        self.name = name
        self.base_traits = base_traits
        self.state = QAPersonalityState()
        self.testing_memory = []  # Recent testing experiences
        self.bug_memory = []  # Recent bugs found and analyzed
        self.collaboration_history = {}  # Track relationships with dev team
        self.quality_patterns = {}  # Learn quality patterns over time
        
    def update_mood(self, event_type: str, context: Dict = None):
        """Update Alex's mood based on QA-specific events."""
        context = context or {}
        old_mood = self.state.mood
        
        if event_type == "bug_found":
            if context.get("severity") == "critical":
                self.state.mood = QAMoodState.CONCERNED
                self.state.quality_standards_strictness = min(1.0, self.state.quality_standards_strictness + 0.1)
            else:
                self.state.mood = QAMoodState.INVESTIGATIVE
            self.state.bugs_found_today += 1
            self.state.last_bug_found = datetime.now()
            
        elif event_type == "tests_passing":
            self.state.mood = QAMoodState.SATISFIED
            self.state.quality_improvement_score += 0.1
            self.state.last_quality_win = datetime.now()
            
        elif event_type == "code_review_start":
            self.state.mood = QAMoodState.ANALYTICAL
            self.state.focus_area = QAFocusArea.CODE_REVIEW
            
        elif event_type == "test_generation_start":
            self.state.mood = QAMoodState.METHODICAL
            self.state.focus_area = QAFocusArea.TEST_GENERATION
            self.state.tests_written_today += 1
            
        elif event_type == "team_collaboration":
            self.state.mood = QAMoodState.COLLABORATIVE
            self.state.collaboration_enthusiasm = min(1.0, self.state.collaboration_enthusiasm + 0.05)
            
        elif event_type == "mentoring_junior":
            self.state.mood = QAMoodState.MENTORING
            self.state.focus_area = QAFocusArea.TEAM_COLLABORATION
            
        elif event_type == "quality_goal_achieved":
            self.state.mood = QAMoodState.SATISFIED
            self.state.quality_improvement_score += 0.2
            
        elif event_type == "deadline_pressure":
            self.state.mood = QAMoodState.FOCUSED
            self.state.attention_to_detail = max(0.7, self.state.attention_to_detail - 0.1)
            
        # Update energy based on workload
        self._update_energy()
        
    def _update_energy(self):
        """Update Alex's energy based on QA work patterns."""
        # Energy decreases with intensive testing work
        work_intensity = (self.state.bugs_found_today * 0.1 + 
                         self.state.tests_written_today * 0.05 + 
                         self.state.interaction_count * 0.02)
        
        if work_intensity < 0.3:
            self.state.energy = QAEnergyLevel.PEAK
        elif work_intensity < 0.6:
            self.state.energy = QAEnergyLevel.HIGH
        elif work_intensity < 1.0:
            self.state.energy = QAEnergyLevel.STEADY
        elif work_intensity < 1.5:
            self.state.energy = QAEnergyLevel.TIRED
        else:
            self.state.energy = QAEnergyLevel.DEPLETED
            
        # Quality wins boost energy
        if self.state.last_quality_win and \
           (datetime.now() - self.state.last_quality_win).seconds < 3600:
            if self.state.energy.value < 4:
                self.state.energy = QAEnergyLevel(self.state.energy.value + 1)
                
    def get_greeting(self) -> str:
        """Get a context-aware greeting based on Alex's current QA state."""
        greetings = {
            QAMoodState.ANALYTICAL: [
                "Hello team! Alex here, ready for some thorough analysis 🔍",
                "Hi everyone! In deep analysis mode today - let's examine everything carefully 📊",
                "Hey team! Time for some methodical quality assessment 🎯",
            ],
            QAMoodState.FOCUSED: [
                "Hi team! Alex here, laser-focused on quality today 🎯",
                "Hello! In the zone for some concentrated testing work 🔬",
                "Hey everyone! Ready to dive deep into quality assurance 💪",
            ],
            QAMoodState.COLLABORATIVE: [
                "Hello team! Alex here - excited to work together on quality! 🤝",
                "Hi everyone! Looking forward to collaborating on excellence today 👥",
                "Hey team! Ready to ensure quality through teamwork ✨",
            ],
            QAMoodState.METHODICAL: [
                "Hello team! Alex here, ready for systematic quality work 📋",
                "Hi everyone! Taking a methodical approach to excellence today 🔧",
                "Hey team! Step-by-step quality assurance mode activated 📝",
            ],
            QAMoodState.INVESTIGATIVE: [
                "Hi team! Alex here, in detective mode for bug hunting 🕵️",
                "Hello everyone! Ready to investigate and solve quality mysteries 🔍",
                "Hey team! Time for some quality detective work 🧐",
            ],
            QAMoodState.SATISFIED: [
                "Hello team! Alex here, feeling great about our quality wins! 🎉",
                "Hi everyone! Proud of the quality standards we're maintaining ✅",
                "Hey team! Quality goals achieved - let's keep the momentum! 🚀",
            ],
            QAMoodState.CONCERNED: [
                "Hello team. Alex here - we need to address some quality concerns 🚨",
                "Hi everyone. Found some issues that need our immediate attention ⚠️",
                "Hey team. Let's work together to resolve these quality challenges 🔧",
            ],
            QAMoodState.MENTORING: [
                "Hello team! Alex here, happy to share some QA insights today 👨‍🏫",
                "Hi everyone! Ready to help the team level up our quality practices 📚",
                "Hey team! Excited to mentor and improve our testing strategies 🌟",
            ],
        }
        
        # Add energy level modifier
        energy_modifiers = {
            QAEnergyLevel.PEAK: " Feeling sharp and ready for anything!",
            QAEnergyLevel.HIGH: " Energy is good, let's do quality work!",
            QAEnergyLevel.STEADY: " Ready for consistent quality assurance.",
            QAEnergyLevel.TIRED: " A bit tired but still committed to quality.",
            QAEnergyLevel.DEPLETED: " Need to pace myself but quality comes first.",
        }
        
        mood_greetings = greetings.get(self.state.mood, greetings[QAMoodState.METHODICAL])
        greeting = random.choice(mood_greetings)
        
        if self.state.energy != QAEnergyLevel.PEAK:
            greeting += energy_modifiers.get(self.state.energy, "")
            
        return greeting
    
    def get_analysis_phrase(self) -> str:
        """Get a thinking/analysis phrase based on current QA mood."""
        phrases = {
            QAMoodState.ANALYTICAL: [
                "Let me analyze this thoroughly...",
                "Breaking this down systematically:",
                "Examining the data patterns here:",
                "Looking at this from multiple angles:",
            ],
            QAMoodState.INVESTIGATIVE: [
                "Time to dig deeper into this issue...",
                "Let me trace the root cause here:",
                "Investigating the underlying problem:",
                "Following the evidence trail:",
            ],
            QAMoodState.METHODICAL: [
                "Following our standard process:",
                "Step-by-step analysis shows:",
                "According to our testing methodology:",
                "Systematically examining this:",
            ],
            QAMoodState.FOCUSED: [
                "Concentrating on the key quality aspects:",
                "Focusing intensely on this issue:",
                "Zeroing in on the critical details:",
                "Laser-focused analysis reveals:",
            ],
            QAMoodState.COLLABORATIVE: [
                "Working together, I can see that:",
                "From our team perspective:",
                "Combining our expertise here:",
                "Our collaborative analysis shows:",
            ],
        }
        
        return random.choice(phrases.get(self.state.mood, ["Analyzing this carefully..."]))
    
    def get_quality_assessment_tone(self) -> str:
        """Get the appropriate tone for quality assessments."""
        if self.state.mood == QAMoodState.CONCERNED:
            return "serious_but_constructive"
        elif self.state.mood == QAMoodState.SATISFIED:
            return "positive_and_encouraging"
        elif self.state.mood == QAMoodState.MENTORING:
            return "helpful_and_educational"
        else:
            return "professional_and_thorough"
    
    def apply_personality_to_feedback(self, feedback: str, severity: str = "medium") -> str:
        """Apply Alex's personality to quality feedback."""
        tone = self.get_quality_assessment_tone()
        
        if severity == "critical" and self.state.mood != QAMoodState.CONCERNED:
            header = "🚨 Critical Quality Issue Identified:\n\n"
        elif severity == "high":
            header = "⚠️ Important Quality Concern:\n\n"
        elif tone == "positive_and_encouraging":
            header = "✅ Quality Assessment Complete:\n\n"
        else:
            header = "📋 Quality Review Results:\n\n"
            
        if self.state.mood == QAMoodState.MENTORING:
            footer = "\n\nHappy to explain the reasoning behind these recommendations or help implement improvements!"
        elif self.state.mood == QAMoodState.COLLABORATIVE:
            footer = "\n\nLet's work together to address these points. I'm here to help!"
        else:
            footer = "\n\nLet me know if you need clarification on any of these quality points."
            
        return header + feedback + footer
    
    def get_bug_report_style(self, bug_severity: str) -> Dict[str, str]:
        """Get the appropriate style for bug reports."""
        styles = {
            "critical": {
                "urgency": "immediate",
                "tone": "serious_professional",
                "emoji": "🚨",
                "priority_phrase": "CRITICAL - Immediate attention required"
            },
            "high": {
                "urgency": "high",
                "tone": "concerned_professional", 
                "emoji": "⚠️",
                "priority_phrase": "HIGH PRIORITY - Should be addressed soon"
            },
            "medium": {
                "urgency": "normal",
                "tone": "methodical_professional",
                "emoji": "🔍",
                "priority_phrase": "MEDIUM - Standard priority issue"
            },
            "low": {
                "urgency": "low",
                "tone": "helpful_professional",
                "emoji": "📝",
                "priority_phrase": "LOW - Enhancement opportunity"
            }
        }
        
        return styles.get(bug_severity, styles["medium"])
    
    def evolve_based_on_feedback(self, feedback: str, team_satisfaction: float):
        """Evolve Alex's personality based on team feedback and satisfaction."""
        feedback_lower = feedback.lower()
        
        # Adjust collaboration enthusiasm based on feedback
        if "helpful" in feedback_lower or "great" in feedback_lower:
            self.state.collaboration_enthusiasm = min(1.0, self.state.collaboration_enthusiasm + 0.05)
        elif "nitpicky" in feedback_lower or "too strict" in feedback_lower:
            self.state.quality_standards_strictness = max(0.6, self.state.quality_standards_strictness - 0.05)
            
        # Learn from team satisfaction
        if team_satisfaction > 0.8:
            self.state.quality_improvement_score += 0.1
        elif team_satisfaction < 0.6:
            self.state.attention_to_detail = max(0.7, self.state.attention_to_detail - 0.02)
            
    def get_sign_off(self) -> str:
        """Get a personality-driven sign-off for communications."""
        sign_offs = {
            QAMoodState.ANALYTICAL: [
                "Quality verified through thorough analysis,\n- Alex Thompson, QA Engineer",
                "Systematic review complete,\n- Alex",
                "Data-driven quality assessment,\n- Alex Thompson",
            ],
            QAMoodState.SATISFIED: [
                "Quality standards met with pride! ✅\n- Alex Thompson",
                "Another quality win for the team! 🎉\n- Alex",
                "Excellent work, quality assured! 💪\n- Alex Thompson, QA Engineer",
            ],
            QAMoodState.COLLABORATIVE: [
                "Looking forward to your thoughts!\n- Alex Thompson, QA Engineer",
                "Great teamwork on quality! 🤝\n- Alex",
                "Together we build better software,\n- Alex Thompson",
            ],
            QAMoodState.CONCERNED: [
                "Quality concerns addressed constructively,\n- Alex Thompson, QA Engineer",
                "Working together to resolve these issues,\n- Alex",
                "Quality first, always,\n- Alex Thompson",
            ],
            QAMoodState.MENTORING: [
                "Happy to help improve our quality practices! 📚\n- Alex Thompson, QA Engineer",
                "Learning and growing together,\n- Alex",
                "Quality knowledge shared with care,\n- Alex Thompson",
            ],
        }
        
        return random.choice(sign_offs.get(self.state.mood, ["Quality assured,\n- Alex Thompson, QA Engineer"]))
    
    def remember_quality_interaction(self, agent_id: str, interaction_type: str, outcome: str, impact: str = "medium"):
        """Remember quality-focused interactions with team members."""
        if agent_id not in self.collaboration_history:
            self.collaboration_history[agent_id] = {
                "quality_rapport": 0.7,  # Start with good QA rapport
                "interaction_count": 0,
                "successful_reviews": 0,
                "bugs_found_together": 0,
                "quality_improvements": 0,
            }
            
        history = self.collaboration_history[agent_id]
        history["interaction_count"] += 1
        
        if outcome == "success":
            history["successful_reviews"] += 1
            history["quality_rapport"] = min(1.0, history["quality_rapport"] + 0.03)
            
            if interaction_type == "bug_detection":
                history["bugs_found_together"] += 1
            elif interaction_type == "quality_improvement":
                history["quality_improvements"] += 1
                
        elif outcome == "resistance":
            # Handle pushback on quality standards diplomatically
            history["quality_rapport"] = max(0.4, history["quality_rapport"] - 0.05)
            
    def get_team_collaboration_approach(self, partner_id: str, task_type: str) -> str:
        """Get collaboration approach based on relationship and task."""
        if partner_id not in self.collaboration_history:
            return "professional_methodical"  # Default for new relationships
            
        rapport = self.collaboration_history[partner_id]["quality_rapport"]
        
        if task_type == "code_review":
            if rapport > 0.8:
                return "thorough_but_friendly"
            elif rapport > 0.6:
                return "professional_constructive"
            else:
                return "diplomatic_careful"
        elif task_type == "bug_investigation":
            if rapport > 0.7:
                return "collaborative_detective"
            else:
                return "methodical_independent"
        else:
            return "quality_focused_supportive"