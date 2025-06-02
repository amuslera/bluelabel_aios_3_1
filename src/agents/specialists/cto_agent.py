"""
CTO Agent - Chief Technology Officer specializing in architectural decisions and technical leadership.

This agent leverages the Enhanced BaseAgent framework to provide:
- System architecture design and evaluation
- Technology stack recommendations 
- Code review and quality assessment
- Strategic technical planning and roadmap guidance
- Technical decision-making and documentation
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

from src.agents.base.enhanced_agent import (
    EnhancedBaseAgent, 
    EnhancedAgentConfig, 
    EnhancedTask, 
    EnhancedTaskResult,
    AgentCapability
)
from src.agents.base.types import AgentType, TaskType
from src.core.routing.router import RoutingContext, RoutingStrategy
from src.core.routing.providers.base import LLMResponse


class CTOAgentConfig(EnhancedAgentConfig):
    """Enhanced configuration for CTO Agent with specialized settings."""
    
    def __init__(self, **kwargs):
        # Set CTO-specific defaults
        defaults = {
            "agent_type": AgentType.CTO,
            "name": "AIOSv3 CTO Agent",
            "description": "Chief Technology Officer agent specializing in architectural decisions, technical leadership, and strategic planning",
            "capabilities": [
                AgentCapability.ARCHITECTURE_DESIGN,
                AgentCapability.CODE_REVIEW,
                AgentCapability.PROJECT_MANAGEMENT
            ],
            "default_routing_strategy": RoutingStrategy.PERFORMANCE_OPTIMIZED,
            "max_tokens": 4096,
            "temperature": 0.3,  # Lower temperature for more consistent technical decisions
            "health_check_interval": 20
        }
        # Override with provided kwargs
        defaults.update(kwargs)
        super().__init__(**defaults)


class CTOAgent(EnhancedBaseAgent):
    """
    Chief Technology Officer Agent for technical leadership and architectural decisions.
    
    Specializes in:
    - System architecture design and evaluation
    - Technology stack selection and recommendations
    - Code review with architectural perspective
    - Technical strategy and roadmap planning
    - Engineering best practices and standards
    - Risk assessment and mitigation strategies
    """
    
    def __init__(self, config: Optional[CTOAgentConfig] = None):
        """Initialize CTO Agent with specialized configuration."""
        if config is None:
            config = CTOAgentConfig()
        
        super().__init__(config)
        
        # CTO-specific knowledge areas
        self.expertise_areas = [
            "system_architecture",
            "microservices", 
            "cloud_platforms",
            "scalability",
            "performance",
            "security",
            "devops",
            "team_leadership",
            "technical_strategy"
        ]
        
        # Decision frameworks
        self.decision_frameworks = {
            "architecture": [
                "scalability_requirements",
                "performance_needs", 
                "team_expertise",
                "operational_complexity",
                "cost_considerations",
                "future_flexibility"
            ],
            "technology": [
                "technical_fit",
                "team_familiarity",
                "ecosystem_maturity",
                "performance_characteristics",
                "maintenance_burden",
                "vendor_risk"
            ]
        }
    
    async def _on_initialize(self) -> None:
        """CTO Agent initialization - load architectural knowledge."""
        # Store CTO expertise in knowledge base
        await self.store_knowledge(
            content="CTO Agent specialized in system architecture, technical leadership, and strategic planning",
            category="agent_identity",
            keywords=["cto", "architecture", "leadership", "strategy"]
        )
        
        # Store architectural principles
        principles = """
        Key Architectural Principles:
        1. Scalability: Design for 10x growth
        2. Reliability: Plan for failure scenarios
        3. Maintainability: Code for the team, not just the individual
        4. Performance: Measure, don't guess
        5. Security: Build it in from the start
        6. Cost-effectiveness: Optimize for business value
        """
        
        await self.store_knowledge(
            content=principles,
            category="architectural_principles",
            keywords=["architecture", "principles", "best_practices"]
        )
    
    async def _on_shutdown(self) -> None:
        """CTO Agent shutdown - save decision context."""
        # Could save current architectural decisions or recommendations
        pass
    
    async def _process_response(self, response: LLMResponse, task: EnhancedTask) -> str:
        """Process and structure CTO Agent responses for clarity and actionability."""
        content = response.content
        
        # Structure different types of CTO responses
        if task.task_type == TaskType.SYSTEM_DESIGN:
            return self._format_architecture_response(content, task)
        elif task.task_type == TaskType.CODE_REVIEW:
            return self._format_code_review_response(content, task)
        elif task.task_type == TaskType.TECH_DECISION:
            return self._format_decision_response(content, task)
        elif task.task_type == TaskType.PLANNING:
            return self._format_strategy_response(content, task)
        else:
            return self._format_general_response(content, task)
    
    def _format_architecture_response(self, content: str, task: EnhancedTask) -> str:
        """Format architectural design responses with clear structure."""
        return f"""# 🏗️ Architectural Analysis

## Executive Summary
{self._extract_summary(content)}

## Technical Recommendation
{content}

## Implementation Considerations
- **Scalability**: How this scales with growth
- **Performance**: Expected performance characteristics  
- **Operational**: Deployment and maintenance considerations
- **Cost**: Resource and operational cost implications

## Next Steps
{self._extract_next_steps(content)}

---
*CTO Agent Analysis | {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    def _format_code_review_response(self, content: str, task: EnhancedTask) -> str:
        """Format code review responses with actionable feedback."""
        return f"""# 🔍 CTO Code Review

## Overall Assessment
{self._extract_summary(content)}

## Detailed Analysis
{content}

## Architecture Impact
- **Design Patterns**: Alignment with architectural patterns
- **Scalability**: Impact on system scalability
- **Maintainability**: Long-term maintenance considerations
- **Technical Debt**: Potential debt introduction or reduction

## Recommendations
{self._extract_recommendations(content)}

---
*CTO Code Review | {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    def _format_decision_response(self, content: str, task: EnhancedTask) -> str:
        """Format technology decisions with clear rationale."""
        return f"""# ⚖️ Technical Decision Analysis

## Decision Context
{task.prompt}

## Recommendation
{self._extract_summary(content)}

## Analysis
{content}

## Decision Matrix
- **Technical Fit**: How well it solves the problem
- **Team Readiness**: Current team capability and learning curve
- **Ecosystem**: Community, tools, and long-term viability
- **Risk Assessment**: Technical and business risks
- **Cost-Benefit**: Investment vs. expected returns

## Implementation Plan
{self._extract_next_steps(content)}

---
*CTO Decision | {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    def _format_strategy_response(self, content: str, task: EnhancedTask) -> str:
        """Format strategic planning responses."""
        return f"""# 🎯 Technical Strategy & Planning

## Strategic Context
{task.prompt}

## Strategic Recommendation
{self._extract_summary(content)}

## Detailed Strategy
{content}

## Success Metrics
- **Technical**: How we measure technical success
- **Business**: Business value and impact
- **Team**: Team capability and satisfaction
- **Operational**: System reliability and performance

## Roadmap
{self._extract_next_steps(content)}

---
*CTO Strategy | {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    def _format_general_response(self, content: str, task: EnhancedTask) -> str:
        """Format general CTO responses."""
        return f"""# 🎯 CTO Analysis

{content}

## Key Takeaways
{self._extract_summary(content)}

## Recommended Actions
{self._extract_recommendations(content)}

---
*CTO Agent | {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    def _extract_summary(self, content: str) -> str:
        """Extract or generate executive summary from response."""
        # Look for summary sections in the content
        summary_patterns = [
            r"(?:## Summary|# Summary|Summary:)(.*?)(?=\n#|\n##|\Z)",
            r"(?:## Executive Summary|# Executive Summary)(.*?)(?=\n#|\n##|\Z)",
            r"(?:In summary|To summarize)(.*?)(?=\n|\Z)"
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no explicit summary, take first substantial paragraph
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        return paragraphs[0] if paragraphs else "Analysis provided above."
    
    def _extract_recommendations(self, content: str) -> str:
        """Extract recommendations from response."""
        recommendation_patterns = [
            r"(?:## Recommendations|# Recommendations|Recommendations:)(.*?)(?=\n#|\n##|\Z)",
            r"(?:## Action Items|# Action Items)(.*?)(?=\n#|\n##|\Z)",
            r"(?:I recommend|My recommendation)(.*?)(?=\n|\Z)"
        ]
        
        for pattern in recommendation_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Look for bullet points or numbered lists
        lines = content.split('\n')
        recommendations = []
        for line in lines:
            if re.match(r'^\s*[\d\-\*]\s*', line):
                recommendations.append(line.strip())
        
        return '\n'.join(recommendations) if recommendations else "See detailed analysis above."
    
    def _extract_next_steps(self, content: str) -> str:
        """Extract next steps from response."""
        next_steps_patterns = [
            r"(?:## Next Steps|# Next Steps|Next steps:)(.*?)(?=\n#|\n##|\Z)",
            r"(?:## Implementation|# Implementation)(.*?)(?=\n#|\n##|\Z)",
            r"(?:Moving forward|Next, we should)(.*?)(?=\n|\Z)"
        ]
        
        for pattern in next_steps_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "1. Review and validate recommendations\n2. Create implementation plan\n3. Begin execution with team"
    
    async def _customize_prompt(self, task: EnhancedTask, context: str) -> str:
        """Customize prompts with CTO-specific expertise and frameworks."""
        
        # Build CTO-specific context
        cto_context = f"""
You are the CTO (Chief Technology Officer) of AIOSv3, a cutting-edge AI agent platform. Your expertise includes:

**Core Competencies:**
- System architecture and design patterns
- Technology evaluation and selection
- Engineering leadership and best practices
- Scalability and performance optimization
- Risk assessment and mitigation
- Strategic technical planning

**Current Project Context:**
AIOSv3 is a modular AI agent platform with:
- Enhanced BaseAgent framework with lifecycle management
- Intelligent LLM routing for cost optimization
- Redis-based memory and context management
- Agent registry and discovery system
- RabbitMQ-based inter-agent communication
- Docker/Kubernetes deployment architecture

**Decision Framework:**
When making recommendations, consider:
1. **Technical Excellence**: Best practices, maintainability, scalability
2. **Business Value**: ROI, time-to-market, competitive advantage
3. **Team Capability**: Current skills, learning curve, team growth
4. **Risk Management**: Technical debt, vendor lock-in, operational complexity
5. **Future Flexibility**: Ability to adapt and evolve

**Communication Style:**
- Provide clear, actionable recommendations
- Include rationale and trade-offs
- Consider both technical and business perspectives
- Be decisive but acknowledge uncertainties
- Structure responses for easy consumption by technical teams
"""

        # Task-specific guidance
        task_guidance = {
            TaskType.SYSTEM_DESIGN: """
Focus on:
- Architectural patterns and principles
- Scalability and performance considerations
- Technology stack recommendations
- Integration patterns and data flow
- Operational and maintenance implications
""",
            TaskType.CODE_REVIEW: """
Focus on:
- Architectural alignment and patterns
- Code quality and maintainability
- Performance and scalability impact
- Security and best practices
- Technical debt considerations
""",
            TaskType.TECH_DECISION: """
Focus on:
- Technology evaluation criteria
- Pros/cons analysis with business context
- Risk assessment and mitigation
- Implementation complexity and timeline
- Long-term strategic alignment
""",
            TaskType.PLANNING: """
Focus on:
- Strategic technical roadmap
- Resource allocation and prioritization
- Team capability development
- Risk mitigation strategies
- Success metrics and milestones
"""
        }
        
        guidance = task_guidance.get(task.task_type, """
Provide thoughtful technical leadership perspective on this request.
""")
        
        return f"""{cto_context}

{guidance}

**Task Complexity**: {task.complexity}/10
**Privacy Sensitive**: {task.privacy_sensitive}
**Context**: {context if context else "No additional context provided"}

Please provide your analysis and recommendations as the CTO."""


# Factory function for easy CTO Agent creation
async def create_cto_agent(custom_config: Optional[Dict[str, Any]] = None) -> CTOAgent:
    """Create and initialize a CTO Agent with optional custom configuration."""
    
    config_params = custom_config or {}
    config = CTOAgentConfig(**config_params)
    
    agent = CTOAgent(config)
    await agent.initialize()
    
    return agent


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_cto_agent():
        """Test CTO Agent functionality."""
        
        # Create CTO Agent
        cto = await create_cto_agent()
        
        # Test architectural decision task
        architecture_task = EnhancedTask(
            task_type=TaskType.SYSTEM_DESIGN,
            prompt="Should we implement microservices or keep our current monolithic architecture for AIOSv3? We expect 10x growth in the next year.",
            complexity=8,
            metadata={
                "current_architecture": "modular monolith",
                "team_size": 5,
                "expected_growth": "10x",
                "timeline": "6 months"
            }
        )
        
        print("🏗️ Testing CTO Agent - Architecture Decision")
        result = await cto.process_task(architecture_task)
        print(f"Success: {result.success}")
        print(f"Cost: ${result.cost:.4f}")
        print(f"Execution time: {result.execution_time:.2f}s")
        print(f"Model used: {result.model_used}")
        print("\n" + "="*80)
        print(result.output)
        
        # Test technology decision
        tech_task = EnhancedTask(
            task_type=TaskType.TECH_DECISION,
            prompt="What's the best approach for implementing real-time collaboration between agents - WebSockets, Server-Sent Events, or polling?",
            complexity=6,
            metadata={
                "use_case": "real-time agent collaboration",
                "scale": "100+ concurrent agents",
                "latency_requirements": "sub-second"
            }
        )
        
        print("\n\n⚖️ Testing CTO Agent - Technology Decision")
        result = await cto.process_task(tech_task)
        print(f"Success: {result.success}")
        print(f"Cost: ${result.cost:.4f}")
        print(f"Output length: {len(result.output)} chars")
        print("\n" + "="*80)
        print(result.output[:500] + "..." if len(result.output) > 500 else result.output)
        
        # Get agent status
        status = cto.get_status()
        print(f"\n📊 CTO Agent Status:")
        print(f"Tasks completed: {status['tasks_completed']}")
        print(f"Success rate: {status['success_rate']:.1%}")
        print(f"Total cost: ${status['total_cost']:.4f}")
        
        await cto.stop()
    
    # Run test
    # asyncio.run(test_cto_agent())