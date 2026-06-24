"""
session_checkpoint.py — Generate session-checkpoint.html artifact.

Reads:
- graphify-out/SESSION_RESUME.md  (DO NOT REDO section, TARUN P0 ACTIONS, OPEN DECISIONS)
- git log (last 5 commits via subprocess)

Single-column layout, warm ivory background, DM Mono / monospace timestamp.
CSP-compliant HTML — no external requests.
"""

import re
import subprocess
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


def _alphaveda_path(relative: str) -> Path:
    return ALPHAVEDA_ROOT / relative


# ── Git helpers ───────────────────────────────────────────────────────────────

def _get_recent_commits(repo_root: Path, n: int = 5) -> list[dict]:
    """Return last n commits as list of {hash, date, subject}."""
    try:
        result = subprocess.run(
            ["git", "log", f"-{n}", "--format=%H|%as|%s"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=10,
        )
        commits = []
        for line in result.stdout.strip().splitlines():
            parts = line.split("|", 2)
            if len(parts) == 3:
                commits.append({"hash": parts[0][:9], "date": parts[1], "subject": parts[2]})
        return commits
    except Exception as exc:
        warnings.warn(f"git log failed: {exc}", RuntimeWarning, stacklevel=3)
        return []


def _get_head_hash(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


# ── SESSION_RESUME parser ─────────────────────────────────────────────────────

def _parse_session_resume(path: Path) -> dict:
    """
    Extract three sections from SESSION_RESUME.md:
    - do_not_redo: lines under "DO NOT REDO"
    - tarun_p0: lines under "TARUN P0 ACTIONS"
    - open_decisions: lines under "OPEN DECISIONS"
    Falls back to placeholder data on file-not-found (FM-04).
    """
    if not path.exists():
        warnings.warn(
            f"SESSION_RESUME.md not found at {path} — using placeholder data (FM-04)",
            RuntimeWarning,
            stacklevel=3,
        )
        return {
            "do_not_redo": ["SESSION_RESUME.md missing — no completed work list available"],
            "tarun_p0": ["Locate or regenerate SESSION_RESUME.md"],
            "open_decisions": [],
            "raw_excerpt": "",
        }

    text = path.read_text(encoding="utf-8")

    do_not_redo = _extract_section(text, "DO NOT REDO", stop_on=["TARUN", "OPEN DECISION", "BLOCK SEQUENCE"])
    tarun_p0 = _extract_section(text, "TARUN P0", stop_on=["OPEN DECISION", "DO NOT REDO", "BLOCK SEQUENCE"])
    open_decisions = _extract_section(text, "OPEN DECISION", stop_on=["TARUN", "DO NOT REDO", "BLOCK SEQUENCE"])

    # Raw excerpt for additional context (first 400 chars of non-heading content)
    raw_lines = [l for l in text.splitlines() if l.strip() and not l.startswith("#")]
    raw_excerpt = " ".join(raw_lines[:5])[:400]

    return {
        "do_not_redo": do_not_redo[:15],
        "tarun_p0": tarun_p0[:10],
        "open_decisions": open_decisions[:8],
        "raw_excerpt": raw_excerpt,
    }


def _extract_section(text: str, header: str, stop_on: list[str]) -> list[str]:
    """
    Return bullet/list items from the section starting with `header`
    and ending at any line containing a `stop_on` keyword.
    """
    lines = text.splitlines()
    in_section = False
    results = []
    stop_lower = [s.lower() for s in stop_on]

    for line in lines:
        stripped = line.strip()
        lower = stripped.lower()

        if header.lower() in lower:
            in_section = True
            continue

        if in_section:
            if any(s in lower for s in stop_lower) and (stripped.startswith("#") or stripped.startswith("##")):
                break
            # Accept bullet lines and plain non-empty lines that aren't headings
            if stripped.startswith(("-", "*", "•", "·", "1", "2", "3", "4", "5")):
                clean = re.sub(r"^[-*•·\d.)\s]+", "", stripped).strip()
                if clean:
                    results.append(clean)
            elif stripped and not stripped.startswith("#") and not stripped.startswith("|") and len(stripped) > 4:
                results.append(stripped)

    return results


# ── HTML builder ─────────────────────────────────────────────────────────────

def generate(feedback: Optional[list] = None, **kwargs) -> str:
    """
    Generate session-checkpoint.html content.
    feedback: list[str] from council review loop.
    """
    feedback = feedback or []

    resume_path = _alphaveda_path("graphify-out/SESSION_RESUME.md")
    repo_root = ALPHAVEDA_ROOT.parent  # repo root is one level above alphaveda/

    data = _parse_session_resume(resume_path)
    commits = _get_recent_commits(repo_root)
    head_hash = _get_head_hash(repo_root)

    # Build section HTML blocks
    do_not_redo_html = _build_item_list(data["do_not_redo"], color=BRAND["green"])
    tarun_p0_html = _build_item_list(data["tarun_p0"], color=BRAND["terra"])
    open_decisions_html = _build_item_list(data["open_decisions"], color=BRAND["gold"])
    commits_html = _build_commits(commits)
    feedback_section = _build_feedback_section(feedback)

    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline';">
<title>AlphaVeda — Session Checkpoint</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Courier New', Courier, monospace;
    background: {BRAND['ivory']};
    color: {BRAND['indigo']};
    min-height: 100vh;
    padding: 2rem 1.5rem;
    max-width: 760px;
    margin: 0 auto;
  }}
  h1 {{ font-size: 1.35rem; letter-spacing: 0.08em; color: {BRAND['indigo']}; margin-bottom: 0.2rem; }}
  .ts {{
    font-size: 0.7rem;
    color: #6b6880;
    margin-bottom: 2rem;
    letter-spacing: 0.06em;
  }}
  .hash-badge {{
    display: inline-block;
    background: {BRAND['indigo']};
    color: {BRAND['gold']};
    font-size: 0.7rem;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    letter-spacing: 0.06em;
    margin-left: 0.5rem;
  }}
  .section {{ margin-bottom: 2rem; }}
  .section-title {{
    font-size: 0.72rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    font-weight: 700;
    margin-bottom: 0.75rem;
    padding-bottom: 0.35rem;
    border-bottom: 2px solid currentColor;
  }}
  .item-list {{ list-style: none; }}
  .item {{ display: flex; gap: 0.6rem; padding: 0.45rem 0; border-bottom: 1px solid rgba(0,0,0,0.06); font-size: 0.82rem; line-height: 1.5; }}
  .item:last-child {{ border-bottom: none; }}
  .item-dot {{ flex-shrink: 0; margin-top: 0.1rem; }}
  .no-items {{ font-size: 0.8rem; color: #9a97a8; }}
  /* Commits */
  .commit-list {{ list-style: none; }}
  .commit-row {{
    display: flex; gap: 0.75rem; align-items: baseline;
    padding: 0.4rem 0;
    border-bottom: 1px solid rgba(0,0,0,0.06);
    font-size: 0.78rem;
  }}
  .commit-row:last-child {{ border-bottom: none; }}
  .commit-hash {{
    font-size: 0.68rem;
    background: {BRAND['indigo']};
    color: {BRAND['teal']};
    padding: 0.1rem 0.4rem;
    border-radius: 3px;
    flex-shrink: 0;
  }}
  .commit-date {{ color: #9a97a8; font-size: 0.7rem; flex-shrink: 0; }}
  .commit-msg {{ color: {BRAND['indigo']}; }}
  /* Feedback */
  details {{
    margin-top: 1.5rem;
    background: rgba(26,31,60,0.06);
    border-radius: 6px;
    padding: 0.75rem 1rem;
  }}
  details summary {{
    cursor: pointer; font-size: 0.75rem; color: {BRAND['teal']};
    letter-spacing: 0.08em; text-transform: uppercase;
    list-style: none;
  }}
  details summary::before {{ content: '▶  '; }}
  details[open] summary::before {{ content: '▼  '; }}
  .feedback-list {{ padding: 0.5rem 1rem; }}
  .feedback-list li {{ font-size: 0.78rem; color: {BRAND['indigo']}; margin-bottom: 0.3rem; }}
</style>
</head>
<body>
<h1>AlphaVeda — Session Checkpoint<span class="hash-badge">{head_hash}</span></h1>
<div class="ts">Generated {generated_at}</div>

<!-- What was built / DO NOT REDO -->
<div class="section">
  <div class="section-title" style="color:{BRAND['green']}">What Was Built (Do Not Redo)</div>
  {do_not_redo_html}
</div>

<!-- Tarun P0 Actions -->
<div class="section">
  <div class="section-title" style="color:{BRAND['terra']}">Tarun P0 Actions</div>
  {tarun_p0_html}
</div>

<!-- Open Decisions -->
<div class="section">
  <div class="section-title" style="color:{BRAND['gold']}">Open Decisions</div>
  {open_decisions_html}
</div>

<!-- Recent Git Commits -->
<div class="section">
  <div class="section-title" style="color:{BRAND['teal']}">Recent Git Commits</div>
  {commits_html}
</div>

{feedback_section}
</body>
</html>"""

    return html


def _build_item_list(items: list, color: str) -> str:
    if not items:
        return '<div class="no-items">None recorded.</div>'
    rows = []
    for item in items:
        escaped = item.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        rows.append(
            f'  <li class="item">'
            f'<span class="item-dot" style="color:{color}">&#9658;</span>'
            f'<span>{escaped}</span></li>'
        )
    return f'<ul class="item-list">\n' + "\n".join(rows) + "\n</ul>"


def _build_commits(commits: list) -> str:
    if not commits:
        return '<div class="no-items">No git history available.</div>'
    rows = []
    for c in commits:
        subj = c["subject"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        rows.append(
            f'  <li class="commit-row">'
            f'<span class="commit-hash">{c["hash"]}</span>'
            f'<span class="commit-date">{c["date"]}</span>'
            f'<span class="commit-msg">{subj}</span></li>'
        )
    return f'<ul class="commit-list">\n' + "\n".join(rows) + "\n</ul>"


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
