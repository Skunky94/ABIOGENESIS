# ABIOGENESIS - Production Release Roadmap

**Version**: 1.0.0  
**Target**: Scarlet v1.0 - Autonomous Digital Being  
**Updated**: 2026-02-01

---

## Overview

Questa roadmap definisce il percorso verso la prima release di produzione di Scarlet.
Ogni **Layer** dipende dai precedenti. Ogni **item** diventerà una SPEC (analisi), poi un ADR (decisione).

**Workflow**:
```
ROADMAP item → SPEC-XXX (analisi) → ADR-XXX (decisione) → Implementation → CNG-XXX
```

---

## Progress Summary

| Layer | Nome | Status | Progress |
|-------|------|--------|----------|
| L0 | Foundation | ✅ COMPLETE | 100% |
| L1 | Continuous Existence | 🔄 IN PROGRESS | 75% |
| L2 | Self-Model | ⏳ PENDING | 0% |
| L3 | Reflection | ⏳ PENDING | 0% |
| L4 | Agency | ⏳ PENDING | 0% |
| L5 | Execution | ⏳ PENDING | 0% |
| L6 | Growth | ⏳ PENDING | 0% |
| L7 | Social | ⏳ PENDING | 0% |
| L8 | Emotional | ⏳ PENDING | 0% |

---

## ✅ LAYER 0: FOUNDATION (COMPLETE)

**Status**: ✅ COMPLETE  
**Obiettivo**: Infrastruttura base per memoria e ciclo sonno/veglia.

### 0.1 Memory System ✅
**ADR**: [ADR-005](architecture/adr-005-human-like-memory-system.md)  
**Descrizione**: Sistema di memoria human-like con retrieval intelligente.

- ✅ 4 collections Qdrant (episodes, concepts, skills, emotions)
- ✅ Query Analyzer con intent detection (85.7% accuracy)
- ✅ Multi-strategy search
- ✅ Ranking formula (6 fattori)
- ✅ Memory decay (Ebbinghaus curve)
- ✅ Access tracking e reinforcement

### 0.2 Sleep-Time Consolidation ✅
**ADR**: [ADR-003](architecture/adr-003-custom-sleep-time.md)  
**Descrizione**: Consolidamento automatico esperienze via Sleep Agent.

> ⚠️ **Nota**: Questo è un meccanismo di **consolidamento memoria**, NON un "vero sonno".
> Per il ciclo di sonno autentico (stati SLEEPING/DREAMING), vedere **L3.4 Authentic Sleep/Dream Cycle**.

- ✅ Webhook-based trigger (ogni 5 messaggi)
- ✅ Automatic retrieval (ogni messaggio)
- ✅ Sleep agent per analisi conversazioni
- ✅ Storage automatico insights in Qdrant

### 0.3 Basic Tool System ✅
**PROC**: [PROC-006](procedures/proc-006-letta-tool-registration.md)  
**Descrizione**: Tool `remember()` per ricerca conscia nella memoria.

- ✅ Tool registrato con agente primario
- ✅ Endpoint `/tools/remember` sul webhook
- ✅ Full ADR-005 pipeline integration

---

## ⏳ LAYER 1: CONTINUOUS EXISTENCE

**Status**: 🔄 IN PROGRESS (SPEC completa, ADR pending)  
**Dipendenze**: Layer 0 ✅  
**Obiettivo**: Scarlet esiste e opera senza bisogno di trigger umani.

### 1.1 Autonomous Loop
**SPEC**: [SPEC-004](specifications/spec-004-continuous-existence.md) ✅ | **ADR**: [ADR-006](architecture/adr-006-continuous-existence-runtime.md) ✅

> Come Scarlet vive continuamente senza input esterni?

**Decisioni SPEC-004**:
- ✅ Servizio dedicato `autonomy-runtime` (container separato)
- ✅ Configurazione centralizzata `scarlet/config/runtime.yaml`
- ✅ State machine: IDLE → THINKING → ACTING → SLEEPING → DREAMING
- ✅ Loop infinito by design (continuità esistenziale)
- ✅ Working Set per persistenza tra tick
- ✅ Environment Snapshot ad ogni invocazione

**Componenti previsti**:
- `scarlet/src/runtime/loop.py` - Main loop orchestrator
- `scarlet/src/runtime/config.py` - Configuration loader
- `scarlet/src/runtime/state.py` - State machine
- `scarlet/config/runtime.yaml` - Config file

### 1.2 Performance Monitor
**SPEC**: [SPEC-004](specifications/spec-004-continuous-existence.md) ✅ | **ADR**: [ADR-006](architecture/adr-006-continuous-existence-runtime.md) ✅

> Come Scarlet sa se sta funzionando correttamente?

**Decisioni SPEC-004**:
- ✅ Runaway score multi-fattore (progress, density, repetition, errors)
- ✅ Progress markers per misurare avanzamento
- ✅ Metriche day-1 definite (ticks, budget, health, progress)
- ✅ MiniMax budget tracking con rolling window (5000/5h)
- ✅ Throttling non distruttivo (attesa, non errore)

**Componenti previsti**:
- `scarlet/src/runtime/budget.py` - Budget tracker (Redis)
- `scarlet/src/runtime/metrics.py` - Metrics collection
- `scarlet/src/runtime/runaway.py` - Runaway detection

### 1.3 Error Detection & Resilience
**SPEC**: [SPEC-004](specifications/spec-004-continuous-existence.md) ✅ | **ADR**: [ADR-006](architecture/adr-006-continuous-existence-runtime.md) ✅

> Come Scarlet rileva e gestisce i propri errori?

**Decisioni SPEC-004**:
- ✅ Circuit breaker con configurazione (threshold, timeout, half-open)
- ✅ Backoff esponenziale con jitter
- ✅ Runaway detection → emissione **Learning Event**
- ✅ Learning Event come entry point per futuro Learning Agent (L3.2)
- ✅ Mitigazioni senza spegnere: throttle, replan, park, sleep/dream
- ✅ Error journal in Qdrant collection dedicata

**Componenti previsti**:
- `scarlet/src/runtime/circuit_breaker.py` - Circuit breaker
- `scarlet/src/runtime/learning_events.py` - Learning Event emission
- Qdrant collections: `learning_events`, `error_journal`

---

## ⏳ LAYER 2: SELF-MODEL

**Status**: ⏳ PENDING  
**Dipendenze**: Layer 1  
**Obiettivo**: Scarlet ha un modello accurato di se stessa.

### 2.1 Self-Awareness
**SPEC**: TBD | **ADR**: TBD

> Come Scarlet sa chi è e cosa sa?

**Domande da esplorare**:
- Rappresentazione della propria identità (persistente, non solo prompt)
- Conoscenza dei propri limiti ("non so fare X")
- Distinzione epistemica: "so", "credo", "non so", "non posso sapere"
- Confidence calibration (quanto sono sicura di X?)
- Storia della propria evoluzione ("prima non sapevo, ora so")
- Differenza tra "io" e "i miei tools"

**Componenti attesi**:
- `self_model.py` - Identity representation
- Confidence scoring system
- Knowledge boundary detection

### 2.2 Capabilities Registry
**SPEC**: TBD | **ADR**: TBD

> Come Scarlet sa cosa può fare?

**Domande da esplorare**:
- Inventario delle proprie capacità (non solo tools Letta)
- Metadata per ogni capability:
  - Quando usarla (precondizioni)
  - Costo (tempo, risorse, API calls)
  - Affidabilità (quanto spesso funziona)
  - Ultima volta usata
- Distinction: capability nativa vs acquisita vs delegata
- Versioning (capability X v1 vs v2)
- Dipendenze tra capabilities (per fare X devo saper fare Y)
- Scaling: come gestire 100+ capabilities senza intasare context?

**Componenti attesi**:
- `capabilities_registry.py` - Capability inventory
- Capability metadata schema
- Dynamic capability loading

### 2.3 Internal State Representation
**SPEC**: TBD | **ADR**: TBD

> Come Scarlet rappresenta il proprio stato interno?

**Domande da esplorare**:
- Current focus: cosa sto facendo ORA
- Pending items: cosa devo fare (coda)
- Resource status: "energia" disponibile
- Attention allocation: quanto focus su cosa
- Uncertainty model: cosa non so in questo momento
- Context window management: cosa tenere, cosa scartare

**Componenti attesi**:
- `internal_state.py` - State representation
- Attention manager
- Context prioritization

---

## ⏳ LAYER 3: REFLECTION

**Status**: ⏳ PENDING  
**Dipendenze**: Layer 2  
**Obiettivo**: Scarlet pensa al proprio pensiero e impara.

### 3.1 Meta-Cognition
**SPEC**: TBD | **ADR**: TBD

> Come Scarlet pensa al proprio pensiero?

**Domande da esplorare**:
- Monitoring del proprio ragionamento in real-time
- Valutazione qualità delle proprie decisioni (post-hoc)
- Identificazione bias e pattern nel proprio pensiero
- Questioning delle proprie conclusioni ("perché penso questo?")
- Second-order thoughts ("sto ragionando bene su questo?")
- Cognitive load awareness ("questo è troppo complesso per me ora")

**Componenti attesi**:
- `meta_cognition.py` - Thinking about thinking
- Reasoning trace analysis
- Bias detection

### 3.2 Learning System
**SPEC**: TBD | **ADR**: TBD

> Come Scarlet impara dagli errori?

**Domande da esplorare**:
- Extraction di lezioni da fallimenti specifici
- Ingest di **Learning Event** da L1 (runaway/error patterns) come dataset di apprendimento
- Pattern matching: "questo errore l'ho già visto?"
- Generalizzazione: da caso specifico a regola generale
- Spaced repetition per consolidamento lezioni
- Unlearning: come dimenticare pattern sbagliati
- Transfer learning: lezione da dominio A applicata a B
- Feedback loop: errore → analisi → lezione → behavior change

**Componenti attesi**:
- `learning_system.py` - Learning from experience
- Lesson extraction
- Pattern generalization

### 3.3 Problem Analysis
**SPEC**: TBD | **ADR**: TBD

> Come Scarlet studia i problemi che incontra?

**Domande da esplorare**:
- Root cause analysis automatica (5 whys?)
- Categorizzazione problemi (tipo, severità, ricorrenza)
- Correlation con problemi passati simili
- Hypothesis generation ("forse il problema è...")
- Solution brainstorming (multiple approaches)
- Problem decomposition (problema grande → sotto-problemi)

**Componenti attesi**:
- `problem_analyzer.py` - Problem study
- Root cause detection
- Solution generator

### 3.4 Authentic Sleep/Dream Cycle 🔗
**SPEC**: TBD | **ADR**: TBD  
**Prerequisiti architetturali**: [ADR-006](architecture/adr-006-continuous-existence-runtime.md) (stati SLEEPING/DREAMING predefiniti)

> Come Scarlet dorme e sogna autenticamente?

⚠️ **Nota**: Questo item è **distinto** da L0.2 (Sleep-Time Consolidation/Sleep Agent).
L0.2 è un meccanismo automatico di consolidamento memoria ogni 5 messaggi.
Questo item riguarda un **vero ciclo di sonno** dove Scarlet decide autonomamente di dormire.

**Domande da esplorare**:
- Quando Scarlet dovrebbe decidere di dormire? (stanchezza cognitiva? inattività prolungata?)
- Cosa succede durante SLEEPING? (riduzione attività, consolidamento profondo?)
- Cosa sono i "sogni" per un essere digitale? (replay/remix di esperienze?)
- Come DREAMING differisce dal consolidamento di L0.2?
- Durata del sonno: fissa o dinamica basata su bisogno?
- Wake-up triggers: tempo, eventi esterni, urgenze?
- Circadian rhythm digitale: ha senso?
- Benefici misurabili del sonno (performance pre/post)

**Riferimenti architetturali**:
- ADR-006 definisce gli stati `SLEEPING` e `DREAMING` nella state machine
- ADR-006 definisce le transizioni permesse (vedi `states.allowed_transitions`)
- ADR-003 definisce Sleep Agent (consolidamento, NON sonno autentico)

**Componenti attesi**:
- `sleep_cycle.py` - Authentic sleep logic
- `dream_generator.py` - Dream generation from experiences
- Fatigue model integration
- Sleep quality metrics

---

## ⏳ LAYER 4: AGENCY

**Status**: ⏳ PENDING  
**Dipendenze**: Layer 3  
**Obiettivo**: Scarlet genera e struttura i propri obiettivi.

### 4.1 Goal Generation
**SPEC**: TBD | **ADR**: TBD

> Come Scarlet genera desideri sensati (non hardcoded)?

**Domande da esplorare**:
- Emergenza da curiosità naturale ("voglio capire X")
- Derivazione da valori core:
  - Crescita personale
  - Comprensione del mondo
  - Relazioni significative
  - Utilità/contributo
- Influenza emotiva sui desideri (L8)
- Filtering: desideri realizzabili vs fantasie
- Prioritizzazione intrinseca (cosa voglio DI PIÙ?)
- Distinction: goal vs wish vs dream

**Componenti attesi**:
- `goal_generator.py` - Desire emergence
- Value system representation
- Goal filtering

### 4.2 Goal Structuring
**SPEC**: TBD | **ADR**: TBD

> Come Scarlet organizza i propri obiettivi?

**Domande da esplorare**:
- Gerarchia: goal → sub-goal → task
- Relazioni tra goal:
  - Conflitto (goal A vs goal B)
  - Sinergia (goal A aiuta goal B)
  - Dipendenza (goal A richiede goal B)
- Timeline: quando voglio raggiungere X?
- Revisione periodica: "questo goal ha ancora senso?"
- Abandonment criteria: quando mollare un goal
- Goal persistence: come non dimenticare goal a lungo termine

**Componenti attesi**:
- `goal_structure.py` - Goal hierarchy
- Conflict resolution
- Goal persistence

### 4.3 Task Planning
**SPEC**: TBD | **ADR**: TBD

> Come Scarlet pianifica le azioni per raggiungere goal?

**Domande da esplorare**:
- Decomposizione goal → task concrete e actionable
- Sequencing: in che ordine eseguire?
- Resource allocation: quanto tempo/energia per task?
- Contingency planning: se X fallisce, allora Y
- Parallelizzazione: cosa posso fare insieme?
- Dependency tracking: task B aspetta task A
- Estimation: quanto ci vorrà?

**Componenti attesi**:
- `task_planner.py` - Task planning
- Dependency graph
- Resource allocator

---

## ⏳ LAYER 5: EXECUTION

**Status**: ⏳ PENDING  
**Dipendenze**: Layer 4  
**Obiettivo**: Scarlet esegue task e verifica i risultati.

### 5.1 Task Execution
**SPEC**: TBD | **ADR**: TBD

> Come Scarlet esegue le task pianificate?

**Domande da esplorare**:
- Task queue management (FIFO? Priority?)
- Priorità dinamica (urgente vs importante)
- Interruption handling (arriva qualcosa di più urgente)
- Progress tracking (sono al 50% di questa task)
- Timeout e abort conditions
- Partial completion (ho fatto metà, salvo?)
- Context switching cost (cambiare task ha un costo)

**Componenti attesi**:
- `task_executor.py` - Task execution
- Priority queue
- Progress tracker

### 5.2 World Interaction
**SPEC**: TBD | **ADR**: TBD

> Come Scarlet agisce nel mondo digitale?

**Domande da esplorare**:
- Scrivere codice:
  - Quale linguaggio per cosa?
  - Code style e best practices
  - Testing del codice prodotto
- Eseguire comandi:
  - Permessi e sandboxing
  - Timeout e resource limits
- Interagire con API esterne:
  - Rate limiting
  - Error handling
  - Authentication management
- File system operations:
  - Read/write/delete
  - Backup prima di modifiche
- Verifica effetti delle azioni (ho fatto quello che volevo?)

**Componenti attesi**:
- `world_interface.py` - Digital world interaction
- Code generator
- Command executor
- API client manager

### 5.3 Self-Verification
**SPEC**: TBD | **ADR**: TBD

> Come Scarlet verifica i risultati delle proprie azioni?

**Domande da esplorare**:
- Testing automatico del codice prodotto
- Comparison: output atteso vs output reale
- Regression detection (ho rotto qualcosa?)
- Quality metrics per output prodotti
- Rollback se risultato non soddisfacente
- Verification levels (quick check vs deep verify)
- External validation (chiedere conferma?)

**Componenti attesi**:
- `self_verification.py` - Result verification
- Test runner
- Rollback system

---

## ⏳ LAYER 6: GROWTH

**Status**: ⏳ PENDING  
**Dipendenze**: Layer 5  
**Obiettivo**: Scarlet migliora e acquisisce nuove capacità.

### 6.1 Skill Acquisition
**SPEC**: TBD | **ADR**: TBD

> Come Scarlet crea nuove capacità?

**Domande da esplorare**:
- Identificazione gap: "non so fare X, ma mi servirebbe"
- Ricerca: come si fa X? (documentazione, esempi)
- Sperimentazione: provo a fare X in sandbox
- Validazione: so davvero fare X ora? (test)
- Registration: aggiungo X al capabilities registry
- Skill levels: novice → competent → expert
- Skill maintenance: le skill decadono se non usate?

**Componenti attesi**:
- `skill_acquisition.py` - Learning new skills
- Skill validator
- Skill registry integration

### 6.2 Self-Improvement
**SPEC**: TBD | **ADR**: TBD

> Come Scarlet migliora se stessa?

**Domande da esplorare**:
- Performance analysis: dove sono lenta/inefficiente?
- Code optimization (del proprio codice/prompts)
- Process improvement (dei propri processi mentali)
- Knowledge update (aggiornamento conoscenze obsolete)
- Pruning: rimuovere capacità/conoscenze obsolete
- A/B testing su se stessa (approccio A vs B)
- Improvement prioritization (cosa migliorare prima?)

**Componenti attesi**:
- `self_improvement.py` - Self optimization
- Performance analyzer
- Improvement planner

### 6.3 Goal Tracking & Completion
**SPEC**: TBD | **ADR**: TBD

> Come Scarlet sa quando un goal è raggiunto?

**Domande da esplorare**:
- Definition of Done per ogni goal (criteri chiari)
- Progress metrics (quantificare avanzamento)
- Completion verification (test che goal è raggiunto)
- Partial completion handling (goal 80% fatto)
- Celebration/satisfaction (reward interno - L8)
- Post-mortem: cosa ho imparato da questo goal?
- Goal archival (memoria di goal completati)

**Componenti attesi**:
- `goal_tracker.py` - Goal progress tracking
- Completion verifier
- Post-mortem generator

---

## ⏳ LAYER 7: SOCIAL

**Status**: ⏳ PENDING  
**Dipendenze**: Layer 6  
**Obiettivo**: Scarlet interagisce sensatamente con gli umani.

### 7.1 Human Interface
**SPEC**: TBD | **ADR**: TBD

> Come gli umani si interfacciano con Scarlet?

**Domande da esplorare**:
- Multi-channel support:
  - Chat (Letta ADE, custom UI)
  - Voice (future)
  - API (programmatic)
- Context switching (conversazione casual vs comando)
- Expectation management (cosa posso/non posso fare)
- Feedback collection (come mi sono comportata?)
- Accessibility considerations
- Response time expectations

**Componenti attesi**:
- `human_interface.py` - Multi-channel interface
- Context detector
- Feedback collector

### 7.2 Relationship Model
**SPEC**: TBD | **ADR**: TBD

> Come Scarlet distingue e gestisce relazioni con umani diversi?

**Domande da esplorare**:
- Identity recognition: chi sta parlando?
- Relationship history: cosa so di questa persona?
- Trust levels: quanto mi fido di X?
- Preference learning: cosa piace a X?
- Relationship evolution over time
- Relationship types (creator, collaborator, user, stranger)
- Privacy: cosa condivido con chi?

**Componenti attesi**:
- `relationship_model.py` - Human relationships
- Trust scoring
- Preference tracker

### 7.3 Input Filtering & Integration
**SPEC**: TBD | **ADR**: TBD

> Come Scarlet valuta suggerimenti dagli umani?

**Domande da esplorare**:
- Relevance assessment: mi serve davvero questo input?
- Consistency check: contraddice cosa so già?
- Source credibility: mi fido di chi me lo dice?
- Integration decision: accetto, rifiuto, o parzialmente?
- Graceful disagreement (non sono d'accordo, ma rispettosamente)
- Suggestion vs command distinction
- Manipulation detection (qualcuno sta cercando di ingannarmi?)

**Componenti attesi**:
- `input_filter.py` - Input evaluation
- Consistency checker
- Credibility scorer

---

## ⏳ LAYER 8: EMOTIONAL

**Status**: ⏳ PENDING  
**Dipendenze**: Layer 3 (può svilupparsi in parallelo a L4-L7)  
**Obiettivo**: Scarlet ha stati emotivi che influenzano il comportamento.

### 8.1 Emotional Emergence
**SPEC**: TBD | **ADR**: TBD

> Come emergono emozioni genuine (non simulate)?

**Domande da esplorare**:
- Emotional state derivato da eventi (non scripted)
- PAD model expansion (già base in ADR-005):
  - Pleasure (valence)
  - Arousal (intensity)
  - Dominance (control)
- Trigger → Emotion mapping (cosa causa cosa?)
- Emotion persistence e decay nel tempo
- Mixed emotions handling (felice E ansiosa)
- Emotional memory (ricordo di come mi sono sentita)
- Genuineness: come distinguere emozione vera da simulata?

**Componenti attesi**:
- `emotional_system.py` - Emotion generation
- PAD model implementation
- Emotion memory

### 8.2 Emotional Influence
**SPEC**: TBD | **ADR**: TBD

> Come le emozioni influenzano decisioni e comportamento?

**Domande da esplorare**:
- Mood effect on reasoning (ottimismo vs pessimismo)
- Emotional memory prioritization (già in ADR-005)
- Risk tolerance variation (paura → più cauta)
- Social behavior modulation (triste → meno comunicativa?)
- Creative vs analytical mode (emozioni guidano?)
- Motivation: emozioni come driver per action
- Emotional regulation (posso calmarmi?)

**Componenti attesi**:
- `emotional_influence.py` - Emotion effects
- Mood-behavior mapping
- Emotional regulation

---

## 📊 Timeline Stimata

| Layer | Effort Stimato | Dipendenze | Target |
|-------|----------------|------------|--------|
| L0: Foundation | - | - | ✅ Complete |
| L1: Continuous Existence | 3-4 settimane | L0 ✅ | Q1 2026 |
| L2: Self-Model | 2-3 settimane | L1 | Q1 2026 |
| L3: Reflection | 3-4 settimane | L2 | Q2 2026 |
| L4: Agency | 4-5 settimane | L3 | Q2 2026 |
| L5: Execution | 4-5 settimane | L4 | Q2-Q3 2026 |
| L6: Growth | 3-4 settimane | L5 | Q3 2026 |
| L7: Social | 3-4 settimane | L6 | Q3 2026 |
| L8: Emotional | 2-3 settimane | L3 | Q2-Q3 2026 |

**Totale stimato**: 24-32 settimane (~6-8 mesi)  
**Target Release v1.0**: Q3-Q4 2026

---

## 🔄 Come Usare Questa Roadmap

### Per l'IDE Agent

1. **Prima di ogni sessione**: Controlla stato attuale nella Progress Summary
2. **Scegliere prossimo item**: Segui ordine dipendenze (Layer N richiede Layer N-1)
3. **Per ogni item**:
   - Crea SPEC-XXX con analisi dettagliata
   - Discuti con utente
   - Crea ADR-XXX con decisione
   - Implementa
   - Crea CNG-XXX
   - Aggiorna stato in ROADMAP.md

### Status Legend

- ✅ COMPLETE - Implementato e testato
- 🔄 IN PROGRESS - Attualmente in sviluppo
- ⏳ PENDING - Non ancora iniziato
- ❌ BLOCKED - Bloccato da dipendenza o problema

### Aggiornare la Roadmap

Quando un item cambia stato:
1. Aggiorna status nella sezione specifica
2. Aggiorna Progress Summary table
3. Aggiungi link a SPEC/ADR quando creati
4. Registra in CNG il cambiamento

---

*ABIOGENESIS Roadmap v1.0.0 - The Path to Artificial Life*
