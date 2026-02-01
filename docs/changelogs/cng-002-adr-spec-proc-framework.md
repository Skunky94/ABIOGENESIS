# CNG-002: Framework Documentazione ADR/SPEC/PROC

**ID**: DOCS-002  
**Status**: Complete  
**Date**: 2026-02-01  
**Type**: DOCS  
**Breaking**: No  
**Version**: 0.3.7 → 0.3.8

---

## Descrizione

Formalizzazione del framework di documentazione numerata (ADR, SPEC, PROC) come fonte di verità per procedure e decisioni architetturali.

---

## Contesto

L'IDE Agent aveva bisogno di consultare documenti specifici prima di ogni implementazione. Serviva una struttura chiara con numerazione standard.

---

## Modifiche Effettuate

### Files Modificati

| File | Tipo | Descrizione |
|------|------|-------------|
| `.github/copilot-instructions.md` | Modified | Aggiunta sezione CRITICAL ADR/SPEC/PROC Rule |
| `docs/procedures/index.md` | Created | Migrato da docs/guides/procedures.md |
| `docs/INDEX.md` | Modified | Aggiornato v1.1.0 con sezione PROC |
| `docs/guides/procedures.md` | Deleted | Migrato a procedures/ |

### Dettagli Tecnici

Documentazione numerata attuale:
- ADR: ADR-001 → ADR-005 (architettura)
- SPEC: memory-system-architecture, human-to-scarlet-mapping
- PROC: P-001 → P-005 (procedure operative)

---

## Documentazione Correlata

| Tipo | Documento | Relazione |
|------|-----------|-----------|
| ADR | ADR-001 → ADR-005 | Documenti referenziati |

---

## Impatto

**Compatibilità**: Non-Breaking  
**Azioni Richieste**: Nessuna

---

## Tags

#docs #procedures #adr #organization
