-- Additive: BROOKFIELD_INDIA_RET (real ticker BIRET) is a REIT, not equity or ETF --
-- genuinely different instrument class (units in a trust, not company shares or a
-- fund basket). Widening asset_class CHECK, same pattern as the earlier 'etf' addition.
ALTER TABLE instruments DROP CONSTRAINT IF EXISTS instruments_asset_class_check;
ALTER TABLE instruments ADD CONSTRAINT instruments_asset_class_check
  CHECK (asset_class IN ('equity', 'etf', 'reit'));
