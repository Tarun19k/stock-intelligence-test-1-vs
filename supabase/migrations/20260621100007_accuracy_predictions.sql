-- AlphaVeda Migration 0007: accuracy_predictions
-- Every signal emit writes one row here (no exceptions, no batching).
-- Council conditions: regime_tag (C12/Dalio), cycle_phase (C13/Marks), accuracy_streak_flag (Soros).
-- regime_tag uses CHECK only — NOT a FK to macro_regime (time-series, not a lookup table).
-- outcome_id is intentionally absent here — added in 0008 via ALTER TABLE to avoid circular FK.

CREATE TABLE IF NOT EXISTS accuracy_predictions (
  id                   BIGSERIAL PRIMARY KEY,
  instrument_id        INT NOT NULL REFERENCES instruments(id),
  emitted_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  direction            VARCHAR(5) NOT NULL CHECK (direction IN ('BULL','BEAR')),
  confidence           SMALLINT NOT NULL CHECK (confidence BETWEEN 0 AND 100),
  magnitude_target     NUMERIC(6,4),       -- expected return fraction
  horizon_days         INT NOT NULL,
  regime_tag           VARCHAR(20) NOT NULL CHECK (
    regime_tag IN ('RISK_ON','RISK_OFF','STAGFLATION','DEFLATION')
  ),
  lynch_class          VARCHAR(20) NOT NULL CHECK (
    lynch_class IN ('fast_grower','stalwart','slow_grower',
                    'cyclical','turnaround','asset_play')
  ),
  cycle_phase          VARCHAR(20) NOT NULL CHECK (
    cycle_phase IN ('early_bull','mid_bull','late_bull',
                    'early_bear','mid_bear','late_bear')
  ),
  accuracy_streak_flag BOOLEAN NOT NULL DEFAULT false
  -- outcome_id BIGINT added in migration 0008 via ALTER TABLE
  -- (accuracy_outcomes does not exist yet at 0007 run time — circular FK avoided)
);
