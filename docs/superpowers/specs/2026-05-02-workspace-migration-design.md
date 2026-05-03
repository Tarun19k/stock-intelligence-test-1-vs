# Workspace Migration Design — Enhanced Claude Code Environment into GSI Dashboard
**Date:** 2026-05-02  
**Author:** Tarun Kochhar  
**Status:** APPROVED — pending implementation plan  
**Scope:** Migrate skills, hooks, slash commands, global config, and token optimization methodology from `agentic-operations` repo into the GSI Dashboard Claude Code workspace at `/Users/home/Agentic Tools - Projects/stock-intelligence-test-1-vs`

---

## 1. What We Are Building

A controlled, approval-gated file migration process that:

1. Installs global Claude Code capabilities (skills, commands, CLAUDE.md) from `agentic-operations/global-config/` into `~/.claude/` — affecting all workspaces
2. Installs project-level capabilities into `.claude/` within the GSI Dashboard repo — affecting only this workspace
3. Maintains a permanent migration audit trail in `agentic-operations/` so this process becomes part of centralised operations
4. Never writes a file without: (a) showing the full content/diff to Tarun, (b) receiving explicit approval, (c) writing a snapshot/rollback point

---

## 2. Source and Destination Map

| Incoming File | Destination | Notes |
|---|---|---|
| `global-config/CLAUDE.md` (adapted) | `~/.claude/CLAUDE.md` | Paths adapted: `/Users/tarunkochhar/` → `/Users/home/`. Merge Status section content updated to reflect this device's actual state. |
| `global-config/skills/token-tracker/` | `~/.claude/skills/token-tracker/` | SKILL.md enhanced with `model: haiku` frontmatter during install |
| `global-config/skills/skill-design-guardrails/` | `~/.claude/skills/skill-design-guardrails/` | SKILL.md enhanced with `model: haiku` frontmatter during install |
| `global-config/commands/workspace-status.md` | `~/.claude/commands/workspace-status.md` | Genuinely new — no conflict |
| Migration registry files (new) | `agentic-operations/MIGRATION_REGISTRY.md` + `migration-state.json` | Created during Phase 0 |
| Snapshot infrastructure (new) | `agentic-operations/backups/snapshots/` | Created during Phase 0; `.gitignore` amended first |

**Requires correction before install:**

| File | Issue | Resolution |
|---|---|---|
| `global-config/bootstrap.sh` | All paths hardcoded to `/Users/tarunkochhar/` | Adapt to `/Users/home/` throughout; store corrected version back in `agentic-operations/global-config/` as a valid future-use script |
| `global-config/commands/new-session.md` | Incoming (84 lines) may be less advanced than existing GSI (106 lines) | Diff both → merge: keep GSI's advanced content, pull in any new sections from incoming → write combined version |
| `global-config/commands/close-session.md` | Same risk — size not yet confirmed | Same: diff → merge |
| `global-config/commands/log-learnings.md` | Same risk — size not yet confirmed | Same: diff → merge |
| `global-config/statusline-command.sh` | Conflicts with active claude-hud plugin in `~/.claude/settings.json` | Decision gate: (a) keep in source repo only (no action), or (b) install to `~/.claude/` without activating. Switching statusline is a separate explicit decision — not part of this migration |
| `global-config/settings-template.json` | Reference-only by design | No action — correct as-is |

---

## 3. Approval Gate Protocol

Every file write follows this sequence without exception:

```
SHOW     → Present full content (for new files) or unified diff (for modifications)
ASSESS   → State: destination path, model used, rationale, risk level, reversibility
WAIT     → Do not proceed until Tarun confirms with explicit approval ("proceed", "yes", "approved")
SNAPSHOT → Write pre-change snapshot to agentic-operations/backups/snapshots/ (named: YYYY-MM-DD-HH-MM-<target-path-slug>.md)
WRITE    → Execute the file write
CONFIRM  → Re-read the written file; verify content matches intent
LOG      → Append entry to MIGRATION_REGISTRY.md and update migration-state.json
```

**First-write exception (Phase 0 only):** Snapshot infrastructure itself is written before the snapshot gate exists. This is the only time the SNAPSHOT step is skipped. The exception is documented explicitly in the MIGRATION_REGISTRY.md Phase 0 entry with reason: "bootstrap — snapshot gate being established."

---

## 4. Migration Registry Schema

### MIGRATION_REGISTRY.md structure
Append-only markdown log at `agentic-operations/MIGRATION_REGISTRY.md`. Each entry:

```markdown
## [YYYY-MM-DD HH:MM] — <file-slug>
- **Action:** create | modify | skip | delete
- **Source:** <relative path in agentic-operations/>
- **Destination:** <absolute path on this device>
- **Status:** pending | in_progress | completed | failed
- **Rationale:** <one sentence>
- **Snapshot:** <path to pre-change snapshot, or "bootstrap-exception">
- **Reversibility:** <how to undo>
- **Approved by:** Tarun (explicit confirmation in session)
```

### migration-state.json schema
```json
{
  "schema_version": "1",
  "device": "home",
  "session_opened": "YYYY-MM-DD",
  "session_closed": null,
  "phase": "0 | 1 | 2 | 3 | 4",
  "items": [
    {
      "id": "item-slug",
      "status": "pending | in_progress | completed | failed",
      "destination": "/absolute/path",
      "action": "create | modify | skip | delete",
      "snapshot_path": "relative/path/or/bootstrap-exception",
      "completed_at": null
    }
  ]
}
```

**Status lifecycle:**
```
pending → in_progress → completed
                     ↘ failed
```

`in_progress` is mandatory. If a session ends with any item `in_progress`, next session must treat it as `failed` and restart from the SHOW step for that item. Never assume a write completed if status was not updated to `completed` in the same session.

### workspace-sync boundary
`workspace-sync` skill manages the operational file registry for ongoing workspace state. The migration registry is a one-time audit trail. They do not merge. After migration completes, workspace-sync takes over ongoing sync responsibility.

---

## 5. Path Adaptation Rules

Before writing any file from `global-config/` to its destination, apply these substitutions:

| From | To | Files affected |
|---|---|---|
| `/Users/tarunkochhar/` | `/Users/home/` | `global-config/CLAUDE.md` (lines 10, 12), `backups/manifest.json` |
| Stale "Merge Status: in progress — 24 actions" | Section body rewritten: list F3/F4/G3 as DONE on this device, note remaining Phase 4 items as deferred | `global-config/CLAUDE.md` Merge Status section |
| `(no model: frontmatter)` | `model: haiku` added in frontmatter block | `token-tracker/SKILL.md`, `skill-design-guardrails/SKILL.md` |

---

## 6. Skills Enhancement Specification

Both incoming skills ship without `model:` frontmatter. During installation, the following frontmatter block is added to each SKILL.md before writing:

```yaml
---
name: <existing-name>
description: <existing-description>
model: haiku
---
```

**Rationale:** Both skills perform mechanical, well-defined tasks (cost attribution, checklist review) with under 100 lines of output and no cross-file reasoning. Haiku is the correct tier. Not adding frontmatter means Claude uses the session default (Sonnet), burning 3–4× more tokens per invocation on routine checklist tasks.

---

## 7. Commands Install Rules

| Command | Action | Reason |
|---|---|---|
| `workspace-status.md` | Install as new → `~/.claude/commands/workspace-status.md` | Does not exist globally or at project level |
| `new-session.md` | Diff → merge → install combined version | Incoming (84 lines) < existing GSI (106 lines); merge preserves GSI's advanced content |
| `close-session.md` | Diff → merge → install combined version | Size comparison pending; same merge approach |
| `log-learnings.md` | Diff → merge → install combined version | Size comparison pending; same merge approach |

All merges go through the full approval gate — combined content is shown to Tarun before any write.

---

## 8. Pre-Conditions (must be satisfied before Phase 1 begins)

1. `backups/snapshots/` added to `agentic-operations/.gitignore` — prevents snapshot artifacts from being committed
2. `agentic-operations/MIGRATION_REGISTRY.md` created (Phase 0)
3. `agentic-operations/migration-state.json` created (Phase 0)
4. `agentic-operations/backups/snapshots/` directory structure confirmed

---

## 9. Migration Phases

### Phase 0 — Snapshot Infrastructure (prerequisite)
- Amend `.gitignore`
- Create `MIGRATION_REGISTRY.md` with bootstrap entry
- Create `migration-state.json` in initial state
- Confirm `backups/snapshots/` directory exists

### Phase 1 — Global Config (`~/.claude/`)
Items in dependency order:
1. `~/.claude/CLAUDE.md` — adapted global rules (path-corrected)
2. `~/.claude/skills/token-tracker/SKILL.md` — enhanced with model frontmatter
3. `~/.claude/skills/token-tracker/token-model-rules.md` — unified tier rules
4. `~/.claude/skills/skill-design-guardrails/SKILL.md` — enhanced with model frontmatter
5. `~/.claude/commands/workspace-status.md` — new command

### Phase 2 — Commands Merge + Corrections
- Correct `bootstrap.sh` paths (`/Users/tarunkochhar/` → `/Users/home/`) and write back to source
- Diff `new-session.md`, `close-session.md`, `log-learnings.md` — produce merged version per file
- Statusline decision gate: keep in source only vs install dormant
- All merges follow full approval gate (SHOW merged content → WAIT → SNAPSHOT → WRITE)

### Phase 3 — Registry and Ops Integration
- Update `agentic-operations/WORKSPACE_MERGE_ACTION_PLAN.md` — mark this-device items as DONE
- Update `agentic-operations/.claude/registry.json` — fix memory path
- Final migration-state.json close (session_closed, all statuses = completed)

### Phase 4 — Strategic Items (deferred — scope to be defined)
Items S1–S5 from WORKSPACE_MERGE_ACTION_PLAN.md. Scope TBD by Tarun before this phase begins. Not blocking Phases 0–3.

---

## 10. Model Routing for Migration Tasks

| Activity | Model | Rationale |
|---|---|---|
| Reading and diffing files | Haiku | Mechanical comparison, no judgment |
| Writing adapted CLAUDE.md | Sonnet | Cross-file path adaptation + semantic correctness judgment |
| Writing skills with frontmatter enhancement | Haiku | Template addition to known pattern |
| Writing new commands (workspace-status) | Haiku | Single file, no cross-file reasoning |
| Registry and state file writes | Haiku | Structured JSON/markdown, under 100 lines |
| Phase 4 scope definition | Sonnet | Architectural judgment required |

---

## 11. Rollback Protocol

For any `failed` item:
1. Read the snapshot file at `agentic-operations/backups/snapshots/<snapshot-path>`
2. If destination was a new file: delete it
3. If destination was a modified file: restore from snapshot content
4. Update migration-state.json: status → `failed`
5. Append failure entry to MIGRATION_REGISTRY.md with reason
6. Re-present to Tarun from SHOW step with failure context

For global `~/.claude/` files: snapshots capture the full pre-migration state. These files did not exist before migration, so rollback = deletion.

---

## 12. Success Criteria

Migration is complete when:
- All Phase 0–3 items have status `completed` in migration-state.json
- `~/.claude/CLAUDE.md` contains `/Users/home/` paths (not `/Users/tarunkochhar/`)
- Both installed skills have `model: haiku` in frontmatter
- `python3 regression.py` passes at same baseline (451/451) — migration touches no GSI code
- `python3 compliance_check.py` passes — migration touches no GSI source files
- `agentic-operations/MIGRATION_REGISTRY.md` has a complete entry for every action taken
- Phase 4 scope is documented even if deferred

---

## 13. Out of Scope

- Running `bootstrap.sh` (hardcoded wrong paths)
- Switching statusline from claude-hud to bash script
- Any changes to GSI app code, regression suite, or governance docs
- Merging workspace-sync skill with migration registry (boundary maintained)
- Phase 4 strategic items (deferred until scope defined)
