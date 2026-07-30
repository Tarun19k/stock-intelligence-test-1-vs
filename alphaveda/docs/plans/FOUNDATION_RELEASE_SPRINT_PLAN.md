# Foundation Release — Sprint Plan
**Milestone name (per source material):** "Foundation Release: Specification, Governance and Executable Prototype Skeleton"
**Source:** `Knowledge Repository/AlphaVeda_idea/Agentic application to understand home schooling - Portfolio Churn Strategy Design.pdf` (66 pages, full-text extracted and read 2026-07-30)
**Prepared using:** `pm-execution` skill (sprint-plan method), single-operator context (Tarun + Claude, no team velocity data — capacity framed as attention/session time, not story points)

---

## Gap analysis — real, verified 2026-07-30

The source PDF specifies a 9-phase build sequence (Phase A–I) with hard gates between each, a specific repository blueprint, an 11-subagent orchestration structure, and a 20-file prerequisite package. Checked live against the actual `alphaveda/` repo:

| Blueprint element | Source requires | Actual state (verified live) |
|---|---|---|
| Prerequisite package (20 named files) | `01-product-charter.md` ... `20-risk-register.md` | Consolidated into one doc, `OFFSET_HARVEST_YIELD_FOUNDATION.md` — 8 of 10 *content* areas covered, but not structured as the 20 discrete files (traceability/open-decisions/risk-register files don't exist standalone) |
| `docs/trimurti/` (framework.md, brahma-gates.md, vishnu-gates.md, shiva-gates.md) | Required in Phase A | **Does not exist** |
| `docs/decisions/ADR-*.md` | Required in Phase A | **Does not exist** — zero ADRs anywhere in the repo |
| Separate engine services (`offset-engine/`, `harvest-engine/`, `yield-engine/`, `orchestration/`, `conflict-resolution/`) | Required in Phase B/E/F/G | **Does not exist** — zero files matching any of these names |
| `.claude/agents/` (11-subagent structure: Lead Orchestrator + Product Spec, Domain/Financial Model, Data Architecture, Backend, Frontend/UX, Quantitative Engine, Data-Quality, Security, Test/Validation, Compliance Review, Drift/Evidence Auditor) | Required for Phase A onward | **Does not exist** — all work this project has done was single-session, single-agent (me), not the specified orchestrated multi-agent structure |
| Phase C — Portfolio truth layer (transaction ledger, position calc, cost basis, corporate-action interface, security master, valuation, gain calc, reconciliation, data-quality scores, immutable audit events) | Must complete + gate ("golden portfolios reconcile exactly") before Phase D | `holdings` table exists (added 2026-07-30) but is **empty, 0 rows** — schema-only, none of the other 9 elements (cost basis, corporate-action interface, reconciliation, audit events) exist |
| Phase D — Diagnostic prototype (concentration, allocation, overlap, gains attribution, Growth Strength/Fragility/Defence) | After Phase C gate passes | Two UI mockups built (Screen 1, Screen 4) **explicitly marked illustrative** — correctly not claiming to be Phase D since Phase C hasn't gated |
| Phase E/F/G — Offset/Harvest/Yield prototypes | After Phase D | Prereqs 3/4 (contracts, hierarchy) drafted — this is Phase A content, not E/F/G implementation |
| Claude Code hooks (before-file-mod: block metric/tax-rule changes without ADR; after-code-mod: run tests/scan hardcoded rates; before-completion: golden portfolios, lineage checks) | Required per source's "Role of CLAUDE.md" section | **None of these hooks exist** in `alphaveda/.claude/` |
| G0/G1/G2 decision classes | Required, maps onto CLAUDE.md's own gate | **Already adopted** — OHY Prereq 9 explicitly maps this onto AlphaVeda's External State Write Gate |

**Bottom line:** what's been built so far (signal engine, accuracy ledger, instrument pages, OHY prereq drafts) is real and independently verified this session — but it is a *different, earlier product* (a momentum-signal research tool) running in parallel with the Trimurti/Offset-Harvest-Yield Portfolio Intelligence system this source material describes. The two haven't been reconciled into one governed repository yet. Phase A (Constitution and specification) is roughly 60-70% done by content, 0% done by the source's own required *file structure*. Phase B (engineering skeleton) has not started. Phase C (portfolio truth layer) has one empty table and nothing else.

---

## Sprint Goal

**Close Phase A's structural gap and start Phase B's skeleton — without touching any recommendation logic (Offset/Harvest/Yield engines) until Phase A is formally gated closed, per the source's own rule: "No implementation of recommendation logic until these documents are marked approved."**

## Capacity (single-operator framing)

- Owner: Tarun (approval gates, G2 decisions, real data)
- Executor: Claude (drafting, repo restructuring, G0/G1 work)
- Buffer: OHY Prereqs 5 & 7 (Calculation Spec, Tax Engine Spec) remain G2-blocked on Tarun's methodology — not in this sprint's committed scope, tracked as a dependency

## Stories — this sprint

1. **Restructure existing OHY content into the source's 20-file prerequisite package** — owner: Claude — dependencies: none — effort: low (mechanical split of existing `OFFSET_HARVEST_YIELD_FOUNDATION.md` content into the named files, no new content)
2. **Create `docs/trimurti/` (framework.md, brahma-gates.md, vishnu-gates.md, shiva-gates.md)** — owner: Claude — dependencies: story 1 — effort: low
3. **Retroactively write ADRs for major decisions already made this session** (Model B product boundary, sequencing gate, ETF scope correction, migration-tree reconciliation) — owner: Claude — dependencies: none — effort: medium (real content exists, needs ADR formatting)
4. **Design the `.claude/agents/` 11-subagent structure** (not yet dispatching them — just the skill/agent definitions per Council Rule A discipline: no agent without a backing file) — owner: Claude, reviewed by Tarun — dependencies: none — effort: medium
5. **Phase C — Portfolio truth layer, minimum viable slice**: cost basis field + reconciliation test against Tarun's real holdings — owner: Claude (build) + Tarun (real data) — dependencies: Tarun's real holdings values (already an open ask from earlier this session) — effort: medium, **blocked on Tarun**
6. **Draft the 3 missing before/after/completion Claude Code hooks** the source explicitly recommends (block metric-spec/tax-rule changes without an ADR; scan for hardcoded tax rates; run golden portfolios before completion) — owner: Claude — dependencies: story 3 (needs ADR structure to reference) — effort: medium

## Dependencies / Critical Path

Story 5 (portfolio truth layer) is the actual gate for everything downstream (Phase D diagnostics, Phase E-G engines) — and it is blocked on Tarun providing real holdings data, exactly as flagged earlier this session. Stories 1-4 and 6 have zero Tarun-side blockers and can proceed immediately.

## Risks

- **Risk:** Building the 11-subagent structure without real orchestration discipline becomes theater (agents defined but never dispatched with real scope separation). **Mitigation:** apply Council Rule A (skill must exist + be indexed before any dispatch) to these exactly as done for AlphaVeda's existing council seats — no agent gets used until it has a real, reviewed SKILL.md.
- **Risk:** Retroactive ADRs could be written to look more rigorous than the actual decision process was. **Mitigation:** ADRs cite the actual session evidence (commit hashes, live verification results) already produced this session — nothing invented.
- **Risk:** This sprint could become pure documentation/structure work with no forward product movement, while the revenue blocker (Governance Pack) sits unpublished. **Mitigation:** none of these 6 stories compete with the Governance Pack publish action — that remains a separate, higher-priority, Tarun-only action per the round table's own finding.
