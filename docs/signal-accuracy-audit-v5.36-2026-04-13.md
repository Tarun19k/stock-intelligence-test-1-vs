# Signal Accuracy Audit — v5.36 | 2026-04-13 | session_024
**Auditor:** quant-reviewer (worktree agent Track B + main context)
**Triggered by:** Pre-launch mandatory audit (`last_full_audit: null`)
**Overall status:** ⚠️ PASS WITH NOTES

No P0 blockers found. v5.37 sprint can proceed as planned.
Ten new findings: 2× P1, 6× P2, 2× P3. All backlog items.

---

## Domain 1 — Indicator Math
**Status: PASS WITH NOTES**

| Indicator | Expected | Actual (code) | Match | Severity | Line # |
|---|---|---|---|---|---|
| RSI(14) | Wilder's RMA `ewm(com=13)` | Cutler's SMA `rolling(14).mean()` | DEVIATION | **P1** | 36–38 |
| EMA(20/50/200) | `ewm(span=N, adjust=False)` α=2/(N+1) | Exactly as expected | MATCH | OK | 25–30 |
| MACD | EMA(12)−EMA(26), EMA(9) signal, histogram | Exactly as expected | MATCH | OK | 42–46 |
| Bollinger Bands | ±2σ, ddof=0 (TradingView std) | `rolling(20).std()` ddof=1 (pandas default) | DEVIATION | **P2** | 49–53 |
| ATR(14) | Wilder's RMA | `tr.rolling(14).mean()` — SMA | DEVIATION | **P1** | 56–61 |
| ADX(14) | Correct +DM/−DM, SMA(14) smoothing | Correct formula and smoothing | MATCH | OK | 63–72 |
| Stochastic %K | `(C−Low14)/(High14−Low14)×100` | Exactly as expected | MATCH | OK | 74–77 |
| OBV | Cumulative volume-signed direction | `np.sign(c.diff())` approach | MATCH | OK | 81–82 |

**D1 notes:**
- RSI divergence: 3–8 points on stocks with <100 bars; converges to <0.5 points at >100 bars. Users on Zerodha/TradingView will see different values on new listings.
- ATR divergence: 5–15% on volatile stocks at short windows; converges at >100 bars.
- Bollinger ddof difference: ~2.6% on band width at n=20. Scale-invariant — same direction, slightly wider bands vs TradingView.

---

## Domain 2 — Signal Logic
**Status: PASS WITH NOTES**

### Weinstein Stage Classification
- MA period: `close.rolling(150).mean()` = 150 daily bars ≈ 30 weeks. **CORRECT.**
- MA slope: computed over last **10 bars** (not documented 4 weeks = 20 bars). See D2-01.
- All 4 stage conditions well-defined. ✓
- `near_ma` variable computed at line 259 but never referenced in any branch. See D2-02.

### Elder Triple Screen
- Screen 1 (weekly tide): Weekly resample via `resample('W').last()`. EMA(13)/EMA(26) on weekly data. Rising MACD histogram = bullish tide. **CORRECT.**
- Screen 2 (daily momentum): Daily RSI threshold 40 (classic Wilder: 30). Wider entry window — practitioner variation, acceptable.
- Screen 3 (entry trigger): **NOT IMPLEMENTED.** The function runs only 2 of 3 Elder screens. UI currently labels this "Elder Triple Screen" — inaccurate. See D2-03.

### Signal Arbitration Matrix (vs CLAUDE.md Policy 6)
Policy 6: "Documented hierarchy: Weinstein > Elder in conflict; veto must be visibly disclosed in UI"

| Stage | Elder BUY | Elder WATCH | Elder SELL |
|---|---|---|---|
| Stage 1 | Capped WATCH (if score≥58) | Capped WATCH | Capped WATCH |
| Stage 2 | Score-driven: STRONG BUY / BUY / WATCH | Score-driven | BUY→WATCH cap; else score-driven |
| Stage 3 | Capped WATCH (if score≥58) | Capped WATCH | Capped WATCH |
| Stage 4 | **AVOID — hard veto** ✓ | **AVOID** ✓ | **AVOID** ✓ |

**Verdict:** Stage 4 veto fires correctly in all combinations. Policy 6 hierarchy is enforced. ✓

### veto_applied Flag — MISSING (D2-04)
`compute_unified_verdict()` return dict does NOT include a `veto_applied` boolean key.
Policy 6 requires veto disclosure in UI. The veto fires correctly but the explicit boolean for UI
disclosure is absent. See D2-04. (Note: `conflicts` list partially serves this purpose but is not
the Boolean flag used for disclosure gating.)

---

## Domain 3 — Fundamental Data
**Status: D3-01 CONFIRMED (INFY) | PASS (HDFCBANK, RELIANCE)**
**CEO validation:** 2026-04-13 | Source: Screener.in

### ROE Validation Table — CEO Cross-Check Complete

| Ticker | Company | ROE (calculated) | ROE (field) | Screener.in actual | Field delta | Field pass? | Calc delta | Calc pass? |
|---|---|---|---|---|---|---|---|---|
| INFY.NS | Infosys Ltd | **0.37%** | 32.68% | **30.3%** | 2.38pp | ✅ ±3pp | **29.93pp** | ❌ D3-01 CONFIRMED |
| HDFCBANK.NS | HDFC Bank Ltd | **13.18%** | 14.02% | **14.4%** | 0.38pp | ✅ ±3pp | 1.22pp | ✅ PASS |
| RELIANCE.NS | Reliance Industries | **9.49%** | None | **8.40%** | N/A | N/A | 1.09pp | ✅ PASS |

### P/E and P/B Spot Check (as of 2026-04-13)

| Ticker | P/E (trailing) | P/B | Market Cap (INR) | Price (INR) |
|---|---|---|---|---|
| INFY.NS | 17.92 | 5.97 | ₹5.15T | ₹1,273.60 |
| HDFCBANK.NS | 17.72 | 2.16 | ₹12.22T | ₹794.00 |
| RELIANCE.NS | 21.36 | 2.02 | ₹17.76T | ₹1,312.20 |

### Field Availability (India NSE)

| Field | INFY.NS | HDFCBANK.NS | RELIANCE.NS |
|---|---|---|---|
| netIncomeToCommon | ✅ 3.2B | ✅ 745.1B | ✅ 832.1B |
| bookValue (per share) | ✅ 213.33 | ✅ 367.24 | ✅ 648.12 |
| sharesOutstanding | ✅ 4.05B | ✅ 15.4B | ✅ 13.5B |
| returnOnEquity | ✅ 0.3268 (32.68%) | ✅ 0.1402 (14.02%) | ❌ None |
| trailingPE | ✅ 17.92 | ✅ 17.72 | ✅ 21.36 |
| marketCap | ✅ | ✅ | ✅ |
| revenueGrowth | ✅ 3.2% | ✅ 26.4% | ✅ 10.4% |

### D3-01 Finding — INFY.NS Currency Mismatch (P1)

**Calculated ROE = 0.37%** while `returnOnEquity` field = **32.68%** — a 32.3pp gap far beyond ±3pp tolerance.

Root cause hypothesis: Infosys files financial results in USD (global company with USD reporting). `netIncomeToCommon` = ~$3.2B USD, but `bookValue` (₹213.33/share) × `sharesOutstanding` (4.05B) are in INR. The formula computes USD income / INR equity → wrong result.

Impact in production: `_calc_roe()` returns 0.37% for INFY.NS (all three raw fields are non-None, so the fallback to `returnOnEquity` is never reached). `signal_score()` receives 0.37% ROE for Infosys — effectively treating it as a near-zero-return company when actual ROE is ~32%.

**CEO validation required:** Open screener.in/company/INFY, find "Return on Equity" in the 10-year table. If Screener shows ~30–35%, D3-01 is confirmed as a real production defect.

### CEO Cross-Check Instructions

1. **INFY.NS** → screener.in/company/INFY → "Return on Equity" (most recent annual)
   - Compare to: calculated **0.37%** and returnOnEquity **32.68%**
   - If Screener shows ~30–35%: D3-01 confirmed P1. `_calc_roe()` uses wrong value for INFY.NS.

2. **HDFCBANK.NS** → screener.in/company/HDFCBANK → "Return on Equity" (most recent annual)
   - Compare to: calculated **13.18%**
   - Tolerance: ±3pp vs Screener fiscal year value

3. **RELIANCE.NS** → screener.in/company/RELIANCE → "Return on Equity" (most recent annual)
   - Compare to: calculated **9.49%**
   - Tolerance: ±3pp vs Screener fiscal year value

---

## Domain 4 — Forecast Calibration
**Status: PASS (static params) | DEFERRED (calibration)**

### Holt-Winters Parameters (indicators.py lines 488–491)

| Parameter | Value | Threshold | Status |
|---|---|---|---|
| α (level smoothing) | 0.3 | Must be < 0.5 | ✅ OK |
| β (trend smoothing) | 0.1 | Must be < 0.3 | ✅ OK |
| φ (damping factor) | 0.88 | Must be 0.8–0.99 | ✅ OK |

All Holt-Winters parameters within safe operating range. No overfit/runaway risk.

### Bootstrap Methodology Checks

| Check | Expected | Found | Status |
|---|---|---|---|
| Log returns | `np.log()` or `np.diff(np.log(...))` | `np.diff(np.log(close.values))` (line 442) | ✅ PASS |
| Min history guard | ≥30 bars | `len(close) < 30` → return empty (line 438) | ✅ PASS |
| Reproducibility | seed=42 | `np.random.default_rng(seed=42)` (line 455) | ✅ PASS |
| Momentum blend decay | 1.0 at day 1 → 0.0 at day 63 | `max(0.0, 1.0 - horizon/63.0)` | ✅ PASS |
| Blend at 21 days | ~80% (documented) | **66.7%** (actual formula) | ⚠️ D4-01 (comment mismatch) |
| Neutral zone 45–55% | Must suppress directional signal | **NOT IMPLEMENTED** | OPEN-009 (pre-tracked) |

### D4 Calibration: DEFERRED
`st.session_state["forecast_history"]` always starts empty on cold session (OPEN-003: no Supabase persistence). Requires ≥20 resolved forecasts for bucket analysis. Set milestone: re-run after OPEN-003 implemented and 90+ days of production forecasts accumulated.

---

## Domain 5 — Portfolio Math
**Status: PASS WITH NOTES**

### CVaR Formula (Rockafellar-Uryasev 2000)
Verified at portfolio.py lines 239–261:
- `CVAR_ALPHA = 0.95` ✅
- `zeta = cp.Variable()` — VaR auxiliary ✅
- `z = cp.Variable(n_scenarios, nonneg=True)` — exceedance variables ✅
- `cvar_val = zeta + (1.0 / (n_scenarios * (1.0 - CVAR_ALPHA))) * cp.sum(z)` ✅
- Constraint: `z >= -port_ret - zeta` ✅

Formula matches Rockafellar & Uryasev (2000) exactly. **CVaR math: PASS.**

### Key Constants

| Constant | Expected | Actual | Status |
|---|---|---|---|
| CVAR_ALPHA | 0.95 | **0.95** | ✅ OK |
| MAX_WEIGHT | ~0.40 | **0.35** | ✅ Conservative — not a defect |
| EXP_DECAY | ~0.94 | **0.97** | ⚠️ D5-01 — slower decay |

### Stability Score Thresholds (lines 370–375)
```
max_std < 8    → STABLE
8 ≤ max_std < 15 → MODERATE
max_std ≥ 15   → UNSTABLE
```
Thresholds match pre-verified values. ✅
OPEN-025 (pre-tracked P1): ≥15 boundary vs >15 in docstring/UI — not re-raised.

### Efficient Frontier
Returns 12 points with correct fields (lambda, weights, exp_ret, cvar, sharpe). No monotonicity enforcement guard. See D5-02.

---

## Issues Found

| ID | Domain | Description | Severity | Sprint action |
|---|---|---|---|---|
| D1-01 | D1 | RSI: Cutler's SMA not Wilder's RMA — 3–8pt divergence at <100 bars | **P1** | Add to GSI_SPRINT.md backlog |
| D1-02 | D1 | ATR: SMA smoothing not Wilder's RMA — 5–15% divergence on volatile stocks | **P1** | Add to GSI_SPRINT.md backlog |
| D3-01 | D3 | INFY.NS: `_calc_roe()` returns 0.37% (calculated) vs 32.68% (returnOnEquity field) — likely USD/INR currency mismatch | **P1** | CEO validate first; if confirmed, fix `_calc_roe()` |
| D1-03 | D1 | Bollinger: ddof=1 vs ddof=0 — ~2.6% band width difference vs TradingView | P2 | Backlog |
| D2-03 | D2 | Elder Screen 3 (entry trigger) not implemented — UI incorrectly labels as "Triple Screen" | P2 | Label fix or Screen 3 implementation |
| D2-04 | D2 | `veto_applied` boolean key absent from `compute_unified_verdict()` return dict — Policy 6 disclosure | P2 | Add `veto_applied` key to return dict |
| D5-01 | D5 | `EXP_DECAY=0.97` vs expected 0.94 — half-life 23d vs 11d, older data weighted more | P2 | Backlog — verify design intent |
| D5-02 | D5 | Efficient frontier: no monotonicity guard — solver instability not detected | P2 | Backlog — add assertion |
| D2-01 | D2 | Weinstein slope window: 10 bars (2 weeks) vs documented 4 weeks | P3 | Backlog |
| D2-02 | D2 | `near_ma` variable at line 259: computed but never used — dead code | P3 | Backlog (cleanup) |
| D4-01 | D4 | Blend comment says ~80% at 21d; formula yields 66.7% — comment mismatch | P3 | Fix comment only |

**Pre-tracked (not re-raised):**
- OPEN-009: Neutral zone 45–55% — tracked, in sprint backlog
- OPEN-025: Stability ≥15 vs >15 boundary — tracked P1

---

## Sprint Items Raised (NEW — from this audit)

Items to add to `GSI_SPRINT.md` backlog (all P1/P2):

| Sprint ID | Description | Severity | Domain |
|---|---|---|---|
| QA-D1-01 | Fix RSI: switch from Cutler's rolling SMA to Wilder's RMA (`ewm(com=13)`) | P1 | D1 |
| QA-D1-02 | Fix ATR: switch from SMA(14) to Wilder's RMA smoothing | P1 | D1 |
| QA-D3-01 | Fix `_calc_roe()`: detect USD/INR currency mismatch; prefer `returnOnEquity` when calculated value diverges >10pp | P1 | D3 (pending CEO confirmation) |
| QA-D2-03 | Fix UI label: "Elder Triple Screen" → "Elder Two-Screen Filter" OR implement Screen 3 | P2 | D2 |
| QA-D2-04 | Add `veto_applied: bool` key to `compute_unified_verdict()` return dict | P2 | D2 |
| QA-D5-01 | Verify EXP_DECAY=0.97 design intent; document or adjust to 0.94 | P2 | D5 |
| QA-D5-02 | Add efficient frontier monotonicity assertion | P2 | D5 |
| QA-D1-03 | Bollinger ddof: document deviation from TradingView in UI tooltip | P2 | D1 |

---

## Recommended Fix: Immediate (before v5.37 ship)

None required — no P0 blockers. All findings are P1/P2/P3.

**However, QA-D3-01 depends on CEO validation:** if INFY.NS ROE anomaly is confirmed against Screener.in, the fix should be absorbed into v5.37a (SEBI sprint) alongside OPEN-022/027/028/029.

---

*Audit complete: 2026-04-13 | session_024*
*Domains audited: D1 ✅ | D2 ✅ | D3 ⏳ CEO pending | D4 ✅ (static) + DEFERRED (calibration) | D5 ✅*
*Vercel migration research: see docs/migration/ (3 artifacts)*
