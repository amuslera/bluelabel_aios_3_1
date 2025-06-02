#!/usr/bin/env python3
"""
Polished Demo - Clean, focused, and actually useful
"""

import asyncio
import sys
import os
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.layout import Layout
from rich import box
from rich.table import Table

# Add src to path
sys.path.insert(0, '/Users/arielmuslera/Development/Projects/bluelabel-AIOSv3.1')

from src.visualization.improved_visualizer import ImprovedVisualizer, ActivityType


class PolishedVisualizer(ImprovedVisualizer):
    """Polished visualizer with useful features only"""
    
    def create_layout(self, show_menu=False):
        """Create simplified layout"""
        layout = Layout()
        
        if show_menu:
            # Layout with menu
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="body", ratio=3),
                Layout(name="menu", size=10),
                Layout(name="footer", size=3)
            )
        else:
            # Layout without menu
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="body", ratio=1),
                Layout(name="footer", size=3)
            )
        
        # Body split into 3 columns
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
        
    def render_menu_panel(self) -> Panel:
        """Render focused menu panel"""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Option", style="white", width=50)
        
        table.add_row("[bold green]🎉 Sprint Complete! What would you like to do?[/bold green]")
        table.add_row("")
        table.add_row("[bold cyan]1.[/bold cyan] 💾 Export full session data (JSON)")
        table.add_row("[bold cyan]2.[/bold cyan] 📊 Generate sprint report (Markdown)") 
        table.add_row("[bold cyan]3.[/bold cyan] 🔄 Run another sprint")
        table.add_row("[bold cyan]4.[/bold cyan] 🚀 Exit")
        table.add_row("")
        table.add_row("[dim]Metrics and chat history are visible above[/dim]")
        
        return Panel(
            table,
            title="💬 Post-Sprint Options",
            border_style="green",
            box=box.ROUNDED
        )
        
    def get_meaningful_events(self):
        """Extract meaningful events from session log"""
        meaningful = []
        for event in self.session_log:
            if event["event_type"] == "message":
                data = event["data"]
                if data.get("from") != "System":
                    meaningful.append(f"{data['from']} → {data['to']}: {data['content'][:50]}...")
            elif event["event_type"] == "activity_update":
                data = event["data"]
                if "complete" in data.get("description", "").lower():
                    meaningful.append(f"{data['agent']}: {data['description']}")
        return meaningful[-10:]  # Last 10 meaningful events


async def run_demo(visualizer, layout, live):
    """Run the demo sequence"""
    
    # Initialize agents
    for agent_name in ["Marcus Chen", "Emily Rodriguez", "Alex Thompson", "Jordan Kim"]:
        await visualizer.update_agent_activity(
            agent_name, ActivityType.IDLE, "Ready for sprint assignment", 0
        )
    
    await visualizer.render_frame(layout)
    live.update(layout)
    await asyncio.sleep(1)
    
    # Quick sprint
    await visualizer.send_message("System", "Team", "🎯 Sprint Goal: Build E-Commerce Authentication System", "announcement")
    
    visualizer.update_workflow("Authentication Sprint", [
        {"name": "Requirements & Analysis", "completed": False},
        {"name": "Backend Development", "completed": False},
        {"name": "Frontend Development", "completed": False},
        {"name": "Testing & QA", "completed": False},
        {"name": "Deployment", "completed": False}
    ])
    
    # Quick phases
    phases = [
        ("Marcus Chen", "Gathering authentication requirements", "Requirements complete: JWT auth, OAuth2 social login"),
        ("Marcus Chen", "Building FastAPI backend", "Backend API complete! Swagger docs available"),
        ("Emily Rodriguez", "Creating React components", "Frontend complete with responsive design"),
        ("Alex Thompson", "Running comprehensive tests", "Testing complete! 35 tests passed, 4 issues found"),
        ("Jordan Kim", "Production deployment", "🎉 SPRINT COMPLETE! Authentication system live!")
    ]
    
    for i, (agent, activity, completion_msg) in enumerate(phases):
        await visualizer.update_agent_activity(agent, ActivityType.CODING, activity, 100)
        await visualizer.send_message(agent, "Team", completion_msg)
        
        # Update workflow
        completed_items = []
        for j, item_name in enumerate(["Requirements & Analysis", "Backend Development", "Frontend Development", "Testing & QA", "Deployment"]):
            completed_items.append({"name": item_name, "completed": j <= i})
        visualizer.update_workflow("Authentication Sprint", completed_items)
        
        visualizer.metrics["lines_written"] += 50
        if "test" in activity.lower():
            visualizer.metrics["tests_passed"] += 7
            visualizer.metrics["bugs_found"] += 1
        if "deployment" in activity.lower():
            visualizer.metrics["deployments"] = 1
        
        await visualizer.render_frame(layout)
        live.update(layout)
        await asyncio.sleep(1.5)
    
    # Final completion states
    for agent_name in ["Marcus Chen", "Emily Rodriguez", "Alex Thompson", "Jordan Kim"]:
        await visualizer.update_agent_activity(agent_name, ActivityType.IDLE, "Sprint completed successfully! 🎉", 100)
    
    await visualizer.render_frame(layout)
    live.update(layout)
    
    return visualizer.export_session_log()


def generate_sprint_report(visualizer, exported_file):
    """Generate a markdown sprint report"""
    report = f"""# Sprint Report - E-Commerce Authentication System

## Summary
- **Duration**: ~10 seconds (simulated 2-week sprint)
- **Team**: 4 engineers
- **Result**: ✅ Successfully deployed to production

## Metrics
- 📝 **Lines of Code**: {visualizer.metrics['lines_written']}
- ✅ **Tests Passed**: {visualizer.metrics['tests_passed']}
- 🐛 **Issues Found**: {visualizer.metrics['bugs_found']}
- 🚀 **Deployments**: {visualizer.metrics['deployments']}

## Key Deliverables
1. JWT-based authentication system
2. OAuth2 social login integration
3. Multi-factor authentication support
4. Comprehensive test coverage
5. Production-ready deployment

## Team Contributions
- **Marcus Chen**: Requirements analysis, backend API development
- **Emily Rodriguez**: Frontend components and responsive design
- **Alex Thompson**: Testing suite and security analysis
- **Jordan Kim**: Production deployment and monitoring

## Next Steps
- Monitor production metrics
- Gather user feedback
- Plan Phase 2 features (biometric login, SSO)

---
*Generated from session: {os.path.basename(exported_file)}*
"""
    
    # Save to data/reports directory
    os.makedirs("data/reports", exist_ok=True)
    base_name = os.path.basename(exported_file).replace('.json', '_report.md')
    filename = f"data/reports/{base_name}"
    with open(filename, 'w') as f:
        f.write(report)
    return filename


async def polished_demo():
    """Polished demo with useful features only"""
    
    while True:  # Allow restarting
        console = Console()
        visualizer = PolishedVisualizer(console=console)
        
        # Welcome screen
        console.clear()
        console.print(Panel(
            Align.center(
                Text.from_markup(
                    "[bold cyan]AI Team Sprint Visualization[/bold cyan]\n\n"
                    "[yellow]Watch your AI team complete a sprint:[/yellow]\n"
                    "• See real-time collaboration\n"
                    "• Track progress and metrics\n"
                    "• Export results when complete\n\n"
                    "[green]Starting sprint simulation...[/green]",
                    justify="center"
                )
            ),
            title="Welcome",
            border_style="blue",
            height=12
        ))
        await asyncio.sleep(3)
        
        # Run the demo
        console.clear()
        layout = visualizer.create_layout(show_menu=False)
        
        with Live(layout, console=console, refresh_per_second=6) as live:
            try:
                exported_file = await run_demo(visualizer, layout, live)
                
                # Switch to menu layout
                menu_layout = visualizer.create_layout(show_menu=True)
                await visualizer.render_frame(menu_layout)
                menu_layout["menu"].update(visualizer.render_menu_panel())
                live.update(menu_layout)
                
                # Keep showing for a moment
                await asyncio.sleep(2)
                
            except KeyboardInterrupt:
                console.print(f"\n🚀 Demo interrupted.")
                return
        
        # Interface stays visible above, menu works below
        console.print()  # Just one line space
        
        # Interactive menu loop
        while True:
            try:
                choice = console.input("[bold green]Choose an option (1-4): [/bold green]").strip()
                
                if choice == "1":
                    # Export session data
                    file_size = os.path.getsize(exported_file)
                    console.print(f"\n✅ Session data already exported:")
                    console.print(f"   📄 File: [cyan]{exported_file}[/cyan]")
                    console.print(f"   📊 Size: [yellow]{file_size:,} bytes[/yellow]")
                    console.print(f"   📋 Events: [green]{len(visualizer.session_log)} total[/green]")
                    
                elif choice == "2":
                    # Generate sprint report
                    report_file = generate_sprint_report(visualizer, exported_file)
                    console.print(f"\n✅ Sprint report generated:")
                    console.print(f"   📄 File: [cyan]{report_file}[/cyan]")
                    console.print(f"   📝 Format: [yellow]Markdown[/yellow]")
                    console.print(f"   📊 Ready for sharing!")
                        
                elif choice == "3":
                    # Re-run demo
                    console.print("[yellow]🔄 Starting new sprint...[/yellow]")
                    await asyncio.sleep(1)
                    break
                    
                elif choice == "4":
                    # Exit
                    console.print("\n[green]👋 Thanks for using AI Team Visualization![/green]")
                    console.print("[dim]Your sprint results are saved above.[/dim]")
                    return
                    
                else:
                    console.print(f"[red]Please enter 1-4.[/red]")
                    
            except KeyboardInterrupt:
                console.print(f"\n[yellow]Goodbye![/yellow]")
                return


if __name__ == "__main__":
    try:
        asyncio.run(polished_demo())
    except KeyboardInterrupt:
        print("\nBye!")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()