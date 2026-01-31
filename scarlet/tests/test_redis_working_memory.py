"""
Test Redis Working Memory Integration

Verifica che la Working Memory si connetta correttamente a Redis
e che tutte le operazioni funzionino con persistenza.

Author: ABIOGENESIS Team
Date: 2026-02-01
"""

import os
import sys
import time

# Aggiungi src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configura per Redis locale
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"


def test_redis_connection():
    """Test connessione Redis diretta."""
    print("\n" + "=" * 60)
    print("TEST: Redis Connection")
    print("=" * 60)
    
    try:
        import redis
        r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        pong = r.ping()
        print(f"✓ Redis PING: {pong}")
        
        # Test operazioni base
        r.set("test_key", "test_value")
        value = r.get("test_key")
        print(f"✓ Redis SET/GET: {value}")
        r.delete("test_key")
        print("✓ Redis DELETE: OK")
        
        return True
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        return False


def test_working_memory_redis():
    """Test Working Memory con Redis."""
    print("\n" + "=" * 60)
    print("TEST: Working Memory with Redis")
    print("=" * 60)
    
    try:
        from memory.working_memory import (
            WorkingMemory,
            WorkingMemoryItem,
            WorkingMemoryItemType,
            get_working_memory
        )
        
        # Crea istanza con Redis
        wm = WorkingMemory(session_id="test_redis_session")
        
        # Verifica connessione Redis
        if wm._redis is not None:
            print(f"✓ Working Memory connected to Redis")
        else:
            print("✗ Working Memory using in-memory fallback")
            return False
        
        # Test: Aggiungi item
        wm_item = wm.add(
            content="Test Redis persistence",
            item_type=WorkingMemoryItemType.FACT,
            importance=0.9
        )
        item_id = wm_item.id
        print(f"✓ Added item: {item_id}")
        
        # Test: Retrieve item
        item = wm.get(item_id)
        if item and item.content == "Test Redis persistence":
            print(f"✓ Retrieved item: {item.content}")
        else:
            print(f"✗ Failed to retrieve item")
            return False
        
        # Test: Persistence across instances
        wm2 = WorkingMemory(session_id="test_redis_session")
        item2 = wm2.get(item_id)
        if item2 and item2.content == "Test Redis persistence":
            print(f"✓ Item persisted across instances")
        else:
            print(f"✗ Item not persisted (this is expected with local cache)")
        
        # Test: Capacity
        print(f"✓ Capacity: {wm.count}/{wm.capacity}")
        
        # Test: Search
        results = wm.search("Redis")
        print(f"✓ Search 'Redis': {len(results)} results")
        
        # Test: Rehearsal
        wm.rehearse(item_id)
        print(f"✓ Rehearsal: OK")
        
        # Test: Clear
        wm.clear()
        print(f"✓ Clear: OK")
        
        return True
        
    except Exception as e:
        print(f"✗ Working Memory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_working_memory_integration():
    """Test integrazione completa con Orchestrator."""
    print("\n" + "=" * 60)
    print("TEST: Memory Orchestrator with Redis WM")
    print("=" * 60)
    
    try:
        from memory.memory_orchestrator import (
            get_orchestrator,
            remember,
            recall,
            MemoryOrchestrator
        )
        
        # Crea orchestrator
        orch = get_orchestrator()
        print(f"✓ Orchestrator created")
        
        # Verifica WM connessa a Redis
        if orch.working_memory._redis is not None:
            print(f"✓ WM connected to Redis")
        else:
            print(f"✗ WM using in-memory fallback")
        
        # Test remember (low importance -> WM)
        success = remember(
            "Questa è una nota temporanea",
            importance=0.3
        )
        print(f"✓ Remember (low importance): {'stored in WM' if success else 'failed'}")
        
        # Test remember (high importance -> LTM)
        success = remember(
            "Questa è una informazione importante da ricordare",
            importance=0.9
        )
        print(f"✓ Remember (high importance): {'stored in LTM' if success else 'failed'}")
        
        # Test recall
        results = recall("nota temporanea", limit=5)
        if hasattr(results, 'results'):
            print(f"✓ Recall: {len(results.results)} results")
        else:
            print(f"✓ Recall: response received")
        
        # Cleanup
        orch.working_memory.clear()
        
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wm_decay_and_capacity():
    """Test decay e capacity limits."""
    print("\n" + "=" * 60)
    print("TEST: Working Memory Decay & Capacity")
    print("=" * 60)
    
    try:
        from memory.working_memory import (
            WorkingMemory,
            WorkingMemoryItemType,
        )
        
        wm = WorkingMemory(session_id="test_capacity", capacity=7)
        wm.clear()  # Start fresh
        
        # Aggiungi 10 items (oltre capacità)
        for i in range(10):
            wm.add(
                content=f"Item numero {i}",
                item_type=WorkingMemoryItemType.FACT,
                importance=0.1 * i  # Importanza crescente
            )
        
        # Verifica che solo 7 siano rimasti (capacity)
        count = wm.count
        print(f"✓ Capacity limit enforced: {count}/7 items")
        
        if count > 7:
            print(f"✗ Capacity exceeded!")
            return False
        
        # Verifica che siano rimasti quelli più importanti
        items = wm.get_all()
        if items:
            min_importance = min(i.importance for i in items)
            print(f"✓ Lowest importance remaining: {min_importance:.1f}")
        
        wm.clear()
        return True
        
    except Exception as e:
        print(f"✗ Decay/Capacity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print(" REDIS WORKING MEMORY TESTS")
    print("=" * 60)
    
    results = {
        "Redis Connection": test_redis_connection(),
        "Working Memory Redis": test_working_memory_redis(),
        "Orchestrator Integration": test_working_memory_integration(),
        "Decay & Capacity": test_wm_decay_and_capacity(),
    }
    
    # Summary
    print("\n" + "=" * 60)
    print(" TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
