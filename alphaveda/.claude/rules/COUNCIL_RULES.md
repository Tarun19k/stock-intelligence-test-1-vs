# AlphaVeda — Council Seat Rules
# Enforces zero-assumption tolerance for council dispatch.
# Last updated: 2026-08-17 (registry corrected — see note below)

## Rule A — Council Seat Dispatch Gate (ENFORCED)

Before dispatching any council seat as an agent, verify:
1. A `SKILL.md` exists at `~/.claude/skills/<seat-skill-name>/SKILL.md`
2. The seat is registered in `~/.claude/skills-index.md`

If either check fails, dispatch is BLOCKED. Create the skill and register it first.
A REVISE/APPROVE verdict from an unbacked seat is INADMISSIBLE and cannot count toward Phase sign-off.

**Canonical source of truth for seat status:** `alphaveda/.claude/skills-index.md` (git-tracked —
this table below is a convenience mirror and can go stale; if the two disagree, skills-index.md
wins). 2026-08-17 correction: this table previously marked all 18 seats "✓" unconditionally — a
fresh Claude Code on the web workspace found none of the 18 `SKILL.md` files actually present
under `~/.claude/skills/` (that directory doesn't persist across remote-workspace containers), so
the "✓" was describing the *design*, not verified runtime state. Don't repeat that mistake — a
"✓" here means a real, checked-in `SKILL.md` exists at `alphaveda/.claude/skills/<name>/SKILL.md`
(git-durable) and is mirrored to `~/.claude/skills/` by `.claude/hooks/session-start.sh` every
session, not that the seat "exists" as a design concept.

**Seat → Skill registry (AlphaVeda council):**
| Persona name | Canonical skill name | SKILL.md exists |
|---|---|---|
| Buffett | panel-buffett | ⬜ not yet rebuilt |
| Munger | panel-munger | ⬜ not yet rebuilt |
| Dalio | panel-dalio | ⬜ not yet rebuilt |
| Marks | panel-marks | ⬜ not yet rebuilt |
| Soros | panel-soros | ⬜ not yet rebuilt |
| Druckenmiller | panel-druckenmiller | ⬜ not yet rebuilt |
| Lynch | panel-lynch | ⬜ not yet rebuilt |
| Wealth & Revenue | doctrine-panel-wealth-revenue-strategist | ⬜ not yet rebuilt |
| Constraint Enforcer | doctrine-panel-constraint-enforcer | ⬜ not yet rebuilt |
| Shakuni | red-team | ⬜ not yet rebuilt |
| Synthesis Chair | synthesis-chair | ⬜ not yet rebuilt |
| UX/Accessibility (was Tanvi Rao) | ui-ux-pro-max | ⬜ not yet rebuilt |
| SRA/Reliability Architect (was Imran) | doctrine-panel-systems-reliability-architect | ⬜ not yet rebuilt |
| DB Integrity (was Rashida) | doctrine-panel-constraint-enforcer (DB ext) | ⬜ not yet rebuilt |
| Calibration Integrity (was Reddy) | calibration-integrity | ✅ rebuilt 2026-08-17, PROVISIONAL |
| Jhunjhunwala | circuit-microstructure-reviewer | ⬜ not yet rebuilt |
| Bhattacharya | data-licence-compliance-reviewer | ⬜ not yet rebuilt |
| Varghese | sebi-compliance-reviewer | ✅ rebuilt 2026-08-17, PROVISIONAL |
| (orchestrator, not a Financial Council seat but same Rule A gate) | chief-of-staff | ✅ rebuilt 2026-08-17, PROVISIONAL — weakest evidence base of the 3, see its SKILL.md Provenance |

**PROVISIONAL** = reconstructed from this repo's own documentation and real historical verdicts
(`bridge/data/council/audit-log.jsonl`, `graphify-out/SESSION_RESUME.md`), self-tested to
reproduce those real recorded outcomes — not the original file. Treat verdicts from these 3 as
admissible for now, but Tarun should spot-check each skill's embedded self-test cases (and
replace with the original `SKILL.md` if it still exists on his own machine) before relying on them
for anything higher-stakes than what's already been through this reconstruction check.

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

## Rule E — Financial Council Consultation Gate (added 2026-07-30, standing rule — Tarun-mandated)

**Effective immediately, applies to all AlphaVeda work going forward, not just this session.**

Before any AlphaVeda decision is finalized that touches: a retail-facing screen or UI copy, signal
presentation or framing, portfolio-decision logic (Offset/Harvest/Yield engines, diagnostics,
metric definitions), or any G1/G2-class decision per `OFFSET_HARVEST_YIELD_FOUNDATION.md`'s
decision-class boundaries — the Financial Council must be consulted and its verdict logged before
that decision ships or is treated as final.

**Minimum required seats** (per Rule A's registry above — all already backed, no new skill needed):
- At least one investor-persona seat (Buffett, Munger, Dalio, Lynch, Marks, Soros, or Druckenmiller
  — pick based on relevance to the specific decision, not all seven every time)
- `sebi-compliance-reviewer` (Varghese) — mandatory whenever the decision touches retail-facing
  output, regardless of which investor seat also runs
- `calibration-integrity` (Reddy) — mandatory whenever the decision touches a displayed metric,
  score, or confidence claim

**What this gates:** new screens (Screens 2/3/5-9 per the source blueprint), any change to how
Offset/Harvest/Yield outputs are framed, any new metric added to the diagnostic dictionary, any
copy change on an existing shipped page that alters what a retail user is told. **Does not gate**:
internal engineering scaffolding (repo restructuring, ADRs, hooks, subagent definitions, synthetic
test fixtures with no retail-facing surface) — those follow the ordinary premortem/External State
Write Gate rules already in force, not this one.

**Enforcement mechanism:** same as Rule A — no mechanical hook exists to block this (Agent-tool
dispatches aren't observable by hooks, same honest limitation already documented in global
`chief-of-staff/SKILL.md`'s Council Engagement Logging section). This is a discipline requirement,
verified by checking `bridge/data/council/audit-log.jsonl` for a matching entry before treating any
gated decision as shippable — the same Claim Verification Gate pattern used elsewhere in this
system. A gated decision with no matching audit-log entry has not actually cleared this gate,
regardless of how confident the implementation looks.

**Bypass:** Tarun may say "skip financial council for [specific decision] this session" — valid for
that item only, never persisted, logged as a bypass in the session record same as the global Layer
1 Council Gate's bypass mechanism.

## Verification hook
```bash
# Before dispatching a seat:
~/.claude/scripts/check-seat-skill.sh <seat-skill-name>
# Returns 0 = OK to dispatch, 1 = BLOCKED
```
