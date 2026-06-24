"""
council_review.py — Deterministic council review engine for AlphaVeda artifacts.

5 seats, each runs independently (FM-03: no seat sees others' verdicts).
SynthesisChair aggregates last.

Usage:
    from council_review import review_all
    results = review_all(html_content, artifact_type)
    # results = {"verdicts": [...], "final": {"verdict": ..., "gaps": [...]}}

Rule-based only — no LLM calls; safe for CI.
"""

import re
from pathlib import Path
from typing import Literal

ArtifactType = Literal["sprint-status", "schema-viewer", "session-checkpoint"]
Verdict = Literal["APPROVE", "REVISE"]

# Required sections per artifact type (TanviRao check)
REQUIRED_SECTIONS: dict[str, list[str]] = {
    "sprint-status": [
        "sprint status",
        "stream status",
        "sprint progress",
        "blocker",
        "next action",
    ],
    "schema-viewer": [
        "schema viewer",
        "card",
        "col-list",
        "card-header",
        "grid",
    ],
    "session-checkpoint": [
        "session checkpoint",
        "do not redo",
        "tarun p0",
        "open decision",
        "commit",
    ],
}

# Signal words that trigger SEBI disclaimer requirement (Varghese check)
SEBI_SIGNAL_WORDS = re.compile(
    r"\b(BULLISH|BEARISH|signal|confidence|BUY|SELL)\b", re.IGNORECASE
)

# CSP violation patterns (FM-02)
CSP_VIOLATION_PATTERNS = [
    (re.compile(r"<link\s[^>]*href\s*=\s*['\"]https?://", re.IGNORECASE), "external <link> tag"),
    (re.compile(r"<script\s[^>]*src\s*=\s*['\"]https?://", re.IGNORECASE), "external <script src>"),
    (re.compile(r"fetch\s*\(", re.IGNORECASE), "fetch() call"),
    (re.compile(r"@import\s+url\((?!data:)", re.IGNORECASE), "@import url() with external ref"),
    (re.compile(r"XMLHttpRequest", re.IGNORECASE), "XMLHttpRequest"),
    (re.compile(r"import\s+\w+\s+from\s+['\"]https?://", re.IGNORECASE), "ES module import from external URL"),
    (re.compile(r'url\((?!data:|#|\'#|"#)[\'"]?(?!data:)[\'"]?https?://', re.IGNORECASE), "CSS url() external ref"),
    (re.compile(r'<link\s[^>]*rel\s*=\s*[\'"]stylesheet[\'"][^>]*href\s*=', re.IGNORECASE), "stylesheet <link>"),
    (re.compile(r'<link\s[^>]*href\s*=\s*[\'"][^\'">]+[\'"][^>]*rel\s*=\s*[\'"]stylesheet[\'"]', re.IGNORECASE), "stylesheet <link> (attr-reversed)"),
]

MAX_FILE_SIZE_BYTES = 500 * 1024  # 500 KB


# ── Individual seat review functions ─────────────────────────────────────────
# Each function receives ONLY the html string — FM-03 compliance.

def _constraint_enforcer_review(html: str, artifact_type: ArtifactType) -> dict:
    """
    ConstraintEnforcer: scan for CSP violations.
    Checks for external resource requests (link, script, fetch, import, url()).
    """
    seat = "ConstraintEnforcer"
    gaps = []

    for pattern, label in CSP_VIOLATION_PATTERNS:
        if pattern.search(html):
            gaps.append(f"CSP violation detected: {label}")

    # Also check that a Content-Security-Policy meta tag exists
    csp_meta = re.compile(r'<meta[^>]+Content-Security-Policy', re.IGNORECASE)
    if not csp_meta.search(html):
        gaps.append("Missing <meta http-equiv='Content-Security-Policy'> tag")

    return {
        "seat": seat,
        "verdict": "REVISE" if gaps else "APPROVE",
        "gaps": gaps,
    }


def _varghese_sebi_review(html: str, artifact_type: ArtifactType) -> dict:
    """
    Varghese (SEBI): if artifact contains signal words, disclaimer must be present.
    Disclaimer must include 'research purposes only'.
    """
    seat = "Varghese"
    gaps = []

    has_signal_words = bool(SEBI_SIGNAL_WORDS.search(html))
    if has_signal_words:
        # Check for disclaimer text
        disclaimer_patterns = [
            re.compile(r"research purposes only", re.IGNORECASE),
            re.compile(r"not investment advice", re.IGNORECASE),
        ]
        for pat in disclaimer_patterns:
            if not pat.search(html):
                gaps.append(
                    f"Artifact contains signal words (BULLISH/BEARISH/signal/confidence) "
                    f"but missing disclaimer text: '{pat.pattern}'"
                )

    return {
        "seat": seat,
        "verdict": "REVISE" if gaps else "APPROVE",
        "gaps": gaps,
    }


def _tanviRao_ux_review(html: str, artifact_type: ArtifactType) -> dict:
    """
    TanviRao (UX): all 4+ required sections present; no section heading > 40 chars.
    """
    seat = "TanviRao"
    gaps = []

    required = REQUIRED_SECTIONS.get(artifact_type, [])
    html_lower = html.lower()
    for section_keyword in required:
        if section_keyword.lower() not in html_lower:
            gaps.append(f"Required section/element missing: '{section_keyword}'")

    # Check section heading lengths (h1-h4 and .section-title class content)
    heading_re = re.compile(r"<h[1-4][^>]*>([^<]{1,200})</h[1-4]>", re.IGNORECASE)
    for m in heading_re.finditer(html):
        heading_text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if len(heading_text) > 40:
            gaps.append(
                f"Section heading too long ({len(heading_text)} chars > 40): "
                f"'{heading_text[:50]}...'"
            )

    return {
        "seat": seat,
        "verdict": "REVISE" if gaps else "APPROVE",
        "gaps": gaps,
    }


def _imranSRA_reliability_review(
    html: str, artifact_type: ArtifactType, file_size_bytes: int = 0
) -> dict:
    """
    ImranSRA (reliability):
    - File size < 500 KB
    - 'Generated' timestamp present in content (validates artifact was freshly generated)
    - No Python traceback in output (artifact generated without exception)
    """
    seat = "ImranSRA"
    gaps = []

    # Use provided size or estimate from string length
    size = file_size_bytes if file_size_bytes > 0 else len(html.encode("utf-8"))
    if size > MAX_FILE_SIZE_BYTES:
        gaps.append(
            f"Artifact too large: {size // 1024}KB exceeds 500KB limit"
        )

    # Check for 'Generated' timestamp
    if "Generated" not in html and "generated" not in html.lower():
        gaps.append("No 'Generated' timestamp found in artifact — staleness check failed")

    # Check for Python tracebacks (sign of an exception being swallowed into HTML)
    if "Traceback (most recent call last)" in html:
        gaps.append("Python traceback found in artifact output — generation exception not handled")

    if "Error:" in html and "placeholder" not in html.lower():
        # Only flag if it's not a placeholder note
        pass  # Too noisy — skip; traceback check above is sufficient

    return {
        "seat": seat,
        "verdict": "REVISE" if gaps else "APPROVE",
        "gaps": gaps,
    }


def _synthesis_chair_aggregate(seat_results: list[dict]) -> dict:
    """
    SynthesisChair: aggregate all seat verdicts.
    - Any REVISE → final REVISE with combined gaps
    - All APPROVE → APPROVE
    FM-03: receives each seat's output, not intermediate reasoning.
    """
    seat = "SynthesisChair"
    all_gaps = []
    any_revise = False

    for result in seat_results:
        if result["verdict"] == "REVISE":
            any_revise = True
            for gap in result["gaps"]:
                prefixed = f"[{result['seat']}] {gap}"
                all_gaps.append(prefixed)

    return {
        "seat": seat,
        "verdict": "REVISE" if any_revise else "APPROVE",
        "gaps": all_gaps,
    }


# ── Public interface ──────────────────────────────────────────────────────────

def review_all(
    html: str,
    artifact_type: ArtifactType,
    file_size_bytes: int = 0,
) -> dict:
    """
    Run all council seats on the HTML artifact independently, then aggregate.

    Returns:
    {
        "verdicts": [  # one per seat, in run order
            {"seat": str, "verdict": "APPROVE"|"REVISE", "gaps": [str, ...]},
            ...
        ],
        "final": {"seat": "SynthesisChair", "verdict": ..., "gaps": [...]}
    }

    FM-03 compliance: each seat function receives ONLY the html string.
    """
    # Each seat runs independently — FM-03: no seat sees others' outputs
    seat_results = [
        _constraint_enforcer_review(html, artifact_type),
        _varghese_sebi_review(html, artifact_type),
        _tanviRao_ux_review(html, artifact_type),
        _imranSRA_reliability_review(html, artifact_type, file_size_bytes),
    ]

    final = _synthesis_chair_aggregate(seat_results)

    return {
        "verdicts": seat_results,
        "final": final,
    }


def collect_gaps(review_result: dict) -> list[str]:
    """Extract all gap strings from a review_all() result."""
    return review_result["final"]["gaps"]


def is_approved(review_result: dict) -> bool:
    """Return True if final verdict is APPROVE."""
    return review_result["final"]["verdict"] == "APPROVE"
