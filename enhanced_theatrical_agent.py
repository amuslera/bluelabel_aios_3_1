#!/usr/bin/env python3
"""
Enhanced Theatrical Agent - Faster with strategic engagement

70% faster base speed but with:
- Progress bars for multi-step operations
- Thinking pauses at key decision points
- Status indicators and animations
- Smooth transitions between phases
"""

import asyncio
import json
import time
import random
import subprocess
import sys
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from datetime import datetime
from enum import Enum
from contextlib import asynccontextmanager

# Define agent capabilities
class AgentCapability(Enum):
    DESIGN = "design"
    CODING = "coding"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    API_DESIGN = "api_design"
    DATABASE = "database"
    UI_DESIGN = "ui_design"
    METRICS = "metrics"
    PLANNING = "planning"

# Agent personas with adjusted speeds
ENHANCED_PERSONAS = {
    'monitor': {
        'name': 'Diana Martinez',
        'emoji': '📊',
        'color': '\033[94m',  # Blue
        'thinking_phrases': [
            "Analyzing monitoring requirements",
            "Considering real-time data flow",
            "Evaluating visualization options",
            "Planning metric collection"
        ],
        'decision_style': 'data-driven',
        'base_typing_speed': 0.01,  # Much faster
        'thinking_time': (1.5, 3.0)  # Shorter pauses
    },
    'backend': {
        'name': 'Marcus Chen',
        'emoji': '⚙️',
        'color': '\033[92m',  # Green
        'thinking_phrases': [
            "Designing API structure",
            "Optimizing for performance",
            "Planning error handling",
            "Considering scalability"
        ],
        'decision_style': 'systematic',
        'base_typing_speed': 0.008,
        'thinking_time': (1.5, 3.0)
    },
    'frontend': {
        'name': 'Alex Rivera',
        'emoji': '🎨',
        'color': '\033[95m',  # Purple
        'thinking_phrases': [
            "Visualizing user interface",
            "Planning component architecture",
            "Considering user experience",
            "Designing interactions"
        ],
        'decision_style': 'user-centric',
        'base_typing_speed': 0.012,
        'thinking_time': (1.5, 3.0)
    },
    'architect': {
        'name': 'Sarah Kim',
        'emoji': '🏗️',
        'color': '\033[96m',  # Cyan
        'thinking_phrases': [
            "Analyzing system architecture",
            "Evaluating design patterns",
            "Planning integration points",
            "Considering future scalability"
        ],
        'decision_style': 'holistic',
        'base_typing_speed': 0.015,
        'thinking_time': (2.0, 3.5)
    }
}

class ProgressBar:
    """Animated progress bar for long operations."""
    
    def __init__(self, total: int, description: str, color: str = '\033[0m'):
        self.total = total
        self.current = 0
        self.description = description
        self.color = color
        self.reset = '\033[0m'
        self.start_time = time.time()
        
    def update(self, step_description: str = ""):
        """Update progress bar."""
        self.current += 1
        percentage = (self.current / self.total) * 100
        filled = int((self.current / self.total) * 30)
        bar = '█' * filled + '░' * (30 - filled)
        
        elapsed = time.time() - self.start_time
        if self.current > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
            eta_str = f" ETA: {int(eta)}s"
        else:
            eta_str = ""
        
        print(f"\r{self.color}[{bar}] {percentage:3.0f}% - {step_description:<40}{eta_str}{self.reset}", 
              end='', flush=True)
        
        if self.current >= self.total:
            print()  # New line when complete

class EnhancedTheatricalAgent:
    """
    Enhanced theatrical agent with better pacing and engagement.
    70% faster but with strategic pauses and progress visualization.
    """
    
    def __init__(self, agent_id: str, name: str, capabilities: List[str], 
                 llm_config: dict, knowledge_base: dict = None):
        """Initialize enhanced theatrical agent."""
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.llm_config = llm_config
        self.knowledge_base = knowledge_base or {}
        
        # Enhanced theatrical properties
        self.role = agent_id.split('_')[0] if '_' in agent_id else 'backend'
        self.persona = ENHANCED_PERSONAS.get(self.role, ENHANCED_PERSONAS['backend'])
        self.theatrical_name = self.persona['name']
        self.emoji = self.persona['emoji']
        self.color = self.persona['color']
        self.reset = '\033[0m'
        self.typing_speed = self.persona['base_typing_speed']
        self.thinking_time = self.persona['thinking_time']
        
        # Performance settings
        self.enable_theatrical = True
        self.show_typing = True
        self.show_thinking = True
        self.show_progress = True
        
        # Status tracking
        self.current_task = None
        self.current_phase = None
        
    def print_colored(self, text: str, end='\n'):
        """Print with agent's color."""
        print(f"{self.color}{text}{self.reset}", end=end, flush=True)
    
    async def type_fast(self, text: str, prefix: str = ""):
        """Type text quickly but visibly."""
        if prefix:
            print(f"{self.color}{prefix} ", end='', flush=True)
            
        if self.show_typing and self.enable_theatrical:
            # Type in chunks for speed
            words = text.split()
            for i, word in enumerate(words):
                print(f"{self.color}{word}", end='', flush=True)
                if i < len(words) - 1:
                    print(" ", end='', flush=True)
                await asyncio.sleep(self.typing_speed * len(word))
            print(self.reset)
        else:
            print(f"{self.color}{text}{self.reset}")
    
    async def think_with_animation(self, context: str = None, duration: float = None):
        """Show thinking with animated dots - only at key moments."""
        if not self.show_thinking or not self.enable_theatrical:
            return
            
        if duration is None:
            duration = random.uniform(*self.thinking_time)
            
        # Choose thought based on context
        if context:
            thought = f"{context}"
        else:
            thought = random.choice(self.persona['thinking_phrases'])
        
        print(f"{self.color}{self.emoji} ", end='', flush=True)
        
        # Quick animation
        start_time = time.time()
        animation = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        i = 0
        
        while time.time() - start_time < duration:
            print(f"\r{self.color}{self.emoji} {animation[i % len(animation)]} {thought}...", 
                  end='', flush=True)
            await asyncio.sleep(0.1)
            i += 1
        
        print(f"\r{self.color}{self.emoji} ✓ {thought}    {self.reset}")
        await asyncio.sleep(0.3)
    
    @asynccontextmanager
    async def progress_context(self, description: str, steps: int):
        """Context manager for progress bar operations."""
        if self.show_progress and self.enable_theatrical:
            progress = ProgressBar(steps, description, self.color)
            self.print_colored(f"\n📋 {description}")
            yield progress
            await asyncio.sleep(0.5)
        else:
            # Dummy progress object
            class DummyProgress:
                def update(self, desc=""): pass
            yield DummyProgress()
    
    async def show_status(self, status: str, icon: str = "•"):
        """Show a quick status update."""
        self.print_colored(f"{icon} {status}")
        await asyncio.sleep(0.2)
    
    async def phase_transition(self, phase: str, icon: str = "🔄"):
        """Smooth transition between phases."""
        self.current_phase = phase
        print()  # Empty line
        self.print_colored(f"{icon} {phase}")
        self.print_colored("─" * 50)
        await asyncio.sleep(0.5)
    
    async def show_code_block(self, filename: str, code: str, description: str = None):
        """Show code being written with fast display."""
        self.print_colored(f"\n📝 Creating: {filename}")
        
        if description:
            await self.type_fast(description, prefix="💡")
            await asyncio.sleep(0.3)
        
        # Show code quickly but visibly
        self.print_colored("```python")
        
        lines = code.split('\n')
        # Show first 15 lines with very fast typing
        for i, line in enumerate(lines[:15]):
            if line.strip():
                print(f"{self.color}{line}{self.reset}")
                await asyncio.sleep(0.01)  # Very brief pause per line
        
        if len(lines) > 15:
            self.print_colored(f"... [{len(lines) - 15} more lines]")
            
        self.print_colored("```")
        await asyncio.sleep(0.5)
    
    async def make_decision(self, decision: str, options: List[Dict[str, Any]], 
                          choice: str, reasoning: str):
        """Show decision making process quickly."""
        await self.phase_transition(f"Decision: {decision}", "🤔")
        
        # Quick option display
        for i, option in enumerate(options, 1):
            self.print_colored(f"\n  Option {i}: {option['name']}")
            if 'pros' in option:
                self.print_colored(f"    ✅ {option['pros']}")
            if 'cons' in option:
                self.print_colored(f"    ⚠️  {option['cons']}")
            await asyncio.sleep(0.2)
        
        # Brief thinking
        await self.think_with_animation("weighing options", duration=1.5)
        
        # Decision
        self.print_colored(f"\n✅ Decision: {choice}")
        await self.type_fast(reasoning, prefix="📋")
        await asyncio.sleep(0.5)
    
    async def run_command(self, cmd: list, description: str = None) -> subprocess.CompletedProcess:
        """Run command with quick visual feedback."""
        desc = description or "Running command"
        
        if self.enable_theatrical:
            await self.show_status(desc, "🔧")
            cmd_str = ' '.join(cmd)
            self.print_colored(f"  $ {cmd_str}")
            
            # Quick execution animation
            print(f"{self.color}  ⚡ ", end='', flush=True)
            for _ in range(3):
                print(".", end='', flush=True)
                await asyncio.sleep(0.1)
        
        # Run actual command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if self.enable_theatrical:
            if result.returncode == 0:
                print(f" ✅{self.reset}")
            else:
                print(f" ❌{self.reset}")
                if result.stderr:
                    self.print_colored(f"  Error: {result.stderr.strip()}")
            await asyncio.sleep(0.3)
        
        return result
    
    async def narrate(self, message: str, detail: str = None):
        """Quick narration of actions."""
        await self.show_status(message, self.emoji)
        if detail:
            await self.type_fast(detail, prefix="  →")
    
    async def complete_task(self, task_name: str):
        """Mark task as complete with celebration."""
        print()
        self.print_colored(f"✅ {task_name} complete!")
        await asyncio.sleep(0.5)
    
    def set_performance_mode(self, mode: str):
        """Adjust performance settings."""
        if mode == 'fast':
            self.show_typing = False
            self.show_thinking = False
            self.show_progress = True
        elif mode == 'balanced':
            self.show_typing = True
            self.show_thinking = True
            self.show_progress = True
        elif mode == 'detailed':
            self.show_typing = True
            self.show_thinking = True
            self.show_progress = True
            self.typing_speed *= 2  # Slower


# Factory function
def create_enhanced_agent(role: str, capabilities: List[str], 
                         llm_config: dict) -> EnhancedTheatricalAgent:
    """Create an enhanced theatrical agent."""
    agent_id = f"{role}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    name = f"{role.title()} Agent"
    
    return EnhancedTheatricalAgent(
        agent_id=agent_id,
        name=name,
        capabilities=capabilities,
        llm_config=llm_config
    )


# Demo function to show the improvements
async def demo_enhanced_pacing():
    """Demonstrate the enhanced pacing."""
    print("\n🎭 ENHANCED THEATRICAL AGENT DEMO")
    print("=" * 50)
    print("70% faster with strategic engagement")
    print("=" * 50 + "\n")
    
    # Create agent
    agent = create_enhanced_agent(
        'backend',
        ['coding', 'api_design', 'testing'],
        {'model': 'gpt-4', 'temperature': 0.7}
    )
    
    # Introduction
    await agent.narrate(
        f"Hello! I'm {agent.theatrical_name}",
        "Let me show you the enhanced pacing"
    )
    
    # Show progress bar for multi-step task
    async with agent.progress_context("Building API endpoints", 5) as progress:
        steps = [
            "Setting up server framework",
            "Creating data models",
            "Implementing endpoints",
            "Adding validation",
            "Writing tests"
        ]
        
        for step in steps:
            progress.update(step)
            await asyncio.sleep(0.5)  # Simulate work
    
    # Quick decision
    await agent.make_decision(
        "API Framework",
        [
            {'name': 'FastAPI', 'pros': 'Modern, fast, great docs'},
            {'name': 'Flask', 'pros': 'Simple, flexible'}
        ],
        "FastAPI",
        "Better for async operations and automatic validation"
    )
    
    # Show code creation
    code = """from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Monitoring API")

class Activity(BaseModel):
    agent_id: str
    activity_type: str
    timestamp: float
    details: dict

@app.post("/activities")
async def create_activity(activity: Activity):
    # Store activity
    await store_activity(activity)
    return {"status": "success", "id": generate_id()}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}"""
    
    await agent.show_code_block(
        "api_server.py",
        code,
        "Implementing FastAPI server with type safety"
    )
    
    # Quick command
    await agent.run_command(
        ['echo', 'API server ready!'],
        "Testing server output"
    )
    
    # Complete
    await agent.complete_task("API implementation")
    
    print("\n✨ Demo complete! Notice:")
    print("  • Faster typing and transitions")
    print("  • Progress bars for long operations")
    print("  • Strategic thinking pauses")
    print("  • Clear status indicators")


if __name__ == "__main__":
    asyncio.run(demo_enhanced_pacing())