"""Signal weight loader — DB active weights with cold-start fallback.

Priority (Munger review gate condition):
  1. ACTIVE rows in signal_weights table for (lynch_class, regime)
  2. COLD_START_WEIGHTS Bayesian priors (Buffett floor always satisfied)

DB exception during load → cold-start (weights are not security-critical;
fail-open is correct here, unlike is_commercial() which is fail-closed).
"""
from __future__ import annotations
from constants import COLD_START_WEIGHTS
from src.config import get_supabase_client


def load_weights(lynch_class: str, regime: str) -> dict[str, float]:
    """Return {signal_name: weight} for the given segment.

    Queries signal_weights WHERE lynch_class=? AND regime=? AND status='ACTIVE'.
    Falls back to COLD_START_WEIGHTS if no rows or DB unavailable.
    Raises ValueError if lynch_class is unrecognised AND DB returns nothing.
    """
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
        if result.data:
            return {row["signal_name"]: row["weight"] for row in result.data}
    except Exception:
        pass

    # Fall back to cold-start priors
    if lynch_class not in COLD_START_WEIGHTS:
        raise ValueError(
            f"No weights found: lynch_class={lynch_class!r} has no DB rows "
            "and is not in COLD_START_WEIGHTS."
        )
    return dict(COLD_START_WEIGHTS[lynch_class])
