---
name: adr
description: Create and update Architecture Decision Records for ABIOGENESIS
---

# ADR (Architecture Decision Record) Skill

## Purpose
Maintain architectural documentation using the ADR format for significant decisions.

## When to Create an ADR

Create an ADR when decisions involve:
- Framework or tool selection (e.g., Letta adoption)
- Database or storage choices
- Integration patterns
- Major refactoring
- Technology stack changes

Small fixes and incremental improvements don't need ADRs.

## ADR Template

See `docs/architecture/adr-template.md` for the full template, but use this structure:

```markdown
# ADR-XXX: Descriptive Title

**Status**: [Proposed | Accepted | Deprecated | Rejected]
**Date**: YYYY-MM-DD
**Author**: Claude Code

## Context
[Why do we need to make this decision?]

## Decision
[What have we decided to do?]

## Consequences
### Positive
- [Benefits]

### Negative
- [Drawbacks]

### Neutral
- [Trade-offs]

## Alternatives Considered
- [Option]: Why rejected

## References
- [Links]
```

## Usage

### Create new ADR
```bash
# Check next number
ls docs/architecture/adr-*.md | sort

# Copy template
cp docs/architecture/adr-template.md docs/architecture/adr-XXX-title.md
```

### Update Status
When implementing or deprecating:
1. Open the ADR
2. Change **Status** header
3. Add **Last Updated** date

## ADR Index

| Number | Title | Status |
|--------|-------|--------|
| ADR-001 | Letta Framework Adoption | Accepted |
| ADR-002 | Scarlet Setup (Foundation + Embeddings) | Accepted |

## Checklist
- [ ] Filename: `adr-XXX-title.md`
- [ ] Status valid
- [ ] All sections filled
- [ ] CHANGELOG.md updated
