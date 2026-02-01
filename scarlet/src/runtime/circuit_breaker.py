"""
Circuit Breaker
===============

Prevents cascading failures with circuit breaker pattern.

ADR-006: Error Handling
SPEC-004: Section 10.2 - Circuit Breaker

States:
- CLOSED: Normal operation, requests allowed
- OPEN: Failures exceeded threshold, requests blocked
- HALF_OPEN: Testing if service recovered
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, TypeVar, Any

from .config import CircuitBreakerConfig

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Blocking requests
    HALF_OPEN = "half_open" # Testing recovery


@dataclass
class CircuitStats:
    """Circuit breaker statistics."""
    state: CircuitState
    failure_count: int
    success_count: int
    last_failure_time: float | None
    last_success_time: float | None
    half_open_calls: int
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "last_success_time": self.last_success_time,
            "half_open_calls": self.half_open_calls,
        }


class CircuitBreaker:
    """
    Circuit breaker for protecting against cascading failures.
    
    Usage:
        cb = CircuitBreaker(config)
        
        # Check before calling
        if cb.can_execute():
            try:
                result = await risky_operation()
                cb.record_success()
            except Exception as e:
                cb.record_failure()
                raise
    """
    
    def __init__(self, config: CircuitBreakerConfig, name: str = "default"):
        self.config = config
        self.name = name
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float | None = None
        self._last_success_time: float | None = None
        self._half_open_calls = 0
    
    @property
    def state(self) -> CircuitState:
        """Get current state, checking for timeout transitions."""
        if self._state == CircuitState.OPEN:
            # Check if timeout has passed
            if self._last_failure_time is not None:
                elapsed = time.time() - self._last_failure_time
                if elapsed >= self.config.reset_timeout_s:
                    logger.info(f"Circuit {self.name}: OPEN -> HALF_OPEN (timeout)")
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_calls = 0
        
        return self._state
    
    def can_execute(self) -> bool:
        """
        Check if a request can be executed.
        
        Returns:
            True if request is allowed
        """
        state = self.state  # This may update state
        
        if state == CircuitState.CLOSED:
            return True
        
        if state == CircuitState.OPEN:
            return False
        
        if state == CircuitState.HALF_OPEN:
            # Allow limited calls in half-open state
            return self._half_open_calls < self.config.half_open_max_calls
        
        return False
    
    def record_success(self) -> None:
        """Record a successful operation."""
        self._success_count += 1
        self._last_success_time = time.time()
        
        if self._state == CircuitState.HALF_OPEN:
            self._half_open_calls += 1
            
            # If enough successes in half-open, close circuit
            if self._half_open_calls >= self.config.half_open_max_calls:
                logger.info(f"Circuit {self.name}: HALF_OPEN -> CLOSED (recovered)")
                self._state = CircuitState.CLOSED
                self._failure_count = 0
        
        elif self._state == CircuitState.CLOSED:
            # Reset failure count on success
            self._failure_count = 0
    
    def record_failure(self) -> None:
        """Record a failed operation."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._state == CircuitState.HALF_OPEN:
            # Failure in half-open state reopens circuit
            logger.warning(f"Circuit {self.name}: HALF_OPEN -> OPEN (failure)")
            self._state = CircuitState.OPEN
            self._half_open_calls = 0
        
        elif self._state == CircuitState.CLOSED:
            # Check if we should open
            if self._failure_count >= self.config.error_threshold:
                logger.warning(f"Circuit {self.name}: CLOSED -> OPEN (threshold)")
                self._state = CircuitState.OPEN
    
    def get_stats(self) -> CircuitStats:
        """Get current statistics."""
        return CircuitStats(
            state=self.state,
            failure_count=self._failure_count,
            success_count=self._success_count,
            last_failure_time=self._last_failure_time,
            last_success_time=self._last_success_time,
            half_open_calls=self._half_open_calls,
        )
    
    def reset(self) -> None:
        """Reset circuit to closed state."""
        logger.info(f"Circuit {self.name}: Reset to CLOSED")
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._half_open_calls = 0
    
    async def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Async function to execute
            *args, **kwargs: Arguments to pass
            
        Returns:
            Function result
            
        Raises:
            CircuitOpenError: If circuit is open
            Original exception: If function fails
        """
        if not self.can_execute():
            raise CircuitOpenError(f"Circuit {self.name} is open")
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            self.record_success()
            return result
        
        except Exception:
            self.record_failure()
            raise


class CircuitOpenError(Exception):
    """Raised when trying to execute through an open circuit."""
    pass
