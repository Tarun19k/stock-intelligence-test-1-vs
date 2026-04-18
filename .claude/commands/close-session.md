---
description: Close the current GSI Dashboard session — writes a machine-readable breadcrumb before any /clear, enabling lean startup (~9k) instead of full /new-session (~50k) on the next deliberate clear.
---

# Close Session — GSI Dashboard

Run this command **before** issuing `/clear` at the end of a deliberate session pause.
This enables the next session to restore context with a lean startup instead of a full
`/new-session` protocol.

> **Do NOT run if context was NOT going to be cleared.** The breadcrumb is only useful
> before a deliberate `/clear`. Unexpected session limits still require `/new-session`.

---

## When to use

- You are pausing work mid-session and plan to `/clear` and resume later
- The sprint is still IN_PROGRESS (GSI_WIP.md Status: ACTIVE)
- You want the next session to skip the 10–15k source-file reads of full /new-session

When **not** to use:
- Sprint is COMPLETE (just let /new-session run at next start — the WIP is already IDLE)
- You did not finish the implementation work in this session and there is no clean checkpoint

---

## Steps

### Step 1 — Verify GSI_WIP.md is in a clean state

Read the current GSI_WIP.md `## Session Status` block.

- If Status is `ACTIVE` and a CHECKPOINT block exists → proceed to Step 2.
- If Status is `IDLE` → breadcrumb not needed. Report: "WIP is already IDLE — breadcrumb not required. Use /new-session at next start."
- If Status is `ACTIVE` but no CHECKPOINT exists → write the CHECKPOINT block first (per CLAUDE.md Rule 4), then proceed to Step 2.

### Step 2 — Run regression baseline

```bash
python3 regression.py
```

Note the N/N result. This will be stored in the breadcrumb so the next session
can verify the baseline in one command instead of re-reading CLAUDE.md.

### Step 3 — Identify latest snapshot number

```bash
grep -n "^## SNAPSHOT-[0-9]" GSI_SESSION_SNAPSHOT.md | sort -t'-' -k2 -n | tail -1
```

Note the SNAPSHOT number (e.g. SNAPSHOT-015).

### Step 4 — Read current version from GSI_WIP.md

From the Session Status block already read in Step 1, extract:
- `Version` field (e.g. "v5.39 → v5.40")
- `Sprint` field (e.g. "v5.40 IN_PROGRESS")
- `Session ID` field (e.g. "session_030")

### Step 5 — Write breadcrumb file

Write `.claude/session_breadcrumb.json` with the following structure:

```json
{
  "written_at": "[YYYY-MM-DD]",
  "session_id": "[session_NNN]",
  "version": "[vX.XX → vX.XX or single version if COMPLETE]",
  "sprint": "[vX.XX IN_PROGRESS | vX.XX COMPLETE]",
  "regression_baseline": "[N/N PASS]",
  "regression_count": N,
  "latest_snapshot": "SNAPSHOT-[NNN]",
  "wip_status": "ACTIVE",
  "branch": "[git rev-parse --abbrev-ref HEAD output]",
  "last_commit": "[git rev-parse --short HEAD output]",
  "resume_note": "Lean startup available. Run: python3 regression.py → verify [N/N]. If mismatch, fall back to /new-session."
}
```

Use Bash to get branch and last commit:
```bash
git rev-parse --abbrev-ref HEAD && git rev-parse --short HEAD
```

### Step 6 — Commit the breadcrumb

```bash
git add .claude/session_breadcrumb.json GSI_WIP.md
git commit -m "chore(session_NNN): close-session breadcrumb + WIP checkpoint"
git push
```

### Step 7 — Report and clear

Print:

```
✓ Breadcrumb written to .claude/session_breadcrumb.json
  Version:     [version]
  Sprint:      [sprint]
  Regression:  [N/N PASS]
  Snapshot:    [SNAPSHOT-NNN]
  Branch:      [branch] @ [commit]

Lean startup available next session:
  1. Read .claude/session_breadcrumb.json
  2. python3 regression.py → verify [N/N]
  3. If match: resume from GSI_WIP.md CHECKPOINT
  4. If mismatch: fall back to /new-session (full protocol)

Safe to /clear now.
```

Then the user may issue `/clear`.

---

## Lean startup protocol (next session after a /close-session)

When resuming after a deliberate close (breadcrumb exists):

1. Read `.claude/session_breadcrumb.json` (~0.3k)
2. Run `python3 regression.py` (~3k) — compare to `regression_count` in breadcrumb
3. If match → read GSI_WIP.md CHECKPOINT block only (~2k) → resume from "Currently working on" line
4. If mismatch → fall back to full `/new-session` protocol

**Estimated cost: ~5–9k tokens** (vs ~35–50k for full /new-session)

Savings break-even: any session that would otherwise need `/new-session` after a deliberate clear.

---

## Files written

- `.claude/session_breadcrumb.json` — lean startup anchor (overwritten each close)
- `GSI_WIP.md` — CHECKPOINT block (if not already written)

---

*Added v5.40 (session_030). Addresses wiring gap identified in session_029 investigation:
close-session → breadcrumb → lean 9k startup vs 50k /new-session.*
