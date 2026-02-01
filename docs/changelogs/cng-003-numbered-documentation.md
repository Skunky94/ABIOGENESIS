# CNG-003: Documentazione Numerata Completa

**ID**: DOCS-003  
**Status**: Complete  
**Date**: 2026-02-01  
**Type**: DOCS  
**Breaking**: No  
**Version**: 0.3.8 → 0.4.0

---

## Descrizione

Riorganizzazione completa della documentazione in formato numerato. Ogni ADR, SPEC e PROC ora ha il proprio file con numerazione standardizzata e template dedicato.

---

## Contesto

Le procedure erano raggruppate in un unico file index.md. Serviva estrarle in file singoli con numerazione standard come gli ADR.

---

## Modifiche Effettuate

### Files Modificati

| File | Tipo | Descrizione |
|------|------|-------------|
| `docs/procedures/proc-001-system-prompt-update.md` | Created | Estratto da index.md |
| `docs/procedures/proc-002-agent-config-modification.md` | Created | Estratto da index.md |
| `docs/procedures/proc-003-agent-recreation.md` | Created | Estratto da index.md |
| `docs/procedures/proc-004-database-backup.md` | Created | Estratto da index.md |
| `docs/procedures/proc-005-docker-services-update.md` | Created | Estratto da index.md |
| `docs/procedures/proc-template.md` | Created | Template per nuove PROC |
| `docs/specifications/spec-001-memory-system-architecture.md` | Renamed | Da memory-system-architecture.md |
| `docs/specifications/spec-002-human-to-scarlet-mapping.md` | Renamed | Da human-to-scarlet-mapping.md |
| `docs/specifications/spec-003-architectural-review.md` | Renamed | Da architectural-review.md |
| `docs/specifications/spec-template.md` | Created | Template per nuove SPEC |
| `docs/INDEX.md` | Modified | v1.2.0 con link a tutti i file numerati |
| `.github/copilot-instructions.md` | Modified | v2.0.0 lista completa ADR/SPEC/PROC |
| `docs/procedures/index.md` | Deleted | Contenuto migrato in file singoli |

### Struttura Finale

```
docs/
├── architecture/           ← ADR
│   ├── adr-001 → adr-005
│   └── adr-template.md
├── specifications/         ← SPEC
│   ├── spec-001 → spec-003
│   └── spec-template.md
└── procedures/             ← PROC
    ├── proc-001 → proc-005
    └── proc-template.md
```

---

## Documentazione Correlata

| Tipo | Documento | Relazione |
|------|-----------|-----------|
| PROC | PROC-001 → PROC-005 | Procedure create |
| SPEC | SPEC-001 → SPEC-003 | Specifiche rinominate |

---

## Impatto

**Compatibilità**: Non-Breaking  
**Azioni Richieste**: Nessuna

---

## Tags

#docs #adr #spec #proc #organization #templates
