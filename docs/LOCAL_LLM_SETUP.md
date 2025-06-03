# Local LLM Setup Guide for AIOSv3.1

**Last Updated**: June 3, 2025  
**Sprint**: 3.0 - Infrastructure & Cost Optimization  
**Status**: COMPLETE ✅

## Overview

This guide explains how to use local LLMs with AIOSv3.1 agents for 100% cost savings during development and testing.

## Quick Start

### 1. Verify Ollama is Running
```bash
# Check if Ollama is installed
ollama --version

# Start Ollama service (if not running)
ollama serve

# List available models
ollama list
```

### 2. Current Setup
- **Model**: mistral:latest (4.1GB)
- **Endpoint**: http://localhost:11434
- **All 4 agents**: Configured to use local model first

### 3. Test Local LLM
```bash
# Run integration test
python3 test_local_llm.py
```

Expected output:
- Connection Test: ✓ Passed
- Generation Test: ✓ Passed  
- Agent Tests: ✓ All Passed

## Configuration Details

### LLM Routing (`/config/llm_routing.yaml`)
- **Priority**: Ollama (1) > Claude (2) > OpenAI (3)
- **Local Target**: 85% of requests
- **Fallback**: Cloud providers for complex tasks

### Agent Model Preferences
- **Marcus (Backend)**: mistral:latest → claude-3-5-sonnet
- **Emily (Frontend)**: mistral:latest → gpt-4-turbo
- **Alex (QA)**: mistral:latest → gpt-3.5-turbo
- **Jordan (DevOps)**: mistral:latest → gpt-4-turbo

## Performance Expectations

### Response Times (M4 Pro MacBook)
- Simple tasks: 8-10 seconds
- Medium tasks: 10-15 seconds
- Complex tasks: 15-20 seconds

### Cost Savings
- Development/Testing: 100% ($0.00)
- Estimated savings: $0.008 per 4 agent requests

## Running Agents with Local LLM

### Example: Backend Agent Task
```python
from src.agents.specialists.backend_agent import MarcusBackendAgent

# Agent will automatically use local LLM based on routing config
agent = MarcusBackendAgent()
response = await agent.process_task({
    "type": "code_generation",
    "content": "Create a FastAPI endpoint for user login"
})
```

### Running Full Demo
```bash
# The demo will use local models automatically
python3 demo_final.py
```

## Optional Enhancements

### 1. Download Better Code Model
```bash
# For improved code generation (4.5GB, 32k context)
ollama pull qwen2.5-coder:7b
```

### 2. Mac Mini as LLM Server
```bash
# On Mac Mini:
OLLAMA_HOST=0.0.0.0:11434 ollama serve

# On MacBook Pro:
export OLLAMA_HOST=mac-mini.local:11434
```

### 3. Add More Models
```bash
# For specialized tasks
ollama pull codellama:13b     # Better for code
ollama pull llama3.1:8b       # 128k context
ollama pull deepseek-coder:6.7b  # Code-specific
```

## Monitoring Local Usage

Check the test results:
```bash
cat local_llm_test_results.json
```

View Ollama logs:
```bash
# macOS
tail -f ~/.ollama/logs/server.log
```

## Troubleshooting

### Ollama Not Running
```bash
brew services start ollama
# or
ollama serve
```

### Slow Response Times
- Check available RAM: `top` or Activity Monitor
- Reduce concurrent requests in config
- Use smaller models for simple tasks

### Model Download Issues
```bash
# Resume interrupted download
ollama pull mistral:latest

# Check download progress
ps aux | grep ollama
```

## Best Practices

1. **Development**: Use local models for all non-critical tasks
2. **Testing**: Run test suites with local models
3. **Production**: Use cloud models for customer-facing features
4. **Complex Tasks**: Let routing system escalate to cloud

## Cost Analysis

### Before Local LLM
- Average daily cost: $10-50 (depending on usage)
- Cost per agent task: $0.002-0.02

### After Local LLM  
- Development cost: $0.00
- Testing cost: $0.00
- Production cost: Reduced by 85%+

## Next Steps

1. Download additional models for specific use cases
2. Set up Mac Mini as dedicated LLM server
3. Fine-tune routing rules based on actual usage
4. Monitor quality vs. cost trade-offs

---

**Sprint 3.0 Complete!** Local LLM infrastructure is ready for cost-effective development.