# Expert: Dr. Kavya Menon — Behavioral Finance

**Domain:** Behavioral finance
**Seat label:** Reflexivity & Streak Skepticism

## Top concern about AlphaVeda
Guard 2 (Soros) and the `accuracy_streak_flag` / `STREAK_DISCOUNT_FACTOR = 0.7` mechanism are meant to enforce counter-cyclical skepticism — accuracy streaks should *reduce* confidence, not amplify it. But the implementation only discounts at the *weight-proposal / ledger-aggregation* stage (Section 3 ledger query: `actual_return * (CASE WHEN accuracy_streak_flag THEN 0.7 ELSE 1.0 END)`). It does **not** discount the live `confidence` emitted on a streaking instrument. So at a cycle peak — exactly when reflexivity is most dangerous — the engine keeps emitting high confidence and Kelly keeps sizing up, while the discount only quietly shows up months later in a quarterly weight proposal. The streak flag punishes the historical record but not the current bet. This inverts the intended Soros guard.

## Evaluation lenses
1. Goodhart resistance — once `hit_rate` drives weight proposals, does optimising the metric (frequent easy calls) degrade the underlying objective (return capture)?
2. Reflexivity timing — does the skepticism mechanism act *before* the dangerous bet (live confidence) or only *after* (retrospective ledger discount)?
3. Streak symmetry — does `compute_streak_flag` only flag winning streaks (overconfidence), or also losing streaks (capitulation), which is the other behavioral failure mode?

## Key questions for R3 council
- `STREAK_DISCOUNT_FACTOR = 0.7` is applied in the ledger aggregation (Section 3) but nowhere in the live emit flow (Section 5, steps 1–7). Should a streaking instrument's *emitted confidence* be discounted before Kelly sizes it, not just its backward-looking record?
- `compute_streak_flag` (Section 3) returns True only when "last STREAK_WINDOW predictions were all correct." Where is the mirror guard for 5 consecutive *wrong* calls (model breakdown / capitulation)?
- Guard 6 (Munger) cites "lollapalooza at cycle peak" — but the quarterly review gate runs every ~90 days. A peak can form and break inside one quarter. Is quarterly cadence fast enough to catch the very lollapalooza it names?

## Red flags in current design
1. **Section 3 ledger query vs Section 5 emit flow**: `STREAK_DISCOUNT_FACTOR=0.7` discounts only the aggregated `streak_adj_return`, never the live `confidence` fed to Kelly — the counter-cyclical guard fires too late to prevent the peak bet.
2. **Section 3 `compute_streak_flag`**: asymmetric — flags only winning streaks; no detection of consecutive losses, leaving capitulation/over-discounting unguarded.
3. **Guard 6 + Section 5**: `hit_rate` (Section 3 ledger) is the proposal trigger, which is precisely the Goodhart-able metric Munger's guard warns about — the model can raise hit rate by making safe, low-magnitude calls, gaming the ledger while `avg_peak_return` stagnates.
