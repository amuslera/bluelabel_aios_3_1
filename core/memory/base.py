"""
Memory system base interfaces for AIOSv3 platform.

Provides memory management for agent conversations, context tracking,
and knowledge persistence across agent interactions.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union, Dict, List

from pydantic import BaseModel, Field


class MemoryType(Enum):
    """Types of memory storage."""
    
    CONVERSATION = "conversation"  # Chat history and context
    KNOWLEDGE = "knowledge"  # Long-term facts and information
    PROCEDURAL = "procedural"  # How-to knowledge and procedures
    EPISODIC = "episodic"  # Specific events and experiences
    SEMANTIC = "semantic"  # General concepts and relationships


class MemoryPriority(Enum):
    """Memory importance levels for retention policies."""
    
    CRITICAL = "critical"  # Must retain indefinitely
    HIGH = "high"  # Retain for extended periods
    MEDIUM = "medium"  # Standard retention
    LOW = "low"  # Short-term retention
    EPHEMERAL = "ephemeral"  # Delete after session


class MemoryScope(Enum):
    """Scope of memory accessibility."""
    
    GLOBAL = "global"  # Accessible to all agents
    AGENT_TYPE = "agent_type"  # Accessible to agents of same type
    AGENT_INSTANCE = "agent_instance"  # Private to specific agent
    SESSION = "session"  # Limited to current session
    TEAM = "team"  # Shared within agent team


class MemoryEntry(BaseModel):
    """Individual memory entry."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    memory_type: MemoryType
    priority: MemoryPriority = MemoryPriority.MEDIUM
    scope: MemoryScope = MemoryScope.AGENT_INSTANCE
    
    # Context information
    agent_id: str
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    task_id: Optional[str] = None
    
    # Temporal information
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    accessed_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    # Semantic information
    keywords: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    embedding: Optional[List[float]] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source: Optional[str] = None
    confidence: float = 1.0  # 0.0-1.0 confidence in memory accuracy
    
    def update_access_time(self) -> None:
        """Update the last accessed timestamp."""
        self.accessed_at = datetime.utcnow()


class ConversationContext(BaseModel):
    """Context for a conversation thread."""
    
    conversation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    session_id: str
    
    # Message history
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    total_messages: int = 0
    
    # Token management
    total_tokens: int = 0
    max_context_tokens: int = 32768
    compression_threshold: int = 24576  # 75% of max
    
    # Context state
    current_topic: Optional[str] = None
    active_tasks: List[str] = Field(default_factory=list)
    mentioned_entities: List[str] = Field(default_factory=list)
    
    # Temporal tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    
    # Memory links
    related_memories: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    
    def add_message(self, message: Dict[str, Any], tokens: int = 0) -> None:
        """Add a message to the conversation."""
        self.messages.append(message)
        self.total_messages += 1
        self.total_tokens += tokens
        self.last_activity = datetime.utcnow()
    
    def needs_compression(self) -> bool:
        """Check if conversation needs token compression."""
        return self.total_tokens > self.compression_threshold


class MemoryQuery(BaseModel):
    """Query for retrieving memories."""
    
    # Content filtering
    query_text: Optional[str] = None
    keywords: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    
    # Type and scope filtering
    memory_types: Optional[List[MemoryType]] = None
    scopes: Optional[List[MemoryScope]] = None
    priorities: Optional[List[MemoryPriority]] = None
    
    # Context filtering
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    task_id: Optional[str] = None
    
    # Temporal filtering
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    accessed_after: Optional[datetime] = None
    
    # Semantic search
    use_semantic_search: bool = True
    similarity_threshold: float = 0.7
    
    # Result configuration
    limit: int = 10
    offset: int = 0
    include_expired: bool = False


class MemorySearchResult(BaseModel):
    """Result from memory search."""
    
    entry: MemoryEntry
    relevance_score: float = 0.0
    similarity_score: Optional[float] = None
    match_reasons: List[str] = Field(default_factory=list)


class MemoryStats(BaseModel):
    """Statistics about memory usage."""
    
    total_entries: int = 0
    entries_by_type: Dict[str, int] = Field(default_factory=dict)
    entries_by_scope: Dict[str, int] = Field(default_factory=dict)
    entries_by_priority: Dict[str, int] = Field(default_factory=dict)
    
    # Storage metrics
    total_size_bytes: int = 0
    embedding_count: int = 0
    expired_entries: int = 0
    
    # Activity metrics
    daily_accesses: int = 0
    weekly_accesses: int = 0
    most_accessed_entries: List[str] = Field(default_factory=list)
    
    # Performance metrics
    avg_query_time_ms: float = 0.0
    cache_hit_rate: float = 0.0


class MemoryBackend(ABC):
    """Abstract base class for memory storage backends."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the memory backend."""
        self.config = config
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the backend connection and resources."""
        pass
    
    @abstractmethod
    async def store_memory(self, entry: MemoryEntry) -> str:
        """Store a memory entry and return its ID."""
        pass
    
    @abstractmethod
    async def get_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve a specific memory by ID."""
        pass
    
    @abstractmethod
    async def update_memory(self, memory_id: str, entry: MemoryEntry) -> bool:
        """Update an existing memory entry."""
        pass
    
    @abstractmethod
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory entry."""
        pass
    
    @abstractmethod
    async def search_memories(self, query: MemoryQuery) -> List[MemorySearchResult]:
        """Search for memories matching the query."""
        pass
    
    @abstractmethod
    async def store_conversation(self, context: ConversationContext) -> str:
        """Store conversation context."""
        pass
    
    @abstractmethod
    async def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """Retrieve conversation context."""
        pass
    
    @abstractmethod
    async def update_conversation(self, context: ConversationContext) -> bool:
        """Update conversation context."""
        pass
    
    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Remove expired memories and return count of deleted entries."""
        pass
    
    @abstractmethod
    async def get_stats(self) -> MemoryStats:
        """Get memory usage statistics."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the backend and cleanup resources."""
        pass


class EmbeddingProvider(ABC):
    """Abstract base class for text embedding providers."""
    
    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text."""
        pass
    
    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for multiple texts."""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get the dimension of embedding vectors."""
        pass


class MemoryManager(ABC):
    """Abstract base class for memory management."""
    
    def __init__(self, backend: MemoryBackend, embedding_provider: Optional[EmbeddingProvider] = None):
        """Initialize the memory manager."""
        self.backend = backend
        self.embedding_provider = embedding_provider
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the memory manager and its backend."""
        pass
    
    @abstractmethod
    async def store(
        self,
        content: str,
        memory_type: MemoryType,
        agent_id: str,
        priority: MemoryPriority = MemoryPriority.MEDIUM,
        scope: MemoryScope = MemoryScope.AGENT_INSTANCE,
        **kwargs
    ) -> str:
        """Store a new memory entry."""
        pass
    
    @abstractmethod
    async def retrieve(
        self,
        query: Union[str, MemoryQuery],
        agent_id: str,
        limit: int = 10
    ) -> List[MemorySearchResult]:
        """Retrieve memories matching the query."""
        pass
    
    @abstractmethod
    async def update(self, memory_id: str, **updates) -> bool:
        """Update a memory entry."""
        pass
    
    @abstractmethod
    async def forget(self, memory_id: str) -> bool:
        """Delete a memory entry."""
        pass
    
    @abstractmethod
    async def get_conversation_context(
        self,
        conversation_id: str,
        agent_id: str
    ) -> Optional[ConversationContext]:
        """Get conversation context for managing chat history."""
        pass
    
    @abstractmethod
    async def update_conversation_context(
        self,
        context: ConversationContext
    ) -> bool:
        """Update conversation context."""
        pass
    
    @abstractmethod
    async def compress_conversation(
        self,
        conversation_id: str,
        agent_id: str
    ) -> bool:
        """Compress conversation history when context becomes too long."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> int:
        """Clean up expired memories."""
        pass
    
    @abstractmethod
    async def get_statistics(self) -> MemoryStats:
        """Get memory usage statistics."""
        pass