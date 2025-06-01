# Multi-Terminal Claude Code Collaboration

## Quick Start

### Step 1: Start the Collaboration Server
In Terminal 1:
```bash
cd /Users/arielmuslera/Development/Projects/bluelabel-AIOSv3
python3 collaboration_server.py
```

You'll see:
```
Starting collaboration server on port 8765
Collaboration server running at ws://localhost:8765
Multiple Claude Code instances can now connect and collaborate!
```

### Step 2: Open Multiple Terminals

**Terminal 2 (You as Product Owner):**
```bash
cd /Users/arielmuslera/Development/Projects/bluelabel-AIOSv3
python3 join_collaboration.py --role=human --name="Product Owner"
```

**Terminal 3 (Claude Code as CTO):**
```bash
cd /Users/arielmuslera/Development/Projects/bluelabel-AIOSv3
python3 join_collaboration.py --role=cto --name="CTO Agent"
```

**Terminal 4 (Claude Code as Backend Dev):**
```bash
cd /Users/arielmuslera/Development/Projects/bluelabel-AIOSv3
python3 join_collaboration.py --role=backend-dev --name="Backend Developer"
```

**Terminal 5 (Claude Code as QA):**
```bash
cd /Users/arielmuslera/Development/Projects/bluelabel-AIOSv3
python3 join_collaboration.py --role=qa --name="QA Engineer"
```

## What You'll See

Each terminal will show:
```
🔗 Connecting to collaboration server: ws://localhost:8765
✅ Connected as: Product Owner (human)

🔄 Synced with collaboration state:
   👥 Active collaborators: 4
   💬 Recent messages: 0
   📋 Active tasks: 0

👥 Current Team:
   🟢 Product Owner (human)
   🟢 CTO Agent (cto)
   🟢 Backend Developer (backend-dev)
   🟢 QA Engineer (qa)

💡 Available commands for human:
   chat <message>    - Send message to team
   status <status>   - Update your status (active/busy/idle)
   task <title>      - Create new task
   team              - Show team status
   tasks             - Show active tasks
   help              - Show this help
   quit              - Leave collaboration

human> 
```

## How to Collaborate

### 1. Send Messages Between Terminals
In any terminal:
```
human> chat Hey team, let's implement user authentication
```

All other terminals will see:
```
💬 [14:32:15] Product Owner: Hey team, let's implement user authentication
```

### 2. Create and Track Tasks
```
human> task Implement JWT authentication system
```

All terminals see:
```
📋 Task updated: Implement JWT authentication system [planned]
```

### 3. Update Status
```
cto> status busy working on auth architecture
```

All terminals see:
```
🔄 CTO Agent is now busy - working on: auth architecture
```

### 4. Show Team Status
```
human> team
```

Shows:
```
👥 Current Team:
   🟢 Product Owner (human)
   🟡 CTO Agent (cto) - working on auth architecture
   🟢 Backend Developer (backend-dev)
   🟢 QA Engineer (qa)
```

## Real Collaboration Examples

### Example 1: Planning Session
```
# Terminal 2 (You)
human> chat We need to add user authentication to our API

# Terminal 3 (CTO) 
cto> chat I'll design the architecture. Should we use JWT or OAuth?

# Terminal 2 (You)
human> chat JWT for simplicity. What's your recommendation for the flow?

# Terminal 3 (CTO)
cto> task Design JWT authentication architecture
cto> status busy analyzing auth requirements
```

### Example 2: Development Workflow
```
# Terminal 2 (You)
human> task Implement user login endpoint

# Terminal 3 (CTO)
cto> chat I'll create the technical spec first

# Terminal 4 (Backend Dev)
backend-dev> chat Waiting for spec, then I'll implement

# Terminal 5 (QA)
qa> chat I'll prepare test cases while you design
```

## Key Features

### ✅ Real-time Communication
- All terminals see messages instantly
- Status updates broadcast to everyone
- File change notifications

### ✅ Task Coordination
- Create and track tasks across team
- Assign work to different roles
- Monitor progress in real-time

### ✅ Team Awareness
- See who's online and what they're working on
- Status updates (active/busy/idle)
- Role-based context

### ✅ Repository Integration
- All instances work in same repo directory
- File change notifications
- Shared context about codebase

## Next Steps

This foundation enables:

1. **Actual Claude Code Integration**
   - Replace dummy terminals with real Claude Code instances
   - Each instance has its role-specific prompts and behavior

2. **File System Integration** 
   - Notify team when files are changed
   - Coordinate to avoid conflicts
   - Track who's working on what files

3. **Task Execution**
   - CTO Agent creates technical specs
   - Backend Dev implements code
   - QA creates and runs tests
   - All coordinated through the collaboration server

4. **Advanced Features**
   - Code review workflows
   - Automated testing integration
   - Git workflow coordination

This is the foundation for true multi-terminal Claude Code collaboration!