# GSI Dashboard — Development Skills & Learned Patterns
# Version: 1.1 | Updated: 2026-03-31
# Source: Sessions 001–010, audit reports v5.28–v5.32
# This is the accumulated institutional knowledge for building GSI correctly.
# Read before implementing any new feature. Update after every sprint.

---

## Skill 1 — Adding a New Metric to the KPI Panel

**Context:** `_render_kpi_panel()` in `dashboard.py`. Called for every stock view.

### DO
- Check whether the metric is available from `get_ticker_info()` for all asset classes
- Add a null guard before display: `val_str = f'{val:.1f}%' if val != 0 else "N/A"`
- Add a `HELP_TEXT` entry in `config.py` and wire it to the `tip=` parameter
- For fundamentals (ROE, P/E, P/B): suppress for non-equity asset classes using `show_fundamentals = asset_class in ("equity", "etf")`
- Test with at least one Indian large cap, one US stock, and one debt/rates instrument

### DO NOT
- Do not display a raw 0.0 value from `safe_float(None)`. `safe_float` returns 0.0 for null — 0.0 is not a valid ROE, it's a data gap.
- Do not add a metric that requires a separate API call without a TTL ≥ 24h on that call
- Do not show a metric for which the calculation methodology is not explained in a tooltip

### Learned from
- D-02 audit finding: ROE 0.0% for Reliance (actual ~10%) — yfinance returns null, `safe_float(None) = 0.0`, display showed 0.0% as if it were data

---

## Skill 2 — Adding an AI Narrative / Insight Section

**Context:** `_tab_insights()` in `dashboard.py`. The Watch Out For / What to Consider / What the Data Says columns.

### DO
- Always include the algorithmic disclosure banner above the insight columns
- Always include the SEBI disclaimer below or within the section
- Write insight text from raw indicator values (`sig["rsi"]`, `sig["macdh"]`), never from derived labels
- Use a defensive fallback that reflects actual data state: if RSI < 45 or MACD < 0, the fallback MUST reflect weakness, not neutrality
- Label the section explicitly: "Algorithmically generated from quantitative signals. Not human analyst opinion."

### DO NOT
- Do not hard-code fallback text like "No major red flags at this time." — this fires regardless of actual market conditions
- Do not generate narrative text that contradicts the raw indicators shown in the same panel on the same screen
- Do not name specific stocks as recommendations without showing their current BUY/WATCH/AVOID verdict

### The narrative ↔ data coherence rule
Every statement in the narrative must be traceable to a data point in the `sig` dict. If the narrative says "momentum is healthy", RSI must be > 50. If RSI = 36, the narrative must not say "neutral momentum zone."

### When integrating Claude API for narrative (OPEN-018)
- Use `claude-haiku-4-5` for real-time dashboard calls — Opus/Sonnet are too slow and too expensive
- Gate behind a button ("Generate AI Summary") — never auto-call on every rerun
- Cache output with `@st.cache_data(ttl=3600)` — narrative doesn't need hourly refresh
- API key must come from `st.secrets["ANTHROPIC_API_KEY"]` — never hardcoded
- Every Claude-generated paragraph must carry the algorithmic disclosure label
- Pass raw `sig` dict values to the prompt, never the verdict label — let Claude reason from data

### Learned from
- C-01: "No major red flags" shown while RSI=36, ADX=declining, 9/12 US sectors negative
- C-03: RSI 36 (bearish, approaching oversold) described as "neutral momentum zone" in AI text
- Expert QA #29, #32: Zero disclaimers, unlabeled algorithmic output

---

## Skill 3 — Adding a New RSS Feed / News Source

**Context:** `config.py` GLOBAL_TOPICS `"rss"` lists. Consumed by `get_news()` in `market_data.py`.

### DO
- Verify the feed is active by checking the most recent article date before adding
- Add the domain to the RSS allowlist in `market_data.py` (`_RSS_ALLOWLIST`)
- Use HTTPS URLs only
- Prefer feeds that update daily or more frequently for topics marked "Live"
- Test the feed with `feedparser.parse(url)` and check `entries[0].published` before shipping

### DO NOT
- Do not add feeds from platforms known for infrequent updates (TechCrunch Hype, niche newsletters)
- Do not keep a feed in production if its most recent article is > 90 days old
- Do not label a section "📰 Live Headlines" if the feed's freshness has not been verified

### The 48-hour rule
If the most recent article in a feed is older than 48 hours, the UI label must show "📰 Recent Coverage (DD Mon YYYY)" not "📰 Live Headlines". This is implemented in `_render_topic_card()` via `_age_h` check.

### Learned from
- F-03 audit finding: TechCrunch Hype feed serving 2022 articles labeled "Live" (fixed v5.31)
- GI audit F-11: False "Real-Time" claim in page subtitle

---

## Skill 4 — Adding a New Page Section with Expandable Content

**Context:** `st.expander()` calls in `global_intelligence.py` and elsewhere.

### DO
- Default to `expanded=True` when the section contains the primary value of the page
- Default to `expanded=False` only for supplementary/advanced content that would overwhelm the first impression
- Ensure the page communicates value within the first visible screen on load — never require a user to click to see content

### DO NOT
- Do not collapse all sections on a page. A page where all content requires clicking is an empty-looking page.
- Do not use `st.expander` as a way to hide content you're not sure about — if content isn't confident enough to show by default, reconsider whether it should be on the page at all.

### Learned from
- F-15 audit finding: GI page loaded with all sections collapsed — beginners navigated away immediately (fixed v5.31)

---

## Skill 5 — Implementing Signal Override Logic

**Context:** `compute_unified_verdict()` in `indicators.py`. The 4-layer verdict system.

### DO
- The override hierarchy is: **Weinstein Stage > Elder Triple Screen > Raw Score**
- When a veto fires, set `align_text` to explicitly name the override: "Stage override applied — Weinstein Stage 4 vetoes momentum signal"
- Add a tooltip on the override label explaining the hierarchy in plain English
- The veto must be disclosed visually, not silently applied

### DO NOT
- Do not show BUY and WAIT signals at equal visual weight with no resolution indicator
- Do not use generic labels ("Momentum signal adjusted") when a specific override has fired — tell the user WHICH framework overrode WHICH
- Do not add a new analytical framework to the verdict pipeline without (a) defining its override position and (b) adding a regression check

### The arbitration rule
Two conflicting signals at equal visual weight with no resolution instruction is a financial harm risk. A user acting on the wrong signal because arbitration was unclear is the failure mode. Always err toward more disclosure, not less.

### Override label format (v5.31+)
When a Weinstein Stage veto fires, `align_text` must use this exact pattern:
> "Stage [N] override applied — Weinstein Stage [N] vetoes [Elder/momentum] signal"

Generic labels like "Momentum signal adjusted" are insufficient — name both frameworks.

### Learned from
- C-04 / Expert QA #14: Elder BUY SETUP + Weinstein WAIT shown side-by-side, equal weight, no guidance (OPEN-012)
- Dashboard D-01: Score 59/100 (BUY territory) with WATCH verdict — user confusion without explanation

---

## Skill 6 — Working with yfinance for Indian Stocks

**Context:** `market_data.py`. yfinance 1.2.0.

### What works reliably for NSE/BSE stocks
- `yf.download(tickers, period, interval)` — price OHLCV, chunked via `_yf_batch_download()`
- `Ticker.history()` — equivalent to download, single ticker
- `Ticker.financials` — annual income statement (Net Income available, large caps only)
- `Ticker.balance_sheet` — annual balance sheet (Equity available, large caps only)

### What is unreliable for NSE/BSE stocks
- `Ticker.info['returnOnEquity']` — frequently returns None for Indian stocks
- `Ticker.info['netIncomeToCommon']` — frequently None
- `Ticker.info['bookValue']` — inconsistent
- Intraday data for BSE-listed stocks — use NSE suffix (.NS) not BSE (.BO) for intraday

### The null handling rule
`safe_float(None)` returns `0.0`. This is the correct behaviour for price calculations. But `0.0` is NOT a valid ROE — it means no data. Always guard: `val_str = f'{val:.1f}%' if val != 0 else 'N/A'` for fundamental metrics.

### Rate limiting
- `_is_rate_limited()` must be checked before every yfinance call
- `get_ticker_info()` has the gate since v5.29
- TTLs: price 300s, ticker info 600s, financials 24h (86400s when implemented)
- Chunk size: 3 tickers per batch, 5s inter-chunk gap

### Learned from
- v5.27 crisis: 8,345-event 429 death spiral from missing rate limit gate
- v5.29: `get_ticker_info` was missing `_is_rate_limited()` gate
- D-02: ROE 0.0% from `safe_float(None)` — data gap displayed as data

---

## Skill 7 — CSS for Streamlit 1.55

**Context:** `styles.py`. Streamlit Cloud deployment.

### Known working selectors (1.55)
```css
/* Sidebar collapse pill when sidebar is closed */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] { ... }

/* Sidebar toggle in main area when collapsed */
section[data-testid="stMain"] button[data-testid="baseButton-headerNoPadding"] { ... }

/* Hide deployment button */
[data-testid="stDeployButton"] { display: none !important; }

/* App toolbar — transparent */
[data-testid="stAppToolbar"] { background: transparent !important; }
```

### Known broken patterns
- `width='stretch'` on `st.dataframe` — raises TypeError in 1.43+
- `[data-testid="stToolbar"] > *:not([data-testid="collapsedControl"])` — interferes with 1.55 toolbar redesign
- `scope='fragment'` on `st.rerun()` — StreamlitAPIException in all versions

### `width="content"` is valid in 1.52+
Use `width="content"` on `st.dataframe` for content-width mode. Do NOT flag this in R2 regression.

### Learned from
- v5.30: Sidebar collapse button disappeared after upgrade to 1.55 — wrong selector
- v5.28 crisis: Cold start hang from `streamlit==1.43.2` incompatible with Python 3.14

---

## Skill 8 — Writing Regression Checks

**Context:** `regression.py`. Run before every commit.

### DO
- Use exact string matching for critical contracts: `"SEBI-registered investment advisor" in db`
- Use `re.findall(r'(?<!def )functionname\(\)', src)` to check for function calls (not definitions)
- When a feature is intentionally moved to a different file, update the check to look in the new file
- After any Option B-style change (removing a UI element), update the corresponding regression check immediately

### DO NOT
- Do not check `dashboard.py` for strings that live in `indicators.py` (e.g. "RATES CONTEXT")
- Do not use `"functionname() not in src"` — this will match the function definition as well as calls
- Do not let a regression check become stale after refactoring — a passing check on stale logic is worse than a failing check

### Known false positives (v5.31)
| Check | Issue | Fix |
|---|---|---|
| `"_render_next_steps_ai() not in gi"` | Matches function definition | Use negative lookbehind regex |
| `"RATES CONTEXT" in dashboard.py` | Wrong file — lives in indicators.py | Check indicators.py |
| `"Momentum:" in dashboard.py` | Removed from header (Option B) | Check for "Momentum Signal Panel" instead |

### Learned from
- v5.31 audit: 2/43 checks were false positives — audit script bugs, not code bugs
- v5.25: R13/R15 checks became stale after `_refresh_fragment` removal — had to invert checks

---

## Skill 9 — Deploying to Streamlit Cloud (Python 3.14)

**Context:** `requirements.txt`, `packages.txt`, no `runtime.txt`.

### Working configuration (v5.28+)
```
streamlit==1.55.0
yfinance==1.2.0
pandas>=1.4.0        # NOT >=3.0.0 — streamlit declares pandas<3 in metadata
numpy>=2.0.0
cvxpy==1.8.2
plotly==5.24.1
feedparser==6.0.11
pytz==2024.2
requests==2.32.3
```

### The pandas constraint
Streamlit 1.55.0's package metadata declares `pandas<3`. pip and uv both reject `pandas>=3.0.0` with a conflict error. Use `pandas>=1.4.0` to let pip resolve to the latest compatible 2.x version. The code is compatible with both 2.x and 3.x — this is a metadata constraint only.

### Local install
```bash
uv pip install -r requirements.txt   # preferred — matches Cloud
pip install -r requirements.txt      # will fail on pandas>=3.0.0
```

### Verify after install
```bash
python3 -c "import streamlit, yfinance, pandas; print(streamlit.__version__, yfinance.__version__, pandas.__version__)"
# Expected: 1.55.0  1.2.0  2.x.x
```

### Learned from
- v5.28 crisis: `pandas>=3.0.0` caused ResolutionImpossible on both pip and uv locally
- Root cause: streamlit 1.55 metadata still declares `pandas<3` even though code is compatible

---

## Skill 10 — Adding a New Global Intelligence Topic

**Context:** `GLOBAL_TOPICS` dict in `config.py`. Rendered by `_render_topic_card()` in `global_intelligence.py`.

### Required structure for every topic
```python
"🔴 Topic Name": {
    "color": "#hexcolor",
    "subtitle": "Theme1 · Theme2 · Theme3",
    "overview": "2–3 sentence summary. No quantitative claims without citation.",
    "chain": [
        ("Node Label", "#color", "Tooltip — max 40 chars"),
        ("Next Node",  "#color", "Tooltip"),
        ("Final Node", "#color", "Tooltip"),
    ],
    "india_impact": "Specific India-relevant impact. Formula preferred over static text.",
    "market_sectors": ["Sector1", "Sector2"],  # NSE sector names
    "watchlist": ["TICKER.NS", "TICKER2.NS"],  # 4–6 tickers max
    "rss": [
        "https://active-feed-verified.com/feed",  # verify <48h fresh before adding
    ],
}
```

### Minimum viable topic
- At least 3 nodes in the impact chain
- At least 2 RSS feeds, both verified fresh
- At least 3 watchlist tickers relevant to the topic
- India impact statement present
- No quantitative claims (%, $, cr) without source and date

### Learned from
- GI audit F-01: Only 2 topics for a page claiming "Global Intelligence Centre"
- GI audit F-14: West Asia text makes claims with no source attribution
- GI audit F-13: India impact formula static — should be dynamic vs live Crude price

---

## Skill 11 — Adding Any Feature That Displays Stock Signals

**Context:** Any page file or dashboard component that shows BUY/WATCH/AVOID, price targets, or investment-oriented text to users.

### DO
- Run `/legal-review` before shipping any new signal-displaying feature
- Every BUY/WATCH/AVOID section must carry the SEBI disclaimer — no exceptions (Hard Rule 13)
- Every algorithmically generated text block must carry the disclosure label
- Frame all signals as "signal visualisation for self-directed research" — never as "recommendations"
- Check `/policy-check` for jurisdiction-specific rules if the feature targets a specific market

### DO NOT
- Do not use the words "buy", "sell", "target price", "entry level", or "exit level" in UI text
- Do not claim data is "real-time" — yfinance has a 15–20 min delay for most markets
- Do not display performance comparisons ("our signals beat the index") without substantiated backtests
- Do not show Chinese A-share signals with investment-oriented framing — CSRC enforcement risk is high
- Do not add a social sharing button that shares a specific signal result — SEBI finfluencer rules apply

### The regulatory hierarchy for GSI
India (SEBI) is the highest-risk jurisdiction. If a feature is legally safe for India, it is safe everywhere.
If a feature is borderline for India, run it past `/legal-review` before shipping.

### Learned from
- Session 010: Full regulatory research across SEBI/SEC/MiFID II/FCA/CSRC
- SEBI finfluencer rules: even free tools displaying live signals on social media face enforcement
- Yahoo Finance ToS: redistribution prohibition means any commercial path requires a licensed data source

---

## Skill 12 — Implementing a Shared Calculation Function

**Context:** Any metric calculated in more than one place (Home, Dashboard, GI page).

### DO
- Before implementing a metric, search all pages for existing calculations of the same value
- If the same metric appears in 2+ places, extract it into `utils.py` as a shared function
- `calc_5d_change(df)` in `utils.py` is the canonical example — use it, never re-implement inline
- Name shared functions descriptively: `_calc_5d_change(df)` not `_get_change(df)`
- Add a regression check that verifies the shared function is imported and used in all call sites

### DO NOT
- Do not implement the same calculation differently in two files — the results will diverge silently
- Do not put calculation logic in page files — pages receive pre-computed data, they don't compute
- Do not add a utility function for a calculation that only appears in one place — YAGNI

### The data coherence rule (GSI_GOVERNANCE Policy 5)
Same metric = same calculation function across all pages.
If two pages show "5-day return" and one uses close-to-close while the other uses OHLCV-adjusted,
users will see different numbers for the same stock on the same day. This destroys trust.

### Learned from
- OPEN-008 (H-01 audit): 5-day calculation was implemented differently in Home, Dashboard, and GI
- Resolution: `calc_5d_change(df)` added to utils.py, all three pages updated in v5.32

---

## Anti-Patterns Catalogue

These patterns have caused production bugs or audit failures. Never reproduce them.

| Anti-pattern | Why it's wrong | Correct pattern |
|---|---|---|
| `safe_float(info.get("returnOnEquity", 0))` then display raw | `safe_float(None) = 0.0` — zero is not a data gap indicator | `val = safe_float(...); val_str = f'{val:.1f}%' if val != 0 else 'N/A'` |
| `cautions or ["No major red flags at this time."]` | Template fires regardless of actual data | Gate on RSI/MACD: `["Momentum indicators are mixed..."] if rsi < 45 or macdh < 0` |
| `with st.expander(name, expanded=False)` for primary content | Page looks empty — users navigate away | `expanded=True` for all primary content sections |
| Calling `_render_next_steps_ai()` | Career advice disconnected from market data = liability | Replace with contextualised action cards tied to live signals |
| `"Live Headlines"` label without timestamp check | Serves stale content as current | Gate on `_age_h < 48` — see `_render_topic_card()` v5.31 |
| `pandas>=3.0.0` in requirements.txt | Streamlit metadata declares `pandas<3` — pip/uv reject | Use `pandas>=1.4.0` |
| Checking `dashboard.py` for "RATES CONTEXT" | String lives in `indicators.py` | Check the file where the logic is, not where output is consumed |
| `st.rerun(scope='fragment')` | StreamlitAPIException in all Streamlit versions | Use plain `st.rerun()` |
| `_refresh_fragment` in app.py | Flooded Cloud logs every 60s — no-op | Removed v5.26. Do not re-add. |
| Equal visual weight for conflicting signals | User acts on wrong signal — financial harm | Always show override label when arbitration fires |
| Same metric calculated inline in multiple pages | Values diverge silently — users see different 5d returns on Home vs Dashboard | Extract to `utils.py` shared function; regression check all call sites |
| "Real-time" label on yfinance data | yfinance has 15–20 min delay — false claim, SEBI/FCA risk | Gate "Live" label on `market_open` bool + timestamp verify |
| Signal result shared on social media with live price | SEBI finfluencer rules apply even for free tools | Use screenshots of methodology/historical examples for social, never live signal results |
| Hardcoded session prompt file (CLAUDE_SESSION_PROMPT.txt) | Pre-governance artefact — Claude Code never read it | Use `.claude/commands/new-session.md` — auto-loads in Claude Code |
| Claude API narrative auto-calls on every rerun | Cost spiral + rate limits + 429 errors | Gate behind button + `@st.cache_data(ttl=3600)` |
