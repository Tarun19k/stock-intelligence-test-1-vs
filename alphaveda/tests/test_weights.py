"""Phase 3 — weights.py tests.
load_weights: returns DB active weights or COLD_START_WEIGHTS fallback.
"""
import pytest
from unittest.mock import MagicMock, patch
from src.signals.weights import load_weights
from constants import COLD_START_WEIGHTS, FUNDAMENTAL_WEIGHT_FLOOR

FUNDAMENTAL_SIGNALS = {"roic", "fcf", "eps_growth", "peg", "dividend", "debt_equity", "book_value"}


def _mock_client(rows: list) -> MagicMock:
    m = MagicMock()
    (m.table.return_value
       .select.return_value
       .eq.return_value
       .eq.return_value
       .eq.return_value
       .execute.return_value
       .data) = rows
    return m


def test_cold_start_returned_when_no_db_rows():
    """Empty DB result → COLD_START_WEIGHTS for the given segment."""
    with patch("src.signals.weights.get_supabase_client", return_value=_mock_client([])):
        result = load_weights(lynch_class="stalwart", regime="RISK_ON")
    assert result == COLD_START_WEIGHTS["stalwart"]


def test_active_weights_returned_from_db():
    """DB rows present → use them instead of cold-start."""
    db_rows = [
        {"signal_name": "roic", "weight": 0.50},
        {"signal_name": "fcf",  "weight": 0.50},
    ]
    with patch("src.signals.weights.get_supabase_client", return_value=_mock_client(db_rows)):
        result = load_weights(lynch_class="stalwart", regime="RISK_ON")
    assert result == {"roic": 0.50, "fcf": 0.50}


def test_invalid_lynch_class_raises():
    """Unknown lynch_class with empty DB → ValueError (no cold-start to fall back to)."""
    with patch("src.signals.weights.get_supabase_client", return_value=_mock_client([])):
        with pytest.raises(ValueError, match="No weights"):
            load_weights(lynch_class="unknown_class", regime="RISK_ON")


def test_cold_start_fundamental_floor_satisfied():
    """All cold-start segments must satisfy the Buffett fundamental floor."""
    with patch("src.signals.weights.get_supabase_client", return_value=_mock_client([])):
        for lynch_class in COLD_START_WEIGHTS:
            result = load_weights(lynch_class=lynch_class, regime="RISK_ON")
            fund_total = sum(v for k, v in result.items() if k in FUNDAMENTAL_SIGNALS)
            assert fund_total >= FUNDAMENTAL_WEIGHT_FLOOR, (
                f"{lynch_class}: fundamental weight {fund_total:.2f} < floor {FUNDAMENTAL_WEIGHT_FLOOR}"
            )


def test_db_exception_falls_back_to_cold_start():
    """DB unreachable → fall back to cold-start (not fail-closed, as weights are not security-critical)."""
    m = MagicMock()
    m.table.side_effect = Exception("DB unreachable")
    with patch("src.signals.weights.get_supabase_client", return_value=m):
        result = load_weights(lynch_class="fast_grower", regime="RISK_ON")
    assert result == COLD_START_WEIGHTS["fast_grower"]


def test_extreme_weight_raises_on_db_path():
    """C2: DB row with injected extreme weight raises ValueError before entering pipeline."""
    db_rows = [{"signal_name": "roic", "weight": 1000.0}]
    with patch("src.signals.weights.get_supabase_client", return_value=_mock_client(db_rows)):
        with pytest.raises(ValueError, match="out of valid range"):
            load_weights(lynch_class="stalwart", regime="RISK_ON")


def test_fundamental_floor_violated_raises_on_db_path():
    """C4: DB rows that violate combined fundamental floor raise ValueError."""
    db_rows = [{"signal_name": "roic", "weight": 0.0}]
    with patch("src.signals.weights.get_supabase_client", return_value=_mock_client(db_rows)):
        with pytest.raises(ValueError, match="FUNDAMENTAL_WEIGHT_FLOOR"):
            load_weights(lynch_class="stalwart", regime="RISK_ON")
