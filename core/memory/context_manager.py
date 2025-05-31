"""
Context window management for AIOSv3 platform.

Manages conversation context, token limits, and intelligent compression
to maintain relevant history within model context windows.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel

from .base import (
    ConversationContext,
    MemoryEntry,
    MemoryManager,
    MemoryPriority,
    MemoryScope,
    MemoryType,
)

logger = logging.getLogger(__name__)


class ContextWindow(BaseModel):
    """Represents a managed context window for an agent."""
    
    agent_id: str
    conversation_id: str
    max_tokens: int = 32768
    
    # Current state
    messages: List[Dict[str, Any]] = []
    current_tokens: int = 0
    
    # Configuration
    reserve_tokens: int = 1024  # Reserve for response
    compression_ratio: float = 0.3  # Keep 30% of content after compression
    min_messages_to_keep: int = 5  # Always keep recent messages
    
    # Tracking
    last_compression: Optional[datetime] = None
    compression_count: int = 0
    
    def add_message(self, message: Dict[str, Any], token_count: int) -> bool:
        """Add a message to the context window."""
        self.messages.append(message)
        self.current_tokens += token_count
        
        return self.needs_compression()
    
    def needs_compression(self) -> bool:
        """Check if context window needs compression."""
        usable_tokens = self.max_tokens - self.reserve_tokens
        return self.current_tokens > usable_tokens
    
    def get_compression_target(self) -> int:
        """Get target token count after compression."""
        usable_tokens = self.max_tokens - self.reserve_tokens
        return int(usable_tokens * self.compression_ratio)


class MessageImportance(BaseModel):
    """Importance scoring for messages during compression."""
    
    message_index: int
    importance_score: float
    reasons: List[str]
    
    # Factors contributing to importance
    recency_score: float = 0.0
    relevance_score: float = 0.0
    information_density: float = 0.0
    task_relevance: float = 0.0
    user_initiated: bool = False


class ContextManager:
    """
    Manages conversation context windows and intelligent compression.
    
    Provides automatic context management to keep conversations within
    model token limits while preserving important information.
    """
    
    def __init__(self, memory_manager: MemoryManager):
        """Initialize context manager."""
        self.memory_manager = memory_manager
        self.active_contexts: Dict[str, ContextWindow] = {}
        
        # Token estimation (rough approximation: ~4 chars per token)
        self.chars_per_token = 4
        
    async def get_context(
        self,
        agent_id: str,
        conversation_id: str,
        max_tokens: int = 32768
    ) -> ContextWindow:
        """Get or create a context window for the conversation."""
        context_key = f"{agent_id}:{conversation_id}"
        
        if context_key not in self.active_contexts:
            # Load existing conversation or create new
            conversation = await self.memory_manager.get_conversation_context(
                conversation_id, agent_id
            )
            
            if conversation:
                context = ContextWindow(
                    agent_id=agent_id,
                    conversation_id=conversation_id,
                    max_tokens=max_tokens,
                    messages=conversation.messages.copy(),
                    current_tokens=conversation.total_tokens,
                )
            else:
                context = ContextWindow(
                    agent_id=agent_id,
                    conversation_id=conversation_id,
                    max_tokens=max_tokens,
                )
            
            self.active_contexts[context_key] = context
        
        return self.active_contexts[context_key]
    
    async def add_message(
        self,
        agent_id: str,
        conversation_id: str,
        message: Dict[str, Any],
        auto_compress: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Add a message to the context window.
        
        Returns:
            Tuple of (needs_compression, summary_if_compressed)
        """
        context = await self.get_context(agent_id, conversation_id)
        
        # Estimate token count for the message
        token_count = self._estimate_tokens(message)
        
        # Add message to context
        needs_compression = context.add_message(message, token_count)
        
        # Update conversation in memory
        await self._update_conversation_memory(context)
        
        # Compress if needed and auto_compress is enabled
        summary = None
        if needs_compression and auto_compress:
            summary = await self.compress_context(agent_id, conversation_id)
            
        return needs_compression, summary
    
    async def compress_context(
        self,
        agent_id: str,
        conversation_id: str,
        target_ratio: Optional[float] = None
    ) -> str:
        """
        Compress context window by summarizing and removing less important messages.
        
        Returns:
            Summary of compressed content
        """
        context_key = f"{agent_id}:{conversation_id}"
        context = self.active_contexts.get(context_key)
        
        if not context or len(context.messages) <= context.min_messages_to_keep:
            return "No compression needed"
        
        logger.info(
            f"Compressing context for {agent_id}:{conversation_id} "
            f"({context.current_tokens} tokens)"
        )
        
        # Calculate target token count
        compression_ratio = target_ratio or context.compression_ratio
        target_tokens = int(context.max_tokens * compression_ratio)
        
        # Score message importance
        message_scores = await self._score_message_importance(context)
        
        # Select messages to keep and compress
        kept_messages, compressed_content = await self._select_messages_for_compression(
            context, message_scores, target_tokens
        )
        
        # Create summary of compressed content
        summary = await self._create_compression_summary(compressed_content)
        
        # Update context with compressed messages
        context.messages = kept_messages
        context.current_tokens = sum(
            self._estimate_tokens(msg) for msg in kept_messages
        )
        context.last_compression = datetime.utcnow()
        context.compression_count += 1
        
        # Store summary as memory
        await self.memory_manager.store(
            content=f"Conversation summary: {summary}",
            memory_type=MemoryType.CONVERSATION,
            agent_id=agent_id,
            priority=MemoryPriority.HIGH,
            scope=MemoryScope.AGENT_INSTANCE,
            conversation_id=conversation_id,
            metadata={
                "type": "compression_summary",
                "original_tokens": context.current_tokens + sum(
                    self._estimate_tokens(msg) for msg in compressed_content
                ),
                "compressed_tokens": context.current_tokens,
                "compression_ratio": compression_ratio,
            }
        )
        
        # Update conversation in memory
        await self._update_conversation_memory(context)
        
        logger.info(
            f"Compressed context to {context.current_tokens} tokens "
            f"(ratio: {context.current_tokens / target_tokens:.2f})"
        )
        
        return summary
    
    async def get_relevant_context(
        self,
        agent_id: str,
        conversation_id: str,
        query: str,
        max_tokens: int = 8192
    ) -> List[Dict[str, Any]]:
        """
        Get relevant context messages for a specific query.
        
        Useful for retrieving focused context for specific tasks.
        """
        context = await self.get_context(agent_id, conversation_id)
        
        if not context.messages:
            return []
        
        # Score messages by relevance to query
        relevant_messages = []
        current_tokens = 0
        
        for message in reversed(context.messages):  # Start with most recent
            if current_tokens >= max_tokens:
                break
            
            relevance_score = self._calculate_relevance(message, query)
            message_tokens = self._estimate_tokens(message)
            
            if relevance_score > 0.3:  # Relevance threshold
                relevant_messages.append({
                    "message": message,
                    "relevance": relevance_score,
                    "tokens": message_tokens
                })
                current_tokens += message_tokens
        
        # Sort by relevance (keeping chronological order for equally relevant)
        relevant_messages.sort(
            key=lambda x: (x["relevance"], -len(relevant_messages) + relevant_messages.index(x)),
            reverse=True
        )
        
        return [msg["message"] for msg in relevant_messages]
    
    async def cleanup_inactive_contexts(self, max_age_hours: int = 24) -> int:
        """Clean up inactive context windows."""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        removed_count = 0
        
        keys_to_remove = []
        for key, context in self.active_contexts.items():
            # Check if context has recent activity
            if (not context.messages or 
                not context.messages[-1].get("timestamp") or
                datetime.fromisoformat(context.messages[-1]["timestamp"]) < cutoff_time):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.active_contexts[key]
            removed_count += 1
        
        logger.info(f"Cleaned up {removed_count} inactive context windows")
        return removed_count
    
    def _estimate_tokens(self, message: Dict[str, Any]) -> int:
        """Estimate token count for a message."""
        content = ""
        
        if isinstance(message.get("content"), str):
            content = message["content"]
        elif isinstance(message.get("content"), list):
            # Handle structured content (like Claude's format)
            for item in message["content"]:
                if isinstance(item, dict) and "text" in item:
                    content += item["text"]
                elif isinstance(item, str):
                    content += item
        
        # Add role and other metadata
        if message.get("role"):
            content += message["role"]
        
        # Rough estimation: ~4 characters per token
        return max(1, len(content) // self.chars_per_token)
    
    async def _score_message_importance(
        self, context: ContextWindow
    ) -> List[MessageImportance]:
        """Score messages by importance for compression decisions."""
        scores = []
        total_messages = len(context.messages)
        
        for i, message in enumerate(context.messages):
            # Recency score (more recent = more important)
            recency_score = (i + 1) / total_messages
            
            # Information density (longer messages with keywords)
            content = self._extract_message_content(message)
            density_score = min(1.0, len(content) / 500)  # Normalize by typical length
            
            # Task relevance (presence of action words, code, etc.)
            task_score = self._calculate_task_relevance(content)
            
            # User-initiated messages are more important
            user_initiated = message.get("role") == "user"
            
            # Overall importance calculation
            importance = (
                recency_score * 0.4 +
                density_score * 0.2 +
                task_score * 0.3 +
                (0.1 if user_initiated else 0.0)
            )
            
            scores.append(MessageImportance(
                message_index=i,
                importance_score=importance,
                reasons=[],
                recency_score=recency_score,
                information_density=density_score,
                task_relevance=task_score,
                user_initiated=user_initiated
            ))
        
        return scores
    
    async def _select_messages_for_compression(
        self,
        context: ContextWindow,
        scores: List[MessageImportance],
        target_tokens: int
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Select which messages to keep vs compress."""
        # Always keep the most recent messages
        min_keep = min(context.min_messages_to_keep, len(context.messages))
        recent_messages = context.messages[-min_keep:]
        recent_tokens = sum(self._estimate_tokens(msg) for msg in recent_messages)
        
        # Sort remaining messages by importance
        remaining_indices = list(range(len(context.messages) - min_keep))
        remaining_scores = scores[:len(context.messages) - min_keep]
        remaining_scores.sort(key=lambda x: x.importance_score, reverse=True)
        
        kept_messages = recent_messages.copy()
        compressed_messages = []
        current_tokens = recent_tokens
        
        # Add important messages until we hit target
        for score in remaining_scores:
            message = context.messages[score.message_index]
            message_tokens = self._estimate_tokens(message)
            
            if current_tokens + message_tokens <= target_tokens:
                kept_messages.insert(-min_keep, message)  # Insert before recent messages
                current_tokens += message_tokens
            else:
                compressed_messages.append(message)
        
        # Add any remaining messages to compressed list
        for i in remaining_indices:
            message = context.messages[i]
            if message not in [msg for msg in kept_messages]:
                compressed_messages.append(message)
        
        return kept_messages, compressed_messages
    
    async def _create_compression_summary(
        self, compressed_messages: List[Dict[str, Any]]
    ) -> str:
        """Create a summary of compressed conversation content."""
        if not compressed_messages:
            return "No content compressed"
        
        # Extract key topics and information
        topics = set()
        key_points = []
        
        for message in compressed_messages:
            content = self._extract_message_content(message)
            
            # Extract potential topics (simple keyword extraction)
            words = re.findall(r'\b[A-Za-z]{3,}\b', content.lower())
            topics.update(words[:5])  # Limit to avoid noise
            
            # Extract sentences that might be key points
            sentences = re.split(r'[.!?]+', content)
            for sentence in sentences:
                if (len(sentence.strip()) > 20 and 
                    any(keyword in sentence.lower() for keyword in 
                        ['implement', 'create', 'build', 'fix', 'issue', 'problem', 'solution'])):
                    key_points.append(sentence.strip()[:100])  # Truncate long sentences
        
        # Create summary
        summary_parts = []
        
        if topics:
            summary_parts.append(f"Discussed topics: {', '.join(list(topics)[:5])}")
        
        if key_points:
            summary_parts.append(f"Key points: {'; '.join(key_points[:3])}")
        
        summary_parts.append(f"Compressed {len(compressed_messages)} messages")
        
        return ". ".join(summary_parts)
    
    def _extract_message_content(self, message: Dict[str, Any]) -> str:
        """Extract text content from a message."""
        content = message.get("content", "")
        
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    text_parts.append(item["text"])
                elif isinstance(item, str):
                    text_parts.append(item)
            return " ".join(text_parts)
        
        return str(content)
    
    def _calculate_task_relevance(self, content: str) -> float:
        """Calculate how task-relevant a message is."""
        task_keywords = [
            'implement', 'create', 'build', 'develop', 'code', 'function',
            'class', 'method', 'api', 'database', 'test', 'debug', 'fix',
            'error', 'issue', 'problem', 'solution', 'design', 'architecture'
        ]
        
        content_lower = content.lower()
        matches = sum(1 for keyword in task_keywords if keyword in content_lower)
        
        return min(1.0, matches / 5)  # Normalize by expected keyword density
    
    def _calculate_relevance(self, message: Dict[str, Any], query: str) -> float:
        """Calculate relevance of a message to a query."""
        content = self._extract_message_content(message).lower()
        query_lower = query.lower()
        
        # Simple keyword matching
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        content_words = set(re.findall(r'\b\w+\b', content))
        
        if not query_words:
            return 0.0
        
        overlap = len(query_words.intersection(content_words))
        return overlap / len(query_words)
    
    async def _update_conversation_memory(self, context: ContextWindow) -> None:
        """Update conversation context in memory storage."""
        conversation_context = ConversationContext(
            conversation_id=context.conversation_id,
            agent_id=context.agent_id,
            session_id=context.conversation_id,  # Use conversation_id as session_id
            messages=context.messages,
            total_messages=len(context.messages),
            total_tokens=context.current_tokens,
            max_context_tokens=context.max_tokens,
            last_activity=datetime.utcnow()
        )
        
        await self.memory_manager.update_conversation_context(conversation_context)