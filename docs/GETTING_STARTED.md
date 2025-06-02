# AIOSv3 Getting Started Guide

Welcome to AIOSv3 - the modular AI agent platform that orchestrates specialized agents to autonomously deliver complex digital products.

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (recommended: Python 3.11)
- **Git** for version control
- **Docker** (optional, for containerized deployment)
- **Redis** (optional, for production memory backend)

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-org/bluelabel-AIOSv3.1.git
cd bluelabel-AIOSv3.1

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Monitoring Server

The monitoring server is the central hub for agent coordination:

```bash
# Start monitoring server
python projects/monitoring/src/enhanced_monitoring_server.py
```

You should see:
```
🚀 Enhanced Monitoring Server starting on port 6795
🔑 Master API Key: aios_...
✅ Database initialized
✅ Server running on http://0.0.0.0:6795
```

**Save the API key** - you'll need it for agent registration!

### 3. Launch the Control Center

In a new terminal, start the Control Center dashboard:

```bash
# Start Control Center
python projects/control_center/src/enhanced_control_center.py
```

This opens an interactive terminal UI where you can:
- Monitor agent status in real-time
- View system health metrics
- Track task execution
- Manage agent lifecycle

### 4. Run Your First Agent

Try the example auto-registering agent:

```bash
# Set the API key (use the one from step 2)
export MONITORING_API_KEY="aios_your_key_here"

# Run example agent
python examples/auto_registering_agent.py
```

You should see the agent:
1. Register with the monitoring server
2. Execute sample tasks
3. Send regular heartbeats
4. Appear in the Control Center dashboard

### 5. Run Coordination Tests

Validate everything works with the test suite:

```bash
# Run all coordination tests
python run_coordination_tests.py
```

## 🎯 What's Next?

- **[Control Center Guide](CONTROL_CENTER.md)** - Master the dashboard
- **[Agent Development](AGENT_DEVELOPMENT.md)** - Build your own agents
- **[API Reference](API_REFERENCE.md)** - Integrate with external systems
- **[Deployment Guide](DEPLOYMENT.md)** - Production setup

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MONITORING_URL` | `http://localhost:6795` | Monitoring server URL |
| `MONITORING_API_KEY` | `aios_default_key` | API key for authentication |
| `MONITORING_DB_PATH` | `monitoring.db` | SQLite database path |
| `RATE_LIMIT` | `100` | Requests per minute limit |
| `JWT_SECRET` | Auto-generated | JWT signing secret |

### Configuration Files

- `config/agents.yaml` - Agent definitions and capabilities
- `config/models.yaml` - LLM model configurations
- `config/routing.yaml` - Task routing rules

## 🆘 Troubleshooting

### Common Issues

**"Connection refused" errors:**
- Ensure monitoring server is running
- Check firewall settings
- Verify correct port (default: 6795)

**"Invalid API key" errors:**
- Use the API key displayed when starting monitoring server
- Set `MONITORING_API_KEY` environment variable
- Check for typos in the key

**Control Center not updating:**
- Verify WebSocket connection to monitoring server
- Check network connectivity
- Restart Control Center if needed

**Agent registration fails:**
- Monitoring server must be running first
- Check API key configuration
- Review agent logs for detailed error messages

### Getting Help

1. **Check Logs**: All components log detailed information
2. **Run Health Checks**: Use `curl http://localhost:6795/api/health`
3. **Test Connectivity**: Use the test script `test_agent_registration.py`
4. **Review Documentation**: Check specific component guides

## 🏗️ Architecture Overview

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

### Key Components

- **Control Center**: Real-time dashboard for monitoring and management
- **Monitoring Server**: Central hub for agent coordination and data collection
- **Agent Registry**: Automatic agent discovery and lifecycle management
- **Specialized Agents**: Task-specific AI agents with distinct capabilities

## 📊 Monitoring Dashboard

Access the web dashboard at: `http://localhost:6795/api/health`

Key metrics displayed:
- Active agent count
- Task execution rates
- System health status
- Performance trends
- Error rates and alerts

## 🔄 Next Steps

1. **Explore Examples**: Try different agent examples in `examples/`
2. **Build Custom Agents**: Follow the agent development guide
3. **Scale Up**: Add more specialized agents for your use case
4. **Production Deploy**: Use Docker and Kubernetes for scale
5. **Monitor Performance**: Use the built-in analytics and metrics

Welcome to the future of AI agent orchestration! 🤖✨