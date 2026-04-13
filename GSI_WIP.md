# GSI Dashboard — Work in Progress
# ════════════════════════════════════════════════════════════════════════
#
# PURPOSE: This file is a mutex. It records exactly what is in flight
# in the current session so that if Claude hits a usage limit mid-session,
# the next Claude instance knows precisely where to resume — without
# duplicating completed work or skipping incomplete work.
#
# RULES:
# 1. Claude writes to this file FIRST before starting any implementation.
# 2. Claude updates this file as each task completes (tick the checkbox).
# 3. Claude writes a CHECKPOINT block before the session ends.
# 4. The next session reads this file BEFORE anything else.
# 5. If status is ACTIVE and a checkpoint exists, resume from checkpoint.
# 6. If status is IDLE, treat as a fresh session start.
#
# ════════════════════════════════════════════════════════════════════════

## Session Status

```
Status:        IDLE
Session ID:    session_026
Version:       v5.37.1
Last updated:  2026-04-14
Sprint:        v5.37 COMPLETE
Manifest:      GSI_SPRINT_MANIFEST.json (COMPLETE)
Next session:  session_027
```

## session_025 — Pre-Sprint Handoff (written end of session_024 extension)

### CHECKPOINT — 2026-04-13 (pre-session_025 handoff)

```
Status:               IDLE — clean start for session_025
Regression baseline:  436/436 PASS (confirmed 2026-04-13, commit fdd5c31)
Compliance:           n/a (no code changed since last compliance run)
Sprint state:         v5.37 PLANNING COMPLETE (3-sprint structure locked)
Last commit:          fdd5c31 — wire math skills to audit commands; confirm D3-01; RECORD-025
```

### Sprint Structure Decided (session_024 extended strategic review)

Three sub-sprints locked in order:

**v5.37a — Code Sprint (SEBI P0 + Quant P1)**
Priority: HIGHEST — blocks any public announcement
Items:
  - OPEN-029: SEBI caption in dashboard.py _render_header_static() after line 178
  - OPEN-027: SEBI caption in home.py _render_global_signals() after line 343
  - OPEN-022a: SEBI caption in week_summary.py Signal Summary tab (lines 649–679)
  - OPEN-022b: SEBI caption in week_summary.py Portfolio Allocator table (lines 956–968)
  - OPEN-028: SEBI caption + cached verdict per ticker in global_intelligence.py:60–90
  - QA-D3-01: indicators.py _calc_roe() — prefer returnOnEquity when available AND calc diverges >10pp
  - QA-D1-01: indicators.py RSI — switch rolling(14).mean() → ewm(com=13, adjust=False) with SMA seed
  - QA-D1-02: indicators.py ATR — same Wilder's RMA switch, batch with QA-D1-01
Model plan: Sonnet sequential, est ~50–55k tokens, Playwright for all UI items

**v5.37b — Governance + Wiring Sprint (Doc + Config — parallel agents)**
Priority: HIGH — closes token governance and social skill wiring gaps
Items (4 worktree tracks):
  Track A: Token budget Execution Contract header → new-feature.md, quant-reviewer.md,
            signal-accuracy-audit.md, qa-brief.md, sprint-review.md
  Track B: Process orchestration → skill-creator.md (wiring quality gate),
            new-session.md (unplanned dispatch guard), sprint-review.md (token retrospective)
  Track C: Social/brand skill wiring → launch-checklist.md (accessibility + canvas-design),
            gsi-brand.md (→ canvas-design), campaign.md + marketing.md (→ newsletter)
  Track D: Quick code fixes → OPEN-023 (litellm model name), OPEN-001/005 (git rm config_OLD.py),
            QA-D2-04 (veto_applied flag), OPEN-025 (UNSTABLE boundary text align), HOOK-01, PROXY-08
Model plan: Track A/B/C → Haiku worktrees (doc-only, ~8–12k each); Track D → Sonnet (touches .py)

**v5.37c — GTM + Brand Execution**
Priority: MEDIUM — launch readiness, not blocking code correctness
Items: visual assets via /canvas-design, content calendar via /content-calendar,
       newsletter via /newsletter, Zerodha Streak competitive analysis,
       LinkedIn channel addition, psychographics layer for 3 personas,
       accessibility audit via /accessibility

### Key Decisions Made (session_024 extension)

1. EXECUTION ORDER: 5.37b BEFORE 5.37a. Reasoning: app is not publicly announced yet;
   no live user exposure to SEBI gaps. Wiring token governance first means 5.37a sprint
   runs cleaner and cheaper. Exception: if CEO announces public beta, flip order immediately.

2. TOKEN GOVERNANCE: All process skill files need an "Execution Contract" header block
   (model, model_rationale, mode, agents, est_tokens, permissions_required, read_avoidance,
   sprint_gate). None of the 7 audited skills currently declare this. Rule: Haiku-first default;
   justify Sonnet in writing; Opus only for architecture decisions.

3. SKILL WIRING QUALITY GATE: skill-creator.md must require that every new skill be wired
   into at least one process file before close, OR explicitly documented as "invoked manually only."
   Root cause: accessibility.md and newsletter skill were both orphaned at creation time.

4. GTM GAPS: Zerodha Streak is the primary competitor for Ritu persona — not in competitive
   analysis. Newsletter channel orphaned from launch plan. LinkedIn missing for India fintech.
   /campaign orchestrator is otherwise complete.

5. NOTEBOOKLM/OBSIDIAN: Research agent dispatched (Haiku, background). Results will be
   in session notification. Read before deciding on tooling.

### Files Modified This Session (session_024 extension)

All committed in fdd5c31:
  - .claude/commands/quant-reviewer.md (math skill wiring)
  - .claude/commands/signal-accuracy-audit.md (math skill wiring + D4 file fix)
  - .claude/quant_audit_pending.json (cleared)
  - CLAUDE.md (Living Documentation + 3 new rows)
  - GSI_SESSION_LEARNINGS.md (RECORD-025)
  - GSI_SPRINT.md (QA-D3-01 CONFIRMED)
  - docs/audit-orchestration/status.json (D3 CEO validation)
  - docs/signal-accuracy-audit-v5.36-2026-04-13.md (D3 table updated)

### Resume Instruction for session_025

Read this file → run /new-session → confirm regression 436/436 →
start v5.37b sprint: open GSI_SPRINT_MANIFEST.json, set status IN_PROGRESS,
dispatch 4 worktree agents (Track A/B/C/D per plan above).
DO NOT start v5.37a code items until v5.37b doc wiring is complete.

---

## session_025 ADDENDUM — New Files + Tooling Strategy (end of session_024 ext)

### Two New Files in reports/ — MUST READ AT SESSION START

Both files placed by user in `reports/` folder. Read in session_025 before any implementation.

**File 1: reports/overview.md**
What it is: Anthropic's official Claude Managed Agents beta documentation.
Key facts:
  - Managed Agents = pre-built agent harness (Anthropic infra, not your own loop)
  - Four concepts: Agent (model+prompt+tools+skills) | Environment (container) | Session (running instance) | Events (SSE stream)
  - Supports: Bash, file ops, web search, MCP servers — same tools Claude Code has
  - Beta header required: managed-agents-2026-04-01
  - Research preview features: outcomes, multiagent, memory (need access request)
  - Rate limits: 60 create/min, 600 read/min
  
Relevance to GSI:
  - This is the API-level equivalent of what we do with worktree agents + Agent tool
  - Key opportunity: the "memory" research preview feature = persistent cross-session state
    (solves what OPEN-003 Supabase was going to solve for forecast_history)
  - The "outcomes" feature = defining success criteria for agent runs = our sprint manifest gate
  - The "multiagent" feature = what we're doing with parallel worktree agents, but managed
  
Action for session_025: Read full overview.md + add an ADR to GSI_DECISIONS.md evaluating
whether Managed Agents API replaces or complements our current worktree agent pattern.
This is a strategic architecture decision — use Opus judgment, document before building.

**File 2: reports/llm-wiki-claude-code-guide.html**
What it is: A how-to guide for building a personal knowledge wiki powered by Claude Code.
Structure (from heading scan):
  - CLAUDE.md as agent brain (tells Claude how to manage the wiki)
  - index.md + log.md as persistent state files
  - scripts/ingest.sh — drop any source file, Claude ingests it into structured wiki entries
  - scripts/lint.sh — wiki health check (coverage, staleness, broken links)
  - 3 modes: Ingest source | Ask a question | Lint the wiki
  - Patterns: Reading Queue, Daily Note, Pre-meeting Brief, Teach Me, Git backup

Relevance to GSI:
  - This IS the local alternative to NotebookLM — same Q&A + synthesis, fully private,
    git-backed, runs inside Claude Code (no external upload)
  - We already have the GSI knowledge base (25+ governance docs, audit trail, decisions,
    session learnings) — the LLM wiki pattern turns this into a queryable system
  - Key delta vs. current state: we have the files but no CLAUDE.md "wiki brain" instructing
    Claude how to manage, ingest, and query them as a unified knowledge base
  - The "lint" pattern maps to our regression.py — it's a health check but for knowledge,
    not code. Catches stale entries, orphaned topics, missing coverage.

Assessment: HIGH VALUE. Adopt this pattern. Implementation plan:
  1. Create docs/wiki/ subdirectory (separate from docs/ to avoid confusion with app docs)
  2. Create docs/wiki/WIKI_BRAIN.md — the agent instruction file (modeled on html guide)
  3. Create docs/wiki/index.md — topic registry (maps to GSI knowledge areas)
  4. Create docs/wiki/log.md — ingestion log
  5. Ingest order (priority): GSI_AUDIT_TRAIL.md → GSI_DECISIONS.md → GSI_SESSION_LEARNINGS.md
     → signal-accuracy-audit-v5.36.md → GSI_SKILLS.md
  6. Wire into new-session.md: after snapshot check, optionally query wiki for context
  7. Wire into sprint-review.md: after sprint close, ingest session learnings into wiki

### Tooling Strategy — Full Picture (session_024 conclusion)

THREE complementary tools, zero redundancy:

1. LLM Wiki (Claude Code, local) — PRIMARY knowledge system
   - Replaces NotebookLM for this project (same Q&A, private, git-backed, free)
   - Lives in docs/wiki/, managed by WIKI_BRAIN.md
   - When to use: "What did we learn about X?" "What decisions touch this file?"
   - Skill needed: create .claude/commands/wiki-query.md and wiki-ingest.md

2. Obsidian (local, free tier) — VISUALIZATION layer only
   - Point vault at repo root — instant graph of all governance docs + their links
   - Dataview plugin: query sprint items, decisions, audit findings by frontmatter
   - When to use: sprint planning (visual), decision archaeology, onboarding navigation
   - No new files needed — Obsidian reads existing repo markdown

3. Claude Code — BUILD layer (unchanged)
   - All code editing, regression, git, agent dispatch
   - The other two tools inform it; they do not replace it

NotebookLM: SKIP for this project. LLM wiki is strictly better (private, no sync friction,
same Q&A capability, already in your workflow). Use NotebookLM only if onboarding external
team members who don't have Claude Code access.

### Action Items for session_025 (ADDENDUM — priority after 5.37b)

New sprint items to add to GSI_SPRINT.md before starting session_025:

1. ADR-026: Claude Managed Agents evaluation — worktree vs. managed pattern
   (Opus judgment required, doc-only, add to 5.37b Track B alongside orchestration fixes)

⚠️  LLM-WIKI-01/02/03 below are SUPERSEDED by the Karpathy section further down.
    Use those revised definitions. Items 2–4 kept for reference only — do NOT execute as written.

2. [SUPERSEDED] LLM-WIKI-01: Create docs/wiki/ structure — see Karpathy section for full entity page list
3. [SUPERSEDED] LLM-WIKI-02: Initial ingest — see Karpathy section for revised priority order
4. [SUPERSEDED] LLM-WIKI-03: 3 skills needed (wiki-ingest + wiki-query + wiki-lint) — old plan only listed 2

5. OBSIDIAN-01: Document Obsidian vault setup in docs/tooling-setup.md
   (Haiku, doc-only — instructions for how to point Obsidian vault at repo + install Dataview)
   Wire into: new-session.md "Tools available" section

   → For LLM-WIKI-01/02/03 authoritative plan: read "Karpathy Gist" section below.

### Karpathy Gist — LLM Wiki (https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

This is the primary source for the LLM wiki pattern. Key insights that change our implementation plan:

**Core insight:** This is ANTI-RAG. Not "search then answer" — but a persistent, LLM-maintained wiki
that COMPOUNDS knowledge. Each ingest makes the whole more valuable through cross-references and
contradiction flagging. The wiki pre-digests everything so queries are instant and contextual.

**Karpathy's exact framing:** "The tedious part of maintaining a knowledge base is not the reading...
it's the bookkeeping." LLMs solve the maintenance burden that kills human-managed wikis.

**Three-layer architecture:**
  Layer 1 — Raw sources (immutable: audit reports, session learnings, sprint boards)
  Layer 2 — The wiki (LLM-generated markdown: entity pages, concept pages, summaries, comparisons)
  Layer 3 — The schema (WIKI_BRAIN.md / CLAUDE.md: defines structure, conventions, workflows)

**Three operations:**
  Ingest: source → extract takeaways → write summary page → update index → update entity/concept pages → log entry
  Query: question → search wiki → synthesize answer with citations → optionally file answer as new wiki page
  Lint: periodic health checks (contradictions, stale claims, orphan pages, missing cross-references)

**Key realisation for GSI:** We ALREADY HAVE most of this infrastructure:
  - Layer 3 (schema): CLAUDE.md Living Documentation table IS the schema
  - Layer 2 (logs): GSI_AUDIT_TRAIL.md + GSI_SESSION_LEARNINGS.md ARE append-only logs (log.md equivalent)
  - Layer 2 (index): CLAUDE.md Living Documentation table IS the index.md equivalent
  What we're MISSING: the ingestion workflow (we write to logs but don't synthesise entity/concept pages)
  and the lint operation (we have regression.py for code but nothing for knowledge health)

**Revised implementation plan (replaces LLM-WIKI items in addendum above):**
  LLM-WIKI-01: Create docs/wiki/ with WIKI_BRAIN.md schema, index.md, log.md
    → WIKI_BRAIN.md tells Claude: how to ingest, what entity pages to maintain, lint criteria
    → Entity pages to create: /wiki/indicators.md, /wiki/signals.md, /wiki/portfolio.md,
      /wiki/regulatory.md, /wiki/architecture.md, /wiki/sprint-history.md
    → CLAUDE.md Living Documentation table becomes the authoritative index pointer
    Model: Haiku (doc-only structure creation)

  LLM-WIKI-02: Initial ingest batch — priority order:
    1. GSI_AUDIT_TRAIL.md → creates /wiki/audit-findings.md with entity links
    2. GSI_DECISIONS.md → creates /wiki/decisions.md with cross-refs to affected files
    3. GSI_SESSION_LEARNINGS.md → creates /wiki/learnings.md with deviation/correction index
    4. signal-accuracy-audit-v5.36.md → updates /wiki/indicators.md + /wiki/signals.md
    Model: Sonnet (judgment needed for synthesis and cross-referencing)

  LLM-WIKI-03: Create two skills:
    .claude/commands/wiki-ingest.md — protocol for ingesting any new source
    .claude/commands/wiki-query.md — protocol for querying wiki with citation
    .claude/commands/wiki-lint.md — health check (contradictions, orphans, stale pages)
    Wire wiki-ingest into: log-learnings.md (after writing RECORD, ingest into wiki)
    Wire wiki-lint into: sprint-review.md (run as part of sprint close health check)
    Model: Haiku (doc-only skill creation)

  OBSIDIAN-01: Point Obsidian vault at repo root. Install Dataview plugin.
    The wiki pages in docs/wiki/ become Obsidian notes. Graph view shows all cross-links.
    Karpathy explicitly recommends Obsidian for browsing — confirms our tooling stack.
    No new files: Obsidian reads existing repo markdown. Document setup in docs/tooling-setup.md.

**What this means for our overall tooling stack (FINAL):**
  LLM Wiki (docs/wiki/) = knowledge layer — compounding, cross-linked, LLM-maintained
  Obsidian (vault = repo root) = visualization layer — graph, Dataview queries, browsing
  Claude Code = build layer — code, regression, git, agent dispatch, wiki maintenance
  NotebookLM = SKIP entirely (LLM wiki is strictly superior for our use case)

### Files NOT to read at session_025 start (read_avoidance)

These are large and already processed:
  - GSI_session.json (42k tokens — use meta block + open_items only via offset)
  - GSI_AUDIT_TRAIL.md (use Grep for specific findings, not full read)
  - GSI_SESSION_LEARNINGS.md (use tail -50 to get recent records only)
  - reports/llm-wiki-claude-code-guide.html (read this checkpoint instead — full analysis above)
  - reports/overview.md (read this checkpoint instead — full analysis above)

## session_024 — Quant Audit + Vercel Migration Research

### CHECKPOINT — 2026-04-13 session_024

```
Status:               ACTIVE (Phase 0 — skills creation in progress)
Regression baseline:  436/436 PASS (confirmed session start)
Compliance:           9/9 PASS (confirmed session start)
Sprint state:         v5.37 PLANNING — not yet IN_PROGRESS; audit must complete first

Currently working on: Phase 0 — creating/fixing 9 skill files
Last completed:       docs/quant-audit-execution-brief-2026-04-13.md written
                      docs/audit-orchestration/status.json created
                      docs/migration/ directory created

Completed (committed: NO — audit is pre-sprint, no commits until Phase 2):
  None yet — Phase 0 skill files being written

Phase 0 — Skills (all pending):
  - [ ] Fix .claude/commands/quant-reviewer.md (Gap 1: D4 wrong file)
  - [ ] Fix .claude/commands/signal-accuracy-audit.md (Gap 2+3: thresholds + RSI)
  - [ ] Create .claude/commands/quant-data-fetcher.md
  - [ ] Create .claude/commands/technical-indicators-math.md
  - [ ] Create .claude/commands/portfolio-risk-math.md
  - [ ] Create .claude/commands/forecasting-calibration-math.md
  - [ ] Create .claude/commands/fundamental-analysis-math.md

Phase 1 — Parallel agents (pending Phase 0):
  - [ ] D3: Main context — yfinance live fetch for INFY.NS, HDFCBANK.NS, RELIANCE.NS
  - [ ] D1+D2+D4+D5: Worktree Sonnet agent → docs/audit-orchestration/domain-findings-auto.md
  - [ ] Vercel migration: Worktree Sonnet agent → docs/migration/ (3 artifacts)

Phase 2 — Consolidation (pending Phase 1):
  - [ ] Write docs/signal-accuracy-audit-v5.36-2026-04-13.md
  - [ ] Raise sprint items in GSI_SPRINT.md
  - [ ] /log-learnings
  - [ ] Update quant_audit_pending.json

Key decisions made this session (add to GSI_DECISIONS.md at close):
  - Quant audit runs BEFORE v5.37 sprint execution (pre-sprint gate)
  - Vercel migration: Python stays Python (Fluid Compute), Next.js frontend
  - DurableAgent pattern for yfinance/portfolio/forecast long-running ops
  - v5.37 not blocked unless audit finds P0 defect
  - RSI/ATR Cutler's smoothing: expected P1 finding (not P0 — converges >100 bars)
  - OPEN-025 is pre-tracked — do NOT re-raise from audit

Pre-supplied audit findings (already known from code inspection):
  - RSI: rolling(14).mean() = Cutler's, not Wilder's → P1
  - ATR: rolling(14).mean() = SMA, not Wilder's → P1
  - Bollinger: ddof=1 vs TradingView ddof=0 → P2
  - OPEN-025: >=15 vs >15 boundary → already tracked, skip

Full execution context: docs/quant-audit-execution-brief-2026-04-13.md
Orchestration status: docs/audit-orchestration/status.json

Resume instruction: Read docs/quant-audit-execution-brief-2026-04-13.md,
  check docs/audit-orchestration/status.json for phase completion,
  continue from first unchecked Phase 0 skill file above.
```

### Phase 0 Task List

- [ ] Fix .claude/commands/quant-reviewer.md
- [ ] Fix .claude/commands/signal-accuracy-audit.md
- [ ] Create .claude/commands/quant-data-fetcher.md
- [ ] Create .claude/commands/technical-indicators-math.md
- [ ] Create .claude/commands/portfolio-risk-math.md
- [ ] Create .claude/commands/forecasting-calibration-math.md
- [ ] Create .claude/commands/fundamental-analysis-math.md
- [ ] Dispatch D1+D2+D4+D5 worktree agent
- [ ] Dispatch Vercel migration worktree agent
- [ ] D3 main-context live fetch
- [ ] Write final audit report
- [ ] Raise sprint items
- [ ] /log-learnings + flag update

---

## session_019 — v5.36 Active Tasks

- [x] PROXY-01: classifier_keywords.py shared config
- [x] PROXY-02: approval_hook.py fallback transparency
- [x] PROXY-03: review_gate.py post-proxy diff gate
- [x] PROXY-04: sprint_planner.py Depends column
- [x] PROXY-05: sprint_planner.py staleness check
- [x] PROXY-06: validate_models.py --spend flag
- [x] PROXY-07: approval_hook.py tool-use guard
- [x] Housekeeping: GSI_SPRINT.md Done section, manifest, WIP → ACTIVE
- [x] D-02 bench: ROE benchmark (subscription — proxy deferred to PROXY-08)
- [x] OPEN-006: Portfolio Allocator stability score UI (subscription)
- [x] EQA-41: Forecast accuracy visual baseline (subscription)
- [x] Sprint close: version.py, GSI_QA_STANDARDS.md, GSI_DECISIONS.md ADR, sync_docs, manifest COMPLETE

---

## session_019 Summary

v5.36 Post-Launch Hardening sprint completed in session_019.
7 PROXY items (PROXY-01–07) delivered: classifier_keywords.py shared keyword source, approval_hook.py fallback transparency + tool-use guard, sprint_planner.py staleness check + Depends column + YELLOW bugfix, validate_models.py --spend flag, review_gate.py commit-tag gate.
3 feature items under subscription: D-02 _calc_roe() self-calculated ROE, OPEN-006 portfolio stability score UI, EQA-41 forecast calibration bar chart.
Proxy env-var lifecycle bug discovered and documented: vars locked at process launch; two-launch sequence documented in CLAUDE.md + sprint_planner.py; PROXY-08 parked in backlog.
ADR-024 recorded. RECORD-012 added to SESSION_LEARNINGS.
Final state: 434/434 PASS, 455/455 active (R27 sprint-manifest included), sync_docs exit 0.

Items delivered:
  - PROXY-01: classifier_keywords.py — single keyword source shared by approval_hook + sprint_planner
  - PROXY-02: approval_hook.py — async_success_callback for fallback transparency logging
  - PROXY-03: review_gate.py — [proxy:model] commit tag gate, exit 1 on unreviewed proxy commits
  - PROXY-04: sprint_planner.py — optional Depends column support
  - PROXY-05: sprint_planner.py — staleness check via git log (_sprint_file_age_days)
  - PROXY-06: validate_models.py — --spend flag with per-provider cost table
  - PROXY-07: approval_hook.py — tool-use guard (tools detected → force deep-reasoning)
  - D-02: indicators.py — _calc_roe() from netIncomeToCommon/bookValue/sharesOutstanding
  - OPEN-006: pages/week_summary.py — stability score UI (10× perturbation test, KPI badge, weight sensitivity)
  - EQA-41: pages/week_summary.py — calibration bar chart with dotted reference baselines

---

## session_017 Summary

v5.35 Launch Readiness sprint + v5.35.1 post-sprint hotfix completed in session_017.
v5.35: All 5 CEO sign-offs (S-01→S-05) delivered. R29 analytics check added (+1, 432→433).
v5.35.1: 3 ticker bugfixes (M&M.NS ampersand, AMBUJACEM typo, Zomato/Paytm misclassification).
Governance: Rule 8 (parallel agent discipline), sprint close step 0 (dual version-field), tiered capacity model, token_budget + token_optimisations manifest fields with quality floor guardrails.
Final state: 433/433 PASS, 0 failures, sync_docs exit 0 (all green), ADR-023 recorded.

Items delivered:
  - S-01: ADR-022 WorldMonitor CSP stopgap decision record (code already in v5.34)
  - S-02: docs/index.html GitHub Pages one-page landing site (placeholder, screenshots pending CEO)
  - S-03: streamlit-analytics2 fail-safe integration in app.py + requirements.txt
  - S-04: docs/social-media-guidelines.md (SEBI finfluencer compliance) + RISK-L04 Mitigated
  - R29: regression check — streamlit_analytics import in app.py (432→433)

Architecture note: 3 parallel worktree agents used (Lead Programmer, Lead Developer, QA).
File writes persisted post-cleanup; CTO (main branch) ran regression + committed per Rule 3.

## v5.34.2 Sprint Checklist — session_016 (ALL COMPLETE)

- [x] STEP 1: GSI_WIP.md → ACTIVE session_016
- [x] STEP 2: GSI_SPRINT_MANIFEST.json → v5.34.2 IN_PROGRESS
- [x] STEP 3: regression.py → R28 hook existence checks (+5, 427→432)
- [x] STEP 4: GSI_COMPLIANCE_CHECKLIST.md → baseline 427→432
- [x] STEP 5: .github/PULL_REQUEST_TEMPLATE.md → baseline 427→432
- [x] STEP 6: version.py → v5.34.2 VERSION_LOG entry
- [x] STEP 7: GSI_QA_STANDARDS.md → v5.34.2 QA brief
- [x] STEP 8: GSI_SPRINT.md → v5.34.2 done entry + current sprint → v5.35
- [x] STEP 9: Sprint close (CLAUDE.md + sync_docs + manifest COMPLETE + archive + WIP IDLE)

## session_016 Summary

v5.34.2 sprint completed cleanly in session_016. All 9 steps executed in order.
R28 adds 5 hook infrastructure existence checks — baseline 427→432.
CTO review fixes from v5.34.1 (C-1/C-2/M-1/M-2/M-4) all verified passing.
Final state: 432/432 PASS, 0 failures. ADR-021 added (git rev-parse pattern).
OPEN-021 added to CLAUDE.md (observability.py compliance check duplication).

---

## v5.34.1 + v5.34.2 Sprint Plan — Claude Code Hook Infrastructure

**Decision (2026-04-05):** Original v5.34.1 had ~15 items — split into two micro-sprints to stay under Rule 5 (9-item limit). v5.34.1 delivers the core hooks. v5.34.2 hardens regression and closes.

**Risk summary (audit):** 4 BLOCKER · 5 TIER-A · 1 PROTECTION · 2 DEBT — all resolved in plan below.

---

## v5.34.1 — Core Hook Implementation (session_015, 8 items)

## CHECKPOINT — 2026-04-05 session_015

```
Status:              ACTIVE (interrupted mid-sprint)
Regression baseline: 427/427 (manifest IN_PROGRESS — R27 showing 11 expected failures)
Last commit:         27dfae0 — GSI_SPRINT_MANIFEST.json status → IN_PROGRESS
Git state:           GSI_WIP.md uncommitted (this checkpoint edit)

Completed — all committed:
  - CLAUDE.md ✓ (sprint close protocol added — 19fd41c)
  - .gitignore ✓ (run_state.json, reports/, screenshots/ — 53cb9d7)
  - GSI_DECISIONS.md ✓ (ADR-019, ADR-020 — 213a5b0)
  - docs/sprint_archive/GSI_SPRINT_MANIFEST_v5.35_PLANNED.json ✓ (b31bd77)
  - GSI_SPRINT_MANIFEST.json ✓ (v5.34.1 created — 78b0ddd; IN_PROGRESS — 27dfae0)
  - GSI_WIP.md ✓ (two-sprint split plan — 8965da6)
  - regression.py ✓ (R27 schema bugfix — 7c6309b)
  - .claude/hooks/ directory ✓ (created via python3, not committed — empty dir)

Not yet started (next task is FIRST):
  1. settings.json — add Write(.claude/hooks/*) + Bash(chmod +x .claude/hooks/*.sh)
     to allow list (BLOCKER — must precede writing hook scripts)
  2. compliance_check.py — extract 8-check script verbatim from CLAUDE.md lines 29-36;
     add CWD detection; exit 0/1
  3. .claude/hooks/pre_commit.sh + chmod +x — regression gate (exit 2)
  4. .claude/hooks/pre_push.sh + chmod +x — compliance gate (exit 2)
  5. .claude/hooks/post_edit.sh + chmod +x — doc audit (suppressOutput on pass)
  6. settings.json — add full hooks block (3 hooks, $CLAUDE_PROJECT_DIR paths)
  7. settings.local.json — remove duplicate sync_docs --check entry
  8. CLAUDE.md — replace inline python3 -c with compliance_check.py ref;
     add to File Structure; update Current State → v5.34.1

R27 live status (run python3 regression.py to see progress):
  Tier-A fails (5 — close items, not implementation): version_entry, claude_md_version,
    context_header, sprint_done_entry, qa_standards_has_brief
  Tier-B fails (6 — still to build): hooks_block_added, compliance_check_py,
    pre_commit_hook, pre_push_hook, post_edit_hook, claude_md_inline_fixed
  Tier-B passes (1 — done): r27_bug_fixed ✓

Key decisions made this session (already in GSI_DECISIONS.md):
  - ADR-019: no maxTokens cap (file write truncation risk)
  - ADR-020: exit 2 (not 1) to block; matcher = tool name only; $CLAUDE_PROJECT_DIR
    for portability; Python stdin parse (jq not installed); dedup on PASS only

Critical implementation notes for next session:
  - compliance_check.py: copy inline script VERBATIM — string quoting is non-trivial
    ('"No major red flags at this time."' and lookbehind regex in _render_next_steps_ai check)
  - Hook stdin JSON path: tool_input.command (not top-level command)
  - Exit 2 blocks PreToolUse; exit 0 allows; exit 1 is non-blocking (common mistake)
  - PostToolUse cannot block — post_edit.sh always exits 0
  - suppressOutput: output {"suppressOutput": true} as JSON to stdout on clean pass
  - v5.34.2 (session_016) handles: R28 checks, baseline counts, version.py, QA brief,
    sprint board, full close

Resume instruction: Read this checkpoint, confirm 427/427 baseline, then start with
  settings.json allow list update (Write + chmod permissions) as the first commit.
```

---

### PHASE 0 — Pre-flight (developer runs manually before session_015 starts)

- [ ] Archive v5.35 PLANNED manifest → `docs/sprint_archive/GSI_SPRINT_MANIFEST_v5.35_PLANNED.json`
      WHY: BLOCKER — 6 CEO sign-off items (S-01→S-05 + RISK-L04) will be lost if manifest is overwritten without archiving
- [ ] `mkdir -p .claude/hooks` in repo root
      WHY: BLOCKER — Write tool cannot create files in non-existent directory
- [ ] Confirm `git check-ignore .claude/hooks/pre_commit.sh` returns nothing
      WHY: Hook scripts are source code; must not be gitignored

---

### PHASE 1 — Sprint start (Claude executes in order)

- [ ] `GSI_SPRINT_MANIFEST.json` — rewrite for v5.34.1
      Set: sprint_version="v5.34.1", status="IN_PROGRESS"
      Add Permanent Tier A checks (with "v5.34.1" as must_contain value)
      Add Tier B checks: compliance_check.py exists, hooks block in settings.json, all 3 hook scripts exist
      Add file_change_log for all 16 files listed in Files Changing section below
      NOTE: v5.35 entries are safe in the Phase 0 archive — do not carry them over
- [ ] `GSI_WIP.md` — set Status → ACTIVE
- [ ] `python3 regression.py` — confirm 427/427 clean baseline before any code changes

---

### PHASE 2 — Blockers first, then implementation (one commit per file)

- [ ] `regression.py` — Fix R27 schema bugs (BLOCKER — must be first commit)
      Fix 1: `_c.get("file","?")` → `_c.get("target_file", _c.get("file","?"))` (manifest uses "target_file")
      Fix 2: `must_contain` is a list in manifest — iterate as list, not treat as string (else TypeError on IN_PROGRESS)
      Run regression after — expect 427/427. Commit: "fix: R27 schema — target_file field + must_contain list iteration"

- [ ] `settings.json` — Pre-authorize hook writes and execution (BLOCKER — must precede hook script creation)
      Add to allow: `"Write(.claude/hooks/*)"` — .sh files not currently covered
      Add to allow: `"Bash(chmod +x .claude/hooks/*.sh)"` — chmod not in allow list
      Add to allow: `"Bash(mkdir -p .claude/hooks)"` — for reproducibility
      Commit: "infra: settings.json — pre-authorize hook write + chmod permissions"

- [ ] `compliance_check.py` — NEW FILE (must precede pre_push.sh)
      Extract inline script from CLAUDE.md lines 29-36 — copy VERBATIM (Rules 11-14 depend on exact string matching)
      Add CWD detection: cd to repo root if called from hook context
      Add clean exit 0 on pass / exit 1 on fail with structured output (N/8 checks passed)
      WARNING: preserve exact quoting in '"No major red flags at this time."' and lookbehind regex in Rule 14
      Run regression after — 427/427. Commit: "feat: compliance_check.py — extracted from CLAUDE.md"

- [ ] `.claude/hooks/pre_commit.sh` — NEW FILE
      PreToolUse on Bash; parse tool_input.command via Python stdin; fires on git commit
      Check .claude/run_state.json: skip if result=="PASS" and hash==current HEAD (dedup)
      On cache miss: run python3 regression.py; exit 2 on fail; write run_state.json
      chmod +x immediately after write
      Run regression after — 427/427. Commit: "feat: .claude/hooks/pre_commit.sh — regression gate"

- [ ] `.claude/hooks/pre_push.sh` — NEW FILE (depends on compliance_check.py existing)
      PreToolUse on Bash; parse tool_input.command via Python stdin; fires on git push
      Calls: python3 $CLAUDE_PROJECT_DIR/compliance_check.py
      Exit 2 on failure; exit 0 on pass
      chmod +x immediately after write
      Run regression after — 427/427. Commit: "feat: .claude/hooks/pre_push.sh — compliance gate"

- [ ] `.claude/hooks/post_edit.sh` — NEW FILE
      PostToolUse on Write|Edit; filters for *.md via tool_input.file_path
      Calls: python3 $CLAUDE_PROJECT_DIR/sync_docs.py --check
      On clean pass: output {"suppressOutput": true}; exit 0 (silent)
      On issues: print output; exit 0 (PostToolUse cannot block)
      chmod +x immediately after write
      Run regression after — 427/427. Commit: "feat: .claude/hooks/post_edit.sh — doc audit on *.md"

- [ ] `settings.json` — Add full hooks block
      Add "hooks" block with all 3 hooks using $CLAUDE_PROJECT_DIR paths
      Move "Bash(python3 sync_docs.py --check)" into allow list (from settings.local.json)
      Run regression after — 427/427. Commit: "feat: settings.json — add hooks block (3 Claude Code hooks)"

- [ ] `settings.local.json` — Remove duplicate sync_docs entry
      Remove: "Bash(python3 sync_docs.py --check)" (now in settings.json)
      Commit: "chore: settings.local.json — remove migrated sync_docs permission"

- [ ] `CLAUDE.md` — Three targeted changes
      Change 1: Replace inline python3 -c block in Run Commands with `python3 compliance_check.py`
      Change 2: Add compliance_check.py to File Structure section (utility module, rebuild-safe)
      Change 3: Update Current State version → v5.34.1
      Run regression after — 427/427. Commit: "docs: CLAUDE.md — compliance_check.py ref + v5.34.1 state"

---

### PHASE 3 — Regression hardening

- [ ] `regression.py` — Add R28 hook infrastructure checks
      R28a: .claude/hooks/pre_commit.sh exists
      R28b: .claude/hooks/pre_push.sh exists
      R28c: .claude/hooks/post_edit.sh exists
      R28d: compliance_check.py exists in repo root
      R28e: settings.json contains "hooks" keyword
      NOTE: do NOT add compliance_check.py to PROJECT_FILES (module-level exit() breaks R1 syntax checks)
      Run regression after — expect 427+5 = 432/432. Commit: "feat: regression.py R28 — hook infrastructure checks"

- [ ] `GSI_COMPLIANCE_CHECKLIST.md` — Update baseline count to 432
      Commit: "docs: GSI_COMPLIANCE_CHECKLIST.md — baseline 427→432"

- [ ] `.github/PULL_REQUEST_TEMPLATE.md` — Update baseline count to 432
      Commit: "docs: .github/PULL_REQUEST_TEMPLATE.md — baseline 427→432"

---

### PHASE 4 — Sprint close (per CLAUDE.md sprint close protocol)

- [ ] `version.py` — Add v5.34.1 VERSION_LOG entry
      Notes: hook infrastructure, compliance_check.py, 3 hooks, R27 bugfix, R28 checks, baseline 432/432
      Commit: "chore: version.py — v5.34.1 VERSION_LOG entry"

- [ ] `GSI_QA_STANDARDS.md` — Add v5.34.1 QA brief
      Infrastructure sprint — no UI changes. Test plan: verify each hook fires (attempt failing commit, push, md edit)
      Per Rule 15: must include before/after description, not just numbered steps
      Commit: "docs: GSI_QA_STANDARDS.md — v5.34.1 QA brief"

- [ ] `GSI_DECISIONS.md` — Verify "v5.34.1" appears (ADR-019/020 already written; check string presence)

- [ ] `GSI_SPRINT.md` — Add v5.34.1 Done entry
      Commit: "docs: GSI_SPRINT.md — v5.34.1 sprint board entry"

- [ ] `python3 sync_docs.py` — Full sync (rebuilds CHANGELOG, README, AGENTS; prompts for SEMI items)

- [ ] `python3 regression.py` — Final confirm 432/432

- [ ] `GSI_SPRINT_MANIFEST.json` — status → COMPLETE; archive to docs/sprint_archive/GSI_SPRINT_MANIFEST_v5.34.1.json
      NEXT: rebuild v5.35 manifest from docs/sprint_archive/GSI_SPRINT_MANIFEST_v5.35_PLANNED.json

- [ ] `GSI_WIP.md` — Status → IDLE; move active tasks to Completed; write session_015 summary

- [ ] `CLAUDE.md Open Items` — Add OPEN-XXX for observability.py _inline_compliance_check() duplication (Policy 5 debt)

---

### Deferred to future sprint (not in v5.34.1)

- SessionStart hook — auto-check GSI_WIP.md status on session open
- Stop hook — end-of-session GSI_WIP.md reminder
- statusMessage UX polish on regression gate hook
- Dedup hook for explicit mid-session python3 regression.py calls
- Hook testing dry-run strategy (force-fail a check to verify exit 2 blocks)
- observability.py _inline_compliance_check() → call compliance_check.py instead (OPEN-XXX)

---

### Files Changing — v5.34.1 only (8 implementation files)

**New (4):** compliance_check.py · .claude/hooks/pre_commit.sh · .claude/hooks/pre_push.sh · .claude/hooks/post_edit.sh
**Modified (3):** regression.py (R27 fix only) · .claude/settings.json (×2 commits) · .claude/settings.local.json
**Docs (1):** CLAUDE.md (inline script replacement + file structure entry + v5.34.1 Current State)

---

## v5.34.2 — Hardening + Sprint Close (session_016, 7 items)

### PHASE 3 — Regression hardening

- [ ] `regression.py` — Add R28 hook existence checks (5 checks: 3 hooks + compliance_check.py + settings.json hooks block)
      Run regression → expect 427+5 = 432/432
      Commit: "feat: regression.py R28 — hook infrastructure existence checks"

- [ ] `GSI_COMPLIANCE_CHECKLIST.md` — Update baseline 427→432
      Commit: "docs: GSI_COMPLIANCE_CHECKLIST.md — baseline 427→432"

- [ ] `.github/PULL_REQUEST_TEMPLATE.md` — Update baseline 427→432
      Commit: "docs: .github/PULL_REQUEST_TEMPLATE.md — baseline 427→432"

### PHASE 4 — Sprint close

- [ ] `version.py` — Add v5.34.2 VERSION_LOG entry
      Notes: R28 hook existence checks, baseline 432/432
      Commit: "chore: version.py — v5.34.2 VERSION_LOG entry"

- [ ] `GSI_QA_STANDARDS.md` — Add v5.34.2 QA brief
      Infrastructure sprint — no UI changes. Hook verification test plan (per Rule 15: before/after, not just numbered steps)
      Commit: "docs: GSI_QA_STANDARDS.md — v5.34.2 QA brief"

- [ ] `GSI_SPRINT.md` — Add v5.34.1 + v5.34.2 Done entries
      Commit: "docs: GSI_SPRINT.md — v5.34.1/v5.34.2 done entries"

- [ ] Sprint close sequence (no individual commits — per close protocol):
      python3 sync_docs.py → python3 regression.py → manifest COMPLETE + archive → GSI_WIP.md IDLE
      Add OPEN-021 to CLAUDE.md: observability.py _inline_compliance_check() drift (Policy 5 debt)

### Files Changing — v5.34.2 only (7 files)

**Modified (2):** regression.py (R28 checks) · version.py
**Docs (3):** GSI_QA_STANDARDS.md · GSI_SPRINT.md · CLAUDE.md (OPEN-021 + baseline update)
**Baseline counts (2):** GSI_COMPLIANCE_CHECKLIST.md · .github/PULL_REQUEST_TEMPLATE.md
**Auto-generated:** CHANGELOG.md · README.md · AGENTS.md · GSI_CONTEXT.md
**Archived:** docs/sprint_archive/GSI_SPRINT_MANIFEST_v5.34.1.json · docs/sprint_archive/GSI_SPRINT_MANIFEST_v5.34.2.json

---

## Pending Infrastructure Fix — session_014 MUST DO FIRST

### Root cause (session_013 post-mortem)
7 files were missed in v5.34: CHANGELOG.md, README.md, AGENTS.md,
GSI_COMPLIANCE_CHECKLIST.md, .github/PULL_REQUEST_TEMPLATE.md,
GSI_DECISIONS.md, GSI_QA_STANDARDS.md.

Three failure categories:
- **Category A** (CHANGELOG, README, AGENTS): auto-generated by sync_docs.py,
  which was never listed as a Phase 3 step and had no Tier A manifest check.
- **Category B** (compliance checklist, PR template): contain hardcoded baseline
  counts ("410/410") that must track the regression baseline — no manifest entry,
  no R27 check, no one planned for them.
- **Category C** (GSI_DECISIONS.md ADR, GSI_QA_STANDARDS.md brief): required
  every sprint by Rule 6 and sync_docs.py advisory, but never encoded as Tier A.

### The fix — two CLAUDE.md changes

**Change 1 — Rule 2, step 3:** Add a "Permanent Tier A" section listing 5 always-
required checks that go into EVERY sprint manifest, regardless of sprint content:

```
Permanent Tier A (add to every manifest, not just sprint-specific):
  - sync_docs_passes: python3 sync_docs.py exits 0 (covers CHANGELOG/README/AGENTS)
  - compliance_baseline_current: GSI_COMPLIANCE_CHECKLIST.md contains "ALL {N} CHECKS PASS"
  - pr_template_baseline_current: .github/PULL_REQUEST_TEMPLATE.md contains "ALL {N} CHECKS PASS"
  - decisions_has_adr: GSI_DECISIONS.md contains "v{sprint_version}"
  - qa_standards_has_brief: GSI_QA_STANDARDS.md contains "v{sprint_version}"
```

**Change 2 — Phase 3 close protocol:** Add `python3 sync_docs.py` as explicit step
before declaring sprint COMPLETE (currently absent from the protocol entirely).

### Implementation scope (session_014)
1. Edit CLAUDE.md Rule 2, step 3 — add Permanent Tier A section (5 checks)
2. Edit CLAUDE.md Phase 3 close protocol — add sync_docs.py step
3. Run regression.py — expect 427/427 (CLAUDE.md change does not affect R-checks)
4. Commit: "infra: add permanent Tier A manifest checks + sync_docs to Phase 3 protocol"
5. Then execute v5.35 sprint items below

No new regression checks needed — R27 already enforces Tier A; adding checks to
the template means they appear automatically in the next sprint's manifest.

---

## Active Tasks — v5.35 Launch Readiness (session_014)

### Phase 0 — Infra fix (MUST complete before sprint items)
- [ ] CLAUDE.md: Rule 2 Permanent Tier A section + Phase 3 sync_docs step
- [ ] regression.py: confirm 427/427 still passes
- [ ] Commit infra fix

### Phase 1 — Launch blockers (Claude-executable)
- [ ] global_intelligence.py: remove WorldMonitor iframe, add external link button (S-01)
- [ ] app.py + requirements.txt: streamlit-analytics integration (S-03)
- [ ] docs/social-media-guidelines.md: new file for RISK-L04 (S-04 prerequisite)
- [ ] GSI_RISK_REGISTER.md: RISK-L04 Open → Mitigated

### Phase 2 — CEO-action items (requires Tarun to run the app)
- [ ] CEO: run `streamlit run app.py`, capture 3–4 screenshots
  - Dashboard tab (stock with BUY verdict — e.g. a Nifty 50 stock)
  - Global Intelligence page (topics visible)
  - Week Summary / Group Overview
  - Portfolio Allocator (optional)
- [ ] CEO: hand screenshots to Claude for README + landing page integration

### Phase 3 — Landing page (GitHub Pages)
- [ ] docs/index.html: one-page GitHub Pages site using /design skill
  (depends on screenshots from Phase 2, but can build placeholder structure first)

### Phase 4 — Sprint close
- [ ] version.py: v5.35 VERSION_LOG entry
- [ ] CLAUDE.md: Current State updated to v5.35
- [ ] ADR-018: WorldMonitor stopgap decision in GSI_DECISIONS.md
- [ ] QA brief: v5.35 in GSI_QA_STANDARDS.md
- [ ] /log-learnings: session_014 learnings
- [ ] python3 sync_docs.py
- [ ] GSI_SPRINT_MANIFEST.json: status → COMPLETE, archive
- [ ] GSI_WIP.md: Status → IDLE

---

## Active Tasks — v5.34 (update as each completes)

### Phase 0 — Infrastructure (session_013)
- [x] regression.py: R27 sprint manifest sync checks added
- [x] GSI_SPRINT_MANIFEST.json: manifest created (16 checks: 4 Tier A + 10 Tier B v5.33 + 2 Tier B infra)
- [x] CLAUDE.md: Rule 2 updated (manifest step), Rule 7 added (amendment workflow)
- [x] GSI_WIP.md: Status ACTIVE (this file — in progress)

### Phase 0 — Doc debt backfill (v5.33 misses)
- [x] GSI_AUDIT_TRAIL.md: 6 resolution records (H-02, D-07, D-09, G-02, G-05, EQA-38) + Section 4 regen
- [x] GSI_GOVERNANCE.md: Enforcement section Planned → Implemented (v5.33)
- [x] GSI_RISK_REGISTER.md: RISK-T09 Open → Mitigated
- [x] GSI_LOOPHOLE_LOG.md: Class 4 RISK-001 → Fixed (v5.33); 399 → 410
- [x] version.py: Add missing v5.31 entry
- [x] GSI_CONTEXT.md: Remove incorrectly added OPEN-001; close OPEN-001/OPEN-005

### Phase 1 — Observability dashboard (prerequisites for UX items)
- [x] market_data.py: instrumentation (rate-limit getter, hit/miss counters, error counter, fetch latency)
- [x] pages/observability.py: new founder-only page (App Health + Program tabs)
- [x] regression.py: R26 observability checks (syntax + instrumentation contracts)

### Phase 2 — UX items (after Phase 1 complete + passing)
- [x] D-05: Week Summary loading indicator on Dashboard navigation
- [x] G-03/F-10: Impact chain overflow fix at 1280px
- [x] F-14: West Asia content attribution

### Phase 3 — Sprint close
- [x] version.py: v5.34 VERSION_LOG entry
- [x] CLAUDE.md: Current State updated to v5.34
- [x] GSI_CONTEXT.md: header updated to v5.34
- [x] GSI_SPRINT.md: v5.34 moved to Done
- [x] GSI_SPRINT_MANIFEST.json: status → COMPLETE, archive to docs/sprint_archive/
- [x] GSI_WIP.md: Status → IDLE

## Completed This Session (session_012 — v5.33)

- [x] GSI_LOOPHOLE_LOG.md created — 6-class automation loophole registry
- [x] regression.py R10b: GSI_LOOPHOLE_LOG.md added (399→400)
- [x] regression.py R25: 6 policy enforcement checks added (400→410)
- [x] market_data.py: safe_ticker_key() gate (RISK-003)
- [x] indicators.py: Elder labels → plain English (D-07)
- [x] config.py: GI topics 2→5 (G-02)
- [x] global_intelligence.py: G-05 + P0 compliance + RISK-001 XSS + 48h gate
- [x] home.py: H-02 loading states + RISK-001 XSS
- [x] dashboard.py: D-09 correction factor disclosure
- [x] dashboard.py: P0 compliance gaps (SEBI, algo disclosure, "no red flags" fallback)
- [x] version.py: v5.33 entry added
- [x] CLAUDE.md: baseline 400→410, Current State updated to v5.33
- [x] GSI_COMPLIANCE_CHECKLIST.md: 400→410
- [x] .github/PULL_REQUEST_TEMPLATE.md: 400→410
- [x] GSI_WIP.md: Status IDLE, all tasks ticked
- [x] GSI_SPRINT.md: v5.33 moved to Done, velocity updated

## Previously Completed (session_010 — v5.32)

- [x] v5.32: calc_5d_change() utility (OPEN-008) — utils.py, home.py
- [x] v5.32: P(gain) neutral zone (OPEN-009) — forecast.py
- [x] v5.32: Forecast dedup (OPEN-010) — forecast.py
- [x] v5.32: Dynamic week titles (OPEN-011) — week_summary.py
- [x] v5.32: Weinstein override label (OPEN-012) — dashboard.py
- [x] v5.32: MACD (Daily) label (OPEN-013) — dashboard.py
- [x] v5.32: GI market filter (OPEN-014) — global_intelligence.py, app.py
- [x] v5.32: Market LIVE badge (OPEN-015) — app.py
- [x] v5.32: GI cache coherence (OPEN-016) — global_intelligence.py
- [x] v5.32: R23b regression checks added — regression.py
- [x] GSI_AUDIT_TRAIL.md created — 48 findings, immutable log
- [x] GSI_WIP.md created (this file)
- [x] GSI_SPRINT.md created
- [x] GSI_DECISIONS.md created
- [x] GSI_DEPENDENCIES.md created
- [x] CLAUDE.md checkpoint protocol added
- [x] Regression baseline: 392/392

## Files Generated (in outputs/) — Commit Status

All files committed and pushed to GitHub as of 2026-03-29.

## Decisions Made This Session (not yet in GSI_DECISIONS.md)

None — all decisions from this session are recorded in GSI_DECISIONS.md.

## CHECKPOINT

```
No active checkpoint — session_010 complete.
Next session starts fresh.
```

---

## How to Use This File

### When starting a new session
1. Read this file first — before reading CLAUDE.md or session.json.
2. If `Status: IDLE` — proceed normally with new-session protocol.
3. If `Status: ACTIVE` — read the CHECKPOINT block and resume from there.
   Do NOT start fresh. Do NOT regenerate completed tasks.

### When Claude suspects it is running low on context
Claude writes a CHECKPOINT block here immediately:

```
## CHECKPOINT — [date] [session-id]

Status: ACTIVE (interrupted)
Currently working on: [exact task — file, function, what change]
Completed so far (safe to use from outputs/):
  - [file] ✓
  - [file] ✓
Not yet started:
  - [task]
  - [task]
Decisions made (add to GSI_DECISIONS.md):
  - [decision + reason]
Regression baseline at checkpoint: [N]/[N]
Git state: [committed / not committed — list uncommitted files]
Resume instruction: [one sentence telling next Claude exactly where to pick up]
```

### When session ends cleanly
Claude updates Status to IDLE, clears active tasks, moves them to Completed.

### Conflict prevention rules
- If this file shows `Status: ACTIVE`, do not start a new sprint until:
  (a) the checkpoint work is completed, or
  (b) the interrupted session's outputs are discarded and the WIP is reset.
- Never edit a CHECKPOINT block — add a new one below the old one.
- The most recent CHECKPOINT always wins.

---

## CHECKPOINT — 2026-04-13 | session_025 | v5.36 → v5.37 (phase boundary)

```
Status:               ACTIVE (phase boundary — v5.37a COMPLETE, v5.37b NOT STARTED)
Regression:           492/500 (8 failures = 4 R27.A sprint-close + 4 R27.B v5.37b pending)
Compliance:           NOT YET RUN (run at sprint close only)
Last git commit:      fdd5c31 (unchanged — no commits made this session yet)
bash-git approval:    PRE-APPROVED for all commits by user (session_025)
Commit strategy:      All .py files commit together after sprint close (pre_commit.sh blocks
                      mid-sprint due to R27.A checks requiring sync_docs + QA brief first)
```

### v5.37a — COMPLETE (4/4 items done, files edited but NOT YET COMMITTED)

- [x] df01-open027 — pages/home.py — period 1mo→3mo (3 places) + SEBI caption after line 343
- [x] open-029    — pages/dashboard.py — SEBI caption after _render_header_static() line 178
- [x] open-022    — pages/week_summary.py — SEBI caption in Signal Summary tab + Portfolio Allocator
- [x] open-028    — pages/global_intelligence.py — SEBI caption + BUY/WATCH/AVOID verdict badges
                    (new import: compute_indicators, signal_score from indicators)
                    (new: _vcols dict, df_ind fetch, verdict badge in HTML)

### v5.37b — NOT STARTED (5 items pending)

- [ ] df-03       — pages/week_summary.py — data-as-of timestamp in Portfolio Allocator
- [ ] df-08       — pages/home.py — Top Movers temporal scope label
- [ ] haiku-cluster-H1 — litellm-proxy/config.yaml + sprint_planner.py + portfolio.py + week_summary.py
                          (OPEN-023: groq/qwen-qwq-32b; OPEN-025: >= 15 comment align)
- [ ] haiku-cluster-H2 — market_data.py + pages/global_intelligence.py
                          (DF-02: RSS ET Markets + Reuters; DF-05: macro last-reviewed label)
- [ ] open-026    — CLAUDE.md EP table + regression.py R8 (adds compute_stability_score → 437/437)

### Additional files changed this session (not yet committed)

- GSI_SPRINT_MANIFEST.json — status IN_PROGRESS; playwright fields added to all items;
                              prereq-claude-features → DONE; v5.37a items → DONE;
                              _baseline_correction note added; new file_change_log entries
- GSI_SESSION_SNAPSHOT.md — SNAPSHOT-010 appended (2026-04-13, session_025, no deviations)
- CLAUDE.md               — sprint-monitor wired in Claude Code line + Claude.ai reference block
- .claude/commands/sprint-monitor.md — NEW FILE (sprint execution monitor skill)
- docs/ai-ops/observability-dashboard-plan.md — NEW FILE (local north star obs dashboard plan v1.1)

### Pre-sprint decisions recorded this session

- bash-git pre-approved for all commits (session_025)
- Local observability tool confirmed (not Streamlit Cloud) — ANTHROPIC_API_KEY via shell env
- Vercel migration target: v5.39/v6.0, earliest ~3–4 sessions from now, 10-week execution
- sprint-monitor skill onboarded; observability-dashboard-plan v1.1 documented
- prereq-claude-features confirmed DONE (docs/ai-ops/claude-features-reference.md exists, 16KB)
- Manifest R27.A baseline discrepancy noted: manifest says 434, actual 436, expected exit 437

### Resume instruction

Next session: run /new-session → confirm CHECKPOINT above → resume with v5.37b.
First item: df-03 (week_summary.py, sonnet, data-as-of timestamp in Portfolio Allocator).
All v5.37a files are edited and working — do NOT re-implement them.
Commit strategy: all files commit together after sprint close when 500/500 regression passes.

---

## CHECKPOINT — 2026-04-14 | session_026 | v5.37.1 — SPRINT COMPLETE

```
Status:               IDLE — sprint v5.37 COMPLETE including v5.37.1 hotfix
Regression:           444/444 PASS (last confirmed during v5.37.1 close, manifest IN_PROGRESS)
                      Expected current baseline with manifest COMPLETE: 437/437
                      (436 stable base + 1 R8 check added by open-026 for compute_stability_score)
Compliance:           ALL 436 CHECKS PASS (confirmed during sprint close)
Last git commit:      17a5167 (v5.37.1 all files committed and pushed to main)
bash-git approval:    N/A — all work committed and pushed
```

### Sprint v5.37 — ALL ITEMS COMPLETE (9/9 + v5.37.1 hotfix)

**v5.37a items (4/4):**
- [x] df01-open027 — pages/home.py — period 1mo→3mo (3 places) + SEBI caption after _render_global_signals()
- [x] open-029    — pages/dashboard.py — SEBI caption after _render_header_static() (line 178)
- [x] open-022    — pages/week_summary.py — SEBI captions in Signal Summary + Portfolio Allocator
- [x] open-028    — pages/global_intelligence.py — SEBI caption + BUY/WATCH/AVOID verdict badges

**v5.37b items (5/5):**
- [x] df-03       — pages/week_summary.py — data-as-of timestamp in Portfolio Allocator
- [x] df-08       — pages/home.py — Top Movers temporal scope label (1-day % change caption)
- [x] haiku-H1    — litellm-proxy/config.yaml + sprint_planner.py (OPEN-023: groq/qwen-qwq-32b)
                    + portfolio.py (OPEN-025: >= 15 comment/docstring align)
                    + pages/week_summary.py (OPEN-025: UNSTABLE threshold UI text)
- [x] haiku-H2    — market_data.py (DF-02: DEFAULT_NEWS_FEEDS constant)
                    + pages/global_intelligence.py (DF-05: macro last-reviewed label)
- [x] open-026    — CLAUDE.md EP table + regression.py R8 (compute_stability_score added → 437/437)

**v5.37.1 hotfix (post-sprint):**
- [x] market_data.py — _ticker_cache_period dict added; period match guard in fresh-serve check
                       Root cause: period-agnostic cache served 5d DataFrames for 3mo requests
                       when tickers were "fresh" — caused Global Signals "Computing..." stuck state
- [x] Full hotfix documentation: ADR-026, RECORD-028, Loophole Class 3, QA brief, velocity row

### Open items from this session

- [ ] **Playwright PLAYWRIGHT-01 through PLAYWRIGHT-06** — NEVER RUN. Require running Streamlit
      instance + ui-test skill. Carry forward to next session pre-sprint check.
- [ ] **quant_audit_pending.json** — pending=true for D3/D5 (false positive from post-edit hook
      on market_data.py RSS constant edit). Not a real quant audit trigger. Note at next session start.
- [ ] **v5.38 planning** — not started. Next sprint scope TBD.

### Key decisions from session_026

- Period-aware `_ticker_cache` fix: `_ticker_cache_period` parallel dict, period match in
  fresh-serve check. ADR-026 records rejected alternatives. (Loophole Class 3 added)
- Playwright deferral pattern: when no running app instance, explicitly list deferred tests
  in CHECKPOINT — do NOT silently skip or declare sprint COMPLETE without noting them
- post-edit hook on market_data.py overwrites quant_audit_pending.json entirely — commit
  hook output as-is; do not fight the hook output

### Resume instruction

Next session: run /new-session → run `python3 regression.py` to confirm 437/437 baseline.
If quant_audit_pending.json shows pending=true for D3/D5, acknowledge as false positive and proceed.
First work: plan v5.38 sprint or run deferred Playwright tests (PLAYWRIGHT-01 through PLAYWRIGHT-06).
