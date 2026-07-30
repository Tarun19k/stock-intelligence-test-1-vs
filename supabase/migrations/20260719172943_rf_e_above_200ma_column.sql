-- 20260719172943_rf_e_above_200ma_column.sql
-- RECONSTRUCTED 2026-07-30 from live schema introspection (column confirmed
-- to actually exist via information_schema query) — no file existed for this
-- previously-applied version in either local migration tree.

ALTER TABLE macro_regime ADD COLUMN IF NOT EXISTS above_200ma BOOLEAN;
