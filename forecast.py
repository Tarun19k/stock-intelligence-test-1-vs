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
                   forecast_price: float, current_price: float) -> dict:
    """Record a new forecast entry (one per ticker per day)."""
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

    history[key].append({
        "made_on":       today,
        "due_on":        (datetime.now() + timedelta(days=horizon_days)).strftime("%Y-%m-%d"),
        "horizon_days":  horizon_days,
        "forecast_price": round(forecast_price, 2),
        "base_price":    round(current_price, 2),
        "actual_price":  None,
        "accuracy_pct":  None,
        "resolved":      False,
    })
    save_forecast_history(history)
    return history


def resolve_forecasts(ticker: str, current_price: float) -> dict:
    """
    Check all pending forecasts whose due date has passed and mark them
    resolved with accuracy. Idempotent — already-resolved entries are skipped.
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
            e["actual_price"] = round(current_price, 2)
            e["accuracy_pct"] = round(max(0.0, 100.0 - pct_err), 2)
            e["resolved"]     = True
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
