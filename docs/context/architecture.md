# GSI Architecture Reference
# Read when making structural changes. Verify entry points against source before trusting — this file can lag code (see OPEN-026).

## Streamlit 1.55 Runtime Constraints
- `@st.fragment(run_every=N)` dims entire page during re-render — expected, not a bug
- `use_container_width=True` correct for `st.dataframe`; do NOT use `width='stretch'`
- `width='content'` valid on `st.dataframe` in 1.52+ (content-width mode)
- `st.rerun(scope='fragment')` raises StreamlitAPIException — use plain `st.rerun()`
- `st.plotly_chart` uses `config={'responsive': True}` — `**kwargs` deprecated in 1.50
- WorldMonitor cannot embed via iframe — CSP `frame-ancestors: 'self'` blocks *.streamlit.app (ADR-022)

## Safe Rebuild Order
```
version.py              Changelog + CURRENT_VERSION. No logic.
tickers.json            Master ticker registry. Edit here, NEVER in config.py.
config.py               Constants hub. Re-exports GROUPS + VERSION_LOG.
utils.py                safe_run(), sanitise(), init_session_state().
styles.py               All CSS in CSS constant. inject_css() called once from app.py.
indicators.py           compute_indicators(df), signal_score(df, info), unified verdict.
market_data.py          All yfinance + RSS. Token bucket + _ticker_cache + warmth guard.
data_manager.py         DataManager M2: CircuitBreaker + CacheManager. Bypass mode until M4.
forecast.py             Forecast lifecycle. session_state as primary store.
portfolio.py            Mean-CVaR engine. No Streamlit calls.
pages/week_summary.py   Weekly summary + group/market overview.
pages/global_intelligence.py  Geopolitical topics + WorldMonitor link + watchlists.
pages/home.py           Ticker bar + homepage. 3 deferred @st.fragment sections.
pages/dashboard.py      4-tab stock dashboard: Charts | Forecast | Compare | Insights.
pages/observability.py  Founder-only App Health + Program dashboard. DEV_TOKEN gated.
app.py                  Entry point. Routing. No _refresh_fragment.
regression.py           Regression suite. Must pass before every commit.
compliance_check.py     Pre-push gate. Run before git push.
```

## Key Entry Points
**Verify these against source before using — OPEN-026 documents known drift.**

```
app.py              _is_market_open(country), _on_market_change()
pages/home.py       render_ticker_bar(cb), render_homepage(cb, market_open)
                    _render_global_signals()          # @st.fragment(run_every=60)
                    _render_top_movers(cb)            # @st.fragment(run_every=60)
                    _render_news_feed(cb)             # @st.fragment(run_every=300)
pages/dashboard.py  render_dashboard(ticker, name, country, cur_sym, info, df, cb, ...)
                    _make_live_price_fragment(...)    # @st.fragment(run_every=5s market only)
pages/week_summary.py render_week_summary, render_market_overview, render_group_overview
                    _render_forecast_accuracy_report()
pages/global_intelligence.py render_global_intelligence(cur_sym, cb, market_open)
pages/observability.py render_observability() — DEV_TOKEN gated, MPA direct URL only
market_data.py      get_ticker_bar_data_fresh(tickers) [TTL=10s]
                    get_batch_data(tickers, period, interval, cache_buster) [TTL=300s]
                    get_price_data(ticker, period, interval, cache_buster) [TTL=300s]
                    get_ticker_info(ticker, cache_buster) [TTL=600s]
                    get_live_price(ticker) [TTL=5s]
                    get_intraday_chart_data(ticker) [TTL=60s]
                    get_top_movers(symbols, max_symbols, cache_buster) [TTL=300s]
                    get_news(feeds, max_n, cache_buster) [TTL=600s]
                    is_ticker_cache_warm(tickers) → bool
                    get_health_stats() → dict
                    get_rate_limit_state() → dict
indicators.py       compute_indicators(df), signal_score(df, info)
                    compute_weinstein_stage(df), compute_elder_screens(df)
                    compute_unified_verdict(sig, stage, elder, asset_class)
                    compute_stability_score(df)
forecast.py         store_forecast, resolve_forecasts, render_forecast_accuracy
portfolio.py        check_data_quality, compute_log_returns, winsorize_returns
                    bootstrap_scenarios, optimise_mean_cvar, compute_efficient_frontier
                    detect_stress_regime, check_regime_conflicts, compute_stability_score
utils.py            safe_run(fn, context, default), sanitise(text, max_len)
                    sanitise_bold(text, max_len), init_session_state()
```

## Rate Limiting Architecture (current — v5.26)
| Component | Detail |
|---|---|
| `_global_throttle()` | Token bucket: max=5, rate=0.4s. threading.Lock serialises all threads. |
| `_yf_batch_download()` | CHUNK=3, inter-chunk=5s, rate-limit backoff=10s, cold-start delay=2s |
| `_ticker_cache` | Module-level dict. Survives @st.cache_data evictions. Stale fallback. |
| `_ticker_cache_period` | Parallel dict: sym → period string last fetched. |
| `is_ticker_cache_warm()` | 70% majority threshold. Gates fragments on cold start. |

OPEN-007-M3: SQLite + priority queue planned but deferred — Vercel Workflow DevKit replaces this.

## Code Anti-Patterns
Patterns that have caused production bugs. Check before implementing anything in these areas.

| Anti-pattern | Effect | Correct pattern |
|---|---|---|
| `st.expander(expanded=False)` for primary content | Page looks empty | `expanded=True` for all primary content |
| `"Live Headlines"` without 48h freshness check | Stale content as current | Gate on `_age_h < 48` |
| `pandas>=3.0.0` in requirements.txt | pip/uv ResolutionImpossible | Use `pandas>=1.4.0` |
| Checking `dashboard.py` for strings that live in `indicators.py` | False regression passes | Check the file where the logic lives |
| Equal weight for conflicting signals without arbitration label | User acts on wrong signal | Override label mandatory |
| Same metric calculated inline in 2+ page files | Values diverge silently | Extract to `utils.py` |
| `"Real-time"` / `"Live"` label on yfinance data | 15–20 min delay — false claim | Gate on `market_open` bool + timestamp |
| Sharing a live signal result on social media | SEBI finfluencer rules | Screenshots of methodology only — never live signal outputs |
