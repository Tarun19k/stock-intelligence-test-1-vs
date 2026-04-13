# Quant Audit — Automated Domains | 2026-04-13 | session_024

**Auditor:** worktree agent (Sonnet 4.6)
**Scope:** D1 (Indicator Math) · D2 (Signal Logic) · D4-static (Forecast params only) · D5 (Portfolio Math)
**D3:** Handled in main context (CEO validation required)
**D4-calibration:** DEFERRED — requires live forecast history (see D4 section)

---

## Domain 1 — Indicator Math
**Status: PASS WITH NOTES**

| Indicator | Expected | Actual (code) | Match | Severity | Line # |
|---|---|---|---|---|---|
| RSI(14) | Wilder's RMA `ewm(com=13)` | Cutler's SMA `rolling(14).mean()` on gains/losses | DEVIATION (pre-known) | P1 | 36–38 |
| EMA(12/26/9) | `ewm(span=N, adjust=False)` | Exactly as expected | MATCH | OK | 42–46 |
| MACD | EMA(12)−EMA(26), EMA(9) signal, histogram | Exactly as expected | MATCH | OK | 42–46 |
| Bollinger Bands | ±2σ, ddof=0 (TradingView convention) | `rolling(20).std()` — no explicit ddof → ddof=1 (pandas default) | DEVIATION (pre-known) | P2 | 49–53 |
| ATR(14) | Wilder's RMA | `tr.rolling(14).mean()` — SMA smoothing | DEVIATION (pre-known) | P1 | 56–61 |
| ADX(14) | +DM/−DM correct; SMA(14) for smoothing | Correct +DM/−DM formula; `rolling(14).mean()` for smoothing | MATCH | OK | 63–72 |
| Stochastic %K | `(C−Low14)/(High14−Low14)×100` | Exactly as expected | MATCH | OK | 74–77 |
| OBV | `np.sign(c.diff())×v` cumsum | Exactly as expected via `np.sign(c.diff())` | MATCH | OK | 81–82 |

**Notes:**
- All three pre-supplied deviations confirmed (RSI P1, ATR P1, Bollinger P2)
- No unexpected deviations beyond pre-supplied findings
- EMA, MACD, ADX, Stochastic, OBV all match reference formulas exactly

---

## Domain 2 — Signal Logic
**Status: PASS WITH NOTES**

### Weinstein Stage Logic (lines 219–298)
- MA period: `close.rolling(150).mean()` — 150 days ≈ 30 weeks. **CORRECT.**
- MA slope: computed over last **10 bars** (not 20 bars / 4 weeks as referenced). See D2-01.
- All 4 stage conditions (1/2/3/4) have well-defined entry criteria. ✓
- Stage 4 veto fires correctly — AVOID output enforced. ✓
- `near_ma` variable computed at line 259 but never used in any branch — dead code. See D2-02.

### Elder Triple Screen (lines 309–393)
- Screen 1 (weekly trend): Correctly resamples to weekly via `resample('W').last()`. Uses EMA(13)/EMA(26) on weekly data. Signal = rising MACD histogram. **CORRECT.**
- Screen 2 (daily momentum): Daily RSI threshold 40 (vs classic 30 — wider entry window, practitioner variation). `suppress_buy` correctly set True for bearish tide verdicts.
- Screen 3 (entry trigger): **NOT IMPLEMENTED** — function only implements 2 of 3 Elder screens. UI currently labels this as "Elder Triple Screen" which is inaccurate. See D2-03.

### Unified Verdict Arbitration Matrix
| Stage | Elder BUY | Elder WATCH | Elder SELL |
|---|---|---|---|
| Stage 1 | Capped at WATCH if score≥58 | Capped at WATCH if score≥58 | Capped at WATCH if score≥58 |
| Stage 2 | Score-driven: STRONG BUY / BUY / WATCH / CAUTION | Score-driven | If BUY in raw_signal → WATCH; else score-driven |
| Stage 3 | Capped at WATCH if score≥58 | Capped at WATCH if score≥58 | Capped at WATCH if score≥58 |
| Stage 4 | **AVOID — hard veto, conflict logged** | AVOID | AVOID |

**Policy 6 compliance:** Stage 4 veto fires correctly in all combinations. Weinstein > Elder hierarchy enforced. ✓

### veto_applied Flag — MISSING (D2-04)
The `compute_unified_verdict()` return dict keys are:
`final_signal`, `final_color`, `conflicts`, `verdict_reason`, `horizon_note`, `raw_score`, `stage_label`, `elder_verdict`, `is_debt`

**`veto_applied` boolean key is absent.** Policy 6 requires veto disclosure in UI. The veto logic is correct but the flag for explicit UI disclosure is missing. The `conflicts` list may partially serve this role but is not the explicit boolean key. See D2-04.

---

## Domain 4 — Forecast (Static Parameters Only)
**Status: PASS (static params) | DEFERRED (calibration)**

### Holt-Winters Parameters (`indicators.py` lines 488–491)
| Parameter | Expected | Actual | Status |
|---|---|---|---|
| α (level smoothing) | 0.3 | **0.3** | OK — moderate lag, not overreactive |
| β (trend smoothing) | 0.1 | **0.1** | OK — slow trend, prevents whipsaw |
| φ (damping factor) | 0.88 | **0.88** | OK — mild damping, reasonable for retail |

All three parameters within acceptable ranges (α<0.5 ✓, β<0.3 ✓, φ>0.8 ✓, φ<1.0 ✓)

### Bootstrap Forecast Methodology (`indicators.py` lines 438–465)
- Log returns: `np.diff(np.log(close.values))` — **YES** (line 442). Correct.
- Min history guard: `len(close) < 30` → return empty — **YES** (line 438). Correct.
- Seed=42: `np.random.default_rng(seed=42)` — **YES** (line 455). Determinism confirmed.
- Momentum blend: `blend = max(0.0, 1.0 - horizon_days / 63.0)`. At 21d: **blend = 0.667 (66.7%)**. Code comment says "~80%" — inaccurate. See D4-01.
- Neutral zone 45–55%: **NOT IMPLEMENTED** in `compute_unified_verdict()`. Only thresholds `< 40` and `> 65` found. OPEN-009 (pre-tracked). Not re-raised.

### D4 Calibration Status
**DEFERRED** — requires ≥20 resolved forecasts from `st.session_state["forecast_history"]`. Cold session always has 0 entries (OPEN-003: no Supabase persistence implemented). Re-run after OPEN-003 implemented. This is expected behaviour, not a defect.

---

## Domain 5 — Portfolio Math
**Status: PASS WITH NOTES**

### CVaR Formula Verification (lines 239–261)
- `CVAR_ALPHA` = **0.95** (line 50). Matches expected. ✓
- Rockafellar-Uryasev LP reformulation: **VERIFIED CORRECT**
  - `zeta = cp.Variable()` — VaR auxiliary variable ✓
  - `z = cp.Variable(n_scenarios, nonneg=True)` — CVaR exceedance variables ✓
  - `cvar_val = zeta + (1.0 / (n_scenarios * (1.0 - CVAR_ALPHA))) * cp.sum(z)` ✓
  - Constraint: `z >= -port_ret - zeta` ✓
  - Formula matches Rockafellar & Uryasev (2000) exactly.

### Key Constants Found
| Constant | Expected | Actual | Status |
|---|---|---|---|
| `CVAR_ALPHA` | 0.95 | **0.95** | OK |
| `MAX_WEIGHT` | ~0.40 | **0.35** | Conservative — not a defect |
| `EXP_DECAY` | ~0.94 | **0.97** | Slower decay — see D5-01 |
| `MIN_STOCKS` | 2–3 | Need to verify | — |

### Bootstrap Log Returns
- Formula: `np.diff(np.log(cl.values))` (line 118). CORRECT.
- Exponential weights: `weights /= weights.sum()` normalisation present (line 173). CORRECT.
- EXP_DECAY=0.97: half-life ≈ 23 days (vs 11 days at 0.94). Weights older data more heavily. See D5-01.

### Stability Score Thresholds (exact code, lines 370–375)
```python
max_std = max(weight_std.values()) if weight_std else 0
if max_std < 8:
    score = "STABLE"
elif max_std < 15:
    score = "MODERATE"
else:
    score = "UNSTABLE"
```
Matches pre-verified values exactly. ✓

**OPEN-025 (pre-tracked P1):** UNSTABLE fires at `≥15` (code) vs `>15` (docstring/UI). Existing sprint item — not re-raised.

### Efficient Frontier (lines ~184+)
- Returns 12 points (`n_points=12`). ✓
- Each point has: `lambda`, `weights`, `exp_ret`, `cvar`, `sharpe`. Correct fields. ✓
- No monotonicity enforcement (assert that higher CVaR → higher exp_ret). See D5-02.

---

## Issues Found

| ID | Domain | Description | Severity | Sprint action |
|---|---|---|---|---|
| D1-01 | D1 | RSI uses Cutler's SMA not Wilder's RMA — diverges 3–8pts on stocks with <100 bars | P1 | Add to GSI_SPRINT.md backlog |
| D1-02 | D1 | ATR uses SMA(14) not Wilder's RMA — same divergence pattern as RSI | P1 | Add to GSI_SPRINT.md backlog |
| D1-03 | D1 | Bollinger ddof=1 vs ddof=0 — ~2.6% diff in band width vs TradingView | P2 | Backlog |
| D2-01 | D2 | Weinstein slope window 10 bars (2 weeks) vs documented 4 weeks | P3 | Backlog |
| D2-02 | D2 | `near_ma` variable at line 259 computed but never used — dead code | P3 | Backlog (cleanup) |
| D2-03 | D2 | Elder Screen 3 (entry trigger) not implemented — only 2/3 screens active | P2 | Add UI label "Double Screen" or implement Screen 3 |
| D2-04 | D2 | `veto_applied` boolean key absent from `compute_unified_verdict()` return dict — Policy 6 requires veto disclosure | P2 | Add `veto_applied` key to return dict |
| D4-01 | D4 | Momentum blend comment says ~80% at 21d; actual formula gives 66.7% — doc mismatch | P3 | Fix comment only |
| D5-01 | D5 | `EXP_DECAY=0.97` vs expected ~0.94 — half-life 23 days vs 11 days, older data weighted more | P2 | Backlog — verify intent with portfolio designer |
| D5-02 | D5 | Efficient frontier has no monotonicity guard — solver instability could produce backwards-bending section without detection | P2 | Backlog — add assertion |

**P0 findings: NONE. No sprint blocker. v5.37 can proceed as planned.**

---

## Pre-Tracked Items (referenced, not re-raised)
- **OPEN-009**: Neutral zone 45–55% not implemented in forecast UI — pre-tracked, in CLAUDE.md OPEN items
- **OPEN-025**: Stability UNSTABLE boundary >=15 vs >15 — pre-tracked P1, existing sprint item

---

*Generated by worktree agent (Track B) | 2026-04-13 | session_024*
*Token usage: ~51k | Duration: ~175s*
