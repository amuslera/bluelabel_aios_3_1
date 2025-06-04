"""
Simple file-based message bus for agent communication.
NO QUEUES, NO DATABASES - just JSON files.
"""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

class SimpleMessageBus:
    """File-based message passing system."""
    
    def __init__(self, workspace_dir: str = "workspace"):
        self.workspace = Path(workspace_dir)
        self.messages_dir = self.workspace / "messages"
        self.messages_dir.mkdir(parents=True, exist_ok=True)
        
    def send_message(self, to_agent: str, message: Dict[str, Any]) -> str:
        """Send a message to an agent by writing to their inbox."""
        # Add metadata
        message["id"] = f"msg_{int(time.time() * 1000)}"
        message["timestamp"] = datetime.now().isoformat()
        message["to"] = to_agent
        
        # Write to agent's inbox
        inbox_file = self.messages_dir / f"{to_agent.lower()}_inbox.json"
        
        # Read existing messages
        messages = self.read_inbox(to_agent)
        messages.append(message)
        
        # Write back
        with open(inbox_file, 'w') as f:
            json.dump(messages, f, indent=2)
        
        return message["id"]
    
    def read_inbox(self, agent_name: str) -> List[Dict[str, Any]]:
        """Read all messages for an agent."""
        inbox_file = self.messages_dir / f"{agent_name.lower()}_inbox.json"
        
        if inbox_file.exists():
            with open(inbox_file, 'r') as f:
                return json.load(f)
        return []
    
    def get_next_message(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get the next unprocessed message for an agent."""
        messages = self.read_inbox(agent_name)
        
        if messages:
            # Return first message
            return messages[0]
        return None
    
    def mark_processed(self, agent_name: str, message_id: str):
        """Mark a message as processed by removing it from inbox."""
        messages = self.read_inbox(agent_name)
        
        # Filter out processed message
        remaining = [msg for msg in messages if msg.get("id") != message_id]
        
        # Write back
        inbox_file = self.messages_dir / f"{agent_name.lower()}_inbox.json"
        with open(inbox_file, 'w') as f:
            json.dump(remaining, f, indent=2)
        
        # Archive the processed message
        self.archive_message(agent_name, next(
            (msg for msg in messages if msg.get("id") == message_id), 
            None
        ))
    
    def archive_message(self, agent_name: str, message: Optional[Dict[str, Any]]):
        """Archive a processed message."""
        if not message:
            return
            
        archive_dir = self.messages_dir / "archive"
        archive_dir.mkdir(exist_ok=True)
        
        archive_file = archive_dir / f"{agent_name.lower()}_processed.json"
        
        # Read existing archive
        if archive_file.exists():
            with open(archive_file, 'r') as f:
                archive = json.load(f)
        else:
            archive = []
        
        # Add processed timestamp
        message["processed_at"] = datetime.now().isoformat()
        archive.append(message)
        
        # Write back
        with open(archive_file, 'w') as f:
            json.dump(archive, f, indent=2)
    
    def broadcast(self, message: Dict[str, Any], agents: List[str]):
        """Send a message to multiple agents."""
        message["type"] = "broadcast"
        
        for agent in agents:
            self.send_message(agent, message.copy())
    
    def clear_all_messages(self):
        """Clear all message files (for testing)."""
        for msg_file in self.messages_dir.glob("*.json"):
            if msg_file.parent.name != "archive":
                msg_file.write_text("[]")
    
    def get_message_stats(self) -> Dict[str, Any]:
        """Get statistics about messages."""
        stats = {
            "total_pending": 0,
            "by_agent": {},
            "archived": 0
        }
        
        # Count pending messages
        for inbox_file in self.messages_dir.glob("*_inbox.json"):
            agent_name = inbox_file.stem.replace("_inbox", "")
            messages = self.read_inbox(agent_name)
            count = len(messages)
            
            stats["by_agent"][agent_name] = count
            stats["total_pending"] += count
        
        # Count archived
        archive_dir = self.messages_dir / "archive"
        if archive_dir.exists():
            for archive_file in archive_dir.glob("*_processed.json"):
                with open(archive_file, 'r') as f:
                    archived = json.load(f)
                    stats["archived"] += len(archived)
        
        return stats