"""Accuracy ledger — streak flag computation.

The streak flag signals that the model has been consistently correct for
STREAK_WINDOW consecutive predictions on the same instrument+direction.
The flag is read by the emit pipeline (step 3b) to apply STREAK_DISCOUNT_FACTOR
BEFORE calibration — this is the pipeline contract (Soros condition).
"""
from __future__ import annotations
from constants import STREAK_WINDOW


def compute_streak_flag(consecutive_count: int) -> bool:
    """True when consecutive same-direction correct predictions >= STREAK_WINDOW."""
    return consecutive_count >= STREAK_WINDOW
