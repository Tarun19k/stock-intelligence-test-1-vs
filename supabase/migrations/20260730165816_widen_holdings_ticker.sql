-- 20260730165816_widen_holdings_ticker.sql
-- Real bug found live: the initial ingest_holdings_from_pnl.py write failed
-- (HTTP 400, "value too long for type character varying(20)") because
-- fallback-generated tickers for unresolved ISINs (ETF/MF units, e.g. "MOTILAL
-- OS NASDAQ100 ETF") exceed 20 chars, while holdings_lots was already built
-- at VARCHAR(30). Widening holdings.ticker to match, so both tables are
-- consistent for the same real ticker values.

ALTER TABLE holdings ALTER COLUMN ticker TYPE VARCHAR(30);
