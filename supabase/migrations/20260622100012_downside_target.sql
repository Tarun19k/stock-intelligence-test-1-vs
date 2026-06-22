-- AlphaVeda Migration 0012: downside_target — Kelly loss-leg schema dependency
-- Source: R1 Red Team GAP-001 + R3 Council MA-2/MA-3.
-- accuracy_predictions.id is BIGSERIAL; this ALTER targets the correct live table.

-- GAP-001 fix: Kelly formula requires both win leg (magnitude_target) and loss leg (downside_target)
-- Without downside_target, b = magnitude_target / downside_target cannot be computed
-- Source rule: stop-loss fraction emitted by the signal; ATR-based default if signal does not emit one

ALTER TABLE accuracy_predictions
    ADD COLUMN IF NOT EXISTS downside_target NUMERIC(6,4)
        CHECK (downside_target > 0 AND downside_target <= 1.0);

COMMENT ON COLUMN accuracy_predictions.downside_target IS
    'Loss leg for Kelly formula: b = magnitude_target / downside_target. '
    'Source: signal-emitted stop-loss fraction, or ATR(14)/price as default. '
    'NULL = signal predates this column; Path page suppresses rupee amounts when NULL.';

-- Until downside_target is populated, Path page must not show rupee Kelly amounts
-- Enforced in path optimizer: if downside_target IS NULL, emit direction+confidence only

-- migration 0012: downside_target — Kelly loss-leg schema dependency
