-- Migration 0014: unique constraint on accuracy_outcomes(prediction_id, resolved_at)
--
-- Required by: ingest.py step 6 batch upsert (on_conflict="prediction_id,resolved_at")
-- Prevents double-scoring when GHA cron + manual workflow_dispatch fire on the same date.
-- Run this migration before the first G0 seed (python3 scripts/ingest.py).
--
-- Apply via Supabase SQL editor or CLI:
--   supabase db push  (if using supabase CLI)
--   or paste into Supabase dashboard → SQL Editor

ALTER TABLE accuracy_outcomes
    ADD CONSTRAINT accuracy_outcomes_prediction_date_unique
    UNIQUE (prediction_id, resolved_at);
