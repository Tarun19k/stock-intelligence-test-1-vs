# =============================================================================
# DEPRECATED - superseded by alphaveda/web/ (Next.js, live in production).
# This Streamlit page is not maintained and may not reflect current SEBI
# compliance copy or signal logic. Do not use as a reference for current behavior.
# =============================================================================

"""Signals page — signal output with cold-start label and weight review banner.

Tanvi Rao condition: get_cold_start_label() returns a label when segment_obs is below threshold.
Munger condition: get_weight_review_banner() returns a banner when PROPOSED weights exist.
PAGE_REQUIRES_DISCLAIMER = True (Varghese).
"""
from __future__ import annotations
from constants import OBSERVATION_THRESHOLD

PAGE_REQUIRES_DISCLAIMER: bool = True

_COLD_START_LABEL = (
    "Cold-start model — fewer than {threshold} observations in this segment. "
    "Weights are Bayesian priors, not ledger-calibrated."
)

_WEIGHT_REVIEW_BANNER = (
    "⚠ {count} signal weight(s) are in PROPOSED status and await your review. "
    "Use approve_signal_weight() to promote or archive."
)


def get_cold_start_label(segment_obs: int) -> str | None:
    """Return cold-start label when segment_obs < OBSERVATION_THRESHOLD, else None."""
    if segment_obs < OBSERVATION_THRESHOLD:
        return _COLD_START_LABEL.format(threshold=OBSERVATION_THRESHOLD)
    return None


def get_proposed_weights_count() -> int:
    """Return count of signal_weights rows in PROPOSED status."""
    from src.config import get_supabase_client
    try:
        result = (
            get_supabase_client()
            .table("signal_weights")
            .select("id", count="exact")
            .eq("status", "PROPOSED")
            .execute()
        )
        return result.count or 0
    except Exception:
        return 0


def get_weight_review_banner() -> str | None:
    """Return review banner when PROPOSED weights exist, else None."""
    count = get_proposed_weights_count()
    if count == 0:
        return None
    return _WEIGHT_REVIEW_BANNER.format(count=count)


def render() -> None:
    """Streamlit render entry point — called by app.py navigation."""
    import streamlit as st
    st.header("Signals")

    banner = get_weight_review_banner()
    if banner:
        st.warning(banner)

    st.caption("Signal output is research-only. See SEBI disclaimer below.")
    st.info("Select an instrument and segment to view signals.")
