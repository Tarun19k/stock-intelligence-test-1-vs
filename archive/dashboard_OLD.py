# pages/dashboard.py — Phase 3: Full 4-tab dashboard
# Tabs: Technical Charts | Forecast | Compare | Insights & Actions
# Entry point: render_dashboard(ticker, name, country, cur_sym, info, df, cb)

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

from utils import safe_float, sanitise, sanitise_bold, responsive_cols, log_error, safe_run, info_tip, section_title_with_tip
from indicators import compute_indicators, signal_score
from market_data import get_price_data, get_news
from config import HELP_TEXT
from forecast import (
    store_forecast, resolve_forecasts,
    render_forecast_accuracy,
)



def _has_ohlcv(df: pd.DataFrame) -> bool:
    """Return True only if df has all required OHLCV columns as proper Series."""
    if df is None or df.empty:
        return False
    required = ["Open", "High", "Low", "Close", "Volume"]
    for col in required:
        if col not in df.columns:
            return False
        if isinstance(df[col], pd.DataFrame):
            return False
    return True


def _safe_close(df: pd.DataFrame, default=None):
    """Safely return df['Close'] as a Series, or default."""
    if df is None or df.empty or "Close" not in df.columns:
        return default if default is not None else pd.Series(dtype=float)
    val = df["Close"]
    return val.iloc[:, 0] if isinstance(val, pd.DataFrame) else val


# ─────────────────────────────────────────────────────────────────
# KPI TILE helper
# ─────────────────────────────────────────────────────────────────
def _kpi(col, label: str, value: str, css_cls: str = "", tip: str = ""):
    """KPI tile — tip= adds hover tooltip on card and ℹ️ icon on label."""
    label_html = info_tip(label, tip) if tip else sanitise(label)
    tip_attr   = sanitise(tip, 400)
    col.markdown(
        f'<div class="kpi-card {css_cls}" title="{tip_attr}">' +
        f'<div class="kpi-label">{label_html}</div>' +
        f'<div class="kpi-value">{sanitise(value)}</div>' +
        f'</div>',
        unsafe_allow_html=True,
    )


def _graph_help(*lines):
    body = " · ".join(lines)
    st.markdown(
        f'<div class="graph-help">{sanitise(body, max_len=400)}</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────
# LIVE PRICE HEADER
# ─────────────────────────────────────────────────────────────────
def _render_header(ticker, name, country, cur_sym, info, df, sig_data):
    _cl     = _safe_close(df)
    price   = safe_float(_cl.iloc[-1])  if not _cl.empty else 0
    prev    = safe_float(_cl.iloc[-2])  if len(_cl) >= 2 else price
    chg     = (price - prev) / prev * 100       if prev else 0
    chg_col = "#00c853" if chg >= 0 else "#ff1744"
    arrow   = "▲" if chg >= 0 else "▼"

    mkt_cap  = safe_float(info.get("marketCap", 0))
    sector   = sanitise(info.get("sector") or info.get("quoteType", ""), 40)
    longname = sanitise(info.get("longName", name), 60)
    sig      = sig_data["signal"]
    sig_col  = sig_data["sigcolor"]
    score    = sig_data["score"]
    cap_str  = f"{cur_sym}{mkt_cap/1e9:.1f}B" if mkt_cap > 1e9 else "—"

    tip_signal = sanitise(HELP_TEXT["signal"], 400)
    tip_score  = sanitise(HELP_TEXT["score"],  400)
    tip_ticker = sanitise(HELP_TEXT["ticker"], 400)

    st.markdown(
        f'<div style="color:#c8d6f0;background:linear-gradient(135deg,#111827,#1f2937);' +
        f'border-radius:14px;padding:20px 28px;margin-bottom:18px;' +
        f'border:1px solid #1f2d40">' +
        f'<div style="font-size:0.74rem;color:#6b7280;margin-bottom:4px">' +
        f'{sanitise(country)} · {sanitise(ticker, 20)} · {sector} · Mkt Cap {cap_str}</div>' +
        f'<div style="font-size:1.85rem;font-weight:900;color:#fff">{longname}</div>' +
        f'<div style="display:flex;align-items:baseline;gap:14px;margin-top:6px">' +
        f'<span style="font-size:2rem;font-weight:900;color:#4f8ef7">{cur_sym}{price:,.2f}</span>' +
        f'<span style="font-size:1.15rem;color:{chg_col};font-weight:700">{arrow} {abs(chg):.2f}% today</span></div>' +
        f'<div style="margin-top:10px;display:flex;align-items:center;gap:8px">' +
        f'<span title="{tip_signal}" style="background:{sig_col}22;border:1px solid {sig_col};' +
        f'border-radius:20px;padding:4px 14px;color:{sig_col};font-weight:700;' +
        f'font-size:0.86rem">{sanitise(sig)}</span>' +
        f'<span style="color:#9ab8e0;background:#1a2332;border:1px solid #2d3a5e;' +
        f'border-radius:6px;padding:3px 10px;font-size:0.72rem;color:#4b6080">' +
        f'Score {score}/100</span>' +
        f'<span style="color:#9ab8e0;background:#1a2332;border:1px solid #2d3a5e;' +
        f'border-radius:6px;padding:3px 10px;font-size:0.72rem;color:#4f8ef7;' +
        f'font-family:monospace">{sanitise(ticker, 20)}</span>' +
        f'</div></div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────
# KPI SIGNAL PANEL
# ─────────────────────────────────────────────────────────────────
def _render_kpi_panel(sig: dict, cur_sym: str):
    st.markdown(section_title_with_tip("📊 KPI Signal Panel", HELP_TEXT["score"]),
                unsafe_allow_html=True)

    def _color(val, green_cond, red_cond):
        if green_cond(val): return "green"
        if red_cond(val):   return "red"
        return "yellow"

    row1 = responsive_cols(4)
    _kpi(row1[0], "RSI 14",        f'{sig["rsi"]:.1f}',
         _color(sig["rsi"], lambda v: v < 40, lambda v: v > 70), tip=HELP_TEXT["rsi"])
    _kpi(row1[1], "MACD Histogram", f'{sig["macdh"]:.3f}',
         _color(sig["macdh"], lambda v: v > 0, lambda v: v < 0), tip=HELP_TEXT["macd_h"])
    _kpi(row1[2], "Bollinger Width", f'{sig["bbw"]:.1f}%',   "yellow", tip=HELP_TEXT["bbw"])
    _kpi(row1[3], "ATR Volatility",  f'{cur_sym}{sig["atr"]:.2f}', "yellow", tip=HELP_TEXT["atr"])

    row2 = responsive_cols(5)
    _kpi(row2[0], "ADX Trend",
         f'{sig["adx"]:.1f}',
         _color(sig["adx"], lambda v: v > 25, lambda v: v < 15), tip=HELP_TEXT["adx"])
    _kpi(row2[1], "Stochastic %K",
         f'{sig["stoch"]:.1f}',
         _color(sig["stoch"], lambda v: v < 30, lambda v: v > 75), tip=HELP_TEXT["stoch"])
    pe_str = f'{sig["pe"]:.1f}x' if sig["pe"] > 0 else "N/A"
    _kpi(row2[2], "P/E · P/B",
         f'{pe_str} · {sig["pb"]:.2f}x',
         _color(sig["pe"], lambda v: 0 < v < 22, lambda v: v > 40), tip=HELP_TEXT["pe_pb"])
    _kpi(row2[3], "ROE · Rev Growth",
         f'{sig["roe"]:.1f}% · {sig["revg"]:.1f}%',
         _color(sig["roe"], lambda v: v > 15, lambda v: v < 5), tip=HELP_TEXT["roe_revg"])
    _kpi(row2[4], "OBV · Volume",
         f'{sig["obv"]:.1f}M · {sig["volm"]:.1f}M', "", tip=HELP_TEXT["obv_vol"])


# ─────────────────────────────────────────────────────────────────
# TAB 1 — TECHNICAL CHARTS
# ─────────────────────────────────────────────────────────────────

@st.fragment(run_every=60)
def _live_kpi_panel(sig: dict, cur_sym: str):
    """Fragment: re-renders live price KPIs every 60 s.
    Charts and analysis sections are outside this fragment."""
    _render_kpi_panel(sig, cur_sym)  # ← calls the REAL function

def _tab_charts(df: pd.DataFrame, cur_sym: str):
    _graph_help(
        "Daily candles + Bollinger Bands + SMA20/50/200",
        "MACD Histogram + Signal Line",
        "RSI with 30/70 bands",
        "Volume bars",
    )
    dp = df.tail(120).copy()
    if dp.empty:
        st.info("Not enough data for chart.")
        return

    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True,
        row_heights=[0.46, 0.20, 0.20, 0.14],
        vertical_spacing=0.03,
        subplot_titles=["Price · Bollinger · MAs", "MACD", "RSI", "Volume"],
    )
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=dp.index, open=dp["Open"], high=dp["High"],
        low=dp["Low"], close=dp["Close"], name="Price",
        increasing_line_color="#00c853", decreasing_line_color="#ff1744",
    ), row=1, col=1)
    # MAs
    for col_name, color, dash in [
        ("SMA20","#4fc3f7","solid"),("SMA50","#ffd600","dash"),("SMA200","#ff6d00","dot"),
    ]:
        if col_name in dp.columns:
            fig.add_trace(go.Scatter(
                x=dp.index, y=dp[col_name], name=col_name,
                line=dict(color=color, width=1.2, dash=dash),
            ), row=1, col=1)
    # Bollinger
    if "BBU" in dp.columns:
        fig.add_trace(go.Scatter(
            x=dp.index, y=dp["BBU"],
            line=dict(color="#7986cb", width=1, dash="dot"),
            showlegend=False,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=dp.index, y=dp["BBL"], name="BB Band",
            line=dict(color="#7986cb", width=1, dash="dot"),
            fill="tonexty", fillcolor="rgba(121,134,203,0.06)",
        ), row=1, col=1)
    # MACD
    if "MACDH" in dp.columns:
        hc = ["#00c853" if v >= 0 else "#ff1744" for v in dp["MACDH"]]
        fig.add_trace(go.Bar(
            x=dp.index, y=dp["MACDH"], marker_color=hc,
            name="Histogram", opacity=0.7,
        ), row=2, col=1)
        fig.add_trace(go.Scatter(
            x=dp.index, y=dp["MACD"], name="MACD",
            line=dict(color="#4fc3f7", width=1.2),
        ), row=2, col=1)
        fig.add_trace(go.Scatter(
            x=dp.index, y=dp["MACDS"], name="Signal",
            line=dict(color="#ffd600", width=1.2, dash="dash"),
        ), row=2, col=1)
    # RSI
    if "RSI" in dp.columns:
        fig.add_trace(go.Scatter(
            x=dp.index, y=dp["RSI"], name="RSI",
            line=dict(color="#e040fb", width=1.8),
            fill="tozeroy", fillcolor="rgba(224,64,251,0.05)",
        ), row=3, col=1)
        fig.add_hline(y=70, row=3, col=1,
                      line_dash="dot", line_color="#ff1744", line_width=0.8)
        fig.add_hline(y=30, row=3, col=1,
                      line_dash="dot", line_color="#00c853", line_width=0.8)
    # Volume
    vc = ["#00c853" if dp["Close"].iloc[i] >= dp["Close"].iloc[max(i-1,0)] else "#ff1744"
          for i in range(len(dp))]
    fig.add_trace(go.Bar(
        x=dp.index, y=dp["Volume"], marker_color=vc,
        name="Volume", opacity=0.6,
    ), row=4, col=1)

    fig.update_layout(
        template="plotly_dark", height=720,
        xaxis_rangeslider_visible=False,
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(color="#c8cee8"),
        legend=dict(orientation="h", y=1.02),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    fig.update_yaxes(title_text="Price",  row=1, col=1)
    fig.update_yaxes(title_text="MACD",   row=2, col=1)
    fig.update_yaxes(title_text="RSI",    row=3, col=1)
    fig.update_yaxes(title_text="Volume", row=4, col=1)
    st.plotly_chart(fig, width='stretch', config={"responsive": True})


# ─────────────────────────────────────────────────────────────────
# TAB 2 — FORECAST (Monte Carlo)
# ─────────────────────────────────────────────────────────────────
def _tab_forecast(ticker: str, df: pd.DataFrame, sig: dict,
                  cur_sym: str, info: dict):
    # ── Inline filter controls (localised to this tab) ────────────────
    fc1, fc2, _gap = st.columns([1.4, 1.4, 3])
    with fc1:
        st.markdown('<div style="font-size:0.72rem;color:#6b7a90;'
                    'letter-spacing:1px;text-transform:uppercase;'
                    'margin-bottom:4px">📅 Lookback Window</div>',
                    unsafe_allow_html=True)
        lookback_label = st.radio(
            "Lookback", ["30 days", "60 days", "90 days", "180 days"],
            index=2, horizontal=True, key=f"fc_lb_{ticker}",
            label_visibility="collapsed",
        )
    with fc2:
        st.markdown('<div style="font-size:0.72rem;color:#6b7a90;'
                    'letter-spacing:1px;text-transform:uppercase;'
                    'margin-bottom:4px">🔭 Forecast Horizon</div>',
                    unsafe_allow_html=True)
        horizon_label = st.radio(
            "Horizon", ["1M", "3M", "6M", "12M"],
            index=1, horizontal=True, key=f"fc_hz_{ticker}",
            label_visibility="collapsed",
        )

    lookback_days_map  = {"30 days": 30, "60 days": 60, "90 days": 90, "180 days": 180}
    fcast_days_map     = {"1M": 21,  "3M": 63,  "6M": 126, "12M": 252}
    lookback_days      = lookback_days_map[lookback_label]
    fcast_days         = fcast_days_map[horizon_label]

    st.markdown("<hr style='border-color:#1a2540;margin:8px 0 14px'>",
                unsafe_allow_html=True)
    _graph_help(
        f"Solid line = {lookback_label} price history",
        f"Dashed = {horizon_label} forecast direction",
        "Shaded band = confidence range (1.5× annualised vol)",
    )
    if df.empty or len(df) < 30:
        st.warning("Not enough price history for forecast.")
        return

    _cl      = _safe_close(df)
    if _cl.empty:
        st.warning("Price data unavailable — cannot build forecast. Try reloading or switching stocks.")
        return
    price    = safe_float(_cl.iloc[-1])
    hist     = _cl.tail(lookback_days)
    x        = np.arange(len(hist))
    z        = np.polyfit(x, hist.values, 1)
    fn       = np.poly1d(z)

    fx  = np.arange(len(hist), len(hist) + fcast_days)
    fv  = fn(fx)
    vol = float(hist.pct_change().std()) * float(hist.values[-1])
    vol_arr  = vol * np.sqrt(np.arange(1, fcast_days + 1))
    try:
        fc_dates = pd.bdate_range(df.index[-1] + timedelta(1),
                                  periods=fcast_days)
    except Exception:
        fc_dates = pd.date_range(df.index[-1] + timedelta(1),
                                 periods=fcast_days)
    fc = pd.DataFrame({
        "Date":     fc_dates,
        "Forecast": fv,
        "Upper":    fv + 1.5 * vol_arr,
        "Lower":    fv - 1.5 * vol_arr,
    })
    target = float(fc["Forecast"].iloc[-1])
    upside = (target - price) / price * 100 if price else 0

    # Store & resolve forecasts
    safe_run(lambda: store_forecast(ticker, fcast_days, target, price),
             context="forecast:store")
    safe_run(lambda: resolve_forecasts(ticker, price),
             context="forecast:resolve")

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=hist.index, y=hist,
        name="Historical", line=dict(color="#4f8ef7", width=2),
        fill="tozeroy", fillcolor="rgba(79,142,247,0.05)",
    ))
    fig2.add_trace(go.Scatter(
        x=fc["Date"], y=fc["Forecast"],
        name="Forecast", line=dict(color="#ffd600", width=2.5, dash="dash"),
    ))
    fig2.add_trace(go.Scatter(
        x=list(fc["Date"]) + list(fc["Date"])[::-1],
        y=list(fc["Upper"]) + list(fc["Lower"])[::-1],
        fill="toself", fillcolor="rgba(255,214,0,0.07)",
        line=dict(color="rgba(0,0,0,0)"), name="Confidence Band",
    ))
    fig2.add_annotation(
        x=str(fc["Date"].iloc[-1].date()), y=target,
        text=f"Target {cur_sym}{target:,.0f} ({upside:+.1f}%)",
        showarrow=True, arrowhead=2,
        font=dict(color="#ffd600", size=13),
        bgcolor="#1f2937", bordercolor="#ffd600",
    )
    fig2.update_layout(
        template="plotly_dark", height=420,
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(color="#c8cee8"),
        legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center"),
        margin=dict(l=10, r=10, t=20, b=10),
    )
    fig2.update_xaxes(title_text="Date")
    fig2.update_yaxes(title_text="Price")
    st.plotly_chart(fig2, width='stretch', config={"responsive": True})

    c1, c2, c3 = st.columns(3)
    c1.metric("Current Price", f"{cur_sym}{price:,.2f}", f"{upside:+.2f}%")
    c2.metric(f"Target ({sig['horizon']})",
              f"{cur_sym}{target:,.0f}", f"{upside:+.1f}%")
    c3.metric("52-Week Range",
              f"{cur_sym}{float(_cl.min()):,.0f}–{cur_sym}{float(_cl.max()):,.0f}")

    slope_pct = float(z[0]) / float(hist.iloc[0]) * 100 if hist.iloc[0] else 0
    rationale = [
        f"Trend slope {slope_pct:+.3f}% per day over 90 days — "
        f"{'upward' if slope_pct > 0 else 'downward'} bias in the forecast.",
        f"RSI at {sig['rsi']:.1f} — "
        f"{'oversold, recoveries often follow.' if sig['rsi'] < 35 else 'overbought, near-term resistance possible.' if sig['rsi'] > 70 else 'neutral, no extreme momentum.'}",
        f"MACD at {sig['macdh']:.3f} — "
        f"{'positive, buying momentum building.' if sig['macdh'] > 0 else 'negative, selling pressure present.'}",
        f"Price is {'above' if price > sig['sma50'] else 'below'} 50-day and "
        f"{'above' if price > sig['sma200'] else 'below'} 200-day average.",
        f"ATR daily average swing of {cur_sym}{sig['atr']:.2f} used to size the confidence band.",
        f"Band: Upper {cur_sym}{float(fc['Upper'].iloc[-1]):,.0f} · "
        f"Lower {cur_sym}{float(fc['Lower'].iloc[-1]):,.0f} (1.5× annualised vol).",
    ]
    st.markdown('<p class="section-title">📋 Forecast Rationale</p>',
                unsafe_allow_html=True)
    for item in rationale:
        st.markdown(
            f'<div class="insight-box" style="font-size:0.82rem">{sanitise(item, 300)}</div>',
            unsafe_allow_html=True,
        )
    st.markdown("---")
    render_forecast_accuracy(ticker, cur_sym)


# ─────────────────────────────────────────────────────────────────
# TAB 3 — COMPARE
# ─────────────────────────────────────────────────────────────────
def _tab_compare(ticker: str, name: str, df: pd.DataFrame,
                 compare_names: list, stock_map: dict, cb: int):
    # ── Inline Compare With filter (localised to this tab) ────────────
    from config import GROUPS, CURRENCY   # late import — avoids circular dep

    # Build a flat {display_label: (name, ticker)} map for the multiselect
    # Build flat {label: (name, ticker)} from stock_map {name: ticker}
    _flat: dict = {}
    for _n, _t in stock_map.items():
        if _t != ticker:
            _flat[f"{_n}  [{_t}]"] = (_n, _t)

    st.markdown('<div style="font-size:0.72rem;color:#6b7a90;'
                'letter-spacing:1px;text-transform:uppercase;'
                'margin-bottom:4px">📊 Compare With (select up to 4)</div>',
                unsafe_allow_html=True)
    cmp_col, _gap = st.columns([3, 1])
    with cmp_col:
        selected_labels = st.multiselect(
            "Compare With",
            options=list(_flat.keys()),
            default=[],
            max_selections=4,
            key=f"cmp_sel_{ticker}",
            label_visibility="collapsed",
            placeholder="Search and add stocks to compare…",
        )

    # Resolve selected labels → names + tickers
    compare_names = [_flat[lbl][0] for lbl in selected_labels if lbl in _flat]
    _extra_tickers = [_flat[lbl][1] for lbl in selected_labels if lbl in _flat]

    period_col, _gap2 = st.columns([1.6, 4])
    with period_col:
        st.markdown('<div style="font-size:0.72rem;color:#6b7a90;'
                    'letter-spacing:1px;text-transform:uppercase;'
                    'margin-bottom:4px">📅 Period</div>',
                    unsafe_allow_html=True)
        cmp_period = st.radio(
            "Period", ["3M", "6M", "1Y", "2Y", "5Y"],
            index=2, horizontal=True, key=f"cmp_period_{ticker}",
            label_visibility="collapsed",
        )

    period_yf_map = {"3M": "3mo", "6M": "6mo", "1Y": "1y",
                     "2Y": "2y",  "5Y": "5y"}
    yf_period = period_yf_map[cmp_period]

    st.markdown("<hr style='border-color:#1a2540;margin:8px 0 14px'>",
                unsafe_allow_html=True)
    _graph_help(
        f"All stocks indexed to 100 at start of {cmp_period} period",
        "Higher line = better relative return over the selected window",
        "Hover over any line to see exact normalised value",
    )

    all_names   = [name]   + compare_names
    all_tickers = [ticker] + _extra_tickers
    colors      = ["#4f8ef7","#00c853","#ffd600","#e040fb","#ff9800"]

    fig3 = go.Figure()
    for i, (nm, tk) in enumerate(zip(all_names, all_tickers)):
        d = get_price_data(tk, period=yf_period) if tk != ticker else df
        if d is None or d.empty:
            continue
        _cl  = _safe_close(d)
        norm = _cl / float(_cl.iloc[0]) * 100 if not _cl.empty else _cl
        ret  = (float(_cl.iloc[-1]) / float(_cl.iloc[0]) - 1) * 100 if len(_cl) >= 2 else 0
        fig3.add_trace(go.Scatter(
            x=d.index, y=norm,
            name=f"{sanitise(nm, 30)} ({ret:+.1f}%)",
            line=dict(color=colors[i % len(colors)], width=2),
        ))

    fig3.update_layout(
        template="plotly_dark", height=400,
        title=f"{cmp_period} Relative Performance (Base = 100)",
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(color="#c8cee8"),
        legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center"),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    fig3.update_xaxes(title_text="Date")
    fig3.update_yaxes(title_text="Normalised (100=start)")
    st.plotly_chart(fig3, width='stretch', config={"responsive": True})


# ─────────────────────────────────────────────────────────────────
# TAB 4 — INSIGHTS & ACTIONS
# ─────────────────────────────────────────────────────────────────
def _tab_insights(sig: dict, cur_sym: str, ticker: str, df: pd.DataFrame):
    _graph_help(
        "Plain-English verdict combining all signals",
        "Signal badge = overall call · Insights = what data says",
        "Actions = what to do · Caution = what to avoid",
    )
    rsi    = sig["rsi"]
    macdh  = sig["macdh"]
    _cl    = _safe_close(df)
    price  = safe_float(_cl.iloc[-1]) if not _cl.empty else 0
    sma50  = sig["sma50"]
    sma200 = sig["sma200"]
    adx    = sig["adx"]
    pe     = sig["pe"]
    roe    = sig["roe"]
    score  = sig["score"]

    # Compute upside again for insight copy
    hist = _safe_close(df).tail(90)
    x    = np.arange(len(hist))
    z    = np.polyfit(x, hist.values, 1) if len(hist) >= 2 else [0, 0]
    fn   = np.poly1d(z)
    fv   = fn(np.arange(len(hist), len(hist) + 126))
    target = float(fv[-1]) if len(fv) else price
    upside = (target - price) / price * 100 if price else 0

    insights, actions, cautions = [], [], []

    if rsi < 35:
        insights.append(f"<b>RSI {rsi:.1f}</b> — stock looks <b>oversold</b>. Often precedes a bounce.")
        actions.append("Consider starting a small position. Spread over 2–3 weeks to average cost.")
    elif rsi > 70:
        insights.append(f"<b>RSI {rsi:.1f}</b> — stock looks <b>overbought</b>. Upward momentum may slow.")
        cautions.append("Avoid fresh buying. If you hold, consider booking 30–40% of gains.")
    else:
        insights.append(f"<b>RSI {rsi:.1f}</b> — <b>neutral zone</b>. No extreme momentum signal.")

    if macdh > 0:
        insights.append(f"<b>MACD {macdh:+.3f}</b> — buying momentum building.")
        actions.append("Momentum is in your favour. Trend followers can hold or add.")
    else:
        insights.append(f"<b>MACD {macdh:+.3f}</b> — selling pressure stronger.")
        cautions.append("Wait until MACD turns positive before adding position.")

    if price > sma50 > sma200:
        insights.append("Price above both moving averages — <b>Golden Zone</b>. Long-term trend is up.")
        actions.append("Use pullbacks as buying opportunities.")
    elif price < sma50 and price < sma200:
        insights.append("Price below both averages — <b>downtrend</b>.")
        cautions.append("Wait for price to cross above the 50-day average before entering.")

    if adx > 25:
        insights.append(f"<b>ADX {adx:.1f}</b> — strong, clear trend direction confirmed.")
    else:
        insights.append(f"<b>ADX {adx:.1f}</b> — no clear trend, market moving sideways.")

    if upside > 10:
        insights.append(f"Forecast sees <b>{upside:.1f}% upside</b> over horizon.")
        actions.append("Positive forecast. Regular fixed investments reduce timing risk.")
    elif upside < -5:
        insights.append(f"Forecast shows <b>{upside:.1f}% downside risk</b> over horizon.")
        cautions.append("Negative forecast trend. Reduce exposure or wait for reversal signal.")

    if 0 < pe < 20:
        insights.append(f"<b>P/E {pe:.1f}x</b> — reasonably priced relative to earnings.")
        actions.append("Valuation is attractive. Long-term investors can accumulate.")
    elif pe > 40:
        insights.append(f"<b>P/E {pe:.1f}x</b> — expensive. High expectations already priced in.")
        cautions.append("High valuation leaves little room for error.")

    if roe > 18:
        insights.append(f"<b>ROE {roe:.1f}%</b> — very efficient at turning capital into profit.")
    elif 0 < roe < 8:
        insights.append(f"<b>ROE {roe:.1f}%</b> — low return on capital. Watch margin trends.")

    # Signal badge
    sig_col = sig["sigcolor"]
    st.markdown(
        f'<div style="background:{sig_col}15;border:1.5px solid {sig_col};' +
        f'border-radius:12px;padding:14px 18px;margin-bottom:14px">' +
        f'<div style="font-size:1.25rem;font-weight:900;color:{sig_col}">' +
        f'Overall Signal: {sanitise(sig["signal"])}</div>' +
        f'<div style="font-size:0.80rem;color:#9aa0b4;margin-top:6px">' +
        f'{"Strong signals align for a buy." if "BUY" in sig["signal"] else "Mixed signals — patience is the play." if "WATCH" in sig["signal"] else "Multiple warning signs — better opportunities likely ahead."}' +
        f'</div></div>',
        unsafe_allow_html=True,
    )

    ci, ca, cc = responsive_cols(3)
    with ci:
        st.markdown('<p class="section-title">🔍 What the data says</p>',
                    unsafe_allow_html=True)
        for ins in insights:
            st.markdown(
                f'<div class="insight-box">{sanitise_bold(ins, 400)}</div>',
                unsafe_allow_html=True,
            )
    with ca:
        st.markdown('<p class="section-title">✅ What to consider doing</p>',
                    unsafe_allow_html=True)
        for a in (actions or ["No strong action signal right now. Monitor and wait."]):
            st.markdown(
                f'<div class="action-box">{sanitise_bold(a, 400)}</div>',
                unsafe_allow_html=True,
            )
    with cc:
        st.markdown('<p class="section-title">⚠️ What to be careful about</p>',
                    unsafe_allow_html=True)
        for c in (cautions or ["No major red flags. Keep stop-losses in place."]):
            st.markdown(
                f'<div class="warn-box">{sanitise_bold(c, 400)}</div>',
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────────
def render_dashboard(ticker: str, name: str, country: str, cur_sym: str,
                     info: dict, df: pd.DataFrame, cb: int = 0,
                     compare_names: list = None, stock_map: dict = None,
                     market_open: bool = False):
    compare_names = compare_names or []
    stock_map     = stock_map or {}
    st.session_state["data_stale"] = False  # KI-017b: clear stale flag on load

    # Early OHLCV validation
    if not _has_ohlcv(df):
        st.error(
            f"⚠️ Price data for **{sanitise(ticker, 20)}** could not be loaded correctly. "
            "Columns received: " + str(list(df.columns) if df is not None and not df.empty else "empty") +
            "\n\nThis is usually a temporary yfinance issue. "
            "**Try selecting the stock again** or wait 30 seconds and refresh."
        )
        return

    # Compute indicators
    df = safe_run(
        lambda: compute_indicators(df),
        context="dashboard:compute_indicators", default=df,
    ) if not df.empty else df

    sig = safe_run(
        lambda: signal_score(df, info),
        context="dashboard:signal_score",
        default={"score": 0, "signal": "NO DATA", "sigcolor": "#6b7280",
                 "rsi": 50, "macdh": 0, "bbw": 0, "atr": 0, "adx": 20,
                 "stoch": 50, "obv": 0, "volm": 0, "sma50": 0, "sma200": 0,
                 "pe": 0, "pb": 0, "roe": 0, "revg": 0, "signals": [],
                 "horizon": "6M", "hreason": "", "macd": 0, "macds": 0,
                 "bb_pct": 0.5, "bbu": 0, "bbl": 0, "revg": 0},
    )

    _render_header(ticker, name, country, cur_sym, info, df, sig)
    _live_kpi_panel(sig, cur_sym)
    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Technical Charts",
        "🔮 Forecast",
        "⚖️ Compare",
        "💡 Insights & Actions",
    ])
    with tab1: _tab_charts(df, cur_sym)
    with tab2: _tab_forecast(ticker, df, sig, cur_sym, info)
    with tab3: _tab_compare(ticker, name, df, compare_names, stock_map, cb)
    with tab4: _tab_insights(sig, cur_sym, ticker, df)