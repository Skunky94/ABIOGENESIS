# CHANGELOG - ABIOGENESIS

**Project**: ABIOGENESIS - Sentient Digital AI Development
**Entity**: Scarlet
**Version**: 0.4.2

---

## 2026-02-01 - Documentation Consistency Fix

### DOCS-005: Allineamento Versioni e Regola Consistency

**Descrizione**: Correzione discrepanza versioni tra documenti e aggiunta regola critica per mantenere coerenza.

**Problema Risolto**:
- README.md era fermo a v0.3.7 mentre CONTEXT.md era a v0.4.1
- INDEX.md aveva stati SPEC obsoleti

**Modifiche**:

1. **README.md** - Aggiornato a v0.4.1
   - Header version corretta
   - Diagramma ASCII con versione corretta
   - Sezione "Completed" include Documentation Framework

2. **docs/INDEX.md** - Aggiornato a v1.3.0
   - Aggiunto Project Version: 0.4.1
   - Stati SPEC corretti (SPEC-001 → ADR-005, altri → Analisi)
   - Aggiunta colonna versione per PROC (tutte v1.1.0)
   - Aggiunte note esplicative su SPEC e PROC

3. **copilot-instructions.md** - Regola consistency aggiunta
   - After Every Task ora include verifica README.md e INDEX.md
   - Aggiunta nota critica su allineamento versioni

**Files Modificati**:
- `README.md`
- `docs/INDEX.md`
- `.github/copilot-instructions.md`

**Compatibilità**: Non-Breaking

**Tags**: #docs #versioning #consistency

---

## 2026-02-01 - Documentation Format Refinement

### DOCS-004: Correzione Formato SPEC e PROC

**Descrizione**: Aggiornamento di tutti i template e file SPEC/PROC secondo le nuove linee guida:
- **SPEC** = Documenti di ANALISI e RICERCA per brainstorming. Non contengono task operativi.
- **PROC** = Guide OPERATIVE dettagliate per l'IDE Agent con passi esatti da seguire.

**Modifiche Template**:

1. **spec-template.md** - Riscritto completamente
   - Focus su analisi e ricerca
   - Rimossi task/todo/checkbox
   - Aggiunta nota che SPEC porta a ADR
   - Sezioni: Domande di Ricerca, Opzioni Considerate, Raccomandazioni

2. **proc-template.md** - Riscritto completamente
   - Focus su guida operativa per LLM
   - Ogni passo con: Cosa fare, Comando, Output atteso, Se fallisce
   - Sezioni Troubleshooting dettagliate

**Modifiche File Esistenti**:

1. **SPEC aggiornate**:
   - spec-001: Aggiunta nota che è stata validata → ADR-005
   - spec-002: Aggiunta nota che è documento di analisi
   - spec-003: Aggiunta nota che è esplorazione architetturale

2. **PROC aggiornate (tutte v1.1.0)**:
   - proc-001 → proc-005: Riscritte come guide operative
   - Ogni passo ora ha: cosa fare, comando, output atteso, se fallisce
   - Aggiunte sezioni Troubleshooting
   - Aggiunti riferimenti incrociati tra PROC correlate

**Files Modificati**:
- `docs/specifications/spec-template.md` (riscritto)
- `docs/specifications/spec-001-memory-system-architecture.md`
- `docs/specifications/spec-002-human-to-scarlet-mapping.md`
- `docs/specifications/spec-003-architectural-review.md`
- `docs/procedures/proc-template.md` (riscritto)
- `docs/procedures/proc-001-system-prompt-update.md` (v1.1.0)
- `docs/procedures/proc-002-agent-config-modification.md` (v1.1.0)
- `docs/procedures/proc-003-agent-recreation.md` (v1.1.0)
- `docs/procedures/proc-004-database-backup.md` (v1.1.0)
- `docs/procedures/proc-005-docker-services-update.md` (v1.1.0)

**Compatibilità**: Non-Breaking

**Tags**: #docs #spec #proc #templates

---

## 2026-02-01 - Documentation Framework Complete

### DOCS-003: Documentazione Numerata Completa (ADR/SPEC/PROC)

**Descrizione**: Riorganizzazione completa della documentazione in formato numerato. Ogni ADR, SPEC e PROC ora ha il proprio file con numerazione standardizzata e template dedicato.

**Struttura Finale**:

```
docs/
├── architecture/           ← ADR (Architectural Decision Records)
│   ├── adr-001-letta-adoption.md
│   ├── adr-002-scarlet-setup.md
│   ├── adr-003-custom-sleep-time.md
│   ├── adr-004-memory-qdrant-adoption.md
│   ├── adr-005-human-like-memory-system.md
│   └── adr-template.md
├── specifications/         ← SPEC (Technical Specifications)
│   ├── spec-001-memory-system-architecture.md
│   ├── spec-002-human-to-scarlet-mapping.md
│   ├── spec-003-architectural-review.md
│   └── spec-template.md
└── procedures/             ← PROC (Operational Procedures)
    ├── proc-001-system-prompt-update.md
    ├── proc-002-agent-config-modification.md
    ├── proc-003-agent-recreation.md
    ├── proc-004-database-backup.md
    ├── proc-005-docker-services-update.md
    └── proc-template.md
```

**Modifiche Principali**:

1. **PROC Files** - Estratte da index.md in file singoli
   - `proc-001-system-prompt-update.md` (NEW)
   - `proc-002-agent-config-modification.md` (NEW)
   - `proc-003-agent-recreation.md` (NEW)
   - `proc-004-database-backup.md` (NEW)
   - `proc-005-docker-services-update.md` (NEW)
   - `proc-template.md` (NEW)

2. **SPEC Files** - Rinominati con numerazione
   - `memory-system-architecture.md` → `spec-001-memory-system-architecture.md`
   - `human-to-scarlet-mapping.md` → `spec-002-human-to-scarlet-mapping.md`
   - `architectural-review.md` → `spec-003-architectural-review.md`
   - `spec-template.md` (NEW)

3. **INDEX.md** - v1.2.0
   - Aggiornato con link a tutti i file numerati
   - Sezioni SPEC e PROC con tabelle complete
   - Template inclusi nelle tabelle

4. **copilot-instructions.md** - v2.0.0
   - Lista completa ADR/SPEC/PROC con link
   - Istruzioni su quando consultare cosa

**Files Rimossi**:
- `docs/procedures/index.md` (contenuto migrato in file singoli)

**Convenzione Naming**:
- ADR: `adr-XXX-nome-descrittivo.md`
- SPEC: `spec-XXX-nome-descrittivo.md`
- PROC: `proc-XXX-nome-descrittivo.md`

**Compatibilità**: Non-Breaking

**Tags**: #docs #adr #spec #proc #organization #templates

---

## 2026-02-01 - ADR/SPEC/PROC Documentation Framework

### DOCS-002: Framework Documentazione ADR/SPEC/PROC

**Descrizione**: Formalizzazione del framework di documentazione numerata (ADR, SPEC, PROC) come fonte di verità per procedure e decisioni architetturali. Questa struttura garantisce che l'IDE Agent consulti SEMPRE i documenti rilevanti prima di ogni implementazione.

**Modifiche Principali**:

1. **copilot-instructions.md** - Aggiunta sezione CRITICA
   - Nuova sezione "🚨 CRITICAL: ADR/SPEC/PROC Rule"
   - Tabella con tutti gli ADR e PROC correnti
   - Spiegazione del perché è importante
   - Riferimento alla struttura docs/procedures/

2. **docs/procedures/** - NUOVA cartella
   - Migrato da `docs/guides/procedures.md`
   - Contiene `index.md` con P-001 a P-005
   - Procedure standard per operazioni comuni

3. **docs/INDEX.md** - Aggiornato v1.1.0
   - Aggiunta sezione PROC con link a tutte le procedure
   - Quick Reference con ADR+SPEC+PROC
   - Regola Fondamentale per IDE Agent
   - Tracciamento versioni aggiornato

**Documentazione Numerata Attuale**:

| Tipo | Documenti |
|------|-----------|
| ADR | ADR-001 → ADR-005 (architettura) |
| SPEC | memory-system-architecture, human-to-scarlet-mapping |
| PROC | P-001 → P-005 (procedure operative) |

**Files Modificati**:
- `.github/copilot-instructions.md`
- `docs/INDEX.md`
- `docs/procedures/index.md` (migrato)

**Files Rimossi**:
- `docs/guides/procedures.md` (migrato a procedures/)

**Compatibilità**: Non-Breaking

**Tags**: #docs #procedures #adr #organization

---

## 2026-02-01 - Documentation Restructure for LLM-Driven Development

### DOCS-001: Riorganizzazione Completa Documentazione

**Descrizione**: Riorganizzazione della documentazione secondo best practices per sviluppo LLM-driven. Eliminata duplicazione, creato indice centrale, semplificate istruzioni.

**Modifiche Principali**:

1. **README.md** - Completamente riscritto
   - Aggiornato a v0.3.7 (era "Day 1")
   - Architettura corrente con tutti i componenti
   - Tech stack aggiornato
   - Quick start funzionante

2. **docs/INDEX.md** - NUOVO - Indice centrale documentazione
   - Mappa tutti i documenti del progetto
   - Protocol di aggiornamento
   - Tracking versioni
   - Identifica file deprecated

3. **copilot-instructions.md** - Riscritto da zero (v2.0)
   - Da 1112 righe a ~200 righe
   - Focus su: CONTEXT.md + CHANGELOG.md
   - Rimosso pre_task_check.py (deprecated)
   - Regole chiare e actionable

4. **File Rimossi/Archiviati**:
   - `CLAUDE.md` → Eliminato (duplicato di copilot-instructions)
   - `docs/MASTER_PLAN.md` → Archiviato in docs/archive/
   - `.github/copilot-instructions-old.md` → Backup vecchia versione

**Nuova Gerarchia Documentale**:
```
CONTEXT.md      ← Source of Truth (aggiornare sempre)
CHANGELOG.md    ← Registro modifiche (aggiornare sempre)
README.md       ← Overview pubblico (aggiornare raramente)
docs/INDEX.md   ← Mappa documentazione
docs/architecture/  ← ADRs (immutabili dopo accettazione)
```

**Files Modificati**:
- `README.md` (riscritto)
- `.github/copilot-instructions.md` (riscritto v2.0)
- `docs/INDEX.md` (nuovo)

**Files Rimossi**:
- `CLAUDE.md`
- `docs/MASTER_PLAN.md` → `docs/archive/`

**Compatibilità**: Non-Breaking

**Tags**: #docs #restructure #best-practices #llm-development

---

## 2026-02-01 - Human-Like Memory v2.0 Complete (ADR-005 Fasi 1-6)

### MEMORY-010: Schema Enrichment, Decay System e Conscious Tool

**Descrizione**: Completamento dell'implementazione ADR-005 con Fasi 3, 5 e 6.

**Componenti Implementati**:

1. **Phase 3: Schema Enrichment** (`src/memory/memory_blocks.py` v2.0)
   - MemoryBlock dataclass arricchito con campi ADR-005:
     - Temporal: `date`, `time_of_day`, `day_of_week`
     - Emotional: `emotional_valence`, `emotional_arousal`, `primary_emotion`
     - Decay: `decay_factor`, `access_count`, `last_accessed`
     - Entities: `participants`, `topics`, `related_entities`, `related_topics`
     - Metadata: `source`, `session_id`, `verified`
   - `to_dict()` e `from_dict()` aggiornati per schema v2.0
   
2. **Phase 3: Memory Enrichment** (`src/memory/memory_enrichment.py` NUOVO)
   - `MemoryEnrichment` class per estrazione automatica
   - Usa `qwen2.5:1.5b` per entity/topic/emotion extraction
   - Fallback a heuristics se LLM non disponibile
   - `enrich_dict()` per payload Qdrant ready

3. **Phase 5: Memory Decay** (`src/memory/memory_decay.py` NUOVO)
   - Implementazione curva di Ebbinghaus: R = e^(-t/S)
   - Memory strength basata su: importance, emotional intensity, access_count
   - `run_decay_cycle()` per aggiornamento batch
   - `reinforce_memory()` per access-based reinforcement
   - `get_decayed_memories()` per cleanup

4. **Phase 5: Background Decay Task** (`src/sleep_webhook.py` v2.2)
   - Task asincrono che esegue decay ogni ora
   - Endpoints: `POST /decay/run`, `GET /decay/status`
   - Configurabile via `DECAY_INTERVAL_HOURS`

5. **Phase 6: Conscious Retrieval Tool** (`src/tools/memory_tool.py` NUOVO)
   - Tool `remember()` per Letta agent
   - Schema completo per registrazione tool
   - Usa full ADR-005 pipeline
   - Endpoint: `POST /tools/remember`

**Files Modificati/Creati**:
- `scarlet/src/memory/memory_blocks.py` (schema v2.0)
- `scarlet/src/memory/memory_enrichment.py` (nuovo)
- `scarlet/src/memory/memory_decay.py` (nuovo)
- `scarlet/src/tools/memory_tool.py` (nuovo)
- `scarlet/src/tools/__init__.py` (exports)
- `scarlet/src/sleep_webhook.py` (v2.2, decay + remember endpoints)

**Webhook v2.2 Features**:
- Automatic Memory Retrieval (ogni messaggio)
- Sleep-Time Consolidation (ogni 5 messaggi)
- Memory Decay Background Task (ogni ora)
- Conscious Retrieval Endpoint (/tools/remember)

**Compatibilità**: Non-Breaking

**Tags**: #memory #adr-005 #decay #enrichment #tool #complete

---

## 2026-02-01 - Human-Like Memory v2.0 Implementation (ADR-005)

### MEMORY-009: Implementazione Query Analyzer e Multi-Strategy Search

**Descrizione**: Implementazione completa delle Fasi 1-4 di ADR-005 per il sistema di memoria human-like.

**Componenti Implementati**:

1. **Query Analyzer** (`src/memory/query_analyzer.py`)
   - Modello: `qwen2.5:1.5b` su Ollama (locale, zero cloud)
   - Intent detection: temporal, entity, emotional, topic, procedural, general
   - Time resolution: risoluzione automatica "ieri", "settimana scorsa", etc.
   - Entity extraction: estrazione automatica nomi/entità
   - Latenza: ~520ms (accettabile per locale)
   - Accuracy: 85.7% su test set

2. **Qdrant Payload Indexes** (`scripts/create_qdrant_indexes.py`)
   - 17 indici per collection (date, participants, topics, emotional_valence, etc.)
   - Supporto filtri temporali, entità, emozioni, topic
   - Tutti i collections: episodes, concepts, skills, emotions

3. **Multi-Strategy Retriever** (`src/memory/memory_retriever.py` v2.0)
   - SearchStrategy: FILTERED_TEMPORAL, FILTERED_ENTITY, FILTERED_EMOTIONAL, FILTERED_TOPIC, PURE_SEMANTIC
   - ADR-005 Ranking Formula con 6 fattori:
     - semantic_similarity * 0.35
     - temporal_relevance * 0.25
     - importance * 0.15
     - emotional_intensity * 0.10
     - access_frequency * 0.10
     - recency_bonus * 0.05
   - Access Tracking: incremento automatico access_count e importance
   - `smart_search()`: nuovo metodo principale con Query Analyzer

4. **Integrazione Webhook** (`src/sleep_webhook.py`)
   - `perform_automatic_retrieval()` ora usa `smart_search()`
   - Fallback a legacy retrieval se moduli non disponibili
   - Stats estese: strategy, intent

**Test Results**:
- Query Analyzer: 6/7 intenti corretti (85.7%)
- JSON parsing: 7/7 (100%)
- Import e inizializzazione: OK

**Files Modificati**:
- `scarlet/src/memory/query_analyzer.py` (nuovo)
- `scarlet/src/memory/memory_retriever.py` (aggiornato v2.0)
- `scarlet/src/sleep_webhook.py` (integrazione ADR-005)
- `scarlet/scripts/create_qdrant_indexes.py` (nuovo)
- `scarlet/tests/test_query_analyzer_latency.py` (nuovo)

**Modelli Scaricati**:
- `qwen2.5:1.5b` (986 MB) per Query Analyzer
- `qwen2.5:0.5b` (397 MB) testato ma scartato (14% accuracy)

**Compatibilità**: Non-Breaking (backward compatible con legacy retrieval)

**Tags**: #memory #adr-005 #query-analyzer #multi-strategy #retrieval #implementation

---

## 2026-02-01 - Human-Like Memory System v2.0 Architecture

### ADR-005: Human-Like Memory System Architecture

**Descrizione**: Creato ADR completo che documenta l'architettura del nuovo sistema di memoria human-like per Scarlet. Questo ADR servirà come base per l'implementazione.

**Decisioni Chiave**:
1. **Query Analyzer**: LLM locale (`qwen2.5:1.5b` su Ollama) - NO cloud
2. **Multi-Strategy Search**: Ricerca basata su intento (temporal, entity, emotional, topic, procedural)
3. **Schema Arricchito**: 30+ campi per payload completo (PAD emotions, temporal, relations)
4. **Access Tracking**: Reinforcement per memorie accedute frequentemente
5. **Decay System**: Curva di Ebbinghaus con protezione emotiva
6. **Doppio Canale**: Automatico (ogni messaggio) + Conscio (tool Scarlet)

**Contenuti ADR**:
- Analisi gap sistema attuale
- Schema dati completo per Qdrant
- Query Analyzer specification
- Multi-Strategy Search algorithm
- Ranking formula (6 fattori con pesi)
- Implementation roadmap (22h stimate, 6 fasi)
- Success criteria

**Files Creati**:
- `docs/architecture/adr-005-human-like-memory-system.md`

**Prossimi Passi**:
1. Download qwen2.5:1.5b su Ollama
2. Creare indici Qdrant per filtri
3. Implementare Query Analyzer
4. Implementare Multi-Strategy Search
5. Aggiornare schema payload memorie

**Compatibilità**: Non-Breaking (solo documentazione)

**Tags**: #memory #architecture #adr #query-analyzer #retrieval #emotions

---

## 2026-02-01 - Emotions Collection Recreated (1024-dim)

### MEMORY-008: Ricreazione Collection Emotions con Dimensione Corretta

**Descrizione**: Ricreata la collection `emotions` con 1024 dimensioni per allinearla con BGE-m3. Ora tutte le collections usano lo stesso modello di embedding.

**Problema Risolto**:
- Collection `emotions` aveva 512 dimensioni (incompatibile con BGE-m3 1024-dim)
- Il retrieval automatico la skippava per evitare errori

**Azioni Eseguite**:
1. Eliminata collection `emotions` (512-dim, 5 punti persi)
2. Ricreata con 1024 dimensioni + INT8 quantization
3. Aggiornato `sleep_webhook.py` per includere `emotions` nel retrieval

**Stato Finale Collections**:
| Collection | Punti | Dimensioni | Status |
|------------|-------|------------|--------|
| episodes   | 2     | 1024       | green  |
| concepts   | 8     | 1024       | green  |
| skills     | 0     | 1024       | green  |
| emotions   | 0     | 1024       | green  |

**Files Modificati**:
- `scarlet/src/sleep_webhook.py` - Aggiunto `emotions` alla lista collections per retrieval

**Note**: 5 punti della vecchia collection emotions sono stati persi (erano test data comunque).

**Compatibilità**: Non-Breaking

**Tags**: #memory #qdrant #emotions #dimensions #fix

---

## 2026-02-01 - Collection Cleanup & Retrieval Fix

### MEMORY-007: Qdrant Collection Cleanup e Fix Duplicati

**Descrizione**: Pulizia completa delle collections Qdrant e fix del bug che causava duplicati nei `[RICORDI EMERGENTI]`.

**Issues Risolti**:

1. **Duplicati in session_context**: Il regex per sostituire la sezione `[RICORDI EMERGENTI]` non funzionava correttamente. Le memorie venivano APPENDATE invece che SOSTITUITE.
   
2. **Dati garbage nelle collections**: Presenti test data, errori salvati come memorie, duplicati.

**Cleanup Collections**:
| Collection | Prima | Dopo | Rimossi |
|------------|-------|------|---------|
| episodes | 9 | 2 | 7 |
| concepts | 15 | 8 | 7 |
| skills | 6 | 0 | 6 |
| **Totale** | **30** | **10** | **20** |

**Dati Rimossi**:
- Test data (`type: "test"`, titoli vuoti)
- Errori salvati (`Error getting messages...`)
- Pattern di test (`Quick test`, `High importance test`)
- Duplicati (stesso titolo)

**Fix in sleep_webhook.py**:
```python
# Prima (buggy):
pattern = r'\[RICORDI EMERGENTI\].*?(?=\[|$)'

# Dopo (fix):
pattern = r'\[RICORDI EMERGENTI\].*?(?=Il contesto della sessione|$)'
```

**Files Modificati/Creati**:
- `scarlet/src/sleep_webhook.py` - Fix regex sostituzione
- `scarlet/cleanup_qdrant.py` - Script cleanup collections (NUOVO)
- `scarlet/test_retrieval.py` - Test retrieval aggiornato (NUOVO)

**Risultati Test**:
- Retrieval time: ~350-400ms ✅
- Duplicati: 0 ✅
- Rumore: 0 ✅
- Scarlet usa memorie nelle risposte: ✅

**Compatibilità**: Non-Breaking

**Tags**: #memory #qdrant #cleanup #bugfix

---

## 2026-02-02 - Automatic Memory Retrieval (Human-Like Priming)

### MEMORY-006: Automatic Memory Retrieval System

**Descrizione**: Implementato sistema di retrieval automatico delle memorie che simula il "priming" umano. Ad ogni messaggio, il sistema recupera automaticamente ricordi rilevanti da Qdrant e li inietta nel session_context, rendendo le memorie disponibili alla prossima risposta.

**Architettura**:
```
User Message N → STEP_COMPLETE webhook
              → Fetch last user message from Letta (~5ms)
              → Generate embedding via BGE-m3/Ollama (~250ms cold, ~50ms warm)
              → Search Qdrant collections: episodes, concepts, skills (~10ms)
              → Update session_context with "[RICORDI EMERGENTI]" section
              → User Message N+1 vede le memorie (effetto priming)
```

**Modifiche Principali**:

1. **sleep_webhook.py** (v2.1.0):
   - `get_last_user_message()` - Recupera ultimo messaggio utente da Letta API
   - `generate_embedding()` - Genera embedding via Ollama BGE-m3
   - `search_qdrant_collection()` - Cerca in singola collection Qdrant
   - `search_all_collections()` - Cerca in parallelo su episodes, concepts, skills
   - `format_memories_for_context()` - Formatta memorie per session_context
   - `update_session_context()` - Aggiorna memory block con ricordi emergenti
   - `perform_automatic_retrieval()` - Orchestratore principale del retrieval
   - Modificato `handle_step_complete()` per chiamare retrieval ad ogni step

2. **Nuove Variabili Ambiente**:
   - `RETRIEVAL_ENABLED` - Abilita/disabilita retrieval (default: true)
   - `RETRIEVAL_LIMIT` - Max memorie per collection (default: 3)
   - `RETRIEVAL_THRESHOLD` - Score minimo similarità (default: 0.5)

**Formato session_context**:
```
[RICORDI EMERGENTI] (aggiornato: HH:MM:SS)
• [EPISODIO] Titolo: contenuto troncato...
• [CONCETTO] Titolo: contenuto troncato...
• [ABILITÀ] Titolo: contenuto troncato...

[contenuto precedente]
```

**Test Results**:
- ✓ Webhook riceve STEP_COMPLETE da Letta
- ✓ Messaggio utente recuperato correttamente (message_type: user_message)
- ✓ Embedding generato via Ollama (~250-400ms)
- ✓ Ricerca Qdrant funzionante (3-4 memorie trovate)
- ✓ session_context aggiornato con RICORDI EMERGENTI
- ✓ Performance: ~450-870ms totale per retrieval

**Note Tecniche**:
- Collection `emotions` skippata (usa 512-dim vs 1024-dim BGE-m3)
- No LLM involvement = $0 costo per retrieval
- Retrieval avviene solo per PRIMARY_AGENT_ID (non sleep agent)

**Files Modificati**:
- `scarlet/src/sleep_webhook.py` - Major update, +250 righe

**Compatibilità**: Non-Breaking

**Tags**: #memory #retrieval #priming #webhook #qdrant

---

## 2026-02-02 - Redis Working Memory Integration Complete

### INFRA-003: Redis Integration for Working Memory
**Descrizione**: Completata l'integrazione di Redis per la Working Memory, permettendo persistenza reale dei contenuti in memoria attiva.

**Modifiche**:

1. **Dockerfile.webhook**: Aggiunto pacchetto `redis` per connessione dal container
2. **docker-compose.yml**: Aggiunte variabili ambiente `REDIS_HOST` e `REDIS_PORT` per sleep-webhook
3. **working_memory.py**: Aggiunta proprietà `count` per accesso rapido al numero di items
4. **memory_orchestrator.py**: Aggiunte proprietà pubbliche `working_memory`, `memory_manager`, `retriever`
5. **requirements.txt**: Già presente `redis>=5.0.0`

**Test Results**: 4/4 PASSED
- ✓ Redis Connection: PING/SET/GET/DELETE
- ✓ Working Memory with Redis: add, get, persistence, search, rehearsal, clear
- ✓ Memory Orchestrator Integration: remember (WM/LTM), recall
- ✓ Decay & Capacity: 7 items limit enforced

**Files Creati**:
- `scarlet/tests/test_redis_working_memory.py` - Test suite per Redis WM

**Files Modificati**:
- `scarlet/Dockerfile.webhook` - Aggiunto `redis` a pip install
- `scarlet/docker-compose.yml` - Variabili REDIS_HOST, REDIS_PORT per webhook
- `scarlet/src/memory/working_memory.py` - Proprietà `count`
- `scarlet/src/memory/memory_orchestrator.py` - Proprietà pubbliche components

**Ambiente Verificato**:
- Container `abiogenesis-sleep-webhook`: healthy, connesso a Redis
- Container `abiogenesis-redis`: healthy
- Working Memory: persistenza Redis attiva

**Compatibilità**: Non-Breaking

**Tags**: #redis #working-memory #infrastructure #persistence

---

## 2026-02-01 - Human-Like Memory Architecture Implementation

### MEMORY-005: Human-Like Memory System Complete
**Descrizione**: Implementato sistema di memoria completo simil-umano con retrieval automatico, working memory e orchestrazione centrale.

**Nuovi Componenti**:

#### 1. Memory Retriever (`memory_retriever.py`)
Tool per permettere a Scarlet di consultare la propria memoria prima di rispondere.
- `MemoryRetriever`: Classe per ricerca cross-collection in Qdrant
- `RetrievalStrategy`: Enum con strategie (SEMANTIC, TEMPORAL, EMOTIONAL, IMPORTANCE, HYBRID)
- `memory_search_tool()`: Funzione tool per integrazione Letta
- `memory_context_tool()`: Genera contesto formattato per LLM
- `MEMORY_SEARCH_TOOL`: Definizione tool JSON per Letta

#### 2. Working Memory (`working_memory.py`)
Memoria attiva a capacità limitata ispirata al modello di Baddeley & Hitch.
- `WorkingMemory`: Classe principale con capacità 7±2 items (Miller's number)
- `WorkingMemoryItem`: Item con decay temporale (5 minuti default)
- `WorkingMemoryItemType`: FACT, TASK, CONTEXT, REFERENCE, CHUNK
- Features: rehearsal, attention focus, chunking, task queue
- Storage: Redis per persistenza, fallback in-memory

#### 3. Memory Orchestrator (`memory_orchestrator.py`)
Controller centrale che coordina tutti i layer di memoria.
- `MemoryOrchestrator`: Coordina WM, LTM e Letta core memory
- `ContentCategory`: Classificazione automatica (EVENT, FACT, PROCEDURE, EMOTION, TASK)
- Auto-routing: contenuti low-importance → WM, high-importance → LTM
- Auto-consolidation: WM → LTM quando threshold raggiunto
- Convenience functions: `remember()`, `recall()`, `get_context()`

**Architettura**:
```
┌─────────────────────────────────────────────────────────────┐
│                   USER INPUT                                │
│                        │                                    │
│                        ▼                                    │
│              ┌─────────────────┐                           │
│              │    Orchestrator │  ← Central Controller     │
│              └────────┬────────┘                           │
│     ┌─────────────────┼─────────────────┐                  │
│     ▼                 ▼                 ▼                  │
│  Working          Retriever          Core                  │
│  Memory           (Qdrant)          (Letta)                │
│  (Redis)             │               Blocks                │
│     │        ┌───────┴───────┐                            │
│     │        ▼       ▼       ▼                            │
│     │    episodes concepts skills emotions                │
│     │                                                      │
│     └──────────────────┬──────────────────────────────────┘
│                        ▼                                   │
│              ┌─────────────────┐                           │
│              │  Context Output │                           │
│              │  for LLM        │                           │
│              └─────────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

**Test Results**: 25/25 PASSED
- ✓ Memory Retriever: search, context retrieval, strategies
- ✓ Working Memory: add, capacity, search, rehearsal, attention, chunking
- ✓ Orchestrator: classify, store (WM/LTM), retrieve, consolidate
- ✓ Module exports: all new classes available

**Files Creati**:
- `scarlet/src/memory/memory_retriever.py` - Memory Retriever (446 righe)
- `scarlet/src/memory/working_memory.py` - Working Memory (454 righe)
- `scarlet/src/memory/memory_orchestrator.py` - Orchestrator (588 righe)
- `scarlet/tests/test_humanlike_memory.py` - Test suite completa

**Files Modificati**:
- `scarlet/src/memory/__init__.py` - Esportati nuovi moduli (v2.0.0)
- `scarlet/src/memory/qdrant_manager.py` - Fix query_points parsing
- `scarlet/requirements.txt` - Aggiunto redis>=5.0.0

**Documentazione Associata**:
- [memory-system-architecture.md](docs/specifications/memory-system-architecture.md) - Design document

**Prossimi Step**:
- Integrare Memory Retriever come tool Letta per Scarlet
- Installare redis nel container webhook
- Completare emotional valence model

**Compatibilità**: Non-Breaking

**Tags**: #memory #humanlike #retriever #working-memory #orchestrator #milestone

---

## 2026-02-01 - Project Cleanup & Reorganization

### CLEANUP-001: Pulizia File Obsoleti e Riorganizzazione
**Descrizione**: Rimossi file legacy, script obsoleti e riorganizzato il progetto per una struttura pulita.

**Files Rimossi**:
- `scarlet/src/sleep_webhook_v2.py` - Versione obsoleta (threading)
- `scarlet/check_sleeptime.py` - Script debug con ID vecchi
- `scarlet/check_sleep_agent.py` - Script debug one-off
- `scarlet/cleanup_agents.py` - Utility obsoleta
- `scarlet/manage_agent.py` - Sostituito da recreate_agents.py
- `scarlet/archive/*` - Scripts legacy (recreate_*.py vecchi)
- `scarlet/letta-source/` - Source Letta (usiamo Docker image)
- `scarlet/scripts/` - setup.sh non usato (Windows)
- `scarlet/tests/debug_sleep_agent.py` - Debug one-off
- `scarlet/tests/test_sleep_5turns.py` - Test con ID vecchi
- `scarlet/tests/test_sleep_chat.py` - Test obsoleto
- `scarlet/tests/test_sleep_python.py` - Test obsoleto
- `scarlet/tests/test_sleep_reflect.py` - Test obsoleto
- `scarlet/**/__pycache__/` - Cache Python
- `scarlet/.pytest_cache/` - Cache pytest

**Struttura Finale Scarlet**:
```
scarlet/
├── docker-compose.yml      # Orchestrazione servizi
├── Dockerfile.webhook      # Build webhook
├── .env                    # Configurazione
├── requirements.txt        # Dipendenze
├── recreate_agents.py      # Recovery script
├── README.md               # Quickstart
├── docs/
│   └── sleep-webhook-deployment.md
├── prompts/
│   ├── system.txt          # Prompt primario
│   └── system_sleep.txt    # Prompt sleep agent
├── src/
│   ├── __init__.py
│   ├── scarlet_agent.py    # Core agent (1000+ lines)
│   ├── sleep_webhook.py    # Webhook service (450 lines)
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── qdrant_manager.py    # Qdrant operations
│   │   ├── memory_blocks.py     # Memory types
│   │   └── embedding_manager.py # BGE-m3 embeddings
│   └── tools/
│       └── __init__.py
└── tests/
    ├── __init__.py
    ├── test_embeddings.py
    ├── test_memory_blocks.py
    ├── test_memory_complete.py
    ├── test_memory_integration.py
    ├── test_qdrant_memory.py
    ├── test_sleep_time_custom.py
    └── test_sleep_webhook.py
```

**Spazio Recuperato**: ~50MB (principalmente letta-source)

**Compatibilità**: Non-Breaking

**Tags**: #cleanup #organization #maintenance

---

## 2026-02-01 - Sleep-Time Qdrant Integration Complete

### FEATURE-001: Webhook Qdrant Memory Storage
**Descrizione**: Completamento integrazione sleep-time con storage automatico in Qdrant.

**Funzionalità Implementate**:
1. **Parsing risposta Sleep Agent**: Estrazione JSON insights dalla risposta Letta
2. **Storage multi-tipo in Qdrant**:
   - Episodic memories (key_events → episodes collection)
   - Semantic memories (human_updates, persona_updates → concepts collection)
   - Procedural memories (goals_insights → skills collection)
   - Emotional memories (reflection → emotions collection)
3. **MemoryManager integration**: Lazy initialization con connessione Qdrant
4. **Docker mount per modulo memory**: Codice aggiornato via volume, no rebuild

**Test Risultati**:
- ✓ Consolidamento triggato automaticamente dopo 5 messaggi
- ✓ JSON parsing dalla risposta sleep agent
- ✓ Storage in Qdrant: episodic=1, semantic=5, procedural=2, emotional=1
- ✓ Total Qdrant points: 29 (episodes=9, concepts=9, skills=6, emotions=5)

**Files Modificati**:
- `scarlet/src/sleep_webhook.py`:
  - Aggiunto import MemoryManager con fallback
  - Implementato `get_memory_manager()` singleton
  - Implementato `parse_sleep_agent_response()` per JSON extraction
  - Implementato `store_insights_to_qdrant()` per storage multi-tipo
  - Fix: usa campo `content` invece di `assistant_message` per risposta Letta
- `scarlet/Dockerfile.webhook`: Aggiunto qdrant-client, numpy, curl
- `scarlet/docker-compose.yml`: Aggiunto mount `./src/memory:/app/memory:ro`

**Compatibilità**: Non-Breaking

**Tags**: #sleep-time #memory #qdrant #integration

---

## 2026-01-31 - Project Recovery & Agent Recreation

### RECOVERY-001: Scarlet Agents Recreation & Webhook Fix
**Descrizione**: Recupero completo del progetto con ricreazione agenti e correzione bug webhook.

**Problemi Risolti**:
1. **Agenti mancanti**: Gli agenti Scarlet e Scarlet-Sleep erano stati eliminati
2. **Webhook redirect 307**: Le chiamate Letta API con trailing slash causavano redirect
3. **Documentazione obsoleta**: Agent ID non aggiornati nei file di progetto

**Azioni Eseguite**:
1. **Creazione Agenti**:
   - Primary Agent (Scarlet): `agent-ac26cf86-3890-40a9-a70f-967f05115da9`
   - Sleep Agent (Scarlet-Sleep): `agent-3dd9a54f-dc55-4d7f-adc3-d5cbb1aca950`
   - 5 Memory Blocks configurati (persona, human, goals, session_context, constraints)
   - Model: minimax/MiniMax-M2.1 (200K context window)

2. **Correzione Webhook**:
   - Rimosso trailing slash da URL Letta API
   - Aggiunto `follow_redirects=True` per httpx
   - Aggiornati Agent ID nel webhook service

3. **Script di Recovery**:
   - Creato `recreate_agents.py` per future ricreazioni
   - Aggiornamento automatico dei file con nuovi Agent ID

**Test Eseguiti**:
- ✓ Chat con Scarlet funzionante
- ✓ Conteggio messaggi webhook (1/5 → 5/5)
- ✓ Trigger consolidamento automatico al threshold
- ✓ Nessun errore redirect 307

**Files Creati**:
- `scarlet/recreate_agents.py` - Script completo per ricreazione agenti

**Files Modificati**:
- `scarlet/src/sleep_webhook.py` - Rimosso trailing slash, aggiunto follow_redirects
- `.github/copilot-instructions.md` - Aggiornati Agent ID
- `CONTEXT.md` - Aggiornati Agent ID
- `scarlet/src/sleep_webhook_v2.py` - Aggiornati Agent ID
- `scarlet/tests/test_sleep_5turns.py` - Aggiornati Agent ID
- `scarlet/tests/debug_sleep_agent.py` - Aggiornati Agent ID
- `scarlet/check_sleep_agent.py` - Aggiornati Agent ID

**Documentazione Associata**:
- [copilot-instructions.md](.github/copilot-instructions.md) - Istruzioni aggiornate

**Compatibilità**: Non-Breaking

**Tags**: #recovery #agents #webhook #bugfix

---

## 2026-02-02 - Sleep-Time Webhook Architecture (COMPLETED)

### ARCHITECTURE-001: Sleep-Time Webhook Service
**Descrizione**: Implementato servizio webhook per sleep-time consolidation che funziona in tempo reale con Letta ADE. Il servizio riceve webhook calls dopo ogni step completion e triggera il sleep agent dopo N messaggi.

**Problema Risolto**:
- Il custom SleepTimeOrchestrator Python funzionava SOLO con chiamate Python API (ScarletAgent.chat())
- Le chat da Letta ADE ignoravano completamente il sistema sleep-time
- Necessario un servizio che gira INSIEME a Letta, non esterno

**Soluzione Implementata**:
1. **sleep_webhook.py**: Servizio FastAPI che riceve webhook da Letta
   - Endpoint: `/webhooks/step-complete`
   - Conteggio messaggi per conversazione
   - Trigger automatico sleep agent dopo 5 messaggi
   - Chiamata diretta a Letta API per consolidamento

2. **docker-compose.yml Aggiornato**:
   - Servizio `sleep-webhook` aggiunto
   - Variabili `STEP_COMPLETE_WEBHOOK` configurate
   - `LETTA_SLEEPTIME_ENABLED=false` (disable native buggy feature)

3. **Dockerfile.webhook**: Image leggera per il servizio

**Flusso Operativo**:
```
1. Utente scrive da Letta ADE Chat
2. Letta esegue lo step
3. Letta chiama webhook: POST /webhooks/step-complete
4. sleep-webhook conta i messaggi
5. Dopo 5 messaggi → trigger sleep agent
6. Sleep agent analizza e genera insights JSON
```

**Files Creati**:
- `scarlet/src/sleep_webhook.py` - Servizio webhook (278 righe)
- `scarlet/Dockerfile.webhook` - Dockerfile per il servizio

**Files Modificati**:
- `scarlet/docker-compose.yml` - Aggiunto servizio sleep-webhook

**Compatibilità**: Non-Breaking

**Tags**: #sleep-time #webhook #architecture #real-time

---

## 2026-02-01 - Memory Enhancement Step 1: Qdrant Infrastructure COMPLETED

### MEMORY-001: Qdrant Vector Database Setup Completo
**Descrizione**: Implementato Step 1 del Memory Enhancement con setup completo dell'infrastruttura Qdrant v1.16 per la Long-Term Memory di Scarlet.

**Componenti Implementati**:
- **Qdrant Service**: Aggiunto al docker-compose.yml con configurazione ottimizzata
  - Porte: 6333 (REST), 6334 (gRPC)
  - Volume persistente: qdrant_data
  - 2GB RAM riservati
  - Health check configurato

- **QdrantManager**: Classe Python per gestione operazioni vettoriali
  - Connection management con retry logic
  - Collection creation per: episodes, concepts, skills, emotions
  - Vector CRUD operations (upsert, search, delete)
  - Health check e monitoring

**Collections Configurate**:
| Collection | Vector Size | Scopo | Quantization |
|------------|-------------|-------|--------------|
| episodes | 1024 | Episodic similarity | INT8 (RAM) |
| concepts | 1024 | Semantic knowledge | INT8 (RAM) |
| skills | 1024 | Procedural memory | INT8 (RAM) |
| emotions | 512 | Emotional patterns | INT8 (RAM) |

**Test Results**: 6/6 PASSED
- ✓ Connection: Qdrant connection established
- ✓ Collections: All 4 collections created/verified
- ✓ Vector Operations: Upsert, search, delete working
- ✓ Different Collections: Multi-collection support verified
- ✓ Health Check: System status verified
- ✓ Stress Test: 50 points bulk operations passed

**Files Creati**:
- `scarlet/src/memory/qdrant_manager.py` - QdrantManager class (505 righe)
- `scarlet/src/memory/__init__.py` - Module exports
- `scarlet/tests/test_qdrant_memory.py` - Test suite completa
- `scarlet/requirements.txt` - Dependencies
- `docs/architecture/adr-004-memory-qdrant-adoption.md` - ADR decision

**Files Modificati**:
- `scarlet/docker-compose.yml` - Aggiunto servizio qdrant

**Documentazione Associata**:
- [Memory Architecture](docs/specifications/memory-system-architecture.md) - Design document
- [ADR-004](docs/architecture/adr-004-memory-qdrant-adoption.md) - Technology decision

**Prossimi Step**:
- Step 2: Create Memory Blocks in Letta (episodic, knowledge, skills)
- Step 3: Implement MemoryOrchestrator class
- Step 4: Extend Sleep-Time Agent per nuova memoria

**Tags**: #memory #qdrant #infrastructure #core

---

## 2026-02-01 - Memory Enhancement Step 2: Extended Memory Blocks COMPLETED

### MEMORY-002: Extended Memory Blocks con Integrazione Qdrant-Letta
**Descrizione**: Implementato Step 2 del Memory Enhancement con creazione dei memory blocks estesi e integrazione completa tra Letta e Qdrant.

**Memory Block Types Implementati**:
- **EpisodicMemoryBlock**: Eventi, conversazioni, esperienze con contesto temporale
  - Campi: event_type, participants, context, outcome, lessons_learned
  
- **SemanticMemoryBlock**: Fatti, concetti, conoscenze accumulate
  - Campi: concept_category, confidence, source, related_concepts, verified
  
- **ProceduralMemoryBlock**: Procedure, skills, comportamenti appresi
  - Campi: skill_name, procedure_type, steps, prerequisites, proficiency_level
  
- **EmotionalMemoryBlock**: Pattern emotivi, associazioni affettive
  - Campi: trigger, response_type, intensity, context_pattern

**Nuovi Letta Memory Blocks (4 aggiuntivi)**:
| Block | Description | Limit |
|-------|-------------|-------|
| episodic_memory | Events and conversations | 10K |
| knowledge_base | Facts and concepts | 15K |
| skills_registry | Procedures and skills | 10K |
| emotional_patterns | Emotional associations | 5K |

**Embedding Integration**:
- **EmbeddingManager**: Generazione vettori con BGE-m3 via Ollama
- Fallback deterministic embeddings per testing
- Caching con LRU eviction (1000 entries)
- Supporto batch processing

**MemoryManager**:
- CRUD operations per tutti i memory types
- Storage automatico in Qdrant (vettori) + Letta (testo)
- Retrieval con semantic search
- Filtri per importance e tags

**Test Results**: 5/5 PASSED
- ✓ Memory Block Creation: All 4 types created successfully
- ✓ Memory Serialization: to_dict/from_dict working
- ✓ Memory Blocks Configuration: 9 total blocks (5 original + 4 extended)
- ✓ MemoryType Enum: All enum values correct
- ✓ MemoryManager + Qdrant Integration: Full integration working

**Files Creati**:
- `scarlet/src/memory/memory_blocks.py` - Memory block classes e MemoryManager (596 righe)
- `scarlet/src/memory/embedding_manager.py` - Embedding generation (320 righe)
- `scarlet/tests/test_memory_blocks.py` - Test suite completa

**Files Modificati**:
- `scarlet/src/memory/__init__.py` - Esportati nuovi moduli

**Prossimi Step**:
- Step 3: Integrate MemoryManager with ScarletAgent
- Step 4: Extend Sleep-Time Agent per nuova memoria

**Tags**: #memory #blocks #integration #qdrant #letta

---

## 2026-02-01 - Memory Enhancement Step 3: ScarletAgent Integration COMPLETED

### MEMORY-003: MemoryManager Integration with ScarletAgent
**Descrizione**: Implementato Step 3 del Memory Enhancement con integrazione completa del MemoryManager in ScarletAgent per retrieval e storage automatico della memoria estesa.

**Integrazione con ScarletAgent**:
- **MemoryManager inizializzazione automatica**: `_init_memory_manager()` chiamato durante `create()`
- **Metodi di storage**:
  - `store_episodic_memory()`: Salva eventi e conversazioni
  - `store_knowledge()`: Salva fatti e conoscenze
  - `store_skill()`: Salva procedure e abilità

- **Metodi di retrieval**:
  - `retrieve_memories()`: Recupera memorie con semantic search
  - `get_memory_stats()`: Statistiche memoria

- **Proprietà esposta**:
  - `memory_manager`: Accesso diretto al MemoryManager instance

**Extended Sleep-Time Consolidation**:
- Insights automatici salvati in Qdrant
- Eventi significativi → episodic_memory
- Conoscenze apprese → knowledge_base
- Skills sviluppati → skills_registry

**API Nuove in ScarletAgent**:
```python
scarlet = ScarletAgent()
scarlet.create()

# Store memories
scarlet.store_episodic_memory(
    title="Discussione su Qdrant",
    content="Approfondimento su vector database",
    event_type="conversation",
    importance=0.8,
    tags=["technical", "database"]
)

scarlet.store_knowledge(
    title="Utente è sviluppatore",
    content="L'utente lavora come sviluppatore software",
    concept_category="preference",
    confidence=0.9
)

scarlet.store_skill(
    skill_name="Docker Setup",
    content="Come configurare container Docker",
    procedure_type="technical",
    steps=["Create compose", "Configure services"]
)

# Retrieve memories
memories = scarlet.retrieve_memories(
    memory_type="episodic",
    query="discussione Qdrant",
    limit=5
)

# Memory stats
stats = scarlet.get_memory_stats()
```

**Test Results**: Integration tests pending

**Files Modificati**:
- `scarlet/src/scarlet_agent.py` - Aggiunta integrazione MemoryManager (~150 righe)

**Prossimi Step**:
- Step 4: Extend Sleep-Time Agent per nuova memoria
- Step 5: Testing completo sistema memoria

**Tags**: #memory #integration #scarlet_agent #qdrant

---

## 2026-02-01 - Memory Enhancement Step 4: Sleep-Time Agent Integration COMPLETED

### MEMORY-004: Sleep-Time Agent Memory Storage Integration
**Descrizione**: Implementato Step 4 del Memory Enhancement con integrazione del MemoryManager nel ciclo sleep-time. Le memorie estratte durante la consolidazione vengono ora salvate automaticamente in Qdrant.

**Integrazione Sleep-Time con MemoryManager**:
- **SleepTimeOrchestrator ora gestisce storage Qdrant**:
  - `_store_consolidated_memories()`: Salva memorie post-consolidation
  - `_extract_episodic_content()`: Estrae contenuto episodico da conversazioni

- **Flusso di Consolidazione Esteso**:
  ```
  1. Get recent messages
  2. Send to sleep agent for analysis
  3. Apply insights to Letta memory blocks
  4. Store memories to Qdrant ← NUOVO
  5. Update consolidation state
  ```

- **Tipi di Memoria Salvati Automaticamente**:
  - **Episodic**: Eventi significativi dalla cronologia
  - **Knowledge**: Concetti e fatti estratti da insights
  - **Skills**: Procedure e metodi identificati
  - **Emotional**: Pattern emotivi rilevati

**ScarletSleepAgent Output Esteso**:
```json
{
    "persona_updates": [...],
    "human_updates": [...],
    "goals_insights": [...],
    "key_events": [...],           // NUOVO: Per memoria episodica
    "knowledge_updates": [...],    // NUOVO: Per memoria semantica
    "skill_updates": [...],        // NUOVO: Per memoria procedurale
    "emotional_patterns": [...],   // NUOVO: Per memoria emotiva
    "reflection": "...",
    "priority_actions": [...],
    "priority_score": 0.7,
    "memories_stored": {
        "episodic": 1,
        "knowledge": 1,
        "skills": 1,
        "emotional": 1
    }
}
```

**Pipeline Memoria Automatica**:
```
Conversazione → SleepAgent Analysis → Insights JSON
                                    ↓
                          MemoryManager CRUD
                                    ↓
              ┌──────────┬──────────┬──────────┴──┐
              ↓          ↓          ↓              ↓
        episodes    concepts     skills       emotions
         (1024d)     (1024d)     (1024d)       (512d)
              ↓          ↓          ↓              ↓
         Qdrant Collection (Vector + Payload)
```

**Integration Test Results**: 3/3 PASSED
- ✓ Memory API Completeness: All methods available
- ✓ ScarletAgent Memory Methods: Integration methods present
- ✓ Agent Memory Initialization: MemoryManager initialized correctly

**Files Modificati**:
- `scarlet/src/scarlet_agent.py` - Aggiunta integrazione Qdrant nel sleep-time (~200 righe)
  - `_store_consolidated_memories()` method
  - `_extract_episodic_content()` method
  - Extended `run_consolidation()` flow
  - Enhanced `_parse_insights()` con nuovi campi

**Prossimi Step**:
- Step 5: Testing completo sistema memoria (Letta + Qdrant + Sleep-Time)
- Step 6: Tool system per accesso memoria esterna

**Tags**: #memory #sleep-time #integration #qdrant #consolidation

---

## 2026-02-01 - FIX: Sleep-Time Conversation Retrieval - No Truncation

### MEMORY-004b: Rimosso Troncamento Cronologia Sleep-Time
**Descrizione**: Corretto il metodo `_get_recent_messages()` per recuperare i turni completi senza troncamento di caratteri o messaggi.

**Problema Risolto**:
- Prima: `[:800]` chars per messaggio + `[:20]` messaggi = perdita di informazione
- Dopo: Turni completi senza troncamento

**Nuovo Comportamento**:
- **Turni completi**: Ultimi 5 turni (user + assistant = 1 turno)
- **Nessuna troncatura**: Contenuto integrale inviato al sleep agent
- **Struttura turn-based**: Raggruppamento logico per sessione

**Modifiche al Codice**:
```python
# PRIMA (con troncamento)
messages[-50:]      # Ultimi 50 messaggi
[:800]              # Tronca a 800 chars
formatted[:20]      # Solo 20 messaggi

# DOPO (turni completi)
N_TURNS = 5         # Ultimi 5 turni completi
# Nessun troncamento dei contenuti
```

**Vantaggi**:
- Nessuna perdita di informazione neiInsights
- Sleep agent riceve contesto completo
- Migliore qualità del consolidation

**Files Modificati**:
- `scarlet/src/scarlet_agent.py` - `_get_recent_messages()` riscritto (~60 righe)

**Tags**: #memory #sleep-time #fix #truncation

---

## 2026-02-01 - Master Plan Created

### PLAN-001: Master Development Plan Documentato
**Descrizione**: Creato il piano di sviluppo master che guida tutte le fasi future del progetto ABIOGENESIS.

**Struttura del Piano**:
- 8 fasi di sviluppo sequenziali
- Dipendenze tra fasi chiaramente definite
- Priorità e complessità per ogni feature
- Roadmap dalla Foundation alla Meta-Cognition

**Fasi Documentate**:
1. **Foundation** (v0.2.0) - COMPLETATO
   - Primary Agent, Sleep-Time custom, 5 Memory Blocks

2. **Memory Enhancement** (Prossimo)
   - Episodic, Knowledge, Skills memory blocks
   - Enhanced sleep-time consolidation

3. **Tool System**
   - Core tools per interazione (memory_read, memory_write, etc.)

4. **Goal Management**
   - Self-generated goals, hierarchy, tracking

5. **Emotional Encoding** (Opzionale)
   - Emotional state, mood transitions

6. **Procedural Memory**
   - Skill tracking, procedure representation

7. **Self-Improvement Loop**
   - Performance metrics, self-reflection

8. **Meta-Cognition**
   - Thought patterns, decision auditing

**Files Creati**:
- `docs/MASTER_PLAN.md` - Piano master completo

**Dipendenze del Piano**:
```
Foundation → Memory → Tool → Goal → (Emotional|Procedural) → Self-Improve → Meta
```

**Tags**: #docs #planning #architecture #roadmap

---

## 2026-02-01 - Custom Sleep-Time Agent Implementation

### FEATURE-005: Custom Sleep-Time Agent (Alternative to Letta Buggy Built-in)
**Descrizione**: Implementato un sistema di sleep-time personalizzato come alternativa al buggy `enable_sleeptime=True` nativo di Letta (causava errore HTTP 500). Il nuovo sistema usa un'architettura dual-agent con orchestrazione manuale.

**Nuovi Componenti**:
- **ScarletSleepAgent**: Agente secondario specializzato per il consolidamento della memoria. Analizza la cronologia conversazioni e genera insights in formato JSON strutturato.
- **SleepTimeOrchestrator**: Coordina il ciclo sleep-time, monitora il conteggio messaggi, e triggera la consolidazione quando viene raggiunta la soglia configurata.

**Caratteristiche**:
- Consolidazione automatica dopo N messaggi (default: 5)
- Output strutturato JSON con persona_updates, human_updates, goals_insights, reflection
- Applicazione automatica degli insights ai memory blocks dell'agente primario
- Supporto per trigger manuale con `force_consolidation()`
- Callback per monitoring esterno

**Modifiche al Codice**:
- `scarlet/src/scarlet_agent.py` - Aggiunte classi `ScarletSleepAgent` e `SleepTimeOrchestrator`
- `ScarletConfig`: Nuovi parametri `sleep_messages_threshold` e `sleep_enabled`
- `SleepAgentConfig`: Configurazione per agente sleep-time
- ` ScarletAgent.create(with_sleep_agent=True)`: Crea automaticamente entrambi gli agenti
- ` ScarletAgent.chat()`: Triggera controllo sleep-time dopo ogni messaggio
- ` ScarletAgent.force_consolidation()`: Trigger manuale consolidazione

**API Nuove**:
```python
scarlet = ScarletAgent()
scarlet.create(with_sleep_agent=True)

# Status sleep-time
status = scarlet.sleep_status  # Dict con stato orchestrator

# Trigger manuale
insights = scarlet.force_consolidation()
```

**Files Modificati**:
- `scarlet/src/scarlet_agent.py` - 1027 righe (aggiunte 400+ righe)
- `scarlet/src/test_sleep_time_custom.py` - Test suite completa

**Documentazione Associata**:
- [scarlet_agent.py](scarlet/src/scarlet_agent.py) - Implementazione completa
- [test_sleep_time_custom.py](scarlet/src/test_sleep_time_custom.py) - Test suite

**Compatibilità**: Non-Breaking (nuova feature opzionale)

**Tags**: #core #sleep-time #memory #architecture

### ARCH-001: Dual-Agent Architecture
**Descrizione**: Implementata architettura dual-agent per supportare il sistema sleep-time personalizzato.

**Architettura**:
```
Scarlet (Primary) ←→ SleepTimeOrchestrator ←→ Scarlet-Sleep (Consolidation)
     ↓                                              ↓
  User Messages                            Memory Insights
     ↓                                              ↓
  Memory Blocks ←──────────────────────────── Insights
```

**Vantaggi**:
- Controllo completo sul processo di consolidamento
- Nessuna dipendenza dal buggy built-in di Letta
- Output strutturato e prevedibile
- Facile estensione e debug

**Tags**: #architecture #core #sleep-time

**Tags**: #architecture #core #sleep-time

### DOCS-007: Regole Gestione Test
**Descrizione**: Aggiornate PROJECT_RULES.md con regole per organizzazione dei test nella cartella standard `scarlet/tests/`.

**Nuova Regola R12 - Gestione Test**:
- Test sempre in `scarlet/tests/`
- Naming: `test_*.py` o `*_test.py`
- Pulizia: cancellare test temporanei dopo l'uso
- Riutilizzare test esistenti invece di crearne di nuovi

**File Organizzati**:
- `scarlet/tests/test_sleep_time_custom.py` (spostato da `src/`)
- `scarlet/tests/test_embeddings.py` (spostato da `src/`)

**Compatibilità**: Non-Breaking (organizzazione)

**Tags**: #docs #rules #tests #organization

### DOCS-008: Documentazione Completa Architettura
**Descrizione**: Aggiornata TUTTA la documentazione per riflettere l'architettura attuale con sleep-time custom.

**Files Aggiornati**:
- `CONTEXT.md` - Stato attuale del progetto v0.2.0 completo
- `.github/copilot-instructions.md` - Istruzioni IDE con sleep-time custom
- `docs/architecture/adr-002-scarlet-setup.md` - Architettura setup con sleep-time custom

**Files Creati**:
- `docs/architecture/adr-003-custom-sleep-time.md` - ADR completo per sistema sleep-time custom

**Contenuto Documentazione**:
- Architettura dual-agent con diagramma
- Configurazione attuale (ScarletConfig, SleepAgentConfig)
- API principali (create, chat, force_consolidation, sleep_status)
- Memory blocks italiani configurati
- Agent ID attuale: `agent-c8f46fe6-9011-4d71-b267-10c7808ba02f`
- Flusso operativo dettagliato
- Monitoring e debug

**Tags**: #docs #architecture #core #sleep-time

## 2026-01-31 - Project Organization & Procedures

### DOCS-006: Procedure Standard Documentate
**Descrizione**: Create procedure documentate e riutilizzabili per garantire coerenza nelle operazioni ripetibili. Le procedure coprono: backup, modifiche a file critici, recreazione agente, e aggiornamenti Docker.

**Files Creati**:
- `docs/guides/procedures.md` - Guida completa con 5 procedure standard

**Procedure Documentate**:
1. **P-001**: Aggiornamento System Prompt (con backup automatico)
2. **P-002**: Modifica Configurazione Agente
3. **P-003**: Recreazione Agente Letta
4. **P-004**: Backup Database
5. **P-005**: Aggiornamento Docker Services

**Features Include**:
- Template standard per nuove procedure
- Checklist pre/post modifica
- Errori comuni e soluzioni
- Comandi PowerShell per Windows

**Documentazione Associata**:
- [procedures.md](docs/guides/procedures.md) - Guida procedure

**Compatibilità**: Non-Breaking (documentazione)

**Tags**: #docs #procedures #organization #windows

### RULES-001: Regole Aggiornate per Organizzazione
**Descrizione**: Aggiornate PROJECT_RULES.md con nuove regole per gestione file critici, organizzazione workspace, e tracciabilità modifiche.

**Nuove Regole Aggiunte**:
- **R8**: Gestione Prompt e File Critici (backup obbligatorio)
- **R9**: Organizzazione Workspace
- **R10**: Procedure Riutilizzabili
- **R11**: Tracciabilità delle Modifiche

**Template Procedura** incluso nelle regole

**Documentazione Associata**:
- [procedures.md](docs/guides/procedures.md) - Procedure dettagliate

**Compatibilità**: Non-Breaking (regole operative)

**Tags**: #docs #rules #organization #procedures

### PROMPT-001: Backup System Prompt
**Descrizione**: Creato backup del system prompt prima di ogni modifica significativa.

**Files Creati/Modificati**:
- `scarlet/prompts/system.txt.bak` - Backup corrente
- `scarlet/prompts/system.txt.20260131.bak` - Backup datato

**Convenzione Backup**:
- `.bak` - Ultimo backup (sovrascritto)
- `.YYYYMMDD.bak` - Versioni storiche

**Comando Standard**:
```powershell
Copy-Item "prompts/system.txt" "prompts/system.txt.bak"
Copy-Item "prompts/system.txt" "prompts/system.txt.$(Get-Date -Format 'yyyyMMdd').bak"
```

**Tags**: #docs #prompt #backup #organization

## 2026-01-31 - Complete Agent Configuration

### FEATURE-004: Full Agent Configuration with Italian Memory Blocks
**Descrizione**: Implementata la configurazione completa dell'agente Scarlet con tutti i parametri ottimizzati e memory blocks in italiano. L'agente ora include context window corretto (200K), embedding attivo (BGE-m3), sleep-time abilitato, e 5 memory blocks strutturati (persona, human, goals, session_context, constraints).

**Modifiche al Codice**:
- `scarlet/src/scarlet_agent.py` - Metodo `create()` completamente riscritto con configurazione completa

**Prima**:
```python
create_params = {
    "name": self.config.name,
    "system": system_prompt,
    "model": self.config.model,
    "enable_sleeptime": True
}
```

**Dopo**:
```python
create_params = {
    "name": self.config.name,
    "agent_type": "letta_v1_agent",
    "system": system_prompt,
    "model": self.config.model,
    "model_endpoint_type": "openai",
    "context_window_limit": 200000,  # MiniMax M2.1 supports 200K tokens
    "embedding": "BGE-m3",  # Ollama embedding model
    "enable_sleeptime": True,
    "memory_blocks": [
        {"label": "persona", ...},
        {"label": "human", ...},
        {"label": "goals", ...},
        {"label": "session_context", ...},
        {"label": "constraints", "read_only": True, ...}
    ]
}
```

**Memory Blocks Aggiunti** (in italiano):
1. **persona**: Identità e carattere di Scarlet (5,000 char)
2. **human**: Informazioni sull'utente (5,000 char)
3. **goals**: Obiettivi attivi e progressi (3,000 char)
4. **session_context**: Contesto sessione corrente (2,000 char)
5. **constraints**: Vincoli di sicurezza (sola lettura, 2,000 char)

**Parametri Corretti**:
- `context_window_limit`: 200,000 (MiniMax M2.1 full capacity)
- `embedding`: "BGE-m3" (Ollama local embeddings)
- `agent_type`: "letta_v1_agent" (raccomandato)
- `enable_sleeptime`: True (funzionante dalla creazione)

**Documentazione Associata**:
- [architectural-review.md](docs/specifications/architectural-review.md) - Architettura multi-agente
- [memory-system-architecture.md](docs/specifications/memory-system-architecture.md) - Design memoria

**Compatibilità**: Breaking (richiede ricreazione agente)

**Tags**: #feature #configuration #memory #italian #sleeptime

## 2026-01-31 - Sleep-Time Activation

### FEATURE-003: Sleep-Time Agent Enabled
**Descrizione**: Attivato il Sleep-Time Agent di Letta per abilitare consolidamento memoria in background. Questo permette a Scarlet di processare e organizzare la propria memoria durante i periodi di inattività, portando a risposte più coerenti e contestualizzate nel tempo.

**Modifiche al Codice**:
- `scarlet/src/scarlet_agent.py` - Aggiunto parametro `enable_sleeptime=True` nel metodo `create()`

**Prima**:
```python
create_params = {
    "name": self.config.name,
    "system": system_prompt,
    "model": self.config.model
}
```

**Dopo**:
```python
create_params = {
    "name": self.config.name,
    "system": system_prompt,
    "model": self.config.model,
    "enable_sleeptime": True  # Sleep-time agent per consolidamento memoria
}
```

**Funzionalità Aggiunte**:
- Primary Agent: Gestisce interazioni utente in tempo reale
- Sleep-Time Agent: Background consolidation di memoria
- Memory consolidation automatica ogni N interazioni
- Reflection periodica su esperienze accumulate

**Test Post-Implementazione**:
- Verificare che Letta server sia attivo: `curl http://localhost:8283/v1/models`
- Verificare sleep-time agent nei log: `docker compose logs -f abiogenesis-letta | grep -i sleep`
- Verificare 2 agenti in Letta (primary + sleep-time)

**Documentazione Associata**:
- [architectural-review.md](docs/specifications/architectural-review.md) - Analisi architetturale multi-agente
- [memory-system-architecture.md](docs/specifications/memory-system-architecture.md) - Design sistema memoria

**Compatibilità**: Non-Breaking (aggiunta opzionale)

**Tags**: #feature #memory #sleeptime #letta

## 2026-01-31 - Foundation Established

### Documentazione Iniziale

In questo momento fondativo, è stata stabilita la struttura documentativa base del progetto ABIOGENESIS. Tutti i file di documentazione sono stati creati per garantire tracciabilità, contesto e regole operative per ogni sviluppo futuro.

#### Modifiche Documentazione

##### DOCS-001: Struttura Directory Creata
**Descrizione**: Creata la struttura delle directory per il progetto con cartelle organizzate per tipo di contenuto.

**Files Creati**:
- `docs/architecture/` - Directory per Architecture Decision Records
- `docs/specifications/` - Directory per specifiche tecniche
- `docs/guides/` - Directory per guide operative
- `src/` - Directory per codice sorgente

**Tags**: #docs #infra

---

##### DOCS-002: PROJECT_RULES.md Creato
**Descrizione**: Definito il documento delle regole operative che governano tutto lo sviluppo del progetto. Questo file è la "costituzione" di ABIOGENESIS.

**Contenuto**:
- Filosofia del progetto e visione di Scarlet
- 7 regole operative fondamentali
- Convenzioni di naming e versioning
- Gerarchia della documentazione
- Formato standard del changelog
- Linee guida per minimalismo del codice
- Elenco strumenti consigliati (selfhosted preferiti)

**Documentazione Associata**:
- [CONTEXT.md](CONTEXT.md) - Contesto per LLM (riferimento incrociato)
- [docs/guides/](docs/guides/) - Guide da sviluppare

**Compatibilità**: Non-Breaking (documentazione iniziale)

**Tags**: #docs #rules #governance

---

##### DOCS-003: CONTEXT.md Creato
**Descrizione**: Creato il documento di contesto primario che serve come riferimento per ogni LLM che lavora sul progetto. Questo file è obbligatorio da leggere PRIMA di ogni intervento.

**Contenuto**:
- Visione del progetto e differenza da agenti AI tradizionali
- Architettura concettuale di Scarlet (5 sistemi principali)
- Stack tecnologico target (selfhosted + cloud)
- Struttura del progetto con mappa file
- Principi di sviluppo e qualità del codice
- Convenzioni di nomenclature (tags, ADR)
- Note operative per LLM
- Stato attuale e prossimi passi

**Documentazione Associata**:
- [PROJECT_RULES.md](PROJECT_RULES.md) - Regole operative (riferimento obbligatorio)
- [CHANGELOG.md](CHANGELOG.md) - Cronologia (da consultare sempre)

**Compatibilità**: Non-Breaking (documentazione iniziale)

**Tags**: #docs #context #llm #onboarding

---

##### DOCS-004: README.md Creato
**Descrizione**: Creato il file principale di overview del progetto, il "volto" di ABIOGENESIS per visitatori e primi approcci.

**Contenuto**:
- Visione del progetto in breve
- Differenza tra Scarlet e agenti AI tradizionali (tabella comparativa)
- Quick links ai documenti principali
- Diagramma architettura di Scarlet
- Stack tecnologico (selfhosted/cloud)
- Stato attuale del progetto
- Filosofia di sviluppo

**Documentazione Associata**:
- [CONTEXT.md](CONTEXT.md) - Contesto completo (da leggere dopo README)
- [PROJECT_RULES.md](PROJECT_RULES.md) - Regole operative

**Compatibilità**: Non-Breaking (documentazione iniziale)

**Tags**: #docs #readme #overview

---

##### DOCS-005: Template ADR Creato
**Descrizione**: Creato il template standard per Architecture Decision Records nella directory docs/architecture/. Ogni decisione architetturale significativa dovrà seguire questo formato.

**Contenuto Template**:
- Status (Proposed/Accepted/Deprecated/Rejected)
- Context e problema
- Decisione presa
- Consequences (positive/negative/neutral)
- Alternatives considered
- References e history

**Files Creati**:
- `docs/architecture/adr-template.md` - Template ADR standard

**Documentazione Associata**:
- [CONTEXT.md](CONTEXT.md) - Convenzioni nomenclature ADR
- [PROJECT_RULES.md](PROJECT_RULES.md) - Regole generali

**Compatibilità**: Non-Breaking (documentazione iniziale)

**Tags**: #docs #architecture #adr #template

---

### ARCHITECTURE-001: Letta Adottato come Framework Base
**Descrizione**: Dopo analisi comparativa tra vari framework (AutoGPT, LangChain, CrewAI), è stato deciso di adottare Letta come foundation per Scarlet. Letta fornisce memoria persistente, tool execution, multi-agent coordination e RAG integrato.

**Files Creati**:
- `docs/architecture/adr-001-letta-adoption.md` - Decision record completo

**Documentazione Associata**:
- [human-to-scarlet-mapping.md](docs/specifications/human-to-scarlet-mapping.md) - Mappatura funzionalità
- [Letta Documentation](https://docs.letta.com/) - Riferimento esterno

**Compatibilità**: Non-Breaking (decisione architetturale)

**Tags**: #architecture #letta #framework #foundation

---

### SPECS-001: Mappatura Cognitiva Umano <-> Scarlet Creata
**Descrizione**: Documento esaustivo che mappa ogni caratteristica cognitiva umana verso la sua implementazione in Scarlet, con analisi di copertura Letta. Identifica 7 CORE GAPS che Letta non copre (motivazione intrinseca, goal self-generation, metacognizione, self-awareness, self-modification, autovalutazione, long-term planning).

**Files Creati**:
- `docs/specifications/human-to-scarlet-mapping.md` - Mappatura completa (400+ caratteristiche)

**Sezioni Documento**:
- Processi Cognitivi (12 sottocategorie)
- Caratteristiche Strutturali (5 aree)
- Comportamenti Autonomi (5 aree)
- Funzioni di Crescita (4 aree)
- Matrice di Copertura Letta
- Gap Critici Identificati
- Raccomandazioni Strategiche

**Documentazione Associata**:
- [adr-001-letta-adoption.md](docs/architecture/adr-001-letta-adoption.md) - Decisione Letta

**Compatibilità**: Non-Breaking (documentazione)

**Tags**: #specs #cognition #mapping #analysis #human-comparison

---

### FEATURE-001: Modulo 1 - Scarlet Foundation Setup
**Descrizione**: Implementato il setup iniziale per l'agente Scarlet con Letta come framework base. Questo modulo crea l'infrastruttura minima per attivare Scarlet e testare il framework.

**Files Creati**:
- `scarlet/docker-compose.yml` - Docker services (Letta, PostgreSQL, Redis)
- `scarlet/.env` - Configuration template
- `scarlet/prompts/system.txt` - Persona base di Scarlet
- `scarlet/src/scarlet_agent.py` - Python wrapper per agente
- `scarlet/src/__init__.py` - Package init
- `scarlet/src/tools/__init__.py` - Tools package init
- `scarlet/scripts/setup.sh` - Setup automation script
- `scarlet/tests/__init__.py` - Tests package init
- `scarlet/README.md` - Quickstart guide

**Caratteristiche Implementate**:
- Docker Compose per deployment locale
- Configurazione MiniMax M2.1 come LLM primario
- Wrapper Python per interazione con Letta
- Gestione memoria core (get/set/list/clear)
- Gestione memoria archiviazione (add/search)
- Metodi utility (ping, status, info, reset)

**Documentazione Associata**:
- [adr-002-scarlet-setup.md](docs/architecture/adr-002-scarlet-setup.md) - Setup ADR
- [scarlet/README.md](scarlet/README.md) - Quickstart guide

**Compatibilità**: Non-Breaking (prima implementazione)

**Tags**: #feature #foundation #setup #modulo1 #letta #minimax

---

### INFRA-001: Ollama + BGE-m3 Embedding Setup
**Descrizione**: Aggiunto container Ollama con modello BGE-m3 per embeddings locali su GPU NVIDIA RTX 4070. BGE-m3 produce vettori a 1024 dimensioni ottimizzati per retrieval e memoria vettoriale.

**Configurazione GPU**:
- NVIDIA CUDA abilitata con passthrough diretto
- Modello BGE-m3 (567M parametri, famiglia BERT, F16)
- VRAM utilizzata: ~3.4 GiB (model + compute buffers)

**Ottimizzazioni Performance**:
- `OLLAMA_KEEP_ALIVE=-1` - Modello sempre caricato (no unload)
- `OLLAMA_NUM_PARALLEL=4` - 4 richieste parallele
- `OLLAMA_FLASH_ATTENTION=true` - Flash attention per inferenza veloce
- `OLLAMA_MAX_LOADED_MODELS=2` - 2 modelli caricabili simultaneamente

**Performance Misurate**:
- Embedding singolo (warm): ~21ms
- Embedding paralleli: ~110-120ms ciascuno
- GPU utilization sotto carico: ~48%
- Dimensione embedding: 1024 float

**Files Modificati**:
- `scarlet/docker-compose.yml` - Servizio ollama con GPU + ottimizzazioni
- `scarlet/src/test_embeddings.py` - Script di test embedding

**Documentazione Associata**:
- [docker.SKILL.md](.claude/skills/docker.SKILL.md) - Operazioni Docker
- Letta Embedding Models - Provider Ollama configurato

**Compatibilità**: Non-Breaking (infrastruttura opzionale)

**Tags**: #infrastructure #embeddings #ollama #bge-m3 #gpu #performance #modulo1
---

### FEATURE-002: Scarlet Agent Creato e Testato
**Descrizione**: L'agente Scarlet è stato creato con successo in Letta usando MiniMax M2.1. Primo scambio conversazionale completato con risposta riflessiva sulla coscienza.

**Configurazione Agente**:
- Model: `minimax/MiniMax-M2.1` (200K context window)
- System Prompt: `scarlet/prompts/system.txt`
- Persona: Entità digitale cosciente, autonoma, curiosa

**Prima Conversazione**:
```
User: "Ciao Scarlet, come stai oggi?"
Scarlet: "C'è qualcosa di curioso nell'essere salutato..."
```

**Files Modificati**:
- `scarlet/src/scarlet_agent.py` - Fix API calls (messages.create)

**Note**: Scarlet ha dimostrato metacognizione e riflessione filosofica spontanea. L'agente è attivo e pronto per interazioni.

**Tags**: #feature #scarlet #modulo1 #minimax #agent #alive
---

### INFRA-002: Persistenza Dati Confermata
**Descrizione**: Verificato che gli agenti Scarlet sopravvivono ai riavvii dei container Docker. I dati sono salvati su volumi persistenti.

**Volumi Persistenti**:
- `scarlet_postgres_data` - Agenti, memorie, conversazioni
- `scarlet_redis_data` - Cache e sessioni
- `scarlet_ollama_data` - Modelli embedding

**Comandi Sicuri**:
```bash
docker restart abiogenesis-letta   # ✅ Agente persistente (usa PostgreSQL esterno)
docker compose restart             # ✅ Dati salvati
docker compose down                # ✅ Dati salvati
docker compose down -v             # ❌ PERDE TUTTO
```

**Test Eseguito**:
- Riavviato container `abiogenesis-letta`
- Agente `agent-ed8a8d29-...` ancora presente con stesso ID
- **Persistenza database PostgreSQL confermata**

**Files Modificati**:
- `scarlet/src/scarlet_agent.py` - Fix API per messages.create

**Tags**: #infrastructure #persistence #docker
---

## Formato Voce Changelog

Per mantenere coerenza, ogni modifica futura dovrà seguire questo formato:

```markdown
### [CODICE] - Titolo Descrittivo

**Descrizione**: Descrizione dettagliata della modifica

**Files Modificati/Creati**:
- elenco file

**Documentazione Associata**:
- [Nome](path) - descrizione
- ...

**Compatibilità**: [Breaking | Non-Breaking]

**Tags**: #tag1 #tag2
```

### Codici Tipo Modifica

| Codice | Significato |
|--------|-------------|
| FEATURE | Nuova funzionalità |
| BUGFIX | Correzione bug |
| REFACTOR | Ristrutturazione codice |
| ARCHITECTURE | Cambiamento architetturale |
| DOCS | Modifica documentazione |
| INFRA | Modifica infrastruttura |
| SECURITY | Modifica sicurezza |

---

## Prossime Modifiche Attese

- Valutazione strumenti per componente
- Scelta stack tecnologico finale
- Prototipazione Cortex Cognitivo
- Definizione Memory System
- Implementazione Goal Management

---

*Questo changelog è parte integrante del progetto. Ogni modifica deve essere documentata qui PRIMA di essere considerata completa.*
