---
name: fundamental-analysis-math
description: Mathematical reference for fundamental analysis metrics used in the GSI Dashboard. Covers ROE formula variants (TTM vs fiscal), yfinance data conventions for NSE/BSE (why None is returned), P/E and P/B interpretation, acceptable tolerance ranges per metric, and DuPont decomposition. Used by signal-accuracy-audit Domain 3 agents and quant-data-fetcher.
---

# Fundamental Analysis Mathematics — Reference

**Use when:** Running Domain 3 (Fundamental Data Accuracy) of the quant audit,
or validating `_calc_roe()` and `signal_score()` in `indicators.py`.

---

## 1. Return on Equity (ROE)

### Standard formula
```
ROE = Net Income / Shareholders' Equity × 100

where: Shareholders' Equity = Total Assets - Total Liabilities
                             = Book Value per Share × Shares Outstanding
```

### GSI implementation (`indicators.py:90-111`)
```
ROE_GSI = netIncomeToCommon / (bookValue × sharesOutstanding) × 100
```

| yfinance field | Meaning | Units |
|---|---|---|
| `netIncomeToCommon` | Net income attributable to common shareholders (TTM) | Currency |
| `bookValue` | **Per-share** book value | Currency per share |
| `sharesOutstanding` | Total shares outstanding | Count |

**Note:** `bookValue × sharesOutstanding` = total book equity. This is correct.
**Fallback:** If any field is None → `returnOnEquity × 100` (yfinance pre-computed, also TTM).

### Variants and their differences

| Variant | Formula | Source | Difference |
|---|---|---|---|
| TTM (trailing 12 months) | Uses last 4 quarters' net income | yfinance, Screener.in | Most current |
| Fiscal year | Uses annual report net income | NSE filings, Moneycontrol | May lag by 6–9 months |
| Average equity | Net Income / ((Equity_t + Equity_t-1) / 2) | Some data providers | Smoother but needs 2 years |
| DuPont | Profit Margin × Asset Turnover × Leverage | — | Decomposed view |

**Acceptable tolerance (audit D3):** ±3 percentage points between yfinance TTM and
Screener.in fiscal year value. Larger gaps need investigation.

### DuPont Decomposition (for context, not in GSI)
```
ROE = Net Profit Margin × Asset Turnover × Equity Multiplier
    = (Net Income/Revenue) × (Revenue/Assets) × (Assets/Equity)
```
Useful for diagnosing WHY ROE changed — not currently used in GSI signal scoring.

---

## 2. P/E Ratio — Price-to-Earnings

### Formula
```
Trailing P/E = Current Price / Trailing 12M EPS
Forward P/E  = Current Price / Consensus Forward EPS
```

### yfinance field
- `trailingPE` = Current Price / TTM EPS (most reliable)
- `forwardPE` = Current Price / Analyst estimate (less reliable, often missing for NSE)

### Acceptable staleness
- Price component: intraday, 15-min delayed on yfinance
- EPS component: quarterly — can be 90+ days stale between earnings
- **Expected P/E drift per day:** 0.1–2% depending on stock movement

### Sector norms (India, 2025-2026)
| Sector | Typical P/E |
|---|---|
| IT (INFY, TCS, WIPRO) | 20–35× |
| Banking (HDFC, ICICI, SBI) | 12–22× |
| Pharma | 18–30× |
| Consumer FMCG | 35–60× |
| PSU / Energy (ONGC, BPCL) | 5–12× |
| Auto (M&M, Tata Motors) | 15–30× |

**Audit tolerance for P/E spot-check:** ±5% vs. NSE/BSE website value.

---

## 3. P/B Ratio — Price-to-Book

### Formula
```
P/B = Current Market Price / Book Value per Share
```

### yfinance field
- `priceToBook` = Current Price / `bookValue`

### Interpretation
| P/B | General meaning |
|---|---|
| < 1.0 | Trading below book — may indicate distress or undervaluation |
| 1–3× | Normal for banks, manufacturing |
| 3–10× | Normal for tech, FMCG brands (intangible-heavy) |
| > 10× | Premium brands (consumer, pharma R&D) |

**Audit tolerance:** ±10% vs. Screener.in (book value updates quarterly).

---

## 4. yfinance Data Conventions — NSE/BSE

### Why Indian fundamentals return None

yfinance sources Indian fundamental data from Yahoo Finance which aggregates from
multiple data providers. Coverage for NSE/BSE is inconsistent because:
1. Indian companies file in INR using non-GAAP formats
2. Yahoo Finance's Indian data aggregation has gaps
3. Some fields (bookValue, netIncomeToCommon) require quarterly parsing that Yahoo
   doesn't always complete for all NSE stocks

### Field availability by category (NSE large-caps, empirical)

| Field | Coverage | Notes |
|---|---|---|
| `marketCap` | ~95% | Most reliable for NSE |
| `currentPrice` / `regularMarketPrice` | ~95% | Real-time |
| `trailingPE` | ~70% | Missing when EPS negative or not filed |
| `priceToBook` | ~60% | Better for Nifty 50, poor for mid/small cap |
| `returnOnEquity` | ~40% | Usually None for NSE — use `_calc_roe()` instead |
| `netIncomeToCommon` | ~50% | Better for large-caps |
| `bookValue` | ~55% | Reasonable for Nifty 50 |
| `sharesOutstanding` | ~75% | Usually available |
| `revenueGrowth` | ~50% | Often None for smaller NSE stocks |

### What to do when fields are None

| Scenario | Correct handling |
|---|---|
| `returnOnEquity` None for NSE | Expected — not a bug. `_calc_roe()` provides self-calculated fallback |
| `_calc_roe()` returns 0.0 | All three raw fields were None AND `returnOnEquity` was None. Document as "data unavailable" — not a code defect |
| `trailingPE` None | Note in D3 report — expected for negative-EPS or non-filing tickers |
| `bookValue` None | Cannot calculate ROE — falls to `returnOnEquity` fallback |

---

## 5. D3 Audit — Acceptable Tolerances

| Metric | Source | Acceptable gap vs. filing | Notes |
|---|---|---|---|
| ROE | Screener.in latest annual report | ±3pp | TTM vs fiscal year lag |
| P/E | NSE website | ±5% | Price moves between check and reference |
| P/B | Screener.in | ±10% | Book value updates quarterly |
| Market Cap | NSE website | ±2% | Should be near real-time |

### Screener.in cross-check procedure
1. Open screener.in/company/TICKER (e.g., screener.in/company/INFY)
2. Find "Return on Equity" in the 10-year history table — use most recent full year
3. Compare to `_calc_roe()` output within ±3pp
4. If gap > 3pp: check if yfinance TTM spans a different fiscal year than Screener.in

---

## 6. Revenue Growth (`revenueGrowth`)

### yfinance field
- `revenueGrowth` = YoY revenue growth rate (decimal, e.g., 0.15 = 15%)

### GSI usage
```python
revg = safe_float(info.get("revenueGrowth", 0)) * 100  # converts to %
```

### Interpretation
| Value | Signal |
|---|---|
| > 20% | Strong growth — positive signal contribution |
| 10–20% | Moderate growth — neutral-positive |
| 0–10% | Slow growth — neutral |
| < 0% | Revenue declining — negative signal |

**NSE coverage note:** `revenueGrowth` returns None for ~50% of NSE stocks.
`safe_float(None, 0)` → 0.0 → neutral treatment. This is correct defensive coding.

---

## 7. ROE in Signal Score Context

`signal_score()` uses ROE as one of several scoring inputs:

```python
roe = _calc_roe(info)
# roe feeds into scoring weights alongside RSI, MACD, Bollinger, ADX, etc.
```

**Impact of ROE=0.0 fallback (Indian stocks):**
When `_calc_roe()` returns 0.0 for an Indian stock, the ROE component of the
momentum score is neutral (contributes 0 to the composite). This is the correct
behaviour — we don't want a zero ROE to actively penalise a stock where data is
simply unavailable.

**Verify in audit:** Check that `signal_score()` handles `roe=0.0` as neutral,
not as "ROE = 0% which is very bad". Look at the scoring weight for `roe=0`.
