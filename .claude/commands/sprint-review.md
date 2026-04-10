---
description: Review the current sprint's completed work and plan the next sprint from open items.
---

## Step 1 — Load context (targeted reads only)

Read **only the `meta` block and `open_items` array** from `GSI_session.json`. Do NOT read the full file (~42k tokens).
- Use `offset` to target the `open_items` section (starts around line 1086)
- Extract: `current_version`, `meta.last_session`, and all items in `open_items[]`

The canonical open items list is in `CLAUDE.md` — use it as the source of truth. GSI_session.json is used only to confirm `current_version` and `meta.last_session`.

Read `CLAUDE.md` Open Items section for the authoritative backlog (skip if already in context).

## Step 2 — Sprint retrospective

List all items completed in the most recent session:
- Version shipped + regression baseline (before → after)
- Fixes with their audit reference IDs
- QA verification status (brief passed / PLAYWRIGHT-ID passed / pending)

## Step 3 — Open items by priority

List all open items from CLAUDE.md, grouped:
- **P0 / HIGH** (fix in next sprint)
- **MEDIUM** (next 2 sprints)
- **LOW** (backlog)

For each P0/HIGH item include: ID, title, target version, estimated effort (Low/Medium/High based on scope).

Flag anti-patterns to avoid in sprint selection:
- More than 4 items in the risky lane (P0 regulatory + unknown API behavior)
- Any item with unresolved external dependency (e.g. waiting for CEO action)
- Batching code files that touch different modules (regression isolation risk)

## Step 4 — Proposed next sprint scope

Select the 5–7 most impactful HIGH items that:
- Can be batched logically (e.g., all SEBI compliance fixes together)
- Don't have unresolved dependencies
- Have clear pass criteria

Present as a table with columns:

| ID | Title | Files | Functions | Model | Mode | Est tokens | Pass criterion |
|---|---|---|---|---|---|---|---|

**Model column rules** (from docs/ai-ops/token-model-rules.md):
- `haiku` — single known file, ≤1 judgment call, no cross-file reasoning
- `sonnet` — multi-section edits, cross-file coherence, moderate judgment
- `opus` — novel algorithm, security audit, first-time subsystem design

**Mode column rules:**
- `sequential` — items with shared state or ordering dependencies
- `parallel_agent` — fully independent items (different files, no shared state)
- `worktree` — parallel + isolated git copy needed

## Step 5 — Governance check

For each proposed item, identify which of the 7 policies in GSI_GOVERNANCE.md it relates to. Flag any item that would require a new DO NOT UNDO rule.

Present the sprint plan as a table. Ask for confirmation before starting any work.
