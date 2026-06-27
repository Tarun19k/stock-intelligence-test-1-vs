"""Shared fixtures for AlphaVeda test suite."""
import os
import sys
import pytest

# Ensure alphaveda/ is on the path so imports resolve correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Load .env from workspace root (one level up from alphaveda/)
from dotenv import load_dotenv
_env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(_env_path, override=False)

# Must be set at module level — test_governance_integrity.py reads os.environ at
# import time (before any fixture runs). A session-scoped fixture fires too late.
os.environ.setdefault("GOVERNANCE_STRICT", "1")


@pytest.fixture(scope="session")
def supabase_client():
    """Live Supabase client — requires Phase 2 src/config.py + SUPABASE_URL in .env.
    Skips cleanly when src/config.py is not yet implemented (Phase 1 state).
    """
    try:
        from src.config import get_supabase_client
    except ImportError:
        pytest.skip("src/config.py not yet implemented — Phase 2 required")
    return get_supabase_client()


@pytest.fixture
def sample_ohlcv_rows():
    """15 OHLCV rows for ATR(14) tests. Values are realistic NSE prices."""
    rows = [
        {"high": 1010 + i, "low": 990 + i, "close": 1000 + i}
        for i in range(15)
    ]
    return rows


@pytest.fixture
def empty_ohlcv_rows():
    return []
