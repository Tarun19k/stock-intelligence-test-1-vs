-- AlphaVeda Migration 0016: widen ingest_status.status column
-- VARCHAR(10) is too narrow for 'SKIPPED_HOLIDAY' (15 chars).
-- Migration 0015 expanded the CHECK constraint but not the column width.

ALTER TABLE ingest_status ALTER COLUMN status TYPE VARCHAR(20);

-- PARITY-CHECK: manual column width ingest_status.status widened to VARCHAR(20) —
--   column exists either way (migration 0015 created it), so a PostgREST select
--   cannot distinguish VARCHAR(10) from VARCHAR(20); a too-narrow column only fails
--   at insert time (e.g. writing 'SKIPPED_HOLIDAY'), not at select time. Verify
--   manually via Supabase SQL editor: SELECT character_maximum_length FROM
--   information_schema.columns WHERE table_name = 'ingest_status' AND column_name =
--   'status'; expect 20.

-- Verify
SELECT column_name, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'ingest_status' AND column_name = 'status';
