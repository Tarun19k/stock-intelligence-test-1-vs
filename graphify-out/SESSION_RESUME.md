# SESSION_RESUME.md — GSI / AlphaVeda Workspace
# Recovery: `/chief-of-staff recover` then read this file first

**Session date:** 2026-06-21 (continued — readiness check + AWS + artifacts + strategic analysis)
**Previous session:** 2026-06-20 (Phase A/B/C complete + brand + sprint plan)
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

## DO NOT REDO — Session 2026-06-21 additions

16. **Q2 CHANGED: Cloud-only confirmed.** Docker not installed, no plan to install. Supabase cloud ap-south-1, free tier. Supersedes "parallel local + cloud". Locked permanently.

17. **AWS dev account confirmed clean.** Screenshot reviewed — 0 services, 0 spend. Pre-July 2025 legacy account. Always-free Lambda + EventBridge + CloudWatch + S3 covers all AlphaVeda ops at $0.00. Use `ap-south-1` region.

18. **Salesforce dev org scoped.** Stream C consulting CRM only (3 outreach targets, call notes). Not AlphaVeda infrastructure.

19. **Claude Code Artifacts education complete.** Launched June 18, 2026. Beta — Team/Enterprise only. CSP: inline CSS/JS, no external calls, 16MB cap. Plan-agnostic skill created: `~/.claude/skills/alphaveda-artifacts/SKILL.md`. 4 artifact types: sprint-status, schema-viewer, data-flow, session-checkpoint. First committed at `31154ff`.

20. **G0-25 (historical ingest) removed from G0 exit gate.** One-time local script, run before G1. G0 exit = schema + 10 seeds + pytest 6/6 only.

21. **G0.5 added to sprint plan.** AWS Lambda + EventBridge + CloudWatch + S3. Between G0 and G1. Replaces GHA as primary ingest. SES production access: file request 48hr before first waitlist email.

22. **NSE/BSE User-Agent requirement confirmed.** Both return 200 only with browser User-Agent header. All HTTP fetches in BhavcopyCProvider must include `headers={"User-Agent": "Mozilla/5.0 ..."}`. Must be in base DataProvider class.

23. **G0 readiness check complete — 7/7 panel PROCEED.** 3 P0 blockers: pip packages (supabase, postgrest, pandas_market_calendars), Supabase cloud project (Tarun action), NSE User-Agent fix (CoS action at G0-12).

24. **Strategic analysis complete (2026-06-21).** Posture: OFFENSIVE with Enforcement repairs. Weakest pillar: Enforcement (2/5). S0 = LATE. Stream C = now ENFORCE. Graph needs own repo. 5 graph enhancements documented. Restructured timeline in EXACT RESUME POINT above.

25. **Graph enhancement plan (5 items).** E1: alphaveda repo = separate graph. E2: Indian Market as anchor node. E3: docs/architecture.md at G0. E4: Quarter Kelly as queryable node. E5: SEBI compliance as queryable community.

26. **Memory updated 2026-06-21:**
    - `project_alphaveda_sprint.md` — Q2 cloud-only, restructured sprint status, AWS + Salesforce decisions, G0-25 out of exit gate
    - `reference_alphaveda_artifacts.md` — new file, artifacts skill reference
    - `MEMORY.md` — index updated with artifacts entry, alphaveda sprint description updated

---

## ARTIFACTS

| Type | Path | Generated |
|---|---|---|
| sprint-status | docs/artifacts/2026-06-20/sprint-status.html | 2026-06-20 |
| session-checkpoint | docs/artifacts/2026-06-21/session-checkpoint.html | 2026-06-21 |

## EXACT RESUME POINT — UPDATED 2026-06-21

**Where we stopped:** Housekeeping + bookkeeping complete. G0 fully designed, blocked on 2 Tarun P0 actions.

**NEXT ACTION — P0 (TODAY) — Tarun:**
1. Create Supabase cloud project at supabase.com → region: ap-south-1 → free tier → share SUPABASE_URL + ANON_KEY + SERVICE_KEY
2. Run: `pip install supabase postgrest pandas_market_calendars`
3. Stream A (Gumroad) is in a SEPARATE session — do not block G0 on it

**After P0 confirmed → CoS begins G0 immediately (no further input needed from Tarun until G0 design review).**

**RESTRUCTURED SPRINT TIMELINE (updated 2026-06-21):**
| Phase | Status | Days | Key gate |
|---|---|---|---|
| S0 — Stream A | LATE — separate session | — | CoS owns S0-1/S0-2; Tarun owns S0-3/S0-4 |
| P0 — Pre-build fixes | PENDING Tarun | TODAY | Supabase cloud + pip install |
| G0 — Foundation | READY* after P0 | Day 1-2 | pytest 6/6 + schema applied + 10 seed instruments |
| G0.5 — AWS layer | PLANNED | Day 2-3 | Lambda + EventBridge + CloudWatch + S3 |
| G1 — App shell | PLANNED | Day 3-4 | Tarun self-use test 30min |
| G2 — Auth + deploy | PLANNED | Day 5-7 | SES production access filed 48hr before email |
| RC — Revenue check | PLANNED | Day 8-9 | Sales count + beta feedback |

**S0 is in a SEPARATE session. G0 starts after P0 fixes, not after S0.**

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
