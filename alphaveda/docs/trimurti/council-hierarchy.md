# Council Hierarchy Under Trimurti — Who Reviews What, With What Authority

Every AlphaVeda council seat (registry: `alphaveda/.claude/rules/COUNCIL_RULES.md` Rule A) is
mapped here to (1) its primary Trimurti role, (2) which OHY loop stage it reviews, and (3) its
decision class (G0/G1/G2, per `OFFSET_HARVEST_YIELD_FOUNDATION.md` §4). This is the "hierarchy
below Brahma/Vishnu/Shiva" — real assessment/planning authority, decisions each seat may make
directly, and where it may only recommend.

## The loop, with seats attached at each stage

```
Observe --------[Calibration Integrity: data quality]
   |
Offset ---------[Munger: risk/bias | Marks: cycle risk | SRE: reliability]
   |
Harvest --------[Buffett: value realisation | Varghese: tax/SEBI compliance]
   |
Yield ----------[Lynch: growth quality | Dalio: risk-adjusted allocation]
   |
Re-check Offset-[Munger again -- mandatory revalidation, same seat]
   |
You decide -----[Wealth & Revenue Strategist: commercial framing only, never the decision itself]
   |
Outcome logged--[Drift/Evidence Auditor: did the prediction hold]
```

## Full mapping table

| Seat | Trimurti role | OHY stage(s) reviewed | Decision class | May decide (G0) | May recommend (G1) | Requires Tarun (G2) |
|---|---|---|---|---|---|---|
| Buffett | Brahma (candidate creation) | Harvest | G1 | — | Which realised-value candidates are worth surfacing | Whether a specific holding's thesis is broken |
| Munger | Shiva (challenge/bias) | Offset (primary + revalidation) | G1 | — | Flag concentration/bias risk, structural safeguards | Materiality threshold itself |
| Dalio | Brahma (allocation candidates) | Yield | G1 | — | Category-level allocation candidates | Goal-required-return methodology |
| Lynch | Brahma (growth-quality read) | Yield | G1 | — | Growth-quality classification narrative | — (classification itself is G1, not G2, once schema exists) |
| Marks | Shiva (cycle risk) | Offset | G1 | — | Cycle-position risk flags | — |
| Soros | Shiva (reflexivity/regime) | Offset | G1 | — | Regime-shift flags | — |
| Druckenmiller | Brahma (macro candidates) | Yield | G1 | — | Macro-aware allocation ideas | — |
| Wealth & Revenue Strategist | (not Trimurti-classed — commercial lens) | "You decide" stage only | G1 | — | Commercial framing of the decision (never the decision) | — |
| Constraint Enforcer | Vishnu (resource/stability) | Whole loop, cross-cutting | G0/G1 mixed | Token/resource-budget calls, scope trims | Architecture/governance changes | — |
| Red-Team (Shakuni) | Shiva (adversarial) | Whole loop, before any release | G1 | — | Attack scenarios, failure modes | — |
| Synthesis Chair | Shiva (final arbitration) | Cross-seat conflicts only | G1 | — | Resolve named seat disagreements | Doctrine reversals (escalates to Tarun) |
| UX/Accessibility | Vishnu (comprehension/stability) | Whole loop, UI layer | G0/G1 | Layout/interaction patterns within design system | New interaction patterns | — |
| SRE/Reliability Architect | Vishnu (infra stability) | Observe, Offset (data pipeline) | G0/G1 | Bounded technical fixes (bug fixes, timeouts) | Architecture changes | — |
| DB Integrity | Vishnu (schema stability) | Observe (portfolio truth layer) | G0/G1 | Schema drift fixes (additive only) | Schema redesigns | — |
| Calibration Integrity | Shiva (data honesty) | Observe | G1 | — | Precision/confidence display rules | — |
| Jhunjhunwala (circuit/microstructure) | Shiva (data quality) | Observe | G1 | — | Circuit-lock/microstructure flags | — |
| Bhattacharya (data licence) | Vishnu (compliance stability) | Observe (data sourcing) | G1 | — | Licence-class compliance flags | — |
| Varghese (SEBI compliance) | Shiva (regulatory challenge) | Harvest (tax framing), whole loop's UI copy | G1 | — | Compliance-safe language | Legal product classification |

## What "deeper level assessment and planning" means concretely

Each seat above does not just issue a verdict — per its Trimurti role, it owns:
- **Brahma seats** (Buffett, Dalio, Lynch, Druckenmiller): generate *candidates*, not final picks —
  e.g. Dalio proposes 2-3 allocation categories, does not pick "the" allocation.
- **Vishnu seats** (Constraint Enforcer, UX, SRE, DB Integrity, Bhattacharya): protect what already
  works — their job is to say what must NOT change, as much as what should.
- **Shiva seats** (Munger, Marks, Soros, Red-Team, Synthesis Chair, Calibration Integrity,
  Jhunjhunwala, Varghese): actively try to break the candidate before it ships — per
  `docs/trimurti/shiva-gates.md`'s own rule, one critical Shiva finding blocks release regardless
  of how well everything else scored.

## Next upskill step (not yet done, real gap)

Each seat's own `SKILL.md` should reference this hierarchy file directly (per Council Rule B:
"every dispatch prompt must name its backing skill"). This session added the OHY-loop role to
`panel-munger` and `panel-buffett` as a proof of concept (see those files) — the remaining 16
seats' SKILL.md files still need the same section added. Tracked here as an open item, not
silently assumed done.
