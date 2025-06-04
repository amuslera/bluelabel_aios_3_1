#!/usr/bin/env python3
"""
Requirements Extractor - Advanced extraction of technical requirements.
Uses patterns, NLP techniques, and domain knowledge to extract structured requirements.
"""

import re
import logging
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RequirementType(Enum):
    """Types of technical requirements."""
    API_INTEGRATION = "api_integration"
    DATA_STORAGE = "data_storage"
    USER_INTERFACE = "user_interface"
    AUTHENTICATION = "authentication"
    NOTIFICATION = "notification"
    SCHEDULING = "scheduling"
    DATA_PROCESSING = "data_processing"
    REPORTING = "reporting"
    SECURITY = "security"
    PERFORMANCE = "performance"


@dataclass
class ExtractedRequirement:
    """A single extracted technical requirement."""
    type: RequirementType
    description: str
    components: List[str]  # Technical components needed
    confidence: float  # 0.0 to 1.0
    source_text: str  # Original text this came from


class RequirementsExtractor:
    """Extracts technical requirements from natural language."""
    
    def __init__(self):
        """Initialize the requirements extractor."""
        # Define patterns for different requirement types
        self.requirement_patterns = {
            RequirementType.API_INTEGRATION: [
                r"(?:integrate|connect|pull|fetch|extract|get).{0,20}(?:from|via|using|through)\s+(\w+)",
                r"(\w+)\s+(?:api|API|integration|webhook)",
                r"(?:third.party|external)\s+(?:service|api|system)",
            ],
            RequirementType.DATA_STORAGE: [
                r"(?:store|save|persist|keep|retain|archive)\s+(.+?)(?:\.|,|$)",
                r"(?:database|storage|repository)\s+(?:for|to)\s+(.+?)(?:\.|,|$)",
                r"(?:need|want).{0,20}(?:history|log|record)\s+(?:of|for)\s+(.+?)(?:\.|,|$)",
            ],
            RequirementType.USER_INTERFACE: [
                r"(?:interface|ui|dashboard|page|screen|form)\s+(?:for|to)\s+(.+?)(?:\.|,|$)",
                r"(?:display|show|visualize|present)\s+(.+?)(?:\.|,|$)",
                r"(?:user|users)\s+(?:can|should|must)\s+(?:see|view|access)\s+(.+?)(?:\.|,|$)",
            ],
            RequirementType.AUTHENTICATION: [
                r"(?:login|sign.in|authenticate|auth)",
                r"(?:user|account)\s+(?:management|system|access)",
                r"(?:secure|protect|restrict)\s+(?:access|data)",
            ],
            RequirementType.NOTIFICATION: [
                r"(?:notify|alert|email|send|message)\s+(.+?)(?:\.|,|$)",
                r"(?:digest|summary|report)\s+(?:via|through|by)\s+(?:email|sms|notification)",
                r"(?:daily|weekly|scheduled)\s+(?:email|notification|alert)",
            ],
            RequirementType.SCHEDULING: [
                r"(?:schedule|scheduled|cron|periodic|recurring)",
                r"(?:daily|weekly|hourly|monthly)\s+(?:job|task|process)",
                r"(?:at|every)\s+(?:\d+|specific)\s+(?:time|hour|day)",
            ],
            RequirementType.DATA_PROCESSING: [
                r"(?:process|analyze|transform|summarize|extract)\s+(.+?)(?:\.|,|$)",
                r"(?:ai|ml|machine.learning|nlp)\s+(?:to|for)\s+(.+?)(?:\.|,|$)",
                r"(?:automatically|auto)\s+(?:generate|create|produce)\s+(.+?)(?:\.|,|$)",
            ],
        }
        
        # Component mappings for each requirement type
        self.component_mappings = {
            RequirementType.API_INTEGRATION: {
                "pocket": ["Pocket API Client", "OAuth2 Authentication", "Rate Limiting"],
                "instapaper": ["Instapaper API", "API Key Management"],
                "readwise": ["Readwise API", "Webhook Handler"],
                "default": ["HTTP Client", "API Gateway", "Error Handling"],
            },
            RequirementType.DATA_STORAGE: {
                "article": ["Article Model", "PostgreSQL/MySQL", "Full-text Search"],
                "user": ["User Model", "Authentication DB", "Session Storage"],
                "metadata": ["NoSQL Store", "Caching Layer", "Redis"],
                "default": ["Database Schema", "ORM Layer", "Migrations"],
            },
            RequirementType.NOTIFICATION: {
                "email": ["Email Service", "SMTP/SendGrid", "Template Engine"],
                "digest": ["Digest Generator", "Scheduler", "Queue System"],
                "default": ["Notification Service", "Message Queue", "Delivery Tracking"],
            },
            RequirementType.DATA_PROCESSING: {
                "summarize": ["LLM Integration", "Text Processing", "Token Management"],
                "extract": ["Content Extractor", "HTML Parser", "Data Cleaner"],
                "analyze": ["Analytics Engine", "ML Pipeline", "Data Transformer"],
                "default": ["Processing Pipeline", "Worker Service", "Job Queue"],
            },
        }
    
    def extract_requirements(self, text: str) -> List[ExtractedRequirement]:
        """Extract all technical requirements from text."""
        requirements = []
        text_lower = text.lower()
        
        # Extract requirements by type
        for req_type, patterns in self.requirement_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    # Extract the requirement description
                    if match.groups():
                        description = match.group(1).strip()
                    else:
                        description = match.group(0).strip()
                    
                    # Skip very short matches
                    if len(description) < 5:
                        continue
                    
                    # Get components for this requirement
                    components = self._identify_components(req_type, description)
                    
                    # Calculate confidence based on pattern match quality
                    confidence = self._calculate_confidence(description, match)
                    
                    requirement = ExtractedRequirement(
                        type=req_type,
                        description=self._clean_description(description),
                        components=components,
                        confidence=confidence,
                        source_text=match.group(0)
                    )
                    
                    # Avoid duplicates
                    if not self._is_duplicate(requirement, requirements):
                        requirements.append(requirement)
        
        # Extract implicit requirements
        requirements.extend(self._extract_implicit_requirements(text))
        
        return sorted(requirements, key=lambda x: x.confidence, reverse=True)
    
    def _identify_components(self, req_type: RequirementType, description: str) -> List[str]:
        """Identify technical components needed for a requirement."""
        components = []
        mappings = self.component_mappings.get(req_type, {})
        
        # Check for specific keywords
        for keyword, component_list in mappings.items():
            if keyword != "default" and keyword in description.lower():
                components.extend(component_list)
        
        # Add default components if no specific ones found
        if not components and "default" in mappings:
            components.extend(mappings["default"])
        
        return list(set(components))  # Remove duplicates
    
    def _calculate_confidence(self, description: str, match) -> float:
        """Calculate confidence score for extracted requirement."""
        confidence = 0.7  # Base confidence
        
        # Increase confidence for longer, more specific descriptions
        if len(description) > 30:
            confidence += 0.1
        
        # Increase confidence for exact keyword matches
        keywords = ["must", "need", "require", "should"]
        if any(keyword in description.lower() for keyword in keywords):
            confidence += 0.1
        
        # Decrease confidence for vague terms
        vague_terms = ["maybe", "possibly", "might", "could"]
        if any(term in description.lower() for term in vague_terms):
            confidence -= 0.2
        
        return min(1.0, max(0.1, confidence))
    
    def _clean_description(self, description: str) -> str:
        """Clean and format requirement description."""
        # Remove extra whitespace
        description = ' '.join(description.split())
        
        # Capitalize first letter
        if description:
            description = description[0].upper() + description[1:]
        
        # Remove trailing punctuation
        description = description.rstrip('.,;:')
        
        return description
    
    def _is_duplicate(self, req: ExtractedRequirement, existing: List[ExtractedRequirement]) -> bool:
        """Check if requirement is duplicate of existing ones."""
        for existing_req in existing:
            # Same type and similar description
            if (existing_req.type == req.type and 
                self._similarity(existing_req.description, req.description) > 0.8):
                return True
        return False
    
    def _similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity (0.0 to 1.0)."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _extract_implicit_requirements(self, text: str) -> List[ExtractedRequirement]:
        """Extract requirements that are implied but not explicitly stated."""
        implicit_reqs = []
        text_lower = text.lower()
        
        # If mentions email/digest, implies scheduling
        if "digest" in text_lower or "daily" in text_lower or "weekly" in text_lower:
            if not any("schedul" in text_lower for _ in [1]):  # Not already mentioned
                implicit_reqs.append(ExtractedRequirement(
                    type=RequirementType.SCHEDULING,
                    description="Schedule automated digest generation",
                    components=["Cron Scheduler", "Job Queue", "Time Zone Handler"],
                    confidence=0.8,
                    source_text="[Implied from digest requirement]"
                ))
        
        # If mentions API integration, implies authentication
        if "api" in text_lower or "integrate" in text_lower:
            if not any(word in text_lower for word in ["auth", "login", "credential"]):
                implicit_reqs.append(ExtractedRequirement(
                    type=RequirementType.AUTHENTICATION,
                    description="API authentication and credential management",
                    components=["OAuth Handler", "API Key Storage", "Token Refresh"],
                    confidence=0.7,
                    source_text="[Implied from API integration]"
                ))
        
        # If mentions user preferences, implies data storage
        if "preference" in text_lower or "settings" in text_lower or "configure" in text_lower:
            implicit_reqs.append(ExtractedRequirement(
                type=RequirementType.DATA_STORAGE,
                description="Store user preferences and settings",
                components=["User Preferences Model", "Settings Storage", "Config Management"],
                confidence=0.8,
                source_text="[Implied from user configuration needs]"
            ))
        
        return implicit_reqs
    
    def generate_technical_spec(self, requirements: List[ExtractedRequirement]) -> Dict[str, List[str]]:
        """Generate technical specification from extracted requirements."""
        spec = {
            "backend_services": [],
            "apis": [],
            "databases": [],
            "integrations": [],
            "infrastructure": [],
            "security": [],
        }
        
        # Aggregate components by category
        all_components = []
        for req in requirements:
            all_components.extend(req.components)
        
        # Categorize components
        for component in set(all_components):
            component_lower = component.lower()
            
            if any(term in component_lower for term in ["api", "client", "webhook"]):
                spec["apis"].append(component)
            elif any(term in component_lower for term in ["database", "model", "schema", "storage"]):
                spec["databases"].append(component)
            elif any(term in component_lower for term in ["oauth", "auth", "security", "encryption"]):
                spec["security"].append(component)
            elif any(term in component_lower for term in ["queue", "worker", "scheduler", "pipeline"]):
                spec["infrastructure"].append(component)
            elif any(term in component_lower for term in ["service", "handler", "processor", "engine"]):
                spec["backend_services"].append(component)
            else:
                spec["integrations"].append(component)
        
        return spec


def test_requirements_extractor():
    """Test the requirements extractor."""
    extractor = RequirementsExtractor()
    
    # Test text from user conversation
    test_text = """
    I would like to be able to extract information from articles I save to 'read later' 
    and create a sort of daily or weekly digest. I use Pocket to save articles.
    The system should automatically pull articles from Pocket, summarize them using AI, 
    and send me an email digest every morning at 7 AM. I'd also like to configure
    which topics I'm most interested in. Budget is around $5k and I need it within 2 weeks.
    """
    
    # Extract requirements
    requirements = extractor.extract_requirements(test_text)
    
    print("Extracted Requirements:")
    print("=" * 60)
    
    for req in requirements:
        print(f"\nType: {req.type.value}")
        print(f"Description: {req.description}")
        print(f"Components: {', '.join(req.components)}")
        print(f"Confidence: {req.confidence:.2f}")
        print(f"Source: {req.source_text[:50]}...")
    
    # Generate technical spec
    print("\n\nTechnical Specification:")
    print("=" * 60)
    
    spec = extractor.generate_technical_spec(requirements)
    for category, items in spec.items():
        if items:
            print(f"\n{category.replace('_', ' ').title()}:")
            for item in items:
                print(f"  - {item}")


if __name__ == "__main__":
    test_requirements_extractor()