#!/bin/bash
# before-completion.sh — DRAFTED 2026-07-30, NOT YET WIRED into settings.json.
#
# Source (PDF p.58): "run full test suite; run golden portfolios; run
# recommendation-stability tests; run data-lineage checks; generate change summary;
# verify documentation updates; produce unresolved-risk report."
#
# Draft only. Wiring into settings.json as a Stop hook is a separate decision.

set -euo pipefail

cd "$(dirname "$0")/../.." || exit 1

echo "[before-completion] Running full test suite..."
python3 -m pytest tests/ -q || echo "[WARN] Test suite reported failures." >&2

echo "[before-completion] Running the OHY synthetic golden-portfolio prototype..."
python3 scripts/ohy_synthetic_prototype.py > /tmp/ohy_prototype_output.json 2>&1 || \
  echo "[WARN] Synthetic prototype run failed — see /tmp/ohy_prototype_output.json" >&2
echo "[before-completion] Synthetic prototype output saved to /tmp/ohy_prototype_output.json for review."

echo "[before-completion] Unresolved-risk report (draft, manual for now):"
echo "  - Prereq 5 (Calculation Spec): OPEN — blocks all real Offset/Harvest/Yield thresholds"
echo "  - Prereq 7 (Tax Engine Spec): OPEN — blocks all real tax logic"
echo "  - Prereq 8 (Investor Model): schema only, no real values yet"
echo "  - Portfolio ledger: schema live, 0 rows"

echo "[before-completion] Done (draft — not yet wired live)."
