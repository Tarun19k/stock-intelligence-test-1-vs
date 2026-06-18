# Graph Report - stock-intelligence-test-1-vs  (2026-06-18)

## Corpus Check
- 47 files · ~1,250,576 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1410 nodes · 2282 edges · 73 communities detected
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 259 edges (avg confidence: 0.77)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0d64d517`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 78|Community 78]]

## God Nodes (most connected - your core abstractions)
1. `GSI Dashboard` - 126 edges
2. `CacheManager` - 32 edges
3. `main()` - 22 edges
4. `Left Sidebar Navigation` - 22 edges
5. `Index Performance This Week` - 21 edges
6. `ok()` - 19 edges
7. `Sensex Index (211)` - 19 edges
8. `Portfolio Allocator View` - 19 edges
9. `Indian Market (NSE/BSE)` - 18 edges
10. `Forecast Table (Ticker / Made On / Due On / Horizon / P(Gain) / Status)` - 18 edges

## Surprising Connections (you probably didn't know these)
- `calc_5d_change()` --calls--> `_render_global_overview_prices()`  [INFERRED]
  utils.py → pages/home.py
- `get_batch_data()` --calls--> `render_group_overview()`  [INFERRED]
  market_data.py → pages/week_summary.py
- `DataType` --uses--> `TestCacheManagerMiss`  [INFERRED]
  data_manager.py → tests/test_data_manager_m2.py
- `DataType` --uses--> `TestCacheManagerHit`  [INFERRED]
  data_manager.py → tests/test_data_manager_m2.py
- `DataType` --uses--> `TestCacheManagerTTL`  [INFERRED]
  data_manager.py → tests/test_data_manager_m2.py

## Communities (79 total, 12 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (73): GSI Dashboard v5.36, Bug: Static Text with Delay Load, Multi-Asset Weekly Performance Bar Chart, Multi-Asset Weekly Return Bar Chart, Crude Oil WTI ($115), Crude WTI, Gold ($4,685), Week of 06 Apr – 07 Apr 2026 (current week) (+65 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (56): compute_correction_factor(), compute_indicators(), _compute_stock_scores(), fetch_topic_news(), get_accuracy_summary(), get_info(), _get_live_price_fast(), get_news() (+48 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (51): compute_correction_factor(), compute_indicators(), _compute_stock_scores(), fetch_topic_news(), get_accuracy_summary(), _get_live_price_fast(), get_news_headlines(), get_price_data() (+43 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (51): _market_status(), _next_open(), Price + daily % + 5-day weekly % cards for all ticker bar instruments.     batch, BUY/WATCH/AVOID + RSI for each global instrument.     Fetches 3mo data (separate, Home page = Global Market Overview.     Tier 1 (immediate): morning brief + mark, Fixed 36px ticker strip via window.parent iframe injection.     get_batch_data c, _render_global_overview_prices(), _render_global_signals() (+43 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (52): Wait for Price to Reclaim 50-Day Average, Wait for MACD Histogram to Turn Positive, Bearish Tide Badge, Bearish — Avoid Buying Card, Stage 4 Declining Detail Card, Stage 2 Oversold RSI — Low Risk Entry Consideration, SEBI Disclaimer Banner, Insights & Actions Tab (+44 more)

### Community 5 - "Community 5"
Cohesion: 0.04
Nodes (51): Refresh Data Button, App Version v5.36, Refresh Data Button, Commodities & Global Inflation, Compare Tab, Dark Theme UI, Dashboard Screenshots Strip, Important Disclaimer Section (+43 more)

### Community 6 - "Community 6"
Cohesion: 0.05
Nodes (50): After Costs Metric, After Costs Return Metric, Allocation Stability Indicator, Allocation Stability Indicator, Bank Nifty Ticker Price (52,716, +0.20%), Bharti Airtel Regime Conflict Signal, Bharti Airtel Signal Conflict (Allocator vs Technical), CAUTION Signal Badges (+42 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (48): All Risks Mitigated Status Banner, App Internals Section, App Version v5.38, Deploy Button, Estimated Tokens Column, Sub-sprint Column, Compliance Gates (Live Check), compliance_check.py File (+40 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (40): _detect_asset_class(), _graph_help(), _has_ohlcv(), _kpi(), _make_live_kpi_fragment(), _make_live_price_fragment(), Static header: stock identity + unified verdict badge + momentum score.     verd, Shared renderer — called by live fragment and closed-market fallback. (+32 more)

### Community 9 - "Community 9"
Cohesion: 0.07
Nodes (39): _get_dev_token(), _inline_compliance_check(), _market_status_rows(), _parse_audit_counts(), _parse_compliance_output(), _parse_loophole_log(), _parse_risk_counts(), _parse_risk_register() (+31 more)

### Community 10 - "Community 10"
Cohesion: 0.08
Nodes (38): _get_week_range(), _index_perf_row(), _multi_asset_weekly_chart(), _nifty_heatmap(), _nifty_weekly_chart(), Weekly calibration report for the Historical Simulation forecast engine.     Sho, Return (week_start, week_end, label, is_current) in IST., Default view — no market selected.     Shows a broad cross-market weekly pulse: (+30 more)

### Community 11 - "Community 11"
Cohesion: 0.17
Nodes (37): check_audit_trail(), check_baseline_staleness(), check_context_freshness(), check_decisions(), check_dependencies(), check_qa_brief(), check_regression_r10b(), check_session_json() (+29 more)

### Community 12 - "Community 12"
Cohesion: 0.08
Nodes (34): Global Trend Signals Section, GSI Dashboard Application v5.36, Home Screen Bottom Section, Latest Market News Section, Top Mover: AAPL (250.19, -3.25%), Top Mover: HINDUNILVR (2,110.60, +1.24%), Top Mover: INFY (1,339.40, +2.54%), Top Mover: TCS (2,539.80, +2.60%) (+26 more)

### Community 13 - "Community 13"
Cohesion: 0.08
Nodes (33): All Mitigated Success Banner, App Internals Page, App Internals Tab Bar, Cache Hits/Misses Detail (13 hits / 77 misses), Compliance Gates Section, Deploy Button, Fetch Latency Chart (last 20 samples), Metric: Avg Fetch Time (690.3 ms) (+25 more)

### Community 14 - "Community 14"
Cohesion: 0.07
Nodes (32): Bank Nifty Metric Card, Bar Chart Global Indices (Nifty/S&P/Nasdaq/FTSE/Hang Seng/Crude Oil/10Y UST), Dollar (USD/INR) Metric Card, Weekly Forecast Accuracy Report, Global Intelligence Navigation Item, Gold Metric Card, Group Selector, Index Performance This Week (+24 more)

### Community 15 - "Community 15"
Cohesion: 0.14
Nodes (11): CacheManager, Bounded LRU in-memory cache (L2).      Deployment note: Streamlit-specific.  Sin, Store result.  No-op if status == UNAVAILABLE.         Evicts the LRU entry if a, Remove all cache entries for this ticker across all DataTypes., _make_result(), Unit tests for DataManager M2 — CacheManager and DataContract.  Run: pytest test, TestCacheManagerHit, TestCacheManagerInvalidate (+3 more)

### Community 16 - "Community 16"
Cohesion: 0.09
Nodes (28): Accuracy Metrics Auto-Populate Note (after due dates pass), Forecast Table Column: Due On, First Resolution Date: 2026-04-13, Forecast Engine — Weekly Accuracy Report, Forecast Horizon 21 Days (1M), Forecast Horizon 63 Days (3M), P(Gain) Field — Probability of Gain, Forecast Status: Pending (+20 more)

### Community 17 - "Community 17"
Cohesion: 0.09
Nodes (27): Stress Regime Detected Alert Banner, Daily Return Axis (y-axis), Daily Volatility Axis (x-axis), Risk Profile Selector (Conservative / Balanced / Aggressive), Portfolio Allocator Feature, Allocation Stability Indicator (STABLE), Portfolio Size Input (10000), Expected Annual Return (+7.8%) (+19 more)

### Community 18 - "Community 18"
Cohesion: 0.11
Nodes (27): Asian Overnight Market Data, F&O Data Feature, Global Cues Context, Global Market Overview, GSI Home Screen, India Market Status (CLOSED), Live Signals Feature, Asia Market Coverage (+19 more)

### Community 19 - "Community 19"
Cohesion: 0.09
Nodes (24): Compliance Checks, Dashboard Tabs, Data-as-of Disclosure, Error Log Section, Green Pass Indicators, GSI QA Audit Report v5.36, GSI Version 5.36, Indian Equities Market (+16 more)

### Community 20 - "Community 20"
Cohesion: 0.09
Nodes (13): DataManager, HealthSnapshot, Factory for UNAVAILABLE DataResult.     Use this everywhere — never construct Da, Point-in-time health state.  Consumed by sidebar observability panel (M6).     R, True if at least one source breaker is CLOSED and DataManager is not in bypass., Always safe to call — never raises.         Returns a snapshot of current health, Direct access to a source's circuit breaker. Used by source adapters (M4/M5)., Synchronous data fetch.  Returns DataResult — never raises.         M1: always r (+5 more)

### Community 21 - "Community 21"
Cohesion: 0.38
Nodes (20): bg(), blank_slide(), box(), divider(), label(), pill(), GSI Dashboard — Community Launch Pitch Deck Run: python3 docs/build_pitch_deck.p, Legal / disclaimer — required on all decks (+12 more)

### Community 22 - "Community 22"
Cohesion: 0.14
Nodes (22): Candlestick Chart, MACD (Daily) Chart, Price Chart with Bollinger Bands, RSI (14) Chart, Volume Chart, Chart Date Range: Nov 2025 to Apr 2026, India Market, Bollinger Bands Indicator (+14 more)

### Community 23 - "Community 23"
Cohesion: 0.1
Nodes (17): calc_5d_change(), info_tip(), log_error(), Label + ℹ️ icon with native HTML title= tooltip (no JS, XSS-safe).     Use insid, <p class=section-title> with inline ℹ️ tooltip. Drop-in for bare section titles., Shared 5-day percentage change utility — call this EVERYWHERE a 5-day     or wee, Escape HTML special chars before injecting into unsafe_allow_html blocks., Like sanitise() but preserves <b> and </b> for emphasis in insight cards.     Pr (+9 more)

### Community 24 - "Community 24"
Cohesion: 0.17
Nodes (18): compute_correction_factor(), get_accuracy_summary(), get_pending_forecast_summary(), get_weekly_accuracy_report(), load_forecast_history(), Check all pending forecasts whose due date has passed and mark them     resolved, Auto-correction factor.     If mean accuracy < 95 %, return the mean of actual/f, Return accuracy stats dict for display in the Forecast tab. (+10 more)

### Community 25 - "Community 25"
Cohesion: 0.12
Nodes (15): info_tip(), log_error(), Label + ℹ️ icon with native HTML title= tooltip (no JS, XSS-safe).     Use insid, <p class=section-title> with inline ℹ️ tooltip. Drop-in for bare section titles., Escape HTML special chars before injecting into unsafe_allow_html blocks., Like sanitise() but preserves <b> and </b> for emphasis in insight cards.     Pr, Sanitise ticker before use as dict/JSON key. Allows A-Za-z0-9.-^= only., Validate URL is http/https and not pointing at internal/local network. (+7 more)

### Community 26 - "Community 26"
Cohesion: 0.18
Nodes (11): Enum, CircuitState, DataType, Priority, data_manager.py — Global Stock Intelligence Dashboard DataManager: resilient dat, ResultStatus, validate(), _validate_batch() (+3 more)

### Community 27 - "Community 27"
Cohesion: 0.24
Nodes (16): _graph_help(), _has_ohlcv(), _kpi(), _live_kpi_panel(), Fragment: re-renders live price KPIs every 60 s.     Charts and analysis section, Return True only if df has all required OHLCV columns as proper Series., Safely return df['Close'] as a Series, or default., KPI tile — tip= adds hover tooltip on card and ℹ️ icon on label. (+8 more)

### Community 28 - "Community 28"
Cohesion: 0.12
Nodes (17): 4-Tab Stock Dashboard Feature, Forecast Tracker Feature, Global Intelligence Feature, Live Ticker Bar Feature, Week Summary Feature, Everything in One Place Features Section, Asia-Pacific Market, China Market (+9 more)

### Community 29 - "Community 29"
Cohesion: 0.16
Nodes (13): CustomLogger, ApprovalLayer, _classify(), _macos_approve(), _osascript(), Run an AppleScript snippet and return (stdout, returncode)., Show a native macOS dialog. Returns (choice, alt_model).     choice: "approve" |, Interactive terminal approval with timeout.     Returns (choice, alt_model). (+5 more)

### Community 30 - "Community 30"
Cohesion: 0.2
Nodes (3): _make_ohlcv(), TestDataContractBATCH, TestDataContractOHLCV

### Community 31 - "Community 31"
Cohesion: 0.24
Nodes (14): _all_commits(), check_commits(), _full_message(), _get_note(), _git(), main(), _mark_reviewed(), Return the full commit message for a given SHA. (+6 more)

### Community 32 - "Community 32"
Cohesion: 0.2
Nodes (13): _market_status(), _next_open(), Fragment wrapping all DYNAMIC home-page sections:     morning brief status, mark, Called from app.py routing — renders the Home page body., Renders a fixed 36px ticker strip pinned to the very top of the page.      Strat, render_homepage(), _render_live_section(), _render_market_status_row() (+5 more)

### Community 33 - "Community 33"
Cohesion: 0.16
Nodes (15): ADX Trend Metric (31.0), Algorithmic Signal Panel, ATR Volatility Metric (₹34.76), Bollinger Width Metric (8.7%), MACD Daily Chart, MACD Metric (-6.775), Price Bollinger Bands Chart, RSI (14) Chart (+7 more)

### Community 34 - "Community 34"
Cohesion: 0.15
Nodes (5): DataContract, Wire-level shape validator for each DataType.      Validates that data received, SourceTag, TestDataContractINFO, TestDataContractLIVE

### Community 35 - "Community 35"
Cohesion: 0.22
Nodes (13): classify(), _load_model_display_names(), main(), parse_backlog(), _parse_done_ids(), parse_in_progress(), Classify a backlog item into an execution tier.      Priority order (first match, Extract items from the '### In Progress' table in GSI_SPRINT.md.     These are i (+5 more)

### Community 36 - "Community 36"
Cohesion: 0.2
Nodes (13): _market_of(), Personalised AI career & investment action cards., Render one expandable topic card with chain + news + watchlist., Horizontal cascade of geopolitical impact nodes., Main entry point — called from app.py routing., Infer market from ticker suffix for watchlist filtering (OPEN-014)., Live mini price badges for a topic watchlist., render_global_intelligence() (+5 more)

### Community 37 - "Community 37"
Cohesion: 0.15
Nodes (14): Breadcrumb: Current Week > India > Nifty 50, Weekly Returns All Stocks Bar Chart, Market Filter (India), Nifty 50 Group, 49 Stocks Tracked Label, Sidebar Group Selector, Sidebar Stock Selector, No Stock Selected State (showing weekly summary) (+6 more)

### Community 38 - "Community 38"
Cohesion: 0.14
Nodes (14): Refresh Data Button, Search Filter (Company Name or Symbol), Market CLOSED Status, Market CLOSED Badge, Market CLOSED Indicator, Nav: Dashboard, Nav: Global Intelligence, Nav: Home (+6 more)

### Community 39 - "Community 39"
Cohesion: 0.27
Nodes (13): Alignment Indicator, BUY Signal, Composite Momentum Score, Elder Triple Screen, Documented Override Hierarchy, RSI, MACD, Volume, ATR Indicators, Signal Engine, Stage 2 Advancing (+5 more)

### Community 40 - "Community 40"
Cohesion: 0.17
Nodes (13): Dashboard Screenshot Preview, Elder Triple Screen Framework, Weinstein Stage Analysis Framework, ATR Indicator, MACD Indicator, RS (Relative Strength) Indicator, Landing Page Hero Section, View on GitHub Nav Link (+5 more)

### Community 41 - "Community 41"
Cohesion: 0.17
Nodes (7): CircuitBreaker, get_datamanager(), Per-source circuit breaker.  Three-state machine:          CLOSED ──(N consecuti, Returns True if a request should proceed.         CLOSED  → always True., Call after any successful fetch from this source., Call after any failed fetch from this source., Returns the shared DataManager singleton.      @st.cache_resource ensures exactl

### Community 42 - "Community 42"
Cohesion: 0.24
Nodes (11): _extract_names(), _load_yaml(), main(), parse_config(), query_health(), Parse config.yaml and return [(alias, provider_model), ...] in order.     Return, GET {proxy_url}/health with Bearer auth.     Returns parsed JSON dict on success, Extract model name strings from a health endpoint list.     LiteLLM may return d (+3 more)

### Community 43 - "Community 43"
Cohesion: 0.23
Nodes (10): Render one expandable topic card with chain + news + watchlist., Horizontal cascade of geopolitical impact nodes., Main entry point — called from app.py routing., Live mini price badges for a topic watchlist., Personalised AI career & investment action cards., render_global_intelligence(), _render_impact_chain(), _render_next_steps_ai() (+2 more)

### Community 44 - "Community 44"
Cohesion: 0.21
Nodes (12): 52-Week High Price Reference, 52-Week Low Price Reference, Crude WTI Price Widget, Declining Trend Signal (Stage 4 — price 9.6% below 50-week average), Gold Price Widget, Macro Market Data, Price Change Indicator, Search UI Settled State (+4 more)

### Community 45 - "Community 45"
Cohesion: 0.29
Nodes (10): get_news(), get_price_data(), get_ticker_info(), get_top_movers(), _is_allowed_rss(), _normalize_df(), Return clean float Series from Close; guards MultiIndex yfinance output., Guarantee df always has string columns: Open High Low Close Volume.     Handles (+2 more)

### Community 46 - "Community 46"
Cohesion: 0.29
Nodes (10): get_news(), get_price_data(), get_ticker_info(), get_top_movers(), _is_allowed_rss(), _normalize_df(), Return clean float Series from Close; guards MultiIndex yfinance output., Guarantee df always has string columns: Open High Low Close Volume.     Handles (+2 more)

### Community 47 - "Community 47"
Cohesion: 0.18
Nodes (11): Group-Level Sector Selection Feature, Auto & EV Sector Group, Banks & Finance Sector Group, FMCG & Consumer Sector Group, IT & Technology Sector Group, Nifty Next 50 Group, Pharma & Healthcare Sector Group, Sensex 30 Group (+3 more)

### Community 48 - "Community 48"
Cohesion: 0.31
Nodes (9): build(), extract_dnu_rules(), find_repo_root(), item_label(), Run all 75 validation checks. Returns list of failure strings., Pull DO NOT UNDO rules verbatim from CLAUDE.md — never drift from source., Build content string from all sources., run() (+1 more)

### Community 49 - "Community 49"
Cohesion: 0.38
Nodes (10): compute_correction_factor(), get_accuracy_summary(), load_forecast_history(), forecast.py, Render accuracy tracking panel — only function here that calls st.*, # NOTE: render_forecast_accuracy is the only function here that calls st.*, render_forecast_accuracy(), resolve_forecasts() (+2 more)

### Community 50 - "Community 50"
Cohesion: 0.38
Nodes (9): _persona_card(), _render_allocation_brief(), _render_asset_input(), _render_conflict_banner(), _render_council_grid(), render_council_review(), _render_header(), _render_mode_selector() (+1 more)

### Community 51 - "Community 51"
Cohesion: 0.31
Nodes (10): AI & Job Markets, China Slowdown & Trade Shifts, Geopolitical & Technology Intelligence, Global Intelligence Centre, Impact Chains, Market Linkages, US Rate Cycle & Fed Policy, West Asia Conflict (+2 more)

### Community 52 - "Community 52"
Cohesion: 0.22
Nodes (9): Crude WTI Price Live, Gold Price Live, USD/INR FX Rate Live, Bank Nifty Index Live Price, Dow Jones Index Live Price, Hang Seng Index Live Price, Nifty 50 Index Live Price, Sensex Index Live Price (+1 more)

### Community 53 - "Community 53"
Cohesion: 0.36
Nodes (7): _check_deps_current(), _check_jsonl_tier(), _git_last_commit_date(), main(), Return YYYY-MM-DD of the most recent commit touching path, or '' if unknown., Pass if requirements.txt was NOT committed more recently than GSI_DEPENDENCIES.m, C11 — latest token-burn-log.jsonl entry must have tier field in every items[] ob

### Community 54 - "Community 54"
Cohesion: 0.36
Nodes (7): chk(), regression.py, regression.py — GSI Regression & Validation Suite Run from project root: python, R-ZIP · KI-014: Re-read packaged zip from disk and run full suite.     Catches f, report(), run(), verify_zip()

### Community 55 - "Community 55"
Cohesion: 0.36
Nodes (6): chk(), regression.py — GSI Regression & Validation Suite Run from project root: python, R-ZIP · KI-014: Re-read packaged zip from disk and run full suite.     Catches f, report(), run(), verify_zip()

### Community 56 - "Community 56"
Cohesion: 0.29
Nodes (8): Global Intelligence Dashboard Tab, Global Intelligence Feature, Market Groups / Sections, Multi-Market Coverage, News Article Cards, Global Market News Section, Market Sentiment Indicators, Ticker / Symbol Tags on News Cards

### Community 57 - "Community 57"
Cohesion: 0.43
Nodes (5): chk(), R-ZIP · KI-014: Re-read packaged zip from disk and run full suite.     Catches f, report(), run(), verify_zip()

### Community 58 - "Community 58"
Cohesion: 0.4
Nodes (4): compute_indicators(), Add RSI, MACD, Bollinger, SMA, ATR, ADX, Stoch, OBV, VolumeMA to df., Compute composite signal score (0–100) from latest indicator row.     Returns di, signal_score()

### Community 60 - "Community 60"
Cohesion: 0.5
Nodes (3): DataResult, Returns DataResult if the entry exists (FRESH or STALE), None if not found., Every DataManager response is a DataResult.     data is None if and only if stat

### Community 64 - "Community 64"
Cohesion: 0.67
Nodes (3): Deploy Button, Overflow Menu (Three Dots), Top Bar

## Knowledge Gaps
- **523 isolated node(s):** `R-ZIP · KI-014: Re-read packaged zip from disk and run full suite.     Catches f`, `Return the forecast history dict.     Primary store: st.session_state[_SS_KEY].`, `Persist the forecast history dict.     Always writes to session_state (works on`, `Record a new forecast entry (one per ticker per day).     simulation: optional d`, `Check all pending forecasts whose due date has passed and mark them     resolved` (+518 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GSI Dashboard` connect `Community 5` to `Community 0`, `Community 4`, `Community 6`, `Community 7`, `Community 12`, `Community 16`, `Community 19`, `Community 22`, `Community 28`, `Community 33`, `Community 37`, `Community 38`, `Community 39`, `Community 40`, `Community 44`, `Community 47`, `Community 51`, `Community 52`, `Community 56`, `Community 64`, `Community 66`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Why does `Nifty 50 (2,716 +0.20%)` connect `Community 0` to `Community 17`, `Community 18`, `Community 5`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Why does `Streamlit Application` connect `Community 19` to `Community 5`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `GSI Dashboard` (e.g. with `Stock Search Feature` and `Reliance Industries`) actually correct?**
  _`GSI Dashboard` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `CacheManager` (e.g. with `.test_get_returns_none_on_empty_cache()` and `.test_get_returns_none_for_different_ticker()`) actually correct?**
  _`CacheManager` has 24 INFERRED edges - model-reasoned connections that need verification._
- **What connects `R-ZIP · KI-014: Re-read packaged zip from disk and run full suite.     Catches f`, `Return the forecast history dict.     Primary store: st.session_state[_SS_KEY].`, `Persist the forecast history dict.     Always writes to session_state (works on` to the rest of the system?**
  _523 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06 - nodes in this community are weakly interconnected._