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
import logging
import math
import statistics
from datetime import date, timedelta
from constants import (
    ARBITRATION_MARGIN,
    OBSERVATION_THRESHOLD,
    STREAK_DISCOUNT_FACTOR,
    STREAK_WINDOW,
)
from src.accuracy.ledger import compute_streak_flag
from src.signals.arbitration import arbitrate

_LOG = logging.getLogger(__name__)

# ── RF-I fix constants ──────────────────────────────────────────────────────
# RF-I (2026-07-13, verified live against production DB): the momentum
# reference row used to be "whatever is oldest in the fetched <=21-row
# window" — for sparse instruments (~9 total rows, not daily-continuous) that
# silently meant almost the entire available history, diluting real moves to
# near-zero confidence (RELIANCE: ret=0.38%, confidence=1.9, suppressed).
#
# Part 1 (below, used in emit_signal): reference row is anchored to a target
# CALENDAR date ~21 days back from as_of, not "21 rows back." If no row
# exists within tolerance of that target, we fail loud (None + logged
# reason) instead of silently redefining the window.
#
# Part 2 (below, used in emit_signal): confidence is volatility-normalized
# (z-score of the move against the stdev of recent period returns) instead
# of a flat abs(ret) * 500 — the old formula had no way to distinguish a
# real move on a calm/low-beta stock from noise on a volatile one.
REFERENCE_WINDOW_CALENDAR_DAYS = 21
REFERENCE_TOLERANCE_TRADING_DAYS = 3
# Safety-net lookback for the OHLCV fetch: wide enough to comfortably contain
# the tolerance window above plus a full STDEV_WINDOW_ROWS of daily closes
# even when data is dense (daily-continuous). This is NOT itself a tolerance
# bound — it only ensures the fetch doesn't starve the stdev calculation.
FETCH_LOOKBACK_CALENDAR_DAYS = 32
STDEV_WINDOW_ROWS = 21

# CONFIDENCE_SCALE derivation (not a guessed magic number):
# confidence = min(abs(ret / stdev) * CONFIDENCE_SCALE, 100.0)
# We want a genuine ~1-sigma move (a realistic signal, not noise) to clear
# ARBITRATION_MARGIN (15.0) with comfortable headroom, so a single
# volatility-normalized signal can stand on its own without relying on other
# signals to help it clear the dead zone. Setting
#   CONFIDENCE_SCALE = 2.5 * ARBITRATION_MARGIN
# gives:
#   z = 1.0  (1-sigma move)   -> confidence = 37.5  (2.5x the margin)
#   z = 1.5  (1.5-sigma move) -> confidence = 56.25 (3.75x the margin)
#   z = 0.4  (0.4-sigma move) -> confidence = 15.0  (exactly at the margin)
# A calm/low-beta stock is no longer structurally suppressed by a low raw
# abs(ret): what matters is the size of the move RELATIVE TO ITS OWN
# volatility, not the raw magnitude vs. an instrument-agnostic constant.
CONFIDENCE_SCALE = 2.5 * ARBITRATION_MARGIN

# Below this, dividing by stdev is not just noisy — it's meaningless (a flat
# tape, not genuinely "zero risk"). Guards against ZeroDivisionError / inf / NaN.
MIN_STDEV_EPSILON = 1e-6


def _reference_tolerance_bounds(
    target_date: date,
    tolerance_trading_days: int = REFERENCE_TOLERANCE_TRADING_DAYS,
) -> tuple[date, date]:
    """Return (lower, upper) calendar-date bounds equivalent to
    +/- tolerance_trading_days weekday (Mon-Fri) sessions around target_date.

    Deliberately does NOT use pandas_market_calendars here: that library's
    first .schedule() call has real, unavoidable one-time setup cost
    (~700-900ms, confirmed via profiling) that blew emit_signal()'s 800ms
    latency SLA when this path was hit. A plain weekday walk is inexact
    around NSE holidays (may include 1-2 non-trading days in the tolerance
    window), but for a fuzzy +/-3-session tolerance band that inexactness is
    immaterial — worst case the window is very slightly wider than intended,
    never narrower, so it never causes a false RF-I_STALE_REFERENCE suppression.
    """
    lower = target_date
    remaining = tolerance_trading_days
    while remaining > 0:
        lower -= timedelta(days=1)
        if lower.weekday() < 5:  # Mon=0 .. Fri=4
            remaining -= 1

    upper = target_date
    remaining = tolerance_trading_days
    while remaining > 0:
        upper += timedelta(days=1)
        if upper.weekday() < 5:
            remaining -= 1

    return lower, upper


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
        .select("regime,nifty_vix,above_200ma")
        .lte("regime_date", as_of)
        .order("regime_date", desc=True)
        .limit(1)
        .execute()
    )
    regime_data = regime_row.data[0] if regime_row.data else {}
    regime = regime_data.get("regime", "RISK_ON")
    vix = float(regime_data.get("nifty_vix") or 14.0)
    above_200ma = bool(regime_data.get("above_200ma", True))

    # 3. Load weights for this segment (cold-start fallback if no ACTIVE rows)
    weights = load_weights(lynch_class, regime)

    # 4. Fetch the most recent rows up to as_of (RF-I fix part 2). The limit
    #    (FETCH_LOOKBACK_CALENDAR_DAYS-sized) is a generous safety net sized to
    #    comfortably cover both the reference-row tolerance search and the
    #    STDEV_WINDOW_ROWS volatility window below, for dense daily data. No
    #    server-side lower-bound filter — Python-side tolerance filtering below
    #    already excludes anything outside range, and dropping the extra WHERE
    #    clause measurably reduced query latency under the 800ms emit SLA.
    as_of_date = date.fromisoformat(as_of)
    reference_target_date = as_of_date - timedelta(days=REFERENCE_WINDOW_CALENDAR_DAYS)
    tolerance_lower, tolerance_upper = _reference_tolerance_bounds(reference_target_date)

    ohlcv_result = (
        supabase.table("ohlcv")
        .select("trade_date,open,high,low,close,circuit_flag")
        .eq("instrument_id", instrument_id)
        .lte("trade_date", as_of)
        .order("trade_date", desc=True)
        .limit(32)
        .execute()
    )
    ohlcv_rows = list(reversed(ohlcv_result.data or []))  # chronological

    if not ohlcv_rows:
        return None

    last = ohlcv_rows[-1]
    last_close = last.get("close")
    if last_close is None:
        return None

    # 5a. Locate the calendar-anchored reference row (RF-I fix part 2): the
    # available row nearest reference_target_date, but ONLY if it falls
    # within tolerance. An ingestion gap that pushes the nearest row outside
    # tolerance must fail loud, not silently redefine the window to
    # "whatever's oldest in the fetched rows" (the RF-I root cause).
    candidates = [
        row
        for row in ohlcv_rows
        if row.get("close") is not None
        and row.get("trade_date")
        and tolerance_lower <= date.fromisoformat(row["trade_date"]) <= tolerance_upper
    ]
    if not candidates:
        _LOG.warning(
            "RF-I_STALE_REFERENCE: emit_signal suppressed instrument_id=%s as_of=%s "
            "target=%s tolerance=[%s, %s] nearest_available=%s",
            instrument_id, as_of, reference_target_date, tolerance_lower, tolerance_upper,
            ohlcv_rows[0].get("trade_date") if ohlcv_rows else None,
        )
        return None

    reference_row = min(
        candidates,
        key=lambda row: abs((date.fromisoformat(row["trade_date"]) - reference_target_date).days),
    )
    ref_close = reference_row["close"]
    if not ref_close or ref_close == 0:
        return None

    if reference_row.get("trade_date") == last.get("trade_date"):
        # Reference resolved to the same row as "last" (only one usable row
        # in range) — no genuine multi-day move to measure. Let ret fall
        # through as 0.0; the insufficient-return-history guard below (5b)
        # is what actually suppresses this case, not a fabricated ret.
        ret = 0.0
    else:
        ret = (last_close - ref_close) / ref_close

    direction = "BULL" if ret >= 0 else "BEAR"

    # 5b. Volatility-normalized confidence (RF-I fix part 1). See
    # CONFIDENCE_SCALE derivation above the module constants.
    stdev_window = ohlcv_rows[-STDEV_WINDOW_ROWS:]
    closes = [row["close"] for row in stdev_window if row.get("close") is not None]
    period_returns = [
        (closes[i] - closes[i - 1]) / closes[i - 1]
        for i in range(1, len(closes))
        if closes[i - 1]
    ]
    if len(period_returns) < 2:
        # Can't compute a meaningful stdev from 0-1 return observations.
        _LOG.warning(
            "RF-I_INSUFFICIENT_RETURN_HISTORY: emit_signal suppressed instrument_id=%s "
            "as_of=%s n_returns=%s", instrument_id, as_of, len(period_returns),
        )
        return None

    stdev = statistics.stdev(period_returns)
    if not math.isfinite(stdev) or stdev < MIN_STDEV_EPSILON:
        _LOG.warning(
            "RF-I_ZERO_VOLATILITY: emit_signal suppressed instrument_id=%s as_of=%s stdev=%s",
            instrument_id, as_of, stdev,
        )
        return None

    z_score = abs(ret) / stdev
    confidence = z_score * CONFIDENCE_SCALE
    if not math.isfinite(confidence):
        _LOG.warning(
            "RF-I_NONFINITE_CONFIDENCE: emit_signal suppressed instrument_id=%s as_of=%s "
            "z_score=%s", instrument_id, as_of, z_score,
        )
        return None
    confidence = min(confidence, 100.0)

    # No artificial floor: weak signals must fail to clear ARBITRATION_MARGIN
    # naturally and go silent via emit_pipeline() returning None. A floor here
    # previously defeated that suppression mechanism (RF-B, 2026-07-09).
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
    # RF-E fix (2026-07-19): above_200ma now comes from a manually-seeded macro_regime
    # column instead of hardcoded 22000/20000 constants that always evaluated as "above MA".
    # derive_cycle_phase() only compares close > 200ma, so any two values with the right
    # relative order produce identical output; the real values are unused for now.
    cycle_phase = derive_cycle_phase(
        regime=regime,
        nifty_close=22000.0 if above_200ma else 18000.0,
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
