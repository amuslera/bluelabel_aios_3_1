#!/usr/bin/env python3
"""
Brief Generator - Transforms Hermes conversation state into ProjectBrief.
Extracts requirements, identifies project type, and structures information.
"""

import re
import logging
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime, timedelta

from src.agents.specialists.hermes.project_brief import (
    ProjectBrief, ProjectType, Priority, UserRequirement,
    TechnologyStack, Timeline
)
from src.agents.specialists.hermes.hermes_agent_simple import (
    ConversationState, IntentBucket
)
from src.agents.specialists.hermes.requirements_extractor import (
    RequirementsExtractor, RequirementType
)

logger = logging.getLogger(__name__)


class BriefGenerator:
    """Generates project briefs from Hermes conversations."""
    
    def __init__(self):
        """Initialize the brief generator."""
        self.requirements_extractor = RequirementsExtractor()
        self.project_type_keywords = {
            ProjectType.WEB_APP: [
                "website", "web app", "web application", "portal", "dashboard",
                "frontend", "ui", "user interface", "responsive", "web-based"
            ],
            ProjectType.API_SERVICE: [
                "api", "rest", "graphql", "microservice", "backend service",
                "endpoint", "webhook", "integration api"
            ],
            ProjectType.AUTOMATION: [
                "automate", "automation", "workflow", "scheduled", "batch",
                "digest", "notification", "extract", "process automatically"
            ],
            ProjectType.DATA_PIPELINE: [
                "etl", "data pipeline", "data processing", "analytics",
                "reporting", "data transformation", "data flow"
            ],
            ProjectType.MOBILE_APP: [
                "mobile app", "ios", "android", "react native", "flutter",
                "mobile application", "smartphone app"
            ],
            ProjectType.INTEGRATION: [
                "integrate", "integration", "connect", "sync", "bridge",
                "third-party", "external service", "api integration"
            ],
            ProjectType.ANALYTICS: [
                "analytics", "dashboard", "metrics", "kpi", "reporting",
                "visualization", "insights", "data analysis"
            ]
        }
        
        self.tech_stack_patterns = {
            TechnologyStack.MERN: ["react", "node", "mongodb", "express"],
            TechnologyStack.MEAN: ["angular", "node", "mongodb", "express"],
            TechnologyStack.DJANGO: ["django", "python", "postgresql"],
            TechnologyStack.FASTAPI: ["fastapi", "python", "api"],
            TechnologyStack.SERVERLESS: ["lambda", "serverless", "aws"]
        }
    
    def generate_brief(self, state: ConversationState) -> ProjectBrief:
        """Generate a complete project brief from conversation state."""
        brief = ProjectBrief(
            session_id=state.session_id,
            created_at=datetime.now()
        )
        
        # Extract basic information
        brief.name = self._extract_project_name(state)
        brief.description = self._generate_description(state)
        brief.project_type = self._identify_project_type(state)
        brief.priority = self._determine_priority(state)
        
        # User information
        brief.user_persona = getattr(state.persona, 'style', 'business')
        brief.user_technical_level = self._assess_technical_level(state)
        
        # Extract requirements
        self._extract_requirements(state, brief)
        
        # Technical specifications
        self._extract_technical_specs(state, brief)
        
        # Timeline and budget
        self._extract_timeline_budget(state, brief)
        
        # Key features and metrics
        self._extract_features_metrics(state, brief)
        
        # Summary and next steps
        brief.conversation_summary = self._generate_summary(state)
        brief.clarifications_needed = self._identify_clarifications(state)
        
        return brief
    
    def _extract_project_name(self, state: ConversationState) -> str:
        """Extract or generate a project name."""
        # Look for explicit project names in user messages
        for msg in state.messages:
            if msg["role"] == "user":
                # Pattern: "build a/an X" or "create a/an X"
                match = re.search(r'(?:build|create|make|develop)\s+(?:a|an)\s+(.+?)(?:\.|,|$)', 
                                msg["content"], re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    # Clean up and capitalize
                    return self._clean_project_name(name)
        
        # Fallback based on intent
        if state.intent_state.current_bucket == IntentBucket.AUTOMATE:
            return "Automation Workflow"
        elif state.intent_state.current_bucket == IntentBucket.BUILD:
            return "Custom Application"
        
        return "New Project"
    
    def _clean_project_name(self, name: str) -> str:
        """Clean and format project name."""
        # Remove common suffixes
        name = re.sub(r'\s+(system|app|application|tool|platform)$', '', name, flags=re.IGNORECASE)
        # Title case
        words = name.split()
        return ' '.join(word.capitalize() for word in words)
    
    def _generate_description(self, state: ConversationState) -> str:
        """Generate project description from conversation."""
        # Collect all user descriptions
        descriptions = []
        for msg in state.messages:
            if msg["role"] == "user":
                content = msg["content"]
                # Look for descriptive sentences
                if len(content) > 50:  # Likely contains description
                    descriptions.append(content)
        
        if descriptions:
            # Use the most detailed description
            return max(descriptions, key=len)
        
        # Fallback to intent-based description
        if state.intent_state.specific_type:
            return f"A {state.intent_state.specific_type} solution"
        
        return "Project requirements to be clarified"
    
    def _identify_project_type(self, state: ConversationState) -> ProjectType:
        """Identify the type of project from conversation."""
        # Combine all user messages
        all_text = ' '.join(msg["content"].lower() 
                           for msg in state.messages if msg["role"] == "user")
        
        # Score each project type
        scores = {}
        for ptype, keywords in self.project_type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            if score > 0:
                scores[ptype] = score
        
        # Return highest scoring type
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        # Check intent bucket as fallback
        if state.intent_state.current_bucket == IntentBucket.AUTOMATE:
            return ProjectType.AUTOMATION
        elif state.intent_state.current_bucket == IntentBucket.ANALYZE:
            return ProjectType.ANALYTICS
        
        return ProjectType.UNKNOWN
    
    def _determine_priority(self, state: ConversationState) -> Priority:
        """Determine project priority from conversation."""
        urgent_keywords = ["urgent", "asap", "immediately", "critical", "emergency"]
        high_keywords = ["important", "priority", "need", "quickly", "soon"]
        
        all_text = ' '.join(msg["content"].lower() 
                           for msg in state.messages if msg["role"] == "user")
        
        if any(keyword in all_text for keyword in urgent_keywords):
            return Priority.CRITICAL
        elif any(keyword in all_text for keyword in high_keywords):
            return Priority.HIGH
        
        return Priority.MEDIUM
    
    def _assess_technical_level(self, state: ConversationState) -> str:
        """Assess user's technical level from conversation."""
        tech_indicators = {
            "advanced": ["api", "database", "backend", "frontend", "architecture", 
                        "microservices", "docker", "kubernetes"],
            "intermediate": ["server", "hosting", "framework", "library", "git"],
            "basic": ["code", "programming", "website", "app"],
        }
        
        all_text = ' '.join(msg["content"].lower() 
                           for msg in state.messages if msg["role"] == "user")
        
        for level, keywords in tech_indicators.items():
            if any(keyword in all_text for keyword in keywords):
                return level
        
        return "non-technical"
    
    def _extract_requirements(self, state: ConversationState, brief: ProjectBrief):
        """Extract user requirements from conversation."""
        # Extract from explicit project requirements
        if state.project_requirements:
            for key, value in state.project_requirements.items():
                # Determine category and priority
                category = "functional"
                priority = Priority.MEDIUM
                
                if key in ["authentication", "security", "performance"]:
                    category = "non-functional"
                    priority = Priority.HIGH
                
                brief.add_requirement(
                    description=f"{key}: {value}",
                    category=category,
                    priority=priority
                )
        
        # Extract from conversation patterns
        requirement_patterns = [
            (r"I (?:need|want|would like) (?:to|it to) (.+?)(?:\.|,|$)", Priority.HIGH),
            (r"It should (?:be able to |)(.+?)(?:\.|,|$)", Priority.MEDIUM),
            (r"Must (?:have|include|support) (.+?)(?:\.|,|$)", Priority.HIGH),
            (r"(?:Feature|Functionality):\s*(.+?)(?:\.|,|$)", Priority.MEDIUM),
        ]
        
        for msg in state.messages:
            if msg["role"] == "user":
                content = msg["content"]
                for pattern, priority in requirement_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        brief.add_requirement(
                            description=match.strip(),
                            category="functional",
                            priority=priority,
                            source=content
                        )
        
        # Add constraints
        self._extract_constraints(state, brief)
    
    def _extract_constraints(self, state: ConversationState, brief: ProjectBrief):
        """Extract project constraints."""
        constraint_patterns = {
            "budget": r"budget[^\w]*(?:is |of |around |approximately |)([^\.,]+)",
            "timeline": r"(?:deadline|timeline|due|complete[^\w]*(?:by|in)|deliver[^\w]*(?:by|in))\s*([^\.,]+)",
            "technology": r"(?:use|using|built with|in)\s+(react|vue|angular|python|java|node)",
        }
        
        all_text = ' '.join(msg["content"] 
                           for msg in state.messages if msg["role"] == "user")
        
        for constraint_type, pattern in constraint_patterns.items():
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                brief.constraints.append(f"{constraint_type}: {match.group(1).strip()}")
    
    def _extract_technical_specs(self, state: ConversationState, brief: ProjectBrief):
        """Extract technical specifications using advanced requirements extractor."""
        # Get all user messages
        all_text = ' '.join(msg["content"] 
                           for msg in state.messages if msg["role"] == "user")
        
        # Use requirements extractor
        extracted_reqs = self.requirements_extractor.extract_requirements(all_text)
        
        # Generate technical spec from extracted requirements
        tech_spec = self.requirements_extractor.generate_technical_spec(extracted_reqs)
        
        # Map to brief's technical spec structure
        if tech_spec["backend_services"]:
            for service in tech_spec["backend_services"]:
                brief.add_technical_requirement("backend", service)
        
        if tech_spec["apis"]:
            for api in tech_spec["apis"]:
                brief.add_technical_requirement("api", api)
        
        if tech_spec["databases"]:
            for db in tech_spec["databases"]:
                brief.add_technical_requirement("database", db)
        
        if tech_spec["integrations"]:
            for integration in tech_spec["integrations"]:
                brief.add_technical_requirement("integration", integration)
        
        if tech_spec["security"]:
            for security in tech_spec["security"]:
                brief.add_technical_requirement("security", security)
        
        if tech_spec["infrastructure"]:
            for infra in tech_spec["infrastructure"]:
                brief.add_technical_requirement("performance", infra)
        
        # Also add high-confidence requirements as user requirements
        for req in extracted_reqs:
            if req.confidence >= 0.7:
                priority = Priority.HIGH if req.confidence >= 0.8 else Priority.MEDIUM
                brief.add_requirement(
                    description=req.description,
                    category="functional" if req.type != RequirementType.SECURITY else "non-functional",
                    priority=priority,
                    source=req.source_text
                )
        
        # Identify technology stack
        brief.technical_spec.suggested_stack = self._identify_tech_stack(all_text.lower())
    
    def _identify_tech_stack(self, text: str) -> TechnologyStack:
        """Identify suggested technology stack."""
        for stack, keywords in self.tech_stack_patterns.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            if matches >= 2:  # At least 2 matching keywords
                return stack
        return TechnologyStack.CUSTOM
    
    def _extract_timeline_budget(self, state: ConversationState, brief: ProjectBrief):
        """Extract timeline and budget information."""
        all_text = ' '.join(msg["content"] 
                           for msg in state.messages if msg["role"] == "user")
        
        # Timeline extraction
        timeline_match = re.search(r'(\d+)\s*(day|week|month)', all_text, re.IGNORECASE)
        if timeline_match:
            number = int(timeline_match.group(1))
            unit = timeline_match.group(2).lower()
            
            # Convert to days
            if unit == "week":
                days = number * 7
            elif unit == "month":
                days = number * 30
            else:
                days = number
            
            brief.timeline.estimated_duration_days = days
            
            # Check if urgent
            if "urgent" in all_text or "asap" in all_text:
                brief.timeline.is_urgent = True
        
        # Budget extraction
        budget_match = re.search(r'\$([0-9,]+)(?:k|thousand)?|\b(\d+)k\b', all_text, re.IGNORECASE)
        if budget_match:
            if budget_match.group(1):
                amount = budget_match.group(1).replace(',', '')
                brief.budget_range = f"${amount}"
            else:
                amount = budget_match.group(2)
                brief.budget_range = f"${amount}k"
    
    def _extract_features_metrics(self, state: ConversationState, brief: ProjectBrief):
        """Extract key features and success metrics."""
        # Key features from requirements
        feature_keywords = ["feature", "ability", "functionality", "support", "allow"]
        
        for msg in state.messages:
            if msg["role"] == "user":
                content = msg["content"]
                for keyword in feature_keywords:
                    if keyword in content.lower():
                        sentences = content.split('.')
                        for sentence in sentences:
                            if keyword in sentence.lower() and len(sentence) > 20:
                                brief.key_features.append(sentence.strip())
        
        # Success metrics
        all_text = ' '.join(msg["content"] 
                           for msg in state.messages if msg["role"] == "user")
        
        metric_keywords = ["success", "goal", "achieve", "measure", "kpi"]
        metric_patterns = [
            r"(\d+%[^\.]+)",  # Percentage-based metrics
            r"(?:save|reduce|increase)\s+(?:\d+%?[^\.]+)",  # Improvement metrics
        ]
        
        for pattern in metric_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            for match in matches:
                brief.success_metrics.append(match.strip())
    
    def _generate_summary(self, state: ConversationState) -> str:
        """Generate conversation summary."""
        summary_parts = []
        
        # Add intent summary
        intent = state.intent_state.current_bucket.value
        summary_parts.append(f"User wants to {intent} a solution")
        
        # Add project type
        if state.project_requirements:
            req_count = len(state.project_requirements)
            summary_parts.append(f"with {req_count} identified requirements")
        
        # Add conversation length
        summary_parts.append(f"discussed over {state.turn_count} turns")
        
        return ". ".join(summary_parts) + "."
    
    def _identify_clarifications(self, state: ConversationState) -> List[str]:
        """Identify what clarifications are still needed."""
        clarifications = []
        
        # Check for missing core information
        if not state.project_requirements.get("users"):
            clarifications.append("Who will be the primary users of this system?")
        
        if not state.project_requirements.get("timeline"):
            clarifications.append("What is the desired timeline for completion?")
        
        if not state.project_requirements.get("budget"):
            clarifications.append("What is the budget range for this project?")
        
        # Check for vague requirements
        vague_terms = ["some", "maybe", "possibly", "might", "could"]
        for msg in state.messages:
            if msg["role"] == "user":
                content = msg["content"].lower()
                if any(term in content for term in vague_terms):
                    clarifications.append("Please clarify any tentative features marked with 'maybe' or 'possibly'")
                    break
        
        return clarifications


def test_brief_generator():
    """Test the brief generator with a sample conversation."""
    from src.agents.specialists.hermes.hermes_agent_simple import ConversationState
    from src.agents.specialists.hermes.persona_system import PersonaLibrary
    
    # Create test conversation state
    state = ConversationState()
    state.persona = PersonaLibrary.get_business_persona()
    
    # Simulate conversation
    state.add_message("user", "Hello, I need help building something")
    state.add_message("assistant", "Hi! I'd be happy to help. What would you like to build?")
    state.add_message("user", "I would like to be able to extract information from articles I save to 'read later' and create a sort of daily or weekly digest. I use Pocket to save articles.")
    state.add_message("assistant", "That sounds like a great automation project! Let me understand better...")
    state.add_message("user", "Yes, I want it to automatically pull articles from Pocket, summarize them using AI, and send me an email digest every morning. Budget is around $5k and I need it within 2 weeks.")
    
    # Set intent and requirements
    state.intent_state.current_bucket = IntentBucket.AUTOMATE
    state.intent_state.specific_type = "article digest automation"
    state.project_requirements = {
        "source": "Pocket API",
        "processing": "AI summarization",
        "delivery": "Email digest",
        "schedule": "Daily morning"
    }
    
    # Generate brief
    generator = BriefGenerator()
    brief = generator.generate_brief(state)
    
    # Print results
    print(brief.to_markdown())
    print("\n" + "="*60)
    print(f"Project Type: {brief.project_type.value}")
    print(f"Complexity: {brief.estimate_complexity()}/10")
    print(f"Requirements: {len(brief.requirements)}")
    print(f"Technical Specs: {len(brief.technical_spec.backend_requirements)} backend, "
          f"{len(brief.technical_spec.api_endpoints)} APIs")


if __name__ == "__main__":
    test_brief_generator()