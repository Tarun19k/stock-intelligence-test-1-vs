-- Migration 0017: add hit and return_pct columns to accuracy_outcomes
--
-- These columns were missing from the initial table creation.
-- Required by: ingest.py step 6 (batch upsert hit + return_pct)
--              emit_signal() in engine.py (hit_rate computation)
--              resolve_outcomes.py (writes hit boolean + return_pct float)
--
-- hit: TRUE = direction prediction was correct on next trading close
--      DEFAULT FALSE so existing rows (no resolved outcome yet) don't break
-- return_pct: signed return from entry price to resolution close; NULL until resolved
--
-- Apply: paste into Supabase Dashboard → SQL Editor, or `supabase db push`

ALTER TABLE accuracy_outcomes
    ADD COLUMN IF NOT EXISTS hit BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS return_pct NUMERIC(8, 4);
