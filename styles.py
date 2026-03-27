# styles.py
# Depends on: nothing
# Called from: app.py only (inject once at boot)
# Contains: full CSS string — no logic

import streamlit as st

CSS = """
<style>
body, .main { background: #0e1117; color: #c8d6f0; }

/* ── Ticker bar: suppress Streamlit header so fixed strip sits flush ── */
header[data-testid="stHeader"] {
    height: 0 !important; min-height: 0 !important;
    padding: 0 !important; overflow: hidden !important;
    visibility: hidden !important;
}
/* ── Toolbar: hide chrome, preserve the sidebar collapse button ─ */
/* Streamlit 1.55: stAppToolbar redesigned — hide decoration only */
[data-testid="stDecoration"]  { display: none !important; }
[data-testid="stDeployButton"] { display: none !important; }

/* Make the toolbar bar itself invisible but keep it in flow      */
/* so the collapse button remains accessible.                     */
[data-testid="stAppToolbar"] {
    background: transparent !important;
    border-bottom: none !important;
    box-shadow: none !important;
}

/* ── Sidebar OPEN: collapse button (right edge of sidebar) ────── */
[data-testid="stSidebar"] button[data-testid="baseButton-headerNoPadding"] {
    background: #1a2540 !important;
    border: 1px solid #2d3a5e !important;
    border-radius: 0 8px 8px 0 !important;
    opacity: 1 !important;
}

/* ── Sidebar CLOSED: re-open pill (Streamlit 1.55 + fallback) ─── */
/* Streamlit 1.55 moved the collapsed control — target both        */
/* the legacy data-testid and the new button placement.            */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
    position: fixed !important;
    left: 0 !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    z-index: 9999999 !important;
    background: #1a2540 !important;
    border: 1px solid #2d3a5e !important;
    border-left: none !important;
    border-radius: 0 8px 8px 0 !important;
    width: 20px !important;
    height: 56px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 2px 0 8px rgba(0,0,0,0.5) !important;
    cursor: pointer !important;
    visibility: visible !important;
    opacity: 1 !important;
}
[data-testid="collapsedControl"]:hover,
[data-testid="stSidebarCollapsedControl"]:hover {
    background: #253356 !important;
    width: 26px !important;
}
[data-testid="collapsedControl"] button,
[data-testid="stSidebarCollapsedControl"] button {
    background: transparent !important;
    border: none !important;
    width: 100% !important; height: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    visibility: visible !important;
}
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] svg {
    stroke: #4f8ef7 !important;
    fill: none !important;
    width: 12px !important; height: 12px !important;
    visibility: visible !important;
}

/* Streamlit 1.55: sidebar toggle button when sidebar is collapsed */
/* targets the floating button Streamlit renders in the main area  */
section[data-testid="stMain"] > div > button[kind="header"],
section[data-testid="stMain"] button[data-testid="baseButton-headerNoPadding"] {
    position: fixed !important;
    left: 0 !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    z-index: 9999999 !important;
    background: #1a2540 !important;
    border: 1px solid #2d3a5e !important;
    border-left: none !important;
    border-radius: 0 8px 8px 0 !important;
    width: 20px !important;
    height: 56px !important;
    visibility: visible !important;
    opacity: 1 !important;
    cursor: pointer !important;
}

/* ── Fixed 36px ticker strip ── */
.ticker-wrap {
    position: fixed; top: 0; left: 0; width: 100vw; z-index: 1000000;
    background: linear-gradient(90deg, #070c1a 0%, #0a1020 100%);
    border-bottom: 1px solid #1a2540; height: 32px;
    overflow: hidden; display: flex; align-items: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.5);
}
.ticker-track {
    display: flex; align-items: center; white-space: nowrap;
    animation: tickerScroll 60s linear infinite; will-change: transform;
}
.ticker-wrap:hover .ticker-track { animation-play-state: paused; }
@keyframes tickerScroll {
    0%   { transform: translateX(0); }
    100% { transform: translateX(-33.33%); }
}
.tick-item  { display:inline-flex;align-items:center;gap:5px;padding:0 12px;
              font-size:0.71rem;font-family:'JetBrains Mono','Fira Code',ui-monospace,monospace; }
.tick-name  { color:#4b6080;font-weight:600; }
.tick-price { color:#c8d6f0;font-weight:700; }
.tick-chg   { font-weight:700; }
.tick-sep   { color:#1f2d40;padding:0 3px;font-size:0.8rem; }

/* ── Padding so content clears the fixed ticker bar ── */
[data-testid="stAppViewContainer"] > section[data-testid="stMain"]
    { padding-top: 32px !important; }
.main .block-container     { padding-top: 46px !important; }
section.main > div:first-child { padding-top: 32px !important; }
[data-testid="stSidebar"] > div:first-child
    { padding-top: 36px !important; margin-top: 0 !important; }

/* ── Hide Streamlit's auto-generated MPA sidebar nav ── */
[data-testid="stSidebarNav"]          { display: none !important; }
[data-testid="stSidebarNavItems"]     { display: none !important; }
[data-testid="stSidebarNavSeparator"] { display: none !important; }
section[data-testid="stSidebar"] > div:first-child > div:first-child
    { padding-top: 0 !important; }

/* ── Hide deploy / share button ── */
[data-testid="stDeployButton"] { display: none !important; }



.kpi-card {
    background: linear-gradient(135deg, #1e2130, #252840); color: #c8d6f0;
    border-radius: 12px; padding: 14px 18px; margin: 5px 0;
    border-left: 4px solid #4f8ef7;
}
.kpi-card.green  { border-left-color: #00c853; }
.kpi-card.red    { border-left-color: #ff1744; }
.kpi-card.yellow { border-left-color: #ffd600; }

.kpi-value  { font-size: 1.6rem; font-weight: 800; color: #fff; }
.kpi-label  { font-size: 0.72rem; color: #9aa0b4; text-transform: uppercase; letter-spacing: 1px; }
.kpi-delta  { font-size: 0.82rem; margin-top: 3px; }
.kpi-help   { font-size: 0.72rem; color: #5c6380; margin-top: 4px; font-style: italic; }

.section-title {
    font-size: 1.15rem; font-weight: 700; color: #c8cee8;
    margin: 28px 0 10px; padding-bottom: 6px;
    border-bottom: 1px solid #1f2540;
}

.insight-box {
    background: linear-gradient(135deg, #0d2137, #102040);
    border: 1px solid #1e4060; border-radius: 10px; padding: 13px 17px; margin: 7px 0;
;color:#c8d6f0;font-size:0.84rem;line-height:1.6}
.action-box {
    background: linear-gradient(135deg, #0d2614, #0f2d17);
    border: 1px solid #1a4d24; border-radius: 10px; padding: 13px 17px; margin: 7px 0;
;color:#b9f5c8;font-size:0.84rem;line-height:1.6}
.warn-box {
    background: linear-gradient(135deg, #2a1a00, #331f00);
    border: 1px solid #5c3800; border-radius: 10px; padding: 13px 17px; margin: 7px 0;
;color:#ffe0b2;font-size:0.84rem;line-height:1.6}

.news-card  { background: #1a1d2e; color: #c8d6f0; border-radius: 8px; padding: 11px 14px; margin: 5px 0; border-left: 3px solid #4f8ef7; }
.news-title { font-size: 0.86rem; font-weight: 600; color: #dde2f5; }
.news-meta  { font-size: 0.70rem; color: #6b7280; margin-top: 3px; }
.news-sum   { font-size: 0.78rem; color: #8a91a8; margin-top: 4px; }

.group-badge { background: #1a2035; border: 1px solid #2d3a5e; border-radius: 8px; padding: 10px 14px; margin: 4px 0; font-size: 0.82rem; color: #9aa0b4; }
.graph-help  { background: #12151f; border-left: 3px solid #2d3a5e; border-radius: 6px; padding: 10px 14px; margin: 8px 0; font-size: 0.80rem; color: #7a82a0; }
.valid-badge { background: #0d2614; border: 1px solid #1a4d24; border-radius: 6px; padding: 4px 10px; font-size: 0.72rem; color: #4caf50; display: inline-block; margin-top: 4px; }

/* ── Responsive ── */
@media screen and (max-width: 768px) {
    [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important; }
    .kpi-card  { padding: 10px 12px !important; margin: 3px 0 !important; }
    .kpi-value { font-size: 1.25rem !important; }
    .kpi-label { font-size: 0.65rem !important; }
    .kpi-delta { font-size: 0.72rem !important; }
    .section-title { font-size: 0.95rem !important; }
    .news-card  { padding: 9px 11px !important; }
    .news-title { font-size: 0.82rem !important; }
    .news-meta  { font-size: 0.65rem !important; }
    .news-sum   { font-size: 0.72rem !important; }
    .insight-box, .action-box, .warn-box { padding: 10px 12px !important; font-size: 0.80rem !important; }
    .group-badge { padding: 8px 10px !important; font-size: 0.78rem !important; }
    [data-testid="stPlotlyChart"] div { height: 280px !important; min-height: 220px !important; }
    [data-testid="stSidebar"] { min-width: 260px !important; max-width: 80vw !important; }
    [data-testid="stButton"] button { width: 100% !important; font-size: 0.82rem !important; padding: 8px 12px !important; }
    [data-testid="stSelectbox"] { width: 100% !important; }
    [data-testid="stRadio"] div { flex-wrap: wrap !important; gap: 6px !important; }
    .main .block-container { padding: 1rem 0.75rem !important; max-width: 100% !important; }
}
@media screen and (min-width: 769px) and (max-width: 1024px) {
    [data-testid="column"] { min-width: 45% !important; }
    .kpi-value { font-size: 1.4rem !important; }
    [data-testid="stPlotlyChart"] div { height: 340px !important; }
    .main .block-container { padding: 1.2rem 1rem !important; }
}
@media (hover: none) and (pointer: coarse) {
    [data-testid="stButton"] button { min-height: 44px !important; font-size: 0.88rem !important; }
    [data-testid="stSelectbox"] select, [data-testid="stMultiSelect"] { min-height: 44px !important; }
    [data-testid="stCheckbox"] label { min-height: 40px !important; display: flex !important; align-items: center !important; }
}
.insight-box b,.insight-box strong{color:#ffffff;font-weight:800}.action-box b,.action-box strong{color:#ffffff;font-weight:800}.warn-box b,.warn-box strong{color:#ffcc80;font-weight:800}</style>
"""


def inject_css():
    """Inject global CSS once at app startup. Call from app.py before any other render."""
    st.markdown(CSS, unsafe_allow_html=True)
    # Clear any stale sidebar-collapsed state from browser localStorage.
    # Streamlit stores sidebar state under keys like 'stSidebar' or similar —
    # clearing them ensures the sidebar opens on first load after a CSS change.
    import streamlit.components.v1 as _stc
    _stc.html(
        "<script>"
        "try{"
        "var keys=Object.keys(window.parent.localStorage);"
        "keys.forEach(function(k){"
        "if(k.indexOf('sidebar')>-1||k.indexOf('Sidebar')>-1||k.indexOf('collapsed')>-1){"
        "window.parent.localStorage.removeItem(k);"
        "}"
        "});"
        "}catch(e){}"
        "</script>",
        height=0, scrolling=False
    )
