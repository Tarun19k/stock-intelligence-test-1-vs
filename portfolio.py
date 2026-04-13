# portfolio.py — Mean-CVaR Portfolio Optimisation Engine
# Depends on: numpy, cvxpy (optional — graceful fallback if not installed)
# Called from: pages/week_summary.py → render_group_overview() Allocator tab
# NO Streamlit calls in this file — pure computation only.
#
# Algorithm: Rockafellar-Uryasev (2000) Mean-CVaR linear programme.
# Reference: https://github.com/NVIDIA-AI-Blueprints/quantitative-portfolio-optimization
# Same maths as NVIDIA blueprint; CPU/cvxpy replaces GPU/cuOpt at retail scale (<50 stocks).
#
# Pipeline (v5.23 — layers 1-4 of 12):
#   1. Raw historical log returns (90-day)
#   2. Winsorize at 99th percentile  (corporate action artifact fix — HIGH/D3)
#   3. Exponential weighting         (stationarity fix — HIGH/A1)
#   4. CVaR optimisation with regime-adjusted risk aversion
#   + Data quality validator         (HIGH/D1)
#   + Stress regime detection        (CRITICAL/P1, CRITICAL/M1)
#   + Layer 4 regime conflict check  (Weinstein/Elder cross-validation)

import numpy as np
from datetime import datetime, timedelta
from utils import log_error, safe_run

# ── Optional cvxpy import ─────────────────────────────────────────────────────
try:
    import cvxpy as cp
    CVXPY_AVAILABLE = True
except ImportError:
    CVXPY_AVAILABLE = False

# ── Constants ─────────────────────────────────────────────────────────────────
MIN_HISTORY_DAYS   = 63          # minimum trading days required per stock
WINSOR_PCTILE      = 99          # clip returns at this percentile
N_SCENARIOS        = 2000        # bootstrap scenario count (CPU-friendly at retail scale)
MAX_WEIGHT         = 0.35        # max 35% in any single stock
MIN_WEIGHT_FLOOR   = 0.05        # min 5% if stock is included (no tiny positions)
MIN_STOCKS         = 5           # minimum stocks in final allocation
ROUND_TRIP_COST    = 0.0025      # 0.25% estimated brokerage + STT round-trip (India)
VIX_STRESS_THRESH  = 25.0        # VIX above this → stress mode
CORR_CRISIS_THRESH = 0.85        # avg pairwise correlation above this → crisis regime
EXP_DECAY          = 0.97        # exponential decay per day (recent = higher weight)

# Risk aversion by profile — higher lambda = more risk-averse
RISK_AVERSION = {
    "conservative": 3.0,
    "balanced":     1.0,
    "aggressive":   0.3,
}

# CVaR confidence level
CVAR_ALPHA = 0.95   # tail = worst 5% of scenarios


# ── Data quality ──────────────────────────────────────────────────────────────

def check_data_quality(ticker: str, df) -> dict:
    """
    Validate a price DataFrame before including it in optimisation.
    Returns: {ok: bool, reason: str, days: int}
    Flags: insufficient history, zero-volume days, extreme daily moves (artifact).
    HIGH/D1: zero-volume and >15% daily moves indicate bad data, not real returns.
    """
    if df is None or df.empty:
        return {"ok": False, "reason": "no data", "days": 0}

    try:
        cl = df["Close"]
        if hasattr(cl, "iloc") and cl.ndim > 1:
            cl = cl.iloc[:, 0]
        cl = cl.dropna().astype(float)
    except Exception:
        return {"ok": False, "reason": "Close column malformed", "days": 0}

    days = len(cl)
    if days < MIN_HISTORY_DAYS:
        return {"ok": False, "reason": f"only {days} days (<{MIN_HISTORY_DAYS} required)", "days": days}

    # Check for zero-volume days (yfinance artifact / market halts)
    if "Volume" in df.columns:
        try:
            vol = df["Volume"].dropna().astype(float)
            zero_vol = int((vol == 0).sum())
            if zero_vol > days * 0.10:   # >10% zero-volume days
                return {"ok": False, "reason": f"{zero_vol} zero-volume days (>{10}% of history)", "days": days}
        except Exception:
            pass

    # Check for extreme daily moves that indicate corporate action artifacts
    log_ret = np.diff(np.log(cl.values))
    extreme = int(np.sum(np.abs(log_ret) > 0.20))  # >20% single-day move
    if extreme > 2:
        return {"ok": False, "reason": f"{extreme} extreme daily moves (>20%) — likely data artifacts", "days": days}

    return {"ok": True, "reason": "pass", "days": days}


# ── Returns computation ───────────────────────────────────────────────────────

def compute_log_returns(df_dict: dict) -> tuple:
    """
    Compute daily log returns matrix from dict of {name: DataFrame}.
    Returns: (returns_matrix np.ndarray [days x stocks], names list, excluded list)
    Only stocks passing data quality check are included.
    Uses most recent MIN_HISTORY_DAYS trading days.
    """
    valid_series = {}
    excluded     = []

    for name, df in df_dict.items():
        qc = check_data_quality(name, df)
        if not qc["ok"]:
            excluded.append((name, qc["reason"]))
            continue
        try:
            cl = df["Close"]
            if hasattr(cl, "iloc") and cl.ndim > 1:
                cl = cl.iloc[:, 0]
            cl = cl.dropna().astype(float)
            log_ret = np.diff(np.log(cl.values))
            valid_series[name] = log_ret
        except Exception as e:
            excluded.append((name, str(e)[:60]))

    if len(valid_series) < 2:
        return np.array([]), list(valid_series.keys()), excluded

    # Align to common length — use shortest valid series
    min_len = min(len(s) for s in valid_series.values())
    min_len = min(min_len, MIN_HISTORY_DAYS * 3)  # cap at ~9 months

    names   = list(valid_series.keys())
    matrix  = np.column_stack([s[-min_len:] for s in valid_series.values()])
    return matrix, names, excluded


# ── Winsorization ─────────────────────────────────────────────────────────────

def winsorize_returns(returns: np.ndarray) -> np.ndarray:
    """
    Clip each column (stock) at the WINSOR_PCTILE percentile.
    HIGH/D3: corporate action splits/mergers cause extreme outlier log returns
    that corrupt all 2000 bootstrap scenarios if not clipped.
    """
    if returns.size == 0:
        return returns
    out = returns.copy()
    for j in range(out.shape[1]):
        col = out[:, j]
        lo  = np.percentile(col, 100 - WINSOR_PCTILE)
        hi  = np.percentile(col, WINSOR_PCTILE)
        out[:, j] = np.clip(col, lo, hi)
    return out


# ── Exponentially weighted bootstrap ─────────────────────────────────────────

def bootstrap_scenarios(returns: np.ndarray,
                        n: int = N_SCENARIOS) -> np.ndarray:
    """
    Generate n scenario vectors by sampling rows from returns matrix.
    Exponential weighting: recent rows are sampled more frequently.
    HIGH/A1: if the 90-day window spans a regime change, equal weighting
    averages the two regimes. Exponential decay means the last 30 days
    dominate, which better reflects current conditions.
    Returns: (n x stocks) scenario matrix where each row is one daily return vector.
    """
    if returns.size == 0 or n == 0:
        return np.array([])

    T = returns.shape[0]
    # Weights decay exponentially — row T-1 (today) has weight 1.0,
    # row 0 (oldest) has weight EXP_DECAY^(T-1)
    weights = np.array([EXP_DECAY ** (T - 1 - t) for t in range(T)])
    weights /= weights.sum()

    indices   = np.random.choice(T, size=n, replace=True, p=weights)
    scenarios = returns[indices, :]
    return scenarios


# ── Efficient Frontier ────────────────────────────────────────────────────────

def compute_efficient_frontier(scenarios: np.ndarray,
                                names: list,
                                n_points: int = 12) -> list:
    """
    Solve optimisation at n_points different risk aversion values.
    Returns list of dicts: [{lambda, weights, exp_ret, cvar, sharpe}, ...]
    Used to draw the efficient frontier chart.
    """
    lambdas = np.logspace(np.log10(0.1), np.log10(5.0), n_points)
    frontier = []
    for lam in lambdas:
        result = optimise_mean_cvar(scenarios, names, risk_aversion=float(lam))
        if result.get("status") == "optimal":
            frontier.append({
                "lambda":   round(float(lam), 3),
                "weights":  result["weights"],
                "exp_ret":  result["exp_ret"],
                "cvar":     result["cvar"],
                "sharpe":   result.get("sharpe", 0),
            })
    return frontier


# ── Core optimiser ────────────────────────────────────────────────────────────

def optimise_mean_cvar(scenarios: np.ndarray,
                       names: list,
                       risk_aversion: float = 1.0,
                       max_weight: float = MAX_WEIGHT,
                       min_stocks: int = MIN_STOCKS) -> dict:
    """
    Solve the Mean-CVaR optimisation problem (Rockafellar-Uryasev 2000).

    Minimise:   -lambda * E[w'r] + CVaR_alpha(w'r)
    Subject to: sum(w) = 1
                0 <= w_i <= max_weight
                CVaR reformulation via auxiliary variables

    CVaR reformulation (makes it a linear programme):
        CVaR = VaR + 1/(n*(1-alpha)) * sum(max(loss_i - VaR, 0))
    Introduce: z_i >= 0,  z_i >= -r_i'w - zeta  (loss exceedances)
    Then: CVaR = zeta + 1/(n*(1-alpha)) * sum(z_i)

    Returns dict: {status, weights, names, exp_ret, cvar, sharpe,
                   exp_ret_after_cost, confidence_lo, confidence_hi,
                   n_stocks, excluded_below_floor}
    """
    if not CVXPY_AVAILABLE:
        return {"status": "cvxpy_not_installed",
                "message": "Add cvxpy to requirements.txt and redeploy."}

    if scenarios.size == 0 or len(names) < 2:
        return {"status": "insufficient_data"}

    n_scenarios, n_stocks = scenarios.shape

    try:
        w    = cp.Variable(n_stocks, nonneg=True)    # portfolio weights
        zeta = cp.Variable()                          # VaR auxiliary (alpha-quantile)
        z    = cp.Variable(n_scenarios, nonneg=True)  # CVaR exceedance variables

        # Scenario returns for this portfolio: scenarios @ w  (n_scenarios,)
        port_ret = scenarios @ w

        # CVaR constraint: z_i >= -port_ret_i - zeta  (loss - VaR exceedance)
        cvar_val = zeta + (1.0 / (n_scenarios * (1.0 - CVAR_ALPHA))) * cp.sum(z)

        # Expected return
        exp_ret  = cp.sum(port_ret) / n_scenarios

        # Objective: maximise return - lambda * CVaR
        objective = cp.Maximize(exp_ret - risk_aversion * cvar_val)

        constraints = [
            cp.sum(w) == 1,
            w <= max_weight,
            z >= -port_ret - zeta,
        ]

        prob = cp.Problem(objective, constraints)
        prob.solve(solver=cp.CLARABEL, warm_start=True)

        if prob.status not in ("optimal", "optimal_inaccurate"):
            return {"status": prob.status or "failed"}

        raw_weights = np.array(w.value).flatten()
        raw_weights = np.maximum(raw_weights, 0)

        # Apply minimum floor — remove positions below 5%, redistribute
        floor_mask    = raw_weights >= MIN_WEIGHT_FLOOR
        n_above_floor = int(floor_mask.sum())

        if n_above_floor < min_stocks:
            # Not enough stocks above floor — take top min_stocks by weight
            top_idx   = np.argsort(raw_weights)[::-1][:min_stocks]
            floor_mask = np.zeros(n_stocks, dtype=bool)
            floor_mask[top_idx] = True

        final_weights = np.where(floor_mask, raw_weights, 0.0)
        total = final_weights.sum()
        if total > 0:
            final_weights /= total   # renormalise to sum=1

        # Compute realised metrics on final weights
        port_scenario_rets = scenarios @ final_weights
        e_ret      = float(np.mean(port_scenario_rets)) * 252   # annualise
        port_std   = float(np.std(port_scenario_rets)) * np.sqrt(252)
        sorted_ret = np.sort(port_scenario_rets)
        cutoff_idx = int(np.floor(n_scenarios * (1.0 - CVAR_ALPHA)))
        cvar_daily = -float(np.mean(sorted_ret[:cutoff_idx]))    # daily CVaR (positive = loss)

        sharpe = round(e_ret / port_std, 2) if port_std > 0 else 0.0

        # Transaction cost adjustment
        e_ret_after_cost = e_ret - ROUND_TRIP_COST * 252  # annualised cost

        # Confidence band: ±1 std dev of scenario annual returns
        scenario_annual = port_scenario_rets * 252
        conf_lo = float(np.percentile(scenario_annual, 10))
        conf_hi = float(np.percentile(scenario_annual, 90))

        # Build allocation list
        allocation = []
        for i, name in enumerate(names):
            w_i = float(final_weights[i])
            if w_i >= MIN_WEIGHT_FLOOR * 0.5:   # show if >= 2.5%
                allocation.append({
                    "name":   name,
                    "weight": round(w_i, 4),
                    "pct":    round(w_i * 100, 1),
                })
        allocation.sort(key=lambda x: x["weight"], reverse=True)

        excluded_below_floor = int((raw_weights > 0.01).sum()) - len(allocation)

        return {
            "status":              "optimal",
            "weights":             final_weights.tolist(),
            "allocation":          allocation,
            "names":               names,
            "exp_ret":             round(e_ret * 100, 2),          # % annualised
            "exp_ret_after_cost":  round(e_ret_after_cost * 100, 2),
            "cvar":                round(cvar_daily * 100, 2),      # daily CVaR %
            "sharpe":              sharpe,
            "n_stocks":            len(allocation),
            "conf_lo":             round(conf_lo * 100, 1),
            "conf_hi":             round(conf_hi * 100, 1),
            "excluded_below_floor": max(0, excluded_below_floor),
        }

    except Exception as e:
        log_error("portfolio:optimise_mean_cvar", e)
        return {"status": "error", "message": str(e)[:120]}


# ── Stability score ───────────────────────────────────────────────────────────

def compute_stability_score(scenarios: np.ndarray,
                             names: list,
                             risk_aversion: float = 1.0,
                             n_perturbations: int = 10) -> dict:
    """
    Perturbation test: re-run optimiser n times with ±5% random noise on returns.
    MEDIUM/validation Layer 2: small input changes should not flip allocations.
    Returns: {score: 'STABLE'|'MODERATE'|'UNSTABLE', weight_std: dict}
    Threshold: flag UNSTABLE if any stock weight std dev >= 15%.
    """
    if not CVXPY_AVAILABLE or scenarios.size == 0:
        return {"score": "UNKNOWN", "weight_std": {}}

    weight_runs = {n: [] for n in names}
    for _ in range(n_perturbations):
        noise    = 1.0 + np.random.uniform(-0.05, 0.05, scenarios.shape)
        noisy_sc = scenarios * noise
        res      = optimise_mean_cvar(noisy_sc, names, risk_aversion=risk_aversion)
        if res.get("status") == "optimal":
            for i, n in enumerate(names):
                weight_runs[n].append(res["weights"][i])

    if all(len(v) == 0 for v in weight_runs.values()):
        return {"score": "UNKNOWN", "weight_std": {}}

    weight_std = {}
    for n, vals in weight_runs.items():
        if vals:
            weight_std[n] = round(float(np.std(vals)) * 100, 1)

    max_std = max(weight_std.values()) if weight_std else 0
    if max_std < 8:
        score = "STABLE"
    elif max_std < 15:
        score = "MODERATE"
    else:
        score = "UNSTABLE"

    return {"score": score, "weight_std": weight_std, "max_std": round(max_std, 1)}


# ── Regime / stress detection ─────────────────────────────────────────────────

def detect_stress_regime(returns: np.ndarray,
                          vix_df=None) -> dict:
    """
    CRITICAL/P1 + CRITICAL/M1: detect market stress before showing allocation.

    Checks:
      1. VIX level — if VIX daily close > VIX_STRESS_THRESH → stress
      2. Correlation crisis — if avg pairwise 30-day correlation > CORR_CRISIS_THRESH
         diversification has collapsed (COVID/crisis pattern)

    Returns: {stress: bool, reason: str, mode: 'normal'|'stress'|'crisis'}
    """
    result = {"stress": False, "reason": "", "mode": "normal",
              "vix": None, "avg_corr": None}

    # VIX check
    if vix_df is not None and not vix_df.empty:
        try:
            cl = vix_df["Close"]
            if hasattr(cl, "iloc") and cl.ndim > 1:
                cl = cl.iloc[:, 0]
            latest_vix = float(cl.dropna().iloc[-1])
            result["vix"] = round(latest_vix, 1)
            if latest_vix > VIX_STRESS_THRESH:
                result["stress"] = True
                result["mode"]   = "stress"
                result["reason"] = f"VIX at {latest_vix:.1f} (>{VIX_STRESS_THRESH}) — market fear elevated"
        except Exception:
            pass

    # Correlation crisis check (uses last 30 rows of return matrix)
    if returns.size > 0 and returns.shape[1] >= 3:
        try:
            recent = returns[-30:, :] if returns.shape[0] >= 30 else returns
            corr_matrix  = np.corrcoef(recent.T)
            n = corr_matrix.shape[0]
            # Average of upper triangle (pairwise correlations, excluding self)
            upper_tri = corr_matrix[np.triu_indices(n, k=1)]
            avg_corr  = float(np.mean(upper_tri))
            result["avg_corr"] = round(avg_corr, 2)
            if avg_corr > CORR_CRISIS_THRESH:
                result["stress"] = True
                result["mode"]   = "crisis"
                result["reason"] = (
                    f"Average stock correlation = {avg_corr:.2f} "
                    f"(>{CORR_CRISIS_THRESH}) — diversification has collapsed"
                )
        except Exception:
            pass

    return result


# ── Regime conflict check (Layer 4) ──────────────────────────────────────────

def check_regime_conflicts(allocation: list, stock_signals: dict) -> list:
    """
    Layer 4: cross-check optimiser output against existing Weinstein/Elder signals.
    OPEN-006/Layer 4: if optimiser allocates >=10% to a stock with verdict AVOID
    → flag conflict. User sees warning before acting.

    allocation:    list of {name, weight, pct} from optimise_mean_cvar
    stock_signals: dict of {name: {signal, score, verdict}} from signal_score()

    Returns: list of {name, weight_pct, signal, severity} conflict items.
    """
    conflicts = []
    avoid_signals = {"AVOID", "CAUTION"}
    for item in allocation:
        name  = item["name"]
        wpct  = item["pct"]
        sig   = stock_signals.get(name, {})
        verdict = sig.get("signal", "") or sig.get("verdict", "")
        if wpct >= 10.0 and verdict.upper() in avoid_signals:
            conflicts.append({
                "name":       name,
                "weight_pct": wpct,
                "signal":     verdict,
                "severity":   "HIGH" if verdict.upper() == "AVOID" else "MEDIUM",
            })
    return conflicts
