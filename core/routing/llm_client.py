"""
LLM Client for connecting to various model providers.
Supports Anthropic Claude, OpenAI, and local Ollama models.
"""

import logging
import os
from abc import ABC, abstractmethod

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LLMResponse(BaseModel):
    """Response from an LLM."""

    content: str
    model: str
    usage: dict[str, int] = {}
    finish_reason: str = "completed"
    cost_estimate: float = 0.0


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        pass


class AnthropicClient(LLMClient):
    """Client for Anthropic Claude models."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

        self.base_url = "https://api.anthropic.com"
        self.client = httpx.AsyncClient(
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            timeout=60.0,
        )

    async def generate(
        self,
        prompt: str,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> LLMResponse:
        """Generate response using Claude."""

        try:
            # Map old model names to new ones
            model_mapping = {
                "claude-3-opus-20240229": "claude-3-5-sonnet-20241022",
                "claude-3-sonnet-20240229": "claude-3-5-sonnet-20241022",
                "claude-3-opus": "claude-3-5-sonnet-20241022",
                "claude-3-sonnet": "claude-3-5-sonnet-20241022",
            }

            # Use mapping if available, otherwise use provided model
            actual_model = model_mapping.get(model, model)

            payload = {
                "model": actual_model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
            }

            response = await self.client.post(
                f"{self.base_url}/v1/messages", json=payload
            )
            response.raise_for_status()

            data = response.json()

            # Extract content from Claude's response format
            content = ""
            if data.get("content") and len(data["content"]) > 0:
                content = data["content"][0].get("text", "")

            usage = data.get("usage", {})
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)

            # Estimate cost based on model
            cost_estimate = self._calculate_cost(model, input_tokens, output_tokens)

            return LLMResponse(
                content=content,
                model=model,
                usage={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                },
                finish_reason=data.get("stop_reason", "completed"),
                cost_estimate=cost_estimate,
            )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling Claude API: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            raise

    def _calculate_cost(
        self, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Calculate cost for Claude API usage."""

        # Claude pricing (per 1K tokens)
        pricing = {
            "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
            "claude-3-haiku-20240229": {"input": 0.00025, "output": 0.00125},
        }

        model_pricing = pricing.get(model, {"input": 0.003, "output": 0.015})

        input_cost = (input_tokens / 1000) * model_pricing["input"]
        output_cost = (output_tokens / 1000) * model_pricing["output"]

        return input_cost + output_cost


class OpenAIClient(LLMClient):
    """Client for OpenAI models."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.base_url = "https://api.openai.com"
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    async def generate(
        self,
        prompt: str,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> LLMResponse:
        """Generate response using OpenAI."""

        try:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            response = await self.client.post(
                f"{self.base_url}/v1/chat/completions", json=payload
            )
            response.raise_for_status()

            data = response.json()

            # Extract content from OpenAI's response format
            content = ""
            if data.get("choices") and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]

            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

            # Estimate cost
            cost_estimate = self._calculate_cost(model, input_tokens, output_tokens)

            return LLMResponse(
                content=content,
                model=model,
                usage={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": usage.get(
                        "total_tokens", input_tokens + output_tokens
                    ),
                },
                finish_reason=data["choices"][0].get("finish_reason", "completed"),
                cost_estimate=cost_estimate,
            )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling OpenAI API: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            raise

    def _calculate_cost(
        self, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Calculate cost for OpenAI API usage."""

        # OpenAI pricing (per 1K tokens)
        pricing = {
            "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        }

        model_pricing = pricing.get(model, {"input": 0.01, "output": 0.03})

        input_cost = (input_tokens / 1000) * model_pricing["input"]
        output_cost = (output_tokens / 1000) * model_pricing["output"]

        return input_cost + output_cost


class OllamaClient(LLMClient):
    """Client for local Ollama models."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            timeout=120.0
        )  # Longer timeout for local models

    async def generate(
        self,
        prompt: str,
        model: str = "llama3:8b-instruct",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> LLMResponse:
        """Generate response using Ollama."""

        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "options": {"temperature": temperature, "num_predict": max_tokens},
                "stream": False,
            }

            response = await self.client.post(
                f"{self.base_url}/api/generate", json=payload
            )
            response.raise_for_status()

            data = response.json()

            content = data.get("response", "")

            # Ollama doesn't provide detailed token usage, estimate it
            estimated_input_tokens = len(prompt.split()) * 1.3
            estimated_output_tokens = len(content.split()) * 1.3

            return LLMResponse(
                content=content,
                model=model,
                usage={
                    "input_tokens": int(estimated_input_tokens),
                    "output_tokens": int(estimated_output_tokens),
                    "total_tokens": int(
                        estimated_input_tokens + estimated_output_tokens
                    ),
                },
                finish_reason="completed",
                cost_estimate=0.0,  # Local models are free
            )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling Ollama API: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            raise

    async def check_health(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False


class LLMClientFactory:
    """Factory for creating LLM clients."""

    def __init__(self):
        self._clients = {}

    def get_client(self, provider: str, **kwargs) -> LLMClient:
        """Get or create an LLM client for the specified provider."""

        if provider not in self._clients:
            if provider == "anthropic":
                self._clients[provider] = AnthropicClient(**kwargs)
            elif provider == "openai":
                self._clients[provider] = OpenAIClient(**kwargs)
            elif provider == "ollama":
                self._clients[provider] = OllamaClient(**kwargs)
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")

        return self._clients[provider]

    async def test_connection(self, provider: str, **kwargs) -> bool:
        """Test connection to an LLM provider."""
        try:
            client = self.get_client(provider, **kwargs)

            if provider == "ollama":
                return await client.check_health()
            else:
                # Test with a simple prompt
                response = await client.generate(
                    prompt="Hello, can you respond with just 'OK'?", max_tokens=10
                )
                return "OK" in response.content or len(response.content) > 0
        except Exception as e:
            logger.error(f"Connection test failed for {provider}: {e}")
            return False


# Global factory instance
llm_factory = LLMClientFactory()
