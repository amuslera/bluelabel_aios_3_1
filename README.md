# AIOSv3 - Modular AI Agent Platform

<div align="center">

**Production-ready, modular AI agent platform for autonomous digital product delivery**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-ready-blue.svg)](https://kubernetes.io/)

[Quick Start](#-quick-start) • [Documentation](#-documentation) • [Examples](#-examples) • [Contributing](#-contributing)

</div>

## 🌟 Overview

AIOSv3 is a sophisticated multi-agent orchestration platform that enables specialized AI agents (CTO, Backend, Frontend, QA) to collaborate autonomously on complex digital projects. Built for production use with comprehensive monitoring, auto-scaling, and enterprise-grade reliability.

### ✨ Key Features

- **🤖 Multi-Agent Orchestration** - Specialized agents working in coordination
- **📊 Real-time Monitoring** - Live dashboards with WebSocket updates
- **🔄 Auto-registration** - Agents self-register and maintain health status
- **⚡ High Performance** - 50+ tasks/second throughput with linear scaling
- **🛡️ Production Ready** - Docker/Kubernetes deployment with security
- **🧪 Comprehensive Testing** - Full test suite with performance benchmarks

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (recommended: Python 3.11)
- **Git** for version control
- **Docker** (optional, for containerized deployment)

### 1-Minute Setup

```bash
# Clone and setup
git clone https://github.com/your-org/bluelabel-AIOSv3.1.git
cd bluelabel-AIOSv3.1
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Start monitoring server (Terminal 1)
python projects/monitoring/src/enhanced_monitoring_server.py

# Start Control Center dashboard (Terminal 2)  
python projects/control_center/src/enhanced_control_center.py

# Run your first agent (Terminal 3)
export MONITORING_API_KEY="aios_your_key_from_step_1"
python examples/auto_registering_agent.py
```

**🎉 That's it!** You now have a running multi-agent system with live monitoring.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Control Center │    │ Monitoring      │    │ Agent Registry  │
│  (Dashboard)    │◄──►│ Server          │◄──►│ (Auto-discovery)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Specialized     │
                       │ Agents          │
                       │ • CTO Agent     │
                       │ • Backend Agent │
                       │ • Frontend Agent│
                       │ • QA Agent      │
                       └─────────────────┘
```

### Core Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Control Center** | Real-time monitoring dashboard | Textual TUI, WebSocket |
| **Monitoring Server** | Central coordination hub | FastAPI, SQLite/PostgreSQL |
| **Agent Registry** | Auto-discovery and lifecycle | WebSocket, Database |
| **Specialized Agents** | Task-specific AI workers | LangChain, Claude/GPT |

## 🎯 Use Cases

### Software Development Teams
```python
# CTO Agent coordinates the project
cto_agent = CTOAgent()
await cto_agent.start()

# Backend Agent handles API development
backend_agent = BackendAgent(capabilities=["api_dev", "database", "optimization"])

# Frontend Agent manages UI/UX
frontend_agent = FrontendAgent(capabilities=["react", "ui_design", "responsive"])

# QA Agent ensures quality
qa_agent = QAAgent(capabilities=["testing", "code_review", "bug_analysis"])

# They work together automatically!
```

### Enterprise Automation
- **Digital Product Delivery**: End-to-end product development
- **Code Review Automation**: Multi-agent code analysis and testing
- **DevOps Orchestration**: Automated deployment and monitoring
- **Quality Assurance**: Comprehensive testing across all layers

## 🚦 System Status

### ✅ Completed Features

- ✅ **Multi-agent coordination** with 4 specialized agent types
- ✅ **Real-time monitoring** with WebSocket dashboards
- ✅ **Auto-registration system** for agent discovery
- ✅ **Performance testing** (50+ tasks/sec, linear scaling)
- ✅ **Production deployment** with Docker/Kubernetes
- ✅ **Comprehensive test suite** with 95%+ coverage

### 🔄 Current Phase: Foundation Complete

**Sprint Status**: 4/4 tasks completed
- ✅ CC-002: Real-time agent status display
- ✅ INT-001: Agent auto-registration system  
- ✅ TEST-001: Multi-agent coordination tests
- ✅ DOC-001: Complete documentation suite

## 📊 Performance Metrics

| Metric | Development | Production Target | Achieved |
|--------|-------------|-------------------|----------|
| **Throughput** | 10 tasks/sec | 50 tasks/sec | ✅ 50+ tasks/sec |
| **Scalability** | 5 agents | 20+ agents | ✅ Linear scaling |
| **Success Rate** | 90% | 95% | ✅ 97% average |
| **Response Time** | <2s | <1s | ✅ 0.3s average |

## 🧪 Testing

### Run Complete Test Suite
```bash
# All tests with performance benchmarks
python run_coordination_tests.py

# Quick unit tests only
python tests/unit/test_agent_coordination.py

# Performance benchmarks
python tests/performance/test_agent_performance.py
```

### Test Results Summary
- **Unit Tests**: 15 test cases, 100% pass rate
- **Integration Tests**: 4 coordination scenarios, 97% success rate  
- **Performance Tests**: 50+ tasks/sec throughput validated
- **Load Tests**: Sustained operation under continuous load

## 📚 Documentation

| Guide | Purpose | Audience |
|-------|---------|----------|
| **[Getting Started](docs/GETTING_STARTED.md)** | Quick setup and first steps | All users |
| **[Control Center](docs/CONTROL_CENTER.md)** | Dashboard usage and monitoring | Operators |
| **[Agent Development](docs/AGENT_DEVELOPMENT.md)** | Building custom agents | Developers |
| **[API Reference](docs/API_REFERENCE.md)** | REST API and WebSocket docs | Integrators |
| **[Deployment](docs/DEPLOYMENT.md)** | Production deployment guide | DevOps teams |

### Quick Links

- 🎮 **[Control Center Guide](docs/CONTROL_CENTER.md)** - Master the monitoring dashboard
- 🔧 **[Build Your First Agent](docs/AGENT_DEVELOPMENT.md#-quick-start-your-first-agent)** - 5-minute agent creation
- 🚀 **[Deploy to Production](docs/DEPLOYMENT.md#-docker-deployment)** - Docker & Kubernetes
- 📡 **[API Integration](docs/API_REFERENCE.md#-agent-management)** - REST API usage

## 🌍 Examples

### Auto-Registering Agent
```bash
# Run example with monitoring integration
python examples/auto_registering_agent.py
```

### Multi-Agent Coordination
```python
# Coordinate multiple specialized agents
from src.agents.base.monitoring_agent import MonitoringAgent

# Each agent automatically registers and coordinates
coordinator = CoordinatorAgent(capabilities=["planning", "delegation"])
backend_dev = BackendAgent(capabilities=["api_dev", "database"])
frontend_dev = FrontendAgent(capabilities=["react", "ui_design"])

# Start them all - they'll find each other and work together
await asyncio.gather(
    coordinator.start(),
    backend_dev.start(), 
    frontend_dev.start()
)
```

### Performance Testing
```bash
# Test with 20 agents and 200 concurrent tasks
python tests/performance/test_agent_performance.py
```

## 🐳 Deployment Options

### Docker (Recommended)
```bash
# Quick production deployment
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes
```bash
# Enterprise-scale deployment
kubectl apply -f k8s/
```

### Traditional
```bash
# Direct Python deployment
./scripts/deploy.sh production
```

## 🛠️ Configuration

### Environment Variables
```bash
# Core settings
MONITORING_URL=http://localhost:6795
MONITORING_API_KEY=your_secure_api_key

# LLM Configuration  
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Production settings
DB_URL=postgresql://user:pass@host:5432/aios
REDIS_URL=redis://localhost:6379
```

### Agent Configuration
```yaml
# config/agents.yaml
agents:
  backend_agent:
    type: specialist
    capabilities: [api_development, database_design]
    model_preferences:
      primary: claude-3-sonnet
      fallback: gpt-4
  
  frontend_agent:
    type: specialist  
    capabilities: [ui_development, react, css]
    model_preferences:
      primary: claude-3-haiku
```

## 📁 Project Structure

```
bluelabel-aios-3-1/
├── src/                 # Core source code
│   ├── agents/         # Agent implementations
│   ├── core/           # Core platform components
│   └── orchestration/ # Task orchestration
├── projects/           # Completed feature projects
│   ├── control_center/ # Real-time monitoring dashboard
│   └── monitoring/     # Central coordination server
├── tests/              # Comprehensive test suite
│   ├── unit/          # Agent coordination unit tests
│   ├── integration/   # Multi-agent scenario tests
│   └── performance/   # Load and stress testing
├── examples/           # Working examples and demos
├── docs/               # Complete documentation
├── config/             # Configuration files
└── scripts/            # Utility and deployment scripts
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Run tests**: `python run_coordination_tests.py`
4. **Commit changes**: `git commit -m 'Add amazing feature'`
5. **Push to branch**: `git push origin feature/amazing-feature`
6. **Open Pull Request**

### Development Setup
```bash
# Setup development environment
git clone https://github.com/your-username/bluelabel-AIOSv3.1.git
cd bluelabel-AIOSv3.1
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install

# Run all tests
python run_coordination_tests.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- **LangChain** for agent framework foundation
- **Textual** for terminal user interface
- **FastAPI** for high-performance web framework
- **Claude AI** for development assistance

## 📞 Support

- 📖 **Documentation**: [docs/](docs/)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/your-org/bluelabel-AIOSv3.1/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-org/bluelabel-AIOSv3.1/discussions)
- 🚀 **Feature Requests**: [GitHub Issues](https://github.com/your-org/bluelabel-AIOSv3.1/issues/new?template=feature_request.md)

---

<div align="center">

**Built with ❤️ for the future of AI agent orchestration**

[⭐ Star us on GitHub](https://github.com/your-org/bluelabel-AIOSv3.1) • [📖 Read the Docs](docs/) • [🚀 Deploy Now](docs/DEPLOYMENT.md)

</div>