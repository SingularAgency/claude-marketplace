# Calendar Automatcher

Encuentra y agenda automáticamente un sync táctico de 30 minutos entre PM, PO y Talento en las próximas 48 horas — sin revisar tres agendas manualmente.

## ¿Qué hace?

1. Consulta la disponibilidad de los tres participantes via Google Calendar.
2. Encuentra el primer hueco libre de 30 minutos dentro del horario laboral (08:00–17:00, hora Guatemala).
3. Propone el horario encontrado y espera tu confirmación.
4. Crea el evento y envía las invitaciones automáticamente.

## Skills incluidas

### `setup` — Configuración inicial
Guarda los emails de PM, PO y Talento una sola vez. Después, el automatcher los usará siempre sin pedirlos de nuevo.

**Cómo activarlo:** Di "setup" o "configurar automatcher".

### `autobook` — Buscar y agendar
Busca disponibilidad y propone un horario para tu confirmación.

**Cómo activarlo:** Di "agendar sync", "busca disponibilidad" o "agéndanos".

## Requisitos

- Google Calendar conectado en Cowork.
- Acceso de lectura al calendario de los otros dos participantes (al menos free/busy).

## Configuración

- **Timezone**: America/Guatemala (UTC-6)
- **Horario laboral**: 08:00–17:00
- **Buffer de cortesía**: 2 horas desde el momento de ejecución
- **Ventana de búsqueda**: 48 horas
- **Duración del bloque**: 30 minutos

La configuración se guarda en `~/.calendar-automatcher-config.json` y puede actualizarse ejecutando `setup` de nuevo.
