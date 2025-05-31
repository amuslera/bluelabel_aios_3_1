#!/usr/bin/env python3
"""
Launch the Theatrical Development Show
Opens each agent in its own terminal window for the full experience
"""

import subprocess
import sys
import time
import platform

def launch_terminal(title: str, command: str):
    """Launch a command in a new terminal window."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        # Use AppleScript to open Terminal with specific title and command
        script = f'''
        tell application "Terminal"
            do script "{command}"
            set current settings of selected tab of window 1 to settings set "Ocean"
            set custom title of selected tab of window 1 to "{title}"
        end tell
        '''
        subprocess.run(["osascript", "-e", script])
    
    elif system == "Linux":
        # Try different terminal emulators
        terminals = [
            ["gnome-terminal", "--title", title, "--", "bash", "-c", f"{command}; read -p 'Press enter to close'"],
            ["xterm", "-title", title, "-e", f"{command}; read -p 'Press enter to close'"],
            ["konsole", "--title", title, "-e", "bash", "-c", f"{command}; read -p 'Press enter to close'"]
        ]
        
        for term_cmd in terminals:
            try:
                subprocess.run(term_cmd)
                break
            except FileNotFoundError:
                continue
    
    elif system == "Windows":
        # Windows Terminal or CMD
        subprocess.run(["start", title, "cmd", "/k", command], shell=True)

def main():
    """Launch the theatrical show."""
    print("🎭 Welcome to the Theatrical Development Show!")
    print("=" * 50)
    print("\nThis will open 4 terminal windows, each showing")
    print("an AI agent working at a pace you can follow.\n")
    
    agents = [
        ("🏗️ Sarah - Architect", "architect"),
        ("⚙️ Marcus - Backend", "backend"),
        ("🎨 Alex - Frontend", "frontend"),
        ("🔍 Priya - Tester", "tester")
    ]
    
    print("Agents to launch:")
    for name, _ in agents:
        print(f"  • {name}")
    
    print("\nEach agent will:")
    print("  • Introduce themselves")
    print("  • Show their thinking process")
    print("  • Type code at readable speed")
    print("  • Explain their decisions")
    print("  • Collaborate with the team\n")
    
    input("Press Enter to start the show...")
    
    print("\n🚀 Launching agents...\n")
    
    # Launch each agent in its own terminal
    for i, (title, role) in enumerate(agents):
        print(f"Opening terminal for {title}...")
        command = f"cd {sys.path[0]} && python3 theatrical_agents.py {role}"
        launch_terminal(title, command)
        time.sleep(2)  # Stagger launches for effect
    
    print("\n✨ All agents launched!")
    print("\nWatch each terminal to see the agents at work.")
    print("Notice how each has their own personality and style!")
    print("\n💡 Tip: Arrange the windows so you can see all four.")

if __name__ == "__main__":
    main()