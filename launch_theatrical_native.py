#!/usr/bin/env python3
"""
Launch the native v3.1 theatrical dashboard
Built from scratch to work with v3.1's architecture
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from projects.theatrical_dashboard_v31.theatrical_dashboard_native import main

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎭 AIOSv3.1 Native Theatrical Dashboard")
    print("="*60)
    print("\nThis dashboard is built specifically for v3.1's architecture")
    print("It features the same beautiful 3-tab design as v3.0:")
    print("  • Agents - Real-time status and activity for each agent")
    print("  • Full Log - Complete timeline of all events")
    print("  • Performance - Metrics and performance data")
    print("\nPress 'q' to quit the dashboard")
    print("="*60 + "\n")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✅ Dashboard closed")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure you have textual installed: pip install textual")