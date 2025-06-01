#!/usr/bin/env python3
"""
Launch Theatrical Sprint - Run agents in separate terminals

This launches the theatrical orchestrator which shows real agents
building the monitoring system at human-comprehensible pace.
"""

import subprocess
import sys
import os
import time

def main():
    print("\n" + "="*70)
    print("🎭 THEATRICAL SPRINT LAUNCHER")
    print("="*70)
    print("\nThis will launch real agents to build the monitoring system")
    print("at a pace you can follow and understand.\n")
    
    print("What you'll see:")
    print("- ✨ Agents thinking through problems")
    print("- 📝 Code being written line by line")
    print("- 🤔 Decision-making processes")
    print("- 👥 Agent collaboration")
    print("- 📊 Progress tracking")
    print("- 🔧 Real git operations\n")
    
    print("The agents will build:")
    print("- WebSocket monitoring server")
    print("- Agent activity reporter")
    print("- Real-time Rich dashboard")
    print("- Metrics collection system")
    print("- Database persistence")
    print("- Integration tests\n")
    
    print("This is NOT a demo - real code will be created in:")
    print("./theatrical_monitor_project/\n")
    
    input("Press Enter to start the theatrical sprint...")
    
    print("\n🚀 Launching theatrical orchestrator...\n")
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Launch the orchestrator
    try:
        subprocess.run([sys.executable, "theatrical_orchestrator.py"])
    except KeyboardInterrupt:
        print("\n\n👋 Sprint cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")

if __name__ == "__main__":
    main()