# GSI Dashboard — Pre-Deployment Compliance Checklist
# Version: 1.0 | Established: 2026-03-28
# Run this checklist before every git push to main.
# All items must be YES before deploying. No exceptions for P0 items.

---

## Tier 1 — P0 Regulatory (Block deploy if any fail)

### Disclaimers
- [ ] SEBI disclaimer present in `_tab_insights()` above the 3 insight columns
- [ ] Algorithmic disclosure label present in `_tab_insights()`
- [ ] No named stock recommendations without their BUY/WATCH/AVOID verdict shown alongside
- [ ] "What You Should Do Next" section is NOT present in `global_intelligence.py`
- [ ] No section named "Live" or "Real-Time" where data is static or >48h old

### Signal integrity
- [ ] "No major red flags" fallback is NOT the default Watch Out For text
- [ ] Watch Out For fallback checks RSI and MACD before choosing tone
- [ ] When Weinstein Stage overrides Elder, an override label is shown (OPEN-012 — implement when fixed)
- [ ] Momentum score (X/100) is NOT visible in the dashboard header (Option B, v5.31)

### Data accuracy
- [ ] ROE shows "N/A" when `sig["roe"] == 0` (not "0.0%")
- [ ] P/E shows "N/A" when `sig["pe"] == 0` (already implemented)

---

## Tier 2 — P0 Data Integrity (Block deploy if any fail)

### Freshness
- [ ] All RSS feeds in config.py have been verified live within the last 30 days
- [ ] No feed in any "Live Headlines" section has a most-recent article older than 90 days
- [ ] The AI & Jobs RSS feeds are not TechCrunch Hype or techcrunch.com/feed/

### Consistency
- [ ] Any new metric added to the KPI panel is calculated the same way across all pages it appears on
- [ ] If a 5-day % calculation was modified, both Home and Dashboard use the same function

---

## Tier 3 — Architecture (Block deploy if any fail)

### Module boundaries
- [ ] No page file (`dashboard.py`, `home.py`, etc.) imports directly from `yfinance`
- [ ] No page file calls `yf.download()` or `yf.Ticker()` directly
- [ ] `indicators.py`, `forecast.py`, `portfolio.py` contain zero `import streamlit` statements
- [ ] `data_manager.py` does not import from `market_data.py`

### Rate limiting
- [ ] `_is_rate_limited()` is called before every yfinance API call in `market_data.py`
- [ ] No `time.sleep()` calls outside `_yf_download()` and `_yf_batch_download()`

### Regression
- [ ] `python3 regression.py` returns `ALL 378 CHECKS PASS` (or current baseline — check CLAUDE.md)
- [ ] `version.py` has a new VERSION_LOG entry for the version being deployed
- [ ] CURRENT_VERSION matches the version entry being deployed

---

## Tier 4 — UX (Warn but do not block)

### Layout
- [ ] All KPI card labels fit on one line at 1280px (test at 6 cards per row)
- [ ] Global Intelligence topic cards default to `expanded=True`
- [ ] No section appears empty on cold load (every section has content or a loading state)
- [ ] Market status cards show short labels: IND, USA, EUR, CHN, COMM, ETF

### Chart labeling
- [ ] MACD chart has a timeframe label (Daily / Intraday) — pending OPEN-013
- [ ] Any new chart with a configurable lookback period shows the lookback label on the chart

---

## Tier 5 — Performance (Warn but do not block)

- [ ] No new Python package added without checking bundle size impact
- [ ] No new `@st.cache_data` function with TTL < 10s unless justified
- [ ] Cold-start API calls remain at ≤ 10 tickers (do not reintroduce the 100-ticker cold start)

---

## Quick compliance script

Run this after `python3 regression.py` passes:

```bash
python3 -c "
import ast, re

files = {
    'db': open('dashboard.py').read(),
    'gi': open('pages/global_intelligence.py').read(),
    'md': open('market_data.py').read(),
    'ind': open('indicators.py').read(),
}

checks = [
    ('SEBI disclaimer',         'SEBI-registered investment advisor' in files['db']),
    ('Algo disclosure',         'algorithmically generated' in files['db'].lower() or 'Algorithmic analysis' in files['db']),
    ('No raw score in header',  'Momentum: {score}/100' not in files['db']),
    ('No red flags fallback',   '\"No major red flags at this time.\"' not in files['db']),
    ('ROE null guard',          'roe_str' in files['db']),
    ('Next steps removed',      len(re.findall(r\"(?<!def )_render_next_steps_ai\(\)\", files['gi'])) == 0),
    ('RATES CONTEXT in ind',    'RATES CONTEXT' in files['ind']),
    ('Rate limit gate in md',   '_is_rate_limited()' in files['md']),
]

fails = [(name, ok) for name, ok in checks if not ok]
print(f'{len(checks) - len(fails)}/{len(checks)} compliance checks passed')
if fails:
    print('FAILED:')
    for name, _ in fails:
        print(f'  ❌ {name}')
else:
    print('✅ All compliance checks passed — safe to deploy')
"
```
