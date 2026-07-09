"""Signal emit engine — full pipeline: arbitrate → discount → calibrate.

Pipeline contract (Soros condition — non-negotiable):
  Step 3a: arbitrate(signals) → direction + confidence
  Step 3b: apply STREAK_DISCOUNT_FACTOR to confidence (BEFORE calibration)
  Step 3c: calibrate_confidence(post-discount confidence, obs, hit_rate) → p

Bins used for accuracy scoring must be built from POST-discount confidence.
Calibrating before discounting would produce bins misaligned with actual emit values.

Phase 4 adds Kelly sizing (step 4) as a separate layer on top of this pipeline.

emit_signal() is the DB orchestrator: computes signals from OHLCV history,
calls emit_pipeline(), writes to accuracy_predictions.
"""
from __future__ import annotations
from constants import (
    OBSERVATION_THRESHOLD,
    STREAK_DISCOUNT_FACTOR,
    STREAK_WINDOW,
)
from src.accuracy.ledger import compute_streak_flag
from src.signals.arbitration import arbitrate


def calibrate_confidence(
    confidence: float,
    segment_obs: int,
    hit_rate: float,
) -> float:
    """Map raw confidence to calibrated probability p ∈ [0.0, 1.0].

    Cold-start (segment_obs < OBSERVATION_THRESHOLD):
        p = min(confidence / 100, hit_rate)
    Warm (segment_obs >= OBSERVATION_THRESHOLD):
        p = min(confidence / 100, hit_rate)   — same formula; warm path for future Platt scaling
    """
    return min(confidence / 100.0, hit_rate)


def emit_pipeline(
    signals: list[dict],
    streak_count: int,
    segment_obs: int,
    hit_rate: float,
) -> dict | None:
    """Pure pipeline: no DB calls. Accepts pre-computed inputs.

    Returns emit dict or None (suppressed).
    Returned dict keys: direction, pre_calibration_confidence, calibrated_p,
                        streak_discounted.
    """
    arb = arbitrate(signals)
    if arb is None:
        return None

    confidence = arb["confidence"]

    # Step 3b — streak discount BEFORE calibration (Soros pipeline contract)
    streak_discounted = compute_streak_flag(streak_count)
    if streak_discounted:
        confidence = confidence * STREAK_DISCOUNT_FACTOR

    # Step 3c — calibration uses post-discount confidence
    calibrated_p = calibrate_confidence(
        confidence=confidence,
        segment_obs=segment_obs,
        hit_rate=hit_rate,
    )

    return {
        "direction": arb["direction"],
        "pre_calibration_confidence": confidence,
        "calibrated_p": calibrated_p,
        "streak_discounted": streak_discounted,
    }


def emit_signal(instrument_id: int, as_of: str) -> dict | None:
    """DB orchestrator: load context → build signal → emit → write accuracy_predictions.

    Verified column names (2026-07-01):
      macro_regime : regime_date (NOT NULL), regime, nifty_vix
      accuracy_predictions : direction, confidence, regime_tag, lynch_class,
                             magnitude_target, downside_target, emitted_at
      ohlcv : trade_date, open, high, low, close, circuit_flag

    Returns the written accuracy_predictions row dict, or None if suppressed.
    Signature matches TestImranConditions.test_emit_latency_under_800ms.
    """
    from datetime import datetime, timezone
    from src.config import get_supabase_client
    from src.signals.weights import load_weights
    from src.signals.downside import compute_downside_target

    supabase = get_supabase_client()

    # 1. Load instrument — lynch_class required for weight segment lookup
    inst = (
        supabase.table("instruments")
        .select("id,ticker,classification")
        .eq("id", instrument_id)
        .limit(1)
        .execute()
    )
    if not inst.data:
        return None
    lynch_class = inst.data[0]["classification"]

    # 2. Get current regime — macro_regime uses regime_date (not effective_date)
    regime_row = (
        supabase.table("macro_regime")
        .select("regime,nifty_vix")
        .lte("regime_date", as_of)
        .order("regime_date", desc=True)
        .limit(1)
        .execute()
    )
    regime_data = regime_row.data[0] if regime_row.data else {}
    regime = regime_data.get("regime", "RISK_ON")
    vix = float(regime_data.get("nifty_vix") or 14.0)

    # 3. Load weights for this segment (cold-start fallback if no ACTIVE rows)
    weights = load_weights(lynch_class, regime)

    # 4. Fetch recent OHLCV for signal computation (ATR_PERIOD + buffer)
    ohlcv_result = (
        supabase.table("ohlcv")
        .select("trade_date,open,high,low,close,circuit_flag")
        .eq("instrument_id", instrument_id)
        .lte("trade_date", as_of)
        .order("trade_date", desc=True)
        .limit(21)
        .execute()
    )
    ohlcv_rows = list(reversed(ohlcv_result.data or []))  # chronological

    if not ohlcv_rows:
        return None

    # 5. Build MVP signal: price momentum, weight=1.0 to clear ARBITRATION_MARGIN=15.0
    #    >= 2 rows → multi-day return; == 1 row → intraday (open → close)
    last = ohlcv_rows[-1]
    last_close = last.get("close")
    if last_close is None:
        return None

    if len(ohlcv_rows) >= 2:
        ref_close = ohlcv_rows[0]["close"]
        if not ref_close or ref_close == 0:
            return None
        ret = (last_close - ref_close) / ref_close
    else:
        ref_open = last.get("open") or last_close
        if not ref_open or ref_open == 0:
            return None
        ret = (last_close - ref_open) / ref_open

    direction = "BULL" if ret >= 0 else "BEAR"
    # No artificial floor: weak signals must fail to clear ARBITRATION_MARGIN
    # naturally and go silent via emit_pipeline() returning None. A floor here
    # previously defeated that suppression mechanism (RF-B, 2026-07-09).
    confidence = min(abs(ret) * 500, 100.0)
    signals = [{"direction": direction, "confidence": confidence,
                "signal_name": "momentum_price", "weight": 1.0}]

    # 6. Compute segment accuracy stats for calibration inputs
    all_preds_r = (
        supabase.table("accuracy_predictions")
        .select("id")
        .eq("instrument_id", instrument_id)
        .execute()
    )
    all_preds = all_preds_r.data or []
    segment_obs = len(all_preds)
    hit_rate = 0.5  # cold-start default
    streak_count = 0
    if all_preds:
        pred_ids = [p["id"] for p in all_preds]
        outcomes = (
            supabase.table("accuracy_outcomes")
            .select("hit")
            .in_("prediction_id", pred_ids)
            .execute()
            .data or []
        )
        if outcomes:
            hit_rate = sum(1 for o in outcomes if o["hit"]) / len(outcomes)
        recent = (
            supabase.table("accuracy_outcomes")
            .select("hit")
            .in_("prediction_id", pred_ids)
            .order("id", desc=True)
            .limit(STREAK_WINDOW + 1)
            .execute()
            .data or []
        )
        streak_count = sum(1 for o in recent if o["hit"])

    # 7. Run emit pipeline (arbitrate → streak discount → calibrate)
    result = emit_pipeline(signals, streak_count, segment_obs, hit_rate)
    if result is None:
        return None

    # 8. Compute ATR-based targets (Druckenmiller / GAP-001 fix)
    downside_target = compute_downside_target(instrument_id, None, ohlcv_rows)
    magnitude_target = downside_target  # symmetric ATR range for MVP

    # 8b. Compute cycle_phase — required NOT NULL column (check constraint: VALID_PHASES)
    from src.accuracy.cycle_phase import derive_cycle_phase, VIX_THRESHOLD
    # Use close vs a rough Nifty proxy; since we lack Nifty 200MA data assume above (mid-cycle)
    cycle_phase = derive_cycle_phase(
        regime=regime,
        nifty_close=22000.0,   # placeholder — assume above 200MA (mid-cycle RISK_ON)
        nifty_200ma=20000.0,
        vix=vix,
    )

    # 9. Write to accuracy_predictions (all NOT NULL columns verified 2026-07-01)
    #    confidence is SMALLINT (0-100); calibrated_p is float (0.0-1.0) → convert
    row = {
        "instrument_id": instrument_id,
        "direction": result["direction"],
        "confidence": int(round(result["calibrated_p"] * 100)),
        "regime_tag": regime,
        "lynch_class": lynch_class,
        "cycle_phase": cycle_phase,
        "horizon_days": 1,
        "magnitude_target": magnitude_target,
        "downside_target": downside_target,
        "emitted_at": datetime.now(timezone.utc).isoformat(),
    }
    written = supabase.table("accuracy_predictions").insert(row).execute()
    return written.data[0] if written.data else None
