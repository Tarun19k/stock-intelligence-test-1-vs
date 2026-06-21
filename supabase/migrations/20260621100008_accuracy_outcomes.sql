-- AlphaVeda Migration 0008: accuracy_outcomes
-- Resolved outcomes for each prediction after horizon_days expires.
-- peak_return_pct = maximum return during the horizon window (Druckenmiller condition).
-- After creating this table, the circular FK is resolved via ALTER TABLE on accuracy_predictions.

CREATE TABLE IF NOT EXISTS accuracy_outcomes (
  id               BIGSERIAL PRIMARY KEY,
  prediction_id    BIGINT NOT NULL REFERENCES accuracy_predictions(id),
  outcome_date     DATE NOT NULL,
  actual_direction VARCHAR(5) NOT NULL CHECK (actual_direction IN ('BULL','BEAR')),
  actual_return    NUMERIC(8,4),
  peak_return_pct  NUMERIC(8,4),          -- max return during horizon window
  is_correct       BOOLEAN NOT NULL,
  resolved_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Resolve circular FK: accuracy_predictions.outcome_id could not reference
-- accuracy_outcomes at 0007 run time because this table did not exist yet.
ALTER TABLE accuracy_predictions
  ADD COLUMN outcome_id BIGINT REFERENCES accuracy_outcomes(id);
