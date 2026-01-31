"""
Working Memory for Scarlet

This module provides:
- Redis-based working memory implementation
- Capacity-limited active memory (7±2 items)
- Attention mechanism and rehearsal
- Integration with long-term memory systems

Inspired by human working memory models (Baddeley & Hitch).

Author: ABIOGENESIS Team
Version: 1.0.0
Date: 2026-02-01
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)

# Constants for human-like working memory
DEFAULT_CAPACITY = 7  # Miller's magic number (7±2)
MIN_CAPACITY = 5
MAX_CAPACITY = 9
DEFAULT_DECAY_SECONDS = 300  # 5 minutes without rehearsal
REHEARSAL_BOOST_SECONDS = 120  # Rehearsal adds 2 minutes


class WorkingMemoryItemType(Enum):
    """Types of items in working memory"""
    FACT = "fact"           # Current relevant fact
    TASK = "task"           # Active task or goal
    CONTEXT = "context"     # Environmental context
    REFERENCE = "reference" # Pointer to LTM
    CHUNK = "chunk"         # Grouped related items


@dataclass
class WorkingMemoryItem:
    """A single item in working memory"""
    id: str
    item_type: WorkingMemoryItemType
    content: str
    importance: float = 0.5  # 0.0 to 1.0
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 1
    expires_at: float = 0.0  # Unix timestamp
    source: Optional[str] = None  # Where this came from (e.g., "episodic:uuid")
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.expires_at == 0.0:
            self.expires_at = time.time() + DEFAULT_DECAY_SECONDS
    
    @property
    def is_expired(self) -> bool:
        """Check if item has decayed."""
        return time.time() > self.expires_at
    
    @property
    def time_remaining(self) -> float:
        """Seconds until expiration."""
        return max(0, self.expires_at - time.time())
    
    def rehearse(self) -> None:
        """Refresh item to prevent decay."""
        self.last_accessed = time.time()
        self.access_count += 1
        self.expires_at = time.time() + DEFAULT_DECAY_SECONDS + REHEARSAL_BOOST_SECONDS
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "item_type": self.item_type.value,
            "content": self.content,
            "importance": self.importance,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "expires_at": self.expires_at,
            "source": self.source,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkingMemoryItem":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            item_type=WorkingMemoryItemType(data["item_type"]),
            content=data["content"],
            importance=data.get("importance", 0.5),
            created_at=data.get("created_at", time.time()),
            last_accessed=data.get("last_accessed", time.time()),
            access_count=data.get("access_count", 1),
            expires_at=data.get("expires_at", time.time() + DEFAULT_DECAY_SECONDS),
            source=data.get("source"),
            metadata=data.get("metadata", {}),
        )


class WorkingMemory:
    """
    Working Memory implementation for Scarlet.
    
    Implements a capacity-limited, decay-based working memory
    inspired by human cognitive models.
    
    Features:
    - Capacity limit (7±2 items)
    - Time-based decay
    - Rehearsal to maintain items
    - Importance-based eviction
    - Chunking support
    - Integration with LTM via Redis
    """
    
    def __init__(
        self,
        redis_client=None,
        capacity: int = DEFAULT_CAPACITY,
        session_id: Optional[str] = None,
    ):
        """
        Initialize working memory.
        
        Args:
            redis_client: Optional Redis client for persistence
            capacity: Maximum items (5-9)
            session_id: Unique session identifier
        """
        self.capacity = max(MIN_CAPACITY, min(MAX_CAPACITY, capacity))
        self.session_id = session_id or self._generate_session_id()
        self._redis = redis_client
        self._local_cache: Dict[str, WorkingMemoryItem] = {}
        self._attention_focus: Optional[str] = None  # Currently attended item
        self._task_queue: List[str] = []  # Pending tasks
        
        # Initialize Redis connection if not provided
        if self._redis is None:
            self._connect_redis()
        
        # Load existing state if available
        self._load_state()
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        timestamp = str(time.time())
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    def _connect_redis(self) -> bool:
        """Connect to Redis."""
        try:
            import redis
            host = os.getenv("REDIS_HOST", "localhost")
            port = int(os.getenv("REDIS_PORT", "6379"))
            self._redis = redis.Redis(
                host=host,
                port=port,
                decode_responses=True,
                socket_timeout=5,
            )
            self._redis.ping()
            logger.info(f"[WorkingMemory] Connected to Redis at {host}:{port}")
            return True
        except Exception as e:
            logger.warning(f"[WorkingMemory] Redis connection failed: {e}")
            self._redis = None
            return False
    
    def _redis_key(self, suffix: str = "") -> str:
        """Generate Redis key for this session."""
        base = f"scarlet:wm:{self.session_id}"
        return f"{base}:{suffix}" if suffix else base
    
    def _load_state(self) -> None:
        """Load state from Redis if available."""
        if self._redis is None:
            return
        
        try:
            data = self._redis.get(self._redis_key("state"))
            if data:
                state = json.loads(data)
                for item_data in state.get("items", []):
                    item = WorkingMemoryItem.from_dict(item_data)
                    if not item.is_expired:
                        self._local_cache[item.id] = item
                self._attention_focus = state.get("attention_focus")
                self._task_queue = state.get("task_queue", [])
                logger.debug(f"[WorkingMemory] Loaded {len(self._local_cache)} items from Redis")
        except Exception as e:
            logger.warning(f"[WorkingMemory] Failed to load state: {e}")
    
    def _save_state(self) -> None:
        """Save state to Redis."""
        if self._redis is None:
            return
        
        try:
            state = {
                "items": [item.to_dict() for item in self._local_cache.values()],
                "attention_focus": self._attention_focus,
                "task_queue": self._task_queue,
                "updated_at": time.time(),
            }
            self._redis.setex(
                self._redis_key("state"),
                DEFAULT_DECAY_SECONDS * 2,  # TTL double the decay time
                json.dumps(state),
            )
        except Exception as e:
            logger.warning(f"[WorkingMemory] Failed to save state: {e}")
    
    def _generate_item_id(self, content: str) -> str:
        """Generate unique ID for an item."""
        return hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()[:16]
    
    def _cleanup_expired(self) -> int:
        """Remove expired items."""
        expired = [
            item_id for item_id, item in self._local_cache.items()
            if item.is_expired
        ]
        for item_id in expired:
            del self._local_cache[item_id]
        
        if expired:
            logger.debug(f"[WorkingMemory] Cleaned up {len(expired)} expired items")
            self._save_state()
        
        return len(expired)
    
    def _evict_if_needed(self) -> Optional[WorkingMemoryItem]:
        """Evict lowest importance item if over capacity."""
        self._cleanup_expired()
        
        if len(self._local_cache) < self.capacity:
            return None
        
        # Find item with lowest importance and oldest access
        items = list(self._local_cache.values())
        items.sort(key=lambda x: (x.importance, x.last_accessed))
        
        evicted = items[0]
        del self._local_cache[evicted.id]
        
        logger.debug(f"[WorkingMemory] Evicted item: {evicted.content[:50]}...")
        return evicted
    
    # === Public API ===
    
    def add(
        self,
        content: str,
        item_type: WorkingMemoryItemType = WorkingMemoryItemType.FACT,
        importance: float = 0.5,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WorkingMemoryItem:
        """
        Add an item to working memory.
        
        Args:
            content: The content to remember
            item_type: Type of item
            importance: Priority (0.0-1.0)
            source: Optional source reference
            metadata: Additional metadata
            
        Returns:
            The created WorkingMemoryItem
        """
        # Evict if necessary
        evicted = self._evict_if_needed()
        
        # Create new item
        item = WorkingMemoryItem(
            id=self._generate_item_id(content),
            item_type=item_type,
            content=content,
            importance=importance,
            source=source,
            metadata=metadata or {},
        )
        
        self._local_cache[item.id] = item
        self._attention_focus = item.id
        self._save_state()
        
        logger.debug(f"[WorkingMemory] Added: {content[:50]}... (importance={importance})")
        return item
    
    def get(self, item_id: str) -> Optional[WorkingMemoryItem]:
        """Get an item by ID, refreshing access time."""
        self._cleanup_expired()
        
        item = self._local_cache.get(item_id)
        if item:
            item.rehearse()
            self._attention_focus = item_id
            self._save_state()
        
        return item
    
    def remove(self, item_id: str) -> bool:
        """Remove an item from working memory."""
        if item_id in self._local_cache:
            del self._local_cache[item_id]
            if self._attention_focus == item_id:
                self._attention_focus = None
            self._save_state()
            return True
        return False
    
    def get_all(self) -> List[WorkingMemoryItem]:
        """Get all active items in working memory."""
        self._cleanup_expired()
        return list(self._local_cache.values())
    
    def rehearse(self, item_ids: Optional[List[str]] = None) -> int:
        """
        Rehearse items to keep them active.
        
        Args:
            item_ids: Specific items to rehearse. If None, rehearses attention focus.
            
        Returns:
            Number of items rehearsed
        """
        if item_ids is None:
            if self._attention_focus:
                item_ids = [self._attention_focus]
            else:
                return 0
        
        count = 0
        for item_id in item_ids:
            if item_id in self._local_cache:
                self._local_cache[item_id].rehearse()
                count += 1
        
        if count > 0:
            self._save_state()
        
        return count
    
    def search(self, query: str) -> List[WorkingMemoryItem]:
        """
        Search working memory by content.
        
        Args:
            query: Search query
            
        Returns:
            Matching items sorted by relevance
        """
        self._cleanup_expired()
        
        query_lower = query.lower()
        matches = []
        
        for item in self._local_cache.values():
            if query_lower in item.content.lower():
                matches.append(item)
        
        # Sort by importance and recency
        matches.sort(key=lambda x: (x.importance, x.last_accessed), reverse=True)
        return matches
    
    def clear(self) -> int:
        """Clear all items from working memory."""
        count = len(self._local_cache)
        self._local_cache.clear()
        self._attention_focus = None
        self._task_queue.clear()
        self._save_state()
        return count
    
    def dump_to_ltm(self) -> List[Dict[str, Any]]:
        """
        Dump working memory contents for storage in long-term memory.
        
        Returns:
            List of items suitable for LTM storage
        """
        items_for_ltm = []
        
        for item in self._local_cache.values():
            if item.importance >= 0.5:  # Only dump important items
                items_for_ltm.append({
                    "content": item.content,
                    "type": item.item_type.value,
                    "importance": item.importance,
                    "access_count": item.access_count,
                    "source": item.source,
                    "metadata": item.metadata,
                })
        
        return items_for_ltm
    
    def chunk(self, item_ids: List[str], chunk_name: str) -> Optional[WorkingMemoryItem]:
        """
        Combine multiple items into a single chunk.
        
        This is a key human memory strategy for exceeding capacity limits.
        
        Args:
            item_ids: IDs of items to chunk
            chunk_name: Name for the chunk
            
        Returns:
            The new chunked item
        """
        items_to_chunk = []
        for item_id in item_ids:
            if item_id in self._local_cache:
                items_to_chunk.append(self._local_cache[item_id])
        
        if not items_to_chunk:
            return None
        
        # Combine contents
        combined_content = f"[CHUNK: {chunk_name}]\n"
        combined_content += "\n".join([f"- {item.content}" for item in items_to_chunk])
        
        # Calculate combined importance
        avg_importance = sum(item.importance for item in items_to_chunk) / len(items_to_chunk)
        
        # Remove individual items
        for item in items_to_chunk:
            del self._local_cache[item.id]
        
        # Create chunk
        chunk = self.add(
            content=combined_content,
            item_type=WorkingMemoryItemType.CHUNK,
            importance=min(1.0, avg_importance + 0.1),  # Slightly boost chunked items
            metadata={"chunked_from": item_ids},
        )
        
        return chunk
    
    # === Properties ===
    
    @property
    def count(self) -> int:
        """Get number of items in working memory."""
        self._cleanup_expired()
        return len(self._local_cache)
    
    # === Attention Management ===
    
    @property
    def attention(self) -> Optional[WorkingMemoryItem]:
        """Get the currently attended item."""
        if self._attention_focus:
            return self._local_cache.get(self._attention_focus)
        return None
    
    def focus(self, item_id: str) -> bool:
        """Set attention focus to a specific item."""
        if item_id in self._local_cache:
            self._attention_focus = item_id
            self._local_cache[item_id].rehearse()
            self._save_state()
            return True
        return False
    
    # === Task Queue ===
    
    def add_task(self, task: str, priority: float = 0.5) -> WorkingMemoryItem:
        """Add a task to the task queue."""
        item = self.add(
            content=task,
            item_type=WorkingMemoryItemType.TASK,
            importance=priority,
        )
        self._task_queue.append(item.id)
        self._save_state()
        return item
    
    def get_next_task(self) -> Optional[WorkingMemoryItem]:
        """Get and remove the next task from the queue."""
        while self._task_queue:
            task_id = self._task_queue.pop(0)
            if task_id in self._local_cache:
                task = self._local_cache[task_id]
                del self._local_cache[task_id]
                self._save_state()
                return task
        return None
    
    # === Status ===
    
    @property
    def status(self) -> Dict[str, Any]:
        """Get working memory status."""
        self._cleanup_expired()
        
        return {
            "session_id": self.session_id,
            "capacity": self.capacity,
            "items_count": len(self._local_cache),
            "available_slots": self.capacity - len(self._local_cache),
            "attention_focus": self._attention_focus,
            "task_queue_size": len(self._task_queue),
            "redis_connected": self._redis is not None,
            "items": [
                {
                    "id": item.id,
                    "type": item.item_type.value,
                    "content_preview": item.content[:50],
                    "importance": item.importance,
                    "expires_in": int(item.time_remaining),
                }
                for item in self._local_cache.values()
            ]
        }
    
    def to_context_string(self) -> str:
        """Format working memory as context string for LLM."""
        self._cleanup_expired()
        
        if not self._local_cache:
            return ""
        
        parts = ["== WORKING MEMORY =="]
        
        # Sort by importance
        items = sorted(
            self._local_cache.values(),
            key=lambda x: x.importance,
            reverse=True
        )
        
        for item in items:
            marker = "→" if item.id == self._attention_focus else "•"
            parts.append(f"{marker} [{item.item_type.value.upper()}] {item.content}")
        
        return "\n".join(parts)


# Global working memory instance
_global_wm: Optional[WorkingMemory] = None


def get_working_memory(session_id: Optional[str] = None) -> WorkingMemory:
    """Get or create global working memory instance."""
    global _global_wm
    if _global_wm is None or (session_id and _global_wm.session_id != session_id):
        _global_wm = WorkingMemory(session_id=session_id)
    return _global_wm
