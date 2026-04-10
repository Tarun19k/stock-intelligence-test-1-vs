# GSI Token Optimization & Model Selection Rules
# Extracted from sessions 021–022 methodology. Treat as standing policy.
# Last updated: 2026-04-10 (session_022)

---

## Part 1 — Model Selection Rules

### The Three-Tier Model

| Model | Cost Ratio | Use When |
|---|---|---|
| **Haiku** | 1× | Grep/search, doc-only edits, template-filling, single-line targeted edits with exact location known, compliance pattern checks, manifest creation from known schema |
| **Sonnet** | ~5× | Multi-section edits requiring contextual judgment, function rewrites, cross-file coherence, sprint planning, moderate architecture decisions |
| **Opus** | ~15× | Novel algorithm design, complex multi-file architecture with cascading implications, security audits, first-time design of new subsystems |

### Haiku Qualification Criteria
All 3 conditions must be true:
1. The edit location is known (file + function + approximate line range)
2. ≤1 judgment call is required (e.g. "insert this text after line X")
3. No cross-file reasoning is needed

If ANY condition fails → escalate to Sonnet.

### Sonnet Qualification Criteria  
At least one of:
- Multiple sections of a file need editing and they interact
- Must understand surrounding code to write correct code
- Edit touches 2+ files with coherence requirements
- Output feeds into another item's input

### Opus Qualification Criteria
Reserve for:
- First-time design of a new subsystem with no prior pattern in the repo
- Security review requiring adversarial thinking
- Architecture decisions that affect 5+ files
- Tasks where Sonnet has previously failed on a similar item

---

## Part 2 — Execution Mode Rules

### Sequential vs. Parallel Decision Matrix

| Scenario | Mode |
|---|---|
| Items touch different files, no shared state | **Parallel (worktree agents)** |
| Items touch the same file | **Sequential** |
| Item B requires output from Item A | **Sequential** |
| Doc-only items (*.md, *.json config) | **Batch into single Haiku agent** |
| High-risk items (new logic, core functions) | **Sequential in main context** |
| Regression must pass between items | **Sequential** |

### Worktree Agent Rules (Rule 8 enforcement)
- Agent prompt MUST include: file path, target function, and relevant CLAUDE.md scoped rules
- Agents MUST NOT run git commands — write the file only
- CTO reads agent diff before committing — never blind-commit agent output
- One regression run by CTO after all agents complete
- Cluster same-model items into single agent only if they touch different files

### Batching Rules
- Batch ONLY for doc-only changes (*.md, *.json config files)
- Never batch code files together — regression isolation requires separate commits
- Maximum batch size: 4 files per agent (beyond this, token savings are negated by prompt complexity)

---

## Part 3 — Read Cost Awareness

### File Read Cost Tiers

| Size | Approx Tokens | Rule |
|---|---|---|
| < 100 lines | ~1.5k | Read freely |
| 100–300 lines | ~4k | Read fully if you'll edit it; Grep if searching only |
| 300–600 lines | ~8k | Read targeted sections (offset/limit); Grep first to find location |
| > 600 lines | ~12k+ | NEVER read fully. Always use offset/limit targeting specific section |
| JSON manifests > 1000 lines | ~40k+ | Read only specific keys via offset to known line range |

### Known Expensive Files in This Repo

| File | Est. Tokens | Strategy |
|---|---|---|
| `GSI_session.json` | ~42k | Never read fully. Target `open_items` (line ~1086) and `meta` block only. Use CLAUDE.md as canonical backlog instead. |
| `GSI_SESSION_SNAPSHOT.md` | ~8k | Read only last SNAPSHOT block (last 40 lines) unless comparing full history |
| `pages/dashboard.py` | ~18k | Grep for target function first; read ±50 lines around it |
| `pages/home.py` | ~8k | Read in 100-line chunks targeting known functions |
| `indicators.py` | ~12k | Read only the function being changed + 20 lines context |
| `regression.py` | ~12k | Never read fully in-session; run via Bash only |

### Read-Before-Edit Rule (non-negotiable)
**Always Read before Edit — no exceptions.**
`read_avoidance` optimisation type is BANNED for files being edited.
Grep/Glob are valid for files being searched but not modified.

---

## Part 4 — Context Budget Allocation

### Session Context Budget (rough targets)

| Activity | Budget | Notes |
|---|---|---|
| Session startup (new-session) | ≤5k | After optimization (see new-session rules below) |
| Per file read (editing) | Pay actual cost | No avoidance |
| Per regression run | ~3k | Run only when required (pre-commit, post-sprint) |
| Worktree agent (isolated) | ~20–25k each | Does NOT consume main context |
| Haiku agent (Haiku model) | ~15–18k each | Cheaper; use for doc/manifest tasks |
| Sprint manifest write | ~4k | Template-fill; Haiku |
| sync_docs run | ~2k | Post-sprint only |
| Sprint close sequence | ~10k | Allocate at end |

### When to Stop and Checkpoint
- If >70% of estimated session context is consumed and sprint is <50% done → write GSI_WIP.md checkpoint
- If a single item is consuming >20k tokens → it needs splitting before continuation
- Regression failures that require diagnosis: cap at 3 investigation cycles before escalating to user

---

## Part 5 — Specific Anti-Patterns (learned from sessions)

### ❌ Anti-pattern: Full JSON read
```
Read GSI_session.json  # 42k tokens wasted
```
✅ Fix: Use `offset` to target `open_items` array. Or use CLAUDE.md open items table (already loaded in context).

### ❌ Anti-pattern: Redundant governance read
```
# Step 2: Read GSI_GOVERNANCE.md (7 policies)
```
✅ Fix: The 7 policies are summarized in CLAUDE.md (already in context). Only read GSI_GOVERNANCE.md when a policy is being amended or a new policy is being proposed.

### ❌ Anti-pattern: Full snapshot history read
```
Read GSI_SESSION_SNAPSHOT.md  # full file, all historical snapshots
```
✅ Fix: Read last 40 lines only. Previous snapshots are historical; only the most recent matters for deviation check.

### ❌ Anti-pattern: Blind agent dispatch
```
Agent: "Fix the SEBI compliance issue in home.py"  # no file path, no function, no rules
```
✅ Fix: Always include: file path + target function + line range + relevant scoped rules from CLAUDE.md.

### ❌ Anti-pattern: Diagnosis by reading entire file
```
# Bug in indicator pipeline → read all 670 lines of indicators.py
```
✅ Fix: Grep for the suspected function name first, read ±50 lines around the match, expand only if needed.

### ❌ Anti-pattern: Parallel agents on same file
```
# Agent 1: edit home.py line 333
# Agent 2: edit home.py line 343  (concurrent)
```
✅ Fix: Sequential in main context when both edits touch the same file. Parallel only across different files.

### ❌ Anti-pattern: Writing docs for undecided items
```
# Write sprint manifest before decisions are locked
```
✅ Fix: Lock all decisions (order, model, source choices, park/proceed) before writing any documentation.

---

## Part 6 — Sprint Planning Token Rules

### Pre-Sprint Checklist (token-efficient order)
1. Read GSI_WIP.md (mutex check) — ~1k
2. Confirm decisions already locked in session — no re-read
3. Write GSI_SPRINT_MANIFEST.json (Haiku, template-fill) — ~4k
4. Run regression once to confirm baseline — ~3k
5. Begin execution

### Sprint Item Budget Guide
| Item complexity | Model | Mode | Est. tokens |
|---|---|---|---|
| Single-line targeted fix | Haiku | Sequential or worktree | 8–12k |
| Multi-section page edit | Sonnet | Sequential | 15–20k |
| Cross-file coherence fix | Sonnet | Sequential | 20–25k |
| Doc-only batch (3–4 files) | Haiku | Single worktree agent | 15–18k |
| New subsystem design | Opus | Sequential | 30–50k |
| Parallel worktree cluster (3 items) | Haiku | 3× worktree agents | 45–54k agent (isolated) |

**Flag any single item estimated >20k as a split candidate before starting.**

---

## Part 7 — Model Mapping Reference Card

Quick lookup: activity type → model assignment

| Activity | Model |
|---|---|
| grep/glob/search in codebase | Haiku |
| Read file to understand (no edit planned) | Haiku |
| Insert SEBI disclaimer at known line | Haiku |
| Add st.caption after known line | Haiku |
| Fix single typo / wrong constant | Haiku |
| Update version string | Haiku |
| Write/update *.md governance doc | Haiku |
| Fill sprint manifest JSON template | Haiku |
| Update GSI_session.json meta fields | Haiku |
| Rewrite a function with logic changes | Sonnet |
| Add new section to a page (requires reading context) | Sonnet |
| Cross-file fix (same logic, 2 pages) | Sonnet |
| Sprint planning + item specs | Sonnet |
| Root cause diagnosis (unknown location) | Sonnet |
| New DO NOT UNDO rule proposal | Sonnet |
| ADR / architecture decision record | Sonnet |
| New subsystem design (first time) | Opus |
| Security audit | Opus |
| Complex multi-file refactor (5+ files) | Opus |
| Novel algorithm (e.g. QUANT-01 scoring engine) | Opus |

---

*Append new learnings after each sprint. This document is append-only for historical sections.*
