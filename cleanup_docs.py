#!/usr/bin/env python3
"""
Documentation Cleanup Recommendations
"""

import os
from pathlib import Path

# Files to keep, update, or archive
RECOMMENDATIONS = {
    "KEEP": [
        "CLAUDE.md - Core project instructions",
        "PROJECT_CONTEXT.md - Current state (updated June 3, 2025)",
        "README.md - Project overview", 
        "ARCHITECTURE.md - Technical architecture",
        "DEVELOPMENT_PROCESS.md - Sprint process guide",
        "PHASE_2_COMPLETE.md - Recent milestone",
        "DEMO_GUIDE.md - Demo documentation",
        "HANDOFF_JUNE_2025.md - Current handoff",
    ],
    
    "UPDATE_DONE": [
        "AGENT_ROSTER.md - Added actual vs designed agent names",
        "PROJECT_CONTEXT.md - Fixed dates to June 3, 2025",
    ],
    
    "ARCHIVED": [
        "HANDOFF_SESSION_DEC_2024.md → archive/session_handoffs/",
        "THEATRICAL_DASHBOARD_*.md → archive/theatrical_dashboards/",
        "6 demo iterations → archive/demo_iterations/",
    ],
    
    "NEEDS_UPDATE": [
        "ROLE_DEFINITIONS.md - Update agent names to match implementation",
        "HANDOFF_TO_NEW_CLAUDE_INSTANCE.md - Update date from Dec 2024",
        "sprints/active/CURRENT_SPRINT.md - Needs Phase 3 planning",
    ]
}

def main():
    print("📚 Documentation Cleanup Summary\n")
    print("=" * 60)
    
    for category, files in RECOMMENDATIONS.items():
        print(f"\n{category}:")
        print("-" * 40)
        for file in files:
            print(f"  • {file}")
    
    print("\n\n📋 Recommended Actions:")
    print("-" * 60)
    print("1. Update ROLE_DEFINITIONS.md with correct agent names")
    print("2. Update HANDOFF_TO_NEW_CLAUDE_INSTANCE.md date")
    print("3. Create Phase 3 sprint plan in CURRENT_SPRINT.md")
    print("4. Consider consolidating multiple handoff documents")
    
    print("\n✅ Cleanup Status:")
    print("-" * 60)
    print("• Dates fixed: June 3, 2025")
    print("• Old demos archived: 6 files")
    print("• Session files archived: 4 files")
    print("• Core docs updated: 2 files")
    print("• Ready for Phase 3!")

if __name__ == "__main__":
    main()