"""
data_manager.py — Global Stock Intelligence Dashboard
DataManager: resilient data access layer.

Milestone history:
  M1 (v5.27) — Skeleton + bypass mode + circuit breaker + type definitions.
               No pages are routed through DataManager yet.
               All fetch() stubs return UNAVAILABLE.
               bypass_mode() == True always in M1.
  M2          — CacheManager (L2 + L3) + DataContract validator.
  M3          — Priority queue + request coalescer + worker thread.
  M4          — YAHOO adapter + pages migration + cache_buster retirement.
  M5          — nsepython + FRED fallback adapters.
  M6          — Observability UI + hardening.

DO NOT:
  - Route RSS news fetches through DataManager.  Ever.
    RSS has no fallback chain and no circuit breaker. It stays in market_data.py.
  - Instantiate DataManager directly.  Use get_datamanager().
  - Use a module-level variable for the singleton.  @st.cache_resource only.
  - Import market_data from this file (circular import risk in M4).
"""

from __future__ import annotations

import logging
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

import pandas as pd
import streamlit as st

log = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Enumerations
# ═══════════════════════════════════════════════════════════════════════════════

class Priority(Enum):
    P0 = 0  # Live price tile / intraday — user is actively watching
    P1 = 1  # Stock dashboard OHLCV / fundamentals — just selected
    P2 = 2  # Background warm-up / deferred fragments


class DataType(Enum):
    OHLCV    = auto()  # Historical OHLCV DataFrame
    INFO     = auto()  # Fundamentals dict (P/E, P/B, etc.)
    LIVE     = auto()  # Single live price (float)
    INTRADAY = auto()  # 1-minute bars DataFrame
    BATCH    = auto()  # Multi-ticker OHLCV (group heatmap / movers)


class ResultStatus(Enum):
    FRESH       = auto()  # Fetched from source within TTL
    CACHED      = auto()  # Served from cache, within TTL
    STALE       = auto()  # Served from cache, past TTL — source unavailable
    UNAVAILABLE = auto()  # No data anywhere — caller must render error card


class SourceTag(Enum):
    YAHOO       = auto()  # yfinance + yahooquery (one logical source, one breaker)
    NSEPYTHON   = auto()  # India tickers only
    FRED        = auto()  # Rates group only (~5 of 7 tickers)
    STALE_CACHE = auto()  # _ticker_cache fallback (module-level dict in market_data.py)


class CircuitState(Enum):
    CLOSED    = auto()  # Normal — requests pass through
    OPEN      = auto()  # Dead — requests rejected immediately
    HALF_OPEN = auto()  # Recovery probe — exactly one request allowed


# ═══════════════════════════════════════════════════════════════════════════════
# Data types
# ═══════════════════════════════════════════════════════════════════════════════

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


def unavailable(ticker: str, data_type: DataType, reason: str) -> DataResult:
    """
    Factory for UNAVAILABLE DataResult.
    Use this everywhere — never construct DataResult(UNAVAILABLE) inline.
    Never return None from any DataManager method.

    Note: fetched_wall_time defaults to time.time() at construction — it does NOT
    represent a real fetch time.  Callers must guard on .ok or status before using
    fetched_wall_time for Policy 7 "data as of HH:MM" display.
    """
    return DataResult(
        status=ResultStatus.UNAVAILABLE,
        data=None,
        source=None,
        fetched_at=time.monotonic(),
        ticker=ticker,
        data_type=data_type,
        error_msg=reason,
    )


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
            stored = result
        # Lock released before constructing stale DataResult (no allocation under lock)
        ttl = self._TTL.get(data_type, 300)
        age = time.monotonic() - stored.fetched_at
        if age <= ttl:
            return stored

        # Past TTL — wrap as STALE so caller knows to trigger a background refresh
        return DataResult(
            status=ResultStatus.STALE,
            data=stored.data,
            source=stored.source,
            fetched_at=stored.fetched_at,
            fetched_wall_time=stored.fetched_wall_time,
            ticker=stored.ticker,
            data_type=stored.data_type,
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


# ═══════════════════════════════════════════════════════════════════════════════
# Circuit breaker
# ═══════════════════════════════════════════════════════════════════════════════

class CircuitBreaker:
    """
    Per-source circuit breaker.  Three-state machine:

        CLOSED ──(N consecutive failures)──► OPEN
           ▲                                   │
           │ (probe succeeds)      (recovery    │
           │                       window       │
        HALF_OPEN ◄────────────────elapsed)────┘
           │
           └──(probe fails)──► OPEN (recovery_window *= 1.5, capped at 600s)

    Thread-safe: all state reads and transitions hold _lock.
    HALF_OPEN grants exactly one probe slot — subsequent callers get False
    until the probe resolves via record_success() or record_failure().
    """

    def __init__(
        self,
        source:            SourceTag,
        failure_threshold: int   = 3,
        recovery_window_s: float = 60.0,
        probe_timeout_s:   float = 10.0,
    ) -> None:
        self.source            = source
        self.failure_threshold = failure_threshold
        self.probe_timeout_s   = probe_timeout_s

        self._recovery_window: float = recovery_window_s
        self._state:           CircuitState  = CircuitState.CLOSED
        self._failure_count:   int           = 0
        self._last_failure_at: float         = 0.0
        self._probe_granted:   bool          = False
        self._lock:            threading.Lock = threading.Lock()

    # ── Public read ───────────────────────────────────────────────────────────

    @property
    def state(self) -> CircuitState:
        with self._lock:
            return self._state

    # ── Decision ──────────────────────────────────────────────────────────────

    def allow_request(self) -> bool:
        """
        Returns True if a request should proceed.
        CLOSED  → always True.
        OPEN    → False unless recovery_window elapsed, then transition to HALF_OPEN → True (once).
        HALF_OPEN → True for exactly one probe; False for all subsequent callers.
        """
        with self._lock:
            if self._state == CircuitState.CLOSED:
                return True

            if self._state == CircuitState.OPEN:
                elapsed = time.monotonic() - self._last_failure_at
                if elapsed >= self._recovery_window:
                    self._state = CircuitState.HALF_OPEN
                    self._probe_granted = False
                    log.info("CircuitBreaker HALF_OPEN for %s (recovery probe)", self.source.name)
                else:
                    return False

            # HALF_OPEN — grant exactly one probe slot
            if self._state == CircuitState.HALF_OPEN:
                if not self._probe_granted:
                    self._probe_granted = True
                    return True
                return False  # probe already in flight

            return False

    # ── Outcome recording ─────────────────────────────────────────────────────

    def record_success(self) -> None:
        """Call after any successful fetch from this source."""
        with self._lock:
            prev = self._state
            self._failure_count = 0
            self._probe_granted = False
            self._state         = CircuitState.CLOSED
            if prev != CircuitState.CLOSED:
                log.info("CircuitBreaker CLOSED for %s (recovery succeeded)", self.source.name)

    def record_failure(self) -> None:
        """Call after any failed fetch from this source."""
        with self._lock:
            self._failure_count  += 1
            self._last_failure_at = time.monotonic()

            if self._state == CircuitState.HALF_OPEN:
                # Probe failed — back to OPEN, extend recovery window (exponential, cap 600s)
                self._recovery_window = min(self._recovery_window * 1.5, 600.0)
                self._state           = CircuitState.OPEN
                self._probe_granted   = False
                log.warning(
                    "CircuitBreaker OPEN for %s (probe failed, next window=%.0fs)",
                    self.source.name,
                    self._recovery_window,
                )
                return

            if (
                self._state == CircuitState.CLOSED
                and self._failure_count >= self.failure_threshold
            ):
                self._state = CircuitState.OPEN
                log.warning(
                    "CircuitBreaker OPEN for %s after %d consecutive failures",
                    self.source.name,
                    self._failure_count,
                )


# ═══════════════════════════════════════════════════════════════════════════════
# DataManager
# ═══════════════════════════════════════════════════════════════════════════════

class DataManager:
    """
    Singleton resilient data access layer.

    Obtain via:   dm = get_datamanager()
    Never:        dm = DataManager()   ← bypasses cache_resource, creates duplicates

    M2 state
    --------
    bypass_mode == True (property).
    Pages continue calling market_data.py directly.
    All fetch() stubs return UNAVAILABLE — pages must NOT call them yet.
    CacheManager (L2 bounded LRU, 200 entries) is initialised and wired to
    invalidate() / invalidate_all().
    DataContract validator is available for use by source adapters (M4).
    Circuit breakers are instantiated and ready for M4/M5 source adapters.
    """

    def __init__(self) -> None:
        self._bypass:        bool  = True    # M1: always True. Set False in M3.
        self._healthy:       bool  = False   # M1/M2/M3: False. True when source adapter live.
        self._cache_hits:    int   = 0
        self._cache_misses:  int   = 0
        self._last_fetch_at: float | None = None
        self._lock:          threading.Lock = threading.Lock()

        # M2: L2 bounded LRU cache — bypass=True means no data flows through it yet.
        # Wired to fetch()/fetch_batch() in M4.  invalidate() and invalidate_all()
        # delegate here immediately so the interface is consistent from M2 onward.
        self._cache_manager: CacheManager = CacheManager()

        # One circuit breaker per logical source.
        # YAHOO covers both yfinance and yahooquery (same IP, same breaker).
        self._breakers: dict[SourceTag, CircuitBreaker] = {
            SourceTag.YAHOO: CircuitBreaker(
                SourceTag.YAHOO,
                failure_threshold=3,
                recovery_window_s=60.0,
                probe_timeout_s=10.0,
            ),
            SourceTag.NSEPYTHON: CircuitBreaker(
                SourceTag.NSEPYTHON,
                failure_threshold=3,
                recovery_window_s=120.0,
                probe_timeout_s=15.0,
            ),
            SourceTag.FRED: CircuitBreaker(
                SourceTag.FRED,
                failure_threshold=3,
                recovery_window_s=300.0,
                probe_timeout_s=10.0,
            ),
            SourceTag.STALE_CACHE: CircuitBreaker(
                SourceTag.STALE_CACHE,
                failure_threshold=999,   # never opens — stale cache is always available
                recovery_window_s=1.0,
                probe_timeout_s=0.1,
            ),
        }

        log.info("DataManager M2 initialised — bypass_mode=True, CacheManager ready, circuit breakers ready")

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    @property
    def bypass_mode(self) -> bool:
        """
        True while DataManager is in bypass (M1–M2).
        When True, all pages use market_data.py directly.
        Set False in M3 once the worker thread and queue are live.
        """
        return self._bypass

    def is_healthy(self) -> bool:
        """
        True if at least one source breaker is CLOSED and DataManager is not in bypass.
        Pages call this before deciding whether to use DataManager or fall back to
        direct market_data.py calls.
        M1: always False.
        """
        if self._bypass:
            return False
        return any(
            b.state == CircuitState.CLOSED
            for b in self._breakers.values()
            if b.source != SourceTag.STALE_CACHE
        )

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

    def get_breaker(self, source: SourceTag) -> CircuitBreaker:
        """Direct access to a source's circuit breaker. Used by source adapters (M4/M5)."""
        return self._breakers[source]

    # ── Data access — M1 stubs ────────────────────────────────────────────────
    # Pages do NOT call these in M1.  Wired in M3/M4.

    def fetch(
        self,
        ticker:     str,
        data_type:  DataType,
        priority:   Priority,
        max_age_s:  int | None  = None,
        session_id: str | None  = None,
    ) -> DataResult:
        """
        Synchronous data fetch.  Returns DataResult — never raises.
        M1: always returns UNAVAILABLE (bypass mode).
        M3+: check cache → coalesce → enqueue → wait → return.
        """
        return unavailable(ticker, data_type, "DataManager in bypass mode (M1 — pages use market_data.py directly)")

    def fetch_batch(
        self,
        tickers:    list[str],
        data_type:  DataType,
        priority:   Priority,
        max_age_s:  int | None  = None,
        session_id: str | None  = None,
    ) -> dict[str, DataResult]:
        """
        Batch fetch.  Returns partial results — callers handle missing keys.
        M1: all tickers return UNAVAILABLE.
        """
        return {
            t: unavailable(t, data_type, "DataManager in bypass mode (M1)")
            for t in tickers
        }

    def invalidate(self, ticker: str) -> None:
        """
        Atomically clears all cache layers for this ticker.
        Called on stock switch (replaces cache_buster pattern in M4).
        M2: clears L2 CacheManager.
        """
        if self._cache_manager is not None:
            self._cache_manager.invalidate(ticker)

    def invalidate_all(self) -> None:
        """
        Full cache wipe.  Called on global Refresh button.
        M2: clears L2 CacheManager.
        """
        if self._cache_manager is not None:
            self._cache_manager.invalidate_all()

    def prefetch(self, tickers: list[str], data_type: DataType) -> None:
        """
        Fire-and-forget P2 enqueue for background warm-up.
        M1: no-op.
        """


# ═══════════════════════════════════════════════════════════════════════════════
# Singleton factory — the only public entry point
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def get_datamanager() -> DataManager:
    """
    Returns the shared DataManager singleton.

    @st.cache_resource ensures exactly one instance per Streamlit process,
    shared across all user sessions and all reruns.

    If DataManager.__init__ raises (should never happen in M1),
    a safe bypass-mode instance is returned so the app degrades gracefully
    rather than crashing on startup.

    Usage:
        from data_manager import get_datamanager, DataType, Priority
        dm = get_datamanager()
        if dm.bypass_mode:
            df = get_price_data(ticker, ...)   # direct market_data.py call
        else:
            result = dm.fetch(ticker, DataType.OHLCV, Priority.P1)
    """
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
        dm._cache_manager = None  # M2: None signals no cache available in emergency fallback
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
