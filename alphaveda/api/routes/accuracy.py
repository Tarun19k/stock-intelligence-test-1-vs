"""GET /accuracy — accuracy ledger summary.

Delegates to src/pages/accuracy.py for staleness logic.
Accuracy data populates once predictions reach OBSERVATION_THRESHOLD (30).
"""
from __future__ import annotations
from datetime import date
from fastapi import APIRouter
from src.config import get_supabase_client
from src.pages.accuracy import get_staleness_warning, get_proposed_weights_summary
from api._envelope import envelope

router = APIRouter()


@router.get("")
def accuracy_state() -> dict:
    sb = get_supabase_client()

    # Latest signal_weights review date — used for staleness check.
    weights_result = (
        sb.table("signal_weights")
        .select("approved_at")
        .eq("status", "ACTIVE")
        .order("approved_at", desc=True)
        .limit(1)
        .execute()
    )

    staleness_warning = None
    if weights_result.data and weights_result.data[0].get("approved_at"):
        last_review_str = weights_result.data[0]["approved_at"][:10]
        last_review = date.fromisoformat(last_review_str)
        staleness_warning = get_staleness_warning(last_review)

    summary = get_proposed_weights_summary()

    data = {
        "proposed_weights_count": summary["count"],
        "has_pending": summary["has_pending"],
        "staleness_warning": staleness_warning,
        # outcome_rows: total resolved predictions (populates after OBSERVATION_THRESHOLD).
        "outcome_rows": (
            sb.table("accuracy_outcomes")
            .select("id", count="exact")
            .execute()
            .count or 0
        ),
    }
    return envelope(data, as_of=date.today())
