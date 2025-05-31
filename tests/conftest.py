"""Pytest configuration and fixtures for AIOSv3."""

import asyncio
import os
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from dotenv import load_dotenv

from agents.specialists.cto_agent import CTOAgent
from core.routing.router import LLMRouter

# Load test environment variables
load_dotenv()


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def llm_router() -> LLMRouter:
    """Create an LLM router for testing."""
    return LLMRouter()


@pytest.fixture
def cto_agent(llm_router: LLMRouter) -> CTOAgent:
    """Create a CTO agent for testing."""
    return CTOAgent(llm_router=llm_router)


@pytest.fixture
def skip_if_no_api_key() -> None:
    """Skip test if API keys are not available."""
    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        pytest.skip("No API keys available for testing")


@pytest.fixture
def mock_task_data() -> dict[str, Any]:
    """Provide mock task data for testing."""
    return {
        "type": "test_task",
        "description": "A test task for unit testing",
        "parameters": {"test": True},
        "priority": 5,
        "complexity": 3,
    }


@pytest.fixture
def mock_agent_config() -> dict[str, Any]:
    """Provide mock agent configuration for testing."""
    return {
        "name": "Test Agent",
        "description": "An agent for testing",
        "role": "tester",
        "capabilities": ["testing", "validation"],
        "model_preferences": {
            "primary": "claude-3-sonnet",
            "fallback": "gpt-4-turbo",
        },
    }
