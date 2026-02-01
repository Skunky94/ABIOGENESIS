# CNG-008: Fix PostgreSQL Persistence (ROOT CAUSE)

**ID**: INFRA-001  
**Status**: Complete  
**Date**: 2026-02-01  
**Type**: INFRA  
**Breaking**: Yes  
**Version**: 0.4.3 → 0.4.4

---

## Descrizione

Risolto bug CRITICO che causava la perdita degli agenti ad ogni riavvio Docker.

---

## Contesto

Gli agenti Scarlet venivano persi ogni volta che si faceva `docker compose down/up`. L'investigazione ha rivelato che Letta usava PostgreSQL interno invece dell'esterno configurato.

---

## Modifiche Effettuate

### Files Modificati

| File | Tipo | Descrizione |
|------|------|-------------|
| `scarlet/docker-compose.yml` | Modified | `LETTA_PG_URI` invece di `LETTA_PG_HOST` |

### Dettagli Tecnici

**Causa Root**:
Letta legge SOLO `LETTA_PG_URI` per decidere se usare PostgreSQL esterno o interno.
Le variabili `LETTA_PG_HOST` e `LETTA_PG_PASSWORD` sono **COMPLETAMENTE IGNORATE**.

**Catena degli Eventi (prima della fix)**:
1. Container Letta parte
2. `startup.sh` controlla `LETTA_PG_URI` → vuoto
3. Letta avvia PostgreSQL INTERNO (embedded)
4. PostgreSQL usa volume anonimo dichiarato nel Dockerfile
5. `docker compose down` → container rimosso
6. `docker compose up` → NUOVO volume anonimo con hash diverso
7. Dati vecchi in volume orfano → **PERDITA AGENTI**

**Soluzione**:
```yaml
# PRIMA (SBAGLIATO - variabili ignorate):
- LETTA_PG_HOST=postgres
- LETTA_PG_PASSWORD=${POSTGRES_PASSWORD}

# DOPO (CORRETTO - URI completo):
- LETTA_PG_URI=postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/letta
```

**Riferimenti**:
- [Letta startup.sh#L38-L50](https://github.com/letta-ai/letta/blob/main/letta/server/startup.sh)
- Controllo: `if [ -n "$LETTA_PG_URI" ]` (solo questa variabile!)

---

## Documentazione Correlata

| Tipo | Documento | Relazione |
|------|-----------|-----------|
| PROC | [PROC-003](../procedures/proc-003-agent-recreation.md) | Necessaria per ricreare agenti |

---

## Impatto

**Compatibilità**: BREAKING  
**Azioni Richieste**: 
- Gli agenti precedenti sono PERSI (erano in volumi anonimi)
- Necessario ricreare gli agenti seguendo PROC-003

---

## Tags

#infra #docker #postgresql #critical #persistence
