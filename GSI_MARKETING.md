# GSI_MARKETING.md — Marketing Strategy & Launch Plan
# Version: v1.0 | Created: 2026-03-31
# Append new versions below. Never edit existing records.

---

## Positioning Statement

**For** retail investors, active traders, and finance students
**Who** want multi-market technical signal analysis without a paywall
**The GSI Dashboard is** a free, no-login stock intelligence tool
**That** combines Weinstein Stage analysis and Elder Triple Screen into a single verdict
across 9 global markets and 559 tickers
**Unlike** TradingView (paywalled), Yahoo Finance (US-centric, no signals), or Screener.in (India-only)
**Our product** is fully free, open-source, India-first with global breadth, and explains every signal in plain English.

---

## Core Messages

### Primary (all audiences)
> "Multi-market stock signals. Free. No login. 9 markets, 559 tickers."

### For Indian investors (Ritu)
> "NSE/BSE technical signals — Weinstein Stage + Elder Triple Screen — without the TradingView subscription."

### For global traders (Alex)
> "See what's moving in India, China, and Europe before US markets open. One dashboard. Free."

### For students (Priya)
> "Apply Weinstein Stage and Elder Triple Screen to 559 real tickers. Every signal explained. Free."

---

## Legal Messaging Guardrails

**ALWAYS say:**
- "Educational signal visualisation tool"
- "Not investment advice"
- "Not SEBI-registered"
- "For self-directed research only"
- "Data sourced via yfinance — verify before acting"

**NEVER say:**
- "Investment advice" / "trading signals" / "buy/sell recommendations"
- "Real-time data" (yfinance has 15–20min delay)
- "Guaranteed accuracy" / "proven signals"
- "AI-powered investment decisions"

---

## Launch Channel Strategy

### Phase 1 — Soft launch (beta, 5–10 users)
**Goal:** Catch P0 bugs. Validate core UX. Get first testimonials.
**Channels:** Personal network, close connections in finance/tech.
**Timeline:** 1 week before public launch.

### Phase 2 — Community launch
**Goal:** 100–500 daily active users in first month.

| Platform | Community | Post approach | Timing |
|---|---|---|---|
| Reddit | r/IndiaInvestments (220k) | "Built a free Nifty signal dashboard — feedback welcome" | Monday 9am IST |
| Reddit | r/algotrading (60k) | Technical post: Weinstein + Elder implementation details | Tuesday |
| Reddit | r/stocks (5.5M) | "Free multi-market alternative to TradingView" | Wednesday |
| Hacker News | Show HN | Link to GitHub, technical architecture focus | Thursday 9am ET |
| Product Hunt | General | Full launch: tagline + screenshots + GIF demo | Friday |
| StockTwits | General | Cross-post for retail investor reach | Ongoing |

### Phase 3 — Organic growth
- SEO via GitHub Pages landing page (target: "free TradingView alternative India")
- Twitter/X: Weekly "signal of the week" posts
- YouTube: 2-min demo video (Weinstein Stage explained with real chart)

---

## Product Hunt Launch Assets (to be built)

**Tagline (60 chars max):**
`Free multi-market stock signals. No login. 9 markets.`

**Description (260 chars):**
`GSI Dashboard combines Weinstein Stage analysis and Elder Triple Screen into a single BUY/WATCH/AVOID verdict across 559 tickers in India, USA, Europe, China and more. Free, open-source, no account required.`

**First comment (maker comment):**
Should cover: why built, what problem it solves, what makes it different,
link to GitHub, invite feedback, include educational disclaimer.

**Assets needed:**
- [ ] 1200×630 Open Graph / PH hero image (dark theme screenshot)
- [ ] 800×450 demo GIF (stock selection → dashboard → Insights tab)
- [ ] 3–5 feature screenshots

---

## Reddit Post Templates

### r/IndiaInvestments
```
Title: Built a free Nifty/Sensex + global signal dashboard — no TradingView subscription needed

I got tired of hitting TradingView's 2-indicator free tier limit every time I wanted to
check Weinstein Stage + MACD on my Nifty watchlist. So I built one.

**What it does:**
- 9 markets: India, USA, Europe, China, Commodities, ETFs
- 559 tickers across 38 groups
- Weinstein Stage + Elder Triple Screen → single BUY/WATCH/AVOID verdict
- Portfolio allocator (Mean-CVaR) for group-level analysis
- Global Intelligence page for macro context

**What it doesn't do:**
- Tell you what to buy (not investment advice, not SEBI-registered)
- Require login or account
- Cost anything

[Link] | [GitHub]

Would love feedback from fellow retail investors — what signals/markets am I missing?
```

---

## Success Metrics (MVP)

| Metric | Target (30 days post-launch) | Measurement |
|---|---|---|
| Daily active users | 50+ | streamlit-analytics |
| GitHub stars | 25+ | GitHub |
| Bounce rate (app) | <60% | streamlit-analytics |
| P0 bug reports | 0 open after 48h | GitHub Issues |
| Reddit upvotes | 50+ on launch post | Reddit |

---

## Version History

| Version | Date | Notes |
|---|---|---|
| v1.0 | 2026-03-31 | Initial marketing strategy — positioning, channels, launch plan, templates |
