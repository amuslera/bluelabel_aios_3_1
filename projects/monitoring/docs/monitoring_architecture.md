# Monitoring System Architecture

## Overview
Real-time monitoring system for AIOSv3 agents with <1s latency goal.

## Architecture Decision
After analyzing requirements, I've chosen a **hybrid approach**:
1. Primary: WebSocket for real-time updates
2. Fallback: File-based monitoring for reliability

## Components

### 1. Agent Logger
```python
# Each agent includes this logger
class AgentActivityLogger:
    """Logs all agent activities with structured data."""
    
    def log_activity(self, activity_type: str, details: dict):
        # Send via WebSocket if connected
        # Write to file as backup
        pass
```

### 2. Message Format
```json
{
    "timestamp": "2025-05-31T14:23:41.123Z",
    "agent_id": "backend_12345",
    "agent_name": "Backend Developer",
    "activity_type": "file_operation",
    "details": {
        "operation": "create",
        "file_path": "/src/models/user.py",
        "lines_added": 145
    },
    "task_id": "TASK-176",
    "progress": 82
}
```

### 3. Data Flow
```
Agent Activity → Logger → WebSocket/File → Monitor Service → Terminal UI
```

## Implementation Plan
1. Backend team: Implement logger and streaming
2. Frontend team: Build terminal UI
3. QA team: Test with high message volumes
