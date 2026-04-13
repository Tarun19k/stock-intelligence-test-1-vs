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
| v5.32 QA Brief | v5.32 | 2026-03-29 | TBD | 9 fixes: data coherence + temporal labeling |
| v5.34 QA Brief | v5.34 | 2026-04-01 | TBD | 5 fixes: observability, UX, P0 compliance |

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

Discrepancies in this table are P1 data coherence bugs. OPEN-008 and OPEN-016 fixed in v5.32 — if values still diverge, regression has occurred.

---

## 10. v5.32 QA Brief — Data Coherence & Temporal Labeling Sprint

**Version:** v5.32 | **Date:** 2026-03-29 | **Fixes:** 9 | **Regression baseline:** 391/391

---

### Fix 1 — 5-day % consistency across pages (OPEN-008 / H-01)
**Audit ref:** H-01 | **Files changed:** `utils.py`, `pages/home.py`

**What changed:** Home page and Dashboard now use the same `calc_5d_change()` function
from `utils.py` to calculate 5-day returns. Previously each page had its own inline calc,
which caused different values in the same session.

**Where to look:**
- Page: Home page → Global Snapshot section (the price cards row)
- Navigate to: Open app → Home tab → scroll to "📊 Global Snapshot"
- Also check: Select any stock → Dashboard → Charts tab → Live KPI panel

**Before (v5.31):**
Nifty 50 card on Home page could show e.g. `-9.4%` (5d) while the same
stock's Dashboard KPI panel showed `-1.3%` in the same session.

**After (v5.32):**
Both pages show the same 5-day figure for the same instrument.

**Pass criteria:** Record Nifty 50 5-day % from Home snapshot card, then select
`^NSEI` on the Dashboard. Both figures must match within ±0.1%.

**Fail criteria:** Any difference greater than 0.1% between the two pages in
the same session is a failure.

**Note:** Small differences (<0.1%) are acceptable due to cache timing.
Differences >1% indicate the fix is not active.

---

### Fix 2 — Forecast P(gain) neutral zone (OPEN-009 / D-03)
**Audit ref:** D-03 | **Files changed:** `forecast.py`

**What changed:** P(gain) values between 45% and 55% now display as
"Neutral (45–55%)" instead of a specific percentage like "49%", which
implied false directional precision.

**Where to look:**
- Page: Dashboard → Forecast tab
- Navigate to: Select any stock (RELIANCE.NS works well) → Forecast tab →
  look at the forecast history table column "P(Gain)"

**Before (v5.31):**
P(Gain) column showed values like "49%" or "52%" even when the model
had no real directional conviction.

**After (v5.32):**
Any value in the 45–55% band shows "Neutral (45–55%)" instead.
Values outside this band (e.g. 38%, 67%) still show the exact figure.

**Pass criteria:** Change the forecast horizon using the slider until
P(gain) falls near 50%. The table must show "Neutral (45–55%)", not "50%".

**Fail criteria:** Any value between 45 and 55 shown as a bare percentage (e.g. "49%").

**Note:** You may need to try a few stocks or horizons to find a case in the
neutral band. NSEI or broad ETFs tend to cluster near 50%.

---

### Fix 3 — Forecast deduplication (OPEN-010 / D-04)
**Audit ref:** D-04 | **Files changed:** `forecast.py`

**What changed:** If you view a stock's forecast, navigate away, then return
to the same stock's Forecast tab in the same session, the forecast now
updates rather than silently keeping the earlier entry.

**Where to look:**
- Page: Dashboard → Forecast tab
- Navigate to: Select RELIANCE.NS → Forecast tab → note the "Made On" date
  and forecast price → select a different stock → return to RELIANCE.NS →
  Forecast tab

**Before (v5.31):**
Revisiting the same stock on the same day silently discarded the new
forecast and kept the original, even if you changed the horizon.

**After (v5.32):**
The latest forecast for today replaces the earlier one. The table shows
the most recent entry for each ticker/horizon combination.

**Pass criteria:** Revisit the same stock's Forecast tab twice in one session.
Both visits should show a consistent forecast that reflects the current run.

**Fail criteria:** Forecast history shows two entries for the same ticker and
horizon with the same "Made On" date.

**Note:** This is most visible in extended sessions where a stock is revisited.

---

### Fix 4 — Dynamic section titles in Week Summary (OPEN-011 / D-06 / D-08)
**Audit ref:** D-06, D-08 | **Files changed:** `pages/week_summary.py`

**What changed:** All section headers in the Week Summary now show the actual
date range and whether data is for the current week or last week. Previously
all headers said "This Week" even on weekends when the data was from the
prior week.

**Where to look:**
- Page: Week Summary (default home view, or no stock selected)
- Navigate to: Open app without selecting any stock → observe section headings

**Before (v5.31):**
All sections showed "This Week" regardless of the actual date.
On a Saturday, the heading still read "📊 Group Performance This Week"
with no date reference.

**After (v5.32):**
- On a weekday: "🌐 Index Performance — This Week (Week of 24 Mar–28 Mar 2026)"
- On a weekend: "🌐 Index Performance — Last Week (Week of 24 Mar–28 Mar 2026)"
All five section headings now include this dynamic label.

**Pass criteria:** At least 3 section headings on the Week Summary page must
show the date range in grey text alongside the main title.

**Fail criteria:** Any section heading that says only "This Week" with no date
range, or a section that says "This Week" when tested on a Saturday or Sunday.

**Note:** Test is most revealing on weekends. On weekdays, "This Week" is
correct — confirm the date range still appears in the subtitle.

---

### Fix 5 — Weinstein override label (OPEN-012 / C-04)
**Audit ref:** C-04, Expert QA #14 | **Files changed:** `pages/dashboard.py`

**What changed:** When the Weinstein Stage analysis overrides the momentum
signal, the dashboard header now shows the specific stage and a clear
explanation instead of the generic "Momentum signal adjusted".

**Where to look:**
- Page: Dashboard → Charts tab header (verdict badge row)
- Navigate to: Select a stock in a Stage 3 or Stage 4 (declining/downtrend)
  with a positive short-term momentum. Stocks in correction often show this.

**Before (v5.31):**
Header showed: `⚠️ Momentum signal adjusted`
No indication of which framework overrode which.

**After (v5.32):**
Header shows: `⚠️ Stage 4 overrides momentum — see Insights`
(or Stage 3, Stage 2 depending on the detected stage)

**Pass criteria:** Find any stock where the verdict is WATCH despite positive
RSI/MACD signals. The header alignment label must name the Weinstein Stage
that caused the override.

**Fail criteria:** Header shows "Momentum signal adjusted" (old generic label)
or shows no conflict label when a conflict exists.

**Note:** Not all stocks will show this — it only fires when Weinstein Stage
conflicts with the momentum score. Large-cap indices in downtrend (e.g.
Hang Seng, or any stock near 52-week lows) are good candidates.

---

### Fix 6 — MACD timeframe labeling (OPEN-013 / C-06)
**Audit ref:** C-06 | **Files changed:** `pages/dashboard.py`

**What changed:** The MACD chart subplot and KPI panel card now explicitly
say "(Daily)" so users know they are reading daily MACD, not intraday.

**Where to look:**
- Page: Dashboard → Charts tab
- Navigate to: Select any stock (INFY.NS or AAPL) → Charts tab → scroll
  to the indicator subplots below the main candlestick chart

**Before (v5.31):**
Chart subplot header: "MACD"
KPI panel card label: "MACD Histogram"

**After (v5.32):**
Chart subplot header: "MACD (Daily)"
KPI panel card label: "MACD Histogram (Daily)"

**Pass criteria:** Both the chart subplot title and the KPI panel card label
must include "(Daily)".

**Fail criteria:** Either label shows plain "MACD" without the timeframe qualifier.

**Note:** The intraday MACD (if shown in live price fragment during market hours)
is a separate display — this fix applies to the main chart and KPI panel only.

---

### Fix 7 — GI watchlist filters to selected market (OPEN-014 / F-05)
**Audit ref:** F-05 | **Files changed:** `pages/global_intelligence.py`, `app.py`

**What changed:** The watchlist badges on Global Intelligence topic cards now
filter to the market selected in the sidebar. If you select "India" in the
market dropdown, the watchlist shows only Indian stocks. Previously it showed
all stocks regardless of market selection.

**Where to look:**
- Page: Global Intelligence
- Navigate to: Set sidebar market to "India" → Global Intelligence page →
  open any topic card → scroll to "📌 Related Stocks to Watch"
- Then: Change sidebar to "USA" → observe same section

**Before (v5.31):**
"Related Stocks to Watch" showed all watchlist stocks (Indian + US + others)
regardless of which market was selected in the sidebar.

**After (v5.32):**
With "India" selected: only `.NS`/`.BO` suffix stocks appear.
With "USA" selected: only US tickers (no suffix) appear.
If no stocks match the selected market: shows a note "No watchlist stocks for
[Market] market in this topic."

**Pass criteria:**
- With India selected: zero US tickers (NVDA, MSFT etc.) in any watchlist
- With USA selected: zero Indian tickers (RELIANCE.NS etc.) in any watchlist

**Fail criteria:** Any watchlist showing stocks from a different market than
the one currently selected in the sidebar.

**Note:** "All" market selection shows all watchlist stocks (baseline behaviour).

---

### Fix 8 — Market LIVE badge specificity (OPEN-015 / C-09)
**Audit ref:** C-09 | **Files changed:** `app.py`

**What changed:** The green LIVE badge in the sidebar now names the specific
market that is open, instead of the generic "Market LIVE".

**Where to look:**
- Page: Any page with the sidebar visible
- Navigate to: Use the app during market hours for any exchange → observe
  the green badge in the sidebar below the market dropdown

**Before (v5.31):**
Badge text: `🟢 Market LIVE — auto-refreshing`
No indication of which market is open.

**After (v5.32):**
Badge text: `🟢 India Market LIVE — auto-refreshing` (when India is selected
and NSE is open), or `🟢 USA Market LIVE — auto-refreshing` etc.

**Pass criteria:** The badge must include the country name from the sidebar
market selector.

**Fail criteria:** Badge shows "Market LIVE" without the market name.

**Note:** This can only be fully tested during actual market hours (NSE:
Mon–Fri 9:15–15:30 IST; NYSE: Mon–Fri 9:30–16:00 EST). Outside market hours
the red "CLOSED" badge shows — confirm it still appears correctly.

---

### Fix 9 — GI price coherence with ticker bar (OPEN-016 / G-04)
**Audit ref:** G-04 | **Files changed:** `pages/global_intelligence.py`

**What changed:** GI watchlist badges now use `cache_buster=0`, the same
cache key as the ticker bar. This guarantees both show the same price in the
same session — eliminating the "Nifty 22,820 in ticker bar vs 23,306 in GI"
class of divergence.

**Where to look:**
- Page: Global Intelligence
- Navigate to: Note the Nifty 50 price in the ticker bar at the top →
  open Global Intelligence → find a topic with `^NSEI` in its watchlist

**Before (v5.31):**
GI watchlist used `cache_buster=cb` (session-scoped), which could diverge
from the ticker bar's `cache_buster=0` if a Refresh had been triggered.

**After (v5.32):**
GI watchlist always uses `cache_buster=0`, matching the ticker bar's cache key.

**Pass criteria:** Record the Nifty price from the ticker bar. The same ticker
in the GI watchlist must show the same price (±0).

**Fail criteria:** Any price difference between the ticker bar and GI watchlist
for the same instrument in the same session.

**Note:** A fresh load (no Refresh pressed) may show both as "—" if the cache
is still warming. Press Refresh once and then compare — both should update to
the same value.

---

## 11. v5.32 Persona Test Matrix

Each fix mapped to which persona is most likely to catch a failure and
which is most harmed if the bug persists.

| Fix | Primary tester persona | Failure impact if missed |
|---|---|---|
| Fix 1 — 5-day consistency | Fundamental Analyst | Trust-breaking: two numbers for the same fact |
| Fix 2 — P(gain) neutral | Active Trader | False precision — 49% implies directional conviction |
| Fix 3 — Forecast dedup | Active Trader | Stale forecast silently persists in same session |
| Fix 4 — Dynamic week titles | Complete Beginner | Weekend user sees "This Week" — data is last week's |
| Fix 5 — Weinstein override | Quant / Systematic | Conflict disclosed but arbitration hidden |
| Fix 6 — MACD timeframe | Active Trader | User assumes intraday MACD when it's daily |
| Fix 7 — GI market filter | NRI / Global Investor | Indian-focused user sees US stocks they don't follow |
| Fix 8 — Specific LIVE badge | Casual Retail Investor | "Market LIVE" with no context — which market? |
| Fix 9 — GI price coherence | Fundamental Analyst | Two different prices for same stock on same screen |

**Recommended test order for a time-constrained QA session (30 min):**
Fix 1 → Fix 9 → Fix 5 → Fix 8 → Fix 4 (highest impact / easiest to verify)

---

## 12. v5.32 Cross-Page Data Consistency Baseline

Fill in during QA and keep for regression comparison in v5.33:

| Metric | v5.32 baseline value | Notes |
|---|---|---|
| Nifty 50 5-day % — Home | ___ | Record from Global Snapshot card |
| Nifty 50 5-day % — Dashboard | ___ | Must match Home within ±0.1% |
| Nifty 50 price — ticker bar | ___ | Record from scrolling ticker |
| Nifty 50 price — GI watchlist | ___ | Must match ticker bar exactly |
| Crude WTI price — ticker bar | ___ | |
| Crude WTI price — GI West Asia watchlist | ___ | Must match ticker bar |
| RELIANCE.NS verdict | ___ | BUY / WATCH / AVOID |
| RELIANCE.NS Weinstein Stage | ___ | 1–4 |
| RELIANCE.NS override label (if conflict) | ___ | Should name the stage |
| ROE shown for RELIANCE.NS | ___ | Should be N/A or actual % — not 0.0% |
| Week Summary "This Week" or "Last Week"? | ___ | Depends on day tested |
| Date range shown in section title | ___ | e.g. "24 Mar–28 Mar 2026" |


---

## 13. Complete Audit Finding Registry

> **⚠️ SUPERSEDED — 2026-03-29**
> This section has been superseded by `GSI_AUDIT_TRAIL.md`, which is the
> authoritative, append-only audit record. This section is preserved as a
> historical record of the pre-audit-trail format and will not be edited.
> For current finding status, reading order, and resolution records,
> refer to `GSI_AUDIT_TRAIL.md`.


**All findings from all 6 audit reports conducted on v5.28 (2026-03-28).**
Status legend: ✅ Fixed (version) | 🔶 Open (priority) | ⚠️ Known/Won't fix | 🔵 Decision pending

---

### Homepage Audit (v5.28 · Score: 6/10)

| ID | Finding | Priority | Status |
|---|---|---|---|
| H-01 | Nifty 50 5-day shows -9.4% on Home vs -1.3% on Dashboard — same session, same ticker | P1 | ✅ Fixed v5.32 (calc_5d_change utility) |
| H-02 | Global Trend Signals show "—" on first load with no loading state explanation | P2 | 🔶 Open (warmth guard shows placeholder, no user message) |
| H-03 | Market status cards wrap mid-word: "COMM ODI TIES" at standard viewport | P1 | ✅ Fixed v5.31 (short labels IND/USA/EUR/CHN/COMM/ETF) |

---

### Dashboard Audit (v5.28 · Score: 7/10)

| ID | Finding | Priority | Status |
|---|---|---|---|
| D-01 | Score 59/100 shown alongside WATCH verdict — confusing without explanation of why BUY was vetoed | P1 | ✅ Fixed v5.31 (Option B: raw score removed from header) |
| D-02 | ROE shows 0.0% for RELIANCE.NS — yfinance returns null, safe_float(None)=0.0 displayed as data | P0 | ✅ Fixed v5.31 (N/A guard: val != 0 else "N/A") |
| D-03 | Forecast P(gain) 46% displayed identically to 79% — no neutral zone for low-conviction signals | P1 | ✅ Fixed v5.32 (45–55% shows "Neutral") |
| D-04 | Forecast tracker creates duplicate same-day entries when stock revisited in same session | P1 | ✅ Fixed v5.32 (replace not skip on same-day) |
| D-05 | Week Summary state persists when navigating to Dashboard — no loading indicator shown | P2 | 🔶 Open |
| D-06 | Section headers say "Weekly +1.36%" and "Daily -2.09%" with no date range — contradictory without context | P1 | ✅ Fixed v5.32 (dynamic titles with date range) |
| D-07 | Elder Triple Screen verdict labels (BUY SETUP / WAIT) use jargon not plain English | P2 | 🔶 Open |
| D-08 | "This Week" on all week_summary headers even on weekends when data is from prior week | P1 | ✅ Fixed v5.32 (dynamic "Last Week" on weekends) |
| D-09 | Forecast correction factor applied silently — user shown adjusted forecast with no disclosure | P2 | 🔶 Open |

---

### Global Intelligence Audit (v5.28 · Score: 3/10)

| ID | Finding | Priority | Status |
|---|---|---|---|
| G-01 | WorldMonitor embedded map blocked by CSP (frame-ancestors). Appeared as blank white space | P0 | ⚠️ Won't fix — replaced with external link button |
| G-02 | Only 4 topic cards — insufficient for a page claiming "Global Intelligence Centre" | P2 | 🔶 Open — new topics require India impact formula |
| G-03 | Impact chain nodes overflow at 1280px standard viewport | P2 | 🔶 Open |
| G-04 | Ticker bar shows Nifty 22,820 while GI watchlist shows 23,306 — same session | P1 | ✅ Fixed v5.32 (cache_buster=0 in GI watchlist) |
| G-05 | GI subtitle claims "Real-time geopolitical & technology trends" while serving stale content | P1 | ✅ Partially fixed v5.31 (Live Headlines date-gated) |

---

### Expert QA Report (v5.28 · Score: 5.5/10 · 43 findings total)

High and critical findings listed. Full 43-finding report available from QA analyst.

| ID | Finding | Priority | Status |
|---|---|---|---|
| #14 | Elder Triple Screen and Weinstein Stage shown at equal visual weight with no arbitration disclosed | P1 | ✅ Fixed v5.32 (override label names the stage) |
| #29 | Zero investment disclaimers anywhere on the platform — full liability exposure | P0 | ✅ Fixed v5.31 (SEBI disclaimer + algorithmic disclosure) |
| #32 | AI-generated narrative not labeled as algorithmic output — appears as human analysis | P0 | ✅ Fixed v5.31 (algorithmic disclosure banner) |
| #33 | "Invest in NVDA, TSM, MSFT Azure" in GI with no disclaimer or signal context | P0 | ✅ Fixed v5.31 (What You Should Do Next removed) |
| #38 | GI page subtitle "Real-Time" claim while map is broken and content is 3 years old | P1 | ✅ Partially fixed v5.31 (date gate on Live Headlines) |
| #41 | Forecast accuracy tracker has no visual baseline — user cannot tell if 65% accuracy is good or bad | P2 | 🔶 Open |
| #43 | No data export anywhere — quants and advisors cannot extract signals for external use | P3 | 🔶 Open (v6 roadmap) |

---

### Data Dependency Report (v5.28 · Score: 2/10 · 9 cross-page conflicts)

| ID | Finding | Priority | Status |
|---|---|---|---|
| C-01 | AI narrative says "no major red flags" while 9/12 US sectors are negative — Watch Out For uses no sector data | P0 | ✅ Fixed v5.31 (RSI/MACD-aware fallback) + 🔶 Open (sector breadth still not wired to narrative) |
| C-02 | Gold +3.92% visible in ticker bar while stock-level AI narrative says "no macro risk" | P1 | 🔶 Open — requires OPEN-018 (Claude API integration) |
| C-03 | RSI 36 (bearish, approaching oversold) described as "neutral momentum zone" in AI text | P1 | 🔶 Open — requires OPEN-018 (Claude API integration) |
| C-04 | Elder Triple Screen BUY SETUP + Weinstein WAIT shown simultaneously with no resolution | P1 | ✅ Fixed v5.32 (override label names the stage) |
| C-05 | Momentum Score 58/100 shown with no scale definition, no per-indicator breakdown | P2 | 🔶 Open (OPEN-RISK-003 / C-05) |
| C-06 | MACD on chart is daily; MACD in KPI panel refreshes every 60s (intraday) — unlabeled | P1 | ✅ Fixed v5.32 (MACD (Daily) label on chart and panel) |
| C-07 | Price shown in multiple currencies with no conversion — EUR-listed stocks vs USD context | P3 | 🔶 Open |
| C-08 | Sector breadth (9/12 US sectors negative) computed correctly but never passed to AI narrative | P1 | 🔶 Open — requires OPEN-018 (Claude API integration) |
| C-09 | "Market LIVE" badge active at 2AM Saturday — all markets closed | P1 | ✅ Fixed v5.32 (badge names specific market + gated on market_open bool) |

---

### 360° Bird's Eye View (v5.31 · Score: 5.5/10)

| ID | Finding | Priority | Status |
|---|---|---|---|
| F-01 | Only 2 topic cards visible on GI page (others collapsed) — page looks empty on first load | P1 | ✅ Fixed v5.31 (expanded=True by default) |
| F-02 | India Impact text is a static formula — not computed from live Crude WTI price | P1 | 🔶 Open (OPEN-014 improved market filter; India formula still static) |
| F-03 | TechCrunch RSS serving 2022–2023 articles labeled "Live" | P0 | ✅ Fixed v5.31 (stale feeds replaced + 48h date gate) |
| F-04 | GI watchlist stocks hardcoded — ignores market selector | P1 | ✅ Fixed v5.32 (_market_of() filter + selected_market param) |
| F-05 | GI watchlist always shows India stocks regardless of market selector | P1 | ✅ Fixed v5.32 (same as F-04) |
| F-06 | "What You Should Do Next" — career advice disconnected from live market data | P0 | ✅ Fixed v5.31 (section removed) |
| F-07 | Forecast accuracy report visible in Week Summary but Forecast tab has no link to it | P3 | 🔶 Open |
| F-08 | Portfolio Allocator has no export — cannot download recommended weights | P3 | 🔶 Open (v6 roadmap) |
| F-09 | Compare tab normalises to 100 at period start but no disclosure of normalisation method | P2 | 🔶 Open |
| F-10 | Impact chain overflows at 1280px standard viewport (same as G-03) | P2 | 🔶 Open |
| F-11 | Momentum score shown in header before verdict badge — misleads P1 Glancer persona | P0 | ✅ Fixed v5.31 (Option B: score removed from header) |
| F-12 | Named stock investment recommendations (NVDA, TSM, MSFT) without disclaimer | P0 | ✅ Fixed v5.31 (section removed) |
| F-13 | India Impact formula is static string — "every $10/bbl rise adds ₹1.2L cr to import bill" | P1 | 🔶 Open |
| F-14 | West Asia section makes quantitative claims with no source attribution or date | P1 | 🔶 Open |
| F-15 | All GI topic cards collapsed on first load — page appears empty to Complete Beginner | P1 | ✅ Fixed v5.31 (expanded=True by default) |

---

### Summary Table — All Findings by Status

| Status | Count | Notes |
|---|---|---|
| ✅ Fixed v5.31 | 11 | All 8 QA-verified fixes + 3 additional |
| ✅ Fixed v5.32 | 9 | All 9 OPEN items from v5.32 sprint |
| 🔶 Open | 17 | Tracked in GSI_session.json open_items |
| ⚠️ Known / Won't fix | 1 | G-01 WorldMonitor CSP — replaced with link |
| 🔵 Decision pending | 1 | D-02 ROE benchmark (industry avg comparator) |
| **Total** | **39** | Across 6 reports, v5.28 baseline |

---

### Open Findings Tracker (as of v5.32)

Findings still open, mapped to their OPEN-XXX tracking ID:

| Finding ID | Description (short) | Mapped to | Target |
|---|---|---|---|
| H-02 | No loading state explanation on first load | — | v5.33 consideration |
| D-05 | Week Summary state persists on Dashboard load | — | v5.33 consideration |
| D-07 | Elder labels use jargon (BUY SETUP / WAIT) | — | v5.33 consideration |
| D-09 | Correction factor applied silently | — | v5.33 consideration |
| G-02 | Only 4 GI topic cards | — | v6 roadmap |
| G-03 / F-10 | Impact chain overflows at 1280px | — | v5.33 consideration |
| #41 | Forecast accuracy has no visual baseline | — | v5.33 consideration |
| #43 | No data export anywhere | — | v6 roadmap |
| C-01 (partial) | Sector breadth not wired to AI narrative | OPEN-018 | Future phase |
| C-02 | Macro data not wired to stock-level narrative | OPEN-018 | Future phase |
| C-03 | RSI 36 described as neutral in AI text | OPEN-018 | Future phase |
| C-05 | Score 58/100 has no scale or breakdown | RISK-003 | v5.33 |
| C-07 | Multi-currency without conversion disclosure | — | v6 roadmap |
| C-08 | Sector breadth computed but not passed to AI | OPEN-018 | Future phase |
| F-02 / F-13 | India Impact static formula | OPEN-018 | Future phase |
| F-07 | No link from Forecast tab to Accuracy Report | — | v5.33 consideration |
| F-08 / F-09 | No Portfolio export, no normalisation disclosure | — | v6 roadmap |
| F-14 | West Asia content unsourced | — | v5.33 consideration |
| D-02 benchmark | ROE card with no industry comparator | OPEN-ROE | v5.33 |


---

## 11. v5.34 QA Brief — Observability, UX, P0 Compliance

**Version:** v5.34 | **Date:** 2026-04-01 | **Fixes:** 5 | **Regression baseline:** 415/415

---

### Fix 1 — Observability dashboard (Phase 1)
**Files changed:** `market_data.py`, `pages/observability.py`

**What changed:** New founder-only internal page accessible via direct Streamlit MPA URL. Gated by `st.secrets["DEV_TOKEN"]` PIN. Two tabs: App Health (live cache/rate-limit stats, latency chart, market sessions) and Program (sprint manifest, audit counts, risk register, compliance check, velocity chart).

**Where to look:** Navigate directly to the observability page URL (e.g. `<app_url>/observability`).

**Before:** No internal visibility into cache health, rate-limit state, or program status.

**After:** App Health tab shows cache hit rate, P95 fetch latency, rate-limit cooldown state, and all 9 market session statuses. Program tab shows sprint manifest summary, audit trail counts, inline 8-gate compliance check.

**Pass criteria:**
- Without `DEV_TOKEN` set in secrets: page shows PIN entry form, nothing else visible
- With correct PIN: App Health tab renders within 5s, all metric tiles have values
- Program tab: compliance check shows 8/8 passed; version log shows v5.34 as latest

---

### Fix 2 — D-05: Loading indicator on Dashboard navigation
**Audit ref:** D-05 | **File changed:** `app.py`

**What changed:** When a user selects a new stock, `data_stale=True` triggers `st.spinner("Loading <stock name>…")` wrapping the data fetch and dashboard render. Spinner clears after render.

**Where to look:** Sidebar → select any market → select a group → select a stock.

**Before:** After clicking a stock, the page went blank (or showed stale content) with no indication that data was loading. Could take 2–4s with no feedback.

**After:** "Loading <stock name>…" spinner appears immediately on stock selection, disappears when the dashboard renders.

**Pass criteria:** Select a stock not previously visited in the session. A spinner with the stock name appears within 0.5s of selection and disappears when the dashboard header is visible.

---

### Fix 3 — G-03 / F-10: Impact chain overflow at 1280px
**Audit ref:** G-03, F-10 | **File changed:** `pages/global_intelligence.py`

**What changed:** `width:100%; max-width:100%; box-sizing:border-box` added to the outer `div` of `_render_impact_chain()`. The `overflow-x:auto` scroll was already present but the container lacked explicit width constraints.

**Where to look:** Global Intelligence tab → any topic card → expand → scroll to the Impact Chain section.

**Before:** At 1280px viewport, the impact chain nodes would overflow the column boundary, causing horizontal scrolling of the full page rather than just the chain container.

**After:** At 1280px, the chain container scrolls horizontally within its column bounds. The rest of the page layout is unaffected.

**Pass criteria:** Open at 1280px width (or use browser dev tools). Expand any topic card. The impact chain should show a horizontal scrollbar confined to the chain container. The page-level scrollbar should be vertical only.

---

### Fix 4 — F-14: West Asia quantitative attribution
**Audit ref:** F-14 | **Files changed:** `config.py`, `pages/global_intelligence.py`

**What changed:** An `attribution` field added to the West Asia Conflict topic in `GLOBAL_TOPICS`. Rendered as `st.caption("Sources: …")` above the watchlist badges when present.

**Where to look:** Global Intelligence tab → expand "🔴 West Asia Conflict" → look below the India Impact box.

**Before:** Specific quantitative claims (oil sensitivity: ₹1.2L cr per $10/bbl; freight: +30%; rupee impact: 50–80 paise) had no source attribution.

**After:** A caption line reads: "Sources: Figures sourced from Reuters, Al Jazeera, and US EIA reports (2024–2025). Oil price sensitivity estimates: PPAC India. Freight cost data: Drewry World Container Index. Content reviewed periodically; not updated in real time."

**Pass criteria:** The attribution caption is visible in the West Asia card. No other topic card shows an attribution caption (it is conditional on the field being present).

---

### Fix 5 — P0 compliance: raw score removed from header; ROE null guard
**Files changed:** `pages/dashboard.py`

**What changed:**
- `Momentum: {score}/100` span removed from `_render_header_static()` — score now only visible in the KPI panel
- `roe_str` null guard added: `sig["roe"] == 0` (yfinance null) now displays `"N/A"` instead of `"0.0%"`

**Where to look:** Select any stock → Dashboard header area (below the stock name).

**Before:** A small grey badge reading e.g. "Momentum: 62/100" appeared beside the verdict badge in the header. For Indian stocks where yfinance returns null ROE, the KPI panel showed "ROE: 0.0%".

**After:** Header shows only the verdict badge and the plain-English alignment note. ROE KPI shows "N/A" when the data is unavailable.

**Pass criteria:**
- Header: no "Momentum: XX/100" text visible anywhere in the header card. Score is visible only in the KPI panel row.
- ROE: select an Indian stock (e.g. RELIANCE.NS). If ROE data is unavailable, the KPI panel should show "N/A · X.X%" not "0.0% · X.X%".

---

## v5.34.1 QA Brief — Claude Code Hook Infrastructure (2026-04-05)

**Sprint type:** Infrastructure — no UI changes. No visual before/after possible.
**Regression baseline before sprint:** 427/427 PASS
**Regression baseline after sprint:** 446/450 (4 Tier-A sprint-close doc checks pending; not implementation failures)

**What was built:**
- `compliance_check.py` — 8-check pre-push gate (extracted from CLAUDE.md inline script)
- `.claude/hooks/pre_commit.sh` — blocks `git commit` via Claude Code if regression fails
- `.claude/hooks/pre_push.sh` — blocks `git push` via Claude Code if compliance checks fail
- `.claude/hooks/post_edit.sh` — audits doc coherence after any `*.md` write/edit
- `settings.json` — hooks block wired; sync_docs --check migrated from settings.local.json

**How to verify each hook fires correctly:**

### Hook 1 — pre_commit.sh (regression gate)
**Before:** Claude Code can issue `git commit` even if regression is failing.
**After:** Claude Code `git commit` is blocked (exit 2) when `python3 regression.py` fails.

**Test procedure:**
1. Introduce a deliberate regression failure (e.g. add `'Momentum: {score}/100'` to `pages/dashboard.py`)
2. Ask Claude Code to commit the file
3. **Expected:** Claude Code is blocked — you should see the regression output and `BLOCKED` message; the commit does not proceed

**Pass criteria:** The commit does not happen. Revert the test change.

---

### Hook 2 — pre_push.sh (compliance gate)
**Before:** Claude Code can `git push` even if compliance checks fail.
**After:** Claude Code `git push` is blocked (exit 2) when `python3 compliance_check.py` fails.

**Test procedure:**
1. Temporarily remove the SEBI disclaimer line from `pages/dashboard.py`
2. Ask Claude Code to push to GitHub
3. **Expected:** Push is blocked — you should see `FAIL: SEBI disclaimer` and `BLOCKED` message; no network push occurs

**Pass criteria:** The push does not reach GitHub. Revert the test change.

---

### Hook 3 — post_edit.sh (doc audit)
**Before:** No automatic doc coherence check after markdown edits.
**After:** Any `*.md` write/edit triggers `sync_docs.py --check`; clean passes are silent (suppressOutput).

**Test procedure:**
1. Ask Claude Code to make a small edit to any `*.md` file
2. **Expected clean pass:** No output from the hook — the edit appears with no extra messages
3. To see a non-silent result: introduce a deliberate doc inconsistency (ask Claude to check `sync_docs.py --check` independently to understand what it checks)

**Pass criteria:** Clean edits produce no hook output. The hook does not block any write (PostToolUse cannot block).

---

**Note on exit codes (ADR-020):** Exit 2 blocks PreToolUse; exit 1 is non-blocking (common mistake to avoid). PostToolUse hooks always exit 0 — they cannot block operations.


---

## v5.34.2 QA Brief — Regression Hardening + Sprint Close
**Sprint type:** Infrastructure (no UI changes)
**Date:** 2026-04-05
**Baseline change:** 427 → 432 PASS (R28 adds 5 hook existence checks)

### Area 1 — R28 regression checks

**Before:** No automated verification that hook scripts and compliance tooling exist on disk. If files were deleted or missed during setup, the pipeline would silently break.
**After:** 5 R28 checks run every time `python3 regression.py` is executed.

**Test procedure:**
1. Run `python3 regression.py`
2. **Expected output:** `ALL 432 CHECKS PASS` (exact text)
3. Verify R28 section shows 5/5 OK in the per-category breakdown
4. Negative test: rename `.claude/hooks/pre_commit.sh` temporarily → regression reports R28 failure; restore and re-run to confirm 432/432 again

**Pass criteria:** `ALL 432 CHECKS PASS` with R28 showing 0 failures.

---

### Area 2 — CTO review fixes verification

**C-1: sync_docs.py exit code fix**
**Before:** `sync_docs.py --check` exited 0 even when issues were found, making the post_edit.sh error branch unreachable.
**After:** Exits 1 on issues, 0 on clean pass.

**Test procedure:**
1. Run `python3 sync_docs.py --check`
2. **Expected (clean repo):** exits 0, output ends with `All checks passed`
3. Deliberate-issue test: introduce a version mismatch (e.g. edit a doc to reference a non-existent version), then run `python3 sync_docs.py --check` — **expected:** non-zero exit (you can verify with `echo $?`)
4. Restore the deliberate change

**Pass criteria:** Clean repo exits 0. Dirty repo exits non-zero.

---

**C-2: observability.py path fix**
**Before:** `_read_file_safe("dashboard.py")` at repo root returned empty (file is at `pages/dashboard.py`), causing false compliance failures on the Program tab.
**After:** Path corrected to `pages/dashboard.py`.

**Test procedure:**
1. Run `python3 compliance_check.py`
2. **Expected output:** `8/8 compliance checks passed` (exact text) followed by `✅ All compliance checks passed — safe to deploy`

**Pass criteria:** `8/8 compliance checks passed` with no FAIL lines.

---

**M-1: git rev-parse replaces CLAUDE_PROJECT_DIR in hooks**
**Before:** Hook scripts used `CLAUDE_PROJECT_DIR` env variable (not always set in hook execution context), causing bash errors.
**After:** All hooks use `REPO=$(git rev-parse --show-toplevel)` — git-native, always reliable.

**Test procedure:**
1. Attempt a git commit via Claude Code (modify any tracked file)
2. **Expected:** pre_commit.sh fires, runs regression, no "CLAUDE_PROJECT_DIR: unbound variable" errors
3. Attempt a git push via Claude Code
4. **Expected:** pre_push.sh fires, runs compliance check, no bash variable errors

**Pass criteria:** No unbound variable errors in hook output.

---

### Area 3 — Hook wiring end-to-end smoke test

**Before:** Hook infrastructure was new in v5.34.1; CTO review found path and exit-code bugs.
**After:** All 3 bugs fixed; hooks are confirmed working.

**Test procedure (Claude Code session):**
1. Ask Claude Code to edit any `.md` file (e.g. add a blank line to CLAUDE.md)
2. **Expected:** post_edit.sh fires silently (no output) on clean pass
3. Ask Claude Code to commit the change
4. **Expected:** pre_commit.sh runs regression; commit proceeds if 432/432 pass
5. Verify run_state.json is written to `.claude/run_state.json` (dedup cache)

**Pass criteria:** All 3 hooks fire without errors. Commit succeeds with 432/432.

---

## v5.35 QA Brief — Launch Readiness Sprint

**Version:** v5.35 | **Date:** 2026-04-06 | **Fixes:** 4 | **Regression baseline:** 433/433

**Sprint summary:** MVP launch readiness. Analytics integration (S-03), GitHub Pages landing page (S-02), social media compliance guidelines (S-04 / RISK-L04), and formal ADR for WorldMonitor CSP stopgap (S-01 — no UI change, doc-only).

**Personas to test:** Complete Beginner (landing page), Financial Advisor/PM (disclaimer copy), Developer (analytics/hook verification).

---

### Fix 1 — streamlit-analytics2 integration (S-03)

**Audit ref:** S-03 (CEO sign-off)
**Files changed:** `app.py`, `requirements.txt`
**Function changed:** module-level (top of app.py routing section)

#### What changed
`streamlit_analytics.start_tracking()` and `stop_tracking()` now wrap the full routing section of `app.py`; `streamlit-analytics2` added to `requirements.txt`. The integration is fail-safe — if the package is absent, `_ANALYTICS_ENABLED = False` and the app runs normally.

#### Where to look
Page: Any — analytics is invisible to end users during normal operation.
Navigate to: Open app in a browser → navigate between Home, Dashboard, and Global Intelligence tabs.
Admin view: Append `?analytics=on` to the app URL (if streamlit-analytics2 admin panel is enabled — password-protected or open depending on version).

#### Before (v5.34.2)
No usage tracking. No data on which markets, stocks, or pages are accessed. No page view counts.

#### After (v5.35)
Page views tracked silently. No visible change to the user interface. App startup does not slow down. No new UI elements on any page.

#### Pass criteria
App loads normally on first visit. No Python traceback visible in the app. Navigation between all pages (Home → Dashboard → Global Intelligence) works without error. If the analytics admin panel loads at `?analytics=on`, it shows page view counts > 0 after a few navigations.

#### Fail criteria
- Any `ModuleNotFoundError: No module named 'streamlit_analytics'` visible in the app
- App throws an exception on startup related to the analytics import
- Any new UI element appearing on Home, Dashboard, or Global Intelligence pages that was not there before

#### Note
Analytics admin panel appearance depends on streamlit-analytics2 version and whether a password is configured. Absence of the admin panel is NOT a failure — only errors in app startup or navigation are failures.

---

### Fix 2 — GitHub Pages landing page (S-02)

**Audit ref:** S-02 (CEO sign-off)
**Files changed:** `docs/index.html`
**Function changed:** New file — static HTML

#### What changed
A single-page GitHub Pages landing site was created at `docs/index.html`. Sections: sticky nav, hero with CTA, stats bar (9 markets / 559 tickers / 38 groups / 4 tabs), screenshot placeholder slots (3), signal engine demo with mock verdict table, 6-feature grid, 9-market coverage grid, SEBI disclaimer box, CTA band, footer.

#### Where to look
Page: GitHub Pages — `https://tarun19k.github.io/stock-intelligence-test-1-vs/` (after GitHub Pages is enabled in repo settings → Pages → branch: main, folder: /docs)
Navigate to: Open the URL directly in a browser. Scroll top-to-bottom.
Alternatively: Open `docs/index.html` in a local browser by double-clicking the file.

#### Before (v5.34.2)
No landing page existed. `docs/` directory only contained `sprint_archive/`. No public marketing presence.

#### After (v5.35)
`docs/index.html` is a complete dark-theme one-pager with: hero headline + two CTAs, 4-stat bar, 3 screenshot placeholder slots, signal engine explainer with live-looking verdict mockup, 6-feature cards, 9-market flag grid, legal disclaimer box with SEBI language, footer with GitHub and app links.

#### Pass criteria
- Page loads without browser errors in Chrome/Safari/Firefox
- All 3 CTAs ("Open Dashboard →") link to the Streamlit app URL
- SEBI disclaimer section is visible without scrolling more than 80% down the page
- Page is readable on a mobile viewport (320px wide): no horizontal overflow, text is legible
- At 1280px viewport: no element overflows its container

#### Fail criteria
- Broken layout at 1280px (content overflows, columns collapse incorrectly)
- Missing SEBI disclaimer box (regulatory requirement — P0 if absent)
- "Open Dashboard →" buttons link to the wrong URL or 404
- Screenshot slots show broken images instead of placeholder text

#### Note
Screenshot slots are intentionally empty (placeholder text) until CEO provides actual app screenshots. Replacing them requires editing the `screenshot-slot` div classes — see HTML comment in the file. Absence of real screenshots is NOT a failure for v5.35.

---

### Fix 3 — Social media guidelines doc (S-04 / RISK-L04)

**Audit ref:** RISK-L04 (Risk Register)
**Files changed:** `docs/social-media-guidelines.md` (new), `GSI_RISK_REGISTER.md`
**Function changed:** New doc file; risk register row update

#### What changed
`docs/social-media-guidelines.md` created with 5 sections: approved content, prohibited content, platform-specific rules (Reddit, Product Hunt, Twitter/X, LinkedIn), SEBI Finfluencer rules, and launch sequence. `GSI_RISK_REGISTER.md` RISK-L04 status updated `Open → Mitigated`.

#### Where to look
Doc: Open `docs/social-media-guidelines.md` in any Markdown viewer or text editor.
Risk register: Open `GSI_RISK_REGISTER.md` and search for `RISK-L04`.

#### Before (v5.34.2)
RISK-L04 was `Open` with a brief note in the risk register only. No actionable guidance existed for what to post or not post on social media about the tool.

#### After (v5.35)
`docs/social-media-guidelines.md` provides explicit rules. Examples of prohibited content: "Screenshot showing RELIANCE.NS: BUY — this is prohibited even with a disclaimer." Examples of approved content: methodology diagrams, historical examples, developer progress updates. RISK-L04 is `Mitigated` in the risk register.

#### Pass criteria
- `docs/social-media-guidelines.md` exists and opens without error
- The word "SEBI" appears in the document (required for manifest check)
- Section 2 (Prohibited Content) explicitly names live BUY/WATCH/AVOID screenshots as prohibited
- `GSI_RISK_REGISTER.md` RISK-L04 row shows `Mitigated` (not `Open`)
- Risk Summary Dashboard shows `Open: 8` and `Mitigated: 10`

#### Fail criteria
- `docs/social-media-guidelines.md` missing or empty
- RISK-L04 still shows `Open` in the risk register
- No explicit prohibition on live signal screenshots in the document

#### Note
This is a policy document, not a code change. No app UI changes are expected. Full enforcement depends on human behaviour — the doc mitigates the risk by documenting intent, not by technical controls.

---

### Fix 4 — WorldMonitor CSP stopgap — ADR-022 (S-01 formal record)

**Audit ref:** G-01, ADR-022
**Files changed:** `GSI_DECISIONS.md`
**Function changed:** Append-only doc change; no code change

#### What changed
ADR-022 formally records the WorldMonitor iframe → link-button decision (already implemented in a prior session). No UI change in this sprint. The expander and link button already exist in `pages/global_intelligence.py`.

#### Where to look
App: Open app → Global Intelligence tab → expand "🗺️ WorldMonitor — Live Interactive Global Events Map"
Doc: Open `GSI_DECISIONS.md` and search for `ADR-022`

#### Before (v5.34.2)
The link button was already present in the UI (no change). ADR-022 did not exist as a formal decision record.

#### After (v5.35)
`GSI_DECISIONS.md` contains ADR-022 documenting: why the iframe was replaced, what alternatives were rejected (proxy, CSP header override), and what the long-term fix is (OPEN-020 Leaflet.js).

#### Pass criteria
- In the app: "🗺️ WorldMonitor — Live Interactive Global Events Map" expander is visible on the Global Intelligence page
- Clicking "🗺️ Open WorldMonitor Live Map" opens `https://worldmonitor.app` in a new browser tab
- Caption below the button reads: "WorldMonitor cannot be embedded here due to their Content Security Policy. Click above to open the live map in a new tab."
- In `GSI_DECISIONS.md`: `ADR-022` section exists with "WorldMonitor" in the title

#### Fail criteria
- Blank/grey area where WorldMonitor should appear (CSP block showing as broken embed — means the iframe was accidentally restored)
- Link button missing from the expander
- ADR-022 absent from GSI_DECISIONS.md

#### Note
The worldmonitor.app URL is external and not controlled by this project. If the site itself is down or unavailable, that is not a failure of this fix. Only verify that the link button exists and points to the correct URL.

---

### Cross-page spot check (Section 9 baseline)

Record these 6 values at the start of each test session and compare to previous run:

| Reading | Value | Expected |
|---|---|---|
| Nifty 50 5-day % on Home page | ___ | Must match Dashboard within ±0.1% |
| Nifty 50 5-day % on Dashboard (same session) | ___ | Must match Home within ±0.1% |
| Crude WTI price in ticker bar | ___ | Must match GI West Asia watchlist within ±0.5% |
| Crude WTI price in GI West Asia watchlist | ___ | Must match ticker bar within ±0.5% |
| Verdict for RELIANCE.NS | ___ | Record only — no expected value (market-dependent) |
| ROE shown for RELIANCE.NS | ___ | Must show `N/A` or a non-zero % (never `0.0%`) |

Discrepancies greater than tolerance are **P1 data coherence bugs**. OPEN-008 and OPEN-016 (fixed v5.32) — if values diverge, report as regression.

---

### What I need back from QA

**Must-have (block ship if missing):**
- [ ] Fix 1 pass/fail: does the app load without `streamlit_analytics` error?
- [ ] Fix 2 pass/fail: does `docs/index.html` render correctly at 1280px and mobile?
- [ ] Fix 2: is the SEBI disclaimer box visible on the landing page?
- [ ] Fix 4: does the WorldMonitor link button open the correct URL?
- [ ] Cross-page spot check completed (6 readings recorded)

**Good-to-have (ship regardless, note for v5.36):**
- [ ] Fix 2: screenshot on mobile viewport (320px) showing no horizontal overflow
- [ ] Fix 2: feedback on landing page copy — does the hero headline land with a non-technical reader?
- [ ] Fix 3: is the prohibited content list specific enough, or are there edge cases to add?
- [ ] Analytics admin panel confirmed working at `?analytics=on`
- [ ] Landing page CTA clicks tracked in analytics (confirms full integration)

---

## v5.35.1 QA Brief — Post-Sprint Hotfix (2026-04-06)

**Tester:** Tarun Kochhar (self-verify — no UI design changes)
**Scope:** 3 ticker bugfixes with visible runtime behaviour. Governance/planning changes have no UI surface.

---

## Fix 1 — M&M.NS ampersand preserved (safe_ticker_key)

**File changed:** `utils.py`
**Function changed:** `safe_ticker_key()`

### What changed
`[^A-Za-z0-9.\-^=]` → `[^A-Za-z0-9.\-^=&]` — ampersand now passes through the sanitiser.

### Where to look
Page: Dashboard → Nifty 50 group or any group containing Mahindra & Mahindra
Navigate to: Home → select India → select NIFTY 50 group → scroll to M&M

### Before
Terminal showed: `$MM.NS: possibly delisted; no price data found` — Mahindra & Mahindra card showed no data or error state.

### After
M&M.NS fetches cleanly. Mahindra & Mahindra card shows price, signals, and KPIs normally.

### Pass criteria
No `MM.NS` error in terminal. Mahindra & Mahindra card loads with a price and verdict.

### Fail criteria
Terminal still shows `MM.NS` 404 error after reload.

---

## Fix 2 — Ambuja Cements ticker corrected (AMBUJACEM.NS)

**File changed:** `tickers.json`

### What changed
`AMBUJACEMENT.NS` → `AMBUJACEM.NS` (typo — extra "ENT" suffix not part of NSE symbol).

### Where to look
Page: Dashboard → Nifty Next 50 group → Ambuja Cements card

### Before
Terminal showed: `HTTP Error 404: Quote not found for symbol: AMBUJACEMENT.NS`

### After
`AMBUJACEM.NS` fetches cleanly. Ambuja Cements card shows price and signals.

### Pass criteria
No `AMBUJACEMENT.NS` 404 error in terminal. Ambuja Cements card loads data.

### Fail criteria
404 error persists for `AMBUJACEMENT.NS`.

---

## Fix 3 — Zomato + Paytm removed from IT & Technology group

**File changed:** `tickers.json`

### What changed
Zomato and Paytm removed from `IT & Technology` sector group (food delivery and fintech respectively). Both remain in Nifty Next 50.

### Where to look
Page: Dashboard → IT & Technology sector group

### Before
Zomato and Paytm appeared in IT & Technology ticker list.

### After
IT & Technology no longer contains Zomato or Paytm. Both still appear in Nifty Next 50.

### Pass criteria
IT & Technology group does not contain Zomato or Paytm entries. Nifty Next 50 still shows both.

### Fail criteria
Either stock still visible in the IT & Technology group.

### Note
Governance and planning changes (Rule 8, tiered capacity, token budget fields) have no UI surface — not in scope for QA.

---

## Cross-page spot check — v5.35.1

| Reading | Location A | Location B | Match? |
|---|---|---|---|
| 5-day % for RELIANCE.NS | Home ticker bar | Dashboard KPI panel | |
| Verdict badge for TCS.NS | Home group card | Dashboard header | |
| Market status (India) | Home LIVE badge | Dashboard tab label | |
| Nifty 50 index price | Home indices row | Week Summary market card | |
| HDFC Bank RSI | Dashboard KPI panel | Dashboard chart tooltip | |
| Sector breadth | Week Summary group view | Global Intelligence watchlist | |

## What I need back from QA

**Must-have:**
- [ ] Fix 1 pass/fail: M&M.NS loads without terminal error
- [ ] Fix 2 pass/fail: AMBUJACEM.NS loads without terminal error
- [ ] Fix 3 pass/fail: Zomato/Paytm absent from IT & Technology

**Good-to-have:**
- [ ] Vodafone Idea (IDEA.NS) — does it load or show intermittent errors? (watch item for v5.36)

---

# QA Brief — v5.36 Post-Launch Hardening

**Sprint:** v5.36 | **Date:** 2026-04-07 | **Session:** session_019
**Scope:** Proxy infrastructure (PROXY-01–07) + D-02 bench + OPEN-006 stability UI + EQA-41 calibration chart
**Regression baseline entering:** 434 | **Baseline exiting:** 434

---

## Fix 1 — Portfolio stability score added to Portfolio Allocator (OPEN-006)

**File changed:** `pages/week_summary.py`

### What changed
After the metric cards in the Portfolio Allocator tab, a new "Allocation Stability" section appears. It runs a 10× perturbation test (±5% noise on return scenarios) and reports STABLE / MODERATE / UNSTABLE with a colour-coded KPI badge. An expandable panel shows per-stock weight sensitivity (coloured horizontal bars).

### Where to look
Page: Week Summary → any sector group → Portfolio Allocator tab → scroll below metric cards

### Before
No stability indication. User had to trust allocation output blindly.

### After
Green badge: STABLE (weights consistent across perturbations). Orange: MODERATE. Red: UNSTABLE. Expandable details show which stocks drive instability.

### Pass criteria
- [ ] Portfolio Allocator tab shows "Allocation Stability" section below metric cards
- [ ] Badge colour matches verdict (green/orange/red)
- [ ] Expandable "Weight sensitivity" panel opens and shows per-stock bars
- [ ] No Python exception in terminal when section renders

### Fail criteria
- Section missing entirely
- `AttributeError` on `compute_stability_score`
- Badge always shows UNKNOWN regardless of portfolio

---

## Fix 2 — Forecast accuracy calibration chart (EQA-41)

**File changed:** `pages/week_summary.py`

### What changed
The Forecast Accuracy report section (Week Summary → group view → Forecast Accuracy tab) now includes a Plotly horizontal bar chart below the KPI cards. Each bar shows actual accuracy vs the target baseline, with dotted reference lines. Bars are colour-coded: green = on/above target, red = below target.

### Where to look
Page: Week Summary → any sector group → Forecast Accuracy tab (if resolved forecasts exist)

### Before
KPI cards only (plain metric numbers). No visual calibration.

### After
Horizontal bar chart below the KPI cards. X-axis is percentage, Y-axis is each metric. Dotted vertical reference lines at each target.

### Pass criteria
- [ ] Calibration chart appears below KPI cards when at least one metric has resolved data
- [ ] Chart absent (no error) when no resolved forecast data exists
- [ ] Bars green for ≥target, red for <target
- [ ] Reference lines visible at each target value

### Fail criteria
- `ImportError` on plotly in week_summary
- Chart renders with all-zero bars when data exists
- Section crashes with no resolved forecasts

---

## Fix 3 — ROE self-calculation via _calc_roe() (D-02 bench)

**File changed:** `indicators.py`

### What changed
`signal_score()` no longer reads `returnOnEquity` directly from yfinance info (unreliable — often None or 0). New `_calc_roe()` helper calculates ROE from first principles: `(netIncomeToCommon) / (bookValue × sharesOutstanding) × 100`. Falls back to yfinance's field if inputs are unavailable.

### Where to look
Page: Dashboard → any stock → KPI panel → ROE figure

### Before
ROE showed 0.0% or N/A for many stocks where yfinance's `returnOnEquity` was blank.

### After
ROE shows a calculated value for stocks where netIncomeToCommon, bookValue, and sharesOutstanding are available. N/A guard still applies (0.0 treated as data gap per financial-safety rule).

### Pass criteria
- [ ] ROE non-zero for at least one large-cap stock (e.g. TCS.NS, RELIANCE.NS)
- [ ] ROE shows N/A (not 0.0%) for stocks with missing income/book data
- [ ] No AttributeError or KeyError in terminal from `_calc_roe`

### Fail criteria
- All stocks show N/A (regression — calc_roe not triggering)
- ROE shows raw 0.0% (null guard bypassed)

---

## Proxy infrastructure (PROXY-01–07) — No UI surface, tooling-only

These items affect the litellm proxy CLI tools in `litellm-proxy/`. No Streamlit UI changes. Verify at the terminal level only.

| Item | File | Check |
|---|---|---|
| PROXY-01 | `classifier_keywords.py` + both importers | `python3 litellm-proxy/approval_hook.py` imports without error |
| PROXY-02 | `approval_hook.py` | `async_success_callback` method exists |
| PROXY-03 | `review_gate.py` | `python3 litellm-proxy/review_gate.py --help` exits 0 |
| PROXY-04 | `sprint_planner.py` | Depends column shown if present in board |
| PROXY-05 | `sprint_planner.py` | Staleness warning shown for old in-progress items |
| PROXY-06 | `validate_models.py` | `python3 litellm-proxy/validate_models.py --help` shows `--spend` flag |
| PROXY-07 | `approval_hook.py` | Tool-use guard block present in `async_pre_call_hook` |

---

## Cross-page spot check — v5.36

| Reading | Location A | Location B | Match? |
|---|---|---|---|
| ROE for RELIANCE.NS | Dashboard KPI panel | — | Non-zero % or N/A |
| Stability badge for any group | Portfolio Allocator tab | — | STABLE/MODERATE/UNSTABLE |
| Calibration chart | Forecast Accuracy tab | — | Visible if resolved forecasts |

## What I need back from QA

**Must-have:**
- [ ] Fix 1 pass/fail: Stability score renders in Portfolio Allocator
- [ ] Fix 2 pass/fail: Calibration chart renders in Forecast Accuracy (or absent cleanly)
- [ ] Fix 3 pass/fail: ROE non-zero for at least one stock

**Good-to-have:**
- [ ] PROXY-06 `--spend` flag visible in `--help` output
- [ ] `review_gate.py --help` exits 0

---

# QA Brief — v5.37 SEBI Compliance + Governance Sprint

**Sprint:** v5.37 | **Date:** 2026-04-14 | **Session:** session_025/026

## Summary of changes

9 code items + 2 governance items across 8 files:

| # | Fix | File | Expected visible change |
|---|---|---|---|
| 1 | df01/OPEN-027 | pages/home.py | `_render_global_signals()` now shows SEBI disclaimer caption below signal cards; `period="3mo"` in 3 batch calls (no visible diff — prevents DF-01 silent empty signals) |
| 2 | OPEN-029 | pages/dashboard.py | Compact SEBI caption appears below ticker header on all 4 tabs (Charts/Forecast/Compare/Insights) |
| 3 | OPEN-022 | pages/week_summary.py | SEBI caption in Signal Summary tab above BUY/WATCH/AVOID count cards; SEBI caption in Portfolio Allocator below "📊 Optimal Allocation" title |
| 4 | OPEN-028 | pages/global_intelligence.py | SEBI caption after "Related Stocks to Watch" title; each watchlist stock now shows BUY/WATCH/AVOID verdict badge below name |
| 5 | df-03 | pages/week_summary.py | Caption below Portfolio Allocator allocation table: "Based on 6-month daily price history · Data as of DD Mon YYYY" |
| 6 | df-08 | pages/home.py | Caption below Top Movers cards: "1-day % change (previous close → latest close) · Refreshes every 60 s" |
| 7 | OPEN-023 | litellm-proxy/config.yaml | hf-code model name `groq/openai/gpt-oss-20b` → `groq/qwen-qwq-32b` (runtime fix, no UI change) |
| 8 | OPEN-025 | portfolio.py + week_summary.py | UI text now reads "σ >= 15%" for UNSTABLE threshold (was "> 15%") |
| 9 | df-02 | market_data.py | `DEFAULT_NEWS_FEEDS` constant added (ET Markets + Reuters + BBC Business + ToI); no UI change |
| 10 | df-05 | pages/global_intelligence.py | Caption after all topic cards: "Geopolitical & macro analysis · Algorithmically curated from static research · Last reviewed: Apr 2026" |
| 11 | OPEN-026 | CLAUDE.md + regression.py | EP table + R8 additions (no UI change) |

## Before / After screenshots required

**Fix 1 — SEBI in Global Signals (home.py):**
- Before: Signal cards (BUY/WATCH/AVOID counts for each market group) with short "For informational purposes only" caption only
- After: Full SEBI disclaimer text visible below signal cards on Home page

**Fix 2 — SEBI in Dashboard header (dashboard.py):**
- Before: Ticker name / verdict badge / price tile with NO disclaimer on Charts, Forecast, Compare tabs
- After: Compact SEBI caption line directly below header verdict badge on all tabs

**Fix 3 — SEBI in Portfolio Allocator (week_summary.py):**
- Before: "📊 Optimal Allocation" title → immediately allocation rows
- After: "📊 Optimal Allocation" → SEBI caption → data-as-of caption → allocation rows

**Fix 4 — Verdict badges in GI watchlist (global_intelligence.py):**
- Before: Related stock tiles show price + 1-day change only
- After: Each stock tile shows an additional BUY/WATCH/AVOID badge (coloured pill)

**Fix 5 — Data-as-of in Portfolio Allocator:**
- Expected text: "Based on 6-month daily price history · Data as of 14 Apr 2026" (or current date)

**Fix 6 — Top Movers caption:**
- Expected text below the 6 mover cards: "1-day % change (previous close → latest close) · Refreshes every 60 s"

**Fix 10 — GI macro last-reviewed:**
- Expected text after all topic accordion cards: "Geopolitical & macro analysis · Algorithmically curated from static research · Last reviewed: Apr 2026"

## Cross-page spot check — v5.37

| Reading | Location | Expected |
|---|---|---|
| SEBI disclaimer | Dashboard (Charts tab) | Visible below verdict badge |
| SEBI disclaimer | Portfolio Allocator | Visible below "Optimal Allocation" title |
| SEBI disclaimer | Signal Summary tab | Visible above BUY/WATCH/AVOID count cards |
| Verdict badge | GI → any topic watchlist | BUY/WATCH/AVOID pill next to each stock |
| Data-as-of | Portfolio Allocator | "Data as of DD Mon YYYY" caption present |
| Top Movers label | Home page | "previous close → latest close" caption present |
| UNSTABLE threshold | Portfolio Allocator expander | "σ >= 15%" (not "> 15%") |

## Playwright Test Cases

**PLAYWRIGHT-01:** Navigate to Home page → assert global signals section shows SEBI caption text · Assert at least one RSI value ≠ 50 in signal badges · Edge case: fragment runs every 60s — verify caption persists on re-render

**PLAYWRIGHT-02:** Navigate to any stock dashboard → assert SEBI caption text visible in header area on Charts tab · Switch to Forecast tab → assert caption still visible · Edge case: header renders for all 4 tabs — verify not just Insights tab

**PLAYWRIGHT-03:** Navigate to Week Summary → Signal Summary tab → assert SEBI caption present · Navigate to Portfolio Allocator tab → run optimisation → assert SEBI caption present in allocation table area

**PLAYWRIGHT-04:** Navigate to Global Intelligence → Related Stocks section → assert SEBI caption present · Assert at least one ticker shows BUY/WATCH/AVOID verdict badge · Edge case: cold cache — graceful fallback if verdict unavailable

**PLAYWRIGHT-05:** Navigate to Week Summary → Portfolio Allocator → run optimisation → assert data freshness label visible near metric cards

**PLAYWRIGHT-06:** Navigate to Home page → Top Movers section → assert temporal scope caption visible

## What I need back from QA

**Must-have:**
- [ ] Fix 1 pass/fail: SEBI caption visible on Home page below global signals section
- [ ] Fix 2 pass/fail: SEBI caption visible on Dashboard header (Charts tab, before Insights)
- [ ] Fix 3 pass/fail: SEBI caption visible in Portfolio Allocator below "Optimal Allocation" title
- [ ] Fix 4 pass/fail: At least one verdict badge visible in a GI topic watchlist
- [ ] Fix 5 pass/fail: Data-as-of caption shows a real date (not "unknown")
- [ ] Fix 6 pass/fail: Top Movers caption visible below mover cards

**Good-to-have:**
- [ ] Fix 10 pass/fail: Last-reviewed caption visible at bottom of GI topic section

---

# QA Brief — v5.37.1 Hotfix: Global Signals "Computing..." Fix

**Sprint:** v5.37.1 | **Date:** 2026-04-14 | **Session:** session_026 (post-sprint QA)

## Summary

Single file change in `market_data.py`. No new UI elements — this fix unblocks existing UI.

| Fix | File | Expected visible change |
|---|---|---|
| Period-aware `_ticker_cache` | market_data.py | All 10 global signal cards now resolve (no permanent "Computing..." state) |

## Before / After

**Before:** On cold start, top 5–7 signal cards (NIFTY 50, SENSEX, BANK NIFTY, S&P 500, NASDAQ) show "Computing..." permanently. Bottom 3–4 (HANG SENG, GOLD, CRUDE WTI, USD/INR) resolve correctly.

**After:** All 10 cards resolve once the 3mo price data is fetched (~15–20 seconds after ticker bar warmup). No card should stay in "Computing..." beyond the first refresh cycle.

## Verification steps

1. Restart the app (clears module-level cache)
2. Navigate to Home page
3. Wait for ticker bar to populate (warmup phase)
4. Observe Global Trend Signals section — all 10 cards should transition from "Computing..." to a signal within one 60s fragment cycle
5. No card should show "Computing..." after the second fragment render

## What I need back from QA

- [ ] All 10 global signal cards show BUY/WATCH/AVOID (or ↑ RISING / ↓ FALLING for FX/commodities) within 90 seconds of page load
- [ ] No regression in Top Movers or News Feed sections (same page, different fragment)
