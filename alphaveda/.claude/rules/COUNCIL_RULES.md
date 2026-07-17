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
| Jhunjhunwala | circuit-microstructure-reviewer | ✓ (created 2026-06-26) |
| Bhattacharya | data-licence-compliance-reviewer | ✓ (created 2026-06-26) |
| Varghese | sebi-compliance-reviewer | ✓ (created 2026-06-26) |

## Rule B — Skill Reference in Dispatch Prompt
Every council dispatch prompt must name its backing skill:
> "Apply the standard in `~/.claude/skills/<skill-name>/SKILL.md`"

A prompt describing seat behaviour inline without referencing the backing skill is a violation.

## Rule C — No Inline Seat Logic in Code
Scripts that invoke council seats (e.g. `scripts/council_review.py`) must not encode
seat review logic inline. Reference the skill file instead.
Known violation: `alphaveda/scripts/council_review.py` — must be refactored to delegate
to skills rather than encoding seat criteria as inline regex/functions.

## Rule D — External State Write Gate (mirrored from global `~/.claude/CLAUDE.md`, 2026-07-17)
Source of truth is the global file — if the two ever disagree, global wins; update this
copy to match, don't edit them independently. Added after a `RemoteTrigger` write
silently dropped a routine's config (assumed "partial update" meant merge; it meant
whole-object replace). Applies to any tool call in this workspace that modifies live
external platform state — most relevantly, Task D's ingest-scheduler work if it uses
`RemoteTrigger` or similar.

Write log / tools-seen registry: `~/.claude/logs/external-state-writes.log`

**Before any tool call that modifies live external platform/infrastructure state**
(RemoteTrigger, Supabase, Vercel, Notion, Slack, or similar):

1. **Semantics check, before classification:** if this tool has no prior entry in the
   write log, confirm its merge-vs-replace update semantics from docs or a dry read
   first — never assume from the tool's name or vendor. This determines which branch
   below applies.
2. **Classify and act:**
   - **Replace-object** (RemoteTrigger, Notion properties, Vercel settings, Supabase row
     `UPDATE`): GET current full state → DIFF (state what's changing, confirm what's
     not) → PRESERVE unchanged fields explicitly, but never round-trip masked/
     redacted/server-generated fields (`***` secrets, timestamps, version counters) →
     prefer the narrowest write available (field-level/PATCH/ETag) over full-object
     replace, to avoid clobbering a concurrent edit → VERIFY after.
   - **Append/event** (Slack send, Supabase INSERT, deploy triggers): no prior object —
     GET/DIFF/PRESERVE don't apply. VERIFY only.
   - **Irreversible-replace** (schema migrations, column drops/alters): highest blast
     radius, no field-level narrowing available. DIFF mandatory, plus an explicit
     go/no-go confirmation before executing.
3. **Log the write** to the file above (tool, object, fields changed, timestamp) —
   detection backstop, not prevention. No mechanical enforcement exists for this action
   class; a bounded time-to-detection is the accepted operating point.

## Verification hook
```bash
# Before dispatching a seat:
~/.claude/scripts/check-seat-skill.sh <seat-skill-name>
# Returns 0 = OK to dispatch, 1 = BLOCKED
```
