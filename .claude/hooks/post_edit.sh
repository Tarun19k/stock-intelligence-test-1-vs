#!/usr/bin/env bash
# post_edit.sh — PostToolUse hook: doc audit on *.md file writes/edits
#
# Fires after Claude Code calls Write or Edit on a file.
# Reads tool input JSON from stdin. Extracts tool_input.file_path.
# Filters for *.md files only — other files are silently ignored.
# Calls sync_docs.py --check for doc coherence audit.
# On clean pass: outputs {"suppressOutput": true} to suppress noise.
# On issues: prints output (PostToolUse cannot block — always exits 0).
#
# ADR-020: PostToolUse cannot block; suppressOutput on clean pass.

set -uo pipefail

REPO=$(git rev-parse --show-toplevel)

# --- Parse stdin JSON to get the file path ---
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('tool_input', {}).get('file_path', ''))
" 2>/dev/null || echo "")

# Only run on *.md files
if [[ "$FILE_PATH" != *.md ]]; then
    echo '{"suppressOutput": true}'
    exit 0
fi

# --- Run doc audit ---
# Use `if` to capture exit code without triggering set -e on non-zero exit.
cd "$REPO"
if OUTPUT=$(python3 sync_docs.py --check 2>&1); then
    # Clean pass — suppress output to avoid cluttering the conversation
    echo '{"suppressOutput": true}'
else
    # Issues found — print for developer awareness
    echo "[post_edit] Doc audit found issues after editing $FILE_PATH:"
    echo "$OUTPUT"
fi

# PostToolUse cannot block — always exit 0
exit 0
