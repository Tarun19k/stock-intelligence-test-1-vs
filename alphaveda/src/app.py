"""AlphaVeda — Streamlit entry point.

SEBI disclaimer (Varghese): injected via get_disclaimer_html() on every page render.
The disclaimer is pinned as fixed-bottom HTML — never conditional, collapsible, or dismissable.
"""
from __future__ import annotations
from constants import SEBI_DISCLAIMER

_DISCLAIMER_HTML = f'<div class="av-sebi-footer">{SEBI_DISCLAIMER}</div>'


def get_disclaimer_html() -> str:
    """Return the fixed-bottom SEBI disclaimer HTML block.

    Always returns the full SEBI_DISCLAIMER text — never empty, never conditional.
    Called once per page render by the app entry point.
    """
    return _DISCLAIMER_HTML


def main() -> None:
    """Streamlit app entry point."""
    import streamlit as st
    from src.pages import data_viewer, signals, path, accuracy
    from src.styles import get_css

    st.set_page_config(
        page_title="AlphaVeda",
        page_icon="◈",
        layout="wide",
    )

    # Design system CSS — must inject before any content
    st.markdown(get_css(), unsafe_allow_html=True)

    # SEBI disclaimer pinned — fires before any page content (Varghese requirement)
    st.markdown(get_disclaimer_html(), unsafe_allow_html=True)

    _NAV_LABELS = {
        "Data Viewer": "Market Data",
        "Signals": "Signals",
        "Path": "Path",
        "Accuracy": "Accuracy",
    }

    page = st.sidebar.radio(
        "Navigate",
        options=list(_NAV_LABELS.keys()),
        format_func=lambda k: _NAV_LABELS[k],
        label_visibility="collapsed",
    )

    page_map = {
        "Data Viewer": data_viewer,
        "Signals": signals,
        "Path": path,
        "Accuracy": accuracy,
    }
    page_map[page].render()


if __name__ == "__main__":
    main()
