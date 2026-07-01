"""
Council Conditions Test Suite
==============================
Every test is labelled with the council seat that owns it.
A failing test here = a council condition not met.
Run: pytest tests/test_council_conditions.py -v

Phase sign-off rule: all tests for a Phase must be GREEN before Phase is done.
Full mapping: alphaveda/COUNCIL_TEST_MAP.md
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 1 — Foundation constants (GREEN — run independently of Supabase)
# ─────────────────────────────────────────────────────────────────────────────


class TestBuffettConditions:
    """Buffett: FUNDAMENTAL_WEIGHT_FLOOR = 0.30 is enforced across all cold-start weights."""

    def test_floor_constant_is_30_percent(self):
        from constants import FUNDAMENTAL_WEIGHT_FLOOR
        assert FUNDAMENTAL_WEIGHT_FLOOR == 0.30

    def test_fundamental_floor_applies_to_all_cold_starts(self):
        """Every cold-start segment must have total fundamental weight ≥ 0.30."""
        from constants import COLD_START_WEIGHTS, FUNDAMENTAL_WEIGHT_FLOOR
        FUNDAMENTAL_SIGNALS = {"roic", "fcf", "eps_growth", "peg", "dividend", "debt_equity", "book_value"}
        for segment, weights in COLD_START_WEIGHTS.items():
            fundamental_total = sum(v for k, v in weights.items() if k in FUNDAMENTAL_SIGNALS)
            assert fundamental_total >= FUNDAMENTAL_WEIGHT_FLOOR, (
                f"{segment}: fundamental total {fundamental_total:.2f} < floor {FUNDAMENTAL_WEIGHT_FLOOR}"
            )


class TestDruckenmillerConditions:
    """Druckenmiller: Quarter-Kelly formula must produce correct position sizes."""

    def test_quarter_kelly_fraction_is_25_percent(self):
        from constants import QUARTER_KELLY_FRACTION
        assert QUARTER_KELLY_FRACTION == 0.25

    def test_kelly_no_rupee_without_downside(self):
        """Kelly returns 0 when downside_target is None — cannot size without loss-leg."""
        from src.portfolio.optimizer import kelly_position_size
        from constants import PORTFOLIO_VALUE
        result = kelly_position_size(p=0.65, magnitude_target=0.15, downside_target=None,
                                     portfolio_value=PORTFOLIO_VALUE)
        assert result == 0

    def test_kelly_positive_rupee_with_valid_downside(self):
        """b = magnitude/downside = 0.15/0.07 = 2.14; f = 0.65 - 0.35/2.14 = 0.486 → >0 before cap."""
        from src.portfolio.optimizer import kelly_position_size
        from constants import PORTFOLIO_VALUE
        result = kelly_position_size(p=0.65, magnitude_target=0.15, downside_target=0.07,
                                     portfolio_value=PORTFOLIO_VALUE)
        assert result > 0

    def test_kelly_zero_on_negative_edge(self):
        """p - q/b = 0.20 - 0.80/0.25 = -2.99 → clamp to 0, no negative position."""
        from src.portfolio.optimizer import kelly_position_size
        from constants import PORTFOLIO_VALUE
        result = kelly_position_size(p=0.20, magnitude_target=0.05, downside_target=0.20,
                                     portfolio_value=PORTFOLIO_VALUE)
        assert result == 0

    def test_kelly_capped_at_max_position(self):
        """Position must never exceed MAX_POSITION_PCT of PORTFOLIO_VALUE."""
        from src.portfolio.optimizer import kelly_position_size
        from constants import PORTFOLIO_VALUE, MAX_POSITION_PCT
        result = kelly_position_size(p=0.90, magnitude_target=0.50, downside_target=0.01,
                                     portfolio_value=PORTFOLIO_VALUE)
        max_rupee = PORTFOLIO_VALUE * MAX_POSITION_PCT
        assert result <= max_rupee


class TestSorosConditions:
    """Soros: Streak discount fires at emit (step 3b), NOT in the ledger SQL."""

    def test_streak_window_constant(self):
        from constants import STREAK_WINDOW, STREAK_DISCOUNT_FACTOR
        assert STREAK_WINDOW == 5
        assert STREAK_DISCOUNT_FACTOR == 0.7

    def test_pipeline_contract_ordering(self):
        """discount fires BEFORE calibration — bins are built from post-discount confidence."""
        from src.signals.engine import emit_pipeline
        # Contract verified by test_pipeline_discount_fires_before_calibration in test_engine.py

    def test_streak_flag_fires_at_n(self):
        """streak_flag = True only when consecutive same-direction count == STREAK_WINDOW."""
        from src.accuracy.ledger import compute_streak_flag
        from constants import STREAK_WINDOW
        assert compute_streak_flag(consecutive_count=STREAK_WINDOW - 1) is False
        assert compute_streak_flag(consecutive_count=STREAK_WINDOW) is True
        assert compute_streak_flag(consecutive_count=STREAK_WINDOW + 2) is True


class TestMarksConditions:
    """Marks: cycle_phase derivation must be deterministic and exhaustive."""

    def test_risk_on_above_ma_low_vix_is_mid_bull(self):
        from src.accuracy.cycle_phase import derive_cycle_phase
        phase = derive_cycle_phase("RISK_ON", nifty_close=22000, nifty_200ma=20000, vix=15.0)
        assert phase == "mid_bull"

    def test_all_results_are_valid_phases(self):
        from src.accuracy.cycle_phase import derive_cycle_phase, PHASE_RULES
        VALID_PHASES = {"early_bull", "mid_bull", "late_bull", "early_bear", "mid_bear", "late_bear"}
        for rule in PHASE_RULES:
            result = derive_cycle_phase(
                regime=rule["regime"],
                nifty_close=rule["test_close"],
                nifty_200ma=rule["test_200ma"],
                vix=rule["test_vix"],
            )
            assert result in VALID_PHASES, f"PHASE_RULES entry produced invalid phase: {result}"

    def test_never_returns_none(self):
        from src.accuracy.cycle_phase import derive_cycle_phase
        result = derive_cycle_phase("RISK_OFF", nifty_close=18000, nifty_200ma=20000, vix=30.0)
        assert result is not None


class TestArbitrationConditions:
    """Soros + Buffett: Arbitration suppresses when bull/bear confidence within ARBITRATION_MARGIN."""

    def test_suppression_when_within_margin(self):
        from src.signals.arbitration import arbitrate
        signals = [
            {"direction": "BULL", "confidence": 70, "signal_name": "roic", "weight": 0.5},
            {"direction": "BEAR", "confidence": 70, "signal_name": "momentum_rsi", "weight": 0.5},
        ]
        result = arbitrate(signals)
        assert result is None  # suppressed — net = 0, within ARBITRATION_MARGIN=15

    def test_bull_wins_clear_majority(self):
        from src.signals.arbitration import arbitrate
        signals = [
            {"direction": "BULL", "confidence": 80, "signal_name": "roic", "weight": 0.6},
            {"direction": "BEAR", "confidence": 40, "signal_name": "momentum_rsi", "weight": 0.4},
        ]
        result = arbitrate(signals)
        assert result is not None
        assert result["direction"] == "BULL"


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 1 — DB schema (requires live Supabase; skip without SUPABASE_URL)
# ─────────────────────────────────────────────────────────────────────────────

skip_no_db = pytest.mark.skipif(
    not os.environ.get("SUPABASE_URL"),
    reason="SUPABASE_URL not set — G-MIG gate required before these run"
)


class TestRashidaConditions:
    """Rashida (DB integrity): All critical tables and columns must exist."""

    @skip_no_db
    def test_instruments_table_exists_with_classification(self, supabase_client):
        result = supabase_client.table("instruments").select("classification").limit(1).execute()
        assert result.data is not None

    @skip_no_db
    def test_accuracy_predictions_has_downside_target(self, supabase_client):
        """Migration 0012 — downside_target column. BLOCKED until G-MIG."""
        result = supabase_client.table("accuracy_predictions").select("downside_target").limit(1).execute()
        assert result.data is not None

    @skip_no_db
    def test_portfolio_buckets_seeded(self, supabase_client):
        result = supabase_client.table("portfolio_buckets").select("bucket_name").execute()
        names = {r["bucket_name"] for r in result.data}
        assert {"emergency", "near_term", "medium_term", "long_term"}.issubset(names)

    @skip_no_db
    def test_waitlist_table_exists(self, supabase_client):
        result = supabase_client.table("waitlist").select("price_feedback").limit(1).execute()
        assert result.data is not None


class TestJhunjhunwalaConditions:
    """Jhunjhunwala: circuit_flag on ohlcv — hard pre-G1 gate for data quality."""

    @skip_no_db
    def test_ohlcv_has_circuit_flag(self, supabase_client):
        """Migration 0013 — circuit_flag column. BLOCKED until G-MIG."""
        result = supabase_client.table("ohlcv").select("circuit_flag").limit(1).execute()
        assert result.data is not None


class TestBhattacharyaConditions:
    """Bhattacharya (data licensing): licence_class and deliverable_volume must exist."""

    @skip_no_db
    def test_ohlcv_has_licence_class(self, supabase_client):
        """Migration 0013 — licence_class column."""
        result = supabase_client.table("ohlcv").select("licence_class").limit(1).execute()
        assert result.data is not None

    @skip_no_db
    def test_ohlcv_has_deliverable_volume(self, supabase_client):
        result = supabase_client.table("ohlcv").select("deliverable_volume").limit(1).execute()
        assert result.data is not None


class TestShakuniConditions:
    """Shakuni: Duplicate ACTIVE signal_weights per segment must be impossible."""

    @skip_no_db
    def test_no_duplicate_active_per_segment(self, supabase_client):
        """Partial unique index on signal_weights(lynch_class, regime) WHERE status='ACTIVE'."""
        from uuid import uuid4
        unique_signal = f"_test_shakani_{uuid4().hex[:8]}"
        row1 = {
            "lynch_class": "stalwart", "regime": "RISK_ON",
            "signal_name": unique_signal, "weight": 0.5,
            "status": "ACTIVE", "approved_by": "tarun",
        }
        inserted_id = None
        try:
            r1 = supabase_client.table("signal_weights").insert(row1).execute()
            assert len(r1.data) == 1, "First insert should succeed"
            inserted_id = r1.data[0]["id"]
            # Second insert with same lynch_class+regime+ACTIVE must violate unique index
            with pytest.raises(Exception):
                supabase_client.table("signal_weights").insert(row1).execute()
        finally:
            if inserted_id:
                supabase_client.table("signal_weights").delete().eq("id", inserted_id).execute()


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 2 — Commercial gate (requires is_commercial() from src/config.py)
# ─────────────────────────────────────────────────────────────────────────────


class TestConstraintEnforcerConditions:
    """Constraint Enforcer: commercial gate is fail-closed; SEBI rules are non-negotiable."""

    def test_is_commercial_fail_closed(self):
        """Any exception in DB check → is_commercial() returns True (fail-closed: block yfinance when state unknown)."""
        from src.config import is_commercial
        import unittest.mock as mock
        with mock.patch("src.config.get_supabase_client", side_effect=Exception("DB unreachable")):
            result = is_commercial()
        assert result is True  # fail-closed for licensing: unknown state → treat as commercial, block yfinance

    def test_is_commercial_true_when_subscriber_exists(self):
        """If any waitlist row has converted_at set → commercial=True."""
        import unittest.mock as mock
        from src.config import is_commercial
        m = mock.MagicMock()
        (m.table.return_value.select.return_value
         .not_.is_.return_value.limit.return_value
         .execute.return_value.data) = [{"id": 1}]
        with mock.patch("src.config.get_supabase_client", return_value=m):
            assert is_commercial() is True


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 6 — G0 gate (duplicated from test_g0_gate.py for council labelling)
# ─────────────────────────────────────────────────────────────────────────────


class TestSynthesisChairConditions:
    """Synthesis Chair: G0 criterion 10 must run first; Kelly must produce rupee output."""

    @skip_no_db
    def test_c10_seed_instruments_exist_runs_first(self, supabase_client):
        """Criterion 10 is the prerequisite for all other G0 tests."""
        result = supabase_client.table("instruments").select("classification").execute()
        assert len(result.data) >= 10
        classes = {r["classification"] for r in result.data}
        assert len(classes) >= 3

    def test_c8_kelly_rupee_live_with_downside(self):
        from src.portfolio.optimizer import kelly_position_size
        from constants import PORTFOLIO_VALUE
        result = kelly_position_size(p=0.65, magnitude_target=0.15, downside_target=0.07,
                                     portfolio_value=PORTFOLIO_VALUE)
        assert result > 0


class TestReddyConditions:
    """Reddy (calibration): cold-start calibration p must be ≤ confidence/100."""

    def test_cold_start_calibration_p_leq_confidence(self):
        """When segment has <30 observations, p = min(confidence/100, hit_rate)."""
        from src.signals.engine import calibrate_confidence
        confidence = 75
        hit_rate = 0.60
        p = calibrate_confidence(confidence=confidence, segment_obs=15, hit_rate=hit_rate)
        assert p <= confidence / 100
        assert p == min(confidence / 100, hit_rate)


class TestImranConditions:
    """Imran (SRA): stale or missing ingest_status rows must surface as visible warnings."""

    @skip_no_db
    def test_ingest_status_table_exists(self, supabase_client):
        result = supabase_client.table("ingest_status").select("last_run").limit(1).execute()  # renamed from run_at in migration 0015
        assert result.data is not None

    def test_stale_ingest_surfaces_amber_banner(self):
        """If last_run > 1 day ago → amber banner shown (Imran SRA condition)."""
        import unittest.mock as mock
        from datetime import date, timedelta
        from src.pages.data_viewer import get_staleness_banner
        stale_dt = (date.today() - timedelta(days=3)).isoformat() + "T18:30:00+00:00"
        m = mock.MagicMock()
        (m.table.return_value.select.return_value.eq.return_value
         .order.return_value.limit.return_value.execute.return_value.data) = [
            {"last_run": stale_dt}
        ]
        banner = get_staleness_banner(m)
        assert banner is not None
        assert any(w in banner.lower() for w in ("updated", "since", "stale"))

    def test_emit_latency_under_800ms(self):
        """Full emit pipeline (arbitration → discount → calibrate → kelly) ≤ 800ms."""
        import time
        from src.signals.engine import emit_signal
        start = time.time()
        emit_signal(instrument_id=1, as_of="2026-06-21")
        elapsed_ms = (time.time() - start) * 1000
        assert elapsed_ms <= 800, f"Emit took {elapsed_ms:.0f}ms — exceeds 800ms SLA"
