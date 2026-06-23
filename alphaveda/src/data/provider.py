"""DataProvider ABC — every OHLCV data source must subclass this.

CommercialLicenseError is raised by providers that require a commercial licence
(e.g. yfinance) when is_commercial() returns True.

licence_class must be set on every row written to ohlcv (Bhattacharya's requirement):
  'open'       — BSE/NSE Bhavcopy, freely redistributable
  'personal'   — yfinance, personal use only (blocked when commercial=True)
  'commercial' — FMP or equivalent, requires paid licence
"""
from __future__ import annotations
from abc import ABC, abstractmethod


class CommercialLicenseError(Exception):
    """Raised when accessing a personal-use-only source under a commercial licence."""
    pass


class DataProvider(ABC):
    @abstractmethod
    def fetch_ohlcv(self, instrument_id: int, as_of: str) -> list[dict]:
        """Return OHLCV rows. Each row must include licence_class."""
        pass

    @property
    @abstractmethod
    def licence_class(self) -> str:
        """'open' | 'personal' | 'commercial'."""
        pass
