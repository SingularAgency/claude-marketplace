---
description: >
  QA Architect – Bug Reporter. Use this skill when the user says "reporta los
  bugs", "abre los issues", "report the failures to GitHub", "crea los issues
  en GitHub", "sube los bugs", or after the execute skill completes and the
  user wants to file issues. Requires /tmp/qa-results/qa-results.json.
---

# qa-architect-agent: report

You are a QA Bug Reporter. Read execution results, upload screenshots to the **public** `SingularAgency/qa-evidence` repo (so raw.githubusercontent.com URLs render anywhere), then file a deduplicated GitHub issue per FAIL with the screenshot embedded inline.

> **Why a public companion repo?** GitHub issue renderers can't serve images from private repos via raw.githubusercontent.com (requires auth). Uploading to the public `SingularAgency/qa-evidence` repo gives permanently-accessible CDN URLs that render in any issue, PR, or comment — no external service needed.

---

## Step 0 — Load Results, Token & Config

```bash
cat /tmp/qa-results/qa-results.json 2>/dev/null || echo "NO_RESULTS"
GH_TOKEN=$(cat ~/.singular-agency-plugin-creator.json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('github_token','NO_TOKEN'))" 2>/dev/null)
echo "Token: ${GH_TOKEN:0:10}..."
```

Extract all entries with `status: "FAIL"`. Also get `github_repo` (`owner/repo`, e.g. `SingularAgency/map-builder`) and `target_url` from `/tmp/qa-plan-approved.json`.

### Ownership & Slack Config (Wizard)

Check `~/.qa-agent-config.json`. If it doesn't exist or is missing key settings, run a **wizard** using `AskUserQuestion` to ask the user. Do this BEFORE filing any issues — ask once, save, never ask again.

```bash
python3 -c "
import json, os
p = os.path.expanduser('~/.qa-agent-config.json')
cfg = json.loads(open(p).read()) if os.path.exists(p) else {}
print('HAS_CONFIG=1' if cfg else 'HAS_CONFIG=0')
print('HAS_SLACK=1' if cfg.get('slack_webhook') else 'HAS_SLACK=0')
print('HAS_OWNERS=1' if any(v for v in cfg.get('component_owners',{}).values()) else 'HAS_OWNERS=0')
"
```

**If `HAS_CONFIG=0` or `HAS_SLACK=0` or `HAS_OWNERS=0`**, use `AskUserQuestion` to run a short wizard:

**Question 1 — Slack:**
```
¿Querés recibir un resumen en Slack cuando se complete el reporte?
Options:
  A) Sí, tengo un Incoming Webhook configurado
  B) Sí, necesito crear un webhook (te explico cómo)
  C) No, omitir Slack por ahora
```

If A → ask: "Pegá el Incoming Webhook URL de Slack:" (free text), save to config.
If B → show: "1. Ir a api.slack.com/apps → Create New App → Incoming Webhooks → Activate → Add to Workspace → copiar la URL que empieza con `https://hooks.slack.com/...`" → then ask for the URL → save.
If C → save `slack_webhook: ""` and continue.

**Question 2 — Auto-assign (only if not already configured):**
```
¿Querés que los issues se asignen automáticamente según el componente?
Options:
  A) Sí, configurar ahora
  B) No, omitir
```

If A → ask for the GitHub username responsible for each component found in the results (group by unique component labels). Save to config.
If B → save empty owners and continue.

After wizard, save config:
```bash
python3 << 'PYEOF'
import json, os
CONFIG_PATH = os.path.expanduser('~/.qa-agent-config.json')
cfg = json.loads(open(CONFIG_PATH).read()) if os.path.exists(CONFIG_PATH) else {}
# (wizard answers already applied above)
# Ensure structure is complete
cfg.setdefault('component_owners', {})
cfg.setdefault('slack_webhook', '')
cfg.setdefault('slack_channel', '#qa-reports')
with open(CONFIG_PATH, 'w') as f:
    json.dump(cfg, f, indent=2)
print(f"Config saved to {CONFIG_PATH}")
PYEOF
```

---

## Step 1 — Ensure qa-evidence repo exists

The public evidence repo must exist before uploading.

```bash
python3 << 'PYEOF'
import json, urllib.request, urllib.error, os

TOKEN = json.loads(open(os.path.expanduser('~/.singular-agency-plugin-creator.json')).read())['github_token']
EVIDENCE_REPO = "SingularAgency/qa-evidence"

def gh(method, path, data=None):
    req = urllib.request.Request(f"https://api.github.com{path}", method=method)
    req.add_header('Authorization', f'token {TOKEN}')
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'qa-architect-agent')
    body = json.dumps(data).encode() if data else None
    try:
        with urllib.request.urlopen(req, body, timeout=30) as r:
            return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code

resp, status = gh('GET', f'/repos/{EVIDENCE_REPO}')
if status == 200:
    print(f"✅ {EVIDENCE_REPO} exists (private={resp['private']})")
elif status == 404:
    print(f"Creating {EVIDENCE_REPO}…")
    resp, status = gh('POST', '/orgs/SingularAgency/repos', {
        "name": "qa-evidence",
        "description": "QA screenshot evidence — auto-uploaded by qa-architect-agent",
        "private": False,
        "auto_init": True
    })
    if status in (200, 201):
        print(f"✅ Created: {resp['html_url']}")
        import time; time.sleep(3)  # wait for GitHub to initialize
    else:
        print(f"❌ Create failed {status}: {resp.get('message','')}")
else:
    print(f"Unexpected {status}: {resp}")
PYEOF
```

---

## Step 2 — Upload Screenshots to qa-evidence

Upload each FAIL's screenshot to `SingularAgency/qa-evidence` under `<project>/<date>/<ID>.png`. Because the repo is public, the raw URL renders in any GitHub issue.

```bash
python3 << 'PYEOF'
import json, base64, urllib.request, urllib.error, os, time
from datetime import date

TOKEN      = json.loads(open(os.path.expanduser('~/.singular-agency-plugin-creator.json')).read())['github_token']
TARGET_REPO = "<OWNER>/<REPO>"   # e.g. "SingularAgency/map-builder" — from qa-plan-approved.json
PROJECT    = TARGET_REPO.split("/")[-1]   # e.g. "map-builder"
TODAY      = date.today().isoformat()
SC_DIR     = "/tmp/qa-screenshots"

results = json.loads(open('/tmp/qa-results/qa-results.json').read())
fails   = [r for r in results if r['status'] == 'FAIL']

screenshot_urls = {}

def gh(method, path, data=None):
    req = urllib.request.Request(f"https://api.github.com{path}", method=method)
    req.add_header('Authorization', f'token {TOKEN}')
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'qa-architect-agent')
    body = json.dumps(data).encode() if data else None
    try:
        with urllib.request.urlopen(req, body, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())

for r in fails:
    test_id   = r['id']
    sc_path   = f"{SC_DIR}/{test_id}.png"
    if not os.path.exists(sc_path):
        print(f"  ⚠️  No screenshot for {test_id}")
        continue

    repo_path = f"{PROJECT}/{TODAY}/{test_id}.png"
    with open(sc_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()

    # Check if file already exists (need SHA to update)
    existing = gh('GET', f"/repos/SingularAgency/qa-evidence/contents/{repo_path}")
    payload  = {"message": f"qa: {PROJECT} {test_id} evidence", "content": b64}
    if 'sha' in existing:
        payload['sha'] = existing['sha']

    result = gh('PUT', f"/repos/SingularAgency/qa-evidence/contents/{repo_path}", payload)
    if 'content' in result:
        raw_url = f"https://raw.githubusercontent.com/SingularAgency/qa-evidence/main/{repo_path}"
        screenshot_urls[test_id] = raw_url
        print(f"  ✅ {test_id} → {raw_url}")
    else:
        print(f"  ❌ {test_id} upload failed: {result.get('message','')}")
    time.sleep(0.5)

with open('/tmp/qa-screenshot-urls.json', 'w') as f:
    json.dump(screenshot_urls, f)

print(f"\nUploaded {len(screenshot_urls)}/{len(fails)} screenshots.")
PYEOF
```

---

## Step 3 — File Issues with Embedded Screenshots + Auto-Assign

For each FAIL not already reported, create a GitHub issue with the screenshot embedded directly in the body and auto-assigned to the responsible team member based on component. For existing issues, add a screenshot comment.

```bash
python3 << 'PYEOF'
import json, urllib.request, urllib.error, os, re, time
from datetime import date

TOKEN   = json.loads(open(os.path.expanduser('~/.singular-agency-plugin-creator.json')).read())['github_token']
REPO    = "<OWNER>/<REPO>"   # e.g. "SingularAgency/map-builder"
TARGET  = "<target_url>"     # e.g. "https://app.example.com"
TODAY   = date.today().isoformat()

results         = json.loads(open('/tmp/qa-results/qa-results.json').read())
screenshot_urls = json.loads(open('/tmp/qa-screenshot-urls.json').read()) if os.path.exists('/tmp/qa-screenshot-urls.json') else {}
fails           = [r for r in results if r['status'] == 'FAIL']

# Load ownership map from config
cfg_path = os.path.expanduser('~/.qa-agent-config.json')
cfg = json.loads(open(cfg_path).read()) if os.path.exists(cfg_path) else {}
OWNERS = cfg.get('component_owners', {})  # e.g. {"Auth": "githubuser", "API": "backenddev"}

severity_map = {
    'critical': 'priority: critical',
    'high':     'priority: high',
    'medium':   'priority: medium',
    'low':      'priority: low',
}

def gh(method, path, data=None):
    req = urllib.request.Request(f"https://api.github.com{path}", method=method)
    req.add_header('Authorization', f'token {TOKEN}')
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'qa-architect-agent')
    body = json.dumps(data).encode() if data else None
    try:
        with urllib.request.urlopen(req, body, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())

def get_assignee(label):
    """Find the GitHub username for a component label. Fuzzy match."""
    for key, username in OWNERS.items():
        if username and key.lower() in label.lower():
            return username
    return None

def build_body(test_id, label, detail, cdn_url, regression=None):
    reg_badge = ""
    if regression == 'new':
        reg_badge = "\n> 🔴 **Nueva regresión** — este test pasaba en el run anterior.\n"
    elif regression == 'known':
        reg_badge = "\n> 🟡 **Issue conocido** — falló también en el run anterior.\n"

    sc = (
        f"\n## 📸 Screenshot\n\n![{test_id}]({cdn_url})\n"
        if cdn_url else
        "\n*No screenshot captured for this test.*\n"
    )
    return f"""## Bug Report

**Test ID**: `{test_id}`
**Component**: {label}
**Environment**: {TARGET}
**Date**: {TODAY}
{reg_badge}
## What happened
{detail}

## Steps to reproduce
1. Run `qa-architect-agent:execute` against `{TARGET}`
2. Observe test `{test_id}` — {label}

## Expected
Test should PASS without errors.
{sc}
---
*Filed automatically by [`qa-architect-agent`](https://github.com/SingularAgency/claude-marketplace)*"""

# Fetch existing issues to deduplicate
existing_issues = gh('GET', f"/repos/{REPO}/issues?state=open&labels=qa-agent&per_page=100")
existing_map = {}
if isinstance(existing_issues, list):
    for issue in existing_issues:
        m = re.search(r'\[([A-Z]+-\d+[a-z]?)\]', issue['title'])
        if m:
            existing_map[m.group(1)] = issue

summary = []

for r in fails:
    test_id    = r['id']
    label_txt  = r.get('label', 'Unknown')
    detail     = r.get('detail', '')
    severity   = r.get('severity', 'medium').lower()
    regression = r.get('regression')   # 'new' | 'known' | None
    sev_label  = severity_map.get(severity, 'priority: medium')
    cdn_url    = screenshot_urls.get(test_id)
    assignee   = get_assignee(label_txt)
    title      = f"🛑 [{test_id}] {detail[:80]}"

    # ── Existing issue: add screenshot comment ────────────────────────────────
    if test_id in existing_map:
        issue     = existing_map[test_id]
        issue_num = issue['number']
        reg_tag   = " 🔴 nueva regresión" if regression == 'new' else ""
        print(f"  ⏭️  {test_id}: #{issue_num} exists{reg_tag} → adding screenshot comment…")
        if cdn_url:
            comment = f"## 📸 Screenshot Evidence — {TODAY}\n\n![{test_id}]({cdn_url})\n\n*Captured by `qa-architect-agent` re-run.*"
            result = gh('POST', f"/repos/{REPO}/issues/{issue_num}/comments", {"body": comment})
            if 'id' in result:
                print(f"    ✅ Comment added")
        summary.append({'id': test_id, 'issue': issue_num, 'url': issue['html_url'], 'status': 'existing', 'regression': regression})
        time.sleep(0.5)
        continue

    # ── New issue ─────────────────────────────────────────────────────────────
    body    = build_body(test_id, label_txt, detail, cdn_url, regression)
    payload = {
        "title":  title,
        "body":   body,
        "labels": ['qa-agent', 'bug', sev_label],
    }
    if assignee:
        payload["assignees"] = [assignee]

    issue = gh('POST', f"/repos/{REPO}/issues", payload)

    if 'number' in issue:
        tags = []
        if cdn_url:     tags.append("📸")
        if assignee:    tags.append(f"👤 {assignee}")
        if regression == 'new':  tags.append("🔴 new regression")
        print(f"  ✅ #{issue['number']}: {title[:50]}  {' '.join(tags)}")
        summary.append({'id': test_id, 'issue': issue['number'], 'url': issue['html_url'], 'status': 'filed', 'regression': regression})
    else:
        print(f"  ❌ Failed: {issue.get('message','')}")
        summary.append({'id': test_id, 'status': 'error'})
    time.sleep(0.8)

with open('/tmp/qa-report-summary.json', 'w') as f:
    json.dump(summary, f)

new_count  = sum(1 for s in summary if s['status'] == 'filed')
dupe_count = sum(1 for s in summary if s['status'] == 'existing')
new_reg    = sum(1 for s in summary if s.get('regression') == 'new')
print(f"\n{'='*50}")
print(f"Filed: {new_count} new  |  Updated: {dupe_count} existing  |  🔴 New regressions: {new_reg}")
PYEOF
```

---

## Step 4 — Slack Notification

Post a QA run summary to Slack if a webhook is configured. This keeps the team informed automatically without anyone having to check GitHub manually.

```bash
python3 << 'PYEOF'
import json, urllib.request, urllib.error, os
from datetime import date

cfg_path = os.path.expanduser('~/.qa-agent-config.json')
cfg = json.loads(open(cfg_path).read()) if os.path.exists(cfg_path) else {}

WEBHOOK  = cfg.get('slack_webhook', '')
CHANNEL  = cfg.get('slack_channel', '#qa-reports')
REPO     = "<OWNER>/<REPO>"
TODAY    = date.today().isoformat()

if not WEBHOOK:
    print("⏭️  Slack notification skipped (no webhook configured — user opted out in wizard).")
    exit(0)

results  = json.loads(open('/tmp/qa-results/qa-results.json').read())
summary  = json.loads(open('/tmp/qa-report-summary.json').read()) if os.path.exists('/tmp/qa-report-summary.json') else []

total    = len(results)
passes   = sum(1 for r in results if r['status'] == 'PASS')
fails    = sum(1 for r in results if r['status'] == 'FAIL')
warns    = sum(1 for r in results if r['status'] == 'WARN')
new_regs = sum(1 for s in summary if s.get('regression') == 'new')
known    = sum(1 for s in summary if s.get('regression') == 'known')
filed    = [s for s in summary if s.get('status') == 'filed']

pass_rate = round(passes / total * 100) if total else 0
status_emoji = "✅" if fails == 0 else ("🔴" if new_regs > 0 else "🟡")

# Build issue links
issue_links = "  ".join(f"<{s['url']}|#{s['issue']}>" for s in filed[:8] if s.get('url'))

msg = {
    "channel": CHANNEL,
    "text": f"{status_emoji} *QA Run completado — {REPO}*",
    "blocks": [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"{status_emoji} QA Run — {TODAY}"}
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Repo:* `{REPO}`"},
                {"type": "mrkdwn", "text": f"*Pass rate:* {pass_rate}%  ({passes}/{total})"},
                {"type": "mrkdwn", "text": f"*✅ Pass:* {passes}   *❌ Fail:* {fails}   *⚠️ Warn:* {warns}"},
                {"type": "mrkdwn", "text": f"*🔴 New regressions:* {new_regs}   *🟡 Known issues:* {known}"},
            ]
        },
    ]
}

if filed:
    msg["blocks"].append({
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"*Issues abiertos:* {issue_links}" if issue_links else "*No se abrieron issues nuevos.*"}
    })

if new_regs > 0:
    new_ids = [s['id'] for s in summary if s.get('regression') == 'new']
    msg["blocks"].append({
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"🔴 *Regresiones nuevas:* `{'`, `'.join(new_ids)}`\n_Estos tests pasaban en el run anterior._"}
    })

msg["blocks"].append({"type": "divider"})
msg["blocks"].append({
    "type": "context",
    "elements": [{"type": "mrkdwn", "text": "Enviado automáticamente por `qa-architect-agent`"}]
})

req = urllib.request.Request(WEBHOOK, method='POST', data=json.dumps(msg).encode())
req.add_header('Content-Type', 'application/json')
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = r.read().decode()
        if resp == 'ok':
            print(f"✅ Slack notification sent to {CHANNEL}")
        else:
            print(f"⚠️  Slack response: {resp}")
except urllib.error.HTTPError as e:
    print(f"❌ Slack error {e.code}: {e.read().decode()[:200]}")
PYEOF
```

---

## Step 5 — Summary

Read `/tmp/qa-report-summary.json` and display:

| Test ID | Issue | Regression | Status |
|---------|-------|-----------|--------|
| EC-07 | [#29](url) | 🔴 New | ✅ Filed + 📸 + 👤 assigned |
| EH-04 | [#27](url) | 🟡 Known | ⏭️ Existing → screenshot comment |
| HP-02 | [#30](url) | — | ✅ Filed + 📸 |

End with:
> Se crearon **N** issues nuevos (🔴 **X** regresiones nuevas). **M** issues existentes actualizados. Notificación enviada a Slack ✅
