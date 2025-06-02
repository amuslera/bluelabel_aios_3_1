"""
Unified LLM Integration System for AIOSv3.

This module provides the main interface for using LLMs across the platform,
integrating the router, providers, and configuration.
"""

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional, Union

from .router import LLMRouter, RoutingContext, RoutingPolicy, RoutingStrategy
from .providers import (
    ClaudeProvider,
    ClaudeConfig,
    OpenAIProvider,
    OpenAIConfig,
    LocalProvider,
    LocalConfig,
    LLMRequest,
    LLMResponse,
)
from src.agents.base.types import TaskType

logger = logging.getLogger(__name__)


class LLMIntegration:
    """
    Main LLM integration class for AIOSv3.
    
    Handles initialization, routing, and execution of LLM requests
    across multiple providers with cost optimization.
    """
    
    def __init__(self):
        """Initialize the LLM integration system."""
        self.router = LLMRouter()
        self._initialized = False
        self._total_cost = 0.0
        self._request_count = 0
        self._cost_by_provider: Dict[str, float] = {}
        
    async def initialize(self) -> None:
        """Initialize all configured LLM providers."""
        if self._initialized:
            return
            
        logger.info("Initializing LLM integration system...")
        
        # Initialize Claude provider if API key is available
        claude_api_key = os.getenv("ANTHROPIC_API_KEY")
        if claude_api_key:
            try:
                claude_config = ClaudeConfig(
                    api_key=claude_api_key,
                    rate_limit_requests_per_minute=100,
                    timeout=30.0,
                )
                claude_provider = ClaudeProvider(claude_config)
                self.router.register_provider("claude", claude_provider)
                logger.info("✅ Claude provider registered")
            except Exception as e:
                logger.warning(f"Failed to register Claude provider: {e}")
        else:
            logger.warning("ANTHROPIC_API_KEY not found, Claude provider not available")
        
        # Initialize OpenAI provider if API key is available
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            try:
                openai_config = OpenAIConfig(
                    api_key=openai_api_key,
                    rate_limit_requests_per_minute=100,
                    timeout=30.0,
                )
                openai_provider = OpenAIProvider(openai_config)
                self.router.register_provider("openai", openai_provider)
                logger.info("✅ OpenAI provider registered")
            except Exception as e:
                logger.warning(f"Failed to register OpenAI provider: {e}")
        else:
            logger.warning("OPENAI_API_KEY not found, OpenAI provider not available")
        
        # Initialize Ollama provider (always try, as it's local)
        try:
            ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            local_config = LocalConfig(
                provider_type="ollama",
                base_url=ollama_base_url,
                model_discovery_enabled=True,
                timeout=60.0,  # Longer timeout for local models
            )
            local_provider = LocalProvider(local_config)
            self.router.register_provider("ollama", local_provider)
            logger.info("✅ Ollama provider registered")
        except Exception as e:
            logger.warning(f"Failed to register Ollama provider: {e}")
        
        # Initialize the router
        await self.router.initialize()
        
        # Log provider status
        status = await self.router.get_provider_status()
        for provider_name, provider_status in status.items():
            health = provider_status.get("health", {})
            if health.get("is_healthy"):
                models = provider_status.get("available_models", [])
                logger.info(f"✅ {provider_name}: {len(models)} models available")
            else:
                logger.warning(f"❌ {provider_name}: {health.get('status_message', 'unhealthy')}")
        
        self._initialized = True
        logger.info("LLM integration system initialized successfully")
    
    async def generate(
        self,
        prompt: str,
        agent_id: str = "default",
        task_type: Optional[TaskType] = None,
        complexity: int = 5,
        privacy_sensitive: bool = False,
        preferred_provider: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response using the best available LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            agent_id: ID of the agent making the request
            task_type: Type of task being performed
            complexity: Task complexity (1-10)
            privacy_sensitive: Whether the data is privacy sensitive
            preferred_provider: Preferred provider name
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            **kwargs: Additional arguments passed to the LLM
            
        Returns:
            LLMResponse with the generated content
        """
        if not self._initialized:
            await self.initialize()
        
        # Create routing context
        context = RoutingContext(
            agent_id=agent_id,
            task_type=task_type,
            complexity=complexity,
            privacy_sensitive=privacy_sensitive,
            user_preferences={"preferred_provider": preferred_provider} if preferred_provider else {},
        )
        
        # Determine routing strategy based on context
        if privacy_sensitive:
            strategy = RoutingStrategy.PRIVACY_FIRST
        elif complexity <= 3:
            strategy = RoutingStrategy.COST_OPTIMIZED
        elif complexity >= 8:
            strategy = RoutingStrategy.PERFORMANCE_OPTIMIZED
        else:
            strategy = RoutingStrategy.BALANCED
        
        # Create routing policy
        policy = RoutingPolicy(
            strategy=strategy,
            max_cost_per_request=1.0,  # $1 max per request
            privacy_required=privacy_sensitive,
            preferred_providers=[preferred_provider] if preferred_provider else [],
        )
        
        # Create LLM request
        request = LLMRequest(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        
        # Route the request
        decision = await self.router.route_request(request, context, policy)
        
        logger.info(
            f"Routing decision: {decision.provider_name}/{decision.model_id} "
            f"(strategy: {strategy.value}, cost: ${decision.estimated_cost:.4f})"
        )
        
        # Execute the request
        response = await self.router.execute_request(request, decision)
        
        # Track costs
        self._track_cost(decision.provider_name, response.total_cost)
        
        return response
    
    async def generate_with_fallback(
        self,
        prompt: str,
        providers: List[str],
        **kwargs
    ) -> Optional[LLMResponse]:
        """
        Generate a response trying multiple providers in order.
        
        Args:
            prompt: The prompt to send
            providers: List of provider names to try in order
            **kwargs: Additional arguments for generate()
            
        Returns:
            LLMResponse or None if all providers fail
        """
        for provider in providers:
            try:
                return await self.generate(
                    prompt=prompt,
                    preferred_provider=provider,
                    **kwargs
                )
            except Exception as e:
                logger.warning(f"Provider {provider} failed: {e}")
                continue
        
        logger.error(f"All providers failed for prompt: {prompt[:100]}...")
        return None
    
    def _track_cost(self, provider: str, cost: float) -> None:
        """Track cost by provider."""
        self._total_cost += cost
        self._request_count += 1
        
        if provider not in self._cost_by_provider:
            self._cost_by_provider[provider] = 0.0
        self._cost_by_provider[provider] += cost
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost tracking summary."""
        return {
            "total_cost": self._total_cost,
            "request_count": self._request_count,
            "average_cost_per_request": self._total_cost / max(1, self._request_count),
            "cost_by_provider": self._cost_by_provider,
            "cost_savings": self._calculate_cost_savings(),
        }
    
    def _calculate_cost_savings(self) -> Dict[str, float]:
        """Calculate cost savings vs using only cloud providers."""
        # Assume all requests would have gone to Claude-3.5-Sonnet
        cloud_only_cost = self._request_count * 0.05  # Estimated avg cost
        actual_cost = self._total_cost
        
        return {
            "cloud_only_estimate": cloud_only_cost,
            "actual_cost": actual_cost,
            "savings": max(0, cloud_only_cost - actual_cost),
            "savings_percentage": (
                (cloud_only_cost - actual_cost) / cloud_only_cost * 100
                if cloud_only_cost > 0 else 0
            ),
        }
    
    async def test_all_providers(self) -> Dict[str, bool]:
        """Test connectivity to all registered providers."""
        results = {}
        
        status = await self.router.get_provider_status()
        for provider_name, provider_status in status.items():
            health = provider_status.get("health", {})
            results[provider_name] = health.get("is_healthy", False)
        
        return results
    
    async def shutdown(self) -> None:
        """Shutdown all providers cleanly."""
        logger.info("Shutting down LLM integration system...")
        
        for provider_name, provider in self.router.providers.items():
            try:
                await provider.shutdown()
                logger.info(f"✅ {provider_name} provider shut down")
            except Exception as e:
                logger.error(f"Error shutting down {provider_name}: {e}")
        
        self._initialized = False
        logger.info("LLM integration system shut down")


# Global instance for easy access
llm_integration = LLMIntegration()


async def get_llm() -> LLMIntegration:
    """Get the initialized LLM integration instance."""
    if not llm_integration._initialized:
        await llm_integration.initialize()
    return llm_integration