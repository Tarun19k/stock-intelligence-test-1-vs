# forecast.py
# Depends on: config, utils
# Called from: pages/dashboard.py (Forecast tab)
# Contains: store_forecast, resolve_forecasts, accuracy summary, render panel
# NOTE: render_forecast_accuracy is the only function here that calls st.*

import os
import json
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from config import FORECAST_STORE_FILE
from utils import log_error, safe_ticker_key, safe_run


def load_forecast_history() -> dict:
    if os.path.exists(FORECAST_STORE_FILE):
        try:
            with open(FORECAST_STORE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_forecast_history(data: dict):
    try:
        with open(FORECAST_STORE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log_error("save_forecast_history", e)


def store_forecast(ticker: str, horizon_days: int, forecast_price: float, current_price: float) -> dict:
    history = load_forecast_history()
    key = f"{safe_ticker_key(ticker)}_{horizon_days}d"
    if key not in history:
        history[key] = []
    entry = {
        "made_on":        datetime.now().strftime("%Y-%m-%d"),
        "due_on":         (datetime.now() + timedelta(days=horizon_days)).strftime("%Y-%m-%d"),
        "horizon_days":   horizon_days,
        "forecast_price": round(forecast_price, 2),
        "base_price":     round(current_price, 2),
        "actual_price":   None,
        "accuracy_pct":   None,
        "resolved":       False,
    }
    today = datetime.now().strftime("%Y-%m-%d")
    if not any(e["made_on"] == today for e in history[key]):
        history[key].append(entry)
    save_forecast_history(history)
    return history


def resolve_forecasts(ticker: str, current_price: float) -> dict:
    history = load_forecast_history()
    today = datetime.now().strftime("%Y-%m-%d")
    changed = False
    for key, entries in history.items():
        if not key.startswith(safe_ticker_key(ticker) + "_"):
            continue
        for e in entries:
            if not e["resolved"] and e["due_on"] <= today:
                actual = current_price
                e["actual_price"]  = round(actual, 2)
                pct_err            = abs(actual - e["forecast_price"]) / e["forecast_price"] * 100
                e["accuracy_pct"]  = round(max(0, 100 - pct_err), 2)
                e["resolved"]      = True
                changed = True
    if changed:
        save_forecast_history(history)
    return history


def compute_correction_factor(ticker: str, min_entries: int = 3) -> float:
    history = load_forecast_history()
    resolved = []
    for key, entries in history.items():
        if not key.startswith(safe_ticker_key(ticker) + "_"):
            continue
        for e in entries:
            if e["resolved"] and e["actual_price"] and e["forecast_price"]:
                resolved.append(e["actual_price"] / e["forecast_price"])
    if len(resolved) < min_entries:
        return 1.0
    mean_accuracy = sum(max(0, 100 - abs(r - 1) * 100) for r in resolved) / len(resolved)
    if mean_accuracy >= 95.0:
        return 1.0
    return round(sum(resolved) / len(resolved), 4)


def get_accuracy_summary(ticker: str) -> dict:
    history = load_forecast_history()
    all_resolved = []
    for key, entries in history.items():
        if not key.startswith(safe_ticker_key(ticker) + "_"):
            continue
        all_resolved += [e for e in entries if e["resolved"]]
    if not all_resolved:
        return {"count": 0, "mean_accuracy": None, "correction_factor": 1.0, "entries": []}
    accs   = [e["accuracy_pct"] for e in all_resolved if e["accuracy_pct"] is not None]
    mean_a = round(sum(accs) / len(accs), 2) if accs else None
    return {
        "count":            len(all_resolved),
        "mean_accuracy":    mean_a,
        "correction_factor": compute_correction_factor(ticker),
        "entries":          all_resolved[-10:],
    }


def render_forecast_accuracy(ticker: str, cur_sym: str):
    """Render accuracy tracking panel — only function here that calls st.*"""
    acc = get_accuracy_summary(ticker)
    st.markdown("### 📏 Forecast Accuracy Tracker")
    if acc["count"] == 0:
        st.info("No resolved forecasts yet. Accuracy data builds as forecast due-dates pass.")
        return
    mean_a = acc["mean_accuracy"] or 0
    cf     = acc["correction_factor"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Resolved Forecasts", acc["count"])
    c2.metric("Mean Accuracy", f"{mean_a:.1f}%",
              delta="✅ No correction needed" if mean_a >= 95 else "⚠️ Auto-correction ON")
    c3.metric("Correction Factor", f"{cf:.4f}",
              delta="1.0000 = perfect" if cf == 1.0 else f"{'▲' if cf > 1 else '▼'} applied to forecasts")
    if mean_a < 95:
        st.warning(f"⚙️ Auto-correction active — past forecasts averaged **{mean_a:.1f}%** accuracy. "
                   f"Correction factor **{cf:.4f}×** applied to today's forecast.")
    else:
        st.success(f"✅ Forecast accuracy is **{mean_a:.1f}%** — above 95% threshold. No correction applied.")
    rows = [{"Made On": e["made_on"], "Due On": e["due_on"],
             "Forecast": f"{cur_sym}{e['forecast_price']:,.2f}",
             "Actual":   f"{cur_sym}{e['actual_price']:,.2f}" if e["actual_price"] else "—",
             "Accuracy": f"{e['accuracy_pct']:.1f}%" if e["accuracy_pct"] is not None else "—"}
            for e in reversed(acc["entries"])]
    if rows:
        st.dataframe(pd.DataFrame(rows), width='stretch', hide_index=True)
