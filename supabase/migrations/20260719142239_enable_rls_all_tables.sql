-- 20260719142239_enable_rls_all_tables.sql
-- RECONSTRUCTED 2026-07-30: this version was recorded as applied in
-- supabase_migrations.schema_migrations with no corresponding file in either
-- local migration tree (root or alphaveda/) — found during a migration-tree
-- reconciliation diagnosis. All statements are idempotent (ENABLE ROW LEVEL
-- SECURITY is safe to re-run on an already-enabled table), so this file is
-- safe to apply even though the exact original statement list is not known
-- with certainty — reconstructed from the core tables that existed as of
-- this migration's real timestamp (2026-07-19).

ALTER TABLE instruments ENABLE ROW LEVEL SECURITY;
ALTER TABLE ohlcv ENABLE ROW LEVEL SECURITY;
ALTER TABLE fundamentals ENABLE ROW LEVEL SECURITY;
ALTER TABLE macro_regime ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_buckets ENABLE ROW LEVEL SECURITY;
ALTER TABLE trade_outcomes ENABLE ROW LEVEL SECURITY;
ALTER TABLE accuracy_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE accuracy_outcomes ENABLE ROW LEVEL SECURITY;
ALTER TABLE signal_weights ENABLE ROW LEVEL SECURITY;
ALTER TABLE ingest_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE waitlist ENABLE ROW LEVEL SECURITY;
