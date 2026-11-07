#!/usr/bin/env bash
# check-seat-skill.sh — Council Rule A dispatch gate.
# Usage: check-seat-skill.sh <seat-skill-name>
# Exit 0 = OK to dispatch (SKILL.md exists and is non-empty).
# Exit 1 = BLOCKED (missing or empty) — create/register the skill first.
#
# Mechanical, deterministic: this is a plain existence + non-empty check,
# nothing more. It does not evaluate skill quality — that's the job of the
# self-test cases inside each SKILL.md, checked separately by a human.

set -euo pipefail

if [ $# -ne 1 ]; then
  echo "usage: check-seat-skill.sh <seat-skill-name>" >&2
  exit 2
fi

SEAT="$1"
SKILL_FILE="$HOME/.claude/skills/$SEAT/SKILL.md"

if [ ! -s "$SKILL_FILE" ]; then
  echo "BLOCKED: $SKILL_FILE missing or empty — seat '$SEAT' cannot be dispatched (Rule A)." >&2
  exit 1
fi

echo "OK: $SKILL_FILE present — seat '$SEAT' cleared for dispatch."
exit 0
