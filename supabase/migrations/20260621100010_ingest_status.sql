-- AlphaVeda Migration 0010: ingest_status
-- Tracks each ingest script run; queried by data_viewer.py to surface staleness warnings.
-- data_viewer.py checks: if latest run_at < today 6 PM IST → show amber STALE badge.

CREATE TABLE IF NOT EXISTS ingest_status (
  id           SERIAL PRIMARY KEY,
  script_name  VARCHAR(100) NOT NULL,
  run_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  status       VARCHAR(10) NOT NULL CHECK (status IN ('OK','FAILED','PARTIAL')),
  error_msg    TEXT,
  rows_written INT
);
