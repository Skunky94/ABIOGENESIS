# SPEC-XXX: [Titolo Specifica]

**Status**: [Draft | Review | Accepted | Superseded]  
**Version**: 1.0.0  
**Date**: YYYY-MM-DD  
**Author**: [Nome]  
**Focus**: [Area di focus]

> **Nota**: Questo documento è un'analisi tecnica/progettuale per brainstorming e ricerca.
> Una volta validata, questa SPEC può portare alla creazione di un ADR.

---

## 1. Executive Summary

### 1.1 Obiettivo dell'Analisi

[Descrizione breve di cosa si sta analizzando e perché questa ricerca è necessaria.]

### 1.2 Domande di Ricerca

1. [Domanda principale che questa SPEC vuole rispondere]
2. [Domanda secondaria]
3. [Domanda secondaria]

### 1.3 Scope

**Incluso**:
- [Area inclusa nell'analisi]
- [Area inclusa nell'analisi]

**Escluso**:
- [Area NON coperta da questa SPEC]
- [Area NON coperta da questa SPEC]

---

## 2. Background e Contesto

### 2.1 Situazione Attuale

[Descrizione dello stato attuale. Cosa abbiamo? Cosa funziona? Cosa no?]

### 2.2 Problemi Identificati

| Problema | Impatto | Urgenza |
|----------|---------|---------|
| [Problema 1] | [Alto/Medio/Basso] | [Alta/Media/Bassa] |
| [Problema 2] | [Alto/Medio/Basso] | [Alta/Media/Bassa] |

### 2.3 Documenti Correlati

- [ADR-XXX](../architecture/adr-xxx-name.md) - Decisione correlata
- [SPEC-XXX](spec-xxx-name.md) - Specifica correlata

---

## 3. Analisi Tecnica

### 3.1 Stato dell'Arte

[Ricerca su come questo problema viene risolto altrove. Paper, progetti open source, best practices del settore.]

### 3.2 Opzioni Considerate

#### Opzione A: [Nome]

**Descrizione**: [Spiegazione dell'approccio]

**Pro**:
- [Vantaggio 1]
- [Vantaggio 2]

**Contro**:
- [Svantaggio 1]
- [Svantaggio 2]

**Complessità**: [Alta/Media/Bassa]

#### Opzione B: [Nome]

**Descrizione**: [Spiegazione dell'approccio]

**Pro**:
- [Vantaggio 1]
- [Vantaggio 2]

**Contro**:
- [Svantaggio 1]
- [Svantaggio 2]

**Complessità**: [Alta/Media/Bassa]

### 3.3 Analisi Comparativa

| Criterio | Opzione A | Opzione B | Note |
|----------|-----------|-----------|------|
| Performance | ⭐⭐⭐ | ⭐⭐ | [Note] |
| Complessità | ⭐⭐ | ⭐⭐⭐ | [Note] |
| Manutenibilità | ⭐⭐⭐ | ⭐⭐ | [Note] |
| Costo | ⭐⭐⭐ | ⭐⭐ | [Note] |

---

## 4. Architettura Proposta

### 4.1 Diagramma Concettuale

```
┌─────────────────────────────────────────┐
│                                         │
│   [Diagramma architettura proposta]     │
│                                         │
└─────────────────────────────────────────┘
```

### 4.2 Componenti Principali

| Componente | Responsabilità | Tecnologia Proposta |
|------------|----------------|---------------------|
| [Nome] | [Descrizione] | [Tech] |
| [Nome] | [Descrizione] | [Tech] |

### 4.3 Flussi Dati

[Descrizione di come i dati fluiscono tra i componenti]

---

## 5. Strutture Dati

### 5.1 Schema Proposto

```python
# Esempio di schema proposto
class ExampleModel:
    """Descrizione del modello."""
    field_a: str
    field_b: int
    field_c: Optional[List[str]]
```

### 5.2 Storage

| Dato | Storage | Motivazione |
|------|---------|-------------|
| [Tipo dato] | [PostgreSQL/Qdrant/Redis] | [Perché] |

---

## 6. Algoritmi e Logiche

### 6.1 [Nome Algoritmo/Logica]

**Input**: [Descrizione]  
**Output**: [Descrizione]  
**Complessità**: O(n)

**Pseudocodice**:
```
1. [Step 1]
2. [Step 2]
3. [Step 3]
```

**Ragionamento**: [Perché questo approccio]

---

## 7. Rischi e Mitigazioni

| Rischio | Probabilità | Impatto | Mitigazione Proposta |
|---------|-------------|---------|---------------------|
| [Rischio 1] | [Alta/Media/Bassa] | [Alto/Medio/Basso] | [Come mitigare] |
| [Rischio 2] | [Alta/Media/Bassa] | [Alto/Medio/Basso] | [Come mitigare] |

---

## 8. Valutazione Strumenti Esterni

### 8.1 Strumenti Considerati

| Tool | Scopo | Valutazione | Raccomandazione |
|------|-------|-------------|-----------------|
| [Tool 1] | [Cosa fa] | [Pro/Contro] | ✅ Usa / ❌ Evita / 🔲 Valuta |
| [Tool 2] | [Cosa fa] | [Pro/Contro] | ✅ Usa / ❌ Evita / 🔲 Valuta |

---

## 9. Conclusioni e Raccomandazioni

### 9.1 Sintesi Analisi

[Riassunto dei punti chiave emersi dall'analisi]

### 9.2 Raccomandazione

**Opzione Raccomandata**: [Opzione X]

**Motivazione**: [Perché questa è la scelta migliore]

### 9.3 Prossimi Passi Suggeriti

Se questa SPEC viene accettata, si raccomanda di:
1. Creare ADR-XXX per formalizzare la decisione
2. [Altro passo]
3. [Altro passo]

---

## 10. Open Questions

Domande ancora da risolvere:

1. [Domanda aperta 1]
2. [Domanda aperta 2]

---

## History

| Data | Autore | Modifica |
|------|--------|----------|
| YYYY-MM-DD | [Nome] | Versione iniziale |

---

*SPEC-XXX v1.0.0 - ABIOGENESIS Project*  
*Documento di analisi e ricerca - Non contiene task operativi*
