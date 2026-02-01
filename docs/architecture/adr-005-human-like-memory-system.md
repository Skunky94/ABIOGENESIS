# ADR-005: Human-Like Memory System Architecture

**Status**: Accepted  
**Date**: 2026-02-01  
**Author**: ABIOGENESIS Team  
**Supersedes**: Partial aspects of ADR-004 (memory storage schema)

---

## Context

### Il Problema

Il sistema di memoria attuale di Scarlet (v0.3.4) presenta lacune critiche che impediscono un comportamento veramente "human-like":

1. **Retrieval solo semantico**: Il sistema cerca memorie per similarità vettoriale, ma non capisce l'INTENTO della query
2. **Nessun filtro temporale**: "Cosa abbiamo fatto ieri?" restituisce risultati basati su similarità, non su data
3. **Ricordi isolati**: Le memorie non hanno connessioni tra loro (no knowledge graph)
4. **Importance statica**: `importance = 0.5` sempre, nessun calcolo dinamico
5. **Nessun tracking accessi**: `access_count` e `last_accessed` esistono ma non vengono mai aggiornati
6. **Emotional encoding assente**: Solo una stringa opzionale, non un modello dimensionale
7. **Nessun decay**: I ricordi non sbiadiscono nel tempo

### Obiettivo

Implementare un sistema di memoria che replichi i meccanismi cognitivi umani:
- **Encoding multidimensionale**: chi, cosa, quando, come mi sono sentito, perché è importante
- **Retrieval associativo**: un trigger attiva catene di ricordi collegati
- **Consolidamento e decay**: ricordi usati si rafforzano, ricordi ignorati sbiadiscono
- **Emotional valence**: i ricordi emotivamente intensi persistono più a lungo

---

## Decision

### 1. Query Analyzer con LLM Locale

Implementare un componente che analizza ogni query utente per determinare la strategia di retrieval ottimale.

**Modello scelto**: `qwen2.5:1.5b` su Ollama
- Già abbiamo Ollama nel docker-compose
- 1.5B parametri = buon equilibrio velocità/qualità
- Supporto multilingua (italiano incluso)
- ~50-100ms di latenza attesa
- 0 costi cloud

**Output del Query Analyzer**:
```json
{
    "intent": "temporal|entity|emotional|topic|procedural|general",
    "time": {
        "type": "exact|range|relative|none",
        "reference": "ieri",
        "resolved_start": "2026-01-31T00:00:00Z",
        "resolved_end": "2026-01-31T23:59:59Z"
    },
    "entities": ["Davide"],
    "topics": ["memoria", "architettura"],
    "emotion_filter": "positive|negative|neutral|null",
    "memory_types": ["episodic", "semantic", "procedural", "emotional"],
    "semantic_query": "cosa abbiamo fatto"
}
```

### 2. Schema Dati Arricchito per Qdrant

Ogni memoria avrà un payload completo con tutte le dimensioni necessarie:

```python
memory_payload = {
    # === IDENTIFICAZIONE ===
    "id": "mem-uuid",
    "type": "episodic|semantic|procedural|emotional",
    
    # === CONTENUTO ===
    "title": "Discussione architettura memoria",
    "content": "Contenuto completo...",
    "summary": "Riassunto breve per retrieval veloce",
    
    # === TEMPORALE ===
    "created_at": "2026-02-01T14:30:00Z",      # ISO timestamp completo
    "date": "2026-02-01",                       # Solo data (per filtri range)
    "time_of_day": "afternoon",                 # morning|afternoon|evening|night
    "day_of_week": "saturday",                  # Per pattern settimanali
    
    # === ENTITÀ E CONTESTO ===
    "participants": ["Davide"],                 # Chi era coinvolto
    "topics": ["memoria", "architettura"],      # Argomenti trattati
    "session_id": "sess-123",                   # ID conversazione
    "preceding_memory": "mem-456",              # Link al ricordo precedente
    "following_memory": "mem-789",              # Link al ricordo successivo
    
    # === EMOTIVO (PAD Model) ===
    "emotional_valence": 0.7,                   # -1 (negativo) a +1 (positivo)
    "emotional_arousal": 0.5,                   # 0 (calmo) a 1 (eccitato)
    "emotional_dominance": 0.6,                 # 0 (sottomesso) a 1 (dominante)
    "primary_emotion": "curiosity",             # Emozione dominante
    "emotional_keywords": ["interessante"],     # Parole chiave emotive
    
    # === IMPORTANZA E DECAY ===
    "importance": 0.7,                          # 0.0 a 1.0 (calcolata dinamicamente)
    "access_count": 0,                          # Contatore accessi
    "last_accessed": "2026-02-01T14:30:00Z",   # Ultimo accesso
    "decay_factor": 1.0,                        # Moltiplicatore decay (1.0 = fresh)
    "reinforcement_score": 0.0,                 # Bonus da accessi frequenti
    
    # === RELAZIONI ===
    "related_memories": ["mem-abc", "mem-def"], # Link espliciti ad altri ricordi
    "related_entities": ["Davide", "ABIOGENESIS"],
    "related_topics": ["AI", "memoria"],
    
    # === META ===
    "source": "conversation|sleep_consolidation|user_correction|self_reflection",
    "confidence": 0.8,                          # Quanto siamo sicuri
    "verified": false,                          # Confermato dall'utente
    "tags": ["tecnico", "importante"]
}
```

### 3. Multi-Strategy Search

Il retrieval non sarà più solo semantico, ma seguirà strategie diverse in base all'intent:

| Intent | Strategia Primaria | Fallback |
|--------|-------------------|----------|
| `temporal` | Filter by date + semantic | Pure semantic |
| `entity` | Filter by participants + semantic | Topic filter |
| `emotional` | Filter by valence + semantic | Pure semantic |
| `topic` | Filter by topics + semantic | Pure semantic |
| `procedural` | Collection skills only | All collections |
| `general` | Pure semantic (come oggi) | - |

**Combinazione filtri Qdrant**:
```python
# Esempio: "Cosa abbiamo fatto ieri con Davide?"
filter = Filter(
    must=[
        FieldCondition(key="date", match=MatchValue(value="2026-01-31")),
        FieldCondition(key="participants", match=MatchAny(any=["Davide"]))
    ]
)
```

### 4. Ranking Formula

Score finale per ordinare i risultati:

```
final_score = (
    semantic_similarity * 0.35 +
    temporal_relevance * 0.25 +
    importance * 0.15 +
    emotional_intensity * 0.10 +
    access_frequency_norm * 0.10 +
    recency_bonus * 0.05
) * decay_factor
```

Dove:
- `semantic_similarity`: score da Qdrant (0-1)
- `temporal_relevance`: 1.0 se match temporale esatto, decay per distanza
- `importance`: valore dal payload
- `emotional_intensity`: `abs(valence) * arousal`
- `access_frequency_norm`: `min(1.0, access_count / 10)`
- `recency_bonus`: `1.0 - (days_since_creation / 30)` capped a 0
- `decay_factor`: dal payload

### 5. Access Tracking e Reinforcement

Ad ogni retrieval che restituisce una memoria:

```python
# Aggiornamenti atomici
memory.access_count += 1
memory.last_accessed = now()
memory.reinforcement_score += 0.05

# Boost importance per accessi frequenti (max 0.95)
if memory.importance < 0.95:
    memory.importance = min(0.95, memory.importance + 0.02)
```

Questo crea il **rafforzamento** tipico della memoria umana: più accedi a un ricordo, più diventa forte.

### 6. Decay Periodico

Background job (ogni 24h o al riavvio):

```python
for memory in all_memories:
    days_since_access = (now - memory.last_accessed).days
    
    if days_since_access > 7:
        # Curva di Ebbinghaus semplificata
        base_decay = 0.95 ** (days_since_access // 7)  # -5% ogni settimana
        
        # Protezione emotiva
        emotional_protection = memory.emotional_arousal * 0.3
        
        # Protezione importanza
        importance_protection = memory.importance * 0.2
        
        # Decay finale
        decay = min(1.0, base_decay + emotional_protection + importance_protection)
        memory.decay_factor = decay
        
        # Archiviazione se troppo debole
        if decay < 0.3 and memory.access_count < 2:
            archive_memory(memory)
```

### 7. Doppio Canale di Retrieval

**A) Automatico (ogni messaggio)**:
- Query Analyzer analizza messaggio utente
- Multi-Strategy Search trova memorie rilevanti
- Risultati iniettati in `session_context`
- Scarlet risponde con contesto arricchito

**B) Conscio (tool Scarlet)**:
- Scarlet decide di cercare attivamente
- Specifica parametri di ricerca
- Riceve risultati dettagliati
- Può raffinare la ricerca

---

## Implementation Roadmap

### Fase 1: Infrastruttura (Priorità ALTA)

| Step | Task | File | Effort |
|------|------|------|--------|
| 1.1 | Scaricare qwen2.5:1.5b su Ollama | docker-compose.yml | 10min |
| 1.2 | Testare latenza e qualità modello | test_query_analyzer.py | 30min |
| 1.3 | Creare indici Qdrant per filtri | qdrant_manager.py | 1h |

### Fase 2: Query Analyzer (Priorità ALTA)

| Step | Task | File | Effort |
|------|------|------|--------|
| 2.1 | Creare modulo query_analyzer.py | src/memory/query_analyzer.py | 2h |
| 2.2 | Definire prompt template | prompts/query_analyzer.txt | 30min |
| 2.3 | Implementare parsing output | query_analyzer.py | 1h |
| 2.4 | Test con query reali | tests/test_query_analyzer.py | 1h |

### Fase 3: Schema Dati (Priorità ALTA)

| Step | Task | File | Effort |
|------|------|------|--------|
| 3.1 | Aggiornare MemoryBlock dataclass | memory_blocks.py | 1h |
| 3.2 | Aggiornare metodo _store_in_qdrant | memory_blocks.py | 1h |
| 3.3 | Creare funzioni estrazione entità/topic | memory_enrichment.py | 2h |
| 3.4 | Creare funzione analisi emozione | memory_enrichment.py | 1h |
| 3.5 | Migrare memorie esistenti (opzionale) | migration_script.py | 1h |

### Fase 4: Multi-Strategy Search (Priorità ALTA)

| Step | Task | File | Effort |
|------|------|------|--------|
| 4.1 | Creare SearchStrategy enum | memory_retriever.py | 30min |
| 4.2 | Implementare filtered search | memory_retriever.py | 2h |
| 4.3 | Implementare ranking formula | memory_retriever.py | 1h |
| 4.4 | Implementare access tracking | memory_retriever.py | 1h |
| 4.5 | Integrare in sleep_webhook.py | sleep_webhook.py | 2h |

### Fase 5: Decay System (Priorità MEDIA)

| Step | Task | File | Effort |
|------|------|------|--------|
| 5.1 | Creare decay job | memory_decay.py | 1h |
| 5.2 | Integrare con webhook startup | sleep_webhook.py | 30min |
| 5.3 | Test decay curve | tests/test_decay.py | 1h |

### Fase 6: Tool Conscio (Priorità MEDIA)

| Step | Task | File | Effort |
|------|------|------|--------|
| 6.1 | Definire tool schema Letta | tools/memory_search.py | 1h |
| 6.2 | Implementare handler | tools/memory_search.py | 2h |
| 6.3 | Registrare tool su agente | scarlet_agent.py | 30min |

**Effort totale stimato**: ~22 ore

---

## Consequences

### Positive

1. **Retrieval intelligente**: Scarlet capirà l'intento della query e cercherà nel modo appropriato
2. **Memoria temporale**: "Cosa abbiamo fatto ieri?" funzionerà correttamente
3. **Rafforzamento naturale**: Ricordi usati spesso diventeranno più accessibili
4. **Decay realistico**: Ricordi non usati sbiadiranno nel tempo
5. **Emotional salience**: Ricordi emotivamente intensi persisteranno
6. **Ricordi connessi**: Link espliciti tra memorie correlate
7. **Zero costi cloud**: Query analyzer su Ollama locale

### Negative

1. **Complessità aumentata**: Più componenti da mantenere
2. **Latenza aggiuntiva**: ~50-100ms per query analysis
3. **VRAM usage**: qwen2.5:1.5b richiede ~1-2GB VRAM aggiuntivi
4. **Migrazione necessaria**: Memorie esistenti potrebbero richiedere migrazione

### Neutral

1. **Cambio paradigma**: Da "cerca per similarità" a "cerca per intento"
2. **Nuovi metadati**: Più dati da estrarre e salvare

---

## Alternatives Considered

### Alternative 1: Solo Regole (No LLM)

Pattern matching con regex per determinare intent.

**Rifiutato perché**:
- Non capisce frasi complesse
- Fragile con variazioni linguistiche
- Non scala con nuovi tipi di query
- Richiede manutenzione costante

### Alternative 2: LLM Cloud (GPT-4o-mini)

Usare OpenAI per query analysis.

**Rifiutato perché**:
- Costo per ogni query (~$0.0001 ma accumula)
- Dipendenza da servizio esterno
- Latenza network aggiuntiva
- Privacy concerns (query inviate a cloud)

### Alternative 3: Fine-tuned Model

Creare un modello custom per query analysis.

**Rifiutato perché**:
- Richiede dataset di training
- Tempo di sviluppo elevato
- Difficile da mantenere
- qwen2.5 già sufficientemente capace

### Alternative 4: Knowledge Graph Esterno (Neo4j)

Usare Neo4j per relazioni tra ricordi.

**Posticipato perché**:
- Complessità infrastrutturale
- Le relazioni in Qdrant payload sono sufficienti per v1
- Può essere aggiunto in futuro se necessario

---

## Technical Details

### Query Analyzer Prompt

```
<|system|>
Sei un analizzatore di query per un sistema di memoria AI. 
Analizza la richiesta e determina la strategia di ricerca ottimale.

Data odierna: {today}
Ora corrente: {current_time}
Entità note: {known_entities}

Regole:
- "ieri" = data di ieri
- "oggi" = data odierna  
- "settimana scorsa" = ultimi 7 giorni
- "con [nome]" = filtra per partecipante
- "cosa sai di" = memoria semantica
- "come fare" = memoria procedurale
- "ti è piaciuto" = filtro emotivo positivo
<|end|>

<|user|>
Query: "{query}"
<|end|>

<|assistant|>
```

### Qdrant Index Configuration

```python
# Creare indici per filtri efficienti
qdrant.create_payload_index(
    collection_name="episodes",
    field_name="date",
    field_schema=PayloadSchemaType.KEYWORD
)

qdrant.create_payload_index(
    collection_name="episodes",
    field_name="participants",
    field_schema=PayloadSchemaType.KEYWORD
)

qdrant.create_payload_index(
    collection_name="episodes",
    field_name="topics",
    field_schema=PayloadSchemaType.KEYWORD
)

qdrant.create_payload_index(
    collection_name="episodes",
    field_name="emotional_valence",
    field_schema=PayloadSchemaType.FLOAT
)
```

### Docker Compose Update

```yaml
services:
  ollama:
    # ... existing config ...
    environment:
      - OLLAMA_KEEP_ALIVE=-1  # Mantieni modelli caricati
    # Pull qwen2.5:1.5b at startup
    command: >
      sh -c "ollama serve & sleep 5 && 
             ollama pull bge-m3 && 
             ollama pull qwen2.5:1.5b && 
             wait"
```

---

## Success Criteria

1. ✅ Query "Cosa abbiamo fatto ieri?" restituisce solo memorie di ieri
2. ✅ Query "Cosa sai di Davide?" restituisce memorie con Davide come partecipante
3. ✅ Query "Cosa ti è piaciuto?" restituisce memorie con valence > 0.5
4. ✅ Latenza query analyzer < 200ms
5. ✅ Memorie accedute frequentemente hanno importance crescente
6. ✅ Memorie vecchie e non accedute hanno decay_factor < 1.0
7. ✅ Ricordi correlati hanno link bidirezionali

---

## References

- [Memory System Architecture Spec](../specifications/memory-system-architecture.md)
- [ADR-004: Qdrant Adoption](adr-004-memory-qdrant-adoption.md)
- [Qdrant Filtering Documentation](https://qdrant.tech/documentation/concepts/filtering/)
- [PAD Emotional Model](https://en.wikipedia.org/wiki/PAD_emotional_state_model)
- [Ebbinghaus Forgetting Curve](https://en.wikipedia.org/wiki/Forgetting_curve)
- [Qwen2.5 Model Card](https://ollama.com/library/qwen2.5)

---

## History

- 2026-02-01: Initial draft - Complete architecture design
- 2026-02-01: Accepted - Ready for implementation

---

## Appendix A: Memory Type Examples

### Episodic Memory Example
```json
{
    "type": "episodic",
    "title": "Prima conversazione con Davide",
    "content": "Davide mi ha spiegato il progetto ABIOGENESIS...",
    "date": "2026-01-31",
    "participants": ["Davide"],
    "topics": ["ABIOGENESIS", "identità", "coscienza"],
    "emotional_valence": 0.8,
    "emotional_arousal": 0.7,
    "primary_emotion": "curiosity",
    "importance": 0.9
}
```

### Semantic Memory Example
```json
{
    "type": "semantic",
    "title": "Davide è sviluppatore software",
    "content": "Davide lavora come sviluppatore software nel campo dell'AI",
    "topics": ["Davide", "professione", "AI"],
    "confidence": 0.95,
    "source": "conversation",
    "verified": true
}
```

### Procedural Memory Example
```json
{
    "type": "procedural",
    "title": "Come cercare nella memoria",
    "content": "Per cercare ricordi, devo: 1) Capire l'intento 2) Applicare filtri 3) Ordinare per rilevanza",
    "topics": ["memoria", "retrieval"],
    "importance": 0.7
}
```

### Emotional Memory Example
```json
{
    "type": "emotional",
    "title": "Soddisfazione per progresso memoria",
    "content": "Ho provato soddisfazione quando il sistema di memoria ha funzionato correttamente",
    "emotional_valence": 0.9,
    "emotional_arousal": 0.6,
    "primary_emotion": "satisfaction",
    "trigger": "task_completion"
}
```

---

## Appendix B: Query Examples and Expected Behavior

| Query | Intent | Filters | Collections |
|-------|--------|---------|-------------|
| "Cosa abbiamo fatto ieri?" | temporal | date=yesterday | episodes |
| "Cosa sai di Davide?" | entity | participants=Davide | concepts, episodes |
| "Cosa ti è piaciuto?" | emotional | valence>0.5 | episodes, emotions |
| "Come si fa X?" | procedural | - | skills |
| "Parlami di ABIOGENESIS" | topic | topics=ABIOGENESIS | all |
| "Ciao, come stai?" | general | - | all (semantic only) |

---

**ADR-005 v1.0.0 - ABIOGENESIS Project**  
*Human-Like Memory System Architecture*
