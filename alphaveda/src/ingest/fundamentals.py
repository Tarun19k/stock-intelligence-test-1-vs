"""BSE XBRL fundamentals loader.

parse_bse_xbrl_fundamentals() is a pure transformation function.
All numeric fields are normalised to float; missing/invalid values become None.
"""
from __future__ import annotations

_NUMERIC_FIELDS = (
    "roic", "fcf", "eps_growth", "peg", "dividend", "debt_equity", "book_value",
    # promoter_pledge_pct/eps/revenue_cr added 2026-07-27 (ingest_fundamentals.py GAP 1
    # fix): unlike roic/peg/eps_growth these are primitive XBRL facts, not derived
    # ratios that need separate extraction engineering — they need only float parsing,
    # so they belong here as ordinary pass-through numeric fields.
    "promoter_pledge_pct", "eps", "revenue_cr",
    # roe added 2026-07-29 (migration 0019): sector-appropriate profitability metric
    # for financial-sector tickers (roic/debt_equity are NULL-by-design for banks —
    # see sector_class below, not a data gap).
    "roe",
)
_TEXT_FIELDS = ("sector_class",)  # 'industrial' | 'financial'; passthrough, no float cast
_NULL_SENTINELS = frozenset({"NA", "N/A", "", "NULL", "null", "None"})


def _safe_float(val: object) -> float | None:
    if val is None:
        return None
    if isinstance(val, str) and val.strip() in _NULL_SENTINELS:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def parse_bse_xbrl_fundamentals(xbrl_data: dict) -> dict:
    """Parse a BSE XBRL fundamentals response dict into a normalised flat dict.

    Required output keys: symbol, roic, fcf, eps_growth, peg, dividend,
    debt_equity, book_value, promoter_pledge_pct, eps, revenue_cr, source.
    """
    result: dict = {
        "symbol": xbrl_data.get("symbol", ""),
        "source": xbrl_data.get("source", "bse_xbrl"),
    }
    for field in _NUMERIC_FIELDS:
        result[field] = _safe_float(xbrl_data.get(field))
    for field in _TEXT_FIELDS:
        val = xbrl_data.get(field)
        result[field] = val if val not in (None, "") else None
    return result
