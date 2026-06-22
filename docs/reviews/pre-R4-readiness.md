# Pre-R4 Readiness Council — CoS-Led
**Date:** 2026-06-22
**Led by:** Chief of Staff
**Council:** 21 voices (7 investor + 4 doctrine + 9 expert + Wealth & Revenue Strategist)
**Input:** Design doc v0.4 + migrations 0011 (schema_fixes) / 0012 (downside_target)
**Verdict:** CONDITIONAL READY

---

## CoS State Brief (Observer Mode)

Block 3.1 was re-scoped per R3's Synthesis Chair adjudication from "amend design doc" to "produce v0.4 + dependent migrations + gate bindings." This readiness check verifies what actually landed in the files against that mandate. State, faithfully reported:

**What v0.4 produced (verified present):**
- **Migration 0012** adds `accuracy_predictions.downside_target NUMERIC(6,4) CHECK (>0 AND <=1.0)` — the Kelly loss leg. Targets the correct live table (`accuracy_predictions.id` is BIGSERIAL, confirmed in live 0007). Present and correct as a schema object.
- **Migration 0011 (schema_fixes)** batches four changes per MA-9: (a) partial unique index `signal_weights_one_active_per_segment WHERE status='ACTIVE'`; (b) `approve_signal_weight(p_id INT)` atomic demote-then-promote; (c) status CHECK extended to include `'SUPERSEDED'`; (d) `accuracy_outcomes UNIQUE (prediction_id)` idempotency; (e) `ohlcv.circuit_flag` + `deliverable_volume`; (f) `ohlcv.licence_class`. All schema objects present.
- **Kelly rewrite (Section 6):** `b = magnitude_target / downside_target`; NULL-downside returns 0 (no rupee); MIN floor removed from the zero-edge path; `p` documented as calibrated, not raw confidence.
- **Arbitration (Section 5.7):** weighted-vote rule with `ARBITRATION_MARGIN = 15.0` suppression band — the P0-chain head is now specified.
- **Calibration (Section 5.8):** per-segment empirical decile binning; cold-segment fallback `p = min(confidence/100, measured_hit_rate)`; cold-forever note (MA-14).
- **Emit-time streak discount (Section 5, step 3b):** discount fires at live emit before Kelly and ledger write — GAP-004 inversion addressed structurally.
- **E2 redesign (Section 6):** PRIMARY confident path + UNCERTAINTY path (double threshold AND below-200MA).
- **Regime as-of join (Section 5):** `regime_date <= emitted_at::date DESC LIMIT 1`; silent RISK_ON fallback removed; `REGIME_STALENESS_DAYS = 3` freshness guard.
- **Commercial gate (Section 8.5):** derived from `waitlist.converted_at`, fail-closed; substance test C9b.
- **G0 gate** upgraded from 6/6 to 10 criteria testing the found defects directly.

**Ground-truth checks the CoS ran on the live migration directory:**
- `emitted_at` **EXISTS** in live 0007 (line 10) — the regime as-of join references a real column.
- `converted_at` **EXISTS** in live `20260621100011_waitlist.sql` (line 14) — the commercial gate references a real column.
- **TWO files now carry ordinal 0011**: `20260621100011_waitlist.sql` (original) and `20260622100011_schema_fixes.sql` (new). Full date-prefixed sort keeps them distinct and ordered, but the duplicated human ordinal is a latent hazard.

**What remains open (the substance of this council's findings):**
1. `downside_target` has a *column* but no *producer* — ATR(14)/price is named in a comment, never specified as a module.
2. The 0011 partial index has no pre-existing-violation cleanup before `CREATE UNIQUE INDEX`.
3. Calibration bins are learned from undiscounted historical confidence but consumed post-discount — a bin-mismatch cascade.
4. G0 criterion ordering (apply-0011 vs test-uniqueness) is unspecified for a fresh CI DB.

---

## Council Readiness Challenges

### 1. Warren Buffett (GAP-010 circuit, GAP-012 yfinance) — CONDITIONAL
**Q1:** `ohlcv.circuit_flag` and `deliverable_volume` columns are present in 0011 (schema pre-work). But the design itself states GAP-010 enforcement is `resolve_outcomes.py` exclusion logic, explicitly deferred to G1. The *schema* is fixed; the *learning-loop protection* is not yet code. Sufficient for R4 (schema landed), not for G1.
**Q2:** New risk — `circuit_flag BOOLEAN NOT NULL DEFAULT FALSE`. Every historical ingest before the resolver is taught to set it will carry FALSE, silently scoring circuit days as real until the G1 logic ships. The default masks absence of detection.
**Q3:** No R4 blocker. GAP-010 is correctly a hard pre-G1 gate; flagged, not blocking R4 synthesis.

### 2. Charlie Munger (GAP-008 drift, GAP-009 ACTIVE uniqueness, GAP-013 MIN floor) — FAIL
**Q1:** GAP-009 root cause is NOT fully fixed. The partial index is correct *for future state*, but migration 0011 runs `CREATE UNIQUE INDEX signal_weights_one_active_per_segment` against a table whose live defect (status-in-UNIQUE) may have already permitted two ACTIVE rows per segment. `CREATE UNIQUE INDEX` on a table that already violates the constraint **fails at apply time** with a duplicate-key error. There is no `DELETE`/`UPDATE ... SUPERSEDED` cleanup step before the index creation. The migration is non-idempotent against a dirty table and will abort, leaving the fix unapplied — the doc reads fixed, the DB stays broken (exactly the trap Shakuni named in R3).
**Q2:** New risk — the status CHECK is dropped and re-added (`DROP CONSTRAINT IF EXISTS ... ADD CONSTRAINT`). If any live row already holds a value outside the new set this is fine, but if the index creation aborts first, the CHECK change may or may not have committed depending on whether the migration runs in one transaction. Transaction boundary is unstated.
**Q3:** R4 BLOCKER. R4 synthesis assumes the schema fixes are applyable. A migration that aborts on a dirty table is not buildable as written.

### 3. Ray Dalio (GAP-007 regime join, GAP-008) — PASS
**Q1:** GAP-007 fixed at root. The as-of join `regime_date <= emitted_at::date DESC LIMIT 1` is specified, the silent RISK_ON fallback is removed, and `emitted_at` **exists in live 0007** (CoS verified line 10) — so the join references a real column. The challenge routed to this seat (that `emitted_at` might not exist) is REFUTED by the live file. Sufficient.
**Q2:** None. The freshness guard (REGIME_STALENESS_DAYS=3, fail-visible) is the correct second-order fix.
**Q3:** None.

### 4. Stanley Druckenmiller (GAP-001 Kelly, GAP-005 E2, GAP-014 DB caps) — FAIL
**Q1:** GAP-001 formula is now dimensionally correct (`b = magnitude/downside`). BUT the input pipeline is unspecified: `downside_target` has a column (0012) and a NULL-guard (return 0), yet **no module produces it**. The comment says "signal-emitted stop-loss fraction, or ATR(14)/price as default" — ATR(14) is never defined anywhere in the design (no `atr.py`, no constant, no formula, no trace-matrix row). So on Day 1, every signal that does not emit a stop-loss has `downside_target = NULL` → Kelly returns 0 → Path page shows direction only → **Layer 4's rupee output never appears**. The formula is correct and the marquee feature is still dark. GAP-014 (DB cap precedence) is unaddressed in v0.4 — still pre-G1.
**Q2:** New risk — the NULL→0 path is silent. A reviewer sees "Kelly fixed" but never sees a rupee amount, and cannot tell whether that is correct suppression or a missing producer. Indistinguishable failure modes.
**Q3:** R4 BLOCKER. R4 cannot synthesize a buildable Layer 4 when the loss-leg producer is unspecified. This is MA-3 ("specify where downside_target comes from") marked resolved in prose but not actually resolved.

### 5. Howard Marks (GAP-015 shrinkage, GAP-016 asymmetric streak) — CONDITIONAL
**Q1:** Both correctly pre-G1. The cold-forever note (MA-14) is present and pairs the calibration transition with shrinkage intent. Acceptable for R4.
**Q2:** New risk — the design says "build calibration on shrinkage not a hard cutover" but no shrinkage formula (`w = n/(n+k)·w_learned + k/(n+k)·w_prior`) is written into v0.4. The hard 30-obs cutover still stands in Section 7. The cliff Marks warned of in R3 is not yet removed — only acknowledged.
**Q3:** None for R4 (pre-G1).

### 6. George Soros (GAP-004 streak discount at emit) — FAIL
**Q1:** The discount now fires at step 3b (emit time) — the timing inversion is fixed. BUT the fix introduces a calibration cascade defect (see routed challenge). Step 3b multiplies emitted confidence by 0.7. Step 5.8 then maps that *discounted* confidence to a calibrated `p` using bins built from *undiscounted* history. A signal whose true confidence was 100 arrives at calibration as 70; the bin for "70" was learned from outcomes where 70 meant no-streak. So the streak prediction is calibrated against the wrong reliability bin — under-discounted or over-discounted unpredictably. The guard now fires at the right *time* but corrupts the *calibration* it feeds. Half-fixed.
**Q2:** New risk — double discount. The ledger SQL ALSO applies 0.7 (Section 3, retained as "secondary check"). If both the emit path and the ledger path discount, streak returns are multiplied by 0.49, not 0.7. The "secondary check" is now redundant-and-compounding, not a backstop.
**Q3:** R4 BLOCKER (shared with Menon/Reddy). The emit→calibration ordering must be resolved before the P0 chain is declared self-consistent.

### 7. Peter Lynch (classification integrity, cold-start coherence) — PASS
**Q1:** Classification CHECK enforced in live 0001; cold-start priors present per segment; cold-forever behavior now explicitly stated (priors hold). Coherent.
**Q2:** Minor — `COLD_START_WEIGHTS` test asserts sum-to-1.0 per segment, but FUNDAMENTAL_WEIGHT_FLOOR adjustment "before use" could break that sum; the interaction is untested. Note, not block.
**Q3:** None.

### 8. Shakuni (Red Team — attacks Block 3.1 output) — FAIL
**Q1 (attack the fix):** Three live holes in Block 3.1's own output:
- **The G0 gate is self-defeating.** Criterion 2 (single-ACTIVE uniqueness) tests the partial index. Criterion 10 (apply 0011/0012) is what *creates* that index. On a fresh CI DB the gate does not specify that 10 runs before 2 — if criteria run in listed order, criterion 2 tests a table with no index and **passes vacuously** (zero rows, no violation), verifying nothing. The gate that was upgraded to catch the found defects cannot catch GAP-009 on a clean DB.
- **The 0011 index aborts on a dirty DB** (Munger's finding) — so on the *production* DB the gate's criterion 10 ("applied without error") fails, and on a *fresh* DB criterion 2 passes meaninglessly. There is no DB state where the gate both applies and verifies.
- **Duplicate 0011 ordinal.** Two files named ...100011...; anyone referencing "migration 0011" by ordinal is now ambiguous.
**Q2:** New risk — `approve_signal_weight()` reads `lynch_class/regime/signal_name` via three correlated subqueries on `id = p_id`; if called with a non-PROPOSED id it silently no-ops the promote but still runs the demote, potentially demoting a live ACTIVE with nothing promoted to replace it. No guard that p_id is PROPOSED before demoting.
**Q3:** R4 BLOCKER — the verification gate is not trustworthy.

### 9. Constraint Enforcer (SEBI substance, commercial gate, premortem) — CONDITIONAL
**Q1:** Commercial gate design is present (8.5), derived from `converted_at` (which EXISTS in live waitlist — verified), fail-closed, C9b substance test specified. Gate *design* satisfied per the R3 condition (enforcement deferred is acceptable).
**Q2:** New risk — `is_commercial()` fail-closed assumes commercial=True on Supabase unreachable, blocking yfinance. Correct for ToS. But the same unreachable state also drives the missing-run watcher and regime read; one Supabase outage cascades into three independent fail-closed behaviors with no unified degraded-state UX. Unowned interaction.
**Q3:** Premortem governance — this readiness review touches the design doc (architectural-trigger surface). Premortem must be logged before the v0.5 corrective writes that this council mandates. Not an R4 blocker but a process gate on the next write.

### 10. Systems Reliability Architect (async ingest, apply order, idempotency) — FAIL
**Q1:** Idempotency `UNIQUE (prediction_id)` on accuracy_outcomes is present in 0011 — good. Async ingest separation is specified. BUT migration apply *order* and *transactionality* are unspecified: 0011 batches six DDL operations with no `BEGIN/COMMIT` wrapper shown and no ordering guarantee that the cleanup (absent anyway) precedes the index. Partial application of a six-statement migration leaves the schema in an undefined intermediate state.
**Q2:** New risk — `ADD CONSTRAINT accuracy_outcomes_prediction_unique UNIQUE` (not `IF NOT EXISTS`, unlike the ohlcv ADD COLUMNs). Re-running 0011 after a partial failure aborts on the already-existing constraint. The migration is not idempotent on re-run — the exact PARTIAL-rerun case Imran's finding was meant to close, reintroduced in the fix for it.
**Q3:** R4 BLOCKER — migration apply correctness is a build prerequisite.

### 11. Synthesis Chair — ENGAGED
≥2 seats disagree substantively (see dedicated section). Munger/Druckenmiller/Soros/Shakuni/SRE return FAIL; Dalio/Lynch/Reddy-partial return PASS on adjacent points. Engaged.

### 12. Prof. Sanjay Iyer (portfolio-theory — Kelly, calibration math) — FAIL
**Q1:** Kelly formula math is now correct. Calibration method (empirical decile binning) is sound in principle. BUT two math defects survive: (a) the downside_target producer is unspecified (shared with Druckenmiller) so Kelly cannot run; (b) the calibration bin mismatch (shared with Soros) — feeding post-discount confidence into pre-discount bins is a calibration error, not just an engineering ordering nit. The corrected `p` is systematically wrong for streak rows.
**Q2:** New risk — cold-segment fallback `p = min(confidence/100, measured_hit_rate)` uses `measured_hit_rate` which, per Bhattacharya, is itself corrupted until GAP-010 enforcement ships. Calibration floor rests on an uncleaned metric.
**Q3:** R4 BLOCKER — the P0 chain (arbitration→confidence→calibration→Kelly) is not yet self-consistent at the discount/calibration seam.

### 13. Dr. Anika Reddy (signal-engineering — arbitration, emit flow) — CONDITIONAL
**Q1:** Arbitration (5.7) is now fully specified — inputs, weighted-vote rule, suppression band, three test rows. The spec void GAP-003 is genuinely closed. Emit flow is ordered.
**Q2:** New risk — arbitration emits "winning side score normalised to [0,100]" as confidence, THEN step 3b discounts it, THEN 5.8 calibrates. Three sequential transforms on one number with no single documented pipeline diagram. The normalisation function ("normalised to [0,100]") is itself unspecified — by what scale?
**Q3:** Conditional — the emit→discount→calibration pipeline must be written as one ordered contract (this is the cascade Menon/Soros/Iyer all hit from different angles).

### 14. Dr. Kavya Menon (behavioral-finance — E2, streak emit) — FAIL
**Q1:** E2 redesign (PRIMARY + UNCERTAINTY path) correctly splits the floor's two jobs — the deterioration paradox is structurally fixed. Streak discount moved to emit — correct. BUT (the routed cascade): the behavioral intent of Guard 2 (skepticism at the peak) is undermined by the calibration mismatch — a discounted confidence calibrated against undiscounted bins may map *back up* to a higher `p` than intended, partially un-doing the skepticism the discount applied. The behavioral guard and the calibration layer fight each other.
**Q2:** New risk — double-discount (emit + ledger SQL) compounds to 0.49, over-penalising streaks beyond the 0.7 design intent. Behaviorally this swings from "inverted guard" (v0.3) to "over-aggressive guard" (v0.4) — corrected past the target.
**Q3:** R4 BLOCKER — the discount/calibration interaction must be resolved.

### 15. Deepak Nair (schema-design — 0011/0012 correctness, no-regression) — FAIL
**Q1:** 0012 is correct and targets the right table. 0011 is mostly correct but has the GAP-009 root-cause hole: no pre-existing-violation cleanup before `CREATE UNIQUE INDEX`. The migration assumes a clean table; the live defect means it may not be. A `DELETE`/demote of pre-existing duplicate ACTIVEs (keeping the most recent `approved_at`) must run *before* the index.
**Q2:** New risks (regression): (a) `ADD CONSTRAINT ... UNIQUE` is not `IF NOT EXISTS` → non-idempotent on re-run; (b) no transaction wrapper on a six-statement migration; (c) duplicate 0011 ordinal across two files; (d) `approve_signal_weight` has no PROPOSED-guard before demote.
**Q3:** R4 BLOCKER — migration correctness is the schema seat's R4 sign-off and it is not clean.

### 16. Adv. Meera Sundaram (sebi-compliance — commercial gate substance) — PASS
**Q1:** Gate binds to `converted_at` (verified to exist), C9b substance test asserts no imperative BUY/SELL and rupee suppression at commercial=True. Substance-over-presence requirement met in design. Sufficient for R4 (enforcement pre-launch).
**Q2:** None new. Reframed language ("X is bullish") is specified now.
**Q3:** None for R4.

### 17. Rohan Varghese (data-licensing — licence_class, yfinance gate) — PASS
**Q1:** `ohlcv.licence_class TEXT CHECK (personal|commercial|open) DEFAULT 'personal'` present in 0011. The query "is any commercially-served row from a personal-only provider" is now answerable. Sufficient.
**Q2:** Minor — DEFAULT 'personal' means every pre-existing row is tagged personal regardless of true source; a backfill rule for already-ingested rows is unspecified. Note, not block.
**Q3:** None.

### 18. Vikram Bhattacharya (market-microstructure — circuit_flag adequacy) — CONDITIONAL
**Q1:** `circuit_flag` + `deliverable_volume` columns are adequate *as schema*. But circuit detection logic (open==high==low==close at band) is not written, and India-VIX calibration of VIX_CALM_THRESHOLD=18.0 (flagged in R3) is still uncalibrated. Dual-listed NSE/BSE conflicting-outcome case still undefined.
**Q2:** New risk — `circuit_flag DEFAULT FALSE` scores all history as non-circuit until detection ships (shared with Buffett).
**Q3:** None for R4 (pre-G1), but GAP-010 enforcement remains a hard pre-G1 gate.

### 19. Tanvi Rao (product-ux — suppression UX, G0 testability) — CONDITIONAL
**Q1:** Suppression-as-deliberate-state note present (8.5). G0 criterion 6 (no rupee without downside) and criterion 7 (disclaimer non-occlusion) are testable. Acceptable.
**Q2:** New risk — with the downside_target producer unspecified (Druckenmiller), the Path page will show direction-only for EVERY signal on Day 1, not as a designed commercial-gate state but as a "feature never appeared" state. The deliberate-suppression UX was designed for the commercial transition, not for a Day-1 empty-producer state — these are different states presented identically.
**Q3:** None blocking, but UX must distinguish "suppressed by gate" from "no downside producer yet."

### 20. Imran Sheikh (systems-reliability — idempotency, missing-run watcher) — FAIL
**Q1:** `UNIQUE (prediction_id)` closes the double-write on resolve — the contract I asked for. BUT the constraint is added via `ADD CONSTRAINT` without `IF NOT EXISTS`, so the migration that implements my idempotency fix is itself non-idempotent on re-run — a PARTIAL-failed 0011 cannot be safely re-applied. The fix for re-run safety is not re-run safe.
**Q2:** New risk — the missing-run watcher (GAP-006) is specified in prose (Section 7/8) but has no migration object and no G0 criterion testing that the watcher fires on a genuinely-never-ran (no-row) case. Criterion 3 tests "stop ingest, advance clock" — that tests a stale row, not a never-existed row. The original GAP-006 "no row at all" case is still untested.
**Q3:** R4 BLOCKER (migration re-run safety) + note (watcher no-row test gap).

### 21. Wealth & Revenue Strategist (T3 pricing, ₹999/mo fallback) — CONDITIONAL
**Q1 (is the pricing assumption sound for R4?):** ₹999/mo is a *fallback to unblock*, not a validated price. Building R4 synthesis "around" it is acceptable ONLY because the architecture is price-invariant: nothing in the schema, Kelly, calibration, or commercial gate changes if the price is ₹499 or ₹1,999. The commercial gate fires on `converted_at` regardless of amount. So the price assumption does NOT change the architecture — this is the key finding that de-risks proceeding.
**Q2 (revenue risk if price is wrong):** Low architectural risk, real go/no-go risk. If true WTP is materially below ₹999, the commercial case for FMP ($14/mo) + the SEBI/RIA compliance cost may not clear — but that is an R5+ commercial-viability question, not an R4 synthesis input. R4 synthesizes a *buildable design*; it does not commit to a price.
**Q3 (delay 24h for real signal vs proceed):** Proceed. The revenue consequence of a 24h delay for one investor's WhatsApp reply is near-zero (no live product, no churn, no burn against the 21-day window that this delay touches). The consequence of *blocking R4 on it* is a stalled council chain (Shakuni's MA-10 finding). Recommendation: proceed to R4 on the ₹999 fallback flagged explicitly as an assumption; let the real signal arrive asynchronously and feed R5 commercial viability, not R4 synthesis. T3 is NOT an R4 blocker once the architecture is shown price-invariant.

---

## Failures Identified

1. **[Munger/Nair/Shakuni/SRE] Migration 0011 `CREATE UNIQUE INDEX` has no pre-existing-violation cleanup.** On the live (dirty) DB it aborts; the GAP-009 fix never applies. Root cause: the migration assumes a clean table while the live defect it patches may have already written duplicate ACTIVE rows.

2. **[Druckenmiller/Iyer/Reddy] `downside_target` has a column but no producer.** ATR(14)/price is named in a comment, never specified as a module/constant/test. Kelly returns 0 for every non-stop-loss signal on Day 1 → Layer 4 rupee output never renders. MA-3 marked resolved in prose, not actually resolved.

3. **[Soros/Menon/Iyer] Calibration bin mismatch.** Emit-time discount (step 3b) feeds post-discount confidence into calibration bins (5.8) learned from undiscounted history → wrong reliability bin applied to streak predictions. Plus double-discount (emit 0.7 × ledger 0.7 = 0.49) over-penalises streaks past design intent.

4. **[Shakuni] G0 gate is self-defeating.** Criterion 2 (uniqueness) can pass vacuously on a fresh DB where criterion 10 hasn't yet created the index; the gate upgraded to catch GAP-009 cannot catch it. No DB state exists where the gate both applies (0011) and meaningfully verifies (criterion 2).

5. **[Imran/SRE/Nair] Migration 0011 is non-idempotent on re-run.** `ADD CONSTRAINT ... UNIQUE` lacks `IF NOT EXISTS`; no transaction wrapper on six DDL statements. A PARTIAL-failed 0011 cannot be safely re-applied — the idempotency fix is not itself idempotent.

6. **[Shakuni/Nair] `approve_signal_weight()` has no PROPOSED-guard before demote.** Called with a non-PROPOSED id, it demotes the live ACTIVE and promotes nothing — leaves the segment with zero ACTIVE weights.

7. **[Nair/Shakuni] Duplicate 0011 ordinal.** `20260621100011_waitlist.sql` and `20260622100011_schema_fixes.sql` both carry ordinal 0011 — ambiguous by ordinal reference (sort order is safe via full timestamp).

---

## Risk / Dependency / Mitigation Map

| # | Risk | Dependency | Mitigation | Owner | Model |
|---|---|---|---|---|---|
| R-01 | 0011 index aborts on live dirty DB → GAP-009 unfixed | Live signal_weights may hold dup ACTIVE rows | Prepend cleanup: demote all-but-latest ACTIVE to SUPERSEDED before `CREATE UNIQUE INDEX`; wrap migration in BEGIN/COMMIT | CoS | Sonnet |
| R-02 | Kelly never renders rupee (no downside producer) | ATR(14)/price module unspecified | Specify `src/signals/downside.py`: emit signal stop-loss OR `ATR(14)/price`; add constant, trace-matrix row, test | CoS | Sonnet |
| R-03 | Calibration applies wrong bin to streak rows + double-discount | Emit-discount vs calibration-bin provenance | Decide ONE: discount before binning (rebuild bins on discounted history) OR calibrate then discount. Remove ledger-SQL secondary discount to kill the 0.49 compound | Iyer + Reddy / CoS | Opus |
| R-04 | G0 gate verifies nothing on fresh DB | Criterion ordering (10 before 2) + seed a violation | Mandate criterion 10 runs first; add a fixture that seeds a dup-ACTIVE then asserts criterion 2 catches it | CoS | Sonnet |
| R-05 | 0011 not re-runnable after PARTIAL | `ADD CONSTRAINT` not guarded | Use `IF NOT EXISTS` / DO-block guard on the UNIQUE constraint; wrap whole migration in one transaction | CoS | Sonnet |
| R-06 | approve_signal_weight zeroes a segment | No PROPOSED-guard before demote | Add `IF NOT EXISTS(SELECT 1 ... WHERE id=p_id AND status='PROPOSED') THEN RAISE` before demote | CoS | Sonnet |
| R-07 | Duplicate 0011 ordinal confusion | Two files, same ordinal | Rename new file to 0013 (next free ordinal) or document the ordinal-collision explicitly in the migration header | CoS | Haiku |
| R-08 | Missing-run "no row at all" still untested | G0 criterion 3 tests stale, not absent | Add G0 criterion: empty ingest_status → watcher fires red banner | CoS | Sonnet |
| R-09 | circuit_flag DEFAULT FALSE scores history as clean | GAP-010 enforcement pre-G1 | Confirm pre-G1 gate blocks learning loop until detection ships; backfill rule for existing rows | Tarun + CoS | Sonnet |
| R-10 | ₹999/mo price unvalidated | T3 WhatsApp signal | Proceed price-invariant; feed real signal to R5 commercial viability, not R4 | Tarun | Haiku |

---

## Next Steps (mapped to owner and model)

| Priority | Step | Owner | Model | Blocks |
|---|---|---|---|---|
| P0 | Add pre-index cleanup + transaction wrapper to 0011 (R-01, R-05, R-06) | CoS | Sonnet | R4 |
| P0 | Specify downside_target producer module (R-02) | CoS | Sonnet | R4 |
| P0 | Resolve emit-discount vs calibration-bin ordering; remove double-discount (R-03) | Iyer+Reddy / CoS | Opus | R4 |
| P0 | Fix G0 gate ordering + seed-a-violation fixture (R-04) | CoS | Sonnet | R4 |
| P1 | Rename new 0011 → 0013; resolve ordinal collision (R-07) | CoS | Haiku | clean apply |
| P1 | Add no-row missing-run G0 criterion (R-08) | CoS | Sonnet | G0 |
| P1 | Log premortem before v0.5 corrective writes (Constraint Enforcer) | CoS | — | next write |
| P2 | Confirm GAP-010 pre-G1 gate + backfill rule (R-09) | Tarun+CoS | Sonnet | G1 |
| P2 | Proceed R4 on ₹999 fallback flagged as assumption (R-10) | Tarun | Haiku | — |

---

## Synthesis Chair Assessment

**Engaged** — genuine substantive disagreement: Dalio/Lynch/Sundaram/Varghese return PASS while Munger/Druckenmiller/Soros/Nair/Iyer/Menon/Imran/Shakuni/SRE return FAIL.

**The named tension:** Is Block 3.1 "done"? The PASS seats are correct that the *design-level* fixes landed — arbitration is specified, the regime join references a real column, the commercial gate binds to a real column, Kelly's formula is dimensionally correct. The FAIL seats are correct that the fixes are *not buildable as written*: the migration aborts on the live table, the Kelly producer is missing, the calibration seam is internally inconsistent, and the gate that should catch all this is itself defeated.

**This is not a contradiction — it is the same pattern R3 named, recurring one level down.** R3's central finding was "a doc that reads fixed over a database that stays broken." Block 3.1 produced migrations this time (real progress), but the migrations carry the *same class* of defect: they assume a clean state the live system does not have (0011 cleanup), they specify a column without its producer (downside_target), and the verification gate cannot distinguish fixed from broken (G0 criterion 2 vacuous pass). The fix moved from "doc-vs-DB drift" to "migration-vs-live-state drift" — one layer deeper, same root cause: **artifacts assuming a state that is not verified to hold.**

**My thesis (adjudication):**
1. **Block 3.1 is NOT complete.** Four P0 corrections (R-01..R-04) are structural, not execution-detail — each invalidates a different load-bearing claim (schema applies / Kelly renders / calibration coherent / gate verifies).
2. **But the gaps are now narrow and bounded** — they are fixes to *delivered* artifacts, not missing artifacts. This is materially closer than R3.
3. **R4 cannot start on the current files** because R4 synthesis requires a self-consistent, buildable design, and three of the four P0s break self-consistency or buildability.
4. **The price-invariance finding (Wealth seat) removes T3 as an R4 blocker** — the one dependency R3 feared would stall the chain is de-risked by architecture, not by waiting.

**Minority view preserved (PASS seats):** the design's conceptual architecture is sound and the v0.4 amendments are the right *shape*; the failures are in execution fidelity of the migrations and the emit pipeline ordering, not in the design thesis. This is compatible with the adjudication: a short, bounded v0.5 corrective pass closes all four P0s without re-opening the design.

---

## Final Verdict + R4 Conditions

**CONDITIONAL READY.**

R4 Synthesis may NOT start on the current files. It may start immediately after a bounded v0.5 corrective pass closing the four P0 conditions below. No design re-litigation is needed — these are fidelity fixes to delivered artifacts.

**Conditions that MUST be met before R4 begins:**
- **C-1:** Migration 0011 rewritten with (a) pre-index cleanup demoting all-but-latest ACTIVE per segment to SUPERSEDED before `CREATE UNIQUE INDEX`; (b) `IF NOT EXISTS`/guarded UNIQUE constraint; (c) single transaction wrapper; (d) PROPOSED-guard in `approve_signal_weight` before demote. *(R-01, R-05, R-06)*
- **C-2:** `downside_target` producer specified — a named module (e.g. `src/signals/downside.py`) computing signal-emitted stop-loss OR `ATR(14)/price`, with ATR(14) formula, a constant, a trace-matrix row, and a test. Without this Kelly cannot run and Layer 4 stays dark. *(R-02)*
- **C-3:** Emit-discount vs calibration-bin ordering resolved as one documented pipeline (arbitration→normalise→discount→calibrate→Kelly), AND the ledger-SQL secondary discount removed or proven non-compounding. *(R-03)*
- **C-4:** G0 gate fixed — criterion 10 (apply migrations) ordered before criterion 2 (uniqueness), plus a fixture that seeds a duplicate ACTIVE and asserts criterion 2 catches it; add the no-row missing-run criterion. *(R-04, R-08)*

**Conditions before R4 COMPLETES (not blocking start):**
- C-5: Resolve duplicate 0011 ordinal (rename new file → 0013). *(R-07)*
- C-6: Confirm GAP-010 pre-G1 gate + circuit_flag backfill rule. *(R-09)*
- C-7: Premortem logged before the v0.5 corrective writes.
- C-8: R4 proceeds on the ₹999/mo fallback explicitly flagged as an unvalidated assumption; real T3 signal feeds R5 commercial viability, not R4. *(R-10)*

**Why CONDITIONAL READY and not NOT READY:** the four P0s are bounded fidelity fixes to delivered artifacts, not missing design — a single short v0.5 pass closes them. **Why not READY:** three of the four break buildability or self-consistency, which R4 synthesis structurally requires. The design thesis is sound; the migrations and emit pipeline need one more fidelity pass.
