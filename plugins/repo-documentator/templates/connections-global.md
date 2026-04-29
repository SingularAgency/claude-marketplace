---
last-reviewed: {{DATE}}
status: draft
auto-detected: true
---

# System connection map

Global view of how all modules connect. For each module's local view, see `modules/<name>/connections.md`.

## Global diagram

```mermaid
graph LR
    {{GLOBAL_GRAPH}}
```

> Line conventions: solid = sync (HTTP/RPC), dotted = async (events/queues), thick = critical/blocking.

## Dependency matrix

| From \ To | {{MOD_A}} | {{MOD_B}} | {{MOD_C}} | External |
|---|---|---|---|---|
| **{{MOD_A}}** | — | HTTP | event | Stripe |
| **{{MOD_B}}** | — | — | — | — |
| **{{MOD_C}}** | DB | — | — | SendGrid |

> Empty cells = no direct connection. Mark with the connection type.

## External systems

| System | Type | Modules using it | Criticality | Plan B if it goes down |
|---|---|---|---|---|
| {{SYSTEM}} | {{type}} | {{modules}} | {{level}} | {{plan}} |

## Domain events (bus / queue)

If the system has event-based communication:

| Event | Publishes | Subscribers | Guarantees |
|---|---|---|---|
| {{NAME}} | {{MODULE}} | {{MODULES}} | {{at-least-once / exactly-once / best-effort}} |

## Dangerous shared data

Subtle couplings NOT visible in the code that create dependency between modules:

- {{COUPLING}} — Risk: {{WHY_IT_HURTS}}

## Critical paths

Module sequences where a single failure breaks the business:

1. **{{PATH_NAME}}**: {{MODULE_A}} → {{MODULE_B}} → {{MODULE_C}}
   - Associated workflow: `workflows/{{NAME}}.md`
   - If it goes down: {{IMPACT}}
