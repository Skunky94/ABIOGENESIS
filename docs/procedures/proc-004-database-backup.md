# PROC-004: Backup Database

**Status**: Active  
**Version**: 1.1.0  
**Date**: 2026-02-01  
**Author**: ABIOGENESIS Team

> **Questa è una GUIDA OPERATIVA per l'IDE Agent.**
> Seguire i passi ESATTAMENTE come descritti per garantire consistenza.

---

## Scopo

Creare un backup del database PostgreSQL che contiene la memoria di Scarlet.
Questo backup è **essenziale** prima di operazioni distruttive.

---

## Quando Usare Questa Procedura

**USA questa procedura quando**:
- Stai per eseguire [PROC-003: Agent Recreation](proc-003-agent-recreation.md) ← **OBBLIGATORIO**
- Stai per fare aggiornamenti Docker importanti
- Vuoi fare manutenzione preventiva periodica
- Stai per modificare schema database o fare migrazioni

**Frequenza consigliata**: Almeno una volta a settimana, o prima di ogni operazione rischiosa.

---

## Prerequisiti

Prima di iniziare, verifica che:

1. **Docker running**: `docker ps` mostra container attivi
2. **PostgreSQL attivo**: Container `abiogenesis-postgres` in stato "Up"

Comando di verifica:
```powershell
docker ps --filter "name=abiogenesis-postgres" --format "{{.Names}}: {{.Status}}"
```

**Output atteso**: `abiogenesis-postgres: Up X minutes/hours (healthy)`

---

## Procedura Passo-Passo

### Passo 1: Vai nella directory Scarlet

**Cosa fare**: Cambia directory di lavoro

**Comando**:
```powershell
cd h:\ABIOGENESIS\scarlet
```

---

### Passo 2: Crea directory backups (se non esiste)

**Cosa fare**: Assicurati che la directory di destinazione esista

**Comando**:
```powershell
New-Item -ItemType Directory -Path "backups" -Force
```

**Output atteso**: Directory creata o già esistente

---

### Passo 3: Esegui backup SQL

**Cosa fare**: Dump completo del database

**Comando**:
```powershell
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
docker compose exec -T postgres pg_dump -U postgres letta > "backups/letta_backup_$timestamp.sql"
```

**Output atteso**: File SQL creato (nessun output a schermo se successo)

**Se fallisce**: Verifica che il container postgres sia running

---

### Passo 4: Verifica backup creato

**Cosa fare**: Controlla che il file esista e abbia contenuto

**Comando**:
```powershell
Get-ChildItem "backups" | Sort-Object LastWriteTime -Descending | Select-Object -First 3
```

**Output atteso**: Lista con il nuovo file, dimensione > 0 bytes

**IMPORTANTE**: Se la dimensione è 0, il backup è VUOTO e NON VALIDO!

---

### Passo 5: Verifica integrità database (opzionale)

**Cosa fare**: Testa che il database risponda

**Comando**:
```powershell
docker compose exec postgres psql -U postgres -d letta -c "SELECT count(*) FROM agents"
```

**Output atteso**: Numero di agenti (es. `1` o `2`)

---

## Verifica Finale

Al termine, verifica che:

1. File `backups/letta_backup_YYYYMMDD_HHMMSS.sql` esiste
2. Dimensione file > 0 bytes (tipicamente diversi MB)
3. Nome file contiene timestamp corretto

---

## Restore (Come Ripristinare)

### Da backup SQL

```powershell
cd h:\ABIOGENESIS\scarlet
docker compose exec -T postgres psql -U postgres letta < backups/letta_backup_YYYYMMDD_HHMMSS.sql
```

**Nota**: Sostituisci `YYYYMMDD_HHMMSS` con il timestamp del backup che vuoi ripristinare.

---

## Alternativa: Backup Volume Completo

Per un backup più completo (include tutto il volume Docker):

```powershell
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
docker run --rm -v scarlet_postgres_data:/data -v ${PWD}/backups:/backup alpine tar czf /backup/postgres_volume_$timestamp.tar.gz /data
```

**Restore da volume**:
```powershell
docker compose stop postgres
docker run --rm -v scarlet_postgres_data:/data -v ${PWD}/backups:/backup alpine sh -c "cd /data && tar xzf /backup/postgres_volume_YYYYMMDD.tar.gz --strip 1"
docker compose start postgres
```

---

## Troubleshooting

### Problema: File backup ha dimensione 0

**Causa**: Database vuoto o errore di connessione

**Soluzione**: Verifica container attivo e riprova:
```powershell
docker compose exec postgres psql -U postgres -d letta -c "SELECT 1"
```

---

### Problema: "Cannot connect to database"

**Causa**: Container non running

**Soluzione**: 
```powershell
docker compose up -d postgres
# Attendi 10 secondi
docker compose exec postgres psql -U postgres -d letta -c "SELECT 1"
```

---

## Note Importanti

- 💡 I backup SQL sono **più portabili** e facili da verificare
- 📌 Mantieni almeno **3 backup recenti**
- ⚠️ Elimina backup più vecchi di 30 giorni per risparmiare spazio

## Politica di Retention Consigliata

| Frequenza | Retention |
|-----------|-----------|
| Giornaliero | Ultimi 7 giorni |
| Settimanale | Ultime 4 settimane |
| Mensile | Ultimi 3 mesi |

---

## Documenti Correlati

- [PROC-003: Agent Recreation](proc-003-agent-recreation.md) - Esegui SEMPRE questa PROC prima
- [PROC-005: Docker Services Update](proc-005-docker-services-update.md)
- [ADR-004: Memory with Qdrant](../architecture/adr-004-memory-qdrant-adoption.md)

---

*PROC-004 v1.1.0 - ABIOGENESIS Project*  
*Procedura operativa per IDE Agent*
