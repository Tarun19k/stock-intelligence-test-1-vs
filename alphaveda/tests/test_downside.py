"""Phase 3 — downside.py tests."""
import pytest
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


# ── Circuit flag tests (Jhunjhunwala Phase 4 condition) ──────────────────────

def test_downside_all_circuit_rows_returns_fallback():
    """All rows circuit-locked → fewer than 2 clean rows → DOWNSIDE_FALLBACK."""
    rows = [
        {"high": 110, "low": 109, "close": 110, "circuit_flag": True},
        {"high": 110, "low": 109, "close": 110, "circuit_flag": True},
        {"high": 110, "low": 109, "close": 110, "circuit_flag": True},
    ]
    result = compute_downside_target(1, None, rows)
    assert result == pytest.approx(0.05)


def test_downside_circuit_rows_excluded_from_atr():
    """Circuit rows excluded — result equals clean-only result (contamination removed)."""
    clean_rows = [
        {"high": 110, "low": 100, "close": 105, "circuit_flag": False},
        {"high": 115, "low": 108, "close": 112, "circuit_flag": False},
    ]
    mixed_rows = [
        {"high": 110, "low": 100, "close": 105, "circuit_flag": False},
        {"high": 110.1, "low": 110.0, "close": 110.0, "circuit_flag": True},  # compressed TR
        {"high": 115, "low": 108, "close": 112, "circuit_flag": False},
    ]
    clean_result = compute_downside_target(1, None, clean_rows)
    mixed_result = compute_downside_target(1, None, mixed_rows)
    assert mixed_result == pytest.approx(clean_result)


def test_downside_circuit_window_shrinkage_no_crash():
    """Filtering reduces clean rows below ATR_PERIOD — must degrade gracefully."""
    two_clean = [
        {"high": 110, "low": 100, "close": 105, "circuit_flag": False},
        {"high": 115, "low": 108, "close": 112, "circuit_flag": False},
    ]
    circuit_rows = [
        {"high": 111, "low": 110, "close": 110.5, "circuit_flag": True}
        for _ in range(ATR_PERIOD)
    ]
    rows = two_clean + circuit_rows
    result = compute_downside_target(1, None, rows)
    assert 0.01 <= result <= 0.30  # no crash, valid output


def test_downside_circuit_last_row_uses_clean_close():
    """Circuit-locked last row excluded — last_close sourced from last clean row."""
    clean_only = [
        {"high": 110, "low": 100, "close": 105, "circuit_flag": False},
        {"high": 115, "low": 108, "close": 112, "circuit_flag": False},
    ]
    with_circuit_tail = clean_only + [
        {"high": 112, "low": 112, "close": 112, "circuit_flag": True},
    ]
    clean_result = compute_downside_target(1, None, clean_only)
    circuit_result = compute_downside_target(1, None, with_circuit_tail)
    assert circuit_result == pytest.approx(clean_result)
