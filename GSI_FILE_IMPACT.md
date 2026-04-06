# GSI File Impact Map
# ════════════════════════════════════════════════════════════════════════
# PURPOSE: Pre-change reference. Before making ANY change, look up the
# change type below and update EVERY file listed. No exceptions.
# Post-change: run python3 sync_docs.py — exits 0 = repo files in sync.
# Memory files are outside the repo; sync_docs.py reminds you of them.
#
# Rule: if your change touches two types, union the file lists.
# ════════════════════════════════════════════════════════════════════════

---

## TYPE A — Version bump (any new version shipped, always applies)

Every release, every hotfix, every patch requires ALL of these.

### Code / config
- [ ] `version.py` — VERSION_LOG entry; CURRENT_VERSION auto-updates

### Session state
- [ ] `GSI_session.json` — THREE fields: `meta.current_app_version`, `meta.current_version` (top-level), `meta.next_version`
- [ ] `GSI_WIP.md` — `Version:` field in Session Status block + session summary

### Documentation
- [ ] `CLAUDE.md` — `## Current State (vX.XX)` header + version block in "Versions since last update"
- [ ] `GSI_SPRINT.md` — Done section (table row per item) + Sprint Velocity table row
- [ ] `GSI_QA_STANDARDS.md` — QA brief for the version (3 visible fixes minimum)
- [ ] `GSI_DECISIONS.md` — ADR entry if any architecture/process decision was made
- [ ] `GSI_SESSION_LEARNINGS.md` — RECORD entries for stale/confusion/learning/deviation

### Auto-generated (via `python3 sync_docs.py`)
- [ ] `CHANGELOG.md`
- [ ] `README.md`
- [ ] `AGENTS.md`

### Auto-generated (via `python3 regression.py`)
- [ ] `GSI_CONTEXT.md`

### Memory (outside repo — sync_docs reminds you, cannot auto-check)
- [ ] `memory/project_overview.md` — version, baseline count, ticker count
- [ ] `memory/project_open_items.md` — remove closed items, add new watch items

---

## TYPE B — Regression baseline changes (+/- any check)

Applies IN ADDITION TO Type A whenever the `regression.py` check count changes.

- [ ] `GSI_COMPLIANCE_CHECKLIST.md` — `ALL N CHECKS PASS` baseline count
- [ ] `.github/PULL_REQUEST_TEMPLATE.md` — `ALL N CHECKS PASS` baseline count
- [ ] `CLAUDE.md` — baseline count in Current State block
- [ ] `GSI_session.json` — `regression.expected_output` + `regression.last_result`

---

## TYPE C — Ticker changes (`tickers.json` modified)

Applies IN ADDITION TO Type A.

- [ ] `memory/project_overview.md` — ticker count (currently 556)
- [ ] `CLAUDE.md` — ticker count in Project Overview line if it appears

---

## TYPE D — New Python file or new entry point

Applies IN ADDITION TO Type A whenever a new `.py` file is created or a new public function added.

- [ ] `CLAUDE.md` — File Structure section (add file + one-line description)
- [ ] `CLAUDE.md` — Key Entry Points section (add public functions)
- [ ] `regression.py` — R8 EP list if new entry point; R1 syntax check list if new module

---

## TYPE E — New governance document (`GSI_*.md`)

Applies IN ADDITION TO Type A whenever a new governance file is created.

- [ ] `regression.py` — R10b `gov_docs` list
- [ ] `CLAUDE.md` — Living Documentation table (name + purpose)
- [ ] `sync_docs.py` — coverage map comment at top

---

## TYPE F — Risk register change (new risk, status change)

Applies IN ADDITION TO Type A.

- [ ] `GSI_RISK_REGISTER.md` — row added or status updated
- [ ] Risk summary counts at bottom of register (Open/Mitigated totals)

---

## TYPE G — Audit finding resolved

Applies IN ADDITION TO Type A.

- [ ] `GSI_AUDIT_TRAIL.md` — RESOLUTION record appended (append-only, never edit)

---

## TYPE H — New loophole / governance failure class caught

Applies IN ADDITION TO Type A.

- [ ] `GSI_LOOPHOLE_LOG.md` — new Class entry appended

---

## TYPE I — New development pattern or anti-pattern discovered

Applies IN ADDITION TO Type A.

- [ ] `GSI_SKILLS.md` — DO / DON'T entry in relevant skill section

---

## TYPE J — New package dependency or constraint

Applies IN ADDITION TO Type A.

- [ ] `requirements.txt` — package added
- [ ] `GSI_DEPENDENCIES.md` — CONSTRAINT-NNN entry
- [ ] `CLAUDE.md` — Environment section if version-pinned

---

## Quick reference matrix

| What you did | Types |
|---|---|
| Shipped any version (sprint or hotfix) | A always |
| Added/removed regression checks | A + B |
| Modified tickers.json | A + C |
| Created a new .py file | A + D |
| Created a new GSI_*.md | A + E |
| Mitigated a risk | A + F |
| Closed an audit finding | A + G |
| Found a new automation failure class | A + H |
| Discovered a new dev pattern | A + I |
| Added a new package | A + J |
| Multiple of the above | A + all relevant |

---

## How to use this file

**Before starting any change:**
1. Identify the change type(s) from the Quick Reference Matrix
2. Open this file and tick every applicable file as a TODO
3. Do not close the sprint until every box is ticked

**During sprint planning:**
Add a `doc_impact` array to each item in `GSI_SPRINT_MANIFEST.json`:
```json
{
  "id": "item-id",
  "change_types": ["A", "B"],
  "doc_impact": [
    "version.py", "GSI_session.json", "GSI_WIP.md", "CLAUDE.md",
    "GSI_SPRINT.md", "GSI_QA_STANDARDS.md", "GSI_COMPLIANCE_CHECKLIST.md",
    ".github/PULL_REQUEST_TEMPLATE.md", "GSI_SESSION_LEARNINGS.md",
    "memory/project_overview.md"
  ]
}
```

**Post-change gate (two commands):**
```bash
python3 sync_docs.py   # exits 0 = all repo-tracked files in sync
python3 regression.py  # exits 0 = all checks pass + GSI_CONTEXT.md refreshed
```
Then manually verify memory files (sync_docs.py lists them in the COMMIT section).
