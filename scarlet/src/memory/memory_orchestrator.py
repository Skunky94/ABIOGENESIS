"""
Memory Orchestrator for Scarlet

This module provides:
- Central controller for all memory layers
- Automatic storage routing based on content type
- Intelligent retrieval strategy selection
- Memory consolidation coordination
- Cross-layer consistency management

The Memory Orchestrator is the "central executive" of Scarlet's memory system,
inspired by Baddeley's working memory model.

Author: ABIOGENESIS Team
Version: 1.0.0
Date: 2026-02-01
"""

import os
import sys
import json
import logging
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


class MemoryOperation(Enum):
    """Types of memory operations"""
    STORE = auto()
    RETRIEVE = auto()
    UPDATE = auto()
    DELETE = auto()
    CONSOLIDATE = auto()


class ContentCategory(Enum):
    """Categories for automatic content classification"""
    EVENT = "event"           # Something that happened → Episodic
    FACT = "fact"             # Information about something → Semantic
    PROCEDURE = "procedure"   # How to do something → Procedural
    EMOTION = "emotion"       # Emotional response → Emotional
    TASK = "task"             # Active task → Working
    UNKNOWN = "unknown"       # Couldn't classify


@dataclass
class MemoryRequest:
    """Request to the memory orchestrator"""
    operation: MemoryOperation
    content: str
    category: Optional[ContentCategory] = None
    importance: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = "user"  # user, system, sleep_agent, etc.
    
    
@dataclass
class MemoryResponse:
    """Response from the memory orchestrator"""
    success: bool
    operation: MemoryOperation
    results: Any = None
    message: str = ""
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsolidationResult:
    """Result of memory consolidation"""
    items_processed: int = 0
    items_stored: int = 0
    items_updated: int = 0
    working_memory_dumped: int = 0
    errors: List[str] = field(default_factory=list)


class MemoryOrchestrator:
    """
    Central Memory Controller for Scarlet.
    
    Coordinates all memory layers:
    - Working Memory (Redis): Active, short-term storage
    - Episodic Memory (Qdrant): Events and experiences
    - Semantic Memory (Qdrant): Facts and knowledge
    - Procedural Memory (Qdrant): Skills and procedures
    - Emotional Memory (Qdrant): Affective patterns
    - Core Memory (Letta): Identity and context
    
    Responsibilities:
    - Route storage requests to appropriate layer
    - Select optimal retrieval strategy
    - Coordinate consolidation from WM to LTM
    - Maintain cross-layer consistency
    """
    
    # Keywords for content classification
    CATEGORY_KEYWORDS = {
        ContentCategory.EVENT: [
            "accaduto", "successo", "evento", "conversazione", "discussione",
            "happened", "occurred", "event", "conversation", "discussed",
            "meeting", "session", "quando", "when", "yesterday", "today",
        ],
        ContentCategory.FACT: [
            "è", "sono", "significa", "definizione", "fatto", "informazione",
            "is", "are", "means", "definition", "fact", "information",
            "sapere", "know", "learned", "discovered", "true", "false",
        ],
        ContentCategory.PROCEDURE: [
            "come", "procedura", "metodo", "step", "passaggi", "istruzioni",
            "how", "procedure", "method", "steps", "instructions",
            "processo", "process", "guide", "tutorial", "skill",
        ],
        ContentCategory.EMOTION: [
            "sentire", "emozione", "felice", "triste", "arrabbiato", "paura",
            "feel", "emotion", "happy", "sad", "angry", "fear", "joy",
            "love", "hate", "excited", "worried", "curious", "satisfied",
        ],
        ContentCategory.TASK: [
            "fare", "compito", "obiettivo", "goal", "task", "todo",
            "do", "complete", "finish", "start", "begin", "priority",
        ],
    }
    
    def __init__(
        self,
        memory_manager=None,
        working_memory=None,
        retriever=None,
        letta_client=None,
        agent_id: Optional[str] = None,
        auto_consolidate: bool = True,
        consolidation_threshold: int = 10,
    ):
        """
        Initialize the Memory Orchestrator.
        
        Args:
            memory_manager: MemoryManager for LTM operations
            working_memory: WorkingMemory for active storage
            retriever: MemoryRetriever for search
            letta_client: Letta client for core memory
            agent_id: Scarlet's agent ID for Letta operations
            auto_consolidate: Enable automatic WM→LTM consolidation
            consolidation_threshold: WM items before auto-consolidation
        """
        self._memory_manager = memory_manager
        self._working_memory = working_memory
        self._retriever = retriever
        self._letta_client = letta_client
        self._agent_id = agent_id
        
        self._auto_consolidate = auto_consolidate
        self._consolidation_threshold = consolidation_threshold
        self._initialized = False
        
        # Statistics
        self._stats = {
            "operations": 0,
            "stores": 0,
            "retrieves": 0,
            "consolidations": 0,
            "errors": 0,
        }
        
        # Callbacks
        self._on_store_callback: Optional[Callable] = None
        self._on_retrieve_callback: Optional[Callable] = None
    
    @property
    def working_memory(self):
        """Public access to working memory component."""
        self._ensure_initialized()
        return self._working_memory
    
    @property
    def memory_manager(self):
        """Public access to memory manager (Qdrant LTM)."""
        self._ensure_initialized()
        return self._memory_manager
    
    @property
    def retriever(self):
        """Public access to memory retriever."""
        self._ensure_initialized()
        return self._retriever
    
    def _ensure_initialized(self) -> bool:
        """Lazy initialization of components."""
        if self._initialized:
            return True
        
        try:
            # Initialize Memory Manager
            if self._memory_manager is None:
                from memory.memory_blocks import MemoryManager
                from memory.qdrant_manager import get_manager
                qdrant = get_manager()
                self._memory_manager = MemoryManager(qdrant_manager=qdrant)
            
            # Initialize Working Memory
            if self._working_memory is None:
                from memory.working_memory import get_working_memory
                self._working_memory = get_working_memory()
            
            # Initialize Retriever
            if self._retriever is None:
                from memory.memory_retriever import get_retriever
                self._retriever = get_retriever()
            
            self._initialized = True
            logger.info("[MemoryOrchestrator] Initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"[MemoryOrchestrator] Initialization failed: {e}")
            return False
    
    # === Content Classification ===
    
    def classify_content(self, content: str) -> ContentCategory:
        """
        Automatically classify content into a category.
        
        Uses keyword matching and heuristics to determine
        the best memory layer for storage.
        
        Args:
            content: The content to classify
            
        Returns:
            ContentCategory for the content
        """
        content_lower = content.lower()
        scores = {cat: 0 for cat in ContentCategory}
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content_lower:
                    scores[category] += 1
        
        # Find highest scoring category
        max_score = max(scores.values())
        if max_score > 0:
            for cat, score in scores.items():
                if score == max_score:
                    return cat
        
        return ContentCategory.UNKNOWN
    
    def _calculate_importance(self, content: str, category: ContentCategory) -> float:
        """
        Calculate importance score for content.
        
        Args:
            content: The content
            category: The classified category
            
        Returns:
            Importance score (0.0-1.0)
        """
        base_importance = 0.5
        
        # Boost for certain categories
        category_boost = {
            ContentCategory.EMOTION: 0.1,
            ContentCategory.TASK: 0.15,
            ContentCategory.FACT: 0.05,
        }
        
        importance = base_importance + category_boost.get(category, 0)
        
        # Boost for longer content (likely more detailed)
        if len(content) > 200:
            importance += 0.1
        
        # Boost for content with keywords suggesting importance
        importance_keywords = ["importante", "important", "critical", "critico", "remember", "ricorda"]
        if any(kw in content.lower() for kw in importance_keywords):
            importance += 0.2
        
        return min(1.0, importance)
    
    # === Storage Operations ===
    
    def store(
        self,
        content: str,
        category: Optional[ContentCategory] = None,
        importance: Optional[float] = None,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        force_ltm: bool = False,
    ) -> MemoryResponse:
        """
        Store content in the appropriate memory layer.
        
        Automatically classifies content and routes to the best layer:
        - Low importance + recent → Working Memory
        - High importance or force_ltm → Long-Term Memory
        
        Args:
            content: Content to store
            category: Optional category override
            importance: Optional importance override
            title: Optional title for the memory
            metadata: Additional metadata
            force_ltm: Force storage in long-term memory
            
        Returns:
            MemoryResponse with result
        """
        start_time = time.time()
        
        if not self._ensure_initialized():
            return MemoryResponse(
                success=False,
                operation=MemoryOperation.STORE,
                message="Orchestrator not initialized"
            )
        
        # Classify if not provided
        if category is None:
            category = self.classify_content(content)
        
        # Calculate importance if not provided
        if importance is None:
            importance = self._calculate_importance(content, category)
        
        # Generate title if not provided
        if title is None:
            title = content[:50] + ("..." if len(content) > 50 else "")
        
        self._stats["operations"] += 1
        
        try:
            # Decide storage layer
            if force_ltm or importance >= 0.6:
                # Store in Long-Term Memory
                result = self._store_in_ltm(
                    content=content,
                    category=category,
                    importance=importance,
                    title=title,
                    metadata=metadata,
                )
            else:
                # Store in Working Memory first
                result = self._store_in_wm(
                    content=content,
                    category=category,
                    importance=importance,
                    metadata=metadata,
                )
            
            self._stats["stores"] += 1
            
            # Check if auto-consolidation needed
            if self._auto_consolidate:
                self._check_auto_consolidation()
            
            # Callback
            if self._on_store_callback:
                self._on_store_callback(content, category, importance)
            
            duration = (time.time() - start_time) * 1000
            
            return MemoryResponse(
                success=True,
                operation=MemoryOperation.STORE,
                results=result,
                message=f"Stored in {'LTM' if force_ltm or importance >= 0.6 else 'WM'}",
                duration_ms=duration,
                metadata={"category": category.value, "importance": importance}
            )
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"[MemoryOrchestrator] Store failed: {e}")
            return MemoryResponse(
                success=False,
                operation=MemoryOperation.STORE,
                message=str(e)
            )
    
    def _store_in_ltm(
        self,
        content: str,
        category: ContentCategory,
        importance: float,
        title: str,
        metadata: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Store in Long-Term Memory (Qdrant)."""
        
        # Route to appropriate memory type
        if category == ContentCategory.EVENT:
            memory = self._memory_manager.create_episodic_memory(
                title=title,
                content=content,
                event_type="conversation",
                importance=importance,
                tags=metadata.get("tags", []) if metadata else [],
            )
        elif category == ContentCategory.FACT:
            memory = self._memory_manager.create_semantic_memory(
                title=title,
                content=content,
                concept_category="fact",
                importance=importance,
                confidence=0.8,
                tags=metadata.get("tags", []) if metadata else [],
            )
        elif category == ContentCategory.PROCEDURE:
            memory = self._memory_manager.create_procedural_memory(
                skill_name=title,
                content=content,
                procedure_type="general",
                importance=importance,
                tags=metadata.get("tags", []) if metadata else [],
            )
        elif category == ContentCategory.EMOTION:
            memory = self._memory_manager.create_emotional_memory(
                trigger=metadata.get("trigger", "interaction") if metadata else "interaction",
                content=content,
                response_type=metadata.get("emotion_type", "reaction") if metadata else "reaction",
                intensity=importance,
            )
        else:
            # Default to semantic
            memory = self._memory_manager.create_semantic_memory(
                title=title,
                content=content,
                importance=importance,
            )
        
        return {"memory_id": memory.id, "type": category.value, "layer": "ltm"}
    
    def _store_in_wm(
        self,
        content: str,
        category: ContentCategory,
        importance: float,
        metadata: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Store in Working Memory (Redis)."""
        from memory.working_memory import WorkingMemoryItemType
        
        # Map category to WM item type
        type_mapping = {
            ContentCategory.TASK: WorkingMemoryItemType.TASK,
            ContentCategory.FACT: WorkingMemoryItemType.FACT,
            ContentCategory.EVENT: WorkingMemoryItemType.CONTEXT,
            ContentCategory.PROCEDURE: WorkingMemoryItemType.REFERENCE,
        }
        
        item_type = type_mapping.get(category, WorkingMemoryItemType.FACT)
        
        item = self._working_memory.add(
            content=content,
            item_type=item_type,
            importance=importance,
            metadata=metadata,
        )
        
        return {"item_id": item.id, "type": category.value, "layer": "wm"}
    
    # === Retrieval Operations ===
    
    def retrieve(
        self,
        query: str,
        include_wm: bool = True,
        include_ltm: bool = True,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
    ) -> MemoryResponse:
        """
        Retrieve memories matching a query.
        
        Searches both Working Memory and Long-Term Memory,
        combining and ranking results.
        
        Args:
            query: Natural language query
            include_wm: Search working memory
            include_ltm: Search long-term memory
            memory_types: LTM types to search
            limit: Maximum results
            
        Returns:
            MemoryResponse with results
        """
        start_time = time.time()
        
        if not self._ensure_initialized():
            return MemoryResponse(
                success=False,
                operation=MemoryOperation.RETRIEVE,
                message="Orchestrator not initialized"
            )
        
        self._stats["operations"] += 1
        results = []
        
        try:
            # Search Working Memory first (faster, more recent)
            if include_wm:
                wm_results = self._working_memory.search(query)
                for item in wm_results[:limit // 2]:
                    results.append({
                        "source": "working_memory",
                        "content": item.content,
                        "importance": item.importance,
                        "type": item.item_type.value,
                        "relevance": 0.9,  # WM items are highly relevant
                    })
            
            # Search Long-Term Memory
            if include_ltm:
                ltm_results = self._retriever.search(
                    query=query,
                    memory_types=memory_types,
                    limit=limit,
                )
                for result in ltm_results:
                    results.append({
                        "source": "long_term_memory",
                        "content": result.content,
                        "importance": result.importance,
                        "type": result.memory_type,
                        "relevance": result.relevance_score,
                        "title": result.title,
                    })
            
            # Sort by combined score
            results.sort(
                key=lambda x: x["relevance"] * 0.6 + x["importance"] * 0.4,
                reverse=True
            )
            
            self._stats["retrieves"] += 1
            
            # Callback
            if self._on_retrieve_callback:
                self._on_retrieve_callback(query, len(results))
            
            duration = (time.time() - start_time) * 1000
            
            return MemoryResponse(
                success=True,
                operation=MemoryOperation.RETRIEVE,
                results=results[:limit],
                message=f"Found {len(results)} memories",
                duration_ms=duration,
            )
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"[MemoryOrchestrator] Retrieve failed: {e}")
            return MemoryResponse(
                success=False,
                operation=MemoryOperation.RETRIEVE,
                message=str(e)
            )
    
    def retrieve_context(self, query: str, max_tokens: int = 2000) -> str:
        """
        Get formatted context string for LLM.
        
        Combines Working Memory and LTM into a context string
        suitable for injecting into prompts.
        
        Args:
            query: Query for context retrieval
            max_tokens: Approximate max tokens
            
        Returns:
            Formatted context string
        """
        if not self._ensure_initialized():
            return ""
        
        parts = []
        char_count = 0
        max_chars = max_tokens * 4
        
        # Working memory context
        wm_context = self._working_memory.to_context_string()
        if wm_context:
            parts.append(wm_context)
            char_count += len(wm_context)
        
        # LTM context
        if char_count < max_chars:
            ltm_context = self._retriever.retrieve_context(
                query=query,
                max_tokens=(max_tokens - char_count // 4),
            )
            if ltm_context:
                parts.append(ltm_context)
        
        return "\n\n".join(parts)
    
    # === Consolidation ===
    
    def consolidate(self, force: bool = False) -> ConsolidationResult:
        """
        Consolidate Working Memory to Long-Term Memory.
        
        Moves important items from WM to LTM, similar to
        human memory consolidation during sleep.
        
        Args:
            force: Force consolidation even if below threshold
            
        Returns:
            ConsolidationResult with statistics
        """
        if not self._ensure_initialized():
            return ConsolidationResult(errors=["Not initialized"])
        
        result = ConsolidationResult()
        
        try:
            # Get items from working memory
            wm_items = self._working_memory.get_all()
            result.items_processed = len(wm_items)
            
            # Only consolidate important items
            for item in wm_items:
                if item.importance >= 0.5:
                    try:
                        # Classify and store in LTM
                        category = self.classify_content(item.content)
                        self._store_in_ltm(
                            content=item.content,
                            category=category,
                            importance=item.importance,
                            title=item.content[:50],
                            metadata=item.metadata,
                        )
                        result.items_stored += 1
                    except Exception as e:
                        result.errors.append(f"Failed to store item: {e}")
            
            # Dump WM
            if force:
                dumped = self._working_memory.dump_to_ltm()
                result.working_memory_dumped = len(dumped)
                self._working_memory.clear()
            
            self._stats["consolidations"] += 1
            logger.info(f"[MemoryOrchestrator] Consolidated {result.items_stored} items to LTM")
            
        except Exception as e:
            result.errors.append(str(e))
            self._stats["errors"] += 1
        
        return result
    
    def _check_auto_consolidation(self) -> None:
        """Check if auto-consolidation should be triggered."""
        wm_count = len(self._working_memory.get_all())
        if wm_count >= self._consolidation_threshold:
            logger.info(f"[MemoryOrchestrator] Auto-consolidating (WM has {wm_count} items)")
            self.consolidate()
    
    # === Core Memory (Letta) ===
    
    def update_core_memory(self, block_label: str, value: str) -> bool:
        """
        Update a Letta core memory block.
        
        Args:
            block_label: The block to update (persona, human, goals, etc.)
            value: New value for the block
            
        Returns:
            True if successful
        """
        if self._letta_client is None or self._agent_id is None:
            logger.warning("[MemoryOrchestrator] Letta not configured")
            return False
        
        try:
            self._letta_client.agents.blocks.update(
                agent_id=self._agent_id,
                block_label=block_label,
                value=value,
            )
            return True
        except Exception as e:
            logger.error(f"[MemoryOrchestrator] Core update failed: {e}")
            return False
    
    def get_core_memory(self, block_label: str) -> Optional[str]:
        """Get a Letta core memory block value."""
        if self._letta_client is None or self._agent_id is None:
            return None
        
        try:
            block = self._letta_client.agents.blocks.retrieve(
                agent_id=self._agent_id,
                block_label=block_label,
            )
            return block.value if block else None
        except Exception as e:
            logger.error(f"[MemoryOrchestrator] Core retrieve failed: {e}")
            return None
    
    # === Configuration ===
    
    def set_callbacks(
        self,
        on_store: Optional[Callable] = None,
        on_retrieve: Optional[Callable] = None,
    ) -> None:
        """Set callback functions for memory operations."""
        self._on_store_callback = on_store
        self._on_retrieve_callback = on_retrieve
    
    def configure_letta(self, client, agent_id: str) -> None:
        """Configure Letta client for core memory operations."""
        self._letta_client = client
        self._agent_id = agent_id
    
    # === Status ===
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        return {
            **self._stats,
            "initialized": self._initialized,
            "auto_consolidate": self._auto_consolidate,
            "consolidation_threshold": self._consolidation_threshold,
        }
    
    @property
    def status(self) -> Dict[str, Any]:
        """Get full orchestrator status."""
        if not self._ensure_initialized():
            return {"initialized": False}
        
        return {
            "initialized": True,
            "stats": self.stats,
            "working_memory": self._working_memory.status,
            "ltm_connected": self._memory_manager.is_qdrant_connected(),
            "ltm_stats": self._memory_manager.get_memory_stats(),
            "letta_configured": self._letta_client is not None,
        }


# Global orchestrator instance
_global_orchestrator: Optional[MemoryOrchestrator] = None


def get_orchestrator() -> MemoryOrchestrator:
    """Get or create global orchestrator instance."""
    global _global_orchestrator
    if _global_orchestrator is None:
        _global_orchestrator = MemoryOrchestrator()
    return _global_orchestrator


# === Convenience Functions ===

def remember(content: str, importance: float = 0.5, **kwargs) -> MemoryResponse:
    """Quick function to store a memory."""
    return get_orchestrator().store(content, importance=importance, **kwargs)


def recall(query: str, **kwargs) -> MemoryResponse:
    """Quick function to retrieve memories."""
    return get_orchestrator().retrieve(query, **kwargs)


def get_context(query: str, max_tokens: int = 2000) -> str:
    """Quick function to get formatted context."""
    return get_orchestrator().retrieve_context(query, max_tokens)
