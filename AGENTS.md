# AGENTS.md — Global Stock Intelligence Dashboard
# Universal AI agent context file (Claude Code, Cursor, Codex, Zed, OpenCode)
# Mirrors CLAUDE.md for cross-tool compatibility.
# Keep in sync with CLAUDE.md on every version update.
# Last synced: 2026-04-06 v5.35.1

## Project
Multi-market stock intelligence dashboard. Python + Streamlit.
Entry: `app.py`. 559 tickers, 9 markets, 38 groups.
Repo: https://github.com/Tarun19k/stock-intelligence-test-1-vs

## Environment
streamlit==1.55.0, yfinance==1.2.0, pandas>=1.4.0, cvxpy==1.8.2
Python 3.14. No API keys. No database. No secrets.

## Before any commit
```bash
python3 regression.py   # ALL 433 CHECKS PASS required
```

## Critical rules (never violate)
1. No hard-coded market values — all prices via API
2. No `import yfinance` outside market_data.py
3. No Streamlit calls in indicators.py, forecast.py, portfolio.py
4. SEBI disclaimer required on every signal section
5. Algorithmic outputs must be labeled as algorithmically generated
6. `_is_rate_limited()` before every yfinance call in market_data.py
7. `safe_float(None)` returns 0.0 — 0.0 is not a valid ROE, show N/A
8. ROE/fundamentals null: `val_str = f'{val:.1f}%' if val != 0 else "N/A"`
9. "No major red flags" fallback checks RSI and MACD first
10. Momentum score (X/100) not in dashboard header — verdict badge only
11. `_render_next_steps_ai()` must NOT be called from render_global_intelligence()
12. pages/ must NOT call DataManager.fetch() until M4

## Governance
Read GSI_GOVERNANCE.md before implementing any new feature.
Read GSI_SKILLS.md for the relevant implementation pattern.
Run GSI_COMPLIANCE_CHECKLIST.md compliance script before pushing.

## Architecture
- market_data.py → all yfinance I/O
- indicators.py → pure computation, no Streamlit
- pages/ → rendering only, data passed as args
- data_manager.py → M1 skeleton, bypass mode until M4

## Version
v5.35.1 | Regression: 378/378
