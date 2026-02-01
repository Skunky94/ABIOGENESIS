"""
Runaway Detection
=================

Detects pathological loops (runaway) based on lack of progress.

ADR-006: Decision 6 - Runaway Detection
SPEC-004: Section 7 - Runaway Detection

Key principle: Runaway = continuity without observable progress.
NOT runaway: tool usage, legitimate repetition, infinite loop (by design).
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from redis.asyncio import Redis

from .config import RunawayConfig
from .working_set import ProgressMarker

logger = logging.getLogger(__name__)


@dataclass
class TickSignature:
    """
    Signature of a tick for repetition detection.
    
    We hash key aspects of the tick to detect repetitive patterns.
    """
    tick_id: str
    timestamp: datetime
    state: str
    intent_hash: str
    action_hash: str | None
    had_progress: bool
    had_error: bool
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "tick_id": self.tick_id,
            "timestamp": self.timestamp.isoformat(),
            "state": self.state,
            "intent_hash": self.intent_hash,
            "action_hash": self.action_hash,
            "had_progress": self.had_progress,
            "had_error": self.had_error,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> TickSignature:
        """Deserialize from dictionary."""
        return cls(
            tick_id=data["tick_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            state=data["state"],
            intent_hash=data["intent_hash"],
            action_hash=data.get("action_hash"),
            had_progress=data.get("had_progress", False),
            had_error=data.get("had_error", False),
        )


@dataclass
class RunawayScore:
    """
    Result of runaway analysis.
    """
    total_score: float              # 0..1
    is_runaway: bool                # score >= threshold
    consecutive_high: int           # Consecutive ticks above threshold
    
    # Component scores
    progress_absence_score: float   # 0..1
    trigger_density_score: float    # 0..1
    signature_repetition_score: float  # 0..1
    error_streak_score: float       # 0..1
    
    # Details
    analysis_window_ticks: int
    progress_markers_in_window: int
    unique_signatures_in_window: int
    errors_in_window: int
    
    runaway_type: str | None = None  # tool_spam, thought_loop, etc.
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "total_score": self.total_score,
            "is_runaway": self.is_runaway,
            "consecutive_high": self.consecutive_high,
            "progress_absence_score": self.progress_absence_score,
            "trigger_density_score": self.trigger_density_score,
            "signature_repetition_score": self.signature_repetition_score,
            "error_streak_score": self.error_streak_score,
            "analysis_window_ticks": self.analysis_window_ticks,
            "progress_markers_in_window": self.progress_markers_in_window,
            "unique_signatures_in_window": self.unique_signatures_in_window,
            "errors_in_window": self.errors_in_window,
            "runaway_type": self.runaway_type,
        }


class RunawayDetector:
    """
    Detects runaway behavior based on multi-factor scoring.
    
    Factors:
    - progress_absence: No progress markers in window
    - trigger_density: Too many LLM triggers per minute
    - signature_repetition: Same tick signatures repeating
    - error_streak: Consecutive errors
    """
    
    def __init__(self, config: RunawayConfig, key_prefix: str = "scarlet:runtime:"):
        self.config = config
        self.history_key = f"{key_prefix}runaway:history"
        self.consecutive_key = f"{key_prefix}runaway:consecutive"
        self._redis: Redis | None = None
        
        # In-memory history for quick access
        self._history: list[TickSignature] = []
        self._consecutive_high: int = 0
    
    def set_redis(self, redis: Redis) -> None:
        """Set Redis connection."""
        self._redis = redis
    
    def record_tick(
        self,
        tick_id: str,
        state: str,
        intent: str,
        action: str | None,
        progress_markers: list[ProgressMarker],
        had_error: bool,
    ) -> None:
        """
        Record a tick for runaway analysis.
        
        Args:
            tick_id: Unique tick identifier
            state: Current runtime state
            intent: Scarlet's intent for this tick
            action: Action taken (if any)
            progress_markers: New progress markers this tick
            had_error: Whether an error occurred
        """
        signature = TickSignature(
            tick_id=tick_id,
            timestamp=datetime.utcnow(),
            state=state,
            intent_hash=self._hash_text(intent),
            action_hash=self._hash_text(action) if action else None,
            had_progress=len(progress_markers) > 0,
            had_error=had_error,
        )
        
        self._history.append(signature)
        
        # Keep only window_ticks
        if len(self._history) > self.config.window_ticks:
            self._history = self._history[-self.config.window_ticks:]
    
    def analyze(self) -> RunawayScore:
        """
        Analyze recent history for runaway behavior.
        
        Returns:
            RunawayScore with analysis results
        """
        if len(self._history) < 3:
            # Not enough data
            return RunawayScore(
                total_score=0.0,
                is_runaway=False,
                consecutive_high=0,
                progress_absence_score=0.0,
                trigger_density_score=0.0,
                signature_repetition_score=0.0,
                error_streak_score=0.0,
                analysis_window_ticks=len(self._history),
                progress_markers_in_window=0,
                unique_signatures_in_window=len(self._history),
                errors_in_window=0,
            )
        
        window = self._history[-self.config.window_ticks:]
        
        # 1. Progress absence score
        ticks_with_progress = sum(1 for t in window if t.had_progress)
        progress_absence_score = 1.0 - (ticks_with_progress / len(window))
        
        # 2. Trigger density score (simplified - based on window time span)
        if len(window) >= 2:
            time_span = (window[-1].timestamp - window[0].timestamp).total_seconds()
            if time_span > 0:
                ticks_per_minute = (len(window) / time_span) * 60
                # Normalize: 10+ ticks/min = 1.0, 2 ticks/min = 0.0
                trigger_density_score = min(1.0, max(0.0, (ticks_per_minute - 2) / 8))
            else:
                trigger_density_score = 0.5
        else:
            trigger_density_score = 0.0
        
        # 3. Signature repetition score
        intent_hashes = [t.intent_hash for t in window]
        unique_intents = len(set(intent_hashes))
        # If all same intent = 1.0, all different = 0.0
        signature_repetition_score = 1.0 - (unique_intents / len(window))
        
        # 4. Error streak score
        consecutive_errors = 0
        for t in reversed(window):
            if t.had_error:
                consecutive_errors += 1
            else:
                break
        # Normalize: 5+ errors = 1.0
        error_streak_score = min(1.0, consecutive_errors / 5)
        
        # Calculate weighted total
        weights = self.config.weights
        total_score = (
            weights.progress_absence * progress_absence_score +
            weights.trigger_density * trigger_density_score +
            weights.signature_repetition * signature_repetition_score +
            weights.error_streak * error_streak_score
        )
        
        # Check if runaway
        is_high = total_score >= self.config.score_threshold
        
        if is_high:
            self._consecutive_high += 1
        else:
            self._consecutive_high = 0
        
        is_runaway = self._consecutive_high >= self.config.consecutive_ticks
        
        # Determine runaway type
        runaway_type = None
        if is_runaway:
            if signature_repetition_score > 0.7 and progress_absence_score > 0.5:
                runaway_type = "tool_spam"
            elif progress_absence_score > 0.8:
                runaway_type = "thought_loop"
            elif error_streak_score > 0.6:
                runaway_type = "error_spiral"
            else:
                runaway_type = "generic"
        
        return RunawayScore(
            total_score=total_score,
            is_runaway=is_runaway,
            consecutive_high=self._consecutive_high,
            progress_absence_score=progress_absence_score,
            trigger_density_score=trigger_density_score,
            signature_repetition_score=signature_repetition_score,
            error_streak_score=error_streak_score,
            analysis_window_ticks=len(window),
            progress_markers_in_window=ticks_with_progress,
            unique_signatures_in_window=unique_intents,
            errors_in_window=sum(1 for t in window if t.had_error),
            runaway_type=runaway_type,
        )
    
    def _hash_text(self, text: str) -> str:
        """Create a short hash of text for comparison."""
        return hashlib.md5(text.encode()).hexdigest()[:8]
    
    def reset(self) -> None:
        """Reset runaway history (e.g., after mitigation)."""
        self._history = []
        self._consecutive_high = 0
        logger.info("Runaway history reset")
    
    def get_metrics(self) -> dict:
        """Get metrics for monitoring."""
        score = self.analyze()
        return {
            "runaway_score": score.total_score,
            "runaway_consecutive": score.consecutive_high,
            "runaway_is_active": int(score.is_runaway),
            "runaway_progress_absence": score.progress_absence_score,
            "runaway_signature_repetition": score.signature_repetition_score,
        }
