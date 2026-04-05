#!/usr/bin/env bash
# pre_push.sh — PreToolUse hook: compliance gate on git push
#
# Fires when Claude Code calls Bash with a command matching "git push".
# Reads tool input JSON from stdin. Extracts tool_input.command.
# Calls compliance_check.py; exit 2 blocks the push on any failure.
# Exit 0 allows the push when all compliance checks pass.
#
# ADR-020: exit 2 (not 1) to block; $CLAUDE_PROJECT_DIR for portability;
#          Python stdin parse (jq not installed on all systems).

: "${CLAUDE_PROJECT_DIR:?CLAUDE_PROJECT_DIR is not set — hook cannot run}"

set -euo pipefail

REPO="$CLAUDE_PROJECT_DIR"

# --- Parse stdin JSON to get the command being attempted ---
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('tool_input', {}).get('command', ''))
" 2>/dev/null || echo "")

# Only gate on actual git push calls
if [[ "$COMMAND" != *"git push"* ]]; then
    exit 0
fi

# --- Run compliance checks ---
echo "[pre_push] Running compliance checks..."
cd "$REPO"
if python3 compliance_check.py; then
    exit 0
else
    echo "[pre_push] BLOCKED: compliance failures must be fixed before pushing."
    exit 2
fi
