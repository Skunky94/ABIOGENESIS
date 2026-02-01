# CNG-011: Ristrutturazione Sistema Changelog

**Data**: 2026-02-01  
**Tipo**: DOCS  
**Versione**: 0.4.6  
**Breaking**: No

---

## Descrizione

Ristrutturazione completa del sistema di gestione changelog secondo nuovo formato numerato CNG (Changelog).

## Problema

Il CHANGELOG.md monolitico aveva raggiunto ~2000 righe, rendendo difficile:
- Navigazione rapida
- Ricerca di cambiamenti specifici
- Comprensione della cronologia
- Manutenzione

## Soluzione Implementata

### Nuovo Sistema CNG

Introdotto sistema di documentazione numerata parallelo a ADR/SPEC/PROC:

| Tipo | Location | Scopo |
|------|----------|-------|
| **ADR** | `docs/architecture/` | Decisioni architetturali |
| **SPEC** | `docs/specifications/` | Specifiche tecniche |
| **PROC** | `docs/procedures/` | Procedure operative |
| **CNG** | `docs/changelogs/` | **Entry changelog dettagliate** |

### Struttura

```
docs/changelogs/
├── cng-template.md           # Template per nuovi CNG
├── cng-001-documentation-restructure.md
├── cng-002-adr-spec-proc-framework.md
├── ...
└── cng-011-changelog-restructure.md
```

### Formato CHANGELOG.md Principale

Da monolitico a **index snello con link**:

```markdown
## 2026-02-01

| ID | Change | Descrizione |
|----|--------|-------------|
| [CNG-011] | **DOCS: Restructure** | Sistema CNG |
| [CNG-010] | **FEATURE: Agents** | Ricreazione |
```

## Files Modificati

- `CHANGELOG.md` - Riscritto in formato snello
- `.github/copilot-instructions.md` - Aggiunte regole CNG
- `docs/INDEX.md` - Aggiunta sezione changelogs

## Files Creati

- `docs/changelogs/cng-template.md`
- `docs/changelogs/cng-001-documentation-restructure.md`
- `docs/changelogs/cng-002-adr-spec-proc-framework.md`
- `docs/changelogs/cng-003-numbered-documentation.md`
- `docs/changelogs/cng-004-spec-proc-format.md`
- `docs/changelogs/cng-005-version-consistency.md`
- `docs/changelogs/cng-006-proc-tool-registration.md`
- `docs/changelogs/cng-007-remember-tool-registration.md`
- `docs/changelogs/cng-008-postgresql-persistence-fix.md`
- `docs/changelogs/cng-009-pgvector-extension.md`
- `docs/changelogs/cng-010-agent-recreation.md`
- `docs/changelogs/cng-011-changelog-restructure.md`

## Vantaggi

1. **Navigazione**: Indice snello per overview rapida
2. **Dettaglio**: CNG files per informazioni complete
3. **Consistenza**: Stesso formato di ADR/SPEC/PROC
4. **Manutenibilità**: File piccoli e focalizzati
5. **Ricerca**: Facilmente greeppabile

## Regole Operative

### Quando creare un CNG

- Ogni change significativo → nuovo CNG
- Gruppi di change correlati → unico CNG
- Bug fix minori → possono essere raggruppati

### Naming Convention

```
cng-XXX-short-description.md
```

- `XXX`: Numero sequenziale a 3 cifre
- `short-description`: Descrizione in kebab-case

### Contenuto Minimo CNG

1. Data e tipo
2. Descrizione breve
3. Files modificati
4. Compatibilità

---

**Tags**: #docs #changelog #organization #cng
