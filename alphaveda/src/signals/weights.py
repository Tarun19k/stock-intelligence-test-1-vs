"""Signal weight loader — DB active weights with cold-start fallback.

Priority (Munger review gate condition):
  1. ACTIVE rows in signal_weights table for (lynch_class, regime)
  2. COLD_START_WEIGHTS Bayesian priors (Buffett floor always satisfied)

DB exception during load → cold-start (weights are not security-critical;
fail-open is correct here, unlike is_commercial() which is fail-closed).
"""
from __future__ import annotations
from datetime import datetime, timezone
from constants import COLD_START_WEIGHTS, FUNDAMENTAL_WEIGHT_FLOOR
from src.config import get_supabase_client

# Signals that count toward the Buffett fundamental floor.
FUNDAMENTAL_SIGNALS: frozenset[str] = frozenset({
    "roic", "fcf", "eps_growth", "peg", "dividend", "debt_equity", "book_value",
})

# Hard upper bound per signal weight — catches injected extreme values.
_MAX_SIGNAL_WEIGHT: float = 5.0


def _validate_db_weights(weights: dict[str, float]) -> dict[str, float]:
    """Validate DB-loaded weights before they enter the signal pipeline.

    Raises ValueError on:
    - Any weight outside [0.0, _MAX_SIGNAL_WEIGHT] (C2 — injection guard)
    - Combined fundamental weight below FUNDAMENTAL_WEIGHT_FLOOR when
      at least one fundamental signal is present (C4 — Buffett floor on DB path)
    """
    for signal_name, weight in weights.items():
        if not (0.0 <= weight <= _MAX_SIGNAL_WEIGHT):
            raise ValueError(
                f"Signal weight out of valid range: "
                f"{signal_name}={weight!r} (must be 0.0–{_MAX_SIGNAL_WEIGHT})"
            )
    present_fundamentals = FUNDAMENTAL_SIGNALS & weights.keys()
    if present_fundamentals:
        fundamental_total = sum(weights[sig] for sig in present_fundamentals)
        if fundamental_total < FUNDAMENTAL_WEIGHT_FLOOR:
            raise ValueError(
                f"DB weights violate FUNDAMENTAL_WEIGHT_FLOOR: "
                f"combined {present_fundamentals} = {fundamental_total:.3f} "
                f"< {FUNDAMENTAL_WEIGHT_FLOOR}"
            )
    return weights


def load_weights(lynch_class: str, regime: str) -> dict[str, float]:
    """Return {signal_name: weight} for the given segment.

    Queries signal_weights WHERE lynch_class=? AND regime=? AND status='ACTIVE'.
    Falls back to COLD_START_WEIGHTS if no rows or DB unavailable.
    Raises ValueError if lynch_class is unrecognised AND DB returns nothing.
    """
    db_data = None
    try:
        result = (
            get_supabase_client()
            .table("signal_weights")
            .select("signal_name,weight")
            .eq("lynch_class", lynch_class)
            .eq("regime", regime)
            .eq("status", "ACTIVE")
            .execute()
        )
        db_data = result.data
    except Exception:
        pass  # DB unreachable — fall through to cold-start

    if db_data:
        weights = {row["signal_name"]: row["weight"] for row in db_data}
        return _validate_db_weights(weights)  # ValueError propagates — data integrity failure

    # Fall back to cold-start priors
    if lynch_class not in COLD_START_WEIGHTS:
        raise ValueError(
            f"No weights found: lynch_class={lynch_class!r} has no DB rows "
            "and is not in COLD_START_WEIGHTS."
        )
    return dict(COLD_START_WEIGHTS[lynch_class])


def approve_signal_weight(weight_id: int) -> None:
    """Change a signal weight row from PROPOSED → ACTIVE.

    This is the sole application-layer path to ACTIVE status.
    Only invoke from a human-initiated context — automation is prohibited.

    Raises ValueError if:
    - The row is not found (id does not exist)
    - The row's current status is not 'PROPOSED'
    """
    client = get_supabase_client()
    result = (
        client.table("signal_weights")
        .select("id,status")
        .eq("id", weight_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise ValueError(f"signal_weights row not found: id={weight_id}")

    current_status = result.data[0]["status"]
    if current_status != "PROPOSED":
        raise ValueError(
            f"Cannot approve weight id={weight_id}: "
            f"status is {current_status!r}, expected 'PROPOSED'"
        )

    (client.table("signal_weights")
        .update({
            "status": "ACTIVE",
            "approved_by": "tarun",
            "approved_at": datetime.now(timezone.utc).isoformat(),
        })
        .eq("id", weight_id)
        .execute())
