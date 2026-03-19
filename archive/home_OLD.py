# pages/home.py — Phase 2: exact homepage with fixed top ticker bar
# Depends on: config, utils, market_data
# Entry point: render_homepage(cb)
#   render_ticker_bar() — called from app.py BEFORE sidebar renders
#                         so it appears at the absolute page top

import pytz
import pandas as pd
import streamlit as st
import streamlit.components.v1 as _st_components
from datetime import datetime, timedelta
from config import MARKET_SESSIONS, CURRENT_VERSION, VERSION_LOG
from pages.week_summary import render_week_summary
from utils import sanitise,  safe_run, responsive_cols, log_error
from market_data import get_price_data, get_top_movers, get_news


# ══════════════════════════════════════════════════════════════════
# GLOBAL TICKER BAR — fixed to top of every page
# Called once from app.py before sidebar so it renders above all
# ══════════════════════════════════════════════════════════════════

TICKER_SYMBOLS = [
    ("Nifty 50",    "^NSEI"),
    ("Sensex",      "^BSESN"),
    ("Bank Nifty",  "^NSEBANK"),
    ("S&P 500",     "^GSPC"),
    ("Nasdaq",      "^NDX"),
    ("Dow Jones",   "^DJI"),
    ("Hang Seng",   "^HSI"),
    ("Gold",        "GC=F"),
    ("Crude WTI",   "CL=F"),
    ("USD/INR",     "USDINR=X"),
]

def render_ticker_bar(cb: int = 0):
    """
    Renders a fixed 36px ticker strip pinned to the very top of the page.

    Strategy: st.markdown() puts HTML inside Streamlit's component tree where
    position:fixed is trapped by ancestor overflow constraints. We escape this
    by using st.components.v1.html() which renders in an iframe, then uses
    window.parent to inject the ticker directly into the host page's <body>.
    CSS is still injected unconditionally via st.markdown for the header-hide
    and padding rules (those work fine from st.markdown).
    """
    import streamlit.components.v1 as _components

    # ① CSS always fires — hides Streamlit header, reserves 36px top padding
    st.markdown("""<style>
header[data-testid="stHeader"]{height:0!important;min-height:0!important;
    padding:0!important;overflow:hidden!important;visibility:hidden!important;}
.stAppToolbar,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;}
[data-testid="stAppViewContainer"]>section[data-testid="stMain"]{padding-top:36px!important;}
.main .block-container{padding-top:50px!important;}
[data-testid="stSidebar"]>div:first-child{padding-top:36px!important;margin-top:0!important;}
</style>""", unsafe_allow_html=True)

    # ② Build ticker data
    items = []
    for name, sym in TICKER_SYMBOLS:
        df = safe_run(
            lambda s=sym: get_price_data(s, period="5d", interval="1d"),
            context=f"ticker_bar:{sym}", default=None,
        )
        if df is not None and not df.empty and len(df) >= 2 and "Close" in df.columns:
            _cl = df["Close"]
            _cl = _cl.iloc[:, 0] if isinstance(_cl, pd.DataFrame) else _cl
            _cl = _cl.dropna().astype(float)
            if len(_cl) < 2:
                continue
            lp  = float(_cl.iloc[-1])
            pp  = float(_cl.iloc[-2])
            chg = (lp - pp) / pp * 100 if pp else 0
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
        return  # CSS already injected above — layout stays clean

    ticker_content = " ".join(items * 3)  # triple for seamless CSS loop

    # ③ Inject ticker HTML into window.parent (host page body) via iframe JS
    #    This fully escapes Streamlit's component tree and renders as a true
    #    fixed overlay — not inside any st container.
    _components.html(f"""
<script>
(function() {{
    var TICKER_ID = 'gsi-ticker-bar';
    var parent = window.parent;
    if (!parent) return;

    // Remove stale ticker on re-render
    var old = parent.document.getElementById(TICKER_ID);
    if (old) old.remove();

    // Inject style into parent head (idempotent)
    if (!parent.document.getElementById('gsi-ticker-css')) {{
        var s = parent.document.createElement('style');
        s.id = 'gsi-ticker-css';
        s.textContent = `
            #gsi-ticker-bar {{
                position: fixed;
                top: 0; left: 0;
                width: 100vw;
                height: 36px;
                z-index: 2147483647;
                background: linear-gradient(90deg,#070c1a 0%,#0a1020 100%);
                border-bottom: 1px solid #1a2540;
                overflow: hidden;
                display: flex;
                align-items: center;
                box-shadow: 0 2px 12px rgba(0,0,0,.5);
            }}
            #gsi-ticker-bar .ticker-track {{
                display: flex;
                align-items: center;
                white-space: nowrap;
                animation: gsiScroll 60s linear infinite;
                will-change: transform;
            }}
            #gsi-ticker-bar:hover .ticker-track {{
                animation-play-state: paused;
            }}
            @keyframes gsiScroll {{
                0%   {{ transform: translateX(0); }}
                100% {{ transform: translateX(-33.33%); }}
            }}
            #gsi-ticker-bar .tick-item {{
                display: inline-flex; align-items: center; gap: 5px;
                padding: 0 12px;
                font-size: .71rem;
                font-family: "JetBrains Mono","Fira Code",ui-monospace,monospace;
            }}
            #gsi-ticker-bar .tick-name  {{ color:#4b6080; font-weight:600; }}
            #gsi-ticker-bar .tick-price {{ color:#c8d6f0; font-weight:700; }}
            #gsi-ticker-bar .tick-chg   {{ font-weight:700; }}
            #gsi-ticker-bar .tick-sep   {{ color:#1f2d40; padding:0 3px; font-size:.8rem; }}
        `;
        parent.document.head.appendChild(s);
    }}

    // Create and inject ticker div
    var div = parent.document.createElement('div');
    div.id = TICKER_ID;
    div.innerHTML = '<div class="ticker-track">{ticker_content}</div>';
    parent.document.body.prepend(div);
}})();
</script>
""", height=0, scrolling=False)
# ══════════════════════════════════════════════════════════════════
# MARKET STATUS
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
            f'<div class="kpi-card" style="border-left-color:{color}">' +
            f'<div class="kpi-label">{mkt}</div>' +
            f'<div class="kpi-delta" style="color:{color};font-weight:700">{label}</div>' +
            f'{"<div class=kpi-help>" + sub + "</div>" if sub else ""}' +
            f'</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════
# MORNING BRIEF
# ══════════════════════════════════════════════════════════════════

def _render_morning_brief():
    now_ist = datetime.now(pytz.timezone("Asia/Kolkata"))
    h = now_ist.hour
    if   h < 6:  msg = "Pre-dawn. Asian futures are setting early direction for the day."
    elif h < 9:  msg = "Pre-market. Watch SGX Nifty and Dow futures for opening clues."
    elif h < 10: msg = "Opening bell. First 30-minute range often defines the day's bias."
    elif h < 12: msg = "Morning session. Institutional order flow peaks before noon — watch block deals."
    elif h < 14: msg = "Midday consolidation. Volume tapers — breakouts here often extend into close."
    elif h < 15: msg = "Final 90 minutes. FII/DII provisional data and closing auction drive last moves."
    elif h < 16: msg = "Post-market. Review today's data, set alerts, plan tomorrow's watchlist."
    else:        msg = "Market closed. Global cues — US markets, Asian overnight, F&O data — matter now."

    st.markdown(
        f'<div class="insight-box">' +
        f'<span style="font-size:0.78rem;color:#6b7a90">' +
        f'{now_ist.strftime("%A, %d %B %Y")} · {now_ist.strftime("%H:%M")} IST</span><br>' +
        f'<span style="font-size:0.88rem;color:#c8d6f0">{msg}</span>' +
        f'</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════
# TOP MOVERS
# ══════════════════════════════════════════════════════════════════

TOP_MOVER_WATCH = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
    "SBIN.NS","HINDUNILVR.NS","ITC.NS","AXISBANK.NS","WIPRO.NS",
    "AAPL","MSFT","GOOGL","AMZN","NVDA","META","TSLA",
    "^NSEI","^GSPC","GC=F",
]

def _render_top_movers(cb: int):
    st.markdown('<p class="section-title">🚀 Top Movers Today</p>',
                unsafe_allow_html=True)
    movers = safe_run(
        lambda: get_top_movers(TOP_MOVER_WATCH, max_symbols=20),
        context="home:top_movers", default=[]
    )
    if not movers:
        st.caption("Loading movers data…")
        return
    cols = responsive_cols(min(len(movers[:6]), 6))
    for col, (sym, chg, price) in zip(cols, movers[:6]):
        color = "#00c853" if chg >= 0 else "#ff1744"
        arrow = "▲" if chg >= 0 else "▼"
        name  = sym.replace(".NS","").replace(".BO","")
        col.markdown(
            f'<div class="kpi-card" style="border-left-color:{color}">' +
            f'<div class="kpi-label">{name}</div>' +
            f'<div class="kpi-value" style="font-size:1.05rem">{price:,.2f}</div>' +
            f'<div class="kpi-delta" style="color:{color}">{arrow} {abs(chg):.2f}%</div>' +
            f'</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════
# NEWS FEED
# ══════════════════════════════════════════════════════════════════

NEWS_FEEDS = [
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://feeds.bbci.co.uk/news/business/rss.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
]

def _render_news_feed(cb: int):
    st.markdown('<p class="section-title">📰 Latest Market News</p>',
                unsafe_allow_html=True)
    articles = safe_run(
        lambda: get_news(NEWS_FEEDS, max_n=6),
        context="home:news", default=[]
    )
    if not articles:
        st.caption("Fetching headlines…")
        return
    for a in articles:
        st.markdown(
            f'<div class="news-card">' +
            f'<div class="news-title"><a href="{a["link"]}" target="_blank" ' +
            f'style="color:#dde2f5;text-decoration:none">{a["title"]}</a></div>' +
            f'<div class="news-meta">{a["source"]} · {a["date"]}</div>' +
            f'<div class="news-sum">{a["summary"]}</div>' +
            f'</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════
# VERSION LOG
# ══════════════════════════════════════════════════════════════════

def _render_version_log():
    with st.expander("📋 Version History", expanded=False):
        rows = [{"Version": v["version"], "Date": v["date"], "Notes": v["notes"]}
                for v in reversed(VERSION_LOG)]
        st.dataframe(pd.DataFrame(rows), width='stretch', hide_index=True)


# ══════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════

def _s(t, n=200): return sanitise(t, max_len=n)

@st.fragment(run_every=60)
def _render_live_section(market_open: bool = False, cb: int = 0):
    """
    Fragment wrapping all DYNAMIC home-page sections:
    morning brief status, market session open/closed badges, top movers.
    Runs every 60 s when called (Streamlit ignores run_every if market is
    closed — we control that by only calling with run_every when open).
    Static sections (news feed, version log) live outside this fragment.
    """
    safe_run(_render_morning_brief,   context="morning_brief")


def render_homepage(cb: int = 0, market_open: bool = False):
    """Called from app.py routing — renders the Home page body."""
    st.markdown(
        '<div style="font-size:2rem;font-weight:900;color:#c8d6f0;margin-bottom:2px">' +
        '📈 Global Stock Intelligence</div>' +
        f'<div style="font-size:0.82rem;color:#4b6080;margin-bottom:16px">' +
        f'{CURRENT_VERSION} · Real-time · India · USA · Europe · China · ETFs · Commodities</div>',
        unsafe_allow_html=True,
    )
    _render_morning_brief()
    st.divider()
    _render_market_status_row()
    st.divider()
    _render_top_movers(cb)
    st.divider()
    _render_news_feed(cb)
    st.divider()
    render_week_summary(cur_sym="₹", cb=cb)
    st.divider()
    _render_version_log()
