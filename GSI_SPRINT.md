# GSI Dashboard — Sprint Board
# ════════════════════════════════════════════════════════════════════════
# This file is the single source of truth for sprint planning.
# Updated at the start and end of every session.
# The "In Progress" column acts as a WIP lock alongside GSI_WIP.md.
# ════════════════════════════════════════════════════════════════════════

## Current Sprint: v5.33 (Planning)

**Status:** Planning — not started
**Target date:** TBD
**Regression baseline entering sprint:** 392/392

---

### Backlog (candidate items for v5.33)

Sourced from GSI_session.json open_items and GSI_AUDIT_TRAIL.md open findings.
Prioritised by impact and implementation effort.

**Phase groupings:**
- Items marked `OPEN-018 (Claude API)` require AI narrative integration — future phase, do not start before OPEN-018.
- Items marked `OPEN-007` depend on DataManager M2 — complete M2 before starting those.
- All other items are standalone and can be picked for the next sprint.
Prioritised by impact and implementation effort.

| ID | Description | Effort | Source | Governance policy |
|---|---|---|---|---|
| RISK-001 | XSS guard: sanitise() in unsafe_allow_html f-strings | Low | session | Policy 2 (architecture) |
| RISK-003 | safe_ticker_key() before yf.download() | Low | session | Policy 2 |
| D-02 bench | ROE benchmark: self-calculate from yfinance financials | Medium | audit | Policy 5 (data coherence) |
| H-02 | Loading state explanation on first load | Low | audit | Policy 3 (UX) |
| D-07 | Elder labels in plain English (BUY SETUP → Bullish setup) | Low | audit | Policy 3 |
| D-09 | Forecast correction factor disclosed to user | Low | audit | Policy 7 (freshness) |
| G-03 | Impact chain overflow fix at 1280px | Low | audit | Policy 3 |
| F-14 | West Asia content attribution | Low | audit | Policy 1 (data integrity) |
| OPEN-004 | Extract SCORING_WEIGHTS to config.py | Low | session | Policy 2 |
| OPEN-003 | Cross-session forecast persistence (Supabase) | High | session | Policy 2 |
| D-05 | Week Summary state persists on Dashboard navigation — no loading indicator | Low | audit | Policy 3 (UX) |
| G-02 | Only 4 GI topic cards — insufficient for "Global Intelligence Centre" | Medium | audit | Policy 1 (data) |
| C-02 | Macro data (Gold, Crude) not accessible to stock-level AI narrative | Medium | audit | OPEN-018 (Claude API) |
| C-03 | RSI 36 described as "neutral momentum" in AI narrative — wrong | Medium | audit | OPEN-018 (Claude API) |
| C-08 | Sector breadth computed but never passed to AI narrative engine | Medium | audit | OPEN-018 (Claude API) |
| F-02 | India Impact formula static — not computed from live Crude price | Medium | audit | OPEN-018 (Claude API) |
| F-10 | Impact chain overflows at 1280px — duplicate of G-03 | Low | audit | Policy 3 (UX) |
| EQA-38 | GI subtitle "Real-Time" claim — partially fixed (Live Headlines gated) | Low | audit | Policy 7 (freshness) |
| C-01 | Sector breadth not wired to narrative — partially fixed in v5.31 | Medium | audit | OPEN-018 (Claude API) |
| OPEN-006 | Portfolio Allocator stability score UI (shipped v5.23 — needs UI polish) | Medium | session | Policy 3 (UX) |
| OPEN-007 | DataManager M2: CacheManager + DataContract validator | High | session | Policy 2 (arch) |
| OPEN-017 | Governance policy framework — 7 policies to enforce in regression (R25) | Low | session | Policy 2 (arch) |
| OPEN-018 | Claude API integration — live AI narrative (Opus 4.6 / Mythos-ready) | Medium | session | Policy 4,5 |
| C-05 | Momentum score decomposition / scale disclosure | Medium | audit | Policy 5 |
| EQA-41 | Forecast accuracy visual baseline | Medium | audit | Policy 7 |
| G-05 | GI subtitle "Real-Time" — remove false claim | Low | audit | Policy 7 |

---

### In Progress

Nothing in progress. Next session picks from Backlog above.

---

### Done — v5.32 (2026-03-29)

| ID | Description | Verified |
|---|---|---|
| OPEN-008 | calc_5d_change() shared utility | Regression R23b |
| OPEN-009 | P(gain) 45–55% neutral zone | Regression R23b |
| OPEN-010 | Forecast dedup — replace same-day entries | Regression R23b |
| OPEN-011 | Dynamic week summary section titles | Regression R23b |
| OPEN-012 | Weinstein override label names the stage | Regression R23b |
| OPEN-013 | MACD (Daily) label on chart + KPI panel | Regression R23b |
| OPEN-014 | GI watchlist market filter | Regression R23b |
| OPEN-015 | Market LIVE badge names specific market | Regression R23b |
| OPEN-016 | GI watchlist cache_buster=0 | Regression R23b |

---

### Done — v5.31 (2026-03-28)

| ID | Description | Verified |
|---|---|---|
| P0-1 | Option B: raw score removed from header | QA verified |
| P0-2 | ROE null guard: N/A not 0.0% | QA verified |
| P0-3 | SEBI disclaimer + algorithmic disclosure | QA verified |
| P0-4 | Watch Out For RSI/MACD-aware fallback | QA verified |
| H-03 | Market status short labels | QA verified |
| F-15/F-01 | GI topic cards expanded by default | QA verified |
| F-03 | Stale RSS replaced, 48h freshness gate | QA verified |
| F-06/EQA-33 | What You Should Do Next removed | QA verified |
| EQA-29 | SEBI disclaimer | QA verified |
| EQA-32 | Algorithmic disclosure | QA verified |

---

### Sprint Planning Rules

1. **Max 9 items per sprint** — v5.32 was the ceiling. Larger sprints fragment context and risk mid-session limits.
2. **Group by file** — batch changes to the same file in the same sprint. Cross-file changes in separate sprints.
3. **Regression check before adding** — every new item must have a clear R-check definition before entering "In Progress".
4. **No item enters "In Progress" without a WIP entry** — update GSI_WIP.md simultaneously.
5. **Commit after every file** — do not batch multiple files into a single commit. If Claude hits a limit, only uncommitted files are at risk.

---

### Sprint Velocity

| Sprint | Version | Items | Sessions | Outcome |
|---|---|---|---|---|
| Data coherence | v5.32 | 9 | 1 | All 9 complete, 11 R23b checks |
| P0 regulatory | v5.31 | 8 | 1 | All 8 verified by QA |
| Lazy loading M0-M3 | v5.24–v5.25 | 6 | 2 | Complete |
| Portfolio allocator | v5.23 | 1 major | 1 | Complete |
