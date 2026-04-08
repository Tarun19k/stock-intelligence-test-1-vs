# GSI — GTM & Phased Market Entry Strategy
# Generated: 2026-04-07 | Session: session_020
# Source: market-position skill + GSI_PRODUCT.md personas + GSI_RISK_REGISTER.md legal risks

---

## POSITIONING (CONFIRMED)

**One-line:** "The free, no-login multi-market stock signal dashboard — Weinstein Stage + Elder Triple Screen → one verdict. India-first, globally aware."

**Secondary angle:** "The tool that shows its work" — every signal has a HELP tooltip, every verdict has a plain-English reason. Educational transparency as a trust driver.

---

## COMPETITIVE LANDSCAPE

| Tool | Strength | Weakness | GSI Advantage |
|---|---|---|---|
| TradingView | Best charting, huge community | Free = 2 indicators, constant upsell | Fully free, no paywall |
| Yahoo Finance | Fundamental data, news | Poor signal aggregation, US-centric | Multi-market signals, India-first |
| Screener.in | Indian fundamentals | India only, no technical signals | 9 markets, technical + fundamental |
| Ticker Tape | India UX | India only, subscription for advanced | Free, global coverage |
| Bloomberg | Comprehensive | $30k/year | Free |

**Key differentiators (lead with these in every post):**
1. Free with no login — instant access, no account required
2. India-first, globally aware — deep NSE/BSE coverage + 8 other markets
3. Two-method signal arbitration — Weinstein Stage + Elder Triple Screen → one verdict
4. Educational transparency — every signal explained in plain English
5. Open source — code visible on GitHub, no black box

---

## WHAT NOT TO CLAIM (LEGAL RED LINES)

- NEVER: "investment advice", "buy/sell recommendations", "guaranteed signals", "SEBI-registered", "real-time data"
- ALWAYS: "educational tool", "signal visualisation", "not investment advice", "15–20 min delayed data"
- Reference: RISK-L01 (SEBI), RISK-L02 (Yahoo ToS), docs/social-media-guidelines.md

---

## PHASED MARKET ENTRY PLAN

### Phase 0 — Launch Prep (session_020 + 1 more)
**Goal:** Ship the last P0 blocker, build launch assets.

| Action | Who | Session |
|---|---|---|
| README with real screenshots (P0 blocker) | Claude + CEO (screenshots) | session_020 |
| Playwright RAM load test (Portfolio Allocator + cvxpy under load) | Claude (post app start) | session_020 |
| demo-gif: 30s animated walkthrough Home → Dashboard → Portfolio Allocator | Claude (/demo-gif skill) | session_020 or next |
| Regenerate CTO brief for v5.36 (score 7/10, new gap table) | Claude | session_021 |
| Update GSI_session.json last_session → session_020 | Claude | session_020 close |

**Exit criteria:** README has screenshots, load test passes, demo GIF exists.

---

### Phase 1 — Private Beta (2 weeks, 0 dev sessions)
**Goal:** Stress test with real users before public noise.

| Action | Owner | Notes |
|---|---|---|
| Share with 10–20 people in personal network | CEO | Traders, finance students, developers |
| Monitor streamlit-analytics dashboard | Both | Is it loading? Are users navigating all tabs? |
| Collect 3–5 written testimonials | CEO | For Product Hunt listing description |
| Fix any production bugs found | Claude | Bug-fix sessions only; no new features |
| RAM check: does the app crash? | Both | Watch Streamlit Cloud logs after each user session |

**Exit criteria:** 0 crash reports, at least 3 testimonials, analytics showing real navigation patterns.

---

### Phase 2 — Community Launch (1 session prep + launch week)
**Goal:** Drive first 200+ MAU through organic community posts.

**Platform sequence (in order):**
1. **r/IndiaInvestments** (220k): "Built a free NSE/BSE technical signal dashboard — Weinstein Stage + Elder Screen in one view. No login, no paywall. Feedback welcome."
2. **r/algotrading** (60k): Technical deep-dive post on signal arbitration implementation (Weinstein > Elder hierarchy, 2K-path Monte Carlo forecast)
3. **Show HN**: "GSI — open source multi-market stock signal dashboard" — lead with GitHub link + architecture decisions
4. **Product Hunt**: Full launch — demo GIF, screenshots, founder story, free tier prominent
5. **r/stocks** (5.5M): "Free alternative to TradingView for multi-market signals" — broadest reach, lowest conversion

**Timing rules:**
- Monday morning IST (market open week energy)
- Avoid: Indian market holidays, US earnings weeks (FAANG etc.)
- Sequence: Post r/IndiaInvestments first, monitor 24h, then r/algotrading, then HN, then PH on same week

**Template post (r/IndiaInvestments):**
```
Title: I built a free NSE/BSE + 8 other markets technical signal dashboard — no login, no paywall

[brief description of what Weinstein Stage and Elder Triple Screen are]
[screenshot of dashboard with RELIANCE.NS or HDFC.NS showing STABLE verdict]
[link to app]
[link to GitHub]

Completely free. No account needed. For educational purposes — not investment advice.
Feedback welcome on what markets/features to add next.
```

---

### Phase 3 — Educational Content (2–3 sessions, parallel to Phase 2 growth)
**Goal:** Establish authority, drive SEO, attract developer community.

Details in: `docs/program/educational-guidebook-concept.md`

---

### Phase 4 — Monetisation Prep (post 500 MAU)
**Trigger:** streamlit-analytics shows 500+ unique sessions/month sustained for 2 weeks.

| Action | Prerequisites |
|---|---|
| Auth integration (Auth0 free tier) | CEO decision on freemium feature split |
| Freemium tier gating (5 lookups/day free → unlimited Pro) | Auth working |
| Claude AI narrative (OPEN-018) | DataManager M4 first |
| DataManager M4 production data layer (OPEN-007) | M2 first |
| Polygon.io data licence evaluation | First paying user arrived |
| Excel export (OPEN-XLSX) | Pro tier defined |
| Custom domain (v2+) | First revenue |

---

## FINANCIAL ADVISORY NOTES

### Yahoo Finance ToS — Critical Constraint (RISK-L02)
- Current status: Accepted for MVP under educational/non-commercial framing
- Commercial trigger: First ₹1 of subscription revenue
- Action needed: ADR-025 — document the trigger formally
- Alternative data sources at commercial scale:
  - Polygon.io: ~$30/month Basic, $80/month Starter (includes NSE data)
  - Alpha Vantage Premium: $50/month
  - Quandl/Nasdaq Data Link: $30–200/month depending on coverage
  - yfinance alternative: financedatabase + investpy (both free but less reliable)

### SEBI Regulatory Framing (RISK-L01 — Mitigated)
- All signal sections have SEBI disclaimer (R17 enforces in regression)
- Social media guidelines documented: docs/social-media-guidelines.md
- Key rule: "developer sharing a tool" framing only; no live signal screenshots in posts
- Never quote specific stocks as BUY/SELL in promotional content

### GDPR / Analytics (RISK-L05 — Open)
- streamlit-analytics uses no PII, no cookies — low risk for EU users
- If Claude API added (OPEN-018), review Anthropic data processing terms before EU launch
