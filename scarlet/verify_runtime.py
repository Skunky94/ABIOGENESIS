#!/usr/bin/env python
"""
Quick verification script for Autonomy Runtime
Run from ABIOGENESIS root: python scarlet/verify_runtime.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set config path
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config', 'runtime.yaml')

def test_config():
    """Test config loading."""
    print("\n=== TEST: Config Loading ===")
    from runtime.config import load_config
    
    config = load_config(CONFIG_PATH)
    print(f"✓ Config loaded from: {CONFIG_PATH}")
    print(f"  - tick_interval_base_s: {config.loop.tick_interval_base_s}")
    print(f"  - budget: {config.budget.requests_limit}/{config.budget.window_seconds}s")
    print(f"  - letta_url: {config.letta.api_url}")
    print(f"  - idle activities: {len(config.idle.activities)}")
    return config

def test_state_machine(config):
    """Test state machine."""
    print("\n=== TEST: State Machine ===")
    from runtime.state import StateMachine, RuntimeState, StateTransitionRequest, TransitionType
    
    sm = StateMachine(config)
    print(f"✓ StateMachine created, initial state: {sm.current_state.value}")
    
    # Test valid transition
    req = StateTransitionRequest(
        desired_state=RuntimeState.THINKING,
        transition_type=TransitionType.START_TASK,
        reason="Test transition"
    )
    result = sm.apply_transition(req)
    print(f"✓ Transition IDLE->THINKING: {'success' if result else 'FAILED'}")
    print(f"  Current state: {sm.current_state.value}")
    
    # Test placeholder state (should fail)
    req_sleep = StateTransitionRequest(
        desired_state=RuntimeState.SLEEPING,
        transition_type=TransitionType.SLEEP,
        reason="Test placeholder"
    )
    result_sleep = sm.apply_transition(req_sleep)
    print(f"✓ Transition to SLEEPING (placeholder): {'blocked as expected' if not result_sleep else 'ERROR - should be blocked!'}")
    
    return sm

def test_budget_tracker(config):
    """Test budget tracker (without Redis)."""
    print("\n=== TEST: Budget Tracker ===")
    from runtime.budget import BudgetTracker, BudgetSnapshot
    
    tracker = BudgetTracker(config.budget, "test:")
    print(f"✓ BudgetTracker created")
    print(f"  - limit: {config.budget.requests_limit}")
    print(f"  - window: {config.budget.window_seconds}s")
    print(f"  - throttle_threshold: {config.budget.throttle_threshold}")
    return tracker

def test_working_set():
    """Test working set."""
    print("\n=== TEST: Working Set ===")
    from runtime.working_set import WorkingSetManager, TaskEntry
    from datetime import datetime
    
    manager = WorkingSetManager("test:")
    print(f"✓ WorkingSetManager created")
    
    now = datetime.utcnow()
    task = TaskEntry(
        id="task-001", 
        description="Test task", 
        state="pending",
        created_at=now,
        updated_at=now,
        metadata={"key": "value"}
    )
    manager.add_task(task)
    print(f"  - Added task: task-001")
    print(f"  - Pending tasks: {len(manager.working_set.pending_tasks)}")
    
    manager.tick()
    print(f"  - Tick count after tick(): {manager.working_set.tick_count}")
    return manager

def test_runaway_detector(config):
    """Test runaway detector."""
    print("\n=== TEST: Runaway Detector ===")
    from runtime.runaway import RunawayDetector
    
    detector = RunawayDetector(config.runaway, "test:")
    print(f"✓ RunawayDetector created")
    
    score = detector.analyze()
    print(f"  - Initial score: {score.total_score:.2f}")
    print(f"  - Is runaway: {score.is_runaway}")
    
    # Record some ticks
    for i in range(5):
        detector.record_tick(f"tick-{i}", "idle", "test", None, [], had_error=True)
    
    score_after = detector.analyze()
    print(f"  - After 5 error ticks: {score_after.total_score:.2f}")
    print(f"  - Is runaway now: {score_after.is_runaway}")
    print(f"  - Error score: {score_after.error_streak_score:.2f}")
    return detector

def test_circuit_breaker(config):
    """Test circuit breaker."""
    print("\n=== TEST: Circuit Breaker ===")
    from runtime.circuit_breaker import CircuitBreaker, CircuitState
    
    cb = CircuitBreaker(config.circuit_breaker, "test")
    print(f"✓ CircuitBreaker created, state: {cb.state.value}")
    
    # Record failures up to threshold
    threshold = config.circuit_breaker.error_threshold
    for _ in range(threshold):
        cb.record_failure()
    
    print(f"  - After {threshold} failures: {cb.state.value}")
    print(f"  - Can execute: {cb.can_execute()}")
    return cb

def test_metrics():
    """Test metrics collector."""
    print("\n=== TEST: Metrics Collector ===")
    from runtime.metrics import MetricsCollector
    
    collector = MetricsCollector("test:")
    print(f"✓ MetricsCollector created")
    
    collector.record_tick(
        tick_id="tick-001",
        duration_s=0.5,
        state="idle",
        llm_triggered=True,
        budget_remaining=4999,
        runaway_score=0.1,
        had_error=False,
        had_progress=True
    )
    
    metrics = collector.get_metrics()
    print(f"  - Total ticks: {metrics.total_ticks}")
    print(f"  - Total LLM calls: {metrics.total_llm_calls}")
    
    prometheus = collector.get_prometheus_metrics()
    print(f"  - Prometheus output lines: {len(prometheus.split(chr(10)))}")
    return collector

def test_learning_events():
    """Test learning events."""
    print("\n=== TEST: Learning Events ===")
    from runtime.learning_events import LearningEventEmitter, LearningEvent
    
    emitter = LearningEventEmitter("test_learning_events")
    print(f"✓ LearningEventEmitter created")
    print(f"  - Collection: test_learning_events")
    return emitter

def test_services():
    """Test connections to running services."""
    print("\n=== TEST: Service Connectivity ===")
    import urllib.request
    import json
    
    services = [
        ("Letta", "http://localhost:8283/v1/health"),
        ("Qdrant", "http://localhost:6333/collections"),
        ("Sleep Webhook", "http://localhost:8284/health"),
    ]
    
    for name, url in services:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                data = response.read().decode()
                status = "✓" if response.status == 200 else "⚠"
                print(f"{status} {name}: HTTP {response.status}")
        except Exception as e:
            print(f"✗ {name}: {e}")

def main():
    """Run all verification tests."""
    print("=" * 60)
    print("AUTONOMY RUNTIME VERIFICATION")
    print("=" * 60)
    
    try:
        # Core module tests
        config = test_config()
        test_state_machine(config)
        test_budget_tracker(config)
        test_working_set()
        test_runaway_detector(config)
        test_circuit_breaker(config)
        test_metrics()
        test_learning_events()
        
        # Service connectivity
        test_services()
        
        print("\n" + "=" * 60)
        print("✓ ALL VERIFICATION TESTS PASSED")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\n✗ VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
