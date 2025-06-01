#!/bin/bash
# Sprint 1.6 Launch Script - Control Center & Agent Intelligence

echo "🚀 Starting Sprint 1.6: Control Center & Agent Intelligence"
echo "=========================================================="

# Check if Redis is running (optional)
if command -v redis-cli &> /dev/null && redis-cli ping &> /dev/null; then
    echo "✓ Redis is running"
else
    echo "⚠️  Redis not running - starting with Docker Compose"
    if command -v docker-compose &> /dev/null; then
        docker-compose -f docker-compose.redis.yml up -d
        echo "✓ Redis started via Docker"
    else
        echo "⚠️  Redis not available - some features will be limited"
    fi
fi

echo ""
echo "📋 Sprint Overview:"
echo "- Duration: 2 weeks"
echo "- Focus: Control Center UI + Agent Intelligence"
echo "- Agents: Backend (Marcus), Frontend (Alex)"
echo ""

echo "🎯 Launch Options:"
echo ""
echo "1. Full Sprint Orchestration (Recommended):"
echo "   python3 sprint_1_6_orchestrator.py"
echo "   This will:"
echo "   - Launch agents automatically"
echo "   - Monitor their development"
echo "   - Review PRs with AI assistance"
echo "   - Handle merge decisions"
echo ""
echo "2. Fast Demo Mode:"
echo "   python3 sprint_1_6_orchestrator.py --fast"
echo ""
echo "3. Manual Agent Launch (if preferred):"
echo "   python3 launch_agent_with_tasks.py backend --task-file sprint_1_6_tasks/backend_agent_tasks.md"
echo "   python3 launch_agent_with_tasks.py frontend --task-file sprint_1_6_tasks/frontend_agent_tasks.md"
echo ""
echo "💡 Tip: Run each agent in a separate terminal for best visibility"
echo ""

# Create a simple status file
echo "Sprint 1.6 launched at $(date)" > sprint_1_6_status.log
echo "Agents can now be started with the commands above" >> sprint_1_6_status.log

echo "✅ Sprint 1.6 is ready to go!"