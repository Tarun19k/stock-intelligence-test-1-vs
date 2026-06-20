# AlphaVeda MVP Design
**Date:** 2026-06-21  
**Status:** IN PROGRESS — Section 1 complete, Sections 2–8 pending council review  
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

## Sections 2–8 — PENDING

| Section | Content | Status |
|---|---|---|
| 2 | Data Model — 9 migrations (6 core + 3 accuracy tables) | PENDING |
| 3 | 24-Segment Accuracy Ledger Schema | PENDING |
| 4 | Data Viewer Design — screens, layout, provenance display | PENDING |
| 5 | Signal Engine Design — signal types, confidence, arbitration | PENDING |
| 6 | Path Optimizer Design — Kelly sizing, bucket-aware ranking | PENDING |
| 7 | Accuracy Feedback Loop Design — prediction log, outcome tracking, proposals | PENDING |
| 8 | Quality Standards — data gates, test coverage, confidence display rules | PENDING |

---

*Design doc version 0.1 — Section 1 only. Pending council review before Sections 2–8 are written.*
