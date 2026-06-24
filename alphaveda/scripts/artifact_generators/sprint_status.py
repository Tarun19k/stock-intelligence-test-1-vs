"""
sprint_status.py — Generate sprint-status.html artifact.

Reads:
- graphify-out/SESSION_RESUME.md  (sprint state, blockers, decisions)
- COUNCIL_TEST_MAP.md              (Phase test counts per status)

Outputs CSP-compliant HTML with:
- Revenue clock (days remaining; red if ≤3)
- Stream status strip (A/B/C/D)
- Sprint progress table (Phase 1–6)
- P0 blockers section
- Next action
"""

import re
import warnings
from datetime import date, datetime
from pathlib import Path
from typing import Optional

# Revenue deadline — hard-coded as specified
REVENUE_DEADLINE = date(2026, 6, 30)

BRAND = {
    "indigo": "#1A1F3C",
    "ivory": "#F5F3EC",
    "gold": "#E8A020",
    "teal": "#2D7A72",
    "green": "#4A8C5C",
    "terra": "#C0503A",
}

# Alphaveda workspace root (two levels above this file: scripts/artifact_generators → alphaveda)
_HERE = Path(__file__).resolve()
ALPHAVEDA_ROOT = _HERE.parent.parent.parent


def _alphaveda_path(relative: str) -> Path:
    return ALPHAVEDA_ROOT / relative


# ── Parsers ──────────────────────────────────────────────────────────────────

def _parse_session_resume(path: Path) -> dict:
    """
    Parse SESSION_RESUME.md for sprint state, blockers, streams, next action.
    Returns a dict with keys: streams, blockers, next_action, decisions.
    Falls back to placeholder data if file is absent (FM-04).
    """
    if not path.exists():
        warnings.warn(
            f"SESSION_RESUME.md not found at {path} — using placeholder data (FM-04)",
            RuntimeWarning,
            stacklevel=3,
        )
        return _placeholder_session_data()

    text = path.read_text(encoding="utf-8")

    # -- Streams A/B/C/D ---
    streams = _extract_streams(text)

    # -- P0 blockers ---
    blockers = _extract_section_lines(text, "P0 BLOCKER", "DO NOT REDO", "BLOCK SEQUENCE")
    if not blockers:
        blockers = _extract_section_lines(text, "BLOCKER", "DECISION", "NEXT")

    # -- Next action ---
    next_action = _extract_next_action(text)

    # -- Open decisions ---
    decisions = _extract_section_lines(text, "OPEN DECISION", "TARUN", "---")

    return {
        "streams": streams,
        "blockers": blockers[:10],   # cap at 10
        "next_action": next_action,
        "decisions": decisions[:5],
    }


def _extract_streams(text: str) -> dict:
    """Look for Stream A/B/C/D status lines anywhere in the text."""
    streams = {"A": "UNKNOWN", "B": "UNKNOWN", "C": "UNKNOWN", "D": "UNKNOWN"}
    pattern = re.compile(r"(?i)stream\s+([abcd])[:\s]+([A-Z_/\-]+)")
    for m in pattern.finditer(text):
        key = m.group(1).upper()
        val = m.group(2).strip()
        if key in streams:
            streams[key] = val
    # Fallback: look for table rows  | A | ... | STATUS |
    row_pat = re.compile(r"\|\s*([A-D])\s*\|[^|]*\|\s*([A-Z_/\-]+)\s*\|")
    for m in row_pat.finditer(text):
        key = m.group(1).upper()
        val = m.group(2).strip()
        if key in streams and streams[key] == "UNKNOWN":
            streams[key] = val
    return streams


def _extract_section_lines(text: str, *section_headers: str) -> list:
    """Extract bullet/list lines from the first matching section header."""
    lines = text.splitlines()
    in_section = False
    results = []
    stop_headers = {h.lower() for h in section_headers}

    for line in lines:
        lower = line.lower()
        if any(h in lower for h in stop_headers):
            if not in_section:
                in_section = True
                continue
            else:
                break
        if in_section:
            stripped = line.strip()
            if stripped.startswith(("-", "*", "•", "·")) or (
                len(stripped) > 5 and not stripped.startswith("#")
            ):
                clean = re.sub(r"^[-*•·]\s*", "", stripped).strip()
                if clean:
                    results.append(clean)
    return results


def _extract_next_action(text: str) -> str:
    pattern = re.compile(
        r"(?i)next\s+action[s]?\s*[:\-]\s*(.+?)(?:\n|$)"
    )
    m = pattern.search(text)
    if m:
        return m.group(1).strip()

    # Look for TARUN P0 ACTIONS section
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "tarun" in line.lower() and "p0" in line.lower():
            for j in range(i + 1, min(i + 6, len(lines))):
                candidate = lines[j].strip()
                if candidate and not candidate.startswith("#"):
                    return re.sub(r"^[-*•·]\s*", "", candidate).strip()

    return "See SESSION_RESUME.md for next action."


def _placeholder_session_data() -> dict:
    return {
        "streams": {"A": "PRE_LAUNCH", "B": "BLOCKED", "C": "NOT_STARTED", "D": "NOT_STARTED"},
        "blockers": ["SESSION_RESUME.md not found — placeholder data shown"],
        "next_action": "Locate or regenerate SESSION_RESUME.md",
        "decisions": [],
    }


def _parse_council_test_map(path: Path) -> dict:
    """
    Parse COUNCIL_TEST_MAP.md and count GREEN/RED/SPEC per Phase (1–6).
    Returns {phase: {"GREEN": n, "RED": n, "SPEC": n, "total": n}}
    """
    phases: dict[str, dict] = {}

    if not path.exists():
        warnings.warn(
            f"COUNCIL_TEST_MAP.md not found at {path} — phase progress unavailable",
            RuntimeWarning,
            stacklevel=3,
        )
        return {str(p): {"GREEN": 0, "RED": 0, "SPEC": 0, "total": 0} for p in range(1, 7)}

    text = path.read_text(encoding="utf-8")
    # Table rows: | Seat | Condition | Test file | Function | Phase | Status |
    row_re = re.compile(
        r"\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|\s*(\w+)\s*\|\s*(GREEN|RED|SPEC)[^|]*\|"
    )
    for m in row_re.finditer(text):
        phase_raw = m.group(1).strip()
        status = m.group(2).strip()
        # Normalise phase: "1" / "2" / ... / "G1" / "1 ext" → use raw string key
        phase_key = re.sub(r"\s+", "", phase_raw)
        if phase_key not in phases:
            phases[phase_key] = {"GREEN": 0, "RED": 0, "SPEC": 0, "total": 0}
        phases[phase_key][status] = phases[phase_key].get(status, 0) + 1
        phases[phase_key]["total"] += 1

    # Ensure Phases 1–6 always present
    for p in range(1, 7):
        key = str(p)
        if key not in phases:
            phases[key] = {"GREEN": 0, "RED": 0, "SPEC": 0, "total": 0}

    return phases


def _pct(n: int, total: int) -> int:
    if total == 0:
        return 0
    return round(100 * n / total)


# ── HTML builder ─────────────────────────────────────────────────────────────

def generate(feedback: Optional[list] = None, **kwargs) -> str:
    """
    Generate sprint-status.html content.
    feedback: list[str] from council review loop (FM-01 / feedback integration).
    """
    feedback = feedback or []

    resume_path = _alphaveda_path("graphify-out/SESSION_RESUME.md")
    map_path = _alphaveda_path("COUNCIL_TEST_MAP.md")

    session_data = _parse_session_resume(resume_path)
    phase_data = _parse_council_test_map(map_path)

    today = date.today()
    days_remaining = (REVENUE_DEADLINE - today).days
    clock_color = BRAND["terra"] if days_remaining <= 3 else BRAND["gold"]
    clock_label = "DAYS TO REVENUE DEADLINE"

    # Build stream badges
    stream_badges = _build_stream_badges(session_data["streams"])

    # Build phase table rows
    phase_rows = _build_phase_rows(phase_data)

    # Build blockers
    blockers_html = _build_blockers(session_data["blockers"])

    # Next action
    next_action = session_data["next_action"]

    # Council feedback section (FM-01 feedback loop)
    feedback_section = _build_feedback_section(feedback)

    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline';">
<title>AlphaVeda — Sprint Status</title>
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
  /* Revenue clock */
  .clock-wrap {{
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    background: rgba(255,255,255,0.05);
    border: 2px solid {clock_color};
    border-radius: 10px;
    padding: 1.2rem 2.5rem;
    margin-bottom: 2rem;
  }}
  .clock-num {{ font-size: 3.5rem; font-weight: 700; color: {clock_color}; line-height: 1; }}
  .clock-label {{ font-size: 0.7rem; letter-spacing: 0.12em; color: #9a97a8; margin-top: 0.4rem; }}
  /* Streams */
  .section-title {{ font-size: 0.75rem; letter-spacing: 0.15em; color: {BRAND['gold']}; margin-bottom: 0.75rem; text-transform: uppercase; }}
  .streams-wrap {{ display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 2rem; }}
  .stream-badge {{
    display: flex; flex-direction: column; align-items: center;
    padding: 0.75rem 1.25rem;
    border-radius: 8px;
    min-width: 90px;
    background: rgba(255,255,255,0.06);
  }}
  .stream-letter {{ font-size: 1.5rem; font-weight: 700; }}
  .stream-status {{ font-size: 0.65rem; letter-spacing: 0.08em; margin-top: 0.3rem; }}
  /* Phase table */
  table {{ border-collapse: collapse; width: 100%; max-width: 680px; margin-bottom: 2rem; }}
  th, td {{ padding: 0.5rem 0.75rem; text-align: left; font-size: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.08); }}
  th {{ color: {BRAND['gold']}; font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase; }}
  .bar-wrap {{ background: rgba(255,255,255,0.1); border-radius: 4px; height: 8px; width: 120px; }}
  .bar-fill {{ height: 8px; border-radius: 4px; background: {BRAND['teal']}; }}
  .pct-label {{ font-size: 0.72rem; color: {BRAND['teal']}; margin-left: 0.4rem; }}
  /* Blockers */
  .blockers-wrap {{ margin-bottom: 2rem; max-width: 680px; }}
  .blocker-item {{
    display: flex; align-items: flex-start; gap: 0.6rem;
    padding: 0.6rem 0.9rem; margin-bottom: 0.5rem;
    background: rgba(192,80,58,0.15);
    border-left: 3px solid {BRAND['terra']};
    border-radius: 0 6px 6px 0;
    font-size: 0.8rem;
    line-height: 1.45;
  }}
  .blocker-dot {{ color: {BRAND['terra']}; flex-shrink: 0; margin-top: 0.05rem; }}
  /* Next action */
  .next-action-wrap {{
    max-width: 680px;
    padding: 0.9rem 1.1rem;
    background: rgba(45,122,114,0.15);
    border-left: 3px solid {BRAND['teal']};
    border-radius: 0 6px 6px 0;
    font-size: 0.85rem;
    line-height: 1.5;
    margin-bottom: 2rem;
  }}
  /* Council feedback */
  details summary {{
    cursor: pointer; font-size: 0.75rem; color: {BRAND['gold']};
    letter-spacing: 0.08em; text-transform: uppercase;
    list-style: none; margin-bottom: 0.5rem;
  }}
  details summary::before {{ content: '▶  '; }}
  details[open] summary::before {{ content: '▼  '; }}
  .feedback-list {{ padding: 0.5rem 1rem; }}
  .feedback-list li {{ font-size: 0.78rem; color: #d4c9a8; margin-bottom: 0.3rem; }}
  .no-blockers {{ color: {BRAND['green']}; font-size: 0.82rem; }}
</style>
</head>
<body>
<h1>AlphaVeda — Sprint Status</h1>
<div class="generated">Generated {generated_at} &nbsp;|&nbsp; Deadline: {REVENUE_DEADLINE.isoformat()}</div>

<!-- Revenue Clock -->
<div class="clock-wrap">
  <div class="clock-num" style="color:{clock_color}">{days_remaining}</div>
  <div class="clock-label">{clock_label}</div>
</div>

<!-- Stream Status -->
<div class="section-title">Stream Status</div>
<div class="streams-wrap">
{stream_badges}
</div>

<!-- Sprint Progress -->
<div class="section-title">Sprint Progress</div>
<table>
  <thead><tr><th>Phase</th><th>GREEN</th><th>RED</th><th>SPEC</th><th>Progress</th></tr></thead>
  <tbody>
{phase_rows}
  </tbody>
</table>

<!-- P0 Blockers -->
<div class="section-title">P0 Blockers</div>
<div class="blockers-wrap">
{blockers_html}
</div>

<!-- Next Action -->
<div class="section-title">Next Action</div>
<div class="next-action-wrap">{next_action}</div>

{feedback_section}
</body>
</html>"""

    return html


def _build_stream_badges(streams: dict) -> str:
    status_colors = {
        "COMPLETE": "#4A8C5C",
        "DONE": "#4A8C5C",
        "PASS": "#4A8C5C",
        "ACTIVE": "#2D7A72",
        "IN_PROGRESS": "#2D7A72",
        "PRE_LAUNCH": "#E8A020",
        "BLOCKED": "#C0503A",
        "NOT_STARTED": "#4a4a6a",
        "UNKNOWN": "#4a4a6a",
    }
    badges = []
    for letter, status in sorted(streams.items()):
        color = status_colors.get(status.upper(), "#4a4a6a")
        badges.append(
            f'  <div class="stream-badge" style="border:1px solid {color}">'
            f'<span class="stream-letter" style="color:{color}">{letter}</span>'
            f'<span class="stream-status" style="color:{color}">{status}</span></div>'
        )
    return "\n".join(badges)


def _build_phase_rows(phase_data: dict) -> str:
    rows = []
    for phase_num in range(1, 7):
        key = str(phase_num)
        d = phase_data.get(key, {"GREEN": 0, "RED": 0, "SPEC": 0, "total": 0})
        green, red, spec, total = d["GREEN"], d["RED"], d["SPEC"], d["total"]
        pct = _pct(green, total)
        bar_fill = max(0, min(100, pct))
        rows.append(
            f'    <tr>'
            f'<td>Phase {phase_num}</td>'
            f'<td style="color:#4A8C5C">{green}</td>'
            f'<td style="color:#C0503A">{red}</td>'
            f'<td style="color:#9a97a8">{spec}</td>'
            f'<td><div style="display:flex;align-items:center">'
            f'<div class="bar-wrap"><div class="bar-fill" style="width:{bar_fill}%"></div></div>'
            f'<span class="pct-label">{pct}%</span></div></td>'
            f'</tr>'
        )
    return "\n".join(rows)


def _build_blockers(blockers: list) -> str:
    if not blockers:
        return '<div class="no-blockers">No P0 blockers detected.</div>'
    items = []
    for b in blockers:
        b_escaped = b.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        items.append(
            f'  <div class="blocker-item">'
            f'<span class="blocker-dot">&#9654;</span>'
            f'<span>{b_escaped}</span></div>'
        )
    return "\n".join(items)


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
