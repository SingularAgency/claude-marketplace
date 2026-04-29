---
adr: {{NUMBER}}
title: {{TITLE}}
date: {{DATE}}
status: {{proposed | accepted | superseded | deprecated}}
deciders: [{{NAMES}}]
supersedes: {{ADR_NUMBER_OR_NONE}}
---

# ADR-{{NUMBER}}: {{TITLE}}

## Context

{{SITUATION_THAT_LED_TO_THE_DECISION}}

> What was happening in the business or in the system that required a decision. Constraints, pressures, opportunities.

## Options considered

### Option A: {{NAME}}
- **Pros:** {{LIST}}
- **Cons:** {{LIST}}

### Option B: {{NAME}}
- **Pros:** {{LIST}}
- **Cons:** {{LIST}}

## Decision

{{WHAT_WAS_CHOSEN}}

## Main reason

{{WHY_THIS_AND_NOT_THE_OTHERS}}

> This is the most important line of the document. If in 6 months someone wants to change this decision, this is what they should re-evaluate.

## Consequences

### Positive
- {{LIST}}

### Negative / costs accepted
- {{LIST}}

### Things we'll need to watch
- {{LIST}}

## When to revisit this decision

{{TRIGGER}}

> E.g.: "If LATAM customer share exceeds 40%, revisit Stripe vs MercadoPago."
