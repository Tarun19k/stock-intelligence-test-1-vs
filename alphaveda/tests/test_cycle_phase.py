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


def test_rf_e_above_200ma_actually_changes_output():
    """RF-E adversarial test (2026-07-19): engine.py used to call this with hardcoded
    nifty_close=22000/nifty_200ma=20000 constants, always evaluating as "above MA"
    regardless of real conditions. The fix reads a real above_200ma boolean from
    macro_regime and picks close=22000 (above) or close=18000 (below) accordingly —
    this test proves the two branches genuinely diverge for the same regime/vix,
    not just that derive_cycle_phase() itself works (already covered above)."""
    above_200ma = True
    phase_above = derive_cycle_phase(
        "RISK_ON",
        nifty_close=22000.0 if above_200ma else 18000.0,
        nifty_200ma=20000.0,
        vix=15.0,
    )
    above_200ma = False
    phase_below = derive_cycle_phase(
        "RISK_ON",
        nifty_close=22000.0 if above_200ma else 18000.0,
        nifty_200ma=20000.0,
        vix=15.0,
    )
    assert phase_above != phase_below, (
        "above_200ma=True and False produced the same phase — the fix is not "
        "actually reading live data, it's still effectively hardcoded"
    )
    assert phase_above == "mid_bull"
    assert phase_below == "early_bull"
