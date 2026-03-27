# CLAUDE.md — Global Stock Intelligence Dashboard
# Read this FULLY before touching any file in this repo.
# Last updated: 2026-03-27 (Session 007 — v5.26 hotfix batch)
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
python3 regression.py       # MUST pass (323/323) before any new work
```

Deploy: Streamlit Community Cloud (1GB RAM) + local dev.

---

## Environment

```
streamlit==1.55.0   yfinance==1.2.0     feedparser==6.0.11
plotly==5.24.1      pandas>=1.4.0       numpy>=2.0.0
pytz==2024.2        requests==2.32.3    cvxpy==1.8.2
```

Runtime: Python 3.14.x (Streamlit Cloud default). System deps: libopenblas-dev.

Streamlit 1.55 notes:
- `@st.fragment(run_every=N)` dims entire page during re-render — expected, not a bug
- `use_container_width=True` correct for `st.dataframe`; do NOT use `width='stretch'`
- `width='content'` is valid on `st.dataframe` in 1.52+ (content-width mode)
- `st.rerun(scope='fragment')` raises StreamlitAPIException — use plain `st.rerun()`
- `_refresh_fragment` REMOVED in v5.26 — do not re-add
- `st.plotly_chart` uses `config={'responsive': True}` — `**kwargs` deprecated in 1.50

---

## Current State (v5.28 — 2026-03-27)

**Regression baseline: 374/374 PASS**

Key changes since v5.27:
- `requirements.txt`: streamlit 1.43.2→1.55.0, yfinance 0.2.54→1.2.0, pandas 2.2.3→>=3.0.0
- Python 3.14.x — runtime.txt removed, Streamlit Cloud uses latest (3.14)
- `indicators.py`: OBV direction — `.apply(lambda)` replaced with `np.sign()` (pandas 3.0 vectorised)
- `regression.py` R2: removed `'content'` from invalid width patterns (`width="content"` valid in 1.52+)
- No code changes to any pages — all Streamlit API calls already compatible with 1.55
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
market_data.py          All yfinance + RSS. Token bucket + _ticker_cache + warmth guard.
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

### Current (v5.26) — Token Bucket + Module Cache
| Component | Detail |
|---|---|
| `_global_throttle()` | Token bucket: max=5, rate=0.4s. threading.Lock serialises all threads. |
| `_yf_batch_download()` | CHUNK=3, inter-chunk=5s, rate-limit backoff=10s, cold-start delay=2s |
| `_ticker_cache` | Module-level dict. Survives @st.cache_data evictions. Stale fallback. |
| `is_ticker_cache_warm()` | 70% majority threshold. Gates fragments on cold start. |

### Planned (OPEN-007) — DataManager: SQLite + Priority Queue
Three new packages: `requests-cache` + `requests-ratelimiter` + `pyrate-limiter`.
Combined as `CachedLimiterSession` passed to `yf.Ticker(session=)`.
Benefits: cache survives restarts, market-aware TTLs, stale-while-revalidate.
**NOT YET INTEGRATED** — see Open Items.

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
market_data.py      get_ticker_bar_data_fresh(tickers) [TTL=10s]
                    get_batch_data(tickers, period, interval, cache_buster) [TTL=300s]
                    get_price_data(ticker, period, interval, cache_buster) [TTL=300s]
                    get_ticker_info(ticker, cache_buster) [TTL=600s]
                    get_live_price(ticker) [TTL=5s]
                    get_intraday_chart_data(ticker) [TTL=60s]
                    get_top_movers(symbols, max_symbols, cache_buster) [TTL=300s]
                    get_news(feeds, max_n, cache_buster) [TTL=600s]
                    is_ticker_cache_warm(tickers) → bool
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

---

## Regression Suite

`python3 regression.py` — run from repo root. All checks must pass before any commit.

22 rule categories across syntax, imports, design contracts, lazy-loading contracts (R22).
R8 EP list: verify `_refresh_fragment` absent from app.py EP, `_make_live_price_fragment` present in dashboard EP.

---

## Open Items

| ID | Priority | Task |
|---|---|---|
| OPEN-001 | HIGH | git rm config_OLD.py + git rm --cached forecast_history.json |
| OPEN-002 | MED | README update |
| OPEN-003 | MED | Cross-session forecast persistence (Supabase) |
| OPEN-004 | LOW | Extract SCORING_WEIGHTS to config |
| OPEN-005 | HIGH | git rm config_OLD.py from repo root |
| OPEN-006 | MED | Portfolio Allocator stability score UI + backtest |
| **OPEN-007** | **HIGH** | **DataManager: SQLite + priority queue + market-aware TTLs** |
| RISK-001 | MED | XSS: sanitise() all {ticker}/{name} in unsafe_allow_html f-strings |
| RISK-003 | LOW | safe_ticker_key() in _yf_download() before yf.download() |

---

## Session Manifest (Dynamic State)

**GSI_Session.json Gist:** https://gist.github.com/Tarun19k/7c894c02dad4e76fe7c404bf963baeab

To resume with Claude:
> "I am working on the Global Stock Intelligence Dashboard.
>  Here is CLAUDE.md and GSI_Session.json — read both fully before we proceed."
