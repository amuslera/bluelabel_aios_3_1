#!/usr/bin/env python3
"""
Launch Real Demo - Choose between different demo options
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
    
    # Options table
    table = Table(title="Available Demos", box=box.ROUNDED)
    table.add_column("#", style="cyan", width=3)
    table.add_column("Demo", style="green")
    table.add_column("Description", style="white")
    table.add_column("Duration", style="yellow")
    
    table.add_row("1", "End-to-End Demo", "Complete flow: Human request → CTO consultation → Build → Delivery", "~20 min")
    table.add_row("2", "Task Management Build", "Direct build of task management system with all agents", "~15 min")
    table.add_row("3", "Interactive CTO Mode", "Interactive consultation with project customization", "~25 min")
    table.add_row("4", "Theatrical Dashboard", "Visual dashboard showing agent collaboration", "~10 min")
    table.add_row("5", "Quick Test", "Minimal demo to test agent connectivity", "~5 min")
    table.add_row("6", "Simple Working", "Simulated agent collaboration (no LLM calls)", "~30 sec")
    table.add_row("7", "Auto Enhanced", "Clean demo with chat - starts automatically", "~2 min")
    table.add_row("8", "Polished", "Professional demo with fixed layout", "~2 min")
    table.add_row("9", "Final", "Production-ready demo with all fixes", "~2 min")
    
    console.print(table)
    console.print()
    
    choice = Prompt.ask("Select demo to run", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"], default="9")
    
    console.print()
    
    if choice == "1":
        console.print("[bold green]Launching End-to-End Demo...[/]")
        os.system("python3 demo_end_to_end.py")
    elif choice == "2":
        console.print("[bold green]Launching Task Management Build Demo...[/]")
        os.system("python3 scripts/task_management_demo.py")
    elif choice == "3":
        console.print("[bold green]Launching Interactive CTO Demo...[/]")
        os.system("python3 scripts/demo_orchestrator.py")
    elif choice == "4":
        console.print("[bold green]Launching Theatrical Dashboard...[/]")
        os.system("python3 demos/theatrical_minimal_demo.py")
    elif choice == "5":
        console.print("[bold green]Launching Quick Test Demo...[/]")
        os.system("python3 scripts/demo_orchestrator_simple.py")
    elif choice == "6":
        console.print("[bold green]Launching Simple Working Demo...[/]")
        os.system("python3 demo_working_simple.py")
    elif choice == "7":
        console.print("[bold green]Launching Auto Enhanced Demo...[/]")
        os.system("python3 demo_auto_enhanced.py")
    elif choice == "8":
        console.print("[bold green]Launching Polished Demo...[/]")
        os.system("python3 demo_polished.py")
    elif choice == "9":
        console.print("[bold green]Launching Final Demo...[/]")
        os.system("python3 demo_final.py")

if __name__ == "__main__":
    main()