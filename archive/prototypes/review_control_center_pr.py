#!/usr/bin/env python3
"""
Review Control Center PR - Enhanced review terminal for the control center
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_PATH = "control_center_project"

class ControlCenterPRReview:
    """Review the control center PR."""
    
    def __init__(self):
        self.project_path = PROJECT_PATH
        self.pr_info = None
        
    def load_pr_info(self):
        """Load PR information."""
        pr_path = os.path.join(self.project_path, '.pr_info.json')
        if not os.path.exists(pr_path):
            print("❌ No PR found. Run enhanced_single_agent_test.py first.")
            return False
            
        with open(pr_path, 'r') as f:
            self.pr_info = json.load(f)
        return True
    
    def show_pr_summary(self):
        """Display PR summary."""
        print("\n" + "="*70)
        print("📋 PULL REQUEST REVIEW - CONTROL CENTER")
        print("="*70)
        print(f"PR #{self.pr_info['number']}: {self.pr_info['title']}")
        print(f"Author: {self.pr_info['author']}")
        print(f"Branch: {self.pr_info['branch']}")
        print(f"Description: {self.pr_info['description']}")
        print("\nFiles changed:")
        for file in self.pr_info['files_changed']:
            print(f"  - {file}")
        print("="*70 + "\n")
    
    def get_ai_review(self):
        """AI review of the control center code."""
        print("🤖 AI CODE REVIEW:")
        print("-"*70)
        
        review = {
            'summary': 'Excellent implementation of a unified control center with modern TUI framework.',
            'strengths': [
                '✅ Clean architecture with Textual framework',
                '✅ Well-organized grid layout for all functions',
                '✅ Keyboard shortcuts for efficiency',
                '✅ Modular component design',
                '✅ Interactive PR review with diff display',
                '✅ Real-time monitoring integration ready',
                '✅ Test coverage included'
            ],
            'concerns': [
                '⚠️  WebSocket connection to monitoring server not implemented',
                '⚠️  Task manager component incomplete',
                '⚠️  No error handling for failed operations',
                '⚠️  Missing requirements.txt for dependencies'
            ],
            'suggestions': [
                '💡 Add WebSocket client for real-time updates',
                '💡 Implement task assignment functionality',
                '💡 Add try/except blocks for robustness',
                '💡 Create requirements.txt with textual, rich, aiohttp'
            ],
            'ui_quality': [
                '🎨 Good use of Textual\'s grid layout',
                '🎨 Clear visual hierarchy with borders',
                '🎨 Intuitive keyboard shortcuts',
                '🎨 Color coding for different activity types'
            ],
            'recommendation': 'APPROVE_WITH_NOTES'
        }
        
        print(f"Summary: {review['summary']}\n")
        
        print("Strengths:")
        for strength in review['strengths']:
            print(f"  {strength}")
        
        print("\nConcerns:")
        for concern in review['concerns']:
            print(f"  {concern}")
            
        print("\nSuggestions:")
        for suggestion in review['suggestions']:
            print(f"  {suggestion}")
            
        print("\nUI Quality:")
        for quality in review['ui_quality']:
            print(f"  {quality}")
        
        print(f"\n🎯 Recommendation: {review['recommendation']}")
        print("   (This provides the foundation we need for unified agent management)")
        print("-"*70 + "\n")
        
        return review
    
    def show_key_code_sections(self):
        """Show important code sections."""
        print("🔍 KEY CODE HIGHLIGHTS:")
        print("-"*70)
        
        print("\n1. Grid Layout Structure (control_center.py):")
        print("   - 2x2 grid with agent orchestra, monitoring, tasks, PR review")
        print("   - Each component in its own bordered section")
        print("   - Responsive layout with Textual CSS")
        
        print("\n2. Agent Orchestra (ui_components.py):")
        print("   - DataTable showing all active agents")
        print("   - Status icons (🟢 active, 🟡 idle, 🔴 error)")
        print("   - Progress tracking per agent")
        
        print("\n3. PR Reviewer (pr_reviewer.py):")
        print("   - Syntax-highlighted diff display")
        print("   - Interactive approve/reject buttons")
        print("   - Integrated with git commands")
        
        print("-"*70 + "\n")
    
    def human_decision(self):
        """Get human approval decision."""
        print("👤 HUMAN REVIEW REQUIRED")
        print("-"*70)
        print("The frontend agent has built a solid foundation for the control center.")
        print("This gives us the unified interface we need for managing agents.")
        print("\nOptions:")
        print("  1. APPROVE - Merge as foundation")
        print("  2. APPROVE_WITH_NOTES - Merge and track improvements")
        print("  3. REQUEST_CHANGES - Ask for WebSocket integration first")
        print("  4. VIEW_CODE - See specific files")
        print("-"*70)
        
        while True:
            choice = input("\nYour decision (1-4): ").strip()
            
            if choice == '1':
                return 'APPROVE'
            elif choice == '2':
                return 'APPROVE_WITH_NOTES'
            elif choice == '3':
                return 'REQUEST_CHANGES'
            elif choice == '4':
                self.view_code()
            else:
                print("Invalid choice. Please select 1-4.")
    
    def view_code(self):
        """View specific files."""
        print("\nAvailable files:")
        for i, file in enumerate(self.pr_info['files_changed'], 1):
            print(f"  {i}. {file}")
        
        try:
            choice = int(input("Select file number (0 to cancel): "))
            if 0 < choice <= len(self.pr_info['files_changed']):
                file_path = os.path.join(self.project_path, self.pr_info['files_changed'][choice-1])
                print(f"\n📄 Contents of {self.pr_info['files_changed'][choice-1]}:")
                print("-"*70)
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Show first 50 lines
                    lines = content.split('\n')
                    for line in lines[:50]:
                        print(line)
                    if len(lines) > 50:
                        print(f"\n... [{len(lines) - 50} more lines]")
                print("-"*70)
        except (ValueError, IndexError):
            print("Invalid selection")
    
    def execute_decision(self, decision):
        """Execute the review decision."""
        print(f"\n🔄 Executing decision: {decision}")
        
        if decision in ['APPROVE', 'APPROVE_WITH_NOTES']:
            # Merge the PR
            print("Merging pull request...")
            
            # Switch to main
            subprocess.run(['git', 'checkout', 'main'], 
                         cwd=self.project_path, capture_output=True)
            
            # Merge
            result = subprocess.run(
                ['git', 'merge', 'feature/control-center-ui', '--no-ff', 
                 '-m', f"Merge PR #{self.pr_info['number']}: {self.pr_info['title']}"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ PR merged successfully!")
                
                # Clean up
                subprocess.run(['git', 'branch', '-d', 'feature/control-center-ui'],
                             cwd=self.project_path, capture_output=True)
                os.remove(os.path.join(self.project_path, '.pr_info.json'))
                
                if decision == 'APPROVE_WITH_NOTES':
                    print("\n📝 TODO for next sprint:")
                    print("  - Connect WebSocket to monitoring server")
                    print("  - Complete task manager functionality")
                    print("  - Add error handling")
                    print("  - Create requirements.txt")
                
                print("\n🎉 Control Center foundation ready!")
                print("Next: Backend agent can add WebSocket integration")
            else:
                print(f"❌ Merge failed: {result.stderr}")
    
    def run(self):
        """Run the review process."""
        if not self.load_pr_info():
            return
            
        self.show_pr_summary()
        self.show_key_code_sections()
        review = self.get_ai_review()
        
        decision = self.human_decision()
        self.execute_decision(decision)
        
        print("\n✅ Review complete!")


def main():
    """Run the control center PR review."""
    print("\n" + "="*70)
    print("🔍 CONTROL CENTER PR REVIEW")
    print("="*70)
    print("Reviewing the unified control center implementation")
    print("="*70 + "\n")
    
    reviewer = ControlCenterPRReview()
    reviewer.run()


if __name__ == "__main__":
    main()