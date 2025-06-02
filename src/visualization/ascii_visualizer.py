#!/usr/bin/env python3
"""
ASCII-only visualizer for terminals with box drawing issues
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
from rich.align import Align
from rich.columns import Columns
from rich import box
import json
import os
import asyncio
import sys

# Add src to path
sys.path.insert(0, '/Users/arielmuslera/Development/Projects/bluelabel-AIOSv3.1')

from src.visualization.enhanced_visualizer import (
    ActivityType, AgentProfile, AgentAction, Message, 
    ChatHistoryManager, SessionMenu
)


class ASCIIVisualizer:
    """ASCII-only visualizer for maximum terminal compatibility"""
    
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
            layout.split_column(
                Layout(name="menu", ratio=1)
            )
        elif show_summary:
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="body", ratio=2),
                Layout(name="summary", size=10),
                Layout(name="footer", size=3)
            )
        else:
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="body", ratio=1),
                Layout(name="footer", size=3)
            )
        
        if not show_menu:
            layout["body"].split_row(
                Layout(name="agents", ratio=3),
                Layout(name="communication", ratio=2),
                Layout(name="metrics", ratio=1)
            )
            
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
            
            layout["communication"].split_column(
                Layout(name="messages", ratio=2),
                Layout(name="workflow", ratio=1)
            )
        
        return layout
        
    def render_agent_panel(self, agent_name: str) -> Panel:
        """Render agent panel with action history using ASCII borders"""
        agent = self.agents.get(agent_name)
        if not agent:
            return Panel("Unknown agent", border_style="red", box=box.ASCII)
            
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
            box=box.ASCII,
            padding=(0, 1)
        )
        
    def render_scrollable_messages_panel(self) -> Panel:
        """Render scrollable messages panel with ASCII borders"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Message", style="white")
        
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
            
        scroll_info = self.chat_manager.get_scroll_info()
        title = f"💬 Team Chat ({scroll_info})"
        
        return Panel(
            table,
            title=title,
            border_style="blue",
            box=box.ASCII
        )
        
    def render_workflow_panel(self) -> Panel:
        """Render workflow panel with ASCII borders"""
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
            box=box.ASCII
        )
        
    def render_metrics_panel(self) -> Panel:
        """Render metrics panel with ASCII borders"""
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
            box=box.ASCII
        )
        
    def render_header(self) -> Panel:
        """Render header with ASCII borders"""
        header_text = Text("🤖 AI Development Team", style="bold cyan")
        shortcuts = " | ↑↓ Scroll Chat | PgUp/PgDn Page | /search | m Menu"
        header_text.append(shortcuts, style="dim")
        
        return Panel(
            Align.center(header_text),
            box=box.ASCII,
            border_style="cyan"
        )
        
    def render_footer(self) -> Panel:
        """Render footer with ASCII borders"""
        time_str = datetime.now().strftime("%H:%M:%S")
        status = f"⏰ {time_str} | 👥 4 agents active | 🔄 Running"
        
        return Panel(
            Align.center(Text(status, style="dim")),
            box=box.ASCII,
            border_style="dim"
        )
        
    def render_summary_panel(self, console_messages: List[str], exported_file: Optional[str] = None) -> Panel:
        """Render session summary panel with ASCII borders"""
        session_content = Text()
        session_content.append("📝 Session Log:\n", style="bold cyan")
        for i, msg in enumerate(console_messages[-5:], 1):
            session_content.append(f"{i}. {msg}\n", style="white")
            
        session_panel = Panel(
            session_content,
            title="Session Log",
            border_style="cyan",
            box=box.ASCII
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
            box=box.ASCII
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
            box=box.ASCII
        )
        
        columns = Columns([session_panel, results_panel, export_panel], equal=True)
        
        return Panel(
            columns,
            title="🎉 Sprint Complete - Session Summary",
            border_style="green",
            box=box.ASCII
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
            filename = f"ai_team_session_ascii_{timestamp}.json"
            
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
            # Create ASCII menu
            menu_content = Text()
            menu_content.append("🎉 Sprint Complete - What's Next?\n\n", style="bold cyan")
            
            menu_options = [
                ("1", "📜 View Full Session Log"),
                ("2", "💬 Browse Chat History"),
                ("3", "📊 Detailed Metrics Report"),
                ("4", "🔄 Run Quick Demo"),
                ("5", "🎭 Run Full Sprint Demo"),
                ("6", "💾 Export Session Data"),
                ("7", "🔍 Search Chat History"),
                ("8", "🚀 Exit")
            ]
            
            for key, description in menu_options:
                menu_content.append(f"  {key}. {description}\n", style="white")
                
            menu_content.append("\nEnter your choice (1-8): ", style="bold yellow")
            
            menu_panel = Panel(
                menu_content,
                title="Interactive Session Menu",
                border_style="green",
                box=box.ASCII
            )
            layout["menu"].update(menu_panel)
        else:
            layout["header"].update(self.render_header())
            layout["marcus"].update(self.render_agent_panel("Marcus Chen"))
            layout["emily"].update(self.render_agent_panel("Emily Rodriguez"))
            layout["alex"].update(self.render_agent_panel("Alex Thompson"))
            layout["jordan"].update(self.render_agent_panel("Jordan Kim"))
            layout["messages"].update(self.render_scrollable_messages_panel())
            layout["workflow"].update(self.render_workflow_panel())
            layout["metrics"].update(self.render_metrics_panel())
            layout["footer"].update(self.render_footer())
            
            try:
                if console_messages is not None:
                    layout["summary"].update(self.render_summary_panel(console_messages, exported_file))
            except KeyError:
                pass


async def test_ascii_visualizer():
    """Test the ASCII visualizer"""
    console = Console()
    visualizer = ASCIIVisualizer(console=console)
    
    console.clear()
    console.print("[bold green]🔧 Testing ASCII Visualizer (No Unicode Box Drawing)[/bold green]\n")
    
    # Add sample data
    await visualizer.update_agent_activity(
        "Marcus Chen", ActivityType.CODING, 
        "Building authentication API with secure JWT handling", 75
    )
    
    await visualizer.send_message("Marcus Chen", "Team", "Backend API endpoints ready for testing")
    await visualizer.send_message("Emily Rodriguez", "Marcus Chen", "Great! Starting frontend integration")
    
    visualizer.metrics["lines_written"] = 150
    visualizer.metrics["tests_passed"] = 25
    
    # Test individual panels
    agent_panel = visualizer.render_agent_panel("Marcus Chen")
    console.print(agent_panel)
    console.print()
    
    messages_panel = visualizer.render_scrollable_messages_panel()
    console.print(messages_panel)
    console.print()
    
    metrics_panel = visualizer.render_metrics_panel()
    console.print(metrics_panel)
    
    console.print("\n[bold green]✅ ASCII visualizer test complete![/bold green]")
    console.print("All panels should now display with solid ASCII borders.")


if __name__ == "__main__":
    try:
        asyncio.run(test_ascii_visualizer())
    except KeyboardInterrupt:
        print("\n\nTest interrupted.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()