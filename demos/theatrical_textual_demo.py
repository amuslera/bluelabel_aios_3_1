#!/usr/bin/env python3
"""
Theatrical Dashboard Demo - v3.0 Style using Textual

This demo showcases the theatrical dashboard using Textual framework,
recreating the v3.0 design approach with a rich terminal UI.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Check if textual is installed
try:
    import textual
    print("✅ Textual is installed")
except ImportError:
    print("❌ Textual is not installed!")
    print("\nTo install Textual, run:")
    print("  pip3 install textual")
    print("\nTextual provides advanced terminal UI capabilities.")
    sys.exit(1)

from src.visualization.theatrical_dashboard_textual import TheatricalDashboard


def main():
    """Run the Textual theatrical dashboard"""
    print("🎭 AIOSv3.1 Theatrical Dashboard - v3.0 Style")
    print("=" * 50)
    print("This demo uses Textual for a rich terminal UI experience")
    print("similar to the original v3.0 dashboard design.")
    print("-" * 50)
    print("\nStarting dashboard...")
    print("(Press Ctrl+C to exit)")
    print("-" * 50)
    
    # Create and run the Textual app
    app = TheatricalDashboard()
    app.run()


if __name__ == "__main__":
    main()