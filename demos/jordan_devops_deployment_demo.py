#!/usr/bin/env python3
"""
Jordan Kim DevOps Agent - Full Stack Deployment Demo

This demo showcases Jordan deploying a complete application built by
Marcus (backend), Emily (frontend), and tested by Alex (QA).

Jordan will:
1. Analyze the application requirements
2. Generate CI/CD pipelines
3. Provision infrastructure with Terraform
4. Set up monitoring and alerting
5. Deploy the application with zero downtime
6. Handle a simulated incident
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add project root to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.specialists.devops_agent import JordanDevOpsAgent, InfrastructureProject
from src.agents.specialists.cicd_manager import CICDManager, PipelineConfig
from src.agents.specialists.infrastructure_manager import InfrastructureManager, InfrastructureSpec
from src.agents.specialists.monitoring_manager import MonitoringManager, MonitoringSpec
from src.core.messaging.queue import MessageQueue

console = Console()


class DevOpsDemo:
    """Orchestrates the DevOps deployment demonstration"""
    
    def __init__(self):
        self.jordan = JordanDevOpsAgent()
        self.console = console
        self.deployment_stages = []
        
    async def run(self):
        """Run the complete DevOps demonstration"""
        self.console.print(Panel.fit(
            "[bold cyan]Jordan Kim - DevOps Engineering Agent[/bold cyan]\n"
            "[yellow]'If it's not automated, it's broken'[/yellow]",
            title="🚀 DevOps Deployment Demo"
        ))
        
        # Introduction
        await self.introduction()
        
        # Stage 1: Receive application from team
        await self.receive_application()
        
        # Stage 2: Analyze infrastructure needs
        await self.analyze_infrastructure()
        
        # Stage 3: Generate CI/CD pipelines
        await self.generate_pipelines()
        
        # Stage 4: Provision infrastructure
        await self.provision_infrastructure()
        
        # Stage 5: Setup monitoring
        await self.setup_monitoring()
        
        # Stage 6: Deploy application
        await self.deploy_application()
        
        # Stage 7: Simulate incident response
        await self.handle_incident()
        
        # Summary
        await self.summary()
        
    async def introduction(self):
        """Jordan introduces himself"""
        greeting = self.jordan.personality.get_greeting()
        self.console.print(f"\n[green]{greeting}[/green]")
        
        await asyncio.sleep(1)
        
        self.console.print(
            f"\n[cyan]I'm Jordan Kim, your DevOps engineer. Former Netflix SRE, "
            f"Kubernetes contributor, and automation enthusiast.[/cyan]"
        )
        
        philosophy = self.jordan.personality.get_philosophy()
        self.console.print(f"\n[yellow]My philosophy: {philosophy}[/yellow]")
        
        await asyncio.sleep(2)
        
    async def receive_application(self):
        """Receive application details from the team"""
        self.console.print("\n[bold]📦 Stage 1: Receiving Application from Team[/bold]\n")
        
        # Simulate receiving messages from team
        messages = [
            ("Marcus Chen", "Backend API is ready! FastAPI with PostgreSQL, fully tested."),
            ("Emily Rodriguez", "Frontend React app complete with responsive design!"),
            ("Alex Thompson", "All tests passing! 95% coverage achieved.")
        ]
        
        for agent, message in messages:
            self.console.print(f"[blue]{agent}:[/blue] {message}")
            await asyncio.sleep(1)
            
            # Jordan's response
            response = self.jordan.personality.get_collaboration_comment(agent)
            self.console.print(f"[green]Jordan:[/green] {response}\n")
            await asyncio.sleep(1)
            
        self.console.print("[cyan]Jordan: Alright team, let me set up the infrastructure and deployment pipeline![/cyan]")
        await asyncio.sleep(2)
        
    async def analyze_infrastructure(self):
        """Analyze infrastructure requirements"""
        self.console.print("\n[bold]🔍 Stage 2: Analyzing Infrastructure Requirements[/bold]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Analyzing application architecture...", total=None)
            
            project_spec = {
                "name": "taskmaster-pro",
                "type": "web",
                "indicators": {
                    "multiple_services": True,
                    "high_traffic": True,
                    "requires_database": True,
                    "requires_cache": True
                }
            }
            
            analysis = await self.jordan.analyze_infrastructure_needs(project_spec)
            await asyncio.sleep(2)
            
        # Display analysis results
        table = Table(title="Infrastructure Analysis")
        table.add_column("Component", style="cyan")
        table.add_column("Recommendation", style="green")
        
        table.add_row("Project Type", analysis["project_type"])
        table.add_row("Orchestration", analysis["recommended_stack"].get("orchestration", "Kubernetes"))
        table.add_row("CI/CD", analysis["recommended_stack"].get("ci_cd", "GitLab CI"))
        table.add_row("Monitoring", analysis["recommended_stack"].get("monitoring", "Prometheus + Grafana"))
        table.add_row("Storage", analysis["recommended_stack"].get("storage", "PostgreSQL + Redis"))
        
        self.console.print(table)
        
        self.console.print(f"\n[green]Jordan: {self.jordan.personality.get_work_comment('infrastructure')}[/green]")
        await asyncio.sleep(2)
        
    async def generate_pipelines(self):
        """Generate CI/CD pipelines"""
        self.console.print("\n[bold]🔧 Stage 3: Generating CI/CD Pipelines[/bold]\n")
        
        project = InfrastructureProject(
            project_name="taskmaster-pro",
            project_type="microservices",
            tech_stack=["python", "javascript", "react", "fastapi"],
            environments=["dev", "staging", "prod"]
        )
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Generating CI/CD configurations...", total=None)
            
            templates = await self.jordan.generate_ci_cd_pipeline(project)
            await asyncio.sleep(2)
            
        # Display generated files
        self.console.print("[bold]Generated Pipeline Configurations:[/bold]")
        for filename in templates.keys():
            self.console.print(f"  ✅ {filename}")
            
        # Show a sample pipeline
        self.console.print("\n[bold]Sample GitHub Actions Workflow:[/bold]")
        sample = templates.get("github_actions", "")[:500] + "..."
        self.console.print(Panel(sample, title=".github/workflows/ci-cd.yml"))
        
        comment = self.jordan.personality.get_work_comment("deploy")
        self.console.print(f"\n[green]Jordan: {comment}[/green]")
        await asyncio.sleep(2)
        
    async def provision_infrastructure(self):
        """Provision cloud infrastructure"""
        self.console.print("\n[bold]☁️ Stage 4: Provisioning Infrastructure[/bold]\n")
        
        spec = InfrastructureSpec(
            project_name="taskmaster-pro",
            environment="prod",
            cloud_provider="aws",
            region="us-east-1",
            compute_type="kubernetes",
            min_nodes=3,
            max_nodes=10,
            database_type="postgres",
            database_ha=True,
            enable_monitoring=True
        )
        
        manager = InfrastructureManager()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            tasks = [
                "Creating VPC and networking...",
                "Provisioning EKS cluster...",
                "Setting up RDS database...",
                "Configuring security groups...",
                "Installing cluster addons..."
            ]
            
            for task_desc in tasks:
                task = progress.add_task(task_desc, total=None)
                await asyncio.sleep(1.5)
                progress.remove_task(task)
                self.console.print(f"  ✅ {task_desc.replace('...', '')} - Complete")
                
        # Show infrastructure summary
        table = Table(title="Infrastructure Summary")
        table.add_column("Resource", style="cyan")
        table.add_column("Details", style="green")
        
        table.add_row("Kubernetes Cluster", "EKS with 3-10 nodes (auto-scaling)")
        table.add_row("Database", "RDS PostgreSQL Multi-AZ")
        table.add_row("Load Balancer", "Application Load Balancer")
        table.add_row("Monitoring", "Prometheus + Grafana")
        table.add_row("Estimated Cost", "$450/month")
        
        self.console.print("\n")
        self.console.print(table)
        
        self.console.print(f"\n[green]Jordan: Infrastructure provisioned! {self.jordan.personality.get_success_comment()}[/green]")
        await asyncio.sleep(2)
        
    async def setup_monitoring(self):
        """Setup monitoring and alerting"""
        self.console.print("\n[bold]📊 Stage 5: Setting Up Monitoring & Observability[/bold]\n")
        
        project = InfrastructureProject(
            project_name="taskmaster-pro",
            project_type="microservices",
            tech_stack=["python", "javascript"]
        )
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            tasks = [
                ("Installing Prometheus...", 1.5),
                ("Configuring Grafana dashboards...", 2),
                ("Setting up alerting rules...", 1),
                ("Deploying ELK stack...", 2),
                ("Configuring distributed tracing...", 1.5)
            ]
            
            for task_desc, duration in tasks:
                task = progress.add_task(task_desc, total=None)
                await asyncio.sleep(duration)
                progress.remove_task(task)
                self.console.print(f"  ✅ {task_desc.replace('...', '')} - Complete")
                
        # Show monitoring setup
        monitoring_config = await self.jordan.setup_monitoring(project)
        
        self.console.print("\n[bold]Monitoring Configuration:[/bold]")
        self.console.print(f"  📈 Metrics: Prometheus with {monitoring_config['metrics']['prometheus']['scrape_interval']} scrape interval")
        self.console.print(f"  📊 Dashboards: {len(monitoring_config['metrics']['grafana_dashboards'])} Grafana dashboards")
        self.console.print(f"  🚨 Alerts: {len(monitoring_config['alerting']['rules'])} alerting rules")
        self.console.print(f"  📝 Logs: ELK stack with structured logging")
        self.console.print(f"  🔍 Tracing: Jaeger with distributed tracing")
        
        # Show SLOs
        self.console.print("\n[bold]Service Level Objectives:[/bold]")
        for slo in monitoring_config['slos']:
            self.console.print(f"  • {slo['name']}: {slo['target']}{'%' if slo['name'] == 'Availability' else 'ms' if 'Latency' in slo['name'] else '%'}")
            
        comment = self.jordan.personality.get_work_comment("monitor")
        self.console.print(f"\n[green]Jordan: {comment}[/green]")
        await asyncio.sleep(2)
        
    async def deploy_application(self):
        """Deploy the application"""
        self.console.print("\n[bold]🚀 Stage 6: Deploying Application[/bold]\n")
        
        # Update deployment metrics
        self.jordan.personality.update_metrics({"deployment_success": True})
        
        deployment_stages = [
            ("Building Docker images...", "✅ Images built and pushed to registry"),
            ("Running database migrations...", "✅ Database schema updated"),
            ("Deploying to staging environment...", "✅ Staging deployment successful"),
            ("Running smoke tests...", "✅ All smoke tests passed"),
            ("Promoting to production (Blue-Green)...", "✅ Blue environment ready"),
            ("Switching traffic to blue...", "✅ Traffic switched with zero downtime"),
            ("Monitoring deployment health...", "✅ All health checks passing")
        ]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            for stage, result in deployment_stages:
                task = progress.add_task(stage, total=None)
                await asyncio.sleep(1.5)
                progress.remove_task(task)
                self.console.print(f"  {result}")
                
        # Show deployment summary
        self.console.print("\n[bold green]Deployment Complete! 🎉[/bold green]")
        
        table = Table(title="Deployment Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Deployment Strategy", "Blue-Green")
        table.add_row("Downtime", "0 seconds")
        table.add_row("Rollback Time", "< 30 seconds")
        table.add_row("Health Status", "All services healthy")
        table.add_row("Response Time", "p99: 45ms")
        
        self.console.print(table)
        
        success_comment = self.jordan.personality.get_success_comment()
        self.console.print(f"\n[green]Jordan: {success_comment}[/green]")
        
        # Update metrics
        self.jordan.deployment_metrics["total_deployments"] += 1
        self.jordan.deployment_metrics["successful_deployments"] += 1
        
        await asyncio.sleep(2)
        
    async def handle_incident(self):
        """Simulate and handle an incident"""
        self.console.print("\n[bold]🚨 Stage 7: Incident Response Simulation[/bold]\n")
        
        await asyncio.sleep(1)
        
        self.console.print("[bold red]ALERT: High error rate detected in production![/bold red]")
        
        # Update incident metrics
        self.jordan.personality.update_metrics({"incident_started": True})
        
        incident_data = {
            "description": "API response times degraded, error rate at 5%",
            "indicators": {
                "high_error_rate": True,
                "degraded_performance": True
            }
        }
        
        response = await self.jordan.handle_incident(incident_data)
        
        self.console.print(f"\n[yellow]Jordan: {self.jordan.personality.get_work_comment('incident')}[/yellow]")
        
        # Show incident response
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            for step in response["mitigation_steps"]:
                task = progress.add_task(step, total=None)
                await asyncio.sleep(1)
                progress.remove_task(task)
                self.console.print(f"  ✅ {step}")
                
        # Resolution
        self.console.print("\n[bold green]Incident Resolved![/bold green]")
        self.console.print(f"  • Root Cause: Memory leak in API service")
        self.console.print(f"  • Resolution: Rolled back to previous version")
        self.console.print(f"  • MTTR: 15 minutes")
        self.console.print(f"  • Impact: 0.1% of requests affected")
        
        # Update metrics
        self.jordan.personality.update_metrics({"incident_resolved": True})
        
        self.console.print(f"\n[green]Jordan: Incident resolved! Creating post-mortem document and updating runbooks.[/green]")
        await asyncio.sleep(2)
        
    async def summary(self):
        """Show deployment summary"""
        self.console.print("\n[bold]📋 Deployment Summary[/bold]\n")
        
        # Final metrics
        table = Table(title="DevOps Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Deployments", str(self.jordan.deployment_metrics["total_deployments"]))
        table.add_row("Success Rate", "100%")
        table.add_row("System Uptime", f"{self.jordan.personality.devops_metrics.system_uptime}%")
        table.add_row("Automation Coverage", f"{self.jordan.personality.devops_metrics.automation_coverage}%")
        table.add_row("MTTR", "15 minutes")
        table.add_row("Infrastructure Cost", "$450/month")
        
        self.console.print(table)
        
        # Files generated
        self.console.print("\n[bold]Generated Artifacts:[/bold]")
        artifacts = [
            "CI/CD Pipelines (GitHub Actions, GitLab CI, Jenkins)",
            "Infrastructure as Code (Terraform modules)",
            "Kubernetes manifests (Deployments, Services, ConfigMaps)",
            "Monitoring configuration (Prometheus, Grafana, Alerts)",
            "Documentation (README, runbooks, architecture diagrams)"
        ]
        
        for artifact in artifacts:
            self.console.print(f"  📄 {artifact}")
            
        # Final thoughts
        philosophy = self.jordan.personality.get_philosophy()
        self.console.print(f"\n[yellow]Jordan's Final Thought: {philosophy}[/yellow]")
        
        self.console.print("\n[bold green]Deployment complete! The application is live with full observability and zero-downtime deployment capability.[/bold green]")
        
        # Sign off
        self.console.print(f"\n[cyan]Jordan: Great work team! Remember - if it's not automated, we'll automate it next sprint! 🚀[/cyan]")


async def main():
    """Run the DevOps deployment demonstration"""
    demo = DevOpsDemo()
    
    try:
        await demo.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error during demo: {e}[/red]")
        raise


if __name__ == "__main__":
    asyncio.run(main())