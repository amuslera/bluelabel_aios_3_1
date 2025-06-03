#!/usr/bin/env python3
"""
Simple launcher for the theatrical dashboard that works with v3.1
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the adapter orchestrator
from projects.theatrical_dashboard.v31_orchestrator_adapter import SimpleTheatricalOrchestrator

def main():
    """Run a simple theatrical demo"""
    print("🎭 AIOSv3.1 Theatrical Demo (Simplified)")
    print("=" * 50)
    print("\nThis demonstrates v3.1 agents in theatrical mode")
    print("Note: Using simplified orchestrator for compatibility\n")
    
    orchestrator = SimpleTheatricalOrchestrator(
        event_callback=lambda e: print(f"[{e['type']}] {e['agent_id']}: {e['message']}")
    )
    
    try:
        asyncio.run(orchestrator.run_demo())
    except KeyboardInterrupt:
        print("\n\n🛑 Demo interrupted")
    
    print("\n✅ Demo complete!")

if __name__ == "__main__":
    main()