"""
Working Set Management
======================

Manages the Working Set - Scarlet's continuity memory between ticks.

ADR-006: Decision 3 - Loop Contract (Working Set)
SPEC-004: Section 4.3 - Working Set

The Working Set allows Scarlet to "resume" between ticks,
maintaining context about ongoing tasks and recent thoughts.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from redis.asyncio import Redis

logger = logging.getLogger(__name__)


@dataclass
class TaskEntry:
    """
    A task in the Working Set.
    
    Tasks can be:
    - pending: queued for execution
    - active: currently being worked on
    - blocked: waiting for something
    - done: completed
    - parked: temporarily set aside
    """
    id: str
    description: str
    state: Literal["pending", "active", "blocked", "done", "parked"]
    created_at: datetime
    updated_at: datetime
    progress_markers: list[str] = field(default_factory=list)
    stop_condition: str | None = None
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "progress_markers": self.progress_markers,
            "stop_condition": self.stop_condition,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> TaskEntry:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            description=data["description"],
            state=data["state"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            progress_markers=data.get("progress_markers", []),
            stop_condition=data.get("stop_condition"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ProgressMarker:
    """
    A marker indicating progress was made.
    
    Progress markers are used to detect runaway (no progress = potential loop).
    """
    id: str
    tick_id: str
    timestamp: datetime
    marker_type: str                    # From config.progress.significant_changes
    continuation_ref: str
    evidence: str | None = None
    verified: bool = False
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "tick_id": self.tick_id,
            "timestamp": self.timestamp.isoformat(),
            "marker_type": self.marker_type,
            "continuation_ref": self.continuation_ref,
            "evidence": self.evidence,
            "verified": self.verified,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> ProgressMarker:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            tick_id=data["tick_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            marker_type=data["marker_type"],
            continuation_ref=data["continuation_ref"],
            evidence=data.get("evidence"),
            verified=data.get("verified", False),
        )


@dataclass
class WorkingSet:
    """
    Scarlet's continuity memory between ticks.
    
    This allows Scarlet to:
    - Resume tasks across ticks
    - Track what she was thinking about
    - Know what evidence she expected
    - Avoid repeating actions (idempotency)
    """
    # Task tracking
    active_tasks: list[TaskEntry] = field(default_factory=list)
    pending_tasks: list[TaskEntry] = field(default_factory=list)
    parked_tasks: list[TaskEntry] = field(default_factory=list)
    
    # Last frame of thought
    last_thought_summary: str = ""      # Summary (not full CoT)
    last_intent: str = ""
    last_expected_evidence: str = ""
    
    # Progress
    progress_markers: list[ProgressMarker] = field(default_factory=list)
    idempotency_keys: set[str] = field(default_factory=set)
    
    # Metadata
    last_updated: datetime = field(default_factory=datetime.utcnow)
    tick_count: int = 0
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "active_tasks": [t.to_dict() for t in self.active_tasks],
            "pending_tasks": [t.to_dict() for t in self.pending_tasks],
            "parked_tasks": [t.to_dict() for t in self.parked_tasks],
            "last_thought_summary": self.last_thought_summary,
            "last_intent": self.last_intent,
            "last_expected_evidence": self.last_expected_evidence,
            "progress_markers": [m.to_dict() for m in self.progress_markers[-50:]],  # Keep last 50
            "idempotency_keys": list(self.idempotency_keys)[-100:],  # Keep last 100
            "last_updated": self.last_updated.isoformat(),
            "tick_count": self.tick_count,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> WorkingSet:
        """Deserialize from dictionary."""
        return cls(
            active_tasks=[TaskEntry.from_dict(t) for t in data.get("active_tasks", [])],
            pending_tasks=[TaskEntry.from_dict(t) for t in data.get("pending_tasks", [])],
            parked_tasks=[TaskEntry.from_dict(t) for t in data.get("parked_tasks", [])],
            last_thought_summary=data.get("last_thought_summary", ""),
            last_intent=data.get("last_intent", ""),
            last_expected_evidence=data.get("last_expected_evidence", ""),
            progress_markers=[ProgressMarker.from_dict(m) for m in data.get("progress_markers", [])],
            idempotency_keys=set(data.get("idempotency_keys", [])),
            last_updated=datetime.fromisoformat(data["last_updated"]) if "last_updated" in data else datetime.utcnow(),
            tick_count=data.get("tick_count", 0),
        )


class WorkingSetManager:
    """
    Manages Working Set persistence and operations.
    
    Storage: Redis (hot) with Qdrant backup (cold).
    """
    
    def __init__(self, key_prefix: str = "scarlet:runtime:"):
        self.key = f"{key_prefix}working_set"
        self._redis: Redis | None = None
        self._working_set: WorkingSet = WorkingSet()
    
    def set_redis(self, redis: Redis) -> None:
        """Set Redis connection."""
        self._redis = redis
    
    @property
    def working_set(self) -> WorkingSet:
        """Get current Working Set."""
        return self._working_set
    
    async def load(self) -> WorkingSet:
        """
        Load Working Set from Redis.
        
        Returns:
            Loaded WorkingSet or new empty one
        """
        if self._redis is None:
            logger.warning("Redis not connected, using empty Working Set")
            return self._working_set
        
        try:
            data = await self._redis.get(self.key)
            if data:
                self._working_set = WorkingSet.from_dict(json.loads(data))
                logger.debug(f"Loaded Working Set (tick {self._working_set.tick_count})")
            else:
                logger.info("No existing Working Set, starting fresh")
                self._working_set = WorkingSet()
        except Exception as e:
            logger.error(f"Error loading Working Set: {e}")
            self._working_set = WorkingSet()
        
        return self._working_set
    
    async def save(self) -> None:
        """Save Working Set to Redis."""
        if self._redis is None:
            logger.warning("Redis not connected, cannot save Working Set")
            return
        
        try:
            self._working_set.last_updated = datetime.utcnow()
            data = json.dumps(self._working_set.to_dict())
            await self._redis.set(self.key, data)
            logger.debug(f"Saved Working Set (tick {self._working_set.tick_count})")
        except Exception as e:
            logger.error(f"Error saving Working Set: {e}")
    
    def tick(self) -> None:
        """Called each tick to update Working Set."""
        self._working_set.tick_count += 1
        self._working_set.last_updated = datetime.utcnow()
    
    def add_task(self, task: TaskEntry) -> None:
        """Add a new task."""
        task.created_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        
        if task.state == "active":
            self._working_set.active_tasks.append(task)
        elif task.state == "pending":
            self._working_set.pending_tasks.append(task)
        elif task.state == "parked":
            self._working_set.parked_tasks.append(task)
        
        logger.debug(f"Added task: {task.id} ({task.state})")
    
    def update_task(self, task_id: str, state: str | None = None, **updates) -> bool:
        """
        Update a task.
        
        Args:
            task_id: Task ID to update
            state: New state (triggers list move)
            **updates: Other fields to update
            
        Returns:
            True if task found and updated
        """
        # Find task in all lists
        task = None
        source_list = None
        
        for lst, name in [
            (self._working_set.active_tasks, "active"),
            (self._working_set.pending_tasks, "pending"),
            (self._working_set.parked_tasks, "parked"),
        ]:
            for t in lst:
                if t.id == task_id:
                    task = t
                    source_list = (lst, name)
                    break
            if task:
                break
        
        if not task:
            return False
        
        # Update fields
        task.updated_at = datetime.utcnow()
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        # Handle state change
        if state and state != source_list[1]:
            source_list[0].remove(task)
            task.state = state  # type: ignore
            
            if state == "active":
                self._working_set.active_tasks.append(task)
            elif state == "pending":
                self._working_set.pending_tasks.append(task)
            elif state == "parked":
                self._working_set.parked_tasks.append(task)
            elif state == "done":
                pass  # Remove from working set
        
        logger.debug(f"Updated task: {task_id} -> {state or source_list[1]}")
        return True
    
    def add_progress_marker(self, marker: ProgressMarker) -> None:
        """Add a progress marker."""
        self._working_set.progress_markers.append(marker)
        
        # Keep only last 50 markers
        if len(self._working_set.progress_markers) > 50:
            self._working_set.progress_markers = self._working_set.progress_markers[-50:]
        
        logger.debug(f"Added progress marker: {marker.marker_type}")
    
    def add_idempotency_key(self, key: str) -> bool:
        """
        Add an idempotency key.
        
        Returns:
            True if key was new, False if already exists
        """
        if key in self._working_set.idempotency_keys:
            return False
        
        self._working_set.idempotency_keys.add(key)
        
        # Keep only last 100 keys
        if len(self._working_set.idempotency_keys) > 100:
            # Convert to list, remove oldest, convert back
            keys = list(self._working_set.idempotency_keys)
            self._working_set.idempotency_keys = set(keys[-100:])
        
        return True
    
    def update_thought(
        self,
        summary: str | None = None,
        intent: str | None = None,
        expected_evidence: str | None = None,
    ) -> None:
        """Update the last thought frame."""
        if summary is not None:
            self._working_set.last_thought_summary = summary
        if intent is not None:
            self._working_set.last_intent = intent
        if expected_evidence is not None:
            self._working_set.last_expected_evidence = expected_evidence
    
    def get_recent_progress_markers(self, n: int = 10) -> list[ProgressMarker]:
        """Get the N most recent progress markers."""
        return self._working_set.progress_markers[-n:]
    
    def has_active_task(self) -> bool:
        """Check if there's an active task."""
        return len(self._working_set.active_tasks) > 0
    
    def get_summary(self) -> dict:
        """Get a summary for logging/monitoring."""
        return {
            "active_tasks": len(self._working_set.active_tasks),
            "pending_tasks": len(self._working_set.pending_tasks),
            "parked_tasks": len(self._working_set.parked_tasks),
            "progress_markers": len(self._working_set.progress_markers),
            "tick_count": self._working_set.tick_count,
            "last_intent": self._working_set.last_intent[:50] if self._working_set.last_intent else "",
        }
