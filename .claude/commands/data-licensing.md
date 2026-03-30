# Data Licensing — GSI Dashboard

Check data source terms of service and licensing before adding any new data feed.

## Current data sources and their status

| Source | Access method | Personal use | Commercial use | Redistribution | Status |
|---|---|---|---|---|---|
| Yahoo Finance | yfinance (unofficial) | ✅ OK | ❌ Prohibited | ❌ Prohibited | Accepted risk (MVP) |
| BBC RSS | feedparser | ✅ OK | ✅ OK (editorial) | ⚠️ Attribution required | Allowlisted |
| Reuters RSS | feedparser | ✅ OK | ✅ OK (editorial) | ⚠️ Attribution required | Allowlisted |
| TechCrunch RSS | feedparser | N/A | N/A | N/A | Removed v5.31 (stale) |

## Yahoo Finance ToS — key constraints
- Data is "for personal use only"
- "You agree not to redistribute the information found herein"
- yfinance is an unofficial wrapper — not endorsed by Yahoo
- **Commercial path requires:** Switch to a licensed data provider

## Licensed data alternatives (for commercial/v2+ path)

| Provider | Free tier | Paid tier | Coverage | Notes |
|---|---|---|---|---|
| Polygon.io | 5 API calls/min, US only, delayed | $29/mo+ | US stocks, options, crypto | Strong REST API |
| Alpha Vantage | 25 calls/day, delayed | $50/mo+ | Global, forex, crypto | yfinance-like simplicity |
| EODHD | 20 calls/day | $20/mo+ | 70+ exchanges, NSE/BSE included | Good India coverage |
| Quandl (Nasdaq) | Limited free | Custom pricing | Financial datasets | More for fundamentals |
| Tiingo | 50 calls/hour free | $10/mo+ | US stocks, crypto | Clean REST API |
| NSE India (official) | Public API (limited) | N/A | Indian markets only | Unstable, rate limited |

## Decision rule before adding any new data source
1. Can it be accessed without an API key? → Likely unofficial → Check ToS
2. Does ToS allow commercial redistribution? → Required for any paid tier
3. Does it cover the markets GSI needs? (India mandatory for core use case)
4. Is it stable enough for production? (check uptime history, GitHub issues)
5. Add to `GSI_DEPENDENCIES.md` with constraint entry

## RSS feed addition rule (from market-data.md scoped rule)
Every new RSS feed domain must be added to `_ALLOWED_RSS_DOMAINS` in `market_data.py`.
Check robots.txt and ToS for the domain before adding.
Attribution in UI: show source name on every news item.

## Commercial launch trigger
When GSI moves from free educational tool → any form of commercial product:
1. Must switch to licensed data source (EODHD or Polygon.io for global coverage)
2. Update all disclaimers to reflect licensed data
3. Remove Yahoo Finance attribution
4. Update GSI_DEPENDENCIES.md and GSI_RISK_REGISTER.md (close RISK-L02)
