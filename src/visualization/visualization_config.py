"""
Visualization Configuration System

Provides configuration options for the agent visualization system,
including themes, animation speeds, and display preferences.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class VisualizationTheme(Enum):
    """Available visualization themes"""
    CYBERPUNK = "cyberpunk"      # Neon colors, high contrast
    PROFESSIONAL = "professional"  # Muted colors, clean
    PLAYFUL = "playful"          # Bright colors, fun icons
    MATRIX = "matrix"            # Green on black, terminal style
    PASTEL = "pastel"            # Soft, calming colors


class AnimationStyle(Enum):
    """Animation styles for transitions"""
    SMOOTH = "smooth"            # Smooth transitions
    INSTANT = "instant"          # No transitions
    TYPEWRITER = "typewriter"    # Text appears character by character
    FADE = "fade"               # Fade in/out effects


@dataclass
class AgentTheme:
    """Theme configuration for an individual agent"""
    primary_color: str
    secondary_color: str
    accent_color: str
    icon: str
    activity_icons: Dict[str, str] = field(default_factory=dict)
    mood_colors: Dict[str, str] = field(default_factory=dict)


@dataclass
class SoundEffects:
    """Sound effect configuration (for future enhancement)"""
    enabled: bool = False
    volume: float = 0.5
    typing_sound: str = "keyboard_click"
    message_sound: str = "notification"
    success_sound: str = "success_chime"
    error_sound: str = "error_beep"
    deployment_sound: str = "rocket_launch"


@dataclass
class VisualizationConfig:
    """Main visualization configuration"""
    
    # Display settings
    theme: VisualizationTheme = VisualizationTheme.CYBERPUNK
    animation_style: AnimationStyle = AnimationStyle.SMOOTH
    show_timestamps: bool = True
    show_agent_moods: bool = True
    show_code_syntax_highlighting: bool = True
    max_message_history: int = 10
    max_code_lines_shown: int = 20
    
    # Theatrical pacing
    default_speed_preset: str = "normal"
    enable_auto_slowdown: bool = True  # Automatically slow down for important events
    important_event_multiplier: float = 0.5  # Speed multiplier for important events
    
    # Layout preferences
    layout_style: str = "grid"  # grid, vertical, horizontal, focus
    code_panel_size_ratio: float = 0.4
    show_metrics_panel: bool = True
    show_timeline: bool = True
    
    # Agent-specific themes
    agent_themes: Dict[str, AgentTheme] = field(default_factory=dict)
    
    # Visual effects
    enable_particle_effects: bool = True
    enable_glow_effects: bool = True
    enable_transition_animations: bool = True
    
    # Accessibility
    high_contrast_mode: bool = False
    colorblind_mode: Optional[str] = None  # None, "protanopia", "deuteranopia", "tritanopia"
    font_size: str = "medium"  # small, medium, large
    
    # Sound effects (future enhancement)
    sound_effects: SoundEffects = field(default_factory=SoundEffects)
    
    def __post_init__(self):
        """Initialize default agent themes based on selected theme"""
        if not self.agent_themes:
            self.agent_themes = self._get_default_agent_themes()
            
    def _get_default_agent_themes(self) -> Dict[str, AgentTheme]:
        """Get default agent themes based on visualization theme"""
        if self.theme == VisualizationTheme.CYBERPUNK:
            return {
                "Marcus Chen": AgentTheme(
                    primary_color="cyan",
                    secondary_color="bright_cyan",
                    accent_color="blue",
                    icon="⚙️",
                    activity_icons={
                        "coding": "⌨️",
                        "debugging": "🔧",
                        "thinking": "🧠"
                    },
                    mood_colors={
                        "energetic": "bright_cyan",
                        "focused": "cyan",
                        "stressed": "red"
                    }
                ),
                "Emily Rodriguez": AgentTheme(
                    primary_color="magenta",
                    secondary_color="bright_magenta",
                    accent_color="purple",
                    icon="🎨",
                    activity_icons={
                        "designing": "✏️",
                        "coding": "🖌️",
                        "reviewing": "🎭"
                    },
                    mood_colors={
                        "creative": "bright_magenta",
                        "focused": "magenta",
                        "frustrated": "red"
                    }
                ),
                "Alex Thompson": AgentTheme(
                    primary_color="yellow",
                    secondary_color="bright_yellow",
                    accent_color="orange",
                    icon="🔍",
                    activity_icons={
                        "testing": "🧪",
                        "debugging": "🐛",
                        "reviewing": "📋"
                    },
                    mood_colors={
                        "methodical": "yellow",
                        "alert": "bright_yellow",
                        "concerned": "orange"
                    }
                ),
                "Jordan Kim": AgentTheme(
                    primary_color="green",
                    secondary_color="bright_green",
                    accent_color="lime",
                    icon="🚀",
                    activity_icons={
                        "deploying": "📦",
                        "monitoring": "📊",
                        "automating": "⚡"
                    },
                    mood_colors={
                        "efficient": "bright_green",
                        "focused": "green",
                        "incident": "red"
                    }
                )
            }
        elif self.theme == VisualizationTheme.PROFESSIONAL:
            return {
                "Marcus Chen": AgentTheme(
                    primary_color="blue",
                    secondary_color="light_blue",
                    accent_color="navy",
                    icon="👔",
                    activity_icons={"coding": "💼", "debugging": "🔍", "thinking": "💭"}
                ),
                "Emily Rodriguez": AgentTheme(
                    primary_color="purple",
                    secondary_color="light_purple",
                    accent_color="indigo",
                    icon="👩‍💼",
                    activity_icons={"designing": "📐", "coding": "💻", "reviewing": "📝"}
                ),
                "Alex Thompson": AgentTheme(
                    primary_color="orange",
                    secondary_color="light_orange",
                    accent_color="amber",
                    icon="🧑‍💼",
                    activity_icons={"testing": "✓", "debugging": "⚠️", "reviewing": "📊"}
                ),
                "Jordan Kim": AgentTheme(
                    primary_color="teal",
                    secondary_color="light_teal",
                    accent_color="turquoise",
                    icon="👨‍💼",
                    activity_icons={"deploying": "🔄", "monitoring": "📈", "automating": "⚙️"}
                )
            }
        else:  # Default/Playful theme
            return {
                "Marcus Chen": AgentTheme(
                    primary_color="bright_blue",
                    secondary_color="blue",
                    accent_color="cyan",
                    icon="🦾",
                    activity_icons={"coding": "💻", "debugging": "🔨", "thinking": "💡"}
                ),
                "Emily Rodriguez": AgentTheme(
                    primary_color="bright_magenta",
                    secondary_color="magenta",
                    accent_color="pink",
                    icon="🦄",
                    activity_icons={"designing": "🎨", "coding": "✨", "reviewing": "👀"}
                ),
                "Alex Thompson": AgentTheme(
                    primary_color="bright_yellow",
                    secondary_color="yellow",
                    accent_color="gold",
                    icon="🦅",
                    activity_icons={"testing": "🔬", "debugging": "🔎", "reviewing": "✅"}
                ),
                "Jordan Kim": AgentTheme(
                    primary_color="bright_green",
                    secondary_color="green",
                    accent_color="lime",
                    icon="🚁",
                    activity_icons={"deploying": "🚀", "monitoring": "🎯", "automating": "🤖"}
                )
            }


class VisualizationPresets:
    """Pre-configured visualization settings for different use cases"""
    
    @staticmethod
    def demo_mode() -> VisualizationConfig:
        """Settings optimized for demonstrations"""
        return VisualizationConfig(
            theme=VisualizationTheme.CYBERPUNK,
            animation_style=AnimationStyle.SMOOTH,
            default_speed_preset="slow",
            enable_auto_slowdown=True,
            important_event_multiplier=0.3,
            enable_particle_effects=True,
            enable_glow_effects=True,
            show_agent_moods=True,
            max_code_lines_shown=15
        )
        
    @staticmethod
    def monitoring_mode() -> VisualizationConfig:
        """Settings optimized for real-time monitoring"""
        return VisualizationConfig(
            theme=VisualizationTheme.PROFESSIONAL,
            animation_style=AnimationStyle.INSTANT,
            default_speed_preset="fast",
            enable_auto_slowdown=False,
            enable_particle_effects=False,
            enable_glow_effects=False,
            show_metrics_panel=True,
            layout_style="grid",
            max_message_history=20
        )
        
    @staticmethod
    def accessibility_mode() -> VisualizationConfig:
        """Settings optimized for accessibility"""
        return VisualizationConfig(
            theme=VisualizationTheme.PROFESSIONAL,
            animation_style=AnimationStyle.INSTANT,
            high_contrast_mode=True,
            font_size="large",
            enable_particle_effects=False,
            enable_glow_effects=False,
            show_timestamps=True,
            default_speed_preset="slow"
        )
        
    @staticmethod
    def presentation_mode() -> VisualizationConfig:
        """Settings optimized for presentations"""
        return VisualizationConfig(
            theme=VisualizationTheme.PLAYFUL,
            animation_style=AnimationStyle.TYPEWRITER,
            default_speed_preset="slow",
            enable_auto_slowdown=True,
            important_event_multiplier=0.2,
            font_size="large",
            max_code_lines_shown=10,
            layout_style="focus",
            enable_particle_effects=True
        )


class ImportantEvents:
    """Define what constitutes an important event for auto-slowdown"""
    
    EVENTS = {
        # High importance - slow down significantly
        "deployment_start": {"importance": 1.0, "description": "Starting deployment"},
        "test_failure": {"importance": 0.9, "description": "Test failure detected"},
        "bug_found": {"importance": 0.9, "description": "Bug discovered"},
        "code_review_comment": {"importance": 0.8, "description": "Code review feedback"},
        
        # Medium importance - moderate slowdown
        "function_complete": {"importance": 0.6, "description": "Function completed"},
        "test_pass": {"importance": 0.5, "description": "Tests passing"},
        "design_decision": {"importance": 0.7, "description": "Design decision made"},
        
        # Low importance - minimal slowdown
        "thinking": {"importance": 0.3, "description": "Agent thinking"},
        "typing": {"importance": 0.2, "description": "Code being written"},
        "idle": {"importance": 0.1, "description": "Agent idle"}
    }
    
    @classmethod
    def get_slowdown_factor(cls, event_type: str, base_multiplier: float) -> float:
        """Calculate slowdown factor for an event"""
        if event_type in cls.EVENTS:
            importance = cls.EVENTS[event_type]["importance"]
            # More important events get more slowdown
            return base_multiplier * (1 - importance * 0.5)
        return 1.0