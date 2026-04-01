## Summary
<!-- One sentence: what does this PR change and why? -->

## Version
<!-- e.g. v5.32 -->

## Fixes / Changes
<!-- List each change with its audit reference ID where applicable -->
- [ ] Fix: [description] (audit ref: [e.g. OPEN-008, H-01])
- [ ] Fix: [description]

## Regression
```
python3 regression.py
```
- [ ] ALL 427 CHECKS PASS (or current baseline — verify against CLAUDE.md)

## Compliance (Tier 1–3 must all pass before merge)

### Tier 1 — P0 Regulatory
- [ ] SEBI disclaimer present in `_tab_insights()` above the 3 columns
- [ ] Algorithmic disclosure present in `_tab_insights()`
- [ ] No raw Momentum score (X/100) in dashboard header
- [ ] "No major red flags" blanket fallback NOT present
- [ ] ROE shows N/A when `sig["roe"] == 0`
- [ ] `_render_next_steps_ai()` NOT called from GI page

### Tier 2 — P0 Data Integrity
- [ ] All RSS feeds verified live within last 30 days
- [ ] Any metric shown on 2+ pages uses the same calculation function

### Tier 3 — Architecture
- [ ] No page file imports yfinance directly
- [ ] No Streamlit calls in indicators.py / forecast.py / portfolio.py
- [ ] `_is_rate_limited()` called before every new yfinance function
- [ ] VERSION_LOG entry added to version.py

## QA
- [ ] QA brief generated and sent to tester
- [ ] All fixes in this PR verified by QA
- [ ] Cross-page data consistency spot check completed (see GSI_QA_STANDARDS.md §9)

## Session manifest
- [ ] GSI_session.json updated (file_state, open_items, session entry)
- [ ] CLAUDE.md current state updated
- [ ] GSI_session.json pushed to Gist

## Notes
<!-- Any scope limitations, known issues, or follow-up items for next sprint -->
