"""Regression tests keeping backtest signal replay aligned with the live engine."""
from types import SimpleNamespace

import pytest

from scripts import backtest
from src.signals import engine


class _CapturedSignal(Exception):
    """Stop the live DB orchestration once its momentum signal is available."""


class _Query:
    def __init__(self, rows):
        self._rows = rows

    def __getattr__(self, _name):
        return lambda *_args, **_kwargs: self

    def execute(self):
        return SimpleNamespace(data=self._rows)


class _EngineClient:
    def __init__(self, ohlcv_rows):
        self._table_rows = {
            "instruments": [{"id": 1, "ticker": "TEST", "classification": "stalwart"}],
            "macro_regime": [{"regime": "RISK_ON", "nifty_vix": 14.0}],
            "ohlcv": ohlcv_rows,
            "accuracy_predictions": [],
        }

    def table(self, name):
        return _Query(self._table_rows[name])


def _backtest_momentum_signal(monkeypatch, ret):
    captured = {}

    def capture(signals, *_args):
        captured.update(signals[0])
        return {
            "direction": signals[0]["direction"],
            "calibrated_p": signals[0]["confidence"] / 100.0,
        }

    monkeypatch.setattr(backtest, "emit_pipeline", capture)
    signal_close = 100.0 * (1.0 + ret)
    backtest._replay_instrument(
        rows=[
            {"open": 100.0, "close": signal_close},
            {"open": signal_close, "close": signal_close},
        ],
        segment_obs=0,
        hit_rate=0.5,
        streak_count=0,
    )
    return captured["direction"], captured["confidence"]


def _live_momentum_signal(monkeypatch, ret):
    def capture(signals, *_args):
        signal = signals[0]
        raise _CapturedSignal((signal["direction"], signal["confidence"]))

    signal_close = 100.0 * (1.0 + ret)
    # emit_signal requests descending rows from the DB, then reverses them.
    client = _EngineClient([
        {"open": 100.0, "close": signal_close},
        {"open": 100.0, "close": 100.0},
    ])
    monkeypatch.setattr("src.config.get_supabase_client", lambda: client)
    monkeypatch.setattr(engine, "emit_pipeline", capture)

    with pytest.raises(_CapturedSignal) as exc_info:
        engine.emit_signal(instrument_id=1, as_of="2026-07-14")
    return exc_info.value.args[0]


@pytest.mark.parametrize(
    ("ret", "expected_direction"),
    [
        pytest.param(0.02, "BULL", id="positive-return"),
        pytest.param(-0.02, "BEAR", id="negative-return"),
        pytest.param(0.0, "BULL", id="zero-return-boundary"),
    ],
)
def test_backtest_momentum_price_matches_live_engine(monkeypatch, ret, expected_direction):
    """Replay and live paths must emit exactly the same direction and confidence."""
    replay_result = _backtest_momentum_signal(monkeypatch, ret)
    live_result = _live_momentum_signal(monkeypatch, ret)

    assert replay_result == live_result
    assert replay_result[0] == expected_direction
