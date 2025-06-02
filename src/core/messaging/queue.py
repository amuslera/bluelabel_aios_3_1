"""
RabbitMQ message queue client for AIOSv3.

Provides publisher/consumer abstractions for reliable agent-to-agent communication.
"""

import asyncio
import json
import logging
import os
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

import aio_pika
from aio_pika import Exchange, Message, Queue
from aio_pika.abc import AbstractRobustConnection
from pydantic import BaseModel

logger = logging.getLogger(__name__)


@dataclass
class MessageEnvelope:
    """Envelope for messages with metadata."""

    id: str
    sender_id: str
    recipient_id: str
    message_type: str
    priority: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None


class AgentMessage(BaseModel):
    """Standard message format for agent communication."""

    envelope: dict[str, Any]  # MessageEnvelope as dict
    payload: dict[str, Any]
    metadata: dict[str, Any] = {}


class MessageHandler(ABC):
    """Abstract base class for message handlers."""

    @abstractmethod
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle an incoming message and optionally return a response."""
        pass


class MessageQueue:
    """
    Asynchronous RabbitMQ client for agent communication.

    Features:
    - Automatic connection management with retry
    - Publisher/consumer abstractions
    - Dead letter queue support
    - Message routing and exchanges
    - Health monitoring
    """

    def __init__(
        self,
        rabbitmq_url: Optional[str] = None,
        exchange_name: str = "aiosv3.agents",
        dlx_name: str = "aiosv3.agents.dlx",
    ):
        """
        Initialize the message queue client.

        Args:
            rabbitmq_url: RabbitMQ connection URL
            exchange_name: Main exchange for agent communication
            dlx_name: Dead letter exchange for failed messages
        """
        self.rabbitmq_url = rabbitmq_url or os.getenv(
            "RABBITMQ_URL", "amqp://aiosv3:dev_password@localhost:5672/"
        )
        self.exchange_name = exchange_name
        self.dlx_name = dlx_name

        self.connection: Optional[AbstractRobustConnection] = None
        self.channel = None
        self.exchange: Optional[Exchange] = None
        self.dlx: Optional[Exchange] = None

        self.message_handlers: dict[str, MessageHandler] = {}
        self.is_connected = False

    async def connect(self) -> None:
        """Establish connection to RabbitMQ."""
        try:
            logger.info(f"Connecting to RabbitMQ at {self.rabbitmq_url}")

            self.connection = await aio_pika.connect_robust(
                self.rabbitmq_url, client_properties={"connection_name": "aiosv3-agent"}
            )

            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)

            # Create main exchange
            self.exchange = await self.channel.declare_exchange(
                self.exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
            )

            # Create dead letter exchange
            self.dlx = await self.channel.declare_exchange(
                self.dlx_name, aio_pika.ExchangeType.TOPIC, durable=True
            )

            self.is_connected = True
            logger.info("Successfully connected to RabbitMQ")

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def disconnect(self) -> None:
        """Close connection to RabbitMQ."""
        if self.connection:
            await self.connection.close()
            self.is_connected = False
            logger.info("Disconnected from RabbitMQ")

    async def publish(
        self,
        routing_key: str,
        payload: dict[str, Any],
        sender_id: str,
        recipient_id: str = "*",
        message_type: str = "general",
        priority: int = 5,
        correlation_id: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> str:
        """
        Publish a message to the exchange.

        Args:
            routing_key: Routing key for message delivery
            payload: Message payload
            sender_id: ID of the sending agent
            recipient_id: ID of the target agent (or "*" for broadcast)
            message_type: Type of message
            priority: Message priority (1-10)
            correlation_id: Correlation ID for request/response
            reply_to: Queue name for responses

        Returns:
            str: Message ID
        """
        if not self.is_connected:
            await self.connect()

        message_id = str(uuid.uuid4())

        envelope = MessageEnvelope(
            id=message_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=message_type,
            priority=priority,
            created_at=datetime.utcnow(),
            correlation_id=correlation_id,
            reply_to=reply_to,
        )

        agent_message = AgentMessage(
            envelope=envelope.__dict__,
            payload=payload,
            metadata={
                "routing_key": routing_key,
                "published_at": datetime.utcnow().isoformat(),
            },
        )

        message_body = agent_message.model_dump_json().encode()

        message = Message(
            message_body,
            message_id=message_id,
            correlation_id=correlation_id,
            reply_to=reply_to,
            priority=priority,
            delivery_mode=2,  # Persistent
            headers={
                "sender_id": sender_id,
                "recipient_id": recipient_id,
                "message_type": message_type,
            },
        )

        await self.exchange.publish(message, routing_key=routing_key)

        logger.debug(f"Published message {message_id} to {routing_key}")
        return message_id

    async def create_queue(
        self,
        queue_name: str,
        routing_keys: list[str],
        agent_id: str,
        durable: bool = True,
        exclusive: bool = False,
    ) -> Queue:
        """
        Create a queue bound to routing keys.

        Args:
            queue_name: Name of the queue
            routing_keys: List of routing patterns to bind
            agent_id: ID of the agent that owns this queue
            durable: Whether queue survives broker restart
            exclusive: Whether queue is exclusive to connection

        Returns:
            Queue: The created queue
        """
        if not self.is_connected:
            await self.connect()

        # Create queue with DLX configuration
        queue_args = {
            "x-dead-letter-exchange": self.dlx_name,
            "x-dead-letter-routing-key": f"failed.{agent_id}",
            "x-message-ttl": 3600000,  # 1 hour TTL
            "x-max-retries": 3,
        }

        queue = await self.channel.declare_queue(
            queue_name, durable=durable, exclusive=exclusive, arguments=queue_args
        )

        # Bind to routing keys
        for routing_key in routing_keys:
            await queue.bind(self.exchange, routing_key)
            logger.debug(f"Bound queue {queue_name} to {routing_key}")

        return queue

    async def register_handler(
        self,
        agent_id: str,
        handler: MessageHandler,
        routing_keys: list[str],
        queue_name: Optional[str] = None,
    ) -> None:
        """
        Register a message handler for an agent.

        Args:
            agent_id: ID of the agent
            handler: Message handler instance
            routing_keys: Routing patterns to listen for
            queue_name: Custom queue name (defaults to agent_id)
        """
        queue_name = queue_name or f"agent.{agent_id}"

        queue = await self.create_queue(
            queue_name=queue_name, routing_keys=routing_keys, agent_id=agent_id
        )

        self.message_handlers[agent_id] = handler

        async def process_message(message: aio_pika.IncomingMessage) -> None:
            async with message.process():
                try:
                    # Parse message
                    agent_message = AgentMessage.model_validate_json(message.body)

                    logger.debug(
                        f"Received message {agent_message.envelope['id']} for {agent_id}"
                    )

                    # Handle message
                    response = await handler.handle_message(agent_message)

                    # Send response if provided and reply_to is set
                    if response and agent_message.envelope.get("reply_to"):
                        await self.publish(
                            routing_key=agent_message.envelope["reply_to"],
                            payload=response.payload,
                            sender_id=agent_id,
                            recipient_id=agent_message.envelope["sender_id"],
                            message_type="response",
                            correlation_id=agent_message.envelope.get("correlation_id"),
                        )

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse message: {e}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    # Message will be sent to DLX due to exception
                    raise

        await queue.consume(process_message)
        logger.info(f"Registered handler for agent {agent_id} on queue {queue_name}")

    async def send_to_agent(
        self,
        target_agent_id: str,
        payload: dict[str, Any],
        sender_id: str,
        message_type: str = "task",
        priority: int = 5,
        wait_for_response: bool = False,
        timeout: float = 30.0,
    ) -> Optional[AgentMessage]:
        """
        Send a message directly to another agent.

        Args:
            target_agent_id: ID of the target agent
            payload: Message payload
            sender_id: ID of the sending agent
            message_type: Type of message
            priority: Message priority
            wait_for_response: Whether to wait for a response
            timeout: Response timeout in seconds

        Returns:
            AgentMessage: Response message if wait_for_response=True
        """
        routing_key = f"agent.{target_agent_id}.{message_type}"

        correlation_id = None
        reply_to = None

        if wait_for_response:
            correlation_id = str(uuid.uuid4())
            reply_to = f"response.{sender_id}.{correlation_id}"

            # Create temporary response queue
            response_queue = await self.create_queue(
                queue_name=reply_to,
                routing_keys=[reply_to],
                agent_id=sender_id,
                durable=False,
                exclusive=True,
            )

        # Send message
        message_id = await self.publish(
            routing_key=routing_key,
            payload=payload,
            sender_id=sender_id,
            recipient_id=target_agent_id,
            message_type=message_type,
            priority=priority,
            correlation_id=correlation_id,
            reply_to=reply_to,
        )

        if not wait_for_response:
            return None

        # Wait for response
        try:
            response_future = asyncio.Future()

            async def handle_response(message: aio_pika.IncomingMessage) -> None:
                async with message.process():
                    if message.correlation_id == correlation_id:
                        agent_message = AgentMessage.model_validate_json(message.body)
                        response_future.set_result(agent_message)

            await response_queue.consume(handle_response)

            response = await asyncio.wait_for(response_future, timeout=timeout)
            return response

        except TimeoutError:
            logger.warning(f"Timeout waiting for response from {target_agent_id}")
            return None
        finally:
            # Clean up response queue
            if wait_for_response:
                await response_queue.delete()

    async def broadcast(
        self,
        payload: dict[str, Any],
        sender_id: str,
        message_type: str = "broadcast",
        agent_filter: Optional[str] = None,
    ) -> str:
        """
        Broadcast a message to all agents.

        Args:
            payload: Message payload
            sender_id: ID of the sending agent
            message_type: Type of message
            agent_filter: Optional filter pattern for agents

        Returns:
            str: Message ID
        """
        routing_key = f"broadcast.{message_type}"
        if agent_filter:
            routing_key += f".{agent_filter}"

        return await self.publish(
            routing_key=routing_key,
            payload=payload,
            sender_id=sender_id,
            recipient_id="*",
            message_type=message_type,
        )

    async def health_check(self) -> dict[str, Any]:
        """Check the health of the message queue connection."""
        if not self.is_connected:
            return {
                "status": "disconnected",
                "connected": False,
                "exchange": None,
            }

        try:
            # Test connection by declaring a temporary queue
            test_queue = await self.channel.declare_queue(
                f"health.check.{uuid.uuid4()}",
                exclusive=True,
                auto_delete=True,
            )
            await test_queue.delete()

            return {
                "status": "healthy",
                "connected": True,
                "exchange": self.exchange_name,
                "dlx": self.dlx_name,
                "url": self.rabbitmq_url,
            }
        except Exception as e:
            return {
                "status": "error",
                "connected": self.is_connected,
                "error": str(e),
            }


# Global message queue instance
message_queue = MessageQueue()
