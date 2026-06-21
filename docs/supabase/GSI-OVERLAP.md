# GSI-AlphaVeda Supabase State & Overlap Analysis

**Date:** 2026-06-21  
**Reviewed:** Agentic-ops manager.py + GSI migrations + no GSI Python client (yet)

---

## Current Supabase Projects

**SINGLE UNIFIED PROJECT:** All workspaces (agentic-ops, GSI, Crochet) share one Supabase instance.
- URL: `SUPABASE_URL` env var (same across repos)
- Auth: Service key in `SUPABASE_SERVICE_KEY` (same across repos)
- Manager: `agentic-operations/supabase/manager.py` (unified interface)

---

## Existing Tables (Agentic-ops migrations 001–005)

| Table | Purpose | Workspace | Rows |
|---|---|---|---|
| `profiles` | User auth extension | All | ~1 |
| `gsi_subscriptions` | GSI plan + payment | GSI | TBD |
| `gsi_alerts` | Stock alert prefs | GSI | TBD |
| `graph_metrics` | Graph health time-series | Agentic-ops | TBD |
| `pipeline_runs` | Daily news pipeline logs | Agentic-ops | TBD |
| `crochet_projects` | Project metadata | Crochet | TBD |
| `crochet_rows` | Row tracking | Crochet | TBD |
| `council_runs` | Council run history | Agentic-ops | TBD |
| `council_findings` | Findings lifecycle | Agentic-ops | TBD |

---

## AlphaVeda Tables (GSI migrations 001–006)

| Table | Purpose | Rows | Dependencies |
|---|---|---|---|
| `instruments` | Lynch classification | ~559 | — |
| `ohlcv` | Daily OHLCV (Bhavcopy) | ~2.5M | instruments |
| `fundamentals` | Q earnings + shareholding | ~2.2K | instruments |
| `macro_regime` | RBI/FII/VIX time-series | ~365 | — |
| `portfolio_buckets` | 4-bucket config | 4 (seeded) | — |
| `trade_outcomes` | Entry/exit tracking | TBD | instruments, portfolio_buckets |

---

## Naming Conflicts

**ZERO conflicts identified.** AlphaVeda tables (`instruments`, `ohlcv`, `fundamentals`, `macro_regime`, `portfolio_buckets`, `trade_outcomes`) do not overlap with existing agentic-ops/GSI names.

Missing from GSI migrations but mentioned in AlphaVeda spec:
- `accuracy_predictions` — not yet migrated
- `accuracy_outcomes` — not yet migrated
- `signal_weights` — not yet migrated
- `ingest_status` — not yet migrated
- `waitlist` — not yet migrated (separate from Gumroad?)

---

## Recommendation

**✓ Proceed with shared project.** No conflicts; cost-efficient; manager.py functions extend cleanly to support AlphaVeda reads/writes.

**Setup checklist:**
1. Ensure GHA secrets `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` are set (confirm in agentic-ops CI)
2. Apply GSI migrations 001–006 via `supabase db push` (if not already applied)
3. Wire manager.py functions for AlphaVeda CRUD:
   - `push_instruments()` — batch upsert
   - `push_ohlcv()` — batch append
   - `get_trade_outcomes()` — query for accuracy engine
4. Test cross-workspace auth: GSI user reading own trade outcomes vs agentic-ops service role writing metrics

---

## Graph Size Impact

AlphaVeda adds ~2.5M rows to `ohlcv` table. Storage ~15–20 GB (Postgres). Supabase free tier supports up to 1 GB; pro tier 8 GB. **Pro tier required** if full history included; consider archiving OHLCV to cold storage (S3) after 12+ months.
