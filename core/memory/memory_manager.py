"""
Memory manager implementation for AIOSv3 platform.

Provides high-level memory management for agents including storage,
retrieval, context management, and intelligent compression.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from .base import (
    ConversationContext,
    EmbeddingProvider,
    MemoryBackend,
    MemoryEntry,
    MemoryManager,
    MemoryPriority,
    MemoryQuery,
    MemoryScope,
    MemorySearchResult,
    MemoryStats,
    MemoryType,
)
from .context_manager import ContextManager

logger = logging.getLogger(__name__)


class AIOSMemoryManager(MemoryManager):
    """
    Production memory manager for AIOSv3 platform.
    
    Features:
    - Multi-backend storage support
    - Intelligent context management
    - Automatic compression and cleanup
    - Vector similarity search
    - Memory prioritization and retention policies
    """
    
    def __init__(
        self,
        backend: MemoryBackend,
        embedding_provider: Optional[EmbeddingProvider] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the memory manager."""
        super().__init__(backend, embedding_provider)
        
        self.config = config or {}
        self.context_manager = ContextManager(self)
        
        # Memory retention policies
        self.retention_policies = {
            MemoryPriority.CRITICAL: None,  # Never expire
            MemoryPriority.HIGH: timedelta(days=365),  # 1 year
            MemoryPriority.MEDIUM: timedelta(days=90),  # 3 months
            MemoryPriority.LOW: timedelta(days=30),  # 1 month
            MemoryPriority.EPHEMERAL: timedelta(hours=24),  # 1 day
        }
        
        # Update retention policies from config
        if "retention_policies" in self.config:
            for priority, days in self.config["retention_policies"].items():
                if days is not None:
                    self.retention_policies[MemoryPriority(priority)] = timedelta(days=days)
                else:
                    self.retention_policies[MemoryPriority(priority)] = None
    
    async def initialize(self) -> None:
        """Initialize the memory manager and its backend."""
        logger.info("Initializing AIOS memory manager")
        
        await self.backend.initialize()
        
        # Start background cleanup task if configured
        cleanup_interval = self.config.get("cleanup_interval_hours", 24)
        if cleanup_interval > 0:
            logger.info(f"Memory cleanup will run every {cleanup_interval} hours")
        
        logger.info("AIOS memory manager initialized successfully")
    
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
        # Calculate expiration based on priority
        expires_at = None
        retention_period = self.retention_policies.get(priority)
        if retention_period:
            expires_at = datetime.utcnow() + retention_period
        
        # Extract metadata from kwargs
        session_id = kwargs.get("session_id")
        conversation_id = kwargs.get("conversation_id")
        task_id = kwargs.get("task_id")
        keywords = kwargs.get("keywords", [])
        categories = kwargs.get("categories", [])
        metadata = kwargs.get("metadata", {})
        source = kwargs.get("source")
        confidence = kwargs.get("confidence", 1.0)
        
        # Generate embedding if provider is available
        embedding = None
        if self.embedding_provider:
            try:
                embedding = await self.embedding_provider.generate_embedding(content)
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")
        
        # Create memory entry
        entry = MemoryEntry(
            content=content,
            memory_type=memory_type,
            priority=priority,
            scope=scope,
            agent_id=agent_id,
            session_id=session_id,
            conversation_id=conversation_id,
            task_id=task_id,
            expires_at=expires_at,
            keywords=keywords,
            categories=categories,
            embedding=embedding,
            metadata=metadata,
            source=source,
            confidence=confidence,
        )
        
        # Store in backend
        memory_id = await self.backend.store_memory(entry)
        
        logger.debug(
            f"Stored {memory_type.value} memory for agent {agent_id}: {memory_id}"
        )
        
        return memory_id
    
    async def retrieve(
        self,
        query: Union[str, MemoryQuery],
        agent_id: str,
        limit: int = 10
    ) -> List[MemorySearchResult]:
        """Retrieve memories matching the query."""
        # Convert string query to MemoryQuery
        if isinstance(query, str):
            memory_query = MemoryQuery(
                query_text=query,
                agent_id=agent_id,
                limit=limit,
                use_semantic_search=bool(self.embedding_provider)
            )
        else:
            memory_query = query
            memory_query.agent_id = agent_id
            memory_query.limit = limit
        
        # Search memories
        results = await self.backend.search_memories(memory_query)
        
        logger.debug(
            f"Retrieved {len(results)} memories for agent {agent_id}"
        )
        
        return results
    
    async def update(self, memory_id: str, **updates) -> bool:
        """Update a memory entry."""
        # Get existing memory
        memory = await self.backend.get_memory(memory_id)
        if not memory:
            return False
        
        # Apply updates
        for field, value in updates.items():
            if hasattr(memory, field):
                setattr(memory, field, value)
        
        # Regenerate embedding if content changed and provider is available
        if "content" in updates and self.embedding_provider:
            try:
                memory.embedding = await self.embedding_provider.generate_embedding(
                    memory.content
                )
            except Exception as e:
                logger.warning(f"Failed to update embedding: {e}")
        
        # Update in backend
        return await self.backend.update_memory(memory_id, memory)
    
    async def forget(self, memory_id: str) -> bool:
        """Delete a memory entry."""
        success = await self.backend.delete_memory(memory_id)
        
        if success:
            logger.debug(f"Deleted memory: {memory_id}")
        
        return success
    
    async def get_conversation_context(
        self,
        conversation_id: str,
        agent_id: str
    ) -> Optional[ConversationContext]:
        """Get conversation context for managing chat history."""
        return await self.context_manager.get_context(agent_id, conversation_id)
    
    async def update_conversation_context(
        self,
        context: ConversationContext
    ) -> bool:
        """Update conversation context."""
        return await self.backend.update_conversation(context)
    
    async def compress_conversation(
        self,
        conversation_id: str,
        agent_id: str
    ) -> bool:
        """Compress conversation history when context becomes too long."""
        try:
            summary = await self.context_manager.compress_context(
                agent_id, conversation_id
            )
            
            logger.info(
                f"Compressed conversation {conversation_id} for agent {agent_id}: {summary}"
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to compress conversation: {e}")
            return False
    
    async def add_conversation_message(
        self,
        agent_id: str,
        conversation_id: str,
        message: Dict[str, Any],
        auto_compress: bool = True
    ) -> bool:
        """Add a message to conversation context."""
        try:
            needs_compression, summary = await self.context_manager.add_message(
                agent_id, conversation_id, message, auto_compress
            )
            
            if summary:
                logger.info(f"Auto-compressed conversation: {summary}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to add conversation message: {e}")
            return False
    
    async def get_relevant_context(
        self,
        agent_id: str,
        conversation_id: str,
        query: str,
        max_tokens: int = 8192
    ) -> List[Dict[str, Any]]:
        """Get relevant context messages for a specific query."""
        return await self.context_manager.get_relevant_context(
            agent_id, conversation_id, query, max_tokens
        )
    
    async def search_memories_by_type(
        self,
        memory_type: MemoryType,
        agent_id: str,
        limit: int = 10,
        **filters
    ) -> List[MemorySearchResult]:
        """Search memories by type with additional filters."""
        query = MemoryQuery(
            memory_types=[memory_type],
            agent_id=agent_id,
            limit=limit,
            **filters
        )
        
        return await self.backend.search_memories(query)
    
    async def get_recent_memories(
        self,
        agent_id: str,
        hours: int = 24,
        limit: int = 50
    ) -> List[MemorySearchResult]:
        """Get recent memories for an agent."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        query = MemoryQuery(
            agent_id=agent_id,
            created_after=cutoff_time,
            limit=limit,
            use_semantic_search=False  # Just get recent, don't need semantic search
        )
        
        return await self.backend.search_memories(query)
    
    async def get_memories_by_task(
        self,
        task_id: str,
        agent_id: str,
        limit: int = 20
    ) -> List[MemorySearchResult]:
        """Get all memories related to a specific task."""
        query = MemoryQuery(
            task_id=task_id,
            agent_id=agent_id,
            limit=limit,
            use_semantic_search=False
        )
        
        return await self.backend.search_memories(query)
    
    async def store_knowledge(
        self,
        content: str,
        agent_id: str,
        category: str,
        keywords: Optional[List[str]] = None,
        scope: MemoryScope = MemoryScope.AGENT_TYPE,
        **kwargs
    ) -> str:
        """Store knowledge that should be retained long-term."""
        return await self.store(
            content=content,
            memory_type=MemoryType.KNOWLEDGE,
            agent_id=agent_id,
            priority=MemoryPriority.HIGH,
            scope=scope,
            categories=[category],
            keywords=keywords or [],
            **kwargs
        )
    
    async def store_procedure(
        self,
        content: str,
        agent_id: str,
        procedure_name: str,
        keywords: Optional[List[str]] = None,
        scope: MemoryScope = MemoryScope.AGENT_TYPE,
        **kwargs
    ) -> str:
        """Store procedural knowledge (how-to information)."""
        return await self.store(
            content=content,
            memory_type=MemoryType.PROCEDURAL,
            agent_id=agent_id,
            priority=MemoryPriority.HIGH,
            scope=scope,
            categories=[procedure_name],
            keywords=keywords or [],
            **kwargs
        )
    
    async def cleanup(self) -> int:
        """Clean up expired memories and inactive contexts."""
        logger.info("Starting memory cleanup")
        
        # Cleanup expired memories
        expired_count = await self.backend.cleanup_expired()
        
        # Cleanup inactive conversation contexts
        inactive_count = await self.context_manager.cleanup_inactive_contexts(
            max_age_hours=self.config.get("context_max_age_hours", 24)
        )
        
        total_cleaned = expired_count + inactive_count
        
        if total_cleaned > 0:
            logger.info(f"Memory cleanup completed: {total_cleaned} items removed")
        
        return total_cleaned
    
    async def get_statistics(self) -> MemoryStats:
        """Get memory usage statistics."""
        return await self.backend.get_stats()
    
    async def export_memories(
        self,
        agent_id: str,
        memory_types: Optional[List[MemoryType]] = None,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Export memories for backup or analysis."""
        query = MemoryQuery(
            agent_id=agent_id,
            memory_types=memory_types,
            limit=10000,  # Large limit for export
            use_semantic_search=False
        )
        
        results = await self.backend.search_memories(query)
        
        export_data = {
            "agent_id": agent_id,
            "export_time": datetime.utcnow().isoformat(),
            "memory_count": len(results),
            "memories": []
        }
        
        for result in results:
            memory_data = result.entry.model_dump()
            # Convert datetime objects to strings for JSON serialization
            for field in ["created_at", "updated_at", "accessed_at", "expires_at"]:
                if memory_data.get(field):
                    memory_data[field] = memory_data[field].isoformat()
            
            export_data["memories"].append(memory_data)
        
        logger.info(f"Exported {len(results)} memories for agent {agent_id}")
        
        return export_data
    
    async def import_memories(
        self,
        import_data: Dict[str, Any],
        agent_id: Optional[str] = None
    ) -> int:
        """Import memories from backup data."""
        imported_count = 0
        
        target_agent_id = agent_id or import_data.get("agent_id")
        if not target_agent_id:
            raise ValueError("Agent ID must be provided for import")
        
        for memory_data in import_data.get("memories", []):
            try:
                # Reconstruct memory entry
                memory_data["agent_id"] = target_agent_id  # Override agent ID
                
                # Parse datetime fields
                for field in ["created_at", "updated_at", "accessed_at", "expires_at"]:
                    if memory_data.get(field):
                        memory_data[field] = datetime.fromisoformat(memory_data[field])
                
                # Convert enum fields
                memory_data["memory_type"] = MemoryType(memory_data["memory_type"])
                memory_data["priority"] = MemoryPriority(memory_data["priority"])
                memory_data["scope"] = MemoryScope(memory_data["scope"])
                
                entry = MemoryEntry(**memory_data)
                await self.backend.store_memory(entry)
                imported_count += 1
                
            except Exception as e:
                logger.warning(f"Failed to import memory: {e}")
                continue
        
        logger.info(f"Imported {imported_count} memories for agent {target_agent_id}")
        
        return imported_count
    
    async def shutdown(self) -> None:
        """Shutdown the memory manager."""
        logger.info("Shutting down AIOS memory manager")
        
        # Final cleanup
        await self.cleanup()
        
        # Shutdown backend
        await self.backend.shutdown()
        
        logger.info("AIOS memory manager shutdown completed")