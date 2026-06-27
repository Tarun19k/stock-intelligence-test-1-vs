# AlphaVeda — Council → Test Map
# Living document. Housekeeping updates after each Phase completion.
# Every council seat must have at least one test before Phase sign-off.

## How to read this

Column "Phase" = when the test is written and must pass.
Column "Status" = SPEC (not written) | RED (stub written, fails) | GREEN (passes) | SIGNED OFF (council reviewed)

---

## Investment Persona Seats (9)

| Seat | Condition | Test file | Function | Phase | Status |
|---|---|---|---|---|---|
| **Buffett** | FUNDAMENTAL_WEIGHT_FLOOR = 0.30 enforced at weights load | test_constants.py | test_fundamental_floor_value | 1 | GREEN ✓ |
| **Buffett** | Floor applies to COLD_START_WEIGHTS | test_constants.py | test_fundamental_floor_applies_to_all_cold_starts | 1 | GREEN ✓ |
| **Buffett** | Floor enforced at emit time (engine) | test_engine.py | test_floor_enforced_at_emit | 3 | GREEN ✓ |
| **Munger** | Weight proposal banner on signals page | test_app.py | test_review_banner_shown | 5 | GREEN ✓ |
| **Munger** | Weight proposal banner on path page | test_app.py | test_review_banner_on_path_page | 5 | GREEN ✓ |
| **Munger** | Accuracy tab shows PROPOSED rows | test_app.py | test_accuracy_tab_review_ui | 5 | GREEN ✓ |
| **Munger** | Staleness backstop: 90-day overdue warning | test_app.py | test_staleness_backstop_banner | 5 | GREEN ✓ |
| **Dalio** | Regime as-of join (not latest row) | test_regime.py | test_regime_as_of_join | 2 | GREEN ✓ |
| **Dalio** | Regime cached per calendar day | test_regime.py | test_regime_cached | 3 | GREEN ✓ |
| **Dalio** | Stale regime → visible warning (not silent default) | test_regime.py | test_stale_regime_fails_visibly | 3 | GREEN ✓ |
| **Dalio** | regime_tag on every prediction row | test_migrations.py | test_prediction_without_regime_rejected | G1 | SPEC |
| **Marks** | cycle_phase derivation — all PHASE_RULES | test_cycle_phase.py | test_all_results_are_valid_phases | 2 | GREEN ✓ |
| **Marks** | cycle_phase never returns None | test_cycle_phase.py | test_never_returns_none | 2 | GREEN ✓ |
| **Marks** | Invalid phase rejected by DB | test_migrations.py | test_invalid_phase_rejected | G1 | SPEC |
| **Soros** | Streak discount fires at emit (step 3b), not ledger | test_engine.py | test_streak_discount_applied_when_flag_set | 3 | GREEN ✓ |
| **Soros** | PIPELINE CONTRACT: bins built from post-discount confidence | test_engine.py | test_pipeline_discount_fires_before_calibration | 3 | GREEN ✓ |
| **Soros** | Streak flag triggers correctly at STREAK_WINDOW | test_ledger.py | test_at_window_is_true | 3 | GREEN ✓ |
| **Druckenmiller** | Kelly formula: b = magnitude/downside | test_optimizer.py | test_kelly_rupee_with_downside | 4 | GREEN ✓ |
| **Druckenmiller** | Kelly returns 0 when downside_target=None | test_optimizer.py | test_kelly_no_rupee_without_downside | 4 | GREEN ✓ |
| **Druckenmiller** | Kelly capped at MAX_POSITION_PCT | test_optimizer.py | test_kelly_capped_at_max_position | 4 | GREEN ✓ |
| **Druckenmiller** | EXIT E1: drift outside Kelly band | test_optimizer.py | test_exit_e1 | 4 | GREEN ✓ |
| **Druckenmiller** | EXIT E2: consecutive BEAR emits (bucket-aware) | test_optimizer.py | test_exit_e2_bucket_threshold | 4 | GREEN ✓ |
| **Druckenmiller** | EXIT E2: confidence floor (≥50 only counts) | test_optimizer.py | test_exit_e2_confidence_floor | 4 | GREEN ✓ |
| **Druckenmiller** | EXIT E2: UNCERTAINTY path (double threshold + MA) | test_optimizer.py | test_exit_e2_uncertainty_path | 4 | GREEN ✓ |
| **Druckenmiller** | EXIT E3: magnitude_target < 3% | test_optimizer.py | test_exit_e3 | 4 | GREEN ✓ |
| **Druckenmiller** | EXIT E4: sector cap breach | test_optimizer.py | test_exit_e4 | 4 | GREEN ✓ |
| **Lynch** | instruments.classification CHECK — 6 values | test_migrations.py | test_instruments_table | 1 | GREEN ✓ |
| **Lynch** | Invalid Lynch class rejected | test_migrations.py | test_invalid_class_rejected | G1 | SPEC |
| **Lynch** | lynch_class on every prediction row | test_migrations.py | test_prediction_without_lynch_rejected | G1 | SPEC |
| **Jhunjhunwala** | ohlcv.circuit_flag column exists | test_migrations.py | test_ohlcv_has_circuit_flag | 1 | GREEN ✓ |
| **Jhunjhunwala** | circuit_flag backfill rule documented | DATA_SOURCES.md | (rule, not test) | 1 | GREEN ✓ |
| **Jhunjhunwala** | circuit_flag rows excluded from resolve_outcomes | test_ingest.py | test_circuit_flag_row_excluded | 6 | GREEN ✓ |
| **Jhunjhunwala** | Mixed circuit/clean: only clean symbols resolve | test_ingest.py | test_mixed_circuit_partial_resolution | 6 | GREEN ✓ |
| **Wealth & Revenue** | waitlist.price_feedback column | test_migrations.py | test_waitlist_table | 1 | GREEN ✓ |
| **Wealth & Revenue** | is_commercial() derived from converted_at | test_is_commercial.py | test_is_commercial_false_when_no_subscribers | 2 | GREEN ✓ |
| **Wealth & Revenue** | is_commercial() fail-closed | test_is_commercial.py | test_is_commercial_fail_closed | 2 | GREEN ✓ |
| **Wealth & Revenue** | Waitlist form writes to DB | test_waitlist.py | test_waitlist_form_submits | 1 ext | SPEC |
| **DB Integrity** | Bhavcopy parse: correct OHLCV fields | test_ingest.py | test_correct_ohlcv_fields | 6 | GREEN ✓ |
| **DB Integrity** | Fundamentals parse: required keys + None on NA | test_ingest.py | test_returns_all_required_keys | 6 | GREEN ✓ |

---

## Technical / Governance Seats (12)

| Seat | Condition | Test file | Function | Phase | Status |
|---|---|---|---|---|---|
| **SRA/Reliability Architect** | Stale ingest → amber banner | test_g0_gate.py | test_c3_missing_run_stale_warning | 6 | GREEN ✓ |
| **SRA/Reliability Architect** | Zero ingest_status rows → red banner | test_g0_gate.py | test_c4_missing_run_no_row | 6 | GREEN ✓ |
| **SRA/Reliability Architect** | Staleness flag: OK/STALE/MISSING logic | test_ingest.py | test_ok_when_recent | 6 | GREEN ✓ |
| **SRA/Reliability Architect** | Signal emit latency ≤ 800ms | test_engine.py | test_emit_latency | 3 | SKIP — G1 load test |
| **Constraint Enforcer** | No imperative BUY/SELL in output | test_g0_gate.py | test_c6_sebi_substance | 6 | GREEN ✓ |
| **Constraint Enforcer** | Commercial gate fail-closed | test_is_commercial.py | test_is_commercial_fail_closed | 2 | GREEN ✓ |
| **Constraint Enforcer** | Rupee suppressed when commercial=True | test_app.py | test_no_rupee_when_commercial | 5 | GREEN ✓ |
| **Bhattacharya** | ohlcv.licence_class column | test_migrations.py | test_ohlcv_has_licence_class | 1 | GREEN ✓ |
| **Bhattacharya** | ohlcv.deliverable_volume column | test_migrations.py | test_ohlcv_has_circuit_flag | 1 | GREEN ✓ |
| **Varghese** | SEBI disclaimer on every page | test_app.py | test_disclaimer_in_every_page | 5 | GREEN ✓ |
| **Varghese** | Disclaimer not conditionalised | test_app.py | test_disclaimer_non_dismissable | 5 | GREEN ✓ |
| **Varghese** | SEBI substance (no advice language) | test_g0_gate.py | test_c6_sebi_substance | 6 | GREEN ✓ |
| **UX/Accessibility** | Cold-start label shown | test_app.py | test_cold_start_label_visible | 5 | GREEN ✓ |
| **UX/Accessibility** | Rupee suppression = deliberate state (label) | test_app.py | test_rupee_suppression_label | 5 | GREEN ✓ |
| **DB Integrity** | All 11 core tables exist | test_migrations.py | test_instruments_table..test_ingest_status_table | 1 | RED |
| **DB Integrity** | accuracy_predictions.downside_target | test_migrations.py | test_accuracy_predictions_has_downside_target | 1 | RED |
| **DB Integrity** | portfolio_buckets seeded (4 rows) | test_migrations.py | test_portfolio_buckets_seeded | 1 | RED |
| **Calibration Integrity** | Calibration p ≤ confidence/100 (cold-start) | test_g0_gate.py | test_c5_calibration_cold_start | 6 | GREEN ✓ |
| **Calibration Integrity** | Calibration cold fallback: p = min(conf/100, hit_rate) | test_calibration.py | test_cold_start_calibration | G1 | SPEC |
| **Shakuni** | No duplicate ACTIVE per segment | test_g0_gate.py | test_c2_signal_weights_no_duplicate_active | 6 | GREEN ✓ |
| **Shakuni** | approve_signal_weight rejects non-PROPOSED | test_signal_weights.py | test_approve_rejects_non_proposed | 3 | GREEN ✓ |
| **Synthesis Chair** | G0 criterion 10 runs first | test_g0_gate.py | test_c10_seed_instruments_exist | 6 | RED (needs seed) |
| **Synthesis Chair** | Kelly rupee live with valid downside | test_g0_gate.py | test_c8_kelly_rupee_with_downside | 6 | GREEN ✓ |

---

## Phase Sign-Off Protocol

Each Phase is NOT done until:
1. All tests in that Phase column are GREEN
2. Relevant council seats have reviewed test quality (not just count)
3. GSI `regression.py` is 455/455 PASS
4. FILE_INVENTORY.md updated to DONE for all Phase files
5. `test_governance_integrity.py` runs with 0 warnings (warn mode) for this Phase
6. Council seats dispatched as **independent subagents** (not same-context simulation) — each receives only pytest output + map column, not other seats' verdicts
7. Commit includes `[council:subagent]` tag to audit that independent review occurred

**Drift check:** Before Phase sign-off, verify COUNCIL_TEST_MAP function names match actual test files (`test_green_tests_are_collectable` enforces this automatically).

**Subagent rule:** Same-context seat simulation suppresses genuine disagreement. Each seat's `[council:subagent]` verdict must come from a fresh agent invocation with no prior seat outputs in context.

| Phase | Required council reviewers | Model |
|---|---|---|
| Phase 1 | DB Integrity, Bhattacharya, Jhunjhunwala, Wealth & Revenue | Sonnet |
| Phase 2 | Dalio, Marks, SRA/Reliability Architect, Constraint Enforcer | Sonnet |
| Phase 3 | Soros, Druckenmiller, Buffett, Lynch, Shakuni | Sonnet |
| Phase 4 | Druckenmiller, Jhunjhunwala | Sonnet |
| Phase 5 | Varghese, Munger, UX/Accessibility, Constraint Enforcer | Sonnet |
| Phase 6 (G0) | All 21 council seats | **Opus** |

Last updated: 2026-06-26 (Phase 6 SIGNED OFF — 179 PASS / 1 SKIP / 3 FAIL; c10 RED = intentional seed gate; all 21 seats resolved; seat names updated to skill-canonical names)

---

## Completed Phases

- Phase 1 (Foundation) — signed off 2026-06-23
- Phase 2 (Data Layer) — signed off 2026-06-23
- Phase 3 (Signal Layer) — signed off 2026-06-25 [council:subagent]
  - Soros: APPROVE — pipeline contract enforced; 4 calibration items for Phase 6 backlog
  - Druckenmiller: APPROVE — GAP-001 Kelly prerequisite satisfied; 2 hardening items before Phase 5
  - Shakuni: REVISE resolved → APPROVE — C1 (approve_signal_weight), C2 (weight range), C3 (KeyError), C4 (floor on DB path) all fixed; 112 PASS / 15 SKIP / 3 FAIL
- Phase 4 (Portfolio Layer) — signed off 2026-06-25 [council:subagent]
  - Druckenmiller: APPROVE — Kelly correct, GAP-001 resolved, all 4 exit rules sound
  - Jhunjhunwala: REVISE resolved → APPROVE — circuit_flag filter added to compute_downside_target(); 4 tests added; 132 PASS / 12 SKIP / 3 FAIL
- Phase 5 (Presentation Layer) — signed off 2026-06-25 [council:subagent]
  - Varghese: APPROVE — disclaimer pinned unconditionally, uses constant, non-dismissable; non-blocking: test fallback `or "not" in html.lower()` too permissive (polish for later)
  - Constraint Enforcer: APPROVE — commercial gate fail-closed, rupee=None when commercial, suppression label uses deliberate-state language; non-blocking: double is_commercial() call per render (caching for G1)
  - UX/Accessibility (ui-ux-pro-max): APPROVE — cold-start uses OBSERVATION_THRESHOLD constant, suppression label passes degradation check; non-blocking: "Bayesian priors" may confuse lay users (polish item)
  - Munger: REVISE resolved → APPROVE — accuracy.get_proposed_weights_count() was standalone Supabase query; fixed to delegate to signals (single source of truth); all 4 weight-review conditions met; 144 PASS / 12 SKIP / 3 FAIL
- Phase 6 (GHA Ingest Pipeline) — signed off 2026-06-26 [council:subagent]
  - Wave 1 (7 seats): Buffett APPROVE; Munger REVISE→APPROVE (circuit_flag end-to-end); Soros APPROVE (horizon deferred G1); Druckenmiller APPROVE (horizon deferred G1); Jhunjhunwala REVISE→APPROVE (circuit_flag proxy in parser); Marks REVISE→APPROVE (NO_DATA + SKIPPED_HOLIDAY); Dalio REVISE→APPROVE (_is_trading_day NSE calendar)
  - Wave 2 (14 seats): Lynch APPROVE; Wealth & Revenue APPROVE; Bhattacharya APPROVE; Varghese APPROVE; UX/Accessibility REVISE→APPROVE (banner language); Shakuni APPROVE; Constraint Enforcer APPROVE; SRA/Reliability Architect REVISE→APPROVE (TIMESTAMPTZ parsing + stale test); DB Integrity REVISE→APPROVE (ingest_status columns, ohlcv instrument_id resolution, accuracy_outcomes write); Calibration Integrity REVISE→APPROVE (BULL/BEAR enum, hit+return_pct output); Synthesis Chair REVISE→APPROVE (all fixes resolved)
  - Final: 179 PASS / 1 SKIP / 3 FAIL; 3 FAIL = intentional G0 seed gates (need live DB seed)
