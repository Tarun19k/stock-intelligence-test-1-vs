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

## FM-02 — Disclaimer drop on a new Next.js route (P1 — DESIGNED)

**Risk:** Next.js per-route rendering could drop the pinned SEBI disclaimer
that Streamlit injected globally. A developer adds a new route without
re-adding the disclaimer component.

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

`SebiDisclaimer` is a React Server Component. It fetches the disclaimer
text from the FastAPI backend (`/health` or a dedicated `/disclaimer` endpoint).
Single source of truth = Python `constants.py`. Renders as fixed-position footer.
Not collapsible. Not dismissable. Not conditional.

### Layer 2 — Backend as source of truth

Every API response envelope contains `sebi_disclaimer: "AlphaVeda provides..."`.
Frontend renders the backend-provided string, never its own copy.
Text cannot drift between Python and TypeScript.

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
}
```

This test blocks Vercel deploy on failure. Mirrors `test_sebi_substance` in pytest.

---

## FM-01 — Railway cold-start / blank frontend (P2 — DESIGNED)

**Risk:** Railway free-tier dyno sleeps after 15 min idle. First request
times out. Frontend shows blank screen or unhandled error.

**Mitigation: 2-part design**

### Part 1 — Keep-warm ping (prevents sleep during market hours)

```yaml
# .github/workflows/keepwarm.yml — Session A task
on:
  schedule:
    - cron: '*/14 * * * *'  # every 14 min — under Railway's 15-min sleep threshold
jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - name: Keep Railway warm
        run: |
          curl -f ${{ secrets.RAILWAY_API_URL }}/health || echo "Warm-up ping sent"
```

NSE market hours: 9:15am–3:30pm IST = UTC 3:45am–10:00am.
Keep-warm runs all day (cheap GHA minutes, no Railway cost).

### Part 2 — Frontend graceful degradation (never shows blank screen)

```tsx
// In any Server Component that fetches from Railway — Session B task
async function fetchWithTimeout(url: string, ms = 30000) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), ms)
  try {
    return await fetch(url, { signal: controller.signal })
  } catch {
    return null  // triggers WarmingState, not a crash
  } finally {
    clearTimeout(timeout)
  }
}

// If fetch returns null: show WarmingState, not an error boundary crash
function WarmingState() {
  return (
    <div className="warming-state">
      AlphaVeda is warming up. Data will load in a few seconds.
      <button onClick={() => location.reload()}>Refresh</button>
    </div>
  )
}
```

### Upgrade path (if cold-start persists)

Upgrade Railway to Starter ($5/month) for always-on dyno.
Decision deferred until first subscriber confirms value.
Budget signal: if any single subscriber complains about blank screen → upgrade.

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
| FM-02: disclaimer drop on new route | DESIGNED | 3-layer: root layout + backend envelope + Playwright CI |
| FM-01: Railway cold-start | DESIGNED | Keep-warm GHA cron + frontend WarmingState + 30s timeout |

SRA verdict upgrades from CONDITIONAL to APPROVED once FM-02 Playwright gate
is written and passing in Session B CI pipeline.
