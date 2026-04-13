---
description: GSI sprint execution monitor — register manifest items as tasks, track status, surface blockers, emit micro-reports, and brief CTO before parallel clusters. Invoke with /sprint-monitor init | status | complete <id> | cluster <H1|H2>.
---

# Sprint Monitor — GSI Dashboard

Manages task tracking for the active GSI sprint using Claude Code's Task tools and
GSI_SPRINT_MANIFEST.json as the source of truth.

> **Baseline note:** Manifest `regression_baseline_entering` may lag behind the actual
> running baseline. Always confirm with `python3 regression.py` — do not trust the
> manifest integer alone. As of session_025, the confirmed baseline is 436/436.

---

## Commands

| Command | When to use |
|---|---|
| `/sprint-monitor init` | Once at sprint start — register all pending items as Tasks |
| `/sprint-monitor status` | On demand — current task table + regression state |
| `/sprint-monitor complete <item-id>` | After CTO confirms regression passes for an item |
| `/sprint-monitor cluster <H1\|H2>` | Before dispatching a parallel worktree cluster |
| `/sprint-monitor blocker <item-id> <reason>` | When an item is stuck — log and surface to user |

---

## Step 1 — init (run once at sprint start, before first implementation item)

1. Read `GSI_SPRINT_MANIFEST.json` — extract all items where `status` ≠ `"DONE"` and entry has no `_section` key.
2. For each pending item, call **TaskCreate**:
   - `title`: `[item.id] — [item.title]`
   - `description`: `sub_sprint: [item.sub_sprint] | model: [item.model] | mode: [item.mode] | files: [item.files joined] | criterion: [item.pass_criterion]`
   - `status`: `pending`
3. Confirm task count matches pending manifest items. Report any mismatch.
4. Print sprint table:

```
Sprint: v5.37 | Status: IN_PROGRESS | Baseline: 436/436
─────────────────────────────────────────────────────────────────────
ID                   Sub    Model   Mode       Status     Files
prereq-claude-feat   prereq haiku   bg_agent   DONE       1
df01-open027         v5.37a haiku   sequential pending    pages/home.py
open-029             v5.37a haiku   sequential pending    pages/dashboard.py
open-022             v5.37a sonnet  sequential pending    pages/week_summary.py
open-028             v5.37a sonnet  sequential pending    pages/global_intelligence.py
df-03                v5.37b sonnet  sequential pending    pages/week_summary.py
df-08                v5.37b sonnet  sequential pending    pages/home.py
haiku-cluster-H1     v5.37b haiku   parallel   pending    4 files
haiku-cluster-H2     v5.37b haiku   parallel   pending    2 files
open-026             v5.37b haiku   sequential pending    CLAUDE.md + regression.py
─────────────────────────────────────────────────────────────────────
```

---

## Step 2 — status (on demand)

1. Call **TaskList** to get current task states.
2. Read `GSI_SPRINT_MANIFEST.json` to cross-reference manifest status.
3. Emit formatted table:

```
Sprint Monitor — [timestamp]
Regression: [last confirmed N/N] | Compliance: [PASS / not yet run]
─────────────────────────────────────────────────────────────────
item-id            | status      | regression | committed
df01-open027       | completed   | 436/436    | yes
open-029           | in_progress | —          | no
open-022           | pending     | —          | —
...
─────────────────────────────────────────────────────────────────
Next: [next pending item-id and its model/mode]
Blockers: [none | list]
```

---

## Step 3 — complete <item-id> (after CTO confirms regression passes)

1. Call **TaskUpdate** → status: `completed` for the given task.
2. Update manifest item status to `"DONE"` in `GSI_SPRINT_MANIFEST.json`.
3. Print micro-report:

```
✓ [item-id] COMPLETE
  Regression:  N/N PASS (delta: +N checks if regression.py was modified)
  Files:       [list of files changed]
  Git commit:  [PENDING — awaiting bash-git approval from user]
  Next item:   [next-item-id] | model: [model] | mode: [mode]
  Playwright:  [PLAYWRIGHT-NN pending at sprint close | N/A]
```

4. **Never** issue a git commit automatically. Always surface the commit as `PENDING` and wait for the user to approve the bash-git action explicitly.

---

## Step 4 — cluster <H1|H2> (before dispatching parallel worktree agents)

Print a cluster brief and wait for explicit user "proceed" before dispatching:

```
⚡ Cluster [H1|H2] — ready to dispatch [N] worktree agents

  Agent 1: [sub-item-id]
    Files:   [list]
    Changes: [bullet list from manifest sub_items[].changes]
    Model:   haiku

  Agent 2: [sub-item-id]
    Files:   [list]
    Changes: [bullet list]
    Model:   haiku

  Rule 8 reminder:
    ✗ Agents must NOT run git add / git commit / git push
    ✓ Agents write files only — CTO reviews diffs and commits
    ✓ One regression run by CTO after all agents close is sufficient

Awaiting: user confirmation to dispatch (/sprint-monitor proceed-cluster)
```

After user confirms, dispatch agents per `superpowers:dispatching-parallel-agents` skill.

---

## Step 5 — blocker <item-id> <reason>

1. Call **TaskUpdate** → status: `pending` (or `blocked` if supported) with note.
2. Surface to user immediately:

```
🚫 BLOCKER — [item-id]
  Reason: [reason]
  Impact: [which subsequent items depend on this file?]
  Options:
    A) Skip and continue with next independent item
    B) Fix blocker inline (describe fix needed)
    C) Defer to next session (update WIP.md checkpoint)
```

---

## Sprint close trigger

When all tasks show `completed`:

```
🏁 All [N] sprint items complete. Sprint close sequence:
   Step 0a: /log-learnings  (R32 requires RECORD in GSI_SESSION_LEARNINGS.md)
   Step 1:  python3 sync_docs.py
   Step 2:  python3 regression.py → confirm [N] PASS
   Step 2a: /ui-test → run PLAYWRIGHT-01 through PLAYWRIGHT-06
   Step 3:  Update GSI_SPRINT_MANIFEST.json status → COMPLETE, archive to docs/sprint_archive/
   Step 4:  Set GSI_WIP.md Status → IDLE
```

---

## GSI-specific constraints

- **bash-git is not pre-approved** — every commit requires explicit user approval. Always surface as `PENDING` in micro-reports.
- **Playwright tests** (PLAYWRIGHT-01 to PLAYWRIGHT-06) are sprint-close only — do not run mid-sprint.
- **Parallel clusters** always require an explicit CTO "proceed" acknowledgement — never auto-dispatch.
- **Regression baseline**: Actual = 436/436. Manifest `regression_baseline_entering: 434` is stale (written session_022 before v5.35.1 governance patches). Expected exit: 437 (436 + 1 for open-026 R8 addition).
- **Manifest status**: Update item `status` fields in `GSI_SPRINT_MANIFEST.json` as work progresses — R27 reads this file.
