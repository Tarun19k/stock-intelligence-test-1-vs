---
name: quant-data-fetcher
description: Safe protocol for fetching live yfinance market data outside the Streamlit app context — for use during quant audits, D3 fundamental validation, and ticker mapping checks. Covers direct yf.Ticker() calls, rate-safe delays, field availability by market, and passing results to GSI functions like _calc_roe().
---

# Quant Data Fetcher — Safe yfinance Protocol (Audit Context)

**Use when:** Running Domain 3 (Fundamental Data) or ticker mapping checks during a
quant audit. Do NOT use for production data fetching — that goes through `market_data.py`.

---

## Why a separate protocol

The GSI app fetches data via `market_data.py` which wraps yfinance with:
- Token bucket rate limiter (`_global_throttle()`)
- Module-level cache (`_ticker_cache`)
- Streamlit `@st.cache_data` decorators

These cannot be used outside a running Streamlit session. In audit context, we call
yfinance directly — but we must replicate the safety constraints manually.

---

## Step 1 — Verify environment

```python
import yfinance as yf
import time
print(yf.__version__)  # must be 1.2.0 per GSI constraints
```

If version mismatch: stop and note in audit report. Do not proceed with mismatched version.

---

## Step 2 — Fetch info dict (safe single-ticker call)

```python
import yfinance as yf
import time

def audit_fetch_info(ticker: str, delay_s: float = 2.0) -> dict:
    """
    Fetch yfinance info dict for one ticker.
    delay_s: minimum 2.0s — matches GSI token bucket rate (0.4s/token × 5 tokens).
    Returns {} on error (do not raise — audit should continue).
    """
    try:
        time.sleep(delay_s)  # rate-safe gap between calls
        t = yf.Ticker(ticker)
        info = t.info
        return info if isinstance(info, dict) else {}
    except Exception as e:
        print(f"[audit_fetch_info] {ticker}: {e}")
        return {}
```

**Call sequence for 3 tickers:**
```python
tickers = ["INFY.NS", "HDFCBANK.NS", "RELIANCE.NS"]
infos = {}
for ticker in tickers:
    infos[ticker] = audit_fetch_info(ticker)  # 2s gap built-in
```

---

## Step 3 — Extract ROE via _calc_roe()

Do NOT reimport `_calc_roe` from the app — replicate the logic inline to avoid
Streamlit import side effects:

```python
def audit_calc_roe(info: dict) -> dict:
    """
    Replicates indicators._calc_roe() for audit use.
    Returns dict with value, source, and raw fields for transparency.
    """
    def safe_float(v, default=0.0):
        try:
            f = float(v)
            return f if f == f else default  # NaN check
        except (TypeError, ValueError):
            return default

    net_income = safe_float(info.get("netIncomeToCommon"))
    book_value = safe_float(info.get("bookValue"))       # per-share
    shares     = safe_float(info.get("sharesOutstanding"))

    if net_income and book_value and shares:
        equity = book_value * shares
        if equity > 0:
            return {
                "value":  round((net_income / equity) * 100, 2),
                "source": "calculated",
                "net_income": net_income,
                "book_value": book_value,
                "shares":     shares,
            }

    # Fallback
    roe_direct = safe_float(info.get("returnOnEquity"))
    return {
        "value":  round(roe_direct * 100, 2),
        "source": "fallback_yf_returnOnEquity",
        "net_income": net_income,
        "book_value": book_value,
        "shares":     shares,
    }
```

---

## Step 4 — Field availability matrix by market

Expected `None` returns per market — these are data gaps, NOT bugs:

| Field | India (NSE/BSE) | US | UK/EU | China |
|---|---|---|---|---|
| `netIncomeToCommon` | Often None | ✅ | Partial | Partial |
| `bookValue` | Often None | ✅ | Partial | Partial |
| `sharesOutstanding` | Partial | ✅ | Partial | Partial |
| `returnOnEquity` | Usually None | ✅ | Partial | Often None |
| `trailingPE` | Partial | ✅ | Partial | Partial |
| `marketCap` | ✅ | ✅ | ✅ | Partial |

**When all three raw fields are None → `_calc_roe()` returns `0.0`.**
Document as: "ROE unavailable — yfinance does not supply Indian market fundamentals."
Tolerance: ±3pp vs. Screener.in filing values.

---

## Step 5 — Build the D3 CEO validation table

After fetching all tickers, format as:

```python
print(f"{'Ticker':<15} {'ROE Value':>10} {'Source':<30} {'Net Income':>15} {'Book Val':>10} {'Shares':>15}")
for ticker, info in infos.items():
    result = audit_calc_roe(info)
    print(f"{ticker:<15} {result['value']:>10.2f}% {result['source']:<30} "
          f"{result['net_income']:>15,.0f} {result['book_value']:>10.2f} {result['shares']:>15,.0f}")
```

The CEO then opens Screener.in for each ticker and cross-checks against the
"Return on Equity" figure in the latest annual report.

---

## Step 6 — Ticker mapping integrity check

Sample strategy: 3 tickers from India (NSE), 2 from US, 2 from China, 1 each from
Japan, Germany, UK, Saudi Arabia, Australia, Brazil = ~14 calls total.

```python
def audit_ticker_check(ticker: str) -> dict:
    """Check that ticker resolves without error and has expected name."""
    info = audit_fetch_info(ticker, delay_s=1.5)
    return {
        "ticker":   ticker,
        "resolved": bool(info),
        "name":     info.get("longName") or info.get("shortName") or "UNKNOWN",
        "sector":   info.get("sector", "N/A"),
        "currency": info.get("currency", "N/A"),
        "empty_df": not bool(info),
    }
```

**Pass criterion:** Ticker resolves (non-empty info), name plausibly matches expected
company, no delisted indicator (yfinance returns empty dict `{}` for delisted tickers).

---

## Constraints

- **Max tickers per audit run:** 15 (avoids rate-limit exhaustion)
- **Min delay between calls:** 2.0s (matches GSI rate budget)
- **Do NOT use** `yf.download()` with multiple tickers — use `yf.Ticker()` one at a time
- **Do NOT import** from `market_data.py` — Streamlit decorators trigger import errors
- **Do NOT** run during market hours for Indian markets — 9:15–15:30 IST increases 429s
- **yfinance 1.2.0 only** — MultiIndex structure changed in 1.1.x; do not run with other versions
