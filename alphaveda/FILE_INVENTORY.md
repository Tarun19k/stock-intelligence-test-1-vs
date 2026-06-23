# AlphaVeda File Inventory
# Maintained by housekeeping after each Phase. Status: SPEC | STUB | IMPL | TESTED | DONE

## Legend
- SPEC: defined in design doc, not yet created
- STUB: file exists, no implementation
- IMPL: implemented, tests not yet run
- TESTED: pytest passes
- DONE: tested + GSI regression GREEN

## Phase 1 — Foundation

| File | Status | Notes |
|---|---|---|
| `constants.py` | TESTED | All test_constants.py assertions pass |
| `requirements.txt` | DONE | No test needed |
| `CONTRIBUTING.md` | DONE | Quality rules documented |
| `.claude/rules/SEBI_COMPLIANCE.md` | DONE | Session rule |
| `.claude/rules/COMMERCIAL_GATE.md` | DONE | Session rule |
| `.claude/rules/DATA_SOURCES.md` | DONE | Session rule |
| `pytest.ini` | DONE | Test runner config |
| `tests/conftest.py` | STUB | supabase_client fixture needs Phase 2 src/config.py; skip_no_src guard needed |
| `tests/test_constants.py` | TESTED | 12/12 PASS |
| `tests/test_council_conditions.py` | STUB | 16 PASS, 17 SKIP, 10 ERROR (conftest guard gap — see council finding) |
| `tests/test_migrations.py` | STUB | G-MIG PASS; requires Phase 2 conftest fix to run |
| `COUNCIL_TEST_MAP.md` | DONE | 21 seats mapped, Phase sign-off protocol |
| `waitlist_signup.py` | IMPL | Needs streamlit smoke test |
| `scripts/verify_migrations.py` | DONE | G-MIG PASS confirmed 11 tables + 4 columns |
| `FILE_INVENTORY.md` | DONE | This file |

## Phase 2 — Data Layer

| File | Status | Notes |
|---|---|---|
| `src/config.py` | SPEC | get_supabase_client() + is_commercial() |
| `src/data/regime.py` | SPEC | get_current_regime(emitted_at) as-of join |
| `src/data/provider.py` | SPEC | DataProvider ABC + CommercialLicenseError |
| `src/accuracy/cycle_phase.py` | SPEC | derive_cycle_phase() PHASE_RULES |
| `tests/test_cycle_phase.py` | STUB | RED — src/ not implemented |
| `tests/test_regime.py` | SPEC | Not yet written |
| `tests/test_is_commercial.py` | SPEC | Not yet written |

## Phase 3 — Signal Layer

| File | Status | Notes |
|---|---|---|
| `src/accuracy/ledger.py` | SPEC | compute_streak_flag() |
| `src/signals/downside.py` | SPEC | compute_downside_target() ATR(14)/price |
| `src/signals/arbitration.py` | SPEC | arbitrate() weighted-vote |
| `src/signals/weights.py` | SPEC | active loader + cold-start fallback |
| `src/signals/engine.py` | SPEC | full emit pipeline steps 1–7 |
| `tests/test_downside.py` | STUB | RED — src/ not implemented |
| `tests/test_arbitration.py` | STUB | RED — src/ not implemented |
| `tests/test_ledger.py` | SPEC | Not yet written |
| `tests/test_weights.py` | SPEC | Not yet written |
| `tests/test_engine.py` | SPEC | Not yet written |

## Phase 4 — Portfolio Layer

| File | Status | Notes |
|---|---|---|
| `src/portfolio/buckets.py` | SPEC | rank_for_bucket() |
| `src/portfolio/optimizer.py` | SPEC | kelly_position_size() + E1–E4 EXIT |
| `tests/test_optimizer.py` | STUB | RED — src/ not implemented |
| `tests/test_buckets.py` | SPEC | Not yet written |

## Phase 5 — Presentation Layer

| File | Status | Notes |
|---|---|---|
| `app.py` | SPEC | SEBI disclaimer injection + navigation |
| `pages/data_viewer.py` | SPEC | 4 tabs + staleness badge |
| `pages/signals.py` | SPEC | Signal display + weight proposal banner |
| `pages/path.py` | SPEC | Kelly output + E1–E4 display |
| `pages/accuracy.py` | SPEC | 24-segment ledger + quarterly review UI |
| `tests/test_app.py` | SPEC | Not yet written |

## Phase 6 — GHA Ingest

| File | Status | Notes |
|---|---|---|
| `scripts/ingest_bhavcopy.py` | SPEC | |
| `scripts/ingest_shareholding.py` | SPEC | |
| `scripts/ingest_financials.py` | SPEC | |
| `scripts/calculate_fundamentals.py` | SPEC | |
| `scripts/update_macro.py` | SPEC | |
| `scripts/resolve_outcomes.py` | SPEC | |
| `scripts/seed_historical.py` | SPEC | |
| `.github/workflows/ingest.yml` | SPEC | Cron 5:45 PM IST weekdays |
| `tests/test_g0_gate.py` | STUB | RED — src/ not implemented |
| `WEIGHT_REVIEW_PROCESS.md` | SPEC | Quarterly review doc |

## Isolation Boundary
**AlphaVeda files:** Everything in `alphaveda/`
**GSI files:** Everything at workspace root (app.py, pages/, etc.)
**Shared (read-only):** `supabase/migrations/`, `.env`
**No cross-imports permitted.**

Last updated: 2026-06-23 — G-MIG PASS; Phase 2 unblocked; conftest guard needed before Phase 2 DB tests
