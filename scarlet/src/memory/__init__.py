"""
Memory Management Module for Scarlet

This package contains:
- qdrant_manager: Qdrant vector database operations
- embedding_manager: Embedding generation using BGE-m3
- memory_blocks: Extended memory block definitions
- memory_retriever: Memory search and retrieval tool
- working_memory: Redis-based working memory
- memory_orchestrator: Central memory controller

Author: ABIOGENESIS Team
Version: 2.0.0
Date: 2026-02-01
"""

from .qdrant_manager import (
    QdrantManager,
    QdrantConfig,
    CollectionConfig,
    CollectionType,
    COLLECTION_CONFIGS,
    get_manager,
    setup_memory_collections,
)

from .embedding_manager import (
    EmbeddingManager,
    EmbeddingResult,
    get_embedding_manager,
)

from .memory_blocks import (
    MemoryType,
    MemoryBlock,
    EpisodicMemoryBlock,
    SemanticMemoryBlock,
    ProceduralMemoryBlock,
    EmotionalMemoryBlock,
    MemoryManager,
    EXTENDED_MEMORY_BLOCKS,
    ALL_MEMORY_BLOCKS,
)

from .memory_retriever import (
    MemoryRetriever,
    RetrievalResult,
    RetrievalStrategy,
    get_retriever,
    memory_search_tool,
    memory_context_tool,
    MEMORY_SEARCH_TOOL,
)

from .working_memory import (
    WorkingMemory,
    WorkingMemoryItem,
    WorkingMemoryItemType,
    get_working_memory,
)

from .memory_orchestrator import (
    MemoryOrchestrator,
    MemoryRequest,
    MemoryResponse,
    MemoryOperation,
    ContentCategory,
    ConsolidationResult,
    get_orchestrator,
    remember,
    recall,
    get_context,
)

__all__ = [
    # Qdrant
    "QdrantManager",
    "QdrantConfig",
    "CollectionConfig",
    "CollectionType",
    "COLLECTION_CONFIGS",
    "get_manager",
    "setup_memory_collections",
    # Embeddings
    "EmbeddingManager",
    "EmbeddingResult",
    "get_embedding_manager",
    # Memory Blocks
    "MemoryType",
    "MemoryBlock",
    "EpisodicMemoryBlock",
    "SemanticMemoryBlock",
    "ProceduralMemoryBlock",
    "EmotionalMemoryBlock",
    "MemoryManager",
    "EXTENDED_MEMORY_BLOCKS",
    "ALL_MEMORY_BLOCKS",
    # Memory Retriever
    "MemoryRetriever",
    "RetrievalResult",
    "RetrievalStrategy",
    "get_retriever",
    "memory_search_tool",
    "memory_context_tool",
    "MEMORY_SEARCH_TOOL",
    # Working Memory
    "WorkingMemory",
    "WorkingMemoryItem",
    "WorkingMemoryItemType",
    "get_working_memory",
    # Orchestrator
    "MemoryOrchestrator",
    "MemoryRequest",
    "MemoryResponse",
    "MemoryOperation",
    "ContentCategory",
    "ConsolidationResult",
    "get_orchestrator",
    "remember",
    "recall",
    "get_context",
]
