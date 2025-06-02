"""
Agent Activity Logger for AIOSv3 Monitoring System

This module provides logging functionality for all agent activities.
Following junior developer practices: clear code, extensive comments.
"""

import json
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
import websockets
from pathlib import Path


class AgentActivityLogger:
    """
    Logs all agent activities for real-time monitoring.
    
    This logger sends activities via WebSocket when available,
    with file-based fallback for reliability.
    """
    
    def __init__(self, agent_id: str, agent_name: str, agent_role: str):
        """
        Initialize the logger for a specific agent.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_name: Human-readable name (e.g., "Backend Developer")
            agent_role: Agent role (e.g., "backend", "frontend")
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.agent_role = agent_role
        self.websocket = None
        self.connected = False
        self.log_file = Path(f"logs/{agent_id}.jsonl")
        
        # Create logs directory if it doesn't exist
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Current task tracking
        self.current_task_id = None
        self.task_start_time = None
        self.task_progress = 0
        
        print(f"Logger initialized for {agent_name}")
    
    async def connect(self, monitor_url: str = "ws://localhost:6793"):
        """
        Connect to the monitoring service via WebSocket.
        
        Args:
            monitor_url: WebSocket URL of monitoring service
        """
        try:
            self.websocket = await websockets.connect(monitor_url)
            self.connected = True
            print(f"✅ Connected to monitoring service")
            
            # Send initial registration
            await self._send_activity("agent_connected", {
                "agent_role": self.agent_role,
                "status": "ready"
            })
        except Exception as e:
            print(f"⚠️  Could not connect to monitor: {e}")
            print(f"   Falling back to file-based logging")
            self.connected = False
    
    async def log_activity(self, activity_type: str, details: Dict[str, Any]):
        """
        Log an agent activity.
        
        Args:
            activity_type: Type of activity (e.g., "file_created", "task_started")
            details: Dictionary with activity-specific details
        """
        # Create activity record
        activity = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "activity_type": activity_type,
            "details": details,
            "task_id": self.current_task_id,
            "progress": self.task_progress
        }
        
        # Try to send via WebSocket
        if self.connected:
            try:
                await self._send_activity(activity_type, details)
            except:
                self.connected = False
                print("⚠️  Lost connection to monitor")
        
        # Always write to file as backup
        self._write_to_file(activity)
    
    async def _send_activity(self, activity_type: str, details: Dict[str, Any]):
        """Send activity via WebSocket."""
        if self.websocket:
            message = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "activity_type": activity_type,
                "details": details,
                "task_id": self.current_task_id,
                "progress": self.task_progress
            }
            await self.websocket.send(json.dumps(message))
    
    def _write_to_file(self, activity: Dict[str, Any]):
        """Write activity to log file."""
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(activity) + '\n')
    
    async def start_task(self, task_id: str, description: str):
        """Log task start."""
        self.current_task_id = task_id
        self.task_start_time = time.time()
        self.task_progress = 0
        
        await self.log_activity("task_started", {
            "task_id": task_id,
            "description": description
        })
    
    async def update_progress(self, progress: int, message: str = ""):
        """Update task progress."""
        self.task_progress = progress
        
        await self.log_activity("progress_update", {
            "progress": progress,
            "message": message
        })
    
    async def complete_task(self, summary: str):
        """Log task completion."""
        duration = time.time() - self.task_start_time if self.task_start_time else 0
        
        await self.log_activity("task_completed", {
            "task_id": self.current_task_id,
            "duration_seconds": duration,
            "summary": summary
        })
        
        self.current_task_id = None
        self.task_progress = 100


# Example usage
async def example_usage():
    """Show how to use the logger."""
    logger = AgentActivityLogger(
        agent_id="backend_12345",
        agent_name="Backend Developer",
        agent_role="backend"
    )
    
    # Connect to monitor
    await logger.connect()
    
    # Log various activities
    await logger.start_task("TASK-101", "Implement user authentication")
    
    await logger.log_activity("decision_made", {
        "decision": "Use JWT for authentication",
        "reasoning": "Stateless and scalable"
    })
    
    await logger.update_progress(25, "Created user model")
    
    await logger.log_activity("file_created", {
        "file_path": "/src/models/user.py",
        "lines": 89
    })
    
    await logger.update_progress(50, "Implemented auth endpoints")
    
    await logger.complete_task("Authentication system implemented")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
