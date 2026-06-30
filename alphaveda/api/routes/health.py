"""GET /health — liveness + data presence gate.

ohlcv_rows > 0 is required for Session A milestone. HTTP 200 alone is
not sufficient — the milestone check must confirm real data is present.
"""
from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter
from src.config import get_supabase_client

router = APIRouter()


@router.get("/health")
def health() -> dict:
    sb = get_supabase_client()

    ohlcv_count = (
        sb.table("ohlcv").select("id", count="exact").execute().count or 0
    )

    ingest_rows = (
        sb.table("ingest_status")
        .select("status,last_run")
        .eq("status", "OK")
        .order("last_run", desc=True)
        .limit(1)
        .execute()
    )
    last_ok = ingest_rows.data[0] if ingest_rows.data else None

    return {
        "status": "ok",
        "ohlcv_rows": ohlcv_count,
        "last_ingest": last_ok["last_run"] if last_ok else None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
