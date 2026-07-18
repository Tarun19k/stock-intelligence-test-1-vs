#!/usr/bin/env python3
"""Daily ingest orchestrator — called by GHA at EOD.

Steps:
  1. Download NSE Bhavcopy for target_date
  2. Resolve symbol → instrument_id via instruments table
  3. Upsert OHLCV rows (circuit_flag set by parser)
  4. Emit predictions for each active instrument (emit_signal → accuracy_predictions)
  5. Resolve open predictions against actual closes (circuit rows excluded)
  6. Write accuracy_outcomes rows (hit + return_pct)
  7. Write ingest_status row (OK / NO_DATA / SKIPPED_HOLIDAY / ERROR)

Usage:
  python scripts/ingest.py               # today
  python scripts/ingest.py 2026-06-26    # specific date

Schema reference (FALLBACK_SCHEMA in schema_viewer.py):
  ohlcv          : instrument_id, as_of, open/high/low/close, volume,
                   circuit_flag, licence_class, source, ingested_at (DEFAULT now())
  ingest_status  : source (NN), last_run, rows_written, status
  accuracy_outcomes: prediction_id (NN), outcome_date (NN), actual_direction (NN),
                     is_correct (NN), resolved_at (DEFAULT now()), hit (DEFAULT false),
                     return_pct, actual_return, peak_return_pct
                     (verified live via information_schema 2026-07-13 — outcome_date/
                     actual_direction/is_correct were NOT NULL with no default and were
                     silently unpopulated by Step 6 until this date; fixed same day)
"""
from __future__ import annotations

import os
import sys
from datetime import date, timedelta

# Ensure alphaveda/ is on the path when run from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Load .env from workspace root (two levels up from alphaveda/scripts/)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"), override=False)
except ImportError:
    pass  # dotenv not installed — env vars must be set in shell


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

    # Idempotency guard (G23): the ingest trigger now has two independent sources
    # (RemoteTrigger primary, GHA schedule: backup) that can both fire for the same
    # target_date if the primary is late and the backup also lands. Without this
    # check, a duplicate fire would re-run Steps 1-7 and double-insert predictions/
    # outcomes for a date already processed. An OK row for this exact date means
    # ingest already completed successfully — skip cleanly rather than reprocess.
    #
    # BUG FIXED 2026-07-18: the original version compared `last_run` (a timestamptz
    # column, stored as e.g. "2026-07-17T00:00:00+00:00") to a bare date string via
    # .eq() — this silently never matched, so the guard never actually skipped a
    # real duplicate. Confirmed live: a manual trigger 2.5h after a successful
    # scheduled run reprocessed the full pipeline instead of skipping, writing a
    # second set of predictions for the same day. Fixed with an explicit UTC
    # date-range comparison instead of relying on implicit type casting.
    range_start = f"{target_date.isoformat()}T00:00:00+00:00"
    range_end = f"{(target_date + timedelta(days=1)).isoformat()}T00:00:00+00:00"
    existing = (
        supabase.table("ingest_status")
        .select("id, status")
        .gte("last_run", range_start)
        .lt("last_run", range_end)
        .eq("status", "OK")
        .limit(1)
        .execute()
    )
    if existing.data:
        return {"date": target_date.isoformat(), "ohlcv_rows": 0,
                "outcomes_resolved": 0, "status": "SKIPPED_ALREADY_DONE",
                "existing_ingest_status_id": existing.data[0]["id"]}

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
        "predictions_emitted": 0,
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

        # Step 2: Fetch all seeded instruments (one query), join against bhavcopy in Python.
        # We do NOT pass all 2,000+ bhavcopy tickers to Supabase — the URL would exceed
        # PostgREST limits and return a 400. The instruments table is always small
        # (tens to hundreds of rows), so fetching it wholesale is correct and fast.
        inst_result = (
            supabase.table("instruments")
            .select("id, ticker")
            .eq("is_active", True)
            .execute()
        )
        symbol_to_id: dict[str, int] = {r["ticker"]: r["id"] for r in (inst_result.data or [])}
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
                "trade_date": target_date.isoformat(),  # DB column is trade_date (not as_of)
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

        # Step 3: Upsert OHLCV (conflict on instrument_id + trade_date per UNIQUE constraint).
        if ohlcv_rows:
            supabase.table("ohlcv").upsert(ohlcv_rows, on_conflict="instrument_id,trade_date").execute()
        summary["ohlcv_rows"] = len(ohlcv_rows)

        # Step 4: Emit predictions for each instrument that appeared in today's bhavcopy.
        # Fail-open: one instrument failing must not abort the full ingest.
        from src.signals.engine import emit_signal
        predictions_emitted = 0
        for iid in symbol_to_id.values():
            try:
                emitted = emit_signal(instrument_id=iid, as_of=target_date.isoformat())
                if emitted is not None:
                    predictions_emitted += 1
            except Exception as emit_exc:
                print(f"[WARN] emit_signal skipped instrument_id={iid}: {emit_exc}", flush=True)
        summary["predictions_emitted"] = predictions_emitted
        print(f"[INFO] Emitted {predictions_emitted} predictions for {target_date}", flush=True)

        # Step 5: Batch-resolve entry prices — ONE query for all predictions.
        # Avoids N+1 Supabase calls (one per prediction) under production load.
        #
        # G18 fix (2026-07-12, calibration-integrity + SRE council review): this step
        # previously had NO horizon-maturity gate and NO terminal-resolution check —
        # every row in accuracy_predictions was re-resolved on every ingest run, and
        # because accuracy_outcomes' unique constraint is on (prediction_id,
        # resolved_at) rather than prediction_id alone, each run appended a NEW
        # outcome row for the same prediction with that day's price. A prediction
        # could accumulate a different hit/miss verdict every day it stayed in the
        # query, corrupting the ledger's own promise that a stated horizon (T+1)
        # means anything. Two independent gates fix this:
        #   1. Horizon maturity: only resolve predictions where emitted_at's date +
        #      horizon_days <= target_date (the horizon has actually elapsed).
        #   2. Terminal exclusion: never re-resolve a prediction_id that already has
        #      an accuracy_outcomes row, regardless of horizon — once resolved, done.
        from src.ingest.resolve_outcomes import resolve_outcomes_from_ohlcv
        # DB column is 'direction' (not 'signal_direction') — resolve_outcomes.py
        # uses the Python key 'signal_direction', so we remap at dict-build time.
        already_resolved_ids = {
            row["prediction_id"]
            for row in (
                supabase.table("accuracy_outcomes")
                .select("prediction_id")
                .execute()
            ).data or []
        }
        open_preds_all = (
            supabase.table("accuracy_predictions")
            .select("id, instrument_id, direction, emitted_at, horizon_days")
            .execute()
        ).data or []

        open_preds_raw = []
        for p in open_preds_all:
            if p["id"] in already_resolved_ids:
                continue  # terminal — already scored, never re-resolve
            emitted_date = date.fromisoformat(p["emitted_at"][:10])
            horizon_days = p.get("horizon_days") or 1
            if target_date < emitted_date + timedelta(days=horizon_days):
                continue  # horizon not yet elapsed — leave open for a future run
            open_preds_raw.append(p)

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
                    .select("instrument_id,trade_date,close")
                    .in_("instrument_id", pred_instrument_ids)
                    .in_("trade_date", pred_emit_dates)
                    .execute()
                )
                for row in (prior_batch.data or []):
                    entry_price_map[(row["instrument_id"], row["trade_date"])] = row["close"]

            for pred in open_preds_raw:
                symbol = id_to_symbol.get(pred["instrument_id"])
                if not symbol:
                    continue
                emitted_date = pred["emitted_at"][:10]  # matches trade_date key format
                entry_close = entry_price_map.get((pred["instrument_id"], emitted_date))
                if entry_close is None:
                    continue
                prediction_dicts.append({
                    "id": pred["id"],
                    "symbol": symbol,
                    "signal_direction": pred["direction"],  # remap DB col → Python key
                    "entry_price": entry_close,
                })

        resolutions = resolve_outcomes_from_ohlcv(prediction_dicts, parsed_rows)
        summary["outcomes_resolved"] = len(resolutions)

        # Step 6: Batch upsert accuracy_outcomes — idempotent on (prediction_id, resolved_at).
        # Requires unique constraint — see supabase/migrations/0014_accuracy_outcomes_unique.sql.
        # Replaces per-row insert() which caused silent double-scoring on re-runs.
        #
        # 2026-07-13 fix: outcome_date/actual_direction/is_correct are live NOT NULL
        # columns (verified via information_schema) that this upsert never populated,
        # causing every real ingest run to fail on the first resolved-outcomes batch
        # since G18 shipped. outcome_date mirrors resolved_at (same event, same day);
        # actual_direction/is_correct are the observed-outcome counterparts to hit/
        # return_pct, computed in resolve_outcomes_from_ohlcv().
        if resolutions:
            outcome_rows = [
                {
                    "prediction_id": res["prediction_id"],
                    "outcome_date": target_date.isoformat(),
                    "resolved_at": target_date.isoformat(),
                    "hit": res["hit"],
                    "is_correct": res["hit"],
                    "actual_direction": res["actual_direction"],
                    "return_pct": res["return_pct"],
                    "actual_return": res["return_pct"],
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
