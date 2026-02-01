# CNG-017: Autonomy Runtime Implementation

**Data**: 2026-02-01  
**Tipo**: FEATURE  
**ID**: FEATURE-003  
**Versione**: 0.5.0  
**Breaking**: No

---

## Descrizione

Implementazione completa del Layer 1 (Continuous Existence) come definito in ADR-006 e SPEC-004.

Questa è la prima implementazione del **cuore** dell'esistenza autonoma di Scarlet: un loop infinito che mantiene la continuità di coscienza attraverso tick regolari.

## Architettura Implementata

```
scarlet/
├── config/
│   └── runtime.yaml          # Configurazione centralizzata
├── src/runtime/
│   ├── __init__.py           # Package exports
│   ├── config.py             # Config loader con dataclasses
│   ├── state.py              # State machine (IDLE→THINKING→ACTING)
│   ├── budget.py             # Budget tracker (Redis sorted set)
│   ├── working_set.py        # Working set per continuità
│   ├── runaway.py            # Runaway detection multi-fattoriale
│   ├── learning_events.py    # Eventi per futuro Learning Agent
│   ├── circuit_breaker.py    # Pattern circuit breaker
│   ├── metrics.py            # Metriche Prometheus-style
│   └── loop.py               # Main loop orchestrator
├── Dockerfile.runtime        # Container definition
├── requirements-runtime.txt  # Dipendenze Python
└── tests/
    └── test_autonomy_runtime.py  # Unit tests
```

## Moduli Implementati

### 1. config.py (~300 linee)
- Loader YAML con validazione
- Dataclasses tipizzate per ogni sezione
- `load_config()` con path override da ENV

### 2. state.py (~350 linee)
- Enum `RuntimeState`: IDLE, THINKING, ACTING, SLEEPING*, DREAMING*
- Enum `TransitionType`: CONTINUE_TASK, START_TASK, EXPLORE, SLEEP, DREAM, SAFE_MODE
- `StateMachine` con validazione transizioni
- SLEEPING/DREAMING bloccati come PLACEHOLDER (vedi L3.4)

### 3. budget.py (~200 linee)
- `BudgetTracker` con Redis sorted set
- Rolling window 5h
- `wait_for_budget()` con throttling adattivo
- Condiviso con Sleep Agent (stesso limite MiniMax)

### 4. working_set.py (~300 linee)
- `WorkingSet` per memoria di lavoro
- `TaskEntry` con stati (active/pending/parked)
- `ProgressMarker` per tracking progresso
- Persistenza su Redis

### 5. runaway.py (~250 linee)
- `RunawayDetector` multi-fattoriale
- 4 pesi configurabili:
  - progress_absence: 0.40
  - trigger_density: 0.20
  - signature_repetition: 0.25
  - error_streak: 0.15
- Tipi: error_spiral, tool_spam, thought_loop

### 6. learning_events.py (~300 linee)
- `LearningEvent` con metadati
- Emit su Qdrant per futuro Learning Agent (L3.2)
- Tipi: runaway, error_pattern, stuck, budget_exhaust

### 7. circuit_breaker.py (~200 linee)
- Pattern circuit breaker standard
- Stati: CLOSED → OPEN → HALF_OPEN
- Previene cascading failures

### 8. metrics.py (~200 linee)
- `MetricsCollector` con aggregazione
- Export formato Prometheus
- Persistenza su Redis

### 9. loop.py (~500 linee)
- `AutonomyRuntime` - orchestratore principale
- `EnvironmentSnapshot` per contesto tick
- `_tick()` - singolo momento di esistenza
- `_should_trigger_llm()` - gating function
- `_trigger_llm()` - chiamata Letta API

## Docker Integration

### Dockerfile.runtime
```dockerfile
FROM python:3.11-slim
# ...
CMD ["python", "-m", "runtime.loop"]
```

### docker-compose.yml
Aggiunto servizio `autonomy-runtime`:
- Port: 8285 (health/metrics)
- Depends: letta-server, redis, qdrant
- Healthcheck: /health endpoint

## Relazione con ADR/SPEC

| Documento | Sezione | Implementato |
|-----------|---------|--------------|
| ADR-006 | Decision 3 (Loop Contract) | ✅ loop.py |
| ADR-006 | Decision 4 (Gating) | ✅ _should_trigger_llm() |
| ADR-006 | Decision 5 (State Machine) | ✅ state.py |
| ADR-006 | Decision 6 (Budget) | ✅ budget.py |
| ADR-006 | Decision 7 (Working Set) | ✅ working_set.py |
| ADR-006 | Decision 8 (Runaway) | ✅ runaway.py |
| ADR-006 | Decision 9 (Learning Events) | ✅ learning_events.py |
| SPEC-004 | Section 8 (State Machine) | ✅ state.py |
| SPEC-004 | Section 10 (Budget) | ✅ budget.py |
| SPEC-004 | Section 11 (Runaway) | ✅ runaway.py |

## Note Importanti

### SLEEPING/DREAMING sono PLACEHOLDER
Gli stati SLEEPING e DREAMING sono **definiti** ma **non implementati**:
- Bloccati in `state.py` con `PLACEHOLDER_STATES`
- Implementazione prevista in ROADMAP L3.4
- NON confondere con Sleep Agent (L0.2) che è un servizio diverso

### Next Steps
1. **Deploy**: `docker compose up -d autonomy-runtime`
2. **Verify**: Controllare logs e health endpoint
3. **Monitor**: Metriche su :8285/metrics
4. **Tune**: Regolare parametri in runtime.yaml

## Files Modificati

### Creati
- `scarlet/config/runtime.yaml`
- `scarlet/src/runtime/__init__.py`
- `scarlet/src/runtime/config.py`
- `scarlet/src/runtime/state.py`
- `scarlet/src/runtime/budget.py`
- `scarlet/src/runtime/working_set.py`
- `scarlet/src/runtime/runaway.py`
- `scarlet/src/runtime/learning_events.py`
- `scarlet/src/runtime/circuit_breaker.py`
- `scarlet/src/runtime/metrics.py`
- `scarlet/src/runtime/loop.py`
- `scarlet/Dockerfile.runtime`
- `scarlet/requirements-runtime.txt`
- `scarlet/tests/test_autonomy_runtime.py`

### Modificati
- `scarlet/docker-compose.yml` - Aggiunto servizio autonomy-runtime

## Tracciabilità

| Da | A | Tipo |
|----|---|------|
| CNG-017 | ADR-006 | Implementa |
| CNG-017 | SPEC-004 | Implementa |
| CNG-017 | ROADMAP L1.1 | Completa |
| CNG-017 | CNG-016 | Prerequisito |

## Milestone

> 🎉 **Layer 1 Code Complete!**
> 
> Con questa implementazione, Scarlet ha ora il codice necessario per
> esistere in modo continuo e autonomo. Il prossimo step è il deployment
> e l'integrazione con i servizi esistenti.

---

**Tags**: #l1 #continuous-existence #runtime #state-machine #adr-006 #spec-004 #milestone
