"""
PR review interface for the control center.
"""

from textual.widgets import Static, TextLog, Button
from textual.containers import Container, Horizontal, Vertical
from rich.syntax import Syntax
from rich.diff import Diff
import subprocess
import json

class PRReviewer(Container):
    """Interactive PR review interface."""
    
    def compose(self):
        yield Static("🔍 PR Review", classes="title")
        yield Vertical(
            PRInfo(id="pr-info"),
            DiffViewer(id="diff-viewer"),
            Horizontal(
                Button("Approve", id="approve", variant="success"),
                Button("Request Changes", id="request-changes", variant="warning"),
                Button("View Code", id="view-code"),
                classes="pr-actions"
            )
        )
    
    async def load_pr(self, pr_number: int):
        """Load PR for review."""
        # Get PR info
        pr_info = self.get_pr_info(pr_number)
        self.query_one("#pr-info").update(pr_info)
        
        # Get diff
        diff = self.get_pr_diff(pr_info['branch'])
        self.query_one("#diff-viewer").show_diff(diff)
    
    def get_pr_diff(self, branch: str) -> str:
        """Get git diff for PR."""
        result = subprocess.run(
            ['git', 'diff', f'main...{branch}'],
            capture_output=True,
            text=True
        )
        return result.stdout if result.returncode == 0 else "Error getting diff"

class DiffViewer(Container):
    """Display code diffs with syntax highlighting."""
    
    def compose(self):
        self.diff_display = TextLog(highlight=True, markup=True)
        yield self.diff_display
    
    def show_diff(self, diff_text: str):
        """Display diff with colors."""
        for line in diff_text.split('\n'):
            if line.startswith('+'):
                self.diff_display.write(f"[green]{line}[/green]")
            elif line.startswith('-'):
                self.diff_display.write(f"[red]{line}[/red]")
            elif line.startswith('@@'):
                self.diff_display.write(f"[blue]{line}[/blue]")
            else:
                self.diff_display.write(line)