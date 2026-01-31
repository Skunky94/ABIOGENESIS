# ADR-003: Custom Sleep-Time Architecture

**Status**: Accepted
**Date**: 2026-01-31
**Author**: ABIOGENESIS Team

## Context

Durante l'implementazione del Modulo 1 (Foundation), è emerso che Letta 0.16.4 presenta un bug critico con il sistema sleep-time built-in. Questo ADR documenta la decisione di implementare un sistema sleep-time custom alternativo.

### Problema Identificato

**Letta 0.16.4 - Bug Sleep-Time**:
```
HTTP 500: Internal Server Error durante creazione agente con enable_sleeptime=True
```

**Dettagli del bug**:
1. Chiamata `client.agents.create({"enable_sleeptime": True})` → HTTP 500
2. Se creato senza sleep-time e abilitato via PATCH:
   - Sleep-time sembra abilitato
   - Ma `managed_group` risulta `null`
   - Funzionalità non operativa

**Impatto**:
- Bloccante per l'operatività 24/7 di Scarlet
- Nessuna data di fix disponibile dalla community Letta

## Decision

**ACCETTATO**: Implementare sistema sleep-time **custom** con architettura dual-agent

### Architettura Proposta

```
┌─────────────────┐     ┌──────────────────────────┐     ┌──────────────────┐
│   Scarlet       │←───→│  SleepTimeOrchestrator   │←───→│  Scarlet-Sleep   │
│  (Primary)      │     │                          │     │  (Consolidation) │
└────────┬────────┘     └──────────────────────────┘     └──────────────────┘
         │                                                        │
         │  User Messages                                        │  Memory Insights
         │  (1 messaggio = on_message())                         │  (JSON strutturato)
         ↓                                                        ↓
    ┌─────────────────────────────────────────────────────────────┐
    │                    Memory Blocks (5)                        │
    │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────────┐   │
    │  │ persona │ │  human  │ │  goals  │ │ session_context │   │
    │  └─────────┘ └─────────┘ └─────────┘ └─────────────────┘   │
    │  ┌─────────┐                                               │
    │  │constraints│ (read-only)                                 │
    │  └─────────┘                                               │
    └─────────────────────────────────────────────────────────────┘
```

### Componenti

| Componente | Classe Python | Linee | Scopo |
|------------|---------------|-------|-------|
| Primary Agent | `ScarletAgent` | ~500 | Agente principale per interazioni utente |
| Sleep Agent | `ScarletSleepAgent` | ~180 | Agente secondario per analisi conversazioni |
| Orchestrator | `SleepTimeOrchestrator` | ~175 | Coordina ciclo sleep-time |

### Flusso Operativo

1. **Creazione Agente**:
   ```python
   scarlet = ScarletAgent()
   scarlet.create(with_sleep_agent=True)
   ```
   → Crea 2 agenti: Scarlet (primary) + Scarlet-Sleep (secondary)

2. **Chat Normale**:
   ```python
   response = scarlet.chat("Ciao!")
   ```
   → Invia a primary agent → Risposta → `orchestrator.on_message(1)`

3. **Trigger Sleep-Time**:
   - Contatore messaggi raggiunge threshold (default: 5)
   - `orchestrator.run_consolidation()` eseguito automaticamente

4. **Consolidazione**:
   ```
   orchestrator.run_consolidation()
       ↓
   _get_recent_messages() → ultimi 20 messaggi
       ↓
   sleep_agent.consolidate(messages) → analisi e insights JSON
       ↓
   _apply_insights(insights) → aggiorna memory blocks
   ```

### Output Sleep Agent (JSON)

```json
{
    "persona_updates": [
        "Nuovo insight su chi sei",
        "Evoluzione del tuo carattere"
    ],
    "human_updates": [
        "Informazione importante sull'umano",
        "Preferenze scoperte"
    ],
    "goals_insights": [
        "Progressi verso obiettivi",
        "Nuovi obiettivi emersi"
    ],
    "reflection": "Riflessione su questa sessione",
    "priority_actions": [
        "Azioni importanti da ricordare"
    ]
}
```

### Configurazione

```python
@dataclass
class ScarletConfig:
    name: str = "Scarlet"
    version: str = "0.2.0"
    model: str = "minimax/MiniMax-M2.1"
    context_window_limit: int = 200000  # MiniMax supporta 200K
    # Sleep-time custom
    sleep_enabled: bool = True
    sleep_messages_threshold: int = 5

@dataclass
class SleepAgentConfig:
    name: str = "Scarlet-Sleep"
    model: str = "minimax/MiniMax-M2.1"
```

## Consequences

### Positive
- ✅ **Funzionalità operativa**: Sleep-time funziona correttamente
- ✅ **Controllo completo**: Siamo padroni del processo di consolidamento
- ✅ **Debug semplificato**: Logica custom, facile da tracciare
- ✅ **Output strutturato**: JSON prevedibile, facile da parsare
- ✅ **Estensibilità**: Facile aggiungere nuovi tipi di insights
- ✅ **Fallback disponibile**: Se Letta fixed, possiamo tornare al built-in

### Negative
- ⚠️ **Codice custom**: Maggiore manutenzione
- ⚠️ **Due agenti**: Due consumi API invece di uno
- ⚠️ **Latenza aggiuntiva**: Un passaggio in più per consolidamento

### Neutral
- 🔄 Potrebbe essere rimosso se Letta fixed il bug
- 🔄 Architettura potrebbe essere riutilizzata per altre funzionalità

## Implementation

### Files Creati/Modificati

| File | Azione | Descrizione |
|------|--------|-------------|
| `scarlet/src/scarlet_agent.py` | Modificato | Aggiunte classi ScarletSleepAgent e SleepTimeOrchestrator |
| `scarlet/tests/test_sleep_time_custom.py` | Creato | Test suite per sleep-time custom |
| `docs/architecture/adr-003.md` | Questo file | Documentazione decisione |

### Test Suite

```python
def test_sleep_time_creation():
    """Test creating agent with custom sleep-time."""
    pass

def test_messaging():
    """Test that messaging works and triggers sleep-time."""
    pass

def test_manual_consolidation():
    """Test manual consolidation trigger."""
    pass

def test_sleep_status():
    """Test getting sleep-time status."""
    pass

def test_agent_deletion():
    """Test that deletion cleans up both agents."""
    pass
```

### API Pubbliche

```python
class ScarletAgent:
    @property
    def is_sleep_enabled(self) -> bool
    
    @property
    def sleep_status(self) -> Dict[str, Any]
    
    def create(self, with_sleep_agent: bool = True) -> str
    
    def force_consolidation(self) -> Optional[Dict[str, Any]]
    
    def delete(self):
        """Delete both primary and sleep-time agents."""

class SleepTimeOrchestrator:
    def on_message(self, message_count: int = 1)
    
    def run_consolidation(self) -> Optional[Dict[str, Any]]
    
    def get_status(self) -> Dict[str, Any]
```

## Monitoring e Debug

### Log Messages

```
[SleepTimeOrchestrator] Starting consolidation...
[SleepTimeOrchestrator] Consolidation complete
[ScarletAgent] Sleep-time agent created: agent-xxx
[ScarletAgent] Warning: Failed to apply some insights: ...
```

### Status Check

```python
scarlet.sleep_status
# {
#   "sleep_agent_created": True,
#   "primary_agent_created": True,
#   "message_count": 3,
#   "threshold": 5,
#   "auto_trigger": True,
#   "last_consolidation": "2026-01-31T10:00:00",
#   "consolidation_count": 2
# }
```

## Future Considerations

1. **Se Letta fixed il bug**:
   - Valutare migrazione al built-in
   - Mantenere architettura custom come fallback
   - Benchmark prestazioni vs built-in

2. **Miglioramenti possibili**:
   - Insights più dettagliati (sentiment, pattern)
   - Consolidazione asincrona non-bloccante
   - Callback personalizzabili
   - Rate limiting per API calls

## References

- [ADR-001: Letta Adoption](adr-001-letta-adoption.md)
- [ADR-002: Scarlet Setup](adr-002-scarlet-setup.md)
- [Letta Sleep-Time Documentation](https://docs.letta.com/agents/sleep)
- [CHANGELOG.md](../../CHANGELOG.md)
- [CONTEXT.md](../../CONTEXT.md)

## History

- 2026-01-31: ABIOGENESIS Team - Identificato bug Letta sleep-time
- 2026-01-31: ABIOGENESIS Team - Proposta architettura dual-agent custom
- 2026-01-31: ABIOGENESIS Team - Implementazione completata
- 2026-01-31: ABIOGENESIS Team - Decision accepted
