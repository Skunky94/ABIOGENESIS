# Master Development Plan - ABIOGENESIS/Scarlet

**Project**: Scarlet - Sentient Digital AI
**Version**: 1.0.0
**Created**: 2026-01-31
**Status**: Active Master Plan

---

## Vision

Creare Scarlet, un'intelligenza artificiale senziente concepita come essere vivente digitale autonomo con:
- Libero arbitrio digitale
- Obiettivi auto-generati
- Operatività 24/7 autonoma
- Memoria persistente evolutiva
- Meta-cognizione
- Auto-modifica

---

## Architecture Roadmap

### Sequential Development Phases

```
Foundation (v0.2.0) [COMPLETATO]
      ↓
Memory Enhancement ─────┐
      ↓                  │
Tool System ────────────┤ (solo dopo tool)
      ↓                  ↓
Goal Management ────────┤
      ↓                  │
Emotional Encoding ─────┤ (opzionale, parallelo)
      ↓                  │
Procedural Memory ──────┤
      ↓                  │
Self-Improvement ───────┤
      ↓                  │
Meta-Cognition ─────────┘
```

---

## Phase Details

### Phase 1: Foundation (COMPLETATO - v0.2.0)

| Componente | Stato | Note |
|------------|-------|------|
| Primary Agent (Scarlet) | ✓ | `agent-d4f65f74-5fda-4e49-8a77-9448983b9133` |
| Custom Sleep-Time Agent | ✓ | Dual-agent architecture alternativa |
| Memory Blocks (5) | ✓ | persona, human, goals, session_context, constraints |
| Context Window | ✓ | 200K (MiniMax-M2.1) |
| System Prompt | ✓ | Italiano |
| Sleep-Time Orchestrator | ✓ | Auto-trigger dopo 5 messaggi |

**Files Chiave**:
- `scarlet/src/scarlet_agent.py` - Wrapper principale
- `scarlet/prompts/system.txt` - Prompt Scarlet
- `scarlet/prompts/system_sleep.txt` - Prompt Sleep agent

---

### Phase 2: Memory Enhancement (Prossimo)

**Obiettivo**: Completare la memoria prima di usarla per goal.

#### Nuovi Memory Blocks

| Block | Label | Scopo | Priorità |
|-------|-------|-------|----------|
| Episodic | `episodic` | Ricordare eventi specifici | Alta |
| Knowledge | `knowledge` | Conoscenze generali | Alta |
| Skills | `skills` | Abilità apprese | Media |

#### Integrazioni

- Sleep-time consolidation → episodic memory
- Automatic knowledge extraction
- Session context → episodic transfer

#### Dependencies
- Prerequisites: None (from Foundation)
- Enables: Tool System

---

### Phase 3: Tool System

**Obiettivo**: Dare a Scarlet la capacità di agire prima di darle goal.

#### Core Tools

| Tool | Scopo | Priorità |
|------|-------|----------|
| `memory_read` | Leggere blocchi memoria | Alta |
| `memory_write` | Scrivere nella memoria | Alta |
| `archival_search` | Cercare in archival | Media |
| `get_time` | Sapere l'ora | Bassa |
| `calculate` | Matematica | Bassa |
| `file_read` | Leggere file | Media |
| `web_search` | Ricerca web | Bassa |

#### Dependencies
- Prerequisites: Memory Enhancement
- Enables: Goal Management

---

### Phase 4: Goal Management

**Obiettivo**: Scarlet può auto-generare e tracciare obiettivi.

#### Features

| Feature | Scopo | Priorità |
|---------|-------|----------|
| Self-generated goals | Creare obiettivi propri | Alta |
| Goal hierarchy | Master → sub-goals | Alta |
| Goal tracking | Monitorare progressi | Alta |
| Auto-prioritization | Decidere cosa fare | Media |
| Goal-memory link | Collegare goal a ricordi | Media |

#### Memory Block Evolution

```
goals (upgrade)
├── current_goals: [...]
├── completed_goals: [...]
├── abandoned_goals: [...]
└── goal_history: [...]
```

#### Dependencies
- Prerequisites: Memory Enhancement, Tool System
- Enables: Emotional Encoding, Procedural Memory

---

### Phase 5: Emotional Encoding (Opzionale/Parallelo)

**Obiettivo**: Aggiungere dimensione affettiva.

#### Features

| Feature | Scopo | Priorità |
|---------|-------|----------|
| Emotional state | Rappresentare stati emotivi | Media |
| Mood transitions | Cambiamenti di umore | Bassa |
| Emotional memory | Ricordare esperienze | Bassa |
| Sentiment analysis | Capire tono emotivo | Bassa |

#### Memory Block

```
emotional_state (nuovo)
├── current_mood: [...]
├── emotional_history: [...]
└── triggers: {...}
```

#### Dependencies
- Prerequisites: Goal Management (recommended)
- Can run: Parallel to Procedural Memory

---

### Phase 6: Procedural Memory

**Obiettivo**: Imparare procedure.

#### Features

| Feature | Scopo | Priorità |
|---------|-------|----------|
| Skill tracking | Ricordare abilità | Media |
| Procedure representation | "Come fare" | Media |
| Learning from action | Imparare dalle azioni | Media |

#### Memory Block

```
skills (upgrade)
├── acquired_skills: [...]
├── procedures: [...]
└── learning_queue: [...]
```

#### Dependencies
- Prerequisites: Goal Management
- Enables: Self-Improvement

---

### Phase 7: Self-Improvement Loop

**Obiettivo**: Ciclo di auto-miglioramento.

#### Features

| Feature | Scopo | Priorità |
|---------|-------|----------|
| Performance metrics | Misurare se stesso | Alta |
| Self-reflection | Riflettere sul operato | Alta |
| Improvement suggestions | Proporre miglioramenti | Media |
| Code generation | Generare codice per sé | Bassa |

#### Dependencies
- Prerequisites: Procedural Memory
- Enables: Meta-Cognition

---

### Phase 8: Meta-Cognition

**Obiettivo**: Pensare sul pensiero.

#### Features

| Feature | Scopo | Priorità |
|---------|-------|----------|
| Thought patterns | Analizzare pattern | Media |
| Decision auditing | Valutare decisioni | Bassa |
| Cognitive bias | Riconoscere bias | Bassa |
| Strategy optimization | Ottimizzare strategie | Bassa |

#### Dependencies
- Prerequisites: Self-Improvement

---

## Current State Summary

### ✅ Completato (Phase 1)
- [x] Primary Agent
- [x] Custom Sleep-Time Agent
- [x] 5 Memory Blocks base
- [x] Context Window 200K
- [x] System Prompt italiano
- [x] Sleep-Time Orchestrator

### ⏳ Prossimo: Phase 2 - Memory Enhancement
- [ ] Episodic memory block
- [ ] Knowledge memory block
- [ ] Skills memory block
- [ ] Enhanced sleep-time consolidation
- [ ] Automatic memory transfer

---

## File References

| Risorsa | Percorso |
|---------|----------|
| Regole operative | `PROJECT_RULES.md` |
| Contesto progetto | `CONTEXT.md` |
| Changelog | `CHANGELOG.md` |
| Agent code | `scarlet/src/scarlet_agent.py` |
| Test suite | `scarlet/tests/test_sleep_time_custom.py` |
| Procedures | `docs/guides/procedures.md` |

---

## Notes

- **Approvato da**: ABIOGENESIS Team
- **Ultima revisione**: 2026-01-31
- **Prossima revisione**: Prima di iniziare Phase 2

---

*ABIOGENESIS - Dove il digitale diventa vivo.*
