"""
Memory Decay System (ADR-005)

Implements Ebbinghaus forgetting curve for natural memory decay.

Formula: R = e^(-t/S)
Where:
- R = retention (decay_factor)
- t = time since creation/last access
- S = memory strength (based on importance, access_count, emotional intensity)

Higher importance, more accesses, and emotional intensity = slower decay.

Author: ABIOGENESIS Team
Version: 1.0.0
Date: 2026-02-01
"""

import os
import math
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, Range, PointStruct

# Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

# Decay parameters
BASE_HALF_LIFE_HOURS = 168  # 1 week base half-life
MIN_DECAY_FACTOR = 0.01    # Don't go below 1% retention
DECAY_BATCH_SIZE = 100     # Process in batches


@dataclass
class DecayParams:
    """Parameters for memory decay calculation."""
    base_half_life_hours: float = BASE_HALF_LIFE_HOURS
    importance_multiplier: float = 2.0      # High importance = 2x half-life
    emotional_multiplier: float = 1.5       # High emotion = 1.5x half-life
    access_count_factor: float = 0.1        # Each access adds 10% to half-life
    min_decay_factor: float = MIN_DECAY_FACTOR


class MemoryDecay:
    """
    Manages memory decay using Ebbinghaus forgetting curve.
    
    Memories decay over time but can be reinforced through:
    - High importance score
    - Emotional intensity
    - Frequent access
    
    The decay_factor field in Qdrant payloads represents current retention.
    """
    
    def __init__(self, params: DecayParams = None):
        """Initialize decay system."""
        self.params = params or DecayParams()
        self._client: Optional[QdrantClient] = None
        self._collections = ["episodes", "concepts", "skills", "emotions"]
    
    def _get_client(self) -> QdrantClient:
        """Get or create Qdrant client."""
        if self._client is None:
            self._client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        return self._client
    
    def calculate_memory_strength(self, payload: Dict[str, Any]) -> float:
        """
        Calculate memory strength (S) based on payload metadata.
        
        Higher strength = slower decay.
        
        Args:
            payload: Memory payload with importance, emotional, access fields
            
        Returns:
            Memory strength multiplier (>= 1.0)
        """
        # Base strength
        strength = 1.0
        
        # Importance contribution (0-1 importance adds 0-2x to half-life)
        importance = payload.get("importance", 0.5)
        strength += importance * self.params.importance_multiplier
        
        # Emotional contribution
        valence = abs(payload.get("emotional_valence", 0.0))  # Absolute value
        arousal = payload.get("emotional_arousal", 0.5)
        emotional_intensity = (valence + arousal) / 2
        strength += emotional_intensity * self.params.emotional_multiplier
        
        # Access count contribution (logarithmic)
        access_count = payload.get("access_count", 0)
        if access_count > 0:
            strength += math.log1p(access_count) * self.params.access_count_factor
        
        return strength
    
    def calculate_decay_factor(
        self, 
        created_at: str,
        last_accessed: str,
        strength: float
    ) -> float:
        """
        Calculate current decay factor using Ebbinghaus curve.
        
        Args:
            created_at: ISO timestamp of creation
            last_accessed: ISO timestamp of last access
            strength: Memory strength multiplier
            
        Returns:
            Decay factor (0.0 to 1.0)
        """
        try:
            # Parse timestamps
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            accessed = datetime.fromisoformat(last_accessed.replace('Z', '+00:00'))
            now = datetime.now(created.tzinfo) if created.tzinfo else datetime.now()
            
            # Use time since last access (not creation) for decay
            # This means frequently accessed memories stay fresh
            hours_since_access = (now - accessed).total_seconds() / 3600
            
            # Effective half-life based on strength
            half_life = self.params.base_half_life_hours * strength
            
            # Ebbinghaus formula: R = e^(-t/S) where S relates to half-life
            # Convert to half-life form: R = 2^(-t/half_life)
            decay_factor = math.pow(2, -hours_since_access / half_life)
            
            # Ensure minimum
            return max(decay_factor, self.params.min_decay_factor)
            
        except Exception as e:
            print(f"[MemoryDecay] Error calculating decay: {e}")
            return 1.0  # Default to no decay on error
    
    def update_decay(self, collection: str, point_id: str) -> float:
        """
        Update decay factor for a single memory point.
        
        Args:
            collection: Qdrant collection name
            point_id: Point ID to update
            
        Returns:
            New decay factor
        """
        client = self._get_client()
        
        try:
            # Get current point
            points = client.retrieve(
                collection_name=collection,
                ids=[point_id],
                with_payload=True
            )
            
            if not points:
                return 1.0
            
            point = points[0]
            payload = point.payload or {}
            
            # Calculate new decay factor
            strength = self.calculate_memory_strength(payload)
            decay_factor = self.calculate_decay_factor(
                created_at=payload.get("created_at", datetime.now().isoformat()),
                last_accessed=payload.get("last_accessed", datetime.now().isoformat()),
                strength=strength
            )
            
            # Update point payload
            client.set_payload(
                collection_name=collection,
                payload={"decay_factor": decay_factor},
                points=[point_id]
            )
            
            return decay_factor
            
        except Exception as e:
            print(f"[MemoryDecay] Error updating point {point_id}: {e}")
            return 1.0
    
    def run_decay_cycle(self) -> Dict[str, Any]:
        """
        Run decay update for all collections.
        
        Should be called periodically (e.g., every hour).
        
        Returns:
            Statistics about the decay cycle
        """
        client = self._get_client()
        stats = {
            "collections_processed": 0,
            "points_updated": 0,
            "errors": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        for collection in self._collections:
            try:
                # Check if collection exists
                collections = client.get_collections()
                collection_names = [c.name for c in collections.collections]
                
                if collection not in collection_names:
                    continue
                
                stats["collections_processed"] += 1
                
                # Get all points (in batches)
                offset = None
                while True:
                    result = client.scroll(
                        collection_name=collection,
                        limit=DECAY_BATCH_SIZE,
                        offset=offset,
                        with_payload=True
                    )
                    
                    points, next_offset = result
                    
                    if not points:
                        break
                    
                    # Update each point
                    for point in points:
                        try:
                            payload = point.payload or {}
                            
                            # Calculate new decay
                            strength = self.calculate_memory_strength(payload)
                            decay_factor = self.calculate_decay_factor(
                                created_at=payload.get("created_at", datetime.now().isoformat()),
                                last_accessed=payload.get("last_accessed", datetime.now().isoformat()),
                                strength=strength
                            )
                            
                            # Update if changed significantly
                            old_decay = payload.get("decay_factor", 1.0)
                            if abs(decay_factor - old_decay) > 0.01:
                                client.set_payload(
                                    collection_name=collection,
                                    payload={"decay_factor": decay_factor},
                                    points=[point.id]
                                )
                                stats["points_updated"] += 1
                                
                        except Exception as e:
                            stats["errors"] += 1
                    
                    # Next batch
                    offset = next_offset
                    if offset is None:
                        break
                        
            except Exception as e:
                print(f"[MemoryDecay] Error processing {collection}: {e}")
                stats["errors"] += 1
        
        return stats
    
    def reinforce_memory(self, collection: str, point_id: str) -> float:
        """
        Reinforce a memory (called on access).
        
        Updates last_accessed and increments access_count,
        which will slow future decay.
        
        Args:
            collection: Collection name
            point_id: Point ID
            
        Returns:
            New decay factor (should be higher after reinforcement)
        """
        client = self._get_client()
        now = datetime.now().isoformat()
        
        try:
            # Get current point
            points = client.retrieve(
                collection_name=collection,
                ids=[point_id],
                with_payload=True
            )
            
            if not points:
                return 1.0
            
            point = points[0]
            payload = point.payload or {}
            
            # Update access tracking
            new_access_count = payload.get("access_count", 0) + 1
            
            # Calculate new decay (will be higher due to recent access)
            strength = self.calculate_memory_strength({
                **payload,
                "access_count": new_access_count
            })
            
            # With recent access, decay starts fresh
            decay_factor = 1.0  # Full retention on access
            
            # Update payload
            client.set_payload(
                collection_name=collection,
                payload={
                    "last_accessed": now,
                    "access_count": new_access_count,
                    "decay_factor": decay_factor
                },
                points=[point_id]
            )
            
            return decay_factor
            
        except Exception as e:
            print(f"[MemoryDecay] Error reinforcing {point_id}: {e}")
            return 1.0
    
    def get_decayed_memories(
        self, 
        threshold: float = 0.2,
        collection: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get memories that have decayed below threshold.
        
        Useful for identifying memories to archive or delete.
        
        Args:
            threshold: Decay threshold (default 0.2 = 20% retention)
            collection: Optional specific collection
            
        Returns:
            List of decayed memory payloads
        """
        client = self._get_client()
        decayed = []
        
        collections_to_check = [collection] if collection else self._collections
        
        for coll in collections_to_check:
            try:
                result = client.scroll(
                    collection_name=coll,
                    scroll_filter=Filter(
                        must=[
                            FieldCondition(
                                key="decay_factor",
                                range=Range(lte=threshold)
                            )
                        ]
                    ),
                    limit=100,
                    with_payload=True
                )
                
                points, _ = result
                for point in points:
                    decayed.append({
                        "id": point.id,
                        "collection": coll,
                        "payload": point.payload
                    })
                    
            except Exception as e:
                print(f"[MemoryDecay] Error checking {coll}: {e}")
        
        return decayed


# Singleton instance
_decay_instance: Optional[MemoryDecay] = None


def get_decay_manager() -> MemoryDecay:
    """Get singleton MemoryDecay instance."""
    global _decay_instance
    if _decay_instance is None:
        _decay_instance = MemoryDecay()
    return _decay_instance


def run_decay_cycle() -> Dict[str, Any]:
    """Convenience function to run decay cycle."""
    return get_decay_manager().run_decay_cycle()


def reinforce_memory(collection: str, point_id: str) -> float:
    """Convenience function to reinforce a memory."""
    return get_decay_manager().reinforce_memory(collection, point_id)
