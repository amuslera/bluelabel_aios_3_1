#!/bin/bash
set -e

# Clean startup script for monitoring system
# Prevents stdout flooding and coordinates spam

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGS_DIR="${PROJECT_ROOT}/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting AIOSv3 Monitoring System${NC}"
echo -e "${BLUE}====================================${NC}"

# Create logs directory
mkdir -p "${LOGS_DIR}"

# Kill any existing monitoring processes
echo -e "${YELLOW}🧹 Cleaning up existing processes...${NC}"
pkill -f "monitoring_server\|control_center\|dashboard" 2>/dev/null || true

# Wait for cleanup
sleep 2

# Start monitoring server in background with output redirection
echo -e "${GREEN}📊 Starting monitoring server...${NC}"
cd "${PROJECT_ROOT}"
nohup python -m projects.monitoring.src.enhanced_monitoring_server \
    > "${LOGS_DIR}/monitoring_stdout.log" \
    2> "${LOGS_DIR}/monitoring_stderr.log" &

MONITORING_PID=$!
echo "Monitoring server PID: ${MONITORING_PID}"

# Wait for server to start
echo -e "${YELLOW}⏳ Waiting for server to start...${NC}"
sleep 3

# Check if monitoring server is running
if ! kill -0 "${MONITORING_PID}" 2>/dev/null; then
    echo -e "${RED}❌ Monitoring server failed to start${NC}"
    echo -e "${RED}Check logs: ${LOGS_DIR}/monitoring_stderr.log${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Monitoring server started successfully${NC}"
echo -e "${BLUE}📄 Logs available at:${NC}"
echo -e "   - Server: ${LOGS_DIR}/monitoring.log"
echo -e "   - Stdout: ${LOGS_DIR}/monitoring_stdout.log"
echo -e "   - Stderr: ${LOGS_DIR}/monitoring_stderr.log"

echo -e "\n${GREEN}🎯 Monitoring system is ready!${NC}"
echo -e "${YELLOW}Commands:${NC}"
echo -e "   - View logs: tail -f ${LOGS_DIR}/monitoring.log"
echo -e "   - Stop server: kill ${MONITORING_PID}"
echo -e "   - Health check: curl http://localhost:6795/api/health"

# Store PID for easy cleanup
echo "${MONITORING_PID}" > "${LOGS_DIR}/monitoring.pid"

echo -e "\n${BLUE}Press Ctrl+C to stop the monitoring system${NC}"

# Wait for interrupt
trap "echo -e '\n${YELLOW}🛑 Stopping monitoring system...${NC}'; kill ${MONITORING_PID} 2>/dev/null || true; rm -f ${LOGS_DIR}/monitoring.pid; echo -e '${GREEN}✅ Monitoring system stopped${NC}'; exit 0" INT

# Keep script running
wait "${MONITORING_PID}"