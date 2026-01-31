# ADR-004: Memory System Architecture - Qdrant Vector Database Adoption

**Status**: Accepted
**Date**: 2026-01-31
**Author**: ABIOGENESIS Team

## Context

Il sistema di memoria di Scarlet richiede capacità di archiviazione e recupero vettoriale per supportare:
- **Episodic Memory**: Ricerca per similarità di esperienze passate
- **Semantic Memory**: Ricerca per similarità di concetti e conoscenze
- **Emotional Memory**: Pattern matching emozionale
- **Retrieval Scalability**: Supporto per anni di conversazioni

Letta fornisce:
- Memory blocks (5 blocks: persona, human, goals, session_context, constraints)
- Archival memory con passages (search automatico)

Ma Letta NON fornisce:
- Vector similarity search avanzata
- Hybrid search (dense + sparse vectors)
- Quantization per efficienza RAM
- Distributed deployment
- Multi-collection management

**Qdrant v1.16** offre tutte queste capacità out-of-the-box.

## Decision

Adottare **Qdrant v1.16** come vector database primario per Long-Term Memory di Scarlet.

### Architettura Decision

```
┌─────────────────────────────────────────────────────────────────┐
│                    SCARLET MEMORY ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  LAYER 1: WORKING MEMORY (200K token context)             │  │
│  │  - Letta core memory blocks                               │  │
│  │  - MiniMax-M2.1 context window                            │  │
│  └───────────────────────────────────────────────────────────┘  │
│                            ↓                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  LAYER 2: CORE MEMORY (5 Letta blocks)                    │  │
│  │  - persona: Identità e carattere                          │  │
│  │  - human: Informazioni sull'umano                         │  │
│  │  - goals: Obiettivi correnti                              │  │
│  │  - session_context: Contesto sessione                     │  │
│  │  - constraints: Vincoli operativi (read-only)             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                            ↓                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  LAYER 3: LONG-TERM MEMORY (Qdrant + PostgreSQL)          │  │
│  │                                                           │  │
│  │  Qdrant Collections:                                      │  │
│  │  ┌─────────────┬─────────────┬─────────────────────────┐  │  │
│  │  │ Collection  │ Vector Size │ Scopo                   │  │  │
│  │  ├─────────────┼─────────────┼─────────────────────────┤  │  │
│  │  │ episodes    │ 1024        │ Episodic similarity     │  │  │
│  │  │ concepts    │ 1024        │ Semantic knowledge      │  │  │
│  │  │ skills      │ 1024        │ Procedural memory       │  │  │
│  │  │ emotions    │ 512         │ Emotional patterns      │  │  │
│  │  └─────────────┴─────────────┴─────────────────────────┘  │  │
│  │                                                           │  │
│  │  PostgreSQL Tables:                                       │  │
│  │  - concept_relations (graph edges)                        │  │
│  │  - episodic_temporal (temporal edges)                     │  │
│  │  - skill_prerequisites (learning paths)                   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                            ↓                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  LAYER 4: SELF-MODEL (Evolving Identity)                  │  │
│  │  - Meta-cognitive patterns                                │  │
│  │  - Identity evolution over time                           │  │
│  │  - Values and beliefs                                     │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Qdrant Configuration

```yaml
# docker-compose.yml service
qdrant:
  image: qdrant/qdrant:v1.16.0
  container_name: abiogenesis-qdrant
  ports:
    - "6333:6333"  # REST API
    - "6334:6334"  # gRPC API
  volumes:
    - qdrant_data:/qdrant/storage
  environment:
    - QDRANT__SERVICE__API_TIMEOUT=30
    - QDRANT__STORAGE__OPTIMIZE_THRESHOLD=1024
    # Performance settings
    - QDRANT__STORAGE__PERFORMANCE_UPDATE_RATE=20
    - QDRANT__STORAGE__SEARCH_MAX_THREADS=4
  deploy:
    resources:
      reservations:
        memory: 2G
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:6333/dashboard"]
    interval: 30s
    timeout: 10s
    retries: 5
  restart: unless-stopped
  networks:
    - abiogenesis-net
```

### Embeddings Configuration

- **Model**: BGE-m3 (1024 dimensioni)
- **Provider**: Ollama (GPU-accelerated)
- **Collection Mapping**:
  - `episodes` → Full BGE-m3 (1024 dim)
  - `concepts` → Full BGE-m3 (1024 dim)
  - `skills` → Full BGE-m3 (1024 dim)
  - `emotions` → Truncated (512 dim)

### Collections Schema

```python
# episodes collection
CollectionConfig(
    vectors=VectorParams(
        size=1024,
        distance=Distance.COSINE,
        on_disk=True
    ),
    optimizers=OptimizersConfigDiff(
        default_segment_number=2,
        max_optimization_threads=4
    ),
    hnsw_config=HnswConfigDiff(
        m=16,
        ef_construct=100,
        full_scan_threshold=10000
    )
)

# emotions collection (smaller vectors for efficiency)
CollectionConfig(
    vectors=VectorParams(
        size=512,
        distance=Distance.COSINE,
        on_disk=True
    ),
    quantization=QuantizationConfig(
        scalar=ScalarQuantization(
            type=ScalarType.INT8,
            always_ram=True  # Keep in RAM for fast access
        )
    )
)
```

## Consequences

### Positive
- **Hybrid Search**: Dense + sparse vector search per ricerche più accurate
- **Quantization**: 97% riduzione RAM (INT8 quantization)
- **SIMD Acceleration**: VLLM integration per performance
- **Distributed**: Supporto nativo per deployment distribuito
- **Scalability**: Milioni di vettori senza degradazione performance
- **Cost-Effective**: Storage efficiente (~35MB/anno per anni di conversazioni)

### Negative
- **Nuovo Componente**: Aggiunge complessità operativa
- **Doppia Gestione**: Memoria in Letta + vettori in Qdrant
- **Sync Complexity**: Mantenere consistenza tra i due sistemi

### Neutral
- **Operatore Aggiuntivo**: `docker compose` deve includere Qdrant
- **Monitoring Aggiuntivo**: Dashboard Qdrant disponibile su porta 6333

## Alternatives Considered

### Alternative 1: Neo4j per Vector Search
**Descrizione**: Usare Neo4j con vector search index.
**Motivo Rifiuto**: Neo4j vector search è ancora in beta, meno performante di Qdrant per pure vector operations.

### Alternative 2: PostgreSQL + pgvector
**Descrizione**: Usare PostgreSQL con estensione pgvector.
**Motivo Rifiuto**: Meno flessibile per hybrid quantization ris search epetto a Qdrant nativo.

### Alternative 3: Solo Letta Archival Memory
**Descrizione**: Limitarsi a Letta passages/archival memory.
**Motivo Rifiuto**: Letta non offre advanced vector search features necessarie per retrieval umano-like.

## References

- **Qdrant Documentation**: https://qdrant.tech/documentation/
- **Memory System Architecture**: `docs/specifications/memory-system-architecture.md`
- **Master Plan**: `docs/MASTER_PLAN.md`
- **Letta Memory System**: https://docs.letta.com/

## History

- 2026-01-31: ABIOGENESIS Team - Initial decision (Accepted)
- 2026-01-31: Step 1 of Memory Enhancement phase

---

**ADR v1.0.0 - ABIOGENESIS Project**
*Vedi anche: [CONTEXT.md](../../CONTEXT.md), [PROJECT_RULES.md](../../PROJECT_RULES.md)*
