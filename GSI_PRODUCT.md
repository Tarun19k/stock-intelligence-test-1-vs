# GSI_PRODUCT.md — Product Roadmap & MVP Definition
# Version: v1.0 | Created: 2026-03-31
# Append new versions below. Never edit existing records.

---

## Product Vision

A free, no-login, multi-market stock signal dashboard that makes institutional-grade
technical analysis (Weinstein Stage, Elder Triple Screen) accessible to retail investors,
traders, and finance students across India, USA, Europe, and beyond.

**Not:** An investment advisory. Not a trading platform. Not SEBI-registered.
**Is:** An educational signal visualisation tool for self-directed learning and research.

---

## User Personas

### Persona 1 — Ritu (Indian Retail Investor)
- Age: 35 | Location: Mumbai | Platform: Zerodha
- Goal: Technical signals for NSE/BSE without paying ₹1,200/month for TradingView Pro
- Frustration: Free tools are US-centric; Indian-focused tools lack technical depth
- Behaviour: Opens dashboard 3×/week before market open; checks sector signals
- Success: "I can see the Weinstein stage for my watchlist in one view"

### Persona 2 — Alex (US Retail Trader)
- Age: 28 | Location: Austin, TX | Platform: Robinhood + Reddit r/stocks
- Goal: Multi-market breadth — what's moving globally before US market opens
- Frustration: Yahoo Finance is fundamental-heavy; no signal aggregation
- Behaviour: Daily Global Intelligence page + Top Movers; weekly portfolio check
- Success: "I can see India/China/Europe signals before US open — no other free tool does this"

### Persona 3 — Priya (Finance Student)
- Age: 22 | Location: Bangalore | Platform: University coursework
- Goal: Apply Weinstein Stage and Elder Triple Screen to real data for assignments
- Frustration: Theory without practice; Bloomberg costs more than her tuition
- Behaviour: Uses HELP tooltips extensively; tracks forecast accuracy; exports for reports
- Success: "I understand what Stage 2 looks like on a real chart"

---

## MVP Scope (v1.0 Public Launch)

### In scope — current app + hardening
| Feature | Status | Priority |
|---|---|---|
| 9 markets, 559 tickers, 38 groups | Done | P0 |
| Unified verdict (Weinstein + Elder) | Done | P0 |
| 4-tab stock dashboard | Done | P0 |
| Portfolio Allocator | Done | P1 |
| Global Intelligence page | Done | P1 |
| SEBI + algo disclaimers | Done | P0 |
| Landing page (GitHub Pages) | Not started | P0 |
| README with screenshots | Not started | P0 |
| Basic analytics (streamlit-analytics) | Not started | P1 |
| Playwright UI test suite | Not started | P1 |
| Excel export (download button) | Not started | P2 |
| PDF report export | Not started | P2 |

### Out of scope (MVP) — v2+ roadmap
| Feature | Reason deferred |
|---|---|
| User auth / login | Not needed for free public tool; adds complexity |
| Persistent forecasts (Supabase) | OPEN-003 — complexity, cost |
| Claude AI narrative (full OPEN-018) | Nice-to-have, not blocking |
| Custom domain | Paid tier on Streamlit Cloud |
| Mobile native app | Major effort, web-first first |
| Email alerts | Requires auth + backend |
| Portfolio tracking | Requires auth + persistent storage |
| Paid tier | Post-traction |

---

## Dependency Map

### Current production dependencies
| Package | Version | Purpose | Risk |
|---|---|---|---|
| streamlit | ==1.55.0 | UI framework | CSS selectors change on upgrade — see CONSTRAINT-002 |
| yfinance | ==1.2.0 | Market data | ToS: personal/educational only; no commercial redistribution |
| pandas | >=1.4.0 | Data processing | <3.0 (Streamlit metadata declares pandas<3) |
| plotly | ==5.24.1 | Charts | Stable — low upgrade risk |
| numpy | >=2.0.0 | Numerics | Stable |
| cvxpy | ==1.8.2 | Portfolio optimiser | Requires libopenblas-dev on Linux (packages.txt) |
| feedparser | ==6.0.11 | RSS news | Stable |
| pytz | ==2024.2 | Timezone handling | Stable |
| requests | ==2.32.3 | HTTP | Stable |

### MVP additions needed
| Package | Purpose | Notes |
|---|---|---|
| streamlit-analytics | Usage tracking | Zero-backend, JSON persistence |
| openpyxl | Excel export | Add when /export-xlsx shipped |
| reportlab | PDF export | Add when /export-pdf shipped |
| anthropic | Claude AI narrative | Add when OPEN-018 shipped; needs API key in secrets |
| playwright | UI testing | Dev dependency only, not in requirements.txt |

---

## Free Tier Constraints & Mitigations

| Constraint | Limit | Current mitigation | MVP action |
|---|---|---|---|
| RAM | 1GB total | Token bucket + module cache | Memory profiling before launch |
| App sleep | 12h inactivity | N/A (acceptable for MVP) | Document in README |
| No custom domain | streamlit.app URL only | Acceptable for MVP | Buy domain for v2 |
| No persistent storage | Filesystem wiped on redeploy | Session state for forecasts | Supabase for v2 (OPEN-003) |
| No background jobs | No cron/scheduler | Fragment auto-refresh handles it | Acceptable for MVP |
| Cold start | ~5–15s first load | Warmth guard + lazy loading | Document expected load time |

---

## Monetisation Path (Post-MVP, v2+)

Not planned for MVP. All monetisation decisions deferred until traction is established.

Potential paths under consideration (no commitment):
1. **Freemium**: Free = current app. Pro = exports, Claude AI narrative, alerts
2. **API access**: Pay-per-call for signal data (requires proper data licensing)
3. **White-label**: Dashboard for financial educators / institutions

**Hard constraint:** Any monetisation path requires resolving Yahoo Finance ToS
(data redistribution prohibition). Likely requires switching to a paid licensed data
source (Polygon.io, Quandl, etc.) for commercial use.

---

## Version History

| Version | Date | Notes |
|---|---|---|
| v1.0 | 2026-03-31 | Initial product doc — personas, MVP scope, dependencies, free tier map |
