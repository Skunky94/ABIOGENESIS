"""
Memory Management Module for Scarlet

This package contains:
- qdrant_manager: Qdrant vector database operations
- embedding_manager: Embedding generation using BGE-m3
- memory_blocks: Extended memory block definitions
- memory_orchestrator: Central memory controller
- consolidation: Sleep-time memory consolidation

Author: ABIOGENESIS Team
Version: 1.0.0
Date: 2026-01-31
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
]
