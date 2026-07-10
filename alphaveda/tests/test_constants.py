"""Phase 1 — constants.py tests. These pass immediately (constants.py is implemented first)."""
import pytest
from constants import (
    FUNDAMENTAL_WEIGHT_FLOOR,
    STREAK_WINDOW,
    STREAK_DISCOUNT_FACTOR,
    OBSERVATION_THRESHOLD,
    PROPOSAL_MIN_DELTA,
    QUARTER_KELLY_FRACTION,
    PORTFOLIO_VALUE,
    MAX_POSITION_PCT,
    SECTOR_CAP_PCT,
    CASH_FLOOR_PCT,
    ATR_PERIOD,
    E2_CONSECUTIVE_THRESHOLD,
    E2_CONFIDENCE_FLOOR,
    COLD_START_WEIGHTS,
    SEBI_DISCLAIMER,
    ARBITRATION_MARGIN,
    REGIME_STALENESS_DAYS,
)


def test_fundamental_floor_value():
    assert FUNDAMENTAL_WEIGHT_FLOOR == 0.30


def test_streak_constants():
    assert STREAK_WINDOW == 5
    assert 0 < STREAK_DISCOUNT_FACTOR < 1.0


def test_kelly_fraction():
    assert QUARTER_KELLY_FRACTION == 0.25


def test_position_bounds():
    assert MAX_POSITION_PCT == 0.10
    assert SECTOR_CAP_PCT == 0.35
    assert CASH_FLOOR_PCT == 0.10


def test_atr_period():
    assert ATR_PERIOD == 14


def test_e2_bucket_thresholds():
    assert E2_CONSECUTIVE_THRESHOLD["near_term"] == 3
    assert E2_CONSECUTIVE_THRESHOLD["medium_term"] == 5
    assert E2_CONSECUTIVE_THRESHOLD["long_term"] == 7


def test_e2_confidence_floor():
    assert E2_CONFIDENCE_FLOOR == 50


def test_cold_start_weights_sum_to_1():
    for cls, weights in COLD_START_WEIGHTS.items():
        total = sum(weights.values())
        assert abs(total - 1.0) < 1e-6, f"{cls} weights sum to {total}, not 1.0"


def test_fundamental_floor_applies_to_all_cold_starts():
    """ROIC + FCF + pledge combined must be >= FUNDAMENTAL_WEIGHT_FLOOR for every class."""
    fundamental_signals = {"roic", "fcf", "pledge"}
    for cls, weights in COLD_START_WEIGHTS.items():
        combined = sum(v for k, v in weights.items() if k in fundamental_signals)
        assert combined >= FUNDAMENTAL_WEIGHT_FLOOR, (
            f"{cls}: fundamentals weight {combined:.2f} < floor {FUNDAMENTAL_WEIGHT_FLOOR}"
        )


def test_sebi_disclaimer_non_empty():
    assert len(SEBI_DISCLAIMER) > 50
    assert "investment advice" in SEBI_DISCLAIMER.lower()
    assert "not" in SEBI_DISCLAIMER.lower()


def test_arbitration_margin_pinned():
    """C5: Pin ARBITRATION_MARGIN at 15.0 — any refactor moving it to config must fail this test."""
    assert ARBITRATION_MARGIN == 15.0


def test_regime_staleness_days():
    assert REGIME_STALENESS_DAYS == 3


def test_generated_ts_disclaimer_matches_source():
    """NG-4 / A2: web/lib/sebi-disclaimer.generated.ts must stay byte-identical to
    what alphaveda/scripts/generate_sebi_disclaimer_ts.py would produce from
    constants.py right now. This is the single source-of-truth guarantee — if
    someone edits SEBI_DISCLAIMER without regenerating, or hand-edits the .generated.ts
    file, this test fails CI.
    """
    import sys
    from pathlib import Path

    alphaveda_dir = Path(__file__).resolve().parents[1]
    scripts_dir = alphaveda_dir / "scripts"
    sys.path.insert(0, str(scripts_dir))
    from generate_sebi_disclaimer_ts import render  # noqa: E402

    generated_path = alphaveda_dir / "web" / "lib" / "sebi-disclaimer.generated.ts"
    expected = render(SEBI_DISCLAIMER)
    actual = generated_path.read_text(encoding="utf-8")
    assert actual == expected, (
        "sebi-disclaimer.generated.ts is out of sync with constants.py SEBI_DISCLAIMER. "
        "Run: python3 alphaveda/scripts/generate_sebi_disclaimer_ts.py"
    )
