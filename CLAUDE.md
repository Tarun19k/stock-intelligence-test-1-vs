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
python3 regression.py       # MUST pass (374/374) before any new work
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

## Current State (v5.31 — 2026-03-28)

**Regression baseline: 374/374 PASS**

Versions since last CLAUDE.md update:
- **v5.29** — `get_ticker_info` missing `_is_rate_limited()` gate added
- **v5.30** — `styles.py` sidebar collapse CSS for Streamlit 1.55 (stSidebarCollapsedControl)
- **v5.31** — QA audit P0 fixes (see Open Items for full audit backlog):
  - Option B: raw Momentum score removed from header; verdict + plain-English reason only
  - ROE 0.0% null guard → N/A (yfinance returns null for Indian tickers via safe_float→0)
  - Watch Out For false positive fixed: RSI/MACD-aware default, never blanket "no red flags"
  - SEBI disclaimer + algorithmic disclosure added to Insights tab (P0 regulatory fix)
  - Market status card labels: IND/USA/EUR/CHN/COMM/ETF (prevents mid-word wrapping)
  - TechCrunch stale RSS feeds removed from AI & Jobs config
  - GI topic cards: expanded=True by default
  - Live Headlines label: date-gated, only "Live" when article <48h old
  - "What You Should Do Next" removed from GI page (liability, no market relevance)
  - R17 regression updated: "Momentum Signal Panel" accepted as valid score label
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
11. **Do NOT restore "No major red flags at this time."** as the Watch Out For fallback. It is a false safety statement. The RSI/MACD-aware default is the correct replacement.
12. **Do NOT display raw Momentum score (X/100) in the dashboard header.** Option B is final — verdict badge + plain-English reason only. Score is in KPI panel.
13. **Do NOT remove the SEBI disclaimer from `_tab_insights()`.** It is a P0 regulatory requirement. It must appear before the three insight columns.
14. **Do NOT call `_render_next_steps_ai()` from `render_global_intelligence()`.** Removed v5.31 — liability risk. Function definition kept for future redesign.

---

## Regression Suite

`python3 regression.py` — run from repo root. All checks must pass before any commit.

22 rule categories across syntax, imports, design contracts, lazy-loading contracts (R22).
R8 EP list: verify `_refresh_fragment` absent from app.py EP, `_make_live_price_fragment` present in dashboard EP.

---

## Open Items

### Infrastructure
| ID | Priority | Task |
|---|---|---|
| OPEN-001 | HIGH | git rm config_OLD.py + git rm --cached forecast_history.json |
| OPEN-002 | MED | README update |
| OPEN-003 | MED | Cross-session forecast persistence (Supabase) |
| OPEN-004 | LOW | Extract SCORING_WEIGHTS to config |
| OPEN-005 | HIGH | git rm config_OLD.py from repo root |
| OPEN-006 | MED | Portfolio Allocator stability score UI + backtest |
| **OPEN-007** | **HIGH** | **DataManager M2: CacheManager + DataContract validator (M1 complete)** |
| RISK-001 | MED | XSS: sanitise() all {ticker}/{name} in unsafe_allow_html f-strings |
| RISK-003 | LOW | safe_ticker_key() in _yf_download() before yf.download() |

### QA Audit Backlog — v5.32 Sprint (P1 High)
| ID | Audit Ref | Task |
|---|---|---|
| OPEN-008 | H-01 | 5-day calculation unification — shared `_calc_5d_change(df)` across Home/Dashboard/GI |
| OPEN-009 | D-03 | Forecast neutral threshold — P(gain) 45–55% shows "Insufficient directional signal" |
| OPEN-010 | D-04 | Forecast deduplication — update existing entry when forecast unchanged same day |
| OPEN-011 | D-06/D-08 | Temporal labels — explicit "This week" / "Today" on all time-relative figures |
| OPEN-012 | C-04 | Weinstein override disclosure — label when Stage vetoes Elder signal |
| OPEN-013 | C-06 | MACD timeframe label — "Daily" on chart, "Intraday (live)" on KPI panel |
| OPEN-014 | F-05 | GI watchlist responds to market selector — pass `country` param |
| OPEN-015 | C-09 | Market LIVE badge gated on `market_open` bool, not Streamlit runtime |
| OPEN-016 | G-04 | GI ticker data coherence — use ticker_cache when warm |

### QA Audit Backlog — v5.33+ (P2 / Roadmap)
| ID | Audit Ref | Task |
|---|---|---|
| OPEN-017 | Governance | 7-policy governance framework + R25 regression checks |
| OPEN-018 | C-01 | Feed sector breadth into AI narrative engine (full C-01 fix) |
| OPEN-019 | C-05 | Momentum Score decomposition bar chart |
| OPEN-020 | G-01 | WorldMonitor self-hosted (Leaflet.js + ACLED/GDELT API) |

## Governance Policy Framework (v5.31)

Seven policies agreed during QA audit session. All future features must comply.

| # | Policy | Core Rule |
|---|---|---|
| 1 | Data & Logic Integrity | No hard-coded dynamic values; refresh invalidates all cache layers |
| 2 | Architectural Policies | Strict module separation; CSP compliance on all embeds; scalable impact chains |
| 3 | UX & Performance Standards | Persona-ready density; 2MB bundle cap; 4:5 + 16:9 responsive |
| **4** | **Regulatory & Compliance** | **SEBI disclaimer on every signal section; algorithmic outputs labeled; no unnamed investment recommendations** |
| **5** | **Data Coherence** | **Same metric = same calculation function across all pages; AI narrative must consume same data as indicator panel** |
| **6** | **Signal Arbitration** | **Documented hierarchy: Weinstein > Elder in conflict; veto must be visibly disclosed in UI** |
| **7** | **Data Freshness Labeling** | **Recency claims ("Live", "Real-Time") gated on timestamp verification; stale data shows source date** |

Policies 4–7 are new additions from audit session 009. Policies 1–3 were pre-existing.

---

## Session Manifest (Dynamic State)

**GSI_Session.json Gist:** https://gist.github.com/Tarun19k/7c894c02dad4e76fe7c404bf963baeab

To resume with Claude:
> "I am working on the Global Stock Intelligence Dashboard.
>  Here is CLAUDE.md and GSI_Session.json — read both fully before we proceed."
