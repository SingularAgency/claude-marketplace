---
description: Guides a Singular Agency team member through creating a new Claude Code plugin and submitting it as a pull request to the SingularAgency/claude-marketplace on GitHub. Triggered by phrases like "create a plugin", "new plugin", "add a plugin to the marketplace", "contribute a plugin", "scaffold a plugin".
---

Guide the user through creating a new plugin for the Singular Agency marketplace and submitting it as a GitHub pull request. Follow each phase in order.

---

## Phase 0 — Welcome & Token

Show this message exactly:

---

👋 **Bienvenido al Plugin Creator de Singular Agency**

Con esta herramienta puedes agregar un nuevo plugin al marketplace del equipo en minutos. Al final del proceso se abrirá un Pull Request en GitHub automáticamente — solo necesitas que alguien con acceso lo apruebe.

Para enviar el PR necesitaré tu GitHub Personal Access Token. Si aún no lo tienes, aquí te explico cómo crearlo:

1. Ve a [github.com/settings/tokens](https://github.com/settings/tokens) e inicia sesión con tu cuenta de Singular Agency
2. Clic en **"Generate new token (classic)"**
3. Nombre: `singular-agency-marketplace` · Expiración: 90 días
4. Marca solo el scope: ✅ **repo**
5. Clic en **Generate token** — copia el token inmediatamente (empieza con `ghp_`)

**No lo necesitas todavía** — te lo pediré al final, justo antes de enviar el PR.

¿Listo para empezar? Cuéntame qué plugin quieres crear.

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

Write the SKILL.md for the main skill based on what the user described:
- Frontmatter `description` must be third-person and include specific trigger phrases
- The body is instructions FOR Claude — write as directives, not documentation
- Keep it focused and under 2,000 words
- Use imperative style ("Parse the input", not "You should parse the input")

Refer to `references/plugin-template.md` for a complete worked example.

### README.md

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

## Phase 3 — Ask for GitHub token

Tell the user:

> **Último paso antes de enviar el PR.**
>
> Necesito tu GitHub Personal Access Token (el que empieza con `ghp_`).
>
> Si aún no lo tienes:
> 1. Ve a **github.com → Settings → Developer settings → Personal access tokens → Tokens (classic)**
> 2. Genera uno con el scope ✅ **repo**
> 3. Cópialo y pégalo aquí
>
> El token solo se usará para crear la branch, subir los archivos y abrir el PR. No se guarda en ningún lado.

Wait for the token before proceeding.

---

## Phase 4 — Submit the PR

Use Python3 to interact with the GitHub API — it comes pre-installed on macOS, Linux and Windows and handles encoding reliably on all platforms. Run each step in order, substituting all `<placeholders>` with real values before executing.

### Step 1 — Get SHA of main + marketplace.json SHA

```python
python3 -c "
import urllib.request, json

TOKEN = '<TOKEN>'
OWNER = 'SingularAgency'
REPO  = 'claude-marketplace'

def get(path):
    req = urllib.request.Request(
        f'https://api.github.com{path}',
        headers={'Authorization': f'token {TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)

sha = get(f'/repos/{OWNER}/{REPO}/git/ref/heads/main')['object']['sha']
mkt_sha = get(f'/repos/{OWNER}/{REPO}/contents/.claude-plugin/marketplace.json?ref=main')['sha']
print('MAIN_SHA=' + sha)
print('MKT_SHA=' + mkt_sha)
"
```

Save both values — you'll need them in the next steps.

### Step 2 — Create branch

```python
python3 -c "
import urllib.request, json

TOKEN  = '<TOKEN>'
OWNER  = 'SingularAgency'
REPO   = 'claude-marketplace'
BRANCH = 'add-plugin-<plugin-name>'
SHA    = '<MAIN_SHA>'

data = json.dumps({'ref': f'refs/heads/{BRANCH}', 'sha': SHA}).encode()
req  = urllib.request.Request(
    f'https://api.github.com/repos/{OWNER}/{REPO}/git/refs',
    data=data, method='POST',
    headers={'Authorization': f'token {TOKEN}', 'Content-Type': 'application/json', 'Accept': 'application/vnd.github.v3+json'}
)
with urllib.request.urlopen(req) as r:
    print('Branch created:', json.load(r)['ref'])
"
```

### Step 3 — Push plugin files

Run this script once for each file. Update `REPO_PATH` and `LOCAL_PATH` for each one.

```python
python3 -c "
import urllib.request, json, base64

TOKEN      = '<TOKEN>'
OWNER      = 'SingularAgency'
REPO       = 'claude-marketplace'
BRANCH     = 'add-plugin-<plugin-name>'
REPO_PATH  = 'plugins/<plugin-name>/.claude-plugin/plugin.json'
LOCAL_PATH = '/tmp/<plugin-name>/.claude-plugin/plugin.json'

with open(LOCAL_PATH, 'rb') as f:
    content = base64.b64encode(f.read()).decode()

data = json.dumps({'message': f'add {REPO_PATH}', 'content': content, 'branch': BRANCH}).encode()
req  = urllib.request.Request(
    f'https://api.github.com/repos/{OWNER}/{REPO}/contents/{REPO_PATH}',
    data=data, method='PUT',
    headers={'Authorization': f'token {TOKEN}', 'Content-Type': 'application/json', 'Accept': 'application/vnd.github.v3+json'}
)
with urllib.request.urlopen(req) as r:
    print('Pushed:', json.load(r)['content']['path'])
"
```

Files to push (in order):
1. `plugins/<plugin-name>/.claude-plugin/plugin.json` ← `/tmp/<plugin-name>/.claude-plugin/plugin.json`
2. `plugins/<plugin-name>/skills/<skill-name>/SKILL.md` ← `/tmp/<plugin-name>/skills/<skill-name>/SKILL.md`
3. `plugins/<plugin-name>/README.md` ← `/tmp/<plugin-name>/README.md`

### Step 4 — Update marketplace.json

```python
python3 -c "
import urllib.request, json, base64

TOKEN   = '<TOKEN>'
OWNER   = 'SingularAgency'
REPO    = 'claude-marketplace'
BRANCH  = 'add-plugin-<plugin-name>'
MKT_SHA = '<MKT_SHA>'

def req(method, path, data=None):
    r = urllib.request.Request(
        f'https://api.github.com{path}', data=data, method=method,
        headers={'Authorization': f'token {TOKEN}', 'Content-Type': 'application/json', 'Accept': 'application/vnd.github.v3+json'}
    )
    with urllib.request.urlopen(r) as resp:
        return json.load(resp)

raw = req('GET', f'/repos/{OWNER}/{REPO}/contents/.claude-plugin/marketplace.json?ref={BRANCH}')
mkt = json.loads(base64.b64decode(raw['content']))

mkt['plugins'].append({
    'name':        '<plugin-name>',
    'source':      './plugins/<plugin-name>',
    'description': '<description>',
    'version':     '0.1.0',
    'author':      {'name': 'Singular Agency', 'email': 'as@singularagency.co'},
    'license':     'MIT',
    'category':    'productivity'
})

updated = base64.b64encode(json.dumps(mkt, indent=2).encode()).decode()
result  = req('PUT', f'/repos/{OWNER}/{REPO}/contents/.claude-plugin/marketplace.json',
    json.dumps({'message': 'add <plugin-name> to marketplace', 'content': updated, 'sha': MKT_SHA, 'branch': BRANCH}).encode()
)
print('Updated:', result['commit']['sha'])
"
```

### Step 5 — Open the Pull Request

```python
python3 -c "
import urllib.request, json

TOKEN  = '<TOKEN>'
OWNER  = 'SingularAgency'
REPO   = 'claude-marketplace'
BRANCH = 'add-plugin-<plugin-name>'

data = json.dumps({
    'title': 'Add plugin: <plugin-name>',
    'body':  '## New plugin: <plugin-name>\n\n<description>\n\n### Skills\n- \`/<skill-name>\` — <what it does>\n\n---\n*Submitted via plugin-creator*',
    'head':  BRANCH,
    'base':  'main'
}).encode()

req = urllib.request.Request(
    f'https://api.github.com/repos/{OWNER}/{REPO}/pulls',
    data=data, method='POST',
    headers={'Authorization': f'token {TOKEN}', 'Content-Type': 'application/json', 'Accept': 'application/vnd.github.v3+json'}
)
with urllib.request.urlopen(req) as r:
    print('PR:', json.load(r)['html_url'])
"
```

---

## Phase 5 — Confirm and wrap up

After the PR is created, tell the user:
- The PR URL
- That a reviewer at Singular Agency will approve and merge it
- Once merged, the plugin will be available via `/plugin install <plugin-name>@singular-agency-marketplace`

Do not expose the token, raw API responses, or internal file paths to the user.
