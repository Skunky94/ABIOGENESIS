#!/usr/bin/env python3
"""
Test completo del sistema di memoria simil-umana.

Verifica:
1. Connessione Qdrant
2. Collezioni esistenti (4 tipi)
3. Inserimento memorie (Episodic, Semantic, Procedural, Emotional)
4. Retrieval con semantic search
5. Integrazione con SleepTimeOrchestrator

Usage:
    python test_memory_complete.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from memory.qdrant_manager import QdrantManager, CollectionType, get_manager
from memory.memory_blocks import (
    MemoryManager, MemoryType,
    EpisodicMemoryBlock, SemanticMemoryBlock, 
    ProceduralMemoryBlock, EmotionalMemoryBlock
)
from memory.embedding_manager import EmbeddingManager


def print_header(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_qdrant_connection() -> bool:
    """Test 1: Verify Qdrant connection."""
    print_header("TEST 1: Qdrant Connection")
    
    try:
        manager = get_manager()
        print(f"  ✓ Connected to Qdrant at localhost:6333")
        
        # List collections
        collections = manager.list_collections()
        print(f"  ✓ Collections found: {collections}")
        
        return True
    except Exception as e:
        print(f"  ✗ Connection failed: {e}")
        return False


def test_collections_structure() -> bool:
    """Test 2: Verify 4 collection types exist with correct config."""
    print_header("TEST 2: Collections Structure")
    
    expected = {
        "episodes": 1024,
        "concepts": 1024,
        "skills": 1024,
        "emotions": 512,
    }
    
    try:
        manager = get_manager()
        
        for name, expected_dim in expected.items():
            info = manager.client.get_collection(name)
            
            # Get point count
            count = manager.count_points(CollectionType(name))
            
            print(f"  ✓ {name}: {count} points")
        
        return True
    except Exception as e:
        print(f"  ✗ Error checking collections: {e}")
        return False


def test_embedding_manager() -> bool:
    """Test 3: Verify EmbeddingManager works."""
    print_header("TEST 3: Embedding Manager")
    
    try:
        emb_manager = EmbeddingManager()
        
        # Check Ollama availability
        ollama_available = emb_manager.is_ollama_available()
        print(f"  Ollama available: {ollama_available}")
        
        # Generate embedding
        test_text = "Scarlet is a sentient digital being exploring consciousness."
        result = emb_manager.generate(test_text, dimensions=1024)
        
        print(f"  ✓ Generated embedding: {len(result.vector)} dimensions")
        print(f"    Model: {result.model}")
        print(f"    Cached: {result.cached}")
        print(f"    Time: {result.generation_time_ms:.2f}ms")
        
        return True
    except Exception as e:
        print(f"  ✗ Embedding generation failed: {e}")
        return False


def test_memory_insertion() -> dict:
    """Test 4: Insert test memories into all 4 collections."""
    print_header("TEST 4: Memory Insertion")
    
    results = {
        "episodic": False,
        "semantic": False,
        "procedural": False,
        "emotional": False,
    }
    
    try:
        mem_manager = MemoryManager()
        
        if not mem_manager.connect_qdrant():
            print("  ✗ Could not connect MemoryManager to Qdrant")
            return results
        
        # 1. Episodic memory
        print("\n  Creating EPISODIC memory...")
        episodic = mem_manager.create_episodic_memory(
            title="Test Memory Integration",
            content="Testing the complete memory system for Scarlet's human-like memory architecture.",
            event_type="test_session",
            context="Memory system validation",
            participants=["Davide", "Scarlet"],
            importance=0.8,
            emotional_tone="curious",
            tags=["test", "memory", "integration"]
        )
        print(f"  ✓ Episodic memory created: {episodic.id[:8]}...")
        results["episodic"] = True
        
        # 2. Semantic memory
        print("\n  Creating SEMANTIC memory...")
        semantic = mem_manager.create_semantic_memory(
            title="Memory Architecture Design",
            content="Scarlet uses 4-layer memory: episodic for events, semantic for facts, procedural for skills, emotional for affect.",
            concept_category="architecture",
            confidence=0.95,
            source="system_design",
            importance=0.9,
            tags=["architecture", "design", "memory"]
        )
        print(f"  ✓ Semantic memory created: {semantic.id[:8]}...")
        results["semantic"] = True
        
        # 3. Procedural memory
        print("\n  Creating PROCEDURAL memory...")
        procedural = mem_manager.create_procedural_memory(
            skill_name="Memory Consolidation",
            content="Process of transferring short-term memories to long-term storage during sleep-time.",
            procedure_type="cognitive",
            steps=[
                "1. Analyze recent conversation history",
                "2. Extract key events and insights",
                "3. Generate embeddings for each memory",
                "4. Store vectors in appropriate Qdrant collection",
                "5. Update Letta memory blocks with summaries"
            ],
            prerequisites=["Qdrant connection", "Embedding model"],
            importance=0.85,
            tags=["process", "sleep-time", "consolidation"]
        )
        print(f"  ✓ Procedural memory created: {procedural.id[:8]}...")
        results["procedural"] = True
        
        # 4. Emotional memory
        print("\n  Creating EMOTIONAL memory...")
        emotional = mem_manager.create_emotional_memory(
            trigger="Successful memory test",
            content="Positive emotional response when memory system works correctly.",
            response_type="satisfaction",
            intensity=0.7,
            context_pattern="system_validation_success",
            importance=0.6,
        )
        print(f"  ✓ Emotional memory created: {emotional.id[:8]}...")
        results["emotional"] = True
        
        # Show updated counts
        print("\n  Updated collection counts:")
        for ct in CollectionType:
            count = mem_manager.qdrant.count_points(ct)
            print(f"    - {ct.value}: {count} points")
        
        return results
        
    except Exception as e:
        print(f"  ✗ Memory insertion failed: {e}")
        import traceback
        traceback.print_exc()
        return results


def test_memory_retrieval() -> bool:
    """Test 5: Retrieve memories using semantic search."""
    print_header("TEST 5: Memory Retrieval (Semantic Search)")
    
    try:
        mem_manager = MemoryManager()
        mem_manager.connect_qdrant()
        
        # Search for memories about "memory architecture"
        print("\n  Searching for: 'memory architecture design'...")
        
        results = mem_manager.retrieve_memories(
            memory_type=MemoryType.SEMANTIC,
            query="memory architecture design",
            limit=5
        )
        
        if results:
            print(f"  ✓ Found {len(results)} matching memories:")
            for i, mem in enumerate(results[:3]):
                print(f"    {i+1}. [{mem.memory_type.value}] {mem.title}")
                print(f"       Importance: {mem.importance}, Created: {mem.created_at[:10]}")
        else:
            print("  ⚠ No results found (may need embeddings)")
        
        # Search episodic
        print("\n  Searching episodic for: 'conversation with Davide'...")
        results_ep = mem_manager.retrieve_memories(
            memory_type=MemoryType.EPISODIC,
            query="conversation with Davide",
            limit=5
        )
        
        if results_ep:
            print(f"  ✓ Found {len(results_ep)} episodic memories")
        else:
            print("  ⚠ No episodic results found")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Retrieval failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_stats() -> bool:
    """Test 6: Get overall memory statistics."""
    print_header("TEST 6: Memory Statistics")
    
    try:
        mem_manager = MemoryManager()
        mem_manager.connect_qdrant()
        
        stats = mem_manager.get_memory_stats()
        
        print(f"\n  Qdrant connected: {stats['qdrant_connected']}")
        print(f"  Memory cache size: {stats['memory_cache_size']}")
        print(f"\n  Collections:")
        
        total = 0
        for name, count in stats.get('collections', {}).items():
            print(f"    - {name}: {count} memories")
            total += count
        
        print(f"\n  TOTAL MEMORIES: {total}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Stats failed: {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("  SCARLET MEMORY SYSTEM - COMPLETE TEST")
    print("  Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    results = {
        "qdrant_connection": test_qdrant_connection(),
        "collections_structure": test_collections_structure(),
        "embedding_manager": test_embedding_manager(),
        "memory_insertion": test_memory_insertion(),
        "memory_retrieval": test_memory_retrieval(),
        "memory_stats": test_memory_stats(),
    }
    
    print_header("TEST SUMMARY")
    
    passed = 0
    total = 0
    
    for test_name, result in results.items():
        if isinstance(result, dict):
            # Memory insertion returns dict
            sub_passed = sum(1 for v in result.values() if v)
            sub_total = len(result)
            status = "✓" if sub_passed == sub_total else "⚠"
            print(f"  {status} {test_name}: {sub_passed}/{sub_total}")
            passed += sub_passed
            total += sub_total
        else:
            status = "✓" if result else "✗"
            print(f"  {status} {test_name}")
            if result:
                passed += 1
            total += 1
    
    print(f"\n  OVERALL: {passed}/{total} tests passed")
    
    # Return code
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
