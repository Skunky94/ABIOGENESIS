# ABIOGENESIS - Documentation Index

**Version**: 1.7.0  
**Updated**: 2026-02-01  
**Maintainer**: IDE Agent (GitHub Copilot / Claude)
**Project Version**: 0.4.10

---

## 📚 Quick Reference

| Cosa cerchi? | Documento |
|--------------|-----------|
| **Panoramica progetto** | [README.md](../README.md) |
| **Stato attuale & next steps** | [CONTEXT.md](../CONTEXT.md) |
| **🗺️ Roadmap v1.0** | [ROADMAP.md](ROADMAP.md) |
| **Cronologia modifiche** | [CHANGELOG.md](../CHANGELOG.md) |
| **Dettagli changelog** | [docs/changelogs/](changelogs/) (CNG-XXX) |
| **Decisioni architetturali** | [docs/architecture/](architecture/) (ADR-XXX) |
| **Specifiche tecniche** | [docs/specifications/](specifications/) (SPEC-XXX) |
| **Procedure operative** | [docs/procedures/](procedures/) (PROC-XXX) |

> 🚨 **ROADMAP + ADR + SPEC + PROC + CNG** = Documentazione critica. Consultare SEMPRE prima di implementazioni!

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
| [ADR-006](architecture/adr-006-continuous-existence-runtime.md) | Continuous Existence Runtime | ✅ Accepted |

### Technical Specifications (/docs/specifications/)

> **Nota**: Le SPEC sono documenti di ANALISI e RICERCA. Non contengono task operativi.
> Una SPEC validata porta alla creazione di un ADR.

| SPEC | Titolo | Stato |
|------|--------|-------|
| [SPEC-001](specifications/spec-001-memory-system-architecture.md) | Memory System Architecture | ✅ Accepted → ADR-005 |
| [SPEC-002](specifications/spec-002-human-to-scarlet-mapping.md) | Mappatura Cognitiva Umano-Scarlet | 📚 Analisi di Ricerca |
| [SPEC-003](specifications/spec-003-architectural-review.md) | Architectural Review | 📚 Analisi Esplorativa |
| [SPEC-004](specifications/spec-004-continuous-existence.md) | Continuous Existence (L1) | ✅ Accepted → ADR-006 |
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
| [PROC-006](procedures/proc-006-letta-tool-registration.md) | Letta Tool Registration | Registrare tool custom con agente | v1.0.0 |
| [PROC-007](procedures/proc-007-memory-blocks-setup.md) | Memory Blocks Setup | Setup blocchi memoria per agenti | v1.0.0 |
| [proc-template](procedures/proc-template.md) | Template per nuove PROC | 📄 Template | - |

> ⚠️ **IMPORTANTE**: Prima di eseguire operazioni documentate nelle PROC, consultare SEMPRE la procedura corrispondente per garantire consistenza.

### Changelog Entries (/docs/changelogs/)

> **Nota**: I CNG sono file di DETTAGLIO per ogni voce del changelog.
> Il CHANGELOG.md principale contiene solo un indice snello con link ai CNG.

| CNG | Titolo | Tipo |
|-----|--------|------|
| [CNG-016](changelogs/cng-016-sleeping-dreaming-clarification.md) | SLEEPING/DREAMING Clarification | DOCS |
| [CNG-015](changelogs/cng-015-adr-006-continuous-existence.md) | ADR-006 L1 Runtime | DOCS |
| [CNG-014](changelogs/cng-014-spec-004-l1-complete.md) | SPEC-004 L1 Complete | DOCS |
| [CNG-013](changelogs/cng-013-production-roadmap.md) | Production Roadmap | DOCS |
| [CNG-012](changelogs/cng-012-readme-showcase.md) | README Vetrina GitHub | DOCS |
| [CNG-011](changelogs/cng-011-changelog-restructure.md) | Ristrutturazione Changelog | DOCS |
| [CNG-010](changelogs/cng-010-agent-recreation.md) | Ricreazione Agenti | FEATURE |
| [CNG-009](changelogs/cng-009-pgvector-extension.md) | pgvector Extension | INFRA |
| [CNG-008](changelogs/cng-008-postgresql-persistence-fix.md) | PostgreSQL Persistence Fix | INFRA |
| [CNG-007](changelogs/cng-007-remember-tool-registration.md) | Tool Remember | FEATURE |
| [CNG-006](changelogs/cng-006-proc-tool-registration.md) | PROC-006 Creata | DOCS |
| [CNG-005](changelogs/cng-005-version-consistency.md) | Version Consistency | DOCS |
| [CNG-004](changelogs/cng-004-spec-proc-format.md) | SPEC/PROC Format | DOCS |
| [CNG-003](changelogs/cng-003-numbered-documentation.md) | Numbered Docs | DOCS |
| [CNG-002](changelogs/cng-002-adr-spec-proc-framework.md) | ADR/SPEC/PROC Framework | DOCS |
| [CNG-001](changelogs/cng-001-documentation-restructure.md) | Documentation Restructure | DOCS |
| [cng-template](changelogs/cng-template.md) | Template per nuovi CNG | 📄 Template |

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
| Nuova feature implementata | CNG file → `CHANGELOG.md` → `CONTEXT.md` |
| Cambio architetturale | Nuovo ADR → CNG file → `CHANGELOG.md` → `CONTEXT.md` |
| Bug fix | CNG file → `CHANGELOG.md` |
| Cambio stack/tools | `README.md` → `CONTEXT.md` |
| Fine sessione | Verifica `CONTEXT.md` aggiornato |

### Ordine di Aggiornamento

```
1. docs/changelogs/cng-XXX.md  (dettagli completi)
2. CHANGELOG.md                (aggiungi riga con link al CNG)
3. CONTEXT.md                  (aggiorna stato attuale)
4. README.md                   (solo se cambia overview)
5. ADR/Specs                   (se decisione architetturale)
```

---

## 🔍 Per l'IDE Agent

### 🚨 Regola Fondamentale
**PRIMA di qualsiasi implementazione, azione o ragionamento esteso:**
1. Consulta la **ROADMAP** → Cosa è la prossima priorità?
2. Verifica se esiste una **PROC** rilevante → Seguila
3. Verifica se esiste un **ADR** rilevante → Rispettalo
4. Verifica se esiste una **SPEC** rilevante → Allineati

### Prima di Ogni Task
1. Leggi `CONTEXT.md` per stato attuale
2. Consulta `ROADMAP.md` per priorità
3. Consulta ADR/SPEC/PROC rilevanti
4. Verifica `CHANGELOG.md` per storia recente

### Dopo Ogni Task
1. Crea file CNG in `docs/changelogs/`
2. Aggiorna `CHANGELOG.md` con link al CNG
3. Aggiorna `CONTEXT.md` se cambia lo stato
4. Aggiorna `ROADMAP.md` se completi un item

### File da NON Modificare Frequentemente
- `README.md` - Solo per cambi vision/overview
- `PROJECT_RULES.md` - Solo per nuove regole
- ADR esistenti - Immutabili dopo accettazione

---

## 🗺️ Roadmap

**Location**: [ROADMAP.md](ROADMAP.md)

La roadmap definisce il percorso verso Scarlet v1.0 con 8 Layer di sviluppo:

| Layer | Focus | Status |
|-------|-------|--------|
| L0 | Foundation | ✅ COMPLETE |
| L1 | Continuous Existence | ⏳ Next |
| L2 | Self-Model | Planned |
| L3 | Reflection | Planned |
| L4 | Agency | Planned |
| L5 | Execution | Planned |
| L6 | Growth | Planned |
| L7 | Social | Planned |
| L8 | Emotional | Parallel from L3 |

**Workflow**: ROADMAP item → SPEC → ADR → Implementation → CNG

---

## 🏷️ Version Tracking

| Documento | Versione | Data |
|-----------|----------|------|
| INDEX.md | 1.5.0 | 2026-02-01 |
| README.md | 0.4.7 | 2026-02-01 |
| CONTEXT.md | 1.0.13 | 2026-02-01 |
| CHANGELOG.md | 0.4.7 | 2026-02-01 |
| ROADMAP.md | 1.0.0 | 2026-02-01 |
| PROJECT_RULES.md | 1.0.0 | 2026-01-31 |
| copilot-instructions.md | 2.1.0 | 2026-02-01 |

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
