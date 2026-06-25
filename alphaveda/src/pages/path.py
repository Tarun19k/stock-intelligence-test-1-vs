"""Path page — Kelly sizing and rupee display.

Constraint Enforcer condition: rupee_size is None when is_commercial()=True.
Tanvi Rao condition: get_suppression_label() presents suppression as deliberate state.
PAGE_REQUIRES_DISCLAIMER = True (Varghese).
"""
from __future__ import annotations
from constants import PORTFOLIO_VALUE
from src.config import is_commercial

PAGE_REQUIRES_DISCLAIMER: bool = True

_SUPPRESSION_LABEL = (
    "Position size is shown as direction + confidence only. "
    "Rupee sizing is reserved for personal research use (pre-commercial state)."
)


def get_kelly_display_data(
    calibrated_p: float,
    magnitude_target: float,
    downside_target: float | None,
) -> dict:
    """Return display dict for the Path page.

    Keys:
      direction  : "BULLISH" | "BEARISH"
      rupee_size : float (position rupees) when not commercial; None when commercial
      suppressed : True when commercial=True and rupee is withheld
    """
    from src.portfolio.optimizer import kelly_position_size

    direction = "BULLISH" if calibrated_p >= 0.5 else "BEARISH"

    if is_commercial():
        return {"direction": direction, "rupee_size": None, "suppressed": True}

    rupee = kelly_position_size(
        p=calibrated_p,
        magnitude_target=magnitude_target,
        downside_target=downside_target,
        portfolio_value=PORTFOLIO_VALUE,
    )
    return {"direction": direction, "rupee_size": rupee, "suppressed": False}


def get_proposed_weights_count() -> int:
    """Delegate to signals.get_proposed_weights_count — path page shares the same banner."""
    from src.pages.signals import get_proposed_weights_count as _count
    return _count()


def get_weight_review_banner() -> str | None:
    """Return weight review banner if PROPOSED weights exist (mirrors signals page)."""
    from src.pages.signals import _WEIGHT_REVIEW_BANNER
    count = get_proposed_weights_count()
    if count == 0:
        return None
    return _WEIGHT_REVIEW_BANNER.format(count=count)


def get_suppression_label() -> str:
    """Return the rupee-suppression state label — deliberate state, not degraded fallback."""
    return _SUPPRESSION_LABEL


def render() -> None:
    """Streamlit render entry point — called by app.py navigation."""
    import streamlit as st
    st.header("Path")

    commercial = is_commercial()
    if commercial:
        st.info(get_suppression_label())

    st.caption("Signal direction and sizing are research-only. See SEBI disclaimer below.")
    st.info("Select an instrument and segment to view Kelly sizing path.")
