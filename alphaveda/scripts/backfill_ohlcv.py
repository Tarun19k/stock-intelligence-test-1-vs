#!/usr/bin/env python3
"""Standalone historical OHLCV backfill — NOT wired into the live ingest.py pipeline.

Deliberately kept separate from scripts/ingest.py (which handles today's daily EOD
ingest + prediction emission + outcome resolution). This script has one job: pull
N trading days of historical daily OHLCV for a single instrument from NSE Bhavcopy
and upsert it into the `ohlcv` table, using the exact same provenance conventions
ingest.py already uses.

Data source: NSE Bhavcopy archive (nsearchives.nseindia.com), the same open-licence
source scripts/ingest.py uses for daily EOD. Confirmed empirically (2026-07-21) that
the archive serves at least 1 calendar year of historical daily files at the same
URL pattern used for "today" — no separate historical API, package, or yfinance
fallback was needed. yfinance was NOT used: commercial-gate state is irrelevant here
because Bhavcopy already covers this need and is the licensed source of truth.

Idempotent / safe to re-run: upserts on the real unique constraint
`ohlcv_instrument_id_trade_date_key` = UNIQUE (instrument_id, trade_date), confirmed
live via pg_constraint on the alphaveda-prod Supabase project (kowlkczswaglbmabygtl).
By default, dates already present for the target instrument are skipped (no re-fetch)
to reduce load on NSE's archive; pass --force to overwrite them anyway.

Schema (confirmed live via information_schema, 2026-07-21):
  ohlcv: id (PK), instrument_id (NOT NULL, FK -> instruments.id), trade_date (NOT
  NULL, date), open/high/low/close (NOT NULL, numeric), volume (NOT NULL, bigint),
  source (NOT NULL, varchar(50)), ingested_at (NOT NULL, timestamptz, DEFAULT now()),
  circuit_flag (NOT NULL, boolean, DEFAULT false), deliverable_volume (nullable),
  licence_class (nullable text, CHECK IN ('personal','commercial','open'),
  DEFAULT 'personal' — ALWAYS pass 'open' explicitly for Bhavcopy rows, do not rely
  on the column default).

Usage:
  python scripts/backfill_ohlcv.py --ticker RELIANCE --instrument-id 4
  python scripts/backfill_ohlcv.py --ticker RELIANCE --instrument-id 4 --trading-days 252
  python scripts/backfill_ohlcv.py --ticker RELIANCE --instrument-id 4 --dry-run
  python scripts/backfill_ohlcv.py --ticker RELIANCE --instrument-id 4 --force

This script does NOT loop over multiple instruments on its own — each invocation is
scoped to exactly one ticker/instrument_id, passed explicitly on the command line.
There is no "backfill everything" mode; a caller wanting the full 14-instrument
backfill must invoke this once per instrument, each a separate, auditable call.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import date, timedelta

# Ensure alphaveda/ is on the path when run from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"), override=False)
except ImportError:
    pass  # dotenv not installed — env vars must be set in shell

_REQUEST_DELAY_SECONDS = 0.4  # be polite to NSE's archive; avoid rate-limit/IP-block risk
_UPSERT_BATCH_SIZE = 50


def _trading_days(end_date: date, n_days: int) -> list[date]:
    """Return the last n_days NSE trading days up to and including end_date, oldest first.

    Uses the same exchange-calendar-aware / Mon-Fri-fallback logic as ingest.py's
    _is_trading_day, walking backward from end_date until n_days trading days are found.
    """
    try:
        import pandas_market_calendars as mcal
        nse = mcal.get_calendar("NSE")
        start_probe = end_date - timedelta(days=int(n_days * 1.6) + 15)  # generous buffer for holidays/weekends
        schedule = nse.schedule(start_date=start_probe.isoformat(), end_date=end_date.isoformat())
        days = [d.date() for d in schedule.index]
        return days[-n_days:]
    except Exception:
        # Fallback: Mon-Fri only (no holiday awareness)
        days: list[date] = []
        d = end_date
        while len(days) < n_days:
            if d.weekday() < 5:
                days.append(d)
            d -= timedelta(days=1)
        return sorted(days)


def run_backfill(
    ticker: str,
    instrument_id: int,
    trading_days: int = 252,
    end_date: date | None = None,
    force: bool = False,
    dry_run: bool = False,
) -> dict:
    """Backfill `trading_days` trading days of historical daily OHLCV for one instrument.

    Returns a summary dict: {ticker, instrument_id, requested, already_present,
    fetched, written, failed, failed_dates, status}.
    """
    if end_date is None:
        end_date = date.today()

    from src.config import get_supabase_client
    supabase = get_supabase_client()

    target_days = _trading_days(end_date, trading_days)

    summary: dict = {
        "ticker": ticker,
        "instrument_id": instrument_id,
        "requested": len(target_days),
        "already_present": 0,
        "fetched": 0,
        "written": 0,
        "failed": 0,
        "failed_dates": [],
        "status": "OK",
    }

    # Skip dates already present for this instrument unless --force.
    days_to_fetch = target_days
    if not force:
        existing = (
            supabase.table("ohlcv")
            .select("trade_date")
            .eq("instrument_id", instrument_id)
            .in_("trade_date", [d.isoformat() for d in target_days])
            .execute()
        )
        existing_dates = {row["trade_date"] for row in (existing.data or [])}
        summary["already_present"] = len(existing_dates)
        days_to_fetch = [d for d in target_days if d.isoformat() not in existing_dates]

    if dry_run:
        summary["status"] = "DRY_RUN"
        summary["would_fetch"] = [d.isoformat() for d in days_to_fetch]
        return summary

    from src.ingest.bhavcopy import download_bhavcopy_nse, parse_bhavcopy_nse

    def _flush(pending: list[dict]) -> None:
        """Upsert whatever has accumulated so far. Called incrementally (not just at
        the end) so a slow run that gets interrupted partway through still has its
        already-fetched rows durably written — nothing sits only in memory."""
        if not pending:
            return
        supabase.table("ohlcv").upsert(pending, on_conflict="instrument_id,trade_date").execute()
        summary["written"] += len(pending)
        pending.clear()

    rows_to_upsert: list[dict] = []
    for i, d in enumerate(days_to_fetch):
        if i > 0:
            time.sleep(_REQUEST_DELAY_SECONDS)
        try:
            csv_bytes = download_bhavcopy_nse(d.isoformat())
            parsed_rows = parse_bhavcopy_nse(csv_bytes.decode("utf-8", errors="replace"))
        except Exception as exc:
            print(f"[WARN] download/parse failed for {d.isoformat()}: {exc}", flush=True)
            summary["failed"] += 1
            summary["failed_dates"].append(d.isoformat())
            continue

        match = next((r for r in parsed_rows if r["symbol"] == ticker), None)
        if match is None:
            # Either a genuine no-trade day for this symbol, or a holiday the
            # exchange-calendar didn't know about. Not a hard failure.
            print(f"[INFO] no {ticker} row in bhavcopy for {d.isoformat()} — skipping", flush=True)
            continue

        summary["fetched"] += 1
        rows_to_upsert.append({
            "instrument_id": instrument_id,
            "trade_date": d.isoformat(),
            "open": match["open"],
            "high": match["high"],
            "low": match["low"],
            "close": match["close"],
            "volume": match["volume"],
            "circuit_flag": match["circuit_flag"],
            "licence_class": match["licence_class"],  # 'open' — from parse_bhavcopy_nse
            "source": match["source"],  # 'bhavcopy_nse' — from parse_bhavcopy_nse
            # ingested_at omitted — DB DEFAULT now() handles it, matches ingest.py convention
        })
        print(f"[INFO] fetched {ticker} {d.isoformat()} close={match['close']}", flush=True)

        if len(rows_to_upsert) >= _UPSERT_BATCH_SIZE:
            _flush(rows_to_upsert)

    _flush(rows_to_upsert)  # final partial batch

    if summary["failed"] > 0 and summary["written"] == 0:
        summary["status"] = "ERROR"
    elif summary["failed"] > 0:
        summary["status"] = "PARTIAL"

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ticker", required=True, help="NSE symbol, e.g. RELIANCE")
    parser.add_argument("--instrument-id", required=True, type=int, help="instruments.id for this ticker")
    parser.add_argument("--trading-days", type=int, default=252, help="number of trading days to backfill (default 252)")
    parser.add_argument("--end-date", type=str, default=None, help="YYYY-MM-DD, defaults to today")
    parser.add_argument("--force", action="store_true", help="re-fetch and overwrite dates already present")
    parser.add_argument("--dry-run", action="store_true", help="print the trading-day list without writing")
    args = parser.parse_args()

    end = date.fromisoformat(args.end_date) if args.end_date else None
    result = run_backfill(
        ticker=args.ticker,
        instrument_id=args.instrument_id,
        trading_days=args.trading_days,
        end_date=end,
        force=args.force,
        dry_run=args.dry_run,
    )
    print(result)
    sys.exit(0 if result["status"] in ("OK", "DRY_RUN", "PARTIAL") else 1)
