"""Phase 2 — cycle_phase.py tests. RED until src/accuracy/cycle_phase.py is implemented."""
import pytest
from src.accuracy.cycle_phase import derive_cycle_phase

VALID_PHASES = {
    "early_bull", "mid_bull", "late_bull",
    "early_bear", "mid_bear", "late_bear",
}


def test_risk_on_above_ma_low_vix():
    phase = derive_cycle_phase("RISK_ON", nifty_close=22000, nifty_200ma=20000, vix=15.0)
    assert phase == "mid_bull"


def test_risk_on_above_ma_high_vix():
    phase = derive_cycle_phase("RISK_ON", nifty_close=22000, nifty_200ma=20000, vix=25.0)
    assert phase == "late_bull"


def test_risk_on_below_ma_low_vix():
    phase = derive_cycle_phase("RISK_ON", nifty_close=18000, nifty_200ma=20000, vix=15.0)
    assert phase == "early_bull"


def test_risk_off_below_ma_high_vix():
    phase = derive_cycle_phase("RISK_OFF", nifty_close=18000, nifty_200ma=20000, vix=25.0)
    assert phase == "mid_bear"


def test_risk_off_below_ma_low_vix():
    phase = derive_cycle_phase("RISK_OFF", nifty_close=18000, nifty_200ma=20000, vix=12.0)
    assert phase == "late_bear"


def test_risk_off_above_ma_high_vix():
    phase = derive_cycle_phase("RISK_OFF", nifty_close=22000, nifty_200ma=20000, vix=25.0)
    assert phase == "early_bear"


def test_stagflation_below_ma_high_vix():
    phase = derive_cycle_phase("STAGFLATION", nifty_close=18000, nifty_200ma=20000, vix=25.0)
    assert phase == "mid_bear"


def test_deflation_below_ma_low_vix():
    phase = derive_cycle_phase("DEFLATION", nifty_close=18000, nifty_200ma=20000, vix=12.0)
    assert phase == "late_bear"


def test_all_results_are_valid_phases():
    """Exhaustive check: every PHASE_RULES entry returns a valid phase label."""
    regimes = ["RISK_ON", "RISK_OFF", "STAGFLATION", "DEFLATION"]
    for regime in regimes:
        for above in [True, False]:
            for vix_low in [True, False]:
                close = 22000 if above else 18000
                vix = 12.0 if vix_low else 25.0
                phase = derive_cycle_phase(regime, close, 20000, vix)
                assert phase in VALID_PHASES, f"Invalid phase {phase!r} for {regime}/{above}/{vix_low}"


def test_never_returns_none():
    phase = derive_cycle_phase("DEFLATION", 18000, 20000, 25.0)
    assert phase is not None
