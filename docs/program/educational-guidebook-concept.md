# GSI Educational Guidebook — Concept & Plan
# Generated: 2026-04-07 | Session: session_020
# Status: CONCEPT APPROVED (session_020) — implementation pending skill creation

---

## CONCEPT OVERVIEW

**Title:** "Build an AI-Powered Stock Signal Tool in Python — A Practical Guide"

**Core idea:** Use the simplest extract of GSI as a worked example. NOT the full 559-ticker
production app, but a minimal "gsi-tutorial" repo that a student can build from scratch and
have working by Chapter 6. Each chapter teaches one AI/data concept using a financial
data use case.

**Why this is a GTM accelerator:**
- Establishes GSI as an authority product, not just a weekend project
- Drives developer community trust → GitHub stars → Product Hunt ranking → SEO
- Attracts Priya persona (finance students) as users of the main app
- r/learnpython + r/MachineLearning cross-post potential (500k+ combined)
- Zero cost to produce; Claude writes it

---

## TARGET READER

**Primary:** Priya persona — finance/CS student, age 20–25, knows Python basics, unfamiliar with financial data APIs or AI signal pipelines.

**Secondary:** Junior developers interested in fintech AI, looking for a portfolio project.

**NOT:** Experienced quants or traders (they already have their tools). The guidebook speaks to beginners.

---

## CHAPTER STRUCTURE

| Ch | Title | GSI concept | AI concept taught |
|---|---|---|---|
| 1 | Fetching Real Market Data | `market_data.py` simplified | API calls, rate limiting, caching basics |
| 2 | Computing Technical Signals | `indicators.py` RSI + MACD | Feature engineering from time series |
| 3 | The Verdict Engine | `compute_unified_verdict()` | Rule-based AI, signal arbitration, hierarchy |
| 4 | Visualising with Plotly | `_tab_charts()` simplified | Data visualisation, chart types, interactivity |
| 5 | Adding Probabilistic Forecasting | `forecast.py` Monte Carlo (simplified) | Probabilistic reasoning, confidence intervals |
| 6 | Building the UI with Streamlit | `app.py` minimal version | Rapid UI prototyping, fragment caching |
| 7 | Responsible AI in Finance | SEBI disclaimer, DO NOT UNDO rules | AI ethics, regulatory framing, educational vs. advisory |

### Chapter 7 is non-negotiable
The guidebook must model the same SEBI/educational framing as the main app. Any code
that displays signals carries a disclaimer. This is also the chapter that makes the
guidebook distinctive — most AI tutorials never discuss the regulatory and ethical layer.

---

## TUTORIAL REPO DESIGN

**Repo name:** `gsi-tutorial` (separate from main repo, MIT licence)

**What it includes:**
- Chapters 1–6 as Jupyter notebooks + equivalent .py scripts
- `requirements.txt` with minimal deps: yfinance, pandas, plotly, streamlit, numpy
- 5 hard-coded tickers only (RELIANCE.NS, AAPL, MSFT, BTC-USD, FTSE index)
- README with "What you'll build" screenshot at the end

**What it explicitly EXCLUDES:**
- `tickers.json` (559 tickers — not needed for tutorial; avoids ToS grey area)
- Any production-grade rate limiting code (simplified version used)
- Portfolio Allocator (cvxpy adds complexity; save for advanced appendix)
- Any data that could be construed as signals for real trading decisions

---

## DISTRIBUTION PLAN

| Channel | Content | Timing |
|---|---|---|
| GitHub | `gsi-tutorial` repo, linked from main GSI README | Before r/learnpython post |
| dev.to / Hashnode | One article per chapter (7 posts over 7 weeks) | Starting Phase 3 |
| r/learnpython (860k) | "I built a beginner-friendly tutorial: AI-powered stock signals in Python" | Post 1 with Ch 1–3 done |
| r/MachineLearning | Same post, technical angle (feature engineering on financial time series) | Same week |
| r/IndiaInvestments | "Learn how our free signal tool works — step-by-step tutorial" | Cross-link to main app |
| Main app README | "Want to learn how this works? → Tutorial repo" | Permanent link |

---

## SKILLS NEEDED TO PRODUCE THIS

1. **`tutorial-creator` skill** (MISSING — needs to be created via `/skill-creator`)
   - Encodes: curriculum design, code-snippet extraction from existing modules, learning-objective framing, Jupyter notebook structuring
   - Input: target chapter, source GSI module, reader level
   - Output: notebook + companion .py + one blog article

2. **`doc-coauthoring` skill** (EXISTS) — for co-writing the compliance chapter (Ch 7)

3. **`claude-api` skill** (EXISTS) — if we later add an AI narrative layer to the tutorial using Claude API

---

## COMPLIANCE CHECKLIST FOR GUIDEBOOK

Every chapter that shows a signal or verdict must include:
- [ ] "For educational purposes only. Not financial advice."
- [ ] Any BUY/WATCH/AVOID output labeled as "simulated signal — not a recommendation"
- [ ] Chapter 7 disclaimer must mirror the SEBI text from the main app
- [ ] Tutorial README must state: "Built for learning. Use for research only."

---

## IMPLEMENTATION ROADMAP

| Step | Session | Action |
|---|---|---|
| 1 | session_021 | Create `tutorial-creator` skill via `/skill-creator` |
| 2 | session_021 | Write Chapter 1 notebook (market data fetch + rate limiting) |
| 3 | session_022 | Write Chapters 2–3 (indicators + verdict engine) |
| 4 | session_022 | Create `gsi-tutorial` GitHub repo, push Ch 1–3 |
| 5 | session_023 | Write Chapters 4–6 (charts + forecast + Streamlit UI) |
| 6 | session_023 | Write Chapter 7 (responsible AI — co-authored with /doc-coauthoring) |
| 7 | session_024 | Post r/learnpython + r/MachineLearning launch |
| 8 | Ongoing | dev.to article series (1/week) |
