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

## Circuit-flag rule (pre-G1)
ohlcv.circuit_flag = TRUE marks circuit-locked prices.
These rows must be EXCLUDED from outcome scoring in resolve_outcomes.py.
This exclusion is NOT implemented at G0 — it is a hard pre-G1 gate.
Do not begin accuracy ledger updates until circuit_flag exclusion is wired.
