-- AlphaVeda Migration 0001: instruments
-- Lynch classification is NOT NULL from Day 1 (council condition C7/Lynch)

CREATE TABLE IF NOT EXISTS instruments (
  id             SERIAL PRIMARY KEY,
  ticker         VARCHAR(20) NOT NULL UNIQUE,
  name           VARCHAR(200) NOT NULL,
  exchange       VARCHAR(10) NOT NULL CHECK (exchange IN ('NSE', 'BSE')),
  classification VARCHAR(20) NOT NULL CHECK (
    classification IN ('fast_grower','stalwart','slow_grower',
                       'cyclical','turnaround','asset_play')
  ),
  isin           CHAR(12),
  sector         VARCHAR(100),
  is_active      BOOLEAN NOT NULL DEFAULT true,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
