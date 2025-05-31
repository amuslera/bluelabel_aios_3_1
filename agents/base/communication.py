"""
Agent communication interface for AIOSv3 platform.

Provides agent-to-agent communication via message queue system with
request/response patterns, broadcast messaging, and collaboration protocols.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable

from pydantic import BaseModel, Field

from core.messaging.queue import AgentMessage, MessageHandler, MessageQueue
from core.orchestration.discovery import AgentDiscovery
from .exceptions import AgentCommunicationError, TaskTimeoutError
from .types import AgentType, TaskType

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of agent-to-agent messages."""
    
    # Direct communication
    REQUEST = "request"  # Request for action/information
    RESPONSE = "response"  # Response to a request
    NOTIFICATION = "notification"  # One-way notification
    
    # Task coordination
    TASK_ASSIGNMENT = "task_assignment"  # Assign task to agent
    TASK_RESULT = "task_result"  # Task completion result
    TASK_DELEGATION = "task_delegation"  # Delegate task to another agent
    TASK_COLLABORATION = "task_collaboration"  # Collaborative task request
    
    # System messages
    AGENT_ANNOUNCEMENT = "agent_announcement"  # Agent availability announcement
    HEALTH_CHECK = "health_check"  # Health check ping
    STATUS_UPDATE = "status_update"  # Agent status update
    
    # Broadcast messages
    BROADCAST = "broadcast"  # Message to all agents
    TYPE_BROADCAST = "type_broadcast"  # Message to agents of specific type
    CAPABILITY_BROADCAST = "capability_broadcast"  # Message to agents with capability


class Priority(Enum):
    """Message priority levels."""
    
    URGENT = 1  # Immediate processing required
    HIGH = 2    # High priority
    NORMAL = 5  # Normal priority
    LOW = 8     # Low priority
    BACKGROUND = 10  # Background processing


class AgentCommunicationMessage(BaseModel):
    """Standard message format for agent communication."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType
    sender_id: str
    recipient_id: str | None = None  # None for broadcast
    conversation_id: str | None = None  # For tracking conversation threads
    parent_message_id: str | None = None  # For response chains
    
    # Content
    subject: str
    content: dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    priority: Priority = Priority.NORMAL
    timeout_seconds: float | None = None
    requires_response: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    
    # Context
    context: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class ConversationThread(BaseModel):
    """Tracks a conversation between agents."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    participants: list[str]
    subject: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = 0
    is_active: bool = True
    context: dict[str, Any] = Field(default_factory=dict)


class PendingRequest(BaseModel):
    """Tracks pending requests awaiting responses."""
    
    request_id: str
    sender_id: str
    recipient_id: str
    message_type: MessageType
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    timeout_at: datetime
    future: asyncio.Future | None = None  # For async waiting


class AgentCommunicationInterface:
    """
    Handles agent-to-agent communication via message queue.
    
    Features:
    - Request/response patterns with timeout handling
    - Broadcast messaging to multiple agents
    - Conversation threading and context tracking
    - Message routing and delivery confirmation
    - Collaboration patterns for multi-agent tasks
    """
    
    def __init__(
        self,
        agent_id: str,
        message_queue: MessageQueue,
        discovery: AgentDiscovery | None = None,
        default_timeout: float = 30.0,
    ):
        """Initialize the communication interface."""
        self.agent_id = agent_id
        self.message_queue = message_queue
        self.discovery = discovery
        self.default_timeout = default_timeout
        
        # State tracking
        self.pending_requests: dict[str, PendingRequest] = {}
        self.conversations: dict[str, ConversationThread] = {}
        self.message_handlers: dict[MessageType, list[Callable]] = {}
        
        # Background tasks
        self._cleanup_task: asyncio.Task | None = None
        self._shutdown_event = asyncio.Event()
        
        # Statistics
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "requests_sent": 0,
            "requests_received": 0,
            "responses_sent": 0,
            "responses_received": 0,
            "timeouts": 0,
            "errors": 0,
        }

    async def initialize(self) -> None:
        """Initialize the communication interface."""
        try:
            logger.info(f"Initializing communication interface for agent {self.agent_id}")
            
            # Register message handler with queue
            handler = AgentMessageHandler(self)
            await self.message_queue.register_handler(
                agent_id=self.agent_id,
                handler=handler,
                routing_keys=[
                    f"agent.{self.agent_id}",  # Direct messages
                    "agent.broadcast",         # Broadcast messages
                    f"agent.{self.agent_id}.request",  # Direct requests
                    f"agent.{self.agent_id}.response", # Direct responses
                ],
                queue_name=f"agent.{self.agent_id}.inbox",
            )
            
            # Start background cleanup task
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            logger.info(f"Communication interface initialized for agent {self.agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize communication interface: {e}")
            raise AgentCommunicationError(
                f"Communication initialization failed: {e}",
                agent_id=self.agent_id
            )

    async def shutdown(self) -> None:
        """Shutdown the communication interface."""
        try:
            logger.info(f"Shutting down communication interface for agent {self.agent_id}")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Cancel pending requests
            for request in self.pending_requests.values():
                if request.future and not request.future.done():
                    request.future.cancel()
            
            # Stop cleanup task
            if self._cleanup_task:
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass
            
            logger.info(f"Communication interface shutdown complete for agent {self.agent_id}")
            
        except Exception as e:
            logger.error(f"Error during communication shutdown: {e}")

    async def send_request(
        self,
        recipient_id: str,
        subject: str,
        content: dict[str, Any] | None = None,
        message_type: MessageType = MessageType.REQUEST,
        priority: Priority = Priority.NORMAL,
        timeout: float | None = None,
        conversation_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Send a request to another agent and wait for response.
        
        Returns:
            Response content from the recipient agent
        """
        try:
            timeout = timeout or self.default_timeout
            
            # Create request message
            message = AgentCommunicationMessage(
                message_type=message_type,
                sender_id=self.agent_id,
                recipient_id=recipient_id,
                conversation_id=conversation_id,
                subject=subject,
                content=content or {},
                priority=priority,
                timeout_seconds=timeout,
                requires_response=True,
            )
            
            # Create pending request tracker
            future = asyncio.Future()
            pending_request = PendingRequest(
                request_id=message.id,
                sender_id=self.agent_id,
                recipient_id=recipient_id,
                message_type=message_type,
                timeout_at=datetime.utcnow() + timedelta(seconds=timeout),
                future=future,
            )
            
            self.pending_requests[message.id] = pending_request
            
            # Send message
            await self._send_message(message)
            
            # Wait for response with timeout
            try:
                response = await asyncio.wait_for(future, timeout=timeout)
                self.stats["responses_received"] += 1
                return response
                
            except asyncio.TimeoutError:
                self.stats["timeouts"] += 1
                raise TaskTimeoutError(
                    f"Request to {recipient_id} timed out after {timeout}s",
                    agent_id=self.agent_id,
                    task_id=message.id,
                    timeout_seconds=timeout,
                )
            
            finally:
                # Cleanup pending request
                self.pending_requests.pop(message.id, None)
                
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Failed to send request to {recipient_id}: {e}")
            raise AgentCommunicationError(
                f"Request failed: {e}",
                agent_id=self.agent_id,
                target_agent_id=recipient_id,
            )

    async def send_response(
        self,
        request_message: AgentCommunicationMessage,
        content: dict[str, Any],
        success: bool = True,
    ) -> None:
        """Send a response to a request message."""
        try:
            response = AgentCommunicationMessage(
                message_type=MessageType.RESPONSE,
                sender_id=self.agent_id,
                recipient_id=request_message.sender_id,
                conversation_id=request_message.conversation_id,
                parent_message_id=request_message.id,
                subject=f"Re: {request_message.subject}",
                content={
                    "success": success,
                    "data": content,
                },
                priority=request_message.priority,
            )
            
            await self._send_message(response)
            self.stats["responses_sent"] += 1
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Failed to send response: {e}")
            raise AgentCommunicationError(
                f"Response failed: {e}",
                agent_id=self.agent_id,
                target_agent_id=request_message.sender_id,
            )

    async def send_notification(
        self,
        recipient_id: str,
        subject: str,
        content: dict[str, Any] | None = None,
        priority: Priority = Priority.NORMAL,
        conversation_id: str | None = None,
    ) -> None:
        """Send a one-way notification to another agent."""
        try:
            message = AgentCommunicationMessage(
                message_type=MessageType.NOTIFICATION,
                sender_id=self.agent_id,
                recipient_id=recipient_id,
                conversation_id=conversation_id,
                subject=subject,
                content=content or {},
                priority=priority,
                requires_response=False,
            )
            
            await self._send_message(message)
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Failed to send notification to {recipient_id}: {e}")
            raise AgentCommunicationError(
                f"Notification failed: {e}",
                agent_id=self.agent_id,
                target_agent_id=recipient_id,
            )

    async def broadcast_message(
        self,
        subject: str,
        content: dict[str, Any] | None = None,
        target_type: AgentType | None = None,
        target_capability: str | None = None,
        priority: Priority = Priority.NORMAL,
    ) -> None:
        """Broadcast a message to multiple agents."""
        try:
            # Determine broadcast type and routing
            if target_type:
                message_type = MessageType.TYPE_BROADCAST
                routing_key = f"agent.type.{target_type.value}"
            elif target_capability:
                message_type = MessageType.CAPABILITY_BROADCAST
                routing_key = f"agent.capability.{target_capability}"
            else:
                message_type = MessageType.BROADCAST
                routing_key = "agent.broadcast"
            
            message = AgentCommunicationMessage(
                message_type=message_type,
                sender_id=self.agent_id,
                recipient_id=None,  # Broadcast
                subject=subject,
                content=content or {},
                priority=priority,
                requires_response=False,
            )
            
            # Send via specific routing key
            await self.message_queue.publish(
                routing_key=routing_key,
                payload=message.model_dump(),
                sender_id=self.agent_id,
                recipient_id="*",
                message_type=message_type.value,
                priority=priority.value,
            )
            
            self.stats["messages_sent"] += 1
            logger.info(f"Broadcast message sent: {subject}")
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Failed to broadcast message: {e}")
            raise AgentCommunicationError(
                f"Broadcast failed: {e}",
                agent_id=self.agent_id,
            )

    async def delegate_task(
        self,
        task_type: TaskType,
        task_description: str,
        task_parameters: dict[str, Any] | None = None,
        preferred_agent_type: AgentType | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Delegate a task to the most suitable agent."""
        try:
            # Find suitable agent if discovery is available
            target_agent_id = None
            if self.discovery:
                target_agent_id = await self.discovery.find_agent_for_task(
                    task_type=task_type,
                    preferred_agent_type=preferred_agent_type,
                    exclude_agents=[self.agent_id],  # Don't delegate to self
                )
            
            if not target_agent_id:
                raise AgentCommunicationError(
                    f"No suitable agent found for task type {task_type.value}",
                    agent_id=self.agent_id,
                )
            
            # Send task delegation request
            content = {
                "task_type": task_type.value,
                "description": task_description,
                "parameters": task_parameters or {},
                "delegated_by": self.agent_id,
            }
            
            response = await self.send_request(
                recipient_id=target_agent_id,
                subject=f"Task Delegation: {task_type.value}",
                content=content,
                message_type=MessageType.TASK_DELEGATION,
                timeout=timeout,
            )
            
            logger.info(f"Task delegated to {target_agent_id}: {task_description}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to delegate task: {e}")
            raise AgentCommunicationError(
                f"Task delegation failed: {e}",
                agent_id=self.agent_id,
            )

    async def start_conversation(
        self,
        participants: list[str],
        subject: str,
        initial_message: dict[str, Any] | None = None,
    ) -> str:
        """Start a multi-agent conversation."""
        try:
            conversation = ConversationThread(
                participants=[self.agent_id] + participants,
                subject=subject,
            )
            
            self.conversations[conversation.id] = conversation
            
            # Send initial message if provided
            if initial_message:
                for participant in participants:
                    await self.send_notification(
                        recipient_id=participant,
                        subject=f"Conversation: {subject}",
                        content=initial_message,
                        conversation_id=conversation.id,
                    )
            
            logger.info(f"Started conversation {conversation.id}: {subject}")
            return conversation.id
            
        except Exception as e:
            logger.error(f"Failed to start conversation: {e}")
            raise AgentCommunicationError(
                f"Conversation start failed: {e}",
                agent_id=self.agent_id,
            )

    def register_handler(
        self,
        message_type: MessageType,
        handler: Callable[[AgentCommunicationMessage], Any],
    ) -> None:
        """Register a handler for specific message types."""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        
        self.message_handlers[message_type].append(handler)
        logger.debug(f"Registered handler for {message_type.value}")

    async def handle_incoming_message(self, raw_message: AgentMessage) -> None:
        """Handle incoming messages from the message queue."""
        try:
            # Parse agent communication message
            message_data = raw_message.payload
            message = AgentCommunicationMessage.model_validate(message_data)
            
            self.stats["messages_received"] += 1
            
            # Update conversation tracking
            if message.conversation_id:
                await self._update_conversation(message)
            
            # Handle responses to pending requests
            if message.message_type == MessageType.RESPONSE and message.parent_message_id:
                await self._handle_response(message)
                return
            
            # Route to registered handlers
            handlers = self.message_handlers.get(message.message_type, [])
            for handler in handlers:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"Handler error for {message.message_type.value}: {e}")
            
            # Track request statistics
            if message.message_type in [MessageType.REQUEST, MessageType.TASK_DELEGATION]:
                self.stats["requests_received"] += 1
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Error handling incoming message: {e}")

    def get_stats(self) -> dict[str, Any]:
        """Get communication statistics."""
        return {
            **self.stats,
            "pending_requests": len(self.pending_requests),
            "active_conversations": len([c for c in self.conversations.values() if c.is_active]),
            "total_conversations": len(self.conversations),
        }

    # Private helper methods
    
    async def _send_message(self, message: AgentCommunicationMessage) -> None:
        """Send a message via the message queue."""
        # Determine routing key
        if message.recipient_id:
            routing_key = f"agent.{message.recipient_id}"
        else:
            routing_key = "agent.broadcast"
        
        # Add request suffix for requests
        if message.message_type in [MessageType.REQUEST, MessageType.TASK_DELEGATION]:
            routing_key += ".request"
        elif message.message_type == MessageType.RESPONSE:
            routing_key += ".response"
        
        await self.message_queue.publish(
            routing_key=routing_key,
            payload=message.model_dump(),
            sender_id=self.agent_id,
            recipient_id=message.recipient_id or "*",
            message_type=message.message_type.value,
            priority=message.priority.value,
        )
        
        self.stats["messages_sent"] += 1
        
        # Track request statistics
        if message.message_type in [MessageType.REQUEST, MessageType.TASK_DELEGATION]:
            self.stats["requests_sent"] += 1

    async def _handle_response(self, response: AgentCommunicationMessage) -> None:
        """Handle response to a pending request."""
        request_id = response.parent_message_id
        pending_request = self.pending_requests.get(request_id)
        
        if pending_request and pending_request.future and not pending_request.future.done():
            # Resolve the pending future with response content
            pending_request.future.set_result(response.content)
        else:
            logger.warning(f"Received response for unknown request {request_id}")

    async def _update_conversation(self, message: AgentCommunicationMessage) -> None:
        """Update conversation tracking."""
        conversation_id = message.conversation_id
        if conversation_id in self.conversations:
            conversation = self.conversations[conversation_id]
            conversation.last_activity = datetime.utcnow()
            conversation.message_count += 1
            
            # Add new participants if not already included
            if message.sender_id not in conversation.participants:
                conversation.participants.append(message.sender_id)

    async def _cleanup_loop(self) -> None:
        """Background loop to cleanup expired requests and conversations."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(10)  # Cleanup every 10 seconds
                await self._cleanup_expired_requests()
                await self._cleanup_old_conversations()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    async def _cleanup_expired_requests(self) -> None:
        """Remove expired pending requests."""
        now = datetime.utcnow()
        expired_requests = [
            req_id for req_id, req in self.pending_requests.items()
            if req.timeout_at < now
        ]
        
        for req_id in expired_requests:
            pending_request = self.pending_requests.pop(req_id)
            if pending_request.future and not pending_request.future.done():
                pending_request.future.cancel()
        
        if expired_requests:
            logger.debug(f"Cleaned up {len(expired_requests)} expired requests")

    async def _cleanup_old_conversations(self) -> None:
        """Remove old inactive conversations."""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)  # Keep for 24 hours
        
        old_conversations = [
            conv_id for conv_id, conv in self.conversations.items()
            if conv.last_activity < cutoff_time and not conv.is_active
        ]
        
        for conv_id in old_conversations:
            del self.conversations[conv_id]
        
        if old_conversations:
            logger.debug(f"Cleaned up {len(old_conversations)} old conversations")


class AgentMessageHandler(MessageHandler):
    """Message handler that routes messages to agent communication interface."""
    
    def __init__(self, comm_interface: AgentCommunicationInterface):
        self.comm_interface = comm_interface

    async def handle_message(self, message: AgentMessage) -> AgentMessage | None:
        """Handle incoming messages and route to communication interface."""
        await self.comm_interface.handle_incoming_message(message)
        # No response needed as responses are handled separately
        return None