# AlphaVeda — 10-Day Revenue Sprint Plan
**Clock start:** 2026-06-20  
**Clock end:** 2026-06-30  
**Revenue target:** First sale by Day 3 (Stream A) · First beta user by Day 7 (Stream D)  
**Owner:** Tarun Kochhar · **Builder:** CoS (Claude)

---

## Revenue Stream Priority

| Stream | Path to revenue | Earliest revenue | Owner |
|---|---|---|---|
| **A — Gumroad Starter Pack** | List → first sale | **Day 1–3** | Tarun lists, CoS supports |
| **D — AlphaVeda beta** | G0 → G1 → beta invite | Day 7–10 | CoS builds, Tarun tests |
| C — Financial consulting | Outreach → first call | Day 5–10 | Tarun (no code needed) |
| B — YarnZoo/Crochet | Deferred — out of 10-day scope | — | — |

**Revenue goal by Day 10:** ≥1 Stream A sale ($49 minimum) + ≥1 AlphaVeda beta user signed up

---

## Architectural Principles (locked)

1. **Local-first data:** AlphaVeda queries only local Supabase at runtime. No external API calls in the app layer.
2. **Ingest is separate:** Scheduled GHA cron (primary) + lazy fallback (startup check) feeds the local store.
3. **Provider abstraction:** `DataProvider` ABC routes by exchange. India → BSE/Bhavcopy. Non-India → FMP (commercial) / yfinance (personal).
4. **Commercial gate:** `is_commercial_licensed` flag on each provider. yfinance blocked at instantiation when `ALPHAVEDA_COMMERCIAL=true`.
5. **Test-first schema:** No migration is done until `pytest` passes for that migration.
6. **Dual environment:** `.env.local` (localhost:54321) + `.env.production` (Supabase cloud) from Day 1.

---

## Data Architecture

```
EXTERNAL SOURCES              INGEST SCRIPTS (scheduled)           LOCAL SUPABASE           APP
──────────────────────────────────────────────────────────────────────────────────────────────
Bhavcopy (NSE/BSE daily) ──→  scripts/ingest_bhavcopy.py      ──→  ohlcv              ──→
BSE Shareholding (qtrly) ──→  scripts/ingest_shareholding.py  ──→  fundamentals       ──→  AlphaVeda
BSE Financials (qtrly)   ──→  scripts/ingest_financials.py    ──→                     ──→  queries
FMP / Alpha Vantage      ──→  scripts/ingest_non_india.py     ──→  ohlcv (non-India)  ──→  local only
BSE XBRL (derived)       ──→  scripts/calculate_fundamental…  ──→  fundamentals       ──→
Manual (monthly)         ──→  scripts/update_macro.py         ──→  macro_regime       ──→
```

---

## Council-Approved Data Depths

| Data Type | Depth | Rows (2,000 tickers) | Storage |
|---|---|---|---|
| OHLCV (daily) | 3 years (~750 trading days) | ~1.5M | ~75 MB |
| Fundamentals (quarterly) | 5 years (20 quarters) | ~40,000 | ~8 MB |
| Macro (monthly) | 5 years (60 months) | 60 | <1 MB |
| **Total** | | | **~83 MB** (fits Supabase free tier) |

---

## Schema — 6 Migrations

### 0001_instruments.sql
```sql
CREATE TABLE instruments (
  ticker         TEXT PRIMARY KEY,
  name           TEXT NOT NULL,
  exchange       TEXT NOT NULL CHECK (exchange IN ('NSE','BSE','NYSE','LSE','OTHER')),
  sector         TEXT,
  industry       TEXT,
  classification TEXT CHECK (classification IN (
                   'FAST_GROWER','STALWART','SLOW_GROWER',
                   'CYCLICAL','TURNAROUND','ASSET_PLAY')),
  is_psu         BOOLEAN DEFAULT FALSE,
  active         BOOLEAN DEFAULT TRUE,
  added_at       TIMESTAMPTZ DEFAULT NOW()
);
```

### 0002_ohlcv.sql
```sql
CREATE TABLE ohlcv (
  id          BIGSERIAL PRIMARY KEY,
  ticker      TEXT NOT NULL REFERENCES instruments(ticker),
  date        DATE NOT NULL,
  open        NUMERIC NOT NULL,
  high        NUMERIC NOT NULL,
  low         NUMERIC NOT NULL,
  close       NUMERIC NOT NULL,
  volume      BIGINT,
  source      TEXT NOT NULL DEFAULT 'bhavcopy',
  ingested_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (ticker, date)
);
CREATE INDEX idx_ohlcv_ticker_date ON ohlcv (ticker, date DESC);
```

### 0003_fundamentals.sql
```sql
CREATE TABLE fundamentals (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ticker                TEXT NOT NULL REFERENCES instruments(ticker),
  fundamentals_as_of    DATE NOT NULL,            -- Munger: mandatory, enforced NOT NULL
  source                TEXT NOT NULL,             -- 'bse_filing' | 'fmp' | 'calculated'
  -- Buffett Tier 1 (must-have)
  roic                  NUMERIC,
  fcf_yield             NUMERIC,
  revenue_cagr_3yr      NUMERIC,
  operating_margin      NUMERIC,
  promoter_pledge_pct   NUMERIC,                  -- India: BSE shareholding primary
  promoter_holding_pct  NUMERIC,                  -- India: BSE shareholding primary
  -- Buffett Tier 2
  pe_ttm                NUMERIC,
  debt_to_equity        NUMERIC,
  -- Munger addition (9th field — hard ceiling)
  capex_intensity       NUMERIC,
  last_updated          TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (ticker, fundamentals_as_of, source)
);
```

### 0004_macro_regime.sql
```sql
CREATE TABLE macro_regime (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  recorded_date        DATE NOT NULL UNIQUE,
  pmi_manufacturing    NUMERIC,    -- Growth axis
  pmi_services         NUMERIC,    -- Growth axis
  rbi_repo_rate        NUMERIC,    -- Inflation axis (%)
  cpi_yoy              NUMERIC,    -- Inflation axis (%)
  regime               TEXT CHECK (regime IN ('RISK_ON','RISK_OFF','STAGFLATION','DEFLATION')),
  current_regime       BOOLEAN DEFAULT FALSE,
  notes                TEXT,
  updated_by           TEXT DEFAULT 'manual',
  last_updated         TIMESTAMPTZ DEFAULT NOW()
);
-- Only one current_regime row at a time
CREATE UNIQUE INDEX idx_macro_current ON macro_regime (current_regime) WHERE current_regime = TRUE;
```

### 0005_portfolio_buckets.sql
```sql
CREATE TABLE portfolio_buckets (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  bucket_type      TEXT NOT NULL CHECK (bucket_type IN (
                     'EMERGENCY','NEAR_TERM','MEDIUM_TERM','LONG_TERM')),
  bucket_name      TEXT NOT NULL,
  target_amount    NUMERIC NOT NULL,
  current_amount   NUMERIC DEFAULT 0,
  equity_pct_min   NUMERIC,
  equity_pct_max   NUMERIC,
  horizon_years_min INTEGER,
  horizon_years_max INTEGER,
  gsi_managed      BOOLEAN DEFAULT FALSE,
  notes            TEXT,
  last_updated     TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (bucket_type)
);
```

### 0006_trade_outcomes.sql
```sql
CREATE TABLE trade_outcomes (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ticker            TEXT NOT NULL REFERENCES instruments(ticker),
  entry_date        DATE,
  entry_price       NUMERIC,
  exit_date         DATE,
  exit_price        NUMERIC,
  quantity          NUMERIC,
  position_size_pct NUMERIC,   -- % of portfolio at entry
  kelly_factor      NUMERIC,   -- quarter Kelly used
  signal_strength   TEXT CHECK (signal_strength IN ('HIGH','MEDIUM','LOW')),
  outcome_pnl       NUMERIC,
  notes             TEXT,
  created_at        TIMESTAMPTZ DEFAULT NOW()
);
```

---

## DataProvider Architecture

```python
# src/data/provider.py
from abc import ABC, abstractmethod
import os
import pandas as pd

class CommercialLicenseError(Exception):
    pass

class DataProvider(ABC):
    @property
    @abstractmethod
    def is_commercial_licensed(self) -> bool: ...

    @property
    @abstractmethod
    def supports_fundamentals(self) -> bool: ...

    def _check_commercial_gate(self):
        if os.getenv('ALPHAVEDA_COMMERCIAL') == 'true' and not self.is_commercial_licensed:
            raise CommercialLicenseError(
                f"{self.__class__.__name__} is not licensed for commercial use. "
                "Set ALPHAVEDA_COMMERCIAL=false or use a licensed provider."
            )

    @abstractmethod
    def fetch_ohlcv(self, ticker: str, start: str, end: str) -> pd.DataFrame:
        """Returns DataFrame with columns: date, open, high, low, close, volume"""
        ...

    @abstractmethod
    def fetch_fundamentals(self, ticker: str) -> dict:
        """Returns dict with 9 Buffett+Munger fields. Missing fields = None."""
        ...

# Provider routing
def get_provider(exchange: str, data_type: str) -> 'DataProvider':
    is_commercial = os.getenv('ALPHAVEDA_COMMERCIAL') == 'true'
    if exchange in ('NSE', 'BSE'):
        if data_type == 'ohlcv':
            return BhavcopyCProvider()
        if data_type == 'shareholding':
            return BSEShareholdingProvider()
        if data_type == 'fundamentals':
            return BSEFinancialsProvider()
    else:
        if is_commercial:
            return FMPProvider()
        return YFinanceProvider()
```

---

## Ingest Architecture

**Primary:** GitHub Actions cron (`ingest.yml`)
```yaml
schedule:
  - cron: '15 12 * * 1-5'   # 5:45 PM IST (UTC+5:30), weekdays
```
- Holiday guard: `pandas_market_calendars` checks NSE calendar before fetch
- On trading day: download Bhavcopy ZIP → parse → upsert to `ohlcv` table (local + cloud)
- On holiday: skip with log entry

**Fallback:** Lazy ingest in app startup
```python
def ingest_if_stale():
    """Called in app.py before any data query. Catches missed cron runs."""
    latest = db.execute("SELECT MAX(date) FROM ohlcv").scalar()
    if is_trading_day(today) and latest < today:
        run_bhavcopy_ingest(from_date=latest + 1day, to_date=today)
```

---

## Sprint Plan

### SPRINT 0 — Revenue Unlock (Day 1) ← START HERE
**Goal:** Stream A live on Gumroad. First sale possible today.  
**Duration:** 2 hours  
**Owner:** Tarun (listing) + CoS (Gate 3 fix)

| Task | Owner | Effort | Dependency |
|---|---|---|---|
| S0-1: Fix Gate 3 (README requirements section in Governance Pack) | CoS | 30 min | None |
| S0-2: Final Gumroad listing copy review | CoS | 20 min | S0-1 |
| S0-3: Create Gumroad product ($49/$99/$149 tiers) | Tarun | 30 min | S0-2 |
| S0-4: Post launch (LinkedIn + X) | Tarun | 30 min | S0-3 |
| S0-5: Update business-goal PRIORITY.md with Stream A live date | CoS | 10 min | S0-3 |

**Exit criteria:** Gumroad URL is live and shareable. Stream A status = LIVE.

---

### SPRINT 1 — AlphaVeda G0: Foundation (Day 2–3)
**Goal:** Repo created, 6 migrations applied, providers stubbed, ingest working, tests passing.  
**Duration:** 3–4 hours (one session)  
**Owner:** CoS builds, Tarun reviews at end

| Task | Owner | Effort | Dependency |
|---|---|---|---|
| G0-1: Create `alphaveda` GitHub repo + `.gitignore` | CoS | 15 min | None |
| G0-2: `supabase init` + link to cloud project (cloud-only — no local Docker) | CoS | 15 min | G0-1, Tarun P0-1 |
| G0-3: ~~REMOVED — merged into G0-2 (cloud-only, no separate local/cloud step)~~ | — | — | — |
| G0-4: Write migration 0001 (instruments + exchange + Lynch) | CoS | 20 min | G0-2 |
| G0-5: Write migration 0002 (ohlcv + index) | CoS | 20 min | G0-4 |
| G0-6: Write migration 0003 (fundamentals — source/date NOT NULL) | CoS | 25 min | G0-4 |
| G0-7: Write migration 0004 (macro_regime + unique partial index) | CoS | 20 min | None |
| G0-8: Write migration 0005 (portfolio_buckets) | CoS | 15 min | None |
| G0-9: Write migration 0006 (trade_outcomes) | CoS | 15 min | None |
| G0-10: Apply all migrations → cloud only (`supabase db push`) | CoS | 15 min | G0-4 → G0-9 |
| G0-11: Write `DataProvider` ABC + `CommercialLicenseError` | CoS | 30 min | G0-10 |
| G0-12: Write `BhavcopyCProvider` (working — NSE daily ZIP) | CoS | 45 min | G0-11 |
| G0-13: Write `BSEShareholdingProvider` stub | CoS | 20 min | G0-11 |
| G0-14: Write `BSEFinancialsProvider` stub | CoS | 20 min | G0-11 |
| G0-15: Write `FMPProvider` stub (commercial, non-India) | CoS | 20 min | G0-11 |
| G0-16: Write `YFinanceProvider` (personal use, non-India) | CoS | 20 min | G0-11 |
| G0-17: Write `ingest.yml` (GHA cron + holiday guard) | CoS | 30 min | G0-12 |
| G0-18: Write `ingest_if_stale()` lazy fallback | CoS | 20 min | G0-12 |
| G0-19: Write `calculate_fundamentals.py` (ROIC, FCF yield, capex intensity) | CoS | 45 min | G0-13/14 |
| G0-20: Write `update_macro.py` + staleness warning (>35 days) | CoS | 20 min | G0-10 |
| G0-21: Write `constants.py` (DISCLAIMER + MACRO_INPUTS dict) | CoS | 15 min | None |
| G0-22: Write `pytest` scaffold + 6 smoke tests (incl. `assert len(df) > 0` on Bhavcopy fetch) | CoS | 30 min | G0-10 |
| G0-23: Write `.env.example` (all env vars: SUPABASE_URL, ANON_KEY, SERVICE_KEY, ALPHAVEDA_COMMERCIAL, BSE_USER_AGENT) | CoS | 10 min | All |
| G0-24: Seed data — 10 NSE instruments + current RISK_ON macro row | CoS | 20 min | G0-10 |
| G0-25: ~~REMOVED FROM G0 EXIT GATE~~ — 3yr historical ingest is a one-time local setup script (`scripts/seed_historical.py`), run before G1, not a G0 dependency | — | — | — |
| G0-26: pytest passes — G0 exit gate | CoS | — | All |

**Exit criteria:** `supabase db push` succeeds (cloud) + `pytest` 6/6 (incl. Bhavcopy row-count assertion) + `python -c "from src.data.provider import get_provider"` works + `git status` shows no secrets + `.env.example` has ALPHAVEDA_COMMERCIAL documented + all stubs raise `NotImplementedError`.

---

### SPRINT 2 — AlphaVeda G1: Basic App Shell (Day 4–5)
**Goal:** Working Streamlit app reading from local Supabase. Real data visible. Self-use test complete.  
**Duration:** 3–4 hours

| Task | Owner | Effort | Dependency |
|---|---|---|---|
| G1-1: `app.py` entry point + page router | CoS | 30 min | G0 done |
| G1-2: `config.py` — env loading, DB client, env switching | CoS | 20 min | G0 done |
| G1-3: OHLCV chart page (single ticker, candlestick, from local DB) | CoS | 45 min | G1-2 |
| G1-4: RSI + 200-day MA overlay on chart | CoS | 30 min | G1-3 |
| G1-5: Fundamental stats card (9 fields, source badge, as_of date) | CoS | 40 min | G1-2 |
| G1-6: Promoter pledge + holding display (color-coded: >15% = amber) | CoS | 20 min | G1-5 |
| G1-7: Macro regime indicator card (current regime badge) | CoS | 20 min | G1-2 |
| G1-8: Portfolio bucket view (4-bucket display, current vs target) | CoS | 30 min | G1-2 |
| G1-9: SEBI disclaimer footer (persistent, on every page) | CoS | 10 min | G1-1 |
| G1-10: `ingest_if_stale()` called on app startup | CoS | 15 min | G0-18 |
| G1-11: Seed real data — 5 NSE tickers with full 3yr OHLCV | CoS | 20 min | G0-25 |
| G1-12: Self-use test session (Tarun uses the app for 30 min) | Tarun | 30 min | G1-1 → G1-11 |
| G1-13: G1 regression tests (10 checks — data loads, pages render) | CoS | 30 min | G1-12 |

**Exit criteria:** App runs locally against real NSE data. Tarun has used it. 10 regression checks pass.

---

### SPRINT 3 — AlphaVeda G2: Auth + Cloud Deploy (Day 6–8)
**Goal:** Supabase auth live. Waitlist form collecting emails. App deployed to Streamlit Cloud (or Vercel). First beta invite sent.  
**Duration:** 3–4 hours

| Task | Owner | Effort | Dependency |
|---|---|---|---|
| G2-1: Supabase auth setup (email/password, RLS policies) | CoS | 30 min | G0 cloud project |
| G2-2: `auth.py` module (get_supabase, get_current_user, render_auth_gate) | CoS | 40 min | G2-1 |
| G2-3: Route protection (authenticated vs anonymous tiers) | CoS | 30 min | G2-2 |
| G2-4: Waitlist form (email + "₹999/month — does that work for you?" question) | CoS | 20 min | G2-1 |
| G2-5: `waitlist` table migration (source, price_ok, joined_at) | CoS | 15 min | G2-4 |
| G2-6: Streamlit Cloud deployment + Supabase cloud secrets | Tarun + CoS | 30 min | All G1 done |
| G2-7: Custom domain (optional — alphaveda.in or alphavedaapp.com) | Tarun decision | — | G2-6 |
| G2-8: Beta invite #1 — Tarun as external user (different device/browser) | Tarun | 15 min | G2-6 |
| G2-9: G2 regression tests (10 checks — auth flows, data isolation) | CoS | 30 min | G2-3 |
| G2-10: GHA ingest cron live on `alphaveda` repo | CoS | 20 min | G0-17 |

**Exit criteria:** App is publicly accessible. Waitlist form works. Beta invite #1 accepted. GHA cron runs first successful ingest.

---

### SPRINT 4 — Revenue Checkpoint + Feedback (Day 9–10)
**Goal:** Count Stream A sales. Collect first AlphaVeda beta feedback. Adjust plan.  
**Duration:** 2 hours

| Task | Owner | Effort | Dependency |
|---|---|---|---|
| RC-1: Stream A sales count + first buyer follow-up | Tarun | 30 min | S0 done |
| RC-2: AlphaVeda beta feedback session (Tarun uses app as user, logs gaps) | Tarun | 30 min | G2 done |
| RC-3: First 5 waitlist invite emails (from Tarun's network) | Tarun | 30 min | G2-4 |
| RC-4: Sprint retrospective — what shipped vs planned, what's next | CoS | 20 min | All |
| RC-5: Update SESSION_RESUME.md + memory for next session | CoS | 20 min | RC-4 |

**Exit criteria:** Revenue signal confirmed (≥1 Stream A sale OR ≥1 AlphaVeda waitlist signup). Next sprint defined.

---

## Effort Summary

| Sprint | Session(s) | Effort | Revenue unlock |
|---|---|---|---|
| S0 — Stream A Launch | Day 1 | 2 hrs | ✓ First sale possible Day 1 |
| G0 — Foundation | Day 2–3 | 3–4 hrs | — |
| G1 — App Shell | Day 4–5 | 3–4 hrs | — |
| G2 — Auth + Deploy | Day 6–8 | 3–4 hrs | ✓ Waitlist + beta |
| Checkpoint | Day 9–10 | 2 hrs | ✓ Revenue count |
| **Total** | **10 days** | **~15 hrs CoS · ~3 hrs Tarun** | |

---

## Data Provider Replacement Map (EODHD → Free Stack)

| Field | Free Source | Cost | Commercial? |
|---|---|---|---|
| Promoter pledge % | BSE Shareholding API | ₹0 | ✓ Official |
| Promoter holding % | BSE Shareholding API | ₹0 | ✓ Official |
| Revenue, Operating Income, Net Income | BSE Quarterly Results (XBRL) | ₹0 | ✓ Official |
| ROIC (calculated) | From BSE P&L + Balance Sheet | ₹0 | ✓ Official |
| FCF yield (calculated) | BSE Cash Flow + Bhavcopy market cap | ₹0 | ✓ Official |
| Capex intensity (calculated) | BSE Cash Flow + P&L | ₹0 | ✓ Official |
| Revenue CAGR 3yr (calculated) | BSE historical results | ₹0 | ✓ Official |
| Operating margin | BSE Results or Screener.in | ₹0 | ✓/Grey |
| P/E TTM | yfinance SYMBOL.NS (personal) → FMP (commercial) | ₹0 → ₹1,200/mo | Personal/Commercial |
| D/E ratio | yfinance SYMBOL.NS (personal) → FMP (commercial) | ₹0 → ₹1,200/mo | Personal/Commercial |
| Non-India OHLCV (commercial) | Financial Modeling Prep (FMP) | ₹1,200/mo at launch | ✓ Commercial |
| Non-India OHLCV (personal) | yfinance | ₹0 | Personal only |

**EODHD total replacement cost at personal use:** ₹0  
**EODHD total replacement cost at first subscriber:** ₹1,200/mo ($14 FMP Starter)  
**Break-even:** 2 subscribers at ₹999/month covers FMP cost

---

## Stream C — Financial Consulting (parallel, no code needed)

| Action | Effort | Timeline |
|---|---|---|
| Identify 3 potential consulting clients (existing network) | 30 min | Day 1 |
| Send outreach (WhatsApp/email, "30-min portfolio review") | 20 min | Day 2 |
| First call booked | — | Day 4–7 |
| First consulting revenue | — | Day 5–10 |

Consulting revenue requires zero build time. Can run in parallel with all sprints. Rate: ₹3,000–₹10,000/call.

---

## Open Decisions (Tarun — needed before or during sprints)

| Decision | Needed by | Default if no answer |
|---|---|---|
| Q1: Ingest trigger — Option D (Hybrid) confirmed? | Sprint 1 | Default: Option D |
| Q2: Supabase cloud project region (ap-south-1 recommended) | Sprint 1 | ap-south-1 |
| AlphaVeda pricing: ₹999/mo, ₹1,999/mo, or tiered? | Sprint 3 | ₹999/mo single tier |
| Custom domain for AlphaVeda? (alphaveda.in available?) | Sprint 3 | Streamlit subdomain for now |
| Stream C: who are the 3 consulting outreach targets? | Day 1–2 | Tarun identifies |

---

*Plan version 1.0 — 2026-06-20. Built from council outputs (Phase A/B/C) + strategic analysis. Next review: Sprint 4 checkpoint (Day 9-10).*
