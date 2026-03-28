# pages/global_intelligence.py
# Depends on: config, utils, market_data
# Called from: app.py → "🌍 Global Intelligence" route
# Entry point: render_global_intelligence(cur_sym, cb)

import pandas as pd
import streamlit as st
import streamlit.components.v1 as stc
from config import GLOBAL_TOPICS, NEXT_STEPS_AI
from utils import sanitise, safe_run, responsive_cols, log_error, safe_float
from market_data import get_news, get_price_data


def _render_impact_chain(chain: list):
    """Horizontal cascade of geopolitical impact nodes."""
    nodes_html = ""
    for i, (label, color, tooltip) in enumerate(chain):
        arrow = (
            f'<div style="color:#4b6080;font-size:1.1rem;'
            f'align-self:center;padding:0 2px">›</div>'
            if i < len(chain) - 1 else ""
        )
        nodes_html += (
            f'<div title="{tooltip}" style="background:#161c22;color:#c8d6f0;'
            f'border:1px solid {color};border-radius:10px;'
            f'padding:8px 12px;min-width:110px;max-width:140px;'
            f'text-align:center;cursor:help;flex-shrink:0">'
            f'<div style="font-size:0.70rem;color:{color};font-weight:700">'
            f'{label}</div>'
            f'<div style="font-size:0.62rem;color:#6b7a90;margin-top:3px">'
            f'{tooltip[:40]}</div>'
            f'</div>{arrow}'
        )
    st.markdown(
        f'<div style="overflow-x:auto">'
        f'<div style="display:flex;align-items:stretch;gap:6px;'
        f'padding:12px 4px;min-width:max-content">'
        f'{nodes_html}</div></div>',
        unsafe_allow_html=True  # content sanitised at source,
    )


def _render_watchlist_badges(tickers: list, cur_sym: str, cb: int):
    """Live mini price badges for a topic watchlist."""
    st.markdown('<p class="section-title">📌 Related Stocks to Watch</p>',
                unsafe_allow_html=True)
    cols = responsive_cols(min(len(tickers), 6))
    for col, sym in zip(cols, tickers):
        df = safe_run(
            lambda s=sym: get_price_data(s, period="5d", interval="1d",
                                         cache_buster=cb),
            context=f"gi:watchlist:{sym}", default=None,
        )
        if df is not None and not df.empty and len(df) >= 2:
            _cl = df["Close"].iloc[:,0] if isinstance(df["Close"], pd.DataFrame) else df["Close"]
            _cl = _cl.dropna()
            lp  = safe_float(_cl.iloc[-1]) if len(_cl) >= 1 else 0
            pp  = safe_float(_cl.iloc[-2]) if len(_cl) >= 2 else lp
            chg = (lp - pp) / pp * 100 if pp else 0
            color = "#00c853" if chg >= 0 else "#ff1744"
            arr   = "▲" if chg >= 0 else "▼"
            name  = sym.replace(".NS","").replace(".BO","")
            col.markdown(
                f'<div style="background:#0d1117;border:1px solid {color}44;'
                f'border-radius:8px;padding:8px;text-align:center">'
                f'<div style="font-size:0.72rem;color:#6b7a90">{name}</div>'
                f'<div style="font-size:0.90rem;font-weight:800;color:#fff">'
                f'{lp:,.0f}</div>'
                f'<div style="font-size:0.74rem;color:{color}">'
                f'{arr} {abs(chg):.1f}%</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            col.markdown(
                f'<div style="background:#0d1117;color:#c8d6f0;border:1px solid #2d3a5e;'
                f'border-radius:8px;padding:8px;text-align:center;'
                f'font-size:0.72rem;color:#4b6080">'
                f'{sym.replace(".NS","")}<br>—</div>',
                unsafe_allow_html=True,
            )


def _render_next_steps_ai():
    """Personalised AI career & investment action cards."""
    st.markdown('<p class="section-title">🎯 What You Should Do Next</p>',
                unsafe_allow_html=True)
    cols = responsive_cols(len(NEXT_STEPS_AI))
    for col, (title, body, color) in zip(cols, NEXT_STEPS_AI):
        col.markdown(
            f'<div style="background:#12151f;border:1px solid {color}44;'
            f'border-radius:12px;padding:14px;height:220px">'
            f'<div style="font-weight:900;color:{color};font-size:0.88rem;'
            f'margin-bottom:8px">{title}</div>'
            f'<div style="font-size:0.76rem;color:#9aa0b4;line-height:1.5">'
            f'{body}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def _render_topic_card(topic_name: str, topic: dict, cur_sym: str, cb: int):
    """Render one expandable topic card with chain + news + watchlist."""
    with st.expander(topic_name, expanded=True):
        color = topic["color"]
        st.markdown(
            f'<div style="font-size:0.82rem;color:{color};'
            f'font-weight:700;margin-bottom:6px">{topic["subtitle"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="insight-box" style="font-size:0.84rem;'
            f'color:#c8d6f0">{topic["overview"]}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("**📉 Impact Chain**")
        _render_impact_chain(topic["chain"])

        if topic.get("india_impact"):
            st.markdown(
                f'<div class="warn-box" style="font-size:0.82rem">'
                f'🇮🇳 <strong>India Impact:</strong> {topic["india_impact"]}'
                f'</div>',
                unsafe_allow_html=True,
            )

        sectors = ", ".join(topic.get("market_sectors", []))
        if sectors:
            st.markdown(
                f'<div class="group-badge">📊 Affected Sectors: {sectors}</div>',
                unsafe_allow_html=True,
            )

        if topic.get("watchlist"):
            _render_watchlist_badges(topic["watchlist"], cur_sym, cb)

        # Live news — only label "Live" when articles are recent (< 48 hours)
        from datetime import datetime, timezone
        import email.utils as _eut
        articles = safe_run(
            lambda: get_news(topic.get("rss", []), max_n=5, cache_buster=cb),
            context=f"gi:news:{topic_name[:20]}", default=[]
        )
        # Check if newest article is < 48h old
        _news_label = "📰 Recent Coverage"
        if articles:
            try:
                _newest = articles[0].get("date", "")
                _dt = _eut.parsedate_to_datetime(_newest) if _newest else None
                if _dt:
                    _age_h = (datetime.now(timezone.utc) - _dt).total_seconds() / 3600
                    _news_label = "📰 Live Headlines" if _age_h < 48 else f"📰 Recent Coverage ({_dt.strftime('%d %b %Y')})"
            except Exception:
                pass
        st.markdown(f'<p class="section-title">{_news_label}</p>',
                    unsafe_allow_html=True)
        if articles:
            for a in articles:
                st.markdown(
                    f'<div class="news-card">'
                    f'<div class="news-title"><a href="{a["link"]}" '
                    f'target="_blank" style="color:#dde2f5;text-decoration:none">'
                    f'{a["title"]}</a></div>'
                    f'<div class="news-meta">{a["source"]} · {a["date"]}</div>'
                    f'<div class="news-sum">{a["summary"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("Fetching headlines…")


def _s(t, n=200): return sanitise(t, max_len=n)

def render_global_intelligence(cur_sym: str = "$", cb: int = 0, market_open: bool = False):
    """Main entry point — called from app.py routing."""
    st.markdown(
        '<div style="font-size:1.6rem;font-weight:900;color:#c8d6f0;'
        'margin-bottom:4px">🌍 Global Intelligence Centre</div>'
        '<div style="font-size:0.84rem;color:#4b6080;margin-bottom:20px">'
        'Real-time geopolitical & technology trends · Impact chains · '
        'Market linkages · World monitor live feed</div>',
        unsafe_allow_html=True,
    )

    # WorldMonitor live map
    with st.expander("🗺️ WorldMonitor — Live Interactive Global Events Map",
                     expanded=True):
        st.caption("Live global event data. Use controls to explore conflicts, "
                   "economic zones, and risk regions.")
        # WorldMonitor blocks framing from *.streamlit.app (CSP frame-ancestors)
        # Show an inline link so the map is still accessible
        st.markdown(
            '<a href="https://worldmonitor.app" target="_blank" '
            'style="display:inline-flex;align-items:center;gap:8px;padding:10px 20px;'
            'background:#0d1b2e;border:1px solid #2d4a6e;border-radius:8px;'
            'color:#7eb3ff;text-decoration:none;font-size:0.9rem;font-weight:600">'
            '🗺️ Open WorldMonitor Live Map</a>',
            unsafe_allow_html=True,
        )
        st.caption(
            "WorldMonitor cannot be embedded here due to their Content Security Policy. "
            "Click above to open the live map in a new tab."
        )

    st.divider()

    # Topic cards
    for topic_name, topic in GLOBAL_TOPICS.items():
        _render_topic_card(topic_name, topic, cur_sym, cb)

    st.divider()
    st.markdown(
        '<div style="font-size:0.72rem;color:#4b6080;text-align:center;padding:8px">'
        '⚙️ Analysis is algorithmically generated from market data. '
        '<strong style="color:#ff9800">Not financial advice.</strong> '
        'For informational purposes only. Consult a SEBI-registered investment advisor '
        'before acting on any information shown here.'
        '</div>',
        unsafe_allow_html=True,
    )
