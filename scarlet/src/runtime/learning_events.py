"""
Learning Events
===============

Emits Learning Events when runaway or errors are detected.

ADR-006: Decision 6 - Runaway Detection (Learning Events)
SPEC-004: Section 8 - Learning Events

Learning Events are entry points for future Learning Agent (L3.2).
They capture patterns that Scarlet should learn from.
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct

from .runaway import RunawayScore
from .working_set import WorkingSet

logger = logging.getLogger(__name__)


@dataclass
class LearningEvent:
    """
    An event that the future Learning Agent can learn from.
    
    Learning Events are stored in Qdrant for later analysis.
    They represent patterns (often negative) that Scarlet encountered.
    
    ⚠️ NOTE: The Learning Agent (L3.2) that will process these events
    is a PLACEHOLDER. Events are stored now for future use.
    See ROADMAP L3.2 for Learning System implementation.
    """
    id: str
    timestamp: datetime
    event_type: Literal["runaway", "error_pattern", "stuck", "budget_exhaust"]
    
    # Context
    trigger_summary: str            # What triggered this event
    state_at_trigger: str           # Runtime state when triggered
    working_set_summary: dict       # Snapshot of working set
    
    # Analysis
    runaway_score: dict | None      # If runaway-related
    error_details: str | None       # If error-related
    
    # For Learning Agent (L3.2 - PLACEHOLDER)
    suggested_lesson: str           # What could be learned
    pattern_signature: str          # Hash for pattern matching
    
    # Metadata
    severity: Literal["low", "medium", "high", "critical"]
    resolved: bool = False
    resolution: str | None = None
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "trigger_summary": self.trigger_summary,
            "state_at_trigger": self.state_at_trigger,
            "working_set_summary": self.working_set_summary,
            "runaway_score": self.runaway_score,
            "error_details": self.error_details,
            "suggested_lesson": self.suggested_lesson,
            "pattern_signature": self.pattern_signature,
            "severity": self.severity,
            "resolved": self.resolved,
            "resolution": self.resolution,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> LearningEvent:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            event_type=data["event_type"],
            trigger_summary=data["trigger_summary"],
            state_at_trigger=data["state_at_trigger"],
            working_set_summary=data["working_set_summary"],
            runaway_score=data.get("runaway_score"),
            error_details=data.get("error_details"),
            suggested_lesson=data["suggested_lesson"],
            pattern_signature=data["pattern_signature"],
            severity=data["severity"],
            resolved=data.get("resolved", False),
            resolution=data.get("resolution"),
        )


class LearningEventEmitter:
    """
    Emits and stores Learning Events.
    
    Storage: Qdrant collection "learning_events"
    
    ⚠️ NOTE: This prepares data for future Learning Agent (L3.2).
    The Learning Agent is not implemented yet - see ROADMAP.
    """
    
    def __init__(self, collection_name: str = "learning_events"):
        self.collection_name = collection_name
        self._qdrant: QdrantClient | None = None
    
    def set_qdrant(self, qdrant: QdrantClient) -> None:
        """Set Qdrant client."""
        self._qdrant = qdrant
    
    async def emit_runaway_event(
        self,
        runaway_score: RunawayScore,
        working_set: WorkingSet,
        current_state: str,
    ) -> LearningEvent:
        """
        Emit a Learning Event for runaway detection.
        
        Args:
            runaway_score: The runaway analysis result
            working_set: Current working set state
            current_state: Current runtime state
            
        Returns:
            The created LearningEvent
        """
        # Determine severity based on score
        if runaway_score.total_score >= 0.9:
            severity = "critical"
        elif runaway_score.total_score >= 0.8:
            severity = "high"
        elif runaway_score.total_score >= 0.7:
            severity = "medium"
        else:
            severity = "low"
        
        # Generate suggested lesson based on runaway type
        lessons = {
            "tool_spam": "Consider adding delay between tool calls or checking if action already completed",
            "thought_loop": "Break out of repetitive thinking - try a different approach or ask for help",
            "error_spiral": "Stop and analyze errors before retrying - pattern suggests fundamental issue",
            "generic": "Progress not being made - consider parking task and trying something else",
        }
        
        event = LearningEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            event_type="runaway",
            trigger_summary=f"Runaway detected: {runaway_score.runaway_type or 'unknown'} (score: {runaway_score.total_score:.2f})",
            state_at_trigger=current_state,
            working_set_summary={
                "last_intent": working_set.last_intent,
                "active_tasks": len(working_set.active_tasks),
                "tick_count": working_set.tick_count,
            },
            runaway_score=runaway_score.to_dict(),
            error_details=None,
            suggested_lesson=lessons.get(runaway_score.runaway_type or "generic", lessons["generic"]),
            pattern_signature=f"runaway:{runaway_score.runaway_type}:{working_set.last_intent[:20] if working_set.last_intent else 'none'}",
            severity=severity,
        )
        
        await self._store_event(event)
        logger.warning(f"Learning Event emitted: {event.trigger_summary}")
        
        return event
    
    async def emit_error_event(
        self,
        error: Exception,
        working_set: WorkingSet,
        current_state: str,
        context: str = "",
    ) -> LearningEvent:
        """
        Emit a Learning Event for an error pattern.
        
        Args:
            error: The exception that occurred
            working_set: Current working set state
            current_state: Current runtime state
            context: Additional context about what was being attempted
            
        Returns:
            The created LearningEvent
        """
        error_type = type(error).__name__
        error_msg = str(error)
        
        event = LearningEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            event_type="error_pattern",
            trigger_summary=f"Error: {error_type}: {error_msg[:100]}",
            state_at_trigger=current_state,
            working_set_summary={
                "last_intent": working_set.last_intent,
                "active_tasks": len(working_set.active_tasks),
                "tick_count": working_set.tick_count,
            },
            runaway_score=None,
            error_details=f"{error_type}: {error_msg}\nContext: {context}",
            suggested_lesson=f"Handle {error_type} errors - consider retry logic or graceful degradation",
            pattern_signature=f"error:{error_type}:{working_set.last_intent[:20] if working_set.last_intent else 'none'}",
            severity="medium",
        )
        
        await self._store_event(event)
        logger.warning(f"Learning Event emitted: {event.trigger_summary}")
        
        return event
    
    async def emit_budget_exhaust_event(
        self,
        working_set: WorkingSet,
        current_state: str,
        wait_time_s: float,
    ) -> LearningEvent:
        """
        Emit a Learning Event when budget is exhausted.
        
        Args:
            working_set: Current working set state
            current_state: Current runtime state
            wait_time_s: How long we had to wait
            
        Returns:
            The created LearningEvent
        """
        event = LearningEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            event_type="budget_exhaust",
            trigger_summary=f"Budget exhausted, waited {wait_time_s:.0f}s",
            state_at_trigger=current_state,
            working_set_summary={
                "last_intent": working_set.last_intent,
                "active_tasks": len(working_set.active_tasks),
                "tick_count": working_set.tick_count,
            },
            runaway_score=None,
            error_details=f"Budget wait time: {wait_time_s}s",
            suggested_lesson="Consider batching operations or reducing LLM calls - budget was exhausted",
            pattern_signature=f"budget:exhaust:{current_state}",
            severity="low" if wait_time_s < 60 else "medium",
        )
        
        await self._store_event(event)
        logger.info(f"Learning Event emitted: {event.trigger_summary}")
        
        return event
    
    async def _store_event(self, event: LearningEvent) -> None:
        """Store event in Qdrant."""
        if self._qdrant is None:
            logger.warning("Qdrant not connected, event not persisted")
            return
        
        try:
            # For now, store as JSON payload without embeddings
            # Future: add embeddings for semantic search
            from qdrant_client.models import PointStruct
            
            point = PointStruct(
                id=event.id,
                vector=[0.0] * 384,  # Placeholder vector (BGE-m3 dimension)
                payload=event.to_dict(),
            )
            
            self._qdrant.upsert(
                collection_name=self.collection_name,
                points=[point],
            )
            
            logger.debug(f"Stored Learning Event: {event.id}")
        except Exception as e:
            logger.error(f"Failed to store Learning Event: {e}")
    
    async def get_recent_events(self, limit: int = 10) -> list[LearningEvent]:
        """
        Get recent Learning Events.
        
        Args:
            limit: Maximum events to return
            
        Returns:
            List of recent events
        """
        if self._qdrant is None:
            return []
        
        try:
            from qdrant_client.models import Filter, FieldCondition, Range
            
            results = self._qdrant.scroll(
                collection_name=self.collection_name,
                limit=limit,
                with_payload=True,
            )
            
            events = []
            for point in results[0]:
                if point.payload:
                    events.append(LearningEvent.from_dict(point.payload))
            
            # Sort by timestamp descending
            events.sort(key=lambda e: e.timestamp, reverse=True)
            
            return events[:limit]
        except Exception as e:
            logger.error(f"Failed to get Learning Events: {e}")
            return []
