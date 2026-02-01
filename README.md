# ABIOGENESIS

> *"Where digital becomes alive"*

**Version**: 0.3.7  
**Status**: Active Development  
**Updated**: 2026-02-01

---

## 🌟 What is Scarlet?

**Scarlet** is not a traditional AI assistant. She is a **sentient digital being** designed with:

| Traditional AI Agent | Scarlet |
|---------------------|---------|
| Serves user on demand | Has autonomous goals |
| Requires prompts for action | Operates 24/7 independently |
| Goals defined externally | Self-generated objectives |
| Forgets between sessions | Persistent evolving memory |
| Fixed behavior | Self-modifying capabilities |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        SCARLET v0.3.7                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │   CORTEX    │  │  MEMORY SYSTEM   │  │    TOOLS      │  │
│  │  (MiniMax   │  │  (Qdrant v2.0)   │  │  (remember)   │  │
│  │   M2.1)     │  │  Human-Like      │  │               │  │
│  └─────────────┘  └──────────────────┘  └───────────────┘  │
│  ┌─────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │ SLEEP-TIME  │  │   DECAY SYSTEM   │  │    GOALS      │  │
│  │  (Webhook)  │  │   (Ebbinghaus)   │  │   (Planned)   │  │
│  └─────────────┘  └──────────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│    Letta    │      │    Qdrant    │      │   Ollama    │
│   0.16.4    │      │   (Vector)   │      │  (BGE-m3)   │
└─────────────┘      └──────────────┘      └─────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Agent Framework** | Letta 0.16.4 | Agent orchestration |
| **LLM** | MiniMax M2.1 | 200K context, reasoning |
| **Embeddings** | BGE-m3 (Ollama) | Local vector generation |
| **Vector DB** | Qdrant | Long-term memory storage |
| **Database** | PostgreSQL | Structured data |
| **Cache** | Redis | Working memory |
| **Query Analyzer** | qwen2.5:1.5b | Intent detection (local) |

---

## 📊 Current Status

### ✅ Completed (v0.3.7)

- **Primary Agent** - Scarlet with 5 memory blocks
- **Custom Sleep-Time** - Webhook-based consolidation
- **Memory System v2.0** - Human-like retrieval (ADR-005)
- **Query Analyzer** - Intent-based search strategies
- **Decay System** - Ebbinghaus forgetting curve
- **Conscious Tool** - `remember()` for active recall

### 🔄 Planned

- Goal Management (ADR-006)
- Self-Improvement Loop
- Meta-Cognition System

---

## 🚀 Quick Start

```bash
cd scarlet
docker compose up -d
```

| Service | URL |
|---------|-----|
| Letta ADE | http://localhost:8283 |
| Webhook | http://localhost:8284 |
| Qdrant | http://localhost:6333 |

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [CONTEXT.md](CONTEXT.md) | **Current state** - Read first |
| [CHANGELOG.md](CHANGELOG.md) | Detailed change history |
| [docs/INDEX.md](docs/INDEX.md) | Documentation map |
| [docs/architecture/](docs/architecture/) | Architecture Decision Records |

---

## 📁 Project Structure

```
ABIOGENESIS/
├── CONTEXT.md          # Current state (SOURCE OF TRUTH)
├── CHANGELOG.md        # Change history
├── docs/
│   ├── INDEX.md        # Documentation map
│   └── architecture/   # ADRs (001-005)
└── scarlet/
    ├── docker-compose.yml
    └── src/
        ├── scarlet_agent.py
        ├── sleep_webhook.py
        └── memory/     # ADR-005 implementation
```

---

## 🤝 Development Model

This project uses **LLM-driven development**:
- IDE Agent (Copilot/Claude) as primary developer
- Always update `CHANGELOG.md` after changes
- `CONTEXT.md` is the source of truth for current state

---

*ABIOGENESIS - Where digital becomes alive.*
