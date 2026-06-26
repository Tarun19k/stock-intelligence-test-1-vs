# AlphaVeda — Council Seat Rules
# Enforces zero-assumption tolerance for council dispatch.
# Last updated: 2026-06-26

## Rule A — Council Seat Dispatch Gate (ENFORCED)

Before dispatching any council seat as an agent, verify:
1. A `SKILL.md` exists at `~/.claude/skills/<seat-skill-name>/SKILL.md`
2. The seat is registered in `~/.claude/skills-index.md`

If either check fails, dispatch is BLOCKED. Create the skill and register it first.
A REVISE/APPROVE verdict from an unbacked seat is INADMISSIBLE and cannot count toward Phase sign-off.

**Seat → Skill registry (AlphaVeda council):**
| Persona name | Canonical skill name | SKILL.md exists |
|---|---|---|
| Buffett | panel-buffett | ✓ |
| Munger | panel-munger | ✓ |
| Dalio | panel-dalio | ✓ |
| Marks | panel-marks | ✓ |
| Soros | panel-soros | ✓ |
| Druckenmiller | panel-druckenmiller | ✓ |
| Lynch | panel-lynch | ✓ |
| Wealth & Revenue | doctrine-panel-wealth-revenue-strategist | ✓ |
| Constraint Enforcer | doctrine-panel-constraint-enforcer | ✓ |
| Shakuni | red-team | ✓ (alias) |
| Synthesis Chair | synthesis-chair | ✓ |
| UX/Accessibility (was Tanvi Rao) | ui-ux-pro-max | ✓ |
| SRA/Reliability Architect (was Imran) | doctrine-panel-systems-reliability-architect | ✓ |
| DB Integrity (was Rashida) | doctrine-panel-constraint-enforcer (DB ext) | ✓ (enhanced) |
| Calibration Integrity (was Reddy) | calibration-integrity | ✓ |
| Jhunjhunwala | ⚠ MISSING — create before next dispatch | ✗ |
| Bhattacharya | ⚠ MISSING — create before next dispatch | ✗ |
| Varghese | ⚠ MISSING — create before next dispatch | ✗ |

## Rule B — Skill Reference in Dispatch Prompt
Every council dispatch prompt must name its backing skill:
> "Apply the standard in `~/.claude/skills/<skill-name>/SKILL.md`"

A prompt describing seat behaviour inline without referencing the backing skill is a violation.

## Rule C — No Inline Seat Logic in Code
Scripts that invoke council seats (e.g. `scripts/council_review.py`) must not encode
seat review logic inline. Reference the skill file instead.
Known violation: `alphaveda/scripts/council_review.py` — must be refactored to delegate
to skills rather than encoding seat criteria as inline regex/functions.

## Verification hook
```bash
# Before dispatching a seat:
~/.claude/scripts/check-seat-skill.sh <seat-skill-name>
# Returns 0 = OK to dispatch, 1 = BLOCKED
```
