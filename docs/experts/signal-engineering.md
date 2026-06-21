# Expert: Dr. Anika Reddy — ML & Signal Engineering

**Domain:** ML / signal engineering
**Seat label:** Signal Scoring & Arbitration

## Top concern about AlphaVeda
The `confidence` field (0–100 SMALLINT, `accuracy_predictions`, migration 0007) is used in two incompatible ways. It is an *input* to Kelly sizing as a probability `p = confidence / 100` (Section 6, `kelly_position_size`), and it is also the thing the 24-segment ledger is supposed to *calibrate* against `is_correct`. But the signal emit flow (Section 5) never describes how the composite 0–100 score is actually computed from the weighted signals — it jumps from "Enforce `FUNDAMENTAL_WEIGHT_FLOOR`" straight to "Emit signal with all context fields." A confidence number fed directly into Kelly as a win-probability, with no documented calibration map from weighted-signal-score to probability, will produce systematically wrong position sizes. An 85/100 confidence is treated as p=0.85 in the Kelly formula whether or not the segment ledger shows 85% historical hit rate.

## Evaluation lenses
1. Calibration — is `confidence` a calibrated probability (Kelly demands this) or an uncalibrated composite score being misused as one?
2. Prior soundness — do `COLD_START_WEIGHTS` (Section 5) function as genuine Bayesian priors that the ledger updates, or are they fixed until a hard 30-observation cutover with no smooth blending?
3. Arbitration determinism — when TA signals conflict (`src/signals/arbitration.py`), is the resolution rule specified, or left as an undefined "conflict resolution" stub?

## Key questions for R3 council
- What is the exact function mapping weighted signal scores to the 0–100 `confidence`, and is it calibrated so that confidence=70 historically means ~70% `is_correct`?
- `COLD_START_WEIGHTS` are described as "Bayesian priors" but Section 7 says they are "replaced segment-by-segment" at 30 observations — that is a hard cutover, not Bayesian updating. Is there any blending between prior and observed, or a discontinuity at observation 30?
- How does `src/signals/arbitration.py` resolve a bull/bear conflict — does it suppress emission, average, or pick the higher-weighted signal? Section 1 names it but Sections 5–7 never define it.

## Red flags in current design
1. **Section 6 `kelly_position_size`**: uses `p = confidence / 100` as a calibrated win-probability with zero calibration layer documented — guaranteed sizing error if confidence is an uncalibrated composite.
2. **Section 5 + Section 7**: `OBSERVATION_THRESHOLD = 30` triggers a hard swap from `COLD_START_WEIGHTS` to learned weights with no shrinkage/blending — a discontinuity that will jolt sizing and confidence the day a segment crosses 30.
3. **Section 1 `src/signals/arbitration.py`**: signal arbitration is listed as a module and a core capability ("Signal arbitration: when TA signals conflict") but is undefined in every detailed section — no rule, no constant, no test in the Section 9 matrix.
