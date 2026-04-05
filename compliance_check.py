#!/usr/bin/env python3
"""GSI Compliance Checker — pre-push gate.

Extracted verbatim from CLAUDE.md §Run Commands inline script.
Run from repo root or from .claude/hooks/pre_push.sh (CWD auto-corrected).
Exit 0 on all checks pass. Exit 1 on any failure.
"""
import os
import re
import sys

# CWD detection: if called from a hook context the CWD may be anywhere.
# Resolve repo root as the directory containing this file.
_repo_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(_repo_root)

files = {
    'db': open('pages/dashboard.py').read(),
    'gi': open('pages/global_intelligence.py').read(),
    'md': open('market_data.py').read(),
    'ind': open('indicators.py').read(),
}

checks = [
    ('SEBI disclaimer',      'SEBI-registered investment advisor' in files['db']),
    ('Algo disclosure',      'algorithmically generated' in files['db'].lower()),
    ('No raw score',         'Momentum: {score}/100' not in files['db']),
    ('No red flags fallback','"No major red flags at this time."' not in files['db']),
    ('ROE guard',            'roe_str' in files['db']),
    ('Next steps removed',   len(re.findall(r'(?<!def )_render_next_steps_ai\(\)', files['gi'])) == 0),
    ('RATES CONTEXT',        'RATES CONTEXT' in files['ind']),
    ('Rate limit gate',      '_is_rate_limited()' in files['md']),
]

fails = [n for n, ok in checks if not ok]
total = len(checks)
passed = total - len(fails)

print(f'{passed}/{total} compliance checks passed')
if fails:
    for n in fails:
        print(f'  FAIL: {n}')
    sys.exit(1)
else:
    print('Safe to push')
    sys.exit(0)
