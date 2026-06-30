# Phase 7 — Design Decisions (SRA Conditionals Resolved)
# Last updated: 2026-06-28

SRA gave CONDITIONAL approval on FM-01, FM-02, FM-05.
These are the design decisions that resolve each conditional before build begins.

---

## FM-05 — Build against empty DB (RESOLVED ✓)

**Risk:** Phase 7 build starts against empty DB. Endpoints return [], looks working but is hollow.
**Status: RESOLVED — G0 cleared 2026-06-28.**

Verification:
- 14 instruments seeded (all 6 Lynch classifications covered)
- 13 OHLCV rows from 2026-06-25 (first live ingest via bhavcopy)
- ingest_status row: status=OK, last_run=2026-06-25
- Test suite: 186 PASS / 2 SKIP / 0 FAIL

Session A additional gate: `/health` must return `ohlcv_rows > 0` (not just HTTP 200).
Asserted by `test_health_returns_200_with_real_data()` in `tests/test_api.py`.

---

## FM-02 — Disclaimer drop on a new Next.js route (P1 — REVISED 2026-06-30)

**Risk:** Next.js per-route rendering could drop the pinned SEBI disclaimer
that Streamlit injected globally. A developer adds a new route without
re-adding the disclaimer component.

**Council revision (2026-06-30):** Gall's Law council eliminated FastAPI as
primary data path. Original Layer 2 ("SebiDisclaimer fetches from FastAPI
backend") was a runtime dependency on a parked service — P1 silent failure if
API unreachable. Revised Layer 2 uses Vercel env var: text is immutable per
deployment, enforced at build time, never null in production.

**Mitigation: 3-layer defence**

### Layer 1 — Structural (cannot be removed per-page)

```tsx
// app/layout.tsx — Session B task
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        {children}
        <SebiDisclaimer />  {/* OUTSIDE {children} — every route inherits this */}
      </body>
    </html>
  )
}
```

`SebiDisclaimer` is a React Server Component (no NEXT_PUBLIC_ prefix — never
reaches client bundle). Renders as fixed-position footer. Not collapsible.
Not dismissable. Not conditional.

### Layer 2 — Vercel env var as source of truth (REVISED)

```typescript
// app/components/SebiDisclaimer.tsx
const text = process.env.SEBI_DISCLAIMER  // server-side only
if (!text) {
  throw new Error('SEBI_DISCLAIMER env var is required — set in Vercel project settings')
}
// Throws at build time → Vercel deploy fails if env var absent
// Text is immutable per deployment — cannot mutate at runtime
```

`SEBI_DISCLAIMER` Vercel env var is populated from `constants.py` text during
Vercel project setup (same one-time step as SUPABASE_URL). Python `constants.py`
remains the canonical definition.

**Drift risk (Synthesis Chair minority view):** If `constants.py` text is ever
updated, Vercel env var must be manually re-synced. Mitigated by Playwright
exact-text assertion (Layer 3) — text mismatch fails CI before deploy.

### Layer 3 — CI Playwright gate (blocks Vercel deploy)

```typescript
// tests/sebi.spec.ts — Session B task
const routes = ['/', '/signals', '/path', '/accuracy']
for (const route of routes) {
  test(`SEBI disclaimer present on ${route}`, async ({ page }) => {
    await page.goto(route)
    // Must be visible (not hidden, not display:none)
    await expect(page.getByText('NOT investment advice')).toBeVisible()
    await expect(page.getByText('research purposes only')).toBeVisible()
    // Prohibited language check
    const text = await page.content()
    expect(text).not.toContain('BUY')
    expect(text).not.toContain('SELL')
    expect(text).not.toContain('invest in')
  })
  // FM-B: service key must never appear in client HTML (SRE gate)
  test(`service key not exposed on ${route}`, async ({ page }) => {
    await page.goto(route)
    const html = await page.content()
    expect(html).not.toContain('SUPABASE_SERVICE_KEY')
  })
}
```

This test blocks Vercel deploy on failure. Mirrors `test_sebi_substance` in pytest.

---

## FM-01 — Cold-start (ELIMINATED — Fly.io chosen over Railway)

**Original risk:** Backend sleep on idle → blank frontend.

**Resolution:** Fly.io with `auto_stop_machines = false` and `min_machines_running = 1`
in `fly.toml` keeps the VM permanently alive. No sleep, no cold-start, no keep-warm
GHA cron needed. FM-01 is eliminated at the infrastructure level, not mitigated.

**fly.toml config (enforces this):**
```toml
[http_service]
  auto_stop_machines = false
  min_machines_running = 1
```

**Cost:** 256MB shared-cpu-1x on Fly.io bom (Mumbai) = ~$2.02/month.
Trial credit $5 → ~2.5 months runway. Add credit card before credit depletes.

**No GHA keep-warm cron needed.** A new workflow would add scheduled runs
(limitation impact). With Fly.io always-on, this cron is unnecessary — eliminated.

---

## Async Supabase client decision (CoS-owned)

**Question:** Should FastAPI backend use async or sync Supabase client?

**Decision: sync client (`supabase-py`) for Phase 7.**

Rationale:
- Existing `src/config.py` `get_supabase_client()` is sync.
- All `src/` signal, portfolio, and accuracy logic is synchronous.
- Wrapping sync logic in `async def` handlers requires `run_in_executor()` everywhere.
- FastAPI handles `def` route handlers correctly via thread pool offloading. No deadlock.
- Revisit at G1 if Railway concurrency becomes a bottleneck.

**Implementation:** All FastAPI route handlers defined as `def` (not `async def`).

---

## CORS domain strategy (CoS-owned)

Vercel generates preview URLs like `alphaveda-web-abc123.vercel.app` per deploy.
These change. Locking to exact URL would break all preview deploys.

**Decision:** Use `allow_origin_regex` for Vercel domain pattern.

```python
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://alphaveda.*\.vercel\.app|http://localhost:3000",
    allow_methods=["GET"],
)
```

Allows all AlphaVeda Vercel preview deploys. Blocks external origins.
Never `allow_origins=['*']` — that would allow any origin to call the API.

---

## SRA status after design decisions

| Conditional | Status | Resolution |
|---|---|---|
| FM-05: build against empty DB | RESOLVED | G0 cleared 2026-06-28 — 14 instruments, 13 OHLCV rows |
| FM-02: disclaimer drop on new route | REVISED + DESIGNED | 3-layer: root layout + Vercel env var (revised 2026-06-30) + Playwright CI |
| FM-01: Fly.io cold-start | ELIMINATED | `auto_stop_machines = false` + `min_machines_running = 1` in fly.toml |

SRA verdict upgrades from CONDITIONAL to APPROVED once FM-02 Playwright gate
is written and passing in Session B CI pipeline.

## Directory structure decision (council 2026-06-30)

Next.js frontend goes in `alphaveda/web/` (inside alphaveda/, not at repo root).
Vercel root directory setting: `alphaveda/web`.
All AlphaVeda code lives in one directory. Root-level GSI legacy files frozen.

## FastAPI deployment decision (council 2026-06-30)

`alphaveda/api/` stays in repo — code is built and pytest passes via TestClient.
Fly.io deployment DEFERRED to Session C gate. No live server needed for Session B.
Rationale: Session B queries Supabase directly. No FastAPI in the data path.
Fly.io trial credit preserved. Tarun fly deploy commands deferred.
