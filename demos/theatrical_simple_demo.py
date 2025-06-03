#!/usr/bin/env python3
"""
Simple Theatrical Dashboard Demo - Uses mock agents for clean demonstration

This demo showcases the theatrical dashboard without requiring
full agent initialization, making it perfect for quick demos.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Use standalone demo which doesn't require agent initialization
from theatrical_demo_standalone import TheatricalDemo


async def main():
    """Run the simple theatrical demo"""
    print("🎭 AIOSv3.1 Simple Theatrical Dashboard")
    print("=" * 50)
    print("This demo shows the theatrical dashboard concept")
    print("with simulated agents (no complex initialization).")
    print("-" * 50)
    
    demo = TheatricalDemo()
    
    try:
        await demo.run()
    except KeyboardInterrupt:
        print("\n\n✨ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())