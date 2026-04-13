---
name: forecasting-calibration-math
description: Mathematical reference for forecast methodology and calibration in the GSI Dashboard. Covers Holt-Winters damped trend (α/β/φ interpretation), bootstrap P(gain) methodology, calibration standards (Brier score), neutral zone rationale, and seed=42 determinism tradeoff. Used by signal-accuracy-audit Domain 4 agents.
---

# Forecasting & Calibration Mathematics — Reference

**Use when:** Running Domain 4 (Forecast Calibration) of the quant audit,
or reviewing `indicators.py` `compute_forecast()` / `_holt_winters_damped()`.

**Note:** `compute_forecast()` and `_holt_winters_damped()` live in `indicators.py`
(lines 404 and 488), NOT `forecast.py`. `forecast.py` handles storage/display only.

---

## 1. Forecast Methodology — Historical Simulation

GSI uses **historical simulation with bootstrapped log-returns** as the primary model:

```
1. Compute log returns: r[t] = ln(P[t]/P[t-1])
2. Bootstrap draws:     Draw horizon_days returns with replacement (seed=42)
3. Apply drift blend:   draws += blend * momentum_mu  (blend decays to 0 at 63d)
4. Simulate finals:     P_final = P_current * exp(sum(draws))
5. Compute percentiles: p10, p25, p50, p75, p90
6. Compute P(gain):     fraction of simulations where P_final > P_current
```

**Why not ARIMA or ML?**
- Historical simulation is interpretable to retail users
- No parameter fitting (avoids overfitting on short Indian market history)
- Preserves fat tails naturally (bootstrap samples real extreme events)

---

## 2. Holt-Winters Damped Trend

`_holt_winters_damped()` is a secondary "point estimate" model used alongside
the bootstrap distribution. It provides a single price target.

**Double exponential smoothing with damped trend:**
```
Level:  L[t] = α × P[t] + (1-α) × (L[t-1] + φ × B[t-1])
Trend:  B[t] = β × (L[t] - L[t-1]) + (1-β) × φ × B[t-1]

Forecast at horizon h:
  F(h) = L[T] + B[T] × Σᵢ₌₁ʰ φⁱ
        = L[T] + B[T] × φ(1 - φʰ)/(1 - φ)
```

**GSI parameters (`indicators.py:488-509`):**
```python
alpha=0.3, beta=0.1, phi=0.88
```

### Parameter interpretation guide

| Parameter | Symbol | GSI value | Valid range | Interpretation |
|---|---|---|---|---|
| Level smoothing | α | 0.3 | (0, 1) | How fast L tracks actual price. 0.3 = moderate lag — not overreactive |
| Trend smoothing | β | 0.1 | (0, 1) | How fast trend estimate updates. 0.1 = slow trend — prevents whipsaw |
| Damping factor | φ | 0.88 | (0, 1) | How fast trend decays to flat. 0.88 = moderate dampening |

### Red flag thresholds (from skill `quant-reviewer`)
| Condition | Risk | Action |
|---|---|---|
| α > 0.5 | Overfit to recent data — forecast is just "recent price + trend" | Flag P2 |
| φ < 0.8 | Aggressive damping — trend decays too fast, estimate converges to L[T] too quickly | Flag P2 |
| β > 0.3 | Trend overreacts to single large moves | Flag P2 |
| φ = 1.0 | Undamped — extrapolates trend linearly, can produce runaway estimates | Flag P1 |

**GSI assessment:** α=0.3 (OK), β=0.1 (OK), φ=0.88 (OK — mild damping, reasonable).

### Initialisation
```python
L[0] = prices[0]
B[0] = prices[1] - prices[0]
```
GSI initialises level to first price, trend to first difference. Standard approach.
Alternative (more stable): use SMA(n) for L[0], average first differences for B[0].

---

## 3. P(gain) Calculation

```
P(gain) = (count of simulations where P_final > P_current) / n_simulations × 100
```

**GSI implementation:**
```python
rng    = np.random.default_rng(seed=42)  # reproducible
draws  = rng.choice(log_ret, size=(n_simulations, horizon_days), replace=True)
draws += blend * momentum_mu
finals = current * np.exp(draws.sum(axis=1))
p_gain = float((finals > current).mean() * 100)
```

**Seed=42 determinism:** The same ticker+period always produces the same P(gain).
This is intentional (reproducibility, prevents "refresh to get a different signal").
Tradeoff: P(gain) doesn't update between price data refreshes.

---

## 4. Neutral Zone — 45–55%

**Rationale:** A coin flip is 50%. A model that says 51% should not be treated as
a directional signal — that's within noise of random. The neutral zone captures
the range where the model has insufficient directional evidence.

**GSI neutral zone:** 45–55% (OPEN-009, implemented in v5.32)
```python
if 45 <= p_gain <= 55:
    pass  # neutral — don't score direction
```

**Mathematical basis:** If the model has ±5pp uncertainty (reasonable for short-horizon
bootstrap), any P(gain) within ±5pp of 50% is indistinguishable from random.
The 45–55% band is therefore a ±5pp uncertainty buffer around 50%.

**Tightening guidance:**
- Institutional use: ±3pp (47–53%) may be appropriate with more data
- The band should never be wider than ±10pp — that would suppress too many signals

---

## 5. Forecast Calibration Standards

**Calibration** means: P(gain) buckets should approximate actual win rates.
A well-calibrated model where P(gain) = 65% should win approximately 65% of the time.

### Minimum data requirements
- Domain 4 calibration check requires ≥ 20 resolved forecasts
- "Resolved" = forecast horizon passed, actual outcome known
- GSI forecast history lives in `st.session_state["forecast_history"]` (no persistence, OPEN-003)
- Expected history on cold session start: 0 entries → Domain 4 always DEFERRED

### Bucket analysis (run when ≥ 20 entries available)

| P(gain) bucket | Expected win rate | Tolerance |
|---|---|---|
| < 35% | ~35% (bears win) | ±15pp |
| 35–45% | ~40% | ±15pp |
| 45–55% | ~50% (neutral) | ±15pp |
| 55–65% | ~60% | ±15pp |
| > 65% | ~65% | ±15pp |

**Pass criterion:** All buckets within ±15pp of expected (soft target — small sample expected).
**Tighten to ±10pp before institutional launch.**

### Brier Score (reference metric)

```
BS = (1/N) × Σ (p_i - o_i)²

where: p_i = predicted probability (P(gain)/100)
       o_i = actual outcome (1 if gain, 0 if loss)
```

Perfect calibration: BS = 0.
Random model: BS = 0.25 (p=0.5 always).
Climatological baseline: BS ≈ 0.21–0.24 for equity markets.

**GSI target:** BS < 0.22 (beat climatological baseline).

---

## 6. Regime-Conditioned Drift

GSI applies a blend between momentum-adjusted and pure-bootstrap forecasts:

```python
momentum_mu = log_ret[-30:].mean()              # recent 30-day mean daily return
blend       = max(0.0, 1.0 - horizon_days/63.0) # 1.0 at day 1, 0.0 at day 63
draws      += blend * momentum_mu               # adjust each simulated path
```

**Interpretation:**
- 21-day horizon: blend ≈ 0.67 → 67% momentum-adjusted, 33% pure bootstrap
- 63-day horizon: blend = 0.0 → pure bootstrap (no momentum)

**Rationale:** Short-term momentum is predictive over days; it dissipates over months.
This is consistent with academic evidence on momentum factor (Jegadeesh & Titman 1993).

**Pass criterion:** `blend` decreases monotonically from 1.0 to 0.0 as horizon increases.
At horizon=63: blend = 0 exactly (no drift applied). Verify via inspection.
