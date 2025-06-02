# Agent Development Guide

Learn how to build specialized AI agents for the AIOSv3 platform. This guide covers everything from basic agent creation to advanced coordination patterns.

## 🏗️ Agent Architecture

### Base Agent Hierarchy

```
BaseAgent (Abstract)
├── MonitoringAgent (Auto-registration)
├── SpecializedAgent (Role-specific)
└── CustomAgent (Your implementation)
```

### Core Components

1. **Agent Configuration** - Defines capabilities and behavior
2. **Task Execution** - Core business logic
3. **Communication** - Inter-agent messaging
4. **Memory Management** - Persistent state storage
5. **Health Monitoring** - Status and performance tracking

## 🚀 Quick Start: Your First Agent

### 1. Basic Agent Template

```python
from src.agents.base.monitoring_agent import MonitoringAgent
from src.agents.base.agent import AgentConfig, Task
from src.agents.base.types import AgentType

class MyFirstAgent(MonitoringAgent):
    """A simple example agent."""
    
    async def _execute_task_internal(self, task: Task, model_id: str) -> dict:
        """Execute the task - implement your logic here."""
        
        # Your agent logic goes here
        result = f"Processed: {task.description}"
        
        # Return structured result
        return {
            "status": "completed",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def can_handle_task(self, task: Task) -> bool:
        """Define which tasks this agent can handle."""
        return task.type in ["general", "example"] or "general" in self.capabilities

# Usage
async def main():
    config = AgentConfig(
        name="My First Agent",
        description="An example agent for learning",
        agent_type=AgentType.GENERALIST,
        capabilities=["general", "example"],
        model_preferences={"primary": "claude-3-sonnet"}
    )
    
    agent = MyFirstAgent(config=config)
    await agent.start()
    
    # Agent is now running and registered!
    # It will automatically handle tasks and send heartbeats
```

### 2. Run Your Agent

```bash
# Set monitoring server connection
export MONITORING_API_KEY="your_api_key"
export MONITORING_URL="http://localhost:6795"

# Run your agent
python my_first_agent.py
```

## 🎯 Agent Types and Roles

### Specialist Agent Patterns

#### Backend Agent
```python
class BackendAgent(MonitoringAgent):
    """Specialized agent for backend development tasks."""
    
    def __init__(self, **kwargs):
        config = AgentConfig(
            name="Backend Developer Agent",
            description="Handles API development, database design, and backend logic",
            agent_type=AgentType.SPECIALIST,
            capabilities=[
                "api_development", "database_design", "backend_logic",
                "performance_optimization", "security_implementation"
            ],
            model_preferences={
                "primary": "claude-3-sonnet",
                "code_review": "gpt-4",
                "documentation": "claude-3-haiku"
            }
        )
        super().__init__(config=config, **kwargs)
    
    async def _execute_task_internal(self, task: Task, model_id: str) -> dict:
        if task.type == "api_development":
            return await self._develop_api(task)
        elif task.type == "database_design":
            return await self._design_database(task)
        elif task.type == "performance_optimization":
            return await self._optimize_performance(task)
        else:
            return await self._handle_general_backend_task(task)
    
    async def _develop_api(self, task: Task) -> dict:
        """Implement API development logic."""
        # Use the assigned LLM model for code generation
        # Access task parameters: task.parameters
        # Report progress: await self.send_custom_metric("progress", 0.5)
        
        return {
            "api_endpoints": ["GET /users", "POST /users"],
            "documentation": "OpenAPI spec generated",
            "tests": "Unit tests created"
        }
```

#### Frontend Agent
```python
class FrontendAgent(MonitoringAgent):
    """Specialized agent for frontend development."""
    
    def __init__(self, **kwargs):
        config = AgentConfig(
            name="Frontend Developer Agent", 
            description="Handles UI/UX development and user experience",
            agent_type=AgentType.SPECIALIST,
            capabilities=[
                "ui_development", "ux_design", "responsive_design",
                "component_creation", "state_management"
            ]
        )
        super().__init__(config=config, **kwargs)
    
    def can_handle_task(self, task: Task) -> bool:
        frontend_tasks = [
            "ui_development", "component_creation", 
            "styling", "user_interface", "frontend"
        ]
        return any(cap in str(task.type) for cap in frontend_tasks)
```

#### QA Agent
```python
class QAAgent(MonitoringAgent):
    """Quality assurance and testing agent."""
    
    async def _execute_task_internal(self, task: Task, model_id: str) -> dict:
        if task.type == "test_creation":
            return await self._create_tests(task)
        elif task.type == "code_review":
            return await self._review_code(task)
        elif task.type == "bug_analysis":
            return await self._analyze_bugs(task)
        
        return {"status": "completed", "action": "qa_task_completed"}
    
    async def _create_tests(self, task: Task) -> dict:
        """Generate comprehensive test suites."""
        test_types = ["unit", "integration", "e2e"]
        
        await self.report_milestone("Test creation started")
        
        results = {}
        for test_type in test_types:
            # Generate tests using LLM
            await self.send_custom_metric("test_progress", f"{test_type}_tests")
            results[f"{test_type}_tests"] = f"Generated {test_type} tests"
        
        return {
            "tests_created": results,
            "coverage_target": "90%",
            "frameworks": ["pytest", "jest", "playwright"]
        }
```

## 🤝 Agent Coordination Patterns

### 1. Task Delegation Pattern

```python
class CoordinatorAgent(MonitoringAgent):
    """Coordinates work between multiple specialized agents."""
    
    async def _execute_task_internal(self, task: Task, model_id: str) -> dict:
        if task.complexity > 7:
            # Break down complex task
            subtasks = await self._decompose_task(task)
            
            # Delegate to specialists
            results = []
            for subtask in subtasks:
                specialist = await self._find_best_agent(subtask)
                if specialist:
                    result = await self._delegate_task(specialist, subtask)
                    results.append(result)
            
            # Combine results
            return await self._combine_results(results)
        else:
            # Handle simple tasks directly
            return await self._handle_simple_task(task)
    
    async def _find_best_agent(self, task: Task) -> str:
        """Find the best agent for a specific task."""
        # Query monitoring server for available agents
        # Match task requirements with agent capabilities
        # Return agent ID of best match
        pass
    
    async def _delegate_task(self, agent_id: str, task: Task) -> dict:
        """Delegate task to another agent."""
        # Send task to agent via monitoring server
        # Monitor progress
        # Return result when complete
        pass
```

### 2. Pipeline Pattern

```python
class PipelineAgent(MonitoringAgent):
    """Processes tasks through a sequential pipeline."""
    
    def __init__(self, pipeline_stages: List[str], **kwargs):
        self.pipeline_stages = pipeline_stages
        super().__init__(**kwargs)
    
    async def _execute_task_internal(self, task: Task, model_id: str) -> dict:
        result = {"input": task.parameters}
        
        for stage in self.pipeline_stages:
            await self.send_custom_metric("pipeline_stage", stage)
            result = await self._execute_stage(stage, result, model_id)
            
            # Report progress
            progress = (self.pipeline_stages.index(stage) + 1) / len(self.pipeline_stages)
            await self.send_custom_metric("pipeline_progress", progress)
        
        return result
    
    async def _execute_stage(self, stage: str, data: dict, model_id: str) -> dict:
        """Execute a specific pipeline stage."""
        if stage == "validation":
            return await self._validate_input(data)
        elif stage == "processing":
            return await self._process_data(data)
        elif stage == "formatting":
            return await self._format_output(data)
        
        return data
```

### 3. Collaboration Pattern

```python
class CollaborativeAgent(MonitoringAgent):
    """Collaborates with other agents on shared tasks."""
    
    async def _execute_task_internal(self, task: Task, model_id: str) -> dict:
        # Check if this is a collaborative task
        if "collaboration_id" in task.parameters:
            return await self._handle_collaborative_task(task)
        else:
            return await self._handle_individual_task(task)
    
    async def _handle_collaborative_task(self, task: Task) -> dict:
        """Handle tasks requiring collaboration."""
        collab_id = task.parameters["collaboration_id"]
        
        # Join collaboration session
        await self._join_collaboration(collab_id)
        
        # Contribute to shared work
        contribution = await self._make_contribution(task)
        
        # Share with other agents
        await self._share_contribution(collab_id, contribution)
        
        # Wait for all contributions
        final_result = await self._wait_for_completion(collab_id)
        
        return final_result
```

## 🔧 Advanced Features

### Custom Memory Management

```python
class StatefulAgent(MonitoringAgent):
    """Agent with advanced memory management."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_memory = {}
        self.session_memory = {}
    
    async def on_start(self):
        """Load persistent memory on startup."""
        await super().on_start()
        await self._load_project_memory()
    
    async def on_stop(self):
        """Save memory before shutdown."""
        await self._save_project_memory()
        await super().on_stop()
    
    async def _execute_task_internal(self, task: Task, model_id: str) -> dict:
        # Access project context
        project_id = task.parameters.get("project_id")
        if project_id:
            context = self.project_memory.get(project_id, {})
            # Use context in task execution
        
        result = await self._process_with_context(task, context)
        
        # Update memory
        if project_id:
            self._update_project_memory(project_id, result)
        
        return result
```

### Error Handling and Recovery

```python
class ResilientAgent(MonitoringAgent):
    """Agent with advanced error handling."""
    
    async def _execute_task_internal(self, task: Task, model_id: str) -> dict:
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                result = await self._attempt_task_execution(task, model_id)
                
                # Validate result
                if await self._validate_result(result):
                    return result
                else:
                    raise ValueError("Result validation failed")
                    
            except Exception as e:
                retry_count += 1
                await self.report_issue(
                    f"Task execution failed (attempt {retry_count}): {str(e)}",
                    severity="warning" if retry_count < max_retries else "error"
                )
                
                if retry_count < max_retries:
                    # Exponential backoff
                    await asyncio.sleep(2 ** retry_count)
                    
                    # Try different approach or model
                    if retry_count == 2:
                        model_id = await self._get_fallback_model()
                else:
                    # Final failure
                    return {
                        "status": "failed",
                        "error": str(e),
                        "retry_count": retry_count
                    }
```

### Custom Metrics and Monitoring

```python
class InstrumentedAgent(MonitoringAgent):
    """Agent with comprehensive monitoring."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.metrics_collector = MetricsCollector()
    
    async def _execute_task_internal(self, task: Task, model_id: str) -> dict:
        # Start metrics collection
        with self.metrics_collector.timer("task_execution"):
            self.metrics_collector.increment("tasks_started")
            
            try:
                result = await self._core_task_logic(task, model_id)
                
                # Report success metrics
                self.metrics_collector.increment("tasks_completed")
                self.metrics_collector.histogram("task_complexity", task.complexity)
                
                # Send custom metrics to monitoring server
                await self.send_custom_metric("execution_efficiency", {
                    "task_type": str(task.type),
                    "complexity": task.complexity,
                    "execution_time": self.metrics_collector.get_last_duration(),
                    "model_used": model_id
                })
                
                return result
                
            except Exception as e:
                self.metrics_collector.increment("tasks_failed")
                raise
```

## 🧪 Testing Your Agents

### Unit Testing

```python
import pytest
from unittest.mock import AsyncMock, Mock

@pytest.mark.asyncio
async def test_agent_task_execution():
    """Test basic agent task execution."""
    
    # Create agent with mock dependencies
    agent = MyCustomAgent(
        config=test_config,
        monitoring_url="",  # Disable monitoring for tests
        api_key=""
    )
    agent.monitoring_enabled = False
    
    await agent.start()
    
    try:
        # Create test task
        task = Task(
            type="test_task",
            description="Test task execution",
            complexity=3
        )
        
        # Execute task
        result = await agent.execute_task(task)
        
        # Verify result
        assert result.status == "success"
        assert result.agent_id == agent.id
        assert "result" in result.result
        
    finally:
        await agent.stop()

@pytest.mark.asyncio 
async def test_agent_error_handling():
    """Test agent error handling."""
    
    agent = MyCustomAgent()
    
    # Create problematic task
    bad_task = Task(type="invalid_type", description="This should fail")
    
    result = await agent.execute_task(bad_task)
    
    # Should handle error gracefully
    assert result.status == "error"
    assert "error" in result.error
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_agent_coordination():
    """Test coordination between multiple agents."""
    
    # Create multiple agents
    coordinator = CoordinatorAgent()
    worker1 = WorkerAgent()
    worker2 = WorkerAgent()
    
    await coordinator.start()
    await worker1.start()
    await worker2.start()
    
    try:
        # Create complex task requiring coordination
        complex_task = Task(
            type="complex_project",
            description="Multi-agent project",
            complexity=10,
            parameters={"requires_coordination": True}
        )
        
        # Execute through coordinator
        result = await coordinator.execute_task(complex_task)
        
        # Verify coordination occurred
        assert result.status == "success"
        assert len(worker1.task_history) > 0
        assert len(worker2.task_history) > 0
        
    finally:
        await coordinator.stop()
        await worker1.stop()
        await worker2.stop()
```

## 📚 Best Practices

### 1. Configuration Management

```python
# Use environment-specific configs
class ProductionBackendAgent(BackendAgent):
    def __init__(self):
        config = AgentConfig(
            name="Production Backend Agent",
            max_concurrent_tasks=10,
            health_check_interval=30,
            model_preferences={
                "primary": "claude-3-opus",  # More powerful for production
                "fallback": "claude-3-sonnet"
            }
        )
        super().__init__(config=config)

class DevelopmentBackendAgent(BackendAgent):
    def __init__(self):
        config = AgentConfig(
            name="Development Backend Agent", 
            max_concurrent_tasks=3,
            health_check_interval=60,
            model_preferences={
                "primary": "claude-3-haiku"  # Faster/cheaper for development
            }
        )
        super().__init__(config=config)
```

### 2. Logging and Debugging

```python
import logging

class DebuggableAgent(MonitoringAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Setup detailed logging
        self.debug_logger = logging.getLogger(f"debug.{self.id}")
        self.debug_logger.setLevel(logging.DEBUG)
        
        handler = logging.FileHandler(f"agent_{self.id}_debug.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.debug_logger.addHandler(handler)
    
    async def _execute_task_internal(self, task: Task, model_id: str) -> dict:
        self.debug_logger.debug(f"Starting task execution: {task.id}")
        self.debug_logger.debug(f"Task details: {task.dict()}")
        
        try:
            result = await self._core_execution(task, model_id)
            self.debug_logger.debug(f"Task completed successfully: {result}")
            return result
        except Exception as e:
            self.debug_logger.error(f"Task execution failed: {e}", exc_info=True)
            raise
```

### 3. Performance Optimization

```python
class OptimizedAgent(MonitoringAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Connection pooling for external APIs
        self.http_session = None
        
        # Caching for expensive operations
        self.result_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def on_start(self):
        await super().on_start()
        
        # Initialize connection pool
        self.http_session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=10)
        )
    
    async def on_stop(self):
        if self.http_session:
            await self.http_session.close()
        
        await super().on_stop()
    
    async def _execute_task_internal(self, task: Task, model_id: str) -> dict:
        # Check cache first
        cache_key = self._generate_cache_key(task)
        if cache_key in self.result_cache:
            cached_result, timestamp = self.result_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                await self.send_custom_metric("cache_hit", True)
                return cached_result
        
        # Execute task
        result = await self._core_execution(task, model_id)
        
        # Cache result
        self.result_cache[cache_key] = (result, time.time())
        
        return result
```

## 🚀 Deployment

### Production Deployment

```python
# production_agent.py
import os
from my_agent import MyCustomAgent

async def main():
    # Production configuration
    config = AgentConfig(
        name=os.getenv("AGENT_NAME", "Production Agent"),
        max_concurrent_tasks=int(os.getenv("MAX_TASKS", "5")),
        health_check_interval=float(os.getenv("HEALTH_CHECK_INTERVAL", "30")),
        model_preferences={
            "primary": os.getenv("PRIMARY_MODEL", "claude-3-sonnet"),
            "fallback": os.getenv("FALLBACK_MODEL", "claude-3-haiku")
        }
    )
    
    agent = MyCustomAgent(
        config=config,
        monitoring_url=os.getenv("MONITORING_URL"),
        api_key=os.getenv("MONITORING_API_KEY")
    )
    
    try:
        await agent.start()
        
        # Keep running until interrupted
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        print("Shutting down agent...")
    finally:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
COPY production_agent.py .

ENV PYTHONPATH=/app

CMD ["python", "production_agent.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  my-agent:
    build: .
    environment:
      - MONITORING_URL=http://monitoring-server:6795
      - MONITORING_API_KEY=${MONITORING_API_KEY}
      - AGENT_NAME=Production My Agent
      - MAX_TASKS=5
    depends_on:
      - monitoring-server
    restart: unless-stopped
```

## 📖 Next Steps

1. **Study Examples**: Review agents in `examples/` directory
2. **Run Tests**: Use the coordination test suite to validate your agents
3. **Monitor Performance**: Use Control Center to optimize agent behavior
4. **Scale Up**: Deploy multiple instances for production workloads
5. **Contribute**: Share your agent patterns with the community

Happy agent building! 🤖✨