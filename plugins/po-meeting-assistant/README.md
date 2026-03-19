# PO Meeting Assistant

Asistente autónomo que prepara al Product Owner para sus reuniones. Consulta Slack, Gmail y Read.ai en tiempo real — sin almacenar mensajes — y envía un briefing estratégico por Slack antes de cada reunión con un cliente.

---

## ¿Cómo funciona?

1. Una tarea automática revisa tu Google Calendar cada 5 minutos
2. Cuando detecta una reunión con un cliente en los próximos minutos, consulta en tiempo real:
   - Los últimos **N días** de emails del cliente (Gmail)
   - Los mensajes recientes en los canales de Slack configurados
   - Las transcripciones de reuniones anteriores (Read.ai)
3. Sintetiza todo y te envía un resumen estratégico por Slack

> **Sin base de datos de mensajes.** No guardamos emails, chats ni transcripciones. Solo tu configuración (clientes, canales, preferencias). Cada briefing consulta los datos frescos en el momento.

---

## Requisitos antes de instalar

| Qué necesitás | Dónde conseguirlo |
|---|---|
| Acceso a tu workspace de Slack | Tu cuenta habitual de Slack |
| Cuenta de Google con Calendar | La misma que usás para tus reuniones |
| Credenciales de Supabase | Tu administrador de sistemas te las envía (o creás una cuenta gratis en supabase.com) |
| Cuenta de Read.ai con acceso MCP | app.read.ai → Settings → MCP (requiere plan pago) |

---

## Instalación

Una vez instalado el plugin, decile a Claude:

> **"configurar el asistente"**

Claude te guía por todo el proceso conversacionalmente. No necesitás hacer nada técnico.

El wizard cubre:
1. Conectar Slack, Google Calendar, Supabase y Read.ai
2. Crear tu perfil (nombre, lead time, ventana de tiempo, usuario de Slack)
3. Configurar tu primer cliente
4. Programar la tarea automática de briefing

---

## Skills disponibles

### `setup` — Configuración inicial
Wizard guiado. Usar solo la primera vez.

**Activar:** `"configurar el asistente"` · `"primera vez"`

---

### `generate-briefing` — Briefing on-demand
Genera un briefing de cualquier cliente cuando querés, sin esperar la reunión.

**Activar:**
- `"dame el brief de Acme"`
- `"prepárame para la reunión de las 3pm"`
- `"¿qué hay pendiente con Bancolombia?"`

---

### `configure` — Gestión de configuración
Agrega, edita o elimina clientes, canales y preferencias.

**Activar:**
- `"agregar cliente [nombre]"`
- `"agregar el canal #dev-general como canal global"`
- `"cambiar los canales de Acme"`
- `"quiero 7 días de historial"` · `"quiero 30 días de historial"`
- `"cambiar el briefing a 15 minutos antes"`
- `"¿qué clientes tengo configurados?"`

---

## Tarea automática

| Tarea | Frecuencia | Qué hace |
|---|---|---|
| Briefing check | Cada 5 minutos | Revisa el calendario; si hay reunión próxima, consulta todas las fuentes y envía el DM |

La tarea es muy liviana el 95% del tiempo (solo revisa el calendario y termina). Solo consume recursos cuando hay una reunión a punto de empezar.

---

## Ventana de tiempo

Durante el setup, elegís cuántos días de historial consultar. Esta preferencia controla:
- Cuántos días de emails busca en Gmail
- Cuántos días de mensajes lee en cada canal de Slack
- Cuántas transcripciones de Read.ai considera

**Referencia de costos aproximados por briefing:**

| Ventana | Costo aprox. por briefing |
|---|---|
| 7 días | Muy bajo |
| 14 días (recomendado) | Bajo |
| 30 días | Moderado |

Podés cambiarlo en cualquier momento diciéndole a Claude `"quiero [N] días de historial"`.

---

## Conectores

| Conector | Para qué | Tipo |
|---|---|---|
| **Gmail** | Emails de clientes | Oficial |
| **Slack** | Canales + envío de DMs | Oficial |
| **Google Calendar** | Detectar reuniones | Oficial |
| **Supabase** | Guardar configuración | Oficial |
| **Read.ai** | Transcripciones de reuniones | Personalizado |

**Alternativa a Read.ai:** Si usás Fireflies, Granola o Krisp, también son compatibles. Pedíselo a Claude durante el setup.

---

## Variables de entorno

| Variable | Descripción |
|---|---|
| `READAI_MCP_URL` | URL del servidor MCP de Read.ai (Settings → MCP en app.read.ai) |

Las demás credenciales se configuran a través de los conectores oficiales de Claude.

---

## Soporte

Desarrollado por **Singular Agency** — as@singularagency.co
