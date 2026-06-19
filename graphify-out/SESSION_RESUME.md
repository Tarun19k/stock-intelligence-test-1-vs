# SESSION_RESUME.md — GSI / AlphaVeda Workspace
# Recovery: `/chief-of-staff recover` then read this file first

**Session date:** 2026-06-20 (multi-session — Phase A/B/C complete + brand + sprint plan)
**Workspace:** stock-intelligence-test-1-vs (GSI → now AlphaVeda)

---

## DO NOT REDO — Already completed this session

1. **NPS + ELSS ambiguity RESOLVED** — Tarun confirmed: ADDITIONAL to ₹17L, not within it. Total wealth = ₹21.1L. Bucket architecture holds. ₹17L is clean liquid investable corpus.

2. **Phase B council COMPLETE** — Conditions 2 + 4 resolved:
   - Lynch (Condition 2): 6-category stock classification schema + `is_psu BOOLEAN` flag. Enum: `FAST_GROWER, STALWART, SLOW_GROWER, CYCLICAL, TURNAROUND, ASSET_PLAY`. Auto-suggest logic defined (EPS CAGR thresholds, sector triggers, P/B for asset plays).
   - Buffett + Munger (Condition 4): 9-field fundamental layer (hard ceiling enforced by Munger). Fields: roic, fcf_yield, revenue_cagr_3yr, operating_margin, promoter_pledge_pct, promoter_holding_pct (Tier 1) + pe_ttm, debt_to_equity, capex_intensity (Tier 2). `fundamentals_as_of DATE NOT NULL` + `source TEXT NOT NULL` mandatory per Munger.

3. **ALL 7 CONDITIONS RESOLVED** — Build is fully unblocked.

4. **Product name confirmed: AlphaVeda** — New repo to be created (not the GSI repo). Name etymology: Alpha (excess returns above benchmark, first/leading) + Veda (Sanskrit: to know, ancient wisdom).

5. **Brand brief complete** — Full brand identity document at:
   - `docs/brand/alphaveda-brand-brief.md` (source)
   - `docs/brand/alphaveda-brand-brief.html` (rendered one-pager, open in browser)
   - Tagline: "Know before you act." (sub: "Ancient wisdom. Modern signals.")
   - Colors: Deep Indigo #1A1F3C + Warm Ivory #F5F3EC + Saffron Gold #E8A020
   - Typography: Fraunces (headings) + DM Mono (data) + Inter (prose)
   - Logo: Yantra Mark (Concept A, recommended for launch)
   - Lead attribute: Precise (non-negotiable)
   - SEBI anchor: "AlphaVeda illuminates the data. You drive the decision."
   - Persona: Arjun, 34, Bengaluru, ₹5L-₹30L portfolio, 4 browser tabs open

6. **C1-C4 environment confirmed:**
   - C1: Supabase CLI 2.104.0 ✓ (using `supabase start` local)
   - C2: Python 3.14.3 ✓ (pandas/numpy/streamlit wheel-tested, all clean)
   - C3: New repo = `alphaveda` (pending creation)
   - C4: Node v20.12.1, npm 10.5.0 ✓

7. **Q1/Q2/Q3 architecture decisions locked:**
   - Q1 (ingest): Option D — Hybrid. GHA cron 5:45 PM IST weekdays (+ NSE holiday guard) + lazy fallback on app startup.
   - Q2 (environments): Parallel local (localhost:54321) + Supabase cloud (ap-south-1) from Day 1. Cut local once G2 stable.
   - Q3 (historical depth): OHLCV 3yr · Fundamentals 5yr (20 quarters) · Macro 5yr (60 months). ~83 MB total, fits free tier.

8. **Local-first data architecture confirmed:**
   - AlphaVeda queries ONLY local Supabase at runtime. No external API calls in app layer.
   - Ingest scripts (GHA cron) write to Supabase. App reads from Supabase. Sources never hit at query time.

9. **EODHD replaced by free BSE stack:**
   - Promoter pledge % + holding %: BSE Shareholding API (official, quarterly, primary source)
   - Revenue, margins, cash flows: BSE Quarterly Results (XBRL)
   - ROIC, FCF yield, capex intensity: Calculated from BSE filings via `scripts/calculate_fundamentals.py`
   - P/E TTM, D/E: yfinance SYMBOL.NS (personal) → FMP $14/mo (commercial)
   - Non-India OHLCV: yfinance (personal) → Financial Modeling Prep (commercial, $14/mo)
   - EODHD cost eliminated: ₹0 at personal use, ₹1,200/mo at first subscriber

10. **6-migration schema designed** — See `docs/alphaveda-sprint-plan.md` for full SQL:
    - 0001: instruments (ticker, exchange, Lynch classification, is_psu)
    - 0002: ohlcv (daily OHLCV + source + ingested_at, unique ticker+date index)
    - 0003: fundamentals (9 fields + source NOT NULL + fundamentals_as_of NOT NULL)
    - 0004: macro_regime (PMI + RBI + CPI, unique partial index on current_regime)
    - 0005: portfolio_buckets (4-bucket Dalio design)
    - 0006: trade_outcomes (Quarter Kelly tracking, empty at G0)

11. **DataProvider ABC designed** — `CommercialLicenseError` raised when `ALPHAVEDA_COMMERCIAL=true` and provider is unlicensed. Provider routing by exchange column. yfinance blocked in commercial mode.

12. **Strategic analysis complete** — 6-framework run. Key findings:
    - Commitment trap: yfinance has no enforcement gate (fixed: CommercialLicenseError)
    - Weakest pillar: Enforcement (0 tests at G0 start — fixed: pytest scaffold mandatory)
    - Misclassified action: Stream A treated as Persuade, should be Enforce (ship it)
    - Integrity violation: EODHD accepted without checking BSE primary source (fixed)

13. **10-day sprint plan complete** — at `docs/alphaveda-sprint-plan.md`:
    - Sprint 0 (Day 1): Stream A Gumroad launch — highest leverage, Tarun action
    - G0 (Day 2-3): Repo + 6 migrations + providers + ingest + pytest
    - G1 (Day 4-5): Streamlit app shell + real data + self-use test
    - G2 (Day 6-8): Auth + cloud deploy + waitlist form + beta invite
    - Checkpoint (Day 9-10): Revenue count + beta feedback
    - Revenue goal: ≥1 Stream A sale by Day 3 · ≥1 beta user by Day 7

14. **Revenue clock reset: 21 days → 10 days.** New deadline: 2026-06-30.

15. **Memory updated:**
    - `project_gsi_bucket_architecture.md` — NPS/ELSS ambiguity resolved (additional)
    - `project_alphaveda_sprint.md` — new file, 10-day sprint state
    - `MEMORY.md` — index updated

---

## EXACT RESUME POINT

**Where we stopped:** Sprint plan complete, housekeeping checkpoint in progress.

**NEXT ACTION — SPRINT 0 (Day 1) — Tarun:**
1. Stream A: Gate 3 fix (CoS, 30 min) → Gumroad listing creation (Tarun, 30 min) → launch post (Tarun, 30 min)
2. This is the ONLY action that generates revenue in the next 48 hours
3. After Stream A is listed: CoS begins G0 (alphaveda repo creation → migrations → providers)

**SPRINT 0 tasks by owner:**
| Task | Owner | Effort |
|---|---|---|
| S0-1: Fix Gate 3 in Governance Pack README | CoS | 30 min |
| S0-2: Gumroad listing copy review | CoS | 20 min |
| S0-3: Create Gumroad product ($49/$99/$149) | Tarun | 30 min |
| S0-4: Launch post (LinkedIn + X) | Tarun | 30 min |

**G0 starts after Sprint 0 is live.**

---

## 7 PRE-BUILD CONDITIONS — ALL RESOLVED ✓

| # | Condition | Status |
|---|---|---|
| 1 | Data source architecture | ✓ Bhavcopy + yfinance + BSE + FMP three-tier |
| 2 | Stock classification schema | ✓ Lynch 6-enum + is_psu BOOLEAN |
| 3 | Bucket architecture | ✓ 4-bucket ₹17L design |
| 4 | Fundamental data layer | ✓ 9 fields, Munger ceiling, BSE as primary source |
| 5 | Macro regime classifier | ✓ PMI + RBI/CPI semi-manual, current: RISK_ON |
| 6 | SEBI compliance | ✓ Analytics framing, RIA at first payment |
| 7 | Position sizing | ✓ Quarter Kelly, portfolio_value = ₹7.25L |

---

## OPEN DECISIONS (Tarun-owned)

| Decision | Default if no answer | Needed by |
|---|---|---|
| AlphaVeda pricing: ₹999/mo or tiered? | ₹999/mo single tier | Sprint 3 (Day 6-8) |
| Custom domain? (alphaveda.in?) | Streamlit subdomain for now | Sprint 3 |
| Stream C consulting: who are the 3 outreach targets? | Tarun identifies | Day 1-2 |
| Stream A Gate 6: Tarun final sign-off on Gumroad listing | Required before listing | Sprint 0 |

---

## COMMERCIAL STATE

- **Stream A (Gumroad Governance Pack):** SPRINT 0 — list on Day 1. OVERDUE. Gate 3 (README fix) = only remaining blocker from CoS side.
- **Stream C (Financial consulting):** Available now, no code needed. 3 outreach targets needed from Tarun.
- **Stream D (AlphaVeda):** G0 starts after Sprint 0. First beta user target: Day 7. First subscriber: Day 10+.
- **Stream B (YarnZoo):** Deferred — out of 10-day scope.
- **Revenue clock:** 10 days remaining (deadline 2026-06-30).

---

## KEY ARTIFACTS THIS SESSION

| Artifact | Location | Status |
|---|---|---|
| Brand brief (Markdown) | `docs/brand/alphaveda-brand-brief.md` | Committed |
| Brand brief (HTML) | `docs/brand/alphaveda-brand-brief.html` | Committed |
| Sprint plan | `docs/alphaveda-sprint-plan.md` | Committed |
| Session resume | `graphify-out/SESSION_RESUME.md` | This file |
| Memory: bucket architecture | `~/.claude/projects/.../memory/project_gsi_bucket_architecture.md` | Updated |
| Memory: sprint state | `~/.claude/projects/.../memory/project_alphaveda_sprint.md` | New |

---

## PARALLEL SESSION NOTE

Stream A (Governance Pack) has its own session history. Do not conflate with AlphaVeda. Sprint 0 cross-references Gate 3 fix from Stream A session.

---

## PRIOR SESSION STATE (preserved — do not redo)

### 2026-06-19 RAG GATEWAY + SYSTEMS ANALYSIS — COMPLETE
- RAG Gateway P0 fully built: `~/.claude/scripts/rag-gateway.sh` (three-tier routing)
- G3 fix done: dispatch table row in research-development skill
- Systems analysis complete: G1-G4 feedback loop gaps mapped
- Phase plan: P1 session-start-reader → P2 respond signals → P3 JSONL watcher

### 2026-06-19 PHASE A COUNCIL COMPLETE
- Condition 1: Bhavcopy + yfinance + EODHD (now updated: EODHD → BSE free stack)
- Condition 5: PMI + RBI/CPI macro regime, semi-manual monthly
- Condition 6: SEBI compliance, analytics framing, RIA at first payment
- Condition 7: Quarter Kelly + hard caps (10% max, 1% min, 35% sector, 10% cash floor)

### 2026-06-18 INFRASTRUCTURE SPRINT — COMPLETE
- Housekeeping skill built
- Stop hook #7 added (housekeeping-stop-hook.sh)
- Council briefing HTML built
- Haiku review gate established

### PRIOR WORK (session 2026-06-16 → 2026-06-18)
- 7-seat full council: 7 REVISE verdicts (do not re-run)
- 28-requirement inventory: complete (do not rebuild)
- Strategic analysis: CONSOLIDATE posture (still valid)
- RAG gateway: live (commit 4eb2188)
