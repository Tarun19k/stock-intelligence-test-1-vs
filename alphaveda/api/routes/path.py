"""GET /path — Kelly sizing state.

Delegates to src/pages/path.py for commercial gate and suppression logic.
Rupee sizing is suppressed when is_commercial()=True (fail-closed).
Commercial state is determined server-side only — never client-side.
"""
from __future__ import annotations
from datetime import date
from fastapi import APIRouter
from src.config import is_commercial
from src.pages.path import get_suppression_label
from src.pages.signals import get_proposed_weights_count
from api._envelope import envelope

router = APIRouter()


@router.get("")
def path_state() -> dict:
    commercial = is_commercial()
    proposed_count = get_proposed_weights_count()

    data = {
        "commercial": commercial,
        "suppressed": commercial,
        "suppression_label": get_suppression_label() if commercial else None,
        "proposed_weights_count": proposed_count,
        # direction and rupee_size are populated once signals are emitted.
        # In cold-start state (no resolved outcomes yet), these are null.
        "direction": None,
        "rupee_size": None,
    }
    return envelope(data, as_of=date.today())
