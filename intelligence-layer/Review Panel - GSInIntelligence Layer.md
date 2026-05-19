# **The Framework Audit — Skills, Panel & Stress-Test Design**

(Ask questions against all gaps identified or low clarity of ask)

## **Prompt for Claude: You are acting as a principal architect, intelligence-systems strategist, product thinker, and adversarial reviewer for the GSI application.**

Project context:
- Product: GSI application / Global Stock Intelligence app
- Current app URL: https://stock-intelligence-test-1.streamlit.app/
- Objective: design a production-grade "skill" first, and then an extensible "intelligence layer" for GSI that can evaluate stocks, generate market interpretations, improve prediction quality, surface alphas, and support near-accurate probabilistic forecasts using multiple algorithms and supporting models.
- This is not a generic AI feature request. It is a systems-design, reasoning, orchestration, and decision-support problem.
- Your output should help me turn this into a clear implementation and prompting plan for Claude-based development.

Important context you must internalize before answering:
1. The current Global Intelligence concept is ambitious and differentiated, but its execution has previously shown major weaknesses:
   - too narrow thematic coverage,
   - stale or misleading “live” content,
   - broken external dependency patterns,
   - weak linkage between macro intelligence and market implications,
   - zero or insufficient quantitative overlays,
   - static text pretending to be live intelligence,
   - poor context switching across markets,
   - and compliance/disclaimer risk when surfacing actionable stock ideas.
2. Therefore, your job is not to praise the concept. Your job is to pressure-test it, de-risk it, and engineer the next steps so rigorously that weak logic gets exposed early.
3. You must think in terms of:
   - architecture,
   - data integrity,
   - model orchestration,
   - decision logic,
   - explainability,
   - regulatory/compliance boundaries,
   - confidence scoring,
   - failure modes,
   - product UX,
   - and phased execution.

Your mission:
Build a deeply thought-through plan for the next steps to create:
A) a Claude skill for GSI intelligence,
B) then a scalable intelligence layer for the GSI application.

The intelligence layer should eventually help with:
- evaluating stocks,
- generating structured stock theses,
- identifying market regimes,
- detecting macro-to-market linkages,
- supporting scenario analysis,
- surfacing alpha signals,
- combining multiple algorithms/models,
- and producing probabilistic, explainable predictions rather than shallow recommendations.

Your output must be written for an operator-builder, not an academic.

WORKING STYLE RULES:
- Ask hard questions wherever the ask is underspecified.
- Challenge assumptions rather than smoothing over them.
- Do not jump straight to a solution.
- First identify ambiguity, risks, hidden assumptions, and missing decisions.
- Then build a staged plan.
- Then run multiple premortem iterations.
- Then revise the plan after each premortem.
- Continue until you can justify a confidence score of 99%+ OR explicitly state why 99% is not honestly achievable yet.
- Never fake certainty.
- Prefer a lower honest confidence score over a polished hallucination.

REQUIRED OPERATING LENS:
Use a multi-panel expert reasoning framework inspired by:
- Buffett = business quality / long-term durability / discipline
- Munger = inversion / error elimination / checklist thinking
- Dalio = macro regime / debt cycle / cross-asset linkages
- Druckenmiller = dominant factor / timing / regime shifts
- Howard Marks = cycle position / second-level thinking / risk asymmetry
- Soros = reflexivity / narrative feedback loops / regime breaks
- Peter Lynch = know-what-you-own / ground-truth practicality

Do NOT roleplay them theatrically.
Instead, use them as analytic lenses and label where each lens materially changes the design.

NON-NEGOTIABLE OUTPUT STRUCTURE:

## 1. Clarify the ask
- Restate what I am actually trying to build.
- List all ambiguities, contradictions, and unresolved choices.
- Ask the minimum necessary high-value questions.
- Separate:
  - what is known,
  - what is assumed,
  - what is unknown,
  - what is dangerous to assume.

## 2. Define the end-state
Describe what a mature GSI intelligence layer should actually do.
Include:
- user jobs to be done,
- system capabilities,
- decision outputs,
- confidence outputs,
- explainability requirements,
- compliance boundaries,
- and what “good” looks like.

Also distinguish:
- a “skill”,
- an “intelligence layer”,
- a “forecasting engine”,
- a “signal engine”,
- and a “decision-support layer”.

## 3. Design principles
Propose first-principles design rules for the system.
These should cover:
- truth over fluency,
- probabilistic outputs over deterministic claims,
- source freshness,
- market-context awareness,
- cross-market adaptability,
- explainability,
- fail-safe behavior,
- no static text disguised as live intelligence,
- no unsupported stock recommendations,
- explicit confidence + evidence separation,
- and human override where needed.

## 4. System architecture
Design the architecture in layers.
At minimum cover:
- data ingestion layer,
- data quality and freshness layer,
- feature engineering layer,
- market regime layer,
- stock evaluation layer,
- signal aggregation layer,
- alpha discovery layer,
- prediction layer,
- narrative/explanation layer,
- UI decision layer,
- audit/compliance layer,
- and monitoring/feedback layer.

For each layer provide:
- purpose,
- inputs,
- outputs,
- failure risks,
- observability requirements,
- and whether it should be deterministic, statistical, heuristic, or LLM-assisted.

## 5. Skill-first roadmap
Before building the full intelligence layer, define the best first Claude skill to build.
Explain why this should be first.
It must be:
- high leverage,
- measurable,
- hard to fake,
- useful even before the full system exists.

Include:
- exact responsibilities of the first skill,
- what it must not do,
- required inputs,
- expected outputs,
- rules,
- evaluation criteria,
- and example invocation patterns.

## 6. Algorithm and model stack
Recommend a multi-model architecture.
Cover categories such as:
- rules engines,
- factor models,
- technical indicators,
- macro regime classifiers,
- probabilistic forecasting models,
- anomaly detection,
- event-impact mapping,
- ranking models,
- ensemble methods,
- and LLM reasoning modules.

For each category explain:
- why it exists,
- what problem it solves,
- what its weaknesses are,
- and how it should be combined with other layers.

Do not pretend one model can solve everything.

## 7. Alpha framework
Define what “finding alpha” should mean in this system.
Break alpha into categories such as:
- valuation dislocations,
- trend continuation,
- mean reversion,
- earnings/fundamental revisions,
- macro transmission effects,
- cross-asset dislocations,
- sentiment/narrative divergence,
- and event-driven opportunities.

For each:
- define the signal,
- define evidence needed,
- define likely false positives,
- define when not to use it.

## 8. Prediction philosophy
Explain how the system should think about predictions.
Must include:
- point estimate vs probability band,
- base rates,
- scenario trees,
- confidence intervals,
- when “no edge” is the correct answer,
- regime sensitivity,
- and how to avoid false precision.

Make clear how “near accurate” should be translated into a realistic product promise.

## 9. Next steps roadmap
Create a staged roadmap:
- Phase 0: framing and risk containment
- Phase 1: first skill
- Phase 2: intelligence layer MVP
- Phase 3: quantitative expansion
- Phase 4: adaptive learning and feedback loops
- Phase 5: production hardening

For each phase include:
- goals,
- deliverables,
- dependencies,
- risks,
- kill criteria,
- and success metrics.

## 10. Premortem round 1
Assume the project failed badly after 6 months.
List the top reasons.
Include:
- product failure,
- data failure,
- model failure,
- UX failure,
- trust failure,
- compliance failure,
- and organizational failure.

Then revise the roadmap.

## 11. Premortem round 2
Run a harsher premortem as if a quant PM, a skeptical trader, and a compliance officer all attacked the design.
Forcefully identify:
- hidden overfitting,
- narrative hallucination,
- stale data risk,
- false signal confidence,
- unexplainable recommendations,
- and misleading UX patterns.

Then revise the architecture and roadmap again.

## 12. Premortem round 3
Now assume the system technically works but still fails to create user trust or differentiated value.
Explain why.
Then revise:
- the product scope,
- user-facing outputs,
- and deployment sequence.

## 13. Known unknowns registry
Create an explicit table of:
- unknowns,
- why each matters,
- how to resolve it,
- and what assumptions are currently unsafe.

## 14. Confidence scoring
Score confidence separately for:
- product framing,
- architecture quality,
- first skill choice,
- model strategy,
- roadmap quality,
- compliance safety,
- and implementation realism.

Then provide:
- current overall confidence score,
- why it is not higher,
- what exact evidence would be needed to reach 99%,
- and whether 99% is honestly attainable at this stage.

## 15. Final deliverables
End with these exact artifacts:
1. A one-page executive summary
2. A builder-ready next steps plan
3. A skill spec for Claude
4. An intelligence-layer architecture spec
5. A premortem findings summary
6. A priority decisions list
7. A “do not build this wrong” warning list

QUALITY BAR:
- Be concrete, not generic.
- Use tables where helpful.
- Expose tradeoffs.
- State failure modes explicitly.
- Avoid buzzwords unless operationalized.
- Distinguish live data, derived signals, inferred narratives, and speculative outputs.
- If a step depends on information I have not provided, say so clearly.
- If 99% confidence cannot yet be justified, say exactly what blocks it.

EXTRA INSTRUCTION:
Where appropriate, convert vague ideas into operational constructs.
Examples:
- “evaluate stocks” -> define scoring dimensions, evidence schema, and decision logic
- “find alpha” -> define alpha classes, signal tests, and invalidation rules
- “near accurate predictions” -> define calibration, hit-rate, Brier score, probability bands, and abstention conditions
- “intelligence layer” -> define orchestrator, memory, models, evidence graph, and decision outputs

Your answer should be comprehensive, highly structured, adversarially robust, and implementation-oriented. 

## **Prompt for Claude ends**

## **First — The Honest Answer to "Are Buffett & Munger Sufficient?"**

**No. They are not.**  
Here's why, stated plainly:  
Buffett and Munger are the greatest **business quality \+ long-term value** investors in history. But your specific problem has **four dimensions** that fall outside their core competency:

| Your Problem Dimension  | Buffett/Munger Coverage  | Gap  |
| :---- | :---- | :---- |
| Precious metals as an asset class  | ❌ Buffett actively avoids gold  | Blind spot — they would dismiss the entire thesis  |
| Macro timing (Fed, dollar, rates)  | ⚠️ Munger understood macro but avoided timing  | Partial — they'd say "don't time markets"  |
| Commodity supply/demand cycles  | ❌ Neither specialised here  | Significant gap  |
| 6–12 month tactical allocation  | ❌ Their horizon is 10–20 years  | Fundamental mismatch  |
| Portfolio construction & sizing  | ✅ Munger's concentration principles apply  | Strong coverage  |
| Behavioural discipline  | ✅ Both — their greatest strength  | Strong coverage  |
| Tax-efficient execution  | ✅ Buffett is obsessive about this  | Strong coverage  |
| Derivatives & ETF structure  | ⚠️ Buffett uses derivatives sparingly  | Partial  |

**Conclusion:** Buffett and Munger give us the **philosophical skeleton** — discipline, margin of safety, inversion, concentration. But we need **5 additional experts** to cover the gaps your specific problem demands.  
---

## **The Full Expert Panel — 7 Minds**

*Each brings a distinct, non-overlapping lens. Together they cover every dimension of your problem.*  
---

### **1\. Warren Buffett — Value & Business Quality**

**Role on panel:** Chief Discipline Officer  
**What he contributes:**

* Circle of competence — only act within what you understand deeply  
* Margin of safety — never pay full price  
* Long-term business quality over short-term price action  
* Tax efficiency — never sell a great business for a mediocre one

**Limitation here:**

* Actively anti-gold: *"Gold has no utility"*  
* 10–20 year horizon vs your 6–12 months  
* Would likely tell you to hold your compounders (NALCO, PFC, NLC) and do nothing

**His single most useful question for your plan:**  
*"If you couldn't sell this ETF for 5 years, would you still buy it?"*  
---

### **2\. Charlie Munger — Mental Models & Inversion**

**Role on panel:** Chief Error-Elimination Officer  
**What he contributes:**

* Inversion — find every way the plan fails before it starts  
* Latticework of mental models — no single-lens thinking  
* Incentive analysis — why is this trade popular right now? Who benefits?  
* Checklist methodology — eliminate errors systematically

**Limitation here:**

* Also skeptical of commodities as investments  
* Academic about macro — wouldn't give you price targets

**His single most useful question:**  
*"What would have to be true for this to go catastrophically wrong?"* *(We built the premortem from this — Munger's contribution is already embedded)*  
---

### **3\. Ray Dalio — Macro, Cycles & All-Weather Portfolio**

**Role on panel:** Chief Macro Officer  
**Why he's essential:** Ray Dalio built the **All-Weather Portfolio** specifically designed to perform across all economic environments. He is the world's foremost authority on:

* How gold behaves across the debt cycle  
* The relationship between real interest rates, dollar strength, and gold  
* The "Beautiful Deleveraging" framework — when gold outperforms vs underperforms  
* Paradigm shifts in global reserve currencies

**Dalio's framework directly applied to your plan:**

| Economic Environment  | Gold  | Silver  | Probability Now  |
| :---- | :---- | :---- | :---- |
| Rising growth \+ Rising inflation  | ✅ Strong  | ✅ Strong  | Low  |
| Falling growth \+ Rising inflation (Stagflation)  | ✅✅ Very strong  | ⚠️ Mixed  | **Medium — current** |
| Rising growth \+ Falling inflation  | ❌ Weak  | ✅ Strong (industrial)  | Low  |
| Falling growth \+ Falling inflation (Deflation)  | ⚠️ Mixed  | ❌ Very weak  | Medium  |

**Current environment** (US CPI 3.8%, slowing growth fears, strong dollar) \= **Stagflation leaning.**Dalio's framework says: **gold outperforms silver in stagflation.** This directly contradicts a silver-heavy allocation.  
**His single most useful question:**  
*"What is the debt cycle position and how does it affect every asset class simultaneously?"*  
---

### **4\. Stanley Druckenmiller — Macro Timing & Concentration**

**Role on panel:** Chief Timing Officer  
**Why he's essential:** Druckenmiller is the greatest macro trader in history — **30 years, never a losing year, average 30% annual returns.** He is the master of:

* Identifying the **one dominant macro factor**driving everything  
* **Concentrating heavily** when conviction is high (he bets 100% on his best idea — not 15%)  
* Knowing **when the thesis changes** and exiting immediately  
* Understanding currency markets and their effect on commodities

**His framework for your problem:** Druckenmiller would ask: *"What is the dominant factor?"* Right now the answer is: **the US Dollar.** Everything else — gold, silver, equities — is downstream of the dollar move. His approach:

1. Get the dollar call right first  
2. Then position in metals as a consequence  
3. Not the other way around

**His view on silver at GSR 17.5x:**  
*"Never chase a trade that's already been made. The easy money is gone. Find the next trade."*  
**His single most useful question:**  
*"What's the one thing that, if it changes, changes everything? Are you positioned for THAT?"*  
---

### **5\. Howard Marks — Risk Assessment & Market Cycles**

**Role on panel:** Chief Risk Officer  
**Why he's essential:** Howard Marks writes the most rigorous investment memos in the world. His two books — *The Most Important Thing* and *Mastering the Market Cycle* — are the definitive frameworks for:

* **Where are we in the cycle?** (Not just market cycle — sentiment cycle, credit cycle, commodity cycle)  
* **Second-level thinking** — what does the consensus think, and why is it wrong or right?  
* **Risk calibration** — the goal is not maximum return, it's the best risk-adjusted return

**Marks' cycle framework applied to metals right now:**

| Cycle Indicator  | Reading  | Implication  |
| :---- | :---- | :---- |
| Silver 1Y return: \+170%  | **Late cycle** — extreme performance  | Caution  |
| GSR at 17.5x  | **Extended** — historically extreme  | Reversion risk  |
| News tone: universally bullish on silver  | **Greed dominant** | Marks sells here  |
| RSI was 80+ before crash  | **Overbought** confirmed  | Correction underway  |
| Post-crash: RSI cooling  | **Early mean reversion** | Wait, don't catch falling knife  |

**Marks' most important insight for your plan:**  
*"The most dangerous thing is to buy something because everyone agrees it's a good idea."* Silver at ₹3.5L/kg with 170% 1Y return and universal bullish coverage \= **maximum consensus.** Marks would wait for the cycle to turn.  
**His single most useful question:**  
*"If I'm right, how much do I make? If I'm wrong, how much do I lose? Is that ratio acceptable?"*  
---

### **6\. George Soros — Reflexivity & Momentum Breaks**

**Role on panel:** Chief Sentiment Officer  
**Why he's essential:** Soros developed the theory of **Reflexivity** — markets are not efficient, they are self-reinforcing feedback loops where price movements change fundamentals, which change prices further. This is especially true in commodities.  
**Applied to silver's 2026 move:**

* Silver prices rose → triggered speculative ETF inflows → pushed prices higher → triggered more inflows → RSI hit 80 → duty hike spike → crash  
* This is a **classic reflexive bubble partial unwind** — not a fundamental repricing  
* The question Soros asks: *"Has reflexivity reversed? Are we now in the self-reinforcing downward loop?"*

**His framework for your entry timing:** Soros waits for the **trend to establish after the reversal**, not the bottom. He would say:

* Don't buy silver at ₹3.5L thinking it's cheap after 170% rally  
* Wait for a **base to form** — 2–3 months of sideways trading after the crash  
* **Then** enter with size when the new uptrend is confirmed

**His single most useful question:**  
*"Are you riding a trend or fighting a reflexive reversal? Know which one you're in."*  
---

### **7\. Peter Lynch — Know What You Own & Ground Truth**

**Role on panel:** Chief Reality Officer  
**Why he's essential:** Peter Lynch ran the Magellan Fund to a 29.2% annual return for 13 years — the greatest mutual fund record ever. His approach: **invest in what you understand from real life.** His famous line:  
*"Invest in what you know."*  
**Applied to your portfolio — Lynch would immediately ask:**

* You own NALCO (+489%) — do you know why? Do you track aluminium demand data?  
* You own Welspun Corp (+821%) — do you know their order book? Their pipeline exposure?  
* You own Hindustan Zinc (+15%) — do you know that Zinc is the primary revenue driver, not silver?

**Lynch's specific contribution:** He would do a **"know what you own" audit** on every position — and he would be deeply uncomfortable with how many metals-adjacent holdings you have **without a clear thesis for each.**  
**His single most useful question:**  
*"Can you explain in 2 minutes, to a 12-year-old, why each of these positions will make money?"*  
---

## **The Complete Panel — Roles & Coverage Map**

| Expert  | Primary Domain  | Coverage in Your Plan  | Replaces/Supplements  |
| :---- | :---- | :---- | :---- |
| **Buffett** | Business quality, long-term value  | Portfolio discipline, tax efficiency  | Foundation  |
| **Munger** | Mental models, inversion  | Premortem, error elimination  | Supplements Buffett  |
| **Dalio** | Macro cycles, all-weather  | Gold in stagflation, debt cycle  | Fills macro gap  |
| **Druckenmiller** | Macro timing, concentration  | Dollar first, then metals  | Fills timing gap  |
| **Howard Marks** | Risk & market cycles  | Cycle positioning, risk-reward  | Fills risk gap  |
| **Soros** | Reflexivity, sentiment breaks  | Entry timing after reversal  | Fills sentiment gap  |
| **Lynch** | Ground truth, know what you own  | Position-by-position reality check  | Fills accountability gap  |

---

## **What Skills Does This Panel Require From Me?**

To not return false positives under aggressive challenge, here is the **exact skill architecture** I must apply:

### **Tier 1 — Verification Skills**

* Every number must be pulled from a primary source (live data, dated news, official reports)  
* Every claim must state its source, date, and confidence level  
* Conflicting data must be presented, not suppressed (e.g., central bank net selling in March)

### **Tier 2 — Analytical Skills**

* **Multi-model synthesis** — no single framework. Apply all 7 lenses simultaneously  
* **Falsifiability testing** — every claim must be stated in a way that could be proven wrong  
* **Base rate analysis** — what actually happens to silver after a 170% 1Y run historically?  
* **Second-order thinking** — what happens after the obvious outcome?

### **Tier 3 — Anti-False-Positive Skills**

* **Steel-manning opposition** — the strongest possible case against silver must be presented, not the weakest  
* **Premortem rigor** — assume failure, work backward (already done)  
* **Known unknowns registry** — explicit list of what we don't know and can't verify  
* **Aggressive self-challenge** — I must find the errors before you do

### **Tier 4 — Execution Skills**

* **Tax-aware structuring** — every exit and entry optimised for STCL harvesting  
* **Position sizing mathematics** — not intuition  
* **Behavioural pre-commitment** — rules written before markets open, not during

---

## **The One Skill That Prevents False Positives Above All Else**

**Stating the confidence level and source of every single claim — always.**  
Not: *"Silver has a supply deficit."* But: *"Silver has had a supply deficit — per Silver Institute 2024 World Silver Survey — but the exact duration is unverified in this session. Confidence: 7/10."*  
When you challenge me aggressively, every claim either holds (because it's sourced) or falls (and I tell you exactly why it fell and what replaces it). There are no hidden assumptions left to collapse.  
---

## **Summary — The Revised Operating Framework**

Buffett     → Discipline, margin of safety, tax efficiency  
Munger      → Inversion, premortem, error elimination    
Dalio       → Macro cycle, stagflation framework, debt cycle  
Druckenmiller → Dollar first, timing discipline, concentration  
Marks       → Cycle positioning, risk-reward calibration  
Soros       → Reflexivity, entry after trend confirmation  
Lynch       → Know what you own, ground-truth audit

**Seven lenses. Zero untested assumptions. Every claim sourced and confidence-rated.**  
