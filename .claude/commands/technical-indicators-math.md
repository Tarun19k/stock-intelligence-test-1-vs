---
name: technical-indicators-math
description: Canonical mathematical reference for all technical indicators used in the GSI Dashboard. Defines correct formulas, smoothing method taxonomy (SMA vs EWM vs Wilder's RMA), platform comparison table, and acceptable divergence tolerances. Used by signal-accuracy-audit Domain 1 agents.
---

# Technical Indicators — Mathematical Reference

**Use when:** Running Domain 1 (Indicator Math Validation) of the quant audit,
or verifying indicator implementations during code review.

---

## Smoothing Method Taxonomy

Three distinct smoothing methods are used across technical indicators. Confusion between
them is the most common source of indicator implementation divergence.

### SMA — Simple Moving Average
```
SMA(n, t) = (P[t] + P[t-1] + ... + P[t-n+1]) / n
```
Properties: Equal weights, always lags by n/2 periods. Recomputes entirely each bar.
pandas: `series.rolling(n).mean()`

### EMA — Exponential Moving Average (standard)
```
α = 2 / (n + 1)
EMA(t) = α × P[t] + (1 - α) × EMA(t-1)
```
Properties: Recency-weighted, infinite memory, faster than SMA. α=2/(n+1) is standard.
pandas: `series.ewm(span=n, adjust=False).mean()`

### RMA — Wilder's Moving Average (Relative Moving Average)
```
α = 1 / n
RMA(t) = α × P[t] + (1 - α) × RMA(t-1)
       = (prev_avg × (n-1) + P[t]) / n
```
Properties: Slower than EMA, heavier smoothing. Wilder used this for RSI and ATR.
pandas equivalent: `series.ewm(com=n-1, adjust=False).mean()` — note: `com=n-1` not `span=n`
**Key distinction:** EMA with span=14 ≠ RMA with period=14. α_EMA = 2/15 ≈ 0.133; α_RMA = 1/14 ≈ 0.071.

### Cutler's RSI vs Wilder's RSI
| Method | Smoothing | Formula | Platform |
|---|---|---|---|
| Wilder's (original 1978) | RMA, com=13 | avg_gain = (prev×13 + gain)/14 | TradingView, Bloomberg, Zerodha Kite, NSE chart |
| Cutler's (1994) | SMA | avg_gain = rolling(14).mean() of gains | Some backtesting libraries |
| EWM (common mistake) | EWM, span=14 | ewm(span=14).mean() | — |

**GSI uses Cutler's (SMA).** Values converge with Wilder's for lookbacks > 100 bars.
Divergence at short windows: 3–8 RSI points. Not a P0 — classify as P1.

---

## Canonical Formulas

### RSI — Relative Strength Index (14-period)

**Wilder's method (reference standard):**
```
delta[t] = Close[t] - Close[t-1]
gain[t]  = max(delta[t], 0)
loss[t]  = max(-delta[t], 0)

# First value: SMA seed
avg_gain[0] = mean(gain[0:14])
avg_loss[0] = mean(loss[0:14])

# Subsequent values: Wilder's RMA
avg_gain[t] = (avg_gain[t-1] × 13 + gain[t]) / 14
avg_loss[t] = (avg_loss[t-1] × 13 + loss[t]) / 14

RS[t]  = avg_gain[t] / avg_loss[t]
RSI[t] = 100 - 100 / (1 + RS[t])
```

**GSI implementation (Cutler's SMA):**
```python
delta = c.diff()
gain  = delta.clip(lower=0).rolling(14).mean()   # SMA not RMA
loss  = (-delta.clip(upper=0)).rolling(14).mean() # SMA not RMA
rs    = gain / loss.replace(0, np.nan)
RSI   = 100 - 100 / (1 + rs)
```

Overbought: >70. Oversold: <30.

---

### EMA — 20, 50, 200 period

```python
ema = close.ewm(span=N, adjust=False).mean()  # α = 2/(N+1)
```
GSI implementation matches standard exactly. No divergence expected.

---

### MACD — Moving Average Convergence Divergence

Standard parameters (Gerald Appel 1979):
```
MACD line   = EMA(12) - EMA(26)
Signal line = EMA(9) of MACD line
Histogram   = MACD - Signal
```
```python
ema12 = c.ewm(span=12, adjust=False).mean()
ema26 = c.ewm(span=26, adjust=False).mean()
MACD  = ema12 - ema26
MACDS = MACD.ewm(span=9, adjust=False).mean()
MACDH = MACD - MACDS
```
GSI implementation matches standard exactly.

---

### Bollinger Bands — 20-period, ±2σ

```
Middle = SMA(20)
Upper  = SMA(20) + 2 × σ(20)
Lower  = SMA(20) - 2 × σ(20)
```

**ddof controversy:**
| Platform | ddof | std formula |
|---|---|---|
| TradingView | 0 | Population std: sqrt(Σ(x-μ)²/n) |
| pandas default | 1 | Sample std: sqrt(Σ(x-μ)²/(n-1)) |
| GSI | 1 (default) | `c.rolling(20).std()` — pandas default |

Divergence at n=20: |ddof=1 - ddof=0| / ddof=0 ≈ 1/(2×20) = 2.6%. Classify as P2.

```python
bb_mid = c.rolling(20).mean()
bb_std = c.rolling(20).std()     # ddof=1 (sample)
BBU    = bb_mid + 2 * bb_std
BBL    = bb_mid - 2 * bb_std
BBW    = (BBU - BBL) / bb_mid * 100   # bandwidth %
```

---

### ATR — Average True Range (14-period)

**True Range:**
```
TR[t] = max(High[t] - Low[t],
            |High[t] - Close[t-1]|,
            |Low[t]  - Close[t-1]|)
```

**Wilder's method (reference standard):** RMA(14) of TR
```
ATR[t] = (ATR[t-1] × 13 + TR[t]) / 14
```

**GSI implementation:** SMA(14) of TR
```python
tr  = pd.concat([h-lo, (h-c.shift()).abs(), (lo-c.shift()).abs()], axis=1).max(axis=1)
ATR = tr.rolling(14).mean()   # SMA, not Wilder's RMA
```
Same deviation as RSI. Classify as P1. ATR converges with Wilder's over long windows.

---

### ADX — Average Directional Index (14-period)

```
+DM[t] = High[t] - High[t-1]  if > 0 and > -(Low[t] - Low[t-1])  else 0
-DM[t] = Low[t-1] - Low[t]    if > 0 and > (High[t] - High[t-1]) else 0

+DI = 100 × SMA(+DM, 14) / ATR(14)
-DI = 100 × SMA(-DM, 14) / ATR(14)

DX  = 100 × |+DI - -DI| / (+DI + -DI)
ADX = SMA(DX, 14)
```

GSI implementation matches this formula. ADX > 25 = trending.

---

### Stochastic %K (14-period)

```
%K[t] = 100 × (Close[t] - Low(14)[t]) / (High(14)[t] - Low(14)[t])
```
GSI implementation matches standard. Oversold <20, Overbought >80.

---

### OBV — On-Balance Volume

```
OBV[t] = OBV[t-1] + Volume[t]  if Close[t] > Close[t-1]
        = OBV[t-1] - Volume[t]  if Close[t] < Close[t-1]
        = OBV[t-1]              if Close[t] = Close[t-1]
```
GSI implementation uses `np.sign(c.diff())` — mathematically equivalent.

---

## Platform Comparison — Which RSI Should Match?

For Indian retail users (Zerodha Kite, NSE chart): **Wilder's RSI is the reference.**
GSI uses Cutler's, which will diverge from what users see on Zerodha on recent bars.

| Platform | RSI method | ATR method |
|---|---|---|
| TradingView | Wilder's RMA | Wilder's RMA |
| Bloomberg Terminal | Wilder's RMA | Wilder's RMA |
| Zerodha Kite | Wilder's RMA | Wilder's RMA |
| NSE charts | Wilder's RMA | — |
| GSI Dashboard | Cutler's SMA | SMA |

**Implication:** GSI signals may differ from what Indian users see on their broker
platform by 3–8 RSI points on stocks with <60 bars of data (new listings, post-halt).
For established stocks with 200+ bars, difference is <0.5 points.

---

## Divergence Tolerance Table

| Indicator | Method difference | Short-window divergence | Long-window convergence | Severity |
|---|---|---|---|---|
| RSI | Cutler's vs Wilder's | 3–8 points (<60 bars) | <0.5 points (>100 bars) | P1 |
| ATR | SMA vs Wilder's | 5–15% on volatile stocks | <2% (>100 bars) | P1 |
| Bollinger | ddof=1 vs ddof=0 | 2.6% on band width | Same (scale-invariant) | P2 |
| EMA | N/A — exact match | — | — | — |
| MACD | N/A — exact match | — | — | — |
| ADX | N/A — close match | <1 point | — | P2 |
| Stochastic | N/A — exact match | — | — | — |
| OBV | N/A — exact match | — | — | — |
