# 📈 Global Stock Intelligence Dashboard

A production-grade financial intelligence platform built on Python and Streamlit. Aggregates live market data across **559 tickers · 9 markets · 38 sector groups**, applies a multi-layer technical analysis engine, and presents investment signals, portfolio optimisation, and geopolitical intelligence in a unified interface.

**Live:** https://stock-intelligence-test-1.streamlit.app

---

## Features

- **Multi-market coverage** — India (NSE/BSE), USA, Europe, China, ETFs, Commodities, FX, Rates, Indices
- **4-layer verdict engine** — Weinstein Stage + Elder Triple Screen + RSI/MACD/ADX composite + conflict detection
- **Bootstrapped forecasting** — 2,000-path Historical Simulation with P10/P90 confidence bands
- **Mean-CVaR portfolio optimiser** — Rockafellar-Uryasev (2000), stress regime detection, VIX-aware risk budgets
- **Global Intelligence Centre** — geopolitical topic cards with live RSS, impact chains, watchlist badges
- **Rate-limit resilient** — token bucket throttle, module-level cache, CircuitBreaker (DataManager M1)

---

## Quick Start

```bash
git clone https://github.com/Tarun19k/stock-intelligence-test-1-vs
cd stock-intelligence-test-1-vs
uv pip install -r requirements.txt   # or: pip install -r requirements.txt
streamlit run app.py
```

Requires Python 3.14. No API keys. No database. No secrets.

---

## Development

### Before any commit
```bash
python3 regression.py          # must be ALL 399 CHECKS PASS
```

### Before any push to main
Run the compliance script in `GSI_COMPLIANCE_CHECKLIST.md` — Tier 1–3 are blocking.

### Environment
```
streamlit==1.55.0   yfinance==1.2.0     pandas>=1.4.0
plotly==5.24.1      cvxpy==1.8.2        feedparser==6.0.11
```

See `requirements.txt` for full dependency list. `pandas>=3.0.0` will not resolve — Streamlit 1.55 metadata declares `pandas<3`. Use `pandas>=1.4.0`.

---

## Project Structure

```
app.py                        Entry point. Routing. Session state.
market_data.py                All yfinance + RSS. Rate limiting.
indicators.py                 Technical analysis engine.
forecast.py                   Bootstrapped forecasting engine.
portfolio.py                  Mean-CVaR optimiser. No Streamlit.
config.py                     Constants. MARKET_SESSIONS, GLOBAL_TOPICS.
utils.py                      Shared utilities. safe_run, sanitise.
styles.py                     All CSS. inject_css() called once.
data_manager.py               DataManager M1 skeleton (bypass mode).
version.py                    VERSION_LOG + CURRENT_VERSION.
tickers.json                  559 tickers across 38 groups. Single source of truth.
regression.py                 378-check test suite.
pages/
  home.py                     Global Market Overview.
  dashboard.py                4-tab stock dashboard.
  week_summary.py             Weekly summary + group/market overview.
  global_intelligence.py      Geopolitical intelligence centre.
```

---

## Governance & Documentation

All four documents live in the repo root. Read them before making changes.

| Document | Purpose |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Architecture reference. Start every Claude session with this. |
| [`GSI_GOVERNANCE.md`](GSI_GOVERNANCE.md) | 7 mandatory policies for all development. |
| [`GSI_QA_STANDARDS.md`](GSI_QA_STANDARDS.md) | QA brief template, issue classification, test personas. |
| [`GSI_SKILLS.md`](GSI_SKILLS.md) | Development patterns and anti-patterns from production bugs. |
| [`GSI_COMPLIANCE_CHECKLIST.md`](GSI_COMPLIANCE_CHECKLIST.md) | Pre-deploy gate. Run before every push. |
| [`GSI_session.json`](GSI_session.json) | Session manifest. Tracks open items, file state, regression baseline. |

---

## Regulatory Disclaimer

This application is for informational and educational purposes only. All signals, verdicts, and analysis are algorithmically generated from quantitative technical indicators and are not human analyst opinions. This is not financial advice. Consult a SEBI-registered investment advisor before making any investment decisions. Past performance is not indicative of future results.

---

## Versioning

Current version: see `CLAUDE.md` Current State section.
Full changelog: `version.py` → `VERSION_LOG`.
Human-readable changelog: `CHANGELOG.md`.

---

## License

Private repository. Not licensed for redistribution.

Current version: v5.32 | Regression: ALL 399 CHECKS PASS
