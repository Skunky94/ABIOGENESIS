"""
Unit Tests for Autonomy Runtime
================================

ADR-006: Continuous Existence Runtime
SPEC-004: Continuous Existence

These tests verify the runtime components work correctly.
"""

import asyncio
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# =============================================================================
# Config Tests
# =============================================================================

class TestConfig:
    """Test config loading."""
    
    def test_load_config_from_yaml(self):
        """Test loading config from YAML file."""
        from runtime.config import load_config
        
        # Use test config
        config = load_config()
        
        assert config is not None
        assert config.loop is not None
        assert config.letta is not None
        assert config.budget is not None
        
    def test_config_defaults(self):
        """Test config has sensible defaults."""
        from runtime.config import load_config
        
        config = load_config()
        
        # Verify defaults
        assert config.loop.tick_interval_base_s == 30
        assert config.budget.requests_limit == 5000
        assert config.budget.window_seconds == 18000  # 5 hours


# =============================================================================
# State Machine Tests
# =============================================================================

class TestStateMachine:
    """Test state machine transitions."""
    
    def test_initial_state_is_idle(self):
        """Test state machine starts in IDLE."""
        from runtime.state import StateMachine, RuntimeState
        from runtime.config import load_config
        
        config = load_config()
        sm = StateMachine(config)
        
        assert sm.current_state == RuntimeState.IDLE
    
    def test_valid_transition_idle_to_thinking(self):
        """Test valid transition IDLE -> THINKING."""
        from runtime.state import (
            StateMachine, RuntimeState, 
            StateTransitionRequest, TransitionType
        )
        from runtime.config import load_config
        
        config = load_config()
        sm = StateMachine(config)
        
        request = StateTransitionRequest(
            desired_state=RuntimeState.THINKING,
            transition_type=TransitionType.START_TASK,
            reason="Testing transition",
        )
        
        result = sm.apply_transition(request)
        
        assert result is True
        assert sm.current_state == RuntimeState.THINKING
    
    def test_valid_transition_thinking_to_acting(self):
        """Test valid transition THINKING -> ACTING."""
        from runtime.state import (
            StateMachine, RuntimeState,
            StateTransitionRequest, TransitionType
        )
        from runtime.config import load_config
        
        config = load_config()
        sm = StateMachine(config)
        
        # First go to THINKING
        sm.apply_transition(StateTransitionRequest(
            desired_state=RuntimeState.THINKING,
            transition_type=TransitionType.START_TASK,
            reason="Go to thinking",
        ))
        
        # Then to ACTING
        result = sm.apply_transition(StateTransitionRequest(
            desired_state=RuntimeState.ACTING,
            transition_type=TransitionType.CONTINUE_TASK,
            reason="Execute action",
        ))
        
        assert result is True
        assert sm.current_state == RuntimeState.ACTING
    
    def test_invalid_transition_blocked(self):
        """Test invalid transition is blocked."""
        from runtime.state import (
            StateMachine, RuntimeState,
            StateTransitionRequest, TransitionType
        )
        from runtime.config import load_config
        
        config = load_config()
        sm = StateMachine(config)
        
        # Try to go from IDLE directly to ACTING (invalid)
        result = sm.apply_transition(StateTransitionRequest(
            desired_state=RuntimeState.ACTING,
            transition_type=TransitionType.CONTINUE_TASK,
            reason="Invalid jump",
        ))
        
        assert result is False
        assert sm.current_state == RuntimeState.IDLE
    
    def test_placeholder_states_blocked(self):
        """Test SLEEPING/DREAMING transitions are blocked (placeholders)."""
        from runtime.state import (
            StateMachine, RuntimeState,
            StateTransitionRequest, TransitionType
        )
        from runtime.config import load_config
        
        config = load_config()
        sm = StateMachine(config)
        
        # Try to go to SLEEPING (placeholder)
        result = sm.apply_transition(StateTransitionRequest(
            desired_state=RuntimeState.SLEEPING,
            transition_type=TransitionType.SLEEP,
            reason="Try to sleep",
        ))
        
        assert result is False
        assert sm.current_state == RuntimeState.IDLE


# =============================================================================
# Budget Tracker Tests
# =============================================================================

class TestBudgetTracker:
    """Test budget tracking."""
    
    @pytest.mark.asyncio
    async def test_budget_snapshot_calculation(self):
        """Test budget snapshot calculation."""
        from runtime.budget import BudgetTracker
        from runtime.config import load_config
        
        config = load_config()
        tracker = BudgetTracker(config.budget, "test:")
        
        # Mock Redis
        mock_redis = AsyncMock()
        mock_redis.zrangebyscore = AsyncMock(return_value=[])
        tracker.set_redis(mock_redis)
        
        snapshot = await tracker.get_snapshot()
        
        assert snapshot is not None
        assert snapshot.requests_limit == 5000
        assert snapshot.remaining == 5000
        assert not snapshot.is_exhausted
    
    @pytest.mark.asyncio
    async def test_record_request_updates_count(self):
        """Test recording a request."""
        from runtime.budget import BudgetTracker
        from runtime.config import load_config
        
        config = load_config()
        tracker = BudgetTracker(config.budget, "test:")
        
        # Mock Redis
        mock_redis = AsyncMock()
        mock_redis.zadd = AsyncMock()
        mock_redis.zremrangebyscore = AsyncMock()
        mock_redis.zcount = AsyncMock(return_value=1)
        mock_redis.zrangebyscore = AsyncMock(return_value=["req1"])
        tracker.set_redis(mock_redis)
        
        await tracker.record_request("tick-123")
        
        # Verify zadd was called
        mock_redis.zadd.assert_called_once()


# =============================================================================
# Working Set Tests
# =============================================================================

class TestWorkingSet:
    """Test working set management."""
    
    def test_add_task(self):
        """Test adding a task."""
        from runtime.working_set import WorkingSetManager, WorkingSet
        
        manager = WorkingSetManager("test:")
        
        manager.add_task(
            task_id="task-001",
            intent="Test task",
            context={"key": "value"},
        )
        
        assert len(manager.working_set.active_tasks) == 1
        assert manager.working_set.active_tasks[0].id == "task-001"
    
    def test_tick_increments_counter(self):
        """Test tick increments counter."""
        from runtime.working_set import WorkingSetManager
        
        manager = WorkingSetManager("test:")
        initial_count = manager.working_set.tick_count
        
        manager.tick()
        
        assert manager.working_set.tick_count == initial_count + 1
    
    def test_set_last_intent(self):
        """Test setting last intent."""
        from runtime.working_set import WorkingSetManager
        
        manager = WorkingSetManager("test:")
        manager.set_last_intent("Exploring memories")
        
        assert manager.working_set.last_intent == "Exploring memories"


# =============================================================================
# Runaway Detector Tests
# =============================================================================

class TestRunawayDetector:
    """Test runaway detection."""
    
    def test_no_runaway_initially(self):
        """Test no runaway detected initially."""
        from runtime.runaway import RunawayDetector
        from runtime.config import load_config
        
        config = load_config()
        detector = RunawayDetector(config.runaway, "test:")
        
        score = detector.analyze()
        
        assert not score.is_runaway
        assert score.total_score == 0.0
    
    def test_error_streak_increases_score(self):
        """Test error streak increases runaway score."""
        from runtime.runaway import RunawayDetector
        from runtime.config import load_config
        
        config = load_config()
        detector = RunawayDetector(config.runaway, "test:")
        
        # Record ticks with errors
        for i in range(5):
            detector.record_tick(
                tick_id=f"tick-{i}",
                state="idle",
                intent="test",
                action=None,
                progress_markers=[],
                had_error=True,
            )
        
        score = detector.analyze()
        
        # Error weight is 0.15, 5 errors = high contribution
        assert score.breakdown["error_streak"] > 0
    
    def test_signature_repetition_detected(self):
        """Test signature repetition is detected."""
        from runtime.runaway import RunawayDetector
        from runtime.config import load_config
        
        config = load_config()
        detector = RunawayDetector(config.runaway, "test:")
        
        # Record identical ticks
        for i in range(10):
            detector.record_tick(
                tick_id=f"tick-{i}",
                state="thinking",
                intent="same intent",
                action="same action",
                progress_markers=[],
                had_error=False,
            )
        
        score = detector.analyze()
        
        # Repetition weight is 0.25
        assert score.breakdown["signature_repetition"] > 0


# =============================================================================
# Circuit Breaker Tests
# =============================================================================

class TestCircuitBreaker:
    """Test circuit breaker pattern."""
    
    def test_initial_state_closed(self):
        """Test circuit starts closed."""
        from runtime.circuit_breaker import CircuitBreaker, CircuitState
        from runtime.config import load_config
        
        config = load_config()
        cb = CircuitBreaker(config.circuit_breaker, "test")
        
        assert cb.state == CircuitState.CLOSED
        assert cb.can_execute()
    
    def test_opens_after_failures(self):
        """Test circuit opens after threshold failures."""
        from runtime.circuit_breaker import CircuitBreaker, CircuitState
        from runtime.config import load_config
        
        config = load_config()
        cb = CircuitBreaker(config.circuit_breaker, "test")
        
        # Record failures up to threshold
        for _ in range(config.circuit_breaker.failure_threshold):
            cb.record_failure()
        
        assert cb.state == CircuitState.OPEN
        assert not cb.can_execute()
    
    def test_success_resets_failures(self):
        """Test success resets failure count."""
        from runtime.circuit_breaker import CircuitBreaker
        from runtime.config import load_config
        
        config = load_config()
        cb = CircuitBreaker(config.circuit_breaker, "test")
        
        # Record some failures
        cb.record_failure()
        cb.record_failure()
        
        # Record success
        cb.record_success()
        
        assert cb.stats.consecutive_failures == 0


# =============================================================================
# Metrics Tests
# =============================================================================

class TestMetrics:
    """Test metrics collection."""
    
    def test_record_tick(self):
        """Test recording tick metrics."""
        from runtime.metrics import MetricsCollector
        
        collector = MetricsCollector("test:")
        
        collector.record_tick(
            tick_id="tick-001",
            duration_s=0.5,
            state="idle",
            llm_triggered=True,
            budget_remaining=4999,
            runaway_score=0.1,
            had_error=False,
            had_progress=True,
        )
        
        assert collector.runtime_metrics.total_ticks == 1
        assert collector.runtime_metrics.total_llm_calls == 1
    
    def test_prometheus_export(self):
        """Test Prometheus format export."""
        from runtime.metrics import MetricsCollector
        
        collector = MetricsCollector("test:")
        
        collector.record_tick(
            tick_id="tick-001",
            duration_s=0.5,
            state="idle",
            llm_triggered=True,
            budget_remaining=4999,
            runaway_score=0.1,
            had_error=False,
            had_progress=True,
        )
        
        output = collector.to_prometheus()
        
        assert "scarlet_runtime_ticks_total" in output
        assert "scarlet_runtime_llm_calls_total" in output


# =============================================================================
# Integration Tests (require running services)
# =============================================================================

@pytest.mark.integration
class TestIntegration:
    """Integration tests requiring running services."""
    
    @pytest.mark.asyncio
    async def test_full_tick_cycle(self):
        """Test a full tick cycle with mocked services."""
        # This would be a more comprehensive test with actual service mocks
        pass


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
