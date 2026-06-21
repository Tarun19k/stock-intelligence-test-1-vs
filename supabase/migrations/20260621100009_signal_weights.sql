-- AlphaVeda Migration 0009: signal_weights
-- 24-segment weight ledger (Lynch class × macro regime × signal name).
-- PROPOSED rows are human-reviewed quarterly before becoming ACTIVE (Munger/Guard 6).
-- UNIQUE on (lynch_class, regime, signal_name, status) allows one PROPOSED + one ACTIVE per segment/signal.

CREATE TABLE IF NOT EXISTS signal_weights (
  id            SERIAL PRIMARY KEY,
  lynch_class   VARCHAR(20) NOT NULL,
  regime        VARCHAR(20) NOT NULL,
  signal_name   VARCHAR(50) NOT NULL,  -- e.g. 'roic', 'momentum_rsi', 'peg'
  weight        NUMERIC(5,4) NOT NULL,
  status        VARCHAR(10) NOT NULL CHECK (status IN ('ACTIVE','PROPOSED','REJECTED')),
  proposed_at   TIMESTAMPTZ,
  approved_at   TIMESTAMPTZ,
  approved_by   TEXT,                  -- 'tarun' when human-approved
  observation_n INT,                   -- how many outcomes drove this proposal
  UNIQUE (lynch_class, regime, signal_name, status)
);
