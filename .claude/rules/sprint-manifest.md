---
paths:
  - "GSI_SPRINT_MANIFEST.json"
---

# Scoped Rules — GSI_SPRINT_MANIFEST.json

These rules activate automatically when editing `GSI_SPRINT_MANIFEST.json`.

## Mandatory fields per item

Every non-section item that is NOT status=DONE must have:
- `model` ∈ {haiku, sonnet, opus} — model selection rationale must be specified in `model_rationale`
- `mode` ∈ {sequential, parallel_agent, worktree}
- `playwright` — either `"PLAYWRIGHT-NN: Navigate … Assert … Edge cases: …"` (for items touching .py files) or `"N/A — <reason>"` (for doc-only items)
- `est_tokens` — estimated token range (e.g. "8k–12k")

R30 blocks commits when model/mode fields are missing or invalid during IN_PROGRESS status.
R31 blocks sprint COMPLETE if PLAYWRIGHT-IDs are not in GSI_QA_STANDARDS.md.

## Status transitions

| From | To | Required actions |
|---|---|---|
| PLANNING | IN_PROGRESS | Set sprint open; notify R27/R28/R30/R31/R32 now active |
| IN_PROGRESS | COMPLETE | Run full sprint close protocol (CLAUDE.md Rule 2 sprint close steps) |
| Any | COMPLETE | R32 requires GSI_SESSION_LEARNINGS.md RECORD dated ≥ manifest `created` |

## file_change_log discipline

Before committing any file during an active sprint:
1. Check if the file is already in `file_change_log`
2. If NOT listed: add an entry with `doc_updates_required` or `no_doc_update_reason`
3. R27 fails if committed file is absent from the log

## token_budget discipline

Fill the `token_budget` block BEFORE implementation. Reference costs:
- Sequential item: ~8–12k · Parallel agent item: ~20–25k
- Regression run: ~3k · sync_docs: ~2k · Large file read: ~4k

See docs/ai-ops/token-model-rules.md for model selection and execution mode rules.
