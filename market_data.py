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
import streamlit as st
from urllib.parse import urlparse
from utils import safe_run, log_error, safe_url

# ── RSS allowlist ─────────────────────────────────────────────────────────────
_ALLOWED_RSS_DOMAINS = {
    "feeds.feedburner.com", "feeds.reuters.com",
    "timesofindia.indiatimes.com", "economictimes.indiatimes.com",
    "aljazeera.com", "techcrunch.com", "finance.yahoo.com",
    "bbci.co.uk", "bbc.co.uk", "bbc.com",
    "artificialintelligence-news.com", "ndtvprofit.com",
    "moneycontrol.com", "livemint.com", "businessstandard.com",
    "thehindubusinessline.com", "financialexpress.com",
}

def _is_allowed_rss(url: str) -> bool:
    if not safe_url(url):
        return False
    try:
        host = urlparse(url).netloc.lower().lstrip("www.")
        return any(host == d or host.endswith("." + d) for d in _ALLOWED_RSS_DOMAINS)
    except Exception:
        return False

# ── Global token-bucket rate limiter ────────────────────────────────────────
# Yahoo Finance allows ~5 requests per 5 seconds before triggering limits.
# This single global lock ensures all download calls across the app
# (ticker bar, top movers, week summary) share one rate budget.
import threading as _threading
_RATE_LOCK   = _threading.Lock()
_MIN_INTERVAL = 1.5   # minimum seconds between any two yfinance calls globally
_last_yf_call = [0.0]  # mutable list so inner functions can mutate it

def _global_throttle():
    """Block until at least _MIN_INTERVAL has elapsed since last yfinance call."""
    with _RATE_LOCK:
        now  = time.monotonic()
        wait = _MIN_INTERVAL - (now - _last_yf_call[0])
        if wait > 0:
            time.sleep(wait)
        _last_yf_call[0] = time.monotonic()


# ── Single-ticker download with retry ────────────────────────────────────────
def _yf_download(ticker: str, **kwargs) -> pd.DataFrame:
    """
    Calls yf.download() (not itself) with exponential backoff on rate limits.
    Max 3 attempts: waits 2s then 4s before returning empty DataFrame.
    """
    for attempt in range(3):
        _global_throttle()
        try:
            df = yf.download(ticker, **kwargs)   # NOTE: yf.download, not _yf_download
            return df if df is not None else pd.DataFrame()
        except Exception as exc:
            if type(exc).__name__ == "YFRateLimitError":
                if attempt < 2:
                    time.sleep(2 ** (attempt + 1))  # 2s, 4s
                    continue
            return pd.DataFrame()
    return pd.DataFrame()


# ── Multi-ticker batch download ───────────────────────────────────────────────
def _yf_batch_download(tickers: list, period: str = "5d",
                       interval: str = "1d") -> dict:
    """
    Fetch multiple tickers in ONE yf.download() call.
    Returns {ticker: DataFrame} mapping. Empty dict on failure.
    Yahoo Finance handles up to ~50 tickers per batch without rate issues.
    """
    if not tickers:
        return {}
    _global_throttle()
    try:
        raw = yf.download(
            tickers, period=period, interval=interval,
            auto_adjust=True, progress=False, group_by="ticker",
        )
        if raw is None or raw.empty:
            return {}
        result = {}
        if len(tickers) == 1:
            # Single ticker — yf returns flat DataFrame, not grouped
            df = _normalize_df(raw.copy())
            if not df.empty:
                df.index = pd.to_datetime(df.index)
                df.sort_index(inplace=True)
                result[tickers[0]] = df
        else:
            for sym in tickers:
                try:
                    df = raw[sym].copy() if sym in raw.columns.get_level_values(1) else pd.DataFrame()
                    if isinstance(df, pd.DataFrame) and not df.empty:
                        df = _normalize_df(df)
                        df.index = pd.to_datetime(df.index)
                        df.sort_index(inplace=True)
                        result[sym] = df
                except Exception:
                    pass
        return result
    except Exception as exc:
        if type(exc).__name__ == "YFRateLimitError":
            time.sleep(5)
        return {}


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
    if isinstance(df.columns, pd.MultiIndex):
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
    _throttle(ticker)
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
    _throttle(ticker)
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
    _throttle(ticker)
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
    _throttle(ticker)
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
