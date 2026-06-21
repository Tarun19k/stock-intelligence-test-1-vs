-- AlphaVeda Migration 0005: portfolio_buckets
-- 4-bucket portfolio structure seeded at G0.
-- horizon_days_max NULL = indefinite (long_term bucket).

CREATE TABLE IF NOT EXISTS portfolio_buckets (
  id               SERIAL PRIMARY KEY,
  bucket_name      VARCHAR(50) NOT NULL CHECK (
    bucket_name IN ('emergency','near_term','medium_term','long_term')
  ),
  target_value_inr NUMERIC(12,2) NOT NULL,
  horizon_days_min INT NOT NULL,
  horizon_days_max INT,                  -- NULL = indefinite (long_term)
  cash_floor_pct   NUMERIC(5,2) NOT NULL DEFAULT 10.0,
  max_position_pct NUMERIC(5,2) NOT NULL DEFAULT 10.0,
  sector_cap_pct   NUMERIC(5,2) NOT NULL DEFAULT 35.0
);

-- Seed once at G0 — all 4 buckets
INSERT INTO portfolio_buckets VALUES
  (1, 'emergency',   500000,    0,    90,   100.0,  0.0,  0.0),
  (2, 'near_term',   250000,   90,   365,    10.0, 10.0, 35.0),
  (3, 'medium_term', 500000,  365,  1825,    10.0, 10.0, 35.0),
  (4, 'long_term',   450000, 1825,  NULL,    10.0, 10.0, 35.0);
