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
Status:        ACTIVE
Session ID:    session_013
Version:       v5.34
Last updated:  2026-03-31
Sprint:        v5.34 IN PROGRESS
Manifest:      GSI_SPRINT_MANIFEST.json (IN_PROGRESS, 16 R27 checks)
```

## Active Tasks — v5.34 (update as each completes)

### Phase 0 — Infrastructure (session_013)
- [x] regression.py: R27 sprint manifest sync checks added
- [x] GSI_SPRINT_MANIFEST.json: manifest created (16 checks: 4 Tier A + 10 Tier B v5.33 + 2 Tier B infra)
- [x] CLAUDE.md: Rule 2 updated (manifest step), Rule 7 added (amendment workflow)
- [x] GSI_WIP.md: Status ACTIVE (this file — in progress)

### Phase 0 — Doc debt backfill (v5.33 misses)
- [x] GSI_AUDIT_TRAIL.md: 6 resolution records (H-02, D-07, D-09, G-02, G-05, EQA-38) + Section 4 regen
- [x] GSI_GOVERNANCE.md: Enforcement section Planned → Implemented (v5.33)
- [x] GSI_RISK_REGISTER.md: RISK-T09 Open → Mitigated
- [x] GSI_LOOPHOLE_LOG.md: Class 4 RISK-001 → Fixed (v5.33); 399 → 410
- [x] version.py: Add missing v5.31 entry
- [x] GSI_CONTEXT.md: Remove incorrectly added OPEN-001; close OPEN-001/OPEN-005

### Phase 1 — Observability dashboard (prerequisites for UX items)
- [x] market_data.py: instrumentation (rate-limit getter, hit/miss counters, error counter, fetch latency)
- [x] pages/observability.py: new founder-only page (App Health + Program tabs)
- [x] regression.py: R26 observability checks (syntax + instrumentation contracts)

### Phase 2 — UX items (after Phase 1 complete + passing)
- [x] D-05: Week Summary loading indicator on Dashboard navigation
- [x] G-03/F-10: Impact chain overflow fix at 1280px
- [x] F-14: West Asia content attribution

### Phase 3 — Sprint close
- [ ] version.py: v5.34 VERSION_LOG entry
- [ ] CLAUDE.md: Current State updated to v5.34
- [ ] GSI_CONTEXT.md: header updated to v5.34
- [ ] GSI_SPRINT.md: v5.34 moved to Done
- [ ] GSI_SPRINT_MANIFEST.json: status → COMPLETE, archive to docs/sprint_archive/
- [ ] GSI_WIP.md: Status → IDLE

## Completed This Session (session_012 — v5.33)

- [x] GSI_LOOPHOLE_LOG.md created — 6-class automation loophole registry
- [x] regression.py R10b: GSI_LOOPHOLE_LOG.md added (399→400)
- [x] regression.py R25: 6 policy enforcement checks added (400→410)
- [x] market_data.py: safe_ticker_key() gate (RISK-003)
- [x] indicators.py: Elder labels → plain English (D-07)
- [x] config.py: GI topics 2→5 (G-02)
- [x] global_intelligence.py: G-05 + P0 compliance + RISK-001 XSS + 48h gate
- [x] home.py: H-02 loading states + RISK-001 XSS
- [x] dashboard.py: D-09 correction factor disclosure
- [x] dashboard.py: P0 compliance gaps (SEBI, algo disclosure, "no red flags" fallback)
- [x] version.py: v5.33 entry added
- [x] CLAUDE.md: baseline 400→410, Current State updated to v5.33
- [x] GSI_COMPLIANCE_CHECKLIST.md: 400→410
- [x] .github/PULL_REQUEST_TEMPLATE.md: 400→410
- [x] GSI_WIP.md: Status IDLE, all tasks ticked
- [x] GSI_SPRINT.md: v5.33 moved to Done, velocity updated

## Previously Completed (session_010 — v5.32)

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
