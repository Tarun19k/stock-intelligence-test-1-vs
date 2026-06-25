"""Phase 3 — engine.py tests.
Tests cover: calibrate_confidence (pure), emit_pipeline (pure, ordering),
             and emit_signal (DB-dependent, mocked).
"""
import pytest
from unittest.mock import MagicMock, patch
from constants import STREAK_WINDOW, STREAK_DISCOUNT_FACTOR, OBSERVATION_THRESHOLD
from src.signals.engine import calibrate_confidence, emit_pipeline


# ─────────────────────────────────────────────────────────────────────────────
# calibrate_confidence — Reddy condition (COUNCIL_TEST_MAP Phase 3)
# ─────────────────────────────────────────────────────────────────────────────

def test_cold_start_calibration_p_eq_min():
    """Cold-start: p = min(confidence/100, hit_rate). Reddy council condition."""
    p = calibrate_confidence(confidence=75, segment_obs=15, hit_rate=0.60)
    assert p == min(75 / 100, 0.60)


def test_cold_start_p_leq_confidence_over_100():
    """Calibrated p must never exceed confidence/100 in cold-start."""
    p = calibrate_confidence(confidence=90, segment_obs=5, hit_rate=0.99)
    assert p <= 90 / 100


def test_warm_path_uses_hit_rate():
    """Warm path (>= OBSERVATION_THRESHOLD): p = hit_rate (capped at confidence/100)."""
    p = calibrate_confidence(confidence=80, segment_obs=OBSERVATION_THRESHOLD, hit_rate=0.55)
    assert p == min(80 / 100, 0.55)


def test_calibration_result_in_unit_interval():
    """Calibrated p must always be in [0.0, 1.0]."""
    for confidence, obs, hit in [(0, 0, 0.0), (100, 50, 1.0), (60, 10, 0.45)]:
        p = calibrate_confidence(confidence=confidence, segment_obs=obs, hit_rate=hit)
        assert 0.0 <= p <= 1.0


# ─────────────────────────────────────────────────────────────────────────────
# emit_pipeline — Soros pipeline contract (discount BEFORE calibration)
# ─────────────────────────────────────────────────────────────────────────────

_BULL_SIGNALS = [
    {"direction": "BULL", "confidence": 80, "signal_name": "roic", "weight": 0.6},
    {"direction": "BEAR", "confidence": 20, "signal_name": "momentum_rsi", "weight": 0.4},
]

_SUPPRESSED_SIGNALS = [
    {"direction": "BULL", "confidence": 70, "signal_name": "roic", "weight": 0.5},
    {"direction": "BEAR", "confidence": 70, "signal_name": "momentum_rsi", "weight": 0.5},
]


def test_emit_pipeline_returns_none_on_suppression():
    """Suppressed arbitration → None from emit_pipeline."""
    result = emit_pipeline(
        signals=_SUPPRESSED_SIGNALS,
        streak_count=0,
        segment_obs=0,
        hit_rate=0.5,
    )
    assert result is None


def test_streak_discount_applied_when_flag_set():
    """Pipeline contract: streak discount applied to confidence; result confidence < raw."""
    raw = emit_pipeline(
        signals=_BULL_SIGNALS,
        streak_count=0,
        segment_obs=0,
        hit_rate=0.5,
    )
    discounted = emit_pipeline(
        signals=_BULL_SIGNALS,
        streak_count=STREAK_WINDOW,
        segment_obs=0,
        hit_rate=0.5,
    )
    assert raw is not None and discounted is not None
    assert discounted["pre_calibration_confidence"] < raw["pre_calibration_confidence"]
    assert discounted["streak_discounted"] is True


def test_no_discount_below_streak_window():
    """streak_count < STREAK_WINDOW → no discount applied."""
    result = emit_pipeline(
        signals=_BULL_SIGNALS,
        streak_count=STREAK_WINDOW - 1,
        segment_obs=0,
        hit_rate=0.5,
    )
    assert result is not None
    assert result["streak_discounted"] is False


def test_pipeline_discount_fires_before_calibration():
    """Soros pipeline contract: calibrated_p uses POST-discount confidence, not pre-discount."""
    # With streak: pre_cal_confidence = raw * STREAK_DISCOUNT_FACTOR
    # calibrated_p = min(pre_cal_confidence / 100, hit_rate)
    raw_confidence = 80 * 0.6  # BULL score from _BULL_SIGNALS
    discounted = raw_confidence * STREAK_DISCOUNT_FACTOR
    expected_p = min(discounted / 100, 0.50)

    result = emit_pipeline(
        signals=_BULL_SIGNALS,
        streak_count=STREAK_WINDOW,
        segment_obs=0,
        hit_rate=0.50,
    )
    assert result is not None
    assert result["calibrated_p"] == pytest.approx(expected_p, abs=1e-6)


def test_emit_pipeline_direction_correct():
    result = emit_pipeline(
        signals=_BULL_SIGNALS,
        streak_count=0,
        segment_obs=0,
        hit_rate=0.5,
    )
    assert result is not None
    assert result["direction"] == "BULL"
