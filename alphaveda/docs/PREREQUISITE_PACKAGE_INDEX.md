# Prerequisite Package Index — Source's 20-File List Mapped to Reality

Source: PDF p.63, "Minimum prerequisite package Claude needs." Rather than mechanically split the
already-working `OFFSET_HARVEST_YIELD_FOUNDATION.md` into 20 near-empty stub files, this index
maps each named file to where its content actually lives — and honestly names the ones that don't
exist anywhere yet.

| # | Source file name | Actual location | Status |
|---|---|---|---|
| 01 | product-charter.md | `OFFSET_HARVEST_YIELD_FOUNDATION.md` §1 + `ADR-001` | Covered |
| 02 | scope-and-non-goals.md | `OFFSET_HARVEST_YIELD_FOUNDATION.md` §3 (Prereq 2) | Covered |
| 03 | user-and-market-definition.md | Source PDF §4 (investor classifications A-E) — **not yet transcribed into AlphaVeda's own docs** | **Gap** |
| 04 | trimurti-governance.md | `docs/trimurti/framework.md` (new, 2026-07-30) | Covered |
| 05 | offset-contract.md | `OFFSET_HARVEST_YIELD_FOUNDATION.md` §6 | Covered |
| 06 | harvest-contract.md | `OFFSET_HARVEST_YIELD_FOUNDATION.md` §6 | Covered |
| 07 | yield-contract.md | `OFFSET_HARVEST_YIELD_FOUNDATION.md` §6 | Covered |
| 08 | trigger-orchestration.md | `OFFSET_HARVEST_YIELD_FOUNDATION.md` §7 (Prereq 4) | Covered |
| 09 | metric-dictionary.md | **Not written** — Prereq 5 is G2-blocked, only the metric *names* exist (source p.50), no definitions | **Gap, blocked on Tarun** |
| 10 | data-source-policy.md | `OFFSET_HARVEST_YIELD_FOUNDATION.md` §5 (Prereq 6) | Covered |
| 11 | domain-model.md | Partial — `holdings` table schema exists; no full domain model doc | **Gap** |
| 12 | tax-engine-requirements.md | Named in `OFFSET_HARVEST_YIELD_FOUNDATION.md` as Prereq 7, no content | **Gap, blocked on Tarun** |
| 13 | human-approval-boundaries.md | `OFFSET_HARVEST_YIELD_FOUNDATION.md` §4 (Prereq 9) | Covered |
| 14 | ux-behavioural-principles.md | Source PDF §2 (loss aversion, disposition effect, etc.) — **not yet transcribed** | **Gap** |
| 15 | acceptance-criteria.md | `OFFSET_HARVEST_YIELD_FOUNDATION.md` §9 (Prereq 10) | Covered |
| 16 | test-strategy.md | `alphaveda/tests/` exists (215 real tests) but no written strategy doc for OHY specifically | **Gap** |
| 17 | delivery-roadmap.md | `FOUNDATION_RELEASE_SPRINT_PLAN.md` (new, 2026-07-30) | Covered |
| 18 | open-decisions.md | **Not written as a standalone log** — open decisions currently scattered across GAP_REGISTER.md, this doc, and session memory | **Gap — real, worth fixing** |
| 19 | claude-operating-instructions.md | `alphaveda/.claude/rules/*.md` + `CLAUDE.md` | Covered (different file names, same function) |
| 20 | risk-register.md | Partially in `GAP_REGISTER.md`, not OHY-specific | **Gap** |

## Honest summary

**12 of 20 covered**, under different file names but with equivalent real content — not
fragmented for the sake of matching the source's naming convention. **8 genuine gaps**, three of
which (09, 12, and the financial pieces of 03/14) are blocked on Tarun's methodology (Prereqs 5/7)
and cannot be filled by Claude alone. The other gaps (open-decisions.md, risk-register.md,
domain-model.md, test-strategy.md, the non-financial parts of user/UX definitions) are genuinely
buildable now and are the real next-sprint candidates — not yet started, to avoid this response
becoming pure documentation churn instead of the working prototype and Trimurti gates already
delivered this session.
