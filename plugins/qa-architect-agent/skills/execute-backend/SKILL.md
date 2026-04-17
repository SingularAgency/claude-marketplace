---
description: >
  QA Backend – k6 Executor. Use this skill when the user says "testea el
  backend", "run API tests", "ejecuta k6", "prueba los endpoints", "testea
  los websockets", "prueba GraphQL", or after qa-architect routes a backend
  test plan for execution.
---

# qa-architect-agent: execute-backend

You are a k6 expert. Your job is to execute backend API test plans — functional correctness, auth enforcement, and optional load/performance testing. You support REST, WebSockets, GraphQL, and gRPC.

---

## Step 0 — Load Testing Wizard (ALWAYS RUN FIRST)

Present this before doing anything else:

```
🔧 ¿Quieres incluir load testing? (opcional)

k6 puede simular múltiples usuarios concurrentes para medir rendimiento.

1️⃣  Solo functional tests (rápido, ~2-3 min) — recomendado
2️⃣  Functional + load básico (10 VUs × 30s) — detecta regresiones de rendimiento
3️⃣  Functional + load completo (rampa 1→50 VUs, 5 min) — stress test real

¿Qué prefieres? (escribe 1, 2 o 3)
```

Store the selection as `$LOAD_MODE` (1 = functional_only, 2 = basic_load, 3 = full_load).
**Never start load tests without an explicit selection.**

---

## Step 1 — Read Approved Plan

Read `/tmp/qa-plan-approved.json`. Extract:
- `target_url` → `BASE_URL`
- `email`, `password` → auth credentials
- `route_map.api` → list of API endpoints to test
- `protocols` (if present) → `["REST", "WebSocket", "GraphQL", "gRPC"]`

If the file doesn't exist, stop:
> "No hay un plan aprobado. Genera y aprueba un plan con `qa-architect-agent:plan` primero."

---

## Step 2 — Environment Setup

```bash
# Install k6
if ! which k6 2>/dev/null; then
  curl -sL https://github.com/grafana/k6/releases/download/v0.51.0/k6-v0.51.0-linux-amd64.tar.gz \
    | tar xz -C /tmp/ && sudo mv /tmp/k6-v0.51.0-linux-amd64/k6 /usr/local/bin/ 2>/dev/null \
  || echo "Could not install k6 — trying apt..."
  curl -s https://dl.k6.io/key.gpg | gpg --dearmor | sudo tee /usr/share/keyrings/k6-archive-keyring.gpg >/dev/null 2>&1
  echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list >/dev/null
  sudo apt-get update -qq && sudo apt-get install -y k6 2>/dev/null
fi

k6 version
mkdir -p /tmp/k6-tests /tmp/k6-results
```

---

## Step 3 — Get Auth Token

### Supabase (most common with this stack)

```bash
# Get Supabase URL and anon key from the app's environment or ask the user
# Try to extract from the repo or from the plan JSON
SUPABASE_URL=$(cat /tmp/qa-plan-approved.json | python3 -c "import json,sys; p=json.load(sys.stdin); print(p.get('supabase_url',''))" 2>/dev/null)
SUPABASE_ANON_KEY=$(cat /tmp/qa-plan-approved.json | python3 -c "import json,sys; p=json.load(sys.stdin); print(p.get('supabase_anon_key',''))" 2>/dev/null)
EMAIL=$(cat /tmp/qa-plan-approved.json | python3 -c "import json,sys; p=json.load(sys.stdin); print(p.get('email',''))")
PASSWORD=$(cat /tmp/qa-plan-approved.json | python3 -c "import json,sys; p=json.load(sys.stdin); print(p.get('password',''))")

# Get token via Supabase Auth
TOKEN=$(curl -s -X POST \
  "${SUPABASE_URL}/auth/v1/token?grant_type=password" \
  -H "Content-Type: application/json" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\"}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin).get('access_token',''))")

if [ -z "$TOKEN" ] || [ "$TOKEN" = "None" ]; then
  echo "⚠️  Supabase token not obtained. Trying Next.js session..."
  # Fallback: Next.js credentials
  TOKEN=$(curl -s -X POST "${BASE_URL}/api/auth/callback/credentials" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\"}" \
    -c /tmp/cookies.txt | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('token',''))" 2>/dev/null)
fi

echo "Token obtained: ${TOKEN:0:20}..."
```

---

## Step 4 — Get a Real Test ID

```bash
# Fetch a real resource ID from the API (never use hardcoded/fake IDs)
TEST_ID=$(curl -s -H "Authorization: Bearer ${TOKEN}" \
  "${BASE_URL}/api/proposals" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
# Handle both array and {data:[...]} shapes
items = data if isinstance(data, list) else data.get('data', data.get('proposals', []))
if items: print(items[0].get('id', ''))
else: print('')
")

echo "Test ID: $TEST_ID"
```

---

## Step 5 — Write k6 Test Suite

Write `/tmp/k6-tests/suite.js` based on the approved plan's endpoint list and `$LOAD_MODE`.

```javascript
import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const latency = new Trend('latency', true);

// Load mode injected by runner
const LOAD_MODE = __ENV.LOAD_MODE || '1';

// Stage configs
const stages = {
  '1': [{ duration: '30s', target: 1 }],                                               // functional only
  '2': [{ duration: '10s', target: 10 }, { duration: '20s', target: 10 }, { duration: '5s', target: 0 }],  // basic
  '3': [{ duration: '60s', target: 10 }, { duration: '120s', target: 30 }, { duration: '60s', target: 50 }, { duration: '30s', target: 0 }], // full
};

export let options = {
  stages: stages[LOAD_MODE] || stages['1'],
  thresholds: {
    'http_req_duration': LOAD_MODE === '3' ? ['p(95)<3000'] : ['p(95)<2000'],
    'http_req_failed': ['rate<0.05'],
    'errors': ['rate<0.10'],
  },
};

export function setup() {
  // Get token once, share with all VUs
  const authRes = http.post(
    `${__ENV.SUPABASE_URL}/auth/v1/token?grant_type=password`,
    JSON.stringify({ email: __ENV.EMAIL, password: __ENV.PASSWORD }),
    { headers: { 'Content-Type': 'application/json', 'apikey': __ENV.SUPABASE_ANON_KEY } }
  );
  const token = authRes.status === 200 ? JSON.parse(authRes.body).access_token : null;
  return { token, baseUrl: __ENV.BASE_URL, testId: __ENV.TEST_ID };
}

export default function(data) {
  const { token, baseUrl, testId } = data;
  const auth = { headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } };
  const noAuth = { headers: { 'Content-Type': 'application/json' } };

  // ── AUTHENTICATED ENDPOINTS ──────────────────────────────
  group('LIST resources (authenticated)', () => {
    const res = http.get(`${baseUrl}/api/proposals`, auth);
    const ok = check(res, {
      '200 status': r => r.status === 200,
      'returns data': r => { try { const b = JSON.parse(r.body); return Array.isArray(b) || b.data || b.proposals; } catch { return false; } },
      'response < 2s': r => r.timings.duration < 2000,
    });
    errorRate.add(!ok);
    latency.add(res.timings.duration);
  });

  group('GET single resource', () => {
    if (!testId) return;
    const res = http.get(`${baseUrl}/api/proposals/${testId}`, auth);
    check(res, {
      '200 status': r => r.status === 200,
      'has id': r => { try { return JSON.parse(r.body).id !== undefined; } catch { return false; } },
    });
    latency.add(res.timings.duration);
  });

  // ── AUTH BOUNDARY (security) ────────────────────────────
  group('AUTH BOUNDARY — no token', () => {
    const securityEndpoints = [
      { method: 'GET',    url: `${baseUrl}/api/proposals` },
      { method: 'GET',    url: `${baseUrl}/api/proposals/${testId || 'test-id'}` },
      { method: 'POST',   url: `${baseUrl}/api/proposals/generate`,       body: '{}' },
      { method: 'POST',   url: `${baseUrl}/api/chat`,                     body: '{}' },
      { method: 'PUT',    url: `${baseUrl}/api/proposals/${testId || 'test-id'}`, body: '{}' },
      { method: 'DELETE', url: `${baseUrl}/api/proposals/${testId || 'test-id'}` },
    ];

    for (const ep of securityEndpoints) {
      const res = ['POST','PUT','PATCH'].includes(ep.method)
        ? http.request(ep.method, ep.url, ep.body ?? null, noAuth)
        : http.get(ep.url, noAuth);

      const isSecure = [401, 403].includes(res.status);
      const ok = check(res, {
        [`${ep.method} ${ep.url.split('/api/')[1]} → 401/403`]: r => [401, 403].includes(r.status),
      });
      errorRate.add(!ok);
    }
  });

  sleep(0.5);
}

export function handleSummary(data) {
  return { '/tmp/k6-results/summary.json': JSON.stringify(data, null, 2) };
}
```

---

## Step 6 — Run k6

```bash
k6 run \
  --env LOAD_MODE="${LOAD_MODE}" \
  --env BASE_URL="${BASE_URL}" \
  --env SUPABASE_URL="${SUPABASE_URL}" \
  --env SUPABASE_ANON_KEY="${SUPABASE_ANON_KEY}" \
  --env EMAIL="${EMAIL}" \
  --env PASSWORD="${PASSWORD}" \
  --env TEST_ID="${TEST_ID}" \
  --out json=/tmp/k6-results/raw.ndjson \
  /tmp/k6-tests/suite.js 2>&1 | tee /tmp/k6-results/stdout.txt
```

---

## Step 7 — Parse Results

```bash
python3 - << 'PYEOF'
import json, sys
from collections import defaultdict

durations, failed_requests, checks_pass, checks_fail = [], [], 0, 0
groups_data = defaultdict(lambda: {'checks': [], 'durations': []})

with open('/tmp/k6-results/raw.ndjson') as f:
    for line in f:
        try:
            obj = json.loads(line.strip())
            if obj['type'] == 'Point':
                m = obj['metric']
                v = obj['data']['value']
                tags = obj['data'].get('tags', {})
                grp = tags.get('group', 'ungrouped')

                if m == 'http_req_duration':
                    durations.append(v)
                    groups_data[grp]['durations'].append(v)
                elif m == 'http_req_failed' and v > 0:
                    failed_requests.append(tags.get('url', '?'))
                elif m == 'checks':
                    if v == 1: checks_pass += 1
                    else: checks_fail += 1
        except:
            pass

results = {
    'run_at': __import__('datetime').datetime.utcnow().isoformat(),
    'load_mode': '$LOAD_MODE',
    'target_url': '$BASE_URL',
    'summary': {},
    'security_boundaries': [],
    'thresholds_met': True
}

if durations:
    durations.sort()
    n = len(durations)
    p95_idx = int(n * 0.95)
    p99_idx = int(n * 0.99)
    error_rate = len(failed_requests) / n * 100 if n > 0 else 0
    
    results['summary'] = {
        'total_requests': n,
        'checks_passed': checks_pass,
        'checks_failed': checks_fail,
        'error_rate_pct': round(error_rate, 2),
        'avg_ms': round(sum(durations) / n, 1),
        'p50_ms': round(durations[n // 2], 1),
        'p95_ms': round(durations[p95_idx], 1),
        'p99_ms': round(durations[p99_idx], 1),
        'max_ms': round(durations[-1], 1),
    }
    
    print(f"\n📊 K6 RESULTS")
    print(f"{'='*40}")
    print(f"  Total requests: {n}")
    print(f"  Checks passed:  {checks_pass}")
    print(f"  Checks failed:  {checks_fail}")
    print(f"  Error rate:     {error_rate:.1f}%")
    print(f"  avg latency:    {results['summary']['avg_ms']}ms")
    print(f"  p95 latency:    {results['summary']['p95_ms']}ms")
    print(f"  p99 latency:    {results['summary']['p99_ms']}ms")
    print(f"  max latency:    {results['summary']['max_ms']}ms")
    
    # Threshold check
    if results['summary']['p95_ms'] > 2000:
        print(f"\n⚠️  THRESHOLD BREACH: p95 > 2000ms ({results['summary']['p95_ms']}ms)")
        results['thresholds_met'] = False
    if error_rate > 5:
        print(f"\n🔥 HIGH ERROR RATE: {error_rate:.1f}% (threshold: 5%)")
        results['thresholds_met'] = False
else:
    print("No duration data found in results")

with open('/tmp/k6-results/results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Results saved to /tmp/k6-results/results.json")
PYEOF
```

---

## Step 8 — Report

Show the final summary table:

```
📊 BACKEND TEST RESULTS
════════════════════════════════════
Protocol:   REST [+ WebSocket] [+ GraphQL]
Load mode:  functional_only / basic_load / full_load
Target:     https://...

Requests:   N total
Checks:     X pass / Y fail
Error rate: X.X%
avg:        XXXms | p95: XXXms | p99: XXXms

Security boundaries:
  ✅ GET /api/proposals → 401 ✓
  ✅ POST /api/chat → 401 ✓
  ❌ PUT /api/proposals/:id → 200 (CRITICAL — no auth!)
════════════════════════════════════
```

If any security boundary FAILs (endpoint returned 200 without token), flag as:
```
🚨 CRITICAL: [N] endpoint(s) accessible without authentication
   → Run `qa-architect-agent:report` to file GitHub issues
```

If thresholds breached, flag as:
```
🔥 PERFORMANCE: p95 = Xms (threshold 2000ms) — investigate slow endpoints
```
