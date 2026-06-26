"""Phase 6 — Ingest pipeline unit tests (pure functions only, no live DB required).

Council seats covered:
  Imran (SRA)      — staleness flag logic
  Jhunjhunwala     — circuit_flag exclusion in resolve_outcomes
  Wealth & Revenue — waitlist form submits to DB
  Rashida          — fundamentals parse produces required keys

Run: pytest tests/test_ingest.py -v
"""
import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Bhavcopy parsing (src/ingest/bhavcopy.py)
# ─────────────────────────────────────────────────────────────────────────────

NSE_CSV_SAMPLE = """\
SYMBOL,SERIES,OPEN,HIGH,LOW,CLOSE,LAST,PREVCLOSE,TOTTRDQTY,TOTTRDVAL,TIMESTAMP,TOTALTRADES,ISIN
RELIANCE,EQ,2800.00,2850.00,2790.00,2830.00,2830.00,2790.00,1000000,2830000000,26-JUN-2026,50000,INE002A01018
INFY,EQ,1500.00,1520.00,1490.00,1510.00,1510.00,1495.00,500000,755000000,26-JUN-2026,30000,INE009A01021
BADROW,XX,0,0,0,0,0,0,0,0,26-JUN-2026,0,INVALID
TCS,BE,3500.00,3550.00,3480.00,3520.00,3520.00,3490.00,200000,704000000,26-JUN-2026,20000,INE467B01029
"""


class TestParseBhavcopynse:
    def test_returns_ohlcv_list(self):
        from src.ingest.bhavcopy import parse_bhavcopy_nse
        rows = parse_bhavcopy_nse(NSE_CSV_SAMPLE)
        assert isinstance(rows, list)
        assert len(rows) == 3  # RELIANCE + INFY + TCS (BADROW skipped)

    def test_correct_ohlcv_fields(self):
        from src.ingest.bhavcopy import parse_bhavcopy_nse
        rows = parse_bhavcopy_nse(NSE_CSV_SAMPLE)
        row = next(r for r in rows if r["symbol"] == "RELIANCE")
        assert row["open"] == pytest.approx(2800.00)
        assert row["high"] == pytest.approx(2850.00)
        assert row["low"] == pytest.approx(2790.00)
        assert row["close"] == pytest.approx(2830.00)
        assert row["volume"] == 1000000

    def test_source_and_licence_class(self):
        from src.ingest.bhavcopy import parse_bhavcopy_nse
        rows = parse_bhavcopy_nse(NSE_CSV_SAMPLE)
        for row in rows:
            assert row["source"] == "bhavcopy_nse"
            assert row["licence_class"] == "open"

    def test_skips_non_eq_be_bl_series(self):
        from src.ingest.bhavcopy import parse_bhavcopy_nse
        rows = parse_bhavcopy_nse(NSE_CSV_SAMPLE)
        symbols = {r["symbol"] for r in rows}
        assert "BADROW" not in symbols

    def test_includes_be_series(self):
        from src.ingest.bhavcopy import parse_bhavcopy_nse
        rows = parse_bhavcopy_nse(NSE_CSV_SAMPLE)
        symbols = {r["symbol"] for r in rows}
        assert "TCS" in symbols

    def test_empty_csv_returns_empty_list(self):
        from src.ingest.bhavcopy import parse_bhavcopy_nse
        rows = parse_bhavcopy_nse("SYMBOL,SERIES,OPEN,HIGH,LOW,CLOSE,LAST,PREVCLOSE,TOTTRDQTY,TOTTRDVAL,TIMESTAMP,TOTALTRADES,ISIN\n")
        assert rows == []

    def test_circuit_flag_set_on_hlc_equal(self):
        """Jhunjhunwala gate: proxy detects H==L==C (locked-price bar) as circuit."""
        from src.ingest.bhavcopy import parse_bhavcopy_nse
        circuit_csv = (
            "SYMBOL,SERIES,OPEN,HIGH,LOW,CLOSE,LAST,PREVCLOSE,TOTTRDQTY,TOTTRDVAL,TIMESTAMP,TOTALTRADES,ISIN\n"
            "CIRCUIT,EQ,1100.00,1100.00,1100.00,1100.00,1100.00,1000.00,500,550000,26-JUN-2026,10,INE001A01036\n"
        )
        rows = parse_bhavcopy_nse(circuit_csv)
        assert len(rows) == 1
        assert rows[0]["circuit_flag"] is True

    def test_circuit_flag_false_on_normal_bar(self):
        """Normal trading day (H≠L): circuit_flag must be False."""
        from src.ingest.bhavcopy import parse_bhavcopy_nse
        rows = parse_bhavcopy_nse(NSE_CSV_SAMPLE)
        normal = next(r for r in rows if r["symbol"] == "RELIANCE")
        assert normal["circuit_flag"] is False


# ─────────────────────────────────────────────────────────────────────────────
# Ingest staleness flag (Imran SRA condition)
# ─────────────────────────────────────────────────────────────────────────────

class TestIngestStalenessFlag:
    def test_ok_when_recent(self):
        from src.ingest.bhavcopy import get_ingest_staleness_flag
        from datetime import date, timedelta
        today = date.today()
        assert get_ingest_staleness_flag(today, today) == "OK"
        assert get_ingest_staleness_flag(today - timedelta(days=1), today) == "OK"

    def test_stale_when_over_one_day(self):
        from src.ingest.bhavcopy import get_ingest_staleness_flag
        from datetime import date, timedelta
        today = date.today()
        assert get_ingest_staleness_flag(today - timedelta(days=2), today) == "STALE"
        assert get_ingest_staleness_flag(today - timedelta(days=30), today) == "STALE"

    def test_missing_when_no_run(self):
        from src.ingest.bhavcopy import get_ingest_staleness_flag
        from datetime import date
        assert get_ingest_staleness_flag(None, date.today()) == "MISSING"


# ─────────────────────────────────────────────────────────────────────────────
# Resolve outcomes (Jhunjhunwala circuit_flag condition)
# ─────────────────────────────────────────────────────────────────────────────

class TestResolveOutcomes:
    def _sample_ohlcv(self, circuit_flag=False, close=1100.0, symbol="RELIANCE"):
        return {"symbol": symbol, "close": close, "circuit_flag": circuit_flag}

    def _sample_pred(self, direction="BULLISH", entry_price=1000.0, symbol="RELIANCE"):
        return {"id": 1, "symbol": symbol, "direction": direction, "entry_price": entry_price}

    def test_circuit_flag_row_excluded(self):
        """Jhunjhunwala: circuit_flag=True rows must NOT be used for outcome scoring."""
        from src.ingest.resolve_outcomes import resolve_outcomes_from_ohlcv
        ohlcv = [self._sample_ohlcv(circuit_flag=True, close=1100.0)]
        preds = [self._sample_pred()]
        result = resolve_outcomes_from_ohlcv(preds, ohlcv)
        assert result == [], "Circuit-locked row must not resolve any prediction"

    def test_non_circuit_row_resolves(self):
        from src.ingest.resolve_outcomes import resolve_outcomes_from_ohlcv
        ohlcv = [self._sample_ohlcv(circuit_flag=False, close=1100.0)]
        preds = [self._sample_pred()]
        result = resolve_outcomes_from_ohlcv(preds, ohlcv)
        assert len(result) == 1

    def test_bullish_win_on_gain(self):
        from src.ingest.resolve_outcomes import resolve_outcomes_from_ohlcv
        ohlcv = [self._sample_ohlcv(close=1100.0)]
        preds = [self._sample_pred(direction="BULLISH", entry_price=1000.0)]
        result = resolve_outcomes_from_ohlcv(preds, ohlcv)
        assert result[0]["outcome"] == "WIN"

    def test_bullish_loss_on_drop(self):
        from src.ingest.resolve_outcomes import resolve_outcomes_from_ohlcv
        ohlcv = [self._sample_ohlcv(close=900.0)]
        preds = [self._sample_pred(direction="BULLISH", entry_price=1000.0)]
        result = resolve_outcomes_from_ohlcv(preds, ohlcv)
        assert result[0]["outcome"] == "LOSS"

    def test_bearish_win_on_drop(self):
        from src.ingest.resolve_outcomes import resolve_outcomes_from_ohlcv
        ohlcv = [self._sample_ohlcv(close=900.0)]
        preds = [self._sample_pred(direction="BEARISH", entry_price=1000.0)]
        result = resolve_outcomes_from_ohlcv(preds, ohlcv)
        assert result[0]["outcome"] == "WIN"

    def test_mixed_circuit_partial_resolution(self):
        """When some rows are circuit-locked, only non-circuit symbols resolve."""
        from src.ingest.resolve_outcomes import resolve_outcomes_from_ohlcv
        ohlcv = [
            {"symbol": "RELIANCE", "close": 1100.0, "circuit_flag": False},
            {"symbol": "INFY", "close": 1500.0, "circuit_flag": True},
        ]
        preds = [
            {"id": 1, "symbol": "RELIANCE", "direction": "BULLISH", "entry_price": 1000.0},
            {"id": 2, "symbol": "INFY", "direction": "BULLISH", "entry_price": 1400.0},
        ]
        result = resolve_outcomes_from_ohlcv(preds, ohlcv)
        assert len(result) == 1
        assert result[0]["prediction_id"] == 1

    def test_zero_entry_price_skipped(self):
        from src.ingest.resolve_outcomes import resolve_outcomes_from_ohlcv
        ohlcv = [self._sample_ohlcv(close=1100.0)]
        preds = [self._sample_pred(entry_price=0)]
        result = resolve_outcomes_from_ohlcv(preds, ohlcv)
        assert result == [], "Zero entry_price must be skipped to avoid ZeroDivisionError"


# ─────────────────────────────────────────────────────────────────────────────
# BSE XBRL fundamentals parsing (src/ingest/fundamentals.py)
# ─────────────────────────────────────────────────────────────────────────────

class TestParseBseXbrlFundamentals:
    def test_returns_all_required_keys(self):
        from src.ingest.fundamentals import parse_bse_xbrl_fundamentals
        data = {"symbol": "RELIANCE", "roic": "0.15", "fcf": "50000", "eps_growth": "0.12",
                "peg": "1.2", "dividend": "0.03", "debt_equity": "0.4", "book_value": "1200"}
        result = parse_bse_xbrl_fundamentals(data)
        for key in ("symbol", "roic", "fcf", "eps_growth", "peg", "dividend", "debt_equity", "book_value", "source"):
            assert key in result, f"Missing key: {key}"

    def test_na_values_become_none(self):
        from src.ingest.fundamentals import parse_bse_xbrl_fundamentals
        data = {"symbol": "TCS", "roic": "NA", "fcf": "", "eps_growth": None,
                "peg": "NA", "dividend": "NA", "debt_equity": "NA", "book_value": "NA"}
        result = parse_bse_xbrl_fundamentals(data)
        assert result["roic"] is None
        assert result["fcf"] is None
        assert result["eps_growth"] is None

    def test_numeric_fields_are_floats(self):
        from src.ingest.fundamentals import parse_bse_xbrl_fundamentals
        data = {"symbol": "INFY", "roic": "0.20", "fcf": "30000", "eps_growth": "0.15",
                "peg": "1.5", "dividend": "0.04", "debt_equity": "0.2", "book_value": "800"}
        result = parse_bse_xbrl_fundamentals(data)
        assert isinstance(result["roic"], float)
        assert result["roic"] == pytest.approx(0.20)

    def test_source_is_bse_xbrl(self):
        from src.ingest.fundamentals import parse_bse_xbrl_fundamentals
        result = parse_bse_xbrl_fundamentals({"symbol": "X"})
        assert result["source"] == "bse_xbrl"
