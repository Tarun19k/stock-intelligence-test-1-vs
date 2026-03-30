# GSI Dashboard — Audit Trail
# ════════════════════════════════════════════════════════════════════════════
#
# GOVERNANCE RULES — READ BEFORE TOUCHING THIS FILE
#
# 1. APPEND ONLY. No record in this file may ever be edited or deleted.
#    Mistakes in a record are corrected by adding a CORRECTION record that
#    references the original record ID. The original stays intact.
#
# 2. EVERY FINDING gets a record, regardless of severity. A finding that is
#    immediately disregarded still gets a FINDING record followed by a
#    DISREGARD record explaining why.
#
# 3. EVERY STATUS CHANGE gets a RESOLUTION record. "Fixed", "Won't Fix",
#    "Deferred", and "Disregarded" are all resolution types — each creates
#    a new record with a date, version, and reason. The finding record
#    itself is never touched.
#
# 4. REGRESSIONS get a REOPEN record. If a previously fixed finding
#    resurfaces, do not edit the original RESOLUTION record. Add a REOPEN
#    record referencing the original finding ID.
#
# 5. THE CURRENT STATE VIEW (Section 4) is a derived summary — regenerated
#    each version by reading the log. It is NOT the source of truth.
#    The records in Sections 1–3 are the source of truth.
#
# 6. RECORD IDs are permanent and unique. Once assigned, an ID is never
#    reused, even if the original finding is deleted (which it cannot be).
#
# 7. DATES are in YYYY-MM-DD format. Version numbers follow the project's
#    version.py CURRENT_VERSION at the time of recording.
#
# ════════════════════════════════════════════════════════════════════════════

---

## Section 1 — Finding Records (Immutable)

Each finding is recorded once. Never edited after creation.

### Format
```
FINDING | ID | Date | Version-tested | Source-report | Severity | Description
```

Severity: P0 (regulatory/safety) | P1 (high) | P2 (medium) | P3 (low) | P4 (cosmetic)

---

<!-- BATCH: v5.28 audit session, all recorded 2026-03-28 -->

FINDING | H-01 | 2026-03-28 | v5.28 | Homepage Audit | P1 |
  Nifty 50 5-day % shows different values on Home page vs Dashboard in the same
  session. Observed: -9.4% (Home Global Snapshot) vs -1.3% (Dashboard KPI panel).
  Root cause: two separate inline calculations using different window logic.

FINDING | H-02 | 2026-03-28 | v5.28 | Homepage Audit | P2 |
  Global Trend Signals section shows dashes on first load with no explanation.
  The warmth guard correctly defers loading but does not communicate to the user
  that data is loading — looks like an error or empty state.

FINDING | H-03 | 2026-03-28 | v5.28 | Homepage Audit | P1 |
  Market status cards wrap mid-word at 1280px standard viewport.
  Observed: "COMM ODI TIES" for Commodities, "ET Fs" for ETFs.
  Label strings too long for card width at standard desktop resolution.

FINDING | D-01 | 2026-03-28 | v5.28 | Dashboard Audit | P1 |
  Dashboard header shows raw Momentum Score (59/100) alongside WATCH verdict.
  Score of 59 is in "BUY territory" by the scale but verdict is WATCH.
  No explanation of why score and verdict diverge. P1 Glancer persona confused.

FINDING | D-02 | 2026-03-28 | v5.28 | Dashboard Audit | P0 |
  ROE shows 0.0% for RELIANCE.NS. Actual ROE is approximately 10%.
  Root cause: yfinance returns null for Indian stocks; safe_float(None) returns
  0.0 which is displayed as "0.0%" — a false data point, not a data gap indicator.

FINDING | D-03 | 2026-03-28 | v5.28 | Dashboard Audit | P1 |
  Forecast P(gain) = 46% displayed identically to P(gain) = 79%.
  Both show as a bare percentage with no indication that 46% is near-neutral.
  Users may interpret 46% as a meaningful bearish signal when it indicates
  the model has no directional conviction.

FINDING | D-04 | 2026-03-28 | v5.28 | Dashboard Audit | P1 |
  Forecast accuracy tracker creates duplicate same-day entries when a stock
  is revisited within the same session. store_forecast() skips silently if
  today's date already exists for the key — the user sees the original
  (possibly stale) forecast, not the freshest run.

FINDING | D-05 | 2026-03-28 | v5.28 | Dashboard Audit | P2 |
  Week Summary page state persists when the user navigates to the Dashboard tab
  and back. No loading indicator is shown during the transition, making the app
  appear frozen for 1–2 seconds on cold navigation.

FINDING | D-06 | 2026-03-28 | v5.28 | Dashboard Audit | P1 |
  Week Summary section headers show "Weekly +1.36%" and "Daily -2.09%" in the
  same view with no temporal context labels. On a weekend, "This Week" header
  appears while showing the prior week's data.

FINDING | D-07 | 2026-03-28 | v5.28 | Dashboard Audit | P2 |
  Elder Triple Screen verdict labels use jargon: "BUY SETUP", "WAIT", "NOT YET".
  These are Elder's original terms but are opaque to the P1 Glancer and
  Complete Beginner personas. No plain-English equivalents provided.

FINDING | D-08 | 2026-03-28 | v5.28 | Dashboard Audit | P1 |
  All week_summary.py section headings hard-code "This Week" regardless of
  whether the data is from the current or prior week. Tested Saturday 2026-03-28:
  all headings showed "This Week" while displaying Mon–Fri prior week data.

FINDING | D-09 | 2026-03-28 | v5.28 | Dashboard Audit | P2 |
  Forecast correction factor is applied silently. When prior forecasts were
  consistently biased, the model applies a correction multiplier. The adjusted
  forecast is shown with no disclosure that a correction has been applied or
  what it was.

FINDING | G-01 | 2026-03-28 | v5.28 | GI Audit | P0 |
  WorldMonitor interactive map blocked by Content Security Policy (frame-ancestors).
  The embedded iframe shows as a blank white space. No fallback displayed.
  First-time users see an empty section with no explanation.

FINDING | G-02 | 2026-03-28 | v5.28 | GI Audit | P2 |
  Only 4 topic cards on the Global Intelligence page. Page claims to be a
  "Global Intelligence Centre" but 4 topics provides shallow coverage.
  Major topics missing: Middle East energy, India-China border, US-EU trade.

FINDING | G-03 | 2026-03-28 | v5.28 | GI Audit | P2 |
  Impact chain visualisation overflows at 1280px standard viewport width.
  Long chains (5+ nodes) require horizontal scrolling, which is not indicated
  to the user and fails entirely on mobile viewports.

FINDING | G-04 | 2026-03-28 | v5.28 | GI Audit | P1 |
  Same ticker shows different prices in the ticker bar vs GI watchlist badges
  within the same session. Observed: Nifty 50 at 22,820 (ticker bar) vs 23,306
  (GI watchlist). Root cause: GI uses cache_buster=cb (session-scoped) while
  ticker bar uses cache_buster=0 — different cache keys, different cached values.

FINDING | G-05 | 2026-03-28 | v5.28 | GI Audit | P1 |
  GI page subtitle reads "Real-time geopolitical & technology trends" while
  the WorldMonitor map is broken (G-01) and AI & Jobs RSS articles are from
  2022–2023 (F-03). The "Real-time" claim is false across multiple sections.

FINDING | EQA-14 | 2026-03-28 | v5.28 | Expert QA Report | P1 |
  Expert QA finding #14: Elder Triple Screen displays "BUY SETUP" while
  Weinstein Stage displays "WAIT" at equal visual weight with no arbitration
  label. User has no way to know which signal takes precedence.

FINDING | EQA-29 | 2026-03-28 | v5.28 | Expert QA Report | P0 |
  Expert QA finding #29: Zero investment disclaimers anywhere on the platform.
  No SEBI disclaimer on signal sections. Full regulatory liability exposure for
  a platform serving investment signals to retail users.

FINDING | EQA-32 | 2026-03-28 | v5.28 | Expert QA Report | P0 |
  Expert QA finding #32: AI-generated narrative sections (Watch Out For, What
  to Consider, What the Data Says) are not labeled as algorithmically generated.
  Indistinguishable from human analyst opinion to a non-technical user.

FINDING | EQA-33 | 2026-03-28 | v5.28 | Expert QA Report | P0 |
  Expert QA finding #33: Global Intelligence "What You Should Do Next" section
  contains named stock investment recommendations (NVDA, TSM, MSFT Azure) with
  no disclaimer, no signal context, and no connection to live market data.

FINDING | EQA-38 | 2026-03-28 | v5.28 | Expert QA Report | P1 |
  Expert QA finding #38: GI page subtitle claims "Real-Time" while the
  WorldMonitor map is blocked (G-01) and the AI & Jobs section serves
  articles from 2022–2023 labeled "Live Headlines".

FINDING | EQA-41 | 2026-03-28 | v5.28 | Expert QA Report | P2 |
  Expert QA finding #41: Forecast accuracy tracker shows a percentage (e.g.
  65%) with no baseline or benchmark. User cannot assess if this is good or
  poor — random chance gives 50%, so 65% may be modest or excellent depending
  on market conditions.

FINDING | EQA-43 | 2026-03-28 | v5.28 | Expert QA Report | P3 |
  Expert QA finding #43: No data export anywhere in the platform. Quants,
  systematic traders, and financial advisors cannot extract signals, portfolio
  weights, or forecast data for use in external workflows.

FINDING | C-01 | 2026-03-28 | v5.28 | Data Dependency Report | P0 |
  AI narrative (Watch Out For) says "No major red flags at this time" while
  9 of 12 US sectors are negative and RSI is at 36 (approaching oversold).
  The narrative has no access to sector breadth data — it reads only the
  individual stock's indicators.

FINDING | C-02 | 2026-03-28 | v5.28 | Data Dependency Report | P1 |
  Macro data visible in ticker bar (Gold +3.92%, Crude WTI rising) is not
  accessible to the stock-level AI narrative. A simultaneous Gold and Crude
  surge is a risk-off signal but the narrative cannot reflect this.

FINDING | C-03 | 2026-03-28 | v5.28 | Data Dependency Report | P1 |
  RSI of 36 (bearish, approaching oversold) described as "neutral momentum
  zone" in the AI narrative text. The narrative does not read the same RSI
  value the KPI panel displays — it uses a different code path.

FINDING | C-04 | 2026-03-28 | v5.28 | Data Dependency Report | P1 |
  Elder Triple Screen and Weinstein Stage shown in conflict at equal visual
  weight with no resolution. Duplicate of EQA-14 from a different audit
  perspective — data pipeline root cause confirmed.

FINDING | C-05 | 2026-03-28 | v5.28 | Data Dependency Report | P2 |
  Momentum Score 58/100 displayed with no scale definition. Users do not
  know what constitutes a high or low score, how each indicator is weighted,
  or what the theoretical maximum represents.

FINDING | C-06 | 2026-03-28 | v5.28 | Data Dependency Report | P1 |
  MACD shown on the main chart uses daily bars. MACD in the KPI Signal Panel
  refreshes every 60 seconds during live sessions (intraday MACD). Neither
  is labeled with a timeframe — the user may assume they show the same thing.

FINDING | C-07 | 2026-03-28 | v5.28 | Data Dependency Report | P3 |
  Prices for European stocks are shown in their local currency (GBP, EUR)
  without a USD/INR conversion or disclosure. Mixed-currency comparisons
  in the Compare tab are misleading without normalisation.

FINDING | C-08 | 2026-03-28 | v5.28 | Data Dependency Report | P1 |
  Sector breadth is correctly computed (count of positive/negative sectors)
  but the result is never passed to the AI narrative engine. The narrative
  cannot reference macro-level trends even when they are directly relevant.

FINDING | C-09 | 2026-03-28 | v5.28 | Data Dependency Report | P1 |
  "Market LIVE" badge in the sidebar fires based on Streamlit app runtime,
  not on actual market open hours. Observed firing at 2AM Saturday when all
  markets globally are closed.

FINDING | F-01 | 2026-03-28 | v5.28 | 360° Bird's Eye View | P1 |
  All GI topic cards collapsed on first load. Page appears empty to the
  Complete Beginner persona — they see only the collapsed card headers and
  navigate away without discovering the content.

FINDING | F-02 | 2026-03-28 | v5.28 | 360° Bird's Eye View | P1 |
  India Impact text in GI topic cards is a static string: "every $10/bbl
  rise in Crude adds ₹1.2L cr to India's import bill." This is a fixed
  formula, not computed from the live Crude WTI price visible in the ticker.

FINDING | F-03 | 2026-03-28 | v5.28 | 360° Bird's Eye View | P0 |
  TechCrunch RSS feed in the AI & Jobs GI topic is serving articles from
  2022–2023, labeled "📰 Live Headlines". The feed is stale — no recency
  check was applied before deploying.

FINDING | F-04 | 2026-03-28 | v5.28 | 360° Bird's Eye View | P1 |
  GI watchlist badges show India NSE stocks regardless of which market is
  selected in the sidebar. Selecting "USA" in the sidebar does not change
  the watchlist content.

FINDING | F-05 | 2026-03-28 | v5.28 | 360° Bird's Eye View | P1 |
  Duplicate of F-04 confirmed from a separate audit path — GI watchlist
  is hardcoded and market-selector-independent. Recorded separately to
  preserve both audit paths as evidence.

FINDING | F-06 | 2026-03-28 | v5.28 | 360° Bird's Eye View | P0 |
  "What You Should Do Next" section in GI page contains career/investment
  action cards (invest in NVDA, TSM, MSFT) with no disclaimer, no live
  signal connection, and no regulatory disclosure.

FINDING | F-07 | 2026-03-28 | v5.28 | 360° Bird's Eye View | P3 |
  Forecast Accuracy Report is accessible from Week Summary but the Forecast
  tab on the Dashboard has no link or reference to it. Users who generate
  forecasts are unlikely to discover the accuracy tracking feature.

FINDING | F-08 | 2026-03-28 | v5.28 | 360° Bird's Eye View | P3 |
  Portfolio Allocator has no export mechanism. Users cannot download the
  recommended weights, efficient frontier data, or CVaR outputs for use
  in actual portfolio management tools.

FINDING | F-09 | 2026-03-28 | v5.28 | 360° Bird's Eye View | P2 |
  Compare tab normalises all stocks to 100 at the period start date.
  The normalisation methodology is not disclosed. A user unfamiliar with
  normalised return charts may misread the scale as absolute prices.

FINDING | F-10 | 2026-03-28 | v5.28 | 360° Bird's Eye View | P2 |
  Impact chain visualisation overflows at 1280px. Duplicate of G-03
  confirmed from a different audit perspective — recorded separately.

FINDING | F-11 | 2026-03-28 | v5.28 | 360° Bird's Eye View | P0 |
  Raw Momentum Score (58/100) displayed in the dashboard header before the
  verdict badge. P1 Glancer persona sees the score first and anchors on it
  before reading the verdict — creates misleading first impression.

FINDING | F-12 | 2026-03-28 | v5.28 | 360° Bird's Eye View | P0 |
  Duplicate of EQA-33 — named investment recommendations in GI page without
  disclaimer. Recorded separately as it was discovered via a different
  audit path (content review vs regulatory review).

FINDING | F-13 | 2026-03-28 | v5.28 | 360° Bird's Eye View | P1 |
  Duplicate of F-02 confirmed — India Impact formula is static.
  Recorded separately as this was identified independently during the
  content accuracy section of the 360° review.

FINDING | F-14 | 2026-03-28 | v5.28 | 360° Bird's Eye View | P1 |
  West Asia geopolitical section makes specific quantitative claims (e.g.
  oil price thresholds, percentage impacts) with no source attribution
  and no date stamp. Claims may be outdated or unverifiable.

FINDING | F-15 | 2026-03-28 | v5.28 | 360° Bird's Eye View | P1 |
  Duplicate of F-01 confirmed — GI topic cards collapsed on first load.
  Recorded separately as it was identified in the UX section of the 360°
  review, distinct from the structural finding in the GI audit.

---

## Section 2 — Resolution Records (Immutable)

Each resolution is a new record. Finding records are never edited.
Status types: FIXED | DEFERRED | WONT_FIX | DISREGARDED | PARTIAL

### Format
```
RESOLUTION | Finding-ID | Date | Version | Status | Resolved-by | Reason
```

---

<!-- BATCH: v5.31 fixes, all recorded 2026-03-28 -->

RESOLUTION | H-03  | 2026-03-28 | v5.31 | FIXED |
  Market status card labels shortened to IND / USA / EUR / CHN / COMM / ETF.
  Mid-word wrapping eliminated at 1280px. QA verified 2026-03-28.

RESOLUTION | D-01  | 2026-03-28 | v5.31 | FIXED |
  Option B implemented: raw Momentum Score removed from dashboard header.
  Verdict badge + plain-English reason only. Score remains in KPI panel.
  QA verified 2026-03-28 (Fix 1 — initial tester confusion resolved on re-test).

RESOLUTION | D-02  | 2026-03-28 | v5.31 | FIXED |
  ROE null guard added: `roe_str = f'{val:.1f}%' if val != 0 else "N/A"`.
  safe_float(None)=0.0 no longer displayed as "0.0%". QA verified 2026-03-28.

RESOLUTION | EQA-29 | 2026-03-28 | v5.31 | FIXED |
  SEBI disclaimer added above the 3 insight columns in _tab_insights().
  Text: "For informational purposes only. Not financial advice. Consult a
  SEBI-registered investment advisor before making investment decisions."
  QA verified 2026-03-28.

RESOLUTION | EQA-32 | 2026-03-28 | v5.31 | FIXED |
  Algorithmic disclosure banner added to _tab_insights() above narrative columns.
  Text: "Algorithmic analysis — generated from quantitative signals, not a human
  analyst opinion." QA verified 2026-03-28.

RESOLUTION | EQA-33 | 2026-03-28 | v5.31 | FIXED |
  _render_next_steps_ai() removed from render_global_intelligence().
  Function definition retained for possible future redesign with live signals.
  DO NOT UNDO rule added to CLAUDE.md (rule 14). QA verified 2026-03-28.

RESOLUTION | EQA-38 | 2026-03-28 | v5.31 | PARTIAL |
  Partial fix only. Live Headlines date gate added: label shows "Live" only when
  most recent article < 48h old. WorldMonitor map (G-01) remains replaced with
  external link. Page subtitle "Real-Time" claim not yet corrected.
  Full resolution requires subtitle update (pending).

RESOLUTION | G-01  | 2026-03-28 | v5.31 | WONT_FIX |
  WorldMonitor CSP blocks all *.streamlit.app domains at their server level.
  Cannot be resolved without WorldMonitor changing their policy.
  Replaced with external link button + caption explaining CSP limitation.
  Acceptable UX — user can open the map in a new tab. Not re-testable.

RESOLUTION | C-01  | 2026-03-28 | v5.31 | PARTIAL |
  Partial fix only. Watch Out For fallback now checks RSI and MACD before
  generating text — "No major red flags" no longer fires unconditionally.
  Root cause (sector breadth not wired to narrative) remains unresolved.
  Full resolution requires OPEN-018 (Claude API integration — future phase).

RESOLUTION | F-01  | 2026-03-28 | v5.31 | FIXED |
  GI topic cards set to expanded=True by default. Page no longer appears
  empty on first load. QA verified 2026-03-28 (Fix 6 brief).

RESOLUTION | F-03  | 2026-03-28 | v5.31 | FIXED |
  TechCrunch RSS feeds removed from AI & Jobs topic config. Replaced with
  active, verified feeds. Live Headlines date gate added (48h freshness check).
  QA verified 2026-03-28 (Fix 7 brief).

RESOLUTION | F-06  | 2026-03-28 | v5.31 | FIXED |
  "What You Should Do Next" section removed from render_global_intelligence().
  DO NOT UNDO rule 14 added to CLAUDE.md. QA verified 2026-03-28 (Fix 8 brief).

RESOLUTION | F-11  | 2026-03-28 | v5.31 | FIXED |
  Duplicate of D-01 — resolved by same change (Option B, score removed from header).
  QA verified 2026-03-28. Finding retained as separate record per audit trail rules.

RESOLUTION | F-12  | 2026-03-28 | v5.31 | FIXED |
  Duplicate of EQA-33 — resolved by same change (What You Should Do Next removed).
  QA verified 2026-03-28. Finding retained as separate record per audit trail rules.

RESOLUTION | F-15  | 2026-03-28 | v5.31 | FIXED |
  Duplicate of F-01 — resolved by same change (expanded=True on topic cards).
  QA verified 2026-03-28. Finding retained as separate record per audit trail rules.

<!-- BATCH: v5.32 fixes, all recorded 2026-03-29 -->

RESOLUTION | H-01  | 2026-03-29 | v5.32 | FIXED |
  calc_5d_change() shared utility added to utils.py. home.py inline 5-day
  calculation replaced with the shared function. Both Home and Dashboard now
  use the same window logic. QA spot check required: Nifty 5-day must match
  across pages within ±0.1%.

RESOLUTION | D-03  | 2026-03-29 | v5.32 | FIXED |
  P(gain) 45–55% now displays as "Neutral (45–55%)" in the forecast table.
  Neutral-zone entries excluded from directional accuracy scoring in the
  weekly calibration report.

RESOLUTION | D-04  | 2026-03-29 | v5.32 | FIXED |
  store_forecast() now replaces same-day entries (filters out matching
  made_on == today) instead of silently returning early. Revisiting a stock
  in the same session now shows the freshest forecast.

RESOLUTION | D-06  | 2026-03-29 | v5.32 | FIXED |
  Duplicate of D-08 — resolved by same change (dynamic section titles).
  Finding retained as separate record per audit trail rules.

RESOLUTION | D-08  | 2026-03-29 | v5.32 | FIXED |
  All week_summary.py section headings now call _get_week_range() and display
  "This Week" or "Last Week" with the actual date range. Weekend testing should
  show "Last Week (Week of [date range])".

RESOLUTION | EQA-14 | 2026-03-29 | v5.32 | FIXED |
  Dashboard header override label now reads "Stage N overrides momentum —
  see Insights" where N is the actual Weinstein Stage. verdict["weinstein_stage"]
  is read and interpolated into the label string.

RESOLUTION | C-04  | 2026-03-29 | v5.32 | FIXED |
  Duplicate of EQA-14 — resolved by same change. Finding retained as separate
  record per audit trail rules.

RESOLUTION | C-06  | 2026-03-29 | v5.32 | FIXED |
  MACD chart subplots now titled "MACD (Daily)". KPI panel card now labeled
  "MACD Histogram (Daily)". Timeframe ambiguity eliminated.

RESOLUTION | C-09  | 2026-03-29 | v5.32 | FIXED |
  Market LIVE badge now reads "{country} Market LIVE" using the market_open
  boolean from _is_market_open() — not Streamlit runtime. Badge shows the
  specific market name (India, USA, etc.).

RESOLUTION | F-04  | 2026-03-29 | v5.32 | FIXED |
  _market_of() helper added to global_intelligence.py. _render_watchlist_badges()
  now accepts selected_market param and filters tickers by market suffix.
  render_global_intelligence() accepts selected_market=country from app.py.

RESOLUTION | F-05  | 2026-03-29 | v5.32 | FIXED |
  Duplicate of F-04 — resolved by same change. Finding retained as separate
  record per audit trail rules.

RESOLUTION | G-04  | 2026-03-29 | v5.32 | FIXED |
  GI watchlist badges now use cache_buster=0, matching the ticker bar's cache
  key. Prices guaranteed to be from the same cache entry within a session.

RESOLUTION | F-13  | 2026-03-29 | v5.32 | DEFERRED |
  Duplicate of F-02 — India Impact static formula. Deferred alongside F-02
  to OPEN-018 (Claude API integration, future phase). Both findings remain open.

<!-- Disregard records -->

RESOLUTION | F-09  | 2026-03-28 | v5.28 | DISREGARDED |
  Normalisation disclosure for Compare tab (all stocks indexed to 100 at period
  start). Disregarded at triage: normalised return charts are industry standard
  and the label "Normalised to 100" is common knowledge among the target personas
  (Active Trader, Fundamental Analyst). Would add UI noise for marginal gain.
  Recorded here per audit trail policy. May be revisited if beginner persona
  feedback indicates confusion.

RESOLUTION | C-07  | 2026-03-28 | v5.28 | DISREGARDED |
  Mixed-currency display without conversion. Disregarded at triage: European
  stocks are a small fraction of the ticker universe (17 of 559) and the
  Compare tab allows user-controlled selection. Adding currency conversion
  would require a FX rate API or hardcoded rates (stale risk). Acceptable
  limitation — disclosed in SECURITY.md known limitations section.
  Recorded here per audit trail policy.

RESOLUTION | EQA-43 | 2026-03-28 | v5.28 | DEFERRED |
  Data export feature. Deferred to v6 roadmap. Platform is a signal dashboard,
  not a data API. Export functionality is a product scope change, not a bug fix.
  No session-level tracking ID assigned — addressed in v6 planning phase.

RESOLUTION | F-07  | 2026-03-28 | v5.28 | DEFERRED |
  Link from Forecast tab to Accuracy Report. Low priority — users who generate
  forecasts are likely to explore the Week Summary page and discover the report.
  Deferred to v5.33 consideration backlog.

RESOLUTION | F-08  | 2026-03-28 | v5.28 | DEFERRED |
  Portfolio Allocator export. Deferred to v6 roadmap alongside EQA-43.
  Requires file generation infrastructure not currently in the platform.

---

## Section 3 — Reopen Records (Immutable)

If a resolved finding regresses, a REOPEN record is added here.
The original RESOLUTION record is never edited.

### Format
```
REOPEN | Finding-ID | Date | Version | Evidence | Reopened-by
```

---

<!-- No regressions detected as of v5.32 — 2026-03-29 -->

---

## Section 4 — Current State View (Derived — not source of truth)

**Generated:** 2026-03-29 | **Based on version:** v5.32
**Regenerate this section after every sprint by reading Sections 1–3.**

| Finding | Severity | Current status | Version resolved |
|---|---|---|---|
| H-01 | P1 | ✅ Fixed | v5.32 |
| H-02 | P2 | 🔶 Open | — |
| H-03 | P1 | ✅ Fixed | v5.31 |
| D-01 | P1 | ✅ Fixed | v5.31 |
| D-02 | P0 | ✅ Fixed | v5.31 |
| D-03 | P1 | ✅ Fixed | v5.32 |
| D-04 | P1 | ✅ Fixed | v5.32 |
| D-05 | P2 | 🔶 Open | — |
| D-06 | P1 | ✅ Fixed | v5.32 |
| D-07 | P2 | 🔶 Open | — |
| D-08 | P1 | ✅ Fixed | v5.32 |
| D-09 | P2 | 🔶 Open | — |
| G-01 | P0 | ⚠️ Won't fix | v5.31 (replaced) |
| G-02 | P2 | 🔶 Open | — |
| G-03 | P2 | 🔶 Open | — |
| G-04 | P1 | ✅ Fixed | v5.32 |
| G-05 | P1 | 🟡 Partial | v5.31 (subtitle pending) |
| EQA-14 | P1 | ✅ Fixed | v5.32 |
| EQA-29 | P0 | ✅ Fixed | v5.31 |
| EQA-32 | P0 | ✅ Fixed | v5.31 |
| EQA-33 | P0 | ✅ Fixed | v5.31 |
| EQA-38 | P1 | 🟡 Partial | v5.31 (subtitle pending) |
| EQA-41 | P2 | 🔶 Open | — |
| EQA-43 | P3 | ⏳ Deferred | v6 roadmap |
| C-01 | P0 | 🟡 Partial | v5.31 (breadth pending) |
| C-02 | P1 | 🔶 Open | OPEN-018 |
| C-03 | P1 | 🔶 Open | OPEN-018 |
| C-04 | P1 | ✅ Fixed | v5.32 |
| C-05 | P2 | 🔶 Open | — |
| C-06 | P1 | ✅ Fixed | v5.32 |
| C-07 | P3 | 🚫 Disregarded | 2026-03-28 |
| C-08 | P1 | 🔶 Open | OPEN-018 |
| C-09 | P1 | ✅ Fixed | v5.32 |
| F-01 | P1 | ✅ Fixed | v5.31 |
| F-02 | P1 | 🔶 Open | OPEN-018 |
| F-03 | P0 | ✅ Fixed | v5.31 |
| F-04 | P1 | ✅ Fixed | v5.32 |
| F-05 | P1 | ✅ Fixed | v5.32 |
| F-06 | P0 | ✅ Fixed | v5.31 |
| F-07 | P3 | ⏳ Deferred | v5.33 backlog |
| F-08 | P3 | ⏳ Deferred | v6 roadmap |
| F-09 | P2 | 🚫 Disregarded | 2026-03-28 |
| F-10 | P2 | 🔶 Open | — |
| F-11 | P0 | ✅ Fixed | v5.31 |
| F-12 | P0 | ✅ Fixed | v5.31 |
| F-13 | P1 | ⏳ Deferred | OPEN-018 |
| F-14 | P1 | 🔶 Open | — |
| F-15 | P1 | ✅ Fixed | v5.31 |

**Status key:** ✅ Fixed | 🟡 Partial | 🔶 Open | ⚠️ Won't fix | 🚫 Disregarded | ⏳ Deferred

**Counts as of v5.32:**
- ✅ Fixed: 23 | 🟡 Partial: 3 | 🔶 Open: 14 | ⚠️ Won't fix: 1 | 🚫 Disregarded: 2 | ⏳ Deferred: 4
- Total findings: 48

---

## Section 5 — Audit Trail Governance Log

Records of decisions about this file itself — also append-only.

GOVERNANCE | 2026-03-29 | v5.32 |
  GSI_AUDIT_TRAIL.md created. Supersedes the mutable Status column in
  GSI_QA_STANDARDS.md Section 13. All 48 findings from 6 audit reports
  recorded as FINDING records with timestamps. Resolution records created
  for all actioned items. Disregard records created for two findings
  (F-09, C-07) that were triage-rejected. This creation is itself an
  auditable event.

GOVERNANCE | 2026-03-29 | v5.32 |
  GSI_QA_STANDARDS.md Section 13 superseded. That section's content is
  preserved in the file as a historical record of the pre-audit-trail
  format. It will not be edited further. All future finding tracking
  moves to this file.
