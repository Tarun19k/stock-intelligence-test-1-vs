# GSI v5.1 — KeyError 'Close' Hotfix

## Root Cause
yfinance 0.2.54 on Python 3.14 returns DataFrames with:
- MultiIndex columns like ('Close','AAPL') for some US tickers
- Numeric RangeIndex (0,1,2,3,4) on certain auto_adjust edge cases
- Duplicate column names after MultiIndex flattening

Switching between stocks busts the @st.cache_data cache and triggers a
fresh yf.download whose column shape differed from the guard logic.

## Files Changed (3)
| File | Fix |
|---|---|
| market_data.py | _normalize_df(): handles MultiIndex, RangeIndex, duplicates, alt names |
| indicators.py | OHLCV column guard before any computation |
| pages/dashboard.py | _has_ohlcv(), _safe_close() helpers + early exit on bad df |

## How to Apply
Replace these 3 files only. No other files change.
