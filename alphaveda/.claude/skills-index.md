# Claude Skills Index — this workspace

Registry of skills backing AlphaVeda's Financial Council (`alphaveda/.claude/rules/COUNCIL_RULES.md`
Rule A). Single source of truth for seat → skill mapping — COUNCIL_RULES.md's own table must mirror
this file, not duplicate it independently. If the two ever disagree, this file wins; update
COUNCIL_RULES.md to match.

**Canonical source:** these SKILL.md files are git-tracked at `alphaveda/.claude/skills/<name>/SKILL.md`
in the `stock-intelligence-test-1-vs` repo. The copies under `~/.claude/skills/<name>/SKILL.md` (the
path Rule A's dispatch-gate check reads) are a runtime mirror — durable via git, not via this
container's home directory, which is ephemeral in Claude Code on the web / remote workspaces. A
SessionStart hook should sync repo → `~/.claude/skills/` at the top of every session once the
hook-install permission blocker (see workspace catch-up thread, 2026-08-17) is cleared; until then,
mirror manually at session start: `cp -r alphaveda/.claude/skills/* ~/.claude/skills/`.

## Seat → Skill registry

| Persona | Canonical skill name | Status | Backing doc(s) used to (re)build |
|---|---|---|---|
| Varghese (SEBI) | `sebi-compliance-reviewer` | ✅ rebuilt 2026-08-17 | `alphaveda/.claude/rules/SEBI_COMPLIANCE.md`, audit-log entries #3/#4 |
| Reddy (Calibration Integrity) | `calibration-integrity` | ✅ rebuilt 2026-08-17 | audit-log entries #1/#4, `SESSION_RESUME.md` OHY materiality loop |
| Krishna (orchestrator) | `chief-of-staff` | ✅ rebuilt 2026-08-17 | `docs/BACKGROUND_BRIEFING.md`, `docs/trimurti/shiva-gates.md`, `SESSION_RESUME.md` |
| Buffett | `panel-buffett` | ⬜ not yet rebuilt | — |
| Munger | `panel-munger` | ⬜ not yet rebuilt | — |
| Dalio | `panel-dalio` | ⬜ not yet rebuilt | — |
| Marks | `panel-marks` | ⬜ not yet rebuilt | — |
| Soros | `panel-soros` | ⬜ not yet rebuilt | — |
| Druckenmiller | `panel-druckenmiller` | ⬜ not yet rebuilt | — |
| Lynch | `panel-lynch` | ⬜ not yet rebuilt | — |
| Wealth & Revenue Strategist | `doctrine-panel-wealth-revenue-strategist` | ⬜ not yet rebuilt | — |
| Constraint Enforcer | `doctrine-panel-constraint-enforcer` | ⬜ not yet rebuilt | — |
| SRA / Reliability Architect | `doctrine-panel-systems-reliability-architect` | ⬜ not yet rebuilt | — |
| Shakuni | `red-team` | ⬜ not yet rebuilt | — |
| Synthesis Chair | `synthesis-chair` | ⬜ not yet rebuilt | — |
| UX/Accessibility (was Tanvi Rao) | `ui-ux-pro-max` | ⬜ not yet rebuilt | — |
| Jhunjhunwala | `circuit-microstructure-reviewer` | ⬜ not yet rebuilt | — |
| Bhattacharya | `data-licence-compliance-reviewer` | ⬜ not yet rebuilt | — |

**Legend:** ✅ rebuilt and self-tested against real historical verdicts, PROVISIONAL until Tarun
spot-checks · ⬜ still missing — dispatch remains BLOCKED under Rule A until rebuilt.

## Verification

`~/.claude/scripts/check-seat-skill.sh <seat-skill-name>` — exit 0 if the skill exists and is
non-empty, exit 1 otherwise. Run before any council dispatch, per Rule A.
