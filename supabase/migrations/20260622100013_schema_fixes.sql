-- AlphaVeda Migration 0013: schema integrity + data provenance batch
-- v0.5 corrective pass: pre-index cleanup + idempotency guards + transaction wrapper
-- Renamed from 0011 to 0013 (ordinal collision with 20260621100011_waitlist.sql resolved).
-- Sources: R1 GAP-009/010/012, R3 MA-1/MA-9, pre-R4 council C-1/R-01/R-05/R-06.

BEGIN;

-- ── 1. GAP-009: CLEANUP before index ──────────────────────────────────────
-- The live UNIQUE (lynch_class, regime, signal_name, status) may have already
-- permitted two ACTIVE rows per segment. CREATE UNIQUE INDEX aborts if the
-- constraint is already violated. Demote all-but-latest ACTIVE per segment
-- to SUPERSEDED so the index can be created cleanly.

-- Extend status CHECK to allow SUPERSEDED before touching any rows.
ALTER TABLE signal_weights
    DROP CONSTRAINT IF EXISTS signal_weights_status_check;
ALTER TABLE signal_weights
    ADD CONSTRAINT signal_weights_status_check
    CHECK (status IN ('ACTIVE','PROPOSED','REJECTED','SUPERSEDED'));

-- Demote stale duplicates: for each (lynch_class, regime, signal_name),
-- keep the most recent ACTIVE (highest id), set the rest to SUPERSEDED.
UPDATE signal_weights sw
SET    status     = 'SUPERSEDED',
       approved_at = NOW()
WHERE  status = 'ACTIVE'
AND    id NOT IN (
    SELECT MAX(id)
    FROM   signal_weights
    WHERE  status = 'ACTIVE'
    GROUP  BY lynch_class, regime, signal_name
);

-- Now create the partial index safely.
CREATE UNIQUE INDEX IF NOT EXISTS signal_weights_one_active_per_segment
    ON signal_weights (lynch_class, regime, signal_name)
    WHERE status = 'ACTIVE';

-- ── 2. GAP-009: atomic approve helper ─────────────────────────────────────
-- Demotes prior ACTIVE → SUPERSEDED, then promotes the PROPOSED row → ACTIVE.
-- PROPOSED-guard: raises if p_id is not in PROPOSED status (prevents demoting
-- an ACTIVE with nothing to replace it).

CREATE OR REPLACE FUNCTION approve_signal_weight(p_id INT)
RETURNS VOID AS $$
BEGIN
    -- Guard: only promote rows that are currently PROPOSED.
    IF NOT EXISTS (
        SELECT 1 FROM signal_weights WHERE id = p_id AND status = 'PROPOSED'
    ) THEN
        RAISE EXCEPTION 'approve_signal_weight: id % is not in PROPOSED status', p_id;
    END IF;

    -- Demote prior ACTIVE for this segment.
    UPDATE signal_weights
    SET    status      = 'SUPERSEDED',
           approved_at = NOW()
    WHERE  lynch_class = (SELECT lynch_class FROM signal_weights WHERE id = p_id)
    AND    regime      = (SELECT regime      FROM signal_weights WHERE id = p_id)
    AND    signal_name = (SELECT signal_name FROM signal_weights WHERE id = p_id)
    AND    status = 'ACTIVE';

    -- Promote the PROPOSED row.
    UPDATE signal_weights
    SET    status      = 'ACTIVE',
           approved_by = 'tarun',
           approved_at = NOW()
    WHERE  id = p_id;
END;
$$ LANGUAGE plpgsql;

-- ── 3. Outcome idempotency (Imran) ────────────────────────────────────────
-- Prevent double-write on re-run after PARTIAL ingest.
-- DO-block guard makes this idempotent on re-run.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE  conname = 'accuracy_outcomes_prediction_unique'
        AND    conrelid = 'accuracy_outcomes'::regclass
    ) THEN
        ALTER TABLE accuracy_outcomes
            ADD CONSTRAINT accuracy_outcomes_prediction_unique
            UNIQUE (prediction_id);
    END IF;
END;
$$;

-- ── 4. GAP-010 pre-work: circuit flag + liquidity on ohlcv ────────────────
ALTER TABLE ohlcv
    ADD COLUMN IF NOT EXISTS circuit_flag       BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS deliverable_volume BIGINT;

COMMENT ON COLUMN ohlcv.circuit_flag        IS 'TRUE when price is circuit-locked. Exclude from outcome scoring until GAP-010 enforcement ships at G1.';
COMMENT ON COLUMN ohlcv.deliverable_volume  IS 'BSE deliverable quantity. NULL = not available. Liquidity floor check at G1.';

-- ── 5. GAP-012 pre-work: licence_class on ohlcv ──────────────────────────
ALTER TABLE ohlcv
    ADD COLUMN IF NOT EXISTS licence_class TEXT
        CHECK (licence_class IN ('personal','commercial','open'))
        DEFAULT 'personal';

COMMENT ON COLUMN ohlcv.licence_class IS 'personal=yfinance/BSE personal use only. commercial=FMP licensed. open=Bhavcopy/BSE official.';

COMMIT;

-- migration 0013: schema integrity + data provenance batch (v0.5 corrective)
