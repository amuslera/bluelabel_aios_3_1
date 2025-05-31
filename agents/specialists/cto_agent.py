"""
CTO Agent - Strategic technical leader and primary AI interface.

This agent serves as the bridge between you (the CEO) and the AI development team.
It handles strategic planning, architecture decisions, and team coordination.
"""

import json
import logging
from pathlib import Path
from typing import Any

from agents.base.agent import AgentConfig, BaseAgent, Task
from core.routing.llm_client import llm_factory
from core.routing.router import LLMRouter

logger = logging.getLogger(__name__)


class CTOAgent(BaseAgent):
    """
    Chief Technology Officer Agent

    Responsibilities:
    - Interface with CEO (you) for project requirements
    - Break down complex projects into manageable tasks
    - Make architectural decisions
    - Coordinate other agents
    - Review and approve technical solutions
    - Strategic planning and roadmap development
    """

    def __init__(
        self, agent_id: str | None = None, llm_router: LLMRouter | None = None
    ):
        # Create CTO-specific configuration
        config = AgentConfig(
            name="CTO Agent",
            description="Strategic technical leader and your primary AI interface",
            role="Chief Technology Officer",
            capabilities=[
                "project_planning",
                "architecture_design",
                "task_decomposition",
                "team_coordination",
                "strategic_decisions",
                "code_review",
                "technology_evaluation",
                "roadmap_planning",
            ],
            model_preferences={
                "primary": "claude-3-opus",
                "fallback": "claude-3-sonnet",
                "budget_mode": "gpt-4-turbo",
            },
            personality={
                "communication_style": "executive",
                "decision_making": "analytical",
                "leadership_style": "collaborative",
            },
        )

        super().__init__(agent_id=agent_id, config=config, llm_router=llm_router)

        # CTO-specific state
        self.current_projects: list[dict[str, Any]] = []
        self.team_members: list[str] = []  # Agent IDs of team members
        self.strategic_context = {
            "company_stage": "startup",
            "tech_stack_preferences": [],
            "architectural_principles": [],
            "current_priorities": [],
        }

    def can_handle_task(self, task: Task) -> bool:
        """
        CTO Agent can handle all task types, including general communication.

        Args:
            task: The task to check

        Returns:
            bool: Always True for CTO Agent
        """
        # CTO can handle any task type
        return True

    async def _execute_task_internal(self, task: Task, model_id: str) -> dict[str, Any]:
        """
        Execute CTO-specific tasks.

        Args:
            task: The task to execute
            model_id: The model to use for execution

        Returns:
            Dict[str, Any]: The task result
        """

        if task.type == "project_planning":
            return await self._handle_project_planning(task, model_id)
        elif task.type == "architecture_design":
            return await self._handle_architecture_design(task, model_id)
        elif task.type == "task_decomposition":
            return await self._handle_task_decomposition(task, model_id)
        elif task.type == "team_coordination":
            return await self._handle_team_coordination(task, model_id)
        elif task.type == "strategic_decision":
            return await self._handle_strategic_decision(task, model_id)
        elif task.type == "code_review":
            return await self._handle_code_review(task, model_id)
        elif task.type == "ceo_communication":
            return await self._handle_ceo_communication(task, model_id)
        else:
            return await self._handle_general_task(task, model_id)

    async def _handle_project_planning(
        self, task: Task, model_id: str
    ) -> dict[str, Any]:
        """Handle project planning tasks."""

        project_requirements = task.parameters.get("requirements", "")
        timeline = task.parameters.get("timeline", "")
        constraints = task.parameters.get("constraints", {})

        # Generate project plan using LLM
        prompt = f"""
        As the CTO of a startup, I need to create a comprehensive project plan.
        
        Project Requirements:
        {project_requirements}
        
        Timeline: {timeline}
        
        Constraints: {json.dumps(constraints, indent=2)}
        
        Please provide a detailed project plan including:
        1. Project overview and objectives
        2. Technical architecture recommendations
        3. Phase breakdown with milestones
        4. Resource requirements (team composition)
        5. Technology stack recommendations
        6. Risk assessment and mitigation strategies
        7. Success metrics and KPIs
        
        Format the response as structured JSON with clear sections.
        """

        # Here we would call the actual LLM
        # For now, return a structured response
        project_plan = {
            "project_id": f"proj_{task.id[:8]}",
            "overview": "Project plan generated successfully",
            "phases": [
                {
                    "name": "Discovery & Planning",
                    "duration": "1-2 weeks",
                    "deliverables": [
                        "Requirements analysis",
                        "Technical specifications",
                    ],
                },
                {
                    "name": "Architecture & Design",
                    "duration": "1 week",
                    "deliverables": [
                        "System architecture",
                        "Database design",
                        "API specifications",
                    ],
                },
                {
                    "name": "Development",
                    "duration": "4-6 weeks",
                    "deliverables": ["MVP implementation", "Testing", "Documentation"],
                },
                {
                    "name": "Launch & Iteration",
                    "duration": "2 weeks",
                    "deliverables": [
                        "Deployment",
                        "Monitoring",
                        "User feedback integration",
                    ],
                },
            ],
            "team_requirements": [
                {"role": "Backend Developer", "agent_type": "backend_agent"},
                {"role": "Frontend Developer", "agent_type": "frontend_agent"},
                {"role": "QA Engineer", "agent_type": "qa_agent"},
            ],
            "technology_stack": {
                "backend": "FastAPI + PostgreSQL",
                "frontend": "React + TypeScript",
                "deployment": "Docker + Kubernetes",
            },
            "risks": [
                {
                    "risk": "Timeline overrun",
                    "mitigation": "Agile methodology with regular checkpoints",
                },
                {
                    "risk": "Technical complexity",
                    "mitigation": "Proof of concept development",
                },
            ],
            "success_metrics": [
                "Functionality delivered on time",
                "Performance benchmarks met",
                "User satisfaction score > 4.0",
            ],
        }

        # Store project in memory
        self.current_projects.append(project_plan)

        return {
            "plan": project_plan,
            "recommendations": [
                "Start with MVP to validate core functionality",
                "Implement CI/CD pipeline from day one",
                "Regular stakeholder reviews every sprint",
            ],
            "next_steps": [
                "Create detailed user stories",
                "Set up development environment",
                "Recruit/assign team members",
            ],
        }

    async def _handle_architecture_design(
        self, task: Task, model_id: str
    ) -> dict[str, Any]:
        """Handle architecture design tasks."""

        requirements = task.parameters.get("requirements", "")
        scale_requirements = task.parameters.get("scale", "small")

        architecture = {
            "system_overview": "Microservices architecture with API gateway",
            "components": [
                {
                    "name": "API Gateway",
                    "purpose": "Request routing and authentication",
                    "technology": "Kong or FastAPI",
                },
                {
                    "name": "User Service",
                    "purpose": "User management and authentication",
                    "technology": "FastAPI + PostgreSQL",
                },
                {
                    "name": "Core Business Logic",
                    "purpose": "Main application functionality",
                    "technology": "FastAPI + Redis",
                },
                {
                    "name": "Frontend Application",
                    "purpose": "User interface",
                    "technology": "React + TypeScript",
                },
            ],
            "data_flow": "Client -> API Gateway -> Services -> Database",
            "deployment_strategy": "Containerized with Kubernetes",
            "scalability_considerations": [
                "Horizontal scaling of stateless services",
                "Database read replicas for performance",
                "CDN for static assets",
            ],
        }

        return {
            "architecture": architecture,
            "diagrams": "System diagrams would be generated here",
            "implementation_notes": [
                "Start with monolith, extract services as needed",
                "Use database per service pattern",
                "Implement distributed tracing from start",
            ],
        }

    async def _handle_task_decomposition(
        self, task: Task, model_id: str
    ) -> dict[str, Any]:
        """Break down complex tasks into smaller, manageable tasks."""

        high_level_task = task.parameters.get("task_description", "")

        # This would use LLM to intelligently break down tasks
        subtasks = [
            {
                "id": f"subtask_1_{task.id[:8]}",
                "title": "Setup Development Environment",
                "description": "Initialize project structure and dependencies",
                "assigned_to": "backend_agent",
                "priority": 10,
                "estimated_effort": "4 hours",
                "dependencies": [],
            },
            {
                "id": f"subtask_2_{task.id[:8]}",
                "title": "Database Design",
                "description": "Design database schema and relationships",
                "assigned_to": "backend_agent",
                "priority": 9,
                "estimated_effort": "6 hours",
                "dependencies": ["subtask_1"],
            },
            {
                "id": f"subtask_3_{task.id[:8]}",
                "title": "API Development",
                "description": "Implement REST API endpoints",
                "assigned_to": "backend_agent",
                "priority": 8,
                "estimated_effort": "12 hours",
                "dependencies": ["subtask_2"],
            },
            {
                "id": f"subtask_4_{task.id[:8]}",
                "title": "Frontend Components",
                "description": "Build React components for UI",
                "assigned_to": "frontend_agent",
                "priority": 7,
                "estimated_effort": "16 hours",
                "dependencies": ["subtask_3"],
            },
        ]

        return {
            "original_task": high_level_task,
            "subtasks": subtasks,
            "execution_order": [
                task["id"]
                for task in sorted(subtasks, key=lambda x: x["priority"], reverse=True)
            ],
            "total_estimated_effort": "38 hours",
            "critical_path": ["subtask_1", "subtask_2", "subtask_3", "subtask_4"],
        }

    async def _handle_team_coordination(
        self, task: Task, model_id: str
    ) -> dict[str, Any]:
        """Handle team coordination and management tasks."""

        coordination_type = task.parameters.get("type", "status_update")

        if coordination_type == "status_update":
            return await self._get_team_status()
        elif coordination_type == "task_assignment":
            return await self._assign_tasks(task.parameters)
        elif coordination_type == "conflict_resolution":
            return await self._resolve_conflicts(task.parameters)
        else:
            return {"message": "Coordination task completed", "type": coordination_type}

    async def _handle_strategic_decision(
        self, task: Task, model_id: str
    ) -> dict[str, Any]:
        """Handle strategic and architectural decisions."""

        decision_context = task.parameters.get("context", "")
        options = task.parameters.get("options", [])

        # This would use sophisticated reasoning via LLM
        decision = {
            "decision": "Option 1 selected based on strategic alignment",
            "reasoning": [
                "Better long-term scalability",
                "Lower technical debt accumulation",
                "Faster time to market",
            ],
            "implementation_plan": [
                "Phase 1: Proof of concept (1 week)",
                "Phase 2: Full implementation (3 weeks)",
                "Phase 3: Testing and optimization (1 week)",
            ],
            "success_criteria": [
                "Performance benchmarks met",
                "Developer satisfaction maintained",
                "Budget constraints respected",
            ],
        }

        return decision

    async def _handle_code_review(self, task: Task, model_id: str) -> dict[str, Any]:
        """Handle code review tasks."""

        code_content = task.parameters.get("code", "")
        review_type = task.parameters.get("review_type", "general")

        # This would use LLM for sophisticated code analysis
        review_result = {
            "overall_score": 8.5,
            "feedback": [
                {
                    "type": "improvement",
                    "line": 15,
                    "message": "Consider extracting this logic into a separate function",
                    "severity": "medium",
                },
                {
                    "type": "approval",
                    "message": "Good use of type hints and clear variable names",
                    "severity": "low",
                },
            ],
            "approval_status": "approved_with_suggestions",
            "next_steps": [
                "Address medium severity items",
                "Add unit tests for new functionality",
                "Update documentation",
            ],
        }

        return review_result

    async def _handle_ceo_communication(
        self, task: Task, model_id: str
    ) -> dict[str, Any]:
        """Handle communication with CEO (you)."""

        message_type = task.parameters.get("type", "chat")
        content = task.parameters.get("content", "")

        if message_type == "project_status":
            return await self._prepare_project_status_report()
        elif message_type == "technical_consultation":
            return await self._provide_technical_consultation(content)
        elif message_type == "resource_request":
            return await self._handle_resource_request(task.parameters)
        else:
            # General chat - use LLM
            try:
                # Check if CEO is asking about code/architecture review
                if any(
                    keyword in content.lower()
                    for keyword in [
                        "review",
                        "code",
                        "architecture",
                        "codebase",
                        "analyze",
                        "what does",
                    ]
                ):
                    # Read some key files to understand the codebase
                    code_context = self._analyze_codebase()

                    # Create a prompt with code context
                    prompt = f"""You are the CTO of AIOSv3. The CEO asked: {content}

Here's what I found in our codebase:
{code_context}

Be CONCISE and SPECIFIC about our actual code:
- Point out specific files and patterns you see
- Identify what's working well and what needs improvement
- Give concrete next steps
- Keep response under 3 short paragraphs
- Be direct - no corporate speak"""
                else:
                    # Regular conversation
                    prompt = f"""You are the CTO of AIOSv3, a startup building a modular AI agent platform.

CEO's message: {content}

Be CONCISE and ACTION-ORIENTED. Get to the point quickly. No fluff.
- Answer in 2-3 short paragraphs max
- Focus on what we should DO, not theory
- Be direct and practical
- Think like a technical co-founder who codes

Current context:
- We're building AIOSv3: a platform for AI agents that collaborate to build software
- We have: CTO Agent (you), with plans for Builder, Backend, Frontend, QA agents
- Key feature: LLM routing between cloud (Claude) and local models
- Tech stack: Python, FastAPI, LangChain, Docker/K8s
- Current status: Basic CTO agent working, need to build more agents"""

                # Get the appropriate LLM client
                provider = "anthropic" if "claude" in model_id else "openai"
                client = llm_factory.get_client(provider)

                # Call the LLM
                # Use the actual model ID from the config
                model_config = (
                    self.llm_router.models.get(model_id) if self.llm_router else None
                )
                actual_model_id = model_config.model_id if model_config else model_id

                llm_response = await client.generate(
                    prompt=prompt,
                    model=actual_model_id,
                    temperature=0.7,
                    max_tokens=1000,
                )

                # Parse the response to extract sections
                response_text = llm_response.content

                # Simple parsing - in production, use better parsing
                main_response = response_text.split("Key recommendations:")[0].strip()

                recommendations = []
                actions = []

                if "Key recommendations:" in response_text:
                    recs_section = response_text.split("Key recommendations:")[1]
                    if "Suggested immediate actions:" in recs_section:
                        recs_text = recs_section.split("Suggested immediate actions:")[
                            0
                        ]
                        actions_text = recs_section.split(
                            "Suggested immediate actions:"
                        )[1]

                        # Extract bullet points
                        recommendations = [
                            r.strip()
                            for r in recs_text.split("\n")
                            if r.strip().startswith("-") or r.strip().startswith("•")
                        ]
                        actions = [
                            a.strip()
                            for a in actions_text.split("\n")
                            if a.strip().startswith("-") or a.strip().startswith("•")
                        ]

                # Track cost
                if self.llm_router:
                    self.llm_router.track_cost(llm_response.cost_estimate)

                return {
                    "response": main_response,
                    "suggestions": [r.lstrip("- •") for r in recommendations],
                    "follow_up_actions": [a.lstrip("- •") for a in actions],
                    "model_used": model_id,
                    "cost": llm_response.cost_estimate,
                }

            except Exception as e:
                logger.error(f"Error calling LLM: {e}")
                return {
                    "response": f"I understand your request: '{content}'. Let me analyze this and provide a strategic recommendation.",
                    "suggestions": [
                        "Let's break this down into phases",
                        "We should start with a proof of concept",
                    ],
                    "follow_up_actions": [
                        "Define requirements",
                        "Research technology options",
                    ],
                    "error": str(e),
                }

    async def _handle_general_task(self, task: Task, model_id: str) -> dict[str, Any]:
        """Handle general tasks that don't fit specific categories."""

        return {
            "message": f"CTO Agent processed general task: {task.description}",
            "analysis": "Task completed successfully",
            "recommendations": [
                "Consider breaking down complex tasks for better tracking"
            ],
        }

    async def _get_team_status(self) -> dict[str, Any]:
        """Get current status of all team members."""

        team_status = {
            "team_size": len(self.team_members),
            "active_projects": len(self.current_projects),
            "overall_health": "good",
            "members": [
                {
                    "agent_id": member_id,
                    "status": "active",
                    "current_tasks": 2,
                    "utilization": "75%",
                }
                for member_id in self.team_members
            ],
        }

        return team_status

    async def _assign_tasks(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Assign tasks to team members."""

        tasks = parameters.get("tasks", [])
        assignments = []

        for task in tasks:
            # Simple assignment logic - would be more sophisticated
            best_agent = self._find_best_agent_for_task(task)
            assignments.append(
                {
                    "task_id": task.get("id"),
                    "assigned_to": best_agent,
                    "reasoning": f"Best match for {task.get('type', 'general')} tasks",
                }
            )

        return {"assignments": assignments}

    def _find_best_agent_for_task(self, task: dict[str, Any]) -> str:
        """Find the best agent for a given task."""

        task_type = task.get("type", "general")

        # Simple mapping - would be more sophisticated with actual agent capabilities
        type_mapping = {
            "backend": "backend_agent",
            "frontend": "frontend_agent",
            "testing": "qa_agent",
            "deployment": "devops_agent",
        }

        return type_mapping.get(task_type, "general_agent")

    async def _prepare_project_status_report(self) -> dict[str, Any]:
        """Prepare a comprehensive project status report for the CEO."""

        report = {
            "executive_summary": "All projects are progressing as planned",
            "projects": [
                {
                    "name": project.get("project_id", "Unknown"),
                    "status": "on_track",
                    "completion": "65%",
                    "next_milestone": "MVP completion",
                    "risks": ["None identified"],
                }
                for project in self.current_projects
            ],
            "team_performance": {
                "velocity": "above_target",
                "quality_metrics": "excellent",
                "morale": "high",
            },
            "recommendations": [
                "Continue current development pace",
                "Consider adding QA automation",
                "Plan for scaling team next quarter",
            ],
        }

        return report

    async def _provide_technical_consultation(self, query: str) -> dict[str, Any]:
        """Provide technical consultation on complex topics."""

        # This would use advanced LLM reasoning
        consultation = {
            "query": query,
            "analysis": "Technical analysis would be provided here using LLM",
            "recommendations": [
                "Option 1: Recommended approach",
                "Option 2: Alternative approach",
            ],
            "trade_offs": {
                "Option 1": {"pros": ["Fast", "Scalable"], "cons": ["Complex"]},
                "Option 2": {"pros": ["Simple"], "cons": ["Limited scalability"]},
            },
            "decision_framework": "Choose Option 1 for long-term growth",
        }

        return consultation

    def add_team_member(self, agent_id: str) -> None:
        """Add a new team member."""
        if agent_id not in self.team_members:
            self.team_members.append(agent_id)
            self.logger.info(f"Added {agent_id} to team")

    def remove_team_member(self, agent_id: str) -> None:
        """Remove a team member."""
        if agent_id in self.team_members:
            self.team_members.remove(agent_id)
            self.logger.info(f"Removed {agent_id} from team")

    def update_strategic_context(self, context_updates: dict[str, Any]) -> None:
        """Update the strategic context for decision making."""
        self.strategic_context.update(context_updates)
        self.logger.info("Strategic context updated")

    def get_project_summary(self) -> dict[str, Any]:
        """Get a summary of all current projects."""
        return {
            "total_projects": len(self.current_projects),
            "projects": [
                {
                    "id": project.get("project_id"),
                    "status": "active",  # Would be computed
                    "team_size": len(project.get("team_requirements", [])),
                }
                for project in self.current_projects
            ],
        }

    def _analyze_codebase(self) -> str:
        """Analyze key files in the codebase to understand the architecture."""
        analysis = []
        project_root = Path(__file__).parent.parent.parent  # Go up to project root

        # Key files to analyze
        key_files = [
            ("agents/base/agent.py", "Base Agent Architecture"),
            ("agents/specialists/cto_agent.py", "CTO Agent Implementation"),
            ("core/routing/router.py", "LLM Routing System"),
            ("core/routing/llm_client.py", "LLM Client Integration"),
            ("api/main.py", "API Server"),
            ("config/models.yaml", "Model Configuration"),
            ("config/agents.yaml", "Agent Configuration"),
        ]

        analysis.append("=== CODEBASE STRUCTURE ===")

        # Get directory structure
        for category in ["agents", "core", "api", "config"]:
            path = project_root / category
            if path.exists():
                files = [f.name for f in path.rglob("*.py") if f.is_file()][:5]
                analysis.append(f"\n{category}/: {', '.join(files)}")

        analysis.append("\n\n=== KEY COMPONENTS ===")

        # Read and summarize key files
        for file_path, description in key_files:
            full_path = project_root / file_path
            if full_path.exists():
                try:
                    with open(full_path) as f:
                        content = f.read()
                        lines = content.split("\n")

                        # Get imports and class definitions
                        imports = [
                            l
                            for l in lines
                            if l.startswith("import") or l.startswith("from")
                        ][:3]
                        classes = [
                            l.strip() for l in lines if l.strip().startswith("class ")
                        ][:2]

                        analysis.append(f"\n{file_path} ({description}):")
                        analysis.append(f"  - {len(lines)} lines")
                        if classes:
                            analysis.append(f"  - Classes: {', '.join(classes)}")
                        if "TODO" in content:
                            analysis.append("  - Has TODOs")
                except Exception:
                    analysis.append(f"\n{file_path}: Error reading file")

        # Summary stats
        py_files = list(project_root.rglob("*.py"))
        yaml_files = list(project_root.rglob("*.yaml"))

        analysis.append("\n\n=== PROJECT STATS ===")
        analysis.append(f"- Total Python files: {len(py_files)}")
        analysis.append(f"- Total YAML configs: {len(yaml_files)}")
        analysis.append(
            "- Main components: agents, core routing, API server, configurations"
        )

        return "\n".join(analysis)
