"""
Visualization module for AIOSv3.1

Provides theatrical dashboards and real-time agent monitoring.
"""

from .theatrical_adapter import TheatricalOrchestrator, TheatricalEvent, EventType, AgentAdapter
from .theatrical_dashboard import TheatricalDashboard

__all__ = [
    'TheatricalOrchestrator',
    'TheatricalEvent', 
    'EventType',
    'AgentAdapter',
    'TheatricalDashboard'
]