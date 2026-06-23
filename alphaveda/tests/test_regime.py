"""Phase 2 — regime.py tests.
All tests use mocks: macro_regime has no seed data (Dalio's requirement).
Live DB tests deferred to G0 gate once ingest has seeded real rows.
"""
import pytest
from datetime import date
from unittest.mock import MagicMock, patch


def _mock_client(data: list) -> MagicMock:
    mock = MagicMock()
    (mock.table.return_value
         .select.return_value
         .lte.return_value
         .order.return_value
         .limit.return_value
         .execute.return_value
         .data) = data
    return mock


def test_regime_as_of_join():
    """Returns the most recent regime row where effective_date <= emitted_at."""
    mock = _mock_client([
        {"regime": "RISK_ON", "effective_date": "2026-06-01", "nifty_close": 22000}
    ])
    with patch("src.data.regime.get_supabase_client", return_value=mock):
        from src.data.regime import get_current_regime
        result = get_current_regime(date(2026, 6, 21))
    assert result is not None
    assert result["regime"] == "RISK_ON"


def test_regime_returns_none_when_empty():
    """Must return None (not raise) when macro_regime is empty — Dalio's empty-table path."""
    mock = _mock_client([])
    with patch("src.data.regime.get_supabase_client", return_value=mock):
        from src.data.regime import get_current_regime
        result = get_current_regime(date(2026, 6, 21))
    assert result is None


def test_regime_returns_none_on_db_exception():
    """Any exception → None. Caller checks staleness; this function never raises."""
    mock = MagicMock()
    mock.table.side_effect = Exception("DB unreachable")
    with patch("src.data.regime.get_supabase_client", return_value=mock):
        from src.data.regime import get_current_regime
        result = get_current_regime(date(2026, 6, 21))
    assert result is None


def test_regime_lte_called_with_correct_date():
    """Verify the as-of join uses lte(effective_date) not just latest row."""
    mock = _mock_client([{"regime": "RISK_OFF", "effective_date": "2026-05-01"}])
    with patch("src.data.regime.get_supabase_client", return_value=mock):
        from src.data.regime import get_current_regime
        result = get_current_regime(date(2026, 5, 15))
    mock.table.return_value.select.return_value.lte.assert_called_once_with(
        "effective_date", "2026-05-15"
    )
    assert result["regime"] == "RISK_OFF"


def test_regime_order_desc():
    """Query must order by effective_date descending to get most recent row."""
    mock = _mock_client([{"regime": "RISK_ON", "effective_date": "2026-06-01"}])
    with patch("src.data.regime.get_supabase_client", return_value=mock):
        from src.data.regime import get_current_regime
        get_current_regime(date(2026, 6, 21))
    mock.table.return_value.select.return_value.lte.return_value.order.assert_called_once_with(
        "effective_date", desc=True
    )
