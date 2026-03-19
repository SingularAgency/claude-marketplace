# Briefing Format — Synthesis Instructions

## Filosofía del briefing

El PO entra a una reunión con un cliente. No necesita una lista de tareas — necesita saber **qué importa estratégicamente** y cómo llevar la conversación. El briefing debe leerlo en 60 segundos y salir con claridad sobre qué defender, qué negociar y qué resolver.

Priorizar siempre: impacto sobre exhaustividad. Si algo no es accionable o estratégico, no va.

---

## Synthesis Rules

- Enfocarse en **qué decir**, no en qué pasó. Transformar hechos en puntos de conversación.
- Si hay información de OKRs o metas del cliente en los datos, conectarlos explícitamente con lo que se va a discutir.
- Si hay contradicción entre fuentes (email dice una cosa, Slack otra), surfacearla como punto de negociación.
- Cruzar fuentes activamente: si el equipo interno discutió algo que el cliente también mencionó, eso es el punto más importante del briefing.
- Omitir secciones completas si no hay datos relevantes. No rellenar.
- Tono: directo, de colega a colega. No corporativo.

---

## Output Format (Slack DM)

```
📋 *BRIEFING: [Client Display Name]* — Reunión en [X] minutos

━━━━━━━━━━━━━━━━━━━━━━━
*📊 OKRs ACTIVOS* [omitir sección completa si no hay datos de Airtable]
*[Nombre del Objetivo]* — [Quarter] · [Status] · [Avg%]% completado
  • [Key Result 1] — [Current]% / [Target]% _(Status)_
  • [Key Result 2] — [Current]% / [Target]% _(Status)_

*🎯 PUNTOS ESTRATÉGICOS A TRATAR*
[2-4 temas concretos para llevar a la reunión, formulados como puntos de conversación.
Cuando aplique, conectar explícitamente con el OKR relevante.]

• *[Tema 1]:* [descripción + por qué importa hoy] → _conecta con OKR: [nombre]_ _(fuente, hace X días)_
• *[Tema 2]:* [descripción + ángulo estratégico] _(fuente, hace X días)_

*🔴 RIESGOS / PUNTOS SENSIBLES*
[Solo si hay algo que puede generar fricción, cancelación, o afectar la relación. Omitir si no hay.]

• [Riesgo concreto] [si aplica: → _pone en riesgo OKR: [nombre]_]

*⚡ CONTEXTO INTERNO RELEVANTE*
[Algo del equipo que el PO debe saber antes de entrar. Solo si afecta lo que se va a discutir.]

• [Insight interno] _(#canal, hace X horas)_

*💡 ÁNGULO RECOMENDADO*
[Una sola recomendación basada en evidencia concreta. Si hay OKRs, anclarla en ellos. 2-3 oraciones.]
━━━━━━━━━━━━━━━━━━━━━━━
_Fuentes: [N] mensajes de Slack · [N] emails · [N] transcripciones · [N] OKRs de Airtable | Datos hasta: [timestamp]_
_Enviado usando @Claude_
```

---

## Cómo construir los Puntos Estratégicos

No transcribir lo que pasó. Transformarlo en punto de conversación:

| En lugar de... | Escribir... |
|---|---|
| "Claudia preguntó por el timeline del admin panel" | "Admin panel invoices: el cliente está esperando un timeline — definir uno hoy o acordar fecha de respuesta" |
| "Frederick compartió el doc de migración" | "Documento de migración LifeFile/Hallandale listo para revisión — buena oportunidad para presentarlo y alinearse antes del go-live" |
| "Hubo problemas con el gateway de pagos" | "Gateway de pagos degradado esta semana — si el cliente lo trae, el equipo ya tiene el análisis" |

---

## Uso de OKRs de Airtable

Los OKRs vienen directamente de Airtable — son datos reales, no inferencias. Usarlos así:

**En la sección OKRs:** mostrar el estado actual de cada Objective con sus Key Results y porcentaje de progreso. Un KR con Current < 50% del Target y Status no completado = en riesgo.

**En los Puntos Estratégicos:** cuando un tema de conversación conecta con un OKR, decirlo explícitamente: `→ conecta con OKR: [nombre del objetivo]`. Esto le da al PO munición para enmarcar la conversación en términos de impacto, no de tareas.

**En Riesgos:** si hay una cancelación, bloqueo o problema que amenaza directamente el logro de un Key Result, mencionarlo: `→ pone en riesgo OKR: [nombre]`.

**En el Ángulo Recomendado:** anclar la recomendación en los OKRs cuando sea posible. Ejemplo: *"Con el KR de automatización al 30%, esta reunión es el momento para alinear prioridades de Q2 antes de que el gap se haga más grande."*

Si Airtable no tiene OKRs para este cliente, omitir la sección completa y no mencionarla.

---

## Quality Checks Before Sending

- [ ] ¿Cada punto estratégico tiene un "¿y para qué?" implícito? (no es solo un hecho, es un punto de acción)
- [ ] ¿Las fuentes tienen timestamp relativo ("ayer", "hace 2h") no fechas absolutas?
- [ ] ¿El Ángulo Recomendado está basado en evidencia concreta de los datos?
- [ ] ¿El mensaje total es menor a 350 palabras?
- [ ] ¿Está todo en español?
