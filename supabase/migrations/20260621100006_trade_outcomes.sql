-- AlphaVeda Migration 0006: trade_outcomes
-- Tracks entry/exit trades per instrument per bucket.
-- exit_trigger populated on EXIT signals (E1-E4); NULL for HOLD/BUY rows.
-- return_pct and exit columns populated on exit only.

CREATE TABLE IF NOT EXISTS trade_outcomes (
  id             BIGSERIAL PRIMARY KEY,
  instrument_id  INT NOT NULL REFERENCES instruments(id),
  bucket_id      INT NOT NULL REFERENCES portfolio_buckets(id),
  entry_date     DATE NOT NULL,
  entry_price    NUMERIC(12,2) NOT NULL,
  exit_date      DATE,
  exit_price     NUMERIC(12,2),
  position_value NUMERIC(12,2) NOT NULL,
  return_pct     NUMERIC(8,4),          -- populated on exit
  notes          TEXT,
  exit_trigger   CHAR(2) CHECK (exit_trigger IN ('E1','E2','E3','E4'))
                                        -- E1: Kelly band drift | E2: signal reversal streak
                                        -- E3: insufficient edge | E4: sector cap breach
                                        -- NULL for HOLD/BUY positions
);
