# SESSION_RESUME.md — AlphaVeda Workspace
# Recovery: `/chief-of-staff recover` then read this file first

**Session date:** 2026-06-22 (council review gate + Block 0-2 + Supabase live)
**Previous session:** 2026-06-21 (design doc complete, HTML artifact, expert skills gate)
**Workspace:** stock-intelligence-test-1-vs (GSI → AlphaVeda MVP build)

---

## DO NOT REDO — Session 2026-06-22 (updated post-council)

### 1. Council Review Gate — ALL 4 QUESTIONS VOTED

11-seat council (7 investor + 4 doctrine) voted on all 4 HTML Tab 6 questions:

| Question | Verdict | Key action |
|---|---|---|
| Q1 — 9 migrations | REVISE | 4 migration fixes (B1-B4) |
| Q2 — Cold-start weights | APPROVE | 2 conditions tracked |
| Q3 — EXIT trigger E2 | REVISE | Bucket-aware thresholds + confidence floor |
| Q4 — Review banner | APPROVE | 3 additions required |

Council also produced sequenced action plan (Block 0–8).

### 2. Block 0 — Design Doc v0.3 COMPLETE (commit 0fe54b0)

All council REVISE verdicts applied to `docs/superpowers/specs/2026-06-21-alphaveda-mvp-design.md`:
- B1: outcome_id FK removed from 0007_accuracy_predictions; added via ALTER TABLE at end of 0008
- B2: UNIQUE(regime) removed from 0004_macro_regime — time-series table, same regime repeats daily
- B3: exit_trigger CHAR(2) E1-E4 added to 0006_trade_outcomes
- B4: 0010_ingest_status.sql added as new migration spec
- E2 EXIT trigger now bucket-aware: near_term=3, medium_term=5, long_term=7 consecutive BEAR signals
- E2 confidence floor ≥ 50 added (E2_CONFIDENCE_FLOOR = 50 in constants.py)
- Weight proposal banner added to pages/path.py spec
- WEIGHT_REVIEW_PROCESS.md spec added inline (quarterly, backstop 90 days, obs≥30 + delta≥3%)
- Section 1.5 (non-goals, 9 items) added by R2b
- SLAs subsection in Section 8 added by R2b (7 rows, realistic free-tier targets)

### 3. Block 2 — ALL 3 AGENTS COMPLETE (commit 252b8ac + 0fe54b0 + 8ff0364)

| Agent | Output | Commit |
|---|---|---|
| R2a (Opus) | 9 expert personas → `docs/experts/` (9 files, 366–504 words each) | 252b8ac |
| R2b (Sonnet) | Section 1.5 non-goals + SLAs added to design doc | 0fe54b0 |
| R2c (Sonnet) | `DESIGN.md` at repo root (232 lines, 15 brand tokens, 8 sections) | 8ff0364 |

### 4. Critical Schema Defect Found and Fixed (commit 252b8ac)

Found by R2a expert Deepak Nair (schema-design persona):
- **Bug:** Council B0.1 fix added UNIQUE(regime) to macro_regime to allow FK reference from accuracy_predictions. But macro_regime is a time-series table — UNIQUE(regime) caps it at exactly 4 rows total, making all ingest beyond the 4th row fail silently.
- **Fix:** UNIQUE(regime) removed. accuracy_predictions.regime_tag changed from FK to CHECK-only. Enum validation via CHECK is correct; referential integrity to a time-series table was architecturally wrong.

### 5. Supabase LIVE — alphaveda-prod ap-south-1 (commit 69e943e)

- Project: **alphaveda-prod** | Ref: **kowlkczswaglbmabygtl** | Region: ap-south-1 (Mumbai)
- Org: ferhzizogqwgdoxymgiy (Tarun19k's Org) | Plan: Free tier
- All 11 migrations applied to remote DB (verified via Supabase dashboard)
- Credentials: `.env` at workspace root (gitignored — NEVER commit)
- Credentials inventory: `docs/supabase/CREDENTIALS.md` (committed, no secrets)
- Recovery instructions: curl management API (see CREDENTIALS.md)
- Memory: `~/.claude/projects/.../memory/project_alphaveda_supabase.md`

### 6. Supabase Documentation Complete (commit 8ff0364)

| File | Lines | Contents |
|---|---|---|
| `supabase/migrations/20260621100001_instruments.sql` | — | Lynch classification NOT NULL, 6-value CHECK |
| `supabase/migrations/20260621100002_ohlcv.sql` | — | UNIQUE(instrument_id, trade_date) |
| `supabase/migrations/20260621100003_fundamentals.sql` | — | UNIQUE(instrument_id, period_end) |
| `supabase/migrations/20260621100004_macro_regime.sql` | — | regime CHECK only, NO UNIQUE (time-series) |
| `supabase/migrations/20260621100005_portfolio_buckets.sql` | — | 4 seed rows included |
| `supabase/migrations/20260621100006_trade_outcomes.sql` | — | exit_trigger CHAR(2) E1-E4, nullable |
| `supabase/migrations/20260621100007_accuracy_predictions.sql` | — | regime_tag CHECK only; no outcome_id |
| `supabase/migrations/20260621100008_accuracy_outcomes.sql` | — | ends with ALTER TABLE adding outcome_id FK |
| `supabase/migrations/20260621100009_signal_weights.sql` | — | UNIQUE(lynch_class, regime, signal_name, status) |
| `supabase/migrations/20260621100010_ingest_status.sql` | — | staleness badge backing table |
| `supabase/migrations/20260621100011_waitlist.sql` | — | price_feedback + referred_by columns |
| `docs/supabase/SCHEMA.md` | 595 | Full ERD + 11 table refs + FK map + index recommendations |
| `docs/supabase/GSI-OVERLAP.md` | — | No conflicts; only other project is Claude Observability (Tokyo) |
| `DESIGN.md` | 232 | Developer onboarding doc, 15 brand tokens, page map, data flow |

### 7. R2a Expert Findings — 5 Design Issues (input for R1)

Found while writing expert personas — not yet actioned, mandatory challenge targets for Block 3:

| # | Expert | Finding | Severity |
|---|---|---|---|
| F2 | portfolio-theory (Prof. Sanjay Iyer) | `magnitude_target` used as Kelly odds `b` is dimensionally wrong — loss leg unmodelled | P1 |
| F3 | behavioral-finance (Dr. Kavya Menon) | `STREAK_DISCOUNT_FACTOR=0.7` discounts ledger accuracy only, not live emitted confidence | P1 |
| F4 | signal-engineering (Dr. Anika Reddy) | `confidence` fed to Kelly with no calibration map; `arbitration.py` completely unspecified | P1 |
| F5 | systems-reliability (Imran Sheikh) | GHA cron + Supabase free-tier both auto-pause on inactivity; missed ingest run = silent failure | P2 |
| Q2-C2 | schema-design (Deepak Nair) | macro_regime referenced as FK when it is a time-series — structural misuse of FK semantics | FIXED |

### 8. Block 3 — R1 Red Team COMPLETE (commit a23eb6f)

- Verdict: **REVISE** — 18 gaps (P0:4, P1:9, P2:5)
- Report: `docs/reviews/R1-red-team.md`
- Core finding: Kelly formula (`b = magnitude_target`) is dimensionally wrong — floors to "1% in everything" for all realistic inputs. Invalidates Layer 4.
- 4 P0 gaps: GAP-001 (Kelly), GAP-002 (calibration), GAP-003 (arbitration void), GAP-006 (silent pipeline pause)
- All 6 mandatory targets confirmed (F2, F3, F4, F5, E2, Shakuni)

### 9. Block 4 — R3 Full Council COMPLETE (commit a23eb6f)

- Council: 20 voices (7 investor + 4 doctrine + 9 expert)
- Verdict: **CONDITIONAL GO**
- Report: `docs/reviews/R3-council-strategic-assessment.md`
- 14 missing actions identified — Block 3.1 was under-scoped
- Synthesis Chair re-classified GAP-009 as P0 (live migration defect)
- Soros and Druckenmiller **withdrew prior approvals** — GAP-004/005 promoted into Block 3.1
- Block 3.1 re-scoped: "produce v0.4 + migrations 0011/0012 + commercial-gate binding, in dependency order, reconciled against live migrations"

### 10. Session 2026-06-22 Commits (in order)

| Commit | Description |
|---|---|
| 0fe54b0 | design doc v0.3 — council amendments + non-goals + SLAs |
| 252b8ac | schema defect fix + R2a expert personas + supabase init |
| 8ff0364 | 11 migration SQL files + SCHEMA.md + GSI-OVERLAP.md + DESIGN.md |
| 69e943e | Supabase cloud live + credentials inventory + .env.example |
| 402a06c | housekeeping checkpoint — SESSION_RESUME + graphify-out |
| a23eb6f | R1 red team + R3 council strategic assessment |

### 11. This Session (2026-06-23 continued) — Governance Fix Plan COUNCIL-APPROVED

**Session resumed post-compaction.** Phase 2 state verified (61/22/3 confirmed), session alignment PASS.

Council assessment of Phase 2 quality produced 8 findings (5 P1, 3 P2). Root cause investigation: governance documents are passive prose — they cannot enforce themselves. The council identified this as a structural gap, not a process gap.

**Permanent fix: `test_governance_integrity.py`** — makes COUNCIL_TEST_MAP.md and skip reasons self-enforcing at every pytest run.

**Premortem completed:** 14 failure modes identified and addressed. Re-challenge survived. Confidence: **96/100** (2-point deduction for absent CI enforcement — accepted limitation). Plan approved.

**10-step sequenced execution plan (council-approved):**
1. Move `test_regime_cached` + `test_stale_regime_fails_visibly` to Phase 3 in COUNCIL_TEST_MAP.md (Dalio caching scoped to Phase 3)
2. Remove stale `@pytest.mark.skip` from 3 TestMarksConditions tests (cycle_phase.py IS implemented)
3. Fix ghost test: implement body of `test_is_commercial_true_when_subscriber_exists` or remove it
4. Add `## Completed Phases` section to COUNCIL_TEST_MAP.md (Phase 1, Phase 2)
5. One-time map audit: verify every GREEN function name against actual test files
6. Add strict skip reason format to CONTRIBUTING.md
7. Build `tests/test_governance_integrity.py` — `--warn` mode, all 14 FM fixes applied
8. Run full suite: zero warnings in warn mode
9. Update COUNCIL_TEST_MAP.md sign-off protocol (drift check + subagent rule + full-suite rule); rename TestShakaniConditions → TestShakuniConditions
10. Commit everything as Phase-housekeeping commit

After Phase 3 complete + signed off → promote governance test from `--warn` to `--strict`.

---

## EXACT RESUME POINT — UPDATED 2026-06-24 (full action plan with skills mapped)

**NEXT ACTION: GROUP A — Step 1 (COUNCIL_TEST_MAP.md: move Dalio's 2 entries to Phase 3)**

Phase 2 COMPLETE (commit ce9cba9). Test state: 61 PASS / 22 SKIP / 3 FAIL (intentional G0 gate).
GSI regression: 455/455 PASS. Governance fix plan: council-approved, 96/100 premortem (Section 11).

---

### GROUP A — Quick code fixes (Steps 1–3 · ~20 min · no council gate)

| Step | Action | File | Line(s) | Skill / Model |
|---|---|---|---|---|
| 1 | COUNCIL_TEST_MAP.md: move `test_regime_cached` + `test_stale_regime_fails_visibly` Phase 2→3 with note: *"caching scoped to Phase 3 — engine.py is the primary caller"* | `COUNCIL_TEST_MAP.md` | Lines 24–25 | Direct Edit · T2 Sonnet |
| 2 | Remove 4 stale skip decorators: Marks × 3 + CE `test_is_commercial_fail_closed` | `tests/test_council_conditions.py` | Lines 114, 120, 133, 260 | Direct Edit · T2 Sonnet |
| 3a | Remove stale skip from `test_is_commercial_true_when_subscriber_exists` | `tests/test_council_conditions.py` | Line 269 | Direct Edit · T2 Sonnet |
| 3b | Implement ghost test body using mock pattern from `test_is_commercial.py` (mock chain: `mock.table...not_.is_...execute.return_value.data = [{"id":1}]`) | `tests/test_council_conditions.py` | Line 270–274 | Direct Edit · T2 Sonnet (read `test_is_commercial.py` first) |

**After Group A:** ~65 PASS / ~18 SKIP / 3 FAIL

---

### GROUP B — Governance document updates (Steps 4–6 · ~20 min)

| Step | Action | File | Skill / Model |
|---|---|---|---|
| 4 | Add `## Completed Phases` section to COUNCIL_TEST_MAP.md: `- Phase 1 (Foundation) — 2026-06-23` + `- Phase 2 (Data Layer) — 2026-06-23` | `COUNCIL_TEST_MAP.md` | Direct Edit · T2 Sonnet |
| 5 | One-time map audit — correct drifted statuses: `test_regime_as_of_join` SPEC→GREEN; Marks `test_all_phase_rules`+`test_never_returns_none` RED→GREEN; rename `test_is_commercial_from_db` → `test_is_commercial_false_when_no_subscribers`; Phase 1 migration entries RED→GREEN | `COUNCIL_TEST_MAP.md` | T1 Haiku (grep sweep) + T2 Sonnet (edits) |
| 6 | Add to CONTRIBUTING.md: (a) Quality Rule 4 — skip format contract `"<path/module.py> not yet implemented — Phase N"`; (b) Council independence rule — Phase sign-off via subagent only | `CONTRIBUTING.md` | Direct Edit · T2 Sonnet |

---

### GROUP C — Build governance test (Steps 7–10 · ~45 min)

| Step | Action | File | Skill / Model | Key notes |
|---|---|---|---|---|
| 7 | Write `tests/test_governance_integrity.py` in `--warn` mode | New file | Direct Write · T2 Sonnet | 7 test functions (see spec below) |
| 8 | Run `python3 -m pytest alphaveda/tests/ --tb=short` — must show 0 governance warnings | bash | T1 Haiku | Full suite, not subset |
| 9 | Amend COUNCIL_TEST_MAP.md sign-off protocol (4 steps → 7); rename `TestShakaniConditions` → `TestShakuniConditions` | `COUNCIL_TEST_MAP.md`, `tests/test_council_conditions.py` | Direct Edit · T2 Sonnet | Protocol step 7: `[council:subagent]` marker |
| 10 | Commit: `chore(alphaveda): governance housekeeping — test_governance_integrity + map + protocol` | git | T1 Haiku bash | No [council:subagent] needed (housekeeping, not Phase sign-off) |

**`tests/test_governance_integrity.py` — 7 test functions:**
```
TestGovernanceMap:
  test_parser_reads_minimum_rows()       # sentinel: assert len(rows) >= 30 (FM-05)
  test_no_spec_in_complete_phases()      # SPEC in Completed Phase → warn (FM-04)
  test_green_tests_are_collectable()     # subprocess --collect-only per GREEN row (FM-06)
  test_no_ghost_tests()                  # un-skipped + pass-only body → warn (FM-08)

TestSkipReason:
  test_no_stale_phase_skips()            # "not yet implemented — Phase N" + N complete → warn (FM-07)
  test_environmental_skips_exempt()      # "SUPABASE_URL not set" → never flagged (FM-07)

TestGovernanceMeta:
  test_governance_test_is_self_checking()  # asserts parser returned ≥30 rows (FM-05 guard)
```
Resources: `COUNCIL_TEST_MAP.md`, `tests/test_council_conditions.py`, `subprocess` (pytest --collect-only), `re`, `ast`

**After Groups A–C:** ~65 PASS / ~18 SKIP / 3 FAIL + governance test GREEN (0 warnings)

---

### PHASE 3 — Signal Layer (after Step 10 committed and green)

| Order | Module | Test file | State | TDD sequence | Resources | Skill / Model |
|---|---|---|---|---|---|---|
| 1 | `src/accuracy/ledger.py` — `compute_streak_flag()` | `tests/test_ledger.py` | SPEC → write first | Write RED → implement → GREEN | `constants.py` (STREAK_WINDOW), design doc §3.1 | Direct TDD · T2 Sonnet |
| 2 | `src/signals/downside.py` — `compute_downside_target()` | `tests/test_downside.py` | STUB/importorskip → un-stub | Remove importorskip → RED → implement → GREEN | existing 7 stubs, `constants.py` (DOWNSIDE_ATR_PERIOD=14) | Direct TDD · T2 Sonnet |
| 3 | `src/signals/arbitration.py` — `arbitrate()` | `tests/test_arbitration.py` | STUB/importorskip → un-stub | Remove importorskip → RED → implement → GREEN | existing 6 stubs, `constants.py` (ARBITRATION_MARGIN=15.0) | Direct TDD · T2 Sonnet |
| 4 | `src/signals/weights.py` — active loader + cold-start | `tests/test_weights.py` | SPEC → write first | Write RED → implement → GREEN | `test_is_commercial.py` (supabase mock pattern), design doc §3.3 | Direct TDD · T2 Sonnet |
| 5 | `src/signals/engine.py` — full emit pipeline steps 1–7 | `tests/test_engine.py` | SPEC → write first | Write RED → implement → GREEN | All Phase 2+3 files once built, design doc §3.4 | Direct TDD · T2 Sonnet (or subagent via `dispatching-parallel-agents`) |

**Phase 3 sign-off:** Soros, Druckenmiller, Shakuni dispatched as **independent subagents** via `dispatching-parallel-agents` skill. Each receives: (1) full pytest -q output, (2) COUNCIL_TEST_MAP.md Phase 3 column, (3) Phase 2 critical findings list. Commit must include `[council:subagent]`.

**After Phase 3 + sign-off:** ~95 PASS / ~11 SKIP / 3 FAIL + promote governance test `--warn` → `--strict`

---

### TEST SUITE STATE PROGRESSION

| Milestone | PASS | SKIP | FAIL | Notes |
|---|---|---|---|---|
| Now (baseline) | 61 | 22 | 3 | Phase 2 complete |
| After Group A | ~65 | ~18 | 3 | 4 stale skips removed + ghost fixed |
| After Groups B+C | ~65 | ~18 | 3 | Governance test GREEN (0 warnings) |
| After Phase 3 | ~95+ | ~11 | 3 | Phase 4 stubs remain SKIP |
| After Phase 3 sign-off | ~95+ | ~11 | 3 | Governance test promoted to --strict |

The 3 FAIL tests (`test_c10_*`) require seed data — intentional until Phase 6 ingest pipeline.

---

### GOVERNANCE FM SUMMARY (for next session)

- FM-01→14: all addressed in the approved plan (Section 11)
- Two accepted residual risks (FM-11, FM-12): no CI enforcement → documentation mitigation only
- Dalio caching: Move to Phase 3 in Step 1 — no Tarun approval needed, council-resolved

Design doc v0.6 is the approved build spec. R4 CONDITIONAL GO is in force. Build sequence:

| Phase | Content | Day |
|---|---|---|
| Phase 1 (Foundation) | Create repo, apply 13 migrations, constants.py, .claude/rules/, seed 10 instruments | Day 1 |
| Phase 2 (Data layer) | config.py, regime.py, provider.py, cycle_phase.py | Day 1–2 |
| Phase 3 (Signal layer) | ledger.py, downside.py, arbitration.py, weights.py, engine.py | Day 2–3 |
| Phase 4 (Portfolio layer) | buckets.py, optimizer.py with Kelly + E1-E4 | Day 3 |
| Phase 5 (Presentation) | app.py + 4 pages (data_viewer, signals, path, accuracy) | Day 4 |
| Phase 6 (GHA ingest) | 5 ingest scripts + resolve_outcomes.py + ingest.yml | Day 4–5 |

**Pre-G1 tracked items (not blocking build):**
- GAP-006: keepalive strategy for GHA + Supabase free tier (before first billing)
- calibration.py interface spec (before G1 regression suite)
- approve_signal_weight RLS caller-identity check (before G2)

---

## TARUN P0 ACTIONS — Still Pending

| Action | Status | Blocks |
|---|---|---|
| T1: Supabase project creation | ✓ COMPLETE (done this session) | — |
| T2: `pip install supabase postgrest pandas_market_calendars streamlit plotly pytest` | PENDING confirmation | G0 smoke tests |
| T3: WhatsApp 3 NSE investors pricing signal ("₹999/month for confidence-scored signals?") | PENDING | R4 Synthesis (≥1 response needed) |
| T4: Confirm UI label "Signal weights: using priors (N observations)" — G0 scope or G1? | PENDING | Determines test_smoke.py spec |
| Stream C: 3 consulting outreach targets | OVERDUE | Revenue |
| Stream A Gate 6: Gumroad listing sign-off | SEPARATE SESSION | Revenue |

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
| T4: UI label "using priors" — G0 smoke test or G1? | Assume G0 (required) | Before writing test_smoke.py |
| Pricing validation: WhatsApp 3 contacts | ₹999/mo assumed if no response | Before R4 (needs ≥1 real signal) |
| Stream C: 3 consulting outreach targets | OVERDUE — no default | TODAY |
| AlphaVeda pricing: ₹999/mo single tier or tiered? | ₹999/mo single tier | Sprint G2 |
| Custom domain? (alphaveda.in?) | Streamlit subdomain | Sprint G2 |
| Stream A Gate 6: final Gumroad listing sign-off | Required before publishing | Separate session |

---

## COMMERCIAL STATE — Updated 2026-06-22

- **Stream A (Gumroad Governance Pack):** LATE — separate session. Gates 2+6 Tarun-owned.
- **Stream C (Financial consulting):** OVERDUE. 3 targets needed immediately.
- **Stream D (AlphaVeda):** Supabase live ✓. R1→R4 in progress. G0 pending T2 + pytest.
- **Stream B (YarnZoo / StitchFlow):** Deferred — out of 21-day scope.
- **Revenue clock:** 21-day goal, started 2026-06-21. AlphaVeda is highest-leverage stream in progress.

---

## BLOCK SEQUENCE — STATUS

| Block | Description | Status |
|---|---|---|
| Block 0 | Design doc v0.3 amendments | ✓ COMPLETE |
| Block 1 | Tarun actions (T1-T4) | T1 ✓, T2/T3/T4 pending |
| Block 2 | R2a + R2b + R2c parallel agents | ✓ COMPLETE |
| Block 3 | R1 Red Team (REVISE, 18 gaps) | ✓ COMPLETE |
| Block 4 | R3 Full Council (CONDITIONAL GO, 14 MAs) | ✓ COMPLETE |
| Block 3.1 | v0.4 + migrations 0011/0012 + gates (7 steps) | ✓ COMPLETE (73c242f) |
| pre-R4 council | 21-voice readiness check → CONDITIONAL READY (82917e5) | ✓ COMPLETE |
| v0.5 corrective | C-1..C-4 closed: 0013 migration + downside.py + pipeline order + G0 gate | ✓ COMPLETE (7c9ec93) |
| Block 5 (R4) | 21-voice synthesis → CONDITIONAL GO, BC-1..BC-8 applied, design doc v0.6 | ✓ COMPLETE (b7baaa3) |
| Block 6 Phase 1 | alphaveda/ scaffold: constants, rules, TDD suite, waitlist page | ✓ COMPLETE (1ae8e37) |
| Council test suite | COUNCIL_TEST_MAP.md + tests/test_council_conditions.py (21 seats mapped) | ✓ COMPLETE (4517d80) |
| G-MIG gate | 11 tables + 4 columns (downside_target, circuit_flag, deliverable_volume, licence_class) | ✓ PASS |
| Block 6 Phase 2 | Data layer: config.py, regime.py, provider.py, cycle_phase.py | ✓ COMPLETE (ce9cba9) |
| Block 7 | G0 gate (10 criteria: 9 tests + 1 seed) | After Block 6 + T2 |
| Block 8 | Post-G0 (G1, auth, GHA cron) | Future sessions |

---

## SECURITY RULES — PERMANENT (never modify)

- `.env` is gitignored — NEVER commit
- `SUPABASE_SERVICE_KEY` for ingest scripts only — never in Streamlit app/client code
- `ALPHAVEDA_COMMERCIAL=false` must remain false until first non-self subscriber (triggers FMP/paid data gate)
- yfinance blocked when `ALPHAVEDA_COMMERCIAL=true` via CommercialLicenseError
- SEBI disclaimer must appear on every page — never remove or conditionalize
- No signal_weights status change PROPOSED → ACTIVE without `approved_by='tarun'` — automation cannot approve weights

---

## DO NOT REDO — Prior Sessions (preserved)

### 2026-06-21 MVP DESIGN — ALL 9 SECTIONS COMPLETE (817 lines)
- 7/7 council unanimous: Option C feedback loop, Approach 2 MVP scope
- 9 migrations fully specified (original 9 → now 11 with ingest_status + waitlist)
- 13 council conditions traced to file + artifact + test (Section 9 trace matrix)
- 6 mandatory accuracy guards locked
- HTML artifact committed: `docs/artifacts/2026-06-21/alphaveda-mvp-spec.html` (`397d5fc`)
- Council ownership map: 7 investor + 4 doctrine + 9 expert domain gaps

### 2026-06-21 PHASE B COUNCIL + ARCHITECTURE
- Lynch (Condition 2): Lynch 6-enum classification
- Buffett + Munger (Condition 4): 9-field fundamental layer
- All 7 conditions resolved
- Q2 CHANGED: Cloud-only confirmed. Docker not installed. Supabase cloud ap-south-1 only.

### 2026-06-21 PRODUCT NAME + BRAND
- Product name: AlphaVeda (Alpha = excess returns; Veda = Sanskrit "to know")
- Colors: Deep Indigo #1A1F3C + Warm Ivory #F5F3EC + Saffron Gold #E8A020
- Typography: Fraunces (headings) + DM Mono (data) + Inter (prose)
- Brand brief: `docs/brand/alphaveda-brand-brief.md`

### 2026-06-19→20 INFRASTRUCTURE + PHASE A COUNCIL
- RAG gateway live, council complete, GSI bucket architecture confirmed
- Q1 (ingest): GHA cron 5:45 PM IST weekdays + lazy fallback
- Q3 (historical depth): OHLCV 3yr · Fundamentals 5yr · Macro 5yr

### 2026-06-16→18 PRIOR WORK (do not re-run)
- 7-seat full council: 7 REVISE verdicts (do not re-run)
- 28-requirement inventory: complete (do not rebuild)
- Strategic analysis: CONSOLIDATE posture (still valid)
- RAG gateway: live (commit 4eb2188)
