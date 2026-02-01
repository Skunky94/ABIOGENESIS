"""
Scarlet Autonomy Runtime
========================

Continuous existence loop for Scarlet - Layer 1 implementation.

Architecture Decision: ADR-006
Specification: SPEC-004

This package provides:
- Main loop orchestrator (loop.py)
- State machine (state.py)
- Budget tracking (budget.py)
- Working set management (working_set.py)
- Runaway detection (runaway.py)
- Learning events (learning_events.py)
- Circuit breaker (circuit_breaker.py)
- Metrics collection (metrics.py)
- Configuration loading (config.py)
"""

__version__ = "1.0.0"

from .config import RuntimeConfig, load_config
from .state import RuntimeState, StateTransitionRequest, TransitionType
from .loop import AutonomyRuntime

__all__ = [
    "RuntimeConfig",
    "load_config",
    "RuntimeState",
    "StateTransitionRequest",
    "TransitionType",
    "AutonomyRuntime",
]
