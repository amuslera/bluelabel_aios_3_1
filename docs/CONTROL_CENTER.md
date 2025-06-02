# Control Center User Guide

The AIOSv3 Control Center is your command dashboard for monitoring and managing the entire multi-agent system. It provides real-time visibility into agent performance, task execution, and system health.

## 🖥️ Starting the Control Center

```bash
# Make sure monitoring server is running first
python projects/monitoring/src/enhanced_monitoring_server.py

# In a new terminal, start Control Center
python projects/control_center/src/enhanced_control_center.py
```

## 📊 Dashboard Overview

The Control Center uses a terminal-based UI (TUI) with four main panels:

```
┌─────────────────────────────────────────────────────────────────┐
│ 🟢 Connected - Connected to monitoring server                  │
├─────────────────┬─────────────────┬─────────────────────────────┤
│ 🤖 Agent        │ 📊 Activity     │ 📋 Task Manager            │
│ Orchestra       │ Monitor         │                             │
│                 │                 │                             │
│ [Agent Cards]   │ [Live Activity  │ [Task Assignment]           │
│ [Agent Table]   │  Stream]        │ [Task Queue]                │
│                 │                 │                             │
├─────────────────┴─────────────────┼─────────────────────────────┤
│ 📈 System Health Dashboard        │                             │
│                                   │                             │
│ [Metrics] [Alerts] [Performance]  │                             │
└───────────────────────────────────┴─────────────────────────────┘
```

## 🤖 Agent Orchestra Panel

### Agent Views

**Card View** (default):
- Visual cards for each registered agent
- Real-time status indicators (🟢 Active, 🟡 Idle, 🔴 Error)
- Task progress bars
- Performance metrics (success rate, health score)
- Agent capabilities and current tasks

**Table View**:
- Compact tabular display
- Sortable columns
- Quick overview of all agents
- Status, role, current task, progress, success rate

### Agent Status Indicators

| Icon | Status | Description |
|------|--------|-------------|
| 🟢 | Active | Agent is processing tasks |
| 🟡 | Idle | Agent is ready for tasks |
| 🔵 | Busy | Agent at maximum task capacity |
| 🔴 | Error | Agent has encountered errors |
| ⚫ | Offline | Agent is not responding |

### Agent Actions

Use the action buttons to:
- **Launch Agent**: Start a new agent instance
- **Stop Agent**: Gracefully stop an agent
- **Restart Agent**: Restart an unresponsive agent
- **Agent Details**: View detailed agent information

## 📊 Activity Monitor Panel

Real-time activity stream showing:

### Activity Types
- **🚀 Startup**: Agent registration and initialization
- **📋 Task Start**: When agents begin task execution
- **✅ Task Complete**: Successful task completion
- **❌ Task Error**: Task execution failures
- **💓 Heartbeat**: Regular agent health checks
- **🔄 Status Update**: Agent state changes
- **📈 Custom Metric**: Agent-reported metrics
- **🏆 Milestone**: Significant achievements

### Activity Details
Each activity shows:
- Timestamp
- Agent name and ID
- Activity type and status
- Detailed message
- Metadata (execution time, complexity, etc.)

### Color Coding
- **Green**: Success events
- **Red**: Error events  
- **Yellow**: Warning events
- **Blue**: Informational events

## 📋 Task Manager Panel

### Task Assignment

**Manual Task Assignment**:
1. Enter task description in the input field
2. Click "Assign" to distribute to best available agent
3. Task appears in the task queue
4. Monitor progress in real-time

**Task Queue Display**:
- Task ID and description
- Assigned agent
- Current status (Pending, In Progress, Completed, Failed)
- Progress percentage

### Task Routing

The system automatically routes tasks based on:
- Agent capabilities
- Current load
- Task complexity
- Agent specialization

## 📈 System Health Dashboard

### Key Metrics

**Agent Metrics**:
- Active Agents: Currently running agents
- Tasks Today: Total tasks processed in 24h
- Success Rate: Overall task success percentage
- Avg Response: Average task execution time

**System Status**:
- 🟢 All Systems Operational
- 🟡 Performance Degraded
- 🔴 System Issues Detected

**Load Indicators**:
- Normal: < 5 active agents
- Medium: 5-10 active agents  
- High: > 10 active agents

### Recent Alerts

Common alerts include:
- Agent registration/unregistration
- Performance degradation warnings
- High error rate notifications
- System resource alerts
- Task queue backlog warnings

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `q` | Quit Control Center |
| `r` | Refresh all data |
| `c` | Connect/Reconnect to monitoring server |
| `t` | Focus on task assignment input |
| `Ctrl+L` | Clear activity log |

## 🔧 Configuration

### Connection Settings

Set environment variables before starting:
```bash
export MONITORING_WS_URL="ws://localhost:6795/ws"
export MONITORING_API_KEY="your_api_key_here"
```

### Display Options

The Control Center automatically:
- Reconnects if connection is lost
- Updates displays every 5 seconds
- Maintains connection health
- Handles server restarts gracefully

## 📡 WebSocket Integration

### Real-time Updates

The Control Center uses WebSocket connections for:
- Live agent status updates
- Real-time activity streaming
- Instant task completion notifications
- System health monitoring

### Connection Management

- **Auto-reconnection**: Automatically reconnects on connection loss
- **Exponential backoff**: Smart retry logic for failed connections
- **Connection indicators**: Clear status display in header
- **Graceful degradation**: Continues working with cached data

## 🚨 Troubleshooting

### Connection Issues

**"🔴 Disconnected" status:**
1. Verify monitoring server is running
2. Check WebSocket URL and API key
3. Test connection: `curl http://localhost:6795/api/health`
4. Restart Control Center

**Blank or static displays:**
1. Check network connectivity
2. Verify API key permissions
3. Look for error messages in terminal
4. Try refreshing with `r` key

### Performance Issues

**Slow updates:**
- Reduce number of active agents
- Check system resources
- Verify network latency
- Consider local deployment

**Memory usage:**
- Control Center maintains limited history
- Restart periodically for long sessions
- Monitor system resources

## 🎯 Best Practices

### Monitoring Workflow

1. **Start with Overview**: Check system health dashboard
2. **Review Agents**: Ensure all expected agents are active
3. **Monitor Activity**: Watch for errors or unusual patterns
4. **Manage Tasks**: Assign tasks and monitor progress
5. **Respond to Alerts**: Address issues as they arise

### Agent Management

- **Regular Health Checks**: Monitor agent health scores
- **Load Balancing**: Distribute tasks evenly
- **Performance Tuning**: Adjust based on metrics
- **Proactive Maintenance**: Restart agents showing degradation

### Task Management

- **Clear Descriptions**: Use descriptive task names
- **Monitor Progress**: Watch for stuck or slow tasks
- **Error Handling**: Investigate failed tasks
- **Capacity Planning**: Scale agents based on task volume

## 📊 Metrics and Analytics

### Performance Metrics

**Agent Performance**:
- Task completion times
- Success/failure rates
- Health scores over time
- Capability utilization

**System Performance**:
- Throughput (tasks per second)
- Latency (response times)
- Resource utilization
- Error rates

### Historical Data

The Control Center shows:
- Recent activity (last 100 events)
- Current session metrics
- Real-time performance data
- Trend indicators

For historical analysis, check:
- Monitoring server logs
- Database exports
- Performance test results

## 🔗 Integration

### API Integration

Access the same data programmatically:
```bash
# Get agent status
curl -H "X-API-Key: your_key" http://localhost:6795/api/agents

# Get recent activities  
curl -H "X-API-Key: your_key" http://localhost:6795/api/activities

# Submit new task
curl -X POST -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"agent_123","type":"task","message":"Process data"}' \
  http://localhost:6795/api/activities
```

### External Monitoring

Integrate with external tools:
- **Prometheus**: Metrics export endpoints
- **Grafana**: Dashboard integration
- **ELK Stack**: Log aggregation
- **Custom Tools**: JSON API access

The Control Center provides the human interface, while APIs enable automation and integration with your existing infrastructure.

## 🎉 Advanced Features

### Multi-Environment Support

Run multiple environments:
```bash
# Development environment
MONITORING_URL=http://dev-server:6795 python enhanced_control_center.py

# Production environment  
MONITORING_URL=http://prod-server:6795 python enhanced_control_center.py
```

### Custom Dashboards

Extend the Control Center:
- Add custom panels
- Integrate domain-specific metrics
- Create specialized views
- Build custom alerts

The modular architecture makes it easy to extend and customize for your specific needs.