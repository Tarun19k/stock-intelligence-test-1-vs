"""Phase 3 — approve_signal_weight() tests.

Governance rule: no signal_weights status change PROPOSED → ACTIVE without
approved_by='tarun'. Automation cannot approve weights.
"""
import pytest
import unittest.mock as mock
from src.signals.weights import approve_signal_weight


def _mock_select_chain(data: list) -> mock.MagicMock:
    m = mock.MagicMock()
    (m.table.return_value
     .select.return_value
     .eq.return_value
     .limit.return_value
     .execute.return_value.data) = data
    return m


def test_approve_rejects_non_proposed():
    """Approval gate rejects any status that is not PROPOSED."""
    for non_proposed_status in ("ACTIVE", "ARCHIVED"):
        m = _mock_select_chain([{"id": 1, "status": non_proposed_status}])
        with mock.patch("src.signals.weights.get_supabase_client", return_value=m):
            with pytest.raises(ValueError, match="expected 'PROPOSED'"):
                approve_signal_weight(1)


def test_approve_rejects_missing_row():
    """Approval gate rejects when the weight_id does not exist."""
    m = _mock_select_chain([])
    with mock.patch("src.signals.weights.get_supabase_client", return_value=m):
        with pytest.raises(ValueError, match="not found"):
            approve_signal_weight(99)
