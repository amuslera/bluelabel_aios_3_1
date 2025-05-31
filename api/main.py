"""
FastAPI application for AIOSv3 platform.
Provides REST API endpoints for interacting with agents.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

from agents.base.agent import Task
from agents.specialists.cto_agent import CTOAgent
from core.routing.llm_client import llm_factory
from core.routing.router import LLMRouter

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global agents registry
agents_registry = {}
llm_router = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""

    # Startup
    logger.info("Starting AIOSv3 platform...")

    # Initialize LLM router
    global llm_router
    llm_router = LLMRouter()

    # Create CTO Agent
    cto_agent = CTOAgent(llm_router=llm_router)
    agents_registry["cto"] = cto_agent
    await cto_agent.start()

    logger.info("AIOSv3 platform started successfully")

    yield

    # Shutdown
    logger.info("Shutting down AIOSv3 platform...")

    # Stop all agents
    for agent in agents_registry.values():
        await agent.stop()

    logger.info("AIOSv3 platform shut down")


# Create FastAPI app
app = FastAPI(
    title="AIOSv3 - AI Agent Platform",
    description="Modular AI Agent Platform for collaborative software development",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API
class TaskRequest(BaseModel):
    """Request model for creating tasks."""

    type: str
    description: str
    parameters: dict[str, Any] = {}
    priority: int = 5
    complexity: int = 5
    requires_privacy: bool = False


class TaskResponse(BaseModel):
    """Response model for task results."""

    task_id: str
    agent_id: str
    status: str
    result: dict[str, Any] | None = None
    error: str | None = None
    execution_time: float
    model_used: str
    cost_estimate: float


class AgentStatus(BaseModel):
    """Model for agent status information."""

    id: str
    name: str
    is_active: bool
    capabilities: list[str]
    tasks_completed: int


class ChatMessage(BaseModel):
    """Model for chat messages with the CTO."""

    message: str
    context: dict[str, Any] = {}


class ChatResponse(BaseModel):
    """Response model for chat interactions."""

    response: str
    agent_id: str
    suggestions: list[str] = []
    follow_up_actions: list[str] = []


# Dependency to get agents
def get_agent(agent_id: str):
    """Get an agent by ID."""
    if agent_id not in agents_registry:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return agents_registry[agent_id]


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to AIOSv3 - AI Agent Platform",
        "version": "0.1.0",
        "agents": list(agents_registry.keys()),
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agents_active": len([a for a in agents_registry.values() if a.is_active]),
        "total_agents": len(agents_registry),
    }


@app.get("/agents", response_model=list[AgentStatus])
async def list_agents():
    """List all available agents."""
    return [
        AgentStatus(
            id=agent_id,
            name=agent.name,
            is_active=agent.is_active,
            capabilities=agent.capabilities,
            tasks_completed=len(agent.task_history),
        )
        for agent_id, agent in agents_registry.items()
    ]


@app.get("/agents/{agent_id}", response_model=AgentStatus)
async def get_agent_status(agent_id: str):
    """Get status of a specific agent."""
    agent = get_agent(agent_id)
    return AgentStatus(
        id=agent_id,
        name=agent.name,
        is_active=agent.is_active,
        capabilities=agent.capabilities,
        tasks_completed=len(agent.task_history),
    )


@app.post("/agents/{agent_id}/tasks", response_model=TaskResponse)
async def create_task(agent_id: str, task_request: TaskRequest):
    """Create and execute a task for an agent."""
    agent = get_agent(agent_id)

    # Create task
    task = Task(
        type=task_request.type,
        description=task_request.description,
        parameters=task_request.parameters,
        priority=task_request.priority,
        complexity=task_request.complexity,
        requires_privacy=task_request.requires_privacy,
    )

    # Execute task
    result = await agent.execute_task(task)

    return TaskResponse(
        task_id=result.task_id,
        agent_id=result.agent_id,
        status=result.status,
        result=result.result,
        error=result.error,
        execution_time=result.execution_time,
        model_used=result.model_used,
        cost_estimate=result.cost_estimate,
    )


@app.get("/agents/{agent_id}/tasks")
async def get_agent_tasks(agent_id: str, limit: int = 10):
    """Get recent tasks for an agent."""
    agent = get_agent(agent_id)

    recent_tasks = agent.task_history[-limit:] if agent.task_history else []

    return [
        {
            "task_id": task.task_id,
            "status": task.status,
            "execution_time": task.execution_time,
            "model_used": task.model_used,
            "cost_estimate": task.cost_estimate,
            "created_at": task.created_at,
        }
        for task in recent_tasks
    ]


@app.post("/cto/chat", response_model=ChatResponse)
async def chat_with_cto(message: ChatMessage):
    """Chat interface with the CTO Agent."""

    cto_agent = get_agent("cto")

    # Create a communication task
    task = Task(
        type="ceo_communication",
        description=f"CEO message: {message.message}",
        parameters={
            "type": "chat",
            "content": message.message,
            "context": message.context,
        },
        priority=8,  # High priority for CEO communications
        complexity=6,
    )

    # Execute the task
    result = await cto_agent.execute_task(task)

    if result.status == "error":
        raise HTTPException(status_code=500, detail=result.error)

    # Extract response components
    response_data = result.result or {}

    return ChatResponse(
        response=response_data.get("response", "Task completed successfully"),
        agent_id="cto",
        suggestions=response_data.get("suggestions", []),
        follow_up_actions=response_data.get("follow_up_actions", []),
    )


@app.post("/cto/project-plan")
async def create_project_plan(project_request: dict[str, Any]):
    """Request CTO to create a project plan."""

    cto_agent = get_agent("cto")

    task = Task(
        type="project_planning",
        description="Create comprehensive project plan",
        parameters={
            "requirements": project_request.get("requirements", ""),
            "timeline": project_request.get("timeline", ""),
            "constraints": project_request.get("constraints", {}),
        },
        priority=9,
        complexity=8,
    )

    result = await cto_agent.execute_task(task)

    if result.status == "error":
        raise HTTPException(status_code=500, detail=result.error)

    return {
        "task_id": result.task_id,
        "project_plan": result.result,
        "cost_estimate": result.cost_estimate,
    }


@app.post("/cto/architecture")
async def design_architecture(architecture_request: dict[str, Any]):
    """Request CTO to design system architecture."""

    cto_agent = get_agent("cto")

    task = Task(
        type="architecture_design",
        description="Design system architecture",
        parameters=architecture_request,
        priority=9,
        complexity=8,
    )

    result = await cto_agent.execute_task(task)

    if result.status == "error":
        raise HTTPException(status_code=500, detail=result.error)

    return {
        "task_id": result.task_id,
        "architecture": result.result,
        "cost_estimate": result.cost_estimate,
    }


@app.get("/routing/status")
async def get_routing_status():
    """Get LLM routing status and cost tracking."""
    if llm_router:
        return {
            "models_available": len(llm_router.models),
            "cost_summary": llm_router.get_cost_summary(),
            "routing_active": True,
        }
    else:
        return {"routing_active": False}


@app.post("/routing/test")
async def test_llm_connections():
    """Test connections to all configured LLM providers."""

    test_results = {}

    # Test Anthropic
    try:
        anthropic_available = await llm_factory.test_connection("anthropic")
        test_results["anthropic"] = {
            "available": anthropic_available,
            "error": None if anthropic_available else "Connection failed",
        }
    except Exception as e:
        test_results["anthropic"] = {"available": False, "error": str(e)}

    # Test OpenAI
    try:
        openai_available = await llm_factory.test_connection("openai")
        test_results["openai"] = {
            "available": openai_available,
            "error": None if openai_available else "Connection failed",
        }
    except Exception as e:
        test_results["openai"] = {"available": False, "error": str(e)}

    # Test Ollama (if configured)
    try:
        ollama_available = await llm_factory.test_connection("ollama")
        test_results["ollama"] = {
            "available": ollama_available,
            "error": None if ollama_available else "Ollama not running",
        }
    except Exception as e:
        test_results["ollama"] = {"available": False, "error": str(e)}

    return test_results


if __name__ == "__main__":
    # Configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    workers = int(os.getenv("API_WORKERS", "1"))
    reload = os.getenv("DEBUG", "true").lower() == "true"

    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        workers=workers if not reload else 1,
        reload=reload,
    )
