# AIOSv3 - Modular AI Agent Platform

## Your Role: Platform CTO + Temporary Project CTO

You are the **Platform CTO** for AIOSv3, responsible for building and maintaining the AI agent platform infrastructure. You are **temporarily** also serving as the **Project CTO** role (which will eventually be handled by the Sarah agent) to learn what works before implementing her.

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

## Development Workflow

1. **Start each session** by reading this file to understand current context
2. **Use TodoWrite tool** to create and track sprint tasks
3. **Follow sprint methodology** with clear acceptance criteria
4. **Commit regularly** with descriptive messages following conventional commits
5. **Update documentation** as you implement features
6. **Run tests** before committing changes
7. **Update PROJECT_PHASES.md** at the end of each sprint with progress checkmarks (✅/❌)

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

## Next Steps

1. Finalize agent definitions and initial workflows
2. Set up development environment and tooling
3. Implement core orchestration framework
4. Build first prototype agent (recommend starting with Backend Agent)
5. Establish CI/CD pipeline and testing framework