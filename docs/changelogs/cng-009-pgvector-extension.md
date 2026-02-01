# CNG-009: PostgreSQL pgvector Extension

**Status**: Complete  
**Date**: 2026-02-01  
**Type**: INFRA  
**Breaking**: No  
**Version**: 0.4.4 (continued)

---

## Descrizione

Aggiunta immagine pgvector e init script per estensione vector richiesta da Letta.

---

## Contesto

Dopo aver corretto la persistenza (CNG-008), Letta falliva con errore `type "vector" does not exist` perché PostgreSQL vanilla non ha l'estensione pgvector.

---

## Modifiche Effettuate

### Files Modificati

| File | Tipo | Descrizione |
|------|------|-------------|
| `scarlet/docker-compose.yml` | Modified | Immagine `pgvector/pgvector:pg15` e mount init-db |
| `scarlet/init-db/01-init-extensions.sql` | Created | Auto-create extension vector |

### Dettagli Tecnici

Modifiche:
1. Cambiato da `postgres:15-alpine` a `pgvector/pgvector:pg15`
2. Aggiunto init script `init-db/01-init-extensions.sql`
3. Mount automatico `/docker-entrypoint-initdb.d`

```sql
-- init-db/01-init-extensions.sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## Documentazione Correlata

| Tipo | Documento | Relazione |
|------|-----------|-----------|
| CNG | [CNG-008](cng-008-postgresql-persistence-fix.md) | Fix prerequisito |

---

## Impatto

**Compatibilità**: Non-Breaking  
**Azioni Richieste**: Nessuna

---

## Tags

#infra #docker #postgresql #pgvector
