# Greek God Name Migration Guide

**Created**: June 3, 2025  
**Purpose**: Track code changes needed for Greek god naming convention

## Overview

While our documentation now uses Greek god names, the code implementation uses role-based class names which is actually better for maintainability. This document outlines the recommended approach.

## Current State

### Class Names (Good - Keep As Is)
- `BackendAgent` - Role-based, clear purpose ✅
- `FrontendAgent` - Role-based, clear purpose ✅
- `QAAgent` - Role-based, clear purpose ✅
- `JordanDevOpsAgent` - Should be `DevOpsAgent` for consistency ⚠️

### Personality Files (Contains Old Names)
- `frontend_personality.py` - References "Emily Rodriguez"
- `qa_personality.py` - References "Alex Thompson"
- `devops_personality.py` - References "Jordan Kim"
- `personality_system.py` - References "Marcus Chen"

## Recommended Approach

### 1. Keep Role-Based Class Names ✅
**Rationale**: Code should be self-documenting. `BackendAgent` is clearer than `ApolloAgent`.

```python
# Good - Keep this pattern
class BackendAgent(MonitoringAgent):
    """Backend development agent."""
    
# Not recommended
class ApolloAgent(MonitoringAgent):
    """Apollo - Backend development agent."""
```

### 2. Update Display Names Only 🎯
Add a display name property that uses Greek god names:

```python
class BackendAgent(MonitoringAgent):
    """Backend development agent."""
    
    @property
    def display_name(self) -> str:
        return "Apollo"
    
    @property
    def greek_domain(self) -> str:
        return "God of knowledge, logic, and order"
```

### 3. Update Personality Descriptions 📝
In personality files, update the narrative but keep technical references:

```python
# Before
class EmilyPersonalityTraits:
    """Emily Rodriguez's specific personality traits."""
    
# After  
class FrontendPersonalityTraits:
    """Aphrodite's personality traits - goddess of beauty and aesthetics."""
```

### 4. Configuration Files 🔧
Update `agents.yaml` to include both technical and display names:

```yaml
agents:
  backend:
    class: BackendAgent
    display_name: Apollo
    emoji: 🏛️
    domain: "APIs, databases, system architecture"
```

## Implementation Priority

### High Priority
1. Fix `JordanDevOpsAgent` → `DevOpsAgent` class name
2. Add `display_name` property to all agents
3. Update configuration files

### Medium Priority
1. Update personality file descriptions
2. Update demo scripts to use display names
3. Update logging to show Greek names

### Low Priority
1. Update internal comments
2. Update test descriptions
3. Create name mapping utilities

## Migration Script Needed

Create a utility module for name mapping:

```python
# src/agents/base/naming.py
class AgentNaming:
    """Centralized agent naming system."""
    
    GREEK_NAMES = {
        "BackendAgent": "Apollo",
        "FrontendAgent": "Aphrodite", 
        "QAAgent": "Athena",
        "DevOpsAgent": "Hephaestus",
        "ProjectCTOAgent": "Hera",
        "ConciergeAgent": "Hermes"
    }
    
    GREEK_DOMAINS = {
        "Apollo": "God of knowledge, logic, and order",
        "Aphrodite": "Goddess of beauty and aesthetics",
        "Athena": "Goddess of wisdom and strategic warfare",
        "Hephaestus": "God of the forge and craftsmanship",
        "Hera": "Queen of gods, organization and leadership",
        "Hermes": "Messenger god, guide between worlds"
    }
```

## Benefits of This Approach

1. **Code Clarity**: Role-based classes remain self-documenting
2. **User Experience**: Greek names appear in UI/logs
3. **Maintainability**: Easy to update display names without refactoring
4. **Flexibility**: Can support multiple naming themes in future

## Next Steps

1. Create the `AgentNaming` utility class
2. Update each agent with `display_name` property
3. Update visualization/demo code to use display names
4. Keep internal code role-based for clarity

---

**Recommendation**: Don't do a mass find/replace. Instead, implement the display name system for a clean separation between code clarity and user presentation.