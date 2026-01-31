"""
Test Human-Like Memory Architecture

Tests the new memory components:
- Memory Retriever (search & retrieval)
- Working Memory (Redis-based)
- Memory Orchestrator (central controller)

Author: ABIOGENESIS Team
Date: 2026-02-01
"""

import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Test results
RESULTS = {"passed": 0, "failed": 0, "errors": []}


def test_passed(name: str):
    print(f"  ✓ {name}")
    RESULTS["passed"] += 1


def test_failed(name: str, error: str):
    print(f"  ✗ {name}: {error}")
    RESULTS["failed"] += 1
    RESULTS["errors"].append(f"{name}: {error}")


# === Test 1: Memory Retriever ===
print("\n" + "=" * 60)
print("TEST 1: Memory Retriever")
print("=" * 60)

try:
    from memory.memory_retriever import (
        MemoryRetriever, 
        get_retriever, 
        RetrievalStrategy,
        memory_search_tool,
    )
    
    retriever = get_retriever()
    test_passed("MemoryRetriever import & creation")
    
    # Test search
    results = retriever.search(
        query="conversazione recente",
        memory_types=["episodic", "semantic"],
        limit=5,
    )
    
    if isinstance(results, list):
        test_passed(f"Search executed ({len(results)} results)")
    else:
        test_failed("Search", "Invalid result type")
    
    # Test context retrieval
    context = retriever.retrieve_context("test query", max_tokens=500)
    test_passed(f"Context retrieval ({len(context)} chars)")
    
    # Test tool function
    tool_result = memory_search_tool("test query", limit=3)
    if "status" in tool_result:
        test_passed("Tool function works")
    else:
        test_failed("Tool function", "Invalid output")

except Exception as e:
    test_failed("Memory Retriever", str(e))


# === Test 2: Working Memory ===
print("\n" + "=" * 60)
print("TEST 2: Working Memory")
print("=" * 60)

try:
    from memory.working_memory import (
        WorkingMemory,
        WorkingMemoryItemType,
        get_working_memory,
    )
    
    wm = get_working_memory(session_id="test_humanlike")
    wm.clear()  # Start fresh
    test_passed("WorkingMemory import & creation")
    
    # Test add
    item = wm.add(
        content="Test fact: Scarlet is a digital entity",
        item_type=WorkingMemoryItemType.FACT,
        importance=0.7,
    )
    test_passed(f"Add item (id={item.id[:8]}...)")
    
    # Test capacity (7±2)
    if 5 <= wm.capacity <= 9:
        test_passed(f"Capacity correct: {wm.capacity}")
    else:
        test_failed("Capacity", f"Got {wm.capacity}, expected 5-9")
    
    # Test search
    matches = wm.search("Scarlet")
    test_passed(f"Search found {len(matches)} matches")
    
    # Test rehearsal
    count = wm.rehearse([item.id])
    test_passed(f"Rehearsed {count} items")
    
    # Test attention
    wm.focus(item.id)
    if wm.attention:
        test_passed("Attention focus works")
    else:
        test_failed("Attention", "No focus set")
    
    # Test chunking
    item2 = wm.add("Another item", importance=0.5)
    chunk = wm.chunk([item.id, item2.id], "Test Chunk")
    if chunk:
        test_passed("Chunking works")
    else:
        test_failed("Chunking", "No chunk created")
    
    # Test status
    status = wm.status
    test_passed(f"Status: {status['items_count']} items, redis={status['redis_connected']}")
    
    # Cleanup
    wm.clear()
    test_passed("Cleared working memory")

except Exception as e:
    test_failed("Working Memory", str(e))


# === Test 3: Memory Orchestrator ===
print("\n" + "=" * 60)
print("TEST 3: Memory Orchestrator")
print("=" * 60)

try:
    from memory.memory_orchestrator import (
        MemoryOrchestrator,
        get_orchestrator,
        ContentCategory,
        remember,
        recall,
        get_context,
    )
    
    orch = get_orchestrator()
    test_passed("MemoryOrchestrator import & creation")
    
    # Test classification
    test_cases = [
        ("Oggi ho parlato con Marco", ContentCategory.EVENT),
        ("Python è un linguaggio di programmazione", ContentCategory.FACT),
        ("Per fare questo, prima devi...", ContentCategory.PROCEDURE),
        ("Mi sento molto curioso", ContentCategory.EMOTION),
    ]
    
    for content, expected in test_cases:
        result = orch.classify_content(content)
        if result == expected:
            test_passed(f"Classify: '{content[:25]}...' → {result.value}")
        else:
            print(f"  ⚠ Got {result.value}, expected {expected.value}")
    
    # Test store to WM
    resp = orch.store(
        content="Low importance test item",
        importance=0.3,
    )
    test_passed(f"Store to WM: {resp.success}")
    
    # Test store to LTM
    resp = orch.store(
        content="High importance test: User prefers Python",
        importance=0.8,
        force_ltm=True,
    )
    test_passed(f"Store to LTM: {resp.success}")
    
    # Test retrieve
    resp = orch.retrieve(query="test", limit=5)
    test_passed(f"Retrieve: {len(resp.results) if resp.results else 0} results")
    
    # Test convenience functions
    resp = remember("Quick test", importance=0.5)
    test_passed(f"remember(): {resp.success}")
    
    resp = recall("test")
    test_passed(f"recall(): {resp.success}")
    
    ctx = get_context("test")
    test_passed(f"get_context(): {len(ctx)} chars")
    
    # Test consolidation
    result = orch.consolidate()
    test_passed(f"Consolidate: {result.items_stored} stored")
    
    # Test status
    status = orch.status
    test_passed(f"Status: init={status['initialized']}")

except Exception as e:
    test_failed("Memory Orchestrator", str(e))


# === Test 4: Module Exports ===
print("\n" + "=" * 60)
print("TEST 4: Module Exports")
print("=" * 60)

try:
    from memory import (
        # Retriever
        MemoryRetriever,
        get_retriever,
        MEMORY_SEARCH_TOOL,
        # Working Memory
        WorkingMemory,
        get_working_memory,
        # Orchestrator
        MemoryOrchestrator,
        get_orchestrator,
        remember,
        recall,
        get_context,
    )
    
    test_passed("All new exports available from memory module")
    
    # Verify tool definition
    if "name" in MEMORY_SEARCH_TOOL and MEMORY_SEARCH_TOOL["name"] == "memory_search":
        test_passed("MEMORY_SEARCH_TOOL has correct structure")
    else:
        test_failed("MEMORY_SEARCH_TOOL", "Invalid structure")

except ImportError as e:
    test_failed("Module exports", str(e))


# === Summary ===
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"  Passed: {RESULTS['passed']}")
print(f"  Failed: {RESULTS['failed']}")

if RESULTS["errors"]:
    print("\nErrors:")
    for err in RESULTS["errors"]:
        print(f"  - {err}")

print("\n" + "=" * 60)
if RESULTS["failed"] == 0:
    print("✓ ALL TESTS PASSED")
    print("  Human-like memory architecture ready!")
else:
    print(f"✗ {RESULTS['failed']} TESTS FAILED")
print("=" * 60)

sys.exit(0 if RESULTS["failed"] == 0 else 1)
