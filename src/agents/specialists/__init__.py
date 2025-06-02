"""
Specialized AI agents for AIOSv3 platform.

Each agent has unique expertise and personality.
"""

from .backend_agent import BackendAgent, create_marcus_agent
from .frontend_agent import FrontendAgent, create_emily_agent

__all__ = [
    "BackendAgent",
    "create_marcus_agent",
    "FrontendAgent", 
    "create_emily_agent",
]