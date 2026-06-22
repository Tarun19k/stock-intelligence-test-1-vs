# AlphaVeda MVP Design
**Date:** 2026-06-22  
**Status:** v0.4 — AMENDED POST-R1+R3-COUNCIL — R1 Red Team 18 gaps + R3 Council MA-1..MA-14 applied; migrations 0011/0012 added; P0 chain + emit-time guards + commercial gate + upgraded G0 gate  
**Author:** CoS (Claude Sonnet 4.6) + Tarun Kochhar  
**Brainstorming session:** 2026-06-21, chief-of-staff + panel-convene workflow

---

## Locked Decisions (pre-design, council-unanimous)

| Decision | Verdict | Council |
|---|---|---|
| Product architecture | Option A — standalone repo, separate from GSI | CoS recommendation, Tarun approved |
| Feedback loop | Option C — rule-weighted accuracy + data depth compounding | 7/7 unanimous |
| MVP scope | Approach 2 — balanced MVP (data viewer + signal engine + path optimizer + auth) | 7/7 unanimous |
| Accuracy self-improvement | Compounds over time with 6 mandatory guards | 7/7 unanimous |

---

## 6 Mandatory Accuracy Guards (council conditions — cannot be deferred)

| # | Guard | Seat | Prevents |
|---|---|---|---|
| 1 | Regime-segmented accuracy — weights adjust within RISK_ON/OFF/STAGFLATION/DEFLATION, never across | Dalio + Marks | Cross-cycle weight contamination |
| 2 | Counter-cyclical weighting — accuracy streaks trigger skepticism, not confidence boost | Soros | Reflexivity self-amplification at market peak |
| 3 | Fundamentals weight floor — ROIC/FCF/promoter pledge never demoted below minimum regardless of ledger | Buffett | Short-term accuracy pressure destroying long-term signals |
| 4 | 24-segment accuracy ledger — Lynch classification (6) × Dalio regime (4) = 24 independent segments | Lynch | Fast Grower weights bleeding into Cyclical analysis |
| 5 | Magnitude + peak-return logging — signal quality = hit rate × magnitude factor, not hit rate alone | Druckenmiller | Optimising for signal frequency instead of return capture |
| 6 | Quarterly human review gate — weight adjustment proposals generated, never auto-applied | Munger | Goodhart's Law; lollapalooza at cycle peak |

---

## 7 Schema-Level Implementation Conditions (council mandated — in schema from Day 1)

| Seat | Condition |
|---|---|
| Buffett | Fundamentals weight floor constant defined before first prediction row inserted |
| Munger | Quarterly review process documented (not a placeholder) before G0 build begins |
| Dalio | `macro_regime` tag column on every `accuracy_predictions` row, populated at insert time |
| Marks | `cycle_phase` segment column in accuracy ledger schema from Day 1 |
| Soros | `accuracy_streak_flag` column in ledger schema from Day 1 |
| Druckenmiller | `kelly_position_size` is a required output column of path optimizer, not deferred |
| Lynch | `classification` column in `instruments` table populated at G1; every signal row inherits it |

---

## Section 1 — Architecture

### Product Definition
AlphaVeda is a **predictions and accuracy tool** that identifies the right path to gain returns for portfolios under a user profile. It operates as three co-equal layers working together:

1. **Data quality layer** — accurate, fact-checked, provenance-tracked ingestion from official sources
2. **Data viewer layer** — meaningful interpretation of what the data shows (co-equal with prediction layer)
3. **Signal engine + path optimizer** — stock-level signals feeding portfolio-level recommendations, personalized to bucket profile

### Five-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 5 — PRESENTATION                                         │
│  Streamlit app                                                  │
│  · Data viewer: charts, fundamentals, macro regime, buckets     │
│  · Signal display: confidence scores, classification badge      │
│  · Path recommendations: ranked move list with Kelly sizing     │
│  · Accuracy dashboard: 24-segment ledger, weight proposals      │
│  · SEBI disclaimer: persistent footer on every page            │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 4 — PATH OPTIMIZER                                       │
│  Input: user bucket profile + current holdings + signal output  │
│  Output: ranked BUY/EXIT/REBALANCE/HOLD list per bucket        │
│  · Filters signals by bucket horizon (Long-Term vs Near-Term)   │
│  · Applies Kelly sizing: kelly_position_size per recommendation │
│  · Max position 10% (₹72,500), min 1% (₹7,250), sector 35%   │
│  · Cash floor 10% (₹72,500) always liquid                      │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 3 — SIGNAL ENGINE                                        │
│  · Directional signals: bull/bear per instrument                │
│  · Confidence scoring: 0–100 composite                          │
│  · Signal arbitration: when TA signals conflict                 │
│  · Every signal tagged: regime + Lynch classification + date   │
│  · Prediction horizon: 30/60/90 days per bucket type           │
│  · Logs to accuracy_predictions on every emit                   │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2 — STORAGE (Supabase cloud, ap-south-1, free tier)     │
│  6 core tables: instruments · ohlcv · fundamentals ·           │
│                 macro_regime · portfolio_buckets · trade_outcomes│
│  3 accuracy tables: accuracy_predictions · accuracy_outcomes ·  │
│                     signal_weights                              │
│  24-segment ledger: accuracy per Lynch class × macro regime    │
│  All accuracy rows: regime_tag + cycle_phase + streak_flag      │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 1 — DATA QUALITY                                         │
│  Sources: Bhavcopy (NSE/BSE daily) · BSE Shareholding (qtrly)  │
│           BSE Financials XBRL (qtrly) · Macro manual (monthly) │
│  Providers: DataProvider ABC · BhavcopyCProvider ·             │
│             BSEShareholdingProvider · BSEFinancialsProvider ·   │
│             YFinanceProvider (personal) · FMPProvider (commercial)│
│  Guards: CommercialLicenseError · User-Agent header required   │
│  Provenance: every row has source + ingested_at + freshness    │
└─────────────────────────────────────────────────────────────────┘
         ↑ accuracy_outcomes feed back to Layer 2 ledger ↑
         ↑ 24-segment weights proposed quarterly to Tarun ↑
```

### Cross-Cutting: Accuracy Feedback Loop

The feedback loop connects Layer 3 back to Layer 2 without creating a new layer:

```
Signal emitted (Layer 3)
    → logged to accuracy_predictions with full context:
      regime_tag, lynch_class, confidence, direction, magnitude_target,
      horizon_days, accuracy_streak_flag, cycle_phase
    → prediction window expires (horizon_days from emit date)
    → outcome logged to accuracy_outcomes:
      actual_direction, actual_magnitude, peak_return_pct, outcome_date
    → 24-segment ledger updated (lynch_class × regime segment)
    → when segment N ≥ 30 observations: weight proposal generated
    → proposal written to signal_weights with status = PROPOSED
    → quarterly: Tarun reviews proposals → approves or rejects
    → approved proposals update signal_weights.status = ACTIVE
    → signal engine reads ACTIVE weights on next emit
```

**Self-improvement is the ledger filling, not the algorithm tuning itself.** The algorithm proposes; the human approves.

### Standalone Repo Architecture

```
alphaveda/                      ← new GitHub repo
├── src/
│   ├── data/
│   │   ├── provider.py         ← DataProvider ABC + routing
│   │   ├── bhavcopy.py
│   │   ├── bse_shareholding.py
│   │   ├── bse_financials.py
│   │   ├── yfinance_provider.py
│   │   └── fmp_provider.py
│   ├── signals/
│   │   ├── engine.py           ← signal emit + accuracy log
│   │   ├── arbitration.py      ← conflict resolution
│   │   └── weights.py          ← reads ACTIVE weights from DB
│   ├── portfolio/
│   │   ├── optimizer.py        ← path recommendations + Kelly sizing
│   │   └── buckets.py          ← bucket-aware filtering
│   ├── accuracy/
│   │   ├── ledger.py           ← 24-segment update logic
│   │   ├── outcomes.py         ← prediction resolution
│   │   └── proposals.py        ← weight proposal generation
│   └── config.py               ← env loading, DB client, env switching
├── scripts/
│   ├── ingest_bhavcopy.py
│   ├── ingest_shareholding.py
│   ├── ingest_financials.py
│   ├── calculate_fundamentals.py
│   ├── update_macro.py
│   └── seed_historical.py
├── migrations/
│   ├── 0001_instruments.sql
│   ├── 0002_ohlcv.sql
│   ├── 0003_fundamentals.sql
│   ├── 0004_macro_regime.sql
│   ├── 0005_portfolio_buckets.sql
│   ├── 0006_trade_outcomes.sql
│   ├── 0007_accuracy_predictions.sql
│   ├── 0008_accuracy_outcomes.sql
│   └── 0009_signal_weights.sql
├── app.py                      ← Streamlit entry point
├── pages/
│   ├── data_viewer.py          ← charts, fundamentals, macro, buckets
│   ├── signals.py              ← signal display + classification
│   ├── path.py                 ← path recommendations + Kelly output
│   └── accuracy.py             ← 24-segment dashboard + proposals
├── auth.py                     ← Supabase auth + RLS (G2)
├── tests/
│   ├── test_smoke.py           ← 6 G0 smoke tests
│   └── test_regression.py      ← 10 G1 regression tests
├── .github/workflows/
│   └── ingest.yml              ← GHA cron 5:45 PM IST weekdays
├── .env.example
├── constants.py                ← SEBI disclaimer + weights constants
└── requirements.txt
```

### Shared Supabase Instance

AlphaVeda and GSI share one Supabase project (ap-south-1). Table namespacing prevents collision:

```
Supabase project: alphaveda-prod (ap-south-1)
├── AlphaVeda tables: instruments, ohlcv, fundamentals, macro_regime,
│                     portfolio_buckets, trade_outcomes,
│                     accuracy_predictions, accuracy_outcomes,
│                     signal_weights, waitlist
└── GSI tables (when OPEN-003 ships): gsi_forecasts, gsi_accuracy_ledger,
                                       gsi_sessions (prefixed to avoid collision)
```

---

## Section 1.5 — Non-Goals

**AlphaVeda does NOT stream real-time market prices or tick data.** The MVP ingest cadence is once daily at 5:45 PM IST via GHA cron; Supabase free tier (ap-south-1) has no websocket budget for live feeds, and Bhavcopy is an end-of-day file by design.

**AlphaVeda does NOT provide SEBI-RIA investment advice or buy/sell recommendations framed as advice.** SEBI registration as a Research Analyst or Investment Adviser is a regulatory prerequisite the product does not hold in v1; every signal output is research-only, with a pinned non-dismissable disclaimer enforced by `.claude/rules/SEBI_COMPLIANCE.md` (Section 4).

**AlphaVeda does NOT execute trades automatically or integrate with any broker API.** Path optimizer output is a ranked recommendation list read by Tarun; no order-routing, no Zerodha/ICICI Direct API calls, no paper-trading engine. Execution remains a manual human step.

**AlphaVeda does NOT support multi-user authentication or per-user data isolation in v1.** Auth (G2) is implemented via `auth.py` and Supabase RLS but is a single-user gate only — multi-user tenancy, role-based access, and per-user portfolio isolation are deferred beyond G2 as stated in the locked decisions table (Section 1).

**AlphaVeda does NOT use paid commercial data sources (FMP or equivalent) in MVP.** `FMPProvider` is present in the provider routing table but gated behind `CommercialLicenseError` until the first non-self subscriber; the free BSE stack (Bhavcopy + XBRL + Shareholding) is the sole ingest path through v1 go-live.

**AlphaVeda does NOT run historical backtests or simulate past signal performance.** The accuracy ledger is forward-only — predictions are logged at emit time and resolved as outcomes arrive; retrofitting historical signals would break the regime-tag and cycle_phase integrity the council mandated for accuracy tracking (Guards 1 and 4).

**AlphaVeda does NOT track portfolio P&L, realised gains, or tax lots.** P&L accounting, XIRR calculation, and cost-basis tracking live in GSI (the existing dashboard sharing the same Supabase instance); AlphaVeda reads `portfolio_buckets` for sizing context only and does not duplicate that accounting layer.

**AlphaVeda does NOT ship a native mobile app or a mobile-optimised Progressive Web App in MVP.** The presentation layer is Streamlit running on Mac local dev; Streamlit's responsive layout is accepted as-is. A mobile-first redesign is a post-v1 decision gated on the waitlist subscriber count.

**AlphaVeda does NOT auto-apply weight proposals from the accuracy ledger.** Weight changes require Tarun's explicit quarterly approval (Guard 6 — Munger condition, Section 7); the system writes `status = PROPOSED` and surfaces a banner notification; no code path exists that transitions a row to `ACTIVE` without human approval.

---

## Section 2 — Data Model (9 Migrations)

### Core tables (6 migrations)

**0001_instruments.sql**
```sql
CREATE TABLE instruments (
  id             SERIAL PRIMARY KEY,
  ticker         VARCHAR(20) NOT NULL UNIQUE,
  name           VARCHAR(200) NOT NULL,
  exchange       VARCHAR(10) NOT NULL CHECK (exchange IN ('NSE', 'BSE')),
  classification VARCHAR(20) NOT NULL CHECK (
    classification IN ('fast_grower','stalwart','slow_grower',
                       'cyclical','turnaround','asset_play')
  ),                          -- Lynch classification; NOT NULL from Day 1 (Gap 7)
  isin           CHAR(12),
  sector         VARCHAR(100),
  is_active      BOOLEAN NOT NULL DEFAULT true,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**0002_ohlcv.sql**
```sql
CREATE TABLE ohlcv (
  id            BIGSERIAL PRIMARY KEY,
  instrument_id INT NOT NULL REFERENCES instruments(id),
  trade_date    DATE NOT NULL,
  open          NUMERIC(12,2) NOT NULL,
  high          NUMERIC(12,2) NOT NULL,
  low           NUMERIC(12,2) NOT NULL,
  close         NUMERIC(12,2) NOT NULL,
  volume        BIGINT NOT NULL,
  source        VARCHAR(50) NOT NULL,   -- 'bhavcopy_nse' | 'bhavcopy_bse'
  ingested_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (instrument_id, trade_date)
);
```

**0003_fundamentals.sql**
```sql
CREATE TABLE fundamentals (
  id            BIGSERIAL PRIMARY KEY,
  instrument_id INT NOT NULL REFERENCES instruments(id),
  period_end    DATE NOT NULL,           -- quarter-end date
  roic_pct      NUMERIC(8,2),
  fcf_cr        NUMERIC(12,2),           -- crores
  promoter_pledge_pct NUMERIC(5,2),
  debt_equity   NUMERIC(8,2),
  eps           NUMERIC(10,2),
  revenue_cr    NUMERIC(12,2),
  source        VARCHAR(50) NOT NULL,
  ingested_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (instrument_id, period_end)
);
```

**0004_macro_regime.sql**
```sql
CREATE TABLE macro_regime (
  id          SERIAL PRIMARY KEY,
  regime_date DATE NOT NULL UNIQUE,
  regime      VARCHAR(20) NOT NULL CHECK (
    regime IN ('RISK_ON','RISK_OFF','STAGFLATION','DEFLATION')
  ),                          -- no UNIQUE: this is a time-series table; same regime repeats across dates
  rbi_rate    NUMERIC(4,2),
  usd_inr     NUMERIC(8,2),
  nifty_vix   NUMERIC(6,2),
  fii_flow_cr NUMERIC(12,2),            -- FII net monthly, crores
  notes       TEXT,
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**0005_portfolio_buckets.sql**
```sql
CREATE TABLE portfolio_buckets (
  id              SERIAL PRIMARY KEY,
  bucket_name     VARCHAR(50) NOT NULL CHECK (
    bucket_name IN ('emergency','near_term','medium_term','long_term')
  ),
  target_value_inr NUMERIC(12,2) NOT NULL,
  horizon_days_min INT NOT NULL,
  horizon_days_max INT,                  -- NULL = indefinite (long_term)
  cash_floor_pct  NUMERIC(5,2) NOT NULL DEFAULT 10.0,
  max_position_pct NUMERIC(5,2) NOT NULL DEFAULT 10.0,
  sector_cap_pct  NUMERIC(5,2) NOT NULL DEFAULT 35.0
);

-- Seed once at G0
INSERT INTO portfolio_buckets VALUES
  (1,'emergency',  500000,  0,    90,  100.0, 0.0,  0.0),
  (2,'near_term',  250000,  90,   365, 10.0,  10.0, 35.0),
  (3,'medium_term',500000,  365,  1825,10.0,  10.0, 35.0),
  (4,'long_term',  450000,  1825, NULL,10.0,  10.0, 35.0);
```

**0006_trade_outcomes.sql**
```sql
CREATE TABLE trade_outcomes (
  id              BIGSERIAL PRIMARY KEY,
  instrument_id   INT NOT NULL REFERENCES instruments(id),
  bucket_id       INT NOT NULL REFERENCES portfolio_buckets(id),
  entry_date      DATE NOT NULL,
  entry_price     NUMERIC(12,2) NOT NULL,
  exit_date       DATE,
  exit_price      NUMERIC(12,2),
  position_value  NUMERIC(12,2) NOT NULL,
  return_pct      NUMERIC(8,4),          -- populated on exit
  notes           TEXT,
  exit_trigger    CHAR(2) CHECK (exit_trigger IN ('E1','E2','E3','E4'))  -- populated on EXIT signals; NULL for HOLD/BUY
);
```

### Accuracy tables (3 migrations)

**0007_accuracy_predictions.sql**
```sql
CREATE TABLE accuracy_predictions (
  id                  BIGSERIAL PRIMARY KEY,
  instrument_id       INT NOT NULL REFERENCES instruments(id),
  emitted_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  direction           VARCHAR(5) NOT NULL CHECK (direction IN ('BULL','BEAR')),
  confidence          SMALLINT NOT NULL CHECK (confidence BETWEEN 0 AND 100),
  magnitude_target    NUMERIC(6,4),       -- expected return fraction
  horizon_days        INT NOT NULL,
  regime_tag          VARCHAR(20) NOT NULL CHECK (
    regime_tag IN ('RISK_ON','RISK_OFF','STAGFLATION','DEFLATION')
  ),                          -- CHECK not FK: macro_regime is a time-series, not a lookup; enum validated here
  lynch_class         VARCHAR(20) NOT NULL CHECK (
    lynch_class IN ('fast_grower','stalwart','slow_grower',
                    'cyclical','turnaround','asset_play')
  ),
  cycle_phase         VARCHAR(20) NOT NULL CHECK (
    cycle_phase IN ('early_bull','mid_bull','late_bull',
                    'early_bear','mid_bear','late_bear')
  ),
  accuracy_streak_flag BOOLEAN NOT NULL DEFAULT false
  -- outcome_id added in 0008 via ALTER TABLE (circular FK: accuracy_outcomes doesn't exist yet at 0007 run time)
);
```

**0008_accuracy_outcomes.sql**
```sql
CREATE TABLE accuracy_outcomes (
  id               BIGSERIAL PRIMARY KEY,
  prediction_id    BIGINT NOT NULL REFERENCES accuracy_predictions(id),
  outcome_date     DATE NOT NULL,
  actual_direction VARCHAR(5) NOT NULL CHECK (actual_direction IN ('BULL','BEAR')),
  actual_return    NUMERIC(8,4),
  peak_return_pct  NUMERIC(8,4),          -- max return during horizon window
  is_correct       BOOLEAN NOT NULL,
  resolved_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Resolve circular FK: accuracy_predictions.outcome_id couldn't reference this table at 0007 run time
ALTER TABLE accuracy_predictions
  ADD COLUMN outcome_id BIGINT REFERENCES accuracy_outcomes(id);
```

**0009_signal_weights.sql**
```sql
CREATE TABLE signal_weights (
  id              SERIAL PRIMARY KEY,
  lynch_class     VARCHAR(20) NOT NULL,
  regime          VARCHAR(20) NOT NULL,
  signal_name     VARCHAR(50) NOT NULL,  -- e.g. 'roic', 'momentum_rsi', 'peg'
  weight          NUMERIC(5,4) NOT NULL,
  status          VARCHAR(10) NOT NULL CHECK (status IN ('ACTIVE','PROPOSED','REJECTED')),
  proposed_at     TIMESTAMPTZ,
  approved_at     TIMESTAMPTZ,
  approved_by     TEXT,                  -- 'tarun' when human-approved
  observation_n   INT,                   -- how many outcomes drove this proposal
  UNIQUE (lynch_class, regime, signal_name, status)
);
```

**0010_ingest_status.sql**
```sql
CREATE TABLE ingest_status (
  id          SERIAL PRIMARY KEY,
  script_name VARCHAR(100) NOT NULL,
  run_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  status      VARCHAR(10) NOT NULL CHECK (status IN ('OK','FAILED','PARTIAL')),
  error_msg   TEXT,
  rows_written INT
);
```

### Waitlist table (commercial intelligence)

```sql
CREATE TABLE waitlist (
  id              SERIAL PRIMARY KEY,
  email           VARCHAR(200) NOT NULL UNIQUE,
  name            VARCHAR(200),
  signed_up_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  price_feedback  VARCHAR(20) CHECK (
    price_feedback IN ('too_high','fair','too_low')
  ),                                     -- Gap 10 closed
  referred_by     VARCHAR(200),          -- referral source (Gap 10 closed)
  converted_at    TIMESTAMPTZ            -- set when user becomes subscriber
);
```

---

## Section 3 — 24-Segment Accuracy Ledger + Supporting Modules

### The ledger grid

The ledger is not a table — it is a query view over `accuracy_outcomes` grouped by `lynch_class × regime`. At any point, the ledger cell for (fast_grower, RISK_ON) holds:

```sql
SELECT
  p.lynch_class,
  p.regime_tag,
  COUNT(*)                          AS n_observations,
  AVG(o.is_correct::int)            AS hit_rate,
  AVG(o.peak_return_pct)            AS avg_peak_return,
  AVG(o.actual_return * (CASE WHEN p.accuracy_streak_flag THEN 0.7 ELSE 1.0 END)) AS streak_adj_return
FROM accuracy_predictions p
JOIN accuracy_outcomes o ON o.prediction_id = p.id
GROUP BY p.lynch_class, p.regime_tag;
```

When a cell's `n_observations ≥ 30`, a weight proposal is generated for that segment.

### cycle_phase derivation module (Gap 5 closed)

File: `src/accuracy/cycle_phase.py`

```python
# Derives cycle_phase from macro_regime + Nifty 200-day MA position + VIX level.
# Called once per signal emit — not cached, reads current macro state.

PHASE_RULES = [
    # (regime, nifty_above_200ma, vix_below_threshold) → cycle_phase
    ('RISK_ON',     True,  True,  'mid_bull'),
    ('RISK_ON',     True,  False, 'late_bull'),   # high VIX in uptrend = late cycle
    ('RISK_ON',     False, True,  'early_bull'),
    ('RISK_OFF',    False, False, 'mid_bear'),
    ('RISK_OFF',    False, True,  'late_bear'),   # low VIX in downtrend = exhaustion
    ('RISK_OFF',    True,  False, 'early_bear'),
    ('STAGFLATION', False, False, 'mid_bear'),
    ('STAGFLATION', True,  False, 'late_bull'),
    ('DEFLATION',   False, True,  'late_bear'),
    ('DEFLATION',   False, False, 'mid_bear'),
]

def derive_cycle_phase(regime: str, nifty_close: float, nifty_200ma: float, vix: float) -> str:
    above_ma = nifty_close > nifty_200ma
    vix_low  = vix < 18.0           # VIX_CALM_THRESHOLD in constants.py
    for r, ma, v, phase in PHASE_RULES:
        if r == regime and ma == above_ma and v == vix_low:
            return phase
    return 'mid_bull'               # safe default — never None
```

### Streak detection (Gap 6 closed)

Constants in `constants.py`:
```python
STREAK_WINDOW       = 5     # consecutive correct predictions to trigger flag
STREAK_DISCOUNT_FACTOR = 0.7  # weight proposals discounted when streak_flag = true
```

Logic in `src/accuracy/ledger.py`:

```python
def compute_streak_flag(instrument_id: int, lynch_class: str, regime: str, db) -> bool:
    """Returns True if last STREAK_WINDOW predictions in this segment were all correct."""
    recent = db.table('accuracy_outcomes') \
        .select('is_correct') \
        .eq('prediction.instrument_id', instrument_id) \
        .eq('prediction.lynch_class', lynch_class) \
        .eq('prediction.regime_tag', regime) \
        .order('outcome_date', desc=True) \
        .limit(STREAK_WINDOW).execute()
    if len(recent.data) < STREAK_WINDOW:
        return False
    return all(row['is_correct'] for row in recent.data)
```

---

## Section 4 — Data Viewer Design

### Pages

**`pages/data_viewer.py`** — 4 tabs:
- **Price tab**: Candlestick OHLCV (Plotly), 50/200 MA overlay, volume bar chart below
- **Fundamentals tab**: Table of ROIC, FCF, promoter_pledge, D/E, EPS growth for last 8 quarters; color-coded (green > 15% ROIC, red > 15% pledge)
- **Macro tab**: Current regime badge (color-coded), RBI rate, USD/INR, VIX, FII flow. Regime history timeline.
- **Buckets tab**: 4-bucket allocation bar, current value vs target, cash floor indicator

**Data provenance**: every section shows `Source: {source}  |  Last ingested: {ingested_at}` in small gray text. If `ingested_at` > 1 trading day ago, show amber "STALE" badge.

### SEBI disclaimer — pinned (Gap 9 closed)

Implemented in `app.py` (runs on every page load, before any page content):

```python
# Injected as fixed-bottom HTML — not a Streamlit widget, cannot be scrolled past
st.markdown("""
<style>
  .sebi-disclaimer {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: #fff3cd; color: #664d03;
    padding: 6px 16px; font-size: 11px;
    border-top: 1px solid #ffc107; z-index: 9999;
  }
</style>
<div class="sebi-disclaimer">
  ⚠ AlphaVeda provides information and analysis only. This is NOT investment advice.
  Consult a SEBI-registered investment advisor before making any investment decision.
  Past signal accuracy does not guarantee future returns.
</div>
""", unsafe_allow_html=True)
```

This block runs before `st.navigation()` — every page inherits it. It cannot be dismissed.

### .claude/rules/ directory (Gap 9 closed)

```
alphaveda/.claude/rules/
├── SEBI_COMPLIANCE.md       # pinned disclaimer required, no RIA advisory content
├── COMMERCIAL_GATE.md       # CommercialLicenseError rules, yfinance block
└── DATA_SOURCES.md          # licensed vs free source table, upgrade triggers
```

These are enforced at the repository level — any Claude session working on AlphaVeda reads them at session start via CLAUDE.md `include` directive.

---

## Section 5 — Signal Engine Design

### Constants (Gap 1 closed)

`constants.py` — all signal-related constants live here:

```python
# Fundamentals guard — cannot be overridden by ledger regardless of segment accuracy
FUNDAMENTAL_WEIGHT_FLOOR = 0.30   # min combined weight for ROIC + FCF + pledge signals

# Counter-cyclical guard
STREAK_WINDOW          = 5
STREAK_DISCOUNT_FACTOR = 0.7

# Accuracy ledger thresholds
OBSERVATION_THRESHOLD  = 30       # min observations before weight proposal generated
PROPOSAL_MIN_DELTA     = 0.03     # proposal only if new weight differs by ≥ 3%

# Cycle phase VIX boundary
VIX_CALM_THRESHOLD     = 18.0

# SEBI disclaimer text (single source of truth)
SEBI_DISCLAIMER = (
    "AlphaVeda provides information and analysis only. "
    "This is NOT investment advice. Consult a SEBI-registered "
    "investment advisor before making any investment decision."
)

# EXIT trigger E2 — bucket-aware consecutive threshold + confidence floor
E2_CONSECUTIVE_THRESHOLD: dict[str, int] = {
    'near_term':   3,
    'medium_term': 5,
    'long_term':   7,
}
E2_CONFIDENCE_FLOOR = 50   # emits below this confidence do not count toward E2 streak

# Cold-start weights (Gap 11 — Bayesian priors for Day 1)
COLD_START_WEIGHTS: dict[str, dict[str, float]] = {
    'fast_grower':  {'roic': 0.30, 'eps_growth': 0.25, 'peg': 0.20, 'momentum_rsi': 0.15, 'pledge': 0.10},
    'stalwart':     {'roic': 0.35, 'fcf': 0.25, 'eps_growth': 0.15, 'momentum_rsi': 0.15, 'pledge': 0.10},
    'slow_grower':  {'fcf': 0.35, 'dividend': 0.25, 'roic': 0.20, 'pledge': 0.15, 'momentum_rsi': 0.05},
    'cyclical':     {'macro_regime': 0.35, 'roic': 0.20, 'momentum_rsi': 0.25, 'pledge': 0.10, 'fcf': 0.10},
    'turnaround':   {'fcf': 0.30, 'debt_equity': 0.25, 'roic': 0.20, 'pledge': 0.15, 'momentum_rsi': 0.10},
    'asset_play':   {'roic': 0.25, 'fcf': 0.25, 'book_value': 0.25, 'pledge': 0.15, 'momentum_rsi': 0.10},
}
# Source: academic finance literature + documented Lynch/Buffett preference ratios.
# These are priors only — replaced segment-by-segment as observations reach OBSERVATION_THRESHOLD.
# FUNDAMENTAL_WEIGHT_FLOOR applies: combined ROIC+FCF+pledge weight never drops below 0.30.
```

### Regime-read timing (Gap 3 closed; as-of-prediction-time join added in v0.4 — closes GAP-007 / MA-6)

*GAP-006 (missing-run detection) and GAP-007 (regime read race) share one root cause — a time-series read treated as point-in-time with no freshness assertion — and are specified together in this pass per MA-6.*

```python
# get_current_regime in src/data/regime.py
#
# Returns the regime as-of a given prediction timestamp, not "the latest."
# This prevents contaminating the accuracy ledger on transition days.
#
# Join rule: SELECT regime FROM macro_regime
#            WHERE regime_date <= emitted_at::date
#            ORDER BY regime_date DESC LIMIT 1
#
# Freshness guard: if latest regime_date < today - REGIME_STALENESS_DAYS (3),
#   set regime_stale = True on the prediction and surface a staleness warning.
#   Do NOT default to 'RISK_ON' when stale — fail visibly, not silently.
#
# Cache: singleton per calendar day, keyed by date. Re-fetch if emitted_at.date
# differs from cache key (handles intra-day regime updates correctly).

REGIME_STALENESS_DAYS = 3
```

The `get_supabase_client()` singleton (in `src/config.py`) is unchanged. The v0.4 change is to `get_current_regime()`: it now takes an `emitted_at` argument and joins the regime row whose `regime_date <= emitted_at::date` (DESC, LIMIT 1) — the as-of semantics — instead of always returning the newest row. The v0.3 silent fallback to `'RISK_ON'` when the table is empty/stale is **removed**: the prediction is flagged `regime_stale = True` and a staleness warning surfaces, failing visibly rather than tagging a prediction with a wrong default.

Rationale: macro regime does not change intraday, so per-calendar-day caching still holds; but a prediction made on a regime-transition day (or before today's cron fires) must inherit the regime that was in force *at emit time*, not whatever the latest row happens to be — otherwise both regime segments get contaminated (Guard 1).

### Signal emit flow

`src/signals/engine.py`:
1. Read current regime via `get_current_regime()` (cached singleton)
2. Derive `cycle_phase` via `cycle_phase.derive_cycle_phase()`
3. Compute `accuracy_streak_flag` via `ledger.compute_streak_flag()`

**Step 3b — Apply emit-time streak discount (Guard 2 — Soros) [added in v0.4, closes GAP-004 / MA-4]:**
```
    if compute_streak_flag(instrument_id, lynch_class, regime):
        confidence = confidence * STREAK_DISCOUNT_FACTOR  # 0.7
        # Note: discount applied BEFORE Kelly and BEFORE ledger write.
        # The ledger SQL also applies the discount (secondary check), but
        # the primary guard fires here at emit time.
```
*Rationale: in v0.3 the discount fired only at quarterly ledger aggregation, so at a reflexive cycle peak the engine sized UP exactly when Guard 2 was designed to size DOWN. The discount now fires at the live emit, before calibration and Kelly consume the confidence.*

4. Load active weights: query `signal_weights` WHERE status='ACTIVE' AND lynch_class=X AND regime=Y — if no ACTIVE rows, fall back to `COLD_START_WEIGHTS[lynch_class]`
5. Enforce `FUNDAMENTAL_WEIGHT_FLOOR` before scoring
6. Emit signal with all context fields (confidence already streak-discounted per step 3b)
7. Write to `accuracy_predictions` (every emit, no exceptions)

### Weight proposal review notification (Gap 2 closed)

`pages/signals.py` — at top of page, before signal list:

```python
proposed = db.table('signal_weights').select('id').eq('status','PROPOSED').execute()
if proposed.data:
    st.warning(
        f"⚠ {len(proposed.data)} signal weight proposal(s) awaiting your review. "
        "Visit the Accuracy tab → Weight Proposals to review.",
        icon="🔔"
    )
```

This is a passive notification banner — it does not auto-apply anything. Human review remains the gate.

The same banner runs in `pages/path.py` (top of page, before recommendation list) — Tarun may navigate directly to the Path page without visiting Signals:

```python
proposed = db.table('signal_weights').select('id').eq('status','PROPOSED').execute()
if proposed.data:
    st.warning(
        f"⚠ {len(proposed.data)} signal weight proposal(s) awaiting review. "
        "Accuracy tab → Weight Proposals.",
        icon="🔔"
    )
```

### Weight review process (`WEIGHT_REVIEW_PROCESS.md`)

Committed to repo root at G0. Content:

- **Cadence:** Quarterly (every ~90 days)
- **Reviewer:** Tarun Kochhar
- **Trigger:** Any `signal_weights` row with `status = 'PROPOSED'` and `observation_n ≥ 30`
- **Staleness backstop:** If oldest PROPOSED row age > 90 days, Accuracy tab shows an amber warning: "Weight proposals pending for N days — quarterly review overdue"
- **Approval criteria:** `observation_n ≥ 30` AND `|proposed_weight − current_weight| ≥ PROPOSAL_MIN_DELTA (0.03)`
- **Approval action:** Update `status = 'ACTIVE'`, set `approved_at = now()`, `approved_by = 'tarun'`
- **Rejection action:** Update `status = 'REJECTED'` — proposal logged but never applied
- **Effect:** Signal engine reads only `ACTIVE` weights. No weight change is live until this step.

---

### 5.7 Signal Arbitration (arbitration.py)

*Added in v0.4 — closes GAP-003 (R1) / MA-13 dependency chain step 1. This is the FIRST link in the P0 dependency chain: arbitration → confidence → calibration → Kelly. Whatever arbitration emits determines what is logged to the accuracy ledger, which feeds calibration (5.8), which feeds Kelly (Section 6).*

**File:** src/signals/arbitration.py

**Purpose:** When the signal engine produces conflicting directional signals for the same instrument
(e.g., a BULL from a momentum signal and a BEAR from a fundamental signal), arbitration
determines what — if anything — is emitted and logged to the accuracy ledger.

**Inputs:**
- signals: List[SignalEmit] — all signals for this instrument this cycle
- weights: Dict[str, float] — ACTIVE weight per signal_name for this segment

**Rule:**
1. Separate signals into BULL and BEAR buckets.
2. Compute weighted_bull = sum(confidence_i * weight_i) for all BULL signals.
3. Compute weighted_bear = sum(confidence_j * weight_j) for all BEAR signals.
4. If |weighted_bull - weighted_bear| < ARBITRATION_MARGIN: suppress emission (no row logged).
5. Else: emit the direction with the higher weighted score. Emitted confidence = winning side score normalised to [0,100].

**Constants (constants.py):**
ARBITRATION_MARGIN = 15.0  # suppress emission if weighted scores are within 15 points

**Trace matrix:** C-ARB — test_arbitration_suppression + test_arbitration_bull_wins + test_arbitration_bear_wins

### 5.8 Confidence Calibration

*Added in v0.4 — closes GAP-002 (R1) / MA-13 dependency chain step 3. Sits between arbitration's emitted confidence (5.7) and Kelly's `p` consumption (Section 6).*

**Why:** confidence is a composite score, not a calibrated probability. Feeding it directly to
Kelly as p systematically overestimates win probability. The calibration map corrects this.

**Method:** Per-segment empirical reliability binning.
1. Group historical accuracy_predictions by (lynch_class, regime, confidence_decile).
2. For each bin, compute empirical_p = count(is_correct=TRUE) / count(*).
3. Map: p = empirical_p for the bin matching this prediction's confidence.

**Cold-segment fallback:** If a segment has < OBSERVATION_THRESHOLD (30) observations,
p = min(confidence / 100, measured_hit_rate_for_segment). This is fail-conservative:
never assume p > measured hit rate.

**Calibration update:** Run after each quarterly weight review. Store calibration bins in
a new table (add at G1): calibration_bins(lynch_class, regime, confidence_lower, confidence_upper, empirical_p).
At G0: cold-start fallback applies to all segments (< 30 obs by definition).

**Cold-segment-forever note (MA-14 — Lynch/Marks minority view):** with 24 segments and a single
low-volume user, most cells may never reach 30 observations. This is acceptable and intended:
the cold-segment fallback above holds priors indefinitely for such cells. Build the calibration
structure (the slot, the table, the binning) but do not assume the ledger fills. Pair with GAP-015
shrinkage so the weight transition and the calibration transition do not both jump at observation 30.

---

## Section 6 — Path Optimizer Design

### Kelly sizing

`src/portfolio/optimizer.py`:

```python
PORTFOLIO_VALUE = 725000   # ₹7.25L GSI equity tranche (from constants.py)
MAX_POSITION_PCT = 0.10    # ₹72,500
MIN_POSITION_PCT = 0.01    # ₹7,250
SECTOR_CAP_PCT   = 0.35
CASH_FLOOR_PCT   = 0.10

# kelly_position_size in src/path/optimizer.py
#
# Kelly criterion: f = p - q/b
#   p = calibrated win probability (from calibration_bins, or cold fallback)
#   q = 1 - p
#   b = magnitude_target / downside_target  (true net odds = win leg / loss leg)
#
# CRITICAL: if downside_target is None (signal predates schema), return 0 — no position.
# Path page shows direction+confidence only when position_size == 0.

def kelly_position_size(p: float, magnitude_target: float,
                        downside_target: float | None,
                        portfolio_value: float) -> float:
    if downside_target is None or downside_target <= 0:
        return 0  # cannot compute without loss leg — show direction only

    b = magnitude_target / downside_target  # true net odds
    q = 1.0 - p
    full_kelly = p - (q / b)

    if full_kelly <= 0:
        return 0  # negative or zero edge — no position

    quarter_kelly = full_kelly * QUARTER_KELLY_FRACTION  # 0.25

    raw = quarter_kelly * portfolio_value
    return max(0, min(MAX_POSITION_PCT * portfolio_value, raw))
    # Note: MIN_POSITION_PCT floor removed — zero-edge bets return 0, not MIN
```

**v0.4 amendments to this function (closes GAP-001, GAP-002, GAP-013, R3 MA-3):**
- `b` is now true net odds = `magnitude_target / downside_target`, not the dimensionally-wrong `b = magnitude_target` of v0.3. Requires migration 0012 (`downside_target` column).
- **`downside_target` source rule (MA-3):** the signal emits a stop-loss fraction as its loss leg; if the signal does not emit one, default to `ATR(14) / price`. Stored on `accuracy_predictions.downside_target` (migration 0012). When NULL (signal predates the column), this function returns 0 and the Path page shows direction + confidence only — never a rupee amount.
- `p` is the **calibrated** probability from Section 5.8, not raw `confidence / 100`. The caller passes the calibrated value; this function no longer divides confidence by 100 itself.
- `MIN_POSITION_PCT` floor is **removed** from the return (GAP-013): zero/negative-edge bets now return 0 and drop from the recommendation list, rather than being forced into a 1% position. The `MIN_POSITION_PCT` constant remains in `constants.py` but is no longer applied as a floor inside `kelly_position_size` — it may only floor positions that have already cleared the edge test (full_kelly > 0).

### EXIT trigger conditions (Gap 4 closed)

The path optimizer emits EXIT recommendations under exactly four conditions:

| # | Condition | Signal |
|---|---|---|
| E1 | Position size drifted outside Kelly band (current_value > max_position × 1.1 OR < min_position × 0.9) | Rebalance — trim/top-up |
| E2 | Signal direction has flipped from BULL to BEAR on N consecutive emits (confidence ≥ 50 only) where N is bucket-aware: near_term=3, medium_term=5, long_term=7 | Exit — signal reversal |
| E3 | Latest magnitude_target dropped below 3% (signal no longer asymmetric enough) | Exit — insufficient edge |
| E4 | Adding this position would breach sector allocation cap (35%) for the bucket | Exit or block — sector cap |

EXIT signals are logged to `trade_outcomes` with an `exit_trigger` column (E1–E4). Trigger E2 thresholds and constants live in `constants.py`:

```python
E2_CONSECUTIVE_THRESHOLD = {
    'near_term':   3,   # 3 trading days — fast exit for short horizon
    'medium_term': 5,   # 1 trading week buffer
    'long_term':   7,   # 1.5 weeks — long-term holdings tolerate short noise
}
E2_CONFIDENCE_FLOOR = 50  # low-confidence emits do not count toward E2 streak
```

**EXIT Trigger E2 — Sustained Deterioration (redesigned in v0.4 — closes GAP-005 / MA-5):**

```
EXIT Trigger E2 — Sustained Deterioration (bucket-aware + uncertainty path):

PRIMARY path (confident deterioration):
  consecutive_bear_emits >= E2_CONSECUTIVE_THRESHOLD[bucket]  # {near_term:3, medium:5, long:7}
  AND confidence >= E2_CONFIDENCE_FLOOR  # 50

UNCERTAINTY path (uncertain deterioration — new):
  consecutive_bear_emits >= E2_CONSECUTIVE_THRESHOLD[bucket] * 2  # double threshold
  AND confidence < E2_CONFIDENCE_FLOOR
  AND instrument.close < instrument.ma_200d  # only when below 200-day MA

Rationale: low-confidence BEAR emits during a decline are signal, not noise.
The original single-floor design suppressed the exit exactly when capital
preservation matters most. The uncertainty path uses a higher streak bar
(double threshold) as the noise filter, and adds the 200-day MA as a
second confirming condition, so truly noisy signals below-floor don't trigger.
```

In v0.3 a below-floor BEAR emit always reset the streak — meaning the exit self-suppressed precisely when the model was most uncertain and the market was deteriorating fastest. The redesign splits the floor's two jobs: the PRIMARY path keeps the noise filter for confident reversals; the UNCERTAINTY path lets low-confidence bear runs feed a separate exit, gated by a doubled streak bar AND the 200-day MA, so genuine deterioration is no longer silenced.

### Bucket-aware ranking

Each signal is scored against the bucket profile before surfacing:

```python
def rank_for_bucket(signal, bucket: str) -> float | None:
    horizon_map = {
        'near_term':   (90, 365),
        'medium_term': (365, 1825),
        'long_term':   (1825, None),
    }
    lo, hi = horizon_map.get(bucket, (0, None))
    if signal.horizon_days < lo:
        return None    # not surfaced for this bucket
    if hi and signal.horizon_days > hi:
        return None
    return signal.confidence * signal.magnitude_target
```

Emergency bucket (₹5L) receives no stock signals — cash-only, not in optimizer scope.

---

## Section 7 — Accuracy Feedback Loop Design

### Cold-start (Day 1, empty ledger) — Gap 11 closed

On Day 1, `signal_weights` has no ACTIVE rows. The signal engine falls back to `COLD_START_WEIGHTS` in `constants.py` (documented in Section 5). These are segment-level Bayesian priors — not global weights, because the 24-segment architecture requires segment-level defaults.

The priors are:
- Anchored in documented investment principles (Lynch's PEG priority for fast growers; Buffett's ROIC priority for stalwarts)
- Segment-specific, not a single global default
- Automatically superseded segment-by-segment as each cell reaches 30 observations
- `FUNDAMENTAL_WEIGHT_FLOOR` applies to priors too — if any prior set produces combined fundamental weight < 0.30, it is adjusted up before use

Cold-start is transparent in the UI: a label on the signals page reads "Signal weights: using priors (N observations)" until the first ACTIVE weight is approved.

### Prediction logging

Every signal emit (Section 5, step 7) writes one row to `accuracy_predictions`. No exceptions, no batching — logged synchronously in the same DB call as the signal response. This ensures the accuracy ledger is never ahead or behind the signal engine.

### Outcome resolution

GHA cron job `ingest.yml` runs at 5:45 PM IST on weekdays. After OHLCV ingest, a second step runs `scripts/resolve_outcomes.py`:

1. Query `accuracy_predictions` WHERE `outcome_id IS NULL` AND `emitted_at + horizon_days ≤ today`
2. For each unresolved prediction, fetch the OHLCV return over the horizon window
3. Write to `accuracy_outcomes` (direction, actual_return, peak_return_pct, is_correct)
4. Back-fill `accuracy_predictions.outcome_id`
5. Trigger `ledger.update_segment()` for the affected segment cell

### Weight proposal generation

After any `update_segment()` call:
- Query the cell's current observation count
- If `n_observations ≥ 30` AND proposed weight delta ≥ `PROPOSAL_MIN_DELTA`:
  - Write to `signal_weights` with status='PROPOSED', observation_n, proposed_at
  - Do NOT update any ACTIVE weight
  - Notification banner in UI (Section 5) surfaces it to Tarun on next visit

### Quarterly review gate

Once per quarter, Tarun reviews all PROPOSED rows. For each:
- Approve → update status='ACTIVE', approved_at, approved_by='tarun'
- Reject → update status='REJECTED'

Signal engine reads only ACTIVE rows. No weight change takes effect without this step. This is governance, not automation.

---

## Section 8 — Quality Standards

### Async startup ingest (Gap 8 closed)

Ingest scripts (`scripts/ingest_bhavcopy.py`, etc.) are **separate scheduled jobs** — they do not run on app startup. The Streamlit app starts in under 3 seconds regardless of ingest state. It queries what is in Supabase; if data is stale, it shows a staleness indicator.

Ingest status tracking:
```sql
CREATE TABLE ingest_status (
  id          SERIAL PRIMARY KEY,
  script_name VARCHAR(100) NOT NULL,
  run_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  status      VARCHAR(10) NOT NULL CHECK (status IN ('OK','FAILED','PARTIAL')),
  error_msg   TEXT,
  rows_written INT
);
```

`pages/data_viewer.py` reads the latest row for each script on page load and shows a warning if any script's last run was FAILED or if `run_at < today at 6 PM` (i.e., today's ingest hasn't completed).

### Supabase connection singleton (Gap 8 closed)

`src/config.py` provides a module-level singleton (see Section 5). Key rules:
- Only `get_supabase_client()` is called — never `create_client()` directly in application code
- Connection is reused across all pages in the Streamlit session
- Uses SUPABASE_URL + SUPABASE_ANON_KEY (anonymous) for reads; SERVICE_KEY only in ingest scripts

### Test coverage targets

| Layer | Tests | Coverage target |
|---|---|---|
| Migrations | 1 smoke test per migration (table exists, columns correct, CHECK passes) | 100% |
| cycle_phase.py | 10 unit tests covering all PHASE_RULES entries | 100% |
| constants.py | 3 tests: FUNDAMENTAL_WEIGHT_FLOOR enforced, COLD_START_WEIGHTS sum to 1.0 per segment, SEBI_DISCLAIMER non-empty | 100% |
| signal engine emit | 5 integration tests: cold-start path, streak flag, regime fallback, floor enforcement, prediction logged | 100% critical paths |
| path optimizer | 4 tests: all 4 EXIT conditions trigger, Kelly size within bounds | 100% |
| Outcome resolution | 3 tests: correct/incorrect outcome, peak return logged, streak flag updated | 100% |

G0 gate requires 6 smoke tests to pass. G1 gate requires full regression suite.

### .claude/rules/ enforcement

Every Claude session in the AlphaVeda repo reads `CLAUDE.md` which includes:
```
include .claude/rules/SEBI_COMPLIANCE.md
include .claude/rules/COMMERCIAL_GATE.md
include .claude/rules/DATA_SOURCES.md
```

These files are committed at G0 before any code. Content:
- `SEBI_COMPLIANCE.md`: SEBI disclaimer pinned on every page; no buy/sell recommendations phrased as advice; no SEBI-RIA content
- `COMMERCIAL_GATE.md`: CommercialLicenseError rules; yfinance blocked when ALPHAVEDA_COMMERCIAL=true; FMP at first non-self subscriber
- `DATA_SOURCES.md`: licensed source table; BSE free stack is default; upgrade triggers

### SLAs and Performance Targets

All targets are set for Streamlit running on Mac local dev + Supabase free tier (ap-south-1, 500 MB, shared compute). No CDN, no dedicated DB compute. Breach actions are lightweight — the product is single-user in v1, so SLA breaches surface as manual investigation tasks, not incident pages.

| Metric | Target | Measurement | Breach action |
|---|---|---|---|
| App cold start time (first page load after `streamlit run app.py`) | ≤ 5 seconds to interactive UI (SEBI disclaimer visible, nav rendered) | Manual timer from `streamlit run` output to browser tab interactive; logged in test notes at G0 smoke test | Audit startup imports — move heavy provider imports to lazy-load inside page functions; check Supabase singleton init latency |
| Page render time — `data_viewer.py` with OHLCV candlestick chart (90 days of data, 1 instrument) | ≤ 4 seconds from page navigation click to chart rendered | Browser DevTools network waterfall; timed in G1 regression run against a seeded 90-day OHLCV dataset | Profile Plotly render vs Supabase query time; if query > 1.5 s, add `(instrument_id, trade_date)` index (already in 0002 UNIQUE constraint); if Plotly > 2 s, downsample to weekly for initial render |
| Full Bhavcopy ingest job completion (NSE + BSE, ~2,000 instruments, one trading day) | ≤ 8 minutes end-to-end in GHA runner (ubuntu-latest, free tier) | GHA workflow step duration logged in `ingest_status` table (`run_at` → step end delta); visible in GHA Actions tab | Batch inserts in chunks of 500 rows using Supabase `upsert`; if still breaching, split NSE and BSE into parallel GHA jobs |
| Signal emit latency per instrument (single instrument, regime cached, weights loaded) | ≤ 800 ms from `engine.emit(instrument_id)` call to `accuracy_predictions` row confirmed written | Unit test timer in `test_smoke.py`; measured against seeded DB with 1 ACTIVE weight row | Profile DB round-trips: regime read (should be cached), streak flag query (add index on `accuracy_outcomes.prediction_id`), weight load query |
| Supabase read query p95 latency (simple SELECT with one WHERE clause, e.g., latest regime row) | ≤ 600 ms from Supabase client `.execute()` call to Python dict returned | Logged via `time.perf_counter()` wrapper in `get_current_regime()` during G1 regression run; p95 over 20 successive calls | If latency > 600 ms consistently: check ap-south-1 region routing from Mac; confirm SUPABASE_ANON_KEY is project-local not global; enable Supabase connection pooling (PgBouncer, free tier supports it) |
| GHA cron job start-to-finish time (ingest + outcome resolution + ledger update) | ≤ 12 minutes total wall-clock time in GHA free-tier runner | GHA workflow `duration` field on the completed run; visible in Actions tab | If breaching: separate ingest and outcome resolution into two sequential jobs; add `continue-on-error: false` so partial runs surface immediately rather than silently completing |
| Stale data warning latency (time from `ingested_at` threshold breach to amber badge visible in UI) | ≤ 1 page load (the staleness check runs on every `data_viewer.py` render, not cached) | Manual verification: set `ingested_at` to yesterday in test DB row, load data_viewer page, confirm amber STALE badge appears without a second reload | If badge not appearing: verify `ingest_status` query in `data_viewer.py` is reading `run_at` not a cached value; confirm Streamlit is not caching the staleness query via `@st.cache_data` |

### 8.5 Commercial Gate (ALPHAVEDA_COMMERCIAL)

*Added in v0.4 — closes GAP-011 + GAP-012 (R1) / MA-8. Enforcement code is pre-launch, but the gate DESIGN is specified now per the Constraint Enforcer / Sundaram / Varghese condition: retrofitting a fail-closed gate after the data layer is built is far more expensive.*

#### Commercial State Detection

NEVER derive commercial state from a manual env flag. Derive from data:

```python
# In app startup (app.py) and ingest script (ingest.py):
from supabase import create_client
def is_commercial() -> bool:
    result = supabase.table('waitlist').select('id').not_.is_('converted_at', None).limit(1).execute()
    return len(result.data) > 0
```

Fail-closed: if Supabase is unreachable at startup, assume commercial=True (block yfinance).

#### What changes at commercial=True

| Component | Personal (commercial=False) | Commercial (commercial=True) |
|---|---|---|
| Data source | yfinance + BSE + Bhavcopy | FMP ($14/mo) + BSE + Bhavcopy |
| Layer 4 output | Rupee Kelly amounts | Direction + confidence only (no rupee) |
| SEBI framing | "Signal X is BULLISH for Y" | Same — never imperative BUY |
| CommercialLicenseError | Silently blocked in DataProvider | Raised if yfinance called |

#### SEBI substance test (required in CI)

The C9 test asserts SEBI disclaimer *presence*. Add C9b — substance test:
- Assert no output contains imperative language: "BUY", "SELL", "invest in", "put money"
- Assert Layer 4 labels read: "BULLISH signal" / "BEARISH signal" / "No signal" (never rupee amount when commercial=True)
- Assert disclaimer text includes: "research purposes only" and "not investment advice"

**Suppression-as-deliberate-state (Tanvi Rao UX note):** when the gate fires and rupee amounts are suppressed, the Path page transitions from "buy ₹72,500 of X" to "X is bullish." This must be presented as a designed, intentional state — not a degraded fallback — so the first paying subscriber's first impression is not a feature that vanished. The `licence_class` column (migration 0011) lets a query answer "is any commercially-served row from a personal-only provider," supporting the fail-closed check.

---

## Section 9 — Condition-to-Artifact Trace Matrix

**Permanent structural fix for council gap accumulation (Root Cause 3).**

Every council condition must map to a file, artifact, and test before implementation starts. If any row has no artifact, that condition is not done.

| # | Council Condition | Seat | File | Artifact | Test |
|---|---|---|---|---|---|
| C1 | Fundamentals weight floor enforced | Buffett | `constants.py` | `FUNDAMENTAL_WEIGHT_FLOOR = 0.30` | `test_floor_enforced()` |
| C2 | Quarterly review notification — banner on signals + path pages; inline review UI on Accuracy tab; WEIGHT_REVIEW_PROCESS.md committed | Munger | `pages/signals.py`, `pages/path.py`, `pages/accuracy.py`, `WEIGHT_REVIEW_PROCESS.md` | Banner code in 2 pages; Accuracy tab shows PROPOSED rows with approve/reject; process doc | `test_review_banner_shown()`, `test_review_banner_on_path_page()`, `test_accuracy_tab_review_ui()` |
| C3 | Regime-read timing: startup + 24h cache | Dalio | `src/config.py` | `get_current_regime()` singleton | `test_regime_cached()` |
| C4 | EXIT trigger conditions defined; E2 bucket-aware (3/5/7) + confidence floor ≥ 50 | Druckenmiller | `src/portfolio/optimizer.py` + `constants.py` | E1–E4 trigger table, `E2_CONSECUTIVE_THRESHOLD`, `E2_CONFIDENCE_FLOOR` | `test_exit_e1()` … `test_exit_e4()`, `test_e2_confidence_floor()`, `test_e2_bucket_threshold()` |
| C5 | cycle_phase derivation module | Marks | `src/accuracy/cycle_phase.py` | `derive_cycle_phase()` function | `test_all_phase_rules()` |
| C6 | Streak detection N + discount factor | Soros | `constants.py` + `src/accuracy/ledger.py` | `STREAK_WINDOW`, `STREAK_DISCOUNT_FACTOR`, `compute_streak_flag()` | `test_streak_flag_fires_at_n()` |
| C7 | Lynch classification CHECK in migration | Lynch | `migrations/0001_instruments.sql` | CHECK constraint 6 values | `test_invalid_class_rejected()` |
| C8 | Async startup ingest + singleton + error surfacing | Systems Reliability | `src/config.py`, `scripts/`, `pages/data_viewer.py` | `get_supabase_client()`, `ingest_status` table, staleness badge | `test_stale_warning_shown()` |
| C9 | SEBI disclaimer pinned; `.claude/rules/` created | Constraint Enforcer | `app.py`, `.claude/rules/` | Fixed-bottom HTML block, 3 rule files | `test_disclaimer_in_every_page()` |
| C10 | Waitlist: price_feedback + referred_by | Wealth & Revenue | `migrations/waitlist.sql` | 2 columns with CHECK | `test_waitlist_columns_exist()` |
| C11 | Cold-start Bayesian prior for empty ledger | Synthesis Chair | `constants.py` | `COLD_START_WEIGHTS` dict | `test_cold_start_weights_sum_to_1()`, `test_floor_applies_to_priors()` |
| C12 | regime_tag on every accuracy_predictions row | Dalio (schema) | `migrations/0007_accuracy_predictions.sql` | NOT NULL column | `test_prediction_without_regime_rejected()` |
| C13 | cycle_phase in accuracy ledger schema | Marks (schema) | `migrations/0007_accuracy_predictions.sql` | NOT NULL CHECK column | `test_invalid_phase_rejected()` |

**Review protocol (permanent, applies to every future design doc):**

1. **Strategic review** (concept level) — vote on approach options. Output: locked decisions.
2. **Architecture review** (spec level, Section 1) — review file structure and layer design. Output: 7 schema conditions.
3. **Trace matrix gate** (between Section 1 and Sections 2-8) — map all conditions to artifacts. Any unmapped condition is a mandatory gap before proceeding.
4. **Implementation review** (after Sections 2-8) — council reviews the completed trace matrix. Sections may not proceed to writing-plans until every row has an artifact.

This protocol replaces the current pattern of discovering gaps at each review stage.

---

## G0 Exit Gate — Updated (v0.4)

*Upgraded in v0.4 — closes MA-12. The original gate ("6/6 + 10 seeds + ingest_status") could not catch the defects R1 found. The gate now tests the found defects directly.*

Original: pytest 6/6 + 10 seed instruments + ingest_status populated

Updated — ALL of the following must pass:

1. pytest 6/6 (existing tests)
2. test_signal_weights_single_active: assert no (lynch_class, regime, signal_name) tuple has 2+ ACTIVE rows
3. test_missing_run_detection: stop ingest, advance mock clock, assert data_viewer renders staleness banner
4. test_calibration_cold_start: assert p <= confidence/100 for all cold segments (p never inflated above raw confidence)
5. test_sebi_substance: assert no UI text contains imperative buy/sell language
6. test_kelly_no_rupee_without_downside: create a prediction with downside_target=NULL, assert Path page shows no rupee amount
7. test_disclaimer_nonocculsion: assert last interactive element in Path page is not covered by .sebi-disclaimer bar (CSS padding-bottom check)
8. 10 seed instruments loaded across ≥3 Lynch classifications
9. ingest_status has ≥1 OK row
10. All 2 new migrations (0011, 0012) applied without error

---

## v0.4 Migration Addenda (Section 2 supplement)

*Migrations are the single source of truth (MA-7 / GAP-008). Section 2's inline SQL above reflects the original 0001–0011 set; v0.4 adds two migrations. The live files use date-prefixed names so they sort after the existing `20260621*` set.*

**0011 — `20260622100011_schema_fixes.sql`** (batched per MA-9):
- GAP-009: partial unique index `signal_weights_one_active_per_segment` on `(lynch_class, regime, signal_name) WHERE status='ACTIVE'`; `approve_signal_weight(p_id INT)` atomic demote-then-promote; `status` CHECK extended to include `'SUPERSEDED'`.
- Imran idempotency: `accuracy_outcomes` gains `UNIQUE (prediction_id)`.
- GAP-010 pre-work: `ohlcv.circuit_flag BOOLEAN DEFAULT FALSE`, `ohlcv.deliverable_volume BIGINT`.
- GAP-012 pre-work: `ohlcv.licence_class TEXT CHECK (personal|commercial|open) DEFAULT 'personal'`.

**0012 — `20260622100012_downside_target.sql`**:
- GAP-001: `accuracy_predictions.downside_target NUMERIC(6,4) CHECK (>0 AND <=1.0)` — Kelly loss leg.

**Reconciliation notes (MA-7):** the live `0009` UNIQUE includes `status` (the GAP-009 defect) — 0011's partial index is the fix; the live design-doc inline 0009 SQL above still shows the original UNIQUE and is retained for history with this note flagging it superseded. `signal_weights` has no `updated_at` column, so `approve_signal_weight` stamps `approved_at`; `signal_weights.id` is `SERIAL`, so the function takes `p_id INT` (not UUID).

**GAP-010 is a HARD pre-G1 gate** (Buffett, Bhattacharya): circuit-locked / illiquid prints must be excluded from outcome scoring before the learning loop runs, or `peak_return_pct` corruption compounds quarterly. The 0011 columns are the schema pre-work; the `resolve_outcomes.py` exclusion logic is the G1 enforcement.

---

*Design doc version 0.4 — Sections 1–9 + G0 gate + commercial gate + migration addenda complete. Status: AMENDED POST-R1+R3-COUNCIL.*
