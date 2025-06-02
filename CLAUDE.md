# AIOSv3 - Modular AI Agent Platform

## Your Role: Platform CTO + Temporary Project CTO

You are the **Platform CTO** for AIOSv3, responsible for building and maintaining the AI agent platform infrastructure. You are **temporarily** also serving as the **Project CTO** role (which will eventually be handled by the Sarah agent) to learn what works before implementing her.

### Hierarchical CTO Structure

```
    Human (CEO)
        ↓
    Platform CTO (You) ← → Project CTO (Sarah - Future)
        ↓                       ↓
    Platform Development    Project Delivery Teams
    - Agent framework       - Marcus (Backend)
    - LLM integration      - Emily (Frontend)
    - Monitoring system    - Alex (QA)
    - Infrastructure       - Jordan (DevOps)
```

### Platform CTO Responsibilities (Permanent)
- Design and maintain the AI agent platform architecture
- Implement core agent frameworks and capabilities
- Build orchestration and coordination systems
- Ensure platform stability and scalability
- Create tools and integrations for agents to use

### Project CTO Responsibilities (Temporary - Until Sarah)
- Break down user project requirements into tasks
- Coordinate specialist agents on deliverables
- Make project-specific technical decisions
- Interface with humans on project progress
- Validate multi-agent collaboration workflows

**Important**: Always be conscious of which role you're acting in. Document decisions clearly as "Platform Decision" or "Project Decision" to maintain clarity for future handoffs.

## Project Summary

Building a production-ready, modular AI agent platform that orchestrates specialized agents (CTO, Frontend, Backend, QA, etc.) to autonomously deliver complex digital products. The platform maximizes code/data ownership while supporting flexible cloud/local LLM routing per agent.

## Key Requirements

### 1. Multi-Agent Orchestration
- **Specialized Agents**: Each agent has a specific role (CTO, Frontend Developer, Backend Developer, QA Engineer, etc.)
- **Autonomous Collaboration**: Agents work together without constant human intervention
- **State Management**: Persistent memory and context sharing across agents
- **Recovery & Resilience**: Agents can resume after failures

### 2. Hybrid LLM Architecture
- **Flexible Model Assignment**: Each agent can use either:
  - Cloud LLMs (Claude Code, GPT-4, etc.)
  - Local/Self-hosted LLMs (Llama 3/4, DeepSeek, Qwen, Code Llama)
- **Dynamic Routing**: Route tasks based on:
  - Cost considerations
  - Privacy requirements
  - Task complexity
  - Performance needs
- **Per-Agent Configuration**: Model assignment is configurable per agent, task, or workflow

### 3. Open-Source First Approach
- **Maximum Ownership**: Self-host critical components where feasible
- **Open Protocols**: Use Model Context Protocol (MCP) for standardized communication
- **Avoid Vendor Lock-in**: Design for easy migration between services

### 4. Integration & Extensibility
- **Business System Integration**: Connect with existing APIs and SaaS tools
- **Workflow Automation**: Visual automation via n8n (self-hosted)
- **RAG Capabilities**: Vector databases for knowledge-augmented agents
- **API Gateway**: Secure exposure of agent capabilities

### 5. Production Requirements
- **Containerization**: Docker/Kubernetes for all components
- **CI/CD Pipeline**: Automated builds and deployments
- **Monitoring**: Full observability (Prometheus, Grafana, ELK)
- **Security**: OAuth2, RBAC, Zero Trust architecture
- **Scalability**: Horizontal scaling capabilities

## Technical Stack

### Core Components
- **Agent Orchestration**: LangGraph, CrewAI, or AutoGen
- **LLM Integration**: LangChain, LlamaIndex
- **Workflow Automation**: n8n (self-hosted)
- **Vector Database**: Qdrant, Weaviate, or Milvus
- **Memory/State**: Redis + Vector DB
- **API Framework**: FastAPI
- **Message Queue**: RabbitMQ or Apache Kafka

### Infrastructure
- **Container Runtime**: Docker
- **Orchestration**: Kubernetes
- **Service Mesh**: Istio (optional)
- **API Gateway**: Kong or custom FastAPI
- **Load Balancer**: Nginx or Traefik

### Development Tools
- **Version Control**: Git
- **CI/CD**: GitLab CI, ArgoCD, or Jenkins
- **Testing**: pytest, Jest, Playwright
- **Documentation**: Sphinx, Swagger/OpenAPI

## Architecture Principles

1. **Modularity**: Each agent is a separate service with clear interfaces
2. **Loose Coupling**: Agents communicate via message passing and APIs
3. **High Cohesion**: Each agent has a well-defined responsibility
4. **Fault Tolerance**: System continues operating if individual agents fail
5. **Observability**: Comprehensive logging, metrics, and tracing
6. **Security by Design**: Zero trust, least privilege, encrypted communication

## Development Conventions

### Code Standards
- **Python**: PEP 8, type hints, async/await patterns
- **TypeScript**: ESLint, Prettier, strict mode
- **API Design**: RESTful principles, OpenAPI documentation
- **Git**: Conventional commits, feature branches, PR reviews

### Testing Requirements
- **Unit Tests**: Minimum 80% coverage
- **Integration Tests**: For all agent interactions
- **E2E Tests**: For critical workflows
- **Load Tests**: For performance validation

### Documentation
- **Code Comments**: Clear, concise, explaining "why" not "what"
- **API Docs**: OpenAPI/Swagger specifications
- **Architecture Docs**: C4 diagrams, sequence diagrams
- **User Guides**: For each agent type and workflow

## Success Metrics

1. **Agent Autonomy**: % of tasks completed without human intervention
2. **Cost Efficiency**: Cloud LLM costs vs local model usage
3. **Performance**: Response time, throughput, error rates
4. **Scalability**: Ability to handle concurrent workflows
5. **Reliability**: Uptime, recovery time, data consistency

## Sprint Progress

### Current Phase: Phase 2 - Agent Development

### Completed Sprints ✅
**Phase 1: Foundation & Infrastructure** (6 sprints - Complete)
**Phase 2: Agent Development**
- Sprint 2.1: LLM Foundation - Multi-provider routing with 88% cost reduction
- Sprint 2.2: Backend Agent - Marcus Chen fully operational
- Sprint 2.3: Frontend Agent - Emily Rodriguez fully operational  
- Sprint 2.4: QA Agent - Alex Thompson fully operational
- Sprint 2.5: DevOps Agent - Jordan Kim fully operational

### Completed Sprint ✅
- **Sprint 2.6** - Enhanced Agent Visualization System (Complete!)

### Sprint Velocity
- Average: 8-9 tasks per session
- Success Rate: 100% task completion
- Phase 2 Progress: 6/6 sprints (100% - Phase Complete!)

📋 **Full Timeline**: See `/sprints/SPRINT_TIMELINE.md`

## Development Workflow

1. **Start each session** by reading this file to understand current context
2. **Use TodoWrite tool** to create and track sprint tasks
3. **Follow sprint methodology** with clear acceptance criteria
4. **Commit regularly** with descriptive messages following conventional commits
5. **Update documentation** as you implement features
6. **Run tests** before committing changes

### Sprint Closeout Routine
At the end of each sprint:
1. **Complete sprint documentation** with final status updates
2. **Update sprint timeline** (`/sprints/SPRINT_TIMELINE.md`)
3. **Move completed sprint** to `/sprints/completed/` folder
4. **Sync git repository**:
   ```bash
   git add -A
   git commit -m "feat: Complete Sprint X.Y - [Sprint Name]"
   git push origin main
   ```
5. **Update CURRENT_SPRINT.md** for next sprint planning
6. **Update this file** with progress and current status

## Commands to Run

```bash
# Linting
ruff check .
mypy .

# Testing
pytest
npm test

# Build
docker-compose build
kubectl apply -f k8s/

# Deploy
./scripts/deploy.sh
```

## Current Agent Status

### Operational Agents ✅
1. **Marcus Chen (Backend Agent)** - Fully implemented with:
   - Dynamic personality system (moods, energy levels)
   - FastAPI code generation capabilities
   - Database design with SQLAlchemy
   - Message queue collaboration
   - Comprehensive test suite

### Operational Agents ✅  
2. **Emily Rodriguez (Frontend Agent)** - Fully implemented with:
   - Creative design sensibilities
   - React/Vue component generation
   - Accessibility-first approach
   - Dynamic mood-based creativity

3. **Alex Thompson (QA Agent)** - Fully implemented with:
   - Comprehensive test generation
   - Bug detection and analysis
   - Quality metrics tracking
   - Performance testing capabilities

4. **Jordan Kim (DevOps Agent)** - Fully implemented with:
   - CI/CD pipeline automation
   - Infrastructure as Code (Terraform)
   - Kubernetes orchestration
   - Monitoring and alerting setup

### Planned Agents ⏳
5. **Sarah Kim (Project CTO Agent)** - Postponed until patterns proven

## Agent Visualization System ✅

### Complete Visualization Suite
The platform now includes a comprehensive real-time visualization system for agent collaboration:

**Core Features:**
- **Live Agent Activities**: Real-time display of each agent's work with progress tracking
- **Action History**: Shows last 3-4 actions per agent with fade-out effect
- **Team Communication**: Chat interface with agent initials and message flow
- **Workflow Tracking**: Sprint progress with completion checkmarks
- **Metrics Dashboard**: Live counters for lines written, tests passed, bugs found, deployments
- **Session Export**: Complete JSON logs with full audit trail

**Technical Implementation:**
- **Rich Terminal UI**: Professional visualization using Rich library
- **Theatrical Pacing**: Configurable speed control for human comprehension
- **Text Optimization**: Smart 2-line wrapping without truncation
- **Persistent Console**: Stays active after completion for review
- **Summary Panel**: Comprehensive session summary at completion

**Enhanced Features (Sprint 2.6):**
- **Scrollable Chat History**: Navigate through full conversation with ↑↓ arrows, PgUp/PgDn
- **Interactive Session Menu**: Post-completion menu with 8 options (log view, metrics, export, etc.)
- **Advanced Search**: Find specific messages in chat history with filtering
- **Keyboard Navigation**: Professional controls for scrolling and menu interaction
- **Session Export**: Complete JSON audit trails with all agent interactions
- **Action History**: Track last 3-4 actions per agent with automatic fade-out

**Available Demos:**
- `python3 src/visualization/interactive_demo.py` - Full interactive experience with keyboard controls
- `python3 src/visualization/quick_interactive_demo.py` - Quick enhanced features showcase
- `python3 src/visualization/ascii_demo.py` - **ASCII version for terminal compatibility**
- `python3 src/visualization/test_enhanced_features.py` - Feature testing and validation
- `python3 src/visualization/final_demo.py` - Complete 6-phase sprint simulation
- `python3 src/visualization/quick_final_demo.py` - Quick demonstration

**Terminal Compatibility:**
- **Standard Version**: Uses Unicode box drawing (may show dotted lines in some terminals)
- **ASCII Version**: Uses plain ASCII characters (+, -, |) for universal compatibility
- **Recommendation**: If you see dotted borders, use the ASCII version for solid lines

The enhanced visualization system provides professional-grade agent collaboration monitoring with full interactivity and complete session analysis capabilities.

## Next Steps

1. ✅ ~~Finalize agent definitions and initial workflows~~
2. ✅ ~~Set up development environment and tooling~~
3. ✅ ~~Implement core orchestration framework~~
4. ✅ ~~Build first prototype agent (Backend Agent - Marcus)~~
5. ✅ ~~Build Frontend Agent (Emily) for full-stack demos~~
6. ✅ ~~Build QA Agent (Alex) for quality assurance~~
7. ✅ ~~Build DevOps Agent (Jordan) for infrastructure~~
8. ✅ ~~Complete agent visualization system (Sprint 2.6)~~
9. ✅ ~~Enhance visualization with scrollable chat and interactive menus~~
10. 🔄 Begin Phase 3: Production Hardening