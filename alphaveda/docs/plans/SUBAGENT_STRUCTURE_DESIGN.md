# AlphaVeda OHY Subagent Structure — Design (Not Yet Dispatched)

**Status:** DESIGN ONLY. Per Council Rule A (`alphaveda/.claude/rules/COUNCIL_RULES.md`), no
subagent here may be dispatched until each has a real, indexed `SKILL.md` and Tarun has reviewed
this design. Nothing below grants tool access yet.

**Source:** PDF pp.54-55 — "Recommended agent structure."

## The 11 roles

```
Lead Orchestrator
|
+-- Product Specification Agent
+-- Domain and Financial Model Agent
+-- Data Architecture Agent
+-- Backend Agent
+-- Frontend and UX Agent
+-- Quantitative Engine Agent
+-- Data-Quality Agent
+-- Security Agent
+-- Test and Validation Agent
+-- Compliance Review Agent
`-- Drift and Evidence Auditor
```

## The load-bearing constraint (source p.55, adopted verbatim)

> "The same Claude subagent should not: design a financial formula; implement it; and approve its
> own implementation."

Three separate roles per financial-logic change:
- **Author** — drafts the specification (e.g. a Prereq 5 metric formula, once Tarun's methodology exists)
- **Implementer** — writes the code
- **Independent Validator** — reviews, cannot be the same agent instance/context as Author or Implementer

## Mapping onto AlphaVeda's existing council (reuse-first, not 11 new skills)

| Source role | AlphaVeda equivalent | Status |
|---|---|---|
| Lead Orchestrator | chief-of-staff (this skill) | Exists |
| Product Specification | product-technical (extended 2026-07-30 to cover AlphaVeda) | Exists |
| Domain and Financial Model | panel-buffett/munger/dalio/lynch/marks/soros/druckenmiller (Author role) | Exists |
| Data Architecture | doctrine-panel-systems-reliability-architect | Exists |
| Backend | (direct Sonnet work, no dedicated skill) | Gap — acceptable, matches existing pattern for non-financial engineering |
| Frontend and UX | ui-ux-pro-max + financial-data-viz | Exists |
| Quantitative Engine | **no current skill** — this is the real, net-new gap | **Gap — needs a skill once Prereq 5 is approved** |
| Data-Quality | calibration-integrity | Exists |
| Security | security-guidance (bundled plugin) | Exists |
| Test and Validation | (direct — AlphaVeda's own test suite + Constraint Enforcer's DB Integrity Extension) | Exists |
| Compliance Review | sebi-compliance-reviewer (Varghese) | Exists |
| Drift and Evidence Auditor | dronacharya-ld-lead + doctrine-panel-constraint-enforcer's Claim Verification Gate | Exists |

**Real finding:** 10 of 11 roles already map onto existing, backed skills — reuse, not 11 new
agents. The one genuine gap is **Quantitative Engine** (the role that would author/implement the
actual Offset/Harvest/Yield formulas) — and per the Author/Implementer/Validator separation rule
above, this cannot be built as a skill until Prereq 5's methodology exists, since there is nothing
yet for it to author.

## Next step, blocked

Do not create a "quantitative-engine" skill or dispatch any financial-formula work through these
roles until Prereq 5 (Calculation Specification) and Prereq 7 (Tax Engine Specification) are
resolved by Tarun — this is the same G2 boundary already enforced everywhere else in this project.
