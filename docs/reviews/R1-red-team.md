# R1 Red Team — AlphaVeda MVP Design v0.3
**Date:** 2026-06-22
**Reviewer:** R1 Red Team (Opus)
**Verdict:** REVISE
**Gap count:** 18 gaps identified (4 P0, 9 P1, 5 P2)

---

## Executive Summary

This design is well-structured and has clearly survived a prior council pass — the Section 9 trace matrix, the cold-start priors, and the circular-FK handling are evidence of real engineering discipline. But the document hides three classes of fatal defect behind a veneer of completeness. The most dangerous are **mathematical, not architectural**: the Kelly position sizer is wrong by construction (GAP-001), it consumes an uncalibrated number as if it were a probability (GAP-002), and `arbitration.py` — named as a core capability in the critical path — is a complete specification void (GAP-003). These three are not "gaps to close before build"; they mean the headline feature (position-sized path recommendations) produces numbers that are confidently, systematically wrong. A wrong Kelly number presented in a polished Streamlit table with a rupee value next to it is more dangerous than no number, because it manufactures false precision for a single user betting ₹7.25L of real capital.

The second class is **timing inversion of the council's own guards**. The Soros counter-cyclical guard (Guard 2) is supposed to fire skepticism *before* the dangerous bet. As implemented, `STREAK_DISCOUNT_FACTOR=0.7` only touches the quarterly ledger aggregation — it never discounts the live confidence that Kelly sizes against (GAP-004). At a cycle peak, the engine sizes UP exactly when the guard was designed to size DOWN, and the correction arrives months later in a proposal banner. The E2 confidence floor has the same inversion: the exit signal self-suppresses precisely when the model is most uncertain and the market is deteriorating fastest (GAP-005). These are not bugs in code that doesn't exist yet — they are design-level logic inversions baked into the constants and the data flow.

The third class is **silent-failure surface area**. The entire accuracy loop hangs on one best-effort GHA cron plus a free-tier Supabase that pauses after 7 days idle (GAP-006). When both pause, the app still loads and serves stale data with no error state, because `ingest_status` only logs runs that *happen* — the "never ran" case writes no row and trips no alert. Combined with the regime-read race condition (GAP-007), the system can confidently make and size predictions against a regime tag that is days stale and never resolve the outcomes that would correct it.

**Recommendation: REVISE.** The four P0 gaps (Kelly dimensionality, calibration, arbitration spec, missing-run detection) are structural design defects, not execution details. They must be re-specified in the design doc before any G0 build begins. The Kelly defect alone invalidates Layer 4, which is one of the three co-equal product layers. This is not a CONDITIONAL_PASS because the fixes are not "clear and mechanical" — fixing Kelly requires modelling a loss leg the schema does not currently capture, and fixing calibration requires a layer (Platt/isotonic) the design has no slot for.

---

## Gaps

### GAP-001: Kelly odds parameter `b` is dimensionally wrong — every position size is unsound — P0
**Section:** Section 6, `kelly_position_size`
**Finding:** The code sets `b = magnitude_target if magnitude_target > 0 else 0.05` and computes `full_kelly = (p - q/b)`. The Kelly criterion's `b` is *net odds* = (amount won per unit staked) / (amount lost per unit staked). `magnitude_target` is an expected upside fraction (e.g., 0.15 = "15% upside") — it describes only the win leg. The loss leg is never modelled anywhere in the schema or the function. So `q/b` divides the loss-probability by a quantity that is not odds, producing a number with no financial meaning. The formula is not "approximately right" — it is dimensionally incoherent.
**Risk:** Every rupee amount on the Path page is wrong. With `magnitude_target = 0.15` and `p = 0.85`, the code computes `0.85 - 0.15/0.15 = 0.85 - 1.0 = -0.15` → clamped to 0 → then the final clamp floors it to MIN (₹7,250). With `magnitude_target = 0.05` (the floor) and `p = 0.85`: `0.85 - 0.15/0.05 = 0.85 - 3.0 = -2.15` → 0 → MIN. The function will floor nearly every realistic input to the 1% minimum, masking the error as "conservative sizing" while actually producing garbage. When the loss leg is asymmetric (a turnaround stock with 30% downside vs 15% upside), the true Kelly fraction halves, but the formula cannot see this at all.
**Fix required before build:** yes
**Proposed resolution:** Add a `downside_target` (or stop-loss fraction) to `accuracy_predictions` and to the signal emit contract. Compute `b = magnitude_target / downside_target` (true net odds). Re-derive: `f = p - q/b` where both legs are real. Until a loss leg exists, the Path page must NOT display rupee amounts — show direction + confidence only. This is the single most important fix in the document.

### GAP-002: `confidence` is fed to Kelly as a calibrated probability `p` with no calibration layer — P0
**Section:** Section 6 (`p = confidence / 100`) + Section 5 (emit flow, step 6)
**Finding:** Kelly requires `p` to be a true win probability. `confidence` is a 0–100 composite of weighted signal scores (Section 5 never even specifies the score→confidence function — it jumps from "enforce FUNDAMENTAL_WEIGHT_FLOOR" straight to "emit signal"). There is no Platt scaling, no isotonic regression, no mapping that guarantees confidence=70 corresponds to ~70% historical `is_correct`. The 24-segment ledger *measures* hit rate but is never wired back to *calibrate* the confidence-to-probability map — it only drives quarterly weight proposals.
**Risk:** Uncalibrated confidence is almost always overconfident on out-of-sample data. Feeding p=0.85 when the segment's true hit rate is 0.60 inflates the Kelly numerator `(p - q/b)` and oversizes positions — the exact failure mode quarter-Kelly was supposed to dampen, re-introduced upstream.
**Fix required before build:** yes
**Proposed resolution:** Insert a calibration map between confidence emission and Kelly consumption. Minimum viable: per-segment empirical reliability binning (group historical predictions by confidence decile, compute actual hit rate per bin, use that as `p`). Document the score→confidence function explicitly in Section 5. Until calibration exists, cap Kelly `p` at the segment's measured `hit_rate` (fail-conservative).

### GAP-003: `arbitration.py` is named in the critical path but never specified — P0
**Section:** Section 1 (`src/signals/arbitration.py`, "Signal arbitration: when TA signals conflict") — absent from Sections 5–9
**Finding:** Arbitration is listed as a Layer 3 core capability and a source file, but no section defines its inputs, logic, or outputs. There is no constant, no rule, no test row in the Section 9 trace matrix. When a bull signal and a bear signal conflict on the same instrument, the design does not say whether the engine suppresses emission, averages, picks the higher-weighted signal, or picks the higher-confidence one. This is a black box sitting directly upstream of `accuracy_predictions` and Kelly.
**Risk:** Every conflicting-signal case has undefined behavior. Whatever the implementer guesses becomes load-bearing logic with no review, no test, and no traceability. Conflict resolution choices materially change hit rate and which direction gets logged to the ledger — so an unspecified arbitration silently determines accuracy ledger contents.
**Fix required before build:** yes
**Proposed resolution:** Add a dedicated subsection to Section 5 specifying the arbitration rule (recommend: weighted-vote using ACTIVE weights, with a "suppress emission if |bull_score − bear_score| < ARBITRATION_MARGIN" no-emit band to avoid logging coin-flip predictions). Add `ARBITRATION_MARGIN` to constants.py and a `test_arbitration_*` row to the trace matrix.

### GAP-004: STREAK_DISCOUNT_FACTOR fires at ledger aggregation, not at live emit — Soros guard inverted — P1
**Section:** Section 3 ledger query vs Section 5 emit flow (steps 1–7)
**Finding:** `STREAK_DISCOUNT_FACTOR=0.7` appears only in the Section 3 ledger SQL (`actual_return * CASE WHEN accuracy_streak_flag THEN 0.7 ELSE 1.0 END`). The live emit flow computes `accuracy_streak_flag` (step 3) but never applies the discount to the emitted `confidence`. So a 5-win streak raises confidence in real time (more conviction), and the discount only surfaces months later in a quarterly weight proposal. Guard 2 (Soros) explicitly states "accuracy streaks trigger skepticism, not confidence boost" — the implementation does the opposite at the moment that matters.
**Risk:** At a reflexive cycle peak — when streaks are longest and most dangerous — the engine emits maximum confidence, Kelly (already oversizing per GAP-002) sizes up further, and the only brake is a banner that appears next quarter. The guard punishes the historical record but not the current bet. This is the precise failure the Soros seat was added to prevent.
**Fix required before build:** yes (pre-G0)
**Proposed resolution:** Apply the discount in the emit path: if `compute_streak_flag()` is True, multiply emitted `confidence` by `STREAK_DISCOUNT_FACTOR` *before* it is written to `accuracy_predictions` and *before* Kelly consumes it. The ledger-stage discount can remain as a secondary check but must not be the only one.

### GAP-005: E2 confidence floor creates a deterioration paradox — exit suppresses when most needed — P1
**Section:** Section 6 (E2 trigger) + Section 5 (`E2_CONFIDENCE_FLOOR = 50`)
**Finding:** E2 fires only when `consecutive_bear >= bucket_threshold AND confidence >= E2_CONFIDENCE_FLOOR (50)`. A BEAR emit below confidence 50 does not count toward the streak. But low confidence during a bear run is exactly the signature of a deteriorating, uncertain market. The exit signal therefore self-suppresses when the model is least sure and the downside is fastest.
**Risk:** Holdings ride a deteriorating instrument all the way down because each "uncertain bear" emit resets/fails the streak. The floor was added to prevent noise-driven exits, but it conflates "noisy" with "uncertain," and uncertainty during a decline is signal, not noise. The user is exposed precisely in the regime where capital preservation matters most.
**Fix required before build:** yes (pre-G0)
**Proposed resolution:** Split the floor's two jobs. Keep a noise filter, but make low-confidence bear emits count toward a *separate* "uncertainty exit" path (e.g., if N consecutive emits are BEAR regardless of confidence AND the instrument is below its 200-day MA, trigger a review-exit). Do not let a single floor silence the deterioration case.

### GAP-006: No missing-run detection — silent simultaneous cron + Supabase pause — P0
**Section:** Section 7 (`ingest.yml`) + Section 8 (`ingest_status`)
**Finding:** The whole accuracy loop depends on one GHA cron (best-effort; delayable 15–60+ min; auto-disabled after 60 days repo inactivity) plus Supabase free tier (pauses after 7 days inactivity). `ingest_status` logs OK/FAILED/PARTIAL *only when the script runs*. A cron that never fires writes no row — and the design's staleness check keys off `run_at < today 6PM`, which only catches a row that exists. The "no row at all" case is the dangerous one and nothing actively asserts "a run should have happened by now."
**Risk:** Both pause during a quiet stretch → Streamlit still loads (it just queries whatever is in Supabase) → serves stale data with no error state → predictions past their horizon never resolve → `outcome_id` stays NULL → ledger stalls → streak flags drift → and the user sees confident, current-looking signals built on dead data. This is a textbook silent failure on a financial tool.
**Fix required before build:** yes
**Proposed resolution:** Add an active "expected run" watcher: on every `data_viewer` load, compute expected-last-run from the weekday cron schedule and compare to MAX(`run_at`); if no OK row exists for the most recent expected slot, render a blocking red banner ("Data pipeline has not run since X — signals may be stale"). Add a keep-alive: a lightweight scheduled query (or GHA heartbeat) to prevent the 7-day Supabase pause and the 60-day GHA auto-disable. Make staleness fail-closed: if last successful ingest > N trading days, suppress Kelly amounts entirely.

### GAP-007: Regime read is a race between cron and prediction — no defined join semantics — P1
**Section:** Section 5 (`get_current_regime()`) + Section 2 (`macro_regime` as time series)
**Finding:** `macro_regime` is a time series (one row per `regime_date`). `get_current_regime()` reads the latest row by `regime_date DESC LIMIT 1` and caches it for the calendar day. The design never specifies *which* regime a prediction should be tagged with: the most recent row, or the row as-of prediction time. If a prediction is made before today's cron fires (or the cron drops), the "current" regime is yesterday's or last week's row — silently. There is no as-of-prediction-time join; the prediction inherits whatever the latest row happens to be.
**Risk:** Predictions get tagged with a stale `regime_tag`, contaminating the regime-segmented ledger (Guard 1 — the entire premise that weights never bleed across regimes). A regime transition day is the worst case: predictions emitted that morning are tagged with the prior regime, polluting both segments.
**Fix required before build:** yes (pre-G0)
**Proposed resolution:** Define explicit as-of semantics: tag each prediction with the regime row whose `regime_date <= emitted_at::date`, ordered DESC. Add a freshness guard: if the latest `regime_date` is more than K days behind today, flag the prediction (`regime_stale=true`) or refuse to emit. Document the chosen join in Section 5.

### GAP-008: SQL injection / dimensional mismatch — macro_regime design doc shows UNIQUE that the real migration omits — P1
**Section:** Section 2 (`0004_macro_regime.sql` inline) vs actual migration `20260621100004_macro_regime.sql`
**Finding:** The design doc's inline `0004` SQL shows `regime VARCHAR(20) NOT NULL CHECK (...)` with a comment "no UNIQUE: this is a time-series table." The schema-design expert (Deepak Nair) reviewed a *different* version showing `regime ... NOT NULL UNIQUE` and flagged it as fatal (caps the table at 4 rows). The actual migration file is correct (CHECK-only, no UNIQUE). This is design-doc-vs-migration-vs-expert-review drift: three artifacts describe three different states of the same table.
**Risk:** The expert's top concern is now stale, but nobody has reconciled it. If a future implementer trusts the expert review over the migration, they may "fix" a non-problem or reintroduce the UNIQUE. More broadly: the design doc and the migrations are not guaranteed in sync, so the trace matrix's promise ("every condition maps to an artifact") is undermined — the artifacts disagree.
**Fix required before build:** yes (pre-G0)
**Proposed resolution:** Establish the migration files as the single source of truth, regenerate the design doc's inline SQL from them, and mark the schema-design expert's UNIQUE concern as RESOLVED with a note. Add a CI check that diffs inline-doc SQL against migration files.

### GAP-009: `signal_weights` UNIQUE does not enforce one ACTIVE per segment — P1
**Section:** Section 2 / migration `0009` (`UNIQUE (lynch_class, regime, signal_name, status)`)
**Finding:** The uniqueness key includes `status`. This permits exactly one ACTIVE *and* one PROPOSED *and* one REJECTED per segment+signal — but the review process (Section 5) assumes "the signal engine reads only ACTIVE rows" as if there is exactly one. Across status transitions (PROPOSED→ACTIVE while an older ACTIVE still exists, or a re-proposal), two ACTIVE rows can coexist. The engine's weight load (`WHERE status='ACTIVE' AND lynch_class=X AND regime=Y`) would then return multiple rows for the same signal with no tiebreak.
**Risk:** Nondeterministic weights. Two ACTIVE rows for `(fast_grower, RISK_ON, roic)` → the engine silently picks one (or sums, or errors) depending on implementation. The whole governance premise ("human approves one weight") breaks.
**Fix required before build:** yes (pre-G0)
**Proposed resolution:** Add a partial unique index: `CREATE UNIQUE INDEX ON signal_weights (lynch_class, regime, signal_name) WHERE status='ACTIVE'`. On approval, atomically demote the prior ACTIVE row (to SUPERSEDED) in the same transaction.

### GAP-010: Circuit-locked / illiquid Bhavcopy prints scored as real outcomes — P1
**Section:** Section 7 (`resolve_outcomes.py`) + `0002_ohlcv.sql`
**Finding:** The outcome resolver computes `actual_return` and `peak_return_pct` from raw OHLCV `close`/`high`. Indian cash-segment Bhavcopy prints circuit-locked closes that are not tradeable prices, and `peak_return_pct` from a circuit-day `high` is fictional liquidity. The `ohlcv` schema has no circuit/deliverable-volume field. Illiquid `turnaround` / `asset_play` / microcap names — where circuits are common — get inflated hit rates and peak returns.
**Risk:** The 24-segment ledger systematically over-rewards exactly the illiquid segments where signals are least executable. `peak_return_pct` (the Druckenmiller magnitude metric, Guard 5) is the most corrupted field, and it feeds weight proposals. The model learns to favor unfillable microcap rallies.
**Fix required before build:** no (pre-G1)
**Proposed resolution:** Add `deliverable_volume` and a `circuit_flag` (or derive circuit from open==high==low==close at a band) to `ohlcv`. In `resolve_outcomes.py`, exclude or down-weight circuit-locked days when computing returns, and refuse to score outcomes where deliverable volume is below a liquidity floor.
**(Mandatory target adjacent — see Microstructure assessment.)**

### GAP-011: SEBI substance-over-form — position-sized BUY/EXIT list is advice, not research — P1
**Section:** Section 1 (Layer 4) + Section 6 (rupee Kelly amounts) + Section 1.5 (non-goals)
**Finding:** The product claims research-only, but Layer 4 emits a "ranked BUY/EXIT/REBALANCE/HOLD list per bucket" with specific rupee amounts (₹72,500 max, ₹7,250 min) tied to a specific user's `portfolio_buckets` and holdings. Under SEBI (Investment Advisers) Regulations 2013, personalised position-sized recommendations are investment advice in substance — a yellow footer does not cure it. The C9 test asserts disclaimer *presence* only, never the advice-vs-research substance question.
**Risk:** Today this is a single-user tool (Tarun's own capital), so the RIA boundary likely does not yet bind — but the design names a "first non-self subscriber" as the commercial trigger, and at that instant the path optimizer's output becomes regulated advice with no guardrail change. The accuracy ledger also creates a discoverable trail of "advice."
**Fix required before build:** no (pre-launch / pre-first-subscriber, but the gate must be designed now)
**Proposed resolution:** Define the exact commercial event (recommend: binding it to `waitlist.converted_at` non-null, same trigger as the data-licensing gate) that converts the product to regulated territory, and specify what Layer 4 must suppress at that point (rupee amounts → directional research framing). Add a substance test, not just a presence test. Reframe output language now ("signal X is bullish for instrument Y") rather than imperative BUY.

### GAP-012: yfinance commercial gate hangs on a manual env flag, not on conversion state — P1
**Section:** Section 8 (`ALPHAVEDA_COMMERCIAL=true`) + `COMMERCIAL_GATE.md` + Section 2 (`waitlist.converted_at`)
**Finding:** yfinance personal-use ToS is breached the moment a paying subscriber exists. The exact signal for that is `waitlist.converted_at` going non-null. But the gate fires on a manual boolean env flag (`ALPHAVEDA_COMMERCIAL`) that nothing wires to `converted_at`. The product can silently keep serving yfinance data to a commercial user. `ohlcv.source` is free-text VARCHAR with no licence class, so no query can even answer "is any commercially-served row from a personal-only provider?"
**Risk:** First paying customer = silent ToS breach with no detection. Fail-open by default.
**Fix required before build:** no (pre-launch, but design the binding now)
**Proposed resolution:** Derive commercial state from data, not a flag: a startup check that sets commercial mode if `SELECT count(*) FROM waitlist WHERE converted_at IS NOT NULL > 0`. Make `CommercialLicenseError` fail-closed (block yfinance) when state is ambiguous. Add a `licence_class` column to `ohlcv.source` provenance. When the gate fires inside the GHA cron, it must write `ingest_status` status='FAILED' loudly, not swallow.

### GAP-013: MIN_POSITION_PCT floor forces capital into zero/negative-edge bets — P1
**Section:** Section 6 (`kelly_position_size` final clamp)
**Finding:** The function computes `quarter_kelly = max(0, full_kelly * 0.25)` (correctly zeroing no-edge bets) but the final return is `max(MIN_POSITION_PCT * portfolio_value, min(MAX..., raw))`. The outer `max(MIN, ...)` overrides the zero-edge guard: a signal Kelly says to skip (full_kelly ≤ 0) still gets floored to ₹7,250.
**Risk:** Every no-edge or negative-edge signal that reaches the optimizer receives a 1% allocation. Combined with GAP-001 (which floors nearly everything to MIN anyway), the practical output of the sizer is "put 1% in everything," which is not Kelly at all.
**Fix required before build:** no (pre-G0; trivial once GAP-001 is fixed)
**Proposed resolution:** Short-circuit: if `quarter_kelly == 0`, return 0 (no position / drop from list) before applying the MIN clamp. MIN should floor only positions that already cleared the edge test.

### GAP-014: bucket DB caps vs hardcoded optimizer constants — no precedence rule — P2
**Section:** Section 6 (`MAX_POSITION_PCT=0.10` in optimizer.py) vs `0005_portfolio_buckets.sql` (per-bucket `max_position_pct`, `sector_cap_pct`)
**Finding:** Buckets seed per-bucket caps in the DB; the optimizer hardcodes the same values as module constants. The design never states which wins. A stricter per-bucket DB cap could be silently overridden by the looser hardcoded constant.
**Risk:** A future bucket with a tighter cap (e.g., near_term at 5%) is ignored because the code reads the 10% constant. Silent risk-limit breach.
**Fix required before build:** no (pre-G1)
**Proposed resolution:** DB row is source of truth; delete the hardcoded constants or load them from the bucket row at runtime. Add a test asserting the optimizer respects a DB cap stricter than the constant.

### GAP-015: Hard cutover at 30 observations — no shrinkage between prior and learned weights — P2
**Section:** Section 5 / Section 7 (`OBSERVATION_THRESHOLD = 30`)
**Finding:** `COLD_START_WEIGHTS` are called "Bayesian priors," but Section 7 replaces them "segment-by-segment" at exactly 30 observations — a hard swap, not Bayesian updating. There is no blending/shrinkage between prior and observed.
**Risk:** A discontinuity jolts confidence and sizing the day a segment crosses its 30th observation. Observation 29 uses pure prior; observation 30 uses pure learned weight, which at n=30 is itself high-variance. The "prior" is not actually functioning as a prior.
**Fix required before build:** no (pre-G1)
**Proposed resolution:** Blend with shrinkage: `w = (n/(n+k)) * w_learned + (k/(n+k)) * w_prior`, with `k` a pseudo-count (e.g., 30). Smooth transition, no cliff, and the prior genuinely informs early estimates.

### GAP-016: Streak detection is asymmetric — winning streaks flagged, losing streaks invisible — P2
**Section:** Section 3 (`compute_streak_flag`)
**Finding:** The flag returns True only when the last STREAK_WINDOW outcomes were all correct. There is no mirror for 5 consecutive *wrong* calls — the model-breakdown / capitulation signature. The system can be in sustained failure and emit no warning.
**Risk:** A segment whose model has broken (5+ consecutive misses) keeps emitting at face-value confidence with no skepticism applied, and the user has no signal that the model is failing in that segment.
**Fix required before build:** no (pre-G1)
**Proposed resolution:** Add a `losing_streak_flag` and a corresponding emit-time action (suppress or down-weight, and surface a UI warning "model underperforming in this segment").
**(Mandatory target adjacent — see Behavioral assessment.)**

### GAP-017: Fixed-bottom SEBI disclaimer occludes the last row of every key table — P2
**Section:** Section 4 (`.sebi-disclaimer` CSS, `position: fixed; bottom: 0`)
**Finding:** The fixed bar has no compensating content bottom-margin. Streamlit renders content into a scrolling container; the bar will overlap the final rows of the Fundamentals 8-quarter table, the Path recommendation list, and the Accuracy PROPOSED-rows review UI — the rows that matter most. The C9 test asserts presence/z-index, not non-occlusion.
**Risk:** The compliance fix creates a usability defect on exactly the action surfaces. Worst case, an approve/reject button on the Accuracy tab sits under the bar and is unclickable.
**Fix required before build:** no (pre-G1)
**Proposed resolution:** Add `padding-bottom` (≈ bar height + buffer) to the main content container globally. Add a visual regression / manual test asserting the last interactive element clears the bar.

### GAP-018: Two independent staleness indicators can contradict each other — P2
**Section:** Section 4 (provenance "> 1 trading day" amber STALE badge) vs Section 8 (`ingest_status` FAILED/overdue warning)
**Finding:** `data_viewer` has two separate freshness signals computed from different sources (row `ingested_at` vs `ingest_status.run_at`) with no reconciliation rule. They can disagree on the same page load.
**Risk:** User sees "data fresh" badge next to "ingest overdue" warning, loses trust in both, and learns to ignore staleness signals entirely — defeating the purpose on a financial tool.
**Fix required before build:** no (pre-G1)
**Proposed resolution:** Single source of truth for freshness: derive one consolidated state (FRESH / STALE / PIPELINE_DOWN) from both inputs with a documented precedence, render one badge.

---

## Mandatory Target Assessment

### F2 — Kelly odds dimensionally wrong (GAP-001)
**Confirmed and the design is wrong by construction.** `b = magnitude_target` treats an expected-upside fraction as net odds. Kelly's `b` must be win-size/loss-size; the loss leg does not exist anywhere in the schema or the function signature. How bad is the error? Catastrophic in a quiet way: for any realistic `magnitude_target` (5–20%) and any confidence above ~50, `q/b` dwarfs `p`, the numerator goes negative, gets zeroed, and the final MIN clamp floors the position to 1%. So the sizer silently degenerates into "1% in everything" and the error hides as conservatism. Can it be fixed with the current schema? **No** — there is no column for the loss leg. `accuracy_predictions` has `magnitude_target` but no `downside_target` / stop-loss fraction. The fix requires a schema addition (12th migration). When the loss leg is asymmetric (turnaround: 30% down, 15% up), true `b = 0.15/0.30 = 0.5`, and the correct Kelly fraction is roughly half what a symmetric assumption gives — the current code cannot represent this at all because it has no downside input. **This single defect invalidates Layer 4's rupee output.**

### F3 — Streak discount fires too late (GAP-004)
**Confirmed.** `STREAK_DISCOUNT_FACTOR=0.7` lives only in the Section 3 ledger aggregation SQL. The live emit flow (Section 5, steps 1–7) computes `accuracy_streak_flag` at step 3 but never applies the discount to emitted `confidence`. The discount therefore touches the backward-looking record but not the forward bet. The recalculation that would propagate it is quarterly. So the timeline is: streak forms → confidence rises in real time → Kelly sizes up → ledger quietly records discounted returns → a proposal appears next quarter. At the cycle peak (longest streaks, peak reflexivity, the exact Soros scenario), the engine does the *opposite* of the guard's intent. This is not a tuning issue — it is a logic inversion. The flag is computed in the right place and then ignored where it matters.

### F4 — Confidence calibration gap + arbitration black box (GAP-002, GAP-003)
**Both confirmed.** (a) `confidence/100` is consumed as a calibrated probability with no calibration map and no documented score→confidence function. The ledger measures hit rate but never feeds it back to calibrate `p` — it only drives weight proposals. Uncalibrated confidence is systematically overconfident, inflating Kelly's numerator. (b) `arbitration.py` is named as a core Layer 3 capability and a source file, but has zero specification — no inputs, no logic, no outputs, no constant, no trace-matrix test row. It sits directly upstream of the accuracy ledger, so undefined arbitration silently determines what direction gets logged. Both are P0. Calibration cannot be a post-launch add because every Kelly number depends on it; arbitration cannot be left to implementer guess because it determines ledger contents.

### F5 — Silent inactivity failure (GAP-006)
**Confirmed and worse than stated.** GHA scheduled workflows auto-disable after 60 days of repo inactivity; Supabase free tier pauses after ~7 days idle. The compounding failure: when both pause, Streamlit still loads (it queries whatever is in Supabase) and serves stale data with no error state. `ingest_status` only logs runs that execute — a cron that never fires writes no row, so the "never ran" case is invisible to a staleness check that keys off existing rows. The design specifies *when* a present row is stale but not *who asserts a run should have happened*. There is no keep-alive for either the cron or the Supabase project, and `get_current_regime()`'s singleton has no defined behavior when the DB is paused (likely an unhandled exception on first cold read, or a fallback to the hardcoded `'RISK_ON'` default — which is itself a silent wrong-regime failure).

### E2 — Confidence floor edge case (GAP-005)
**Confirmed paradox.** E2 requires `confidence >= E2_CONFIDENCE_FLOOR (50)` for a BEAR emit to count toward the exit streak. During a genuine deterioration the model's confidence often drops below 50 (high uncertainty). Those emits don't count, the streak never completes, and the exit never fires — precisely when capital preservation matters most. The floor conflates "noisy" with "uncertain"; uncertainty during a decline is signal. The signal is most needed exactly when the floor silences it.

### Shakuni — macro_regime-as-context race condition (GAP-007)
**Confirmed.** `macro_regime` is stored as a time series but used as a point-in-time context. `get_current_regime()` reads `regime_date DESC LIMIT 1` and caches per calendar day; the design never specifies which regime row a prediction joins (most recent vs as-of-prediction-time). If the cron hasn't fired today (or dropped), "current" is silently yesterday's or last week's row. On a regime-transition day, morning predictions get tagged with the prior regime, contaminating the regime-segmented ledger that Guard 1 exists to protect. The fallback default `'RISK_ON'` when `macro_regime` is empty (Section 5 code) is an additional silent-wrong-regime hazard. This is a real ingest-vs-prediction race with no defined ordering or freshness guard.

---

## Verdict Rationale

**REVISE**, not CONDITIONAL_PASS, for three reasons:

1. **Four P0 gaps, and their fixes are not mechanical.** CONDITIONAL_PASS requires P0s with clear, ready fixes. GAP-001 (Kelly) needs a new schema column and a re-derivation; GAP-002 (calibration) needs an entire layer the design has no slot for; GAP-003 (arbitration) needs a from-scratch specification of critical-path logic; GAP-006 (missing-run detection) needs an active watcher plus keep-alive infrastructure. These are design re-specifications, not execution details.

2. **The headline feature is invalid as designed.** Layer 4 (path optimizer with Kelly sizing) is one of three co-equal product layers. GAP-001 + GAP-002 + GAP-013 mean its rupee output is mathematically unsound and degenerates to "1% in everything." Shipping a financial tool whose marquee number is wrong-by-construction is worse than shipping without it.

3. **Multiple council guards are inverted, not merely incomplete.** GAP-004 (Soros) and GAP-005 (E2) are logic inversions baked into constants and data flow — the guards fire in the wrong direction or at the wrong time. These were the specific conditions the council mandated; implementing them backwards defeats the review that approved the design.

The design is close. The architecture, trace matrix, and migration discipline are genuinely good, and most P1/P2 gaps are straightforward. But the mathematical core of the value proposition must be re-specified before build. Re-issue as v0.4 with: a loss-leg schema column, a calibration layer, a full arbitration spec, an active missing-run watcher, emit-time streak discounting, and a redesigned E2 uncertainty path. Then re-review.
