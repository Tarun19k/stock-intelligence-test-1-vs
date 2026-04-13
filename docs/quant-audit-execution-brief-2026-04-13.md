# Quant Audit Execution Brief — 2026-04-13 | session_024
# ════════════════════════════════════════════════════════════════════════
# PURPOSE: Self-contained brief for orchestrator agent and future sessions.
# A new Claude instance reading ONLY this file + CLAUDE.md has full context
# to resume execution exactly where it was interrupted.
# STATUS: IN PROGRESS — skills being created, agents not yet dispatched
# ════════════════════════════════════════════════════════════════════════

## Why This Audit

`quant_audit_pending.json` shows `last_full_audit: null` — no quant audit has
ever run. Mandatory before public beta. Triggered manually this session BEFORE
starting the v5.37 sprint. All v5.37 sprint work is blocked until audit completes
or P0 defects are known (so sprint can absorb them).

## Skill Actions Required Before Agent Dispatch

### Fixes (urgent — will cause agent failures if not applied first)

| File | Gap | What to fix |
|---|---|---|
| `.claude/commands/quant-reviewer.md` | Gap 1 | Step 1 says "Read `forecast.py` — `compute_forecast()`, `_holt_winters_damped()`". **Both live in `indicators.py` lines 404 and 488.** `forecast.py` is storage/display only. Change the file reference. |
| `.claude/commands/signal-accuracy-audit.md` | Gap 2 | D5 stability thresholds are stale. Skill says: `σ < 5%→STABLE; 5–15%→MODERATE; >15%→UNSTABLE`. **Actual code `portfolio.py:370-375`: `<8%→STABLE; 8–15%→MODERATE; ≥15%→UNSTABLE`**. Also: OPEN-025 (known boundary issue `>=15` vs `>15`) — pre-note as P1/tracked, not new finding. |
| `.claude/commands/signal-accuracy-audit.md` | Gap 3 | RSI check says "must use `com=13`". **Actual code uses `rolling(14).mean()` — Cutler's RSI (SMA-based), not Wilder's RMA.** Agent needs guidance: classify the deviation, don't invent a verdict. Add note: "If SMA smoothing found, flag as P1 (not P0) and note: Cutler's RSI converges with Wilder's for lookbacks >100 bars; diverges 3-8 points on short windows." |

### Creates (new skills)

| File to create | Purpose |
|---|---|
| `.claude/commands/quant-data-fetcher.md` | D3 live data protocol — safe yfinance calls outside app context |
| `.claude/commands/technical-indicators-math.md` | D1 math reference — canonical formulas, smoothing taxonomy, platform comparison |
| `.claude/commands/portfolio-risk-math.md` | D5 math reference — CVaR, Rockafellar-Uryasev, bootstrap, stability thresholds |
| `.claude/commands/forecasting-calibration-math.md` | D4 math reference — Holt-Winters params, P(gain) calibration, bootstrap validity |
| `.claude/commands/fundamental-analysis-math.md` | D3 math reference — ROE variants, NSE/BSE yfinance conventions, tolerance ranges |

---

## Pre-Flight Gaps Found in Codebase (discovered during this session)

These are real code issues — not audit skill issues. The agent will find these
and should classify them per the severity guidance below.

| Gap | Location | Detail | Expected classification |
|---|---|---|---|
| Gap 3 — RSI smoothing | `indicators.py:35-39` | `rolling(14).mean()` = Cutler's RSI, not Wilder's. TradingView/Zerodha use Wilder's. Diverges 3-8 pts short-window. | P1 |
| Gap 3b — ATR smoothing | `indicators.py:61` | `tr.rolling(14).mean()` = SMA, not Wilder's exponential. Same issue as RSI. | P1 |
| OPEN-025 (pre-known) | `portfolio.py:370-375` | Stability UNSTABLE fires at `>=15` (code) but docstring+UI say `>15`. Off-by-one at boundary. | P1/tracked — already in CLAUDE.md OPEN items, do NOT re-raise as new |
| Bollinger ddof | `indicators.py:50` | `c.rolling(20).std()` uses pandas default `ddof=1` (sample std). TradingView uses `ddof=0` (population std). ~2.6% difference at n=20. | P2 |

### OPEN-025 handling (important)
OPEN-025 is ALREADY in CLAUDE.md open items and GSI_SPRINT.md backlog.
The audit report should reference it as: "OPEN-025 (pre-tracked): threshold
boundary >=15 vs >15 — classified P1, sprint item already exists."
Do NOT add it to GSI_SPRINT.md again.

---

## Known Data Limitations for D3 (Indian Market)

Per CLAUDE.md: `Ticker.info['returnOnEquity']` returns `None` for most Indian stocks.
`_calc_roe()` in `indicators.py:90-111` self-calculates from:
  - `netIncomeToCommon` (info dict)
  - `bookValue` (per-share, info dict)
  - `sharesOutstanding` (info dict)
  - Fallback: `returnOnEquity * 100` if raw fields unavailable
  - Returns `0.0` if neither source yields valid non-zero result

**Expected behaviour for NSE large-caps:** All three raw fields may return `None`,
causing fallback to `returnOnEquity` which is also `None` → function returns `0.0`.
This is a **data gap, not a bug**. Document as: "ROE unavailable via yfinance for
Indian market tickers — D3 validation requires manual cross-check against NSE filings."

**Primary D3 validation tickers:**
- `INFY.NS` — best yfinance coverage among NSE large-caps (tech sector)
- `HDFCBANK.NS` — financial sector, likely partial coverage
- `RELIANCE.NS` — conglomerate, may have partial coverage
- Fallback to one US ticker if needed: `AAPL` — full yfinance coverage, validate formula

**D3 CEO validation required:** After agent fetches ROE values, Tarun cross-checks
against Screener.in for each ticker. Accept ±3pp tolerance (TTM vs fiscal year lag).

---

## Execution Plan — 3 Parallel Tracks

```
PHASE 0 — Context preservation + skill fixes (main context, this session)
  [DONE] Execution brief written
  [ ] GSI_WIP.md → ACTIVE checkpoint
  [ ] Orchestration status.json created
  [ ] Fix quant-reviewer.md (Gap 1)
  [ ] Fix signal-accuracy-audit.md (Gap 2+3)
  [ ] Create quant-data-fetcher.md
  [ ] Create technical-indicators-math.md
  [ ] Create portfolio-risk-math.md
  [ ] Create forecasting-calibration-math.md
  [ ] Create fundamental-analysis-math.md

PHASE 1 — Parallel agent dispatch (after Phase 0 complete)
  TRACK A (main context, ~8k): D3 live data fetch
    - Run Python: fetch yfinance info for INFY.NS, HDFCBANK.NS, RELIANCE.NS
    - Compute _calc_roe() for each
    - Present CEO validation table
    
  TRACK B (worktree agent, Sonnet, ~30k isolated): D1 + D2 + D4-static + D5
    - Reads: indicators.py (670 lines), portfolio.py (462 lines), CLAUDE.md Policy 6
    - Uses: technical-indicators-math, portfolio-risk-math, forecasting-calibration-math
    - Pre-supplied findings: Gap 3 RSI/ATR (classify P1), OPEN-025 (pre-tracked P1)
    - Pre-supplied correct thresholds: STABLE <8%, MODERATE 8-15%, UNSTABLE >=15%
    - Writes: docs/audit-orchestration/domain-findings-auto.md
    - Updates: docs/audit-orchestration/status.json at each domain completion
    
  TRACK C (worktree agent, Sonnet, ~35k isolated): Vercel migration research
    - Reads: app.py, all pages/*.py, market_data.py, portfolio.py, tickers.json
    - Uses: vercel:nextjs, vercel:bootstrap, vercel:vercel-functions, vercel:workflow
    - Produces:
        docs/migration/vercel-migration-plan.md
        docs/migration/component-mapping.md  
        docs/migration/migration-risks.md
    - Key architecture: DurableAgent for yfinance calls, createHook() for CEO gates,
      namespaced streams for observability, RetryableError for rate limits

PHASE 2 — Consolidation (main context, ~8k)
  - Read Track B findings + D3 CEO validation
  - D4: document as deferred (0 forecasts in session_state, OPEN-003 pending)
    Static: α=0.3, β=0.1, φ=0.88 documented
  - Write final report: docs/signal-accuracy-audit-v5.36-2026-04-13.md
  - Raise new sprint items to GSI_SPRINT.md (P0 blocks v5.37; P1 goes to backlog)
  - Run log-learnings skill
  - Update quant_audit_pending.json

PHASE 3 — Sprint gate decision
  - If P0 found: add to v5.37a as blocker before SEBI fixes
  - If P1/P2 only: proceed with v5.37 as planned
  - Open v5.37 sprint manifest
```

---

## Audit Report Schema

Output: `docs/signal-accuracy-audit-v5.36-2026-04-13.md`

```markdown
# Signal Accuracy Audit — v5.36 | 2026-04-13 | session_024
**Auditor:** quant-reviewer
**Triggered by:** Pre-launch mandatory audit (last_full_audit: null)
**Overall status:** [PASS / PASS WITH NOTES / FAIL]

## Domain 1 — Indicator Math: [status]
[table: indicator | expected formula | actual formula | match? | severity]

## Domain 2 — Signal Logic: [status]
[9-combination arbitration matrix vs CLAUDE.md Policy 6]
[veto_applied flag check]

## Domain 3 — Fundamental Data: [PENDING CEO / PASS / FAIL]
[ROE table: ticker | yfinance computed | screener.in actual | delta | within tolerance?]
[P/E staleness observed]
[Ticker mapping sample: 14 tickers across 4 markets]

## Domain 4 — Forecast Calibration: [DEFERRED]
Reason: 0 forecasts in session_state (OPEN-003: cross-session persistence pending)
Static parameters documented: α=0.3, β=0.1, φ=0.88
Milestone: re-run after 90 days of production forecasts

## Domain 5 — Portfolio Math: [status]
[CVaR formula verified against Rockafellar-Uryasev 2000]
[Stability thresholds: STABLE <8%, MODERATE 8-15%, UNSTABLE >=15%]
[OPEN-025 pre-noted: boundary >=15 vs >15 — tracked P1]

## Issues found
[List with P0/P1/P2/tracked — or "None"]

## Sprint items raised
[New items only — OPEN-025 excluded as pre-existing]
```

---

## Vercel Migration Agent Brief

**Model:** Claude Sonnet 4.6  
**Mode:** Research and planning only — NO code writes  
**Reads:** Full app structure  
**Uses:** vercel:nextjs, vercel:bootstrap, vercel:vercel-functions, vercel:workflow

### Key architectural decisions to recommend

1. **Python backend stays Python** — Vercel Fluid Compute supports Python 3.14.
   yfinance, pandas, numpy, cvxpy all run as Vercel Functions (not Edge).
   Do NOT recommend porting data layer to TypeScript.

2. **Frontend: Next.js App Router** — Replace Streamlit pages with React components.
   Use awesome-design-md Vercel design system for visual consistency.

3. **DurableAgent for long-running ops:**
   - `get_batch_data()` → workflow step with RetryableError on 429
   - `optimise_mean_cvar()` → workflow step (compute-intensive, may exceed 300s)
   - `compute_forecast()` → workflow step (2000 simulations)
   - D3-style CEO gates → `createHook()` approval flow

4. **Namespaced streams for observability:**
   - `getWritable({ namespace: "market-data:fetch" })` — replaces market_data.py logging
   - `getWritable({ namespace: "portfolio:optimize" })` — replaces in-app optimization logs
   - `getWritable({ namespace: "signals:compute" })` — live signal computation stream

5. **session_state replacement** — `createHook()` + database (Vercel Marketplace:
   Supabase) replaces st.session_state for forecast_history (resolves OPEN-003)

6. **Rate limiting** — Token bucket in market_data.py → `RetryableError("Rate limited",
   { retryAfter: "0.4s" })` in workflow steps. Eliminates `_global_throttle()`.

7. **1GB RAM constraint** — Fluid Compute functions scale independently per request.
   Portfolio optimizer (cvxpy + numpy) gets its own function with 1GB limit.

### Artifacts schema

`docs/migration/vercel-migration-plan.md`:
- Phase 1: Scaffold (Next.js app, Python API routes, Vercel config)
- Phase 2: Data layer (market_data.py → Vercel Functions + Workflow steps)
- Phase 3: UI migration (Streamlit pages → React components, page-by-page)
- Phase 4: Cutover (DNS, monitoring, Streamlit sunset)

`docs/migration/component-mapping.md`:
- Table: every `st.*` call → Next.js/React equivalent
- Every `@st.fragment` → React Suspense or SWR polling equivalent
- Every `@st.cache_data` → Next.js unstable_cache or Redis equivalent

`docs/migration/migration-risks.md`:
- cvxpy on serverless (solver compatibility, cold start time)
- yfinance rate limits under concurrent Vercel requests
- session_state persistence gap (OPEN-003 resolution path)
- SEBI disclaimer continuity across all migrated pages
- Streamlit Community Cloud free tier → Vercel Hobby tier cost comparison

---

## Orchestration Observability Architecture

Status file: `docs/audit-orchestration/status.json`
Updated by each agent at phase boundaries.

```json
{
  "audit_session": "session_024",
  "date": "2026-04-13",
  "overall_status": "IN_PROGRESS",
  "phases": {
    "phase_0_skills": { "status": "IN_PROGRESS", "completed": [], "pending": [] },
    "phase_1_d3_main": { "status": "PENDING", "findings": null },
    "phase_1_auto_agent": { "status": "PENDING", "findings_file": null },
    "phase_1_vercel_agent": { "status": "PENDING", "artifacts": [] },
    "phase_2_report": { "status": "PENDING", "report_file": null },
    "phase_3_sprint_gate": { "status": "PENDING", "decision": null }
  },
  "sprint_items_raised": [],
  "ceo_validation_required": true,
  "d3_ceo_gate": {
    "tickers": ["INFY.NS", "HDFCBANK.NS", "RELIANCE.NS"],
    "status": "PENDING",
    "values_computed": false
  }
}
```

---

## Token Budget

| Track | Model | Est. tokens | Notes |
|---|---|---|---|
| Phase 0 skills | Sonnet (main ctx) | ~15k | 9 file writes, all small |
| Phase 1 D3 main ctx | Sonnet (main ctx) | ~8k | Python calls + table |
| Phase 1 auto agent | Sonnet (worktree) | ~30k | Isolated — no main ctx cost |
| Phase 1 Vercel agent | Sonnet (worktree) | ~35k | Isolated — no main ctx cost |
| Phase 2 consolidation | Sonnet (main ctx) | ~8k | Read agent output + write report |
| **Total main context** | | **~31k** | |
| **Total agents (isolated)** | | **~65k** | |
| **Grand total** | | **~96k** | |

---

## Resume Instructions

If context compacted mid-execution:
1. Read this file first
2. Read `docs/audit-orchestration/status.json` to see which phases completed
3. Read `GSI_WIP.md` CHECKPOINT block for exact resume point
4. Do NOT re-run completed phases
5. Skills in `.claude/commands/` — check if they exist before creating
6. Agents — check `docs/audit-orchestration/domain-findings-auto.md` before re-dispatching
