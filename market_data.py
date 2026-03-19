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

# ── Rate throttle — prevents hammering yfinance ────────────────────────────────
_last_call: dict = {}
_MIN_INTERVAL = 1.2

def _throttle(sym: str):
    now  = time.monotonic()
    wait = _MIN_INTERVAL - (now - _last_call.get(sym, 0))
    if wait > 0:
        time.sleep(wait)
    _last_call[sym] = time.monotonic()


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
        df = yf.download(ticker, period=period, interval=interval,
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
    """
    _throttle(ticker)
    try:
        return yf.Ticker(ticker).info or {}
    except Exception as e:
        log_error(f"get_ticker_info:{ticker}", e)
        return {}


@st.cache_data(ttl=300, show_spinner=False)
def get_top_movers(symbols: list, max_symbols: int = 20,
                   cache_buster: int = 0) -> list:
    """
    Return top movers sorted by absolute % change.
    cache_buster: pass cb so the homepage refresh button busts this cache too.
    """
    results = []
    for sym in symbols[:max_symbols]:
        df = get_price_data(sym, period="5d", interval="1d",
                            cache_buster=cache_buster)
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
