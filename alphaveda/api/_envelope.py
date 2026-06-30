"""SEBI envelope helper — wraps every API response.

Single source of truth for sebi_disclaimer text is constants.py.
Frontend renders the backend-provided string; text cannot drift between
Python and TypeScript.
"""
from __future__ import annotations
from datetime import date as _date
from constants import SEBI_DISCLAIMER


def envelope(data: list | dict, as_of: _date | None = None) -> dict:
    """Wrap data in the standard SEBI envelope.

    Every endpoint must return this structure. The Next.js frontend
    renders sebi_disclaimer directly from this field — never from a
    hardcoded TypeScript string.
    """
    return {
        "data": data,
        "sebi_disclaimer": SEBI_DISCLAIMER,
        "as_of": (as_of or _date.today()).isoformat(),
    }
