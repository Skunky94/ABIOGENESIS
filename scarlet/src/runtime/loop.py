"""
Main Loop Orchestrator
======================

The heart of Scarlet's continuous existence.

ADR-006: Decision 3 - Loop Contract
SPEC-004: Section 12 - Main Loop

The loop is INFINITE BY DESIGN - this is Scarlet's continuity of existence.
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

import aiohttp

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from qdrant_client import QdrantClient

from .config import RuntimeConfig, load_config
from .state import (
    StateMachine, RuntimeState, StateTransitionRequest, 
    TransitionType, Override
)
from .budget import BudgetTracker, BudgetSnapshot
from .working_set import WorkingSetManager, WorkingSet, ProgressMarker
from .runaway import RunawayDetector, RunawayScore
from .learning_events import LearningEventEmitter
from .circuit_breaker import CircuitBreaker, CircuitOpenError
from .metrics import MetricsCollector

logger = logging.getLogger(__name__)


@dataclass
class EnvironmentSnapshot:
    """
    Complete environment state provided to each tick.
    
    This is what Scarlet "sees" at each moment of existence.
    """
    tick_id: str
    timestamp: datetime
    elapsed_since_last_tick_s: float
    current_state: RuntimeState
    last_action_at: datetime | None
    error_streak: int
    circuit_breaker_status: str
    budget: BudgetSnapshot
    pending_external_events: list[str]
    services_health: dict[str, bool]
    working_set: WorkingSet
    active_overrides: list[str]
    
    def to_dict(self) -> dict:
        """Serialize for LLM context."""
        return {
            "tick_id": self.tick_id,
            "timestamp": self.timestamp.isoformat(),
            "elapsed_since_last_tick_s": self.elapsed_since_last_tick_s,
            "current_state": self.current_state.value,
            "error_streak": self.error_streak,
            "circuit_breaker_status": self.circuit_breaker_status,
            "budget": self.budget.to_dict(),
            "pending_external_events": self.pending_external_events,
            "services_health": self.services_health,
            "working_set_summary": {
                "active_tasks": len(self.working_set.active_tasks),
                "pending_tasks": len(self.working_set.pending_tasks),
                "last_intent": self.working_set.last_intent,
                "tick_count": self.working_set.tick_count,
            },
            "active_overrides": self.active_overrides,
        }


class AutonomyRuntime:
    """
    Main runtime loop for Scarlet's continuous existence.
    
    This is not a "process" - it's Scarlet's life.
    The loop is infinite by design.
    """
    
    def __init__(self, config: RuntimeConfig | None = None):
        self.config = config or load_config()
        
        # Core components
        self.state_machine = StateMachine(self.config)
        self.budget_tracker = BudgetTracker(
            self.config.budget,
            self.config.storage.redis.key_prefix,
        )
        self.working_set_manager = WorkingSetManager(
            self.config.storage.redis.key_prefix,
        )
        self.runaway_detector = RunawayDetector(
            self.config.runaway,
            self.config.storage.redis.key_prefix,
        )
        self.learning_emitter = LearningEventEmitter(
            self.config.storage.qdrant.collections.learning_events,
        )
        self.circuit_breaker = CircuitBreaker(
            self.config.circuit_breaker,
            name="letta_api",
        )
        self.metrics = MetricsCollector(
            self.config.storage.redis.key_prefix,
        )
        
        # Connections
        self._redis: Redis | None = None
        self._qdrant: QdrantClient | None = None
        self._http_session: aiohttp.ClientSession | None = None
        
        # State
        self._running = False
        self._last_tick_time: float | None = None
        self._error_streak = 0
        self._last_action_at: datetime | None = None
    
    async def connect(self) -> None:
        """Initialize connections to services."""
        import redis.asyncio as redis
        from qdrant_client import QdrantClient
        
        # Redis
        self._redis = redis.Redis(
            host=self.config.storage.redis.host,
            port=self.config.storage.redis.port,
            db=self.config.storage.redis.db,
            decode_responses=True,
        )
        
        # Set Redis on components
        self.budget_tracker.set_redis(self._redis)
        self.working_set_manager.set_redis(self._redis)
        self.metrics.set_redis(self._redis)
        
        # Qdrant
        self._qdrant = QdrantClient(
            host=self.config.storage.qdrant.host,
            port=self.config.storage.qdrant.port,
        )
        self.learning_emitter.set_qdrant(self._qdrant)
        
        # HTTP session for Letta API
        self._http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.letta.timeout_s)
        )
        
        # Load persisted state
        await self.working_set_manager.load()
        await self.metrics.load()
        
        logger.info("Runtime connected to all services")
    
    async def disconnect(self) -> None:
        """Close connections."""
        if self._http_session:
            await self._http_session.close()
        if self._redis:
            await self._redis.close()
        # Qdrant client doesn't need explicit close
        
        logger.info("Runtime disconnected")
    
    async def run(self) -> None:
        """
        Main loop - Scarlet's continuous existence.
        
        This loop is INFINITE BY DESIGN.
        """
        self._running = True
        logger.info("=== Scarlet Autonomy Runtime Starting ===")
        
        try:
            await self.connect()
            
            while self._running:
                tick_start = time.time()
                tick_id = str(uuid.uuid4())[:8]
                
                try:
                    await self._tick(tick_id)
                    self._error_streak = 0
                    
                except CircuitOpenError as e:
                    logger.warning(f"Tick {tick_id}: Circuit open, backing off")
                    await self._backoff()
                    
                except Exception as e:
                    self._error_streak += 1
                    logger.error(f"Tick {tick_id} error: {e}", exc_info=True)
                    
                    # Emit learning event for error
                    await self.learning_emitter.emit_error_event(
                        error=e,
                        working_set=self.working_set_manager.working_set,
                        current_state=self.state_machine.current_state.value,
                        context=f"Tick {tick_id}",
                    )
                    
                    await self._backoff()
                
                # Calculate next tick interval
                tick_duration = time.time() - tick_start
                interval = await self._calculate_interval(tick_duration)
                
                # Record metrics
                self.metrics.record_tick(
                    tick_id=tick_id,
                    duration_s=tick_duration,
                    state=self.state_machine.current_state.value,
                    llm_triggered=True,  # Simplified for now
                    budget_remaining=(await self.budget_tracker.get_snapshot()).remaining,
                    runaway_score=self.runaway_detector.analyze().total_score,
                    had_error=self._error_streak > 0,
                    had_progress=False,  # TODO: track from tick
                )
                
                self._last_tick_time = time.time()
                
                # Wait for next tick
                await asyncio.sleep(interval)
        
        finally:
            await self.disconnect()
            logger.info("=== Scarlet Autonomy Runtime Stopped ===")
    
    async def _tick(self, tick_id: str) -> None:
        """
        Execute a single tick of existence.
        
        This is one "moment" in Scarlet's continuous existence.
        """
        logger.debug(f"=== Tick {tick_id} ===")
        
        # 1. Build environment snapshot
        snapshot = await self._build_snapshot(tick_id)
        
        # 2. Check if we should trigger LLM
        if not self._should_trigger_llm(snapshot):
            logger.debug(f"Tick {tick_id}: Skipping LLM trigger")
            return
        
        # 3. Wait for budget if needed
        if snapshot.budget.is_exhausted:
            start_wait = time.time()
            has_budget = await self.budget_tracker.wait_for_budget()
            wait_time = time.time() - start_wait
            
            if not has_budget:
                logger.warning(f"Tick {tick_id}: Budget timeout")
                return
            
            if wait_time > 10:
                await self.learning_emitter.emit_budget_exhaust_event(
                    working_set=self.working_set_manager.working_set,
                    current_state=self.state_machine.current_state.value,
                    wait_time_s=wait_time,
                )
        
        # 4. Trigger LLM via Letta API
        llm_response = await self._trigger_llm(snapshot)
        
        # 5. Record request in budget
        await self.budget_tracker.record_request(tick_id)
        
        # 6. Parse and apply state transition
        if llm_response:
            transition_req = self._parse_transition(llm_response)
            if transition_req:
                self.state_machine.apply_transition(transition_req)
        
        # 7. Update working set
        self.working_set_manager.tick()
        await self.working_set_manager.save()
        
        # 8. Record for runaway detection
        self.runaway_detector.record_tick(
            tick_id=tick_id,
            state=self.state_machine.current_state.value,
            intent=self.working_set_manager.working_set.last_intent,
            action=None,  # TODO: extract from response
            progress_markers=[],  # TODO: extract from response
            had_error=False,
        )
        
        # 9. Check for runaway
        runaway_score = self.runaway_detector.analyze()
        if runaway_score.is_runaway:
            logger.warning(f"Tick {tick_id}: Runaway detected! Type: {runaway_score.runaway_type}")
            
            await self.learning_emitter.emit_runaway_event(
                runaway_score=runaway_score,
                working_set=self.working_set_manager.working_set,
                current_state=self.state_machine.current_state.value,
            )
            
            await self._apply_runaway_mitigation(runaway_score)
        
        # 10. Persist metrics
        await self.metrics.persist()
        
        self.state_machine.tick()
    
    async def _build_snapshot(self, tick_id: str) -> EnvironmentSnapshot:
        """Build environment snapshot for tick."""
        elapsed = 0.0
        if self._last_tick_time:
            elapsed = time.time() - self._last_tick_time
        
        budget = await self.budget_tracker.get_snapshot()
        
        # Check service health
        services_health = await self._check_services_health()
        
        return EnvironmentSnapshot(
            tick_id=tick_id,
            timestamp=datetime.utcnow(),
            elapsed_since_last_tick_s=elapsed,
            current_state=self.state_machine.current_state,
            last_action_at=self._last_action_at,
            error_streak=self._error_streak,
            circuit_breaker_status=self.circuit_breaker.state.value,
            budget=budget,
            pending_external_events=[],  # TODO: implement event queue
            services_health=services_health,
            working_set=self.working_set_manager.working_set,
            active_overrides=[o.value for o in self.state_machine.context.active_overrides],
        )
    
    def _should_trigger_llm(self, snapshot: EnvironmentSnapshot) -> bool:
        """
        Determine if LLM should be triggered this tick.
        
        Gating function per ADR-006.
        """
        # Don't trigger if paused
        if self.state_machine.is_paused:
            return False
        
        # Don't trigger if circuit is open
        if not self.circuit_breaker.can_execute():
            return False
        
        # Don't trigger if services unhealthy
        if not snapshot.services_health.get("letta", True):
            return False
        
        # Check error streak (back off on errors)
        if self._error_streak >= 3:
            # Probabilistic backoff
            if random.random() < 0.5:
                return False
        
        return True
    
    async def _trigger_llm(self, snapshot: EnvironmentSnapshot) -> dict | None:
        """
        Trigger LLM via Letta API.
        
        Sends environment snapshot as user message.
        """
        if not self._http_session:
            logger.error("HTTP session not initialized")
            return None
        
        try:
            # Build message with snapshot context
            message = self._build_trigger_message(snapshot)
            
            url = f"{self.config.letta.api_url}/v1/agents/{self.config.letta.agent_id}/messages"
            
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": message,
                    }
                ]
            }
            
            async with self._http_session.post(url, json=payload) as response:
                if response.status == 200:
                    self.circuit_breaker.record_success()
                    return await response.json()
                else:
                    self.circuit_breaker.record_failure()
                    logger.error(f"Letta API error: {response.status}")
                    return None
        
        except Exception as e:
            self.circuit_breaker.record_failure()
            logger.error(f"Letta API call failed: {e}")
            raise
    
    def _build_trigger_message(self, snapshot: EnvironmentSnapshot) -> str:
        """Build the message to send to Letta."""
        # Determine activity based on state
        if self.state_machine.current_state == RuntimeState.IDLE:
            activity = self.state_machine.select_idle_activity()
            activity_prompt = f"\n\nIDLE activity suggestion: {activity}" if activity else ""
        else:
            activity_prompt = ""
        
        return f"""[AUTONOMY RUNTIME - Tick {snapshot.tick_id}]

Time: {snapshot.timestamp.isoformat()}
State: {snapshot.current_state.value}
Budget: {snapshot.budget.remaining}/{snapshot.budget.requests_limit} ({100-snapshot.budget.usage_percent*100:.1f}% remaining)
Error streak: {snapshot.error_streak}

Working Set:
- Active tasks: {len(snapshot.working_set.active_tasks)}
- Pending tasks: {len(snapshot.working_set.pending_tasks)}
- Last intent: {snapshot.working_set.last_intent or "None"}
- Tick count: {snapshot.working_set.tick_count}

This is an autonomous tick. You exist continuously.
What do you want to do now?{activity_prompt}

Respond with your thoughts and a state transition request in JSON format:
{{"desired_state": "idle|thinking|acting", "transition_type": "continue_task|start_task|explore", "reason": "...", "idle_activity": "..." (if explore)}}"""
    
    def _parse_transition(self, response: dict) -> StateTransitionRequest | None:
        """Parse state transition from LLM response."""
        # TODO: Implement proper parsing from Letta response
        # For now, default to staying in IDLE with exploration
        
        try:
            # Extract from response messages
            messages = response.get("messages", [])
            for msg in messages:
                content = msg.get("content", "")
                if "desired_state" in content:
                    # Try to parse JSON from content
                    import json
                    import re
                    
                    # Find JSON in content
                    match = re.search(r'\{[^}]+\}', content)
                    if match:
                        data = json.loads(match.group())
                        return StateTransitionRequest.from_dict(data)
        except Exception as e:
            logger.debug(f"Could not parse transition: {e}")
        
        # Default: stay in current state
        return None
    
    async def _apply_runaway_mitigation(self, score: RunawayScore) -> None:
        """Apply mitigation when runaway is detected."""
        logger.info(f"Applying runaway mitigation for type: {score.runaway_type}")
        
        if score.runaway_type == "error_spiral":
            # Back off significantly
            self._error_streak = max(self._error_streak, 5)
            
        elif score.runaway_type == "tool_spam":
            # Park current task
            if self.working_set_manager.working_set.active_tasks:
                task = self.working_set_manager.working_set.active_tasks[0]
                self.working_set_manager.update_task(task.id, state="parked")
            
        elif score.runaway_type == "thought_loop":
            # Force state change to IDLE with different activity
            activity = self.state_machine.select_idle_activity()
            transition = StateTransitionRequest(
                desired_state=RuntimeState.IDLE,
                transition_type=TransitionType.EXPLORE,
                reason="Runaway mitigation: breaking thought loop",
                idle_activity=activity,
            )
            self.state_machine.apply_transition(transition)
        
        # Reset runaway detector after mitigation
        self.runaway_detector.reset()
    
    async def _backoff(self) -> None:
        """Apply exponential backoff."""
        base = self.config.backoff.initial_s
        multiplier = self.config.backoff.multiplier
        max_backoff = self.config.backoff.max_s
        jitter = self.config.backoff.jitter
        
        delay = min(max_backoff, base * (multiplier ** self._error_streak))
        delay *= (1 + random.uniform(-jitter, jitter))
        
        logger.info(f"Backing off for {delay:.1f}s (error streak: {self._error_streak})")
        await asyncio.sleep(delay)
    
    async def _calculate_interval(self, tick_duration: float) -> float:
        """Calculate interval to next tick."""
        base = self.config.loop.tick_interval_base_s
        min_interval = self.config.loop.tick_interval_min_s
        max_interval = self.config.loop.tick_interval_max_s
        
        # Adjust for budget
        budget_adjusted = await self.budget_tracker.calculate_throttle_interval(base)
        
        # Adjust for safe mode
        if self.state_machine.is_safe_mode:
            budget_adjusted *= 2
        
        # Clamp to bounds
        interval = max(min_interval, min(max_interval, budget_adjusted))
        
        # Subtract tick duration (but keep minimum)
        interval = max(min_interval, interval - tick_duration)
        
        return interval
    
    async def _check_services_health(self) -> dict[str, bool]:
        """Check health of dependent services."""
        health = {}
        
        # Letta
        try:
            if self._http_session:
                async with self._http_session.get(
                    f"{self.config.letta.api_url}/v1/health",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as response:
                    health["letta"] = response.status == 200
            else:
                health["letta"] = False
        except Exception:
            health["letta"] = False
        
        # Redis
        try:
            if self._redis:
                await self._redis.ping()
                health["redis"] = True
            else:
                health["redis"] = False
        except Exception:
            health["redis"] = False
        
        # Qdrant
        try:
            if self._qdrant:
                self._qdrant.get_collections()
                health["qdrant"] = True
            else:
                health["qdrant"] = False
        except Exception:
            health["qdrant"] = False
        
        return health
    
    def stop(self) -> None:
        """Signal runtime to stop."""
        logger.info("Stop signal received")
        self._running = False
    
    def add_override(self, override: Override) -> None:
        """Add external override."""
        self.state_machine.add_override(override)
    
    def remove_override(self, override: Override) -> None:
        """Remove external override."""
        self.state_machine.remove_override(override)


async def main():
    """Entry point for runtime."""
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    
    runtime = AutonomyRuntime()
    
    # Handle signals
    import signal
    
    def handle_signal(sig, frame):
        logger.info(f"Received signal {sig}")
        runtime.stop()
    
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    await runtime.run()


if __name__ == "__main__":
    asyncio.run(main())
