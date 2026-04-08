# GSI Executive Brief — v5.36
# Generated: 2026-04-07 | Session: session_020 | Regression: 434/434 PASS
# Mode: Program Chief + CTO + CFO + COO (all four lenses)
# Source: CXO skill + live file reads (GSI_PRODUCT.md, GSI_RISK_REGISTER.md, reports/gsi-cto-brief.html, GSI_SPRINT.md)
# NOTE: reports/gsi-cto-brief.html frozen at v5.28 — scores in this doc updated to v5.36 state

---

## PROGRAM STATUS

```
Version:          v5.36
Regression:       434/434 PASS — clean
Sprint:           v5.36 COMPLETE (session_019) · v5.37 not yet started
Sessions to MVP:  2–3 (README screenshots + Playwright load test)
CTO Brief score:  5/10 at v5.28 → estimated 7/10 at v5.36
```

---

## MVP READINESS GATE

| Item | Priority | Status | Blocker? |
|---|---|---|---|
| 9 markets, 559 tickers, 38 groups | P0 | DONE | No |
| Unified verdict (Weinstein + Elder) | P0 | DONE | No |
| 4-tab stock dashboard | P0 | DONE | No |
| SEBI + algo disclaimers (R17 enforced) | P0 | DONE | No |
| Signal conflict resolution (Weinstein > Elder hierarchy) | P0 | DONE v5.32 | No |
| ROE data integrity fix (_calc_roe self-calc) | P0 | DONE v5.36 | No |
| Stale RSS / false "Live" label (48h gate) | P0 | DONE v5.31 | No |
| Landing page (docs/index.html GitHub Pages) | P0 | DONE v5.35 | No — screenshots missing |
| README with screenshots | P0 | PENDING | **YES — launch blocker** |
| WorldMonitor CSP fix (full Leaflet.js) | P0→Stopgap | Stopgap only (link button) | Partial — OPEN-020 deferred |
| streamlit-analytics integration | P1 | DONE v5.35 | No |
| Playwright UI test suite | P1 | NOT STARTED | No (P1) |

**Launch blockers remaining: 1** — README screenshots.

---

## ACTIVE BLOCKERS REQUIRING CEO DECISION

### BLOCKER-1: Yahoo Finance ToS → Commercial Use (RISK-L02)
- **Trigger:** First ₹1 of subscription revenue
- **Options:** (A) Stay educational indefinitely — no monetisation, (B) Switch to Polygon.io (~$30/mo) when first paying user arrives, (C) Apply for Yahoo Finance commercial licence
- **Recommended:** Option B — document trigger in ADR-025
- **Status:** Accepted for MVP. Must be formalised before freemium launch.

### BLOCKER-2: RAM Profiling Before High-Traffic Push (RISK-T02)
- **Issue:** Streamlit Community Cloud 1GB RAM limit; Portfolio Allocator + cvxpy + 559 tickers = unknown peak RAM
- **Recommended:** Playwright-driven load test before Reddit/PH launch
- **Status:** Not blocking MVP prep. Must precede Phase 2 community launch.

---

## CTO: TECHNICAL HEALTH SCORECARD (v5.36)

| Dimension | v5.28 Score | v5.36 Score | Delta |
|---|---|---|---|
| Data layer coherence | 2/5 | 3/5 | DataManager M1 bypass mode; cross-page cache added; DataContract missing |
| Rate limiting & resilience | 3/5 | 4/5 | Token bucket + warmth guard + stale fallback; single-source risk remains |
| Regression coverage | 3/5 | 5/5 | 434 checks; R17/R25/R26/R28/R29 enforce compliance + observability + hooks |
| Module boundary discipline | 3/5 | 4/5 | yfinance correctly gatekept; compliance_check.py extracted |
| Compliance enforcement | 2/5 | 5/5 | 3 pre-commit hooks + 8-gate compliance script |

### Remaining Architecture Gaps

| Gap | Impact | Sprint estimate |
|---|---|---|
| DataManager M2 (OPEN-007) — no DataContract validator | Cross-page data coherence not guaranteed | 1–2 sprints |
| WorldMonitor full fix (OPEN-020) — Leaflet.js + GDELT | Headline visual is a link button, not interactive map | 2 sprints |
| No error monitoring (RISK-O01) — Sentry free tier | Production errors invisible | 0.5 sprint |
| Claude AI narrative (OPEN-018) | Strongest differentiator — no LLM output in product yet | 1 sprint (after DataManager) |

---

## CFO: COST & REVENUE PATH

### Current Cost Stack: ₹0/month
- Streamlit Community Cloud: free
- yfinance: free (educational use)
- streamlit-analytics: zero backend
- LiteLLM proxy: local only

### Revenue Milestones

| Stage | Trigger | Revenue potential | Required unlock |
|---|---|---|---|
| Stage 0 (now): Free launch | README done | ₹0 — traction building | 2–3 sessions |
| Stage 1: Freemium gating | 500+ MAU | ₹20k–50k/month | Auth (Auth0 free) + paid tier design |
| Stage 2: Pro tier | 2,000+ MAU | ₹1.5L–3L/month | Polygon.io + Claude AI narrative + Excel export |
| Stage 3: B2B/white-label | 1 institutional client | ₹5L+/year | Custom domain + SLA |

**CFO rule:** Do not spend a rupee until Stage 1 trigger (500 MAU). All pre-Stage-1 work is ₹0.

---

## COO: OPERATIONS HEALTH — HEALTHY

| Metric | Status | Notes |
|---|---|---|
| Sprint cadence | Healthy | 7–12 items/sprint, all under 9-item cap; v5.36 COMPLETE |
| Regression discipline | Healthy | 434/434, no baseline drift in last 3 sessions |
| Snapshot deviations | Clean | 0 DEVIATION records in last 4 snapshots (SNAPSHOT-001 through 005) |
| Phase 3 compliance | Full | sync_docs, manifest archive, WIP→IDLE followed in v5.35/v5.36 |
| Session learnings | Healthy | 12 records: 0 HALLUCINATION, 1 CONFUSION, 3 STALE (all fixed), 8 LEARNING |

**Process gap:** `GSI_session.json` `last_session` field stuck at `session_015` — update to `session_020` at session close.

---

## SIGN-OFF QUEUE

| Decision | Options | Recommended |
|---|---|---|
| ADR-025: Yahoo ToS commercial trigger | A / B / C (see above) | Option B |
| Guidebook scope | MIT licence + no production tickers in tutorial repo | Confirm |
| Beta list | Who are the 10–20 beta testers? | CEO to define |
| Reddit launch timing | Which Monday IST? | Avoid earnings weeks |
