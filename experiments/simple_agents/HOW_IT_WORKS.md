# How the Simple Agents Experiment Works

## The Big Picture
Instead of complex infrastructure (RabbitMQ, Redis, databases), agents communicate by reading and writing JSON files. It's like passing notes in class!

## Visual Demo
Run this to see agents interact:
```bash
python3 experiments/simple_agents/visual_demo.py
```

You'll see:
- 🤖 **Agents coming online** (Apollo, Aphrodite)
- 📬 **Message bus status** (who has messages)
- 📨 **Messages flowing** between agents
- 📄 **Files being created** as agents work
- 🤝 **Handoffs** when agents need help

## How Communication Works

### 1. Message Bus = JSON Files
```
messages/
├── apollo_inbox.json       # Apollo's pending messages
├── aphrodite_inbox.json    # Aphrodite's pending messages
└── archive/                # Processed messages
```

### 2. Sending a Message
```python
# Orchestrator sends task to Apollo
message_bus.send_message("Apollo", {
    "type": "task",
    "task": {"description": "Create an API"},
    "from": "Orchestrator"
})
# This writes to apollo_inbox.json
```

### 3. Reading Messages
```python
# Apollo checks inbox
message = message_bus.get_next_message("Apollo")
# This reads from apollo_inbox.json
```

### 4. Handoffs
When Apollo needs frontend help:
```python
apollo.handoff_to("Aphrodite", {
    "reason": "Need UI for this API",
    "backend_ready": True
})
# This writes to aphrodite_inbox.json
```

## Interactive Mode

Run this for manual control:
```bash
python3 experiments/simple_agents/test_simple_collaboration.py --interactive
```

Commands:
- `task` - Create a new task
- `cycle` - Run one orchestration cycle
- `status` - See what's happening
- `messages` - Check message queues
- `quit` - Exit

## What Gets Created

After running, check:
```
workspace/
├── code/
│   ├── backend/
│   │   ├── user_management_api.py  # Apollo's API
│   │   └── models.py               # Apollo's database
│   └── frontend/
│       └── Dashboard.jsx           # Aphrodite's UI
├── messages/
│   └── archive/                    # Processed messages
└── orchestrator.log               # What happened
```

## Key Insights

1. **No Infrastructure Needed**: Just Python and files
2. **Easy to Debug**: Read the JSON files directly
3. **Visual Feedback**: See exactly what agents are doing
4. **Real Code Output**: Agents generate actual code files

## Try This

1. **Watch a full workflow**:
   ```bash
   python3 experiments/simple_agents/visual_demo.py
   ```

2. **Create your own task**:
   ```bash
   python3 experiments/simple_agents/test_simple_collaboration.py -i
   # Then type: task
   # Assign to: Apollo
   # Task type: create_api
   # Description: Build a weather API
   ```

3. **Check the output**:
   ```bash
   ls experiments/simple_agents/workspace/code/backend/
   cat experiments/simple_agents/workspace/code/backend/weather_api.py
   ```

## What This Proves

✅ Multi-agent collaboration works with simple file passing
✅ Agents can hand off tasks to each other
✅ State can be maintained between handoffs
✅ No complex infrastructure required for MVP

## Next Steps

Currently we have:
- Apollo (Backend) ✅
- Aphrodite (Frontend) ✅ (basic)

Still need:
- Athena (QA)
- Hephaestus (DevOps)
- Real LLM integration (currently using templates)

But the patterns are proven!