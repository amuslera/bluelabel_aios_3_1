"""
Enhanced Agent Visualizer

Advanced visualization with scrollable chat history and interactive session menu.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.align import Align
from rich.columns import Columns
from rich import box
import json
import os
import asyncio
import sys


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
    initials: str


@dataclass
class AgentAction:
    """Single action performed by an agent"""
    activity_type: ActivityType
    description: str
    progress: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class Message:
    """Inter-agent message"""
    from_agent: str
    to_agent: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    message_type: str = "chat"


class ChatHistoryManager:
    """Manages scrollable chat history with navigation"""
    
    def __init__(self, max_visible: int = 6):
        self.messages: List[Message] = []
        self.max_visible = max_visible
        self.scroll_offset = 0
        self.search_term = ""
        self.filtered_messages: List[int] = []  # Indices of filtered messages
        
    def add_message(self, message: Message):
        """Add a message to history"""
        self.messages.append(message)
        # Auto-scroll to bottom when new message arrives
        self.scroll_to_bottom()
        
    def scroll_up(self, lines: int = 1):
        """Scroll up in chat history"""
        self.scroll_offset = max(0, self.scroll_offset - lines)
        
    def scroll_down(self, lines: int = 1):
        """Scroll down in chat history"""
        max_offset = max(0, len(self.get_display_messages()) - self.max_visible)
        self.scroll_offset = min(max_offset, self.scroll_offset + lines)
        
    def scroll_to_top(self):
        """Scroll to top of history"""
        self.scroll_offset = 0
        
    def scroll_to_bottom(self):
        """Scroll to bottom of history"""
        self.scroll_offset = max(0, len(self.get_display_messages()) - self.max_visible)
        
    def page_up(self):
        """Page up in chat history"""
        self.scroll_up(self.max_visible)
        
    def page_down(self):
        """Page down in chat history"""
        self.scroll_down(self.max_visible)
        
    def search(self, term: str):
        """Search for messages containing term"""
        self.search_term = term.lower()
        if not term:
            self.filtered_messages = []
            return
            
        self.filtered_messages = []
        for i, msg in enumerate(self.messages):
            if (term in msg.content.lower() or 
                term in msg.from_agent.lower() or 
                term in msg.to_agent.lower()):
                self.filtered_messages.append(i)
                
    def clear_search(self):
        """Clear search filter"""
        self.search_term = ""
        self.filtered_messages = []
        
    def get_display_messages(self) -> List[Message]:
        """Get messages to display (filtered if search active)"""
        if self.filtered_messages:
            return [self.messages[i] for i in self.filtered_messages]
        return self.messages
        
    def get_visible_messages(self) -> List[Message]:
        """Get currently visible messages based on scroll position"""
        display_messages = self.get_display_messages()
        start = self.scroll_offset
        end = start + self.max_visible
        return display_messages[start:end]
        
    def get_scroll_info(self) -> str:
        """Get scroll position info"""
        total = len(self.get_display_messages())
        if total == 0:
            return "No messages"
            
        visible_start = self.scroll_offset + 1
        visible_end = min(self.scroll_offset + self.max_visible, total)
        
        info = f"Messages {visible_start}-{visible_end}/{total}"
        if self.search_term:
            info += f" (filtered: '{self.search_term}')"
        return info


class SessionMenu:
    """Interactive session menu for post-completion actions"""
    
    def __init__(self, visualizer, console: Console):
        self.visualizer = visualizer
        self.console = console
        self.active = False
        
    def show_menu(self) -> str:
        """Show interactive menu and return selected action"""
        menu_options = [
            ("1", "📜 View Full Session Log", "view_log"),
            ("2", "💬 Browse Chat History", "browse_chat"),
            ("3", "📊 Detailed Metrics Report", "metrics_report"),
            ("4", "🔄 Run Quick Demo", "quick_demo"),
            ("5", "🎭 Run Full Sprint Demo", "full_demo"),
            ("6", "💾 Export Session Data", "export_data"),
            ("7", "🔍 Search Chat History", "search_chat"),
            ("8", "🚀 Exit", "exit")
        ]
        
        # Create menu display
        menu_content = Text()
        menu_content.append("🎉 Sprint Complete - What's Next?\n\n", style="bold cyan")
        
        for key, description, action in menu_options:
            menu_content.append(f"  {key}. {description}\n", style="white")
            
        menu_content.append("\nEnter your choice (1-8): ", style="bold yellow")
        
        menu_panel = Panel(
            menu_content,
            title="Interactive Session Menu",
            border_style="green",
            box=box.DOUBLE
        )
        
        return menu_panel
        
    async def handle_choice(self, choice: str) -> str:
        """Handle menu choice and return action"""
        actions = {
            "1": "view_log",
            "2": "browse_chat", 
            "3": "metrics_report",
            "4": "quick_demo",
            "5": "full_demo",
            "6": "export_data",
            "7": "search_chat",
            "8": "exit"
        }
        return actions.get(choice, "invalid")


class EnhancedVisualizer:
    """Enhanced visualization system with scrollable chat and interactive menu"""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.agents = self._initialize_agents()
        self.agent_actions: Dict[str, List[AgentAction]] = {name: [] for name in self.agents.keys()}
        self.chat_manager = ChatHistoryManager(max_visible=6)
        self.session_menu = SessionMenu(self, self.console)
        self.metrics = {
            "lines_written": 0,
            "tests_passed": 0,
            "bugs_found": 0,
            "deployments": 0
        }
        self.workflow_items = []
        self.session_log = []
        self.keyboard_handler = None
        self.menu_mode = False
        
    def _initialize_agents(self) -> Dict[str, AgentProfile]:
        """Initialize agent profiles with initials"""
        return {
            "Marcus Chen": AgentProfile("Marcus Chen", "Backend Engineer", "cyan", "⚙️", "MC"),
            "Emily Rodriguez": AgentProfile("Emily Rodriguez", "Frontend Engineer", "magenta", "🎨", "ER"),
            "Alex Thompson": AgentProfile("Alex Thompson", "QA Engineer", "yellow", "🔍", "AT"),
            "Jordan Kim": AgentProfile("Jordan Kim", "DevOps Engineer", "green", "🚀", "JK")
        }
        
    def _wrap_text(self, text: str, max_width: int = 35) -> List[str]:
        """Wrap text to fit in panels, preferring word boundaries"""
        if len(text) <= max_width:
            return [text]
            
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= max_width:
                current_line = current_line + " " + word if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    lines.append(word[:max_width])
                    current_line = word[max_width:]
                    
        if current_line:
            lines.append(current_line)
            
        return lines[:2]
        
    def create_layout(self, show_summary: bool = False, show_menu: bool = False) -> Layout:
        """Create layout with optional summary panel or menu"""
        layout = Layout()
        
        if show_menu:
            # Menu mode - full screen menu
            layout.split_column(
                Layout(name="menu", ratio=1)
            )
        elif show_summary:
            # Summary mode
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="body", ratio=2),
                Layout(name="summary", size=10),
                Layout(name="footer", size=3)
            )
        else:
            # Normal mode
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="body", ratio=1),
                Layout(name="footer", size=3)
            )
        
        if not show_menu:
            # Body layout (same for normal and summary modes)
            layout["body"].split_row(
                Layout(name="agents", ratio=3),
                Layout(name="communication", ratio=2),
                Layout(name="metrics", ratio=1)
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
        """Render agent panel with action history"""
        agent = self.agents.get(agent_name)
        if not agent:
            return Panel("Unknown agent", border_style="red")
            
        actions = self.agent_actions.get(agent_name, [])
        recent_actions = actions[-4:] if actions else []
        
        content = Text()
        
        # Agent header
        content.append(f"{agent.icon} {agent.name}\n", style=f"bold {agent.color}")
        content.append(f"{agent.role}\n\n", style=f"dim {agent.color}")
        
        if recent_actions:
            for i, action in enumerate(recent_actions):
                opacity = "bold" if i == len(recent_actions) - 1 else "dim"
                
                status_icon = self._get_activity_icon(action.activity_type)
                content.append(f"{status_icon} ", style=f"{opacity} {agent.color}")
                
                description_lines = self._wrap_text(action.description, 30)
                for j, line in enumerate(description_lines):
                    content.append(f"{line}\n", style=f"{opacity} white")
                
                if i == len(recent_actions) - 1 and action.progress > 0:
                    progress_bar = self._create_simple_progress_bar(action.progress)
                    content.append(f"{progress_bar}\n", style=f"{opacity} {agent.color}")
                    
                if i < len(recent_actions) - 1:
                    content.append("\n")
                    
        else:
            content.append("💤 Waiting for tasks...", style="dim")
            
        return Panel(
            content,
            border_style=agent.color,
            box=box.ROUNDED,
            padding=(0, 1)
        )
        
    def render_scrollable_messages_panel(self) -> Panel:
        """Render scrollable messages panel"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Message", style="white")
        
        # Get visible messages based on scroll position
        visible_messages = self.chat_manager.get_visible_messages()
        
        for msg in visible_messages:
            if msg.from_agent == "System":
                table.add_row(f"[bold yellow]📢 System: {msg.content}[/bold yellow]")
            else:
                from_agent = self.agents.get(msg.from_agent)
                if from_agent:
                    if msg.to_agent == "Team":
                        content_lines = self._wrap_text(msg.content, 45)
                        first_line = content_lines[0] if content_lines else msg.content
                        table.add_row(
                            f"[{from_agent.color}]{from_agent.icon}{from_agent.initials} → Team:[/{from_agent.color}] {first_line}"
                        )
                    else:
                        to_agent = self.agents.get(msg.to_agent)
                        if to_agent:
                            content_lines = self._wrap_text(msg.content, 35)
                            first_line = content_lines[0] if content_lines else msg.content
                            table.add_row(
                                f"[{from_agent.color}]{from_agent.icon}{from_agent.initials}[/{from_agent.color}] → "
                                f"[{to_agent.color}]{to_agent.icon}{to_agent.initials}:[/{to_agent.color}] {first_line}"
                            )
                            
        if not visible_messages:
            table.add_row("[dim]No messages to display[/dim]")
            
        # Add scroll info to title
        scroll_info = self.chat_manager.get_scroll_info()
        title = f"💬 Team Chat ({scroll_info})"
        
        return Panel(
            table,
            title=title,
            border_style="blue",
            box=box.ROUNDED
        )
        
    def render_workflow_panel(self) -> Panel:
        """Render workflow panel"""
        content = Text()
        
        if self.workflow_items:
            for item in self.workflow_items[:5]:
                icon = "✅" if item.get("completed") else "⏳"
                name = item.get("name", "Unknown")
                name_lines = self._wrap_text(name, 25)
                for i, line in enumerate(name_lines):
                    prefix = f"{icon} " if i == 0 else "   "
                    content.append(f"{prefix}{line}\n", 
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
        """Render metrics panel"""
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
        """Render header"""
        header_text = Text("🤖 AI Development Team", style="bold cyan")
        
        # Add keyboard shortcuts info
        shortcuts = " | ↑↓ Scroll Chat | PgUp/PgDn Page | /search | m Menu"
        header_text.append(shortcuts, style="dim")
        
        return Panel(
            Align.center(header_text),
            box=box.DOUBLE,
            border_style="cyan"
        )
        
    def render_footer(self) -> Panel:
        """Render footer"""
        time_str = datetime.now().strftime("%H:%M:%S")
        status = f"⏰ {time_str} | 👥 4 agents active | 🔄 Running"
        
        return Panel(
            Align.center(Text(status, style="dim")),
            box=box.ROUNDED,
            border_style="dim"
        )
        
    def render_summary_panel(self, console_messages: List[str], exported_file: Optional[str] = None) -> Panel:
        """Render session summary panel"""
        session_content = Text()
        session_content.append("📝 Session Log:\n", style="bold cyan")
        for i, msg in enumerate(console_messages[-5:], 1):
            session_content.append(f"{i}. {msg}\n", style="white")
            
        session_panel = Panel(
            session_content,
            title="Session Log",
            border_style="cyan",
            box=box.ROUNDED
        )
        
        results_content = Text()
        results_content.append("📊 Final Results:\n", style="bold yellow")
        results_content.append(f"📝 Lines: {self.metrics['lines_written']}\n", style="cyan")
        results_content.append(f"✅ Tests: {self.metrics['tests_passed']}\n", style="green")
        results_content.append(f"🐛 Bugs: {self.metrics['bugs_found']}\n", style="red")
        results_content.append(f"🚀 Deploys: {self.metrics['deployments']}\n", style="blue")
        
        results_panel = Panel(
            results_content,
            title="Sprint Results",
            border_style="yellow",
            box=box.ROUNDED
        )
        
        export_content = Text()
        export_content.append("💾 Export Status:\n", style="bold magenta")
        if exported_file:
            export_content.append(f"✅ Exported!\n", style="green")
            filename = os.path.basename(exported_file) if exported_file else "unknown"
            export_content.append(f"📄 {filename}\n", style="dim")
            export_content.append("Complete session log\nwith all activities\n\n", style="white")
            export_content.append("Press 'm' for menu", style="bold cyan")
        else:
            export_content.append("⏳ Export pending...", style="yellow")
            
        export_panel = Panel(
            export_content,
            title="Export Status",
            border_style="magenta",
            box=box.ROUNDED
        )
        
        columns = Columns([session_panel, results_panel, export_panel], equal=True)
        
        return Panel(
            columns,
            title="🎉 Sprint Complete - Session Summary",
            border_style="green",
            box=box.DOUBLE
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
        filled = int(progress / 5)
        empty = 20 - filled
        return f"[{'=' * filled}{' ' * empty}] {int(progress)}%"
        
    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Log event for export"""
        self.session_log.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        })
        
    async def update_agent_activity(
        self, 
        agent_name: str, 
        activity_type: ActivityType,
        description: str,
        progress: float = 0.0,
        code_snippet: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Update agent activity"""
        action = AgentAction(
            activity_type=activity_type,
            description=description,
            progress=progress,
            metadata=metadata or {}
        )
        
        if agent_name in self.agent_actions:
            self.agent_actions[agent_name].append(action)
            
        self._log_event("activity_update", {
            "agent": agent_name,
            "activity": activity_type.value,
            "description": description,
            "progress": progress
        })
        
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
        
        self.chat_manager.add_message(message)
        
        self._log_event("message", {
            "from": from_agent,
            "to": to_agent,
            "content": content,
            "type": message_type
        })
        
    def update_workflow(self, name: str, items: List[Dict[str, Any]]):
        """Update workflow items"""
        self.workflow_items = items
        self._log_event("workflow_update", {"name": name, "items": items})
        
    def export_session_log(self, filename: Optional[str] = None) -> str:
        """Export session log to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_team_session_enhanced_{timestamp}.json"
            
        export_data = {
            "session_info": {
                "start_time": self.session_log[0]["timestamp"] if self.session_log else datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "agents": [
                    {
                        "name": agent.name,
                        "role": agent.role,
                        "total_actions": len(self.agent_actions.get(name, []))
                    }
                    for name, agent in self.agents.items()
                ]
            },
            "final_metrics": self.metrics,
            "final_workflow": self.workflow_items,
            "events": self.session_log,
            "chat_history": [
                {
                    "from": msg.from_agent,
                    "to": msg.to_agent,
                    "content": msg.content,
                    "type": msg.message_type,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in self.chat_manager.messages
            ],
            "agent_action_history": {
                name: [
                    {
                        "activity_type": action.activity_type.value,
                        "description": action.description,
                        "progress": action.progress,
                        "timestamp": action.timestamp.isoformat()
                    }
                    for action in actions
                ]
                for name, actions in self.agent_actions.items()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        return filename
        
    async def render_frame(self, layout: Layout, console_messages: Optional[List[str]] = None, exported_file: Optional[str] = None):
        """Render all panels into the layout"""
        if "menu" in layout._children:
            # Menu mode
            layout["menu"].update(self.session_menu.show_menu())
        else:
            # Normal or summary mode
            layout["header"].update(self.render_header())
            layout["marcus"].update(self.render_agent_panel("Marcus Chen"))
            layout["emily"].update(self.render_agent_panel("Emily Rodriguez"))
            layout["alex"].update(self.render_agent_panel("Alex Thompson"))
            layout["jordan"].update(self.render_agent_panel("Jordan Kim"))
            layout["messages"].update(self.render_scrollable_messages_panel())
            layout["workflow"].update(self.render_workflow_panel())
            layout["metrics"].update(self.render_metrics_panel())
            layout["footer"].update(self.render_footer())
            
            # Render summary panel if present
            try:
                if console_messages is not None:
                    layout["summary"].update(self.render_summary_panel(console_messages, exported_file))
            except KeyError:
                pass