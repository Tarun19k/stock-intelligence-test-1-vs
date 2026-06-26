"""Waitlist form submission handler.

record_waitlist_submission() is idempotent — if the email already exists,
returns the existing record rather than raising a duplicate-key error.
"""
from __future__ import annotations

from typing import Optional


def record_waitlist_submission(
    supabase_client,
    email: str,
    price_feedback: Optional[str] = None,
) -> dict:
    """Insert a waitlist row for the given email.

    Returns the created or existing record dict.
    Idempotent: duplicate email → existing record returned, no error raised.
    """
    existing = (
        supabase_client.table("waitlist")
        .select("id, email")
        .eq("email", email)
        .limit(1)
        .execute()
    )
    if existing.data:
        return existing.data[0]

    row: dict = {"email": email}
    if price_feedback is not None:
        row["price_feedback"] = price_feedback

    result = supabase_client.table("waitlist").insert(row).execute()
    return result.data[0]
