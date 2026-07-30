#!/bin/bash
# before-file-modification.sh — DRAFTED 2026-07-30, NOT YET WIRED into settings.json.
#
# Source (PDF p.58): "block changes to approved metric specifications; block changes to
# tax rules without an ADR; prevent direct edits to generated migration files; validate
# that the working branch is permitted."
#
# This script is a draft implementation, not yet live. Wiring it into
# alphaveda/.claude/settings.json as a PreToolUse hook is a separate decision requiring
# its own review — auto-executing hooks are real standing infrastructure, not something
# to enable silently alongside a documentation pass.
#
# Expected input: the file path being modified, via $CLAUDE_HOOK_FILE_PATH (or similar —
# exact env var name must be confirmed against current Claude Code hook API before wiring,
# per AGENTS.md's own warning that this Next.js/Claude Code version may differ from
# training-data assumptions).

set -euo pipefail

TARGET="${1:-}"
if [[ -z "$TARGET" ]]; then
  echo "before-file-modification.sh: no target file provided" >&2
  exit 0  # fail-open until this hook is actually wired and tested live
fi

# Block direct edits to generated Supabase migration files.
if [[ "$TARGET" == *"supabase/migrations/"* ]]; then
  echo "[BLOCKED] $TARGET is a migration file — create a new migration instead of editing an applied one." >&2
  exit 1
fi

# Block edits to metric specifications without a same-session ADR reference.
if [[ "$TARGET" == *"metric-dictionary"* || "$TARGET" == *"OFFSET_HARVEST_YIELD_FOUNDATION.md" ]]; then
  echo "[WARN] $TARGET touches metric/tax specification content." >&2
  echo "[WARN] Per source p.58: this requires an approved metric spec + a versioned ADR + new golden test cases + independent validation." >&2
  echo "[WARN] This draft hook does not yet verify an ADR exists — it only warns. Do not treat a warning-only pass as a real gate." >&2
fi

exit 0
