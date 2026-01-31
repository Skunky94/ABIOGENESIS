---
name: changelog
description: Document changes in CHANGELOG.md following project rules
---

# Changelog Documentation Skill

## Purpose
Maintain accurate, complete changelog documentation for all ABIOGENESIS changes.

## Usage
Invoke when completing any code, documentation, or configuration change:
```
/changelog
```

## Format Template

```markdown
### [TYPE-XXX] - Descriptive Title

**Descrizione**: Detailed description of what changed

**Files Modificati/Creati**:
- file1.py
- file2.md

**Documentazione Associata**:
- [Name](path) - description

**Compatibilità**: [Breaking | Non-Breaking]

**Tags**: #tag1 #tag2
```

## Type Codes

| Code | Meaning |
|------|---------|
| FEATURE | New functionality |
| BUGFIX | Bug correction |
| REFACTOR | Code restructuring |
| ARCHITECTURE | Architectural change |
| DOCS | Documentation change |
| INFRA | Infrastructure change |
| SECURITY | Security-related |

## Examples

### Adding new feature
```markdown
### FEATURE-015 - Goal Management System

**Descrizione**: Implemented autonomous goal generation and tracking system for Scarlet.

**Files Creati**:
- `scarlet/src/goals/goal_manager.py`
- `scarlet/src/goals/models.py`

**Documentazione Associata**:
- [adr-003-goals.md](docs/architecture/adr-003-goals.md) - Architecture decision

**Compatibilità**: Non-Breaking

**Tags**: #goals #autonomy #modulo3
```

### Docker config change
```markdown
### INFRA-007 - Ollama Embedding Container Added

**Descrizione**: Added Ollama container for local embedding model support.

**Files Modificati**:
- `scarlet/docker-compose.yml`
- `scarlet/.env`

**Documentazione Associata**:
- [ollama-setup.md](docs/guides/ollama-setup.md) - Setup guide

**Compatibilità**: Non-Breaking

**Tags**: #infrastructure #embeddings #ollama
```

## Before Writing

1. Identify all files modified
2. Determine change type (FEATURE/BUGFIX/etc)
3. Assign sequential number (XXX)
4. List relevant tags

## After Writing

Verify:
- [ ] Format matches template
- [ ] All files listed
- [ ] Links are valid
- [ ] Tags are appropriate
