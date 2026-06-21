-- AlphaVeda Migration 0004: macro_regime
-- Time-series table: one row per date, UNIQUE on regime_date only.
-- regime column has CHECK constraint only — NO UNIQUE constraint.
-- Same regime value ('RISK_ON', etc.) repeats across many dates; UNIQUE would cap table at 4 rows.

CREATE TABLE IF NOT EXISTS macro_regime (
  id          SERIAL PRIMARY KEY,
  regime_date DATE NOT NULL UNIQUE,
  regime      VARCHAR(20) NOT NULL CHECK (
    regime IN ('RISK_ON','RISK_OFF','STAGFLATION','DEFLATION')
  ),
  rbi_rate    NUMERIC(4,2),
  usd_inr     NUMERIC(8,2),
  nifty_vix   NUMERIC(6,2),
  fii_flow_cr NUMERIC(12,2),            -- FII net monthly, crores
  notes       TEXT,
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
