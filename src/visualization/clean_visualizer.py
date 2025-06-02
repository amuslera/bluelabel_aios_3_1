"""
Clean Agent Visualizer

A cleaner, more organized visualization system for agent activities.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.align import Align
from rich.columns import Columns
from rich import box


class ActivityType(Enum):
    """Types of activities agents can perform"""
    IDLE = "idle"
    THINKING = "thinking"
    CODING = "coding"
    TESTING = "testing"
    DEBUGGING = "debugging"
    REVIEWING = "reviewing"
    DEPLOYING = "deploying"
    MONITORING = "monitoring"
    DESIGNING = "designing"
    COMMUNICATING = "communicating"


@dataclass
class AgentProfile:
    """Agent profile information"""
    name: str
    role: str
    color: str
    icon: str


@dataclass
class AgentActivity:
    """Current activity of an agent"""
    activity_type: ActivityType
    description: str
    progress: float = 0.0
    start_time: datetime = field(default_factory=datetime.now)
    code_snippet: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class Message:
    """Inter-agent message"""
    from_agent: str
    to_agent: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    message_type: str = "chat"


class CleanVisualizer:
    """Clean visualization system for agent activities"""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.agents = self._initialize_agents()
        self.activities: Dict[str, AgentActivity] = {}
        self.messages: List[Message] = []
        self.metrics = {
            "lines_written": 0,
            "tests_passed": 0,
            "bugs_found": 0,
            "deployments": 0
        }
        self.workflow_items = []
        
    def _initialize_agents(self) -> Dict[str, AgentProfile]:
        """Initialize agent profiles"""
        return {
            "Marcus Chen": AgentProfile("Marcus Chen", "Backend Engineer", "cyan", "⚙️"),
            "Emily Rodriguez": AgentProfile("Emily Rodriguez", "Frontend Engineer", "magenta", "🎨"),
            "Alex Thompson": AgentProfile("Alex Thompson", "QA Engineer", "yellow", "🔍"),
            "Jordan Kim": AgentProfile("Jordan Kim", "DevOps Engineer", "green", "🚀")
        }
        
    def create_layout(self) -> Layout:
        """Create a clean, organized layout"""
        layout = Layout()
        
        # Main structure - simpler with better proportions
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3)
        )
        
        # Body split into 3 columns
        layout["body"].split_row(
            Layout(name="agents", ratio=3),      # Agent activities
            Layout(name="communication", ratio=2), # Messages & workflow
            Layout(name="metrics", ratio=1)      # Metrics
        )
        
        # Agents in 2x2 grid
        layout["agents"].split_column(
            Layout(name="agents_top"),
            Layout(name="agents_bottom")
        )
        
        layout["agents_top"].split_row(
            Layout(name="marcus"),
            Layout(name="emily")
        )
        
        layout["agents_bottom"].split_row(
            Layout(name="alex"),
            Layout(name="jordan")
        )
        
        # Communication split
        layout["communication"].split_column(
            Layout(name="messages", ratio=2),
            Layout(name="workflow", ratio=1)
        )
        
        return layout
        
    def render_agent_panel(self, agent_name: str) -> Panel:
        """Render a clean agent panel"""
        agent = self.agents.get(agent_name)
        if not agent:
            return Panel("Unknown agent", border_style="red")
            
        activity = self.activities.get(agent_name)
        
        # Build content
        content = Text()
        
        # Agent header
        content.append(f"{agent.icon} {agent.name}\n", style=f"bold {agent.color}")
        content.append(f"{agent.role}\n\n", style=f"dim {agent.color}")
        
        if activity:
            # Activity status
            status_icon = self._get_activity_icon(activity.activity_type)
            content.append(f"{status_icon} ", style=agent.color)
            content.append(f"{activity.description}\n", style="white")
            
            # Progress bar (cleaner)
            if activity.progress > 0:
                progress_bar = self._create_simple_progress_bar(activity.progress)
                content.append(f"\n{progress_bar}\n", style=agent.color)
                
            # Code snippet (if coding)
            if activity.code_snippet and len(activity.code_snippet) > 0:
                content.append("\n📝 ", style="dim")
                content.append("Code:\n", style="dim")
                # Show only first 3 lines
                lines = activity.code_snippet.split('\n')[:3]
                for line in lines:
                    if line.strip():
                        content.append(f"  {line[:40]}...\n", style="dim white")
                        
        else:
            content.append("💤 Idle", style="dim")
            
        return Panel(
            content,
            border_style=agent.color,
            box=box.ROUNDED,
            padding=(0, 1)
        )
        
    def render_messages_panel(self) -> Panel:
        """Render a clean messages panel"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Message", style="white")
        
        # Show last 6 messages
        recent = self.messages[-6:] if self.messages else []
        
        for msg in recent:
            if msg.from_agent == "System":
                table.add_row(f"[bold yellow]📢 {msg.content}[/bold yellow]")
            else:
                from_agent = self.agents.get(msg.from_agent)
                if from_agent:
                    if msg.to_agent == "Team":
                        table.add_row(
                            f"[{from_agent.color}]{from_agent.icon} → Team:[/{from_agent.color}] {msg.content[:50]}..."
                        )
                    else:
                        to_agent = self.agents.get(msg.to_agent)
                        if to_agent:
                            table.add_row(
                                f"[{from_agent.color}]{from_agent.icon}[/{from_agent.color}] → "
                                f"[{to_agent.color}]{to_agent.icon}:[/{to_agent.color}] {msg.content[:40]}..."
                            )
                            
        if not recent:
            table.add_row("[dim]No messages yet[/dim]")
            
        return Panel(
            table,
            title="💬 Team Chat",
            border_style="blue",
            box=box.ROUNDED
        )
        
    def render_workflow_panel(self) -> Panel:
        """Render a clean workflow panel"""
        content = Text()
        
        if self.workflow_items:
            for item in self.workflow_items[:5]:  # Show only 5 items
                icon = "✅" if item.get("completed") else "⏳"
                name = item.get("name", "Unknown")
                content.append(f"{icon} {name}\n", 
                             style="green" if item.get("completed") else "yellow")
        else:
            content.append("No workflow items", style="dim")
            
        return Panel(
            content,
            title="📋 Workflow",
            border_style="purple",
            box=box.ROUNDED
        )
        
    def render_metrics_panel(self) -> Panel:
        """Render a clean metrics panel"""
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="bold")
        table.add_column("Value", justify="right")
        
        table.add_row("📝 Lines", f"[cyan]{self.metrics['lines_written']}[/cyan]")
        table.add_row("✅ Tests", f"[green]{self.metrics['tests_passed']}[/green]")
        table.add_row("🐛 Bugs", f"[red]{self.metrics['bugs_found']}[/red]")
        table.add_row("🚀 Deploys", f"[blue]{self.metrics['deployments']}[/blue]")
        
        return Panel(
            table,
            title="📊 Metrics",
            border_style="green",
            box=box.ROUNDED
        )
        
    def render_header(self) -> Panel:
        """Render a clean header"""
        return Panel(
            Align.center(
                Text("🤖 AI Development Team", style="bold cyan")
            ),
            box=box.DOUBLE,
            border_style="cyan"
        )
        
    def render_footer(self) -> Panel:
        """Render a clean footer"""
        time_str = datetime.now().strftime("%H:%M:%S")
        status = f"⏰ {time_str} | 👥 4 agents active | 🔄 Running"
        
        return Panel(
            Align.center(Text(status, style="dim")),
            box=box.ROUNDED,
            border_style="dim"
        )
        
    def _get_activity_icon(self, activity_type: ActivityType) -> str:
        """Get icon for activity type"""
        icons = {
            ActivityType.IDLE: "💤",
            ActivityType.THINKING: "🤔",
            ActivityType.CODING: "💻",
            ActivityType.TESTING: "🧪",
            ActivityType.DEBUGGING: "🐛",
            ActivityType.REVIEWING: "👀",
            ActivityType.DEPLOYING: "🚀",
            ActivityType.MONITORING: "📊",
            ActivityType.DESIGNING: "📐",
            ActivityType.COMMUNICATING: "💬"
        }
        return icons.get(activity_type, "❓")
        
    def _create_simple_progress_bar(self, progress: float) -> str:
        """Create a simple text progress bar"""
        filled = int(progress / 5)  # 20 chars total
        empty = 20 - filled
        return f"[{'=' * filled}{' ' * empty}] {int(progress)}%"
        
    async def update_agent_activity(
        self, 
        agent_name: str, 
        activity_type: ActivityType,
        description: str,
        progress: float = 0.0,
        code_snippet: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Update an agent's activity"""
        self.activities[agent_name] = AgentActivity(
            activity_type=activity_type,
            description=description,
            progress=progress,
            code_snippet=code_snippet,
            metadata=metadata or {}
        )
        
    async def send_message(
        self,
        from_agent: str,
        to_agent: str,
        content: str,
        message_type: str = "chat"
    ):
        """Send a message between agents"""
        self.messages.append(Message(
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            message_type=message_type
        ))
        
        # Keep only last 20 messages
        if len(self.messages) > 20:
            self.messages = self.messages[-20:]
            
    def update_workflow(self, name: str, items: List[Dict[str, Any]]):
        """Update workflow items"""
        self.workflow_items = items
        
    async def render_frame(self, layout: Layout):
        """Render all panels into the layout"""
        layout["header"].update(self.render_header())
        layout["marcus"].update(self.render_agent_panel("Marcus Chen"))
        layout["emily"].update(self.render_agent_panel("Emily Rodriguez"))
        layout["alex"].update(self.render_agent_panel("Alex Thompson"))
        layout["jordan"].update(self.render_agent_panel("Jordan Kim"))
        layout["messages"].update(self.render_messages_panel())
        layout["workflow"].update(self.render_workflow_panel())
        layout["metrics"].update(self.render_metrics_panel())
        layout["footer"].update(self.render_footer())