# AIOSv3 Directory Structure

```
bluelabel-AIOSv3/
├── .github/                      # GitHub specific files
│   ├── workflows/                # CI/CD workflows
│   └── ISSUE_TEMPLATE/           # Issue templates
│
├── agents/                       # Agent implementations
│   ├── base/                     # Base agent classes
│   │   ├── __init__.py
│   │   ├── agent.py              # Abstract base agent
│   │   ├── memory.py             # Memory management
│   │   └── context.py            # Context handling
│   │
│   ├── specialists/              # Specialized agents
│   │   ├── __init__.py
│   │   ├── cto_agent.py          # CTO/Architecture agent
│   │   ├── backend_agent.py      # Backend developer
│   │   ├── frontend_agent.py     # Frontend developer
│   │   ├── qa_agent.py           # QA engineer
│   │   └── devops_agent.py       # DevOps engineer
│   │
│   └── tests/                    # Agent-specific tests
│       ├── __init__.py
│       └── test_*.py
│
├── core/                         # Core platform components
│   ├── __init__.py
│   ├── orchestrator/             # Agent orchestration
│   │   ├── __init__.py
│   │   ├── scheduler.py          # Task scheduling
│   │   ├── workflow.py           # Workflow engine
│   │   └── coordinator.py        # Agent coordination
│   │
│   ├── routing/                  # LLM routing logic
│   │   ├── __init__.py
│   │   ├── router.py             # Main routing engine
│   │   ├── strategies.py         # Routing strategies
│   │   └── models.py             # Model configurations
│   │
│   ├── communication/            # Inter-agent communication
│   │   ├── __init__.py
│   │   ├── mcp.py                # MCP protocol implementation
│   │   ├── events.py             # Event system
│   │   └── messages.py           # Message types
│   │
│   └── memory/                   # Shared memory system
│       ├── __init__.py
│       ├── store.py              # Memory storage
│       ├── vector_db.py          # Vector DB interface
│       └── cache.py              # Caching layer
│
├── integrations/                 # External integrations
│   ├── __init__.py
│   ├── llm/                      # LLM providers
│   │   ├── __init__.py
│   │   ├── base.py               # Base LLM interface
│   │   ├── claude.py             # Claude integration
│   │   ├── openai.py             # OpenAI integration
│   │   ├── local/                # Local model integrations
│   │   │   ├── __init__.py
│   │   │   ├── llama.py          # Llama models
│   │   │   ├── deepseek.py       # DeepSeek models
│   │   │   └── qwen.py           # Qwen models
│   │   └── config.py             # LLM configurations
│   │
│   ├── tools/                    # External tools
│   │   ├── __init__.py
│   │   ├── github.py             # GitHub integration
│   │   ├── jira.py               # Jira integration
│   │   ├── slack.py              # Slack integration
│   │   └── custom.py             # Custom tool base
│   │
│   └── workflows/                # Workflow automation
│       ├── __init__.py
│       ├── n8n.py                # n8n integration
│       └── templates/            # Workflow templates
│
├── api/                          # API layer
│   ├── __init__.py
│   ├── main.py                   # FastAPI app
│   ├── routes/                   # API routes
│   │   ├── __init__.py
│   │   ├── agents.py             # Agent endpoints
│   │   ├── workflows.py          # Workflow endpoints
│   │   ├── admin.py              # Admin endpoints
│   │   └── health.py             # Health checks
│   │
│   ├── models/                   # Pydantic models
│   │   ├── __init__.py
│   │   ├── requests.py           # Request models
│   │   └── responses.py          # Response models
│   │
│   └── middleware/               # API middleware
│       ├── __init__.py
│       ├── auth.py               # Authentication
│       ├── rate_limit.py         # Rate limiting
│       └── logging.py            # Request logging
│
├── ui/                           # Web UI (Phase 5)
│   ├── src/                      # Source code
│   │   ├── components/           # React components
│   │   ├── pages/                # Page components
│   │   ├── hooks/                # Custom hooks
│   │   ├── services/             # API services
│   │   └── App.tsx               # Main app
│   │
│   ├── public/                   # Static assets
│   ├── package.json              # Node dependencies
│   └── tsconfig.json             # TypeScript config
│
├── infrastructure/               # Infrastructure as Code
│   ├── docker/                   # Docker configurations
│   │   ├── Dockerfile.agent      # Agent container
│   │   ├── Dockerfile.api        # API container
│   │   └── docker-compose.yml    # Local development
│   │
│   ├── kubernetes/               # K8s manifests
│   │   ├── base/                 # Base configurations
│   │   ├── overlays/             # Environment overlays
│   │   └── helm/                 # Helm charts
│   │
│   └── terraform/                # Cloud infrastructure
│       ├── modules/              # Terraform modules
│       └── environments/         # Environment configs
│
├── config/                       # Configuration files
│   ├── __init__.py
│   ├── settings.py               # Application settings
│   ├── agents.yaml               # Agent configurations
│   ├── models.yaml               # Model configurations
│   └── workflows.yaml            # Workflow definitions
│
├── scripts/                      # Utility scripts
│   ├── setup.sh                  # Development setup
│   ├── deploy.sh                 # Deployment script
│   ├── test.sh                   # Test runner
│   └── migrate.py                # Database migrations
│
├── tests/                        # Integration tests
│   ├── __init__.py
│   ├── integration/              # Integration tests
│   ├── e2e/                      # End-to-end tests
│   └── fixtures/                 # Test fixtures
│
├── docs/                         # Documentation
│   ├── architecture/             # Architecture docs
│   │   ├── overview.md           # System overview
│   │   ├── agents.md             # Agent design
│   │   └── routing.md            # Routing design
│   │
│   ├── api/                      # API documentation
│   ├── deployment/               # Deployment guides
│   └── development/              # Development guides
│
├── monitoring/                   # Monitoring configs
│   ├── prometheus/               # Prometheus configs
│   ├── grafana/                  # Grafana dashboards
│   └── alerts/                   # Alert rules
│
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore file
├── README.md                     # Project README
├── CLAUDE.md                     # AI assistant context
├── PROJECT_PHASES.md             # Project roadmap
├── PROJECT_STRUCTURE.md          # This file
├── pyproject.toml                # Python project config
├── requirements.txt              # Python dependencies
├── requirements-dev.txt          # Dev dependencies
└── Makefile                      # Common commands
```

## Key Design Decisions

### 1. Modular Agent Architecture
- Each agent is self-contained in `agents/specialists/`
- Shared functionality in `agents/base/`
- Clear separation between agent logic and infrastructure

### 2. Core Platform Services
- `core/orchestrator/`: Manages agent lifecycle and workflows
- `core/routing/`: Handles LLM selection and routing
- `core/communication/`: Standardized inter-agent messaging
- `core/memory/`: Shared state and context management

### 3. Integration Layer
- `integrations/llm/`: Abstracted LLM providers
- `integrations/tools/`: External service connectors
- `integrations/workflows/`: Workflow automation adapters

### 4. API Design
- FastAPI-based REST API in `api/`
- Clear route organization
- Middleware for cross-cutting concerns

### 5. Infrastructure as Code
- Docker for containerization
- Kubernetes for orchestration
- Terraform for cloud resources

### 6. Configuration Management
- YAML-based configuration in `config/`
- Environment-specific overrides
- Runtime configuration updates

### 7. Testing Strategy
- Unit tests co-located with code
- Integration tests in `tests/`
- E2E tests for critical paths

### 8. Documentation
- Architecture documentation in `docs/`
- API documentation auto-generated
- Development guides for onboarding

## File Naming Conventions

### Python Files
- Snake_case for modules: `backend_agent.py`
- Snake_case for functions: `process_request()`
- PascalCase for classes: `BackendAgent`

### TypeScript/JavaScript
- PascalCase for components: `AgentDashboard.tsx`
- camelCase for utilities: `formatResponse.ts`
- kebab-case for CSS: `agent-dashboard.css`

### Configuration Files
- Lowercase with hyphens: `agent-config.yaml`
- Environment prefix: `prod-settings.yaml`

### Documentation
- Uppercase for top-level: `README.md`
- Lowercase for guides: `deployment-guide.md`

## Module Dependencies

```
┌─────────────┐
│     API     │ ◄── External requests
└──────┬──────┘
       │
┌──────▼──────┐
│ Orchestrator │ ◄── Workflow management
└──────┬──────┘
       │
┌──────▼──────┐
│   Agents    │ ◄── Task execution
└──────┬──────┘
       │
┌──────▼──────┐
│   Router    │ ◄── LLM selection
└──────┬──────┘
       │
┌──────▼──────┐
│     LLM     │ ◄── Model inference
└─────────────┘
```

## Getting Started

1. Clone the repository
2. Run `./scripts/setup.sh` to set up development environment
3. Copy `.env.example` to `.env` and configure
4. Run `docker-compose up` for local development
5. Access API at `http://localhost:8000`
6. Access UI at `http://localhost:3000` (when implemented)

## Development Workflow

1. Create feature branch from `main`
2. Implement changes following structure
3. Write tests for new functionality
4. Update documentation
5. Submit PR for review
6. Merge after approval and CI pass