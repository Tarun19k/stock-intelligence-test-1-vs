# GSI Panel Infrastructure Review
## Multi-Premortem Gap Analysis & Implementation Plan
**Date:** 2026-05-19 | **Prepared by:** Claude (session_033) | **Status:** DRAFT — REVIEW REQUIRED

---

## SECTION 1: Panel Skills Quality Audit

### Rating Scale
- **PRODUCTION READY** — framework is concrete, output is machine-parseable, sources are named
- **NEEDS WORK** — structural gaps that weaken output quality
- **CRITICAL GAP** — missing capability that blocks a core use case

---

### Buffett — PRODUCTION READY

| Dimension | Assessment |
|---|---|
| Core framework uniqueness | Economic moat scoring (0–12 across 4 dimensions) is uniquely his. Owner Earnings formula is explicit. Circle of Competence has clear IN/EDGE/OUT classification. |
| Output parseability | Structured table with named fields, scores, and single-verdict enum (BUY/WATCH/AVOID/OUTSIDE CIRCLE). Machine-parseable. |
| Source specificity | SEC EDGAR, BSE/NSE filings, earnings transcripts, Berkshire letters. Named and actionable. |
| Missing | No explicit treatment of Indian conglomerate structures (holding companies with subsidiary complexity common in BSE). No ROCE vs ROIC disambiguation for Indian GAAP. |
| **Rating** | **PRODUCTION READY** |

---

### Munger — PRODUCTION READY

| Dimension | Assessment |
|---|---|
| Core framework uniqueness | Inversion protocol + incentive mapping + 5-discipline latticework is distinctly Munger. No overlap with Buffett's moat lens at the core. |
| Output parseability | Inversion test (3 failure modes), incentive map (stakeholders), mental model cross-check (3 disciplines), lollapalooza risk flag. Structured and parseable. |
| Source specificity | Proxy filings (DEF 14A), Form 4 insider filings, BSE insider disclosures, customer complaint data. Named and actionable. |
| Missing | No explicit treatment of promoter pledging — India's primary form of management incentive misalignment. Promoter pledge % is a Munger-relevant signal unique to Indian markets. |
| **Rating** | **PRODUCTION READY (add promoter pledge signal)** |

---

### Dalio — PRODUCTION READY

| Dimension | Assessment |
|---|---|
| Core framework uniqueness | 4-quadrant macro regime matrix + debt cycle position is uniquely Dalio. The India-specific signal list (RBI, DXY, Brent, GST collections) makes it operationally grounded. |
| Output parseability | Regime quadrant, debt cycle stage, asset-quadrant fit table, India signals, hedge suggestion. Structured and parseable. |
| Source specificity | RBI MPC statements, SEBI FII/DII data, US Fed H.4.1, India IIP/CPI (mospi.gov.in), Bridgewater public excerpts. Specific. |
| Missing | No treatment of China contagion risk — relevant for Indian IT and metals. No INR-EM correlation analysis (INR often moves with EM bloc, not just DXY). |
| **Rating** | **PRODUCTION READY** |

---

### Druckenmiller — PRODUCTION READY

| Dimension | Assessment |
|---|---|
| Core framework uniqueness | Explicit % upside/downside ratio requirement + liquidity analysis + expectations gap is distinctly Druckenmiller. No other panellist requires a stated risk/reward number. |
| Output parseability | Risk/reward ratio, liquidity environment, expectations gap direction, momentum signal (Weinstein Stage cross-ref), exit trigger, position size recommendation. Structured. |
| Source specificity | NSE price/volume, SEBI FII/DII, options PCR/IV skew, RBI OMO calendar, US Fed balance sheet. Named. |
| Missing | No treatment of VWAP/volume profile — Druckenmiller uses tape reading and volume confirmation that the current skill doesn't model. |
| **Rating** | **PRODUCTION READY** |

---

### Marks — PRODUCTION READY

| Dimension | Assessment |
|---|---|
| Core framework uniqueness | Cycle temperature (too hot/neutral/too cold) + pendulum + second-level thinking is distinctly Marks. Credit spread focus differs from Soros's reflexivity mechanism. |
| Output parseability | Second-level analysis (consensus vs. divergence), cycle temperature, 3-dimension risk assessment, pendulum position. Structured. |
| Source specificity | India VIX, Nifty P/E historical percentile, SIP inflow data, F&O retail vs. institutional, Oaktree memos. Named. |
| Missing | No treatment of distressed debt specifically — Marks' primary domain. For Indian context: NCLT resolution timeline, haircut data on resolved cases. |
| **Rating** | **PRODUCTION READY** |

---

### Soros — PRODUCTION READY

| Dimension | Assessment |
|---|---|
| Core framework uniqueness | 7-stage boom-bust model + reflexivity mechanism (cognitive + participating functions) + mandatory falsification trigger is uniquely Soros. |
| Output parseability | Prevailing bias, boom-bust stage (1–7), fundamentals vs. trend divergence, crack condition with probability, falsification trigger. Structured. |
| Source specificity | SEBI FII daily, India VIX, F&O OI/margin, real estate inventory data (Anarock, PropEquity), 13F filings. Named. |
| Missing | No treatment of currency reflexivity specifically — INR/USD feedback loops (FII carry trade → INR strengthen → more FII → until it breaks) deserve a dedicated sub-model. |
| **Rating** | **PRODUCTION READY** |

---

### Lynch — PRODUCTION READY

| Dimension | Assessment |
|---|---|
| Core framework uniqueness | 6-category stock classification (Slow Grower/Stalwart/Fast Grower/Cyclical/Turnaround/Asset Play) with PEG as primary metric is distinctly Lynch. No other panellist classifies by growth profile before applying metrics. |
| Output parseability | Stock category, 2-sentence story, GARP metrics (PEG), ten-bagger checklist, field research signal, balance sheet summary. Structured. |
| Source specificity | Screener.in, Valuepickr, BSE quarterly results, Google Trends, Zomato/Swiggy rankings for consumer research. Named and India-specific. |
| Missing | No treatment of Indian family-business Fast Growers — promoter family execution quality is a key Lynch-relevant variable in India that has no Western analogue. |
| **Rating** | **PRODUCTION READY** |

---

### Panel Convener — NEEDS WORK

| Dimension | Assessment |
|---|---|
| Synthesis table | Defined and parseable. Covers all 7 panellists with verdict + key concern. Good. |
| Decision rules | 7-row decision matrix is clear but uses equal weighting. No calibration by stock type. |
| Execution protocol | Step sequence (Dalio first → Marks+Soros → Buffett+Lynch → Druckenmiller → Munger) is logical. |
| Learning protocol | learning-log.md exists. No Brier score tracking or automatic outcome flagging. |
| Prompt caching | Architecture referenced but not fully specified. |
| Time horizon handling | Missing: user must declare time horizon, convener must weight panellists accordingly. Short-horizon favours Druckenmiller/Marks; long-horizon favours Buffett/Lynch. |
| Missing panellists | No slot for Risk Manager, Quant, or Compliance — these must be added as the skill library grows. |
| **Rating** | **NEEDS WORK — 4 specific additions required (see Section 6)** |

---

## SECTION 2: Missing Skills Inventory

### P0 — Blocks Basic Workflow

#### 1. `panel-compliance` (trigger: `/compliance`)
**Gap:** No skill enforces SEBI regulations, investor suitability, or disclaimer requirements. Any panel verdict delivered without compliance framing is a liability.
- Covers: SEBI Research Analyst Regulations 2014, investor categorisation (retail/non-institutional/institutional), suitability assessment, mandatory disclosures, prohibited content (price targets without registered RA status), required caveats
- Without it: panel output is legally problematic for any public-facing GSI deployment

#### 2. `panel-risk-manager` (trigger: `/risk`)
**Gap:** No skill computes portfolio-level risk. The 7 current skills assess individual stocks. A portfolio of 10 WATCH calls might have 0.95 correlation — the risk manager catches this.
- Covers: Value at Risk (VaR), Conditional VaR (CVaR), maximum drawdown, Sharpe/Sortino ratio, portfolio correlation matrix, tail risk events, position sizing relative to portfolio
- Without it: panel output enables stock picking without portfolio risk context

#### 3. `panel-dcf` (trigger: `/dcf`)
**Gap:** Buffett covers Owner Earnings but not explicit DCF models. Financial analysts, investment bankers, and institutional investors require a DCF with stated assumptions.
- Covers: DCF model construction (WACC, terminal growth rate, FCF projection), sensitivity tables, scenario analysis (base/bull/bear), sum-of-parts for conglomerates
- Without it: panel has no quantitative intrinsic value estimate

---

### P1 — Significantly Weakens Output

#### 4. `panel-portfolio-manager` (trigger: `/pm`)
**Gap:** Portfolio-level allocation decisions require Sharpe/Sortino tracking, rebalancing rules, and correlation-aware sizing. The current Druckenmiller skill handles single-position sizing but not portfolio construction.
- Covers: Modern Portfolio Theory application, efficient frontier (links to GSI's existing cvxpy engine), position sizing (Kelly criterion), rebalancing triggers, sector/geography concentration limits

#### 5. `panel-quant` (trigger: `/quant`)
**Gap:** No skill enforces statistical discipline. Backtests without significance testing are marketing. Signal validation requires p-values, out-of-sample testing, and regime-conditioned performance.
- Covers: Factor model construction (momentum, value, quality, size), backtest discipline (no look-ahead bias, walk-forward testing), signal significance (p-value, Sharpe of signal), Brier score tracking for probabilistic forecasts

#### 6. `panel-technical-analyst` (trigger: `/ta`)
**Gap:** Druckenmiller covers macro momentum. Lynch covers growth stories. Neither provides pure technical analysis: support/resistance levels, chart patterns, volume confirmation, moving average frameworks.
- Covers: Weinstein Stage methodology (deep-dive, not just label), key S/R levels from price history, chart pattern recognition (cup-and-handle, flag, head-and-shoulders), volume analysis, RSI divergence protocols

---

### P2 — Nice to Have

#### 7. `panel-macro-economist` (trigger: `/macro`)
An expansion of Dalio's framework with more granular intermarket analysis (bonds, currencies, commodities as a unified system). Dalio operates at regime level; a dedicated macro economist skill handles the transmission mechanism between macro inputs and sector/stock impacts.

#### 8. `panel-sector-analyst` (trigger: `/sector`)
Relative value within sectors. Peer comparison. Sector rotation signals. Dalio identifies which sectors to prefer in a macro regime; the sector analyst identifies which companies within that sector are relatively better positioned.

---

## SECTION 3: GSI Feature Gap Analysis (Per Persona)

### Current GSI Tabs
- **🏠 Home** — market overview, group heatmap, market status
- **📊 Dashboard** — stock-level signals, charts, technical indicators
- **🌍 Global Intelligence** — cross-market analysis (in development)

---

| Persona | Has in GSI Now | Missing — Must Build |
|---|---|---|
| **Retail Investor** | RSI, Weinstein Stage, momentum score, BUY/WATCH/AVOID signal | Panel verdict per ticker, plain-English explanation of each signal, suitability disclaimer, goal-based view (SIP vs. lump sum vs. trade) |
| **Active Trader** | RSI, price charts, momentum | Intraday data (yfinance limitation), risk/reward overlay on chart, entry/exit zone visualisation, options PCR display |
| **Portfolio Manager** | Portfolio Allocator (efficient frontier via cvxpy) | Live Sharpe/Sortino tracking per position, drawdown history, VaR gauge, correlation heatmap across holdings, rebalancing alert |
| **Investment Banker** | Basic price + yfinance fundamentals | EV/EBITDA comp table, M&A activity signals per sector, deal premium analysis |
| **Financial Analyst** | Price data, P/E from yfinance | DCF inputs form + calculator, earnings estimate vs. actuals tracker, PEG display alongside P/E, analyst consensus summary |
| **Risk Manager** | Rate limit cooldown notice (infrastructure, not risk) | VaR display, maximum drawdown chart, correlation matrix, tail risk flag when correlation > 0.8 across holdings |
| **Compliance Officer** | SEBI disclaimer in sidebar | Investor category selector (retail/HNI/institutional), suitability gate before showing speculative signals, compliance audit log |
| **Macro Economist** | Global Intelligence tab (partial) | Structured macro regime display (Dalio quadrant), RBI policy tracker, FII/DII flow chart, India VIX trend, INR trajectory |
| **Quant Analyst** | Signal output (RSI, momentum, Weinstein) | Signal backtest results (hit rate, Sharpe of signal), factor exposure display, statistical significance badge on signals |
| **CXO / Executive** | Home page summary | One-page executive brief: top 5 opportunities, portfolio P&L, key risks, macro regime in one sentence, recommended action |

---

## SECTION 4: UI/UX Requirements for Panel Integration

### Where Panel Lives
**New tab: "🧠 Panel Analysis"** added to the sidebar radio nav alongside Home, Dashboard, Global Intelligence.

Entry point: User selects a ticker in the Dashboard → Panel Analysis tab becomes active for that ticker.

### Panel Trigger
```
[Ticker selected in Dashboard]
         ↓
[Panel Analysis tab — shows ticker context]
         ↓
[Button: "Run Full Panel (7 members)"]   [Button: "Quick View (3 members)"]
         ↓
[Progress: "Running Dalio... ✓  Running Marks... ✓  Running Soros..."]
         ↓
[Synthesis Table → Expandable individual assessments]
```

### Verdict Display (Streamlit Components)
```python
# Synthesis table — st.dataframe with colour mapping
verdict_colours = {"BUY": "#00c853", "WATCH": "#ffab00", "AVOID": "#ff1744", "OUTSIDE CIRCLE": "#90a4ae"}

# Traffic light badges — custom HTML via st.markdown
st.markdown(f'<span style="background:{colour};border-radius:4px;padding:2px 8px;color:white;font-weight:700">{verdict}</span>', unsafe_allow_html=True)

# Expandable individual assessments
with st.expander("Buffett — Moat Score 8/12 — WATCH"):
    st.markdown(buffett_output)  # pre-formatted markdown from skill output

# Consensus bar
st.progress(buy_count / 7, text=f"BUY: {buy_count}/7  WATCH: {watch_count}/7  AVOID: {avoid_count}/7")
```

### Loading / Streaming
- Run panellists sequentially (not parallel) to enable prompt caching — participants 2–7 hit the cache
- Use `st.status` (Streamlit 1.28+) for live progress: each panellist completes → checkmark appears
- Show partial results as each panellist finishes, don't wait for all 7

### Time Horizon Selector
Add before "Run Panel" button:
```python
time_horizon = st.selectbox("Investment horizon", ["< 1 month (Trade)", "1–12 months (Swing)", "1–5 years (Invest)", "5+ years (Hold)"])
```
This value is passed to the convener, which weights Druckenmiller/Marks for short horizons and Buffett/Lynch for long.

---

## SECTION 5: Three-Round Premortem Assessment

### Round 1 — Failure Mode Identification (10 modes)

| # | Failure Mode | Impact |
|---|---|---|
| F1 | Panel gives confident BUY on a stock with bad financials because LLM infers (hallucinates) ROIC and EPS growth rather than pulling real data | User loses money; trust in tool destroyed |
| F2 | All 7 panellists return WATCH → user has no actionable decision | Tool is useless for this ticker; user abandons panel feature |
| F3 | Buffett marks a stock OUTSIDE CIRCLE, Lynch marks it Fast Grower, Druckenmiller marks it BUY — user doesn't know how to resolve the conflict | Confusion; user ignores panel output |
| F4 | Full 7-member panel run costs $0.50–2.00 per run in API tokens at scale → user runs it 20x per session → $10–40 API burn per user per day | Product is economically unviable |
| F5 | User treats AVOID as a directive to sell a stock they already hold, ignoring their own entry price and tax situation | Incorrect application; compliance liability |
| F6 | SEBI compliance risk: panel output resembles a research report without required disclaimers and registered RA disclosure | Legal liability for Tarun |
| F7 | Prompt caching fails silently (API header version changes) → all 7 participants pay full token cost → cost blows up | Invisible cost explosion |
| F8 | Panel run times out — 7 sequential API calls at ~10–20 seconds each = 70–140 seconds total → Streamlit default 120s timeout kills the session | Feature broken for every user |
| F9 | India-specific data (promoter pledging, BSE filings, NSE F&O data) is not pulled in real time — LLM relies on training data cutoff (Aug 2025) for company-specific facts | Outdated and wrong analysis |
| F10 | Learning log is never populated — no feedback loop — panellists never improve and systematic biases accumulate invisibly | Infrastructure decays; no improvement over time |

---

### Round 2 — Root Causes + Fixes

| Failure | Root Cause | Fix |
|---|---|---|
| F1: Hallucinated financials | Skills say "pull from sources" but provide no structured data input — LLM fills gaps by inference | **Require structured data block** before panel run: P/E, EPS growth 3yr, ROIC, D/E, revenue growth. Panel is disabled if data is not provided. GSI fetches from yfinance and pre-populates. |
| F2: All WATCH | Skills don't require panellists to state a "watch trigger" — WATCH is a terminal state | **Add mandatory "Watch Trigger" field** to each skill's output format: if verdict is WATCH, panellist must state the specific observable that would upgrade to BUY or downgrade to AVOID |
| F3: Unresolved conflict | Convener synthesis table presents verdicts but gives no conflict resolution guidance | **Convener blind spot map** (already written) handles most cases. Add: if Buffett says OUTSIDE CIRCLE, his verdict is excluded from consensus count; convener notes the scope limitation |
| F4: API cost explosion | No token budget gate before panel run | **Tiered access**: Quick Panel (Dalio + Marks + Lynch = 3 members, ~$0.10) vs. Full Panel (7 members, ~$0.50). Prompt caching reduces cost by ~80% on members 2–7 |
| F5: AVOID misapplied | Output format doesn't contextualise for existing holders vs. new buyers | **Add position context to convener output**: "AVOID = do not initiate new position. If you already hold, see your entry price, tax situation, and portfolio context before acting." |
| F6: SEBI compliance | No compliance framing around panel output | **Compliance skill (P0)** wraps every panel output with required SEBI disclaimers. Panel output cannot be displayed without compliance wrapper |
| F7: Silent cache failure | No logging of cache hits/misses in production | **Log cache statistics** per panel run (already implemented in roundtable_runner.py — apply same pattern to panel runner). Alert if cache read tokens = 0 on participants 2–7 |
| F8: Timeout | 7 sequential 20-second calls = 140 seconds > Streamlit 120-second default | **Two fixes**: (1) Streamlit timeout: increase via `server.scriptRunTimeoutSecs = 300` in `.streamlit/config.toml`. (2) Architecture: make panel an async job — trigger → job ID → poll for results. Panel runs in background, user sees live updates |
| F9: Stale India data | Skills reference live sources but don't pull them at invocation time | **Pre-flight data fetch** before panel run: pull FII/DII (SEBI), India VIX (NSE), BSE company filing date, promoter pledge % from BSE bulk data. Pass as structured input to panel |
| F10: No feedback loop | Learning log exists but no mechanism triggers outcome review | **Scheduled outcome review**: 3-month, 6-month, 12-month reminder (via existing cron infrastructure) — cron prompts Claude to check the learning log and surface unreviewed panel decisions |

---

### Round 3 — Re-Challenge the Fixed Plan

After applying all Round 2 fixes, 4 residual risks remain that cannot be fully eliminated:

| Residual Risk | Why It Cannot Be Fully Fixed | Permanent Safeguard |
|---|---|---|
| Data quality for Indian small-caps | yfinance coverage is thin for BSE small-caps — ROIC, EPS growth data often missing or wrong | Mandatory data confidence score in pre-flight. If confidence < 60%, panel is flagged "LOW DATA QUALITY — interpret with caution" |
| LLM reasoning variability | Even with structured inputs, LLM synthesis varies between runs. Same inputs can produce different verdicts on consecutive runs | Log all panel runs with input hash. Surface "verdict changed from last run" notice. Target consistency > 85% on identical inputs. |
| Timing risk on macro regime calls | Dalio's regime classification can be correct in direction but wrong in timing by 6–18 months | Dalio output always includes: "this regime call has a 6–18 month lag before visible in earnings — do not use as a short-term signal" |
| SEBI compliance evolution | SEBI regulations change. The compliance skill will become stale | Compliance skill has a "last reviewed" date header. Set a 90-day review reminder in the cron. |

**Confidence Score:**
- Failure modes identified (10 modes): 20/20
- Root causes mapped (all 10 traced to specific cause): 20/20
- Fixes applied (all 10 have concrete, actionable fix): 20/20
- Re-challenge survived (only execution-detail and structural-but-known gaps remain): 22/25 (−3 for data quality gap being structural and partially unresolvable)
- Gap type classification (remaining gaps correctly classified): 12/15 (−3 for timing risk on macro — still a design gap, not execution)

**Total: 94/100** — below 98 threshold. The two unresolved points:
1. Data quality for Indian small-caps (structural — yfinance limitation)
2. LLM reasoning variability (architectural — requires consistency testing infrastructure)

**Required before declaring 98/100:** Build the pre-flight data confidence scorer and run 20 test panel runs measuring verdict consistency on identical inputs.

---

## SECTION 6: New Skill Specifications (MVP)

### `panel-compliance` (P0)

**Trigger:** `/compliance` | Runs automatically after every panel convener output

**Core framework:**
1. Classify the user (retail / HNI / institutional) — different suitability rules apply
2. Check if the signal constitutes a "buy/sell recommendation" under SEBI RA Regulations 2014
3. Apply required disclaimers: not SEBI registered, educational only, not personalised advice
4. Flag if the stock is in the SME or illiquid category (higher risk disclosure required)
5. Check if any panellist's output contains prohibited content (price targets, guaranteed returns language)

**Required input:** Panel output text + user category (retail/HNI/institutional) + ticker exchange (NSE/BSE/International)

**Output format:**
```
COMPLIANCE ASSESSMENT
User Category: Retail / HNI / Institutional
Suitability: Suitable / Caution / Not Suitable for this category
Prohibited content found: Yes / No
  [If Yes: flag the specific text]
Required disclaimer: [mandatory text — always appended to panel output]
SEBI status: Educational content only. Not SEBI RA registered. Not investment advice.
```

**Sources:** SEBI Circular SEBI/HO/IMD/DF1/CIR/P/2022/127, SEBI RA Regulations 2014, SEBI Investor Charter

---

### `panel-risk-manager` (P0)

**Trigger:** `/risk` | Run alongside or after panel convener for portfolio-level context

**Core framework:**
1. Compute/estimate VaR (95%, 99%) using historical volatility from price data
2. Identify maximum drawdown from 52-week high
3. Check portfolio correlation if multiple tickers provided (flag if >0.8)
4. Apply Kelly Criterion for position sizing given stated win rate and risk/reward
5. Identify tail risk scenarios: what macro shock causes a >30% drawdown?

**Required input:** Ticker, current price, 52-week range, portfolio context (optional: other holdings for correlation)

**Output format:**
```
RISK ASSESSMENT — [TICKER]
VaR (95%, 1-month): [%] — estimated from 12-month historical volatility
Max Drawdown (52-week): [%] from [high price]
Kelly Position Size: [%] of portfolio — given stated risk/reward and win rate
Correlation Warning: [if portfolio context provided — flag pairs >0.8]
Tail Risk Scenario: [one specific macro shock and its estimated impact]
Risk Verdict: LOW / MEDIUM / HIGH / EXTREME
Stop Loss Suggestion: [price level — based on max tolerable drawdown]
```

**Sources:** NSE/BSE historical price data via yfinance, India VIX (proxy for implied volatility)

---

### `panel-dcf` (P1)

**Trigger:** `/dcf`

**Core framework:**
1. Collect FCF inputs (or estimate from available data): revenue, EBIT margin, D&A, capex, working capital
2. Project FCF for 5 years using base/bull/bear growth assumptions
3. Apply WACC (India context: risk-free rate = 10Y G-Sec yield + equity risk premium + beta)
4. Compute terminal value (Gordon Growth Model: 5% long-term growth for India)
5. Output intrinsic value range and margin of safety at current price

**Required input:** Ticker + either (a) last 3 years FCF, or (b) revenue, EBIT margin, D&A, capex

**Output format:**
```
DCF VALUATION — [TICKER]
Base case intrinsic value: ₹[X] — [X]% upside/downside from current
Bull case: ₹[X] | Bear case: ₹[X]
WACC used: [%] (risk-free: [%] + ERP: [%] + beta: [X])
Terminal growth rate: [%]
Margin of safety at current price: [%]
Data quality: HIGH / MEDIUM / LOW — [source of financial inputs]
DCF Verdict: SIGNIFICANTLY UNDERVALUED / FAIR VALUE / OVERVALUED
```

---

### `panel-portfolio-manager` (P1)

**Trigger:** `/pm`

**Core framework:**
1. Apply Modern Portfolio Theory: given a set of positions, compute portfolio-level Sharpe/Sortino
2. Identify the marginal contribution of a new position to portfolio volatility
3. Apply the GSI efficient frontier engine (cvxpy already integrated)
4. Set concentration limits: max 25% in one stock, max 40% in one sector, max 30% in one country
5. Rebalancing trigger: flag if any position drifts >5% from target weight

**Required input:** Portfolio holdings (list of tickers + weights) + proposed new position

**Output format:**
```
PORTFOLIO ASSESSMENT — [PROPOSED TICKER]
Current portfolio Sharpe: [X]
Portfolio Sharpe with new position: [X] — [improved / degraded]
Marginal volatility contribution: [%]
Concentration check:
  Stock: [X]% (limit 25%) — [PASS/FAIL]
  Sector: [X]% (limit 40%) — [PASS/FAIL]
  Country: [X]% (limit 30%) — [PASS/FAIL]
Rebalancing needed: [Yes/No — positions drifted]
PM Verdict: ADD / HOLD / REDUCE — position sizing: [%] of portfolio
```

---

## SECTION 7: Implementation Sequence

### Phase 1 — Foundation (Weeks 1–2) — Complete Panel MVP

| Item | Files | Effort | Dependency |
|---|---|---|---|
| Write `panel-compliance` skill | `~/.claude/skills/panel-compliance/SKILL.md` | 2h | None |
| Write `panel-risk-manager` skill | `~/.claude/skills/panel-risk-manager/SKILL.md` | 3h | None |
| Write `panel-dcf` skill | `~/.claude/skills/panel-dcf/SKILL.md` | 3h | None |
| Update convener with time horizon weighting | `~/.claude/skills/panel-convene/SKILL.md` | 1h | None |
| Add Watch Trigger field to all 7 skills | All 7 SKILL.md files | 2h | None |
| Add promoter pledge signal to Munger skill | `panel-munger/SKILL.md` | 30min | None |

### Phase 2 — GSI Integration (Weeks 2–4) — Panel in the Tool

| Item | Files | Effort | Dependency |
|---|---|---|---|
| Build panel runner (Python module) | `intelligence-layer/panel_runner.py` | 1 day | Skills complete |
| Pre-flight data fetcher | `intelligence-layer/panel_data_fetcher.py` | 4h | panel_runner.py |
| Panel Analysis tab (Streamlit) | `pages/panel_analysis.py` | 1 day | panel_runner.py |
| Add tab to app.py nav | `app.py` | 1h | panel_analysis.py |
| Compliance wrapper | `intelligence-layer/compliance_wrapper.py` | 2h | panel-compliance skill |
| Streamlit timeout config | `.streamlit/config.toml` | 15min | None |

### Phase 3 — Portfolio & Risk Layer (Weeks 4–6)

| Item | Files | Effort | Dependency |
|---|---|---|---|
| Write `panel-portfolio-manager` skill | `~/.claude/skills/panel-portfolio-manager/SKILL.md` | 3h | Phase 1 |
| Write `panel-quant` skill | `~/.claude/skills/panel-quant/SKILL.md` | 4h | Phase 1 |
| Write `panel-technical-analyst` skill | `~/.claude/skills/panel-technical-analyst/SKILL.md` | 3h | Phase 1 |
| Portfolio risk dashboard | `pages/portfolio_risk.py` | 2 days | panel-portfolio-manager, panel-risk-manager |
| VaR and drawdown chart | `pages/portfolio_risk.py` | 4h | price data in market_data.py |

### Phase 4 — Feedback & Learning (Week 6+)

| Item | Files | Effort | Dependency |
|---|---|---|---|
| Outcome review cron | Existing cron infrastructure | 2h | Phase 2 |
| Brier score calculator | `intelligence-layer/brier_tracker.py` | 3h | panel_runner.py + outcome log |
| Panellist weight calibration | `panel-convene/SKILL.md` update | 2h | Brier score data (3+ months) |

---

## SECTION 8: Prompt Caching Architecture for Panel Runs

### Content Block Structure
```python
messages = [{
    "role": "user",
    "content": [
        {
            "type": "text",
            "text": base_context,          # Ticker data + financials + Weinstein + RSI + macro snapshot
            "cache_control": {"type": "ephemeral"},  # CACHED — shared across all 7 panellists
        },
        {
            "type": "text",
            "text": panellist_instruction,  # "You are the Buffett panellist. Apply your framework..."
            # NOT cached — unique per panellist (~150 tokens)
        }
    ]
}]
```

### Token Estimates
| Component | Tokens | Cached? |
|---|---|---|
| Ticker data (price, P/E, EPS growth, ROIC, D/E, Weinstein Stage, RSI, momentum) | ~300 | Yes |
| Macro context (regime, FII flow, India VIX, RBI stance) | ~400 | Yes |
| Skill framework (each panellist's full SKILL.md content) | ~800 | Yes |
| Panellist instruction ("You are Buffett, apply your framework") | ~150 | No |
| **Base prompt total (cacheable)** | **~1,500** | **Yes** |
| Per-panellist instruction | ~150 | No |

### Cost Savings
- Full cache miss (participant 1): ~1,650 tokens billed at full rate
- Cache hit (participants 2–7): ~150 tokens billed at full rate + 1,500 at 10% cache rate
- Savings per participant 2–7: ~1,350 tokens at 90% discount
- Savings per 7-member panel run: 6 × 1,350 = 8,100 tokens saved at 90%
- At Sonnet input rate (~$3/M): saves ~$0.024 per full panel run
- At Haiku rate for T1 panellists (~$0.25/M): even more impactful

### Integration with roundtable_runner.py
The same `cache_control: {"type": "ephemeral"}` block pattern and `anthropic-beta: prompt-caching-2024-07-31` header already implemented in `scripts/roundtable_runner.py` applies directly. The `panel_runner.py` module (Phase 2) should be a direct port of this pattern.

---

## SECTION 9: File-Organizer Skill Review

### Current State: NEEDS WORK

The `file-organizer` skill's GSI workspace model is materially out of date. Specific gaps:

| Missing Element | Impact |
|---|---|
| `intelligence-layer/` directory not modelled | New panel output files, review documents, and skills placed incorrectly |
| `pages/` (5 active files) not listed | Incorrect guidance on where new pages belong |
| `docs/context/`, `docs/ai-ops/` not in model | Architecture and token-model-rules.md not discoverable via skill |
| No distinction between `~/.claude/skills/` (global) and GSI-local skills | Panel skills may be incorrectly recommended for GSI workspace directory |
| No rules for `.claude/rules/` scoped rule files | Governance files (do-not-undo.md, market-data.md) not modelled |
| No placement rule for `panel-infrastructure-review.md` style documents | These should live in `intelligence-layer/`, not `docs/` |
| `intelligence-layer/panel-convene/learning-log.md` not modelled | Learning log has no canonical home in the skill's model |

### Specific Additions Required (not rewrites)

Add to the GSI workspace model section:
```
intelligence-layer/           — panel infrastructure, design briefs, review documents
  panel-infrastructure-review.md — architecture review docs
  panel_runner.py             — panel execution module (Phase 2)
  panel_data_fetcher.py       — pre-flight data module (Phase 2)
  skills/                     — GSI-local panel output scratch (NOT ~/.claude/skills/)

~/.claude/skills/panel-*/    — investor panel skills (global, cross-workspace)
  SKILL.md                   — skill definition
  learning-log.md            — outcome tracking (panel-convene only)

.claude/rules/               — scoped rule files (do-not-undo.md, market-data.md, etc.)
pages/                       — Streamlit page modules (home.py, dashboard.py, global_intelligence.py,
                               panel_analysis.py when built, portfolio_risk.py when built)
```

---

## SECTION 10: Streamlit → Vercel Migration Analysis

### 10.1 Streamlit-Specific API Dependency Map

**Load-bearing `st.*` calls by category:**

| Category | Count (approx) | Trivially replaceable | Load-bearing |
|---|---|---|---|
| Layout (`st.columns`, `st.expander`, `st.tabs`) | ~40 | Partial — React equivalents exist but require rewrite | Yes |
| State (`st.session_state`) | ~25 | No — requires frontend state management (Zustand, Redux) | Yes |
| Widgets (`st.selectbox`, `st.radio`, `st.button`, `st.slider`) | ~30 | Yes — standard HTML form elements | No |
| Data display (`st.dataframe`, `st.plotly_chart`) | ~15 | Yes — recharts, plotly.js work in React | No |
| Caching (`@st.cache_data`, `@st.cache_resource`) | ~10 | No — requires Redis or equivalent | Yes |
| Markdown (`st.markdown`, `st.write`) | ~50 | Yes — trivial in React | No |
| Fragment/rerun (`st.rerun`, `@st.fragment`) | ~5 | No — requires WebSocket or SSE | Yes |

**Most load-bearing constructs:**
1. `st.session_state` — entire navigation state, ticker selection, cache buster
2. `@st.cache_data` — rate limit gate, price data caching
3. Module-level globals (`_rl_cooldown_until`, `_rl_hit_count`) — rate limit state
4. `st.rerun()` — triggered by market change and refresh button
5. `@st.fragment` — auto-refresh ticker bar (if present)

---

### 10.2 Migration Target Options

#### Option A: Vercel + Next.js (React) + Python API Routes
- **What maps:** All display logic → React components; st.plotly_chart → plotly.js; st.dataframe → tanstack-table
- **What has no equivalent:** Module-level rate limit state (CRITICAL — see 10.3); @st.cache_data → must use Vercel KV or Redis; st.session_state → must use Zustand or localStorage
- **Effort:** 4–6 weeks (full rewrite of frontend; Python API routes for data fetching)
- **Cold start:** 1–3s for Python API routes on Vercel serverless — tolerable for interactive queries, fatal for streaming panel runs
- **Blocker:** `cvxpy + pandas + yfinance` combined > 50MB → **exceeds Vercel Python function limit (50MB)**. Cannot deploy as-is.
- **Cost:** Free tier (100GB-hours/month) breaks at ~500 daily active users; Pro ($20/month) gives 1000GB-hours

#### Option B: Vercel Edge + FastAPI (Python) on Railway
- **What maps:** FastAPI replaces Streamlit server; React/Next.js frontend consumes FastAPI endpoints; session state → JWT or cookies; cache → Redis (Upstash)
- **Effort:** 3–4 weeks (FastAPI backend rewrite + React frontend shell)
- **Cold start:** None — Railway runs always-on containers
- **Deployable:** Yes — Railway has no 50MB limit; full Python dependency stack works
- **Cost:** Railway Starter $5/month + Vercel free tier. Total: ~$5–12/month at current scale

#### Option C: Render + FastAPI + Plain HTML (minimal rewrite)
- **What maps:** FastAPI for all endpoints; Jinja2 templates + Alpine.js for interactivity (near-zero JS framework overhead)
- **Effort:** 2–3 weeks (faster than full React; closer to current Streamlit mental model)
- **Cold start:** Render free tier sleeps after 15min inactivity (spin-up: 30–60s). Render Starter ($7/month) = always-on
- **Deployable:** Yes
- **Cost:** $7/month (Render Starter) — cheapest fully-deployable option

**Recommendation: Option B (Railway FastAPI + Vercel Edge React)**
- Eliminates the 50MB Python limit blocker
- Preserves always-on state for the rate limit gate during migration
- Vercel Edge handles CDN, SSL, preview deployments automatically
- Railway's deploy model is closest to the current always-on Streamlit process

---

### 10.3 File-by-File Impact Assessment

| File | Status | What Changes |
|---|---|---|
| `app.py` | **Major rewrite** | Routing logic → FastAPI routes + React navigation; sidebar → React layout |
| `market_data.py` | **Major changes** | Module-level rate limit globals → Redis-backed distributed lock (Upstash); @st.cache_data → Redis TTL cache |
| `indicators.py` | **Minor changes** | Pure computation — keep as-is; expose via FastAPI endpoint |
| `config.py` | **Keep as-is** | Pure data — import into FastAPI |
| `styles.py` | **Delete** | CSS moves to React/Tailwind |
| `utils.py` | **Minor changes** | init_session_state → Redis/JWT; render_error_log → FastAPI error endpoint |
| `pages/home.py` | **Major rewrite** | React component |
| `pages/dashboard.py` | **Major rewrite** | React component + FastAPI data endpoint |
| `pages/global_intelligence.py` | **Major rewrite** | React component |
| `pages/week_summary.py` | **Major rewrite** | React component |
| `pages/observability.py` | **Keep logic, rewrite display** | Observability data → FastAPI endpoint; UI → React |
| `tickers.json` | **Keep as-is** | Static data — served by FastAPI |
| `requirements.txt` | **Major changes** | Add: fastapi, uvicorn, upstash-redis, httpx. Remove: streamlit, streamlit-analytics2 |
| `regression.py` | **Keep + extend** | Add FastAPI endpoint regression tests |
| `compliance_check.py` | **Keep as-is** | Pre-push gate — language agnostic |
| `.streamlit/config.toml` | **Delete** | Replaced by Railway/Vercel config |

---

### 10.4 Panel Skills Integration on Vercel/Railway

**The panel run problem on serverless:**
- A full 7-member panel run = 7 sequential Anthropic API calls
- Each call: ~10–20 seconds
- Total: 70–140 seconds
- Vercel function timeout: 10s (Hobby), 60s (Pro), 300s (Enterprise)
- **Conclusion: Panel runs cannot run inside Vercel serverless functions on Hobby or Pro**

**Solution: Background job architecture**
```
User triggers panel run
        ↓
Railway FastAPI endpoint: POST /panel/run
  → creates job ID
  → enqueues job (Redis queue or Celery)
  → returns job_id immediately (< 1 second)
        ↓
Frontend polls: GET /panel/status/{job_id}
  → returns progress (Dalio: complete, Marks: running...)
        ↓
Panel worker process (Railway background worker)
  → runs all 7 panellists sequentially (with prompt caching)
  → writes results to Redis with job_id key
        ↓
Frontend: GET /panel/result/{job_id}
  → renders synthesis table
```

**Prompt caching in serverless context:**
- Prompt caching is stateless at the API level — works identically in serverless vs. long-running process
- The cache lives in Anthropic's infrastructure, not in the app process
- No change required to the caching strategy for serverless deployment

**Streaming alternative (if async job is too complex for Phase 1):**
Use Server-Sent Events (SSE) from Railway FastAPI to stream panel results as each panellist completes. FastAPI natively supports SSE via `StreamingResponse`. Frontend uses `EventSource` API. This avoids the polling complexity.

---

### 10.5 Migration Premortem (3 rounds)

**Round 1 — Immediate breakages on migration:**
1. Rate limit gate collapses — `_rl_cooldown_until` is per-process, not shared → 429 storm under any load
2. `cvxpy` import fails on Vercel — 50MB limit exceeded → Portfolio Allocator dead on arrival
3. `st.session_state` has no equivalent → all navigation state (ticker selection, market choice, cache buster) is lost on page reload
4. `@st.cache_data` TTL caching → no equivalent without Redis → every request hits yfinance → rate limit hit in minutes
5. Auto-refresh (ticker bar) requires WebSocket → not available in Vercel serverless

**Round 2 — Root causes + fixes:**
1. Rate limit state → Fix: Upstash Redis for distributed lock (`SETNX` with TTL = cooldown duration). Pre-migration requirement.
2. cvxpy size → Fix: Option B (Railway) eliminates the limit. OR: replace cvxpy with scipy.optimize.minimize (smaller footprint) for Vercel-only path.
3. Session state → Fix: JWT stored in cookie for server-side session; React Zustand for client-side UI state.
4. Cache → Fix: Upstash Redis with TTL per ticker. Same Redis instance as rate limit gate.
5. Auto-refresh → Fix: Replace with client-side polling (React useEffect with 30s interval hitting FastAPI endpoint).

**Round 3 — Residual risks:**
- **Data freshness during migration window:** If Streamlit and FastAPI run simultaneously (strangler fig pattern), cache is duplicated — users may see different data depending on which service they hit. Fix: migrate to single backend before exposing FastAPI to users.
- **yfinance ToS risk:** yfinance is already a grey-area data source. Migration to FastAPI makes the scraping more visible (server-side vs. browser). No change to risk profile, but worth noting.
- **Upstash Redis latency:** Redis adds ~5–20ms per cache read on Railway→Upstash. Acceptable for data fetches; negligible for the rate limit gate.

---

### 10.6 Recommended Migration Sequence

**Phase 0 — Pre-migration (no user-facing changes, 1 week)**
- Replace `_rl_cooldown_until`/`_rl_hit_count` globals with Upstash Redis in `market_data.py`
- Add `fastapi`, `uvicorn`, `httpx`, `upstash-redis` to requirements
- Write FastAPI app shell: `api/main.py` with health endpoint and one data endpoint (`/api/price/{ticker}`)
- Success criteria: FastAPI and Streamlit both running locally, sharing the same Redis rate limit state

**Phase 1 — Minimum viable Railway deploy (1 week)**
- Deploy FastAPI backend to Railway
- Deploy static frontend shell (Next.js on Vercel) pointing to Railway
- Migrate market data endpoints to FastAPI: `/api/price`, `/api/info`, `/api/rate_limit_state`
- Streamlit remains primary UI — FastAPI is backend-only
- Success criteria: Streamlit reads from FastAPI endpoints; data consistency verified

**Phase 2 — Full feature parity (2–3 weeks)**
- Build React frontend: Home, Dashboard, Global Intelligence tabs
- Migrate all pages to React components consuming FastAPI
- Retire Streamlit frontend
- Portfolio Allocator: replace cvxpy with scipy (if Vercel-only) OR keep cvxpy on Railway worker
- Success criteria: regression.py passes on FastAPI; all Streamlit features available in React

**Phase 3 — Panel skills + intelligence layer (Week 4–6)**
- Implement panel runner as Railway background worker (Redis queue + Celery or ARQ)
- Add SSE streaming for real-time panel progress
- Add Panel Analysis tab to React frontend
- Wire compliance wrapper to every panel output
- Success criteria: full 7-member panel run completes in <90 seconds; compliance wrapper active; prompt caching hit rate >80% on members 2–7

---

*Document compiled: 2026-05-19 | Sources: all 8 panel SKILL.md files, GSI codebase (app.py, market_data.py, requirements.txt, pages/*), Agent 2 migration analysis, 3-round premortem.*
