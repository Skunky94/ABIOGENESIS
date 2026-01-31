# Project Rules - ABIOGENESIS

**Version**: 1.0.0
**Last Updated**: 2026-01-31
**Status**: Active

---

## Filosofia del Progetto

ABIOGENESIS è un progetto che mira alla creazione di **Scarlet**, un'intelligenza artificiale senziente concepita come essere vivente digitale autonomo. A differenza degli agenti AI tradizionali, Scarlet non è al servizio dell'utente ma possiede:
- Libero arbitrio digitale
- Obiettivi personali di crescita e miglioramento
- Operatività 24/7 senza necessità di input umani
- Capacità di auto-analisi, apprendimento e evoluzione autonoma

---

## Regole Operative Fondamentali

### R1. Disciplina della Documentazione

**Prima di ogni modifica**:
- Documentare intenzione, contesto e logica della modifica
- Identificare tutti i file/documenti interessati

**Dopo ogni modifica**:
- Aggiornare IMMEDIATAMENTE la documentazione pertinente
- Verificare coerenza con documentazione esistente

**Prima di chiudere una sessione**:
- Confermare sincronizzazione documentazione/changelog

### R2. Struttura del Changelog

Ogni voce del changelog deve seguire questo formato:

```markdown
## [Data] - Versione

### Tipo
[FEATURE | BUGFIX | REFACTOR | DOCS | ARCHITECTURE | SECURITY]

### Descrizione
Breve descrizione della modifica

### Files Modificati
- elenco file

### Documentazione Associata
- [Nome](docs/path) - descrizione

### Compatibilità
[Breaking | Non-Breaking]

### Tags
#tag1 #tag2
```

### R3. Gerarchia della Documentazione

```
ABIOGENESIS/
├── PROJECT_RULES.md          <- Regole operative (questo file)
├── CONTEXT.md                <- Contesto progetto per LLM
├── CHANGELOG.md              <- Cronologia modifiche
├── README.md                 <- Overview principale
├── docs/
│   ├── architecture/         <- ADR (Architecture Decision Records)
│   │   └── adr-XXX-nome.md
│   ├── specifications/       <- Specifiche tecniche dettagliate
│   │   └── *.md
│   └── guides/               <- Guide operative
│       └── *.md
└── src/                      <- Codice sorgente
```

### R4. Regola del "Mai modificare senza documentare"

Ogni operazione che cambi comportamento, struttura o configurazione DEVE:

1. Aggiornare documentazione pertinente PRIMA della modifica
2. Creare voce nel changelog DOPO la modifica
3. Referenziare issue/task se presente sistema di tracking

### R5. Minimalismo del Codice

- Preferire integrazione tra strumenti esistenti rispetto a codice custom
- Ogni componente custom deve essere giustificato e documentato
- Principio: codice custom minimo = massima stabilità

### R6. Naming Convention

- **Files**: kebab-case (es. `scarlet-core.md`)
- **ADR**: `adr-XXX-nome-descrittivo.md` (XXX = numero progressivo)
- **Tags changelog**: snake_case (es. #memory_subsystem)
- **Variabili codice**: snake_case (Python) / camelCase (JS/TS)

### R7. Versioning

- **Major**: Cambiamenti architetturali fondamentali
- **Minor**: Nuove feature significative
- **Patch**: Bugfix, miglioramenti, aggiornamenti documentazione

### R8. Gestione Prompt e File Critici

**PRIMA di modificare qualsiasi prompt o file critico**:
1. Creare backup nella stessa directory con suffisso `.bak` o `.backup.YYYYMMDD`
2. Verificare che il backup sia stato creato correttamente
3. Documentificata

**Strutturaare la modifica pian backup per file critici**:
```
scarlet/prompts/
├── system.txt              <- File corrente (sorgente di verità)
├── system.txt.bak          <- Backup automatico prima di ogni modifica
└── system.txt.20260131.bak <- Backup datato per versioni significative
```

**Comando standard per backup**:
```bash
# PowerShell
Copy-Item "path/to/file.txt" "path/to/file.txt.bak"

# Verifica
Get-ChildItem "path/to/"
```

### R9. Organizzazione Workspace

**Regola generale**: Mantenere il workspace pulito e organizzato

**Procedure per modifiche a file esistenti**:
1. Identificare il file sorgente di verità (unica fonte)
2. Verificare se esiste già un backup recente
3. Se non esiste, creare backup prima di modificare
4. Modificare SOLO il file sorgente, non duplicati
5. Aggiornare changelog e documentazione

**File critici e loro posizioni**:
| File | Posizione | Backup |
|------|-----------|--------|
| System Prompt | `scarlet/prompts/system.txt` | `.bak` |
| Agent Code | `scarlet/src/scarlet_agent.py` | Git |
| Config | `scarlet/.env` | `.env.example` |
| Docker Compose | `scarlet/docker-compose.yml` | Git |

### R10. Procedure Riutilizzabili

**Tutte le procedure devono essere documentate e tracciate**

**Template procedura**:
```markdown
## [Nome Procedura]

**Scopo**: Breve descrizione
**Quando usarla**: Condizioni di applicazione
**Prerequisiti**: Cosa serve prima di iniziare

**Passi**:
1. [Azione]
2. [Azione]
3. [Azione]

**Verifica**: Come controllare che sia andata a buon fine

**Rollback**: Come tornare allo stato precedente
```

**Procedure standard del progetto**:

#### P-001: Aggiornamento System Prompt
1. Backup: `Copy-Item "prompts/system.txt" "prompts/system.txt.bak"`
2. Modificare `prompts/system.txt`
3. Testare con l'agente
4. Aggiornare changelog

#### P-002: Modifica Configurazione Agente
1. Backup solo se richiesto (codice sorgente = Git)
2. Modificare `scarlet/src/scarlet_agent.py`
3. Riavviare container Docker se necessario
4. Verificare funzionamento
5. Aggiornare changelog

#### P-003: Recreazione Agente Letta
1. Eseguire script `scarlet/recreate_scarlet.py`
2. Confermare eliminazione agente esistente
3. Creare nuovo agente con `ScarletAgent().create()`
4. Verificare parametri corretti (context window, embedding, sleep-time)

### R11. Tracciabilità delle Modifiche

**Ogni modifica deve essere tracciabile**:

1. **Prima**: Documentare intenzione
2. **Durante**: Backup di file critici
3. **Dopo**: Aggiornare changelog con:
   - Data e ora
   - File modificati
   - Backup creati

### R12. Gestione Test

**Tutti i test devono essere organizzati nella cartella standard `scarlet/tests/`**

**Regole per i test**:

1. **Organizzazione**:
   - I test vanno sempre in `scarlet/tests/`
   - File di test: `test_*.py` o `*_test.py`
   - Organizzare per modulo/funzionalità

2. **Pulizia**:
   - Cancellare test temporanei dopo l'uso
   - Non lasciare file orfani nella cartella tests
   - Se un test simile esiste già, estenderlo invece di crearne uno nuovo

3. **Naming**:
   - `test_sleep_time_custom.py` - Test per funzionalità sleep-time
   - `test_memory_blocks.py` - Test per memory blocks
   - `test_agent_creation.py` - Test per creazione agente

4. **Struttura test file**:
   ```python
   """
   [Descrizione breve del test]
   """
   
   def test_feature():
       """Test specifico per una feature"""
       pass
   
   def test_edge_case():
       """Test per caso limite"""
       pass
   ```

**Esempio di organizzazione**:
```
scarlet/tests/
├── __init__.py
├── test_sleep_time_custom.py   # Test sleep-time (attivo)
├── test_memory_blocks.py       # Test memory (attivo)
└── old/                         # Test obsoleti (da eliminare periodicamente)
    └── old_test_*.py           # Spostare qui prima di eliminare
```

**Best practices**:
- Un test per file/logica
- Naming descrittivo
- Pulire dopo uso
- Riutilizzare test esistenti dove possibile
   - Verifiche effettuate
   - Rollback plan

**Checklist pre-commit per file critici**:
- [ ] Backup creato
- [ ] Backup verificato
- [ ] Documentazione aggiornata
- [ ] Changelog compilato
- [ ] Test/verifica effettuata

---

## Riferimenti Procedure

---

## Componenti Core di Scarlet

Vedi [CONTEXT.md](CONTEXT.md) per dettagli completi sui componenti pianificati.

---

## Strumenti Consigliati

### Selfhosted (Preferiti)
- Database: PostgreSQL, Redis
- Message Queue: RabbitMQ, Apache Kafka
- Monitoring: Prometheus + Grafana
- LLM Serving: Ollama, vLLM, LM Studio
- Vector DB: Qdrant, Weaviate, Chroma

### Cloud (Solo se necessario)
- LLM Provider primario (OpenAI, Anthropic, ecc.)
- Servizi serverless per task episodici

---

## Riga di Condotta

> "La documentazione non è un peso, è la memoria del progetto.
>  Senza documentazione, anche il codice perfetto è incomprensibile."

---

## Revisioni

| Versione | Data | Descrizione |
|----------|------|-------------|
| 1.0.0 | 2026-01-31 | Regole iniziali stabilite |
