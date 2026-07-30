-- 20260730165449_holdings_lots.sql
-- Real per-lot cost-basis detail, additive alongside holdings (aggregate view).
-- Populated from a real Groww P&L export (Trade Level "Unrealised trades" section) --
-- see alphaveda/scripts/ingest_holdings_from_pnl.py. Needed for Prereq 7's
-- grandfathering/holding-period-per-lot tax logic, which the aggregate holdings
-- table cannot support.

CREATE TABLE IF NOT EXISTS holdings_lots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(30) NOT NULL,
    isin VARCHAR(20),
    real_name TEXT NOT NULL,
    qty NUMERIC NOT NULL,
    buy_price NUMERIC NOT NULL,
    buy_date DATE NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'groww_pnl_export',
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE holdings_lots ENABLE ROW LEVEL SECURITY;
-- No policies added: reads/writes go through SUPABASE_SERVICE_KEY (server-side
-- only), which bypasses RLS by design -- same pattern as holdings/build_tasks.
