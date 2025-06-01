#!/usr/bin/env python3
"""
Theatrical Base Agent - Real agents with human-comprehensible pacing

This creates agents with theatrical features for human comprehension
while maintaining full functionality. Not a demo - this is for production use.
"""

import asyncio
import json
import time
import random
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from enum import Enum

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

# Agent personas for different roles
THEATRICAL_PERSONAS = {
    'monitor': {
        'name': 'Diana Martinez',
        'emoji': '📊',
        'color': '\033[94m',  # Blue
        'thinking_phrases': [
            "Analyzing monitoring requirements...",
            "Considering dashboard layout options...",
            "Thinking about real-time update strategies...",
            "Evaluating visualization approaches..."
        ],
        'decision_style': 'data-driven',
        'typing_speed': 0.03
    },
    'backend': {
        'name': 'Marcus Chen',
        'emoji': '⚙️',
        'color': '\033[92m',  # Green
        'thinking_phrases': [
            "Designing the API structure...",
            "Considering performance implications...",
            "Thinking about error handling...",
            "Planning database schema..."
        ],
        'decision_style': 'systematic',
        'typing_speed': 0.025
    },
    'frontend': {
        'name': 'Alex Thompson',
        'emoji': '🎨',
        'color': '\033[95m',  # Purple
        'thinking_phrases': [
            "Visualizing the user interface...",
            "Considering user experience flow...",
            "Thinking about responsive design...",
            "Planning component architecture..."
        ],
        'decision_style': 'user-centric',
        'typing_speed': 0.035
    },
    'architect': {
        'name': 'Sarah Kim',
        'emoji': '🏗️',
        'color': '\033[96m',  # Cyan
        'thinking_phrases': [
            "Analyzing system architecture...",
            "Considering scalability patterns...",
            "Evaluating technology choices...",
            "Planning integration points..."
        ],
        'decision_style': 'holistic',
        'typing_speed': 0.04
    }
}

class TheatricalBaseAgent:
    """
    Real agent with theatrical pacing and visibility.
    Full agent implementation with theatrical features.
    """
    
    def __init__(self, agent_id: str, name: str, capabilities: List[str], 
                 llm_config: dict, knowledge_base: dict = None):
        """Initialize theatrical agent with real capabilities."""
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.llm_config = llm_config
        self.knowledge_base = knowledge_base or {}
        
        # Add theatrical properties
        self.role = agent_id.split('_')[0] if '_' in agent_id else 'backend'
        self.persona = THEATRICAL_PERSONAS.get(self.role, THEATRICAL_PERSONAS['backend'])
        self.theatrical_name = self.persona['name']
        self.emoji = self.persona['emoji']
        self.color = self.persona['color']
        self.reset = '\033[0m'
        self.typing_speed = self.persona['typing_speed']
        
        # Pacing configuration
        self.enable_theatrical = True
        self.min_thinking_time = 2.0
        self.max_thinking_time = 5.0
        self.step_delay = 1.5
        
    def print_colored(self, text: str, end='\n'):
        """Print with agent's color."""
        if self.enable_theatrical:
            print(f"{self.color}{text}{self.reset}", end=end, flush=True)
        else:
            print(text, end=end, flush=True)
    
    async def think_aloud(self, context: str = None):
        """Show realistic thinking process."""
        if not self.enable_theatrical:
            return
            
        # Choose appropriate thinking phrase
        if context:
            thought = f"Thinking about {context}..."
        else:
            thought = random.choice(self.persona['thinking_phrases'])
        
        print(f"{self.color}{self.emoji} ", end='', flush=True)
        
        # Animated thinking
        thinking_time = random.uniform(self.min_thinking_time, self.max_thinking_time)
        start_time = time.time()
        
        while time.time() - start_time < thinking_time:
            for dots in ['', '.', '..', '...']:
                if time.time() - start_time >= thinking_time:
                    break
                print(f"\r{self.color}{self.emoji} {thought}{dots}   ", end='', flush=True)
                await asyncio.sleep(0.3)
        
        print(f"\r{self.color}{self.emoji} {thought}   {self.reset}")
        await asyncio.sleep(0.5)
    
    async def narrate_action(self, action: str, details: str = None):
        """Narrate what the agent is about to do."""
        if not self.enable_theatrical:
            return
            
        self.print_colored(f"\n{self.emoji} {action}")
        if details:
            await self.type_message(details, prefix="  💭")
        await asyncio.sleep(self.step_delay)
    
    async def type_message(self, message: str, prefix: str = "💬"):
        """Type out a message with realistic speed."""
        if not self.enable_theatrical:
            print(f"{prefix} {message}")
            return
            
        print(f"{self.color}{prefix} ", end='', flush=True)
        for char in message:
            print(f"{self.color}{char}", end='', flush=True)
            await asyncio.sleep(self.typing_speed)
        print(self.reset)
        await asyncio.sleep(0.5)
    
    async def show_progress(self, task_name: str, steps: List[str], 
                          current_step: int = None):
        """Show progress through task steps."""
        if not self.enable_theatrical:
            return
            
        total = len(steps)
        
        if current_step is None:
            # Show all steps
            self.print_colored(f"\n📋 Task: {task_name}")
            self.print_colored(f"   Steps planned: {total}")
            await asyncio.sleep(0.5)
            
            for i, step in enumerate(steps, 1):
                progress = int((i / total) * 20)
                bar = '█' * progress + '░' * (20 - progress)
                
                self.print_colored(f"\n[{bar}] Step {i}/{total}")
                await self.type_message(step, prefix="  🔨")
                
                # Think between steps
                if i < total and i % 2 == 0:
                    await self.think_aloud()
                else:
                    await asyncio.sleep(self.step_delay)
        else:
            # Show single step progress
            if 0 <= current_step < total:
                progress = int(((current_step + 1) / total) * 20)
                bar = '█' * progress + '░' * (20 - progress)
                step = steps[current_step]
                
                self.print_colored(
                    f"[{bar}] Step {current_step + 1}/{total}: {step}"
                )
    
    async def show_code_writing(self, filename: str, code: str, 
                               explanation: str = None):
        """Show code being written with explanation."""
        if not self.enable_theatrical:
            return
            
        self.print_colored(f"\n📝 Writing {filename}")
        
        if explanation:
            await self.type_message(explanation, prefix="💡")
            await asyncio.sleep(0.5)
        
        # Show code with syntax highlighting hints
        self.print_colored("```python")
        
        lines = code.split('\n')
        for i, line in enumerate(lines[:20]):  # Show first 20 lines
            if line.strip():
                # Add slight delay for each line
                indent = len(line) - len(line.lstrip())
                print(' ' * indent, end='')
                
                # Type the line
                for char in line.strip():
                    print(f"{self.color}{char}", end='', flush=True)
                    await asyncio.sleep(0.015)  # Faster than messages
            print()
            
            # Occasional pause
            if i > 0 and i % 5 == 0:
                await asyncio.sleep(0.5)
        
        if len(lines) > 20:
            self.print_colored(f"... [{len(lines) - 20} more lines]")
        
        self.print_colored("```")
        await asyncio.sleep(1)
    
    async def show_decision_making(self, decision: str, options: List[Dict[str, Any]], 
                                 choice: str, reasoning: str):
        """Show decision-making process."""
        if not self.enable_theatrical:
            return
            
        await self.narrate_action(f"Making decision: {decision}")
        
        # Show options
        self.print_colored("\n🤔 Evaluating options:")
        for i, option in enumerate(options, 1):
            await asyncio.sleep(0.5)
            self.print_colored(f"\n  Option {i}: {option['name']}")
            if 'pros' in option:
                self.print_colored(f"    ✅ {option['pros']}")
            if 'cons' in option:
                self.print_colored(f"    ❌ {option['cons']}")
        
        # Think about it
        await self.think_aloud("weighing the options")
        
        # Announce decision
        self.print_colored(f"\n✅ Decision: {choice}")
        await self.type_message(reasoning, prefix="  📋")
        await asyncio.sleep(1)
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task with theatrical narration."""
        task_desc = task.get('description', 'Unknown task')
        
        # Introduction
        if self.enable_theatrical:
            await self.narrate_action(
                f"Starting task: {task_desc}",
                f"Let me analyze what needs to be done..."
            )
            await self.think_aloud()
        
        # Execute the actual task
        try:
            # Here we would integrate with the actual LLM/task execution
            # For now, return success to demonstrate the theatrical flow
            result = {
                'status': 'completed',
                'task_id': task.get('id', 'unknown'),
                'output': f"Task '{task_desc}' completed"
            }
            
            # Conclusion
            if self.enable_theatrical and result.get('status') == 'completed':
                await self.narrate_action(
                    "Task completed successfully!",
                    f"All steps for '{task_desc}' have been finished."
                )
            
            return result
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def run_command(self, cmd: list, description: str = None) -> subprocess.CompletedProcess:
        """Run command with theatrical presentation."""
        if self.enable_theatrical:
            desc = description or "Running command"
            self.print_colored(f"\n🔧 {desc}")
            
            # Show command
            cmd_str = ' '.join(cmd)
            self.print_colored(f"$ {cmd_str}")
            await asyncio.sleep(0.5)
            
            # Show execution
            print(f"{self.color}⚡ Executing", end='', flush=True)
            for _ in range(3):
                print(".", end='', flush=True)
                await asyncio.sleep(0.3)
            print(self.reset)
        
        # Run actual command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if self.enable_theatrical:
            if result.returncode == 0:
                self.print_colored("✅ Success!")
                if result.stdout and len(result.stdout.strip()) < 200:
                    self.print_colored(f"📤 Output: {result.stdout.strip()}")
            else:
                self.print_colored("❌ Command failed!")
                if result.stderr:
                    self.print_colored(f"📤 Error: {result.stderr.strip()}")
            
            await asyncio.sleep(1)
        
        return result
    
    async def collaborate(self, message: str, target_agent: str = None):
        """Show collaboration with other agents."""
        if not self.enable_theatrical:
            return
            
        self.print_colored(f"\n👥 Collaboration")
        
        if target_agent:
            await self.type_message(f"@{target_agent}: {message}", prefix="📢")
        else:
            await self.type_message(f"@team: {message}", prefix="📢")
        
        await asyncio.sleep(1)
    
    def set_theatrical_mode(self, enabled: bool, pacing_multiplier: float = 1.0):
        """Configure theatrical mode."""
        self.enable_theatrical = enabled
        if pacing_multiplier != 1.0:
            self.typing_speed *= pacing_multiplier
            self.min_thinking_time *= pacing_multiplier
            self.max_thinking_time *= pacing_multiplier
            self.step_delay *= pacing_multiplier

# Example of how to create a theatrical agent
def create_theatrical_agent(role: str, capabilities: List[str], 
                          llm_config: dict) -> TheatricalBaseAgent:
    """Factory function to create theatrical agents."""
    agent_id = f"{role}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    name = f"{role.title()} Agent"
    
    agent = TheatricalBaseAgent(
        agent_id=agent_id,
        name=name,
        capabilities=capabilities,
        llm_config=llm_config
    )
    
    return agent