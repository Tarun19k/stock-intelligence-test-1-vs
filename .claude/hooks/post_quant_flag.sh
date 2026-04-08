#!/usr/bin/env bash
# post_quant_flag.sh — PostToolUse hook: quant audit pending flag
#
# Fires after Claude Code calls Write or Edit on a file.
# Detects edits to quant-critical files: indicators.py, forecast.py,
# portfolio.py, market_data.py.
# Writes .claude/quant_audit_pending.json with triggered domains.
# new-session and quant-reviewer read this flag at session start.
#
# Domain mapping:
#   indicators.py  → D1 (Indicator Math) + D2 (Signal Logic)
#   forecast.py    → D4 (Forecast Calibration)
#   portfolio.py   → D5 (Portfolio Math)
#   market_data.py → D3 (Fundamental Data spot-check)
#
# PostToolUse cannot block — always exits 0.
# On non-quant file: outputs {"suppressOutput": true} silently.

set -uo pipefail

REPO=$(git rev-parse --show-toplevel)
FLAG="$REPO/.claude/quant_audit_pending.json"

# --- Parse stdin JSON to get the file path ---
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('tool_input', {}).get('file_path', ''))
" 2>/dev/null || echo "")

BASENAME=$(basename "$FILE_PATH")

# --- Map file to triggered domains ---
case "$BASENAME" in
    indicators.py)
        DOMAINS='["D1", "D2"]'
        LABEL="D1 (Indicator Math) + D2 (Signal Logic)"
        ;;
    forecast.py)
        DOMAINS='["D4"]'
        LABEL="D4 (Forecast Calibration)"
        ;;
    portfolio.py)
        DOMAINS='["D5"]'
        LABEL="D5 (Portfolio Math)"
        ;;
    market_data.py)
        DOMAINS='["D3"]'
        LABEL="D3 (Fundamental Data)"
        ;;
    *)
        # Not a quant-critical file — suppress output
        echo '{"suppressOutput": true}'
        exit 0
        ;;
esac

# --- Write the pending flag (merge with any existing pending domains) ---
DATE=$(date +%Y-%m-%d)

python3 - <<PYEOF
import json, os

flag_path = "$FLAG"
existing = {}
if os.path.exists(flag_path):
    try:
        existing = json.load(open(flag_path))
    except Exception:
        pass

# Merge new domains with any already-pending domains
existing_domains = existing.get("pending_domains", [])
new_domains = $DOMAINS
merged = sorted(set(existing_domains + new_domains))

record = {
    "pending": True,
    "pending_domains": merged,
    "last_triggered_by": "$BASENAME",
    "last_triggered_at": "$DATE",
    "last_full_audit": existing.get("last_full_audit", None)
}
json.dump(record, open(flag_path, "w"), indent=2)
print(record)
PYEOF

echo ""
echo "[quant_flag] ⚠️  Quant audit flagged: $BASENAME edited → $LABEL pending."
echo "[quant_flag] Run /quant-reviewer to run the audit and clear this flag."

exit 0
