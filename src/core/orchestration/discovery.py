"""
Agent discovery service for AIOSv3 platform.

Provides intelligent agent discovery, load balancing, and routing
for optimal task assignment and agent collaboration.
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Any

from src.agents.base.types import AgentHealth, AgentMetadata, AgentState, AgentType, TaskType
from src.core.orchestration.registry import AgentRegistry, get_agent_registry

logger = logging.getLogger(__name__)


class AgentDiscovery:
    """
    Intelligent agent discovery and selection service.

    Features:
    - Find agents by type, capability, or availability
    - Load balancing and performance-based selection
    - Health-aware agent filtering
    - Capability matching for tasks
    - Geographic and resource-based routing
    """

    def __init__(self, registry: AgentRegistry | None = None):
        """Initialize the discovery service."""
        self.registry = registry

    async def initialize(self) -> None:
        """Initialize the discovery service."""
        if not self.registry:
            self.registry = await get_agent_registry()
        logger.info("Agent discovery service initialized")

    async def find_agent_for_task(
        self,
        task_type: TaskType,
        complexity: int = 5,
        privacy_required: bool = False,
        preferred_agent_type: AgentType | None = None,
        exclude_agents: list[str] | None = None,
    ) -> str | None:
        """
        Find the best agent to handle a specific task.

        Args:
            task_type: Type of task to be handled
            complexity: Task complexity (1-10)
            privacy_required: Whether task requires privacy/local processing
            preferred_agent_type: Preferred agent type if any
            exclude_agents: List of agent IDs to exclude

        Returns:
            Agent ID of the best match, or None if no suitable agent found
        """
        try:
            logger.debug(f"Finding agent for task type {task_type.value}, complexity {complexity}")

            # Get candidate agents
            candidates = await self._get_candidate_agents(
                task_type=task_type,
                preferred_agent_type=preferred_agent_type,
                exclude_agents=exclude_agents or [],
            )

            if not candidates:
                logger.warning(f"No candidate agents found for task type {task_type.value}")
                return None

            # Filter by availability and health
            available_agents = await self._filter_available_agents(candidates)
            
            if not available_agents:
                logger.warning("No available agents found")
                return None

            # Score and rank agents
            scored_agents = await self._score_agents_for_task(
                available_agents, task_type, complexity, privacy_required
            )

            if not scored_agents:
                logger.warning("No agents passed scoring criteria")
                return None

            # Select best agent (highest score)
            best_agent = max(scored_agents, key=lambda x: x["score"])
            
            logger.info(
                f"Selected agent {best_agent['agent_id']} (score: {best_agent['score']:.2f}) "
                f"for task type {task_type.value}"
            )
            
            return best_agent["agent_id"]

        except Exception as e:
            logger.error(f"Error finding agent for task: {e}")
            return None

    async def find_agents_by_type(
        self,
        agent_type: AgentType,
        healthy_only: bool = True,
        available_only: bool = True,
    ) -> list[str]:
        """Find all agents of a specific type."""
        try:
            agents = await self.registry.list_agents(
                agent_type=agent_type,
                healthy_only=healthy_only,
            )

            if available_only:
                agents = await self._filter_available_agents(agents)

            return agents

        except Exception as e:
            logger.error(f"Error finding agents by type {agent_type.value}: {e}")
            return []

    async def find_agents_by_capability(
        self,
        capability: str,
        healthy_only: bool = True,
        available_only: bool = True,
    ) -> list[str]:
        """Find all agents with a specific capability."""
        try:
            agents = await self.registry.find_agents_by_capability(capability)

            if healthy_only:
                filtered_agents = []
                for agent_id in agents:
                    health = await self.registry.get_agent_health(agent_id)
                    if health and health.is_healthy:
                        filtered_agents.append(agent_id)
                agents = filtered_agents

            if available_only:
                agents = await self._filter_available_agents(agents)

            return agents

        except Exception as e:
            logger.error(f"Error finding agents by capability {capability}: {e}")
            return []

    async def get_agent_load_balancing_info(self, agent_ids: list[str]) -> dict[str, dict[str, Any]]:
        """Get load balancing information for a list of agents."""
        try:
            load_info = {}

            for agent_id in agent_ids:
                health = await self.registry.get_agent_health(agent_id)
                stats = await self.registry.get_agent_stats(agent_id)

                if health and stats:
                    load_info[agent_id] = {
                        "health_score": health.health_score,
                        "response_time_ms": health.response_time_ms,
                        "cpu_usage_percent": health.cpu_usage_percent,
                        "memory_usage_mb": health.memory_usage_mb,
                        "success_rate": stats.success_rate,
                        "average_execution_time": stats.average_execution_time,
                        "tasks_completed": stats.tasks_completed,
                        "last_active": stats.last_active.isoformat(),
                    }

            return load_info

        except Exception as e:
            logger.error(f"Error getting load balancing info: {e}")
            return {}

    async def select_agent_with_load_balancing(
        self,
        agent_ids: list[str],
        strategy: str = "least_loaded",
    ) -> str | None:
        """
        Select an agent using load balancing strategy.

        Strategies:
        - least_loaded: Select agent with lowest CPU/memory usage
        - fastest: Select agent with best response time
        - round_robin: Simple round-robin selection
        - random: Random selection
        - best_health: Select agent with highest health score
        """
        try:
            if not agent_ids:
                return None

            if strategy == "random":
                return random.choice(agent_ids)

            if strategy == "round_robin":
                # Simple round-robin (would need persistent state for true round-robin)
                return agent_ids[0]

            # For other strategies, we need load balancing info
            load_info = await self.get_agent_load_balancing_info(agent_ids)
            
            if not load_info:
                # Fallback to random if no load info available
                return random.choice(agent_ids)

            if strategy == "least_loaded":
                # Select agent with lowest resource usage
                def load_score(agent_id: str) -> float:
                    info = load_info[agent_id]
                    cpu_score = 1.0 - (info["cpu_usage_percent"] / 100.0)
                    memory_score = 1.0 - min(info["memory_usage_mb"] / 1000.0, 1.0)  # Normalize to 1GB
                    return (cpu_score + memory_score) / 2

                return max(load_info.keys(), key=load_score)

            elif strategy == "fastest":
                # Select agent with best response time
                return min(load_info.keys(), key=lambda aid: load_info[aid]["response_time_ms"])

            elif strategy == "best_health":
                # Select agent with highest health score
                return max(load_info.keys(), key=lambda aid: load_info[aid]["health_score"])

            else:
                logger.warning(f"Unknown load balancing strategy: {strategy}, using random")
                return random.choice(agent_ids)

        except Exception as e:
            logger.error(f"Error in load balancing selection: {e}")
            return random.choice(agent_ids) if agent_ids else None

    async def get_discovery_stats(self) -> dict[str, Any]:
        """Get discovery service statistics."""
        try:
            registry_stats = await self.registry.get_registry_stats()
            
            # Add discovery-specific stats
            discovery_stats = {
                "registry_stats": registry_stats,
                "discovery_timestamp": datetime.utcnow().isoformat(),
                "total_agents": registry_stats.get("total_agents", 0),
                "healthy_agents": registry_stats.get("healthy_agents", 0),
                "agents_by_type": registry_stats.get("agents_by_type", {}),
                "agents_by_state": registry_stats.get("agents_by_state", {}),
                "average_health_score": registry_stats.get("average_health_score", 0.0),
            }

            return discovery_stats

        except Exception as e:
            logger.error(f"Error getting discovery stats: {e}")
            return {"error": str(e)}

    # Private helper methods

    async def _get_candidate_agents(
        self,
        task_type: TaskType,
        preferred_agent_type: AgentType | None = None,
        exclude_agents: list[str] | None = None,
    ) -> list[str]:
        """Get candidate agents that can potentially handle the task."""
        candidates = []
        exclude_agents = exclude_agents or []

        if preferred_agent_type:
            # Look for preferred agent type first
            type_agents = await self.registry.list_agents(agent_type=preferred_agent_type)
            candidates.extend([aid for aid in type_agents if aid not in exclude_agents])

        # Find agents by capability mapping
        capability_agents = []
        
        # Map task types to capabilities (simplified mapping)
        task_capability_map = {
            TaskType.CODE_REVIEW: ["code_review", "backend_development", "frontend_development"],
            TaskType.CODE_GENERATION: ["code_generation", "backend_development", "frontend_development"],
            TaskType.SYSTEM_DESIGN: ["system_design", "architecture"],
            TaskType.TESTING: ["testing", "qa"],
            TaskType.DEPLOYMENT: ["deployment", "devops"],
            TaskType.GENERAL: ["general"],
        }

        capabilities = task_capability_map.get(task_type, ["general"])
        
        for capability in capabilities:
            cap_agents = await self.registry.find_agents_by_capability(capability)
            capability_agents.extend([aid for aid in cap_agents if aid not in exclude_agents])

        # Combine and deduplicate
        all_candidates = list(set(candidates + capability_agents))
        
        return all_candidates

    async def _filter_available_agents(self, agent_ids: list[str]) -> list[str]:
        """Filter agents by availability (can accept new tasks)."""
        available_agents = []

        for agent_id in agent_ids:
            health = await self.registry.get_agent_health(agent_id)
            
            if not health:
                continue

            # Check if agent is in a state that can accept tasks
            accepting_states = [AgentState.IDLE, AgentState.BUSY]
            if health.state in accepting_states and health.is_healthy:
                available_agents.append(agent_id)

        return available_agents

    async def _score_agents_for_task(
        self,
        agent_ids: list[str],
        task_type: TaskType,
        complexity: int,
        privacy_required: bool,
    ) -> list[dict[str, Any]]:
        """Score agents based on their suitability for the task."""
        scored_agents = []

        for agent_id in agent_ids:
            try:
                score = await self._calculate_agent_task_score(
                    agent_id, task_type, complexity, privacy_required
                )
                
                if score > 0:  # Only include agents with positive scores
                    scored_agents.append({
                        "agent_id": agent_id,
                        "score": score,
                    })

            except Exception as e:
                logger.warning(f"Error scoring agent {agent_id}: {e}")

        return scored_agents

    async def _calculate_agent_task_score(
        self,
        agent_id: str,
        task_type: TaskType,
        complexity: int,
        privacy_required: bool,
    ) -> float:
        """Calculate a score for how well an agent matches a task."""
        metadata = await self.registry.get_agent_metadata(agent_id)
        health = await self.registry.get_agent_health(agent_id)
        stats = await self.registry.get_agent_stats(agent_id)

        if not metadata or not health or not stats:
            return 0.0

        score = 0.0

        # Base score from health
        score += health.health_score * 40  # 40% weight

        # Success rate score
        score += stats.success_rate * 20  # 20% weight

        # Response time score (inverse - lower is better)
        response_score = max(0, 1.0 - (health.response_time_ms / 5000.0))  # Normalize to 5s
        score += response_score * 15  # 15% weight

        # Agent type compatibility
        type_compatibility = self._get_type_compatibility(metadata.type, task_type)
        score += type_compatibility * 15  # 15% weight

        # Complexity handling capability
        complexity_score = self._get_complexity_score(metadata.type, complexity)
        score += complexity_score * 10  # 10% weight

        # Penalize for high resource usage
        resource_penalty = (health.cpu_usage_percent / 100.0 + 
                          min(health.memory_usage_mb / 1000.0, 1.0)) / 2
        score *= (1.0 - resource_penalty * 0.2)  # Up to 20% penalty

        return max(0.0, score)

    def _get_type_compatibility(self, agent_type: AgentType, task_type: TaskType) -> float:
        """Get compatibility score between agent type and task type."""
        # Compatibility matrix (0.0 to 1.0)
        compatibility_matrix = {
            AgentType.CTO: {
                TaskType.SYSTEM_DESIGN: 1.0,
                TaskType.ARCHITECTURE_REVIEW: 1.0,
                TaskType.TECH_DECISION: 1.0,
                TaskType.CODE_REVIEW: 0.8,
                TaskType.PLANNING: 0.9,
                TaskType.GENERAL: 0.6,
            },
            AgentType.BACKEND_DEV: {
                TaskType.CODE_GENERATION: 1.0,
                TaskType.CODE_REVIEW: 0.9,
                TaskType.BUG_FIX: 1.0,
                TaskType.REFACTORING: 0.9,
                TaskType.SYSTEM_DESIGN: 0.7,
                TaskType.GENERAL: 0.5,
            },
            AgentType.FRONTEND_DEV: {
                TaskType.CODE_GENERATION: 1.0,
                TaskType.CODE_REVIEW: 0.9,
                TaskType.BUG_FIX: 1.0,
                TaskType.REFACTORING: 0.9,
                TaskType.GENERAL: 0.5,
            },
            AgentType.QA_ENGINEER: {
                TaskType.TESTING: 1.0,
                TaskType.CODE_REVIEW: 0.8,
                TaskType.BUG_FIX: 0.7,
                TaskType.GENERAL: 0.4,
            },
            AgentType.DEVOPS: {
                TaskType.DEPLOYMENT: 1.0,
                TaskType.INFRASTRUCTURE: 1.0,
                TaskType.MONITORING_SETUP: 1.0,
                TaskType.CI_CD: 1.0,
                TaskType.GENERAL: 0.4,
            },
            AgentType.GENERALIST: {
                TaskType.GENERAL: 1.0,
                TaskType.RESEARCH: 0.8,
                TaskType.DOCUMENTATION: 0.8,
            },
        }

        agent_compatibility = compatibility_matrix.get(agent_type, {})
        return agent_compatibility.get(task_type, 0.3)  # Default 30% compatibility

    def _get_complexity_score(self, agent_type: AgentType, complexity: int) -> float:
        """Get score based on agent's ability to handle task complexity."""
        # Define complexity ranges for different agent types
        complexity_ranges = {
            AgentType.CTO: (5, 10),  # Can handle high complexity
            AgentType.BACKEND_DEV: (2, 9),
            AgentType.FRONTEND_DEV: (2, 8),
            AgentType.QA_ENGINEER: (2, 8),
            AgentType.DEVOPS: (4, 10),
            AgentType.GENERALIST: (1, 6),  # Limited to lower complexity
        }

        min_complexity, max_complexity = complexity_ranges.get(agent_type, (1, 10))
        
        if complexity < min_complexity:
            # Over-qualified
            return 0.7
        elif complexity > max_complexity:
            # Under-qualified
            return 0.2
        else:
            # Good fit - score based on how well it fits the range
            range_size = max_complexity - min_complexity
            position = (complexity - min_complexity) / range_size
            # Peak score at 70% of the range
            optimal_position = 0.7
            distance_from_optimal = abs(position - optimal_position)
            return 1.0 - (distance_from_optimal * 0.3)


# Global discovery instance
agent_discovery: AgentDiscovery | None = None


async def get_agent_discovery() -> AgentDiscovery:
    """Get the global agent discovery instance."""
    global agent_discovery
    
    if agent_discovery is None:
        agent_discovery = AgentDiscovery()
        await agent_discovery.initialize()
    
    return agent_discovery


async def initialize_agent_discovery(registry: AgentRegistry | None = None) -> AgentDiscovery:
    """Initialize the global agent discovery instance."""
    global agent_discovery
    
    agent_discovery = AgentDiscovery(registry)
    await agent_discovery.initialize()
    
    return agent_discovery