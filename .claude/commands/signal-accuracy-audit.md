---
name: signal-accuracy-audit
description: Run a financial data accuracy audit across indicators, signals, forecasts, fundamentals, and portfolio math. Use when verifying that computed values (RSI, Weinstein stage, P(gain), ROE, CVaR) are mathematically correct and empirically meaningful — not just that they render.
---

# Signal & Data Accuracy Audit — GSI Dashboard

## When to use
- Before any public release or beta launch
- After any change to `indicators.py`, `forecast.py`, `portfolio.py`, or `market_data.py`
- When a user reports a signal that looks wrong ("RELIANCE shows BUY but it's down 30% this month")
- Periodically (once per major version) as a calibration health check

## What this audit does NOT replace
- `regression.py` — structural/import checks, still required
- `qa-brief` — UI rendering checks, still required
- `compliance_check.py` — pre-push gate, still required
This audit checks *mathematical and empirical correctness*, not structure or rendering.

---

## Domain 1 — Indicator Math Validation

**File:** `indicators.py:compute_indicators()`

**Method:** Pick 2–3 tickers with well-known historical data (e.g. RELIANCE.NS, INFY.NS). Fetch OHLCV via `market_data.get_price_data()`. Run `compute_indicators(df)`. Cross-check each value against a reference calculation.

### Checks

| Indicator | Formula to verify | Reference |
|---|---|---|
| EMA(20) | Exponential: α=2/(20+1); seed = SMA(20) first bar | pandas `ewm(span=20, adjust=False)` |
| EMA(50) | Same method, span=50 | Same |
| EMA(200) | Same method, span=200 | Same |
| RSI(14) | Reference: Wilder's RMA: avg_gain = (prev_avg×13 + gain)/14, `com=13`. **GSI uses `rolling(14).mean()` (Cutler's RSI / SMA-based) — this is a known deviation.** Classify as P1 if found: Cutler's converges with Wilder's for lookbacks >100 bars; diverges 3–8 pts on short windows. Do NOT classify as P0. | See `technical-indicators-math` for full taxonomy |
| MACD | EMA(12) − EMA(26); signal = EMA(9) of MACD; hist = MACD − signal | Standard parameters — pandas `ewm(span=N, adjust=False)` |
| Bollinger Upper/Lower | SMA(20) ± 2 × rolling std(20) | **ddof note:** GSI uses `c.rolling(20).std()` = pandas default `ddof=1`. TradingView uses `ddof=0`. ~2.6% divergence at n=20 — classify as P2 if found. |
| ATR(14) | True Range = max(H−L, \|H−Cprev\|, \|L−Cprev\|); Wilder's 14-period smoothing. **GSI uses `tr.rolling(14).mean()` (SMA) — same Cutler's deviation as RSI.** | Classify as P1 if SMA found. Same convergence argument applies. |

**Pass criterion:** All values within ±0.1% of reference calculation on a 100-bar window.
**Classification guidance:** P0 = formula wrong and diverges materially at any window. P1 = known smoothing deviation, converges long-term. P2 = minor convention difference (ddof, rounding).

---

## Domain 2 — Signal Logic Audit

**Files:** `indicators.py:compute_weinstein_stage()`, `compute_elder_screens()`, `compute_unified_verdict()`

### Weinstein Stage checks

| Stage | Criteria to verify | Common error |
|---|---|---|
| Stage 1 (base) | Price flat/rising near 30-wk MA; MA flattening | MA period: weekly close, 30 bars |
| Stage 2 (advance) | Price above rising 30-wk MA; volume expanding | "Rising" = slope > 0 over last 4 weeks |
| Stage 3 (top) | Price stalling near flat/turning MA | |
| Stage 4 (decline) | Price below falling 30-wk MA | |

**Spot check:** Take 5 well-known stocks in different trend phases. Manually assess stage. Compare to `compute_weinstein_stage()` output. Document any mismatches.

### Elder Triple Screen checks
- Screen 1 (weekly trend): weekly MACD histogram direction — verify it uses *weekly* resampled data, not daily
- Screen 2 (daily momentum): daily RSI or Stochastic — verify period and overbought/oversold thresholds
- Screen 3 (entry): verify entry signal conditions are consistent with Elder's documented method

### Unified verdict arbitration
- Weinstein Stage 4 must veto any Elder BUY — verify `compute_unified_verdict()` enforces this
- Weinstein Stage 2 + Elder BUY = BUY; Stage 2 + Elder SELL = WATCH (Weinstein wins positive)
- When veto fires: verify `veto_applied` flag is set in returned dict (used by UI disclosure, DO NOT UNDO Rule 12)

**Pass criterion:** Arbitration matrix matches CLAUDE.md Governance Policy 6 in all 9 combinations.

---

## Domain 3 — Fundamental Data Accuracy

**File:** `indicators.py:_calc_roe()`, `signal_score()`

### ROE self-calculation (D-02)
1. Pick RELIANCE.NS. Fetch `info` via `market_data.get_ticker_info()`.
2. Run `_calc_roe(info)`. Note the value.
3. Cross-check against latest annual report ROE (NSE filings / Screener.in / Moneycontrol).
4. Acceptable tolerance: ±3 percentage points (yfinance trailing 12M vs. fiscal year difference expected).
5. If yfinance `returnOnEquity` field is present and non-null, `_calc_roe()` should fall back to it — verify fallback logic path.

### P/E, Market Cap spot-check
- Fetch 5 large-cap tickers. Compare yfinance `trailingPE`, `marketCap` to NSE/BSE website values.
- Note staleness: yfinance data may lag 15 min (intraday) to 1 day (fundamentals). Document observed lag.

### Ticker mapping integrity
- Read `tickers.json`. For each market, sample 5 tickers.
- Verify: (a) ticker string resolves in yfinance without error, (b) company name matches, (c) sector classification is correct.
- Flag any delisted tickers (yfinance returns empty DataFrame).

---

## Domain 4 — Forecast Calibration

**File:** `forecast.py`, `indicators.py:compute_forecast()`

### P(gain) probability check
1. Retrieve stored forecasts from `st.session_state["forecast_history"]` (or run `resolve_forecasts()` on historical data).
2. Group forecasts by P(gain) bucket: <35%, 35–45%, 45–55% (neutral zone), 55–65%, >65%.
3. For each bucket, calculate actual outcome rate (did price rise over the forecast horizon?).
4. **Calibration target:** P(gain) bucket should approximate actual win rate ±15 pp (soft target — small sample expected).

### Neutral zone (OPEN-009)
- Verify that P(gain) in range 45–55% triggers "Insufficient directional signal" text.
- Verify the threshold is applied consistently in both `compute_forecast()` output and UI rendering.

### Holt-Winters parameters
- Read `_holt_winters_damped()` in `indicators.py`. Note α (level smoothing), β (trend smoothing), φ (damping factor).
- These are empirical — document current values and flag if α > 0.5 (overfit to recent data) or φ < 0.8 (aggressive damping).

---

## Domain 5 — Portfolio Math

**File:** `portfolio.py`

### Log returns
- Verify: `log_returns = np.log(prices / prices.shift(1))` — standard formula. Check that NaN first row is dropped before optimisation.

### CVaR calculation
- At 95% confidence: CVaR = mean of the bottom 5% of return scenarios.
- Spot-check with a 1000-scenario bootstrap: CVaR should be ≤ VaR (5th percentile).

### Efficient frontier
- Run `compute_efficient_frontier()` on Nifty 50 group. Verify: (a) returns a Pareto-optimal curve (monotonically increasing return as risk increases), (b) minimum-variance portfolio is leftmost point.

### Stability score (OPEN-006)
- Perturbation test: 10× perturb returns ±5% random noise, re-run optimisation, record σ of portfolio weights across runs.
- **Thresholds (verified 2026-04-13 from `portfolio.py:370-375`):** max_std < 8% → STABLE; 8% ≤ max_std < 15% → MODERATE; max_std ≥ 15% → UNSTABLE.
- **OPEN-025 (pre-tracked P1):** Docstring says `> 15%` UNSTABLE but code fires at `>= 15%`. Off-by-one at boundary. Already in CLAUDE.md open items. Reference it as pre-tracked — do NOT raise as new finding.
- Verify thresholds match the above values (not the old 5%/15% values — those are stale).

---

## Audit output format

Produce a markdown report `docs/signal-accuracy-audit-v{version}.md` with:

```markdown
# Signal Accuracy Audit — v{version} | {date}
## Summary: PASS / PASS WITH NOTES / FAIL
## Domain 1 — Indicator Math: [status]
[table of checks with values + pass/fail]
## Domain 2 — Signal Logic: [status]
[arbitration matrix, any mismatches]
## Domain 3 — Fundamental Data: [status]
[ROE spot-check, P/E lag observed, any delisted tickers]
## Domain 4 — Forecast Calibration: [status]
[P(gain) bucket table, calibration result]
## Domain 5 — Portfolio Math: [status]
[CVaR spot-check, stability thresholds confirmed]
## Issues found: [list or "none"]
## Recommended fixes: [list or "none, audit clean"]
```

---

## GSI-specific constraints

- **Do not** run full `get_batch_data()` during audit — use single-ticker `get_price_data()` to avoid rate-limit exhaustion.
- **Do not** modify `indicators.py` or `portfolio.py` during the audit. Read and validate only. If a fix is needed, open a separate sprint item.
- **Tolerance for yfinance data lag:** Up to 1-day lag on fundamentals is expected and not a defect.
- **Sample size:** 3–5 tickers per domain is sufficient for a spot-check audit. This is not a full backtesting framework.
- **Audit cadence:** Run before every public launch and after any change to `indicators.py`, `forecast.py`, or `portfolio.py`.
