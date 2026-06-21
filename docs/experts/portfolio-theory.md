# Expert: Prof. Sanjay Iyer — Portfolio Theory & Position Sizing

**Domain:** Portfolio theory / Kelly criterion / position sizing
**Seat label:** Kelly Sizing & Allocation Caps

## Top concern about AlphaVeda
The `kelly_position_size` implementation (Section 6) computes full Kelly as `(p - q/b)` with `b = magnitude_target` floored at 0.05, then takes a flat Quarter-Kelly (`* 0.25`) and clamps to `[MIN_POSITION_PCT, MAX_POSITION_PCT]`. Two defects compound. First, the formula `(p - q/b)` is the *fractional Kelly for a binary bet*, but `b` is being fed `magnitude_target` (an expected-return fraction, e.g. 0.06), which is not the same as the payoff odds Kelly requires — odds `b` should be win-size/loss-size, and the loss size is never modelled, so `q/b` is dimensionally wrong. Second, the clamp `max(MIN, min(MAX, raw))` floors *every* position at 1% (₹7,250) — including positions where Kelly correctly returns ≤0 (a bet you should not take). A negative-edge signal still gets a ₹7,250 allocation.

## Evaluation lenses
1. Kelly correctness — are `p`, `q`, and `b` dimensionally consistent (win-prob, loss-prob, win/loss odds), or is `magnitude_target` being misused as odds?
2. Floor semantics — does `MIN_POSITION_PCT` force capital into negative-edge or zero-edge bets the Kelly math says to skip?
3. Portfolio-level constraint stacking — do `MAX_POSITION_PCT` (10%), `SECTOR_CAP_PCT` (35%), and `CASH_FLOOR_PCT` (10%) compose into a feasible allocation, or can they contradict?

## Key questions for R3 council
- In `(p - q/b)`, what is the loss magnitude? `b` is set to `magnitude_target` (expected upside) — where is the downside that the Kelly odds ratio requires?
- When `quarter_kelly = max(0, full_kelly * 0.25)` is 0 (no edge), the function still returns `MIN_POSITION_PCT * portfolio_value` = ₹7,250 due to the final clamp. Is forcing a 1% position on a zero-edge signal intended?
- The four buckets in `0005_portfolio_buckets.sql` seed `max_position_pct` and `sector_cap_pct` per bucket, but Section 6 hardcodes `MAX_POSITION_PCT = 0.10` in `optimizer.py` — which source wins, the DB row or the constant?

## Red flags in current design
1. **Section 6 `kelly_position_size`**: `b = magnitude_target` conflates expected return with payoff odds; the loss leg of the bet is unmodelled, making `q/b` and therefore the whole Kelly fraction unsound.
2. **Section 6 final clamp**: `max(MIN_POSITION_PCT * portfolio_value, ...)` overrides the `max(0, ...)` zero-edge guard, forcing ₹7,250 into bets Kelly says to skip.
3. **Section 1 vs Section 6**: bucket-level caps in `portfolio_buckets` (DB) duplicate module-level constants in `optimizer.py`; the design never states precedence, risking a 10% constant silently overriding a stricter per-bucket DB cap.
