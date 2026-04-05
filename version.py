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
    {"version": "v5.17",    "date": "2026-03-20", "notes": "Bug fixes: forecast negative price clamp (OBS-006), polyfit crash guard on <2 rows (KI-021), styles.py CSS docstring merge (OBS-003), dead code removal home.py (OBS-002), late import fix dashboard.py (OBS-004), responsive_cols stub documented (OBS-001)"},
    {"version": "v5.18",    "date": "2026-03-21", "notes": "Live auto-refresh: market-open drives 5s price tile + 60s KPI/intraday fragments. Static header split. get_live_price() + get_intraday_chart_data() added. Manual toggle removed. Fragment at module level (fixes timer reset). LIVE/CLOSED badge in sidebar."},
    {"version": "v5.19",    "date": "2026-03-21", "notes": "Forecasting engine rebuild: polyfit replaced by Historical Simulation (2000 bootstrapped paths). Weinstein Stage + Elder Triple Screen veto. Unified verdict with conflict detection. Weekly accuracy calibration report on week summary page."},
    {"version": "v5.20",    "date": "2026-03-21", "notes": "UX fix: header now shows unified verdict (not raw score signal). 44% of stock views were showing misleading BUY on WATCH/AVOID stocks. Added _detect_asset_class(), P/E suppressed for non-equity. Momentum Score labelled pre-regime-filter. 7 new HELP_TEXT entries (Weinstein, Elder, P(gain), HistSim, conflict, unified_verdict). render_dashboard computes verdict before header renders."},
    {"version": "v5.20.1",  "date": "2026-03-21", "notes": "Hotfix: verdict_reason in compute_unified_verdict now contextualises score against verdict in plain English. Stage 2 + weak momentum now reads 'trend cycle healthy but technicals not supportive — wait for RSI/MACD to improve' instead of bare score number."},
    {"version": "v5.20.2",  "date": "2026-03-21", "notes": "Hotfix: app.py — explicit get_price_data.clear() + get_ticker_info.clear() on ticker switch. cb increment alone was insufficient — new cb value could already exist in cache from prior fetch of same ticker. Fixes stale price/blank charts on first stock load."},
    {"version": "v5.21",    "date": "2026-03-21", "notes": "Phase 2: Debt & Rates verdict suppression (RATES CONTEXT replaces BUY/SELL for yield instruments). Dynamic chart subplots — no blank MACD/RSI panels when indicators missing. Plain English header labels ('Trend and momentum agree' / 'Momentum signal adjusted'). All 6 new HELP_TEXT keys wired to tooltips (weinstein_stage, elder_screen, p_gain, hist_sim, conflict, unified_verdict). Debt KPI panel shows yield context warning."},
    {"version": "v5.22",    "date": "2026-03-23", "notes": "4-state dashboard routing: stock (full dashboard), group (group overview — weekly heatmap + signals + top/bottom movers), market (market breadth by group), default (revamped week summary — multi-asset chart + navigation hints). render_market_overview + render_group_overview added to week_summary.py."},
    {"version": "v5.23",    "date": "2026-03-24", "notes": "Portfolio Allocator: new portfolio.py (Mean-CVaR, Rockafellar-Uryasev 2000). 9 functions: data quality validator, log returns, winsorize (99th pctile), exponential-weighted bootstrap (2000 scenarios), cvxpy optimiser, efficient frontier, stability score, stress regime detection (VIX+correlation), regime conflict check. render_group_overview() gets 3-tab layout: Weekly Returns | Portfolio Allocator | Signal Summary. All CRITICAL+HIGH stress test fixes baked in: P1 VIX stress mode, M1 correlation crisis, D1 data quality validator, D3 winsorization, A1 exponential weighting, P4 leverage disclaimer, Layer 4 conflict check, post-cost return estimate, confidence band (P10-P90)."},
    {"version": "v5.24",    "date": "2026-03-26", "notes": "Lazy loading redesign (M0-M2): get_batch_data consolidates get_ticker_bar_data+get_group_data. Home page redesigned as Global Market Overview — removes render_week_summary call, adds _render_global_signals (@st.fragment), price snapshot (0-extra-fetch cache hit), _render_top_movers and _render_news_feed as @st.fragment. week_summary sections wrapped in @st.fragment: _index_perf_row, _nifty_heatmap, _sector_cards, _nifty_weekly_chart, _multi_asset_weekly_chart. render_group_overview uses get_batch_data. Cold-start API calls: ~100 tickers → 10 tickers."},
    {"version": "v5.25",    "date": "2026-03-26", "notes": "M3: routing guard — grp_explicitly_selected flag prevents 49-ticker group heatmap from auto-firing on cold start. render_group_overview only fires when user explicitly clicks a group. Reset on market switch. M1b: cold-start warmth guards on _render_global_signals and _render_top_movers — fragments defer fetches until ticker bar has populated _ticker_cache. get_batch_data raises RuntimeError on empty result so failed fetches are not cached for 300s TTL. is_ticker_cache_warm() added to market_data.py."},
    {"version": "v5.26", "date": "2026-03-26", "notes": "Hotfix batch: is_ticker_cache_warm majority threshold (70%); double _yf_batch_download cold start; _ticker_cache_time TTL bug; yfinance 0.2.54 MultiIndex; pandas 3.0 chained assignment; indicators len guard; live_price empty series guard; compare safe_run; chunk gap 3s to 5s; backoff 5s to 10s; 2s cold-start delay; OHLCV retry button; _refresh_fragment removed; R8 EP updated."},
    {"version": "v5.27", "date": "2026-03-27",
 "notes": "Emergency fix: global 429 cooldown gate (_is_rate_limited, _set_rate_limited, "
          "_clear_rate_limit_state) added to market_data.py. _yf_batch_download + "
          "_yf_download abort on cooldown instead of retrying. get_ticker_bar_data_fresh "
          "TTL 10s → 60s (root cause of 8,345-event 429 death spiral on Cloud). "
          "nav_page guards on _render_global_signals + _render_top_movers (fragment ghost fix). "
          "BUG-007 closed. 11 new R23 regression checks added."},
    {"version": "v5.28", "date": "2026-03-27",
     "notes": "Python 3.14 + dependency upgrade: streamlit 1.43.2->1.55.0, "
              "yfinance 0.2.54->1.2.0 (pandas 3.0 compatible, no breaking changes from 0.2.x), "
              "pandas 2.2.3->>=3.0.0. indicators.py: OBV direction .apply(lambda) replaced with "
              "numpy.sign() vectorised form (pandas 3.0 compatible). regression.py R2: "
              "width=content no longer flagged (valid in Streamlit 1.52+). "
              "DataManager M1 skeleton also included in this deploy."},


    {"version": "v5.29", "date": "2026-03-27",
     "notes": "get_ticker_info: add _is_rate_limited() gate (was missing from v5.27 — "              "only _yf_download/_yf_batch_download had the gate). Stops ticker info calls "              "firing during 429 cooldown window and polluting the error log."},
    {"version": "v5.30", "date": "2026-03-27",
     "notes": "styles.py: sidebar collapse button CSS updated for Streamlit 1.55 "              "compatibility. Added stSidebarCollapsedControl selector + main-area "              "button fallback. Removed stToolbar child visibility rule that was "              "interfering with 1.55 toolbar redesign."},
    {"version": "v5.31", "date": "2026-03-28",
     "notes": "P0 regulatory sprint (8 fixes, QA verified). "
              "Option B: raw Momentum Score removed from dashboard header (D-01). "
              "ROE null guard: N/A not 0.0% (D-02). "
              "SEBI disclaimer + algorithmic disclosure added to _tab_insights() (EQA-29, EQA-32). "
              "Watch Out For RSI/MACD-aware fallback — 'no red flags' blanket text removed (C-01 partial). "
              "Market status card labels shortened to IND/USA/EUR/CHN/COMM/ETF (H-03). "
              "GI topic cards expanded=True by default (F-01, F-15). "
              "TechCrunch RSS replaced + 48h freshness gate added (F-03). "
              "What You Should Do Next removed from GI page — liability risk (EQA-33, F-06, F-12). "
              "WorldMonitor CSP block: iframe replaced with external link button (G-01)."},
    {"version": "v5.32", "date": "2026-03-29",
     "notes": "Data coherence + temporal labeling sprint (9 fixes, 11 new R23b checks). "
              "OPEN-008: calc_5d_change() in utils.py — cross-page 5-day consistency. "
              "OPEN-009: P(gain) 45-55% neutral zone — excluded from accuracy scoring. "
              "OPEN-010: Forecast dedup — same-day entry replaced not silently skipped. "
              "OPEN-011: week_summary section titles dynamic: This Week vs Last Week. "
              "OPEN-012: Weinstein override label names the stage explicitly. "
              "OPEN-013: MACD chart subplots and KPI panel show (Daily) timeframe. "
              "OPEN-014: GI watchlist filters to selected market via _market_of(). "
              "OPEN-015: Market LIVE badge names specific market country. "
              "OPEN-016: GI watchlist cache_buster=0 — price coherence with ticker bar. "},
    {"version": "v5.33", "date": "2026-03-31",
     "notes": "Security, compliance & governance sprint (8 fixes, 10 new R25 checks). "
              "RISK-003: safe_ticker_key() before yf.download()/_yf_batch_download(). "
              "RISK-001: sanitise()/safe_url() XSS guards on all RSS output in home.py + GI. "
              "D-07: Elder Triple Screen labels → plain English (Bullish setup / Hold / Bearish). "
              "G-02: GI topics expanded 2→5 (US Rate Cycle, China Slowdown, Commodities). "
              "G-05: GI subtitle false 'Real-Time' claim removed. "
              "H-02: First-load cards show 'Loading…'/'Computing…' not silent '—'. "
              "D-09: Forecast auto-correction factor disclosed before P(gain) card. "
              "OPEN-017: R25 governance regression checks (6 policy enforcement rules). "
              "P0 compliance gaps found + fixed: SEBI disclaimer, algo disclosure, "
              "'no red flags' blanket fallback, 48h Live Headlines gate — "
              "all were listed as v5.31 fixes but were never committed to the codebase. "
              "GSI_LOOPHOLE_LOG.md created — 6-class automation loophole registry. "
              "Regression baseline: 400→410 (10 new R25 checks)."},
    {"version": "v5.34", "date": "2026-04-01",
     "notes": "Sprint manifest infrastructure + v5.33 doc debt backfill + observability dashboard + UX fixes. "
              "GSI_SPRINT_MANIFEST.json + R27: living sprint manifest system — every committed file "
              "must be logged with doc_updates_required or no_doc_update_reason; R27 enforces this "
              "with Pass 1 (log completeness) + Pass 2 (must_contain checks). "
              "Doc debt (v5.33 misses): 6 audit trail resolutions (H-02/D-07/D-09/G-02/G-05/EQA-38), "
              "GSI_GOVERNANCE.md enforcement Planned→Implemented, RISK-T09 Open→Mitigated, "
              "GSI_LOOPHOLE_LOG.md Class 4 Fixed, missing v5.31 version entry added. "
              "Phase 1 — observability: market_data.py instrumentation (_cache_stats, _fetch_errors, "
              "_fetch_latency_ms, get_health_stats(), get_rate_limit_state()); "
              "pages/observability.py founder-only page (App Health + Program tabs, DEV_TOKEN gate); "
              "5 new R26 regression checks. "
              "Phase 2 — UX: D-05 loading spinner on Dashboard nav (data_stale gate); "
              "G-03/F-10 impact chain overflow CSS fix (width:100% + box-sizing:border-box at 1280px); "
              "F-14 West Asia quantitative claims now carry source attribution (Reuters/EIA/PPAC/Drewry). "
              "Regression baseline: 410→415 (5 new R26 checks; R27 checks are sprint-active only)."},
    {"version": "v5.34.1", "date": "2026-04-05",
     "notes": "Claude Code hook infrastructure sprint. "
              "compliance_check.py: 8-check pre-push gate extracted from CLAUDE.md inline script "
              "(fixed dashboard.py→pages/dashboard.py path bug; CWD auto-correction for hook context). "
              ".claude/hooks/pre_commit.sh: PreToolUse regression gate — exit 2 blocks git commit on "
              "regression failure; deduplicates via run_state.json (skips if PASS at current HEAD). "
              ".claude/hooks/pre_push.sh: PreToolUse compliance gate — exit 2 blocks git push on any "
              "compliance_check.py failure. "
              ".claude/hooks/post_edit.sh: PostToolUse doc audit — fires on Write|Edit of *.md files; "
              "calls sync_docs.py --check; suppressOutput on clean pass (PostToolUse cannot block). "
              "settings.json: full hooks block wired (3 hooks, $CLAUDE_PROJECT_DIR paths); "
              "sync_docs --check migrated from settings.local.json allow list. "
              "R27: schema bugfixes (target_file field + must_contain list iteration). "
              "Regression baseline: 427 pre-sprint (450 total checks mid-sprint including 23 R27 checks)."}
]

CURRENT_VERSION: str = VERSION_LOG[-1]["version"]