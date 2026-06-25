"""Portfolio Kelly sizing and exit rules.

Kelly formula (Druckenmiller):
  b = magnitude_target / downside_target  (odds ratio: upside per unit risked)
  f* = p - (1-p) / b                      (full Kelly fraction)
  position = f* × QUARTER_KELLY_FRACTION × portfolio_value

Returns 0 when: downside_target is None/zero, or full Kelly is non-positive (no edge).
Cap at MAX_POSITION_PCT × portfolio_value — hard concentration limit.
MIN_POSITION_PCT is NOT a floor — zero-edge positions must return 0, not the floor.

Exit rules (Druckenmiller E1–E4):
  E1: current position has drifted outside the Kelly band (±50% of kelly target by default)
  E2: N consecutive BEAR emits (bucket-aware threshold) each with confidence >= E2_CONFIDENCE_FLOOR
  E2-UNCERTAINTY: double threshold + moving-average condition
  E3: magnitude_target has fallen below 3%
  E4: sector holding weight exceeds SECTOR_CAP_PCT
"""
from __future__ import annotations
from constants import (
    MAX_POSITION_PCT,
    QUARTER_KELLY_FRACTION,
    SECTOR_CAP_PCT,
    E2_CONSECUTIVE_THRESHOLD,
    E2_CONFIDENCE_FLOOR,
)

_E1_BAND_TOLERANCE = 0.50   # 50% drift from Kelly target triggers E1
_E3_MAGNITUDE_FLOOR = 0.03  # 3% upside target minimum
_E2_UNCERTAINTY_MULTIPLIER = 2  # UNCERTAINTY path uses 2× the standard threshold


def kelly_position_size(
    p: float,
    magnitude_target: float,
    downside_target: float | None,
    portfolio_value: float,
) -> float:
    """Compute quarter-Kelly rupee position size.

    Returns 0 on no-edge (Kelly ≤ 0), zero/None downside, or if portfolio_value ≤ 0.
    Never returns a value below 0 or above MAX_POSITION_PCT × portfolio_value.
    """
    if not downside_target or portfolio_value <= 0:
        return 0

    b = magnitude_target / downside_target
    q = 1.0 - p
    full_kelly = p - q / b

    if full_kelly <= 0:
        return 0

    raw = full_kelly * QUARTER_KELLY_FRACTION * portfolio_value
    return min(raw, MAX_POSITION_PCT * portfolio_value)


def should_exit_e1(
    current_position_pct: float,
    kelly_target_pct: float,
    tolerance: float = _E1_BAND_TOLERANCE,
) -> bool:
    """E1: position drifted outside Kelly band.

    Triggers when |current - kelly_target| > tolerance × kelly_target.
    """
    if kelly_target_pct <= 0:
        return current_position_pct > 0  # any position on zero-edge should exit
    drift = abs(current_position_pct - kelly_target_pct)
    return drift > tolerance * kelly_target_pct


def should_exit_e2(
    consecutive_bear_count: int,
    bucket_type: str,
    latest_confidence: float,
    uncertainty_path: bool = False,
) -> bool:
    """E2: consecutive BEAR emits exceed bucket-specific threshold.

    Only counts emits with confidence >= E2_CONFIDENCE_FLOOR.
    uncertainty_path doubles the threshold and requires the MA condition (caller signals via flag).
    """
    if latest_confidence < E2_CONFIDENCE_FLOOR:
        return False
    threshold = E2_CONSECUTIVE_THRESHOLD[bucket_type]
    if uncertainty_path:
        threshold = threshold * _E2_UNCERTAINTY_MULTIPLIER
    return consecutive_bear_count >= threshold


def should_exit_e3(magnitude_target: float) -> bool:
    """E3: upside target has degraded below the minimum useful threshold."""
    return magnitude_target < _E3_MAGNITUDE_FLOOR


def should_exit_e4(
    sector_weight: float,
    cap: float = SECTOR_CAP_PCT,
) -> bool:
    """E4: sector weight exceeds concentration cap."""
    return sector_weight > cap
