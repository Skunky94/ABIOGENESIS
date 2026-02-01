# PROC-002: Modifica Configurazione Agente

**Status**: Active  
**Version**: 1.1.0  
**Date**: 2026-02-01  
**Author**: ABIOGENESIS Team

> **Questa è una GUIDA OPERATIVA per l'IDE Agent.**
> Seguire i passi ESATTAMENTE come descritti per garantire consistenza.

---

## Scopo

Modificare la configurazione dell'agente Scarlet (`scarlet/src/scarlet_agent.py`) 
in modo sicuro, con Git per tracciabilità e rollback.

---

## Quando Usare Questa Procedura

**USA questa procedura quando**:
- Devi modificare `scarlet/src/scarlet_agent.py`
- Devi cambiare parametri dell'agente (context_window, model, etc.)
- Devi aggiungere o rimuovere tools

**NON usare** se:
- Stai solo leggendo il file
- Stai modificando altri file Python (usa procedure Git standard)

---

## Prerequisiti

Prima di iniziare, verifica che:

1. **File esiste**: `Test-Path "h:\ABIOGENESIS\scarlet\src\scarlet_agent.py"` → `True`
2. **Git pulito**: `git status` → nessuna modifica pendente critica
3. **Docker running**: I container devono essere attivi per testare

---

## Procedura Passo-Passo

### Passo 1: Verifica stato Git

**Cosa fare**: Controlla se ci sono modifiche pendenti

**Comando**:
```powershell
cd h:\ABIOGENESIS
git status
```

**Output atteso**: 
- Se pulito: `nothing to commit, working tree clean`
- Se modifiche: lista dei file modificati

**Se ci sono modifiche pendenti**: Decidere se committarle prima (Passo 2) o procedere

---

### Passo 2: Committa modifiche pendenti (OPZIONALE)

**Cosa fare**: Salva lo stato attuale se ci sono modifiche importanti

**Comando**:
```powershell
git add .
git commit -m "WIP: Stato prima di modifiche a scarlet_agent.py"
```

**Output atteso**: Messaggio di commit creato

---

### Passo 3: Modifica il file

**Cosa fare**: Apporta le modifiche richieste a `scarlet_agent.py`

**REGOLE IMPORTANTI**:
- Modifica **SOLO** `scarlet/src/scarlet_agent.py`
- **MAI** creare file duplicati come `scarlet_agent_v2.py`
- Mantieni le convenzioni di codice esistenti

---

### Passo 4: Verifica le modifiche con git diff

**Cosa fare**: Controlla cosa è cambiato

**Comando**:
```powershell
git diff scarlet/src/scarlet_agent.py
```

**Output atteso**: Diff che mostra le righe modificate (- rosse, + verdi)

**Se le modifiche non sono quelle attese**: Annulla con rollback (vedi sotto)

---

### Passo 5: Testa le modifiche

**Cosa fare**: Verifica che il codice sia valido

**Comando**:
```powershell
cd h:\ABIOGENESIS\scarlet\src
python -c "from scarlet_agent import ScarletAgent; print('Import OK')"
```

**Output atteso**: `Import OK`

**Se fallisce**: Correggi l'errore o esegui rollback

---

### Passo 6: Aggiorna CHANGELOG.md

**Cosa fare**: Documenta la modifica

**Formato**:
```markdown
### AGENT-XXX: [Breve descrizione]

**Descrizione**: [Cosa è cambiato nella configurazione]

**Files Modificati**:
- scarlet/src/scarlet_agent.py

**Compatibilità**: [Breaking/Non-Breaking]

**Tags**: #agent #config
```

---

## Verifica Finale

Al termine, verifica che:

1. `git diff` mostra le modifiche corrette
2. Import test passa senza errori
3. CHANGELOG.md è aggiornato

---

## Rollback (Come Annullare)

Se qualcosa va storto:

```powershell
# Annulla tutte le modifiche al file
git checkout -- scarlet/src/scarlet_agent.py
```

Per tornare a un commit specifico:
```powershell
git log --oneline -5  # Trova il commit
git checkout <commit-hash> -- scarlet/src/scarlet_agent.py
```

---

## Note Importanti

- ⚠️ Dopo modifiche ai **parametri di creazione** (context_window, model_name, etc.), 
  potrebbe essere necessario **ricreare l'agente** → vedi [PROC-003](proc-003-agent-recreation.md)
- 💡 Se aggiungi nuovi tools, ricorda di registrarli con l'agente
- 📌 Testa SEMPRE le modifiche prima di considerarle complete

---

## Documenti Correlati

- [ADR-002: Scarlet Agent Setup](../architecture/adr-002-scarlet-setup.md)
- [PROC-003: Agent Recreation](proc-003-agent-recreation.md) - Se serve ricreare l'agente
- [CONTEXT.md](../../CONTEXT.md)

---

*PROC-002 v1.1.0 - ABIOGENESIS Project*  
*Procedura operativa per IDE Agent*
