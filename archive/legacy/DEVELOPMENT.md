# AIOSv3 Development Guide

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.12+
- Git

### Initial Setup
```bash
# 1. Clone and enter the repository
git clone <repository-url>
cd bluelabel-AIOSv3

# 2. Run the development setup script
./scripts/dev-setup.sh

# 3. The script will:
#    - Check prerequisites
#    - Create necessary directories
#    - Set up configuration files
#    - Build and start all services
#    - Display access URLs
```

### Development Environment
After running the setup script, you'll have access to:

| Service | URL | Credentials |
|---------|-----|-------------|
| **API Documentation** | http://localhost:8000/docs | - |
| **RabbitMQ Management** | http://localhost:15672 | aiosv3 / dev_password |
| **MinIO Console** | http://localhost:9001 | aiosv3 / dev_password_123 |
| **Prometheus** | http://localhost:9090 | - |
| **Grafana** | http://localhost:3000 | admin / dev_password |
| **Qdrant** | http://localhost:6333 | - |

## 🛠️ Development Workflow

### Daily Development
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs (all services)
docker-compose -f docker-compose.dev.yml logs -f

# View logs (specific service)
docker-compose -f docker-compose.dev.yml logs -f app

# Enter the development container
docker-compose -f docker-compose.dev.yml exec app bash

# Stop environment
docker-compose -f docker-compose.dev.yml down
```

### Code Development
```bash
# Inside the container or with local Python environment

# Install pre-commit hooks (first time only)
pre-commit install

# Run tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run linting
ruff check .

# Run formatting
black .
isort .

# Run type checking
mypy .

# Run all quality checks
pre-commit run --all-files
```

### Working with Services

#### RabbitMQ
```python
# Test message queue connection
from core.messaging.queue import MessageQueue

queue = MessageQueue()
await queue.connect()
await queue.publish("test.queue", {"message": "Hello World"})
```

#### MinIO Object Storage
```python
# Test object storage
from core.storage.object_store import ObjectStorage

storage = ObjectStorage()
await storage.upload_file("test-bucket", "test.txt", b"Hello World")
```

#### Qdrant Vector Database
```bash
# Test Qdrant connection
curl http://localhost:6333/collections
```

## 🧪 Testing

### Test Structure
```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for component interactions
├── e2e/           # End-to-end tests for full workflows
├── fixtures/      # Test data and mock objects
└── conftest.py    # Pytest configuration
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test types
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term

# Run tests matching pattern
pytest -k "test_agent"

# Run tests with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### Writing Tests
```python
# Example unit test
import pytest
from unittest.mock import Mock

from agents.base.agent import Agent, AgentConfig


class TestAgent:
    def test_should_create_agent_with_valid_config(self):
        # Arrange
        config = AgentConfig(
            name="Test Agent",
            capabilities=["coding"],
            model_preferences={"primary": "claude-3-sonnet"}
        )
        
        # Act
        agent = Agent(config)
        
        # Assert
        assert agent.name == "Test Agent"
        assert agent.capabilities == ["coding"]

    @pytest.mark.asyncio
    async def test_should_execute_task_successfully(self):
        # Arrange
        agent = Agent(valid_config)
        task = Task(type="test", description="Test task")
        
        # Act
        result = await agent.execute_task(task)
        
        # Assert
        assert result.status == "success"
```

## 🔧 Debugging

### Debugging in Container
```bash
# Enter container with debugging tools
docker-compose -f docker-compose.dev.yml exec app bash

# Start Python with debugger
python -m pdb script.py

# Use IPython for interactive debugging
ipython
```

### VS Code Debugging
1. Install the Python extension
2. Use the provided `.vscode/launch.json` configuration
3. Set breakpoints and start debugging

### Log Debugging
```python
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Use structured logging
logger.info("Processing task", extra={
    "task_id": task.id,
    "agent_id": agent.id,
    "action": "start_processing"
})
```

## 📦 Dependency Management

### Adding New Dependencies
```bash
# Add runtime dependency
echo "new-package>=1.0.0" >> requirements.txt

# Add development dependency  
echo "new-dev-package>=1.0.0" >> requirements-dev.txt

# Update pyproject.toml if needed
# Then rebuild containers
docker-compose -f docker-compose.dev.yml build
```

### Updating Dependencies
```bash
# Update all dependencies
pip-compile --upgrade requirements.in
pip-compile --upgrade requirements-dev.in

# Update specific dependency
pip-compile --upgrade-package package-name requirements.in
```

## 🚨 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different ports in docker-compose.dev.yml
```

#### Container Won't Start
```bash
# Check container logs
docker-compose -f docker-compose.dev.yml logs service-name

# Rebuild containers
docker-compose -f docker-compose.dev.yml build --no-cache

# Remove volumes and restart
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

#### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Or run container as current user
docker-compose -f docker-compose.dev.yml exec --user $(id -u):$(id -g) app bash
```

#### Database Connection Issues
```bash
# Check if services are running
docker-compose -f docker-compose.dev.yml ps

# Test database connections
docker-compose -f docker-compose.dev.yml exec redis redis-cli ping
docker-compose -f docker-compose.dev.yml exec rabbitmq rabbitmq-diagnostics status
```

### Performance Issues
```bash
# Monitor resource usage
docker stats

# Check container logs for errors
docker-compose -f docker-compose.dev.yml logs --tail=100

# Profile Python code
python -m cProfile -o profile.out script.py
```

## 🔄 Git Workflow

### Branch Naming
- `feature/task-description` - New features
- `bugfix/issue-description` - Bug fixes  
- `hotfix/critical-fix` - Critical production fixes
- `refactor/component-name` - Code refactoring

### Commit Messages
```bash
# Format: type(scope): description
git commit -m "feat(agents): add message queue communication"
git commit -m "fix(api): resolve authentication error"
git commit -m "docs(readme): update installation instructions"
```

### Pull Request Process
1. Create feature branch from `main`
2. Make changes and commit
3. Run all quality checks: `pre-commit run --all-files`
4. Push branch and create pull request
5. Address review feedback
6. Squash and merge after approval

## 📊 Monitoring and Observability

### Application Metrics
- API response times and error rates
- Agent task completion rates
- Message queue throughput
- Database query performance

### Accessing Metrics
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **Application logs**: `docker-compose logs -f app`

### Adding Custom Metrics
```python
from prometheus_client import Counter, Histogram

# Define metrics
task_counter = Counter('agent_tasks_total', 'Total tasks processed', ['agent_type', 'status'])
task_duration = Histogram('agent_task_duration_seconds', 'Task processing time')

# Use metrics
task_counter.labels(agent_type='backend', status='success').inc()
with task_duration.time():
    # Process task
    pass
```

## 🎯 Performance Guidelines

### Response Time Targets
- API endpoints: < 200ms
- Agent communication: < 100ms  
- File operations: < 500ms
- Database queries: < 100ms

### Resource Limits
- Memory: < 512MB per agent
- CPU: < 50% under normal load
- Disk: < 1GB per workspace

### Optimization Tips
- Use async/await for I/O operations
- Implement connection pooling
- Cache frequently accessed data
- Monitor and profile regularly

---

For more detailed information, see:
- [Project Plan](PROJECT_PLAN.md)
- [Architecture Documentation](REFINED_ARCHITECTURE.md)
- [Development Standards](DEVELOPMENT_STANDARDS.md)