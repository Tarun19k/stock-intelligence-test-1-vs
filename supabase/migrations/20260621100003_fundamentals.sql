-- AlphaVeda Migration 0003: fundamentals
-- Quarterly fundamentals from BSE XBRL + Shareholding; unique per instrument+period

CREATE TABLE IF NOT EXISTS fundamentals (
  id                  BIGSERIAL PRIMARY KEY,
  instrument_id       INT NOT NULL REFERENCES instruments(id),
  period_end          DATE NOT NULL,           -- quarter-end date
  roic_pct            NUMERIC(8,2),
  fcf_cr              NUMERIC(12,2),           -- crores
  promoter_pledge_pct NUMERIC(5,2),
  debt_equity         NUMERIC(8,2),
  eps                 NUMERIC(10,2),
  revenue_cr          NUMERIC(12,2),
  source              VARCHAR(50) NOT NULL,
  ingested_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (instrument_id, period_end)
);
