---
description: Start a new GSI Dashboard development session — confirms regression baseline, runs snapshot deviation check, and summarises open items ready to work on.
---

## Step 1 — Mutex check (do this first, before anything else)

Read `GSI_WIP.md`.
- If `Status: ACTIVE` — read the CHECKPOINT block and resume from it exactly. Skip the rest of this command.
- If `Status: IDLE` — proceed.

## Step 2 — Load context

Read these files:
1. `CLAUDE.md` — architecture reference, DO NOT UNDO rules, open items *(skip if already in context)*
2. `GSI_session.json` — read ONLY the `meta` block and `open_items` array. Do NOT read the full file. Use `offset` parameter to target the relevant section (open_items starts around line 1086). The canonical open items list is in CLAUDE.md — use GSI_session.json only to confirm `current_version` and `meta.last_session`.

> **Do NOT read GSI_GOVERNANCE.md** — the 7 policies are summarized in CLAUDE.md under "Governance Policy Framework." Only read GSI_GOVERNANCE.md when amending a policy.

## Step 3 — Regression baseline

Run:
```bash
python3 regression.py
```

Confirm output matches the baseline in CLAUDE.md. If it does not match, stop and report the discrepancy — do not proceed until resolved.

## Step 4 — Snapshot deviation check (CRITICAL — do not skip)

Read `GSI_SNAPSHOT_QUESTIONS.md` — note the current QSet version and ACTIVE questions.

Find and read the **most recent SNAPSHOT block** from `GSI_SESSION_SNAPSHOT.md`:
1. Run `grep -n "^## SNAPSHOT-[0-9]" GSI_SESSION_SNAPSHOT.md | sort -t'-' -k3 -n | tail -1` to get the highest-numbered snapshot's line number.
2. Use `Read` with `offset=<that line>` and `limit=35` — enough to cover one full block (blocks are ~25–28 lines).
Do NOT read last-N-lines — the file is append-only but older snapshots may be out of order.

For each active question, read source files using targeted offset/limit reads (not full reads). Compare extracted answers to the previous snapshot:
- Differs in substance → **DEVIATION** — log in `GSI_SESSION_LEARNINGS.md` before any code; report to user
- Legitimately changed → **UPDATED** — note in new snapshot header
- New question (QSet version changed) → **NEW** — no prior answer
- Identical → no action

Append new SNAPSHOT block to `GSI_SESSION_SNAPSHOT.md`:
```
## SNAPSHOT-[NNN] | [date] | [session_NNN] | [vX.XX] | [QSet-vN]
*Compared to SNAPSHOT-[NNN-1] (QSet-[vN]). Deviations: [list or "none"]. Updated: [list or "none"]. New questions: [list or "none"].*

**Q01. Regression baseline:** [extracted from regression.py output + CLAUDE.md]
...
```

## Step 5 — Quant audit flag check

Read `.claude/quant_audit_pending.json`. Report:
- If `pending: true` → ⚠️ Quant audit pending — domains: [list] triggered by [file] on [date].
- If `last_full_audit` is null → ⚠️ No quant audit has ever been run. Required before public beta launch.
- If `last_full_audit` is set and >90 days ago → ⚠️ Quarterly quant audit due.
- If pending: false and <90 days → suppress output.

## Step 6 — Session summary

Report:
- Current app version + regression baseline
- Snapshot result: "No deviations" or list of deviations
- Any pending pre-sprint tasks from GSI_WIP.md
- Quant audit status (only if action needed)
- OPEN items from CLAUDE.md sorted by priority (HIGH first) — do NOT re-read GSI_session.json for this

Then ask: **"What would you like to work on this session?"**

Do not write any code or make any changes until the user responds.

---
*Optimized 2026-04-10: removed full GSI_session.json read (~42k tokens), removed redundant GSI_GOVERNANCE.md read (~3k tokens), narrowed snapshot read to last 50 lines. Estimated savings: ~47k tokens per session start.*
