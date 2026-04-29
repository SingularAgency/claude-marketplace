---
workflow: {{WORKFLOW_NAME}}
type: end-to-end
modules-involved: [{{MODULES}}]
external-systems: [{{EXTERNAL_SYSTEMS}}]
last-reviewed: {{DATE}}
status: draft
auto-detected: true
owner: "{{OWNER}}"
---

# Workflow: {{WORKFLOW_NAME_HUMAN}}

## Business objective

{{WHAT_THIS_ACHIEVES}}

> What this workflow achieves from the business point of view. Pull from PRD / product docs.

## Trigger

{{HOW_IT_STARTS}}

> What kicks this workflow off — a human action, a system event, a schedule.

## Actors involved

{{ACTORS_LIST}}

> Both human actors and systems, with a one-line description of each one's role in the flow.

## Business view (non-technical)

> The big picture, in plain language. For the technical step-by-step with endpoints and data, see the **Technical sequence** below.

```mermaid
flowchart LR
    {{BUSINESS_FLOWCHART}}

    classDef person fill:#cce5ff,stroke:#0066cc,color:#003366
    classDef warn fill:#fff3cd,stroke:#ff9900,color:#664d03
    classDef good fill:#d4edda,stroke:#28a745,color:#155724
    classDef neutral fill:#e9ecef,stroke:#6c757d,color:#212529
```

**What this is, in one paragraph:** {{ONE_PARAGRAPH_BUSINESS}}

**Who's involved:** {{WHO_LINE}}

**Why it matters:** {{WHY_LINE}}

> The flowchart MUST use only business-language nodes and labels. NO endpoints (`POST /api/...`), NO database tables, NO internal services. Use em-dashes inside `|...|` edge labels — never parentheses (Mermaid breaks).

## Technical sequence (for engineers)

```mermaid
sequenceDiagram
    autonumber
    {{SEQUENCE_DIAGRAM}}
```

> Include human actors AND systems as participants. Cite endpoints, DB writes, events, queues. This is where the technical detail lives.

## Variants

{{VARIANTS_OR_OMIT}}

> If the workflow has branches that materially change the flow (e.g. agent-driven vs manual), document each variant. Otherwise, omit this section.

## Happy path (step by step)

{{HAPPY_PATH_BUSINESS_PROSE}}

> Numbered steps in **plain English**, no `[API → DB]` notation, no path:line refs, no internal endpoint mentions. Describe what the user / system does, not how the code does it.

## Edge cases

{{EDGE_CASES_BUSINESS_FRAMING}}

> Each edge case has: "What it looks like to the user", "Why it happens" (high-level), and "Resolution" (in business terms). NO code smells, NO function names.

## Business rules applied

{{BUSINESS_RULES_CROSS_REF}}

> Reference rules documented in each module's `business-rules` section. Format: ``modules/<x>.md` — <rule restated in plain language>``.

## Key data flowing

| Stage | What's flowing | From | To |
|---|---|---|---|
| {{STAGE}} | {{DATA}} | {{FROM}} | {{TO}} |

> Plain-English description of what information passes between actors. Not a schema dump.

## SLAs / time expectations

{{SLAS_OR_TBD}}

> Real production timing if measurable; otherwise honest TBD ("to be measured once in regular use").

## Metrics / KPIs

{{METRICS_OR_TBD}}

## What has historically failed here

{{INCIDENT_HISTORY_OR_TBD}}

> Useful for new members. "When you hear X, check Y first." If empty, say so honestly.
