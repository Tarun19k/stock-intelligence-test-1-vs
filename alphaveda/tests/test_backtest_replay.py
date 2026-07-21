"""Tests for scripts/backtest_replay.py — the Phase 0 backtest/refinement harness.

Replaces tests/test_backtest.py (deleted along with scripts/backtest.py).
The old test pinned scripts/backtest.py's independently-reimplemented
formula against src/signals/engine.py's real formula; its fixtures also
predated the RF-I fix (no trade_date field) and its parity check started
failing the moment engine.py changed underneath it. backtest_replay.py has
no formula of its own to drift — it imports compute_momentum_signal() and
emit_pipeline() directly — so there is nothing left to pin in that shape.
What's worth keeping from the old test is the *idea* of a concrete,
independently-verifiable expected value; that's what test_fixture below is.
"""
from __future__ import annotations

from datetime import date, timedelta
from types import SimpleNamespace

import pytest

from scripts import backtest_replay
from src.signals.engine import compute_momentum_signal, emit_pipeline


# ── shared fake Supabase client (read-only accuracy/OHLCV context) ─────────

class _Query:
    def __init__(self, rows):
        self._rows = rows

    def __getattr__(self, _name):
        return lambda *_args, **_kwargs: self

    def execute(self):
        return SimpleNamespace(data=self._rows)


class _FakeClient:
    """Fixed, in-memory Supabase stand-in — every table returns the same
    canned rows regardless of filters, matching the pattern used by the
    (now-deleted) tests/test_backtest.py's fake client. Good enough here
    because _historical_rows/_accuracy_context only ever call
    .table(name).select(...)....execute() and read .data."""

    def __init__(self, ohlcv_rows):
        self._tables = {
            "ohlcv": ohlcv_rows,
            "accuracy_predictions": [],
            "accuracy_outcomes": [],
            "bt_backtest_runs": [],
            "bt_backtest_attribution": [],
        }
        self._next_run_id = 1

    def table(self, name):
        if name == "bt_backtest_runs":
            return _InsertCapture(self, name)
        return _Query(self._tables[name])


class _InsertCapture:
    """Minimal insert-capable stand-in for bt_backtest_runs so dry_run=False
    paths (not exercised by these tests, but kept honest) would also work."""

    def __init__(self, client, name):
        self._client = client
        self._name = name
        self._payload = None

    def insert(self, payload):
        self._payload = payload
        return self

    def execute(self):
        run_id = self._client._next_run_id
        self._client._next_run_id += 1
        row = {**self._payload, "id": run_id}
        self._client._tables[self._name].append(row)
        return SimpleNamespace(data=[row])


def _business_days(start: date, n: int) -> list[date]:
    days: list[date] = []
    d = start
    while len(days) < n:
        if d.weekday() < 5:  # Mon-Fri
            days.append(d)
        d += timedelta(days=1)
    return days


# ── Test 1: fixture-based, hand-computed expected result ───────────────────
#
# Hand calculation (independently derived from the documented formula in
# src/signals/engine.py, not by calling the code under test — reproduced
# here so it can be checked by eye):
#
#   24 business days, 2026-01-05 (Mon) .. 2026-02-05.
#   close = 100.0 for the first 23 days, close = 100.5 on the 24th (last) day.
#   as_of = 2026-02-05 (the last day).
#
#   Step 1 — reference row:
#     target = as_of - 21 calendar days = 2026-01-15.
#     tolerance = target +/- 3 weekday sessions = [2026-01-12, 2026-01-20].
#     2026-01-15 itself is a Thursday and IS one of the 24 business days, so
#     it's in the candidate set and is the closest (0-day) match.
#     reference row = 2026-01-15, close = 100.0.
#     ret = (100.5 - 100.0) / 100.0 = 0.005  ->  direction = BULL.
#
#   Step 2 — volatility normalization:
#     stdev window = last 21 closes = [100.0]*20 + [100.5].
#     period_returns = [0.0]*19 + [0.005]   (20 values, only the last nonzero)
#     mean = 0.005 / 20 = 0.00025
#     sum((x-mean)^2) = 19*(0.00025)^2 + (0.005-0.00025)^2
#                      = 19*6.25e-8 + 0.00475^2
#                      = 1.1875e-6 + 2.25625e-5 = 2.375e-5
#     sample variance = 2.375e-5 / (20-1) = 1.25e-6
#     stdev = sqrt(1.25e-6) = 0.0011180339887498949
#
#   Step 3 — confidence:
#     CONFIDENCE_SCALE = 2.5 * ARBITRATION_MARGIN = 2.5 * 15.0 = 37.5
#     z = |ret| / stdev = 0.005 / 0.0011180339887498949 = 4.47213595499958
#     confidence = min(z * 37.5, 100.0) = min(167.7..., 100.0) = 100.0  (capped)
#
#   Step 4 — arbitration: single BULL signal, weight=1.0 -> bull_score=100.0,
#     bear_score=0.0, |diff|=100.0 >= ARBITRATION_MARGIN (15.0) -> emits BULL,
#     confidence=100.0.
#
#   Step 5 — calibration (cold start, hit_rate=0.5, streak_count=0 so no
#     streak discount since 0 < STREAK_WINDOW=5):
#     calibrated_p = min(confidence/100.0, hit_rate) = min(1.0, 0.5) = 0.5.
#
# Verified independently via a standalone arithmetic script before writing
# these assertions (not by running engine.py).

def test_fixture_hand_computed_momentum_signal():
    days = _business_days(date(2026, 1, 5), 24)
    closes = [100.0] * 23 + [100.5]
    rows = [{"trade_date": d.isoformat(), "close": c} for d, c in zip(days, closes)]
    as_of = days[-1].isoformat()

    signals = compute_momentum_signal(rows, as_of)
    assert signals is not None
    assert len(signals) == 1
    assert signals[0]["direction"] == "BULL"
    assert signals[0]["signal_name"] == "momentum_price"
    assert signals[0]["confidence"] == pytest.approx(100.0, abs=1e-9)

    result = emit_pipeline(signals, streak_count=0, segment_obs=0, hit_rate=0.5)
    assert result is not None
    assert result["direction"] == "BULL"
    assert result["calibrated_p"] == pytest.approx(0.5, abs=1e-12)
    assert result["streak_discounted"] is False


def test_fixture_hand_computed_bear_direction():
    """Mirror case: close drops instead of rises -> BEAR, same magnitude."""
    days = _business_days(date(2026, 1, 5), 24)
    closes = [100.0] * 23 + [99.5]
    rows = [{"trade_date": d.isoformat(), "close": c} for d, c in zip(days, closes)]
    as_of = days[-1].isoformat()

    signals = compute_momentum_signal(rows, as_of)
    assert signals is not None
    assert signals[0]["direction"] == "BEAR"
    assert signals[0]["confidence"] == pytest.approx(100.0, abs=1e-9)


# ── Test 2: determinism ──────────────────────────────────────────────────

def _demo_ohlcv_rows() -> list[dict]:
    """A longer, gently-varying series (60 business days) so the replay
    produces multiple non-suppressed observations, not just the saturated
    single-spike case above — a more realistic determinism check."""
    days = _business_days(date(2025, 11, 1), 60)
    # Deterministic pseudo-variation: no randomness, no wall-clock, so two
    # calls in the same test process are trivially guaranteed identical
    # inputs. That's the point — determinism here is about the HARNESS
    # (does it introduce any non-determinism of its own?), not about the
    # input data being "random but seeded."
    closes = []
    base = 100.0
    for i in range(len(days)):
        # simple deterministic wave, no RNG
        base += 0.3 if i % 3 == 0 else (-0.2 if i % 3 == 1 else 0.1)
        closes.append(round(base, 4))
    return [
        {"trade_date": d.isoformat(), "open": c, "high": c, "low": c,
         "close": c, "circuit_flag": False}
        for d, c in zip(days, closes)
    ]


def test_backtest_replay_determinism():
    rows = _demo_ohlcv_rows()
    weights_config = {"momentum_price": 1.25}

    def _run():
        client = _FakeClient(rows)
        return backtest_replay.run_backtest_replay(
            client,
            weights_config=weights_config,
            start_date=rows[0]["trade_date"],
            end_date=rows[-1]["trade_date"],
            instrument_ids=[999],
            config_label="determinism-test",
            dry_run=True,
        )

    first = _run()
    second = _run()

    # Non-trivial: this fixture must actually produce scoreable observations,
    # otherwise the determinism check would trivially pass on None == None.
    assert first["run_row"]["score"] is not None

    assert first["run_row"]["weights_config"] == second["run_row"]["weights_config"]
    assert first["run_row"]["score"] == second["run_row"]["score"]
    assert first["run_row"]["data_depth_days"] == second["run_row"]["data_depth_days"]
    assert first["run_row"]["insufficient_depth"] == second["run_row"]["insufficient_depth"]
    assert first["attribution_rows"] == second["attribution_rows"]


def test_weights_config_missing_signal_fails_loud():
    """A weights_config that doesn't cover an emitted signal must raise, not
    silently default a weight — silent defaults are the exact drift this
    harness exists to prevent."""
    with pytest.raises(ValueError, match="momentum_price"):
        backtest_replay._weighted_signals(
            [{"direction": "BULL", "confidence": 50.0,
              "signal_name": "momentum_price", "weight": 1.0}],
            {"some_other_signal": 2.0},
        )


def test_empty_weights_config_passes_through_unchanged():
    base = [{"direction": "BULL", "confidence": 50.0,
             "signal_name": "momentum_price", "weight": 1.0}]
    assert backtest_replay._weighted_signals(base, {}) == base


def test_stale_reference_is_suppressed_and_reason_captured():
    """A single OHLCV row (no history 21 days back) must suppress via
    RF-I_STALE_REFERENCE, and backtest_replay must capture that reason
    rather than silently dropping it."""
    rows = [{"trade_date": "2026-02-05", "close": 100.0}]
    signals, reason = backtest_replay._capture_suppression_reason(
        "src.signals.engine", compute_momentum_signal, rows, "2026-02-05",
    )
    assert signals is None
    assert reason is not None
    assert "RF-I_STALE_REFERENCE" in reason
