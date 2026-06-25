"""Signal arbitration — resolves conflicting bull/bear signals into a single emit decision.

Algorithm (Reddy condition, GAP-003 fix):
  1. Compute weighted confidence score for each direction.
  2. If |bull_score - bear_score| < ARBITRATION_MARGIN → suppress (return None).
  3. Otherwise emit the winning direction with confidence = winning_score.

The ARBITRATION_MARGIN creates a dead zone that prevents weak-majority signals
from generating noisy emits. A 15-point margin means the system needs a clear
directional signal before committing.
"""
from __future__ import annotations
from constants import ARBITRATION_MARGIN


def arbitrate(signals: list[dict]) -> dict | None:
    """Resolve signals into a single directional emit, or None if suppressed.

    Each signal dict: {"direction": "BULL"|"BEAR", "confidence": float,
                       "signal_name": str, "weight": float}
    Returns: {"direction": str, "confidence": float} or None.
    """
    if not signals:
        return None

    bull_score = sum(
        s["confidence"] * s["weight"] for s in signals if s["direction"] == "BULL"
    )
    bear_score = sum(
        s["confidence"] * s["weight"] for s in signals if s["direction"] == "BEAR"
    )

    if abs(bull_score - bear_score) < ARBITRATION_MARGIN:
        return None

    if bull_score > bear_score:
        return {"direction": "BULL", "confidence": min(100.0, bull_score)}
    return {"direction": "BEAR", "confidence": min(100.0, bear_score)}
