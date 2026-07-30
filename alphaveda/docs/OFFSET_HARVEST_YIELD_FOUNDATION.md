# Offset / Harvest / Yield — Foundation Draft
**STATUS: Prerequisite 1 (Product Boundary) APPROVED by Tarun 2026-07-30 — Model B, constrained variant, as recommended below. Prerequisites 2–10 NOT YET DRAFTED. Documentation only past this point. Zero code, zero financial claims, zero regulatory positioning implied beyond what is explicitly stated below.**
**Scope: Phase A, Prerequisite 1 (Product Boundary) + partial glossary only — per Tarun's 2026-07-29 explicit, narrow go-ahead. Trigger thresholds, tax logic, and recommendation eligibility are OUT OF SCOPE (G2-class, human-approval-required per the source document's own governance model) and must not be inferred or filled in here.**
**Source: externally-authored PDF (ChatGPT-generated, not verified) — treat all source claims as proposals to evaluate, not settled fact.**

---

## 1. Product Boundary (Phase A, Prerequisite 1)

### The choice

The source document (page 46) requires one unambiguous operating model to be fixed before anything else is built. Four candidates:

| Model | What it is (source, p.46) |
|---|---|
| A — Portfolio education tool | Explains portfolio characteristics without personalised recommendations. |
| B — Decision-support tool | Uses user-specific holdings and goals to compare choices, but the investor or advisor makes the decision. |
| C — Personalised advisory tool | Produces recommendations tailored to the individual. |
| D — Execution platform | Generates and sends transactions to a broker. |

The source recommends **B** ("a read-only portfolio decision-support tool with simulated recommendations and no automatic execution").

### Recommendation for AlphaVeda: **Model B — but a constrained variant, not the source's wording as-is.**

Adopt Model B's *capability* (compare portfolio states using the user's own holdings and goals; investor decides), while keeping AlphaVeda's *existing* research-only legal framing and language discipline. Concretely: **Model B in function, Model A in vocabulary.**

### Why B, and why C and D are ruled out

AlphaVeda's current, live compliance posture (`alphaveda/.claude/rules/SEBI_COMPLIANCE.md`) states plainly:

> "AlphaVeda is NOT a SEBI-registered Research Analyst or Investment Adviser. It is a personal research tool. No output constitutes regulated financial advice."

and prohibits, in *any* output:
- imperative language — "BUY", "SELL", "invest in", "you should";
- personalised-advice framing — "you should buy X" or "recommended for you".

Measured against that:

- **Model D (execution) — breaks the posture outright.** Sending transactions to a broker is regulated activity on its own and cannot coexist with a "personal research tool, no regulated advice" position. Ruled out.
- **Model C (personalised advisory) — breaks the posture outright.** "Recommendations tailored to the individual" is the definition of personalised investment advice, the exact thing AlphaVeda's rules forbid and that would require SEBI Investment Adviser registration. Ruled out.
- **Model A (education only) — safe, but too narrow.** Pure education cannot use the user's actual holdings/goals to compare Offset/Harvest/Yield options, which is the entire point of this capability. Consistent with the posture, but under-delivers the feature.
- **Model B — the right ceiling, *conditional* on scrubbing.** B is the only model that supports the intended capability without stepping into registered-adviser territory. But it is **not** automatically consistent with AlphaVeda's current posture, and must not be copied verbatim from the source.

### The material caveat: B is *not* free — it needs its own new guardrails

The source's own phrasing for B uses "simulated **recommendations**" and personalisation to "user-specific holdings and goals." Two problems against AlphaVeda's live rules:

1. **The word "recommendation."** AlphaVeda's permitted framing is "Signal: BULLISH / X shows bullish indicators based on [signals] / research output only — not a recommendation." Portfolio-level output must inherit the same discipline: present *comparisons of portfolio states on stated dimensions*, never a ranked "recommended option for you." The source itself flags this direction (p.13: "The recommended option must not automatically be the most aggressive one") but still leans on recommendation language that AlphaVeda's rules do not permit.
2. **Personalisation raises the bar.** AlphaVeda today emits generic, per-instrument signals. Model B introduces the user's *actual* holdings, goals, and constraints, and compares portfolio-level actions against them. That is materially more particularised than a generic signal, and moves closer to the line SEBI's IA framework polices — even where no explicit "buy X" is stated. This is a new surface, not a free extension of the current tool.

Therefore, adopting B requires **new, B-specific disclaimers and controls in addition to** the existing pinned SEBI disclaimer — not the existing disclaimer alone. At minimum (to be specified and approved later, not here):
- extend the prohibited-language rule to portfolio actions (no "you should trim", "sell now", "recommended reallocation");
- present every comparison with the "retain / no-action" state at equal visual weight (source p.4, p.39 — consistent with AlphaVeda's neutrality intent);
- label all output "simulated research scenarios," not "recommendations";
- keep the whole surface read-only with no execution path (aligns with both the source and AlphaVeda);
- note that `COMMERCIAL_GATE.md` already suppresses rupee amounts when `commercial=True` (direction + confidence only) — the portfolio surface must respect that same suppression.

The source concedes B "still requires compliance review." For AlphaVeda specifically, that review is **not** a formality: it is the gate that decides whether the personalisation in B can be delivered without changing AlphaVeda's "not an Investment Adviser" self-classification. Legal product classification is explicitly G2 (source p.64) — human/domain approval mandatory. This document does **not** resolve it; it recommends the target and flags the conditions.

**Net:** Recommend Model B, constrained to research-only vocabulary and read-only/no-execution, with new portfolio-level disclaimers layered on top of the existing SEBI disclaimer. Reject C and D as posture-breaking. Final legal classification remains a G2 human decision.

---

## 2. Glossary — concepts and structures only

**Reminder:** the following define *what each trigger is for* and *what shape its inputs and outputs take*. They deliberately do **not** state materiality thresholds, tax treatment, eligibility maths, or activation logic. Those are G2 / human-approval-required (source p.64) and are out of scope for this draft. Where the source states a formula or cut-off, it is named only as "deferred," never reproduced.

### Offset

- **Purpose (source p.29, p.47):** a *decision gate*. Offset determines whether an existing or emerging portfolio condition is material enough to justify review or correction at all. It answers, at a structural level: "is anything here worth acting on, and would correcting it plausibly be worth the cost?" It is not an instruction to trade.
- **Required inputs (structure only, source p.47):** a detected condition; the evidence attached to it; a materiality test; investor/goal relevance; an intervention-cost input; a confidence requirement; and the set of outputs it is permitted to emit. *The actual materiality cut-offs, confidence levels, and cost maths are deferred (G2).*
- **Required outputs (enumerated states, source p.30, p.47–48):** exactly one of a fixed, ordered set of states — e.g. *no material offset / observe / monitor / review / action-justified / urgent-or-human-escalation*. **Constraint the source is explicit about:** Offset must *not* directly say "sell." It classifies severity; it does not issue trade instructions. (Aligns with AlphaVeda's prohibited-language rule.)
- **Out of scope here:** what counts as "material," the severity thresholds, and the offset-benefit calculation.

### Harvest

- **Purpose (source p.31):** determine whether value that already exists in the portfolio — a gain, a loss, income, or an over-concentrated exposure — can be *responsibly realised or released* without undermining the investor's long-term position. It is the value-realisation engine, distinct from the Offset gate.
- **Structural requirement (source p.31, p.48):** "Harvest" is too broad to be a single thing and **must be split into named subtypes** before any logic exists — goal/liquidity harvesting, concentration/risk harvesting, tax-loss harvesting, tax-gain harvesting, income harvesting, and opportunity harvesting. Each subtype is a *separate* contract with its own inputs and permissions.
- **Required inputs (structure only):** the candidate holding(s); an explicitly identified *purpose category* (which subtype); and the cost/benefit dimensions the source names conceptually — tax effect, risk reduction, goal-funding value, opportunity improvement, net of costs. *The eligibility formula that combines these, and all tax rules, are deferred to a versioned, jurisdiction-specific tax engine (source p.32, p.51–52) and are OUT OF SCOPE — G2.*
- **Required outputs (structure, source Phase F gate p.61–62):** Harvest may not "activate" without (a) a clearly identified purpose and (b) an after-cost benefit determination. Output feeds the option set; it does not execute. Automated tax-loss harvesting is explicitly deferred until a tax module is independently approved.
- **Out of scope here:** every tax rule, set-off ordering, holding-period treatment, and the harvest-benefit formula.

### Yield

- **Purpose (source p.33):** determine whether capital that is retained, newly contributed, or released by a Harvest can be *deployed more productively* toward the investor's goal. The source recommends the internal engine be named **"Productive Capital Deployment,"** even if the user-facing label stays "Yield," precisely to prevent it being read as "chase the highest headline income."
- **Structural requirement (source p.33–34, p.52):** Yield must explicitly distinguish several *different* notions of return and must not optimise headline income in isolation — goal-required return, total expected return, income yield, risk-adjusted return, after-tax return, liquidity-adjusted return, and incremental improvement over the current position. These are structural categories the engine must keep separate, not a ranking rule.
- **Required inputs (structure only, source p.40):** the available capital *and its funding source* (new deposits, dividends, realised gains, realised losses + replacement, maturing instruments, reduced holdings, existing cash — source notes the source affects urgency and suitable deployment); the goal-required return; and the applicable risk, liquidity, concentration, and suitability constraints.
- **Required outputs (structure, source Phase G p.62):** in its constrained form, Yield proposes *allocation categories* — e.g. retain cash / broad equity / diversified equity / liquid-or-short-duration / goal reserve — **not** individual security picks. Output must not violate Offset, liquidity, suitability, or concentration limits.
- **Out of scope here:** expected-return methodology, any security-selection logic, risk/return thresholds, and after-tax return maths — all G2.

---

*End of draft. Nothing below the Product Boundary recommendation and the glossary has been drafted. Trigger contracts, orchestration, conflict-resolution rules, metric dictionary, UX wireframes, and all implementation detail are the explicit NEXT step, gated behind Tarun's review of this document.*
