#!/usr/bin/env python3
"""
Live Three-Way Collaboration Terminal

Real-time terminal interface for Human + Claude Code + CTO Agent collaboration.
Shows the conversation flow and allows human input in real-time.
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from typing import Optional, List, Dict, Any

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.specialists.cto_agent import create_cto_agent, CTOAgent
from agents.base.enhanced_agent import EnhancedTask, EnhancedTaskResult
from agents.base.types import TaskType
from core.routing.router import LLMRouter, RoutingPolicy, RoutingStrategy
from core.routing.providers.claude import ClaudeProvider, ClaudeConfig
from core.routing.providers.mock_provider import MockProvider, MockConfig


class CollaborationTerminal:
    """Interactive terminal for three-way collaboration."""
    
    def __init__(self):
        self.cto_agent: Optional[CTOAgent] = None
        self.conversation_history: List[Dict[str, Any]] = []
        self.session_start = datetime.now()
        self.total_cost = 0.0
        
    def print_banner(self):
        """Print the collaboration banner."""
        print("=" * 80)
        print("🚀 AIOSv3 LIVE THREE-WAY COLLABORATION TERMINAL")
        print("=" * 80)
        print("👥 Participants:")
        print("   👤 Human (you)")  
        print("   🤖 Claude Code (orchestrating)")
        print("   👨‍💼 CTO Agent (technical decisions)")
        print("=" * 80)
        print("💡 Commands:")
        print("   'help' - Show available commands")
        print("   'status' - Show agent and session status")
        print("   'history' - Show conversation history")
        print("   'clear' - Clear screen")
        print("   'quit' - Exit collaboration")
        print("=" * 80)
        print()
    
    def print_separator(self, title: str = ""):
        """Print a visual separator."""
        if title:
            print(f"\n{'─' * 20} {title} {'─' * (57 - len(title))}")
        else:
            print("─" * 80)
    
    def print_message(self, speaker: str, message: str, metadata: Dict[str, Any] = None):
        """Print a formatted message in the conversation."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Speaker icons and colors
        icons = {
            "human": "👤",
            "claude_code": "🤖", 
            "cto_agent": "👨‍💼"
        }
        
        icon = icons.get(speaker, "💬")
        
        print(f"\n[{timestamp}] {icon} {speaker.replace('_', ' ').title()}:")
        print("─" * 40)
        
        # Format message with proper indentation
        lines = message.split('\n')
        for line in lines:
            print(f"  {line}")
        
        # Show metadata if provided
        if metadata:
            print("\n📊 Metadata:")
            for key, value in metadata.items():
                if key in ['cost', 'execution_time', 'tokens_used', 'model_used']:
                    print(f"   {key}: {value}")
        
        print("─" * 40)
    
    async def setup_cto_agent(self) -> bool:
        """Set up the CTO Agent with LLM routing."""
        try:
            print("🔧 Setting up CTO Agent and LLM routing...")
            
            # Create router with cost-optimized policy
            policy = RoutingPolicy(
                strategy=RoutingStrategy.COST_OPTIMIZED,
                max_cost_per_request=0.25,  # $0.25 max per request
                max_response_time_ms=45000,  # 45 seconds for complex analysis
                fallback_providers=["claude"]
            )
            
            router = LLMRouter(default_policy=policy)
            
            # Configure Claude provider
            api_key = os.getenv("ANTHROPIC_API_KEY", "mock-key-for-testing")
            claude_config = ClaudeConfig(
                provider_name="claude",
                api_key=api_key,
                timeout=45.0,
                max_retries=3
            )
            
            claude_provider = ClaudeProvider(claude_config)
            router.register_provider("claude", claude_provider)
            
            # Initialize router
            await router.initialize()
            
            # Check if providers are healthy
            provider_status = await router.get_provider_status()
            healthy_providers = [
                name for name, status in provider_status.items()
                if status.get("stats", {}).get("initialized", False)
            ]
            
            if not healthy_providers:
                print("⚠️  Claude API not available, using mock provider for demo...")
                
                # Create new router with mock provider
                mock_router = LLMRouter(default_policy=policy)
                mock_config = MockConfig(
                    provider_name="mock",
                    response_delay=1.5  # Simulate thinking time
                )
                mock_provider = MockProvider(mock_config)
                mock_router.register_provider("mock", mock_provider)
                await mock_router.initialize()
                router = mock_router
                print("✅ Mock provider ready for demonstration")
            else:
                print(f"✅ Real Claude API connected: {healthy_providers}")
            
            # Create CTO agent
            self.cto_agent = await create_cto_agent({
                "temperature": 0.3,  # More consistent for technical decisions
                "max_tokens": 4096
            })
            
            # Replace router
            self.cto_agent.router = router
            
            print(f"✅ CTO Agent ready: {self.cto_agent.agent_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup CTO Agent: {e}")
            return False
    
    def add_to_history(self, speaker: str, message: str, metadata: Dict[str, Any] = None):
        """Add message to conversation history."""
        self.conversation_history.append({
            "timestamp": datetime.now(),
            "speaker": speaker,
            "message": message,
            "metadata": metadata or {}
        })
    
    async def handle_human_input(self, user_input: str) -> bool:
        """Handle human input and coordinate responses."""
        
        # Add human message to history
        self.add_to_history("human", user_input)
        self.print_message("human", user_input)
        
        # Claude Code (me) analyzing and routing
        claude_code_response = "Let me consult our CTO Agent for a technical analysis of this question..."
        self.add_to_history("claude_code", claude_code_response)
        self.print_message("claude_code", claude_code_response)
        
        # Show thinking indicator
        print("🤔 CTO Agent thinking", end="", flush=True)
        for _ in range(3):
            await asyncio.sleep(0.5)
            print(".", end="", flush=True)
        print(" 💭")
        
        # Create task for CTO Agent
        task = EnhancedTask(
            task_type=self._determine_task_type(user_input),
            prompt=user_input,
            complexity=self._estimate_complexity(user_input),
            metadata={
                "conversation_context": "live_collaboration",
                "session_id": str(self.session_start.timestamp()),
                "human_participant": True
            }
        )
        
        # Process with CTO Agent
        start_time = time.time()
        result = await self.cto_agent.process_task(task)
        execution_time = time.time() - start_time
        
        # Track costs
        if result.success:
            self.total_cost += result.cost
        
        # Show CTO Agent response
        if result.success:
            metadata = {
                "cost": f"${result.cost:.4f}",
                "execution_time": f"{execution_time:.2f}s",
                "tokens_used": result.tokens_used,
                "model_used": result.model_used,
                "provider_used": result.provider_used
            }
            self.add_to_history("cto_agent", result.output, metadata)
            self.print_message("cto_agent", result.output, metadata)
        else:
            error_msg = f"I encountered an error while analyzing your question: {result.error}"
            self.add_to_history("cto_agent", error_msg)
            self.print_message("cto_agent", error_msg)
        
        return True
    
    def _determine_task_type(self, user_input: str) -> TaskType:
        """Determine the best task type for the input."""
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ["architecture", "design", "system"]):
            return TaskType.SYSTEM_DESIGN
        elif any(word in user_lower for word in ["code", "review", "implementation"]):
            return TaskType.CODE_REVIEW
        elif any(word in user_lower for word in ["decision", "choose", "recommend", "should we"]):
            return TaskType.TECH_DECISION
        elif any(word in user_lower for word in ["plan", "strategy", "roadmap"]):
            return TaskType.PLANNING
        else:
            return TaskType.GENERAL
    
    def _estimate_complexity(self, user_input: str) -> int:
        """Estimate task complexity from 1-10."""
        # Simple heuristic based on question length and keywords
        base_complexity = min(len(user_input.split()) // 10, 5) + 3
        
        complex_keywords = ["architecture", "scalability", "security", "performance", "integration"]
        if any(keyword in user_input.lower() for keyword in complex_keywords):
            base_complexity += 2
        
        return min(base_complexity, 10)
    
    def show_status(self):
        """Show current session status."""
        self.print_separator("SESSION STATUS")
        
        if self.cto_agent:
            status = self.cto_agent.get_status()
            print(f"🆔 CTO Agent ID: {status['agent_id']}")
            print(f"🔄 State: {status['lifecycle_state']}")
            print(f"✅ Tasks completed: {status['tasks_completed']}")
            print(f"📈 Success rate: {status['success_rate']:.1%}")
        
        print(f"💰 Total session cost: ${self.total_cost:.4f}")
        print(f"⏱️  Session duration: {datetime.now() - self.session_start}")
        print(f"💬 Messages exchanged: {len(self.conversation_history)}")
        
        self.print_separator()
    
    def show_history(self):
        """Show conversation history."""
        self.print_separator("CONVERSATION HISTORY")
        
        for entry in self.conversation_history[-10:]:  # Last 10 messages
            timestamp = entry["timestamp"].strftime("%H:%M:%S")
            speaker = entry["speaker"].replace("_", " ").title()
            message = entry["message"][:100] + "..." if len(entry["message"]) > 100 else entry["message"]
            
            print(f"[{timestamp}] {speaker}: {message}")
        
        if len(self.conversation_history) > 10:
            print(f"... and {len(self.conversation_history) - 10} more messages")
        
        self.print_separator()
    
    def show_help(self):
        """Show help information."""
        self.print_separator("COLLABORATION COMMANDS")
        print("💡 Available commands:")
        print("   help     - Show this help message")
        print("   status   - Show CTO Agent and session status")
        print("   history  - Show recent conversation history")
        print("   clear    - Clear the terminal screen")
        print("   quit     - Exit the collaboration session")
        print("")
        print("🎯 How to collaborate:")
        print("   • Ask technical questions about AIOSv3 architecture")
        print("   • Request technology recommendations")
        print("   • Discuss implementation strategies")
        print("   • Get code review feedback")
        print("   • Plan technical roadmaps")
        print("")
        print("📝 Example questions:")
        print("   • Should we use microservices or monolith for the agent registry?")
        print("   • How should we implement authentication for inter-agent communication?")
        print("   • What's the best approach for agent state persistence?")
        self.print_separator()
    
    async def run(self):
        """Run the interactive collaboration terminal."""
        self.print_banner()
        
        # Setup CTO Agent
        if not await self.setup_cto_agent():
            print("❌ Failed to initialize collaboration. Exiting.")
            return
        
        print("🎉 Three-way collaboration ready!")
        print("💭 Ask me anything about AIOSv3 architecture, and I'll work with the CTO Agent to help you.")
        print("   Type 'help' for commands or start asking technical questions...")
        
        try:
            while True:
                print("\n" + "─" * 80)
                user_input = input("👤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                elif user_input.lower() == 'status':
                    self.show_status()
                    continue
                elif user_input.lower() == 'history':
                    self.show_history()
                    continue
                elif user_input.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    self.print_banner()
                    continue
                
                # Handle collaborative input
                await self.handle_human_input(user_input)
        
        except KeyboardInterrupt:
            print("\n\n👋 Collaboration interrupted by user")
        except Exception as e:
            print(f"\n❌ Error during collaboration: {e}")
        
        finally:
            # Cleanup
            if self.cto_agent:
                print("\n🧹 Shutting down CTO Agent...")
                await self.cto_agent.stop()
            
            # Show final stats
            print(f"\n📊 Final session stats:")
            print(f"   💰 Total cost: ${self.total_cost:.4f}")
            print(f"   ⏱️  Duration: {datetime.now() - self.session_start}")
            print(f"   💬 Messages: {len(self.conversation_history)}")
            print("\n👋 Thanks for collaborating! See you next time.")


async def main():
    """Main entry point."""
    terminal = CollaborationTerminal()
    await terminal.run()


if __name__ == "__main__":
    # Run the collaboration terminal
    asyncio.run(main())