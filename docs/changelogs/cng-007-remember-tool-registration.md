# CNG-007: Registrazione Tool `remember`

**Status**: Complete  
**Date**: 2026-02-01  
**Type**: FEATURE  
**Breaking**: No  
**Version**: 0.4.2 → 0.4.3

---

## Descrizione

Completato ADR-005 Phase 6 - Registrato il tool `remember` con l'agente Scarlet per ricerca conscia nella memoria.

---

## Contesto

ADR-005 richiedeva un tool `remember()` che Scarlet può invocare consciamente per cercare nella memoria a lungo termine.

---

## Modifiche Effettuate

### Files Modificati

| File | Tipo | Descrizione |
|------|------|-------------|
| `scarlet/register_remember_tool.py` | Created | Script riutilizzabile per registrazione tool |

### Dettagli Tecnici

Tool registrato:
- **Nome**: `remember`
- **ID**: `tool-ae8f3fd1-c853-4381-b342-a7ea7b59133e`
- **Funzione**: Ricerca conscia nella memoria (Query Analyzer + Multi-Strategy + Ranking)
- **Endpoint**: `/tools/remember` sul webhook

Tool collegati a Scarlet:
- `remember` - Ricerca memoria conscia (ADR-005)
- `conversation_search` - Ricerca conversazioni Letta
- `memory_insert` - Inserimento memoria Letta
- `memory_replace` - Sostituzione memoria Letta

**Nota**: Rilevato errore autenticazione LLM (MiniMax) non correlato alla registrazione.

---

## Documentazione Correlata

| Tipo | Documento | Relazione |
|------|-----------|-----------|
| ADR | [ADR-005](../architecture/adr-005-human-like-memory-system.md) | Decisione implementata |
| PROC | [PROC-006](../procedures/proc-006-letta-tool-registration.md) | Procedura seguita |

---

## Impatto

**Compatibilità**: Non-Breaking  
**Azioni Richieste**: Nessuna

---

## Tags

#adr-005 #tool #memory #letta
