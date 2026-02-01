"""
Metrics Collection
==================

Collects and exposes runtime metrics for monitoring.

ADR-006: Monitoring
SPEC-004: Section 11 - Metriche Day-1
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from redis.asyncio import Redis

logger = logging.getLogger(__name__)


@dataclass
class TickMetrics:
    """Metrics for a single tick."""
    tick_id: str
    timestamp: datetime
    duration_s: float
    state: str
    llm_triggered: bool
    budget_remaining: int
    runaway_score: float
    had_error: bool
    had_progress: bool


@dataclass
class RuntimeMetrics:
    """Aggregated runtime metrics."""
    # Counters
    total_ticks: int = 0
    total_llm_calls: int = 0
    total_errors: int = 0
    total_runaway_detections: int = 0
    
    # Current state
    current_state: str = "idle"
    uptime_s: float = 0.0
    
    # Recent history
    recent_tick_durations: list[float] = field(default_factory=list)
    recent_runaway_scores: list[float] = field(default_factory=list)
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.utcnow)
    last_tick_at: datetime | None = None
    last_error_at: datetime | None = None
    
    def to_dict(self) -> dict:
        """Serialize to dictionary (for Prometheus/JSON)."""
        avg_tick_duration = (
            sum(self.recent_tick_durations) / len(self.recent_tick_durations)
            if self.recent_tick_durations else 0.0
        )
        
        return {
            "runtime_total_ticks": self.total_ticks,
            "runtime_total_llm_calls": self.total_llm_calls,
            "runtime_total_errors": self.total_errors,
            "runtime_total_runaway_detections": self.total_runaway_detections,
            "runtime_current_state": self.current_state,
            "runtime_uptime_seconds": self.uptime_s,
            "runtime_avg_tick_duration_seconds": avg_tick_duration,
            "runtime_last_tick_timestamp": self.last_tick_at.isoformat() if self.last_tick_at else None,
        }


class MetricsCollector:
    """
    Collects and manages runtime metrics.
    
    Metrics are stored in Redis for persistence and
    exposed via HTTP endpoint for monitoring.
    """
    
    def __init__(self, key_prefix: str = "scarlet:runtime:"):
        self.key_prefix = key_prefix
        self._redis: Redis | None = None
        self._metrics = RuntimeMetrics()
        self._start_time = time.time()
    
    def set_redis(self, redis: Redis) -> None:
        """Set Redis connection."""
        self._redis = redis
    
    def record_tick(
        self,
        tick_id: str,
        duration_s: float,
        state: str,
        llm_triggered: bool,
        budget_remaining: int,
        runaway_score: float,
        had_error: bool,
        had_progress: bool,
    ) -> None:
        """Record metrics for a tick."""
        self._metrics.total_ticks += 1
        self._metrics.current_state = state
        self._metrics.last_tick_at = datetime.utcnow()
        self._metrics.uptime_s = time.time() - self._start_time
        
        if llm_triggered:
            self._metrics.total_llm_calls += 1
        
        if had_error:
            self._metrics.total_errors += 1
            self._metrics.last_error_at = datetime.utcnow()
        
        if runaway_score >= 0.7:  # Threshold
            self._metrics.total_runaway_detections += 1
        
        # Keep recent history (last 100)
        self._metrics.recent_tick_durations.append(duration_s)
        if len(self._metrics.recent_tick_durations) > 100:
            self._metrics.recent_tick_durations = self._metrics.recent_tick_durations[-100:]
        
        self._metrics.recent_runaway_scores.append(runaway_score)
        if len(self._metrics.recent_runaway_scores) > 100:
            self._metrics.recent_runaway_scores = self._metrics.recent_runaway_scores[-100:]
        
        logger.debug(
            f"Tick {tick_id}: {duration_s:.2f}s, state={state}, "
            f"llm={llm_triggered}, budget={budget_remaining}"
        )
    
    def get_metrics(self) -> RuntimeMetrics:
        """Get current metrics."""
        self._metrics.uptime_s = time.time() - self._start_time
        return self._metrics
    
    def get_prometheus_metrics(self) -> str:
        """
        Get metrics in Prometheus format.
        
        Returns:
            Prometheus-formatted metrics string
        """
        m = self.get_metrics()
        
        lines = [
            "# HELP runtime_total_ticks Total number of ticks processed",
            "# TYPE runtime_total_ticks counter",
            f"runtime_total_ticks {m.total_ticks}",
            "",
            "# HELP runtime_total_llm_calls Total LLM API calls",
            "# TYPE runtime_total_llm_calls counter",
            f"runtime_total_llm_calls {m.total_llm_calls}",
            "",
            "# HELP runtime_total_errors Total errors encountered",
            "# TYPE runtime_total_errors counter",
            f"runtime_total_errors {m.total_errors}",
            "",
            "# HELP runtime_total_runaway_detections Total runaway detections",
            "# TYPE runtime_total_runaway_detections counter",
            f"runtime_total_runaway_detections {m.total_runaway_detections}",
            "",
            "# HELP runtime_uptime_seconds Runtime uptime in seconds",
            "# TYPE runtime_uptime_seconds gauge",
            f"runtime_uptime_seconds {m.uptime_s:.2f}",
            "",
        ]
        
        if m.recent_tick_durations:
            avg = sum(m.recent_tick_durations) / len(m.recent_tick_durations)
            lines.extend([
                "# HELP runtime_avg_tick_duration_seconds Average tick duration",
                "# TYPE runtime_avg_tick_duration_seconds gauge",
                f"runtime_avg_tick_duration_seconds {avg:.4f}",
                "",
            ])
        
        if m.recent_runaway_scores:
            avg = sum(m.recent_runaway_scores) / len(m.recent_runaway_scores)
            lines.extend([
                "# HELP runtime_avg_runaway_score Average runaway score",
                "# TYPE runtime_avg_runaway_score gauge",
                f"runtime_avg_runaway_score {avg:.4f}",
                "",
            ])
        
        return "\n".join(lines)
    
    async def persist(self) -> None:
        """Persist metrics to Redis."""
        if self._redis is None:
            return
        
        try:
            import json
            key = f"{self.key_prefix}metrics"
            data = json.dumps(self._metrics.to_dict())
            await self._redis.set(key, data)
        except Exception as e:
            logger.error(f"Failed to persist metrics: {e}")
    
    async def load(self) -> None:
        """Load metrics from Redis."""
        if self._redis is None:
            return
        
        try:
            import json
            key = f"{self.key_prefix}metrics"
            data = await self._redis.get(key)
            if data:
                stored = json.loads(data)
                self._metrics.total_ticks = stored.get("runtime_total_ticks", 0)
                self._metrics.total_llm_calls = stored.get("runtime_total_llm_calls", 0)
                self._metrics.total_errors = stored.get("runtime_total_errors", 0)
                logger.info(f"Loaded metrics: {self._metrics.total_ticks} ticks")
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")
