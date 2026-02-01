# PROC-003: Recreazione Agente Letta

**Status**: Active  
**Version**: 1.1.0  
**Date**: 2026-02-01  
**Author**: ABIOGENESIS Team

> **Questa è una GUIDA OPERATIVA per l'IDE Agent.**
> Seguire i passi ESATTAMENTE come descritti per garantire consistenza.

---

## Scopo

Eliminare l'agente Scarlet esistente e ricrearlo con nuova configurazione.
Questa operazione è necessaria quando si cambiano parametri che non possono 
essere modificati a runtime (context_window, model, etc.).

---

## ⚠️ ATTENZIONE CRITICA

> **OPERAZIONE DISTRUTTIVA** - Tutta la memoria dell'agente viene **PERSA PERMANENTEMENTE**.
> 
> **PRIMA DI PROCEDERE**: Esegui [PROC-004: Database Backup](proc-004-database-backup.md)!
> 
> Se non hai il backup e qualcosa va storto, i dati sono **IRRECUPERABILI**.

---

## Quando Usare Questa Procedura

**USA questa procedura quando**:
- Hai modificato parametri di creazione in `scarlet_agent.py` (context_window, model, etc.)
- Serve un reset completo dell'agente
- L'agente è corrotto o non risponde

**NON usare** se:
- Vuoi solo modificare il prompt → usa [PROC-001](proc-001-system-prompt-update.md)
- Vuoi modificare tools → spesso basta un reload, non recreazione

---

## Prerequisiti

Prima di iniziare, verifica che:

1. **BACKUP ESEGUITO**: Hai seguito [PROC-004](proc-004-database-backup.md) ← **OBBLIGATORIO**
2. **Docker running**: `docker ps` mostra tutti i container attivi
3. **Config aggiornata**: Le modifiche sono già in `scarlet_agent.py`

---

## Procedura Passo-Passo

### Passo 1: Esegui BACKUP (OBBLIGATORIO)

**Cosa fare**: Crea backup del database PRIMA di qualsiasi altra operazione

**Comando**:
```powershell
cd h:\ABIOGENESIS\scarlet
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
docker compose exec -T postgres pg_dump -U postgres letta > "backups/letta_backup_$timestamp.sql"
```

**Output atteso**: File SQL creato in `backups/`

**Se fallisce**: NON PROCEDERE. Risolvi prima il problema di backup.

---

### Passo 2: Verifica backup creato

**Cosa fare**: Controlla che il backup esista e abbia contenuto

**Comando**:
```powershell
Get-ChildItem "backups" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
```

**Output atteso**: File con dimensione > 0 bytes

---

### Passo 3: Elimina l'agente esistente

**Cosa fare**: Esegui lo script di eliminazione

**Comando**:
```powershell
cd h:\ABIOGENESIS\scarlet
python archive/recreate_scarlet.py
```

**Quando ti chiede conferma**: Digita `yes` e premi INVIO

**Output atteso**: Messaggio di conferma eliminazione

---

### Passo 4: Verifica eliminazione

**Cosa fare**: Controlla che l'agente non esista più

**Comando**:
```powershell
python check_sleeptime.py
```

**Output atteso**: Nessun agente listato, o messaggio "No agents found"

---

### Passo 5: Crea nuovo agente

**Cosa fare**: Crea l'agente con la nuova configurazione

**Comando**:
```powershell
python -c "from src.scarlet_agent import ScarletAgent; agent = ScarletAgent(); agent.create(); print(f'Agent created: {agent.agent_id}')"
```

**Output atteso**: `Agent created: agent-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`

**IMPORTANTE**: Annota il nuovo Agent ID!

---

### Passo 6: Verifica nuovo agente

**Cosa fare**: Controlla che l'agente sia configurato correttamente

**Comando**:
```powershell
python check_sleeptime.py
```

**Output atteso**: 
- Agent ID visibile
- `context_window=200000`
- `enable_sleeptime=True`

---

### Passo 7: Aggiorna CONTEXT.md

**Cosa fare**: Aggiorna CONTEXT.md con il nuovo Agent ID

**Cerca la sezione** "Current Agent IDs" e sostituisci l'ID.

---

## Verifica Finale

Al termine, verifica che:

1. Backup esiste in `scarlet/backups/`
2. Nuovo agente risponde (check_sleeptime.py mostra dati)
3. CONTEXT.md ha il nuovo Agent ID
4. CHANGELOG.md documenta la recreazione

---

## Rollback (Ripristino da Backup)

> ⚠️ **Il rollback NON ripristina l'agente automaticamente** - ripristina solo il database.

```powershell
# Ripristina database
docker compose exec -T postgres psql -U postgres letta < backups/letta_backup_YYYYMMDD_HHMMSS.sql

# Dopo il ripristino, l'agente dovrebbe riapparire con i vecchi dati
python check_sleeptime.py
```

---

## Troubleshooting

### Problema: Script di recreazione non trova l'agente

**Causa**: Agent ID non corrisponde

**Soluzione**: Verifica l'ID in CONTEXT.md e nello script

---

### Problema: Nuovo agente non si crea

**Causa**: Errore nella configurazione

**Soluzione**: Controlla i log con:
```powershell
docker logs abiogenesis-letta --tail 50
```

---

## Note Importanti

- ⚠️ Dopo la recreazione, **tutta la memoria conversazionale è persa**
- 📌 Il webhook potrebbe aver bisogno di riconfigurazione con il nuovo agent_id
- 💡 Documenta SEMPRE il motivo della recreazione nel CHANGELOG

---

## Documenti Correlati

- [ADR-002: Scarlet Agent Setup](../architecture/adr-002-scarlet-setup.md)
- [ADR-003: Custom Sleep-Time](../architecture/adr-003-custom-sleep-time.md)
- [PROC-004: Database Backup](proc-004-database-backup.md) - **ESEGUI PRIMA**
- [CONTEXT.md](../../CONTEXT.md) - Da aggiornare dopo

---

*PROC-003 v1.1.0 - ABIOGENESIS Project*  
*Procedura operativa per IDE Agent*
