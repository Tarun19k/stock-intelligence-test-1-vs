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

Read `GSI_SESSION_SNAPSHOT.md`. Find the most recent SNAPSHOT block.

Answer all 10 questions from the fixed question set (Q1–Q10) based on what you extracted from the files in Steps 2–3. Write your answers mentally.

Compare your answers to the previous snapshot's answers. For each question:
- If your answer differs in substance from the previous snapshot → mark as **DEVIATION**
- If a value legitimately changed (new baseline, sprint closed, new rule) → mark as **UPDATED**
- If identical → no action needed

If any DEVIATIONs are found:
1. Log each one in `GSI_SESSION_LEARNINGS.md` as type DEVIATION before writing any code
2. Investigate the cause: did a doc change ambiguously? did a file get updated without the snapshot being updated?
3. Report the deviations to the user before asking what to work on

Write the new SNAPSHOT block to `GSI_SESSION_SNAPSHOT.md` (append — do not edit previous blocks).

## Step 5 — Session summary

Report:
- Current app version + regression baseline
- Snapshot result: "No deviations" or list of deviations found
- Any pending pre-sprint infrastructure tasks from GSI_WIP.md
- All OPEN items sorted by priority (HIGH first)
- Last session summary (1 sentence from GSI_session.json)

Then ask: **"What would you like to work on this session?"**

Do not write any code or make any changes until the user responds.
