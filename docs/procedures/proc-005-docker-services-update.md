# PROC-005: Aggiornamento Docker Services

**Status**: Active  
**Version**: 1.1.0  
**Date**: 2026-02-01  
**Author**: ABIOGENESIS Team

> **Questa è una GUIDA OPERATIVA per l'IDE Agent.**
> Seguire i passi ESATTAMENTE come descritti per garantire consistenza.

---

## Scopo

Aggiornare i servizi Docker dopo modifiche a `docker-compose.yml` senza perdere dati.

---

## Quando Usare Questa Procedura

**USA questa procedura quando**:
- Hai modificato `docker-compose.yml`
- Devi aggiornare immagini Docker
- Devi cambiare configurazioni di rete o volumi
- Devi aggiungere o rimuovere servizi

**NON usare** se:
- Vuoi solo vedere lo stato dei container → usa `docker compose ps`
- Vuoi solo vedere i log → usa `docker compose logs`

---

## Prerequisiti

Prima di iniziare, verifica che:

1. **File valido**: `docker-compose.yml` modificato e sintatticamente corretto
2. **Servizi stabili**: Nessun servizio in stato "unhealthy" o "restarting"
3. **Backup** (se modifiche rischiose): Segui [PROC-004](proc-004-database-backup.md)

---

## Procedura Passo-Passo

### Passo 1: Vai nella directory Scarlet

**Cosa fare**: Cambia directory di lavoro

**Comando**:
```powershell
cd h:\ABIOGENESIS\scarlet
```

---

### Passo 2: Verifica stato servizi attuali

**Cosa fare**: Controlla lo stato di tutti i container

**Comando**:
```powershell
docker compose ps
```

**Output atteso**: Lista di container, tutti in stato "Up"

**Se vedi "unhealthy"**: Risolvi prima il problema del servizio

---

### Passo 3: Valida docker-compose.yml

**Cosa fare**: Verifica che il file sia sintatticamente corretto

**Comando**:
```powershell
docker compose config --quiet
```

**Output atteso**: **Nessun output** = file valido

**Se ci sono errori**: Correggi il file prima di procedere

---

### Passo 4: Aggiorna i servizi

**Cosa fare**: Applica le modifiche

**Comando**:
```powershell
docker compose up -d
```

**Output atteso**: Messaggi di container creati/aggiornati

---

### Passo 5: Verifica che tutti i servizi siano running

**Cosa fare**: Controlla stato post-aggiornamento

**Comando**:
```powershell
docker compose ps
```

**Output atteso**:
```
NAME                        STATUS
abiogenesis-letta           Up (healthy)
abiogenesis-ollama          Up (healthy)
abiogenesis-postgres        Up (healthy)
abiogenesis-qdrant          Up (healthy)
abiogenesis-redis           Up (healthy)
abiogenesis-sleep-webhook   Up (healthy)
```

**Se qualcosa non è "Up"**: Vedi sezione Troubleshooting

---

### Passo 6: Controlla log per errori

**Cosa fare**: Verifica che non ci siano errori nei log recenti

**Comando**:
```powershell
docker compose logs --tail 30
```

**Output atteso**: Nessun errore critico (ERROR, FATAL)

---

### Passo 7: Verifica accessibilità servizi

**Cosa fare**: Testa che le API rispondano

**Comandi**:
```powershell
# Letta API
curl http://localhost:8283/v1/health

# Webhook
curl http://localhost:8284/health

# Qdrant
curl http://localhost:6333/collections
```

**Output atteso**: Risposta JSON o "ok" da ogni endpoint

---

## Verifica Finale

Al termine, verifica che:

1. Tutti i container sono in stato "Up"
2. Tutti i container con healthcheck sono "healthy"
3. Nessun errore critico nei log
4. Gli endpoint health rispondono
5. CHANGELOG.md è aggiornato (se modifica significativa)

---

## Rollback (Come Annullare)

### Se qualcosa non funziona

```powershell
# Ritorna alla versione precedente del file
git checkout -- docker-compose.yml

# Riapplica
docker compose up -d
```

### Se serve rollback completo

```powershell
# Ferma tutti i servizi
docker compose down

# Checkout versione precedente
git checkout HEAD~1 -- docker-compose.yml

# Riavvia
docker compose up -d
```

---

## Troubleshooting

### Problema: Container non parte

**Comando diagnostico**:
```powershell
docker compose logs <nome-servizio>
```

**Causa comune**: Errore configurazione o dipendenza mancante

---

### Problema: "Port already in use"

**Comando diagnostico**:
```powershell
netstat -ano | findstr :<PORT>
```

**Soluzione**: Termina il processo che usa la porta o cambia porta nel docker-compose.yml

---

### Problema: Healthcheck failing

**Causa comune**: Servizio lento a partire

**Soluzione**: Aumenta `start_period` nel healthcheck del servizio

---

### Problema: Volume not found

**Causa**: Nome volume cambiato

**Soluzione**: Verifica i nomi volumi in docker-compose.yml siano consistenti

---

## Note Importanti

- ⚠️ I volumi Docker **persistono** anche con `docker compose down`
- 🚨 **MAI** usare `docker compose down -v` a meno che tu voglia **ELIMINARE TUTTI I DATI**
- 📌 Aggiorna CONTEXT.md se cambiano porte o configurazioni significative

---

## Documenti Correlati

- [PROC-004: Database Backup](proc-004-database-backup.md) - Esegui prima se modifiche rischiose
- [ADR-001: Letta Framework Adoption](../architecture/adr-001-letta-adoption.md)
- [CONTEXT.md](../../CONTEXT.md)

---

*PROC-005 v1.1.0 - ABIOGENESIS Project*  
*Procedura operativa per IDE Agent*
