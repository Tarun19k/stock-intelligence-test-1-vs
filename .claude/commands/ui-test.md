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

## Workflow
1. Start app in background: `streamlit run app.py &`
2. Wait for port 8501 to be ready
3. Launch Playwright, navigate to localhost:8501
4. Wait for `networkidle` before any DOM inspection or interaction
5. Screenshot after each action — never assume state

## Key test areas for GSI
- Sidebar market selector → correct tickers load
- Stock search → dashboard tab appears
- SEBI disclaimer visible in Insights tab (P0 regulatory)
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
Before any MVP release. After any CSS/layout change. After Streamlit version upgrades.
