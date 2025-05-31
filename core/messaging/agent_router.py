"""
Agent message router for AIOSv3 platform.

Provides intelligent message routing for agent-to-agent communication,
including broadcast handling, load balancing, and failover routing.
"""

import logging
from typing import Any

from agents.base.types import AgentType, TaskType
from core.orchestration.discovery import AgentDiscovery
from core.orchestration.registry import AgentRegistry
from .queue import MessageQueue
from .routing import MessageRouter, RoutingDecision

logger = logging.getLogger(__name__)


class AgentMessageRouter(MessageRouter):
    """
    Specialized message router for agent communication.
    
    Features:
    - Agent-aware routing based on capabilities
    - Load balancing across available agents
    - Broadcast message distribution
    - Failover routing for unavailable agents
    - Type and capability-based routing
    """
    
    def __init__(
        self,
        registry: AgentRegistry,
        discovery: AgentDiscovery,
        message_queue: MessageQueue,
    ):
        """Initialize the agent message router."""
        super().__init__()
        self.registry = registry
        self.discovery = discovery
        self.message_queue = message_queue

    async def route_message(
        self,
        routing_key: str,
        payload: dict[str, Any],
        sender_id: str,
        recipient_id: str | None = None,
        message_type: str = "general",
        priority: int = 5,
        **kwargs
    ) -> RoutingDecision:
        """
        Route a message to the appropriate agent(s).
        
        Args:
            routing_key: Original routing key
            payload: Message payload
            sender_id: ID of sending agent
            recipient_id: ID of target agent (None for broadcast)
            message_type: Type of message
            priority: Message priority
            
        Returns:
            RoutingDecision: Decision on how to route the message
        """
        try:
            logger.debug(f"Routing message from {sender_id} to {recipient_id}: {routing_key}")
            
            # Handle direct agent messages
            if recipient_id and recipient_id != "*":
                return await self._route_direct_message(
                    routing_key, payload, sender_id, recipient_id, message_type, priority
                )
            
            # Handle broadcast messages
            if routing_key.startswith("agent.broadcast") or recipient_id == "*":
                return await self._route_broadcast_message(
                    routing_key, payload, sender_id, message_type, priority
                )
            
            # Handle type-based routing
            if "agent.type." in routing_key:
                return await self._route_type_based_message(
                    routing_key, payload, sender_id, message_type, priority
                )
            
            # Handle capability-based routing
            if "agent.capability." in routing_key:
                return await self._route_capability_based_message(
                    routing_key, payload, sender_id, message_type, priority
                )
            
            # Handle task delegation routing
            if message_type in ["task_delegation", "task_assignment"]:
                return await self._route_task_message(
                    routing_key, payload, sender_id, message_type, priority
                )
            
            # Default routing
            return await self._route_default(routing_key, payload, sender_id, priority)
            
        except Exception as e:
            logger.error(f"Error routing message: {e}")
            # Return original routing as fallback
            return RoutingDecision(
                routing_key=routing_key,
                exchange="agents",
                queue_name=f"agent.{recipient_id or 'unknown'}",
                success=False,
                reason=f"Routing error: {e}",
            )

    async def _route_direct_message(
        self,
        routing_key: str,
        payload: dict[str, Any],
        sender_id: str,
        recipient_id: str,
        message_type: str,
        priority: int,
    ) -> RoutingDecision:
        """Route a direct message to a specific agent."""
        try:
            # Check if recipient agent exists and is available
            health = await self.registry.get_agent_health(recipient_id)
            
            if not health:
                # Agent not found - try to find alternative
                logger.warning(f"Agent {recipient_id} not found, attempting failover")
                return await self._route_with_failover(
                    routing_key, payload, sender_id, recipient_id, message_type, priority
                )
            
            if not health.is_healthy:
                # Agent unhealthy - try failover
                logger.warning(f"Agent {recipient_id} is unhealthy, attempting failover")
                return await self._route_with_failover(
                    routing_key, payload, sender_id, recipient_id, message_type, priority
                )
            
            # Route to specific agent queue
            queue_name = f"agent.{recipient_id}.inbox"
            
            return RoutingDecision(
                routing_key=f"agent.{recipient_id}",
                exchange="agents",
                queue_name=queue_name,
                success=True,
                reason=f"Direct routing to agent {recipient_id}",
                metadata={
                    "recipient_health_score": health.health_score,
                    "recipient_state": health.state.value,
                }
            )
            
        except Exception as e:
            logger.error(f"Error in direct message routing: {e}")
            return RoutingDecision(
                routing_key=routing_key,
                exchange="agents",
                queue_name=f"agent.{recipient_id}.inbox",
                success=False,
                reason=f"Direct routing error: {e}",
            )

    async def _route_broadcast_message(
        self,
        routing_key: str,
        payload: dict[str, Any],
        sender_id: str,
        message_type: str,
        priority: int,
    ) -> RoutingDecision:
        """Route a broadcast message to all agents."""
        try:
            # Get all healthy agents
            all_agents = await self.registry.list_agents(healthy_only=True)
            recipient_count = len(all_agents)
            
            # Use fanout exchange for broadcast
            return RoutingDecision(
                routing_key="",  # Fanout ignores routing key
                exchange="agents.broadcast",
                queue_name="",  # Fanout to all bound queues
                success=True,
                reason=f"Broadcast to {recipient_count} agents",
                metadata={
                    "broadcast_type": "all_agents",
                    "recipient_count": recipient_count,
                    "recipients": all_agents,
                }
            )
            
        except Exception as e:
            logger.error(f"Error in broadcast routing: {e}")
            return RoutingDecision(
                routing_key="agent.broadcast",
                exchange="agents",
                queue_name="agent.broadcast",
                success=False,
                reason=f"Broadcast routing error: {e}",
            )

    async def _route_type_based_message(
        self,
        routing_key: str,
        payload: dict[str, Any],
        sender_id: str,
        message_type: str,
        priority: int,
    ) -> RoutingDecision:
        """Route message to agents of a specific type."""
        try:
            # Extract agent type from routing key
            # Format: agent.type.{agent_type}
            parts = routing_key.split(".")
            if len(parts) < 3:
                raise ValueError(f"Invalid type routing key: {routing_key}")
            
            agent_type_str = parts[2]
            agent_type = AgentType(agent_type_str)
            
            # Find agents of this type
            agents = await self.discovery.find_agents_by_type(
                agent_type=agent_type,
                healthy_only=True,
                available_only=True,
            )
            
            if not agents:
                return RoutingDecision(
                    routing_key=routing_key,
                    exchange="agents",
                    queue_name="",
                    success=False,
                    reason=f"No available agents of type {agent_type.value}",
                )
            
            # For type broadcast, use topic exchange
            return RoutingDecision(
                routing_key=f"agent.type.{agent_type.value}",
                exchange="agents.topics",
                queue_name="",  # Topic routing to multiple queues
                success=True,
                reason=f"Type routing to {len(agents)} {agent_type.value} agents",
                metadata={
                    "agent_type": agent_type.value,
                    "recipient_count": len(agents),
                    "recipients": agents,
                }
            )
            
        except Exception as e:
            logger.error(f"Error in type-based routing: {e}")
            return RoutingDecision(
                routing_key=routing_key,
                exchange="agents",
                queue_name="",
                success=False,
                reason=f"Type routing error: {e}",
            )

    async def _route_capability_based_message(
        self,
        routing_key: str,
        payload: dict[str, Any],
        sender_id: str,
        message_type: str,
        priority: int,
    ) -> RoutingDecision:
        """Route message to agents with a specific capability."""
        try:
            # Extract capability from routing key
            # Format: agent.capability.{capability_name}
            parts = routing_key.split(".")
            if len(parts) < 3:
                raise ValueError(f"Invalid capability routing key: {routing_key}")
            
            capability = parts[2]
            
            # Find agents with this capability
            agents = await self.discovery.find_agents_by_capability(
                capability=capability,
                healthy_only=True,
                available_only=True,
            )
            
            if not agents:
                return RoutingDecision(
                    routing_key=routing_key,
                    exchange="agents",
                    queue_name="",
                    success=False,
                    reason=f"No available agents with capability {capability}",
                )
            
            # Route to capability-based topic
            return RoutingDecision(
                routing_key=f"agent.capability.{capability}",
                exchange="agents.topics",
                queue_name="",
                success=True,
                reason=f"Capability routing to {len(agents)} agents with {capability}",
                metadata={
                    "capability": capability,
                    "recipient_count": len(agents),
                    "recipients": agents,
                }
            )
            
        except Exception as e:
            logger.error(f"Error in capability-based routing: {e}")
            return RoutingDecision(
                routing_key=routing_key,
                exchange="agents",
                queue_name="",
                success=False,
                reason=f"Capability routing error: {e}",
            )

    async def _route_task_message(
        self,
        routing_key: str,
        payload: dict[str, Any],
        sender_id: str,
        message_type: str,
        priority: int,
    ) -> RoutingDecision:
        """Route task-related messages to optimal agents."""
        try:
            # Extract task information from payload
            task_type_str = payload.get("task_type")
            complexity = payload.get("complexity", 5)
            preferred_agent_type_str = payload.get("preferred_agent_type")
            
            if not task_type_str:
                raise ValueError("Task messages must include task_type")
            
            task_type = TaskType(task_type_str)
            preferred_agent_type = None
            if preferred_agent_type_str:
                preferred_agent_type = AgentType(preferred_agent_type_str)
            
            # Find best agent for the task
            best_agent = await self.discovery.find_agent_for_task(
                task_type=task_type,
                complexity=complexity,
                preferred_agent_type=preferred_agent_type,
                exclude_agents=[sender_id],  # Don't route back to sender
            )
            
            if not best_agent:
                return RoutingDecision(
                    routing_key=routing_key,
                    exchange="agents",
                    queue_name="",
                    success=False,
                    reason=f"No suitable agent found for task {task_type.value}",
                )
            
            # Route to the selected agent
            return RoutingDecision(
                routing_key=f"agent.{best_agent}",
                exchange="agents",
                queue_name=f"agent.{best_agent}.inbox",
                success=True,
                reason=f"Task routing to optimal agent {best_agent}",
                metadata={
                    "task_type": task_type.value,
                    "complexity": complexity,
                    "selected_agent": best_agent,
                    "routing_method": "intelligent_selection",
                }
            )
            
        except Exception as e:
            logger.error(f"Error in task message routing: {e}")
            return RoutingDecision(
                routing_key=routing_key,
                exchange="agents",
                queue_name="",
                success=False,
                reason=f"Task routing error: {e}",
            )

    async def _route_with_failover(
        self,
        routing_key: str,
        payload: dict[str, Any],
        sender_id: str,
        original_recipient: str,
        message_type: str,
        priority: int,
    ) -> RoutingDecision:
        """Route with failover when primary recipient is unavailable."""
        try:
            # Get original recipient's metadata to find similar agents
            metadata = await self.registry.get_agent_metadata(original_recipient)
            
            if metadata:
                # Find agents of the same type
                alternative_agents = await self.discovery.find_agents_by_type(
                    agent_type=metadata.type,
                    healthy_only=True,
                    available_only=True,
                )
                
                # Remove original recipient and sender from alternatives
                alternative_agents = [
                    agent for agent in alternative_agents 
                    if agent not in [original_recipient, sender_id]
                ]
                
                if alternative_agents:
                    # Select best alternative using load balancing
                    selected_agent = await self.discovery.select_agent_with_load_balancing(
                        alternative_agents,
                        strategy="least_loaded",
                    )
                    
                    if selected_agent:
                        return RoutingDecision(
                            routing_key=f"agent.{selected_agent}",
                            exchange="agents",
                            queue_name=f"agent.{selected_agent}.inbox",
                            success=True,
                            reason=f"Failover routing to {selected_agent} (original: {original_recipient})",
                            metadata={
                                "original_recipient": original_recipient,
                                "failover_recipient": selected_agent,
                                "failover_reason": "recipient_unavailable",
                            }
                        )
            
            # No suitable failover found
            return RoutingDecision(
                routing_key=routing_key,
                exchange="agents",
                queue_name=f"agent.{original_recipient}.inbox",
                success=False,
                reason=f"No failover agent available for {original_recipient}",
                metadata={
                    "original_recipient": original_recipient,
                    "failover_attempted": True,
                    "failover_success": False,
                }
            )
            
        except Exception as e:
            logger.error(f"Error in failover routing: {e}")
            return RoutingDecision(
                routing_key=routing_key,
                exchange="agents",
                queue_name=f"agent.{original_recipient}.inbox",
                success=False,
                reason=f"Failover routing error: {e}",
            )

    async def _route_default(
        self,
        routing_key: str,
        payload: dict[str, Any],
        sender_id: str,
        priority: int,
    ) -> RoutingDecision:
        """Default routing for unmatched patterns."""
        # Extract potential recipient from routing key
        parts = routing_key.split(".")
        if len(parts) >= 2 and parts[0] == "agent":
            recipient_id = parts[1]
            return RoutingDecision(
                routing_key=routing_key,
                exchange="agents",
                queue_name=f"agent.{recipient_id}.inbox",
                success=True,
                reason="Default routing based on routing key pattern",
            )
        
        # Fallback to general routing
        return RoutingDecision(
            routing_key=routing_key,
            exchange="agents",
            queue_name="agent.general",
            success=True,
            reason="Fallback to general agent queue",
        )


async def initialize_agent_router(
    registry: AgentRegistry,
    discovery: AgentDiscovery,
    message_queue: MessageQueue,
) -> AgentMessageRouter:
    """Initialize and configure the agent message router."""
    router = AgentMessageRouter(registry, discovery, message_queue)
    
    # Register the router with the message queue
    message_queue.set_router(router)
    
    logger.info("Agent message router initialized and configured")
    return router