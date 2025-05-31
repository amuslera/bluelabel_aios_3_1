"""
Claude provider implementation for AIOSv3 platform.

Provides integration with Anthropic's Claude API for cloud-based LLM services.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, AsyncIterator, Optional

import httpx
from pydantic import BaseModel

from .base import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
    ModelInfo,
    ModelCapability,
    ModelSize,
    ModelType,
    ProviderConfig,
    ProviderHealthStatus,
)

logger = logging.getLogger(__name__)


class ClaudeConfig(ProviderConfig):
    """Configuration specific to Claude provider."""

    api_version: str = "2023-06-01"
    max_tokens_default: int = 4096
    temperature_default: float = 0.7
    organization_id: Optional[str] = None


class ClaudeProvider(LLMProvider):
    """
    Provider implementation for Anthropic's Claude API.

    Supports Claude 3 models with chat completions, function calling,
    and streaming responses.
    """

    # Claude model definitions
    CLAUDE_MODELS = {
        "claude-3-5-sonnet-20241022": ModelInfo(
            id="claude-3-5-sonnet-20241022",
            name="Claude 3.5 Sonnet",
            provider="claude",
            model_type=ModelType.CHAT,
            size=ModelSize.LARGE,
            capabilities=[
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CODE_GENERATION,
                ModelCapability.REASONING,
                ModelCapability.ANALYSIS,
                ModelCapability.CREATIVE_WRITING,
                ModelCapability.MATH,
                ModelCapability.TOOL_USE,
                ModelCapability.VISION,
            ],
            context_length=200000,
            input_cost_per_token=3.0e-6,  # $3.00 per million tokens
            output_cost_per_token=15.0e-6,  # $15.00 per million tokens
            max_requests_per_minute=1000,
            supports_streaming=True,
            supports_functions=True,
            privacy_level="cloud",
            performance_tier=5,
            availability=0.995,
        ),
        "claude-3-opus-20240229": ModelInfo(
            id="claude-3-opus-20240229",
            name="Claude 3 Opus",
            provider="claude",
            model_type=ModelType.CHAT,
            size=ModelSize.XLARGE,
            capabilities=[
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CODE_GENERATION,
                ModelCapability.REASONING,
                ModelCapability.ANALYSIS,
                ModelCapability.CREATIVE_WRITING,
                ModelCapability.MATH,
                ModelCapability.TOOL_USE,
                ModelCapability.VISION,
            ],
            context_length=200000,
            input_cost_per_token=15.0e-6,  # $15.00 per million tokens
            output_cost_per_token=75.0e-6,  # $75.00 per million tokens
            max_requests_per_minute=1000,
            supports_streaming=True,
            supports_functions=True,
            privacy_level="cloud",
            performance_tier=5,
            availability=0.99,
        ),
        "claude-3-haiku-20240307": ModelInfo(
            id="claude-3-haiku-20240307",
            name="Claude 3 Haiku",
            provider="claude",
            model_type=ModelType.CHAT,
            size=ModelSize.MEDIUM,
            capabilities=[
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CODE_GENERATION,
                ModelCapability.REASONING,
                ModelCapability.ANALYSIS,
                ModelCapability.CREATIVE_WRITING,
                ModelCapability.TOOL_USE,
            ],
            context_length=200000,
            input_cost_per_token=0.25e-6,  # $0.25 per million tokens
            output_cost_per_token=1.25e-6,  # $1.25 per million tokens
            max_requests_per_minute=1000,
            supports_streaming=True,
            supports_functions=True,
            privacy_level="cloud",
            performance_tier=4,
            availability=0.995,
        ),
    }

    def __init__(self, config: ClaudeConfig):
        """Initialize Claude provider."""
        super().__init__(config)
        self.config: ClaudeConfig = config
        self.client: Optional[httpx.AsyncClient] = None
        self.base_url = config.api_base or "https://api.anthropic.com"

        # Rate limiting
        self._request_timestamps: list[float] = []
        self._request_lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize the Claude provider and load available models."""
        logger.info("Initializing Claude provider")

        if not self.config.api_key:
            raise ValueError("Claude API key is required")

        # Initialize HTTP client
        headers = {
            "x-api-key": self.config.api_key,
            "anthropic-version": self.config.api_version,
            "content-type": "application/json",
        }

        if self.config.organization_id:
            headers["anthropic-organization"] = self.config.organization_id

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=self.config.timeout,
            verify=self.config.verify_ssl,
        )

        # Load available models
        self._models = self.CLAUDE_MODELS.copy()

        # Verify API access
        await self._verify_api_access()

        logger.info(f"Claude provider initialized with {len(self._models)} models")

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response using Claude API."""
        if not self.client:
            raise RuntimeError("Provider not initialized")

        start_time = time.time()

        try:
            # Rate limiting
            await self._enforce_rate_limits()

            # Prepare request payload
            payload = self._prepare_request_payload(request)

            # Make API request
            response = await self.client.post("/v1/messages", json=payload)
            response.raise_for_status()

            # Parse response
            response_data = response.json()
            return self._parse_response(request, response_data, start_time)

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Claude API error: {e.response.status_code} - {e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"Error generating Claude response: {e}")
            raise

    async def generate_stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Generate a streaming response using Claude API."""
        if not self.client:
            raise RuntimeError("Provider not initialized")

        try:
            # Rate limiting
            await self._enforce_rate_limits()

            # Prepare request payload
            payload = self._prepare_request_payload(request)
            payload["stream"] = True

            # Make streaming request
            async with self.client.stream(
                "POST", "/v1/messages", json=payload
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        if data.strip() == "[DONE]":
                            break

                        try:
                            import json

                            event_data = json.loads(data)

                            if event_data.get("type") == "content_block_delta":
                                delta = event_data.get("delta", {})
                                if delta.get("type") == "text_delta":
                                    yield delta.get("text", "")

                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            logger.error(f"Error in Claude streaming: {e}")
            raise

    async def get_models(self) -> list[ModelInfo]:
        """Get list of available Claude models."""
        return list(self._models.values())

    async def health_check(self) -> ProviderHealthStatus:
        """Perform health check on Claude API."""
        if not self.client:
            return ProviderHealthStatus(
                provider_name=self.provider_name,
                is_healthy=False,
                status_message="Provider not initialized",
            )

        start_time = time.time()

        try:
            # Simple API health check
            response = await self.client.get("/v1/models", timeout=10.0)
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                return ProviderHealthStatus(
                    provider_name=self.provider_name,
                    is_healthy=True,
                    response_time_ms=response_time,
                    available_models=list(self._models.keys()),
                    status_message="API accessible",
                )
            else:
                return ProviderHealthStatus(
                    provider_name=self.provider_name,
                    is_healthy=False,
                    response_time_ms=response_time,
                    status_message=f"API returned status {response.status_code}",
                )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return ProviderHealthStatus(
                provider_name=self.provider_name,
                is_healthy=False,
                response_time_ms=response_time,
                status_message=f"Health check failed: {e}",
            )

    async def shutdown(self) -> None:
        """Shutdown the provider and cleanup resources."""
        if self.client:
            await self.client.aclose()
            self.client = None
        logger.info("Claude provider shutdown completed")

    def _prepare_request_payload(self, request: LLMRequest) -> dict[str, Any]:
        """Prepare the request payload for Claude API."""
        payload = {
            "model": request.model_id,
            "messages": request.messages,
            "max_tokens": request.max_tokens or self.config.max_tokens_default,
            "temperature": request.temperature,
        }

        # Optional parameters
        if request.top_p is not None:
            payload["top_p"] = request.top_p

        if request.stop_sequences:
            payload["stop_sequences"] = request.stop_sequences

        # Tool use support
        if request.functions:
            payload["tools"] = self._convert_functions_to_tools(request.functions)

        return payload

    def _convert_functions_to_tools(
        self, functions: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Convert OpenAI-style functions to Claude tools format."""
        tools = []
        for func in functions:
            tool = {
                "name": func["name"],
                "description": func.get("description", ""),
                "input_schema": func.get("parameters", {}),
            }
            tools.append(tool)
        return tools

    def _parse_response(
        self, request: LLMRequest, response_data: dict[str, Any], start_time: float
    ) -> LLMResponse:
        """Parse Claude API response into LLMResponse."""
        response_time = (time.time() - start_time) * 1000

        # Extract content
        content = ""
        function_call = None

        if "content" in response_data:
            for block in response_data["content"]:
                if block["type"] == "text":
                    content += block["text"]
                elif block["type"] == "tool_use":
                    function_call = {
                        "name": block["name"],
                        "arguments": block["input"],
                    }

        # Extract usage information
        usage = response_data.get("usage", {})
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)

        # Calculate costs
        model_info = self.get_model_info(request.model_id)
        input_cost = 0.0
        output_cost = 0.0

        if model_info:
            input_cost = input_tokens * model_info.input_cost_per_token
            output_cost = output_tokens * model_info.output_cost_per_token

        return LLMResponse(
            content=content,
            model_id=request.model_id,
            provider=self.provider_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=input_cost + output_cost,
            response_time_ms=response_time,
            finish_reason=response_data.get("stop_reason"),
            function_call=function_call,
            request_id=response_data.get("id"),
        )

    async def _verify_api_access(self) -> None:
        """Verify API access by making a test request."""
        try:
            response = await self.client.get("/v1/models", timeout=10.0)
            if response.status_code not in [
                200,
                404,
            ]:  # 404 is OK, means endpoint not found but auth works
                response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError("Invalid Claude API key")
            elif e.response.status_code == 403:
                raise ValueError("Claude API access forbidden")
            else:
                logger.warning(f"API verification returned {e.response.status_code}")
        except Exception as e:
            logger.warning(f"API verification failed: {e}")

    async def _enforce_rate_limits(self) -> None:
        """Enforce rate limiting for Claude API."""
        if (
            not hasattr(self.config, "rate_limit_requests_per_minute")
            or not self.config.rate_limit_requests_per_minute
        ):
            return

        async with self._request_lock:
            current_time = time.time()

            # Remove timestamps older than 1 minute
            self._request_timestamps = [
                ts for ts in self._request_timestamps if current_time - ts < 60
            ]

            # Check if we're at the rate limit
            if (
                len(self._request_timestamps)
                >= self.config.rate_limit_requests_per_minute
            ):
                # Calculate wait time until oldest request expires
                oldest_request = min(self._request_timestamps)
                wait_time = 60 - (current_time - oldest_request)

                if wait_time > 0:
                    logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                    await asyncio.sleep(wait_time)

            # Add current request timestamp
            self._request_timestamps.append(current_time)
