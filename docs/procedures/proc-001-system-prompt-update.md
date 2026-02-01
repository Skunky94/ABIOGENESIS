# PROC-001: Aggiornamento System Prompt

**Status**: Active  
**Version**: 1.1.0  
**Date**: 2026-02-01  
**Author**: ABIOGENESIS Team

> **Questa è una GUIDA OPERATIVA per l'IDE Agent.**
> Seguire i passi ESATTAMENTE come descritti per garantire consistenza.

---

## Scopo

Aggiornare il system prompt di Scarlet (`scarlet/prompts/system.txt`) in modo sicuro, 
con backup automatico e tracciabilità delle modifiche.

---

## Quando Usare Questa Procedura

**USA questa procedura quando**:
- Devi modificare `scarlet/prompts/system.txt`
- Devi cambiare la personalità o le istruzioni di Scarlet
- Devi aggiungere nuove capabilities al prompt

**NON usare** se stai solo leggendo il file senza modificarlo.

---

## Prerequisiti

Prima di iniziare, verifica che:

1. **File esiste**: `Test-Path "h:\ABIOGENESIS\scarlet\prompts\system.txt"` → deve restituire `True`
2. **Directory accessibile**: Puoi scrivere nella directory prompts

---

## Procedura Passo-Passo

### Passo 1: Entra nella directory dei prompt

**Cosa fare**: Cambia directory di lavoro

**Comando**:
```powershell
cd h:\ABIOGENESIS\scarlet\prompts
```

**Output atteso**: Nessun errore, prompt cambia a `H:\ABIOGENESIS\scarlet\prompts>`

---

### Passo 2: Crea backup con timestamp

**Cosa fare**: Crea due backup - uno fisso (.bak) e uno datato

**Comando**:
```powershell
$timestamp = Get-Date -Format "yyyyMMdd"
Copy-Item "system.txt" "system.txt.bak"
Copy-Item "system.txt" "system.txt.$timestamp.bak"
```

**Output atteso**: Due file creati senza errori

**Se fallisce**: Verifica che system.txt esista con `Get-ChildItem`

---

### Passo 3: Verifica backup creati

**Cosa fare**: Controlla che i backup esistano

**Comando**:
```powershell
Get-ChildItem "system.txt*"
```

**Output atteso**: Lista con almeno 3 file (system.txt, system.txt.bak, system.txt.YYYYMMDD.bak)

---

### Passo 4: Modifica il file sorgente

**Cosa fare**: Apporta le modifiche richieste a `system.txt`

**REGOLE IMPORTANTI**:
- Modifica **SOLO** `system.txt` (il file originale)
- **MAI** creare file duplicati come `system_v2.txt`
- **MAI** modificare i file `.bak`

---

### Passo 5: Aggiorna CHANGELOG.md

**Cosa fare**: Documenta la modifica nel CHANGELOG

**Formato**:
```markdown
### PROMPT-XXX: [Breve descrizione]

**Descrizione**: [Cosa è cambiato nel prompt e perché]

**Files Modificati**:
- scarlet/prompts/system.txt

**Compatibilità**: Non-Breaking

**Tags**: #prompt #scarlet
```

---

## Verifica Finale

Al termine, verifica che:

1. `system.txt` contiene le nuove modifiche
2. `system.txt.bak` contiene la versione precedente
3. `system.txt.YYYYMMDD.bak` esiste come backup datato
4. `CHANGELOG.md` è aggiornato

---

## Rollback (Come Annullare)

Se qualcosa va storto:

```powershell
# Ripristina dalla versione precedente
Copy-Item "system.txt.bak" "system.txt" -Force
```

Per ripristinare una versione specifica datata:
```powershell
Copy-Item "system.txt.20260201.bak" "system.txt" -Force
```

---

## Note Importanti

- ⚠️ Il file `.bak` viene **sovrascritto** ad ogni esecuzione di questa procedura
- 📌 I file `.YYYYMMDD.bak` mantengono versioni storiche (non vengono sovrascritti)
- 💡 Se esegui più modifiche nello stesso giorno, il backup datato conterrà la prima versione del giorno

---

## Documenti Correlati

- [ADR-002: Scarlet Agent Setup](../architecture/adr-002-scarlet-setup.md)
- [CONTEXT.md](../../CONTEXT.md)

---

*PROC-001 v1.1.0 - ABIOGENESIS Project*  
*Procedura operativa per IDE Agent*
- [CONTEXT.md](../../CONTEXT.md)

---

*PROC-001 v1.0.0 - ABIOGENESIS Project*
