# AlphaVeda — Supabase Schema Reference

**Source:** `docs/superpowers/specs/2026-06-21-alphaveda-mvp-design.md` (Section 2)
**Supabase project:** alphaveda-prod (ap-south-1, free tier)
**Last updated:** 2026-06-21
**Tables:** 11 (9 migrations + waitlist + ingest_status)

---

## 1. Entity Relationship Diagram

```
┌─────────────────────────┐
│       instruments        │
│ * id (SERIAL)           │
│   ticker                │
│   classification        │
│   exchange              │
│   isin, sector          │
│   is_active             │
└──────────┬──────────────┘
           │
     ┌─────┴──────┬──────────────┬──────────────────┐
     ▼            ▼              ▼                  ▼
┌─────────┐  ┌────────────┐  ┌──────────────┐  ┌─────────────────────┐
│  ohlcv  │  │fundamentals│  │trade_outcomes│  │accuracy_predictions  │
│* id     │  │* id        │  │* id          │  │* id                  │
│instrument│  │instrument  │  │instrument_id │  │  instrument_id       │
│_id →    │  │_id →       │  │  → instr.    │  │  → instruments       │
│ instr.  │  │ instr.     │  │  bucket_id   │  │  emitted_at          │
│trade_   │  │period_end  │  │  → buckets   │  │  direction           │
│date     │  │roic_pct    │  │  entry_date  │  │  confidence          │
│open/    │  │fcf_cr      │  │  entry_price │  │  regime_tag          │
│high/    │  │promoter_   │  │  exit_date   │  │  lynch_class         │
│low/     │  │pledge_pct  │  │  exit_trigger│  │  cycle_phase         │
│close    │  │source      │  │  return_pct  │  │  accuracy_streak_flag│
│volume   │  └────────────┘  └──────┬───────┘  │  horizon_days        │
│source   │                         │           │  outcome_id ──────┐  │
└─────────┘                         │           └──────────┬────────┘  │
                                    │                      │           │
                              ┌─────┴──────┐              │           │
                              │portfolio_  │              │           │
                              │buckets     │              │           │
                              │* id        │              ▼           │
                              │bucket_name │   ┌──────────────────┐  │
                              │target_value│   │accuracy_outcomes │  │
                              │horizon_days│   │* id              │  │
                              │cash_floor  │   │  prediction_id → │  │
                              │max_position│   │    acc_pred.id   │  │
                              │sector_cap  │   │  outcome_date    │  │
                              └────────────┘   │  actual_direction│  │
                                               │  actual_return   │  │
                                               │  peak_return_pct │  │
                                               │  is_correct      │  │
                                               └──────────────────┘  │
                                                         ▲           │
                                                         └───────────┘
                                               (outcome_id added via
                                               ALTER TABLE in 0008 —
                                               circular FK resolved)

┌────────────────────────────────────────┐
│              signal_weights            │
│ * id                                   │
│   lynch_class                          │
│   regime                               │
│   signal_name                          │
│   weight                               │
│   status  (ACTIVE | PROPOSED | REJECTED│
│   observation_n                        │
│   approved_by                          │
└────────────────────────────────────────┘
  (no FK — standalone weights registry)

┌──────────────────────────────────┐
│           macro_regime           │
│ * id                             │
│   regime_date (UNIQUE)           │
│   regime  (RISK_ON/OFF/...)      │
│   rbi_rate, usd_inr, nifty_vix  │
│   fii_flow_cr                    │
└──────────────────────────────────┘
  (no FK into other tables — time-series;
   accuracy_predictions uses CHECK not FK
   to validate regime_tag values)

┌────────────────────────────────┐        ┌─────────────────────────────┐
│         ingest_status          │        │           waitlist           │
│ * id                           │        │ * id                         │
│   script_name                  │        │   email (UNIQUE)             │
│   run_at                       │        │   name                       │
│   status (OK|FAILED|PARTIAL)   │        │   signed_up_at               │
│   rows_written                 │        │   price_feedback             │
│   error_msg                    │        │   referred_by                │
└────────────────────────────────┘        │   converted_at               │
  (no FK — operational log)              └─────────────────────────────┘
                                            (no FK — standalone)
```

**FK arrow legend:** `→` points from the FK column to the referenced PK. `* id` = primary key.

---

## 2. Table Reference

### 2.1 instruments

**Purpose:** Master list of tradeable instruments (NSE/BSE equities); source of truth for all FK lookups.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | SERIAL | PRIMARY KEY | Auto-increment |
| ticker | VARCHAR(20) | NOT NULL, UNIQUE | NSE/BSE symbol |
| name | VARCHAR(200) | NOT NULL | Company name |
| exchange | VARCHAR(10) | NOT NULL, CHECK (NSE, BSE) | Listing exchange |
| classification | VARCHAR(20) | NOT NULL, CHECK (6 values) | Lynch class; NOT NULL from Day 1 per C7 |
| isin | CHAR(12) | nullable | International identifier |
| sector | VARCHAR(100) | nullable | BSE sector string |
| is_active | BOOLEAN | NOT NULL DEFAULT true | Soft-delete flag |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT now() | Insert timestamp |

**Notable constraints:**
- UNIQUE (ticker)
- CHECK classification IN ('fast_grower','stalwart','slow_grower','cyclical','turnaround','asset_play')
- CHECK exchange IN ('NSE','BSE')

**Row volume:**
- G0: ~50 seeded instruments (Nifty 50 subset)
- G1: ~200–500 instruments (broader BSE coverage)
- Steady state: ~2,000 (all Bhavcopy instruments)

---

### 2.2 ohlcv

**Purpose:** Daily OHLCV price history sourced from Bhavcopy (NSE and BSE); primary data for chart rendering and return calculation.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | BIGSERIAL | PRIMARY KEY | Large auto-increment (high volume) |
| instrument_id | INT | NOT NULL, FK → instruments(id) | Many rows per instrument |
| trade_date | DATE | NOT NULL | Trading session date |
| open | NUMERIC(12,2) | NOT NULL | Opening price (INR) |
| high | NUMERIC(12,2) | NOT NULL | Intraday high |
| low | NUMERIC(12,2) | NOT NULL | Intraday low |
| close | NUMERIC(12,2) | NOT NULL | Closing price (INR) |
| volume | BIGINT | NOT NULL | Shares traded |
| source | VARCHAR(50) | NOT NULL | 'bhavcopy_nse' or 'bhavcopy_bse' |
| ingested_at | TIMESTAMPTZ | NOT NULL DEFAULT now() | Ingest timestamp |

**Notable constraints:**
- UNIQUE (instrument_id, trade_date) — prevents duplicate ingest of same day
- FK: instrument_id → instruments(id)

**Row volume:**
- G0: ~50 instruments × ~250 trading days = ~12,500 rows
- G1: ~500 × 500 = ~250,000 rows
- Steady state: ~2,000 instruments × 3,000 days = ~6M rows

---

### 2.3 fundamentals

**Purpose:** Quarterly fundamental data per instrument sourced from BSE XBRL filings; drives Buffett/Lynch signal weights.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | BIGSERIAL | PRIMARY KEY | |
| instrument_id | INT | NOT NULL, FK → instruments(id) | |
| period_end | DATE | NOT NULL | Quarter-end date (e.g. 2026-03-31) |
| roic_pct | NUMERIC(8,2) | nullable | Return on invested capital % |
| fcf_cr | NUMERIC(12,2) | nullable | Free cash flow in crores |
| promoter_pledge_pct | NUMERIC(5,2) | nullable | % of promoter shares pledged |
| debt_equity | NUMERIC(8,2) | nullable | D/E ratio |
| eps | NUMERIC(10,2) | nullable | Earnings per share |
| revenue_cr | NUMERIC(12,2) | nullable | Revenue in crores |
| source | VARCHAR(50) | NOT NULL | 'bse_xbrl' or 'bse_shareholding' |
| ingested_at | TIMESTAMPTZ | NOT NULL DEFAULT now() | |

**Notable constraints:**
- UNIQUE (instrument_id, period_end) — one row per instrument per quarter
- FK: instrument_id → instruments(id)

**Row volume:**
- G0: ~50 instruments × 4 quarters = ~200 rows
- Steady state: ~2,000 instruments × 20 quarters = ~40,000 rows

---

### 2.4 macro_regime

**Purpose:** Daily macro regime tag (Dalio 4-regime model) with supporting indicators; read by signal engine to tag every prediction.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | SERIAL | PRIMARY KEY | |
| regime_date | DATE | NOT NULL, UNIQUE | One row per date |
| regime | VARCHAR(20) | NOT NULL, CHECK (4 values) | Current regime classification |
| rbi_rate | NUMERIC(4,2) | nullable | RBI repo rate % |
| usd_inr | NUMERIC(8,2) | nullable | Exchange rate |
| nifty_vix | NUMERIC(6,2) | nullable | India VIX level |
| fii_flow_cr | NUMERIC(12,2) | nullable | FII net monthly flow (crores) |
| notes | TEXT | nullable | Manual context from Tarun |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT now() | Last update time |

**Notable constraints:**
- UNIQUE (regime_date)
- CHECK regime IN ('RISK_ON','RISK_OFF','STAGFLATION','DEFLATION')
- Not referenced by FK from accuracy_predictions — regime_tag uses a CHECK constraint instead to avoid joining a time-series table on every signal read

**Row volume:**
- G0: ~12 rows (monthly cadence)
- Steady state: ~250 rows/year (daily updates if available, monthly in practice)

---

### 2.5 portfolio_buckets

**Purpose:** Defines the 4 portfolio buckets with their sizing rules; seeded once at G0, rarely modified.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | SERIAL | PRIMARY KEY | Fixed: 1–4 |
| bucket_name | VARCHAR(50) | NOT NULL, CHECK (4 values) | Bucket identifier |
| target_value_inr | NUMERIC(12,2) | NOT NULL | Target corpus in INR |
| horizon_days_min | INT | NOT NULL | Minimum hold horizon |
| horizon_days_max | INT | nullable | NULL = indefinite (long_term) |
| cash_floor_pct | NUMERIC(5,2) | NOT NULL DEFAULT 10.0 | Minimum cash % |
| max_position_pct | NUMERIC(5,2) | NOT NULL DEFAULT 10.0 | Max single position % |
| sector_cap_pct | NUMERIC(5,2) | NOT NULL DEFAULT 35.0 | Max sector allocation % |

**Notable constraints:**
- CHECK bucket_name IN ('emergency','near_term','medium_term','long_term')
- 4 rows seeded at G0 via INSERT in migration 0005; no ongoing writes expected

**Row volume:** 4 rows at G0; static.

---

### 2.6 trade_outcomes

**Purpose:** Logs actual entry and exit trades per instrument per bucket; captures EXIT trigger reason (E1–E4).

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | BIGSERIAL | PRIMARY KEY | |
| instrument_id | INT | NOT NULL, FK → instruments(id) | |
| bucket_id | INT | NOT NULL, FK → portfolio_buckets(id) | Which bucket holds this position |
| entry_date | DATE | NOT NULL | Position open date |
| entry_price | NUMERIC(12,2) | NOT NULL | Entry price (INR) |
| exit_date | DATE | nullable | NULL = position still open |
| exit_price | NUMERIC(12,2) | nullable | NULL = position still open |
| position_value | NUMERIC(12,2) | NOT NULL | Position size at entry (INR) |
| return_pct | NUMERIC(8,4) | nullable | Populated on exit |
| notes | TEXT | nullable | Free-form context |
| exit_trigger | CHAR(2) | nullable, CHECK (E1–E4) | Why position was exited |

**Notable constraints:**
- FK: instrument_id → instruments(id)
- FK: bucket_id → portfolio_buckets(id)
- CHECK exit_trigger IN ('E1','E2','E3','E4')
- exit_trigger NULL is valid for open or HOLD/BUY positions

**Row volume:**
- G0: ~10–20 rows (manual test entries)
- Steady state: one row per trade; hundreds over multiple years of use

---

### 2.7 accuracy_predictions

**Purpose:** Log of every signal emitted by the signal engine; the source table for the 24-segment accuracy ledger. Written synchronously on every signal emit.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | BIGSERIAL | PRIMARY KEY | |
| instrument_id | INT | NOT NULL, FK → instruments(id) | |
| emitted_at | TIMESTAMPTZ | NOT NULL DEFAULT now() | Signal emit time |
| direction | VARCHAR(5) | NOT NULL, CHECK (BULL, BEAR) | Predicted direction |
| confidence | SMALLINT | NOT NULL, CHECK 0–100 | Composite confidence score |
| magnitude_target | NUMERIC(6,4) | nullable | Expected return fraction |
| horizon_days | INT | NOT NULL | Prediction window (30/60/90) |
| regime_tag | VARCHAR(20) | NOT NULL, CHECK (4 values) | Dalio regime at emit time (Dalio council condition C12) |
| lynch_class | VARCHAR(20) | NOT NULL, CHECK (6 values) | Instrument Lynch class (Lynch council condition C13) |
| cycle_phase | VARCHAR(20) | NOT NULL, CHECK (6 values) | Market cycle phase at emit (Marks condition C13) |
| accuracy_streak_flag | BOOLEAN | NOT NULL DEFAULT false | True if last 5 predictions in segment were correct (Soros condition) |
| outcome_id | BIGINT | nullable, FK → accuracy_outcomes(id) | Added via ALTER TABLE in 0008; NULL until outcome resolved |

**Notable constraints:**
- FK: instrument_id → instruments(id)
- FK: outcome_id → accuracy_outcomes(id) — added in migration 0008, not at table creation
- CHECK regime_tag IN ('RISK_ON','RISK_OFF','STAGFLATION','DEFLATION')
- CHECK lynch_class IN ('fast_grower','stalwart','slow_grower','cyclical','turnaround','asset_play')
- CHECK cycle_phase IN ('early_bull','mid_bull','late_bull','early_bear','mid_bear','late_bear')
- CHECK direction IN ('BULL','BEAR')
- CHECK confidence BETWEEN 0 AND 100

**Row volume:**
- G0: ~0–50 rows (smoke test signals)
- G1: ~1,000–5,000 rows (months of daily signals)
- Steady state: grows indefinitely; ~50 instruments × 250 trading days/year = ~12,500 rows/year

---

### 2.8 accuracy_outcomes

**Purpose:** Records resolved outcomes for each prediction; populated by the daily GHA resolve_outcomes.py job after the prediction horizon expires.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | BIGSERIAL | PRIMARY KEY | |
| prediction_id | BIGINT | NOT NULL, FK → accuracy_predictions(id) | One outcome per prediction |
| outcome_date | DATE | NOT NULL | Date outcome was resolved |
| actual_direction | VARCHAR(5) | NOT NULL, CHECK (BULL, BEAR) | Observed market direction |
| actual_return | NUMERIC(8,4) | nullable | Actual return over horizon |
| peak_return_pct | NUMERIC(8,4) | nullable | Max return during horizon window (Druckenmiller condition) |
| is_correct | BOOLEAN | NOT NULL | Direction matched prediction |
| resolved_at | TIMESTAMPTZ | NOT NULL DEFAULT now() | Resolution timestamp |

**Notable constraints:**
- FK: prediction_id → accuracy_predictions(id)
- CHECK actual_direction IN ('BULL','BEAR')
- One row per prediction (accuracy_predictions.outcome_id back-fills after this row is created)

**Row volume:** Same as accuracy_predictions — one outcome row per resolved prediction.

---

### 2.9 signal_weights

**Purpose:** Stores per-segment signal weights; ACTIVE rows are read by the signal engine; PROPOSED rows await quarterly human review; REJECTED rows are archived.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | SERIAL | PRIMARY KEY | |
| lynch_class | VARCHAR(20) | NOT NULL | One of 6 Lynch classes |
| regime | VARCHAR(20) | NOT NULL | One of 4 Dalio regimes |
| signal_name | VARCHAR(50) | NOT NULL | e.g. 'roic', 'momentum_rsi', 'peg' |
| weight | NUMERIC(5,4) | NOT NULL | Signal weight value (0.0–1.0) |
| status | VARCHAR(10) | NOT NULL, CHECK (3 values) | ACTIVE, PROPOSED, or REJECTED |
| proposed_at | TIMESTAMPTZ | nullable | When proposal was generated |
| approved_at | TIMESTAMPTZ | nullable | When Tarun approved |
| approved_by | TEXT | nullable | 'tarun' when human-approved |
| observation_n | INT | nullable | Observation count driving the proposal |

**Notable constraints:**
- UNIQUE (lynch_class, regime, signal_name, status)
- CHECK status IN ('ACTIVE','PROPOSED','REJECTED')
- Table is empty at G0 — signal engine falls back to COLD_START_WEIGHTS constants
- FUNDAMENTAL_WEIGHT_FLOOR (0.30) is enforced in application code, not a DB constraint

**Row volume:**
- G0: 0 rows (cold-start from constants)
- G1+: grows as segments accumulate 30+ observations; max ~24 segments × N signals per segment

---

### 2.10 ingest_status

**Purpose:** Operational log of every ingest script run; queried by the data viewer to surface staleness and failure badges.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | SERIAL | PRIMARY KEY | |
| script_name | VARCHAR(100) | NOT NULL | e.g. 'ingest_bhavcopy', 'resolve_outcomes' |
| run_at | TIMESTAMPTZ | NOT NULL DEFAULT now() | When the run started |
| status | VARCHAR(10) | NOT NULL, CHECK (3 values) | OK, FAILED, or PARTIAL |
| error_msg | TEXT | nullable | Error detail on FAILED |
| rows_written | INT | nullable | Row count written on OK/PARTIAL |

**Notable constraints:**
- CHECK status IN ('OK','FAILED','PARTIAL')
- No UNIQUE constraint — append-only log; each run adds a new row
- Queries always use ORDER BY run_at DESC LIMIT 1 per script_name to get latest status

**Row volume:**
- ~5 scripts × 250 trading days/year = ~1,250 rows/year
- Free-tier strategy: old rows purged after 90 days via GHA maintenance job (keeps table under ~375 rows)

---

### 2.11 waitlist

**Purpose:** Captures early subscriber interest with price feedback and referral source for commercial intelligence (Gap 10).

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | SERIAL | PRIMARY KEY | |
| email | VARCHAR(200) | NOT NULL, UNIQUE | Subscriber email |
| name | VARCHAR(200) | nullable | Optional display name |
| signed_up_at | TIMESTAMPTZ | NOT NULL DEFAULT now() | Signup timestamp |
| price_feedback | VARCHAR(20) | nullable, CHECK (3 values) | 'too_high', 'fair', or 'too_low' |
| referred_by | VARCHAR(200) | nullable | Referral source or code |
| converted_at | TIMESTAMPTZ | nullable | Set when subscriber activates |

**Notable constraints:**
- UNIQUE (email)
- CHECK price_feedback IN ('too_high','fair','too_low')
- No FK relationships — standalone commercial table

**Row volume:** Low volume throughout all stages; expected <500 rows at steady state.

---

## 3. FK Relationship Map

All FK relationships in the schema, listed flat:

| Relationship | Type | Notes |
|---|---|---|
| `ohlcv.instrument_id → instruments.id` | Many-to-one | Many daily price rows per instrument |
| `fundamentals.instrument_id → instruments.id` | Many-to-one | Many quarterly rows per instrument |
| `trade_outcomes.instrument_id → instruments.id` | Many-to-one | Many trade rows per instrument |
| `trade_outcomes.bucket_id → portfolio_buckets.id` | Many-to-one | Many trades per bucket |
| `accuracy_predictions.instrument_id → instruments.id` | Many-to-one | Many prediction rows per instrument |
| `accuracy_outcomes.prediction_id → accuracy_predictions.id` | One-to-one | Exactly one outcome per prediction |
| `accuracy_predictions.outcome_id → accuracy_outcomes.id` | One-to-one (back-ref) | Nullable; added via ALTER TABLE in migration 0008 — circular FK resolved this way |

**Special case — circular FK:**
`accuracy_predictions.outcome_id` references `accuracy_outcomes.id`, but `accuracy_predictions` is created in migration 0007 and `accuracy_outcomes` does not exist until migration 0008. The column cannot be added at table creation. Migration 0008 resolves this with:

```sql
-- At end of 0008_accuracy_outcomes.sql, after CREATE TABLE accuracy_outcomes:
ALTER TABLE accuracy_predictions
  ADD COLUMN outcome_id BIGINT REFERENCES accuracy_outcomes(id);
```

This means the FK is deferred — `outcome_id` is NULL at prediction insert time and is back-filled by `resolve_outcomes.py` after the outcome row is created.

**Tables with no FK relationships:**
- `macro_regime` — standalone time-series; regime_tag in accuracy_predictions validated via CHECK, not FK
- `signal_weights` — standalone weights registry; lynch_class and regime validated via application code
- `ingest_status` — append-only operational log
- `waitlist` — standalone commercial table

---

## 4. Migration Ordering Rationale

Migrations **must run in 0001 → 0011 order**. Running out of order will fail with `relation does not exist` errors or leave the schema in an inconsistent state.

### Why 0001 must run first

`instruments` is the root reference table. Five tables declare FK constraints into `instruments.id`:
- `ohlcv` (0002)
- `fundamentals` (0003)
- `trade_outcomes` (0006)
- `accuracy_predictions` (0007)

If any of these migrations run before 0001, PostgreSQL will reject the `REFERENCES instruments(id)` clause because the target table does not yet exist.

### Why 0002 and 0003 depend on 0001

`ohlcv` and `fundamentals` both declare `instrument_id INT NOT NULL REFERENCES instruments(id)`. The FK is validated at DDL execution time (not deferred). 0001 must exist before either can be created.

### Why 0006 depends on 0001 and 0005

`trade_outcomes` has two FK constraints: `instrument_id → instruments(id)` (0001) and `bucket_id → portfolio_buckets(id)` (0005). Both target tables must exist before 0006 runs. This creates a hard ordering: 0001 → 0005 → 0006.

### Why 0007 depends on 0001

`accuracy_predictions` declares `instrument_id INT NOT NULL REFERENCES instruments(id)`. Same rule as 0002/0003 — instruments must exist first.

### Why 0007 must run before 0008

This is the circular FK case. `accuracy_outcomes` (0008) declares `prediction_id BIGINT NOT NULL REFERENCES accuracy_predictions(id)`. If 0008 runs before 0007, that FK reference fails because `accuracy_predictions` does not exist yet.

Additionally, the tail of 0008 (`ALTER TABLE accuracy_predictions ADD COLUMN outcome_id ...`) directly modifies the `accuracy_predictions` table. If 0007 has not run, this ALTER TABLE will also fail.

### Why 0009 can run after 0007/0008

`signal_weights` has no FK constraints — it stores lynch_class and regime as plain VARCHAR columns validated by CHECK constraints. It could theoretically run at any point after 0001 (since 0001 defines the classification values the application uses). The 0009 ordering is logical grouping, not a hard dependency.

### Why 0010 (ingest_status) can run last among core migrations

`ingest_status` has no FK constraints and no dependency on any other table. It could run at any position after 0001. Placement at 0010 is intentional — it is an operational concern, not a data model concern, and is logically grouped after the accuracy tables.

### Why waitlist is separate

`waitlist` is a standalone commercial table with no FK relationships. The design document shows it as a separate SQL block outside the numbered migration sequence. In practice, it should be committed as migration 0011 or a named `waitlist.sql` run after all core migrations.

---

## 5. Index Recommendations

The following indexes are recommended beyond the constraints already defined (UNIQUE constraints create indexes automatically in PostgreSQL).

### accuracy_predictions

```sql
-- Streak check: last N predictions for an instrument in a given segment
CREATE INDEX idx_acc_pred_instrument_emitted
  ON accuracy_predictions (instrument_id, emitted_at DESC);

-- 24-segment ledger grouping: GROUP BY lynch_class, regime_tag
CREATE INDEX idx_acc_pred_ledger_segment
  ON accuracy_predictions (lynch_class, regime_tag);
```

**Query pattern:** `WHERE instrument_id = X AND lynch_class = Y AND regime_tag = Z ORDER BY emitted_at DESC LIMIT 5` (streak flag computation). Without the composite index, this requires a sequential scan over all predictions for an instrument.

### ohlcv

```sql
-- Chart data: range scan for a single instrument over a date window
CREATE INDEX idx_ohlcv_instrument_date
  ON ohlcv (instrument_id, trade_date DESC);
```

**Query pattern:** `WHERE instrument_id = X AND trade_date BETWEEN Y AND Z ORDER BY trade_date`. The UNIQUE constraint on `(instrument_id, trade_date)` already creates this index implicitly — no additional index needed here. Verify that the UNIQUE index covers the query planner's range scan path before adding a redundant index.

### signal_weights

```sql
-- Signal engine reads: load ACTIVE weights for a given segment
CREATE INDEX idx_signal_weights_active_segment
  ON signal_weights (status, lynch_class, regime)
  WHERE status = 'ACTIVE';
```

**Query pattern:** `WHERE status = 'ACTIVE' AND lynch_class = X AND regime = Y`. The partial index (`WHERE status = 'ACTIVE'`) keeps the index small — only ACTIVE rows are indexed, which is the only status the signal engine reads at emit time.

### ingest_status

```sql
-- Latest status per script: used on every data_viewer page load
CREATE INDEX idx_ingest_status_script_run
  ON ingest_status (script_name, run_at DESC);
```

**Query pattern:** `WHERE script_name = X ORDER BY run_at DESC LIMIT 1`. Without this index, each staleness check scans the full table per script name, which grows at ~1,250 rows/year.

### accuracy_outcomes

```sql
-- Outcome resolution: find unresolved predictions by prediction_id
CREATE INDEX idx_acc_outcomes_prediction
  ON accuracy_outcomes (prediction_id);
```

**Query pattern:** `WHERE prediction_id = X` used during streak flag computation and outcome back-fill. The FK constraint does not automatically create an index on the FK column in PostgreSQL — this index must be created explicitly.

---

## 6. Free-Tier Constraints

AlphaVeda runs on the Supabase free tier (ap-south-1). These limits affect schema and query design.

### Row and storage limits

| Resource | Free-tier limit | AlphaVeda impact |
|---|---|---|
| Database storage | 500 MB | At steady state (~6M ohlcv rows), ohlcv is the primary consumer. NUMERIC(12,2) × 10 columns × 6M rows ≈ ~180 MB. Well within limit at G0/G1. Monitor at G2. |
| File storage | 1 GB | Not used in MVP (no file uploads) |
| Row limits | No hard row cap | Supabase free tier enforces storage MB, not row count. Row growth is safe as long as total storage stays under 500 MB. |

### Compute and connections

| Resource | Free-tier limit | AlphaVeda impact |
|---|---|---|
| Dedicated compute | None (shared) | Supabase free uses shared Postgres. No dedicated vCPU. All queries compete with other projects on the node. The regime cache singleton (Section 5) reduces per-emit DB reads to avoid shared-compute latency spikes. |
| Connection pool | ~60 connections (PgBouncer default) | Single-user Streamlit app + GHA ingest jobs peak at 3–5 simultaneous connections. Well within limit. Connection singleton in `src/config.py` ensures the Streamlit app holds exactly one connection. |
| Max connections (direct Postgres) | ~15 | GHA ingest scripts must use connection pooling or sequenced jobs, not parallel direct connections. The ingest.yml workflow runs jobs sequentially for this reason. |

### API quotas

| Resource | Free-tier limit | AlphaVeda impact |
|---|---|---|
| API requests | 500,000 / month | At G0/G1 with single user + daily ingest, estimated usage is ~10,000–50,000 requests/month. Safe. Regime cache singleton reduces requests-per-signal from ~3 to ~1 after first emit of the day. |
| Realtime connections | 200 | Not used — MVP has no realtime subscriptions. |
| Edge Functions | 500,000 invocations/month | Not used in MVP. |
| Project pause | Projects pause after 1 week of inactivity | GHA cron runs at 5:45 PM IST weekdays. This keeps the project active on all weekdays. Weekend gaps (2 days) are within the 7-day inactivity threshold. |

### How ingest_status accounts for free-tier constraints

Three design decisions in `ingest_status` directly respond to free-tier limits:

1. **No UNIQUE constraint on (script_name, run_at)** — allows rapid re-runs on FAILED status without needing to UPDATE existing rows. INSERT is always cheaper than SELECT-then-UPDATE under free-tier shared compute.

2. **Append-only with 90-day purge** — rather than updating a single "latest status" row per script, each run appends a new row. This keeps writes simple and idempotent. A GHA maintenance job purges rows older than 90 days to keep the table under ~375 rows and prevent table bloat eating into the 500 MB storage budget.

3. **Script-name + run_at index** — the staleness check in `data_viewer.py` queries `ORDER BY run_at DESC LIMIT 1 per script_name` on every page load. Without the index, a full table scan runs on every page visit. With the index, Supabase free-tier shared compute resolves this in one B-tree lookup per script.

---

## Self-Verification Checklist

- [x] File created at `docs/supabase/SCHEMA.md`
- [x] All 11 tables have subsections in Table Reference (2.1–2.11)
- [x] ERD shows all FK relationships as arrows
- [x] FK map lists: ohlcv→instruments, fundamentals→instruments, trade_outcomes→instruments, trade_outcomes→portfolio_buckets, accuracy_predictions→instruments, accuracy_outcomes→accuracy_predictions, accuracy_predictions.outcome_id→accuracy_outcomes
- [x] Section 4 explains migration ordering including why 0007 must run before 0008
- [x] Section 5 covers all four query pattern categories from the brief
- [x] Section 6 covers free-tier limits and ingest_status design rationale
- [x] File is well above 120 lines
