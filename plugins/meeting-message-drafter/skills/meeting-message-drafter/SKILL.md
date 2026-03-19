---
name: meeting-message-drafter
description: |
  Redacta mensajes (para clientes, equipo o cualquier destinatario) basándose en el transcript de una reunión específica almacenado en Airtable.

  Usa esta skill siempre que el usuario mencione una reunión y quiera redactar algún tipo de mensaje, comunicación o acción a partir de lo que se habló. Ejemplos de frases que deben activar esta skill:

  - "En la reunión de [cliente] de hoy quedé de enviarle un mensaje a..."
  - "Redacta un follow-up para el cliente de la reunión de [nombre] de ayer"
  - "A partir de la reunión de [cliente], escribe un mensaje para el equipo"
  - "Necesito mandarle algo al cliente sobre lo que hablamos en [reunión]"
  - "Basándote en la reunión de hoy con [nombre], redacta un correo que diga..."
  - "Qué acciones quedaron pendientes de la reunión de [cliente]?"
  - "Redacta un resumen de la reunión de [nombre] para compartir"

  También activa si el usuario pide cualquier comunicación que implique revisar lo que pasó en una reunión pasada o del día.
---

# Meeting Message Drafter

Esta skill te permite redactar mensajes, follow-ups, resúmenes y cualquier comunicación basada en el transcript real de una reunión almacenada en Airtable.

## Contexto del sistema

Los datos de reuniones están en Airtable:
- **Base ID**: `app4CGMhPVzJzxaCx` (base "Miguel / Claudia Meetings")
- **Tabla de Reuniones** ID: `tblUamUKowirQeoE0`
- **Tabla de Clientes** ID: `tblc0yzS0yyOv9L0i`

### Campos clave de la tabla Meetings:
| Campo | ID | Descripción |
|---|---|---|
| Title | `fldAaYsRnoiu1aJtQ` | Nombre de la reunión |
| meeting_transcript | `fldsdc1GfJ8oRiLQz` | Transcript completo |
| Date | `fldXI111nYz9mIxsL` | Fecha (YYYY-MM-DD) |
| Client (lookup) | `fldZF9fPKAgxIxvKL` | Nombre del cliente |
| Participants | `fldArVA7qgt8GDKv4` | Participantes |
| Action Items | `fldx1ghwoiaOpXmXo` | Ítems de acción vinculados |

### Campos clave de la tabla Clients:
| Campo | ID | Descripción |
|---|---|---|
| Client Name | `fldlXZVGlrhuZ7Tn3` | Nombre del cliente |
| client_stakeholder | `fldP42ryrKYSA06J1` | Nombre del stakeholder principal |
| Stakeholder Email | `fldbFWK5bkxidgQjh` | Email del stakeholder |
| agile_slack_id | `fldGAL5xNnRMK6HQf` | Slack ID del canal del cliente |
| internal_slack_id | `fld1eFcHSTTfIykbr` | Slack ID del canal interno |

---

## Flujo de trabajo

### Paso 1: Interpretar la solicitud del usuario

Extrae de lo que dice el usuario:
1. **Identificador de la reunión**: nombre del cliente o parte del título (ej. "Bloomer Health", "Velvet", "Ediphi")
2. **Fecha de la reunión**: "hoy", "ayer", una fecha específica, o deja implícita la fecha más reciente
3. **Qué mensaje redactar**: lo que el usuario quiere comunicar (follow-up al cliente, resumen para el equipo, email, mensaje de Slack, etc.)

Si alguno de estos datos no está claro, pregunta antes de buscar. Preferiblemente en una sola pregunta concisa.

### Paso 2: Buscar la reunión en Airtable

Busca en la tabla **Meetings** usando filtros:
- Filtra por `Title` que **contenga** el identificador de la reunión mencionado por el usuario
- Filtra por `Date` igual a la fecha indicada (usa formato `YYYY-MM-DD`)

**Para "hoy"**: usa la fecha actual del sistema.
**Para "ayer"**: usa la fecha de ayer.
**Para fechas relativas como "la semana pasada"**: usa el rango apropiado.

Si hay más de un resultado, muéstrale al usuario los títulos encontrados y pregunta cuál es la reunión correcta antes de continuar.

Si no se encuentra ninguna reunión, comunícalo claramente e intenta con una búsqueda más amplia (solo por nombre, sin fecha).

### Paso 2b: Si el mensaje es para el cliente externo, buscar el stakeholder en la tabla Clients

Cuando el usuario pide un mensaje **para el cliente** (no para alguien del equipo interno), siempre debes consultar la tabla **Clients** (`tblc0yzS0yyOv9L0i`) para obtener los datos del contacto externo:
- Busca el registro cuyo `Client Name` coincida con el nombre del cliente de la reunión
- Extrae el campo `client_stakeholder` (nombre del contacto externo) y `Stakeholder Email` si aplica

**Importante:** Los nombres que aparecen en el transcript de una reunión interna suelen ser miembros del equipo de Singular, NO el cliente externo. El stakeholder del cliente es la persona del lado del cliente, cuyo nombre está en la tabla Clients — no en el transcript. No confundas a los participantes internos de la reunión con el destinatario externo del mensaje.

### Paso 3: Leer el transcript

Una vez identificado el registro correcto, lee el campo `meeting_transcript`. Este campo contiene la conversación completa de la reunión.

Complementa con:
- `Participants` para saber quién estuvo en la reunión
- El nombre del cliente desde `Client Name (from Assignee)` si aplica

### Paso 4: Redactar el mensaje

Con el transcript en mano, redacta exactamente lo que el usuario pidió. Guíate por estos principios:

**Si es un mensaje para el cliente:**
- Tono profesional pero cálido
- Menciona los acuerdos o próximos pasos concretos que surgieron de la reunión
- No reveles conversaciones internas del equipo que no deban ir al cliente
- Si el usuario no especificó el tono, usa el mismo tono de la conversación con el cliente en el transcript

**Si es un mensaje para el equipo interno:**
- Tono directo, orientado a acción
- Resalta tareas, responsables y fechas si las hay
- Puede ser más informal

**Si el usuario especificó algo concreto** (ej. "dile que el bug del QR está resuelto" o "avísale que la próxima reunión es el martes"):
- Redacta exactamente eso, usando el contexto del transcript para darle profundidad y veracidad al mensaje
- No inventes datos que no estén en el transcript o en la solicitud del usuario

**Formato del mensaje:**
- Presenta el mensaje en un bloque claramente delimitado, listo para copiar y pegar
- Si aplica, incluye una línea de asunto sugerida (para emails) o menciona el canal/destinatario (para Slack)
- Al final del mensaje, ofrece ajustarlo si el usuario quiere cambiar el tono, agregar información o acortarlo

### Paso 5: Ofrecer variantes o ajustes

Después de presentar el mensaje, ofrece brevemente:
- Cambiar el tono (más formal, más casual)
- Agregar o quitar información
- Adaptar para otro canal (email vs. Slack)

---

## Ejemplo de interacción

**Usuario:** "En la reunión de Velvet de hoy quedé de mandarle un mensaje a Maxi diciéndole que lo del QR ya se resolvió y que empecemos a coordinar mejor el QA antes de mandar builds."

**Flujo:**
1. Identificador: "Velvet" | Fecha: hoy | Mensaje: confirmación del fix de QR + propuesta de coordinación de QA
2. Buscar reunión con título que contenga "Velvet" y fecha = hoy
3. Leer transcript → ver que se habló del bug de QR Code y la propuesta de que Octavio revise builds antes que el cliente
4. Redactar mensaje para Maxi con ese contexto

---

## Manejo de errores comunes

- **No se encuentra la reunión**: Informa al usuario, sugiere buscar sin fecha o con otro término
- **Transcript vacío**: Avisa que la reunión existe pero no tiene transcript aún
- **Múltiples reuniones del mismo día con nombre similar**: Muestra opciones y pide al usuario que elija
- **Información sensible en el transcript**: Sé discreto y no incluyas en mensajes al cliente conversaciones internas que no correspondan
