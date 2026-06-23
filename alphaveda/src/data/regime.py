"""Macro regime reader — as-of join against macro_regime table.

Returns the most recent regime row where effective_date <= emitted_at.
Returns None (not raises) when the table is empty or the DB is unreachable.
Stale-regime detection is the caller's responsibility (REGIME_STALENESS_DAYS from constants).
"""
from __future__ import annotations
from datetime import date
from typing import Optional
from src.config import get_supabase_client


def get_current_regime(emitted_at: date) -> Optional[dict]:
    """As-of join: SELECT * FROM macro_regime WHERE effective_date <= :emitted_at
    ORDER BY effective_date DESC LIMIT 1.

    Returns None when:
    - macro_regime is empty
    - no row predates emitted_at
    - any exception occurs (DB down, auth failure, etc.)
    """
    try:
        result = (
            get_supabase_client()
            .table("macro_regime")
            .select("*")
            .lte("effective_date", str(emitted_at))
            .order("effective_date", desc=True)
            .limit(1)
            .execute()
        )
        if not result.data:
            return None
        return result.data[0]
    except Exception:
        return None
