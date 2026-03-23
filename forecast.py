# forecast.py
# Depends on: config, utils
# Called from: pages/dashboard.py (Forecast tab)
# Contains: store_forecast, resolve_forecasts, accuracy summary, render panel
#
# FIX (v5.16): Replaced filesystem-only persistence with st.session_state as
# the primary store. On Streamlit Cloud the filesystem is ephemeral and wiped
# on every redeploy, silently deleting all forecast history.
#
# New behaviour:
#   - session_state is the live store — persists for the duration of a user session.
#   - On first access per session, seeds from forecast_history.json if the file
#     exists (works in local dev; silent no-op on cloud where the file is absent).
#   - Writes back to disk after every mutation so local dev retains history
#     across restarts (cloud write fails silently — that's fine).
#   - All callers (store_forecast, resolve_forecasts, etc.) are unchanged in
#     signature — this is a pure internal storage swap.
#
# FIX (v5.16): KI-021 guard — render_forecast_accuracy now validates that
# the ticker argument is non-empty before querying history.

import os
import json
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from config import FORECAST_STORE_FILE
from utils import log_error, safe_ticker_key, safe_run

# Session-state key used as the live store
_SS_KEY = "forecast_history"


# ── Storage helpers ───────────────────────────────────────────────────────────

def load_forecast_history() -> dict:
    """
    Return the forecast history dict.
    Primary store: st.session_state[_SS_KEY].
    On first call per session, seeds from disk if the JSON file exists.
    """
    if _SS_KEY not in st.session_state:
        data: dict = {}
        if os.path.exists(FORECAST_STORE_FILE):
            try:
                with open(FORECAST_STORE_FILE, encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                log_error("forecast:load_seed", e)
        st.session_state[_SS_KEY] = data
    return st.session_state[_SS_KEY]


def save_forecast_history(data: dict) -> None:
    """
    Persist the forecast history dict.
    Always writes to session_state (works on cloud + local).
    Also tries to write to disk — succeeds in local dev, silent no-op on cloud.
    """
    st.session_state[_SS_KEY] = data
    try:
        with open(FORECAST_STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass  # Cloud: ephemeral FS — session_state is the source of truth


# ── Forecast CRUD ─────────────────────────────────────────────────────────────

def store_forecast(ticker: str, horizon_days: int,
                   forecast_price: float, current_price: float,
                   simulation: dict = None) -> dict:
    """
    Record a new forecast entry (one per ticker per day).
    simulation: optional dict from compute_forecast() — stores full
    percentile distribution for weekly accuracy tracking.
    """
    if not ticker:
        return {}
    history = load_forecast_history()
    key = f"{safe_ticker_key(ticker)}_{horizon_days}d"
    if key not in history:
        history[key] = []

    today = datetime.now().strftime("%Y-%m-%d")
    # One entry per day — no duplicates
    if any(e["made_on"] == today for e in history[key]):
        return history

    # OBS-006 / KI-021: clamp to 0.01
    forecast_price = max(forecast_price, 0.01)

    entry = {
        "made_on":        today,
        "due_on":         (datetime.now() + timedelta(days=horizon_days)).strftime("%Y-%m-%d"),
        "horizon_days":   horizon_days,
        "forecast_price": round(forecast_price, 2),
        "base_price":     round(current_price, 2),
        "actual_price":   None,
        "accuracy_pct":   None,
        "resolved":       False,
        "method":         "historical_simulation_v1",
        # Full distribution — enables proper accuracy tracking
        "p10":     simulation.get("p10")    if simulation else None,
        "p25":     simulation.get("p25")    if simulation else None,
        "p75":     simulation.get("p75")    if simulation else None,
        "p90":     simulation.get("p90")    if simulation else None,
        "p_gain":  simulation.get("p_gain") if simulation else None,
        # Resolution tracking fields (set on resolve)
        "in_p25_p75": None,  # was actual in the central band?
        "in_p10_p90": None,  # was actual in the wide band?
        "direction_correct": None,  # did we get the direction right?
    }
    history[key].append(entry)
    save_forecast_history(history)
    return history


def resolve_forecasts(ticker: str, current_price: float) -> dict:
    """
    Check all pending forecasts whose due date has passed and mark them
    resolved with accuracy. Computes calibration fields for weekly report.
    """
    if not ticker:
        return {}
    history = load_forecast_history()
    today   = datetime.now().strftime("%Y-%m-%d")
    changed = False
    prefix  = safe_ticker_key(ticker) + "_"

    for key, entries in history.items():
        if not key.startswith(prefix):
            continue
        for e in entries:
            if e["resolved"] or e["due_on"] > today:
                continue
            fp = e["forecast_price"]
            if not fp:
                continue
            pct_err = abs(current_price - fp) / fp * 100
            e["actual_price"]      = round(current_price, 2)
            e["accuracy_pct"]      = round(max(0.0, 100.0 - pct_err), 2)
            e["resolved"]          = True
            # Calibration: was actual within confidence bands?
            p25 = e.get("p25"); p75 = e.get("p75")
            p10 = e.get("p10"); p90 = e.get("p90")
            if p25 is not None and p75 is not None:
                e["in_p25_p75"] = bool(p25 <= current_price <= p75)
            if p10 is not None and p90 is not None:
                e["in_p10_p90"] = bool(p10 <= current_price <= p90)
            # Direction: did P(gain) predict correctly?
            p_gain = e.get("p_gain")
            base   = e.get("base_price", fp)
            if p_gain is not None and base:
                predicted_up = p_gain >= 50
                actually_up  = current_price >= base
                e["direction_correct"] = bool(predicted_up == actually_up)
            changed = True

    if changed:
        save_forecast_history(history)
    return history


def compute_correction_factor(ticker: str, min_entries: int = 3) -> float:
    """
    Auto-correction factor.
    If mean accuracy < 95 %, return the mean of actual/forecast ratios so
    callers can scale new forecasts. Returns 1.0 if insufficient history.
    """
    if not ticker:
        return 1.0
    history  = load_forecast_history()
    resolved = []
    prefix   = safe_ticker_key(ticker) + "_"

    for key, entries in history.items():
        if not key.startswith(prefix):
            continue
        for e in entries:
            if e["resolved"] and e["actual_price"] and e["forecast_price"]:
                resolved.append(e["actual_price"] / e["forecast_price"])

    if len(resolved) < min_entries:
        return 1.0

    mean_accuracy = sum(
        max(0, 100 - abs(r - 1) * 100) for r in resolved
    ) / len(resolved)

    if mean_accuracy >= 95.0:
        return 1.0

    return round(sum(resolved) / len(resolved), 4)


def get_accuracy_summary(ticker: str) -> dict:
    """Return accuracy stats dict for display in the Forecast tab."""
    if not ticker:
        return {"count": 0, "mean_accuracy": None, "correction_factor": 1.0, "entries": []}

    history      = load_forecast_history()
    all_resolved = []
    prefix       = safe_ticker_key(ticker) + "_"

    for key, entries in history.items():
        if key.startswith(prefix):
            all_resolved += [e for e in entries if e["resolved"]]

    if not all_resolved:
        return {"count": 0, "mean_accuracy": None, "correction_factor": 1.0, "entries": []}

    accs   = [e["accuracy_pct"] for e in all_resolved if e["accuracy_pct"] is not None]
    mean_a = round(sum(accs) / len(accs), 2) if accs else None

    return {
        "count":             len(all_resolved),
        "mean_accuracy":     mean_a,
        "correction_factor": compute_correction_factor(ticker),
        "entries":           all_resolved[-10:],
    }


# ── Render ────────────────────────────────────────────────────────────────────

def render_forecast_accuracy(ticker: str, cur_sym: str) -> None:
    """
    Render the Forecast Accuracy Tracker panel.
    Only function in this module that calls st.*.
    """
    st.markdown("### 📏 Forecast Accuracy Tracker")

    if not ticker:
        st.info("No ticker selected.")
        return

    acc = get_accuracy_summary(ticker)

    if acc["count"] == 0:
        st.info(
            "No resolved forecasts yet for this stock. "
            "Accuracy data builds up over time as forecast due-dates pass."
        )
        return

    mean_a = acc["mean_accuracy"] or 0
    cf     = acc["correction_factor"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Resolved Forecasts", acc["count"])
    c2.metric(
        "Mean Accuracy", f"{mean_a:.1f}%",
        delta="✅ No correction needed" if mean_a >= 95 else "⚠️ Auto-correction ON",
    )
    c3.metric(
        "Correction Factor", f"{cf:.4f}",
        delta="1.0000 = perfect" if cf == 1.0 else f"{'▲' if cf > 1 else '▼'} applied to forecasts",
    )

    if mean_a < 95:
        st.warning(
            f"⚙️ **Auto-correction active** — past forecasts averaged "
            f"**{mean_a:.1f}% accuracy** (target: 95%). "
            f"Correction factor **{cf:.4f}×** is being applied to today's forecast."
        )
    else:
        st.success(
            f"✅ Forecast accuracy is **{mean_a:.1f}%** — "
            f"above 95% threshold. No correction applied."
        )

    rows = [
        {
            "Made On":  e["made_on"],
            "Due On":   e["due_on"],
            "Forecast": f"{cur_sym}{e['forecast_price']:,.2f}",
            "Actual":   f"{cur_sym}{e['actual_price']:,.2f}" if e["actual_price"] else "—",
            "Accuracy": f"{e['accuracy_pct']:.1f}%" if e["accuracy_pct"] is not None else "—",
        }
        for e in reversed(acc["entries"])
    ]
    if rows:
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


# ── Weekly accuracy report ─────────────────────────────────────────────────

def get_weekly_accuracy_report() -> dict:
    """
    Aggregate all resolved forecasts across all tickers.
    Returns calibration stats for the weekly summary page.

    Tracks:
      - Directional accuracy: did P(gain)>=50% predict direction correctly?
      - Band calibration: what % of actuals landed in P25-P75 and P10-P90?
      - Mean accuracy: how close was P50 to actual price?
    """
    history = load_forecast_history()
    resolved = []

    for key, entries in history.items():
        for e in entries:
            if e.get("resolved") and e.get("actual_price") is not None:
                resolved.append({**e, "_key": key})

    if not resolved:
        return {"count": 0, "entries": []}

    # Compute aggregate stats
    direction_results = [e for e in resolved if e.get("direction_correct") is not None]
    band_25_75        = [e for e in resolved if e.get("in_p25_p75") is not None]
    band_10_90        = [e for e in resolved if e.get("in_p10_p90") is not None]
    accuracy_vals     = [e["accuracy_pct"] for e in resolved
                         if e.get("accuracy_pct") is not None]

    dir_accuracy = (
        round(sum(e["direction_correct"] for e in direction_results)
              / len(direction_results) * 100, 1)
        if direction_results else None
    )
    band_25_75_hit = (
        round(sum(e["in_p25_p75"] for e in band_25_75)
              / len(band_25_75) * 100, 1)
        if band_25_75 else None
    )
    band_10_90_hit = (
        round(sum(e["in_p10_p90"] for e in band_10_90)
              / len(band_10_90) * 100, 1)
        if band_10_90 else None
    )
    mean_accuracy = round(sum(accuracy_vals) / len(accuracy_vals), 1) if accuracy_vals else None

    # Expected calibration targets:
    #   P25-P75 band should capture ~50% of outcomes
    #   P10-P90 band should capture ~80% of outcomes
    #   Direction accuracy: random = 50%, good model > 55%

    return {
        "count":            len(resolved),
        "dir_accuracy":     dir_accuracy,
        "band_25_75_hit":   band_25_75_hit,
        "band_10_90_hit":   band_10_90_hit,
        "mean_accuracy":    mean_accuracy,
        "expected_25_75":   50.0,   # theoretical target
        "expected_10_90":   80.0,   # theoretical target
        "expected_dir":     55.0,   # target: beat random by 5%
        "entries":          sorted(resolved, key=lambda x: x["made_on"], reverse=True)[:20],
    }
