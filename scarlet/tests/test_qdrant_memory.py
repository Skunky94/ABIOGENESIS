"""
Test Suite for Qdrant Memory Infrastructure

Tests:
- Qdrant connection
- Collection creation
- Vector operations (upsert, search, delete)
- Health checks

Author: ABIOGENESIS Team
Version: 1.0.0
Date: 2026-01-31
"""

import sys
import os
import time
import uuid
import logging
from typing import List

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from qdrant_client.models import PointStruct

from memory.qdrant_manager import (
    QdrantManager,
    QdrantConfig,
    CollectionType,
    get_manager,
    setup_memory_collections,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_test_vector(dim: int = 1024) -> List[float]:
    """Generate a random vector for testing"""
    import random
    return [random.uniform(-1, 1) for _ in range(dim)]


def test_connection():
    """Test Qdrant connection"""
    logger.info("=" * 60)
    logger.info("TEST: Qdrant Connection")
    logger.info("=" * 60)
    
    manager = QdrantManager()
    
    # Test connection
    connected = manager.connect(max_retries=3)
    assert connected, "Failed to connect to Qdrant"
    logger.info("✓ Qdrant connection successful")
    
    # Test health check
    health = manager.health_check()
    assert health["connected"], "Health check failed"
    logger.info("✓ Health check passed")
    
    manager.disconnect()
    return True


def test_collections():
    """Test collection creation and management"""
    logger.info("=" * 60)
    logger.info("TEST: Collection Management")
    logger.info("=" * 60)
    
    manager = get_manager()
    
    # Create all collections
    results = manager.create_all_collections()
    for ct, success in results.items():
        assert success, f"Failed to create {ct.value} collection"
        logger.info(f"✓ Collection '{ct.value}' created/verified")
    
    # List collections
    collections = manager.list_collections()
    expected = [ct.value for ct in CollectionType]
    for exp in expected:
        assert exp in collections, f"Collection '{exp}' not found"
        logger.info(f"✓ '{exp}' in collection list")
    
    # Get collection info
    for ct in CollectionType:
        info = manager.get_collection_info(ct)
        assert info is not None, f"Failed to get info for {ct.value}"
        logger.info(f"✓ {ct.value}: {info['vectors_count']} vectors")
    
    return True


def test_vector_operations():
    """Test vector CRUD operations"""
    logger.info("=" * 60)
    logger.info("TEST: Vector Operations")
    logger.info("=" * 60)
    
    manager = get_manager()
    collection_type = CollectionType.EPISODES
    vector_dim = 1024
    
    # Generate test vectors
    test_vectors = [generate_test_vector(vector_dim) for _ in range(5)]
    point_ids = [str(uuid.uuid4()) for _ in range(5)]
    
    # Create points
    points = [
        PointStruct(
            id=pid,
            vector=vec,
            payload={
                "type": "test",
                "name": f"test_point_{i}",
                "timestamp": time.time(),
            }
        )
        for i, (pid, vec) in enumerate(zip(point_ids, test_vectors))
    ]
    
    # Upsert points
    success = manager.upsert_points(collection_type, points)
    assert success, "Failed to upsert points"
    logger.info(f"✓ Upserted {len(points)} points")
    
    # Wait for indexing
    time.sleep(1)
    
    # Count points
    count = manager.count_points(collection_type)
    logger.info(f"✓ Collection has {count} points")
    
    # Search
    query_vec = generate_test_vector(vector_dim)
    results = manager.search(collection_type, query_vec, limit=3)
    logger.info(f"✓ Search returned {len(results)} results")
    
    # Delete points
    success = manager.delete_points(collection_type, point_ids)
    assert success, "Failed to delete points"
    logger.info(f"✓ Deleted {len(point_ids)} points")
    
    # Verify deletion
    count_after = manager.count_points(collection_type)
    logger.info(f"✓ Collection has {count_after} points after deletion")
    
    return True


def test_different_collections():
    """Test operations on different collection types"""
    logger.info("=" * 60)
    logger.info("TEST: Different Collection Types")
    logger.info("=" * 60)
    
    manager = get_manager()
    
    for ct in CollectionType:
        # Get expected dimension from config
        from memory.qdrant_manager import COLLECTION_CONFIGS
        expected_dim = COLLECTION_CONFIGS[ct].vector_size
        
        # Generate vector with correct dimension
        test_vec = generate_test_vector(expected_dim)
        point_id = str(uuid.uuid4())
        
        point = PointStruct(
            id=point_id,
            vector=test_vec,
            payload={"type": "test", "collection": ct.value}
        )
        
        # Upsert
        success = manager.upsert_points(ct, [point])
        assert success, f"Failed to upsert to {ct.value}"
        logger.info(f"✓ Upserted to '{ct.value}' (dim={expected_dim})")
        
        # Search
        results = manager.search(ct, test_vec, limit=1)
        assert len(results) >= 1, f"No results from {ct.value}"
        logger.info(f"✓ Search in '{ct.value}' returned {len(results)} results")
        
        # Delete
        manager.delete_points(ct, [point_id])
        logger.info(f"✓ Cleaned up '{ct.value}'")
    
    return True


def test_health_check():
    """Test comprehensive health check"""
    logger.info("=" * 60)
    logger.info("TEST: Health Check")
    logger.info("=" * 60)
    
    manager = get_manager()
    health = manager.health_check()
    
    assert health["connected"], "Not connected"
    logger.info("✓ Connected")
    
    assert "collections" in health, "Missing collections info"
    logger.info(f"✓ Collections info: {health['collections']}")
    
    assert health.get("error") is None, f"Health error: {health.get('error')}"
    logger.info("✓ No errors")
    
    return True


def test_stress():
    """Stress test with multiple operations"""
    logger.info("=" * 60)
    logger.info("TEST: Stress Test")
    logger.info("=" * 60)
    
    manager = get_manager()
    collection = CollectionType.EPISODES
    
    # Batch operations
    batch_size = 50
    vectors = [generate_test_vector(1024) for _ in range(batch_size)]
    point_ids = [str(uuid.uuid4()) for _ in range(batch_size)]
    
    points = [
        PointStruct(
            id=pid,
            vector=vec,
            payload={"type": "stress_test", "batch": "large"}
        )
        for pid, vec in zip(point_ids, vectors)
    ]
    
    # Bulk upsert
    success = manager.upsert_points(collection, points)
    assert success, "Bulk upsert failed"
    logger.info(f"✓ Bulk upsert: {batch_size} points")
    
    # Batch search
    for i in range(0, batch_size, 10):
        query = vectors[i]
        results = manager.search(collection, query, limit=5)
        logger.info(f"  Search {i}: {len(results)} results")
    
    # Cleanup
    manager.delete_points(collection, point_ids)
    logger.info(f"✓ Cleanup: {batch_size} points deleted")
    
    return True


def run_all_tests():
    """Run all tests"""
    logger.info("\n" + "=" * 60)
    logger.info("QDRANT MEMORY INFRASTRUCTURE TEST SUITE")
    logger.info("=" * 60 + "\n")
    
    tests = [
        ("Connection", test_connection),
        ("Collections", test_collections),
        ("Vector Operations", test_vector_operations),
        ("Different Collections", test_different_collections),
        ("Health Check", test_health_check),
        ("Stress Test", test_stress),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, "PASSED"))
        except Exception as e:
            logger.error(f"✗ {name} FAILED: {e}")
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
