# CLAUDE.md — Global Stock Intelligence Dashboard
# Read this before touching any file in this repo.
# Stable reference — updated only when architecture changes, not every session.
# Dynamic session state lives in GSI_Session.json (see Gist URL at bottom).

---

## Project Overview

Multi-market stock intelligence dashboard built with Streamlit.
Entry point: `app.py` (root). 9 markets, 38+ tickers, 4-tab per-stock dashboard.
Two repos exist — ALL active work is in the modular repo only:

- **ACTIVE:** https://github.com/Tarun19k/stock-intelligence-test-1-vs
- **REFERENCE ONLY (monolith, do not edit):** https://github.com/Tarun19k/global-gsi-intelligence

---

## Run Commands

```bash
streamlit run app.py        # run the app locally
python3 regression.py       # MUST pass before any new work
```

Deploy target: Streamlit Community Cloud + local dev.

---

## Environment — Pinned Versions

```
streamlit==1.43.2   yfinance==0.2.54    feedparser==6.0.11
plotly==5.24.1      pandas==2.2.3       numpy==1.26.4
pytz==2024.2        requests==2.32.3
```

Streamlit notes:
- `@st.fragment` available from 1.37+
- `width='stretch'` is correct for `st.dataframe` in 1.43+
- `use_container_width` deprecated for all st.* calls — do not use
- `width='stretch'` must NOT be passed to `st.plotly_chart` — use `config={'responsive':True}` only
- `st.rerun(scope='fragment')` raises StreamlitAPIException in 1.43 — use plain `st.rerun()`

---

## File Structure

Safe rebuild order (bottom = depends on everything above):

```
version.py              Changelog only. VERSION_LOG list + CURRENT_VERSION string.
tickers.json            Master ticker registry. 9 markets. Edit here — never in config.py.
config.py               Constants hub. Re-exports GROUPS + VERSION_LOG. No Streamlit calls.
utils.py                Cross-cutting helpers. safe_run(), sanitise(), init_session_state().
styles.py               All CSS. inject_css() called once from app.py. CSS must be in CSS constant.
indicators.py           Technical analysis. compute_indicators(df) + signal_score(df, info).
market_data.py          All external fetches. yfinance + RSS. cache_buster on all 4 functions.
forecast.py             Forecast lifecycle. store/resolve/accuracy. session_state as primary store.
pages/week_summary.py   Weekly performance summary. Embedded by home.py + routed by app.py.
pages/global_intelligence.py  Geopolitical topics, watchlists, live news, WorldMonitor map.
pages/home.py           Homepage. Ticker bar (window.parent injection) + morning brief + movers.
pages/dashboard.py      4-tab stock detail: Charts | Forecast | Compare | Insights.
portfolio.py            Mean-CVaR portfolio optimisation engine. No Streamlit calls.
app.py                  Entry point. Market selector, routing, auto-refresh fragment.
```

### Dependency Tiers

```
Leaves      version.py · tickers.json
Tier 0      config.py  (loads from leaves)
Tier 1      utils.py · styles.py
Tier 2      indicators.py · market_data.py · forecast.py
Tier 3      pages/week_summary.py · pages/global_intelligence.py
            pages/home.py · pages/dashboard.py
Entry       app.py  (imports all tiers)
```

---

## Key Public API — Entry Points Per File

```
app.py              _is_market_open(country) → bool
                    _on_market_change() → None
                    _refresh_fragment() → None  # @st.fragment(run_every=60)

pages/home.py       render_ticker_bar(cb=0) → None
                    render_homepage(cb=0, market_open=False) → None

pages/dashboard.py  render_dashboard(ticker, name, country, cur_sym, info, df,
                                     cb=0, compare_names=None, stock_map=None,
                                     market_open=False) → None
                    _live_kpi_panel(sig, cur_sym) → None  # @st.fragment(run_every=60)

pages/global_intelligence.py
                    render_global_intelligence(cur_sym='$', cb=0, market_open=False) → None

pages/week_summary.py
                    render_week_summary(cur_sym='₹', cb=0) → None

market_data.py      get_price_data(ticker, period='1y', interval='1d', cache_buster=0) → DataFrame
                    get_ticker_info(ticker, cache_buster=0) → dict
                    get_top_movers(symbols, max_symbols=20, cache_buster=0) → list
                    get_news(feeds, max_n=8, cache_buster=0) → list

indicators.py       compute_indicators(df) → DataFrame
                    signal_score(df, info) → dict

forecast.py         store_forecast(ticker, horizon_days, forecast_price, current_price) → dict
                    resolve_forecasts(ticker, current_price) → dict
                    render_forecast_accuracy(ticker, cur_sym) → None

utils.py            safe_run(fn, context='', default=None) → Any
                    sanitise(text, max_len=200) → str
                    sanitise_bold(text, max_len=400) → str
                    init_session_state() → None
                    responsive_cols(desktop, tablet=None, mobile=1) → list

styles.py           inject_css() → None

portfolio.py        check_data_quality(ticker, df) → dict
                    compute_log_returns(df_dict) → (np.ndarray, names, excluded)
                    winsorize_returns(returns) → np.ndarray
                    bootstrap_scenarios(returns, n=2000) → np.ndarray
                    optimise_mean_cvar(scenarios, names, risk_aversion, ...) → dict
                    compute_efficient_frontier(scenarios, names, n_points=12) → list
                    compute_stability_score(scenarios, names, ...) → dict
                    detect_stress_regime(returns, vix_df) → dict
                    check_regime_conflicts(allocation, stock_signals) → list
```

---

## Architecture Decisions

| Decision | Why — do not reverse without reading this |
|---|---|
| `tickers.json` extracted from `config.py` | config.py was 962 lines — 680 of which were the GROUPS dict. Extracted to JSON loaded at import time. All `from config import GROUPS` calls unchanged. Edit tickers here, never in config.py. |
| `version.py` split from `config.py` | VERSION_LOG grows with every patch (25+ entries). Isolating it means config.py stays stable between releases. config.py re-exports both `CURRENT_VERSION` and `VERSION_LOG` for full backward compat. |
| `session_state` as primary forecast store | Streamlit Cloud filesystem wiped on every redeploy. session_state survives reruns. Disk write is best-effort local backup only. |
| `cache_buster: int = 0` on all market_data functions | `@st.cache_data` keys on ALL args — incrementing cb forces real fetch. Default 0 = all existing call sites unchanged. |
| Manual `st.radio` routing in app.py | Streamlit MPA auto-generates duplicate sidebar nav. Manual routing = full control. MPA nav hidden via CSS. |
| Gists for code sharing with Claude | Files >400 lines must have dedicated single-file Gists — multi-file Gist HTML truncates, silently hiding later files. |

---

## DO NOT UNDO — Hard Rules

Violating any of these has caused a production crash or data loss before.

1. **Do NOT revert `forecast.py` to filesystem-only persistence.**
   Streamlit Cloud wipes the filesystem on every redeploy. session_state is the fix.

2. **Do NOT remove `cache_buster: int = 0` from `market_data.py` functions.**
   This is what makes the Refresh button and auto-refresh actually work.

3. **Do NOT add `scope='fragment'` back to `st.rerun()` in `_refresh_fragment`.**
   Causes `StreamlitAPIException` in Streamlit 1.43. Plain `st.rerun()` is correct.

4. **Do NOT move `VERSION_LOG` back into `config.py`.**
   Deliberately in `version.py`. `config.py` re-exports it — all callers unchanged.

5. **Do NOT move `GROUPS` ticker dict back into `config.py`.**
   Deliberately in `tickers.json`. Keeps `config.py` under 300 lines.

6. **Do NOT use Streamlit native MPA routing as primary nav.**
   Intentional design. MPA sidebar hidden via CSS in `styles.py`. Do not remove that rule.

7. **Do NOT use `TATAMOTORS.NS` as a ticker.**
   Delisted October 2025. Use `TMCV.NS` (commercial vehicles) and `TMPV.NS` (PV/EV).

8. **Do NOT put CSS in the `inject_css()` docstring.**
   Docstrings are not executed. All CSS must be inside the `CSS` constant in `styles.py`.
   This was a live production bug (OBS-003) — the sidebar nav, ticker bar, and header suppression
   were invisible to the browser for an unknown duration.

---

## Regression Suite — `regression.py`

Run `python3 regression.py` from project root. Must show **307/307 PASS** before starting any new work.

> **Keep this number in sync with `GSI_Session.json → regression.expected_output`.**
> R18 check in regression.py will fail if CLAUDE.md is stale — update both together.

| Check | What it validates |
|---|---|
| R1 | Syntax — all 11 source files AST-parse clean |
| R2.KI-001 | No deprecated `use_container_width=True` |
| R3 | No bare `except:` |
| R4.KI-005 | No unsafe raw `df["Close"]` access |
| R5.KI-010 | `pd` / `np` imported wherever used |
| R6.KI-013 | No `st.sidebar.X` inside `@st.fragment` |
| R7.KI-012 | No blocking `time.sleep(N≥1)` |
| R8.KI-002 | All declared entry points are defined |
| R8b.KI-015 | No `@st.fragment` self-recursion |
| R9.KI-002 | All cross-file imports resolve |
| R10.KI-009 | RSS allowlist clean + no `http://` feed URLs |
| R11 | Version log ≥ 20 entries + dynamic `CURRENT_VERSION` |
| R11.KI-011 | `TATAMOTORS.NS` absent from all source files |
| R12.KI-014 | `market_open` param propagated correctly |
| R13 | Design contracts: ticker bar, `data_stale`, refresh button, plain `st.rerun()` |
| R14.KI-016 | Market-switch state isolation (8 sub-checks) |

**Known regression gap:** R13.KI-008 checks for `stSidebarNav` anywhere in `styles.py`
(including comments). Should check inside the `CSS` constant specifically. Fix next session.

---

## Scoring Model — `indicators.py signal_score()`

| Component | Max pts | Key thresholds |
|---|---|---|
| RSI | 25 | <30=25, <45=20, <60=12, <70=8, ≥70=2 |
| MACD | 20 | bullish crossover + positive=20, recovering=14, else=2 |
| SMA Trend | 20 | price>SMA50>SMA200=20, >SMA50=12, >SMA200=6, pullback=10 |
| Bollinger | 15 | bb_pct<0.15=15, <0.35=8 |
| Volume | 10 | ratio>1.5=10, >1.2=5 |
| ADX | 10 | adx>25=10 |
| **Total** | **100** | STRONG BUY≥72 / BUY≥58 / WATCH≥40 / CAUTION<40 |

---

## External API Behaviour

**yfinance:**
- HTTP 401 Invalid Crumb — session token expired. `safe_run()` catches, returns empty DataFrame. Auto-resolves at next cache TTL (300s).
- HTTP 401 Unauthorized — Yahoo premium endpoint restriction. Expected, no fix needed.
- HTTP 404 "possibly delisted" — ticker unavailable. Transient → retry. Permanent → update `tickers.json`.
- Column format — `_normalize_df()` handles MultiIndex, RangeIndex, duplicates, Adj Close rename. `_safe_close()` guards against Close being DataFrame instead of Series.

**RSS feeds:**
- All URLs must be `https://` — `safe_url()` rejects `http://`.
- Domain allowlist enforced in `market_data.py _ALLOWED_RSS_DOMAINS`.
- `feedparser` returns empty entries silently on timeout — `safe_run()` catches exceptions.

---

## Forecast History Schema — `forecast_history.json`

```
Key format:  {safe_ticker_key}_{horizon_days}d   e.g. INFY.NS_63d
Fields:      made_on, due_on, horizon_days, forecast_price, base_price,
             actual_price (null until resolved), accuracy_pct (null until resolved),
             resolved (bool)
Warning:     forecast_price clamped to 0.01 minimum since v5.17 (OBS-006).
             Any entries with negative prices pre-date v5.17 and should be removed manually.
```

---

## Open Work

See `open_items` in GSI_Session.json for full detail. Summary:

| ID | Priority | Task |
|---|---|---|
| OPEN-001 | HIGH | `git rm --cached forecast_history.json .DS_Store __pycache__/` + move old monolith files to `archive/` |
| OPEN-002 | MED | README update — file structure, deployment steps, fix main file reference |
| OPEN-003 | MED | Cross-session forecast persistence (Supabase free tier recommended) |
| OPEN-004 | LOW | Extract scoring weights to `SCORING_WEIGHTS` dict in `indicators.py` |
| OPEN-005 | HIGH | `git rm config_OLD.py` from repo root |
| OPEN-006 | MED | Portfolio Allocator v5.24: wire stability score UI badge + backtest engine + CVaR calibration tracker |

---

## Session Manifest (Dynamic State)

Current version, session history, file versions, Gist URLs, and next steps per file
live in the session manifest — updated every session:

**GSI_Session.json Gist:** https://gist.github.com/Tarun19k/7c894c02dad4e76fe7c404bf963baeab

To resume a session with Claude:
> "I am working on the Global Stock Intelligence Dashboard.
>  Here is the session manifest GSI_Session.json — read it fully and confirm our state before we proceed."
