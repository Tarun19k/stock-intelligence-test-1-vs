# pages/week_summary.py
# Shown when no stock is selected in the sidebar
# Entry point: render_week_summary(cur_sym, cb)

import pytz
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils import safe_run, responsive_cols
from market_data import get_price_data
from forecast import get_weekly_accuracy_report

# ── Week date range ────────────────────────────────────────────────────────────
def _get_week_range():
    """Return (week_start, week_end, label, is_current) in IST."""
    ist  = pytz.timezone("Asia/Kolkata")
    today = datetime.now(ist).date()
    dow   = today.weekday()          # Mon=0 … Sun=6
    is_weekend = dow >= 5
    if is_weekend:
        # Show last completed week
        week_end   = today - timedelta(days=dow - 4)   # last Friday
        week_start = week_end - timedelta(days=4)       # last Monday
        label = f"Week of {week_start.strftime('%d %b')} – {week_end.strftime('%d %b %Y')} (past week)"
        is_current = False
    else:
        week_start = today - timedelta(days=dow)
        week_end   = today
        label = f"Week of {week_start.strftime('%d %b')} – {week_end.strftime('%d %b %Y')} (current week)"
        is_current = True
    return week_start, week_end, label, is_current


# ── Index performance block ───────────────────────────────────────────────────
INDEX_WATCH = [
    ("Nifty 50",       "^NSEI",    "₹"),
    ("Sensex",         "^BSESN",   "₹"),
    ("Nifty Bank",     "^NSEBANK", "₹"),
    ("S&P 500",        "^GSPC",    "$"),
    ("Nasdaq 100",     "^NDX",     "$"),
    ("Hang Seng",      "^HSI",     "HK$"),
    ("Gold",           "GC=F",     "$"),
    ("Crude Oil WTI",  "CL=F",     "$"),
]

def _index_perf_row(cb: int):
    st.markdown('<p class="section-title">🌐 Index Performance — This Week</p>',
                unsafe_allow_html=True)
    cols = responsive_cols(4)
    col_idx = 0
    for name, sym, csym in INDEX_WATCH:
        df = safe_run(
            lambda s=sym: get_price_data(s, period="1mo", interval="1d",
                                         cache_buster=cb),
            context=f"week:{sym}", default=None,
        )
        if df is None or df.empty or len(df) < 2:
            continue
        week_start, _, _, _ = _get_week_range()
        df_week = df[df.index.date >= week_start]
        if df_week.empty:
            df_week = df.tail(5)
        open_p  = float(df_week["Close"].iloc[0])
        close_p = float(df_week["Close"].iloc[-1])
        chg_pct = (close_p - open_p) / open_p * 100 if open_p else 0
        color   = "#00c853" if chg_pct >= 0 else "#ff1744"
        arrow   = "▲" if chg_pct >= 0 else "▼"
        with cols[col_idx % 4]:
            st.markdown(
                f'<div class="kpi-card" style="border-left-color:{color}">' +
                f'<div class="kpi-label">{name}</div>' +
                f'<div class="kpi-value" style="font-size:1.05rem">{csym}{close_p:,.0f}</div>' +
                f'<div class="kpi-delta" style="color:{color}">{arrow} {abs(chg_pct):.2f}%</div>' +
                f'</div>',
                unsafe_allow_html=True,
            )
        col_idx += 1


# ── Nifty 50 weekly heatmap ───────────────────────────────────────────────────
NIFTY50_TICKERS = [
    ("Reliance",    "RELIANCE.NS"), ("TCS",         "TCS.NS"),
    ("HDFC Bank",   "HDFCBANK.NS"), ("Infosys",     "INFY.NS"),
    ("ICICI Bank",  "ICICIBANK.NS"),("HUL",         "HINDUNILVR.NS"),
    ("ITC",         "ITC.NS"),      ("SBI",         "SBIN.NS"),
    ("Airtel",      "BHARTIARTL.NS"),("Kotak",      "KOTAKBANK.NS"),
    ("L&T",         "LT.NS"),       ("HCL Tech",    "HCLTECH.NS"),
    ("Asian Paints","ASIANPAINT.NS"),("Axis Bank",  "AXISBANK.NS"),
    ("Wipro",       "WIPRO.NS"),    ("Maruti",      "MARUTI.NS"),
    ("Sun Pharma",  "SUNPHARMA.NS"),("Titan",       "TITAN.NS"),
    ("Bajaj Fin",   "BAJFINANCE.NS"),("Nestle",     "NESTLEIND.NS"),
    ("UltraTech",   "ULTRACEMCO.NS"),("NTPC",       "NTPC.NS"),
    ("Power Grid",  "POWERGRID.NS"),("M&M",         "M&M.NS"),
    ("ONGC",        "ONGC.NS"),     ("Divi's",      "DIVISLAB.NS"),
    ("Bajaj Finserv","BAJAJFINSV.NS"),("Dr Reddy",  "DRREDDY.NS"),
    ("Adani Ports", "ADANIPORTS.NS"),("Tata Motors","TMCV.NS"),
]

def _nifty_heatmap(cb: int):
    st.markdown('<p class="section-title">🟩 Nifty 50 — Weekly Returns Heatmap</p>',
                unsafe_allow_html=True)
    week_start, _, _, _ = _get_week_range()
    names, returns = [], []
    for name, sym in NIFTY50_TICKERS:
        df = safe_run(
            lambda s=sym: get_price_data(s, period="1mo", interval="1d",
                                         cache_buster=cb),
            context=f"heatmap:{sym}", default=None,
        )
        if df is None or df.empty or len(df) < 2:
            names.append(name); returns.append(0.0); continue
        df_w = df[df.index.date >= week_start]
        if df_w.empty: df_w = df.tail(5)
        o = float(df_w["Close"].iloc[0])
        c = float(df_w["Close"].iloc[-1])
        returns.append(round((c - o) / o * 100 if o else 0, 2))
        names.append(name)

    # 5-column treemap-style bar
    fig = go.Figure(go.Bar(
        x=names, y=returns,
        marker_color=["#00c853" if r >= 0 else "#ff1744" for r in returns],
        text=[f"{r:+.1f}%" for r in returns],
        textposition="outside",
    ))
    fig.update_layout(
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font_color="#9aa0b4", height=320,
        yaxis=dict(title="Weekly Return %", gridcolor="#1f2540",
                   zeroline=True, zerolinecolor="#4b6080"),
        xaxis=dict(gridcolor="#1f2540"),
        margin=dict(l=10, r=10, t=20, b=60),
        showlegend=False,
    )
    fig.update_traces(cliponaxis=False)
    st.plotly_chart(fig, width='stretch', config={"responsive": True})


# ── Sector performance mini-cards ─────────────────────────────────────────────
SECTOR_PROXIES = [
    ("IT",       "^CNXIT"),
    ("Bank",     "^NSEBANK"),
    ("Pharma",   "^CNXPHARMA"),
    ("Auto",     "^CNXAUTO"),
    ("FMCG",     "^CNXFMCG"),
    ("Metal",    "^CNXMETAL"),
    ("Energy",   "^CNXENERGY"),
    ("Realty",   "^CNXREALTY"),
]

def _sector_cards(cb: int):
    st.markdown('<p class="section-title">📊 Sector Snapshot</p>',
                unsafe_allow_html=True)
    week_start, _, _, _ = _get_week_range()
    cols = responsive_cols(len(SECTOR_PROXIES))
    for col, (name, sym) in zip(cols, SECTOR_PROXIES):
        df = safe_run(
            lambda s=sym: get_price_data(s, period="1mo", interval="1d",
                                         cache_buster=cb),
            context=f"sector:{sym}", default=None,
        )
        if df is None or df.empty or len(df) < 2:
            col.markdown(
                f'<div class="kpi-card"><div class="kpi-label">{name}</div>' +
                '<div class="kpi-delta">—</div></div>',
                unsafe_allow_html=True,
            )
            continue
        df_w = df[df.index.date >= week_start]
        if df_w.empty: df_w = df.tail(5)
        o = float(df_w["Close"].iloc[0])
        c = float(df_w["Close"].iloc[-1])
        chg = (c - o) / o * 100 if o else 0
        color = "#00c853" if chg >= 0 else "#ff1744"
        arr   = "▲" if chg >= 0 else "▼"
        col.markdown(
            f'<div class="kpi-card" style="border-left-color:{color}">' +
            f'<div class="kpi-label">Nifty {name}</div>' +
            f'<div class="kpi-delta" style="color:{color}">{arr} {abs(chg):.2f}%</div>' +
            f'</div>',
            unsafe_allow_html=True,
        )


# ── Weekly Nifty 50 line chart ────────────────────────────────────────────────
def _nifty_weekly_chart(cb: int):
    st.markdown('<p class="section-title">📈 Nifty 50 — Week in Charts</p>',
                unsafe_allow_html=True)
    df = safe_run(
        lambda: get_price_data("^NSEI", period="1mo", interval="1d",
                               cache_buster=cb),
        context="week_chart:nifty", default=None,
    )
    df_b = safe_run(
        lambda: get_price_data("^NSEBANK", period="1mo", interval="1d",
                               cache_buster=cb),
        context="week_chart:banknifty", default=None,
    )
    week_start, _, _, _ = _get_week_range()

    fig = go.Figure()
    for data, name, color in [
        (df,  "Nifty 50",   "#4f8ef7"),
        (df_b,"Bank Nifty", "#ffd600"),
    ]:
        if data is None or data.empty: continue
        d = data[data.index.date >= week_start]
        if d.empty: d = data.tail(5)
        _clw = d["Close"].iloc[:,0] if isinstance(d["Close"], pd.DataFrame) else d["Close"]
        norm = _clw / _clw.iloc[0] * 100 if not _clw.empty else _clw
        fig.add_trace(go.Scatter(
            x=d.index, y=norm,
            line=dict(color=color, width=2.5), name=name,
        ))
    fig.update_layout(
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font_color="#9aa0b4", height=280,
        yaxis=dict(title="Indexed (open = 100)", gridcolor="#1f2540"),
        xaxis=dict(gridcolor="#1f2540"),
        legend=dict(orientation="h", y=1.08),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    st.plotly_chart(fig, width='stretch', config={"responsive": True})


# ── Main entry ────────────────────────────────────────────────────────────────
def render_week_summary(cur_sym: str = "₹", cb: int = 0):
    _, _, week_label, is_current = _get_week_range()
    tag = "📅 Current Week" if is_current else "📅 Past Week"

    st.markdown(
        f'<div style="font-size:1.6rem;font-weight:900;color:#c8d6f0">' +
        f'📊 The Week That Was</div>' +
        f'<div style="font-size:0.84rem;color:#4b6080;margin-bottom:6px">' +
        f'{tag} · {week_label}</div>' +
        f'<div class="insight-box" style="font-size:0.84rem;margin-bottom:20px">' +
        f'Select a stock from the sidebar to open its full dashboard — ' +
        f'price charts, technical signals, forecast, and news.</div>',
        unsafe_allow_html=True,
    )
    _index_perf_row(cb)
    st.divider()
    _nifty_weekly_chart(cb)
    st.divider()
    _sector_cards(cb)
    st.divider()
    _nifty_heatmap(cb)
    st.divider()
    _render_forecast_accuracy_report()


# ── Forecast Engine Weekly Accuracy Report ────────────────────────────────────
def _render_forecast_accuracy_report():
    """
    Weekly calibration report for the Historical Simulation forecast engine.
    Shown at end-of-week on the Week Summary page.
    Tracks:
      - Directional accuracy (did P(gain) predict direction correctly?)
      - Band calibration (did outcomes land inside P25-P75 and P10-P90?)
      - Mean price accuracy (how close was P50 to actual?)
    """
    st.markdown('<p class="section-title">🎯 Forecast Engine — Weekly Accuracy Report</p>',
                unsafe_allow_html=True)

    report = safe_run(get_weekly_accuracy_report,
                      context="week:forecast_report", default={"count": 0})

    if not report or report.get("count", 0) == 0:
        st.markdown(
            '<div class="insight-box" style="font-size:0.84rem">'
            '📊 No resolved forecasts yet this cycle. Accuracy data builds as '
            'forecast due-dates pass. Check back end-of-week after forecasts made '
            'on Monday have resolved.</div>',
            unsafe_allow_html=True,
        )
        return

    count    = report["count"]
    dir_acc  = report.get("dir_accuracy")
    b2575    = report.get("band_25_75_hit")
    b1090    = report.get("band_10_90_hit")
    mean_acc = report.get("mean_accuracy")
    exp_2575 = report.get("expected_25_75", 50.0)
    exp_1090 = report.get("expected_10_90", 80.0)
    exp_dir  = report.get("expected_dir", 55.0)

    # ── KPI row ───────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)

    def _kpi_card(col, label, val, target, unit="%", invert=False):
        if val is None:
            col.markdown(
                f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
                f'<div class="kpi-value">—</div></div>',
                unsafe_allow_html=True)
            return
        ok    = val >= target if not invert else val <= target
        color = "#00c853" if ok else "#ff9800"
        delta = val - target
        col.markdown(
            f'<div class="kpi-card" style="border-left-color:{color}">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value" style="font-size:1.3rem">{val:.1f}{unit}</div>'
            f'<div class="kpi-delta" style="color:{color}">'
            f'Target {target:.0f}{unit} ({delta:+.1f})</div>'
            f'</div>', unsafe_allow_html=True)

    _kpi_card(c1, "Resolved Forecasts", count, 1, unit="")
    _kpi_card(c2, "Direction Accuracy", dir_acc, exp_dir)
    _kpi_card(c3, "P25–P75 Hit Rate",   b2575,   exp_2575)
    _kpi_card(c4, "P10–P90 Hit Rate",   b1090,   exp_1090)

    # ── Calibration explanation ───────────────────────────────────
    notes = []
    if dir_acc is not None:
        if dir_acc >= exp_dir:
            notes.append(f"✅ Direction accuracy {dir_acc:.1f}% beats random (target >{exp_dir:.0f}%). "
                         f"P(gain) signal is adding real value.")
        else:
            notes.append(f"⚠️ Direction accuracy {dir_acc:.1f}% is near-random (target >{exp_dir:.0f}%). "
                         f"More resolved forecasts needed for reliable signal.")

    if b2575 is not None:
        if 40 <= b2575 <= 65:
            notes.append(f"✅ P25–P75 band captured {b2575:.1f}% of outcomes "
                         f"(well-calibrated — target ~50%).")
        elif b2575 < 40:
            notes.append(f"⚠️ P25–P75 captured only {b2575:.1f}% — bands may be too narrow. "
                         f"Volatility is higher than history suggested.")
        else:
            notes.append(f"ℹ️ P25–P75 captured {b2575:.1f}% — bands may be slightly wide.")

    if b1090 is not None:
        if b1090 >= 70:
            notes.append(f"✅ P10–P90 band captured {b1090:.1f}% of outcomes (target >70%).")
        else:
            notes.append(f"⚠️ P10–P90 captured only {b1090:.1f}% — model is underestimating tail risk.")

    for note in notes:
        color = "#00c85322" if note.startswith("✅") else "#ff980022" if note.startswith("⚠️") else "#1a2332"
        border = "#00c853" if note.startswith("✅") else "#ff9800" if note.startswith("⚠️") else "#2d3a5e"
        st.markdown(
            f'<div style="background:{color};border-left:3px solid {border};'
            f'border-radius:6px;padding:10px 14px;margin:5px 0;'
            f'font-size:0.82rem;color:#c8d6f0">{note}</div>',
            unsafe_allow_html=True)

    # ── Recent entries table ──────────────────────────────────────
    entries = report.get("entries", [])
    if entries:
        import pandas as pd
        rows = []
        for e in entries[:10]:
            rows.append({
                "Ticker":    e.get("_key", "").replace("_63d","").replace("_21d",""),
                "Made":      e.get("made_on",""),
                "Horizon":   f'{e.get("horizon_days",63)}d',
                "P50 Fcst":  f'{e.get("forecast_price",""):.2f}' if e.get("forecast_price") else "—",
                "Actual":    f'{e.get("actual_price",""):.2f}' if e.get("actual_price") else "—",
                "P(gain)":   f'{e.get("p_gain",""):.0f}%' if e.get("p_gain") is not None else "—",
                "Direction": "✅" if e.get("direction_correct") else "❌" if e.get("direction_correct") is False else "—",
                "In Band":   "✅" if e.get("in_p25_p75") else "❌" if e.get("in_p25_p75") is False else "—",
                "Accuracy":  f'{e.get("accuracy_pct",""):.1f}%' if e.get("accuracy_pct") is not None else "—",
            })
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
