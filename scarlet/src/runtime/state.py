"""
State Machine
=============

Runtime state management with validated transitions.

ADR-006: Decision 4 - State Machine
SPEC-004: Section 5 - State Machine

States:
- IDLE: Proactive exploration (NOT passive waiting)
- THINKING: Processing/deciding on specific task
- ACTING: Executing action
- SLEEPING: Authentic sleep cycle (⚠️ PLACEHOLDER - see ROADMAP L3.4)
- DREAMING: Dream processing (⚠️ PLACEHOLDER - see ROADMAP L3.4)
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Literal

from .config import RuntimeConfig, IdleActivityConfig

logger = logging.getLogger(__name__)


class RuntimeState(str, Enum):
    """
    Runtime states for Scarlet's continuous existence.
    
    Note: SLEEPING and DREAMING are defined but NOT IMPLEMENTED yet.
    They will be enabled when ROADMAP L3.4 is implemented.
    """
    IDLE = "idle"           # Proactive exploration (NOT passive waiting)
    THINKING = "thinking"   # Processing/deciding on specific task
    ACTING = "acting"       # Executing action
    SLEEPING = "sleeping"   # ⚠️ Placeholder - Future L3.4
    DREAMING = "dreaming"   # ⚠️ Placeholder - Future L3.4


class TransitionType(str, Enum):
    """
    Types of state transitions.
    
    Note: EXPLORE (not IDLE) to clarify this is proactive behavior.
    """
    CONTINUE_TASK = "continue_task"     # Resume ongoing task
    START_TASK = "start_task"           # Start new task
    EXPLORE = "explore"                 # Enter proactive IDLE exploration
    SLEEP = "sleep"                     # Enter sleeping (future)
    DREAM = "dream"                     # Enter dreaming (future)
    SAFE_MODE = "safe_mode"             # Conservative mode


class Override(str, Enum):
    """External overrides that can be applied to the runtime."""
    SAFE_MODE = "safe_mode"     # Reduce trigger rate, disable expensive actions
    PAUSE = "pause"             # No LLM triggers (health only)
    RESUME = "resume"           # Resume normal operation


@dataclass
class StateTransitionRequest:
    """
    Request from LLM to transition state.
    
    The runtime VALIDATES this request against allowed transitions.
    LLM doesn't write state directly - it proposes transitions.
    """
    desired_state: RuntimeState
    transition_type: TransitionType
    reason: str
    continuation_ref: str | None = None     # Link to task/progress
    idle_activity: str | None = None        # IDLE activity chosen (if EXPLORE)
    confidence: float | None = None         # 0..1 (optional)
    suggested_next_tick_s: float | None = None  # Hint (runtime decides)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "desired_state": self.desired_state.value,
            "transition_type": self.transition_type.value,
            "reason": self.reason,
            "continuation_ref": self.continuation_ref,
            "idle_activity": self.idle_activity,
            "confidence": self.confidence,
            "suggested_next_tick_s": self.suggested_next_tick_s,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> StateTransitionRequest:
        """Deserialize from dictionary."""
        return cls(
            desired_state=RuntimeState(data["desired_state"]),
            transition_type=TransitionType(data["transition_type"]),
            reason=data.get("reason", ""),
            continuation_ref=data.get("continuation_ref"),
            idle_activity=data.get("idle_activity"),
            confidence=data.get("confidence"),
            suggested_next_tick_s=data.get("suggested_next_tick_s"),
        )


@dataclass
class IdleActivity:
    """
    Activity chosen during IDLE state (proactive exploration).
    
    A sentient being never "waits passively". In IDLE, Scarlet:
    - memory_wandering: Recalls old memories to rebuild continuity
    - self_reflection: Thinks about recent actions
    - capability_audit: Examines own capabilities
    - curiosity_research: Searches for interesting information
    - goal_contemplation: Reflects on goals and desires
    - relationship_review: Thinks about known people
    """
    activity_type: Literal[
        "memory_wandering",
        "self_reflection",
        "capability_audit",
        "curiosity_research",
        "goal_contemplation",
        "relationship_review",
    ]
    trigger: str                    # What triggered this activity
    duration_ticks: int             # How many ticks to dedicate
    started_at: datetime = field(default_factory=datetime.utcnow)
    output: str | None = None       # Insight generated (if any)
    ticks_elapsed: int = 0


@dataclass
class StateContext:
    """
    Current state context maintained by runtime.
    """
    current_state: RuntimeState
    previous_state: RuntimeState | None = None
    state_entered_at: datetime = field(default_factory=datetime.utcnow)
    ticks_in_state: int = 0
    active_overrides: list[Override] = field(default_factory=list)
    current_idle_activity: IdleActivity | None = None
    idle_ticks_total: int = 0       # Total IDLE ticks (for sleep_after_ticks)
    last_transition: StateTransitionRequest | None = None


class StateMachine:
    """
    State machine for Scarlet's continuous existence.
    
    Validates transitions against config and manages state context.
    """
    
    # States that are implemented in L1
    IMPLEMENTED_STATES = {RuntimeState.IDLE, RuntimeState.THINKING, RuntimeState.ACTING}
    
    # States that are placeholders for future implementation
    PLACEHOLDER_STATES = {RuntimeState.SLEEPING, RuntimeState.DREAMING}
    
    def __init__(self, config: RuntimeConfig):
        self.config = config
        self.context = StateContext(
            current_state=RuntimeState(config.states.initial)
        )
        self._last_activity_times: dict[str, datetime] = {}
    
    @property
    def current_state(self) -> RuntimeState:
        """Get current state."""
        return self.context.current_state
    
    @property
    def is_paused(self) -> bool:
        """Check if runtime is paused."""
        return Override.PAUSE in self.context.active_overrides
    
    @property
    def is_safe_mode(self) -> bool:
        """Check if runtime is in safe mode."""
        return Override.SAFE_MODE in self.context.active_overrides
    
    def validate_transition(self, request: StateTransitionRequest) -> tuple[bool, str]:
        """
        Validate a state transition request.
        
        Returns:
            (is_valid, reason)
        """
        # Check if target state is a placeholder
        if request.desired_state in self.PLACEHOLDER_STATES:
            return False, f"State {request.desired_state.value} is a placeholder (see ROADMAP L3.4)"
        
        # Check if transition is allowed
        allowed = self.config.states.allowed_transitions.get(
            self.current_state.value, []
        )
        
        if request.desired_state.value not in allowed:
            return False, (
                f"Transition from {self.current_state.value} to "
                f"{request.desired_state.value} not allowed. "
                f"Allowed: {allowed}"
            )
        
        # Check overrides
        if self.is_paused and request.desired_state != RuntimeState.IDLE:
            return False, "Runtime is paused, only IDLE state allowed"
        
        # Validate IDLE activity if transitioning to IDLE
        if request.desired_state == RuntimeState.IDLE and request.idle_activity:
            if request.idle_activity not in self.config.idle.activities:
                return False, f"Unknown IDLE activity: {request.idle_activity}"
            
            activity_config = self.config.idle.activities[request.idle_activity]
            if not activity_config.enabled:
                return False, f"IDLE activity {request.idle_activity} is disabled"
            
            # Check cooldown
            if activity_config.cooldown_hours:
                last_time = self._last_activity_times.get(request.idle_activity)
                if last_time:
                    hours_since = (datetime.utcnow() - last_time).total_seconds() / 3600
                    if hours_since < activity_config.cooldown_hours:
                        return False, (
                            f"IDLE activity {request.idle_activity} is on cooldown "
                            f"({activity_config.cooldown_hours - hours_since:.1f}h remaining)"
                        )
        
        return True, "OK"
    
    def apply_transition(self, request: StateTransitionRequest) -> bool:
        """
        Apply a validated state transition.
        
        Returns:
            True if transition was applied
        """
        is_valid, reason = self.validate_transition(request)
        
        if not is_valid:
            logger.warning(f"Invalid transition rejected: {reason}")
            return False
        
        # Save previous state
        self.context.previous_state = self.context.current_state
        
        # Update state
        self.context.current_state = request.desired_state
        self.context.state_entered_at = datetime.utcnow()
        self.context.ticks_in_state = 0
        self.context.last_transition = request
        
        # Handle IDLE-specific logic
        if request.desired_state == RuntimeState.IDLE:
            self.context.idle_ticks_total += 1
            
            if request.idle_activity:
                activity_config = self.config.idle.activities[request.idle_activity]
                self.context.current_idle_activity = IdleActivity(
                    activity_type=request.idle_activity,  # type: ignore
                    trigger=request.reason,
                    duration_ticks=activity_config.max_ticks,
                )
                self._last_activity_times[request.idle_activity] = datetime.utcnow()
        else:
            self.context.current_idle_activity = None
        
        logger.info(
            f"State transition: {self.context.previous_state.value} -> "
            f"{request.desired_state.value} ({request.reason})"
        )
        
        return True
    
    def tick(self) -> None:
        """Called each tick to update state context."""
        self.context.ticks_in_state += 1
        
        # Update IDLE activity if active
        if self.context.current_idle_activity:
            self.context.current_idle_activity.ticks_elapsed += 1
    
    def select_idle_activity(self) -> str | None:
        """
        Select an IDLE activity based on weights and cooldowns.
        
        Returns:
            Activity name or None if none available
        """
        available = []
        weights = []
        
        for name, config in self.config.idle.activities.items():
            if not config.enabled:
                continue
            
            # Check cooldown
            if config.cooldown_hours:
                last_time = self._last_activity_times.get(name)
                if last_time:
                    hours_since = (datetime.utcnow() - last_time).total_seconds() / 3600
                    if hours_since < config.cooldown_hours:
                        continue
            
            available.append(name)
            weights.append(config.weight)
        
        if not available:
            return None
        
        # Normalize weights
        total = sum(weights)
        if total == 0:
            return random.choice(available)
        
        weights = [w / total for w in weights]
        
        return random.choices(available, weights=weights, k=1)[0]
    
    def should_consider_sleep(self) -> bool:
        """
        Check if runtime should consider transitioning to SLEEPING.
        
        Note: SLEEPING is a placeholder (L3.4), this is for future use.
        """
        return self.context.idle_ticks_total >= self.config.idle.sleep_after_ticks
    
    def add_override(self, override: Override) -> None:
        """Add an external override."""
        if override == Override.RESUME:
            # RESUME removes other overrides
            self.context.active_overrides = []
            logger.info("Overrides cleared (RESUME)")
        elif override not in self.context.active_overrides:
            self.context.active_overrides.append(override)
            logger.info(f"Override added: {override.value}")
    
    def remove_override(self, override: Override) -> None:
        """Remove an external override."""
        if override in self.context.active_overrides:
            self.context.active_overrides.remove(override)
            logger.info(f"Override removed: {override.value}")
    
    def to_dict(self) -> dict:
        """Serialize state context to dictionary."""
        return {
            "current_state": self.context.current_state.value,
            "previous_state": self.context.previous_state.value if self.context.previous_state else None,
            "state_entered_at": self.context.state_entered_at.isoformat(),
            "ticks_in_state": self.context.ticks_in_state,
            "active_overrides": [o.value for o in self.context.active_overrides],
            "idle_ticks_total": self.context.idle_ticks_total,
            "current_idle_activity": {
                "type": self.context.current_idle_activity.activity_type,
                "trigger": self.context.current_idle_activity.trigger,
                "ticks_elapsed": self.context.current_idle_activity.ticks_elapsed,
            } if self.context.current_idle_activity else None,
        }
    
    def from_dict(self, data: dict) -> None:
        """Restore state context from dictionary."""
        self.context.current_state = RuntimeState(data["current_state"])
        self.context.previous_state = RuntimeState(data["previous_state"]) if data.get("previous_state") else None
        self.context.state_entered_at = datetime.fromisoformat(data["state_entered_at"])
        self.context.ticks_in_state = data.get("ticks_in_state", 0)
        self.context.active_overrides = [Override(o) for o in data.get("active_overrides", [])]
        self.context.idle_ticks_total = data.get("idle_ticks_total", 0)
