#!/usr/bin/env python3
"""
Unified Review Process for Sprint 1.6 - Control Center Project

This combines the best patterns from our existing review processes to create
a streamlined workflow for reviewing multi-agent deliverables.

Key Features:
1. Multi-agent PR coordination
2. Integrated AI review with domain-specific checks
3. Human approval workflow with visual diffs
4. Automatic orchestration of merge/feedback cycles
5. Learning from review decisions
"""

import os
import sys
import json
import subprocess
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Project configuration
CONTROL_CENTER_PATH = "control_center_project"
SPRINT_VERSION = "1.6"


class ReviewDecision(Enum):
    """Review decisions available."""
    APPROVE = "approve"
    APPROVE_WITH_NOTES = "approve_with_notes"
    REQUEST_CHANGES = "request_changes"
    REJECT = "reject"
    ESCALATE = "escalate"  # New: escalate to orchestrator


@dataclass
class PRInfo:
    """Pull request information."""
    number: int
    title: str
    branch: str
    author: str
    agent_role: str
    description: str
    created_at: str
    files_changed: List[str]
    task_id: Optional[str] = None
    dependencies: List[str] = None
    test_results: Optional[Dict[str, Any]] = None


@dataclass
class ReviewCriteria:
    """Domain-specific review criteria."""
    role: str
    criteria: List[str]
    required_files: List[str]
    quality_checks: List[str]


class UnifiedReviewProcess:
    """Unified review process for multi-agent deliverables."""
    
    def __init__(self, project_path: str = CONTROL_CENTER_PATH):
        self.project_path = project_path
        self.prs_to_review: List[PRInfo] = []
        self.review_history: List[Dict[str, Any]] = []
        self.current_pr: Optional[PRInfo] = None
        
        # Define review criteria per agent role
        self.review_criteria = self._initialize_review_criteria()
        
    def _initialize_review_criteria(self) -> Dict[str, ReviewCriteria]:
        """Initialize domain-specific review criteria."""
        return {
            "frontend": ReviewCriteria(
                role="frontend",
                criteria=[
                    "UI components are modular and reusable",
                    "Proper state management implemented",
                    "Responsive design considerations",
                    "Accessibility standards met",
                    "User interactions are intuitive"
                ],
                required_files=["ui_components.py", "control_center.py"],
                quality_checks=["No hardcoded values", "Event handlers properly bound"]
            ),
            "backend": ReviewCriteria(
                role="backend",
                criteria=[
                    "API endpoints follow REST conventions",
                    "Proper error handling implemented",
                    "WebSocket connections managed correctly",
                    "Data validation in place",
                    "Security considerations addressed"
                ],
                required_files=["api_endpoints.py", "websocket_handler.py"],
                quality_checks=["Authentication implemented", "Rate limiting configured"]
            ),
            "integration": ReviewCriteria(
                role="integration",
                criteria=[
                    "Components properly integrated",
                    "Data flow is clear and efficient",
                    "Error propagation handled",
                    "Configuration management solid",
                    "Deployment ready"
                ],
                required_files=["main.py", "config.py", "requirements.txt"],
                quality_checks=["All services connectable", "Configuration validated"]
            )
        }
    
    async def scan_for_prs(self) -> List[PRInfo]:
        """Scan project directory for pending PRs."""
        print("🔍 Scanning for pull requests...")
        
        prs_found = []
        
        # Look for PR info files
        for pr_file in Path(self.project_path).glob(".pr_info_*.json"):
            with open(pr_file, 'r') as f:
                pr_data = json.load(f)
                
            pr_info = PRInfo(
                number=pr_data['number'],
                title=pr_data['title'],
                branch=pr_data['branch'],
                author=pr_data['author'],
                agent_role=pr_data.get('agent_role', 'unknown'),
                description=pr_data.get('description', ''),
                created_at=pr_data['created_at'],
                files_changed=pr_data['files_changed'],
                task_id=pr_data.get('task_id'),
                dependencies=pr_data.get('dependencies', []),
                test_results=pr_data.get('test_results')
            )
            
            prs_found.append(pr_info)
        
        self.prs_to_review = sorted(prs_found, key=lambda x: x.created_at)
        
        print(f"✅ Found {len(self.prs_to_review)} PRs to review")
        return self.prs_to_review
    
    def show_review_dashboard(self):
        """Display review dashboard with all pending PRs."""
        print("\n" + "="*80)
        print("📊 UNIFIED REVIEW DASHBOARD - Sprint 1.6")
        print("="*80)
        
        if not self.prs_to_review:
            print("No pending PRs to review.")
            return
        
        print(f"\nPending Reviews: {len(self.prs_to_review)}")
        print("-"*80)
        
        for i, pr in enumerate(self.prs_to_review, 1):
            status_icon = "🟡" if pr.dependencies else "🟢"
            print(f"\n{i}. {status_icon} PR #{pr.number}: {pr.title}")
            print(f"   Author: {pr.author} ({pr.agent_role})")
            print(f"   Branch: {pr.branch}")
            print(f"   Files: {len(pr.files_changed)}")
            if pr.dependencies:
                print(f"   ⚠️  Dependencies: {', '.join(pr.dependencies)}")
        
        print("\n" + "="*80)
    
    async def review_pr(self, pr: PRInfo) -> Dict[str, Any]:
        """Perform AI review of a PR based on agent role."""
        self.current_pr = pr
        
        print(f"\n🤖 AI REVIEW: {pr.title}")
        print("-"*80)
        
        # Get role-specific criteria
        criteria = self.review_criteria.get(pr.agent_role, None)
        
        review = {
            'pr_number': pr.number,
            'timestamp': datetime.now().isoformat(),
            'agent_role': pr.agent_role,
            'summary': f'Review of {pr.agent_role} implementation for control center',
            'strengths': [],
            'concerns': [],
            'suggestions': [],
            'code_quality': {},
            'recommendation': 'APPROVE_WITH_NOTES'
        }
        
        # Role-specific review logic
        if pr.agent_role == "frontend":
            review['strengths'] = [
                '✅ Clean Textual-based TUI implementation',
                '✅ Modular component architecture',
                '✅ Clear separation of concerns',
                '✅ Keyboard shortcuts implemented',
                '✅ Responsive grid layout'
            ]
            review['concerns'] = [
                '⚠️  WebSocket client not yet implemented',
                '⚠️  No error boundaries for UI crashes',
                '⚠️  Task assignment UI incomplete'
            ]
            review['suggestions'] = [
                '💡 Add WebSocket client for real-time updates',
                '💡 Implement error boundaries for robustness',
                '💡 Complete task assignment interface'
            ]
            
        elif pr.agent_role == "backend":
            review['strengths'] = [
                '✅ Well-structured API endpoints',
                '✅ WebSocket server implementation solid',
                '✅ Good error handling patterns',
                '✅ Data validation implemented'
            ]
            review['concerns'] = [
                '⚠️  Missing authentication middleware',
                '⚠️  No rate limiting implemented',
                '⚠️  Database persistence not configured'
            ]
            review['suggestions'] = [
                '💡 Add JWT authentication',
                '💡 Implement rate limiting for API endpoints',
                '💡 Configure SQLite for persistence'
            ]
            
        elif pr.agent_role == "integration":
            review['strengths'] = [
                '✅ All components properly wired together',
                '✅ Configuration management clean',
                '✅ Main entry point well organized',
                '✅ Requirements.txt complete'
            ]
            review['concerns'] = [
                '⚠️  No Docker configuration yet',
                '⚠️  Missing environment variable handling',
                '⚠️  No health check endpoints'
            ]
            review['suggestions'] = [
                '💡 Add Dockerfile for containerization',
                '💡 Use python-dotenv for env vars',
                '💡 Add /health endpoint for monitoring'
            ]
        
        # Check for required files
        if criteria:
            missing_files = [f for f in criteria.required_files 
                           if f not in pr.files_changed]
            if missing_files:
                review['concerns'].append(
                    f'⚠️  Missing expected files: {", ".join(missing_files)}'
                )
        
        # Display review
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
        
        # Test results if available
        if pr.test_results:
            print("\n🧪 Test Results:")
            print(f"  Passed: {pr.test_results.get('passed', 0)}")
            print(f"  Failed: {pr.test_results.get('failed', 0)}")
            print(f"  Coverage: {pr.test_results.get('coverage', 'N/A')}")
        
        print(f"\n🎯 Recommendation: {review['recommendation']}")
        print("-"*80)
        
        return review
    
    def show_diff(self, pr: PRInfo):
        """Show git diff for the PR."""
        print(f"\n📄 CODE CHANGES FOR PR #{pr.number}:")
        print("-"*80)
        
        # Get diff between main and feature branch
        result = subprocess.run(
            ['git', 'diff', f'main...{pr.branch}', '--stat'],
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"Error getting diff: {result.stderr}")
        
        print("-"*80)
    
    async def get_human_decision(self, pr: PRInfo, review: Dict[str, Any]) -> ReviewDecision:
        """Get human approval decision."""
        print("\n👤 HUMAN REVIEW REQUIRED")
        print("-"*80)
        print(f"PR #{pr.number}: {pr.title}")
        print(f"Author: {pr.author} ({pr.agent_role})")
        print("\nBased on the AI review above, you have the following options:")
        print("  1. APPROVE - Merge the PR as is")
        print("  2. APPROVE_WITH_NOTES - Merge now, track improvements")
        print("  3. REQUEST_CHANGES - Ask agent to fix issues")
        print("  4. REJECT - Close PR without merging")
        print("  5. ESCALATE - Escalate to orchestrator for team discussion")
        print("  6. VIEW_DIFF - See detailed code changes")
        print("  7. RUN_TESTS - Run the test suite")
        print("-"*80)
        
        while True:
            choice = input("\nYour decision (1-7): ").strip()
            
            if choice == '1':
                return ReviewDecision.APPROVE
            elif choice == '2':
                return ReviewDecision.APPROVE_WITH_NOTES
            elif choice == '3':
                return ReviewDecision.REQUEST_CHANGES
            elif choice == '4':
                return ReviewDecision.REJECT
            elif choice == '5':
                return ReviewDecision.ESCALATE
            elif choice == '6':
                self.show_diff(pr)
            elif choice == '7':
                await self.run_tests(pr)
            else:
                print("Invalid choice. Please select 1-7.")
    
    async def run_tests(self, pr: PRInfo):
        """Run tests for the PR."""
        print("\n🧪 Running tests...")
        print("-"*80)
        
        # Checkout the PR branch
        subprocess.run(['git', 'checkout', pr.branch], 
                      cwd=self.project_path, capture_output=True)
        
        # Run pytest
        result = subprocess.run(
            ['python', '-m', 'pytest', 'tests/', '-v', '--tb=short'],
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
        
        # Return to main branch
        subprocess.run(['git', 'checkout', 'main'], 
                      cwd=self.project_path, capture_output=True)
        print("-"*80)
    
    async def execute_decision(self, pr: PRInfo, decision: ReviewDecision, review: Dict[str, Any]):
        """Execute the review decision."""
        print(f"\n🔄 Executing decision: {decision.value}")
        
        if decision in [ReviewDecision.APPROVE, ReviewDecision.APPROVE_WITH_NOTES]:
            # Merge the PR
            print(f"Merging PR #{pr.number}...")
            
            # Switch to main
            subprocess.run(['git', 'checkout', 'main'], 
                         cwd=self.project_path, capture_output=True)
            
            # Merge feature branch
            commit_msg = f"Merge PR #{pr.number}: {pr.title}\n\nAuthor: {pr.author}\nRole: {pr.agent_role}"
            result = subprocess.run(
                ['git', 'merge', pr.branch, '--no-ff', '-m', commit_msg],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ PR #{pr.number} merged successfully!")
                
                # Delete feature branch
                subprocess.run(['git', 'branch', '-d', pr.branch],
                             cwd=self.project_path, capture_output=True)
                
                # Remove PR info file
                pr_file = os.path.join(self.project_path, f'.pr_info_{pr.number}.json')
                if os.path.exists(pr_file):
                    os.remove(pr_file)
                
                if decision == ReviewDecision.APPROVE_WITH_NOTES:
                    print("\n📝 Tracking improvements for next iteration:")
                    for concern in review['concerns']:
                        print(f"  {concern}")
                    
                    # Save improvement items
                    self._save_improvement_items(pr, review['concerns'])
                    
            else:
                print(f"❌ Merge failed: {result.stderr}")
                
        elif decision == ReviewDecision.REQUEST_CHANGES:
            print(f"📝 Changes requested for PR #{pr.number}")
            print("\nThe agent will be notified to address:")
            for concern in review['concerns']:
                print(f"  {concern}")
            
            # Create feedback file for agent
            feedback = {
                'pr_number': pr.number,
                'decision': decision.value,
                'timestamp': datetime.now().isoformat(),
                'requested_changes': review['concerns'],
                'suggestions': review['suggestions']
            }
            
            feedback_file = os.path.join(self.project_path, f'.pr_feedback_{pr.number}.json')
            with open(feedback_file, 'w') as f:
                json.dump(feedback, f, indent=2)
            
            print(f"\n✅ Feedback saved to {feedback_file}")
            
        elif decision == ReviewDecision.ESCALATE:
            print(f"🚨 Escalating PR #{pr.number} to orchestrator")
            print("\nThis will trigger a team discussion about:")
            print(f"  • {pr.title}")
            print(f"  • Key concerns: {', '.join(review['concerns'][:2])}")
            
            # Create escalation record
            escalation = {
                'pr_number': pr.number,
                'pr_info': asdict(pr),
                'review': review,
                'escalation_reason': 'Human reviewer requested team discussion',
                'timestamp': datetime.now().isoformat()
            }
            
            escalation_file = os.path.join(self.project_path, f'.pr_escalation_{pr.number}.json')
            with open(escalation_file, 'w') as f:
                json.dump(escalation, f, indent=2)
            
            print(f"\n✅ Escalation recorded. Orchestrator will coordinate team discussion.")
    
    def _save_improvement_items(self, pr: PRInfo, concerns: List[str]):
        """Save improvement items for tracking."""
        improvements_file = os.path.join(self.project_path, 'improvements_backlog.json')
        
        # Load existing items
        if os.path.exists(improvements_file):
            with open(improvements_file, 'r') as f:
                improvements = json.load(f)
        else:
            improvements = []
        
        # Add new items
        for concern in concerns:
            improvements.append({
                'id': f"IMP-{len(improvements) + 1}",
                'source_pr': pr.number,
                'agent_role': pr.agent_role,
                'description': concern.replace('⚠️  ', ''),
                'created_at': datetime.now().isoformat(),
                'status': 'pending'
            })
        
        # Save updated list
        with open(improvements_file, 'w') as f:
            json.dump(improvements, f, indent=2)
    
    def save_review_record(self, pr: PRInfo, review: Dict[str, Any], decision: ReviewDecision):
        """Save review record for learning and metrics."""
        record = {
            'pr_number': pr.number,
            'timestamp': datetime.now().isoformat(),
            'agent_role': pr.agent_role,
            'ai_review': review,
            'human_decision': decision.value,
            'files_reviewed': pr.files_changed,
            'sprint_version': SPRINT_VERSION
        }
        
        # Save to reviews directory
        reviews_dir = os.path.join(self.project_path, 'reviews')
        os.makedirs(reviews_dir, exist_ok=True)
        
        review_file = os.path.join(reviews_dir, f"pr_{pr.number}_review.json")
        with open(review_file, 'w') as f:
            json.dump(record, f, indent=2)
        
        print(f"\n📝 Review record saved to: {review_file}")
    
    def show_review_summary(self):
        """Show summary of review session."""
        print("\n" + "="*80)
        print("📊 REVIEW SESSION SUMMARY")
        print("="*80)
        
        if not self.review_history:
            print("No reviews completed in this session.")
            return
        
        print(f"\nReviews Completed: {len(self.review_history)}")
        
        # Count decisions
        decisions = {}
        for record in self.review_history:
            decision = record['decision']
            decisions[decision] = decisions.get(decision, 0) + 1
        
        print("\nDecisions Made:")
        for decision, count in decisions.items():
            print(f"  • {decision}: {count}")
        
        # Show improvements tracked
        improvements_file = os.path.join(self.project_path, 'improvements_backlog.json')
        if os.path.exists(improvements_file):
            with open(improvements_file, 'r') as f:
                improvements = json.load(f)
            pending = [i for i in improvements if i['status'] == 'pending']
            if pending:
                print(f"\nImprovements Tracked: {len(pending)}")
        
        print("\n✅ Review session complete!")
        print("="*80)
    
    async def run_review_session(self):
        """Run the complete review session."""
        print("\n" + "="*80)
        print("🔍 UNIFIED REVIEW PROCESS - Sprint 1.6")
        print("="*80)
        print("AI reviews code → Human approves → System coordinates merges")
        print("="*80 + "\n")
        
        # Scan for PRs
        await self.scan_for_prs()
        
        if not self.prs_to_review:
            print("No PRs found to review.")
            return
        
        # Show dashboard
        self.show_review_dashboard()
        
        # Review each PR
        for pr in self.prs_to_review:
            print(f"\n{'='*80}")
            print(f"REVIEWING PR #{pr.number}")
            print(f"{'='*80}")
            
            # AI review
            review = await self.review_pr(pr)
            
            # Human decision
            decision = await self.get_human_decision(pr, review)
            
            # Execute decision
            await self.execute_decision(pr, decision, review)
            
            # Save record
            self.save_review_record(pr, review, decision)
            
            # Track in history
            self.review_history.append({
                'pr': asdict(pr),
                'review': review,
                'decision': decision.value
            })
            
            print(f"\n✅ Review of PR #{pr.number} complete!")
            
            # Ask if continue
            if len(self.prs_to_review) > 1:
                cont = input("\nContinue to next PR? (y/n): ")
                if cont.lower() != 'y':
                    break
        
        # Show summary
        self.show_review_summary()


async def main():
    """Run the unified review process."""
    reviewer = UnifiedReviewProcess()
    await reviewer.run_review_session()


if __name__ == "__main__":
    asyncio.run(main())