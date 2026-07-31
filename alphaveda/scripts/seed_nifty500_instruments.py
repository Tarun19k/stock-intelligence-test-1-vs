#!/usr/bin/env python3
"""Seed instruments from NSE's live official Nifty 500 constituent list.

Every ticker/name/ISIN/sector value here comes from NSE's own published index
file at run time -- nothing is hand-typed (per NO_HARDCODING.md). Newly-seeded
rows get classification='unclassified' + signal_gate_until far in the future:
a real Lynch classification (fast_grower/stalwart/slow_grower/cyclical/
turnaround/asset_play) requires real per-company analysis that hasn't been
done for 484 of these tickers, and engine.py reads this column directly to
pick a signal-weight segment -- guessing would silently drive real signal
output. The gate suppresses emission (same mechanism already used for TMCV's
post-demerger gate) while OHLCV/fundamentals collection can proceed normally.

Dry-run by default. Requires --live-write to actually insert rows.

Usage:
  python3 scripts/seed_nifty500_instruments.py            # dry run
  python3 scripts/seed_nifty500_instruments.py --live-write --i-understand-this-writes-real-financial-data
"""
from __future__ import annotations

import csv
import io
import os
import ssl
import sys
import urllib.request
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"), override=False)
except ImportError:
    pass

NIFTY500_URL = "https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv"
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AlphaVeda/1.0; +research-only)"}

# Gate far enough out that it functions as "held open until a human closes it,"
# not a real forecasted date -- same convention as TMCV's real 2027-01-01 gate,
# just with no real reopen date to anchor to since none exists yet.
UNCLASSIFIED_GATE_UNTIL = "2099-01-01"


def fetch_nifty500() -> list[dict]:
    """Download and parse NSE's live Nifty 500 constituent CSV.

    Returns list of dicts: {name, sector, ticker, series, isin}.
    """
    import certifi
    ctx = ssl.create_default_context(cafile=certifi.where())
    req = urllib.request.Request(NIFTY500_URL, headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        text = resp.read().decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for row in reader:
        rows.append({
            "name": row["Company Name"].strip(),
            "sector": row["Industry"].strip(),
            "ticker": row["Symbol"].strip(),
            "series": row["Series"].strip(),
            "isin": row["ISIN Code"].strip(),
        })
    return rows


def build_new_rows(nifty500: list[dict], existing_tickers: set[str]) -> list[dict]:
    """Rows for tickers not already in instruments, ready for insert."""
    new_rows = []
    for r in nifty500:
        if r["ticker"] in existing_tickers:
            continue
        new_rows.append({
            "ticker": r["ticker"],
            "name": r["name"],
            "exchange": "NSE",
            "classification": "unclassified",
            "isin": r["isin"],
            "sector": r["sector"],
            "is_active": True,
            "signal_gate_until": UNCLASSIFIED_GATE_UNTIL,
        })
    return new_rows


def main() -> None:
    live_write = "--live-write" in sys.argv
    confirmed = "--i-understand-this-writes-real-financial-data" in sys.argv

    print(f"Fetching live Nifty 500 constituent list from NSE ({date.today().isoformat()})...")
    nifty500 = fetch_nifty500()
    print(f"  {len(nifty500)} constituents fetched.")

    from src.config import get_supabase_client
    supabase = get_supabase_client()
    existing = supabase.table("instruments").select("ticker").execute()
    existing_tickers = {r["ticker"] for r in existing.data}
    print(f"  {len(existing_tickers)} tickers already in instruments (unchanged, not touched).")

    new_rows = build_new_rows(nifty500, existing_tickers)
    print(f"  {len(new_rows)} new tickers to seed, classification='unclassified', "
          f"signal_gate_until={UNCLASSIFIED_GATE_UNTIL}.")

    if not live_write:
        print("\nDRY RUN -- no writes made. Sample of first 5 new rows:")
        for r in new_rows[:5]:
            print(f"  {r['ticker']:14s} {r['name']:35s} {r['sector']}")
        print(f"\nRe-run with --live-write --i-understand-this-writes-real-financial-data to write.")
        return

    if not confirmed:
        print("ERROR: --live-write requires --i-understand-this-writes-real-financial-data")
        sys.exit(1)

    written = 0
    for r in new_rows:
        supabase.table("instruments").insert(r).execute()
        written += 1
    print(f"\nLIVE WRITE COMPLETE -- {written} new instruments rows inserted.")


if __name__ == "__main__":
    main()
