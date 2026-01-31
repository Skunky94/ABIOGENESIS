# ADR-002: Scarlet Modulo 1 - Foundation Setup

**Status**: Accepted
**Date**: 2026-01-31
**Author**: ABIOGENESIS Team

## Context

Il progetto ABIOGENESIS ha bisogno di un setup iniziale per sviluppo e testing dell'agente Scarlet. Dopo la decisione architetturale ADR-001 di usare Letta come framework base, è necessario creare l'infrastruttura minima per:

1. Far funzionare Letta localmente
2. Configurare il LLM (MiniMax M2.1)
3. Avere un'interfaccia Python per interagire con l'agente
4. Automatizzare il setup per sviluppo

## Decision

**ACCETTATO**: Creare un setup modulare in `scarlet/` con Docker Compose per l'infrastruttura e un wrapper Python per l'interazione.

### Stack Tecnologico Confermato

| Componente | Strumento | Note |
|------------|-----------|------|
| **Agent Framework** | Letta | Foundation (ADR-001) |
| **LLM** | MiniMax M2.1 | Via OpenAI-compatible API |
| **Embeddings** | BGE-m3 | Ollama locale, GPU RTX 4070 |
| **Database** | PostgreSQL 15 | Letta default, persistente |
| **Cache** | Redis 7 | Sessioni, working memory |
| **Deployment** | Docker Compose | Locale, sviluppo |

### Struttura del Modulo

```
scarlet/
├── docker-compose.yml          # Servizi Docker (Letta, PostgreSQL, Redis)
├── .env                        # Configurazione (API keys, settings)
├── README.md                   # Quickstart guide
├── prompts/
│   └── system.txt              # System prompt - Persona Scarlet
├── scripts/
│   └── setup.sh                # Script automazione setup
├── src/
│   ├── __init__.py
│   ├── scarlet_agent.py        # Wrapper Python principale
│   └── tools/                  # Custom tools (futuro)
└── tests/
    └── __init__.py
```

### Componenti del Wrapper Python

La classe `ScarletAgent` fornisce:

| Metodo | Descrizione |
|--------|-------------|
| `create()` | Crea l'agente con system prompt |
| `chat(message)` | Invia messaggio, riceve risposta |
| `chat_stream(message)` | Risposta streaming |
| `memory_core_set(key, value)` | Imposta memoria core |
| `memory_core_get(key)` | Leggi memoria core |
| `memory_core_list()` | Lista memorie core |
| `memory_core_clear(key)` | Cancella memoria |
| `memory_archival_add(text)` | Aggiungi ad archival |
| `memory_archival_search(query)` | Cerca in archival |
| `info()` | Informazioni agente |
| `status()` | Status corrente |
| `ping()` | Verifica connessione server |
| `reset()` | Reset e ricreazione agente |

## Consequences

### Positive
- ✅ **Setup riproducibile**: Docker Compose garantisce ambiente consistente
- ✅ **Sviluppo rapido**: Wrapper Python semplifica interazione
- ✅ **Estensibilità**: Struttura modulare per futuri moduli
- ✅ **Documentazione**: Quickstart guide per nuovi sviluppatori
- ✅ **MiniMax supportato**: API compatibility confermata
- ✅ **Embeddings GPU**: BGE-m3 su RTX 4070 (1024 dim, <200MB VRAM)

### Negative
- ⚠️ **Dipendenza Docker**: Richiede Docker per sviluppo locale
- ⚠️ **Risorse sistema**: PostgreSQL + Redis + Letta consumano RAM
- ⚠️ **API key esterna**: MiniMax richiede account e pagamento

### Neutral
- 🔄 Setup può essere adattato per produzione con modifiche
- 🔄 Qdrant disabilitato per ora (attivabile se necessario)

## Alternatives Considered

### Alternative 1: Letta Cloud
**Rifiutato perché**:
- Meno controllo sull'ambiente
- Difficoltà debugging
- Costi variabili non prevedibili
- Richiede account Letta Cloud

### Alternative 2: Sviluppo senza Docker
**Rifiutato perché**:
- Configurazione complessa PostgreSQL/Redis
- Difficoltà riproducibilità ambiente
- Incompatibilità sistemi operativi

### Alternative 3: Solo Letta senza wrapper
**Rifiutato perché**:
- API Letta troppo basso livello
- Codice duplicato in ogni progetto
- Difficoltà manutenzione

## Implementation Details

### Docker Services

```yaml
letta-server:    # Agent framework API
  port: 8283
  depends_on: [postgres, redis, ollama]

postgres:        # Database persistente
  port: 5432 (internal)
  volume: postgres_data

redis:           # Cache e sessioni
  port: 6379 (internal)
  volume: redis_data

ollama:          # Embeddings locali (BGE-m3)
  port: 11434
  volumes: ollama_data
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

### Configurazione Environment

```bash
# LLM
MINIMAX_API_KEY=xxx          # LLM API key (MiniMax)
LETTA_MODEL=minimax/MiniMax-M2.1

# Server
LETTA_SERVER_URL=http://localhost:8283
POSTGRES_PASSWORD=xxx

# Embeddings (Ollama locale)
OLLAMA_BASE_URL=http://ollama:11434
```

### BGE-m3 Technical Specifications

| Parametro | Valore | Note |
|-----------|--------|------|
| **Parametri** | 566.70M | 569M ufficiali |
| **Dimensione Embedding** | 1024 | Dense vectors |
| **Context Length** | 8192 tokens | Max input |
| **Precisione** | F16 | Ottimale per qualità |
| **Pooling** | Mean Pooling | Type 2 |
| **Multi-Lingua** | 100+ lingue | Inclusa Italiana |
| **Funzionalità** | Dense retrieval | Sparse/Multi-vector via Python |

**Riferimento**: [BGE-M3 Documentation](https://bge-model.com/bge/bge_m3.html)

## References

- [ADR-001: Letta Adoption](adr-001-letta-adoption.md)
- [Letta Documentation](https://docs.letta.com/)
- [human-to-scarlet-mapping.md](../specifications/human-to-scarlet-mapping.md)
- [CONTEXT.md](../../CONTEXT.md)
- [PROJECT_RULES.md](../../PROJECT_RULES.md)

## History

- 2026-01-31: ABIOGENESIS Team - Initial acceptance
