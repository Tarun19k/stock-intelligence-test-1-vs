---
name: portfolio-risk-math
description: Mathematical reference for portfolio risk calculations used in the GSI Dashboard. Covers CVaR/VaR theory, Rockafellar-Uryasev LP formulation, log returns assumptions, bootstrap scenario generation, stability score interpretation, and efficient frontier invariants. Used by signal-accuracy-audit Domain 5 agents.
---

# Portfolio Risk Mathematics — Reference

**Use when:** Running Domain 5 (Portfolio Math) of the quant audit, or verifying
`portfolio.py` implementations during code review.

---

## 1. Value at Risk (VaR) vs CVaR

### VaR — Value at Risk at confidence level α
```
VaR_α = -inf{r : P(R ≤ r) ≥ 1-α}
      = the (1-α)-quantile of the loss distribution
```
At α=0.95: VaR is the loss exceeded only 5% of the time.
**Problem:** VaR ignores the severity of losses beyond the threshold (tail-blind).

### CVaR — Conditional Value at Risk (Expected Shortfall)
```
CVaR_α = E[−R | R ≤ −VaR_α]
        = mean of the worst (1−α) fraction of returns
```
At α=0.95 (GSI's `CVAR_ALPHA`): CVaR = average of the bottom 5% of scenarios.
**CVaR is always ≥ VaR.** CVaR is convex and sub-additive — suitable for optimisation.

**Verification:** In a 1000-scenario simulation, CVaR_0.95 = mean of the 50 worst returns.

---

## 2. Rockafellar-Uryasev (2000) LP Reformulation

The naive CVaR optimisation requires sorting — not differentiable. Rockafellar-Uryasev
reformulate it as a linear programme:

**Primal problem:**
```
Minimise: −λ E[w'r] + CVaR_α(w'r)

Subject to:  sum(w) = 1
             0 ≤ w_i ≤ max_weight
             CVaR via auxiliary reformulation
```

**Auxiliary reformulation (makes it LP):**
```
CVaR = ζ + 1/(n(1-α)) × Σᵢ zᵢ

where:  zᵢ ≥ 0
        zᵢ ≥ −rᵢ'w − ζ    (loss exceedances above VaR threshold ζ)
```

`ζ` is the VaR auxiliary variable. `z_i` captures losses beyond VaR.

**GSI implementation (`portfolio.py:207-290`):**
```python
zeta = cp.Variable()                          # VaR auxiliary
z    = cp.Variable(n_scenarios, nonneg=True)  # CVaR exceedance variables
w    = cp.Variable(n_stocks, nonneg=True)     # portfolio weights

portfolio_returns = scenarios @ w             # (n_scenarios,) vector
loss_exceedances  = -portfolio_returns - zeta

constraints = [
    cp.sum(w) == 1,
    w <= max_weight,
    z >= loss_exceedances,
    # ... min_stocks constraints
]

cvar = zeta + cp.sum(z) / (n_scenarios * (1 - CVAR_ALPHA))
objective = cp.Minimize(-risk_aversion * cp.sum(portfolio_returns) / n_scenarios + cvar)
```

**Pass criterion:** CVaR returned by solver should satisfy CVaR ≥ VaR (5th percentile
of scenario returns). If CVaR < VaR: solver error or incorrect alpha.

---

## 3. Log Returns

**Formula:**
```
r[t] = ln(P[t] / P[t-1]) = ln(P[t]) − ln(P[t-1])
```

**GSI implementation:** `np.diff(np.log(close.values))`

**Why log returns (vs simple returns):**
- Time-additive: r[0→T] = Σ r[t]
- Approximately normal for small changes
- Bounded below at −∞ (prevents negative prices in simulation)

**IID assumption:** Bootstrap sampling assumes returns are independent and identically
distributed. Violations:
- Volatility clustering (GARCH effects) — returns are NOT IID in practice
- GSI mitigation: exponential weighting in bootstrap (recent returns weighted more)
- Acceptable for a retail dashboard; institutional use would require GARCH

**Minimum sample size for stability:**
- < 30 bars: unreliable (GSI guard at 30 bars minimum)
- 30–60 bars: "Limited history" warning triggered
- 60–252 bars: normal operation
- > 252 bars: preferred (1 trading year)

---

## 4. Bootstrap Scenario Generation

**Standard (equal-weight):**
```python
indices   = np.random.choice(T, size=(n_simulations, horizon), replace=True)
scenarios = returns[indices]
```

**GSI (exponential-weight, recent emphasis):**
```python
EXP_DECAY = 0.94  # GSI constant (verify in portfolio.py)
weights = [EXP_DECAY**(T-1-t) for t in range(T)]  # row T-1 (today) has weight 1.0
weights /= sum(weights)
indices   = np.random.choice(T, size=n, replace=True, p=weights)
scenarios = returns[indices, :]
```

**Rationale:** Recent 30 days dominate — better reflects current market regime than
equal-weight averaging that blurs regime changes.

**Pass criterion:** Scenarios matrix is (N × stocks) shaped. Row sums vary (not all
equal). No all-zero rows. Exponential weights sum to 1.0.

---

## 5. Stability Score — σ Threshold Interpretation

### What max_std means

`compute_stability_score()` runs 10 perturbation trials (±5% random noise on returns),
re-optimises each time, and measures the standard deviation of each stock's weight
across the 10 trials.

`max_std` = maximum weight σ across all stocks, expressed as a percentage.

**Example:** If RELIANCE.NS weight varies between 8% and 22% across 10 runs,
that's a σ of ~(22-8)/4 ≈ 3.5% per-run std ≈ `max_std` of ~4% → STABLE.

### Thresholds (verified from `portfolio.py:370-375`, 2026-04-13)

| max_std | Score | Interpretation |
|---|---|---|
| < 8% | STABLE | Small perturbations change allocations by <8pp — reliable |
| 8% ≤ x < 15% | MODERATE | Allocations somewhat sensitive — use with caution |
| ≥ 15% | UNSTABLE | Allocations flip significantly — treat as illustrative only |

**OPEN-025 note (pre-tracked P1):** Docstring says `> 15%` UNSTABLE but code
fires at `>= 15%` (edge case at exactly 15%). Off-by-one at boundary. Do NOT
re-raise from audit — already tracked in CLAUDE.md.

### Why these thresholds matter

A portfolio showing 30% RELIANCE, 20% INFY on one optimisation but 5% RELIANCE,
45% INFY on a slightly perturbed run is not reliable advice. The UNSTABLE label
prevents a retail user from acting on a fragile recommendation.

---

## 6. Efficient Frontier Invariants

**Definition:** The efficient frontier is the set of portfolios that maximise
expected return for a given level of risk (CVaR).

**Invariant 1 — Monotonicity:** As risk increases (CVaR increases), expected return
must be non-decreasing along the frontier.

**Invariant 2 — Minimum-variance portfolio:** The leftmost point of the frontier
is the minimum-CVaR portfolio. It corresponds to the highest `risk_aversion` lambda.

**GSI verification:**
```python
frontier = compute_efficient_frontier(scenarios, names, n_points=12)
# frontier is list of {lambda, weights, exp_ret, cvar, sharpe}
# Sort by cvar ascending — exp_ret should be non-decreasing
cvar_values   = [p["cvar"] for p in frontier]
expret_values = [p["exp_ret"] for p in frontier]
assert all(expret_values[i] <= expret_values[i+1] or
           abs(expret_values[i] - expret_values[i+1]) < 1e-6
           for i in range(len(expret_values)-1))
```

**Pass criterion:** At least 10 of 12 frontier points are Pareto-optimal (non-dominated).
A flat or backward-bending section indicates solver instability — classify P1.

---

## 7. Key Constants in portfolio.py (verify these match)

| Constant | Expected value | Purpose |
|---|---|---|
| `CVAR_ALPHA` | 0.95 | 95th percentile CVaR — worst 5% |
| `N_SCENARIOS` | ~1000 | Bootstrap simulation count |
| `MAX_WEIGHT` | ~0.40 | Maximum single-stock weight |
| `MIN_STOCKS` | 2–3 | Minimum number of stocks held |
| `EXP_DECAY` | ~0.94 | Exponential weighting decay |
| `MIN_WEIGHT_FLOOR` | 0.05 | Min weight if stock included |
