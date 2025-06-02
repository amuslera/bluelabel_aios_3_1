"""
LLM routing system for AIOSv3 platform.

Provides intelligent routing between cloud and local LLM providers based on
cost, privacy requirements, performance needs, and availability.
"""

import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, Field

from src.agents.base.types import TaskType
from .providers.base import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
    ModelCapability,
    ProviderHealthStatus,
)

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Available routing strategies."""

    COST_OPTIMIZED = "cost_optimized"  # Prefer cheapest option
    PERFORMANCE_OPTIMIZED = "performance_optimized"  # Prefer fastest/best quality
    PRIVACY_FIRST = "privacy_first"  # Prefer local/private models
    BALANCED = "balanced"  # Balance cost, performance, and privacy
    FAILOVER = "failover"  # Use backup when primary fails


class RoutingPolicy(BaseModel):
    """Routing policy configuration."""

    strategy: RoutingStrategy = RoutingStrategy.BALANCED
    max_cost_per_request: float = 1.0  # Maximum cost in USD
    min_performance_tier: int = 3  # Minimum performance tier (1-5)
    privacy_required: bool = False  # Require local models
    preferred_providers: list[str] = Field(default_factory=list)
    fallback_providers: list[str] = Field(default_factory=list)
    max_response_time_ms: float = 30000  # Maximum acceptable response time
    enable_caching: bool = True
    cache_ttl_minutes: int = 60


class RoutingContext(BaseModel):
    """Context information for routing decisions."""

    agent_id: str
    task_type: Optional[TaskType] = None
    complexity: int = 5  # 1-10 scale
    privacy_sensitive: bool = False
    budget_remaining: Optional[float] = None
    deadline: Optional[datetime] = None
    user_preferences: dict[str, Any] = Field(default_factory=dict)
    previous_failures: list[str] = Field(default_factory=list)  # Failed provider names


class RoutingDecision(BaseModel):
    """Result of a routing decision."""

    provider_name: str
    model_id: str
    reasoning: str
    estimated_cost: float
    estimated_response_time_ms: float
    confidence: float  # 0.0-1.0 confidence in decision
    fallback_options: list[dict[str, str]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMRouter:
    """
    Intelligent LLM routing system.

    Routes requests to optimal providers based on configurable policies
    considering cost, performance, privacy, and availability constraints.
    """

    def __init__(self, default_policy: Optional[RoutingPolicy] = None):
        """Initialize the LLM router."""
        self.providers: dict[str, LLMProvider] = {}
        self.default_policy = default_policy or RoutingPolicy()
        self.routing_cache: dict[str, tuple[RoutingDecision, datetime]] = {}
        self.provider_stats: dict[str, dict[str, Any]] = {}

        # Performance tracking
        self.response_times: dict[str, list[float]] = {}
        self.error_rates: dict[str, float] = {}
        self.last_health_check: dict[str, datetime] = {}

    async def initialize(self) -> None:
        """Initialize all registered providers."""
        logger.info("Initializing LLM router")

        for provider_name, provider in self.providers.items():
            try:
                await provider.initialize()
                self.provider_stats[provider_name] = {
                    "initialized": True,
                    "requests": 0,
                    "successes": 0,
                    "failures": 0,
                    "total_cost": 0.0,
                    "avg_response_time": 0.0,
                }
                logger.info(f"Provider {provider_name} initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize provider {provider_name}: {e}")
                self.provider_stats[provider_name] = {
                    "initialized": False,
                    "error": str(e),
                }

        logger.info(f"LLM router initialized with {len(self.providers)} providers")

    def register_provider(self, name: str, provider: LLMProvider) -> None:
        """Register a new LLM provider."""
        self.providers[name] = provider
        logger.info(f"Registered provider: {name}")

    async def route_request(
        self,
        request: LLMRequest,
        context: RoutingContext,
        policy: Optional[RoutingPolicy] = None,
    ) -> RoutingDecision:
        """
        Route a request to the optimal provider.

        Args:
            request: The LLM request to route
            context: Context information for routing
            policy: Override policy (uses default if None)

        Returns:
            RoutingDecision: Decision on which provider/model to use
        """
        routing_policy = policy or self.default_policy

        # Check cache first
        if routing_policy.enable_caching:
            cached_decision = self._check_cache(request, context, routing_policy)
            if cached_decision:
                logger.debug(f"Using cached routing decision for {context.agent_id}")
                return cached_decision

        # Get available providers
        available_providers = await self._get_available_providers(
            context.previous_failures
        )

        if not available_providers:
            raise RuntimeError("No available providers for routing")

        # Score and rank providers
        provider_scores = await self._score_providers(
            request, context, routing_policy, available_providers
        )

        if not provider_scores:
            raise RuntimeError("No suitable providers found for request")

        # Select best provider
        best_provider_name, best_score = max(
            provider_scores.items(), key=lambda x: x[1]["total_score"]
        )
        best_provider = self.providers[best_provider_name]

        # Select best model from provider
        best_model = await self._select_model(request, context, best_provider)

        # Create routing decision
        decision = RoutingDecision(
            provider_name=best_provider_name,
            model_id=best_model.id,
            reasoning=self._generate_reasoning(
                routing_policy.strategy, best_provider_name, best_score
            ),
            estimated_cost=self._estimate_cost(request, best_model),
            estimated_response_time_ms=self._estimate_response_time(best_provider_name),
            confidence=best_score["confidence"],
            fallback_options=self._get_fallback_options(
                provider_scores, best_provider_name
            ),
            metadata={
                "strategy": routing_policy.strategy.value,
                "scores": provider_scores,
                "model_info": best_model.model_dump(),
            },
        )

        # Cache decision
        if routing_policy.enable_caching:
            self._cache_decision(request, context, routing_policy, decision)

        logger.info(
            f"Routed request to {best_provider_name}/{best_model.id} "
            f"(score: {best_score['total_score']:.3f})"
        )

        return decision

    async def execute_request(
        self,
        request: LLMRequest,
        decision: RoutingDecision,
        with_fallback: bool = True,
    ) -> LLMResponse:
        """
        Execute a request using the routing decision.

        Args:
            request: The LLM request to execute
            decision: The routing decision
            with_fallback: Whether to try fallback options on failure

        Returns:
            LLMResponse: The response from the provider
        """
        provider = self.providers[decision.provider_name]
        start_time = time.time()

        try:
            # Update request with selected model
            request.model_id = decision.model_id

            # Execute request
            response = await provider.generate(request)

            # Track success
            self._track_request_success(
                decision.provider_name, time.time() - start_time, response.total_cost
            )

            return response

        except Exception as e:
            # Track failure
            self._track_request_failure(decision.provider_name, str(e))

            if with_fallback and decision.fallback_options:
                logger.warning(
                    f"Provider {decision.provider_name} failed: {e}, trying fallback"
                )

                # Try first fallback option
                fallback = decision.fallback_options[0]
                fallback_provider = self.providers[fallback["provider"]]

                try:
                    request.model_id = fallback["model"]
                    response = await fallback_provider.generate(request)

                    # Track fallback success
                    self._track_request_success(
                        fallback["provider"],
                        time.time() - start_time,
                        response.total_cost,
                    )

                    return response

                except Exception as fallback_error:
                    self._track_request_failure(
                        fallback["provider"], str(fallback_error)
                    )
                    logger.error(f"Fallback also failed: {fallback_error}")

            raise

    async def get_provider_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all providers."""
        status = {}

        for provider_name, provider in self.providers.items():
            try:
                health = await provider.health_check()
                stats = self.provider_stats.get(provider_name, {})

                status[provider_name] = {
                    "health": health.model_dump(),
                    "stats": stats,
                    "available_models": [
                        model.id for model in await provider.get_models()
                    ],
                    "last_check": datetime.utcnow().isoformat(),
                }
            except Exception as e:
                status[provider_name] = {
                    "health": {"is_healthy": False, "error": str(e)},
                    "stats": self.provider_stats.get(provider_name, {}),
                    "error": str(e),
                }

        return status

    async def _get_available_providers(
        self, excluded: Optional[list[str]] = None
    ) -> list[str]:
        """Get list of available providers."""
        excluded = excluded or []
        available = []

        for provider_name, provider in self.providers.items():
            if provider_name in excluded:
                continue

            try:
                # Check if provider is initialized and healthy
                if not self.provider_stats.get(provider_name, {}).get(
                    "initialized", False
                ):
                    continue

                # Quick health check if needed
                if (
                    provider_name not in self.last_health_check
                    or (
                        datetime.utcnow() - self.last_health_check[provider_name]
                    ).seconds
                    > 300
                ):
                    health = await provider.health_check()
                    self.last_health_check[provider_name] = datetime.utcnow()

                    if not health.is_healthy:
                        continue

                available.append(provider_name)

            except Exception as e:
                logger.warning(f"Provider {provider_name} health check failed: {e}")
                continue

        return available

    async def _score_providers(
        self,
        request: LLMRequest,
        context: RoutingContext,
        policy: RoutingPolicy,
        available_providers: list[str],
    ) -> dict[str, dict[str, float]]:
        """Score all available providers based on policy."""
        provider_scores = {}

        for provider_name in available_providers:
            provider = self.providers[provider_name]

            try:
                # Get provider models
                models = await provider.get_models()
                if not models:
                    continue

                # Find best model for this provider
                best_model = await self._select_model(request, context, provider)
                if not best_model:
                    continue

                # Calculate scores
                scores = {
                    "cost_score": self._calculate_cost_score(
                        request, best_model, policy
                    ),
                    "performance_score": self._calculate_performance_score(
                        provider_name, best_model, policy
                    ),
                    "privacy_score": self._calculate_privacy_score(best_model, policy),
                    "availability_score": self._calculate_availability_score(
                        provider_name
                    ),
                    "capability_score": self._calculate_capability_score(
                        best_model, context.task_type
                    ),
                }

                # Calculate weighted total based on strategy
                total_score = self._calculate_weighted_score(scores, policy.strategy)
                scores["total_score"] = total_score
                scores["confidence"] = min(1.0, total_score)

                provider_scores[provider_name] = scores

            except Exception as e:
                logger.warning(f"Failed to score provider {provider_name}: {e}")
                continue

        return provider_scores

    async def _select_model(
        self, request: LLMRequest, context: RoutingContext, provider: LLMProvider
    ) -> Any:  # Returns ModelInfo
        """Select the best model from a provider."""
        models = await provider.get_models()

        if not models:
            return None

        # Filter models by capability if task type is specified
        if context.task_type:
            required_capability = self._task_to_capability(context.task_type)
            if required_capability:
                models = [
                    model
                    for model in models
                    if required_capability in model.capabilities
                ]

        if not models:
            # Fallback to any model
            models = await provider.get_models()

        # Score models and select best
        best_model = None
        best_score = -1

        for model in models:
            score = 0

            # Performance tier
            score += model.performance_tier * 0.3

            # Context length (prefer longer for complex tasks)
            if context.complexity > 7:
                score += min(1.0, model.context_length / 32768) * 0.2

            # Cost efficiency (lower cost is better)
            if model.input_cost_per_token > 0:
                cost_efficiency = 1.0 / (1.0 + model.input_cost_per_token * 1000000)
                score += cost_efficiency * 0.3
            else:
                score += 0.3  # Local models get full cost efficiency score

            # Availability
            score += model.availability * 0.2

            if score > best_score:
                best_score = score
                best_model = model

        return best_model

    def _task_to_capability(self, task_type: TaskType) -> Optional[ModelCapability]:
        """Map task type to required model capability."""
        mapping = {
            TaskType.CODE_GENERATION: ModelCapability.CODE_GENERATION,
            TaskType.CODE_REVIEW: ModelCapability.CODE_GENERATION,
            TaskType.BUG_FIX: ModelCapability.CODE_GENERATION,
            TaskType.REFACTORING: ModelCapability.CODE_GENERATION,
            TaskType.TESTING: ModelCapability.CODE_GENERATION,
            TaskType.DOCUMENTATION: ModelCapability.TEXT_GENERATION,
            TaskType.SYSTEM_DESIGN: ModelCapability.REASONING,
            TaskType.TECH_DECISION: ModelCapability.REASONING,
            TaskType.ARCHITECTURE_REVIEW: ModelCapability.REASONING,
            TaskType.PERFORMANCE_ANALYSIS: ModelCapability.ANALYSIS,
            TaskType.REQUIREMENTS_ANALYSIS: ModelCapability.ANALYSIS,
            TaskType.RISK_ASSESSMENT: ModelCapability.ANALYSIS,
            TaskType.FEASIBILITY_STUDY: ModelCapability.ANALYSIS,
            TaskType.RESEARCH: ModelCapability.ANALYSIS,
            TaskType.PLANNING: ModelCapability.REASONING,
            # Default to text generation for other tasks
        }
        return mapping.get(task_type, ModelCapability.TEXT_GENERATION)

    def _calculate_cost_score(
        self, request: LLMRequest, model: Any, policy: RoutingPolicy
    ) -> float:
        """Calculate cost score (higher is better)."""
        estimated_cost = self._estimate_cost(request, model)

        if estimated_cost == 0:  # Local models
            return 1.0

        if estimated_cost > policy.max_cost_per_request:
            return 0.0  # Too expensive

        # Normalize cost score (cheaper is better)
        max_cost = policy.max_cost_per_request
        return 1.0 - (estimated_cost / max_cost)

    def _calculate_performance_score(
        self, provider_name: str, model: Any, policy: RoutingPolicy
    ) -> float:
        """Calculate performance score."""
        score = 0.0

        # Model performance tier
        if model.performance_tier >= policy.min_performance_tier:
            score += model.performance_tier / 5.0 * 0.5

        # Provider reliability
        stats = self.provider_stats.get(provider_name, {})
        if stats.get("requests", 0) > 0:
            success_rate = stats.get("successes", 0) / stats["requests"]
            score += success_rate * 0.3
        else:
            score += 0.3  # Default for new providers

        # Response time
        avg_response_time = self._estimate_response_time(provider_name)
        if avg_response_time <= policy.max_response_time_ms:
            time_score = 1.0 - (avg_response_time / policy.max_response_time_ms)
            score += time_score * 0.2

        return min(1.0, score)

    def _calculate_privacy_score(self, model: Any, policy: RoutingPolicy) -> float:
        """Calculate privacy score."""
        if policy.privacy_required and model.privacy_level != "local":
            return 0.0

        privacy_scores = {
            "local": 1.0,
            "hybrid": 0.7,
            "cloud": 0.3,
        }

        return privacy_scores.get(model.privacy_level, 0.5)

    def _calculate_availability_score(self, provider_name: str) -> float:
        """Calculate availability score."""
        stats = self.provider_stats.get(provider_name, {})

        if not stats.get("initialized", False):
            return 0.0

        error_rate = self.error_rates.get(provider_name, 0.0)
        return 1.0 - error_rate

    def _calculate_capability_score(
        self, model: Any, task_type: Optional[TaskType]
    ) -> float:
        """Calculate capability score."""
        if not task_type:
            return 1.0

        required_capability = self._task_to_capability(task_type)
        if not required_capability:
            return 1.0

        if required_capability in model.capabilities:
            return 1.0

        # Check for related capabilities
        related_score = 0.5
        if ModelCapability.TEXT_GENERATION in model.capabilities:
            related_score += 0.3

        return related_score

    def _calculate_weighted_score(
        self, scores: dict[str, float], strategy: RoutingStrategy
    ) -> float:
        """Calculate weighted total score based on strategy."""
        weights = {
            RoutingStrategy.COST_OPTIMIZED: {
                "cost_score": 0.5,
                "performance_score": 0.2,
                "privacy_score": 0.1,
                "availability_score": 0.1,
                "capability_score": 0.1,
            },
            RoutingStrategy.PERFORMANCE_OPTIMIZED: {
                "cost_score": 0.1,
                "performance_score": 0.5,
                "privacy_score": 0.1,
                "availability_score": 0.2,
                "capability_score": 0.1,
            },
            RoutingStrategy.PRIVACY_FIRST: {
                "cost_score": 0.1,
                "performance_score": 0.2,
                "privacy_score": 0.5,
                "availability_score": 0.1,
                "capability_score": 0.1,
            },
            RoutingStrategy.BALANCED: {
                "cost_score": 0.25,
                "performance_score": 0.25,
                "privacy_score": 0.2,
                "availability_score": 0.2,
                "capability_score": 0.1,
            },
        }

        strategy_weights = weights.get(strategy, weights[RoutingStrategy.BALANCED])

        total_score = 0.0
        for score_type, weight in strategy_weights.items():
            total_score += scores.get(score_type, 0.0) * weight

        return total_score

    def _estimate_cost(self, request: LLMRequest, model: Any) -> float:
        """Estimate cost for the request."""
        # Rough token estimation
        input_tokens = len(str(request.messages)) // 4  # ~4 chars per token
        output_tokens = request.max_tokens or 1000

        input_cost = input_tokens * model.input_cost_per_token
        output_cost = output_tokens * model.output_cost_per_token

        return input_cost + output_cost

    def _estimate_response_time(self, provider_name: str) -> float:
        """Estimate response time for provider."""
        if provider_name in self.response_times:
            times = self.response_times[provider_name]
            if times:
                return sum(times) / len(times)

        # Default estimates
        defaults = {
            "claude": 5000,  # 5 seconds
            "local": 10000,  # 10 seconds
        }

        return defaults.get(provider_name, 7500)

    def _generate_reasoning(
        self, strategy: RoutingStrategy, provider_name: str, scores: dict[str, float]
    ) -> str:
        """Generate human-readable reasoning for the decision."""
        top_scores = sorted(
            [
                (k, v)
                for k, v in scores.items()
                if k != "total_score" and k != "confidence"
            ],
            key=lambda x: x[1],
            reverse=True,
        )[:2]

        reasoning = f"Selected {provider_name} using {strategy.value} strategy. "
        reasoning += f"Top factors: {top_scores[0][0]}({top_scores[0][1]:.2f})"

        if len(top_scores) > 1:
            reasoning += f", {top_scores[1][0]}({top_scores[1][1]:.2f})"

        return reasoning

    def _get_fallback_options(
        self, provider_scores: dict[str, dict[str, float]], selected_provider: str
    ) -> list[dict[str, str]]:
        """Get fallback options sorted by score."""
        fallbacks = []

        sorted_providers = sorted(
            [
                (name, scores)
                for name, scores in provider_scores.items()
                if name != selected_provider
            ],
            key=lambda x: x[1]["total_score"],
            reverse=True,
        )

        for provider_name, _ in sorted_providers[:2]:  # Top 2 fallbacks
            provider = self.providers[provider_name]
            # Use first available model as fallback
            models = provider.available_models
            if models:
                fallbacks.append(
                    {
                        "provider": provider_name,
                        "model": models[0].id,
                    }
                )

        return fallbacks

    def _check_cache(
        self, request: LLMRequest, context: RoutingContext, policy: RoutingPolicy
    ) -> Optional[RoutingDecision]:
        """Check routing cache for existing decision."""
        cache_key = self._generate_cache_key(request, context, policy)

        if cache_key in self.routing_cache:
            decision, timestamp = self.routing_cache[cache_key]

            # Check if cache entry is still valid
            if datetime.utcnow() - timestamp < timedelta(
                minutes=policy.cache_ttl_minutes
            ):
                return decision
            else:
                # Remove expired entry
                del self.routing_cache[cache_key]

        return None

    def _cache_decision(
        self,
        request: LLMRequest,
        context: RoutingContext,
        policy: RoutingPolicy,
        decision: RoutingDecision,
    ) -> None:
        """Cache a routing decision."""
        cache_key = self._generate_cache_key(request, context, policy)
        self.routing_cache[cache_key] = (decision, datetime.utcnow())

        # Cleanup old entries (keep only last 1000)
        if len(self.routing_cache) > 1000:
            oldest_key = min(
                self.routing_cache.keys(), key=lambda k: self.routing_cache[k][1]
            )
            del self.routing_cache[oldest_key]

    def _generate_cache_key(
        self, request: LLMRequest, context: RoutingContext, policy: RoutingPolicy
    ) -> str:
        """Generate cache key for request."""
        key_parts = [
            str(hash(str(request.messages))),
            context.task_type.value if context.task_type else "none",
            str(context.complexity),
            str(context.privacy_sensitive),
            policy.strategy.value,
            str(policy.max_cost_per_request),
            str(policy.privacy_required),
        ]
        return ":".join(key_parts)

    def _track_request_success(
        self, provider_name: str, response_time: float, cost: float
    ) -> None:
        """Track successful request."""
        stats = self.provider_stats[provider_name]
        stats["requests"] += 1
        stats["successes"] += 1
        stats["total_cost"] += cost

        # Update response times
        if provider_name not in self.response_times:
            self.response_times[provider_name] = []

        self.response_times[provider_name].append(response_time * 1000)  # Convert to ms

        # Keep only recent response times
        if len(self.response_times[provider_name]) > 100:
            self.response_times[provider_name] = self.response_times[provider_name][
                -50:
            ]

        # Update error rate
        total_requests = stats["requests"]
        failures = stats.get("failures", 0)
        self.error_rates[provider_name] = (
            failures / total_requests if total_requests > 0 else 0.0
        )

    def _track_request_failure(self, provider_name: str, error: str) -> None:
        """Track failed request."""
        stats = self.provider_stats[provider_name]
        stats["requests"] += 1
        stats["failures"] = stats.get("failures", 0) + 1

        # Update error rate
        total_requests = stats["requests"]
        failures = stats["failures"]
        self.error_rates[provider_name] = (
            failures / total_requests if total_requests > 0 else 0.0
        )
