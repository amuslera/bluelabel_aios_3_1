"""
Local model provider implementation for AIOSv3 platform.

Provides integration with local LLM services like Ollama, vLLM, and LocalAI.
"""

import asyncio
import json
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


class LocalConfig(ProviderConfig):
    """Configuration specific to local model providers."""

    provider_type: str = "ollama"  # "ollama", "vllm", "localai"
    base_url: str = "http://localhost:11434"  # Default Ollama port
    model_discovery_enabled: bool = True
    auto_pull_models: bool = False
    default_max_tokens: int = 2048
    default_temperature: float = 0.7


class LocalProvider(LLMProvider):
    """
    Provider implementation for local LLM services.

    Supports multiple local inference backends:
    - Ollama (default)
    - vLLM
    - LocalAI
    """

    def __init__(self, config: LocalConfig):
        """Initialize local provider."""
        super().__init__(config)
        self.config: LocalConfig = config
        self.client: Optional[httpx.AsyncClient] = None
        self.base_url = config.base_url or "http://localhost:11434"

        # Provider-specific API paths
        self.api_paths = self._get_api_paths()

    def _get_api_paths(self) -> dict[str, str]:
        """Get API paths based on provider type."""
        if self.config.provider_type == "ollama":
            return {
                "generate": "/api/generate",
                "chat": "/api/chat",
                "models": "/api/tags",
                "pull": "/api/pull",
                "health": "/api/tags",
            }
        elif self.config.provider_type == "vllm":
            return {
                "generate": "/v1/completions",
                "chat": "/v1/chat/completions",
                "models": "/v1/models",
                "health": "/health",
            }
        elif self.config.provider_type == "localai":
            return {
                "generate": "/v1/completions",
                "chat": "/v1/chat/completions",
                "models": "/v1/models",
                "health": "/readyz",
            }
        else:
            raise ValueError(f"Unsupported provider type: {self.config.provider_type}")

    async def initialize(self) -> None:
        """Initialize the local provider and discover available models."""
        logger.info(
            f"Initializing {self.config.provider_type} provider at {self.base_url}"
        )

        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.config.timeout,
            verify=self.config.verify_ssl,
        )

        # Discover available models
        if self.config.model_discovery_enabled:
            await self._discover_models()
        else:
            # Load default models based on provider type
            self._load_default_models()

        logger.info(f"Local provider initialized with {len(self._models)} models")

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response using local model."""
        if not self.client:
            raise RuntimeError("Provider not initialized")

        start_time = time.time()

        try:
            # Prepare request based on provider type
            if self.config.provider_type == "ollama":
                return await self._generate_ollama(request, start_time)
            else:
                return await self._generate_openai_compatible(request, start_time)

        except Exception as e:
            logger.error(f"Error generating local response: {e}")
            raise

    async def generate_stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Generate a streaming response using local model."""
        if not self.client:
            raise RuntimeError("Provider not initialized")

        try:
            if self.config.provider_type == "ollama":
                async for chunk in self._generate_stream_ollama(request):
                    yield chunk
            else:
                async for chunk in self._generate_stream_openai_compatible(request):
                    yield chunk

        except Exception as e:
            logger.error(f"Error in local streaming: {e}")
            raise

    async def get_models(self) -> list[ModelInfo]:
        """Get list of available local models."""
        return list(self._models.values())

    async def health_check(self) -> ProviderHealthStatus:
        """Perform health check on local model service."""
        if not self.client:
            return ProviderHealthStatus(
                provider_name=self.provider_name,
                is_healthy=False,
                status_message="Provider not initialized",
            )

        start_time = time.time()

        try:
            # Use provider-specific health endpoint
            health_path = self.api_paths["health"]
            response = await self.client.get(health_path, timeout=10.0)
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                return ProviderHealthStatus(
                    provider_name=self.provider_name,
                    is_healthy=True,
                    response_time_ms=response_time,
                    available_models=list(self._models.keys()),
                    status_message=f"{self.config.provider_type} service healthy",
                )
            else:
                return ProviderHealthStatus(
                    provider_name=self.provider_name,
                    is_healthy=False,
                    response_time_ms=response_time,
                    status_message=f"Service returned status {response.status_code}",
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
        logger.info("Local provider shutdown completed")

    async def _discover_models(self) -> None:
        """Discover available models from the local service."""
        try:
            models_path = self.api_paths["models"]
            response = await self.client.get(models_path, timeout=30.0)
            response.raise_for_status()

            models_data = response.json()

            if self.config.provider_type == "ollama":
                await self._parse_ollama_models(models_data)
            else:
                await self._parse_openai_compatible_models(models_data)

        except Exception as e:
            logger.warning(f"Model discovery failed: {e}, loading defaults")
            self._load_default_models()

    async def _parse_ollama_models(self, models_data: dict[str, Any]) -> None:
        """Parse Ollama models response."""
        models = models_data.get("models", [])

        for model_data in models:
            model_name = model_data.get("name", "")
            model_size_bytes = model_data.get("size", 0)

            # Estimate model size category from bytes
            size_gb = model_size_bytes / (1024**3)
            if size_gb < 1:
                size_category = ModelSize.SMALL
            elif size_gb < 10:
                size_category = ModelSize.MEDIUM
            elif size_gb < 50:
                size_category = ModelSize.LARGE
            else:
                size_category = ModelSize.XLARGE

            # Determine capabilities based on model name
            capabilities = self._infer_capabilities_from_name(model_name)

            model_info = ModelInfo(
                id=model_name,
                name=model_name,
                provider=self.provider_name,
                model_type=ModelType.CHAT,
                size=size_category,
                capabilities=capabilities,
                context_length=self._infer_context_length(model_name),
                input_cost_per_token=0.0,  # Local models are free
                output_cost_per_token=0.0,
                supports_streaming=True,
                supports_functions=False,  # Most local models don't support function calling
                privacy_level="local",
                performance_tier=self._infer_performance_tier(model_name),
                availability=0.95,  # Lower than cloud due to local dependencies
                metadata={
                    "size_bytes": model_size_bytes,
                    "size_gb": round(size_gb, 2),
                    "provider_type": "ollama",
                },
            )

            self._models[model_name] = model_info

    async def _parse_openai_compatible_models(
        self, models_data: dict[str, Any]
    ) -> None:
        """Parse OpenAI-compatible models response."""
        models = models_data.get("data", [])

        for model_data in models:
            model_id = model_data.get("id", "")

            capabilities = self._infer_capabilities_from_name(model_id)

            model_info = ModelInfo(
                id=model_id,
                name=model_id,
                provider=self.provider_name,
                model_type=ModelType.CHAT,
                size=ModelSize.MEDIUM,  # Default assumption
                capabilities=capabilities,
                context_length=self._infer_context_length(model_id),
                input_cost_per_token=0.0,
                output_cost_per_token=0.0,
                supports_streaming=True,
                supports_functions=False,
                privacy_level="local",
                performance_tier=3,  # Default assumption
                availability=0.95,
                metadata={
                    "provider_type": self.config.provider_type,
                },
            )

            self._models[model_id] = model_info

    def _load_default_models(self) -> None:
        """Load default model configurations when discovery fails."""
        if self.config.provider_type == "ollama":
            default_models = {
                "llama2": ModelInfo(
                    id="llama2",
                    name="Llama 2",
                    provider=self.provider_name,
                    model_type=ModelType.CHAT,
                    size=ModelSize.LARGE,
                    capabilities=[
                        ModelCapability.TEXT_GENERATION,
                        ModelCapability.REASONING,
                        ModelCapability.ANALYSIS,
                    ],
                    context_length=4096,
                    privacy_level="local",
                    performance_tier=3,
                ),
                "codellama": ModelInfo(
                    id="codellama",
                    name="Code Llama",
                    provider=self.provider_name,
                    model_type=ModelType.CODE,
                    size=ModelSize.LARGE,
                    capabilities=[
                        ModelCapability.CODE_GENERATION,
                        ModelCapability.TEXT_GENERATION,
                    ],
                    context_length=16384,
                    privacy_level="local",
                    performance_tier=4,
                ),
            }
        else:
            default_models = {
                "local-model": ModelInfo(
                    id="local-model",
                    name="Local Model",
                    provider=self.provider_name,
                    model_type=ModelType.CHAT,
                    size=ModelSize.MEDIUM,
                    capabilities=[ModelCapability.TEXT_GENERATION],
                    context_length=2048,
                    privacy_level="local",
                    performance_tier=3,
                ),
            }

        self._models.update(default_models)

    def _infer_capabilities_from_name(self, model_name: str) -> list[ModelCapability]:
        """Infer model capabilities from name."""
        capabilities = [ModelCapability.TEXT_GENERATION]

        name_lower = model_name.lower()

        if any(term in name_lower for term in ["code", "programming", "developer"]):
            capabilities.append(ModelCapability.CODE_GENERATION)

        if any(term in name_lower for term in ["chat", "instruct", "assistant"]):
            capabilities.extend(
                [
                    ModelCapability.REASONING,
                    ModelCapability.ANALYSIS,
                ]
            )

        if "math" in name_lower:
            capabilities.append(ModelCapability.MATH)

        if any(term in name_lower for term in ["creative", "write", "story"]):
            capabilities.append(ModelCapability.CREATIVE_WRITING)

        return capabilities

    def _infer_context_length(self, model_name: str) -> int:
        """Infer context length from model name."""
        name_lower = model_name.lower()

        if "32k" in name_lower:
            return 32768
        elif "16k" in name_lower:
            return 16384
        elif "8k" in name_lower:
            return 8192
        elif "4k" in name_lower:
            return 4096
        else:
            return 2048  # Conservative default

    def _infer_performance_tier(self, model_name: str) -> int:
        """Infer performance tier from model name."""
        name_lower = model_name.lower()

        if any(term in name_lower for term in ["70b", "65b", "large", "xl"]):
            return 4
        elif any(term in name_lower for term in ["30b", "33b", "medium"]):
            return 3
        elif any(term in name_lower for term in ["13b", "7b", "small"]):
            return 2
        else:
            return 1

    async def _generate_ollama(
        self, request: LLMRequest, start_time: float
    ) -> LLMResponse:
        """Generate response using Ollama API."""
        # Convert messages to Ollama format
        if len(request.messages) == 1 and request.messages[0].get("role") == "user":
            # Use generate endpoint for simple prompts
            payload = {
                "model": request.model_id,
                "prompt": request.messages[0]["content"],
                "stream": False,
                "options": {
                    "temperature": request.temperature,
                    "num_predict": request.max_tokens or self.config.default_max_tokens,
                },
            }

            response = await self.client.post(self.api_paths["generate"], json=payload)
        else:
            # Use chat endpoint for conversations
            payload = {
                "model": request.model_id,
                "messages": request.messages,
                "stream": False,
                "options": {
                    "temperature": request.temperature,
                    "num_predict": request.max_tokens or self.config.default_max_tokens,
                },
            }

            response = await self.client.post(self.api_paths["chat"], json=payload)

        response.raise_for_status()
        response_data = response.json()

        response_time = (time.time() - start_time) * 1000

        # Extract content based on response format
        if "response" in response_data:
            content = response_data["response"]
        elif "message" in response_data:
            content = response_data["message"].get("content", "")
        else:
            content = ""

        return self._create_response(
            content=content,
            model_id=request.model_id,
            response_time_ms=response_time,
            metadata={"provider_type": "ollama"},
        )

    async def _generate_openai_compatible(
        self, request: LLMRequest, start_time: float
    ) -> LLMResponse:
        """Generate response using OpenAI-compatible API."""
        payload = {
            "model": request.model_id,
            "messages": request.messages,
            "max_tokens": request.max_tokens or self.config.default_max_tokens,
            "temperature": request.temperature,
            "stream": False,
        }

        response = await self.client.post(self.api_paths["chat"], json=payload)
        response.raise_for_status()
        response_data = response.json()

        response_time = (time.time() - start_time) * 1000

        # Parse OpenAI-style response
        choices = response_data.get("choices", [])
        content = ""
        if choices:
            message = choices[0].get("message", {})
            content = message.get("content", "")

        return self._create_response(
            content=content,
            model_id=request.model_id,
            response_time_ms=response_time,
            metadata={"provider_type": self.config.provider_type},
        )

    async def _generate_stream_ollama(self, request: LLMRequest) -> AsyncIterator[str]:
        """Generate streaming response using Ollama API."""
        payload = {
            "model": request.model_id,
            "messages": request.messages,
            "stream": True,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens or self.config.default_max_tokens,
            },
        }

        async with self.client.stream(
            "POST", self.api_paths["chat"], json=payload
        ) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
                        elif "response" in data:
                            yield data["response"]
                    except json.JSONDecodeError:
                        continue

    async def _generate_stream_openai_compatible(
        self, request: LLMRequest
    ) -> AsyncIterator[str]:
        """Generate streaming response using OpenAI-compatible API."""
        payload = {
            "model": request.model_id,
            "messages": request.messages,
            "max_tokens": request.max_tokens or self.config.default_max_tokens,
            "temperature": request.temperature,
            "stream": True,
        }

        async with self.client.stream(
            "POST", self.api_paths["chat"], json=payload
        ) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        break

                    try:
                        event_data = json.loads(data)
                        choices = event_data.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue
