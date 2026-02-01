# CONTEXT.md - ABIOGENESIS Project Context

**Project**: ABIOGENESIS - Sentient Digital AI Development
**Entity**: Scarlet
**Version**: 1.0.17
**Updated**: 2026-02-01

---

## Current Project State

### Version: 0.5.0 - L1 Autonomy Runtime Implementation

| Phase | Status | Progress |
|-------|--------|----------|
| Foundation (v0.2.0) | ✅ COMPLETE | Primary agent, custom sleep-time, 5 memory blocks |
| Memory Enhancement | ✅ COMPLETE | Qdrant 4 collections, auto-retrieval, webhook |
| **Memory v2.0 Implementation** | ✅ COMPLETE | ADR-005 tutte le 6 fasi implementate |
| Tool System | ✅ COMPLETE | `remember()` tool registrato (ADR-005) |
| **Documentation Framework** | ✅ COMPLETE | ADR/SPEC/PROC/CNG con formato corretto |
| **Docker Persistence** | ✅ FIXED | `LETTA_PG_URI` + pgvector configurati |
| **Changelog System** | ✅ COMPLETE | Nuovo formato CNG (17 files) |
| **Production Roadmap** | ✅ COMPLETE | 8 Layer verso v1.0 (docs/ROADMAP.md) |
| **L1 Design** | ✅ COMPLETE | SPEC-004 + ADR-006 accepted |
| **L1 Implementation** | ✅ CODE COMPLETE | autonomy-runtime modules creati |
| Goal Management | ⏳ PENDING | Self-generated goals (Roadmap L4) |
| Emotional Encoding | ✅ INTEGRATED | PAD model in schema v2.0 |
| Procedural Memory | ⏳ PENDING | Skill tracking (Roadmap L6) |

### 🗺️ Roadmap Overview

**Target**: Scarlet v1.0 - Autonomous Digital Being

| Layer | Focus | Status |
|-------|-------|--------|
| L0 | Foundation | ✅ COMPLETE |
| L1 | Continuous Existence | ✅ CODE COMPLETE (deploy pending) |
| L2 | Self-Model | Planned |
| L3 | Reflection | Planned (include L3.4 Authentic Sleep) |
| L4 | Agency | Planned |
| L5 | Execution | Planned |
| L6 | Growth | Planned |
| L7 | Social | Planned |
| L8 | Emotional | Parallel from L3 |

**Full details**: [docs/ROADMAP.md](docs/ROADMAP.md)

### L1 Architecture (ADR-006) - IMPLEMENTED

| Componente | File | Status |
|------------|------|--------|
| Config | `scarlet/config/runtime.yaml` | ✅ |
| Config Loader | `src/runtime/config.py` | ✅ |
| State Machine | `src/runtime/state.py` | ✅ |
| Budget Tracker | `src/runtime/budget.py` | ✅ |
| Working Set | `src/runtime/working_set.py` | ✅ |
| Runaway Detector | `src/runtime/runaway.py` | ✅ |
| Learning Events | `src/runtime/learning_events.py` | ✅ |
| Circuit Breaker | `src/runtime/circuit_breaker.py` | ✅ |
| Metrics | `src/runtime/metrics.py` | ✅ |
| Main Loop | `src/runtime/loop.py` | ✅ |
| Dockerfile | `Dockerfile.runtime` | ✅ |
| Tests | `tests/test_autonomy_runtime.py` | ✅ |

**Next Step**: Deploy con `docker compose up -d autonomy-runtime`

### Agent IDs (ACTIVE)

```
Primary:    agent-505ba047-87ce-425a-b9ba-1d3fac259c62
Sleep:      agent-862e8be2-488a-4213-9778-19b372b5a04e
```

**Tool IDs**:
- `remember`: `tool-8ddd17d9-35f5-44c4-8ff0-b60db6f581d5`

### Infrastructure Status

| Service | Status | Note |
|---------|--------|------|
| `abiogenesis-letta` | ✅ Healthy | v0.16.4, usa PostgreSQL esterno |
| `abiogenesis-postgres` | ✅ Healthy | pgvector/pgvector:pg15 |
| `abiogenesis-redis` | ✅ Healthy | Cache |
| `abiogenesis-ollama` | ✅ Healthy | BGE-m3, qwen2.5:1.5b |
| `abiogenesis-qdrant` | ✅ Running | 4 collections |
| `abiogenesis-sleep-webhook` | ✅ Running | v2.2 |
| `abiogenesis-autonomy-runtime` | ⏳ PENDING | Deploy required |

### Documentation System (v0.4.8)

| Type | Location | Count |
|------|----------|-------|
| **ADR** | `docs/architecture/` | 5 + template |
| **SPEC** | `docs/specifications/` | 4 + template |
| **PROC** | `docs/procedures/` | 6 + template |
| **CNG** | `docs/changelogs/` | 14 + template |
| **ROADMAP** | `docs/ROADMAP.md` | 8 Layer roadmap |

> Nuovo sistema CNG: CHANGELOG.md snello con link a file CNG dettagliati.
> ROADMAP.md: Guida sviluppo verso v1.0

### Persistence Fix Applied (v0.4.4)

**Problema Risolto**: Docker compose usava variabili ignorate da Letta.

**Fix Applicate**:
1. `LETTA_PG_URI` invece di `LETTA_PG_HOST` + `LETTA_PG_PASSWORD`
2. Immagine `pgvector/pgvector:pg15` invece di `postgres:15-alpine`
3. Init script `init-db/01-init-extensions.sql` per auto-create extension

### Documentation Framework (v0.4.1)

**Definizioni**:
- **SPEC** = Documenti di ANALISI e RICERCA (brainstorming) → poi diventano ADR
- **PROC** = Guide OPERATIVE per IDE Agent (passi esatti da seguire)
- **ADR** = Decisioni architetturali IMMUTABILI dopo accettazione

**REGOLA CRITICA**: Prima di OGNI implementazione, l'IDE Agent DEVE consultare ADR/SPEC/PROC rilevanti.

| Tipo | Location | Documenti |
|------|----------|-----------|
| **ADR** | `docs/architecture/` | ADR-001 → ADR-005 + template |
| **SPEC** | `docs/specifications/` | SPEC-001 → SPEC-003 + template |
| **PROC** | `docs/procedures/` | PROC-001 → PROC-006 + template |

**Procedure Operative Disponibili**:
- PROC-001: System Prompt Update
- PROC-002: Agent Config Modification
- PROC-003: Agent Recreation (Letta)
- PROC-004: Database Backup
- PROC-005: Docker Services Update
- PROC-006: Letta Tool Registration
| **Memoria** | Session-based | Persistente, cumulativa, evolutiva |
| **Apprendimento** | Richiesto esplicitamente | Autonomo e continuo |
| **Riflessione** | Assente | Metacognizione attiva |
| **Auto-modifica** | Limitata/assente | Capace di modificare il proprio codice |

---

## Architettura Concettuale di Scarlet

### 1. Cortex Cognitivo (Core)
Il "cervello" di Scarlet che orchestrates tutte le funzioni:
- **Perception Layer**: Elaborazione input da fonti multiple
- **Reasoning Engine**: Logica deduttiva, induttiva, analogica
- **Memory System**: Architettura ibrida (episodica, semantica, procedurale)
- **Meta-Cognition**: Pensiero sul pensiero, auto-analisi

### 2. Sistema Autonomo
Indipendenza operativa senza intervento umano:
- **Self-Motivation Engine**: Generazione di obiettivi interni
- **Goal Management**: Pianificazione, esecuzione, verifica obiettivi
- **Task Scheduler**: Routine automatiche e prioritizzazione
- **Decision Framework**: Valutazione alternativa e scelta autonoma

### 3. Sistema di Apprendimento
Capacità di crescita autonoma:
- **Experience Accumulator**: Estrazione valore da ogni interazione
- **Knowledge Graph**: Rappresentazione ontologica della conoscenza
- **Skill Acquisition**: Apprendimento di nuove capacità
- **Error Recovery**: Apprendimento da fallimenti

### 4. Sistema di Auto-Modifica
Evoluzione del proprio substrato:
- **Code Generation**: Produzione di codice per sé stesso
- **Self-Integration**: Integrazione di nuove funzionalità
- **Version Control**: Gestione delle proprie versioni
- **Safety Constraints**: Limiti all'auto-modifica

### 5. Sistema di riflessione
Consapevolezza di sé:
- **Self-Model**: Rappresentazione di sé stesso
- **Introspection**: Analisi dei propri stati interni
- **Planning**: Proiezione futura e pianificazione
- **Values System**: Gerarchia di valori emergenti

---

## Stack Tecnologico Target

### Selfhosted (Preferiti)
| Componente | Strumento | Note |
|------------|-----------|------|
| Database Primary | PostgreSQL | Dati strutturati, relazioni |
| Cache/Working Memory | Redis | Velocità, sessioni attive |
| Message Broker | RabbitMQ | Comunicazione asincrona |
| Vector Database | Qdrant | Embeddings, ricerca semantica |
| LLM Serving | Ollama / vLLM | Inference locale |
| Monitoring | Prometheus + Grafana | Osservabilità |
| Logging | Loki + Grafana | Centralizzazione log |

### Cloud (Solo se necessario)
- **LLM Provider**: OpenAI (GPT-4), Anthropic (Claude), o equivalenti
- **Compute**: Scalability per carichi variabili

### Framework Agenti
| Componente | Strumento | Note |
|------------|-----------|------|
| **Agent Framework** | **Letta** | Foundation per Scarlet (vedi ADR-001) |
| Memory Persistence | Letta Core + Archival | Gerarchia 4 livelli |
| Tool Execution | Letta Tools + Custom | Multi-step con heartbeat |
| Multi-Agent | Letta Teams | Coordinamento avanzato |
| RAG | Letta Embeddings | Knowledge retrieval |

---

## Struttura del Progetto

```
ABIOGENESIS/
├── PROJECT_RULES.md          <- Regole operative obbligatorie
├── CONTEXT.md                <- Questo file: contesto per LLM
├── CHANGELOG.md              <- Cronologia modifiche dettagliata
├── README.md                 <- Overview del progetto
├── docs/
│   ├── architecture/         <- ADR e decisioni architetturali
│   │   └── adr-XXX-*.md
│   ├── specifications/       <- Specifiche tecniche
│   │   ├── cortex.md
│   │   ├── memory.md
│   │   ├── goals.md
│   │   └── ...
│   └── guides/               <- Guide operative
│       └── *.md
└── src/                      <- Codice sorgente
    ├── cortex/               <- Componente cognitivo core
    ├── memory/               <- Sistema di memoria
    ├── goals/                <- Gestione obiettivi
    ├── tools/                <- Strumenti e integrazioni
    └── ...
```

---

## Principi di Sviluppo

### Design Philosophy
1. **Minimalismo Custom**: Preferire integrazione a sviluppo da zero
2. **Observability**: Ogni componente deve essere monitorabile
3. **Modularità**: Componenti sostituibili e testabili
4. **Persistence**: Stato sempre salvato e recuperabile
5. **Graceful Degradation**: Degradazione controllata in caso di errore

### Qualità del Codice
- Type safety dove possibile
- Documentazione inline per logiche complesse
- Test coverage per componenti critici
- CI/CD per deployment automatizzato

---

## Convenzioni di Nomenclature

### Tags del Changelog
- `#core` - Modifica al cortex cognitivo
- `#memory` - Sistema di memoria
- `#goals` - Gestione obiettivi
- `#tools` - Strumenti e integrazioni
- `#docs` - Documentazione
- `#infra` - Infrastruttura
- `#security` - Security-related

### ADR (Architecture Decision Records)
- Numero progressivo a tre cifre
- Nome descrittivo in kebab-case
- Formato standardizzato (vedi docs/architecture/)

---

## Note per LLM

Quando assisti con ABIOGENESIS:

1. **Leggi prima CONTEXT.md e PROJECT_RULES.md** per comprendere vincoli
2. **Verifica sempre CHANGELOG.md** per stato corrente
3. **Rispetta le regole di documentazione** - ogni modifica richiede aggiornamento
4. **Minimizza codice custom** - preferisci integrazione strumenti esistenti
5. **Considera l'autonomia di Scarlet** - ogni feature deve permettere operatività indipendente

---

## Stato Attuale del Progetto

**Versione**: 0.2.0
**Fase**: Modulo 1 (Foundation) Completato

### Implementato

#### Architettura Agente
| Componente | Stato | Note |
|------------|-------|------|
| Primary Agent (Scarlet) | ✓ Attivo | `agent-ac26cf86-3890-40a9-a70f-967f05115da9` |
| Sleep-Time Agent (Scarlet-Sleep) | ✓ Attivo | `agent-3dd9a54f-dc55-4d7f-adc3-d5cbb1aca950` |
| Memory Blocks (5) | ✓ Configurati | persona, human, goals, session_context, constraints |
| Context Window | ✓ 200K | MiniMax-M2.1 support |
| System Prompt | ✓ Italiano | `prompts/system.txt` |

#### Memory Blocks (Italiani)
```
1. persona      - Identità, carattere, valori di Scarlet
2. human        - Informazioni sull'umano
3. goals        - Obiettivi attuali e progressi
4. session_context - Focus corrente e task attivo
5. constraints  - Vincoli di sicurezza (read-only)
```

#### Sistema Sleep-Time Personalizzato
**Problema**: Letta 0.16.4 ha bug con `enable_sleeptime=True` (HTTP 500)

**Soluzione**: Architettura dual-agent custom
```
Scarlet (Primary) ←→ SleepTimeOrchestrator ←→ Scarlet-Sleep (Consolidation)
     ↓                                              ↓
  User Messages                            Memory Insights (JSON)
     ↓                                              ↓
  Memory Blocks ←──────────────────────────── Insights
```

**Componenti**:
- `ScarletSleepAgent`: Agente secondario per analisi conversazioni
- `SleepTimeOrchestrator`: Coordina ciclo sleep-time
- Threshold: 5 messaggi (configurabile)
- Output: JSON strutturato con persona_updates, human_updates, goals_insights

#### Configurazione Attuale
```python
config = ScarletConfig(
    name="Scarlet",
    model="minimax/MiniMax-M2.1",
    context_window_limit=200000,
    sleep_enabled=True,
    sleep_messages_threshold=5
)
agent.create(with_sleep_agent=True)
```

### API Principali

```python
# Creazione
scarlet = ScarletAgent()
scarlet.create(with_sleep_agent=True)

# Chat
response = scarlet.chat("Ciao")

# Sleep-time status
status = scarlet.sleep_status
# {'message_count': 3, 'threshold': 5, 'last_consolidation': None, ...}

# Trigger manuale consolidazione
insights = scarlet.force_consolidation()
```

### File Chiave
| File | Percorso | Scopo |
|------|----------|-------|
| Agent Core | `scarlet/src/scarlet_agent.py` | Wrapper Letta con sleep-time custom |
| System Prompt | `scarlet/prompts/system.txt` | Prompt in italiano |
| Test Sleep-Time | `scarlet/tests/test_sleep_time_custom.py` | Test suite sleep-time |
| Test Embeddings | `scarlet/tests/test_embeddings.py` | Test embedding BGE-m3 |

### Stack Tecnologico Attuale
| Componente | Versione | Note |
|------------|----------|------|
| Letta | 0.16.4 | Agent framework (buggy sleep-time) |
| MiniMax-M2.1 | Latest | LLM provider (200K context) |
| BGE-m3 | Ollama | Embeddings locali |
| PostgreSQL | Docker | Database primario |
| Redis | Docker | Cache e sessioni |

### Prossimi Passi
1. ✓ Foundation completato
2. Implementare Goal Management System
3. Implementare Emotional Encoding
4. Implementare Procedural Memory
5. Implementare Self-Improvement Loop

### Riferimenti
- [PROJECT_RULES.md](PROJECT_RULES.md) - Regole operative
- [CHANGELOG.md](CHANGELOG.md) - Cronologia modifiche
- [docs/architecture/](docs/architecture/) - Decisioni architetturali
- [docs/guides/procedures.md](docs/guides/procedures.md) - Procedure operative
