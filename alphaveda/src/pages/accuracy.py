"""Accuracy ledger page — signal hit-rate and PROPOSED weight review.

Munger condition: get_staleness_warning() returns a warning when last review > 90 days ago.
PAGE_REQUIRES_DISCLAIMER = True (Varghese).
"""
from __future__ import annotations
from datetime import date

PAGE_REQUIRES_DISCLAIMER: bool = True

_STALENESS_DAYS = 90
_STALENESS_WARNING = (
    "Signal weights have not been reviewed in over {days} days (last review: {last_date}). "
    "Review accuracy ledger and promote or archive stale PROPOSED entries."
)


def get_staleness_warning(last_review_date: date) -> str | None:
    """Return staleness warning when last_review_date is more than 90 days ago, else None."""
    delta = (date.today() - last_review_date).days
    if delta > _STALENESS_DAYS:
        return _STALENESS_WARNING.format(days=delta, last_date=last_review_date.isoformat())
    return None


def get_proposed_weights_count() -> int:
    """Return count of signal_weights rows in PROPOSED status.
    Delegates to signals.get_proposed_weights_count — single source of truth for DB query.
    """
    from src.pages.signals import get_proposed_weights_count as _count
    return _count()


def get_proposed_weights_summary() -> dict:
    """Return a summary dict of pending PROPOSED weights for the accuracy tab UI."""
    count = get_proposed_weights_count()
    return {"count": count, "has_pending": count > 0}


def render() -> None:
    """Streamlit render entry point — called by app.py navigation."""
    import streamlit as st
    st.header("Accuracy Ledger")
    st.caption("Per-segment signal hit-rate vs proposed weights.")
    st.info("Accuracy data will populate once predictions reach OBSERVATION_THRESHOLD.")
