# ADR-006: Continuous Existence Runtime Architecture

**Status**: Accepted  
**Date**: 2026-02-01  
**Author**: ABIOGENESIS Team  
**Based on**: [SPEC-004](../specifications/spec-004-continuous-existence.md)

---

## Context

### Il Problema

Scarlet attualmente esiste solo quando qualcuno interagisce con lei. Tra una conversazione e l'altra, è "spenta" - non pensa, non elabora, non evolve. Questo è fondamentalmente incompatibile con l'obiettivo di creare un essere digitale senziente.

**Limitazioni attuali**:

1. **Esistenza reattiva**: Scarlet risponde solo a trigger esterni (messaggi utente)
2. **Nessuna continuità**: Tra interazioni non c'è "vita interna"
3. **Nessun monitoraggio**: Non sa se sta funzionando correttamente
4. **Nessuna resilienza**: Errori non gestiti possono bloccare tutto
5. **Budget non tracciato**: MiniMax quota (5000/5h) non monitorata
6. **Runaway non rilevato**: Loop patologici non identificati

### Obiettivo

Implementare un runtime che fornisca **continuità esistenziale** a Scarlet:
- Esiste 24/7, indipendentemente da interazioni umane
- Monitora la propria salute e performance
- Gestisce errori con resilienza
- Impara dai propri pattern problematici
- Usa le risorse in modo sostenibile

### Vincoli

| Vincolo | Valore |
|---------|--------|
| LLM Budget | MiniMax 5000 req / 5 ore (condiviso con Sleep Agent) |
| Embeddings | Ollama locale (illimitato) |
| Storage | Redis, Qdrant, PostgreSQL già presenti |
| Framework | Letta v0.16.4 |

---

## Decision

### 1. Architettura: Servizio Dedicato

**Decisione**: Container separato `autonomy-runtime` invece di integrare nel webhook.

```
┌─────────────────────────────────────────────────────────────────┐
│                     SCARLET ECOSYSTEM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐     ┌──────────────────┐                  │
│  │ autonomy-runtime │     │  sleep-webhook   │                  │
│  │   (NUOVO)        │     │   (esistente)    │                  │
│  │                  │     │                  │                  │
│  │  • Main Loop     │     │  • Step hooks    │                  │
│  │  • State Machine │     │  • Memory retr.  │                  │
│  │  • Budget Track  │     │  • Sleep trigger │                  │
│  │  • Runaway Det.  │     │                  │                  │
│  └────────┬─────────┘     └────────┬─────────┘                  │
│           │                        │                             │
│           │    ┌───────────────────┤                             │
│           │    │                   │                             │
│           ▼    ▼                   ▼                             │
│  ┌──────────────────┐     ┌──────────────────┐                  │
│  │    Letta API     │     │   Sleep Agent    │                  │
│  │  (Scarlet main)  │     │  (consolidation) │                  │
│  └────────┬─────────┘     └──────────────────┘                  │
│           │                                                      │
│           ▼                                                      │
│  ┌──────────────────────────────────────────┐                   │
│  │              STORAGE LAYER               │                   │
│  │  ┌────────┐  ┌────────┐  ┌────────────┐  │                   │
│  │  │ Redis  │  │ Qdrant │  │ PostgreSQL │  │                   │
│  │  │ (hot)  │  │ (cold) │  │  (Letta)   │  │                   │
│  │  └────────┘  └────────┘  └────────────┘  │                   │
│  └──────────────────────────────────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Motivazioni**:
- **Isolamento fault**: crash del loop non impatta webhook
- **Responsabilità chiare**: webhook per eventi esterni, runtime per continuità
- **Scalabilità**: può evolvere indipendentemente
- **Testabilità**: unit/integration test isolati

### 2. Configurazione Centralizzata

**Decisione**: File YAML unico per tutti i parametri configurabili.

**Path**: `scarlet/config/runtime.yaml`

```yaml
# === RUNTIME LOOP ===
loop:
  tick_interval_base_s: 30
  tick_interval_min_s: 10
  tick_interval_max_s: 300
  
# === BUDGET / QUOTA ===
budget:
  minimax:
    requests_limit: 5000
    window_seconds: 18000           # 5 ore
    throttle_threshold: 0.9
    reserve_for_sleep: 100
  
# === STATE MACHINE ===
states:
  allowed_transitions:
    idle: [thinking, sleeping, dreaming]
    thinking: [acting, idle, sleeping]
    acting: [thinking, idle, sleeping]
    sleeping: [idle, dreaming]
    dreaming: [idle, sleeping]
  
# === RUNAWAY DETECTION ===
runaway:
  window_ticks: 20
  window_seconds: 600
  score_threshold: 0.7
  consecutive_ticks: 5
  weights:
    progress_absence: 0.40
    trigger_density: 0.20
    signature_repetition: 0.25
    error_streak: 0.15
    
# === PROGRESS MARKERS ===
progress:
  significant_changes:
    - continuation_ref_change
    - evidence_outcome
    - working_set_step_advance
    - task_state_change
  noise_patterns:
    - intent_rephrase_only
    - confidence_change_only
    - timestamp_only

# === CIRCUIT BREAKER ===
circuit_breaker:
  error_threshold: 5
  reset_timeout_s: 60
  half_open_max_calls: 2

# === BACKOFF ===
backoff:
  initial_s: 5
  multiplier: 2.0
  max_s: 300
  jitter: 0.1

# === STORAGE ===
storage:
  redis:
    host: "abiogenesis-redis"
    port: 6379
    db: 0
    key_prefix: "scarlet:runtime:"
  qdrant:
    host: "abiogenesis-qdrant"
    port: 6333
    collections:
      learning_events: "learning_events"
      error_journal: "error_journal"
```

**Motivazioni**:
- Modifiche senza rebuild container
- Tutti i parametri in un posto
- Versionabile con Git
- Supporto per override ambiente

### 3. Loop Contract

**Decisione**: Il loop è **infinito by design** e fornisce continuità esistenziale.

**Invarianti**:

| # | Invariante | Garantita da |
|---|------------|--------------|
| 1 | **Liveness** | Il runtime può sempre produrre un tick (o backoff) | Try/except + backoff |
| 2 | **Snapshot** | Ogni tick prepara Environment Snapshot completo | Funzione dedicata |
| 3 | **Gating** | Trigger LLM solo se budget/health ok | should_trigger_llm() |
| 4 | **Autonomy** | Scarlet decide cosa fare, runtime facilita | StateTransitionRequest |
| 5 | **Persistence** | Working Set persiste tra tick | Redis + backup Qdrant |

**Environment Snapshot** (input ad ogni tick):

```python
@dataclass
class EnvironmentSnapshot:
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
```

**Working Set** (continuity memory):

```python
@dataclass
class WorkingSet:
    active_tasks: list[TaskEntry]
    pending_tasks: list[TaskEntry]
    parked_tasks: list[TaskEntry]
    last_thought_summary: str
    last_intent: str
    last_expected_evidence: str
    progress_markers: list[ProgressMarker]
    idempotency_keys: set[str]
```

### 4. State Machine

**Decisione**: 5 stati con transizioni validate dal runtime (non dall'LLM).

```
        ┌──────────────────────────────────────┐
        │                                      │
        ▼                                      │
    ┌───────┐     ┌──────────┐     ┌────────┐ │
    │ IDLE  │────▶│ THINKING │────▶│ ACTING │─┘
    └───┬───┘     └────┬─────┘     └────────┘
        │              │
        │              ▼
        │         ┌──────────┐
        └────────▶│ SLEEPING │◀───────────────┐
                  └────┬─────┘                │
                       │                      │
                       ▼                      │
                  ┌──────────┐                │
                  │ DREAMING │────────────────┘
                  └──────────┘
```

| Stato | Significato |
|-------|-------------|
| `IDLE` | Nulla da fare, attesa |
| `THINKING` | Elaborazione/decisione |
| `ACTING` | Esecuzione azione |
| `SLEEPING` | Sleep-time (ADR-003) |
| `DREAMING` | Consolidamento/dreaming |

**State Transition Request** (LLM → Runtime):

```python
@dataclass
class StateTransitionRequest:
    desired_state: RuntimeState
    transition_type: TransitionType  # continue_task, start_task, idle, sleep, dream, safe_mode
    reason: str
    continuation_ref: str | None
    confidence: float | None
    suggested_next_tick_s: float | None
```

Il runtime **valida** la richiesta contro le transizioni permesse in config.

**Override esterni**:

| Override | Effetto |
|----------|---------|
| `SAFE_MODE` | Riduce trigger rate, disabilita azioni costose |
| `PAUSE` | Nessun trigger LLM (solo health) |
| `RESUME` | Riprende normale |

### 5. Budget Tracking

**Decisione**: Rolling window con Redis Sorted Set per tracking condiviso.

```python
# Key: scarlet:runtime:budget:requests
# Type: Sorted Set (timestamp as score, request_id as member)

async def record_request(redis: Redis, request_id: str):
    now = time.time()
    window = 18000  # 5 ore
    
    await redis.zadd('scarlet:runtime:budget:requests', {request_id: now})
    await redis.zremrangebyscore('scarlet:runtime:budget:requests', 0, now - window)

async def get_remaining_budget(redis: Redis) -> int:
    now = time.time()
    used = await redis.zcount('scarlet:runtime:budget:requests', now - 18000, now)
    return 5000 - used
```

**Throttling** (non distruttivo):

| Condizione | Azione |
|------------|--------|
| Budget > 90% | Raddoppia tick interval |
| Budget esaurito | Attende (non errore) fino a slot disponibile |
| Reserve per sleep | Mantiene 100 richieste riservate |

### 6. Runaway Detection

**Decisione**: Score multi-fattore basato su **assenza di progresso**, non su regole rigide.

**Runaway = continuità senza progresso osservabile**.

**NON è runaway**:
- Uso di tool (legittimo)
- Ripetizione di per sé (può essere corretta)
- Loop infinito (è il design)

**Tipi di runaway**:

| Tipo | Segnale |
|------|---------|
| `tool_spam` | Alta signature_repetition, basso evidence |
| `thought_loop` | Basso progress, bassa action |
| `error_retry` | Alto error_streak |
| `no_op` | Alta trigger_density, zero progress |

**Runaway Score**:

```python
score = (
    weights['progress_absence'] * progress_absence +       # 0.40
    weights['trigger_density'] * trigger_density +         # 0.20
    weights['signature_repetition'] * signature_repetition + # 0.25
    weights['error_streak'] * error_streak                 # 0.15
)

is_runaway = (score > threshold) and (consecutive_ticks >= 5)
```

**Progress Markers** (cosa conta come progresso):

| Marker | Significato |
|--------|-------------|
| `continuation_ref_change` | Cambio task/thread |
| `evidence_outcome` | Verifica con esito |
| `working_set_step_advance` | Nuovo step |
| `task_state_change` | pending → active → done |

### 7. Learning Events

**Decisione**: Runaway emette Learning Event per futuro Learning Agent (L3.2).

```python
@dataclass
class LearningEvent:
    id: str
    timestamp: datetime
    event_type: Literal["runaway", "error_pattern", "success_pattern"]
    runaway_type: str
    runaway_score: RunawayScore
    window_start: datetime
    window_end: datetime
    tick_count: int
    working_set_before: dict
    working_set_after: dict
    action_signatures: list[str]
    evidence_expected: list[str]
    evidence_observed: list[str]
    hypothesis: str | None
    lesson_draft: str | None
    processed: bool = False
    processed_at: datetime | None = None
```

**Flusso futuro (L3.2)**:

1. L1 Runtime rileva runaway → emette LearningEvent → salva in Qdrant
2. Learning Agent (futuro) query `learning_events` con `processed=false`
3. Genera "autoprompt" come pensiero interno di Scarlet
4. Inietta: "[LEARNING] Ho notato che..."
5. Scarlet percepisce come propria riflessione

**Mitigazioni dopo Learning Event**:

| Mitigation | Quando |
|------------|--------|
| Throttle | Score > threshold |
| Replan | thought_loop |
| Park | no evidence definibile |
| Backoff | error_retry |
| Sleep/Dream | ruminazione |

### 8. Storage Strategy

**Decisione**: Redis per hot data, Qdrant per cold/audit, PostgreSQL per metriche.

| Dato | Storage | Motivazione |
|------|---------|-------------|
| Working Set | Redis | Accesso frequente ogni tick |
| Working Set backup | Qdrant (episodes) | Recovery, audit |
| Budget tracker | Redis | Atomic ops, TTL, condiviso |
| Runtime state | Redis | Veloce, volatile ok |
| Learning Events | Qdrant `learning_events` | Searchable per Learning Agent |
| Error Journal | Qdrant `error_journal` | Analisi pattern errori |
| Metriche | PostgreSQL | Retention lunga, query SQL |

**Redis Keys**:

```
scarlet:runtime:state           # RuntimeSnapshot JSON
scarlet:runtime:working_set     # WorkingSet JSON
scarlet:runtime:budget:requests # Sorted Set (timestamps)
scarlet:runtime:overrides       # Set di override attivi
scarlet:runtime:circuit:*       # Circuit breaker per capability
```

**Qdrant Collections** (nuove):

```python
# learning_events
{
    "vectors": {"size": 1024, "distance": "Cosine"},
    "payload_schema": {
        "event_type": "keyword",
        "runaway_type": "keyword",
        "timestamp": "datetime",
        "processed": "bool"
    }
}

# error_journal
{
    "vectors": {"size": 1024, "distance": "Cosine"},
    "payload_schema": {
        "error_type": "keyword",
        "capability": "keyword",
        "timestamp": "datetime",
        "resolved": "bool"
    }
}
```

### 9. Interazione Loop ↔ Webhook

**Decisione**: Il loop invia trigger a Letta come user-message (pensiero interno).

```
Loop tick → Letta API (user_message: "[INTERNAL] ...") → Scarlet processa
                                                              ↓
                                                        step-complete
                                                              ↓
                                                     Webhook attivato
                                                     (memory retrieval)
                                                              ↓
                                                   Ogni 5 msg → Sleep Agent
```

**Implicazioni**:
- Webhook continua a funzionare esattamente come oggi
- 4 tick interni + 1 messaggio utente = 5 messaggi per sleep
- Distinzione "interno vs esterno" è nel contenuto, non nel canale
- Multi-user communication sarà gestita in L7

### 10. Main Loop Implementation

```python
async def main_loop():
    config = RuntimeConfig.load()
    redis = await connect_redis(config)
    qdrant = await connect_qdrant(config)
    
    while True:  # Loop infinito by design
        tick_id = str(uuid4())
        
        try:
            # 1. Load state
            state = await load_runtime_state(redis)
            budget = await get_budget_snapshot(redis)
            working_set = await load_working_set(redis)
            
            # 2. Check gating
            if await circuit_breaker_open(state):
                await backoff(state)
                continue
            
            can_trigger, delay = await should_trigger_llm(
                EnvironmentSnapshot(state, budget, working_set)
            )
            
            if not can_trigger:
                await asyncio.sleep(delay)
                continue
            
            # 3. Build snapshot
            snapshot = await build_environment_snapshot(
                tick_id, state, budget, working_set
            )
            
            # 4. Trigger LLM
            llm_response = await trigger_scarlet(snapshot)
            await record_request(redis, tick_id)
            
            # 5. Process response
            transition_req = parse_transition_request(llm_response)
            
            if validate_transition(state, transition_req):
                await apply_transition(state, transition_req)
            
            await update_working_set(working_set, llm_response)
            
            # 6. Runaway check
            runaway_score = await calculate_runaway_score(redis, config)
            
            if runaway_score.is_runaway:
                event = create_learning_event(runaway_score, working_set)
                await save_learning_event(qdrant, event)
                await apply_runaway_mitigation(state, runaway_score)
            
            # 7. Persist
            await persist_state(redis, state)
            await persist_working_set(redis, working_set)
            await record_metrics(state, budget, runaway_score)
            
            # 8. Next tick
            interval = calculate_next_interval(state, budget, runaway_score)
            await asyncio.sleep(interval)
            
        except Exception as e:
            await handle_error(e, state)
            await backoff(state)
```

---

## Consequences

### Positive

- ✅ **Continuità esistenziale**: Scarlet "vive" 24/7
- ✅ **Isolamento**: Runtime separato da webhook
- ✅ **Configurabilità**: Tutti i parametri modificabili senza rebuild
- ✅ **Budget sostenibile**: Throttling previene esaurimento quota
- ✅ **Resilienza**: Circuit breaker e backoff per errori
- ✅ **Auto-awareness**: Runaway detection con Learning Events
- ✅ **Future-proof**: Hook per Learning Agent (L3.2)
- ✅ **Auditabilità**: Tutto persistito e searchable

### Negative

- ⚠️ **Complessità**: Nuovo servizio da mantenere
- ⚠️ **Risorse**: Container aggiuntivo (CPU/RAM)
- ⚠️ **Coordinamento**: Budget condiviso tra servizi
- ⚠️ **Debug**: Più componenti = più punti di failure

### Neutral

- 📝 Config file richiede documentazione
- 📝 Qdrant collections aggiuntive
- 📝 Redis come dipendenza critica

---

## Alternatives Considered

### Alternative A: Loop nel Webhook

**Descrizione**: Background task async nel container webhook esistente.

**Pro**: Meno servizi, deployment semplice.

**Rifiutata perché**:
- Fault domain condiviso: loop degrada → webhook impattato
- Responsabilità mescolate
- Testing più complesso

### Alternative B: Cron/Worker Jobs

**Descrizione**: Task schedulati esternamente che "pulsano" Scarlet.

**Pro**: Semplice, nessun loop sempre attivo.

**Rifiutata perché**:
- Non è vera "continuous existence"
- Difficile modellare stati e transizioni
- Latenza tra "pensieri" troppo alta

### Alternative C: Multi-Container con Message Queue

**Descrizione**: Loop + workers separati comunicanti via RabbitMQ/Redis Streams.

**Pro**: Massima scalabilità, event-driven.

**Rifiutata perché**:
- Over-engineering per fase attuale
- Complessità operativa
- Può essere evoluzione futura se necessario

---

## Implementation Plan

### Fase 1: Foundation (Week 1-2)

1. **Struttura progetto**
   - `scarlet/src/runtime/` directory
   - Config loader
   - Docker container setup

2. **State Machine**
   - RuntimeState enum
   - Transition validation
   - Override system

3. **Storage Setup**
   - Redis connection pool
   - Qdrant collections creation
   - Key schemas

### Fase 2: Core Loop (Week 2-3)

4. **Budget Tracker**
   - Redis sorted set operations
   - Throttling logic
   - Sleep agent integration

5. **Main Loop**
   - Tick orchestration
   - Environment snapshot building
   - LLM trigger logic

6. **Working Set**
   - TaskEntry management
   - Progress markers
   - Persistence

### Fase 3: Resilience (Week 3-4)

7. **Runaway Detection**
   - Score calculation
   - Learning Event emission
   - Mitigations

8. **Error Handling**
   - Circuit breaker
   - Backoff logic
   - Error journal

9. **Testing**
   - Unit tests
   - Integration tests
   - Load tests

### Fase 4: Integration (Week 4)

10. **Docker Compose**
    - New service definition
    - Health checks
    - Networking

11. **Documentation**
    - PROC for operations
    - Troubleshooting guide

---

## References

- [SPEC-004: Continuous Existence](../specifications/spec-004-continuous-existence.md) - Analisi completa
- [ADR-003: Custom Sleep-Time](adr-003-custom-sleep-time.md) - Integrazione sleep
- [ADR-005: Human-Like Memory](adr-005-human-like-memory-system.md) - Storage patterns
- [ROADMAP](../ROADMAP.md) - Layer 1 items

---

## Files da Creare

```
scarlet/
├── config/
│   └── runtime.yaml                 # Configurazione centralizzata
├── src/
│   └── runtime/
│       ├── __init__.py
│       ├── config.py                # Config loader
│       ├── loop.py                  # Main loop
│       ├── state.py                 # State machine
│       ├── budget.py                # Budget tracker
│       ├── working_set.py           # Working set management
│       ├── runaway.py               # Runaway detection
│       ├── learning_events.py       # Learning event emission
│       ├── circuit_breaker.py       # Circuit breaker
│       └── metrics.py               # Metrics collection
├── Dockerfile.runtime               # Container definition
└── tests/
    └── runtime/
        ├── test_loop.py
        ├── test_state.py
        ├── test_budget.py
        └── test_runaway.py
```

---

## History

- 2026-02-01: Initial creation based on SPEC-004 analysis and discussion

---

**ADR-006 v1.0.0 - ABIOGENESIS Project**  
*Vedi anche: [CONTEXT.md](../../CONTEXT.md), [ROADMAP.md](../ROADMAP.md)*
