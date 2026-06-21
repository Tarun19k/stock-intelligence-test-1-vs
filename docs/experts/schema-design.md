# Expert: Deepak Nair — Database & Schema Design

**Domain:** Database / Postgres schema design
**Seat label:** Migration Ordering & FK Integrity

## Top concern about AlphaVeda
Migration `0004_macro_regime.sql` declares `regime VARCHAR(20) NOT NULL UNIQUE` and a comment states the UNIQUE is required because `accuracy_predictions.regime_tag` (0007) FK-references *the `regime` column*. This is structurally broken. `regime` is a per-row category that legitimately repeats across many `regime_date` rows — a `UNIQUE` constraint on `regime` means the table can hold at most **four rows ever** (one each for RISK_ON/RISK_OFF/STAGFLATION/DEFLATION). But `macro_regime` is a time series with `regime_date NOT NULL UNIQUE` and a daily/monthly cadence (`update_macro.py`). The moment a second day shares a regime value, the insert violates `UNIQUE(regime)`. The FK design forced a uniqueness constraint onto a non-unique column to satisfy Postgres' rule that a FK must point at a UNIQUE/PK column — the correct fix is a small `regimes` lookup/enum table, not making the time series single-row-per-regime.

## Evaluation lenses
1. FK target legality vs domain correctness — does each FK point at a genuinely unique column without distorting the referenced table's cardinality?
2. Migration ordering & circular dependencies — is the 0007↔0008 circular FK resolved cleanly, and is every migration independently runnable in order?
3. Constraint completeness — do CHECK/UNIQUE/NOT NULL constraints express the real invariants (e.g. `signal_weights` "one ACTIVE per segment") without over- or under-constraining?

## Key questions for R3 council
- `macro_regime.regime` is `UNIQUE` to serve the `accuracy_predictions.regime_tag` FK (0007 line). This caps the table at 4 total rows and breaks the daily/monthly time series in `0004`. Should `regime_tag` instead FK a `regimes` lookup table, freeing `macro_regime` to be a proper time series?
- `signal_weights` has `UNIQUE (lynch_class, regime, signal_name, status)` (0009). This permits one ACTIVE *and* one PROPOSED *and* one REJECTED row simultaneously for the same segment+signal — but allows multiple REJECTED rows to collapse into one. Is "exactly one ACTIVE per (class, regime, signal)" actually enforced, or can two ACTIVE rows coexist after a status transition?
- The circular FK is resolved by `0008` ALTER-ing `accuracy_predictions` to add `outcome_id`. If migrations are ever re-run or applied out of order, does 0007 succeed standalone (it must, since 0008 doesn't exist yet at 0007 runtime) — is this ordering encoded anywhere besides filename sequence?

## Red flags in current design
1. **`0004_macro_regime.sql`**: `regime VARCHAR(20) NOT NULL UNIQUE` makes a time-series table single-row-per-regime (max 4 rows ever); the second same-regime day fails to insert. The UNIQUE exists only to make the 0007 FK legal — a lookup-table redesign is required.
2. **`0009_signal_weights.sql`**: `UNIQUE (lynch_class, regime, signal_name, status)` does not guarantee a single ACTIVE weight per segment+signal; the review process (Section 5) assumes "signal engine reads only ACTIVE rows," but the schema permits drift if two rows reach ACTIVE through different transitions.
3. **`0007`/`0008` circular FK**: correctly deferred via ALTER TABLE, but the safe-ordering invariant lives only in filename numbering — no migration runner contract, transaction wrapping, or test (beyond per-migration smoke tests in Section 8) guarantees 0007 is applied before 0008 and never re-applied.
