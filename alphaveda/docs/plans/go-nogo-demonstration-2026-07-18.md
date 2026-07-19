# AlphaVeda — Go / No-Go Demonstration: Should Tarun Start Using It Personally?

**Date:** 2026-07-18
**Decision under review:** Private-first model (REVENUE_ROADMAP.md 2026-07-17 amendment) — Tarun begins using AlphaVeda on his own capital as a walled operator test account, builds trust, later shows consulting clients.
**Council:** Calibration Integrity, SEBI (Varghese), SRA, Buffett, Munger, Wealth & Revenue Strategist, Constraint Enforcer — real combined dispatch, each backing skill read and applied (COUNCIL_RULES.md Rule A/B satisfied; all seats in the registry).
**Evidence discipline:** Dronacharya Verification Evidence block (SKILL.md §46–68, added today after this very idempotency bug) applied to every verdict. Any point not backed by a real command/output/file read is marked **UNVERIFIED**, not asserted.

---

## Provenance note — what I could and could not verify directly

- **Verifiable by me (repo, git, gh, pytest):** the idempotency fix + its tests, the GHA run history, the SEBI disclaimer reconciliation, the scheduler status, the gap register state, the Wilson math.
- **NOT verifiable by me (no live DB access):** the live ledger figures (44 resolved / 54.5% / −0.00%) and the existence of the 7 suspected duplicate `accuracy_predictions` rows for 2026-07-17. I take the ledger numbers as given (task states they were pulled live moments ago) and compute on them, but I flag every downstream conclusion that rests on an unverifiable input.

---

## 1. Seat Verdicts

### 1.1 Calibration Integrity — `calibration-integrity/SKILL.md`

**The real Wilson 95% interval for 54.5% at n=44 (actual computation, not estimate):**

```
n=44, hits=24, p_hat=24/44=0.5455, z=1.95996
Wilson center = (p + z²/2n) / (1 + z²/n)          = 0.5418
Wilson half   = z·√(p(1−p)/n + z²/4n²) / (1+z²/n)  = 0.1411
Wilson 95% CI = [0.4007, 0.6829]  →  [40.1% , 68.3%]   (width 28.2 pts)
z vs fair coin = (24 − 22)/√(44·0.25) = 0.603 → two-sided p = 0.546
```

Comparison to the prior n=30 reading (from prediction-model-learning-loop-2026-07-16.md):
```
n=30 Wilson 95% CI = [30.2% , 63.9%]  (width 33.6 pts)
```

**Interpretation:** More precise, not yet conclusive. The interval tightened by ~5.4 points and the lower bound climbed from 30% to 40%, but **50% still sits inside [40.1%, 68.3%]**, and the coin-flip test is nowhere near significant (p=0.55). The −0.00% average return is economically zero, consistent with *no measurable edge*, not with a *broken* model. n=44 still has near-zero power to detect a realistic 5–10 point edge (needs ~150–700 obs). The honest read is unchanged from the n=30 finding: **inconclusive, in either direction.**

**Does the duplicate-data bug compromise this number?** Critical distinction from the code: the bug produced 7 **unresolved** duplicate prediction rows, and the duplicate run itself resolved **0 outcomes** (per the fix commit message d80b949). The ledger's 54.5% is computed from **44 resolved** outcomes — which currently exclude the unresolved duplicates. So the number is **not directly corrupted right now**. But it is a **live landmine**: if those 7 duplicate 2026-07-17 predictions later reach horizon and resolve, they would double-count one day's predictions into the ledger — inflating n and skewing the rate. This is exactly the "silent bucket that never reconciles" the seat exists to catch.

```
VERIFICATION EVIDENCE
Claim: Wilson 95% CI for 54.5% at n=44 is [40.1%, 68.3%], still statistically inconclusive.
Happy path tested: python3 Wilson computation, real output:
  "n=44 hits=24 p_hat=0.5455 / Wilson95 lo=0.4007 hi=0.6829 / z vs coin=0.603 / two-sided p=0.546"
  n=30 comparison output: "Wilson lo%=30.2 hi%=63.9 ; width n=44: 28.2 pts, n=30: 33.6 pts"
Failure/adversarial scenario tested: checked whether the duplicate rows enter the resolved count —
  fix commit d80b949 states "the duplicate run resolved 0 outcomes" and the 7 dup rows are UNRESOLVED
  in accuracy_predictions; the 44 figure is resolved-only, so not presently corrupted.
Gap, if any: The 44 / 54.5% / −0.00% inputs themselves are UNVERIFIED — no live DB access to
  confirm. Existence of the 7 duplicate rows is likewise UNVERIFIED (task states "unconfirmed").
```

**Calibration Integrity Verdict: INSUFFICIENT DATA (unchanged from n=30) + LATENT CORRUPTION RISK.** The number is not trustworthy-as-signal yet (wide CI, 50% inside), and the ledger is not *clean* until the suspected duplicates are confirmed-and-removed. Weight in a go/no-go: do not let anyone read "54.5%" as an edge, and do not start the trust-gate clock on a ledger with an unresolved-duplicate landmine in it.

---

### 1.2 SEBI Compliance (Varghese) — `sebi-compliance-reviewer/SKILL.md`

Scope: is the live site compliant **for Tarun's personal use right now**? Personal/private use carries a lower bar than public marketing — that framing is the earlier council's "four Section-4 conditions" (council-expert-user-requirements-2026-07-16.md §4).

**Are the 4 conditions still the right frame, and are they met?**
1. **Labeled operator test account** — MET by posture: use is private, not presented as an independent user. (Discipline condition on Tarun, not a code control.)
2. **Ledger walled off** — public `/accuracy` is resolved solely by the automated `resolve_outcomes_from_ohlcv()` path; no personal P&L merges in. Note the duplicate rows are *model predictions*, not Tarun's realized P&L, so the wall is not breached by the bug. Structurally intact.
3. **Never a testimonial** — not triggered; private use does not surface results externally.
4. **Varghese pass before any external mention** — not yet triggered (nothing external planned). Correctly the right frame for the private→client sequence.

Standard hard gates (the ones that BLOCK): disclaimer presence (Check 1) and non-dismissable (Check 7) — RF-D (4-surface disclaimer disagreement) closed 2026-07-17 with canonical `constants.py` text, `sebi.spec.ts` strengthened, stale Vercel env var deleted; 21/21 Playwright tests pass; the SEBI Playwright gate ran green on the most recent push today.

```
VERIFICATION EVIDENCE
Claim: Live site is SEBI-compliant for Tarun's personal use; the 4-condition frame holds and is met.
Happy path tested: gh run list (real output) — "AlphaVeda Web — SEBI Playwright Gate ... success
  2026-07-18T10:19:04Z" (run 29640643769) on the latest main push.
Failure/adversarial scenario tested: read the exact 4 conditions in
  council-expert-user-requirements-2026-07-16.md §4 lines 80–88, and RF-D closure note in
  GAP_REGISTER.md line 34 (canonical text reconciled across 4 surfaces, oracle strengthened,
  stale Vercel var deleted, 21/21 real Playwright tests). Confirmed the duplicate rows are model
  predictions not personal P&L → condition 2 wall not breached.
Gap, if any: I did not re-run the Playwright suite myself this session; I relied on today's green
  gate run. Condition 1/3 are behavioural (Tarun's discipline), not mechanically enforced.
```

**Varghese Verdict: APPROVE for personal use.** No BLOCK. The 4-condition frame is still correct and currently satisfied. The only compliance tripwire is future — the instant personal results are shown to anyone (even one consulting client as "look how it did for me"), condition 4 fires and a Varghese pass is mandatory first.

---

### 1.3 SRA — `doctrine-panel-systems-reliability-architect/SKILL.md`

Is the infrastructure (scheduler + idempotency fix, both built today) mature enough for trusted daily personal use?

**Failure Mode Inventory (real, from code + run history):**
- **FM-01 — idempotency fix verified only against mocks | P1 | detection: silent | recovery: manual.** The 25/25 tests pass, but the adversarial test (`test_adversarial_duplicate_trigger_is_skipped`) patches Supabase with a **mock** returning a canned OK row. The original bug was precisely that `.eq()` against a **real timestamptz column** silently never matched — a behaviour a mock cannot reproduce. This is the exact SEAM-failure pattern flagged in memory (`project_alphaveda_p0_reliability_pattern.md`: "declared done on isolated tests, never the real path"). G23's own lifecycle says **Retest is blocked on Layer 1.5's ≥2 real-failure-scenario evidence requirement** — mocks do not clear it.
- **FM-02 — scheduler unproven over time | P2 | delayed | manual.** `alphaveda-ingest-trigger` RemoteTrigger proven via exactly **one** manual dispatch (SCHEDULER_STATUS.md: single 2026-07-17 log line, run 29597999081). Zero full autonomous weeks completed.
- **FM-03 — GHA backup trigger unreliable | P2 | delayed.** Real `gh run list`: 2 failures in the recent window (task notes 2026-07-13 and 2026-07-10); G23 documents a 100% late/no-show rate on the native `schedule:` cron — which is exactly why it was demoted to backup.
- **FM-04 — live DB never cleaned | P1 | silent.** 7 suspected duplicate unresolved rows sit in `accuracy_predictions` right now (UNVERIFIED — no DB access). The fix stops *new* duplicates; it did not remediate the existing ones.

```
VERIFICATION EVIDENCE
Claim: The idempotency fix is verified against mocks only, not the real timestamptz path it exists to guard.
Happy path tested: cd alphaveda && python3 -m pytest tests/test_ingest.py -q → "25 passed in 1.31s".
Failure/adversarial scenario tested: read tests/test_ingest.py lines 250–320 — the adversarial test
  uses _make_mock_supabase(existing_ok_row=[...]) and asserts .gte/.lt call args; it never exercises a
  real timestamptz range match. G23 (GAP_REGISTER.md line 23) confirms "Retest — not started, blocked
  on Layer 1.5's ≥2 failure-scenario evidence requirement." Scheduler: SCHEDULER_STATUS.md shows one
  dispatch line only. gh run list shows the SEBI/ingest history including recent failures.
Gap, if any: existence/count of the 7 duplicate rows is UNVERIFIED (no DB access).
```

**Observability:** Yellow — watchdog + failure-issue wiring exist (G11 closed), but no output-validation that a run wrote correct, non-duplicate rows.

**"Proven once, fixed today" is not maturity.** Specific recommendation, not vague:
1. Clean the suspected duplicate rows (with the governance approval the Constraint Enforcer names below).
2. Run **one real, non-mocked** duplicate-trigger verification against live Supabase (fire a second trigger for an already-completed date, confirm `SKIPPED_ALREADY_DONE` and zero new rows) — this is what closes FM-01 / G23 Retest.
3. Then require **7 consecutive clean autonomous scheduler runs** (one full trading week the scheduler has *not yet* completed even once; aligns with G20's existing "7 days clean ingest" bar) before treating the pipeline as trustworthy for unattended daily use.

**SRE Verdict: CONDITIONAL — fix FM-01 and FM-04 first. Confidence in the pipeline as-is: 45/100.** Eyes-on personal use is fine today; *unattended* daily trust is not earned until steps 1–3 complete.

---

### 1.4 Buffett + Munger — `panel-buffett/SKILL.md`, `panel-munger/SKILL.md`

**Buffett (non-stock application — the decision itself):** The asset being compounded here is not Tarun's P&L; it's the **transparent accuracy ledger + the operating discipline** that becomes the eventual pitch (roadmap's own rule; council-expert §4). Dogfooding compounds that asset at minimal capital — a passing Buffett test. But "don't lose money / know what you're doing" cuts against *trusting a number you haven't verified is clean*. 54.5% at n=44 with −0.00% return is **no proven edge yet** — fine for dogfooding (that's how the track record gets built), disqualifying only if ever sold as proof.

**Munger (inversion):** How does "Tarun starts building trust now" fail? Invert it. The single most likely failure path: he begins trusting a ledger that silently contains a duplicate-data defect, the defect later surfaces (7 dup rows resolve and skew the rate), and the *trust he was building is destroyed at the moment it was supposed to pay off* — precisely when he'd show a client. Incentive/psychology check: a solo operator eager to reach the trust gate has every incentive to wave the dirty-ledger question through. That is the bias to resist.

```
VERIFICATION EVIDENCE
Claim: Dogfooding is sound now; trusting the ledger numbers should wait until the ledger is verified clean.
Happy path tested: read council-expert-user-requirements-2026-07-16.md §4 (dogfooding "HIGH VALUE as
  private dogfooding, MISALIGNED the instant it's monetized as proof") and REVENUE_ROADMAP.md 2026-07-17
  amendment (private trust gate = 10 clean ingest days + ≥15 resolved signals + Tarun's subjective confidence).
Failure/adversarial scenario tested: fix commit d80b949 confirms the dup rows exist as a real, unremediated
  live-data defect ("Likely duplicate rows now exist in accuracy_predictions for 2026-07-17"), the exact
  landmine the inversion identifies.
Gap, if any: dup-row existence UNVERIFIED without DB access.
```

**Buffett/Munger Verdict: GO on the activity (use it), CONDITIONAL on the trust.** Start dogfooding now — that *is* the moat-building. Do not start *believing the numbers* (or start the trust-gate clock) until the ledger is confirmed clean and the fix is verified on the real path.

---

### 1.5 Wealth & Revenue Strategist — `doctrine-panel-wealth-revenue-strategist/SKILL.md`

Does a go-ahead now serve the private-first model's actual goal — Tarun trusting it enough to show consulting clients (Stream C)?

**Revenue path map:** [Tarun dogfoods] → [pressure-tests product + accumulates clean ledger + governance story] → [subjective + evidenced trust] → [shows consulting clients] → [Stream C / later Stream D]. Personal use generates **₹0 inside the 21-day window by design** (roadmap explicit) — correct; this is pipeline, not cash, and does not compete with Stream A/C revenue hours much.

**Serve or risk?** A go-ahead **serves** the goal *if and only if* the trust being built is on solid ground. Starting Tarun's personal use is the fastest way to accumulate the exact evidence the private gate measures. The **risk** is starting the *trust-gate clock* on a known-dirty ledger + a fix verified only on mocks: the first thing Tarun could discover is bad data, which corrodes the very trust the whole private-first track exists to manufacture. Leverage type: IP/discipline-building (leveraged), not time-for-money — good for the window.

```
VERIFICATION EVIDENCE
Claim: Go-ahead serves the private-first goal for the activity, but starting the trust-gate clock on a
  dirty ledger risks the goal.
Happy path tested: read REVENUE_ROADMAP.md lines 30–38 — near-term priority is explicitly ingest
  reliability + Wilson-CI/trust items, "matter MORE, not less — they're what the private trust gate is
  actually measured against." Personal use = ₹0 by design (lines 138–144).
Failure/adversarial scenario tested: the trust gate's condition 1 is "zero data-integrity bugs across 10
  consecutive trading days" — an unremediated duplicate-row defect is a live data-integrity bug, so the
  clock cannot honestly be counting yet.
Gap, if any: none beyond the shared dup-row UNVERIFIED flag.
```

**Revenue Strategist Verdict: HIGH VALUE, CONDITIONAL.** Green-light personal dogfooding now (serves the goal, costs no revenue hours). Do **not** let the 10-clean-day trust-gate clock start until the ledger is clean and the fix is real-path verified — starting it dirty risks the one thing this track is built to produce.

---

### 1.6 Constraint Enforcer — `doctrine-panel-constraint-enforcer/SKILL.md`

Specific governance gates for **this** decision (not a general audit):

- **Data Governance Approval Gate — UNMET, and it is the operative blocker.** Cleaning the suspected duplicate rows is a **write to live source data** (`accuracy_predictions`), which the global CLAUDE.md gate and local **Rule D (External State Write Gate)** classify as a replace/delete-class Supabase write: requires GET-current → DIFF → **explicit Tarun approval stated in chat** → narrowest write → VERIFY → log. No such approval is present. The cleanup cannot proceed until Tarun approves it.
- **Layer 1.5 / G23 Retest Gate — UNMET.** GAP_REGISTER.md G23 explicitly states Retest is "blocked on Layer 1.5's ≥2 failure-scenario evidence requirement." The 25/25 mocked tests do not satisfy a *real*-path evidence bar. This gate is unmet against the live timestamptz path.
- **Premortem Gate — n/a for the decision itself** (this report is documentation-only; no architectural trigger file is being written). It *would* apply to any settings/scheduler-config change, not to reading a ledger.
- **Priority-stack alignment — PASS.** Ingest reliability + trust items are explicitly the near-term priority (roadmap 2026-07-17); dogfooding advances the private-first pipeline. No misalignment with the 21-day window (personal use is correctly ₹0/out-of-window).

```
VERIFICATION EVIDENCE
Claim: Two governance gates specific to this decision are unmet — data-governance approval for the
  cleanup write, and G23/Layer-1.5 real-path retest.
Happy path tested: read COUNCIL_RULES.md Rule D (External State Write Gate — Supabase row writes are
  replace-class: GET→DIFF→PRESERVE→VERIFY→log) and global CLAUDE.md Data Governance Approval Gate
  ("Writes to ... GSI source files ... NEVER proceed without explicit Tarun approval").
Failure/adversarial scenario tested: GAP_REGISTER.md line 23 — G23 "Retest — not started, blocked on
  Layer 1.5's ≥2 failure-scenario evidence requirement"; confirmed the mocked pytest suite does not
  clear it. No approval string for a cleanup write exists in this session.
Gap, if any: none.
```

**Constraint Enforcer Verdict: DEFER the "trust it / clean it" step until the two gates clear; PROCEED on eyes-on dogfooding.** The data-governance approval gate is a hard stop on the cleanup write.

---

## 2. Synthesized Recommendation

# CONDITIONAL-GO

**GO now, without condition:** Tarun may begin using AlphaVeda personally today as a clearly-walled operator test account. It is SEBI-compliant for private use (Varghese APPROVE, 4 conditions met, disclaimer gate green today), it is legitimate dogfooding that builds the exact ledger-and-discipline asset the private-first model monetizes (Buffett/Munger, Wealth & Revenue), and it costs no 21-day revenue hours.

**CONDITIONAL for the part that actually matters — *trusting the tool's numbers* and *starting the private trust-gate clock*.** Both must wait until the ledger is verifiably clean and the idempotency fix is proven on the real path, not mocks. Do not read 54.5% as an edge (Wilson [40.1%, 68.3%], 50% inside, p=0.55 vs a coin — inconclusive), and do not let the roadmap's 10-clean-day counter start on a ledger carrying an unresolved-duplicate landmine.

Split verdict rationale: every seat agreed the *activity* is safe and useful; the disagreement was entirely about whether the *numbers and the pipeline* are trustworthy yet — and they are not.

---

## 3. Exactly What Closes the Gap

Three items, in order. The decision upgrades from CONDITIONAL-GO to full GO (numbers trusted, trust-clock started) when all three are done:

1. **Confirm-and-clean the duplicate `accuracy_predictions` rows for 2026-07-17.**
   Owner: Tarun approval → Claude/Codex executes. Blocked by the **Data Governance Approval Gate** — needs Tarun's explicit "approved" in chat first. Procedure per Rule D: GET current 2026-07-17 rows (this also *verifies* the currently-UNVERIFIED claim that 7 duplicates exist), DIFF, delete only the duplicate set, VERIFY, log to `external-state-writes.log`. **This is the P0 — a live-data-integrity gate the roadmap's own condition 1 depends on.**

2. **Verify the idempotency fix against the real Supabase timestamptz path, not mocks.**
   Owner: Claude/Codex. Fire a real second trigger for an already-completed date against live Supabase; confirm `status: SKIPPED_ALREADY_DONE` and zero new rows written. Closes **FM-01** and satisfies **G23 Retest / Layer 1.5's ≥2-real-scenario bar** (mocked 25/25 does not).

3. **Run 7 consecutive clean autonomous scheduler runs.**
   Owner: the `alphaveda-ingest-trigger` routine, observed. One full trading week the scheduler has not yet completed even once. Only then is unattended daily reliance earned; this also naturally advances the roadmap's 10-clean-day trust gate.

Until items 1–2 are done, personal use should be **eyes-on** (Tarun watches each run), not unattended. Item 3 lifts the eyes-on requirement.

---

*Method note: all seven backing skills read and applied; verdicts carry the Dronacharya Verification Evidence block with real command output / file reads. The two load-bearing UNVERIFIED inputs — the live ledger figures and the existence of the 7 duplicate rows — are flagged wherever a conclusion rests on them, and closing-gap item 1 is written to verify the second one as its first step.*
