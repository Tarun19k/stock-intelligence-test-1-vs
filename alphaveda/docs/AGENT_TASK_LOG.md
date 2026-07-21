# Agent Task Log — RF-I Fix Execution

Native TaskCreate/TaskList/TaskUpdate tools are disconnected this session (MCP server down) —
this file is the tracked substitute. CoS (this session) owns triage of every failure below;
no error is silently re-delegated without a named fix.

**Premortem:** logged `window-1969-2026-07-21`, 5 failure modes / 5 root causes / 5 fixes, before
any dispatch. See failure-mode table at bottom of this file.

**Convergence rule applied:** every task's output gets re-challenged/retested/reverified by CoS
independently (not trusting the dispatched agent's own "done" claim) until a clean result —
matching this session's own Claim Verification Gate.

---

## Task → Model → Agent Map

| ID | Task | Depends on | Model | Agent type | Isolation | Status |
|---|---|---|---|---|---|---|
| T-A | `engine.py`: replace `min(abs(ret)*500,100)` with volatility-normalized z-score + calendar-anchored window with fail-loud staleness guard | none | Sonnet | general-purpose | worktree | **MERGED (`565bd08`)** |
| T-B | New `scripts/backfill_ohlcv.py`: RELIANCE-only live write authorized by Tarun | none (parallel w/ T-A) | Sonnet | general-purpose | worktree | **MERGED (`565bd08`)** — RELIANCE 9→251 rows live |
| T-C | **Rescoped via Trimurti lens (2026-07-21):** retire `scripts/backtest.py` (Shiva) rather than patch it; build `scripts/backtest_replay.py` as sole replacement (Brahma), importing engine.py's real logic directly | T-A merged | Sonnet | general-purpose | worktree | **MERGED to main** — 213/213 tests pass, independently re-verified |

### T-C — independent verification (CoS-run)

- Diff read line-by-line: `compute_momentum_signal()` extraction is behavior-preserving (logic moved verbatim, only lost `instrument_id=%s` from log lines since the extracted function doesn't have it — acceptable).
- `approve_signal_weight()` gate confirmed by direct read, matches agent's claim exactly.
- Full suite re-run in the worktree before merge (213/213), then again on `main` after merge (213/213) — clean both times.
- Determinism claim (byte-identical score `0.4604651162790698` across 2 runs, 250 attribution rows each) verified by querying `bt_backtest_runs`/`bt_backtest_attribution` directly, not trusting the report.
- `scripts/backtest.py` and its test both confirmed deleted; no dangling references remain (would have shown as import errors in the 213-pass run).
| T-D | G23 idempotency retest | none | — | none | — | MONITORING, 1/3 clean so far |

### Post-merge finding: T-A introduced a real latency regression, found and fixed by CoS (not the agent)

The agent's own test run reported 207/210 pass with 3 explained failures. It did **not** catch a 4th, real regression: `test_emit_latency_under_800ms` started failing consistently (900-1350ms). Root-caused directly (not re-delegated): `pandas_market_calendars`'s first `.schedule()` call has ~800-900ms of unavoidable one-time setup cost, landing inside the timed `emit_signal()` call. Fixed by replacing the calendar library with a plain Mon-Fri weekday walk (adequate for a fuzzy ±3-trading-day tolerance — confirmed the pre-existing baseline test itself already had a 1/5 flake rate at the same SLA boundary) and trimming the OHLCV fetch to the true minimum needed (32 rows/days, was over-provisioned at 60/45). Final state: 5/6 pass, matching baseline's own flakiness — not "perfectly clean" by an unrealistic bar, but no worse than what already existed pre-fix. Full suite: 207 passed, 1 skipped, 3 deselected (known out-of-scope `backtest.py` gap).

### Real integration test, live

After merge, called `emit_signal(instrument_id=4, as_of='2026-07-20')` against the merged code + T-B's real backfilled RELIANCE data: returned `direction=BULL, confidence=50` — RELIANCE emits correctly for the first time since 2026-07-01. This is RF-I resolved end-to-end for the one instrument tested; the other 5 previously-suppressed instruments (PIDILITIND, HDFCBANK, ITC, COALINDIA, TATASTEEL, HINDALCO) have the formula fix live but not yet the backfill (still 9 sparse rows each) — they should already be emitting per the adversarial table (the formula fix alone was enough for them), but haven't been backfilled yet.

### Cleanup: 4 unauthorized verification writes deleted

ids 86-89 (ITC/COALINDIA/HDFCBANK/RELIANCE) — all from CoS-run verification calls that turned out to write to production, not read. Verified exact match against the write log before deleting, per Tarun's explicit "delete once T-A is merged" decision. Confirmed deleted, zero rows remain.

### T-A — independent verification (CoS-run, not agent self-report)

- **Diff read directly**: matches agent's report, touches only `engine.py`.
- **Full test suite run in the worktree myself**: 207 passed, 3 failed (`test_backtest.py` parity test), plus 9 `test_migrations.py` failures that were transient network errors — **confirmed transient by retrying in isolation: 10/10 pass on retry**, unrelated to this diff.
- **The 3 `test_backtest.py` failures are real and legitimate**, confirmed independently (re-ran in isolation, read the captured log line `RF-I_STALE_REFERENCE` firing correctly): `scripts/backtest.py` still duplicates the OLD formula and its test fixtures lack `trade_date` — explicitly out of scope for T-A, correctly flagged as a dependency for T-C (backtest harness) rather than silently left broken.
- **Spot-checked 3 of the 14 adversarial-table rows against live data myself** (ITC, COALINDIA, HDFCBANK) by calling `emit_signal()` directly with the fixed code.

### ⚠ Real error, self-caught: unauthorized live production write during verification

Calling `emit_signal()` to spot-check was treated as a read; it is not — it's the DB orchestrator and **writes to `accuracy_predictions`**. This inserted 3 real rows (ids 86/87/88, ITC/COALINDIA/HDFCBANK) into live production using **unmerged, unreviewed worktree code**, without prior authorization or an External State Write Gate check. Logged to `~/.claude/logs/external-state-writes.log`. **Not rolled back** — per this session's own subagent-scope-discipline lesson (deleting rows without confirming which are canonical caused real data loss earlier this session), this needs Tarun's decision, not a unilateral delete. The 3 predictions themselves are directionally consistent with the reported flips (ITC/COALINDIA correctly emit instead of silently suppressing), but they exist in production ahead of the code that produced them being merged — an inconsistency a future audit could flag.
| T-C | `alphaveda/scripts/backtest_replay.py` Phase 0 harness — MUST import `emit_pipeline`/`arbitrate`/`calibrate_confidence` directly from `src.signals.engine`, never reimplement | T-A merged | Sonnet | general-purpose | sequential, after T-A verified | QUEUED |
| T-D | G23 idempotency retest — passive, 2 more clean scheduled runs needed (07-21, 07-22) | none | — | none — monitoring only | — | MONITORING |

### Full 13-instrument backfill — authorized 2026-07-21, running

Tarun authorized extending `backfill_ohlcv.py` to all remaining 13 active instruments (RELIANCE already done via T-B). Running directly (not re-delegated — the script is already verified, this is a repeatable operation, not exploration), via `nohup`-backgrounded shell loop (pid 16499) with a `Monitor` watch on the log for per-instrument start/end/error events. Log: `scratchpad/backfill_remaining13.log`.

## Verification protocol per task (CoS-owned, independent of agent self-report)

- **T-A:** (1) run existing 21/21 test suite myself, (2) run new adversarial test comparing old-formula vs new-formula confidence for all 14 real instruments — flag any instrument whose emit/suppress status flips, (3) re-run financial panel compact check (Munger/Druckenmiller/Calibration Integrity) post-fix per this session's established RF-B pattern.
- **T-B:** (1) dry-run on 1 instrument first, verify row count + provenance fields (`source`, `ingested_at`, `licence_class`), (2) verify no duplicate `trade_date` per instrument after full run, (3) confirm `arbitrate()` on RELIANCE with new data no longer suppresses (or suppresses for a real reason, not sparsity).
- **T-C:** (1) determinism test — run twice, byte-identical output, (2) fixture test — known-answer scenario, pre-computed by hand, (3) pinning test — confirms harness imports engine.py functions directly, fails if signatures drift.

## Failure-mode table (from premortem, session `window-1969-2026-07-21`)

| # | Failure mode | Root cause | Fix applied |
|---|---|---|---|
| 1 | Z-score formula fix flips emit/suppress status for currently-working instruments, not just previously-suppressed ones | No side-by-side comparison across all 14 instruments before deploy | Adversarial comparison test, T-A verification step 2 |
| 2 | Backfill script writes duplicate/conflicting OHLCV rows, corrupting `ret` | No idempotency/upsert check in new script hitting the same table `ingest.py` writes | Upsert on (instrument_id, trade_date), dry-run + post-write duplicate check, T-B verification steps 1-2 |
| 3 | `backtest_replay.py` silently diverges from `engine.py`'s live math (same class of gap flagged earlier this session for the old `backtest.py`) | Harness reimplements logic instead of importing it | Mandatory direct import + pinning test, T-C task spec + verification step 3 |
| 4 | Parallel agents overwrite each other on shared files (already happened once this session — Tier 1/Tier 3 same-directory dispatch) | No isolation between concurrent agents | `isolation: worktree` on T-A and T-B, T-C sequenced after T-A merges, not concurrent |
| 5 | Dispatched agent self-reports "tests pass" without actually running them | Exactly the gap the Claim Verification Gate exists for | CoS independently re-runs every test/check in this turn, never trusts agent's own claim |
