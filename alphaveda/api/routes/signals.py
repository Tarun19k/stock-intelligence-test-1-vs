"""GET /signals — signal weight status + cold-start state.

Delegates to src/pages/signals.py for all business logic.
No signal computation happens here — signals are emitted by ingest pipeline
and stored in DB. This endpoint reads that state.
"""
from __future__ import annotations
from datetime import date
from fastapi import APIRouter
from src.pages.signals import (
    get_proposed_weights_count,
    get_weight_review_banner,
    get_cold_start_label,
)
from src.config import get_supabase_client
from constants import OBSERVATION_THRESHOLD
from api._envelope import envelope

router = APIRouter()


@router.get("")
def signals_state() -> dict:
    sb = get_supabase_client()

    # Total observations across all segments — used for cold-start label.
    obs_result = (
        sb.table("accuracy_outcomes")
        .select("id", count="exact")
        .execute()
    )
    total_obs = obs_result.count or 0

    proposed_count = get_proposed_weights_count()
    cold_start_label = get_cold_start_label(total_obs)
    weight_banner = get_weight_review_banner()

    data = {
        "cold_start": total_obs < OBSERVATION_THRESHOLD,
        "total_observations": total_obs,
        "observation_threshold": OBSERVATION_THRESHOLD,
        "cold_start_label": cold_start_label,
        "proposed_weights_count": proposed_count,
        "weight_review_banner": weight_banner,
    }
    return envelope(data, as_of=date.today())
