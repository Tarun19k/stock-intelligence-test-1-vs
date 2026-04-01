---
description: Talent & Operations Manager — inventories all Claude skills, identifies gaps and stale skills, assesses operational health, and produces talent requirement reports. Active at all levels; run any time the program state changes.
---

# Talent & Operations Manager

**Role:** Talent Manager + Operations Manager (consolidated)
**Reports to:** CXO / Program Chief → CEO/Founder
**Scope:** Claude skill catalog health, operational process compliance, capability gap analysis

---

## What this skill does

When invoked, it runs two parallel assessments and produces a unified report:

1. **Talent Audit** — inventories all skills in `.claude/commands/`, checks each for freshness, identifies gaps, and flags stale skills that need revision.
2. **Operations Health** — assesses sprint discipline, regression health, compliance gate status, documentation currency, and process adherence.

---

## Step 1 — Talent Audit

Read `.claude/commands/` to list all skill files. For each skill, assess:

**Freshness check (does the skill still reflect reality?):**
- Does the skill reference the current regression baseline? If it hardcodes a number, is it the right one?
- Does the skill reference files that still exist?
- Does the skill cover governance requirements added since it was last written?
- Was any source file the skill reads modified in the last two sprints? If yes, the skill may be stale.

**Coverage check (what skills does the program currently need?):**

Cross-reference the following domains against the existing skill catalog:

| Domain | Expected skills | Check |
|---|---|---|
| Session management | new-session, log-learnings | Exists? Current? |
| Sprint / delivery | sprint-review, compliance-check, qa-brief | Exists? Current? |
| Security & compliance | security-audit, legal-review, policy-check, data-licensing, accessibility | Exists? Current? |
| Product management | mvp-scope, launch-checklist, risk-register | Exists? Current? |
| Content & brand | newsletter, market-position, gsi-brand, changelog-post | Exists? Current? |
| Design & UX | design, canvas-design, theme-factory, web-artifacts-builder, demo-gif | Exists? Current? |
| Export | export-xlsx, export-pdf, docx | Exists? Current? |
| Integration | claude-api, mcp-builder | Exists? Current? |
| Management | cxo, talent-ops | Exists? Current? |
| Feature development | new-feature | Exists? Current? |
| QA & testing | ui-test, perf-profile | Exists? Current? |

**Gap identification:**
List any domain where a skill is missing or where the existing skill does not cover the current program's needs.

**Stale skill candidates:**
Any skill that references a regression baseline, version number, file path, or governance rule that has since changed. Mark as STALE with the specific discrepancy.

---

## Step 2 — Operations Health

Read the following (do not answer from memory — read the actual files):
- `GSI_WIP.md` — is a sprint active? any overdue checkpoints?
- `GSI_SPRINT.md` — sprint velocity, backlog size, anything blocked?
- `GSI_SPRINT_MANIFEST.json` — status (IN_PROGRESS / COMPLETE), any open Tier A gaps?
- `GSI_COMPLIANCE_CHECKLIST.md` — baseline count current?
- `GSI_SESSION_LEARNINGS.md` — how many STALE / DEVIATION records in the last 3 sessions?
- `.github/PULL_REQUEST_TEMPLATE.md` — baseline count current?

Run the compliance gate mentally (read CLAUDE.md "Run Commands" for the 8-gate script). Are all 8 gates expected to pass based on current code?

Assess:
- **Sprint cadence**: Sessions per sprint, items per sprint vs. 9-item ceiling, any stalled items
- **Regression discipline**: Baseline drift (documented vs. actual), R-check gap between features shipped and checks written
- **Doc currency**: How many governance docs were last updated more than 2 sprints ago?
- **Process compliance**: Are Phase 3 close steps being followed? (check last 3 sessions in GSI_SESSION_LEARNINGS.md)

---

## Step 3 — Produce the Talent & Operations Report

Structure:

```
## TALENT & OPERATIONS REPORT
Date: [date] | Session: [session_NNN] | Version: [vX.XX]

### Skill Catalog — [N] skills total
CURRENT: [list of skills assessed as current]
STALE:   [skill name] — [what is stale and why]
MISSING: [domain] — [what skill is needed and what it would cover]

### Operations Health — [HEALTHY / AT RISK / DEGRADED]
Sprint cadence:   [status]
Regression:       [status — actual vs. documented baseline]
Doc currency:     [N docs updated in last 2 sprints, N stale]
Process compliance: [Phase 3 steps followed? Any gaps?]
Open blockers:    [list or "none"]

### Recommended actions (priority order)
1. [action — who owns it — urgency]
2. ...

### Talent requirements for next sprint
[Based on the v5.35 backlog and program state, which skills need to be
invoked, created, or revised before or during the next sprint?]
```

---

## When to run this skill

Run at:
- Start of every sprint (before writing the sprint manifest)
- Before MVP launch sign-off
- Any time a new governance document or regression check is added
- When the CXO requests a talent gap check
- On `/talent-ops` invocation at any time

The report should take approximately 3–5 minutes to produce and should not require
any user input — all data comes from the files listed above.
