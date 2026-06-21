# Expert: Vikram Bhattacharya — NSE/BSE Market Microstructure

**Domain:** NSE/BSE market microstructure
**Seat label:** Bhavcopy Quirks & Liquidity Reality

## Top concern about AlphaVeda
The OHLCV ingest (Section 1, Layer 1; `0002_ohlcv.sql`) treats NSE/BSE Bhavcopy as clean daily bars and the outcome resolver (Section 7) computes `actual_return` and `peak_return_pct` by "fetching the OHLCV return over the horizon window." Indian cash-segment Bhavcopy has structural quirks this ignores: circuit-filter-locked stocks (upper/lower circuit) print a `close` that is *not a tradeable price* — you could not have entered or exited there. A signal that "hit" because a microcap rallied 20% on three days of upper-circuit with zero deliverable volume is recorded as `is_correct = true` and feeds the 24-segment ledger, inflating hit rates on exactly the illiquid `turnaround` / `asset_play` names where circuits are common. `peak_return_pct` (the Druckenmiller magnitude metric) is the most corrupted field, since intraday `high` on a circuit day is fictional liquidity.

## Evaluation lenses
1. Tradeability of recorded prices — is each `close`/`high` in `ohlcv` an executable price, or a circuit-locked / illiquid print that no real order could fill?
2. Segment-specific liquidity — do `cyclical`, `turnaround`, and `asset_play` classifications (Section 2 CHECK) skew toward illiquid microcaps where Bhavcopy is least reliable?
3. Regime instrument validity — is `nifty_vix` (`macro_regime`) the India VIX, and does the `VIX_CALM_THRESHOLD=18.0` reflect Indian-market VIX distribution rather than a US-VIX heuristic?

## Key questions for R3 council
- When `scripts/resolve_outcomes.py` (Section 7) computes return over the horizon, does it exclude or flag days where the instrument was circuit-locked or had near-zero deliverable volume? Neither `ohlcv` nor the resolver carries a circuit/liquidity field.
- `VIX_CALM_THRESHOLD = 18.0` (Section 5) gates `cycle_phase` derivation — India VIX historically sits in the low-to-mid teens in calm regimes and spikes differently from US VIX. Is 18.0 calibrated to India VIX, or imported?
- The signal universe spans NSE and BSE (`exchange` CHECK). For dual-listed names, NSE and BSE Bhavcopy give different closes/volumes — which `source` wins, and can the same instrument get two conflicting outcomes?

## Red flags in current design
1. **Section 7 outcome resolution + `0002_ohlcv.sql`**: no circuit-filter or deliverable-volume field; circuit-locked rallies are scored as genuine `is_correct=true` outcomes, inflating hit rate and `peak_return_pct` for illiquid names.
2. **Section 5 `VIX_CALM_THRESHOLD = 18.0`**: a single VIX boundary drives `cycle_phase` across all four regimes (`PHASE_RULES`) with no evidence it is calibrated to India VIX rather than a generic threshold.
3. **`0002_ohlcv.sql` UNIQUE(instrument_id, trade_date) + `exchange` CHECK**: dual-listed NSE/BSE names can produce divergent bars; the schema's per-instrument uniqueness assumes one exchange's data, with no rule for which Bhavcopy is authoritative.
