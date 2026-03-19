# Guía de configuración de Read.ai MCP

Present these steps to the user one by one.

---

## Instrucciones para el usuario (mostrar tal cual)

### Paso 1: Obtener la URL del servidor MCP de Read.ai

> 1. Entrá a **[app.read.ai](https://app.read.ai)** con tu cuenta
> 2. Hacé clic en tu avatar (arriba a la derecha) → **"Settings"**
> 3. En el menú de la izquierda buscá **"Integrations"** o **"API & MCP"**
> 4. Buscá la sección **"MCP Server"**
> 5. Ahí vas a ver una URL que empieza con `https://` y un token o instrucciones de OAuth
> 6. Copiá esa URL completa

✅ Checkpoint: "¿Tenés la URL del MCP de Read.ai?"

---

### Paso 2: Agregar Read.ai como conector personalizado en Claude

> 1. En Claude, abrí el panel de configuración (ícono de engranaje ⚙️ o "Settings")
> 2. Buscá la sección **"MCP Servers"** o **"Conectores personalizados"**
> 3. Hacé clic en **"Add custom MCP server"** o similar
> 4. Completá los campos:
>    - **Name**: `Read.ai`
>    - **URL**: la URL que copiaste de Read.ai
>    - **Type**: HTTP
> 5. Si te pide autenticación, Read.ai usa OAuth — hacé clic en **"Authorize"** y seguí los pasos en el navegador
> 6. Guardá y verificá que aparezca como conectado ✅

✅ Checkpoint: "¿Read.ai aparece como conectado en tu lista de conectores?"

---

### Si no encontrás la sección MCP en Read.ai

> Si tu plan de Read.ai no incluye acceso al MCP server (es una feature de planes pagos),
> podemos usar **Fireflies** como alternativa. Fireflies hace exactamente lo mismo
> (transcripciones de reuniones) y tiene un conector oficial en Claude.
> ¿Querés que usemos Fireflies en su lugar?

If user confirms Fireflies as alternative, use `suggest_connectors` with UUID: `839a0ae2-0c0f-4c27-9f85-726ed6515536`
