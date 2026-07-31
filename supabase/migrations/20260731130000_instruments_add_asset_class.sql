-- AlphaVeda Migration: add instruments.asset_class ('equity' | 'etf')
--
-- Per OFFSET_HARVEST_YIELD_FOUNDATION.md's ETF inclusion roadmap (Sec 3): ETFs need no
-- ingestion-pipeline change (confirmed twice live -- 2026-07-30 and 2026-07-31 -- that
-- standard equity/gold/liquid-fund ETFs already trade under SERIES:EQ, already included
-- in bhavcopy.py's _VALID_SERIES). The real remaining gap is that `instruments` has no way
-- to distinguish an ETF from a company -- an ETF's "fundamentals" analog is NAV/tracking
-- index/expense ratio, not ROIC/debt-equity/promoter-pledge, and it has no Lynch
-- classification at all (no promoters, no earnings). Additive only -- existing 501 rows
-- default to 'equity' (all are real companies, confirmed via the Nifty 500 seed).

ALTER TABLE instruments ADD COLUMN IF NOT EXISTS asset_class VARCHAR(10) NOT NULL DEFAULT 'equity'
  CHECK (asset_class IN ('equity', 'etf'));
