# CLAUDE.md — Global Stock Intelligence Dashboard
# Read this FULLY before touching any file in this repo.
# Last updated: 2026-03-27 (Session 008 — v5.27 DataManager M1)
# Dynamic session state: GSI_Session.json (see Gist URL at bottom)

---

## Project Overview

Multi-market stock intelligence dashboard built with Streamlit.
Entry point: `app.py` (root). 9 markets, 559 tickers, 38 groups, 4-tab per-stock dashboard.
Two repos — ALL active work is in the modular repo:

- **ACTIVE:** https://github.com/Tarun19k/stock-intelligence-test-1-vs
- **REFERENCE ONLY (monolith, do not edit):** https://github.com/Tarun19k/global-gsi-intelligence

---

## Run Commands

```bash
streamlit run app.py        # run the app locally
python3 regression.py       # MUST pass before any new work
```

Deploy: Streamlit Community Cloud (1GB RAM) + local dev.

---

## Environment

```
streamlit==1.43.2   yfinance==0.2.54    feedparser==6.0.11
plotly==5.24.1      pandas==2.2.3       numpy>=2.0.0
pytz==2024.2        requests==2.32.3    cvxpy==1.8.2
```

Runtime: Python 3.12.13 (pinned via runtime.txt). System deps: libopenblas-dev.

Streamlit 1.43 notes:
- `@st.fragment(run_every=N)` dims entire page during re-render — expected, not a bug
- `width='stretch'` correct for `st.dataframe`; do NOT pass to `st.plotly_chart`
- `st.rerun(scope='fragment')` raises StreamlitAPIException — use plain `st.rerun()`
- `_refresh_fragment` REMOVED in v5.26 — do not re-add

---

## Current State (v5.27 — 2026-03-27)

**Regression baseline: 374/374 PASS**

Key changes since v5.26:
- `data_manager.py` M1: skeleton + bypass mode + CircuitBreaker + all type definitions
- `regression.py` fix: R22 and R23 were dead code after `sys.exit()` — moved inside `run()`
- `regression.py`: R24 added (10 DataManager M1 contract checks)
- `regression.py`: `data_manager.py` added to PROJECT_FILES (R1–R8 now check it)
- v5.27 rate-limit gate already in place: global 429 cooldown (`_is_rate_limited`, `_set_rate_limited`, `_clear_rate_limit_state`) in `market_data.py`
- `get_ticker_bar_data_fresh` TTL raised from 10s → 60s (root cause of 429 death spiral)
- Nav page guards on `_render_global_signals` + `_render_top_movers` (fragment ghost fix)
- DataManager.bypass_mode() == True — pages still use market_data.py directly (M1 by design)

---

## File Structure

Safe rebuild order:

```
version.py              Changelog + CURRENT_VERSION. No logic.
tickers.json            Master ticker registry. Edit here, NEVER in config.py.
config.py               Constants hub. Re-exports GROUPS + VERSION_LOG.
utils.py                safe_run(), sanitise(), init_session_state().
styles.py               All CSS in CSS constant. inject_css() called once from app.py.
indicators.py           compute_indicators(df), signal_score(df, info), unified verdict.
market_data.py          All yfinance + RSS. Token bucket + global 429 gate + _ticker_cache.
data_manager.py         DataManager singleton. Circuit breakers. Type definitions.
                        Bypass mode active (M1). Pages NOT yet routed through it.
forecast.py             Forecast lifecycle. session_state as primary store.
portfolio.py            Mean-CVaR engine. No Streamlit calls.
pages/week_summary.py   Weekly summary + group/market overview.
pages/global_intelligence.py  Geopolitical topics + WorldMonitor link + watchlists.
pages/home.py           Ticker bar + homepage. 3 deferred @st.fragment sections.
pages/dashboard.py      4-tab stock dashboard: Charts | Forecast | Compare | Insights.
app.py                  Entry point. Routing. No _refresh_fragment.
```

---

## Rate Limiting Architecture

### Current (v5.27) — Token Bucket + Global 429 Gate + Module Cache
| Component | Detail |
|---|---|
| `_global_throttle()` | Token bucket: max=5, rate=0.4s. threading.Lock serialises all threads. |
| `_yf_batch_download()` | CHUNK=3, inter-chunk=5s, break on 429, stale cache fallback |
| `_is_rate_limited()` | Global cooldown gate — all fetches check this before touching yfinance |
| `_set_rate_limited()` | Engages cooldown on 429. Exponential backoff: 90s → 120s → 180s |
| `_clear_rate_limit_state()` | Resets backoff counter after clean batch |
| `_ticker_cache` | Module-level dict. Survives @st.cache_data evictions. Stale fallback. |
| `is_ticker_cache_warm()` | 70% majority threshold. Gates fragments on cold start. |
| Ticker bar TTL | 60s (raised from 10s — 10s was root cause of 429 death spiral on AWS IPs) |

### Planned (OPEN-007 — IN PROGRESS M1) — DataManager
M1 complete: data_manager.py skeleton + bypass mode + CircuitBreaker + type definitions.
M2 next: CacheManager (L2 SQLite + L3 _ticker_cache) + DataContract validator.
**Pages still use market_data.py directly. DataManager.bypass_mode() == True.**

---

## Key Entry Points

```
app.py              _is_market_open(country), _on_market_change()
pages/home.py       render_ticker_bar(cb), render_homepage(cb, market_open)
                    _render_global_signals()          # @st.fragment(run_every=60)
                    _render_top_movers(cb)            # @st.fragment(run_every=60)
                    _render_news_feed(cb)             # @st.fragment(run_every=300)
pages/dashboard.py  render_dashboard(ticker, name, country, cur_sym, info, df, cb, ...)
                    _make_live_price_fragment(...)    # @st.fragment(run_every=5s market only)
pages/week_summary.py render_week_summary, render_market_overview, render_group_overview
pages/global_intelligence.py render_global_intelligence(cur_sym, cb, market_open)
market_data.py      get_ticker_bar_data_fresh(tickers) [TTL=60s]
                    get_batch_data(tickers, period, interval, cache_buster) [TTL=300s]
                    get_price_data(ticker, period, interval, cache_buster) [TTL=300s]
                    get_ticker_info(ticker, cache_buster) [TTL=600s]
                    get_live_price(ticker) [TTL=5s]
                    get_intraday_chart_data(ticker) [TTL=60s]
                    get_top_movers(symbols, max_symbols, cache_buster) [TTL=300s]
                    get_news(feeds, max_n, cache_buster) [TTL=600s]
                    is_ticker_cache_warm(tickers) → bool
data_manager.py     get_datamanager() → DataManager          [@st.cache_resource singleton]
                    DataManager.bypass_mode() → bool
                    DataManager.is_healthy() → bool
                    DataManager.get_health() → HealthSnapshot
                    DataManager.fetch(ticker, DataType, Priority, ...) → DataResult
                    DataManager.fetch_batch(tickers, ...) → dict[str, DataResult]
                    DataManager.invalidate(ticker)           [replaces cache_buster in M4]
                    DataManager.invalidate_all()
                    DataManager.prefetch(tickers, DataType)
                    CircuitBreaker.allow_request() → bool
                    CircuitBreaker.record_success()
                    CircuitBreaker.record_failure()
indicators.py       compute_indicators(df), signal_score(df, info)
                    compute_weinstein_stage(df), compute_elder_screens(df)
                    compute_unified_verdict(sig, stage, elder, asset_class)
forecast.py         store_forecast, resolve_forecasts, render_forecast_accuracy
portfolio.py        check_data_quality, compute_log_returns, winsorize_returns
                    bootstrap_scenarios, optimise_mean_cvar, compute_efficient_frontier
                    detect_stress_regime, check_regime_conflicts
utils.py            safe_run(fn, context, default), sanitise(text, max_len)
                    sanitise_bold(text, max_len), init_session_state()
```

---

## DO NOT UNDO — Hard Rules

1. **Do NOT revert `forecast.py` to filesystem persistence.** Cloud wipes filesystem on redeploy.
2. **Do NOT remove `cache_buster: int = 0`** from market_data functions.
3. **Do NOT add `scope='fragment'` to `st.rerun()`.** StreamlitAPIException in 1.43.
4. **Do NOT move VERSION_LOG back into config.py.** In version.py by design.
5. **Do NOT move GROUPS back into config.py.** In tickers.json by design.
6. **Do NOT use Streamlit MPA as primary nav.** MPA sidebar hidden via CSS.
7. **Do NOT use `TATAMOTORS.NS`.** Delisted. Use `TMCV.NS` + `TMPV.NS`.
8. **Do NOT put CSS in `inject_css()` docstring.** All CSS inside `CSS` constant.
9. **Do NOT re-add `_refresh_fragment` to app.py.** Removed v5.26. Was a no-op.
10. **Do NOT pass `cache_buster=cb` to `get_news()`.** News is not stock-specific. Use 0.
11. **Do NOT route `get_news()` / RSS through DataManager.** RSS has no fallback chain
    and no circuit breaker. Lives in market_data.py with feedparser timeout. R24 enforces this.
12. **Do NOT instantiate DataManager directly.** Always use `get_datamanager()`.
    Direct instantiation bypasses @st.cache_resource and creates duplicate instances.
13. **Do NOT use a module-level variable for the DataManager singleton.**
    @st.cache_resource is the correct primitive. Module-level vars are not reliably
    shared across sessions on Streamlit Cloud.
14. **Do NOT import market_data from data_manager.py.** Circular import risk in M4.
    Source adapters own the market_data calls in M4+.
15. **Do NOT return None from any DataManager method.** Always return
    `DataResult(status=UNAVAILABLE)` via the `unavailable()` factory. R24 enforces this.
16. **Do NOT call DataManager.fetch() from pages before M4.** Returns UNAVAILABLE in M1–M3.
    Pages use market_data.py directly until M4 migration.

---

## Regression Suite

`python3 regression.py` — run from repo root. All checks must pass before any commit.

22 rule categories (R1–R22) + R23 (rate-limit gate) + R24 (DataManager M1 contracts).
**Important:** R22 and R23 were dead code (after `sys.exit()`) before Session 008 — now fixed.
R8 EP list: verify `_refresh_fragment` absent from app.py EP, `_make_live_price_fragment` present in dashboard EP.

---

## Open Items

| ID | Priority | Status | Task |
|---|---|---|---|
| OPEN-001 | HIGH | OPEN | git rm config_OLD.py + git rm --cached forecast_history.json |
| OPEN-002 | MED | OPEN | README update |
| OPEN-003 | MED | OPEN | Cross-session forecast persistence (Supabase) |
| OPEN-004 | LOW | OPEN | Extract SCORING_WEIGHTS to config |
| OPEN-005 | HIGH | OPEN | git rm config_OLD.py from repo root |
| OPEN-006 | MED | OPEN | Portfolio Allocator stability score UI + backtest |
| **OPEN-007** | **HIGH** | **IN PROGRESS — M1 complete** | DataManager: M1 skeleton done. M2 next: CacheManager + DataContract. |
| RISK-001 | MED | MONITOR | XSS: sanitise() all {ticker}/{name} in unsafe_allow_html f-strings |
| RISK-003 | LOW | MONITOR | safe_ticker_key() in _yf_download() before yf.download() |

---

## Session Manifest (Dynamic State)

**GSI_Session.json Gist:** https://gist.github.com/Tarun19k/7c894c02dad4e76fe7c404bf963baeab

To resume with Claude:
> "I am working on the Global Stock Intelligence Dashboard.
>  Here is CLAUDE.md and GSI_Session.json — read both fully before we proceed."
