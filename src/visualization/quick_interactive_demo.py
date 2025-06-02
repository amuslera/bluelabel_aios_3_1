#!/usr/bin/env python3
"""
Quick Interactive Demo - Showcases enhanced features
"""

import asyncio
import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

# Add src to path
sys.path.insert(0, '/Users/arielmuslera/Development/Projects/bluelabel-AIOSv3.1')

from src.visualization.enhanced_visualizer import EnhancedVisualizer, ActivityType


async def quick_demo():
    """Quick demonstration of enhanced features"""
    console = Console()
    visualizer = EnhancedVisualizer(console=console)
    
    # Clear screen and show welcome
    console.clear()
    console.print(Panel(
        Align.center(
            Text.from_markup(
                "[bold cyan]Quick Interactive Demo[/bold cyan]\n\n"
                "[yellow]Enhanced Features Showcase:[/yellow]\n"
                "• Scrollable chat history\n"
                "• Interactive session menu\n"
                "• Agent action tracking\n"
                "• Session export capability\n\n"
                "[green]Starting demo...[/green]",
                justify="center"
            )
        ),
        title="Enhanced Visualization",
        border_style="blue"
    ))
    await asyncio.sleep(3)
    
    # Add sample data
    console.print("\n[cyan]📝 Adding sample messages...[/cyan]")
    
    messages = [
        ("Marcus Chen", "Team", "🚀 Starting backend development"),
        ("Emily Rodriguez", "Team", "🎨 Creating beautiful UI components"),
        ("Alex Thompson", "Team", "🔍 Running comprehensive test suite"),
        ("Jordan Kim", "Team", "⚙️ Setting up CI/CD pipeline"),
        ("Marcus Chen", "Emily Rodriguez", "API endpoints ready for frontend integration"),
        ("Emily Rodriguez", "Marcus Chen", "Perfect! Frontend consuming your APIs now"),
        ("Alex Thompson", "Team", "Found 2 security issues - creating tickets"),
        ("Jordan Kim", "Team", "Production deployment successful! 🎉"),
        ("System", "Team", "🎯 Sprint completed successfully!"),
        ("Marcus Chen", "Team", "Great teamwork everyone! 👏"),
        ("Emily Rodriguez", "Team", "UI performance optimized ⚡"),
        ("Alex Thompson", "Team", "All tests passing ✅"),
        ("Jordan Kim", "Team", "Monitoring shows healthy metrics 📊"),
        ("System", "Team", "📈 Sprint metrics: 95% success rate"),
        ("Marcus Chen", "Team", "Ready for next sprint planning")
    ]
    
    for from_agent, to_agent, content in messages:
        await visualizer.send_message(from_agent, to_agent, content)
    
    console.print(f"✅ Added {len(messages)} messages")
    
    # Add agent activities
    console.print("\n[cyan]⚙️ Adding agent activities...[/cyan]")
    
    activities = [
        ("Marcus Chen", ActivityType.CODING, "Implementing authentication service", 85),
        ("Emily Rodriguez", ActivityType.DESIGNING, "Creating responsive login forms", 92),
        ("Alex Thompson", ActivityType.TESTING, "Running security vulnerability scans", 78),
        ("Jordan Kim", ActivityType.DEPLOYING, "Blue-green production deployment", 100)
    ]
    
    for agent, activity, desc, progress in activities:
        await visualizer.update_agent_activity(agent, activity, desc, progress)
    
    console.print(f"✅ Added activities for {len(activities)} agents")
    
    # Test chat scrolling
    console.print("\n[cyan]📜 Testing chat scroll functionality...[/cyan]")
    
    total_messages = len(visualizer.chat_manager.messages)
    visible_count = visualizer.chat_manager.max_visible
    
    console.print(f"   Total messages: {total_messages}")
    console.print(f"   Visible at once: {visible_count}")
    console.print(f"   Scroll position: {visualizer.chat_manager.scroll_offset}")
    
    # Simulate scrolling
    console.print("\n   🔄 Simulating scroll operations...")
    
    # Scroll to top
    visualizer.chat_manager.scroll_to_top()
    console.print(f"   After scroll to top: offset = {visualizer.chat_manager.scroll_offset}")
    
    # Scroll down a few lines
    visualizer.chat_manager.scroll_down(3)
    console.print(f"   After scroll down 3: offset = {visualizer.chat_manager.scroll_offset}")
    
    # Page down
    visualizer.chat_manager.page_down()
    console.print(f"   After page down: offset = {visualizer.chat_manager.scroll_offset}")
    
    # Back to bottom
    visualizer.chat_manager.scroll_to_bottom()
    console.print(f"   After scroll to bottom: offset = {visualizer.chat_manager.scroll_offset}")
    
    # Test search
    console.print("\n[cyan]🔍 Testing search functionality...[/cyan]")
    
    search_terms = ["security", "API", "test"]
    for term in search_terms:
        visualizer.chat_manager.search(term)
        matches = len(visualizer.chat_manager.filtered_messages)
        console.print(f"   Search '{term}': {matches} matches found")
    
    # Clear search
    visualizer.chat_manager.clear_search()
    console.print("   Search cleared")
    
    # Export session
    console.print("\n[cyan]💾 Testing session export...[/cyan]")
    
    export_file = visualizer.export_session_log()
    file_size = os.path.getsize(export_file)
    
    console.print(f"✅ Session exported successfully!")
    console.print(f"   File: {os.path.basename(export_file)}")
    console.print(f"   Size: {file_size:,} bytes")
    
    # Show session menu
    console.print("\n[cyan]📋 Displaying session menu...[/cyan]")
    
    menu_panel = visualizer.session_menu.show_menu()
    console.print(menu_panel)
    
    # Final summary
    console.print("\n" + "="*60)
    console.print("[bold green]🎉 Enhanced Features Demo Complete![/bold green]")
    console.print("\n[yellow]📊 Demo Statistics:[/yellow]")
    console.print(f"   📨 Messages: {len(visualizer.chat_manager.messages)}")
    console.print(f"   ⚙️ Agent Actions: {sum(len(actions) for actions in visualizer.agent_actions.values())}")
    console.print(f"   📋 Events Logged: {len(visualizer.session_log)}")
    console.print(f"   💾 Export File Size: {file_size:,} bytes")
    
    console.print("\n[bold cyan]✨ Enhanced Visualization System Ready![/bold cyan]")
    console.print("\n[yellow]Key Features Demonstrated:[/yellow]")
    console.print("  🔄 Scrollable chat history with navigation controls")
    console.print("  📋 Interactive session menu with multiple options")
    console.print("  🎯 Agent action history tracking (last 3-4 actions)")
    console.print("  💾 Complete session export to JSON")
    console.print("  🔍 Chat search and filtering functionality")
    console.print("  🎨 Professional Rich terminal interface")
    
    console.print(f"\n[dim]Session data exported to: {os.path.basename(export_file)}[/dim]")


if __name__ == "__main__":
    try:
        asyncio.run(quick_demo())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()