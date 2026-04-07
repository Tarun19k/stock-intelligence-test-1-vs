# Changelog

All notable changes to GSI Dashboard.
Full technical detail in `version.py` → `VERSION_LOG`.

## v1.0 — 2026-02-28

- Initial build — India stocks, 5 KPIs.

## v2.0 — 2026-03-06

- USP layer: NLP sentiment, narrative detector, Monte Carlo ROI.

## v3.0 — 2026-03-10

- 643 validated tickers across India/USA/Europe/China.

## v3.1 — 2026-03-10

- Phase 2: scrolling tickers, news feed, morning brief.

## v3.2 — 2026-03-10

- Live auto-refresh via st.fragment — no full page reload.

## v3.3 — 2026-03-10

- Phase 3: forecast accuracy tracking + auto-correction logic.

## v3.4 — 2026-03-11

- [dev skip] Rapid iteration day — v3.4 tag not cut; rolled into v3.5.

## v3.5 — 2026-03-11

- Phase 4-5: nav realign, global tickers, top movers, dashboard reorder.

## v3.6 — 2026-03-11

- [dev skip] UI overhaul started same day; promoted directly to v4.1.

## v4.1 — 2026-03-11

- Fully responsive UI — mobile/tablet/desktop CSS + Plotly responsive config.

## v5.0 — 2026-03-14

- Refactor: 10-file modular structure.

## v5.1 — 2026-03-16

- USA stock universe expanded: +8 groups, 169 total US tickers.

## v5.2 — 2026-03-17

- Ticker bar fix: z-index, Streamlit header suppressed, width:100vw.

## v5.3 — 2026-03-17

- Streamlit toolbar buttons hidden for clean production UI.

## v5.4 — 2026-03-17

- Localised tab filters: Forecast horizon+lookback, Compare With inline.

## v5.5 — 2026-03-17

- Deprecation fix: use_container_width replaced with width='stretch'.

## v5.6 — 2026-03-17

- Insights cards fix: sanitise_bold() added, explicit text colors.

## v5.7 — 2026-03-17

- Global readability audit: dark bg missing-color fixes across 5 files.

## v5.8 — 2026-03-17

- Audit session: cross-file import scan, 38 issues catalogued.

## v5.9 — 2026-03-18

- Patches shipped: _safe_close (5 files), sanitise_bold, NEWS_FEEDS fix.

## v5.10 — 2026-03-18

- UI fixes: ticker via window.parent JS, MPA sidebar nav hidden.

## v5.11 — 2026-03-18

- RSS allowlist: bbci.co.uk + bbc.co.uk added; http:// → https://.

## v5.12 — 2026-03-18

- Regression suite: pd import fix; full 10-category validation green.

## v5.13 — 2026-03-18

- Ticker fix: TATAMOTORS.NS replaced with TMCV.NS + TMPV.NS in 4 places.

## v5.14 — 2026-03-18

- Auto-refresh redesign: @st.fragment (1s tick, non-blocking), scoped rerun.

## v5.15 — 2026-03-18

- Auto-refresh: fragment inside sidebar, market-open auto-toggle.

## v5.15.1 — 2026-03-18

- Hotfix: market_open param missing from render_dashboard backfilled.

## v5.15.2 — 2026-03-18

- regression.py (166-check suite) + KNOWN_ISSUES_LOG.md added.

## v5.16 — 2026-03-19

- Refactor: tickers extracted to tickers.json; version.py split from config.py.

## v5.17 — 2026-03-20

- Bug fixes: forecast negative price clamp (OBS-006), polyfit crash guard on <2 rows (KI-021), styles.py CSS docstring merge (OBS-003), dead code removal home.py (OBS-002), late import fix dashboard.py (OBS-004), responsive_cols stub documented (OBS-001).

## v5.18 — 2026-03-21

- Live auto-refresh: market-open drives 5s price tile + 60s KPI/intraday fragments.
- Static header split. get_live_price() + get_intraday_chart_data() added.
- Manual toggle removed.
- Fragment at module level (fixes timer reset).
- LIVE/CLOSED badge in sidebar.

## v5.19 — 2026-03-21

- Forecasting engine rebuild: polyfit replaced by Historical Simulation (2000 bootstrapped paths).
- Weinstein Stage + Elder Triple Screen veto.
- Unified verdict with conflict detection.
- Weekly accuracy calibration report on week summary page.

## v5.20 — 2026-03-21

- UX fix: header now shows unified verdict (not raw score signal). 44% of stock views were showing misleading BUY on WATCH/AVOID stocks.
- Added _detect_asset_class(), P/E suppressed for non-equity.
- Momentum Score labelled pre-regime-filter. 7 new HELP_TEXT entries (Weinstein, Elder, P(gain), HistSim, conflict, unified_verdict). render_dashboard computes verdict before header renders.

## v5.20.1 — 2026-03-21

- Hotfix: verdict_reason in compute_unified_verdict now contextualises score against verdict in plain English.
- Stage 2 + weak momentum now reads 'trend cycle healthy but technicals not supportive — wait for RSI/MACD to improve' instead of bare score number.

## v5.20.2 — 2026-03-21

- Hotfix: app.py — explicit get_price_data.clear() + get_ticker_info.clear() on ticker switch. cb increment alone was insufficient — new cb value could already exist in cache from prior fetch of same ticker.
- Fixes stale price/blank charts on first stock load.

## v5.21 — 2026-03-21

- Phase 2: Debt & Rates verdict suppression (RATES CONTEXT replaces BUY/SELL for yield instruments).
- Dynamic chart subplots — no blank MACD/RSI panels when indicators missing.
- Plain English header labels ('Trend and momentum agree' / 'Momentum signal adjusted').
- All 6 new HELP_TEXT keys wired to tooltips (weinstein_stage, elder_screen, p_gain, hist_sim, conflict, unified_verdict).
- Debt KPI panel shows yield context warning.

## v5.22 — 2026-03-23

- 4-state dashboard routing: stock (full dashboard), group (group overview — weekly heatmap + signals + top/bottom movers), market (market breadth by group), default (revamped week summary — multi-asset chart + navigation hints). render_market_overview + render_group_overview added to week_summary.py.

## v5.23 — 2026-03-24

- Portfolio Allocator: new portfolio.py (Mean-CVaR, Rockafellar-Uryasev 2000). 9 functions: data quality validator, log returns, winsorize (99th pctile), exponential-weighted bootstrap (2000 scenarios), cvxpy optimiser, efficient frontier, stability score, stress regime detection (VIX+correlation), regime conflict check. render_group_overview() gets 3-tab layout: Weekly Returns | Portfolio Allocator | Signal Summary.
- All CRITICAL+HIGH stress test fixes baked in: P1 VIX stress mode, M1 correlation crisis, D1 data quality validator, D3 winsorization, A1 exponential weighting, P4 leverage disclaimer, Layer 4 conflict check, post-cost return estimate, confidence band (P10-P90).

## v5.24 — 2026-03-26

- Lazy loading redesign (M0-M2): get_batch_data consolidates get_ticker_bar_data+get_group_data.
- Home page redesigned as Global Market Overview — removes render_week_summary call, adds _render_global_signals (@st.fragment), price snapshot (0-extra-fetch cache hit), _render_top_movers and _render_news_feed as @st.fragment. week_summary sections wrapped in @st.fragment: _index_perf_row, _nifty_heatmap, _sector_cards, _nifty_weekly_chart, _multi_asset_weekly_chart. render_group_overview uses get_batch_data.
- Cold-start API calls: ~100 tickers → 10 tickers.

## v5.25 — 2026-03-26

- M3: routing guard — grp_explicitly_selected flag prevents 49-ticker group heatmap from auto-firing on cold start. render_group_overview only fires when user explicitly clicks a group.
- Reset on market switch.
- M1b: cold-start warmth guards on _render_global_signals and _render_top_movers — fragments defer fetches until ticker bar has populated _ticker_cache. get_batch_data raises RuntimeError on empty result so failed fetches are not cached for 300s TTL. is_ticker_cache_warm() added to market_data.py.

## v5.26 — 2026-03-26

- Hotfix batch: is_ticker_cache_warm majority threshold (70%); double _yf_batch_download cold start; _ticker_cache_time TTL bug; yfinance 0.2.54 MultiIndex; pandas 3.0 chained assignment; indicators len guard; live_price empty series guard; compare safe_run; chunk gap 3s to 5s; backoff 5s to 10s; 2s cold-start delay; OHLCV retry button; _refresh_fragment removed; R8 EP updated.

## v5.27 — 2026-03-27

- Emergency fix: global 429 cooldown gate (_is_rate_limited, _set_rate_limited,.

## v5.28 — 2026-03-27

- Python 3.14 + dependency upgrade: streamlit 1.43.2->1.55.0,.

## v5.29 — 2026-03-27

- get_ticker_info: add _is_rate_limited() gate (was missing from v5.27 —.

## v5.30 — 2026-03-27

- styles.py: sidebar collapse button CSS updated for Streamlit 1.55.

## v5.31 — 2026-03-28

- P0 regulatory sprint (8 fixes, QA verified).

## v5.32 — 2026-03-29

- Data coherence + temporal labeling sprint (9 fixes, 11 new R23b checks).

## v5.33 — 2026-03-31

- Security, compliance & governance sprint (8 fixes, 10 new R25 checks).

## v5.34 — 2026-04-01

- Sprint manifest infrastructure + v5.33 doc debt backfill + observability dashboard + UX fixes.

## v5.34.1 — 2026-04-05

- Claude Code hook infrastructure sprint.

## v5.34.2 — 2026-04-05

- Regression hardening + sprint close for v5.34.1 CTO review fixes.

## v5.35 — 2026-04-06

- Launch readiness sprint.
- CEO sign-offs S-01 through S-05 executed.

## v5.35.1 — 2026-04-06


## v5.36 — 2026-04-07

