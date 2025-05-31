# Architecture Decisions & Conventions

## Core Architectural Decisions

### 1. Event-Driven Architecture

**Decision**: Use event-driven architecture for agent communication

**Rationale**:
- Loose coupling between agents
- Asynchronous processing capabilities
- Easy to add new agents without modifying existing ones
- Natural fit for workflow orchestration
- Supports replay and debugging

**Implementation**:
- RabbitMQ or Apache Kafka for message broker
- Event sourcing for critical workflows
- CQRS pattern where appropriate

### 2. Microservices with Shared Libraries

**Decision**: Each agent is a microservice, but share common libraries

**Rationale**:
- Independent deployment and scaling
- Technology flexibility per agent
- Shared code for common functionality
- Easier testing and maintenance

**Implementation**:
- Python package for shared agent functionality
- Separate repositories or monorepo with clear boundaries
- Semantic versioning for shared libraries

### 3. API-First Design

**Decision**: All functionality exposed via well-defined APIs

**Rationale**:
- Clear contracts between components
- Enables multiple UI/client types
- Easier testing and mocking
- Better documentation

**Implementation**:
- OpenAPI 3.0 specifications
- FastAPI for Python services
- Automated API documentation
- Contract testing between services

### 4. Container-Native from Day One

**Decision**: Design for containers and Kubernetes

**Rationale**:
- Consistent deployment across environments
- Built-in scaling and orchestration
- Easy local development
- Cloud-agnostic approach

**Implementation**:
- Multi-stage Dockerfiles
- Kubernetes-native features (ConfigMaps, Secrets)
- Health checks and readiness probes
- Resource limits and requests

### 5. Observability as a First-Class Concern

**Decision**: Built-in monitoring, logging, and tracing

**Rationale**:
- Critical for debugging distributed systems
- Performance optimization
- SLA monitoring
- Proactive issue detection

**Implementation**:
- OpenTelemetry for distributed tracing
- Structured logging (JSON)
- Prometheus metrics
- Correlation IDs across services

## Technical Conventions

### Code Style

#### Python
```python
# Use type hints everywhere
from typing import List, Dict, Optional

class Agent:
    def process_task(
        self,
        task_id: str,
        parameters: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process a task with given parameters.
        
        Args:
            task_id: Unique identifier for the task
            parameters: Task-specific parameters
            timeout: Optional timeout in seconds
            
        Returns:
            Dict containing the task result
            
        Raises:
            TaskTimeoutError: If task exceeds timeout
            InvalidParametersError: If parameters are invalid
        """
        pass
```

#### TypeScript
```typescript
// Use interfaces for all data structures
interface TaskRequest {
  taskId: string;
  agentId: string;
  parameters: Record<string, unknown>;
  timeout?: number;
}

// Use async/await over promises
async function processTask(
  request: TaskRequest
): Promise<TaskResponse> {
  // Implementation
}

// Use proper error handling
try {
  const result = await processTask(request);
} catch (error) {
  if (error instanceof TaskTimeoutError) {
    // Handle timeout
  }
  throw error;
}
```

### API Design

#### RESTful Principles
```yaml
# Resource-based URLs
GET    /api/v1/agents                 # List agents
POST   /api/v1/agents                 # Create agent
GET    /api/v1/agents/{id}           # Get agent
PUT    /api/v1/agents/{id}           # Update agent
DELETE /api/v1/agents/{id}           # Delete agent

# Sub-resources
GET    /api/v1/agents/{id}/tasks     # Get agent's tasks
POST   /api/v1/agents/{id}/tasks     # Assign task to agent

# Actions as POST
POST   /api/v1/agents/{id}/actions/restart
POST   /api/v1/workflows/{id}/actions/execute
```

#### Response Format
```json
{
  "data": {
    "id": "agent-123",
    "type": "backend_agent",
    "attributes": {
      "name": "Backend Developer",
      "status": "active"
    }
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0"
  }
}
```

#### Error Format
```json
{
  "error": {
    "code": "AGENT_NOT_FOUND",
    "message": "Agent with ID 'agent-123' not found",
    "details": {
      "searched_id": "agent-123",
      "search_time": "2024-01-01T00:00:00Z"
    }
  },
  "meta": {
    "request_id": "req-456",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### Database Conventions

#### Schema Design
```sql
-- Use UUID for primary keys
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,  -- Soft deletes
    
    -- Actual columns
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    config JSONB NOT NULL DEFAULT '{}'
);

-- Always include audit fields
-- Always use soft deletes
-- Use JSONB for flexible data
```

#### Naming Conventions
- Tables: plural, snake_case (e.g., `agent_tasks`)
- Columns: snake_case (e.g., `created_at`)
- Indexes: `idx_table_column` (e.g., `idx_agents_type`)
- Foreign keys: `fk_table_referenced` (e.g., `fk_tasks_agents`)

### Message Queue Conventions

#### Event Naming
```python
# Domain.Entity.Action
"agents.backend.task_completed"
"agents.frontend.code_generated"
"workflows.deployment.started"
"system.health.check_failed"
```

#### Message Format
```json
{
  "id": "msg-123",
  "type": "agents.backend.task_completed",
  "timestamp": "2024-01-01T00:00:00Z",
  "source": "backend-agent-1",
  "data": {
    "task_id": "task-456",
    "result": "success",
    "output": {}
  },
  "metadata": {
    "correlation_id": "corr-789",
    "causation_id": "msg-122",
    "user_id": "user-1"
  }
}
```

### Configuration Management

#### Environment Variables
```bash
# Naming convention: PREFIX_CATEGORY_NAME
AIOS_DATABASE_URL=postgresql://localhost/aios
AIOS_REDIS_URL=redis://localhost:6379
AIOS_LOG_LEVEL=info
AIOS_AGENT_TIMEOUT=300

# Secrets always from environment
AIOS_ANTHROPIC_API_KEY=sk-...
AIOS_OPENAI_API_KEY=sk-...
```

#### Configuration Files
```yaml
# config/base.yaml - Shared configuration
app:
  name: "AIOSv3"
  version: "1.0.0"
  
# config/production.yaml - Environment specific
app:
  debug: false
  log_level: "info"
  
# Never commit secrets to configuration files
# Use ${ENV_VAR} syntax for environment substitution
database:
  url: ${AIOS_DATABASE_URL}
```

### Testing Conventions

#### Test Organization
```
tests/
├── unit/              # Fast, isolated tests
├── integration/       # Test component interactions
├── e2e/              # Full system tests
└── fixtures/         # Shared test data
```

#### Test Naming
```python
def test_should_process_task_successfully():
    """Test names describe expected behavior"""
    pass

def test_should_raise_error_when_task_timeout():
    """Include failure scenarios"""
    pass

class TestBackendAgent:
    """Group related tests in classes"""
    
    def test_initialization(self):
        pass
        
    def test_task_processing(self):
        pass
```

### Documentation Standards

#### Code Documentation
```python
"""
Module: agents.backend

This module implements the backend developer agent responsible
for generating and managing backend code.

Classes:
    BackendAgent: Main agent implementation
    
Functions:
    create_backend_agent: Factory function for agent creation
"""
```

#### API Documentation
```python
@app.post(
    "/api/v1/agents",
    response_model=AgentResponse,
    status_code=201,
    summary="Create a new agent",
    description="Creates a new agent with the specified configuration",
    responses={
        201: {"description": "Agent created successfully"},
        400: {"description": "Invalid agent configuration"},
        409: {"description": "Agent already exists"}
    }
)
async def create_agent(request: CreateAgentRequest) -> AgentResponse:
    pass
```

### Security Conventions

#### Authentication & Authorization
```python
# Use OAuth2/JWT for API authentication
# Implement RBAC for authorization
# Always validate input
# Never log sensitive data

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Validate token and return user
    pass

@app.get("/api/v1/agents")
async def list_agents(
    current_user: User = Depends(get_current_user)
):
    # Check user permissions
    if not current_user.has_permission("agents:read"):
        raise HTTPException(status_code=403)
```

#### Data Protection
```python
# Encrypt sensitive data at rest
# Use TLS for all communications
# Implement field-level encryption for PII
# Regular security audits

class SecureAgent:
    def store_credentials(self, credentials: Dict[str, str]):
        encrypted = self.encryption_service.encrypt(credentials)
        self.storage.save(encrypted)
```

### Performance Guidelines

1. **Async Everything**: Use async/await for I/O operations
2. **Connection Pooling**: Reuse database and HTTP connections
3. **Caching Strategy**: Cache at multiple levels (Redis, in-memory)
4. **Batch Operations**: Process multiple items together
5. **Rate Limiting**: Protect against abuse
6. **Circuit Breakers**: Fail fast and recover gracefully

### Deployment Conventions

#### Git Workflow
```bash
main          # Production-ready code
develop       # Integration branch
feature/*     # Feature branches
hotfix/*      # Emergency fixes
release/*     # Release preparation
```

#### Version Control
- Semantic versioning (MAJOR.MINOR.PATCH)
- Tag releases in git
- Keep changelog (CHANGELOG.md)
- Conventional commits

#### CI/CD Pipeline
```yaml
stages:
  - lint        # Code quality checks
  - test        # Run all tests
  - build       # Build containers
  - security    # Security scanning
  - deploy      # Deploy to environment
```

## Decision Records

### ADR-001: Use Python for Core Platform
**Status**: Accepted  
**Context**: Need a language for agent implementation  
**Decision**: Use Python 3.11+  
**Consequences**: Good AI/ML ecosystem, may need optimization for performance

### ADR-002: FastAPI for API Layer
**Status**: Accepted  
**Context**: Need modern, fast API framework  
**Decision**: Use FastAPI over Flask/Django  
**Consequences**: Modern async support, automatic OpenAPI docs, less mature ecosystem

### ADR-003: Kubernetes for Orchestration
**Status**: Accepted  
**Context**: Need container orchestration  
**Decision**: Use Kubernetes over Docker Swarm  
**Consequences**: Industry standard, complex but powerful, good cloud support

### ADR-004: Event-Driven Architecture
**Status**: Accepted  
**Context**: Need agent communication mechanism  
**Decision**: Use event-driven over direct RPC  
**Consequences**: Loose coupling, eventual consistency, more complex debugging

## Living Document

This document is a living guide that should be updated as the project evolves. All team members are encouraged to propose changes through pull requests.