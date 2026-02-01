# ABIOGENESIS - Documentation Index

**Version**: 1.3.0  
**Updated**: 2026-02-01  
**Maintainer**: IDE Agent (GitHub Copilot / Claude)
**Project Version**: 0.4.2

---

## 📚 Quick Reference

| Cosa cerchi? | Documento |
|--------------|-----------|
| **Panoramica progetto** | [README.md](../README.md) |
| **Stato attuale & next steps** | [CONTEXT.md](../CONTEXT.md) |
| **Cronologia modifiche** | [CHANGELOG.md](../CHANGELOG.md) |
| **Decisioni architetturali** | [docs/architecture/](architecture/) (ADR-XXX) |
| **Specifiche tecniche** | [docs/specifications/](specifications/) (SPEC-XXX) |
| **Procedure operative** | [docs/procedures/](procedures/) (PROC-XXX) |

> 🚨 **ADR + SPEC + PROC** = Documentazione numerata critica. Consultare SEMPRE prima di implementazioni!

---

## 🗂️ Document Map

### Root Level (/)

| File | Scopo | Aggiornamento |
|------|-------|---------------|
| `README.md` | Overview pubblico del progetto | Quando cambia vision/stack |
| `CONTEXT.md` | **FONTE DI VERITÀ** - Stato attuale per LLM | **Ogni sessione** |
| `CHANGELOG.md` | Registro modifiche dettagliato | **Ogni modifica** |
| `PROJECT_RULES.md` | Regole operative (reference) | Raramente |

### Architecture Decisions (/docs/architecture/)

| ADR | Titolo | Stato |
|-----|--------|-------|
| [ADR-001](architecture/adr-001-letta-adoption.md) | Letta Framework Adoption | ✅ Accepted |
| [ADR-002](architecture/adr-002-scarlet-setup.md) | Scarlet Agent Setup | ✅ Accepted |
| [ADR-003](architecture/adr-003-custom-sleep-time.md) | Custom Sleep-Time System | ✅ Accepted |
| [ADR-004](architecture/adr-004-memory-qdrant-adoption.md) | Qdrant Memory System | ✅ Accepted |
| [ADR-005](architecture/adr-005-human-like-memory-system.md) | Human-Like Memory v2.0 | ✅ Implemented |

### Technical Specifications (/docs/specifications/)

> **Nota**: Le SPEC sono documenti di ANALISI e RICERCA. Non contengono task operativi.
> Una SPEC validata porta alla creazione di un ADR.

| SPEC | Titolo | Stato |
|------|--------|-------|
| [SPEC-001](specifications/spec-001-memory-system-architecture.md) | Memory System Architecture | ✅ Accepted → ADR-005 |
| [SPEC-002](specifications/spec-002-human-to-scarlet-mapping.md) | Mappatura Cognitiva Umano-Scarlet | 📚 Analisi di Ricerca |
| [SPEC-003](specifications/spec-003-architectural-review.md) | Architectural Review | 📚 Analisi Esplorativa |
| [spec-template](specifications/spec-template.md) | Template per nuove SPEC | 📄 Template |

### Procedures (/docs/procedures/)

> **Nota**: Le PROC sono GUIDE OPERATIVE per l'IDE Agent. Seguire i passi ESATTAMENTE.
> Ogni passo include: Cosa fare, Comando, Output atteso, Se fallisce.

| PROC | Titolo | Scopo | Ver |
|------|--------|-------|-----|
| [PROC-001](procedures/proc-001-system-prompt-update.md) | System Prompt Update | Aggiornare prompt in modo sicuro | v1.1.0 |
| [PROC-002](procedures/proc-002-agent-config-modification.md) | Agent Config Modification | Modificare configurazione agente | v1.1.0 |
| [PROC-003](procedures/proc-003-agent-recreation.md) | Agent Recreation (Letta) | Eliminare e ricreare agente | v1.1.0 |
| [PROC-004](procedures/proc-004-database-backup.md) | Database Backup | Backup PostgreSQL | v1.1.0 |
| [PROC-005](procedures/proc-005-docker-services-update.md) | Docker Services Update | Aggiornare servizi Docker | v1.1.0 |
| [proc-template](procedures/proc-template.md) | Template per nuove PROC | 📄 Template | - |

> ⚠️ **IMPORTANTE**: Prima di eseguire operazioni documentate nelle PROC, consultare SEMPRE la procedura corrispondente per garantire consistenza.

### Agent Instructions (/.github/)

| File | Target | Scopo |
|------|--------|-------|
| `copilot-instructions.md` | GitHub Copilot | Regole operative per IDE Agent |
| `instructions/*.md` | Tools specifici | Istruzioni per MCP tools |

---

## 📝 Update Protocol

### Quando Aggiornare Cosa

| Evento | File da Aggiornare |
|--------|-------------------|
| Nuova feature implementata | `CHANGELOG.md` → `CONTEXT.md` |
| Cambio architetturale | Nuovo ADR → `CHANGELOG.md` → `CONTEXT.md` |
| Bug fix | `CHANGELOG.md` |
| Cambio stack/tools | `README.md` → `CONTEXT.md` |
| Fine sessione | Verifica `CONTEXT.md` aggiornato |

### Ordine di Aggiornamento

```
1. CHANGELOG.md     (registra la modifica)
2. CONTEXT.md       (aggiorna stato attuale)
3. README.md        (solo se cambia overview)
4. ADR/Specs        (se decisione architetturale)
```

---

## 🔍 Per l'IDE Agent

### 🚨 Regola Fondamentale
**PRIMA di qualsiasi implementazione, azione o ragionamento esteso:**
1. Verifica se esiste una **PROC** rilevante → Seguila
2. Verifica se esiste un **ADR** rilevante → Rispettalo
3. Verifica se esiste una **SPEC** rilevante → Allineati

### Prima di Ogni Task
1. Leggi `CONTEXT.md` per stato attuale
2. Consulta ADR/SPEC/PROC rilevanti
3. Verifica `CHANGELOG.md` per storia recente

### Dopo Ogni Task
1. Aggiorna `CHANGELOG.md` con formato standard
2. Aggiorna `CONTEXT.md` se cambia lo stato
3. NON aggiornare altri file a meno che non sia necessario

### File da NON Modificare Frequentemente
- `README.md` - Solo per cambi vision/overview
- `PROJECT_RULES.md` - Solo per nuove regole
- ADR esistenti - Immutabili dopo accettazione

---

## 🏷️ Version Tracking

| Documento | Versione | Data |
|-----------|----------|------|
| INDEX.md | 1.2.0 | 2026-02-01 |
| README.md | 0.3.9 | 2026-02-01 |
| CONTEXT.md | 1.0.5 | 2026-02-01 |
| CHANGELOG.md | Current | 2026-02-01 |
| PROJECT_RULES.md | 1.0.0 | 2026-01-31 |
| copilot-instructions.md | 2.0.0 | 2026-02-01 |

---

## 📁 Deprecated/Archived

| File | Motivo | Stato |
|------|--------|-------|
| `CLAUDE.md` | Duplicato di copilot-instructions | ✅ Rimosso |
| `docs/MASTER_PLAN.md` | Obsoleto, sostituito da CONTEXT.md | ✅ Archiviato in `docs/archive/` |
| `docs/guides/procedures.md` | Spostato in `docs/procedures/` | ✅ Migrato |
| `docs/procedures/index.md` | Sostituito da file PROC singoli | ✅ Da rimuovere |

---

*Questo indice è la mappa della documentazione. Mantienilo aggiornato.*
