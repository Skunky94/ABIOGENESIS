# CNG-016: SLEEPING/DREAMING Clarification

**Data**: 2026-02-01  
**Tipo**: DOCS  
**ID**: DOCS-012  
**Versione**: 0.4.10  
**Breaking**: No

---

## Descrizione

Chiarimento critico sulla distinzione tra:

1. **Sleep Agent (L0.2)**: Meccanismo automatico di consolidamento memoria che viene triggerato 
   ogni 5 messaggi dal webhook. Questo è già implementato (ADR-003).

2. **Stati SLEEPING/DREAMING (futuro)**: Stati nella state machine del runtime per un **vero 
   ciclo di sonno autentico** dove Scarlet decide autonomamente di dormire. Questa è una 
   implementazione futura.

## Motivazione

Confondere questi due concetti potrebbe portare a:
- Implementazione errata del runtime (tentativo di collegare SLEEPING allo Sleep Agent)
- Fraintendimento architetturale tra Layer
- Perdita di tracciabilità quando si implementerà il vero sonno

## Modifiche

### ADR-006 (adr-006-continuous-existence-runtime.md)
- Aggiunta nota esplicativa che SLEEPING/DREAMING sono **placeholder** per implementazione futura
- Tabella comparativa tra Sleep Agent (L0.2) e stati SLEEPING/DREAMING
- Chiarito che per L1 il runtime implementa solo IDLE ↔ THINKING ↔ ACTING

### SPEC-004 (spec-004-continuous-existence.md)
- Stesso chiarimento nella definizione degli stati
- Tabella comparativa Sleep Agent vs stati futuri
- Indicazione che transizioni verso SLEEPING/DREAMING saranno abilitate con L3.4

### ROADMAP (ROADMAP.md)
- **L0.2**: Aggiunta nota che NON è il "vero sonno", rimanda a L3.4
- **L3.4** (NUOVO): Aggiunto item "Authentic Sleep/Dream Cycle"
  - Domande da esplorare sul sonno autentico
  - Riferimenti architetturali a ADR-006 e ADR-003
  - Componenti attesi (sleep_cycle.py, dream_generator.py, fatigue model)
  - Prerequisiti architetturali linkati

## Tracciabilità Futura

Quando si implementerà L3.4 "Authentic Sleep/Dream Cycle":

1. Leggere ADR-006 sezione 4 (State Machine) per stati predefiniti
2. Leggere ADR-006 config `states.allowed_transitions` per transizioni
3. Leggere SPEC-004 sezione 5 per dettagli tecnici
4. Leggere ADR-003 per capire cosa FA GIÀ lo Sleep Agent (e non duplicare)

## Files Modificati

- `docs/architecture/adr-006-continuous-existence-runtime.md`
- `docs/specifications/spec-004-continuous-existence.md`
- `docs/ROADMAP.md`
- `CHANGELOG.md`

## Riferimenti

- ADR-003: Custom Sleep-Time (Sleep Agent esistente)
- ADR-006: Continuous Existence Runtime (stati predefiniti)
- SPEC-004: Continuous Existence specification
- ROADMAP L0.2: Sleep-Time Consolidation (esistente)
- ROADMAP L3.4: Authentic Sleep/Dream Cycle (nuovo, futuro)

---

**Tags**: #sleep #dreaming #state-machine #adr-006 #roadmap #tracciability #future-implementation
