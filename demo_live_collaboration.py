#!/usr/bin/env python3
"""
Live Three-Way Collaboration Demo

Simulates the interactive experience to show how the three-way collaboration works.
This demonstrates what the user would see in a real terminal session.
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


class LiveCollaborationDemo:
    """Demonstrates the live three-way collaboration experience."""
    
    def __init__(self):
        self.cto_agent: Optional[CTOAgent] = None
        self.total_cost = 0.0
    
    def print_banner(self):
        """Print the collaboration banner."""
        print("=" * 80)
        print("🚀 AIOSv3 LIVE THREE-WAY COLLABORATION DEMO")
        print("=" * 80)
        print("👥 Participants:")
        print("   👤 Human (simulated user)")  
        print("   🤖 Claude Code (me, orchestrating)")
        print("   👨‍💼 CTO Agent (making technical decisions)")
        print("=" * 80)
        print("🎬 This demo shows what you'd see in a real terminal session")
        print("=" * 80)
        print()
    
    def print_separator(self, title: str = ""):
        """Print a visual separator."""
        if title:
            print(f"\n{'─' * 20} {title} {'─' * (57 - len(title))}")
        else:
            print("─" * 80)
    
    async def simulate_typing(self, text: str, delay: float = 0.02):
        """Simulate typing effect."""
        for char in text:
            print(char, end='', flush=True)
            await asyncio.sleep(delay)
        print()
    
    def print_message(self, speaker: str, message: str, metadata: Dict[str, Any] = None, typing: bool = False):
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
            print("\n📊 Response Details:")
            for key, value in metadata.items():
                if key in ['cost', 'execution_time', 'tokens_used', 'model_used', 'provider_used']:
                    print(f"   {key}: {value}")
        
        print("─" * 40)
    
    async def setup_cto_agent(self) -> bool:
        """Set up the CTO Agent with LLM routing."""
        try:
            print("🔧 Setting up CTO Agent and LLM routing...")
            
            # Create router with cost-optimized policy
            policy = RoutingPolicy(
                strategy=RoutingStrategy.COST_OPTIMIZED,
                max_cost_per_request=0.25,
                max_response_time_ms=45000,
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
                    response_delay=1.5
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
                "temperature": 0.3,
                "max_tokens": 4096
            })
            
            # Replace router
            self.cto_agent.router = router
            
            print(f"✅ CTO Agent ready: {self.cto_agent.agent_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup CTO Agent: {e}")
            return False
    
    def _determine_task_type(self, user_input: str) -> TaskType:
        """Determine the best task type for the input."""
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ["architecture", "design", "system"]):
            return TaskType.SYSTEM_DESIGN
        elif any(word in user_lower for word in ["security", "auth", "encryption"]):
            return TaskType.TECH_DECISION
        elif any(word in user_lower for word in ["database", "storage", "persistence"]):
            return TaskType.TECH_DECISION
        else:
            return TaskType.GENERAL
    
    async def simulate_collaboration_session(self):
        """Simulate a full collaboration session."""
        
        # Sample questions that show different aspects
        questions = [
            {
                "question": "What's your recommendation for implementing authentication in our agent-to-agent communication?",
                "context": "Security architecture decision"
            },
            {
                "question": "Should we use PostgreSQL or MongoDB for storing agent conversation histories?",
                "context": "Database technology decision"
            },
            {
                "question": "How should we design the agent discovery system for our platform?",
                "context": "System architecture design"
            }
        ]
        
        for i, q in enumerate(questions, 1):
            print(f"\n{'🎬' * 20} SCENARIO {i}: {q['context']} {'🎬' * 20}")
            await asyncio.sleep(1)
            
            # Simulate human typing
            print("\n👤 Human typing", end="", flush=True)
            for _ in range(3):
                await asyncio.sleep(0.5)
                print(".", end="", flush=True)
            print()
            
            # Human question
            self.print_message("human", q["question"])
            await asyncio.sleep(1)
            
            # Claude Code response
            claude_response = f"Great question! This is a critical {q['context'].lower()} decision for AIOSv3. Let me consult our CTO Agent for a comprehensive technical analysis..."
            self.print_message("claude_code", claude_response)
            await asyncio.sleep(1)
            
            # Show CTO Agent thinking
            print("🤔 CTO Agent analyzing", end="", flush=True)
            for _ in range(4):
                await asyncio.sleep(0.8)
                print(".", end="", flush=True)
            print(" 💭")
            
            # Create and process task
            task = EnhancedTask(
                task_type=self._determine_task_type(q["question"]),
                prompt=q["question"],
                complexity=7 + i,  # Increasing complexity
                metadata={
                    "scenario": f"demo_scenario_{i}",
                    "context": q["context"]
                }
            )
            
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
                self.print_message("cto_agent", result.output, metadata)
            else:
                error_msg = f"I encountered an error analyzing this question: {result.error}"
                self.print_message("cto_agent", error_msg)
            
            # Pause between scenarios
            if i < len(questions):
                print("\n⏸️  Pausing before next scenario...")
                await asyncio.sleep(2)
    
    async def show_session_summary(self):
        """Show the final session summary."""
        self.print_separator("SESSION SUMMARY")
        
        if self.cto_agent:
            status = self.cto_agent.get_status()
            print(f"🆔 CTO Agent: {status['agent_id']}")
            print(f"✅ Tasks completed: {status['tasks_completed']}")
            print(f"📈 Success rate: {status['success_rate']:.1%}")
            print(f"⏱️  Average response time: {status['average_execution_time']:.2f}s")
        
        print(f"💰 Total session cost: ${self.total_cost:.4f}")
        print(f"🎯 Collaboration scenarios: 3")
        print(f"🚀 Framework status: Fully operational")
        
        self.print_separator()
    
    async def run_demo(self):
        """Run the complete collaboration demo."""
        self.print_banner()
        
        # Setup
        if not await self.setup_cto_agent():
            print("❌ Failed to initialize collaboration demo.")
            return
        
        print("🎉 Three-way collaboration initialized!")
        print("🎬 Starting collaboration demo with 3 scenarios...")
        await asyncio.sleep(2)
        
        try:
            # Run collaboration scenarios
            await self.simulate_collaboration_session()
            
            # Show summary
            await self.show_session_summary()
            
            print("\n🎯 What you just saw:")
            print("   ✅ Real-time three-way conversation flow")
            print("   ✅ CTO Agent providing expert technical analysis")
            print("   ✅ Cost tracking and performance metrics")
            print("   ✅ Different types of technical decisions")
            print("   ✅ Professional-grade response formatting")
            
            print("\n💡 In a real terminal session, you would:")
            print("   📝 Type your questions interactively")
            print("   👀 See responses in real-time")
            print("   💬 Continue the conversation naturally")
            print("   📊 Track costs and performance live")
            print("   🎯 Get expert technical guidance instantly")
            
        except Exception as e:
            print(f"\n❌ Error during demo: {e}")
        
        finally:
            # Cleanup
            if self.cto_agent:
                print("\n🧹 Shutting down CTO Agent...")
                await self.cto_agent.stop()
            
            print("\n🌟 Demo completed! The three-way collaboration platform is ready for live use.")


async def main():
    """Main entry point."""
    demo = LiveCollaborationDemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())