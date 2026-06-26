"""Score open predictions against actual OHLCV outcomes.

Jhunjhunwala condition (hard gate): circuit_flag=True rows are EXCLUDED from
outcome scoring. A circuit-locked price is not a true market-clearing price and
must never be used to mark a prediction WIN or LOSS. This exclusion is enforced
here at the resolution layer, not upstream in the data loader.
"""
from __future__ import annotations


def resolve_outcomes_from_ohlcv(
    predictions: list[dict],
    ohlcv_rows: list[dict],
) -> list[dict]:
    """Score predictions against actual closing prices, excluding circuit rows.

    Args:
        predictions: list of open prediction dicts with keys:
            id, symbol, direction ('BULLISH'|'BEARISH'), entry_price
        ohlcv_rows: list of OHLCV dicts with keys:
            symbol, close, circuit_flag (bool, defaults False)

    Returns:
        list of resolution dicts: prediction_id, outcome ('WIN'|'LOSS'),
        actual_close, pct_change.
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
        direction = pred.get("direction", "BULLISH")

        if direction == "BULLISH":
            outcome = "WIN" if pct_change > 0 else "LOSS"
        else:
            outcome = "WIN" if pct_change < 0 else "LOSS"

        resolutions.append({
            "prediction_id": pred["id"],
            "outcome": outcome,
            "actual_close": actual_close,
            "pct_change": pct_change,
        })

    return resolutions
