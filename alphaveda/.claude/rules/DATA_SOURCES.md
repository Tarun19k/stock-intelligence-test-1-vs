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

## Sector-class rule (fundamentals, added 2026-07-29, migration 0019)
`fundamentals` schema (roic_pct, fcf_cr, promoter_pledge_pct, debt_equity, eps, revenue_cr)
is an industrial-company schema. Financial-sector tickers (banks/NBFCs — e.g. HDFCBANK,
BAJFINANCE) get two fields set NULL **by design, not as missing data**:
- `debt_equity` — banks are deposit-funded; Borrowings/Equity is not a meaningful
  leverage ratio for them (regulatory capital rules govern bank leverage instead).
- `roic_pct` — the ROCE-as-proxy convention (Tarun-approved 2026-07-29) does not
  apply to banks either; ROCE is not the metric used to assess bank profitability.

Use `roe_pct` (Return on Equity) instead for financial-sector rows — freely available
on Screener's summary bar for every company regardless of sector. `sector_class`
('industrial' | 'financial') on each row tells downstream code (signal generation,
any dashboard) which interpretation applies — check this before treating a NULL
roic_pct/debt_equity as a data gap.

**Known, currently-unsolved gap:** CAR (Capital Adequacy Ratio), NIM (Net Interest
Margin), Gross/Net NPA%, and CASA ratio are the metrics actually used to assess bank
health, but are paywalled on Screener's free tier (confirmed live 2026-07-29 on
HDFCBANK's own page). No column was added for these — adding unpopulatable columns
would recreate the same silent-gap problem one layer up. Revisit if/when a paid data
source is adopted (see Upgrade triggers above).

## Circuit-flag rule
ohlcv.circuit_flag = TRUE marks circuit-locked prices.
These rows ARE EXCLUDED from outcome scoring in resolve_outcomes.py (lines 29–33):
circuit-locked rows are skipped when building the symbol→close map.
This exclusion was implemented before G0 (Jhunjhunwala condition, commit f978fc5).
Do not add a second exclusion layer — the filter already exists at the resolution level.
