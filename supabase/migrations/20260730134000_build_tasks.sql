-- 20260730134000_build_tasks.sql
-- Real backend for the build-verification checklist. Additive only.

CREATE TABLE IF NOT EXISTS build_tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('completed', 'in_progress', 'pending', 'blocked')),
    explanation TEXT NOT NULL,
    simplification TEXT NOT NULL,
    background_context TEXT NOT NULL,
    acceptance_criteria TEXT NOT NULL,
    test_result TEXT NOT NULL,
    test_status VARCHAR(20) NOT NULL CHECK (test_status IN ('pass', 'blocked', 'pending')),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE build_tasks ENABLE ROW LEVEL SECURITY;
-- No policies: all reads/writes go through the Next.js server (API route + server
-- component), which uses SUPABASE_SERVICE_KEY server-side only. No client-side
-- Supabase access to this table exists.
