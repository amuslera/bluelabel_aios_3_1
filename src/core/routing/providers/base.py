"""
Base LLM provider interface for AIOSv3 platform.

Defines the common interface that all LLM providers must implement,
enabling consistent integration across cloud and local models.
"""

import time
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Optional, Union

from pydantic import BaseModel, Field


class ModelType(Enum):
    """Types of LLM models."""

    CHAT = "chat"  # Chat/conversation models
    COMPLETION = "completion"  # Text completion models
    CODE = "code"  # Code generation models
    EMBEDDING = "embedding"  # Embedding models


class ModelSize(Enum):
    """Model size categories."""

    SMALL = "small"  # <1B parameters
    MEDIUM = "medium"  # 1B-10B parameters
    LARGE = "large"  # 10B-70B parameters
    XLARGE = "xlarge"  # >70B parameters


class ModelCapability(Enum):
    """Model capabilities."""

    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    MATH = "math"
    ANALYSIS = "analysis"
    CREATIVE_WRITING = "creative_writing"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    TOOL_USE = "tool_use"
    VISION = "vision"
    AUDIO = "audio"


class ModelInfo(BaseModel):
    """Information about an available model."""

    id: str
    name: str
    provider: str
    model_type: ModelType
    size: ModelSize
    capabilities: list[ModelCapability]
    context_length: int
    input_cost_per_token: float = 0.0  # Cost per input token in USD
    output_cost_per_token: float = 0.0  # Cost per output token in USD
    max_requests_per_minute: Optional[int] = None
    supports_streaming: bool = True
    supports_functions: bool = False
    privacy_level: str = "cloud"  # "local", "cloud", "hybrid"
    performance_tier: int = 1  # 1-5, higher is better
    availability: float = 0.99  # Availability SLA
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProviderConfig(BaseModel):
    """Configuration for an LLM provider."""

    provider_name: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    timeout: float = 30.0
    max_retries: int = 3
    rate_limit_requests_per_minute: Optional[int] = None
    rate_limit_tokens_per_minute: Optional[int] = None
    custom_headers: dict[str, str] = Field(default_factory=dict)
    proxy_url: Optional[str] = None
    verify_ssl: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMRequest(BaseModel):
    """Request to an LLM provider."""

    messages: list[dict[str, str]]
    model_id: str
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop_sequences: Optional[list[str]] = None
    stream: bool = False
    functions: Optional[list[dict[str, Any]]] = None
    function_call: Union[str, dict, None] = None
    user_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMResponse(BaseModel):
    """Response from an LLM provider."""

    content: str
    model_id: str
    provider: str

    # Usage information
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    # Cost information
    input_cost: float = 0.0
    output_cost: float = 0.0
    total_cost: float = 0.0

    # Performance metrics
    response_time_ms: float = 0.0
    queue_time_ms: float = 0.0
    processing_time_ms: float = 0.0

    # Metadata
    finish_reason: Optional[str] = None
    function_call: Optional[dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None

    # Quality metrics
    confidence_score: Optional[float] = None
    safety_score: Optional[float] = None

    metadata: dict[str, Any] = Field(default_factory=dict)


class ProviderHealthStatus(BaseModel):
    """Health status of an LLM provider."""

    provider_name: str
    is_healthy: bool = True
    last_check: datetime = Field(default_factory=datetime.utcnow)
    response_time_ms: float = 0.0
    error_rate: float = 0.0
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset_time: Optional[datetime] = None
    available_models: list[str] = Field(default_factory=list)
    status_message: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMProvider(ABC):
    """
    Abstract base class for all LLM providers.

    Defines the interface that cloud and local providers must implement
    for consistent integration with the routing system.
    """

    def __init__(self, config: ProviderConfig):
        """Initialize the provider with configuration."""
        self.config = config
        self.provider_name = config.provider_name
        self._models: dict[str, ModelInfo] = {}
        self._last_health_check: Optional[datetime] = None
        self._health_status = ProviderHealthStatus(provider_name=self.provider_name)

    @property
    def name(self) -> str:
        """Get the provider name."""
        return self.provider_name

    @property
    def is_healthy(self) -> bool:
        """Check if the provider is healthy."""
        return self._health_status.is_healthy

    @property
    def available_models(self) -> list[ModelInfo]:
        """Get list of available models."""
        return list(self._models.values())

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider and load available models."""
        pass

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response for the given request."""
        pass

    @abstractmethod
    async def generate_stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Generate a streaming response for the given request."""
        pass

    @abstractmethod
    async def get_models(self) -> list[ModelInfo]:
        """Get list of available models from the provider."""
        pass

    @abstractmethod
    async def health_check(self) -> ProviderHealthStatus:
        """Perform a health check on the provider."""
        pass

    async def shutdown(self) -> None:
        """Shutdown the provider and cleanup resources."""
        pass

    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get information about a specific model."""
        return self._models.get(model_id)

    def has_model(self, model_id: str) -> bool:
        """Check if the provider has a specific model."""
        return model_id in self._models

    def calculate_cost(
        self, input_tokens: int, output_tokens: int, model_id: str
    ) -> float:
        """Calculate the cost for a request."""
        model_info = self.get_model_info(model_id)
        if not model_info:
            return 0.0

        input_cost = input_tokens * model_info.input_cost_per_token
        output_cost = output_tokens * model_info.output_cost_per_token
        return input_cost + output_cost

    def get_performance_score(self, model_id: str) -> float:
        """Get performance score for a model (0.0-1.0)."""
        model_info = self.get_model_info(model_id)
        if not model_info:
            return 0.0

        # Combine various factors into a performance score
        base_score = model_info.performance_tier / 5.0  # Normalize to 0-1
        availability_factor = model_info.availability
        health_factor = 1.0 if self.is_healthy else 0.0

        return base_score * availability_factor * health_factor

    def supports_capability(self, model_id: str, capability: ModelCapability) -> bool:
        """Check if a model supports a specific capability."""
        model_info = self.get_model_info(model_id)
        if not model_info:
            return False

        return capability in model_info.capabilities

    def get_privacy_level(self, model_id: str) -> str:
        """Get privacy level for a model."""
        model_info = self.get_model_info(model_id)
        if not model_info:
            return "unknown"

        return model_info.privacy_level

    async def _update_health_status(self) -> None:
        """Update the provider's health status."""
        try:
            start_time = time.time()
            self._health_status = await self.health_check()
            response_time = (time.time() - start_time) * 1000
            self._health_status.response_time_ms = response_time
            self._last_health_check = datetime.utcnow()
        except Exception as e:
            self._health_status.is_healthy = False
            self._health_status.status_message = str(e)
            self._health_status.last_check = datetime.utcnow()

    def _create_response(
        self,
        content: str,
        model_id: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        response_time_ms: float = 0.0,
        **kwargs,
    ) -> LLMResponse:
        """Create a standardized response object."""
        total_tokens = input_tokens + output_tokens

        # Calculate costs
        model_info = self.get_model_info(model_id)
        input_cost = 0.0
        output_cost = 0.0

        if model_info:
            input_cost = input_tokens * model_info.input_cost_per_token
            output_cost = output_tokens * model_info.output_cost_per_token

        return LLMResponse(
            content=content,
            model_id=model_id,
            provider=self.provider_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=input_cost + output_cost,
            response_time_ms=response_time_ms,
            **kwargs,
        )
