# AlphaVeda — Session Plan 2026-06-27
# Status: COUNCIL APPROVED — REVISED SEQUENCE (2026-06-27)
# Owner: Tarun Kochhar | CoS: Claude Sonnet 4.6
# Recorded: 2026-06-27 | Session: window-8671-2026-06-27

---

## Context

Phases 1–6 signed off. UI-1 design system complete (f36e6c9). 179 PASS / 1 SKIP / 3 FAIL (G0 seed gates).
All 21 council seats now skill-backed. Railway deployment approved per council recommendation.
Rules B/C approved by Tarun for global CLAUDE.md write.

---

## Streams (ordered execution)

### Stream 0 — Housekeeping Checkpoint ✓ COMPLETE
**Status:** DONE — commit 93e3140
**Model:** Haiku | **Skill:** housekeeping
- SESSION_RESUME.md updated and committed
- Graph rebuild triggered (auto-hook)

---

### Stream 1 — AlphaVeda MVP Spec
**Status:** ✓ COMPLETE — 2026-06-27 (commit ac9775d)
**Model:** Sonnet | **Skill:** ui-ux-pro-max + bridge-architect
**Est. tokens:** ~8,000
**Output:** `alphaveda/docs/MVP_SPEC.md`

Scope:
1. **Capabilities matrix** — 6 core features (market data, signals, path/Kelly, accuracy, ingest pipeline, SEBI compliance)
2. **User personas** — 3 types (retail researcher, HNI DIY investor, data-curious experimenter)
3. **UI-2 plan** — page-by-page design brief (Data Viewer, Signals, Path, Accuracy) using UI-1 tokens
4. **UX feature list** — MVP does/doesn't; cold-start states; empty states; staleness banners

Graph query first: `"AlphaVeda MVP capabilities personas"` before reading source files.

**Prerequisite:** None. Fully unblocked.
**Definition of done:** `alphaveda/docs/MVP_SPEC.md` committed.

---

### Stream 2 — Global CLAUDE.md Rules B/C
**Status:** ✓ COMPLETE — 2026-06-27 (126 lines; premortem window-8671-2026-06-27)
**Model:** Sonnet | **Skill:** doctrine-panel-constraint-enforcer (review) → CoS (write)
**Est. tokens:** ~5,000

Steps (strict order):
1. Log premortem (`log-premortem.py`, session `window-8671-2026-06-27`)
2. Read CLAUDE.md — audit current line count and structure
3. `doctrine-panel-constraint-enforcer` drafts Rule B and Rule C text
4. Design constraints: each rule = 3–4 lines max, no prose, telegraphic
5. CLAUDE.md must stay under 130 lines after addition
6. Add post-compaction recovery mandate (2 lines, CoS Domain G anchor)
7. Verify line count, commit

**Rule B (Seat Registration Requirement):**
Every council seat dispatched as an agent must have (1) a SKILL.md at `~/.claude/skills/<name>/SKILL.md`
and (2) an entry in `~/.claude/skills-index.md`. Dispatch of an unbacked seat = inadmissible verdict.
Verification: `~/.claude/scripts/check-seat-skill.sh <seat-name>`.

**Rule C (Zero-Assumption Tolerance):**
Every council dispatch prompt must reference its backing skill by name:
`"Apply the standard in ~/.claude/skills/<skill-name>/SKILL.md"`.
Inline description of seat behaviour without skill reference = violation.

**Post-compaction anchor:**
After any compaction event: run `/chief-of-staff recover` → read SESSION_RESUME.md before accepting new work.

**Prerequisite:** Premortem logged. Stream 1 not a prerequisite.
**Definition of done:** CLAUDE.md committed; line count verified ≤130.

---

### Stream 3 — Phase 7 Expert Planning Council
**Status:** QUEUED — background only if council approves
**Model:** Opus (Synthesis Chair) + Sonnet (3 seats) | **Skills:** synthesis-chair, doctrine-panel-systems-reliability-architect, doctrine-panel-constraint-enforcer, doctrine-panel-wealth-revenue-strategist
**Est. tokens:** ~25,000

Council brief:
> "Design a sprint plan for AlphaVeda Phase 7 — migration to hybrid architecture (Next.js on Vercel + FastAPI on Railway). Define session structure, risk register, token budgets, SEBI compliance wiring in Next.js, and the definition of Phase 7 complete. Prerequisite: G0 seed must pass before Phase 7 build begins."

Output: `alphaveda/docs/plans/PHASE7_BRIEF.md`

**Background eligibility conditions (per council):**
- Planning output only — no code, no architectural writes
- All decisions surface to Tarun before any implementation begins
- Phase 7 build cannot start until G0 seed passes AND Tarun explicitly approves Phase 7 brief

**Prerequisite:** Council approval for background execution.
**Definition of done:** `PHASE7_BRIEF.md` committed; Tarun reviews before Phase 7 build.

---

### Stream 4 — Memory + Graph Update
**Status:** QUEUED — runs after Streams 2+3 both complete
**Model:** Haiku | **Skill:** housekeeping + graphify
**Est. tokens:** ~2,000

Actions:
- Update `project_alphaveda_sprint.md` — Phase 7 mobilised, council verdict
- Update `project_alphaveda_governance_rules.md` — Rules B/C: APPROVED → WRITTEN
- New: `project_phase7_planning.md` — Phase 7 architecture, effort, council verdict
- Update `MEMORY.md` index — 3 entries
- `graphify --update alphaveda/` — wire Phase 7 brief + Rules B/C into knowledge graph

**Prerequisite:** Streams 2 + 3 both complete.
**Definition of done:** MEMORY.md committed; graphify update complete.

---

## Milestone map

| Milestone | Status | Blocker |
|---|---|---|
| Phases 1–6 complete | ✓ DONE | — |
| UI-1 design system | ✓ DONE | — |
| All 21 seats skill-backed | ✓ DONE | — |
| Railway deployment config | ○ PLANNED | ~30 min; post-council |
| Rules B/C → CLAUDE.md | ✓ DONE 2026-06-27 | 126 lines; premortem logged |
| AlphaVeda MVP spec | ○ QUEUED | Council clearance |
| G0 seed (live DB) | ✗ BLOCKED | Tarun runs ingest |
| Phase 7 brief | ○ COUNCIL PLANNING | Background agent |
| Phase 7 build | ✗ BLOCKED | G0 seed + Tarun approval |
| First subscriber | ✗ BLOCKED | G0 + auth layer |

---

## Commercial priority (standing)

Stream A (Gumroad Governance Pack): OVERDUE. All 6 gates pass. Tarun publishes.
Stream C (Consulting): OVERDUE. 3 targets needed. No code required.
Stream D (AlphaVeda): Blocked on G0 seed. Phase 7 in planning.

---

## Council review status — COMPLETE 2026-06-27

**Seats:** Red-Team / Constraint Enforcer / Synthesis Chair
**Verdict:** APPROVED WITH MANDATORY REVISIONS

| Stream | Verdict | Mandatory change |
|---|---|---|
| Stream 0 | APPROVED | Done |
| Stream 1 | APPROVED | Runs AFTER Stream 2 (not before) |
| Stream 2 | APPROVED | Premortem verified; Rule B adds "INADMISSIBLE"; Rule C adds council_review.py callout; post-compaction anchor after Cross-Workspace Rules |
| Stream 3 | APPROVED FOR BACKGROUND | PHASE7_BRIEF.md header = "DRAFT — no build without Tarun approval"; no architectural writes from agent |
| Stream 4 | APPROVED | Runs after 2+3 complete |

**Revised execution sequence:**
```
✓ Stream 0 — housekeeping         DONE (93e3140)
✓ Stream 2 — CLAUDE.md Rules B/C  DONE (76ade56; 126 lines)
✓ Stream 1 — MVP spec             DONE (ac9775d)
✓ Stream 3 — Phase 7 council      DONE (c1eacbe; 215 lines, DRAFT)
→ Stream 3 — Phase 7 council      BACKGROUND (after Stream 2, DRAFT only)
→ Stream 4 — memory + graph       AFTER 2+3 complete
```

**Stream 2 skill selection:** `doctrine-panel-constraint-enforcer` reviews and drafts; CoS executes write.
**Stream 3 background constraints:** DRAFT status enforced; no architectural writes; Tarun reviews before any Phase 7 action.
