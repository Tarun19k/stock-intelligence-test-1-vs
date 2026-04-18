#!/usr/bin/env python3
"""GSI Compliance Checker — pre-push gate.

Extracted from CLAUDE.md §Run Commands inline script with path correction:
dashboard.py -> pages/dashboard.py (root path did not exist).
Run from repo root or from .claude/hooks/pre_push.sh (CWD auto-corrected).
Exit 0 on all checks pass. Exit 1 on any failure.
"""
import os
import re
import subprocess
import sys


def _git_last_commit_date(path: str, repo_root: str) -> str:
    """Return YYYY-MM-DD of the most recent commit touching path, or '' if unknown."""
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%ai', '--', path],
            capture_output=True, text=True, cwd=repo_root, timeout=5,
        )
        return result.stdout.strip()[:10]  # YYYY-MM-DD
    except Exception:
        return ''


def _check_deps_current(repo_root: str) -> bool:
    """Pass if requirements.txt was NOT committed more recently than GSI_DEPENDENCIES.md.
    If git is unavailable or either file has no commit history, pass by default."""
    req_date = _git_last_commit_date('requirements.txt', repo_root)
    dep_date = _git_last_commit_date('GSI_DEPENDENCIES.md', repo_root)
    if not req_date or not dep_date:
        return True   # no history → can't determine; don't block
    return req_date <= dep_date


def _check_jsonl_tier(repo_root: str) -> bool:
    """C11 — latest token-burn-log.jsonl entry must have tier field in every items[] object.
    Pass if file absent (first sprint before log exists) or latest entry has no items.
    Fail if any item in the latest entry is missing a tier field."""
    jsonl_path = os.path.join(repo_root, 'docs', 'ai-ops', 'token-burn-log.jsonl')
    if not os.path.exists(jsonl_path):
        return True  # no log yet — can't fail
    try:
        import json as _jc11
        last_entry = None
        with open(jsonl_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    last_entry = _jc11.loads(line)
        if last_entry is None:
            return True  # empty file — can't fail
        items = last_entry.get('items', [])
        if not items:
            return True  # no items — can't fail
        return all('tier' in it for it in items)
    except Exception:
        return False  # parse error → fail


def main() -> None:
    # CWD detection: if called from a hook context the CWD may be anywhere.
    # Resolve repo root as the directory containing this file.
    _repo_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(_repo_root)

    files = {
        'db': open('pages/dashboard.py').read(),
        'gi': open('pages/global_intelligence.py').read(),
        'md': open('market_data.py').read(),
        'ind': open('indicators.py').read(),
        'ws': open('pages/week_summary.py').read(),
    }

    checks = [
        ('SEBI disclaimer',      'SEBI-registered investment advisor' in files['db']),
        ('Algo disclosure',      'algorithmically generated' in files['db'].lower()),
        ('No raw score',         'Momentum: {score}/100' not in files['db']),
        ('No red flags fallback','"No major red flags at this time."' not in files['db']),
        ('ROE null guard',       'roe_str' in files['db']),
        ('Next steps removed',   len(re.findall(r'(?<!def )_render_next_steps_ai\(\)', files['gi'])) == 0),
        ('RATES CONTEXT',        'RATES CONTEXT' in files['ind']),
        ('Rate limit gate',      '_is_rate_limited()' in files['md']),
        # C9 — requirements.txt changes must be accompanied by GSI_DEPENDENCIES.md update.
        # Compares last-commit date of both files. If requirements.txt was committed more
        # recently than GSI_DEPENDENCIES.md, the constraint log is out of date.
        ('Deps doc current when req changed', _check_deps_current(_repo_root)),
        # C10 — week_summary.py must carry SEBI disclaimer (GAP-05 / Policy 4).
        # File-level check: disclaimer must appear somewhere in week_summary.py.
        # Section-level placement (OPEN-022) is a separate P0 fix tracked in open items.
        ('SEBI disclaimer (week_summary)', 'SEBI-registered investment advisor' in files['ws']),
        # C11 — token-burn-log.jsonl latest entry must have tier field in every items[] object.
        # Enforces schema_version 2 (v5.40+): all sprint items must be classified T1/T2/T3.
        # R36 enforces this at manifest-write time; C11 enforces it at JSONL-write time.
        ('JSONL tier field (token-burn-log)', _check_jsonl_tier(_repo_root)),
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


if __name__ == '__main__':
    main()
