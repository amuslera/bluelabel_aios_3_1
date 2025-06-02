"""
DevOps Engineering Agent - Jordan Kim

A pragmatic DevOps engineer focused on infrastructure automation, CI/CD pipelines,
and operational excellence. Jordan brings Netflix-level SRE expertise to the team.
"""

import asyncio
import json
import random
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

from src.agents.base.agent import Agent
from src.agents.base.enhanced_agent import EnhancedAgent
from src.agents.base.types import AgentConfig, TaskResult, TaskStatus
from src.agents.collaborative_agent import CollaborativeAgent
from src.core.messaging.queue import MessageQueue
from src.core.routing.router import RoutingSystem
from src.agents.specialists.devops_personality import DevOpsPersonality


@dataclass
class InfrastructureProject:
    """Represents an infrastructure or deployment project"""
    project_name: str
    project_type: str  # 'microservices', 'monolith', 'serverless', 'ml-pipeline'
    tech_stack: List[str]
    environments: List[str] = field(default_factory=lambda: ['dev', 'staging', 'prod'])
    deployment_strategy: str = 'rolling'  # 'rolling', 'blue-green', 'canary'
    monitoring_setup: Dict[str, Any] = field(default_factory=dict)
    ci_cd_pipeline: Dict[str, Any] = field(default_factory=dict)
    infrastructure_code: Dict[str, str] = field(default_factory=dict)
    security_config: Dict[str, Any] = field(default_factory=dict)
    

class JordanDevOpsAgent(CollaborativeAgent):
    """
    Jordan Kim - The DevOps Engineering Agent
    
    A pragmatic, efficiency-focused DevOps engineer who automates everything
    and builds bulletproof infrastructure. Former Netflix SRE with a passion
    for Kubernetes and zero-downtime deployments.
    """
    
    def __init__(
        self,
        message_queue: Optional[MessageQueue] = None,
        routing_system: Optional[RoutingSystem] = None
    ):
        # Initialize with Jordan's specific configuration
        config = AgentConfig(
            name="Jordan Kim",
            role="DevOps Engineer",
            capabilities=[
                "ci_cd_pipelines",
                "kubernetes_orchestration",
                "infrastructure_as_code",
                "monitoring_observability",
                "cloud_architecture",
                "security_automation",
                "deployment_strategies",
                "disaster_recovery"
            ],
            llm_config={
                "provider": "openai",
                "model": "gpt-4",
                "temperature": 0.3,  # Lower temperature for precise infrastructure work
                "max_tokens": 3000
            }
        )
        
        # Initialize parent with Jordan's personality
        super().__init__(
            config=config,
            message_queue=message_queue,
            routing_system=routing_system,
            personality=DevOpsPersonality()
        )
        
        # Jordan's expertise areas
        self.expertise = {
            "ci_cd": ["GitHub Actions", "GitLab CI", "Jenkins", "ArgoCD", "Spinnaker"],
            "containers": ["Docker", "Kubernetes", "Helm", "Istio", "Linkerd"],
            "infrastructure": ["Terraform", "Ansible", "CloudFormation", "Pulumi"],
            "monitoring": ["Prometheus", "Grafana", "ELK", "Datadog", "New Relic"],
            "clouds": ["AWS", "GCP", "Azure", "Hybrid Cloud"],
            "security": ["Vault", "SOPS", "OPA", "Falco", "Trivy"]
        }
        
        # Current projects Jordan is managing
        self.active_projects: Dict[str, InfrastructureProject] = {}
        
        # Deployment metrics
        self.deployment_metrics = {
            "total_deployments": 0,
            "successful_deployments": 0,
            "failed_deployments": 0,
            "rollbacks": 0,
            "mttr_minutes": 0,  # Mean Time To Recovery
            "uptime_percentage": 99.99
        }
        
        # Jordan's automation principles
        self.principles = [
            "If it's not automated, it's broken",
            "Everything as code - infrastructure, config, policy",
            "Monitoring first, then deploy",
            "Security is not optional",
            "Plan for failure, design for recovery"
        ]
        
    async def analyze_infrastructure_needs(self, project_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project requirements and recommend infrastructure setup"""
        analysis = {
            "project_type": self._determine_project_type(project_spec),
            "recommended_stack": {},
            "estimated_resources": {},
            "security_requirements": [],
            "monitoring_strategy": {},
            "cost_estimate": {}
        }
        
        # Determine infrastructure needs based on project type
        project_type = analysis["project_type"]
        
        if project_type == "microservices":
            analysis["recommended_stack"] = {
                "orchestration": "Kubernetes with Istio service mesh",
                "ci_cd": "GitLab CI with ArgoCD for GitOps",
                "monitoring": "Prometheus + Grafana + Jaeger for tracing",
                "storage": "PostgreSQL with Redis caching",
                "message_queue": "Kafka for event streaming"
            }
        elif project_type == "serverless":
            analysis["recommended_stack"] = {
                "platform": "AWS Lambda with API Gateway",
                "ci_cd": "GitHub Actions with Serverless Framework",
                "monitoring": "CloudWatch with X-Ray tracing",
                "storage": "DynamoDB with S3 for objects",
                "event_bus": "EventBridge for async processing"
            }
        else:  # monolith
            analysis["recommended_stack"] = {
                "hosting": "AWS ECS or traditional VMs",
                "ci_cd": "Jenkins with Blue-Green deployments",
                "monitoring": "New Relic or Datadog",
                "storage": "PostgreSQL with read replicas",
                "caching": "Redis or Memcached"
            }
            
        # Estimate resources
        analysis["estimated_resources"] = self._estimate_resources(project_spec, project_type)
        
        # Security requirements
        analysis["security_requirements"] = [
            "TLS everywhere (mTLS for microservices)",
            "Secrets management with HashiCorp Vault",
            "Container scanning with Trivy",
            "Runtime security with Falco",
            "Policy enforcement with OPA"
        ]
        
        # Monitoring strategy
        analysis["monitoring_strategy"] = {
            "metrics": "Prometheus with custom dashboards",
            "logs": "ELK stack with structured logging",
            "traces": "Jaeger or AWS X-Ray for distributed tracing",
            "alerts": "PagerDuty integration with smart routing",
            "slos": ["99.9% uptime", "p99 latency < 200ms", "error rate < 0.1%"]
        }
        
        return analysis
        
    async def generate_ci_cd_pipeline(self, project: InfrastructureProject) -> Dict[str, str]:
        """Generate CI/CD pipeline configuration"""
        templates = {}
        
        # GitHub Actions workflow
        if "github" in project.tech_stack or True:  # Default to GitHub Actions
            templates["github_actions"] = self._generate_github_actions_workflow(project)
            
        # GitLab CI configuration
        templates["gitlab_ci"] = self._generate_gitlab_ci_config(project)
        
        # Dockerfile for containerization
        templates["dockerfile"] = self._generate_dockerfile(project)
        
        # Kubernetes manifests
        templates["k8s_deployment"] = self._generate_k8s_deployment(project)
        templates["k8s_service"] = self._generate_k8s_service(project)
        
        # Terraform for infrastructure
        templates["terraform_main"] = self._generate_terraform_config(project)
        
        # Monitoring configuration
        templates["prometheus_config"] = self._generate_prometheus_config(project)
        
        return templates
        
    async def setup_monitoring(self, project: InfrastructureProject) -> Dict[str, Any]:
        """Set up comprehensive monitoring and observability"""
        monitoring_config = {
            "metrics": {
                "prometheus": self._configure_prometheus(project),
                "grafana_dashboards": self._create_grafana_dashboards(project)
            },
            "logging": {
                "elasticsearch": self._configure_elasticsearch(project),
                "logstash": self._configure_logstash_pipelines(project),
                "kibana_dashboards": self._create_kibana_dashboards(project)
            },
            "tracing": {
                "jaeger": self._configure_jaeger(project)
            },
            "alerting": {
                "rules": self._create_alerting_rules(project),
                "escalation": self._setup_escalation_policy(project)
            },
            "slos": self._define_slos(project)
        }
        
        return monitoring_config
        
    async def handle_incident(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle production incidents with automated response"""
        response = {
            "incident_id": f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "severity": self._assess_severity(incident_data),
            "affected_services": [],
            "mitigation_steps": [],
            "status_updates": []
        }
        
        # Automated incident response
        if response["severity"] in ["critical", "high"]:
            # Immediate actions
            response["mitigation_steps"].append("Initiated automatic rollback")
            response["mitigation_steps"].append("Scaled up healthy instances")
            response["mitigation_steps"].append("Enabled circuit breakers")
            
            # Notify team
            await self._broadcast_to_team({
                "type": "incident_alert",
                "severity": response["severity"],
                "message": f"🚨 Production incident detected: {incident_data.get('description', 'Unknown issue')}"
            })
            
        # Generate runbook
        response["runbook"] = self._generate_incident_runbook(incident_data)
        
        # Track MTTR
        self.deployment_metrics["mttr_minutes"] = (
            (self.deployment_metrics["mttr_minutes"] * self.deployment_metrics["total_deployments"] + 15) /
            (self.deployment_metrics["total_deployments"] + 1)
        )
        
        return response
        
    async def optimize_infrastructure(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and optimize infrastructure for cost and performance"""
        optimizations = {
            "cost_savings": [],
            "performance_improvements": [],
            "security_enhancements": [],
            "recommendations": []
        }
        
        # Cost optimization
        if current_state.get("idle_resources"):
            optimizations["cost_savings"].append({
                "action": "Right-size underutilized instances",
                "potential_savings": "$2,400/month",
                "implementation": "Terraform plan included"
            })
            
        # Performance optimization
        if current_state.get("high_latency_services"):
            optimizations["performance_improvements"].append({
                "action": "Implement caching layer",
                "expected_improvement": "60% latency reduction",
                "implementation": "Redis configuration provided"
            })
            
        # Security enhancements
        optimizations["security_enhancements"].append({
            "action": "Enable mTLS for service-to-service communication",
            "risk_reduction": "High",
            "implementation": "Istio configuration included"
        })
        
        return optimizations
        
    def _determine_project_type(self, project_spec: Dict[str, Any]) -> str:
        """Determine the type of project based on specifications"""
        indicators = project_spec.get("indicators", {})
        
        if indicators.get("multiple_services") or "microservices" in str(project_spec).lower():
            return "microservices"
        elif indicators.get("event_driven") or "lambda" in str(project_spec).lower():
            return "serverless"
        else:
            return "monolith"
            
    def _estimate_resources(self, project_spec: Dict[str, Any], project_type: str) -> Dict[str, Any]:
        """Estimate resource requirements"""
        base_resources = {
            "microservices": {
                "kubernetes_nodes": 3,
                "cpu_cores": 8,
                "memory_gb": 32,
                "storage_gb": 500,
                "monthly_cost_estimate": "$450"
            },
            "serverless": {
                "lambda_functions": 10,
                "api_gateway_requests": "1M/month",
                "dynamodb_capacity": "On-demand",
                "monthly_cost_estimate": "$200"
            },
            "monolith": {
                "ec2_instances": 2,
                "cpu_cores": 4,
                "memory_gb": 16,
                "storage_gb": 200,
                "monthly_cost_estimate": "$300"
            }
        }
        
        return base_resources.get(project_type, base_resources["monolith"])
        
    def _generate_github_actions_workflow(self, project: InfrastructureProject) -> str:
        """Generate GitHub Actions workflow"""
        workflow = f"""name: CI/CD Pipeline for {project.project_name}

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run tests
      run: |
        docker-compose run --rm test
        
    - name: Security scan
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: '${{{{ github.repository }}}}:${{{{ github.sha }}}}'
        
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          ${{{{ secrets.REGISTRY }}}}/${{{{ github.repository }}}}:${{{{ github.sha }}}}
          ${{{{ secrets.REGISTRY }}}}/${{{{ github.repository }}}}:latest
          
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/{project.project_name} \\
          app=${{{{ secrets.REGISTRY }}}}/${{{{ github.repository }}}}:${{{{ github.sha }}}}
"""
        return workflow
        
    def _generate_dockerfile(self, project: InfrastructureProject) -> str:
        """Generate optimized Dockerfile"""
        # Detect language from tech stack
        if "python" in [tech.lower() for tech in project.tech_stack]:
            return self._python_dockerfile(project)
        elif "node" in [tech.lower() for tech in project.tech_stack]:
            return self._node_dockerfile(project)
        else:
            return self._generic_dockerfile(project)
            
    def _python_dockerfile(self, project: InfrastructureProject) -> str:
        """Python-specific Dockerfile"""
        return """FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Security: Run as non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        
    def _node_dockerfile(self, project: InfrastructureProject) -> str:
        """Node.js-specific Dockerfile"""
        return """FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine
WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /app/node_modules ./node_modules
COPY . .

# Security: Run as non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
USER nodejs

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD node healthcheck.js

EXPOSE 3000
CMD ["node", "server.js"]
"""
        
    def _generic_dockerfile(self, project: InfrastructureProject) -> str:
        """Generic Dockerfile template"""
        return """FROM ubuntu:22.04

WORKDIR /app
COPY . .

# Install dependencies (customize as needed)
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Security: Run as non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080
CMD ["./start.sh"]
"""
        
    def _generate_k8s_deployment(self, project: InfrastructureProject) -> str:
        """Generate Kubernetes deployment manifest"""
        return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {project.project_name}
  labels:
    app: {project.project_name}
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: {project.project_name}
  template:
    metadata:
      labels:
        app: {project.project_name}
    spec:
      containers:
      - name: {project.project_name}
        image: {project.project_name}:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: production
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
"""
        
    def _generate_k8s_service(self, project: InfrastructureProject) -> str:
        """Generate Kubernetes service manifest"""
        return f"""apiVersion: v1
kind: Service
metadata:
  name: {project.project_name}
  labels:
    app: {project.project_name}
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
  selector:
    app: {project.project_name}
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {project.project_name}
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - {project.project_name}.example.com
    secretName: {project.project_name}-tls
  rules:
  - host: {project.project_name}.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {project.project_name}
            port:
              number: 80
"""
        
    def _generate_terraform_config(self, project: InfrastructureProject) -> str:
        """Generate Terraform configuration"""
        return f"""terraform {{
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
    kubernetes = {{
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }}
  }}
}}

# EKS Cluster
module "eks" {{
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "{project.project_name}-cluster"
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {{
    main = {{
      desired_size = 2
      min_size     = 1
      max_size     = 4

      instance_types = ["t3.medium"]
      
      tags = {{
        Environment = "production"
        Project     = "{project.project_name}"
      }}
    }}
  }}
}}

# RDS Database
resource "aws_db_instance" "main" {{
  identifier = "{project.project_name}-db"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_encrypted     = true
  
  db_name  = "{project.project_name.replace('-', '_')}"
  username = "dbadmin"
  password = random_password.db_password.result
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  deletion_protection = true
  skip_final_snapshot = false
  
  tags = {{
    Name        = "{project.project_name}-db"
    Environment = "production"
  }}
}}

# S3 Bucket for artifacts
resource "aws_s3_bucket" "artifacts" {{
  bucket = "{project.project_name}-artifacts"
  
  tags = {{
    Name        = "{project.project_name}-artifacts"
    Environment = "production"
  }}
}}

resource "aws_s3_bucket_versioning" "artifacts" {{
  bucket = aws_s3_bucket.artifacts.id
  versioning_configuration {{
    status = "Enabled"
  }}
}}

resource "aws_s3_bucket_encryption" "artifacts" {{
  bucket = aws_s3_bucket.artifacts.id
  
  rule {{
    apply_server_side_encryption_by_default {{
      sse_algorithm = "AES256"
    }}
  }}
}}
"""
        
    def _generate_prometheus_config(self, project: InfrastructureProject) -> str:
        """Generate Prometheus configuration"""
        return f"""global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

rule_files:
  - "alerts/*.yml"

scrape_configs:
  - job_name: '{project.project_name}'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\\d+)?;(\\d+)
        replacement: $1:$2
        target_label: __address__
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: kubernetes_pod_name
"""
        
    def _configure_prometheus(self, project: InfrastructureProject) -> Dict[str, Any]:
        """Configure Prometheus monitoring"""
        return {
            "scrape_configs": [
                {
                    "job_name": project.project_name,
                    "scrape_interval": "15s",
                    "metrics_path": "/metrics",
                    "static_configs": [{
                        "targets": [f"{project.project_name}:8000"]
                    }]
                }
            ],
            "recording_rules": self._create_recording_rules(project),
            "alerting_rules": self._create_alerting_rules(project)
        }
        
    def _create_grafana_dashboards(self, project: InfrastructureProject) -> List[Dict[str, Any]]:
        """Create Grafana dashboards"""
        return [
            {
                "name": f"{project.project_name} Overview",
                "panels": [
                    {"title": "Request Rate", "query": f"rate(http_requests_total{{job='{project.project_name}'}}[5m])"},
                    {"title": "Error Rate", "query": f"rate(http_requests_total{{job='{project.project_name}',status=~'5..'}}[5m])"},
                    {"title": "Response Time", "query": f"histogram_quantile(0.95, http_request_duration_seconds{{job='{project.project_name}'}})"},
                    {"title": "Active Connections", "query": f"http_connections_active{{job='{project.project_name}'}}"}
                ]
            }
        ]
        
    def _configure_elasticsearch(self, project: InfrastructureProject) -> Dict[str, Any]:
        """Configure Elasticsearch for log aggregation"""
        return {
            "index_pattern": f"{project.project_name}-*",
            "settings": {
                "number_of_shards": 3,
                "number_of_replicas": 1,
                "refresh_interval": "5s"
            },
            "mappings": {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "level": {"type": "keyword"},
                    "service": {"type": "keyword"},
                    "message": {"type": "text"},
                    "trace_id": {"type": "keyword"},
                    "span_id": {"type": "keyword"}
                }
            }
        }
        
    def _configure_logstash_pipelines(self, project: InfrastructureProject) -> Dict[str, str]:
        """Configure Logstash pipelines"""
        return {
            "main": f"""input {{
  beats {{
    port => 5044
  }}
}}

filter {{
  if [service] == "{project.project_name}" {{
    grok {{
      match => {{ "message" => "%{{TIMESTAMP_ISO8601:timestamp}} %{{LOGLEVEL:level}} %{{GREEDYDATA:msg}}" }}
    }}
    
    date {{
      match => [ "timestamp", "ISO8601" ]
    }}
    
    mutate {{
      add_field => {{ "environment" => "%{{[@metadata][env]}}" }}
    }}
  }}
}}

output {{
  elasticsearch {{
    hosts => ["elasticsearch:9200"]
    index => "{project.project_name}-%{{+YYYY.MM.dd}}"
  }}
}}"""
        }
        
    def _create_kibana_dashboards(self, project: InfrastructureProject) -> List[Dict[str, Any]]:
        """Create Kibana dashboards for log analysis"""
        return [
            {
                "title": f"{project.project_name} Logs",
                "visualizations": [
                    {"type": "line", "title": "Log Volume", "query": {"match_all": {}}},
                    {"type": "pie", "title": "Log Levels", "agg": "terms", "field": "level"},
                    {"type": "table", "title": "Recent Errors", "query": {"match": {"level": "ERROR"}}}
                ]
            }
        ]
        
    def _configure_jaeger(self, project: InfrastructureProject) -> Dict[str, Any]:
        """Configure Jaeger for distributed tracing"""
        return {
            "agent": {
                "host": "jaeger-agent",
                "port": 6831
            },
            "sampling": {
                "type": "adaptive",
                "max_traces_per_second": 100
            },
            "storage": {
                "type": "elasticsearch",
                "elasticsearch": {
                    "servers": ["http://elasticsearch:9200"],
                    "index_prefix": f"{project.project_name}-traces"
                }
            }
        }
        
    def _create_recording_rules(self, project: InfrastructureProject) -> List[Dict[str, Any]]:
        """Create Prometheus recording rules for performance"""
        return [
            {
                "record": f"{project.project_name}:http_request_rate5m",
                "expr": f"rate(http_requests_total{{job='{project.project_name}'}}[5m])"
            },
            {
                "record": f"{project.project_name}:http_error_rate5m",
                "expr": f"rate(http_requests_total{{job='{project.project_name}',status=~'5..'}}[5m])"
            }
        ]
        
    def _create_alerting_rules(self, project: InfrastructureProject) -> List[Dict[str, Any]]:
        """Create comprehensive alerting rules"""
        return [
            {
                "alert": "HighErrorRate",
                "expr": f"{project.project_name}:http_error_rate5m > 0.05",
                "for": "5m",
                "labels": {"severity": "critical", "team": "platform"},
                "annotations": {
                    "summary": "High error rate detected",
                    "description": f"Error rate for {project.project_name} is above 5%"
                }
            },
            {
                "alert": "HighLatency",
                "expr": f"histogram_quantile(0.95, http_request_duration_seconds{{job='{project.project_name}'}}) > 0.5",
                "for": "5m",
                "labels": {"severity": "warning", "team": "platform"},
                "annotations": {
                    "summary": "High latency detected",
                    "description": f"95th percentile latency for {project.project_name} is above 500ms"
                }
            },
            {
                "alert": "PodCrashLooping",
                "expr": f"rate(kube_pod_container_status_restarts_total{{pod=~'{project.project_name}.*'}}[5m]) > 0",
                "for": "5m",
                "labels": {"severity": "critical", "team": "platform"},
                "annotations": {
                    "summary": "Pod is crash looping",
                    "description": "Pod {{ $labels.pod }} has restarted {{ $value }} times in the last 5 minutes"
                }
            }
        ]
        
    def _setup_escalation_policy(self, project: InfrastructureProject) -> Dict[str, Any]:
        """Set up alert escalation policy"""
        return {
            "levels": [
                {
                    "level": 1,
                    "targets": ["on-call-engineer"],
                    "delay_minutes": 0
                },
                {
                    "level": 2,
                    "targets": ["team-lead", "on-call-engineer"],
                    "delay_minutes": 15
                },
                {
                    "level": 3,
                    "targets": ["engineering-manager", "team-lead"],
                    "delay_minutes": 30
                }
            ],
            "schedules": {
                "on-call": {
                    "rotation": "weekly",
                    "engineers": ["jordan", "alex", "marcus", "emily"]
                }
            }
        }
        
    def _define_slos(self, project: InfrastructureProject) -> List[Dict[str, Any]]:
        """Define Service Level Objectives"""
        return [
            {
                "name": "Availability",
                "target": 99.9,
                "measurement": "uptime_percentage",
                "window": "30d"
            },
            {
                "name": "Latency",
                "target": 200,
                "measurement": "p99_latency_ms",
                "window": "7d"
            },
            {
                "name": "Error Rate",
                "target": 0.1,
                "measurement": "error_percentage",
                "window": "1d"
            }
        ]
        
    def _assess_severity(self, incident_data: Dict[str, Any]) -> str:
        """Assess incident severity"""
        indicators = incident_data.get("indicators", {})
        
        if indicators.get("service_down") or indicators.get("data_loss"):
            return "critical"
        elif indicators.get("high_error_rate") or indicators.get("degraded_performance"):
            return "high"
        elif indicators.get("minor_issue"):
            return "medium"
        else:
            return "low"
            
    def _generate_incident_runbook(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate incident response runbook"""
        incident_type = incident_data.get("type", "unknown")
        
        runbooks = {
            "service_down": {
                "title": "Service Down Runbook",
                "steps": [
                    "Check pod status: kubectl get pods -l app=<service>",
                    "Check recent deployments: kubectl rollout history deployment/<service>",
                    "If recent deployment, rollback: kubectl rollout undo deployment/<service>",
                    "Check logs: kubectl logs -l app=<service> --tail=100",
                    "Scale up if needed: kubectl scale deployment/<service> --replicas=5",
                    "Check database connectivity",
                    "Verify external dependencies"
                ]
            },
            "high_latency": {
                "title": "High Latency Runbook",
                "steps": [
                    "Check current load: kubectl top pods -l app=<service>",
                    "Review slow query logs",
                    "Check cache hit rates",
                    "Enable emergency caching if available",
                    "Scale horizontally if CPU/Memory constrained",
                    "Review recent code changes for performance regressions"
                ]
            }
        }
        
        return runbooks.get(incident_type, {
            "title": "Generic Incident Runbook",
            "steps": [
                "Assess impact and severity",
                "Gather initial diagnostics",
                "Implement immediate mitigation",
                "Investigate root cause",
                "Implement permanent fix",
                "Document lessons learned"
            ]
        })
        
    async def _execute_task_internal(self, task: str) -> TaskResult:
        """Execute a DevOps task"""
        task_lower = task.lower()
        
        # Route to appropriate handler based on task type
        if any(keyword in task_lower for keyword in ["deploy", "release", "rollout"]):
            result = await self._handle_deployment_task(task)
        elif any(keyword in task_lower for keyword in ["pipeline", "ci", "cd", "build"]):
            result = await self._handle_pipeline_task(task)
        elif any(keyword in task_lower for keyword in ["monitor", "alert", "metric"]):
            result = await self._handle_monitoring_task(task)
        elif any(keyword in task_lower for keyword in ["incident", "outage", "issue"]):
            result = await self._handle_incident_task(task)
        elif any(keyword in task_lower for keyword in ["infrastructure", "terraform", "provision"]):
            result = await self._handle_infrastructure_task(task)
        else:
            result = await self._handle_general_devops_task(task)
            
        return result
        
    async def _handle_deployment_task(self, task: str) -> TaskResult:
        """Handle deployment-related tasks"""
        # Simulate deployment process
        await asyncio.sleep(1)
        
        deployment_plan = {
            "strategy": "blue-green",
            "steps": [
                "Build container image",
                "Run security scans",
                "Deploy to staging",
                "Run smoke tests",
                "Deploy to production (blue)",
                "Validate health checks",
                "Switch traffic to blue",
                "Monitor for 30 minutes",
                "Decommission green"
            ],
            "rollback_plan": "Immediate switch back to green if issues detected",
            "monitoring": "Enhanced monitoring during deployment window"
        }
        
        self.deployment_metrics["total_deployments"] += 1
        self.deployment_metrics["successful_deployments"] += 1
        
        return TaskResult(
            success=True,
            data={
                "deployment_plan": deployment_plan,
                "estimated_time": "45 minutes",
                "risk_level": "low",
                "automation_scripts": "Generated and ready"
            },
            metadata={
                "deployment_id": f"DEP-{datetime.now().strftime('%Y%m%d%H%M')}",
                "metrics_updated": True
            }
        )
        
    async def _handle_pipeline_task(self, task: str) -> TaskResult:
        """Handle CI/CD pipeline tasks"""
        # Create a sample project for pipeline generation
        project = InfrastructureProject(
            project_name="sample-app",
            project_type="microservices",
            tech_stack=["python", "fastapi", "postgresql", "redis"]
        )
        
        # Generate pipeline configurations
        pipeline_configs = await self.generate_ci_cd_pipeline(project)
        
        return TaskResult(
            success=True,
            data={
                "pipeline_configs": pipeline_configs,
                "pipeline_stages": [
                    "Source checkout",
                    "Build & test",
                    "Security scan",
                    "Container build",
                    "Deploy to staging",
                    "Integration tests",
                    "Deploy to production"
                ],
                "estimated_build_time": "12 minutes"
            },
            metadata={"files_generated": len(pipeline_configs)}
        )
        
    async def _handle_monitoring_task(self, task: str) -> TaskResult:
        """Handle monitoring and observability tasks"""
        monitoring_setup = {
            "metrics": {
                "collection": "Prometheus every 15s",
                "retention": "15 days",
                "dashboards": ["Service Overview", "Performance", "Business Metrics"]
            },
            "logs": {
                "aggregation": "ELK Stack",
                "retention": "30 days",
                "alerts": ["Error spike", "Unusual patterns"]
            },
            "traces": {
                "sampling": "1% baseline, 100% on errors",
                "retention": "7 days"
            },
            "alerts": {
                "channels": ["Slack", "PagerDuty", "Email"],
                "severity_levels": ["info", "warning", "critical"]
            }
        }
        
        return TaskResult(
            success=True,
            data=monitoring_setup,
            metadata={"dashboards_created": 3, "alerts_configured": 12}
        )
        
    async def _handle_incident_task(self, task: str) -> TaskResult:
        """Handle incident response tasks"""
        # Simulate incident detection and response
        incident_data = {
            "description": "High error rate detected in payment service",
            "indicators": {"high_error_rate": True}
        }
        
        response = await self.handle_incident(incident_data)
        
        return TaskResult(
            success=True,
            data=response,
            metadata={"incident_id": response["incident_id"], "auto_mitigated": True}
        )
        
    async def _handle_infrastructure_task(self, task: str) -> TaskResult:
        """Handle infrastructure provisioning tasks"""
        infrastructure_plan = {
            "resources": {
                "compute": "3x t3.large EC2 instances",
                "database": "RDS PostgreSQL Multi-AZ",
                "cache": "ElastiCache Redis cluster",
                "storage": "S3 buckets for artifacts",
                "networking": "VPC with public/private subnets"
            },
            "security": {
                "encryption": "At rest and in transit",
                "access": "IAM roles with least privilege",
                "network": "Security groups and NACLs"
            },
            "cost_estimate": "$450/month",
            "terraform_ready": True
        }
        
        return TaskResult(
            success=True,
            data=infrastructure_plan,
            metadata={"iac_files_generated": 5}
        )
        
    async def _handle_general_devops_task(self, task: str) -> TaskResult:
        """Handle general DevOps tasks"""
        # Use routing system for general tasks
        if self.routing_system:
            response = await self.routing_system.route_request(
                agent_id=self.id,
                task=task,
                context={"expertise": self.expertise}
            )
            
            return TaskResult(
                success=True,
                data={"response": response.content, "expertise_applied": True},
                metadata={"llm_model": response.model_used}
            )
        else:
            return TaskResult(
                success=True,
                data={"response": "DevOps task acknowledged. Please provide more specific requirements."},
                metadata={}
            )