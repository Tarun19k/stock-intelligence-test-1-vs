-- 20260730132148_holdings_ledger.sql
-- OHY portfolio ledger — additive only, no existing table touched.
-- Root cause this fixes: OHY UI screens (Portfolio Health, Trigger Explanation)
-- were built against portfolio data that had no schema to back it, confirmed
-- via two independent reviews this session (retail-UX council + Dronacharya
-- skill-gap audit) landing on the same finding.

CREATE TABLE IF NOT EXISTS holdings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(20) NOT NULL,
    qty NUMERIC NOT NULL,
    avg_cost NUMERIC NOT NULL,
    acquired_at DATE NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'manual',
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE holdings ENABLE ROW LEVEL SECURITY;
-- No policies added: reads/writes go through SUPABASE_SERVICE_KEY (server-side
-- only, per alphaveda/web/lib/supabase.ts), which bypasses RLS by design.
