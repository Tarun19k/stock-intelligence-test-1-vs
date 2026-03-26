# pages/dashboard.py — Phase 3: Full 4-tab dashboard
# Tabs: Technical Charts | Forecast | Compare | Insights & Actions
# Entry point: render_dashboard(ticker, name, country, cur_sym, info, df, cb)

import pytz
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

from utils import safe_float, sanitise, sanitise_bold, responsive_cols, log_error, safe_run, info_tip, section_title_with_tip
from indicators import (compute_indicators, signal_score,
                        compute_weinstein_stage, compute_elder_screens,
                        compute_forecast, compute_unified_verdict)
from market_data import get_price_data, get_news, get_live_price, get_intraday_chart_data
from config import HELP_TEXT, GROUPS, CURRENCY
from forecast import (
    store_forecast, resolve_forecasts,
    render_forecast_accuracy, get_weekly_accuracy_report,
)

# ─────────────────────────────────────────────────────────────────
# ASSET CLASS DETECTION
# ─────────────────────────────────────────────────────────────────
def _detect_asset_class(country: str, ticker: str, info: dict) -> str:
    """
    Returns: "equity" | "commodity" | "debt" | "index" | "etf" | "forex"
    Priority: yfinance quoteType → market name → ticker suffix
    """
    qt = (info.get("quoteType") or "").upper()
    if qt == "FUTURE":     return "commodity"
    if qt == "INDEX":      return "index"
    if qt == "ETF":        return "etf"
    if qt == "EQUITY":     return "equity"
    # Market name fallback
    if "Commodities" in country:    return "commodity"
    if "Debt" in country:           return "debt"
    if "Global Indices" in country: return "index"
    if "ETF" in country:            return "etf"
    # Ticker suffix fallback
    if ticker.endswith("=F"):       return "commodity"
    if ticker.startswith("^"):      return "index"
    if ticker.endswith("=X"):       return "forex"
    return "equity"




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
# HEADER — STATIC SECTION (name, sector, signal badge, score)
# Renders once. Never refreshes — these values don't change intraday.
# ─────────────────────────────────────────────────────────────────
def _render_header_static(ticker, name, country, cur_sym, info,
                           sig_data, verdict=None):
    """
    Static header: stock identity + unified verdict badge + momentum score.
    verdict: pre-computed dict from compute_unified_verdict().
    Falls back to raw sig_data if verdict not yet available.
    """
    mkt_cap  = safe_float(info.get("marketCap", 0))
    sector   = sanitise(info.get("sector") or info.get("quoteType", ""), 40)
    longname = sanitise(info.get("longName", name), 60)
    cap_str  = f"{cur_sym}{mkt_cap/1e9:.1f}B" if mkt_cap > 1e9 else "—"

    if verdict:
        fsig        = verdict["final_signal"]
        fcol        = verdict["final_color"]
        score       = verdict["raw_score"]
        reason      = sanitise(verdict.get("verdict_reason", ""), 160)
        confs       = verdict.get("conflicts", [])
        # Plain English — P1 Glancer must understand without reading tabs
        is_debt     = verdict.get("is_debt", False)
        if is_debt:
            align_icon  = "ℹ️"
            align_text  = "Yield instrument — see context below"
            align_color = "#4b6080"
        elif not confs:
            align_icon  = "✅"
            align_text  = "Trend and momentum agree"
            align_color = "#00c853"
        else:
            align_icon  = "⚠️"
            align_text  = "Momentum signal adjusted"
            align_color = "#ff9800"
    else:
        fsig        = sig_data["signal"]
        fcol        = sig_data["sigcolor"]
        score       = sig_data["score"]
        reason      = ""
        align_icon  = "ℹ️"
        align_text  = "Regime analysis pending"
        align_color = "#4b6080"

    tip_verdict = sanitise(HELP_TEXT["signal"], 400)
    tip_score   = sanitise(HELP_TEXT["score"],  400)
    tip_ticker  = sanitise(HELP_TEXT["ticker"], 400)

    st.markdown(
        f'<div style="color:#c8d6f0;background:linear-gradient(135deg,#111827,#1f2937);'
        f'border-radius:14px;padding:16px 28px 14px 28px;margin-bottom:4px;'
        f'border:1px solid #1f2d40">'
        f'<div style="font-size:0.74rem;color:#6b7280;margin-bottom:4px">'
        f'{sanitise(country)} · {sanitise(ticker, 20)} · {sector} · Mkt Cap {cap_str}</div>'
        f'<div style="font-size:1.85rem;font-weight:900;color:#fff">{longname}</div>'
        f'<div style="margin-top:12px;display:flex;align-items:flex-start;'
        f'gap:16px;flex-wrap:wrap">'
        f'<div>'
        f'<span title="{tip_verdict}" style="background:{fcol}22;'
        f'border:1.5px solid {fcol};border-radius:20px;'
        f'padding:5px 16px;color:{fcol};font-weight:800;'
        f'font-size:0.92rem;display:inline-block;margin-bottom:6px">'
        f'🎯 {sanitise(fsig)}</span>'
        f'<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:2px">'
        f'<span title="{tip_score}" style="background:#1a2332;'
        f'border:1px solid #2d3a5e;border-radius:6px;'
        f'padding:3px 10px;font-size:0.72rem;color:#9aa0b4;cursor:help">'
        f'Momentum: {score}/100</span>'
        f'<span style="font-size:0.72rem;color:{align_color};font-weight:600">'
        f'{align_icon} {align_text}</span>'
        f'<span title="{tip_ticker}" style="background:#1a2332;'
        f'border:1px solid #2d3a5e;border-radius:6px;'
        f'padding:3px 10px;font-size:0.72rem;color:#4f8ef7;'
        f'font-family:monospace;cursor:help">{sanitise(ticker, 20)}</span>'
        f'</div></div>'
        f'<div style="flex:1;min-width:200px">'
        f'<div style="font-size:0.79rem;color:#c8d6f0;line-height:1.5;'
        f'padding:8px 12px;background:#0d1117;border-radius:8px;'
        f'border-left:3px solid {fcol}44">{reason}</div>'
        f'</div></div></div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────
# LIVE PRICE TILE
# Fragment refreshes every 5s when market open, static when closed.
# Self-fetches get_live_price() — does NOT call st.rerun().
# Only this tile re-renders; all other content stays untouched.
# ─────────────────────────────────────────────────────────────────
def _render_price_tile(ticker: str, cur_sym: str, df: pd.DataFrame,
                       market_open: bool, live: dict):
    """Shared renderer — called by live fragment and closed-market fallback."""
    if live:
        price = live["price"]
        chg   = live["change_pct"]
        high  = live["day_high"]
        low   = live["day_low"]
        vol   = live["volume"]
        ts    = live.get("timestamp", "")[:16]
        badge = ('<span style="background:#00c85322;border:1px solid #00c853;'
                 'border-radius:12px;padding:2px 10px;font-size:0.70rem;'
                 'color:#00c853;font-weight:700">🟢 LIVE</span>')
    else:
        _cl   = _safe_close(df)
        price = safe_float(_cl.iloc[-1]) if not _cl.empty else 0
        prev  = safe_float(_cl.iloc[-2]) if len(_cl) >= 2 else price
        chg   = (price - prev) / prev * 100 if prev else 0
        high  = safe_float(df["High"].iloc[-1])   if "High"   in df.columns else price
        low   = safe_float(df["Low"].iloc[-1])    if "Low"    in df.columns else price
        vol   = safe_float(df["Volume"].iloc[-1]) if "Volume" in df.columns else 0
        ts    = ""
        badge = ('<span style="background:#ff174422;border:1px solid #ff1744;'
                 'border-radius:12px;padding:2px 10px;font-size:0.70rem;'
                 'color:#ff1744;font-weight:700">🔴 CLOSED</span>')

    chg_col = "#00c853" if chg >= 0 else "#ff1744"
    arrow   = "▲" if chg >= 0 else "▼"
    vol_str = (f"{vol/1e7:.2f}Cr" if vol >= 1e7
               else f"{vol/1e6:.2f}M" if vol >= 1e6
               else f"{vol:,.0f}")
    ts_str  = (f'<span style="font-size:0.68rem;color:#4b6080;margin-left:8px">{ts}</span>'
               if ts else "")

    st.markdown(
        f'<div style="background:linear-gradient(135deg,#0d1f35,#112240);'
        f'border-radius:12px;padding:14px 28px;margin-bottom:12px;'
        f'border:1px solid #1a3050;display:flex;align-items:center;gap:24px;flex-wrap:wrap">'
        f'<div>'
        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">'
        f'{badge}{ts_str}</div>'
        f'<span style="font-size:2.4rem;font-weight:900;color:#4f8ef7">'
        f'{cur_sym}{price:,.2f}</span>'
        f'<span style="font-size:1.1rem;color:{chg_col};font-weight:700;margin-left:12px">'
        f'{arrow} {abs(chg):.2f}% today</span>'
        f'</div>'
        f'<div style="display:flex;gap:20px;flex-wrap:wrap">'
        f'<div style="text-align:center">'
        f'<div style="font-size:0.68rem;color:#4b6080;text-transform:uppercase">Day High</div>'
        f'<div style="font-size:0.92rem;color:#00c853;font-weight:700">{cur_sym}{high:,.2f}</div>'
        f'</div>'
        f'<div style="text-align:center">'
        f'<div style="font-size:0.68rem;color:#4b6080;text-transform:uppercase">Day Low</div>'
        f'<div style="font-size:0.92rem;color:#ff1744;font-weight:700">{cur_sym}{low:,.2f}</div>'
        f'</div>'
        f'<div style="text-align:center">'
        f'<div style="font-size:0.68rem;color:#4b6080;text-transform:uppercase">Volume</div>'
        f'<div style="font-size:0.92rem;color:#c8d6f0;font-weight:700">{vol_str}</div>'
        f'</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _make_live_price_fragment(ticker: str, cur_sym: str,
                               df: pd.DataFrame, market_open: bool):
    """
    Factory that returns a @st.fragment scoped to current ticker.
    run_every=5 when market open → self-fetches live price every 5s in place.
    run_every=None when closed  → renders once from df, no polling.
    Does NOT call st.rerun() — only the tile itself re-renders.
    """
    interval = 5 if market_open else None

    @st.fragment(run_every=interval)
    def _live_price_tile():
        live = {}
        if market_open:
            live = safe_run(
                lambda: get_live_price(ticker),
                context=f"live_price:{ticker}", default={}
            )
        _render_price_tile(ticker, cur_sym, df, market_open, live)

    return _live_price_tile


# ─────────────────────────────────────────────────────────────────
# KPI SIGNAL PANEL
# ─────────────────────────────────────────────────────────────────
def _render_kpi_panel(sig: dict, cur_sym: str, asset_class: str = "equity"):
    """
    Momentum Signal Panel — shows pre-regime-filter technical indicators.
    P/E and ROE suppressed for non-equity asset classes.
    asset_class: "equity" | "commodity" | "index" | "debt" | "etf"
    """
    st.markdown(
        section_title_with_tip(
            "📊 Momentum Signal Panel",
            HELP_TEXT["score"]
        ),
        unsafe_allow_html=True,
    )
    # Label so user knows this is pre-regime-filter
    st.markdown(
        '<div style="font-size:0.72rem;color:#4b6080;margin:-8px 0 10px">'
        'Technical momentum indicators only — see verdict badge above for final signal</div>',
        unsafe_allow_html=True,
    )

    def _color(val, green_cond, red_cond):
        if green_cond(val): return "green"
        if red_cond(val):   return "red"
        return "yellow"

    show_fundamentals = asset_class in ("equity", "etf")

    row1 = responsive_cols(4)
    _kpi(row1[0], "RSI 14",
         f'{sig["rsi"]:.1f}',
         _color(sig["rsi"], lambda v: v < 40, lambda v: v > 70),
         tip=HELP_TEXT["rsi"])
    _kpi(row1[1], "MACD Histogram",
         f'{sig["macdh"]:.3f}',
         _color(sig["macdh"], lambda v: v > 0, lambda v: v < 0),
         tip=HELP_TEXT["macd_h"])
    _kpi(row1[2], "Bollinger Width",
         f'{sig["bbw"]:.1f}%', "yellow",
         tip=HELP_TEXT["bbw"])
    _kpi(row1[3], "ATR Volatility",
         f'{cur_sym}{sig["atr"]:.2f}', "yellow",
         tip=HELP_TEXT["atr"])

    # Row 2: fundamentals shown only for equity/etf
    if show_fundamentals:
        row2 = responsive_cols(5)
        _kpi(row2[0], "ADX Trend",
             f'{sig["adx"]:.1f}',
             _color(sig["adx"], lambda v: v > 25, lambda v: v < 15),
             tip=HELP_TEXT["adx"])
        _kpi(row2[1], "Stochastic %K",
             f'{sig["stoch"]:.1f}',
             _color(sig["stoch"], lambda v: v < 30, lambda v: v > 75),
             tip=HELP_TEXT["stoch"])
        pe_str = f'{sig["pe"]:.1f}x' if sig["pe"] > 0 else "N/A"
        _kpi(row2[2], "P/E · P/B",
             f'{pe_str} · {sig["pb"]:.2f}x',
             _color(sig["pe"], lambda v: 0 < v < 22, lambda v: v > 40),
             tip=HELP_TEXT["pe_pb"])
        _kpi(row2[3], "ROE · Rev Growth",
             f'{sig["roe"]:.1f}% · {sig["revg"]:.1f}%',
             _color(sig["roe"], lambda v: v > 15, lambda v: v < 5),
             tip=HELP_TEXT["roe_revg"])
        _kpi(row2[4], "OBV · Volume",
             f'{sig["obv"]:.1f}M · {sig["volm"]:.1f}M', "",
             tip=HELP_TEXT["obv_vol"])
    elif asset_class == "debt":
        # Yield instruments need context, not momentum colouring.
        # RSI/ATR/BBW shown as-is — no green/red buy/sell interpretation.
        # P/E, MACD-as-signal, ADX-trend all suppressed.
        _cl_close = sig.get("rsi", 50)
        st.markdown(
            '<div style="font-size:0.76rem;color:#ff9800;font-weight:600;'
            'background:#1a1200;border-radius:6px;padding:8px 12px;margin:-4px 0 10px">'            '⚠️ This is a yield instrument. Rising RSI/MACD means yields are rising — '            'which means bond prices are falling. These signals do not indicate a BUY.'            '</div>',
            unsafe_allow_html=True,
        )
        row2 = responsive_cols(3)
        _kpi(row2[0], "RSI (Yield)",
             f'{sig["rsi"]:.1f}', "yellow",
             tip="RSI on a yield instrument: rising RSI = rising yields = falling bond prices. Not a buy signal.")
        _kpi(row2[1], "ATR Volatility",
             f'{cur_sym}{sig["atr"]:.2f}', "yellow",
             tip=HELP_TEXT["atr"])
        _kpi(row2[2], "Bollinger Width",
             f'{sig["bbw"]:.1f}%', "yellow",
             tip=HELP_TEXT["bbw"])
        st.markdown(
            '<div style="font-size:0.76rem;color:#4b6080;'
            'background:#0d1117;border-radius:6px;padding:8px 12px;margin-top:4px">'            'ℹ️ MACD, ADX, Stochastic, P/E, ROE are not applicable for debt & rate instruments. '            'See the Insights tab for yield context.'            '</div>',
            unsafe_allow_html=True,
        )
    else:
        row2 = responsive_cols(3)
        _kpi(row2[0], "ADX Trend",
             f'{sig["adx"]:.1f}',
             _color(sig["adx"], lambda v: v > 25, lambda v: v < 15),
             tip=HELP_TEXT["adx"])
        _kpi(row2[1], "Stochastic %K",
             f'{sig["stoch"]:.1f}',
             _color(sig["stoch"], lambda v: v < 30, lambda v: v > 75),
             tip=HELP_TEXT["stoch"])
        _kpi(row2[2], "OBV · Volume",
             f'{sig["obv"]:.1f}M · {sig["volm"]:.1f}M', "",
             tip=HELP_TEXT["obv_vol"])
        st.markdown(
            f'<div style="font-size:0.76rem;color:#4b6080;'
            f'background:#0d1117;border-radius:6px;padding:8px 12px;margin-top:4px">'
            f'ℹ️ P/E, P/B, ROE and Revenue Growth are not applicable '
            f'for {asset_class} instruments.</div>',
            unsafe_allow_html=True,
        )



# ─────────────────────────────────────────────────────────────────
# TAB 1 — TECHNICAL CHARTS
# ─────────────────────────────────────────────────────────────────

def _make_live_kpi_fragment(ticker: str, cur_sym: str, info: dict, market_open: bool, asset_class: str = "equity"):
    """
    Factory: returns @st.fragment that re-fetches and re-computes KPIs.
    run_every=60 when market open, None when closed.
    Self-contained — does not rely on sig passed from parent render.
    """
    interval = 60 if market_open else None

    @st.fragment(run_every=interval)
    def _live_kpi_panel():
        df_fresh = safe_run(
            lambda: get_price_data(ticker, cache_buster=int(__import__("time").time() // 60)),
            context=f"kpi_fragment:{ticker}", default=pd.DataFrame()
        )
        if df_fresh is not None and not df_fresh.empty:
            df_ind = safe_run(lambda: compute_indicators(df_fresh),
                              context="kpi_fragment:indicators", default=df_fresh)
            sig_fresh = safe_run(lambda: signal_score(df_ind, info),
                                 context="kpi_fragment:signal",
                                 default={"score": 0, "signal": "NO DATA",
                                          "sigcolor": "#6b7280", "rsi": 50,
                                          "macdh": 0, "bbw": 0, "atr": 0,
                                          "adx": 20, "stoch": 50, "obv": 0,
                                          "volm": 0, "sma50": 0, "sma200": 0,
                                          "pe": 0, "pb": 0, "roe": 0, "revg": 0,
                                          "signals": [], "macd": 0, "macds": 0,
                                          "bb_pct": 0.5, "bbu": 0, "bbl": 0})
            _render_kpi_panel(sig_fresh, cur_sym, asset_class)
        else:
            st.caption("KPI data temporarily unavailable.")

    return _live_kpi_panel

def _tab_charts(df: pd.DataFrame, cur_sym: str,
                ticker: str = "", market_open: bool = False):
    # ── Intraday live chart (market open only) ────────────────────
    if market_open and ticker:
        @st.fragment(run_every=60)
        def _intraday_chart():
            df_intra = safe_run(
                lambda: get_intraday_chart_data(ticker),
                context=f"intraday:{ticker}", default=pd.DataFrame()
            )
            if df_intra is None or df_intra.empty:
                st.caption("Intraday data loading…")
                return
            _cl = df_intra["Close"]
            if isinstance(_cl, pd.DataFrame):
                _cl = _cl.iloc[:, 0]
            fig_intra = go.Figure()
            fig_intra.add_trace(go.Candlestick(
                x=df_intra.index,
                open=df_intra["Open"], high=df_intra["High"],
                low=df_intra["Low"],  close=df_intra["Close"],
                name="Today",
                increasing_line_color="#00c853",
                decreasing_line_color="#ff1744",
            ))
            # VWAP line
            if "Volume" in df_intra.columns:
                vwap = (df_intra["Close"] * df_intra["Volume"]).cumsum() / df_intra["Volume"].cumsum()
                fig_intra.add_trace(go.Scatter(
                    x=df_intra.index, y=vwap,
                    name="VWAP", line=dict(color="#ffd600", width=1.5, dash="dot"),
                ))
            fig_intra.update_layout(
                template="plotly_dark", height=300,
                xaxis_rangeslider_visible=False,
                paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
                font=dict(color="#c8cee8"),
                legend=dict(orientation="h", y=1.05),
                margin=dict(l=10, r=10, t=10, b=10),
                title=dict(text="📡 Today — 1 min candles + VWAP  (refreshes every 60s)",
                           font=dict(size=12, color="#6b7280"), x=0),
            )
            fig_intra.update_xaxes(gridcolor="#1f2540")
            fig_intra.update_yaxes(gridcolor="#1f2540")
            st.plotly_chart(fig_intra, config={"responsive": True})

        _intraday_chart()
        st.divider()

    # ── Daily historical chart ────────────────────────────────────
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

    # Dynamic subplot layout — only render panels for available indicators
    _has_macd = "MACDH" in dp.columns and not dp["MACDH"].isna().all()
    _has_rsi  = "RSI"   in dp.columns and not dp["RSI"].isna().all()

    if _has_macd and _has_rsi:
        _rows, _heights, _titles = 4, [0.46, 0.20, 0.20, 0.14], ["Price · Bollinger · MAs", "MACD", "RSI", "Volume"]
        _row_macd, _row_rsi, _row_vol = 2, 3, 4
    elif _has_macd:
        _rows, _heights, _titles = 3, [0.55, 0.28, 0.17], ["Price · Bollinger · MAs", "MACD", "Volume"]
        _row_macd, _row_rsi, _row_vol = 2, None, 3
    elif _has_rsi:
        _rows, _heights, _titles = 3, [0.55, 0.28, 0.17], ["Price · Bollinger · MAs", "RSI", "Volume"]
        _row_macd, _row_rsi, _row_vol = None, 2, 3
    else:
        _rows, _heights, _titles = 2, [0.75, 0.25], ["Price · Bollinger · MAs", "Volume"]
        _row_macd, _row_rsi, _row_vol = None, None, 2
        st.caption("ℹ️ Technical indicators not available for this data — showing price and volume only.")

    fig = make_subplots(
        rows=_rows, cols=1, shared_xaxes=True,
        row_heights=_heights,
        vertical_spacing=0.03,
        subplot_titles=_titles,
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
        ), row=_row_macd, col=1)
        fig.add_trace(go.Scatter(
            x=dp.index, y=dp["MACD"], name="MACD",
            line=dict(color="#4fc3f7", width=1.2),
        ), row=_row_macd, col=1)
        fig.add_trace(go.Scatter(
            x=dp.index, y=dp["MACDS"], name="Signal",
            line=dict(color="#ffd600", width=1.2, dash="dash"),
        ), row=_row_macd, col=1)
    # RSI
    if "RSI" in dp.columns:
        fig.add_trace(go.Scatter(
            x=dp.index, y=dp["RSI"], name="RSI",
            line=dict(color="#e040fb", width=1.8),
            fill="tozeroy", fillcolor="rgba(224,64,251,0.05)",
        ), row=_row_rsi, col=1)
        fig.add_hline(y=70, row=_row_rsi, col=1,
                      line_dash="dot", line_color="#ff1744", line_width=0.8)
        fig.add_hline(y=30, row=_row_rsi, col=1,
                      line_dash="dot", line_color="#00c853", line_width=0.8)
    # Volume
    vc = ["#00c853" if dp["Close"].iloc[i] >= dp["Close"].iloc[max(i-1,0)] else "#ff1744"
          for i in range(len(dp))]
    fig.add_trace(go.Bar(
        x=dp.index, y=dp["Volume"], marker_color=vc,
        name="Volume", opacity=0.6,
    ), row=_row_vol, col=1)

    fig.update_layout(
        template="plotly_dark", height=720,
        xaxis_rangeslider_visible=False,
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(color="#c8cee8"),
        legend=dict(orientation="h", y=1.02),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    fig.update_yaxes(title_text="Price",  row=1, col=1)
    if _row_macd: fig.update_yaxes(title_text="MACD",   row=_row_macd, col=1)
    if _row_rsi:  fig.update_yaxes(title_text="RSI",    row=_row_rsi,  col=1)
    fig.update_yaxes(title_text="Volume", row=_row_vol, col=1)
    st.plotly_chart(fig, config={"responsive": True})


# ─────────────────────────────────────────────────────────────────
# TAB 2 — FORECAST (Historical Simulation Engine v5.19)
# Replaces polyfit with bootstrapped historical returns.
# P(gain) is the headline. Probability fan replaces single target line.
# Max horizon: 63 days (3M) — statistically honest.
# ─────────────────────────────────────────────────────────────────
def _tab_forecast(ticker: str, df: pd.DataFrame, sig: dict,
                  cur_sym: str, info: dict):

    # ── Horizon selector (1M or 3M only) ─────────────────────────
    fc_col, _gap = st.columns([2, 4])
    with fc_col:
        st.markdown('<div style="font-size:0.72rem;color:#6b7a90;'
                    'letter-spacing:1px;text-transform:uppercase;'
                    'margin-bottom:4px">🔭 Forecast Horizon</div>',
                    unsafe_allow_html=True)
        horizon_label = st.radio(
            "Horizon", ["1M (21 days)", "3M (63 days)"],
            index=1, horizontal=True, key=f"fc_hz_{ticker}",
            label_visibility="collapsed",
        )
    horizon_days = 21 if "1M" in horizon_label else 63

    st.markdown("<hr style='border-color:#1a2540;margin:8px 0 14px'>",
                unsafe_allow_html=True)
    _graph_help(
        "2,000 bootstrapped paths from this stock's own return history",
        "P(gain) = probability price is higher at horizon than today",
        "Inner band = central 50% of outcomes  |  Outer band = 80%",
        "Max 3M horizon — beyond this, uncertainty dominates direction",
    )

    if df is None or df.empty or len(df) < 30:
        st.warning("Not enough price history for forecast.")
        return
    _cl = _safe_close(df)
    if _cl.empty:
        st.warning("Price data unavailable.")
        return
    price = safe_float(_cl.iloc[-1])

    # ── Run engine ────────────────────────────────────────────────
    fcast = safe_run(
        lambda: compute_forecast(df, horizon_days=horizon_days, n_simulations=2000),
        context=f"forecast:compute:{ticker}", default=None
    )
    if not fcast or fcast.get("p50") is None:
        st.warning("Forecast engine returned insufficient data.")
        return

    p10, p25, p50 = fcast["p10"], fcast["p25"], fcast["p50"]
    p75, p90      = fcast["p75"], fcast["p90"]
    p_gain        = fcast["p_gain"]
    hw_est        = fcast["holt_estimate"]
    ann_vol       = fcast["annualised_vol_pct"]
    warning_txt   = fcast.get("warning")

    # Store & resolve
    safe_run(lambda: store_forecast(ticker, horizon_days, p50, price, simulation=fcast),
             context="forecast:store")
    safe_run(lambda: resolve_forecasts(ticker, price), context="forecast:resolve")

    if warning_txt:
        st.markdown(
            f'<div class="warn-box" style="font-size:0.82rem">'
            f'⚠️ {sanitise(warning_txt)}</div>',
            unsafe_allow_html=True)

    # ── Headline P(gain) card ─────────────────────────────────────
    pg_col   = "#00c853" if p_gain >= 55 else "#ff9800" if p_gain >= 45 else "#ff1744"
    pg_label = ("Leans bullish" if p_gain >= 55
                else "Roughly balanced" if p_gain >= 45 else "Leans bearish")
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#0d1f35,#112240);'
        f'border-radius:12px;padding:16px 24px;margin-bottom:14px;'
        f'border:1px solid {pg_col}44;display:flex;align-items:center;'
        f'gap:24px;flex-wrap:wrap">'
        f'<div>'
        f'<div style="font-size:0.70rem;color:#6b7080;text-transform:uppercase;'
        f'letter-spacing:1px;margin-bottom:4px">P(Gain) in {horizon_days} days</div>'
        f'<div style="font-size:2.6rem;font-weight:900;color:{pg_col}">{p_gain:.0f}%</div>'
        f'<div style="font-size:0.80rem;color:{pg_col};margin-top:2px">{pg_label}</div>'
        f'</div>'
        f'<div style="display:flex;flex-direction:column;gap:6px">'
        f'<div style="font-size:0.72rem;color:#4b6080">2,000 bootstrapped paths</div>'
        f'<div style="font-size:0.72rem;color:#4b6080">Annualised vol: {ann_vol:.1f}%/yr</div>'
        f'<div style="font-size:0.72rem;color:#4b6080">Method: Historical Simulation</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # ── Probability fan chart ─────────────────────────────────────
    try:
        fc_dates = pd.bdate_range(df.index[-1] + timedelta(1), periods=horizon_days)
    except Exception:
        fc_dates = pd.date_range(df.index[-1] + timedelta(1), periods=horizon_days)

    hist_display = _cl.tail(60)

    def _fan(p_target, n):
        return np.linspace(price, p_target, n)

    fig2 = go.Figure()
    # Historical
    fig2.add_trace(go.Scatter(
        x=hist_display.index, y=hist_display,
        name="Historical", line=dict(color="#4f8ef7", width=2),
        fill="tozeroy", fillcolor="rgba(79,142,247,0.04)",
    ))
    # Outer P10–P90 band
    fig2.add_trace(go.Scatter(
        x=list(fc_dates) + list(fc_dates)[::-1],
        y=list(_fan(p90, horizon_days)) + list(_fan(p10, horizon_days))[::-1],
        fill="toself", fillcolor="rgba(255,152,0,0.06)",
        line=dict(color="rgba(0,0,0,0)"), name="P10–P90 (80%)",
    ))
    # Inner P25–P75 band
    fig2.add_trace(go.Scatter(
        x=list(fc_dates) + list(fc_dates)[::-1],
        y=list(_fan(p75, horizon_days)) + list(_fan(p25, horizon_days))[::-1],
        fill="toself", fillcolor="rgba(255,152,0,0.14)",
        line=dict(color="rgba(0,0,0,0)"), name="P25–P75 (50%)",
    ))
    # Median
    fig2.add_trace(go.Scatter(
        x=fc_dates, y=_fan(p50, horizon_days),
        name="Median (P50)", line=dict(color="#ffd600", width=2.5, dash="dash"),
    ))
    # Holt-Winters
    if hw_est is not None:
        fig2.add_trace(go.Scatter(
            x=fc_dates, y=_fan(hw_est, horizon_days),
            name="Holt-Winters trend", line=dict(color="#e040fb", width=1.5, dash="dot"),
        ))
    fig2.add_annotation(
        x=str(fc_dates[-1].date()), y=p50,
        text=f"Median {cur_sym}{p50:,.0f} ({(p50-price)/price*100:+.1f}%)",
        showarrow=True, arrowhead=2,
        font=dict(color="#ffd600", size=12),
        bgcolor="#1f2937", bordercolor="#ffd600",
    )
    fig2.update_layout(
        template="plotly_dark", height=420,
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(color="#c8cee8"),
        legend=dict(orientation="h", y=1.06, x=0.5, xanchor="center"),
        margin=dict(l=10, r=10, t=20, b=10),
    )
    fig2.update_xaxes(title_text="Date", gridcolor="#1f2540")
    fig2.update_yaxes(title_text="Price", gridcolor="#1f2540")
    st.plotly_chart(fig2, config={"responsive": True})

    # ── Percentile cards ──────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    def _pct_card(col, label, val, color):
        delta = (val - price) / price * 100 if price else 0
        col.markdown(
            f'<div class="kpi-card" style="border-left-color:{color};text-align:center">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value" style="font-size:1.1rem">{cur_sym}{val:,.0f}</div>'
            f'<div class="kpi-delta" style="color:{color}">{delta:+.1f}%</div>'
            f'</div>', unsafe_allow_html=True)
    _pct_card(c1, "Bear (P10)", p10, "#ff1744")
    _pct_card(c2, "Down (P25)", p25, "#ff7043")
    _pct_card(c3, "Base (P50)", p50, "#ffd600")
    _pct_card(c4, "Up   (P75)", p75, "#4f8ef7")
    _pct_card(c5, "Bull (P90)", p90, "#00c853")

    st.markdown(
        f'<div class="graph-help" style="margin-top:12px">'
        f'📌 <b>Method:</b> <span title="{sanitise(HELP_TEXT["hist_sim"], 400)}" '
        f'style="cursor:help">Historical Simulation ℹ️</span> — '
        f'2,000 bootstrapped paths from this stock\'s actual return history. '
        'No normal distribution assumed — fat tails preserved. '
        'Holt-Winters damped trend is a secondary single-number estimate. '
        'Does not account for upcoming earnings or macro events.'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    render_forecast_accuracy(ticker, cur_sym)


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
        d = safe_run(
            lambda t=tk: get_price_data(t, period=yf_period, cache_buster=cb),
            context=f"compare:{tk}", default=None,
        ) if tk != ticker else df
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
    st.plotly_chart(fig3, config={"responsive": True})


# ─────────────────────────────────────────────────────────────────
# TAB 4 — INSIGHTS & ACTIONS (Unified Verdict v5.19)
# Weinstein Stage + Elder Triple Screen gate the momentum score.
# Conflicts are surfaced explicitly before any recommendation.
# ─────────────────────────────────────────────────────────────────
def _tab_insights(sig: dict, cur_sym: str, ticker: str, df: pd.DataFrame,
                  stage: dict = None, elder: dict = None,
                  fcast: dict = None, verdict: dict = None):

    # ── Use pre-computed from render_dashboard, or recompute if standalone ──
    _stage_def  = {"stage": 0, "label": "Unknown", "description": "",
                   "signal_veto": None, "price_vs_ma_pct": 0.0,
                   "ma_slope": 0.0, "ma30w": None}
    _elder_def  = {"weekly_bull": True, "weekly_tide_label": "Unknown",
                   "elder_verdict": "NEUTRAL", "elder_description": "",
                   "suppress_buy": False, "daily_rsi": 50.0,
                   "weekly_hist_now": 0.0, "weekly_hist_prev": 0.0}
    _fcast_def  = {"p_gain": None, "p50": None, "horizon_days": 63}
    _verd_def   = {"final_signal": sig.get("signal", "NO DATA"),
                   "final_color": sig.get("sigcolor", "#6b7280"),
                   "conflicts": [], "verdict_reason": "", "horizon_note": "",
                   "raw_score": sig.get("score", 0), "stage_label": "",
                   "elder_verdict": ""}

    stage   = stage   or safe_run(lambda: compute_weinstein_stage(df),
                                  context="insights:stage", default=_stage_def)
    elder   = elder   or safe_run(lambda: compute_elder_screens(df),
                                  context="insights:elder", default=_elder_def)
    fcast   = fcast   or safe_run(lambda: compute_forecast(df, horizon_days=63),
                                  context="insights:fcast", default=_fcast_def)
    verdict = verdict or safe_run(lambda: compute_unified_verdict(sig, stage, elder, fcast, asset_class=asset_class),
                                  context="insights:verdict", default=_verd_def)

    fsig   = verdict["final_signal"]
    fcol   = verdict["final_color"]
    confs  = verdict["conflicts"]
    reason = verdict["verdict_reason"]

    # ── Conflict banners (shown FIRST — most important) ───────────
    if confs:
        for c in confs:
            st.markdown(
                f'<div style="background:#2a1500;border:1px solid #ff6d00;'
                f'border-radius:10px;padding:14px 18px;margin-bottom:10px">'
                f'<div style="font-size:0.78rem;font-weight:700;color:#ff6d00;'
                f'margin-bottom:6px">⚡ Signal Conflict Detected '
                f'<span title="{sanitise(HELP_TEXT["conflict"], 400)}" '
                f'style="cursor:help;font-size:0.72rem">ℹ️</span></div>'
                f'<div style="font-size:0.82rem;color:#ffcc80;line-height:1.6">'
                f'{sanitise_bold(c, 600)}</div></div>',
                unsafe_allow_html=True,
            )

    # ── Unified verdict card ──────────────────────────────────────
    verdict_sub = ("All systems aligned — trend, momentum, and weekly tide agree."
                   if not confs else "Proceed with caution — conflicting signals present.")
    st.markdown(
        f'<div style="background:{fcol}12;border:1.5px solid {fcol};'
        f'border-radius:12px;padding:16px 20px;margin-bottom:16px">'
        f'<div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">'
        f'<div>'
        f'<div style="font-size:1.35rem;font-weight:900;color:{fcol}">'
        f'🎯 {sanitise(fsig)}</div>'
        f'<div style="font-size:0.80rem;color:#9aa0b4;margin-top:4px">{sanitise(verdict_sub)}</div>'
        f'</div>'
        f'<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:6px">'
        f'<span style="background:#1a2332;border:1px solid #2d3a5e;border-radius:6px;'
        f'padding:3px 10px;font-size:0.72rem;color:#9aa0b4">'
        f'Score {verdict["raw_score"]}/100</span>'
        f'<span style="background:#1a2332;border:1px solid #2d3a5e;border-radius:6px;'
        f'padding:3px 10px;font-size:0.72rem;color:#9aa0b4">'
        f'{sanitise(stage.get("label",""), 30)}</span>'
        f'<span style="background:#1a2332;border:1px solid #2d3a5e;border-radius:6px;'
        f'padding:3px 10px;font-size:0.72rem;color:#9aa0b4">'
        f'{sanitise(elder.get("weekly_tide_label",""), 30)}</span>'
        f'</div></div>'
        f'<div style="font-size:0.80rem;color:#c8d6f0;margin-top:10px;line-height:1.6">'
        f'{sanitise(reason, 300)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Regime detail row ─────────────────────────────────────────
    r1, r2 = st.columns(2)
    with r1:
        st.markdown(section_title_with_tip('📊 Weinstein Stage', HELP_TEXT['weinstein_stage']),
                    unsafe_allow_html=True)
        stage_colors = {1: "#ff9800", 2: "#00c853", 3: "#ff9800", 4: "#ff1744", 0: "#6b7280"}
        sc = stage_colors.get(stage.get("stage", 0), "#6b7280")
        st.markdown(
            f'<div class="insight-box" style="border-left:3px solid {sc}">'
            f'<div style="font-weight:700;color:{sc};margin-bottom:6px">'
            f'{sanitise(stage.get("label",""), 40)}</div>'
            f'<div style="font-size:0.80rem;color:#c8d6f0">'
            f'{sanitise(stage.get("description",""), 300)}</div>'
            f'</div>', unsafe_allow_html=True)
    with r2:
        st.markdown(section_title_with_tip('🌊 Elder Triple Screen', HELP_TEXT['elder_screen']),
                    unsafe_allow_html=True)
        ec = "#00c853" if elder.get("weekly_bull") else "#ff1744"
        st.markdown(
            f'<div class="insight-box" style="border-left:3px solid {ec}">'
            f'<div style="font-weight:700;color:{ec};margin-bottom:6px">'
            f'{sanitise(elder.get("elder_verdict",""), 30)} · '
            f'{sanitise(elder.get("weekly_tide_label",""), 30)}</div>'
            f'<div style="font-size:0.80rem;color:#c8d6f0">'
            f'{sanitise(elder.get("elder_description",""), 300)}</div>'
            f'</div>', unsafe_allow_html=True)

    st.divider()

    # ── Supporting evidence (from raw momentum score) ─────────────
    _cl   = _safe_close(df)
    price = safe_float(_cl.iloc[-1]) if not _cl.empty else 0
    rsi   = sig["rsi"]; macdh = sig["macdh"]
    sma50 = sig["sma50"]; sma200 = sig["sma200"]
    adx   = sig["adx"]; pe = sig["pe"]; roe = sig["roe"]

    p_gain = fcast.get("p_gain")
    p50    = fcast.get("p50")

    insights, actions, cautions = [], [], []

    if rsi < 35:
        insights.append(f"<b>RSI {rsi:.1f}</b> — oversold. Short-term bounce setups often follow.")
        actions.append("If regime is Stage 2, oversold RSI = low-risk entry. Spread over 2–3 weeks.")
    elif rsi > 70:
        insights.append(f"<b>RSI {rsi:.1f}</b> — overbought. Upward momentum may be exhausting.")
        cautions.append("Avoid fresh buying at these levels. Consider trimming if you hold.")
    else:
        insights.append(f"<b>RSI {rsi:.1f}</b> — neutral momentum zone.")

    if macdh > 0:
        insights.append(f"<b>MACD histogram {macdh:+.3f}</b> — buying momentum building.")
        if "BUY" in fsig: actions.append("Momentum aligned with verdict. Trend followers can hold or add.")
    else:
        insights.append(f"<b>MACD histogram {macdh:+.3f}</b> — selling pressure present.")
        cautions.append("Wait for MACD histogram to turn positive before adding exposure.")

    if price > sma50 > sma200:
        insights.append("Price above SMA50 and SMA200 — <b>Golden Zone</b>. Long-term uptrend intact.")
        if "BUY" in fsig: actions.append("Pullbacks toward SMA50 are buying opportunities in this regime.")
    elif price < sma50 and price < sma200:
        insights.append("Price below both moving averages — momentum structurally weak.")
        cautions.append("Wait for price to reclaim the 50-day average before considering entry.")

    if adx > 25:
        insights.append(f"<b>ADX {adx:.1f}</b> — strong trend direction confirmed.")
    else:
        insights.append(f"<b>ADX {adx:.1f}</b> — no confirmed trend. Market ranging.")

    if p_gain is not None:
        pg_str = f"{p_gain:.0f}%"
        if p_gain >= 60:
            insights.append(f"Historical simulation: <b>{pg_str} probability of gain</b> in 63 days.")
            if "BUY" in fsig: actions.append(f"Forecast and signal aligned. P(gain) = {pg_str}.")
        elif p_gain <= 40:
            insights.append(f"Historical simulation: only <b>{pg_str} probability of gain</b> in 63 days.")
            cautions.append(f"Forecast leans negative ({pg_str} P(gain)). Sized positions smaller.")
        else:
            insights.append(f"Historical simulation: roughly balanced odds ({pg_str} P(gain)).")

    if 0 < pe < 20:
        insights.append(f"<b>P/E {pe:.1f}x</b> — reasonable valuation relative to earnings.")
        actions.append("Valuation is supportive for long-term accumulation.")
    elif pe > 40:
        insights.append(f"<b>P/E {pe:.1f}x</b> — expensive. High expectations already priced in.")
        cautions.append("High P/E leaves little room for earnings disappointment.")

    if roe > 18:
        insights.append(f"<b>ROE {roe:.1f}%</b> — high-quality capital allocation.")
    elif 0 < roe < 8:
        insights.append(f"<b>ROE {roe:.1f}%</b> — low return on equity. Watch margins.")

    ci, ca, cc = responsive_cols(3)
    with ci:
        st.markdown('<p class="section-title">🔍 What the data says</p>',
                    unsafe_allow_html=True)
        for ins in insights:
            st.markdown(f'<div class="insight-box">{sanitise_bold(ins, 400)}</div>',
                        unsafe_allow_html=True)
    with ca:
        st.markdown('<p class="section-title">✅ What to consider</p>',
                    unsafe_allow_html=True)
        for a in (actions or ["No strong action signal right now. Monitor and wait."]):
            st.markdown(f'<div class="action-box">{sanitise_bold(a, 400)}</div>',
                        unsafe_allow_html=True)
    with cc:
        st.markdown('<p class="section-title">⚠️ Watch out for</p>',
                    unsafe_allow_html=True)
        for c in (cautions or ["No major red flags at this time."]):
            st.markdown(f'<div class="warn-box">{sanitise_bold(c, 400)}</div>',
                        unsafe_allow_html=True)


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
            "\n\nThis is a temporary yfinance issue — click Retry below."
        )
        if st.button("🔄 Retry", key=f"retry_{ticker}", type="primary"):
            get_price_data.clear()
            st.rerun()
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

    # ── Detect asset class (drives KPI suppression) ─────────────
    asset_class = safe_run(
        lambda: _detect_asset_class(country, ticker, info),
        context="dashboard:asset_class", default="equity"
    )

    # ── Compute regime + verdict BEFORE header renders ────────────
    # All four computed here so header shows the real verdict,
    # not the raw momentum score. Passed to tabs to avoid recomputation.
    stage = safe_run(
        lambda: compute_weinstein_stage(df),
        context="dashboard:stage",
        default={"stage": 0, "label": "Insufficient data",
                 "description": "", "signal_veto": None,
                 "price_vs_ma_pct": 0.0, "ma_slope": 0.0, "ma30w": None}
    )
    elder = safe_run(
        lambda: compute_elder_screens(df),
        context="dashboard:elder",
        default={"weekly_bull": True, "weekly_tide_label": "Unknown",
                 "elder_verdict": "NEUTRAL", "elder_description": "",
                 "suppress_buy": False, "daily_rsi": 50.0,
                 "weekly_hist_now": 0.0, "weekly_hist_prev": 0.0}
    )
    fcast = safe_run(
        lambda: compute_forecast(df, horizon_days=63),
        context="dashboard:fcast",
        default={"p_gain": None, "p50": None, "horizon_days": 63,
                 "p10": None, "p25": None, "p75": None, "p90": None}
    )
    verdict = safe_run(
        lambda: compute_unified_verdict(sig, stage, elder, fcast, asset_class=asset_class),
        context="dashboard:verdict",
        default={"final_signal": sig.get("signal", "NO DATA"),
                 "final_color": sig.get("sigcolor", "#6b7280"),
                 "conflicts": [], "verdict_reason": "",
                 "horizon_note": "", "raw_score": sig.get("score", 0),
                 "stage_label": "", "elder_verdict": ""}
    )

    _render_header_static(ticker, name, country, cur_sym, info, sig, verdict)
    # Live price tile: self-refreshes every 5s when market open, static when closed
    live_price_tile = _make_live_price_fragment(ticker, cur_sym, df, market_open)
    live_price_tile()
    # KPI panel: self-refreshes every 60s when market open, static when closed
    live_kpi = _make_live_kpi_fragment(ticker, cur_sym, info, market_open, asset_class)
    live_kpi()
    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Technical Charts",
        "🔮 Forecast",
        "⚖️ Compare",
        "💡 Insights & Actions",
    ])
    with tab1: _tab_charts(df, cur_sym, ticker=ticker, market_open=market_open)
    with tab2: _tab_forecast(ticker, df, sig, cur_sym, info)
    with tab3: _tab_compare(ticker, name, df, compare_names, stock_map, cb)
    with tab4: _tab_insights(sig, cur_sym, ticker, df,
                              stage=stage, elder=elder,
                              fcast=fcast, verdict=verdict)