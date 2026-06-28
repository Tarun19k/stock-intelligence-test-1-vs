-- AlphaVeda Migration 0015: align ingest_status schema with ingest.py contract
--
-- Migration 0010 created: script_name, run_at, status CHECK ('OK','FAILED','PARTIAL')
-- ingest.py was written to:  source,       last_run, status IN (OK/NO_DATA/SKIPPED_HOLIDAY/ERROR)
-- This migration closes the gap. Run once in Supabase SQL Editor.

-- 1. Rename script_name → source
ALTER TABLE ingest_status RENAME COLUMN script_name TO source;

-- 2. Rename run_at → last_run
ALTER TABLE ingest_status RENAME COLUMN run_at TO last_run;

-- 3. Drop the old status constraint and replace with the full set
ALTER TABLE ingest_status DROP CONSTRAINT IF EXISTS ingest_status_status_check;
ALTER TABLE ingest_status ADD CONSTRAINT ingest_status_status_check
  CHECK (status IN ('OK', 'NO_DATA', 'SKIPPED_HOLIDAY', 'ERROR', 'FAILED', 'PARTIAL'));

-- 4. Rename error_msg → error to match ingest.py summary dict key
ALTER TABLE ingest_status RENAME COLUMN error_msg TO error;

-- Verify
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'ingest_status'
ORDER BY ordinal_position;
