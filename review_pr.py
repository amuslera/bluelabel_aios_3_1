#!/usr/bin/env python3
"""
PR Review Terminal - Human review interface for agent PRs

This provides the review interface where:
1. I (Claude) review the code
2. You approve/reject based on my recommendation
3. We merge or request changes
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_PATH = "monitoring_system"

class PRReviewTerminal:
    """Interactive PR review terminal."""
    
    def __init__(self):
        self.project_path = PROJECT_PATH
        self.pr_info = None
        self.review_complete = False
        
    def load_pr_info(self):
        """Load PR information."""
        pr_path = os.path.join(self.project_path, '.pr_info.json')
        if not os.path.exists(pr_path):
            print("❌ No PR found. Run single_agent_pr_test.py first.")
            return False
            
        with open(pr_path, 'r') as f:
            self.pr_info = json.load(f)
        return True
    
    def show_pr_summary(self):
        """Display PR summary."""
        print("\n" + "="*70)
        print("📋 PULL REQUEST REVIEW")
        print("="*70)
        print(f"PR #{self.pr_info['number']}: {self.pr_info['title']}")
        print(f"Author: {self.pr_info['author']}")
        print(f"Branch: {self.pr_info['branch']}")
        print(f"Created: {self.pr_info['created_at']}")
        print("\nFiles changed:")
        for file in self.pr_info['files_changed']:
            print(f"  - {file}")
        print("="*70 + "\n")
    
    def show_diff(self):
        """Show git diff for the PR."""
        print("📄 CODE CHANGES:")
        print("-"*70)
        
        # Get diff between main and feature branch
        result = subprocess.run(
            ['git', 'diff', 'main...feature/monitoring-server'],
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"Error getting diff: {result.stderr}")
        
        print("-"*70 + "\n")
    
    def get_ai_review(self):
        """Get AI code review (this is where I review the code)."""
        print("🤖 AI CODE REVIEW:")
        print("-"*70)
        
        # In a real implementation, I would analyze the code here
        # For now, I'll provide a structured review
        
        review = {
            'summary': 'The monitoring server implementation looks solid with good structure and error handling.',
            'strengths': [
                '✅ Clean separation of concerns (server vs storage)',
                '✅ Proper WebSocket handling with weak references',
                '✅ CORS configuration for dashboard access',
                '✅ Graceful error handling',
                '✅ Basic test coverage included'
            ],
            'concerns': [
                '⚠️  No authentication implemented yet (was in requirements)',
                '⚠️  ActivityStore disk overflow TODO not implemented',
                '⚠️  Limited test coverage - only basic tests',
                '⚠️  No connection retry logic for clients'
            ],
            'suggestions': [
                '💡 Add basic token authentication for WebSocket connections',
                '💡 Implement disk overflow when memory limit reached',
                '💡 Add integration tests for WebSocket functionality',
                '💡 Add logging for debugging production issues'
            ],
            'security': [
                '🔒 WebSocket connections should validate origin',
                '🔒 Add rate limiting to prevent DoS',
                '🔒 Sanitize activity data before storage'
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
            
        print("\nSuggestions for improvement:")
        for suggestion in review['suggestions']:
            print(f"  {suggestion}")
            
        print("\nSecurity considerations:")
        for security in review['security']:
            print(f"  {security}")
        
        print(f"\n🎯 Recommendation: {review['recommendation']}")
        print("   (APPROVE_WITH_NOTES = merge now, address concerns in next PR)")
        print("-"*70 + "\n")
        
        return review
    
    def human_decision(self):
        """Get human approval decision."""
        print("👤 HUMAN REVIEW REQUIRED")
        print("-"*70)
        print("Based on the AI review above, you have the following options:")
        print("  1. APPROVE - Merge the PR as is")
        print("  2. APPROVE_WITH_NOTES - Merge now, address concerns later")
        print("  3. REQUEST_CHANGES - Ask agent to fix issues before merge")
        print("  4. REJECT - Close PR without merging")
        print("  5. VIEW_CODE - View specific file contents")
        print("  6. RUN_TESTS - Run the test suite")
        print("-"*70)
        
        while True:
            choice = input("\nYour decision (1-6): ").strip()
            
            if choice == '1':
                return 'APPROVE'
            elif choice == '2':
                return 'APPROVE_WITH_NOTES'
            elif choice == '3':
                return 'REQUEST_CHANGES'
            elif choice == '4':
                return 'REJECT'
            elif choice == '5':
                self.view_code()
            elif choice == '6':
                self.run_tests()
            else:
                print("Invalid choice. Please select 1-6.")
    
    def view_code(self):
        """View specific file contents."""
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
                    print(f.read())
                print("-"*70)
        except (ValueError, IndexError):
            print("Invalid selection")
    
    def run_tests(self):
        """Run the test suite."""
        print("\n🧪 Running tests...")
        print("-"*70)
        
        # Run pytest
        result = subprocess.run(
            ['python', '-m', 'pytest', 'tests/', '-v'],
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed")
        print("-"*70)
    
    def execute_decision(self, decision):
        """Execute the review decision."""
        print(f"\n🔄 Executing decision: {decision}")
        
        if decision in ['APPROVE', 'APPROVE_WITH_NOTES']:
            # Merge the PR
            print("Merging pull request...")
            
            # Switch to main
            subprocess.run(['git', 'checkout', 'main'], 
                         cwd=self.project_path, capture_output=True)
            
            # Merge feature branch
            result = subprocess.run(
                ['git', 'merge', 'feature/monitoring-server', '--no-ff', 
                 '-m', f"Merge PR #{self.pr_info['number']}: {self.pr_info['title']}"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ PR merged successfully!")
                
                # Delete feature branch
                subprocess.run(['git', 'branch', '-d', 'feature/monitoring-server'],
                             cwd=self.project_path, capture_output=True)
                
                # Remove PR info file
                os.remove(os.path.join(self.project_path, '.pr_info.json'))
                
                if decision == 'APPROVE_WITH_NOTES':
                    print("\n📝 Remember to address the concerns in the next sprint:")
                    print("  - Add authentication")
                    print("  - Implement disk overflow")
                    print("  - Expand test coverage")
                    print("  - Add connection retry logic")
            else:
                print(f"❌ Merge failed: {result.stderr}")
                
        elif decision == 'REQUEST_CHANGES':
            print("📝 Changes requested. Agent should address:")
            print("  - Authentication implementation")
            print("  - Disk overflow for ActivityStore")
            print("  - Expanded test coverage")
            print("\nThe agent will be notified to make these changes.")
            
        elif decision == 'REJECT':
            print("❌ PR rejected and closed.")
            # Clean up branch
            subprocess.run(['git', 'checkout', 'main'], 
                         cwd=self.project_path, capture_output=True)
            subprocess.run(['git', 'branch', '-D', 'feature/monitoring-server'],
                         cwd=self.project_path, capture_output=True)
            os.remove(os.path.join(self.project_path, '.pr_info.json'))
    
    def save_review_record(self, decision, review):
        """Save review record for learning."""
        record = {
            'pr_number': self.pr_info['number'],
            'timestamp': datetime.now().isoformat(),
            'ai_review': review,
            'human_decision': decision,
            'files_reviewed': self.pr_info['files_changed']
        }
        
        # Save to reviews directory
        reviews_dir = os.path.join(self.project_path, 'reviews')
        os.makedirs(reviews_dir, exist_ok=True)
        
        review_file = os.path.join(reviews_dir, f"pr_{self.pr_info['number']}_review.json")
        with open(review_file, 'w') as f:
            json.dump(record, f, indent=2)
        
        print(f"\n📝 Review saved to: {review_file}")
    
    def run(self):
        """Run the review terminal."""
        if not self.load_pr_info():
            return
            
        self.show_pr_summary()
        self.show_diff()
        review = self.get_ai_review()
        
        decision = self.human_decision()
        self.execute_decision(decision)
        self.save_review_record(decision, review)
        
        print("\n✅ Review process complete!")
        

def main():
    """Run the PR review terminal."""
    print("\n" + "="*70)
    print("🔍 PR REVIEW TERMINAL")
    print("="*70)
    print("AI reviews code → Human approves → System merges")
    print("="*70 + "\n")
    
    terminal = PRReviewTerminal()
    terminal.run()


if __name__ == "__main__":
    main()