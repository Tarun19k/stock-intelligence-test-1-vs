# pages/week_summary.py
# Shown when no stock is selected in the sidebar
# Entry point: render_week_summary(cur_sym, cb)

import pytz
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils import safe_run, responsive_cols
from market_data import get_price_data, get_batch_data
from forecast import get_weekly_accuracy_report, get_pending_forecast_summary
from portfolio import (compute_log_returns, winsorize_returns,
                       bootstrap_scenarios, optimise_mean_cvar,
                       compute_efficient_frontier, detect_stress_regime,
                       check_regime_conflicts, N_SCENARIOS,
                       CVXPY_AVAILABLE, RISK_AVERSION)

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

@st.fragment
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

@st.fragment
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
    st.plotly_chart(fig, config={"responsive": True})


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

@st.fragment
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
@st.fragment
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
    st.plotly_chart(fig, config={"responsive": True})


# ── Main entry ────────────────────────────────────────────────────────────────
def render_week_summary(cur_sym: str = "₹", cb: int = 0):
    """
    Default view — no market selected.
    Shows a broad cross-market weekly pulse: global indices, multi-asset
    performance, Indian market heatmap, sector rotation, and forecast tracker.
    """
    _, _, week_label, is_current = _get_week_range()
    tag      = "📅 Current Week" if is_current else "📅 Past Week"
    ist      = pytz.timezone("Asia/Kolkata")
    now_str  = datetime.now(ist).strftime("%d %b %Y, %I:%M %p IST")

    # ── Hero header ───────────────────────────────────────────────
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#0d1117,#111827);'
        f'border-radius:14px;padding:22px 28px 16px;margin-bottom:16px;'
        f'border:1px solid #1f2d40">'
        f'<div style="font-size:0.72rem;color:#4b6080;margin-bottom:4px;'
        f'letter-spacing:1px;text-transform:uppercase">{tag}</div>'
        f'<div style="font-size:2rem;font-weight:900;color:#c8d6f0;margin-bottom:4px">'
        f'📊 The Week That Was</div>'
        f'<div style="font-size:0.84rem;color:#4b6080;margin-bottom:10px">'
        f'{week_label} · as of {now_str}</div>'
        f'<div style="font-size:0.82rem;color:#9aa0b4;line-height:1.6">'
        f'👈 Select a <b>Market</b> from the sidebar for a market-level overview · '
        f'Select a <b>Group</b> to see sector performance · '
        f'Select a <b>Stock</b> for the full dashboard</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Section 1: Global pulse ───────────────────────────────────
    _index_perf_row(cb)
    st.divider()

    # ── Section 2: Multi-asset weekly performance chart ───────────
    _multi_asset_weekly_chart(cb)
    st.divider()

    # ── Section 3: Indian market deep-dive ───────────────────────
    st.markdown('<p class="section-title">🇮🇳 Indian Market — Weekly Breakdown</p>',
                unsafe_allow_html=True)
    _sector_cards(cb)
    st.divider()
    _nifty_weekly_chart(cb)
    st.divider()
    _nifty_heatmap(cb)
    st.divider()

    # ── Section 4: Forecast engine tracker ───────────────────────
    _render_forecast_accuracy_report()



# ─────────────────────────────────────────────────────────────────
# NEW: Multi-asset weekly performance chart (replaces Nifty-only)
# ─────────────────────────────────────────────────────────────────
@st.fragment
def _multi_asset_weekly_chart(cb: int):
    """Stacked bar chart comparing weekly % returns across asset classes."""
    st.markdown('<p class="section-title">🌐 Multi-Asset Weekly Performance</p>',
                unsafe_allow_html=True)

    week_start, _, _, _ = _get_week_range()
    assets = [
        ("Nifty 50",       "^NSEI",   "Indian Equities"),
        ("S&P 500",        "^GSPC",   "US Equities"),
        ("Nasdaq 100",     "^NDX",    "US Equities"),
        ("FTSE 100",       "^FTSE",   "EU Equities"),
        ("Hang Seng",      "^HSI",    "Asia Equities"),
        ("Gold",           "GC=F",    "Commodities"),
        ("Crude Oil",      "CL=F",    "Commodities"),
        ("US 10Y Yield",   "^TNX",    "Rates"),
    ]

    names, returns, categories = [], [], []
    for name, sym, cat in assets:
        df = safe_run(
            lambda s=sym: get_price_data(s, period="1mo", interval="1d", cache_buster=cb),
            context=f"multi_asset:{sym}", default=None,
        )
        if df is None or df.empty or len(df) < 2:
            continue
        df_w = df[df.index.date >= week_start]
        if df_w.empty:
            df_w = df.tail(5)
        o = float(df_w["Close"].iloc[0])
        c = float(df_w["Close"].iloc[-1])
        ret = round((c - o) / o * 100 if o else 0, 2)
        names.append(name)
        returns.append(ret)
        categories.append(cat)

    if not names:
        st.info("Multi-asset data temporarily unavailable.")
        return

    cat_colors = {
        "Indian Equities": "#4f8ef7",
        "US Equities":     "#7c3aed",
        "EU Equities":     "#0891b2",
        "Asia Equities":   "#0d9488",
        "Commodities":     "#d97706",
        "Rates":           "#6b7280",
    }

    fig = go.Figure()
    for cat in dict.fromkeys(categories):
        idx = [i for i, c in enumerate(categories) if c == cat]
        fig.add_trace(go.Bar(
            x=[names[i] for i in idx],
            y=[returns[i] for i in idx],
            name=cat,
            marker_color=cat_colors.get(cat, "#6b7280"),
            text=[f"{returns[i]:+.1f}%" for i in idx],
            textposition="outside",
        ))

    fig.update_layout(
        template="plotly_dark", height=320,
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(color="#9aa0b4"),
        barmode="group",
        legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center"),
        yaxis=dict(title="Weekly Return %", gridcolor="#1f2540",
                   zeroline=True, zerolinecolor="#4b6080"),
        xaxis=dict(gridcolor="#1f2540"),
        margin=dict(l=10, r=10, t=30, b=40),
    )
    fig.update_traces(cliponaxis=False)
    st.plotly_chart(fig, config={"responsive": True})


# ─────────────────────────────────────────────────────────────────
# NEW: render_market_overview  — State 2
# Market selected, no stock. Shows all groups + top movers per group.
# ─────────────────────────────────────────────────────────────────
def render_market_overview(country: str, groups: dict,
                            cur_sym: str = "$", cb: int = 0):
    """
    Market-level overview: one card per group showing weekly performance
    of the group, top movers, and a breadth indicator.
    """
    _, _, week_label, is_current = _get_week_range()
    tag = "📅 Current Week" if is_current else "📅 Past Week"

    st.markdown(
        f'<div style="background:linear-gradient(135deg,#0d1117,#111827);'
        f'border-radius:14px;padding:20px 28px 14px;margin-bottom:16px;'
        f'border:1px solid #1f2d40">'
        f'<div style="font-size:0.72rem;color:#4b6080;letter-spacing:1px;'
        f'text-transform:uppercase;margin-bottom:4px">{tag} · {country}</div>'
        f'<div style="font-size:1.9rem;font-weight:900;color:#c8d6f0">'
        f'🌍 {country} — Market Overview</div>'
        f'<div style="font-size:0.82rem;color:#9aa0b4;margin-top:6px">'
        f'Select a <b>Group</b> from the sidebar to drill into a sector &nbsp;·&nbsp; '
        f'Select a <b>Stock</b> for the full dashboard</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    week_start, _, _, _ = _get_week_range()

    # ── Group performance cards ───────────────────────────────────
    st.markdown('<p class="section-title">📊 Group Performance This Week</p>',
                unsafe_allow_html=True)

    grp_data = []
    for grp_name, stocks in groups.items():
        tickers_list = list(stocks.values())[:10]  # sample up to 10 per group
        week_returns = []
        for sym in tickers_list:
            df = safe_run(
                lambda s=sym: get_price_data(s, period="1mo", interval="1d",
                                             cache_buster=cb),
                context=f"mkt_overview:{sym}", default=None,
            )
            if df is None or df.empty or len(df) < 2:
                continue
            df_w = df[df.index.date >= week_start]
            if df_w.empty:
                df_w = df.tail(5)
            o = float(df_w["Close"].iloc[0])
            c = float(df_w["Close"].iloc[-1])
            if o:
                week_returns.append((c - o) / o * 100)
        if not week_returns:
            continue
        avg_ret    = round(sum(week_returns) / len(week_returns), 2)
        pct_up     = round(sum(1 for r in week_returns if r > 0) / len(week_returns) * 100)
        grp_data.append((grp_name, avg_ret, pct_up, len(week_returns)))

    if grp_data:
        # Sort best to worst
        grp_data.sort(key=lambda x: x[1], reverse=True)
        cols = responsive_cols(min(4, len(grp_data)))
        for i, (grp, avg, pct_up, n) in enumerate(grp_data):
            color = "#00c853" if avg >= 0 else "#ff1744"
            arrow = "▲" if avg >= 0 else "▼"
            brd   = "#00c85344" if pct_up >= 60 else "#ff174444" if pct_up < 40 else "#ff980044"
            cols[i % len(cols)].markdown(
                f'<div class="kpi-card" style="border-left-color:{color}">'
                f'<div class="kpi-label" style="font-size:0.70rem">{grp}</div>'
                f'<div class="kpi-value" style="font-size:1.1rem;color:{color}">'
                f'{arrow} {abs(avg):.2f}%</div>'
                f'<div class="kpi-delta" style="color:#9aa0b4">'
                f'{pct_up}% stocks up · {n} tracked</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Market breadth chart ──────────────────────────────────────
    if grp_data:
        st.divider()
        st.markdown('<p class="section-title">📈 Market Breadth by Group</p>',
                    unsafe_allow_html=True)
        fig = go.Figure(go.Bar(
            x=[g[0] for g in grp_data],
            y=[g[1] for g in grp_data],
            marker_color=["#00c853" if g[1] >= 0 else "#ff1744" for g in grp_data],
            text=[f"{g[1]:+.1f}%" for g in grp_data],
            textposition="outside",
        ))
        fig.update_layout(
            template="plotly_dark", height=340,
            paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
            font=dict(color="#9aa0b4"),
            yaxis=dict(title="Avg Weekly Return %", gridcolor="#1f2540",
                       zeroline=True, zerolinecolor="#4b6080"),
            xaxis=dict(gridcolor="#1f2540", tickangle=-30),
            margin=dict(l=10, r=10, t=20, b=80),
            showlegend=False,
        )
        fig.update_traces(cliponaxis=False)
        st.plotly_chart(fig, config={"responsive": True})


# ─────────────────────────────────────────────────────────────────
# NEW: render_group_overview  — State 3
# Group selected, no stock. Shows all stocks in the group with
# weekly return heatmap, top/bottom movers, and signal summary.
# ─────────────────────────────────────────────────────────────────
def render_group_overview(country: str, group_name: str,
                           stocks: dict, cur_sym: str = "$", cb: int = 0):
    """
    Group-level overview: weekly return for every stock in the group,
    top gainers/losers, and a quick signal summary.
    """
    from indicators import compute_indicators, signal_score
    from market_data import get_ticker_info

    _, _, week_label, is_current = _get_week_range()
    tag = "📅 Current Week" if is_current else "📅 Past Week"

    st.markdown(
        f'<div style="background:linear-gradient(135deg,#0d1117,#111827);'
        f'border-radius:14px;padding:20px 28px 14px;margin-bottom:16px;'
        f'border:1px solid #1f2d40">'
        f'<div style="font-size:0.72rem;color:#4b6080;letter-spacing:1px;'
        f'text-transform:uppercase;margin-bottom:4px">'
        f'{tag} · {country} · {group_name}</div>'
        f'<div style="font-size:1.9rem;font-weight:900;color:#c8d6f0">'
        f'{group_name}</div>'
        f'<div style="font-size:0.82rem;color:#9aa0b4;margin-top:6px">'
        f'{len(stocks)} stocks tracked &nbsp;·&nbsp; '
        f'Select a <b>Stock</b> from the sidebar for the full dashboard</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    week_start, _, _, _ = _get_week_range()
    stock_rows = []

    # Batch-fetch all group tickers (chunked, not sequential per-ticker)
    _syms  = tuple(stocks.values())
    _batch = safe_run(
        lambda: get_batch_data(_syms, period="3mo", cache_buster=cb),
        context="grp_overview:batch", default={},
    ) or {}

    with st.spinner("Loading group data…"):
        for sname, sym in stocks.items():
            df = _batch.get(sym)
            if df is None or df.empty or len(df) < 5:
                continue
            df_w = df[df.index.date >= week_start]
            if df_w.empty:
                df_w = df.tail(5)
            o   = float(df_w["Close"].iloc[0])
            c   = float(df_w["Close"].iloc[-1])
            ret = round((c - o) / o * 100 if o else 0, 2)

            # Quick signal score (no info dict — technical only)
            sig = safe_run(
                lambda d=df: signal_score(compute_indicators(d), {}),
                context=f"grp_sig:{sym}", default={"signal": "—", "score": 0, "sigcolor": "#6b7280"},
            )
            stock_rows.append({
                "name":    sname,
                "sym":     sym,
                "price":   c,
                "ret":     ret,
                "signal":  sig.get("signal", "—"),
                "score":   sig.get("score", 0),
                "sigcol":  sig.get("sigcolor", "#6b7280"),
            })

    if not stock_rows:
        st.info("Could not load data for this group. Try refreshing.")
        return

    stock_rows.sort(key=lambda x: x["ret"], reverse=True)

    # ── Tabs: Weekly Returns | Portfolio Allocator | Signal Summary ──
    tab_weekly, tab_alloc, tab_signals = st.tabs([
        "📊 Weekly Returns",
        "🎯 Portfolio Allocator",
        "📡 Signal Summary",
    ])

    # ── Tab 1: Weekly returns heatmap ─────────────────────────────
    with tab_weekly:
      st.markdown('<p class="section-title">📊 Weekly Returns — All Stocks</p>',
                unsafe_allow_html=True)

      fig = go.Figure(go.Bar(
          x=[r["name"] for r in stock_rows],
          y=[r["ret"]  for r in stock_rows],
          marker_color=["#00c853" if r["ret"] >= 0 else "#ff1744" for r in stock_rows],
          text=[f"{r['ret']:+.1f}%" for r in stock_rows],
          textposition="outside",
          customdata=[[r["sym"], r["signal"], r["score"]] for r in stock_rows],
          hovertemplate=(
              "<b>%{x}</b><br>"
              "Weekly Return: %{y:+.2f}%<br>"
              "Ticker: %{customdata[0]}<br>"
              "Signal: %{customdata[1]}  Score: %{customdata[2]}/100"
              "<extra></extra>"
          ),
      ))
      fig.update_layout(
          template="plotly_dark", height=max(320, 200 + len(stock_rows) * 8),
          paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
          font=dict(color="#9aa0b4"),
          yaxis=dict(title="Weekly Return %", gridcolor="#1f2540",
                     zeroline=True, zerolinecolor="#4b6080"),
          xaxis=dict(gridcolor="#1f2540", tickangle=-35),
          margin=dict(l=10, r=10, t=20, b=100),
          showlegend=False,
      )
      fig.update_traces(cliponaxis=False)
      st.plotly_chart(fig, config={"responsive": True})

      # ── Top 5 gainers / losers ──────────────────────────────────
      st.divider()
      col_g, col_l = st.columns(2)
      with col_g:
          st.markdown('<p class="section-title">🟢 Top Gainers</p>',
                      unsafe_allow_html=True)
          for r in stock_rows[:5]:
              color = "#00c853"
              st.markdown(
                  f'<div class="kpi-card" style="border-left-color:{color}">'
                  f'<div class="kpi-label">{r["name"]} '
                  f'<span style="font-family:monospace;font-size:0.68rem;'
                  f'color:#4b6080">{r["sym"]}</span></div>'
                  f'<div style="display:flex;justify-content:space-between;'
                  f'align-items:center">'
                  f'<div class="kpi-value" style="font-size:1rem">'
                  f'{cur_sym}{r["price"]:,.2f}</div>'
                  f'<div style="color:{color};font-weight:700">+{r["ret"]:.2f}%</div>'
                  f'<span style="background:{r["sigcol"]}22;border:1px solid {r["sigcol"]};'
                  f'border-radius:10px;padding:2px 8px;font-size:0.68rem;color:{r["sigcol"]}">'
                  f'{r["signal"]}</span>'
                  f'</div></div>',
                  unsafe_allow_html=True,
              )
      with col_l:
          st.markdown('<p class="section-title">🔴 Biggest Declines</p>',
                      unsafe_allow_html=True)
          for r in stock_rows[-5:][::-1]:
              color = "#ff1744"
              st.markdown(
                  f'<div class="kpi-card" style="border-left-color:{color}">'
                  f'<div class="kpi-label">{r["name"]} '
                  f'<span style="font-family:monospace;font-size:0.68rem;'
                  f'color:#4b6080">{r["sym"]}</span></div>'
                  f'<div style="display:flex;justify-content:space-between;'
                  f'align-items:center">'
                  f'<div class="kpi-value" style="font-size:1rem">'
                  f'{cur_sym}{r["price"]:,.2f}</div>'
                  f'<div style="color:{color};font-weight:700">{r["ret"]:.2f}%</div>'
                  f'<span style="background:{r["sigcol"]}22;border:1px solid {r["sigcol"]};'
                  f'border-radius:10px;padding:2px 8px;font-size:0.68rem;color:{r["sigcol"]}">'
                  f'{r["signal"]}</span>'
                  f'</div></div>',
                  unsafe_allow_html=True,
              )

    # ── Tab 2: Portfolio Allocator ────────────────────────────────
    with tab_alloc:
        _render_portfolio_allocator(
            stocks=stocks, stock_rows=stock_rows,
            cur_sym=cur_sym, cb=cb,
        )

    # ── Tab 3: Signal Summary ─────────────────────────────────────
    with tab_signals:
      st.markdown('<p class="section-title">🎯 Signal Summary</p>',
                unsafe_allow_html=True)
      from collections import Counter
      sig_counts = Counter(r["signal"] for r in stock_rows)
      sig_order  = ["STRONG BUY", "BUY", "WATCH", "CAUTION", "AVOID", "RATES CONTEXT", "NO DATA", "—"]
      sig_colors = {
          "STRONG BUY": "#00c853", "BUY": "#4f8ef7",
          "WATCH": "#ff9800", "CAUTION": "#ff1744",
          "AVOID": "#ff1744", "NO DATA": "#6b7280",
          "RATES CONTEXT": "#6b7280", "—": "#6b7280",
      }
      total = len(stock_rows)
      cols  = responsive_cols(min(4, len(sig_counts)))
      ci    = 0
      for sig in sig_order:
          n = sig_counts.get(sig, 0)
          if n == 0:
              continue
          pct   = round(n / total * 100)
          color = sig_colors.get(sig, "#6b7280")
          cols[ci % len(cols)].markdown(
              f'<div class="kpi-card" style="border-left-color:{color}">'
              f'<div class="kpi-label" style="color:{color}">{sig}</div>'
              f'<div class="kpi-value" style="font-size:1.4rem">{n}</div>'
              f'<div class="kpi-delta" style="color:#6b7280">{pct}% of group</div>'
              f'</div>',
              unsafe_allow_html=True,
          )
          ci += 1



# ── Portfolio Allocator (v5.23) ───────────────────────────────────────────────

def _render_portfolio_allocator(stocks: dict, stock_rows: list,
                                 cur_sym: str = "₹", cb: int = 0):
    """
    Mean-CVaR portfolio optimiser tab.
    Steps: data quality → stress check → winsorise → bootstrap → optimise → display.
    All critical stress test fixes (P1, M1, D1, D3, A1) applied inline.
    """
    from market_data import get_price_data, get_batch_data

    if not CVXPY_AVAILABLE:
        st.warning(
            "⚙️ **Portfolio Allocator not available** — `cvxpy` is not installed. "
            "Add `cvxpy` to `requirements.txt` and redeploy to enable this feature."
        )
        return

    # ── 1. Controls ───────────────────────────────────────────────
    c_amt, c_risk = st.columns([2, 3])
    with c_amt:
        st.markdown('<div style="font-size:0.70rem;text-transform:uppercase;'
                    'letter-spacing:1px;color:#4b6080;margin-bottom:4px">'
                    'Investment amount</div>', unsafe_allow_html=True)
        amount = st.number_input(
            f"Amount ({cur_sym})", min_value=10_000, max_value=10_000_000,
            value=100_000, step=10_000, label_visibility="collapsed",
            key=f"alloc_amount_{cb}",
        )
    with c_risk:
        st.markdown('<div style="font-size:0.70rem;text-transform:uppercase;'
                    'letter-spacing:1px;color:#4b6080;margin-bottom:4px">'
                    'Risk comfort level</div>', unsafe_allow_html=True)
        risk_profile = st.radio(
            "Risk", ["Conservative 🛡", "Balanced ⚖", "Aggressive 🚀"],
            horizontal=True, label_visibility="collapsed",
            key=f"alloc_risk_{cb}",
        )
    profile_key = risk_profile.split()[0].lower()

    # ── 2. Load price data for all stocks ─────────────────────────
    with st.spinner("Loading price data for all stocks…"):
        df_dict = {}
        for sname, sym in stocks.items():
            df = safe_run(
                lambda s=sym: get_price_data(s, period="6mo", interval="1d",
                                             cache_buster=cb),
                context=f"alloc:{sym}", default=None,
            )
            if df is not None and not df.empty:
                df_dict[sname] = df

    if len(df_dict) < 3:
        st.info("Not enough data available for this group. Try refreshing.")
        return

    # ── 3. Stress regime check (CRITICAL/P1 + CRITICAL/M1) ───────
    returns_raw, names, excluded = compute_log_returns(df_dict)

    if returns_raw.size == 0 or len(names) < 3:
        st.info(f"Insufficient clean data — {len(excluded)} stocks excluded by quality check.")
        for nm, reason in excluded[:5]:
            st.caption(f"  • {nm}: {reason}")
        return

    # Fetch VIX for stress check
    vix_df = safe_run(
        lambda: get_price_data("^VIX", period="5d", interval="1d", cache_buster=cb),
        context="alloc:vix", default=None,
    )
    regime = detect_stress_regime(returns_raw, vix_df)

    if regime["stress"]:
        mode  = regime["mode"]
        color = "#ff1744" if mode == "crisis" else "#ff9800"
        icon  = "🚨" if mode == "crisis" else "⚠️"
        st.markdown(
            f'<div style="background:{color}11;border:1px solid {color}44;'
            f'border-radius:10px;padding:14px 18px;margin-bottom:14px">'
            f'<div style="font-size:0.80rem;font-weight:700;color:{color};margin-bottom:6px">'
            f'{icon} {"CRISIS" if mode == "crisis" else "STRESS"} REGIME DETECTED</div>'
            f'<div style="font-size:0.80rem;color:#c8d6f0;line-height:1.6">'
            f'{regime["reason"]}<br>'
            f'<b>CVaR estimates may be unreliable in this regime.</b> '
            f'Allocation shown below is based on historical data that may not reflect '
            f'current market conditions. Consider reducing position sizes or waiting '
            f'for conditions to normalise.</div></div>',
            unsafe_allow_html=True,
        )
        if mode == "crisis":
            with st.expander("Show allocation anyway (not recommended)", expanded=False):
                _run_and_display_allocation(
                    returns_raw, names, excluded, df_dict, stock_rows,
                    amount, profile_key, cur_sym, stocks,
                )
            return

    # ── 4. Run optimisation ───────────────────────────────────────
    _run_and_display_allocation(
        returns_raw, names, excluded, df_dict, stock_rows,
        amount, profile_key, cur_sym, stocks,
    )


def _run_and_display_allocation(returns_raw, names, excluded, df_dict, stock_rows,
                                  amount, profile_key, cur_sym, stocks):
    """Inner function — runs optimisation and renders results."""
    import plotly.graph_objects as go

    # Pipeline layers 2-3: Winsorize → Exponential bootstrap
    returns_w  = winsorize_returns(returns_raw)
    scenarios  = bootstrap_scenarios(returns_w, n=N_SCENARIOS)
    risk_av    = RISK_AVERSION.get(profile_key, 1.0)

    with st.spinner(f"Optimising {len(names)}-stock portfolio…"):
        result = optimise_mean_cvar(scenarios, names, risk_aversion=risk_av)

    if result.get("status") != "optimal":
        if result.get("status") == "cvxpy_not_installed":
            st.warning(result["message"])
        else:
            st.error(f"Optimisation did not converge ({result.get('status', 'unknown')}). "
                     "Try a different risk profile or refresh data.")
        return

    allocation = result["allocation"]

    # ── Layer 4: regime conflict check ───────────────────────────
    sig_map = {r["name"]: {"signal": r["signal"]} for r in stock_rows}
    conflicts = check_regime_conflicts(allocation, sig_map)

    if conflicts:
        st.markdown(
            '<div style="background:#ff174411;border:1px solid #ff174444;'
            'border-radius:10px;padding:12px 16px;margin-bottom:12px">',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="font-size:0.78rem;font-weight:700;color:#ff1744;margin-bottom:6px">'
            '⚠️ Regime conflict — optimiser disagrees with technical signals</div>',
            unsafe_allow_html=True,
        )
        for c in conflicts:
            st.markdown(
                f'<div style="font-size:0.76rem;color:#ffb3b3;line-height:1.6">'
                f'• <b>{c["name"]}</b> allocated {c["weight_pct"]:.0f}% '
                f'but technical signal is <b>{c["signal"]}</b>. '
                f'Consider reducing this position or reviewing the Insights tab.</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Metric cards ──────────────────────────────────────────────
    mc1, mc2, mc3, mc4 = st.columns(4)
    ret_color = "#00c853" if result["exp_ret"] > 0 else "#ff1744"
    mc1.markdown(
        f'<div class="kpi-card"><div class="kpi-label">Expected Annual Return</div>'
        f'<div class="kpi-value" style="color:{ret_color}">{result["exp_ret"]:+.1f}%</div>'
        f'<div class="kpi-delta" style="color:#4b6080">'
        f'P10–P90: {result["conf_lo"]:+.0f}% to {result["conf_hi"]:+.0f}%</div></div>',
        unsafe_allow_html=True,
    )
    mc2.markdown(
        f'<div class="kpi-card"><div class="kpi-label">After costs</div>'
        f'<div class="kpi-value" style="font-size:1.3rem;color:{ret_color}">'
        f'{result["exp_ret_after_cost"]:+.1f}%</div>'
        f'<div class="kpi-delta" style="color:#4b6080">-0.25% round-trip est.</div></div>',
        unsafe_allow_html=True,
    )
    mc3.markdown(
        f'<div class="kpi-card"><div class="kpi-label">CVaR (95%)</div>'
        f'<div class="kpi-value" style="color:#ff9800">-{result["cvar"]:.1f}%</div>'
        f'<div class="kpi-delta" style="color:#4b6080">avg worst-5% daily loss</div></div>',
        unsafe_allow_html=True,
    )
    mc4.markdown(
        f'<div class="kpi-card"><div class="kpi-label">Sharpe Ratio</div>'
        f'<div class="kpi-value" style="color:#4f8ef7">{result["sharpe"]:.2f}</div>'
        f'<div class="kpi-delta" style="color:#4b6080">{result["n_stocks"]} stocks</div></div>',
        unsafe_allow_html=True,
    )

    # Leverage disclaimer on aggressive
    if profile_key == "aggressive":
        st.markdown(
            '<div style="background:#ff980011;border:1px solid #ff980044;'
            'border-radius:8px;padding:10px 14px;margin:8px 0;font-size:0.76rem;color:#ffe0b2">'
            '⚠️ <b>Do not use borrowed money with this profile.</b> Leverage multiplies losses — '
            'a CVaR of -9% on 5× leverage = -45% on your equity. These estimates assume cash investment only.'
            '</div>',
            unsafe_allow_html=True,
        )

    # ── Allocation table ──────────────────────────────────────────
    st.markdown('<p class="section-title">📊 Optimal Allocation</p>',
                unsafe_allow_html=True)

    sig_colors = {
        "STRONG BUY": "#00c853", "BUY": "#4f8ef7",
        "WATCH": "#ff9800", "CAUTION": "#ff1744",
        "AVOID": "#ff1744", "RATES CONTEXT": "#6b7280",
    }
    sig_map = {r["name"]: r for r in stock_rows}
    COLORS  = ["#4f8ef7","#00c853","#ffd600","#e040fb","#ff6d00",
               "#00bcd4","#ff5722","#69f0ae","#ff80ab","#80d8ff"]

    for i, item in enumerate(allocation):
        name      = item["name"]
        pct       = item["pct"]
        money     = int(amount * pct / 100)
        clr       = COLORS[i % len(COLORS)]
        row_sig   = sig_map.get(name, {})
        sig_lbl   = row_sig.get("signal", "—")
        sig_clr   = sig_colors.get(sig_lbl, "#6b7280")
        sym       = stocks.get(name, "")

        st.markdown(
            f'<div class="kpi-card" style="border-left-color:{clr};padding:10px 14px;margin:3px 0">'
            f'<div style="display:flex;align-items:center;gap:10px">'
            f'<div style="flex:2;font-size:0.82rem;color:#c8d6f0">{name} '
            f'<span style="font-family:monospace;font-size:0.68rem;color:#4b6080">{sym}</span></div>'
            f'<div style="flex:3;background:#0d1a2e;border-radius:4px;height:8px;overflow:hidden">'
            f'<div style="width:{min(pct*2.5, 95):.0f}%;height:8px;background:{clr};border-radius:4px"></div></div>'
            f'<div style="min-width:44px;text-align:right;font-weight:600;color:{clr}">{pct:.0f}%</div>'
            f'<div style="min-width:80px;text-align:right;font-size:0.78rem;color:#9aa0b4">'
            f'{cur_sym}{money:,.0f}</div>'
            f'<span style="background:{sig_clr}22;border:1px solid {sig_clr}44;'
            f'border-radius:8px;padding:2px 8px;font-size:0.68rem;color:{sig_clr}">{sig_lbl}</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    if excluded:
        st.caption(f"ℹ️ {len(excluded)} stock(s) excluded: " +
                   "; ".join(f"{n} ({r})" for n, r in excluded[:3]))

    # ── Efficient frontier ────────────────────────────────────────
    st.divider()
    st.markdown('<p class="section-title">📈 Efficient Frontier</p>',
                unsafe_allow_html=True)

    with st.spinner("Computing efficient frontier…"):
        frontier = safe_run(
            lambda: compute_efficient_frontier(scenarios, names, n_points=12),
            context="alloc:frontier", default=[],
        )

    if frontier:
        sel_cvar = result["cvar"]
        sel_ret  = result["exp_ret"]
        other_pts = [p for p in frontier
                     if abs(p["cvar"]*100 - sel_cvar) > 0.3 or abs(p["exp_ret"] - sel_ret) > 0.3]
        selected  = [p for p in frontier
                     if abs(p["cvar"]*100 - sel_cvar) <= 0.3 and abs(p["exp_ret"] - sel_ret) <= 0.3]
        if not selected:
            selected = [{"cvar": sel_cvar/100, "exp_ret": sel_ret}]

        fig = go.Figure()
        if other_pts:
            fig.add_trace(go.Scatter(
                x=[p["cvar"]*100 for p in other_pts],
                y=[p["exp_ret"]  for p in other_pts],
                mode="lines+markers", name="Efficient frontier",
                line=dict(color="rgba(79,142,247,0.33)", width=1.5),
                marker=dict(size=6, color="#4f8ef7"),
            ))
        fig.add_trace(go.Scatter(
            x=[sel_cvar], y=[sel_ret],
            mode="markers", name="Your portfolio",
            marker=dict(size=14, color="#ffd600", symbol="star"),
        ))
        fig.update_layout(
            template="plotly_dark", height=280,
            paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
            font=dict(color="#9aa0b4"),
            xaxis=dict(title="Daily CVaR % (risk)", gridcolor="#1f2540",
                       ticksuffix="%"),
            yaxis=dict(title="Expected annual return %", gridcolor="#1f2540",
                       ticksuffix="%"),
            margin=dict(l=10, r=10, t=20, b=40),
            legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center"),
        )
        st.plotly_chart(fig, config={"responsive": True})
    else:
        st.caption("Efficient frontier requires cvxpy to be fully operational.")

    # ── Disclaimer ────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:0.72rem;color:#4b6080;border-top:1px solid #1a2540;'
        'margin-top:10px;padding-top:8px;line-height:1.6">'
        '⚠️ Based on 90-day historical returns. Does not account for upcoming earnings, '
        'macro events, or regulatory changes. Not financial advice. '
        'Optimised for a 21–63 day holding period. P10–P90 confidence band shown, not a guarantee.'
        '</div>',
        unsafe_allow_html=True,
    )

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
        # No resolved forecasts — show pending status so user knows what's coming
        pending = safe_run(get_pending_forecast_summary,
                           context="week:pending_summary", default={"count": 0})
        if pending and pending.get("count", 0) > 0:
            n          = pending["count"]
            earliest   = pending.get("earliest_due", "")
            days_left  = pending.get("days_until_first")
            tickers    = pending.get("tickers", [])
            ticker_str = ", ".join(tickers[:8]) + ("…" if len(tickers) > 8 else "")
            st.markdown(
                f'<div style="background:#0d1f35;border:1px solid #1a3050;'
                f'border-radius:10px;padding:14px 18px;margin-bottom:12px">'
                f'<div style="font-size:0.80rem;font-weight:700;color:#4f8ef7;'
                f'margin-bottom:8px">🕐 {n} forecast(s) being tracked</div>'
                f'<div style="font-size:0.82rem;color:#c8d6f0;line-height:1.8">'
                f'Stocks tracked: <b>{ticker_str}</b><br>'
                f'First resolution date: <b>{earliest}</b>'
                f'{f" — {days_left} day(s) from today" if days_left is not None else ""}<br>'
                f'Accuracy metrics will populate automatically once due dates pass. '
                f'The 1M (21-day) forecasts resolve first.'
                f'</div></div>',
                unsafe_allow_html=True,
            )
            # Show pending table
            import pandas as _pd
            rows = []
            for e in pending.get("pending", [])[:10]:
                rows.append({
                    "Ticker":   e["_key"].replace("_63d","").replace("_21d",""),
                    "Made On":  e["made_on"],
                    "Due On":   e["due_on"],
                    "Horizon":  f'{e["horizon_days"]}d',
                    "P(Gain)":  f'{e["p_gain"]:.0f}%' if e.get("p_gain") is not None else "—",
                    "Status":   "⏳ Pending",
                })
            if rows:
                st.dataframe(_pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.markdown(
                '<div class="insight-box" style="font-size:0.84rem">'
                '📊 No forecasts stored yet. Open a stock\'s Forecast tab '
                'to generate forecasts — they will be tracked automatically here.</div>',
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
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
