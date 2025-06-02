# Deployment Guide

Complete guide for deploying AIOSv3 in production environments, from single-server setups to large-scale Kubernetes clusters.

## 🏗️ Deployment Architectures

### 1. Development Setup
Single machine with all components:
```
┌─────────────────────────────────────┐
│  Development Machine               │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Monitoring  │ │ Control     │   │
│  │ Server      │ │ Center      │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ Agents (3-5 instances)      │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ SQLite Database             │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

### 2. Small Production Setup
Dedicated servers with load balancing:
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Load        │    │ Monitoring  │    │ Database    │
│ Balancer    │◄──►│ Servers     │◄──►│ (PostgreSQL)│
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │
       ▼                   ▼
┌─────────────┐    ┌─────────────┐
│ Agent       │    │ Control     │
│ Cluster     │    │ Center      │
└─────────────┘    └─────────────┘
```

### 3. Large Scale Kubernetes
Enterprise deployment with microservices:
```
┌──────────────────────────────────────────────────────────┐
│ Kubernetes Cluster                                       │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│ │ Monitoring  │ │ Agent       │ │ Control     │          │
│ │ Service     │ │ Deployments │ │ Center      │          │
│ │ (3 replicas)│ │ (Auto-scale)│ │ Service     │          │
│ └─────────────┘ └─────────────┘ └─────────────┘          │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│ │ Redis       │ │ PostgreSQL  │ │ Prometheus  │          │
│ │ Cluster     │ │ HA Setup    │ │ + Grafana   │          │
│ └─────────────┘ └─────────────┘ └─────────────┘          │
└──────────────────────────────────────────────────────────┘
```

## 🐳 Docker Deployment

### Basic Docker Setup

#### 1. Build Images

```bash
# Build monitoring server image
docker build -f docker/Dockerfile.monitoring -t aios/monitoring:latest .

# Build agent base image
docker build -f docker/Dockerfile.agent -t aios/agent-base:latest .

# Build control center image
docker build -f docker/Dockerfile.control-center -t aios/control-center:latest .
```

#### 2. Docker Compose Configuration

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  # Database
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: aios_monitoring
      POSTGRES_USER: aios
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped

  # Redis for caching and sessions
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped

  # Monitoring Server
  monitoring-server:
    image: aios/monitoring:latest
    environment:
      - DB_URL=postgresql://aios:${DB_PASSWORD}@postgres:5432/aios_monitoring
      - REDIS_URL=redis://redis:6379
      - MONITORING_API_KEY=${MONITORING_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - RATE_LIMIT=1000
    ports:
      - "6795:6795"
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6795/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Control Center
  control-center:
    image: aios/control-center:latest
    environment:
      - MONITORING_URL=http://monitoring-server:6795
      - MONITORING_API_KEY=${MONITORING_API_KEY}
    ports:
      - "8080:8080"  # Web interface
    depends_on:
      - monitoring-server
    restart: unless-stopped

  # Backend Agent
  backend-agent:
    image: aios/agent-base:latest
    environment:
      - MONITORING_URL=http://monitoring-server:6795
      - MONITORING_API_KEY=${MONITORING_API_KEY}
      - AGENT_TYPE=backend
      - AGENT_NAME=Backend Agent
      - MAX_CONCURRENT_TASKS=5
    depends_on:
      - monitoring-server
    restart: unless-stopped
    deploy:
      replicas: 2

  # Frontend Agent
  frontend-agent:
    image: aios/agent-base:latest
    environment:
      - MONITORING_URL=http://monitoring-server:6795
      - MONITORING_API_KEY=${MONITORING_API_KEY}
      - AGENT_TYPE=frontend
      - AGENT_NAME=Frontend Agent
      - MAX_CONCURRENT_TASKS=3
    depends_on:
      - monitoring-server
    restart: unless-stopped
    deploy:
      replicas: 2

  # Load Balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - monitoring-server
      - control-center
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    name: aios-network
```

#### 3. Environment Configuration

Create `.env` file:
```bash
# Database
DB_PASSWORD=your_secure_db_password

# API Security
MONITORING_API_KEY=aios_your_secure_api_key_here
JWT_SECRET=your_jwt_secret_here

# LLM Configuration
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Optional: External Services
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
PROMETHEUS_URL=http://prometheus:9090
```

#### 4. Deploy with Docker Compose

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f monitoring-server

# Scale agents
docker-compose -f docker-compose.prod.yml up -d --scale backend-agent=5

# Update configuration
docker-compose -f docker-compose.prod.yml restart monitoring-server
```

### Advanced Docker Configuration

#### Multi-Stage Dockerfile for Optimization

```dockerfile
# docker/Dockerfile.monitoring
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim

# Create non-root user
RUN useradd --create-home --shell /bin/bash aios

# Copy installed packages
COPY --from=builder /root/.local /home/aios/.local

# Copy application code
WORKDIR /app
COPY --chown=aios:aios projects/monitoring/ .
COPY --chown=aios:aios src/ src/

# Set environment
ENV PATH=/home/aios/.local/bin:$PATH
ENV PYTHONPATH=/app

USER aios
EXPOSE 6795

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:6795/api/health || exit 1

CMD ["python", "src/enhanced_monitoring_server.py"]
```

## ☸️ Kubernetes Deployment

### 1. Namespace Setup

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: aios-platform
  labels:
    name: aios-platform
```

### 2. Configuration Management

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aios-config
  namespace: aios-platform
data:
  MONITORING_URL: "http://monitoring-service:6795"
  RATE_LIMIT: "1000"
  LOG_LEVEL: "INFO"
  MAX_CONCURRENT_TASKS: "5"
```

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: aios-secrets
  namespace: aios-platform
type: Opaque
data:
  MONITORING_API_KEY: # base64 encoded
  DB_PASSWORD: # base64 encoded
  JWT_SECRET: # base64 encoded
  OPENAI_API_KEY: # base64 encoded
```

### 3. Database Setup

```yaml
# k8s/postgres.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: aios-platform
spec:
  serviceName: postgres-service
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          value: aios_monitoring
        - name: POSTGRES_USER
          value: aios
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: aios-secrets
              key: DB_PASSWORD
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi

---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: aios-platform
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP
```

### 4. Monitoring Server Deployment

```yaml
# k8s/monitoring-server.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: monitoring-server
  namespace: aios-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: monitoring-server
  template:
    metadata:
      labels:
        app: monitoring-server
    spec:
      containers:
      - name: monitoring-server
        image: aios/monitoring:latest
        ports:
        - containerPort: 6795
        env:
        - name: DB_URL
          value: "postgresql://aios:$(DB_PASSWORD)@postgres-service:5432/aios_monitoring"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: aios-secrets
              key: DB_PASSWORD
        envFrom:
        - configMapRef:
            name: aios-config
        - secretRef:
            name: aios-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 6795
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 6795
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: monitoring-service
  namespace: aios-platform
spec:
  selector:
    app: monitoring-server
  ports:
  - port: 6795
    targetPort: 6795
  type: ClusterIP

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: monitoring-ingress
  namespace: aios-platform
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - aios-monitoring.yourdomain.com
    secretName: monitoring-tls
  rules:
  - host: aios-monitoring.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: monitoring-service
            port:
              number: 6795
```

### 5. Agent Deployments

```yaml
# k8s/agents.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-agents
  namespace: aios-platform
spec:
  replicas: 5
  selector:
    matchLabels:
      app: backend-agent
  template:
    metadata:
      labels:
        app: backend-agent
        agent-type: backend
    spec:
      containers:
      - name: backend-agent
        image: aios/agent-base:latest
        env:
        - name: AGENT_TYPE
          value: "backend"
        - name: AGENT_NAME
          value: "Backend Agent"
        envFrom:
        - configMapRef:
            name: aios-config
        - secretRef:
            name: aios-secrets
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-agents
  namespace: aios-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend-agent
  template:
    metadata:
      labels:
        app: frontend-agent
        agent-type: frontend
    spec:
      containers:
      - name: frontend-agent
        image: aios/agent-base:latest
        env:
        - name: AGENT_TYPE
          value: "frontend"
        - name: AGENT_NAME
          value: "Frontend Agent"
        envFrom:
        - configMapRef:
            name: aios-config
        - secretRef:
            name: aios-secrets
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

### 6. Auto-scaling Configuration

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-agents-hpa
  namespace: aios-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend-agents
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: monitoring-server-hpa
  namespace: aios-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: monitoring-server
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
```

### 7. Deploy to Kubernetes

```bash
# Apply all configurations
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/monitoring-server.yaml
kubectl apply -f k8s/agents.yaml
kubectl apply -f k8s/hpa.yaml

# Check deployment status
kubectl get pods -n aios-platform
kubectl get services -n aios-platform
kubectl get ingress -n aios-platform

# View logs
kubectl logs -f deployment/monitoring-server -n aios-platform
kubectl logs -f deployment/backend-agents -n aios-platform
```

## 🔧 Production Configuration

### 1. Environment Variables

```bash
# Production environment file
# Security
MONITORING_API_KEY=aios_production_secure_key_32_chars
JWT_SECRET=your_production_jwt_secret_64_chars
DB_PASSWORD=very_secure_database_password

# Database
DB_HOST=postgres-service
DB_PORT=5432
DB_NAME=aios_monitoring
DB_USER=aios
DB_SSL_MODE=require

# Redis
REDIS_URL=redis://redis-service:6379
REDIS_PASSWORD=redis_password

# Monitoring
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000

# Rate Limiting
RATE_LIMIT=1000
RATE_LIMIT_WINDOW=60

# LLM APIs
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# External Integrations
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
DATADOG_API_KEY=your_datadog_key

# Performance
MAX_CONCURRENT_TASKS=10
HEALTH_CHECK_INTERVAL=30
WEBSOCKET_TIMEOUT=300

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/aios/server.log
```

### 2. Database Optimization

```sql
-- Production database optimizations
-- Add in init.sql

-- Indexes for performance
CREATE INDEX CONCURRENTLY idx_activities_agent_id_stored_at 
  ON activities(agent_id, stored_at DESC);

CREATE INDEX CONCURRENTLY idx_agent_registrations_status_last_heartbeat 
  ON agent_registrations(status, last_heartbeat DESC);

-- Partitioning for large datasets
CREATE TABLE activities_partitioned (
  LIKE activities INCLUDING ALL
) PARTITION BY RANGE (stored_at);

-- Create monthly partitions
CREATE TABLE activities_2024_12 PARTITION OF activities_partitioned
  FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');

-- Auto-vacuum settings
ALTER TABLE activities SET (
  autovacuum_vacuum_scale_factor = 0.1,
  autovacuum_analyze_scale_factor = 0.05
);
```

### 3. Nginx Load Balancer Configuration

```nginx
# nginx.conf
upstream monitoring_backend {
    least_conn;
    server monitoring-server-1:6795 max_fails=3 fail_timeout=30s;
    server monitoring-server-2:6795 max_fails=3 fail_timeout=30s;
    server monitoring-server-3:6795 max_fails=3 fail_timeout=30s;
}

upstream control_center_backend {
    server control-center-1:8080;
    server control-center-2:8080;
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=websocket:10m rate=5r/s;

server {
    listen 80;
    server_name aios.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name aios.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    # API endpoints
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://monitoring_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket endpoints
    location /ws {
        limit_req zone=websocket burst=10 nodelay;
        proxy_pass http://monitoring_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }

    # Control Center
    location /dashboard/ {
        proxy_pass http://control_center_backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Health checks
    location /health {
        access_log off;
        proxy_pass http://monitoring_backend/api/health;
    }
}
```

## 📊 Monitoring and Observability

### 1. Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'aios-monitoring'
    static_configs:
      - targets: ['monitoring-service:6795']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'aios-agents'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - aios-platform
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_agent_type]
        action: keep
        regex: backend|frontend|qa
```

### 2. Grafana Dashboards

```json
{
  "dashboard": {
    "title": "AIOSv3 Platform Monitoring",
    "panels": [
      {
        "title": "Active Agents",
        "type": "stat",
        "targets": [
          {
            "expr": "aios_active_agents_total",
            "legendFormat": "Active Agents"
          }
        ]
      },
      {
        "title": "Task Execution Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(aios_tasks_completed_total[5m])",
            "legendFormat": "Tasks/sec"
          }
        ]
      },
      {
        "title": "Agent Performance",
        "type": "table",
        "targets": [
          {
            "expr": "avg(aios_task_duration_seconds) by (agent_id)",
            "format": "table"
          }
        ]
      }
    ]
  }
}
```

### 3. Alerting Rules

```yaml
# alerts.yml
groups:
- name: aios-platform
  rules:
  - alert: MonitoringServerDown
    expr: up{job="aios-monitoring"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Monitoring server is down"
      description: "The monitoring server has been down for more than 1 minute"

  - alert: HighTaskFailureRate
    expr: rate(aios_tasks_failed_total[5m]) / rate(aios_tasks_total[5m]) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High task failure rate"
      description: "Task failure rate is above 10% for 2 minutes"

  - alert: AgentUnresponsive
    expr: time() - aios_agent_last_heartbeat > 300
    for: 0m
    labels:
      severity: warning
    annotations:
      summary: "Agent {{ $labels.agent_id }} is unresponsive"
      description: "Agent has not sent heartbeat for over 5 minutes"
```

## 🔐 Security Best Practices

### 1. Network Security

```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: aios-network-policy
  namespace: aios-platform
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: aios-platform
    ports:
    - protocol: TCP
      port: 6795
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: aios-platform
  - to: []
    ports:
    - protocol: TCP
      port: 443  # HTTPS
    - protocol: TCP
      port: 53   # DNS
    - protocol: UDP
      port: 53   # DNS
```

### 2. RBAC Configuration

```yaml
# k8s/rbac.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: aios-operator
  namespace: aios-platform

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: aios-operator-role
  namespace: aios-platform
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: aios-operator-binding
  namespace: aios-platform
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: aios-operator-role
subjects:
- kind: ServiceAccount
  name: aios-operator
  namespace: aios-platform
```

### 3. Pod Security Standards

```yaml
# k8s/pod-security.yaml
apiVersion: v1
kind: Pod
metadata:
  name: monitoring-server
  namespace: aios-platform
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 2000
  containers:
  - name: monitoring-server
    image: aios/monitoring:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
    volumeMounts:
    - name: tmp
      mountPath: /tmp
    - name: var-log
      mountPath: /var/log
  volumes:
  - name: tmp
    emptyDir: {}
  - name: var-log
    emptyDir: {}
```

## 🚀 CI/CD Pipeline

### 1. GitLab CI Configuration

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

variables:
  REGISTRY: registry.gitlab.com/yourorg/aios
  
test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - python -m pytest tests/
    - python run_coordination_tests.py
  coverage: '/TOTAL.*\s+(\d+%)$/'

build:
  stage: build
  image: docker:20.10.16
  services:
    - docker:20.10.16-dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -f docker/Dockerfile.monitoring -t $REGISTRY/monitoring:$CI_COMMIT_SHA .
    - docker build -f docker/Dockerfile.agent -t $REGISTRY/agent:$CI_COMMIT_SHA .
    - docker push $REGISTRY/monitoring:$CI_COMMIT_SHA
    - docker push $REGISTRY/agent:$CI_COMMIT_SHA
  only:
    - main

deploy_staging:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context staging
    - kubectl set image deployment/monitoring-server monitoring-server=$REGISTRY/monitoring:$CI_COMMIT_SHA -n aios-staging
    - kubectl rollout status deployment/monitoring-server -n aios-staging
  only:
    - main

deploy_production:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context production
    - kubectl set image deployment/monitoring-server monitoring-server=$REGISTRY/monitoring:$CI_COMMIT_SHA -n aios-platform
    - kubectl rollout status deployment/monitoring-server -n aios-platform
  when: manual
  only:
    - main
```

### 2. Health Checks and Readiness

```python
# health_check.py
import aiohttp
import asyncio
import sys

async def health_check():
    """Comprehensive health check for deployment."""
    checks = []
    
    # Monitoring server
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://monitoring-service:6795/api/health') as resp:
                if resp.status == 200:
                    checks.append(("Monitoring Server", True))
                else:
                    checks.append(("Monitoring Server", False))
    except Exception:
        checks.append(("Monitoring Server", False))
    
    # Database connectivity
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://monitoring-service:6795/api/agents') as resp:
                if resp.status in [200, 401]:  # 401 is OK, means auth is working
                    checks.append(("Database", True))
                else:
                    checks.append(("Database", False))
    except Exception:
        checks.append(("Database", False))
    
    # Print results
    all_healthy = True
    for service, healthy in checks:
        status = "✅" if healthy else "❌"
        print(f"{status} {service}")
        if not healthy:
            all_healthy = False
    
    return all_healthy

if __name__ == "__main__":
    healthy = asyncio.run(health_check())
    sys.exit(0 if healthy else 1)
```

## 📈 Performance Tuning

### 1. Database Optimization

```sql
-- Performance tuning for PostgreSQL
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Reload configuration
SELECT pg_reload_conf();
```

### 2. Application Performance

```python
# performance_config.py
import os

# Connection pooling
DATABASE_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '20'))
DATABASE_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '10'))

# Caching
REDIS_CACHE_TTL = int(os.getenv('CACHE_TTL', '300'))
REDIS_MAX_CONNECTIONS = int(os.getenv('REDIS_MAX_CONN', '50'))

# WebSocket settings
WEBSOCKET_HEARTBEAT_INTERVAL = int(os.getenv('WS_HEARTBEAT', '30'))
WEBSOCKET_MAX_CONNECTIONS = int(os.getenv('WS_MAX_CONN', '1000'))

# Agent settings
AGENT_HEARTBEAT_INTERVAL = int(os.getenv('AGENT_HEARTBEAT', '30'))
AGENT_TASK_TIMEOUT = int(os.getenv('AGENT_TIMEOUT', '300'))
```

### 3. Resource Limits

```yaml
# Production resource limits
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"

# For high-throughput deployments
resources:
  requests:
    memory: "1Gi"
    cpu: "1000m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

## 🔄 Backup and Recovery

### 1. Database Backup

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Create database backup
kubectl exec -n aios-platform postgres-0 -- pg_dump -U aios aios_monitoring > $BACKUP_DIR/db_backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/db_backup_$DATE.sql

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/db_backup_$DATE.sql.gz s3://your-backup-bucket/aios/

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete
```

### 2. Disaster Recovery

```yaml
# k8s/restore-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: restore-database
  namespace: aios-platform
spec:
  template:
    spec:
      containers:
      - name: restore
        image: postgres:15
        env:
        - name: PGPASSWORD
          valueFrom:
            secretKeyRef:
              name: aios-secrets
              key: DB_PASSWORD
        command:
        - /bin/bash
        - -c
        - |
          # Download backup from S3
          aws s3 cp s3://your-backup-bucket/aios/db_backup_latest.sql.gz /tmp/
          gunzip /tmp/db_backup_latest.sql.gz
          
          # Restore database
          psql -h postgres-service -U aios -d aios_monitoring -f /tmp/db_backup_latest.sql
      restartPolicy: Never
```

## 🎯 Best Practices Summary

### 1. Security
- Use strong API keys and rotate regularly
- Enable TLS/SSL for all communications
- Implement network policies and RBAC
- Run containers as non-root users
- Regular security scans and updates

### 2. Performance
- Use connection pooling
- Implement caching strategies
- Monitor resource usage
- Set appropriate resource limits
- Use horizontal pod autoscaling

### 3. Reliability
- Implement health checks
- Use rolling updates
- Set up monitoring and alerting
- Regular backups
- Test disaster recovery procedures

### 4. Scalability
- Design for horizontal scaling
- Use load balancers
- Implement auto-scaling
- Monitor performance metrics
- Plan capacity carefully

This deployment guide provides everything needed to run AIOSv3 in production, from small single-server setups to large-scale Kubernetes clusters.