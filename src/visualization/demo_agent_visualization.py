#!/usr/bin/env python3
"""
Agent Visualization Demo

Interactive demonstration of the AI agent visualization system.
Shows realistic agent collaboration with theatrical pacing.
"""

import asyncio
import sys
from datetime import datetime
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align
from rich.text import Text

# Add src to path for imports
sys.path.insert(0, '/Users/arielmuslera/Development/Projects/bluelabel-AIOSv3.1')

from src.visualization.agent_visualizer import AgentVisualizer
from src.visualization.activity_simulator import ActivitySimulator
from src.visualization.visualization_config import VisualizationPresets
from src.visualization.code_visualization import CodeVisualizer, LiveCodeSession


class InteractiveDemo:
    """Interactive visualization demo with keyboard controls"""
    
    def __init__(self):
        self.console = Console()
        self.config = VisualizationPresets.demo_mode()
        self.visualizer = AgentVisualizer(config=self.config)
        self.simulator = ActivitySimulator(self.visualizer)
        self.code_viz = CodeVisualizer()
        self.code_session = LiveCodeSession(self.code_viz)
        self.running = True
        self.paused = False
        
    def create_help_panel(self) -> Panel:
        """Create help panel with controls"""
        help_text = Text()
        help_text.append("Controls: ", style="bold yellow")
        help_text.append("SPACE", style="bold cyan")
        help_text.append(" Pause/Resume  ", style="white")
        help_text.append("←/→", style="bold cyan")
        help_text.append(" Speed Control  ", style="white")
        help_text.append("Q", style="bold cyan")
        help_text.append(" Quit", style="white")
        
        speed = self.visualizer.pacing.speed_multiplier
        help_text.append(f"\nSpeed: {speed:.1f}x", style="green")
        if self.paused:
            help_text.append("  [PAUSED]", style="bold red blink")
            
        return Panel(
            Align.center(help_text),
            border_style="blue",
            height=3
        )
        
    def create_layout(self) -> Layout:
        """Create the full demo layout"""
        layout = Layout()
        
        # Create the visualization
        viz_layout = self.visualizer.create_layout()
        
        # Add help panel at the bottom
        help_panel = self.create_help_panel()
        
        # Combine layouts
        layout.split_column(
            Layout(viz_layout, name="main", ratio=9),
            Layout(help_panel, name="help", ratio=1)
        )
        
        return layout
        
    async def handle_keyboard(self):
        """Handle keyboard input for demo control"""
        import termios
        import tty
        
        # Save terminal settings
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            # Set terminal to raw mode
            tty.setraw(sys.stdin.fileno())
            
            while self.running:
                # Non-blocking key check
                import select
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1)
                    
                    if key == 'q' or key == 'Q':
                        self.running = False
                    elif key == ' ':
                        self.paused = not self.paused
                    elif key == '\x1b':  # Escape sequence
                        # Read the rest of the arrow key sequence
                        sys.stdin.read(2)  # Skip [A, [B, [C, or [D
                        next_char = sys.stdin.read(1)
                        if next_char == 'C':  # Right arrow
                            self.visualizer.pacing.speed_multiplier = min(
                                2.0, self.visualizer.pacing.speed_multiplier + 0.1
                            )
                        elif next_char == 'D':  # Left arrow
                            self.visualizer.pacing.speed_multiplier = max(
                                0.1, self.visualizer.pacing.speed_multiplier - 0.1
                            )
                            
                await asyncio.sleep(0.1)
                
        finally:
            # Restore terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
    async def run_demo(self):
        """Run the interactive demo"""
        # Start keyboard handler
        keyboard_task = asyncio.create_task(self.handle_keyboard())
        
        # Initialize agents
        agents = [
            ("Marcus Chen", "Backend Developer", "cyan"),
            ("Emily Rodriguez", "Frontend Developer", "magenta"),
            ("Alex Thompson", "QA Engineer", "yellow"),
            ("Jordan Kim", "DevOps Engineer", "green")
        ]
        
        for name, role, color in agents:
            self.visualizer.add_agent(name, role, color)
            
        # Start the live display
        with Live(
            self.create_layout(),
            console=self.console,
            refresh_per_second=10,
            screen=True
        ) as live:
            try:
                # Run simulation phases
                phases = [
                    ("Planning Phase", self.simulator.simulate_planning_phase),
                    ("Development Phase", self.simulator.simulate_development_phase),
                    ("Testing Phase", self.simulator.simulate_testing_phase),
                    ("Deployment Phase", self.simulator.simulate_deployment_phase),
                    ("Incident Response", self.simulator.simulate_incident_response)
                ]
                
                for phase_name, phase_func in phases:
                    if not self.running:
                        break
                        
                    # Announce phase
                    await self.visualizer.send_message(
                        "System",
                        "Team",
                        f"🎬 Starting {phase_name}",
                        "announcement"
                    )
                    
                    # Run phase
                    await phase_func()
                    
                    # Update display
                    live.update(self.create_layout())
                    
                    # Pause between phases
                    await asyncio.sleep(2)
                    
                # Keep running until user quits
                while self.running:
                    live.update(self.create_layout())
                    await asyncio.sleep(0.1)
                    
                    # Pause simulation if requested
                    while self.paused and self.running:
                        live.update(self.create_layout())
                        await asyncio.sleep(0.1)
                        
            except KeyboardInterrupt:
                self.running = False
                
        # Clean up
        keyboard_task.cancel()
        
        # Show farewell message
        self.console.clear()
        farewell = Panel(
            Align.center(
                Text("Thanks for watching the AI Agent Visualization Demo! 🎬", 
                     style="bold cyan"),
                vertical="middle"
            ),
            title="Demo Complete",
            border_style="green",
            height=5
        )
        self.console.print(farewell)


async def main():
    """Main entry point"""
    console = Console()
    
    # Show welcome screen
    welcome = Panel(
        Align.center(
            Text.from_markup(
                "[bold cyan]AI Agent Visualization Demo[/bold cyan]\n\n"
                "[yellow]Watch as our AI development team collaborates![/yellow]\n\n"
                "[dim]Press any key to start...[/dim]",
                justify="center"
            ),
            vertical="middle"
        ),
        title="Welcome",
        border_style="blue",
        height=10
    )
    
    console.clear()
    console.print(welcome)
    
    # Wait for keypress
    import termios
    import tty
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    # Run the demo
    demo = InteractiveDemo()
    await demo.run_demo()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError running demo: {e}")
        import traceback
        traceback.print_exc()