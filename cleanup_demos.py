#!/usr/bin/env python3
"""
Demo Cleanup Script - Organize and clean demo files
"""

import os
import shutil
from pathlib import Path

# Demo status and recommendations
DEMO_STATUS = {
    # Keep these (working well)
    "demo_final.py": "KEEP - Production ready demo with all fixes",
    "demo_working_simple.py": "KEEP - Simple working demo for quick tests",
    
    # Archive these (iterations/experiments)
    "demo_auto_enhanced.py": "ARCHIVE - Iteration towards final",
    "demo_polished.py": "ARCHIVE - Iteration towards final", 
    "demo_enhanced_interactive.py": "ARCHIVE - Too complex, issues with keyboard",
    "demo_fixed_enhanced.py": "ARCHIVE - Iteration with keyboard issues",
    "demo_simple_enhanced.py": "ARCHIVE - Iteration with display issues",
    "demo_ultimate.py": "ARCHIVE - Overly complex version",
    
    # Fix or archive
    "demo_end_to_end.py": "FIX - Has import issues, otherwise good concept",
    
    # Scripts folder
    "scripts/demo_orchestrator.py": "FIX - Import issues with agents",
    "scripts/demo_orchestrator_simple.py": "FIX - Import issues with agents",
    "scripts/task_management_demo.py": "KEEP - Working task management demo"
}

def main():
    """Clean up demo files"""
    print("🧹 Demo Cleanup Report\n")
    
    # Create archive directory
    archive_dir = Path("archive/demo_iterations")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Process root demos
    print("Root Directory Demos:")
    print("-" * 50)
    for demo_file, status in DEMO_STATUS.items():
        if "/" in demo_file:
            continue  # Skip scripts folder items for now
            
        if os.path.exists(demo_file):
            action, reason = status.split(" - ", 1)
            print(f"• {demo_file}")
            print(f"  Status: {action}")
            print(f"  Reason: {reason}")
            
            if action == "ARCHIVE":
                print(f"  → Moving to {archive_dir}/")
                # shutil.move(demo_file, archive_dir / demo_file)
            
            print()
    
    # Process scripts folder
    print("\nScripts Folder Demos:")
    print("-" * 50)
    for demo_file, status in DEMO_STATUS.items():
        if "/" not in demo_file:
            continue
            
        if os.path.exists(demo_file):
            action, reason = status.split(" - ", 1)
            print(f"• {demo_file}")
            print(f"  Status: {action}")
            print(f"  Reason: {reason}")
            print()
    
    # Recommendations
    print("\n📋 Recommendations:")
    print("-" * 50)
    print("1. Keep only 2 main demos:")
    print("   - demo_final.py (full featured)")
    print("   - demo_working_simple.py (quick test)")
    print("\n2. Fix import issues in:")
    print("   - scripts/demo_orchestrator.py")
    print("   - scripts/demo_orchestrator_simple.py")
    print("   - demo_end_to_end.py")
    print("\n3. Update launcher to show only working demos")
    print("\n4. Archive iterations for reference")
    
    print("\n⚠️  This is a dry run - no files were actually moved")
    print("To execute cleanup, uncomment the shutil.move line")

if __name__ == "__main__":
    main()