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

## 3. Market & Instrument Scope (Phase A, Prerequisite 2)

**Status: REVISED 2026-07-30 per Tarun's explicit instruction — ETFs added to in-scope, MFs/liquid-funds/cash re-parked with target dates + execution roadmaps (no indefinite defers, per the standing rule).**

### The source's recommendation (p.46–47) vs. AlphaVeda's actual current capability

The source recommends an MVP universe of: India, Indian residents, listed Indian equities, equity mutual funds, ETFs, liquid funds/cash, EOD analysis, manual/CSV portfolio import — deferring derivatives, leverage, margin, international tax, complex-pricing bonds, unlisted investments, real estate, cryptocurrency, intraday recommendations, and automated orders.

**Checked against AlphaVeda's live instrument table before adopting this (2026-07-30):** all 16 currently-seeded instruments are NSE-listed equities. Zero mutual funds, ETFs, or liquid-fund instruments exist anywhere in the schema or ingest pipeline (`src/ingest/bhavcopy.py` reads NSE/BSE Bhavcopy — an equity-only feed). Adopting the source's scope verbatim would silently commit to a capability that does not exist today.

### Recommendation for AlphaVeda: narrow the source's scope to match real capability, name the gap explicitly

| Asset class | Source recommends | AlphaVeda can ingest today | Verdict |
|---|---|---|---|
| Listed Indian equities (NSE) | In scope | Yes — `bhavcopy.py`, 16 instruments live | **In scope** |
| ETFs | In scope | **No — checked live 2026-07-30**: `bhavcopy.py`'s `_VALID_SERIES = {"EQ","BE","BL"}` explicitly filters out ETF rows (see its own docstring: "excludes derivatives, ETFs-on-debt, and other non-equity instruments") | **In scope by Tarun's explicit instruction — build required, see roadmap below, not silently assumed working** |
| Equity mutual funds | In scope | No ingest path exists at all | **Parked — target date + roadmap below** |
| Liquid funds | In scope | No ingest path exists | **Parked — same roadmap shape as mutual funds** |
| Cash | In scope | N/A — cash isn't a priced instrument; it's a portfolio-ledger rupee amount | **Always in scope, trivially — no ingest dependency, this was mis-scoped as a "deferred" item earlier; correcting here** |
| Derivatives, leverage, margin | Deferred (source) | No | **Deferred — agreement with source** |
| International tax, complex-pricing bonds, unlisted, real estate, crypto | Deferred (source) | No | **Deferred — agreement with source** |
| Intraday recommendations, automated orders | Deferred (source) | No (EOD-only pipeline) | **Deferred — agreement with source** |

**Net scope for Offset/Harvest/Yield Phase A:** listed NSE equities + ETFs (once the build below lands) + cash (already trivially trackable), EOD data, manual/CSV portfolio import for holdings not already in `instruments`.

### ETF inclusion — real execution roadmap (this is a build task, not a documentation change)

Including ETFs "for now" means real engineering work before OHY can reason about them, not a scope-doc edit alone:

1. **Verify empirically which NSE `SERIES` codes actually correspond to ETFs** in a live Bhavcopy sample — the current exclusion comment is ambiguous about which ETF sub-types (equity ETF vs. gold/debt ETF, which may use different series codes) are already passing through under `EQ` vs. genuinely filtered. Don't assume; check a real file first.
2. **Expand `bhavcopy.py`'s series handling** once (1) is confirmed, so ETF OHLCV actually flows into `ohlcv`.
3. **Add an `asset_class` column** (`'equity'` | `'etf'`) parallel to the existing `sector_class` pattern from migration 0019 — an ETF's "fundamentals" analog is NAV, tracking index, and expense ratio, none of which fit the company-fundamentals schema (no ROIC, no debt/equity, no promoter pledge — an ETF has no promoters).
4. **Source and tier-classify ETF NAV/expense-ratio data** per Prereq 6's evidence policy (not yet vetted — likely NSE's own ETF-specific disclosure, Tier 1 if confirmed official).

**Target date: complete before OHY Phase E (Offset prototype) begins** — Offset/Harvest/Yield literally cannot reason about a portfolio holding an ETF without real data behind it, so this has to land before, not during, Phase E.

### Mutual funds & liquid funds — parked, with target date and roadmap (not indefinite)

**Target date:** Track A close (the same 30-day Synthesis Engine reliability clock), or the first real user portfolio containing one, whichever comes first — same trigger already set for the original MF/ETF deferral, now scoped to MFs/liquid-funds only since ETFs moved to in-scope above.

**Execution roadmap if triggered:**
1. Source AMFI's daily NAV data feed (a real, known, public source — not yet vetted against Prereq 6's tier hierarchy).
2. New ingest module, analogous to `bhavcopy.py` but for fund NAVs.
3. Same `asset_class` extension as ETFs above (`'mutual_fund'` | `'liquid_fund'`), with its own non-company fundamentals analog (category, expense ratio, AUM, benchmark — not ROIC/debt-equity/pledge).
4. Re-run this scope decision with real data in hand, same discipline as the ETF build above.

### Portfolio import for held-but-unlisted-in-AlphaVeda instruments

A user's real portfolio may contain equities AlphaVeda doesn't yet track (any NSE-listed stock outside the current 16), an ETF (in scope, pending the build above), or MFs/liquid funds (parked, see roadmap above). Per the source's own Model B constraint (comparisons only, no execution) and its explicit "no order execution" boundary:
- NSE-listed equities outside the current 16 — CSV/manual import is in scope; the *instrument* itself still needs to exist in `instruments` with real fundamentals/OHLCV before Offset/Harvest/Yield can reason about it. Adding a new instrument is an existing, already-working AlphaVeda capability (demonstrated this session with the 11-ticker batch) — not new build work.
- Cash — always trackable, a ledger amount, not a priced instrument; no ingest dependency.
- ETFs, before the build above lands, and MFs/liquid funds (parked) — the portfolio-comparison surface should show them as **untracked holdings, excluded from Offset/Harvest/Yield analysis, explicitly labeled as such** — never silently omitted or misrepresented as $0.

### Out of scope here (per Prerequisite 3–10, not this document)

Trigger thresholds, materiality cut-offs, and any dollar/rupee-value logic for what counts as a "material" concentration are NOT decided here — this document only fixes *which instruments and asset classes exist in the universe*, not what AlphaVeda does with them.

---

## 4. Human Decision Boundaries (Phase A, Prerequisite 9)

**Status: DRAFT — sequenced after Prerequisite 2, per the agreed task-portfolio plan.**

### Not a new taxonomy — the source's G0/G1/G2 model mapped onto AlphaVeda's existing conventions

The source (p.64) proposes its own G0/G1/G2 classes. AlphaVeda already has a working equivalent — the global CLAUDE.md's **External State Write Gate** (replace-object / append-event / irreversible-replace) and the Data Governance Approval Gate — governing every write this session made (the 11-ticker fundamentals batch, the ISIN correction, migration 0019). Rather than run two parallel classification systems, this document maps the source's categories onto what already exists:

| Source's class | AlphaVeda's existing equivalent | Examples from this session |
|---|---|---|
| G0 — Claude may decide | Routine implementation, no external-state write | Drafting this document itself; internal code refactors |
| G1 — Claude may recommend, human approves | Append-event writes (narrow, reversible) + Claude-proposed thresholds | The 11-ticker fundamentals write (logged, reviewed after); the 15%-concentration onboarding threshold proposed this session and approved by Tarun |
| G2 — Human/domain approval mandatory *before* implementation | Irreversible-replace writes + anything touching financial formulas, tax logic, or regulatory classification | Migration 0019 (schema change, went through DIFF + go/no-go); OHY Prereqs 5/7 (financial formulas, tax law) |

### What Offset/Harvest/Yield may automate (G0/G1, structure only — no thresholds decided here)

- Ingesting and validating portfolio/instrument data (the hybrid onboarding model agreed this session — auto-approve on clean checks).
- Portfolio-level calculations that don't touch G2 territory (concentration %, allocation drift) — using formulas already approved elsewhere, not inventing new ones.
- Identifying missing information and flagging it, rather than silently proceeding.
- Generating candidate Offset/Harvest/Yield allocations *within already-approved constraints* — never proposing a constraint change itself.
- Running simulations against synthetic data (per the sandbox/testing strategy already agreed).
- Producing source-backed explanations (evidence before persuasion, per the source's own UX principle already adopted).
- Flagging a policy violation (e.g., a candidate option that would breach Model B's research-only language) — flagging, not silently correcting and proceeding.

### What requires deterministic policy or Tarun's approval before implementation (G2 — same bar as Prereqs 5/7)

- Interpretation of tax ambiguity, or any change to the tax module's methodology (Prereq 7).
- Any change to a financial formula (Prereq 5) — including the Harvest Benefit calculation, risk-adjusted yield, or Offset materiality thresholds.
- Introducing a new security-selection or replacement-asset logic.
- Overriding a user's stated constraint (locked holdings, minimum cash reserve, prohibited assets).
- Approving a low-confidence recommendation for display — low-confidence output either doesn't ship or ships explicitly labeled, never silently upgraded.
- Introducing a new asset class beyond Prereq 2's approved scope (this is the exact trigger already named for revisiting MF/ETF/liquid-fund support).
- Deciding regulatory suitability or legal product classification (this is what Prereq 1's Model B decision already resolved — reopening it is G2, not a routine call).
- Production data access beyond the sandbox (per the testing/sandbox strategy — real portfolio data stays consent-gated, no-execution, per the source's own Phase I boundary).
- Enabling any trade execution — permanently out of scope per Model B; reopening this is a Prerequisite-1-level decision, not routine.
- Changing a critical threshold once set (e.g., the 15% concentration-review trigger agreed this session) — a threshold change is G2, proposing one for the first time is G1.

### How this interacts with the Trimurti sign-off model already built

This maps directly onto the Shiva gate from the sign-off model two turns ago: G0 items are Brahma/Vishnu self-certified by Claude; G1 items get Claude's Brahma/Vishnu self-certification but Shiva always routes to Tarun; G2 items don't get drafted at all without Tarun's methodology input first (Prereq 5/7's resolution this session — draft from cross-referenced public sources, Tarun signs off before it's trusted).

---

## 5. Data-Source & Evidence Policy (Phase A, Prerequisite 6)

**Status: DRAFT — extends `alphaveda/.claude/rules/DATA_SOURCES.md`, does not duplicate it.**

### Why extend rather than write a new file

`DATA_SOURCES.md` already governs every source AlphaVeda's signal engine uses (NSE/BSE Bhavcopy, BSE XBRL, macro data, yfinance/FMP), with real provenance requirements (`source`, `ingested_at`, `licence_class`) already enforced on every row. This session's own L3-B work used a source not yet in that table — Firecrawl + Screener.in, logged as `source: manual_screener` on all 15 fundamentals rows. OHY needs the same discipline extended to the tiered evidence hierarchy the source PDF recommends (p.50–51), applied to what AlphaVeda has actually used, not a generic list.

### Tiered hierarchy, mapped onto real sources this session touched

| Tier | Source class | AlphaVeda's actual instance | Used for |
|---|---|---|---|
| 1 — Authoritative | Exchange data, regulatory filings, audited statements | NSE Bhavcopy, BSE Bhavcopy, BSE Shareholding/Financials XBRL (already in `DATA_SOURCES.md`) | `ohlcv`, `fundamentals` (existing) |
| 1 — Authoritative | Official regulatory disclosure pages | NSE's bulk pledge-disclosure page (Reg-31/SEBI-LODR column specifically — confirmed this session to be the promoter-only column, distinct from the broader depository-wide column) | `fundamentals.promoter_pledge_pct` |
| 2 — Licensed institutional | Verified market-data vendors | FMP (existing, `commercial=True` only) | `ohlcv` supplement |
| 3 — Secondary analysis | Aggregated financial databases | Screener.in via Firecrawl (`source: manual_screener`) — a real, working source this session, but a secondary aggregator, not a primary filing | `fundamentals` (current interim source, pending Prereq-5's calc-spec decision on whether a Tier-1 source should replace it) |
| 4 — Context only | News, commentary | Not currently used for any stored value | N/A |
| 5 — Prohibited as decision evidence | Unsourced social posts, inferred figures without lineage, LLM-generated financial facts | N/A — already excluded by existing provenance requirements | N/A |

### Real finding this session that this policy must encode, not just describe

Screener.in (Tier 3) was treated as sufficient for fundamentals sourcing this session — but two real data-quality bugs surfaced from *not* independently verifying against a Tier-1 source: (1) wrong ISINs for BAJFINANCE/TATASTEEL only caught by cross-checking BSE's own scrip master directly; (2) TMCV's pledge status genuinely absent from NSE's bulk file post-demerger, correctly recorded as `NULL` rather than inferred. **Policy: any Tier-3-sourced value that a Tier-1 source can independently confirm must be cross-checked before being trusted as fact** — this is the same discipline the Claim Verification Gate already requires generally, made concrete for OHY's specific sources.

### Provenance requirements (extends existing, does not replace)

Same three fields already required (`source`, `ingested_at`, `licence_class` for `ohlcv`) — OHY-derived tables additionally require:
- `evidence_tier` (1–5, per the table above) on any value used in an Offset/Harvest/Yield calculation.
- `cross_verified` (boolean) — whether a Tier-3 value was independently checked against Tier 1/2 before use, per the policy above.

### Out of scope here

Which specific formulas consume which tier of evidence, and what confidence penalty (if any) applies to Tier-3-only data — that's Prereq 5 (calculation spec), not this document.

---

## 6. Offset / Harvest / Yield Formal Contracts (Phase A, Prerequisite 3)

**Status: DRAFT — builds on the Glossary (§2), does not repeat it. Structure only, no thresholds/formulas — those are Prereq 5, G2.**

Each engine gets the same contract shape: named inputs, a fixed enumerated output set, and an explicit "does not decide" boundary. This is the difference between a glossary entry (what it's *for*) and a contract (what it actually *takes and returns*).

### Offset contract
```
INPUT   condition_detected: enum (concentration_drift | liquidity_mismatch | goal_change | ...)
        evidence: [DataPoint]  — each tagged with evidence_tier (Prereq 6)
        investor_constraints: InvestorProfile (Prereq 8)
OUTPUT  one of: no_material_offset | monitor | correct_via_cashflow | partial_rebalance |
                broader_reallocation | urgent_human_escalation
        — never "sell" as a direct instruction (source p.30, already in Glossary)
DOES NOT DECIDE  materiality cut-offs, confidence thresholds, cost-benefit maths — Prereq 5 (G2)
```

### Harvest contract
```
INPUT   subtype: enum (goal_liquidity | risk_concentration | tax_loss | tax_gain | income | opportunity)
        — Harvest is not one contract, it's six, per the Glossary's own structural requirement
        candidate_holding: Instrument
        purpose_category: subtype (above) — must be explicit, never inferred
OUTPUT  one of: not_eligible | eligible_pending_cost_check | eligible
        + after-cost benefit breakdown (tax/risk/goal/opportunity components, unpriced here)
DOES NOT DECIDE  the eligibility formula itself, all tax rules (set-off ordering, holding-period
                 treatment) — Prereq 5 and 7 (both G2)
```

### Yield contract
```
INPUT   available_capital: {amount, funding_source: enum (new_deposit | dividend | realised_gain |
        realised_loss_replacement | maturing_instrument | reduced_holding | existing_cash)}
        goal_required_return: from InvestorProfile (Prereq 8)
        constraints: {risk_limit, liquidity_requirement, concentration_threshold, suitability_rule}
OUTPUT  allocation_category: enum (retain_cash | broad_equity | diversified_equity |
        liquid_short_duration | goal_reserve) — categories only, never individual security picks
        (source p.62, Phase G gate — already in Glossary)
DOES NOT DECIDE  expected-return methodology, security-selection logic, after-tax return maths —
                 Prereq 5 (G2). Internal engine name: "Productive Capital Deployment" per source
                 p.33, user-facing label stays "Yield."
```

### Cross-engine rule already fixed by the Glossary, restated as a contract constraint

No engine's output may itself violate another's constraint — Offset limits Yield's solution space (source p.38, already in Glossary §"Offset versus Yield"). This is enforced at the orchestration layer (Prereq 4), not inside any single engine's contract.

---

## 7. Trigger Hierarchy & Conflict Rules (Phase A, Prerequisite 4)

**Status: DRAFT — encodes the source's own combined hierarchy (p.35, p.38) as AlphaVeda's working decision order, not a re-derivation.**

### Overarching precedence (source p.35, adopted as-is — no disagreement found)

```
1. Investor survival and liquidity
2. Goal continuity
3. Regulatory and suitability constraints
4. Protection from material permanent loss
5. Preservation of durable compounding
6. Tax and cost efficiency
7. Portfolio risk improvement
8. Income generation
9. Incremental return optimisation
10. Tactical opportunity
```

### Severity vocabulary — same 6-level scale across all three engines (source p.37–38)

| Level | Meaning | UX response |
|---|---|---|
| 0 — Dormant | No material condition | No user interruption |
| 1 — Observed | Early/weak evidence | Record silently |
| 2 — Monitoring | Evidence strengthening | Display in portfolio health |
| 3 — Review | Material enough for comparison | Offer strategies |
| 4 — Action justified | Net benefit exceeds threshold (Prereq 5, G2 — the threshold itself) | Highlight recommendation |
| 5 — Critical | Goal, liquidity, or permanent-loss concern | Require prompt review |

"Critical" is reserved for genuinely consequential circumstances — not routine volatility (source's own explicit constraint, already in Glossary).

### Pairwise conflict rules (source p.38, adopted)

- **Offset vs. Harvest:** Offset wins when a structural risk can't safely remain; Harvest wins when the portfolio is structurally healthy but a time-sensitive tax/goal opportunity exists.
- **Harvest vs. Yield:** Harvest doesn't proceed merely because Yield found an attractive replacement — the replacement must exceed current-asset value + tax cost + execution cost + uncertainty premium + lost optionality (formula itself is Prereq 5, G2; the *rule that a formula must be cleared* is fixed here).
- **Offset vs. Yield:** Offset limits the solution space; Yield may only optimise inside already-approved allocation/risk/liquidity/concentration/suitability limits.
- **Goal need vs. all three:** a hard goal or liquidity requirement overrides tax and incremental-return optimisation, full stop.

### Execution sequence — a loop, not a one-way pipeline (source p.36–37, real structural finding already surfaced)

```
Observe → Offset → Harvest → Yield → Offset REVALIDATION → human decision → outcome review → repeat
```

The revalidation step is not optional: a Yield-proposed allocation can itself introduce new concentration, liquidity risk, or tax exposure — Offset must re-check the *proposed* end-state, not just the current one. This is the same principle as the Loop-Engineered Roadmap's own "Fail-Loud" law (verify at the point of change, not only at entry).

### Orchestration ownership (ties Prereq 3's contracts together)

A supervisory orchestrator — not any single engine, and not "language-model interpretation at runtime" (source's own explicit prohibition, p.49) — owns: running the four-step sequence above, applying the precedence list to resolve conflicts, and constructing the final option set (Preserve / Offset-only / Harvest-only / Yield-new-capital / integrated). This orchestrator is itself a build target (Phase H in the source's roadmap), not decided further in this document.

---

*End of draft. Prerequisite 1 (Product Boundary) approved 2026-07-30. Prerequisites 2 (Market & Instrument Scope, revised), 3 (Formal Contracts), 4 (Trigger Hierarchy & Conflict Rules), 6 (Data-Source & Evidence Policy), and 9 (Human Decision Boundaries) drafted above — pending Tarun's review. Prerequisites 8, 10 remain undrafted next. Prerequisites 5, 7 remain G2 — drafting begins once Tarun's cross-referenced-public-source protocol (agreed 2026-07-30) is applied.*
