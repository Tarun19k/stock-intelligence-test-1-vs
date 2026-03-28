# GSI Dashboard — QA Standards & Testing Protocol
# Version: 1.0 | Established: 2026-03-28
# Source: QA audit sessions v5.28–v5.31, post-release testing findings
# Owner: Tarun | Used by: QA analyst, developer

---

## 1. Issue Severity Classification

### P0 — Critical (Fix Before Any User Sees This)
- Financial harm potential or liability exposure
- False safety statements (claiming no risk when risk exists)
- Missing regulatory disclaimers on signal/recommendation sections
- Data showing fundamentally wrong values (0.0% ROE when actual is 10%)
- Core feature broken on day of test (WorldMonitor CSP block)
- Stale data labeled as live/real-time

**SLA:** Fix in current session. Never ship without resolving P0.

### P1 — High (Next Sprint, 1–2 Weeks)
- Same metric showing different values on two pages in the same session
- Signal conflict displayed with no arbitration or explanation
- Temporal labels missing (weekly vs daily figures without context)
- UX failures that affect all personas (text wrapping, empty-looking pages)
- MACD/indicator timeframe unlabeled
- Market-selector-independent content (GI watchlist ignores market choice)

**SLA:** Ship in next version. Document with OPEN-XXX ID.

### P2 — Medium (v6 Roadmap)
- Missing quantitative visualisations on qualitative pages
- Metric context gaps (ROE without industry benchmark)
- Performance improvements
- Mobile viewport edge cases
- Decomposition/explainability of composite scores

**SLA:** Tracked in session manifest. No deadline pressure.

### P3/P4 — Low
- Polish, aesthetic preferences, nice-to-have features
- Minor copy improvements
- Non-critical tooltip additions

---

## 2. QA Brief Template

Every fix shipped must have a QA brief that follows this structure. Lessons from v5.31 Fix1/Fix2 numbering confusion are incorporated.

```
## Fix [N] — [Short name]
Audit ref: [audit ID e.g. D-02, C-01]
File changed: [filename]
Function changed: [function name]

### What changed
[One sentence describing the before and after]

### Where to look
Page: [exact page name]
Navigate to: [step-by-step — "Dashboard tab → select RELIANCE.NS → Insights & Actions"]
Section: [exact section name on screen]

### Before (what you would have seen in v5.30)
[Exact text, value, or description — include screenshot if possible]

### After (what you should see in v5.31)
[Exact text, value, or description — include screenshot if possible]

### Pass criteria
[Single unambiguous condition — "ROE card shows N/A not 0.0%"]

### Fail criteria
[What would constitute a failure — "ROE card shows 0.0% or is absent entirely"]

### Note
[Any scope boundaries — "Industry benchmark comparison is NOT in scope for this fix"]
```

---

## 3. Test Personas

Always test critical fixes against at least two of these personas:

| Persona | Risk Level | What they notice first |
|---|---|---|
| Complete Beginner | HIGH | Missing onboarding, jargon-heavy labels, broken features on load |
| Casual Retail Investor | HIGH | Investment recommendations without disclaimer, stale articles labeled Live |
| Active Trader | MEDIUM | MACD timeframe assumptions, signal conflicts, refresh reliability |
| Fundamental Analyst | MEDIUM | ROE/P/E accuracy, no F&O data, unsourced % claims |
| NRI / Global Investor | MEDIUM | India-US divergence unexplained, EUR/USD context absent |
| Financial Advisor / PM | HIGH | Cannot show to clients without disclaimer — liability exposure |
| Quant / Systematic Trader | LOW | No data export, no regime-aware forecast, no raw signal API |

**For regulatory fixes (P0-3, P0-4):** Must pass Financial Advisor / PM persona.
**For data accuracy fixes (D-02, H-01):** Must pass Fundamental Analyst persona.
**For UX fixes (H-03, F-15):** Must pass Complete Beginner persona.

---

## 4. Audit Finding Naming Convention

All findings from audit reports are tracked with the following ID structure:

```
[Page prefix]-[Sequential number]

Page prefixes:
  H   = Home page
  D   = Dashboard page
  G   = Global Intelligence page
  C   = Cross-page / Data conflict
  F   = Feature-level (any page)
  P0  = P0 Critical (regulatory/safety, crosses pages)
  QA  = Expert QA audit specific
```

Examples: `H-01`, `D-02`, `G-04`, `C-01`, `F-03`, `P0-3`

When adding to `GSI_session.json` known_issues:
```json
"QA-H01-5day": "OPEN P1 — [description] | Target: v5.32"
"QA-D02-ROE": "FIXED v5.31 — QA VERIFIED 2026-03-28 | [description]"
```

---

## 5. Regression Checklist Before Every Commit

```bash
# 1. Syntax check
python3 -c "import ast; [ast.parse(open(f).read()) for f in ['app.py','market_data.py','indicators.py','dashboard.py','home.py','global_intelligence.py','week_summary.py','forecast.py','portfolio.py','config.py','utils.py','styles.py','version.py','regression.py']]"

# 2. Full regression suite
python3 regression.py
# Expected: ALL 378 CHECKS PASS (or current baseline)

# 3. Version entry added
python3 -c "from version import CURRENT_VERSION; print(CURRENT_VERSION)"
# Must match the version you're shipping

# 4. No banned patterns
grep -n "No major red flags at this time" dashboard.py  # must return nothing
grep -n "_render_next_steps_ai()" global_intelligence.py  # must return nothing
grep -n "Momentum: {score}/100" dashboard.py  # must return nothing
```

---

## 6. Known False Positives in Audit Scripts

These were discovered during v5.31 audit and are documented to prevent re-investigation:

| Check | False positive reason | Correct check |
|---|---|---|
| `"_render_next_steps_ai() not in gi"` | `def _render_next_steps_ai():` is a substring match | Use `re.findall(r'(?<!def )_render_next_steps_ai\(\)', src)` |
| `"RATES CONTEXT" not in dashboard.py` | String lives in `indicators.py` where verdict is generated | Check `indicators.py`, not `dashboard.py` |
| `"Momentum:" not in dashboard.py` | Removed from header (Option B) but present in KPI panel section title | Check for `"Momentum Signal Panel"` instead |

---

## 7. Data Source Reliability Matrix

Used when deciding which endpoint to trust for which metric:

| Metric | Source | India reliability | US reliability | TTL |
|---|---|---|---|---|
| Price (OHLCV) | `get_price_data()` → yfinance | High | High | 300s |
| Live price | `get_live_price()` → yfinance | High (market hours) | High | 5s |
| Ticker info (P/E, P/B) | `get_ticker_info()` → `Ticker.info` | Medium (Nifty 50 only) | High | 600s |
| ROE (returnOnEquity) | `Ticker.info` | **LOW — often null** | Medium | 600s |
| ROE (calculated) | `Ticker.financials` + `Ticker.balance_sheet` | Medium (large caps) | High | 24h |
| Sector breadth | `get_batch_data()` → computed | High | High | 300s |
| News / RSS | `get_news()` → feedparser | Varies by feed | Varies | 600s |
| Sector averages | Hardcoded in config.py | Quarterly accuracy | Quarterly accuracy | Manual |

---

## 8. Audit Report Registry

All audit reports received, version tested, and key findings:

| Report | Version tested | Date | Key score | Top finding |
|---|---|---|---|---|
| Homepage Audit | v5.28 | 2026-03-28 | 6/10 | H-01: 5-day figures inconsistent across pages |
| Dashboard Audit | v5.28 | 2026-03-28 | 7/10 | D-01: Score 59/100 but WATCH verdict (confusing) |
| Global Intelligence Audit | v5.28 | 2026-03-28 | 3/10 | G-01: WorldMonitor CSP block; F-03: 3yr old articles live |
| Expert QA Report | v5.28 | 2026-03-28 | 5.5/10 | #29: Zero disclaimers; #32: Algo output unlabeled |
| Data Dependency Report | v5.28 | 2026-03-28 | 2/10 | C-01: No red flags while 9/12 sectors negative |
| 360° Bird's Eye View | v5.31 | 2026-03-28 | 5.5/10 | Meta-synthesis + v5.31 live verification |

---

## 9. Post-Fix Verification Protocol

After every deployment, QA runs this structured checklist:

### Immediate (within 1 hour of deploy)
- [ ] App loads without error on cold start
- [ ] Ticker bar shows prices (not dashes)
- [ ] Selecting a stock loads the dashboard without error
- [ ] Error log in sidebar is empty or shows only rate-limit entries

### P0 fixes specifically
- [ ] SEBI disclaimer visible on Insights tab
- [ ] Algorithmic disclosure visible above the 3 insight columns
- [ ] "Market CLOSED" badge shows when markets are closed
- [ ] No article older than 90 days shown in any "Live" section

### Cross-page data consistency spot check (baseline tracker)
Record these values every test run in the QA log:
- Nifty 50 5-day % on Home page: ___
- Nifty 50 5-day % on Dashboard: ___
- Crude WTI price in ticker bar: ___
- Crude WTI price in GI West Asia watchlist: ___
- Verdict for RELIANCE.NS: ___
- ROE shown for RELIANCE.NS: ___

Discrepancies in this table are P1 data coherence bugs (OPEN-008, OPEN-016).
