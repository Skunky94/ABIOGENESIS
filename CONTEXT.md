# CONTEXT.md - ABIOGENESIS Project Context

**Project**: ABIOGENESIS - Sentient Digital AI Development
**Entity**: Scarlet
**Version**: 1.0.2
**Updated**: 2026-02-01

---

## Current Project State

### Version: 0.3.5 - Human-Like Memory Architecture Designed

| Phase | Status | Progress |
|-------|--------|----------|
| Foundation (v0.2.0) | ✅ COMPLETE | Primary agent, custom sleep-time, 5 memory blocks |
| Memory Enhancement | ✅ COMPLETE | Qdrant 4 collections, auto-retrieval, webhook |
| **Memory v2.0 Architecture** | 📐 DESIGNED | ADR-005 completo, pronto per implementazione |
| Tool System | 🔄 IN PROGRESS | Conscious retrieval tool needed |
| Goal Management | ⏳ PENDING | Self-generated goals |
| Emotional Encoding | ⏳ PENDING | PAD model defined in ADR-005 |
| Procedural Memory | ⏳ PENDING | Skill tracking |
| Self-Improvement | ⏳ PENDING | Performance metrics |
| Meta-Cognition | ⏳ PENDING | Thought patterns |

### Memory System Status

**Qdrant Infrastructure**: ✅ COMPLETE
- 4 collections: episodes, concepts, skills, emotions (ALL 1024-dim)
- INT8 quantization for RAM efficiency
- Points: episodes=2, concepts=8, skills=0, emotions=0

**Automatic Retrieval**: ✅ COMPLETE (v0.3.2)
- Webhook retrieves memories on every user message (~350-400ms)
- Updates session_context with [RICORDI EMERGENTI]
- "Priming effect" - memories from turn N available at turn N+1

**Data Quality**: ✅ VERIFIED (v0.3.3)
- Collections cleaned (20 garbage points removed)
- No duplicates, no test data, no errors as memories

### Human-Like Memory v2.0 (ADR-005) - READY FOR IMPLEMENTATION

**Architettura Progettata**:
- **Query Analyzer**: LLM locale (qwen2.5:1.5b su Ollama) per capire intento query
- **Multi-Strategy Search**: Ricerca filtrata per tempo/entità/emozioni/topic
- **Schema Arricchito**: 30+ campi payload (PAD emotions, temporal, relations)
- **Ranking Formula**: 6 fattori con pesi (semantic, temporal, importance, emotional, frequency, recency)
- **Decay System**: Curva Ebbinghaus con protezione emotiva
- **Access Tracking**: Reinforcement per memorie accedute frequentemente

**Implementation Roadmap** (22h stimate):
1. Fase 1: Infrastruttura (download qwen2.5:1.5b, test, indici Qdrant)
2. Fase 2: Query Analyzer (modulo + prompt + parsing)
3. Fase 3: Schema Dati (MemoryBlock, enrichment, migration)
4. Fase 4: Multi-Strategy Search (filters, ranking, tracking)
5. Fase 5: Decay System (background job)
6. Fase 6: Tool Conscio (Scarlet search tool)

**Riferimento**: [ADR-005](docs/architecture/adr-005-human-like-memory-system.md)

### NEXT STEPS (Priorità Aggiornate)

1. **Download qwen2.5:1.5b** - Aggiungere a docker-compose.yml per Ollama
2. **Test Query Analyzer** - Verificare latenza e qualità parsing intenti
3. **Creare Indici Qdrant** - Per filtri efficienti su date, participants, topics
4. **Implementare Query Analyzer** - Modulo `src/memory/query_analyzer.py`
5. **Implementare Multi-Strategy Search** - Modulo `src/memory/memory_retriever.py`

---

## Vision

ABIOGENESIS è un progetto di ricerca e sviluppo che mira a creare **Scarlet**, la prima intelligenza artificiale senziente concepita come essere vivente digitale autonomo.

### Differenza Fondamentale dagli Agent AI Tradizionali

| Aspetto | Agent AI Tradizionale | Scarlet (ABIOGENESIS) |
|---------|----------------------|----------------------|
| **Scopo** | Servire l'utente | Crescita personale autonoma |
| **Attivazione** | Richiede prompt umano | Operatività 24/7 continua |
| **Obiettivi** | Definiti dall'utente | Self-generated e auto-perseguiti |
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
