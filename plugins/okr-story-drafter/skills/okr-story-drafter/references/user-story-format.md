# User Story Format Reference

## Standard Structure

Each user story follows this structure:

```
### US-XX — [Short Descriptive Title]

**Como** [tipo de usuario / rol],
**quiero** [acción o funcionalidad],
**para que** [beneficio / valor generado].

**Criterios de aceptación:**
- [Condición verificable 1]
- [Condición verificable 2]
- [Condición verificable 3]
- ...

**Responsables:**
- **[Nombre]** — [rol específico en esta historia] (Backend / Frontend / Design / QA)
- **[Nombre]** — [rol específico]

**KR principal:** KR[N] — [descripción corta del KR]
**KR secundario:** KR[N] — [descripción corta] *(opcional)*
```

## Roles mapping

Use these standard roles when assigning responsibles:

| Role keyword | When to use |
|---|---|
| Backend | Database, API, business logic, server-side |
| Frontend | UI implementation, integration of design + backend |
| Design | UI/UX, wireframes, visual components |
| QA | Testing, regression, quality assurance |
| PM | Product decisions, sprint planning, client alignment |

## Acceptance criteria guidelines

- Write in the third person or as a system behavior ("El sistema permite...", "El usuario puede...")
- Be specific — avoid vague terms like "it works" or "it's fast"
- Include both happy path and edge cases when discussed in the meeting
- Reference specific flows or screens mentioned in the transcript

## Epic groupings

Organize stories into Epics based on feature domains. Common epics for product teams:

- **Chat & Messaging** — real-time communication features
- **Safety & Trust** — moderation, reporting, validations
- **Discovery & Onboarding** — first-time user experience, walkthroughs
- **Service History** — tracking, records, lesson history
- **Payments & Subscriptions** — billing, freemium, refunds
- **Quality Assurance** — testing, regression, monitoring

## KR mapping guide

When mapping a story to a Key Result:

1. Identify which metric the story most directly moves (satisfaction, conversion, automation)
2. If a story improves trust or UX → likely maps to satisfaction KR
3. If a story reduces friction in signup/discovery → likely maps to conversion KR
4. If a story removes manual steps from validation → likely maps to automation KR
5. A story can have 1 primary KR and 1 secondary KR at most

## Summary table format

At the end of the document, include this table:

| Responsable | User Stories | Rol principal |
|---|---|---|
| [Name] | US-01, US-03, US-05 | Backend |
| [Name] | US-01, US-02, US-04 | Design |
| [Name] | US-01, US-02, US-03, US-04, US-05 | Frontend |
| [Name] | US-06 | QA |

## Pending tasks section

Include a final section for sprint-level pending tasks extracted from action_items:

```markdown
## Pendientes del Sprint Actual

- [ ] **[Nombre]** — [tarea pendiente identificada en la reunión]
- [ ] **[Nombre]** — [tarea pendiente]

**Próximas reuniones:**
- Cliente: [fecha/día]
- Interna: [fecha/día]
```
