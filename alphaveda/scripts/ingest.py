#!/usr/bin/env python3
"""Daily ingest orchestrator — called by GHA at EOD.

Steps:
  1. Download NSE Bhavcopy for target_date
  2. Resolve symbol → instrument_id via instruments table
  3. Upsert OHLCV rows (circuit_flag set by parser)
  4. Resolve open predictions against actual closes (circuit rows excluded)
  5. Write accuracy_outcomes rows (hit + return_pct)
  6. Write ingest_status row (OK / NO_DATA / SKIPPED_HOLIDAY / ERROR)

Usage:
  python scripts/ingest.py               # today
  python scripts/ingest.py 2026-06-26    # specific date

Schema reference (FALLBACK_SCHEMA in schema_viewer.py):
  ohlcv          : instrument_id, as_of, open/high/low/close, volume,
                   circuit_flag, licence_class, source, ingested_at (DEFAULT now())
  ingest_status  : source (NN), last_run, rows_written, status
  accuracy_outcomes: prediction_id (NN), resolved_at, hit, return_pct
"""
from __future__ import annotations

import os
import sys
from datetime import date

# Ensure alphaveda/ is on the path when run from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _is_trading_day(d: date) -> bool:
    """Return True if d is an NSE trading day (exchange-calendar aware).

    Falls back to Mon-Fri check if pandas_market_calendars is unavailable.
    """
    try:
        import pandas_market_calendars as mcal
        nse = mcal.get_calendar("NSE")
        schedule = nse.schedule(start_date=d.isoformat(), end_date=d.isoformat())
        return not schedule.empty
    except Exception:
        return d.weekday() < 5


def run_ingest(target_date: date | None = None) -> dict:
    """Run the full ingest pipeline for target_date (defaults to today).

    Returns a summary dict with ohlcv_rows, outcomes_resolved, status.
    On error, status='ERROR' and error key is set; ingest_status row written.
    """
    if target_date is None:
        target_date = date.today()

    from src.config import get_supabase_client
    supabase = get_supabase_client()

    # Holiday gate (Dalio condition): write SKIPPED_HOLIDAY, exit cleanly.
    if not _is_trading_day(target_date):
        supabase.table("ingest_status").insert({
            "source": "bhavcopy_nse",
            "last_run": target_date.isoformat(),
            "status": "SKIPPED_HOLIDAY",
            "rows_written": 0,
        }).execute()
        return {"date": target_date.isoformat(), "ohlcv_rows": 0,
                "outcomes_resolved": 0, "status": "SKIPPED_HOLIDAY"}

    summary: dict = {
        "date": target_date.isoformat(),
        "ohlcv_rows": 0,
        "outcomes_resolved": 0,
        "status": "OK",
    }

    try:
        # Step 1: Download + parse
        from src.ingest.bhavcopy import download_bhavcopy_nse, parse_bhavcopy_nse
        csv_bytes = download_bhavcopy_nse(target_date.isoformat())
        parsed_rows = parse_bhavcopy_nse(csv_bytes.decode("utf-8", errors="replace"))

        # Empty-day guard (Marks condition): 0 rows on a trading day = source issue.
        if not parsed_rows:
            supabase.table("ingest_status").insert({
                "source": "bhavcopy_nse",
                "last_run": target_date.isoformat(),
                "status": "NO_DATA",
                "rows_written": 0,
            }).execute()
            summary["status"] = "NO_DATA"
            return summary

        # Step 2: Batch resolve symbol → instrument_id (one query, no N+1).
        symbols = [r["symbol"] for r in parsed_rows]
        inst_result = (
            supabase.table("instruments")
            .select("id, symbol")
            .in_("symbol", symbols)
            .execute()
        )
        symbol_to_id: dict[str, int] = {r["symbol"]: r["id"] for r in (inst_result.data or [])}
        id_to_symbol: dict[int, str] = {v: k for k, v in symbol_to_id.items()}

        # Step 3: Build ohlcv rows mapped to instrument_id.
        ohlcv_rows = []
        symbol_close: dict[str, float] = {}  # reused for outcome resolution
        for row in parsed_rows:
            iid = symbol_to_id.get(row["symbol"])
            if iid is None:
                continue  # instrument not seeded — skip silently
            symbol_close[row["symbol"]] = row["close"]
            ohlcv_rows.append({
                "instrument_id": iid,
                "as_of": target_date.isoformat(),
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "volume": row["volume"],
                "circuit_flag": row["circuit_flag"],
                "licence_class": row["licence_class"],
                "source": row["source"],
                # ingested_at omitted — DEFAULT now() handles it
            })

        # Step 4: Upsert OHLCV (conflict on instrument_id + as_of).
        if ohlcv_rows:
            supabase.table("ohlcv").upsert(ohlcv_rows, on_conflict="instrument_id,as_of").execute()
        summary["ohlcv_rows"] = len(ohlcv_rows)

        # Step 5: Batch-resolve entry prices — ONE query for all predictions.
        # Avoids N+1 Supabase calls (one per prediction) under production load.
        # Horizon maturity gate is a G1 condition (requires target_date migration).
        from src.ingest.resolve_outcomes import resolve_outcomes_from_ohlcv
        open_preds_raw = (
            supabase.table("accuracy_predictions")
            .select("id, instrument_id, signal_direction, emitted_at")
            .execute()
        ).data or []

        prediction_dicts = []
        if open_preds_raw:
            pred_instrument_ids = list({
                p["instrument_id"] for p in open_preds_raw
                if id_to_symbol.get(p["instrument_id"])
            })
            pred_emit_dates = list({p["emitted_at"][:10] for p in open_preds_raw})
            entry_price_map: dict[tuple, float] = {}
            if pred_instrument_ids and pred_emit_dates:
                prior_batch = (
                    supabase.table("ohlcv")
                    .select("instrument_id,as_of,close")
                    .in_("instrument_id", pred_instrument_ids)
                    .in_("as_of", pred_emit_dates)
                    .execute()
                )
                for row in (prior_batch.data or []):
                    entry_price_map[(row["instrument_id"], row["as_of"])] = row["close"]

            for pred in open_preds_raw:
                symbol = id_to_symbol.get(pred["instrument_id"])
                if not symbol:
                    continue
                emitted_date = pred["emitted_at"][:10]
                entry_close = entry_price_map.get((pred["instrument_id"], emitted_date))
                if entry_close is None:
                    continue
                prediction_dicts.append({
                    "id": pred["id"],
                    "symbol": symbol,
                    "signal_direction": pred["signal_direction"],
                    "entry_price": entry_close,
                })

        resolutions = resolve_outcomes_from_ohlcv(prediction_dicts, parsed_rows)
        summary["outcomes_resolved"] = len(resolutions)

        # Step 6: Batch upsert accuracy_outcomes — idempotent on (prediction_id, resolved_at).
        # Requires unique constraint — see supabase/migrations/0014_accuracy_outcomes_unique.sql.
        # Replaces per-row insert() which caused silent double-scoring on re-runs.
        if resolutions:
            outcome_rows = [
                {
                    "prediction_id": res["prediction_id"],
                    "resolved_at": target_date.isoformat(),
                    "hit": res["hit"],
                    "return_pct": res["return_pct"],
                }
                for res in resolutions
            ]
            supabase.table("accuracy_outcomes").upsert(
                outcome_rows,
                on_conflict="prediction_id,resolved_at",
            ).execute()

        # Step 7: Write OK ingest_status row.
        supabase.table("ingest_status").insert({
            "source": "bhavcopy_nse",
            "last_run": target_date.isoformat(),
            "status": "OK",
            "rows_written": len(ohlcv_rows),
        }).execute()

    except Exception as exc:
        summary["status"] = "ERROR"
        summary["error"] = str(exc)
        try:
            supabase.table("ingest_status").insert({
                "source": "bhavcopy_nse",
                "last_run": target_date.isoformat(),
                "status": "ERROR",
                "rows_written": 0,
            }).execute()
        except Exception:
            pass  # DB write failed — log to stdout only

    return summary


if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    target = date.fromisoformat(date_arg) if date_arg else None
    result = run_ingest(target)
    print(result)
    sys.exit(0 if result["status"] in ("OK", "SKIPPED_HOLIDAY") else 1)
