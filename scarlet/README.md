# Scarlet - ABIOGENESIS Agent

**Version**: 0.1.0
**Status**: Modulo 1 - Foundation Setup

---

## Stato Attuale

### Container Docker
```
NAMES                   STATUS
abiogenesis-letta       Up
abiogenesis-postgres    Up (healthy)
abiogenesis-redis       Up (healthy)
```

**Nota**: Il server Letta è in esecuzione sulla porta 8283.

---

## Configurazione LLM

### Opzione 1: MiniMax (Consigliato)

1. Ottieni una API key valida da [MiniMax](https://api.minimax.chat/)
2. Aggiorna `.env`:
```bash
LETTA_MODEL=minimax/MiniMax-M2.1
LETTA_MODEL_ENDPOINT=https://api.minimax.chat/v1/text/chatcompletion_v2
MINIMAX_API_KEY=your_valid_api_key
```

### Opzione 2: OpenAI (Fallback)

```bash
LETTA_MODEL=gpt-4o
OPENAI_API_KEY=your_openai_key
```

### Opzione 3: letta-free (Richiede autenticazione)

Il server Letta include `letta/letta-free` ma richiede configurazione API key.

---

## Quick Start (quando LLM configurato)

```bash
cd scarlet

# Attiva virtual environment
source venv/Scripts/activate  # Windows
# oppure: source venv/bin/activate  # Linux/macOS

# Test Scarlet
python src/scarlet_agent.py
```

O interagisci programmaticamente:

```python
import sys
sys.path.insert(0, 'src')
from scarlet_agent import ScarletAgent

scarlet = ScarletAgent()
scarlet.create()

response = scarlet.chat("Ciao Scarlet!")
print(response)
```

---

## Risoluzione Problemi

### "Authentication failed" con LLM
- Verifica che la API key sia valida
- Per MiniMax: controlla di avere un account attivo

### Container non parte
```bash
docker compose logs abiogenesis-letta
```

### Reset completo
```bash
docker compose down
docker volume rm abiogenesis-postgres abiogenesis-redis
docker compose up -d
```

---

## Project Structure

```
scarlet/
├── docker-compose.yml     # Docker services (Letta, PostgreSQL, Redis)
├── .env                   # Configuration (API keys, settings)
├── README.md              # This file
├── prompts/
│   └── system.txt         # Scarlet's system prompt
├── scripts/
│   └── setup.sh           # Setup script
├── src/
│   ├── __init__.py
│   ├── scarlet_agent.py   # Main agent wrapper
│   └── tools/             # Custom tools (future)
└── tests/
    └── __init__.py
```

---

## Documentazione

- [CONTEXT.md](../CONTEXT.md) - Project context for LLM
- [PROJECT_RULES.md](../PROJECT_RULES.md) - Project rules
- [CHANGELOG.md](../CHANGELOG.md) - Change history
- [docs/architecture/adr-002-scarlet-setup.md](../docs/architecture/adr-002-scarlet-setup.md) - Setup ADR
