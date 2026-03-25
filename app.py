# app.py — KI-012 through KI-016 applied + v5.16 cache_buster patch
import streamlit as st
import pytz
from datetime import datetime
from config import CURRENT_VERSION, MARKET_SESSIONS, CURRENCY, GROUPS
from styles import inject_css
from utils import init_session_state, render_error_log
from market_data import get_price_data, get_ticker_info
from pages.home import render_homepage, render_ticker_bar
from pages.dashboard import render_dashboard
from pages.global_intelligence import render_global_intelligence
from pages.week_summary import (render_week_summary, render_market_overview,
                                  render_group_overview)

st.set_page_config(
    page_title=f"Global Stock Intelligence {CURRENT_VERSION}",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
init_session_state()

# ── Session defaults ─────────────────────────────────────────────────────────
if "nav_page"    not in st.session_state: st.session_state.nav_page    = "🏠 Home"
if "prev_ticker" not in st.session_state: st.session_state.prev_ticker = None
if "cb"          not in st.session_state: st.session_state.cb          = 0
if "data_stale"  not in st.session_state: st.session_state.data_stale  = False
if "grp_sel"     not in st.session_state: st.session_state.grp_sel     = None
if "stk_sel"     not in st.session_state: st.session_state.stk_sel     = None
if "stock_search"not in st.session_state: st.session_state.stock_search = ""
if "market_open" not in st.session_state: st.session_state.market_open = False

# ── Module-level refresh fragment ────────────────────────────────────────────
# Defined here, outside any 'with' block, so Streamlit registers it once
# per session and the 60s timer does NOT reset on user interactions.
# Drives the global ticker bar only — dashboard page has its own fragments.
@st.fragment(run_every=60)
def _refresh_fragment():
    """Kept for compatibility — ticker bar now self-manages via TTL cache.
    No longer increments cb (which was cache-busting ALL tickers every 60s).
    The global rate limiter in market_data.py handles yfinance pacing."""
    pass   # intentional no-op — do not re-add cb increment here


def _is_market_open(country: str) -> bool:
    sess = MARKET_SESSIONS.get(country, {})
    tz   = pytz.timezone(sess.get("tz", "UTC"))
    now  = datetime.now(tz)
    oh, om = sess.get("open",  (9, 0))
    ch, cm = sess.get("close", (17, 0))
    return (now.weekday() < 5
            and (oh, om) <= (now.hour, now.minute) < (ch, cm))

# ── KI-016: market-change callback ──────────────────────────────────────────
def _on_market_change():
    st.session_state["stock_search"] = ""
    st.session_state["prev_ticker"]  = None
    st.session_state["data_stale"]   = None
    for key in ("grp_sel", "stk_sel"):
        st.session_state.pop(key, None)
    st.session_state["nav_page"] = "🏠 Home"
    # NOTE: do NOT increment cb here — that would evict all ticker caches
    # for the new market before any data has been fetched. TTL handles staleness.

# ── Global ticker bar ────────────────────────────────────────────────────────
render_ticker_bar(cb=st.session_state.get("cb", 0))

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 📈 GSI Dashboard `{CURRENT_VERSION}`")
    st.divider()

    country = st.selectbox(
        "🌍 Market",
        list(MARKET_SESSIONS.keys()),
        index=0,
        key="market_sel",
        on_change=_on_market_change,
    )
    cur_sym    = CURRENCY.get(country, "$")
    mkt_grps   = GROUPS.get(country, {})
    market_open = _is_market_open(country)  # computed here so badge can use it

    selected_ticker = None
    selected_name   = None

    if mkt_grps:
        # Flat map of all stocks in the current market for search
        all_stocks: dict = {}
        for grp_name, stocks in mkt_grps.items():
            for sname, sticker in stocks.items():
                all_stocks[f"{sname} [{sticker}]"] = (sname, sticker, grp_name)

        search_query = st.text_input(
            "🔍 Search",
            placeholder="Company name or ticker symbol",
            key="stock_search",
        )

        if search_query.strip():
            q        = search_query.strip().lower()
            filtered = {
                k: v for k, v in all_stocks.items()
                if q in v[0].lower() or q in v[1].lower()
            }
            if not filtered:
                st.caption("No results — try a different name or symbol.")
            else:
                st.caption(f"{len(filtered)} result(s) found")
                selected_label = st.selectbox(
                    "Select", list(filtered.keys()),
                    label_visibility="collapsed",
                )
                # KI-019: guard against None on first render after market switch
                if selected_label and selected_label in filtered:
                    selected_name   = filtered[selected_label][0]
                    selected_ticker = filtered[selected_label][1]
        else:
            grp_names    = list(mkt_grps.keys())
            selected_grp = st.selectbox("📁 Group", grp_names, key="grp_sel")
            # KI-018: guard against None returned by pop() on market switch
            if selected_grp not in mkt_grps:
                selected_grp = grp_names[0]

            stock_map = mkt_grps[selected_grp]
            options   = ["— Select a stock —"] + list(stock_map.keys())
            chosen    = st.selectbox("📊 Stock", options, key="stk_sel")
            # KI-019: guard against None + missing key
            if chosen and chosen != "— Select a stock —" and chosen in stock_map:
                selected_name   = chosen
                selected_ticker = stock_map[chosen]

    # Auto-navigate to dashboard when a new stock is picked
    if selected_ticker and selected_ticker != st.session_state.prev_ticker:
        st.session_state.nav_page    = "📊 Dashboard"
        st.session_state.prev_ticker = selected_ticker
        st.session_state.data_stale  = True
        st.session_state.cb         += 1
        # Explicitly clear price + info caches so first load is always fresh.
        # cb increment alone is not sufficient — the new cb value may already
        # exist in cache from a prior fetch of the same ticker in this session.
        get_price_data.clear()
        get_ticker_info.clear()

    # Selected ticker badge
    if selected_ticker:
        st.markdown(
            f'<div style="background:#1a2332;border:1px solid #2d3a5e;'
            f'border-radius:8px;padding:6px 10px;margin:4px 0;'
            f'font-size:0.78rem;color:#7eb3ff;font-weight:700;font-family:monospace">'
            f'📌 {selected_ticker}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="background:#1a2332;border:1px dashed #2d3a5e;'
            'border-radius:8px;padding:6px 10px;margin:4px 0;'
            'font-size:0.76rem;color:#4b6080">'
            'No stock selected — showing weekly summary</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    nav = st.radio(
        "Navigate",
        ["🏠 Home", "📊 Dashboard", "🌍 Global Intelligence"],
        key="nav_page",
        label_visibility="collapsed",
    )

    # ── Market status badge ──────────────────────────────────────
    if market_open:
        st.markdown(
            '<div style="background:#00c85318;border:1px solid #00c853;'
            'border-radius:8px;padding:6px 12px;margin:4px 0;'
            'font-size:0.78rem;color:#00c853;font-weight:700;text-align:center">'
            '🟢 Market LIVE — auto-refreshing</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="background:#ff174418;border:1px solid #ff1744;'
            'border-radius:8px;padding:6px 12px;margin:4px 0;'
            'font-size:0.78rem;color:#ff1744;font-weight:700;text-align:center">'
            '🔴 Market CLOSED</div>',
            unsafe_allow_html=True,
        )

    if st.button("🔄 Refresh data"):
        st.session_state.cb += 1
        st.rerun()

    st.divider()
    render_error_log()
    _refresh_fragment()  # module-level — timer stable across user interactions

cb = st.session_state.cb
st.session_state.market_open = market_open  # fragment reads this

# ── Routing ──────────────────────────────────────────────────────────────────
# Determine view mode for Dashboard routing:
#   "stock"   — stock explicitly selected
#   "group"   — group selected, stock dropdown at placeholder
#   "market"  — market selected, no group/stock interaction
#   "week"    — default (no meaningful selection or no market groups)
_default_country = list(MARKET_SESSIONS.keys())[0]
if selected_ticker:
    _view_mode = "stock"
elif mkt_grps and st.session_state.get("stk_sel") in (None, "— Select a stock —", ""):
    # Group is selected but no stock chosen
    _view_mode = "group"
elif mkt_grps:
    _view_mode = "market"
else:
    _view_mode = "week"

if nav == "🏠 Home":
    render_homepage(cb=cb, market_open=market_open)

elif nav == "📊 Dashboard":
    if _view_mode == "stock":
        # v5.16 FIX: pass cache_buster=cb so Refresh button actually busts cache
        info = get_ticker_info(selected_ticker, cache_buster=cb)
        df   = get_price_data(selected_ticker,  cache_buster=cb)

        flat_stock_map = {
            sname: sticker
            for grp_stocks in mkt_grps.values()
            if isinstance(grp_stocks, dict)
            for sname, sticker in grp_stocks.items()
        }
        render_dashboard(
            ticker=selected_ticker,
            name=selected_name,
            country=country,
            cur_sym=cur_sym,
            info=info,
            df=df,
            cb=cb,
            stock_map=flat_stock_map,
            market_open=market_open,
        )

    elif _view_mode == "group":
        # Group selected, no stock — show group overview
        _grp = st.session_state.get("grp_sel") or (list(mkt_grps.keys())[0] if mkt_grps else None)
        if _grp and _grp in mkt_grps:
            render_group_overview(
                country=country, group_name=_grp,
                stocks=mkt_grps[_grp], cur_sym=cur_sym, cb=cb,
            )
        else:
            render_week_summary(cur_sym=cur_sym, cb=cb)

    elif _view_mode == "market":
        # Market selected, no group/stock — show market overview
        render_market_overview(
            country=country, groups=mkt_grps, cur_sym=cur_sym, cb=cb,
        )

    else:
        # Default — week summary
        render_week_summary(cur_sym=cur_sym, cb=cb)

elif nav == "🌍 Global Intelligence":
    render_global_intelligence(cur_sym=cur_sym, cb=cb, market_open=market_open)
