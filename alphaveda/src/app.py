"""AlphaVeda — Streamlit entry point.

SEBI disclaimer (Varghese): injected via get_disclaimer_html() on every page render.
The disclaimer is pinned as fixed-bottom HTML — never conditional, collapsible, or dismissable.
"""
from __future__ import annotations
from constants import SEBI_DISCLAIMER

_DISCLAIMER_HTML = (
    '<div style="position:fixed;bottom:0;left:0;width:100%;background:#fffbe6;'
    'border-top:1px solid #e6c800;padding:6px 16px;font-size:0.75rem;z-index:9999;">'
    f'{SEBI_DISCLAIMER}'
    '</div>'
)


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

    st.set_page_config(
        page_title="AlphaVeda",
        page_icon="📊",
        layout="wide",
    )

    # SEBI disclaimer pinned — fires before any page content
    st.markdown(get_disclaimer_html(), unsafe_allow_html=True)

    page = st.sidebar.radio(
        "Navigate",
        options=["Data Viewer", "Signals", "Path", "Accuracy"],
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
