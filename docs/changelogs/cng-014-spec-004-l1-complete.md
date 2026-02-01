# CNG-014: SPEC-004 L1 Continuous Existence Completa

**ID**: DOCS-010  
**Data**: 2026-02-01  
**Tipo**: DOCS  
**Versione**: 0.4.7 → 0.4.8  
**Breaking**: No

---

## Descrizione

Completata e riorganizzata SPEC-004 per Layer 1 (Continuous Existence) dopo discussione
approfondita su tutti i punti aperti. La SPEC è ora pronta per diventare ADR-006.

### Decisioni Chiave Documentate

| Decisione | Scelta |
|-----------|--------|
| **Architettura** | Servizio dedicato `autonomy-runtime` (container separato) |
| **Configurazione** | File YAML unico `scarlet/config/runtime.yaml` |
| **Storage hot** | Redis (Working Set, Budget tracker, Runtime state) |
| **Storage cold** | Qdrant (Learning Events, Error Journal) |
| **Budget MiniMax** | 5000 req/5h rolling window, throttle non distruttivo |
| **Runaway detection** | Score multi-fattore con pesi configurabili |
| **Learning** | Learning Event → futuro Learning Agent (L3.2) |

### Contenuto SPEC-004 v2.0

1. **Executive Summary** - Obiettivo e decisioni chiave
2. **Architettura** - Diagramma e interazione loop/webhook/Letta
3. **Configurazione Centralizzata** - Schema YAML completo
4. **Loop Contract** - Invarianti, Environment Snapshot, Working Set
5. **State Machine** - Stati, transizioni, override esterni
6. **Budget e Quota** - MiniMax tracking con Redis
7. **Runaway Detection** - Tipi, progress markers, score, Learning Event
8. **Storage** - Strategia Redis/Qdrant/PostgreSQL
9. **Main Loop** - Pseudocodice completo
10. **Rischi e Mitigazioni**
11. **Metriche Day-1**
12. **Conclusioni e Next Steps**

### Principi Fondamentali Stabiliti

- Il loop è **infinito by design** (continuità esistenziale)
- Il runtime fornisce trigger, **Scarlet decide** cosa farne
- **Runaway ≠ errore**: è continuità senza progresso, da mitigare
- Learning Event come **ponte verso auto-apprendimento** futuro
- Webhook continua a funzionare (trigger interni contano come messaggi)

## Files Modificati

- `docs/specifications/spec-004-continuous-existence.md` - Riscritto completamente (v2.0)
- `docs/ROADMAP.md` - Aggiornato status L1 a "IN PROGRESS 50%"
- `CONTEXT.md` - Aggiornato a v0.4.8, aggiunta sezione L1 decisions

## Correlazioni

- **SPEC-004**: spec-004-continuous-existence.md (Ready for ADR)
- **ROADMAP**: L1.1, L1.2, L1.3 aggiornati con decisioni
- **Futuro**: ADR-006 (prossimo step)

---

**Tags**: #docs #spec #L1 #architecture #autonomy-runtime #runaway #learning-events
