"""
Code Visualization Components

Advanced visualization for showing code generation, diffs, and
agent contributions in real-time.
"""

import os
import difflib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from rich.text import Text
from rich.syntax import Syntax
from rich.panel import Panel
from rich.console import Console, Group
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.columns import Columns
from rich import box


@dataclass
class CodeContribution:
    """Represents a code contribution from an agent"""
    agent_name: str
    timestamp: datetime
    file_path: str
    line_start: int
    line_end: int
    code: str
    action: str  # 'add', 'modify', 'delete', 'review'
    comment: Optional[str] = None


@dataclass
class CodeFile:
    """Represents a file being worked on"""
    path: str
    language: str
    content: List[str] = field(default_factory=list)
    contributions: List[CodeContribution] = field(default_factory=list)
    current_editor: Optional[str] = None
    last_modified: datetime = field(default_factory=datetime.now)


class CodeVisualizer:
    """Visualizes code generation and collaboration"""
    
    def __init__(self):
        self.files: Dict[str, CodeFile] = {}
        self.agent_colors = {
            "Marcus Chen": "cyan",
            "Emily Rodriguez": "magenta", 
            "Alex Thompson": "yellow",
            "Jordan Kim": "green"
        }
        self.typing_buffers: Dict[str, str] = {}  # Agent -> current typing
        
    def create_file(self, path: str, language: str) -> CodeFile:
        """Create a new file"""
        file = CodeFile(path=path, language=language)
        self.files[path] = file
        return file
        
    def render_code_editor(self, file_path: str, height: int = 20) -> Panel:
        """Render a code editor panel showing current file state"""
        if file_path not in self.files:
            return Panel("No file selected", title="Code Editor", border_style="dim")
            
        file = self.files[file_path]
        
        # Create syntax highlighted code
        code_text = "\n".join(file.content) if file.content else ""
        
        # Add typing buffer if someone is actively typing
        if file.current_editor and file.current_editor in self.typing_buffers:
            buffer = self.typing_buffers[file.current_editor]
            if buffer:
                code_text += buffer
                
        syntax = Syntax(
            code_text,
            file.language,
            theme="monokai",
            line_numbers=True,
            word_wrap=True,
            background_color="default"
        )
        
        # Create title with current editor
        title = f"📝 {file.path}"
        if file.current_editor:
            color = self.agent_colors.get(file.current_editor, "white")
            title += f" - [bold {color}]{file.current_editor} editing...[/bold {color}]"
            
        return Panel(
            syntax,
            title=title,
            border_style=self.agent_colors.get(file.current_editor, "white"),
            height=height
        )
        
    def render_contribution_timeline(self, file_path: str) -> Panel:
        """Render a timeline of contributions to a file"""
        if file_path not in self.files:
            return Panel("No contributions yet", title="Contribution Timeline")
            
        file = self.files[file_path]
        
        table = Table(show_header=True, box=box.SIMPLE)
        table.add_column("Time", style="dim", width=8)
        table.add_column("Agent", width=15)
        table.add_column("Action", width=10)
        table.add_column("Lines", width=10)
        table.add_column("Comment", width=40)
        
        # Show last 10 contributions
        recent_contributions = file.contributions[-10:] if file.contributions else []
        
        for contrib in recent_contributions:
            time_str = contrib.timestamp.strftime("%H:%M:%S")
            agent_color = self.agent_colors.get(contrib.agent_name, "white")
            
            lines_affected = f"{contrib.line_start}-{contrib.line_end}"
            if contrib.line_start == contrib.line_end:
                lines_affected = str(contrib.line_start)
                
            action_emoji = {
                "add": "➕",
                "modify": "✏️",
                "delete": "❌",
                "review": "👀"
            }.get(contrib.action, "❓")
            
            table.add_row(
                time_str,
                f"[{agent_color}]{contrib.agent_name}[/{agent_color}]",
                f"{action_emoji} {contrib.action}",
                lines_affected,
                contrib.comment or ""
            )
            
        return Panel(
            table,
            title="📜 Contribution Timeline",
            border_style="blue"
        )
        
    def render_diff_view(self, file_path: str, show_last_n: int = 5) -> Panel:
        """Render a diff view showing recent changes"""
        if file_path not in self.files:
            return Panel("No changes to show", title="Recent Changes")
            
        file = self.files[file_path]
        
        # Get recent modifications
        recent_mods = [c for c in file.contributions[-show_last_n:] 
                      if c.action in ["add", "modify"]]
        
        if not recent_mods:
            return Panel("No recent modifications", title="Recent Changes")
            
        diff_text = Text()
        
        for contrib in recent_mods:
            # Add header
            agent_color = self.agent_colors.get(contrib.agent_name, "white")
            diff_text.append(f"\n{contrib.agent_name} ", style=f"bold {agent_color}")
            diff_text.append(f"@ line {contrib.line_start}\n", style="dim")
            
            # Show the contributed code with + prefix
            for line in contrib.code.split('\n'):
                if line.strip():
                    diff_text.append("+ ", style="green")
                    diff_text.append(f"{line}\n", style="green")
                    
        return Panel(
            diff_text,
            title="🔍 Recent Changes",
            border_style="green"
        )
        
    def render_file_tree(self) -> Panel:
        """Render a file tree showing all files being worked on"""
        tree_text = Text()
        
        if not self.files:
            tree_text.append("No files yet", style="dim")
        else:
            # Group files by directory
            by_dir: Dict[str, List[str]] = {}
            for path in sorted(self.files.keys()):
                dir_name = os.path.dirname(path) or "."
                if dir_name not in by_dir:
                    by_dir[dir_name] = []
                by_dir[dir_name].append(os.path.basename(path))
                
            # Render tree
            for dir_name, files in by_dir.items():
                tree_text.append(f"📁 {dir_name}/\n", style="blue")
                for file_name in files:
                    full_path = os.path.join(dir_name, file_name)
                    file = self.files.get(full_path)
                    
                    # Icon based on file type
                    if file_name.endswith('.py'):
                        icon = "🐍"
                    elif file_name.endswith(('.js', '.jsx', '.ts', '.tsx')):
                        icon = "📜"
                    elif file_name.endswith(('.yml', '.yaml')):
                        icon = "⚙️"
                    else:
                        icon = "📄"
                        
                    tree_text.append(f"  {icon} {file_name}", style="white")
                    
                    # Show current editor
                    if file and file.current_editor:
                        color = self.agent_colors.get(file.current_editor, "white")
                        tree_text.append(f" [{color}]●[/{color}]", style=color)
                        
                    tree_text.append("\n")
                    
        return Panel(
            tree_text,
            title="📂 Project Files",
            border_style="blue"
        )
        
    def simulate_typing(self, agent_name: str, text: str, file_path: str):
        """Simulate agent typing effect"""
        self.typing_buffers[agent_name] = text
        if file_path in self.files:
            self.files[file_path].current_editor = agent_name
            
    def commit_typing(self, agent_name: str, file_path: str):
        """Commit typed content to file"""
        if agent_name in self.typing_buffers and file_path in self.files:
            buffer = self.typing_buffers[agent_name]
            if buffer:
                file = self.files[file_path]
                
                # Add to file content
                new_lines = buffer.split('\n')
                start_line = len(file.content)
                file.content.extend(new_lines)
                
                # Record contribution
                contrib = CodeContribution(
                    agent_name=agent_name,
                    timestamp=datetime.now(),
                    file_path=file_path,
                    line_start=start_line,
                    line_end=start_line + len(new_lines) - 1,
                    code=buffer,
                    action="add"
                )
                file.contributions.append(contrib)
                
                # Clear buffer
                self.typing_buffers[agent_name] = ""
                file.current_editor = None
                file.last_modified = datetime.now()
                
    def add_review_comment(
        self, 
        agent_name: str, 
        file_path: str, 
        line_number: int,
        comment: str
    ):
        """Add a code review comment"""
        if file_path in self.files:
            file = self.files[file_path]
            contrib = CodeContribution(
                agent_name=agent_name,
                timestamp=datetime.now(),
                file_path=file_path,
                line_start=line_number,
                line_end=line_number,
                code="",
                action="review",
                comment=comment
            )
            file.contributions.append(contrib)
            
    def render_collaboration_matrix(self) -> Panel:
        """Render a matrix showing agent collaboration patterns"""
        table = Table(show_header=True, box=box.ROUNDED)
        table.add_column("Agent", style="bold")
        
        agents = list(self.agent_colors.keys())
        
        # Add columns for each agent
        for agent in agents:
            color = self.agent_colors[agent]
            table.add_column(agent.split()[0], style=color, justify="center")
            
        # Calculate collaboration scores
        collab_matrix = {}
        for file in self.files.values():
            for i, contrib1 in enumerate(file.contributions):
                for contrib2 in file.contributions[i+1:]:
                    if contrib1.agent_name != contrib2.agent_name:
                        key = (contrib1.agent_name, contrib2.agent_name)
                        collab_matrix[key] = collab_matrix.get(key, 0) + 1
                        
        # Build table
        for agent1 in agents:
            row = [agent1.split()[0]]  # First name only
            for agent2 in agents:
                if agent1 == agent2:
                    row.append("—")
                else:
                    score = collab_matrix.get((agent1, agent2), 0)
                    score += collab_matrix.get((agent2, agent1), 0)
                    if score > 0:
                        row.append(str(score))
                    else:
                        row.append("·")
            table.add_row(*row)
            
        return Panel(
            table,
            title="🤝 Collaboration Matrix",
            subtitle="Number of file interactions",
            border_style="purple"
        )


class LiveCodeSession:
    """Manages a live coding session with multiple agents"""
    
    def __init__(self, code_visualizer: CodeVisualizer):
        self.code_viz = code_visualizer
        self.console = Console()
        
    def render_coding_workspace(self) -> Group:
        """Render the complete coding workspace"""
        # Main code editor
        editor = self.code_viz.render_code_editor(
            self.get_active_file() or "main.py", 
            height=25
        )
        
        # Side panels
        file_tree = self.code_viz.render_file_tree()
        timeline = self.code_viz.render_contribution_timeline(
            self.get_active_file() or "main.py"
        )
        
        # Bottom panels
        diff_view = self.code_viz.render_diff_view(
            self.get_active_file() or "main.py"
        )
        collab_matrix = self.code_viz.render_collaboration_matrix()
        
        # Arrange in layout
        top_row = Columns([file_tree, editor, timeline], equal=False)
        bottom_row = Columns([diff_view, collab_matrix], equal=True)
        
        return Group(top_row, bottom_row)
        
    def get_active_file(self) -> Optional[str]:
        """Get the currently active file"""
        # Find file with current editor
        for path, file in self.code_viz.files.items():
            if file.current_editor:
                return path
        # Return most recently modified
        if self.code_viz.files:
            return max(
                self.code_viz.files.items(),
                key=lambda x: x[1].last_modified
            )[0]
        return None


# Example usage function
def demo_code_visualization():
    """Demonstrate code visualization capabilities"""
    viz = CodeVisualizer()
    
    # Create some files
    viz.create_file("src/api/auth.py", "python")
    viz.create_file("src/frontend/Login.jsx", "javascript")
    viz.create_file("tests/test_auth.py", "python")
    
    # Simulate Marcus coding
    viz.simulate_typing(
        "Marcus Chen",
        """def authenticate_user(email: str, password: str) -> Optional[User]:
    user = db.query(User).filter_by(email=email).first()
    if user and user.verify_password(password):
        return user
    return None
""",
        "src/api/auth.py"
    )
    viz.commit_typing("Marcus Chen", "src/api/auth.py")
    
    # Simulate Emily coding
    viz.simulate_typing(
        "Emily Rodriguez",
        """const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    await login({ email, password });
  };
""",
        "src/frontend/Login.jsx"
    )
    viz.commit_typing("Emily Rodriguez", "src/frontend/Login.jsx")
    
    # Simulate Alex reviewing
    viz.add_review_comment(
        "Alex Thompson",
        "src/api/auth.py",
        3,
        "Add rate limiting to prevent brute force attacks"
    )
    
    # Create session and render
    session = LiveCodeSession(viz)
    workspace = session.render_coding_workspace()
    
    console = Console()
    console.print(workspace)