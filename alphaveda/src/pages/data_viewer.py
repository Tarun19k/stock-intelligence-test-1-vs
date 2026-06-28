"""Data viewer page — OHLCV and fundamentals display.

Varghese condition: PAGE_REQUIRES_DISCLAIMER = True — injected by app.py on every render.
Imran SRA condition: staleness banner shown when ingest_status is STALE or MISSING.
"""
from __future__ import annotations
from datetime import date, datetime

PAGE_REQUIRES_DISCLAIMER: bool = True

_STALE_BANNER = (
    "⚠️ Market data hasn't updated since {last_run}. "
    "Signals shown may be based on older prices."
)
_MISSING_BANNER = (
    "🔴 Market data is not yet available. "
    "Data refreshes automatically after market close each trading day."
)


def get_staleness_banner(supabase_client) -> str | None:
    """Query ingest_status and return a banner string if data is stale or missing.

    Returns None when the last ingest was today or yesterday (OK state).
    Imran SRA condition: surfaces as visible UI warning, never silent.
    """
    from src.ingest.bhavcopy import get_ingest_staleness_flag
    try:
        result = (
            supabase_client.table("ingest_status")
            .select("last_run")
            .eq("status", "OK")
            .order("last_run", desc=True)
            .limit(1)
            .execute()
        )
        if not result.data:
            return _MISSING_BANNER
        last_run = datetime.fromisoformat(result.data[0]["last_run"]).date()
        flag = get_ingest_staleness_flag(last_run, date.today())
        if flag == "STALE":
            return _STALE_BANNER.format(last_run=last_run.isoformat())
        return None
    except Exception:
        return _MISSING_BANNER


def render() -> None:
    """Streamlit render entry point — called by app.py navigation."""
    import streamlit as st
    from src.config import get_supabase_client

    st.header("Data Viewer")
    st.caption("OHLCV and fundamentals for tracked instruments.")

    banner = get_staleness_banner(get_supabase_client())
    if banner:
        st.warning(banner)
    else:
        st.info("Connect to Supabase and seed instruments to view data here.")
