"""
LLM routing system for AIOSv3 platform.
Handles dynamic routing between cloud and local models.
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


@dataclass
class RoutingDecision:
    """Represents a routing decision for an LLM request."""

    model_id: str
    reason: str
    confidence: float
    estimated_cost: float
    provider: str
    model_type: str  # "cloud" or "local"


class ModelConfig:
    """Configuration for a single model."""

    def __init__(self, config_dict: dict[str, Any]):
        self.model_id = config_dict.get("model_id", "")
        self.provider = config_dict.get("provider", "")
        self.type = config_dict.get("type", "cloud")
        self.capabilities = config_dict.get("capabilities", [])
        self.cost_per_1k_tokens = config_dict.get("cost_per_1k_tokens", {})
        self.enabled = config_dict.get("enabled", True)
        self.endpoint = config_dict.get("endpoint")
        self.max_tokens = config_dict.get("max_tokens", 4096)
        self.temperature = config_dict.get("temperature", 0.7)


class LLMRouter:
    """
    Intelligent router for LLM requests.

    Routes requests to the most appropriate model based on:
    - Task complexity and type
    - Cost considerations
    - Privacy requirements
    - Model availability
    - Agent preferences
    """

    def __init__(self, config_path: str | None = None):
        """
        Initialize the LLM router.

        Args:
            config_path: Path to configuration directory
        """
        self.config_path = config_path or "config"
        self.models: dict[str, ModelConfig] = {}
        self.agents: dict[str, dict] = {}
        self.routing_config: dict[str, Any] = {}
        self.daily_cost_tracker = 0.0

        self._load_configurations()

    def _load_configurations(self) -> None:
        """Load model and agent configurations."""
        try:
            # Load models configuration
            models_path = Path(self.config_path) / "models.yaml"
            if models_path.exists():
                with open(models_path) as f:
                    models_config = yaml.safe_load(f)
                    for model_name, config in models_config.get("models", {}).items():
                        self.models[model_name] = ModelConfig(config)

            # Load agents configuration
            agents_path = Path(self.config_path) / "agents.yaml"
            if agents_path.exists():
                with open(agents_path) as f:
                    agents_config = yaml.safe_load(f)
                    self.agents = agents_config.get("agents", {})

            # Load routing configuration (if exists)
            routing_path = Path(self.config_path) / "routing.yaml"
            if routing_path.exists():
                with open(routing_path) as f:
                    self.routing_config = yaml.safe_load(f)

            logger.info(
                f"Loaded {len(self.models)} models and {len(self.agents)} agent configs"
            )

        except Exception as e:
            logger.error(f"Failed to load configurations: {e}")
            # Set defaults
            self._set_default_configurations()

    def _set_default_configurations(self) -> None:
        """Set default configurations when loading fails."""
        logger.warning("Using default configurations")

        # Default cloud models
        self.models["claude-3-sonnet"] = ModelConfig(
            {
                "model_id": "claude-3-sonnet-20240229",
                "provider": "anthropic",
                "type": "cloud",
                "capabilities": ["code_generation", "general_reasoning"],
                "cost_per_1k_tokens": {"input": 0.003, "output": 0.015},
                "enabled": True,
            }
        )

        self.models["gpt-4-turbo"] = ModelConfig(
            {
                "model_id": "gpt-4-turbo-preview",
                "provider": "openai",
                "type": "cloud",
                "capabilities": ["code_generation", "problem_solving"],
                "cost_per_1k_tokens": {"input": 0.01, "output": 0.03},
                "enabled": True,
            }
        )

    async def route_request(
        self, agent_id: str, task: dict[str, Any], context: dict[str, Any]
    ) -> RoutingDecision:
        """
        Route a request to the most appropriate model.

        Args:
            agent_id: ID of the requesting agent
            task: Task details
            context: Additional context

        Returns:
            RoutingDecision: Decision about which model to use
        """
        try:
            # Get agent configuration
            agent_config = self.agents.get(agent_id, {})

            # Apply routing rules first
            rule_decision = self._apply_routing_rules(agent_config, task, context)
            if rule_decision:
                return rule_decision

            # Apply routing strategy
            strategy_decision = self._apply_routing_strategy(
                agent_config, task, context
            )
            if strategy_decision:
                return strategy_decision

            # Fallback to agent preferences
            return self._apply_agent_preferences(agent_config, task, context)

        except Exception as e:
            logger.error(f"Routing failed for agent {agent_id}: {e}")
            return self._get_fallback_decision()

    def _apply_routing_rules(
        self,
        agent_config: dict[str, Any],
        task: dict[str, Any],
        context: dict[str, Any],
    ) -> RoutingDecision | None:
        """Apply specific routing rules defined for the agent."""

        routing_rules = agent_config.get("routing_rules", [])

        for rule in routing_rules:
            condition = rule.get("condition", "")
            model_id = rule.get("model", "")

            if self._evaluate_condition(condition, task, context):
                if model_id in self.models and self.models[model_id].enabled:
                    model_config = self.models[model_id]
                    return RoutingDecision(
                        model_id=model_id,
                        reason=f"Rule: {condition}",
                        confidence=0.9,
                        estimated_cost=self._estimate_cost(model_config, task),
                        provider=model_config.provider,
                        model_type=model_config.type,
                    )

        return None

    def _apply_routing_strategy(
        self,
        agent_config: dict[str, Any],
        task: dict[str, Any],
        context: dict[str, Any],
    ) -> RoutingDecision | None:
        """Apply global routing strategy."""

        strategy = context.get("routing_strategy", "balanced")

        if strategy == "cost_optimized":
            return self._route_cost_optimized(agent_config, task)
        elif strategy == "performance_optimized":
            return self._route_performance_optimized(agent_config, task)
        elif strategy == "privacy_first":
            return self._route_privacy_first(agent_config, task)
        else:  # balanced
            return self._route_balanced(agent_config, task)

    def _apply_agent_preferences(
        self,
        agent_config: dict[str, Any],
        task: dict[str, Any],
        context: dict[str, Any],
    ) -> RoutingDecision:
        """Apply agent's model preferences."""

        preferences = agent_config.get("model_preferences", {})

        # Check budget mode
        daily_budget = float(os.getenv("DAILY_CLOUD_BUDGET", "50.0"))
        if self.daily_cost_tracker > daily_budget * 0.8:
            budget_model = preferences.get("budget_mode")
            if budget_model and budget_model in self.models:
                model_config = self.models[budget_model]
                return RoutingDecision(
                    model_id=budget_model,
                    reason="Budget limit approaching",
                    confidence=0.8,
                    estimated_cost=self._estimate_cost(model_config, task),
                    provider=model_config.provider,
                    model_type=model_config.type,
                )

        # Try primary model
        primary_model = preferences.get("primary", "claude-3-sonnet")
        if primary_model in self.models and self.models[primary_model].enabled:
            model_config = self.models[primary_model]
            return RoutingDecision(
                model_id=primary_model,
                reason="Agent preference: primary",
                confidence=0.7,
                estimated_cost=self._estimate_cost(model_config, task),
                provider=model_config.provider,
                model_type=model_config.type,
            )

        # Fallback model
        fallback_model = preferences.get("fallback", "claude-3-sonnet")
        model_config = self.models.get(fallback_model, self.models["claude-3-sonnet"])
        return RoutingDecision(
            model_id=fallback_model,
            reason="Agent preference: fallback",
            confidence=0.6,
            estimated_cost=self._estimate_cost(model_config, task),
            provider=model_config.provider,
            model_type=model_config.type,
        )

    def _evaluate_condition(
        self, condition: str, task: dict[str, Any], context: dict[str, Any]
    ) -> bool:
        """Evaluate a routing condition."""
        try:
            # Simple implementation - would be more sophisticated in production
            eval_context = {
                "task": task,
                "context": context,
                "cost_limit_reached": self.daily_cost_tracker
                > float(os.getenv("DAILY_CLOUD_BUDGET", "50.0")) * 0.8,
                "budget_mode": context.get("budget_mode", False),
            }

            return eval(condition, {"__builtins__": {}}, eval_context)
        except Exception as e:
            logger.warning(f"Failed to evaluate condition '{condition}': {e}")
            return False

    def _route_cost_optimized(
        self, agent_config: dict[str, Any], task: dict[str, Any]
    ) -> RoutingDecision:
        """Route using cost optimization strategy."""

        # Prefer local models
        local_models = [
            model_id
            for model_id, config in self.models.items()
            if config.type == "local" and config.enabled
        ]

        if local_models:
            model_id = local_models[0]  # Pick first available local model
            model_config = self.models[model_id]
            return RoutingDecision(
                model_id=model_id,
                reason="Cost optimization: local model",
                confidence=0.8,
                estimated_cost=0.0,
                provider=model_config.provider,
                model_type="local",
            )

        # Otherwise, pick cheapest cloud model
        cheapest_model = min(
            [(k, v) for k, v in self.models.items() if v.type == "cloud" and v.enabled],
            key=lambda x: x[1].cost_per_1k_tokens.get("input", 0.0),
            default=("claude-3-sonnet", self.models["claude-3-sonnet"]),
        )

        model_id, model_config = cheapest_model
        return RoutingDecision(
            model_id=model_id,
            reason="Cost optimization: cheapest cloud model",
            confidence=0.7,
            estimated_cost=self._estimate_cost(model_config, task),
            provider=model_config.provider,
            model_type="cloud",
        )

    def _route_performance_optimized(
        self, agent_config: dict[str, Any], task: dict[str, Any]
    ) -> RoutingDecision:
        """Route using performance optimization strategy."""

        # Prefer most capable cloud models
        if "claude-3-opus" in self.models and self.models["claude-3-opus"].enabled:
            model_config = self.models["claude-3-opus"]
            return RoutingDecision(
                model_id="claude-3-opus",
                reason="Performance optimization: most capable model",
                confidence=0.9,
                estimated_cost=self._estimate_cost(model_config, task),
                provider=model_config.provider,
                model_type="cloud",
            )

        return self._get_fallback_decision()

    def _route_privacy_first(
        self, agent_config: dict[str, Any], task: dict[str, Any]
    ) -> RoutingDecision:
        """Route using privacy-first strategy."""

        # Only use local models
        local_models = [
            model_id
            for model_id, config in self.models.items()
            if config.type == "local" and config.enabled
        ]

        if local_models:
            model_id = local_models[0]
            model_config = self.models[model_id]
            return RoutingDecision(
                model_id=model_id,
                reason="Privacy first: local model only",
                confidence=0.9,
                estimated_cost=0.0,
                provider=model_config.provider,
                model_type="local",
            )

        raise ValueError("No local models available for privacy-first routing")

    def _route_balanced(
        self, agent_config: dict[str, Any], task: dict[str, Any]
    ) -> RoutingDecision:
        """Route using balanced strategy."""

        # Use task complexity to decide
        complexity = task.get("complexity", 5)

        if complexity >= 8:
            # High complexity - use powerful cloud model
            if "claude-3-opus" in self.models and self.models["claude-3-opus"].enabled:
                model_config = self.models["claude-3-opus"]
                return RoutingDecision(
                    model_id="claude-3-opus",
                    reason="Balanced: high complexity task",
                    confidence=0.8,
                    estimated_cost=self._estimate_cost(model_config, task),
                    provider=model_config.provider,
                    model_type="cloud",
                )
        elif complexity <= 3:
            # Low complexity - try local model
            local_models = [
                model_id
                for model_id, config in self.models.items()
                if config.type == "local" and config.enabled
            ]
            if local_models:
                model_id = local_models[0]
                model_config = self.models[model_id]
                return RoutingDecision(
                    model_id=model_id,
                    reason="Balanced: low complexity, use local",
                    confidence=0.7,
                    estimated_cost=0.0,
                    provider=model_config.provider,
                    model_type="local",
                )

        # Medium complexity - use mid-tier cloud model
        model_config = self.models["claude-3-sonnet"]
        return RoutingDecision(
            model_id="claude-3-sonnet",
            reason="Balanced: medium complexity",
            confidence=0.7,
            estimated_cost=self._estimate_cost(model_config, task),
            provider=model_config.provider,
            model_type="cloud",
        )

    def _estimate_cost(self, model_config: ModelConfig, task: dict[str, Any]) -> float:
        """Estimate the cost of running a task on a model."""
        if model_config.type == "local":
            return 0.0

        # Rough estimation based on task description length
        task_description = task.get("description", "")
        estimated_input_tokens = (
            len(task_description.split()) * 1.3
        )  # Rough approximation
        estimated_output_tokens = (
            estimated_input_tokens * 0.5
        )  # Assume response is half the input

        cost_per_1k = model_config.cost_per_1k_tokens
        input_cost = (estimated_input_tokens / 1000) * cost_per_1k.get("input", 0.0)
        output_cost = (estimated_output_tokens / 1000) * cost_per_1k.get("output", 0.0)

        return input_cost + output_cost

    def _get_fallback_decision(self) -> RoutingDecision:
        """Get a fallback routing decision."""
        model_config = self.models.get("claude-3-sonnet")
        if model_config:
            return RoutingDecision(
                model_id="claude-3-sonnet",
                reason="Fallback decision",
                confidence=0.5,
                estimated_cost=0.01,  # Small fallback cost
                provider=model_config.provider,
                model_type=model_config.type,
            )

        # Ultimate fallback
        return RoutingDecision(
            model_id="claude-3-sonnet",
            reason="Ultimate fallback",
            confidence=0.3,
            estimated_cost=0.01,
            provider="anthropic",
            model_type="cloud",
        )

    def track_cost(self, cost: float) -> None:
        """Track the cost of a completed request."""
        self.daily_cost_tracker += cost

    def get_cost_summary(self) -> dict[str, float]:
        """Get cost tracking summary."""
        daily_budget = float(os.getenv("DAILY_CLOUD_BUDGET", "50.0"))
        return {
            "daily_spent": self.daily_cost_tracker,
            "daily_budget": daily_budget,
            "remaining_budget": max(0, daily_budget - self.daily_cost_tracker),
            "budget_used_percent": (self.daily_cost_tracker / daily_budget) * 100,
        }
