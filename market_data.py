# market_data.py
import time
import feedparser
import pandas as pd
import yfinance as yf
import streamlit as st
from urllib.parse import urlparse
from utils import safe_run, log_error, safe_url

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

_last_call: dict = {}
_MIN_INTERVAL = 1.2


def _normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Guarantee df always has string columns: Open High Low Close Volume.
    Handles every yfinance output shape:
      - MultiIndex  : ('Close','AAPL') → 'Close'
      - RangeIndex  : 0,1,2,3,4       → mapped to OHLCV order
      - Duplicate   : two 'Close' cols → keep first, drop rest
      - Alt names   : 'Adj Close'      → renamed to 'Close'
      - Mixed case  : 'close'          → 'Close'
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
        df.columns = [standard[i] if i < len(standard) else f"col_{i}" for i in range(len(cols))]

    # Step 3: Normalise known alternative names
    rename = {}
    for col in df.columns:
        col_str = str(col)
        if col_str.lower() == "adj close" or col_str == "Adj Close":
            rename[col] = "Close"
        elif col_str.lower() in ("open","high","low","close","volume") and col_str != col_str.capitalize():
            rename[col] = col_str.capitalize()
    if rename:
        df = df.rename(columns=rename)

    # Step 4: Drop duplicate columns — keep first occurrence
    df = df.loc[:, ~df.columns.duplicated()]

    # Step 5: Ensure Close is a Series (not a DataFrame from duplicate flattening)
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in df.columns and isinstance(df[col], pd.DataFrame):
            df[col] = df[col].iloc[:, 0]

    return df


def _throttle(sym: str):
    now = time.monotonic()
    wait = _MIN_INTERVAL - (now - _last_call.get(sym, 0))
    if wait > 0:
        time.sleep(wait)
    _last_call[sym] = time.monotonic()


@st.cache_data(ttl=300, show_spinner=False)
def get_price_data(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
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
def get_ticker_info(ticker: str) -> dict:
    _throttle(ticker)
    try:
        return yf.Ticker(ticker).info or {}
    except Exception as e:
        log_error(f"get_ticker_info:{ticker}", e)
        return {}



def _safe_close(df):
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

@st.cache_data(ttl=300, show_spinner=False)
def get_top_movers(symbols: list, max_symbols: int = 20) -> list:
    results = []
    for sym in symbols[:max_symbols]:
        df = get_price_data(sym, period="5d", interval="1d")
        if df is None or df.empty or len(df) < 2:
            continue
        try:
            _cl = _safe_close(df)
            lp  = float(_cl.iloc[-1]) if len(_cl) >= 1 else 0
            pp  = float(_cl.iloc[-2]) if len(_cl) >= 2 else lp
            chg = (lp - pp) / pp * 100 if pp else 0.0
            results.append((sym, round(chg, 2), round(lp, 2)))
        except Exception as e:
            log_error(f"get_top_movers:{sym}", e)
    results.sort(key=lambda x: abs(x[1]), reverse=True)
    return results


@st.cache_data(ttl=600, show_spinner=False)
def get_news(feeds: list, max_n: int = 8) -> list:
    articles = []
    for url in feeds:
        if not _is_allowed_rss(url):
            log_error("get_news:blocked_url", ValueError(f"Not in allowlist: {url[:60]}"))
            continue
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:max_n]:
                articles.append({
                    "title":   (e.get("title",   "") or "")[:120],
                    "link":    (e.get("link",    "#") or "#"),
                    "source":  (feed.feed.get("title", "") or "")[:30],
                    "summary": (e.get("summary", "") or "")[:200],
                    "date":    (e.get("published","") or "")[:16],
                })
            if len(articles) >= max_n * 2:
                break
        except Exception as ex:
            log_error(f"get_news:{url[:40]}", ex)
    return articles[:max_n]
