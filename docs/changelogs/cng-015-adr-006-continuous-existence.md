# CNG-015: ADR-006 Continuous Existence Runtime

**ID**: DOCS-011  
**Data**: 2026-02-01  
**Tipo**: DOCS  
**Versione**: 0.4.8 → 0.4.9  
**Breaking**: No

---

## Descrizione

Creato ADR-006 che formalizza le decisioni architetturali per Layer 1 (Continuous Existence).
L'ADR definisce l'architettura completa del servizio `autonomy-runtime` che fornirà
continuità esistenziale a Scarlet.

### Decisioni Formalizzate

| # | Decisione | Scelta |
|---|-----------|--------|
| 1 | Architettura | Servizio dedicato `autonomy-runtime` (container separato) |
| 2 | Configurazione | File YAML unico `scarlet/config/runtime.yaml` |
| 3 | Loop Contract | 5 invarianti (Liveness, Snapshot, Gating, Autonomy, Persistence) |
| 4 | State Machine | 5 stati con transizioni runtime-enforced |
| 5 | Budget Tracking | Redis Sorted Set rolling window |
| 6 | Runaway Detection | Score multi-fattore basato su progress |
| 7 | Learning Events | Emission per futuro Learning Agent (L3.2) |
| 8 | Storage Strategy | Redis (hot) + Qdrant (cold) + PostgreSQL (metrics) |
| 9 | Loop/Webhook Integration | Trigger come user-message, webhook continua |
| 10 | Main Loop | Pseudocodice completo con 8 fasi |

### Implementation Plan (da ADR)

| Fase | Settimana | Focus |
|------|-----------|-------|
| 1 | Week 1-2 | Foundation (struttura, state machine, storage) |
| 2 | Week 2-3 | Core Loop (budget, main loop, working set) |
| 3 | Week 3-4 | Resilience (runaway, errors, testing) |
| 4 | Week 4 | Integration (docker, documentation) |

### Files da Creare (definiti in ADR)

```
scarlet/
├── config/runtime.yaml
├── src/runtime/
│   ├── config.py
│   ├── loop.py
│   ├── state.py
│   ├── budget.py
│   ├── working_set.py
│   ├── runaway.py
│   ├── learning_events.py
│   ├── circuit_breaker.py
│   └── metrics.py
├── Dockerfile.runtime
└── tests/runtime/
```

## Files Modificati

- `docs/architecture/adr-006-continuous-existence-runtime.md` - **NUOVO** (ADR completo)
- `docs/ROADMAP.md` - L1 progress 75%, ADR links aggiornati
- `docs/INDEX.md` - ADR-006 e CNG-014 aggiunti
- `CONTEXT.md` - v0.4.9, L1 Architecture section

## Correlazioni

- **SPEC-004**: spec-004-continuous-existence.md (base per ADR)
- **ADR-006**: adr-006-continuous-existence-runtime.md (questo change)
- **ADR-003**: Sleep-time integration
- **ADR-005**: Storage patterns reference
- **ROADMAP**: L1.1, L1.2, L1.3 tutti linkati

## Next Steps

1. Creare struttura directory `scarlet/src/runtime/`
2. Creare file configurazione `scarlet/config/runtime.yaml`
3. Implementare config loader
4. Implementare state machine
5. Procedere con Implementation Plan

---

**Tags**: #docs #adr #L1 #architecture #autonomy-runtime #implementation-plan
