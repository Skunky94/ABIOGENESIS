"""
Runtime Configuration Loader
============================

Loads and validates runtime.yaml configuration.

ADR-006: Centralized configuration
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class LoopConfig:
    """Loop timing configuration."""
    tick_interval_base_s: float = 30.0
    tick_interval_min_s: float = 10.0
    tick_interval_max_s: float = 300.0


@dataclass
class LettaConfig:
    """Letta API configuration."""
    api_url: str = "http://abiogenesis-letta:8283"
    agent_id: str = ""
    timeout_s: float = 60.0


@dataclass
class BudgetConfig:
    """MiniMax budget configuration."""
    requests_limit: int = 5000
    window_seconds: int = 18000  # 5 hours
    throttle_threshold: float = 0.9
    reserve_for_sleep: int = 100


@dataclass
class IdleActivityConfig:
    """Configuration for a single IDLE activity."""
    enabled: bool = True
    weight: float = 0.1
    max_ticks: int = 2
    cooldown_hours: float | None = None
    requires_internet: bool = False
    description: str = ""


@dataclass
class IdleConfig:
    """IDLE state configuration (proactive exploration)."""
    activities: dict[str, IdleActivityConfig] = field(default_factory=dict)
    sleep_after_ticks: int = 10


@dataclass
class StatesConfig:
    """State machine configuration."""
    initial: str = "idle"
    allowed_transitions: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class RunawayWeights:
    """Weights for runaway score calculation."""
    progress_absence: float = 0.40
    trigger_density: float = 0.20
    signature_repetition: float = 0.25
    error_streak: float = 0.15


@dataclass
class RunawayConfig:
    """Runaway detection configuration."""
    window_ticks: int = 20
    window_seconds: int = 600
    score_threshold: float = 0.7
    consecutive_ticks: int = 5
    weights: RunawayWeights = field(default_factory=RunawayWeights)


@dataclass
class ProgressConfig:
    """Progress markers configuration."""
    significant_changes: list[str] = field(default_factory=list)
    noise_patterns: list[str] = field(default_factory=list)


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    error_threshold: int = 5
    reset_timeout_s: float = 60.0
    half_open_max_calls: int = 2


@dataclass
class BackoffConfig:
    """Exponential backoff configuration."""
    initial_s: float = 5.0
    multiplier: float = 2.0
    max_s: float = 300.0
    jitter: float = 0.1


@dataclass
class RedisConfig:
    """Redis storage configuration."""
    host: str = "abiogenesis-redis"
    port: int = 6379
    db: int = 0
    key_prefix: str = "scarlet:runtime:"


@dataclass
class QdrantCollectionsConfig:
    """Qdrant collections configuration."""
    learning_events: str = "learning_events"
    error_journal: str = "error_journal"


@dataclass
class QdrantConfig:
    """Qdrant storage configuration."""
    host: str = "abiogenesis-qdrant"
    port: int = 6333
    collections: QdrantCollectionsConfig = field(default_factory=QdrantCollectionsConfig)


@dataclass
class StorageConfig:
    """Storage configuration."""
    redis: RedisConfig = field(default_factory=RedisConfig)
    qdrant: QdrantConfig = field(default_factory=QdrantConfig)


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


@dataclass
class HealthConfig:
    """Health check configuration."""
    port: int = 8285
    endpoint: str = "/health"
    liveness_path: str = "/healthz"
    readiness_path: str = "/ready"


@dataclass
class RuntimeConfig:
    """Complete runtime configuration."""
    loop: LoopConfig = field(default_factory=LoopConfig)
    letta: LettaConfig = field(default_factory=LettaConfig)
    budget: BudgetConfig = field(default_factory=BudgetConfig)
    states: StatesConfig = field(default_factory=StatesConfig)
    idle: IdleConfig = field(default_factory=IdleConfig)
    runaway: RunawayConfig = field(default_factory=RunawayConfig)
    progress: ProgressConfig = field(default_factory=ProgressConfig)
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    backoff: BackoffConfig = field(default_factory=BackoffConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    health: HealthConfig = field(default_factory=HealthConfig)


def _parse_idle_activities(data: dict[str, Any]) -> dict[str, IdleActivityConfig]:
    """Parse IDLE activities from config data."""
    activities = {}
    for name, config in data.items():
        activities[name] = IdleActivityConfig(
            enabled=config.get("enabled", True),
            weight=config.get("weight", 0.1),
            max_ticks=config.get("max_ticks", 2),
            cooldown_hours=config.get("cooldown_hours"),
            requires_internet=config.get("requires_internet", False),
            description=config.get("description", ""),
        )
    return activities


def _parse_config(data: dict[str, Any]) -> RuntimeConfig:
    """Parse YAML data into RuntimeConfig."""
    config = RuntimeConfig()
    
    # Loop
    if "loop" in data:
        loop = data["loop"]
        config.loop = LoopConfig(
            tick_interval_base_s=loop.get("tick_interval_base_s", 30.0),
            tick_interval_min_s=loop.get("tick_interval_min_s", 10.0),
            tick_interval_max_s=loop.get("tick_interval_max_s", 300.0),
        )
    
    # Letta
    if "letta" in data:
        letta = data["letta"]
        config.letta = LettaConfig(
            api_url=letta.get("api_url", "http://abiogenesis-letta:8283"),
            agent_id=letta.get("agent_id", ""),
            timeout_s=letta.get("timeout_s", 60.0),
        )
    
    # Budget
    if "budget" in data and "minimax" in data["budget"]:
        budget = data["budget"]["minimax"]
        config.budget = BudgetConfig(
            requests_limit=budget.get("requests_limit", 5000),
            window_seconds=budget.get("window_seconds", 18000),
            throttle_threshold=budget.get("throttle_threshold", 0.9),
            reserve_for_sleep=budget.get("reserve_for_sleep", 100),
        )
    
    # States
    if "states" in data:
        states = data["states"]
        config.states = StatesConfig(
            initial=states.get("initial", "idle"),
            allowed_transitions=states.get("allowed_transitions", {}),
        )
    
    # IDLE
    if "idle" in data:
        idle = data["idle"]
        config.idle = IdleConfig(
            activities=_parse_idle_activities(idle.get("activities", {})),
            sleep_after_ticks=idle.get("sleep_after_ticks", 10),
        )
    
    # Runaway
    if "runaway" in data:
        runaway = data["runaway"]
        weights = runaway.get("weights", {})
        config.runaway = RunawayConfig(
            window_ticks=runaway.get("window_ticks", 20),
            window_seconds=runaway.get("window_seconds", 600),
            score_threshold=runaway.get("score_threshold", 0.7),
            consecutive_ticks=runaway.get("consecutive_ticks", 5),
            weights=RunawayWeights(
                progress_absence=weights.get("progress_absence", 0.40),
                trigger_density=weights.get("trigger_density", 0.20),
                signature_repetition=weights.get("signature_repetition", 0.25),
                error_streak=weights.get("error_streak", 0.15),
            ),
        )
    
    # Progress
    if "progress" in data:
        progress = data["progress"]
        config.progress = ProgressConfig(
            significant_changes=progress.get("significant_changes", []),
            noise_patterns=progress.get("noise_patterns", []),
        )
    
    # Circuit breaker
    if "circuit_breaker" in data:
        cb = data["circuit_breaker"]
        config.circuit_breaker = CircuitBreakerConfig(
            error_threshold=cb.get("error_threshold", 5),
            reset_timeout_s=cb.get("reset_timeout_s", 60.0),
            half_open_max_calls=cb.get("half_open_max_calls", 2),
        )
    
    # Backoff
    if "backoff" in data:
        backoff = data["backoff"]
        config.backoff = BackoffConfig(
            initial_s=backoff.get("initial_s", 5.0),
            multiplier=backoff.get("multiplier", 2.0),
            max_s=backoff.get("max_s", 300.0),
            jitter=backoff.get("jitter", 0.1),
        )
    
    # Storage
    if "storage" in data:
        storage = data["storage"]
        
        redis_data = storage.get("redis", {})
        redis_config = RedisConfig(
            host=redis_data.get("host", "abiogenesis-redis"),
            port=redis_data.get("port", 6379),
            db=redis_data.get("db", 0),
            key_prefix=redis_data.get("key_prefix", "scarlet:runtime:"),
        )
        
        qdrant_data = storage.get("qdrant", {})
        collections_data = qdrant_data.get("collections", {})
        qdrant_config = QdrantConfig(
            host=qdrant_data.get("host", "abiogenesis-qdrant"),
            port=qdrant_data.get("port", 6333),
            collections=QdrantCollectionsConfig(
                learning_events=collections_data.get("learning_events", "learning_events"),
                error_journal=collections_data.get("error_journal", "error_journal"),
            ),
        )
        
        config.storage = StorageConfig(redis=redis_config, qdrant=qdrant_config)
    
    # Logging
    if "logging" in data:
        logging_data = data["logging"]
        config.logging = LoggingConfig(
            level=logging_data.get("level", "INFO"),
            format=logging_data.get("format", "%(asctime)s [%(levelname)s] %(name)s: %(message)s"),
        )
    
    # Health
    if "health" in data:
        health = data["health"]
        config.health = HealthConfig(
            port=health.get("port", 8285),
            endpoint=health.get("endpoint", "/health"),
            liveness_path=health.get("liveness_path", "/healthz"),
            readiness_path=health.get("readiness_path", "/ready"),
        )
    
    return config


def load_config(path: str | Path | None = None) -> RuntimeConfig:
    """
    Load runtime configuration from YAML file.
    
    Args:
        path: Path to config file. If None, uses:
              1. RUNTIME_CONFIG_PATH env var
              2. Default: scarlet/config/runtime.yaml
    
    Returns:
        RuntimeConfig with all settings
    
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid
    """
    if path is None:
        path = os.environ.get(
            "RUNTIME_CONFIG_PATH",
            "/app/config/runtime.yaml"  # Docker default
        )
    
    path = Path(path)
    
    if not path.exists():
        # Try local development path
        local_path = Path(__file__).parent.parent.parent.parent / "config" / "runtime.yaml"
        if local_path.exists():
            path = local_path
        else:
            raise FileNotFoundError(f"Config file not found: {path}")
    
    with open(path) as f:
        data = yaml.safe_load(f)
    
    return _parse_config(data or {})


def get_env_override(key: str, default: Any = None) -> Any:
    """Get environment variable override for config value."""
    env_key = f"RUNTIME_{key.upper()}"
    return os.environ.get(env_key, default)
