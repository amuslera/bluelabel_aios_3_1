# 🚀 AIOSv3.1 Quick Start Guide

**Get up and running with the AI agent platform in 5 minutes!**

## 🎯 What is AIOSv3.1?

A platform where AI agents (named after Greek gods) work together to build software:
- **Hermes** 🪽 - Talks to users, understands what they want (Coming Soon)
- **Apollo** 🏛️ - Builds backend APIs and databases
- **Aphrodite** 🎨 - Creates beautiful user interfaces
- **Athena** 🛡️ - Tests everything and finds bugs
- **Hephaestus** 🔨 - Deploys and manages infrastructure

## 📋 Prerequisites

- Python 3.9+
- Docker (optional)
- Ollama (for local LLM) or API keys for Claude/OpenAI

## 🏃 Quick Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/bluelabel-aiosv3.1.git
cd bluelabel-aiosv3.1
```

### 2. Install Dependencies
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Set Up Configuration

#### Option A: Local LLM (Free - Recommended for Development)
```bash
# Install Ollama
brew install ollama  # macOS
# Or visit: https://ollama.ai for other platforms

# Start Ollama
ollama serve

# Pull a model (already done if you followed Sprint 3.0)
ollama pull mistral:latest
```

#### Option B: Cloud LLMs
Create `.env` file:
```env
ANTHROPIC_API_KEY=your_claude_key_here
OPENAI_API_KEY=your_openai_key_here
```

### 4. Verify Installation
```bash
# Test local LLM setup
python test_local_llm.py

# Or run the platform demo
python demo_final.py
```

## 🎮 Running Your First Demo

### See the Agents in Action
```bash
# Run the full theatrical demo
python demo_final.py

# Quick 30-second demo
python demo_working_simple.py

# Task management demo
python scripts/task_management_demo.py
```

### What You'll See:
- Real-time visualization of agents working
- Chat messages between agents
- Progress bars and metrics
- Final deliverables

## 🏛️ Meet the Pantheon

### Current Agents (Operational)
1. **Apollo** (Backend) - "I'll optimize the API for performance..."
2. **Aphrodite** (Frontend) - "Let me create a beautiful interface..."
3. **Athena** (QA) - "I found an edge case we should handle..."
4. **Hephaestus** (DevOps) - "Automating the deployment pipeline..."

### Coming Soon
5. **Hera** (Project CTO) - Coordinates the team
6. **Hermes** (Concierge) - Your conversational interface

## 💻 Basic Usage

### Start a Simple Project
```python
from src.agents.specialists.backend_agent import BackendAgent
from src.agents.specialists.frontend_agent import FrontendAgent

# Create agents
apollo = BackendAgent()
aphrodite = FrontendAgent()

# Give them a task
await apollo.process_task({
    "type": "api_endpoint",
    "description": "Create user registration endpoint"
})

await aphrodite.process_task({
    "type": "component", 
    "description": "Create login form component"
})
```

### Monitor Agent Activity
```bash
# In another terminal
python -m src.visualization.theatrical_dashboard
```

## 🔧 Configuration

### LLM Routing (Automatic)
- **Local Development**: Uses Ollama (free)
- **Complex Tasks**: Routes to Claude
- **Fallback**: OpenAI

See `/config/llm_routing.yaml` for details.

### Agent Configuration
See `/config/agents.yaml` for agent settings.

## 📚 Key Documentation

1. **Architecture**: `/ARCHITECTURE.md` - System design
2. **Agent Guide**: `/AGENT_ROSTER.md` - Meet the gods
3. **Development**: `/DEVELOPMENT_PROCESS.md` - How we work
4. **Local LLM**: `/docs/LOCAL_LLM_SETUP.md` - Cost-free setup

## 🧪 Running Tests

```bash
# Unit tests
pytest

# Integration tests
pytest tests/integration/

# Test specific agent
pytest tests/unit/test_backend_agent.py
```

## 🚀 Next Steps

1. **Run the demos** to see agents in action
2. **Read the docs** to understand the architecture
3. **Try local LLM** to save on API costs
4. **Build something** with the agents!

## 🆘 Getting Help

- **Issues**: Check `/TROUBLESHOOTING.md`
- **Logs**: See `/logs/` directory
- **Community**: Join our Discord (coming soon)

## 🎯 Common Commands

```bash
# See what models you have
ollama list

# Check agent status
python -m src.agents.base.registry list

# Run visualization
python demo_final.py

# Test local LLM
python test_local_llm.py
```

## 🏗️ Project Structure

```
bluelabel-aiosv3.1/
├── src/
│   ├── agents/          # The gods live here
│   ├── core/            # Platform infrastructure
│   └── visualization/   # See agents work
├── config/              # Configuration files
├── demos/               # Example demonstrations
├── docs/                # Documentation
└── tests/               # Test suites
```

## 💡 Pro Tips

1. **Use local LLM** for development (free!)
2. **Watch the demos** to understand agent collaboration
3. **Read agent personalities** in `/AGENT_ROSTER.md`
4. **Follow the sprints** in `/sprints/` to see how we built this

---

**Ready to build something amazing with AI agents? Let's go! 🚀**

For detailed information, see the full documentation in `/docs/`.