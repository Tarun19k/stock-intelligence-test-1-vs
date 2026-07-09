# AlphaVeda — Loop-Engineered Execution Roadmap
# APPROVED 2026-07-01 · Tarun Kochhar
# Do not modify governance rules without Tarun's explicit approval.
# This file is the canonical execution contract. Update it as progress is made.

---

## Plan Status

| Loop | Status | Health gate |
|---|---|---|
| Loop 0 — Foundation | NOT STARTED | macro_regime COUNT=1 + fundamentals COUNT≥14 |
| Loop 1 — Daily Prediction | NOT BUILT | 5 consecutive OK ingests + predictions growing |
| Loop 2 — Weekly Weight Review | DEFERRED | ≥1 segment at 30 observations (est. Day 15) |
| Loop 3 — Weekly Model Improvement | DEFERRED | ≥4 weeks of Loop 1 data (est. Day 28) |
| Session C — Auth | DEFERRED | First subscriber sets waitlist.converted_at |
| Gumroad Stream A | PENALISED + GATED | Tarun's explicit AlphaVeda go-ahead + ≥2026-07-07 |

---

## Anthropic Loop Engineering Laws (active constraints on this plan)

1. **Observable state law** — every action must produce state queryable by a test. "Done" = a row count, a status flag, or a passing test. Not a judgment.
2. **Verifiable exit law** — every loop has a measurable exit condition that `pytest` or a SQL query can assert. No verbal confirmation substitutes.
3. **Fail-loud law** — errors surface in the iteration they occur. `@pytest.mark.skip` on a critical test is a governance violation. Silent GHA failures are a governance violation.

---

## Loop 0 — Foundation (one-time, pre-Loop 1)

**Owner:** Tarun + Claude  
**Deadline:** Before the next GHA ingest run (next trading day after Loop 1 is built)  
**These are data entry tasks, not build tasks. No pipeline needed first.**

| Action | Owner | Measurable gate |
|---|---|---|
| Insert 1 row into `macro_regime` (VIX, regime_tag, cycle_phase, valid_from) | Claude via Supabase MCP | `SELECT COUNT(*) FROM macro_regime` = 1 |
| Run `fundamentals.py` for 14 seeded instruments (BSE XBRL) | Claude | `SELECT COUNT(*) FROM fundamentals` ≥ 14 |

Loop 0 does NOT complete until both SQL gates pass. No proceeding to Loop 1 build without these.

---

## Loop 1 — Daily Prediction Loop (core loop, Mon–Fri forever)

```
┌─────────────────────────────────────────────────────────┐
│  PERCEIVE   NSE Bhavcopy downloaded for trade_date      │
│  ACT        Upsert OHLCV rows (14 instruments)          │
│  EMIT       emit_signal() for each active instrument    │
│             → writes to accuracy_predictions            │
│  RESOLVE    resolve_outcomes() against yesterday's preds│
│             → writes to accuracy_outcomes               │
│  VERIFY     Data completeness check (all tables > 0)    │
│  OBSERVE    ingest_status = OK written                  │
│  ALERT      if predictions_count unchanged → fail GHA   │
└─────────────────────────────────────────────────────────┘
              ↓ repeats next trading day
```

### Build tasks (Session C-P0 — one session)

| Task | File | Gate |
|---|---|---|
| Write `emit_signal(instrument_id, as_of, supabase_client)` | `alphaveda/src/signals/engine.py` | Function importable; no ImportError |
| Wire `emit_signal()` into ingest.py as Step 0 (after OHLCV upsert) | `alphaveda/scripts/ingest.py` | Called once per active instrument per run |
| ATR computation → populate `magnitude_target` + `downside_target` at emit time | `engine.py` | Both columns non-null in accuracy_predictions after emit |
| Add `test_full_operational_loop` (NON-SKIPPABLE) | `alphaveda/tests/test_g0_gate.py` | `SELECT COUNT(*) FROM accuracy_predictions` ≥ 1 after ingest run |
| Remove `@pytest.mark.skip` from `TestImranConditions.test_emit_latency_under_800ms` | `alphaveda/tests/test_council_conditions.py:328` | Test runs + passes (or ImportError surfaces immediately) |
| Add data completeness step to ingest.yml | `.github/workflows/ingest.yml` | Step fails loudly if any required table = 0 rows post-ingest |
| Zero-prediction alert | `ingest.yml` | GHA named alert fires if accuracy_predictions unchanged after 2 consecutive OK ingests |

### Loop 1 health exit condition

5 consecutive trading days where:
- `ingest_status = OK`
- `accuracy_predictions` COUNT increases each day
- No named alerts fired

Only after Loop 1 health confirmed can Loop 2 or Loop 3 work begin (G-L4).

---

## Loop 2 — Weekly Weight Review Loop (human-gated)

**Trigger:** First segment reaches `OBSERVATION_THRESHOLD = 30` (estimated ~Day 15 for stalwart/fast_grower)

```
┌─────────────────────────────────────────────────────────┐
│  PERCEIVE   Query accuracy_outcomes by (lynch_class,    │
│             regime, signal_name)                        │
│  THINK      Compute actual hit_rate per segment         │
│             Compare vs cold_start_weights               │
│  PROPOSE    Write PROPOSED rows to signal_weights       │
│             (only if |new_weight - active| ≥ 0.03)      │
│  SURFACE    SESSION_RESUME shows PROPOSED count +       │
│             oldest proposal date at every session start │
│  CHECKPOINT Tarun reviews → approve_signal_weight()     │
│  ACTIVATE   PROPOSED → ACTIVE                           │
│  VERIFY     load_weights() returns new ACTIVE weights   │
└─────────────────────────────────────────────────────────┘
              ↓ repeats when next segment reaches threshold
```

**Human checkpoint rule:** `approve_signal_weight()` with `approved_by='tarun'` is the sole path to ACTIVE status. Automation cannot approve weights. No exceptions.

---

## Loop 3 — Weekly Model Improvement Loop

**Build trigger:** ≥4 weeks of Loop 1 data (≥80 trading-day predictions). Do not build before.

```
┌─────────────────────────────────────────────────────────┐
│  PERCEIVE   Group accuracy_outcomes by ISO week         │
│  MEASURE    hit_rate, avg_return per week per segment   │
│  COMPARE    Actual vs cold_start priors                 │
│  FLAG       Weeks where hit_rate < 50% or avg_return<0  │
│  DIAGNOSE   Which signal_name drove the miss?           │
│  SURFACE    Weekly deviation table on Accuracy page     │
│  ACT        Systematic miss → feed into Loop 2          │
└─────────────────────────────────────────────────────────┘
              ↓ repeats weekly
```

**Convergence signal:** `hit_rate(week N)` trending upward over 4-week moving window.  
**Convergence achieved:** hit_rate ≥ 55% for 8 consecutive weeks.

---

## Governance Rules (G-L1 through G-L8)

These rules are active from the moment Loop 1 is built. Non-negotiable.

| Rule | Trigger | Consequence |
|---|---|---|
| **G-L1: Loop 1 runs every trading day** | `ingest_status ≠ OK` on a trading day | GHA fails loudly; SESSION_RESUME surfaces failure date |
| **G-L2: Predictions grow each trading day** | `accuracy_predictions` count unchanged after 2 consecutive OK ingests | Named GHA alert; counted as system miss (+24h penalty) |
| **G-L3: PROPOSED weights expire at 14 days** | Any PROPOSED row older than 14 days without review | Surfaced in SESSION_RESUME; +24h penalty if not reviewed |
| **G-L4: No Loop 2/3 work before Loop 1 health confirmed** | Loop 1 not at 5-day health gate | Any upstream work classified TECHNICAL-ONLY and deprioritised |
| **G-L5: test_full_operational_loop is non-skippable** | `@pytest.mark.skip` found on this test | System miss; fails gate count regardless of total PASS |
| **G-L6: Penalty rule persists** | Any system miss on AlphaVeda | +24h Gumroad delay; tally surfaced at session start |
| **G-L7: GraphRAG-first on all internal lookups** | MCP call without prior graph query | Logged in `graphify-gaps.md`; if caused a miss → +24h penalty |
| **G-L8: Gumroad lists when Tarun approves AlphaVeda** | Tarun's explicit go-ahead (not a calendar date) | Penalty floor: 2026-07-07; listing trigger: Tarun's AlphaVeda approval |

---

## Session-by-Session Roadmap

| Session | Goal | Entry condition | Exit gate |
|---|---|---|---|
| **Session C-P0** (next) | Close Loop 1 | Loop 0 seeds in place | `test_full_operational_loop` PASS; predictions accumulate same day |
| **Day 1–5 watch** | Confirm Loop 1 health | Loop 1 built | 5 consecutive OK ingests + prediction count growing |
| **Session C-P1** | GHA completeness gate + Rule D/E in COUNCIL_RULES | Loop 1 at 5-day health | GHA step green; COUNCIL_RULES.md updated |
| **~Day 15** | First Loop 2 trigger | ≥1 segment at 30 observations | PROPOSED rows written; Tarun reviews + approves |
| **~Day 28** | Build Loop 3 surface | ≥4 weeks of Loop 1 data | Weekly deviation table live on Accuracy page |
| **Tarun's go-ahead** | Gumroad Stream A listed | Tarun's explicit AlphaVeda approval (floor: 2026-07-07) | Listing live; price, description, ZIP uploaded |
| **First subscriber** | Session C auth gate | `waitlist.converted_at` set | Auth wired; `is_commercial()` returns True; yfinance blocked |

---

## P1 Backlog (after Loop 1 health confirmed)

- Fixes B/C/D: Notion task sync → `PHASE7_TASKS.md`; `VERCEL_STATE.md`; `PRODUCT_HUB.md` (GraphRAG coverage)
- Rule D (skip audit gate) + Rule E (cross-domain connectivity test) → `COUNCIL_RULES.md`

---

## Penalty Tally — Live

| Date | Miss | +Hours | Cumulative |
|---|---|---|---|
| 2026-07-01 | 6 misses (council session) | +144h | **+144h (+6 days)** |

Each new miss adds +24h to penalty. Surface at session start before accepting any AlphaVeda work.

---

## Progress Log

*Update this section as loops complete, plans improve, or governance rules are refined.*

| Date | What changed |
|---|---|
| 2026-07-01 | Plan created + approved. G-L8 amended: Gumroad gated on Tarun's AlphaVeda approval, not fixed calendar date. |
| 2026-07-09 | Design catalog v2 discovered (gitignored 07-01, never wired to build). Full capability map + loop-engineered gap audit converged: 17 gaps (G1–G17), 6 red flags (RF-A–F). Financial panel (7-member, adapted for system review) returned 3 BLOCKERs: RF-B (emit_signal direction/confidence incoherence below p=0.5), RF-A (marketing overstates multi-doctrine capability vs live single-signal), Munger sequencing (fix RF-B before waitlist G8 ships). Sign-off criterion defined: zero BLOCKER on panel re-run. Gap register not yet a standalone file — see SESSION_RESUME.md 2026-07-09 checkpoint for full detail. |
# hook fix verification 2026-07-09T17:57:09Z
