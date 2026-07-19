# AlphaVeda — Non-Financial Council Scope Sign-off

**Date:** 2026-07-16
**Reviewing:** Finalized near-term build scope (10 items) + revised sequence `1(+RF-D) → 9 → 8 → 2 → 3+4 → 5 → 6(done) → 7 → 10`
**Context:** Financial council (Buffett/Munger/Dalio/Marks/Soros/Druckenmiller/Lynch/Wealth-Revenue) already signed off sequencing + conflict-of-interest. This pass covers the domains that have NOT yet reviewed this finalized version: SEBI compliance, UX, reliability, calibration, rule-compliance.
**Dispatch basis:** Combined council per COUNCIL_RULES.md Rule A/B — five complementary seats, each backed by a registered SKILL.md, applying its own named standard. One pass (seats are non-adversarial domain checks).
**Grounded in:** GAP_REGISTER.md, SEBI_COMPLIANCE.md, COUNCIL_RULES.md, COMMERCIAL_GATE.md, DATA_SOURCES.md, persona-uat-pilot-2026-07-16.md.

---

## 1. Varghese — SEBI Compliance Reviewer

**Lens:** Does RF-D resolution (in item 1) + item 9 disclosure gate close the real regulatory exposure, and is any of the 10 items unnamed compliance risk?

**Live baseline (evidence):** The persona pilot cross-checked all 4 routes against the prohibited-language list and found **no violations** — soft "LEANS UP/DOWN" framing (Check 2 PASS), disclaimer pinned non-dismissable on every page with required substance (Checks 1 + 7 PASS), NG-1 past-performance disclaimer live on /accuracy (Check 4 PASS). Current production is compliant.

**RF-D (item 1):** Resolving it as part of item 1 is correct — but note the distinction the scope must respect. NG-4 (disclaimer *mutability* via Vercel env var) is already CLOSED (`f307967`): text now generates from `constants.py` at build with a CI drift test. RF-D is the *residual* — the disclaimer **text still disagrees across four surfaces** (`constants.py` / Vercel env / `sebi.spec.ts` / lexicon `SEBI_PLAIN`). Closing RF-D means:
- Reconcile all four to the **single canonical `constants.py` text** — and that text must be the one the pilot live-verified as compliant, so reconciliation must not regress substance ("research/analysis only", "NOT investment advice", "Consult a SEBI-registered adviser", "Past accuracy does not guarantee future returns").
- **`sebi.spec.ts` is the test oracle** — if it still asserts old wording, the CI drift test is guarding the wrong string. Update the oracle in the same pass or the reconciliation is unverified.
- **Delete the stale Vercel `SEBI_DISCLAIMER` env var**, don't just supersede it. A dead-but-present mutable override is a latent Check-7/Check-1 hazard.
- The lexicon `SEBI_PLAIN` (Simple-mode line, ex-NG-6) is a *second* disclaimer surface — confirm both Simple and Pro render substance-equivalent text (R11 dual-mode requirement).

**Item 9 (operator-test-account gate):** The 4-condition design is sound and the self-referential clause ("a SEBI-compliance-reviewer pass before any external mention") is exactly right. **But moving it earlier is not merely prudent — it is necessary**, because G6 closed *today* and ₹17,00,000 real capital is already live in `constants.py` + Path Kelly sizing. So the gate must be applied **retroactively against current production**, not just future mentions: verify (a) the ₹ figure is unreachable on any unauthenticated path — NG-2's fail-closed `isPersonalContext()` gate is the enforcing control, confirm it still holds post-G6; (b) the public `/accuracy` ledger contains **model predictions only, never Tarun's realized personal P&L** — the wall must be verified, not assumed.

**Unnamed risk in the 10 items:**
- **Item 10 (Lynch layer)** — the "3-question self-check" must be phrased as *educational self-verification*, never "should you buy" (Check 3). The "news include/exclude filter": news placed adjacent to a directional signal can imply a recommendation — Munger's G21 guardrails (news subordinate, ≤3 items, no headline stronger than source) must apply structurally the moment any news element ships.
- **Item 5 (weekly_forecast_report.py)** — if this report is ever emailed/exported externally, SEBI framing + disclaimer must travel with it. In-scope as a bug fix; flag for the compliance boundary if distribution changes.
- **Items 3+4 (Wilson CI)** — a confidence interval strengthens past-performance honesty; no new exposure.

**VERDICT: APPROVE WITH MODIFICATIONS** — RF-D closure must (a) update `sebi.spec.ts`, (b) delete the stale Vercel env var, (c) keep Simple+Pro substance-equivalent; item 9 must be applied retroactively to verify the already-live ₹17L is walled from public routes and the public ledger carries no personal P&L.

---

## 2. UX — ui-ux-pro-max

**Lens:** Is merging 3+4 the right call or under-scoped? Any UX risk in item 10 touching the Class column?

**Merge 3+4 (Wilson CI + fix `46.666666666666664%` float):** Structurally correct — same page (`/accuracy`), same code location, one pass. The float fix is the pilot's **#1 ranked issue** (breaks Rohan's trust, reads as "broken money tool" to Kavita) — highest damage-per-effort, right to bundle.

**Under-scoping risk — real, must address:** The pilot's central finding is that first-time users (Priya, Kavita) already drown in unexplained jargon ("COLD", "Kelly", "suppressed"). Dropping a bare Wilson interval next to the hit rate — e.g. `46.7% [95% CI: 21–73%]` on a ~15-sample ledger — reads as *more* alarming and technical than the float it replaces: a very wide interval looks like malfunction to Kavita and clutter to Priya. **The CI must ship with its plain-English gloss, not after it.** The good news: the CI *is* the quantitative form of the pilot's issue #5 ask ("sample-size caveat so a sub-50% early ledger reads as 'early days, small sample'"). So pair them: rounded hit rate + interval + one always-visible line ("range is wide because we've only graded a few results so far — early days"). Merging 3+4 without that explainer would trade one credibility bug for a new confusion bug.

**Item 10 touches the Class column — compounding risk:** The pilot's **#2 HIGH issue** is that the Class column is inconsistent *today* — `fast_grower`/`stalwart`/`cyclical` render as friendly clickable chips, but `slow_grower`, `asset_play`, `turnaround` leak as raw enums; Simple mode doesn't cover all enums and Pro mode turns *everything* into raw enums. Item 10 builds a Lynch content layer that reuses `lynch_class`. If it ships the plain-English persona narrative **while three categories still render as raw enums in the column that anchors it**, it *deepens* the inconsistency — the story says "fast-growing company" while the grid says `slow_grower`. **Recommendation: fold Class-column completion into item 10** — every Lynch category gets a plain-English label + tap-to-learn dialog in *both* modes (reuses the A10 lexicon + A11 glossary already built). It is the same `lynch_class` surface; splitting it guarantees a visible seam. This is a scope addition — see Constraint Enforcer for the trade-off.

**VERDICT: APPROVE WITH MODIFICATIONS** — (1) 3+4 must include an always-visible plain-English gloss for the CI (don't ship a bare interval); (2) item 10 must complete Class-column consistency (all Lynch categories, both modes) or it worsens the pilot's #2 issue.

---

## 3. SRA — Systems Reliability Architect

**Lens:** Is the reorder (8→2, 9 earlier) dependency-correct? Reliability risk in item 2 now that it depends on item 8?

**Reorder — correct.** Item 8 (mirror External State Write Gate into COUNCIL_RULES.md) before item 2 (Task D scheduler) is right: the governance rule that constrains external-state writes must exist before the code that performs one lands, so the builder sees it. Item 9 earlier is a risk-reduction (real capital live) with no code dependency either way — no conflict introduced.

**Item 2 reliability — the reorder fixes ordering but not the FMs. New Tier-0 dependency:**

| FM | Description | Severity | Detection | Recovery |
|---|---|---|---|---|
| FM-01 | RemoteTrigger / claude.ai Routines (new primary trigger) itself fails silently — same failure class as G23's GHA `schedule:` | P1 (proof-window stalls) | delayed | manual |
| FM-02 | Both primary (RemoteTrigger) AND backup (GHA `schedule:`) fire for the same date → double ingest | P1 (duplicate rows / double-counted outcomes) | silent | rebuild |
| FM-03 | Watchdog (`ingest-watchdog.yml`, G11) still keyed to old GHA `:00` schedule → false alarms or misses the new trigger's window | P2 | delayed | manual |

**Required before item 2 closes:**
- **Idempotency guard must specify its key = the target trading date.** G18 already added terminal-exclusion at the *outcome* level (skip `prediction_id` already in `accuracy_outcomes`), but the OHLCV upsert / run itself needs a run-level dedup so FM-02's double-fire converges instead of duplicating. Design must name the key, not just say "idempotency guard."
- **Re-point the watchdog** to the new primary trigger's expected fire time, or it guards a schedule nothing uses (FM-03).
- **Honor the retest gate already written into G23:** "Retest — blocked on Layer 1.5's ≥2 failure-scenario evidence requirement." Item 2 is NOT done until two real scenarios are exercised: (a) primary missed → backup catches; (b) both fire → idempotency holds, no duplicate. This is correctly flagged in the register; the scope must not let item 2 close on syntax-verify alone (the G18/G22 pattern of "syntax-verified, not exercised" is the recurring miss here).
- Observability today is **Yellow** (watchdog detects, opens a GitHub Issue — G11) — acceptable, but the Issue-open path must survive the trigger swap.

**VERDICT: APPROVE WITH MODIFICATIONS** — reorder is correct; item 2 design must (1) name the idempotency key (target trading date), (2) re-point the watchdog, (3) close only after the ≥2-scenario retest per G23's own lifecycle, not on syntax-verify.

---

## 4. Calibration Integrity

**Lens:** Does the Methodology Log's first entry satisfy calibration-integrity, or is more needed before item 7 counts as "started" correctly?

**First, a brief-internal ambiguity to resolve:** Item 7 says the first entry documents "the decision to defer wiring the bypassed multi-signal model (`load_weights()`)"; the seat-4 question calls it "the G1-deferral." These are **two different deferrals** (G1 = empty `fundamentals` table; `load_weights()` = bypassed multi-signal blend). The log must be explicit about *which* deferral it records — conflating them is exactly the silent-bucket drift this seat exists to catch.

**Why one entry is insufficient.** A methodology log's calibration job is to make the ledger's provenance auditable — so a future reader cannot mistake *what system earned this hit rate*. The proof window is being run right now on a **single momentum signal at T+1**, and several calibration-material facts are currently documented only in the Gap Register, not the methodology log:
1. **The `load_weights()` bypass itself** — the live confidence numbers are momentum-only, not multi-signal blended ("Active Signal Weights: No active weights yet" is the honest live state per the pilot). Must be logged, or a future reader attributes the ledger to the multi-signal system.
2. **RF-F horizon deviation (T+1 vs council's T+5).** This is calibration-critical: when the model later extends to T+5 or wires weights, the ledger must **not pool T+1 observations with T+5 observations** — that is horizon-segment drift, the same silent-bucket failure as BULL/BULLISH enum drift. The log must record that current observations are T+1-only and are not comparable to a future T+5 track record.
3. **Proof-window exit criterion + start date.** Exit = `OBSERVATION_THRESHOLD` (30 obs) measured **per-`instrument_id`** (post-G19 fix — not pooled by `(lynch_class, regime)`). Start = 2026-07-13 (G22: "Day 1, not Day 0"). Both must be in the log.
4. **G23 gap caveat.** The proof window is observation-count-gated, but G23 (scheduled ingest miss) means calendar days have gaps with no resolved observations. The log must state that missed-ingest days extend real-time-to-proof — otherwise "window closed after N days" misreads a calendar count as an observation count.

None of these touch outcome-resolution/enum/circuit/entry-price mechanics (those remain PASS — G18 horizon-maturity + terminal-exclusion are closed, circuit exclusion is enforced per DATA_SOURCES.md). The defect is **provenance under-documentation**, not ledger corruption.

**VERDICT: APPROVE WITH MODIFICATIONS** — item 7 is not "correctly started" with a single deferral entry. The first tranche must also log: the `load_weights()` bypass, the RF-F T+1 horizon (with the no-pooling-across-horizons rule), the proof-window exit criterion (30 obs per-instrument, start 2026-07-13), and the G23-gap caveat. And it must disambiguate G1-deferral vs `load_weights()`-deferral.

---

## 5. Constraint Enforcer — Governance + Resource

**Lens:** Final rule-compliance pass — does anything violate an existing gate (premortem, data governance, cross-workspace) not yet accounted for?

**Premortem Gate — two unlogged triggers:**
- **Item 8** edits `alphaveda/.claude/rules/COUNCIL_RULES.md` to add a new Rule. `.claude/rules/` is not literally in the global trigger-file list, but adding a governance Rule is an architecture/config change — premortem due-diligence applies ("architecture decisions", "configuration"). **Log a premortem before the write.**
- **Item 2** modifies `ingest.py` + introduces a new scheduler = infrastructure change → premortem trigger. **Complication:** Task D is dispatched to Codex (external runtime), and per the Constraint Enforcer's own gate "subagents cannot use the parent session's premortem — the write must execute from the session that logged it." So either the premortem is logged in this Claude session and the commit is made here after Codex produces the diff, or Codex's output is reviewed and committed from a premortem-logged session. **Account for this in the dispatch design** — it is currently unaddressed.

**Data Governance Gate:**
- **Item 1 / RF-D** changes the canonical SEBI disclaimer text in `constants.py` — regulatory source data. The gate requires **explicit Tarun approval stated in chat** before the write. Not yet present. **Block the RF-D text change until APPROVED is stated.**
- **Item 9** — ₹17L already landed in `constants.py` under G6 (closed today). Item 9 is process/documentation formalization, low code risk — but note for the record that the source write already happened; item 9 governs its *exposure*, which is the correct framing.

**Cross-Workspace Gate — clean.** Item 8 *mirrors* a rule *from* global `~/.claude/CLAUDE.md` *into* alphaveda's local COUNCIL_RULES.md. It does **not** modify global CLAUDE.md, so the "changes affect ALL workspaces — confirm first" rule is not triggered. Mirroring downward (global→local) is safe; only the reverse would need confirmation. Worth stating explicitly so this isn't re-litigated.

**Sequencing sanity — item 8 before item 2 is governance-correct** for a second reason: the External State Write Gate (the rule item 8 installs) is precisely what governs item 2's RemoteTrigger external-state write. Installing the gate before the write it governs is the right order.

**Resource / scope reality:**
- Feasibility: **Tight but Executable** for a solo operator. Six of ten items are done or small; item 10 is explicitly de-scoped to Lynch-only, zero-new-infra — good discipline.
- **21-day revenue clock:** item 1 (landing + waitlist) is the revenue-advancing item (unblocks G8 commercial gate) and is correctly sequenced first. Aligned.
- **Scope additions this council introduced** (each needs a trade-off, per Framework 2): UX seat's Class-column completion folded into item 10, and the CI plain-English gloss into 3+4. Both are small and reuse existing lexicon/glossary infra — displace nothing material, but name them in the design brief so they're not "while we're here" creep. Calibration seat's expanded item-7 first tranche is documentation, no build cost.
- DB Integrity: no schema changes proposed (RF-D, item 9 use existing columns; item 2's idempotency key should reuse the existing date field, not add a column — confirm at design time).

**VERDICT: APPROVE WITH MODIFICATIONS** — log premortems for item 8 (COUNCIL_RULES.md) and item 2 (ingest.py/scheduler, resolving the Codex-vs-parent-session premortem ownership); secure explicit Tarun data-governance approval before the RF-D disclaimer-text change; register the two council-added scope items in the design brief.

---

## Combined Verdict

**READY TO MOVE TO DESIGN/SOLUTIONING — conditional on folding the modifications below into the design brief. No BLOCK from any seat.**

Every finding is an additive scope/governance/documentation refinement — none is a structural or design flaw requiring re-architecture. The sequence itself is endorsed by all five seats (SRA and Constraint Enforcer both independently confirm 8-before-2 and 9-earlier are correct).

**Must be carried into the design brief before build:**
1. **RF-D (item 1):** reconcile 4 surfaces to canonical `constants.py`; update `sebi.spec.ts`; delete stale Vercel env var; Simple+Pro substance-equivalent — **and get explicit Tarun data-governance approval before changing the disclaimer text.**
2. **Item 9:** apply the gate retroactively — verify already-live ₹17L is walled from unauthenticated routes (NG-2 gate holds) and public ledger carries no personal P&L.
3. **Items 3+4:** ship the Wilson CI *with* an always-visible plain-English gloss, never bare.
4. **Item 10:** complete Class-column consistency (all Lynch categories, both modes) or it worsens the pilot's #2 issue.
5. **Item 2:** name the idempotency key (target trading date); re-point the watchdog; close only after G23's ≥2-scenario retest, not on syntax-verify.
6. **Item 7:** first tranche must log the `load_weights()` bypass, RF-F T+1 horizon (no cross-horizon pooling), proof-window exit criterion (30 obs per-instrument, start 2026-07-13) + G23 gap caveat; disambiguate G1-deferral vs `load_weights()`-deferral.
7. **Governance:** log premortems for items 8 and 2 (resolve Codex-vs-parent-session premortem ownership for item 2).

Item 8's cross-workspace posture is clean (mirroring global→local, not editing global).
