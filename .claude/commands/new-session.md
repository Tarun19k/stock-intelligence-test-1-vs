---
description: Start a new GSI Dashboard development session — reads all context files, confirms regression baseline, runs snapshot deviation check, and summarises open items ready to work on.
---

## Step 1 — Mutex check (do this first, before anything else)

Read `GSI_WIP.md`.
- If `Status: ACTIVE` — read the CHECKPOINT block and resume from it exactly. Skip the rest of this command.
- If `Status: IDLE` — proceed.

## Step 2 — Load context

Read these files fully:
1. `CLAUDE.md` — architecture reference, DO NOT UNDO rules, open items
2. `GSI_GOVERNANCE.md` — 7 policies that govern all development
3. `GSI_session.json` — dynamic session state

## Step 3 — Regression baseline

Run:
```bash
python3 regression.py
```

Confirm output matches the baseline in CLAUDE.md. If it does not match, stop and report the discrepancy — do not proceed until resolved.

## Step 4 — Snapshot deviation check (CRITICAL — do not skip)

Read `GSI_SNAPSHOT_QUESTIONS.md`. Note the current QSet version and all ACTIVE (non-RETIRED) questions. For each active question, read the source files listed in the question's **Source** field — do not answer from memory.

Read `GSI_SESSION_SNAPSHOT.md`. Find the most recent SNAPSHOT block and note its QSet version.

For each active question, compare your extracted answer to the previous snapshot's answer:
- Answer differs in substance → **DEVIATION** — log in `GSI_SESSION_LEARNINGS.md` before writing any code; report to user
- Value legitimately changed (new baseline, sprint closed, new rule) → **UPDATED** — note in new snapshot header
- QSet version changed since last snapshot → questions added since then get status **NEW** (no prior answer to compare)
- Identical → no action

Write the new SNAPSHOT block to `GSI_SESSION_SNAPSHOT.md` (append only):
```
## SNAPSHOT-[NNN] | [date] | [session_NNN] | [vX.XX] | [QSet-vN]
*Compared to SNAPSHOT-[NNN-1] (QSet-[vN]). Deviations: [list or "none"]. Updated: [list or "none"]. New questions: [list or "none"].*

**Q01. Regression baseline:** [answer extracted from regression.py output + CLAUDE.md]
...
```

## Step 5 — Session summary

Report:
- Current app version + regression baseline
- Snapshot result: "No deviations" or list of deviations found
- Any pending pre-sprint infrastructure tasks from GSI_WIP.md
- All OPEN items sorted by priority (HIGH first)
- Last session summary (1 sentence from GSI_session.json)

Then ask: **"What would you like to work on this session?"**

Do not write any code or make any changes until the user responds.
