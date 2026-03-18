# indicators.py — Technical indicator computation
# Depends on: pandas, numpy only. No Streamlit, no yfinance.

import numpy as np
import pandas as pd
from utils import safe_float


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add RSI, MACD, Bollinger, SMA, ATR, ADX, Stoch, OBV, VolumeMA to df."""
    if df.empty or len(df) < 20:
        return df
    # Guard: require OHLCV columns — return df as-is if any are missing
    required = ["Open", "High", "Low", "Close", "Volume"]
    missing  = [c for c in required if c not in df.columns]
    if missing:
        return df   # caller's safe_run will surface this gracefully

    df = df.copy()
    c = df["Close"]
    h = df["High"]
    lo = df["Low"]
    v = df["Volume"]

    # SMAs
    df["SMA20"]  = c.rolling(20).mean()
    df["SMA50"]  = c.rolling(50).mean()
    df["SMA200"] = c.rolling(200).mean()

    # RSI
    delta = c.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    df["RSI"] = 100 - 100 / (1 + rs)

    # MACD
    ema12 = c.ewm(span=12, adjust=False).mean()
    ema26 = c.ewm(span=26, adjust=False).mean()
    df["MACD"]  = ema12 - ema26
    df["MACDS"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACDH"] = df["MACD"] - df["MACDS"]

    # Bollinger Bands
    bb_mid = c.rolling(20).mean()
    bb_std = c.rolling(20).std()
    df["BBU"] = bb_mid + 2 * bb_std
    df["BBL"] = bb_mid - 2 * bb_std
    df["BBW"] = (df["BBU"] - df["BBL"]) / bb_mid * 100

    # ATR
    tr = pd.concat([
        h - lo,
        (h - c.shift()).abs(),
        (lo - c.shift()).abs(),
    ], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(14).mean()

    # ADX
    up   = h.diff()
    down = -lo.diff()
    pdm  = up.where((up > down) & (up > 0), 0.0)
    ndm  = down.where((down > up) & (down > 0), 0.0)
    atr14 = tr.rolling(14).mean()
    pdi  = 100 * pdm.rolling(14).mean() / atr14.replace(0, np.nan)
    ndi  = 100 * ndm.rolling(14).mean() / atr14.replace(0, np.nan)
    dx   = (100 * (pdi - ndi).abs() / (pdi + ndi).replace(0, np.nan))
    df["ADX"] = dx.rolling(14).mean()

    # Stochastic %K
    low14  = lo.rolling(14).min()
    high14 = h.rolling(14).max()
    df["Stoch"] = 100 * (c - low14) / (high14 - low14).replace(0, np.nan)

    # OBV
    direction = c.diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    df["OBV"] = (v * direction).cumsum()

    # Volume MA
    df["VolumeMA"] = v.rolling(20).mean()

    return df.dropna(subset=["SMA20"])


def signal_score(df: pd.DataFrame, info: dict) -> dict:
    """
    Compute composite signal score (0–100) from latest indicator row.
    Returns dict with score, signal, sigcolor, and component values.
    """
    if df.empty:
        return {"score": 0, "signal": "NO DATA", "sigcolor": "#6b7280",
                "rsi": 50, "macdh": 0, "bbw": 0, "atr": 0, "adx": 20,
                "stoch": 50, "obv": 0, "volm": 0, "sma50": 0, "sma200": 0,
                "pe": 0, "pb": 0, "roe": 0, "revg": 0, "signals": []}

    latest = df.iloc[-1]
    price  = safe_float(latest.get("Close", 0))

    rsi    = safe_float(latest.get("RSI",    50))
    macdh  = safe_float(latest.get("MACDH",   0))
    bbw    = safe_float(latest.get("BBW",     0))
    atr    = safe_float(latest.get("ATR",     0))
    adx    = safe_float(latest.get("ADX",    20))
    stoch  = safe_float(latest.get("Stoch",  50))
    obv    = safe_float(latest.get("OBV",     0)) / 1e6
    volm   = safe_float(latest.get("Volume",  0)) / 1e6
    sma50  = safe_float(latest.get("SMA50",  price))
    sma200 = safe_float(latest.get("SMA200", price))
    vol_ma = safe_float(latest.get("VolumeMA", volm * 1e6)) / 1e6
    vol_ratio = (volm / vol_ma) if vol_ma > 0 else 1.0
    bbu    = safe_float(latest.get("BBU", price * 1.05))
    bbl    = safe_float(latest.get("BBL", price * 0.95))
    bb_pct = (price - bbl) / (bbu - bbl) if (bbu - bbl) > 0 else 0.5
    macd   = safe_float(latest.get("MACD", 0))
    macds  = safe_float(latest.get("MACDS", 0))

    pe   = safe_float(info.get("trailingPE", 0))
    pb   = safe_float(info.get("priceToBook", 0))
    roe  = safe_float(info.get("returnOnEquity", 0)) * 100
    revg = safe_float(info.get("revenueGrowth", 0)) * 100

    score = 0
    signals = []

    # RSI (0–25)
    if rsi < 30:       score += 25; signals.append("Oversold — Reversal Signal")
    elif rsi < 45:     score += 20; signals.append("RSI Recovery Zone")
    elif rsi < 60:     score += 12; signals.append("RSI Neutral-Bullish")
    elif rsi < 70:     score += 8;  signals.append("RSI Approaching Overbought")
    else:              score += 2;  signals.append("RSI Overbought — Caution")

    # MACD (0–20)
    if macd > macds and macd > 0:  score += 20; signals.append("MACD Bullish Crossover")
    elif macd > macds:             score += 14; signals.append("MACD Recovering")
    else:                          score += 2

    # SMA Trend (0–20)
    if price > sma50 > sma200:     score += 20; signals.append("Above SMA50 & SMA200 — Uptrend")
    elif price > sma50:            score += 12; signals.append("Above SMA50")
    elif price > sma200:           score += 6;  signals.append("Above SMA200")
    elif sma50 > sma200:           score += 10; signals.append("Pullback in Uptrend — Value Entry")

    # Bollinger (0–15)
    if bb_pct < 0.15:              score += 15; signals.append("Price Near Lower BB — Buy Zone")
    elif bb_pct < 0.35:            score += 8;  signals.append("Lower BB Quarter")

    # Volume (0–10)
    if vol_ratio > 1.5:            score += 10; signals.append("Volume Surge — Accumulation")
    elif vol_ratio > 1.2:          score += 5;  signals.append("Above-Average Volume")

    # ADX (0–10)
    if adx > 25:                   score += 10; signals.append("Strong Trend — ADX Confirmed")

    score = min(score, 100)

    if score >= 72:   signal, sigcolor = "STRONG BUY", "#00c853"
    elif score >= 58: signal, sigcolor = "BUY",        "#4f8ef7"
    elif score >= 40: signal, sigcolor = "WATCH",      "#ff9800"
    else:             signal, sigcolor = "CAUTION",    "#ff1744"

    # Horizon
    macd_bull = macd > macds
    above_sma50 = price > sma50
    if score >= 65 and macd_bull and above_sma50 and 35 <= rsi <= 68:
        horizon = "3M"; hreason = "Strong near-term momentum with confirmed trend"
    elif score >= 50 and (macd_bull or above_sma50) and rsi > 30:
        horizon = "6M"; hreason = "Trend building — medium-term accumulation"
    else:
        horizon = "12M"; hreason = "Value recovery thesis — long-term conviction"

    return {
        "score": score, "signal": signal, "sigcolor": sigcolor,
        "horizon": horizon, "hreason": hreason,
        "rsi": rsi, "macdh": macdh, "macd": macd, "macds": macds,
        "bbw": bbw, "atr": atr, "adx": adx, "stoch": stoch,
        "obv": obv, "volm": volm, "sma50": sma50, "sma200": sma200,
        "bb_pct": bb_pct, "bbu": bbu, "bbl": bbl,
        "pe": pe, "pb": pb, "roe": roe, "revg": revg,
        "signals": signals,
    }
