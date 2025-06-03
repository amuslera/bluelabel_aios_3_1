"""
Intent tracking system for Hermes conversations.

Provides sophisticated intent detection and evolution tracking to enable
seamless handoff to task execution workflows.
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from src.agents.specialists.hermes.hermes_agent import IntentBucket


@dataclass
class ProjectType:
    """Represents a specific project type with its characteristics."""
    id: str
    name: str
    category: IntentBucket
    keywords: List[str]
    questions: List[str]
    required_info: List[str]
    
    def matches(self, text: str) -> int:
        """Count keyword matches in text."""
        text_lower = text.lower()
        return sum(1 for keyword in self.keywords if keyword in text_lower)


class IntentTracker:
    """
    Advanced intent tracking for Hermes conversations.
    
    Detects user intent, tracks evolution, and maps to project types.
    """
    
    def __init__(self):
        """Initialize the intent tracker with project definitions."""
        self.project_types = self._initialize_project_types()
        self.intent_keywords = self._initialize_intent_keywords()
        
    def _initialize_project_types(self) -> List[ProjectType]:
        """Define all supported project types."""
        return [
            # Build Something Projects
            ProjectType(
                id="ecommerce_site",
                name="E-commerce Website",
                category=IntentBucket.BUILD,
                keywords=["store", "shop", "ecommerce", "e-commerce", "sell", 
                         "products", "shopping cart", "checkout", "inventory"],
                questions=[
                    "What products will you sell?",
                    "Do you need inventory management?",
                    "Will you handle payments online?",
                    "Do you need customer accounts?"
                ],
                required_info=["products", "payment_method", "shipping"]
            ),
            ProjectType(
                id="saas_app",
                name="SaaS Application",
                category=IntentBucket.BUILD,
                keywords=["saas", "subscription", "software as a service", 
                         "monthly billing", "user management", "multi-tenant"],
                questions=[
                    "What service will your SaaS provide?",
                    "How will you handle subscriptions?",
                    "Do you need team/organization support?",
                    "What's your pricing model?"
                ],
                required_info=["service_type", "pricing_model", "user_types"]
            ),
            ProjectType(
                id="portfolio_site",
                name="Portfolio Website",
                category=IntentBucket.BUILD,
                keywords=["portfolio", "showcase", "work", "projects", 
                         "gallery", "resume", "cv", "about me"],
                questions=[
                    "What type of work will you showcase?",
                    "Do you need a contact form?",
                    "Will you blog about your work?",
                    "Do you want client testimonials?"
                ],
                required_info=["content_type", "sections", "contact_method"]
            ),
            ProjectType(
                id="blog_site",
                name="Blog Website",
                category=IntentBucket.BUILD,
                keywords=["blog", "articles", "posts", "writing", 
                         "content", "publish", "newsletter"],
                questions=[
                    "What topics will you write about?",
                    "Do you need multiple authors?",
                    "Want comments or discussions?",
                    "Need email subscriptions?"
                ],
                required_info=["topics", "author_count", "features"]
            ),
            ProjectType(
                id="api_service",
                name="API Service",
                category=IntentBucket.BUILD,
                keywords=["api", "rest", "graphql", "endpoint", "service",
                         "backend", "microservice", "integration"],
                questions=[
                    "What will your API do?",
                    "Who will consume this API?",
                    "Need authentication?",
                    "What data will it handle?"
                ],
                required_info=["purpose", "consumers", "data_types", "auth"]
            ),
            
            # Automate Task Projects
            ProjectType(
                id="workflow_automation",
                name="Workflow Automation",
                category=IntentBucket.AUTOMATE,
                keywords=["automate", "workflow", "process", "trigger",
                         "schedule", "integration", "connect", "sync"],
                questions=[
                    "What process do you want to automate?",
                    "What triggers the automation?",
                    "Which systems need to connect?",
                    "How often should it run?"
                ],
                required_info=["process", "triggers", "systems", "frequency"]
            ),
            ProjectType(
                id="data_pipeline",
                name="Data Pipeline",
                category=IntentBucket.AUTOMATE,
                keywords=["pipeline", "etl", "data flow", "transform",
                         "extract", "load", "process data", "batch"],
                questions=[
                    "What data sources do you have?",
                    "Where should data end up?",
                    "What transformations needed?",
                    "How much data volume?"
                ],
                required_info=["sources", "destination", "transformations", "volume"]
            ),
            
            # Analyze Data Projects
            ProjectType(
                id="code_analysis",
                name="Code Analysis",
                category=IntentBucket.ANALYZE,
                keywords=["analyze code", "review", "audit", "quality",
                         "security scan", "performance", "refactor"],
                questions=[
                    "What codebase needs analysis?",
                    "Looking for specific issues?",
                    "Need security scanning?",
                    "Want optimization suggestions?"
                ],
                required_info=["codebase", "focus_areas", "goals"]
            ),
            ProjectType(
                id="data_analysis",
                name="Data Analysis",
                category=IntentBucket.ANALYZE,
                keywords=["analyze data", "insights", "metrics", "dashboard",
                         "visualization", "reports", "analytics"],
                questions=[
                    "What data do you need to analyze?",
                    "What insights are you seeking?",
                    "Need visualizations?",
                    "Want automated reports?"
                ],
                required_info=["data_source", "metrics", "reporting_needs"]
            )
        ]
    
    def _initialize_intent_keywords(self) -> Dict[str, Dict[str, float]]:
        """Initialize weighted keywords for intent detection."""
        return {
            "build": {
                # Strong indicators
                "build": 1.0, "create": 1.0, "make": 0.9, "develop": 1.0,
                "need a": 0.8, "want a": 0.8, "looking for": 0.7,
                # Project type indicators
                "website": 0.9, "app": 0.9, "application": 0.9, "site": 0.8,
                "platform": 0.8, "system": 0.7, "service": 0.7,
                # Specific types
                "store": 0.9, "shop": 0.9, "blog": 0.9, "portfolio": 0.9,
                "api": 0.9, "database": 0.8, "backend": 0.8, "frontend": 0.8
            },
            "automate": {
                # Strong indicators
                "automate": 1.0, "automation": 1.0, "workflow": 0.9,
                "process": 0.8, "integrate": 0.8, "connect": 0.7,
                # Action words
                "schedule": 0.8, "trigger": 0.8, "sync": 0.8, "pipeline": 0.9,
                "etl": 0.9, "orchestrate": 0.9, "streamline": 0.8
            },
            "analyze": {
                # Strong indicators
                "analyze": 1.0, "analysis": 1.0, "review": 0.8, "audit": 0.9,
                "assess": 0.8, "evaluate": 0.8, "examine": 0.7,
                # Specific types
                "performance": 0.8, "security": 0.8, "quality": 0.8,
                "metrics": 0.8, "insights": 0.8, "data": 0.7
            },
            "explore": {
                # Exploration indicators
                "what can": 0.9, "how does": 0.8, "tell me": 0.7,
                "explain": 0.8, "help": 0.7, "guide": 0.8,
                "not sure": 0.9, "explore": 0.9, "options": 0.8
            },
            "support": {
                # Support indicators
                "problem": 0.9, "issue": 0.9, "error": 0.9, "broken": 0.9,
                "fix": 0.8, "debug": 0.9, "troubleshoot": 0.9,
                "help with": 0.8, "support": 0.9, "assist": 0.8
            }
        }
    
    def detect_intent(
        self,
        user_input: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> Tuple[IntentBucket, Optional[str], float, Dict[str, Any]]:
        """
        Detect intent from user input with confidence scoring.
        
        Returns:
            Tuple of (bucket, specific_type, confidence, metadata)
        """
        input_lower = user_input.lower()
        
        # Calculate weighted scores for each intent
        intent_scores = {}
        for intent_name, keywords in self.intent_keywords.items():
            score = 0.0
            matches = []
            
            for keyword, weight in keywords.items():
                if keyword in input_lower:
                    score += weight
                    matches.append(keyword)
            
            intent_scores[intent_name] = (score, matches)
        
        # Find the highest scoring intent
        best_intent = max(intent_scores.items(), key=lambda x: x[1][0])
        intent_name, (score, matches) = best_intent
        
        # Map to IntentBucket
        intent_bucket_map = {
            "build": IntentBucket.BUILD,
            "automate": IntentBucket.AUTOMATE,
            "analyze": IntentBucket.ANALYZE,
            "explore": IntentBucket.EXPLORE,
            "support": IntentBucket.SUPPORT
        }
        
        bucket = intent_bucket_map.get(intent_name, IntentBucket.UNKNOWN)
        
        # Calculate confidence
        confidence = min(0.95, score / 3.0)  # Cap at 95%
        
        # Detect specific project type
        specific_type = None
        project_matches = []
        
        if bucket in [IntentBucket.BUILD, IntentBucket.AUTOMATE, IntentBucket.ANALYZE]:
            # Find matching project types
            for project in self.project_types:
                if project.category == bucket:
                    match_count = project.matches(user_input)
                    if match_count > 0:
                        project_matches.append((project, match_count))
            
            # Get best matching project
            if project_matches:
                best_project = max(project_matches, key=lambda x: x[1])
                specific_type = best_project[0].id
        
        # Build metadata
        metadata = {
            "matched_keywords": matches,
            "all_scores": {k: v[0] for k, v in intent_scores.items()},
            "project_matches": [(p.id, count) for p, count in project_matches]
        }
        
        # Boost confidence if we have conversation history supporting this intent
        if conversation_history and len(conversation_history) > 2:
            # Simple history analysis - could be made more sophisticated
            history_text = " ".join([msg["content"] for msg in conversation_history[-3:]])
            if any(keyword in history_text.lower() for keyword in matches):
                confidence = min(0.95, confidence * 1.2)
        
        return bucket, specific_type, confidence, metadata
    
    def get_clarifying_questions(
        self,
        project_type_id: str,
        answered_info: Dict[str, Any]
    ) -> List[str]:
        """Get the next clarifying questions for a project type."""
        # Find the project type
        project = next((p for p in self.project_types if p.id == project_type_id), None)
        if not project:
            return []
        
        # Filter out already answered questions
        unanswered = []
        for i, required in enumerate(project.required_info):
            if required not in answered_info:
                if i < len(project.questions):
                    unanswered.append(project.questions[i])
        
        return unanswered[:3]  # Return up to 3 questions at a time
    
    def extract_project_info(
        self,
        user_input: str,
        project_type_id: str
    ) -> Dict[str, Any]:
        """Extract project-specific information from user input."""
        extracted = {}
        input_lower = user_input.lower()
        
        # Common extraction patterns
        patterns = {
            "product_count": r'(\d+)\s*products?',
            "user_count": r'(\d+)\s*users?',
            "timeline": r'(asap|urgent|(\d+)\s*(days?|weeks?|months?))',
            "budget": r'\$?\s*(\d+[,\d]*)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, input_lower)
            if match:
                extracted[key] = match.group(1)
        
        # Project-specific extraction
        if project_type_id == "ecommerce_site":
            # Check for product types
            product_keywords = ["clothing", "food", "electronics", "books", 
                              "jewelry", "handmade", "digital", "services"]
            for keyword in product_keywords:
                if keyword in input_lower:
                    extracted["product_type"] = keyword
                    break
        
        return extracted
    
    def suggest_next_steps(
        self,
        intent_state: Dict[str, Any],
        project_requirements: Dict[str, Any]
    ) -> List[str]:
        """Suggest next steps based on current intent and requirements."""
        suggestions = []
        
        bucket = intent_state.get("bucket", IntentBucket.UNKNOWN)
        specific_type = intent_state.get("specific_type")
        confidence = intent_state.get("confidence", 0)
        
        if confidence < 0.7:
            suggestions.append("Help me understand your project better")
            suggestions.append("Explore our platform capabilities")
            suggestions.append("See examples of what we can build")
        
        elif bucket == IntentBucket.BUILD and specific_type:
            # Find missing requirements
            project = next((p for p in self.project_types if p.id == specific_type), None)
            if project:
                missing = [req for req in project.required_info 
                          if req not in project_requirements]
                
                if not missing:
                    suggestions.append("Review project summary")
                    suggestions.append("Start building with our AI team")
                    suggestions.append("Get time and cost estimates")
                else:
                    suggestions.append(f"Answer a few more questions ({len(missing)} remaining)")
                    suggestions.append("Skip to basic implementation")
                    suggestions.append("See similar project examples")
        
        else:
            suggestions.append("Tell me more about your needs")
            suggestions.append("Browse project templates")
            suggestions.append("Talk to a human advisor")
        
        return suggestions