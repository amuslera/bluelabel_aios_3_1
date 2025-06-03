"""
Integration module to adapt v3.0 theatrical dashboard for v3.1 agents
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import v3.1 agent implementations
from src.agents.specialists.backend_agent import BackendAgent
from src.agents.specialists.frontend_agent import FrontendAgent
from src.agents.specialists.qa_agent import QAAgent
from src.agents.specialists.devops_agent import DevOpsAgent

# Map v3.0 agent types to v3.1 implementations
AGENT_MAPPING = {
    "backend-001": BackendAgent,
    "frontend-001": FrontendAgent,
    "qa-001": QAAgent,
    "devops-001": DevOpsAgent,
}

def create_v31_agent(agent_id: str, agent_type: str):
    """Create a v3.1 agent instance for the theatrical dashboard."""
    agent_class = AGENT_MAPPING.get(agent_id)
    if agent_class:
        return agent_class()
    return None
