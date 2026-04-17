"""Unit tests for DataManager M2 — CacheManager and DataContract.

Run: pytest tests/test_data_manager_m2.py -v
These tests are direct unit tests of the cache and validation layer.
They do NOT test Streamlit integration — that is covered by regression.py.
"""
import time
import pandas as pd
import pytest
from collections import OrderedDict

from data_manager import (
    CacheManager,
    DataContract,
    DataResult,
    DataType,
    ResultStatus,
    SourceTag,
    unavailable,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_ohlcv(n_rows: int = 30) -> pd.DataFrame:
    dates = pd.date_range("2026-01-01", periods=n_rows, freq="D")
    return pd.DataFrame(
        {"Open": 100.0, "High": 105.0, "Low": 95.0, "Close": 102.0, "Volume": 1_000_000},
        index=dates,
    )


def _make_result(
    ticker: str = "AAPL",
    data_type: DataType = DataType.OHLCV,
    status: ResultStatus = ResultStatus.FRESH,
    age_s: float = 0.0,
) -> DataResult:
    return DataResult(
        status=status,
        data=_make_ohlcv(),
        source=SourceTag.YAHOO,
        fetched_at=time.monotonic() - age_s,
        fetched_wall_time=time.time() - age_s,
        ticker=ticker,
        data_type=data_type,
    )


# ── CacheManager tests ────────────────────────────────────────────────────────

class TestCacheManagerMiss:
    def test_get_returns_none_on_empty_cache(self):
        cm = CacheManager()
        assert cm.get("AAPL", DataType.OHLCV) is None

    def test_get_returns_none_for_different_ticker(self):
        cm = CacheManager()
        cm.put(_make_result("AAPL"))
        assert cm.get("MSFT", DataType.OHLCV) is None

    def test_get_returns_none_for_different_data_type(self):
        cm = CacheManager()
        cm.put(_make_result("AAPL", DataType.OHLCV))
        assert cm.get("AAPL", DataType.INFO) is None


class TestCacheManagerHit:
    def test_put_and_get_returns_fresh_result(self):
        cm = CacheManager()
        result = _make_result("AAPL", DataType.OHLCV)
        cm.put(result)
        got = cm.get("AAPL", DataType.OHLCV)
        assert got is not None
        assert got.ticker == "AAPL"
        assert got.status == ResultStatus.FRESH

    def test_size_increments_on_put(self):
        cm = CacheManager()
        assert cm.size == 0
        cm.put(_make_result("AAPL"))
        assert cm.size == 1
        cm.put(_make_result("MSFT"))
        assert cm.size == 2

    def test_unavailable_not_stored(self):
        cm = CacheManager()
        cm.put(unavailable("AAPL", DataType.OHLCV, "test"))
        assert cm.size == 0
        assert cm.get("AAPL", DataType.OHLCV) is None

    def test_duplicate_put_does_not_grow_cache(self):
        cm = CacheManager()
        cm.put(_make_result("AAPL"))
        cm.put(_make_result("AAPL"))
        assert cm.size == 1


class TestCacheManagerTTL:
    def test_fresh_within_ttl(self):
        cm = CacheManager()
        cm.put(_make_result("AAPL", DataType.OHLCV, age_s=10))  # 10s < 300s TTL
        got = cm.get("AAPL", DataType.OHLCV)
        assert got is not None
        assert got.status == ResultStatus.FRESH

    def test_stale_past_ohlcv_ttl(self):
        cm = CacheManager()
        cm.put(_make_result("AAPL", DataType.OHLCV, age_s=400))  # 400s > 300s TTL
        got = cm.get("AAPL", DataType.OHLCV)
        assert got is not None
        assert got.status == ResultStatus.STALE

    def test_stale_past_live_ttl(self):
        cm = CacheManager()
        cm.put(_make_result("AAPL", DataType.LIVE, age_s=10))  # 10s > 5s LIVE TTL
        got = cm.get("AAPL", DataType.LIVE)
        assert got is not None
        assert got.status == ResultStatus.STALE

    def test_stale_entry_data_is_preserved(self):
        cm = CacheManager()
        cm.put(_make_result("AAPL", DataType.OHLCV, age_s=400))
        got = cm.get("AAPL", DataType.OHLCV)
        assert got.data is not None  # data preserved in stale result


class TestCacheManagerLRU:
    def test_lru_evicts_oldest_at_cap(self):
        cm = CacheManager()
        # Fill exactly to MAX_ENTRIES using distinct tickers
        for i in range(cm.MAX_ENTRIES):
            cm.put(_make_result(f"T{i:04d}", DataType.OHLCV))
        assert cm.size == cm.MAX_ENTRIES
        # Add one more — T0000 (inserted first, LRU) should be evicted
        cm.put(_make_result("ZNEW", DataType.OHLCV))
        assert cm.size == cm.MAX_ENTRIES
        assert cm.get("T0000", DataType.OHLCV) is None
        assert cm.get("ZNEW", DataType.OHLCV) is not None

    def test_recently_accessed_not_evicted(self):
        cm = CacheManager()
        for i in range(cm.MAX_ENTRIES):
            cm.put(_make_result(f"T{i:04d}", DataType.OHLCV))
        # Access T0000 to move it to MRU position
        cm.get("T0000", DataType.OHLCV)
        # Add one more — T0001 (now LRU) should be evicted instead
        cm.put(_make_result("ZNEW", DataType.OHLCV))
        assert cm.get("T0000", DataType.OHLCV) is not None  # survived
        assert cm.get("T0001", DataType.OHLCV) is None      # evicted


class TestCacheManagerInvalidate:
    def test_invalidate_removes_all_types_for_ticker(self):
        cm = CacheManager()
        cm.put(_make_result("AAPL", DataType.OHLCV))
        cm.put(_make_result("AAPL", DataType.INFO))
        cm.put(_make_result("MSFT", DataType.OHLCV))
        cm.invalidate("AAPL")
        assert cm.get("AAPL", DataType.OHLCV) is None
        assert cm.get("AAPL", DataType.INFO) is None
        assert cm.get("MSFT", DataType.OHLCV) is not None  # unaffected

    def test_invalidate_all_clears_everything(self):
        cm = CacheManager()
        cm.put(_make_result("AAPL"))
        cm.put(_make_result("MSFT", DataType.INFO))
        cm.invalidate_all()
        assert cm.size == 0


# ── DataContract tests ────────────────────────────────────────────────────────

class TestDataContractOHLCV:
    def test_valid_ohlcv(self):
        assert DataContract.validate(_make_ohlcv(), DataType.OHLCV, "AAPL") is None

    def test_not_dataframe(self):
        assert DataContract.validate({"Close": 100}, DataType.OHLCV, "AAPL") is not None

    def test_empty_dataframe(self):
        assert DataContract.validate(pd.DataFrame(), DataType.OHLCV, "AAPL") is not None

    def test_missing_close_column(self):
        df = _make_ohlcv().drop(columns=["Close"])
        assert DataContract.validate(df, DataType.OHLCV, "AAPL") is not None

    def test_missing_volume_column(self):
        df = _make_ohlcv().drop(columns=["Volume"])
        assert DataContract.validate(df, DataType.OHLCV, "AAPL") is not None

    def test_non_datetime_index(self):
        df = _make_ohlcv().reset_index(drop=True)
        assert DataContract.validate(df, DataType.OHLCV, "AAPL") is not None

    def test_non_numeric_close(self):
        df = _make_ohlcv()
        df["Close"] = "bad"
        assert DataContract.validate(df, DataType.OHLCV, "AAPL") is not None

    def test_intraday_same_as_ohlcv(self):
        # INTRADAY uses same shape checks as OHLCV
        assert DataContract.validate(_make_ohlcv(), DataType.INTRADAY, "AAPL") is None


class TestDataContractINFO:
    def test_valid_dict(self):
        assert DataContract.validate({"sector": "Tech", "marketCap": 3e12}, DataType.INFO, "AAPL") is None

    def test_not_dict(self):
        assert DataContract.validate("bad", DataType.INFO, "AAPL") is not None

    def test_empty_dict(self):
        assert DataContract.validate({}, DataType.INFO, "AAPL") is not None


class TestDataContractLIVE:
    def test_valid_positive_float(self):
        assert DataContract.validate(150.0, DataType.LIVE, "AAPL") is None

    def test_valid_positive_int(self):
        assert DataContract.validate(150, DataType.LIVE, "AAPL") is None

    def test_zero(self):
        assert DataContract.validate(0.0, DataType.LIVE, "AAPL") is not None

    def test_negative(self):
        assert DataContract.validate(-5.0, DataType.LIVE, "AAPL") is not None

    def test_string(self):
        assert DataContract.validate("150", DataType.LIVE, "AAPL") is not None

    def test_none(self):
        assert DataContract.validate(None, DataType.LIVE, "AAPL") is not None


class TestDataContractBATCH:
    def test_valid_batch(self):
        data = {"AAPL": _make_ohlcv(), "MSFT": _make_ohlcv()}
        assert DataContract.validate(data, DataType.BATCH, "BATCH") is None

    def test_not_dict(self):
        assert DataContract.validate(_make_ohlcv(), DataType.BATCH, "BATCH") is not None

    def test_empty_batch_is_valid(self):
        # Empty batch is structurally valid — callers handle missing keys
        assert DataContract.validate({}, DataType.BATCH, "BATCH") is None

    def test_inner_value_fails_ohlcv(self):
        data = {"AAPL": _make_ohlcv(), "BAD": pd.DataFrame()}
        assert DataContract.validate(data, DataType.BATCH, "BATCH") is not None
