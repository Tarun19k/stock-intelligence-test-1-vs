# Prediction Model — Learning Loop, Versioning & Hit-Rate Diagnosis

**Date:** 2026-07-16
**Author:** Claude (research/synthesis pass, Opus)
**Source PDF:** `Knowledge Repository/Claude for Teachers Program.pdf` (203 pages) — *learning/evolution/feedback angle* (the RAG/retrieval angle is covered separately in `agentic-operations/docs/rag-second-brain-to-alphaveda-2026-07-16.md` and is not repeated here)
**Grounding (real code/docs read):** `src/signals/engine.py`, `src/signals/weights.py`, `docs/GAP_REGISTER.md`, `scripts/ingest.py`, `scripts/backtest.py`, `~/.claude/skills/calibration-integrity/SKILL.md`, git log of `src/signals/`
**Live numbers worked with:** 30 resolved predictions · 46.7% hit rate (≈14/30) · −0.01% avg return · T+1 horizon (RF-F) · Quarter Kelly · 30-obs cold-start threshold

---

## 1. What the PDF actually offers on this angle — honest, not padded

The RAG pass called this PDF "misleading filename, mostly a RAG operating-system design." That was true for *that* angle. For **iterative learning, versioning, feedback loops, and self-evolving methodology, the PDF is not thin — its final third (roughly pages 171–200) is a purpose-built framework for exactly this question.** It carries real weight and should not be force-fit-dismissed. The load-bearing ideas:

**a) The circularity problem — the single most important idea for AlphaVeda (p29).**
> "Claude builds the Skill, teaches the Skill, administers the test, grades the test, and declares the Skill successful. That is not sufficient assurance."

The fix: at least some evaluation must use *fixed expected outputs, deterministic checks, independent human review, and **real operational results**.* Translated to AlphaVeda: **the signal engine must never certify its own edge. The accuracy ledger of real resolved outcomes is the independent evaluator — the one thing in the system that isn't the model grading its own homework.** This is philosophically what the `calibration-integrity` seat already guards ("A calibration number is a promise… resolve outcomes against reality, never against the prediction's own assumptions"). The PDF gives that instinct a name.

**b) The multi-loop model (p31, p173).** The system should run distinct loops — Knowledge, Skill, Workflow, Incident/Problem, **Evaluation**, Model — and *"all three feed an independent governance and evaluation loop… where evidence—not Claude's confidence—determines what is promoted."* AlphaVeda's analogue: signal generation (the model loop) must be gated by a separate evaluation loop (the ledger) before any parameter change is promoted.

**c) The closed operating cycle (p175).** The measurable-outcomes lifecycle:
> Define → Baseline → Measure → Validate → Analyze → Review → Act → Verify → Standardize → Repeat

with the explicit warning that metrics defined once and never revisited create "a closed management loop in which evidence continuously informs decisions" *only if* you actually run the loop. AlphaVeda currently defines and measures, but does not systematically Analyze→Act→Verify.

**d) Five named feedback loops (p192–193).** Most relevant:
- *Operational:* Execution → Measurement → Exception detection → Corrective action → Retest → Stabilization
- *Strategic:* Outcome trend → Value assessment → Priority decision → Roadmap adjustment → New target
- Rule: *"Feedback loops should produce **traceable changes**, not only discussion."*

**e) Three tiers of response to a missed threshold (p193):** Containment (suspend/fallback) → Correction (fix the item) → Corrective action (fix the root cause). This is the same Detect→Log→Contain→Diagnose→Fix→Retest→Review→Monitor lifecycle the RAG pass flagged as idea #8 — **and which `GAP_REGISTER.md` has already adopted** (header note added 2026-07-16, first applied at G23).

**f) Versioned, owned, review-scheduled documents (p35, p42, p106).** Every knowledge article carries a standard header including **Version, Owner, Review Cycle, and Change History**, answers one question, and has "one primary purpose, one owner, and one review cycle." Higher-risk material gets **shorter review cycles** (p58).

**g) Phased maturity — don't place rules on an immature system (p59, p173).** Phase 1 minimum core → Phase 2 add *version control + review cycles* → Phase 3 automation → Phase 4 optimization. Plus the pilot-honesty rules (p173): *"Measure the current state first — without a baseline, benefits will be subjective," "Define failure of the pilot honestly — a pilot should be able to prove the approach is not yet viable," "Make evaluation independent."*

**h) Metric-gaming guardrails (p197).** *"Prohibition on retrospective formula changes without approval"*; don't optimize the metric instead of the result; periodically review the metric itself (retain / refine / replace / retire). Examples of gaming include *"increasing retrieval success by narrowing supported questions"* — the direct analogue of quietly shortening a prediction horizon to make a hit rate look better.

**Verdict on the PDF:** genuinely applicable, not a stretch. It supplies a complete vocabulary (independent evaluation, versioned methodology, closed operating cycle, traceable feedback loops, phased maturity, anti-gaming) that maps cleanly onto AlphaVeda's exact situation.

---

## 2. Current state of AlphaVeda's model documentation & feedback loop — honest audit

### 2.1 Is there a documented, versioned methodology? — **No deliberate practice. Git + scattered rationale is the only record.**

- The signal engine has **6 commits total** (`git log src/signals/`). There is **no methodology changelog, no versioned methodology doc, no parameter-history record.** The model's load-bearing choices — `horizon_days=1`, `QUARTER_KELLY_FRACTION=0.25`, `OBSERVATION_THRESHOLD=30`, `ARBITRATION_MARGIN`, the `min(confidence/100, hit_rate)` calibration formula — exist only as **current-state constants and code**, with git commit messages as the sole trail of *why* they are what they are.
- The closest thing to a methodology-versioning practice is **`RF-F` in `GAP_REGISTER.md`** — a genuinely good "conscious deviation" record explaining *why* T+1 was kept against the council's T+5 ruling, and under what conditions to revisit. But it is a single ad-hoc entry, not a standing practice. Rationale for other parameters is **scattered across RF/G entries and design docs** (`ALPHAVEDA_DESIGN_OVERVIEW.md`, `MVP_SPEC.md`), not consolidated or versioned.
- `GAP_REGISTER.md` *did* just (2026-07-16) adopt a reason-code + RCA lifecycle "adapted from a knowledge-governance pattern reviewed this session" — i.e. this very PDF's idea (f/e above). That is the **seed** of a methodology-evolution practice, currently applied only to incident tracking (G23), not to model-parameter evolution.

**Bottom line:** there is no real methodology-versioning practice yet. Git history is the record. RF-F shows the team *knows how* to write a good conscious-deviation entry — it just hasn't been generalised into a standing log.

### 2.2 Does a feedback loop exist from real outcomes back into the model? — **A thin one exists and it is mostly dormant. The real "outcomes → model improvement" loop does not.**

This is more nuanced than a flat "no." `emit_signal()` **does** read `accuracy_outcomes` back (`engine.py` lines 178–198): it computes a per-instrument `hit_rate` and `streak_count` from resolved outcomes and feeds `hit_rate` into `calibrate_confidence()`. So real outcomes *do* influence future emitted numbers. **But the loop is weak on four counts, all verifiable in code:**

1. **It's a cap, not calibration.** `calibrate_confidence()` returns `min(confidence/100, hit_rate)` — it only ever *shrinks* the confidence number toward the observed hit rate. `backtest.py:140` says so explicitly ("a cap, not true calibration, so results cluster near one hit_rate line"); `G7` confirms warm/Platt calibration is a placeholder.
2. **It touches only the confidence *number*, never the *direction* or *which signals fire*.** A bad hit rate lowers the displayed confidence; it never changes what the model predicts.
3. **It is per-instrument, so it is dormant in practice.** `segment_obs` counts observations **per `instrument_id`**. With ~30 resolved outcomes spread across many tickers, essentially every instrument sits below the 30-obs threshold and runs on the **`hit_rate = 0.5` cold-start default** — so the feedback term is `min(confidence/100, 0.5)` for almost every live prediction. The loop is wired but rarely activated. (`G14`: no scheduled backfill to reach the threshold; `G19`: the UI's pooled denominator hid this.)
4. **Signal weights only change by manual human approval.** `weights.py::approve_signal_weight()` moves a weight `PROPOSED → ACTIVE` and is explicitly human-only ("automation is prohibited"). There is **no automated path** from outcomes to re-weighted signals.

**One more finding worth flagging:** in the live path, `emit_signal()` calls `load_weights()` (line 124) but then **builds a hardcoded single `momentum_price` signal with `weight=1.0` (line 164) and never uses the loaded weights.** The multi-signal weighting machinery exists but is **bypassed** — the live model is literally one momentum feature over ~21 trading days. (Not a bug per the MVP framing, but it reframes the diagnosis in §3.)

**Bottom line:** `accuracy_outcomes` is *not* a pure one-way ledger — it feeds a confidence cap. But it is not a learning loop in any meaningful sense: it can only make the model quieter, never smarter, and for the current sample it barely fires at all.

---

## 3. Is 30 observations at 46.7% statistically meaningful? — **No. It is indistinguishable from a coin flip, in either direction.**

Direct reasoning (n = 30, hits ≈ 14):

- **Hypothesis test vs a coin flip (p=0.5):** expected 15 hits, SD = √(30·0.25) = 2.74. Observed 14 → z = (14−15)/2.74 = **−0.37**, two-sided p ≈ **0.72**. Not remotely significant. 14 hits is exactly what a fair coin produces routinely.
- **Wilson 95% confidence interval for 14/30 ≈ [30%, 64%].** The true hit rate could plausibly be anywhere from 30% to 64%. **50% sits squarely inside.** The data cannot distinguish "broken model" from "coin flip" from "a genuine 60% edge that happened to underperform its sample."
- **The −0.01% average return is economically zero** — one-hundredth of one percent. It is consistent with *no edge*, not with a *broken* model. A truly broken (anti-predictive) model would show a persistent negative return with a tight interval; this shows ~zero with a wide one.
- **Power:** to detect a real 5-point edge (55% vs 50%) at 80% power needs **~700+** observations; even a 10-point edge (60%) needs **~150+**. **n=30 has near-zero power to detect any realistic edge.** Absence of evidence here is not evidence of absence.
- **The number is unsurprising by construction.** The live model is a single momentum feature evaluated at **T+1** (§2.2). A one-day-ahead directional call from one momentum signal is dominated by daily noise; **~50% is the *expected* baseline, not a failure.** RF-F kept T+1 deliberately as "the strictest test of whether the signal has any real edge at all" — and the honest read of the result so far is "no measurable edge yet, on a sample far too small to conclude anything."

**Verdict:** Do **not** treat "46.7% — worse than a coin flip" as a signal-failure finding. It is noise. The single most valuable thing to do with this number is to publish it *with its confidence interval* so it is not misread — both internally and (if ever shown) to users. This is exactly the PDF's "define failure of the pilot honestly" + "make evaluation independent" discipline (p173).

---

## 4. Proposed practice going forward — grounded in the PDF, sized to the real system

The PDF genuinely supports a concrete practice here. Four moves, in PDF terms, each mapped to AlphaVeda reality:

**P1 — A single versioned Methodology Log (PDF §f: Version/Owner/Review Cycle/Change History header).**
One doc — `docs/METHODOLOGY_LOG.md` — recording every change to the model's load-bearing parameters (`horizon_days`, calibration formula, `OBSERVATION_THRESHOLD`, `QUARTER_KELLY_FRACTION`, `ARBITRATION_MARGIN`, weight sets) with: the change, the date, the **evidence that justified it**, and the reviewer. **`RF-F` is already a perfect specimen entry — generalise it.** This replaces "git history is the only record" with a deliberate, one-owner, reviewable trail. Low cost, high durability, and it is precisely what was asked for.

**P2 — An observation-gated review cadence, not a calendar one (PDF §c closed cycle + §g phased maturity).**
Run the PDF's Define→Baseline→Measure→Analyze→Act→Verify→Standardize cycle against the accuracy ledger, **triggered by observation milestones, not dates** — e.g. a formal review each time any segment crosses 30 / 100 / 200 resolved obs. Reviewing on the calendar at n=30 invites exactly the noise-chasing error §3 warns against. Gating on evidence volume is the PDF's phased-maturity rule applied literally.

**P3 — The independent-evaluation gate as an explicit rule (PDF §a circularity + §b evaluation loop).**
Codify: *no model-parameter change may be promoted on the model's own confidence; it must be justified by real resolved outcomes in the ledger, reviewed by the `calibration-integrity` seat.* This already exists as instinct — make it the written gate in the Methodology Log's change procedure.

**P4 — The anti-gaming clause (PDF §h).**
Adopt verbatim the rule *"no retrospective formula change without approval"* and *"do not narrow the question to inflate the metric."* Concretely: **never widen the horizon (T+1→T+5) or retune calibration to make the hit rate look better.** RF-F's conscious-deviation record is the template — any horizon change must be a logged, evidence-justified entry, never a quiet edit. This directly protects the accuracy ledger, which the revenue roadmap names as AlphaVeda's only real moat-seed.

*What the PDF does NOT justify:* building automated weight-learning or Platt scaling now. The PDF's own phased-maturity principle (p59: "the initial repository may be too immature to support the rules placed upon it") says the opposite — with the loop dormant and n=30, the honest cold-start cap is the correct interim, exactly as `G7` already states. Don't build the sophisticated loop before there's data to feed it.

---

## 5. Ranked next steps by leverage — grounded in the actual code, not generic ML advice

1. **Stop treating the hit rate as a finding; publish it with its CI.** No model change is justified by n=30 (§3). Add the Wilson interval wherever the hit rate is surfaced so "46.7%" is never misread as "broken." Zero cost; prevents the highest-probability mistake (overfitting to noise). Everything below depends on this discipline holding.
2. **Recognise the real diagnosis: the live model is one momentum feature at T+1, and `load_weights()` is loaded-but-unused in `emit_signal()` (line 124 vs 164).** The multi-signal edge the architecture was built for is bypassed. The honest lever for a *real* edge is wiring the fundamental/multi-signal weighting — which is blocked behind empty fundamentals data (`G1`, BSE XBRL parser built but never scheduled). "Calibration is broken" is the wrong frame; "the model is running on one noisy feature because the other signals aren't wired" is the right one.
3. **Fix the attribution blindspot (`G5`, `prediction_components` schema) before any tuning.** You currently cannot tell *which* signal caused a miss. Even with one live signal today, per-signal attribution is the hard prerequisite for any genuine outcomes→model loop. This is the true unblock, ahead of any calibration work.
4. **Resolve the cold-start denominator reality (`G14`/`G19`) so the loop can actually activate.** Either accept a pooled-segment calibration (with the G19 honesty fix already applied to the UI) or concentrate predictions on fewer instruments to reach 30 obs *somewhere*. Until this changes, the feedback term is `min(conf, 0.5)` for nearly every prediction — the loop never fires.
5. **Stand up the Methodology Log + observation-gated cadence (P1–P4 above).** Cheap, durable, and the deliverable Tarun asked for. Generalise RF-F; adopt the anti-gaming clause the same day.
6. **Defer T+5 (`RF-F`) and real Platt calibration (`G7`) until ≥~150–200 resolved obs per segment exist.** The PDF's phased-maturity and anti-gaming rules say explicitly: don't do this early. Widening the horizon now would let a same-day-noise signal claim a 5-day track record it hasn't earned — and would be indistinguishable from metric-gaming.

---

*This report deliberately avoids proposing any change to `engine.py`, calibration math, or the horizon. Per §3 and §4, no such change is justified on the current evidence — the leverage is in attribution (G5), data wiring (G1), and a documented, independent, evidence-gated review practice, not in retuning a model against 30 noisy observations.*
