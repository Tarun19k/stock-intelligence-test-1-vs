#!/bin/bash
# after-code-modification.sh — DRAFTED 2026-07-30, NOT YET WIRED into settings.json.
#
# Source (PDF p.58): "run formatting and type checks; run affected unit tests; detect
# unreferenced financial constants; scan for hard-coded tax rates; verify schema
# generation; check secrets."
#
# Draft only. Wiring into settings.json as a PostToolUse hook is a separate decision.

set -euo pipefail

cd "$(dirname "$0")/../.." || exit 1

echo "[after-code-modification] Running tsc --noEmit..."
(cd web && npx tsc --noEmit) || echo "[WARN] tsc reported errors — review before continuing." >&2

echo "[after-code-modification] Scanning for hard-coded tax-rate-shaped numbers (draft heuristic, not exhaustive)..."
# Real Indian capital-gains rates as of common knowledge: 10%, 15%, 20%, 30% appearing
# next to words like "tax"/"ltcg"/"stcg" in newly-changed files is a real smell —
# this is a heuristic scan, not a certified tax-rule checker.
if command -v git >/dev/null 2>&1; then
  git diff --name-only HEAD 2>/dev/null | grep -E '\.(py|ts|tsx)$' | while read -r f; do
    if [[ -f "$f" ]] && grep -niE "(ltcg|stcg|tax_rate|capital_gains?_rate).*\b(10|15|20|30)\b" "$f" >/dev/null 2>&1; then
      echo "[WARN] $f contains a tax-rate-shaped literal near tax-related terms — verify this isn't a hardcoded rate that belongs in a versioned tax module (Prereq 7)." >&2
    fi
  done
fi

echo "[after-code-modification] Done (draft — not yet wired live)."
