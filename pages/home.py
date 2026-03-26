# pages/home.py — v5.24 Global Overview redesign
# Depends on: config, utils, market_data, indicators
# Entry points: render_ticker_bar() — called from app.py before sidebar
#               render_homepage()   — called from app.py routing
#
# LAZY LOADING TIER STRUCTURE:
#   Tier 1 (immediate, 0 extra fetches):
#     render_ticker_bar()              → get_batch_data(10 tickers, 5d)
#     _render_morning_brief()          → no fetch
#     _render_market_status_row()      → no fetch
#     _render_global_overview_prices() → 100% cache hit from ticker bar
#   Tier 2 (deferred @st.fragment, fires after Tier 1 renders):
#     _render_global_signals()         → get_batch_data(10 tickers, 1mo)
#     _render_top_movers()             → get_top_movers(20 tickers)
#     _render_news_feed()              → RSS only, no YF
#
# REMOVED (M1): render_week_summary() call — was firing 8 sections on Home load
# REMOVED (M1): _render_version_log() — not useful on landing page
# CHANGED (M1): get_ticker_bar_data → get_batch_data (M0 consolidation)

import pytz
import pandas as pd
import streamlit as st
import streamlit.components.v1 as _st_components
from datetime import datetime, timedelta
from config import MARKET_SESSIONS, CURRENT_VERSION
from utils import sanitise, safe_run, responsive_cols, log_error
from market_data import (get_price_data, get_top_movers, get_news,
                         get_batch_data, get_ticker_bar_data_fresh,
                         is_ticker_cache_warm, _ticker_cache)
from indicators import compute_indicators, signal_score


# ══════════════════════════════════════════════════════════════════
# TICKER SYMBOLS — shared by ticker bar AND Global Overview
# ══════════════════════════════════════════════════════════════════

TICKER_SYMBOLS = [
    ("Nifty 50",   "^NSEI"),
    ("Sensex",     "^BSESN"),
    ("Bank Nifty", "^NSEBANK"),
    ("S&P 500",    "^GSPC"),
    ("Nasdaq",     "^NDX"),
    ("Dow Jones",  "^DJI"),
    ("Hang Seng",  "^HSI"),
    ("Gold",       "GC=F"),
    ("Crude WTI",  "CL=F"),
    ("USD/INR",    "USDINR=X"),
]

_TICKER_SYMS = tuple(sym for _, sym in TICKER_SYMBOLS)

# Asset class — suppresses BUY/SELL on FX and commodities in signal cards
_ASSET_CLASS = {
    "^NSEI": "equity", "^BSESN": "equity", "^NSEBANK": "equity",
    "^GSPC": "equity", "^NDX":   "equity", "^DJI":    "equity",
    "^HSI":  "equity",
    "GC=F":  "commodity", "CL=F": "commodity",
    "USDINR=X": "fx",
}


# ══════════════════════════════════════════════════════════════════
# GLOBAL TICKER BAR — fixed to top of every page
# ══════════════════════════════════════════════════════════════════

def render_ticker_bar(cb: int = 0):
    """
    Fixed 36px ticker strip via window.parent iframe injection.
    get_batch_data cache_buster=0 — never busted by stock selection.
    """
    import streamlit.components.v1 as _components

    st.markdown("""<style>
header[data-testid="stHeader"]{height:0!important;min-height:0!important;
    padding:0!important;overflow:hidden!important;visibility:hidden!important;}
.stAppToolbar,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;}
[data-testid="stAppViewContainer"]>section[data-testid="stMain"]{padding-top:36px!important;}
.main .block-container{padding-top:50px!important;}
[data-testid="stSidebar"]>div:first-child{padding-top:36px!important;margin-top:0!important;}
</style>""", unsafe_allow_html=True)

    # Try fresh fetch first (10s TTL — retries quickly after rate limits clear)
    # Fall back to module-level _ticker_cache so the bar shows last known data
    # during cold-start rate-limit windows rather than "GSI Loading..." indefinitely
    _batch = safe_run(
        lambda: get_ticker_bar_data_fresh(_TICKER_SYMS),
        context="ticker_bar:batch", default={},
    ) or {}
    if not _batch:
        _batch = {sym: _ticker_cache[sym] for sym in _TICKER_SYMS
                  if sym in _ticker_cache}

    items = []
    for name, sym in TICKER_SYMBOLS:
        df = _batch.get(sym)
        if df is not None and not df.empty and len(df) >= 2 and "Close" in df.columns:
            _cl = df["Close"]
            _cl = _cl.iloc[:, 0] if isinstance(_cl, pd.DataFrame) else _cl
            _cl = _cl.dropna().astype(float)
            if len(_cl) < 2:
                continue
            lp    = float(_cl.iloc[-1])
            pp    = float(_cl.iloc[-2])
            chg   = (lp - pp) / pp * 100 if pp else 0
            color = "#00c853" if chg >= 0 else "#ff1744"
            arrow = "▲" if chg >= 0 else "▼"
            price_str = f"{lp:,.0f}" if lp >= 1000 else f"{lp:,.2f}" if lp >= 1 else f"{lp:.4f}"
            items.append(
                f'<span class="tick-item">'
                f'<span class="tick-name">{name}</span> '
                f'<span class="tick-price">{price_str}</span> '
                f'<span class="tick-chg" style="color:{color}">{arrow}{abs(chg):.2f}%</span>'
                f'</span><span class="tick-sep">·</span>'
            )

    if not items:
        placeholder = (
            '<span class="tick-item">'
            '<span class="tick-name">GSI</span> '
            '<span class="tick-price">Loading…</span>'
            '</span><span class="tick-sep">·</span>'
        ) * 12
        ticker_content = placeholder
    else:
        ticker_content = " ".join(items * 3)

    _components.html(f"""
<script>
(function() {{
    var TICKER_ID = 'gsi-ticker-bar';
    var parent = window.parent;
    if (!parent) return;
    try {{
        var old = parent.document.getElementById(TICKER_ID);
        if (old && old.parentNode) old.parentNode.removeChild(old);
    }} catch(e) {{}}
    if (!parent.document.getElementById('gsi-ticker-css')) {{
        var s = parent.document.createElement('style');
        s.id = 'gsi-ticker-css';
        s.textContent = `
            #gsi-ticker-bar {{
                position: fixed; top: 0; left: 0;
                width: 100vw; height: 36px; z-index: 2147483647;
                background: linear-gradient(90deg,#070c1a 0%,#0a1020 100%);
                border-bottom: 1px solid #1a2540;
                overflow: hidden; display: flex; align-items: center;
                box-shadow: 0 2px 12px rgba(0,0,0,.5);
            }}
            #gsi-ticker-bar .ticker-track {{
                display: flex; align-items: center; white-space: nowrap;
                animation: gsiScroll 60s linear infinite; will-change: transform;
            }}
            #gsi-ticker-bar:hover .ticker-track {{ animation-play-state: paused; }}
            @keyframes gsiScroll {{
                0%   {{ transform: translateX(0); }}
                100% {{ transform: translateX(-33.33%); }}
            }}
            #gsi-ticker-bar .tick-item {{
                display: inline-flex; align-items: center; gap: 5px;
                padding: 0 12px; font-size: .71rem;
                font-family: "JetBrains Mono","Fira Code",ui-monospace,monospace;
            }}
            #gsi-ticker-bar .tick-name  {{ color:#4b6080; font-weight:600; }}
            #gsi-ticker-bar .tick-price {{ color:#c8d6f0; font-weight:700; }}
            #gsi-ticker-bar .tick-chg   {{ font-weight:700; }}
            #gsi-ticker-bar .tick-sep   {{ color:#1f2d40; padding:0 3px; font-size:.8rem; }}
        `;
        parent.document.head.appendChild(s);
    }}
    var div = parent.document.createElement('div');
    div.id = TICKER_ID;
    div.innerHTML = '<div class="ticker-track">{ticker_content}</div>';
    parent.document.body.prepend(div);
}})();
</script>
""", height=1, scrolling=False)


# ══════════════════════════════════════════════════════════════════
# MARKET STATUS (no fetch)
# ══════════════════════════════════════════════════════════════════

def _market_status(country: str) -> tuple:
    sess = MARKET_SESSIONS.get(country, {})
    tz   = pytz.timezone(sess.get("tz", "UTC"))
    now  = datetime.now(tz)
    oh, om = sess.get("open",  (9, 0))
    ch, cm = sess.get("close", (17, 0))
    is_open = (now.weekday() < 5 and
               (oh, om) <= (now.hour, now.minute) < (ch, cm))
    return (
        f"{'🟢 OPEN' if is_open else '🔴 CLOSED'} {now.strftime('%H:%M')} {now.strftime('%a')}",
        "#00c853" if is_open else "#ff1744",
        is_open,
    )


def _next_open(country: str) -> str:
    sess = MARKET_SESSIONS.get(country, {})
    tz   = pytz.timezone(sess.get("tz", "UTC"))
    now  = datetime.now(tz)
    oh, om = sess.get("open", (9, 0))
    for d in range(1, 8):
        nxt = now + timedelta(days=d)
        if nxt.weekday() < 5:
            return nxt.strftime(f"%a %d %b — {oh:02d}:{om:02d}")
    return "—"


def _render_market_status_row():
    st.markdown('<p class="section-title">🌐 Global Market Status</p>',
                unsafe_allow_html=True)
    markets = ["India", "USA", "Europe", "China", "Commodities", "ETFs - Global"]
    cols = responsive_cols(len(markets))
    for col, mkt in zip(cols, markets):
        label, color, is_open = _market_status(mkt)
        sub = "" if is_open else f"Opens {_next_open(mkt)}"
        col.markdown(
            f'<div class="kpi-card" style="border-left-color:{color}">'
            f'<div class="kpi-label">{mkt}</div>'
            f'<div class="kpi-delta" style="color:{color};font-weight:700">{label}</div>'
            f'{"<div class=kpi-help>" + sub + "</div>" if sub else ""}'
            f'</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════
# MORNING BRIEF (no fetch)
# ══════════════════════════════════════════════════════════════════

def _render_morning_brief():
    now_ist = datetime.now(pytz.timezone("Asia/Kolkata"))
    h = now_ist.hour
    if   h < 6:  msg = "Pre-dawn. Asian futures setting early direction for the day."
    elif h < 9:  msg = "Pre-market. Watch SGX Nifty and Dow futures for opening clues."
    elif h < 10: msg = "Opening bell. First 30-minute range often defines the day's bias."
    elif h < 12: msg = "Morning session. Institutional flow peaks before noon — watch block deals."
    elif h < 14: msg = "Midday consolidation. Volume tapers — breakouts here often extend into close."
    elif h < 15: msg = "Final 90 minutes. FII/DII data and closing auction drive last moves."
    elif h < 16: msg = "Post-market. Review today's data, set alerts, plan tomorrow's watchlist."
    else:        msg = "Market closed. Global cues — US markets, Asian overnight, F&O data — matter now."
    st.markdown(
        f'<div class="insight-box">'
        f'<span style="font-size:0.78rem;color:#6b7a90">'
        f'{now_ist.strftime("%A, %d %B %Y")} · {now_ist.strftime("%H:%M")} IST</span><br>'
        f'<span style="font-size:0.88rem;color:#c8d6f0">{msg}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════
# GLOBAL PRICE SNAPSHOT (Tier 1 — 0 extra fetches, cache hit)
# ══════════════════════════════════════════════════════════════════

def _render_global_overview_prices(batch_5d: dict):
    """
    Price + daily % + 5-day weekly % cards for all ticker bar instruments.
    batch_5d is passed in from the same get_batch_data(5d) call already made
    by render_ticker_bar — guaranteed cache hit, zero additional API calls.
    """
    st.markdown('<p class="section-title">📊 Global Snapshot</p>',
                unsafe_allow_html=True)
    cols = responsive_cols(5)
    col_idx = 0
    for name, sym in TICKER_SYMBOLS:
        col = cols[col_idx % 5]
        col_idx += 1
        df = batch_5d.get(sym)
        if df is None or df.empty or len(df) < 2 or "Close" not in df.columns:
            col.markdown(
                f'<div class="kpi-card">'
                f'<div class="kpi-label">{name}</div>'
                f'<div class="kpi-value" style="font-size:0.9rem;color:#4b6080">—</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            continue
        _cl = df["Close"]
        _cl = _cl.iloc[:, 0] if isinstance(_cl, pd.DataFrame) else _cl
        _cl = _cl.dropna().astype(float)
        if len(_cl) < 2:
            continue
        lp        = float(_cl.iloc[-1])
        pp        = float(_cl.iloc[-2])
        chg       = (lp - pp) / pp * 100 if pp else 0
        week_chg  = (lp - float(_cl.iloc[0])) / float(_cl.iloc[0]) * 100 if float(_cl.iloc[0]) else 0
        color     = "#00c853" if chg >= 0 else "#ff1744"
        arrow     = "▲" if chg >= 0 else "▼"
        price_str = f"{lp:,.0f}" if lp >= 1000 else f"{lp:,.2f}" if lp >= 1 else f"{lp:.4f}"
        week_str  = f"+{week_chg:.1f}" if week_chg >= 0 else f"{week_chg:.1f}"
        col.markdown(
            f'<div class="kpi-card" style="border-left-color:{color}">'
            f'<div class="kpi-label">{name}</div>'
            f'<div class="kpi-value" style="font-size:1.05rem">{price_str}</div>'
            f'<div class="kpi-delta" style="color:{color}">{arrow} {abs(chg):.2f}% today</div>'
            f'<div class="kpi-help">5d: {week_str}%</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════
# GLOBAL TREND SIGNALS — @st.fragment (Tier 2, deferred)
# ══════════════════════════════════════════════════════════════════

@st.fragment(run_every=60)
def _render_global_signals():
    """
    BUY/WATCH/AVOID + RSI for each global instrument.
    Fetches 1mo data (separate cache from 5d ticker bar batch).
    Cold-start guard: checks _ticker_cache warmth before firing 1mo batch.
    If 5d data not yet available, shows placeholder and returns — prevents
    concurrent burst with ticker bar that triggers YF rate limits.
    Signals appear on the next Streamlit re-render once cache is warm.
    """
    # Guard: only fetch 1mo data after ticker bar has warmed the 5d cache
    if not is_ticker_cache_warm(_TICKER_SYMS):
        st.caption("⏳ Signals load after price data is ready…")
        return

    batch_1mo = safe_run(
        lambda: get_batch_data(_TICKER_SYMS, period="1mo", cache_buster=0),
        context="global_signals:batch", default={},
    ) or {}

    if not batch_1mo:
        st.caption("Computing signals…")
        return

    st.markdown('<p class="section-title">🧭 Global Trend Signals</p>',
                unsafe_allow_html=True)
    st.caption("Index signals based on RSI + momentum · Not equivalent to full stock analysis")

    cols = responsive_cols(5)
    col_idx = 0
    for name, sym in TICKER_SYMBOLS:
        col = cols[col_idx % 5]
        col_idx += 1
        df = batch_1mo.get(sym)
        if df is None or df.empty or len(df) < 10 or "Close" not in df.columns:
            col.markdown(
                f'<div class="kpi-card">'
                f'<div class="kpi-label">{name}</div>'
                f'<div class="kpi-value" style="font-size:0.85rem;color:#4b6080">—</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            continue

        inds = safe_run(
            lambda d=df: compute_indicators(d),
            context=f"global_signals:ind:{sym}", default=None,
        )
        if inds is None:
            continue

        sig      = safe_run(lambda i=inds: signal_score(i, {}),
                            context=f"global_signals:score:{sym}", default={}) or {}
        signal   = sig.get("signal",   "WATCH")
        sigcolor = sig.get("sigcolor",  "#ffd600")
        score    = sig.get("score",     0)
        rsi      = sig.get("rsi",       None)
        asset    = _ASSET_CLASS.get(sym, "equity")

        if asset in ("fx", "commodity"):
            display_signal = "↑ RISING" if score > 1 else "↓ FALLING" if score < -1 else "→ NEUTRAL"
            display_color  = "#00c853" if score > 1 else "#ff1744" if score < -1 else "#ffd600"
        else:
            display_signal = signal
            display_color  = sigcolor

        rsi_str = f"RSI {rsi:.0f}" if rsi is not None else ""
        col.markdown(
            f'<div class="kpi-card" style="border-left-color:{display_color}">'
            f'<div class="kpi-label">{name}</div>'
            f'<div class="kpi-delta" style="color:{display_color};font-weight:800;font-size:0.95rem">'
            f'{display_signal}</div>'
            f'<div class="kpi-help">Score {score:+d}{" · " + rsi_str if rsi_str else ""}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════
# TOP MOVERS — @st.fragment (Tier 2, deferred)
# ══════════════════════════════════════════════════════════════════

TOP_MOVER_WATCH = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "SBIN.NS", "HINDUNILVR.NS", "ITC.NS", "AXISBANK.NS", "WIPRO.NS",
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
    "^NSEI", "^GSPC", "GC=F",
]


@st.fragment(run_every=60)
def _render_top_movers(cb: int):
    st.markdown('<p class="section-title">🚀 Top Movers Today</p>',
                unsafe_allow_html=True)
    # Guard: defer until ticker bar cache is warm to avoid cold-start burst
    if not is_ticker_cache_warm(_TICKER_SYMS):
        st.caption("⏳ Movers load after price data is ready…")
        return
    movers = safe_run(
        lambda: get_top_movers(TOP_MOVER_WATCH, max_symbols=20, cache_buster=cb),
        context="home:top_movers", default=[]
    )
    if not movers:
        st.caption("Loading movers data…")
        return
    cols = responsive_cols(min(len(movers[:6]), 6))
    for col, (sym, chg, price) in zip(cols, movers[:6]):
        color = "#00c853" if chg >= 0 else "#ff1744"
        arrow = "▲" if chg >= 0 else "▼"
        name  = sym.replace(".NS", "").replace(".BO", "")
        col.markdown(
            f'<div class="kpi-card" style="border-left-color:{color}">'
            f'<div class="kpi-label">{name}</div>'
            f'<div class="kpi-value" style="font-size:1.05rem">{price:,.2f}</div>'
            f'<div class="kpi-delta" style="color:{color}">{arrow} {abs(chg):.2f}%</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════
# NEWS FEED — @st.fragment (Tier 2, deferred — RSS only, no YF)
# ══════════════════════════════════════════════════════════════════

NEWS_FEEDS = [
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://feeds.bbci.co.uk/news/business/rss.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
]


@st.fragment(run_every=300)
def _render_news_feed(cb: int):
    st.markdown('<p class="section-title">📰 Latest Market News</p>',
                unsafe_allow_html=True)
    articles = safe_run(
        lambda: get_news(NEWS_FEEDS, max_n=6, cache_buster=0),  # news not stock-specific
        context="home:news", default=[]
    )
    if not articles:
        st.caption("Fetching headlines…")
        return
    for a in articles:
        st.markdown(
            f'<div class="news-card">'
            f'<div class="news-title"><a href="{a["link"]}" target="_blank" '
            f'style="color:#dde2f5;text-decoration:none">{a["title"]}</a></div>'
            f'<div class="news-meta">{a["source"]} · {a["date"]}</div>'
            f'<div class="news-sum">{a["summary"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════

def _s(t, n=200): return sanitise(t, max_len=n)


def render_homepage(cb: int = 0, market_open: bool = False):
    """
    Home page = Global Market Overview.
    Tier 1 (immediate): morning brief + market status + price snapshot
    Tier 2 (fragments): trend signals + top movers + news
    Zero additional API calls at T+0 — ticker bar cache is reused.
    """
    st.markdown(
        '<div style="font-size:2rem;font-weight:900;color:#c8d6f0;margin-bottom:2px">'
        '🌐 Global Market Overview</div>'
        f'<div style="font-size:0.82rem;color:#4b6080;margin-bottom:16px">'
        f'{CURRENT_VERSION} · Live signals · India · USA · Europe · Asia · Commodities</div>',
        unsafe_allow_html=True,
    )

    # ── Tier 1: immediate, no extra fetches ────────────────────────────────
    _render_morning_brief()
    st.divider()
    _render_market_status_row()
    st.divider()

    # Reuse ticker bar cache — get_ticker_bar_data_fresh has same cache key
    # as render_ticker_bar call above → guaranteed @st.cache_data HIT, 0 fetches
    batch_5d = safe_run(
        lambda: get_ticker_bar_data_fresh(_TICKER_SYMS),
        context="homepage:prices", default={},
    ) or {}
    if not batch_5d:
        batch_5d = {sym: _ticker_cache[sym] for sym in _TICKER_SYMS
                    if sym in _ticker_cache}
    _render_global_overview_prices(batch_5d)
    st.divider()

    # ── Tier 2: deferred fragments ─────────────────────────────────────────
    _render_global_signals()
    st.divider()
    _render_top_movers(cb)
    st.divider()
    _render_news_feed(cb)
