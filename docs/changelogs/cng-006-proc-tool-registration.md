# CNG-006: Procedura Registrazione Tool Letta

**Status**: Complete  
**Date**: 2026-02-01  
**Type**: DOCS  
**Breaking**: No  
**Version**: 0.4.1 → 0.4.2

---

## Descrizione

Creata PROC-006 basata sulle lezioni apprese durante la registrazione del tool `remember`.

---

## Contesto

Durante l'implementazione di ADR-005 Phase 6, sono stati scoperti diversi errori comuni nell'API Letta che meritavano documentazione.

---

## Modifiche Effettuate

### Files Modificati

| File | Tipo | Descrizione |
|------|------|-------------|
| `docs/procedures/proc-006-letta-tool-registration.md` | Created | Guida passo-passo per tool registration |

### Dettagli Tecnici

Errori documentati:
- `tools.create()` non accetta `name` (estratto da source code)
- API corretta: `agents.tools.list()` non `tools.list_for_agent()`
- Bug duplicati in Letta quando si fa attach
- Import devono essere DENTRO la funzione (sandbox)

---

## Documentazione Correlata

| Tipo | Documento | Relazione |
|------|-----------|-----------|
| ADR | [ADR-005](../architecture/adr-005-human-like-memory-system.md) | Tool `remember` implementato |
| PROC | [PROC-006](../procedures/proc-006-letta-tool-registration.md) | Procedura creata |

---

## Impatto

**Compatibilità**: Non-Breaking  
**Azioni Richieste**: Nessuna

---

## Tags

#docs #proc #letta #tools
