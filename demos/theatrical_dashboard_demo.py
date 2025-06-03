#!/usr/bin/env python3
"""
Theatrical Dashboard Demo - Beautiful real-time agent monitoring

This demo showcases the theatrical dashboard with v3.1 agents,
combining the beautiful UI from v3.0 with the real agent architecture from v3.1.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.visualization.theatrical_dashboard import TheatricalDashboard


async def main():
    """Run the theatrical dashboard demo"""
    print("🎭 AIOSv3.1 Theatrical Dashboard Demo")
    print("=" * 50)
    print("This demo shows the beautiful theatrical dashboard design")
    print("integrated with v3.1's real agent architecture.")
    print("-" * 50)
    
    # Create and run dashboard
    dashboard = TheatricalDashboard()
    
    try:
        await dashboard.run()
    except KeyboardInterrupt:
        print("\n\n✨ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())