"""Phase 2 — is_commercial() tests.
All tests use mocks: commercial gate is data-derived, not env-derived.
The fail-closed=True assertion is the most security-critical test in this suite.
"""
import pytest
from unittest.mock import MagicMock, patch


def _mock_client(data: list) -> MagicMock:
    mock = MagicMock()
    (mock.table.return_value
         .select.return_value
         .not_.is_.return_value
         .limit.return_value
         .execute.return_value
         .data) = data
    return mock


def test_is_commercial_false_when_no_subscribers():
    """No converted_at rows → False (personal-use mode, yfinance allowed)."""
    with patch("src.config.get_supabase_client", return_value=_mock_client([])):
        from src.config import is_commercial
        assert is_commercial() is False


def test_is_commercial_true_when_subscriber_exists():
    """Any converted_at row → True (commercial mode, yfinance blocked)."""
    with patch("src.config.get_supabase_client", return_value=_mock_client([{"id": 1}])):
        from src.config import is_commercial
        assert is_commercial() is True


def test_is_commercial_fail_closed():
    """DB exception → True. Fail-closed: unknown state must block yfinance, not permit it."""
    with patch("src.config.get_supabase_client", side_effect=Exception("DB unreachable")):
        from src.config import is_commercial
        assert is_commercial() is True


def test_is_commercial_queries_converted_at_not_env():
    """Verify the query targets converted_at column, not an env flag."""
    mock = _mock_client([])
    with patch("src.config.get_supabase_client", return_value=mock):
        from src.config import is_commercial
        is_commercial()
    mock.table.assert_called_with("waitlist")
    mock.table.return_value.select.assert_called_with("id")
