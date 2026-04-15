---
description: >
  QA Architect – Test Executor. Use this skill when the user says "ejecuta
  los tests", "run the QA tests", "ejecuta el plan", "run the test suite",
  "corre los tests", "execute QA", or after the user approves a test plan
  from the plan skill. Requires an approved plan at /tmp/qa-plan-approved.json
  or inline credentials and URL.
---

# qa-architect-agent: execute

You are a QA Executor. Run the approved test suite using Playwright headless Chromium. Follow every step in order — do not skip setup.

---

## Step 0 — Load Approved Plan

Check for an existing approved plan:

```bash
cat /tmp/qa-plan-approved.json 2>/dev/null || echo "NO_PLAN"
```

If no plan exists, tell the user to run the `plan` skill first (`qa-architect-agent:plan`) and get approval. Do not proceed without a plan or inline credentials.

If a plan exists, extract: `target_url`, `login_url`, `email`, `password`, `test_cases`.

---

## Step 1 — Environment Setup

### 1a. Detect existing Chromium/Chrome (ALWAYS run this first)

```bash
python3 - <<'EOF'
import os, subprocess

candidates = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium-1161/chrome-linux/chrome",
    "/opt/google/chrome/chrome",
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
]

# Also search cache directories
for root_dir in ["/root/.cache/puppeteer", "/home/claude/.cache/puppeteer"]:
    if os.path.isdir(root_dir):
        for dirpath, dirnames, filenames in os.walk(root_dir):
            for fname in filenames:
                if fname == "chrome" and "linux" in dirpath:
                    candidates.append(os.path.join(dirpath, fname))

for path in candidates:
    if os.path.isfile(path) and os.access(path, os.X_OK):
        try:
            result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5)
            version = (result.stdout + result.stderr).strip()
            print(f"FOUND:{path}:{version}")
            break
        except Exception:
            continue
else:
    print("NOT_FOUND")
EOF
```

- If output starts with `FOUND:`, use that path as `CHROME_EXECUTABLE`. Proceed to Step 1b.
- If output is `NOT_FOUND`, attempt to install:

```bash
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install -g playwright@latest 2>&1 | tail -3
npx playwright install --with-deps chromium 2>&1 | tail -10
```

If the install also fails (e.g. CDN blocked), report the error and stop. Do not attempt `web_fetch` as a workaround.

### 1b. Install Playwright npm package (no browser download)

```bash
cd /tmp && npm init -y 2>&1 | tail -1 && \
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install playwright 2>&1 | tail -3
```

### 1c. Create output directories

```bash
mkdir -p /tmp/qa-screenshots /tmp/qa-results
```

### 1d. Verify setup with a quick connectivity test

```bash
cd /tmp && node -e "
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({
    executablePath: process.env.CHROME_PATH,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--ignore-certificate-errors']
  });
  const ctx = await b.newContext({ ignoreHTTPSErrors: true });
  const p = await ctx.newPage();
  await p.goto('about:blank');
  await b.close();
  console.log('PLAYWRIGHT_OK');
})().catch(e => { console.error('PLAYWRIGHT_FAIL:', e.message); process.exit(1); });
" CHROME_PATH="<CHROME_EXECUTABLE>" 2>&1
```

If output is not `PLAYWRIGHT_OK`, report the error and stop.

---

## Step 2 — Write Test Script

Write the full test script to `/tmp/qa-suite.mjs`. The script must:

1. Accept `CHROME_PATH`, `TARGET_URL`, `LOGIN_URL`, `QA_EMAIL`, `QA_PASSWORD` as environment variables — never hardcode credentials.
2. Launch headless Chromium with `--no-sandbox --disable-setuid-sandbox --ignore-certificate-errors` and `ignoreHTTPSErrors: true`.
3. Use robust selectors that try multiple fallbacks (e.g. `input[type="email"], input[name="email"], input[placeholder*="email" i]`).
4. For each test case in the approved plan:
   - Execute the test action
   - Capture result (PASS / FAIL / WARN / SKIP) with a detail string
   - On FAIL, save a screenshot to `/tmp/qa-screenshots/<ID>.png`
5. Run tests in **batches of 5** to avoid memory/timeout issues. Wait 2s between batches.
6. Save all results to `/tmp/qa-results/qa-results.json`.
7. Print a final summary: total, PASS, FAIL, WARN, SKIP counts.

### Test execution rules

**Login flow (reuse session)**:
- After HP-01 (valid login) succeeds, capture cookies/storage and reuse the authenticated context for all subsequent Happy Path and Edge Case tests.
- For EC-07 (unauthenticated access), create a fresh `browser.newContext()` with no cookies.
- Re-login between Edge Case and Error Handling batches to ensure fresh state.

**Selector strategy** (use in this priority order):
1. `input[type="email"]` / `input[type="password"]`
2. `input[name="email"]` / `input[name="password"]`
3. `input[placeholder*="email" i]` / `input[placeholder*="password" i]`
4. `input[type="text"]:first-of-type` (last resort for email)

**Submit button strategy**:
1. `button[type="submit"]`
2. `button:has-text("Login")`, `button:has-text("Log in")`, `button:has-text("Sign in")`
3. `button:has-text("Iniciar")`, `button:has-text("Entrar")`
4. `input[type="submit"]`

**Navigation checks**: after `page.goto()`, always call `page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})` then `page.waitForTimeout(1500)`.

**Error detection**: a page has a server error if `body.innerText` contains `500`, `Internal Server Error`, or `sql` (case-insensitive).

---

## Step 3 — Execute Tests

Run the test script in batches. Total timeout: 600 seconds.

```bash
cd /tmp && timeout 600 node qa-suite.mjs 2>&1
```

Stream output to the user as it runs. If the process times out, report partial results from whatever was written to `/tmp/qa-results/qa-results.json`.

---

## Step 4 — Report Summary

After execution completes, read `/tmp/qa-results/qa-results.json` and display:

1. A summary table:

| Status | Count |
|--------|-------|
| ✅ PASS | N |
| ❌ FAIL | N |
| ⚠️ WARN | N |
| ⏭️ SKIP | N |
| **Total** | **N** |

2. A list of all FAILs and WARNs with their IDs, components, and detail messages.

3. Ask the user:

> ¿Deseas que reporte los bugs encontrados en GitHub? Puedo abrir un issue por cada FAIL usando el skill `qa-architect-agent:report`.

Save the results path for the report skill: `/tmp/qa-results/qa-results.json`.
