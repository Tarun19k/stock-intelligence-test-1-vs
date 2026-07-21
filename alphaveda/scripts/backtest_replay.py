#!/usr/bin/env python3
"""Phase 0 backtest / refinement replay harness.

Retires scripts/backtest.py (deleted). The old script independently
reimplemented a duplicate of engine.py's momentum/confidence formula instead
of importing the real logic — it silently drifted from the live engine after
the RF-I fix (calendar-anchored reference window + volatility-normalized
confidence, src/signals/engine.py), which is exactly why 3 regression tests
in the old tests/test_backtest.py started failing. This harness imports
compute_momentum_signal() and emit_pipeline() DIRECTLY from
src/signals/engine.py (arbitrate() is called internally by emit_pipeline(),
imported from src/signals/arbitration.py) and never reimplements any of that
logic. If the live formula changes again, this harness picks it up
automatically — there is nothing here to keep in sync by hand.

Scope: non-commercial, internal-only tool for model training / algorithm
refinement (per CLAUDE.md Commercial Gate rules and the Phase 0 design
brief comparing weight configs, e.g. "Buffett-weighted" vs
"Druckenmiller-weighted"). NEVER a live fund-management feature.

Hard boundaries (do not remove without a new premortem):
  - Never calls emit_signal() and never writes to accuracy_predictions.
    That table backs live signal emission with different stakes; this
    script only replays historical data through the pure, DB-free pipeline
    functions (compute_momentum_signal, emit_pipeline).
  - Never writes ACTIVE rows to signal_weights and never calls
    src.signals.weights.approve_signal_weight(). Activating a weights_config
    that this harness scored well is a separate, human-gated action: a
    PROPOSED signal_weights row must be created and then a human calls
    approve_signal_weight(weight_id) to flip it to ACTIVE. This script does
    not create PROPOSED rows either — it only writes to the additive-only,
    no-downstream-consumers bt_backtest_runs / bt_backtest_attribution
    tables, which exist precisely so this kind of experimentation has
    somewhere safe to land.

Determinism contract: two calls to run_backtest_replay() with identical
weights_config, date range, instrument_ids, and unchanged underlying
OHLCV/accuracy tables must produce byte-identical weights_config and score
in the returned/written bt_backtest_runs row (run_at is expected to differ —
that's a timestamp, not a deterministic field).
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from dotenv import load_dotenv

    load_dotenv(
        os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
        override=False,
    )
except ImportError:
    pass

from src.signals.engine import compute_momentum_signal, emit_pipeline

# Minimum OHLCV rows for a backtest run to be considered meaningful. Below
# this, compute_momentum_signal structurally cannot produce more than a
# handful of non-suppressed observations (it needs ~21 calendar days of
# history just to locate a reference row, plus STDEV_WINDOW_ROWS=21 closes
# for the volatility normalization) — matches OBSERVATION_THRESHOLD's spirit
# without importing it (that constant means something different: minimum
# *predictions* per segment, not minimum *OHLCV rows*).
MIN_ROWS_FOR_BACKTEST = 40

_SIGNAL_NAME = "momentum_price"


def _weighted_signals(
    base_signals: list[dict], weights_config: dict[str, float]
) -> list[dict]:
    """Apply weights_config (signal_name -> weight) to a signals list.

    An empty weights_config passes signals through unchanged (weight=1.0,
    the live formula's baseline). A non-empty weights_config must cover
    every signal_name actually emitted — fail loud on a gap rather than
    silently defaulting a weight, since a silent default is exactly the
    kind of drift this harness exists to prevent.
    """
    if not weights_config:
        return base_signals
    weighted = []
    for sig in base_signals:
        name = sig["signal_name"]
        if name not in weights_config:
            raise ValueError(
                f"weights_config missing weight for signal {name!r}: "
                f"{sorted(weights_config)!r}"
            )
        weighted.append({**sig, "weight": weights_config[name]})
    return weighted


def _capture_suppression_reason(logger_name: str, fn, *args, **kwargs):
    """Call fn(*args, **kwargs), capturing the last WARNING logged by
    `logger_name` during the call.

    compute_momentum_signal() logs its RF-I_* suppression reasons via
    logging.warning() rather than returning them, since its primary caller
    (emit_signal) only needs the None/not-None signal for control flow.
    This harness wants the reason string for bt_backtest_attribution, so it
    observes the log line instead of re-deriving the reason independently
    (which would risk falling out of sync with the real suppression logic —
    the same failure mode this whole retirement is fixing).
    """
    messages: list[str] = []

    class _Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            messages.append(record.getMessage())

    logger = logging.getLogger(logger_name)
    handler = _Capture(level=logging.WARNING)
    logger.addHandler(handler)
    try:
        result = fn(*args, **kwargs)
    finally:
        logger.removeHandler(handler)
    reason = messages[-1] if messages else None
    return result, reason


def _historical_rows(
    supabase, instrument_id: int, start_date: str, end_date: str
) -> list[dict]:
    """Load chronological, non-circuit-locked OHLCV rows for one instrument
    within [start_date, end_date] (inclusive)."""
    rows: list[dict] = []
    page_size = 1000
    while True:
        result = (
            supabase.table("ohlcv")
            .select("trade_date,open,high,low,close,circuit_flag")
            .eq("instrument_id", instrument_id)
            .eq("circuit_flag", False)
            .gte("trade_date", start_date)
            .lte("trade_date", end_date)
            .order("trade_date")
            .range(len(rows), len(rows) + page_size - 1)
            .execute()
        )
        page = result.data or []
        rows.extend(page)
        if len(page) < page_size:
            break
    return [row for row in rows if not row.get("circuit_flag", False)]


def _accuracy_context(supabase, instrument_id: int) -> tuple[int, float, int]:
    """Return (segment_obs, hit_rate, streak_count) — the same calibration
    inputs emit_signal() computes, taken as a single static baseline for the
    whole replay (Phase 0 scope; a walk-forward per-date version is future
    work, not required here). Read-only — never writes."""
    all_preds_r = (
        supabase.table("accuracy_predictions")
        .select("id")
        .eq("instrument_id", instrument_id)
        .execute()
    )
    all_preds = all_preds_r.data or []
    segment_obs = len(all_preds)
    hit_rate = 0.5
    streak_count = 0

    if all_preds:
        pred_ids = [p["id"] for p in all_preds]
        outcomes = (
            supabase.table("accuracy_outcomes")
            .select("hit")
            .in_("prediction_id", pred_ids)
            .execute()
            .data
            or []
        )
        if outcomes:
            hit_rate = sum(1 for o in outcomes if o["hit"]) / len(outcomes)

        from constants import STREAK_WINDOW

        recent = (
            supabase.table("accuracy_outcomes")
            .select("hit")
            .in_("prediction_id", pred_ids)
            .order("id", desc=True)
            .limit(STREAK_WINDOW + 1)
            .execute()
            .data
            or []
        )
        streak_count = sum(1 for o in recent if o["hit"])

    return segment_obs, hit_rate, streak_count


def _replay_instrument(
    rows: list[dict],
    weights_config: dict[str, float],
    segment_obs: int,
    hit_rate: float,
    streak_count: int,
) -> tuple[list[dict], list[dict]]:
    """Walk each date in `rows` as an as-of date, calling the REAL engine
    functions (compute_momentum_signal, emit_pipeline) — never a
    reimplementation. Returns (observations, attribution_rows).

    observations: resolvable, non-suppressed signals with a next-day outcome
    (used for the run's aggregate score).
    attribution_rows: one row per as-of date processed (suppressed or not),
    shaped for bt_backtest_attribution (minus backtest_run_id/instrument_id,
    added by the caller).
    """
    observations: list[dict] = []
    attribution_rows: list[dict] = []

    for index in range(len(rows) - 1):
        window = rows[: index + 1]
        last = window[-1]
        as_of = last.get("trade_date")
        if as_of is None:
            continue

        base_weight = weights_config.get(_SIGNAL_NAME, 1.0)

        signals, suppression_reason = _capture_suppression_reason(
            "src.signals.engine", compute_momentum_signal, window, as_of
        )
        if signals is None:
            attribution_rows.append({
                "trade_date": as_of,
                "signal_name": _SIGNAL_NAME,
                "weight": base_weight,
                "threshold_crossed": False,
                "reason": suppression_reason or "RF-I_SUPPRESSED_UNKNOWN_REASON",
            })
            continue

        weighted_signals = _weighted_signals(signals, weights_config)
        emit_result = emit_pipeline(weighted_signals, streak_count, segment_obs, hit_rate)

        if emit_result is None:
            attribution_rows.append({
                "trade_date": as_of,
                "signal_name": _SIGNAL_NAME,
                "weight": weighted_signals[0]["weight"],
                "threshold_crossed": False,
                "reason": "ARBITRATION_MARGIN_NOT_CLEARED",
            })
            continue

        outcome_close = rows[index + 1].get("close")
        last_close = last.get("close")
        if outcome_close is None or not last_close:
            attribution_rows.append({
                "trade_date": as_of,
                "signal_name": _SIGNAL_NAME,
                "weight": weighted_signals[0]["weight"],
                "threshold_crossed": True,
                "reason": "NO_RESOLVABLE_OUTCOME",
            })
            continue

        actual_return = (outcome_close - last_close) / last_close
        hit = (
            (emit_result["direction"] == "BULL" and actual_return > 0)
            or (emit_result["direction"] == "BEAR" and actual_return < 0)
        )
        observations.append({
            "hit": hit,
            "direction": emit_result["direction"],
            "calibrated_p": emit_result["calibrated_p"],
        })
        attribution_rows.append({
            "trade_date": as_of,
            "signal_name": _SIGNAL_NAME,
            "weight": weighted_signals[0]["weight"],
            "threshold_crossed": True,
            "reason": f"emitted direction={emit_result['direction']} hit={hit}",
        })

    return observations, attribution_rows


def run_backtest_replay(
    supabase,
    weights_config: dict[str, float],
    start_date: str,
    end_date: str,
    instrument_ids: list[int],
    config_label: str = "unlabeled",
    dry_run: bool = False,
) -> dict:
    """Replay historical OHLCV through the real engine logic for each
    instrument/date, and write one bt_backtest_runs row + N
    bt_backtest_attribution rows (unless dry_run=True).

    Never writes to accuracy_predictions or signal_weights — see module
    docstring for the full boundary rationale.
    """
    all_observations: list[dict] = []
    all_attribution_rows: list[dict] = []
    per_instrument_depth: dict[int, int] = {}

    for instrument_id in instrument_ids:
        rows = _historical_rows(supabase, instrument_id, start_date, end_date)
        per_instrument_depth[instrument_id] = len(rows)
        if len(rows) < 2:
            continue

        segment_obs, hit_rate, streak_count = _accuracy_context(supabase, instrument_id)
        observations, attribution_rows = _replay_instrument(
            rows, weights_config, segment_obs, hit_rate, streak_count,
        )
        all_observations.extend(observations)
        for row in attribution_rows:
            row["instrument_id"] = instrument_id
            all_attribution_rows.append(row)

    if all_observations:
        score = sum(1 for o in all_observations if o["hit"]) / len(all_observations)
    else:
        score = None

    data_depth_days = min(per_instrument_depth.values()) if per_instrument_depth else 0
    insufficient_depth = data_depth_days < MIN_ROWS_FOR_BACKTEST

    run_row = {
        "config_label": config_label,
        "weights_config": weights_config,
        "data_depth_days": data_depth_days,
        "insufficient_depth": insufficient_depth,
        "score": score,
        "notes": (
            f"instruments={instrument_ids} start={start_date} end={end_date} "
            f"n_observations={len(all_observations)} "
            f"n_attribution_rows={len(all_attribution_rows)}"
        ),
    }

    result = {
        "run_row": run_row,
        "attribution_rows": all_attribution_rows,
        "backtest_run_id": None,
    }

    if dry_run:
        return result

    inserted_run = supabase.table("bt_backtest_runs").insert(run_row).execute()
    backtest_run_id = inserted_run.data[0]["id"]
    for row in all_attribution_rows:
        row["backtest_run_id"] = backtest_run_id
    if all_attribution_rows:
        supabase.table("bt_backtest_attribution").insert(all_attribution_rows).execute()

    result["backtest_run_id"] = backtest_run_id
    return result


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--weights-config",
        default="{}",
        help='JSON dict, e.g. \'{"momentum_price": 1.5}\'. Empty dict = live baseline weight (1.0).',
    )
    parser.add_argument("--start-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end-date", required=True, help="YYYY-MM-DD")
    parser.add_argument(
        "--instrument-ids", required=True, help="Comma-separated instrument ids, e.g. 4"
    )
    parser.add_argument("--config-label", default="unlabeled")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute the run/attribution rows but do not write to the DB.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    from src.config import get_supabase_client

    supabase = get_supabase_client()
    weights_config = json.loads(args.weights_config)
    instrument_ids = [int(x) for x in args.instrument_ids.split(",") if x.strip()]

    result = run_backtest_replay(
        supabase,
        weights_config=weights_config,
        start_date=args.start_date,
        end_date=args.end_date,
        instrument_ids=instrument_ids,
        config_label=args.config_label,
        dry_run=args.dry_run,
    )

    print(json.dumps({
        "dry_run": args.dry_run,
        "backtest_run_id": result["backtest_run_id"],
        "run_row": result["run_row"],
        "n_attribution_rows": len(result["attribution_rows"]),
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
