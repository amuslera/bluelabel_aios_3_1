"""
Agent naming system for AIOSv3.1.

Provides mapping between technical class names and Greek god display names.
"""

from typing import Dict, Optional


class AgentNaming:
    """Centralized agent naming system."""
    
    # Map class names to Greek god names
    GREEK_NAMES: Dict[str, str] = {
        "BackendAgent": "Apollo",
        "FrontendAgent": "Aphrodite", 
        "QAAgent": "Athena",
        "DevOpsAgent": "Hephaestus",
        "JordanDevOpsAgent": "Hephaestus",  # Legacy name support
        "ProjectCTOAgent": "Hera",
        "ConciergeAgent": "Hermes"
    }
    
    # Greek god domains and descriptions
    GREEK_DOMAINS: Dict[str, str] = {
        "Apollo": "God of knowledge, logic, and order",
        "Aphrodite": "Goddess of beauty, aesthetics, and creativity",
        "Athena": "Goddess of wisdom, strategic warfare, and crafts",
        "Hephaestus": "God of the forge, craftsmanship, and technology",
        "Hera": "Queen of gods, organization, and leadership",
        "Hermes": "Messenger god, guide between worlds"
    }
    
    # Emojis for each god
    GREEK_EMOJIS: Dict[str, str] = {
        "Apollo": "🏛️",
        "Aphrodite": "🎨",
        "Athena": "🛡️",
        "Hephaestus": "🔨",
        "Hera": "👑",
        "Hermes": "🪽"
    }
    
    # Legacy name mapping (for backward compatibility)
    LEGACY_NAMES: Dict[str, str] = {
        "Marcus Chen": "Apollo",
        "Emily Rodriguez": "Aphrodite",
        "Alex Thompson": "Athena",
        "Jordan Kim": "Hephaestus",
        "Sarah Kim": "Hera"
    }
    
    @classmethod
    def get_display_name(cls, class_name: str) -> str:
        """Get Greek god display name for an agent class."""
        return cls.GREEK_NAMES.get(class_name, class_name)
    
    @classmethod
    def get_domain(cls, greek_name: str) -> Optional[str]:
        """Get the mythological domain for a Greek god name."""
        return cls.GREEK_DOMAINS.get(greek_name)
    
    @classmethod
    def get_emoji(cls, greek_name: str) -> str:
        """Get emoji for a Greek god name."""
        return cls.GREEK_EMOJIS.get(greek_name, "🤖")
    
    @classmethod
    def from_legacy_name(cls, legacy_name: str) -> Optional[str]:
        """Convert legacy human name to Greek god name."""
        return cls.LEGACY_NAMES.get(legacy_name)
    
    @classmethod
    def get_full_title(cls, class_name: str) -> str:
        """Get full title with Greek name and domain."""
        greek_name = cls.get_display_name(class_name)
        domain = cls.get_domain(greek_name)
        emoji = cls.get_emoji(greek_name)
        
        if domain:
            return f"{emoji} {greek_name} - {domain}"
        return f"{emoji} {greek_name}"


# Convenience functions
def get_agent_display_name(class_name: str) -> str:
    """Get display name for an agent class."""
    return AgentNaming.get_display_name(class_name)


def get_agent_emoji(class_name: str) -> str:
    """Get emoji for an agent class."""
    greek_name = AgentNaming.get_display_name(class_name)
    return AgentNaming.get_emoji(greek_name)