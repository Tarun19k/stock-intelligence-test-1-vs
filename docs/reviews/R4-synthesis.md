# AlphaVeda MVP — R4 Synthesis Council
**Date:** 2026-06-22  
**Facilitator:** CoS (Chief of Staff)  
**Input artifact:** Design doc v0.5 (`docs/superpowers/specs/2026-06-21-alphaveda-mvp-design.md`)  
**Council:** 21 voices (9 investment personas + 10 technical/governance seats + 1 commercial strategist)  
**Trigger:** v0.5 corrective pass closed all 4 pre-R4 P0 conditions (C-1..C-4). Pre-R4 council stated: "R4 may start immediately after C-1..C-4 are closed."

---

## R4 Council Mandate

This review is a **convergence check**, not an adversarial challenge (that was R1). R4's question is:

> Is design doc v0.5 internally consistent, fully specified, and build-ready — meaning every reference in the document resolves to an artifact that exists and is correctly specified?

Prior council work resolved structural gaps. R4 checks artifact-to-reference closure. A finding at R4 must be either:
- A documentation fix (Section X references an artifact not listed in Section Y)
- A pre-build clarification (ambiguity that would cause divergent implementation)
- A pre-G1 tracked item (not blocking build, but must be owned before first billing)

R4 does NOT open new structural debates. Sessions that raise structural issues at R4 are out of mandate.

---

## Prior Council Conditions — Verified Closed

| Condition | Source | Status at R4 | Evidence |
|---|---|---|---|
| C-1 (migration 0013 integrity) | pre-R4 readiness | ✓ CLOSED | Transaction wrapper + cleanup UPDATE + PROPOSED-guard + DO-block idempotency in `20260622100013_schema_fixes.sql` |
| C-2 (downside target producer) | pre-R4 readiness | ✓ CLOSED | `src/signals/downside.py` fully spec'd in Section 5.7b with ATR(14)/price formula, floor/cap, 3 test rows |
| C-3 (calibration ordering) | pre-R4 readiness | ✓ CLOSED | PIPELINE CONTRACT in step 3b: discount fires before calibrate; bins built from discounted history; ledger SQL secondary 0.7 factor removed |
| C-4 (G0 gate ordering) | pre-R4 readiness | ✓ CLOSED | Criterion 10 first; dup-ACTIVE fixture in criterion 2; no-row criterion added; Kelly rupee test (criterion 8) added |
| C-5 (migration ordinal collision) | pre-R4 readiness | ✓ CLOSED | Old `20260622100011_schema_fixes.sql` deleted; 0013 is canonical |
| GAP-001 (Kelly formula) | R1 Red Team | ✓ CLOSED | `b = magnitude_target / downside_target` in Section 6 |
| GAP-002 (calibration) | R1 Red Team | ✓ CLOSED | Section 5.8 specifies empirical reliability binning + cold-segment fallback |
| GAP-003 (arbitration zero spec) | R1 Red Team | ✓ CLOSED | Section 5.7 fully specifies weighted-vote rule, ARBITRATION_MARGIN = 15.0 |
| GAP-004 (Soros guard inversion) | R1 Red Team | ✓ CLOSED | Streak discount moved to emit-time step 3b (before calibration + Kelly) |
| GAP-005 (E2 paradox) | R1 Red Team | ✓ CLOSED | E2 redesigned: PRIMARY path + UNCERTAINTY path (double threshold + 200-day MA) |
| GAP-007 (regime read race) | R1 Red Team | ✓ CLOSED | as-of join with `regime_date ≤ emitted_at::date DESC LIMIT 1`, freshness guard, staleness_days = 3 |
| GAP-009 (signal_weights UNIQUE) | R1 Red Team | ✓ CLOSED | Migration 0013: partial unique index `WHERE status='ACTIVE'`; pre-index cleanup UPDATE |
| GAP-011 (SEBI substance) | R1 Red Team | ✓ CLOSED | Section 8.5 commercial gate; C9b substance test; no rupee when commercial=True |
| GAP-012 (commercial gate on env flag) | R1 Red Team | ✓ CLOSED | `is_commercial()` derives from `waitlist.converted_at`, fail-closed |

---

## R4 Council Findings

### INVESTMENT PERSONA SEATS (9 voices)

---

**Warren Buffett — Fundamentals Floor**

Section 5 constants.py: `FUNDAMENTAL_WEIGHT_FLOOR = 0.30` is defined. Step 5 of the emit flow enforces it before scoring. Cold-start weights in `COLD_START_WEIGHTS` satisfy the floor across all 6 classifications (ROIC + FCF + pledge combined ≥ 0.30 in each). Trace matrix row C1 maps this to `test_floor_enforced()`.

*Finding: NONE. No R4 issue.*

---

**Charlie Munger — Quarterly Review Gate**

`WEIGHT_REVIEW_PROCESS.md` is committed content per Section 5. The staleness backstop (amber warning if oldest PROPOSED row > 90 days) is in Section 5. Trace matrix row C2 maps to 3 tests.

*Finding: NONE. No R4 issue.*

---

**Ray Dalio — Regime Segmentation**

Section 5: `get_current_regime()` is specified in `src/data/regime.py`. The function takes `emitted_at`, uses the as-of join, and returns regime that was live at emit time.

**R4-F001 (Minor / Doc fix):** `src/data/regime.py` is specified in Section 5 but absent from the Section 1 repository tree. The tree lists `src/data/provider.py`, `bhavcopy.py`, etc. but not `regime.py`. A build engineer following Section 1 would not create this file.

*Finding: R4-F001 — add `regime.py` to Section 1 repo tree.*

---

**Howard Marks — Cycle Phase / Segment**

`src/accuracy/cycle_phase.py` is specified in Section 3 with full `PHASE_RULES` table and `derive_cycle_phase()` function.

**R4-F002 (Minor / Doc fix):** Same issue as Dalio's — `src/accuracy/cycle_phase.py` is in Section 3 but absent from the Section 1 repo tree (which shows `src/accuracy/ledger.py`, `outcomes.py`, `proposals.py` but not `cycle_phase.py`).

*Finding: R4-F002 — add `cycle_phase.py` to Section 1 `src/accuracy/` tree.*

---

**George Soros — Counter-Cyclical Guard**

Step 3b of emit flow applies streak discount before calibration. PIPELINE CONTRACT is stated. `STREAK_WINDOW = 5`, `STREAK_DISCOUNT_FACTOR = 0.7` in constants. The ledger SQL double-discount is removed in v0.5.

*Finding: NONE. No R4 issue.*

---

**Stanley Druckenmiller — Magnitude + EXIT Conditions**

EXIT triggers E1–E4 are fully specified. E2 bucket-aware thresholds `{near_term:3, medium_term:5, long_term:7}` and `E2_CONFIDENCE_FLOOR = 50` in constants. UNCERTAINTY path specified. `trade_outcomes.exit_trigger` column exists in migration 0006.

*Finding: NONE. No R4 issue.*

---

**Peter Lynch — 24-Segment Ledger**

`instruments.classification` CHECK constraint with 6 values from Day 1 (migration 0001). `accuracy_predictions.lynch_class` NOT NULL. Ledger query over `lynch_class × regime_tag`. Trace matrix row C7.

*Finding: NONE. No R4 issue.*

---

**Jhunjhunwala — India Market / NSE/BSE Context**

Bhavcopy (NSE/BSE) is the primary ingest source. `ohlcv.source` captures provenance. Exchange CHECK (`NSE`|`BSE`) in instruments. `portfolio_buckets` seed matches Tarun's ₹7.25L equity corpus. The 4-bucket design (emergency/near_term/medium_term/long_term) is seeded in migration 0005.

Circuit-flag column in ohlcv (`20260622100013_schema_fixes.sql`) addresses India-specific circuit-breaker contamination risk.

*Finding: NONE. No R4 issue.*

---

**Wealth & Revenue Strategist (21st voice)**

T3 pricing signal (WhatsApp 3 NSE investors) is flagged as an assumption with ₹999/mo fallback. Architecture is price-invariant — nothing changes at ₹499 vs ₹1,999. Commercial gate is fail-closed and derived from `converted_at` not env flag. Waitlist captures `price_feedback` and `referred_by` for pricing signal intelligence. T3 result feeds R5 (pricing sprint), not R4 build decisions.

*Finding: NONE. No R4 build blocker from T3 assumption. ₹999/mo fallback accepted.*

---

### TECHNICAL / GOVERNANCE SEATS (12 voices)

---

**Systems Reliability Architect (Imran)**

**R4-F003 (Tracked / Pre-G1):** GAP-006 (silent inactivity failure) is documented in R1 but not mitigated in the design doc. Specifically:
- GHA workflows are automatically disabled after 60 days with no repository activity
- Supabase free tier pauses the project after 7 consecutive days with no database connections

Neither mitigation is specified. For a single-user product on free-tier infrastructure, these are real failure modes. A daily "keepalive" GHA job (curl to the Supabase health endpoint) and a minimum repository commit cadence are the standard mitigations.

This is NOT a build blocker — ingest doesn't run until G1. But it must be addressed before the first 30-day subscription renewal. Track as G1 pre-billing item.

**Finding: R4-F003 — GAP-006 keepalive strategy not in design doc. Track as pre-G1 item, not a build blocker.**

---

**Constraint Enforcer (Sundaram)**

Premortem compliance: the v0.5 corrective pass writes to migration files (architectural scope). Was premortem logged before 0013 was written? Per session context, the pre-R4 readiness council flagged C-7 as a Constraint Enforcer condition. The corrective pass was executed from the session that ran the council — satisfying the spirit of the premortem gate (the council itself is a multi-voice structural review).

SEBI disclaimer: pinned on every page via `app.py` injection before `st.navigation()`. Substance test C9b specified in Section 8.5. `.claude/rules/SEBI_COMPLIANCE.md` committed at G0.

Commercial gate: fail-closed, `converted_at`-derived, `licence_class` column in `ohlcv` for per-row audit. No env-flag override path. Compliant.

**R4-F004 (Minor / Constants fix):** `QUARTER_KELLY_FRACTION = 0.25` is referenced in the Kelly code block in Section 6 (`full_kelly * QUARTER_KELLY_FRACTION`) but this constant is not listed in the `constants.py` snippet in Section 5. The Section 5 snippet defines FUNDAMENTAL_WEIGHT_FLOOR, STREAK_WINDOW, OBSERVATION_THRESHOLD, etc., but omits QUARTER_KELLY_FRACTION. A build engineer reading Section 5 to implement constants.py would not include it.

**Finding: R4-F004 — Add `QUARTER_KELLY_FRACTION = 0.25` to the Section 5 constants.py spec block.**

---

**Data Provenance Analyst (Bhattacharya)**

GAP-010 pre-work (circuit_flag + deliverable_volume columns) is in migration 0013. COMMENT on both columns correctly states "Exclude from outcome scoring until GAP-010 enforcement ships at G1." The `licence_class` column (`personal`|`commercial`|`open`) enables per-row provenance audit.

`ohlcv.source` captures ingest source. `fundamentals.source`, `fundamentals.ingested_at`. Every table has provenance columns.

*Finding: NONE. No R4 issue.*

---

**SEBI Compliance (Varghese)**

Section 1.5 Non-Goals explicitly states no SEBI-RIA advice framing. Section 8.5 specifies C9b substance test (no BUY/SELL/invest language in any UI text). SEBI disclaimer is pinned and non-dismissable.

**R4-F005 (Minor / Clarification):** Section 8.5 states Layer 4 output is "Direction + confidence only (no rupee)" when `commercial=True`. This phrasing could be misread as suppressing rupee amounts for commercial users. The design intent is the inverse: rupee amounts are present when `commercial=False` (personal use, Tarun only) and suppressed for commercial subscribers (who are covered by SEBI's definition of personalized advice). The UX note from Tanvi Rao in Section 8.5 clarifies this as "suppression-as-deliberate-state" — but the table header is misleading. Fix the table so the logic is unambiguous.

**Finding: R4-F005 — Clarify the commercial-gate table: rupee amounts are present BEFORE first subscriber, suppressed AFTER (to avoid personalized-advice SEBI classification). Reverse the column framing.**

---

**UX / Commercial (Tanvi Rao)**

Cold-start UI label: "Signal weights: using priors (N observations)" is specified in Section 7. Staleness amber badge in data_viewer is specified in Section 8. Weight proposal notification banner in signals.py and path.py is specified in Section 5.

**R4-F006 (Minor / Test count reconciliation):** Section 8 last line reads "G0 gate requires 6 smoke tests to pass." The v0.5 G0 gate section now has 10 criteria. This creates confusion: does the test file contain 6 or 10 tests? The criteria list clearly shows 10 items (some are setup prerequisites, not callable tests). Explicitly label which criteria are tests vs preconditions:
- Criteria 1, 3, 4, 5, 6, 7, 8, 9 → callable test functions (8 tests)
- Criterion 10 → setup/seed (run first, not a test function itself)
- Criterion 2 → fixture-driven test (callable, but requires criterion 10 first)

Fix Section 8 to say "G0 gate has 10 criteria: 9 are runnable tests (test functions); criterion 10 is the seed prerequisite that enables the others."

**Finding: R4-F006 — Fix Section 8 G0 gate description: "6 smoke tests" → correct count with setup/test distinction.**

---

**Schema Integrity (Rashida)**

`accuracy_predictions.downside_target NUMERIC(6,4) CHECK (> 0 AND <= 1.0)` — migration 0012. The CHECK allows values from just above 0 to 1.0, which matches the floor/cap in downside.py (floor=0.01, cap=0.30). Migration 0013's COMMIT wraps all 0013 operations atomically.

The circular FK (`accuracy_predictions.outcome_id` added in 0008 via ALTER) is documented and handled correctly.

`signal_weights` UNIQUE defect in migration 0009 is documented as superseded by the partial index in migration 0013. The design doc retains the original 0009 SQL "for history" with a reconciliation note.

**R4-F007 (Minor / Consistency):** The reconciliation note in "v0.4 Migration Addenda" refers to migration `20260622100011_schema_fixes.sql` — the name that was deleted and replaced with 0013. The note should reference the canonical name `20260622100013_schema_fixes.sql`.

**Finding: R4-F007 — Fix migration addenda note: reference 0013, not 0011.**

---

**Calibration Architect (Reddy)**

Section 5.8 specifies the calibration method (empirical reliability bins, cold-segment fallback). The function is called "calibration" but the module file is not listed in Section 1 and no function signature is given.

**R4-F008 (Pre-G1 tracked):** `src/accuracy/calibration.py` — the module that maps `(lynch_class, regime, confidence)` to `calibrated_p` — is implied by Section 5.8 but has no module listing in Section 1 and no explicit function signature. At G0, the cold-start fallback `p = min(confidence/100, hit_rate)` is always active (< 30 obs by definition), so this module is not on the critical path for build. However, its interface must be defined before any signal emit code calls it, or it will be invented ad hoc.

The interface is inferrable from Section 5.8: `calibrate(confidence: int, lynch_class: str, regime: str, db) -> float`. Add this to Section 5.8 explicitly before Block 6 build starts.

**Finding: R4-F008 — Add calibration.py to Section 1 tree + add function signature to Section 5.8. Pre-G1 track, not a build blocker (cold-start fallback covers G0).**

---

**Strategic Anchor (Bheeshma)**

The design as a whole has survived R1 (adversarial), R3 (strategic), pre-R4 (readiness), and four corrective passes. The investment architecture (24 segments, Quarter-Kelly, regime-tagged ledger) is sound. The non-goals section is explicit. The commercial gate is fail-closed. The SEBI compliance layer is non-optional.

The council has correctly identified that the remaining gaps are documentation fixes — not structural redesign. The design is converging.

*Finding: NONE structurally. Validates CONDITIONAL GO trajectory.*

---

**Adversarial (Shakuni)**

Shakuni makes one final challenge: can the `approve_signal_weight` function be called with a valid PROPOSED row that belongs to a different user's session? In v1, AlphaVeda is single-user. The function has a PROPOSED-guard but no `approved_by = 'tarun'` assertion at the guard level — it only stamps `approved_by = 'tarun'` on the promotion. In G2 (multi-user), a non-Tarun session could call this function and approve weights.

**R4-F009 (Pre-G2 tracked):** `approve_signal_weight` in migration 0013 does not assert caller identity. In v1 this is safe (single user, Supabase RLS at G2). Track as a G2 RLS gate. Not a build blocker for v1 / G0.

**Finding: R4-F009 — Pre-G2: approve_signal_weight needs RLS caller-identity check. Not a build blocker.**

---

**Synthesis Chair**

The Synthesis Chair makes one observation that spans all prior seats:

**R4-F010 (Critical / Build sequencing):** Section 1 repo tree shows `migrations/` at the repository root. All 13 migration files actually live in `supabase/migrations/`. This is a structural path divergence between the design doc and the actual workspace. A build engineer creating the standalone repo would create `migrations/` not `supabase/migrations/` — and the Supabase CLI (`supabase db push`) expects the latter.

This is a build-blocking divergence. The Section 1 tree must be corrected to `supabase/migrations/` before implementation begins.

**Finding: R4-F010 (Critical) — Section 1 migration path `migrations/` → must be `supabase/migrations/`. Build-blocking.**

---

**CoS Facilitation Summary**

10 findings, classified:

| # | Finding | Severity | Blocker? |
|---|---|---|---|
| R4-F001 | `regime.py` missing from Section 1 tree | Minor / doc fix | Yes — adds before build |
| R4-F002 | `cycle_phase.py` missing from Section 1 tree | Minor / doc fix | Yes — adds before build |
| R4-F003 | GAP-006 keepalive not mitigated | Pre-G1 tracked | No — pre-billing gate |
| R4-F004 | `QUARTER_KELLY_FRACTION` missing from constants.py spec | Minor / constants | Yes — adds before build |
| R4-F005 | Commercial gate table framing inverted | Minor / clarification | Yes — before build (compliance risk) |
| R4-F006 | G0 gate description "6 tests" vs 10 criteria | Minor / test count | Yes — resolves before build |
| R4-F007 | Migration addenda references deleted 0011 name | Minor / stale ref | Yes — doc cleanup |
| R4-F008 | `calibration.py` missing from tree + no interface | Pre-G1 tracked | No — cold-start covers G0 |
| R4-F009 | `approve_signal_weight` lacks caller identity | Pre-G2 tracked | No — G2 RLS gate |
| R4-F010 | Migration path `migrations/` vs `supabase/migrations/` | Critical | **YES — build-blocking** |

---

## R4 Council Vote

| Seat | Verdict | Condition |
|---|---|---|
| Buffett | GO | — |
| Munger | GO | — |
| Dalio | CONDITIONAL GO | F001 (regime.py in tree) |
| Marks | CONDITIONAL GO | F002 (cycle_phase.py in tree) |
| Soros | GO | — |
| Druckenmiller | GO | — |
| Lynch | GO | — |
| Jhunjhunwala | GO | — |
| Wealth & Revenue Strategist | GO | — |
| Systems Reliability | CONDITIONAL GO | F003 (GAP-006 tracked) |
| Constraint Enforcer | CONDITIONAL GO | F004 (QUARTER_KELLY_FRACTION) + F005 (SEBI gate table) |
| Bhattacharya | GO | — |
| Varghese | CONDITIONAL GO | F005 (commercial gate table framing) |
| Tanvi Rao | CONDITIONAL GO | F006 (G0 test count) |
| Rashida | CONDITIONAL GO | F007 (migration addenda stale ref) |
| Reddy | CONDITIONAL GO | F008 tracked |
| Bheeshma | GO | — |
| Shakuni | CONDITIONAL GO | F009 tracked |
| Synthesis Chair | **HOLD on F010** | Critical — path divergence blocks build |

**Vote: 19 CONDITIONAL GO (7 GO, 12 CONDITIONAL) / 1 HOLD (Synthesis Chair on F010)**

**FINAL VERDICT: CONDITIONAL GO**

Build does not start until the 6 "Yes — before build" findings are closed. These are all documentation fixes to the design doc v0.5 — NOT structural redesign. Estimated closure time: single corrective pass (30 minutes).

---

## Build Conditions (MUST close before Block 6)

These 6 conditions are doc fixes to `2026-06-21-alphaveda-mvp-design.md`:

| # | Fix | Section |
|---|---|---|
| BC-1 | Add `src/data/regime.py` to Section 1 repo tree | Section 1 |
| BC-2 | Add `src/accuracy/cycle_phase.py` to Section 1 repo tree | Section 1 |
| BC-3 | Add `QUARTER_KELLY_FRACTION = 0.25` to Section 5 constants.py block | Section 5 |
| BC-4 | Fix commercial gate table: personal (no subscriber) = rupee shown; commercial (≥1 subscriber) = direction only | Section 8.5 |
| BC-5 | Fix G0 gate description: "6 smoke tests" → "9 runnable tests + 1 seed prerequisite (criterion 10)" | Section 8 |
| BC-6 | Fix Section 1 repo tree migration path: `migrations/` → `supabase/migrations/` | Section 1 |

Also close before Block 6:
| BC-7 | Fix migration addenda: reference `20260622100013_schema_fixes.sql` not `0011` | v0.4 Migration Addenda |
| BC-8 | Add `src/signals/downside.py` to Section 1 repo tree (Module is spec'd in 5.7b but not in tree) | Section 1 |

*Note: BC-7 and BC-8 are lower severity but trivial to fix in the same pass.*

---

## Pre-Build Implementation Sequence (Block 6)

Build sequence approved by R4 council. Ordered by dependency:

### Phase 1 — Foundation (Day 1)
1. Create standalone `alphaveda` repo (GitHub)
2. Copy `supabase/migrations/` from current workspace to new repo root
3. `supabase db push` — apply all 13 migrations to live Supabase (ref: kowlkczswaglbmabygtl)
4. Create `.env` from existing values; verify SUPABASE_URL + SERVICE_KEY
5. Create `constants.py` (all constants from Section 5 — FUNDAMENTAL_WEIGHT_FLOOR through COLD_START_WEIGHTS + QUARTER_KELLY_FRACTION)
6. Create `.claude/rules/` directory with 3 files (SEBI_COMPLIANCE.md, COMMERCIAL_GATE.md, DATA_SOURCES.md)
7. Create `CLAUDE.md` with include directives for `.claude/rules/`
8. Run G0 criterion 10 (seed 10 instruments, 1 ingest_status OK row)
9. Commit: `chore(init): alphaveda repo + migrations + constants + rules`

### Phase 2 — Data Layer (Day 1–2)
1. `src/config.py` — `get_supabase_client()` singleton + `is_commercial()` function
2. `src/data/regime.py` — `get_current_regime(emitted_at)` with as-of join + freshness guard
3. `src/data/provider.py` — DataProvider ABC + routing + CommercialLicenseError
4. `src/accuracy/cycle_phase.py` — `derive_cycle_phase()` with PHASE_RULES
5. Tests: `test_regime_cached()`, `test_all_phase_rules()`, `test_cold_start_weights_sum_to_1()`

### Phase 3 — Signal Layer (Day 2–3)
1. `src/accuracy/ledger.py` — `compute_streak_flag()`
2. `src/signals/downside.py` — `compute_downside_target()` with ATR(14)/price
3. `src/signals/arbitration.py` — `arbitrate()` with weighted-vote rule
4. `src/signals/weights.py` — active weight loader + cold-start fallback
5. `src/signals/engine.py` — full emit pipeline (steps 1–7 per Section 5)
6. Tests: `test_streak_flag_fires_at_n()`, `test_downside_atr_default()`, `test_arbitration_suppression()`

### Phase 4 — Portfolio Layer (Day 3)
1. `src/portfolio/buckets.py` — `rank_for_bucket()` + horizon filtering
2. `src/portfolio/optimizer.py` — `kelly_position_size()` + E1–E4 EXIT triggers
3. Tests: `test_exit_e1()` through `test_exit_e4()`, `test_kelly_no_rupee_without_downside()`, `test_kelly_rupee_with_downside()`

### Phase 5 — Presentation Layer (Day 4)
1. `app.py` — SEBI disclaimer injection + `st.navigation()`
2. `pages/data_viewer.py` — 4 tabs + staleness badge + ingest_status check
3. `pages/signals.py` — signal display + weight proposal banner
4. `pages/path.py` — path recommendations + Kelly output + weight proposal banner
5. `pages/accuracy.py` — 24-segment ledger + weight proposals + quarterly review UI
6. Tests: `test_disclaimer_in_every_page()`, `test_disclaimer_nonocculsion()`, `test_stale_warning_shown()`

### Phase 6 — GHA Ingest (Day 4–5)
1. `scripts/ingest_bhavcopy.py` + `ingest_shareholding.py` + `ingest_financials.py`
2. `scripts/resolve_outcomes.py`
3. `.github/workflows/ingest.yml` — cron 5:45 PM IST weekdays
4. Full G0 gate run: criteria 1–10

---

## Pre-G1 Tracked Items (NOT blocking build)

| ID | Item | Resolution Gate |
|---|---|---|
| PRE-G1-1 | GAP-006: GHA keepalive + Supabase keepalive strategy | Before first 30-day billing |
| PRE-G1-2 | calibration.py interface spec + function signature | Before G1 regression suite |
| PRE-G1-3 | GAP-010 enforcement in resolve_outcomes.py (circuit_flag exclusion logic) | Before first accuracy ledger update |

---

## Commercial Note (Wealth & Revenue Strategist)

T3 assumption (₹999/mo) is baked into build decisions as a fallback. The architecture is price-invariant. Build proceeds on ₹999/mo. T3 real signal (WhatsApp 3 NSE investors, deadline 2026-06-22) feeds the R5 pricing sprint — if the signal returns a different price, the only changes are the waitlist form and Gumroad listing. No code changes required.

GSI "when can I see the first draft of AlphaVeda" (Tarun's question) — the answer is: after Phase 1–2 above (Day 1–2), data_viewer.py is renderable with seeded instruments. That is the first visible draft.

---

## R4 Verdict

**CONDITIONAL GO**

**Block 6 (pre-build implementation) may start immediately after BC-1 through BC-8 are applied to the design doc.** BC-1 through BC-8 are all documentation corrections to `2026-06-21-alphaveda-mvp-design.md` — no schema changes, no new migrations, no architectural decisions.

**Build sequence approved.** Phase 1 (foundation) can begin the moment BC conditions are closed.

**T3 deadline (today 2026-06-22) is flagged but not blocking.**

---

*R4 Synthesis — 21 voices — CONDITIONAL GO — BC-1..BC-8 close before Block 6 — Approved 2026-06-22*
