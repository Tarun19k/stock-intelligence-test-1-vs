# UI Testing — Streamlit App (Playwright)

Run automated browser tests against the GSI Dashboard using Playwright.

## Setup
```bash
pip install playwright
playwright install chromium
```

## Streamlit defaults
- Local URL: http://localhost:8501
- Wait for `networkidle` before inspecting DOM (Streamlit renders via React)
- Use `--server.headless true` when running in CI

## Step 0 — Discover sprint PLAYWRIGHT-IDs

Read `GSI_SPRINT_MANIFEST.json`. For each item, extract the `playwright` field.

- If `playwright` starts with `PLAYWRIGHT-` → it defines a test case for this sprint. Run it.
- If `playwright` is `"N/A — ..."` → skip that item (no UI to test).
- If manifest is absent or status is `PLANNING` → skip Step 0, proceed to Step 1 generic tests.

For each discovered PLAYWRIGHT-ID, the `playwright` field contains: Navigate instruction · Assert instruction · Edge cases. Run them in order. Report pass/fail per ID. Sprint close is **blocked** if any PLAYWRIGHT-ID fails.

## Step 1 — Workflow

1. Start app in background: `streamlit run app.py &`
2. Wait for port 8501 to be ready
3. Launch Playwright, navigate to localhost:8501
4. Wait for `networkidle` before any DOM inspection or interaction
5. Screenshot after each action — never assume state

## Step 2 — Generic test areas

- Sidebar market selector → correct tickers load
- Stock search → dashboard tab appears
- **SEBI disclaimer visible** on: Insights tab, dashboard header (above tabs), home page global signals section, GI watchlist badges section, week_summary Signal Summary tab (P0 regulatory — all must pass)
- LIVE badge text matches selected market country name
- Weinstein override label appears when Stage vetoes Elder
- MACD chart subtitle shows "(Daily)"
- Forecast tab: neutral zone message appears for P(gain) 45–55%
- Error log in sidebar: no errors on cold start
- Ticker bar renders without JS errors

## Screenshot naming
`test_{feature}_{pass|fail}_{timestamp}.png`

## What NOT to test via Playwright
- Data correctness (covered by regression.py)
- Import structure (covered by regression.py R1/R3)
- Rate limiting logic (unit test in isolation)

## When to run
- Sprint close (mandatory — PLAYWRIGHT-IDs must pass before status → COMPLETE)
- Before any MVP release
- After any CSS/layout change
- After Streamlit version upgrades
