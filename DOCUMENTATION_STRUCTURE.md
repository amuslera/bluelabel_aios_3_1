# AIOSv3.1 Documentation Structure

## 🎯 Goal
Eliminate duplication and create a single source of truth for each type of information.

## 📁 Proposed Structure

```
bluelabel-aios-3-1/
├── README.md                    # Project overview and quick start
├── PROJECT_CONTEXT.md          # Vision, goals, current state (SINGLE SOURCE)
├── DEVELOPMENT_PROCESS.md      # How we work (sprint process, standards)
├── ARCHITECTURE.md             # Technical architecture (SINGLE SOURCE)
│
├── agents/
│   ├── AGENT_ROSTER.md         # All agents and their roles
│   └── onboarding/             # One file per agent type
│       ├── CTO_AGENT.md
│       ├── FRONTEND_AGENT.md
│       ├── BACKEND_AGENT.md
│       ├── QA_AGENT.md
│       └── DEVOPS_AGENT.md
│
├── orchestration/
│   └── ORCHESTRATION_DESIGN.md # How agents work together
│
├── templates/                   # All reusable templates
│   ├── SPRINT_PLAN.md
│   ├── TASK_ASSIGNMENT.md
│   ├── SPRINT_REVIEW.md
│   ├── RETROSPECTIVE.md
│   └── PR_TEMPLATE.md
│
├── sprints/
│   ├── active/
│   │   └── CURRENT_SPRINT.md   # Only current sprint info
│   └── completed/              # Historical sprints
│       ├── SPRINT_001.md
│       └── SPRINT_002.md
│
├── standards/
│   ├── CODING_STANDARDS.md
│   ├── GIT_WORKFLOW.md
│   └── TESTING_REQUIREMENTS.md
│
└── archive/                    # All old/duplicate docs
```

## 🔄 Consolidation Plan

### Files to Merge → PROJECT_CONTEXT.md
- COMMERCIAL_VISION.md
- STRATEGIC_VISION.md
- CURRENT_STATUS.md
- PROJECT_STATUS.md
- PROJECT_PHASES.md
- ROADMAP_2025.md

### Files to Merge → ARCHITECTURE.md
- ARCHITECTURE_DECISIONS.md
- REFINED_ARCHITECTURE.md
- THEATRICAL_AGENTS_DESIGN.md
- PROJECT_STRUCTURE.md

### Files to Merge → DEVELOPMENT_PROCESS.md
- DEVELOPMENT_STANDARDS.md
- WORKFLOW_ROADMAP.md
- IMPLEMENTATION_PLAN.md
- All SPRINT_*.md planning files

### Files to Archive
- All duplicate information
- Old sprint documentation
- Prototype documentation
- Demo instructions

## 📝 Key Documents Explained

### 1. PROJECT_CONTEXT.md
**Purpose**: Single source of truth about the project
**Contents**:
- What is AIOSv3.1?
- Why are we building it?
- What have we achieved so far?
- What's next?
- Key decisions and constraints

### 2. AGENT_ROSTER.md
**Purpose**: Complete guide to all agents
**Contents**:
- Agent name, role, and persona
- Capabilities and expertise
- Communication style
- Collaboration patterns
- Performance expectations

### 3. ORCHESTRATION_DESIGN.md
**Purpose**: How the system works
**Contents**:
- Task distribution algorithm
- Communication protocols
- State management
- Error handling
- Recovery procedures
- Monitoring integration

### 4. Agent Onboarding Files
**Purpose**: Everything an agent needs to start working
**Format**: Each file is self-contained and includes:
- Role definition
- Capabilities
- Current context pointer
- Standards to follow
- Communication protocols
- Example tasks

## 🚀 Migration Steps

1. **Create Core Documents**
   - Merge all vision/status docs → PROJECT_CONTEXT.md
   - Merge all architecture docs → ARCHITECTURE.md
   - Already created DEVELOPMENT_PROCESS.md

2. **Create Templates**
   - Extract patterns from existing sprint docs
   - Standardize formats
   - Add clear instructions

3. **Write Agent Onboarding**
   - One comprehensive file per agent type
   - Include everything needed to start
   - Test with actual agents

4. **Archive Old Documents**
   - Move all superseded docs to archive/legacy/
   - Keep for reference only
   - Add README explaining the archive

5. **Update References**
   - Fix all internal links
   - Update README.md
   - Create migration guide

## ✅ Benefits

1. **No Duplication**: Each piece of information lives in exactly one place
2. **Clear Navigation**: Easy to find what you need
3. **Agent-Friendly**: Agents can quickly understand their context
4. **Maintainable**: Easy to update without creating inconsistencies
5. **Scalable**: Structure supports growth

## 🎯 Success Criteria

- New developer can understand project in 30 minutes
- Agent can onboard in 5 minutes
- No conflicting information
- All processes have templates
- Historical data properly archived