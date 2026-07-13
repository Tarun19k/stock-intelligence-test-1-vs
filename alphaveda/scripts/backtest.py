#!/usr/bin/env python3
"""Read-only historical backtest for the live momentum_price signal."""
from __future__ import annotations

import os
import sys
from collections import defaultdict
from statistics import fmean

# Ensure alphaveda/ is on the path when run from the repository root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from dotenv import load_dotenv

    load_dotenv(
        os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
        override=False,
    )
except ImportError:
    pass

from constants import STREAK_WINDOW
from src.config import get_supabase_client
from src.signals.engine import emit_pipeline


def _accuracy_context(supabase, instrument_id: int) -> tuple[int, float, int]:
    """Return the exact per-instrument calibration inputs used by engine.py."""
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
        pred_ids = [prediction["id"] for prediction in all_preds]
        outcomes = (
            supabase.table("accuracy_outcomes")
            .select("hit")
            .in_("prediction_id", pred_ids)
            .execute()
            .data
            or []
        )
        if outcomes:
            hit_rate = sum(1 for outcome in outcomes if outcome["hit"]) / len(outcomes)

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
        streak_count = sum(1 for outcome in recent if outcome["hit"])

    return segment_obs, hit_rate, streak_count


def _historical_rows(supabase, instrument_id: int) -> list[dict]:
    """Load chronological, non-circuit OHLCV rows for one instrument."""
    rows: list[dict] = []
    page_size = 1000
    while True:
        result = (
            supabase.table("ohlcv")
            .select("trade_date,open,high,low,close,circuit_flag")
            .eq("instrument_id", instrument_id)
            .eq("circuit_flag", False)
            .order("trade_date")
            .range(len(rows), len(rows) + page_size - 1)
            .execute()
        )
        page = result.data or []
        rows.extend(page)
        if len(page) < page_size:
            break

    return [row for row in rows if not row.get("circuit_flag", False)]


def _replay_instrument(
    rows: list[dict],
    segment_obs: int,
    hit_rate: float,
    streak_count: int,
) -> list[dict]:
    """Replay the live 21-row momentum rule and score each next clean close."""
    observations: list[dict] = []

    for index in range(len(rows) - 1):
        window = rows[max(0, index - 20): index + 1]
        last = window[-1]
        last_close = last.get("close")
        if last_close is None:
            continue

        if len(window) >= 2:
            ref_close = window[0].get("close")
            if not ref_close or ref_close == 0:
                continue
            ret = (last_close - ref_close) / ref_close
        else:
            ref_open = last.get("open") or last_close
            if not ref_open or ref_open == 0:
                continue
            ret = (last_close - ref_open) / ref_open

        direction = "BULL" if ret >= 0 else "BEAR"
        confidence = min(abs(ret) * 500, 100.0)
        signals = [{
            "direction": direction,
            "confidence": confidence,
            "signal_name": "momentum_price",
            "weight": 1.0,
        }]
        result = emit_pipeline(signals, streak_count, segment_obs, hit_rate)
        if result is None:
            continue

        outcome_close = rows[index + 1].get("close")
        if outcome_close is None or last_close == 0:
            continue
        actual_return = (outcome_close - last_close) / last_close
        hit = (
            (result["direction"] == "BULL" and actual_return > 0)
            or (result["direction"] == "BEAR" and actual_return < 0)
        )
        signal_return = actual_return if result["direction"] == "BULL" else -actual_return

        # calibrate_confidence()'s min(confidence / 100, hit_rate) is a cap, not true calibration, so results cluster near one hit_rate line.
        observations.append({
            "hit": hit,
            "return": signal_return,
            "predicted_confidence": result["calibrated_p"] * 100.0,
        })

    return observations


def _confidence_bucket(confidence: float) -> str:
    lower = min(int(confidence // 10) * 10, 90)
    return f"{lower}-{lower + 10}"


def _print_table(headers: list[str], rows: list[list[str]]) -> None:
    widths = [len(header) for header in headers]
    for row in rows:
        widths = [max(width, len(value)) for width, value in zip(widths, row)]

    print("  ".join(header.ljust(width) for header, width in zip(headers, widths)))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print("  ".join(value.ljust(width) for value, width in zip(row, widths)))


def run_backtest() -> None:
    """Run the backtest and print per-instrument and calibration summaries."""
    supabase = get_supabase_client()
    instruments = (
        supabase.table("instruments")
        .select("id,ticker,classification")
        .eq("is_active", True)
        .order("ticker")
        .execute()
        .data
        or []
    )

    instrument_rows: list[list[str]] = []
    calibration: dict[tuple[str, str], list[bool]] = defaultdict(list)

    for instrument in instruments:
        instrument_id = instrument["id"]
        lynch_class = instrument.get("classification") or "unclassified"
        segment_obs, hit_rate, streak_count = _accuracy_context(supabase, instrument_id)
        historical_rows = _historical_rows(supabase, instrument_id)
        observations = _replay_instrument(
            historical_rows,
            segment_obs,
            hit_rate,
            streak_count,
        )

        if observations:
            backtest_hit_rate = sum(obs["hit"] for obs in observations) / len(observations)
            average_return = fmean(obs["return"] for obs in observations)
            hit_rate_text = f"{backtest_hit_rate:.2%}"
            average_return_text = f"{average_return:.2%}"
        else:
            hit_rate_text = "N/A"
            average_return_text = "N/A"

        instrument_rows.append([
            str(instrument_id),
            instrument.get("ticker") or "",
            lynch_class,
            str(len(observations)),
            hit_rate_text,
            average_return_text,
        ])

        for observation in observations:
            bucket = _confidence_bucket(observation["predicted_confidence"])
            calibration[("ALL", bucket)].append(observation["hit"])
            calibration[(lynch_class, bucket)].append(observation["hit"])

    print("\nPer-instrument results")
    _print_table(
        ["ID", "Ticker", "Lynch class", "Signals", "Hit rate", "Average return"],
        instrument_rows,
    )

    calibration_rows = []
    for (lynch_class, bucket), hits in sorted(calibration.items()):
        calibration_rows.append([
            lynch_class,
            bucket,
            str(len(hits)),
            f"{sum(hits) / len(hits):.2%}",
        ])

    print("\nCalibration curve")
    _print_table(
        ["Lynch class", "Confidence bucket", "Signals", "Actual hit rate"],
        calibration_rows,
    )


if __name__ == "__main__":
    run_backtest()
