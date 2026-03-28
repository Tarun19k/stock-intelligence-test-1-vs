# GSI Dashboard — Governance Policy Framework
# Version: 1.0 | Established: 2026-03-28
# Source: QA audit sessions (v5.28 → v5.31), 6 independent audit reports
# Owner: Tarun | Enforced by: regression.py R25 (planned v5.33)
#
# These policies govern ALL future development on the GSI Dashboard.
# Any feature, fix, or refactor that violates a policy must be explicitly
# justified and approved before shipping. No exceptions.

---

## Policy 1 — Data & Logic Integrity

**Principle:** Every dynamic value displayed must trace to a live data source. No hard-coded market values.

### Rules
- All prices, percentages, and financial metrics must be retrieved via API or calculated from API data. Never hard-coded in templates or config strings.
- The India Impact formula ("every $10/bbl rise adds ₹1.2L cr to import bill") must be computed dynamically from the live Crude WTI price, not stored as a static string.
- Manual refresh (🔄 Refresh data button) must invalidate ALL cache layers simultaneously — `get_price_data.clear()`, `get_ticker_info.clear()`, and `_ticker_cache` — not just increment `cb`.
- Visualization logic (Plotly, chart rendering) must be decoupled from data processing. Pages receive pre-computed data from market_data.py; they never call yfinance directly.
- Static text that references specific market values (e.g. "20–30% headcount reduction risk") must carry a source citation and date stamp, or be removed.

### Audit findings that triggered this policy
- C-02: Gold +3.92% visible in ticker bar while stock-level AI says "no macro risk" — data isolation
- F-13: India Impact text is static formula, not computed from live Crude price
- F-14: West Asia summary text has no source attribution
- Data Dependency Report root cause #1: Siloed data pipelines with zero cross-referencing

---

## Policy 2 — Architectural Policies

**Principle:** Strict module boundaries. No page imports data, no data layer imports UI.

### Rules
- Pages (`dashboard.py`, `home.py`, `week_summary.py`, `global_intelligence.py`) must NEVER call yfinance directly. All data flows through `market_data.py`.
- `market_data.py` must NEVER import from any page file. No circular dependencies.
- `indicators.py`, `forecast.py`, `portfolio.py` must NEVER contain Streamlit calls. Pure computation only.
- All external embeds (iframes, maps, third-party widgets) must be evaluated for CSP compliance before implementation. Any embed that fails CSP must be replaced with a link button — not silently broken.
- Impact chains must be designed for 2nd and 3rd order expansion. Each topic card in Global Intelligence follows: Trigger → Regional Effect → Market Effect → India Impact → Affected Sectors → Related Stocks. New topics must follow this exact structure.
- `DataManager` singleton must always be accessed via `get_datamanager()`. Never instantiated directly. Pages must NOT call `DataManager.fetch()` until M4.

### Audit findings that triggered this policy
- G-01: WorldMonitor CSP block — iframe embed shipped without CSP validation
- G-01 root cause: External dependency shipped without fallback plan
- Data Dependency Report root cause #1: Four separate pipelines generating outputs independently

---

## Policy 3 — UX & Performance Standards

**Principle:** Every persona can use the app. Content never breaks layout. Performance never degrades cold start.

### Rules
- All KPI card labels must fit on one line at 1280px viewport with 6 cards per row. Test before shipping. Use abbreviated labels (IND not India) with full name in `title=` tooltip when needed.
- No section on any page may appear empty on first load. Sections that require data must show a loading state or skeleton. Sections that expand must default to `expanded=True` if they are the primary content of the page.
- Streamlit bundle must remain under 2MB. No new heavy dependencies without justification.
- All charts must be responsive. Use `config={"responsive": True}` on all `st.plotly_chart` calls. Never use `width='stretch'`.
- 4:5 and 16:9 aspect ratios must render correctly (mobile share and desktop).
- Impact chain visualisations must not overflow at 1280px standard viewport. Use horizontal scroll only as a last resort, and only for chains with >5 nodes.

### Audit findings that triggered this policy
- H-03: "COMM ODI TIES" mid-word wrap on market status cards (fixed v5.31)
- F-15: GI page appeared empty on first load — all sections collapsed (fixed v5.31)
- F-10: Impact chain overflows at standard 1280px viewport

---

## Policy 4 — Regulatory & Compliance ⚠️ HIGHEST PRIORITY

**Principle:** The app operates in a regulated financial environment. Every signal section must carry appropriate disclaimers. Algorithmic outputs must be labeled. No unnamed investment recommendations.

### Rules
- **SEBI disclaimer required** on every tab or section that displays BUY/WATCH/AVOID signals, action guidance, or stock-specific recommendations. Minimum text: *"For informational purposes only. Not financial advice. Consult a SEBI-registered investment advisor before making investment decisions. Past performance is not indicative of future results."*
- **Algorithmic labeling required** on every AI-generated narrative section. Minimum text: *"This analysis is algorithmically generated from quantitative signals. Not a human analyst opinion."* Required by SEBI proposed AI guidelines and EU AI Act.
- **No unnamed investment recommendations.** The phrase "invest in NVDA, TSM, MSFT" or equivalent must never appear without (a) a disclaimer, (b) context about why the stock is mentioned, and (c) the stock's current signal from the app's own analysis.
- Named securities mentioned in contextual sections (watchlists, impact chains) must display their current BUY/WATCH/AVOID verdict alongside the mention. A stock cannot be named without its signal status.
- The "Market LIVE" badge must be gated on actual market open hours (`market_open` boolean computed from `MARKET_SESSIONS`), not on Streamlit app runtime. Showing LIVE when all markets are closed is a false claim.
- The "What You Should Do Next" pattern — generic career or investment action cards disconnected from live market data — is permanently prohibited. All action guidance must reference live signals.

### Audit findings that triggered this policy
- Expert QA #29: Zero investment disclaimers anywhere on the platform (P0 Critical)
- Expert QA #32: Algorithmic narrative not labeled as AI output (P0 Critical)
- GI audit F-12: "Invest in NVDA, TSM, MSFT Azure" with no disclaimer (fixed v5.31)
- GI audit F-11: Page subtitle claims "Real-Time" while serving 3-year-old articles
- Data Dependency C-09: "Market LIVE" badge active at 2AM Saturday (all markets closed)

---

## Policy 5 — Data Coherence

**Principle:** The same metric shown on two pages must derive from the same calculation function. The AI narrative must consume the same data the technical panel displays.

### Rules
- Any percentage figure shown on multiple pages (5-day return, daily change, weekly performance) must derive from a single shared utility function. No page may implement its own version of a calculation that another page also performs.
- The canonical shared utility is `_calc_change_pct(df, days)` — to be implemented in `utils.py` and consumed by `home.py`, `dashboard.py`, and `global_intelligence.py` identically.
- The AI narrative engine (`_tab_insights` Watch Out For / What to Consider sections) must receive the same `sig` dict that the KPI panel displays. These cannot diverge.
- Group performance data (sector breadth — count of sectors positive/negative) must be passed as context to the AI narrative. The narrative must never generate a risk assessment without sector breadth input.
- Macro ticker data (Gold, Crude, USD/INR) visible in the ticker bar must be accessible to the stock-level AI narrative. When Gold and Crude surge simultaneously (risk-off signal), the narrative must reflect this.
- Before shipping any new metric or KPI, verify it is calculated identically to any existing display of the same concept.

### Audit findings that triggered this policy
- H-01: Nifty 5-day shows -9.4% on Home vs -1.3% on Dashboard — same session, same data (OPEN-008)
- G-04: Ticker bar Nifty 22,820 vs GI watchlist 23,306 — same session (OPEN-016)
- D-02: ROE 0.0% for Reliance Industries (actual ~10%) — yfinance returns null, displayed without fallback (fixed v5.31)
- Data Dependency C-01: "No major red flags" while 9/12 US sectors negative (partial fix v5.31)
- Data Dependency C-03: RSI 36 shows as "neutral momentum" in AI narrative (bearish by definition)
- Data Dependency report overall: Data Coherence 2/10, root cause "four siloed pipelines"

---

## Policy 6 — Signal Arbitration

**Principle:** When two analytical frameworks conflict, the resolution hierarchy must be formally defined, implemented in code, and visibly disclosed to the user.

### Rules
- **Weinstein Stage overrides Elder Triple Screen** in all conflict cases. This is the documented hierarchy in the existing codebase. It must be enforced in `compute_unified_verdict()` and displayed in the UI.
- When a Weinstein Stage veto fires (Stage 4 vetoes BUY; Stage 1/3 forces WATCH), the dashboard header must show `"⚠️ Stage override applied"` as the alignment label — not the generic "Momentum signal adjusted".
- The override label must include a tooltip: *"Weinstein Stage analysis takes precedence over Elder Triple Screen signals when the long-term trend cycle conflicts with short-term momentum."*
- Conflict detection already exists in `indicators.py`. The gap is **disclosure** — the conflict fires but isn't explained clearly enough for a non-expert user to understand which signal governs the decision.
- No new analytical framework may be added to the verdict pipeline without (a) defining its position in the override hierarchy and (b) adding a regression check for the override behaviour.

### Audit findings that triggered this policy
- Expert QA #14: Elder says BUY SETUP, Weinstein says WAIT — both at equal visual weight, no arbitration disclosed (OPEN-012)
- Data Dependency C-04: Same finding — signal arbitration failure
- Dashboard audit D-01: Score 59/100 (BUY territory) but WATCH verdict — confusing without explanation (partially addressed by Option B, v5.31)

---

## Policy 7 — Data Freshness Labeling

**Principle:** Any label making a recency claim must be verified against an actual timestamp. Stale data must never be presented as live.

### Rules
- The label "📰 Live Headlines" may only be shown when the most recent article in the feed is less than 48 hours old. Otherwise show "📰 Recent Coverage (DD Mon YYYY)" where the date is the actual date of the most recent article.
- The label "Market LIVE" (green badge) may only be shown when `market_open` is `True` as computed by `_is_market_open()`. When all markets are closed, show "Market CLOSED — Last prices as of [timestamp]".
- The subtitle "Real-time geopolitical & technology trends" may only appear on the Global Intelligence page when at least one live data source (RSS feed with articles <24h old) is actively returning current content.
- Any static analytical text that contains specific quantitative claims (percentages, timeframes, economic projections) must carry a "Source: X | As of: YYYY-MM" attribution.
- RSS feeds must be validated for recency on every deployment. A feed whose most recent article is >90 days old must be replaced before deployment.

### Audit findings that triggered this policy
- GI audit F-03: AI & Jobs section serving 2022–2023 articles labeled "Live" (fixed v5.31)
- GI audit F-11: Page subtitle claims "Real-Time" while map is broken and AI content is 3 years old
- Data Dependency C-09: "Market LIVE" fires on Streamlit runtime not market hours (OPEN-015)
- Home audit H-02: Global Trend Signals show "—" on first load with no loading state explanation

---

## Enforcement

### Current (v5.31)
Policies 4, 6, and 7 are partially enforced via regression checks (R17, R19, R21) and DO NOT UNDO rules in CLAUDE.md. Policies 5 is partially enforced by the Watch Out For RSI/MACD gate added in v5.31.

### Planned (v5.33) — R25 regression checks
New regression category R25 will verify:
- `R25.P4` — SEBI disclaimer string present in `_tab_insights()`
- `R25.P4` — Algorithmic disclosure string present in `_tab_insights()`
- `R25.P4` — `_render_next_steps_ai()` not called from `render_global_intelligence()`
- `R25.P5` — `_calc_change_pct` utility exists in `utils.py` (after OPEN-008 implemented)
- `R25.P6` — Override label present in `_render_header_static()` for conflict case
- `R25.P7` — `_age_h` freshness gate present in `_render_topic_card()`
- `R25.P7` — `market_open` gates the LIVE badge in `app.py`
