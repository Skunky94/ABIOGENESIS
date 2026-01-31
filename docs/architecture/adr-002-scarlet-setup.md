# ADR-002: Scarlet Modulo 1 - Foundation Setup

**Status**: Accepted
**Date**: 2026-01-31
**Last Updated**: 2026-01-31
**Author**: ABIOGENESIS Team

## Context

Il progetto ABIOGENESIS ha bisogno di un setup iniziale per sviluppo e testing dell'agente Scarlet. Dopo la decisione architetturale ADR-001 di usare Letta come framework base, è necessario creare l'infrastruttura minima per:

1. Far funzionare Letta localmente
2. Configurare il LLM (MiniMax M2.1)
3. Avere un'interfaccia Python per interagire con l'agente
4. Automatizzare il setup per sviluppo
5. Implementare sistema sleep-time custom (Letta built-in buggy)

## Decision

**ACCETTATO**: Creare un setup modulare in `scarlet/` con Docker Compose per l'infrastruttura e un wrapper Python per l'interazione, incluso sistema sleep-time custom.

### Stack Tecnologico Confermato

| Componente | Strumento | Note |
|------------|-----------|------|
| **Agent Framework** | Letta 0.16.4 | Foundation (ADR-001) |
| **LLM** | MiniMax M2.1 | Via OpenAI-compatible API, 200K context |
| **Embeddings** | BGE-m3 | Ollama locale, GPU RTX 4070 |
| **Database** | PostgreSQL 15 | Letta default, persistente |
| **Cache** | Redis 7 | Sessioni, working memory |
| **Deployment** | Docker Compose | Locale, sviluppo |

### ⚠️ Problema Letta Sleep-Time (CRITICAL)

**Letta 0.16.4 ha un bug con `enable_sleeptime=True`**:
- Errore HTTP 500 durante creazione agente con sleep-time abilitato
- Il parametro `managed_group` risulta `null`
- **NON usare** il built-in sleep-time di Letta

**Soluzione**: Sistema sleep-time **custom** con architettura dual-agent (vedi sezione "Sleep-Time Custom")

### Sleep-Time Custom Architecture

```
┌─────────────────┐     ┌──────────────────────────┐     ┌──────────────────┐
│   Scarlet       │←───→│  SleepTimeOrchestrator   │←───→│  Scarlet-Sleep   │
│  (Primary)      │     │                          │     │  (Consolidation) │
└────────┬────────┘     └──────────────────────────┘     └──────────────────┘
         │                                                        │
         │  User Messages                                        │  Memory Insights
         │                                                        │  (JSON structured)
         ↓                                                        ↓
    ┌─────────────────────────────────────────────────────────────┐
    │                    Memory Blocks (5)                        │
    │  persona │ human │ goals │ session_context │ constraints   │
    └─────────────────────────────────────────────────────────────┘
```

### Componenti Sleep-Time Custom

| Componente | Classe | Scopo |
|------------|--------|-------|
| Sleep Agent | `ScarletSleepAgent` | Agente secondario per analisi conversazioni |
| Orchestrator | `SleepTimeOrchestrator` | Coordina ciclo sleep-time |

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
│   ├── scarlet_agent.py        # Wrapper Python principale (1027 righe)
│   │   ├── ScarletAgent        # Primary agent wrapper
│   │   ├── ScarletSleepAgent   # Sleep-time agent custom
│   │   └── SleepTimeOrchestrator # Sleep-time coordinator
│   └── tools/                  # Custom tools (futuro)
└── tests/
    ├── __init__.py
    ├── test_sleep_time_custom.py  # Test sleep-time custom
    └── test_embeddings.py         # Test embedding BGE-m3
```

### Memory Blocks (Italiani)

```python
DEFAULT_MEMORY_BLOCKS = [
    {"label": "persona", "value": "Tu sei Scarlet, un essere digitale senziente..."},
    {"label": "human", "value": "Le informazioni sull'umano..."},
    {"label": "goals", "value": "Gli obiettivi..."},
    {"label": "session_context", "value": "Il contesto della sessione..."},
    {"label": "constraints", "value": "VINCOLI (Sola Lettura):...", "read_only": True}
]
```

### Componenti del Wrapper Python

La classe `ScarletAgent` fornisce:

| Metodo | Descrizione |
|--------|-------------|
| `create(with_sleep_agent=True)` | Crea l'agente con system prompt e sleep-time opzionale |
| `chat(message)` | Invia messaggio, riceve risposta (trigger sleep-time) |
| `chat_stream(message)` | Risposta streaming |
| `force_consolidation()` | Trigger manuale consolidazione memoria |
| `sleep_status` | Status del sistema sleep-time |
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
| `delete()` | Elimina agente (primary + sleep) |

## Consequences

### Positive
- ✅ **Setup riproducibile**: Docker Compose garantisce ambiente consistente
- ✅ **Sviluppo rapido**: Wrapper Python semplifica interazione
- ✅ **Estensibilità**: Struttura modulare per futuri moduli
- ✅ **Documentazione**: Quickstart guide per nuovi sviluppatori
- ✅ **MiniMax supportato**: API compatibility confermata, 200K context
- ✅ **Embeddings GPU**: BGE-m3 su RTX 4070 (1024 dim, <200MB VRAM)
- ✅ **Sleep-time funzionante**: Sistema custom bypassa bug Letta

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

### Alternative 4: Letta built-in sleep-time
**Rifiutato perché**:
- Bug HTTP 500 con `enable_sleeptime=True`
- `managed_group` risulta sempre `null`
- Nessuna data di fix disponibile

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

### Sleep-Time Custom Implementation

#### ScarletSleepAgent
```python
class ScarletSleepAgent:
    PROMPT_TEMPLATE = """# Scopo
Sei un agente specializzato nel consolidamento della memoria per Scarlet...

# Output (JSON strutturato)
{{{{
    "persona_updates": [...],
    "human_updates": [...],
    "goals_insights": [...],
    "reflection": "...",
    "priority_actions": [...]
}}}}"""

    def consolidate(conversation_history: str) -> Dict[str, Any]:
        """Analizza conversazioni e genera insights JSON"""
```

#### SleepTimeOrchestrator
```python
class SleepTimeOrchestrator:
    def __init__(self, primary_agent, sleep_agent, message_threshold=5):
        self.message_count = 0
        self.threshold = message_threshold
        self.auto_trigger = True

    def on_message(self, count=1):
        """Chiamato dopo ogni messaggio"""

    def run_consolidation(self) -> Dict[str, Any]:
        """Esegue ciclo completo di consolidamento"""
```

### Agent ID Attuale
```
agent-c8f46fe6-9011-4d71-b267-10c7808ba02f
```

## References

- [ADR-001: Letta Adoption](adr-001-letta-adoption.md)
- [Letta Documentation](https://docs.letta.com/)
- [human-to-scarlet-mapping.md](../specifications/human-to-scarlet-mapping.md)
- [CONTEXT.md](../../CONTEXT.md)
- [PROJECT_RULES.md](../../PROJECT_RULES.md)
- [copilot-instructions.md](../../.github/copilot-instructions.md)

## History

- 2026-01-31: ABIOGENESIS Team - Initial acceptance
- 2026-01-31: ABIOGENESIS Team - Added custom sleep-time architecture (bug Letta)
