"""NSE/BSE Bhavcopy download and parse.

Bhavcopy is NSE/BSE's daily end-of-day price file (open licence).
parse_bhavcopy_nse() is a pure function — safe to unit test without network.
download_bhavcopy_nse() hits the NSE archive — only called from scripts/ingest.py.
"""
from __future__ import annotations

import csv
import io
import urllib.request
from datetime import date
from typing import Optional

_VALID_SERIES = frozenset({"EQ", "BE", "BL"})

_NSE_URL = (
    "https://nsearchives.nseindia.com/products/content/"
    "sec_bhavdata_full_{ddmmyyyy}.csv"
)

_NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AlphaVeda/1.0; +research-only)",
}


def parse_bhavcopy_nse(csv_text: str) -> list[dict]:
    """Parse NSE Bhavcopy CSV text into OHLCV row dicts.

    Only rows with SERIES in {EQ, BE, BL} are included (excludes derivatives,
    ETFs-on-debt, and other non-equity instruments). Malformed numeric rows are
    silently skipped.

    Returned keys per row: symbol, open, high, low, close, volume, source,
    licence_class.
    """
    reader = csv.DictReader(io.StringIO(csv_text))
    rows: list[dict] = []
    for row in reader:
        if row.get("SERIES", "").strip() not in _VALID_SERIES:
            continue
        try:
            rows.append({
                "symbol": row["SYMBOL"].strip(),
                "open": float(row["OPEN"]),
                "high": float(row["HIGH"]),
                "low": float(row["LOW"]),
                "close": float(row["CLOSE"]),
                "volume": int(float(row.get("TOTTRDQTY", "0") or "0")),
                "source": "bhavcopy_nse",
                "licence_class": "open",
            })
        except (ValueError, KeyError):
            continue
    return rows


def get_ingest_staleness_flag(last_run_at: Optional[date], as_of: date) -> str:
    """Classify ingest freshness for the Imran SRA staleness banner.

    Returns:
      'OK'      — last run was today or yesterday
      'STALE'   — last run was more than 1 day ago
      'MISSING' — no run on record
    """
    if last_run_at is None:
        return "MISSING"
    delta = (as_of - last_run_at).days
    return "OK" if delta <= 1 else "STALE"


def download_bhavcopy_nse(date_str: str) -> bytes:
    """Download NSE Bhavcopy CSV for the given YYYY-MM-DD date string.

    Only called from scripts/ingest.py — not unit-tested (network dependency).
    """
    d = date.fromisoformat(date_str)
    ddmmyyyy = d.strftime("%d%m%Y")
    url = _NSE_URL.format(ddmmyyyy=ddmmyyyy)
    req = urllib.request.Request(url, headers=_NSE_HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()
