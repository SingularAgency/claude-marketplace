---
name: morning-greeter
description: >
  Sends a motivational morning greeting via Slack DM to Will. Trigger this skill
  when the scheduled task fires, or when the user says "send morning greeting",
  "saludo de la mañana", "buenos días slack", "morning greeting", "send my
  daily motivation", or "manda el saludo".
metadata:
  version: "0.1.0"
---

# Morning Greeter

Send a motivational morning greeting as a Slack direct message to Will (user ID: U075E2QBTUH).

## Greeting Generation Rules

Generate a short, energizing morning message in Spanish. The message must:

1. Start with a warm greeting (vary daily — e.g., "Buenos días, Will!", "Arriba, Will!", "Nuevo día, nueva oportunidad, Will!")
2. Include a motivational line — draw from themes like growth, discipline, building something meaningful, leveling up, consistency, or strategic thinking
3. Keep it to 2-3 sentences max — punchy, not preachy
4. End with an energizing closer (e.g., "A darle con todo.", "Hoy se construye.", "Dale que hoy es tuyo.")
5. Never repeat the same message — vary structure, vocabulary, and theme each time
6. Tone: warm, direct, like a sharp colleague who believes in you — not generic motivational poster language

## Examples of Good Greetings

- "Buenos días, Will! Cada sistema que diseñas hoy es una pieza más del arquitecto que estás construyendo. A darle con todo."
- "Arriba, Will! La consistencia es lo que separa al builder del que solo planea. Hoy se construye."
- "Nuevo día, Will! Recuerda: cada decisión técnica bien tomada es capital que se acumula. Dale que hoy es tuyo."

## Execution Steps

1. Generate a unique motivational greeting following the rules above.
2. Send the greeting as a Slack DM to user U075E2QBTUH using the `slack_send_message` tool with `channel` set to `U075E2QBTUH`.
3. Confirm the message was sent successfully. If it fails, retry once.
