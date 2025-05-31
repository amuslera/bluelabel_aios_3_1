# AIOSv3 - Modular AI Agent Platform

> A production-ready platform for orchestrating multiple specialized AI agents that collaborate autonomously to deliver complex digital products.

## 🎯 Vision

Build a modular, scalable AI agent platform that:
- Orchestrates specialized agents (CTO, Frontend, Backend, QA, etc.)
- Supports both cloud-based and local LLMs with dynamic routing
- Maximizes code and data ownership
- Enables rapid development of AI-powered workflows

## 🚀 Key Features

- **Multi-Agent Orchestration**: Coordinate multiple specialized agents working together
- **Hybrid LLM Support**: Seamlessly switch between cloud (Claude, GPT-4) and local models (Llama, DeepSeek, Qwen)
- **Dynamic Routing**: Intelligent model selection based on cost, privacy, and performance
- **Open-Source First**: Built on open protocols and frameworks
- **Production Ready**: Kubernetes-native with full observability
- **Workflow Automation**: Visual workflow designer via n8n integration

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Kubernetes cluster (for production)
- 32GB+ RAM (for local LLMs)
- NVIDIA GPU (recommended for local LLMs)

## 🛠️ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/bluelabel-AIOSv3.git
cd bluelabel-AIOSv3
```

### 2. Set Up Development Environment
```bash
# Run setup script
./scripts/setup.sh

# Copy environment variables
cp .env.example .env

# Edit .env with your API keys and configuration
nano .env
```

### 3. Start Local Development
```bash
# Start core services
docker-compose up -d

# Install Python dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run database migrations
python scripts/migrate.py

# Start the API server
uvicorn api.main:app --reload
```

### 4. Access Services
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- n8n: http://localhost:5678
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web UI/CLI    │     │      n8n        │     │  External APIs  │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                         │
    ┌────▼──────────────────────▼─────────────────────────▼────┐
    │                      API Gateway (FastAPI)                │
    └────────────────────────────┬─────────────────────────────┘
                                 │
    ┌────────────────────────────▼─────────────────────────────┐
    │                    Orchestration Layer                    │
    │                  (LangGraph/CrewAI)                      │
    └────────────────────────────┬─────────────────────────────┘
                                 │
    ┌──────────┬─────────┬──────▼──────┬─────────┬────────────┐
    │   CTO    │ Frontend │   Backend   │   QA    │   DevOps   │
    │  Agent   │  Agent   │   Agent     │  Agent  │   Agent    │
    └─────┬────┴────┬────┴──────┬──────┴────┬────┴─────┬──────┘
          │         │            │            │           │
    ┌─────▼─────────▼────────────▼────────────▼───────────▼────┐
    │                     LLM Router                            │
    └─────┬──────────────────────────────────────────────┬──────┘
          │                                              │
    ┌─────▼──────┐                              ┌───────▼──────┐
    │ Cloud LLMs │                              │  Local LLMs  │
    │  (Claude)  │                              │   (Llama)    │
    └────────────┘                              └──────────────┘
```

## 📁 Project Structure

```
bluelabel-AIOSv3/
├── agents/           # Agent implementations
├── core/            # Core platform components
├── integrations/    # External integrations
├── api/             # REST API
├── config/          # Configuration files
├── infrastructure/  # Docker/K8s files
└── docs/           # Documentation
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed structure.

## 🤖 Available Agents

| Agent | Role | Primary Model | Capabilities |
|-------|------|---------------|--------------|
| CTO | Architecture & Leadership | Claude 3 Opus | System design, code review, technical decisions |
| Backend | Backend Development | DeepSeek Coder | API development, database design, integrations |
| Frontend | UI Development | GPT-4 Turbo | React/Vue development, UI/UX implementation |
| QA | Quality Assurance | Llama 3 70B | Test generation, bug detection, quality checks |
| DevOps | Infrastructure | Llama 3 70B | CI/CD, deployment, monitoring setup |

## 🔧 Configuration

### Agent Configuration
Edit `config/agents.yaml` to configure agent behaviors and model preferences.

### Model Configuration
Edit `config/models.yaml` to add new LLM providers or update existing ones.

### Routing Strategy
Edit `config/routing.yaml` to customize how models are selected for tasks.

See [LLM_ROUTING_CONFIG.md](LLM_ROUTING_CONFIG.md) for detailed configuration options.

## 📊 Monitoring

The platform includes comprehensive monitoring:

- **Metrics**: Prometheus + Grafana dashboards
- **Logging**: ELK stack for centralized logging
- **Tracing**: OpenTelemetry for distributed tracing
- **Alerts**: Configurable alerts for system health

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit

# Run integration tests
pytest tests/integration

# Run end-to-end tests
pytest tests/e2e

# Run all tests with coverage
pytest --cov=. --cov-report=html

# Run linting
ruff check .
mypy .
```

## 🚢 Deployment

### Local Development
```bash
docker-compose up
```

### Kubernetes
```bash
# Build images
make build

# Deploy to Kubernetes
kubectl apply -f infrastructure/kubernetes/

# Or use Helm
helm install aiosv3 infrastructure/kubernetes/helm/
```

See [Deployment Guide](docs/deployment/README.md) for detailed instructions.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📚 Documentation

- [Architecture Overview](docs/architecture/overview.md)
- [Agent Development Guide](docs/development/agents.md)
- [API Reference](docs/api/README.md)
- [Configuration Guide](docs/configuration/README.md)

## 🗺️ Roadmap

See [PROJECT_PHASES.md](PROJECT_PHASES.md) for detailed roadmap.

### Current Status: Phase 1 - Foundation
- [x] Project structure and documentation
- [ ] Development environment setup
- [ ] Core infrastructure
- [ ] Base agent framework
- [ ] First agent implementation

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/), [LangGraph](https://github.com/langchain-ai/langgraph), and [CrewAI](https://crewai.io/)
- Inspired by [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) and [BabyAGI](https://github.com/yoheinakajima/babyagi)
- Thanks to the open-source AI community

## 📞 Support

- **Documentation**: [docs.aiosv3.ai](https://docs.aiosv3.ai)
- **Issues**: [GitHub Issues](https://github.com/yourusername/bluelabel-AIOSv3/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/bluelabel-AIOSv3/discussions)
- **Email**: support@aiosv3.ai

---

Built with ❤️ by the AIOSv3 Team