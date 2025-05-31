#!/bin/bash

# AIOSv3 Development Environment Setup Script
set -e

echo "🚀 Setting up AIOSv3 Development Environment"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
print_status "Checking prerequisites..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_success "Prerequisites check passed"

# Create necessary directories
print_status "Creating project directories..."
mkdir -p logs
mkdir -p infrastructure/prometheus
mkdir -p infrastructure/grafana/dashboards
mkdir -p infrastructure/grafana/provisioning/dashboards
mkdir -p infrastructure/grafana/provisioning/datasources
mkdir -p data/workspaces
mkdir -p data/artifacts

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating .env file from template..."
    cp .env.example .env
    print_warning "Please edit .env file with your actual configuration"
fi

# Create Prometheus configuration
print_status "Creating Prometheus configuration..."
cat > infrastructure/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'aiosv3-app'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['rabbitmq:15692']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF

# Create Grafana datasource configuration
print_status "Creating Grafana configuration..."
cat > infrastructure/grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

# Create Grafana dashboard provisioning
cat > infrastructure/grafana/provisioning/dashboards/dashboard.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
EOF

# Build and start development environment
print_status "Building development containers..."
docker-compose -f docker-compose.dev.yml build

print_status "Starting development environment..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# Check service health
print_status "Checking service health..."

services=("rabbitmq:15672" "minio:9000" "redis:6379" "qdrant:6333" "prometheus:9090" "grafana:3000")
for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -f -s "http://localhost:$port" > /dev/null 2>&1; then
        print_success "$name is running on port $port"
    else
        print_warning "$name may still be starting up on port $port"
    fi
done

# Display access information
print_success "Development environment is ready!"
echo ""
echo "🔗 Service Access URLs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📱 Application:        http://localhost:8000"
echo "📊 API Documentation:  http://localhost:8000/docs"
echo "🐰 RabbitMQ Management: http://localhost:15672 (aiosv3/dev_password)"
echo "🗄️  MinIO Console:      http://localhost:9001 (aiosv3/dev_password_123)"
echo "📈 Prometheus:         http://localhost:9090"
echo "📊 Grafana:            http://localhost:3000 (admin/dev_password)"
echo "🔍 Qdrant:             http://localhost:6333"
echo ""
echo "🛠️  Development Commands:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 Enter container:     docker-compose -f docker-compose.dev.yml exec app bash"
echo "📋 View logs:           docker-compose -f docker-compose.dev.yml logs -f"
echo "🔄 Restart services:    docker-compose -f docker-compose.dev.yml restart"
echo "🛑 Stop environment:    docker-compose -f docker-compose.dev.yml down"
echo ""
echo "Happy coding! 🚀"