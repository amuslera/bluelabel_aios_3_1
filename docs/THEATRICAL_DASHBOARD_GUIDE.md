# 🎭 Theatrical Dashboard Guide

## Overview

The Theatrical Dashboard provides a beautiful, real-time visualization of AI agents working together on software projects. It combines the elegant design from v3.0 with v3.1's robust agent architecture.

## Quick Start

### 1. Simple Demo (No Installation Required)
```bash
python3 demos/theatrical_dashboard_demo.py
```

### 2. Compare All Options
```bash
python3 demos/theatrical_comparison_demo.py
```

## Architecture

### Core Components

#### 1. **Theatrical Adapter** (`src/visualization/theatrical_adapter.py`)
- Bridges v3.0 UI concepts with v3.1 agents
- Provides event-driven updates
- Controls theatrical timing
- Manages agent lifecycle

Key Classes:
- `TheatricalEvent` - Event data structure
- `AgentAdapter` - Wraps v3.1 agents
- `TheatricalOrchestrator` - Coordinates agents

#### 2. **Standard Dashboard** (`src/visualization/theatrical_dashboard.py`)
- Rich-based terminal UI
- Real-time agent panels
- Event timeline
- System metrics

Features:
- 2x3 grid layout for 5 agents + system panel
- Scrollable event log
- Per-agent activity tracking
- Color-coded status indicators

#### 3. **Advanced Dashboard** (`src/visualization/theatrical_dashboard_advanced.py`)
- All standard features plus:
- Session recording to JSON
- Real LLM API integration
- Enhanced metrics
- Configurable options

## Usage Examples

### Basic Usage
```python
from src.visualization.theatrical_dashboard import TheatricalDashboard

async def main():
    dashboard = TheatricalDashboard()
    await dashboard.run()
```

### Advanced Usage with Custom Project
```python
from src.visualization.theatrical_dashboard_advanced import AdvancedTheatricalDashboard

async def main():
    dashboard = AdvancedTheatricalDashboard()
    
    # Configure options
    dashboard.config['theatrical_delay'] = 1.0  # Slower for demos
    dashboard.config['enable_export'] = True    # Save session
    
    # Run with custom phases
    phases = [
        {
            'name': 'Planning',
            'agent_id': 'cto-001',
            'tasks': ['Define requirements', 'Create architecture']
        },
        {
            'name': 'Implementation',
            'agent_id': 'backend-001',
            'tasks': ['Build API', 'Create database']
        }
    ]
    
    await dashboard.run_custom_project('My Project', phases)
```

### Real LLM Integration
```python
# The advanced dashboard supports real LLM calls
dashboard.config['show_raw_llm'] = True

# This will make actual API calls to Claude/OpenAI
# Warning: This incurs API costs!
```

## Visual Elements

### Agent Status Indicators
- ⚪ Idle - Agent is ready
- 🤔 Thinking - Analyzing task
- ⚙️ Working - Implementing
- ✅ Ready - Task complete
- ❌ Error - Task failed

### Agent Icons
- 🏛️ CTO (Sarah Chen)
- ⚙️ Backend (Marcus Chen)
- 🎨 Frontend (Emily Rodriguez)
- 🧪 QA (Alex Thompson)
- 🚀 DevOps (Jordan Kim)

### Color Coding
- **Magenta** - CTO/Architecture
- **Cyan** - Backend Development
- **Yellow** - Frontend/UI
- **Green** - QA/Testing
- **Blue** - DevOps/Infrastructure

## Session Export

The advanced dashboard can export sessions for analysis:

```python
# Sessions are automatically saved to:
data/sessions/theatrical_session_YYYYMMDD_HHMMSS.json

# Export contains:
- Session metadata
- Agent metrics
- Complete event log
- Timing information
```

## Configuration Options

### Standard Dashboard
```python
dashboard = TheatricalDashboard(
    max_events=50,      # Event log size
    max_agent_logs=10   # Per-agent log size
)
```

### Advanced Dashboard
```python
dashboard = AdvancedTheatricalDashboard()

# Available config options:
dashboard.config = {
    'theatrical_delay': 0.5,   # Delay between events (seconds)
    'show_raw_llm': False,     # Show raw LLM responses
    'enable_export': True,     # Enable session export
    'theme': 'default'         # Color theme
}
```

## Extending the Dashboard

### Custom Agent Styles
```python
dashboard.agent_styles['new-agent'] = {
    "icon": "🔧",
    "color": "purple",
    "name": "New Agent",
    "title": "Specialist",
    "skills": ["Skill1", "Skill2"]
}
```

### Custom Event Types
```python
from src.visualization.theatrical_adapter import EventType

# Emit custom events
event = TheatricalEvent(
    type=EventType.ACTIVITY,
    agent_id="backend-001",
    message="Custom activity",
    timestamp=datetime.now(),
    details={"custom": "data"}
)
orchestrator.emit_event(event)
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're running from the project root
   - Check that all dependencies are installed

2. **Display Issues**
   - Terminal must support Unicode and colors
   - Recommended: Modern terminal with 120+ columns

3. **Performance**
   - Reduce refresh rate if needed
   - Limit event log size for long sessions

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

1. **For Demos**
   - Use standard dashboard with mock LLMs
   - Increase theatrical_delay for visibility
   - Run in fullscreen terminal

2. **For Development**
   - Use advanced dashboard with export
   - Enable real LLM for testing
   - Monitor costs carefully

3. **For Production**
   - Implement error handling
   - Set appropriate log limits
   - Use session export for audit trails

## Summary

The theatrical dashboard brings v3.0's beautiful visualization to v3.1's robust agent platform. It provides multiple implementation options from simple demos to production-ready monitoring, all while maintaining the theatrical presentation that makes AI agent collaboration understandable and engaging.