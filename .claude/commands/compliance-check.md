---
description: Run all compliance checks before pushing to main. Runs regression suite, then all 5 compliance tiers from GSI_COMPLIANCE_CHECKLIST.md. Reports pass/fail for each item.
---

Run the following checks in sequence and report the result of each:

**Step 1 — Regression suite**
```bash
python3 regression.py
```
Expected: `ALL 378 CHECKS PASS` (or current baseline from CLAUDE.md).

**Step 2 — Quick compliance script**
```python
import re

files = {
    'db':  open('dashboard.py').read(),
    'gi':  open('pages/global_intelligence.py').read(),
    'md':  open('market_data.py').read(),
    'ind': open('indicators.py').read(),
    'app': open('app.py').read(),
}

checks = [
    ('P0: SEBI disclaimer in Insights tab',        'SEBI-registered investment advisor' in files['db']),
    ('P0: Algorithmic disclosure in Insights tab',  'algorithmically generated' in files['db'].lower() or 'Algorithmic analysis' in files['db']),
    ('P0: No raw Momentum score in header',         'Momentum: {score}/100' not in files['db']),
    ('P0: No blanket no-red-flags fallback',        '"No major red flags at this time."' not in files['db']),
    ('P0: ROE null guard present',                  'roe_str' in files['db']),
    ('P0: next_steps_ai not called',                len(__import__('re').findall(r'(?<!def )_render_next_steps_ai\(\)', files['gi'])) == 0),
    ('Arch: RATES CONTEXT in indicators.py',        'RATES CONTEXT' in files['ind']),
    ('Arch: rate limit gate in market_data.py',     '_is_rate_limited()' in files['md']),
    ('Arch: market_open gates LIVE badge',          'market_open' in files['app']),
    ('Freshness: Live Headlines date gate',         '_age_h' in files['gi']),
]

fails = [name for name, ok in checks if not ok]
print(f'{len(checks)-len(fails)}/{len(checks)} compliance checks passed')
if fails:
    for name in fails:
        print(f'  FAIL: {name}')
else:
    print('All compliance checks passed — safe to push')
```

**Step 3 — Governance doc existence**
```bash
ls GSI_GOVERNANCE.md GSI_QA_STANDARDS.md GSI_SKILLS.md GSI_COMPLIANCE_CHECKLIST.md
```

**Step 4 — Version entry**
```bash
python3 -c "from version import CURRENT_VERSION; print('Version:', CURRENT_VERSION)"
```
Confirm CURRENT_VERSION matches what you're deploying.

Report all results clearly. If any check fails, identify the exact fix needed before proceeding.
