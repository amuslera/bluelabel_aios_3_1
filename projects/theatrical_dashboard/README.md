# Theatrical Monitoring System

Real-time visualization and monitoring of AIOSv3 multi-agent orchestration with step-by-step theatrical presentation.

## Components

- **theatrical_orchestrator.py**: Core orchestration logic with theatrical delays and visual feedback
- **theatrical_monitoring_dashboard.py**: Rich TUI dashboard for real-time monitoring
- **dashboards/**: Alternative dashboard implementations and backups

## Usage

Use the main launcher script from the project root:

```bash
python launch_theatrical_demo.py
```

Or run components directly:

```bash
# Console mode only
python -m theatrical_monitoring.theatrical_orchestrator

# Dashboard mode only  
python -m theatrical_monitoring.theatrical_monitoring_dashboard
```

## Features

- 🎭 Theatrical step-by-step agent interactions
- 📊 Real-time status monitoring for all agents
- 📋 Live activity logs with rolling history
- 📈 Performance metrics tracking
- 🎨 Color-coded event visualization
- ⏱️ Configurable timing and verbosity

## Dashboard Versions

The `dashboards/` directory contains:
- **theatrical_monitoring_dashboard_backup.py**: Backup of working dashboard
- **theatrical_monitoring_dashboard_simple_working.py**: Simplified version for testing