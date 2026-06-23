"""Cycle phase derivation — maps macro regime + technical position to one of 6 market phases.

PHASE_RULES format (list of dicts, evaluated by table lookup):
  regime    : str  — "RISK_ON" | "RISK_OFF" | "STAGFLATION" | "DEFLATION"
  above_ma  : bool — True if nifty_close > nifty_200ma
  vix_low   : bool — True if vix < VIX_THRESHOLD (20.0)
  phase     : str  — one of VALID_PHASES
  test_close, test_200ma, test_vix : representative values used by council test_all_results_are_valid_phases

VIX logic: low VIX in a RISK_OFF/below-MA environment signals late-bear (capitulation past,
complacency setting in at bottom), not safety. This is counter-intuitive but empirically correct.
"""
from __future__ import annotations

VIX_THRESHOLD = 20.0

VALID_PHASES = frozenset({
    "early_bull", "mid_bull", "late_bull",
    "early_bear", "mid_bear", "late_bear",
})

PHASE_RULES: list[dict] = [
    # RISK_ON — bull market phases
    {"regime": "RISK_ON",     "above_ma": True,  "vix_low": True,  "phase": "mid_bull",   "test_close": 22000, "test_200ma": 20000, "test_vix": 12.0},
    {"regime": "RISK_ON",     "above_ma": True,  "vix_low": False, "phase": "late_bull",  "test_close": 22000, "test_200ma": 20000, "test_vix": 25.0},
    {"regime": "RISK_ON",     "above_ma": False, "vix_low": True,  "phase": "early_bull", "test_close": 18000, "test_200ma": 20000, "test_vix": 12.0},
    {"regime": "RISK_ON",     "above_ma": False, "vix_low": False, "phase": "early_bear", "test_close": 18000, "test_200ma": 20000, "test_vix": 25.0},
    # RISK_OFF — bear market phases
    {"regime": "RISK_OFF",    "above_ma": True,  "vix_low": True,  "phase": "late_bull",  "test_close": 22000, "test_200ma": 20000, "test_vix": 12.0},
    {"regime": "RISK_OFF",    "above_ma": True,  "vix_low": False, "phase": "early_bear", "test_close": 22000, "test_200ma": 20000, "test_vix": 25.0},
    {"regime": "RISK_OFF",    "above_ma": False, "vix_low": True,  "phase": "late_bear",  "test_close": 18000, "test_200ma": 20000, "test_vix": 12.0},
    {"regime": "RISK_OFF",    "above_ma": False, "vix_low": False, "phase": "mid_bear",   "test_close": 18000, "test_200ma": 20000, "test_vix": 25.0},
    # STAGFLATION — growth slowing, inflation elevated
    {"regime": "STAGFLATION", "above_ma": True,  "vix_low": True,  "phase": "late_bull",  "test_close": 22000, "test_200ma": 20000, "test_vix": 12.0},
    {"regime": "STAGFLATION", "above_ma": True,  "vix_low": False, "phase": "early_bear", "test_close": 22000, "test_200ma": 20000, "test_vix": 25.0},
    {"regime": "STAGFLATION", "above_ma": False, "vix_low": True,  "phase": "early_bear", "test_close": 18000, "test_200ma": 20000, "test_vix": 12.0},
    {"regime": "STAGFLATION", "above_ma": False, "vix_low": False, "phase": "mid_bear",   "test_close": 18000, "test_200ma": 20000, "test_vix": 25.0},
    # DEFLATION — growth slowing, deflation pressure
    {"regime": "DEFLATION",   "above_ma": True,  "vix_low": True,  "phase": "late_bull",  "test_close": 22000, "test_200ma": 20000, "test_vix": 12.0},
    {"regime": "DEFLATION",   "above_ma": True,  "vix_low": False, "phase": "early_bear", "test_close": 22000, "test_200ma": 20000, "test_vix": 25.0},
    {"regime": "DEFLATION",   "above_ma": False, "vix_low": True,  "phase": "late_bear",  "test_close": 18000, "test_200ma": 20000, "test_vix": 12.0},
    {"regime": "DEFLATION",   "above_ma": False, "vix_low": False, "phase": "mid_bear",   "test_close": 18000, "test_200ma": 20000, "test_vix": 25.0},
]

_LOOKUP: dict[tuple, str] = {
    (r["regime"], r["above_ma"], r["vix_low"]): r["phase"]
    for r in PHASE_RULES
}


def derive_cycle_phase(
    regime: str,
    nifty_close: float,
    nifty_200ma: float,
    vix: float,
) -> str:
    """Return one of 6 cycle phases based on macro regime + price vs 200MA + VIX level.
    Falls back to "mid_bear" for unrecognised regimes.
    """
    key = (regime, nifty_close > nifty_200ma, vix < VIX_THRESHOLD)
    return _LOOKUP.get(key, "mid_bear")
