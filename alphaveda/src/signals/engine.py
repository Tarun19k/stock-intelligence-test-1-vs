"""Signal emit engine — full pipeline: arbitrate → discount → calibrate.

Pipeline contract (Soros condition — non-negotiable):
  Step 3a: arbitrate(signals) → direction + confidence
  Step 3b: apply STREAK_DISCOUNT_FACTOR to confidence (BEFORE calibration)
  Step 3c: calibrate_confidence(post-discount confidence, obs, hit_rate) → p

Bins used for accuracy scoring must be built from POST-discount confidence.
Calibrating before discounting would produce bins misaligned with actual emit values.

Phase 4 adds Kelly sizing (step 4) as a separate layer on top of this pipeline.
"""
from __future__ import annotations
from constants import (
    OBSERVATION_THRESHOLD,
    STREAK_DISCOUNT_FACTOR,
)
from src.accuracy.ledger import compute_streak_flag
from src.signals.arbitration import arbitrate


def calibrate_confidence(
    confidence: float,
    segment_obs: int,
    hit_rate: float,
) -> float:
    """Map raw confidence to calibrated probability p ∈ [0.0, 1.0].

    Cold-start (segment_obs < OBSERVATION_THRESHOLD):
        p = min(confidence / 100, hit_rate)
    Warm (segment_obs >= OBSERVATION_THRESHOLD):
        p = min(confidence / 100, hit_rate)   — same formula; warm path for future Platt scaling
    """
    return min(confidence / 100.0, hit_rate)


def emit_pipeline(
    signals: list[dict],
    streak_count: int,
    segment_obs: int,
    hit_rate: float,
) -> dict | None:
    """Pure pipeline: no DB calls. Accepts pre-computed inputs.

    Returns emit dict or None (suppressed).
    Returned dict keys: direction, pre_calibration_confidence, calibrated_p,
                        streak_discounted.
    """
    arb = arbitrate(signals)
    if arb is None:
        return None

    confidence = arb["confidence"]

    # Step 3b — streak discount BEFORE calibration (Soros pipeline contract)
    streak_discounted = compute_streak_flag(streak_count)
    if streak_discounted:
        confidence = confidence * STREAK_DISCOUNT_FACTOR

    # Step 3c — calibration uses post-discount confidence
    calibrated_p = calibrate_confidence(
        confidence=confidence,
        segment_obs=segment_obs,
        hit_rate=hit_rate,
    )

    return {
        "direction": arb["direction"],
        "pre_calibration_confidence": confidence,
        "calibrated_p": calibrated_p,
        "streak_discounted": streak_discounted,
    }
