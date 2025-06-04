#!/usr/bin/env python3
"""
ProjectBrief data structure for agent handoff.
Transforms Hermes conversations into structured development plans.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any
from uuid import uuid4


class ProjectType(Enum):
    """Types of projects we can build."""
    WEB_APP = "web_application"
    API_SERVICE = "api_service"
    AUTOMATION = "automation_workflow"
    DATA_PIPELINE = "data_pipeline"
    MOBILE_APP = "mobile_application"
    INTEGRATION = "system_integration"
    ANALYTICS = "analytics_dashboard"
    UNKNOWN = "unknown"


class Priority(Enum):
    """Task priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TechnologyStack(Enum):
    """Common technology stacks."""
    MERN = "MongoDB, Express, React, Node.js"
    LAMP = "Linux, Apache, MySQL, PHP"
    MEAN = "MongoDB, Express, Angular, Node.js"
    DJANGO = "Django, PostgreSQL, React"
    FASTAPI = "FastAPI, PostgreSQL, Vue"
    SERVERLESS = "AWS Lambda, DynamoDB, React"
    CUSTOM = "Custom Stack"


@dataclass
class UserRequirement:
    """A single user requirement extracted from conversation."""
    id: str = field(default_factory=lambda: str(uuid4())[:8])
    description: str = ""
    category: str = ""  # functional, non-functional, constraint
    priority: Priority = Priority.MEDIUM
    source_message: str = ""  # Which user message this came from
    confidence: float = 0.8  # How confident we are about this requirement


@dataclass
class AcceptanceCriteria:
    """Acceptance criteria for a feature or requirement."""
    id: str = field(default_factory=lambda: str(uuid4())[:8])
    requirement_id: str = ""
    description: str = ""
    testable: bool = True
    automated_test_possible: bool = True


@dataclass
class TechnicalSpecification:
    """Technical details extracted from requirements."""
    backend_requirements: List[str] = field(default_factory=list)
    frontend_requirements: List[str] = field(default_factory=list)
    database_needs: List[str] = field(default_factory=list)
    api_endpoints: List[str] = field(default_factory=list)
    integrations: List[str] = field(default_factory=list)
    security_requirements: List[str] = field(default_factory=list)
    performance_requirements: List[str] = field(default_factory=list)
    suggested_stack: TechnologyStack = TechnologyStack.CUSTOM


@dataclass
class Timeline:
    """Project timeline and milestones."""
    estimated_duration_days: int = 14
    phases: List[Dict[str, Any]] = field(default_factory=list)
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    delivery_date: Optional[datetime] = None
    is_urgent: bool = False


@dataclass
class ProjectBrief:
    """
    Complete project brief generated from Hermes conversation.
    This is the handoff document from Hermes to the specialist agents.
    """
    # Metadata
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    session_id: str = ""  # From Hermes conversation
    
    # Project basics
    name: str = "Untitled Project"
    description: str = ""
    project_type: ProjectType = ProjectType.UNKNOWN
    priority: Priority = Priority.MEDIUM
    
    # User information
    user_persona: str = ""  # business, developer, startup, etc.
    user_technical_level: str = "non-technical"  # non-technical, basic, intermediate, advanced
    user_industry: str = ""
    
    # Requirements
    requirements: List[UserRequirement] = field(default_factory=list)
    acceptance_criteria: List[AcceptanceCriteria] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)  # budget, timeline, tech stack
    
    # Technical specifications
    technical_spec: TechnicalSpecification = field(default_factory=TechnicalSpecification)
    
    # Timeline
    timeline: Timeline = field(default_factory=Timeline)
    
    # Budget (if mentioned)
    budget_range: Optional[str] = None
    budget_flexible: bool = True
    
    # Additional context
    similar_products: List[str] = field(default_factory=list)  # "like Uber for..."
    key_features: List[str] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)
    
    # Agent assignments (filled by orchestrator)
    assigned_agents: Dict[str, List[str]] = field(default_factory=dict)  # agent_name: [task_ids]
    
    # Conversation summary
    conversation_summary: str = ""
    key_decisions: List[str] = field(default_factory=list)
    clarifications_needed: List[str] = field(default_factory=list)
    
    def add_requirement(self, description: str, category: str = "functional", 
                       priority: Priority = Priority.MEDIUM, source: str = "") -> UserRequirement:
        """Add a new requirement to the brief."""
        req = UserRequirement(
            description=description,
            category=category,
            priority=priority,
            source_message=source
        )
        self.requirements.append(req)
        return req
    
    def add_acceptance_criteria(self, requirement_id: str, description: str) -> AcceptanceCriteria:
        """Add acceptance criteria for a requirement."""
        criteria = AcceptanceCriteria(
            requirement_id=requirement_id,
            description=description
        )
        self.acceptance_criteria.append(criteria)
        return criteria
    
    def add_technical_requirement(self, category: str, requirement: str):
        """Add a technical requirement to the appropriate category."""
        spec = self.technical_spec
        if category == "backend":
            spec.backend_requirements.append(requirement)
        elif category == "frontend":
            spec.frontend_requirements.append(requirement)
        elif category == "database":
            spec.database_needs.append(requirement)
        elif category == "api":
            spec.api_endpoints.append(requirement)
        elif category == "integration":
            spec.integrations.append(requirement)
        elif category == "security":
            spec.security_requirements.append(requirement)
        elif category == "performance":
            spec.performance_requirements.append(requirement)
    
    def estimate_complexity(self) -> int:
        """Estimate project complexity on a 1-10 scale."""
        complexity = 3  # Base complexity
        
        # Add based on requirements count
        complexity += min(3, len(self.requirements) // 5)
        
        # Add based on integrations
        complexity += min(2, len(self.technical_spec.integrations))
        
        # Add based on security needs
        if self.technical_spec.security_requirements:
            complexity += 1
        
        # Add based on timeline pressure
        if self.timeline.is_urgent:
            complexity += 1
        
        return min(10, complexity)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert brief to dictionary for serialization."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "session_id": self.session_id,
            "name": self.name,
            "description": self.description,
            "project_type": self.project_type.value,
            "priority": self.priority.value,
            "user_persona": self.user_persona,
            "user_technical_level": self.user_technical_level,
            "requirements": [
                {
                    "id": req.id,
                    "description": req.description,
                    "category": req.category,
                    "priority": req.priority.value
                }
                for req in self.requirements
            ],
            "technical_spec": {
                "backend": self.technical_spec.backend_requirements,
                "frontend": self.technical_spec.frontend_requirements,
                "database": self.technical_spec.database_needs,
                "apis": self.technical_spec.api_endpoints,
                "integrations": self.technical_spec.integrations,
                "security": self.technical_spec.security_requirements,
                "performance": self.technical_spec.performance_requirements,
                "stack": self.technical_spec.suggested_stack.value
            },
            "timeline": {
                "estimated_days": self.timeline.estimated_duration_days,
                "is_urgent": self.timeline.is_urgent,
                "phases": self.timeline.phases,
                "milestones": self.timeline.milestones
            },
            "budget": self.budget_range,
            "complexity": self.estimate_complexity(),
            "key_features": self.key_features,
            "success_metrics": self.success_metrics,
            "assigned_agents": self.assigned_agents,
            "conversation_summary": self.conversation_summary,
            "clarifications_needed": self.clarifications_needed
        }
    
    def to_markdown(self) -> str:
        """Generate a markdown report of the project brief."""
        md = f"""# Project Brief: {self.name}

**ID**: {self.id}  
**Created**: {self.created_at.strftime('%Y-%m-%d %H:%M')}  
**Type**: {self.project_type.value}  
**Priority**: {self.priority.value}  
**Complexity**: {self.estimate_complexity()}/10

## Project Description

{self.description}

## User Profile

- **Persona**: {self.user_persona}
- **Technical Level**: {self.user_technical_level}
- **Industry**: {self.user_industry or 'Not specified'}

## Requirements

### Functional Requirements
"""
        for req in [r for r in self.requirements if r.category == "functional"]:
            md += f"- **{req.priority.value.upper()}**: {req.description}\n"
        
        md += "\n### Non-Functional Requirements\n"
        for req in [r for r in self.requirements if r.category == "non-functional"]:
            md += f"- **{req.priority.value.upper()}**: {req.description}\n"
        
        if self.constraints:
            md += "\n### Constraints\n"
            for constraint in self.constraints:
                md += f"- {constraint}\n"
        
        md += f"""
## Technical Specifications

### Backend Requirements
{chr(10).join('- ' + req for req in self.technical_spec.backend_requirements) or '- None specified'}

### Frontend Requirements  
{chr(10).join('- ' + req for req in self.technical_spec.frontend_requirements) or '- None specified'}

### Database Needs
{chr(10).join('- ' + req for req in self.technical_spec.database_needs) or '- None specified'}

### API Endpoints
{chr(10).join('- ' + req for req in self.technical_spec.api_endpoints) or '- None specified'}

### Integrations
{chr(10).join('- ' + req for req in self.technical_spec.integrations) or '- None specified'}

### Security Requirements
{chr(10).join('- ' + req for req in self.technical_spec.security_requirements) or '- Standard security practices'}

## Timeline

- **Estimated Duration**: {self.timeline.estimated_duration_days} days
- **Urgent**: {'Yes' if self.timeline.is_urgent else 'No'}
- **Budget**: {self.budget_range or 'Not specified'}

## Key Features

{chr(10).join('- ' + feature for feature in self.key_features) or '- To be determined'}

## Success Metrics

{chr(10).join('- ' + metric for metric in self.success_metrics) or '- To be determined'}

## Next Steps

1. Review and validate requirements with specialist agents
2. Create detailed task breakdown
3. Assign tasks to agents based on capabilities
4. Begin development sprint

---
*Generated from Hermes conversation {self.session_id}*
"""
        return md


def create_sample_brief() -> ProjectBrief:
    """Create a sample project brief for testing."""
    brief = ProjectBrief(
        name="Read Later Article Digest",
        description="A system to automatically extract and summarize articles saved for later reading",
        project_type=ProjectType.AUTOMATION,
        priority=Priority.HIGH,
        user_persona="busy_professional",
        user_technical_level="non-technical"
    )
    
    # Add requirements
    req1 = brief.add_requirement(
        "Extract articles from read-later services (Pocket, Instapaper)",
        category="functional",
        priority=Priority.HIGH
    )
    
    req2 = brief.add_requirement(
        "Generate daily/weekly digest emails",
        category="functional", 
        priority=Priority.HIGH
    )
    
    req3 = brief.add_requirement(
        "Summarize articles using AI",
        category="functional",
        priority=Priority.MEDIUM
    )
    
    # Add acceptance criteria
    brief.add_acceptance_criteria(req1.id, "Successfully connects to Pocket API")
    brief.add_acceptance_criteria(req2.id, "Sends digest email at configured time")
    brief.add_acceptance_criteria(req3.id, "Summaries are under 200 words")
    
    # Add technical requirements
    brief.add_technical_requirement("backend", "API integration with Pocket")
    brief.add_technical_requirement("backend", "Email service integration")
    brief.add_technical_requirement("backend", "LLM integration for summaries")
    brief.add_technical_requirement("database", "Store article metadata")
    brief.add_technical_requirement("api", "GET /digest/generate")
    brief.add_technical_requirement("api", "POST /preferences")
    
    # Set other properties
    brief.key_features = [
        "Automatic article extraction",
        "AI-powered summarization",
        "Customizable digest schedule",
        "Multiple read-later service support"
    ]
    
    brief.success_metrics = [
        "90% of articles successfully extracted",
        "Digest generation under 2 minutes",
        "User saves 80% reading time"
    ]
    
    return brief


if __name__ == "__main__":
    # Test the ProjectBrief
    sample = create_sample_brief()
    print(sample.to_markdown())
    print("\n" + "="*60 + "\n")
    print("Complexity:", sample.estimate_complexity())
    print("Dict representation:", sample.to_dict())