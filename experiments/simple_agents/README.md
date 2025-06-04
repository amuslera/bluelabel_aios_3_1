# Simple Agents Experiment

## Overview
This is an **EXPERIMENTAL** implementation of a simplified agent architecture based on OpenAI's guide. This experiment is completely isolated from the main AIOSv3 architecture and is designed to test whether a radically simpler approach can work for our use cases.

**IMPORTANT**: This experiment does NOT replace or modify our main architecture. It's a learning exercise.

## Experiment Goals
1. Test if file-based message passing is sufficient for agent communication
2. Validate handoff patterns with simple state transfer
3. See if agents can collaborate without complex infrastructure
4. Learn patterns we can apply to the main system

## What We're Testing

### Simplified Architecture
```
experiments/simple_agents/
├── README.md (this file)
├── agents/
│   ├── base_agent.py      # Minimal agent base class
│   ├── apollo_simple.py   # Backend agent
│   ├── aphrodite_simple.py # Frontend agent
│   └── hermes_simple.py   # Conversation agent
├── communication/
│   ├── messages/          # JSON message files
│   └── message_bus.py     # File-based message passing
├── orchestration/
│   └── simple_orchestrator.py
├── workspace/             # Shared workspace for agents
│   ├── code/             # Generated code
│   ├── tasks/            # Task definitions
│   └── state/            # Agent state files
└── test_simple_collaboration.py
```

### Key Simplifications
1. **No databases** - Just JSON files
2. **No message queues** - File-based communication
3. **No complex memory** - Just current conversation state
4. **No LLM routing** - Direct API calls
5. **No monitoring** - Simple logging only

## Experiment Rules
1. Keep it SIMPLE - resist adding complexity
2. Use Python stdlib as much as possible
3. Mock LLM responses initially, add real ones later
4. Focus on agent collaboration patterns
5. Document what works and what doesn't

## What Success Looks Like
- Agents can receive tasks and complete them
- Agents can hand off work to each other
- State is maintained during handoffs
- We identify useful patterns for the main system

## What We're NOT Doing
- Not replacing the main architecture
- Not building production-ready code
- Not implementing all features
- Not worrying about scale or performance
- Not implementing security/guardrails

## Timeline
- Day 1: Basic agent structure and file messaging
- Day 2: Implement handoff pattern
- Day 3: Test multi-agent collaboration
- Day 4: Add real LLM calls (optional)
- Day 5: Document findings

---
*Experiment Started: June 3, 2025*
*Status: Active Experiment*
*Owner: Platform CTO*