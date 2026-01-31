"""
Qdrant Vector Database Manager for Scarlet's Long-Term Memory

This module provides:
- Connection management to Qdrant
- Collection creation and configuration
- Vector operations for episodic, semantic, procedural, and emotional memory
- Hybrid search capabilities

Author: ABIOGENESIS Team
Version: 1.0.0
Date: 2026-01-31
"""

import os
import time
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    OptimizersConfigDiff,
    HnswConfigDiff,
    ScalarType,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchParams,
)

logger = logging.getLogger(__name__)


class CollectionType(Enum):
    """Types of memory collections in Qdrant"""
    EPISODES = "episodes"
    CONCEPTS = "concepts"
    SKILLS = "skills"
    EMOTIONS = "emotions"


@dataclass
class QdrantConfig:
    """Configuration for Qdrant connection"""
    host: str = "localhost"
    port: int = 6333
    grpc_port: int = 6334
    api_key: Optional[str] = None
    timeout: int = 30
    prefer_grpc: bool = False
    
    @classmethod
    def from_env(cls) -> "QdrantConfig":
        """Load configuration from environment variables"""
        return cls(
            host=os.getenv("QDRANT_HOST", "localhost"),
            port=int(os.getenv("QDRANT_PORT", "6333")),
            grpc_port=int(os.getenv("QDRANT_GRPC_PORT", "6334")),
            api_key=os.getenv("QDRANT_API_KEY"),
            timeout=int(os.getenv("QDRANT_TIMEOUT", "30")),
            prefer_grpc=os.getenv("QDRANT_PREFER_GRPC", "false").lower() == "true",
        )


@dataclass
class CollectionConfig:
    """Configuration for a Qdrant collection"""
    name: str
    vector_size: int
    distance: Distance = Distance.COSINE
    on_disk: bool = True
    # HNSW Index settings
    hnsw_m: int = 16
    hnsw_ef_construct: int = 100
    full_scan_threshold: int = 10000
    # Optimization settings
    default_segment_number: int = 2
    max_optimization_threads: int = 4
    # Quantization settings
    quantization_enabled: bool = False
    quantization_type: ScalarType = ScalarType.INT8
    quantization_always_ram: bool = False
    
    def to_qdrant_config(self) -> dict:
        """Convert to Qdrant collection configuration"""
        config = {
            "vectors": VectorParams(
                size=self.vector_size,
                distance=self.distance,
                on_disk=self.on_disk,
            ),
            "optimizers": OptimizersConfigDiff(
                default_segment_number=self.default_segment_number,
                max_optimization_threads=self.max_optimization_threads,
            ),
            "hnsw_config": HnswConfigDiff(
                m=self.hnsw_m,
                ef_construct=self.hnsw_ef_construct,
                full_scan_threshold=self.full_scan_threshold,
            ),
        }
        
        if self.quantization_enabled:
            config["quantization"] = {
                "scalar": {
                    "type": self.quantization_type.value,
                    "always_ram": self.quantization_always_ram,
                }
            }
        
        return config


# Collection configurations for Scarlet's memory system
COLLECTION_CONFIGS: Dict[CollectionType, CollectionConfig] = {
    CollectionType.EPISODES: CollectionConfig(
        name="episodes",
        vector_size=1024,  # BGE-m3 full dimension
        hnsw_m=16,
        hnsw_ef_construct=100,
        full_scan_threshold=10000,
        quantization_enabled=True,
        quantization_always_ram=True,
    ),
    CollectionType.CONCEPTS: CollectionConfig(
        name="concepts",
        vector_size=1024,  # BGE-m3 full dimension
        hnsw_m=16,
        hnsw_ef_construct=100,
        full_scan_threshold=10000,
        quantization_enabled=True,
        quantization_always_ram=True,
    ),
    CollectionType.SKILLS: CollectionConfig(
        name="skills",
        vector_size=1024,  # BGE-m3 full dimension
        hnsw_m=16,
        hnsw_ef_construct=100,
        full_scan_threshold=5000,
        quantization_enabled=True,
        quantization_always_ram=True,
    ),
    CollectionType.EMOTIONS: CollectionConfig(
        name="emotions",
        vector_size=512,  # Truncated for efficiency
        hnsw_m=8,
        hnsw_ef_construct=64,
        full_scan_threshold=2000,
        quantization_enabled=True,
        quantization_always_ram=True,
    ),
}


class QdrantManager:
    """
    Manager for Qdrant vector database operations.
    
    Handles connection, collection management, and vector operations
    for Scarlet's Long-Term Memory System.
    """
    
    def __init__(self, config: Optional[QdrantConfig] = None):
        """
        Initialize Qdrant manager.
        
        Args:
            config: Qdrant configuration. If None, loads from environment.
        """
        self.config = config or QdrantConfig.from_env()
        self._client: Optional[QdrantClient] = None
        self._connected = False
        
    @property
    def client(self) -> QdrantClient:
        """Get or create Qdrant client"""
        if self._client is None:
            self._client = QdrantClient(
                host=self.config.host,
                port=self.config.port,
                grpc_port=self.config.grpc_port if self.config.prefer_grpc else None,
                api_key=self.config.api_key,
                timeout=self.config.timeout,
                prefer_grpc=self.config.prefer_grpc,
            )
        return self._client
    
    def connect(self, max_retries: int = 5, retry_delay: float = 2.0) -> bool:
        """
        Connect to Qdrant with retry logic.
        
        Args:
            max_retries: Maximum number of connection retries
            retry_delay: Delay between retries in seconds
            
        Returns:
            True if connection successful, False otherwise
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Connecting to Qdrant at {self.config.host}:{self.config.port}...")
                self.client.get_collections()
                self._connected = True
                logger.info("✓ Qdrant connection established")
                return True
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        
        logger.error("✗ Failed to connect to Qdrant")
        return False
    
    def disconnect(self) -> None:
        """Close connection to Qdrant"""
        if self._client is not None:
            self._client.close()
            self._client = None
            self._connected = False
            logger.info("Qdrant connection closed")
    
    def is_connected(self) -> bool:
        """Check if connected to Qdrant"""
        if not self._connected:
            return False
        try:
            self.client.get_collections()
            return True
        except Exception:
            self._connected = False
            return False
    
    def create_collection(self, collection_type: CollectionType) -> bool:
        """
        Create a collection for the specified memory type.
        
        Args:
            collection_type: Type of memory collection to create
            
        Returns:
            True if collection created or already exists
        """
        config = COLLECTION_CONFIGS[collection_type]
        collection_name = config.name
        
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            existing_names = [c.name for c in collections.collections]
            
            if collection_name in existing_names:
                logger.info(f"Collection '{collection_name}' already exists")
                return True
            
            # Create collection
            logger.info(f"Creating collection '{collection_name}'...")
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=config.to_qdrant_config()["vectors"],
                optimizers_config=config.to_qdrant_config().get("optimizers"),
                hnsw_config=config.to_qdrant_config().get("hnsw_config"),
                quantization_config=config.to_qdrant_config().get("quantization"),
            )
            logger.info(f"✓ Collection '{collection_name}' created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection '{collection_name}': {e}")
            return False
    
    def create_all_collections(self) -> Dict[CollectionType, bool]:
        """
        Create all collections for Scarlet's memory system.
        
        Returns:
            Dictionary mapping collection type to creation status
        """
        results = {}
        for collection_type in CollectionType:
            results[collection_type] = self.create_collection(collection_type)
        return results
    
    def delete_collection(self, collection_type: CollectionType) -> bool:
        """
        Delete a collection.
        
        Args:
            collection_type: Type of memory collection to delete
            
        Returns:
            True if deletion successful
        """
        collection_name = COLLECTION_CONFIGS[collection_type].name
        
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"Collection '{collection_name}' deleted")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection '{collection_name}': {e}")
            return False
    
    def list_collections(self) -> List[str]:
        """List all existing collections"""
        try:
            collections = self.client.get_collections()
            return [c.name for c in collections.collections]
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []
    
    def get_collection_info(self, collection_type: CollectionType) -> Optional[dict]:
        """Get information about a collection"""
        collection_name = COLLECTION_CONFIGS[collection_type].name
        
        try:
            info = self.client.get_collection(collection_name)
            # Handle different API structures in Qdrant v1.16
            vectors_count = info.vectors_count if hasattr(info, 'vectors_count') else 0
            segments_count = info.segments_count if hasattr(info, 'segments_count') else 0
            status = str(info.status) if hasattr(info, 'status') else 'unknown'
            
            # Try to get vector size from config
            vector_size = COLLECTION_CONFIGS[collection_type].vector_size  # Default from config
            
            return {
                "name": collection_name,
                "vector_size": vector_size,
                "vectors_count": vectors_count,
                "segments_count": segments_count,
                "status": status,
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return None
    
    def upsert_points(
        self,
        collection_type: CollectionType,
        points: List[PointStruct],
        wait: bool = True,
    ) -> bool:
        """
        Insert or update points in a collection.
        
        Args:
            collection_type: Type of memory collection
            points: List of points to insert
            wait: Wait for operation to complete
            
        Returns:
            True if operation successful
        """
        collection_name = COLLECTION_CONFIGS[collection_type].name
        
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=points,
                wait=wait,
            )
            logger.debug(f"Upserted {len(points)} points to '{collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to upsert points: {e}")
            return False
    
    def search(
        self,
        collection_type: CollectionType,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        query_filter: Optional[Filter] = None,
    ) -> List[Tuple[dict, float]]:
        """
        Search for similar vectors in a collection.
        
        Args:
            collection_type: Type of memory collection
            query_vector: Query vector to search for
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            query_filter: Optional filter to apply
            
        Returns:
            List of (payload, score) tuples
        """
        collection_name = COLLECTION_CONFIGS[collection_type].name
        
        try:
            # Use query_points for Qdrant v1.16+
            response = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=query_filter,
                search_params=SearchParams(
                    hnsw_ef=128,
                    exact=False,
                ),
            )
            
            # QueryResponse has .points attribute with ScoredPoint objects
            parsed_results = []
            
            # Handle QueryResponse object
            points = response.points if hasattr(response, 'points') else response
            
            for r in points:
                try:
                    if hasattr(r, 'payload') and hasattr(r, 'score'):
                        # ScoredPoint object
                        score = float(r.score) if not isinstance(r.score, (int, float)) else r.score
                        parsed_results.append((r.payload, score))
                    elif isinstance(r, tuple) and len(r) >= 2:
                        # Tuple (payload, score)
                        parsed_results.append((r[0], float(r[1])))
                    elif isinstance(r, dict):
                        # Dict with payload and score
                        parsed_results.append((r.get('payload', {}), float(r.get('score', 0.0))))
                except (TypeError, ValueError) as e:
                    logger.warning(f"Failed to parse result: {e}")
                    continue
                    
            return parsed_results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def delete_points(
        self,
        collection_type: CollectionType,
        point_ids: List[str],
        wait: bool = True,
    ) -> bool:
        """
        Delete points from a collection.
        
        Args:
            collection_type: Type of memory collection
            point_ids: List of point IDs to delete
            wait: Wait for operation to complete
            
        Returns:
            True if operation successful
        """
        collection_name = COLLECTION_CONFIGS[collection_type].name
        
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=point_ids,
                wait=wait,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete points: {e}")
            return False
    
    def count_points(self, collection_type: CollectionType) -> int:
        """Get the number of points in a collection"""
        collection_name = COLLECTION_CONFIGS[collection_type].name
        
        try:
            count = self.client.count(
                collection_name=collection_name,
                exact=True,
            )
            return count.count
        except Exception as e:
            logger.error(f"Failed to count points: {e}")
            return 0
    
    def clear_collection(self, collection_type: CollectionType) -> bool:
        """Clear all points from a collection"""
        collection_name = COLLECTION_CONFIGS[collection_type].name
        
        try:
            self.client.delete_collection(collection_name)
            self.create_collection(collection_type)
            logger.info(f"Collection '{collection_name}' cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Qdrant.
        
        Returns:
            Dictionary with health status information
        """
        result = {
            "connected": self.is_connected(),
            "collections": {},
            "error": None,
        }
        
        if result["connected"]:
            try:
                result["collections"] = {
                    ct.name: self.count_points(ct)
                    for ct in CollectionType
                }
            except Exception as e:
                result["error"] = str(e)
        
        return result


# Convenience functions for common operations
def get_manager() -> QdrantManager:
    """Get a connected Qdrant manager instance"""
    manager = QdrantManager()
    if not manager.connect():
        raise ConnectionError("Failed to connect to Qdrant")
    return manager


def setup_memory_collections() -> Dict[CollectionType, bool]:
    """
    Setup all memory collections for Scarlet.
    
    Creates collections and returns status for each.
    """
    manager = get_manager()
    return manager.create_all_collections()
