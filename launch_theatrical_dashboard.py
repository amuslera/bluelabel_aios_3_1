#!/usr/bin/env python3
"""
Main launcher for the Theatrical Dashboard in AIOSv3.1
This provides the beautiful v3.0 visualization with v3.1's production agents.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now we can import from the theatrical dashboard
from projects.theatrical_dashboard.theatrical_dashboard import TheatricalMonitoringApp
from projects.theatrical_dashboard.theatrical_orchestrator import TheatricalOrchestrator

def main():
    """Launch the theatrical dashboard with menu options."""
    print("🎭 AIOSv3.1 Theatrical Dashboard Launcher")
    print("=" * 50)
    print("\nThis combines:")
    print("  • v3.0's beautiful 3-tab visualization")
    print("  • v3.1's production-ready agents (Marcus, Emily, Alex, Jordan)")
    print("\nSelect mode:")
    print("1. Full Dashboard (Recommended)")
    print("2. Console Mode Only")
    print("3. Dashboard Only (no orchestration)")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            print("\n🚀 Launching full theatrical dashboard...")
            print("Note: This will show a real multi-agent project build")
            run_full_dashboard()
            break
        elif choice == "2":
            print("\n📺 Launching console mode...")
            run_console_only()
            break
        elif choice == "3":
            print("\n📊 Launching dashboard only...")
            run_dashboard_only()
            break
        elif choice == "4":
            print("\n👋 Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please enter 1-4.")

def run_full_dashboard():
    """Run both dashboard and orchestrator together."""
    asyncio.run(run_full_async())

async def run_full_async():
    """Async runner for full dashboard mode."""
    # Create the dashboard app
    app = TheatricalMonitoringApp()
    
    # Create the orchestrator
    orchestrator = TheatricalOrchestrator()
    
    # Run dashboard in background
    dashboard_task = asyncio.create_task(app.run_async())
    
    # Give dashboard time to start
    await asyncio.sleep(2)
    
    # Run orchestrator
    try:
        await orchestrator.run_demo()
    except KeyboardInterrupt:
        print("\n\n🛑 Demo interrupted by user")
    
    # Cancel dashboard
    dashboard_task.cancel()
    try:
        await dashboard_task
    except asyncio.CancelledError:
        pass

def run_console_only():
    """Run just the orchestrator in console mode."""
    from projects.theatrical_dashboard.theatrical_orchestrator import main as orchestrator_main
    orchestrator_main()

def run_dashboard_only():
    """Run just the dashboard without orchestration."""
    app = TheatricalMonitoringApp()
    app.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Theatrical dashboard closed")
        sys.exit(0)