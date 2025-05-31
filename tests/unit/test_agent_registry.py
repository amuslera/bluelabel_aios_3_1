"""
Unit tests for the agent registry and discovery system.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from agents.base.types import (
    AgentHealth,
    AgentMetadata,
    AgentState,
    AgentStats,
    AgentType,
    RegistrationRequest,
    TaskType,
)
from agents.base.exceptions import AgentRegistrationError, DependencyError
from core.orchestration.registry import AgentRegistry
from core.orchestration.discovery import AgentDiscovery


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    redis_mock = AsyncMock()
    redis_mock.ping = AsyncMock()
    redis_mock.hset = AsyncMock()
    redis_mock.hgetall = AsyncMock()
    redis_mock.exists = AsyncMock()
    redis_mock.expire = AsyncMock()
    redis_mock.delete = AsyncMock()
    redis_mock.sadd = AsyncMock()
    redis_mock.srem = AsyncMock()
    redis_mock.smembers = AsyncMock()
    redis_mock.keys = AsyncMock()
    redis_mock.close = AsyncMock()
    return redis_mock


@pytest.fixture
def agent_metadata():
    """Create test agent metadata."""
    return AgentMetadata(
        id="test-agent-123",
        type=AgentType.BACKEND_DEV,
        name="Test Backend Agent",
        description="A test backend development agent",
        capabilities=[],
    )


@pytest.fixture
def registration_request(agent_metadata):
    """Create test registration request."""
    return RegistrationRequest(
        metadata=agent_metadata,
        initial_state=AgentState.IDLE,
        endpoint="http://localhost:8000",
        config={"max_tasks": 3},
    )


@pytest.fixture
def agent_health():
    """Create test agent health."""
    return AgentHealth(
        agent_id="test-agent-123",
        state=AgentState.IDLE,
        last_heartbeat=datetime.utcnow(),
        is_healthy=True,
        health_score=0.95,
    )


@pytest.fixture
def agent_stats():
    """Create test agent statistics."""
    return AgentStats(
        agent_id="test-agent-123",
        tasks_completed=10,
        tasks_failed=1,
        success_rate=0.91,
        last_active=datetime.utcnow(),
    )


class TestAgentRegistry:
    """Test cases for AgentRegistry class."""

    @pytest.mark.asyncio
    async def test_registry_initialization(self, mock_redis):
        """Test registry initialization."""
        with patch('redis.asyncio.from_url', return_value=mock_redis):
            registry = AgentRegistry()
            await registry.initialize()
            
            assert registry.is_running
            mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_registry_initialization_failure(self):
        """Test registry initialization failure."""
        with patch('redis.asyncio.from_url', side_effect=Exception("Connection failed")):
            registry = AgentRegistry()
            
            with pytest.raises(DependencyError):
                await registry.initialize()

    @pytest.mark.asyncio
    async def test_agent_registration_success(self, mock_redis, registration_request):
        """Test successful agent registration."""
        mock_redis.hgetall.return_value = {}  # Agent doesn't exist
        
        with patch('redis.asyncio.from_url', return_value=mock_redis):
            registry = AgentRegistry()
            await registry.initialize()
            
            response = await registry.register_agent(registration_request)
            
            assert response.success
            assert response.agent_id == "test-agent-123"
            assert "backend_developer" in response.assigned_queues
            assert "agent.broadcast" in response.assigned_queues
            
            # Verify Redis calls
            assert mock_redis.hset.call_count >= 3  # metadata, health, stats
            mock_redis.sadd.assert_called()  # Adding to indices

    @pytest.mark.asyncio
    async def test_agent_registration_duplicate(self, mock_redis, registration_request, agent_metadata):
        """Test registration of duplicate agent."""
        # Mock existing agent
        mock_redis.hgetall.return_value = {
            "id": "test-agent-123",
            "type": "backend_developer",
            "name": "Test Backend Agent",
            "description": "A test backend development agent",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "tags": "[]",
        }
        
        with patch('redis.asyncio.from_url', return_value=mock_redis):
            registry = AgentRegistry()
            await registry.initialize()
            
            with pytest.raises(AgentRegistrationError):
                await registry.register_agent(registration_request)

    @pytest.mark.asyncio
    async def test_agent_deregistration(self, mock_redis, agent_metadata):
        """Test agent deregistration."""
        # Mock existing agent
        mock_redis.hgetall.return_value = {
            "id": "test-agent-123",
            "type": "backend_developer",
            "name": "Test Backend Agent",
            "description": "A test backend development agent",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "tags": "[]",
        }
        
        with patch('redis.asyncio.from_url', return_value=mock_redis):
            registry = AgentRegistry()
            await registry.initialize()
            
            success = await registry.deregister_agent("test-agent-123")
            
            assert success
            mock_redis.delete.assert_called()
            mock_redis.srem.assert_called()

    @pytest.mark.asyncio
    async def test_health_update(self, mock_redis, agent_health):
        """Test agent health update."""
        mock_redis.exists.return_value = True
        
        with patch('redis.asyncio.from_url', return_value=mock_redis):
            registry = AgentRegistry()
            await registry.initialize()
            
            success = await registry.update_agent_health("test-agent-123", agent_health)
            
            assert success
            mock_redis.hset.assert_called()
            mock_redis.expire.assert_called()

    @pytest.mark.asyncio
    async def test_get_agent_metadata(self, mock_redis):
        """Test retrieving agent metadata."""
        mock_redis.hgetall.return_value = {
            "id": "test-agent-123",
            "type": "backend_developer",
            "name": "Test Backend Agent",
            "description": "A test backend development agent",
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "owner": "system",
            "tags": "[]",
        }
        
        with patch('redis.asyncio.from_url', return_value=mock_redis):
            registry = AgentRegistry()
            await registry.initialize()
            
            metadata = await registry.get_agent_metadata("test-agent-123")
            
            assert metadata is not None
            assert metadata.id == "test-agent-123"
            assert metadata.type == AgentType.BACKEND_DEV
            assert metadata.name == "Test Backend Agent"

    @pytest.mark.asyncio
    async def test_get_agent_health(self, mock_redis):
        """Test retrieving agent health."""
        mock_redis.hgetall.return_value = {
            "agent_id": "test-agent-123",
            "state": "idle",
            "last_heartbeat": datetime.utcnow().isoformat(),
            "error_count": "0",
            "memory_usage_mb": "128.5",
            "cpu_usage_percent": "15.0",
            "response_time_ms": "250.0",
            "uptime_seconds": "3600.0",
            "is_healthy": "true",
            "health_score": "0.95",
        }
        
        with patch('redis.asyncio.from_url', return_value=mock_redis):
            registry = AgentRegistry()
            await registry.initialize()
            
            health = await registry.get_agent_health("test-agent-123")
            
            assert health is not None
            assert health.agent_id == "test-agent-123"
            assert health.state == AgentState.IDLE
            assert health.is_healthy is True
            assert health.health_score == 0.95

    @pytest.mark.asyncio
    async def test_list_agents_by_type(self, mock_redis):
        """Test listing agents by type."""
        mock_redis.smembers.return_value = {"agent-1", "agent-2", "agent-3"}
        
        with patch('redis.asyncio.from_url', return_value=mock_redis):
            registry = AgentRegistry()
            await registry.initialize()
            
            agents = await registry.list_agents(agent_type=AgentType.BACKEND_DEV)
            
            assert len(agents) == 3
            assert "agent-1" in agents
            mock_redis.smembers.assert_called_with("aiosv3:registry:indices:type:backend_developer")

    @pytest.mark.asyncio
    async def test_find_agents_by_capability(self, mock_redis):
        """Test finding agents by capability."""
        mock_redis.smembers.return_value = {"agent-1", "agent-2"}
        
        with patch('redis.asyncio.from_url', return_value=mock_redis):
            registry = AgentRegistry()
            await registry.initialize()
            
            agents = await registry.find_agents_by_capability("backend_development")
            
            assert len(agents) == 2
            mock_redis.smembers.assert_called_with("aiosv3:registry:indices:capability:backend_development")

    @pytest.mark.asyncio
    async def test_registry_stats(self, mock_redis):
        """Test getting registry statistics."""
        # Mock Redis responses for stats
        mock_redis.keys.return_value = [
            "aiosv3:registry:agents:agent-1:metadata",
            "aiosv3:registry:agents:agent-2:metadata",
        ]
        
        # Mock metadata responses
        metadata_responses = [
            {
                "id": "agent-1",
                "type": "backend_developer",
                "name": "Agent 1",
                "description": "Test agent 1",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "tags": "[]",
            },
            {
                "id": "agent-2",
                "type": "frontend_developer", 
                "name": "Agent 2",
                "description": "Test agent 2",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "tags": "[]",
            },
        ]
        
        # Mock health responses
        health_responses = [
            {
                "agent_id": "agent-1",
                "state": "idle",
                "last_heartbeat": datetime.utcnow().isoformat(),
                "is_healthy": "true",
                "health_score": "0.9",
            },
            {
                "agent_id": "agent-2", 
                "state": "busy",
                "last_heartbeat": datetime.utcnow().isoformat(),
                "is_healthy": "true",
                "health_score": "0.8",
            },
        ]
        
        mock_redis.hgetall.side_effect = metadata_responses + health_responses
        
        with patch('redis.asyncio.from_url', return_value=mock_redis):
            registry = AgentRegistry()
            await registry.initialize()
            
            stats = await registry.get_registry_stats()
            
            assert stats["total_agents"] == 2
            assert stats["healthy_agents"] == 2
            assert stats["unhealthy_agents"] == 0
            assert "backend_developer" in stats["agents_by_type"]
            assert "frontend_developer" in stats["agents_by_type"]
            assert stats["average_health_score"] == 0.85

    @pytest.mark.asyncio
    async def test_stale_agent_cleanup(self, mock_redis):
        """Test cleanup of stale agents."""
        # Mock stale agent
        stale_time = datetime.utcnow() - timedelta(minutes=10)
        mock_redis.keys.return_value = ["aiosv3:registry:agents:stale-agent:health"]
        mock_redis.hgetall.side_effect = [
            # Health data for stale agent
            {
                "agent_id": "stale-agent",
                "state": "idle",
                "last_heartbeat": stale_time.isoformat(),
                "is_healthy": "true",
                "health_score": "0.9",
            },
            # Metadata for stale agent (for removal)
            {
                "id": "stale-agent",
                "type": "backend_developer",
                "name": "Stale Agent",
                "description": "An agent that went stale",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "tags": "[]",
            },
        ]
        
        with patch('redis.asyncio.from_url', return_value=mock_redis):
            registry = AgentRegistry(stale_agent_timeout=300.0)  # 5 minutes
            await registry.initialize()
            
            await registry._cleanup_stale_agents()
            
            # Verify deletion was called
            mock_redis.delete.assert_called()


class TestAgentDiscovery:
    """Test cases for AgentDiscovery class."""

    @pytest.fixture
    def mock_registry(self):
        """Create a mock registry for discovery tests."""
        registry = AsyncMock()
        return registry

    @pytest.mark.asyncio
    async def test_discovery_initialization(self, mock_registry):
        """Test discovery service initialization."""
        discovery = AgentDiscovery(registry=mock_registry)
        await discovery.initialize()
        
        assert discovery.registry == mock_registry

    @pytest.mark.asyncio
    async def test_find_agent_for_task(self, mock_registry):
        """Test finding agent for a specific task."""
        # Mock registry responses
        mock_registry.list_agents.return_value = ["agent-1", "agent-2"]
        mock_registry.find_agents_by_capability.return_value = ["agent-1", "agent-3"]
        
        # Mock health responses
        health_responses = {
            "agent-1": AgentHealth(
                agent_id="agent-1",
                state=AgentState.IDLE,
                is_healthy=True,
                health_score=0.9,
                response_time_ms=200,
            ),
            "agent-2": AgentHealth(
                agent_id="agent-2", 
                state=AgentState.BUSY,
                is_healthy=True,
                health_score=0.8,
                response_time_ms=300,
            ),
            "agent-3": AgentHealth(
                agent_id="agent-3",
                state=AgentState.IDLE,
                is_healthy=True,
                health_score=0.95,
                response_time_ms=150,
            ),
        }
        
        # Mock metadata responses
        metadata_responses = {
            "agent-1": AgentMetadata(
                id="agent-1",
                type=AgentType.BACKEND_DEV,
                name="Backend Agent 1",
                description="Backend development agent",
            ),
            "agent-2": AgentMetadata(
                id="agent-2",
                type=AgentType.BACKEND_DEV,
                name="Backend Agent 2", 
                description="Backend development agent",
            ),
            "agent-3": AgentMetadata(
                id="agent-3",
                type=AgentType.BACKEND_DEV,
                name="Backend Agent 3",
                description="Backend development agent",
            ),
        }
        
        # Mock stats responses
        stats_responses = {
            "agent-1": AgentStats(agent_id="agent-1", success_rate=0.9),
            "agent-2": AgentStats(agent_id="agent-2", success_rate=0.85),
            "agent-3": AgentStats(agent_id="agent-3", success_rate=0.95),
        }
        
        mock_registry.get_agent_health.side_effect = lambda aid: health_responses.get(aid)
        mock_registry.get_agent_metadata.side_effect = lambda aid: metadata_responses.get(aid)
        mock_registry.get_agent_stats.side_effect = lambda aid: stats_responses.get(aid)
        
        discovery = AgentDiscovery(registry=mock_registry)
        await discovery.initialize()
        
        # Find agent for code generation task
        agent_id = await discovery.find_agent_for_task(
            task_type=TaskType.CODE_GENERATION,
            complexity=5,
            preferred_agent_type=AgentType.BACKEND_DEV,
        )
        
        assert agent_id is not None
        assert agent_id in ["agent-1", "agent-2", "agent-3"]

    @pytest.mark.asyncio
    async def test_find_agents_by_type(self, mock_registry):
        """Test finding agents by type."""
        mock_registry.list_agents.return_value = ["agent-1", "agent-2"]
        
        # Mock health for filtering
        mock_registry.get_agent_health.return_value = AgentHealth(
            agent_id="test",
            state=AgentState.IDLE,
            is_healthy=True,
        )
        
        discovery = AgentDiscovery(registry=mock_registry)
        await discovery.initialize()
        
        agents = await discovery.find_agents_by_type(
            agent_type=AgentType.BACKEND_DEV,
            healthy_only=True,
        )
        
        assert len(agents) == 2
        mock_registry.list_agents.assert_called_with(
            agent_type=AgentType.BACKEND_DEV,
            healthy_only=True,
        )

    @pytest.mark.asyncio
    async def test_load_balancing_strategies(self, mock_registry):
        """Test different load balancing strategies."""
        agent_ids = ["agent-1", "agent-2", "agent-3"]
        
        # Mock load balancing info
        load_info = {
            "agent-1": {
                "health_score": 0.9,
                "response_time_ms": 200,
                "cpu_usage_percent": 30,
                "memory_usage_mb": 400,
            },
            "agent-2": {
                "health_score": 0.8,
                "response_time_ms": 150,
                "cpu_usage_percent": 50,
                "memory_usage_mb": 600,
            },
            "agent-3": {
                "health_score": 0.95,
                "response_time_ms": 300,
                "cpu_usage_percent": 20,
                "memory_usage_mb": 300,
            },
        }
        
        # Mock registry responses for load info
        def mock_health_response(agent_id):
            info = load_info[agent_id]
            return AgentHealth(
                agent_id=agent_id,
                state=AgentState.IDLE,
                health_score=info["health_score"],
                response_time_ms=info["response_time_ms"],
                cpu_usage_percent=info["cpu_usage_percent"],
                memory_usage_mb=info["memory_usage_mb"],
            )
        
        def mock_stats_response(agent_id):
            return AgentStats(
                agent_id=agent_id,
                success_rate=0.9,
                average_execution_time=100,
                tasks_completed=10,
                last_active=datetime.utcnow(),
            )
        
        mock_registry.get_agent_health.side_effect = mock_health_response
        mock_registry.get_agent_stats.side_effect = mock_stats_response
        
        discovery = AgentDiscovery(registry=mock_registry)
        await discovery.initialize()
        
        # Test different strategies
        strategies = ["least_loaded", "fastest", "best_health", "random"]
        
        for strategy in strategies:
            selected = await discovery.select_agent_with_load_balancing(
                agent_ids, strategy=strategy
            )
            assert selected in agent_ids
        
        # Test specific expected results
        fastest = await discovery.select_agent_with_load_balancing(
            agent_ids, strategy="fastest"
        )
        assert fastest == "agent-2"  # Lowest response time
        
        best_health = await discovery.select_agent_with_load_balancing(
            agent_ids, strategy="best_health"
        )
        assert best_health == "agent-3"  # Highest health score

    @pytest.mark.asyncio
    async def test_discovery_stats(self, mock_registry):
        """Test getting discovery statistics."""
        mock_registry.get_registry_stats.return_value = {
            "total_agents": 5,
            "healthy_agents": 4,
            "agents_by_type": {"backend_developer": 2, "frontend_developer": 3},
            "average_health_score": 0.85,
        }
        
        discovery = AgentDiscovery(registry=mock_registry)
        await discovery.initialize()
        
        stats = await discovery.get_discovery_stats()
        
        assert stats["total_agents"] == 5
        assert stats["healthy_agents"] == 4
        assert "discovery_timestamp" in stats
        assert "agents_by_type" in stats

    @pytest.mark.asyncio
    async def test_type_compatibility_scoring(self):
        """Test agent type and task type compatibility scoring."""
        discovery = AgentDiscovery()
        
        # Test high compatibility
        cto_design_score = discovery._get_type_compatibility(
            AgentType.CTO, TaskType.SYSTEM_DESIGN
        )
        assert cto_design_score == 1.0
        
        backend_code_score = discovery._get_type_compatibility(
            AgentType.BACKEND_DEV, TaskType.CODE_GENERATION
        )
        assert backend_code_score == 1.0
        
        # Test lower compatibility
        backend_design_score = discovery._get_type_compatibility(
            AgentType.BACKEND_DEV, TaskType.SYSTEM_DESIGN
        )
        assert backend_design_score < 1.0
        
        # Test default compatibility
        generalist_score = discovery._get_type_compatibility(
            AgentType.GENERALIST, TaskType.CODE_REVIEW
        )
        assert generalist_score == 0.3  # Default

    @pytest.mark.asyncio
    async def test_complexity_scoring(self):
        """Test complexity scoring for different agent types."""
        discovery = AgentDiscovery()
        
        # Test CTO with high complexity (good fit)
        cto_high_score = discovery._get_complexity_score(AgentType.CTO, 9)
        assert cto_high_score > 0.8
        
        # Test generalist with high complexity (poor fit)
        generalist_high_score = discovery._get_complexity_score(AgentType.GENERALIST, 9)
        assert generalist_high_score < 0.5
        
        # Test backend with medium complexity (good fit)
        backend_medium_score = discovery._get_complexity_score(AgentType.BACKEND_DEV, 5)
        assert backend_medium_score > 0.8