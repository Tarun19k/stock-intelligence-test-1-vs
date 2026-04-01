# /log-learnings — Append session learnings to GSI_SESSION_LEARNINGS.md

## Purpose
Run this at the end of every session as part of the Phase 3 close protocol.
Captures what was learned, what was stale, and any near-miss confusions.
Feeds the deviation/hallucination detection system.

## When to run
- Phase 3, step 1 (before version.py entry, before commit)
- Any time stale information or a confusion is discovered mid-session

## What to write

For EACH finding from this session, append a record to `GSI_SESSION_LEARNINGS.md`
using this format:

```
## RECORD-[NNN] | [YYYY-MM-DD] | [session_NNN] | [vX.XX] | [TYPE]
**Finding:** [what was wrong/learned/nearly wrong — one paragraph]
**Source:** [file, command, or interaction that surfaced it]
**Impact:** LOW | MEDIUM | HIGH
**Fix applied:** [exact change made, or "documented only — fix pending session_NNN"]
```

Record types:
- LEARNING: new understanding not in any existing doc
- STALE: a context file (CLAUDE.md, GSI_CONTEXT.md, session.json, etc.) contained
  outdated information
- CONFUSION: Claude misread or misapplied something (near-miss)
- HALLUCINATION: Claude generated a fact not present in the codebase or files
- DEVIATION: snapshot Q&A answer differed from the previous session's answer for the
  same question — possible semantic drift in Claude's understanding. Always include
  which Q-number, what the previous answer was, what the new answer is, and root cause.
- CORRECTION: amends a prior record — reference the original RECORD-NNN

## What qualifies

ALWAYS log:
- Any file where the documented value differed from the actual (stale baselines,
  wrong version numbers, missing entries)
- Any rule Claude was tempted to violate or misread
- Any session where generate_context.py / sync_docs.py produced unexpected output
- Any compliance check failure that revealed a pre-existing violation

LOG if notable:
- New architectural patterns discovered that aren't in GSI_SKILLS.md
- Dependency constraint discovered not in GSI_DEPENDENCIES.md
- Any time Claude asked a question the docs should have answered

DO NOT LOG:
- Routine sprint work with no surprises
- Decisions already recorded in GSI_DECISIONS.md
- Findings already in GSI_AUDIT_TRAIL.md

## Numbering

Read the last RECORD-NNN in GSI_SESSION_LEARNINGS.md and increment.

## After writing

1. Run `python3 regression.py` — the file is not checked by regression,
   so this is just a sanity gate for the overall session state.
2. Commit: `docs: log session_NNN learnings (N records)`
3. Continue with remaining Phase 3 close steps.

## Integration with Phase 3

Add to CLAUDE.md Phase 3 close protocol immediately before the version.py step:
```
- [ ] /log-learnings: append stale/confusion/learning records for this session
- [ ] sync_docs.py: python3 sync_docs.py (auto-updates CHANGELOG/README/AGENTS)
```
