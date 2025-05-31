"""
LLM routing system for AIOSv3 platform.

Provides intelligent routing between cloud and local LLM providers based on
cost, privacy requirements, performance needs, and availability.
"""

from .router import (
    LLMRouter,
    RoutingStrategy,
    RoutingPolicy,
    RoutingContext,
    RoutingDecision,
)
from .providers import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
    ModelInfo,
    ModelCapability,
    ModelSize,
    ModelType,
    ProviderConfig,
    ProviderHealthStatus,
    ClaudeProvider,
    ClaudeConfig,
    LocalProvider,
    LocalConfig,
)

__all__ = [
    # Router classes
    "LLMRouter",
    "RoutingStrategy",
    "RoutingPolicy",
    "RoutingContext",
    "RoutingDecision",
    # Provider classes
    "LLMProvider",
    "LLMRequest",
    "LLMResponse",
    "ModelInfo",
    "ModelCapability",
    "ModelSize",
    "ModelType",
    "ProviderConfig",
    "ProviderHealthStatus",
    "ClaudeProvider",
    "ClaudeConfig",
    "LocalProvider",
    "LocalConfig",
]
