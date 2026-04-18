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
              "Regression baseline: 427 pre-sprint (450 total checks mid-sprint including 23 R27 checks)."},
    {"version": "v5.34.2", "date": "2026-04-05",
     "notes": "Regression hardening + sprint close for v5.34.1 CTO review fixes. "
              "R28: 5 hook infrastructure existence checks added — pre_commit.sh, pre_push.sh, "
              "post_edit.sh, compliance_check.py, settings.json hooks block. Baseline 427→432. "
              "CTO review fixes applied (v5.34.1): C-1 sync_docs.py exit code (1 on issues, not 0); "
              "C-2 observability.py path (dashboard.py→pages/dashboard.py); "
              "M-1 git rev-parse replaces CLAUDE_PROJECT_DIR in all hooks (permanent, env-var-free); "
              "M-2 compliance_check.py __main__ guard (prevents R1 syntax check breakage); "
              "M-4 settings.json Write(*.sh) removed (overbroad permission). "
              "GSI_LOOPHOLE_LOG.md Class 2 added (governance script with hardcoded wrong path). "
              ".gitignore: RALPH_PROMPT.md + .claude/ralph-loop.local.md added. "
              "Regression baseline: 432/432 PASS."},
    {"version": "v5.35", "date": "2026-04-06",
     "notes": "Launch readiness sprint. CEO sign-offs S-01 through S-05 executed. "
              "S-01: WorldMonitor CSP stopgap — link button already implemented; "
              "ADR-022 formal decision record added to GSI_DECISIONS.md. "
              "S-02: docs/index.html — GitHub Pages one-page landing site. Dark-theme, "
              "mobile-responsive, SEBI disclaimer, 6-feature grid, 9-market coverage, "
              "3 screenshot placeholder slots (replace when screenshots available). "
              "S-03: streamlit-analytics2 integrated in app.py (fail-safe try/except import). "
              "requirements.txt updated. R29 regression check added (433/433 baseline). "
              "S-04: docs/social-media-guidelines.md — SEBI Finfluencer rules, prohibited content, "
              "platform-specific rules. GSI_RISK_REGISTER.md RISK-L04 Open → Mitigated. "
              "Regression baseline: 432→433 PASS (R29 analytics import check added)."},
    {"version": "v5.35.1", "date": "2026-04-06",
     "notes": ("Post-sprint hotfix + governance improvements. "
               "Fixes: safe_ticker_key now allows & (M&M.NS was stripped to MM.NS — delisted). "
               "tickers.json: AMBUJACEMENT→AMBUJACEM typo; Zomato + Paytm removed from IT & Technology (misclassified — food delivery / fintech). "
               "Governance: CLAUDE.md Rule 8 (parallel agent discipline — no git in worktree agents); "
               "sprint close protocol step 0 (both meta.current_app_version AND current_version must be updated before sync_docs). "
               "Sprint planning: 9-item flat cap → tiered 3-lane budget (≤6 seq, ≤6 parallel, ≤4 risky). "
               "Manifest template: token_budget + token_optimisations fields with quality floor guardrails. "
               "Regression baseline: 433/433 PASS (unchanged).")},
    {"version": "v5.36", "date": "2026-04-07",
     "notes": ("Post-Launch Hardening sprint (session_019). "
               "PROXY-01–07: litellm proxy infrastructure hardening. "
               "classifier_keywords.py: single source of truth for task-classification keyword lists (approval_hook + sprint_planner import from it). "
               "approval_hook.py: PROXY-02 fallback transparency (async_success_callback logs model substitutions); "
               "PROXY-07 tool-use guard (tools detected → force deep-reasoning; Groq does not support tool_use). "
               "sprint_planner.py: PROXY-01 shared keywords import; PROXY-04 optional Depends column; "
               "PROXY-05 staleness check via git log age (_sprint_file_age_days); YELLOW NameError bugfix. "
               "validate_models.py: PROXY-06 --spend flag (LiteLLM /spend endpoint, per-provider cost table). "
               "review_gate.py: PROXY-03 [proxy:model] commit tag convention; unreviewed proxy commit gate (exit 1). "
               "D-02 bench: _calc_roe() self-calculates ROE from netIncomeToCommon/bookValue/sharesOutstanding (yfinance returnOnEquity is unreliable). "
               "OPEN-006: portfolio stability score UI in week_summary.py (10× ±5% perturbation test; KPI card + per-stock weight sensitivity). "
               "EQA-41: forecast accuracy calibration Plotly bar chart with dotted reference baselines. "
               "PROXY-08 parked: env-var lifecycle fix (vars locked at process launch; two-launch sequence documented). "
               "Regression baseline: 434/434 PASS (unchanged from v5.35.1 governance patch).")},
    {"version": "v5.37", "date": "2026-04-14",
     "notes": ("SEBI compliance + governance sprint (session_025/026). "
               "OPEN-027/df01: pages/home.py — period 1mo→3mo (3 call sites) + SEBI caption in _render_global_signals(). "
               "OPEN-029: pages/dashboard.py — SEBI caption added after _render_header_static() verdict badge. "
               "OPEN-022: pages/week_summary.py — SEBI captions in Signal Summary tab + Portfolio Allocator table. "
               "OPEN-028: pages/global_intelligence.py — SEBI caption + BUY/WATCH/AVOID verdict badges in _render_watchlist_badges(). "
               "df-03: week_summary.py Portfolio Allocator — data-as-of timestamp (6-month price history · Data as of [latest close date]). "
               "df-08: home.py Top Movers — temporal scope caption (previous close → latest close). "
               "OPEN-023: litellm-proxy/config.yaml + sprint_planner.py — hf-code model name fixed to groq/qwen-qwq-32b. "
               "OPEN-025: portfolio.py + week_summary.py — UNSTABLE threshold aligned to >= 15 in code, comment, and UI. "
               "df-02: market_data.py — DEFAULT_NEWS_FEEDS constant with ET Markets + Reuters feeds (Al Jazeera general replaced). "
               "df-05: global_intelligence.py — macro analysis last-reviewed caption added. "
               "OPEN-026: CLAUDE.md EP tables + regression.py R8 — compute_stability_score + _render_forecast_accuracy_report added. "
               "Regression baseline: 436/436 PASS (stable base; sprint R27 checks inactive post-close).")},
    {"version": "v5.37.1", "date": "2026-04-14",
     "notes": ("Hotfix (session_026 QA). "
               "market_data.py: _ticker_cache is now period-aware. "
               "Root cause: _yf_batch_download served 5d DataFrames (from ticker-bar warmup) for "
               "3mo requests — tickers were 'fresh' in module cache regardless of period. "
               "len(df) < 10 check in _render_global_signals() → 'Computing...' stuck for "
               "whichever tickers were warm when the 70% threshold fired. "
               "Fix: added _ticker_cache_period dict (sym→period); fresh-serve check now "
               "requires period match. Stale 429-fallback path unaffected. "
               "Regression baseline: 444/444 PASS (unchanged).")},
    {"version": "v5.38", "date": "2026-04-14",
     "notes": ("Governance & observability sprint (session_027). "
               "Regression: R33 (no raw Momentum score in _render_header_static, scoped to function body), "
               "R34 (_ticker_cache_period module-level dict), R35 (token-burn-log COMPLETE gate). "
               "R27 extended: Pass 3 structural quality gates + COMPLETE phase WIP-IDLE check. "
               "R31 extended: N/A reason required. compliance_check.py: C10 SEBI disclaimer in week_summary.py (10 checks). "
               "Policy 8 Token Burn Log: est-vs-actual token dataset; token-burn-log.jsonl + analyze_token_burns.py. "
               "sprint-monitor.md: Playwright hard gate (playwright-done/playwright-defer), Step 0 sprint-open. "
               "new-session.md: ACTIVE resume writes minimal RESUME-tagged snapshot. "
               "observability.py Phase 1: 5 feed parsers + Sprint Monitor + Risk & Compliance tabs. "
               "Regression baseline: 439/439 PASS (always-on; R33+R34 added).")},
    {"version": "v5.39", "date": "2026-04-17",
     "notes": ("Data Layer Hardening sprint (session_028). "
               "DataManager M1 critical bug fixes: lock-ordering deadlock in get_health(), "
               "empty _breakers emergency fallback, bypass_mode @property, fetched_wall_time on DataResult. "
               "market_data.py: get_ticker_info _info_cache stale fallback — fundamentals survive 429 cooldown. "
               "observability.py: Plotly bar opacity fix (marker=dict) — Sprint Monitor chart error resolved. "
               "DataManager M2: CacheManager (bounded LRU L2, 200 entries, TTL per DataType) + "
               "DataContract (wire-level shape validator, 5 DataTypes) wired into DataManager. "
               "R24.M2: 6 new regression checks for CacheManager + DataContract. "
               "DataManager M3 (worker thread) explicitly deferred — Vercel Workflow DevKit territory. "
               "Closed OPEN-027/028/029 (resolved v5.37, stale in docs). "
               "Regression baseline: 452/452 PASS (446 + 6 R24.M2 checks).")},
    {"version": "v5.40", "date": "2026-04-18",
     "notes": ("Token optimization infrastructure sprint (session_030). "
               "T1/T2/T3 tier classification system: T1=doc/single .py ≤20 lines, "
               "T2=multi-section/2-file coherence, T3=new subsystem/≥43k seq est. "
               "Rule 18: Haiku-tier tasks are never subagent-routed; break-even threshold = 43k sequential est. "
               "R36: IN_PROGRESS manifest items must have tier field (T1/T2/T3). "
               "R37: T1 .py items must appear in GSI_QA_STANDARDS.md test brief (COMPLETE gate). "
               "R38: T1 items cannot touch signal-path files (indicators.py, market_data.py, dashboard.py). "
               "C11: latest token-burn-log.jsonl entry must have tier field in all items[]. "
               "token-burn-log.jsonl schema_version 2: adds tier, execution.actual_mode, "
               "est_input_tokens, est_output_tokens, actual_input_tokens, actual_output_tokens per item. "
               "analyze_token_burns.py: variance_alerts() function — flags sprints and items >1.5× est. "
               "ADR-030: T1/T2/T3 decision record + calibrated multipliers (Haiku 0.87×, Sonnet 0.97×, "
               "Haiku subagent 7-11× BANNED, Sonnet subagent 1.4× ≥43k only). "
               "token-model-rules.md updated: calibrated multipliers, T1/T2/T3 table, Sprint Budget Guide. "
               "close-session.md: new /close-session command writes session_breadcrumb.json before /clear — "
               "enables 5-9k lean startup vs 35-50k /new-session on deliberate clears. "
               "Regression baseline: 451/451 PASS (always-on; R36/R37/R38 sprint-active only).")}
]

CURRENT_VERSION: str = VERSION_LOG[-1]["version"]