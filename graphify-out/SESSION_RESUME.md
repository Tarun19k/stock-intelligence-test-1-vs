# SESSION_RESUME.md — AlphaVeda Workspace
# Recovery: `/chief-of-staff recover` then read this file first

**Session date:** 2026-06-28 (G0 cleared + live preview confirmed · Test suite 186 PASS / 2 SKIP / 0 FAIL)
**Workspace:** stock-intelligence-test-1-vs (GSI → AlphaVeda MVP build)
**Last commits:** abb3990 (SESSION_RESUME G0 update), 269fb2d (G0 cleared), 0810379 (migration 0015 + data_viewer fix)

---

## DO NOT REDO — Session 2026-06-28 (G0 cleared + live preview)

### app.py: load_dotenv() added for Streamlit startup (uncommitted → commit this checkpoint)
- `src/app.py`: added `load_dotenv()` at module top using dotenv + os.path relative to file
- Same pattern as `scripts/ingest.py` — harmless in GHA (env vars pre-set there)
- Without this: Streamlit throws "SUPABASE_URL not set" on first render
- Pattern: `load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"), override=False)`

### Live App Preview Confirmed (2026-06-28, Playwright screenshots)
- All 4 pages rendered correctly: Market Data / Signals / Path / Accuracy Ledger
- Design system fully applied: indigo dark shell, gold brand mark, SEBI footer pinned
- Market Data: Imran staleness banner firing correctly ("hasn't updated since 2026-06-25")
- Signals/Path/Accuracy: correct cold-start empty states, SEBI disclaimer visible
- Minor UI note: Streamlit MPA sidebar links (app/accuracy/data viewer/path/signals) visible above custom radio nav — CSS rule to hide not firing in this session. UI-2 polish item, not a blocker.

### Lynch Strategy + Expert Panel Explanation Delivered
- Honest answer documented: 14 stocks = G0 test seed (not screened portfolio)
- Selection criteria: appear in NSE Bhavcopy EQ-series, cover all 6 Lynch classifications, count ≥10
- Expert voices grounded in actual code: COLD_START_WEIGHTS, constants.py constants, engine.py pipeline
- Per-expert mapping: Lynch (classification weights), Buffett (FUNDAMENTAL_WEIGHT_FLOOR=0.30), Soros (STREAK_DISCOUNT_FACTOR=0.7), Munger (PROPOSAL_MIN_DELTA=0.03), Dalio (REGIME_STALENESS_DAYS=3), Marks (VIX_CALM_THRESHOLD=18.0), Druckenmiller (QUARTER_KELLY_FRACTION=0.25, PORTFOLIO_VALUE=725000)

### G0 Live Ingest Pipeline CLEARED (Commit 269fb2d) — 186 PASS / 2 SKIP / 0 FAIL
- Instruments seeded: 14 NSE stocks × 6 Lynch classifications (all 6 covered)
- First live ingest: 2026-06-25 → 13 OHLCV rows written, status=OK
- 6 pipeline bugs fixed (see commit message for full list):
  1. bhavcopy.py: certifi SSL for NSE CDN
  2. bhavcopy.py: CSV header whitespace (NSE "SYMBOL, SERIES," format)
  3. bhavcopy.py: column names OPEN_PRICE/HIGH_PRICE/LOW_PRICE/CLOSE_PRICE/TTL_TRD_QNTY
  4. ingest.py: instrument resolution — fetch all seeded (not .in_() with 2669 tickers — URL limit)
  5. ingest.py: DB column `trade_date` (not `as_of`) + conflict target
  6. ingest.py: DB column `direction` (not `signal_direction`) in accuracy_predictions
  7. test_council_conditions.py: `last_run` (not `run_at`) — migration 0015 rename
  8. migration 0016: VARCHAR(20) for ingest_status.status (SKIPPED_HOLIDAY = 15 chars)
- G0 gate tests: 12/12 PASS

### Council Review — 4-Seat Audit of Phases 1–6 (Session 2026-06-27)
- Shakuni/Red Team, Constraint Enforcer, SRA/Reliability Architect, Synthesis Chair
- 8 specific findings from direct code inspection; RAG: 3 RED / 8 AMBER / 9 GREEN
- All 3 RED items already resolved in commit e35fd0e BEFORE this conversation's review output
- Artifacts committed: sprint-status.html + session-checkpoint.html (4ec7392)
- NOTE: artifacts reflect pre-fix state — test suite was 179/1/3 at time of generation; actual current state is 182/2/4

### Pre-G0 Hardening — All 3 RED Council Items Fixed (Commit e35fd0e)
- ingest.py step 5: N+1 ohlcv queries → single batch query (SRA R-02)
- ingest.py step 6: per-row insert() → batch upsert() on conflict (prediction_id, resolved_at) (S-01/R-03)
- migration 0014: unique constraint on accuracy_outcomes(prediction_id, resolved_at)
- conftest.py: GOVERNANCE_STRICT=1 set at module level, not in fixture (S-03)
- DATA_SOURCES.md: circuit_flag exclusion documented as IMPLEMENTED (C-01)
- test_g0_gate.py: test_c10_ohlcv_has_rows added — closes fake-OK-row loophole (S-02)
- Additional: review banner tightened (C-04), dead ALPHAVEDA_COMMERCIAL_ENV_KEY removed (C-02)
- Additional: test_floor_enforced_at_emit GREEN, test_regime_cached GREEN, test_stale_regime_fails_visibly GREEN
- Suite state after: 182 PASS / 2 SKIP / 4 FAIL (4 FAILs = intentional G0 seed gates)

### Stream 0 — Housekeeping COMPLETE (Commit 93e3140)
- SESSION_RESUME.md checkpoint (2026-06-27) 
- Graph rebuild triggered (auto-hook)

### Stream 2 — Global CLAUDE.md Rules B/C COMPLETE (Commit 76ade56)
- Rule B: Seat registration requirement (INADMISSIBLE verdict for unbacked seats)
- Rule C: Zero-assumption tolerance (dispatch prompts must reference SKILL.md)
- Post-compaction anchor: `/chief-of-staff recover` → SESSION_RESUME.md before new work
- 126 lines (under 130-line threshold); premortem logged: window-8671-2026-06-27

### Stream 1 — AlphaVeda MVP Specification COMPLETE (Commit ac9775d)
- `docs/MVP_SPEC.md` — 6 capabilities, 3 personas, UI-2 page briefs for all 4 pages
- State map: cold-start/empty/staleness/suppression/circuit-locked
- SEBI compliance summary (Varghese 7 checks all pass)
- Definition of MVP complete (single blocker: G0 seed)

### Stream 3 — Phase 7 Expert Planning Council COMPLETE (Commit c1eacbe)
- `docs/plans/PHASE7_BRIEF.md` — 215 lines, DRAFT status
- Architecture: Next.js on Vercel + FastAPI on Railway (hybrid)
- 3-session sprint structure; top-5 risk register; token budgets
- Council verdict: APPROVED WITH CONDITIONAL (SRA's FM-01/02/05 must be designed before Phase 7 build)
- Gate: no Phase 7 action until Tarun says "PHASE7_BRIEF APPROVED"

### Stream 4 — Memory + Graph Update COMPLETE (Commit e0464aa)
- Updated `project_alphaveda_sprint.md` — Phases 1–6 + UI-1 done
- Updated `project_alphaveda_governance_rules.md` — Rules B/C LIVE
- New `project_phase7_planning.md` — Phase 7 architecture + effort
- Updated MEMORY.md index — 3 entries
- Graph update queued (auto-hook)

### UI-1 Design System COMPLETE (Commit f36e6c9)
- `src/styles.py`: CSS tokens (--indigo/--gold/--emerald/--terra/--ivory), Google Fonts (Fraunces/DM Sans/DM Mono),
  sidebar brand mark, signal card component HTML, SEBI footer bar (.av-sebi-footer), metric/button/input overrides
- `src/app.py`: CSS injected before content via get_css(); SEBI footer migrated from inline yellow → design system class
- `tests/test_app.py`: disclaimer test tightened (Varghese Check 7 — asserts absence of onclick/button/dismiss)
- `COUNCIL_RULES.md`: all 3 missing seats now skill-backed — circuit-microstructure-reviewer / data-licence-compliance-reviewer / sebi-compliance-reviewer

### Skills created (global ~/.claude/skills/)
- `circuit-microstructure-reviewer` — Jhunjhunwala seat (7 microstructure checks)
- `data-licence-compliance-reviewer` — Bhattacharya seat (7 licensing checks)
- `sebi-compliance-reviewer` — Varghese seat (7 SEBI compliance checks)
- All 3 pass `check-seat-skill.sh` dispatch gate

### skills-index.md updated
- Added calibration-integrity, ui-ux-pro-max, 3 new council skills — all registered

### Phase 6 (GHA Ingest Pipeline) COMPLETE — 179 PASS / 1 SKIP / 3 FAIL (Commit f978fc5)
- All 4 council REVISE fixes implemented: Tanvi/Imran/Rashida/Reddy
- circuit_flag end-to-end: proxy detection in parser, exclusion in resolve_outcomes
- Holiday gate (NSE trading calendar), empty-day (NO_DATA status), staleness banner wired
- BULL/BEAR direction enum (not BULLISH/BEARISH)
- Stale test un-skipped (Imran condition)
- Schema contract alignment: ingest_status columns, ohlcv instrument_id resolution, accuracy_outcomes write path
- G0 blocked only on live DB seed (first `python3 scripts/ingest.py` run against seeded Supabase)

### Council Seat Infrastructure — Rules + Skills (Commit 0282c4c)
- Skill confidence check: 5 seats without SKILL.md found (Rashida, Reddy, Jhunjhunwala, Bhattacharya, Varghese)
- Created `calibration-integrity/SKILL.md` (new skill, Reddy seat)
- Enhanced `doctrine-panel-constraint-enforcer/SKILL.md` with DB Integrity Extension (Rashida seat)
- Renamed 4 seats to canonical names: Tanvi→UX/Accessibility, Imran→SRA/Reliability Architect, Rashida→DB Integrity, Reddy→Calibration Integrity
- Created `alphaveda/.claude/rules/COUNCIL_RULES.md` (Rules A/B/C: dispatch gate, seat registry, zero-assumption)
- Created `~/.claude/scripts/check-seat-skill.sh` (verification hook)
- Phase 6 sign-off entry in COUNCIL_TEST_MAP.md (all 21 seats resolved, Wave 1+2 verdicts)
- Governance root-cause investigation: unmapped seats, no dispatch-time validation gate (systemic, not one-time)

### 1. Governance Housekeeping + Artifact Automation (Commits 9fa257f, eb95e91, b52381b)
- GROUP A/B/C housekeeping complete — zero governance warnings
- Artifact workflow system built: 3 generators, 5-seat council review, GHA trigger
- Result: 73 PASS / 17 SKIP / 3 FAIL after Groups A-C

### 2. Phase 3 Signal Layer COMPLETE (Commit ea270a5) — 107 PASS
- ledger.py (compute_streak_flag), downside.py (ATR/price), arbitration.py, weights.py, engine.py
- Soros pipeline contract enforced: streak discount fires step 3b BEFORE calibration

### 3. Phase 3 Council Sign-Off COMPLETE (Commit f444ec1) [council:subagent]
- Soros: APPROVE, Druckenmiller: APPROVE, Shakuni: REVISE → resolved
- Shakuni blockers fixed: approve_signal_weight() C1, weight range validation C2, KeyError safety C3, FUNDAMENTAL_WEIGHT_FLOOR on DB path C4, ARBITRATION_MARGIN pin C5
- Result after fixes: 112 PASS / 15 SKIP / 3 FAIL

### 4. Phase 4 Portfolio Layer + Circuit Flag Fix (Commits de5fa22, 9537131)
- `src/portfolio/optimizer.py`: kelly_position_size() + should_exit_e1/e2/e3/e4()
  - Kelly formula CORRECT: b = magnitude_target / downside_target (GAP-001 fixed)
- `src/portfolio/buckets.py`: VALID_BUCKETS, validate_bucket_type(), e2_threshold()
- Jhunjhunwala fix: circuit_flag rows excluded INSIDE compute_downside_target() — 4 tests added

### 5. Phase 4 Council Sign-Off COMPLETE (Commit 6d34e67) [council:subagent]
- Druckenmiller: APPROVE — Kelly correct, all exit rules sound
- Jhunjhunwala: REVISE → APPROVE — circuit_flag filter, 132 PASS / 12 SKIP / 3 FAIL

### 6. Phase 5 Presentation Layer COMPLETE (Commits b09a0a5, 0892867) [council:subagent]
- `src/app.py`: Streamlit entry, get_disclaimer_html() always returns full SEBI_DISCLAIMER
- `src/pages/data_viewer.py`, `signals.py`, `path.py`, `accuracy.py`
- 12 tests GREEN (test_app.py)
- Munger REVISE resolved: accuracy.get_proposed_weights_count() → delegates to signals (single source of truth)
- Council sign-off: Varghese APPROVE, Constraint Enforcer APPROVE, Tanvi Rao APPROVE, Munger REVISE→APPROVE
- Final state: 144 PASS / 12 SKIP / 3 FAIL

---

## EXACT RESUME POINT

**COUNCIL DECISIONS LOGGED 2026-06-30. Session A BUILT + parked (Fly.io deploy deferred to Session C). FM-02 Layer 2 revised (Vercel env var, Varghese APPROVED). Directory: alphaveda/web/. Session B unblocks after Tarun completes 3 Vercel setup actions (no CLI needed).**

| Item | Status | Detail |
|---|---|---|
| Phases 1–6 + UI-1 | ✓ SIGNED OFF | f978fc5 / f36e6c9 |
| Rules B/C → CLAUDE.md | ✓ DONE | 76ade56 |
| MVP Spec | ✓ DONE | ac9775d |
| Phase 7 Brief | ✓ DONE | c1eacbe |
| G0 — Live DB Seed | ✓ CLEARED | 269fb2d — 14 instruments, 13 OHLCV rows, 186 PASS |
| Phase 7 APPROVED | ✓ APPROVED | Tarun approved 2026-06-28 |
| SRA FM-05 | ✓ RESOLVED | G0 cleared 2026-06-28 |
| SRA FM-01 | ✓ ELIMINATED | Fly.io auto_stop=false — no cold-start, no GHA cron needed |
| SRA FM-02 design | ✓ DESIGNED | Root layout + backend envelope + Playwright CI gate |
| GHA ingest zero-row alert | ✓ DONE | Step added to ingest.yml — no new workflow |
| Notion Product Hub | ✓ CREATED | 27 tasks — https://app.notion.com/p/38d648bc8b1b8154bb38f84753045675 |
| Session A — api/ built | ✓ BUILT | api/main.py + 5 routes + Dockerfile + fly.toml + tests/test_api.py |
| Session A — fly deploy | DEFERRED → Session C | Council 2026-06-30: Session B uses Supabase direct, no FastAPI needed |
| Directory structure | ✓ DECIDED | alphaveda/web/ for Next.js (inside alphaveda/, Vercel root = alphaveda/web) |
| FM-02 Layer 2 revised | ✓ APPROVED | Varghese + SRA: Vercel env var replaces FastAPI fetch; build-time enforcement |
| Session B — Next.js | NOT STARTED | Unblocks after Tarun completes 3 Vercel setup actions |

**Fly.io usage tracking:**
- Dashboard: fly.io → Billing → Usage (check weekly)
- Trial: $5 one-time credit, no free allowances
- 256MB machine: ~$2.02/month → ~2.5 months runway on trial
- Add credit card before credit depletes to prevent service shutdown
- Scale if OOM: `fly scale memory 512` (~$3.32/month)

**Tarun — Session A deploy (DEFERRED to Session C gate — not needed for Session B):**
1. `brew install flyctl` → `fly auth login`
2. `fly apps create alphaveda-api` (from alphaveda/ directory)
3. `fly secrets set SUPABASE_URL=<url> SUPABASE_SERVICE_KEY=<key>`
4. `fly deploy` (from alphaveda/ directory)

**Tarun — Session B gate (3 actions, ~10 minutes):**
1. Create Vercel account → import `stock-intelligence-test-1-vs` repo
2. Set root directory to `alphaveda/web` in Vercel project settings
3. Set 3 env vars in Vercel → Settings → Environment Variables:
   - `SUPABASE_URL` = your Supabase project URL
   - `SUPABASE_SERVICE_KEY` = your Supabase service role key
   - `SEBI_DISCLAIMER` = (copy exact text from alphaveda/src/constants.py)

**Tarun — Session C gate (defer until first subscriber is 2 weeks out):**
4. Enable Supabase Auth on `kowlkczswaglbmabygtl`
5. Fly.io deploy (items 1–4 above)

**Remaining AMBER (NOT blocking — G1 scope):**
- Outcome scoring horizon: all predictions scored on day 1 (R-01)
- approve_signal_weight route-level auth guard — Phase 7 Session C (S-08)
- calibrate_confidence warm/cold paths identical — flag before Platt scaling (S-04)
- GHA ingest zero-row alert: NOW DONE (step added to ingest.yml)

---

## OPEN DECISIONS (Tarun-owned)

| Decision | Status | Impact | Needed by |
|---|---|---|---|
| Stream A (Gumroad Governance Pack): publish | OVERDUE | $0 → first revenue | NOW |
| Stream C: 3 consulting targets | OVERDUE | Revenue clock | NOW |
| G0 seed: run ingest.py against live Supabase | ✓ DONE | Cleared 2026-06-28 (269fb2d) | — |
| Phase 7 APPROVED | ✓ DONE | Approved 2026-06-28, plans written, Notion hub live | — |
| Railway account + CLI (Tarun Pre-work) | PENDING | Blocks Session A build | Before Session A |

---

## COMMERCIAL STATE — Updated 2026-06-27

- **Stream A:** READY_TO_LIST. All 6 PRG gates PASS. Tarun to publish. REVENUE BLOCKER.
- **Stream C:** OVERDUE. 3 consulting targets needed. No code required.
- **Stream D (AlphaVeda):** Phases 1–6 + UI-1 done. G0 blocked. Phase 7 (Vercel hybrid) being scoped.
- **Stream B:** Deferred — out of 21-day scope.

---

## BLOCK SEQUENCE — LIVE STATUS

| Block | Status | Commit | Notes |
|---|---|---|---|
| Phase 1 (Foundation) | ✓ SIGNED OFF 2026-06-23 | 1ae8e37 | |
| Phase 2 (Data layer) | ✓ SIGNED OFF 2026-06-23 | ce9cba9 | |
| Phase 3 (Signal layer) | ✓ SIGNED OFF 2026-06-25 | f444ec1 | |
| Phase 4 (Portfolio layer) | ✓ SIGNED OFF 2026-06-25 | 9537131 | |
| Phase 5 (Presentation) | ✓ SIGNED OFF 2026-06-25 | 0892867 | |
| Phase 6 (GHA ingest) | ✓ SIGNED OFF 2026-06-26 | f978fc5 | 179 PASS; all 21 seats resolved |
| G0 Gate | ✓ CLEARED | 269fb2d | 14 instruments seeded; 13 OHLCV rows; 186 PASS |
| UI-1 (CSS + nav) | ✓ COMPLETE | f36e6c9 | Design system; signal card; SEBI footer |
| Railway deployment config | NOT STARTED | — | 30 min; approved per council |
| Rules B/C → CLAUDE.md | APPROVED | — | Premortem + write (next stream) |
| UI-2 (page content) | QUEUED | — | Apply tokens to 4 page modules |
| Phase 7 (Next.js/Vercel hybrid) | PLANNING | — | Council convening this session |

---

## TEST SUITE STATE PROGRESSION

| Milestone | PASS | SKIP | FAIL | Notes |
|---|---|---|---|---|
| After Phase 3 sign-off | 112 | 15 | 3 | Shakuni REVISE resolved |
| After Phase 4 sign-off | 132 | 12 | 3 | Jhunjhunwala REVISE resolved |
| After Phase 5 sign-off | 144 | 12 | 3 | Munger REVISE resolved |
| After Phase 6 sign-off | 179 | 1 | 3 | All 4 REVISE seats resolved; 3 FAIL = intentional G0 seed gates |
| After UI-1 (design system) | 179 | 1 | 3 | No change — CSS/styles.py adds no new tests |

---

## GOVERNANCE BACKLOG

- Rules B+C to global CLAUDE.md — **APPROVED 2026-06-27** (Tarun). Premortem + write next.
- Refactor `alphaveda/scripts/council_review.py` — inline seat logic → SKILL.md references (Phase 7 scope)
- `test_disclaimer_non_dismissable`: now checks for absence of onclick/button/dismiss (Varghese Check 7 tightened)

## PHASE 7 PLANNING — MOBILISED 2026-06-27

**Council recommendation (session 2026-06-27):** Hybrid architecture — Next.js on Vercel + FastAPI on Railway.
**Effort estimate:** 8–12 hours, 2–3 sessions, ~55,000 Sonnet tokens.
**Prerequisite:** G0 seed must pass before Phase 7 build begins.
**Expert council convening this session (background):** SRA + Constraint Enforcer + Revenue + Synthesis Chair.
- Create 3 missing skills: Jhunjhunwala (circuit microstructure), Bhattacharya (data licence), Varghese (SEBI compliance)

---

## PHASE 5–6 NON-BLOCKING ITEMS (carry to UI polish)

- Varghese (SEBI): `test_disclaimer_non_dismissable` fallback `or "not" in html.lower()` too permissive — tighten to specific phrase
- Constraint Enforcer: path.py calls is_commercial() twice per render (get_kelly_display_data + render()) — consider caching at G1
- UX/Accessibility: cold-start label uses "Bayesian priors" — accessible language pass needed before public launch
- UX/Accessibility: cold-start label notes operational cause (observation count) but not implication (lower confidence)

---

*Updated: 2026-06-28 — Phase 7 APPROVED. Notion hub live (27 tasks). SRA FM-01/02/05 designed. Blocked only on Tarun Pre-work (Railway + Vercel accounts + CLIs).*

---

## ARTIFACTS

| Type | Path | Generated | Commit |
|---|---|---|---|
| sprint-status | alphaveda/docs/artifacts/2026-06-27/sprint-status.html | 2026-06-27 | 4ec7392 |
| session-checkpoint | alphaveda/docs/artifacts/2026-06-27/session-checkpoint.html | 2026-06-27 | 4ec7392 |
| mvp-spec-visual | alphaveda/docs/artifacts/2026-06-27/mvp-spec-visual.html | 2026-06-27 | be40071 |
| Session A Brief | alphaveda/docs/plans/PHASE7_SESSION_A_BRIEF.md | 2026-06-28 | this commit |
| Design Decisions | alphaveda/docs/plans/PHASE7_DESIGN_DECISIONS.md | 2026-06-28 | this commit |
| Notion Product Hub | https://app.notion.com/p/38d648bc8b1b8154bb38f84753045675 | 2026-06-28 | online |
