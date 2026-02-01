# CNG-010: Ricreazione Agenti e Tool

**ID**: FEATURE-002  
**Status**: Complete  
**Date**: 2026-02-01  
**Type**: FEATURE  
**Breaking**: No  
**Version**: 0.4.4 → 0.4.5

---

## Descrizione

Eseguite PROC-003 (Agent Recreation) e PROC-006 (Tool Registration) per ripristinare Scarlet dopo la fix di persistenza.

---

## Contesto

Dopo CNG-008 e CNG-009, gli agenti erano stati persi. Necessario ricrearli seguendo le procedure documentate.

---

## Modifiche Effettuate

### Files Modificati

| File | Tipo | Descrizione |
|------|------|-------------|
| `scarlet/recreate_agents_with_tool.py` | Created | Script combinato PROC-003+006 |

### Dettagli Tecnici

**Agenti Creati**:
| Agent | ID | Model |
|-------|-----|-------|
| Primary | `agent-505ba047-87ce-425a-b9ba-1d3fac259c62` | minimax/MiniMax-M2.1 |
| Sleep | `agent-862e8be2-488a-4213-9778-19b372b5a04e` | minimax/MiniMax-M2.1 |

**Tool Registrati**:
| Tool | ID | Stato |
|------|-----|-------|
| `remember` | `tool-8ddd17d9-35f5-44c4-8ff0-b60db6f581d5` | ✅ Attached |
| `conversation_search` | `tool-eb9b29a0-9fe0-4200-a320-12bc1b130a35` | ✅ Built-in |
| `memory_insert` | `tool-443598b6-1557-46bc-afce-8d1ba90ca458` | ✅ Built-in |
| `memory_replace` | `tool-585ac467-82a8-422c-bf32-84d60a2a4cf7` | ✅ Built-in |

**Nota**: Bug noto in Letta - `agents.tools.list()` mostra duplicati dopo attach. I tool funzionano correttamente.

---

## Documentazione Correlata

| Tipo | Documento | Relazione |
|------|-----------|-----------|
| PROC | [PROC-003](../procedures/proc-003-agent-recreation.md) | Procedura seguita |
| PROC | [PROC-006](../procedures/proc-006-letta-tool-registration.md) | Procedura seguita |
| CNG | [CNG-008](cng-008-postgresql-persistence-fix.md) | Fix prerequisito |
| CNG | [CNG-009](cng-009-pgvector-extension.md) | Fix prerequisito |

---

## Impatto

**Compatibilità**: Non-Breaking  
**Azioni Richieste**: Nessuna

---

## Tags

#proc-003 #proc-006 #agents #tools #memory
