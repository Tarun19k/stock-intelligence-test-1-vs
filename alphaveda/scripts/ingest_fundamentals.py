#!/usr/bin/env python3
"""Standalone BSE XBRL fundamentals ingest — NOT wired into scripts/ingest.py.

Deliberately kept separate (same pattern as scripts/backfill_ohlcv.py). ingest.py
handles daily OHLCV + signal emission; this script has one job: locate each active
instrument's latest quarterly "Financial Results" filing on BSE, run it through the
existing pure parser (src/ingest/fundamentals.py: parse_bse_xbrl_fundamentals — NOT
reimplemented here), and upsert into the `fundamentals` table using the same
provenance conventions scripts/ingest.py already uses (source, ingested_at DEFAULT
now(), explicit `open` licence per .claude/rules/DATA_SOURCES.md).

=============================================================================
HONEST FINDING (researched + live-tested 2026-07-24) — read before extending
=============================================================================
BSE does NOT publish a bulk daily/quarterly XBRL fundamentals archive analogous to
the NSE/BSE Bhavcopy CSV. What exists instead, confirmed by hitting BSE's own public
JSON endpoints directly (no key/auth required):

1. Scrip master — bulk, works today:
   GET https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w
   Returns ~4,900 rows in one call: {SCRIP_CD, scrip_id, ISIN_NUMBER, Scrip_Name, ...}.
   Live-tested: 200 OK, 4927 rows, RELIANCE -> SCRIP_CD 500325 confirmed by ISIN match.
   This is what _fetch_scrip_master() below uses to resolve instruments.isin -> BSE
   scrip code — the one part of this pipeline that genuinely IS bulk/archive-shaped.

2. Per-company corporate announcements feed — works today, but PER SCRIP CODE, not
   bulk (must be called once per instrument, like backfill_ohlcv.py's one-ticker-per-
   invocation OHLCV pattern, except this one IS safe to loop automatically since it's
   a real JSON API, not a manual UI form):
   GET https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w
       ?pageno=1&strCat=-1&strPrevDate=YYYYMMDD&strScrip=<SCRIP_CD>
       &strSearch=P&strToDate=YYYYMMDD&strType=C&subcategory=-1
   Live-tested against RELIANCE (500325): 200 OK, real rows, including one with
   CATEGORYNAME="Result", SUBCATNAME="Financial Results", dated 2026-07-17. This
   confirms an automatable, no-manual-lookup path to *find* each instrument's latest
   results filing. _find_latest_result_filing() below uses this.

3. THE GENUINE GAP — turning a located filing into parse_bse_xbrl_fundamentals()'s
   input dict is NOT automated by this script, and here is exactly why:
   - The announcement-feed row for a "Result" filing carries only metadata (NEWSID,
     ATTACHMENTNAME, a headline) plus a link to an attachment. The attachment for the
     filing this script found live was a PDF, not machine-readable XBRL XML — BSE's
     circular (02.04.2025) confirms the actual "Integrated Filing – Financial" XBRL
     submission is a *separate* Listing-Centre subsystem from the general
     announcement/PDF feed, and it is not exposed through any documented bulk or
     per-scrip JSON API. Every public scraper surveyed (BseIndiaApi, bsedata,
     stock-news, screener-scraper) covers price/announcement/corporate-action data —
     none of them parse real BSE XBRL financial-results XML into structured fields.
   - Even granting access to a raw XBRL XML file, XBRL is a namespaced, tag-based
     format (Ind-AS taxonomy elements such as ifrs-full:ProfitLoss). roic, peg, and
     eps_growth are not primitive XBRL facts — they are ratios AlphaVeda would have
     to derive from raw line items (PAT, revenue, shareholders' equity, EPS history).
     Building that tag-to-ratio extractor is a nontrivial, separate piece of
     engineering that does not exist anywhere in this codebase today. Writing a
     fragile guess-the-tag-names scraper for it — silently producing wrong financial
     figures that would flow into a SEBI-adjacent research tool — is a worse outcome
     than not shipping it, so this script does not attempt it.
   Per the dispatch brief's explicit allowance, this is reported honestly rather than
   forced: the FETCH step (per-instrument filing discovery) is real and automated
   below; the XBRL-XML -> flat-dict EXTRACTION step is a missing, separately-scoped
   component. A --manual-input JSON file (see below) lets a human paste already-
   extracted XBRL fields per ticker so the parse -> map -> upsert path can still be
   exercised end-to-end today.

=============================================================================
SECOND GENUINE GAP — parse_bse_xbrl_fundamentals() output vs. the live `fundamentals`
table schema (confirmed live via Supabase MCP list_tables against project
kowlkczswaglbmabygtl, 2026-07-24; table currently has 0 rows):

  fundamentals columns: id, instrument_id, period_end (DATE, NOT NULL), roic_pct,
  fcf_cr, promoter_pledge_pct, debt_equity, eps, revenue_cr, source, ingested_at.

  parse_bse_xbrl_fundamentals() output keys: symbol, source, roic, fcf, eps_growth,
  peg, dividend, debt_equity, book_value.

  Overlap is partial:
    roic         -> roic_pct       (mapped; units NOT verified equal — see below)
    fcf          -> fcf_cr         (mapped; units NOT verified equal — see below)
    debt_equity  -> debt_equity    (direct match)
    source       -> source         (direct match)
  No destination column exists for: eps_growth, peg, dividend, book_value — these
  are DROPPED (never written) and reported explicitly per-row in dry-run output,
  not silently discarded.
  No source field exists for: period_end, promoter_pledge_pct, eps, revenue_cr —
  period_end MUST be supplied externally (--period-end or a "period_end" key in the
  --manual-input JSON; the DB column is NOT NULL, so a row cannot be built without
  it). promoter_pledge_pct/eps/revenue_cr are left NULL.
  Unit mismatch risk (NOT resolved here — flagged for whoever wires a real XBRL
  extractor): fcf_cr's "_cr" suffix strongly implies crores; parse_bse_xbrl_fundamentals
  applies no unit conversion, it only casts to float. A real extractor must produce
  fcf already in crores before this script's mapping step, or figures will be wrong
  by orders of magnitude. Same caution applies to roic_pct (percentage vs. fraction).

=============================================================================
THIRD GENUINE GAP — no UNIQUE constraint on fundamentals(instrument_id, period_end).
Confirmed live: the table's only constraint is the PK on `id`. scripts/ingest.py and
backfill_ohlcv.py both upsert with on_conflict=... against a real unique constraint;
that pattern is NOT available here without a migration (out of scope for this
dispatch — DDL changes are an irreversible-replace class write per the External
State Write Gate and need separate go/no-go authorization). Instead, this script
mimics ingest.py's own idempotency-guard style (see run_ingest.py's G23 comment):
SELECT for an existing (instrument_id, period_end) row first, skip if found, INSERT
(not upsert) otherwise. This is application-level idempotency, not a DB constraint —
a genuine gap, called out rather than quietly worked around with a fabricated
on_conflict target that would raise at runtime.

=============================================================================
Usage:
  python scripts/ingest_fundamentals.py --dry-run
  python scripts/ingest_fundamentals.py --dry-run --tickers RELIANCE,TCS,INFY
  python scripts/ingest_fundamentals.py --dry-run \
      --manual-input path/to/xbrl_fields.json --period-end 2026-06-30

  --manual-input JSON shape (per ticker, same fields the smoke-tested
  parse_bse_xbrl_fundamentals() call already accepts):
    {
      "RELIANCE": {"roic": "12.4", "fcf": "45000", "eps_growth": "NA",
                    "peg": "1.8", "dividend": "8.0", "debt_equity": "0.35",
                    "book_value": "1120.5", "period_end": "2026-06-30"}
    }

No live write path is exercised by this dispatch — see --dry-run requirement in
__main__ below. A future authorized run would drop --dry-run to actually INSERT.
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, timedelta

# Ensure alphaveda/ is on the path when run from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"), override=False)
except ImportError:
    pass  # dotenv not installed — env vars must be set in shell

_REQUEST_DELAY_SECONDS = 0.5  # be polite to BSE's API; avoid rate-limit/IP-block risk
_BSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AlphaVeda/1.0; +research-only)",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.bseindia.com/corporates/ann.html",
    "Origin": "https://www.bseindia.com",
}
_SCRIP_MASTER_URL = "https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w?Group=&Scrip=&industry=&segment=Equity&status=Active"
_ANNOUNCEMENTS_URL = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"
_RESULT_CATEGORY = "Result"
_ANNOUNCEMENT_LOOKBACK_DAYS = 400  # comfortably covers one quarterly cycle + buffer
_ANNOUNCEMENT_MAX_PAGES = 3

# parse_bse_xbrl_fundamentals() output key -> live fundamentals column.
# Keys with no destination are intentionally absent here (dropped, not silently
# mapped) — see "SECOND GENUINE GAP" in the module docstring.
_FIELD_MAP = {
    "roic": "roic_pct",
    "fcf": "fcf_cr",
    "debt_equity": "debt_equity",
    "source": "source",
}
_DROPPED_FIELDS = ("eps_growth", "peg", "dividend", "book_value")


def _http_get_json(url: str) -> object:
    req = urllib.request.Request(url, headers=_BSE_HEADERS)
    # macOS Python's bundled SSL roots often miss intermediate CAs used by BSE's
    # CDN — same issue and same fix as download_bhavcopy_nse() in bhavcopy.py.
    try:
        import certifi
        ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ssl_ctx = None  # fall back to system roots
    with urllib.request.urlopen(req, timeout=20, context=ssl_ctx) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def _fetch_scrip_master() -> list[dict]:
    """Bulk BSE scrip master — one call, ~4,900 rows. The one genuinely bulk/
    archive-shaped resource in this pipeline. Not unit-tested (network dependency),
    same convention as download_bhavcopy_nse()."""
    return _http_get_json(_SCRIP_MASTER_URL)


def _build_isin_to_scripcode(scrip_rows: list[dict]) -> dict[str, str]:
    return {
        row["ISIN_NUMBER"]: row["SCRIP_CD"]
        for row in scrip_rows
        if row.get("ISIN_NUMBER") and row.get("SCRIP_CD")
    }


def _find_latest_result_filing(scrip_code: str, end_date: date) -> dict | None:
    """Query BSE's per-scrip announcement feed and return the most recent row whose
    CATEGORYNAME == 'Result' (BSE's own label for financial-results filings),
    walking back up to _ANNOUNCEMENT_MAX_PAGES pages if needed. Returns None if no
    Result-category filing appears in the lookback window — a real, reportable
    outcome (not an error), same fail-open spirit as ingest.py's per-instrument
    emit_signal try/except.
    """
    from_date = (end_date - timedelta(days=_ANNOUNCEMENT_LOOKBACK_DAYS)).strftime("%Y%m%d")
    to_date = end_date.strftime("%Y%m%d")
    for page in range(1, _ANNOUNCEMENT_MAX_PAGES + 1):
        params = {
            "pageno": page,
            "strCat": "-1",
            "strPrevDate": from_date,
            "strScrip": scrip_code,
            "strSearch": "P",
            "strToDate": to_date,
            "strType": "C",
            "subcategory": "-1",
        }
        url = f"{_ANNOUNCEMENTS_URL}?{urllib.parse.urlencode(params)}"
        try:
            data = _http_get_json(url)
        except Exception as exc:
            print(f"[WARN] BSE announcement fetch failed for scrip={scrip_code} page={page}: {exc}", flush=True)
            return None
        rows = data.get("Table", []) if isinstance(data, dict) else []
        if not rows:
            break
        for row in rows:
            if row.get("CATEGORYNAME") == _RESULT_CATEGORY:
                return {
                    "news_id": row.get("NEWSID"),
                    "news_dt": row.get("NEWS_DT"),
                    "subcategory": row.get("SUBCATNAME"),
                    "headline": row.get("HEADLINE"),
                    "attachment_name": row.get("ATTACHMENTNAME"),
                    "xml_name": row.get("XML_NAME"),
                }
        if len(rows) < 50:  # short page — no more results to page through
            break
        time.sleep(_REQUEST_DELAY_SECONDS)
    return None


def _map_parsed_to_fundamentals_row(parsed: dict, instrument_id: int, period_end: str) -> tuple[dict, list[str]]:
    """Map parse_bse_xbrl_fundamentals() output onto live fundamentals columns.
    Returns (row_dict, dropped_field_names_present_in_input).
    """
    row: dict = {
        "instrument_id": instrument_id,
        "period_end": period_end,
        # ingested_at omitted — DB DEFAULT now() handles it, matches ingest.py convention
    }
    for src_key, dest_col in _FIELD_MAP.items():
        row[dest_col] = parsed.get(src_key)
    dropped_present = [f for f in _DROPPED_FIELDS if parsed.get(f) is not None]
    return row, dropped_present


def run_ingest_fundamentals(
    tickers: list[str] | None = None,
    manual_input: dict[str, dict] | None = None,
    default_period_end: str | None = None,
    dry_run: bool = True,
) -> dict:
    """For each active instrument (optionally filtered to `tickers`), resolve its
    BSE scrip code, locate its latest Result-category filing (real network calls),
    and — for tickers present in `manual_input` — run the supplied XBRL fields
    through parse_bse_xbrl_fundamentals() and build the fundamentals row that would
    be written. dry_run=True (default) never writes; prints/returns intended rows.
    """
    from src.config import get_supabase_client
    from src.ingest.fundamentals import parse_bse_xbrl_fundamentals

    supabase = get_supabase_client()
    manual_input = manual_input or {}

    inst_query = supabase.table("instruments").select("id, ticker, isin").eq("is_active", True)
    if tickers:
        inst_query = inst_query.in_("ticker", tickers)
    instruments = inst_query.execute().data or []

    scrip_rows = _fetch_scrip_master()
    isin_to_scrip = _build_isin_to_scripcode(scrip_rows)

    summary: dict = {
        "requested": len(instruments),
        "scrip_resolved": 0,
        "filing_found": 0,
        "rows_built": 0,
        "rows_written": 0,
        "results": [],
        "status": "DRY_RUN" if dry_run else "OK",
    }

    today = date.today()
    for i, inst in enumerate(instruments):
        if i > 0:
            time.sleep(_REQUEST_DELAY_SECONDS)
        ticker = inst["ticker"]
        isin = inst.get("isin")
        entry: dict = {"ticker": ticker, "instrument_id": inst["id"]}

        scrip_code = isin_to_scrip.get((isin or "").strip()) if isin else None
        if not scrip_code:
            entry["status"] = "NO_SCRIP_CODE_MATCH"
            summary["results"].append(entry)
            print(f"[WARN] {ticker}: no BSE scrip code match for ISIN={isin!r}", flush=True)
            continue
        summary["scrip_resolved"] += 1
        entry["bse_scrip_code"] = scrip_code

        filing = _find_latest_result_filing(scrip_code, today)
        if filing is None:
            entry["status"] = "NO_RESULT_FILING_FOUND"
            summary["results"].append(entry)
            print(f"[INFO] {ticker} ({scrip_code}): no Result-category filing in last "
                  f"{_ANNOUNCEMENT_LOOKBACK_DAYS}d", flush=True)
            continue
        summary["filing_found"] += 1
        entry["latest_filing"] = filing
        print(f"[INFO] {ticker} ({scrip_code}): latest Result filing "
              f"{filing['news_dt']} — {filing['headline']!r}", flush=True)

        xbrl_data = manual_input.get(ticker)
        if xbrl_data is None:
            entry["status"] = "FOUND_NO_EXTRACTOR"  # filing located; no XBRL->dict path exists
            summary["results"].append(entry)
            continue

        period_end = xbrl_data.get("period_end") or default_period_end
        if not period_end:
            entry["status"] = "MISSING_PERIOD_END"
            summary["results"].append(entry)
            print(f"[WARN] {ticker}: manual input present but no period_end supplied "
                  f"(fundamentals.period_end is NOT NULL) — skipping row build", flush=True)
            continue

        parsed = parse_bse_xbrl_fundamentals(xbrl_data)
        row, dropped = _map_parsed_to_fundamentals_row(parsed, inst["id"], period_end)
        entry["status"] = "ROW_BUILT"
        entry["parsed"] = parsed
        entry["fundamentals_row"] = row
        entry["dropped_fields"] = dropped
        summary["rows_built"] += 1

        if dry_run:
            print(f"[DRY_RUN] {ticker}: would write {row}", flush=True)
            if dropped:
                print(f"[DRY_RUN] {ticker}: dropped fields (no destination column): {dropped}", flush=True)
        else:
            existing = (
                supabase.table("fundamentals")
                .select("id")
                .eq("instrument_id", inst["id"])
                .eq("period_end", period_end)
                .limit(1)
                .execute()
            )
            if existing.data:
                entry["status"] = "SKIPPED_ALREADY_PRESENT"
            else:
                supabase.table("fundamentals").insert(row).execute()
                summary["rows_written"] += 1
                entry["status"] = "WRITTEN"

        summary["results"].append(entry)

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tickers", type=str, default=None,
                         help="comma-separated tickers to limit scope, e.g. RELIANCE,TCS,INFY")
    parser.add_argument("--manual-input", type=str, default=None,
                         help="path to JSON file: {ticker: {xbrl fields incl. optional period_end}}")
    parser.add_argument("--period-end", type=str, default=None,
                         help="YYYY-MM-DD default period_end for entries lacking their own")
    parser.add_argument("--dry-run", action="store_true",
                         help="print intended fundamentals rows without writing (required — see module docstring: live write is out of scope for this dispatch)")
    args = parser.parse_args()

    if not args.dry_run:
        print("[ERROR] Live writes to `fundamentals` are out of scope for this script's "
              "current authorization. Re-run with --dry-run.", flush=True)
        sys.exit(2)

    tickers_arg = [t.strip() for t in args.tickers.split(",")] if args.tickers else None
    manual_data: dict[str, dict] = {}
    if args.manual_input:
        with open(args.manual_input) as f:
            manual_data = json.load(f)

    result = run_ingest_fundamentals(
        tickers=tickers_arg,
        manual_input=manual_data,
        default_period_end=args.period_end,
        dry_run=True,
    )
    print(json.dumps(result, indent=2, default=str))
    sys.exit(0)
