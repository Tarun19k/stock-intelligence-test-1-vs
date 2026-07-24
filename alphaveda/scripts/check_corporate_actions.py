#!/usr/bin/env python3
"""Standing corporate-action / price-discontinuity check for backfilled OHLCV.

WHY THIS EXISTS
----------------
Session 2026-07-2x found that scripts/backfill_ohlcv.py pulls raw NSE Bhavcopy
closes with NO corporate-action (split/bonus/rights/demerger) adjustment. A
raw Bhavcopy close is the ACTUAL traded price on that day — which means an
unadjusted 1:1 bonus or a 1:2 split shows up in the historical series as a
genuine ~50%+ single-day "crash" that never happened economically. Two real,
confirmed instances in the current 1-year backfill:

  - HDFCBANK: 1:1 bonus, ex-date 2025-08-26. DB shows close 2025-08-25 =
    1964.10 -> close 2025-08-26 = 973.40 (-50.44%). Real cause: first-ever
    HDFC Bank bonus issue (record date 2025-08-27; NSE/BSE closed 2025-08-26
    for Ganesh Chaturthi doesn't change the ex-date). Sources: LatestLY,
    Goodreturns, AngelOne, HDFC Sky news coverage of the Aug 26 2025 ex-bonus.
  - PIDILITIND: 1:1 bonus, ex-date 2025-09-23. DB shows close 2025-09-22 =
    3038.00 -> close 2025-09-23 = 1489.30 (-50.98%). Real cause: Pidilite's
    first bonus issue in 15 years (record date 2025-09-23). Sources:
    Economic Times, AngelOne, HDFC Sky, Trendlyne corporate-actions page.

Neither was fixed as part of this check — a real adjustment methodology
decision (multiply/divide historical OHLCV by the corporate-action factor,
decide how deep to backfill-adjust, how to handle circuit_flag rows, etc.)
is a separate, larger task requiring sign-off. This script is DETECTION ONLY.

WHAT THIS SCRIPT DOES
----------------------
NSE/BSE do not expose a clean bulk API for historical corporate actions
(confirmed during G1 fundamentals research this session) — so this script
does NOT attempt to auto-fetch corporate-action calendars. What it DOES do,
because it's mechanically checkable against data already in the DB, is scan
every active instrument's OHLCV series for day-over-day close discontinuities
that exceed a threshold (default 15%) and flag them for manual research —
the same "run a real Tavily/BSE/NSE search on the flagged date" workflow used
to investigate HDFCBANK and PIDILITIND above.

Run this BEFORE any future deep backfill (e.g. the planned 750-day/3-year
Phase 2 pull) so newly-flagged windows get manually researched before they're
trusted for return/volatility calculations.

Usage:
  python scripts/check_corporate_actions.py
  python scripts/check_corporate_actions.py --threshold 0.10
  python scripts/check_corporate_actions.py --ticker HDFCBANK
  python scripts/check_corporate_actions.py --json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"), override=False)
except ImportError:
    pass

DEFAULT_THRESHOLD = 0.15  # 15% day-over-day close move triggers manual review


def _fetch_active_instruments(supabase) -> list[dict]:
    resp = (
        supabase.table("instruments")
        .select("id,ticker,name")
        .eq("is_active", True)
        .order("ticker")
        .execute()
    )
    return resp.data or []


def _fetch_closes(supabase, instrument_id: int) -> list[dict]:
    resp = (
        supabase.table("ohlcv")
        .select("trade_date,close,circuit_flag")
        .eq("instrument_id", instrument_id)
        .order("trade_date")
        .execute()
    )
    return resp.data or []


def find_discontinuities(rows: list[dict], threshold: float) -> list[dict]:
    """Scan a ticker's date-sorted close series for |return| > threshold.

    Rows with circuit_flag=True are still reported but annotated, since a
    circuit-locked day is a plausible (if extreme) genuine market move rather
    than an obvious corporate-action artefact — the annotation lets a human
    reviewer down-weight those without silently dropping them from the scan.
    """
    flagged = []
    prev = None
    for row in rows:
        close = row.get("close")
        if close is None:
            prev = row
            continue
        close = float(close)
        if prev is not None and prev.get("close") is not None:
            prev_close = float(prev["close"])
            if prev_close > 0:
                pct_move = (close - prev_close) / prev_close
                if abs(pct_move) >= threshold:
                    flagged.append({
                        "prev_date": prev["trade_date"],
                        "prev_close": prev_close,
                        "date": row["trade_date"],
                        "close": close,
                        "pct_move": round(pct_move * 100, 2),
                        "circuit_flag_prev": bool(prev.get("circuit_flag")),
                        "circuit_flag_current": bool(row.get("circuit_flag")),
                    })
        prev = row
    return flagged


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                         help=f"Day-over-day close move fraction that triggers a flag (default {DEFAULT_THRESHOLD})")
    parser.add_argument("--ticker", type=str, default=None,
                         help="Restrict the scan to a single ticker (default: all active instruments)")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of a text report")
    args = parser.parse_args()

    from src.config import get_supabase_client
    supabase = get_supabase_client()

    instruments = _fetch_active_instruments(supabase)
    if args.ticker:
        instruments = [i for i in instruments if i["ticker"] == args.ticker]
        if not instruments:
            print(f"[ERROR] ticker {args.ticker!r} not found among active instruments", file=sys.stderr)
            return 2

    results: dict = {
        "run_date": date.today().isoformat(),
        "threshold": args.threshold,
        "instruments_scanned": len(instruments),
        "flags": {},
    }

    total_flags = 0
    for inst in instruments:
        rows = _fetch_closes(supabase, inst["id"])
        flags = find_discontinuities(rows, args.threshold)
        if flags:
            results["flags"][inst["ticker"]] = flags
            total_flags += len(flags)

    results["total_flags"] = total_flags

    if args.json:
        print(json.dumps(results, indent=2, default=str))
        return 0 if total_flags == 0 else 1

    print(f"Corporate-action discontinuity check — {results['run_date']}")
    print(f"Threshold: +/-{args.threshold * 100:.0f}% day-over-day close move")
    print(f"Instruments scanned: {results['instruments_scanned']}")
    print()

    if total_flags == 0:
        print("No discontinuities found. CLEAN.")
        return 0

    print(f"{total_flags} discontinuity(ies) found across {len(results['flags'])} ticker(s):\n")
    for ticker, flags in results["flags"].items():
        print(f"  {ticker}:")
        for f in flags:
            note = ""
            if f["circuit_flag_prev"] or f["circuit_flag_current"]:
                note = "  [circuit_flag set on prev and/or current day — may be a genuine circuit move, not a corp action]"
            print(f"    {f['prev_date']} close={f['prev_close']}  ->  {f['date']} close={f['close']}"
                  f"  ({f['pct_move']:+.2f}%){note}")
        print()

    print("ACTION REQUIRED: research each flagged date against real BSE/NSE corporate-action")
    print("announcements or dated financial news (Tavily/BSE/NSE — not assumption) before")
    print("trusting any return/volatility calculation that spans these dates. Do NOT auto-fix.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
