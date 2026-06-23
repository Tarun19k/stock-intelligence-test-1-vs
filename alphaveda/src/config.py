"""Supabase client singleton + commercial gate.

get_supabase_client(): module-level singleton — one connection per process (Imran's requirement).
is_commercial(): derived from waitlist.converted_at, never from env flag. Fail-closed=True.
"""
from __future__ import annotations
import os
from supabase import create_client, Client

_client: Client | None = None


def get_supabase_client() -> Client:
    """Return the module-level Supabase client, creating it once per process."""
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
        _client = create_client(url, key)
    return _client


def is_commercial() -> bool:
    """True if any waitlist row has converted_at set (first non-self subscriber).
    Fail-closed: any exception returns True to block yfinance under unknown state.
    """
    try:
        result = (
            get_supabase_client()
            .table("waitlist")
            .select("id")
            .not_.is_("converted_at", None)
            .limit(1)
            .execute()
        )
        return len(result.data) > 0
    except Exception:
        return True
