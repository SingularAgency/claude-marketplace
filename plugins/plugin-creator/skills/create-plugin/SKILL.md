---
description: Guides a Singular Agency team member through creating a new Claude Code plugin and submitting it as a pull request to the SingularAgency/claude-marketplace on GitHub. Triggered by phrases like "create a plugin", "new plugin", "add a plugin to the marketplace", "contribute a plugin", "scaffold a plugin".
---

Guide the user through creating a new plugin for the Singular Agency marketplace and submitting it as a GitHub pull request. Follow each phase in order.

---

## Phase 0 — Welcome & GitHub MCP Check

Before showing anything to the user, silently check whether the GitHub MCP connector is available by looking for tools prefixed with `mcp__github__` in your tool list (e.g. `mcp__github__create_branch`, `mcp__github__create_pull_request`, `mcp__github__push_files`).

**If GitHub MCP tools ARE available**, show this message:

---

👋 **Bienvenido al Plugin Creator de Singular Agency**

Con esta herramienta puedes agregar un nuevo plugin al marketplace del equipo en minutos. Al final del proceso se abrirá un Pull Request en GitHub automáticamente — solo necesitas que alguien con acceso lo apruebe.

✅ **Conector de GitHub detectado.** No necesitas configurar nada — al final del proceso el PR se enviará automáticamente.

¿Listo para empezar? Cuéntame qué plugin quieres crear.

---

**Si GitHub MCP tools NO están disponibles**, muestra este mensaje y guía al usuario paso a paso:

---

👋 **Bienvenido al Plugin Creator de Singular Agency**

Con esta herramienta puedes agregar un nuevo plugin al marketplace del equipo en minutos. Para enviar el PR automáticamente al final, primero necesitas instalar el conector de GitHub. Te guío en 4 pasos rápidos:

**Paso 1 — Crea un GitHub Personal Access Token:**
1. Ve a [github.com/settings/tokens](https://github.com/settings/tokens) (usa tu cuenta de Singular Agency)
2. Clic en **"Generate new token (classic)"**
3. Nombre: `singular-agency-marketplace` · Expiración: 90 días
4. Marca solo el scope: ✅ **repo**
5. Clic en **Generate token** — copia el token inmediatamente (empieza con `ghp_`)

**Paso 2 — Abre el archivo de configuración de Claude:**
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**Paso 3 — Agrega este bloque al archivo** (reemplaza `TU_TOKEN_AQUI` con el token del paso 1):

```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "TU_TOKEN_AQUI"
      }
    }
  }
}
```

> ⚠️ Si ya tienes otros `mcpServers` configurados, solo agrega el bloque `"github": { ... }` dentro del objeto existente — no reemplaces todo el archivo.

**Paso 4 — Reinicia Claude Desktop** para que active el conector.

---

Usa `AskUserQuestion` para preguntarle al usuario si ya completó la instalación y reinició Claude. Una vez que confirme, verifica de nuevo si los tools `mcp__github__*` están disponibles:
- Si ya aparecen → confirma con "✅ ¡Conector de GitHub activo! Continuemos." y sigue con Phase 1.
- Si aún no aparecen → indícale que asegure haber reiniciado completamente Claude Desktop y lo intente de nuevo.

---

## Phase 1 — Discovery

Ask the user these questions using AskUserQuestion (group them if possible):

1. What should this plugin do? What problem does it solve for the team?
2. What should it be called? (will become the plugin name in kebab-case)
3. What kind of capabilities does it need? (skills / agents / MCP integrations)

Confirm your understanding before proceeding. State the plugin name in kebab-case (e.g. "daily-standup-helper") and what it will do.

---

## Phase 2 — Build the plugin files

Create the plugin directory at `/tmp/<plugin-name>/` with this structure:

```
<plugin-name>/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── <main-skill-name>/
│       └── SKILL.md
└── README.md
```

### plugin.json

```json
{
  "name": "<plugin-name>",
  "version": "0.1.0",
  "description": "<one-line description>",
  "author": {
    "name": "Singular Agency",
    "email": "as@singularagency.co"
  },
  "repository": "https://github.com/SingularAgency/claude-marketplace",
  "license": "MIT"
}
```

### SKILL.md

Write the SKILL.md for the main skill based on what the user described. Follow these rules:
- Frontmatter `description` must be third-person and include specific trigger phrases
- The body is instructions FOR Claude — write as directives, not documentation
- Keep it focused and under 2,000 words
- Use imperative style ("Parse the input", not "You should parse the input")

Refer to `references/plugin-template.md` for a complete worked example.

### README.md

Write a brief README explaining what the plugin does and how to install it:

```markdown
# <Plugin Name>

<One-paragraph description>

## Install

/plugin install <plugin-name>@singular-agency-marketplace

## Skills

| Skill | Trigger phrases | What it does |
|-------|----------------|--------------|
| /<skill-name> | "..." | ... |
```

---

## Phase 3 — Submit the PR via GitHub MCP

Use the GitHub MCP tools to submit the plugin. These tools are available as `mcp__github__*`. Execute these steps in order.

### Step 1 — Verify connection

Call `mcp__github__get_me` to confirm authentication is working. If it returns an error, let the user know and refer back to Phase 0 setup instructions.

### Step 2 — Read marketplace.json from main

Call `mcp__github__get_file_contents` with:
- `owner`: `SingularAgency`
- `repo`: `claude-marketplace`
- `path`: `.claude-plugin/marketplace.json`
- `ref`: `main`

Save both the decoded content (the JSON) and the file's `sha` — you'll need both in Step 5.

### Step 3 — Create a new branch

Branch name: `add-plugin-<plugin-name>`

Call `mcp__github__create_branch` with:
- `owner`: `SingularAgency`
- `repo`: `claude-marketplace`
- `branch`: `add-plugin-<plugin-name>`
- `from_branch`: `main`

### Step 4 — Push all plugin files

Call `mcp__github__push_files` with:
- `owner`: `SingularAgency`
- `repo`: `claude-marketplace`
- `branch`: `add-plugin-<plugin-name>`
- `message`: `add plugin: <plugin-name>`
- `files`: an array with the content of each file read from `/tmp/<plugin-name>/`

Files to include:
1. `plugins/<plugin-name>/.claude-plugin/plugin.json`
2. `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`
3. `plugins/<plugin-name>/README.md`

If `mcp__github__push_files` is not available, use `mcp__github__create_or_update_file` for each file individually.

### Step 5 — Update marketplace.json

Take the marketplace.json content from Step 2 and add the new plugin entry to the `plugins` array:

```json
{
  "name": "<plugin-name>",
  "source": "./plugins/<plugin-name>",
  "description": "<description>",
  "version": "0.1.0",
  "author": {
    "name": "Singular Agency",
    "email": "as@singularagency.co"
  },
  "license": "MIT",
  "category": "productivity"
}
```

Then call `mcp__github__create_or_update_file` with:
- `owner`: `SingularAgency`
- `repo`: `claude-marketplace`
- `path`: `.claude-plugin/marketplace.json`
- `branch`: `add-plugin-<plugin-name>`
- `message`: `add <plugin-name> to marketplace`
- `content`: the updated JSON as a string
- `sha`: the SHA obtained in Step 2 (required to update an existing file)

### Step 6 — Open the Pull Request

Call `mcp__github__create_pull_request` with:
- `owner`: `SingularAgency`
- `repo`: `claude-marketplace`
- `title`: `Add plugin: <plugin-name>`
- `body`:
  ```
  ## New plugin: <plugin-name>

  <description>

  ### Skills
  - `/<skill-name>` — <what it does>

  ---
  *Submitted via plugin-creator*
  ```
- `head`: `add-plugin-<plugin-name>`
- `base`: `main`

---

## Phase 4 — Confirm and wrap up

After the PR is created successfully, tell the user:
- The PR URL (from the tool response `html_url` field)
- That a reviewer at Singular Agency will approve and merge it
- Once merged, the plugin will be available to the whole team via `/plugin install <plugin-name>@singular-agency-marketplace`

Do not expose raw API responses or internal file paths to the user.
