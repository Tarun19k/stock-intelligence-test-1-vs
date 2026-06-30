"""GET /market-data — active instruments with latest OHLCV.

Two-query pattern: instruments (small, always full fetch) then latest
OHLCV date + rows for that date. No N+1 queries (Imran's requirement).
"""
from __future__ import annotations
from datetime import date
from fastapi import APIRouter
from src.config import get_supabase_client
from api._envelope import envelope

router = APIRouter()


@router.get("")
def market_data() -> dict:
    sb = get_supabase_client()

    instruments = (
        sb.table("instruments")
        .select("id,ticker,name,classification")
        .eq("is_active", True)
        .execute()
        .data or []
    )

    if not instruments:
        return envelope([], as_of=date.today())

    # Find latest trade date across all OHLCV rows.
    latest = (
        sb.table("ohlcv")
        .select("trade_date")
        .order("trade_date", desc=True)
        .limit(1)
        .execute()
    )
    if not latest.data:
        # Instruments seeded but no OHLCV yet — honest empty state.
        result = [
            {
                "ticker": i["ticker"],
                "name": i.get("name"),
                "classification": i["classification"],
                "close": None,
                "volume": None,
                "trade_date": None,
            }
            for i in instruments
        ]
        return envelope(result, as_of=date.today())

    latest_date = latest.data[0]["trade_date"]

    ohlcv_rows = (
        sb.table("ohlcv")
        .select("instrument_id,open,high,low,close,volume,trade_date")
        .eq("trade_date", latest_date)
        .execute()
        .data or []
    )
    ohlcv_map = {r["instrument_id"]: r for r in ohlcv_rows}

    result = []
    for inst in instruments:
        o = ohlcv_map.get(inst["id"])
        result.append({
            "ticker": inst["ticker"],
            "name": inst.get("name"),
            "classification": inst["classification"],
            "close": o["close"] if o else None,
            "volume": o["volume"] if o else None,
            "trade_date": o["trade_date"] if o else None,
        })

    return envelope(result, as_of=date.fromisoformat(latest_date))
