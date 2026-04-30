# v5.39 — Data Layer Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix two critical DataManager bugs, add a `get_ticker_info` stale fallback, repair the Plotly opacity error in Sprint Monitor, close three stale OPEN items in docs, and ship DataManager M2 (bounded LRU cache + wire-level DataContract validator).

**Architecture:** All changes are in `data_manager.py`, `market_data.py`, and `pages/observability.py`. DataManager M2 adds `CacheManager` and `DataContract` classes inside `data_manager.py` (no new files). Unit tests go in `tests/test_data_manager_m2.py` (new directory). Bypass mode stays `True` throughout — no pages route through DataManager yet.

**Tech Stack:** Python 3.14, Streamlit 1.55, yfinance 1.2.0, Plotly 5.24.1, pandas ≥ 1.4.0, `collections.OrderedDict` for LRU, `pytest` for unit tests.

---

## File Map

| File | Action | What changes |
|---|---|---|
| `data_manager.py` | Modify | T1: fix `get_health()` lock order, fix `_breakers={}` fallback, `bypass_mode` → `@property`, add `fetched_wall_time` to `DataResult`, str keys in `HealthSnapshot.sources`. T5: add `CacheManager`, `DataContract`, wire into `DataManager.__init__`, update `invalidate()` / `invalidate_all()` |
| `market_data.py` | Modify | T2: add `_info_cache` module-level dict, write on success, serve stale on 429 |
| `pages/observability.py` | Modify | T3: fix `opacity` list → `marker=dict(opacity=[...])` |
| `CLAUDE.md` | Modify | T4: remove OPEN-027/028/029, update regression baseline 436→446, update meta.last_session |
| `GSI_session.json` | Modify | T4: update `meta.last_session` session_026→session_027 |
| `regression.py` | Modify | T5: extend R24 with CacheManager + DataContract checks |
| `tests/test_data_manager_m2.py` | Create | T5: unit tests for CacheManager and DataContract |
| `GSI_SPRINT.md` | Modify | T6: add Done section for v5.39 |
| `docs/ai-ops/token-burn-log.jsonl` | Modify | T7: append actuals entry |

---

## Task 1: Fix M1 Critical Bugs + Minor Cleanups

**Files:**
- Modify: `data_manager.py`

### What to fix

Four changes in one file, all mechanical. No logic changes — only safety and API improvements.

**Fix A — lock ordering in `get_health()` (line 350)**
Before acquiring `self._lock`, snapshot all breaker states. This removes nested lock acquisition.

**Fix B — empty `_breakers` in emergency fallback (line 456)**
The `object.__new__()` path sets `_breakers = {}`. `get_breaker()` calls `self._breakers[source]` which KeyErrors. Populate with the same five breakers as `__init__`.

**Fix C — `bypass_mode()` → `@property` (line 322)**
Rename and decorate. All call sites in the codebase use `dm.bypass_mode()` with parens — update them too.

**Fix D — add `fetched_wall_time` to `DataResult` (line 91)**
Monotonic time cannot be shown to users as "data as of HH:MM". Add a wall-clock field with a default so existing `DataResult(...)` calls don't break.

**Fix E — `HealthSnapshot.sources` str keys (line 134)**
`{SourceTag.YAHOO: CircuitState.CLOSED}` is not JSON-serialisable. Use `.name` string keys.

- [ ] **Step 1: Apply Fix A — snapshot breaker states before lock**

In `data_manager.py`, replace the `get_health` method (lines 345–359):

```python
def get_health(self) -> HealthSnapshot:
    """
    Always safe to call — never raises.
    Returns a snapshot of current health state for the sidebar panel (M6).
    Lock ordering: read breaker states (each holds its own lock) BEFORE
    acquiring self._lock to prevent AB-BA deadlock with M3 worker thread.
    """
    # Snapshot breaker states outside self._lock — each b.state acquires b._lock.
    # Acquiring self._lock while holding a CircuitBreaker._lock would invert
    # the lock hierarchy and deadlock against a worker thread doing the reverse.
    sources = {tag.name: b.state.name for tag, b in self._breakers.items()}
    with self._lock:
        return HealthSnapshot(
            sources=sources,
            cache_hits=self._cache_hits,
            cache_misses=self._cache_misses,
            queue_depth=0,           # M3: replaced with real queue depth
            queue_by_priority={p.name: 0 for p in Priority},
            last_fetch_at=self._last_fetch_at,
            bypass_active=self._bypass,
        )
```

- [ ] **Step 2: Apply Fix B — populate `_breakers` in emergency fallback**

In `get_datamanager()`, replace lines 449–456 (the `object.__new__` block):

```python
    try:
        return DataManager()
    except Exception as exc:  # noqa: BLE001
        log.error("DataManager failed to initialise (%s) — running in bypass mode", exc)
        # Construct a minimal safe instance without calling __init__
        dm = object.__new__(DataManager)
        dm._bypass        = True
        dm._healthy       = False
        dm._cache_hits    = 0
        dm._cache_misses  = 0
        dm._last_fetch_at = None
        dm._lock          = threading.Lock()
        dm._cache_manager = None  # M2: populated below; None signals no cache available
        dm._breakers      = {
            SourceTag.YAHOO: CircuitBreaker(
                SourceTag.YAHOO, failure_threshold=3,
                recovery_window_s=60.0, probe_timeout_s=10.0,
            ),
            SourceTag.NSEPYTHON: CircuitBreaker(
                SourceTag.NSEPYTHON, failure_threshold=3,
                recovery_window_s=120.0, probe_timeout_s=15.0,
            ),
            SourceTag.FRED: CircuitBreaker(
                SourceTag.FRED, failure_threshold=3,
                recovery_window_s=300.0, probe_timeout_s=10.0,
            ),
            SourceTag.STALE_CACHE: CircuitBreaker(
                SourceTag.STALE_CACHE, failure_threshold=999,
                recovery_window_s=1.0, probe_timeout_s=0.1,
            ),
        }
        return dm
```

- [ ] **Step 3: Apply Fix C — `bypass_mode` → `@property`**

Replace the `bypass_mode` method (line 322):

```python
@property
def bypass_mode(self) -> bool:
    """
    True while DataManager is in bypass (M1–M2).
    When True, all pages use market_data.py directly.
    Set False in M3 once the worker thread and queue are live.
    """
    return self._bypass
```

Search for all call sites (`dm.bypass_mode()` with parens) in the project and remove the `()`:

```bash
grep -rn "bypass_mode()" . --include="*.py"
```

Update each found call site from `dm.bypass_mode()` to `dm.bypass_mode`.

- [ ] **Step 4: Apply Fix D — add `fetched_wall_time` to `DataResult`**

In `data_manager.py`, add the import at the top of the file (if not already there):
```python
import time
```
(Already present — confirm with `grep -n "^import time" data_manager.py`.)

Replace the `DataResult` dataclass definition (line 81–108):

```python
@dataclass(frozen=True)
class DataResult:
    """
    Every DataManager response is a DataResult.
    data is None if and only if status == UNAVAILABLE.
    Always check .ok before accessing .data.

    fetched_at:        time.monotonic() — for internal TTL age calculations.
    fetched_wall_time: time.time()      — for user-facing "data as of HH:MM" display (Policy 7).
    """
    status:           ResultStatus
    data:             Any           # pd.DataFrame | dict | float | None
    source:           SourceTag | None
    fetched_at:       float         # time.monotonic() at point of fetch
    ticker:           str
    data_type:        DataType
    error_msg:        str | None = None
    fetched_wall_time: float = field(default_factory=time.time)

    @property
    def ok(self) -> bool:
        """True when data is usable (FRESH, CACHED, or STALE)."""
        return self.status in (
            ResultStatus.FRESH,
            ResultStatus.CACHED,
            ResultStatus.STALE,
        )

    @property
    def is_stale(self) -> bool:
        """True when data is past TTL but served as fallback."""
        return self.status == ResultStatus.STALE
```

- [ ] **Step 5: Apply Fix E — `HealthSnapshot.sources` and `queue_by_priority` doc update**

Update the `HealthSnapshot` docstring at line 129 to reflect string keys:

```python
@dataclass
class HealthSnapshot:
    """
    Point-in-time health state.  Consumed by sidebar observability panel (M6).
    Returned by DataManager.get_health() — always safe to call.

    sources:           SourceTag.name str → CircuitState.name str  (JSON-serialisable)
    queue_by_priority: Priority.name str → int count               (JSON-serialisable)
    """
    sources:           dict   # str → str  (SourceTag.name → CircuitState.name)
    cache_hits:        int
    cache_misses:      int
    queue_depth:       int
    queue_by_priority: dict   # str → int  (Priority.name → count)
    last_fetch_at:     float | None
    bypass_active:     bool
```

- [ ] **Step 6: Run regression to confirm no regressions**

```bash
python3 regression.py 2>&1 | tail -5
```

Expected: `ALL 446 CHECKS PASS` (same as before — no new checks added in T1).

- [ ] **Step 7: Commit**

```bash
git add data_manager.py
git commit -m "fix(data_manager): M1 critical bugs — lock ordering, empty breakers fallback, bypass_mode property, fetched_wall_time, str keys in HealthSnapshot"
```

---

## Task 2: `get_ticker_info` Stale Fallback

**Files:**
- Modify: `market_data.py`

When Yahoo Finance rate-limits the app, `get_ticker_info` returns `{}` and all fundamentals (P/E, P/B, ROE, sector, market cap) go blank. Every other data type has `_ticker_cache` as a stale fallback. This adds the same pattern for INFO.

- [ ] **Step 1: Add `_info_cache` module-level dict**

In `market_data.py`, directly after the `_ticker_cache_period` / `_TICKER_CACHE_TTL` block (around line 163), add:

```python
# ── Module-level info cache (survives across Streamlit rerenders) ────────────
# Mirrors _ticker_cache but stores fundamentals dicts from get_ticker_info().
# Serves stale fundamentals during 429 cooldowns so P/E, P/B, ROE, sector
# do not go blank. Streamlit-specific — replaced by Upstash Redis at migration.
_info_cache: dict = {}   # ticker → dict from yf.Ticker.info
```

- [ ] **Step 2: Write to `_info_cache` on successful fetch**

In `get_ticker_info()` (line 498), replace the function body:

```python
@st.cache_data(ttl=600, show_spinner=False)
def get_ticker_info(ticker: str, cache_buster: int = 0) -> dict:
    """
    Fetch metadata/fundamentals for a ticker.
    cache_buster: same semantics as get_price_data.
    Returns {} on any failure — callers must handle missing keys gracefully.
    On 429 cooldown: returns last known good data from _info_cache (stale fallback).
    Note: yfinance raises TypeError internally for some futures tickers (CL=F,
    GC=F etc.) — this is a known upstream issue, handled silently here.
    """
    if _is_rate_limited():
        # Return stale fundamentals rather than blank — P/E, P/B, sector survive cooldown
        return _info_cache.get(ticker, {})
    _global_throttle()
    try:
        result = yf.Ticker(ticker).info
        if isinstance(result, dict) and result:
            _info_cache[ticker] = result   # update stale fallback on success
            return result
        return {}
    except TypeError:
        # Known yfinance issue with futures/commodity tickers — not our bug.
        return {}
    except Exception as e:
        log_error(f"get_ticker_info:{ticker}", e)
        return _info_cache.get(ticker, {})   # serve stale on any unexpected error
```

- [ ] **Step 3: Run regression**

```bash
python3 regression.py 2>&1 | tail -5
```

Expected: `ALL 446 CHECKS PASS`.

- [ ] **Step 4: Commit**

```bash
git add market_data.py
git commit -m "fix(market_data): get_ticker_info stale fallback via _info_cache — fundamentals survive 429 cooldown"
```

---

## Task 3: Fix Plotly Token Budget Chart

**Files:**
- Modify: `pages/observability.py`

Plotly's `go.Bar()` trace rejects `opacity` as a list. Per-point opacity must go inside `marker=dict(opacity=[...])`.

- [ ] **Step 1: Fix the opacity argument (line 609–615)**

In `pages/observability.py`, find the `fig.add_bar(` block that adds the "actual k" bar (the one with the `opacity=` argument). Replace it:

```python
            if any(a is not None for a in actuals):
                fig.add_bar(
                    x=ids,
                    y=[a if a is not None else 0 for a in actuals],
                    name="actual k",
                    marker=dict(
                        color="#4C9BE8",
                        opacity=[1.0 if a is not None else 0.3 for a in actuals],
                    ),
                )
```

(The `marker_color="#4C9BE8"` and `opacity=[list]` at the trace level are replaced by a single `marker=dict(...)` block. This is how Plotly handles per-point styling on bar traces.)

- [ ] **Step 2: Confirm the fix in the browser**

Navigate to `http://localhost:8501/observability`, unlock with the DEV_TOKEN, click Sprint Monitor tab. The red error banner "Token budget chart unavailable: Invalid value…" must be gone. A grouped bar chart should render (or a "No token_budget.items in manifest" caption if the sprint manifest has no items — either is correct, no error banner).

- [ ] **Step 3: Run regression**

```bash
python3 regression.py 2>&1 | tail -5
```

Expected: `ALL 446 CHECKS PASS`.

- [ ] **Step 4: Commit**

```bash
git add pages/observability.py
git commit -m "fix(observability): Plotly bar opacity list → marker=dict(opacity=[...]) — fixes Sprint Monitor chart error"
```

---

## Task 4: Close Stale OPEN Items in Docs

**Files:**
- Modify: `CLAUDE.md`
- Modify: `GSI_session.json`

OPEN-027, OPEN-028, OPEN-029 were resolved in v5.37 (commit `959d5f7`) but were never removed from the open items table. The regression baseline in CLAUDE.md still shows 436 despite the actual count being 446.

- [ ] **Step 1: Remove OPEN-027, OPEN-028, OPEN-029 from CLAUDE.md**

In the `### QA Audit Backlog — v5.33+ (P2 / Roadmap)` table in `CLAUDE.md`, delete the three rows:

```
| OPEN-027 | **P0** | **SEBI disclaimer absent in `_render_global_signals()`...** |
| OPEN-028 | **P0** | **FS-01 + FS-06: `_render_watchlist_badges()`...** |
| OPEN-029 | **P0** | **SEBI disclaimer absent from `_render_header_static()`...** |
```

- [ ] **Step 2: Update regression baseline in CLAUDE.md**

In the `## Current State (v5.38 ...)` section, change:

```
**Regression baseline: 436/436 PASS** *(stable; R27/R30/R31/R32 add additional checks during active sprints)*
```

to:

```
**Regression baseline: 446/446 PASS** *(stable base; sprint-specific checks (R27/R30/R31/R32) activate when manifest status == IN_PROGRESS)*
```

- [ ] **Step 3: Update `meta.last_session` in GSI_session.json**

Open `GSI_session.json`, find the `"meta"` block, change:

```json
"last_session": "session_026"
```

to:

```json
"last_session": "session_028"
```

(session_027 completed and session_028 is the current session — use session_028 as the authoritative value.)

- [ ] **Step 4: Run regression**

```bash
python3 regression.py 2>&1 | tail -5
```

Expected: `ALL 446 CHECKS PASS`.

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md GSI_session.json
git commit -m "docs: close OPEN-027/028/029 (resolved v5.37), update regression baseline 436→446, fix meta.last_session"
```

---

## Task 5: DataManager M2 — CacheManager + DataContract

**Files:**
- Modify: `data_manager.py`
- Create: `tests/test_data_manager_m2.py`
- Modify: `regression.py`

This is the core infrastructure task. Two new classes inside `data_manager.py`:
- `CacheManager`: bounded OrderedDict LRU (200 entries), TTL-aware, thread-safe.
- `DataContract`: static wire-level validator per `DataType`. Returns `None` if valid, reason `str` if not.

Bypass mode stays `True`. `DataManager.invalidate()` and `invalidate_all()` delegate to `CacheManager`.

### Step group A — Write failing tests first (TDD)

- [ ] **Step 1: Create `tests/` directory and test file**

```bash
mkdir -p tests
touch tests/__init__.py
```

Create `tests/test_data_manager_m2.py`:

```python
"""Unit tests for DataManager M2 — CacheManager and DataContract.

Run: pytest tests/test_data_manager_m2.py -v
These tests are direct unit tests of the cache and validation layer.
They do NOT test Streamlit integration — that is covered by regression.py.
"""
import time
import pandas as pd
import pytest
from collections import OrderedDict

from data_manager import (
    CacheManager,
    DataContract,
    DataResult,
    DataType,
    ResultStatus,
    SourceTag,
    unavailable,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_ohlcv(n_rows: int = 30) -> pd.DataFrame:
    dates = pd.date_range("2026-01-01", periods=n_rows, freq="D")
    return pd.DataFrame(
        {"Open": 100.0, "High": 105.0, "Low": 95.0, "Close": 102.0, "Volume": 1_000_000},
        index=dates,
    )


def _make_result(
    ticker: str = "AAPL",
    data_type: DataType = DataType.OHLCV,
    status: ResultStatus = ResultStatus.FRESH,
    age_s: float = 0.0,
) -> DataResult:
    return DataResult(
        status=status,
        data=_make_ohlcv(),
        source=SourceTag.YAHOO,
        fetched_at=time.monotonic() - age_s,
        fetched_wall_time=time.time() - age_s,
        ticker=ticker,
        data_type=data_type,
    )


# ── CacheManager tests ────────────────────────────────────────────────────────

class TestCacheManagerMiss:
    def test_get_returns_none_on_empty_cache(self):
        cm = CacheManager()
        assert cm.get("AAPL", DataType.OHLCV) is None

    def test_get_returns_none_for_different_ticker(self):
        cm = CacheManager()
        cm.put(_make_result("AAPL"))
        assert cm.get("MSFT", DataType.OHLCV) is None

    def test_get_returns_none_for_different_data_type(self):
        cm = CacheManager()
        cm.put(_make_result("AAPL", DataType.OHLCV))
        assert cm.get("AAPL", DataType.INFO) is None


class TestCacheManagerHit:
    def test_put_and_get_returns_fresh_result(self):
        cm = CacheManager()
        result = _make_result("AAPL", DataType.OHLCV)
        cm.put(result)
        got = cm.get("AAPL", DataType.OHLCV)
        assert got is not None
        assert got.ticker == "AAPL"
        assert got.status == ResultStatus.FRESH

    def test_size_increments_on_put(self):
        cm = CacheManager()
        assert cm.size == 0
        cm.put(_make_result("AAPL"))
        assert cm.size == 1
        cm.put(_make_result("MSFT"))
        assert cm.size == 2

    def test_unavailable_not_stored(self):
        cm = CacheManager()
        cm.put(unavailable("AAPL", DataType.OHLCV, "test"))
        assert cm.size == 0
        assert cm.get("AAPL", DataType.OHLCV) is None

    def test_duplicate_put_does_not_grow_cache(self):
        cm = CacheManager()
        cm.put(_make_result("AAPL"))
        cm.put(_make_result("AAPL"))
        assert cm.size == 1


class TestCacheManagerTTL:
    def test_fresh_within_ttl(self):
        cm = CacheManager()
        cm.put(_make_result("AAPL", DataType.OHLCV, age_s=10))  # 10s < 300s TTL
        got = cm.get("AAPL", DataType.OHLCV)
        assert got is not None
        assert got.status == ResultStatus.FRESH

    def test_stale_past_ohlcv_ttl(self):
        cm = CacheManager()
        cm.put(_make_result("AAPL", DataType.OHLCV, age_s=400))  # 400s > 300s TTL
        got = cm.get("AAPL", DataType.OHLCV)
        assert got is not None
        assert got.status == ResultStatus.STALE

    def test_stale_past_live_ttl(self):
        cm = CacheManager()
        cm.put(_make_result("AAPL", DataType.LIVE, age_s=10))  # 10s > 5s LIVE TTL
        got = cm.get("AAPL", DataType.LIVE)
        assert got is not None
        assert got.status == ResultStatus.STALE

    def test_stale_entry_data_is_preserved(self):
        cm = CacheManager()
        cm.put(_make_result("AAPL", DataType.OHLCV, age_s=400))
        got = cm.get("AAPL", DataType.OHLCV)
        assert got.data is not None  # data preserved in stale result


class TestCacheManagerLRU:
    def test_lru_evicts_oldest_at_cap(self):
        cm = CacheManager()
        # Fill exactly to MAX_ENTRIES using distinct tickers
        for i in range(cm.MAX_ENTRIES):
            cm.put(_make_result(f"T{i:04d}", DataType.OHLCV))
        assert cm.size == cm.MAX_ENTRIES
        # Add one more — T0000 (inserted first, LRU) should be evicted
        cm.put(_make_result("ZNEW", DataType.OHLCV))
        assert cm.size == cm.MAX_ENTRIES
        assert cm.get("T0000", DataType.OHLCV) is None
        assert cm.get("ZNEW", DataType.OHLCV) is not None

    def test_recently_accessed_not_evicted(self):
        cm = CacheManager()
        for i in range(cm.MAX_ENTRIES):
            cm.put(_make_result(f"T{i:04d}", DataType.OHLCV))
        # Access T0000 to move it to MRU position
        cm.get("T0000", DataType.OHLCV)
        # Add one more — T0001 (now LRU) should be evicted instead
        cm.put(_make_result("ZNEW", DataType.OHLCV))
        assert cm.get("T0000", DataType.OHLCV) is not None  # survived
        assert cm.get("T0001", DataType.OHLCV) is None      # evicted


class TestCacheManagerInvalidate:
    def test_invalidate_removes_all_types_for_ticker(self):
        cm = CacheManager()
        cm.put(_make_result("AAPL", DataType.OHLCV))
        cm.put(_make_result("AAPL", DataType.INFO))
        cm.put(_make_result("MSFT", DataType.OHLCV))
        cm.invalidate("AAPL")
        assert cm.get("AAPL", DataType.OHLCV) is None
        assert cm.get("AAPL", DataType.INFO) is None
        assert cm.get("MSFT", DataType.OHLCV) is not None  # unaffected

    def test_invalidate_all_clears_everything(self):
        cm = CacheManager()
        cm.put(_make_result("AAPL"))
        cm.put(_make_result("MSFT", DataType.INFO))
        cm.invalidate_all()
        assert cm.size == 0


# ── DataContract tests ────────────────────────────────────────────────────────

class TestDataContractOHLCV:
    def test_valid_ohlcv(self):
        assert DataContract.validate(_make_ohlcv(), DataType.OHLCV, "AAPL") is None

    def test_not_dataframe(self):
        assert DataContract.validate({"Close": 100}, DataType.OHLCV, "AAPL") is not None

    def test_empty_dataframe(self):
        assert DataContract.validate(pd.DataFrame(), DataType.OHLCV, "AAPL") is not None

    def test_missing_close_column(self):
        df = _make_ohlcv().drop(columns=["Close"])
        assert DataContract.validate(df, DataType.OHLCV, "AAPL") is not None

    def test_missing_volume_column(self):
        df = _make_ohlcv().drop(columns=["Volume"])
        assert DataContract.validate(df, DataType.OHLCV, "AAPL") is not None

    def test_non_datetime_index(self):
        df = _make_ohlcv().reset_index(drop=True)
        assert DataContract.validate(df, DataType.OHLCV, "AAPL") is not None

    def test_non_numeric_close(self):
        df = _make_ohlcv()
        df["Close"] = "bad"
        assert DataContract.validate(df, DataType.OHLCV, "AAPL") is not None

    def test_intraday_same_as_ohlcv(self):
        # INTRADAY uses same shape checks as OHLCV
        assert DataContract.validate(_make_ohlcv(), DataType.INTRADAY, "AAPL") is None


class TestDataContractINFO:
    def test_valid_dict(self):
        assert DataContract.validate({"sector": "Tech", "marketCap": 3e12}, DataType.INFO, "AAPL") is None

    def test_not_dict(self):
        assert DataContract.validate("bad", DataType.INFO, "AAPL") is not None

    def test_empty_dict(self):
        assert DataContract.validate({}, DataType.INFO, "AAPL") is not None


class TestDataContractLIVE:
    def test_valid_positive_float(self):
        assert DataContract.validate(150.0, DataType.LIVE, "AAPL") is None

    def test_valid_positive_int(self):
        assert DataContract.validate(150, DataType.LIVE, "AAPL") is None

    def test_zero(self):
        assert DataContract.validate(0.0, DataType.LIVE, "AAPL") is not None

    def test_negative(self):
        assert DataContract.validate(-5.0, DataType.LIVE, "AAPL") is not None

    def test_string(self):
        assert DataContract.validate("150", DataType.LIVE, "AAPL") is not None

    def test_none(self):
        assert DataContract.validate(None, DataType.LIVE, "AAPL") is not None


class TestDataContractBATCH:
    def test_valid_batch(self):
        data = {"AAPL": _make_ohlcv(), "MSFT": _make_ohlcv()}
        assert DataContract.validate(data, DataType.BATCH, "BATCH") is None

    def test_not_dict(self):
        assert DataContract.validate(_make_ohlcv(), DataType.BATCH, "BATCH") is not None

    def test_empty_batch_is_valid(self):
        # Empty batch is structurally valid — callers handle missing keys
        assert DataContract.validate({}, DataType.BATCH, "BATCH") is None

    def test_inner_value_fails_ohlcv(self):
        data = {"AAPL": _make_ohlcv(), "BAD": pd.DataFrame()}
        assert DataContract.validate(data, DataType.BATCH, "BATCH") is not None
```

- [ ] **Step 2: Run tests — confirm all fail (classes don't exist yet)**

```bash
python3 -m pytest tests/test_data_manager_m2.py -v 2>&1 | tail -10
```

Expected: `ImportError: cannot import name 'CacheManager' from 'data_manager'`

### Step group B — Implement CacheManager

- [ ] **Step 3: Add `collections.OrderedDict` import to `data_manager.py`**

At the top of `data_manager.py`, add to the imports section:

```python
from collections import OrderedDict
```

- [ ] **Step 4: Add `CacheManager` class to `data_manager.py`**

Add after the `unavailable()` factory function (after line 125), before the `HealthSnapshot` dataclass:

```python
# ═══════════════════════════════════════════════════════════════════════════════
# Cache layer — M2
# ═══════════════════════════════════════════════════════════════════════════════

class CacheManager:
    """
    Bounded LRU in-memory cache (L2).

    Deployment note: Streamlit-specific.  Single-process, in-memory.
    Replaced by Vercel KV at migration (docs/migration/vercel-migration-plan.md).

    Key:        (ticker, DataType)
    Cap:        MAX_ENTRIES = 200  (across all data types combined)
    Eviction:   LRU — least-recently-used entry evicted when cap is reached
    TTL:        per DataType, mirrors market_data.py TTLs.
                get() returns ResultStatus.STALE (not None) for expired entries
                so callers can decide to serve stale rather than fetch fresh.
    Thread-safe: all public methods hold _lock.

    Usage (M4+, once bypass is False):
        cm = CacheManager()
        result = cm.get("AAPL", DataType.OHLCV)
        if result is None:
            result = <fetch from source>
            cm.put(result)
        elif result.is_stale:
            <serve stale, trigger background refresh>
    """

    MAX_ENTRIES: int = 200

    # TTL per DataType (seconds) — mirrors market_data.py TTL constants
    _TTL: dict = {
        DataType.LIVE:     5,
        DataType.OHLCV:    300,
        DataType.INTRADAY: 60,
        DataType.INFO:     600,
        DataType.BATCH:    300,
    }

    def __init__(self) -> None:
        # OrderedDict preserves insertion order and supports move_to_end() for O(1) LRU
        self._cache: OrderedDict = OrderedDict()  # (ticker, DataType) → DataResult
        self._lock  = threading.Lock()

    # ── Public interface ──────────────────────────────────────────────────────

    def get(self, ticker: str, data_type: DataType) -> "DataResult | None":
        """
        Returns DataResult if the entry exists (FRESH or STALE), None if not found.
        Moves the accessed entry to MRU position.
        Does NOT remove stale entries — callers decide whether to serve or drop.
        """
        key = (ticker, data_type)
        with self._lock:
            result = self._cache.get(key)
            if result is None:
                return None
            self._cache.move_to_end(key)           # mark as recently used

        ttl = self._TTL.get(data_type, 300)
        age = time.monotonic() - result.fetched_at
        if age <= ttl:
            return result

        # Past TTL — wrap as STALE so caller knows to trigger a background refresh
        return DataResult(
            status=ResultStatus.STALE,
            data=result.data,
            source=result.source,
            fetched_at=result.fetched_at,
            fetched_wall_time=result.fetched_wall_time,
            ticker=result.ticker,
            data_type=result.data_type,
            error_msg="Served from stale L2 cache",
        )

    def put(self, result: "DataResult") -> None:
        """
        Store result.  No-op if status == UNAVAILABLE.
        Evicts the LRU entry if adding would exceed MAX_ENTRIES.
        """
        if result.status == ResultStatus.UNAVAILABLE:
            return
        key = (result.ticker, result.data_type)
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = result
            while len(self._cache) > self.MAX_ENTRIES:
                self._cache.popitem(last=False)    # remove LRU (front of OrderedDict)

    def invalidate(self, ticker: str) -> None:
        """Remove all cache entries for this ticker across all DataTypes."""
        with self._lock:
            keys = [k for k in self._cache if k[0] == ticker]
            for k in keys:
                del self._cache[k]

    def invalidate_all(self) -> None:
        """Full cache wipe."""
        with self._lock:
            self._cache.clear()

    @property
    def size(self) -> int:
        """Current number of cached entries."""
        with self._lock:
            return len(self._cache)
```

### Step group C — Implement DataContract

- [ ] **Step 5: Add `DataContract` class to `data_manager.py`**

Add immediately after `CacheManager` (before `HealthSnapshot`):

```python
class DataContract:
    """
    Wire-level shape validator for each DataType.

    Validates that data received from yfinance has the correct structure —
    columns present, correct index type, non-empty, correct value type.

    Scope: wire-level ONLY.  Does NOT check row-count sufficiency for rolling
    indicators — that is compute_indicators()'s job (indicators.py:21).
    Keeping these concerns separate prevents Policy 5 violations
    (same metric = same function across all pages).

    Usage:
        reason = DataContract.validate(df, DataType.OHLCV, "AAPL")
        if reason is not None:
            return unavailable(ticker, DataType.OHLCV, reason)
    """

    @staticmethod
    def validate(data: Any, data_type: DataType, ticker: str) -> "str | None":
        """
        Returns None if data passes the contract for data_type.
        Returns a reason string (non-empty) if validation fails.
        Never raises — all exceptions are caught and returned as reason strings.
        """
        try:
            if data_type in (DataType.OHLCV, DataType.INTRADAY):
                return DataContract._validate_ohlcv(data)
            if data_type == DataType.INFO:
                return DataContract._validate_info(data)
            if data_type == DataType.LIVE:
                return DataContract._validate_live(data)
            if data_type == DataType.BATCH:
                return DataContract._validate_batch(data)
            return f"Unknown DataType: {data_type}"
        except Exception as exc:
            return f"DataContract internal error for {ticker}/{data_type}: {exc}"

    # ── Per-type validators ───────────────────────────────────────────────────

    @staticmethod
    def _validate_ohlcv(data: Any) -> "str | None":
        if not isinstance(data, pd.DataFrame):
            return "OHLCV: expected pd.DataFrame"
        if data.empty:
            return "OHLCV: DataFrame is empty"
        required = {"Open", "High", "Low", "Close", "Volume"}
        missing = required - set(data.columns)
        if missing:
            return f"OHLCV: missing columns {sorted(missing)}"
        if not pd.api.types.is_datetime64_any_dtype(data.index):
            return "OHLCV: index is not DatetimeIndex"
        if not pd.api.types.is_numeric_dtype(data["Close"]):
            return "OHLCV: Close column is not numeric"
        return None

    @staticmethod
    def _validate_info(data: Any) -> "str | None":
        if not isinstance(data, dict):
            return "INFO: expected dict"
        if not data:
            return "INFO: empty dict"
        return None

    @staticmethod
    def _validate_live(data: Any) -> "str | None":
        if not isinstance(data, (int, float)):
            return "LIVE: expected numeric (int or float)"
        if data <= 0:
            return f"LIVE: price must be positive, got {data}"
        return None

    @staticmethod
    def _validate_batch(data: Any) -> "str | None":
        if not isinstance(data, dict):
            return "BATCH: expected dict"
        # Each value must pass the OHLCV contract
        for sym, df in data.items():
            reason = DataContract._validate_ohlcv(df)
            if reason is not None:
                return f"BATCH[{sym}]: {reason}"
        return None
```

### Step group D — Wire into DataManager

- [ ] **Step 6: Add `_cache_manager` to `DataManager.__init__`**

In `DataManager.__init__` (line 281), add after `self._lock = threading.Lock()`:

```python
        # M2: L2 bounded LRU cache — bypass=True means no data flows through it yet.
        # Wired to fetch()/fetch_batch() in M4.  invalidate() and invalidate_all()
        # delegate here immediately so the interface is consistent from M2 onward.
        self._cache_manager: CacheManager = CacheManager()
```

- [ ] **Step 7: Wire `invalidate()` and `invalidate_all()` to CacheManager**

Replace the stub implementations of `invalidate()` and `invalidate_all()` in `DataManager`:

```python
    def invalidate(self, ticker: str) -> None:
        """
        Atomically clears all cache layers for this ticker.
        Called on stock switch (replaces cache_buster pattern in M4).
        M2: clears L2 CacheManager.
        """
        self._cache_manager.invalidate(ticker)

    def invalidate_all(self) -> None:
        """
        Full cache wipe.  Called on global Refresh button.
        M2: clears L2 CacheManager.
        """
        self._cache_manager.invalidate_all()
```

- [ ] **Step 8: Update `DataManager.__init__` docstring to reflect M2 state**

Change the `M1 state` block in the class docstring:

```python
    M2 state
    --------
    bypass_mode == True (property).
    Pages continue calling market_data.py directly.
    All fetch() stubs return UNAVAILABLE — pages must NOT call them yet.
    CacheManager (L2 bounded LRU, 200 entries) is initialised and wired to
    invalidate() / invalidate_all().
    DataContract validator is available for use by source adapters (M4).
    Circuit breakers are instantiated and ready for M4/M5 source adapters.
```

### Step group E — Run and commit

- [ ] **Step 9: Run unit tests — confirm all pass**

```bash
python3 -m pytest tests/test_data_manager_m2.py -v 2>&1 | tail -20
```

Expected: all tests PASS. If any fail, read the error — it points to a contract mismatch between the test helper and your implementation (e.g. `_make_result` uses `fetched_wall_time` which requires the `DataResult` fix from T1).

- [ ] **Step 10: Extend R24 in `regression.py`**

At the end of the R24 block (after line 718), add:

```python
    # R24.M2 — CacheManager + DataContract contracts
    chk("R24.M2", "dm_cache_manager_class",
        "class CacheManager" in dm,
        "CacheManager class must be defined in data_manager.py (M2)")

    chk("R24.M2", "dm_cache_manager_get",
        "def get(" in dm and "CacheManager" in dm,
        "CacheManager.get() method must be defined")

    chk("R24.M2", "dm_cache_manager_put",
        "def put(" in dm and "CacheManager" in dm,
        "CacheManager.put() method must be defined")

    chk("R24.M2", "dm_data_contract_class",
        "class DataContract" in dm,
        "DataContract class must be defined in data_manager.py (M2)")

    chk("R24.M2", "dm_data_contract_validate",
        "def validate(" in dm and "DataContract" in dm,
        "DataContract.validate() static method must be defined")

    chk("R24.M2", "dm_cache_manager_wired",
        "_cache_manager" in dm,
        "DataManager must hold a _cache_manager instance (M2)")
```

- [ ] **Step 11: Run regression — confirm new checks pass and count increments**

```bash
python3 regression.py 2>&1 | tail -5
```

Expected: `ALL 452 CHECKS PASS` (446 + 6 new R24.M2 checks).

- [ ] **Step 12: Commit**

```bash
git add data_manager.py tests/__init__.py tests/test_data_manager_m2.py regression.py
git commit -m "feat(data_manager): M2 — CacheManager (bounded LRU L2, 200 entries) + DataContract wire-level validator + R24.M2 regression checks"
```

---

## Task 6: Regression Baseline + Final Doc Updates

**Files:**
- Modify: `CLAUDE.md`
- Modify: `GSI_SPRINT.md`

- [ ] **Step 1: Update regression baseline in CLAUDE.md to post-M2 count**

Run regression one final time:

```bash
python3 regression.py 2>&1 | grep "TOTAL"
```

Note the new count (expected: 452). In `CLAUDE.md` Current State section, update:

```
**Regression baseline: 452/452 PASS**
```

(Replace the 446 value set in T4 with the final post-M2 count.)

- [ ] **Step 2: Update OPEN-007 in CLAUDE.md**

In the Open Items table, find OPEN-007 and replace:

```
| **OPEN-007** | **HIGH** | **DataManager M2: CacheManager + DataContract validator (M1 complete)** |
```

with:

```
| OPEN-007-M3 | LOW | DataManager M3: priority queue + worker thread — **DEFERRED** (Vercel Workflow DevKit replaces this; see docs/migration/vercel-migration-plan.md) |
```

- [ ] **Step 3: Add CacheManager and DataContract to CLAUDE.md file structure**

In the `### Code files — safe rebuild order` section, find the `data_manager.py` line and update its description:

```
data_manager.py         DataManager M2 skeleton + CircuitBreaker + CacheManager (L2 LRU) + DataContract validator. Bypass mode until M4.
```

- [ ] **Step 4: Run sync_docs.py**

```bash
python3 sync_docs.py 2>&1 | tail -5
```

Expected: `sync_docs: exit 0` (or equivalent success message — no SEMI-auto prompts for these changes).

- [ ] **Step 5: Add v5.39 Done section to GSI_SPRINT.md**

In `GSI_SPRINT.md`, add a Done section:

```markdown
## v5.39 — Done (session_028, 2026-04-15)

- T1: DataManager M1 critical bugs fixed (lock ordering, empty _breakers fallback, bypass_mode property, fetched_wall_time, HealthSnapshot str keys)
- T2: get_ticker_info stale fallback via _info_cache — fundamentals survive 429 cooldown
- T3: Plotly bar opacity fix — Sprint Monitor token budget chart renders without error
- T4: Closed OPEN-027/028/029 (resolved v5.37), updated regression baseline, fixed meta.last_session
- T5: DataManager M2 — CacheManager (bounded LRU 200 entries) + DataContract (wire-level) + R24.M2 regression checks + unit tests
- T6: Docs + baseline updated, OPEN-007 M3 deferred (Vercel Workflow DevKit territory)
- Regression: 452/452 PASS
```

- [ ] **Step 6: Run final regression**

```bash
python3 regression.py 2>&1 | tail -5
```

Expected: `ALL 452 CHECKS PASS`.

- [ ] **Step 7: Commit**

```bash
git add CLAUDE.md GSI_SPRINT.md
git commit -m "docs(v5.39): update baseline to 452, close OPEN-007 M2, defer M3, update file structure"
```

---

## Task 7: Token Burn Log (Policy 8 / R35)

**Files:**
- Modify: `docs/ai-ops/token-burn-log.jsonl`

- [ ] **Step 1: Append actuals entry to token-burn-log.jsonl**

Append one line to `docs/ai-ops/token-burn-log.jsonl`:

```json
{"schema_version": "1", "sprint": "v5.39", "date_opened": "2026-04-15", "date_closed": "2026-04-15", "sessions": ["session_028"], "actual_tokens_methodology": "self_estimate", "items": [{"id": "T1-m1-critical-fixes", "model": "haiku", "mode": "sequential", "est_tokens": "8k-10k", "actual_tokens": null, "quality": {"regression_passed_first_try": null, "rework_rounds": 0, "wasted_tokens_est": 0, "outcome": "clean"}}, {"id": "T2-info-cache-stale", "model": "haiku", "mode": "sequential", "est_tokens": "6k-8k", "actual_tokens": null, "quality": {"regression_passed_first_try": null, "rework_rounds": 0, "wasted_tokens_est": 0, "outcome": "clean"}}, {"id": "T3-plotly-opacity", "model": "haiku", "mode": "sequential", "est_tokens": "4k-6k", "actual_tokens": null, "quality": {"regression_passed_first_try": null, "rework_rounds": 0, "wasted_tokens_est": 0, "outcome": "clean"}}, {"id": "T4-doc-cleanup", "model": "haiku", "mode": "sequential", "est_tokens": "5k-7k", "actual_tokens": null, "quality": {"regression_passed_first_try": null, "rework_rounds": 0, "wasted_tokens_est": 0, "outcome": "clean"}}, {"id": "T5-cachemanager-datacontract", "model": "sonnet", "mode": "sequential", "est_tokens": "35k-45k", "actual_tokens": null, "quality": {"regression_passed_first_try": null, "rework_rounds": 0, "wasted_tokens_est": 0, "outcome": "clean"}}, {"id": "T6-regression-docs", "model": "haiku", "mode": "sequential", "est_tokens": "5k-7k", "actual_tokens": null, "quality": {"regression_passed_first_try": null, "rework_rounds": 0, "wasted_tokens_est": 0, "outcome": "clean"}}, {"id": "T7-token-burn-log", "model": "haiku", "mode": "sequential", "est_tokens": "3k-5k", "actual_tokens": null, "quality": {"regression_passed_first_try": null, "rework_rounds": 0, "wasted_tokens_est": 0, "outcome": "clean"}}], "overhead": {"regression_runs_actual": null, "sync_docs_actual": null, "sprint_close_actual": null}, "totals": {"est_tokens_sum": "66k-88k", "actual_tokens_sum": null, "delta_vs_est": null, "variance_pct": null}, "learnings": ""}
```

- [ ] **Step 2: Verify JSONL is parseable**

```bash
python3 docs/ai-ops/analyze_token_burns.py 2>&1 | tail -10
```

Expected: no parse errors; the v5.39 entry appears in the output table.

- [ ] **Step 3: Run final regression**

```bash
python3 regression.py 2>&1 | tail -5
```

Expected: `ALL 452 CHECKS PASS`.

- [ ] **Step 4: Run compliance check**

```bash
python3 compliance_check.py 2>&1 | tail -3
```

Expected: `10/10 compliance checks passed`.

- [ ] **Step 5: Update GSI_WIP.md to IDLE**

Set `Status: IDLE` and `Session ID: session_028` and `Sprint: v5.39 COMPLETE` in `GSI_WIP.md`.

- [ ] **Step 6: Final commit**

```bash
git add docs/ai-ops/token-burn-log.jsonl GSI_WIP.md
git commit -m "chore(v5.39): token burn log entry + WIP → IDLE — sprint complete"
```

---

## Self-Review

**Spec coverage check:**
- T1: M1 critical bugs ✅ (lock ordering, empty _breakers, bypass_mode property, fetched_wall_time, str keys)
- T2: get_ticker_info stale fallback ✅
- T3: Plotly opacity fix ✅
- T4: OPEN-027/028/029 closure + baseline + last_session ✅
- T5: CacheManager bounded LRU + DataContract wire-level + unit tests + R24 extension ✅
- T6: regression baseline + docs + sync_docs ✅
- T7: token burn log ✅
- Migration portability note ✅ (in spec, referenced in T6 step for OPEN-007 M3 defer)
- Success criteria all covered ✅

**Placeholder scan:** No TBD, TODO, "similar to above", or incomplete steps found.

**Type consistency:**
- `CacheManager.get()` returns `DataResult | None` — consistent across T5 steps 4, 9 and test file
- `DataContract.validate()` returns `str | None` — consistent across T5 steps 5, 9 and test file
- `DataResult.fetched_wall_time` added in T1 step 4 — used in T5 test helper `_make_result` ✅
- `bypass_mode` changed to `@property` in T1 step 3 — call sites updated in same step ✅
- `HealthSnapshot.sources` changed to `str` keys in T1 steps 1 and 5 — consistent ✅
