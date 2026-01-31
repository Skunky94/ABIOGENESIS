"""
Test Suite for Extended Memory Blocks Integration

Tests:
- Memory block creation (episodic, semantic, procedural, emotional)
- Qdrant integration
- Letta block configuration
- Memory retrieval

Author: ABIOGENESIS Team
Version: 1.0.0
Date: 2026-01-31
"""

import sys
import os
import time
import uuid
from typing import List

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from memory.memory_blocks import (
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
from memory.qdrant_manager import QdrantManager, get_manager

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_memory_block_creation():
    """Test creation of different memory block types"""
    logger.info("=" * 60)
    logger.info("TEST: Memory Block Creation")
    logger.info("=" * 60)
    
    # Test basic MemoryBlock
    basic = MemoryBlock(
        title="Test Memory",
        content="This is a test memory content",
        memory_type=MemoryType.EPISODIC,
        importance=0.8,
    )
    assert basic.id is not None
    assert basic.title == "Test Memory"
    assert basic.memory_type == MemoryType.EPISODIC
    logger.info("✓ Basic MemoryBlock created")
    
    # Test EpisodicMemoryBlock
    episodic = EpisodicMemoryBlock(
        title="First Conversation",
        content="User asked about AI capabilities",
        event_type="conversation",
        context="Initial setup session",
        participants=["user", "scarlet"],
        emotional_tone="positive",
    )
    assert episodic.event_type == "conversation"
    assert "user" in episodic.participants
    logger.info("✓ EpisodicMemoryBlock created")
    
    # Test SemanticMemoryBlock
    semantic = SemanticMemoryBlock(
        title="User is Developer",
        content="The user works as a software developer",
        concept_category="preference",
        confidence=0.9,
        source="direct_conversation",
    )
    assert semantic.concept_category == "preference"
    assert semantic.confidence == 0.9
    logger.info("✓ SemanticMemoryBlock created")
    
    # Test ProceduralMemoryBlock
    procedural = ProceduralMemoryBlock(
        skill_name="Docker Setup",
        content="How to set up Docker containers",
        procedure_type="technical",
        steps=["Create docker-compose.yml", "Configure services", "Run containers"],
        prerequisites=["Docker installed"],
    )
    assert len(procedural.steps) == 3
    assert "Docker installed" in procedural.prerequisites
    logger.info("✓ ProceduralMemoryBlock created")
    
    # Test EmotionalMemoryBlock
    emotional = EmotionalMemoryBlock(
        trigger="Precise technical questions",
        content="User appreciates detailed technical answers",
        response_type="preference",
        intensity=0.7,
    )
    assert emotional.trigger == "Precise technical questions"
    assert emotional.intensity == 0.7
    logger.info("✓ EmotionalMemoryBlock created")
    
    return True


def test_memory_serialization():
    """Test memory block serialization"""
    logger.info("=" * 60)
    logger.info("TEST: Memory Serialization")
    logger.info("=" * 60)
    
    memory = EpisodicMemoryBlock(
        title="Test Conversation",
        content="A significant conversation about AI",
        event_type="conversation",
        importance=0.9,
        tags=["AI", "conversation", "important"],
    )
    
    # Test to_dict
    data = memory.to_dict()
    assert data["title"] == "Test Conversation"
    assert data["memory_type"] == "episodic"
    assert data["importance"] == 0.9
    assert "AI" in data["tags"]
    logger.info("✓ to_dict() works correctly")
    
    # Test from_dict
    restored = MemoryBlock.from_dict(data)
    assert restored.title == "Test Conversation"
    assert restored.memory_type == MemoryType.EPISODIC
    assert restored.importance == 0.9
    logger.info("✓ from_dict() works correctly")
    
    return True


def test_memory_blocks_configuration():
    """Test Letta memory block configurations"""
    logger.info("=" * 60)
    logger.info("TEST: Memory Blocks Configuration")
    logger.info("=" * 60)
    
    # Test EXTENDED_MEMORY_BLOCKS (4 new blocks)
    assert len(EXTENDED_MEMORY_BLOCKS) == 4
    labels = [b["label"] for b in EXTENDED_MEMORY_BLOCKS]
    assert "episodic_memory" in labels
    assert "knowledge_base" in labels
    assert "skills_registry" in labels
    assert "emotional_patterns" in labels
    logger.info(f"✓ EXTENDED_MEMORY_BLOCKS: {len(EXTENDED_MEMORY_BLOCKS)} blocks")
    for block in EXTENDED_MEMORY_BLOCKS:
        logger.info(f"  - {block['label']}: limit={block['limit']}")
    
    # Test ALL_MEMORY_BLOCKS (5 original + 4 extended)
    assert len(ALL_MEMORY_BLOCKS) == 9
    all_labels = [b["label"] for b in ALL_MEMORY_BLOCKS]
    expected = ["persona", "human", "goals", "session_context", "constraints",
                "episodic_memory", "knowledge_base", "skills_registry", "emotional_patterns"]
    assert all_labels == expected
    logger.info(f"✓ ALL_MEMORY_BLOCKS: {len(ALL_MEMORY_BLOCKS)} total blocks")
    
    # Test constraints block is read-only
    constraints_block = next(b for b in ALL_MEMORY_BLOCKS if b["label"] == "constraints")
    assert constraints_block.get("read_only", False) == True
    logger.info("✓ Constraints block is read-only")
    
    return True


def test_memory_manager_qdrant_integration():
    """Test MemoryManager with Qdrant integration"""
    logger.info("=" * 60)
    logger.info("TEST: MemoryManager + Qdrant Integration")
    logger.info("=" * 60)
    
    # Get Qdrant manager
    qdrant = get_manager()
    assert qdrant.is_connected()
    logger.info("✓ Connected to Qdrant")
    
    # Create memory manager
    manager = MemoryManager(qdrant_manager=qdrant)
    assert manager.is_qdrant_connected()
    logger.info("✓ MemoryManager initialized")
    
    # Create and store episodic memory
    episodic = manager.create_episodic_memory(
        title="First Chat Session",
        content="Initial conversation about Scarlet's purpose and capabilities",
        event_type="conversation",
        context="Project ABIOGENESIS setup",
        participants=["developer"],
        importance=0.9,
        emotional_tone="positive",
        tags=["setup", "important", "first"],
    )
    logger.info(f"✓ Created episodic memory: {episodic.id}")
    
    # Create and store semantic memory
    semantic = manager.create_semantic_memory(
        title="Developer Preferences",
        content="Developer prefers detailed technical explanations",
        concept_category="preference",
        confidence=0.85,
        source="conversation_analysis",
        importance=0.7,
        tags=["preference", "developer"],
    )
    logger.info(f"✓ Created semantic memory: {semantic.id}")
    
    # Create and store procedural memory
    procedural = manager.create_procedural_memory(
        skill_name="Memory Consolidation",
        content="Process of extracting and storing important conversation insights",
        procedure_type="cognitive",
        steps=[
            "Analyze conversation for key insights",
            "Extract episodic events",
            "Identify learned facts",
            "Store in appropriate memory system",
        ],
        prerequisites=["Sleep-time system active"],
        importance=0.8,
        tags=["skill", "memory", "consolidation"],
    )
    logger.info(f"✓ Created procedural memory: {procedural.id}")
    
    # Create and store emotional memory
    emotional = manager.create_emotional_memory(
        trigger="Technical questions",
        content="Positive response to detailed technical questions",
        response_type="joy",
        intensity=0.6,
        context_pattern="Developer asking about implementation",
        importance=0.5,
    )
    logger.info(f"✓ Created emotional memory: {emotional.id}")
    
    # Test memory retrieval
    logger.info("\n--- Testing Memory Retrieval ---")
    
    # Retrieve episodic memories (with query for semantic search)
    episodic_memories = manager.retrieve_memories(
        MemoryType.EPISODIC,
        query="conversation",  # Use query for semantic search
        limit=5,
    )
    logger.info(f"✓ Retrieved {len(episodic_memories)} episodic memories with query")
    
    # Retrieve semantic memories
    semantic_memories = manager.retrieve_memories(
        MemoryType.SEMANTIC,
        query="preference",  # Use query for semantic search
        limit=5,
    )
    logger.info(f"✓ Retrieved {len(semantic_memories)} semantic memories with query")
    
    # Retrieve procedural memories
    procedural_memories = manager.retrieve_memories(
        MemoryType.PROCEDURAL,
        query="memory",  # Use query for semantic search
        limit=5,
    )
    logger.info(f"✓ Retrieved {len(procedural_memories)} procedural memories with query")
    
    # Test stats
    stats = manager.get_memory_stats()
    logger.info(f"✓ Memory stats: {stats}")
    
    # Test importance filtering
    important_memories = manager.retrieve_memories(
        MemoryType.EPISODIC,
        min_importance=0.8,
    )
    logger.info(f"✓ High importance memories (≥0.8): {len(important_memories)}")
    
    # Test tag filtering
    tagged_memories = manager.retrieve_memories(
        MemoryType.EPISODIC,
        tags=["important"],
    )
    logger.info(f"✓ Tagged memories (important): {len(tagged_memories)}")
    
    return True


def test_memory_types_enum():
    """Test MemoryType enum values"""
    logger.info("=" * 60)
    logger.info("TEST: MemoryType Enum")
    logger.info("=" * 60)
    
    assert MemoryType.EPISODIC.value == "episodic"
    assert MemoryType.SEMANTIC.value == "semantic"
    assert MemoryType.PROCEDURAL.value == "procedural"
    assert MemoryType.EMOTIONAL.value == "emotional"
    
    logger.info("✓ All MemoryType enum values correct")
    
    return True


def run_all_tests():
    """Run all tests"""
    logger.info("\n" + "=" * 60)
    logger.info("EXTENDED MEMORY BLOCKS TEST SUITE")
    logger.info("=" * 60 + "\n")
    
    tests = [
        ("Memory Block Creation", test_memory_block_creation),
        ("Memory Serialization", test_memory_serialization),
        ("Memory Blocks Configuration", test_memory_blocks_configuration),
        ("MemoryType Enum", test_memory_types_enum),
        ("MemoryManager + Qdrant", test_memory_manager_qdrant_integration),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, "PASSED"))
        except Exception as e:
            logger.error(f"✗ {name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, f"FAILED: {e}"))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    passed = sum(1 for _, r in results if r == "PASSED")
    total = len(results)
    
    for name, result in results:
        status = "✓" if result == "PASSED" else "✗"
        logger.info(f"{status} {name}: {result}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
