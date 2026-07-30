-- 20260720160741_backtest_engine_phase0_tables.sql
-- RECONSTRUCTED 2026-07-30 from live schema introspection — no file existed
-- for this previously-applied version in either local migration tree.
-- Also fixes a real gap found in the same diagnosis: RLS was never enabled
-- on either table (they were created after 20260719142239's blanket enable,
-- so they never got it) — this reconstruction includes it going forward.
--
-- Note: id columns on both tables have NO default (confirmed via
-- information_schema.columns.column_default = NULL) — not auto-incrementing.
-- Whatever process writes to these tables must supply id explicitly.
-- Reconstructed to match, not assumed as a standard serial/identity column.

CREATE TABLE IF NOT EXISTS bt_backtest_runs (
    id BIGINT PRIMARY KEY,
    run_at TIMESTAMPTZ,
    config_label TEXT,
    weights_config JSONB,
    data_depth_days INTEGER,
    insufficient_depth BOOLEAN,
    score NUMERIC,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS bt_backtest_attribution (
    id BIGINT PRIMARY KEY,
    backtest_run_id BIGINT,
    instrument_id BIGINT,
    trade_date DATE,
    signal_name TEXT,
    weight NUMERIC,
    threshold_crossed BOOLEAN,
    reason TEXT
);

ALTER TABLE bt_backtest_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE bt_backtest_attribution ENABLE ROW LEVEL SECURITY;
