# API Reference

Complete API reference for the AIOSv3 monitoring server and agent coordination system.

## 🔗 Base URL

Default monitoring server URL: `http://localhost:6795`

## 🔐 Authentication

All API endpoints require authentication via API key.

### API Key Authentication

Include the API key in requests using one of these methods:

**Header (Recommended):**
```bash
curl -H "X-API-Key: your_api_key_here" http://localhost:6795/api/agents
```

**Query Parameter:**
```bash
curl "http://localhost:6795/api/agents?api_key=your_api_key_here"
```

### Getting an API Key

The master API key is displayed when starting the monitoring server:
```
🚀 Enhanced Monitoring Server starting on port 6795
🔑 Master API Key: aios_abc123xyz...
```

## 📊 Health and Status

### GET /api/health

Public health check endpoint (no authentication required).

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0", 
  "connections": 5,
  "uptime": 1234567.89,
  "features": ["authentication", "rate_limiting", "websockets"]
}
```

## 🤖 Agent Management

### POST /api/agents/register

Register a new agent with the monitoring server.

**Request Body:**
```json
{
  "agent_id": "agent_123",
  "name": "Backend Developer Agent",
  "agent_type": "specialist",
  "capabilities": ["api_development", "database_design"],
  "endpoint": "agent://agent_123",
  "status": "active",
  "metadata": {
    "version": "1.0.0",
    "started_at": "2024-12-08T10:30:00Z"
  }
}
```

**Response (Success):**
```json
{
  "success": true,
  "agent_id": "agent_123",
  "message": "Agent registered successfully",
  "registration": {
    "agent_id": "agent_123",
    "name": "Backend Developer Agent",
    "agent_type": "specialist",
    "capabilities": ["api_development", "database_design"],
    "endpoint": "agent://agent_123",
    "status": "active",
    "registered_at": "2024-12-08T10:30:00Z",
    "last_heartbeat": "2024-12-08T10:30:00Z",
    "metadata": {
      "version": "1.0.0",
      "started_at": "2024-12-08T10:30:00Z"
    }
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Missing required field: name",
  "message": "Agent registration failed"
}
```

### GET /api/agents

Get list of all registered agents.

**Query Parameters:**
- `status` (optional): Filter by agent status (`active`, `idle`, `busy`, `error`, `offline`)
- `type` (optional): Filter by agent type
- `capability` (optional): Filter by specific capability

**Examples:**
```bash
# Get all agents
curl -H "X-API-Key: your_key" http://localhost:6795/api/agents

# Get only active agents
curl -H "X-API-Key: your_key" http://localhost:6795/api/agents?status=active

# Get agents with specific capability
curl -H "X-API-Key: your_key" http://localhost:6795/api/agents?capability=api_development
```

**Response:**
```json
{
  "agents": [
    {
      "agent_id": "agent_123",
      "name": "Backend Developer Agent",
      "agent_type": "specialist",
      "capabilities": ["api_development", "database_design"],
      "endpoint": "agent://agent_123",
      "status": "active",
      "registered_at": "2024-12-08T10:30:00Z",
      "last_heartbeat": "2024-12-08T10:35:00Z",
      "metadata": {
        "current_tasks": 2,
        "tasks_completed": 15,
        "success_rate": 0.95
      }
    }
  ],
  "count": 1,
  "total_registered": 5
}
```

### GET /api/agents/{agent_id}

Get detailed information about a specific agent.

**Response:**
```json
{
  "success": true,
  "agent": {
    "agent_id": "agent_123",
    "name": "Backend Developer Agent",
    "agent_type": "specialist",
    "capabilities": ["api_development", "database_design"],
    "endpoint": "agent://agent_123",
    "status": "active",
    "registered_at": "2024-12-08T10:30:00Z",
    "last_heartbeat": "2024-12-08T10:35:00Z",
    "metadata": {
      "current_tasks": 2,
      "tasks_completed": 15,
      "success_rate": 0.95,
      "health_score": 0.98,
      "uptime_seconds": 3600
    }
  }
}
```

### POST /api/agents/{agent_id}/heartbeat

Send agent heartbeat with status update.

**Request Body:**
```json
{
  "status": "active",
  "metadata": {
    "current_tasks": 3,
    "tasks_completed": 20,
    "uptime_seconds": 3900,
    "memory_usage": 256,
    "health_score": 0.95
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Heartbeat received",
  "server_time": "2024-12-08T10:40:00Z"
}
```

### DELETE /api/agents/{agent_id}

Unregister an agent.

**Response:**
```json
{
  "success": true,
  "message": "Agent agent_123 unregistered successfully"
}
```

## 📋 Activity Management

### POST /api/activities

Store a new activity/event.

**Request Body:**
```json
{
  "agent_id": "agent_123",
  "agent_name": "Backend Developer Agent",
  "type": "task_completion",
  "status": "success",
  "message": "API endpoint development completed",
  "metadata": {
    "task_id": "task_456",
    "execution_time": 45.2,
    "complexity": 7,
    "model_used": "claude-3-sonnet"
  }
}
```

**Response:**
```json
{
  "status": "stored",
  "activity_id": "abc123def456"
}
```

### GET /api/activities

Get stored activities with filtering.

**Query Parameters:**
- `limit` (optional, default: 100): Maximum number of activities to return
- `since` (optional): ISO timestamp to filter activities after this time
- `agent_id` (optional): Filter activities by specific agent
- `type` (optional): Filter by activity type

**Examples:**
```bash
# Get recent activities
curl -H "X-API-Key: your_key" http://localhost:6795/api/activities?limit=50

# Get activities since timestamp
curl -H "X-API-Key: your_key" "http://localhost:6795/api/activities?since=2024-12-08T10:00:00Z"

# Get activities for specific agent
curl -H "X-API-Key: your_key" http://localhost:6795/api/activities?agent_id=agent_123
```

**Response:**
```json
{
  "activities": [
    {
      "id": "abc123def456",
      "agent_id": "agent_123",
      "agent_name": "Backend Developer Agent",
      "type": "task_completion",
      "status": "success",
      "message": "API endpoint development completed",
      "metadata": {
        "task_id": "task_456",
        "execution_time": 45.2,
        "complexity": 7,
        "model_used": "claude-3-sonnet"
      },
      "stored_at": "2024-12-08T10:35:00Z",
      "timestamp": "2024-12-08T10:34:55Z"
    }
  ],
  "count": 1,
  "total": 150
}
```

## 🔧 Admin Endpoints

### POST /api/admin/api-keys

Create a new API key (requires master API key).

**Request Body:**
```json
{
  "name": "Production Key",
  "permissions": ["read", "write"]
}
```

**Response:**
```json
{
  "success": true,
  "api_key": "aios_new_key_here",
  "name": "Production Key",
  "created_at": "2024-12-08T10:45:00Z"
}
```

### GET /api/admin/api-keys

List all API keys (requires master API key).

**Response:**
```json
{
  "api_keys": [
    {
      "name": "master",
      "created": "2024-12-08T10:00:00Z",
      "last_used": "2024-12-08T10:45:00Z",
      "usage_count": 1523
    },
    {
      "name": "Production Key",
      "created": "2024-12-08T10:45:00Z",
      "last_used": null,
      "usage_count": 0
    }
  ],
  "count": 2
}
```

## 🔌 WebSocket API

### Connection

Connect to WebSocket endpoint for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:6795/ws?api_key=your_api_key');

ws.onopen = function() {
    console.log('Connected to monitoring server');
    
    // Subscribe to all activities
    ws.send(JSON.stringify({
        type: 'subscribe',
        filters: {}
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

### Message Types

#### Subscribe to Activities
```json
{
  "type": "subscribe",
  "filters": {
    "agent_id": "agent_123",
    "activity_type": "task_completion"
  }
}
```

#### Ping/Pong
```json
{
  "type": "ping"
}
```

**Response:**
```json
{
  "type": "pong",
  "timestamp": "2024-12-08T10:45:00Z"
}
```

#### Activity Updates
```json
{
  "type": "activity",
  "activity": {
    "id": "abc123",
    "agent_id": "agent_123",
    "type": "task_completion",
    "message": "Task completed successfully"
  },
  "timestamp": "2024-12-08T10:45:00Z"
}
```

#### Agent Registration
```json
{
  "type": "agent_registered",
  "agent": {
    "agent_id": "new_agent_456",
    "name": "New Agent",
    "status": "active"
  }
}
```

## 📊 Data Models

### Agent Registration
```typescript
interface AgentRegistration {
  agent_id: string;
  name: string;
  agent_type: string;
  capabilities: string[];
  endpoint: string;
  status: 'active' | 'idle' | 'busy' | 'error' | 'offline';
  registered_at: string; // ISO timestamp
  last_heartbeat: string; // ISO timestamp  
  metadata: Record<string, any>;
}
```

### Activity
```typescript
interface Activity {
  id: string;
  agent_id: string;
  agent_name: string;
  type: string;
  status: 'success' | 'error' | 'warning' | 'info';
  message: string;
  metadata: Record<string, any>;
  stored_at: string; // ISO timestamp
  timestamp: string; // ISO timestamp
}
```

### Task
```typescript
interface Task {
  id: string;
  type: string;
  description: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  complexity: number; // 1-10
  parameters: Record<string, any>;
  created_at: string; // ISO timestamp
  assigned_agent_id?: string;
}
```

## 🚨 Error Responses

### Standard Error Format
```json
{
  "success": false,
  "error": "Error description",
  "message": "User-friendly error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "validation error details"
  }
}
```

### Common HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid/missing API key |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

### Rate Limiting

API requests are rate limited (default: 100 requests/minute per API key).

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1638360000
```

**Rate Limit Exceeded Response:**
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests, please try again later",
  "retry_after": 60
}
```

## 🔍 Monitoring and Metrics

### Built-in Metrics

The API automatically tracks:
- Request counts by endpoint
- Response times
- Error rates
- Agent activity rates
- WebSocket connections

### Custom Metrics

Agents can send custom metrics via activities:

```json
{
  "agent_id": "agent_123",
  "type": "custom_metric",
  "message": "Memory usage update",
  "metadata": {
    "metric_name": "memory_usage_mb",
    "metric_value": 512,
    "timestamp": "2024-12-08T10:45:00Z"
  }
}
```

## 🛠️ SDK Examples

### Python SDK Usage

```python
import aiohttp
import asyncio

class AIOSClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key}
    
    async def register_agent(self, agent_data: dict):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/agents/register",
                json=agent_data,
                headers=self.headers
            ) as response:
                return await response.json()
    
    async def send_heartbeat(self, agent_id: str, status_data: dict):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/agents/{agent_id}/heartbeat",
                json=status_data,
                headers=self.headers
            ) as response:
                return await response.json()
    
    async def get_agents(self, **filters):
        params = {k: v for k, v in filters.items() if v is not None}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/agents",
                params=params,
                headers=self.headers
            ) as response:
                return await response.json()

# Usage
client = AIOSClient("http://localhost:6795", "your_api_key")

# Register agent
agent_data = {
    "agent_id": "my_agent",
    "name": "My Custom Agent",
    "agent_type": "custom",
    "capabilities": ["general"],
    "endpoint": "agent://my_agent"
}

registration_result = await client.register_agent(agent_data)
```

### JavaScript SDK Usage

```javascript
class AIOSClient {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }
    
    async registerAgent(agentData) {
        const response = await fetch(`${this.baseUrl}/api/agents/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': this.apiKey
            },
            body: JSON.stringify(agentData)
        });
        return await response.json();
    }
    
    async getAgents(filters = {}) {
        const params = new URLSearchParams(filters);
        const response = await fetch(`${this.baseUrl}/api/agents?${params}`, {
            headers: {
                'X-API-Key': this.apiKey
            }
        });
        return await response.json();
    }
    
    connectWebSocket() {
        const ws = new WebSocket(`ws://localhost:6795/ws?api_key=${this.apiKey}`);
        
        ws.onopen = () => {
            ws.send(JSON.stringify({
                type: 'subscribe',
                filters: {}
            }));
        };
        
        return ws;
    }
}

// Usage
const client = new AIOSClient('http://localhost:6795', 'your_api_key');
const agents = await client.getAgents({ status: 'active' });
const ws = client.connectWebSocket();
```

## 🔗 Integration Examples

### Prometheus Metrics Export

```python
# Custom metrics exporter
import time
from prometheus_client import Counter, Histogram, start_http_server

# Metrics
AGENT_REGISTRATIONS = Counter('aios_agent_registrations_total', 'Total agent registrations')
TASK_DURATION = Histogram('aios_task_duration_seconds', 'Task execution duration')
ACTIVE_AGENTS = Gauge('aios_active_agents', 'Number of active agents')

async def export_metrics():
    """Export metrics for Prometheus."""
    client = AIOSClient("http://localhost:6795", api_key)
    
    while True:
        agents = await client.get_agents(status='active')
        ACTIVE_AGENTS.set(agents['count'])
        
        await asyncio.sleep(30)

# Start Prometheus metrics server
start_http_server(8000)
asyncio.create_task(export_metrics())
```

### Grafana Dashboard

Use these queries in Grafana:
```promql
# Active agents over time
aios_active_agents

# Task execution rate
rate(aios_task_completions_total[5m])

# Average task duration
rate(aios_task_duration_seconds_sum[5m]) / rate(aios_task_duration_seconds_count[5m])
```

This API reference provides everything needed to integrate with the AIOSv3 platform programmatically. The RESTful design and WebSocket support enable both real-time monitoring and automated agent management.