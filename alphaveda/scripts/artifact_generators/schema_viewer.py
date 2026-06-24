"""
schema_viewer.py — Generate schema-viewer.html artifact.

Reads: docs/supabase/SCHEMA.md (595-line reference).
Renders 11 tables as cards: instruments, ohlcv, fundamentals, macro_regime,
portfolio_buckets, trade_outcomes, accuracy_predictions, accuracy_outcomes,
signal_weights, ingest_status, waitlist.

CSP-compliant HTML — all CSS/JS inline, no external requests.
"""

import re
import warnings
from datetime import datetime
from pathlib import Path
from typing import Optional

BRAND = {
    "indigo": "#1A1F3C",
    "ivory": "#F5F3EC",
    "gold": "#E8A020",
    "teal": "#2D7A72",
    "green": "#4A8C5C",
    "terra": "#C0503A",
}

_HERE = Path(__file__).resolve()
ALPHAVEDA_ROOT = _HERE.parent.parent.parent

TABLE_ORDER = [
    "instruments",
    "ohlcv",
    "fundamentals",
    "macro_regime",
    "portfolio_buckets",
    "trade_outcomes",
    "accuracy_predictions",
    "accuracy_outcomes",
    "signal_weights",
    "ingest_status",
    "waitlist",
]

# Fallback schema when SCHEMA.md is absent
FALLBACK_SCHEMA: dict[str, dict] = {
    "instruments": {
        "pk": "id (SERIAL)",
        "columns": ["symbol VARCHAR(20)", "name TEXT", "exchange VARCHAR(10)", "classification VARCHAR(30)", "listed BOOLEAN"],
        "not_null": ["symbol", "exchange"],
        "note": "Fallback — SCHEMA.md not found",
    },
    "ohlcv": {
        "pk": "id (BIGSERIAL)",
        "columns": ["instrument_id INT", "as_of DATE", "open NUMERIC", "high NUMERIC", "low NUMERIC", "close NUMERIC", "volume BIGINT", "circuit_flag BOOLEAN", "licence_class VARCHAR(20)", "source VARCHAR(50)", "ingested_at TIMESTAMPTZ"],
        "not_null": ["instrument_id", "as_of", "close", "licence_class"],
        "note": "",
    },
    "fundamentals": {
        "pk": "id (BIGSERIAL)",
        "columns": ["instrument_id INT", "period_end DATE", "roic NUMERIC", "fcf NUMERIC", "pledge_pct NUMERIC", "source VARCHAR(50)", "ingested_at TIMESTAMPTZ"],
        "not_null": ["instrument_id", "period_end"],
        "note": "",
    },
    "macro_regime": {
        "pk": "id (SERIAL)",
        "columns": ["as_of DATE", "regime_tag VARCHAR(30)", "vix NUMERIC", "cycle_phase VARCHAR(20)", "source VARCHAR(50)", "ingested_at TIMESTAMPTZ"],
        "not_null": ["as_of", "regime_tag"],
        "note": "",
    },
    "portfolio_buckets": {
        "pk": "id (SERIAL)",
        "columns": ["name VARCHAR(30)", "description TEXT", "e2_consecutive_threshold INT", "weight_floor NUMERIC"],
        "not_null": ["name"],
        "note": "Seeded with 4 rows at migration time",
    },
    "trade_outcomes": {
        "pk": "id (BIGSERIAL)",
        "columns": ["prediction_id INT", "resolved_at TIMESTAMPTZ", "outcome VARCHAR(20)", "return_pct NUMERIC", "circuit_excluded BOOLEAN"],
        "not_null": ["prediction_id", "outcome"],
        "note": "",
    },
    "accuracy_predictions": {
        "pk": "id (BIGSERIAL)",
        "columns": ["instrument_id INT", "signal_direction VARCHAR(20)", "confidence NUMERIC", "regime_tag VARCHAR(30)", "lynch_class VARCHAR(30)", "magnitude_target NUMERIC", "downside_target NUMERIC", "kelly_fraction NUMERIC", "emitted_at TIMESTAMPTZ"],
        "not_null": ["instrument_id", "signal_direction", "emitted_at"],
        "note": "",
    },
    "accuracy_outcomes": {
        "pk": "id (BIGSERIAL)",
        "columns": ["prediction_id INT", "resolved_at TIMESTAMPTZ", "hit BOOLEAN", "return_pct NUMERIC"],
        "not_null": ["prediction_id"],
        "note": "",
    },
    "signal_weights": {
        "pk": "id (SERIAL)",
        "columns": ["segment VARCHAR(50)", "signal_name VARCHAR(50)", "weight NUMERIC", "status VARCHAR(20)", "proposed_at TIMESTAMPTZ", "approved_at TIMESTAMPTZ"],
        "not_null": ["segment", "signal_name", "weight", "status"],
        "note": "status: ACTIVE | PROPOSED | ARCHIVED. No duplicate ACTIVE per segment.",
    },
    "ingest_status": {
        "pk": "id (SERIAL)",
        "columns": ["source VARCHAR(50)", "last_run TIMESTAMPTZ", "rows_written INT", "status VARCHAR(20)"],
        "not_null": ["source"],
        "note": "",
    },
    "waitlist": {
        "pk": "id (SERIAL)",
        "columns": ["email TEXT", "signed_up_at TIMESTAMPTZ", "converted_at TIMESTAMPTZ", "price_feedback TEXT"],
        "not_null": ["email", "signed_up_at"],
        "note": "converted_at non-null → commercial mode activates",
    },
}


def _parse_schema_md(path: Path) -> dict[str, dict]:
    """
    Parse docs/supabase/SCHEMA.md into a dict keyed by table name.
    Each value: {pk, columns, not_null, note}
    Falls back to FALLBACK_SCHEMA per-table if table not found in file.
    """
    if not path.exists():
        warnings.warn(
            f"SCHEMA.md not found at {path} — using fallback schema definitions",
            RuntimeWarning,
            stacklevel=3,
        )
        return FALLBACK_SCHEMA

    text = path.read_text(encoding="utf-8")
    result: dict[str, dict] = {}

    # Try to extract CREATE TABLE blocks
    create_re = re.compile(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\(([^;]+?)\);",
        re.IGNORECASE | re.DOTALL,
    )

    for m in create_re.finditer(text):
        table_name = m.group(1).lower()
        body = m.group(2)
        cols, pk, not_null = _parse_create_body(body)
        result[table_name] = {"pk": pk, "columns": cols, "not_null": not_null, "note": ""}

    # Fill missing tables from fallback
    for tname in TABLE_ORDER:
        if tname not in result:
            result[tname] = FALLBACK_SCHEMA.get(tname, {
                "pk": "id",
                "columns": ["(schema not available)"],
                "not_null": [],
                "note": "Not found in SCHEMA.md",
            })

    return result


def _parse_create_body(body: str) -> tuple[list, str, list]:
    """Extract column names, PK, and NOT NULL columns from CREATE TABLE body."""
    lines = [l.strip() for l in body.splitlines() if l.strip()]
    columns = []
    pk = ""
    not_null = []

    for line in lines:
        # Strip trailing comma
        line = line.rstrip(",").strip()
        if not line:
            continue
        upper = line.upper()

        if upper.startswith("PRIMARY KEY"):
            # PRIMARY KEY (col, col)
            m = re.search(r"PRIMARY KEY\s*\(([^)]+)\)", line, re.IGNORECASE)
            if m:
                pk = m.group(1).strip()
            continue
        if upper.startswith("CONSTRAINT") or upper.startswith("UNIQUE") or upper.startswith("CHECK") or upper.startswith("FOREIGN"):
            continue

        # Column definition: name TYPE [constraints...]
        parts = line.split()
        if len(parts) < 2:
            continue
        col_name = parts[0]
        col_type = parts[1]
        col_def = f"{col_name} {col_type}"
        columns.append(col_def)

        if "NOT NULL" in upper or "SERIAL" in upper or "BIGSERIAL" in upper:
            not_null.append(col_name)

        # Detect inline PK
        if "PRIMARY KEY" in upper:
            pk = f"{col_name} ({col_type})"

    return columns, pk or "id", not_null


def generate(feedback: Optional[list] = None, **kwargs) -> str:
    """
    Generate schema-viewer.html content.
    feedback: list[str] from council review loop.
    """
    feedback = feedback or []

    schema_path = ALPHAVEDA_ROOT / "docs" / "supabase" / "SCHEMA.md"
    schema = _parse_schema_md(schema_path)

    cards_html = _build_cards(schema)
    feedback_section = _build_feedback_section(feedback)
    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline';">
<title>AlphaVeda — Schema Viewer</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Courier New', Courier, monospace;
    background: {BRAND['indigo']};
    color: {BRAND['ivory']};
    min-height: 100vh;
    padding: 2rem 1.5rem;
  }}
  h1 {{ font-size: 1.4rem; letter-spacing: 0.1em; color: {BRAND['gold']}; margin-bottom: 0.25rem; }}
  .generated {{ font-size: 0.72rem; color: #9a97a8; margin-bottom: 2rem; }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.25rem;
    margin-bottom: 2rem;
  }}
  .card {{
    background: rgba(255,255,255,0.04);
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.1);
    overflow: hidden;
  }}
  .card-header {{
    background: {BRAND['gold']};
    color: {BRAND['indigo']};
    padding: 0.6rem 1rem;
    font-weight: 700;
    font-size: 0.9rem;
    letter-spacing: 0.06em;
  }}
  .card-body {{ padding: 0.75rem 1rem; }}
  .pk-row {{
    font-size: 0.72rem;
    color: {BRAND['teal']};
    margin-bottom: 0.6rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
  }}
  .pk-label {{ color: #9a97a8; }}
  .col-list {{ list-style: none; }}
  .col-item {{
    font-size: 0.75rem;
    padding: 0.2rem 0;
    display: flex;
    align-items: baseline;
    gap: 0.4rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
  }}
  .col-item:last-child {{ border-bottom: none; }}
  .col-name {{ color: {BRAND['ivory']}; }}
  .col-type {{ color: #9a97a8; font-size: 0.7rem; }}
  .nn-badge {{
    font-size: 0.6rem;
    background: rgba(45,122,114,0.3);
    color: {BRAND['teal']};
    border-radius: 3px;
    padding: 0 0.3rem;
    flex-shrink: 0;
  }}
  .note {{
    font-size: 0.68rem;
    color: #9a97a8;
    margin-top: 0.6rem;
    padding-top: 0.5rem;
    border-top: 1px solid rgba(255,255,255,0.08);
    line-height: 1.4;
  }}
  details summary {{
    cursor: pointer; font-size: 0.75rem; color: {BRAND['gold']};
    letter-spacing: 0.08em; text-transform: uppercase;
    list-style: none; margin-bottom: 0.5rem;
  }}
  details summary::before {{ content: '▶  '; }}
  details[open] summary::before {{ content: '▼  '; }}
  .feedback-list {{ padding: 0.5rem 1rem; }}
  .feedback-list li {{ font-size: 0.78rem; color: #d4c9a8; margin-bottom: 0.3rem; }}
</style>
</head>
<body>
<h1>AlphaVeda — Schema Viewer</h1>
<div class="generated">Generated {generated_at} &nbsp;|&nbsp; 11 tables</div>

<div class="grid">
{cards_html}
</div>

<!-- SEBI compliance footer — always present when schema contains signal-related tables -->
<div style="font-size:0.68rem;color:#9a97a8;border-top:1px solid rgba(255,255,255,0.1);
     padding-top:0.75rem;margin-top:1rem;line-height:1.5;">
  AlphaVeda schema reference — for research purposes only.
  Not investment advice. Signal weights and confidence values are internal
  model parameters, not recommendations. Consult a SEBI-registered investment
  advisor before making any investment decision.
</div>

{feedback_section}
</body>
</html>"""

    return html


def _build_cards(schema: dict[str, dict]) -> str:
    parts = []
    for tname in TABLE_ORDER:
        info = schema.get(tname, FALLBACK_SCHEMA.get(tname, {}))
        pk = info.get("pk", "id")
        columns = info.get("columns", [])
        not_null = set(info.get("not_null", []))
        note = info.get("note", "")

        col_items = []
        for col_def in columns[:20]:  # cap at 20 cols per card for FM-06
            parts_col = col_def.split()
            col_name = parts_col[0] if parts_col else col_def
            col_type = " ".join(parts_col[1:]) if len(parts_col) > 1 else ""
            nn = '<span class="nn-badge">NN</span>' if col_name in not_null else ""
            col_items.append(
                f'      <li class="col-item">'
                f'<span class="col-name">{col_name}</span>'
                f'<span class="col-type">{col_type}</span>'
                f'{nn}</li>'
            )

        truncated = ""
        if len(columns) > 20:
            truncated = f'<div class="note">[{len(columns) - 20} more columns — truncated for size]</div>'

        note_html = f'<div class="note">{note}</div>' if note else ""

        card = f"""  <div class="card">
    <div class="card-header">{tname}</div>
    <div class="card-body">
      <div class="pk-row"><span class="pk-label">PK: </span>{pk}</div>
      <ul class="col-list">
{chr(10).join(col_items)}
      </ul>
{truncated}
{note_html}
    </div>
  </div>"""
        parts.append(card)

    return "\n".join(parts)


def _build_feedback_section(feedback: list) -> str:
    if not feedback:
        return ""
    items = "\n".join(
        f'      <li>{f.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</li>'
        for f in feedback
    )
    return f"""
<details>
  <summary>Council Review Notes — gaps addressed in this iteration</summary>
  <ul class="feedback-list">
{items}
  </ul>
</details>"""
