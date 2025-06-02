"""
Agent Activity Visualization System

A theatrical, user-friendly visualization system that shows what each agent
is doing in real-time with configurable pacing for human comprehension.
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.syntax import Syntax
from rich.columns import Columns
from rich.align import Align
import random


class ActivityType(Enum):
    """Types of activities agents can perform"""
    THINKING = "thinking"
    CODING = "coding"
    TESTING = "testing"
    REVIEWING = "reviewing"
    DEPLOYING = "deploying"
    COMMUNICATING = "communicating"
    DEBUGGING = "debugging"
    DESIGNING = "designing"
    MONITORING = "monitoring"
    IDLE = "idle"


@dataclass
class AgentProfile:
    """Visual profile for each agent"""
    name: str
    role: str
    color: str
    icon: str
    status_emoji: Dict[ActivityType, str] = field(default_factory=dict)
    
    def __post_init__(self):
        # Default status emojis
        if not self.status_emoji:
            self.status_emoji = {
                ActivityType.THINKING: "🤔",
                ActivityType.CODING: "💻",
                ActivityType.TESTING: "🧪",
                ActivityType.REVIEWING: "👀",
                ActivityType.DEPLOYING: "🚀",
                ActivityType.COMMUNICATING: "💬",
                ActivityType.DEBUGGING: "🐛",
                ActivityType.DESIGNING: "🎨",
                ActivityType.MONITORING: "📊",
                ActivityType.IDLE: "☕"
            }


@dataclass
class AgentActivity:
    """Represents a single agent activity"""
    agent_name: str
    activity_type: ActivityType
    description: str
    progress: float = 0.0  # 0-100
    start_time: datetime = field(default_factory=datetime.now)
    code_snippet: Optional[str] = None
    target_agent: Optional[str] = None  # For communications
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """Inter-agent message"""
    from_agent: str
    to_agent: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    message_type: str = "chat"  # chat, code_review, task_handoff, alert


class TheatricalPacing:
    """Controls the speed of visualization for human comprehension"""
    
    def __init__(self):
        self.speed_multiplier = 1.0  # 1.0 = normal, 0.5 = half speed, 2.0 = double speed
        self.presets = {
            "realtime": 5.0,      # Actual agent speed (too fast for humans)
            "fast": 2.0,          # Quick but followable
            "normal": 1.0,        # Comfortable viewing pace
            "slow": 0.5,          # Detailed observation
            "step": 0.1,          # Nearly frame-by-frame
            "pause": 0.0          # Paused
        }
        self.current_preset = "normal"
        
    def set_speed(self, preset: str):
        """Set speed using a preset"""
        if preset in self.presets:
            self.current_preset = preset
            self.speed_multiplier = self.presets[preset]
            
    def get_delay(self, base_delay: float) -> float:
        """Get adjusted delay based on current speed"""
        if self.speed_multiplier == 0:
            return float('inf')  # Paused
        return base_delay / self.speed_multiplier
        
    def should_skip_frame(self) -> bool:
        """Determine if we should skip rendering this frame for performance"""
        if self.speed_multiplier > 3.0:
            # Skip some frames at very high speeds
            return random.random() > (1.0 / self.speed_multiplier)
        return False


class AgentVisualizer:
    """Main visualization system for agent activities"""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.agents = self._initialize_agents()
        self.activities: Dict[str, AgentActivity] = {}
        self.messages: List[Message] = []
        self.pacing = TheatricalPacing()
        self.workflow_stages: List[Dict[str, Any]] = []
        self.code_buffer: Dict[str, List[str]] = {}  # Agent -> lines of code
        self.metrics = {
            "lines_written": 0,
            "tests_passed": 0,
            "bugs_found": 0,
            "deployments": 0
        }
        self.running = False
        
    def _initialize_agents(self) -> Dict[str, AgentProfile]:
        """Initialize agent profiles with colors and icons"""
        return {
            "Marcus Chen": AgentProfile(
                name="Marcus Chen",
                role="Backend Engineer",
                color="cyan",
                icon="⚙️"
            ),
            "Emily Rodriguez": AgentProfile(
                name="Emily Rodriguez",
                role="Frontend Engineer",
                color="magenta",
                icon="🎨"
            ),
            "Alex Thompson": AgentProfile(
                name="Alex Thompson",
                role="QA Engineer",
                color="yellow",
                icon="🔍"
            ),
            "Jordan Kim": AgentProfile(
                name="Jordan Kim",
                role="DevOps Engineer",
                color="green",
                icon="🚀"
            )
        }
        
    def create_layout(self) -> Layout:
        """Create the main visualization layout"""
        layout = Layout()
        
        # Main layout structure
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=4)
        )
        
        # Split main area
        layout["main"].split_row(
            Layout(name="agents", ratio=2),
            Layout(name="activity", ratio=3),
            Layout(name="metrics", ratio=1)
        )
        
        # Split agents area
        layout["agents"].split_column(
            Layout(name="agent_marcus", size=6),
            Layout(name="agent_emily", size=6),
            Layout(name="agent_alex", size=6),
            Layout(name="agent_jordan", size=6)
        )
        
        # Split activity area
        layout["activity"].split_column(
            Layout(name="messages", size=8),
            Layout(name="code", ratio=1),
            Layout(name="workflow", size=6)
        )
        
        return layout
        
    def render_header(self) -> Panel:
        """Render the header with title and controls"""
        speed_indicator = f"Speed: {self.pacing.current_preset.upper()} ({self.pacing.speed_multiplier}x)"
        controls = "Controls: [1-5] Speed | [Space] Pause | [Q] Quit"
        
        header_text = Text()
        header_text.append("🤖 AI Development Team Visualizer\n", style="bold cyan")
        header_text.append(f"{speed_indicator} | {controls}", style="dim")
        
        return Panel(
            Align.center(header_text),
            border_style="bright_blue"
        )
        
    def render_agent_panel(self, agent_name: str) -> Panel:
        """Render individual agent status panel"""
        agent = self.agents[agent_name]
        activity = self.activities.get(agent_name)
        
        # Create agent header with icon and name
        header = Text()
        header.append(f"{agent.icon} ", style=f"bold {agent.color}")
        header.append(agent.name, style=f"bold {agent.color}")
        
        # Create content
        content = Text()
        
        if activity:
            # Status line with emoji
            emoji = agent.status_emoji[activity.activity_type]
            content.append(f"{emoji} {activity.activity_type.value.title()}\n", style=f"{agent.color}")
            
            # Description
            content.append(f"{activity.description}\n", style="white")
            
            # Progress bar if applicable
            if activity.progress > 0:
                progress_bar = self._create_mini_progress_bar(activity.progress)
                content.append(progress_bar)
                
            # Mood indicator (if agent has mood)
            if activity.metadata.get("mood"):
                mood = activity.metadata["mood"]
                mood_emoji = self._get_mood_emoji(mood)
                content.append(f"\nMood: {mood_emoji} {mood}", style="dim")
        else:
            content.append("☕ Taking a break...", style="dim")
            
        # Role subtitle
        subtitle = f"[{agent.role}]"
        
        return Panel(
            content,
            title=header,
            subtitle=subtitle,
            border_style=agent.color,
            padding=(0, 1)
        )
        
    def render_messages_panel(self) -> Panel:
        """Render inter-agent communications"""
        content = Text()
        
        # Show last 5 messages
        recent_messages = self.messages[-5:] if self.messages else []
        
        for msg in recent_messages:
            # Handle system messages
            if msg.from_agent == "System":
                content.append("📢 ", style="yellow")
                content.append("System", style="bold yellow")
                content.append(f": {msg.content}\n", style="white")
            elif msg.to_agent == "Team":
                # Broadcast message
                from_agent = self.agents.get(msg.from_agent)
                if from_agent:
                    content.append(f"{from_agent.icon} ", style=from_agent.color)
                    content.append(f"{msg.from_agent}", style=from_agent.color)
                    content.append(" → ", style="white")
                    content.append("Team", style="bold white")
                    content.append(f": {msg.content}\n", style="white")
                else:
                    content.append(f"{msg.from_agent} → Team: {msg.content}\n", style="white")
            else:
                # Direct message between agents
                from_agent = self.agents.get(msg.from_agent)
                to_agent = self.agents.get(msg.to_agent)
                
                if from_agent and to_agent:
                    content.append(f"{from_agent.icon} ", style=from_agent.color)
                    content.append("→ ", style="white")
                    content.append(f"{to_agent.icon}", style=to_agent.color)
                    content.append(f": {msg.content}\n", style="white")
                else:
                    content.append(f"{msg.from_agent} → {msg.to_agent}: {msg.content}\n", style="white")
            
        if not recent_messages:
            content.append("No recent messages...", style="dim")
            
        return Panel(
            content,
            title="💬 Team Communication",
            border_style="blue"
        )
        
    def render_code_panel(self) -> Panel:
        """Render code being written"""
        # Get the most recent code snippet from any agent
        recent_code = None
        code_agent = None
        
        for agent_name, activity in self.activities.items():
            if activity.code_snippet and activity.activity_type == ActivityType.CODING:
                recent_code = activity.code_snippet
                code_agent = agent_name
                break
                
        if recent_code:
            agent_color = self.agents[code_agent].color
            syntax = Syntax(
                recent_code,
                "python",
                theme="monokai",
                line_numbers=True,
                word_wrap=True
            )
            title = f"💻 {code_agent} is coding..."
        else:
            syntax = Text("Waiting for code generation...", style="dim")
            title = "💻 Code Output"
            agent_color = "white"
            
        return Panel(
            syntax,
            title=title,
            border_style=agent_color
        )
        
    def render_workflow_panel(self) -> Panel:
        """Render current workflow stage"""
        content = Text()
        
        if self.workflow_stages:
            current_stage = self.workflow_stages[-1]
            content.append(f"📋 {current_stage['name']}\n", style="bold")
            
            # Show subtasks
            for subtask in current_stage.get('subtasks', []):
                status = "✅" if subtask['completed'] else "⏳"
                content.append(f"  {status} {subtask['name']}\n", style="white")
        else:
            content.append("No active workflow", style="dim")
            
        return Panel(
            content,
            title="🔄 Workflow Progress",
            border_style="purple"
        )
        
    def render_metrics_panel(self) -> Panel:
        """Render productivity metrics"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green", justify="right")
        
        table.add_row("📝 Lines Written", str(self.metrics["lines_written"]))
        table.add_row("✅ Tests Passed", str(self.metrics["tests_passed"]))
        table.add_row("🐛 Bugs Found", str(self.metrics["bugs_found"]))
        table.add_row("🚀 Deployments", str(self.metrics["deployments"]))
        table.add_row("⚡ Efficiency", f"{self._calculate_efficiency()}%")
        
        return Panel(
            table,
            title="📊 Team Metrics",
            border_style="green"
        )
        
    def render_footer(self) -> Panel:
        """Render footer with timeline"""
        # Create a simple activity timeline
        timeline = self._create_activity_timeline()
        
        return Panel(
            timeline,
            title="📅 Activity Timeline",
            border_style="dim"
        )
        
    def _create_mini_progress_bar(self, progress: float, width: int = 20) -> Text:
        """Create a small progress bar"""
        filled = int((progress / 100) * width)
        empty = width - filled
        
        bar = Text()
        bar.append("[", style="white")
        bar.append("█" * filled, style="green")
        bar.append("░" * empty, style="dim")
        bar.append("]", style="white")
        bar.append(f" {progress:.0f}%", style="green")
        
        return bar
        
    def _get_mood_emoji(self, mood: str) -> str:
        """Get emoji for agent mood"""
        mood_emojis = {
            "energetic": "😄",
            "focused": "😐",
            "stressed": "😰",
            "thoughtful": "🤔",
            "accomplished": "😎",
            "collaborative": "🤝"
        }
        return mood_emojis.get(mood.lower(), "😊")
        
    def _create_activity_timeline(self) -> Text:
        """Create a visual timeline of recent activities"""
        timeline = Text()
        
        # Get recent activities (last 10)
        recent_activities = []
        for agent_name, activity in self.activities.items():
            if activity.start_time:
                recent_activities.append((agent_name, activity))
                
        # Sort by time and take last 10
        recent_activities.sort(key=lambda x: x[1].start_time)
        recent_activities = recent_activities[-10:]
        
        for agent_name, activity in recent_activities:
            agent = self.agents[agent_name]
            time_str = activity.start_time.strftime("%H:%M:%S")
            
            timeline.append(f"{time_str} ", style="dim")
            timeline.append(f"{agent.icon} ", style=agent.color)
            timeline.append(f"{activity.description[:50]}...\n", style="white")
            
        return timeline
        
    def _calculate_efficiency(self) -> int:
        """Calculate team efficiency metric"""
        if self.metrics["lines_written"] == 0:
            return 0
            
        # Simple efficiency calculation
        efficiency = min(100, int(
            (self.metrics["tests_passed"] * 100) / 
            max(1, self.metrics["lines_written"] / 10)
        ))
        
        return efficiency
        
    async def update_agent_activity(
        self, 
        agent_name: str, 
        activity_type: ActivityType,
        description: str,
        progress: float = 0.0,
        code_snippet: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Update an agent's current activity"""
        self.activities[agent_name] = AgentActivity(
            agent_name=agent_name,
            activity_type=activity_type,
            description=description,
            progress=progress,
            code_snippet=code_snippet,
            metadata=metadata or {}
        )
        
        # Update metrics based on activity
        if activity_type == ActivityType.CODING and code_snippet:
            self.metrics["lines_written"] += len(code_snippet.split('\n'))
        elif activity_type == ActivityType.TESTING and progress >= 100:
            self.metrics["tests_passed"] += 1
        elif activity_type == ActivityType.DEBUGGING:
            self.metrics["bugs_found"] += 1
        elif activity_type == ActivityType.DEPLOYING and progress >= 100:
            self.metrics["deployments"] += 1
            
    async def send_message(
        self, 
        from_agent: str, 
        to_agent: str, 
        content: str,
        message_type: str = "chat"
    ):
        """Send a message between agents"""
        message = Message(
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            message_type=message_type
        )
        self.messages.append(message)
        
        # Keep only last 20 messages
        if len(self.messages) > 20:
            self.messages = self.messages[-20:]
            
    def update_workflow(self, stage_name: str, subtasks: List[Dict[str, Any]]):
        """Update current workflow stage"""
        self.workflow_stages.append({
            "name": stage_name,
            "subtasks": subtasks,
            "timestamp": datetime.now()
        })
        
        # Keep only last 5 stages
        if len(self.workflow_stages) > 5:
            self.workflow_stages = self.workflow_stages[-5:]
            
    def handle_input(self, key: str):
        """Handle keyboard input for speed control"""
        if key == " ":  # Space bar
            if self.pacing.current_preset == "pause":
                self.pacing.set_speed("normal")
            else:
                self.pacing.set_speed("pause")
        elif key in "12345":
            speed_map = {
                "1": "step",
                "2": "slow", 
                "3": "normal",
                "4": "fast",
                "5": "realtime"
            }
            self.pacing.set_speed(speed_map[key])
        elif key.lower() == "q":
            self.running = False
            
    async def render_frame(self, layout: Layout):
        """Render a single frame of the visualization"""
        # Update all panels
        layout["header"].update(self.render_header())
        
        # Agent panels
        layout["agent_marcus"].update(self.render_agent_panel("Marcus Chen"))
        layout["agent_emily"].update(self.render_agent_panel("Emily Rodriguez"))
        layout["agent_alex"].update(self.render_agent_panel("Alex Thompson"))
        layout["agent_jordan"].update(self.render_agent_panel("Jordan Kim"))
        
        # Activity panels
        layout["messages"].update(self.render_messages_panel())
        layout["code"].update(self.render_code_panel())
        layout["workflow"].update(self.render_workflow_panel())
        
        # Metrics and footer
        layout["metrics"].update(self.render_metrics_panel())
        layout["footer"].update(self.render_footer())
        
    async def run(self):
        """Run the visualization"""
        self.running = True
        layout = self.create_layout()
        
        with Live(
            layout,
            console=self.console,
            screen=True,
            refresh_per_second=10
        ) as live:
            while self.running:
                # Check for frame skip at high speeds
                if not self.pacing.should_skip_frame():
                    await self.render_frame(layout)
                    live.update(layout)
                
                # Theatrical delay
                await asyncio.sleep(self.pacing.get_delay(0.1))
                
                # Handle any keyboard input (would need to be integrated with actual input system)
                # This is a placeholder for the input handling
                
        self.console.print("\n[bold green]Visualization ended.[/bold green]")