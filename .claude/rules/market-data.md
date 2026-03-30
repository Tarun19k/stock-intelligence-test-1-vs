---
paths:
  - "market_data.py"
---

# Market Data Rules — applies when editing market_data.py

## Rate limit gate — mandatory on every new function
Every public function that calls yfinance MUST call `_is_rate_limited()` first and return a safe default if true. Pattern:
```python
if _is_rate_limited():
    return {}   # or [] or pd.DataFrame() depending on return type
_global_throttle()
```

## RSS allowlist
Every new RSS feed domain MUST be added to `_ALLOWED_RSS_DOMAINS` before use. No feed may bypass the allowlist check.

## No direct yfinance calls from pages
This file is the ONLY file allowed to import yfinance. If you find yourself adding `import yfinance` to any other file, stop and route through market_data.py instead.

## TTL guidelines
- Live price (5s data): TTL = 5s
- OHLCV price data: TTL = 300s
- Ticker info (fundamentals): TTL = 600s
- Financial statements (income/balance): TTL = 86400s (24h)
- News/RSS: TTL = 600s
- Batch/group data: TTL = 300s

## cache_buster convention
- All market data functions take `cache_buster: int = 0`
- `get_news()` uses `cache_buster=0` always — news is not stock-specific
- Do NOT pass `cb` (session cache buster) to `get_news()`

## DataManager bypass
Pages must NOT call `DataManager.fetch()` until M4. DataManager is in bypass mode. Do not add DataManager routing to any existing market_data function until M4 is implemented.
