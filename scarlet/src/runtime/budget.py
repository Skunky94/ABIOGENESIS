"""
Budget Tracker
==============

Tracks MiniMax API quota usage with rolling window.

ADR-006: Decision 5 - Budget Tracking
SPEC-004: Section 6 - Budget e Quota

Key features:
- Rolling window (5000 requests / 5 hours)
- Shared budget with Sleep Agent
- Non-destructive throttling (wait, don't error)
- Reserve for sleep agent
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from redis.asyncio import Redis

from .config import BudgetConfig

logger = logging.getLogger(__name__)


@dataclass
class BudgetSnapshot:
    """
    Current budget state.
    
    Provided in EnvironmentSnapshot for each tick.
    """
    requests_used: int
    requests_limit: int
    window_seconds: int
    remaining: int
    usage_percent: float
    is_throttled: bool
    is_exhausted: bool
    reserve_available: int
    oldest_request_age_s: float | None
    
    @property
    def can_make_request(self) -> bool:
        """Check if a request can be made (with reserve)."""
        return self.remaining > 0
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "requests_used": self.requests_used,
            "requests_limit": self.requests_limit,
            "window_seconds": self.window_seconds,
            "remaining": self.remaining,
            "usage_percent": self.usage_percent,
            "is_throttled": self.is_throttled,
            "is_exhausted": self.is_exhausted,
            "reserve_available": self.reserve_available,
            "oldest_request_age_s": self.oldest_request_age_s,
        }


class BudgetTracker:
    """
    Tracks API request budget using Redis sorted set.
    
    Key: {prefix}budget:requests
    Type: Sorted Set (timestamp as score, request_id as member)
    """
    
    def __init__(self, config: BudgetConfig, key_prefix: str = "scarlet:runtime:"):
        self.config = config
        self.key = f"{key_prefix}budget:requests"
        self._redis: Redis | None = None
    
    def set_redis(self, redis: Redis) -> None:
        """Set Redis connection."""
        self._redis = redis
    
    async def record_request(self, request_id: str | None = None) -> str:
        """
        Record a request in the budget.
        
        Args:
            request_id: Optional request ID, generated if not provided
            
        Returns:
            The request ID
        """
        if self._redis is None:
            raise RuntimeError("Redis not connected")
        
        if request_id is None:
            request_id = str(uuid.uuid4())
        
        now = time.time()
        
        # Add to sorted set with timestamp as score
        await self._redis.zadd(self.key, {request_id: now})
        
        # Cleanup old entries
        window_start = now - self.config.window_seconds
        await self._redis.zremrangebyscore(self.key, 0, window_start)
        
        logger.debug(f"Recorded request {request_id}")
        
        return request_id
    
    async def get_snapshot(self) -> BudgetSnapshot:
        """
        Get current budget snapshot.
        
        Returns:
            BudgetSnapshot with current state
        """
        if self._redis is None:
            # Return default snapshot if Redis not connected
            return BudgetSnapshot(
                requests_used=0,
                requests_limit=self.config.requests_limit,
                window_seconds=self.config.window_seconds,
                remaining=self.config.requests_limit,
                usage_percent=0.0,
                is_throttled=False,
                is_exhausted=False,
                reserve_available=self.config.reserve_for_sleep,
                oldest_request_age_s=None,
            )
        
        now = time.time()
        window_start = now - self.config.window_seconds
        
        # Count requests in window
        requests_used = await self._redis.zcount(self.key, window_start, now)
        
        # Calculate effective limit (excluding reserve)
        effective_limit = self.config.requests_limit - self.config.reserve_for_sleep
        remaining = max(0, effective_limit - requests_used)
        
        # Usage percent
        usage_percent = requests_used / self.config.requests_limit if self.config.requests_limit > 0 else 0
        
        # Get oldest request age
        oldest = await self._redis.zrange(self.key, 0, 0, withscores=True)
        oldest_age = (now - oldest[0][1]) if oldest else None
        
        return BudgetSnapshot(
            requests_used=requests_used,
            requests_limit=self.config.requests_limit,
            window_seconds=self.config.window_seconds,
            remaining=remaining,
            usage_percent=usage_percent,
            is_throttled=usage_percent >= self.config.throttle_threshold,
            is_exhausted=remaining <= 0,
            reserve_available=max(0, self.config.requests_limit - requests_used),
            oldest_request_age_s=oldest_age,
        )
    
    async def get_remaining(self) -> int:
        """
        Get remaining budget (quick check).
        
        Returns:
            Number of requests remaining
        """
        snapshot = await self.get_snapshot()
        return snapshot.remaining
    
    async def wait_for_budget(self, timeout_s: float = 300.0) -> bool:
        """
        Wait until budget is available.
        
        Non-destructive throttling: we wait, not error.
        
        Args:
            timeout_s: Maximum time to wait
            
        Returns:
            True if budget became available, False if timeout
        """
        import asyncio
        
        start = time.time()
        check_interval = 5.0  # Check every 5 seconds
        
        while time.time() - start < timeout_s:
            snapshot = await self.get_snapshot()
            
            if snapshot.can_make_request:
                return True
            
            # Calculate wait time based on oldest request expiry
            if snapshot.oldest_request_age_s is not None:
                time_until_expiry = self.config.window_seconds - snapshot.oldest_request_age_s
                wait_time = min(check_interval, max(1.0, time_until_expiry))
            else:
                wait_time = check_interval
            
            logger.info(
                f"Budget exhausted ({snapshot.requests_used}/{snapshot.requests_limit}). "
                f"Waiting {wait_time:.1f}s..."
            )
            
            await asyncio.sleep(wait_time)
        
        return False
    
    async def calculate_throttle_interval(self, base_interval: float) -> float:
        """
        Calculate tick interval based on budget usage.
        
        When budget is high, we increase interval to conserve.
        
        Args:
            base_interval: Base tick interval in seconds
            
        Returns:
            Adjusted interval
        """
        snapshot = await self.get_snapshot()
        
        if snapshot.is_exhausted:
            # Maximum interval when exhausted
            return base_interval * 10
        
        if snapshot.is_throttled:
            # Double interval when throttled
            return base_interval * 2
        
        # Linear scaling based on usage
        # At 80% usage, interval is 1.5x base
        if snapshot.usage_percent > 0.5:
            factor = 1.0 + (snapshot.usage_percent - 0.5)
            return base_interval * factor
        
        return base_interval
    
    async def get_metrics(self) -> dict:
        """
        Get budget metrics for monitoring.
        
        Returns:
            Dictionary of metrics
        """
        snapshot = await self.get_snapshot()
        
        return {
            "budget_requests_used": snapshot.requests_used,
            "budget_requests_limit": snapshot.requests_limit,
            "budget_remaining": snapshot.remaining,
            "budget_usage_percent": snapshot.usage_percent,
            "budget_is_throttled": int(snapshot.is_throttled),
            "budget_is_exhausted": int(snapshot.is_exhausted),
        }
