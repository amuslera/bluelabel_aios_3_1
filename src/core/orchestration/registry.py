"""
Centralized agent registry for AIOSv3 platform.

Provides agent registration, discovery, health monitoring, and lifecycle tracking
for all agents in the system.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any

import redis.asyncio as redis

from src.agents.base.exceptions import AgentRegistrationError, DependencyError
from src.agents.base.types import (
    AgentHealth,
    AgentMetadata,
    AgentState,
    AgentStats,
    AgentType,
    RegistrationRequest,
    RegistrationResponse,
)
from src.core.monitoring.metrics import get_metrics

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Centralized registry for agent management and discovery.

    Features:
    - Agent registration and deregistration
    - Health monitoring and status tracking
    - Agent discovery by type, capability, or status
    - Statistics collection and reporting
    - Automatic cleanup of stale agents
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        registry_prefix: str = "aiosv3:registry",
        health_check_interval: float = 30.0,
        stale_agent_timeout: float = 300.0,  # 5 minutes
    ):
        """Initialize the agent registry."""
        self.redis_url = redis_url
        self.registry_prefix = registry_prefix
        self.health_check_interval = health_check_interval
        self.stale_agent_timeout = stale_agent_timeout
        
        # Redis connection
        self.redis: redis.Redis | None = None
        
        # Background tasks
        self._cleanup_task: asyncio.Task | None = None
        self._shutdown_event = asyncio.Event()
        
        # Metrics
        self.metrics = get_metrics()
        
        # Registry state
        self.is_running = False

    async def initialize(self) -> None:
        """Initialize the registry and start background processes."""
        try:
            logger.info("Initializing agent registry")
            
            # Connect to Redis
            self.redis = redis.from_url(self.redis_url, decode_responses=True)
            await self._test_redis_connection()
            
            # Start background cleanup task
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            self.is_running = True
            logger.info("Agent registry initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent registry: {e}")
            raise DependencyError(f"Registry initialization failed: {e}", dependency_name="redis")

    async def shutdown(self) -> None:
        """Shutdown the registry and cleanup resources."""
        try:
            logger.info("Shutting down agent registry")
            self.is_running = False
            
            # Stop background tasks
            self._shutdown_event.set()
            if self._cleanup_task:
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass
            
            # Close Redis connection
            if self.redis:
                await self.redis.close()
            
            logger.info("Agent registry shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during registry shutdown: {e}")

    async def register_agent(self, request: RegistrationRequest) -> RegistrationResponse:
        """Register a new agent with the registry."""
        try:
            agent_id = request.metadata.id
            logger.info(f"Registering agent {agent_id} (type: {request.metadata.type.value})")
            
            # Validate registration request
            await self._validate_registration(request)
            
            # Create registry entries
            timestamp = datetime.utcnow()
            
            # Store agent metadata
            metadata_key = f"{self.registry_prefix}:agents:{agent_id}:metadata"
            metadata_data = {
                **request.metadata.model_dump(),
                "registered_at": timestamp.isoformat(),
                "endpoint": request.endpoint,
                "config": request.config,
            }
            await self.redis.hset(metadata_key, mapping=metadata_data)
            
            # Initialize health record
            health_key = f"{self.registry_prefix}:agents:{agent_id}:health"
            health_data = AgentHealth(
                agent_id=agent_id,
                state=request.initial_state,
                last_heartbeat=timestamp,
            ).model_dump()
            await self.redis.hset(health_key, mapping=health_data)
            
            # Initialize statistics
            stats_key = f"{self.registry_prefix}:agents:{agent_id}:stats"
            stats_data = AgentStats(agent_id=agent_id, last_active=timestamp).model_dump()
            await self.redis.hset(stats_key, mapping=stats_data)
            
            # Add to type-based indices
            await self._add_to_indices(agent_id, request.metadata)
            
            # Set expiration for health monitoring
            await self.redis.expire(health_key, int(self.stale_agent_timeout))
            
            # Update metrics
            self.metrics.track_agent_operation(
                agent_id=agent_id,
                operation_type="registration",
                status="success"
            )
            
            # Determine assigned queues based on agent type and capabilities
            assigned_queues = self._get_assigned_queues(request.metadata)
            
            response = RegistrationResponse(
                success=True,
                agent_id=agent_id,
                message=f"Agent {agent_id} registered successfully",
                assigned_queues=assigned_queues,
                registry_endpoint=f"registry:{self.registry_prefix}",
            )
            
            logger.info(f"Agent {agent_id} registered successfully with queues: {assigned_queues}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to register agent {request.metadata.id}: {e}")
            self.metrics.track_agent_operation(
                agent_id=request.metadata.id,
                operation_type="registration",
                status="error"
            )
            raise AgentRegistrationError(
                f"Registration failed: {e}",
                agent_id=request.metadata.id
            )

    async def deregister_agent(self, agent_id: str) -> bool:
        """Deregister an agent from the registry."""
        try:
            logger.info(f"Deregistering agent {agent_id}")
            
            # Get agent metadata before removal
            metadata = await self.get_agent_metadata(agent_id)
            if not metadata:
                logger.warning(f"Attempted to deregister non-existent agent {agent_id}")
                return False
            
            # Remove from all registry keys
            keys_to_delete = [
                f"{self.registry_prefix}:agents:{agent_id}:metadata",
                f"{self.registry_prefix}:agents:{agent_id}:health", 
                f"{self.registry_prefix}:agents:{agent_id}:stats",
            ]
            
            await self.redis.delete(*keys_to_delete)
            
            # Remove from indices
            await self._remove_from_indices(agent_id, metadata)
            
            # Update metrics
            self.metrics.track_agent_operation(
                agent_id=agent_id,
                operation_type="deregistration", 
                status="success"
            )
            
            logger.info(f"Agent {agent_id} deregistered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deregister agent {agent_id}: {e}")
            self.metrics.track_agent_operation(
                agent_id=agent_id,
                operation_type="deregistration",
                status="error"
            )
            return False

    async def update_agent_health(self, agent_id: str, health: AgentHealth) -> bool:
        """Update an agent's health status."""
        try:
            health_key = f"{self.registry_prefix}:agents:{agent_id}:health"
            
            # Check if agent exists
            if not await self.redis.exists(health_key):
                logger.warning(f"Attempted to update health for non-existent agent {agent_id}")
                return False
            
            # Update health data
            health_data = health.model_dump()
            await self.redis.hset(health_key, mapping=health_data)
            
            # Refresh expiration
            await self.redis.expire(health_key, int(self.stale_agent_timeout))
            
            # Update metrics
            self.metrics.track_agent_operation(
                agent_id=agent_id,
                operation_type="health_update",
                status="success"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update health for agent {agent_id}: {e}")
            return False

    async def update_agent_stats(self, agent_id: str, stats: AgentStats) -> bool:
        """Update an agent's statistics."""
        try:
            stats_key = f"{self.registry_prefix}:agents:{agent_id}:stats"
            
            # Update statistics
            stats_data = stats.model_dump()
            await self.redis.hset(stats_key, mapping=stats_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update stats for agent {agent_id}: {e}")
            return False

    async def get_agent_metadata(self, agent_id: str) -> AgentMetadata | None:
        """Get metadata for a specific agent."""
        try:
            metadata_key = f"{self.registry_prefix}:agents:{agent_id}:metadata"
            data = await self.redis.hgetall(metadata_key)
            
            if not data:
                return None
            
            # Convert back to AgentMetadata
            return AgentMetadata(
                id=data["id"],
                type=AgentType(data["type"]),
                name=data["name"],
                description=data["description"],
                version=data.get("version", "1.0.0"),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
                owner=data.get("owner", "system"),
                tags=json.loads(data.get("tags", "[]")),
            )
            
        except Exception as e:
            logger.error(f"Failed to get metadata for agent {agent_id}: {e}")
            return None

    async def get_agent_health(self, agent_id: str) -> AgentHealth | None:
        """Get health status for a specific agent."""
        try:
            health_key = f"{self.registry_prefix}:agents:{agent_id}:health"
            data = await self.redis.hgetall(health_key)
            
            if not data:
                return None
            
            return AgentHealth(
                agent_id=data["agent_id"],
                state=AgentState(data["state"]),
                last_heartbeat=datetime.fromisoformat(data["last_heartbeat"]),
                last_task_completed=datetime.fromisoformat(data["last_task_completed"]) if data.get("last_task_completed") else None,
                error_count=int(data.get("error_count", 0)),
                last_error=data.get("last_error"),
                memory_usage_mb=float(data.get("memory_usage_mb", 0)),
                cpu_usage_percent=float(data.get("cpu_usage_percent", 0)),
                response_time_ms=float(data.get("response_time_ms", 0)),
                uptime_seconds=float(data.get("uptime_seconds", 0)),
                is_healthy=data.get("is_healthy", "true").lower() == "true",
                health_score=float(data.get("health_score", 1.0)),
            )
            
        except Exception as e:
            logger.error(f"Failed to get health for agent {agent_id}: {e}")
            return None

    async def get_agent_stats(self, agent_id: str) -> AgentStats | None:
        """Get statistics for a specific agent."""
        try:
            stats_key = f"{self.registry_prefix}:agents:{agent_id}:stats"
            data = await self.redis.hgetall(stats_key)
            
            if not data:
                return None
            
            return AgentStats(
                agent_id=data["agent_id"],
                tasks_completed=int(data.get("tasks_completed", 0)),
                tasks_failed=int(data.get("tasks_failed", 0)),
                average_execution_time=float(data.get("average_execution_time", 0)),
                total_cost=float(data.get("total_cost", 0)),
                models_used=json.loads(data.get("models_used", "{}")),
                success_rate=float(data.get("success_rate", 1.0)),
                last_active=datetime.fromisoformat(data["last_active"]),
            )
            
        except Exception as e:
            logger.error(f"Failed to get stats for agent {agent_id}: {e}")
            return None

    async def list_agents(
        self,
        agent_type: AgentType | None = None,
        state: AgentState | None = None,
        healthy_only: bool = False,
    ) -> list[str]:
        """List all registered agents with optional filtering."""
        try:
            if agent_type:
                # Use type-based index
                type_key = f"{self.registry_prefix}:indices:type:{agent_type.value}"
                agent_ids = await self.redis.smembers(type_key)
            else:
                # Get all agents
                pattern = f"{self.registry_prefix}:agents:*:metadata"
                keys = await self.redis.keys(pattern)
                agent_ids = [key.split(":")[-2] for key in keys]
            
            # Apply additional filters
            if state or healthy_only:
                filtered_ids = []
                for agent_id in agent_ids:
                    health = await self.get_agent_health(agent_id)
                    if not health:
                        continue
                    
                    if state and health.state != state:
                        continue
                    
                    if healthy_only and not health.is_healthy:
                        continue
                    
                    filtered_ids.append(agent_id)
                
                return filtered_ids
            
            return list(agent_ids)
            
        except Exception as e:
            logger.error(f"Failed to list agents: {e}")
            return []

    async def find_agents_by_capability(self, capability: str) -> list[str]:
        """Find agents that have a specific capability."""
        try:
            capability_key = f"{self.registry_prefix}:indices:capability:{capability}"
            agent_ids = await self.redis.smembers(capability_key)
            return list(agent_ids)
            
        except Exception as e:
            logger.error(f"Failed to find agents by capability {capability}: {e}")
            return []

    async def get_registry_stats(self) -> dict[str, Any]:
        """Get overall registry statistics."""
        try:
            stats = {
                "total_agents": 0,
                "agents_by_type": {},
                "agents_by_state": {},
                "healthy_agents": 0,
                "unhealthy_agents": 0,
                "average_health_score": 0.0,
            }
            
            # Get all agent IDs
            pattern = f"{self.registry_prefix}:agents:*:metadata"
            keys = await self.redis.keys(pattern)
            agent_ids = [key.split(":")[-2] for key in keys]
            
            stats["total_agents"] = len(agent_ids)
            
            if not agent_ids:
                return stats
            
            total_health_score = 0.0
            
            for agent_id in agent_ids:
                # Get agent metadata and health
                metadata = await self.get_agent_metadata(agent_id)
                health = await self.get_agent_health(agent_id)
                
                if metadata:
                    # Count by type
                    agent_type = metadata.type.value
                    stats["agents_by_type"][agent_type] = stats["agents_by_type"].get(agent_type, 0) + 1
                
                if health:
                    # Count by state
                    state = health.state.value
                    stats["agents_by_state"][state] = stats["agents_by_state"].get(state, 0) + 1
                    
                    # Count healthy vs unhealthy
                    if health.is_healthy:
                        stats["healthy_agents"] += 1
                    else:
                        stats["unhealthy_agents"] += 1
                    
                    total_health_score += health.health_score
            
            # Calculate average health score
            if agent_ids:
                stats["average_health_score"] = total_health_score / len(agent_ids)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get registry stats: {e}")
            return {"error": str(e)}

    # Private helper methods
    
    async def _test_redis_connection(self) -> None:
        """Test Redis connection."""
        try:
            await self.redis.ping()
            logger.info("Redis connection established")
        except Exception as e:
            raise DependencyError(f"Redis connection failed: {e}", dependency_name="redis")

    async def _validate_registration(self, request: RegistrationRequest) -> None:
        """Validate agent registration request."""
        # Check if agent is already registered
        existing = await self.get_agent_metadata(request.metadata.id)
        if existing:
            raise AgentRegistrationError(
                f"Agent {request.metadata.id} is already registered",
                agent_id=request.metadata.id
            )

    def _get_assigned_queues(self, metadata: AgentMetadata) -> list[str]:
        """Determine which queues an agent should be assigned to."""
        queues = [
            f"agent.{metadata.type.value}",  # Type-specific queue
            "agent.broadcast",  # Broadcast queue for all agents
        ]
        
        # Add capability-based queues
        for capability in metadata.capabilities:
            queues.append(f"capability.{capability.name}")
        
        return queues

    async def _add_to_indices(self, agent_id: str, metadata: AgentMetadata) -> None:
        """Add agent to various indices for quick lookup."""
        # Type-based index
        type_key = f"{self.registry_prefix}:indices:type:{metadata.type.value}"
        await self.redis.sadd(type_key, agent_id)
        
        # Capability-based indices
        for capability in metadata.capabilities:
            capability_key = f"{self.registry_prefix}:indices:capability:{capability.name}"
            await self.redis.sadd(capability_key, agent_id)

    async def _remove_from_indices(self, agent_id: str, metadata: AgentMetadata) -> None:
        """Remove agent from all indices."""
        # Type-based index
        type_key = f"{self.registry_prefix}:indices:type:{metadata.type.value}"
        await self.redis.srem(type_key, agent_id)
        
        # Capability-based indices
        for capability in metadata.capabilities:
            capability_key = f"{self.registry_prefix}:indices:capability:{capability.name}"
            await self.redis.srem(capability_key, agent_id)

    async def _cleanup_loop(self) -> None:
        """Background loop to cleanup stale agents."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._cleanup_stale_agents()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    async def _cleanup_stale_agents(self) -> None:
        """Remove agents that haven't sent heartbeats."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(seconds=self.stale_agent_timeout)
            
            # Get all agent IDs
            pattern = f"{self.registry_prefix}:agents:*:health"
            keys = await self.redis.keys(pattern)
            
            stale_agents = []
            for key in keys:
                agent_id = key.split(":")[-2]
                health = await self.get_agent_health(agent_id)
                
                if health and health.last_heartbeat < cutoff_time:
                    stale_agents.append(agent_id)
            
            # Remove stale agents
            for agent_id in stale_agents:
                logger.warning(f"Removing stale agent {agent_id}")
                await self.deregister_agent(agent_id)
            
            if stale_agents:
                logger.info(f"Cleaned up {len(stale_agents)} stale agents")
                
        except Exception as e:
            logger.error(f"Error cleaning up stale agents: {e}")


# Global registry instance
agent_registry: AgentRegistry | None = None


async def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry instance."""
    global agent_registry
    
    if agent_registry is None:
        agent_registry = AgentRegistry()
        await agent_registry.initialize()
    
    return agent_registry


async def initialize_agent_registry(**kwargs) -> AgentRegistry:
    """Initialize the global agent registry instance."""
    global agent_registry
    
    agent_registry = AgentRegistry(**kwargs)
    await agent_registry.initialize()
    
    return agent_registry