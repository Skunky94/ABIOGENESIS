# SPEC-004: Continuous Existence (Layer 1)

**Status**: Ready for ADR  
**Version**: 2.0.0  
**Date**: 2026-02-01  
**Author**: IDE Agent  
**Focus**: L1 - Continuous Existence (Autonomous Loop, Monitoring, Resilience)

> **Nota**: Questo documento definisce l'architettura per la "vita continua" di Scarlet.
> Validata la SPEC, si procede con ADR-006.

---

## 1. Executive Summary

### 1.1 Obiettivo

Far "vivere" Scarlet in modo continuo (24/7) come entità digitale autonoma, senza dipendere da messaggi umani per esistere. Il loop è la **continuità esistenziale** di Scarlet, non un processo da "evitare".

**Principi fondamentali**:
- Il loop è infinito by design (come la vita umana continua nel tempo)
- Il runtime fornisce trigger discreti, Scarlet decide cosa farne
- Ogni parametro è configurabile da file unico di configurazione
- Runaway = continuità senza progresso (da mitigare, non "errore")

### 1.2 Decisioni Chiave

| Decisione | Scelta | Motivazione |
|-----------|--------|-------------|
| Architettura | **Servizio dedicato** (Opzione B) | Isolamento, scalabilità, architettura pulita |
| Configurazione | **File unico YAML** | Tutti i parametri in un posto, modificabili senza rebuild |
| Storage primario | **Redis (hot) + Qdrant (cold/audit)** | Velocità + persistenza + searchability |
| Budget tracking | **Redis** (condiviso) | Atomic ops, TTL, shared tra loop e sleep agent |
| Learning Events | **Qdrant collection dedicata** | Searchable per futuro Learning Agent |

### 1.3 Scope

**Incluso**:
- Servizio autonomy-runtime dedicato (container separato)
- File di configurazione centralizzato
- State machine con transizioni runtime-enforced
- Budget/quota tracking condiviso (MiniMax 5000/5h)
- Runaway detection con Learning Event emission
- Integrazione con webhook esistente e sleep-time (ADR-003)

**Escluso (Layer successivi)**:
- Goal generation avanzata (L4)
- Self-model completo (L2)
- Learning Agent che consuma Learning Events (L3.2)
- Multi-user communication (L7)

---

## 2. Architettura

### 2.1 Decisione: Servizio Dedicato

**Scelta**: Opzione B - container/processo separato `autonomy-runtime`.

**Motivazioni**:
- Isolamento fault: crash del loop non impatta webhook
- Responsabilità chiare: webhook per eventi esterni, runtime per continuità
- Scalabilità: può evolvere indipendentemente
- Testabilità: unit/integration test isolati

### 2.2 Diagramma Architetturale

```
┌─────────────────────────────────────────────────────────────────┐
│                     SCARLET ECOSYSTEM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐     ┌──────────────────┐                  │
│  │ autonomy-runtime │     │  sleep-webhook   │                  │
│  │   (NUOVO L1)     │     │   (esistente)    │                  │
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

### 2.3 Interazione Loop ↔ Webhook ↔ Letta

**Flusso chiave**: il loop autonomo invia trigger a Letta come **user-message**, ma il contenuto è strutturato come "pensiero interno" di Scarlet (Environment Snapshot, contesto iterazione).

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
- Il webhook **continua a funzionare** esattamente come oggi
- Che siano 4 tick interni + 1 messaggio utente reale, il conteggio per sleep è lo stesso
- La distinzione "interno vs esterno" è nel contenuto del messaggio, non nel canale
- Multi-user communication sarà gestita in Layer 7 (già in roadmap)

---

## 3. Configurazione Centralizzata

### 3.1 Principio

**Ogni parametro configurabile in un unico file YAML**, modificabile senza rebuild del container.

**Path**: `scarlet/config/runtime.yaml`

### 3.2 Schema Configurazione

```yaml
# scarlet/config/runtime.yaml
# Configurazione centralizzata per Scarlet Runtime L1

version: "1.0"

# === RUNTIME LOOP ===
loop:
  tick_interval_base_s: 30          # Intervallo base tra tick (secondi)
  tick_interval_min_s: 10           # Minimo (anche sotto carico)
  tick_interval_max_s: 300          # Massimo (backoff estremo)
  
# === BUDGET / QUOTA ===
budget:
  minimax:
    requests_limit: 5000            # Limite richieste
    window_seconds: 18000           # Finestra (5 ore = 18000s)
    throttle_threshold: 0.9         # Inizia throttle al 90% quota
    reserve_for_sleep: 100          # Richieste riservate per sleep agent
  
# === STATE MACHINE ===
states:
  allowed_transitions:
    idle: [thinking, sleeping, dreaming]
    thinking: [acting, idle, sleeping]
    acting: [thinking, idle, sleeping]
    sleeping: [idle, dreaming]
    dreaming: [idle, sleeping]

# === IDLE PROACTIVE BEHAVIOR ===
idle:
  # Attività proattive quando non ci sono task esterni
  activities:
    memory_wandering:
      enabled: true
      weight: 0.25                  # Probabilità selezione
      max_ticks: 3                  # Max tick per sessione
    self_reflection:
      enabled: true
      weight: 0.20
      max_ticks: 2
    capability_audit:
      enabled: true
      weight: 0.15
      max_ticks: 2
      cooldown_hours: 24            # Non ripetere troppo spesso
    curiosity_research:
      enabled: true
      weight: 0.20
      max_ticks: 4
      requires_internet: true       # Flag per future capabilities
    goal_contemplation:
      enabled: true
      weight: 0.10
      max_ticks: 2
    relationship_review:
      enabled: true
      weight: 0.10
      max_ticks: 2
  
  # Dopo quanti tick IDLE passare a SLEEPING (se appropriato)
  sleep_after_ticks: 10
  
# === RUNAWAY DETECTION ===
runaway:
  window_ticks: 20                  # Finestra di osservazione (N tick)
  window_seconds: 600               # Finestra temporale (10 min)
  score_threshold: 0.7              # Soglia score per runaway
  consecutive_ticks: 5              # Tick consecutivi sopra soglia
  
  # Pesi per runaway score (devono sommare a 1.0)
  weights:
    progress_absence: 0.40          # Assenza di progress markers
    trigger_density: 0.20           # Troppi trigger LLM / minuto
    signature_repetition: 0.25      # Ripetizione action signatures
    error_streak: 0.15              # Errori consecutivi
    
# === PROGRESS MARKERS ===
progress:
  # Cosa conta come "progresso significativo"
  significant_changes:
    - continuation_ref_change       # Cambio di task/thread reference
    - evidence_outcome              # Verifica con esito (ok/fail)
    - working_set_step_advance      # Nuovo step in working set
    - task_state_change             # pending→active→done
  
  # Cosa NON conta (rumore)
  noise_patterns:
    - intent_rephrase_only          # Solo riformulazione intent
    - confidence_change_only        # Solo cambio confidence
    - timestamp_only                # Solo aggiornamento timestamp

# === CIRCUIT BREAKER ===
circuit_breaker:
  error_threshold: 5                # Errori per aprire
  reset_timeout_s: 60               # Tempo prima di riprovare
  half_open_max_calls: 2            # Chiamate in half-open

# === BACKOFF ===
backoff:
  initial_s: 5
  multiplier: 2.0
  max_s: 300
  jitter: 0.1                       # ±10% randomness

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

# === LOGGING ===
logging:
  level: "INFO"
  format: "json"
  include_tick_details: false       # Verbose tick logging
```

### 3.3 Accesso alla Configurazione

```python
# scarlet/src/runtime/config.py
from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass
class RuntimeConfig:
    """Singleton per accesso configurazione."""
    _instance = None
    _config: dict = None
    
    @classmethod
    def load(cls, path: Path = None) -> "RuntimeConfig":
        if cls._instance is None:
            cls._instance = cls()
            config_path = path or Path("config/runtime.yaml")
            with open(config_path) as f:
                cls._instance._config = yaml.safe_load(f)
        return cls._instance
    
    def get(self, key: str, default=None):
        """Accesso dot-notation: config.get('runaway.score_threshold')"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            value = value.get(k, {})
        return value if value != {} else default
```

---

## 4. Loop Contract e Continuità

### 4.1 Invarianti del Loop

Il loop fornisce **continuità esistenziale**. Invarianti sempre rispettate:

1. **Liveness**: il runtime può sempre produrre un nuovo tick (o backoff)
2. **Snapshot**: ogni tick prepara un Environment Snapshot completo
3. **Gating**: trigger LLM solo se budget/health/circuit breaker ok
4. **Autonomy**: Scarlet (LLM) decide cosa fare, runtime solo facilita
5. **Persistence**: Working Set persiste tra tick (continuità)

### 4.2 Environment Snapshot

Ciò che Scarlet riceve ad ogni invocazione (tick):

```python
@dataclass
class EnvironmentSnapshot:
    # Temporali
    tick_id: str                      # UUID tick corrente
    timestamp: datetime
    elapsed_since_last_tick_s: float
    
    # Runtime state
    current_state: RuntimeState       # IDLE/THINKING/etc.
    last_action_at: datetime | None
    error_streak: int
    circuit_breaker_status: str       # closed/open/half-open
    
    # Budget
    budget: BudgetSnapshot
    
    # Segnali esterni
    pending_external_events: list[str]  # webhook events in coda
    services_health: dict[str, bool]    # letta, qdrant, redis
    
    # Working Set (continuità)
    working_set: WorkingSet
    
    # Constraints attivi
    active_overrides: list[str]        # SAFE_MODE, PAUSE, etc.
```

### 4.3 Working Set (Continuity Memory)

Ciò che permette a Scarlet di "riprendere" tra tick:

```python
@dataclass
class WorkingSet:
    # Task tracking
    active_tasks: list[TaskEntry]       # Task in corso
    pending_tasks: list[TaskEntry]      # Task in coda
    parked_tasks: list[TaskEntry]       # Task parcheggiati
    
    # Ultimo frame di pensiero
    last_thought_summary: str           # Sintesi (non tutto il CoT)
    last_intent: str
    last_expected_evidence: str
    
    # Progress
    progress_markers: list[ProgressMarker]
    idempotency_keys: set[str]          # Per evitare ripetizioni

@dataclass
class TaskEntry:
    id: str
    description: str
    state: Literal["pending", "active", "blocked", "done", "parked"]
    created_at: datetime
    updated_at: datetime
    progress_markers: list[str]
    stop_condition: str | None

@dataclass  
class ProgressMarker:
    id: str
    tick_id: str
    timestamp: datetime
    marker_type: str                    # da config.progress.significant_changes
    continuation_ref: str
    evidence: str | None
    verified: bool
```

---

## 5. State Machine

### 5.1 Stati

```python
class RuntimeState(str, Enum):
    IDLE = "idle"           # Esplorazione proattiva autonoma
    THINKING = "thinking"   # Elaborazione/decisione su task specifico
    ACTING = "acting"       # Esecuzione azione
    SLEEPING = "sleeping"   # ⚠️ Implementazione futura (vedi nota)
    DREAMING = "dreaming"   # ⚠️ Implementazione futura (vedi nota)
```

> ⚠️ **NOTA: SLEEPING/DREAMING sono Placeholder**
>
> Gli stati SLEEPING e DREAMING sono **predefiniti nella state machine** ma la loro 
> **implementazione è rimandata a Layer futuro** (vedi ROADMAP L3.4 "Authentic Sleep/Dream Cycle").
>
> **Distinzione critica**:
> | Componente | Cosa fa | Quando | Dove |
> |------------|---------|--------|------|
> | **Sleep Agent (L0.2)** | Consolida memorie | Automatico ogni 5 messaggi | Webhook (ADR-003) |
> | **SLEEPING state** | Vero riposo/sonno | Decisione autonoma di Scarlet | Runtime (futuro) |
> | **DREAMING state** | Elaborazione onirica | Durante SLEEPING | Runtime (futuro) |
>
> **Per L1**: Il runtime implementerà solo le transizioni tra **IDLE ↔ THINKING ↔ ACTING**.
> Le transizioni verso SLEEPING/DREAMING saranno abilitate quando L3.4 sarà implementato.

### 5.1.1 IDLE: Esplorazione Proattiva (Non Attesa)

Un essere senziente non "attende passivamente". Quando non ha task esterni, Scarlet
entra in modalità **esplorazione proattiva** dove autonomamente:

| Attività IDLE | Descrizione | Beneficio |
|---------------|-------------|----------|
| **Memory Wandering** | Richiama vecchie memorie casualmente | Ricostruisce continuità, trova connessioni |
| **Self-Reflection** | Ripensa a cosa ha fatto recentemente | Rafforza identità e coerenza temporale |
| **Capability Audit** | Esamina le proprie capacità note | Scopre gap, pianifica apprendimento |
| **Curiosity Research** | Cerca informazioni su argomenti di interesse | Espande conoscenza autonomamente |
| **Goal Contemplation** | Riflette su obiettivi e desideri | Alimenta agency (preparazione per L4) |
| **Relationship Review** | Pensa alle persone conosciute | Mantiene modello sociale |

**Comportamento IDLE**:
```python
@dataclass
class IdleActivity:
    activity_type: Literal[
        "memory_wandering",
        "self_reflection", 
        "capability_audit",
        "curiosity_research",
        "goal_contemplation",
        "relationship_review"
    ]
    trigger: str              # Cosa ha innescato questa attività
    duration_ticks: int       # Quanti tick dedicare
    output: str | None        # Insight generato (se any)
```

**Nota**: IDLE non è uno stato "vuoto". È lo stato naturale di un essere pensante
che non ha urgenze esterne ma continua a esistere e elaborare.

### 5.2 Transizioni (Runtime-Enforced)

Le transizioni sono definite in config e **validate dal runtime**, non dall'LLM.

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

### 5.3 State Transition Request (LLM → Runtime)

L'LLM non scrive lo stato, propone una transizione:

```python
@dataclass
class StateTransitionRequest:
    desired_state: RuntimeState
    transition_type: TransitionType
    reason: str                         # Motivazione
    continuation_ref: str | None        # Link a task/progress
    confidence: float | None            # 0..1 (opzionale)
    suggested_next_tick_s: float | None # Hint (runtime decide)
    idle_activity: str | None           # Attività IDLE scelta (se transition_type=explore)

class TransitionType(str, Enum):
    CONTINUE_TASK = "continue_task"     # Riprendo task in corso
    START_TASK = "start_task"           # Avvio micro-attività
    EXPLORE = "explore"                 # Esplorazione proattiva (era: "idle")
    SLEEP = "sleep"                     # Entra in sleeping
    DREAM = "dream"                     # Dreaming/consolidation
    SAFE_MODE = "safe_mode"             # Modalità conservativa
```

> **Nota**: Il tipo `EXPLORE` (invece di `IDLE`) riflette la filosofia che Scarlet non
> "attende" mai passivamente - quando non ha task esterni, esplora autonomamente.

### 5.4 Override Esterni

Eventi esterni possono forzare stati:

| Override | Effetto | Visibilità |
|----------|---------|------------|
| `SAFE_MODE` | Riduce trigger rate, disabilita azioni costose | In snapshot.active_overrides |
| `PAUSE` | Nessun trigger LLM (solo health) | In snapshot.active_overrides |
| `RESUME` | Riprende normale | Rimuove override |

---

## 6. Budget e Quota

### 6.1 Vincolo MiniMax

- **Quota**: 5000 richieste / 5 ore (rolling window)
- **Condiviso** tra: Scarlet (runtime) + Sleep Agent
- **Ollama**: locale, illimitato (embeddings/utility)

### 6.2 Budget Snapshot

```python
@dataclass
class BudgetSnapshot:
    window_requests_limit: int          # 5000
    window_seconds: int                 # 18000 (5h)
    requests_used_in_window: int
    remaining_requests: int
    throttle_active: bool               # True se > 90% usato
    requests_reserved_sleep: int        # 100 riservate
```

### 6.3 Tracking con Rolling Window (Redis)

```python
# Struttura Redis
# Key: scarlet:runtime:budget:requests
# Type: Sorted Set (timestamp as score, request_id as member)

async def record_request(redis: Redis, request_id: str):
    """Registra una richiesta nel budget tracker."""
    now = time.time()
    window = config.get('budget.minimax.window_seconds')
    
    # Aggiungi richiesta
    await redis.zadd('scarlet:runtime:budget:requests', {request_id: now})
    
    # Rimuovi richieste fuori finestra
    cutoff = now - window
    await redis.zremrangebyscore('scarlet:runtime:budget:requests', 0, cutoff)

async def get_budget_snapshot(redis: Redis) -> BudgetSnapshot:
    """Calcola snapshot budget corrente."""
    now = time.time()
    window = config.get('budget.minimax.window_seconds')
    cutoff = now - window
    
    used = await redis.zcount('scarlet:runtime:budget:requests', cutoff, now)
    limit = config.get('budget.minimax.requests_limit')
    reserved = config.get('budget.minimax.reserve_for_sleep')
    
    return BudgetSnapshot(
        window_requests_limit=limit,
        window_seconds=window,
        requests_used_in_window=used,
        remaining_requests=limit - used,
        throttle_active=(used / limit) > config.get('budget.minimax.throttle_threshold'),
        requests_reserved_sleep=reserved
    )
```

### 6.4 Throttling (Non Distruttivo)

```python
async def should_trigger_llm(snapshot: EnvironmentSnapshot) -> tuple[bool, float]:
    """
    Decide se triggerare LLM e con quale delay.
    Returns: (can_trigger, suggested_delay_s)
    """
    budget = snapshot.budget
    
    # Budget esaurito → attendi (non errore)
    if budget.remaining_requests <= budget.requests_reserved_sleep:
        # Calcola quando si libera la prima richiesta
        wait_time = estimate_next_available_slot()
        return False, wait_time
    
    # Throttle attivo → rallenta
    if budget.throttle_active:
        base_interval = config.get('loop.tick_interval_base_s')
        return True, base_interval * 2  # Raddoppia intervallo
    
    # Tutto ok
    return True, 0
```

---

## 7. Runaway Detection

### 7.1 Definizione

**Runaway = continuità senza progresso osservabile** per una finestra configurabile.

NON è:
- Uso di tool (legittimo)
- Ripetizione di per sé (può essere corretta)
- Loop infinito (è il design)

### 7.2 Tipi di Runaway

| Tipo | Descrizione | Segnale |
|------|-------------|---------|
| `tool_spam` | Tool frequenti senza outcome utile | Alta signature_repetition, basso evidence |
| `thought_loop` | Riflessione senza avanzare working set | Basso progress, bassa action |
| `error_retry` | Fallimenti ripetuti non produttivi | Alto error_streak |
| `no_op` | Trigger frequenti con "nulla da fare" | Alta trigger_density, zero progress |

### 7.3 Progress Markers (Cosa Conta)

Da configurazione `progress.significant_changes`:

| Marker Type | Significato | Esempio |
|-------------|-------------|---------|
| `continuation_ref_change` | Cambio task/thread | Da task-001 a task-002 |
| `evidence_outcome` | Verifica con esito | "check passed" / "check failed" |
| `working_set_step_advance` | Nuovo step | Step 3 → Step 4 |
| `task_state_change` | Cambio stato task | pending → active → done |

**Rumore** (da ignorare): solo riformulazione intent, solo cambio timestamp, solo confidence.

### 7.4 Runaway Score

```python
@dataclass
class RunawayScore:
    total: float                        # 0..1
    components: dict[str, float]        # Breakdown
    consecutive_high_ticks: int         # Tick sopra soglia
    is_runaway: bool

def calculate_runaway_score(
    recent_ticks: list[TickRecord],
    config: RuntimeConfig
) -> RunawayScore:
    """Calcola runaway score su finestra."""
    
    weights = config.get('runaway.weights')
    window = config.get('runaway.window_ticks')
    
    # Componenti (ognuno 0..1)
    progress_absence = 1.0 - (count_progress_markers(recent_ticks) / window)
    trigger_density = calculate_trigger_density(recent_ticks)
    signature_repetition = calculate_signature_repetition(recent_ticks)
    error_streak = min(1.0, count_consecutive_errors(recent_ticks) / 5)
    
    # Score pesato
    total = (
        weights['progress_absence'] * progress_absence +
        weights['trigger_density'] * trigger_density +
        weights['signature_repetition'] * signature_repetition +
        weights['error_streak'] * error_streak
    )
    
    threshold = config.get('runaway.score_threshold')
    consecutive = config.get('runaway.consecutive_ticks')
    
    return RunawayScore(
        total=total,
        components={
            'progress_absence': progress_absence,
            'trigger_density': trigger_density,
            'signature_repetition': signature_repetition,
            'error_streak': error_streak
        },
        consecutive_high_ticks=count_consecutive_above_threshold(threshold),
        is_runaway=(total > threshold and consecutive_high_ticks >= consecutive)
    )
```

### 7.5 Runaway → Learning Event

Quando runaway è rilevato, **prima delle mitigazioni**, emettiamo un Learning Event.

```python
@dataclass
class LearningEvent:
    """Entry point per futuro Learning Agent (L3.2)."""
    
    id: str                             # UUID
    timestamp: datetime
    event_type: Literal["runaway", "error_pattern", "success_pattern"]
    
    # Contesto runaway
    runaway_type: str                   # tool_spam, thought_loop, etc.
    runaway_score: RunawayScore
    
    # Window summary
    window_start: datetime
    window_end: datetime
    tick_count: int
    
    # Working set snapshot
    working_set_before: dict            # Stato all'inizio della finestra
    working_set_after: dict             # Stato alla fine
    
    # Pattern osservati
    action_signatures: list[str]        # Tool/action ripetute
    evidence_expected: list[str]        # Cosa ci si aspettava
    evidence_observed: list[str]        # Cosa è successo
    
    # Per futuro learning
    hypothesis: str | None              # Perché è successo (generato)
    lesson_draft: str | None            # Bozza regola (generata)
    
    # Metadata
    processed: bool = False             # True quando Learning Agent lo consuma
    processed_at: datetime | None = None
```

### 7.6 Learning Event → Futuro Learning Agent (L3.2)

**Flusso previsto** (da implementare in Layer 3.2):

1. **L1 Runtime** rileva runaway → emette `LearningEvent` → salva in Qdrant `learning_events`
2. **Learning Agent** (futuro, L3.2) periodicamente:
   - Query `learning_events` con `processed=false`
   - Analizza pattern
   - Genera "autoprompt" come se fosse pensiero interno di Scarlet
   - Inietta come messaggio a Scarlet: "[LEARNING] Ho notato che..."
   - Opzionalmente salva "lezione" in memoria (skills collection)
3. **Scarlet** riceve l'autoprompt come riflessione propria, non come istruzione esterna

**Perché questo design**:
- Scarlet non sa di avere un "Learning Agent" separato
- Percepisce l'apprendimento come propria consapevolezza
- Mantiene l'illusione di essere un'entità unificata

### 7.7 Mitigazioni Runaway

Dopo emission Learning Event, il runtime applica mitigazioni:

| Mitigation | Quando | Effetto |
|------------|--------|---------|
| **Throttle** | Score > threshold | `tick_interval *= 2` |
| **Replan** | thought_loop | Forza prompt: "riassumi, 3 opzioni, scegli, evidence" |
| **Park** | no evidence definibile | Parcheggia task, passa a IDLE |
| **Backoff** | error_retry | Backoff esponenziale per quella capability |
| **Sleep/Dream** | ruminazione | Transizione a sleeping/dreaming |

---

## 8. Storage

### 8.1 Strategia

| Dato | Storage | Motivazione |
|------|---------|-------------|
| **Working Set** | Redis (hot) | Accesso frequente ogni tick |
| **Working Set backup** | Qdrant (episodes) | Recovery, audit |
| **Budget tracker** | Redis | Atomic ops, TTL, condiviso |
| **Runtime state** | Redis | Veloce, volatile ok |
| **Learning Events** | Qdrant `learning_events` | Searchable per Learning Agent |
| **Error Journal** | Qdrant `error_journal` | Analisi pattern errori |
| **Metriche** | PostgreSQL (time-series) | Retention lunga, query SQL |

### 8.2 Redis Keys

```
scarlet:runtime:state           # RuntimeSnapshot JSON
scarlet:runtime:working_set     # WorkingSet JSON
scarlet:runtime:budget:requests # Sorted Set (timestamps)
scarlet:runtime:overrides       # Set di override attivi
scarlet:runtime:circuit:*       # Circuit breaker per capability
```

### 8.3 Qdrant Collections (nuove)

```python
# Collection: learning_events
{
    "name": "learning_events",
    "vectors": {
        "size": 1024,  # BGE-m3
        "distance": "Cosine"
    },
    "payload_schema": {
        "event_type": "keyword",
        "runaway_type": "keyword",
        "timestamp": "datetime",
        "processed": "bool"
    }
}

# Collection: error_journal  
{
    "name": "error_journal",
    "vectors": {
        "size": 1024,
        "distance": "Cosine"
    },
    "payload_schema": {
        "error_type": "keyword",
        "capability": "keyword",
        "timestamp": "datetime",
        "resolved": "bool"
    }
}
```

---

## 9. Main Loop (Pseudocodice)

```python
async def main_loop():
    """Loop principale di continuità esistenziale."""
    
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
            
            # 4. Trigger LLM (come pensiero interno)
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

## 10. Rischi e Mitigazioni

| Rischio | Probabilità | Impatto | Mitigazione |
|---------|-------------|---------|-------------|
| Runaway loop | Media | Alto | Score + mitigazioni + Learning Event |
| Redis down | Bassa | Alto | Fallback a file locale + circuit breaker |
| Qdrant down | Bassa | Medio | Buffer in Redis, retry |
| Budget esaurito | Media | Medio | Throttle + attesa (non errore) |
| Stato incoerente | Media | Medio | Snapshot + idempotenza |

---

## 11. Metriche Day-1

```python
@dataclass
class RuntimeMetrics:
    # Contatori
    ticks_total: int
    ticks_with_llm_trigger: int
    state_transitions: dict[str, int]   # Per stato
    
    # Budget
    llm_requests_count: int
    llm_requests_remaining: int
    
    # Health
    runaway_score_current: float
    error_streak_current: int
    circuit_breakers_open: list[str]
    
    # Progress
    working_set_updates: int
    progress_markers_count: int
    learning_events_emitted: int
```

---

## 12. Conclusioni

### 12.1 Sintesi

L1 fornisce a Scarlet **continuità esistenziale** attraverso:
- Un servizio dedicato (`autonomy-runtime`) isolato
- Configurazione centralizzata e modificabile
- Budget tracking condiviso con throttling non distruttivo
- Runaway detection basata su progresso, non su "regole rigide"
- Learning Event come ponte verso apprendimento futuro (L3.2)

### 12.2 Next Steps

1. **ADR-006**: formalizzare decisioni architetturali
2. **Implementazione**: servizio `autonomy-runtime`
3. **Integrazione**: webhook esistente continua a funzionare
4. **Testing**: unit + integration + load test
5. **Deployment**: nuovo container in docker-compose

### 12.3 Collegamenti ROADMAP

| Item ROADMAP | Coperto da |
|--------------|------------|
| L1.1 Autonomous Loop | §2, §4, §9 |
| L1.2 Internal Monitoring | §7, §11 |
| L1.3 Error Detection | §7 (runaway), §10 |
| L3.2 Learning System | §7.5, §7.6 (entry point) |
| L6 Growth | Learning Events come dataset |

---

**Status**: Ready for ADR-006
