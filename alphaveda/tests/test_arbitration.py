"""Phase 3 — arbitration.py tests."""
import pytest
from src.signals.arbitration import arbitrate, ARBITRATION_MARGIN


def _make_signal(direction, confidence, signal_name, weight):
    return {"direction": direction, "confidence": confidence,
            "signal_name": signal_name, "weight": weight}


def test_arbitration_suppression_when_within_margin():
    """If weighted scores are within ARBITRATION_MARGIN, suppress emission."""
    signals = [
        _make_signal("BULL", 70, "roic", 0.5),
        _make_signal("BEAR", 70, "momentum_rsi", 0.5),
    ]
    result = arbitrate(signals)
    assert result is None  # suppressed


def test_arbitration_bull_wins():
    signals = [
        _make_signal("BULL", 80, "roic", 0.6),
        _make_signal("BEAR", 40, "momentum_rsi", 0.4),
    ]
    result = arbitrate(signals)
    assert result is not None
    assert result["direction"] == "BULL"


def test_arbitration_bear_wins():
    signals = [
        _make_signal("BEAR", 90, "momentum_rsi", 0.7),
        _make_signal("BULL", 30, "roic", 0.3),
    ]
    result = arbitrate(signals)
    assert result is not None
    assert result["direction"] == "BEAR"


def test_arbitration_confidence_is_normalised():
    """Emitted confidence is in [0, 100]."""
    signals = [
        _make_signal("BULL", 95, "roic", 0.8),
        _make_signal("BEAR", 20, "momentum_rsi", 0.2),
    ]
    result = arbitrate(signals)
    assert result is not None
    assert 0 <= result["confidence"] <= 100


def test_arbitration_all_bull_emits():
    """All signals agree — must emit."""
    signals = [
        _make_signal("BULL", 80, "roic", 0.5),
        _make_signal("BULL", 70, "fcf", 0.5),
    ]
    result = arbitrate(signals)
    assert result is not None
    assert result["direction"] == "BULL"


def test_arbitration_empty_signals():
    """No signals — must suppress."""
    result = arbitrate([])
    assert result is None


def test_arbitration_malformed_signal_raises():
    """C3: Signal dict missing required keys raises ValueError before scoring."""
    malformed = [{"direction": "BULL", "confidence": 80.0}]  # missing 'weight'
    with pytest.raises(ValueError, match="missing required keys"):
        arbitrate(malformed)
