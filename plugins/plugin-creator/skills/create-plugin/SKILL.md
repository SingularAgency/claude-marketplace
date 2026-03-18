---
description: Guides a Singular Agency team member through creating a new Claude Code plugin and submitting it as a pull request to the SingularAgency/claude-marketplace on GitHub. Triggered by phrases like "create a plugin", "new plugin", "add a plugin to the marketplace", "contribute a plugin", "scaffold a plugin".
---

Guide the user through creating a new plugin for the Singular Agency marketplace and submitting it as a GitHub pull request. Follow each phase in order.

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

## Phase 3 — Ask for GitHub token

Tell the user:

> "To submit this as a PR, I need a GitHub Personal Access Token with `repo` scope. You can create one at github.com → Settings → Developer settings → Personal access tokens → Tokens (classic). Paste it here and I'll handle the rest."

Wait for the token before proceeding.

---

## Phase 4 — Submit the PR via GitHub API

Use Bash to submit the plugin to the marketplace. Execute these steps in order:

### Step 1 — Get the current SHA of main

```bash
curl -s \
  -H "Authorization: token <TOKEN>" \
  https://api.github.com/repos/SingularAgency/claude-marketplace/git/ref/heads/main \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['object']['sha'])"
```

### Step 2 — Create a new branch

Branch name: `add-plugin-<plugin-name>`

```bash
curl -s -X POST \
  -H "Authorization: token <TOKEN>" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/SingularAgency/claude-marketplace/git/refs \
  -d '{"ref":"refs/heads/add-plugin-<plugin-name>","sha":"<SHA_FROM_STEP_1>"}'
```

### Step 3 — Push each file

For each file in the plugin, push it via the contents API. Base64-encode the content:

```bash
CONTENT=$(base64 -w 0 /tmp/<plugin-name>/<file-path>)
curl -s -X PUT \
  -H "Authorization: token <TOKEN>" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/SingularAgency/claude-marketplace/contents/plugins/<plugin-name>/<file-path> \
  -d "{\"message\":\"add <plugin-name>: <file-path>\",\"content\":\"$CONTENT\",\"branch\":\"add-plugin-<plugin-name>\"}"
```

Files to push (in order):
1. `.claude-plugin/plugin.json`
2. `skills/<skill-name>/SKILL.md`
3. `README.md`

### Step 4 — Update marketplace.json to include the new plugin

First, fetch the current marketplace.json:

```bash
curl -s \
  -H "Authorization: token <TOKEN>" \
  https://api.github.com/repos/SingularAgency/claude-marketplace/contents/.claude-plugin/marketplace.json?ref=add-plugin-<plugin-name>
```

This returns the file content (base64) and its SHA. Decode it, add the new plugin entry to the `plugins` array:

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

Then push the updated marketplace.json using the file's SHA for the update:

```bash
UPDATED_CONTENT=$(echo '<updated_json>' | base64 -w 0)
curl -s -X PUT \
  -H "Authorization: token <TOKEN>" \
  https://api.github.com/repos/SingularAgency/claude-marketplace/contents/.claude-plugin/marketplace.json \
  -d "{\"message\":\"add <plugin-name> to marketplace\",\"content\":\"$UPDATED_CONTENT\",\"sha\":\"<FILE_SHA>\",\"branch\":\"add-plugin-<plugin-name>\"}"
```

### Step 5 — Open the Pull Request

```bash
curl -s -X POST \
  -H "Authorization: token <TOKEN>" \
  https://api.github.com/repos/SingularAgency/claude-marketplace/pulls \
  -d '{
    "title": "Add plugin: <plugin-name>",
    "body": "## New plugin: <plugin-name>\n\n<description>\n\n### Skills\n- `/<skill-name>` — <what it does>\n\n---\n*Submitted via plugin-creator*",
    "head": "add-plugin-<plugin-name>",
    "base": "main"
  }'
```

---

## Phase 5 — Confirm and wrap up

After the PR is created, tell the user:
- The PR URL (from the API response `html_url` field)
- That a reviewer at Singular Agency will approve and merge it
- Once merged, the plugin will be available to the whole team via `/plugin install <plugin-name>@singular-agency-marketplace`

Do not expose raw API responses or internal paths to the user.
