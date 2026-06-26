#!/usr/bin/env python3
"""Daily ingest orchestrator — called by GHA at EOD.

Steps:
  1. Download NSE Bhavcopy for target_date
  2. Parse and upsert OHLCV rows (source=bhavcopy_nse, licence_class=open)
  3. Resolve open predictions against actual closes (circuit_flag rows excluded)
  4. Write ingest_status row (OK or ERROR)

Usage:
  python scripts/ingest.py               # today
  python scripts/ingest.py 2026-06-26    # specific date
"""
from __future__ import annotations

import os
import sys
from datetime import date

# Ensure alphaveda/ is on the path when run from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def run_ingest(target_date: date | None = None) -> dict:
    """Run the full ingest pipeline for target_date (defaults to today).

    Returns a summary dict with ohlcv_rows, outcomes_resolved, status.
    On error, status='ERROR' and error key is set; ingest_status row written.
    """
    if target_date is None:
        target_date = date.today()

    from src.config import get_supabase_client
    supabase = get_supabase_client()

    summary: dict = {
        "date": target_date.isoformat(),
        "ohlcv_rows": 0,
        "outcomes_resolved": 0,
        "status": "OK",
    }

    try:
        from src.ingest.bhavcopy import download_bhavcopy_nse, parse_bhavcopy_nse
        csv_bytes = download_bhavcopy_nse(target_date.isoformat())
        rows = parse_bhavcopy_nse(csv_bytes.decode("utf-8", errors="replace"))
        summary["ohlcv_rows"] = len(rows)

        # Upsert OHLCV rows (on conflict symbol+date → update)
        if rows:
            for row in rows:
                row["as_of"] = target_date.isoformat()
                row["ingested_at"] = "now()"
            supabase.table("ohlcv").upsert(rows, on_conflict="symbol,as_of").execute()

        # Resolve open predictions
        from src.ingest.resolve_outcomes import resolve_outcomes_from_ohlcv
        open_preds = (
            supabase.table("accuracy_predictions")
            .select("id, symbol, direction, entry_price")
            .is_("outcome", "null")
            .execute()
        ).data or []
        resolutions = resolve_outcomes_from_ohlcv(open_preds, rows)
        summary["outcomes_resolved"] = len(resolutions)

        for res in resolutions:
            supabase.table("accuracy_predictions").update({
                "outcome": res["outcome"],
                "actual_close": res["actual_close"],
            }).eq("id", res["prediction_id"]).execute()

        # Write OK ingest_status row
        supabase.table("ingest_status").insert({
            "run_at": target_date.isoformat(),
            "status": "OK",
            "ohlcv_rows": len(rows),
            "outcomes_resolved": len(resolutions),
        }).execute()

    except Exception as exc:
        summary["status"] = "ERROR"
        summary["error"] = str(exc)
        try:
            supabase.table("ingest_status").insert({
                "run_at": target_date.isoformat(),
                "status": "ERROR",
                "error_message": str(exc)[:500],
            }).execute()
        except Exception:
            pass  # DB write failed — log to stdout only

    return summary


if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    target = date.fromisoformat(date_arg) if date_arg else None
    result = run_ingest(target)
    print(result)
    sys.exit(0 if result["status"] == "OK" else 1)
