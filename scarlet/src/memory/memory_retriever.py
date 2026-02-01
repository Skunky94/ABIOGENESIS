"""
Memory Retriever Tool for Scarlet - Human-Like Memory System v2.0

This module provides:
- Query-intent-aware retrieval (ADR-005)
- Multi-strategy search (temporal, entity, emotional, topic)
- Multi-factor ranking formula
- Access tracking and reinforcement
- Letta-compatible tool interface

Author: ABIOGENESIS Team
Version: 2.0.0
Date: 2026-02-01
ADR: ADR-005
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
    MatchAny,
    Range,
)

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


class SearchStrategy(Enum):
    """Search strategies based on query intent (ADR-005)"""
    FILTERED_TEMPORAL = "filtered_temporal"     # Filter by date + semantic
    FILTERED_ENTITY = "filtered_entity"         # Filter by participants + semantic
    FILTERED_EMOTIONAL = "filtered_emotional"   # Filter by valence + semantic
    FILTERED_TOPIC = "filtered_topic"           # Filter by topics + semantic
    PURE_SEMANTIC = "pure_semantic"             # Only semantic (fallback)


class RetrievalStrategy(Enum):
    """Legacy strategies (kept for backward compatibility)"""
    SEMANTIC = "semantic"        # Vector similarity search
    TEMPORAL = "temporal"        # Time-based retrieval
    EMOTIONAL = "emotional"      # Emotion-based retrieval
    IMPORTANCE = "importance"    # Priority-based retrieval
    HYBRID = "hybrid"           # Combined approach


@dataclass
class RetrievalResult:
    """Result from memory retrieval (enhanced for ADR-005)"""
    memory_type: str
    title: str
    content: str
    relevance_score: float
    importance: float = 0.5
    emotional_tone: Optional[str] = None
    created_at: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # ADR-005: Additional ranking factors
    id: Optional[str] = None
    collection: Optional[str] = None
    semantic_score: float = 0.0
    temporal_relevance: float = 0.0
    emotional_intensity: float = 0.0
    access_frequency: float = 0.0
    recency_bonus: float = 0.0
    decay_factor: float = 1.0
    payload: Dict[str, Any] = field(default_factory=dict)
    
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
    Memory Retriever for human-like memory access (ADR-005 v2.0).
    
    Provides:
    - Query-intent-aware retrieval
    - Multi-strategy search with Qdrant filters
    - Multi-factor ranking formula
    - Access tracking and reinforcement
    """
    
    # Collection name mapping
    COLLECTION_MAP = {
        "episodic": "episodes",
        "semantic": "concepts", 
        "procedural": "skills",
        "skills": "skills",
        "emotional": "emotions",
        "emotions": "emotions",
        "episodes": "episodes",
        "concepts": "concepts",
    }
    
    # ADR-005 Ranking weights
    WEIGHT_SEMANTIC = 0.35
    WEIGHT_TEMPORAL = 0.25
    WEIGHT_IMPORTANCE = 0.15
    WEIGHT_EMOTIONAL = 0.10
    WEIGHT_FREQUENCY = 0.10
    WEIGHT_RECENCY = 0.05
    
    def __init__(self, memory_manager=None, embedding_manager=None, qdrant_client=None):
        """
        Initialize memory retriever.
        
        Args:
            memory_manager: Optional MemoryManager instance
            embedding_manager: Optional EmbeddingManager instance
            qdrant_client: Optional QdrantClient for direct access
        """
        self._memory_manager = memory_manager
        self._embedding_manager = embedding_manager
        self._qdrant_client = qdrant_client
        self._query_analyzer = None
        self._initialized = False
        
        # Access tracking config
        self.enable_access_tracking = True
        self.importance_boost_per_access = 0.02
        self.max_importance = 0.95
        
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
            
            if self._qdrant_client is None:
                self._qdrant_client = QdrantClient(
                    host=os.getenv("QDRANT_HOST", "localhost"),
                    port=int(os.getenv("QDRANT_PORT", "6333")),
                )
            
            # Try to initialize query analyzer (optional)
            try:
                from memory.query_analyzer import get_query_analyzer
                self._query_analyzer = get_query_analyzer()
                logger.info("[MemoryRetriever] Query Analyzer initialized")
            except Exception as e:
                logger.warning(f"[MemoryRetriever] Query Analyzer not available: {e}")
            
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
    
    def smart_search(
        self,
        query: str,
        query_vector: Optional[List[float]] = None,
        known_entities: Optional[List[str]] = None,
        limit: int = 10,
    ) -> Tuple[List[RetrievalResult], Dict[str, Any]]:
        """
        ADR-005: Intelligent search with query analysis and multi-factor ranking.
        
        Args:
            query: User's query text
            query_vector: Pre-computed embedding (optional)
            known_entities: Known entities for better analysis
            limit: Max results
            
        Returns:
            Tuple of (results, metadata)
        """
        import time
        start_time = time.time()
        
        if not self._ensure_initialized():
            return [], {"error": "Not initialized"}
        
        metadata = {
            "query": query,
            "strategy": SearchStrategy.PURE_SEMANTIC.value,
            "collections_searched": [],
            "total_candidates": 0,
        }
        
        # Step 1: Analyze query (if analyzer available)
        analysis = None
        qdrant_filter = None
        memory_types = ["episodic", "semantic", "procedural", "emotional"]
        
        if self._query_analyzer:
            try:
                analysis = self._query_analyzer.analyze(query, known_entities)
                metadata["intent"] = analysis.intent.value
                metadata["entities"] = analysis.entities
                metadata["topics"] = analysis.topics
                
                # Build filter based on analysis
                qdrant_filter, strategy = self._build_filter_from_analysis(analysis)
                metadata["strategy"] = strategy.value
                
                # Use analyzed memory types
                memory_types = [self._map_memory_type(t) for t in analysis.memory_types]
                
            except Exception as e:
                logger.warning(f"[smart_search] Analysis failed: {e}")
        
        # Step 2: Get embedding if not provided
        if query_vector is None:
            try:
                semantic_query = analysis.semantic_query if analysis else query
                embedding_result = self._embedding_manager.generate(semantic_query, dimensions=1024)
                query_vector = embedding_result.vector
            except Exception as e:
                logger.error(f"[smart_search] Embedding failed: {e}")
                return [], {"error": f"Embedding failed: {e}"}
        
        # Step 3: Search each collection with filter
        all_results = []
        collections = [self.COLLECTION_MAP.get(t, t) for t in memory_types]
        collections = list(set(collections))  # Unique
        metadata["collections_searched"] = collections
        
        for collection in collections:
            try:
                results = self._search_collection_filtered(
                    collection=collection,
                    query_vector=query_vector,
                    qdrant_filter=qdrant_filter,
                    limit=limit * 2,
                )
                all_results.extend(results)
            except Exception as e:
                logger.warning(f"[smart_search] Search failed for {collection}: {e}")
        
        metadata["total_candidates"] = len(all_results)
        
        # Step 4: Apply multi-factor ranking
        ranked_results = self._rank_results_adr005(all_results, analysis)
        
        # Step 5: Trim to limit
        final_results = ranked_results[:limit]
        
        # Step 6: Update access stats
        if self.enable_access_tracking and final_results:
            self._update_access_stats(final_results)
        
        elapsed_ms = (time.time() - start_time) * 1000
        metadata["retrieval_time_ms"] = round(elapsed_ms, 1)
        
        return final_results, metadata
    
    def _build_filter_from_analysis(self, analysis) -> Tuple[Optional[Filter], SearchStrategy]:
        """Build Qdrant filter from query analysis."""
        from .query_analyzer import QueryIntent, TimeType
        
        conditions = []
        strategy = SearchStrategy.PURE_SEMANTIC
        
        # Temporal filter
        if analysis.intent == QueryIntent.TEMPORAL and analysis.time.type != TimeType.NONE:
            strategy = SearchStrategy.FILTERED_TEMPORAL
            date_str = analysis.time.to_date_filter()
            if date_str:
                conditions.append(
                    FieldCondition(key="date", match=MatchValue(value=date_str))
                )
        
        # Entity filter
        if analysis.intent == QueryIntent.ENTITY and analysis.entities:
            strategy = SearchStrategy.FILTERED_ENTITY
            conditions.append(
                FieldCondition(key="participants", match=MatchAny(any=analysis.entities))
            )
        
        # Emotional filter
        if analysis.intent == QueryIntent.EMOTIONAL:
            strategy = SearchStrategy.FILTERED_EMOTIONAL
            if analysis.emotion_filter == "positive":
                conditions.append(
                    FieldCondition(key="emotional_valence", range=Range(gt=0.3))
                )
            elif analysis.emotion_filter == "negative":
                conditions.append(
                    FieldCondition(key="emotional_valence", range=Range(lt=-0.3))
                )
        
        # Topic filter
        if analysis.intent == QueryIntent.TOPIC and analysis.topics:
            strategy = SearchStrategy.FILTERED_TOPIC
            conditions.append(
                FieldCondition(key="topics", match=MatchAny(any=analysis.topics))
            )
        
        qdrant_filter = Filter(must=conditions) if conditions else None
        return qdrant_filter, strategy
    
    def _map_memory_type(self, mem_type: str) -> str:
        """Map memory type string to collection name."""
        return self.COLLECTION_MAP.get(mem_type, mem_type)
    
    def _search_collection_filtered(
        self,
        collection: str,
        query_vector: List[float],
        qdrant_filter: Optional[Filter],
        limit: int,
    ) -> List[RetrievalResult]:
        """Search a collection with optional filter (ADR-005)."""
        try:
            results = self._qdrant_client.search(
                collection_name=collection,
                query_vector=query_vector,
                query_filter=qdrant_filter,
                limit=limit,
                score_threshold=0.3,
                with_payload=True,
            )
            
            memory_results = []
            for hit in results:
                payload = hit.payload or {}
                
                memory_results.append(RetrievalResult(
                    id=str(hit.id),
                    collection=collection,
                    memory_type=collection,
                    title=payload.get("title", "Untitled"),
                    content=payload.get("content", "")[:500],
                    relevance_score=0.0,  # Will be computed
                    semantic_score=hit.score,
                    importance=payload.get("importance", 0.5),
                    emotional_tone=payload.get("primary_emotion") or payload.get("emotional_tone"),
                    created_at=payload.get("created_at"),
                    tags=payload.get("tags", []),
                    decay_factor=payload.get("decay_factor", 1.0),
                    payload=payload,
                ))
            
            return memory_results
            
        except Exception as e:
            logger.error(f"[_search_collection_filtered] Error in {collection}: {e}")
            return []
    
    def _rank_results_adr005(
        self,
        results: List[RetrievalResult],
        analysis=None,
    ) -> List[RetrievalResult]:
        """Apply ADR-005 multi-factor ranking formula."""
        now = datetime.now()
        
        for result in results:
            payload = result.payload
            
            # 1. Semantic similarity
            semantic_score = result.semantic_score
            
            # 2. Temporal relevance
            temporal_relevance = 0.0
            if analysis and analysis.time.resolved_start:
                memory_date_str = payload.get("date")
                if memory_date_str:
                    try:
                        memory_date = datetime.strptime(memory_date_str, "%Y-%m-%d")
                        days_diff = abs((analysis.time.resolved_start - memory_date).days)
                        temporal_relevance = max(0, 1.0 - (days_diff / 7))
                    except:
                        pass
            result.temporal_relevance = temporal_relevance
            
            # 3. Importance
            importance = payload.get("importance", 0.5)
            result.importance = importance
            
            # 4. Emotional intensity
            valence = payload.get("emotional_valence", 0.0)
            arousal = payload.get("emotional_arousal", 0.5)
            emotional_intensity = abs(valence) * arousal if valence else 0.0
            result.emotional_intensity = emotional_intensity
            
            # 5. Access frequency (normalized)
            access_count = payload.get("access_count", 0)
            access_frequency = min(1.0, access_count / 10)
            result.access_frequency = access_frequency
            
            # 6. Recency bonus
            created_at_str = payload.get("created_at")
            recency_bonus = 0.0
            if created_at_str:
                try:
                    if "T" in created_at_str:
                        created_at = datetime.fromisoformat(created_at_str.replace("Z", ""))
                    else:
                        created_at = datetime.strptime(created_at_str, "%Y-%m-%d")
                    days_old = (now - created_at).days
                    recency_bonus = max(0, 1.0 - (days_old / 30))
                except:
                    pass
            result.recency_bonus = recency_bonus
            
            # 7. Decay factor
            decay_factor = payload.get("decay_factor", 1.0)
            result.decay_factor = decay_factor
            
            # ADR-005 Formula
            final_score = (
                semantic_score * self.WEIGHT_SEMANTIC +
                temporal_relevance * self.WEIGHT_TEMPORAL +
                importance * self.WEIGHT_IMPORTANCE +
                emotional_intensity * self.WEIGHT_EMOTIONAL +
                access_frequency * self.WEIGHT_FREQUENCY +
                recency_bonus * self.WEIGHT_RECENCY
            ) * decay_factor
            
            result.relevance_score = round(final_score, 4)
        
        # Sort by final score
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results
    
    def _update_access_stats(self, results: List[RetrievalResult]) -> None:
        """Update access count and importance for retrieved memories (ADR-005)."""
        now = datetime.now().isoformat()
        
        for result in results:
            if not result.id or not result.collection:
                continue
            try:
                current_access = result.payload.get("access_count", 0)
                current_importance = result.payload.get("importance", 0.5)
                
                new_access = current_access + 1
                new_importance = min(
                    self.max_importance,
                    current_importance + self.importance_boost_per_access
                )
                
                self._qdrant_client.set_payload(
                    collection_name=result.collection,
                    payload={
                        "access_count": new_access,
                        "last_accessed": now,
                        "importance": round(new_importance, 3),
                    },
                    points=[result.id],
                )
                
                logger.debug(f"[AccessTracking] Updated {result.id}: count={new_access}")
                
            except Exception as e:
                logger.warning(f"[AccessTracking] Failed for {result.id}: {e}")
    
    def format_for_context(self, results: List[RetrievalResult], max_memories: int = 5) -> str:
        """Format results for session_context injection (ADR-005)."""
        if not results:
            return ""
        
        lines = ["[RICORDI EMERGENTI]", ""]
        
        for i, mem in enumerate(results[:max_memories], 1):
            collection_label = {
                "episodes": "📅 Episodio",
                "concepts": "💡 Concetto",
                "skills": "🔧 Procedura",
                "emotions": "💜 Emozione",
            }.get(mem.collection, "📝 Memoria")
            
            lines.append(f"{i}. {collection_label}: {mem.title}")
            content_preview = mem.content[:150] + "..." if len(mem.content) > 150 else mem.content
            lines.append(f"   {content_preview}")
            
            if mem.temporal_relevance > 0.5:
                lines.append(f"   ⏰ Molto recente")
            if mem.emotional_intensity > 0.5:
                lines.append(f"   💫 Emotivamente significativo")
            
            lines.append("")
        
        return "\n".join(lines)

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
