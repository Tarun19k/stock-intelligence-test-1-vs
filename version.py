# version.py
# Depends on: nothing
# Called from: config.py (re-exports CURRENT_VERSION), and any module that
#              wants the full changelog.
# Contains: VERSION_LOG list + CURRENT_VERSION string ONLY.

VERSION_LOG = [
    {"version": "v1.0",     "date": "2026-02-28", "notes": "Initial build — India stocks, 5 KPIs"},
    {"version": "v2.0",     "date": "2026-03-06", "notes": "USP layer: NLP sentiment, narrative detector, Monte Carlo ROI"},
    {"version": "v3.0",     "date": "2026-03-10", "notes": "643 validated tickers across India/USA/Europe/China"},
    {"version": "v3.1",     "date": "2026-03-10", "notes": "Phase 2: scrolling tickers, news feed, morning brief"},
    {"version": "v3.2",     "date": "2026-03-10", "notes": "Live auto-refresh via st.fragment — no full page reload"},
    {"version": "v3.3",     "date": "2026-03-10", "notes": "Phase 3: forecast accuracy tracking + auto-correction logic"},
    {"version": "v3.4",     "date": "2026-03-11", "notes": "[dev skip] Rapid iteration day — v3.4 tag not cut; rolled into v3.5"},
    {"version": "v3.5",     "date": "2026-03-11", "notes": "Phase 4-5: nav realign, global tickers, top movers, dashboard reorder"},
    {"version": "v3.6",     "date": "2026-03-11", "notes": "[dev skip] UI overhaul started same day; promoted directly to v4.1"},
    {"version": "v4.1",     "date": "2026-03-11", "notes": "Fully responsive UI — mobile/tablet/desktop CSS + Plotly responsive config"},
    {"version": "v5.0",     "date": "2026-03-14", "notes": "Refactor: 10-file modular structure"},
    {"version": "v5.1",     "date": "2026-03-16", "notes": "USA stock universe expanded: +8 groups, 169 total US tickers"},
    {"version": "v5.2",     "date": "2026-03-17", "notes": "Ticker bar fix: z-index, Streamlit header suppressed, width:100vw"},
    {"version": "v5.3",     "date": "2026-03-17", "notes": "Streamlit toolbar buttons hidden for clean production UI"},
    {"version": "v5.4",     "date": "2026-03-17", "notes": "Localised tab filters: Forecast horizon+lookback, Compare With inline"},
    {"version": "v5.5",     "date": "2026-03-17", "notes": "Deprecation fix: use_container_width replaced with width='stretch'"},
    {"version": "v5.6",     "date": "2026-03-17", "notes": "Insights cards fix: sanitise_bold() added, explicit text colors"},
    {"version": "v5.7",     "date": "2026-03-17", "notes": "Global readability audit: dark bg missing-color fixes across 5 files"},
    {"version": "v5.8",     "date": "2026-03-17", "notes": "Audit session: cross-file import scan, 38 issues catalogued"},
    {"version": "v5.9",     "date": "2026-03-18", "notes": "Patches shipped: _safe_close (5 files), sanitise_bold, NEWS_FEEDS fix"},
    {"version": "v5.10",    "date": "2026-03-18", "notes": "UI fixes: ticker via window.parent JS, MPA sidebar nav hidden"},
    {"version": "v5.11",    "date": "2026-03-18", "notes": "RSS allowlist: bbci.co.uk + bbc.co.uk added; http:// → https://"},
    {"version": "v5.12",    "date": "2026-03-18", "notes": "Regression suite: pd import fix; full 10-category validation green"},
    {"version": "v5.13",    "date": "2026-03-18", "notes": "Ticker fix: TATAMOTORS.NS replaced with TMCV.NS + TMPV.NS in 4 places"},
    {"version": "v5.14",    "date": "2026-03-18", "notes": "Auto-refresh redesign: @st.fragment (1s tick, non-blocking), scoped rerun"},
    {"version": "v5.15",    "date": "2026-03-18", "notes": "Auto-refresh: fragment inside sidebar, market-open auto-toggle"},
    {"version": "v5.15.1",  "date": "2026-03-18", "notes": "Hotfix: market_open param missing from render_dashboard backfilled"},
    {"version": "v5.15.2",  "date": "2026-03-18", "notes": "regression.py (166-check suite) + KNOWN_ISSUES_LOG.md added"},
    {"version": "v5.16",    "date": "2026-03-19", "notes": "Refactor: tickers extracted to tickers.json; version.py split from config.py"},
]

CURRENT_VERSION: str = VERSION_LOG[-1]["version"]
