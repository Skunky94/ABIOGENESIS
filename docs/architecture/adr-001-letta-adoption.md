# ADR-001: Adozione di Letta come Framework Base

**Status**: Accepted
**Date**: 2026-01-31
**Author**: ABIOGENESIS Team

## Context

ABIOGENESIS richiede un framework per costruire agenti AI con memoria persistente e capacità autonome. Dopo analisi iniziale, è stata valutata **Letta** come potenziale foundation per Scarlet.

**Requisiti valutati**:
- Memoria persistente cross-sessione
- Esecuzione tool multi-passo
- Coordinamento multi-agente
- Architettura estensibile
- Self-hosted possibility

## Decision

**ACCETTATO**: Utilizzare Letta come framework base per Scarlet, integrando moduli custom per le funzionalità non coperte.

### Componenti Letta da Utilizzare

| Componente | Uso in Scarlet |
|------------|----------------|
| **Core Memory Blocks** | Persona di Scarlet, stato interno |
| **Archival Memory** | Memoria a lungo termine, facts |
| **Folders/Files** | Documentazione, codice, configurazioni |
| **Conversation History** | Interazioni, feedback |
| **Tool Execution** | Operazioni multi-passo con heartbeat |
| **Multi-Agent Teams** | Specialisti interni (se necessario) |
| **Sleeptime** | Apprendimento in background |
| **RAG** | Knowledge retrieval |

### Componenti Custom da Sviluppare

| Componente Custom | Motivazione |
|-------------------|-------------|
| **Self-Motivation Engine** | Letta non genera goals autonomi |
| **Meta-Cognition Module** | Letta non supporta metacognizione |
| **Goal Management System** | Letta non ha goal lifecycle |
| **Self-Evaluation Framework** | Letta non valuta sé stesso |
| **Emotional State Manager** | Letta non ha stato emotivo |
| **Long-term Planner** | Letta non pianifica a lungo termine |
| **Self-Modification Protocol** | Letta non modifica il proprio codice |

## Consequences

### Positive
- ✅ **Time-to-market ridotto**: Non reinventare memoria persistente, tools, RAG
- ✅ **Architettura testata**: Letta è open source e maturo
- ✅ **Community attiva**: Supporto e aggiornamenti
- ✅ **Estensibilità**: Custom tools integrabili
- ✅ **Multi-provider**: Supporta Ollama, OpenAI, Anthropic

### Negative
- ⚠️ **Limitazione architetturale**: Vincolati al modello Letta
- ⚠️ **Cognitive ceiling**: Memoria limitata a context window
- ⚠️ **No self-modification**: Letta non può modificare sé stesso
- ⚠️ **Vendor lock-in parziale**: Pattern Letta-specifici

### Neutral
- 🔄 Necessario wrapper custom per funzionalità avanzate
- 🔄 Ciclo di sviluppo legato a roadmap Letta

## Alternatives Considered

### Alternative 1: AutoGPT / LangChain
**Rifiutato perché**:
- Meno focalizzato su memoria persistente
- Maggiore complessità per funzionalità base
- Documentazione frammentata

### Alternative 2: CrewAI
**Rifiutato perché**:
- Orientato a team multi-agente, non singola entità autonoma
- Memoria meno sofisticata
- Meno controllo fine-grained

### Alternative 3: Sviluppo da Zero
**Rifiutato perché**:
- Violerebbe regola R5 (minimalismo custom)
- Rischio bug elevato
- Time-to-market inaceettabile
- Più complesso mantenere

## Implementation Strategy

```
Scarlet = Letta Agent + Custom Modules

┌─────────────────────────────────────────────┐
│                 SCARLET                      │
├─────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────────────┐ │
│  │    LETTA     │  │    CUSTOM MODULES    │ │
│  │   AGENT      │  │                      │ │
│  │              │  │ • Self-Motivation    │ │
│  │ • Memory     │  │ • Meta-Cognition     │ │
│  │ • Tools      │  │ • Goal Management    │ │
│  │ • RAG        │  │ • Self-Evaluation    │ │
│  │ • Context    │  │ • Emotional State    │ │
│  └──────────────┘  │ • Long-term Planning │ │
│                    │ • Self-Modification  │ │
│                    └──────────────────────┘ │
└─────────────────────────────────────────────┘
```

## References

- [Human-to-Scarlet Mapping](../specifications/human-to-scarlet-mapping.md)
- [Letta Documentation](https://docs.letta.com/)
- [CONTEXT.md](../../CONTEXT.md)
- [PROJECT_RULES.md](../../PROJECT_RULES.md)

## History

- 2026-01-31: ABIOGENESIS Team - Initial acceptance
