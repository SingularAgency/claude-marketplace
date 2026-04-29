---
last-reviewed: {{DATE}}
status: draft
owner: {{OWNER}}
---

# Glossary — Ubiquitous Language

Domain terms. One definition per term — if the same term means different things in different modules, that's a **bounded-context smell** and should be resolved (rename one of the two).

## Format

```
### {{TERM}}
**Definition:** {{SHORT_DEFINITION}}
**Used in:** {{MODULES}}
**Not to be confused with:** {{SIMILAR_TERM}}
**Example:** {{CONCRETE_EXAMPLE}}
**Synonyms in code:** {{TECHNICAL_NAMES_THAT_REPRESENT_THE_SAME}}
```

---

## Terms

### {{TERM}}
**Definition:** {{DEFINITION}}
**Used in:** {{MODULES}}
**Not to be confused with:** {{SIMILAR_TERM}}
**Example:** {{EXAMPLE}}
**Synonyms in code:** {{NAMES}}

> Repeat per term. Sort alphabetically.

---

## Detected ambiguous terms

List of terms that have multiple meanings depending on context. These require resolution (rename or explicitly document the ambiguity).

- **{{TERM}}** — In `{{MODULE_A}}` it means X; in `{{MODULE_B}}` it means Y. Resolution pending.
