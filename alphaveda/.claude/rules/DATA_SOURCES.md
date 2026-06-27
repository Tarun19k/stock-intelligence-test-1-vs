# Data Sources Rules — AlphaVeda

## Source table

| Source | Licence | Gate | Cadence | Tables |
|---|---|---|---|---|
| NSE Bhavcopy | Open (NSE ToS) | Always available | Daily EOD | ohlcv |
| BSE Bhavcopy | Open (BSE ToS) | Always available | Daily EOD | ohlcv |
| BSE Shareholding XBRL | Open | Always available | Quarterly | fundamentals |
| BSE Financials XBRL | Open | Always available | Quarterly | fundamentals |
| Macro data | Manual | Always available | Monthly | macro_regime |
| yfinance | Personal use only | commercial=False only | On-demand | ohlcv supplement |
| FMP | Commercial licence | commercial=True only | Daily | ohlcv supplement |

## Upgrade triggers
- First non-self subscriber (`waitlist.converted_at` set) → FMP replaces yfinance
- Do not activate FMP until ALPHAVEDA_FMP_KEY is set in .env

## Provenance requirements
Every row in ohlcv, fundamentals, macro_regime must have:
- source (VARCHAR 50) — e.g. 'bhavcopy_nse', 'bse_xbrl', 'manual'
- ingested_at (TIMESTAMPTZ) — when this row was written
- licence_class (ohlcv only) — 'personal' | 'commercial' | 'open'

## Circuit-flag rule
ohlcv.circuit_flag = TRUE marks circuit-locked prices.
These rows ARE EXCLUDED from outcome scoring in resolve_outcomes.py (lines 29–33):
circuit-locked rows are skipped when building the symbol→close map.
This exclusion was implemented before G0 (Jhunjhunwala condition, commit f978fc5).
Do not add a second exclusion layer — the filter already exists at the resolution level.
