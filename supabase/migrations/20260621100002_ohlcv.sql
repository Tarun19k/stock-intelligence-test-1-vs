-- AlphaVeda Migration 0002: ohlcv
-- Daily OHLCV from Bhavcopy (NSE/BSE); unique per instrument+date

CREATE TABLE IF NOT EXISTS ohlcv (
  id            BIGSERIAL PRIMARY KEY,
  instrument_id INT NOT NULL REFERENCES instruments(id),
  trade_date    DATE NOT NULL,
  open          NUMERIC(12,2) NOT NULL,
  high          NUMERIC(12,2) NOT NULL,
  low           NUMERIC(12,2) NOT NULL,
  close         NUMERIC(12,2) NOT NULL,
  volume        BIGINT NOT NULL,
  source        VARCHAR(50) NOT NULL,   -- 'bhavcopy_nse' | 'bhavcopy_bse'
  ingested_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (instrument_id, trade_date)
);
