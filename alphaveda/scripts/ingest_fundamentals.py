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
SECOND GENUINE GAP (CLOSED 2026-07-27) — parse_bse_xbrl_fundamentals() output vs. the
live `fundamentals` table schema (confirmed live via Supabase MCP list_tables against
project kowlkczswaglbmabygtl, 2026-07-24; table currently has 0 rows):

  fundamentals columns: id, instrument_id, period_end (DATE, NOT NULL), roic_pct,
  fcf_cr, promoter_pledge_pct, debt_equity, eps, revenue_cr, source, ingested_at.

  parse_bse_xbrl_fundamentals() output keys (as of 2026-07-27): symbol, source, roic,
  fcf, eps_growth, peg, dividend, debt_equity, book_value, promoter_pledge_pct, eps,
  revenue_cr.

  Overlap:
    roic                 -> roic_pct              (mapped; units NOT verified equal — see below)
    fcf                  -> fcf_cr                 (mapped; units NOT verified equal — see below)
    debt_equity           -> debt_equity            (direct match)
    source                -> source                 (direct match)
    promoter_pledge_pct   -> promoter_pledge_pct    (direct match, added 2026-07-27)
    eps                   -> eps                    (direct match, added 2026-07-27)
    revenue_cr            -> revenue_cr             (direct match, added 2026-07-27)
  No destination column exists for: eps_growth, peg, dividend, book_value — these
  are DROPPED (never written) and reported explicitly per-row in dry-run output,
  not silently discarded.
  No source field exists for: period_end — it MUST be supplied externally
  (--period-end or a "period_end" key in the --manual-input JSON; the DB column is
  NOT NULL, so a row cannot be built without it).
  Why promoter_pledge_pct/eps/revenue_cr were added directly to
  parse_bse_xbrl_fundamentals() (src/ingest/fundamentals.py) rather than special-cased
  in this script: unlike roic/peg/eps_growth (derived ratios needing a not-yet-built
  tag-to-ratio extractor — see FIRST GENUINE GAP above), these three are primitive
  XBRL facts (eps, revenue) or a primitive shareholding-XBRL fact
  (promoter_pledge_pct) that need no derivation, only the same float-cast every other
  field already gets in _safe_float(). They are now accepted as ordinary
  --manual-input keys alongside the existing seven (see Usage below).
  Unit mismatch risk (NOT resolved here — flagged for whoever wires a real XBRL
  extractor): fcf_cr's "_cr" suffix strongly implies crores; parse_bse_xbrl_fundamentals
  applies no unit conversion, it only casts to float. A real extractor must produce
  fcf already in crores before this script's mapping step, or figures will be wrong
  by orders of magnitude. Same caution applies to roic_pct (percentage vs. fraction)
  and revenue_cr (crores, per the "_cr" suffix).

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
  parse_bse_xbrl_fundamentals() call already accepts — extended 2026-07-27 with
  promoter_pledge_pct/eps/revenue_cr, see SECOND GENUINE GAP above):
    {
      "RELIANCE": {"roic": "12.4", "fcf": "45000", "eps_growth": "NA",
                    "peg": "1.8", "dividend": "8.0", "debt_equity": "0.35",
                    "book_value": "1120.5", "promoter_pledge_pct": "0.0",
                    "eps": "118.2", "revenue_cr": "231784.0",
                    "period_end": "2026-06-30"}
    }

Dry-run is the DEFAULT (no flag needed) — it always was, and still is, no matter
which other flags are passed. Live writes are opt-in only: pass BOTH --live-write
AND --i-understand-this-writes-live-data together (see __main__ below). Neither
flag alone enables a write; this dispatch does not pass either, so no live write
occurs here.
"""
from __future__ import annotations

import argparse
import json
import os
import random
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
_MIN_SCRIP_MASTER_ROWS = 1_000
_FETCH_FOUND = "FOUND"
_FETCH_NOT_FOUND = "NOT_FOUND"
_FETCH_THROTTLED = "THROTTLED"
_FETCH_ERROR = "FETCH_ERROR"

# parse_bse_xbrl_fundamentals() output key -> live fundamentals column.
# Keys with no destination are intentionally absent here (dropped, not silently
# mapped) — see "SECOND GENUINE GAP" in the module docstring.
# promoter_pledge_pct/eps/revenue_cr added 2026-07-27: primitive XBRL/shareholding
# facts, not derived ratios, so they map 1:1 straight from manual input.
_FIELD_MAP = {
    "roic": "roic_pct",
    "fcf": "fcf_cr",
    "debt_equity": "debt_equity",
    "source": "source",
    "promoter_pledge_pct": "promoter_pledge_pct",
    "eps": "eps",
    "revenue_cr": "revenue_cr",
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


def _fetch_scrip_master() -> object:
    """Bulk BSE scrip master — one call, ~4,900 rows. The one genuinely bulk/
    archive-shaped resource in this pipeline. Not unit-tested (network dependency),
    same convention as download_bhavcopy_nse()."""
    return _http_get_json(_SCRIP_MASTER_URL)


def _validate_scrip_master(rows: object) -> list[dict]:
    """Reject throttled/malformed/truncated preflight data before the batch starts."""
    if not isinstance(rows, list):
        raise RuntimeError("BSE scrip-master preflight failed: response is not a list")
    if _is_throttle_sentinel(rows):
        raise RuntimeError("BSE scrip-master preflight failed: throttle sentinel received")
    if len(rows) < _MIN_SCRIP_MASTER_ROWS:
        raise RuntimeError(
            f"BSE scrip-master preflight failed: received only {len(rows)} rows; "
            f"expected at least {_MIN_SCRIP_MASTER_ROWS}"
        )
    return rows


def _build_isin_to_scripcode(scrip_rows: list[dict]) -> dict[str, str]:
    return {
        row["ISIN_NUMBER"]: row["SCRIP_CD"]
        for row in scrip_rows
        if row.get("ISIN_NUMBER") and row.get("SCRIP_CD")
    }


def _is_throttle_sentinel(rows: object) -> bool:
    """BSE's announcement API intermittently returns {"Table":[{"Column1":1}]}
    instead of real rows — confirmed live 2026-07-29: identical request, same
    params/headers/cookies, alternates between this sentinel and real data across
    repeated calls seconds apart. Not a real "zero results" response (a genuine
    empty result is {"Table":[]}), not a header/UA/param issue (ruled out by direct
    probe), not fixable by cookie priming. Distinguishable by shape: Column1 is
    present while no row carries NEWSID/CATEGORYNAME announcement fields.
    Treated as a transient throttle to retry, not a real "no filing" outcome."""
    if not isinstance(rows, list) or not rows or not all(isinstance(row, dict) for row in rows):
        return False
    has_real_announcement_fields = any(
        row.get("NEWSID") is not None or row.get("CATEGORYNAME") is not None
        for row in rows
    )
    return not has_real_announcement_fields and any("Column1" in row for row in rows)


_THROTTLE_RETRY_DELAYS = (2, 4, 8)  # seconds; one shared retry budget per ticker


def _jittered_delay(delay: float) -> float:
    return delay * random.uniform(0.75, 1.25)


def _find_latest_result_filing(scrip_code: str, end_date: date) -> tuple[str, dict | None]:
    """Query BSE's per-scrip announcement feed and return the most recent row whose
    CATEGORYNAME == 'Result' (BSE's own label for financial-results filings),
    walking back up to _ANNOUNCEMENT_MAX_PAGES pages if needed. The outcome keeps a
    genuine no-filing result distinct from persistent throttling and fetch errors.
    """
    from_date = (end_date - timedelta(days=_ANNOUNCEMENT_LOOKBACK_DAYS)).strftime("%Y%m%d")
    to_date = end_date.strftime("%Y%m%d")
    retries_used = 0
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
            rows = data.get("Table", []) if isinstance(data, dict) else []
            while _is_throttle_sentinel(rows) and retries_used < len(_THROTTLE_RETRY_DELAYS):
                delay = _jittered_delay(_THROTTLE_RETRY_DELAYS[retries_used])
                retries_used += 1
                print(f"[WARN] BSE throttle sentinel for scrip={scrip_code} page={page} "
                      f"— retrying in {delay:.1f}s ({retries_used}/"
                      f"{len(_THROTTLE_RETRY_DELAYS)} ticker retries)", flush=True)
                time.sleep(delay)
                data = _http_get_json(url)
                rows = data.get("Table", []) if isinstance(data, dict) else []
            if _is_throttle_sentinel(rows):
                print(f"[WARN] BSE throttle sentinel persisted for scrip={scrip_code} page={page} "
                      f"after {len(_THROTTLE_RETRY_DELAYS)} retries — giving up this run", flush=True)
                return _FETCH_THROTTLED, None
        except Exception as exc:
            print(f"[WARN] BSE announcement fetch failed for scrip={scrip_code} page={page}: {exc}", flush=True)
            return _FETCH_ERROR, None
        if not rows:
            break
        for row in rows:
            if row.get("CATEGORYNAME") == _RESULT_CATEGORY:
                return _FETCH_FOUND, {
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
    return _FETCH_NOT_FOUND, None


class ThrottleBreaker:
    COOLDOWN_TIERS = (120, 300, 600)
    N_TRIGGER = 2
    MAX_TRIPS = 3
    REQUEST_DELAYS = (1.5, 3.0)

    def __init__(self, checkpoint_callback, no_cooldown: bool = False) -> None:
        self.consecutive_throttled = 0
        self.trips = 0
        self.request_delay = _REQUEST_DELAY_SECONDS
        self.aborted = False
        self._checkpoint_callback = checkpoint_callback
        self._no_cooldown = no_cooldown

    def note_non_throttled(self) -> None:
        self.consecutive_throttled = 0

    def cooldown_and_probe(self, scrip_code: str, end_date: date) -> bool:
        """Cool down by escalating tiers until a one-page probe is not throttled."""
        if self._no_cooldown:
            print("[WARN] Systemic throttle detected; --no-cooldown is set, aborting", flush=True)
            return False
        while self.trips < self.MAX_TRIPS:
            delay = self.COOLDOWN_TIERS[min(self.trips, len(self.COOLDOWN_TIERS) - 1)]
            self.trips += 1
            print(f"[WARN] Systemic BSE throttle: cooldown tier {self.trips}/"
                  f"{self.MAX_TRIPS} for {delay}s", flush=True)
            self._checkpoint_callback()
            remaining = delay
            while remaining > 0:
                if remaining == delay or remaining % 30 == 0:
                    print(f"[INFO] BSE throttle cooldown: {remaining}s remaining", flush=True)
                sleep_for = min(5, remaining)
                time.sleep(sleep_for)
                remaining -= sleep_for
            probe_outcome = _probe_announcement_page(scrip_code, end_date)
            if probe_outcome == _FETCH_THROTTLED:
                print("[WARN] BSE throttle probe still returned sentinel; escalating", flush=True)
                continue
            if probe_outcome == _FETCH_ERROR:
                print("[WARN] BSE throttle probe failed; escalating cooldown tier", flush=True)
                continue
            self.request_delay = self.REQUEST_DELAYS[min(self.trips - 1, len(self.REQUEST_DELAYS) - 1)]
            self.consecutive_throttled = 0
            print(f"[INFO] BSE throttle probe recovered; inter-ticker delay is now "
                  f"{self.request_delay:.1f}s", flush=True)
            return True
        return False


def _probe_announcement_page(scrip_code: str, end_date: date) -> str:
    """Make one cheap page-one request used only by the batch circuit breaker."""
    params = {
        "pageno": 1,
        "strCat": "-1",
        "strPrevDate": (end_date - timedelta(days=_ANNOUNCEMENT_LOOKBACK_DAYS)).strftime("%Y%m%d"),
        "strScrip": scrip_code,
        "strSearch": "P",
        "strToDate": end_date.strftime("%Y%m%d"),
        "strType": "C",
        "subcategory": "-1",
    }
    try:
        data = _http_get_json(f"{_ANNOUNCEMENTS_URL}?{urllib.parse.urlencode(params)}")
        rows = data.get("Table", []) if isinstance(data, dict) else []
        return _FETCH_THROTTLED if _is_throttle_sentinel(rows) else _FETCH_FOUND
    except Exception as exc:
        print(f"[WARN] BSE throttle probe failed for scrip={scrip_code}: {exc}", flush=True)
        return _FETCH_ERROR


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
    no_cooldown: bool = False,
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

    try:
        scrip_rows = _validate_scrip_master(_fetch_scrip_master())
    except Exception as exc:
        raise RuntimeError(f"Cannot start fundamentals ingest. {exc}") from exc
    isin_to_scrip = _build_isin_to_scripcode(scrip_rows)

    summary: dict = {
        "requested": len(instruments),
        "scrip_resolved": 0,
        "filing_found": 0,
        "no_result_filing_found": 0,
        "throttled": 0,
        "fetch_errors": 0,
        "skipped_systemic_throttle": 0,
        "rows_built": 0,
        "rows_written": 0,
        "results": [],
        "status": "DRY_RUN" if dry_run else "OK",
    }

    checkpoint_path = os.path.join(os.getcwd(), "ingest_fundamentals_checkpoint.json")

    def checkpoint() -> None:
        checkpoint_data = dict(summary)
        checkpoint_data["status"] = "PARTIAL_THROTTLED"
        temp_path = f"{checkpoint_path}.tmp"
        with open(temp_path, "w") as checkpoint_file:
            json.dump(checkpoint_data, checkpoint_file, indent=2, default=str)
        os.replace(temp_path, checkpoint_path)
        print(f"[INFO] Partial ingest checkpoint written to {checkpoint_path}", flush=True)

    breaker = ThrottleBreaker(checkpoint, no_cooldown=no_cooldown)
    attempts: dict[str, int] = {}

    def print_resume_command() -> None:
        resume_tickers = [
            entry["ticker"] for entry in summary["results"]
            if entry.get("status") in {"THROTTLED", "SKIPPED_SYSTEMIC_THROTTLE"}
        ]
        if resume_tickers:
            print("[RESUME] python3 alphaveda/scripts/ingest_fundamentals.py --dry-run "
                  f"--tickers {','.join(resume_tickers)}", flush=True)

    today = date.today()
    index = 0
    try:
      while index < len(instruments):
        inst = instruments[index]
        ticker = inst["ticker"]
        isin = inst.get("isin")
        entry: dict = {"ticker": ticker, "instrument_id": inst["id"]}

        if breaker.aborted:
            entry["status"] = "SKIPPED_SYSTEMIC_THROTTLE"
            summary["skipped_systemic_throttle"] += 1
            summary["results"].append(entry)
            index += 1
            continue

        scrip_code = isin_to_scrip.get((isin or "").strip()) if isin else None
        if not scrip_code:
            entry["status"] = "NO_SCRIP_CODE_MATCH"
            summary["results"].append(entry)
            print(f"[WARN] {ticker}: no BSE scrip code match for ISIN={isin!r}", flush=True)
            index += 1
            continue
        if attempts.get(ticker, 0) == 0:
            summary["scrip_resolved"] += 1
        entry["bse_scrip_code"] = scrip_code

        if index > 0 or attempts.get(ticker, 0) > 0:
            time.sleep(breaker.request_delay)
        attempts[ticker] = attempts.get(ticker, 0) + 1
        outcome, filing = _find_latest_result_filing(scrip_code, today)
        if outcome == _FETCH_THROTTLED:
            breaker.consecutive_throttled += 1
            entry["status"] = "THROTTLED"
            if breaker.consecutive_throttled >= breaker.N_TRIGGER:
                recovered = breaker.cooldown_and_probe(scrip_code, today)
                if recovered and attempts[ticker] < 2:
                    print(f"[INFO] {ticker}: re-queued after successful throttle probe", flush=True)
                    continue
                if not recovered:
                    breaker.aborted = True
            summary["throttled"] += 1
            summary["results"].append(entry)
            index += 1
            continue
        breaker.note_non_throttled()
        if outcome == _FETCH_ERROR:
            entry["status"] = "FETCH_ERROR"
            summary["fetch_errors"] += 1
            summary["results"].append(entry)
            index += 1
            continue
        if outcome == _FETCH_NOT_FOUND:
            entry["status"] = "NO_RESULT_FILING_FOUND"
            summary["no_result_filing_found"] += 1
            summary["results"].append(entry)
            print(f"[INFO] {ticker} ({scrip_code}): no Result-category filing in last "
                  f"{_ANNOUNCEMENT_LOOKBACK_DAYS}d", flush=True)
            index += 1
            continue
        assert outcome == _FETCH_FOUND and filing is not None
        summary["filing_found"] += 1
        entry["latest_filing"] = filing
        print(f"[INFO] {ticker} ({scrip_code}): latest Result filing "
              f"{filing['news_dt']} — {filing['headline']!r}", flush=True)

        xbrl_data = manual_input.get(ticker)
        if xbrl_data is None:
            entry["status"] = "FOUND_NO_EXTRACTOR"  # filing located; no XBRL->dict path exists
            summary["results"].append(entry)
            index += 1
            continue

        period_end = xbrl_data.get("period_end") or default_period_end
        if not period_end:
            entry["status"] = "MISSING_PERIOD_END"
            summary["results"].append(entry)
            print(f"[WARN] {ticker}: manual input present but no period_end supplied "
                  f"(fundamentals.period_end is NOT NULL) — skipping row build", flush=True)
            index += 1
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
        index += 1
    except KeyboardInterrupt:
        print("[WARN] Fundamentals ingest interrupted; partial results preserved", flush=True)
        breaker.aborted = True
        for inst in instruments[index:]:
            if not any(item["ticker"] == inst["ticker"] for item in summary["results"]):
                summary["results"].append({
                    "ticker": inst["ticker"],
                    "instrument_id": inst["id"],
                    "status": "SKIPPED_SYSTEMIC_THROTTLE",
                })
                summary["skipped_systemic_throttle"] += 1

    degraded = any(
        entry.get("status") in {"THROTTLED", "SKIPPED_SYSTEMIC_THROTTLE"}
        for entry in summary["results"]
    )
    if degraded:
        summary["status"] = "PARTIAL_THROTTLED"
        print_resume_command()

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
                         help="print intended fundamentals rows without writing (this is the "
                              "default behaviour with or without this flag — kept for explicit "
                              "clarity in scripts/CI invocations)")
    parser.add_argument("--no-cooldown", action="store_true",
                         help="fail fast on systemic throttling instead of waiting through cooldowns")
    parser.add_argument("--live-write", action="store_true",
                         help="opt in to actually INSERTing rows into `fundamentals`. Has no "
                              "effect unless --i-understand-this-writes-live-data is ALSO passed "
                              "(two-flag gate, same explicit-confirmation spirit as the External "
                              "State Write Gate in CLAUDE.md — this table has no UNIQUE "
                              "constraint on (instrument_id, period_end), see THIRD GENUINE GAP "
                              "above, so idempotency here is application-level only)")
    parser.add_argument("--i-understand-this-writes-live-data", action="store_true",
                         dest="i_understand_this_writes_live_data",
                         help="required alongside --live-write to confirm intent; passing this "
                              "alone (without --live-write) does nothing")
    args = parser.parse_args()

    if args.live_write and not args.i_understand_this_writes_live_data:
        print("[ERROR] --live-write requires --i-understand-this-writes-live-data as well "
              "(two-flag confirmation gate — see --help). Re-run with both, or omit both to "
              "stay in dry-run.", flush=True)
        sys.exit(2)

    live_confirmed = args.live_write and args.i_understand_this_writes_live_data
    dry_run = not live_confirmed  # default True; only False when BOTH flags above are passed

    if live_confirmed:
        print("[WARN] LIVE WRITE MODE — rows will be INSERTed into `fundamentals` "
              "(kowlkczswaglbmabygtl). No UNIQUE constraint backs the idempotency check; "
              "see THIRD GENUINE GAP in module docstring.", flush=True)

    tickers_arg = [t.strip() for t in args.tickers.split(",")] if args.tickers else None
    manual_data: dict[str, dict] = {}
    if args.manual_input:
        with open(args.manual_input) as f:
            manual_data = json.load(f)

    try:
        result = run_ingest_fundamentals(
            tickers=tickers_arg,
            manual_input=manual_data,
            default_period_end=args.period_end,
            dry_run=dry_run,
            no_cooldown=args.no_cooldown,
        )
    except Exception as exc:
        print(f"[ERROR] {exc}", flush=True)
        sys.exit(1)
    print(json.dumps(result, indent=2, default=str))
    sys.exit(1 if result["status"] == "PARTIAL_THROTTLED" else 0)
