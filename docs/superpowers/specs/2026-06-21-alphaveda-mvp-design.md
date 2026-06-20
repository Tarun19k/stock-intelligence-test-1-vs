# AlphaVeda MVP Design
**Date:** 2026-06-21  
**Status:** READY FOR USER REVIEW — Sections 1–9 complete; all 11 council gaps closed  
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
  ),
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
  notes           TEXT
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
  regime_tag          VARCHAR(20) NOT NULL REFERENCES macro_regime(regime),
  lynch_class         VARCHAR(20) NOT NULL CHECK (
    lynch_class IN ('fast_grower','stalwart','slow_grower',
                    'cyclical','turnaround','asset_play')
  ),
  cycle_phase         VARCHAR(20) NOT NULL CHECK (
    cycle_phase IN ('early_bull','mid_bull','late_bull',
                    'early_bear','mid_bear','late_bear')
  ),
  accuracy_streak_flag BOOLEAN NOT NULL DEFAULT false,
  outcome_id          BIGINT REFERENCES accuracy_outcomes(id)  -- back-filled on resolution
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

### Regime-read timing (Gap 3 closed)

Regime is read **once at startup**, then refreshed **once per 24-hour batch** (not per signal emit).

`src/config.py`:
```python
_supabase: Client | None = None
_regime_cache: dict | None = None
_regime_cache_date: date | None = None

def get_supabase_client() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    return _supabase

def get_current_regime() -> str:
    global _regime_cache, _regime_cache_date
    today = date.today()
    if _regime_cache is None or _regime_cache_date != today:
        result = get_supabase_client().table('macro_regime') \
            .select('regime').order('regime_date', desc=True).limit(1).execute()
        _regime_cache = result.data[0]['regime'] if result.data else 'RISK_ON'
        _regime_cache_date = today
    return _regime_cache
```

Rationale: macro regime does not change intraday. Per-emit reads add latency and burn Supabase free-tier request quota.

### Signal emit flow

`src/signals/engine.py`:
1. Read current regime via `get_current_regime()` (cached singleton)
2. Derive `cycle_phase` via `cycle_phase.derive_cycle_phase()`
3. Compute `accuracy_streak_flag` via `ledger.compute_streak_flag()`
4. Load active weights: query `signal_weights` WHERE status='ACTIVE' AND lynch_class=X AND regime=Y — if no ACTIVE rows, fall back to `COLD_START_WEIGHTS[lynch_class]`
5. Enforce `FUNDAMENTAL_WEIGHT_FLOOR` before scoring
6. Emit signal with all context fields
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

def kelly_position_size(confidence: int, magnitude_target: float, portfolio_value: float) -> float:
    """Quarter-Kelly: f = (p - q/b) × 0.25"""
    p = confidence / 100
    q = 1 - p
    b = magnitude_target if magnitude_target > 0 else 0.05   # floor at 5%
    full_kelly = (p - q / b)
    quarter_kelly = max(0, full_kelly * 0.25)
    raw = portfolio_value * quarter_kelly
    return max(MIN_POSITION_PCT * portfolio_value,
               min(MAX_POSITION_PCT * portfolio_value, raw))
```

### EXIT trigger conditions (Gap 4 closed)

The path optimizer emits EXIT recommendations under exactly four conditions:

| # | Condition | Signal |
|---|---|---|
| E1 | Position size drifted outside Kelly band (current_value > max_position × 1.1 OR < min_position × 0.9) | Rebalance — trim/top-up |
| E2 | Signal direction has flipped from BULL to BEAR on 3 consecutive emits for the same instrument | Exit — signal reversal |
| E3 | Latest magnitude_target dropped below 3% (signal no longer asymmetric enough) | Exit — insufficient edge |
| E4 | Adding this position would breach sector allocation cap (35%) for the bucket | Exit or block — sector cap |

EXIT signals are logged to `trade_outcomes` with an `exit_trigger` column (E1–E4). Trigger E2 requires 3 consecutive BEAR emits — not a single flip. This prevents noise-driven exits.

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

---

## Section 9 — Condition-to-Artifact Trace Matrix

**Permanent structural fix for council gap accumulation (Root Cause 3).**

Every council condition must map to a file, artifact, and test before implementation starts. If any row has no artifact, that condition is not done.

| # | Council Condition | Seat | File | Artifact | Test |
|---|---|---|---|---|---|
| C1 | Fundamentals weight floor enforced | Buffett | `constants.py` | `FUNDAMENTAL_WEIGHT_FLOOR = 0.30` | `test_floor_enforced()` |
| C2 | Quarterly review notification mechanism | Munger | `pages/signals.py` | Warning banner on PROPOSED count > 0 | `test_review_banner_shown()` |
| C3 | Regime-read timing: startup + 24h cache | Dalio | `src/config.py` | `get_current_regime()` singleton | `test_regime_cached()` |
| C4 | EXIT trigger conditions defined | Druckenmiller | `src/portfolio/optimizer.py` | E1–E4 trigger table + `emit_exit()` | `test_exit_e1()` … `test_exit_e4()` |
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

*Design doc version 0.2 — Sections 1–9 complete. Status: READY FOR USER REVIEW.*
