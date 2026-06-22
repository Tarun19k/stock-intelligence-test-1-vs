# R3 Council — Strategic Assessment of R1 Findings and Action Plan
**Date:** 2026-06-22
**Council:** 20 voices (7 investor + 4 doctrine + 9 expert)
**Input:** R1 Red Team report (REVISE verdict, 18 gaps); design doc v0.3; 3 live migrations (0006/0007/0009)
**Verdict:** CONDITIONAL GO

> This is not a red-team pass. R1 already attacked the *design*. R3 attacks the *action plan that responds to R1* — is it complete, correctly sequenced, and does it account for present and missing challenges before Block 3.1 (v0.4 amendments) begins?

---

## Skill Gap Inventory

**Present and adequate.** The 20-seat composition covers the mathematical core (portfolio-theory, signal-engineering, behavioral-finance), the schema/infra spine (schema-design, two systems-reliability voices), the regulatory perimeter (sebi-compliance, constraint-enforcer), the data perimeter (data-licensing, market-microstructure), and the user surface (product-ux). Every R1 gap has at least one owning seat. The investor seats correctly map to the 6 guards.

**Structurally missing — three domains with NO adequate seat:**

1. **Commercial / pricing strategy (CRITICAL GAP).** T3 (WhatsApp pricing signal from a real NSE investor) is a *hard dependency* on R4 Synthesis, yet no seat in this 20-voice council owns pricing strategy, willingness-to-pay analysis, or the go/no-go economics of a paid AlphaVeda. The `panel-wealth-revenue-strategist` doctrine seat exists in the skill library and owns C10 (waitlist columns) in the trace matrix — but was **not** included in the R3 roster. This is the single biggest skill gap: the plan has a revenue-shaped critical-path bottleneck (T3) with no revenue-domain seat to de-risk it. **Add the Wealth & Revenue Strategist as the 21st voice before R4.**

2. **Quantitative validation / statistical testing.** The fixes to GAP-001 (Kelly re-derivation), GAP-002 (calibration: Platt/isotonic), and GAP-015 (shrinkage) are statistical methods that need an out-of-sample validation discipline. Iyer (portfolio-theory) and Reddy (signal-engineering) can *specify* them, but no seat owns "prove the calibration map is not overfit on n<50 per segment." With 24 segments and a 30-observation threshold, every segment is small-sample. This is a latent skill gap that becomes acute at G1, not G0 — note it now, staff it before G1.

3. **Tax / accounting boundary.** Non-goal #6 says P&L/XIRR/tax-lots live in GSI, not AlphaVeda. But Layer 4 sizes real positions against a ₹7.25L tranche. The interaction between a position-sizing recommendation and the realised-gains/STCG consequence is unowned. Low priority for MVP (single-user, manual execution) but a real seam at first subscriber.

**Recommendation:** Add Wealth & Revenue Strategist now (de-risks T3 and the entire R4 chain). Note quant-validation and tax-boundary gaps for G1 staffing.

---

## Council Votes by Seat

### 7 Investor Seats

**1. Warren Buffett — Fundamentals floor; owns GAP-010, GAP-012.**
Verdict on plan: **CONDITIONAL.** Block 3.1 fixes none of my gaps — both are scheduled pre-G1, not pre-G0, which I accept *for the math*, but GAP-010 (circuit-locked Bhavcopy) directly corrupts the fundamentals-adjacent ledger: a microcap that "hits" on three upper-circuit days inflates the very hit-rate that pressures my floor. My floor (FUNDAMENTAL_WEIGHT_FLOOR=0.30) is a static guard; it does not protect against a *polluted* ledger feeding false confidence into segments. Missing item: the plan must state that GAP-010's circuit-flag fix is a **hard pre-G1 gate**, not a "nice to have," because peak_return_pct corruption begins the day the first outcome resolves.

**2. Charlie Munger — Data integrity, quarterly review; owns GAP-008, GAP-009, GAP-013.**
Verdict: **HOLD until GAP-009 hotfix is in the plan.** GAP-009 is not a design-doc gap — it is a defect in the *already-applied* migration 0009 (I read line 17: `UNIQUE (lynch_class, regime, signal_name, status)`). My entire Guard 6 ("human approves exactly one weight") rests on "the engine reads one ACTIVE row." The live schema permits two. Amending the design doc to v0.4 does nothing to the deployed table. **Block 3.1 as written fixes a document, not the database.** This is a perverse-incentive trap: we will believe we fixed it because the doc says so. GAP-008 (doc/migration/expert drift) is the meta-defect — three artifacts describing three states — and it is *exactly how GAP-009 hid*. GAP-013 (MIN floor forcing capital into zero-edge bets) is trivial once GAP-001 is fixed but must not be forgotten.

**3. Ray Dalio — Regime-segmented accuracy; owns GAP-007, GAP-008.**
Verdict: **CONDITIONAL.** GAP-007 (regime read race) is P1 but it poisons my entire premise — a prediction tagged with yesterday's regime on a transition day contaminates two segments at once. The plan does not list GAP-007 in Block 3.1's four P0s. I accept pre-G0 sequencing *only if* the as-of-prediction-time join semantics are written into the design doc in the same pass as GAP-006 (they share the same root cause: time-series-read-as-point-in-time). Do not split them across blocks. GAP-008's resolution (migrations = single source of truth) must be done before any further migration is written, or v0.4 will drift again.

**4. Stanley Druckenmiller — Kelly, EXIT triggers, magnitude; owns GAP-001, GAP-005, GAP-014.**
Verdict: **CONDITIONAL GO — my P0 is correctly prioritized.** GAP-001 is in Block 3.1 and it is the right call to gate it. But the plan says "add downside_target column + rewrite Kelly" — that column requires a **new migration (0012)** that does not exist (I confirmed 0007 has magnitude_target, no downside). If Block 3.1 only amends the *design doc* and does not also produce the migration SQL, then Block 6 starts with a Kelly spec that has no schema to write to. GAP-005 (E2 paradox) is *my* exit trigger and it was specified backwards — the exit self-suppresses exactly when the market deteriorates fastest. It is marked P1 but it was a council-mandated condition (C4); I want it re-reviewed in v0.4, not deferred. GAP-014 (DB caps vs constants) is P2 but a silent risk-limit breach — cheap to fix, fix it now.

**5. Howard Marks — Cycle-phase, second-order; owns GAP-015, GAP-016.**
Verdict: **CONDITIONAL.** Both my gaps are P2/pre-G1, acceptable. But second-order point: GAP-015 (hard cutover at 30 obs, no shrinkage) interacts with GAP-002 (calibration). If you build calibration on top of a hard-cutover weight system, you calibrate against a discontinuity — the day a segment crosses 30, both the weight AND the calibration map jump. Fix them as a **pair** or you bake in a cliff. GAP-016 (asymmetric streak — losing streaks invisible) is the capitulation blind spot; it is the mirror of the Soros guard and should be specified in the same v0.4 subsection as GAP-004.

**6. George Soros — Counter-cyclical guard; owns GAP-004.**
Verdict: **HOLD on my condition's classification.** GAP-004 is marked P1, but Guard 2 was the *specific* condition I was seated to enforce in the 7/7 approval. The R1 finding is that it was implemented as a *logic inversion*: STREAK_DISCOUNT_FACTOR=0.7 fires at ledger aggregation, not at live emit — so at a reflexive peak the engine sizes UP exactly when I designed it to size DOWN. A guard implemented backwards is worse than no guard, because it creates false safety. **My prior approval was given against a spec that has since been shown to invert my intent. I withdraw the assumption that Guard 2 is satisfied and require GAP-004 to be promoted to a Block 3.1 fix** (emit-time discount), not a P1 deferral. This is the false-consensus trigger for the Synthesis Chair.

**7. Peter Lynch — Classification, cold-start, simplicity; owns GAP-015.**
Verdict: **CONDITIONAL.** The 24-segment design is coherent and the classification CHECK is enforced (C7, confirmed in migration 0001). My concern is small-sample fragility: 24 segments × 30-obs threshold means most cells stay cold for a long time, leaning on COLD_START_WEIGHTS. GAP-015 (no shrinkage) means the transition out of cold-start is a cliff. For a single-user tool generating maybe a handful of signals a day, several segments may *never* reach 30 — the plan needs to state what happens to a segment that is cold forever (answer: priors hold, which is fine, but say so). Keep it simple; do not over-engineer the calibration for cells that will never have data.

### 4 Doctrine Seats

**8. Shakuni (Red Team Adversary) — attacks the plan, not the design.**
The plan's central loophole: **it conflates "amend the design doc" with "fix the defect."** Block 3.1 is titled "Amend design doc to v0.4." Three of the most dangerous findings are NOT design-doc problems:
- GAP-009 is a live migration defect (deployed `UNIQUE` includes status). Editing v0.4 leaves the broken table in production.
- GAP-001's fix *requires* a new migration (0012, downside_target) — a doc edit produces a spec with no table.
- GAP-011/GAP-012 require runtime *data bindings* (converted_at → commercial mode), not prose.

So the plan claims to "fix the 4 P0 gaps" but at least one P0 (GAP-001) and one re-classified P0 (GAP-009, which I argue is P0 because it is live and silently nondeterministic) **cannot be fixed by the action the block performs.** The plan will produce a v0.4 that *reads* fixed while the database stays broken. Second loophole: **no block owns "reconcile doc against live migrations."** GAP-008 proved the artifacts already disagree; nothing in the plan re-anchors them, so v0.4 can introduce *new* drift. Third loophole: **T3 has no timeout** — the entire council chain (R4→R5→build) stalls on one WhatsApp reply from one investor, and no seat owns getting it. Fourth: the G0 gate (Block 7) tests "pytest 6/6 + 10 seeds + ingest_status" but R1 showed the C9 SEBI test asserts *presence not substance* and there is no test for missing-run detection, calibration sanity, or single-ACTIVE-weight — **the gate cannot catch the very defects this review found.** The plan fixes the design but not the gate that's supposed to verify the fix.

**9. Constraint Enforcer — SEBI, gates, governance; owns GAP-011, GAP-012.**
Verdict: **CONDITIONAL GO with a hard governance condition.** GAP-011 is the business-model time bomb: the moment `waitlist.converted_at` goes non-null, Layer 4's personalized rupee output is arguably regulated advice under SEBI IA Regs 2013, and GAP-012 (yfinance personal-use ToS) breaches at the same instant. Both currently hang on a manual env flag (`ALPHAVEDA_COMMERCIAL`) wired to nothing. The plan marks these pre-launch and excludes them from Block 3.1. **I accept deferring the *enforcement code* but NOT deferring the *gate design*** — the binding (converted_at → suppress rupee amounts AND block yfinance, fail-closed) must be specified in v0.4 now, because retrofitting a fail-closed gate after the data layer is built is far more expensive. Also flagging a governance-process point: this review itself touches an architectural-trigger surface (design doc that gates a build); per the premortem rule, the v0.4 amendment work must be logged before writing. And data-governance: no org-corpus or GSI source write is happening here, so that gate is not tripped — this is product-design work.

**10. Systems Reliability Architect — async ingest, singleton; owns GAP-006, GAP-007.**
Verdict: **GO on GAP-006 being in Block 3.1; CONDITIONAL on GAP-007 joining it.** GAP-006 (silent missing-run) is correctly a P0 in the plan — the active "expected-run" watcher + keep-alive is the right fix. But GAP-006 and GAP-007 are the **same root cause**: a time-series read treated as point-in-time with no freshness assertion. Fixing one without the other in the same pass is how the second one re-hides. Add: the keep-alive design must specify *both* the Supabase 7-day-pause prevention and the GHA 60-day-auto-disable prevention — the plan says "keep-alive for Supabase and GHA" but does not say they are different mechanisms (a scheduled query vs a committed heartbeat). Also: PARTIAL status (from Imran's review) needs an idempotency contract or re-runs double-write outcomes.

**11. Synthesis Chair — does not engage until ≥2 seats disagree or unanimous-zero-modification.**
*Engagement triggered.* See dedicated section below. (Trigger met: Soros and Druckenmiller both demand promotion of P1 conditions they originally approved; Munger demands a HOLD on GAP-009; Shakuni attacks the plan's premise — this is genuine substantive disagreement, not consensus.)

### 9 Expert Seats

**12. Prof. Sanjay Iyer (portfolio-theory) — owns GAP-001, GAP-002, GAP-013, GAP-014, GAP-015.**
Verdict: **CONDITIONAL GO.** GAP-001 and GAP-002 are correctly the two hardest P0s and both are in Block 3.1. Critical execution note the plan misses: the Kelly fix is **not just a formula rewrite** — it needs (a) the downside_target schema column [migration 0012], (b) the emit contract to *produce* a downside target (where does it come from? a stop-loss rule? the signal? this is unspecified and is its own design question), and (c) the rule that until downside exists, the Path page shows direction+confidence only, no rupee. The plan lists "rewrite Kelly formula" as if it's one edit; it is three coupled changes. GAP-013 and GAP-014 are cheap and should ride along in 3.1. GAP-002's calibration must be per-segment empirical binning with a documented fallback (cap p at measured hit_rate) for cold segments — and that fallback only works if GAP-010 (circuit pollution) is fixed, or the measured hit_rate is itself garbage.

**13. Dr. Anika Reddy (signal-engineering) — owns GAP-002, GAP-003, GAP-004, GAP-016.**
Verdict: **HOLD until GAP-003 scope is honest.** GAP-003 (arbitration.py is a total spec void) is in Block 3.1, good — but arbitration sits *upstream* of accuracy_predictions, which means whatever rule we pick silently determines what gets logged to the ledger, which determines calibration (GAP-002), which determines Kelly (GAP-001). These four are a **dependency chain, not four parallel fixes**: arbitration → confidence → calibration → Kelly. The plan presents them as a flat list of P0s. They must be specified *in dependency order* in v0.4 or the downstream specs reference upstream constants that don't exist yet. GAP-004 (streak discount at emit) and GAP-016 (losing-streak flag) belong in the same emit-flow subsection — both are emit-time interventions the current design omits.

**14. Dr. Kavya Menon (behavioral-finance) — owns GAP-004, GAP-005, GAP-015, GAP-016.**
Verdict: **HOLD — two council-mandated guards were specified backwards and must be re-reviewed, not deferred.** GAP-004 (Soros inversion) and GAP-005 (E2 deterioration paradox) are both behavioral-guard inversions: the system applies skepticism to the *historical record* but not the *live bet*, and suppresses the exit signal exactly when uncertainty (the real signal during a decline) is highest. These are marked P1. But Guards 2 and 5/E2 were the conditions that earned the 7/7 approval. **Implementing a mandated guard in the wrong direction means the prior approval was conditional on behavior the design does not deliver.** Promote both to Block 3.1. Also: Guard 6's quarterly cadence cannot catch a lollapalooza that forms and breaks inside one quarter — the emit-time discount (GAP-004 fix) is what actually closes that, which is another reason it cannot wait.

**15. Deepak Nair (schema-design) — owns GAP-008, GAP-009, the 12th migration.**
Verdict: **HOLD until the plan contains migration work, not just doc work.** I confirm from the live files: 0009 line 17 has status in the UNIQUE key — two ACTIVE rows are physically permitted today. 0007 has no downside_target. So the plan needs **two new migrations the action plan does not name**: (0011) a partial unique index `CREATE UNIQUE INDEX ... WHERE status='ACTIVE'` plus atomic demote-on-approve [GAP-009 hotfix], and (0012) `ALTER TABLE accuracy_predictions ADD COLUMN downside_target` [GAP-001]. Note: migration 0010 (ingest_status) already exists in the doc/numbering, so the next free numbers are 0011 and 0012. GAP-008 (drift) is the meta-issue: establish migrations as single source of truth and regenerate the doc's inline SQL from them, with a CI diff check, *before* writing 0011/0012, or v0.4 drifts on contact.

**16. Adv. Meera Sundaram (sebi-compliance) — owns GAP-011.**
Verdict: **CONDITIONAL GO — single-user today, but design the gate now.** Today the tool runs on Tarun's own ₹7.25L; the RIA boundary likely does not yet bind. The danger is the *transition*: at `converted_at` non-null, Layer 4's personalized position-sized list becomes advice in substance, and a yellow footer does not cure substance. The plan has **no gate that suppresses rupee amounts at conversion** and the C9 test asserts disclaimer *presence*, never the advice-vs-research *substance*. I do not require enforcement code before build, but I require v0.4 to (a) bind the commercial event to `converted_at`, (b) specify exactly what Layer 4 suppresses at that instant (rupee → directional framing), and (c) add a *substance* test, not just a presence test. Reframe Layer 4 language now ("signal X is bullish for Y") so the imperative-BUY framing is never shipped.

**17. Rohan Varghese (data-licensing) — owns GAP-010, GAP-012.**
Verdict: **CONDITIONAL.** GAP-012 shares GAP-011's trigger: yfinance personal-use ToS breaches the instant a paying subscriber exists, i.e., `converted_at` non-null. The gate must be *derived from data* (a startup check on converted_at), fail-closed when ambiguous, and `ohlcv.source` needs a `licence_class` column so a query can answer "is any commercially-served row from a personal-only provider." None of this is in Block 3.1. I accept pre-launch sequencing for enforcement but the `licence_class` column is a schema change that is cheapest to land with 0011/0012, not later. GAP-010 (circuit flags) is also a schema change (`circuit_flag`/`deliverable_volume` on ohlcv) — batch all three schema additions into one migration pass.

**18. Vikram Bhattacharya (market-microstructure) — owns GAP-010.**
Verdict: **CONDITIONAL — GAP-010 is more strategically severe than its P1 label.** The accuracy ledger *learns* from outcomes. If circuit-locked/illiquid prints are scored as real outcomes, the ledger systematically over-rewards exactly the illiquid turnaround/asset_play/microcap segments where signals are least executable — and `peak_return_pct` (Druckenmiller's magnitude metric) is the most corrupted field, and it feeds weight proposals. So the *self-improvement loop learns the wrong lesson* and compounds it quarterly. This is not a cosmetic data-quality gap; it is a corruption of the learning objective. It must be a hard pre-G1 gate. Separately: VIX_CALM_THRESHOLD=18.0 needs India-VIX calibration (not in any gap, flag it now), and dual-listed NSE/BSE names can produce two conflicting outcomes for one instrument — undefined in the schema.

**19. Tanvi Rao (product-ux) — owns GAP-017, GAP-018, suppression UX.**
Verdict: **CONDITIONAL.** GAP-017 (fixed disclaimer occludes last table row, possibly an approve/reject button) and GAP-018 (two contradicting freshness indicators) are P2 and correctly pre-G1, acceptable. But a strategic UX point the plan ignores: when the commercial gate fires and rupee amounts are suppressed (GAP-011 fix), the Path page's entire value proposition visibly changes — the user goes from "buy ₹72,500 of X" to "X is bullish." That is a jarring product downgrade at the worst moment (first paying customer). The suppression behavior must be *designed as a deliberate state*, not a degraded fallback, or the first subscriber's first impression is a feature that vanished. Also: the path page must label Kelly amounts as prior-driven (not ledger-calibrated) during cold-start — currently only the signals page carries that label.

**20. Imran Sheikh (systems-reliability) — owns GAP-006, keep-alives, missing-run watcher.**
Verdict: **GO on GAP-006 placement; add the idempotency contract.** GAP-006 is correctly a Block 3.1 P0. The watcher design is right (compute expected-last-run from cron schedule, compare to MAX(run_at), block with red banner if no OK row for the latest expected slot). Two additions the plan must capture: (1) the keep-alive is *two* mechanisms — a lightweight scheduled query to defeat Supabase's 7-day pause, and a committed/dispatched heartbeat to defeat GHA's 60-day auto-disable — say so explicitly. (2) PARTIAL status has no resume/idempotency contract; a re-run after PARTIAL can double-write `accuracy_outcomes` against the same `prediction_id`. Add a unique constraint on `accuracy_outcomes(prediction_id)` and an upsert-on-resolve rule — another schema touch for the 0011 batch.

---

## Strategic Risk Map
*(R1's 18 gaps re-sorted by STRATEGIC impact — business-model / financial / regulatory threat — not by technical P0/P1/P2 severity.)*

| Rank | Gap(s) | Strategic class | Why it outranks its technical label |
|---|---|---|---|
| **S1** | GAP-011 + GAP-012 | **Business-model / regulatory existential** | At first paying subscriber, the product simultaneously (a) emits regulated advice without RIA registration and (b) breaches yfinance ToS. Both fire on the same trigger (`converted_at`), both currently wired to nothing. P1 technically; company-ending strategically. |
| **S2** | GAP-001 + GAP-002 + GAP-013 | **Financial — the marquee number is wrong** | Layer 4 (one of 3 co-equal layers) outputs rupee amounts that are dimensionally unsound and degenerate to "1% in everything." False precision on ₹7.25L of real capital is worse than no number. |
| **S3** | GAP-009 | **Governance integrity — live, silent, nondeterministic** | Deployed schema permits two ACTIVE weights → the engine silently picks one → Guard 6's "human approves exactly one weight" is already false in production. A doc edit does not touch it. |
| **S4** | GAP-010 | **Learning-loop corruption (compounds quarterly)** | The self-improvement loop learns from circuit-locked fake outcomes and over-rewards illiquid segments every quarter. The system gets *more* wrong over time, confidently. |
| **S5** | GAP-006 + GAP-007 | **Silent-failure surface (financial tool serving dead data)** | Both pause → app serves stale signals with no error state → user sizes real capital against dead data. Same root cause; must be fixed together. |
| **S6** | GAP-004 + GAP-005 | **Mandated-guard inversion (approval was conditional on these)** | Two of the 6 council guards fire backwards. The 7/7 approval assumed correct behavior. False safety at the cycle peak. |
| **S7** | GAP-003 | **Undefined critical-path logic upstream of everything** | Arbitration silently determines ledger contents → calibration → Kelly. Unspecified = implementer-guessed load-bearing logic. |
| **S8** | GAP-008 | **Meta-defect: artifacts disagree** | This is *how* GAP-009 hid. Until migrations are the single source of truth, every future amendment can re-introduce drift. |
| **S9** | GAP-015, GAP-016, GAP-014, GAP-017, GAP-018 | **Quality / second-order** | Real but pre-G1; each cheap individually; several pair with a P0 (015↔002, 016↔004, 014↔001) and should ride those fixes. |

---

## Missing Actions (not in current plan)

The current Block 3.1 = {amend doc for GAP-001, GAP-002, GAP-003, GAP-006}. The council finds the following are **required and absent**:

1. **MA-1 — Add migration 0011 (GAP-009 hotfix), a database change, to Block 3.1.** Partial unique index `CREATE UNIQUE INDEX ... ON signal_weights (lynch_class, regime, signal_name) WHERE status='ACTIVE'` + atomic demote-prior-ACTIVE-to-SUPERSEDED on approval. Without this, the live defect persists regardless of v0.4. *(Munger, Nair, Shakuni)*

2. **MA-2 — Add migration 0012 (GAP-001 schema dependency) to Block 3.1.** `ALTER TABLE accuracy_predictions ADD COLUMN downside_target NUMERIC(6,4)`. The Kelly rewrite has no table to write to without it. *(Iyer, Druckenmiller, Nair)*

3. **MA-3 — Specify where `downside_target` comes from.** The Kelly fix needs a loss leg the signal must *produce* (stop-loss rule? ATR-based? signal-emitted?). This is an unspecified design question hidden inside "rewrite Kelly." Resolve in v0.4. *(Iyer)*

4. **MA-4 — Promote GAP-004 (Soros emit-time discount) into Block 3.1.** Apply STREAK_DISCOUNT_FACTOR to emitted confidence *before* Kelly and before the ledger write. A mandated guard implemented backwards is not a P1 deferral. *(Soros, Menon, Reddy)*

5. **MA-5 — Promote GAP-005 (E2 uncertainty-exit redesign) into Block 3.1.** Split the floor's two jobs; let low-confidence bear runs feed a separate uncertainty-exit path. Council-mandated condition C4, specified backwards. *(Druckenmiller, Menon)*

6. **MA-6 — Add GAP-007 (regime as-of-prediction-time join) to the same v0.4 pass as GAP-006.** Same root cause (time-series read as point-in-time). Define `regime_date <= emitted_at::date DESC` join + freshness guard. *(Dalio, Systems Reliability Architect)*

7. **MA-7 — Add a "reconcile doc against live migrations" step BEFORE writing v0.4 (GAP-008).** Establish migrations as single source of truth, regenerate inline SQL, add a CI diff check. Do this first or v0.4 drifts on contact. *(Nair, Dalio, Shakuni)*

8. **MA-8 — Specify the commercial gate binding in v0.4 now (GAP-011 + GAP-012), even though enforcement is pre-launch.** Bind to `converted_at`, fail-closed, define what Layer 4 suppresses, add `licence_class` to `ohlcv.source`, add a SEBI *substance* test (not presence). Designing a fail-closed gate after the data layer exists is far costlier. *(Constraint Enforcer, Sundaram, Varghese)*

9. **MA-9 — Batch all schema additions into the 0011 pass:** `circuit_flag`/`deliverable_volume` (GAP-010), `licence_class` on ohlcv (GAP-012), `UNIQUE(prediction_id)` on accuracy_outcomes + upsert rule (PARTIAL idempotency, Imran). One migration pass, not four trickle migrations. *(Varghese, Bhattacharya, Imran, Nair)*

10. **MA-10 — Add a T3 timeout/fallback to the plan.** The entire council chain stalls on one investor's WhatsApp reply with no owner and no deadline. Define: a deadline, a fallback pricing assumption to unblock R4 provisionally, and assign an owner. *(Shakuni, + Wealth & Revenue Strategist once seated)*

11. **MA-11 — Seat the Wealth & Revenue Strategist as the 21st voice before R4.** No current seat owns pricing/WTP — the exact domain T3 lives in. *(Skill-gap inventory)*

12. **MA-12 — Upgrade the G0 gate (Block 7) to test what this review found.** Add tests for: single-ACTIVE-weight uniqueness, missing-run detection firing, calibration sanity (p never exceeds measured hit_rate on cold segments), SEBI substance (no imperative BUY language), and disclaimer non-occlusion. The current "6/6 + 10 seeds + ingest_status" gate cannot catch these defects. *(Shakuni)*

13. **MA-13 — Specify the dependency ORDER of the P0 fixes in v0.4.** arbitration (003) → confidence/score function → calibration (002) → Kelly (001). They are a chain, not a flat list; downstream specs reference upstream constants. *(Reddy, Iyer)*

14. **MA-14 — Define cold-segment-forever behavior and shrinkage pairing (GAP-015↔GAP-002).** Most of 24 segments may never hit 30 obs for a single user; state that priors hold, and build calibration on shrinkage not a hard cutover, or you bake a cliff into both weight and calibration. *(Lynch, Marks, Iyer)*

---

## Synthesis Chair Assessment

*Engagement was triggered — this is NOT a false-consensus rubber stamp. Genuine substantive disagreement exists across at least four seats, and it is not noise; it is structural.*

**The named tension:** The plan classifies GAP-004, GAP-005, GAP-007, GAP-009 as P1/P1/P1/P1 (deferrable past Block 3.1). Four seats — Soros, Menon, Dalio, Munger — independently reject that classification, and Shakuni attacks the deeper premise that "amend doc = fix defect." This is not seven seats agreeing the plan is fine; it is a real fault line between **technical severity (R1's P0/P1/P2)** and **strategic/governance severity (what actually invalidates the prior approval or persists in production)**.

**The false-consensus check I am specifically guarding against:** A plan that fixes the four *mathematically hardest* gaps (001/002/003/006) and defers the rest can *look* like decisive progress and earn a quick GO. That is the trap. Three of the deferred items are not lower-stakes — they are lower-*difficulty*. GAP-009 is a one-line index but it is **live and silently breaking Guard 6 right now**; GAP-004/005 are **inversions of council-mandated guards that the 7/7 approval was conditioned on**. Difficulty and stakes are being conflated. Easy-but-live-and-governance-critical is being filed behind hard-but-not-yet-deployed.

**My thesis (adjudication):**
1. **GAP-009 is re-classified P0** for *deployment* purposes — not because the fix is hard, but because the defect is live, silent, and falsifies a Guard. It enters Block 3.1 as a migration, not a doc edit.
2. **GAP-004 and GAP-005 are re-classified pre-G0 (Block 3.1)** because they are inversions of mandated guards; deferring them means proceeding on a 7/7 approval that no longer holds. Soros's withdrawal of his "Guard 2 satisfied" assumption is valid and stands.
3. **GAP-007 joins GAP-006 in the same pass** by root-cause identity, not by severity.
4. **Shakuni's core finding is upheld:** the block must be renamed and re-scoped from "amend design doc" to **"produce v0.4 design + the migrations and gate-bindings it depends on."** A doc that reads fixed over a database that stays broken is the plan's central latent failure.

**Minority view preserved (Lynch, Marks):** do not over-engineer calibration/shrinkage for 24 segments that, for a single low-volume user, may never reach 30 observations. Sophistication that never gets data is wasted complexity. This is compatible with the thesis: build the *structure* (shrinkage, calibration slot) but accept that priors will hold for most cells indefinitely, and say so explicitly rather than implying the ledger will fill.

**Consensus that IS real (not false):** All 20 seats agree the *architecture, trace-matrix discipline, and migration craftsmanship are genuinely good* and that the four named P0s are correctly identified as P0. The disagreement is purely about **scope and classification of the response**, not about the quality of the design or the validity of R1. That is a healthy, narrow disagreement — resolvable by expanding Block 3.1, not by re-litigating the design.

---

## Final Verdict + Conditions

**CONDITIONAL GO** — proceed to Block 3.1, but only after Block 3.1 is **re-scoped and renamed** from "amend design doc to v0.4" to **"produce v0.4 design doc + dependent migrations (0011, 0012) + commercial-gate bindings, in dependency order, reconciled against live migrations."**

**Conditions that MUST be met before Block 3.1 begins:**
- **C-A (sequencing):** MA-7 first — reconcile doc against the three live migrations and establish migrations as single source of truth (closes GAP-008), or v0.4 drifts on contact.
- **C-B (scope expansion):** Block 3.1 must include MA-1 (0011 GAP-009 hotfix), MA-2 (0012 downside_target), MA-4 (GAP-004 emit-time discount), MA-5 (GAP-005 E2 redesign), MA-6 (GAP-007 regime join), and MA-8 (commercial-gate *design*). These are promoted by Synthesis Chair adjudication, not optional.
- **C-C (seat):** MA-11 — seat the Wealth & Revenue Strategist before R4, and MA-10 — give T3 a deadline + fallback + owner. The council chain cannot be allowed to stall on one WhatsApp reply.

**Conditions that MUST be met before Block 3.1 COMPLETES (i.e., before R4 sign-off):**
- MA-3 (downside_target source rule), MA-13 (P0 dependency order documented), MA-9 (batched schema additions: circuit/liquidity, licence_class, outcomes idempotency), MA-12 (G0 gate upgraded to test the found defects).
- GAP-010 declared a **hard pre-G1 gate** (Buffett, Bhattacharya) — learning-loop corruption is not optional cleanup.

**Answers to the six strategic questions:**
- **Q1 (GAP-009 live defect):** No — the plan as written only amends the doc. **Must add migration 0011.** Re-classified P0 by Synthesis Chair.
- **Q2 (12th migration):** No — `downside_target` does not exist and is not captured. **Must add migration 0012** with the SQL in the v0.4 amendment.
- **Q3 (GAP-011 SEBI business-model risk):** Not addressed; no gate suppresses rupee at `converted_at`. **Must design the binding now** (enforcement may be pre-launch).
- **Q4 (parallel build):** Yes — the data layer (migrations 0011/0012, providers, ingest, keep-alive) is independent of Kelly/calibration and **can start in parallel with the v0.4 math amendments.** Recommend decomposing Block 6 so the schema/data stream begins immediately after C-A/C-B migrations are specified.
- **Q5 (T3 bottleneck):** Critical, unowned, no timeout. **MA-10 + MA-11 mandatory** — deadline, fallback pricing assumption to unblock R4 provisionally, and a revenue seat to own it.
- **Q6 (re-review of Guards 2 & E2):** **Yes — Soros and Druckenmiller/Menon withdraw the assumption that their conditions are satisfied.** GAP-004 and GAP-005 are promoted into Block 3.1; the prior 7/7 approval does not cover backwards-implemented guards.

**Why CONDITIONAL GO and not HOLD:** The design is fundamentally sound — architecture, trace matrix, and migration discipline are real. R1's findings are valid and the four hardest gaps are correctly prioritized. The failure is not in the design or in R1; it is that the *action plan under-scopes its own response* (doc-edit where database/runtime/gate changes are required) and *under-staffs the revenue bottleneck*. These are fixable by expanding and re-sequencing Block 3.1, not by stopping. A HOLD would be warranted only if the design itself were unsound; it is not.

**Why not unconditional GO:** Because four strategically-critical items (GAP-009 live defect, GAP-004/005 mandated-guard inversions, the missing revenue seat) would otherwise be deferred behind a doc that reads "fixed" — the precise false-consensus the Synthesis Chair was convened to prevent.
