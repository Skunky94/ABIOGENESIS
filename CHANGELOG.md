# CHANGELOG - ABIOGENESIS

**Project**: ABIOGENESIS - Sentient Digital AI Development
**Entity**: Scarlet
**Version**: 0.1.0

---

## 2026-01-31 - Foundation Established

### Documentazione Iniziale

In questo momento fondativo, è stata stabilita la struttura documentativa base del progetto ABIOGENESIS. Tutti i file di documentazione sono stati creati per garantire tracciabilità, contesto e regole operative per ogni sviluppo futuro.

#### Modifiche Documentazione

##### DOCS-001: Struttura Directory Creata
**Descrizione**: Creata la struttura delle directory per il progetto con cartelle organizzate per tipo di contenuto.

**Files Creati**:
- `docs/architecture/` - Directory per Architecture Decision Records
- `docs/specifications/` - Directory per specifiche tecniche
- `docs/guides/` - Directory per guide operative
- `src/` - Directory per codice sorgente

**Tags**: #docs #infra

---

##### DOCS-002: PROJECT_RULES.md Creato
**Descrizione**: Definito il documento delle regole operative che governano tutto lo sviluppo del progetto. Questo file è la "costituzione" di ABIOGENESIS.

**Contenuto**:
- Filosofia del progetto e visione di Scarlet
- 7 regole operative fondamentali
- Convenzioni di naming e versioning
- Gerarchia della documentazione
- Formato standard del changelog
- Linee guida per minimalismo del codice
- Elenco strumenti consigliati (selfhosted preferiti)

**Documentazione Associata**:
- [CONTEXT.md](CONTEXT.md) - Contesto per LLM (riferimento incrociato)
- [docs/guides/](docs/guides/) - Guide da sviluppare

**Compatibilità**: Non-Breaking (documentazione iniziale)

**Tags**: #docs #rules #governance

---

##### DOCS-003: CONTEXT.md Creato
**Descrizione**: Creato il documento di contesto primario che serve come riferimento per ogni LLM che lavora sul progetto. Questo file è obbligatorio da leggere PRIMA di ogni intervento.

**Contenuto**:
- Visione del progetto e differenza da agenti AI tradizionali
- Architettura concettuale di Scarlet (5 sistemi principali)
- Stack tecnologico target (selfhosted + cloud)
- Struttura del progetto con mappa file
- Principi di sviluppo e qualità del codice
- Convenzioni di nomenclature (tags, ADR)
- Note operative per LLM
- Stato attuale e prossimi passi

**Documentazione Associata**:
- [PROJECT_RULES.md](PROJECT_RULES.md) - Regole operative (riferimento obbligatorio)
- [CHANGELOG.md](CHANGELOG.md) - Cronologia (da consultare sempre)

**Compatibilità**: Non-Breaking (documentazione iniziale)

**Tags**: #docs #context #llm #onboarding

---

##### DOCS-004: README.md Creato
**Descrizione**: Creato il file principale di overview del progetto, il "volto" di ABIOGENESIS per visitatori e primi approcci.

**Contenuto**:
- Visione del progetto in breve
- Differenza tra Scarlet e agenti AI tradizionali (tabella comparativa)
- Quick links ai documenti principali
- Diagramma architettura di Scarlet
- Stack tecnologico (selfhosted/cloud)
- Stato attuale del progetto
- Filosofia di sviluppo

**Documentazione Associata**:
- [CONTEXT.md](CONTEXT.md) - Contesto completo (da leggere dopo README)
- [PROJECT_RULES.md](PROJECT_RULES.md) - Regole operative

**Compatibilità**: Non-Breaking (documentazione iniziale)

**Tags**: #docs #readme #overview

---

##### DOCS-005: Template ADR Creato
**Descrizione**: Creato il template standard per Architecture Decision Records nella directory docs/architecture/. Ogni decisione architetturale significativa dovrà seguire questo formato.

**Contenuto Template**:
- Status (Proposed/Accepted/Deprecated/Rejected)
- Context e problema
- Decisione presa
- Consequences (positive/negative/neutral)
- Alternatives considered
- References e history

**Files Creati**:
- `docs/architecture/adr-template.md` - Template ADR standard

**Documentazione Associata**:
- [CONTEXT.md](CONTEXT.md) - Convenzioni nomenclature ADR
- [PROJECT_RULES.md](PROJECT_RULES.md) - Regole generali

**Compatibilità**: Non-Breaking (documentazione iniziale)

**Tags**: #docs #architecture #adr #template

---

## Formato Voce Changelog

Per mantenere coerenza, ogni modifica futura dovrà seguire questo formato:

```markdown
### [CODICE] - Titolo Descrittivo

**Descrizione**: Descrizione dettagliata della modifica

**Files Modificati/Creati**:
- elenco file

**Documentazione Associata**:
- [Nome](path) - descrizione
- ...

**Compatibilità**: [Breaking | Non-Breaking]

**Tags**: #tag1 #tag2
```

### Codici Tipo Modifica

| Codice | Significato |
|--------|-------------|
| FEATURE | Nuova funzionalità |
| BUGFIX | Correzione bug |
| REFACTOR | Ristrutturazione codice |
| ARCHITECTURE | Cambiamento architetturale |
| DOCS | Modifica documentazione |
| INFRA | Modifica infrastruttura |
| SECURITY | Modifica sicurezza |

---

## Prossime Modifiche Attese

- Valutazione strumenti per componente
- Scelta stack tecnologico finale
- Prototipazione Cortex Cognitivo
- Definizione Memory System
- Implementazione Goal Management

---

*Questo changelog è parte integrante del progetto. Ogni modifica deve essere documentata qui PRIMA di essere considerata completa.*
