#!/usr/bin/env bash
# pre_commit.sh — PreToolUse hook: regression gate on git commit
#
# Fires when Claude Code calls Bash with a command matching "git commit".
# Reads tool input JSON from stdin. Extracts tool_input.command.
# Deduplicates: skips regression if run_state.json shows PASS for current HEAD.
# Exit 2 blocks the tool call. Exit 0 allows it.
#
# ADR-020: exit 2 (not 1) to block; git rev-parse --show-toplevel for repo root
#          (replaces $CLAUDE_PROJECT_DIR — unreliable across execution contexts);
#          Python stdin parse (jq not installed on all systems).

set -euo pipefail

REPO=$(git rev-parse --show-toplevel)
RUN_STATE="$REPO/.claude/run_state.json"

# --- Parse stdin JSON to get the command being attempted ---
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('tool_input', {}).get('command', ''))
" 2>/dev/null || echo "")

# Only gate on actual git commit calls
if [[ "$COMMAND" != *"git commit"* ]]; then
    exit 0
fi

# --- File-type gate: skip regression for doc-only commits ---
# Only .py changes can break the regression suite. .md/.json/.yaml/.sh/.html/.css
# commits will not affect Python behaviour — skip the 3k-token regression run.
STAGED_PY=$(git -C "$REPO" diff --cached --name-only 2>/dev/null | grep '\.py$' | wc -l | tr -d ' ')
if [ "$STAGED_PY" -eq 0 ]; then
    echo "[pre_commit] No Python files staged — doc-only commit, skipping regression."
    exit 0
fi

# --- Deduplication: skip if last regression passed at current HEAD ---
CURRENT_HEAD=$(git -C "$REPO" rev-parse HEAD 2>/dev/null || echo "unknown")

if [ -f "$RUN_STATE" ]; then
    CACHED=$(python3 -c "
import json, sys
try:
    d = json.load(open('$RUN_STATE'))
    print(d.get('result','') + '|' + d.get('hash',''))
except:
    print('MISS|none')
" 2>/dev/null || echo "MISS|none")
    if [[ "$CACHED" == "PASS|$CURRENT_HEAD" ]]; then
        exit 0
    fi
fi

# --- Run regression ---
echo "[pre_commit] Running regression suite..."
cd "$REPO"
if python3 regression.py; then
    # Write run_state.json (dedup cache)
    python3 -c "
import json
json.dump({'result': 'PASS', 'hash': '$CURRENT_HEAD'}, open('$RUN_STATE', 'w'))
"
    exit 0
else
    echo "[pre_commit] BLOCKED: regression failures must be fixed before committing."
    exit 2
fi
