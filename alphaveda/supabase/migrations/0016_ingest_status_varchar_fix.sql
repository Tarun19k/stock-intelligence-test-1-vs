-- AlphaVeda Migration 0016: widen ingest_status.status column
-- VARCHAR(10) is too narrow for 'SKIPPED_HOLIDAY' (15 chars).
-- Migration 0015 expanded the CHECK constraint but not the column width.

ALTER TABLE ingest_status ALTER COLUMN status TYPE VARCHAR(20);

-- Verify
SELECT column_name, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'ingest_status' AND column_name = 'status';
