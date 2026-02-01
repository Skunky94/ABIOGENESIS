# PROC-006: Registrazione Tool Letta

**Status**: Active  
**Version**: 1.0.0  
**Date**: 2026-02-01  
**Author**: ABIOGENESIS Team

> **Questo documento è una GUIDA OPERATIVA** per l'IDE Agent (LLM).
> Seguire i passi ESATTAMENTE come descritti per garantire consistenza.

---

## Scopo

Registrare un nuovo tool custom con un agente Letta in modo sicuro e senza duplicati.

---

## Quando Usare Questa Procedura

Usa questa procedura quando:
- Devi creare un nuovo tool per Scarlet o altro agente Letta
- Devi aggiornare il codice di un tool esistente
- Devi collegare un tool esistente a un agente diverso

**NON usare** questa procedura se:
- Stai usando i tool built-in di Letta (conversation_search, memory_insert, memory_replace)
- Vuoi solo rimuovere un tool da un agente (usa `agents.tools.detach()` direttamente)

---

## Prerequisiti

Prima di iniziare, verifica che:

1. **Container Letta attivo** - Comando: `docker ps --filter "name=abiogenesis-letta"`
2. **API Letta raggiungibile** - Comando: `Invoke-RestMethod -Uri "http://localhost:8283/v1/health"`
3. **Agent ID noto** - Consultare CONTEXT.md per gli ID agenti correnti
4. **Webhook attivo** (se il tool chiama il webhook) - Comando: `Invoke-RestMethod -Uri "http://localhost:8284/health"`

---

## Lezioni Apprese (CRITICHE)

⚠️ **Errori comuni da evitare**:

| Errore | Causa | Soluzione |
|--------|-------|-----------|
| `got unexpected keyword argument 'name'` | `tools.create()` NON accetta `name` | Il nome viene estratto dalla funzione nel source_code |
| `'ToolsResource' object has no attribute 'list_for_agent'` | API sbagliata | Usare `client.agents.tools.list(agent_id=...)` |
| Tool duplicati nell'agente | Bug Letta: attach crea duplicati | Verificare SEMPRE prima di attach |
| Tool rimossi per errore | Detach di tutti i tool | Salvare lista tool PRIMA di qualsiasi operazione |

---

## Procedura Passo-Passo

### Passo 1: Connessione e Verifica Agente

**Cosa fare**: Connettersi a Letta e verificare che l'agente esista.

**Comando**:
```python
from letta_client import Letta

LETTA_URL = "http://localhost:8283"
AGENT_ID = "agent-ac26cf86-3890-40a9-a70f-967f05115da9"  # Scarlet Primary

client = Letta(base_url=LETTA_URL)
agent = client.agents.retrieve(AGENT_ID)
print(f"Agente trovato: {agent.name}")
```

**Output atteso**: `Agente trovato: Scarlet`

**Se fallisce**: 
- Verificare che AGENT_ID sia corretto (consultare CONTEXT.md)
- Verificare che Letta sia attivo: `docker logs abiogenesis-letta --tail 20`

---

### Passo 2: Salvare Tool Esistenti (BACKUP)

**Cosa fare**: Salvare la lista dei tool attualmente collegati PRIMA di qualsiasi modifica.

**Comando**:
```python
# CRITICO: Salvare lista tool esistenti
existing_agent_tools = list(client.agents.tools.list(agent_id=AGENT_ID))
print(f"Tool attualmente collegati ({len(existing_agent_tools)}):")
for t in existing_agent_tools:
    print(f"  - {t.name} ({t.id})")

# Salvare gli ID per eventuale rollback
backup_tool_ids = [t.id for t in existing_agent_tools]
```

**Output atteso**: Lista dei tool con nome e ID

**Se fallisce**: Se ritorna lista vuota, l'agente potrebbe non avere tool (normale per agenti nuovi)

---

### Passo 3: Verificare se Tool Esiste Già

**Cosa fare**: Controllare se un tool con lo stesso nome esiste già nel sistema.

**Comando**:
```python
TOOL_NAME = "nome_del_tuo_tool"  # Deve corrispondere al nome della funzione!

# Cerca tra TUTTI i tool del sistema (non solo quelli dell'agente)
all_tools = list(client.tools.list())
existing_tool = None
for tool in all_tools:
    if tool.name == TOOL_NAME:
        existing_tool = tool
        print(f"Tool esistente trovato: {tool.id}")
        break

if existing_tool is None:
    print(f"Tool '{TOOL_NAME}' non esiste, verrà creato")
```

**Output atteso**: ID del tool se esiste, altrimenti messaggio che verrà creato

**Se fallisce**: Verificare che il nome corrisponda esattamente al nome della funzione nel source code

---

### Passo 4: Preparare Source Code del Tool

**Cosa fare**: Scrivere il source code del tool. **IL NOME DELLA FUNZIONE DIVENTA IL NOME DEL TOOL**.

**Template**:
```python
TOOL_SOURCE_CODE = '''
def nome_del_tuo_tool(param1: str, param2: int = 10) -> str:
    """
    Descrizione dettagliata del tool.
    Questa docstring appare in Letta come descrizione.
    
    Args:
        param1: Descrizione parametro 1
        param2: Descrizione parametro 2 (default: 10)
        
    Returns:
        Descrizione di cosa ritorna
    """
    import requests  # Import DENTRO la funzione!
    
    webhook_url = "http://sleep-webhook:8284"
    
    try:
        response = requests.post(
            f"{webhook_url}/tuo/endpoint",
            json={"param1": param1, "param2": param2},
            timeout=30.0
        )
        response.raise_for_status()
        return response.json().get("result", "[Nessun risultato]")
    except Exception as e:
        return f"[Errore: {e}]"
'''
```

**Regole CRITICHE**:
- Il nome della funzione (`def nome_del_tuo_tool`) diventa il nome del tool
- Gli import devono essere DENTRO la funzione (sandbox Letta)
- Usare `requests` (disponibile in Letta) non `httpx`
- Il webhook URL deve essere `http://sleep-webhook:8284` (nome Docker interno)
- Gestire sempre le eccezioni e ritornare messaggio di errore user-friendly

**Se fallisce**: Verificare che il source code sia sintatticamente corretto con `compile(TOOL_SOURCE_CODE, '<string>', 'exec')`

---

### Passo 5: Creare o Aggiornare Tool

**Cosa fare**: Creare il tool se non esiste, o aggiornarlo se esiste.

**Comando**:
```python
if existing_tool is None:
    # CREARE nuovo tool
    new_tool = client.tools.create(
        source_code=TOOL_SOURCE_CODE,
        tags=["custom", "tuo-tag"]  # Tags opzionali
    )
    print(f"Tool creato: {new_tool.name} ({new_tool.id})")
    tool_id = new_tool.id
else:
    # AGGIORNARE tool esistente
    updated_tool = client.tools.update(
        tool_id=existing_tool.id,
        source_code=TOOL_SOURCE_CODE,
        tags=["custom", "tuo-tag"]
    )
    print(f"Tool aggiornato: {updated_tool.name} ({updated_tool.id})")
    tool_id = updated_tool.id
```

**Output atteso**: Nome e ID del tool creato/aggiornato

**Se fallisce**: 
- Errore di sintassi nel source code → verificare il codice
- Errore "name" → NON passare `name=` come parametro (vedi Lezioni Apprese)

---

### Passo 6: Verificare se Già Collegato all'Agente

**Cosa fare**: Controllare se il tool è già collegato all'agente per evitare duplicati.

**Comando**:
```python
# CRITICO: Verificare PRIMA di attach per evitare duplicati
current_tools = list(client.agents.tools.list(agent_id=AGENT_ID))
already_attached = any(t.id == tool_id for t in current_tools)

if already_attached:
    print(f"Tool già collegato all'agente, skip attach")
else:
    print(f"Tool non collegato, procedo con attach")
```

**Output atteso**: Messaggio che indica se il tool è già collegato o meno

**Se fallisce**: Verificare che AGENT_ID sia corretto

---

### Passo 7: Collegare Tool all'Agente

**Cosa fare**: Collegare il tool all'agente solo se non già collegato.

**Comando**:
```python
if not already_attached:
    client.agents.tools.attach(
        agent_id=AGENT_ID,
        tool_id=tool_id
    )
    print(f"Tool {tool_id} collegato all'agente {AGENT_ID}")
```

**Output atteso**: Messaggio di conferma

**Se fallisce**: 
- Verificare che l'agente e il tool esistano
- Controllare i log di Letta: `docker logs abiogenesis-letta --tail 50`

---

## Verifica Finale

Al termine della procedura, verifica che:

**Comando di verifica completo**:
```python
# Verifica finale
final_tools = list(client.agents.tools.list(agent_id=AGENT_ID))
print(f"\nTool finali collegati a {agent.name}:")
seen = set()
for t in final_tools:
    if t.name not in seen:
        print(f"  ✅ {t.name} ({t.id})")
        seen.add(t.name)

# Verificare che il nuovo tool sia presente
tool_names = [t.name for t in final_tools]
if TOOL_NAME in tool_names:
    print(f"\n✅ Tool '{TOOL_NAME}' registrato con successo!")
else:
    print(f"\n❌ ERRORE: Tool '{TOOL_NAME}' non trovato!")
```

**Criteri di successo**:
1. ✅ Il nuovo tool appare nella lista
2. ✅ Non ci sono duplicati (stesso ID appare una sola volta)
3. ✅ I tool precedenti sono ancora presenti

---

## Rollback (Come Annullare)

Se qualcosa va storto, segui questi passi:

### Caso 1: Tool collegato per errore

```python
# Rimuovere tool dall'agente
client.agents.tools.detach(agent_id=AGENT_ID, tool_id=tool_id)
print(f"Tool {tool_id} rimosso dall'agente")
```

### Caso 2: Tool creato per errore

```python
# Eliminare tool dal sistema
client.tools.delete(tool_id=tool_id)
print(f"Tool {tool_id} eliminato")
```

### Caso 3: Tool esistenti rimossi per errore

```python
# Ricollegare i tool dal backup
for backup_id in backup_tool_ids:
    try:
        client.agents.tools.attach(agent_id=AGENT_ID, tool_id=backup_id)
        print(f"Ripristinato: {backup_id}")
    except Exception as e:
        print(f"Errore ripristino {backup_id}: {e}")
```

---

## Script Completo di Riferimento

Vedi [scarlet/register_remember_tool.py](../../scarlet/register_remember_tool.py) come esempio funzionante.

---

## Checklist Rapida

```
□ Container Letta attivo
□ AGENT_ID corretto (da CONTEXT.md)
□ Backup tool esistenti fatto
□ Nome funzione nel source code = nome tool desiderato
□ Import dentro la funzione
□ Webhook URL = http://sleep-webhook:8284 (interno Docker)
□ Verificato che tool non già collegato prima di attach
□ Verifica finale: tool presente, no duplicati
□ CHANGELOG aggiornato
```

---

## Riferimenti

- [ADR-005: Human-Like Memory System](../architecture/adr-005-human-like-memory-system.md) - Context del tool remember
- [CONTEXT.md](../../CONTEXT.md) - Agent IDs correnti
- [Letta Tools Documentation](https://docs.letta.com/tools)

---

**PROC-006 v1.0.0 - ABIOGENESIS Project**  
*Letta Tool Registration Procedure*
