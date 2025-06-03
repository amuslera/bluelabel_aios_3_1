# Theatrical Monitoring Dashboard - Technical Guide

## Overview

The Theatrical Monitoring Dashboard is a real-time visualization system for multi-agent AI orchestration. It provides a rich Terminal User Interface (TUI) that displays agent activities, inter-agent communications, performance metrics, and project progress in a theatrical, human-observable manner.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Launch Script                             │
│              (launch_theatrical_demo.py)                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
┌───────┴────────┐         ┌───────┴────────┐
│   Dashboard    │         │  Orchestrator  │
│   (TUI App)    │◄────────┤   (Backend)    │
└────────────────┘ Events  └────────────────┘
        │                           │
        │                           │
┌───────┴────────┐         ┌───────┴────────┐
│ Textual UI     │         │ Agent System   │
│ Components     │         │ (5 AI Agents)  │
└────────────────┘         └────────────────┘
```

### Core Modules

1. **launch_theatrical_demo.py**
   - Entry point with interactive menu
   - Supports multiple demo modes (Console, Dashboard, Side-by-Side, Quick Demo, Custom)
   - Handles process management and mode selection

2. **theatrical_monitoring_dashboard.py**
   - Main TUI application using Textual framework
   - Real-time event processing and display
   - Multi-tab interface (Agents, Full Log, Performance)
   - Export functionality for logs and metrics

3. **theatrical_orchestrator.py**
   - Backend orchestration logic
   - Manages agent lifecycle and task distribution
   - Generates theatrical events with deliberate timing
   - Tracks performance metrics

4. **Agent System**
   - 6 specialized agents: System, CTO, Backend, Frontend, QA, DevOps
   - Each agent has a name and role
   - Enhanced mock provider for demo mode
   - Real LLM integration capability

## Data Flow

### Event System

The dashboard uses an event-driven architecture:

```python
class TheatricalEvent:
    - event_type: str (SYSTEM, INIT, THINKING, TASK, SUCCESS, ERROR, PHASE, DETAILS)
    - agent_id: str (orchestrator, cto-001, backend-001, etc.)
    - agent_role: str (display name)
    - message: str (event description)
    - details: Dict[str, Any] (optional metadata)
    - timestamp: datetime
```

### Real-time Updates

1. **Event Generation**: Orchestrator creates events during task execution
2. **Event Queue**: Events are queued in `orchestrator.events` list
3. **Monitor Loop**: Dashboard polls for new events every 50ms (20Hz)
4. **Batch Processing**: Multiple events processed together before UI refresh
5. **UI Update**: Three views updated simultaneously:
   - Agent panels (status, progress, current task)
   - Full Log (chronological event stream)
   - Performance table (metrics aggregation)

### A2A Communication Detection

The system detects agent-to-agent messages by:
- Pattern matching for markdown headers (`##`, `#`)
- Keywords: "Task:", "Implementation:", "Summary:"
- Special formatting with 📨 emoji
- Message truncation to 100 characters

## UI Components

### 1. Project Info Header
- Displays project description
- Shows team composition with agent names
- Fixed yellow border, 5 lines height

### 2. Agent Panels (Main Tab)
- 2x3 grid layout (was vertical stack)
- Each panel shows:
  - Color square + Agent name + Role
  - Current task status
  - Progress bar
  - Activity history (scrollable, last 100 items)
  - Metrics (tasks, time, cost, tokens)

### 3. Full Log Tab
- Chronological event stream
- Color-coded by agent type
- A2A message detection and formatting
- Scrollable with 500 event limit

### 4. Performance Tab
- DataTable with agent metrics
- Includes agent names column
- Real-time updates
- Totalization row with summary

## Color Scheme

```css
System (SYS):    🟦 blue ($primary)
CTO:             ⬜ white (cyan text)
Backend (BE):    🟩 green ($success)
Frontend (FE):   🟪 purple (magenta text)
QA:              🟧 orange ($warning)
DevOps (DO):     🟥 red ($error)
```

## Dependencies

### Python Requirements
```python
# Core
python >= 3.9
asyncio  # Built-in async support

# UI Framework
textual >= 0.41.0  # Terminal UI framework
rich >= 13.0.0     # Rich text formatting

# Project Dependencies
python-dotenv      # Environment variable management
pydantic          # Data validation
httpx             # Async HTTP client (for real LLM mode)

# Development
logging           # Built-in logging
datetime          # Built-in timestamps
typing            # Type hints
re                # Regular expressions
```

### Installation
```bash
pip install textual rich python-dotenv pydantic httpx
```

## Configuration

### Agent Mapping
```python
AGENT_NAMES = {
    "orchestrator": "System",
    "cto-001": "Sarah Chen",
    "backend-001": "Marcus Chen",
    "frontend-001": "Emily Rodriguez",
    "qa-001": "Alex Thompson",
    "devops-001": "Jordan Kim"
}
```

### Timing Configuration
- Theatrical delay: 1.0-2.0 seconds (configurable)
- UI refresh rate: 20Hz (50ms)
- Event buffer: 500 events max
- Activity history: 100 items per agent

## Key Features

### 1. Real-time Synchronization
- All three views update simultaneously
- Batch event processing for efficiency
- Force refresh after updates
- Yield control with `asyncio.sleep(0)`

### 2. Performance Tracking
- Per-agent metrics (tasks, time, cost, tokens)
- Real-time aggregation
- Export to CSV functionality
- Phase timing breakdown

### 3. Export Capabilities
- Full conversation log (JSON)
- Performance metrics (CSV)
- Organized export directory structure
- Timestamped filenames

### 4. Mock vs Real Mode
- Enhanced mock provider for demos
- Real LLM integration support
- Cost-optimized routing
- Provider selection per agent

## Usage Patterns

### Basic Operation
```bash
# Launch the interactive menu
python3 launch_theatrical_demo.py

# Select option 2 for Dashboard Mode
# Press 's' to start demo
# Press 'q' to quit
# Press 'e' to export logs
# Press 'p' to export performance
# Press 'r' to reset
```

### Custom Configuration
```python
# In theatrical_orchestrator.py
orchestrator = TheatricalOrchestrator(
    theatrical_delay=1.5,  # Seconds between major actions
    show_details=True      # Show cost/time metrics
)
```

## Extending the System

### Adding New Agents
1. Add agent ID to `AGENT_NAMES` mapping
2. Create agent class extending `EnhancedBaseAgent`
3. Add to orchestrator initialization
4. Update UI color scheme if needed

### Custom Events
1. Define new event types
2. Add handling in `_update_agent_from_event()`
3. Update event formatting in `log_event()`

### New UI Components
1. Add new TabPane in `compose()`
2. Create custom widget class
3. Update event processing loop
4. Add to refresh cycle

## Performance Considerations

- UI updates batched for efficiency
- Scrollable containers limit displayed items
- Event history capped at 500 entries
- Activity logs limited to 100 per agent
- Force refresh used sparingly

## Troubleshooting

### Common Issues
1. **Delayed updates**: Increase refresh rate (decrease sleep time)
2. **Color conflicts**: Check terminal theme compatibility
3. **Memory usage**: Reduce history limits
4. **Export failures**: Check directory permissions

### Debug Mode
Enable debug logging:
```python
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler('theatrical_debug.log', mode='w'),
        logging.StreamHandler()  # Add for console output
    ]
)
```

## Future Enhancements

1. **Team Chat Tab**: Dedicated A2A messaging view
2. **Workflow Visualization**: Task dependency graphs
3. **Metrics Dashboard**: Advanced analytics
4. **Real-time Collaboration**: Multi-user support
5. **Plugin System**: Extensible agent types

## License and Credits

Built with:
- Textual by Textualize
- Rich formatting library
- AIOSv3 agent framework

Theatrical timing and visualization concepts inspired by human-observable AI systems.