# Procedure Standard - ABIOGENESIS

**Version**: 1.0.0  
**Date**: 2026-01-31  
**Status**: Active  
**Purpose**: Procedure documentate e riutilizzabili

---

## Indice Procedure

1. [P-001: Aggiornamento System Prompt](#p-001-aggiornamento-system-prompt)
2. [P-002: Modifica Configurazione Agente](#p-002-modifica-configurazione-agente)
3. [P-003: Recreazione Agente Letta](#p-003-recreazione-agente-letta)
4. [P-004: Backup Database](#p-004-backup-database)
5. [P-005: Aggiornamento Docker Services](#p-005-aggiornamento-docker-services)

---

## P-001: Aggiornamento System Prompt

**Scopo**: Aggiornare il system prompt di Scarlet in modo sicuro e tracciabile

**Quando usarla**: Quando si modifica `scarlet/prompts/system.txt`

**Prerequisiti**:
- File esistente in `scarlet/prompts/system.txt`
- Permessi di scrittura sulla directory

**Passi**:

```powershell
# 1. Entrare nella directory dei prompt
cd h:\ABIOGENESIS\scarlet\prompts

# 2. Creare backup con timestamp
$timestamp = Get-Date -Format "yyyyMMdd"
Copy-Item "system.txt" "system.txt.bak"
Copy-Item "system.txt" "system.txt.$timestamp.bak"

# 3. Verificare backup
Get-ChildItem "."

# 4. Modificare il file sorgente (system.txt SOLO)
# NON creare duplicati, modificare sempre il file originale

# 5. Aggiornare changelog
# Vedere sezione dedicata nel CHANGELOG.md
```

**Verifica**:
- `system.txt` modificato con nuovi contenuti
- `system.txt.bak` contiene versione precedente
- `system.txt.20260131.bak` (o simile) backup datato esiste

**Rollback**:
```powershell
# Se qualcosa va storto
Copy-Item "system.txt.bak" "system.txt"
```

**Note**:
- Il file `.bak` viene sovrascritto ogni volta
- Il file `.YYYYMMDD.bak` mantiene versioni storiche
- MAI modificare i file `.bak`, solo il `system.txt` originale

---

## P-002: Modifica Configurazione Agente

**Scopo**: Modificare la configurazione dell'agente Scarlet in modo sicuro

**Quando usarla**: Quando si modifica `scarlet/src/scarlet_agent.py`

**Prerequisiti**:
- File esistente
- Git inizializzato (per rollback)

**Passi**:

```powershell
# 1. Verificare che Git sia aggiornato
cd h:\ABIOGENESIS
git status

# 2. Fare commit delle modifiche pendenti (se necessario)
git add .
git commit -m "Descrizione delle modifiche precedenti"

# 3. Modificare il file sorgente
# Modificare SOLO scarlet/src/scarlet_agent.py

# 4. Verificare con git diff
git diff scarlet/src/scarlet_agent.py

# 5. Testare le modifiche se possibile
# python -c "from scarlet_agent import ScarletAgent; print('OK')"

# 6. Aggiornare changelog
```

**Verifica**:
- Git mostra le modifiche correttamente
- Il codice compila/sintassi corretta
- Funzionalità testata se applicabile

**Rollback**:
```powershell
git checkout -- scarlet/src/scarlet_agent.py
```

---

## P-003: Recreazione Agente Letta

**Scopo**: Eliminare e ricreare l'agente Scarlet con nuova configurazione

**Quando usarla**: Dopo modifiche ai parametri di creazione dell'agente

**Prerequisiti**:
- Configurazione aggiornata in `scarlet_agent.py`
- Script `scarlet/recreate_scarlet.py` disponibile

**Passi**:

```powershell
# 1. Entrare nella directory Scarlet
cd h:\ABIOGENESIS\scarlet

# 2. Eseguire script di recreazione
python recreate_scarlet.py

# 3. Confermare eliminazione quando richiesto
# Digitare "yes" per confermare

# 4. Verificare che l'agente sia stato eliminato
python check_sleeptime.py
# Dovrebbe mostrare "Enable Sleep-time: True" ma senza agenti

# 5. Creare nuovo agente
python -c "from scarlet_agent import ScarletAgent; ScarletAgent().create()"

# 6. Verificare nuovo agente
python check_sleeptime.py
```

**Verifica**:
- Nuovo agente creato con ID diverso
- Parametri corretti: context_window=200000, enable_sleeptime=True
- Memory blocks presenti

**Rollback**:
- Non disponibile - la memoria dell'agente viene persa
- Per ripristinare, serve backup del database

**Nota Importante**: Questa operazione è **distruttiva** - tutta la memoria dell'agente viene persa.

---

## P-004: Backup Database

**Scopo**: Eseguire backup del database PostgreSQL

**Quando usarla**: Prima di operazioni distruttive o periodicamente

**Prerequisiti**:
- Docker Compose funzionante
- Container PostgreSQL attivo

**Passi**:

```powershell
# Backup completo (raccomandato prima di recreazione agente)
cd h:\ABIOGENESIS\scarlet

# Creare backup con timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
docker compose exec -T postgres pg_dump -U postgres letta > "backups/letta_backup_$timestamp.sql"

# Oppure backup volume
docker run --rm -v scarlet_postgres_data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/postgres_$timestamp.tar.gz /data
```

**Verifica**:
- File di backup creato
- Dimensione > 0
- Verifica integrità: `docker compose exec postgres psql -U postgres -d letta -c "SELECT 1"`

**Rollback**:
```powershell
# Ripristino da backup SQL
docker compose exec -T postgres psql -U postgres letta < backups/letta_backup_YYYYMMDD.sql
```

---

## P-005: Aggiornamento Docker Services

**Scopo**: Aggiornare i servizi Docker senza perdere dati

**Quando usarla**: Dopo modifiche a `docker-compose.yml`

**Prerequisiti**:
- File `docker-compose.yml` modificato
- Nessun servizio in stato unhealthy

**Passi**:

```powershell
# 1. Verificare stato servizi
docker compose ps

# 2. Backup volumi se necessario (vedere P-004)

# 3. Aggiornare servizi (no perdite dati)
docker compose up -d

# 4. Verificare che tutti i servizi siano running
docker compose ps

# 5. Check log per errori
docker compose logs --tail 50
```

**Verifica**:
- Tutti i container in stato "Up"
- Nessun errore nei log
- Servizio accessibile: `curl http://localhost:8283/v1/models`

**Rollback**:
```powershell
# Ritorno alla versione precedente docker-compose.yml
git checkout -- docker-compose.yml
docker compose up -d
```

---

## Checklist Pre-Modifica

Per ogni modifica a file critici, verificare:

### Prima di iniziare
- [ ] Backup creato
- [ ] Backup verificato (esiste e dimensione > 0)
- [ ] Documentazione letta
- [ ] Changelog pronto per aggiornamento

### Dopo la modifica
- [ ] File modificato correttamente
- [ ] Test/verifica effettuata
- [ ] Changelog aggiornato
- [ ] Documentazione coerente

---

## Errori Comuni e Soluzioni

| Errore | Causa | Soluzione |
|--------|-------|----------|
| Backup non creato | Path errato | Verificare directory corrente |
| File non trovato | Percorso sbagliato | Usare path assoluti |
| Permesso negato | Directory protected | Eseguire come amministratore |
| Agent non si crea | API non raggiungibile | Verificare Docker attivo |

---

## Template Procedura

Per aggiungere nuove procedure:

```markdown
## P-XXX: [Nome Procedura]

**Scopo**: [Descrizione breve]

**Quando usarla**: [Condizioni di applicazione]

**Prerequisiti**:
- [Requisito 1]
- [Requisito 2]

**Passi**:
```powershell
# Passo 1
comando

# Passo 2
comando
```

**Verifica**: [Come controllare]

**Rollback**: [Come tornare indietro]

**Note**: [Eventuali note]
```

---

*Document Version: 1.0.0*  
*Last Updated: 2026-01-31*  
*Next Review: 2026-02-07*
