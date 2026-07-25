"""Score open predictions against actual OHLCV outcomes.

Jhunjhunwala condition (hard gate): circuit_flag=True rows are EXCLUDED from
outcome scoring. A circuit-locked price is not a true market-clearing price and
must never be used to mark a prediction WIN or LOSS. This exclusion is enforced
here at the resolution layer, not upstream in the data loader.

RF-J / L1-D (2026-07-26, 4-seat council: Lynch, Calibration Integrity,
UX/Accessibility, SEBI compliance/Varghese): the `hit` field is DIRECTION-ONLY
and stays that way — it likely already feeds downstream accuracy%/streak
calculations, and silently redefining it would corrupt historical
interpretation. `magnitude_hit` is added ADDITIVELY: it asks the stricter
question a retail reader actually cares about — "did the stated target get
reached", not just "was the direction right".
"""
from __future__ import annotations

# How much slack the magnitude check allows below the stated target before
# counting it as a miss. 0.10 = actual move must reach at least 90% of the
# stated magnitude/downside target to count as a magnitude hit.
MAGNITUDE_TOLERANCE = 0.10


def resolve_outcomes_from_ohlcv(
    predictions: list[dict],
    ohlcv_rows: list[dict],
) -> list[dict]:
    """Score predictions against actual closing prices, excluding circuit rows.

    Args:
        predictions: list of open prediction dicts with keys:
            id, symbol, signal_direction ('BULL'|'BEAR'), entry_price,
            magnitude_target (optional, positive fraction, BULL target),
            downside_target (optional, positive fraction, BEAR target)
        ohlcv_rows: list of OHLCV dicts with keys:
            symbol, close, circuit_flag (bool, defaults False)

    Returns:
        list of resolution dicts: prediction_id, hit (bool, DIRECTION-ONLY —
        unchanged meaning, do not reinterpret), return_pct, actual_direction
        ('BULL'|'BEAR', the observed outcome direction — distinct from the
        predicted direction), magnitude_hit (bool — direction_hit AND the
        actual move reached at least magnitude_target/downside_target * (1 -
        MAGNITUDE_TOLERANCE); if no target was set on the prediction, magnitude
        cannot be evaluated and defaults to matching the direction-only hit so
        older/target-less predictions are not penalised for data they never
        had), outcome ('WIN'|'PARTIAL'|'LOSS' — three-state: WIN = direction
        and magnitude both hit, PARTIAL = direction hit but magnitude missed,
        LOSS = direction missed).
        Predictions whose symbol has no non-circuit close are silently omitted.
    """
    # Build symbol → last non-circuit close. circuit_flag=True rows are skipped.
    symbol_close: dict[str, float] = {}
    for row in ohlcv_rows:
        if row.get("circuit_flag", False):
            continue
        symbol_close[row["symbol"]] = row["close"]

    resolutions: list[dict] = []
    for pred in predictions:
        symbol = pred.get("symbol", "")
        entry_price = pred.get("entry_price", 0)

        if symbol not in symbol_close:
            continue
        if entry_price == 0:
            continue

        actual_close = symbol_close[symbol]
        pct_change = (actual_close - entry_price) / entry_price
        direction = pred.get("signal_direction", "BULL")
        actual_direction = "BULL" if pct_change > 0 else "BEAR"

        hit = (direction == "BULL" and pct_change > 0) or (direction == "BEAR" and pct_change < 0)

        if not hit:
            magnitude_hit = False
        elif direction == "BULL":
            magnitude_target = pred.get("magnitude_target")
            magnitude_hit = (
                magnitude_target is None
                or pct_change >= magnitude_target * (1 - MAGNITUDE_TOLERANCE)
            )
        else:  # BEAR
            downside_target = pred.get("downside_target")
            magnitude_hit = (
                downside_target is None
                or pct_change <= -downside_target * (1 - MAGNITUDE_TOLERANCE)
            )

        if hit and magnitude_hit:
            outcome = "WIN"
        elif hit:
            outcome = "PARTIAL"
        else:
            outcome = "LOSS"

        resolutions.append({
            "prediction_id": pred["id"],
            "hit": hit,
            "return_pct": pct_change,
            "actual_direction": actual_direction,
            "magnitude_hit": magnitude_hit,
            "outcome": outcome,
        })

    return resolutions
