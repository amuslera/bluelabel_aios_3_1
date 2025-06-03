# AIOSv3.1 Technical Architecture

> **Single Source of Truth for Technical Design** - Last Updated: June 3, 2025

## 🎯 Architecture Overview

AIOSv3.1 uses a modular, event-driven microservices architecture where specialized AI agents collaborate through well-defined protocols to deliver software projects autonomously.

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Web UI    │  │  Control     │  │      CLI        │   │
│  │   (Future)  │  │  Center TUI  │  │   Interface     │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    CONCIERGE LAYER (NEW)                     │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Hermes    │  │    Intent    │  │     Memory      │   │
│  │   (Chat)    │  │ Interpreter  │  │     Proxy       │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                       │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Agent     │  │    Task      │  │    FastAPI      │   │
│  │ Dispatcher  │  │   Tracker    │  │   REST API      │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     AGENT LAYER                              │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │PROJECT CTO* │  │  Frontend    │  │    Backend      │   │
│  │   (Hera)    │  │  (Aphrodite) │  │   (Apollo)      │   │
│  ├─────────────┤  ├──────────────┤  ├─────────────────┤   │
│  │  QA Agent   │  │   DevOps     │  │   Specialist    │   │
│  │  (Athena)   │  │(Hephaestus)  │  │     Agents      │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
│  * Currently handled by Platform CTO (Claude Code)           │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                COMMUNICATION & MEMORY LAYER                  │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  RabbitMQ   │  │    Redis     │  │    Qdrant       │   │
│  │  (Events)   │  │  (State)     │  │  (Knowledge)    │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    LLM ROUTING LAYER                         │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Claude    │  │    GPT-4     │  │  Local Models   │   │
│  │  (Complex)  │  │  (General)   │  │  (Ollama)       │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🏛️ The Pantheon - Agent Roster

### Core Development Agents
- **Apollo** 🏛️ - Backend Development Agent (formerly Marcus)
  - Domain: APIs, databases, system architecture
  - Specialties: FastAPI, SQLAlchemy, microservices
  
- **Aphrodite** 🎨 - Frontend Development Agent (formerly Emily)
  - Domain: UI/UX, visual design, user experience
  - Specialties: React, Vue, accessibility, responsive design
  
- **Athena** 🛡️ - Quality Assurance Agent (formerly Alex)
  - Domain: Testing, bug detection, quality metrics
  - Specialties: Pytest, Jest, security analysis, performance testing
  
- **Hephaestus** 🔨 - DevOps & Infrastructure Agent (formerly Jordan)
  - Domain: CI/CD, deployment, infrastructure
  - Specialties: Docker, Kubernetes, monitoring, automation

### Leadership Agents
- **Hera** 👑 - Project CTO Agent (formerly Sarah) - *Future*
  - Domain: Project orchestration, technical decisions
  - Specialties: Task breakdown, agent coordination
  
- **Hermes** 🪽 - Concierge Agent - *New*
  - Domain: User interaction, intent interpretation
  - Specialties: Natural language understanding, project initiation

## 🎭 Leadership Hierarchy

### Organizational Structure
```
         CEO (Human - Ariel)
              │
         Platform CTO 
       (Claude Code - You)
              │
    ┌─────────┴─────────┐
    │                   │
Hermes              Project CTOs
(Concierge)         (Hera - per project)
    │                   │
    └─────────┬─────────┘
              │
        Development Teams
    (Apollo, Aphrodite, Athena, Hephaestus)
```

**Role Clarifications**:
1. **CEO**: Strategic vision, business decisions, platform direction
2. **Platform CTO**: Infrastructure, architecture, platform capabilities
3. **Hermes (Concierge)**: User-facing interface, translates intent to projects
4. **Hera (Project CTO)**: Manages individual projects, coordinates agents
5. **Development Agents**: Execute specific technical tasks

## 🆕 Concierge Layer Architecture

### Purpose
The Concierge Layer acts as the intelligent interface between users and the platform, enabling natural language interaction and automatic project setup.

### Components

1. **Hermes Chat Wrapper**
   - Wraps Claude Sonnet 4 or GPT-4o
   - Maintains conversation context
   - Injects platform capabilities awareness
   - Handles multi-turn dialogues

2. **Intent Interpreter**
   - Analyzes user requests
   - Identifies project type and requirements
   - Generates structured project definitions
   - Creates initial task breakdowns

3. **Memory Proxy**
   - Interfaces with Redis for session state
   - Queries Qdrant for relevant past projects
   - Builds context from user history
   - Enables learning from successful patterns

### Workflow
```
User Input → Hermes → Intent Analysis → Project Definition
                ↓
          Task Planning → Agent Dispatch → Execution
                ↓
          Progress Updates → User Feedback
```

## 🏗️ Core Architectural Decisions

### 1. Event-Driven Architecture
**Decision**: Asynchronous event-based communication between agents

**Benefits**:
- Loose coupling - agents can evolve independently
- Scalability - easy to add new agents
- Resilience - system continues if one agent fails
- Auditability - all events can be logged and replayed

**Implementation**:
- RabbitMQ for reliable message delivery
- Event schemas defined in protobuf/JSON
- Dead letter queues for failed messages
- Event sourcing for critical workflows

### 2. Microservices with Shared Core
**Decision**: Each agent is an independent service sharing common libraries

**Benefits**:
- Independent deployment and scaling
- Technology flexibility per agent
- Fault isolation
- Clear ownership boundaries

**Implementation**:
- Shared `BaseAgent` class for common functionality
- Agent-specific Docker containers
- Service mesh for inter-agent communication
- Health checks and circuit breakers

### 3. Hybrid LLM Strategy
**Decision**: Route tasks to appropriate LLMs based on complexity and cost

**Benefits**:
- Cost optimization (88% cloud reduction, 100% local for dev)
- Performance optimization
- Privacy control
- Fallback options

**Current Configuration**:
- **Ollama (Local)**: Priority 1 - Development, testing, simple tasks
- **Claude**: Priority 2 - Complex reasoning, architecture decisions
- **OpenAI**: Priority 3 - Fallback, specific capabilities
- **Target**: 85% local model usage

**Implementation**:
- Router evaluates task complexity
- Local models (mistral:latest) for development
- Cloud LLMs for complex reasoning
- Automatic fallback on failure

## 📦 Component Architecture

### Agent Components
```python
class BaseAgent:
    """Core agent functionality"""
    - lifecycle_manager: AgentLifecycleManager
    - memory_manager: MemoryManager
    - llm_router: LLMRouter
    - message_queue: MessageQueue
    - health_monitor: HealthMonitor
    - personality_system: PersonalityEngine  # Dynamic moods
```

### Communication Flow
1. **User → Concierge**
   - Natural language input
   - Hermes interprets intent
   - Creates project structure

2. **Concierge → Orchestration**
   - Structured project definition
   - Task DAG creation
   - Agent assignment

3. **Orchestration → Agents**
   - Task dispatch via RabbitMQ
   - Progress monitoring
   - Result aggregation

4. **Inter-Agent Communication**
   - Direct agent-to-agent messaging
   - Shared workspace access
   - Event notifications

## 🔐 Security Architecture

### Principles
- Zero trust between components
- Encrypted communication
- Least privilege access
- Audit logging for all actions

### Implementation
- mTLS between services
- JWT tokens for API access
- Vault for secrets management
- RBAC for agent permissions

## 📊 Data Architecture

### Data Flow
```
User Input → Hermes → Task Queue → Agents → Results Store → User
                ↓           ↓           ↓
           Memory Store  Redis State  Metrics
                ↓                       ↓
             Qdrant              Prometheus
```

### Storage Strategy
- **Hot Data**: Redis (current state, sessions)
- **Warm Data**: PostgreSQL (project history)
- **Cold Data**: S3/MinIO (archives)
- **Vectors**: Qdrant (semantic search, RAG)
- **Metrics**: Prometheus (performance data)

## 🎨 Visualization System

### Real-Time Monitoring
- Rich terminal UI for agent collaboration
- Live activity tracking per agent
- Chat history with agent communications
- Progress bars and metrics dashboards
- Session recording and export

### Components
- `theatrical_dashboard.py` - Main visualization
- Activity panels for each agent
- Scrollable chat interface
- Performance metrics display

## 🚀 Deployment Architecture

### Development
- Docker Compose for local development
- Ollama for local LLM inference
- Hot reload for agent code
- Local monitoring stack

### Production
- Kubernetes for orchestration
- Horizontal pod autoscaling
- Blue-green deployments
- Multi-region support

### CI/CD Pipeline
```
Code → Test → Build → Security Scan → Deploy Staging → Integration Tests → Deploy Prod
```

## 📈 Scalability Design

### Horizontal Scaling
- Stateless agents
- Queue-based load distribution
- Database read replicas
- CDN for static assets

### Performance Targets
- Agent response time: <1s (cloud), <15s (local)
- Task completion: <5min average
- System throughput: 1000 tasks/hour
- Availability: 99.9%
- Cost: 85%+ requests on local infrastructure

## 🔄 Integration Points

### External Services
- GitHub/GitLab APIs
- Cloud provider APIs (AWS, GCP, Azure)
- LLM provider APIs (Anthropic, OpenAI)
- Monitoring services (Datadog, NewRelic)

### Extension Points
- Custom agent types
- New LLM providers
- Additional tools/capabilities
- Workflow plugins
- Domain-specific agents

## 🏛️ Design Patterns

### Applied Patterns
1. **Repository Pattern**: Data access abstraction
2. **Strategy Pattern**: LLM routing logic
3. **Observer Pattern**: Event notifications
4. **Factory Pattern**: Agent creation
5. **Adapter Pattern**: LLM integrations
6. **Facade Pattern**: Concierge interface

### Anti-Patterns Avoided
- God objects
- Tight coupling
- Synchronous chains
- Hard-coded configuration
- Vendor lock-in

## 📐 Technical Standards

### Code Standards
- Type hints required
- 80% test coverage minimum
- Documented public APIs
- Async/await for I/O
- Semantic naming (role-based, not person-based)

### API Standards
- RESTful design
- OpenAPI documentation
- Versioned endpoints
- Standard error formats
- GraphQL for complex queries (future)

### Operational Standards
- Structured logging (JSON)
- Distributed tracing (OpenTelemetry)
- Metric collection (Prometheus)
- Error budgets (SLO/SLA tracking)

## 🔮 Future Architecture

### Immediate Roadmap (Phase 3)
1. **Concierge Implementation** (Sprints 3.2-3.5)
   - Hermes chat interface
   - Intent interpretation engine
   - Memory integration
   - Multi-domain support

2. **Production Hardening**
   - Security audit
   - Performance optimization
   - Monitoring enhancement
   - Documentation completion

### Long-term Vision
1. **GraphQL Gateway**: Flexible client queries
2. **Event Streaming**: Real-time updates via WebSockets
3. **Edge Deployment**: Regional agent pools
4. **Federated Learning**: Cross-client improvements
5. **Voice Interface**: Audio input/output for Hermes
6. **Mobile SDKs**: iOS/Android integration

### Architecture Evolution
- Service mesh adoption (Istio)
- CQRS implementation
- Graph database for relationships
- ML pipeline for agent improvement
- Multi-tenancy support

---

*This document defines our technical architecture. All implementation should align with these patterns and principles. Last reviewed: June 3, 2025*