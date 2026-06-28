"""NSE/BSE Bhavcopy download and parse.

Bhavcopy is NSE/BSE's daily end-of-day price file (open licence).
parse_bhavcopy_nse() is a pure function — safe to unit test without network.
download_bhavcopy_nse() hits the NSE archive — only called from scripts/ingest.py.
"""
from __future__ import annotations

import csv
import io
import ssl
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


def _detect_circuit_flag(h: float, l: float, c: float) -> bool:
    """Proxy circuit detection: H == L == C > 0 indicates a locked-price bar.

    NSE Bhavcopy has no explicit circuit column. When all trades occur at a
    single price (circuit limit), H=L=C. This is approximate — a genuine single-
    trade day can also show H=L=C. G1 replaces this with the explicit ±5/10/20%
    price-band check against the prior day's close.
    """
    return c > 0 and h == l == c


def parse_bhavcopy_nse(csv_text: str) -> list[dict]:
    """Parse NSE Bhavcopy CSV text into OHLCV row dicts.

    Only rows with SERIES in {EQ, BE, BL} are included (excludes derivatives,
    ETFs-on-debt, and other non-equity instruments). Malformed numeric rows are
    silently skipped.

    Returned keys per row: symbol, open, high, low, close, volume, source,
    licence_class, circuit_flag.
    """
    reader = csv.DictReader(io.StringIO(csv_text))
    # NSE Bhavcopy uses "SYMBOL, SERIES, ..." headers with spaces after commas.
    # csv.DictReader preserves those spaces in field names (e.g. " SERIES" not "SERIES").
    # Strip all field names so lookups work regardless of NSE's formatting.
    if reader.fieldnames:
        reader.fieldnames = [f.strip() for f in reader.fieldnames]
    rows: list[dict] = []
    for row in reader:
        if row.get("SERIES", "").strip() not in _VALID_SERIES:
            continue
        try:
            # NSE sec_bhavdata_full columns (as of 2026):
            #   OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, TTL_TRD_QNTY
            # Older format used OPEN/HIGH/LOW/CLOSE/TOTTRDQTY — support both.
            h = float(row.get("HIGH_PRICE") or row["HIGH"])
            l = float(row.get("LOW_PRICE") or row["LOW"])
            c = float(row.get("CLOSE_PRICE") or row["CLOSE"])
            rows.append({
                "symbol": row["SYMBOL"].strip(),
                "open": float(row.get("OPEN_PRICE") or row["OPEN"]),
                "high": h,
                "low": l,
                "close": c,
                "volume": int(float(
                    row.get("TTL_TRD_QNTY") or row.get("TOTTRDQTY") or "0"
                ) or 0),
                "source": "bhavcopy_nse",
                "licence_class": "open",
                "circuit_flag": _detect_circuit_flag(h, l, c),
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
    # macOS Python's bundled SSL roots often miss intermediate CAs used by NSE's CDN.
    # certifi ships Mozilla's curated CA bundle (already a transitive dep via requests).
    try:
        import certifi
        ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ssl_ctx = None  # fall back to system roots
    with urllib.request.urlopen(req, timeout=30, context=ssl_ctx) as resp:
        return resp.read()
