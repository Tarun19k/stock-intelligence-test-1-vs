"""Data viewer page — OHLCV and fundamentals display.

Varghese condition: PAGE_REQUIRES_DISCLAIMER = True — injected by app.py on every render.
"""
from __future__ import annotations

PAGE_REQUIRES_DISCLAIMER: bool = True


def render() -> None:
    """Streamlit render entry point — called by app.py navigation."""
    import streamlit as st
    st.header("Data Viewer")
    st.caption("OHLCV and fundamentals for tracked instruments.")
    st.info("Connect to Supabase and seed instruments to view data here.")
