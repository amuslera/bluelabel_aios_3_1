#!/usr/bin/env python3
"""
Control Center Demo - Shows what the UI would look like

This is a static demo that doesn't require textual to be installed.
"""

import time
import sys
from datetime import datetime

def clear_screen():
    """Clear the terminal screen."""
    print("\033[2J\033[H", end='')

def print_colored(text, color):
    """Print colored text."""
    colors = {
        'green': '\033[92m',
        'blue': '\033[94m',
        'yellow': '\033[93m',
        'magenta': '\033[95m',
        'red': '\033[91m',
        'cyan': '\033[96m',
        'reset': '\033[0m'
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")

def draw_box(title, content, color='reset', width=40, height=10):
    """Draw a box with content."""
    print_colored("┌" + "─" * (width-2) + "┐", color)
    print_colored(f"│ {title:^{width-4}} │", color)
    print_colored("├" + "─" * (width-2) + "┤", color)
    
    lines = content.split('\n')
    for i in range(height-4):
        if i < len(lines):
            line = lines[i][:width-4]
            print_colored(f"│ {line:<{width-4}} │", color)
        else:
            print_colored("│" + " " * (width-2) + "│", color)
    
    print_colored("└" + "─" * (width-2) + "┘", color)

def show_control_center():
    """Display the control center UI mockup."""
    clear_screen()
    
    # Header
    print_colored("=" * 85, 'cyan')
    print_colored(f"  AIOSv3 CONTROL CENTER - {datetime.now().strftime('%H:%M:%S')}  ".center(85), 'cyan')
    print_colored("=" * 85, 'cyan')
    print()
    
    # Create content for each panel
    agents_content = """Status  Agent         Role      Progress
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟢     Marcus Chen   backend    35%
🟡     Alex Rivera   frontend    0%
🟢     Diana Martinez monitor    80%

[Launch Agent] [Stop] [Restart]"""
    
    monitor_content = """10:45:23 Marcus: file_operation
10:45:25 Marcus: ✅ success
10:45:30 Diana: git_operation
10:45:32 Backend: WebSocket connected
10:45:35 Frontend: Component rendered
10:45:40 Monitor: Metrics collected
10:45:42 System: All agents healthy"""
    
    tasks_content = """ID      Title                    Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MON-002 Add WebSocket integration 🔵 Pending
MON-003 Implement error handling  ⚪ Backlog
UI-002  Add progress animations   🟢 Active
TEST-001 Write integration tests  🔵 Pending

[Assign Task] [Create Task]"""
    
    pr_content = """PR #2: Control Center UI
Author: Alex Rivera
Branch: feature/control-center-ui
Files: 4 changed

Ready for review
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Approve] [Request Changes] [View Diff]"""
    
    # Draw the grid layout
    # Top row
    cursor_y = 6
    sys.stdout.write(f"\033[{cursor_y};1H")
    draw_box("🎭 Agent Orchestra", agents_content, 'green', 42, 11)
    
    sys.stdout.write(f"\033[{cursor_y};44H")
    draw_box("📊 Activity Monitor", monitor_content, 'blue', 42, 11)
    
    # Bottom row
    cursor_y = 18
    sys.stdout.write(f"\033[{cursor_y};1H")
    draw_box("📋 Task Manager", tasks_content, 'yellow', 42, 11)
    
    sys.stdout.write(f"\033[{cursor_y};44H")
    draw_box("🔍 PR Review", pr_content, 'magenta', 42, 11)
    
    # Footer
    sys.stdout.write(f"\033[30;1H")
    print_colored("─" * 85, 'cyan')
    print_colored(" [q]uit [a]gent [p]r-review [t]ask [r]efresh [m]onitor ", 'cyan')
    print()

def animate_activity():
    """Show animated activity in the monitor."""
    activities = [
        ("Backend", "Compiling TypeScript files", "blue"),
        ("Frontend", "Hot reload triggered", "green"),
        ("Monitor", "CPU usage: 23%", "yellow"),
        ("System", "WebSocket message received", "cyan"),
        ("Backend", "API endpoint registered", "blue"),
        ("Tester", "Running test suite", "magenta"),
        ("System", "All tests passed ✅", "green"),
    ]
    
    for i in range(3):
        for actor, message, color in activities:
            # Update just the monitor section
            sys.stdout.write(f"\033[10;46H")
            timestamp = datetime.now().strftime('%H:%M:%S')
            print_colored(f"{timestamp} {actor}: {message:<25}", color)
            time.sleep(0.5)

def main():
    """Run the control center demo."""
    print("\n🎭 CONTROL CENTER DEMO")
    print("=" * 50)
    print("This shows what the control center looks like.")
    print("The real version requires: pip install textual")
    print("=" * 50)
    
    input("\nPress Enter to see the UI mockup...")
    
    try:
        # Show static mockup
        show_control_center()
        
        print("\n📌 This is what the control center provides:")
        print("  • Real-time agent monitoring")
        print("  • Task assignment and tracking")
        print("  • PR review without leaving terminal")
        print("  • Unified interface for all operations")
        
        animate = input("\nWould you like to see it animated? (y/n): ")
        if animate.lower() == 'y':
            show_control_center()
            print("\n🎬 Showing live activity simulation...")
            time.sleep(1)
            animate_activity()
        
        print("\n✨ To run the real interactive version:")
        print("  1. pip install textual rich aiohttp")
        print("  2. ./run_control_center.py")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted.")

if __name__ == "__main__":
    main()