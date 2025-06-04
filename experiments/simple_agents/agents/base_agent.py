"""
Simplified base agent for experimentation.
NO COMPLEX FEATURES - just the bare minimum.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class SimpleAgent:
    """Minimal agent implementation for testing patterns."""
    
    def __init__(self, name: str, role: str, workspace_dir: str = "workspace"):
        self.id = str(uuid.uuid4())[:8]  # Short ID for readability
        self.name = name
        self.role = role
        self.workspace = Path(workspace_dir)
        self.state_file = self.workspace / "state" / f"{name.lower()}_state.json"
        self.current_task = None
        self.conversation_state = []
        
        # Create directories
        self.workspace.mkdir(exist_ok=True)
        (self.workspace / "state").mkdir(exist_ok=True)
        (self.workspace / "messages").mkdir(exist_ok=True)
        
    def receive_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process an incoming message."""
        msg_type = message.get("type", "unknown")
        
        if msg_type == "task":
            return self.handle_task(message)
        elif msg_type == "handoff":
            return self.handle_handoff(message)
        elif msg_type == "query":
            return self.handle_query(message)
        else:
            return {"error": f"Unknown message type: {msg_type}"}
    
    def handle_task(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a task assignment."""
        self.current_task = message.get("task")
        self.conversation_state = message.get("conversation_state", [])
        
        # Save state
        self.save_state()
        
        # Process task (to be overridden by subclasses)
        result = self.process_task(self.current_task)
        
        return {
            "type": "task_result",
            "agent": self.name,
            "task_id": self.current_task.get("id"),
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def handle_handoff(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a handoff from another agent."""
        from_agent = message.get("from_agent")
        self.conversation_state = message.get("conversation_state", [])
        context = message.get("context", {})
        
        # Add handoff to conversation state
        self.conversation_state.append({
            "type": "handoff",
            "from": from_agent,
            "to": self.name,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        
        # Save state
        self.save_state()
        
        return {
            "type": "handoff_acknowledged",
            "agent": self.name,
            "ready": True
        }
    
    def handle_query(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a status query."""
        return {
            "type": "status",
            "agent": self.name,
            "role": self.role,
            "current_task": self.current_task,
            "state_length": len(self.conversation_state)
        }
    
    def handoff_to(self, target_agent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Hand off control to another agent."""
        handoff_msg = {
            "type": "handoff",
            "from_agent": self.name,
            "to_agent": target_agent,
            "conversation_state": self.conversation_state,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
        # Write to message file for target agent
        msg_file = self.workspace / "messages" / f"{target_agent.lower()}_pending.json"
        with open(msg_file, 'w') as f:
            json.dump(handoff_msg, f, indent=2)
        
        return handoff_msg
    
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task. Override in subclasses."""
        return {
            "status": "completed",
            "output": f"{self.name} processed task: {task.get('description', 'unknown')}"
        }
    
    def save_state(self):
        """Save agent state to file."""
        state = {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "current_task": self.current_task,
            "conversation_state": self.conversation_state,
            "last_updated": datetime.now().isoformat()
        }
        
        self.state_file.parent.mkdir(exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self):
        """Load agent state from file."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                self.current_task = state.get("current_task")
                self.conversation_state = state.get("conversation_state", [])
    
    def think(self, prompt: str) -> str:
        """Simulate LLM thinking. Override for real LLM calls."""
        return f"[{self.name} thinking about: {prompt}]"

    def __repr__(self):
        return f"SimpleAgent({self.name}, role={self.role})"