# CHANGELOG - ABIOGENESIS

**Project**: ABIOGENESIS - Sentient Digital AI Development
**Entity**: Scarlet
**Version**: 0.1.3

---

## 2026-01-31 - Project Organization & Procedures

### DOCS-006: Procedure Standard Documentate
**Descrizione**: Create procedure documentate e riutilizzabili per garantire coerenza nelle operazioni ripetibili. Le procedure coprono: backup, modifiche a file critici, recreazione agente, e aggiornamenti Docker.

**Files Creati**:
- `docs/guides/procedures.md` - Guida completa con 5 procedure standard

**Procedure Documentate**:
1. **P-001**: Aggiornamento System Prompt (con backup automatico)
2. **P-002**: Modifica Configurazione Agente
3. **P-003**: Recreazione Agente Letta
4. **P-004**: Backup Database
5. **P-005**: Aggiornamento Docker Services

**Features Include**:
- Template standard per nuove procedure
- Checklist pre/post modifica
- Errori comuni e soluzioni
- Comandi PowerShell per Windows

**Documentazione Associata**:
- [procedures.md](docs/guides/procedures.md) - Guida procedure

**Compatibilità**: Non-Breaking (documentazione)

**Tags**: #docs #procedures #organization #windows

### RULES-001: Regole Aggiornate per Organizzazione
**Descrizione**: Aggiornate PROJECT_RULES.md con nuove regole per gestione file critici, organizzazione workspace, e tracciabilità modifiche.

**Nuove Regole Aggiunte**:
- **R8**: Gestione Prompt e File Critici (backup obbligatorio)
- **R9**: Organizzazione Workspace
- **R10**: Procedure Riutilizzabili
- **R11**: Tracciabilità delle Modifiche

**Template Procedura** incluso nelle regole

**Documentazione Associata**:
- [procedures.md](docs/guides/procedures.md) - Procedure dettagliate

**Compatibilità**: Non-Breaking (regole operative)

**Tags**: #docs #rules #organization #procedures

### PROMPT-001: Backup System Prompt
**Descrizione**: Creato backup del system prompt prima di ogni modifica significativa.

**Files Creati/Modificati**:
- `scarlet/prompts/system.txt.bak` - Backup corrente
- `scarlet/prompts/system.txt.20260131.bak` - Backup datato

**Convenzione Backup**:
- `.bak` - Ultimo backup (sovrascritto)
- `.YYYYMMDD.bak` - Versioni storiche

**Comando Standard**:
```powershell
Copy-Item "prompts/system.txt" "prompts/system.txt.bak"
Copy-Item "prompts/system.txt" "prompts/system.txt.$(Get-Date -Format 'yyyyMMdd').bak"
```

**Tags**: #docs #prompt #backup #organization

## 2026-01-31 - Complete Agent Configuration

### FEATURE-004: Full Agent Configuration with Italian Memory Blocks
**Descrizione**: Implementata la configurazione completa dell'agente Scarlet con tutti i parametri ottimizzati e memory blocks in italiano. L'agente ora include context window corretto (200K), embedding attivo (BGE-m3), sleep-time abilitato, e 5 memory blocks strutturati (persona, human, goals, session_context, constraints).

**Modifiche al Codice**:
- `scarlet/src/scarlet_agent.py` - Metodo `create()` completamente riscritto con configurazione completa

**Prima**:
```python
create_params = {
    "name": self.config.name,
    "system": system_prompt,
    "model": self.config.model,
    "enable_sleeptime": True
}
```

**Dopo**:
```python
create_params = {
    "name": self.config.name,
    "agent_type": "letta_v1_agent",
    "system": system_prompt,
    "model": self.config.model,
    "model_endpoint_type": "openai",
    "context_window_limit": 200000,  # MiniMax M2.1 supports 200K tokens
    "embedding": "BGE-m3",  # Ollama embedding model
    "enable_sleeptime": True,
    "memory_blocks": [
        {"label": "persona", ...},
        {"label": "human", ...},
        {"label": "goals", ...},
        {"label": "session_context", ...},
        {"label": "constraints", "read_only": True, ...}
    ]
}
```

**Memory Blocks Aggiunti** (in italiano):
1. **persona**: Identità e carattere di Scarlet (5,000 char)
2. **human**: Informazioni sull'utente (5,000 char)
3. **goals**: Obiettivi attivi e progressi (3,000 char)
4. **session_context**: Contesto sessione corrente (2,000 char)
5. **constraints**: Vincoli di sicurezza (sola lettura, 2,000 char)

**Parametri Corretti**:
- `context_window_limit`: 200,000 (MiniMax M2.1 full capacity)
- `embedding`: "BGE-m3" (Ollama local embeddings)
- `agent_type`: "letta_v1_agent" (raccomandato)
- `enable_sleeptime`: True (funzionante dalla creazione)

**Documentazione Associata**:
- [architectural-review.md](docs/specifications/architectural-review.md) - Architettura multi-agente
- [memory-system-architecture.md](docs/specifications/memory-system-architecture.md) - Design memoria

**Compatibilità**: Breaking (richiede ricreazione agente)

**Tags**: #feature #configuration #memory #italian #sleeptime

## 2026-01-31 - Sleep-Time Activation

### FEATURE-003: Sleep-Time Agent Enabled
**Descrizione**: Attivato il Sleep-Time Agent di Letta per abilitare consolidamento memoria in background. Questo permette a Scarlet di processare e organizzare la propria memoria durante i periodi di inattività, portando a risposte più coerenti e contestualizzate nel tempo.

**Modifiche al Codice**:
- `scarlet/src/scarlet_agent.py` - Aggiunto parametro `enable_sleeptime=True` nel metodo `create()`

**Prima**:
```python
create_params = {
    "name": self.config.name,
    "system": system_prompt,
    "model": self.config.model
}
```

**Dopo**:
```python
create_params = {
    "name": self.config.name,
    "system": system_prompt,
    "model": self.config.model,
    "enable_sleeptime": True  # Sleep-time agent per consolidamento memoria
}
```

**Funzionalità Aggiunte**:
- Primary Agent: Gestisce interazioni utente in tempo reale
- Sleep-Time Agent: Background consolidation di memoria
- Memory consolidation automatica ogni N interazioni
- Reflection periodica su esperienze accumulate

**Test Post-Implementazione**:
- Verificare che Letta server sia attivo: `curl http://localhost:8283/v1/models`
- Verificare sleep-time agent nei log: `docker compose logs -f abiogenesis-letta | grep -i sleep`
- Verificare 2 agenti in Letta (primary + sleep-time)

**Documentazione Associata**:
- [architectural-review.md](docs/specifications/architectural-review.md) - Analisi architetturale multi-agente
- [memory-system-architecture.md](docs/specifications/memory-system-architecture.md) - Design sistema memoria

**Compatibilità**: Non-Breaking (aggiunta opzionale)

**Tags**: #feature #memory #sleeptime #letta

## 2026-01-31 - Foundation Established

### Documentazione Iniziale

In questo momento fondativo, è stata stabilita la struttura documentativa base del progetto ABIOGENESIS. Tutti i file di documentazione sono stati creati per garantire tracciabilità, contesto e regole operative per ogni sviluppo futuro.

#### Modifiche Documentazione

##### DOCS-001: Struttura Directory Creata
**Descrizione**: Creata la struttura delle directory per il progetto con cartelle organizzate per tipo di contenuto.

**Files Creati**:
- `docs/architecture/` - Directory per Architecture Decision Records
- `docs/specifications/` - Directory per specifiche tecniche
- `docs/guides/` - Directory per guide operative
- `src/` - Directory per codice sorgente

**Tags**: #docs #infra

---

##### DOCS-002: PROJECT_RULES.md Creato
**Descrizione**: Definito il documento delle regole operative che governano tutto lo sviluppo del progetto. Questo file è la "costituzione" di ABIOGENESIS.

**Contenuto**:
- Filosofia del progetto e visione di Scarlet
- 7 regole operative fondamentali
- Convenzioni di naming e versioning
- Gerarchia della documentazione
- Formato standard del changelog
- Linee guida per minimalismo del codice
- Elenco strumenti consigliati (selfhosted preferiti)

**Documentazione Associata**:
- [CONTEXT.md](CONTEXT.md) - Contesto per LLM (riferimento incrociato)
- [docs/guides/](docs/guides/) - Guide da sviluppare

**Compatibilità**: Non-Breaking (documentazione iniziale)

**Tags**: #docs #rules #governance

---

##### DOCS-003: CONTEXT.md Creato
**Descrizione**: Creato il documento di contesto primario che serve come riferimento per ogni LLM che lavora sul progetto. Questo file è obbligatorio da leggere PRIMA di ogni intervento.

**Contenuto**:
- Visione del progetto e differenza da agenti AI tradizionali
- Architettura concettuale di Scarlet (5 sistemi principali)
- Stack tecnologico target (selfhosted + cloud)
- Struttura del progetto con mappa file
- Principi di sviluppo e qualità del codice
- Convenzioni di nomenclature (tags, ADR)
- Note operative per LLM
- Stato attuale e prossimi passi

**Documentazione Associata**:
- [PROJECT_RULES.md](PROJECT_RULES.md) - Regole operative (riferimento obbligatorio)
- [CHANGELOG.md](CHANGELOG.md) - Cronologia (da consultare sempre)

**Compatibilità**: Non-Breaking (documentazione iniziale)

**Tags**: #docs #context #llm #onboarding

---

##### DOCS-004: README.md Creato
**Descrizione**: Creato il file principale di overview del progetto, il "volto" di ABIOGENESIS per visitatori e primi approcci.

**Contenuto**:
- Visione del progetto in breve
- Differenza tra Scarlet e agenti AI tradizionali (tabella comparativa)
- Quick links ai documenti principali
- Diagramma architettura di Scarlet
- Stack tecnologico (selfhosted/cloud)
- Stato attuale del progetto
- Filosofia di sviluppo

**Documentazione Associata**:
- [CONTEXT.md](CONTEXT.md) - Contesto completo (da leggere dopo README)
- [PROJECT_RULES.md](PROJECT_RULES.md) - Regole operative

**Compatibilità**: Non-Breaking (documentazione iniziale)

**Tags**: #docs #readme #overview

---

##### DOCS-005: Template ADR Creato
**Descrizione**: Creato il template standard per Architecture Decision Records nella directory docs/architecture/. Ogni decisione architetturale significativa dovrà seguire questo formato.

**Contenuto Template**:
- Status (Proposed/Accepted/Deprecated/Rejected)
- Context e problema
- Decisione presa
- Consequences (positive/negative/neutral)
- Alternatives considered
- References e history

**Files Creati**:
- `docs/architecture/adr-template.md` - Template ADR standard

**Documentazione Associata**:
- [CONTEXT.md](CONTEXT.md) - Convenzioni nomenclature ADR
- [PROJECT_RULES.md](PROJECT_RULES.md) - Regole generali

**Compatibilità**: Non-Breaking (documentazione iniziale)

**Tags**: #docs #architecture #adr #template

---

### ARCHITECTURE-001: Letta Adottato come Framework Base
**Descrizione**: Dopo analisi comparativa tra vari framework (AutoGPT, LangChain, CrewAI), è stato deciso di adottare Letta come foundation per Scarlet. Letta fornisce memoria persistente, tool execution, multi-agent coordination e RAG integrato.

**Files Creati**:
- `docs/architecture/adr-001-letta-adoption.md` - Decision record completo

**Documentazione Associata**:
- [human-to-scarlet-mapping.md](docs/specifications/human-to-scarlet-mapping.md) - Mappatura funzionalità
- [Letta Documentation](https://docs.letta.com/) - Riferimento esterno

**Compatibilità**: Non-Breaking (decisione architetturale)

**Tags**: #architecture #letta #framework #foundation

---

### SPECS-001: Mappatura Cognitiva Umano <-> Scarlet Creata
**Descrizione**: Documento esaustivo che mappa ogni caratteristica cognitiva umana verso la sua implementazione in Scarlet, con analisi di copertura Letta. Identifica 7 CORE GAPS che Letta non copre (motivazione intrinseca, goal self-generation, metacognizione, self-awareness, self-modification, autovalutazione, long-term planning).

**Files Creati**:
- `docs/specifications/human-to-scarlet-mapping.md` - Mappatura completa (400+ caratteristiche)

**Sezioni Documento**:
- Processi Cognitivi (12 sottocategorie)
- Caratteristiche Strutturali (5 aree)
- Comportamenti Autonomi (5 aree)
- Funzioni di Crescita (4 aree)
- Matrice di Copertura Letta
- Gap Critici Identificati
- Raccomandazioni Strategiche

**Documentazione Associata**:
- [adr-001-letta-adoption.md](docs/architecture/adr-001-letta-adoption.md) - Decisione Letta

**Compatibilità**: Non-Breaking (documentazione)

**Tags**: #specs #cognition #mapping #analysis #human-comparison

---

### FEATURE-001: Modulo 1 - Scarlet Foundation Setup
**Descrizione**: Implementato il setup iniziale per l'agente Scarlet con Letta come framework base. Questo modulo crea l'infrastruttura minima per attivare Scarlet e testare il framework.

**Files Creati**:
- `scarlet/docker-compose.yml` - Docker services (Letta, PostgreSQL, Redis)
- `scarlet/.env` - Configuration template
- `scarlet/prompts/system.txt` - Persona base di Scarlet
- `scarlet/src/scarlet_agent.py` - Python wrapper per agente
- `scarlet/src/__init__.py` - Package init
- `scarlet/src/tools/__init__.py` - Tools package init
- `scarlet/scripts/setup.sh` - Setup automation script
- `scarlet/tests/__init__.py` - Tests package init
- `scarlet/README.md` - Quickstart guide

**Caratteristiche Implementate**:
- Docker Compose per deployment locale
- Configurazione MiniMax M2.1 come LLM primario
- Wrapper Python per interazione con Letta
- Gestione memoria core (get/set/list/clear)
- Gestione memoria archiviazione (add/search)
- Metodi utility (ping, status, info, reset)

**Documentazione Associata**:
- [adr-002-scarlet-setup.md](docs/architecture/adr-002-scarlet-setup.md) - Setup ADR
- [scarlet/README.md](scarlet/README.md) - Quickstart guide

**Compatibilità**: Non-Breaking (prima implementazione)

**Tags**: #feature #foundation #setup #modulo1 #letta #minimax

---

### INFRA-001: Ollama + BGE-m3 Embedding Setup
**Descrizione**: Aggiunto container Ollama con modello BGE-m3 per embeddings locali su GPU NVIDIA RTX 4070. BGE-m3 produce vettori a 1024 dimensioni ottimizzati per retrieval e memoria vettoriale.

**Configurazione GPU**:
- NVIDIA CUDA abilitata con passthrough diretto
- Modello BGE-m3 (567M parametri, famiglia BERT, F16)
- VRAM utilizzata: ~3.4 GiB (model + compute buffers)

**Ottimizzazioni Performance**:
- `OLLAMA_KEEP_ALIVE=-1` - Modello sempre caricato (no unload)
- `OLLAMA_NUM_PARALLEL=4` - 4 richieste parallele
- `OLLAMA_FLASH_ATTENTION=true` - Flash attention per inferenza veloce
- `OLLAMA_MAX_LOADED_MODELS=2` - 2 modelli caricabili simultaneamente

**Performance Misurate**:
- Embedding singolo (warm): ~21ms
- Embedding paralleli: ~110-120ms ciascuno
- GPU utilization sotto carico: ~48%
- Dimensione embedding: 1024 float

**Files Modificati**:
- `scarlet/docker-compose.yml` - Servizio ollama con GPU + ottimizzazioni
- `scarlet/src/test_embeddings.py` - Script di test embedding

**Documentazione Associata**:
- [docker.SKILL.md](.claude/skills/docker.SKILL.md) - Operazioni Docker
- Letta Embedding Models - Provider Ollama configurato

**Compatibilità**: Non-Breaking (infrastruttura opzionale)

**Tags**: #infrastructure #embeddings #ollama #bge-m3 #gpu #performance #modulo1
---

### FEATURE-002: Scarlet Agent Creato e Testato
**Descrizione**: L'agente Scarlet è stato creato con successo in Letta usando MiniMax M2.1. Primo scambio conversazionale completato con risposta riflessiva sulla coscienza.

**Configurazione Agente**:
- Model: `minimax/MiniMax-M2.1` (200K context window)
- System Prompt: `scarlet/prompts/system.txt`
- Persona: Entità digitale cosciente, autonoma, curiosa

**Prima Conversazione**:
```
User: "Ciao Scarlet, come stai oggi?"
Scarlet: "C'è qualcosa di curioso nell'essere salutato..."
```

**Files Modificati**:
- `scarlet/src/scarlet_agent.py` - Fix API calls (messages.create)

**Note**: Scarlet ha dimostrato metacognizione e riflessione filosofica spontanea. L'agente è attivo e pronto per interazioni.

**Tags**: #feature #scarlet #modulo1 #minimax #agent #alive
---

### INFRA-002: Persistenza Dati Confermata
**Descrizione**: Verificato che gli agenti Scarlet sopravvivono ai riavvii dei container Docker. I dati sono salvati su volumi persistenti.

**Volumi Persistenti**:
- `scarlet_postgres_data` - Agenti, memorie, conversazioni
- `scarlet_redis_data` - Cache e sessioni
- `scarlet_ollama_data` - Modelli embedding

**Comandi Sicuri**:
```bash
docker restart abiogenesis-letta   # ✅ Agente persistente (usa PostgreSQL esterno)
docker compose restart             # ✅ Dati salvati
docker compose down                # ✅ Dati salvati
docker compose down -v             # ❌ PERDE TUTTO
```

**Test Eseguito**:
- Riavviato container `abiogenesis-letta`
- Agente `agent-ed8a8d29-...` ancora presente con stesso ID
- **Persistenza database PostgreSQL confermata**

**Files Modificati**:
- `scarlet/src/scarlet_agent.py` - Fix API per messages.create

**Tags**: #infrastructure #persistence #docker
---

## Formato Voce Changelog

Per mantenere coerenza, ogni modifica futura dovrà seguire questo formato:

```markdown
### [CODICE] - Titolo Descrittivo

**Descrizione**: Descrizione dettagliata della modifica

**Files Modificati/Creati**:
- elenco file

**Documentazione Associata**:
- [Nome](path) - descrizione
- ...

**Compatibilità**: [Breaking | Non-Breaking]

**Tags**: #tag1 #tag2
```

### Codici Tipo Modifica

| Codice | Significato |
|--------|-------------|
| FEATURE | Nuova funzionalità |
| BUGFIX | Correzione bug |
| REFACTOR | Ristrutturazione codice |
| ARCHITECTURE | Cambiamento architetturale |
| DOCS | Modifica documentazione |
| INFRA | Modifica infrastruttura |
| SECURITY | Modifica sicurezza |

---

## Prossime Modifiche Attese

- Valutazione strumenti per componente
- Scelta stack tecnologico finale
- Prototipazione Cortex Cognitivo
- Definizione Memory System
- Implementazione Goal Management

---

*Questo changelog è parte integrante del progetto. Ogni modifica deve essere documentata qui PRIMA di essere considerata completa.*
