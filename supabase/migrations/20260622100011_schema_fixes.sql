-- AlphaVeda Migration 0011: schema integrity + data provenance batch
-- Source: R1 Red Team (GAP-009, GAP-010, GAP-012, Imran idempotency finding) + R3 Council MA-1/MA-9.
-- Batched per R3 MA-9: all schema additions land in one pass, not four trickle migrations.
--
-- Reconciliation notes (R3 MA-7 — migrations are single source of truth):
--   * signal_weights has NO updated_at column (cols: proposed_at, approved_at, approved_by).
--     approve_signal_weight() therefore stamps approved_at, the semantically correct existing column.
--   * signal_weights.id is SERIAL (integer), NOT uuid. approve_signal_weight takes p_id INT.

-- ---------------------------------------------------------------------------
-- 1. GAP-009 fix — signal_weights partial unique index + atomic approval procedure
-- ---------------------------------------------------------------------------
-- The live UNIQUE (lynch_class, regime, signal_name, status) in migration 0009
-- includes status, so two ACTIVE rows per segment are physically permitted.
-- This breaks Guard 6 ("human approves exactly one weight"). Enforce one ACTIVE
-- per (lynch_class, regime, signal_name) via a partial unique index.

CREATE UNIQUE INDEX signal_weights_one_active_per_segment
    ON signal_weights (lynch_class, regime, signal_name)
    WHERE status = 'ACTIVE';

-- Helper: atomically demote prior ACTIVE to SUPERSEDED before promoting new ACTIVE.
-- NOTE: status CHECK in migration 0009 allows ('ACTIVE','PROPOSED','REJECTED') only.
-- 'SUPERSEDED' is added to the allowed set below so the demote step does not violate the CHECK.
ALTER TABLE signal_weights
    DROP CONSTRAINT IF EXISTS signal_weights_status_check;
ALTER TABLE signal_weights
    ADD CONSTRAINT signal_weights_status_check
    CHECK (status IN ('ACTIVE','PROPOSED','REJECTED','SUPERSEDED'));

CREATE OR REPLACE FUNCTION approve_signal_weight(p_id INT)
RETURNS VOID AS $$
BEGIN
    UPDATE signal_weights
    SET status = 'SUPERSEDED', approved_at = NOW()
    WHERE lynch_class = (SELECT lynch_class FROM signal_weights WHERE id = p_id)
      AND regime      = (SELECT regime      FROM signal_weights WHERE id = p_id)
      AND signal_name = (SELECT signal_name FROM signal_weights WHERE id = p_id)
      AND status = 'ACTIVE';

    UPDATE signal_weights
    SET status = 'ACTIVE', approved_by = 'tarun', approved_at = NOW()
    WHERE id = p_id AND status = 'PROPOSED';
END;
$$ LANGUAGE plpgsql;

-- ---------------------------------------------------------------------------
-- 2. Outcome idempotency fix (Imran's finding — PARTIAL re-run protection)
-- ---------------------------------------------------------------------------
-- Prevent double-write on re-run after a PARTIAL ingest.
ALTER TABLE accuracy_outcomes
    ADD CONSTRAINT accuracy_outcomes_prediction_unique UNIQUE (prediction_id);

-- ---------------------------------------------------------------------------
-- 3. GAP-010 pre-work — circuit flag + liquidity on ohlcv
-- ---------------------------------------------------------------------------
-- Circuit-locked prices should not be scored as real outcomes.
ALTER TABLE ohlcv
    ADD COLUMN IF NOT EXISTS circuit_flag  BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS deliverable_volume BIGINT;

COMMENT ON COLUMN ohlcv.circuit_flag IS 'TRUE when price is circuit-locked (open=high=low=close at band limit). Exclude from outcome scoring.';
COMMENT ON COLUMN ohlcv.deliverable_volume IS 'BSE deliverable quantity. NULL = not available. Used for liquidity floor check.';

-- ---------------------------------------------------------------------------
-- 4. GAP-012 pre-work — licence_class on ohlcv
-- ---------------------------------------------------------------------------
-- Track data provenance licence for commercial gate enforcement.
ALTER TABLE ohlcv
    ADD COLUMN IF NOT EXISTS licence_class TEXT CHECK (licence_class IN ('personal', 'commercial', 'open')) DEFAULT 'personal';

COMMENT ON COLUMN ohlcv.licence_class IS 'personal = yfinance/BSE personal use only. commercial = FMP licensed. open = Bhavcopy/BSE official.';

-- migration 0011: schema integrity + data provenance batch
