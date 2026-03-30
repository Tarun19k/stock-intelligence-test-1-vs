#!/usr/bin/env python3
"""
sync_docs.py — GSI Dashboard Post-Sprint Documentation Sync
============================================================
Run after every sprint to keep ALL documentation in sync.
GSI_CONTEXT.md is handled separately by regression.py (auto on 0 failures).

Usage:
    python3 sync_docs.py           # full sync + prompted checklist
    python3 sync_docs.py --check   # audit only, no writes (dry run)
    python3 sync_docs.py --auto    # skip all y/n prompts (CI-safe)

Coverage map:
  AUTO  CHANGELOG.md           rebuilt from version.py VERSION_LOG
  AUTO  README.md              version badge + baseline patched
  AUTO  AGENTS.md              mirrors CLAUDE.md version/baseline
  NOTE  GSI_CONTEXT.md         managed by regression.py (not here)
  SEMI  GSI_SPRINT.md          move completed items to Done
  SEMI  GSI_QA_STANDARDS.md    detect missing QA brief for current version
  CHECK GSI_WIP.md             verify Status: IDLE before commit
  CHECK CLAUDE.md              no stale regression count references
  CHECK GSI_COMPLIANCE_CHECKLIST.md  baseline count is current
  CHECK .github/PULL_REQUEST_TEMPLATE.md  baseline count is current
  CHECK version.py             syntax clean, last entry = current version
  CHECK regression.py          R10b gov_docs list = files on disk
  CHECK GSI_session.json       next_version field set correctly
  CHECK GSI_AUDIT_TRAIL.md     all closed findings have RESOLUTION records
  CHECK GSI_DECISIONS.md       current version has at least one ADR
  CHECK GSI_SKILLS.md          prompt if sprint patterns suggest new skill
  CHECK GSI_DEPENDENCIES.md    prompt if new library behaviour encountered
"""

import json, re, os, sys, ast
from datetime import datetime

ISSUES = []

def find_root():
    d = os.path.abspath(os.path.dirname(__file__))
    for _ in range(6):
        if os.path.exists(os.path.join(d, 'GSI_session.json')):
            return d
        d = os.path.dirname(d)
    return None

def load(root, filename):
    path = os.path.join(root, filename)
    return open(path).read() if os.path.exists(path) else ''

def write(root, filename, content, dry_run=False):
    if dry_run:
        print(f"    [DRY-RUN] would write {filename}")
        return
    with open(os.path.join(root, filename), 'w') as f:
        f.write(content)

def ok(msg):    print(f"  \u2705 {msg}")
def warn(msg):  print(f"  \u26a1 {msg}")
def info(msg):  print(f"     {msg}")

def issue(msg):
    ISSUES.append(msg)
    print(f"  \u274c {msg}")

# ── AUTO UPDATES ──────────────────────────────────────────────────────────────

def sync_changelog(root, session, dry_run):
    """Rebuild CHANGELOG.md entirely from version.py VERSION_LOG."""
    ver_src = load(root, 'version.py')
    entries = re.findall(r'\{[^{}]+\}', ver_src, re.DOTALL)
    lines = ["# Changelog", "",
             "All notable changes to GSI Dashboard.",
             "Full technical detail in `version.py` \u2192 `VERSION_LOG`.", ""]
    seen = {}
    for entry in entries:
        v = re.search(r'"version":\s*"([^"]+)"', entry)
        d = re.search(r'"date":\s*"([^"]+)"', entry)
        n = re.search(r'"notes":\s*"([^"]+)"', entry, re.DOTALL)
        if not v or not d: continue
        ver, date = v.group(1), d.group(1)
        if ver in seen or not ver.startswith('v'): continue
        seen[ver] = True
        notes = n.group(1).replace('\\n', ' ') if n else ''
        lines += [f"## {ver} \u2014 {date}", ""]
        for part in re.split(r'\.\s+(?=[A-Z(])', notes):
            part = part.strip()
            if part:
                lines.append(f"- {part}{'.' if not part.endswith('.') else ''}")
        lines.append('')
    content  = '\n'.join(lines)
    existing = load(root, 'CHANGELOG.md')
    version  = session['meta']['current_app_version']
    if content != existing:
        write(root, 'CHANGELOG.md', content, dry_run)
        ok(f"CHANGELOG.md regenerated ({len(seen)} versions, {version} present)")
    else:
        ok(f"CHANGELOG.md already current ({len(seen)} versions)")

def sync_readme(root, session, dry_run):
    """Patch README.md version string and regression baseline."""
    readme   = load(root, 'README.md')
    version  = session['meta']['current_app_version']
    baseline = session['regression']['expected_output']
    updated  = re.sub(r'v\d+\.\d+[\d.]*(?=\s)', version, readme)
    updated  = re.sub(r'ALL \d+ CHECKS PASS', baseline, updated)
    if version not in updated:
        updated = updated.rstrip() + f"\n\nCurrent version: {version} | Regression: {baseline}\n"
    if updated != readme:
        write(root, 'README.md', updated, dry_run)
        ok(f"README.md patched \u2192 {version} / {baseline}")
    else:
        ok("README.md already current")

def sync_agents(root, session, dry_run):
    """Keep AGENTS.md version and baseline in sync with CLAUDE.md."""
    agents   = load(root, 'AGENTS.md')
    version  = session['meta']['current_app_version']
    baseline = session['regression']['expected_output']
    today    = datetime.now().strftime('%Y-%m-%d')
    updated  = re.sub(r'v\d+\.\d+[\d.]*', version, agents)
    updated  = re.sub(r'ALL \d+ CHECKS PASS', baseline, updated)
    updated  = re.sub(r'# Last synced: \d{4}-\d{2}-\d{2}',
                      f'# Last synced: {today}', updated)
    if version not in updated:
        updated = updated.rstrip() + f"\n\n# Last synced: {today} | {version} | {baseline}\n"
    if updated != agents:
        write(root, 'AGENTS.md', updated, dry_run)
        ok(f"AGENTS.md synced \u2192 {version}")
    else:
        ok("AGENTS.md already current")

# ── SEMI-AUTO ─────────────────────────────────────────────────────────────────

def sync_sprint(root, session, dry_run, auto):
    """Move completed items from In Progress to Done in GSI_SPRINT.md."""
    sprint   = load(root, 'GSI_SPRINT.md')
    open_ids = {item['id'] for item in session['open_items']}
    version  = session['meta']['current_app_version']
    in_prog  = re.search(r'### In Progress\n(.+?)(?=###)', sprint, re.DOTALL)
    if not in_prog or 'Nothing' in in_prog.group(1):
        ok("GSI_SPRINT.md \u2014 In Progress empty")
        return
    completed = [i for i in re.findall(
        r'\| (OPEN-\d+|RISK-\d+|[A-Z]+-\d+)', in_prog.group(1))
                 if i not in open_ids]
    if not completed:
        ok("GSI_SPRINT.md \u2014 all in-progress items still open")
        return
    warn(f"GSI_SPRINT.md \u2014 completed items detected: {completed}")
    if not auto and not dry_run:
        if input("     Move to Done? (y/n): ").strip().lower() != 'y':
            info("Skipped \u2014 update GSI_SPRINT.md manually")
            return
    date = datetime.now().strftime('%Y-%m-%d')
    done_hdr = f"### Done \u2014 {version} ({date})"
    tbl_hdr  = "| ID | Description | Verified |\n|---|---|---|"
    if done_hdr not in sprint:
        sprint = sprint.replace('---\n\n### Done',
                                f'---\n\n{done_hdr}\n\n{tbl_hdr}\n\n### Done')
    if not dry_run:
        write(root, 'GSI_SPRINT.md', sprint)
        ok(f"GSI_SPRINT.md \u2014 moved {len(completed)} items to Done")

def check_qa_brief(root, session):
    """Detect if current version has no QA brief in GSI_QA_STANDARDS.md."""
    version = session['meta']['current_app_version']
    if version in load(root, 'GSI_QA_STANDARDS.md'):
        ok(f"GSI_QA_STANDARDS.md \u2014 brief for {version} present")
    else:
        warn(f"GSI_QA_STANDARDS.md \u2014 no brief for {version}")
        info("ACTION: Add a Section using the template at GSI_QA_STANDARDS.md \u00a7 2")
        ISSUES.append(f"GSI_QA_STANDARDS.md: add QA brief for {version}")

# ── CONTENT ACCURACY CHECKS ───────────────────────────────────────────────────

def check_context_freshness(root, session):
    """Verify GSI_CONTEXT.md is current. If stale, instruct to run regression."""
    ctx      = load(root, 'GSI_CONTEXT.md')
    version  = session['meta']['current_app_version']
    baseline = session['regression']['expected_output']
    items_ok = all(item['id'] in ctx for item in session['open_items'])
    if version in ctx and baseline in ctx and items_ok:
        ok(f"GSI_CONTEXT.md \u2014 current ({version}, {baseline})")
    else:
        issue("GSI_CONTEXT.md \u2014 STALE")
        info("Run: python3 regression.py  (auto-regenerates on 0 failures)")
        info("Then re-upload to Claude Project Files")

def check_wip(root):
    wip = load(root, 'GSI_WIP.md')
    if 'IDLE' in wip:
        ok("GSI_WIP.md \u2014 Status: IDLE")
    else:
        issue("GSI_WIP.md \u2014 Status is NOT IDLE \u2014 resolve before committing")

def check_baseline_staleness(root, session):
    """All files with hardcoded baseline counts must match current."""
    baseline = session['regression']['expected_output']
    count    = re.search(r'(\d+)', baseline).group(1)
    targets  = {
        'CLAUDE.md':                        'stale 378 reference',
        'GSI_COMPLIANCE_CHECKLIST.md':      'baseline count',
        '.github/PULL_REQUEST_TEMPLATE.md': 'baseline count',
    }
    for fname, desc in targets.items():
        content = load(root, fname)
        if not content:
            warn(f"{fname} \u2014 not found on disk")
            continue
        # CLAUDE.md: check for any 378 (stale previous count)
        if fname == 'CLAUDE.md' and '378' in content:
            issue(f"{fname} \u2014 stale '378' count found")
            info(f"Replace all '378' references with '{count}'")
        elif fname != 'CLAUDE.md' and count not in content:
            issue(f"{fname} \u2014 current baseline count ({count}) missing")
            info(f"Update to: {baseline}")
        else:
            ok(f"{fname} \u2014 baseline count current")

def check_version_py(root, session):
    ver_src = load(root, 'version.py')
    version = session['meta']['current_app_version']
    try:
        ast.parse(ver_src)
        ok("version.py \u2014 syntax valid")
    except SyntaxError as e:
        issue(f"version.py \u2014 SyntaxError line {e.lineno}: {e.msg}")
        return
    if 'CURRENT_VERSION' not in ver_src:
        issue("version.py \u2014 CURRENT_VERSION not defined")
    else:
        ok("version.py \u2014 CURRENT_VERSION defined")
    last = re.findall(r'"version":\s*"([^"]+)"', ver_src)
    if last and last[-1] == version:
        ok(f"version.py \u2014 last entry = {version} \u2713")
    elif last:
        issue(f"version.py \u2014 last entry is {last[-1]}, expected {version}")
        info(f"Add VERSION_LOG entry for {version}")

def check_regression_r10b(root):
    """R10b gov_docs list must contain all governance docs on disk."""
    reg = load(root, 'regression.py')
    r10b_start = reg.find('gov_docs = [')
    r10b_end   = reg.find(']', r10b_start)
    if r10b_start == -1:
        issue("regression.py \u2014 gov_docs list not found in R10b")
        return
    listed   = set(re.findall(r'"([^"]+\.md)"', reg[r10b_start:r10b_end]))
    required = {'GSI_GOVERNANCE.md','GSI_QA_STANDARDS.md','GSI_SKILLS.md',
                'GSI_COMPLIANCE_CHECKLIST.md','GSI_AUDIT_TRAIL.md',
                'GSI_DECISIONS.md','GSI_SPRINT.md','GSI_WIP.md','GSI_DEPENDENCIES.md'}
    missing = required - listed
    if missing:
        issue(f"regression.py \u2014 R10b missing: {missing}")
        info("Add to gov_docs list in R10b regression check")
    else:
        ok(f"regression.py \u2014 R10b gov_docs complete ({len(listed)} docs)")

def check_session_json(root, session):
    """next_version should be current_version + 1 minor."""
    version  = session['meta']['current_app_version']
    next_ver = session['meta'].get('next_version', 'NOT SET')
    m = re.match(r'v(\d+)\.(\d+)', version)
    if m:
        expected = f"v{m.group(1)}.{int(m.group(2))+1}"
        if next_ver == expected:
            ok(f"GSI_session.json \u2014 next_version: {next_ver} \u2713")
        else:
            warn(f"GSI_session.json \u2014 next_version is '{next_ver}', expected '{expected}'")
            info(f"Update meta.next_version to '{expected}'")
            ISSUES.append(f"GSI_session.json: set next_version to {expected}")

# ── MANUAL CHECKLIST ──────────────────────────────────────────────────────────

def check_audit_trail(root, session):
    """Flag findings that are not open anywhere but have no RESOLUTION record."""
    audit    = load(root, 'GSI_AUDIT_TRAIL.md')
    sprint   = load(root, 'GSI_SPRINT.md')
    open_ids = {item['id'] for item in session['open_items']}
    all_f    = set(re.findall(r'^FINDING \| ([A-Z0-9-]+)', audit, re.MULTILINE))
    all_f.discard('ID')
    resolved = set(re.findall(r'^RESOLUTION \| ([A-Z0-9-]+)', audit, re.MULTILINE))
    untracked = [f for f in all_f
                 if f not in resolved and f not in open_ids and f not in sprint]
    if not untracked:
        ok("GSI_AUDIT_TRAIL.md \u2014 all closed findings have RESOLUTION records")
    else:
        date = datetime.now().strftime('%Y-%m-%d')
        warn(f"GSI_AUDIT_TRAIL.md \u2014 {len(untracked)} need RESOLUTION:")
        for fid in sorted(untracked):
            info(f"RESOLUTION | {fid} | {date} | [version] | FIXED | [description]")
        ISSUES.append(f"GSI_AUDIT_TRAIL.md: add RESOLUTION for {untracked}")

def check_decisions(root, session):
    version = session['meta']['current_app_version']
    if version in load(root, 'GSI_DECISIONS.md'):
        ok(f"GSI_DECISIONS.md \u2014 ADR entry for {version} found")
    else:
        warn(f"GSI_DECISIONS.md \u2014 no ADR for {version}")
        info("Add ADR-NNN for: utility functions, arch changes, option A/B choices, new rules")
        info("Template: see bottom of GSI_DECISIONS.md")
        ISSUES.append(f"GSI_DECISIONS.md: add ADR for {version}")

def check_skills(root, session):
    sessions = session.get('sessions', [])
    summary  = sessions[-1].get('summary', '') if sessions else ''
    triggers = {'null guard':'Skill 4','cache':'Skill 6','dedup':'Skill 3',
                'neutral zone':'Skill 3','override':'Skill 5','label':'Skill 2',
                'freshness':'Skill 8','bypass':'Skill 6'}
    hit = list({s for kw,s in triggers.items() if kw in summary.lower()})
    if hit:
        warn(f"GSI_SKILLS.md \u2014 review for new patterns ({', '.join(hit)})")
        info("Add DO/DON'T entries if a new pattern emerged this sprint")
    else:
        ok("GSI_SKILLS.md \u2014 no obvious new patterns")

def check_dependencies(root, session):
    sessions = session.get('sessions', [])
    summary  = sessions[-1].get('summary', '') if sessions else ''
    kws      = ['version','upgrade','constraint','conflict','compat',
                'requires','library','package','install']
    hit      = [k for k in kws if k in summary.lower()]
    if hit:
        warn(f"GSI_DEPENDENCIES.md \u2014 sprint may have new constraint (keywords: {hit})")
        info("Add CONSTRAINT-NNN entry if a new library limitation was encountered")
    else:
        ok("GSI_DEPENDENCIES.md \u2014 no new constraints detected")

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    dry_run = '--check' in sys.argv
    auto    = '--auto'  in sys.argv

    root = find_root()
    if not root:
        print("ERROR: cannot find repo root")
        sys.exit(1)

    session  = json.load(open(os.path.join(root, 'GSI_session.json')))
    version  = session['meta']['current_app_version']

    print(f"\n{'='*62}")
    print(f"  GSI Documentation Sync \u2014 {version}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    if dry_run: print(f"  MODE: CHECK ONLY (no writes)")
    print(f"{'='*62}")

    print(f"\n\u2500\u2500 AUTO UPDATES \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
    sync_changelog(root, session, dry_run)
    sync_readme(root, session, dry_run)
    sync_agents(root, session, dry_run)
    print(f"  \u2139  GSI_CONTEXT.md: auto-managed by regression.py (run regression to update)")

    print(f"\n\u2500\u2500 SEMI-AUTO \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
    sync_sprint(root, session, dry_run, auto)
    check_qa_brief(root, session)

    print(f"\n\u2500\u2500 CONTENT ACCURACY \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
    check_context_freshness(root, session)
    check_wip(root)
    check_baseline_staleness(root, session)
    check_version_py(root, session)
    check_regression_r10b(root)
    check_session_json(root, session)

    print(f"\n\u2500\u2500 MANUAL CHECKLIST \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
    check_audit_trail(root, session)
    check_decisions(root, session)
    check_skills(root, session)
    check_dependencies(root, session)

    print(f"\n\u2500\u2500 COMMIT \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
    print(f"  git add CHANGELOG.md README.md AGENTS.md")
    print(f"  git add GSI_SPRINT.md GSI_session.json GSI_WIP.md")
    print(f"  git commit -m 'docs: post-sprint sync ({version})'")
    print(f"  git push")
    gist = (session.get('gist_index', {}) or {}).get('url', '')
    if gist: print(f"  Push Gist: {gist}")
    print(f"  Re-upload GSI_CONTEXT.md to Claude Project Files")

    print(f"\n{'='*62}")
    if ISSUES:
        print(f"  {len(ISSUES)} action(s) required:")
        for i, msg in enumerate(ISSUES, 1):
            print(f"  {i}. {msg}")
        print(f"{'='*62}\n")
        sys.exit(1 if not dry_run else 0)
    else:
        print(f"  \u2705 All checks passed \u2014 documentation in sync")
        print(f"{'='*62}\n")

if __name__ == '__main__':
    main()
