"""
Activity storage with overflow to disk.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import deque


class PersistentActivityStore:
    """Activity store with disk persistence."""
    
    def __init__(self, memory_size: int = 1000, disk_path: str = "activities.jsonl"):
        self.memory_store = deque(maxlen=memory_size)
        self.disk_path = disk_path
        self.total_count = 0
        self._load_from_disk()
        
    def _load_from_disk(self):
        """Load recent activities from disk."""
        if os.path.exists(self.disk_path):
            with open(self.disk_path, 'r') as f:
                for line in f:
                    try:
                        activity = json.loads(line)
                        self.memory_store.append(activity)
                        self.total_count += 1
                    except json.JSONDecodeError:
                        pass
                        
    def add(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Add activity to store."""
        activity['id'] = self.total_count
        activity['timestamp'] = datetime.utcnow().isoformat()
        
        # Add to memory
        self.memory_store.append(activity)
        self.total_count += 1
        
        # Persist to disk
        with open(self.disk_path, 'a') as f:
            f.write(json.dumps(activity) + '\n')
            
        return activity
    
    def query(self, agent_id: Optional[str] = None, 
              limit: int = 100, 
              offset: int = 0) -> List[Dict[str, Any]]:
        """Query activities with filters."""
        activities = list(self.memory_store)
        
        if agent_id:
            activities = [a for a in activities if a.get('agent_id') == agent_id]
            
        return activities[offset:offset + limit]
