# Launch Checklist — GSI Dashboard MVP

Pre-launch gate. All items must pass before public announcement.

## Tier 1 — BLOCKING (must pass, no exceptions)

### Legal & Regulatory
- [ ] "Educational use only — not investment advice" on every page showing signals
- [ ] "Not SEBI-registered" disclaimer visible on all BUY/WATCH/AVOID sections
- [ ] "Algorithmically generated" label on all AI narrative sections
- [ ] "Data sourced from Yahoo Finance via yfinance — not for commercial use" in footer/about
- [ ] No target prices, entry/exit levels, or "you should buy/sell X" language anywhere
- [ ] No claim of "real-time" data (yfinance has 15–20min delay for most markets)

### Technical stability
- [ ] python3 regression.py → 396/396 PASS
- [ ] Compliance check (GSI_COMPLIANCE_CHECKLIST.md) → all tiers pass
- [ ] App loads without errors on cold start (Streamlit Cloud)
- [ ] No JS console errors on page load
- [ ] Rate limiter functioning — 429 cooldown gate tested
- [ ] Memory <900MB at rest on Streamlit Cloud

### Data accuracy
- [ ] TATAMOTORS.NS not present — TMCV.NS + TMPV.NS confirmed
- [ ] ROE shows N/A (not 0.0%) for tickers with null yfinance data
- [ ] Watch Out For section never shows "No major red flags at this time."

## Tier 2 — SHOULD pass before launch

### User experience
- [ ] Landing page live (GitHub Pages or Vercel)
- [ ] README has screenshots and 1-paragraph description
- [ ] Cold start time <15s (acceptable for free tier)
- [ ] App title and favicon set correctly
- [ ] Error log in sidebar is empty on normal operation

### Content
- [ ] Product Hunt listing drafted (tagline, description, first comment, GIF/screenshots)
- [ ] Reddit posts drafted for r/IndiaInvestments, r/algotrading, r/stocks
- [ ] GitHub repo description and topics updated

## Tier 3 — NICE to have

- [ ] streamlit-analytics installed for basic usage tracking
- [ ] Open Graph image (1200×630) for social sharing
- [ ] /ui-test Playwright suite passes
- [ ] OPEN-018 (Claude AI narrative) shipped

## Post-launch (within 48h)
- [ ] Monitor Streamlit Cloud resource usage
- [ ] Watch for rate limit errors in error log
- [ ] Collect first feedback — P0 bugs get fixed same day
- [ ] Update GSI_SPRINT.md with feedback-driven items
