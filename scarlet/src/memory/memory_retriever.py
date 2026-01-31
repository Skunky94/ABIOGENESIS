"""
Memory Retriever Tool for Scarlet

This module provides:
- Letta-compatible tool for memory retrieval
- Cross-collection semantic search
- Human-like memory access patterns

Author: ABIOGENESIS Team
Version: 1.0.0
Date: 2026-02-01
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


class RetrievalStrategy(Enum):
    """Strategies for memory retrieval"""
    SEMANTIC = "semantic"        # Vector similarity search
    TEMPORAL = "temporal"        # Time-based retrieval
    EMOTIONAL = "emotional"      # Emotion-based retrieval
    IMPORTANCE = "importance"    # Priority-based retrieval
    HYBRID = "hybrid"           # Combined approach


@dataclass
class RetrievalResult:
    """Result from memory retrieval"""
    memory_type: str
    title: str
    content: str
    relevance_score: float
    importance: float = 0.5
    emotional_tone: Optional[str] = None
    created_at: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def to_context_string(self) -> str:
        """Format as context string for LLM"""
        tone_str = f" [{self.emotional_tone}]" if self.emotional_tone else ""
        date_str = f" ({self.created_at[:10]})" if self.created_at else ""
        return f"[{self.memory_type.upper()}{tone_str}]{date_str} {self.title}: {self.content}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "memory_type": self.memory_type,
            "title": self.title,
            "content": self.content,
            "relevance_score": self.relevance_score,
            "importance": self.importance,
            "emotional_tone": self.emotional_tone,
            "created_at": self.created_at,
            "tags": self.tags,
        }


class MemoryRetriever:
    """
    Memory Retriever for human-like memory access.
    
    Provides cross-collection search capabilities with different
    retrieval strategies to simulate human memory patterns.
    """
    
    def __init__(self, memory_manager=None, embedding_manager=None):
        """
        Initialize memory retriever.
        
        Args:
            memory_manager: Optional MemoryManager instance
            embedding_manager: Optional EmbeddingManager instance
        """
        self._memory_manager = memory_manager
        self._embedding_manager = embedding_manager
        self._initialized = False
        
    def _ensure_initialized(self) -> bool:
        """Lazy initialization of managers."""
        if self._initialized:
            return True
            
        try:
            if self._memory_manager is None:
                from memory.memory_blocks import MemoryManager
                from memory.qdrant_manager import get_manager
                qdrant = get_manager()
                self._memory_manager = MemoryManager(qdrant_manager=qdrant)
            
            if self._embedding_manager is None:
                from memory.embedding_manager import EmbeddingManager
                self._embedding_manager = EmbeddingManager()
            
            self._initialized = True
            return True
            
        except Exception as e:
            logger.error(f"[MemoryRetriever] Initialization failed: {e}")
            return False
    
    def search(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 5,
        min_relevance: float = 0.3,
        strategy: RetrievalStrategy = RetrievalStrategy.HYBRID,
    ) -> List[RetrievalResult]:
        """
        Search memories across collections.
        
        Args:
            query: Natural language query
            memory_types: Types to search ["episodic", "semantic", "procedural", "emotional"]
                         If None, searches all types
            limit: Maximum results per type
            min_relevance: Minimum similarity score (0-1)
            strategy: Retrieval strategy to use
            
        Returns:
            List of RetrievalResult sorted by relevance
        """
        if not self._ensure_initialized():
            logger.warning("[MemoryRetriever] Not initialized, returning empty")
            return []
        
        # Default to all types
        if memory_types is None:
            memory_types = ["episodic", "semantic", "procedural", "emotional"]
        
        all_results = []
        
        # Search each memory type
        for mem_type in memory_types:
            try:
                type_results = self._search_collection(
                    query=query,
                    memory_type=mem_type,
                    limit=limit,
                    min_relevance=min_relevance,
                )
                all_results.extend(type_results)
            except Exception as e:
                logger.warning(f"[MemoryRetriever] Search failed for {mem_type}: {e}")
        
        # Sort by combined score (relevance + importance)
        all_results.sort(
            key=lambda r: (r.relevance_score * 0.7 + r.importance * 0.3),
            reverse=True
        )
        
        # Apply strategy-specific filtering
        if strategy == RetrievalStrategy.IMPORTANCE:
            all_results.sort(key=lambda r: r.importance, reverse=True)
        elif strategy == RetrievalStrategy.TEMPORAL:
            all_results.sort(key=lambda r: r.created_at or "", reverse=True)
        elif strategy == RetrievalStrategy.EMOTIONAL:
            all_results = [r for r in all_results if r.emotional_tone]
        
        return all_results[:limit * 2]  # Return more results for cross-type queries
    
    def _search_collection(
        self,
        query: str,
        memory_type: str,
        limit: int,
        min_relevance: float,
    ) -> List[RetrievalResult]:
        """Search a single collection."""
        from memory.qdrant_manager import CollectionType, COLLECTION_CONFIGS
        from memory.memory_blocks import MemoryType
        
        # Map string to CollectionType
        type_mapping = {
            "episodic": CollectionType.EPISODES,
            "semantic": CollectionType.CONCEPTS,
            "procedural": CollectionType.SKILLS,
            "emotional": CollectionType.EMOTIONS,
        }
        
        collection_type = type_mapping.get(memory_type)
        if not collection_type:
            return []
        
        # Generate query embedding
        dims = COLLECTION_CONFIGS[collection_type].vector_size
        
        try:
            embedding_result = self._embedding_manager.generate(query, dimensions=dims)
            query_vector = embedding_result.vector
        except Exception as e:
            logger.warning(f"[MemoryRetriever] Embedding failed: {e}")
            return []
        
        # Search Qdrant
        try:
            qdrant_results = self._memory_manager.qdrant.search(
                collection_type=collection_type,
                query_vector=query_vector,
                limit=limit,
                score_threshold=min_relevance,
            )
        except Exception as e:
            logger.warning(f"[MemoryRetriever] Qdrant search failed: {e}")
            return []
        
        # Convert to RetrievalResult
        results = []
        for payload, score in qdrant_results:
            # Handle payload formats
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    payload = {"content": payload, "title": "Memory"}
            elif not isinstance(payload, dict):
                payload = {"content": str(payload), "title": "Memory"}
            
            results.append(RetrievalResult(
                memory_type=memory_type,
                title=payload.get("title", "Untitled"),
                content=payload.get("content", "")[:500],  # Limit content length
                relevance_score=float(score),
                importance=payload.get("importance", 0.5),
                emotional_tone=payload.get("emotional_tone"),
                created_at=payload.get("created_at"),
                tags=payload.get("tags", []),
            ))
        
        return results
    
    def retrieve_context(
        self,
        query: str,
        max_tokens: int = 2000,
        include_types: Optional[List[str]] = None,
    ) -> str:
        """
        Retrieve memory context for a query.
        
        Formats retrieved memories as context string suitable
        for injecting into LLM prompts.
        
        Args:
            query: Natural language query
            max_tokens: Approximate max tokens in response
            include_types: Memory types to include
            
        Returns:
            Formatted context string
        """
        results = self.search(
            query=query,
            memory_types=include_types,
            limit=10,
            min_relevance=0.35,
            strategy=RetrievalStrategy.HYBRID,
        )
        
        if not results:
            return ""
        
        # Build context string
        context_parts = ["== RELEVANT MEMORIES =="]
        char_count = 0
        max_chars = max_tokens * 4  # Rough token-to-char ratio
        
        for result in results:
            entry = result.to_context_string()
            if char_count + len(entry) > max_chars:
                break
            context_parts.append(entry)
            char_count += len(entry)
        
        return "\n".join(context_parts)
    
    def get_recent_memories(
        self,
        memory_type: Optional[str] = None,
        limit: int = 5,
        hours: int = 24,
    ) -> List[RetrievalResult]:
        """
        Get recent memories within a time window.
        
        Args:
            memory_type: Optional specific type
            limit: Maximum results
            hours: Time window in hours
            
        Returns:
            List of recent memories
        """
        # For now, just search with temporal strategy
        # TODO: Implement proper temporal filtering with Qdrant filters
        return self.search(
            query="recent events conversations",
            memory_types=[memory_type] if memory_type else None,
            limit=limit,
            strategy=RetrievalStrategy.TEMPORAL,
        )
    
    def get_emotional_memories(
        self,
        emotion: Optional[str] = None,
        limit: int = 5,
    ) -> List[RetrievalResult]:
        """
        Get memories with emotional associations.
        
        Args:
            emotion: Optional specific emotion to filter
            limit: Maximum results
            
        Returns:
            List of emotional memories
        """
        results = self.search(
            query=f"emotional {emotion or 'significant'} experience feeling",
            memory_types=["emotional", "episodic"],
            limit=limit,
            strategy=RetrievalStrategy.EMOTIONAL,
        )
        
        if emotion:
            results = [r for r in results if r.emotional_tone == emotion]
        
        return results


# Letta Tool Definition
MEMORY_SEARCH_TOOL = {
    "name": "memory_search",
    "description": """Search your long-term memory for relevant information.
    
Use this tool to:
- Recall past conversations and events
- Remember facts and knowledge you've learned
- Access skills and procedures you've developed
- Retrieve emotional patterns and associations

Always use this before answering questions that might relate to past experiences or learned information.""",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language query describing what to search for"
            },
            "memory_types": {
                "type": "array",
                "items": {"type": "string", "enum": ["episodic", "semantic", "procedural", "emotional"]},
                "description": "Types of memory to search. Default: all types"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results (default: 5)",
                "default": 5
            }
        },
        "required": ["query"]
    }
}


# Global retriever instance
_global_retriever: Optional[MemoryRetriever] = None


def get_retriever() -> MemoryRetriever:
    """Get or create global retriever instance."""
    global _global_retriever
    if _global_retriever is None:
        _global_retriever = MemoryRetriever()
    return _global_retriever


def memory_search_tool(
    query: str,
    memory_types: Optional[List[str]] = None,
    limit: int = 5,
) -> str:
    """
    Tool function for Letta integration.
    
    Args:
        query: What to search for
        memory_types: Types to search
        limit: Max results
        
    Returns:
        JSON string with results
    """
    retriever = get_retriever()
    results = retriever.search(
        query=query,
        memory_types=memory_types,
        limit=limit,
    )
    
    if not results:
        return json.dumps({
            "status": "no_results",
            "message": f"No memories found for: {query}",
            "results": []
        })
    
    return json.dumps({
        "status": "success",
        "count": len(results),
        "results": [r.to_dict() for r in results]
    }, indent=2)


def memory_context_tool(query: str) -> str:
    """
    Get formatted context from memory for a query.
    
    Args:
        query: What context to retrieve
        
    Returns:
        Formatted context string
    """
    retriever = get_retriever()
    context = retriever.retrieve_context(query)
    
    if not context:
        return "No relevant memories found."
    
    return context
