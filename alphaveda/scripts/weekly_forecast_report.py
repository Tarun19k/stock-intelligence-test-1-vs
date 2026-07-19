#!/usr/bin/env python3
"""Generate the weekly forecast-versus-outcome Markdown report."""
from __future__ import annotations

import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

# Ensure alphaveda/ is importable when this file is run directly.
ALPHAVEDA_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ALPHAVEDA_ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ALPHAVEDA_ROOT.parent / ".env", override=False)
except ImportError:
    pass

from src.config import get_supabase_client


PAGE_SIZE = 1_000
REPORTS_DIR = ALPHAVEDA_ROOT / "docs" / "reports"


def _trading_days_ending_on(report_date: date, count: int = 5) -> list[date]:
    """Return the last ``count`` NSE trading days through ``report_date``."""
    try:
        import pandas_market_calendars as mcal

        calendar = mcal.get_calendar("NSE")
        start_date = report_date - timedelta(days=max(14, count * 3))
        schedule = calendar.schedule(
            start_date=start_date.isoformat(),
            end_date=report_date.isoformat(),
        )
        trading_days = [timestamp.date() for timestamp in schedule.index]
        if len(trading_days) >= count:
            return trading_days[-count:]
    except Exception as exc:
        # The project supports a weekday fallback when the exchange calendar is
        # unavailable, matching the ingest trading-day guard.
        print(
            f"WARN: NSE calendar unavailable, using weekday fallback: {exc}",
            file=sys.stderr,
        )

    trading_days: list[date] = []
    candidate = report_date
    while len(trading_days) < count:
        if candidate.weekday() < 5:
            trading_days.append(candidate)
        candidate -= timedelta(days=1)
    return list(reversed(trading_days))


def _fetch_all(query_factory: Callable[[], Any]) -> list[dict[str, Any]]:
    """Execute a Supabase query in pages without relying on its row cap."""
    rows: list[dict[str, Any]] = []
    start = 0
    while True:
        page = query_factory().range(start, start + PAGE_SIZE - 1).execute().data or []
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            return rows
        start += PAGE_SIZE


def fetch_report_rows(supabase: Any, report_date: date) -> list[dict[str, Any]]:
    """Fetch and join resolved outcomes from the trailing five trading days."""
    trading_days = _trading_days_ending_on(report_date)
    window_start = datetime.combine(trading_days[0], datetime.min.time(), timezone.utc)
    window_end = datetime.combine(report_date + timedelta(days=1), datetime.min.time(), timezone.utc)

    # Keep these selects and the client-side joins aligned with
    # web/app/accuracy/page.tsx.
    outcomes = _fetch_all(
        lambda: (
            supabase.table("accuracy_outcomes")
            .select("id,prediction_id,resolved_at,hit,return_pct")
            .gte("resolved_at", window_start.isoformat())
            .lt("resolved_at", window_end.isoformat())
            .order("resolved_at", desc=True)
        )
    )
    predictions = _fetch_all(
        lambda: supabase.table("accuracy_predictions").select(
            "id,instrument_id,direction,confidence,emitted_at"
        )
    )
    instruments = _fetch_all(
        lambda: supabase.table("instruments").select("id,ticker")
    )

    prediction_by_id = {prediction["id"]: prediction for prediction in predictions}
    ticker_by_id = {instrument["id"]: instrument["ticker"] for instrument in instruments}

    rows: list[dict[str, Any]] = []
    for outcome in outcomes:
        prediction = prediction_by_id.get(outcome["prediction_id"])
        rows.append(
            {
                "ticker": ticker_by_id.get(prediction["instrument_id"], "—") if prediction else "—",
                "direction": prediction["direction"] if prediction else "—",
                "confidence": prediction["confidence"] if prediction else None,
                "outcome": "hit" if outcome["hit"] else "miss",
                "return_pct": outcome["return_pct"],
            }
        )
    return rows


def _markdown_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(rows: list[dict[str, Any]]) -> str:
    """Render report rows as a plain Markdown table."""
    lines = [
        "| ticker | predicted direction | confidence | actual outcome | return_pct |",
        "|---|---|---:|---|---:|",
    ]
    for row in rows:
        confidence = "—" if row["confidence"] is None else f'{float(row["confidence"]):.2f}%'
        return_pct = f'{float(row["return_pct"]):+.2f}%'
        lines.append(
            "| "
            + " | ".join(
                _markdown_cell(value)
                for value in (
                    row["ticker"],
                    row["direction"],
                    confidence,
                    row["outcome"],
                    return_pct,
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Past performance is not indicative of future results. "
            "Educational/research output only - not investment advice.",
        ]
    )
    return "\n".join(lines) + "\n"


def generate_report(report_date: date | None = None) -> Path:
    """Query Supabase and write the dated weekly report."""
    report_date = report_date or datetime.now(timezone.utc).date()
    rows = fetch_report_rows(get_supabase_client(), report_date)
    if not rows:
        print(
            "ERROR: 0 accuracy_outcomes rows in the trailing window - check whether "
            "resolve_outcomes.py's cron ran this week.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"weekly-{report_date.isoformat()}.md"
    report_path.write_text(render_markdown(rows), encoding="utf-8")
    return report_path


if __name__ == "__main__":
    path = generate_report()
    print(path.relative_to(ALPHAVEDA_ROOT.parent))
