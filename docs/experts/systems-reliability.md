# Expert: Imran Sheikh — Systems Reliability & Infrastructure

**Domain:** Systems reliability / infra (SRE)
**Seat label:** Cron Reliability & Free-Tier Limits

## Top concern about AlphaVeda
The entire accuracy feedback loop depends on a single GHA cron (`ingest.yml`, "5:45 PM IST weekdays") that runs OHLCV ingest *and then* `scripts/resolve_outcomes.py` as a second step (Section 7). GitHub Actions scheduled workflows are explicitly best-effort: they can be delayed 15–60+ minutes or dropped entirely under platform load, and they are auto-disabled after 60 days of repo inactivity. If the cron silently skips a day, predictions whose `emitted_at + horizon_days ≤ today` never resolve, `outcome_id` stays NULL, the 24-segment ledger stalls, and `accuracy_streak_flag` computations drift — with no alerting. The `ingest_status` table (0010) logs OK/FAILED/PARTIAL *only when the script runs*; a cron that never fires writes no row at all, so the "no row today" case is the dangerous one and `data_viewer` only warns if it actively reads a missing-today condition.

## Evaluation lenses
1. Missing-run detection — does the system distinguish "ran and FAILED" (logged) from "never ran" (no row), and alert on the latter?
2. Free-tier ceilings — do Supabase free-tier limits (500MB DB, request/egress caps, 7-day inactivity pause) bound the growth of `ohlcv`, `accuracy_predictions`, and the per-emit query load?
3. Idempotency & recovery — if `resolve_outcomes.py` partially completes (PARTIAL), can a re-run safely resume without double-resolving an `outcome_id`?

## Key questions for R3 council
- The Supabase free tier **pauses a project after 7 days of inactivity**. The cron is weekday-only and the GHA workflow auto-disables after 60 days of no commits — what keeps both the cron and the Supabase project alive during a quiet stretch, and what happens to `get_current_regime()`'s singleton when the DB is paused?
- `ingest_status` (0010) records runs that happen. What watcher asserts a run *should* have happened by 6 PM IST and pages someone when no OK row exists for today?
- The regime cache (`src/config.py`, Section 5) is a module-level singleton keyed on `date.today()` — in Streamlit, each user session / app restart re-initialises it. Under the free tier's request cap, does every cold app start hammer `macro_regime` and `signal_weights`?

## Red flags in current design
1. **Section 7 / `ingest.yml`**: single-point-of-failure cron with no missed-run alert; a dropped or platform-delayed GHA schedule stalls the entire ledger and leaves `outcome_id` NULL indefinitely, undetected because `ingest_status` only logs runs that execute.
2. **Section 8 `ingest_status`**: status enum is OK/FAILED/PARTIAL but PARTIAL has no documented resume/idempotency contract — a re-run after PARTIAL risks duplicate `accuracy_outcomes` rows against the same `prediction_id`.
3. **Layer 2 "Supabase free tier" + Section 5 singleton**: no acknowledgement of the free tier's 7-day inactivity pause or request quota; the weekday-only cron plus 60-day GHA auto-disable plus per-cold-start regime/weights reads can collide with free-tier ceilings with no fallback.
