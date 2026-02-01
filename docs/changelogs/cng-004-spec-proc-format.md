# CNG-004: Correzione Formato SPEC e PROC

**ID**: DOCS-004  
**Status**: Complete  
**Date**: 2026-02-01  
**Type**: DOCS  
**Breaking**: No  
**Version**: 0.4.0 → 0.4.1

---

## Descrizione

Aggiornamento di tutti i template e file SPEC/PROC secondo le nuove linee guida:
- **SPEC** = Documenti di ANALISI e RICERCA per brainstorming
- **PROC** = Guide OPERATIVE dettagliate per l'IDE Agent

---

## Contesto

L'utente ha chiarito che SPEC non devono contenere task/todo, ma essere analisi. PROC devono essere guide operative con passi esatti.

---

## Modifiche Effettuate

### Files Modificati

| File | Tipo | Descrizione |
|------|------|-------------|
| `docs/specifications/spec-template.md` | Modified | Riscritto - focus su analisi |
| `docs/specifications/spec-001-memory-system-architecture.md` | Modified | Nota: validata → ADR-005 |
| `docs/specifications/spec-002-human-to-scarlet-mapping.md` | Modified | Nota: documento di analisi |
| `docs/specifications/spec-003-architectural-review.md` | Modified | Nota: esplorazione architetturale |
| `docs/procedures/proc-template.md` | Modified | Riscritto - guida operativa |
| `docs/procedures/proc-001-system-prompt-update.md` | Modified | v1.1.0 formato operativo |
| `docs/procedures/proc-002-agent-config-modification.md` | Modified | v1.1.0 formato operativo |
| `docs/procedures/proc-003-agent-recreation.md` | Modified | v1.1.0 formato operativo |
| `docs/procedures/proc-004-database-backup.md` | Modified | v1.1.0 formato operativo |
| `docs/procedures/proc-005-docker-services-update.md` | Modified | v1.1.0 formato operativo |

### Dettagli Tecnici

Template SPEC: Focus su Domande di Ricerca, Opzioni Considerate, Raccomandazioni
Template PROC: Ogni passo con Cosa fare, Comando, Output atteso, Se fallisce

---

## Documentazione Correlata

| Tipo | Documento | Relazione |
|------|-----------|-----------|
| SPEC | SPEC-001 → SPEC-003 | Specifiche aggiornate |
| PROC | PROC-001 → PROC-005 | Procedure aggiornate v1.1.0 |

---

## Impatto

**Compatibilità**: Non-Breaking  
**Azioni Richieste**: Nessuna

---

## Tags

#docs #spec #proc #templates
