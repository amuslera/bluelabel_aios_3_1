"""
Unit tests for agent communication system.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

from agents.base.communication import (
    AgentCommunicationInterface,
    AgentCommunicationMessage,
    MessageType,
    Priority,
    ConversationThread,
    PendingRequest,
)
from agents.base.types import AgentType, TaskType
from agents.base.exceptions import AgentCommunicationError, TaskTimeoutError
from core.messaging.agent_router import AgentMessageRouter


@pytest.fixture
def mock_message_queue():
    """Create a mock message queue."""
    queue = AsyncMock()
    queue.register_handler = AsyncMock()
    queue.publish = AsyncMock()
    return queue


@pytest.fixture
def mock_discovery():
    """Create a mock agent discovery service."""
    discovery = AsyncMock()
    discovery.find_agent_for_task = AsyncMock(return_value="target-agent")
    return discovery


@pytest.fixture
def communication_interface(mock_message_queue, mock_discovery):
    """Create a communication interface for testing."""
    return AgentCommunicationInterface(
        agent_id="test-agent",
        message_queue=mock_message_queue,
        discovery=mock_discovery,
        default_timeout=10.0,
    )


@pytest.fixture
def sample_message():
    """Create a sample communication message."""
    return AgentCommunicationMessage(
        message_type=MessageType.REQUEST,
        sender_id="sender-agent",
        recipient_id="test-agent",
        subject="Test Request",
        content={"test": "data"},
        requires_response=True,
    )


class TestAgentCommunicationMessage:
    """Test cases for AgentCommunicationMessage model."""

    def test_message_creation(self):
        """Test basic message creation."""
        message = AgentCommunicationMessage(
            message_type=MessageType.NOTIFICATION,
            sender_id="agent-1",
            recipient_id="agent-2",
            subject="Test Message",
            content={"key": "value"},
        )
        
        assert message.message_type == MessageType.NOTIFICATION
        assert message.sender_id == "agent-1"
        assert message.recipient_id == "agent-2"
        assert message.subject == "Test Message"
        assert message.content == {"key": "value"}
        assert message.priority == Priority.NORMAL
        assert not message.requires_response
        assert isinstance(message.created_at, datetime)

    def test_message_with_conversation(self):
        """Test message with conversation tracking."""
        conversation_id = "conv-123"
        parent_id = "parent-456"
        
        message = AgentCommunicationMessage(
            message_type=MessageType.RESPONSE,
            sender_id="agent-1",
            recipient_id="agent-2",
            subject="Response",
            conversation_id=conversation_id,
            parent_message_id=parent_id,
            content={"response": "data"},
        )
        
        assert message.conversation_id == conversation_id
        assert message.parent_message_id == parent_id

    def test_message_with_expiration(self):
        """Test message with expiration time."""
        expires_at = datetime.utcnow() + timedelta(minutes=30)
        
        message = AgentCommunicationMessage(
            message_type=MessageType.REQUEST,
            sender_id="agent-1",
            recipient_id="agent-2",
            subject="Expiring Request",
            expires_at=expires_at,
            content={},
        )
        
        assert message.expires_at == expires_at


class TestAgentCommunicationInterface:
    """Test cases for AgentCommunicationInterface."""

    @pytest.mark.asyncio
    async def test_interface_initialization(self, communication_interface, mock_message_queue):
        """Test communication interface initialization."""
        await communication_interface.initialize()
        
        # Verify message queue handler registration
        mock_message_queue.register_handler.assert_called_once()
        call_args = mock_message_queue.register_handler.call_args
        
        assert call_args[1]["agent_id"] == "test-agent"
        assert "agent.test-agent" in call_args[1]["routing_keys"]
        assert "agent.broadcast" in call_args[1]["routing_keys"]

    @pytest.mark.asyncio
    async def test_send_notification(self, communication_interface, mock_message_queue):
        """Test sending a notification message."""
        await communication_interface.initialize()
        
        await communication_interface.send_notification(
            recipient_id="target-agent",
            subject="Test Notification",
            content={"message": "Hello"},
            priority=Priority.HIGH,
        )
        
        # Verify message was published
        mock_message_queue.publish.assert_called()
        call_args = mock_message_queue.publish.call_args[1]
        
        assert call_args["routing_key"] == "agent.target-agent"
        assert call_args["sender_id"] == "test-agent"
        assert call_args["recipient_id"] == "target-agent"
        assert call_args["priority"] == Priority.HIGH.value

    @pytest.mark.asyncio
    async def test_send_request_and_response(self, communication_interface, mock_message_queue):
        """Test request/response pattern."""
        await communication_interface.initialize()
        
        # Mock the response by manually resolving the future
        async def mock_response():
            # Find the pending request and resolve it
            await asyncio.sleep(0.1)  # Small delay to let request setup
            for request in communication_interface.pending_requests.values():
                if request.future and not request.future.done():
                    request.future.set_result({"success": True, "data": {"result": "success"}})
                    break
        
        # Start the mock response task
        response_task = asyncio.create_task(mock_response())
        
        # Send request
        response = await communication_interface.send_request(
            recipient_id="target-agent",
            subject="Test Request",
            content={"query": "test"},
            timeout=1.0,
        )
        
        await response_task
        
        assert response["success"] is True
        assert response["data"]["result"] == "success"
        
        # Verify stats were updated
        assert communication_interface.stats["requests_sent"] == 1
        assert communication_interface.stats["responses_received"] == 1

    @pytest.mark.asyncio
    async def test_request_timeout(self, communication_interface):
        """Test request timeout handling."""
        await communication_interface.initialize()
        
        # Send request that will timeout
        with pytest.raises(TaskTimeoutError):
            await communication_interface.send_request(
                recipient_id="unavailable-agent",
                subject="Timeout Request",
                timeout=0.1,  # Very short timeout
            )
        
        # Verify timeout was recorded
        assert communication_interface.stats["timeouts"] == 1

    @pytest.mark.asyncio
    async def test_broadcast_message(self, communication_interface, mock_message_queue):
        """Test broadcasting messages."""
        await communication_interface.initialize()
        
        # Test general broadcast
        await communication_interface.broadcast_message(
            subject="General Announcement",
            content={"announcement": "System maintenance"},
        )
        
        mock_message_queue.publish.assert_called()
        call_args = mock_message_queue.publish.call_args[1]
        assert call_args["routing_key"] == "agent.broadcast"
        assert call_args["recipient_id"] == "*"

    @pytest.mark.asyncio
    async def test_type_broadcast(self, communication_interface, mock_message_queue):
        """Test broadcasting to specific agent types."""
        await communication_interface.initialize()
        
        await communication_interface.broadcast_message(
            subject="Backend Announcement",
            content={"message": "Backend update"},
            target_type=AgentType.BACKEND_DEV,
        )
        
        mock_message_queue.publish.assert_called()
        call_args = mock_message_queue.publish.call_args[1]
        assert call_args["routing_key"] == "agent.type.backend_developer"

    @pytest.mark.asyncio
    async def test_capability_broadcast(self, communication_interface, mock_message_queue):
        """Test broadcasting to agents with specific capabilities."""
        await communication_interface.initialize()
        
        await communication_interface.broadcast_message(
            subject="Code Review Request",
            content={"code": "review_this"},
            target_capability="code_review",
        )
        
        mock_message_queue.publish.assert_called()
        call_args = mock_message_queue.publish.call_args[1]
        assert call_args["routing_key"] == "agent.capability.code_review"

    @pytest.mark.asyncio
    async def test_task_delegation(self, communication_interface, mock_discovery):
        """Test task delegation to suitable agents."""
        await communication_interface.initialize()
        
        # Mock discovery to return a suitable agent
        mock_discovery.find_agent_for_task.return_value = "backend-agent"
        
        # Mock the response
        async def mock_response():
            await asyncio.sleep(0.1)
            for request in communication_interface.pending_requests.values():
                if request.future and not request.future.done():
                    request.future.set_result({
                        "success": True,
                        "data": {"task_completed": True, "result": "Task done"}
                    })
                    break
        
        response_task = asyncio.create_task(mock_response())
        
        # Delegate task
        result = await communication_interface.delegate_task(
            task_type=TaskType.CODE_GENERATION,
            task_description="Generate user authentication module",
            task_parameters={"language": "python"},
            preferred_agent_type=AgentType.BACKEND_DEV,
        )
        
        await response_task
        
        assert result["success"] is True
        assert result["data"]["task_completed"] is True
        
        # Verify discovery was called correctly
        mock_discovery.find_agent_for_task.assert_called_with(
            task_type=TaskType.CODE_GENERATION,
            preferred_agent_type=AgentType.BACKEND_DEV,
            exclude_agents=["test-agent"],
        )

    @pytest.mark.asyncio
    async def test_conversation_management(self, communication_interface):
        """Test conversation thread management."""
        await communication_interface.initialize()
        
        participants = ["agent-1", "agent-2", "agent-3"]
        
        conversation_id = await communication_interface.start_conversation(
            participants=participants,
            subject="Project Planning",
            initial_message={"agenda": "Sprint planning"},
        )
        
        assert conversation_id in communication_interface.conversations
        conversation = communication_interface.conversations[conversation_id]
        
        assert conversation.subject == "Project Planning"
        assert "test-agent" in conversation.participants
        assert all(p in conversation.participants for p in participants)

    @pytest.mark.asyncio
    async def test_message_handler_registration(self, communication_interface):
        """Test message handler registration."""
        handler_called = False
        
        async def test_handler(message):
            nonlocal handler_called
            handler_called = True
        
        communication_interface.register_handler(MessageType.NOTIFICATION, test_handler)
        
        # Verify handler is registered
        assert MessageType.NOTIFICATION in communication_interface.message_handlers
        assert test_handler in communication_interface.message_handlers[MessageType.NOTIFICATION]

    @pytest.mark.asyncio
    async def test_incoming_message_handling(self, communication_interface, sample_message):
        """Test handling of incoming messages."""
        await communication_interface.initialize()
        
        handler_called = False
        received_message = None
        
        async def test_handler(message):
            nonlocal handler_called, received_message
            handler_called = True
            received_message = message
        
        communication_interface.register_handler(MessageType.REQUEST, test_handler)
        
        # Create mock AgentMessage
        from core.messaging.queue import AgentMessage
        agent_message = AgentMessage(
            envelope={"sender_id": "sender-agent"},
            payload=sample_message.model_dump(),
            metadata={},
        )
        
        await communication_interface.handle_incoming_message(agent_message)
        
        assert handler_called
        assert received_message.subject == "Test Request"
        assert communication_interface.stats["messages_received"] == 1

    @pytest.mark.asyncio
    async def test_response_handling(self, communication_interface):
        """Test handling of response messages."""
        await communication_interface.initialize()
        
        # Create a pending request
        future = asyncio.Future()
        pending_request = PendingRequest(
            request_id="req-123",
            sender_id="test-agent",
            recipient_id="target-agent",
            message_type=MessageType.REQUEST,
            timeout_at=datetime.utcnow() + timedelta(seconds=30),
            future=future,
        )
        communication_interface.pending_requests["req-123"] = pending_request
        
        # Create response message
        response_message = AgentCommunicationMessage(
            message_type=MessageType.RESPONSE,
            sender_id="target-agent",
            recipient_id="test-agent",
            parent_message_id="req-123",
            subject="Response",
            content={"success": True, "data": {"result": "completed"}},
        )
        
        # Handle the response
        await communication_interface._handle_response(response_message)
        
        # Verify future was resolved
        assert future.done()
        result = future.result()
        assert result["success"] is True
        assert result["data"]["result"] == "completed"

    @pytest.mark.asyncio
    async def test_cleanup_expired_requests(self, communication_interface):
        """Test cleanup of expired requests."""
        await communication_interface.initialize()
        
        # Create expired request
        expired_future = asyncio.Future()
        expired_request = PendingRequest(
            request_id="expired-123",
            sender_id="test-agent",
            recipient_id="target-agent",
            message_type=MessageType.REQUEST,
            timeout_at=datetime.utcnow() - timedelta(minutes=1),  # Already expired
            future=expired_future,
        )
        communication_interface.pending_requests["expired-123"] = expired_request
        
        # Create active request
        active_future = asyncio.Future()
        active_request = PendingRequest(
            request_id="active-456",
            sender_id="test-agent",
            recipient_id="target-agent",
            message_type=MessageType.REQUEST,
            timeout_at=datetime.utcnow() + timedelta(minutes=1),  # Still active
            future=active_future,
        )
        communication_interface.pending_requests["active-456"] = active_request
        
        # Run cleanup
        await communication_interface._cleanup_expired_requests()
        
        # Verify expired request was removed and cancelled
        assert "expired-123" not in communication_interface.pending_requests
        assert expired_future.cancelled()
        
        # Verify active request remains
        assert "active-456" in communication_interface.pending_requests
        assert not active_future.cancelled()

    @pytest.mark.asyncio
    async def test_conversation_cleanup(self, communication_interface):
        """Test cleanup of old conversations."""
        await communication_interface.initialize()
        
        # Create old inactive conversation
        old_conversation = ConversationThread(
            id="old-conv",
            participants=["test-agent", "other-agent"],
            subject="Old Discussion",
            last_activity=datetime.utcnow() - timedelta(days=2),
            is_active=False,
        )
        communication_interface.conversations["old-conv"] = old_conversation
        
        # Create recent conversation
        recent_conversation = ConversationThread(
            id="recent-conv",
            participants=["test-agent", "other-agent"],
            subject="Recent Discussion",
            last_activity=datetime.utcnow() - timedelta(hours=1),
            is_active=False,
        )
        communication_interface.conversations["recent-conv"] = recent_conversation
        
        # Run cleanup
        await communication_interface._cleanup_old_conversations()
        
        # Verify old conversation was removed
        assert "old-conv" not in communication_interface.conversations
        
        # Verify recent conversation remains
        assert "recent-conv" in communication_interface.conversations

    @pytest.mark.asyncio
    async def test_communication_stats(self, communication_interface):
        """Test communication statistics tracking."""
        await communication_interface.initialize()
        
        # Simulate some activity
        communication_interface.stats["messages_sent"] = 5
        communication_interface.stats["messages_received"] = 3
        communication_interface.stats["requests_sent"] = 2
        communication_interface.stats["responses_received"] = 2
        
        # Add pending request and conversation
        pending_request = PendingRequest(
            request_id="pending-123",
            sender_id="test-agent",
            recipient_id="target-agent",
            message_type=MessageType.REQUEST,
            timeout_at=datetime.utcnow() + timedelta(minutes=1),
        )
        communication_interface.pending_requests["pending-123"] = pending_request
        
        conversation = ConversationThread(
            id="active-conv",
            participants=["test-agent", "other-agent"],
            subject="Active Discussion",
            is_active=True,
        )
        communication_interface.conversations["active-conv"] = conversation
        
        # Get stats
        stats = communication_interface.get_stats()
        
        assert stats["messages_sent"] == 5
        assert stats["messages_received"] == 3
        assert stats["requests_sent"] == 2
        assert stats["responses_received"] == 2
        assert stats["pending_requests"] == 1
        assert stats["active_conversations"] == 1
        assert stats["total_conversations"] == 1

    @pytest.mark.asyncio
    async def test_shutdown(self, communication_interface):
        """Test communication interface shutdown."""
        await communication_interface.initialize()
        
        # Add pending request
        future = asyncio.Future()
        pending_request = PendingRequest(
            request_id="pending-123",
            sender_id="test-agent",
            recipient_id="target-agent",
            message_type=MessageType.REQUEST,
            timeout_at=datetime.utcnow() + timedelta(minutes=1),
            future=future,
        )
        communication_interface.pending_requests["pending-123"] = pending_request
        
        # Shutdown
        await communication_interface.shutdown()
        
        # Verify pending request was cancelled
        assert future.cancelled()
        assert communication_interface._shutdown_event.is_set()


class TestAgentMessageRouter:
    """Test cases for AgentMessageRouter."""

    @pytest.fixture
    def mock_registry(self):
        """Create mock agent registry."""
        registry = AsyncMock()
        return registry

    @pytest.fixture
    def mock_discovery(self):
        """Create mock agent discovery."""
        discovery = AsyncMock()
        return discovery

    @pytest.fixture
    def mock_message_queue(self):
        """Create mock message queue."""
        return AsyncMock()

    @pytest.fixture
    def agent_router(self, mock_registry, mock_discovery, mock_message_queue):
        """Create agent message router."""
        return AgentMessageRouter(mock_registry, mock_discovery, mock_message_queue)

    @pytest.mark.asyncio
    async def test_direct_message_routing(self, agent_router, mock_registry):
        """Test direct message routing to specific agent."""
        # Mock healthy agent
        from agents.base.types import AgentHealth, AgentState
        
        mock_health = AgentHealth(
            agent_id="target-agent",
            state=AgentState.IDLE,
            is_healthy=True,
            health_score=0.9,
        )
        mock_registry.get_agent_health.return_value = mock_health
        
        decision = await agent_router.route_message(
            routing_key="agent.target-agent",
            payload={"message": "test"},
            sender_id="sender-agent",
            recipient_id="target-agent",
        )
        
        assert decision.success
        assert decision.routing_key == "agent.target-agent"
        assert decision.queue_name == "agent.target-agent.inbox"
        assert "target-agent" in decision.reason

    @pytest.mark.asyncio
    async def test_broadcast_routing(self, agent_router, mock_registry):
        """Test broadcast message routing."""
        # Mock available agents
        mock_registry.list_agents.return_value = ["agent-1", "agent-2", "agent-3"]
        
        decision = await agent_router.route_message(
            routing_key="agent.broadcast",
            payload={"announcement": "system update"},
            sender_id="sender-agent",
            recipient_id="*",
        )
        
        assert decision.success
        assert decision.exchange == "agents.broadcast"
        assert "3 agents" in decision.reason

    @pytest.mark.asyncio
    async def test_task_delegation_routing(self, agent_router, mock_discovery):
        """Test task delegation routing."""
        # Mock agent discovery
        mock_discovery.find_agent_for_task.return_value = "backend-agent"
        
        decision = await agent_router.route_message(
            routing_key="task.delegate",
            payload={
                "task_type": "code_generation",
                "complexity": 5,
                "description": "Generate API endpoints",
            },
            sender_id="sender-agent",
            message_type="task_delegation",
        )
        
        assert decision.success
        assert decision.routing_key == "agent.backend-agent"
        assert decision.queue_name == "agent.backend-agent.inbox"
        assert "backend-agent" in decision.reason