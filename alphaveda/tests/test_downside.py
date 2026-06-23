"""Phase 3 — downside.py tests. Skipped until src/signals/downside.py is implemented."""
import pytest
pytest.importorskip("src.signals.downside", reason="Phase 3 — src/signals/downside.py not yet implemented")
from src.signals.downside import compute_downside_target
from constants import ATR_PERIOD


def test_downside_signal_override():
    """If signal provides stop_loss_pct, use it directly."""
    result = compute_downside_target(
        instrument_id=1,
        signal_stop_loss_pct=0.08,
        ohlcv_rows=[],
    )
    assert result == pytest.approx(0.08)


def test_downside_signal_override_clamps_to_floor():
    result = compute_downside_target(1, signal_stop_loss_pct=0.001, ohlcv_rows=[])
    assert result == pytest.approx(0.01)  # floor = 0.01


def test_downside_signal_override_clamps_to_cap():
    result = compute_downside_target(1, signal_stop_loss_pct=0.50, ohlcv_rows=[])
    assert result == pytest.approx(0.30)  # cap = 0.30


def test_downside_atr_default(sample_ohlcv_rows):
    """ATR(14)/price default when no signal stop-loss is provided."""
    result = compute_downside_target(1, None, sample_ohlcv_rows)
    assert 0.01 <= result <= 0.30


def test_downside_atr_floor(empty_ohlcv_rows):
    """Insufficient history: fallback to 5%."""
    result = compute_downside_target(1, None, empty_ohlcv_rows)
    assert result == pytest.approx(0.05)


def test_downside_never_zero(sample_ohlcv_rows):
    result = compute_downside_target(1, None, sample_ohlcv_rows)
    assert result > 0


def test_downside_single_row_fallback():
    """Only 1 row — cannot compute true range — fallback to 5%."""
    rows = [{"high": 1010, "low": 990, "close": 1000}]
    result = compute_downside_target(1, None, rows)
    assert result == pytest.approx(0.05)
