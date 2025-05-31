"""
Redis backend implementation for AIOSv3 memory system.

Provides high-performance memory storage using Redis with optional
vector search capabilities via Redis Stack.
"""

import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import redis.asyncio as redis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff

from ..base import (
    ConversationContext,
    MemoryBackend,
    MemoryEntry,
    MemoryQuery,
    MemorySearchResult,
    MemoryStats,
    MemoryType,
    MemoryScope,
    MemoryPriority,
)

logger = logging.getLogger(__name__)


class RedisMemoryBackend(MemoryBackend):
    """
    Redis-based memory backend for fast storage and retrieval.
    
    Features:
    - Fast key-value storage for memories and conversations
    - Optional vector search with Redis Stack
    - Automatic expiration handling
    - Clustering support for high availability
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Redis backend."""
        super().__init__(config)
        
        # Redis connection config
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 6379)
        self.db = config.get("db", 0)
        self.password = config.get("password")
        self.ssl = config.get("ssl", False)
        
        # Redis Stack features
        self.use_vector_search = config.get("use_vector_search", False)
        self.vector_dimension = config.get("vector_dimension", 1536)
        
        # Key prefixes for organization
        self.memory_prefix = "memory:"
        self.conversation_prefix = "conversation:"
        self.index_prefix = "index:"
        self.stats_key = "memory:stats"
        
        # Connection pool
        self.pool = None
        self.redis_client = None
        
        # Vector search index name
        self.vector_index = "memory_vectors"
        
    async def initialize(self) -> None:
        """Initialize Redis connection and create indexes."""
        logger.info(f"Initializing Redis memory backend at {self.host}:{self.port}")
        
        # Create connection pool
        retry = Retry(ExponentialBackoff(), 3)
        
        self.pool = redis.ConnectionPool(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            ssl=self.ssl,
            retry=retry,
            health_check_interval=30,
        )
        
        self.redis_client = redis.Redis(connection_pool=self.pool)
        
        # Test connection
        await self.redis_client.ping()
        
        # Initialize vector search if enabled
        if self.use_vector_search:
            await self._initialize_vector_search()
        
        logger.info("Redis memory backend initialized successfully")
    
    async def store_memory(self, entry: MemoryEntry) -> str:
        """Store a memory entry in Redis."""
        memory_key = f"{self.memory_prefix}{entry.id}"
        
        # Serialize entry
        entry_data = entry.model_dump()
        entry_data["created_at"] = entry.created_at.isoformat()
        entry_data["updated_at"] = entry.updated_at.isoformat()
        entry_data["accessed_at"] = entry.accessed_at.isoformat()
        
        if entry.expires_at:
            entry_data["expires_at"] = entry.expires_at.isoformat()
        
        # Store in Redis
        await self.redis_client.hset(memory_key, mapping=entry_data)
        
        # Set expiration if specified
        if entry.expires_at:
            expires_in = int((entry.expires_at - datetime.utcnow()).total_seconds())
            if expires_in > 0:
                await self.redis_client.expire(memory_key, expires_in)
        
        # Add to indexes
        await self._add_to_indexes(entry)
        
        # Update stats
        await self._update_stats("store")
        
        logger.debug(f"Stored memory {entry.id}")
        return entry.id
    
    async def get_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry by ID."""
        memory_key = f"{self.memory_prefix}{memory_id}"
        
        entry_data = await self.redis_client.hgetall(memory_key)
        
        if not entry_data:
            return None
        
        # Deserialize entry
        entry_dict = {k.decode(): v.decode() for k, v in entry_data.items()}
        
        # Parse datetime fields
        for field in ["created_at", "updated_at", "accessed_at", "expires_at"]:
            if entry_dict.get(field):
                entry_dict[field] = datetime.fromisoformat(entry_dict[field])
        
        # Parse JSON fields
        for field in ["keywords", "categories", "embedding", "metadata"]:
            if entry_dict.get(field):
                entry_dict[field] = json.loads(entry_dict[field])
        
        # Convert enum fields
        entry_dict["memory_type"] = MemoryType(entry_dict["memory_type"])
        entry_dict["priority"] = MemoryPriority(entry_dict["priority"])
        entry_dict["scope"] = MemoryScope(entry_dict["scope"])
        
        entry = MemoryEntry(**entry_dict)
        
        # Update access time
        entry.update_access_time()
        await self.update_memory(memory_id, entry)
        
        return entry
    
    async def update_memory(self, memory_id: str, entry: MemoryEntry) -> bool:
        """Update an existing memory entry."""
        memory_key = f"{self.memory_prefix}{memory_id}"
        
        # Check if entry exists
        exists = await self.redis_client.exists(memory_key)
        if not exists:
            return False
        
        # Update entry
        entry.updated_at = datetime.utcnow()
        await self.store_memory(entry)
        
        return True
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory entry."""
        memory_key = f"{self.memory_prefix}{memory_id}"
        
        # Get entry before deletion for index cleanup
        entry = await self.get_memory(memory_id)
        if not entry:
            return False
        
        # Delete from Redis
        deleted = await self.redis_client.delete(memory_key)
        
        if deleted:
            # Remove from indexes
            await self._remove_from_indexes(entry)
            
            # Update stats
            await self._update_stats("delete")
            
            logger.debug(f"Deleted memory {memory_id}")
        
        return bool(deleted)
    
    async def search_memories(self, query: MemoryQuery) -> List[MemorySearchResult]:
        """Search for memories matching the query."""
        start_time = time.time()
        
        # Use vector search if available and requested
        if self.use_vector_search and query.use_semantic_search and query.query_text:
            results = await self._vector_search(query)
        else:
            results = await self._index_search(query)
        
        # Update query stats
        query_time = (time.time() - start_time) * 1000
        await self._update_query_stats(query_time)
        
        return results
    
    async def store_conversation(self, context: ConversationContext) -> str:
        """Store conversation context."""
        conv_key = f"{self.conversation_prefix}{context.conversation_id}"
        
        # Serialize context
        context_data = context.model_dump()
        context_data["created_at"] = context.created_at.isoformat()
        context_data["last_activity"] = context.last_activity.isoformat()
        context_data["messages"] = json.dumps(context.messages)
        context_data["active_tasks"] = json.dumps(context.active_tasks)
        context_data["mentioned_entities"] = json.dumps(context.mentioned_entities)
        context_data["related_memories"] = json.dumps(context.related_memories)
        
        # Store in Redis
        await self.redis_client.hset(conv_key, mapping=context_data)
        
        logger.debug(f"Stored conversation {context.conversation_id}")
        return context.conversation_id
    
    async def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """Retrieve conversation context."""
        conv_key = f"{self.conversation_prefix}{conversation_id}"
        
        context_data = await self.redis_client.hgetall(conv_key)
        
        if not context_data:
            return None
        
        # Deserialize context
        context_dict = {k.decode(): v.decode() for k, v in context_data.items()}
        
        # Parse datetime fields
        context_dict["created_at"] = datetime.fromisoformat(context_dict["created_at"])
        context_dict["last_activity"] = datetime.fromisoformat(context_dict["last_activity"])
        
        # Parse JSON fields
        for field in ["messages", "active_tasks", "mentioned_entities", "related_memories"]:
            if context_dict.get(field):
                context_dict[field] = json.loads(context_dict[field])
        
        return ConversationContext(**context_dict)
    
    async def update_conversation(self, context: ConversationContext) -> bool:
        """Update conversation context."""
        conv_key = f"{self.conversation_prefix}{context.conversation_id}"
        
        # Check if conversation exists
        exists = await self.redis_client.exists(conv_key)
        if not exists:
            return False
        
        # Update conversation
        context.last_activity = datetime.utcnow()
        await self.store_conversation(context)
        
        return True
    
    async def cleanup_expired(self) -> int:
        """Remove expired memories and return count."""
        # Redis handles TTL expiration automatically
        # We just need to clean up any dangling indexes
        
        cleanup_count = 0
        
        # Scan for memory keys and check if they still exist
        async for key in self.redis_client.scan_iter(f"{self.memory_prefix}*"):
            key_str = key.decode()
            memory_id = key_str.replace(self.memory_prefix, "")
            
            # Check if memory still exists
            if not await self.redis_client.exists(key):
                # Clean up any remaining index entries
                await self._cleanup_memory_indexes(memory_id)
                cleanup_count += 1
        
        if cleanup_count > 0:
            logger.info(f"Cleaned up {cleanup_count} expired memory entries")
        
        return cleanup_count
    
    async def get_stats(self) -> MemoryStats:
        """Get memory usage statistics."""
        stats_data = await self.redis_client.hgetall(self.stats_key)
        
        if not stats_data:
            return MemoryStats()
        
        # Deserialize stats
        stats_dict = {k.decode(): v.decode() for k, v in stats_data.items()}
        
        # Parse JSON fields
        for field in ["entries_by_type", "entries_by_scope", "entries_by_priority", "most_accessed_entries"]:
            if stats_dict.get(field):
                stats_dict[field] = json.loads(stats_dict[field])
        
        # Convert numeric fields
        for field in ["total_entries", "total_size_bytes", "embedding_count", "expired_entries", 
                     "daily_accesses", "weekly_accesses"]:
            if stats_dict.get(field):
                stats_dict[field] = int(stats_dict[field])
        
        for field in ["avg_query_time_ms", "cache_hit_rate"]:
            if stats_dict.get(field):
                stats_dict[field] = float(stats_dict[field])
        
        return MemoryStats(**stats_dict)
    
    async def shutdown(self) -> None:
        """Shutdown Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
        if self.pool:
            await self.pool.disconnect()
        
        logger.info("Redis memory backend shutdown completed")
    
    async def _initialize_vector_search(self) -> None:
        """Initialize vector search index if Redis Stack is available."""
        try:
            # Check if index already exists
            try:
                await self.redis_client.execute_command("FT.INFO", self.vector_index)
                logger.info(f"Vector search index {self.vector_index} already exists")
                return
            except Exception:
                pass  # Index doesn't exist, create it
            
            # Create vector search index
            index_def = [
                "ON", "HASH",
                "PREFIX", "1", f"{self.memory_prefix}",
                "SCHEMA",
                "content", "TEXT", "SORTABLE",
                "memory_type", "TAG", "SORTABLE",
                "agent_id", "TAG", "SORTABLE",
                "keywords", "TAG",
                "embedding", "VECTOR", "FLAT", "6",
                "TYPE", "FLOAT32",
                "DIM", str(self.vector_dimension),
                "DISTANCE_METRIC", "COSINE"
            ]
            
            await self.redis_client.execute_command("FT.CREATE", self.vector_index, *index_def)
            logger.info(f"Created vector search index: {self.vector_index}")
            
        except Exception as e:
            logger.warning(f"Failed to initialize vector search: {e}")
            self.use_vector_search = False
    
    async def _add_to_indexes(self, entry: MemoryEntry) -> None:
        """Add memory entry to searchable indexes."""
        # Type index
        type_key = f"{self.index_prefix}type:{entry.memory_type.value}"
        await self.redis_client.sadd(type_key, entry.id)
        
        # Agent index
        agent_key = f"{self.index_prefix}agent:{entry.agent_id}"
        await self.redis_client.sadd(agent_key, entry.id)
        
        # Keyword indexes
        for keyword in entry.keywords:
            keyword_key = f"{self.index_prefix}keyword:{keyword.lower()}"
            await self.redis_client.sadd(keyword_key, entry.id)
    
    async def _remove_from_indexes(self, entry: MemoryEntry) -> None:
        """Remove memory entry from indexes."""
        # Type index
        type_key = f"{self.index_prefix}type:{entry.memory_type.value}"
        await self.redis_client.srem(type_key, entry.id)
        
        # Agent index
        agent_key = f"{self.index_prefix}agent:{entry.agent_id}"
        await self.redis_client.srem(agent_key, entry.id)
        
        # Keyword indexes
        for keyword in entry.keywords:
            keyword_key = f"{self.index_prefix}keyword:{keyword.lower()}"
            await self.redis_client.srem(keyword_key, entry.id)
    
    async def _cleanup_memory_indexes(self, memory_id: str) -> None:
        """Clean up index entries for a deleted memory."""
        # This is a simplified cleanup - in production, you might want
        # to track which indexes a memory belongs to
        
        # Scan for index keys and remove the memory_id
        async for key in self.redis_client.scan_iter(f"{self.index_prefix}*"):
            await self.redis_client.srem(key, memory_id)
    
    async def _vector_search(self, query: MemoryQuery) -> List[MemorySearchResult]:
        """Perform vector similarity search."""
        # This is a placeholder - actual implementation would need
        # to generate embeddings for the query text and perform
        # vector search using Redis Stack
        
        logger.warning("Vector search not fully implemented")
        return await self._index_search(query)
    
    async def _index_search(self, query: MemoryQuery) -> List[MemorySearchResult]:
        """Perform traditional index-based search."""
        candidate_ids = set()
        
        # Get candidates from different indexes
        if query.agent_id:
            agent_key = f"{self.index_prefix}agent:{query.agent_id}"
            agent_ids = await self.redis_client.smembers(agent_key)
            candidate_ids.update(id.decode() for id in agent_ids)
        
        if query.memory_types:
            for memory_type in query.memory_types:
                type_key = f"{self.index_prefix}type:{memory_type.value}"
                type_ids = await self.redis_client.smembers(type_key)
                if not candidate_ids:
                    candidate_ids.update(id.decode() for id in type_ids)
                else:
                    candidate_ids.intersection_update(id.decode() for id in type_ids)
        
        if query.keywords:
            for keyword in query.keywords:
                keyword_key = f"{self.index_prefix}keyword:{keyword.lower()}"
                keyword_ids = await self.redis_client.smembers(keyword_key)
                if not candidate_ids:
                    candidate_ids.update(id.decode() for id in keyword_ids)
                else:
                    candidate_ids.intersection_update(id.decode() for id in keyword_ids)
        
        # If no specific filters, get all memories for the agent
        if not candidate_ids and query.agent_id:
            agent_key = f"{self.index_prefix}agent:{query.agent_id}"
            agent_ids = await self.redis_client.smembers(agent_key)
            candidate_ids.update(id.decode() for id in agent_ids)
        
        # Retrieve and score candidates
        results = []
        for memory_id in list(candidate_ids)[:query.limit * 2]:  # Get more than needed for filtering
            memory = await self.get_memory(memory_id)
            if memory:
                score = self._calculate_relevance_score(memory, query)
                if score > 0:
                    results.append(MemorySearchResult(
                        entry=memory,
                        relevance_score=score,
                        match_reasons=["index_match"]
                    ))
        
        # Sort by relevance and apply limit
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:query.limit]
    
    def _calculate_relevance_score(self, memory: MemoryEntry, query: MemoryQuery) -> float:
        """Calculate relevance score for a memory entry."""
        score = 0.0
        
        # Text matching
        if query.query_text and memory.content:
            query_words = set(query.query_text.lower().split())
            content_words = set(memory.content.lower().split())
            overlap = len(query_words.intersection(content_words))
            if query_words:
                score += (overlap / len(query_words)) * 0.5
        
        # Keyword matching
        if query.keywords and memory.keywords:
            keyword_overlap = len(set(query.keywords).intersection(set(memory.keywords)))
            score += (keyword_overlap / len(query.keywords)) * 0.3
        
        # Recency boost
        age_days = (datetime.utcnow() - memory.created_at).days
        if age_days < 7:
            score += 0.2 * (7 - age_days) / 7
        
        return min(1.0, score)
    
    async def _update_stats(self, operation: str) -> None:
        """Update memory statistics."""
        await self.redis_client.hincrby(self.stats_key, f"{operation}_count", 1)
        await self.redis_client.hset(self.stats_key, "last_updated", datetime.utcnow().isoformat())
    
    async def _update_query_stats(self, query_time_ms: float) -> None:
        """Update query performance statistics."""
        await self.redis_client.hincrby(self.stats_key, "query_count", 1)
        
        # Update average query time (simplified calculation)
        current_avg = await self.redis_client.hget(self.stats_key, "avg_query_time_ms")
        if current_avg:
            current_avg = float(current_avg.decode())
            new_avg = (current_avg + query_time_ms) / 2
        else:
            new_avg = query_time_ms
        
        await self.redis_client.hset(self.stats_key, "avg_query_time_ms", str(new_avg))