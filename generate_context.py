#!/usr/bin/env python3
"""
generate_context.py
Regenerates GSI_CONTEXT.md from GSI_session.json and CLAUDE.md.
Automatically run by regression.py when ALL checks pass.
Can also be run manually: python3 generate_context.py [--check]

Validation: 75 checks across 13 categories.
If validation fails after generation, exits with code 1.
"""

import json, sys, os, re
from datetime import datetime

def find_repo_root(start):
    d = os.path.abspath(start)
    for _ in range(5):
        if os.path.exists(os.path.join(d, 'GSI_session.json')):
            return d
        d = os.path.dirname(d)
    return None

def extract_dnu_rules(claude_src):
    """Pull DO NOT UNDO rules verbatim from CLAUDE.md — never drift from source."""
    dnu_start = claude_src.find('## DO NOT UNDO')
    if dnu_start == -1:
        return []
    dnu_end = claude_src.find('\n---\n', dnu_start)
    block = claude_src[dnu_start:dnu_end] if dnu_end != -1 else claude_src[dnu_start:]
    rules = []
    for m in re.finditer(r'(\d+)\.\s+\*\*([^*]+)\*\*\s*([^\n]*)', block, re.MULTILINE):
        num, title, detail = int(m.group(1)), m.group(2).strip(), m.group(3).strip()
        line = f"{title}"
        if detail and len(detail) < 90:
            line += f" — {detail}"
        rules.append((num, line))
    return sorted(rules, key=lambda x: x[0])

def item_label(item):
    return item.get('title') or item.get('label') or item.get('id')

def build(root):
    """Build content string from all sources."""
    session    = json.load(open(os.path.join(root, 'GSI_session.json')))
    claude_src = open(os.path.join(root, 'CLAUDE.md')).read()

    version    = session['meta']['current_app_version']
    baseline   = session['regression']['expected_output']
    open_items = session['open_items']
    gist_url   = (session.get('gist_index', {}) or {}).get('url') or \
                 'https://gist.github.com/Tarun19k/7c894c02dad4e76fe7c404bf963baeab'
    dnu_rules  = extract_dnu_rules(claude_src)

    L = []

    L += [
        "# GSI Dashboard — Project Context (lean, always-on)",
        "# Upload ONLY this file to Claude Project Files",
        "# Do NOT upload CLAUDE.md (5k tokens) or GSI_session.json (35k tokens) to Project Files",
        "# Regenerate: python3 generate_context.py  (auto-runs after regression.py passes)",
        f"# Generated: {datetime.now().strftime('%Y-%m-%d')} | {version} | {baseline}",
        "# Target: <1,600 tokens. Do not add verbose content here.",
        "",
        "## Identity",
        "Project: Global Stock Intelligence Dashboard",
        "Repo: https://github.com/Tarun19k/stock-intelligence-test-1-vs",
        f"Session manifest (Gist): {gist_url}",
        "Stack: Python 3.14 · Streamlit 1.55 · yfinance 1.2 · pandas>=1.4.0",
        "Deploy: Streamlit Cloud (community) · no API keys · no database",
        f"Current version: {version} | Regression: {baseline}",
        "",
        "## Architecture — one paragraph",
        "14-file modular app. market_data.py is the ONLY yfinance importer.",
        "indicators / forecast / portfolio have ZERO Streamlit calls.",
        "Pages receive pre-computed data — never fetch directly.",
        "4-state routing in app.py: stock → group → market → week.",
        "DataManager M1 exists (data_manager.py) — BYPASS MODE until M4.",
        "  Pages must NOT call DataManager.fetch() until M4 is implemented.",
        "calc_5d_change() in utils.py is the ONLY 5-day calculation function.",
        "GI watchlist uses cache_buster=0 — matches ticker bar cache key.",
        "tickers.json is the single source of truth for all 559 tickers and 38 groups.",
        "",
        "## DO NOT UNDO — hard rules (sourced live from CLAUDE.md)",
    ]

    for num, rule in dnu_rules:
        L.append(f"{num:>2}. {rule}")

    L += [
        "",
        "## Critical patterns (from GSI_SKILLS.md anti-patterns)",
        "safe_float(None)=0.0 — for ROE/fundamentals: show N/A not 0.0% if val==0",
        "GI topic cards: expanded=True by default — collapsed page looks empty to beginner",
        "RSS 48h freshness gate: Live Headlines label only when newest article < 48h old",
        "WorldMonitor: CSP blocks *.streamlit.app — use external link button, not iframe",
        "DataManager.fetch(): banned in pages until M4 — bypass mode enforced",
        "Algo disclosure: every AI narrative section must be labeled algorithmically generated",
        "SEBI disclaimer: required on every BUY/WATCH/AVOID signal section in pages",
        "",
        "## Dependency constraints (full detail in GSI_DEPENDENCIES.md)",
        "C-001 pandas>=1.4.0 NOT >=3.0.0 — streamlit declares pandas<3 in metadata",
        "C-002 streamlit==1.55: CSS selectors changed — see CONSTRAINT-002 before upgrading",
        "C-003 yfinance MultiIndex: df['Close'].iloc[:,0] if isinstance(..., pd.DataFrame)",
        "C-004 Ticker.info ROE returns None for Indian stocks — guard: val!=0 else 'N/A'",
        "C-005 _is_rate_limited() must precede every yfinance call in market_data.py",
        "C-006 FutureWarning: suppress yfinance/pandas warnings via warnings.filterwarnings",
        "C-007 libopenblas-dev in packages.txt — required by cvxpy on Streamlit Cloud Linux",
        "C-008 st.rerun(scope='fragment') raises StreamlitAPIException — use plain st.rerun()",
        "C-009 WorldMonitor CSP blocks all *.streamlit.app embeds — replaced with link button",
        "",
        "## Governance documents (all in repo root)",
        "GSI_WIP.md               READ FIRST every session. Mutex + CHECKPOINT.",
        "CLAUDE.md                Full architecture reference",
        "GSI_GOVERNANCE.md        7 mandatory policies — read before any new feature",
        "GSI_SKILLS.md            10 dev patterns + anti-patterns catalogue",
        "GSI_DECISIONS.md         15 ADRs — check before re-litigating any design choice",
        "GSI_SPRINT.md            Sprint board + backlog",
        "GSI_AUDIT_TRAIL.md       48 audit findings. Append-only. Never edit records.",
        "GSI_DEPENDENCIES.md      9 compatibility constraints. Check before upgrading.",
        "GSI_QA_STANDARDS.md      Test briefs, personas, finding registry",
        "GSI_COMPLIANCE_CHECKLIST.md  Pre-deploy gate. Tier 1-3 block deploy.",
        "GSI_PRODUCT.md           MVP scope, personas, dependency map, monetisation path",
        "GSI_MARKETING.md         Positioning, competitive analysis, launch strategy",
        "GSI_RISK_REGISTER.md     24 risks: technical, legal, product, operational",
        "GSI_LOOPHOLE_LOG.md      6 classes of automation-caught loopholes. Append as discovered.",
        "GSI_SESSION_LEARNINGS.md Per-session stale-info/confusion/hallucination/deviation log. Append-only via /log-learnings.",
        "GSI_SESSION_SNAPSHOT.md  Per-session Q&A snapshot of 10 key invariants. Compared at session start to detect semantic drift.",
        ".claude/commands/        29 slash commands — skills, legal, product, marketing",
        ".claude/rules/           Path-scoped rules — auto-load in Claude Code only (not claude.ai)",
        "",
        "## Open items",
    ]

    for item in open_items:
        priority = item.get('priority', '?')
        label    = item_label(item)
        L.append(f"  {item['id']} [{priority}]: {label}")

    L += [
        "",
        "## Sprint discipline",
        "Max 9 items per sprint — verified ceiling for single-session completion",
        "Commit after every file — never batch multiple files into one commit",
        "Checkpoint protocol: write CHECKPOINT block to GSI_WIP.md if context runs low",
        "  then immediately push GSI_WIP.md + any committed files to GitHub",
        "",
        "## Session start ritual",
        "1. Read GSI_WIP.md FIRST — ACTIVE = resume from CHECKPOINT, IDLE = proceed",
        "2. This file is already loaded (Project Files)",
        "3. Run: python3 regression.py — expect above baseline",
        "4. Read GSI_GOVERNANCE.md before any new feature development",
        "5. Check GSI_SPRINT.md for current sprint backlog",
        "",
        "## Before every commit",
        "regression.py passes → compliance Tier 1-3 (GSI_COMPLIANCE_CHECKLIST.md)",
        "→ version.py entry added → GSI_WIP.md updated (Status: IDLE) → GSI_SPRINT.md updated",
        "→ commit per file (never batch) → push → update Gist",
        "",
        "## Phase 3 sprint close protocol (full sequence)",
        "1. /log-learnings → GSI_SESSION_LEARNINGS.md (stale/confusion/learning records)",
        "2. Trigger review: scan GSI_SNAPSHOT_QUESTIONS.md checklist — did this sprint add/change",
        "   regression checks, modules, DO NOT UNDO rules, or major invariants? If yes, add/retire",
        "   questions in GSI_SNAPSHOT_QUESTIONS.md and bump QSet version.",
        "3. python3 sync_docs.py (auto-update CHANGELOG, README, AGENTS)",
        "4. Update baseline count in GSI_COMPLIANCE_CHECKLIST.md + .github/PULL_REQUEST_TEMPLATE.md",
        "5. Append ADR → GSI_DECISIONS.md; append QA brief → GSI_QA_STANDARDS.md",
        "6. version.py entry; CLAUDE.md baseline + Current State; GSI_CONTEXT.md header",
        "7. GSI_SPRINT.md Done; GSI_WIP.md Status IDLE",
        "8. regression.py final pass — all checks must pass",
        "9. Commit, push, update Gist",
    ]

    return '\n'.join(L)


def validate(content, session):
    """Run all 75 validation checks. Returns list of failure strings."""
    failures = []
    def chk(desc, cond):
        if not cond:
            failures.append(desc)

    ctx = content.lower()

    # State
    chk("version present",   session['meta']['current_app_version'] in content)
    chk("baseline present",  session['regression']['expected_output'] in content)
    chk("repo URL",          'github.com/tarun19k' in ctx)
    chk("gist URL",          'gist.github.com' in ctx)
    chk("python 3.14",       'python 3.14' in ctx)
    chk("streamlit 1.55",    '1.55' in content)
    chk("yfinance 1.2",      '1.2' in content)
    chk("pandas 1.4.0",      '1.4.0' in content)

    # DO NOT UNDO keywords
    for kw in ['forecast.py','cache_buster',"scope='fragment'",'VERSION_LOG','GROUPS',
               'MPA','TATAMOTORS','CSS','_refresh_fragment','get_news','red flags',
               'momentum score','sebi','next_steps_ai','qa brief']:
        chk(f"DNU rule: {kw}", kw.lower() in ctx)

    # Open items
    for item in session['open_items']:
        chk(f"open item {item['id']}", item['id'] in content)

    # Architecture
    for kw in ["market_data.py is the only",'pages receive pre-computed',
               '4-state routing','bypass mode','calc_5d_change',
               'cache_buster=0','zero streamlit','tickers.json']:
        chk(f"arch: {kw}", kw.lower() in ctx)
    chk("DataManager.fetch banned", 'datamanager.fetch' in ctx)

    # Session continuity
    for kw in ['read gsi_wip.md first','active','idle','checkpoint','max 9','commit per file',
               'update gist']:
        chk(f"WIP: {kw}", kw.lower() in ctx)

    # All 10 governance docs
    for doc in ['GSI_WIP.md','CLAUDE.md','GSI_GOVERNANCE.md','GSI_SKILLS.md',
                'GSI_DECISIONS.md','GSI_SPRINT.md','GSI_AUDIT_TRAIL.md',
                'GSI_DEPENDENCIES.md','GSI_QA_STANDARDS.md','GSI_COMPLIANCE_CHECKLIST.md']:
        chk(f"doc listed: {doc}", doc in content)

    # All 9 dependency constraints
    for kw in ['pandas>=1.4.0','constraint-002','multiindex','n/a not 0.0%',
               '_is_rate_limited','futurewarning','libopenblas',
               "scope='fragment'",'worldmonitor']:
        chk(f"dep: {kw}", kw.lower() in ctx)

    # Anti-patterns
    for kw in ['safe_float','red flags','expanded=true','48h','worldmonitor',
               'sebi disclaimer','algo disclosure', 'datamanager.fetch']:
        chk(f"skill: {kw}", kw.lower() in ctx)

    # Regression/compliance
    for kw in ['regression.py','gsi_compliance_checklist.md','tier 1-3']:
        chk(f"reg: {kw}", kw.lower() in ctx)

    # Audit trail
    for kw in ['gsi_audit_trail.md','append-only','48 audit']:
        chk(f"audit: {kw}", kw.lower() in ctx)

    return failures


def run(check_only=False):
    root = find_repo_root(os.path.dirname(os.path.abspath(__file__)))
    if not root:
        print("ERROR: cannot find repo root (no GSI_session.json in parent dirs)")
        return False

    session    = json.load(open(os.path.join(root, 'GSI_session.json')))
    out_path   = os.path.join(root, 'GSI_CONTEXT.md')
    content    = build(root)
    failures   = validate(content, session)
    tokens_est = len(content) // 4

    if failures:
        print(f"CONTEXT VALIDATION FAILED ({len(failures)} issues):")
        for f in failures:
            print(f"  ✗ {f}")
        return False

    if check_only:
        existing = open(out_path).read() if os.path.exists(out_path) else ''
        if existing == content:
            print(f"GSI_CONTEXT.md is current ({tokens_est} tokens, 0 validation failures)")
            return True
        else:
            print("GSI_CONTEXT.md is STALE — run without --check to regenerate")
            return False

    with open(out_path, 'w') as f:
        f.write(content)

    print(f"  GSI_CONTEXT.md updated: {len(content):,} chars ≈ {tokens_est:,} tokens")
    print(f"  {len(session['open_items'])} open items · "
          f"{session['meta']['current_app_version']} · {session['regression']['expected_output']}")
    return True


if __name__ == '__main__':
    ok = run('--check' in sys.argv)
    sys.exit(0 if ok else 1)
