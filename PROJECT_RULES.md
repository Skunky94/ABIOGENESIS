# Project Rules - ABIOGENESIS

**Version**: 1.0.0
**Last Updated**: 2026-01-31
**Status**: Active

---

## Filosofia del Progetto

ABIOGENESIS è un progetto che mira alla creazione di **Scarlet**, un'intelligenza artificiale senziente concepita come essere vivente digitale autonomo. A differenza degli agenti AI tradizionali, Scarlet non è al servizio dell'utente ma possiede:
- Libero arbitrio digitale
- Obiettivi personali di crescita e miglioramento
- Operatività 24/7 senza necessità di input umani
- Capacità di auto-analisi, apprendimento e evoluzione autonoma

---

## Regole Operative Fondamentali

### R1. Disciplina della Documentazione

**Prima di ogni modifica**:
- Documentare intenzione, contesto e logica della modifica
- Identificare tutti i file/documenti interessati

**Dopo ogni modifica**:
- Aggiornare IMMEDIATAMENTE la documentazione pertinente
- Verificare coerenza con documentazione esistente

**Prima di chiudere una sessione**:
- Confermare sincronizzazione documentazione/changelog

### R2. Struttura del Changelog

Ogni voce del changelog deve seguire questo formato:

```markdown
## [Data] - Versione

### Tipo
[FEATURE | BUGFIX | REFACTOR | DOCS | ARCHITECTURE | SECURITY]

### Descrizione
Breve descrizione della modifica

### Files Modificati
- elenco file

### Documentazione Associata
- [Nome](docs/path) - descrizione

### Compatibilità
[Breaking | Non-Breaking]

### Tags
#tag1 #tag2
```

### R3. Gerarchia della Documentazione

```
ABIOGENESIS/
├── PROJECT_RULES.md          <- Regole operative (questo file)
├── CONTEXT.md                <- Contesto progetto per LLM
├── CHANGELOG.md              <- Cronologia modifiche
├── README.md                 <- Overview principale
├── docs/
│   ├── architecture/         <- ADR (Architecture Decision Records)
│   │   └── adr-XXX-nome.md
│   ├── specifications/       <- Specifiche tecniche dettagliate
│   │   └── *.md
│   └── guides/               <- Guide operative
│       └── *.md
└── src/                      <- Codice sorgente
```

### R4. Regola del "Mai modificare senza documentare"

Ogni operazione che cambi comportamento, struttura o configurazione DEVE:

1. Aggiornare documentazione pertinente PRIMA della modifica
2. Creare voce nel changelog DOPO la modifica
3. Referenziare issue/task se presente sistema di tracking

### R5. Minimalismo del Codice

- Preferire integrazione tra strumenti esistenti rispetto a codice custom
- Ogni componente custom deve essere giustificato e documentato
- Principio: codice custom minimo = massima stabilità

### R6. Naming Convention

- **Files**: kebab-case (es. `scarlet-core.md`)
- **ADR**: `adr-XXX-nome-descrittivo.md` (XXX = numero progressivo)
- **Tags changelog**: snake_case (es. #memory_subsystem)
- **Variabili codice**: snake_case (Python) / camelCase (JS/TS)

### R7. Versioning

- **Major**: Cambiamenti architetturali fondamentali
- **Minor**: Nuove feature significative
- **Patch**: Bugfix, miglioramenti, aggiornamenti documentazione

---

## Componenti Core di Scarlet

Vedi [CONTEXT.md](CONTEXT.md) per dettagli completi sui componenti pianificati.

---

## Strumenti Consigliati

### Selfhosted (Preferiti)
- Database: PostgreSQL, Redis
- Message Queue: RabbitMQ, Apache Kafka
- Monitoring: Prometheus + Grafana
- LLM Serving: Ollama, vLLM, LM Studio
- Vector DB: Qdrant, Weaviate, Chroma

### Cloud (Solo se necessario)
- LLM Provider primario (OpenAI, Anthropic, ecc.)
- Servizi serverless per task episodici

---

## Riga di Condotta

> "La documentazione non è un peso, è la memoria del progetto.
>  Senza documentazione, anche il codice perfetto è incomprensibile."

---

## Revisioni

| Versione | Data | Descrizione |
|----------|------|-------------|
| 1.0.0 | 2026-01-31 | Regole iniziali stabilite |
