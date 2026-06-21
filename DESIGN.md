# AlphaVeda — Developer Design Reference

**Version:** 0.3 (post-council, all 13 conditions closed)
**Date:** 2026-06-21
**Status:** READY FOR BUILD — G0 gate open

---

## 1. Product Summary

AlphaVeda is a predictions and accuracy tool for Indian equity portfolios. It identifies the right
path to gain returns across four portfolio buckets (emergency, near-term, medium-term, long-term)
for a single user profile (Tarun, v1). All three pillars are co-equal: data quality and
interpretation, directional signal generation, and path optimization with accuracy self-improvement.

AlphaVeda is NOT a SEBI-registered investment advisor (RIA), does NOT give investment advice, and
does NOT auto-trade or auto-apply any weight changes. It is a research and analysis tool only.
Every signal weight change requires explicit human approval before it becomes active.

---

## 2. Five-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 5 — PRESENTATION                                         │
│  Streamlit app · 4 pages · SEBI disclaimer pinned (fixed HTML) │
│  Data viewer · Signal display · Path recommendations · Accuracy │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 4 — PATH OPTIMIZER                                       │
│  Bucket-aware ranking · Quarter-Kelly sizing · EXIT triggers    │
│  E1–E4 · Max position 10% · Sector cap 35% · Cash floor 10%    │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 3 — SIGNAL ENGINE                                        │
│  BULL/BEAR directional signals · Confidence 0–100              │
│  Tagged: regime + Lynch class + cycle_phase                     │
│  Logs to accuracy_predictions on every emit (synchronous)       │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2 — STORAGE (Supabase, ap-south-1, free tier)           │
│  6 core tables · 3 accuracy tables · 24-segment ledger         │
│  All accuracy rows carry: regime_tag + cycle_phase + streak_flag│
├─────────────────────────────────────────────────────────────────┤
│  LAYER 1 — DATA QUALITY                                         │
│  Bhavcopy NSE/BSE · BSE Shareholding · BSE Financials XBRL     │
│  DataProvider ABC · CommercialLicenseError gate                 │
│  Provenance: source + ingested_at on every row                  │
└─────────────────────────────────────────────────────────────────┘
         ↑ accuracy_outcomes feed back to Layer 2 ledger ↑
         ↑ weight proposals surface to Layer 5 quarterly  ↑
```

Layer descriptions:

- **Layer 1 — Data Quality:** Ingests from official sources (Bhavcopy, BSE XBRL, manual macro).
  Every row carries provenance. CommercialLicenseError blocks yfinance in production.
- **Layer 2 — Storage:** Supabase cloud, ap-south-1. Holds 6 core tables, 3 accuracy tables, and
  the 24-segment ledger (query view over accuracy_outcomes).
- **Layer 3 — Signal Engine:** Emits BULL/BEAR signals with confidence scores. Every emit is tagged
  with regime, Lynch classification, and cycle_phase, and logged to accuracy_predictions.
- **Layer 4 — Path Optimizer:** Translates signals into ranked BUY/EXIT/REBALANCE/HOLD actions per
  bucket. Applies Quarter-Kelly sizing and enforces all 4 EXIT trigger conditions.
- **Layer 5 — Presentation:** Streamlit multi-page app. SEBI disclaimer is a fixed-bottom HTML
  block injected before any page content — it cannot be scrolled past or dismissed.

---

## 3. Brand Tokens

Extracted from `/docs/artifacts/2026-06-21/alphaveda-mvp-spec.html` CSS custom properties:

| Token name           | Value                    | Used for                                       |
|----------------------|--------------------------|------------------------------------------------|
| `--ink`              | `#1A1F3C`                | Primary text color, body copy, headings        |
| `--paper`            | `#F5F3EC`                | Page background, light text on dark surfaces   |
| `--gold`             | `#E8A020`                | Brand accent, active tab underline, stat numbers |
| `--gold-faint`       | `#FEF7E0`                | Background for gold-tinted cards and badges    |
| `--gold-bd`          | `rgba(232,160,32,.30)`   | Border color for gold-accent cards             |
| `--surface`          | `#ECEAE0`                | Tab bar background, alternating table rows     |
| `--surface2`         | `#E2E0D4`                | Slightly darker surface for nested elements    |
| `--smoke`            | `#8D90A5`                | Secondary/muted text, labels, subtitles        |
| `--green`            | `#1C6B44`                | Success state, correct outcome pills           |
| `--green-bg`         | `#E6F4ED`                | Background for success/pass badges             |
| `--red`              | `#B5382D`                | EXIT trigger cards, error states               |
| `--navy`             | `#0F1326`                | Code block background, dark panels             |
| `--navy2`            | `#161B2E`                | Tooltip background                             |
| `font-family` (body) | `'Inter', system-ui`     | All body and UI text                           |
| `font-family` (brand)| `'Fraunces', Georgia`    | Logo name, headings, stat numbers              |
| `font-family` (mono) | `'DM Mono', monospace`   | Code, badges, column names, table data         |

---

## 4. Page Map

| Page file              | What it shows                                                                 | DB tables read                                          | Key components                                                                     |
|------------------------|-------------------------------------------------------------------------------|---------------------------------------------------------|------------------------------------------------------------------------------------|
| `pages/data_viewer.py` | 4-tab viewer: Price (candlestick + MA + volume), Fundamentals (8 quarters), Macro (regime badge, RBI/VIX/FII), Buckets (allocation bar vs target) | `ohlcv`, `fundamentals`, `macro_regime`, `portfolio_buckets`, `ingest_status` | Plotly candlestick, 50/200 MA overlay, color-coded fundamentals table, regime badge, STALE badge when ingested_at > 1 trading day |
| `pages/signals.py`     | Current BULL/BEAR signals per instrument with confidence score, Lynch classification badge, and weight-proposal notification banner | `instruments`, `accuracy_predictions`, `signal_weights` | Confidence score display (0–100), Lynch class badge, PROPOSED-count warning banner at page top, cold-start label "using priors (N observations)" |
| `pages/path.py`        | Ranked BUY/EXIT/REBALANCE/HOLD list per bucket with Kelly position size; weight-proposal notification banner | `instruments`, `portfolio_buckets`, `accuracy_predictions`, `signal_weights`, `trade_outcomes` | Bucket selector, ranked action list, kelly_position_size (₹), EXIT trigger label (E1–E4), PROPOSED-count warning banner |
| `pages/accuracy.py`    | 24-segment accuracy ledger (Lynch × regime), weight proposals with approve/reject UI, staleness backstop warning if oldest PROPOSED row > 90 days | `accuracy_predictions`, `accuracy_outcomes`, `signal_weights` | 6×4 segment grid with hit rate + observation count per cell, Weight Proposals table with PROPOSED rows, approve/reject controls |

---

## 5. Data Flow

```
  BSE/NSE Official Sources
  ┌────────────────────────┐
  │  Bhavcopy (daily)      │
  │  BSE Shareholding (qtr)│
  │  BSE Financials XBRL   │
  │  Macro (manual monthly)│
  └──────────┬─────────────┘
             │  scripts/ingest_*.py  (GHA cron 5:45 PM IST weekdays)
             ▼
  ┌────────────────────────────────────────────────┐
  │  Supabase tables (Layer 2)                     │
  │  instruments · ohlcv · fundamentals            │
  │  macro_regime · portfolio_buckets · trade_outcomes │
  └──────────────────┬─────────────────────────────┘
                     │  src/signals/engine.py
                     │  reads: regime (cached 24h) + active weights
                     ▼
  ┌────────────────────────────────────────────────┐
  │  Signal Engine (Layer 3)                       │
  │  Emits BULL/BEAR + confidence + cycle_phase    │
  └──────────┬─────────────────────────────────────┘
             │  synchronous write on every emit
             ▼
  ┌────────────────────────┐
  │  accuracy_predictions  │  ← regime_tag, lynch_class,
  │  (one row per signal)  │    cycle_phase, streak_flag
  └──────────┬─────────────┘
             │  scripts/resolve_outcomes.py (GHA, after OHLCV ingest)
             │  runs when emitted_at + horizon_days ≤ today
             ▼
  ┌────────────────────────┐
  │  accuracy_outcomes     │  ← actual_direction, actual_return,
  │                        │    peak_return_pct, is_correct
  └──────────┬─────────────┘
             │  src/accuracy/ledger.py → update_segment()
             ▼
  ┌────────────────────────────────────────────────┐
  │  24-Segment Ledger                             │
  │  (query view: lynch_class × regime_tag)        │
  │  6 Lynch classes × 4 Dalio regimes = 24 cells  │
  └──────────┬─────────────────────────────────────┘
             │  when n_observations ≥ 30 AND delta ≥ PROPOSAL_MIN_DELTA
             ▼
  ┌────────────────────────┐
  │  signal_weights        │  status = PROPOSED
  │  (weight proposals)    │
  └──────────┬─────────────┘
             │  Tarun reviews quarterly (Accuracy tab)
             │  approve → status = ACTIVE, approved_by = 'tarun'
             ▼
  ┌────────────────────────────────────────────────┐
  │  Signal Engine reads ACTIVE weights on next    │
  │  emit. Falls back to COLD_START_WEIGHTS when   │
  │  no ACTIVE rows exist for segment.             │
  └────────────────────────────────────────────────┘
             │
             ▼
  Path Optimizer (Layer 4) → Streamlit UI (Layer 5)
```

---

## 6. Key Constants

All constants live in `constants.py`. No magic numbers in application code.

| Constant name                | Value                               | Purpose                                                                              |
|------------------------------|-------------------------------------|--------------------------------------------------------------------------------------|
| `FUNDAMENTAL_WEIGHT_FLOOR`   | `0.30`                              | Minimum combined weight for ROIC + FCF + promoter_pledge signals — never overridden by ledger |
| `STREAK_WINDOW`              | `5`                                 | Number of consecutive correct predictions that triggers the counter-cyclical skepticism flag |
| `STREAK_DISCOUNT_FACTOR`     | `0.7`                               | Weight proposals are multiplied by this when accuracy_streak_flag is True             |
| `OBSERVATION_THRESHOLD`      | `30`                                | Minimum observations in a ledger segment before a weight proposal is generated       |
| `PROPOSAL_MIN_DELTA`         | `0.03`                              | Minimum absolute weight change (3%) for a proposal to be written — prevents noise proposals |
| `VIX_CALM_THRESHOLD`         | `18.0`                              | VIX level below which market is treated as "low volatility" in cycle_phase derivation |
| `E2_CONSECUTIVE_THRESHOLD`   | `{'near_term': 3, 'medium_term': 5, 'long_term': 7}` | Bucket-aware count of consecutive BEAR emits required before E2 EXIT fires |
| `E2_CONFIDENCE_FLOOR`        | `50`                                | Emits below this confidence do not count toward the E2 consecutive BEAR streak       |
| `COLD_START_WEIGHTS`         | 6-class dict, each sums to 1.0     | Bayesian priors for Day 1 empty ledger. Segment-specific, not global. Automatically superseded per-segment when n_observations ≥ 30. FUNDAMENTAL_WEIGHT_FLOOR applies to priors. |
| `PORTFOLIO_VALUE`            | `725000`                            | ₹7.25L GSI equity tranche — used as base for Kelly position sizing                   |
| `MAX_POSITION_PCT`           | `0.10`                              | Maximum position size as fraction of portfolio (₹72,500 at current corpus)           |
| `MIN_POSITION_PCT`           | `0.01`                              | Minimum position size (₹7,250); Kelly output is clamped to this floor                |
| `SECTOR_CAP_PCT`             | `0.35`                              | Maximum sector allocation per bucket — E4 EXIT fires if this would be breached       |
| `CASH_FLOOR_PCT`             | `0.10`                              | Minimum cash allocation per bucket — always kept liquid                               |
| `SEBI_DISCLAIMER`            | String constant                     | Single source of truth for disclaimer text; used by the fixed-bottom HTML in app.py  |

---

## 7. G0 Checklist

The following 7 steps must all complete before any G1 work begins.

- [ ] Run migrations 0001–0010 against Supabase (alphaveda-prod, ap-south-1) — all must succeed with no errors
- [ ] Seed portfolio_buckets (4 rows: emergency / near_term / medium_term / long_term with target values and horizon bounds)
- [ ] Load 10 seed instruments with Lynch classification populated (NOT NULL from Day 1 — classification column is required)
- [ ] Write 1 row to ingest_status per ingest script (status='OK') to confirm scripts can reach Supabase and write records
- [ ] `pytest tests/test_smoke.py` → 6/6 PASS (migrations exist, constants valid, disclaimer non-empty, cold-start weights sum to 1.0, floor enforced, prediction logged)
- [ ] Confirm UI label "Signal weights: using priors (0 observations)" is visible on the Signals page — confirms cold-start path is active and correctly surfaced
- [ ] `DESIGN.md`, `WEIGHT_REVIEW_PROCESS.md`, and all three `.claude/rules/` files (`SEBI_COMPLIANCE.md`, `COMMERCIAL_GATE.md`, `DATA_SOURCES.md`) committed to the repo root

---

## 8. Contributing Rules

1. **Run `pytest tests/test_smoke.py` before every commit — 6/6 must pass.** This suite guards
   the migration schema, constants integrity, and the prediction-logging requirement. A failing
   smoke test means the database schema or signal flow is broken; do not commit over a failure.

2. **The SEBI disclaimer must appear on every page — never remove or conditionalize the fixed
   footer.** The disclaimer is injected in `app.py` before `st.navigation()` as a fixed-position
   HTML block. It is not a Streamlit widget and must not be converted to one. Removing it or
   wrapping it in a conditional violates compliance rules in `.claude/rules/SEBI_COMPLIANCE.md`.

3. **Never bypass `CommercialLicenseError`.** If `ALPHAVEDA_COMMERCIAL=true` is set in the
   environment, `YFinanceProvider` must raise `CommercialLicenseError` — not silently fall back
   to returning data. The error is the safety gate. See `.claude/rules/COMMERCIAL_GATE.md` for
   the full data-source routing table and upgrade triggers.

4. **Every signal emit must write to `accuracy_predictions` synchronously — no batching, no
   exceptions.** The ledger is only as complete as the signal log. Buffering or deferring the
   insert means accuracy outcomes cannot be resolved correctly and segment observation counts
   will be incorrect. This is enforced by test `test_prediction_logged_on_emit()` in the smoke
   suite.

5. **No `signal_weights` row may transition from `PROPOSED` to `ACTIVE` without
   `approved_by='tarun'`.** Automation may generate proposals and write them with
   `status='PROPOSED'`; it may never set `status='ACTIVE'` or `approved_by` to any value.
   The approval step runs in `pages/accuracy.py` under a human-initiated action only. This is
   governance, not a workflow optimization — do not add shortcuts.
