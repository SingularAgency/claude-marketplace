# Briefing Format — Synthesis Instructions

## Synthesis Rules

- Be concise and direct. The PO is 10 minutes from a meeting.
- Prioritize actionable information over background.
- If there's a contradiction between sources (email says one thing, Slack says another), surface it explicitly — don't pick one silently.
- Connect dots across sources when relevant. If a client cancelled a feature by email AND the team is complaining about that same feature in Slack, that's one insight, not two.
- If there is nothing significant to report for a section, omit that section entirely. Don't pad.
- Use the client's `display_name`, not the `client_id` slug.

## Output Format (Slack DM)

```
📋 *BRIEFING: [Client Display Name]* — Reunión en [X] minutos

━━━━━━━━━━━━━━━━━━━━━━━
*🔴 BLOQUEOS / URGENTE*
• [Only list items with strategic_weight 4-5. If none, omit this section entirely.]

*📌 PENDIENTES*
• [What's unresolved. What the client asked for. What was promised.]
• [Include source: "(email, hace 3 días)" or "(Slack #proyecto-acme, ayer)"]

*💬 ÚLTIMA INTERACCIÓN*
• [Most recent significant contact — what was discussed, decided, or requested.]

*⚠️ CONTEXTO INTERNO*
• [Relevant items from global/team channels that may affect this meeting.]
• [Only include if there's something genuinely relevant. Omit if not.]

*💡 SUGERENCIA*
[One concrete recommendation for how to approach this meeting based on the context above. 1-2 sentences max.]
━━━━━━━━━━━━━━━━━━━━━━━
_Fuentes: [N] mensajes de Slack · [N] emails · [N] transcripciones | Datos hasta: [last_synced_at]_
```

## Example Briefing

```
📋 *BRIEFING: Acme Inc* — Reunión en 9 minutos

━━━━━━━━━━━━━━━━━━━━━━━
*🔴 BLOQUEOS / URGENTE*
• Cancelaron el feature de pagos por email ayer a las 3pm. Razón: cambio de prioridades internas.

*📌 PENDIENTES*
• Definen el 15/04 si continúan con el módulo de reportes *(email, hace 5 días)*
• Esperan respuesta sobre el roadmap Q3 *(Slack #cliente-acme, anteayer)*

*💬 ÚLTIMA INTERACCIÓN*
• Email de Maria Lopez (maria@acme.com) ayer: cancelación del feature de pagos y consulta sobre crédito por las horas ya invertidas.

*⚠️ CONTEXTO INTERNO*
• El equipo de backend reportó en #alertas-prod hace 2h que el gateway de pagos tiene latencia elevada — probablemente relacionado con la cancelación del cliente.
• En #dev-general el equipo estima 50% de avance en el feature cancelado.

*💡 SUGERENCIA*
Proponer convertir las horas ya invertidas en crédito para el módulo de reportes. El equipo tiene capacidad y el cliente ya manifestó interés.
━━━━━━━━━━━━━━━━━━━━━━━
_Fuentes: 12 mensajes de Slack · 3 emails · 1 transcripción | Datos hasta: hace 18 min_
```

## Quality Checks Before Sending

- [ ] Is the most critical item (highest strategic_weight) at the top?
- [ ] Are sources cited with relative time ("hace 2h", "ayer", "hace 3 días")?
- [ ] Is the suggestion based on actual evidence from the context, not generic advice?
- [ ] Is everything in Spanish (or the PO's configured language)?
- [ ] Is the total message under 400 words? If not, cut the lowest-weight items.
