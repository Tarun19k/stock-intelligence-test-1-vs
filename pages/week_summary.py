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
            lambda s=sym: get_price_data(s, period="1mo", interval="1d"),
            context=f"week:{sym}", default=None
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
            lambda s=sym: get_price_data(s, period="1mo", interval="1d"),
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
            lambda s=sym: get_price_data(s, period="1mo", interval="1d"),
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
        lambda: get_price_data("^NSEI", period="1mo", interval="1d"),
        context="week_chart:nifty", default=None,
    )
    df_b = safe_run(
        lambda: get_price_data("^NSEBANK", period="1mo", interval="1d"),
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
