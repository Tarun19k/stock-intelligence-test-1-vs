-- AlphaVeda Migration: widen instruments.classification CHECK to allow 'unclassified'
--
-- Additive only -- does not touch the 16 existing rows, all of which already carry
-- a real Lynch classification. Needed for the Nifty 500 universe expansion: 484 new
-- tickers cannot honestly get a real Lynch classification (fast_grower/stalwart/
-- slow_grower/cyclical/turnaround/asset_play) without real per-company analysis,
-- and engine.py line 336 reads this column directly to pick the signal-weight
-- segment -- a fabricated value would silently drive real signal output, not just
-- sit as inert metadata. 'unclassified' is an honest state label, not a guess.
--
-- Paired with signal_gate_until = '2099-01-01' on newly-seeded rows (same gating
-- mechanism already used for TMCV's post-demerger gate, engine.py's existing
-- signal_gate_until check) -- OHLCV/fundamentals collection starts immediately,
-- signal emission stays suppressed until each ticker gets a real classification.

ALTER TABLE instruments DROP CONSTRAINT instruments_classification_check;

ALTER TABLE instruments ADD CONSTRAINT instruments_classification_check CHECK (
  classification IN ('fast_grower','stalwart','slow_grower',
                     'cyclical','turnaround','asset_play','unclassified')
);
