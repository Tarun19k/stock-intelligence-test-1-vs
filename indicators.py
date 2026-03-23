# indicators.py — Technical indicator computation + forecasting engine
# Depends on: pandas, numpy only. No Streamlit, no yfinance.
# v5.19: Added Weinstein Stage, Elder Triple Screen, Historical Simulation
#        forecast engine, and unified verdict function.

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


# ═══════════════════════════════════════════════════════════════════
# WEINSTEIN STAGE ANALYSIS
# Stan Weinstein — "Secrets for Profiting in Bull and Bear Markets"
# Classifies a stock into its current market cycle stage using the
# 30-week (150-day) moving average and its slope.
# ═══════════════════════════════════════════════════════════════════

def compute_weinstein_stage(df: pd.DataFrame) -> dict:
    """
    Classify stock into Weinstein Stage 1–4.

    Stage 1 — Base/Accumulation: price near flat 30w MA, MA flat/turning up
    Stage 2 — Advancing:         price ABOVE RISING 30w MA  → BUY valid
    Stage 3 — Top/Distribution:  price above flat/falling MA → CAUTION
    Stage 4 — Declining:         price BELOW FALLING 30w MA → AVOID (hard veto)

    Returns dict with: stage (int), label (str), description (str),
    price_vs_ma_pct (float), ma_slope (float), signal_veto (str|None)
    """
    if df is None or df.empty or len(df) < 150:
        return {
            "stage": 0, "label": "Insufficient data",
            "description": "Need 150+ days of history for Stage analysis.",
            "price_vs_ma_pct": 0.0, "ma_slope": 0.0,
            "signal_veto": None, "ma30w": None,
        }

    close = df["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = close.dropna()

    # 30-week MA = 150 trading days
    ma30w   = close.rolling(150).mean()
    ma_now  = safe_float(ma30w.iloc[-1])
    price   = safe_float(close.iloc[-1])

    # MA slope: change over last 10 trading days as % of MA
    ma_10ago = safe_float(ma30w.iloc[-11]) if len(ma30w) >= 11 else ma_now
    ma_slope = (ma_now - ma_10ago) / ma_10ago * 100 if ma_10ago else 0.0

    price_vs_ma = (price - ma_now) / ma_now * 100 if ma_now else 0.0

    # Classify
    above_ma   = price > ma_now
    rising_ma  = ma_slope > 0.05   # small threshold to avoid noise
    flat_ma    = abs(ma_slope) <= 0.05
    near_ma    = abs(price_vs_ma) <= 3.0  # within 3% = "near"

    if above_ma and rising_ma:
        stage = 2
        label = "Stage 2 — Advancing"
        desc  = (f"Price is {price_vs_ma:+.1f}% above its rising 30-week average. "
                 f"Classic uptrend. BUY signals are valid.")
        veto  = None

    elif above_ma and (flat_ma or not rising_ma):
        stage = 3
        label = "Stage 3 — Top / Distribution"
        desc  = (f"Price is above its 30-week average but the average is no longer rising "
                 f"(slope {ma_slope:+.2f}%). Distribution phase — insiders often selling here.")
        veto  = "WATCH"  # cap signal at WATCH

    elif not above_ma and (not rising_ma):
        stage = 4
        label = "Stage 4 — Declining"
        desc  = (f"Price is {abs(price_vs_ma):.1f}% below its falling 30-week average. "
                 f"Confirmed downtrend. No BUY signal is reliable until this reverses.")
        veto  = "AVOID"  # hard override — ignore all BUY signals

    else:
        # below MA but MA is rising — base forming
        stage = 1
        label = "Stage 1 — Base / Accumulation"
        desc  = (f"Price is near or below a flat/turning 30-week average. "
                 f"Potential accumulation zone. Wait for Stage 2 breakout before buying.")
        veto  = "WATCH"  # no confirmed BUY yet

    return {
        "stage":           stage,
        "label":           label,
        "description":     desc,
        "price_vs_ma_pct": round(price_vs_ma, 2),
        "ma_slope":        round(ma_slope, 4),
        "signal_veto":     veto,
        "ma30w":           round(ma_now, 2),
    }


# ═══════════════════════════════════════════════════════════════════
# ELDER TRIPLE SCREEN — FIRST SCREEN (weekly tide)
# Alexander Elder — "Trading for a Living" (1993)
# Weekly MACD histogram direction = the tide.
# A RISING weekly histogram = bullish tide even if value is negative.
# Daily BUY signals are only valid when the weekly tide is bullish.
# ═══════════════════════════════════════════════════════════════════

def compute_elder_screens(df: pd.DataFrame) -> dict:
    """
    Compute Elder's First and Second screens from daily price data.

    First Screen  — Weekly MACD histogram direction (tide)
    Second Screen — Daily RSI position (wave)

    Returns dict with: weekly_bull (bool), weekly_hist_now, weekly_hist_prev,
    weekly_tide_label (str), daily_rsi (float), elder_verdict (str),
    elder_description (str), suppress_buy (bool)
    """
    if df is None or df.empty or len(df) < 60:
        return {
            "weekly_bull": True, "weekly_hist_now": 0.0,
            "weekly_hist_prev": 0.0, "weekly_tide_label": "Insufficient data",
            "daily_rsi": 50.0, "elder_verdict": "NEUTRAL",
            "elder_description": "Need 60+ days for Elder screening.",
            "suppress_buy": False,
        }

    close = df["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = close.dropna()

    # ── First Screen: weekly MACD ─────────────────────────────────
    # Resample to weekly (last close of each week)
    idx    = pd.date_range(end=pd.Timestamp.today(), periods=len(close), freq="B")
    cs     = pd.Series(close.values, index=idx)
    weekly = cs.resample("W").last().dropna()

    if len(weekly) < 30:
        weekly_bull = True
        hist_now = hist_prev = 0.0
    else:
        ema13 = weekly.ewm(span=13, adjust=False).mean()
        ema26 = weekly.ewm(span=26, adjust=False).mean()
        macd_line = ema13 - ema26
        signal    = macd_line.ewm(span=9, adjust=False).mean()
        hist      = macd_line - signal
        hist_now  = safe_float(hist.iloc[-1])
        hist_prev = safe_float(hist.iloc[-2]) if len(hist) >= 2 else hist_now
        weekly_bull = hist_now > hist_prev  # rising histogram = bullish tide

    tide_label = "🌊 Bullish Tide" if weekly_bull else "🌊 Bearish Tide"

    # ── Second Screen: daily RSI ──────────────────────────────────
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    rsi   = safe_float((100 - 100 / (1 + rs)).iloc[-1])

    # ── Combined verdict ──────────────────────────────────────────
    suppress_buy = False

    if weekly_bull and rsi < 40:
        verdict = "BUY SETUP"
        desc    = (f"Weekly tide is bullish (histogram rising) and daily RSI ({rsi:.0f}) "
                   f"has pulled back. Elder's ideal long entry: tide bullish, wave oversold.")
    elif weekly_bull and rsi >= 40:
        verdict = "HOLD / MONITOR"
        desc    = (f"Weekly tide is bullish. Daily RSI ({rsi:.0f}) is not yet oversold — "
                   f"wait for a pullback entry below RSI 40 for lower risk entry.")
    elif not weekly_bull and rsi > 65:
        verdict = "SELL / AVOID"
        desc    = (f"Weekly tide is bearish (histogram falling) and daily RSI ({rsi:.0f}) "
                   f"is extended on a bounce. Elder: sell strength in a bearish tide.")
        suppress_buy = True
    else:
        verdict = "AVOID LONGS"
        desc    = (f"Weekly tide is bearish. Daily RSI ({rsi:.0f}). "
                   f"No long entry until weekly tide turns bullish.")
        suppress_buy = True

    return {
        "weekly_bull":       weekly_bull,
        "weekly_hist_now":   round(hist_now, 4),
        "weekly_hist_prev":  round(hist_prev, 4),
        "weekly_tide_label": tide_label,
        "daily_rsi":         round(rsi, 1),
        "elder_verdict":     verdict,
        "elder_description": desc,
        "suppress_buy":      suppress_buy,
    }


# ═══════════════════════════════════════════════════════════════════
# HISTORICAL SIMULATION FORECAST ENGINE
# Method: Bootstrap historical log-returns (preserves fat tails).
# Regime-conditioned drift: momentum signal decays toward 0 at 63d.
# NO assumption of normal distribution.
# Max horizon: 63 days (3M). Beyond that: statistically unreliable.
# ═══════════════════════════════════════════════════════════════════

def compute_forecast(df: pd.DataFrame,
                     horizon_days: int = 63,
                     n_simulations: int = 2000) -> dict:
    """
    Historical Simulation forecast via bootstrapped log-returns.

    Returns dict with:
      p10, p25, p50, p75, p90  — price percentiles at horizon
      p_gain                   — probability price is higher than today (0–100)
      current_price            — today's close
      horizon_days             — as passed
      method                   — "historical_simulation_v1"
      holt_estimate            — Holt-Winters damped trend estimate (secondary)
      annualised_vol_pct       — annualised volatility of the lookback
      warning                  — None or string if data quality is low
    """
    # Clamp horizon — beyond 63 days the distribution is too wide to be useful
    horizon_days = min(horizon_days, 63)

    empty = {
        "p10": None, "p25": None, "p50": None, "p75": None, "p90": None,
        "p_gain": None, "current_price": None, "horizon_days": horizon_days,
        "method": "historical_simulation_v1", "holt_estimate": None,
        "annualised_vol_pct": None, "warning": "Insufficient data",
    }

    if df is None or df.empty:
        return empty

    close = df["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = close.dropna().astype(float)

    if len(close) < 30:
        return {**empty, "warning": "Need 30+ days of price history."}

    current = float(close.iloc[-1])
    log_ret = np.diff(np.log(close.values))

    # Annualised vol for display
    ann_vol = float(log_ret.std() * np.sqrt(252) * 100)

    # Regime-conditioned, horizon-blended drift
    # Recent 30-day momentum — decays toward 0 at 63d horizon
    recent_window = min(30, len(log_ret))
    momentum_mu   = log_ret[-recent_window:].mean()
    # Blend: 21d → 80% momentum, 63d → 0% momentum (pure bootstrap)
    blend         = max(0.0, 1.0 - horizon_days / 63.0)

    # Bootstrap simulation — draw from actual return distribution
    rng    = np.random.default_rng(seed=42)  # reproducible per-ticker
    draws  = rng.choice(log_ret, size=(n_simulations, horizon_days), replace=True)
    # Apply blended drift adjustment
    draws  = draws + blend * momentum_mu
    finals = current * np.exp(draws.sum(axis=1))

    p_gain = float((finals > current).mean() * 100)

    # Holt-Winters damped trend (secondary single-number estimate)
    hw = _holt_winters_damped(close.values, horizon_days)

    warning = None
    if len(close) < 60:
        warning = "Limited history (<60 days) — forecast range is wide."
    elif ann_vol > 60:
        warning = f"High volatility ({ann_vol:.0f}%/yr) — confidence intervals are wide."

    return {
        "p10":               round(float(np.percentile(finals, 10)), 2),
        "p25":               round(float(np.percentile(finals, 25)), 2),
        "p50":               round(float(np.percentile(finals, 50)), 2),
        "p75":               round(float(np.percentile(finals, 75)), 2),
        "p90":               round(float(np.percentile(finals, 90)), 2),
        "p_gain":            round(p_gain, 1),
        "current_price":     round(current, 2),
        "horizon_days":      horizon_days,
        "method":            "historical_simulation_v1",
        "holt_estimate":     round(float(hw), 2) if hw is not None else None,
        "annualised_vol_pct": round(ann_vol, 1),
        "warning":           warning,
    }


def _holt_winters_damped(prices: np.ndarray, horizon: int,
                          alpha: float = 0.3,
                          beta:  float = 0.1,
                          phi:   float = 0.88) -> float:
    """
    Double exponential smoothing with damped trend.
    phi < 1 prevents runaway extrapolation — trend decays toward flat.
    Returns the forecast at step `horizon`.
    """
    if len(prices) < 2:
        return float(prices[-1]) if len(prices) else 0.0

    l = float(prices[0])
    b = float(prices[1]) - float(prices[0])

    for t in range(1, len(prices)):
        l_prev, b_prev = l, b
        l = alpha * float(prices[t]) + (1 - alpha) * (l_prev + phi * b_prev)
        b = beta * (l - l_prev) + (1 - beta) * phi * b_prev

    damp_sum = sum(phi**i for i in range(1, horizon + 1))
    return l + damp_sum * b


# ═══════════════════════════════════════════════════════════════════
# UNIFIED VERDICT
# Combines: Weinstein Stage → Elder First Screen → momentum score
# Produces a single actionable verdict with conflict detection.
# This is the master function that replaces the disconnected
# signal / forecast / insights outputs.
# ═══════════════════════════════════════════════════════════════════

def compute_unified_verdict(sig: dict, stage: dict, elder: dict,
                             forecast: dict,
                             asset_class: str = "equity") -> dict:
    """
    Apply Stage veto → Elder veto → score → produce final verdict.
    For debt/rates instruments, the momentum pipeline is suppressed entirely
    — yield direction ≠ price direction for the investor holding the bond.

    Returns dict with:
      final_signal  — STRONG BUY / BUY / WATCH / AVOID / RATES CONTEXT
      final_color   — hex color string
      conflicts     — list of conflict description strings (may be empty)
      verdict_reason — plain-English explanation of why this verdict
      horizon_note  — what horizon this is meaningful for
      raw_score     — the original momentum score (for display)
      stage_label   — Weinstein stage label
      elder_verdict — Elder screen verdict
      is_debt       — True if asset_class == "debt"
    """
    raw_score    = sig.get("score", 0)
    raw_signal   = sig.get("signal", "NO DATA")
    stage_num    = stage.get("stage", 0)
    stage_veto   = stage.get("signal_veto")
    elder_supp   = elder.get("suppress_buy", False)
    p_gain       = forecast.get("p_gain")
    conflicts    = []

    # ── Debt / Rates — suppress momentum pipeline entirely ───────
    # MACD bullish on a yield instrument means yields are RISING,
    # which means bond prices are FALLING. Standard BUY signals
    # are inverted for debt holders. Do not show a momentum verdict.
    if asset_class == "debt":
        rsi = sig.get("rsi", 50)
        # Yield direction context from RSI (price of the instrument)
        if rsi > 60:
            yield_ctx = "Yield instrument is elevated — bond prices under pressure."
            color = "#ff9800"
        elif rsi < 40:
            yield_ctx = "Yield instrument is depressed — bond prices may be recovering."
            color = "#4f8ef7"
        else:
            yield_ctx = "Yield level is in a neutral range."
            color = "#6b7280"
        return {
            "final_signal":   "RATES CONTEXT",
            "final_color":    color,
            "conflicts":      [],
            "verdict_reason": (
                f"{yield_ctx} "
                f"Note: standard BUY/SELL signals are not shown for debt instruments — "
                f"rising yields mean falling bond prices. "
                f"See the Yield Context panel below for relevant signals."
            ),
            "horizon_note":   "Yield instruments require macro context, not momentum signals.",
            "raw_score":      raw_score,
            "stage_label":    "N/A for debt instruments",
            "elder_verdict":  "N/A for debt instruments",
            "is_debt":        True,
        }


    if stage_veto == "AVOID":
        final_signal = "AVOID"
        final_color  = "#ff1744"
        if "BUY" in raw_signal:
            conflicts.append(
                f"Signal conflict: Daily momentum score ({raw_score}/100) suggests "
                f"{raw_signal}, but this stock is in {stage['label']}. "
                f"A bullish technical signal inside a confirmed downtrend is typically "
                f"a short-term relief rally — not a durable buying opportunity. "
                f"Wait for price to reclaim the 30-week average and Stage to shift to 1 or 2."
            )
        reason = (f"{stage['label']} detected. Price is {abs(stage['price_vs_ma_pct']):.1f}% "
                  f"below its falling 30-week average. No buy signal is actionable until "
                  f"the trend reverses.")
        horizon_note = "No horizon applicable — avoid new positions."

    elif stage_veto == "WATCH":
        # Cap at WATCH — no BUY
        if raw_score >= 58:
            final_signal = "WATCH"
            final_color  = "#ff9800"
            conflicts.append(
                f"Score is {raw_score}/100 ({raw_signal}) but Weinstein {stage['label']} "
                f"prevents a BUY verdict. The trend cycle does not support a confirmed buy yet."
            )
        else:
            final_signal = raw_signal
            final_color  = sig.get("sigcolor", "#ff9800")
        reason = f"{stage['label']}. {stage['description']}"
        horizon_note = "Monitor only. Wait for Stage 2 breakout."

    else:
        # Stage 2 — score is valid, but still check Elder
        if elder_supp and "BUY" in raw_signal:
            # Elder weekly tide is bearish — cap at WATCH
            final_signal = "WATCH"
            final_color  = "#ff9800"
            conflicts.append(
                f"Score {raw_score}/100 suggests {raw_signal} on daily charts, "
                f"but the weekly trend (Elder First Screen) is bearish. "
                f"Buying against a bearish weekly tide is low-probability. "
                f"Wait for the weekly MACD histogram to start rising."
            )
            reason = f"Stage 2 confirmed but weekly tide is bearish — reduced conviction."
        else:
            # Full score → signal
            if raw_score >= 72:   final_signal, final_color = "STRONG BUY", "#00c853"
            elif raw_score >= 58: final_signal, final_color = "BUY",        "#4f8ef7"
            elif raw_score >= 40: final_signal, final_color = "WATCH",      "#ff9800"
            else:                 final_signal, final_color = "CAUTION",    "#ff1744"

            # Rationale explains verdict in terms the user can act on
            tide_str = "bullish" if not elder_supp else "turning bullish"
            if raw_score >= 58:
                score_ctx = f"Momentum is strong ({raw_score}/100) — trend and technicals agree."
            elif raw_score >= 40:
                score_ctx = f"Momentum is moderate ({raw_score}/100) — watch for strengthening before adding."
            else:
                score_ctx = (f"Momentum is weak ({raw_score}/100) — the trend cycle is healthy "
                             f"but short-term technical signals are not yet supportive. "
                             f"Wait for RSI and MACD to improve before entering.")
            reason = f"Stage 2 uptrend confirmed. Weekly tide {tide_str}. {score_ctx}"
        horizon_note = sig.get("hreason", "")

    # ── Step 2: Forecast–signal conflict check ─────────────────────
    if p_gain is not None:
        if p_gain < 40 and "BUY" in final_signal:
            conflicts.append(
                f"Forecast caution: Historical simulation gives only {p_gain:.0f}% probability "
                f"of being higher in {forecast.get('horizon_days', 63)} days. "
                f"The bullish signal reflects short-term momentum; the distribution of "
                f"outcomes leans slightly negative at this horizon."
            )
        elif p_gain > 65 and final_signal in ("AVOID", "CAUTION"):
            conflicts.append(
                f"Note: Despite the cautious signal, the forecast simulation shows "
                f"{p_gain:.0f}% probability of gain over {forecast.get('horizon_days', 63)} days "
                f"based on historical return patterns. This may reflect mean-reversion potential."
            )

    return {
        "final_signal":   final_signal,
        "final_color":    final_color,
        "conflicts":      conflicts,
        "verdict_reason": reason,
        "horizon_note":   horizon_note,
        "raw_score":      raw_score,
        "stage_label":    stage.get("label", ""),
        "elder_verdict":  elder.get("elder_verdict", ""),
        "is_debt":        False,
    }
