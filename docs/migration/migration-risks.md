# GSI Dashboard — Vercel Migration Risk Register
**Researched:** 2026-04-13 | session_024
**Source:** Code audit of market_data.py, portfolio.py, indicators.py, all pages

---

## Technical Risks

| Risk ID | Risk | Severity | Likelihood | Mitigation |
|---|---|---|---|---|
| MR-01 | cvxpy Clarabel solver cold start on Vercel (first invocation may take 10–15s) | HIGH | HIGH | Pre-warm via cron job; set Fluid Compute `maxDuration=300`; test Clarabel in Python 3.14 on Vercel before commit |
| MR-02 | yfinance rate limits under concurrent Vercel requests (multiple users → 429 from Yahoo Finance) | HIGH | HIGH | Workflow `RetryableError({ retryAfter: "2s" })`; Upstash Redis distributed rate limiter (replaces `_global_throttle()`); request deduplication via Redis |
| MR-03 | Module-level `_ticker_cache` dict not shared across Vercel function instances — each cold start rebuilds cache | HIGH | CERTAIN | Upstash Redis for shared ticker cache; replicate `is_ticker_cache_warm()` logic against Redis key presence |
| MR-04 | `st.session_state["forecast_history"]` lost on every function restart — OPEN-003 | MED | CERTAIN | Supabase `forecast_history` table (migration resolves OPEN-003); required before cutover |
| MR-05 | SEBI disclaimer gaps (OPEN-022/027/028/029) must be present on all migrated pages | HIGH | MED | `<SebiDisclaimer />` shared component; layout.tsx enforces on all signal sections; Playwright tests must verify |
| MR-06 | `st.markdown(unsafe_allow_html=True)` used ~80 times — XSS exposure (RISK-001) | HIGH | MED | `lib/sanitise.ts` with DOMPurify; all HTML rendering goes through `sanitiseHtml()` utility |
| MR-07 | yfinance 1.2.0 `netIncomeToCommon` currency mismatch for USD-reporting NSE stocks (INFY.NS: 0.37% computed vs 32.68% actual) | MED | HIGH | D3 audit finding — prefer `returnOnEquity` field when available; add currency detection |
| MR-08 | `render_ticker_bar()` uses `st.components.v1.html()` to inject JS into parent iframe DOM | MED | CERTAIN | Replace with CSS `position: fixed` sticky bar in Next.js; no iframe DOM manipulation needed |
| MR-09 | cvxpy not available as Python package on Vercel (needs C extension build) | HIGH | MED | Test `pip install cvxpy==1.8.2` in Vercel build; may need `libopenblas-dev` (add to `runtime.txt` or Dockerfile) |
| MR-10 | Elder Screen 3 not implemented (D2-03) — carry-forward risk: migrated UI inherits "Triple Screen" label without 3rd screen | MED | CERTAIN | Fix D2-03 before migration cutover OR clearly label as "Two-Screen Elder Filter" in migrated UI |
| MR-11 | `veto_applied` flag missing from return dict (D2-04) — Policy 6 disclosure requirement | MED | CERTAIN | Fix D2-04 before migration; migrated React component reads `veto_applied` for `<VetoDisclosure />` |
| MR-12 | WorldMonitor iframe CSP block (ADR-022) — already documented, carries forward unchanged | LOW | CERTAIN | Link button approach carries over to Next.js `<Button asChild><a>` — no change needed |

---

## Cost Analysis

| Item | Streamlit Community Cloud | Vercel Hobby | Vercel Pro |
|---|---|---|---|
| Monthly cost | **Free** | **Free** | $20/month |
| Compute | 1GB shared, unlimited time | Fluid (per request) | Fluid (per request) |
| Function timeout | 30s (Streamlit processes) | 300s (Fluid Compute) | 300s (Fluid Compute) |
| Bandwidth | ~1 GB/month | 100 GB/month | 1 TB/month |
| Cron jobs | None | 2/day | Unlimited |
| Analytics | None | Basic Web Analytics | Full observability |
| Custom domains | Yes | Yes | Yes |
| Team members | 1 | 1 | 10 |

**Cost at 100 DAU (estimate):**
- Vercel Hobby: likely free (within generous limits for a dashboard with server-side cache)
- Vercel Pro: $20/month + compute if portfolio optimizer runs frequently (~$5–15/month estimated)

**Recommendation:** Start on Vercel Hobby. Move to Pro before institutional launch for team access and full observability.

---

## Data Continuity Risks

| Data | Current storage | Migration risk | Mitigation |
|---|---|---|---|
| Forecast history | `st.session_state` (lost per restart) | Already lost on every restart — no regression | Supabase provides improvement |
| Ticker cache | Module-level dict (lost per restart) | Already rebuilt per restart on cold start | Redis provides improvement |
| User preferences (market, ticker) | `st.session_state` (within session) | Lost on page navigate in Next.js too | localStorage or URL params |
| DEV_TOKEN gate | `st.secrets` | Migrates to `process.env.DEV_TOKEN` | No data loss |
| No persistent user accounts | — | No change | — |

---

## Regulatory Continuity Risks

| Risk | Detail | Mitigation |
|---|---|---|
| SEBI disclaimer gaps widen during migration | Each new page component could miss disclaimer | `<SebiDisclaimer />` must be enforced at layout level, not page level; Playwright test each route |
| "Live" / "Real-time" label on yfinance data | yfinance has 15–20 min delay — false claim | Market open check migrates via `isMarketOpen()` server function; `NEXT_PUBLIC_MARKET_OPEN` not used — check server-side |
| Algorithmic label requirement (Policy 2) | AI narrative sections must be labeled as algorithmic | `<AlgorithmicLabel />` component required on all signal narrative sections |
| Social media guidelines (RISK-L04) | `docs/social-media-guidelines.md` applies to Next.js app too | No code change — policy document carries forward |

---

## Rollback Plan

If Vercel migration has issues after DNS cutover:

1. **Hour 1:** Repoint DNS back to Streamlit Community Cloud (TTL should be set to 60s before cutover)
2. **Hour 2:** Streamlit app is still deployed — verify it's still running on `*.streamlit.app` URL
3. **Week 1:** Root-cause the Vercel issue in parallel — rollback buys time
4. **Never:** Delete Streamlit deployment until Vercel has been stable for 30+ days

**Key rollback blocker:** If OPEN-003 is resolved (Supabase), forecast history accumulates in Supabase and is NOT available in Streamlit session_state on rollback. This is acceptable — forecast history was never persistent before.

---

## Migration Prerequisites (must complete before Phase 3)

- [ ] D2-03: Label or implement Elder Screen 3
- [ ] D2-04: Add `veto_applied` flag to `compute_unified_verdict()` return dict
- [ ] D3-01: Fix `_calc_roe()` currency detection for USD-reporting NSE tickers (audit finding)
- [ ] OPEN-022/027/028/029: SEBI disclaimers — fix in Streamlit first, then inherit in React
- [ ] Validate cvxpy 1.8.2 builds successfully on Vercel Python runtime
- [ ] Test Upstash Redis latency from Vercel region (ap-south-1 for India users)
- [ ] Set up Supabase project + run `forecast_history` migration SQL

---

*Generated by Vercel migration research agent (Track C) + main context | 2026-04-13 | session_024*
