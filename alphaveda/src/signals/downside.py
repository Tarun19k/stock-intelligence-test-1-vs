"""Downside target computation.

Priority order (GAP-001 fix — Druckenmiller condition):
  1. Signal-provided stop-loss (explicit, e.g. from fundamental analysis)
  2. ATR(14)/price default — derived from recent price action

Result is always clamped to [DOWNSIDE_FLOOR, DOWNSIDE_CAP].
Fallback (DOWNSIDE_FALLBACK) applies when OHLCV history is insufficient.
"""
from __future__ import annotations
from constants import ATR_PERIOD, ATR_MULTIPLIER

DOWNSIDE_FLOOR    = 0.01   # 1%  — minimum stop-loss to avoid noise stops
DOWNSIDE_CAP      = 0.30   # 30% — maximum stop-loss (position sizing breaks above this)
DOWNSIDE_FALLBACK = 0.05   # 5%  — used when insufficient OHLCV rows for ATR


def compute_downside_target(
    instrument_id: int,
    signal_stop_loss_pct: float | None,
    ohlcv_rows: list[dict],
) -> float:
    """Return downside target in [DOWNSIDE_FLOOR, DOWNSIDE_CAP].

    ohlcv_rows: list of dicts with 'high', 'low', 'close' keys, chronological order.
    """
    if signal_stop_loss_pct is not None:
        return _clamp(signal_stop_loss_pct)

    if len(ohlcv_rows) < 2:
        return DOWNSIDE_FALLBACK

    true_ranges = [
        max(
            ohlcv_rows[i]["high"] - ohlcv_rows[i]["low"],
            abs(ohlcv_rows[i]["high"] - ohlcv_rows[i - 1]["close"]),
            abs(ohlcv_rows[i]["low"]  - ohlcv_rows[i - 1]["close"]),
        )
        for i in range(1, len(ohlcv_rows))
    ]

    period = min(ATR_PERIOD, len(true_ranges))
    atr = sum(true_ranges[-period:]) / period

    last_close = ohlcv_rows[-1]["close"]
    if last_close == 0:
        return DOWNSIDE_FALLBACK

    return _clamp(atr * ATR_MULTIPLIER / last_close)


def _clamp(value: float) -> float:
    return max(DOWNSIDE_FLOOR, min(DOWNSIDE_CAP, value))
