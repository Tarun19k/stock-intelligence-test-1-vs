"""Phase 3 — ledger.py tests.
compute_streak_flag: True when consecutive_count >= STREAK_WINDOW.
"""
import pytest
from constants import STREAK_WINDOW
from src.accuracy.ledger import compute_streak_flag


def test_below_window_is_false():
    assert compute_streak_flag(consecutive_count=STREAK_WINDOW - 1) is False


def test_at_window_is_true():
    assert compute_streak_flag(consecutive_count=STREAK_WINDOW) is True


def test_above_window_is_true():
    assert compute_streak_flag(consecutive_count=STREAK_WINDOW + 2) is True


def test_zero_is_false():
    assert compute_streak_flag(consecutive_count=0) is False


def test_one_is_false():
    assert compute_streak_flag(consecutive_count=1) is False


def test_large_count_is_true():
    assert compute_streak_flag(consecutive_count=STREAK_WINDOW * 10) is True


def test_returns_bool_not_int():
    """Return type must be bool, not a truthy int (e.g. 1)."""
    result = compute_streak_flag(consecutive_count=STREAK_WINDOW)
    assert isinstance(result, bool)
