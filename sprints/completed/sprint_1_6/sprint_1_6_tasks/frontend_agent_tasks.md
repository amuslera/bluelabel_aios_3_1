# Frontend Agent Tasks - Sprint 1.6

**Agent**: Alex Rivera
**Role**: Frontend Developer
**Sprint**: 1.6 - Control Center & Agent Intelligence

## 🎯 Your Primary Tasks

### Task 1: CC-001 - Set up Control Center Project Structure
**Priority**: HIGH
**Estimated Time**: 2 hours

**Requirements**:
1. Create `control_center/` directory
2. Set up Textual-based TUI application
3. Create base layout with 4 panels:
   - Top Left: Agent Orchestra
   - Top Right: Activity Monitor
   - Bottom Left: Task Manager
   - Bottom Right: PR Review
4. Add keyboard shortcuts (q=quit, r=refresh, t=theme)

**Files to create**:
- `control_center/__init__.py`
- `control_center/main.py` - Main application
- `control_center/components/__init__.py`
- `control_center/styles.css` - Textual CSS

**Example Structure**:
```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import Grid

class ControlCenterApp(App):
    CSS_PATH = "styles.css"
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Grid(
            AgentOrchestraPanel(),
            ActivityMonitorPanel(),
            TaskManagerPanel(),
            PRReviewPanel(),
        )
        yield Footer()
```

### Task 2: CC-002 - Implement Agent Orchestra Panel
**Priority**: HIGH
**Estimated Time**: 3 hours

**Requirements**:
1. Display table of active agents with columns:
   - Status (🟢 active, 🟡 busy, 🔴 error)
   - Agent Name
   - Role
   - Current Task Progress %
2. Add "Launch Agent" button
3. Connect to Redis registry to get agent list
4. Auto-refresh every 5 seconds

**File to create**: `control_center/components/agent_orchestra.py`

**Acceptance Criteria**:
- [ ] Shows all registered agents
- [ ] Real-time status updates
- [ ] Launch button opens agent config dialog
- [ ] Handles connection errors gracefully

### Task 3: CC-003 - Implement Activity Monitor Panel
**Priority**: HIGH
**Estimated Time**: 3 hours

**Requirements**:
1. WebSocket client connection to monitoring server
2. Display scrolling activity feed
3. Color code by activity type:
   - Green: Success/Info
   - Yellow: Warning
   - Red: Error
   - Blue: Task assignment
4. Show timestamp and agent name for each activity
5. Maximum 100 activities in view

**File to create**: `control_center/components/activity_monitor.py`

**WebSocket Connection Example**:
```python
import websockets
import asyncio

async def connect_to_monitor(self):
    async with websockets.connect("ws://localhost:8765") as websocket:
        await websocket.send(json.dumps({
            "type": "authenticate",
            "token": self.auth_token
        }))
        async for message in websocket:
            await self.handle_activity(json.loads(message))
```

### Task 4: CC-004 - Implement Task Manager Panel
**Priority**: MEDIUM
**Estimated Time**: 3 hours

**Requirements**:
1. Display current sprint tasks from SPRINT_1_6_PLAN.md
2. Show task status (pending, in_progress, completed)
3. Add "Assign Task" button
4. Task assignment dialog with agent selection
5. Update task status in real-time

**File to create**: `control_center/components/task_manager.py`

### Task 5: CC-005 - Implement PR Review Panel
**Priority**: MEDIUM
**Estimated Time**: 2 hours

**Requirements**:
1. Show current PR info:
   - PR number and title
   - Author (agent name)
   - Branch name
   - Files changed count
2. Add "View Diff" button (opens in modal)
3. Add "Approve" and "Request Changes" buttons
4. Integrate with git commands

**File to create**: `control_center/components/pr_review.py`

## 📋 Development Guidelines

1. **Branch Name**: `feature/sprint-1.6-control-center-ui`
2. **UI Framework**: Use Textual (modern TUI framework)
3. **State Management**: Use reactive attributes
4. **Error Handling**: Show user-friendly error messages
5. **Testing**: Create visual tests for each component

## 🎨 Design Guidelines

1. **Color Scheme**:
   - Background: Dark theme by default
   - Success: Green (#50fa7b)
   - Warning: Yellow (#f1fa8c)
   - Error: Red (#ff5555)
   - Info: Blue (#8be9fd)

2. **Layout**:
   - Use CSS Grid for responsive panels
   - Minimum terminal size: 80x24
   - Panels should be equal size

## 🚀 Getting Started

1. Install Textual: `pip install textual`
2. Create your feature branch
3. Start with CC-001 (project setup)
4. Test each component in isolation
5. Run `textual run control_center/main.py` to test

## 💡 Tips

- Look at the existing `control_center_simple.py` for inspiration
- Use Textual's built-in widgets where possible
- The monitoring WebSocket runs on ws://localhost:8765
- Redis connection info is in environment variables

Remember: Focus on functionality first, then polish the UI!