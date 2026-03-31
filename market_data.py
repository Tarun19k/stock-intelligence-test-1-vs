# market_data.py
# Depends on: utils
# Called from: app.py, pages/home.py, pages/dashboard.py,
#              pages/global_intelligence.py, pages/week_summary.py
# Contains: get_price_data, get_ticker_info, get_top_movers, get_news
#
# FIX (v5.16): Added cache_buster: int = 0 param to all four public functions.
# Streamlit's @st.cache_data keys on ALL args — passing a different cb value
# forces a fresh fetch, making the "Refresh data" button and auto-refresh
# actually work. Default=0 means existing call sites continue to work.

import time
import feedparser
import pandas as pd
import yfinance as yf
import logging as _logging
_logging.getLogger("yfinance").setLevel(_logging.ERROR)   # silence "Failed download" warnings
_logging.getLogger("peewee").setLevel(_logging.ERROR)     # silence peewee ORM noise
import warnings as _warnings
# yfinance 1.2.0 was updated for pandas 3.0 compatibility (PR #2683).
# This filter suppresses any residual FutureWarning / Pandas4Warning from
# yfinance internals during the transition window.
_warnings.filterwarnings("ignore", category=FutureWarning, module="yfinance")
import streamlit as st
from urllib.parse import urlparse
from utils import safe_run, log_error, safe_url, safe_ticker_key

# ── RSS allowlist ─────────────────────────────────────────────────────────────
_ALLOWED_RSS_DOMAINS = {
    "feeds.feedburner.com", "feeds.reuters.com",
    "timesofindia.indiatimes.com", "economictimes.indiatimes.com",
    "aljazeera.com", "techcrunch.com", "finance.yahoo.com",
    "bbci.co.uk", "bbc.co.uk", "bbc.com",
    "artificialintelligence-news.com", "ndtvprofit.com",
    "moneycontrol.com", "livemint.com", "businessstandard.com",
    "thehindubusinessline.com", "financialexpress.com",
    "theinternetpatrol.com",
}

def _is_allowed_rss(url: str) -> bool:
    if not safe_url(url):
        return False
    try:
        host = urlparse(url).netloc.lower().lstrip("www.")
        return any(host == d or host.endswith("." + d) for d in _ALLOWED_RSS_DOMAINS)
    except Exception:
        return False

# ── Token-bucket rate limiter ────────────────────────────────────────────────
# Yahoo Finance from datacenter IPs: safe rate is ~5 req/s sustained.
# Token bucket: holds up to 5 tokens, refills at 1 token per 0.4s.
# This lets a burst of 5 fire immediately, then paces at ~2.5 req/s.
# Result: 49-stock group loads in ~20s instead of 122s with a flat 2.5s delay.
import threading as _threading
_RATE_LOCK    = _threading.Lock()
_BUCKET_MAX   = 5      # max burst size
_BUCKET_RATE  = 0.4    # seconds per token (2.5 tokens/second)
_bucket_tokens = [float(_BUCKET_MAX)]
_bucket_last   = [time.monotonic()]

# ── Global rate-limit cooldown gate (v5.27) ──────────────────────────────────
# When Yahoo Finance returns 429, ALL fetches across ALL fragments must pause.
# _global_throttle() serialises concurrent calls but doesn't stop the VOLUME
# of TTL-triggered retries. This gate adds a timed pause that every download
# path checks BEFORE touching yfinance. Uses exponential backoff per hit.
#
# Design:
#   _rl_cooldown_until  — monotonic timestamp after which fetches may resume
#   _rl_hit_count       — consecutive 429 count → drives backoff multiplier
#   _is_rate_limited()  — fast read, called before every download attempt
#   _set_rate_limited() — called on any 429; sets cooldown + increments counter
#   _clear_rate_limit_state() — called on clean batch success; resets counter
#
# Backoff schedule:  1st hit → 90s  |  2nd → 120s  |  3rd+ → 180s
# Thread safety: _rl_cooldown_until needs `global` (float, immutable).
#                _rl_hit_count is a list — mutated in-place, GIL-safe.
_rl_cooldown_until: float = 0.0
_rl_hit_count: list = [0]   # list so nested fns mutate without `global`

def _is_rate_limited() -> bool:
    """True if inside a 429 cooldown window. Fast path — no lock needed."""
    return time.monotonic() < _rl_cooldown_until

def _set_rate_limited(base_seconds: int = 90) -> None:
    """
    Engage global cooldown on 429. Exponential backoff capped at 180s.
    ALL subsequent _yf_batch_download and _yf_download calls will short-circuit
    until the cooldown expires, eliminating the retry storm.
    """
    global _rl_cooldown_until
    _rl_hit_count[0] += 1
    wait = min(base_seconds * (2 ** min(_rl_hit_count[0] - 1, 2)), 180)
    _rl_cooldown_until = time.monotonic() + wait
    log_error(
        "rate_limiter:429",
        Exception(f"Global cooldown: {wait}s (consecutive hit #{_rl_hit_count[0]})")
    )

def _clear_rate_limit_state() -> None:
    """Reset consecutive hit counter after a fully clean batch. No global needed."""
    _rl_hit_count[0] = 0

def _global_throttle():
    """Token-bucket throttle. Fast for small bursts, paced for sustained use."""
    with _RATE_LOCK:
        now = time.monotonic()
        # Replenish tokens based on elapsed time
        elapsed = now - _bucket_last[0]
        _bucket_tokens[0] = min(_BUCKET_MAX, _bucket_tokens[0] + elapsed / _BUCKET_RATE)
        _bucket_last[0] = now
        if _bucket_tokens[0] >= 1.0:
            _bucket_tokens[0] -= 1.0
        else:
            # Need to wait for next token
            wait = _BUCKET_RATE * (1.0 - _bucket_tokens[0])
            time.sleep(wait)
            _bucket_tokens[0] = 0.0
            _bucket_last[0] = time.monotonic()


# ── Single-ticker download with retry ────────────────────────────────────────
def _yf_download(ticker: str, **kwargs) -> pd.DataFrame:
    """
    Single-ticker download with global cooldown check (v5.27).
    If _is_rate_limited(), returns immediately — don't wait for yfinance to 429.
    On 429: calls _set_rate_limited() and returns empty — no per-attempt sleep.
    The global cooldown handles recovery; re-trying in 2s just burns quota.
    """
    ticker = safe_ticker_key(ticker)           # RISK-003: strip non-ticker chars
    for attempt in range(3):
        if _is_rate_limited():                         # v5.27 — abort during cooldown
            return pd.DataFrame()
        _global_throttle()
        try:
            df = yf.download(ticker, **kwargs)
            return df if df is not None else pd.DataFrame()
        except Exception as exc:
            _fetch_errors[ticker] = _fetch_errors.get(ticker, 0) + 1
            if type(exc).__name__ == "YFRateLimitError":
                _set_rate_limited()                    # v5.27 — engage global cooldown
                return pd.DataFrame()                  # don't retry — cooldown handles it
            return pd.DataFrame()
    return pd.DataFrame()


# ── Module-level ticker cache (survives across Streamlit rerenders) ────────────
# Stores the last successfully fetched DataFrame per ticker.
# Yahoo Finance rate-limits on cold start from datacenter IPs — this ensures
# that once data is fetched it is never lost between rerenders, even if the
# next fetch is blocked. TTL-controlled at call site via st.cache_data.
_ticker_cache: dict = {}
_ticker_cache_time: dict = {}
_TICKER_CACHE_TTL = 300  # seconds — match get_price_data TTL

# ── Observability instrumentation (v5.34) ────────────────────────────────────
# No Streamlit calls — pure counters. Read via get_health_stats() / get_rate_limit_state().
_cache_stats: dict = {"hits": 0, "misses": 0}   # _ticker_cache read counters
_fetch_errors: dict = {}                          # ticker → consecutive error count
_fetch_latency_ms: list = []                      # rolling 20 yfinance fetch times (ms)


def is_ticker_cache_warm(tickers: tuple) -> bool:
    """
    Returns True if MOST tickers have a valid entry in the module-level
    _ticker_cache (populated by _yf_batch_download on first successful fetch).
    Uses a majority threshold (>=70%) rather than all() — a single failing
    ticker (e.g. USDINR=X, GC=F under rate limits) should not block signals
    and movers indefinitely when 9/10 price cards are already displaying.
    Intentionally does NOT check _ticker_cache_time TTL — the module-level
    dict is already managed by the 300s @st.cache_data TTL on get_batch_data.
    """
    if not tickers:
        return False
    warm = sum(1 for sym in tickers if sym in _ticker_cache)
    return warm >= max(1, int(len(tickers) * 0.7))


def _parse_batch_raw(raw, tickers: list) -> dict:
    """Extract per-ticker DataFrames from a yf.download() grouped result."""
    result = {}
    if raw is None or raw.empty:
        return result
    if len(tickers) == 1:
        df = _normalize_df(raw.copy())
        if not df.empty:
            df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True)
            result[tickers[0]] = df
    else:
        levels = raw.columns.get_level_values(1) if isinstance(raw.columns, pd.MultiIndex) else []
        for sym in tickers:
            try:
                if sym in levels:
                    df = raw[sym].copy()
                elif sym in raw.columns:
                    df = raw[[sym]].copy()
                else:
                    continue
                if isinstance(df, pd.DataFrame) and not df.empty:
                    df = _normalize_df(df)
                    df.index = pd.to_datetime(df.index)
                    df.sort_index(inplace=True)
                    result[sym] = df
            except Exception:
                pass
    return result


# ── Multi-ticker chunked batch download ───────────────────────────────────────
def _yf_batch_download(tickers: list, period: str = "5d",
                       interval: str = "1d") -> dict:
    """
    Chunked batch downloader with global cooldown gate (v5.27).

    v5.27 changes:
    - Check _is_rate_limited() at entry: if in cooldown, serve _ticker_cache
      immediately — zero yfinance calls, zero queue additions.
    - Check _is_rate_limited() before EACH chunk: a 429 on chunk 1 sets
      cooldown; chunk 2 will see it and skip rather than also firing.
    - On 429: call _set_rate_limited(), serve stale cache for failed tickers,
      break out of chunk loop. Don't sleep-then-continue.
    - On clean success: call _clear_rate_limit_state() to reset backoff counter.
    """
    if not tickers:
        return {}
    tickers = [safe_ticker_key(t) for t in tickers]   # RISK-003: strip non-ticker chars

    # v5.27 — Gate 1: global cooldown active → serve stale cache, no fetch
    if _is_rate_limited():
        cached = {sym: _ticker_cache[sym] for sym in tickers if sym in _ticker_cache}
        if not cached:
            raise RuntimeError("rate_limited_no_cache")   # don't cache empty result
        return cached

    result = {}
    now = time.monotonic()

    # Cold cache delay — prevents instant burst on Cloud wake-up
    if not _ticker_cache:
        time.sleep(2)

    # Serve cached tickers that are still fresh
    fresh = [
        s for s in tickers
        if s in _ticker_cache
        and (now - _ticker_cache_time.get(s, 0)) < _TICKER_CACHE_TTL
    ]
    to_fetch = [s for s in tickers if s not in fresh]
    for s in fresh:
        result[s] = _ticker_cache[s]
    _cache_stats["hits"]   += len(fresh)
    _cache_stats["misses"] += len(to_fetch)

    if not to_fetch:
        return result

    CHUNK = 3
    chunks = [to_fetch[i:i + CHUNK] for i in range(0, len(to_fetch), CHUNK)]
    _any_429 = False

    for i, chunk in enumerate(chunks):
        # v5.27 — Gate 2: re-check cooldown before each chunk
        # (may have been set by a parallel fragment thread between chunks)
        if _is_rate_limited():
            break

        if i > 0:
            time.sleep(5)   # 5s inter-chunk gap — AWS IP recovery window

        _global_throttle()
        try:
            _t0 = time.perf_counter()
            raw = yf.download(
                chunk, period=period, interval=interval,
                auto_adjust=True, progress=False, group_by="ticker",
            )
            _ms = (time.perf_counter() - _t0) * 1000
            _fetch_latency_ms.append(_ms)
            if len(_fetch_latency_ms) > 20:
                _fetch_latency_ms.pop(0)
            chunk_result = _parse_batch_raw(raw, chunk)
            result.update(chunk_result)
            for sym, df in chunk_result.items():
                _ticker_cache[sym] = df
                _ticker_cache_time[sym] = time.monotonic()

        except Exception as exc:
            if type(exc).__name__ == "YFRateLimitError":
                _any_429 = True
                _set_rate_limited()                   # v5.27 — engage global cooldown
                for sym in chunk:                     # serve stale cache for this chunk
                    _fetch_errors[sym] = _fetch_errors.get(sym, 0) + 1
                    if sym in _ticker_cache and sym not in result:
                        result[sym] = _ticker_cache[sym]
                break                                 # abort remaining chunks

    # v5.27 — Reset backoff counter only on fully clean batch
    if not _any_429 and to_fetch:
        _clear_rate_limit_state()

    # Final fallback: stale cache for anything still missing
    for sym in tickers:
        if sym not in result and sym in _ticker_cache:
            result[sym] = _ticker_cache[sym]

    if not result and _is_rate_limited():
        raise RuntimeError("rate_limited_no_cache")
    return result


# ── DataFrame normaliser ───────────────────────────────────────────────────────
def _normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Guarantee df always has string columns: Open High Low Close Volume.
    Handles every yfinance output shape:
      MultiIndex  : ('Close','AAPL') → 'Close'
      RangeIndex  : 0,1,2,3,4 → mapped to OHLCV order
      Duplicate   : two 'Close' cols → keep first, drop rest
      Alt names   : 'Adj Close' → renamed to 'Close'
      Mixed case  : 'close' → 'Close'
    """
    if df is None or df.empty:
        return df
    # Step 1: Flatten MultiIndex
    # yfinance 0.2.54+ changed single-ticker download column order:
    # Old: level 0 = price type (Close/High/...), level 1 = ticker
    # New: level 0 = ticker (GC=F/AAPL/...), level 1 = price type
    # Detect which level contains OHLCV names and use that level.
    if isinstance(df.columns, pd.MultiIndex):
        _price_names = {"open", "high", "low", "close", "volume",
                        "adj close", "adj open", "adj high", "adj low"}
        _l0 = [str(v).lower() for v in df.columns.get_level_values(0)]
        _l1 = [str(v).lower() for v in df.columns.get_level_values(1)]
        if any(v in _price_names for v in _l1) and not any(v in _price_names for v in _l0):
            # New format: ticker in level 0, price types in level 1
            df.columns = df.columns.get_level_values(1)
        else:
            # Old format: price types in level 0
            df.columns = df.columns.get_level_values(0)
    # Step 2: Numeric RangeIndex → map to OHLCV
    if pd.api.types.is_integer_dtype(df.columns) or isinstance(df.columns, pd.RangeIndex):
        standard = ["Open", "High", "Low", "Close", "Volume"]
        cols = list(df.columns)
        df.columns = [standard[i] if i < len(standard) else f"col_{i}"
                      for i in range(len(cols))]
    # Step 3: Normalise alternative column names
    rename = {}
    for col in df.columns:
        cs = str(col)
        if cs.lower() in ("adj close", "adj_close"):
            rename[col] = "Close"
        elif cs.lower() in ("open", "high", "low", "close", "volume") and cs != cs.capitalize():
            rename[col] = cs.capitalize()
    if rename:
        df = df.rename(columns=rename)
    # Step 4: Drop duplicate columns — keep first
    df = df.loc[:, ~df.columns.duplicated()]
    # Step 5: Ensure each OHLCV column is a Series (not a DataFrame slice)
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in df.columns and isinstance(df[col], pd.DataFrame):
            df[col] = df[col].iloc[:, 0]
    return df


# ── _safe_close — shared helper ───────────────────────────────────────────────
def _safe_close(df: pd.DataFrame) -> pd.Series:
    """Return clean float Series from Close; guards MultiIndex yfinance output."""
    if df is None or df.empty:
        return pd.Series(dtype=float)
    try:
        cl = df["Close"]
        if isinstance(cl, pd.DataFrame):
            cl = cl.iloc[:, 0]
        return cl.dropna().astype(float)
    except Exception:
        return pd.Series(dtype=float)


# ── Public API ─────────────────────────────────────────────────────────────────

@st.cache_data(ttl=5, show_spinner=False)
def get_live_price(ticker: str, cache_buster: int = 0) -> dict:
    """
    Fetch the latest intraday price for a live market session.
    Returns dict with: price, prev_close, change_pct, volume, high, low, timestamp.
    Uses period='2d' interval='1m' — gives enough data for today's OHLC + prev close.
    TTL=5s — self-expires every 5 seconds. cache_buster allows forced refresh.
    Returns empty dict on any failure — callers must handle gracefully.
    """
    _global_throttle()
    try:
        df = _yf_download(ticker, period="2d", interval="1m",
                         auto_adjust=True, progress=False)
        if df is None or df.empty:
            return {}
        df = _normalize_df(df)
        if df.empty:
            return {}
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)

        cl    = _safe_close(df)
        if cl.empty:
            return {}

        # Split today vs yesterday by date
        import pytz
        last_ts   = df.index[-1]
        today_str = last_ts.date()
        today_df  = df[df.index.date == today_str]
        prev_df   = df[df.index.date < today_str]

        if len(cl) == 0:
            return None
        price     = float(cl.iloc[-1])
        prev_close = float(_safe_close(prev_df).iloc[-1]) if not prev_df.empty else price
        chg_pct   = (price - prev_close) / prev_close * 100 if prev_close else 0.0

        day_high  = float(today_df["High"].max())  if not today_df.empty and "High"   in today_df.columns else price
        day_low   = float(today_df["Low"].min())   if not today_df.empty and "Low"    in today_df.columns else price
        volume    = float(today_df["Volume"].sum()) if not today_df.empty and "Volume" in today_df.columns else 0.0

        return {
            "price":      round(price, 2),
            "prev_close": round(prev_close, 2),
            "change_pct": round(chg_pct, 2),
            "day_high":   round(day_high, 2),
            "day_low":    round(day_low, 2),
            "volume":     volume,
            "timestamp":  str(last_ts),
        }
    except Exception as e:
        log_error(f"get_live_price:{ticker}", e)
        return {}


@st.cache_data(ttl=60, show_spinner=False)
def get_intraday_chart_data(ticker: str, cache_buster: int = 0) -> pd.DataFrame:
    """
    Fetch today's 1-minute OHLCV bars for the intraday chart.
    TTL=60s — refreshes once per minute inside the chart fragment.
    Returns empty DataFrame on failure.
    """
    _global_throttle()
    try:
        df = _yf_download(ticker, period="1d", interval="1m",
                         auto_adjust=True, progress=False)
        if df is None or df.empty:
            return pd.DataFrame()
        df = _normalize_df(df)
        if df.empty:
            return pd.DataFrame()
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        return df
    except Exception as e:
        log_error(f"get_intraday_chart_data:{ticker}", e)
        return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def get_price_data(ticker: str, period: str = "1y", interval: str = "1d",
                   cache_buster: int = 0) -> pd.DataFrame:
    """
    Fetch OHLCV data for a ticker.
    cache_buster: pass st.session_state.cb to force cache invalidation on
    user-triggered refresh. Default 0 = rely on TTL (300 s).
    """
    _global_throttle()
    try:
        df = _yf_download(ticker, period=period, interval=interval,
                         auto_adjust=True, progress=False)
        if df.empty:
            return pd.DataFrame()
        df = _normalize_df(df)
        if df.empty:
            return pd.DataFrame()
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        return df
    except Exception as e:
        log_error(f"get_price_data:{ticker}", e)
        return pd.DataFrame()


@st.cache_data(ttl=600, show_spinner=False)
def get_ticker_info(ticker: str, cache_buster: int = 0) -> dict:
    """
    Fetch metadata/fundamentals for a ticker.
    cache_buster: same semantics as get_price_data.
    Returns {} on any failure — callers must handle missing keys gracefully.
    Note: yfinance raises TypeError internally for some futures tickers (CL=F,
    GC=F etc.) — this is a known upstream issue, handled silently here.
    """
    if _is_rate_limited():                         # v5.29 — abort during cooldown
        return {}
    _global_throttle()
    try:
        result = yf.Ticker(ticker).info
        return result if isinstance(result, dict) else {}
    except TypeError:
        # Known yfinance issue with futures/commodity tickers — not our bug.
        # Return empty dict; _detect_asset_class will fall back to ticker suffix.
        return {}
    except Exception as e:
        log_error(f"get_ticker_info:{ticker}", e)
        return {}


@st.cache_data(ttl=300, show_spinner=False)
def get_top_movers(symbols: list, max_symbols: int = 20,
                   cache_buster: int = 0) -> list:
    """
    Return top movers sorted by absolute % change.
    Uses _yf_batch_download — ONE Yahoo Finance request for all tickers,
    dramatically reducing rate limit exposure vs the old per-ticker loop.
    """
    syms = list(symbols[:max_symbols])
    if not syms:
        return []
    # One batch call instead of N sequential calls
    batch = _yf_batch_download(syms, period="5d", interval="1d")
    results = []
    for sym in syms:
        df = batch.get(sym)
        if df is None or df.empty or len(df) < 2:
            continue
        try:
            cl  = _safe_close(df)
            lp  = float(cl.iloc[-1]) if len(cl) >= 1 else 0
            pp  = float(cl.iloc[-2]) if len(cl) >= 2 else lp
            chg = (lp - pp) / pp * 100 if pp else 0.0
            results.append((sym, round(chg, 2), round(lp, 2)))
        except Exception as e:
            log_error(f"get_top_movers:{sym}", e)
    results.sort(key=lambda x: abs(x[1]), reverse=True)
    return results


@st.cache_data(ttl=60, show_spinner=False)   # v5.27: was ttl=10 — 10s caused 429 death spiral on AWS IPs
def get_ticker_bar_data_fresh(tickers: tuple) -> dict:
    """
    Ticker bar batch fetch. TTL=60s (v5.27: raised from 10s).
    The original 10s TTL was designed for rapid retry after a transient 429,
    but on Streamlit Cloud's AWS IPs, 429s are sustained — every 10s re-fire
    re-triggered the rate limiter rather than recovering from it.
    The global _is_rate_limited() gate now handles rapid-retry logic instead.
    """
    return _yf_batch_download(list(tickers), period="5d", interval="1d")


@st.cache_data(ttl=300, show_spinner=False)
def get_batch_data(tickers: tuple, period: str = "5d",
                   interval: str = "1d", cache_buster: int = 0) -> dict:
    """
    Unified cached batch fetch — replaces get_ticker_bar_data + get_group_data.
    tickers MUST be a tuple (not list) — @st.cache_data requires hashable args.

    Usage:
      Ticker bar:   get_batch_data(tuple(syms), period="5d",  cache_buster=0)
      Group data:   get_batch_data(tuple(syms), period="3mo", cache_buster=cb)
      Global sig:   get_batch_data(tuple(syms), period="3mo", cache_buster=0)

    cache_buster=0 means TTL-only refresh (never busted by stock selection).
    Pass cb only when an explicit Refresh should force a new fetch.
    Returns {sym: DataFrame} mapping.

    IMPORTANT: raises RuntimeError on total failure so @st.cache_data does NOT
    cache the empty result. This forces a retry on the next call rather than
    serving a stale empty dict for the full 300s TTL.
    Callers must use safe_run() or try/except and default to {}.
    """
    result = _yf_batch_download(list(tickers), period=period, interval=interval)
    # Return result as-is. Empty dict on failure is handled by callers via the
    # module-level _ticker_cache fallback. @st.cache_data will store {} briefly
    # but _ticker_cache provides recovery on next successful fetch.
    return result


@st.cache_data(ttl=600, show_spinner=False)
def get_news(feeds: list, max_n: int = 8,
             cache_buster: int = 0) -> list:
    """
    Fetch RSS news articles from the allowlisted feeds.
    cache_buster: pass cb for refresh-button consistency.
    """
    articles = []
    for url in feeds:
        if not _is_allowed_rss(url):
            log_error("get_news:blocked_url",
                      ValueError(f"Not in allowlist: {url[:60]}"))
            continue
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:max_n]:
                articles.append({
                    "title":   (e.get("title",   "") or "")[:120],
                    "link":    (e.get("link",    "#") or "#"),
                    "source":  (feed.feed.get("title", "") or "")[:30],
                    "summary": (e.get("summary", "") or "")[:200],
                    "date":    (e.get("published", "") or "")[:16],
                })
            if len(articles) >= max_n * 2:
                break
        except Exception as ex:
            log_error(f"get_news:{url[:40]}", ex)
    return articles[:max_n]


# ── Observability getters (v5.34) ─────────────────────────────────────────────

def get_health_stats() -> dict:
    """
    Return cache and fetch health metrics for the observability dashboard.
    No yfinance calls — reads module-level counters only.
    """
    hits   = _cache_stats["hits"]
    misses = _cache_stats["misses"]
    total  = hits + misses
    hit_rate = round(hits / total * 100, 1) if total else 0.0
    samples  = list(_fetch_latency_ms)
    avg_ms   = round(sum(samples) / len(samples), 1) if samples else 0.0
    p95_ms   = round(sorted(samples)[int(len(samples) * 0.95)], 1) if len(samples) >= 2 else avg_ms
    return {
        "cache_hits":      hits,
        "cache_misses":    misses,
        "hit_rate_pct":    hit_rate,
        "avg_fetch_ms":    avg_ms,
        "p95_fetch_ms":    p95_ms,
        "latency_samples": samples,
        "error_counts":    dict(_fetch_errors),
        "total_errors":    sum(_fetch_errors.values()),
        "cache_size":      len(_ticker_cache),
    }


def get_rate_limit_state() -> dict:
    """
    Return rate-limit gate state for the observability dashboard.
    No yfinance calls — reads module-level state only.
    """
    now          = time.monotonic()
    in_cooldown  = _rl_cooldown_until > now
    secs_left    = max(0.0, round(_rl_cooldown_until - now, 1)) if in_cooldown else 0.0
    return {
        "in_cooldown":       in_cooldown,
        "seconds_remaining": secs_left,
        "consecutive_429s":  _rl_hit_count[0],
    }
