# MVP Scope — GSI Dashboard

Define, validate, and track scope for the public MVP release.

## MVP definition for GSI
The MVP is the current app hardened for public use with strangers — not new features.

### In scope (MVP v1.0)
- All 9 markets, 559 tickers, 38 groups — current feature set
- Unified verdict (Weinstein + Elder) with plain-English reason
- 4-tab stock dashboard (Charts, Forecast, Compare, Insights)
- Portfolio Allocator (group view)
- Global Intelligence page
- SEBI disclaimer + algorithmic disclosure on all signal sections
- Basic usage analytics (streamlit-analytics, no backend)
- Landing page (GitHub Pages)
- README / user guide
- "Educational use only" framing throughout

### Out of scope (MVP — defer to v2+)
- User authentication / login
- Persistent forecast history (Supabase — OPEN-003)
- Claude API narrative (OPEN-018) — nice-to-have, not blocking
- Excel/PDF export
- Custom domain
- Mobile native app
- Paid tier / monetisation
- Email alerts / notifications
- Portfolio tracking (user's actual holdings)

## User personas

**Ritu** — Indian retail investor, 35, Zerodha user
- Wants: Nifty 50 signals without paying for TradingView
- Frustration: TradingView free tier = 2 indicators max, constant upsell
- Success metric: Opens dashboard 3x/week, checks sector signals before trading

**Alex** — US retail trader, 28, Reddit r/stocks regular
- Wants: Multi-market breadth view, see what's moving globally
- Frustration: Yahoo Finance is fundamental-heavy, poor signal aggregation
- Success metric: Uses GI page + top movers daily

**Priya** — Finance student, 22, learning technical analysis
- Wants: Understand Weinstein stages and Elder screens in practice
- Frustration: Theory ≠ practical tool, can't afford Bloomberg
- Success metric: Uses HELP_TEXT tooltips, checks forecast accuracy tab

## Acceptance criteria for MVP launch
- [ ] regression.py 396/396 PASS
- [ ] compliance check all tiers pass
- [ ] Playwright UI tests pass (0 JS errors on cold start)
- [ ] SEBI disclaimer visible on Insights tab
- [ ] App loads in <10s on cold start (Streamlit Cloud)
- [ ] Memory <900MB at rest (100MB headroom below 1GB limit)
- [ ] Landing page live on GitHub Pages
- [ ] README updated with screenshots
- [ ] "Educational use only" on every page with stock signals
- [ ] yfinance disclaimer in footer

## Launch sequence
1. Harden app (regression + UI tests + memory profiling)
2. Landing page live
3. Product Hunt draft ready
4. Reddit posts drafted (r/IndiaInvestments, r/stocks, r/algotrading)
5. Soft launch: share with 5–10 beta users
6. Fix P0 feedback
7. Public launch: Product Hunt + Reddit + HackerNews ShowHN
