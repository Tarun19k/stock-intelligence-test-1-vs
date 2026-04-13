# GSI Dashboard — Vercel Migration Plan
**Researched:** 2026-04-13 | session_024
**Current version:** v5.36 | 556 tickers, 9 markets, 38 groups

---

## Current Architecture Summary

Streamlit monolith on Streamlit Community Cloud:
- **Entry point:** `app.py` → routes to 4 pages via MPA (sidebar CSS-hidden)
- **Data layer:** `market_data.py` — yfinance 1.2.0 with token bucket rate limiter (module-level globals)
- **Signal engine:** `indicators.py` — RSI, MACD, Bollinger, Weinstein, Elder, unified verdict
- **Portfolio:** `portfolio.py` — Mean-CVaR via cvxpy (Clarabel solver), exponential bootstrap
- **Forecast:** `forecast.py` + `indicators.py` — historical simulation, stored in `st.session_state` (no persistence)
- **State:** `st.session_state` throughout — lost on every session restart
- **Secrets:** Only `DEV_TOKEN` (observability page gate)
- **RAM:** 1GB Streamlit Community Cloud

### Critical migration constraints found
1. `_global_throttle()` (market_data.py:103–118) uses Python module-level globals (threading.Lock, token counter) — **cannot be shared across Vercel function instances** → needs Upstash Redis for distributed rate limiting
2. `_ticker_cache` dict (market_data.py:151–153) is module-level — **lost per function invocation** on Vercel → needs Vercel KV or Redis for cross-instance caching
3. `render_ticker_bar()` (home.py:67–177) injects JavaScript via `st.components.v1.html()` to manipulate parent iframe DOM — **not applicable in Next.js** → use CSS `position: fixed` directly
4. `optimise_mean_cvar()` (portfolio.py:207) runs Clarabel CVXPY solver inline — needs **isolated Fluid Compute function with 1024 MB RAM**
5. Four SEBI disclaimer gaps (OPEN-022/027/028/029) are resolved structurally by creating a shared `<SebiDisclaimer />` React component
6. `st.markdown(unsafe_allow_html=True)` used ~80 times across pages — **XSS risk** (RISK-001) resolved by `DOMPurify` in `lib/sanitise.ts`

---

## Target Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Next.js App Router (Frontend)                   │
│  /           → HomePage (TickerBar + GlobalSignals)          │
│  /dashboard  → DashboardPage (Charts/Forecast/Compare/KPIs) │
│  /summary    → WeekSummaryPage                               │
│  /global     → GlobalIntelligencePage                        │
│  /health     → ObservabilityPage (DEV_TOKEN gated)          │
└──────────────────┬──────────────────────────────────────────┘
                   │ API Routes (Next.js) + Python Functions
┌──────────────────▼──────────────────────────────────────────┐
│              Vercel Functions (Python 3.14)                  │
│  /api/market-data  → market_data.py functions                │
│  /api/indicators   → indicators.py compute_indicators()      │
│  /api/portfolio    → portfolio.py (1GB Fluid Compute)        │
│  /api/signals      → compute_unified_verdict()               │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              Workflow DevKit (Long-Running Ops)              │
│  get_batch_data()      → workflow step + RetryableError      │
│  optimise_mean_cvar()  → workflow step (300s timeout)        │
│  compute_forecast()    → workflow step (2000 simulations)    │
│  CEO validation gate   → createHook() approval flow          │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              External Services                               │
│  Upstash Redis    → distributed rate limiter + ticker cache  │
│  Supabase         → forecast_history (resolves OPEN-003)     │
│  yfinance 1.2.0   → pinned, runs in Python function          │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Scaffold (Week 1–2)

### 1.1 Create Next.js app
```bash
npx create-next-app@latest gsi-web --typescript --tailwind --app
```

### 1.2 Vercel configuration (`vercel.ts`)
```typescript
import { type VercelConfig } from '@vercel/config/v1';
export const config: VercelConfig = {
  framework: 'nextjs',
  functions: {
    'api/portfolio.py':   { memory: 1024, maxDuration: 300 },
    'api/market-data.py': { memory: 512,  maxDuration: 60  },
    'api/indicators.py':  { memory: 512,  maxDuration: 30  },
  },
  crons: [
    { path: '/api/ticker-cache-warm', schedule: '0 */6 * * *' },
  ],
};
```

### 1.3 Environment variables
| Variable | Purpose | Source |
|---|---|---|
| `DEV_TOKEN` | Observability page gate | Existing `st.secrets.DEV_TOKEN` |
| `UPSTASH_REDIS_URL` | Distributed rate limiter | New — Vercel Marketplace |
| `UPSTASH_REDIS_TOKEN` | Redis auth | New — Vercel Marketplace |
| `SUPABASE_URL` | Forecast history DB | New — Vercel Marketplace |
| `SUPABASE_ANON_KEY` | Supabase auth | New — Vercel Marketplace |
| `NEXT_PUBLIC_APP_VERSION` | Version display | From `version.py` |

### 1.4 Python API route structure
```
api/
  market-data.py   → wraps get_price_data(), get_ticker_info(), get_live_price()
  indicators.py    → wraps compute_indicators(), signal_score()
  portfolio.py     → wraps optimise_mean_cvar(), compute_efficient_frontier()
  forecast.py      → wraps compute_forecast(), store_forecast()
  tickers.py       → serves tickers.json as JSON API
```

---

## Phase 2: Data Layer Migration (Week 3–4)

### 2.1 Rate limiting → Upstash Redis
Replace `_global_throttle()` module-level token bucket with Redis sliding window:
```python
# api/market-data.py
from upstash_ratelimit import Ratelimit, SlidingWindow
from upstash_redis import Redis

ratelimit = Ratelimit(
    redis=Redis.from_env(),
    limiter=SlidingWindow(max_requests=5, window="2s"),
)
```

### 2.2 Cache → Vercel KV + `unstable_cache`
Replace `_ticker_cache` module dict with Vercel KV:
```python
# Cache entries per TTL tier (matches current market_data.py TTLs)
TTLs = {
    "live_price": 5,      # seconds
    "ohlcv": 300,
    "ticker_info": 600,
    "news": 600,
    "financials": 86400,
}
```

### 2.3 Workflow steps for long-running operations
```typescript
// workflows/market-data.ts
async function fetchBatchData(tickers: string[], period: string) {
  "use step"; // auto-retry on 429, result persisted for replay
  const resp = await fetch('/api/market-data', {
    method: 'POST',
    body: JSON.stringify({ tickers, period }),
  });
  if (resp.status === 429) {
    throw new RetryableError("Rate limited", { retryAfter: "2s" });
  }
  return resp.json();
}

export async function marketDataWorkflow(tickers: string[]) {
  "use workflow";
  // Batch in chunks of 3 (mirrors CHUNK=3 in market_data.py)
  const chunks = chunkArray(tickers, 3);
  for (const chunk of chunks) {
    await fetchBatchData(chunk, "3mo");
    await sleep("5s"); // mirrors inter-chunk=5s
  }
}
```

### 2.4 OPEN-003 resolution — Supabase forecast persistence
```sql
-- Supabase migration
CREATE TABLE forecast_history (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ticker      text NOT NULL,
  date        date NOT NULL,
  horizon     integer NOT NULL,
  p_gain      float NOT NULL,
  p10         float, p25 float, p50 float, p75 float, p90 float,
  hw_target   float,
  resolved    boolean DEFAULT false,
  actual_gain boolean,
  created_at  timestamptz DEFAULT now()
);
```

---

## Phase 3: UI Migration (Week 5–8)

### 3.1 Page-by-page migration order
1. **ObservabilityPage** — simplest, no data dependencies, DEV_TOKEN gate test
2. **WeekSummaryPage** — market overview, group signals, no live data
3. **GlobalIntelligencePage** — geopolitical topics, watchlists, RSS news
4. **HomePage** — TickerBar fragment, global signals, top movers
5. **DashboardPage** — most complex: 4 tabs, live price fragment, forecast, compare

### 3.2 Streamlit fragment → React SWR pattern
```tsx
// Replaces @st.fragment(run_every=60) for global signals
import useSWR from 'swr';

export function GlobalSignalsPanel() {
  const { data } = useSWR('/api/signals/global', fetcher, {
    refreshInterval: 60_000,  // matches run_every=60
  });
  return <SignalGrid data={data} />;
}
```

### 3.3 SEBI disclaimer — shared component (resolves OPEN-022/027/028/029)
```tsx
// components/SebiDisclaimer.tsx
export function SebiDisclaimer({ compact = false }: { compact?: boolean }) {
  return (
    <p className={compact ? 'text-xs text-muted-foreground' : 'text-sm text-muted-foreground mt-4'}>
      For educational purposes only. Not SEBI-registered investment advice.
      Consult a SEBI-registered advisor before investing.
    </p>
  );
}
// Used on every page section that shows BUY/WATCH/AVOID signals
```

---

## Phase 4: Cutover (Week 9–10)

### 4.1 Deployment sequence
1. Deploy Next.js app to Vercel (preview URL)
2. Feature-flag test for 7 days (DEV_TOKEN users only)
3. QA brief per `qa-brief` skill on Vercel preview URL
4. Playwright suite run against Vercel preview
5. DNS: `gsi.example.com` → Vercel deployment
6. Streamlit Community Cloud: set to "private" (don't delete immediately)
7. Monitor for 2 weeks → then sunset Streamlit

### 4.2 Cost comparison
| Item | Streamlit Community Cloud | Vercel (Hobby) | Vercel (Pro) |
|---|---|---|---|
| Monthly cost | Free | Free | $20/month |
| Compute | 1GB shared | Fluid (on-demand) | Fluid (on-demand) |
| Bandwidth | Limited | 100 GB/month | 1 TB/month |
| Cron jobs | None | 2/day | Unlimited |
| Analytics | None | Basic | Full |

---

## Open Items Resolution After Migration

| OPEN ID | Status after migration | Notes |
|---|---|---|
| OPEN-001/005 | Resolved | config_OLD.py removed in cleanup |
| OPEN-003 | **RESOLVED** | Supabase forecast_history table |
| OPEN-007 | Replaced | DataManager → Vercel KV + workflow steps |
| OPEN-022/027/028/029 | **RESOLVED** | `<SebiDisclaimer />` component enforced at layout level |
| RISK-001 | **RESOLVED** | `lib/sanitise.ts` + DOMPurify replaces `unsafe_allow_html=True` |
| OPEN-009 | Carried | Neutral zone 45–55% — still needs implementation |
| D2-03/D2-04 | Carried | Elder Screen 3, `veto_applied` flag — still needs implementation |

---

*Generated by Vercel migration research agent (Track C) | 2026-04-13 | session_024*
