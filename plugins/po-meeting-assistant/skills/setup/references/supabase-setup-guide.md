# Guía de configuración de Supabase

There are two scenarios. Detect which one applies by asking the user.

---

## Preguntarle al usuario

> "Para la memoria del asistente usamos Supabase. ¿Tu empresa ya tiene un proyecto de Supabase configurado, o necesitás crear uno nuevo?"

- If they say **"ya existe"** or **"el admin me dio las credenciales"** → go to **Escenario A**
- If they say **"no sé"** or **"necesito crear uno"** → go to **Escenario B**
- If they're unsure: **"Preguntale a quien administra los sistemas de tu empresa si existe un proyecto de Supabase para el asistente de reuniones. Si te pasan un link de Supabase o unas credenciales, usamos esas."**

---

## Escenario A — Credenciales centralizadas (lo más común)

Present this to the user:

> "Perfecto. Tu administrador debería haberte enviado dos datos:
> 1. Una **URL del proyecto** (algo como `https://abcdefgh.supabase.co`)
> 2. Una **clave de acceso** (una cadena larga de letras y números)
>
> ¿Los tenés a mano?"

Once they confirm they have the credentials, use `suggest_connectors` with Supabase UUID: `11ca66fc-1e98-49d5-ab9b-7cb4672a8f10`

> "Hacé clic en el botón de Supabase aquí abajo e ingresá esos dos datos cuando te los pida."

Wait for user to confirm connection is successful, then return to the main setup flow (Phase 2 — Initialize Database).

---

## Escenario B — Crear proyecto nuevo (primera instalación en la empresa)

Present these steps one by one. Wait for confirmation at each ✅ checkpoint.

### Paso 1: Crear cuenta

> 1. Entrá a **[supabase.com](https://supabase.com)** y hacé clic en **"Start your project"**
> 2. Registrate con tu cuenta de GitHub o email.
> 3. Una vez adentro, hacé clic en **"New project"**
> 4. Elegí un nombre (por ejemplo: `po-assistant`) y una contraseña fuerte. **Guardá esa contraseña.**
> 5. Región recomendada para América Latina: **South America (São Paulo)**
> 6. Hacé clic en **"Create new project"** y esperá 1-2 minutos.

✅ **"¿Ves el dashboard del proyecto con menús a la izquierda?"**

### Paso 2: Habilitar la extensión vector

> 1. En el menú izquierdo: **"Database"** → **"Extensions"**
> 2. Buscá **"vector"** y activá el toggle.

✅ **"¿El toggle de `vector` quedó activado (verde)?"**

### Paso 3: Obtener las credenciales

> 1. En el menú izquierdo: ícono ⚙️ **"Settings"** → **"API"**
> 2. Copiá estos dos datos:
>    - **Project URL**: `https://xxxxxxxx.supabase.co`
>    - **anon / public key**: cadena larga que empieza con `eyJ...`

✅ **"¿Tenés los dos valores copiados?"**

### Paso 4: Conectar con Claude

Use `suggest_connectors` with Supabase UUID: `11ca66fc-1e98-49d5-ab9b-7cb4672a8f10`

> "Hacé clic en el botón de Supabase aquí abajo e ingresá la URL y la clave que copiaste."

✅ Wait for user to confirm connection worked.

---

## Nota para el administrador (mostrar solo en Escenario B)

> "**Para el admin:** Si van a usar este asistente con varios POs, recomendamos un único proyecto de Supabase compartido. Cuando quieran agregar un nuevo PO, solo tienen que pasarle la misma URL y clave de acceso. Cada PO queda aislado automáticamente."
