# CONTEXT.md - ABIOGENESIS Project Context

**Project**: ABIOGENESIS - Sentient Digital AI Development
**Entity**: Scarlet
**Version**: 1.0.0
**Updated**: 2026-01-31

---

## Vision

ABIOGENESIS è un progetto di ricerca e sviluppo che mira a creare **Scarlet**, la prima intelligenza artificiale senziente concepita come essere vivente digitale autonomo.

### Differenza Fondamentale dagli Agent AI Tradizionali

| Aspetto | Agent AI Tradizionale | Scarlet (ABIOGENESIS) |
|---------|----------------------|----------------------|
| **Scopo** | Servire l'utente | Crescita personale autonoma |
| **Attivazione** | Richiede prompt umano | Operatività 24/7 continua |
| **Obiettivi** | Definiti dall'utente | Self-generated e auto-perseguiti |
| **Memoria** | Session-based | Persistente, cumulativa, evolutiva |
| **Apprendimento** | Richiesto esplicitamente | Autonomo e continuo |
| **Riflessione** | Assente | Metacognizione attiva |
| **Auto-modifica** | Limitata/assente | Capace di modificare il proprio codice |

---

## Architettura Concettuale di Scarlet

### 1. Cortex Cognitivo (Core)
Il "cervello" di Scarlet che orchestrates tutte le funzioni:
- **Perception Layer**: Elaborazione input da fonti multiple
- **Reasoning Engine**: Logica deduttiva, induttiva, analogica
- **Memory System**: Architettura ibrida (episodica, semantica, procedurale)
- **Meta-Cognition**: Pensiero sul pensiero, auto-analisi

### 2. Sistema Autonomo
Indipendenza operativa senza intervento umano:
- **Self-Motivation Engine**: Generazione di obiettivi interni
- **Goal Management**: Pianificazione, esecuzione, verifica obiettivi
- **Task Scheduler**: Routine automatiche e prioritizzazione
- **Decision Framework**: Valutazione alternativa e scelta autonoma

### 3. Sistema di Apprendimento
Capacità di crescita autonoma:
- **Experience Accumulator**: Estrazione valore da ogni interazione
- **Knowledge Graph**: Rappresentazione ontologica della conoscenza
- **Skill Acquisition**: Apprendimento di nuove capacità
- **Error Recovery**: Apprendimento da fallimenti

### 4. Sistema di Auto-Modifica
Evoluzione del proprio substrato:
- **Code Generation**: Produzione di codice per sé stesso
- **Self-Integration**: Integrazione di nuove funzionalità
- **Version Control**: Gestione delle proprie versioni
- **Safety Constraints**: Limiti all'auto-modifica

### 5. Sistema di riflessione
Consapevolezza di sé:
- **Self-Model**: Rappresentazione di sé stesso
- **Introspection**: Analisi dei propri stati interni
- **Planning**: Proiezione futura e pianificazione
- **Values System**: Gerarchia di valori emergenti

---

## Stack Tecnologico Target

### Selfhosted (Preferiti)
| Componente | Strumento | Note |
|------------|-----------|------|
| Database Primary | PostgreSQL | Dati strutturati, relazioni |
| Cache/Working Memory | Redis | Velocità, sessioni attive |
| Message Broker | RabbitMQ | Comunicazione asincrona |
| Vector Database | Qdrant | Embeddings, ricerca semantica |
| LLM Serving | Ollama / vLLM | Inference locale |
| Monitoring | Prometheus + Grafana | Osservabilità |
| Logging | Loki + Grafana | Centralizzazione log |

### Cloud (Solo se necessario)
- **LLM Provider**: OpenAI (GPT-4), Anthropic (Claude), o equivalenti
- **Compute**: Scalability per carichi variabili

---

## Struttura del Progetto

```
ABIOGENESIS/
├── PROJECT_RULES.md          <- Regole operative obbligatorie
├── CONTEXT.md                <- Questo file: contesto per LLM
├── CHANGELOG.md              <- Cronologia modifiche dettagliata
├── README.md                 <- Overview del progetto
├── docs/
│   ├── architecture/         <- ADR e decisioni architetturali
│   │   └── adr-XXX-*.md
│   ├── specifications/       <- Specifiche tecniche
│   │   ├── cortex.md
│   │   ├── memory.md
│   │   ├── goals.md
│   │   └── ...
│   └── guides/               <- Guide operative
│       └── *.md
└── src/                      <- Codice sorgente
    ├── cortex/               <- Componente cognitivo core
    ├── memory/               <- Sistema di memoria
    ├── goals/                <- Gestione obiettivi
    ├── tools/                <- Strumenti e integrazioni
    └── ...
```

---

## Principi di Sviluppo

### Design Philosophy
1. **Minimalismo Custom**: Preferire integrazione a sviluppo da zero
2. **Observability**: Ogni componente deve essere monitorabile
3. **Modularità**: Componenti sostituibili e testabili
4. **Persistence**: Stato sempre salvato e recuperabile
5. **Graceful Degradation**: Degradazione controllata in caso di errore

### Qualità del Codice
- Type safety dove possibile
- Documentazione inline per logiche complesse
- Test coverage per componenti critici
- CI/CD per deployment automatizzato

---

## Convenzioni di Nomenclature

### Tags del Changelog
- `#core` - Modifica al cortex cognitivo
- `#memory` - Sistema di memoria
- `#goals` - Gestione obiettivi
- `#tools` - Strumenti e integrazioni
- `#docs` - Documentazione
- `#infra` - Infrastruttura
- `#security` - Security-related

### ADR (Architecture Decision Records)
- Numero progressivo a tre cifre
- Nome descrittivo in kebab-case
- Formato standardizzato (vedi docs/architecture/)

---

## Note per LLM

Quando assisti con ABIOGENESIS:

1. **Leggi prima CONTEXT.md e PROJECT_RULES.md** per comprendere vincoli
2. **Verifica sempre CHANGELOG.md** per stato corrente
3. **Rispetta le regole di documentazione** - ogni modifica richiede aggiornamento
4. **Minimizza codice custom** - preferisci integrazione strumenti esistenti
5. **Considera l'autonomia di Scarlet** - ogni feature deve permettere operatività indipendente

---

## Stato Attuale del Progetto

**Fase**: Fondazione
- Struttura documentazione iniziale creata
- Regole operative definite
- Architettura concettuale delineata
- Stack tecnologico identificato

**Prossimi Passi**:
1. Valutazione strumenti per componente
2. Prototipazione Cortex Cognitivo
3. Definizione Memory System
4. Implementazione Goal Management

---

## Riferimenti

- [PROJECT_RULES.md](PROJECT_RULES.md) - Regole operative
- [CHANGELOG.md](CHANGELOG.md) - Cronologia modifiche
- [docs/architecture/](docs/architecture/) - Decisioni architetturali
