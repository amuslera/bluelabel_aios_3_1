#!/usr/bin/env python3
"""
Launch script for the theatrical dashboard in v3.1
"""

import asyncio
import sys
from pathlib import Path

# Add theatrical dashboard to path
sys.path.insert(0, str(Path(__file__).parent))

from theatrical_dashboard import TheatricalMonitoringApp
from theatrical_orchestrator import TheatricalOrchestrator

async def main():
    """Run the theatrical monitoring dashboard."""
    # Create and run the app
    app = TheatricalMonitoringApp()
    
    # Run the orchestrator in the background
    orchestrator = TheatricalOrchestrator()
    
    # Create tasks for both
    dashboard_task = asyncio.create_task(app.run_async())
    orchestrator_task = asyncio.create_task(orchestrator.run_demo())
    
    # Wait for both to complete
    await asyncio.gather(dashboard_task, orchestrator_task)

if __name__ == "__main__":
    print("🎭 Launching AIOSv3.1 Theatrical Dashboard...")
    print("This shows the v3.0 visualization with v3.1 agents")
    asyncio.run(main())
