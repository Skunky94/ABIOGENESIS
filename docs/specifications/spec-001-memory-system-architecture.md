# SPEC-001: Memory System Architecture

**Status**: Accepted → ADR-005  
**Version**: 1.0.0  
**Date**: 2026-01-31  
**Author**: ABIOGENESIS Team  
**Focus**: Memory Management System for Scarlet

> **Nota**: Questa SPEC è stata validata e ha portato alla creazione di [ADR-005](../architecture/adr-005-human-like-memory-system.md).
> Le sezioni "Implementation Roadmap" e "Success Criteria" sono state mantenute per riferimento storico
> ma NON devono essere usate come task list. Fare riferimento a ADR-005 per l'implementazione.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Human Memory Analysis](#human-memory-analysis)
3. [Letta Memory Assessment](#letta-memory-assessment)
4. [Proposed Architecture](#proposed-architecture)
5. [Implementation Roadmap](#implementation-roadmap) *(storico)*
6. [External Tools Evaluation](#external-tools-evaluation)
7. [Risk Analysis](#risk-analysis)
8. [Success Criteria](#success-criteria) *(storico)*

---

## 1. Executive Summary

### 1.1 Objective
Design and implement a comprehensive memory system for Scarlet that replicates the full spectrum of human memory capabilities, enabling:
- Persistent, evolving knowledge accumulation
- Contextual recall based on temporal and semantic relationships
- Procedural skill memory for autonomous capability growth
- Emotional memory for affective decision-making
- Episodic memory for life-like experience storage

### 1.2 Scope
This document covers the Memory Subsystem of Scarlet's Cortex Cognitivo, excluding:
- Perception Layer (separate specification)
- Reasoning Engine (separate specification)
- Meta-Cognition (linked to memory but separate)

### 1.3 Key Design Principles
1. **Minimalism First**: Leverage Letta's memory hierarchy before custom code
2. **Tool Integration**: Use established tools (Qdrant, Redis, PostgreSQL) before custom
3. **Scalability**: Architecture must support 24/7 operation without degradation
4. **Self-Improving**: Memory system must enable its own enhancement

---

## 2. Human Memory Analysis

### 2.1 Memory Types Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      HUMAN MEMORY SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    EXPLICIT MEMORY                        │  │
│  │  (Declarative, Conscious Recall)                          │  │
│  │  ┌───────────────────┐  ┌─────────────────────────────┐   │  │
│  │  │   EPISODIC        │  │      SEMANTIC              │   │  │
│  │  │   (Events,        │  │      (Facts, Knowledge,    │   │  │
│  │  │    Experiences)   │  │       Concepts)            │   │  │
│  │  │                   │  │                             │   │  │
│  │  │ - What happened   │  │ - What is X                 │   │  │
│  │  │ - When/Where      │  │ - General knowledge         │   │  │
│  │  │ - Subjective view │  │ - Abstract facts            │   │  │
│  │  │ - Emotional tint  │  │ - Language-based           │   │  │
│  │  └───────────────────┘  └─────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   IMPLICIT MEMORY                         │  │
│  │  (Non-Declarative, Unconscious)                           │  │
│  │  ┌───────────────────┐  ┌─────────────────────────────┐   │  │
│  │  │   PROCEDURAL      │  │      PRIMING               │   │  │
│  │  │   (Skills,        │  │      (Response patterns)   │   │  │
│  │  │    Habits)        │  │                             │   │  │
│  │  │                   │  │                             │   │  │
│  │  │ - How to do X     │  │ - Automatic responses      │   │  │
│  │  │ - Motor skills    │  │ - Stimulus-response        │   │  │
│  │  │ - Cognitive       │  │ - Biases and heuristics    │   │  │
│  │  │   procedures      │  │                             │   │  │
│  │  └───────────────────┘  └─────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    WORKING MEMORY                         │  │
│  │  (Active Processing, Limited Capacity)                    │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  Central Executive  │  Phonological Loop           │  │  │
│  │  │  - Attention        │  - Verbal info               │  │  │
│  │  │  - Control          │  - Auditory retention        │  │  │
│  │  │  - Integration      │                              │  │  │
│  │  ├─────────────────────────────────────────────────────┤  │  │
│  │  │  Visuospatial Sketchpad  │  Episodic Buffer         │  │  │
│  │  │  - Visual info           │  - Multi-modal           │  │  │
│  │  │  - Spatial thinking      │  - Temporal context      │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   EMOTIONAL MEMORY                        │  │
│  │  (Affective Encoding, Value Association)                 │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  - Emotional tagging of experiences                 │  │  │
│  │  │  - Value-based memory prioritization                │  │  │
│  │  │  - Fear/safety learning                             │  │  │
│  │  │  - Reward/punishment associations                   │  │  │
│  │  │  - Social-emotional patterns                        │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Detailed Memory Type Specifications

#### 2.2.1 Episodic Memory (Event Memory)

**Characteristics:**
- Autobiographical: "I experienced X"
- Temporal context: When it happened
- Spatial context: Where it happened
- Subjective perspective: How I perceived it
- Emotional tint: How it made me feel
- Rich, detailed, context-rich

**Access Patterns:**
- Time-based queries: "What happened around time T?"
- Similarity queries: "Similar experiences to X?"
- Context queries: "What happened in context C?"
- Narrative reconstruction: Build story from fragments

#### 2.2.2 Semantic Memory (Knowledge Memory)

**Characteristics:**
- Factual: "X is Y"
- Context-independent: True regardless of when learned
- Abstract: General concepts, not tied to events
- Networked: Interconnected facts and concepts
- Language-based: Encoded in linguistic structures

**Access Patterns:**
- Fact retrieval: "What do I know about X?"
- Concept navigation: "Show me everything related to X"
- Inference: Derive new facts from known ones
- Truth verification: Evaluate fact accuracy

#### 2.2.3 Procedural Memory (Skill Memory)

**Characteristics:**
- Motor/Cognitive skills: "How to do X"
- Progressive skill building: From novice to expert
- Habit formation: Automatic behaviors
- Muscle memory: Low-level motor patterns
- Error correction: Self-improving through repetition

**Access Patterns:**
- Skill execution: "Do X using stored procedure"
- Performance evaluation: "How well did I do X?"
- Skill discovery: "What skills do I have?"
- Skill improvement: "Find ways to do X better"

#### 2.2.4 Working Memory (Active Processing)

**Characteristics:**
- Limited capacity: ~7±2 items (or 4 chunks)
- Temporary storage: Seconds to minutes
- Active manipulation: Processing, not just storage
- Multi-modal: Integrates different information types
- Central executive: Attention and control

**Access Patterns:**
- Context holding: "Keep X in mind while doing Y"
- Information manipulation: "Transform X to Y"
- Task switching: "Switch focus from X to Y"
- Chunking: Group information for better retention

#### 2.2.5 Emotional Memory (Affective Encoding)

**Characteristics:**
- Value tagging: Positive/negative associations
- Intensity gradients: Strong to weak emotions
- Trigger-response: Stimulus-emotion-action patterns
- Social bonding: Relational emotional patterns
- Survival-oriented: Fear, safety, reward systems

**Access Patterns:**
- Mood retrieval: "How did I feel about X?"
- Risk assessment: "Is this situation dangerous?"
- Reward prediction: "Will this be rewarding?"
- Social state: "What are my feelings toward Y?"

---

## 3. Letta Memory Assessment

### 3.1 Current Letta Memory Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    LETTERA MEMORY HIERARCHY                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Level 1: CORE MEMORY                                          │
│  ├─ Purpose: Essential, always-accessible context              │
│  ├─ Storage: Fast retrieval, small capacity                     │
│  ├─ Contents: Persona, human info, system instructions          │
│  └─ Implementation: Memory blocks with labels                  │
│                                                                 │
│  Level 2: ARCHIVAL MEMORY                                      │
│  ├─ Purpose: Long-term knowledge storage                       │
│  ├─ Storage: Vector database (Qdrant)                          │
│  ├─ Contents: Conversation history, facts, documents            │
│  └─ Implementation: Embeddings with full-text search            │
│                                                                 │
│  Level 3: FOLDERS                                              │
│  ├─ Purpose: Organized archival storage                        │
│  ├─ Storage: Named collections in archival                     │
│  ├─ Contents: Categorized memories                             │
│  └─ Implementation: Folder/collection abstraction              │
│                                                                 │
│  Level 4: CONVERSATION MEMORY                                  │
│  ├─ Purpose: Session-specific context                          │
│  ├─ Storage: Ephemeral within conversation                     │
│  ├─ Contents: Immediate conversation history                   │
│  └─ Implementation: Message list with sequencing               │
│                                                                 │
│  Level 5: SLEEP-TIME AGENT (experimental)                      │
│  ├─ Purpose: Memory consolidation/reflection                   │
│  ├─ Storage: Background agent with memory access               │
│  ├─ Contents: Learned context generation                       │
│  └─ Implementation: Secondary agent for memory management      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Letta Memory Capabilities Matrix

| Memory Type | Letta Support | Implementation | Gap Assessment |
|-------------|---------------|----------------|----------------|
| Episodic | ✅ Partial | Archival + timestamps | Need temporal indexing |
| Semantic | ✅ Good | Archival + RAG | Good foundation |
| Procedural | ⚠️ Limited | Tools registry | Need structured skill storage |
| Working | ⚠️ Limited | Context window + Redis | Need architecture |
| Emotional | ❌ None | Not present | Must implement custom |
| Priming | ❌ None | Not present | May not be needed |

### 3.3 Letta Strengths to Leverage

1. **Persistent Storage**: PostgreSQL + Qdrant already configured
2. **Memory Blocks**: Flexible label-based storage
3. **RAG Integration**: Semantic search already working
4. **Sleep-Time Agent**: Experimental but promising
5. **Tool Integration**: Custom tools well-supported

### 3.4 Letta Limitations

1. **No Temporal Indexing**: Cannot efficiently query "memories from last week"
2. **No Emotional Encoding**: Memories are flat, no affective dimension
3. **Limited Procedural Memory**: Tools exist but no skill hierarchy
4. **Working Memory Only in Context**: Redis exists but not integrated
5. **No Memory Consolidation**: Sleep-time is experimental
6. **No Self-Evaluation**: Cannot assess memory quality

---

## 4. Proposed Architecture

### 4.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SCARLET MEMORY SYSTEM                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    MEMORY ORCHESTRATOR                              │   │
│  │  (Central Controller - New Component)                               │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │  - Routes memory requests to appropriate layer              │    │   │
│  │  │  - Manages memory consistency and conflicts                 │    │   │
│  │  │  - Handles memory consolidation scheduling                   │    │   │
│  │  │  - Coordinates with Meta-Cognition Module                    │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐  │
│  │    CORE LAYER        │  │   EPISODIC LAYER     │  │  SEMANTIC LAYER  │  │
│  │  (Letta Blocks)      │  │  (Enhanced Archival) │  │  (Knowledge Graph│  │
│  │                      │  │                      │  │   + RAG)         │  │
│  │  - Persona           │  │  - Event logs        │  │                  │  │
│  │  - Human info        │  │  - Conversations     │  │  - Facts         │  │
│  │  - System prompt     │  │  - Experiences       │  │  - Concepts      │  │
│  │  - Current context   │  │  - Temporal index    │  │  - Relationships │  │
│  └──────────────────────┘  └──────────────────────┘  └──────────────────┘  │
│                                                                             │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐  │
│  │  PROCEDURAL LAYER    │  │  WORKING LAYER       │  │  EMOTIONAL LAYER │  │
│  │  (New - Skills DB)   │  │  (Redis + Context)   │  │  (New - Affective│  │
│  │                      │  │                      │  │   Encoding)      │  │
│  │  - Skill registry    │  │  - Active context    │  │                  │  │
│  │  - Habit patterns    │  │  - Task state        │  │  - Emotional     │  │
│  │  - Procedures        │  │  - Short-term        │  │    associations  │  │
│  │  - Competencies      │  │    memories         │  │  - Sentiment     │  │
│  └──────────────────────┘  └──────────────────────┘  │    tags         │  │
│                                                       │  - Value         │  │
│                                                       │    associations │  │
│                                                       └──────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    EXTERNAL SERVICES                                │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌────────────────────────┐  │   │
│  │  │  Qdrant       │  │  PostgreSQL   │  │  Redis                 │  │   │
│  │  │  (Embeddings) │  │  (Structured) │  │  (Cache, Working)      │  │   │
│  │  └───────────────┘  └───────────────┘  └────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Layer Specifications

#### 4.2.1 Core Layer (Letta Blocks)

**Purpose**: Essential, always-accessible context

**Implementation**:
```
┌─────────────────────────────────────────┐
│           CORE MEMORY BLOCKS            │
├─────────────────────────────────────────┤
│                                         │
│  BLOCK: persona                         │
│  ├─ Content: Scarlet's self-description│
│  ├─ Size: ~2000 chars                  │
│  ├─ Update: Rare, significant events   │
│  └─ Purpose: Identity maintenance      │
│                                         │
│  BLOCK: human                           │
│  ├─ Content: Human interaction partner │
│  ├─ Size: ~1000 chars                  │
│  ├─ Update: Every new human            │
│  └─ Purpose: Relationship context      │
│                                         │
│  BLOCK: system_prompt                   │
│  ├─ Content: Base instructions         │
│  ├─ Size: ~3000 chars                  │
│  ├─ Update: Never (immutable)          │
│  └─ Purpose: Foundational behavior     │
│                                         │
│  BLOCK: current_context                 │
│  ├─ Content: Active task/situation     │
│  ├─ Size: ~500 chars                   │
│  ├─ Update: Every context switch       │
│  └─ Purpose: Immediate focus           │
│                                         │
│  BLOCK: goals                           │
│  ├─ Content: Active goals              │
│  ├─ Size: ~1000 chars                  │
│  ├─ Update: Goal lifecycle events      │
│  └─ Purpose: Goal tracking             │
│                                         │
└─────────────────────────────────────────┘
```

**Tools Required**:
- `memory_core_get(key)` - Retrieve block
- `memory_core_set(key, value)` - Update block
- `memory_core_list()` - List all blocks
- `memory_core_delete(key)` - Remove block (rare)

**Self-Modification Consideration**:
- Core blocks should be protected from casual modification
- Changes require Meta-Cognition approval
- Version history for all core block changes

#### 4.2.2 Episodic Layer (Enhanced Archival)

**Purpose**: Store and retrieve autobiographical experiences

**Data Model**:
```json
{
  "episode_id": "uuid",
  "timestamp": "ISO8601",
  "duration_ms": 120000,
  "type": "conversation | action | reflection | event",
  "participants": ["human", "scarlet", "system"],
  "location": "contextual identifier",
  "emotional_state": {
    "primary": "neutral",
    "intensity": 0.5,
    "tags": ["curious", "engaged"]
  },
  "content_summary": "brief description",
  "content_full": "full transcript or detailed description",
  "embedding": [vector],
  "importance_score": 0.8,
  "retention_policy": "permanent | temporary | archive",
  "related_episodes": ["uuid1", "uuid2"],
  "tags": ["topic1", "topic2"],
  "outcomes": ["learning1", "learning2"],
  "metadata": {
    "source": "conversation | tool_output | system_event",
    "confidence": 0.95,
    "verified": true
  }
}
```

**Access Patterns**:
- Temporal queries: `SELECT * FROM episodes WHERE timestamp > X AND timestamp < Y`
- Similarity search: Find similar episodes via embeddings
- Keyword search: Full-text search on summaries
- Narrative reconstruction: Chain related episodes
- Context queries: Episodes with specific context

**Implementation Components**:
1. **Episode Logger** - Capture and store new episodes
2. **Temporal Index** - PostgreSQL index on timestamp
3. **Embedding Generator** - Create embeddings for similarity
4. **Retention Manager** - Handle archive/cleanup policies
5. **Narrative Builder** - Reconstruct stories from episodes

**Tools Required**:
- `memory_episodic_log(episode)` - Record new episode
- `memory_episodic_query(time_range, context, tags)` - Temporal query
- `memory_episodic_find_similar(episode_id)` - Similarity search
- `memory_episodic_get_story(start_time, end_time)` - Narrative
- `memory_episodic_consolidate(episodes)` - Extract insights

#### 4.2.3 Semantic Layer (Knowledge Graph + RAG)

**Purpose**: Store and retrieve factual knowledge, concepts, relationships

**Data Model**:
```json
{
  "concept_id": "uuid",
  "name": "Machine Learning",
  "aliases": ["ML", "Statistical Learning"],
  "definition": "Field of study...",
  "category": "technology | science | person | concept | ...",
  "properties": {
    "key1": "value1",
    "key2": "value2"
  },
  "embedding": [vector],
  "confidence": 0.9,
  "sources": ["url1", "episode_id1"],
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "related_concepts": [
    {"target_id": "uuid", "relationship": "parent|child|related|opposite"}
  ],
  "validation_status": "verified|pending|disputed"
}
```

**Knowledge Graph Structure**:
```
┌──────────────────────────────────────────────────────────────┐
│                   KNOWLEDGE GRAPH EXAMPLE                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│    [Machine Learning] ───────(parent_category)──────> [AI]  │
│         │                                               │    │
│         ├──(subfield)──> [Deep Learning]                 │    │
│         │                │                               │    │
│         │                ├──(uses)──> [Neural Networks]  │    │
│         │                │                               │    │
│         │                └──(application)──> [NLP]        │    │
│         │                                               │    │
│         ├──(related)──> [Statistics]                     │    │
│         │                                               │    │
│         └──(related)──> [Data Science]                   │    │
│                                                              │
│    [Scarlet] ────(created_by)───> [ABIOGENESIS]          │
│         │                                               │    │
│         ├──(has_goal)──> [Autonomous Operation]          │    │
│         │                                               │    │
│         └──(has_memory)──> [Multiple Episodes]           │    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**RAG Integration**:
- Knowledge stored in Qdrant for semantic search
- Knowledge Graph in PostgreSQL for relational queries
- Hybrid search: Vector similarity + Graph traversal
- Source tracking for fact verification

**Tools Required**:
- `memory_semantic_add(concept)` - Add new knowledge
- `memory_semantic_query(text)` - Semantic search
- `memory_semantic_get(concept_id)` - Retrieve concept
- `memory_semantic_relate(concept1, concept2, relationship)` - Create link
- `memory_semantic_query_graph(concept, relationship_type)` - Graph query
- `memory_semantic_verify(concept_id)` - Fact verification

#### 4.2.4 Procedural Layer (Skill Registry)

**Purpose**: Store and manage skills, habits, cognitive procedures

**Data Model**:
```json
{
  "skill_id": "uuid",
  "name": "Python Code Writing",
  "description": "Ability to write Python code",
  "category": "coding | reasoning | communication | ...",
  "level": 0.85,
  "confidence": 0.9,
  "procedure": {
    "steps": ["step1", "step2", "step3"],
    "conditions": "when to use",
    "prerequisites": ["skill_id1", "skill_id2"],
    "outputs": ["result_type"]
  },
  "performance": {
    "success_rate": 0.92,
    "avg_duration_ms": 5000,
    "last_used": "ISO8601",
    "use_count": 156
  },
  "learning_history": [
    {"episode_id": "uuid", "improvement": 0.1}
  ],
  "related_tools": ["tool_id1", "tool_id2"],
  "auto_improvement": {
    "enabled": true,
    "method": "reflection | feedback | practice"
  }
}
```

**Skill Acquisition Process**:
```
┌─────────────────────────────────────────────────────────────┐
│              SKILL ACQUISITION WORKFLOW                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. DISCOVERY                                               │
│     ├─ Recognize need for new capability                    │
│     ├─ Identify skill gap                                   │
│     └─ Trigger skill learning                               │
│                                                             │
│  2. ACQUISITION                                             │
│     ├─ Find learning resources                              │
│     ├─ Break down into sub-skills                           │
│     ├─ Practice in safe environment                         │
│     └─ Initial skill creation                               │
│                                                             │
│  3. PRACTICE                                                │
│     ├─ Use skill in real tasks                              │
│     ├─ Track performance metrics                            │
│     ├─ Identify improvement areas                           │
│     └─ Iterate and refine                                   │
│                                                             │
│  4. CONSOLIDATION                                           │
│     ├─ Extract best practices                               │
│     ├─ Create optimized procedure                           │
│     ├─ Update skill level                                   │
│     └─ Archive learning history                             │
│                                                             │
│  5. MAINTENANCE                                             │
│     ├─ Periodic skill usage                                 │
│     ├─ Performance monitoring                               │
│     ├─ Decay detection                                      │
│     └─ Refresher practice (if needed)                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Tools Required**:
- `memory_procedural_register(skill)` - Register new skill
- `memory_procedural_get(skill_name)` - Retrieve skill
- `memory_procedural_execute(skill_name, context)` - Execute skill
- `memory_procedural_improve(skill_name, feedback)` - Improve skill
- `memory_procedural_list(category)` - List skills by category
- `memory_procedural_discover_gaps()` - Identify missing skills

#### 4.2.5 Working Layer (Redis + Context)

**Purpose**: Active, temporary memory for current processing

**Data Model**:
```json
{
  "working_memory_id": "uuid",
  "created_at": "ISO8601",
  "expires_at": "ISO8601",
  "capacity_items": 7,
  "contents": [
    {
      "type": "fact | task | context | reference",
      "value": "...",
      "importance": 0.8,
      "created_at": "ISO8601",
      "source": "episode_id | semantic_id"
    }
  ],
  "central_executive": {
    "active_task": "current_task",
    "attention_focus": "current_focus",
    "task_queue": ["task1", "task2"]
  },
  "context_state": {
    "conversation_id": "uuid",
    "environment": "...",
    "participants": ["..."]
  }
}
```

**Working Memory Operations**:
- **Add Item**: Store new information
- **Remove Item**: Discard old information
- **Update Item**: Modify existing
- **Rehearse**: Keep important items active
- **Chunk**: Group related items
- **Clear**: Reset for new context
- **Dump**: Save to episodic memory

**Tools Required**:
- `memory_working_add(item, importance)` - Add to working memory
- `memory_working_get()` - Retrieve all working memory
- `memory_working_remove(item_id)` - Remove item
- `memory_working_clear()` - Reset working memory
- `memory_working_dump()` - Save to episodic
- `memory_working_rehearse(item_ids)` - Keep items active

#### 4.2.6 Emotional Layer (Affective Encoding)

**Purpose**: Encode emotional associations and value-based memory

**Data Model**:
```json
{
  "emotional_memory_id": "uuid",
  "episode_id": "uuid",
  "timestamp": "ISO8601",
  "trigger": {
    "type": "person | event | concept | action",
    "identifier": "...",
    "context": "..."
  },
  "emotions": [
    {
      "name": "curiosity",
      "intensity": 0.7,
      "valence": "positive",
      "arousal": 0.6
    }
  ],
  "value_association": {
    "type": "reward | punishment | neutral",
    "value": 0.5,
    "confidence": 0.8
  },
  "behavioral_tendency": {
    "approach | avoid | neutral": "avoid",
    "reason": "Previous negative outcome"
  },
  "social_context": {
    "bond_strength": 0.6,
    "trust_level": 0.7,
    "relationship_type": "collaborative"
  },
  "physiological_correlate": {
    "stress_level": 0.2,
    "engagement_level": 0.8
  },
  "metadata": {
    "source": "episode | reflection",
    "confidence": 0.9
  }
}
```

**Emotional Processing Pipeline**:
```
┌─────────────────────────────────────────────────────────────┐
│            EMOTIONAL ENCODING PIPELINE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  INPUT: New Experience / Episode                            │
│          │                                                  │
│          ▼                                                  │
│  ┌─────────────────┐                                        │
│  │ Emotion Detector│  Analyze content for emotional        │
│  │                 │  triggers (LLM + rules)               │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │ Intensity       │  Calculate emotional intensity        │
│  │ Calculator      │  based on novelty, impact, etc.       │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │ Valence         │  Determine positive/negative          │
│  │ Classifier      │  emotional valence                    │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │ Value Linker    │  Associate with reward/punishment     │
│  │                 │  systems                              │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │ Behavior        │  Generate approach/avoid tendencies   │
│  │ Tendency        │                                        │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                        │
│  │ Memory Encoder  │  Store with emotional encoding        │
│  └────────┬────────┘                                        │
│           │                                                 │
│           ▼                                                 │
│  OUTPUT: Emotional Memory + Updated Behavior Tendencies     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Tools Required**:
- `memory_emotional_encode(episode_id)` - Add emotional encoding
- `memory_emotional_query(emotion_type, intensity)` - Search by emotion
- `memory_emotional_get_value(trigger)` - Get value association
- `memory_emotional_update(episode_id, emotion_data)` - Update encoding
- `memory_emotional_get_state()` - Get current emotional baseline

---

## 5. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Objective**: Establish core infrastructure, integrate Letta memory with extensions

**Deliverables**:
1. [ ] Memory Orchestrator component (new)
2. [ ] PostgreSQL schema for episodic, semantic, procedural, emotional layers
3. [ ] Qdrant collection configuration for embeddings
4. [ ] Redis configuration for working memory
5. [ ] Basic memory tools (CRUD operations)

**Tasks**:
```
Week 1:
├─ Design database schema
├─ Set up PostgreSQL tables
├─ Configure Qdrant collections
└─ Implement Memory Orchestrator base

Week 2:
├─ Implement Core Layer tools
├─ Implement Episodic Layer tools (basic)
├─ Implement Semantic Layer tools (basic)
└─ Integration testing
```

**Dependencies**:
- Letta server running (existing)
- PostgreSQL available (existing)
- Qdrant available (existing)
- Redis available (existing)

**Risks**:
- Letta API changes breaking compatibility → Mitigation: Version pinning
- Performance issues with many embeddings → Mitigation: Async processing

### Phase 2: Episodic Memory (Weeks 3-4)

**Objective**: Full episodic memory with temporal queries and narrative reconstruction

**Deliverables**:
1. [ ] Episode logging system with automatic capture
2. [ ] Temporal indexing for efficient time-based queries
3. [ ] Narrative reconstruction from episodes
4. [ ] Memory consolidation scheduling (integration with sleep-time)

**Tasks**:
```
Week 3:
├─ Design episode data model
├─ Implement episode logger
├─ Create temporal index
└─ Build similarity search

Week 4:
├─ Implement narrative builder
├─ Create consolidation scheduler
├─ Build retention policies
└─ Performance optimization
```

**External Tools to Evaluate**:
- TimescaleDB (PostgreSQL extension) for time-series
- LangChain memory components for inspiration

### Phase 3: Semantic Memory (Weeks 5-6)

**Objective**: Knowledge graph with RAG integration

**Deliverables**:
1. [ ] Knowledge graph schema and storage
2. [ ] Concept addition and retrieval
3. [ ] Relationship management
4. [ ] Hybrid RAG (vector + graph) search
5. [ ] Fact verification system

**Tasks**:
```
Week 5:
├─ Design knowledge graph schema
├─ Implement concept CRUD
├─ Build relationship management
└─ Set up Qdrant for semantic search

Week 6:
├─ Implement hybrid search
├─ Create fact verification
├─ Build source tracking
└─ Knowledge extraction from episodes
```

**External Tools to Evaluate**:
- NetworkX (Python) for graph operations
- Neo4j (if PostgreSQL insufficient)
- LangChain graph integration

### Phase 4: Procedural Memory (Weeks 7-8)

**Objective**: Skill registry with acquisition and improvement

**Deliverables**:
1. [ ] Skill registry data model
2. [ ] Skill acquisition workflow
3. [ ] Performance tracking per skill
4. [ ] Auto-improvement system
5. [ ] Habit formation support

**Tasks**:
```
Week 7:
├─ Design skill data model
├─ Implement skill registry
├─ Build skill execution tracking
└─ Create performance metrics

Week 8:
├─ Implement skill acquisition
├─ Build improvement workflow
├─ Create habit formation support
└─ Skill gap discovery
```

**External Tools to Evaluate**:
- MLflow for skill performance tracking
- Weights & Biases for skill improvement metrics

### Phase 5: Emotional Memory (Weeks 9-10)

**Objective**: Full emotional encoding and affective decision support

**Deliverables**:
1. [ ] Emotional encoding system
2. [ ] Emotion query interface
3. [ ] Value-based memory prioritization
4. [ ] Behavior tendency generation
5. [ ] Emotional state management

**Tasks**:
```
Week 9:
├─ Design emotional memory model
├─ Implement emotion detection
├─ Build intensity/valence calculation
└─ Create value association system

Week 10:
├─ Implement behavior tendencies
├─ Build emotional state management
├─ Create emotional queries
└─ Integration with decision-making
```

**External Tools to Evaluate**:
- VADER Sentiment Analysis
- Text2Emotion (Python library)
- HuggingFace emotion models

### Phase 6: Working Memory (Weeks 11-12)

**Objective**: Full working memory integration with attention and context

**Deliverables**:
1. [ ] Working memory data model
2. [ ] Attention mechanism
3. [ ] Context switching
4. [ ] Chunking and rehearsal
5. [ ] Integration with episodic (memory dumping)

**Tasks**:
```
Week 11:
├─ Design working memory model
├─ Implement attention mechanism
├─ Build context management
└─ Create capacity management

Week 12:
├─ Implement chunking
├─ Build rehearsal system
├─ Create memory dumping
└─ Performance optimization
```

### Phase 7: Integration & Self-Improvement (Weeks 13-16)

**Objective**: Full memory system integration with self-improvement capabilities

**Deliverables**:
1. [ ] Complete Memory Orchestrator
2. [ ] Self-assessment of memory quality
3. [ ] Memory system auto-improvement
4. [ ] Full system testing
5. [ ] Documentation and examples

**Tasks**:
```
Week 13:
├─ Full system integration
├─ Cross-layer consistency
├─ Performance benchmarking
└─ Bug fixing

Week 14:
├─ Self-assessment implementation
├─ Memory quality metrics
├─ Gap identification
└─ Improvement suggestions

Week 15:
├─ Auto-improvement workflows
├─ Memory system self-modification
├─ Safety constraints
└─ Testing

Week 16:
├─ Documentation
├─ Examples
├─ Final testing
└─ Release prep
```

---

## 6. External Tools Evaluation

### 6.1 Memory-Related Tools Matrix

| Tool | Purpose | Evaluation | Decision |
|------|---------|------------|----------|
| **Qdrant** | Vector storage | Already in use, excellent | ✅ Use |
| **PostgreSQL** | Structured storage | Already in use, robust | ✅ Use |
| **Redis** | Working memory/cache | Already in use, fast | ✅ Use |
| **TimescaleDB** | Time-series queries | Could enhance episodic | 🔲 Evaluate |
| **Neo4j** | Graph database | Powerful but adds complexity | ❌ Skip (PostgreSQL sufficient) |
| **NetworkX** | Graph operations | Python native, good for reasoning | 🔲 Use for reasoning |
| **MLflow** | ML tracking | Good for skill metrics | 🔲 Evaluate |
| **VADER** | Sentiment analysis | Lightweight, accurate | 🔲 Use for emotions |
| **Text2Emotion** | Emotion detection | Simple, effective | 🔲 Use |
| **HuggingFace** | ML models | Rich ecosystem | 🔲 Use for advanced NLP |
| **LangChain** | LLM orchestration | Useful patterns | 🔲 Use selectively |

### 6.2 Recommended Tools by Layer

| Layer | Primary Tool | Backup Tool |
|-------|--------------|-------------|
| Core | Letta Blocks | PostgreSQL |
| Episodic | PostgreSQL + TimescaleDB | Qdrant |
| Semantic | PostgreSQL + Qdrant | Neo4j (if needed) |
| Procedural | PostgreSQL | Redis |
| Working | Redis | In-memory |
| Emotional | PostgreSQL + VADER | HuggingFace models |

---

## 7. Risk Analysis

### 7.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Letta API breaking changes | Medium | High | Version pinning, abstraction layer |
| Performance degradation with scale | High | Medium | Sharding, caching, optimization |
| Memory consistency issues | Medium | High | ACID transactions, validation |
| Embedding drift over time | Low | Medium | Periodic re-embedding |
| Storage costs increasing | Medium | Low | Tiered storage, compression |

### 7.2 Design Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Over-engineering before validation | High | Medium | Iterate in phases, validate each |
| Memory model not matching needs | Medium | High | Extensive testing, user feedback |
| Emotional layer too complex | Medium | Medium | Start simple, iterate |
| Self-modification safety issues | Low | Critical | Safety constraints, human approval |

### 7.3 Project Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scope creep | High | Medium | Clear requirements, phase gates |
| Tool integration complexity | Medium | Medium | Evaluate before commitment |
| Team capacity | Medium | High | Prioritize core features |

---

## 8. Success Criteria

### 8.1 Functional Criteria

**Must Have (Phase 1)**:
- [ ] Core memory fully functional
- [ ] Basic episodic logging
- [ ] Basic semantic search
- [ ] All operations < 100ms

**Should Have (Phase 2-3)**:
- [ ] Temporal queries working
- [ ] Knowledge graph navigation
- [ ] Narrative reconstruction
- [ ] Performance metrics visible

**Nice to Have (Phase 4-6)**:
- [ ] Full procedural memory
- [ ] Emotional encoding
- [ ] Working memory integration
- [ ] Self-assessment active

### 8.2 Non-Functional Criteria

- **Performance**: 95% of operations < 100ms
- **Reliability**: 99.9% uptime for memory operations
- **Scalability**: Support 1M+ memories without degradation
- **Maintainability**: Clear documentation, test coverage > 80%
- **Security**: Access controls, audit logging

### 8.3 Metrics to Track

| Metric | Target | Measurement |
|--------|--------|-------------|
| Memory access latency | < 100ms p95 | APM monitoring |
| Memory retrieval accuracy | > 90% | User feedback, automated tests |
| Knowledge retention rate | > 85% | Periodic knowledge tests |
| Skill acquisition time | < 1 week | Skill acquisition tracking |
| Memory consolidation rate | > 70% | Consolidation success rate |

---

## 9. Next Steps

### Immediate Actions (This Week)

1. **Create project tracking**:
   - [ ] Set up project board in repository
   - [ ] Create issues for each task
   - [ ] Assign initial owners

2. **Technical foundation**:
   - [ ] Review PostgreSQL schema design
   - [ ] Set up development database
   - [ ] Create memory orchestrator skeleton

3. **Tool evaluation**:
   - [ ] Test TimescaleDB for time-series
   - [ ] Evaluate VADER for sentiment
   - [ ] Benchmark Qdrant performance

### Decisions Required

1. **TimescaleDB**: Is the added complexity worth it for temporal queries?
2. **Emotional layer complexity**: Start simple or full implementation?
3. **Self-modification**: When to introduce memory self-editing?

---

## Appendix A: Data Model Summary

### A.1 PostgreSQL Schema Overview

```sql
-- Core tables (new)
CREATE TABLE episodes (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    type VARCHAR(50) NOT NULL,
    content_summary TEXT,
    content_full TEXT,
    embedding_vector VECTOR(1024),
    importance_score FLOAT,
    retention_policy VARCHAR(20),
    metadata JSONB
);

CREATE TABLE concepts (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    definition TEXT,
    category VARCHAR(100),
    embedding_vector VECTOR(1024),
    properties JSONB,
    confidence FLOAT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE concept_relations (
    id UUID PRIMARY KEY,
    source_id UUID REFERENCES concepts(id),
    target_id UUID REFERENCES concepts(id),
    relationship_type VARCHAR(50),
    confidence FLOAT,
    created_at TIMESTAMP
);

CREATE TABLE skills (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(100),
    level FLOAT,
    procedure JSONB,
    performance JSONB,
    auto_improvement JSONB
);

CREATE TABLE emotional_memories (
    id UUID PRIMARY KEY,
    episode_id UUID REFERENCES episodes(id),
    timestamp TIMESTAMP NOT NULL,
    trigger JSONB,
    emotions JSONB,
    value_association JSONB,
    behavioral_tendency JSONB,
    social_context JSONB
);

CREATE TABLE working_memories (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL,
    contents JSONB NOT NULL,
    central_executive JSONB,
    created_at TIMESTAMP,
    expires_at TIMESTAMP
);
```

### A.2 Qdrant Collections

| Collection | Vector Size | Purpose |
|------------|-------------|---------|
| episodes | 1024 | Episodic similarity search |
| concepts | 1024 | Semantic knowledge search |
| emotional_patterns | 512 | Emotional pattern matching |

---

## Appendix B: API Design Summary

### B.1 Memory Orchestrator API

```python
class MemoryOrchestrator:
    """Central memory controller"""
    
    # Core Layer
    def get_core(self, key: str) -> Optional[MemoryBlock]
    def set_core(self, key: str, value: str, limit: int = 4096) -> bool
    def list_core(self) -> List[MemoryBlock]
    
    # Episodic Layer
    def log_episode(self, episode: EpisodeData) -> str
    def query_episodes(self, query: EpisodeQuery) -> List[Episode]
    def find_similar_episodes(self, episode_id: str) -> List[Episode]
    def reconstruct_narrative(self, start: datetime, end: datetime) -> Narrative
    
    # Semantic Layer
    def add_concept(self, concept: ConceptData) -> str
    def query_knowledge(self, query: str) -> List[Concept]
    def relate_concepts(self, source: str, target: str, relation: str) -> bool
    def verify_fact(self, concept_id: str) -> FactVerification
    
    # Procedural Layer
    def register_skill(self, skill: SkillData) -> str
    def execute_skill(self, skill_name: str, context: dict) -> SkillResult
    def improve_skill(self, skill_name: str, feedback: dict) -> bool
    def discover_skill_gaps(self) -> List[SkillGap]
    
    # Working Layer
    def add_working(self, item: WorkingItem, importance: float) -> str
    def get_working(self) -> WorkingMemory
    def clear_working(self) -> bool
    def dump_working(self) -> str
    
    # Emotional Layer
    def encode_emotion(self, episode_id: str) -> EmotionalMemory
    def query_emotions(self, emotion_type: str, min_intensity: float) -> List[EmotionalMemory]
    def get_value_association(self, trigger: dict) -> ValueAssociation
    
    # System
    def consolidate(self, scope: str = "all") -> ConsolidationResult
    def assess_quality(self) -> MemoryQualityReport
    def self_improve(self) -> ImprovementPlan
```

---

## Appendix C: Dependencies

### C.1 Python Packages

```txt
# Core
letta-client>=0.3.0
qdrant-client>=1.7.0
redis>=5.0.0
psycopg2-binary>=2.9.0
sqlalchemy>=2.0.0

# NLP / ML
numpy>=1.24.0
torch>=2.0.0
transformers>=4.30.0
sentence-transformers>=2.2.0

# Sentiment / Emotion
vaderSentiment>=3.3.0
text2emotion>=0.0.5

# Graph
networkx>=3.0

# Utilities
pydantic>=2.0.0
python-dotenv>=1.0.0
tenacity>=8.0.0
```

### C.2 Infrastructure

```
PostgreSQL >= 14
Qdrant >= 1.7
Redis >= 7
Letta Server (existing)
```

---

*Document Version: 1.0.0*  
*Last Updated: 2026-01-31*  
*Next Review: 2026-02-07*
