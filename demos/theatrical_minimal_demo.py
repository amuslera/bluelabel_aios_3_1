#!/usr/bin/env python3
"""
Minimal Theatrical Dashboard Demo

This version works without requiring the full agent infrastructure,
perfect for quick demonstrations of the theatrical dashboard concept.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.visualization.theatrical_dashboard_minimal import MinimalTheatricalDashboard


async def main():
    """Run the minimal theatrical dashboard demo"""
    print("🎭 AIOSv3.1 Minimal Theatrical Dashboard")
    print("=" * 50)
    print("This demo shows the theatrical dashboard with mock agents.")
    print("No complex initialization required!")
    print("-" * 50)
    
    dashboard = MinimalTheatricalDashboard()
    
    try:
        await dashboard.run()
    except KeyboardInterrupt:
        print("\n\n✨ Demo ended by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())