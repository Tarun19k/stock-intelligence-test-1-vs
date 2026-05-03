# Workspace Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate skills, global config, hooks, and slash commands from `agentic-operations/global-config/` into `~/.claude/` (global) and repair all hardcoded device paths, following a file-level approval gate with snapshot/rollback support.

**Architecture:** Every file write is preceded by SHOW (present content) → WAIT (explicit "yes"/"proceed"/"approved") → SNAPSHOT → WRITE → CONFIRM → LOG. The migration registry and snapshot infrastructure are bootstrapped first (Phase 0). Global `~/.claude/` files are installed in Phase 1; command merges and path corrections happen in Phase 2; ops housekeeping closes in Phase 3.

**Tech Stack:** Bash (file ops, git, grep), JSON (migration-state.json), Markdown (registry, commands, skills). No Python dependencies. All writes are plain files — no compilation or package installs.

---

## File Map

| Path | Action | Phase |
|---|---|---|
| `agentic-operations/.gitignore` | Modify — add `backups/snapshots/` | 0 |
| `agentic-operations/MIGRATION_REGISTRY.md` | Create — append-only audit log | 0 |
| `agentic-operations/migration-state.json` | Create — machine-readable status tracker | 0 |
| `agentic-operations/backups/snapshots/` | Create directory | 0 |
| `~/.claude/CLAUDE.md` | Create — adapted global rules | 1 |
| `~/.claude/skills/token-tracker/SKILL.md` | Create — enhanced with model frontmatter | 1 |
| `~/.claude/skills/token-tracker/token-model-rules.md` | Create — verbatim copy | 1 |
| `~/.claude/skills/skill-design-guardrails/SKILL.md` | Create — enhanced with model frontmatter | 1 |
| `~/.claude/commands/workspace-status.md` | Create — path-corrected | 1 |
| `~/.claude/commands/new-session.md` | Create — global version, path-corrected | 2 |
| `~/.claude/commands/close-session.md` | Create — global generic version | 2 |
| `~/.claude/commands/log-learnings.md` | Create — global generic version | 2 |
| `agentic-operations/global-config/bootstrap.sh` | Modify — lines 250–252 path correction | 2 |
| Statusline decision | Decision gate (no write unless Tarun chooses install) | 2 |
| `agentic-operations/.claude/registry.json` | Modify — memory_path line 8 | 3 |
| `agentic-operations/WORKSPACE_MERGE_ACTION_PLAN.md` | Modify — mark completed items DONE | 3 |
| `agentic-operations/migration-state.json` | Modify — set session_closed, all statuses complete | 3 |
| `agentic-operations/environment-snapshots/home-device-2026-05-02/README.md` | Create — snapshot index and validation guide | 4 |
| `agentic-operations/environment-snapshots/home-device-2026-05-02/environment.md` | Create — full ~/.claude/ state manifest | 4 |
| `agentic-operations/environment-snapshots/home-device-2026-05-02/migration-state-final.json` | Create — copy of closed migration-state.json | 4 |
| `agentic-operations/environment-snapshots/home-device-2026-05-02/verify.sh` | Create — runnable validation script | 4 |
| `agentic-operations/environment-snapshots/home-device-2026-05-02/verify-output.txt` | Create — captured output of running verify.sh on this device | 4 |

---

## Task 1: Phase 0 — Bootstrap Migration Infrastructure

**Files:**
- Modify: `agentic-operations/.gitignore`
- Create: `agentic-operations/MIGRATION_REGISTRY.md`
- Create: `agentic-operations/migration-state.json`
- Create dir: `agentic-operations/backups/snapshots/`

> **Phase 0 bootstrap exception:** These are the first writes. Snapshot infrastructure is being established — the SNAPSHOT step is skipped for these items only. All subsequent phases use full approval gate.

---

- [ ] **Step 1.1: SHOW — present .gitignore amendment to Tarun**

Display this diff:
```diff
--- a/agentic-operations/.gitignore
+++ b/agentic-operations/.gitignore
@@ +++ b
+backups/snapshots/
```

State: "This prevents snapshot files from being committed to the agentic-operations repo. Risk: LOW. Reversible: yes (remove line). Awaiting approval."

- [ ] **Step 1.2: WAIT — do not proceed until Tarun confirms**

- [ ] **Step 1.3: WRITE — amend .gitignore**

Read current `.gitignore`:
```bash
cat "/Users/home/Agentic Tools - Projects/agentic-operations/.gitignore"
```

Add `backups/snapshots/` on a new line at the end. Use Edit tool, appending after the last existing line.

- [ ] **Step 1.4: CONFIRM — verify the line was added**

```bash
grep "backups/snapshots" "/Users/home/Agentic Tools - Projects/agentic-operations/.gitignore"
```
Expected: `backups/snapshots/`

- [ ] **Step 1.5: SHOW — present MIGRATION_REGISTRY.md content to Tarun**

Display the following content and await approval:

```markdown
# Migration Registry — home device
# Append-only. Never edit existing entries.
# Last updated: 2026-05-02

---

## [2026-05-02] — phase-0-bootstrap
- **Action:** create
- **Source:** (new — not from agentic-operations source)
- **Destination:** agentic-operations/MIGRATION_REGISTRY.md (this file)
- **Status:** completed
- **Rationale:** Bootstrap migration audit infrastructure before any other writes
- **Snapshot:** bootstrap-exception (snapshot gate being established)
- **Reversibility:** delete this file
- **Approved by:** Tarun (explicit confirmation in session)

## [2026-05-02] — phase-0-migration-state
- **Action:** create
- **Source:** (new)
- **Destination:** agentic-operations/migration-state.json
- **Status:** completed
- **Rationale:** Machine-readable status tracker for all migration items
- **Snapshot:** bootstrap-exception
- **Reversibility:** delete this file
- **Approved by:** Tarun (explicit confirmation in session)

## [2026-05-02] — phase-0-gitignore
- **Action:** modify
- **Source:** agentic-operations/.gitignore
- **Destination:** agentic-operations/.gitignore
- **Status:** completed
- **Rationale:** Prevent snapshot artifacts from being committed to repo
- **Snapshot:** bootstrap-exception
- **Reversibility:** remove `backups/snapshots/` line
- **Approved by:** Tarun (explicit confirmation in session)
```

- [ ] **Step 1.6: WAIT — do not proceed until Tarun confirms**

- [ ] **Step 1.7: WRITE — create MIGRATION_REGISTRY.md**

Write exactly the content shown in Step 1.5 to:
`/Users/home/Agentic Tools - Projects/agentic-operations/MIGRATION_REGISTRY.md`

- [ ] **Step 1.8: SHOW — present migration-state.json to Tarun**

Display and await approval:

```json
{
  "schema_version": "1",
  "device": "home",
  "session_opened": "2026-05-02",
  "session_closed": null,
  "phase": "0",
  "items": [
    { "id": "global-claude-md",                "status": "pending", "destination": "/Users/home/.claude/CLAUDE.md",                                                "action": "create",   "snapshot_path": "bootstrap-exception", "completed_at": null },
    { "id": "token-tracker-skill-md",           "status": "pending", "destination": "/Users/home/.claude/skills/token-tracker/SKILL.md",                             "action": "create",   "snapshot_path": null, "completed_at": null },
    { "id": "token-tracker-rules-md",           "status": "pending", "destination": "/Users/home/.claude/skills/token-tracker/token-model-rules.md",                 "action": "create",   "snapshot_path": null, "completed_at": null },
    { "id": "skill-design-guardrails-skill-md", "status": "pending", "destination": "/Users/home/.claude/skills/skill-design-guardrails/SKILL.md",                   "action": "create",   "snapshot_path": null, "completed_at": null },
    { "id": "workspace-status-command",         "status": "pending", "destination": "/Users/home/.claude/commands/workspace-status.md",                              "action": "create",   "snapshot_path": null, "completed_at": null },
    { "id": "new-session-command",              "status": "pending", "destination": "/Users/home/.claude/commands/new-session.md",                                   "action": "create",   "snapshot_path": null, "completed_at": null },
    { "id": "close-session-command",            "status": "pending", "destination": "/Users/home/.claude/commands/close-session.md",                                 "action": "create",   "snapshot_path": null, "completed_at": null },
    { "id": "log-learnings-command",            "status": "pending", "destination": "/Users/home/.claude/commands/log-learnings.md",                                 "action": "create",   "snapshot_path": null, "completed_at": null },
    { "id": "bootstrap-sh-correction",          "status": "pending", "destination": "/Users/home/Agentic Tools - Projects/agentic-operations/global-config/bootstrap.sh", "action": "modify", "snapshot_path": null, "completed_at": null },
    { "id": "statusline-decision",              "status": "pending", "destination": "TBD — awaiting Tarun decision",                                                 "action": "pending-decision", "snapshot_path": null, "completed_at": null },
    { "id": "registry-json-fix",               "status": "pending", "destination": "/Users/home/Agentic Tools - Projects/agentic-operations/.claude/registry.json",  "action": "modify",   "snapshot_path": null, "completed_at": null },
    { "id": "action-plan-update",              "status": "pending", "destination": "/Users/home/Agentic Tools - Projects/agentic-operations/WORKSPACE_MERGE_ACTION_PLAN.md", "action": "modify", "snapshot_path": null, "completed_at": null }
  ]
}
```

- [ ] **Step 1.9: WAIT — do not proceed until Tarun confirms**

- [ ] **Step 1.10: WRITE — create migration-state.json**

Write exactly the content shown in Step 1.8 to:
`/Users/home/Agentic Tools - Projects/agentic-operations/migration-state.json`

- [ ] **Step 1.11: Create snapshots directory**

```bash
mkdir -p "/Users/home/Agentic Tools - Projects/agentic-operations/backups/snapshots"
```

- [ ] **Step 1.12: CONFIRM — verify all Phase 0 artifacts**

```bash
ls "/Users/home/Agentic Tools - Projects/agentic-operations/backups/snapshots"
ls "/Users/home/Agentic Tools - Projects/agentic-operations/MIGRATION_REGISTRY.md"
ls "/Users/home/Agentic Tools - Projects/agentic-operations/migration-state.json"
grep "backups/snapshots" "/Users/home/Agentic Tools - Projects/agentic-operations/.gitignore"
```

Expected: all four checks return output (files exist, gitignore entry present).

- [ ] **Step 1.13: LOG — update migration-state.json phase to "1"**

Edit `migration-state.json`: change `"phase": "0"` to `"phase": "1"`.

- [ ] **Step 1.14: Commit Phase 0 to agentic-operations**

```bash
cd "/Users/home/Agentic Tools - Projects/agentic-operations"
git add .gitignore MIGRATION_REGISTRY.md migration-state.json
git commit -m "feat(migration): Phase 0 — bootstrap snapshot infrastructure and migration registry"
```

---

## Task 2: Phase 1a — Install Global CLAUDE.md

**Files:**
- Create: `~/.claude/CLAUDE.md`

**Model:** Sonnet — cross-file adaptation with semantic judgment (path updates + Merge Status rewrite).

---

- [ ] **Step 2.1: SHOW — present adapted ~/.claude/CLAUDE.md to Tarun**

Display the following adapted content and await approval. Changes from source are marked with `← ADAPTED`:

```markdown
# graphify
- **graphify** (`~/.claude/skills/graphify/SKILL.md`) - any input to knowledge graph. Trigger: `/graphify`
When the user types `/graphify`, invoke the Skill tool with `skill: "graphify"` before doing anything else.
# Global Operating Rules

## Owner
Tarun Kochhar (tarun.kochhar19@gmail.com). Claude operates as chief of staff across all workspaces.

## Active Workspaces
- **Agentic Applications** — `/Users/home/Agentic Tools - Projects/agentic-operations/` — org infrastructure, knowledge graph, 13-business-unit corpus. GitHub: https://github.com/Tarun19k/agentic-operations
- **GSI Dashboard** — `/Users/home/Agentic Tools - Projects/stock-intelligence-test-1-vs` — Global Stock Intelligence app (Streamlit, Python). GitHub: https://github.com/Tarun19k/stock-intelligence-test-1-vs
- **Crochet Counter** — not on this device — vanilla JS PWA, crochet row tracker. GitHub: https://github.com/Tarun19k/crochet-counter.git

## Response Style (applies everywhere)
- Plain English. Graph-level clarity — short tables, bullets, one-sentence insights.
- Never summarise what you just did at the end of a response.
- Lead with the answer, not the reasoning chain.

## Session Protocol
- Start every session with `/new-session` — loads state, runs regression, confirms readiness.
- End every session with `/close-session` — commits, updates session manifest, snapshots memory.
- Use `/workspace-status` when switching between workspaces.
- Use `/log-learnings` whenever Tarun corrects an approach or confirms a non-obvious decision.

## Model Routing (global default — see token-model-rules.md for full detail)
- Haiku: mechanical tasks, single-file fixes, clear scope, no cross-file reasoning.
- Sonnet: architectural decisions, multi-file reasoning, synthesis, design.
- Never route to Haiku for tasks above the 43k-token break-even threshold (GSI Rule 18).

## Cross-Workspace Rules
- Changes to `~/.claude/commands/` or `~/.claude/CLAUDE.md` affect ALL workspaces — confirm before modifying.
- GSI DO NOT UNDO rules (18 rules in GSI CLAUDE.md) take precedence in the GSI workspace.
- Org-level governance (org-corpus/) sits above product-level governance (GSI_GOVERNANCE.md).
- GSI session state lives in `GSI_session_updated.json` committed directly to the GSI repo after every session. No Gist.

## Merge Status
Phases 0–3 migration in progress on this device (home). Phase 0 complete.
Action plan: `agentic-operations/WORKSPACE_MERGE_ACTION_PLAN.md`.
Completed on this device: F3 (GSI_CONTEXT.md), F4 (GSI_session.json), G3 (quant_audit_pending state).
Remaining: Phase 4 strategic items S1–S5 (deferred — scope TBD).

## Data Governance Approval Gate (all workspaces)
The following NEVER proceed without explicit Tarun approval — in chat or via ENRICHMENT_LOG.md status:
- Any write to org-corpus/, GSI source files, or equivalent workspace source data
- Any knowledge graph rebuild or data pipeline run
- Any change to CLAUDE.md, session commands, or settings.json hooks/permissions
- Any enrichment proposal implementation (must show APPROVED in the log first)
- Any operation with direct or indirect impact on: data cleanliness, staleness, security, privacy, authenticity, validity
One-time session exception: Tarun may say "proceed without asking for [specific action] this session" — valid for that session only, never persisted.
```

State: "Destination: `~/.claude/CLAUDE.md` (new file — affects all workspaces). Risk: LOW — global rules only, no code. Reversible: delete file. Awaiting approval."

- [ ] **Step 2.2: WAIT — do not proceed until Tarun confirms**

- [ ] **Step 2.3: SNAPSHOT — write pre-install snapshot**

Since `~/.claude/CLAUDE.md` does not yet exist, note in the registry:

Append to `agentic-operations/MIGRATION_REGISTRY.md`:
```markdown
## [2026-05-02] — global-claude-md
- **Action:** create
- **Source:** global-config/CLAUDE.md (adapted)
- **Destination:** /Users/home/.claude/CLAUDE.md
- **Status:** in_progress
- **Rationale:** Global operating rules affecting all workspaces — paths corrected for this device
- **Snapshot:** new-file (no pre-existing content to snapshot)
- **Reversibility:** delete /Users/home/.claude/CLAUDE.md
- **Approved by:** Tarun (explicit confirmation in session)
```

Update `migration-state.json`: set `global-claude-md` status to `"in_progress"`.

- [ ] **Step 2.4: WRITE — create ~/.claude/CLAUDE.md**

```bash
mkdir -p ~/.claude
```

Then write exactly the content shown in Step 2.1 to `/Users/home/.claude/CLAUDE.md`.

- [ ] **Step 2.5: CONFIRM — verify content**

```bash
head -5 ~/.claude/CLAUDE.md
grep "Users/home" ~/.claude/CLAUDE.md
grep "tarunkochhar" ~/.claude/CLAUDE.md
```

Expected:
- `head -5` shows `# graphify` on line 1
- `grep "Users/home"` returns 2 lines (Agentic Applications + GSI paths)
- `grep "tarunkochhar"` returns NO output

- [ ] **Step 2.6: LOG — update registry and state**

In `MIGRATION_REGISTRY.md`, update the `global-claude-md` entry: `**Status:** completed`.

In `migration-state.json`, update `global-claude-md`: `"status": "completed"`, `"completed_at": "2026-05-02"`.

---

## Task 3: Phase 1b — Install token-tracker Skill

**Files:**
- Create: `~/.claude/skills/token-tracker/SKILL.md`
- Create: `~/.claude/skills/token-tracker/token-model-rules.md`

**Model:** Haiku — template addition to known pattern, single directory, no cross-file reasoning.

---

- [ ] **Step 3.1: SHOW — present enhanced SKILL.md to Tarun**

Display the following content (source + `model: haiku` frontmatter added) and await approval:

```markdown
---
name: token-tracker
description: Track and attribute token costs per activity during a Claude Code session. Use this skill whenever the user asks "how much did that cost", "how many tokens", "track my usage", "what's the token cost", "monitor costs", or is about to run an expensive operation (visual companion brainstorming, agent spawns, reading large files, QA orchestration). Also invoke proactively at the start of any session where the user has indicated they want cost visibility. This skill gives you a concrete discipline for estimating, logging, and summarising token costs in real time — without guessing.
model: haiku
---

# Token Tracker

A lightweight discipline for attributing token costs to specific activities during a session. The goal is not perfect accounting — it's enough signal to answer "was that expensive, and why?" so the user can decide what to optimise.

## Model Selection — Map Before Every Task

Before starting any action, task, or activity, state which model you'll use and why. Default to the cheapest model that can do the job correctly.

| Task type | Model | Reasoning |
|-----------|-------|-----------|
| Single CSS rule / aria attribute / one-liner fix | **Haiku** | Mechanical, clear scope, low output |
| Simple bug fix (1 file, < 50 lines output) | **Haiku** | Well-defined, no architectural judgment needed |
| Multi-file refactor, state logic, event delegation | **Sonnet** | Requires cross-file reasoning |
| Brainstorming, architecture, design decisions | **Sonnet** | Needs judgment and context synthesis |
| Debugging complex cross-file interactions | **Sonnet** | Needs deep reasoning across codebase |
| Visual companion screens | **Sonnet** | HTML generation with design judgment |
| Mechanical QA tasks (aria, toast, layout fixes) | **Haiku** | Proven pattern from prior QA work |
| Subagent spawns for parallel exploration | **Haiku** | Exploration tasks are narrow in scope |

**Rule:** State the model choice at the top of every task plan: `Model: Haiku — single CSS fix, no cross-file reasoning needed.`

Escalate to Sonnet only if Haiku output is incorrect or the task turns out to be wider than scoped. Log the escalation reason.

---

## Rate Card (verify against token_log.json if project has one)

| Model | Input $/1M | Output $/1M |
|-------|-----------|------------|
| claude-sonnet-4-x | $3.00 | $15.00 |
| claude-haiku-4-x  | $0.80 |  $4.00 |

Quick mental math: 1,000 tokens ≈ 750 words. At Sonnet rates, 10k input tokens = $0.03.

## What to Track

Log an entry after every major activity. "Major" means any of:

- Reading a file > 2k tokens (check: ~8k chars ≈ 2k tokens)
- Writing a visual companion screen (HTML output)
- Spawning a subagent
- Running a QA task
- Loading a skill body
- Any response that clearly involved heavy reasoning

Don't log: git commands, small file reads, short text replies.

## Log Format

Maintain a running log in the session. When the user asks for a summary, or at natural breakpoints (end of a phase, before a major operation), print the log.

```
SESSION TOKEN LOG — [date]
────────────────────────────────────────────
 Activity                        Input   Output   Est. Cost
 ─────────────────────────────────────────────────────────
 Load CLAUDE.md + rules          ~9.5k      —       $0.029
 Read app.js                     ~7.6k      —       $0.023
 Visual companion screen 1          —    ~0.8k      $0.012
 Visual companion screen 2          —    ~1.1k      $0.017
 Subagent: vault regeneration    ~5.0k   ~0.5k      $0.023
 ─────────────────────────────────────────────────────────
 Session total                  ~22.1k   ~2.4k      $0.104
 Budget remaining (if known)                        $24.77
────────────────────────────────────────────
```

## Estimation Rules

**Input tokens (what you read):**
- File read: chars ÷ 4 (rough tokens). Use the file_token_costs table in token_log.json if it exists.
- Context baseline (CLAUDE.md + rules + system prompt): ~9,500 tokens for this project (from token_log.json).
- Skill body load: count lines × ~12 tokens/line as a rough estimate.
- Conversation history: grows ~500–1,000 tokens per exchange; after 10 exchanges add ~7k to running total.

**Output tokens (what you write):**
- Short reply (< 200 words): ~150 tokens
- Code block (~50 lines): ~400 tokens
- Visual companion HTML screen: ~600–1,500 tokens depending on complexity
- Full file rewrite: chars ÷ 4

**Subagent overhead:** Each spawned agent re-pays the context baseline (~9,500 tokens input) plus whatever files it reads. Mark these clearly in the log.

**Visual companion cost pattern:**
Each brainstorming screen costs roughly:
- Writing HTML: 600–1,500 output tokens ($0.009–$0.023 at Sonnet rates)
- Reading the skill guide once: ~2,000 input tokens ($0.006)
- Server interactions (bash calls): negligible

A full 10-screen brainstorming session ≈ $0.15–$0.25 in output tokens alone.

## How to Use

1. **Session start:** Note the context baseline (files already loaded, skill bodies read).
2. **As you work:** After each major activity, add a line to your mental log with an estimate.
3. **On request or at phase boundaries:** Print the full log table.
4. **Flag before expensive operations:** If about to spawn multiple agents or read pattern.js (41k tokens), warn the user: "This will cost ~$X — proceed?"

## Integration with Existing QA Budget

If the project has `qa-reports/token_log.json`, use its rate card and `month_spent_usd` as the baseline. Add session costs to the running total mentally — the log file itself is only updated by the QA orchestrator skill after completed tasks.

For non-QA work (brainstorming, visual companion, ad-hoc exploration), track separately and report to the user so they can decide whether to update the log manually.

## On Accuracy

These are estimates, not invoices. Claude doesn't have access to the actual token counter. The value is:
- Relative cost awareness ("that agent spawn cost 3× more than this file read")
- Catching surprises before they happen ("reading pattern.js alone = $0.12")
- Informing model choice ("this is a simple CSS fix — Haiku would be fine")

When uncertain, round up. Better to overestimate and be pleasantly wrong.
```

State: "Destination: `~/.claude/skills/token-tracker/SKILL.md` (new file). Enhancement: `model: haiku` frontmatter added (not in source). Risk: LOW. Reversible: delete file. Awaiting approval."

- [ ] **Step 3.2: WAIT — do not proceed until Tarun confirms**

- [ ] **Step 3.3: SNAPSHOT — write pre-install note**

Append to `agentic-operations/MIGRATION_REGISTRY.md`:
```markdown
## [2026-05-02] — token-tracker-skill-md
- **Action:** create
- **Source:** global-config/skills/token-tracker/SKILL.md (enhanced: model: haiku frontmatter added)
- **Destination:** /Users/home/.claude/skills/token-tracker/SKILL.md
- **Status:** in_progress
- **Rationale:** Token cost attribution skill; model frontmatter enforces Haiku routing for mechanical tracking tasks
- **Snapshot:** new-file
- **Reversibility:** delete /Users/home/.claude/skills/token-tracker/
- **Approved by:** Tarun (explicit confirmation in session)
```

Update `migration-state.json`: `token-tracker-skill-md` → `"in_progress"`.

- [ ] **Step 3.4: WRITE — create directory and SKILL.md**

```bash
mkdir -p ~/.claude/skills/token-tracker
```

Write exactly the content shown in Step 3.1 to `/Users/home/.claude/skills/token-tracker/SKILL.md`.

- [ ] **Step 3.5: WRITE — create token-model-rules.md**

Write the following content (verbatim from source `global-config/skills/token-tracker/token-model-rules.md`) to `/Users/home/.claude/skills/token-tracker/token-model-rules.md`:

```markdown
# Token Model Rules — Unified
# Covers: token-tracker skill defaults + GSI Rule 18 + cross-workspace routing
# Last updated: 2026-05-01

---

## The Core Decision

Before every task, state the model and why. One line:
> `Model: Haiku — single CSS fix, no cross-file reasoning.`
> `Model: Sonnet — multi-file refactor, architectural judgment required.`

Never leave the model choice implicit.

---

## Tier System

### T1 — Haiku
**Use when ALL of these are true:**
- Single file, or two files with a clear mechanical relationship
- Output is under ~100 lines
- No architectural judgment required
- Task is a known pattern (CSS patch, aria attribute, one-liner fix, stub creation, mechanical rename)
- Estimated context at start of task is **under 43k tokens**

**Examples:** Single CSS rule, aria attribute, one-liner bug fix, stub file creation, moving/renaming files, simple regex replacement, generating a JSON template.

---

### T2 — Sonnet (default)
**Use when ANY of these is true:**
- Cross-file reasoning needed (e.g. a change in utils.py that affects pages/)
- Output is 50–500 lines with design choices embedded
- Debugging a non-obvious interaction (state, fragments, caching)
- Architectural decision required (what approach, not just how)
- Task requires synthesising multiple files or contexts
- Estimated context **between 43k and 200k tokens**

**Examples:** Multi-file refactor, state logic, event delegation, session protocol implementation, API integration, component design, visual layout decisions, writing governance docs.

---

### T3 — Sonnet + extended thinking (rare)
**Use only when:**
- Deep reasoning required that T2 gets wrong
- Trade-off analysis with multiple valid approaches
- Security review or compliance gap analysis
- Estimated context **above 200k tokens**

---

## The 43k Break-Even Rule (GSI Rule 18)

At 43k tokens of input context, the cost difference between Haiku and Sonnet narrows to the point where Sonnet's quality improvement pays for itself. **Never route a subagent task to Haiku if the estimated context exceeds 43k tokens.**

**Why this number:** Derived from GSI token burn log data (schema_version 2, `docs/ai-ops/token-burn-log.jsonl`). Haiku is ~5× cheaper per token than Sonnet, but on complex tasks above this threshold, Haiku required 2–3× more iterations to produce correct output — making it more expensive in total.

**Practical check:** If you're about to dispatch a subagent and the task involves reading more than ~3 average-sized files (each ~600 lines ≈ 15k tokens each), you're at or above the break-even. Use Sonnet.

---

## Escalation Protocol

1. Dispatch at T1 (Haiku) for tasks that meet all T1 criteria.
2. If Haiku output is incorrect or incomplete: escalate to T2 (Sonnet). Log the escalation:
   > `Escalated T1→T2: Haiku missed [specific issue]. Switching to Sonnet.`
3. Never silently retry Haiku with the same prompt — escalate and explain.

---

## Cost Estimation (before every task)

```
estimated_input  = (context_baseline + task_input_tokens)
estimated_output = expected_lines × 8   (approx tokens/line)
estimated_cost   = (input × model_input_rate) + (output × model_output_rate)
```

Log estimate before task, log actuals after. Use `token-tracker` skill for the accounting.

---

## Per-Task Model Map (quick reference)

| Task | Model | Reason |
|------|-------|--------|
| Single CSS rule / aria / one-liner | Haiku | Mechanical, clear scope |
| Simple bug fix (1 file, <50 lines) | Haiku | Well-defined, no judgment |
| Stub file / scaffold creation | Haiku | Template output |
| Multi-file refactor | Sonnet | Cross-file reasoning |
| State logic / session management | Sonnet | Non-obvious interactions |
| Architecture / design decisions | Sonnet | Judgment required |
| Governance / policy docs | Sonnet | Synthesis across contexts |
| Debugging complex interactions | Sonnet | Deep reasoning |
| Subagent tasks < 43k context | Haiku | Below break-even |
| Subagent tasks ≥ 43k context | Sonnet | GSI Rule 18 applies |
| Security / compliance review | Sonnet (T3 if complex) | Cannot afford errors |
| Knowledge graph extraction | Sonnet | Cross-document synthesis |
```

- [ ] **Step 3.6: CONFIRM — verify both files**

```bash
head -5 ~/.claude/skills/token-tracker/SKILL.md
grep "model: haiku" ~/.claude/skills/token-tracker/SKILL.md
ls ~/.claude/skills/token-tracker/
```

Expected:
- `head -5` shows `---` frontmatter opening
- `grep "model: haiku"` returns the model line
- `ls` shows `SKILL.md` and `token-model-rules.md`

- [ ] **Step 3.7: LOG — update registry and state**

Append to `MIGRATION_REGISTRY.md` (update status to completed). Update `migration-state.json` for both `token-tracker-skill-md` and `token-tracker-rules-md`: status → `"completed"`, `completed_at`: `"2026-05-02"`.

---

## Task 4: Phase 1c — Install skill-design-guardrails Skill

**Files:**
- Create: `~/.claude/skills/skill-design-guardrails/SKILL.md`

**Model:** Haiku — template addition, single file, no judgment required.

---

- [ ] **Step 4.1: SHOW — present enhanced SKILL.md to Tarun**

Display the following content (source + `model: haiku` frontmatter added) and await approval:

```markdown
---
name: skill-design-guardrails
description: Checklist and design principles for building new skills — evals, token estimation, model routing, state schema, verification steps. Use before finalising any new skill, especially orchestration or tracking skills.
model: haiku
---

# Skill Design Guardrails

Derived from the qa-orchestrator threat assessment (2026-04-23). Apply these before finalising any skill, especially orchestration or tracking skills.

---

## Pre-Launch Checklist

Before running evals or packaging, every skill must pass these checks:

### Evals
- [ ] Every eval prompt has a matching fixture — no prompt that triggers a file read without that file existing
- [ ] Every eval has at least 2 objectively verifiable assertions (not subjective)
- [ ] Expected outputs are computed, not eyeballed — run the arithmetic, check the math
- [ ] Both `with_skill` and `without_skill` baseline runs are planned for the same turn
- [ ] Skill is packaged and installed before `with_skill` runs are spawned

### Skill body
- [ ] Error handling section present: what does the skill do when required files are missing, malformed, or out of sync?
- [ ] All statuses in state schemas are defined and exhaustive (e.g. `pending`, `in_progress`, `completed`, `failed`)
- [ ] A verification step exists between "execute" and "log as done"
- [ ] Escalation path exists when the primary approach fails (e.g. haiku fails → retry with sonnet)
- [ ] No hardcoded absolute paths — use `$PWD`, relative paths, or configurable values

### Infrastructure
- [ ] Any JSON log files have a documented recovery path if a write is interrupted
- [ ] Hook scripts fail gracefully and output valid JSON even on error
- [ ] Session-spanning state (queues, logs) has a defined conflict resolution policy

---

## Token Estimation Accuracy

### Context baseline
Never use a single fixed number. The baseline is the sum of:

| Component | How to measure |
|---|---|
| System prompt | Estimate 3000–4000 tokens (varies by Claude Code version) |
| Always-loaded CLAUDE.md | `wc -c CLAUDE.md` → divide by 4 |
| Always-loaded rules files | `wc -c .claude/rules/*.md` → divide by 4 |
| Skill body (if skill is active) | `wc -c SKILL.md` → divide by 4 |
| Conversation history at task start | Grows through a session — add ~1000 per prior task turn |

**Practical default**: measure the project's always-loaded files once, add 3500 for system prompt, and store the result in the task queue's `context_baseline_tokens`. Re-measure if CLAUDE.md or rules change significantly. Do not use 6500 as a universal constant — it will be wrong for most projects.

### Per-task costs that are commonly missed

| Missed cost | Why it matters | How to handle |
|---|---|---|
| Skill body load | Every invocation of a skill adds ~skill_chars/4 tokens | Add to per-task input estimate or to baseline |
| File re-reads | Debugging often reads the same file 2–3× | Estimate 1.5× single-read cost for tasks involving reasoning |
| Conversation history growth | Each completed task adds to input cost of the next | Add +500 tokens per prior completed task in the same session |
| Subagent parent overhead | Agent tool call + result ingestion costs ~200–400 tokens in the parent | Add per subagent spawn |
| Output retries | A fix that fails and is corrected doubles or triples output tokens | Budget 2× estimated output for haiku tasks (lower reliability) |

### Accuracy tier expectations
- **Pre-task estimates**: target ±30% accuracy — these are for routing and budgeting decisions
- **Post-task actuals**: count chars written (code + prose) / 4 — these are for the log
- **Session totals**: expect 15–40% underestimate due to conversation history growth and retries — document this as a known systematic bias, not an error

---

## Model Routing Design

### When to use Haiku
Haiku is appropriate when:
- The fix location is already known before reading the file (the task description pinpoints it)
- The change is formulaic — adding an attribute, changing a constant, a 1-line conditional
- The output is verifiable by visual inspection in under 30 seconds
- Failure cost is low — the change is easy to revert if wrong

### When to use Sonnet
Sonnet is required when:
- The task requires reading and reasoning about existing behavior before deciding what to change
- The change spans 2+ files with non-trivial interactions
- The output requires judgment about correctness (e.g. is this modal pattern accessible?)
- Haiku previously failed or produced an incorrect fix for this task type

### Escalation rule
Always define an explicit escalation path in the skill: if the routed model produces an incorrect or incomplete result (detected via verification step), re-attempt with Sonnet. Log the escalation as a separate entry in the token log with reason `"haiku_escalated"`.

### Never route to Haiku
- Behavioral analysis or architectural decisions
- Multi-file refactors where the interaction surface is unclear
- Tasks with high revert cost (data migrations, auth changes, destructive operations)

---

## State Schema Requirements

Any skill that maintains persistent state (queues, logs, progress) must define:

### Status completeness
Every stateful entity needs an exhaustive status set:
```
pending → in_progress → completed
                     ↘ failed
```
`in_progress` is not optional — it's the only way to detect interrupted sessions and prevent re-execution of partial work.

### Resumption protocol
Document explicitly: if a session ends with a task `in_progress`, what should the next session do?
- Option A: treat as failed, restart from scratch
- Option B: read the partially-modified files and continue from where the diff left off
- Option C: mark as `needs_review`, surface to user before proceeding

Choose one and write it into the skill body.

### Atomic writes
For any JSON log that accumulates across sessions:
- Write to a `.tmp` file first, then rename (atomic on POSIX)
- Or keep a backup copy before overwriting
- The hook script reading the log must handle `JSONDecodeError` and output a valid (degraded) context message rather than crashing silently

### Conflict policy
If two sessions could write to the same log file, define which wins. For single-user local projects, "last write wins" is acceptable if documented. For shared environments, implement a lock file.

---

## Verification Step Design

Every task execution protocol must include a verification step between "execute" and "log as completed." The verification method should match the task type:

| Task type | Verification method |
|---|---|
| UI change | Read the modified file and confirm the intended diff is present |
| Behavioral fix | Describe the expected behavior change and confirm the code implements it |
| Accessibility attribute | Grep for the added attribute in the output file |
| Doc update | Re-read the updated section and confirm it matches the intent |
| Multi-file change | Verify each file independently, then check for cross-file consistency |

**Minimum bar**: always re-read the changed section of the file after writing and confirm it looks correct before marking the task `completed`. Never log completion based on the intent to write — only after confirming the write produced the intended result.

---

## Eval Design Requirements

### Fixture completeness rule
Every eval prompt that causes a file read or write must have that file present in the fixtures directory. Missing fixtures produce false failures that hide real skill problems.

### Assertion quality bar
Good assertions are:
- **Specific**: "response includes the string '12700' as the input token estimate" — not "response mentions token counts"
- **Binary**: pass or fail with no grey area
- **Independent**: each assertion tests one thing

Avoid assertions that would pass even without the skill (non-discriminating). The best assertions are ones where the baseline (without skill) reliably fails.

### Arithmetic assertions
Any eval that requires numerical output (cost projections, token totals) must:
1. Pre-compute the correct value independently before writing the assertion
2. Assert the exact value or a tight range (±5%)
3. Never copy the expected value from the skill's own output — compute it from first principles

### Minimum eval coverage for orchestration skills
- 1 eval testing session-start state reporting
- 1 eval testing the core execution protocol (estimate → route → execute → log)
- 1 eval testing numerical accuracy (token/cost projection)
- 1 eval testing error handling (missing file, wrong status)

The last one is commonly skipped and commonly where real-world failures happen.

---

## Skill Body Discipline

### Length budget
- Under 300 lines: lean, fast to load, easy to follow
- 300–500 lines: acceptable for complex orchestration skills
- Over 500 lines: split into SKILL.md + reference files; keep the body as a decision tree with pointers

### What belongs in the skill body vs reference files
| In SKILL.md | In references/ |
|---|---|
| Decision rules and protocols | Full JSON schemas |
| Routing tables | File path constants |
| Step-by-step procedures | Rate cards and pricing |
| Error handling guidance | Hook script templates |

### Comment discipline
Explain *why* rules exist, not what they are. A routing rule that says "use Haiku for targeted fixes" is less useful than one that explains "Haiku costs 3–4× less per token and is reliable for formulaic changes where the location is already known — the cost saving compounds across many small tasks."

---

## Known Systematic Biases (document in every tracking skill)

These biases are structural — they can be reduced but not eliminated. Document them so users interpret token logs correctly:

1. **Input underestimate**: conversation history growth means later tasks cost more than pre-computed estimates
2. **Output underestimate**: retries and corrections generate 1.5–3× estimated output on average
3. **Baseline drift**: as rules files and CLAUDE.md grow, the baseline increases — re-measure quarterly or after major additions
4. **Skill load not in task estimates**: unless the skill body cost is added to the baseline, it appears as unexplained overhead
```

State: "Destination: `~/.claude/skills/skill-design-guardrails/SKILL.md` (new file). Enhancement: `model: haiku` frontmatter added. Risk: LOW. Reversible: delete directory. Awaiting approval."

- [ ] **Step 4.2: WAIT — do not proceed until Tarun confirms**

- [ ] **Step 4.3: SNAPSHOT — write registry entry**

Append to `MIGRATION_REGISTRY.md` with status `in_progress`. Update `migration-state.json`: `skill-design-guardrails-skill-md` → `"in_progress"`.

- [ ] **Step 4.4: WRITE — create skill**

```bash
mkdir -p ~/.claude/skills/skill-design-guardrails
```

Write exactly the content shown in Step 4.1 to `/Users/home/.claude/skills/skill-design-guardrails/SKILL.md`.

- [ ] **Step 4.5: CONFIRM**

```bash
head -5 ~/.claude/skills/skill-design-guardrails/SKILL.md
grep "model: haiku" ~/.claude/skills/skill-design-guardrails/SKILL.md
```

Expected: frontmatter block at top, `model: haiku` present.

- [ ] **Step 4.6: LOG — update registry and state to completed**

---

## Task 5: Phase 1d — Install workspace-status and global commands

**Files:**
- Create: `~/.claude/commands/workspace-status.md`
- Create: `~/.claude/commands/new-session.md`
- Create: `~/.claude/commands/close-session.md`
- Create: `~/.claude/commands/log-learnings.md`

**Model:** Haiku — single directory, path substitutions, no judgment.

**Important:** `~/.claude/commands/` does not exist yet — needs `mkdir`. The project-level GSI commands at `.claude/commands/` are more specific and take precedence in the GSI workspace. The global versions here serve the Agentic Apps workspace (and any other workspace without project-level overrides).

---

- [ ] **Step 5.1: SHOW — present workspace-status.md to Tarun**

Display the following content (paths corrected from source) and await approval:

```markdown
# /workspace-status

Cross-workspace snapshot. All bash — no file reads.

## Steps

```bash
AA="/Users/home/Agentic Tools - Projects/agentic-operations"
GSI="/Users/home/Agentic Tools - Projects/stock-intelligence-test-1-vs"

echo "=== Agentic Applications ==="
git -C "$AA" log --oneline -3 2>/dev/null
stat -f "graph.json: %Sm" -t "%Y-%m-%d" "$AA/graphify-out/graph.json" 2>/dev/null
tail -4 "$AA/DAILY_ROUNDTABLE_LOG.md" 2>/dev/null

echo "=== GSI Dashboard ==="
[ -d "$GSI" ] && \
  jq -r '"v\(.current_version) | \(.session_date // "date unknown") | regression: \(.last_regression_result // "unknown")"' \
  "$GSI/GSI_session_updated.json" 2>/dev/null || echo "GSI not on this machine"
[ -d "$GSI/.claude" ] && echo ".claude/ exists" || echo ".claude/ MISSING (F3 pending)"

echo "=== Global ==="
ls ~/.claude/commands/ | wc -l | xargs echo "commands:"
ls ~/.claude/skills/   | wc -l | xargs echo "skills:"
cat ~/.claude/scheduled_tasks.json 2>/dev/null | jq '[.[]|.description] | join(", ")' || echo "no active crons"
```

## Report format
```
WORKSPACE STATUS — [date]

Agentic Applications:
  Git    : [hash + message]
  Graph  : last built [date]
  Cron   : [last round-table entry]

GSI Dashboard:
  Version: [v5.xx]  Last session: [date]  Regression: [result]
  .claude/: [exists / MISSING]

Global:
  Commands: N  Skills: N  Crons: [descriptions]
```

**Token budget:** ~200 tokens total (pure bash output, no file reads).
```

State: "Destination: `~/.claude/commands/workspace-status.md` (new file + new directory). Paths corrected: `/Users/tarunkochhar/...` → `/Users/home/...`. Risk: LOW. Reversible: delete file. Awaiting approval."

- [ ] **Step 5.2: WAIT — do not proceed until Tarun confirms**

- [ ] **Step 5.3: SHOW — present new-session.md (global version) to Tarun**

Display the following content (memory paths corrected for this device) and await approval:

```markdown
# /new-session

Orient for a new working session. Fast — bash for state, files only when bash can't answer.

## Steps

### 1. Identify workspace (bash — no file read)
```bash
pwd && git log --oneline -3 2>/dev/null || echo "no git"
```

### 2. Load state — bash first, then 2 targeted memory reads

**Agentic Applications workspace:**
```bash
# Graph freshness — one stat, not GRAPH_REPORT.md
stat -f "%Sm — %N" -t "%Y-%m-%d" graphify-out/graph.json 2>/dev/null || echo "graph.json missing"
# Last round-table entry
tail -8 DAILY_ROUNDTABLE_LOG.md 2>/dev/null || echo "(no round-table log yet)"
```
Then read **one** memory file: `~/.claude/projects/-Users-home-Agentic-Tools---Projects-agentic-operations/memory/project_workspace_merge.md`
→ This gives current work state, pending queue, and next actions. Load others only if the task needs them.

**GSI workspace:**
```bash
# Targeted extraction — not full file read
jq '{version:.current_version, last_session:.session_date, open_items:(.open_items|length), regression:.last_regression_result}' GSI_session_updated.json 2>/dev/null
# Regression
python regression.py 2>&1 | tail -3
```
Then read **one** memory file: `~/.claude/projects/-Users-home-Agentic-Tools---Projects-stock-intelligence-test-1-vs/memory/project_merge_state.md`

**Any workspace:** MEMORY.md index is already in context — do not re-read it. Load additional memory files only if the specific task requires them.

### 3. Report
```
SESSION START — [workspace] — [date]
Last commit : [hash + message]
Graph/State : [graph age OR GSI version]
Round-table : [last entry date + top finding, or NONE]
Open items  : [count + top priority item]
Ready       : YES / NO
```

### 4. Confirm before starting work.

### 5. Cron guard — Agentic Applications workspace only

Check if the daily round-table cron is active:
- Run CronList.
- If a job matching "Round-Table" or "round-table" is present: note its ID in the session report. Done.
- If missing: recreate it with CronCreate using these exact settings:
  - cron: `0 14 * * *`
  - durable: true
  - recurring: true
  - prompt: (use the CRON PROMPT template below, substituting WORKSPACE_ROOT with the result of `pwd`)

**CRON PROMPT TEMPLATE:**
```
DAILY ROUND-TABLE GATE — run silently, no preamble.

WORKSPACE_ROOT: [INSERT pwd RESULT HERE]

Step 1 — Network check:
Run: ping -c1 -W2 8.8.8.8 2>/dev/null && echo ONLINE || echo OFFLINE
If OFFLINE: send PushNotification "Round-table skipped — no network." Stop.

Step 2 — Notify and request approval:
Send PushNotification "Round-table ready. Open Claude Code to approve or skip."
Display this message exactly, then wait for response:

"DAILY ROUND-TABLE — [today's date] — Network: ONLINE
Token budget: confirm you have capacity before approving.
Type YES to run all 3 participants · NO to skip today."

Step 3 — On NO or no response: append "## [today's date] — SKIPPED by user" to [WORKSPACE_ROOT]/DAILY_ROUNDTABLE_LOG.md and stop.

Step 4 — On YES: cd to [WORKSPACE_ROOT], then read [WORKSPACE_ROOT]/global-config/roundtable-prompt.md and execute every instruction in it exactly as written.
```

---
**Token budget:** ~5,500 tokens total (baseline 4,400 + ~1,100 reads).
Do NOT read WORKSPACE.md, GRAPH_REPORT.md, or full GSI_session_updated.json at session start.
Load those on demand when a task actually requires them.
```

State: "Destination: `~/.claude/commands/new-session.md` (global version — project-level GSI version at `.claude/commands/new-session.md` takes precedence in the GSI workspace). Memory paths corrected for this device. Risk: LOW. Reversible: delete file. Awaiting approval."

- [ ] **Step 5.4: WAIT — do not proceed until Tarun confirms**

- [ ] **Step 5.5: SHOW — present close-session.md (global version) to Tarun**

Display the following content (generic/global version — no path corrections needed) and await approval:

```markdown
# /close-session

Close the current working session cleanly. Run this before ending any session.

## Steps

1. **Run final regression / health check:**
   - GSI: `python regression.py` — record result.
   - Agentic Apps: confirm no broken files, graph.json is current.

2. **Update session state:**
   - GSI: update `GSI_session_updated.json` in the project root with: session_id, date, activities completed, new open items, file versions changed, regression result. Commit and push this file with the rest of the session changes — it is the session manifest, no Gist.
   - Agentic Apps: append a brief entry to `DAILY_ROUNDTABLE_LOG.md` if work was done.

3. **Commit and push:**
   - Stage changed files. Write a clear commit message (what changed and why).
   - `git push` to the active repo.

4. **Snapshot memory** — update any memory files in `~/.claude/projects/<project-path>/memory/` that have new information from this session.

5. **Report session close state:**
   ```
   SESSION CLOSE — [workspace name] — [date]
   Version shipped: [version]
   Regression: [N/N PASS]
   Committed: [list of files]
   Open items remaining: [count]
   Handoff note: [one sentence — what to pick up next session]
   ```
```

State: "Destination: `~/.claude/commands/close-session.md` (global generic version — GSI project-level version at `.claude/commands/close-session.md` is more advanced and takes precedence in the GSI workspace). Risk: LOW. Reversible: delete file. Awaiting approval."

- [ ] **Step 5.6: WAIT — do not proceed until Tarun confirms**

- [ ] **Step 5.7: SHOW — present log-learnings.md (global version) to Tarun**

Display the following content and await approval:

```markdown
# /log-learnings

Log a non-obvious learning, decision, or feedback from the current session to memory. Use this whenever something surprising happened, a rule was confirmed, or Tarun corrected an approach.

## Steps

1. **Identify the learning type:**
   - `feedback` — Tarun corrected or confirmed an approach
   - `project` — new fact about the project state or a decision made
   - `user` — new understanding of how Tarun works or what he prefers
   - `reference` — a new external resource or URL to remember

2. **Write the memory file** to `~/.claude/projects/<project-path>/memory/<type>_<topic>.md` using the standard frontmatter format:
   ```
   ---
   name: [descriptive name]
   description: [one line — used for relevance matching in future sessions]
   type: [feedback | project | user | reference]
   ---

   [The learning itself. For feedback/project: lead with the rule/fact, then Why: and How to apply: lines.]
   ```

3. **Update MEMORY.md index** — add a one-line pointer to the new file.

4. **Confirm** with: `Logged: [memory name] → [file path]`
```

State: "Destination: `~/.claude/commands/log-learnings.md` (global generic version — GSI project-level version at `.claude/commands/log-learnings.md` is more advanced and takes precedence in the GSI workspace). Risk: LOW. Reversible: delete file. Awaiting approval."

- [ ] **Step 5.8: WAIT — do not proceed until Tarun confirms**

- [ ] **Step 5.9: WRITE — create all four commands**

```bash
mkdir -p ~/.claude/commands
```

Write each file to `~/.claude/commands/`:
1. `workspace-status.md` — content from Step 5.1
2. `new-session.md` — content from Step 5.3
3. `close-session.md` — content from Step 5.5
4. `log-learnings.md` — content from Step 5.7

- [ ] **Step 5.10: CONFIRM — verify all four commands installed**

```bash
ls ~/.claude/commands/
grep "Users/home" ~/.claude/commands/workspace-status.md
grep "tarunkochhar" ~/.claude/commands/workspace-status.md
grep "Users/home" ~/.claude/commands/new-session.md
grep "tarunkochhar" ~/.claude/commands/new-session.md
```

Expected:
- `ls` shows all 4 files
- Both `grep "Users/home"` return results
- Both `grep "tarunkochhar"` return NO output

- [ ] **Step 5.11: LOG — update registry and state for all 4 commands to completed**

---

## Task 6: Phase 2 — Correct bootstrap.sh Paths

**Files:**
- Modify: `agentic-operations/global-config/bootstrap.sh` (lines 250–252 only)

**Model:** Haiku — 3-line substitution, mechanical.

---

- [ ] **Step 6.1: SNAPSHOT — write pre-change snapshot**

```bash
cp "/Users/home/Agentic Tools - Projects/agentic-operations/global-config/bootstrap.sh" \
   "/Users/home/Agentic Tools - Projects/agentic-operations/backups/snapshots/2026-05-02-bootstrap-sh.bak"
```

Verify:
```bash
ls "/Users/home/Agentic Tools - Projects/agentic-operations/backups/snapshots/"
```

- [ ] **Step 6.2: SHOW — present the diff to Tarun**

Display this diff and await approval:

```diff
--- a/global-config/bootstrap.sh
+++ b/global-config/bootstrap.sh
@@ -250,7 +250,7 @@
-install_memory "$SCRIPT_DIR/memory/agentic-apps"    "$CLAUDE_DIR/projects/-Users-tarunkochhar-Agentic-Applications---Build/memory"                        "Agentic Apps"
-install_memory "$SCRIPT_DIR/memory/gsi"             "$CLAUDE_DIR/projects/-Users-tarunkochhar-Desktop-stock-intelligence-test-1-vs/memory"                "GSI Dashboard"
-install_memory "$SCRIPT_DIR/memory/crochet-counter" "$CLAUDE_DIR/projects/-Users-tarunkochhar-Agentic-Applications---Build-Crochet-Counter/memory"        "Crochet Counter"
+install_memory "$SCRIPT_DIR/memory/agentic-apps"    "$CLAUDE_DIR/projects/-Users-home-Agentic-Tools---Projects-agentic-operations/memory"                 "Agentic Apps"
+install_memory "$SCRIPT_DIR/memory/gsi"             "$CLAUDE_DIR/projects/-Users-home-Agentic-Tools---Projects-stock-intelligence-test-1-vs/memory"       "GSI Dashboard"
+install_memory "$SCRIPT_DIR/memory/crochet-counter" "$CLAUDE_DIR/projects/-Users-home-Agentic-Tools---Projects-Crochet-Counter/memory"                   "Crochet Counter"
```

State: "This corrects the memory install paths for this device. Crochet Counter path updated to match the encoding scheme even though the project is not present on this device — bootstrap.sh handles missing directories gracefully. Risk: LOW. Snapshot saved. Awaiting approval."

- [ ] **Step 6.3: WAIT — do not proceed until Tarun confirms**

- [ ] **Step 6.4: WRITE — apply the 3-line correction**

Read the full bootstrap.sh, then use Edit tool with the exact old/new strings from the diff above.

- [ ] **Step 6.5: CONFIRM**

```bash
grep "tarunkochhar" "/Users/home/Agentic Tools - Projects/agentic-operations/global-config/bootstrap.sh"
grep "Users/home" "/Users/home/Agentic Tools - Projects/agentic-operations/global-config/bootstrap.sh"
```

Expected:
- `grep "tarunkochhar"` returns NO output
- `grep "Users/home"` returns the 3 corrected lines

- [ ] **Step 6.6: LOG — update registry and state to completed**

---

## Task 7: Phase 2 — Statusline Decision Gate

**Files:**
- None unless Tarun chooses option (b)

**Model:** N/A — decision gate only.

---

- [ ] **Step 7.1: SHOW — present decision to Tarun**

Display:

> **Statusline decision required.**
>
> The `global-config/statusline-command.sh` bash script exists in source but conflicts with your active `claude-hud` Node.js plugin (currently configured in `~/.claude/settings.json` as `statusLine`).
>
> **Option (a):** Leave it in the source repo only — no action, no install. Use it as reference if you ever want to switch.
>
> **Option (b):** Install it to `~/.claude/statusline-command.sh` without activating — available on disk but not wired into settings.json. Switching would require a manual settings.json edit.
>
> **Option (c):** This is a separate deliberate decision — not part of this migration. Defer entirely.
>
> Which option?

- [ ] **Step 7.2: WAIT — do not proceed until Tarun responds**

- [ ] **Step 7.3: Execute chosen option**

- If (a) or (c): update `migration-state.json` → `statusline-decision` status: `"completed"`, action: `"skip"`. No file writes.
- If (b): SHOW full file content → WAIT → SNAPSHOT → WRITE to `~/.claude/statusline-command.sh` → CONFIRM → LOG.

---

## Task 8: Phase 3 — Registry.json Path Fix

**Files:**
- Modify: `agentic-operations/.claude/registry.json` (line 8 only)

**Model:** Haiku — single-line JSON value substitution.

---

- [ ] **Step 8.1: SNAPSHOT**

```bash
cp "/Users/home/Agentic Tools - Projects/agentic-operations/.claude/registry.json" \
   "/Users/home/Agentic Tools - Projects/agentic-operations/backups/snapshots/2026-05-02-registry-json.bak"
```

- [ ] **Step 8.2: SHOW — present diff to Tarun**

```diff
--- a/.claude/registry.json
+++ b/.claude/registry.json
@@ -8 +8 @@
-  "memory_path": "/Users/tarunkochhar/.claude/projects/-Users-tarunkochhar-Agentic-Applications---Build/memory",
+  "memory_path": "/Users/home/.claude/projects/-Users-home-Agentic-Tools---Projects-agentic-operations/memory",
```

State: "Corrects the memory path to this device's Claude Code project encoding. Risk: LOW. Snapshot saved. Awaiting approval."

- [ ] **Step 8.3: WAIT — do not proceed until Tarun confirms**

- [ ] **Step 8.4: WRITE — apply correction**

Read `registry.json`, then use Edit tool with the exact old/new strings from the diff above.

- [ ] **Step 8.5: CONFIRM**

```bash
grep "memory_path" "/Users/home/Agentic Tools - Projects/agentic-operations/.claude/registry.json"
```

Expected: `/Users/home/.claude/projects/-Users-home-Agentic-Tools---Projects-agentic-operations/memory`

- [ ] **Step 8.6: LOG — update registry and state to completed**

---

## Task 9: Phase 3 — Action Plan Housekeeping

**Files:**
- Modify: `agentic-operations/WORKSPACE_MERGE_ACTION_PLAN.md` (mark completed items DONE)
- Modify: `agentic-operations/migration-state.json` (close session)

**Model:** Haiku — status field updates, no judgment.

---

- [ ] **Step 9.1: Read current action plan**

```bash
cat "/Users/home/Agentic Tools - Projects/agentic-operations/WORKSPACE_MERGE_ACTION_PLAN.md"
```

- [ ] **Step 9.2: SHOW — present proposed status updates to Tarun**

Display which items you plan to mark as DONE:
- F3 (GSI_CONTEXT.md) — DONE on this device (confirmed at session start)
- F4 (GSI_session.json) — DONE on this device (confirmed at session start)
- G3 (quant_audit_pending state) — DONE on this device (confirmed at session start)
- All Phase 0–2 migration items completed in this plan

Await confirmation.

- [ ] **Step 9.3: WAIT — do not proceed until Tarun confirms**

- [ ] **Step 9.4: WRITE — update action plan**

Read the action plan, then use Edit tool to mark the confirmed items as DONE with the date `2026-05-02`.

- [ ] **Step 9.5: WRITE — close migration-state.json**

Edit `migration-state.json`:
- Set `"session_closed": "2026-05-02"`
- Set `"phase": "3"`
- All items that were completed: set `"status": "completed"` (should all be done by this point)

- [ ] **Step 9.6: CONFIRM**

```bash
grep "session_closed" "/Users/home/Agentic Tools - Projects/agentic-operations/migration-state.json"
```

Expected: `"session_closed": "2026-05-02"`

- [ ] **Step 9.7: Commit all Phase 3 changes**

```bash
cd "/Users/home/Agentic Tools - Projects/agentic-operations"
git add .claude/registry.json WORKSPACE_MERGE_ACTION_PLAN.md migration-state.json MIGRATION_REGISTRY.md
git commit -m "feat(migration): Phase 3 complete — path corrections, action plan updates, registry closed"
```

---

## Task 10: Final Verification

**Files:** None — read-only verification.

---

- [ ] **Step 10.1: Run GSI regression baseline**

```bash
cd "/Users/home/Agentic Tools - Projects/stock-intelligence-test-1-vs"
python3 regression.py
```

Expected: same pass count as before migration (451/451 or current baseline). Migration touched no GSI source code — any regression failure is a pre-existing issue, not caused by this migration.

- [ ] **Step 10.2: Run compliance check**

```bash
python3 compliance_check.py
```

Expected: all checks pass. Migration touched no GSI source files.

- [ ] **Step 10.3: Verify ~/.claude/ structure**

```bash
find ~/.claude -type f | sort
```

Expected output includes:
```
/Users/home/.claude/CLAUDE.md
/Users/home/.claude/commands/close-session.md
/Users/home/.claude/commands/log-learnings.md
/Users/home/.claude/commands/new-session.md
/Users/home/.claude/commands/workspace-status.md
/Users/home/.claude/skills/skill-design-guardrails/SKILL.md
/Users/home/.claude/skills/token-tracker/SKILL.md
/Users/home/.claude/skills/token-tracker/token-model-rules.md
```

- [ ] **Step 10.4: Verify no tarunkochhar paths remain in installed files**

```bash
grep -r "tarunkochhar" ~/.claude/
```

Expected: NO output. Any match is a missed path correction — fix before declaring migration complete.

- [ ] **Step 10.5: Spot-check model frontmatter on both skills**

```bash
grep "model:" ~/.claude/skills/token-tracker/SKILL.md
grep "model:" ~/.claude/skills/skill-design-guardrails/SKILL.md
```

Expected: `model: haiku` in both.

- [ ] **Step 10.6: Commit final verification state to GSI repo**

```bash
cd "/Users/home/Agentic Tools - Projects/stock-intelligence-test-1-vs"
git add docs/superpowers/specs/2026-05-02-workspace-migration-design.md \
         docs/superpowers/plans/2026-05-02-workspace-migration.md
git commit -m "docs: workspace migration spec + implementation plan"
```

---

## Task 11: Phase 4 — Environment Snapshot for Cross-Device Validation

**Files:**
- Create dir: `agentic-operations/environment-snapshots/home-device-2026-05-02/`
- Create: `README.md`, `environment.md`, `migration-state-final.json`, `verify.sh`, `verify-output.txt`

**Purpose:** Once migration is complete, capture a full static snapshot of `~/.claude/` and the corrected source files so the other workspace (Agentic Apps device) can point at this folder and confirm the migration was applied correctly. `verify.sh` is designed to run on any device — it exits 0 on PASS, non-zero on FAIL.

**Model:** Haiku — bash script generation + file listing, no judgment.

---

- [ ] **Step 11.1: Create snapshot directory**

```bash
mkdir -p "/Users/home/Agentic Tools - Projects/agentic-operations/environment-snapshots/home-device-2026-05-02"
```

- [ ] **Step 11.2: Capture environment.md — full ~/.claude/ state manifest**

Run these commands and collect all output:

```bash
echo "=== ~/.claude/ FILE TREE ===" && find ~/.claude -type f | sort
echo ""
echo "=== ~/.claude/CLAUDE.md ===" && cat ~/.claude/CLAUDE.md
echo ""
echo "=== ~/.claude/skills/token-tracker/SKILL.md (first 10 lines) ===" && head -10 ~/.claude/skills/token-tracker/SKILL.md
echo ""
echo "=== ~/.claude/skills/skill-design-guardrails/SKILL.md (first 10 lines) ===" && head -10 ~/.claude/skills/skill-design-guardrails/SKILL.md
echo ""
echo "=== ~/.claude/commands/ FILE LIST ===" && ls -la ~/.claude/commands/
echo ""
echo "=== NO tarunkochhar PATHS CHECK ===" && grep -r "tarunkochhar" ~/.claude/ && echo "FAIL: paths found" || echo "PASS: no stale paths"
echo ""
echo "=== model: haiku CHECK ===" && grep "model:" ~/.claude/skills/token-tracker/SKILL.md && grep "model:" ~/.claude/skills/skill-design-guardrails/SKILL.md
echo ""
echo "=== bootstrap.sh MEMORY PATHS ===" && sed -n '250,252p' "/Users/home/Agentic Tools - Projects/agentic-operations/global-config/bootstrap.sh"
echo ""
echo "=== registry.json memory_path ===" && grep "memory_path" "/Users/home/Agentic Tools - Projects/agentic-operations/.claude/registry.json"
echo ""
echo "=== GSI REGRESSION ===" && cd "/Users/home/Agentic Tools - Projects/stock-intelligence-test-1-vs" && python3 regression.py 2>&1 | tail -3
```

Write the complete output as the body of `environment.md` under a header block:

```markdown
# Environment Snapshot — home device
# Captured: 2026-05-02
# Migration: Phases 0–3 complete
# Purpose: Cross-device validation reference

[paste full bash output here]
```

Write to: `agentic-operations/environment-snapshots/home-device-2026-05-02/environment.md`

- [ ] **Step 11.3: Copy final migration-state.json**

```bash
cp "/Users/home/Agentic Tools - Projects/agentic-operations/migration-state.json" \
   "/Users/home/Agentic Tools - Projects/agentic-operations/environment-snapshots/home-device-2026-05-02/migration-state-final.json"
```

- [ ] **Step 11.4: Write verify.sh**

Write the following script to `agentic-operations/environment-snapshots/home-device-2026-05-02/verify.sh`:

```bash
#!/bin/bash
# verify.sh — validate Claude Code global environment after workspace migration
# Run from any device: bash verify.sh
# Exit 0 = PASS. Exit 1 = FAIL (details printed).
# Expected state: home device migration 2026-05-02

PASS=0
FAIL=0
RESULTS=()

check() {
  local desc="$1"
  local result="$2"  # "pass" or "fail"
  local detail="$3"
  if [ "$result" = "pass" ]; then
    PASS=$((PASS+1))
    RESULTS+=("  PASS  $desc")
  else
    FAIL=$((FAIL+1))
    RESULTS+=("  FAIL  $desc — $detail")
  fi
}

CLAUDE="$HOME/.claude"

# C01 — ~/.claude/CLAUDE.md exists
[ -f "$CLAUDE/CLAUDE.md" ] \
  && check "C01 ~/.claude/CLAUDE.md exists" "pass" "" \
  || check "C01 ~/.claude/CLAUDE.md exists" "fail" "file missing"

# C02 — CLAUDE.md contains no tarunkochhar paths
[ -f "$CLAUDE/CLAUDE.md" ] && ! grep -q "tarunkochhar" "$CLAUDE/CLAUDE.md" \
  && check "C02 CLAUDE.md has no stale paths" "pass" "" \
  || check "C02 CLAUDE.md has no stale paths" "fail" "tarunkochhar found in CLAUDE.md"

# C03 — CLAUDE.md contains /Users/home paths
grep -q "Users/home" "$CLAUDE/CLAUDE.md" 2>/dev/null \
  && check "C03 CLAUDE.md has correct device paths" "pass" "" \
  || check "C03 CLAUDE.md has correct device paths" "fail" "/Users/home not found in CLAUDE.md"

# C04 — token-tracker skill exists
[ -f "$CLAUDE/skills/token-tracker/SKILL.md" ] \
  && check "C04 token-tracker/SKILL.md exists" "pass" "" \
  || check "C04 token-tracker/SKILL.md exists" "fail" "file missing"

# C05 — token-tracker has model: haiku frontmatter
grep -q "model: haiku" "$CLAUDE/skills/token-tracker/SKILL.md" 2>/dev/null \
  && check "C05 token-tracker has model: haiku" "pass" "" \
  || check "C05 token-tracker has model: haiku" "fail" "model: haiku not found in frontmatter"

# C06 — token-model-rules.md exists
[ -f "$CLAUDE/skills/token-tracker/token-model-rules.md" ] \
  && check "C06 token-model-rules.md exists" "pass" "" \
  || check "C06 token-model-rules.md exists" "fail" "file missing"

# C07 — skill-design-guardrails exists
[ -f "$CLAUDE/skills/skill-design-guardrails/SKILL.md" ] \
  && check "C07 skill-design-guardrails/SKILL.md exists" "pass" "" \
  || check "C07 skill-design-guardrails/SKILL.md exists" "fail" "file missing"

# C08 — skill-design-guardrails has model: haiku frontmatter
grep -q "model: haiku" "$CLAUDE/skills/skill-design-guardrails/SKILL.md" 2>/dev/null \
  && check "C08 skill-design-guardrails has model: haiku" "pass" "" \
  || check "C08 skill-design-guardrails has model: haiku" "fail" "model: haiku not found in frontmatter"

# C09 — workspace-status command exists
[ -f "$CLAUDE/commands/workspace-status.md" ] \
  && check "C09 commands/workspace-status.md exists" "pass" "" \
  || check "C09 commands/workspace-status.md exists" "fail" "file missing"

# C10 — new-session command exists
[ -f "$CLAUDE/commands/new-session.md" ] \
  && check "C10 commands/new-session.md exists" "pass" "" \
  || check "C10 commands/new-session.md exists" "fail" "file missing"

# C11 — close-session command exists
[ -f "$CLAUDE/commands/close-session.md" ] \
  && check "C11 commands/close-session.md exists" "pass" "" \
  || check "C11 commands/close-session.md exists" "fail" "file missing"

# C12 — log-learnings command exists
[ -f "$CLAUDE/commands/log-learnings.md" ] \
  && check "C12 commands/log-learnings.md exists" "pass" "" \
  || check "C12 commands/log-learnings.md exists" "fail" "file missing"

# C13 — no tarunkochhar paths anywhere in ~/.claude/
! grep -rq "tarunkochhar" "$CLAUDE/" 2>/dev/null \
  && check "C13 no stale tarunkochhar paths in ~/.claude/" "pass" "" \
  || check "C13 no stale tarunkochhar paths in ~/.claude/" "fail" "run: grep -r tarunkochhar ~/.claude/"

# C14 — workspace-status.md has correct device path (Users/home)
grep -q "Users/home" "$CLAUDE/commands/workspace-status.md" 2>/dev/null \
  && check "C14 workspace-status.md has correct device paths" "pass" "" \
  || check "C14 workspace-status.md has correct device paths" "fail" "/Users/home not found in workspace-status.md"

# C15 — new-session.md has correct memory path (Users/home)
grep -q "Users/home" "$CLAUDE/commands/new-session.md" 2>/dev/null \
  && check "C15 new-session.md has correct memory paths" "pass" "" \
  || check "C15 new-session.md has correct memory paths" "fail" "/Users/home not found in new-session.md"

# C16 — bootstrap.sh path corrections applied (if file exists at expected location)
BOOTSTRAP="$(dirname "$0")/../../../../global-config/bootstrap.sh"
if [ -f "$BOOTSTRAP" ]; then
  ! grep -q "tarunkochhar" "$BOOTSTRAP" \
    && check "C16 bootstrap.sh has no stale paths" "pass" "" \
    || check "C16 bootstrap.sh has no stale paths" "fail" "tarunkochhar found in bootstrap.sh"
else
  check "C16 bootstrap.sh path check" "pass" "(skipped — file not found at expected relative path; check manually)"
fi

# C17 — registry.json memory_path corrected (if file exists)
REGISTRY="$(dirname "$0")/../../../../.claude/registry.json"
if [ -f "$REGISTRY" ]; then
  grep -q "Users/home" "$REGISTRY" \
    && check "C17 registry.json memory_path corrected" "pass" "" \
    || check "C17 registry.json memory_path corrected" "fail" "/Users/home not found in registry.json memory_path"
else
  check "C17 registry.json check" "pass" "(skipped — file not found at expected relative path; check manually)"
fi

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "VERIFY.SH — Migration Validation Report"
echo "Device:  $(hostname)"
echo "Date:    $(date +%Y-%m-%d)"
echo "Checks:  $((PASS+FAIL)) total — $PASS PASS, $FAIL FAIL"
echo "─────────────────────────────────────────"
for r in "${RESULTS[@]}"; do echo "$r"; done
echo "─────────────────────────────────────────"
if [ "$FAIL" -eq 0 ]; then
  echo "RESULT: ALL CHECKS PASS — migration verified"
  exit 0
else
  echo "RESULT: $FAIL CHECKS FAILED — review items above"
  exit 1
fi
```

Make it executable:
```bash
chmod +x "/Users/home/Agentic Tools - Projects/agentic-operations/environment-snapshots/home-device-2026-05-02/verify.sh"
```

- [ ] **Step 11.5: Run verify.sh and capture output**

```bash
bash "/Users/home/Agentic Tools - Projects/agentic-operations/environment-snapshots/home-device-2026-05-02/verify.sh"
```

Capture the full output. Write it verbatim to `verify-output.txt`:

```
# verify.sh output — home device — 2026-05-02
# Run immediately after migration completion

[paste full verify.sh output here]
```

Write to: `agentic-operations/environment-snapshots/home-device-2026-05-02/verify-output.txt`

If any check fails: fix the underlying issue, re-run, and update the output file before continuing.

- [ ] **Step 11.6: Write README.md**

Write the following to `agentic-operations/environment-snapshots/home-device-2026-05-02/README.md`:

```markdown
# Environment Snapshot — home device
**Date:** 2026-05-02
**Migration:** Phases 0–3 complete
**Verified:** See verify-output.txt

## What this folder contains

| File | Purpose |
|---|---|
| `README.md` | This file — index and usage guide |
| `environment.md` | Full ~/.claude/ state manifest captured after migration |
| `migration-state-final.json` | Final migration tracker (all items completed) |
| `verify.sh` | Runnable validation script — use on any device to check expected state |
| `verify-output.txt` | Output of verify.sh on this device — 17/17 PASS expected |

## How to use verify.sh on another device

From the agentic-operations repo root on the target device:

```bash
bash environment-snapshots/home-device-2026-05-02/verify.sh
```

Expected output: `RESULT: ALL CHECKS PASS — migration verified`

If checks fail, cross-reference with `environment.md` to see the exact state expected and compare to actual state on the target device.

## What was migrated

- `~/.claude/CLAUDE.md` — global operating rules (device paths corrected)
- `~/.claude/skills/token-tracker/` — token cost attribution skill (model: haiku added)
- `~/.claude/skills/skill-design-guardrails/` — skill design checklist (model: haiku added)
- `~/.claude/commands/workspace-status.md` — cross-workspace bash snapshot
- `~/.claude/commands/new-session.md` — global session start protocol
- `~/.claude/commands/close-session.md` — global session close protocol
- `~/.claude/commands/log-learnings.md` — global learning logger
- `global-config/bootstrap.sh` — memory install paths corrected (lines 250–252)
- `.claude/registry.json` — memory_path corrected for this device

## What was NOT migrated (and why)

| Item | Reason |
|---|---|
| `bootstrap.sh` (run) | Executed manually — approval-gated install replaced one-shot bootstrap |
| `statusline-command.sh` | Conflicts with active claude-hud plugin — separate decision required |
| `settings-template.json` | Reference document only |
| GSI project-level commands | More advanced versions already exist at `.claude/commands/` in GSI repo |
```

- [ ] **Step 11.7: Commit snapshot folder to agentic-operations**

```bash
cd "/Users/home/Agentic Tools - Projects/agentic-operations"
git add environment-snapshots/
git commit -m "feat(migration): Phase 4 — environment snapshot + verify.sh for cross-device validation"
git push
```

- [ ] **Step 11.8: Report verify.sh output to Tarun**

Print the full contents of `verify-output.txt` to the conversation so Tarun can see the final validation result inline.

---

## Rollback Reference

If any task fails after its SNAPSHOT step:

| Failed task | Snapshot file | Rollback action |
|---|---|---|
| Task 6 (bootstrap.sh) | `backups/snapshots/2026-05-02-bootstrap-sh.bak` | Copy snapshot back to `global-config/bootstrap.sh` |
| Task 8 (registry.json) | `backups/snapshots/2026-05-02-registry-json.bak` | Copy snapshot back to `.claude/registry.json` |
| Any `~/.claude/` file | No snapshot needed — all are new files | `rm` the file; directory structure can stay |
| MIGRATION_REGISTRY.md | No snapshot — Phase 0 bootstrap exception | `rm` the file if aborting migration entirely |

For any failed item: set status to `"failed"` in `migration-state.json`, append failure entry to `MIGRATION_REGISTRY.md` with reason, then surface to Tarun.
