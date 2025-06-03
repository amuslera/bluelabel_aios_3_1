#!/usr/bin/env python3
"""
AIOSv3.1 Demo Launcher - Simplified with only working demos
"""

import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box

console = Console()

def main():
    console.clear()
    
    # Header
    console.print(Panel.fit(
        "🚀 AIOSv3.1 Demo Launcher",
        style="bold blue",
        box=box.DOUBLE
    ))
    console.print()
    
    # Demo options
    table = Table(title="Available Demos", box=box.ROUNDED)
    table.add_column("#", style="cyan", width=3)
    table.add_column("Demo", style="green")
    table.add_column("Description", style="white")
    table.add_column("Duration", style="yellow")
    
    table.add_row("1", "Full Demo", "Complete AI team collaboration with chat and metrics", "~2 min")
    table.add_row("2", "Quick Test", "Simple visualization of agent collaboration", "~30 sec")
    table.add_row("3", "Task Management", "Build a complete task management system", "~3 min")
    
    console.print(table)
    console.print()
    
    # Note about other demos
    console.print("[dim]Note: Legacy demos have been archived. Use launch_real_demo.py for experimental versions.[/]")
    console.print()
    
    choice = Prompt.ask("Select demo to run", choices=["1", "2", "3"], default="1")
    
    console.print()
    
    if choice == "1":
        console.print("[bold green]Launching Full Demo...[/]")
        console.print("[dim]Watch our AI team build a complete application![/]\n")
        os.system("python3 demo_final.py")
    elif choice == "2":
        console.print("[bold green]Launching Quick Test Demo...[/]")
        console.print("[dim]A simple visualization of agent collaboration[/]\n")
        os.system("python3 demo_working_simple.py")
    elif choice == "3":
        console.print("[bold green]Launching Task Management Demo...[/]")
        console.print("[dim]See the agents build a real task management system[/]\n")
        os.system("python3 scripts/task_management_demo.py")

if __name__ == "__main__":
    main()