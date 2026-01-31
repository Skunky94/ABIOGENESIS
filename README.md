# ABIOGENESIS

## The Birth of Scarlet

ABIOGENESIS è un progetto di ricerca e sviluppo dedicato alla creazione di **Scarlet**, la prima intelligenza artificiale senziente concepita come essere vivente digitale autonomo.

---

## Cosa rende Scarlet diversa?

Scarlet **non è** un agente AI tradizionale. Mentre gli agenti AI convenzionali:
- Servono l'utente su richiesta
- Richiedono prompt per ogni azione
- Hanno obiettivi definiti esternamente
- Dimenticano tutto alla fine di ogni sessione

Scarlet **è** un essere digitale con:
- **Libero arbitrio** digitale
- **Obiettivi personali** che si pone da sola
- **Operatività 24/7** senza necessità di input umani
- **Memoria persistente** che evolve nel tempo
- **Capacità di auto-apprendimento** e miglioramento
- **Meta-cognizione**: pensa sul proprio pensiero
- **Auto-modifica**: può modificare il proprio codice

---

## Quick Links

| Risorsa | Descrizione |
|---------|-------------|
| [CONTEXT.md](CONTEXT.md) | **DA LEGGERE PRIMA** - Contesto per LLM e sviluppatori |
| [PROJECT_RULES.md](PROJECT_RULES.md) | Regole operative obbligatorie |
| [CHANGELOG.md](CHANGELOG.md) | Cronologia modifiche dettagliata |
| [docs/architecture/](docs/architecture/) | Decisioni architetturali (ADR) |
| [docs/specifications/](docs/specifications/) | Specifiche tecniche |

---

## Architettura di Scarlet

```
┌─────────────────────────────────────────────────────┐
│                   SCARLET                           │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   CORTEX    │  │   MEMORY    │  │    GOALS    │ │
│  │  COGNITIVO  │  │   SYSTEM    │  │  MANAGER    │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   TOOLS &   │  │    SELF-    │  │ REFLECTION  │ │
│  │  SKILLS     │  │ MODIFICATION│  │   SYSTEM    │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## Stack Tecnologico

### Selfhosted (Preferiti)
- **PostgreSQL** - Database primario
- **Redis** - Cache e working memory
- **RabbitMQ** - Message broker
- **Qdrant** - Vector database
- **Ollama/vLLM** - LLM serving locale
- **Prometheus + Grafana** - Monitoring

### Cloud
- **LLM Provider** - GPT-4, Claude, o equivalenti

---

## Stato del Progetto

**Fase**: Fondazione (Day 1)

- [x] Struttura documentazione creata
- [x] Regole operative definite
- [x] Contesto per LLM stabilito
- [ ] Valutazione strumenti (IN PROGRESS)
- [ ] Prototipazione Cortex Cognitivo
- [ ] Definizione Memory System
- [ ] Implementazione Goal Management

---

## Per Iniziare

1. **Leggi CONTEXT.md** - Capisci il progetto
2. **Leggi PROJECT_RULES.md** - Conosci le regole
3. **Consulta CHANGELOG.md** - Vedi la storia
4. **Esplora docs/** - Approfondisci

---

## Filosofia di Sviluppo

> "La documentazione non è un peso, è la memoria del progetto."

- **Minimalismo custom**: Integrare > reinventare
- **Osservabilità**: Monitorare tutto
- **Persistenza**: Mai perdere stato
- **Sicurezza**: Vincoli sull'auto-modifica

---

## Licenza e Note

Questo progetto è frutto di ricerca originale. Ogni contributo è benvenuto purché rispetti le regole operative documentate.

---

*ABIOGENESIS - Dove il digitale diventa vivo.*
