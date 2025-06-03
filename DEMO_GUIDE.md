# AIOSv3.1 Demo Guide

## Quick Start

Run the simplified launcher:
```bash
python3 launch_demo.py
```

This provides access to the three main working demos.

## Available Demos

### 1. Full Demo (`demo_final.py`)
**Duration**: ~2 minutes  
**Features**:
- Complete AI team collaboration
- Real-time chat between agents
- Progress tracking with metrics
- Dynamic layout that adapts to screen size
- Final summary integrated into progress panel

**Best for**: Showcasing the full platform capabilities

### 2. Quick Test (`demo_working_simple.py`)
**Duration**: ~30 seconds  
**Features**:
- Simple agent visualization
- Fast demonstration of collaboration
- Minimal dependencies
- No keyboard interaction issues

**Best for**: Quick functionality checks and simple demonstrations

### 3. Task Management Demo (`scripts/task_management_demo.py`)
**Duration**: ~3 minutes  
**Features**:
- Builds a complete task management system
- Shows actual code generation
- Demonstrates all 4 agents working together
- Includes realistic development phases

**Best for**: Demonstrating real-world application development

## Demo Architecture

### Working Demos
- `demo_final.py` - Production-ready with all UX improvements
- `demo_working_simple.py` - Simple, reliable visualization
- `scripts/task_management_demo.py` - Real project demonstration

### Archived Demos
Located in `archive/demo_iterations/`:
- Various experimental versions
- Iterations leading to final demo
- Kept for reference and learning

### Demos Needing Fixes
- `demo_end_to_end.py` - Has import issues but good concept
- `scripts/demo_orchestrator.py` - Agent import issues
- `scripts/demo_orchestrator_simple.py` - Agent import issues

## Running Individual Demos

```bash
# Full featured demo
python3 demo_final.py

# Quick test
python3 demo_working_simple.py

# Task management
python3 scripts/task_management_demo.py

# Legacy launcher (all versions)
python3 launch_real_demo.py
```

## Key Features Demonstrated

1. **Multi-Agent Collaboration**
   - Marcus Chen (Backend Engineer)
   - Emily Rodriguez (Frontend Developer)
   - Alex Thompson (QA Engineer)
   - Jordan Kim (DevOps Engineer)

2. **Real-Time Communication**
   - Team chat showing agent interactions
   - Phase-based development workflow
   - Collaborative problem solving

3. **Progress Tracking**
   - Task completion metrics
   - Cost tracking
   - Lines of code written
   - Test coverage percentage

4. **Professional UI**
   - Clean, aligned layouts
   - Dynamic sizing
   - Color-coded agent activities
   - Integrated final summary

## Customization

To modify demo behavior, edit:
- Agent activities in `phases` array
- Chat messages for different interactions
- Metrics and timing
- UI colors and layout proportions

## Troubleshooting

**Import Errors**: Some older demos have import issues due to agent class name changes:
- `DevOpsAgent` → `JordanDevOpsAgent`
- Missing `create_backend_agent` functions
- `TaskStatus` import that doesn't exist

**Display Issues**: If you see `<rich.table.Table object>` errors, the demo is trying to render objects as text. Use the fixed demos instead.

**Keyboard Issues**: Some demos tried to implement interactive controls but had platform compatibility issues. The current demos run automatically or use simple prompts.

## Future Improvements

1. **Web-based UI**: Create a web interface for richer visualization
2. **Real LLM Integration**: Connect actual LLM agents instead of simulations
3. **Recording/Playback**: Add ability to record and replay demo sessions
4. **Customizable Scenarios**: Allow users to define their own project types