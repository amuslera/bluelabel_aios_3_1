"""
Theatrical Agent Orchestrator - Slowed down for human observation

This orchestrator manages agent interactions with deliberate delays and
rich visual feedback so humans can observe the multi-agent collaboration
process in real-time.
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# Import from v3.1 structure
import sys
from pathlib import Path
# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.agents.base.enhanced_agent import EnhancedBaseAgent, EnhancedTask
from src.agents.base.types import TaskType
from src.core.routing.router import LLMRouter, RoutingPolicy, RoutingStrategy
from src.core.routing.providers.claude import ClaudeProvider, ClaudeConfig
from src.core.routing.providers.openai import OpenAIProvider, OpenAIConfig
# Use v3.1's mock provider instead
from src.core.routing.providers.mock_provider import MockProvider, MockConfig

# Load environment variables
load_dotenv()

# Configure logging for theatrical display only when run directly
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)


class TheatricalEvent:
    """Represents a theatrical event in the orchestration."""

    def __init__(self, event_type: str, agent_id: str, agent_role: str,
                 message: str, details: Optional[Dict[str, Any]] = None):
        self.event_type = event_type
        self.agent_id = agent_id
        self.agent_role = agent_role
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()

    def __str__(self) -> str:
        time_str = self.timestamp.strftime("%H:%M:%S")
        return f"[{time_str}] {self.agent_role} ({self.agent_id}): {self.message}"


class TheatricalOrchestrator:
    """
    Orchestrator that manages agent interactions with theatrical timing
    for human observation and understanding.
    """

    def __init__(self, theatrical_delay: float = 1.0, show_details: bool = True):
        """
        Initialize theatrical orchestrator.

        Args:
            theatrical_delay: Seconds to pause between major actions
            show_details: Whether to show detailed task information
        """
        self.theatrical_delay = theatrical_delay
        self.show_details = show_details
        self.events: List[TheatricalEvent] = []
        self.agents: Dict[str, EnhancedBaseAgent] = {}
        self.router: Optional[LLMRouter] = None

        # Performance tracking
        self.start_time: Optional[float] = None
        self.phase_times: Dict[str, float] = {}
        self.total_cost = 0.0
        self.total_tokens = 0

    async def initialize(self) -> None:
        """Initialize the orchestrator and all agents."""
        self._log_event("SYSTEM", "orchestrator", "🎭 Initializing Theatrical Orchestrator...")
        await self._pause()

        # Initialize LLM router with cost-optimized strategy
        self._log_event("SYSTEM", "orchestrator", "🔧 Setting up LLM routing...")
        self.router = LLMRouter(
            default_policy=RoutingPolicy(
                strategy=RoutingStrategy.COST_OPTIMIZED,
                max_cost_per_request=0.50,
            )
        )
        
        # Configure LLM providers
        await self._setup_providers()
        
        # Initialize router after providers are registered
        await self.router.initialize()
        await self._pause()

        # Create and initialize agents
        await self._create_agents()

        self._log_event("SYSTEM", "orchestrator", "✅ Theatrical Orchestrator ready!")
        await self._pause()

    async def _create_agents(self) -> None:
        """Create and initialize all specialist agents."""
        # Import v3.1 agents
        from src.agents.specialists.backend_agent import BackendAgent
        from src.agents.specialists.frontend_agent import FrontendAgent
        from src.agents.specialists.qa_agent import QAAgent
        from src.agents.specialists.devops_agent import DevOpsAgent
        # CTO agent not yet implemented in v3.1, will use mock
        
        agent_configs = [
            ("cto-001", "🏛️ CTO Agent", CTOAgent, CTOAgentConfig),
            ("backend-001", "⚙️ Backend Developer", BackendDeveloperAgent, BackendAgentConfig),
            ("frontend-001", "🎨 Frontend Developer", FrontendDeveloperAgent, FrontendAgentConfig),
            ("qa-001", "🧪 QA Engineer", QAEngineerAgent, QAAgentConfig),
            ("devops-001", "🚀 DevOps Engineer", DevOpsEngineerAgent, DevOpsAgentConfig)
        ]

        for agent_id, display_name, agent_class, config_class in agent_configs:
            self._log_event("INIT", agent_id, f"Creating {display_name}...")
            
            # Create agent configuration
            config = config_class()
            
            # Create agent instance WITHOUT initializing
            agent = agent_class(config)
            
            # CRITICAL: Assign router BEFORE initialization
            agent.router = self.router
            
            # Now initialize the agent with router already set
            await agent.initialize()
            
            # Store the agent
            self.agents[agent_id] = agent
            
            await self._pause(1.0)  # Shorter pause for agent creation

    async def orchestrate_project(self, project_description: str) -> None:
        """
        Orchestrate a complete project with theatrical timing.

        Args:
            project_description: Description of the project to build
        """
        self.start_time = time.time()

        self._log_event("PROJECT", "orchestrator", f"🎬 Starting Project: {project_description}")
        await self._pause()

        # Phase 1: CTO Analysis and Architecture
        await self._phase_1_architecture(project_description)

        # Phase 2: Backend Development
        await self._phase_2_backend()

        # Phase 3: Frontend Development
        await self._phase_3_frontend()

        # Phase 4: QA Testing
        await self._phase_4_testing()

        # Phase 5: DevOps Deployment
        await self._phase_5_deployment()

        # Final Summary
        await self._show_final_summary()

    async def _phase_1_architecture(self, project_description: str) -> None:
        """Phase 1: CTO analyzes requirements and designs architecture."""
        phase_start = time.time()
        self._log_event("PHASE", "cto-001", "🏛️ Phase 1: Architecture & Planning")
        await self._pause()

        cto = self.agents["cto-001"]

        # CTO thinks about the project
        self._log_event("THINKING", "cto-001", "🤔 Analyzing project requirements...")
        await self._pause()

        # Create architecture task
        task = EnhancedTask(
            task_type=TaskType.SYSTEM_DESIGN,
            prompt=f"""
            As the CTO, analyze this project and create a comprehensive technical specification:

            Project: {project_description}

            Please provide:
            1. Technical architecture overview
            2. Technology stack recommendations
            3. Database design
            4. API specifications
            5. Frontend architecture
            6. Testing strategy
            7. Deployment approach

            Focus on creating a production-ready, scalable solution.
            """,
            complexity=8,
            metadata={"phase": "architecture", "project": project_description}
        )

        self._log_event("TASK", "cto-001", "📋 Creating technical specification...")
        await self._pause()

        result = await cto.process_task(task)
        self._update_metrics(result)

        if result.success:
            self._log_event("SUCCESS", "cto-001", "✅ Architecture specification completed!")
            if self.show_details:
                self._log_event("DETAILS", "cto-001", f"Cost: ${result.cost:.4f} | Time: {result.execution_time:.1f}s")
                # Show first 200 chars of output
                preview = result.output[:200] + "..." if len(result.output) > 200 else result.output
                self._log_event("OUTPUT", "cto-001", f"📄 Specification preview: {preview}")
        else:
            self._log_event("ERROR", "cto-001", f"❌ Architecture phase failed: {result.error}")

        self.phase_times["architecture"] = time.time() - phase_start
        await self._pause()

    async def _phase_2_backend(self) -> None:
        """Phase 2: Backend developer implements the API."""
        phase_start = time.time()
        self._log_event("PHASE", "backend-001", "⚙️ Phase 2: Backend Development")
        await self._pause()

        backend = self.agents["backend-001"]

        self._log_event("THINKING", "backend-001", "🤔 Reviewing architecture specifications...")
        await self._pause()

        task = EnhancedTask(
            task_type=TaskType.CODE_GENERATION,
            prompt="""
            Based on the CTO's architecture, implement a robust backend API with:

            1. FastAPI application structure
            2. Database models and migrations
            3. Authentication and authorization
            4. CRUD operations for main entities
            5. Input validation and error handling
            6. API documentation
            7. Unit tests

            Focus on clean, maintainable, production-ready code.
            """,
            complexity=7,
            metadata={"phase": "backend", "component": "api"}
        )

        self._log_event("TASK", "backend-001", "💻 Implementing backend API...")
        await self._pause()

        result = await backend.process_task(task)
        self._update_metrics(result)

        if result.success:
            self._log_event("SUCCESS", "backend-001", "✅ Backend API implementation completed!")
            if self.show_details:
                self._log_event("DETAILS", "backend-001", f"Cost: ${result.cost:.4f} | Time: {result.execution_time:.1f}s")
                lines = result.output.count('\n')
                self._log_event("OUTPUT", "backend-001", f"📊 Generated {lines} lines of backend code")
        else:
            self._log_event("ERROR", "backend-001", f"❌ Backend development failed: {result.error}")

        self.phase_times["backend"] = time.time() - phase_start
        await self._pause()

    async def _phase_3_frontend(self) -> None:
        """Phase 3: Frontend developer creates the user interface."""
        phase_start = time.time()
        self._log_event("PHASE", "frontend-001", "🎨 Phase 3: Frontend Development")
        await self._pause()

        frontend = self.agents["frontend-001"]

        self._log_event("THINKING", "frontend-001", "🤔 Designing user interface components...")
        await self._pause()

        task = EnhancedTask(
            task_type=TaskType.CODE_GENERATION,
            prompt="""
            Create a modern, responsive frontend application with:

            1. React components with TypeScript
            2. State management (Redux/Context)
            3. API integration with the backend
            4. User authentication flow
            5. Responsive design with CSS/Tailwind
            6. Form validation and error handling
            7. Component tests

            Focus on excellent user experience and accessibility.
            """,
            complexity=6,
            metadata={"phase": "frontend", "component": "ui"}
        )

        self._log_event("TASK", "frontend-001", "🎨 Building user interface...")
        await self._pause()

        result = await frontend.process_task(task)
        self._update_metrics(result)

        if result.success:
            self._log_event("SUCCESS", "frontend-001", "✅ Frontend application completed!")
            if self.show_details:
                self._log_event("DETAILS", "frontend-001", f"Cost: ${result.cost:.4f} | Time: {result.execution_time:.1f}s")
                lines = result.output.count('\n')
                self._log_event("OUTPUT", "frontend-001", f"📊 Generated {lines} lines of frontend code")
        else:
            self._log_event("ERROR", "frontend-001", f"❌ Frontend development failed: {result.error}")

        self.phase_times["frontend"] = time.time() - phase_start
        await self._pause()

    async def _phase_4_testing(self) -> None:
        """Phase 4: QA engineer creates comprehensive tests."""
        phase_start = time.time()
        self._log_event("PHASE", "qa-001", "🧪 Phase 4: Quality Assurance")
        await self._pause()

        qa = self.agents["qa-001"]

        self._log_event("THINKING", "qa-001", "🤔 Analyzing application for test coverage...")
        await self._pause()

        task = EnhancedTask(
            task_type=TaskType.TESTING,
            prompt="""
            Create a comprehensive testing suite including:

            1. Unit tests for backend API endpoints
            2. Integration tests for database operations
            3. Frontend component tests
            4. End-to-end user flow tests
            5. Performance and load tests
            6. Security vulnerability tests
            7. CI/CD test automation

            Ensure high test coverage and quality validation.
            """,
            complexity=6,
            metadata={"phase": "testing", "component": "quality_assurance"}
        )

        self._log_event("TASK", "qa-001", "🧪 Creating test suite...")
        await self._pause()

        result = await qa.process_task(task)
        self._update_metrics(result)

        if result.success:
            self._log_event("SUCCESS", "qa-001", "✅ Test suite completed!")
            if self.show_details:
                self._log_event("DETAILS", "qa-001", f"Cost: ${result.cost:.4f} | Time: {result.execution_time:.1f}s")
                lines = result.output.count('\n')
                self._log_event("OUTPUT", "qa-001", f"📊 Generated {lines} lines of test code")
        else:
            self._log_event("ERROR", "qa-001", f"❌ Testing phase failed: {result.error}")

        self.phase_times["testing"] = time.time() - phase_start
        await self._pause()

    async def _phase_5_deployment(self) -> None:
        """Phase 5: DevOps engineer sets up deployment infrastructure."""
        phase_start = time.time()
        self._log_event("PHASE", "devops-001", "🚀 Phase 5: Deployment & Infrastructure")
        await self._pause()

        devops = self.agents["devops-001"]

        self._log_event("THINKING", "devops-001", "🤔 Planning deployment infrastructure...")
        await self._pause()

        task = EnhancedTask(
            task_type=TaskType.INFRASTRUCTURE,
            prompt="""
            Set up production deployment infrastructure including:

            1. Docker containerization
            2. Kubernetes deployment manifests
            3. CI/CD pipeline configuration
            4. Monitoring and logging setup
            5. Security configurations
            6. Database migration scripts
            7. Load balancing and scaling

            Ensure production-ready, scalable infrastructure.
            """,
            complexity=8,
            metadata={"phase": "deployment", "component": "infrastructure"}
        )

        self._log_event("TASK", "devops-001", "🚀 Setting up deployment pipeline...")
        await self._pause()

        result = await devops.process_task(task)
        self._update_metrics(result)

        if result.success:
            self._log_event("SUCCESS", "devops-001", "✅ Deployment infrastructure completed!")
            if self.show_details:
                self._log_event("DETAILS", "devops-001", f"Cost: ${result.cost:.4f} | Time: {result.execution_time:.1f}s")
                lines = result.output.count('\n')
                self._log_event("OUTPUT", "devops-001", f"📊 Generated {lines} lines of infrastructure code")
        else:
            self._log_event("ERROR", "devops-001", f"❌ Deployment phase failed: {result.error}")

        self.phase_times["deployment"] = time.time() - phase_start
        await self._pause()

    async def _show_final_summary(self) -> None:
        """Show final project summary and metrics."""
        total_time = time.time() - self.start_time if self.start_time else 0

        self._log_event("SUMMARY", "orchestrator", "🎉 Project Orchestration Complete!")
        await self._pause()

        self._log_event("METRICS", "orchestrator", "📊 Final Project Metrics:")
        self._log_event("METRICS", "orchestrator", f"   Total Time: {total_time:.1f} seconds")
        self._log_event("METRICS", "orchestrator", f"   Total Cost: ${self.total_cost:.4f}")
        self._log_event("METRICS", "orchestrator", f"   Total Tokens: {self.total_tokens:,}")

        await self._pause()

        self._log_event("METRICS", "orchestrator", "⏱️ Phase Breakdown:")
        for phase, phase_time in self.phase_times.items():
            percentage = (phase_time / total_time * 100) if total_time > 0 else 0
            self._log_event("METRICS", "orchestrator", f"   {phase.title()}: {phase_time:.1f}s ({percentage:.1f}%)")

        await self._pause()

        self._log_event("COMPLETION", "orchestrator", "🏁 All agents have completed their tasks successfully!")

    def _log_event(self, event_type: str, agent_id: str, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log a theatrical event."""
        # Map agent IDs to display roles
        role_map = {
            "orchestrator": "🎭 Orchestrator",
            "cto-001": "🏛️ CTO",
            "backend-001": "⚙️ Backend Dev",
            "frontend-001": "🎨 Frontend Dev",
            "qa-001": "🧪 QA Engineer",
            "devops-001": "🚀 DevOps Engineer"
        }

        role = role_map.get(agent_id, agent_id)
        event = TheatricalEvent(event_type, agent_id, role, message, details)
        self.events.append(event)

        # Print with color coding
        color_map = {
            "SYSTEM": "\033[94m",      # Blue
            "PHASE": "\033[95m",       # Magenta
            "THINKING": "\033[93m",    # Yellow
            "TASK": "\033[96m",        # Cyan
            "SUCCESS": "\033[92m",     # Green
            "ERROR": "\033[91m",       # Red
            "DETAILS": "\033[90m",     # Gray
            "OUTPUT": "\033[90m",      # Gray
            "METRICS": "\033[97m",     # White
            "SUMMARY": "\033[95m",     # Magenta
            "COMPLETION": "\033[92m"   # Green
        }

        color = color_map.get(event_type, "\033[0m")
        reset = "\033[0m"

        print(f"{color}{event}{reset}")

    async def _pause(self, duration: Optional[float] = None) -> None:
        """Pause for theatrical effect."""
        await asyncio.sleep(duration or self.theatrical_delay)

    def _update_metrics(self, result) -> None:
        """Update performance metrics."""
        if hasattr(result, 'cost'):
            self.total_cost += result.cost
        if hasattr(result, 'token_usage') and result.token_usage:
            self.total_tokens += result.token_usage.get('total', 0)

    async def shutdown(self) -> None:
        """Shutdown the orchestrator and all agents."""
        self._log_event("SYSTEM", "orchestrator", "🔄 Shutting down agents...")

        for agent_id, agent in self.agents.items():
            try:
                await agent.stop()
                self._log_event("SYSTEM", agent_id, "✅ Agent shutdown complete")
            except Exception as e:
                self._log_event("ERROR", agent_id, f"❌ Shutdown error: {e}")

        self._log_event("SYSTEM", "orchestrator", "🎭 Theatrical Orchestrator shutdown complete")

    async def _setup_providers(self) -> None:
        """Setup LLM providers - prefer mock for theatrical demo."""
        
        # For theatrical demo, ALWAYS use mock provider for speed and reliability
        self._log_event("SYSTEM", "orchestrator", "🎭 Using mock provider for theatrical demo...")
        mock_config = MockConfig(
            provider_name="enhanced_mock",
            models=[
                {"id": "mock-cto-model", "context_window": 16384},
                {"id": "mock-backend-model", "context_window": 16384},
                {"id": "mock-frontend-model", "context_window": 16384},
                {"id": "mock-qa-model", "context_window": 16384},
                {"id": "mock-devops-model", "context_window": 16384},
            ],
            default_model_id="mock-cto-model",
        )
        mock_provider = EnhancedMockProvider(mock_config)
        await mock_provider.initialize()
        self.router.register_provider("enhanced_mock", mock_provider)
        await self._pause(1.0)
        
        self._log_event("SYSTEM", "orchestrator", "✅ Mock provider configured for fast theatrical demo")


# Demo function
async def demo_theatrical_orchestration():
    """Run a demonstration of theatrical orchestration."""
    print("🎭" + "="*80)
    print("    AIOSV3 THEATRICAL AGENT ORCHESTRATION DEMO")
    print("="*84)
    print()

    orchestrator = TheatricalOrchestrator(
        theatrical_delay=0.5,  # Fast 0.5 second pauses
        show_details=True
    )

    try:
        await orchestrator.initialize()

        project = "E-commerce Platform with real-time inventory, user authentication, payment processing, and admin dashboard"

        await orchestrator.orchestrate_project(project)

    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    asyncio.run(demo_theatrical_orchestration())
