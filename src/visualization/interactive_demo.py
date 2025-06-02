#!/usr/bin/env python3
"""
Interactive Agent Visualization Demo

Enhanced demo with scrollable chat history and interactive session menu.
"""

import asyncio
import sys
import os
import threading
import queue
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from rich.text import Text

# Add src to path
sys.path.insert(0, '/Users/arielmuslera/Development/Projects/bluelabel-AIOSv3.1')

from src.visualization.enhanced_visualizer import EnhancedVisualizer, ActivityType


class KeyboardHandler:
    """Handle keyboard input for interactive controls"""
    
    def __init__(self, visualizer, console):
        self.visualizer = visualizer
        self.console = console
        self.key_queue = queue.Queue()
        self.running = True
        self.menu_mode = False
        
    def start_keyboard_thread(self):
        """Start keyboard input thread"""
        def keyboard_worker():
            try:
                import termios
                import tty
                
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                
                try:
                    tty.setraw(sys.stdin.fileno())
                    
                    while self.running:
                        if sys.stdin in self._select([sys.stdin], [], [], 0.1)[0]:
                            key = sys.stdin.read(1)
                            self.key_queue.put(key)
                            
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    
            except Exception as e:
                # Fallback for non-Unix systems or if termios fails
                pass
                
        self.keyboard_thread = threading.Thread(target=keyboard_worker)
        self.keyboard_thread.daemon = True
        self.keyboard_thread.start()
        
    def _select(self, *args):
        """Cross-platform select implementation"""
        try:
            import select
            return select.select(*args)
        except ImportError:
            # Windows fallback
            return [[], [], []]
            
    async def process_keys(self):
        """Process keyboard input"""
        try:
            while not self.key_queue.empty():
                key = self.key_queue.get_nowait()
                await self.handle_key(key)
        except queue.Empty:
            pass
            
    async def handle_key(self, key: str):
        """Handle individual key presses"""
        if self.menu_mode:
            # Menu navigation
            if key in '12345678':
                action = await self.visualizer.session_menu.handle_choice(key)
                await self.handle_menu_action(action)
            elif key == '\x1b':  # Escape
                self.menu_mode = False
                
        else:
            # Normal mode navigation
            if key == '\x1b':  # Arrow keys start with escape
                # Read the rest of the escape sequence
                try:
                    next1 = self.key_queue.get(timeout=0.1)
                    next2 = self.key_queue.get(timeout=0.1)
                    
                    if next1 == '[':
                        if next2 == 'A':  # Up arrow
                            self.visualizer.chat_manager.scroll_up()
                        elif next2 == 'B':  # Down arrow
                            self.visualizer.chat_manager.scroll_down()
                        elif next2 == '5':  # Page Up
                            extra = self.key_queue.get(timeout=0.1)  # Get the '~'
                            self.visualizer.chat_manager.page_up()
                        elif next2 == '6':  # Page Down
                            extra = self.key_queue.get(timeout=0.1)  # Get the '~'
                            self.visualizer.chat_manager.page_down()
                            
                except queue.Empty:
                    pass
                    
            elif key == 'm' or key == 'M':
                self.menu_mode = True
                
            elif key == '/':
                # Start search mode
                search_term = await self.get_search_input()
                if search_term:
                    self.visualizer.chat_manager.search(search_term)
                    
            elif key == 'c' or key == 'C':
                # Clear search
                self.visualizer.chat_manager.clear_search()
                
            elif key == 'q' or key == 'Q':
                self.running = False
                
    async def get_search_input(self) -> str:
        """Get search input from user (simplified)"""
        # For now, return empty string - in a full implementation,
        # this would capture user input for search
        return ""
        
    async def handle_menu_action(self, action: str):
        """Handle menu actions"""
        if action == "view_log":
            await self.show_full_log()
        elif action == "browse_chat":
            await self.browse_chat_mode()
        elif action == "metrics_report":
            await self.show_metrics_report()
        elif action == "export_data":
            filename = self.visualizer.export_session_log()
            self.console.print(f"✅ Session exported to: {filename}")
        elif action == "exit":
            self.running = False
        else:
            self.menu_mode = False
            
    async def show_full_log(self):
        """Show full session log"""
        self.console.print("\n[bold cyan]📜 Full Session Log[/bold cyan]")
        for i, event in enumerate(self.visualizer.session_log[-20:], 1):
            timestamp = event["timestamp"][:19]  # Remove microseconds
            event_type = event["event_type"]
            self.console.print(f"{i:2d}. [{timestamp}] {event_type}")
            
        self.console.print("\n[dim]Press any key to continue...[/dim]")
        self.menu_mode = False
        
    async def browse_chat_mode(self):
        """Enter chat browsing mode"""
        self.console.print("\n[bold cyan]💬 Chat History Browser[/bold cyan]")
        self.console.print("Use ↑↓ arrows to scroll, 'q' to exit chat mode")
        
        # Set chat to show more messages temporarily
        old_max = self.visualizer.chat_manager.max_visible
        self.visualizer.chat_manager.max_visible = 15
        
        # Browse mode would be implemented here
        await asyncio.sleep(2)
        
        # Restore original setting
        self.visualizer.chat_manager.max_visible = old_max
        self.menu_mode = False
        
    async def show_metrics_report(self):
        """Show detailed metrics report"""
        self.console.print("\n[bold cyan]📊 Detailed Metrics Report[/bold cyan]")
        
        metrics = self.visualizer.metrics
        total_messages = len(self.visualizer.chat_manager.messages)
        total_actions = sum(len(actions) for actions in self.visualizer.agent_actions.values())
        
        report = f"""
📈 Development Metrics:
   📝 Lines Written: {metrics['lines_written']}
   ✅ Tests Passed: {metrics['tests_passed']}
   🐛 Bugs Found: {metrics['bugs_found']}
   🚀 Deployments: {metrics['deployments']}

💬 Communication Metrics:
   📨 Total Messages: {total_messages}
   🔄 Agent Actions: {total_actions}
   
⏱️  Timeline:
   🎯 Sprint Duration: {len(self.visualizer.session_log)} events logged
        """
        
        self.console.print(report)
        self.console.print("\n[dim]Press any key to continue...[/dim]")
        self.menu_mode = False


async def interactive_demo():
    """Run the interactive demo with keyboard controls"""
    console = Console()
    visualizer = EnhancedVisualizer(console=console)
    keyboard = KeyboardHandler(visualizer, console)
    
    # Welcome screen
    console.clear()
    console.print(Panel(
        Align.center(
            Text.from_markup(
                "[bold cyan]Interactive AI Agent Visualization[/bold cyan]\n\n"
                "[yellow]Enhanced Features:[/yellow]\n"
                "• Scrollable chat history (↑↓ arrows)\n"
                "• Page navigation (PgUp/PgDn)\n"
                "• Interactive session menu (m)\n"
                "• Search functionality (/)\n"
                "• Real-time agent collaboration\n\n"
                "[green]Keyboard Controls:[/green]\n"
                "↑↓    - Scroll chat history\n"
                "PgUp/PgDn - Page through messages\n"
                "m     - Open session menu\n"
                "/     - Search chat (demo)\n"
                "c     - Clear search\n"
                "q     - Quit\n\n"
                "[dim]Starting interactive demo...[/dim]",
                justify="center"
            )
        ),
        title="Interactive Demo",
        border_style="blue",
        height=20
    ))
    await asyncio.sleep(5)
    
    # Start keyboard handler
    keyboard.start_keyboard_thread()
    
    # Track console messages and export file
    console_messages = []
    exported_file = None
    
    # Create initial layout
    layout = visualizer.create_layout(show_summary=False)
    
    with Live(
        layout,
        console=console,
        refresh_per_second=4,
        screen=True
    ) as live:
        try:
            # === QUICK SPRINT SIMULATION ===
            console_messages.append("🎯 Interactive Sprint Started")
            
            # Initialize agents
            for agent_name in ["Marcus Chen", "Emily Rodriguez", "Alex Thompson", "Jordan Kim"]:
                await visualizer.update_agent_activity(
                    agent_name, ActivityType.IDLE,
                    "Ready for interactive sprint", 0
                )
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(2)
            
            # === DEVELOPMENT SIMULATION ===
            console_messages.append("📋 Sprint Planning")
            
            await visualizer.send_message(
                "System", "Team",
                "🎯 Interactive Demo: Real-time E-Commerce Authentication",
                "announcement"
            )
            
            # Add multiple messages to demonstrate scrolling
            await visualizer.send_message(
                "Marcus Chen", "Team",
                "I'll handle the backend API architecture and JWT implementation",
                "planning"
            )
            
            await visualizer.send_message(
                "Emily Rodriguez", "Team", 
                "I'll create the React frontend with accessibility features",
                "planning"
            )
            
            await visualizer.send_message(
                "Alex Thompson", "Team",
                "I'll focus on security testing and performance validation",
                "planning"
            )
            
            await visualizer.send_message(
                "Jordan Kim", "Team",
                "I'll set up CI/CD pipelines and Kubernetes deployment",
                "planning"
            )
            
            visualizer.update_workflow("Interactive Sprint", [
                {"name": "Planning", "completed": True},
                {"name": "Development", "completed": False},
                {"name": "Testing", "completed": False},
                {"name": "Deployment", "completed": False}
            ])
            
            await visualizer.render_frame(layout)
            live.update(layout)
            await asyncio.sleep(3)
            
            # === ACTIVE DEVELOPMENT ===
            console_messages.append("⚙️ Active Development")
            
            # Marcus codes
            development_tasks = [
                ("Marcus Chen", "Setting up FastAPI project structure", 20),
                ("Marcus Chen", "Implementing JWT authentication service", 40),
                ("Emily Rodriguez", "Creating React authentication components", 30),
                ("Marcus Chen", "Adding OAuth2 social login integration", 60),
                ("Emily Rodriguez", "Building responsive login/signup forms", 50),
                ("Alex Thompson", "Setting up automated test framework", 35),
                ("Marcus Chen", "Implementing password reset functionality", 80),
                ("Emily Rodriguez", "Adding form validation and error handling", 70),
                ("Alex Thompson", "Running security vulnerability scans", 60),
                ("Jordan Kim", "Configuring Docker and Kubernetes manifests", 45)
            ]
            
            for agent, task, progress in development_tasks:
                await visualizer.update_agent_activity(
                    agent, ActivityType.CODING,
                    task, progress
                )
                
                # Add some messages during development
                if "OAuth2" in task:
                    await visualizer.send_message(
                        "Marcus Chen", "Emily Rodriguez",
                        "OAuth2 endpoints ready - check /api/auth/oauth for specs",
                        "handoff"
                    )
                elif "validation" in task:
                    await visualizer.send_message(
                        "Emily Rodriguez", "Alex Thompson",
                        "Frontend validation complete - ready for security testing",
                        "handoff"
                    )
                elif "vulnerability" in task:
                    await visualizer.send_message(
                        "Alex Thompson", "Team",
                        "Found 2 potential security issues - creating tickets",
                        "alert"
                    )
                    
                visualizer.metrics["lines_written"] += 12
                await visualizer.render_frame(layout)
                live.update(layout)
                
                # Process keyboard input
                await keyboard.process_keys()
                if not keyboard.running:
                    break
                    
                # Check for menu mode
                if keyboard.menu_mode:
                    menu_layout = visualizer.create_layout(show_menu=True)
                    await visualizer.render_frame(menu_layout)
                    live.update(menu_layout)
                    
                    # Wait for menu selection
                    while keyboard.menu_mode and keyboard.running:
                        await keyboard.process_keys()
                        await asyncio.sleep(0.1)
                        
                    # Return to normal layout
                    await visualizer.render_frame(layout)
                    live.update(layout)
                
                await asyncio.sleep(2)
                
                if not keyboard.running:
                    break
                
            # === TESTING PHASE ===
            console_messages.append("🔍 Testing & QA")
            
            testing_tasks = [
                ("Running comprehensive test suite", 75),
                ("Performing load testing", 85),
                ("Security penetration testing", 95),
                ("Generating test coverage report", 100)
            ]
            
            for task, progress in testing_tasks:
                await visualizer.update_agent_activity(
                    "Alex Thompson", ActivityType.TESTING,
                    task, progress
                )
                visualizer.metrics["tests_passed"] += 8
                if progress == 95:
                    visualizer.metrics["bugs_found"] += 1
                    
                await visualizer.render_frame(layout)
                live.update(layout)
                await keyboard.process_keys()
                
                if not keyboard.running or keyboard.menu_mode:
                    break
                    
                await asyncio.sleep(2)
                
            # === DEPLOYMENT ===
            console_messages.append("🚀 Production Deployment")
            
            await visualizer.update_agent_activity(
                "Jordan Kim", ActivityType.DEPLOYING,
                "Deploying to production with blue-green strategy", 100
            )
            
            visualizer.metrics["deployments"] = 1
            
            await visualizer.send_message(
                "Jordan Kim", "Team",
                "🎉 Production deployment successful! All health checks passing",
                "success"
            )
            
            # === COMPLETION ===
            console_messages.append("🎉 Interactive Sprint Complete")
            
            await visualizer.send_message(
                "System", "Team",
                "🎉 Interactive sprint complete! All objectives achieved",
                "announcement"
            )
            
            # Set all agents to completed
            for agent_name in ["Marcus Chen", "Emily Rodriguez", "Alex Thompson", "Jordan Kim"]:
                await visualizer.update_agent_activity(
                    agent_name, ActivityType.IDLE,
                    "Interactive sprint completed! 🎉", 100
                )
            
            visualizer.update_workflow("Interactive Sprint", [
                {"name": "Planning", "completed": True},
                {"name": "Development", "completed": True},
                {"name": "Testing", "completed": True},
                {"name": "Deployment", "completed": True}
            ])
            
            # Export session
            console_messages.append("💾 Session data exported")
            exported_file = visualizer.export_session_log()
            
            # Switch to summary layout
            summary_layout = visualizer.create_layout(show_summary=True)
            await visualizer.render_frame(summary_layout, console_messages, exported_file)
            live.update(summary_layout)
            
            console.print(f"\n[bold green]✨ Interactive demo complete![/bold green]")
            console.print(f"[yellow]Enhanced features demonstrated:[/yellow]")
            console.print(f"• Scrollable chat history with {len(visualizer.chat_manager.messages)} messages")
            console.print(f"• Agent action history tracking")
            console.print(f"• Real-time collaboration visualization")
            console.print(f"• Session export: {os.path.basename(exported_file)}")
            console.print(f"\n[cyan]Try the keyboard controls:[/cyan]")
            console.print(f"• ↑↓ to scroll through chat history")
            console.print(f"• 'm' to open interactive menu")
            console.print(f"• 'q' to quit")
            
            # Keep running with interactive controls
            while keyboard.running:
                await keyboard.process_keys()
                
                if keyboard.menu_mode:
                    menu_layout = visualizer.create_layout(show_menu=True)
                    await visualizer.render_frame(menu_layout)
                    live.update(menu_layout)
                    
                    while keyboard.menu_mode and keyboard.running:
                        await keyboard.process_keys()
                        await asyncio.sleep(0.1)
                        
                    await visualizer.render_frame(summary_layout, console_messages, exported_file)
                    live.update(summary_layout)
                else:
                    await visualizer.render_frame(summary_layout, console_messages, exported_file)
                    live.update(summary_layout)
                    
                await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            keyboard.running = False
            console.print(f"\n[yellow]Interactive demo interrupted by user[/yellow]")
            
    # Final message
    console.clear()
    console.print(Panel(
        Align.center(
            Text.from_markup(
                "[bold green]Interactive Demo Complete![/bold green]\n\n"
                "[cyan]Enhanced Features Demonstrated:[/cyan]\n"
                f"📜 {len(visualizer.chat_manager.messages)} chat messages with scrolling\n"
                f"📊 {len(visualizer.session_log)} events logged\n"
                f"⚙️ {sum(len(actions) for actions in visualizer.agent_actions.values())} agent actions tracked\n"
                f"💾 Complete session exported to JSON\n\n"
                "[yellow]The enhanced visualization system provides:[/yellow]\n"
                "• Scrollable chat history for full conversation review\n"
                "• Interactive session menu for post-completion analysis\n" 
                "• Real-time agent collaboration tracking\n"
                "• Professional keyboard-driven interface\n\n"
                "[bold cyan]Ready for production deployment! 🚀[/bold cyan]",
                justify="center"
            )
        ),
        height=16,
        border_style="green"
    ))


if __name__ == "__main__":
    try:
        asyncio.run(interactive_demo())
    except KeyboardInterrupt:
        print("\n\nInteractive demo ended.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()