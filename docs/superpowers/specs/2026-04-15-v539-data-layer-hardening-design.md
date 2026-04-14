# Design: v5.39 — Data Layer Hardening
**Date:** 2026-04-15
**Session:** session_028
**Status:** Approved — proceed to implementation plan

---

## Problem Statement

The current data layer (`market_data.py` + DataManager M1) has five concrete pain points
that cause user-visible failures today:

1. **Fundamentals go blank on 429.** `get_ticker_info` has no module-level stale fallback.
   During any Yahoo Finance rate-limit cooldown, all P/E, P/B, ROE, sector data disappears.
   Every other data type already has `_ticker_cache` as a stale fallback — INFO doesn't.

2. **Two critical bugs in DataManager M1.** A lock-ordering inversion in `get_health()`
   will deadlock once M3's worker thread exists. The emergency `_breakers = {}` fallback
   causes a `KeyError` on the first adapter call in M4/M5. Both must be fixed before any
   further DataManager milestones proceed.

3. **Token budget chart in Sprint Monitor is broken.** Plotly's bar trace rejects a list
   for the `opacity` property — per-point opacity must go inside `marker=dict(opacity=[...])`.
   Shows a red error banner in the observability page Sprint Monitor tab.

4. **DataManager has no cache layer or data quality contracts.** Pages calling market_data.py
   get raw yfinance output with no provenance (FRESH/CACHED/STALE), no wire-level shape
   validation, and no bounded eviction policy. The existing `_ticker_cache` dict grows
   unbounded across 559 tickers.

5. **OPEN-027/028/029 are stale in CLAUDE.md.** All three were resolved in v5.37 but the
   open items table was never updated, creating false technical debt.

---

## What Is Out of Scope

- **DataManager M3 (worker thread / priority queue):** Replaced by Vercel Workflow DevKit
  when the migration plan (docs/migration/) executes. Building a Python worker thread now
  is infrastructure that will be thrown away. Deferred indefinitely.

- **L3 SQLite persistent cache:** Streamlit Community Cloud filesystem is ephemeral on
  redeploy — L3 delivers zero value for its primary use case. Replaced by Vercel KV at
  migration. Not built.

- **Row-count sufficiency validation in DataContract:** Already handled by
  `compute_indicators()` (indicators.py:21) and `check_data_quality()` (portfolio.py:55).
  DataContract must not duplicate this — Policy 5 (same metric = same function).

---

## Architecture Decisions

### Decision 1 — DataContract is wire-level only
DataContract validates the *shape* of data received from yfinance, not computational
sufficiency. Specifically:
- **OHLCV:** columns `{Open, High, Low, Close, Volume}` present, DatetimeIndex, non-empty,
  Close is numeric.
- **INFO:** `isinstance(dict)`, non-empty.
- **LIVE:** numeric, non-negative, non-zero.
- **INTRADAY:** same as OHLCV + index within today's date range.
- **BATCH:** every ticker key maps to a value passing the OHLCV contract.

Row-count guards stay in `compute_indicators()` and `check_data_quality()` where they live.

### Decision 2 — L2 is a bounded LRU dict, not SQLite
CacheManager L2 is an in-process LRU dict capped at 200 tickers × all DataTypes.
Explicit TTL tracking per entry via a parallel `_cache_times` dict.
Returns `ResultStatus` (FRESH / CACHED / STALE / UNAVAILABLE) with every response.
This replaces the unbounded `_ticker_cache` pattern — same survival characteristic
(module-level, survives Streamlit reruns), bounded size, typed provenance.

### Decision 3 — M3 worker thread is NOT built
The worker thread is Vercel Workflow DevKit territory. M2 ends with bypass=True still
active. The DataManager M2 value is: (a) the critical bug fixes are in place before M3
is ever attempted, (b) the portable Python core (DataContract, CacheManager interface)
is available for Vercel Python API routes at migration time.

### Decision 4 — `get_ticker_info` stale fallback is a market_data.py hotfix
This is not a DataManager concern. A `_info_cache: dict = {}` module-level dict mirroring
`_ticker_cache` is added directly to `market_data.py`. The fix is three lines; it is
Streamlit-specific scaffolding that will not be carried to Vercel (Upstash Redis takes
over there).

### Decision 5 — Platform portability
The DataContract validator and DataResult/CircuitBreaker types are pure Python with no
Streamlit or platform dependency. They port as-is to Vercel Python API routes. The L2
cache is Streamlit-specific and is explicitly documented as such in the code.

---

## Sprint Items

### T1 — Fix M1 critical bugs (`data_manager.py`)
**Model:** Haiku | **Mode:** sequential | **Risk:** low
- Fix lock-ordering in `get_health()`: snapshot breaker states before acquiring `self._lock`
- Fix empty `_breakers = {}` in emergency fallback: populate with same five breakers as `__init__`
- Minor: `bypass_mode()` → `@property`, add `fetched_wall_time` field to DataResult,
  use `.name` string keys in `HealthSnapshot.sources`
**Files:** `data_manager.py`
**Est tokens:** 8k–10k

### T2 — `get_ticker_info` stale fallback (`market_data.py`)
**Model:** Haiku | **Mode:** sequential | **Risk:** low
- Add `_info_cache: dict = {}` module-level dict
- On successful `get_ticker_info` fetch: write to `_info_cache`
- On failure / empty result during 429 cooldown: return `_info_cache.get(ticker, {})` as stale fallback
- Follow exact same pattern as `_ticker_cache` at market_data.py:160
**Files:** `market_data.py`
**Est tokens:** 6k–8k

### T3 — Fix Plotly token budget chart (`pages/observability.py`)
**Model:** Haiku | **Mode:** sequential | **Risk:** low
- Change `opacity=[list]` → `marker=dict(opacity=[...])` on the `fig.add_bar()` call at line 614
- One-line fix; verify chart renders without error banner
**Files:** `pages/observability.py`
**Est tokens:** 4k–6k

### T4 — Close stale OPEN items in CLAUDE.md (`CLAUDE.md`)
**Model:** Haiku | **Mode:** sequential | **Risk:** low
- Remove OPEN-027, OPEN-028, OPEN-029 from the Open Items table (resolved v5.37)
- Update regression baseline reference from 436 → 446 in Current State section
- Update `meta.last_session` in GSI_session.json from session_026 → session_027
**Files:** `CLAUDE.md`, `GSI_session.json`
**Est tokens:** 5k–7k

### T5 — DataManager M2: CacheManager + DataContract (`data_manager.py`)
**Model:** Sonnet | **Mode:** sequential | **Risk:** medium
- Implement `CacheManager` class: bounded LRU L2 dict (200-ticker cap), TTL tracking per
  DataType, `get()` / `put()` / `invalidate()` interface, thread-safe with its own lock
- Implement `DataContract` validator: wire-level checks per DataType (see Decision 1)
- Wire CacheManager into `DataManager.__init__`; bypass=True stays (no pages route yet)
- Add unit tests: TTL expiry, LRU eviction at cap, DataContract pass/fail per DataType
- Regression: extend R24 to cover CacheManager class name and DataContract callable
**Files:** `data_manager.py`, `regression.py`
**Est tokens:** 35k–45k

### T6 — Regression + CLAUDE.md doc updates post-M2
**Model:** Haiku | **Mode:** sequential | **Risk:** low
- Update CLAUDE.md: baseline count, file structure entry for any new test file, Open Items
  table (OPEN-007 M2 → DONE, M3 → explicitly deferred with migration rationale)
- Update GSI_SPRINT.md Done section
- Run sync_docs.py and confirm exit 0
**Files:** `CLAUDE.md`, `GSI_SPRINT.md`
**Est tokens:** 5k–7k

### T7 — Token burn log (Policy 8 / R35)
**Model:** Haiku | **Mode:** sequential | **Risk:** low
- Fill `token_burn_actuals` in sprint manifest
- Write JSONL entry to `docs/ai-ops/token-burn-log.jsonl`
- Run `python3 docs/ai-ops/analyze_token_burns.py` to confirm parseable
**Files:** `docs/ai-ops/token-burn-log.jsonl`
**Est tokens:** 3k–5k

---

## Token Budget Summary

| Item | Model | Est tokens |
|---|---|---|
| T1 M1 critical fixes | Haiku | 8k–10k |
| T2 ticker_info stale fallback | Haiku | 6k–8k |
| T3 Plotly opacity fix | Haiku | 4k–6k |
| T4 CLAUDE.md doc cleanup | Haiku | 5k–7k |
| T5 CacheManager + DataContract | Sonnet | 35k–45k |
| T6 regression + doc updates | Haiku | 5k–7k |
| T7 token burn log | Haiku | 3k–5k |
| Overhead (session start, 3× regression, sync_docs, sprint close) | — | ~28k |
| **Grand total** | | **~94k–116k** |

Fits within a 9-item sprint. T5 is the only Sonnet item — all others are Haiku-eligible
mechanical or doc tasks.

---

## Execution Order

T1 → T2 → T3 → T4 → T5 → T6 → T7

T1 must precede T5 (fixes baked-in bugs before building on top of them).
T4 can run after T3 but before T5 to keep the doc state clean.
T6/T7 are always sprint-close items.

---

## Migration Portability Note

After this sprint, the following DataManager components port to Vercel unchanged:
- `DataResult`, `DataContract`, `CircuitBreaker`, all enums
- CacheManager interface (implementation replaced by Vercel KV)

The following are Streamlit-specific and will not be carried forward:
- CacheManager L2 LRU dict implementation
- `get_ticker_info` `_info_cache` stale fallback in market_data.py

This is intentional and documented here so migration planning (docs/migration/) can
reference this spec rather than re-deriving the portability boundary.

---

## Success Criteria

- `python3 regression.py` passes (updated baseline)
- `python3 compliance_check.py` passes (10/10)
- `get_ticker_info` returns stale fundamentals during a simulated 429 cooldown (manual test)
- Token budget chart renders without error banner in Sprint Monitor tab
- DataContract unit tests pass for all five DataTypes (OHLCV, INFO, LIVE, INTRADAY, BATCH)
- CacheManager: LRU eviction fires at 200-ticker cap, TTL expiry returns STALE not UNAVAILABLE
- OPEN-027/028/029 removed from CLAUDE.md open items
