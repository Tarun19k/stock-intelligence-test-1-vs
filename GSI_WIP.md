# GSI Dashboard — Work in Progress
# ════════════════════════════════════════════════════════════════════════
#
# PURPOSE: This file is a mutex. It records exactly what is in flight
# in the current session so that if Claude hits a usage limit mid-session,
# the next Claude instance knows precisely where to resume — without
# duplicating completed work or skipping incomplete work.
#
# RULES:
# 1. Claude writes to this file FIRST before starting any implementation.
# 2. Claude updates this file as each task completes (tick the checkbox).
# 3. Claude writes a CHECKPOINT block before the session ends.
# 4. The next session reads this file BEFORE anything else.
# 5. If status is ACTIVE and a checkpoint exists, resume from checkpoint.
# 6. If status is IDLE, treat as a fresh session start.
#
# ════════════════════════════════════════════════════════════════════════

## Session Status

```
Status:        IDLE
Session ID:    session_010
Version:       v5.32
Last updated:  2026-03-29
Sprint:        v5.32 complete
```

## Active Tasks (update as each completes)

None — session_010 complete. All v5.32 tasks committed and pushed.

## Completed This Session

- [x] v5.32: calc_5d_change() utility (OPEN-008) — utils.py, home.py
- [x] v5.32: P(gain) neutral zone (OPEN-009) — forecast.py
- [x] v5.32: Forecast dedup (OPEN-010) — forecast.py
- [x] v5.32: Dynamic week titles (OPEN-011) — week_summary.py
- [x] v5.32: Weinstein override label (OPEN-012) — dashboard.py
- [x] v5.32: MACD (Daily) label (OPEN-013) — dashboard.py
- [x] v5.32: GI market filter (OPEN-014) — global_intelligence.py, app.py
- [x] v5.32: Market LIVE badge (OPEN-015) — app.py
- [x] v5.32: GI cache coherence (OPEN-016) — global_intelligence.py
- [x] v5.32: R23b regression checks added — regression.py
- [x] GSI_AUDIT_TRAIL.md created — 48 findings, immutable log
- [x] GSI_WIP.md created (this file)
- [x] GSI_SPRINT.md created
- [x] GSI_DECISIONS.md created
- [x] GSI_DEPENDENCIES.md created
- [x] CLAUDE.md checkpoint protocol added
- [x] Regression baseline: 392/392

## Files Generated (in outputs/) — Commit Status

All files committed and pushed to GitHub as of 2026-03-29.

## Decisions Made This Session (not yet in GSI_DECISIONS.md)

None — all decisions from this session are recorded in GSI_DECISIONS.md.

## CHECKPOINT

```
No active checkpoint — session_010 complete.
Next session starts fresh.
```

---

## How to Use This File

### When starting a new session
1. Read this file first — before reading CLAUDE.md or session.json.
2. If `Status: IDLE` — proceed normally with new-session protocol.
3. If `Status: ACTIVE` — read the CHECKPOINT block and resume from there.
   Do NOT start fresh. Do NOT regenerate completed tasks.

### When Claude suspects it is running low on context
Claude writes a CHECKPOINT block here immediately:

```
## CHECKPOINT — [date] [session-id]

Status: ACTIVE (interrupted)
Currently working on: [exact task — file, function, what change]
Completed so far (safe to use from outputs/):
  - [file] ✓
  - [file] ✓
Not yet started:
  - [task]
  - [task]
Decisions made (add to GSI_DECISIONS.md):
  - [decision + reason]
Regression baseline at checkpoint: [N]/[N]
Git state: [committed / not committed — list uncommitted files]
Resume instruction: [one sentence telling next Claude exactly where to pick up]
```

### When session ends cleanly
Claude updates Status to IDLE, clears active tasks, moves them to Completed.

### Conflict prevention rules
- If this file shows `Status: ACTIVE`, do not start a new sprint until:
  (a) the checkpoint work is completed, or
  (b) the interrupted session's outputs are discarded and the WIP is reset.
- Never edit a CHECKPOINT block — add a new one below the old one.
- The most recent CHECKPOINT always wins.
